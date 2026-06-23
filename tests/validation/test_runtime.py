import requests
import time
import pandas as pd

API_URL = "http://localhost:8000/rank-candidates"

JDS = {
    "AI_ML_Engineer": """
    Looking for a Senior AI/ML Engineer.
    Required Skills: Python, PyTorch, Transformers, LLM, Fine-tuning LLMs, LoRA, Hugging Face, MLOps, Weights & Biases.
    Preferred Skills: Docker, Kubernetes, AWS, FastAPI.
    Experience: 5 to 9 years.
    Seniority: Senior.
    """,
    "Backend_Engineer": """
    Looking for a Mid-level Backend Engineer.
    Required Skills: Python, FastAPI, SQL, PostgreSQL, Docker, Kubernetes, AWS, REST API, Git, Linux.
    Preferred Skills: Redis, Elasticsearch, Kafka.
    Experience: 3 to 6 years.
    Seniority: Mid.
    """,
    "Product_Manager": """
    Looking for a Product Manager (Data & AI).
    Required Skills: Agile, Scrum, JIRA, Product Strategy, Roadmap, Data Analysis, SQL, Stakeholder Management.
    Preferred Skills: Machine Learning, A/B Testing, Python.
    Experience: 4 to 8 years.
    Seniority: Mid.
    """
}

def test_jds():
    print("Testing Live JD Responsiveness...\n")
    results = {}
    
    for name, text in JDS.items():
        print(f"--- Testing {name} ---")
        start = time.time()
        resp = requests.post(API_URL, json={"jd_text": text})
        runtime_http = time.time() - start
        
        if resp.status_code != 200:
            print(f"Error: {resp.text}")
            continue
            
        data = resp.json()
        print(f"Backend reported runtime: {data['runtime_seconds']}s")
        print(f"Total HTTP Roundtrip: {runtime_http:.2f}s")
        
        candidates = data["candidates"]
        top_20 = candidates[:20]
        titles = [c["current_title"] for c in top_20]
        cids = [c["candidate_id"] for c in top_20]
        
        print("\nTop 5 Candidates:")
        for c in candidates[:5]:
            print(f"  Rank {c['rank']}: {c['current_title']} ({c['years_exp']}y) | Score: {c['score']:.4f}")
            print(f"  Reasoning: {c['reasoning']}")
            
        # Count titles
        title_counts = pd.Series(titles).value_counts()
        print("\nTop 20 Title Distribution:")
        print(title_counts.head(5))
        print("\n" + "="*50 + "\n")
        
        results[name] = set(cids)
        
    # Check overlaps
    print("--- Candidate Overlap Analysis (Top 20) ---")
    ai_cids = results.get("AI_ML_Engineer", set())
    be_cids = results.get("Backend_Engineer", set())
    pm_cids = results.get("Product_Manager", set())
    
    print(f"AI/ML vs Backend Overlap: {len(ai_cids.intersection(be_cids))}")
    print(f"AI/ML vs PM Overlap: {len(ai_cids.intersection(pm_cids))}")
    print(f"Backend vs PM Overlap: {len(be_cids.intersection(pm_cids))}")
    
    if len(ai_cids.intersection(be_cids)) < 10 and len(ai_cids.intersection(pm_cids)) < 10:
        print("\nSUCCESS: Rankings are highly JD-responsive.")
    else:
        print("\nWARNING: Rankings might not be sufficiently JD-responsive.")

if __name__ == "__main__":
    # Wait for API to be ready
    for i in range(10):
        try:
            r = requests.get("http://localhost:8000/health")
            if r.status_code == 200:
                print("API is ready.\n")
                break
        except requests.exceptions.ConnectionError:
            print("Waiting for API...")
            time.sleep(5)
            
    test_jds()
