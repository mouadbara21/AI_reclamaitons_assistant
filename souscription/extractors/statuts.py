"""
Parser for Statuts de la Société (Articles of Association) documents.

Layout reference:
  - Title: "STATUTS DE LA SOCIETE ..." or "LES STATUTS"
  - Contains: Legal form, Capital social, Gérant designation.
  - May be scanned (OCR) or digital PDF.
"""

import re
from souscription.models.document import ExtractedStatuts
from souscription.utils.text_cleaner import clean_whitespace


def parse_statuts(text: str) -> ExtractedStatuts:
    """
    Parses Statuts text content and returns a structured Pydantic object.

    Extracts structural fields: legal form, capital amount, and gérant name
    from the articles of association. These are used for cross-reference
    validation against other documents.
    """
    # 1. Forme Juridique — look for common legal form phrases
    forme = None
    forme_patterns = [
        r'SOCIETE\s+A\s+RESPONSABILITE\s+LIMITEE\s+A\s+ASSOCIE\s+UNIQUE',
        r'SOCIETE\s+A\s+RESPONSABILITE\s+LIMITEE',
        r'SOCIETE\s+ANONYME',
        r'SOCIETE\s+EN\s+NOM\s+COLLECTIF',
        r'\bSARL\s*(?:AU|A\.U\.)\b',
        r'\bSARL\b',
        r'\bSA\b(?!\s*(?:capital|siège))',  # Avoid matching "SA" in "SA capital"
        r'\bSNC\b',
    ]
    for pattern in forme_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            forme = clean_whitespace(match.group(0).upper())
            break

    # 2. Capital social
    capital = None
    # Pattern: "CAPITAL ... 100 000,00 DIRHAMS" or "capital social de 10.000 DH"
    capital_patterns = [
        r'CAPITAL\s*(?:SOCIAL)?\s*.*?([\d\s\.]+),\d{2}\s*(?:DIRHAMS|DH)',
        r'capital\s+(?:social\s+)?(?:de\s+|est\s+fix[ée]\s+[àa]\s+)([\d\s\.]+)\s*(?:DIRHAMS|DH|MAD)',
        r'([\d\s\.]+),\d{2}\s*(?:DIRHAMS|DH|MAD)',
    ]
    for pattern in capital_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                val_str = match.group(1).replace(" ", "").replace(".", "")
                capital = float(val_str)
                break
            except (ValueError, AttributeError):
                continue

    # 3. Gérant name
    gerant = None
    gerant_patterns = [
        r'(?:Monsieur|Madame|M\.|Mme)\s+([A-Za-zÀ-ÿ\s\-]+?)\s+est\s+(?:d[ée]sign[ée]|nomm[ée])',
        r'(?:G[ée]rant|G[ée]rante)\s*:\s*(?:Monsieur|Madame|M\.|Mme)?\s*([A-Za-zÀ-ÿ\s\-]+)',
        r'(?:d[ée]sign[ée]|nomm[ée])\s+(?:en\s+qualit[ée]\s+de\s+)?[Gg][ée]rant\s*(?::\s*)?\s*(?:Monsieur|Madame|M\.|Mme)?\s*([A-Za-zÀ-ÿ\s\-]+)',
    ]
    for pattern in gerant_patterns:
        match = re.search(pattern, text)
        if match:
            gerant = clean_whitespace(match.group(1))
            break

    return ExtractedStatuts(
        raw_text=text,
        capital_social=capital,
        forme_juridique=forme,
        gerant_name=gerant
    )
