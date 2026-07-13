"""
Parser for Taxe Professionnelle (Business Tax) registration documents.

Layout reference (AAC060B form):
  - Header: "TAXE PROFESSIONNELLE"
  - Structured rows with label-value pairs.
  - Contains: IF, ICE, RC, TP number, CNI, Company name, Address.
"""

import re
from souscription.models.document import ExtractedTaxeProfessionnelle
from souscription.utils.text_cleaner import clean_whitespace


def parse_taxe_professionnelle(text: str) -> ExtractedTaxeProfessionnelle:
    """
    Parses the text of a Taxe Professionnelle certificate and returns
    a structured Pydantic object.
    
    All values extracted via generic regex — no hardcoded defaults.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # 1. ICE (15 digits)
    ice = ""
    ice_match = re.search(r'\b(00\d{13})\b', text)
    if not ice_match:
        ice_match = re.search(r'\b(\d{15})\b', text)
    if ice_match:
        ice = ice_match.group(1)

    # Collect all 8-digit numbers for disambiguation
    all_8 = re.findall(r'\b(\d{8})\b', text)

    # 2. Identifiant Fiscal (IF) — 8 digits, near "Identifiant Fiscal" anchor
    if_num = ""
    if_anchor = re.search(r'(?:Identifiant|I\.?F)\s*(?:Fiscal)?\s*[:\-]?\s*(\d{7,9})', text, re.IGNORECASE)
    if if_anchor:
        if_num = if_anchor.group(1)
    elif all_8:
        if_num = all_8[0]  # First 8-digit number is typically IF

    # 3. TP Number (Taxe Professionnelle number, typically 8 digits)
    tp_num = ""
    tp_anchor = re.search(r'Taxe\s+Professionnelle\s*[:\-N°]*\s*(\d{7,9})', text, re.IGNORECASE)
    if tp_anchor:
        tp_num = tp_anchor.group(1)
    else:
        # Second distinct 8-digit number
        for candidate in all_8:
            if candidate != if_num and candidate not in ice:
                tp_num = candidate
                break

    # 4. RC Number (can be short like 429045 or long like 10001486291)
    rc_num = ""
    rc_anchor = re.search(r'(?:R\.?C\.?|Registre\s+de\s+Commerce)\s*[:\-N°]*\s*(\d{3,12})', text, re.IGNORECASE)
    if rc_anchor:
        rc_num = rc_anchor.group(1)
    else:
        # Look for digit sequences of 9-12 chars (long RC format)
        long_rc = re.search(r'\b(\d{9,12})\b', text)
        if long_rc and long_rc.group(1) not in ice:
            rc_num = long_rc.group(1)

    # 5. Raison Sociale / Company Name
    denom = ""
    # Strategy A: Line after "Nom" or "Raison Sociale" anchor
    name_anchor = re.search(r'(?:Nom|Raison\s+Sociale)\s*[:\-]?\s*(.+)', text, re.IGNORECASE)
    if name_anchor:
        denom = clean_whitespace(name_anchor.group(1))
    else:
        # Strategy B: First prominent uppercase line that isn't a header
        for line in lines:
            if line.isupper() and len(line) > 5 and not re.search(
                r'TAXE|PROFESSIONNELLE|DIRECTION|GENERALE|IMPOTS|ROYAUME|MAROC|AAC', line, re.IGNORECASE):
                denom = clean_whitespace(line)
                break

    # 6. CNI / CIN of representative (e.g. "BE50973", "CD862418")
    cni = None
    cni_match = re.search(r'\b([A-Z]{1,2}\d{5,7})\b', text)
    if cni_match:
        cni = cni_match.group(1)

    # 7. Siège Social (address)
    siege = ""
    addr_match = re.search(
        r'(\d+\s+(?:RUE|AVENUE|BOULEVARD|BD|AV\.?|LOT|QUARTIER|ZONE)\s+[^\n]{5,60})',
        text, re.IGNORECASE
    )
    if addr_match:
        siege = clean_whitespace(addr_match.group(1))
    else:
        # Fallback: any line with street keywords
        for line in lines:
            if re.search(r'(RUE|AVENUE|BD|BOULEVARD|NR|N°)', line, re.IGNORECASE) and len(line) > 10:
                siege = clean_whitespace(line)
                break

    # 8. Date d'édition
    date_ed = ""
    date_match = re.search(r'(\d{2}[-/]\d{2}[-/]\d{4})', text)
    if date_match:
        date_ed = date_match.group(1)

    return ExtractedTaxeProfessionnelle(
        raw_text=text,
        raison_sociale=denom,
        if_number=if_num,
        ice=ice,
        rc_number=rc_num,
        tp_number=tp_num,
        cni=cni,
        siege_social=siege,
        date_edition=date_ed
    )
