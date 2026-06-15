import numpy as np
from config import match_config, TECH_SKILLS
from core.logger import get_logger
from src.embedder import embed_text


logger = get_logger(__name__)

def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:

    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    if norm_a == 0 or norm_b == 0:
        logger.warning(f"Zero vector detected - returning 0 similarity")
        return 0.0
    
    similarity = np.dot(vec_a, vec_b)/ (norm_a * norm_b)

    return float(np.clip(similarity, -1.0, 1.0))

def extract_skills(text: str) -> set:
    text_lower = text.lower()
    return {
        skill for skill in TECH_SKILLS if skill in text_lower
    }

def get_verdict(score: float) -> str:
    if score >= 0.85:
        return "Strong Match"
    elif score >= 0.70:
        return "Good Match"
    elif score >= 0.50:
        return "Weak Match"
    else:
        return "Poor Match"

def compute_match(resume_text:str, jd_text:str) -> dict:

    logger.info(
        f"Computing match: "
        f"resume={len(resume_text)} chars, "
        f"jd={len(jd_text)} chars"
    )

    resume_embbed = embed_text(resume_text)
    jd_embbed = embed_text(jd_text)

    similarity_score = cosine_similarity(resume_embbed, jd_embbed)

    verdict = get_verdict(similarity_score)

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)
    matched = resume_skills & jd_skills
    missing_skills = jd_skills - resume_skills

    logger.info(
        f"Match complete: score={similarity_score:.3f} "
        f"verdict={verdict} "
        f"matched={len(matched)} "
        f"missing={len(missing_skills)}"
    )

    return {
        "match_score": similarity_score,
        "match_percentage": round(similarity_score * 100, 1),
        "match_skills": sorted(list(matched)),
        "missing_skills": sorted(list(missing_skills)),
        "verdict": verdict,
        "resume_ength": len(resume_text),
        "jd_length": len(jd_text)
    }


