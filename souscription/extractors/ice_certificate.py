"""
Parser for Certificat de l'Identifiant Commun de l'Entreprise (ICE Certificate) documents.

Layout reference (OMPIC-issued certificate):
  - Header: "CERTIFICAT DE L'IDENTIFIANT COMMUN DE L'ENTREPRISE"
  - Structured table with: Dénomination, ICE, IF, RC, CNSS, Sigle, etc.
  - Sigle may appear on page 2 or as a secondary label.
"""

import re
from souscription.models.document import ExtractedICECertificate
from souscription.utils.text_cleaner import clean_whitespace


def parse_ice_certificate(text: str) -> ExtractedICECertificate:
    """
    Parses the text of an ICE Certificate and returns a structured Pydantic object.
    
    All values extracted via generic regex — no hardcoded defaults.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # 1. ICE Number (15 digits, usually starting with 00)
    ice = ""
    ice_match = re.search(r'\b(00\d{13})\b', text)
    if not ice_match:
        ice_match = re.search(r'\b(\d{15})\b', text)
    if ice_match:
        ice = ice_match.group(1)

    # 2. Dénomination (company full legal name)
    #    Typically appears after "Dénomination" label or near the top as a prominent block.
    denom = ""
    denom_anchor = re.search(r'[Dd][ée]nomination\s*(?:de l.entreprise)?\s*[:\-]?\s*(.+)', text)
    if denom_anchor:
        denom = clean_whitespace(denom_anchor.group(1))
    else:
        # Look for large uppercase block before the table structure
        for line in lines:
            if line.isupper() and len(line) > 10 and not re.search(r'CERTIFICAT|IDENTIFIANT|COMMUN|ENTREPRISE|OMPIC|MAROC', line):
                denom = clean_whitespace(line)
                break

    # 3. Identifiant Fiscal (IF)
    if_num = ""
    if_match = re.search(r'(?:Identifiant\s+)?Fiscal\s*[:\-]?\s*(\d{7,9})', text, re.IGNORECASE)
    if not if_match:
        if_match = re.search(r'I\.?F\.?\s*[:\-]?\s*(\d{7,9})', text, re.IGNORECASE)
    if if_match:
        if_num = if_match.group(1)

    # 4. RC Number and City (e.g. "1107/AGADIR" or "RC : 370621 / Casablanca")
    rc_num = ""
    rc_city = ""
    rc_match = re.search(r'(?:R\.?C\.?\s*[:\-]?\s*)?(\d{3,8})\s*/\s*([A-Za-z\s]+)', text)
    if rc_match:
        rc_num = rc_match.group(1)
        rc_city = clean_whitespace(rc_match.group(2).title())

    # 5. Sigle (abbreviation / trade name, may be on a second page)
    sigle = None
    sigle_match = re.search(r'[Ss]igle\s*[:\-]?\s*(.+)', text)
    if sigle_match:
        sigle = clean_whitespace(sigle_match.group(1))
    else:
        # Some ICE certs list the sigle on page 2 as a standalone uppercase line
        # that is much shorter than the denomination
        if denom and len(denom) > 20:
            for line in lines:
                if line.isupper() and 3 < len(line) < len(denom) // 2:
                    if not re.search(r'CERTIFICAT|IDENTIFIANT|COMMUN|ENTREPRISE|OMPIC|MAROC|PAGE', line):
                        sigle = clean_whitespace(line)
                        break

    # 6. Edition Date
    date_ed = ""
    date_match = re.search(r'(\d{1,2}/\d{2}/\d{4})', text)
    if date_match:
        date_ed = date_match.group(1)

    return ExtractedICECertificate(
        raw_text=text,
        denomination=denom,
        ice=ice,
        if_number=if_num,
        rc_number=rc_num,
        rc_city=rc_city,
        sigle=sigle,
        date_edition=date_ed
    )
