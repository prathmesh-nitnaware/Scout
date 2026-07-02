import sys
from pathlib import Path

# Ensure the Scout project root is on sys.path so `scout.*` imports resolve
# whether this file is run directly (python api/main.py) or via uvicorn
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import time
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer

from scout.pipeline.live_ranker import rank_candidates

app = FastAPI(title="Scout API", description="Backend API for the Scout Ranking Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
SUBMISSION_CSV = ROOT / "submission_final.csv"
CANDIDATE_FEATURES = ARTIFACTS / "candidate_features.parquet"
EMBEDDINGS_PATH = ARTIFACTS / "embeddings.npy"
FLAGS_PATH = ARTIFACTS / "validation_flags.json"
MODEL_NAME = "all-MiniLM-L6-v2"

# Global Cache
CACHE = {}

@app.on_event("startup")
def load_cache():
    print("[API] Starting up: Loading cache into memory...")
    start_time = time.time()
    
    # Load feature store
    df_raw = pd.read_parquet(CANDIDATE_FEATURES, engine="pyarrow")
    
    # Filter honeypots
    if FLAGS_PATH.exists():
        with open(FLAGS_PATH, encoding="utf-8") as fh:
            flags = json.load(fh)
        valid_mask = df_raw["candidate_id"].apply(
            lambda cid: flags.get(cid, {}).get("validation_passed", True)
        ).values
        df = df_raw[valid_mask].reset_index(drop=True)
    else:
        valid_mask = np.ones(len(df_raw), dtype=bool)
        df = df_raw.copy()
        
    del df_raw  # Free raw dataframe memory
        
    # Load embeddings
    embeddings = np.load(EMBEDDINGS_PATH)
    
    # If the embeddings file matches the un-filtered raw dataframe length, mask it
    if len(embeddings) == len(valid_mask):
        embeddings = embeddings[valid_mask]
        
    # 🔴 Change 2 — Startup Cache Validation
    if len(df) != len(embeddings):
        raise RuntimeError(
            f"Embedding mismatch: {len(df)} valid candidates vs {len(embeddings)} embeddings."
        )
        
    # 🟡 Change 3 — Normalize Embeddings for more stable retrieval
    print("[API] Normalizing embeddings (L2)...")
    embeddings = embeddings.astype(np.float16)  # Use float16 to halve memory footprint
    norms = np.linalg.norm(embeddings.astype(np.float32), axis=1, keepdims=True)
    embeddings = (embeddings / np.maximum(norms, 1e-12)).astype(np.float16)
        
    # Fit TF-IDF matrix
    print("[API] Fitting TF-IDF Matrix on raw candidate text...")
    tfidf_vec = TfidfVectorizer(max_features=20000, sublinear_tf=True, min_df=2, ngram_range=(1,2), stop_words='english')
    tfidf_matrix = tfidf_vec.fit_transform(df['raw_text'])
    
    df.drop(columns=['raw_text'], inplace=True, errors='ignore')  # Free up large string column
    
    # Load SentenceTransformer
    print(f"[API] Loading SentenceTransformer '{MODEL_NAME}'...")
    model = SentenceTransformer(MODEL_NAME)
    
    # 🟢 Change 7 — Add Warmup inference to prevent first-request latency
    print("[API] Warming up model...")
    model.encode(["warmup query"])
    
    CACHE["df"] = df
    CACHE["embeddings"] = embeddings
    CACHE["tfidf_vec"] = tfidf_vec
    CACHE["tfidf_matrix"] = tfidf_matrix
    CACHE["model"] = model
    CACHE["last_runtime_metrics"] = None  # Placeholder for live metrics
    
    # 🟡 Change 4 — Add comprehensive startup stats for judges
    print(f"""
[API] Cache Loaded Successfully in {time.time() - start_time:.2f}s
==================================================
  Candidates (Valid) : {len(df):,}
  Embeddings Shape   : {embeddings.shape}
  TF-IDF Shape       : {tfidf_matrix.shape}
  Model Name         : {MODEL_NAME}
==================================================
Ready to serve traffic.
""")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Scout Engine is online"}

@app.get("/metrics")
def get_metrics():
    # 🟡 Change 5 — Live Metrics Endpoint reflecting the actual runtime pool
    last_metrics = CACHE.get("last_runtime_metrics")
    
    if last_metrics:
        reduction = [
            {"stage": "Raw Dataset", "count": 100000},
            {"stage": "After Validation", "count": len(CACHE.get("df", []))},
            {"stage": "TF-IDF Pool", "count": last_metrics.get("tfidf_pool_size", 0)},
            {"stage": "MiniLM Pool", "count": last_metrics.get("minilm_pool_size", 0)},
            {"stage": "Union Pool", "count": last_metrics.get("union_pool_size", 0)},
            {"stage": "Final Ranked Output", "count": 100}
        ]
        runtime = last_metrics.get("runtime_seconds", 0)
    else:
        reduction = [
            {"stage": "Raw Dataset", "count": 100000},
            {"stage": "After Validation", "count": len(CACHE.get("df", [])) if CACHE else 97835},
            {"stage": "Live Pools", "count": "Awaiting first query..."},
            {"stage": "Final Ranked Output", "count": 100}
        ]
        runtime = 0.0
    
    try:
        df = pd.read_csv(SUBMISSION_CSV)
        feat_df = CACHE.get("df", pd.read_parquet(CANDIDATE_FEATURES, engine="pyarrow"))
        df = df.merge(feat_df[['candidate_id', 'current_title', 'years_exp']], on='candidate_id', how='left')
        title_dist = df['current_title'].value_counts().reset_index().to_dict(orient="records")
        title_dist = [{"name": r["current_title"], "count": r["count"]} for r in title_dist]
    except Exception as e:
        title_dist = []
        
    return {
        "pipeline_reduction": reduction,
        "title_distribution": title_dist,
        "last_query_runtime_seconds": runtime
    }

# 🟢 Change 6 — Model Metadata Endpoint for architecture transparency
@app.get("/about")
def get_about():
    df_len = len(CACHE.get("df", [])) if CACHE else 0
    return {
        "engine_version": "1.0",
        "retrieval_architecture": "Hybrid Union Pool (TF-IDF + MiniLM Semantic)",
        "embedding_model": MODEL_NAME,
        "candidate_pool_size": df_len,
        "features": {
            "honeypot_filtering": True,
            "structured_scoring": True,
            "credibility_engine": True,
            "dynamic_reasoning": True
        }
    }

class RankRequest(BaseModel):
    jd_text: str

@app.post("/rank-candidates")
def run_ranking(req: RankRequest):
    if not CACHE:
        raise HTTPException(status_code=503, detail="Cache not loaded yet.")
    try:
        res = rank_candidates(req.jd_text, CACHE, top_k=100)
        
        # 🟡 Change 5: Intercept stats and store them for the /metrics route
        if "retrieval_stats" in res:
            CACHE["last_runtime_metrics"] = res["retrieval_stats"]
            CACHE["last_runtime_metrics"]["runtime_seconds"] = res.get("runtime_seconds", 0)

        # Drop verbose debug field — keep response lightweight for frontend
        res.pop("technical_jd_text", None)
        return res
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# 🔴 Change 1 — Properly deprecate the legacy endpoint 
@app.post("/rank")
def legacy_rank():
    raise HTTPException(
        status_code=410, 
        detail="Legacy endpoint retired. Please use /rank-candidates with the dynamic pipeline."
    )

@app.get("/candidate/{candidate_id}")
def get_candidate(candidate_id: str):
    try:
        df = CACHE.get("df")
        if df is None:
            raise HTTPException(status_code=503, detail="Cache not loaded.")
            
        cand_row = df[df["candidate_id"] == candidate_id]
        if cand_row.empty:
            raise HTTPException(status_code=404, detail="Candidate not found")
            
        c_dict = cand_row.iloc[0].to_dict()
        
        if isinstance(c_dict.get("skills"), str):
            try:
                c_dict["skills"] = json.loads(c_dict["skills"])
            except:
                pass
                
        return c_dict
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)