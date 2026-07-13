"""
Utility module for fuzzy string matching using rapidfuzz.
"""

from rapidfuzz import fuzz
from souscription.config.settings import FUZZY_NAME_THRESHOLD, FUZZY_ADDRESS_THRESHOLD
from souscription.utils.text_cleaner import normalize_text

def get_similarity_score(str1: str, str2: str) -> float:
    """
    Computes a token-set similarity score between two strings (0 to 100).
    """
    clean_str1 = normalize_text(str1)
    clean_str2 = normalize_text(str2)
    
    if not clean_str1 or not clean_str2:
        return 0.0
        
    return float(fuzz.token_set_ratio(clean_str1, clean_str2))

def match_names(name1: str, name2: str, threshold: float = FUZZY_NAME_THRESHOLD) -> tuple[bool, float]:
    """
    Compares two company names and returns (matches, score).
    """
    score = get_similarity_score(name1, name2)
    return score >= threshold, score

def match_addresses(addr1: str, addr2: str, threshold: float = FUZZY_ADDRESS_THRESHOLD) -> tuple[bool, float]:
    """
    Compares two physical addresses and returns (matches, score).
    """
    score = get_similarity_score(addr1, addr2)
    return score >= threshold, score
