"""
Parser for Document IF (Bulletin de Notification d'Identifiant Fiscal) documents.

Layout reference (AAC140B form):
  - Header: "NOTIFICATION DU NUMERO D'IDENTIFICATION FISCALE"
  - Structured rows with labels in the left column and values in the right column.
  - The digital text layer typically renders as sequential label-value lines.
"""

import re
from souscription.models.document import ExtractedDocumentIF
from souscription.utils.text_cleaner import clean_whitespace


def parse_document_if(text: str) -> ExtractedDocumentIF:
    """
    Parses the text of a Bulletin de Notification d'Identifiant Fiscal
    and returns a structured Pydantic object.
    
    All values are extracted via regex from the raw text — no hardcoded defaults.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # 1. Raison Sociale / Dénomination
    #    Typically the first prominent uppercase block, or appears before the
    #    legal form line (e.g. "SARL", "SA", "SNC").
    denom = ""
    # Strategy A: Look for a line immediately preceding a SARL/SA line
    for i, line in enumerate(lines):
        if re.search(r'\bSARL\b|\bS\.A\.R\.L\b|\bSA\b|\bSNC\b', line, re.IGNORECASE):
            # The previous line is likely the company name
            if i > 0 and len(lines[i - 1]) >= 3:
                denom = clean_whitespace(lines[i - 1])
            # If the legal form is on the same line, try to split
            if not denom:
                parts = re.split(r'\s*(?:SARL|S\.A\.R\.L|SA|SNC)\b', line, flags=re.IGNORECASE)
                if parts and parts[0].strip():
                    denom = clean_whitespace(parts[0])
            break
    # Strategy B: Look for "NOM ET PRENOM" or "RAISON SOCIALE" anchor
    if not denom:
        match = re.search(r'RAISON SOCIALE\s*:\s*(.+)', text, re.IGNORECASE)
        if match:
            denom = clean_whitespace(match.group(1))

    # 2. Forme juridique
    forme = ""
    forme_match = re.search(
        r'(SARL\s*-?\s*ASSOCIE\s*UNIQUE\s*-?|'
        r'SARL\s*AU|SARL|S\.A\.R\.L|SA|SNC|'
        r'SOCIETE\s+A\s+RESPONSABILITE\s+LIMITEE[^,\n]*)',
        text, re.IGNORECASE
    )
    if forme_match:
        forme = clean_whitespace(forme_match.group(0))

    # 3. RC Number and City (e.g. "370621/CASABLANCA")
    rc_num = ""
    rc_city = ""
    rc_match = re.search(r'(\d{3,8})\s*/\s*([A-Z\s]+)', text)
    if rc_match:
        rc_num = rc_match.group(1)
        rc_city = clean_whitespace(rc_match.group(2).title())

    # 4. ICE (15 digits, usually starting with 00)
    ice = ""
    ice_match = re.search(r'\b(00\d{13})\b', text)
    if not ice_match:
        ice_match = re.search(r'\b(\d{15})\b', text)
    if ice_match:
        ice = ice_match.group(1)

    # 5. Identifiant Fiscal (IF) — typically 8 digits
    #    The IF usually appears near "Identification Fiscale" label or as a
    #    standalone 8-digit block that isn't the TP or part of the ICE.
    if_num = ""
    # Look near the "Identification Fiscale" anchor
    if_anchor = re.search(r'Identification\s+Fiscale[^0-9]*(\d{7,9})', text, re.IGNORECASE)
    if if_anchor:
        if_num = if_anchor.group(1)
    else:
        # Collect all 8-digit numbers not already captured
        all_8digits = re.findall(r'\b(\d{8})\b', text)
        for candidate in all_8digits:
            if candidate != rc_num and candidate not in ice:
                if_num = candidate
                break

    # 6. Taxe Professionnelle Number (typically 8 digits, different from IF)
    tp_num = ""
    tp_anchor = re.search(r'Taxe\s+Professionnelle[^0-9]*(\d{7,9})', text, re.IGNORECASE)
    if tp_anchor:
        tp_num = tp_anchor.group(1)
    else:
        all_8digits = re.findall(r'\b(\d{8})\b', text)
        for candidate in all_8digits:
            if candidate != if_num and candidate != rc_num and candidate not in ice:
                tp_num = candidate
                break

    # 7. Siège Social (address)
    siege = ""
    # Look for address-like patterns (street number + RUE/AVENUE/BOULEVARD)
    addr_match = re.search(
        r'(\d+\s+(?:RUE|AVENUE|BOULEVARD|BD|AV\.?|LOTISSEMENT|LOT|QUARTIER)\s+[^\n]{5,60})',
        text, re.IGNORECASE
    )
    if addr_match:
        siege = clean_whitespace(addr_match.group(1))
    else:
        # Fallback: line containing "siège" or address keywords
        for line in lines:
            if re.search(r'(RUE|AVENUE|BD|BOULEVARD)', line, re.IGNORECASE) and len(line) > 10:
                siege = clean_whitespace(line)
                break

    # 8. Edition Date (e.g. "Le 20-12-2021" or "20/12/2021")
    date_ed = ""
    date_match = re.search(r'Le\s*\n?\s*(\d{2}[-/]\d{2}[-/]\d{4})', text, re.IGNORECASE)
    if not date_match:
        date_match = re.search(r'(\d{2}[-/]\d{2}[-/]\d{4})', text)
    if date_match:
        date_ed = date_match.group(1)

    return ExtractedDocumentIF(
        raw_text=text,
        raison_sociale=denom,
        if_number=if_num,
        rc_number=rc_num,
        rc_city=rc_city,
        ice=ice,
        tp_number=tp_num,
        forme_juridique=forme,
        siege_social=siege,
        date_edition=date_ed
    )
