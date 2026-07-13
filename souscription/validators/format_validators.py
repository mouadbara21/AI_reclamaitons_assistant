"""
Format validation routines for Moroccan document identifiers.

These validators check structural format only (length, character set, prefix),
NOT mathematical checksums (those are in checksum.py).
"""

import re


def validate_ice_format(ice: str) -> tuple[bool, str]:
    """Validate ICE structural format: exactly 15 digits.
    
    Returns (is_valid, message).
    """
    clean = re.sub(r'[\s\-]', '', ice)
    if len(clean) != 15:
        return False, f"ICE must be 15 digits, got {len(clean)} characters"
    if not clean.isdigit():
        return False, "ICE must contain only digits"
    return True, "ICE format is valid"


def validate_if_format(if_number: str) -> tuple[bool, str]:
    """Validate Identifiant Fiscal format: 7-9 digits.
    
    Returns (is_valid, message).
    """
    clean = re.sub(r'[\s\-]', '', if_number)
    if not clean.isdigit():
        return False, "IF must contain only digits"
    if not (7 <= len(clean) <= 9):
        return False, f"IF must be 7-9 digits, got {len(clean)}"
    return True, "IF format is valid"


def validate_rc_format(rc_number: str) -> tuple[bool, str]:
    """Validate Registre de Commerce format.
    
    RC can be a short number (e.g. "429045") or long (e.g. "10001486291").
    Must be 3-12 digits.
    
    Returns (is_valid, message).
    """
    clean = re.sub(r'[\s\-]', '', rc_number)
    if not clean.isdigit():
        return False, "RC number must contain only digits"
    if not (3 <= len(clean) <= 12):
        return False, f"RC number must be 3-12 digits, got {len(clean)}"
    return True, "RC format is valid"


def validate_cin_format(cin: str) -> tuple[bool, str]:
    """Validate Moroccan CIN/CNIE format.
    
    Format: 1-2 uppercase letters followed by 5-7 digits.
    Examples: BE50973, CD862418, BK123456
    
    Returns (is_valid, message).
    """
    clean = cin.strip().upper()
    if not re.match(r'^[A-Z]{1,2}\d{5,7}$', clean):
        return False, f"CIN must be 1-2 letters + 5-7 digits (e.g. BE50973), got: {cin}"
    return True, "CIN format is valid"


def validate_rib_format(rib: str) -> tuple[bool, str]:
    """Validate RIB structural format: exactly 24 alphanumeric characters.
    
    Returns (is_valid, message).
    """
    clean = re.sub(r'[\s\-]', '', rib).upper()
    if len(clean) != 24:
        return False, f"RIB must be 24 characters, got {len(clean)}"
    if not re.match(r'^[A-Z0-9]+$', clean):
        return False, "RIB must contain only letters and digits"
    return True, "RIB format is valid"


def validate_tp_format(tp: str) -> tuple[bool, str]:
    """Validate Taxe Professionnelle number format: typically 8 digits.
    
    Returns (is_valid, message).
    """
    clean = re.sub(r'[\s\-]', '', tp)
    if not clean.isdigit():
        return False, "TP number must contain only digits"
    if not (7 <= len(clean) <= 10):
        return False, f"TP number must be 7-10 digits, got {len(clean)}"
    return True, "TP format is valid"
