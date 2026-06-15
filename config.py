from dataclasses import dataclass


EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
VECTOR_DIMENSIONS: int = 384
MAX_INPUT_TOKENS: int = 512
LOG_LEVEL: str = "INFO"
LOG_DIR: str = "logs"
APP_TITLE: str = "ResumeRadar"
APP_ICON: str = "📄" 


@dataclass
class MatchConfig:
    similarity_threshold: float = 0.75
    top_skills_count: int = 10
    min_resume_length: int = 100
    min_jd_length: int = 50

match_config = MatchConfig() # Singleton Patter : One instance shared everywhere instead of creating new objects repeatedly.


TECH_SKILLS = [
    "python", "fastapi", "docker", "kubernetes", "mlflow",
    "langchain", "rag", "redis", "postgresql", "mongodb",
    "pytorch", "tensorflow", "transformers", "huggingface",
    "sql", "git", "aws", "azure", "gcp", "spark",
    "pandas", "numpy", "scikit-learn", "nlp", "llm",
    "machine learning", "deep learning", "neural network",
    "api", "rest", "microservices", "ci/cd", "linux",
    "fastapi", "streamlit", "flask", "django",
    "vector database", "embeddings", "fine-tuning",
    "langsmith", "langfuse", "pinecone", "chromadb", "faiss"
]