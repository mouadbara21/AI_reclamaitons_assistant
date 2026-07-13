"""
Mathematical checksum validation routines for Moroccan identifiers (RIB, ICE, CNIE MRZ).
"""

import re


# Mapping of letters to digit equivalents for alphanumeric RIBs (ISO 7064 / Moroccan banking)
_RIB_LETTER_MAP = {
    'A': '1', 'J': '1',
    'B': '2', 'K': '2', 'S': '2',
    'C': '3', 'L': '3', 'T': '3',
    'D': '4', 'M': '4', 'U': '4',
    'E': '5', 'N': '5', 'V': '5',
    'F': '6', 'O': '6', 'W': '6',
    'G': '7', 'P': '7', 'X': '7',
    'H': '8', 'Q': '8', 'Y': '8',
    'I': '9', 'R': '9', 'Z': '9',
}


def validate_rib(rib: str) -> bool:
    """Validate a 24-character Moroccan RIB using modulo 97.

    Steps:
      1. Strip whitespace and dashes.
      2. Convert any letters to their digit equivalents using the banking letter map.
      3. Verify the resulting 24-digit number is divisible by 97.

    This is structure-independent (works for BCP 3+3+16+2, BOA 3+5+14+2, etc.).
    """
    # Strip formatting characters (spaces, dashes)
    clean = re.sub(r'[\s\-]', '', rib).upper()

    # Convert letters to digits
    rib_numeric = ''.join(_RIB_LETTER_MAP.get(c, c) for c in clean)

    if len(rib_numeric) != 24 or not rib_numeric.isdigit():
        return False

    return int(rib_numeric) % 97 == 0


def validate_ice(ice: str) -> bool:
    """Validate a 15-digit Moroccan ICE (Identifiant Commun de l'Entreprise).

    Structure: EEEEEEEEE SSSS CC
      - 9-digit entity ID
      - 4-digit establishment number
      - 2-digit check key

    Key = 97 - ((first_13_digits × 100) mod 97)
    Special case: if computed key is 97, the actual key is stored as 00.
    """
    clean_ice = re.sub(r'[\s\-]', '', ice)
    if len(clean_ice) != 15 or not clean_ice.isdigit():
        return False

    base = int(clean_ice[:13])
    actual_key = int(clean_ice[13:15])

    computed_key = 97 - ((base * 100) % 97)
    # Edge case: when remainder is 0, computed_key is 97 → stored as 00
    if computed_key == 97:
        computed_key = 0

    return computed_key == actual_key


def calculate_mrz_check_digit(data: str) -> int:
    """Calculate the ICAO Doc 9303 check digit using weights 7, 3, 1.

    Character values: 0-9 → 0-9, A-Z → 10-35, '<' (filler) → 0.
    """
    WEIGHTS = [7, 3, 1]

    def char_val(c: str) -> int:
        if c.isdigit():
            return int(c)
        elif c.isalpha():
            return ord(c.upper()) - ord('A') + 10
        elif c == '<':
            return 0
        raise ValueError(f"Invalid MRZ character: {c}")

    total = sum(char_val(c) * WEIGHTS[i % 3] for i, c in enumerate(data))
    return total % 10
