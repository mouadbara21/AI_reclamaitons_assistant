"""
Central field-to-regex mapping registry.

This module provides a single source of truth for all regex patterns
used to extract specific fields from Moroccan administrative documents.
Individual extractors should reference these patterns rather than
defining their own ad-hoc regex strings.
"""

import re
from typing import Optional


# ═══════════════════════════════════════════════════════════════════
#  Identifier Patterns
# ═══════════════════════════════════════════════════════════════════

# ICE: 15 digits, commonly starting with "00"
ICE_REGEX = re.compile(r'\b(00\d{13})\b|\b(\d{15})\b')

# IF: 7-9 digits
IF_REGEX = re.compile(r'\b(\d{7,9})\b')

# RC: variable length (3-12 digits), sometimes with city suffix
RC_WITH_CITY_REGEX = re.compile(r'(\d{3,8})\s*/\s*([A-Za-z\s]+)')
RC_STANDALONE_REGEX = re.compile(r'\b(\d{3,12})\b')

# CIN/CNIE: 1-2 letters + 5-7 digits
CIN_REGEX = re.compile(r'\b([A-Z]{1,2}\d{5,7})\b')

# RIB: exactly 24 digits (after stripping spaces)
RIB_REGEX = re.compile(r'\b(\d{24})\b')

# TP: Taxe Professionnelle, typically 8 digits
TP_REGEX = re.compile(r'\b(\d{8})\b')


# ═══════════════════════════════════════════════════════════════════
#  Date Patterns
# ═══════════════════════════════════════════════════════════════════

# French date: DD/MM/YYYY or DD-MM-YYYY
DATE_FR_REGEX = re.compile(r'(\d{2}[/-]\d{2}[/-]\d{4})')

# Timestamp: DD/MM/YYYY HH:MM:SS
TIMESTAMP_REGEX = re.compile(r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})')

# "Fait à ... le DD/MM/YYYY"
FAIT_A_DATE_REGEX = re.compile(
    r'Fait\s+[àa]\s+\w+\s*,?\s*(?:le\s+)?(\d{2}/\d{2}/\d{4})',
    re.IGNORECASE
)


# ═══════════════════════════════════════════════════════════════════
#  Address Patterns
# ═══════════════════════════════════════════════════════════════════

# Street address: number + street type + name
STREET_ADDRESS_REGEX = re.compile(
    r'(\d+\s*,?\s*(?:RUE|AVENUE|BOULEVARD|BD|AV\.?|LOT|QUARTIER|ZONE|IMMEUBLE)'
    r'\s+[^\n]{5,60})',
    re.IGNORECASE
)


# ═══════════════════════════════════════════════════════════════════
#  Company / Legal Patterns
# ═══════════════════════════════════════════════════════════════════

# Legal form (forme juridique)
FORME_JURIDIQUE_REGEX = re.compile(
    r'(SOCIETE\s+A\s+RESPONSABILITE\s+LIMITEE(?:\s+A\s+ASSOCIE\s+UNIQUE)?|'
    r'SOCIETE\s+ANONYME|SOCIETE\s+EN\s+NOM\s+COLLECTIF|'
    r'SARL\s*(?:AU|A\.U\.)?|SA|SNC)',
    re.IGNORECASE
)

# SWIFT/BIC code
SWIFT_REGEX = re.compile(r'(?:SWIFT|BIC)\s*[:\-]?\s*([A-Z0-9]{8,11})', re.IGNORECASE)


# ═══════════════════════════════════════════════════════════════════
#  Extraction Helpers
# ═══════════════════════════════════════════════════════════════════

def find_ice(text: str) -> Optional[str]:
    """Extract the first 15-digit ICE from text."""
    match = ICE_REGEX.search(text)
    if match:
        return match.group(1) or match.group(2)
    return None


def find_rc_with_city(text: str) -> tuple[Optional[str], Optional[str]]:
    """Extract RC number and city from "XXXXXX/CITY" format."""
    match = RC_WITH_CITY_REGEX.search(text)
    if match:
        return match.group(1), match.group(2).strip().title()
    return None, None


def find_date(text: str) -> Optional[str]:
    """Extract the first French-format date from text."""
    match = DATE_FR_REGEX.search(text)
    if match:
        return match.group(1)
    return None


def find_street_address(text: str) -> Optional[str]:
    """Extract the first street address from text."""
    match = STREET_ADDRESS_REGEX.search(text)
    if match:
        return match.group(1).strip()
    return None
