"""
Parser for Certificat de l'Identifiant Commun de l'Entreprise (ICE Certificate) documents.

CRITICAL LAYOUT NOTE:
  The ICE certificate PDF text layer has this order:
    Line 296: CERTIFICAT DE L'IDENTIFIANT COMMUN DE L'ENTREPRISE  (header)
    Line 297: Numéro RC          ← LABEL
    Line 298: Dénomination       ← LABEL
    Line 299: Numéro CNSS        ← LABEL
    Line 300: Identifiant Fiscal ← LABEL
    ... Arabic labels ...
    Line 311: 32770927           ← IF value
    Line 312: 2131887            ← CNSS value
    Line 313: 429045/Casablanca  ← RC value
    Line 314: MEDI TELECOM S.A.  ← Denomination value

  STRATEGY: Don't use "line after Dénomination anchor".
  Instead, find the company name by looking for a line that matches
  company-name patterns (contains S.A., SARL, etc.) or by searching
  the "page 2" section which has "Dénomination" followed by the value.
"""

import re
from souscription.models.document import ExtractedICECertificate
from souscription.utils.text_cleaner import clean_whitespace


def _is_arabic_only(line: str) -> bool:
    """Check if a line consists only of Arabic characters and punctuation."""
    stripped = line.strip()
    if not stripped:
        return True
    return all(
        ('\u0600' <= c <= '\u06FF' or '\u0750' <= c <= '\u077F'
         or '\uFB50' <= c <= '\uFDFF' or '\uFE70' <= c <= '\uFEFF'
         or c in ' .:()،-/*') for c in stripped
    )


def _is_label(line: str) -> bool:
    """Check if a line is a form field label rather than a data value."""
    labels = [
        "Numéro RC", "Dénomination", "Numéro CNSS", "Identifiant Fiscal",
        "IDENTIFIANT COMMUN", "CERTIFICAT", "ENTREPRISE",
        "Informations de la Demande", "Informations Complémentaires",
        "Statut ICE", "LEGAL", "discordance", "rectification",
        "complémentaires", "rééditer",
    ]
    stripped = line.strip()
    for lbl in labels:
        if lbl.lower() in stripped.lower():
            return True
    return False


def parse_ice_certificate(text: str) -> ExtractedICECertificate:
    """
    Parses the text of an ICE Certificate and returns a structured Pydantic object.
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
    # STRATEGY: Find a line containing the legal form suffix (S.A., SARL, etc.)
    # that is NOT a label, NOT Arabic, and NOT a header.
    denom = ""
    # Strategy A: Look for company name pattern (contains S.A. / SARL / etc.)
    for line in lines:
        stripped = clean_whitespace(line)
        if _is_arabic_only(stripped) or _is_label(stripped) or len(stripped) < 3:
            continue
        if re.search(r'\b(?:S\.A\.|SARL|S\.A\.R\.L|S\.A)\b', stripped, re.IGNORECASE):
            # Exclude the email reference lines and disclaimer lines
            if '@' in stripped or '*' in stripped or 'mail' in stripped.lower():
                continue
            denom = stripped
            break

    # Strategy B: On page 2, "Dénomination" label is followed 2 lines later by the value
    if not denom:
        # Find last occurrence of "Dénomination" (page 2 section)
        last_denom_idx = -1
        for i, line in enumerate(lines):
            if "Dénomination" in line and "dénomination/" not in line.lower():
                last_denom_idx = i
        if last_denom_idx >= 0:
            for j in range(1, 5):
                idx = last_denom_idx + j
                if idx < len(lines):
                    candidate = clean_whitespace(lines[idx])
                    if (not _is_arabic_only(candidate) and not _is_label(candidate)
                            and len(candidate) > 3 and '@' not in candidate):
                        denom = candidate
                        break

    # 3. Identifiant Fiscal (IF) — typically 8 digits
    # In the ICE cert text, the IF appears as a standalone 8-digit number
    # on its own line (line 311: "32770927"). It is NOT near the
    # "Identifiant Fiscal" label (which is far above in the label block).
    # We must NOT match digits that are part of the 15-digit ICE number.
    if_num = ""
    all_8 = re.findall(r'\b(\d{8})\b', text)
    for candidate in all_8:
        # Ensure this 8-digit number is NOT a substring of the ICE number
        if ice and candidate in ice:
            continue
        if_num = candidate
        break

    # 4. RC Number and City (e.g. "429045/Casablanca")
    rc_num = ""
    rc_city = ""
    rc_match = re.search(r'(\d{3,8})\s*/\s*([A-Za-z][\w\s]*)', text)
    if rc_match:
        rc_num = rc_match.group(1)
        rc_city = clean_whitespace(rc_match.group(2))
        # Clean up: city should not include trailing company name
        # e.g. "Casablanca Medi Telecom S" → just "Casablanca"
        city_parts = rc_city.split()
        # Take only the first word (city name) if the rest looks like company name
        if len(city_parts) > 1:
            rc_city = city_parts[0]

    # 5. Sigle (abbreviation / trade name)
    sigle = None
    sigle_match = re.search(r'[Ss]igle\s*[:\-]?\s*(.+)', text)
    if sigle_match:
        val = clean_whitespace(sigle_match.group(1))
        if len(val) > 1 and not _is_arabic_only(val):
            sigle = val

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
