import numpy as np
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL, VECTOR_DIMENSIONS
from core.logger import get_logger

logger = get_logger(__name__)

_model = None #caching the model load. Using Singleton patter with lazy initiallization

def load_embedding_model() -> SentenceTransformer:

    global _model 
    if _model is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info(f"Model loaded - vector size: {VECTOR_DIMENSIONS}")
    
    return _model

def embed_text(text: str) -> np.ndarray:

    #input validation
    if not text.strip():
        logger.error("Cannot embed empty text")
        raise ValueError("Text cannot be empty")
    
    model = load_embedding_model()

    logger.info(f"Embedding text: {len(text)} chars")
    embedded_text = model.encode(text)


    if embedded_text.shape[0] != VECTOR_DIMENSIONS:
        logger.error(f"Dimension mismatch: expected {VECTOR_DIMENSIONS}, got : {embedded_text.shape[0]}")
        raise ValueError(f"Embedding dimension mismatch")    
    
    logger.info(f"Embedded successfully: shape {embedded_text.shape}")
    
    return embedded_text