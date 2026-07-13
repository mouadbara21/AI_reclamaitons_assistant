"""
Parser for Attestation de RIB (Bank Account Certificate) documents.

Layout reference:
  - Bank letterhead with logo.
  - Paragraph body: "Attestons que la relation [COMPANY] ... est titulaire ... le numéro :"
  - 24-digit RIB in large bold font.
  - SWIFT code, date, signature, stamp.
"""

import re
from souscription.models.document import ExtractedRIB
from souscription.utils.text_cleaner import clean_whitespace


def parse_attestation_rib(text: str) -> ExtractedRIB:
    """
    Parses the text of a bank RIB attestation and returns a structured
    Pydantic object.
    
    All values extracted via generic regex — no hardcoded defaults.
    """
    # 1. Account Holder Name (Raison Sociale)
    #    Common phrasing: "que la relation [NAME] dont"
    #    or "Madame/Monsieur [NAME] Titulaire"
    #    or "certifions par la présente que [NAME]"
    owner = ""
    owner_patterns = [
        r'(?:la\s+)?relation\s+([A-Z][A-Z\s\-\'\.]{2,60})\s+dont',
        r'certifions.*?que\s+([A-Z][A-Z\s\-\'\.]{2,60})\s+(?:dont|est)',
        r'(?:Madame|Monsieur|M\.)\s+([A-Z][A-Z\s\-\'\.]{2,40})\s+(?:Titulaire|est)',
        r'(?:la\s+société|société)\s+([A-Z][A-Z\s\-\'\.]{2,60})',
    ]
    for pattern in owner_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            owner = clean_whitespace(match.group(1))
            break

    # 2. RIB Number (24 digits)
    #    May appear as a single block "011780000009210006415609"
    #    or with spaces "011 780 000009210006 415609"
    rib = ""
    # First try to find 24 consecutive digits in whitespace-stripped text
    stripped = re.sub(r'[\s\-]', '', text)
    rib_match = re.search(r'(\d{24})', stripped)
    if rib_match:
        rib = rib_match.group(1)
    else:
        # Fallback: find groups of digits separated by spaces that total 24
        digit_groups = re.findall(r'\b(\d{2,16})\b', text)
        buffer = ""
        for group in digit_groups:
            buffer += group
            if len(buffer) == 24:
                rib = buffer
                break
            elif len(buffer) > 24:
                buffer = group  # Reset

    # 3. SWIFT Code (8 or 11 alphanumeric characters)
    swift = None
    swift_match = re.search(r'(?:SWIFT|BIC)\s*[:\-]?\s*([A-Z0-9]{8,11})', text, re.IGNORECASE)
    if swift_match:
        swift = swift_match.group(1)

    # 4. Edition Date (e.g. "25/04/2022", "27/01/2023")
    date_ed = None
    # Look for dates at the end of the document (near "Fait à")
    date_match = re.search(r'Fait\s+[àa]\s+\w+\s+(?:le\s+)?(\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
    if not date_match:
        # Any date in the document
        date_match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
    if date_match:
        date_ed = date_match.group(1)

    return ExtractedRIB(
        raw_text=text,
        raison_sociale=owner,
        rib=rib,
        swift_code=swift,
        date_edition=date_ed
    )
