"""
jd_parser.py — Robust JD Parser
------------------------------------------------
Goal: Extract structure from raw JD text.

Output:
    {
        "role_title": str,
        "required_skills": list[str],
        "preferred_skills": list[str],
        "responsibilities": list[str],
        "raw_jd": str,
        "seniority": str
    }
"""

from __future__ import annotations

import re
from pathlib import Path
from scout.pipeline.extract_jd import parse_seniority

# Curated ML/tech skill vocabulary
SKILL_VOCAB: list[str] = [
    # Core ML
    "PyTorch", "TensorFlow", "Keras", "JAX",
    "Hugging Face", "Transformers", "BERT", "GPT", "T5", "LLaMA", "Mistral",
    "LLM", "Fine-tuning LLMs", "LoRA", "QLoRA", "PEFT", "RLHF",
    "RAG", "Retrieval-Augmented Generation", "Embeddings", "Vector Search",
    "NLP", "NER", "Sentiment Analysis", "Text Classification", "Summarization",
    "Prompt Engineering", "Instruction Tuning",
    
    # Agentic AI & APIs
    "LangChain", "LangGraph", "CrewAI", "OpenAI", "OpenAI API",
    "Gemini", "Claude", "Anthropic", "Agentic AI", "Agents",
    "Multi-Agent Systems", "MCP",

    # Computer Vision
    "Computer Vision", "Image Classification", "Object Detection", "YOLO", "OpenCV",
    "GANs", "Diffusion Models", "Stable Diffusion", "Multimodal", "CLIP",
    
    # ML Ops & Frameworks
    "scikit-learn", "XGBoost", "LightGBM", "CatBoost",
    "Feature Engineering", "MLflow", "Weights & Biases", "BentoML",
    "MLOps", "Model Deployment", "Model Monitoring",
    
    # Data Engineering & Databases
    "Python", "R", "SQL", "Pandas", "NumPy", "PySpark", "Apache Spark",
    "Airflow", "Kafka", "Databricks", "Snowflake", "BigQuery",
    "FAISS", "Pinecone", "Milvus", "Elasticsearch",
    "Redis", "PostgreSQL", "MongoDB",
    "Data Pipelines", "ETL",
    
    # Backend & Frontend
    "Node.js", "TypeScript", "React", "Next.js", "GraphQL", "Microservices",
    
    # Cloud & Infra
    "AWS", "GCP", "Azure", "SageMaker", "Vertex AI",
    "Docker", "Kubernetes", "FastAPI", "REST API",
    
    # Speech
    "Speech Recognition", "TTS", "ASR", "Whisper",
    
    # Math
    "Statistics", "Linear Algebra", "Time Series", "Bayesian",
    
    # Dev tools & Product
    "Git", "GitHub", "Linux", "Agile", "Scrum", "JIRA", "Product Strategy", 
    "Roadmap", "Data Analysis", "Stakeholder Management", "A/B Testing"
]

# Lightweight role -> fallback skills mapping for generic roles
ROLE_FALLBACK_SKILLS: dict[str, list[str]] = {
    "backend developer": ["backend", "api", "microservices", "database"],
    "java developer": ["java", "backend", "rest api", "spring"],
    "frontend developer": ["javascript", "react", "css", "html"],
    "devops engineer": ["docker", "kubernetes", "aws", "linux"],
    "data scientist": ["python", "machine learning", "statistics"],
}

def extract_role_title(text: str) -> str:
    """
    Extract role title from JD.
    Works for both:
      AI Engineer with 5-9 years experience
      Senior Backend Java Engineer
      ML Research Scientist
      Principal Data Engineer
    """
    first_line = text.strip().split("\n")[0]

    # Pattern 1:
    # "AI Engineer with 5 years..."
    m = re.search(
        r"^(.+?)\s+(?:with|for|requiring|required|needed)",
        first_line,
        flags=re.IGNORECASE
    )

    if m:
        return m.group(1).strip()

    # Pattern 2:
    # "Senior Backend Java Engineer"
    role_keywords = (
        "Engineer",
        "Scientist",
        "Manager",
        "Developer",
        "Analyst",
        "Architect",
        "Designer",
        "Director",
        "Lead",
        "Consultant"
    )

    for keyword in role_keywords:
        m = re.search(
            rf"([A-Za-z\s]+{keyword})",
            first_line,
            flags=re.IGNORECASE
        )
        if m:
            return m.group(1).strip()

    return ""


def extract_sections(text: str) -> dict:
    """
    Lightweight state machine to bucket text into 
    Required, Preferred, and Responsibilities.
    """
    state = "required"  # Default state if no headers found
    sections = {"required": [], "preferred": [], "responsibilities": []}
    
    for line in text.splitlines():
        lower_line = line.strip().lower()
        
        # State transitions
        if any(x in lower_line for x in ["responsibilities", "what you'll do", "what you will do", "duties"]):
            state = "responsibilities"
            continue
        elif any(x in lower_line for x in ["preferred", "nice to have", "bonus"]):
            state = "preferred"
            continue
        elif any(x in lower_line for x in ["requirements", "required skills", "must have", "qualifications", "what we're looking for"]):
            state = "required"
            continue
            
        sections[state].append(line)
        
    return {k: "\n".join(v) for k, v in sections.items()}

def find_skills(text: str) -> list[str]:
    """Helper to extract and deduplicate skills from a block of text."""
    lowered = text.lower()
    found: list[str] = []
    
    for skill in SKILL_VOCAB:
        pattern = re.compile(r"\b" + re.escape(skill.lower()) + r"\b")
        if pattern.search(lowered):
            found.append(skill)
            
    # Deduplicate and sort
    return sorted(list(set(found)))

def parse_jd(raw_text: str) -> dict:
    # Extract Role
    role_title = extract_role_title(raw_text)
    
    # Segment the text
    sections = extract_sections(raw_text)
    
    # Find skills per section
    required_skills = find_skills(sections["required"])
    preferred_skills = find_skills(sections["preferred"])
    
    # Fallback: if sectioning failed and both are empty, scan the whole JD as required
    if not required_skills and not preferred_skills:
        required_skills = find_skills(raw_text)
    
    # If still empty, try role-based fallback skills (helps generic single-line JDs)
    if not required_skills:
        rt = (role_title or "").lower()
        # prefer exact match, else substring match
        fallback = ROLE_FALLBACK_SKILLS.get(rt)
        if fallback is None:
            for key, skills in ROLE_FALLBACK_SKILLS.items():
                if key in rt:
                    fallback = skills
                    break
        if fallback:
            required_skills = fallback
        
    # Extract bullet points for responsibilities
    resp_bullets = [
        line.strip().lstrip("-*• ").strip() 
        for line in sections["responsibilities"].splitlines() 
        if line.strip().startswith(("-", "*", "•"))
    ]
            
    # Seniority parsing
    seniority = parse_seniority(raw_text)

    return {
        "role_title": role_title,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "responsibilities": resp_bullets,
        "raw_jd": raw_text,
        "seniority": seniority
    }

def load_jd_from_file(path: str | Path) -> dict:
    text = Path(path).read_text(encoding="utf-8")
    return parse_jd(text)

if __name__ == "__main__":
    import json
    import sys
    
    # Temporary test for single-line JD extraction
    print("--- Test Run ---")
    print(json.dumps(parse_jd(
        "AI Engineer with 5-9 years experience. Required skills: Python, PyTorch, Transformers, RAG, LoRA, FAISS."
    ), indent=2))
    print("----------------\n")
    
    if len(sys.argv) < 2:
        print("Usage: python jd_parser.py <job_description.txt>")
        sys.exit(1)
    result = load_jd_from_file(sys.argv[1])
    print(json.dumps(result, indent=2))