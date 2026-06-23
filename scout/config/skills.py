"""
skills.py — Centralized vocabulary for Scout's parsing and extraction pipeline.
"""

SKILL_VOCAB = [
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

ROLE_PATTERNS = [
    "machine learning engineer",
    "ml engineer",
    "ai engineer",
    "backend engineer",
    "software engineer",
    "data engineer",
    "data scientist",
    "product manager",
    "program manager",
    "computer vision engineer",
    "nlp engineer",
    "frontend engineer",
    "full stack engineer"
]