"""
Utility module for cleaning and normalizing document text contents.
"""

import re
import unicodedata

def remove_accents(text: str) -> str:
    """
    Removes accents from string (e.g. 'Société' -> 'Societe').
    """
    if not text:
        return ""
    # Normalize character representations
    nfkd_form = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def clean_whitespace(text: str) -> str:
    """
    Collapses multiple spaces, newlines, and tabs into a single space and trims.
    """
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def normalize_text(text: str) -> str:
    """
    Applies standard cleaning pipeline: numeral normalization, accent removal,
    whitespace collapsing, and lowercasing.
    """
    if not text:
        return ""
    from souscription.utils.numeral_normalizer import normalize_numerals
    
    text = normalize_numerals(text)
    text = remove_accents(text)
    text = text.lower()
    text = clean_whitespace(text)
    return text
