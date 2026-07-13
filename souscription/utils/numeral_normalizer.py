"""
Utility module for Eastern to Western Arabic numerals normalization.
"""

EASTERN_TO_WESTERN = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')

def normalize_numerals(text: str) -> str:
    """
    Converts Eastern Arabic numerals (٠١٢٣٤٥٦٧٨٩) in a string 
    to standard Western Arabic numerals (0123456789).
    """
    if not text:
        return ""
    return text.translate(EASTERN_TO_WESTERN)
