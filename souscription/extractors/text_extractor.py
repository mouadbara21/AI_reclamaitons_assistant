"""
Text extractor for digital/vector PDFs using PyMuPDF (fitz).
"""

import fitz # PyMuPDF
import os

def extract_pdf_text(pdf_path: str) -> str:
    """
    Extracts plain text from a vector PDF file.
    Returns empty string if document has no text layers.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File not found: {pdf_path}")
        
    text_content = []
    doc = fitz.open(pdf_path)
    
    for page in doc:
        page_text = page.get_text("text")
        if page_text:
            text_content.append(page_text)
            
    doc.close()
    return "\n".join(text_content)
