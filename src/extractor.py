import fitz
from pathlib import Path
from core.logger import get_logger
from config import MAX_INPUT_TOKENS

logger = get_logger(__name__)

def extract_text(file_path: Path) -> str:
    logger.info(f"Starting extraction: {file_path.name}")

    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"No File at: {file_path}")
    
    if file_path.suffix.lower() != ".pdf":
        logger.error(f"Invalid file type: {file_path.suffix}")
        raise ValueError(f"Expected PDF, got: {file_path.suffix}")
    
    try:
        # doc = fitz.open(file_path)
        with fitz.open(file_path) as doc:
            full_text = ""

            for page in doc:
                full_text += page.get_text()

            page_count = doc.page_count
        
        text = full_text.strip()

        if not text:
            logger.warning(f"No text extracted from: {file_path}")
            raise ValueError("PDF appears to be empty or scanned")

        logger.info(f"Extracted {len(text)} chars from {page_count} pages")
        return text[:MAX_INPUT_TOKENS * 4]
    
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise

def get_pdf_preview(pdf_bytes: bytes) -> bytes:
    """
    Renders first page of PDF as PNG image.
    Returns PNG bytes for display in Streamlit.
    """
    logger.info("Generating PDF preview")
    
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[0]
        
        # Matrix controls zoom — 1.5x gives clear readable preview
        
        mat = fitz.Matrix(1.5, 1.5)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        doc.close()
        
        logger.info(f"Preview generated: {len(img_bytes)} bytes")
        return img_bytes
    
    except Exception as e:
        logger.error(f"Preview generation failed: {e}")
        raise