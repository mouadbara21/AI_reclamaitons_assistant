"""
Parser for Document IF (Bulletin de Notification d'Identifiant Fiscal) documents.

Layout reference (AAC140B form):
  Text layer order for this document:
    Line 346: Modèle AAC140B-07I
    Line 349: BULLETIN DE NOTIFICATION DU
    Line 350: N° D'IDENTIFICATION FISCALE
    Line 359: NOM ET PRENOM (S) / RAISON SOCIALE :
    Line 360: IMPOT SUR LE REVENU
    Line 363: MEDI TELECOM S.A
    Line 366: SA - SOCIETE ANONYM -
    Line 367: 429045/CASABLANCA
    Line 371: IDENTIFIANT DE LA TAXE PROFESSIONNELLE :25200117
    Line 375: Immeubles Les Quatre Temps, La Colline, Sidi Maarouf, 20270
"""

import re
from souscription.models.document import ExtractedDocumentIF
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
    """Check if a line is a form label rather than a data value."""
    labels = [
        "NOM ET PRENOM", "RAISON SOCIALE", "N° CNI", "CARTE DE SEJOUR",
        "FORME JURIDIQUE", "REGISTRE DE COMMERCE", "N° ICE",
        "IDENTIFIANT DE LA TAXE", "ADRESSE DU DOMICILE", "ADRESSE DU DIRIGEANT",
        "SIEGE SOCIAL", "PRINCIPAL", "PROFESSION", "ACTIVITE",
        "BULLETIN DE NOTIFICATION", "IDENTIFICATION FISCALE",
        "Service d'assiette", "Recette de l'administration",
        "Perception", "Identification du contribuable",
        "Visa de l'Administration", "SUBDIVISION", "RECETTE DE",
        "BOULEVARD BRAHIM", "Code de vérification",
        "IMPOT SUR LE REVENU", "IMPOT SUR LES SOCIETES",
        "TAXE SUR LA VALEUR", "Ce numéro", "Par ailleurs",
        "dispositions", "Adresse :", "AAC140B",
    ]
    stripped = line.strip()
    if not stripped or len(stripped) < 3:
        return True
    for lbl in labels:
        if lbl.lower() in stripped.lower():
            return True
    # Labels ending with ":"
    if stripped.endswith(':') and len(stripped) < 50:
        return True
    return False


def parse_document_if(text: str) -> ExtractedDocumentIF:
    """
    Parses the text of a Bulletin de Notification d'Identifiant Fiscal
    and returns a structured Pydantic object.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # 1. Raison Sociale / Dénomination
    # Strategy A: Find line containing legal-form suffix (S.A., SARL, etc.)
    # that is NOT a label
    denom = ""
    for line in lines:
        stripped = clean_whitespace(line)
        if _is_arabic_only(stripped) or _is_label(stripped):
            continue
        if re.search(r'\b(?:S\.A\.?|SARL|S\.A\.R\.L)\b', stripped, re.IGNORECASE):
            # Exclude legal form description lines like "SA - SOCIETE ANONYM"
            if re.match(r'^(?:SA\s*-|SARL\s*-)', stripped, re.IGNORECASE):
                continue
            denom = stripped
            break

    # Strategy B: Look after "RAISON SOCIALE" anchor
    if not denom:
        match = re.search(r'RAISON SOCIALE\s*:\s*\n\s*(.+)', text, re.IGNORECASE)
        if match:
            candidate = clean_whitespace(match.group(1))
            if not _is_label(candidate) and len(candidate) > 3:
                denom = candidate

    # 2. Forme juridique
    forme = ""
    forme_match = re.search(
        r'(SA\s*-\s*SOCIETE\s+ANONYM[^,\n]*|'
        r'SARL\s*-?\s*ASSOCIE\s*UNIQUE\s*-?|'
        r'SARL\s*AU|SARL|S\.A\.R\.L|SA|SNC|'
        r'SOCIETE\s+A\s+RESPONSABILITE\s+LIMITEE[^,\n]*)',
        text, re.IGNORECASE
    )
    if forme_match:
        forme = clean_whitespace(forme_match.group(0))

    # 3. RC Number and City (e.g. "429045/CASABLANCA")
    rc_num = ""
    rc_city = ""
    rc_match = re.search(r'(\d{3,8})\s*/\s*([A-Z][A-Za-z\s]+)', text)
    if rc_match:
        rc_num = rc_match.group(1)
        rc_city = clean_whitespace(rc_match.group(2))
        # Take only city name, not trailing text
        city_parts = rc_city.split()
        if city_parts:
            rc_city = city_parts[0]

    # 4. ICE (15 digits, usually starting with 00)
    ice = ""
    ice_match = re.search(r'\b(00\d{13})\b', text)
    if not ice_match:
        ice_match = re.search(r'\b(\d{15})\b', text)
    if ice_match:
        ice = ice_match.group(1)

    # 5. Identifiant Fiscal (IF) — typically 8 digits
    if_num = ""
    # The IF number appears at the top of the document as a prominent number
    if_anchor = re.search(r'Identification\s+Fiscale[^\d]*(\d{7,9})', text, re.IGNORECASE)
    if if_anchor:
        if_num = if_anchor.group(1)
    else:
        # Look for standalone 8-digit number at the beginning of the document
        all_8digits = re.findall(r'\b(\d{8})\b', text)
        for candidate in all_8digits:
            if candidate != rc_num and candidate not in ice:
                if_num = candidate
                break

    # 6. Taxe Professionnelle Number
    tp_num = ""
    tp_anchor = re.search(r'Taxe\s+Professionnelle\s*[:\-N°]*\s*(\d{7,9})', text, re.IGNORECASE)
    if tp_anchor:
        tp_num = tp_anchor.group(1)
    else:
        all_8digits = re.findall(r'\b(\d{8})\b', text)
        for candidate in all_8digits:
            if candidate != if_num and candidate != rc_num and candidate not in ice:
                tp_num = candidate
                break

    # 7. Siège Social (address)
    # The actual address in this document type is "Immeubles Les Quatre Temps..."
    # which does NOT contain RUE/AVENUE/BOULEVARD.
    # Strategy: Find lines that look like a Moroccan address.
    siege = ""
    addr_patterns = [
        r'(?:Immeubles|Rue|Avenue|Boulevard|Bd|Lot|Quartier|Hay|Bloc|Résidence|Zone)\s+.{10,}',
        r'\d+\s+(?:Rue|Avenue|Boulevard|Bd|Av\.?)\s+.{5,}',
    ]
    for line in lines:
        stripped = clean_whitespace(line)
        if _is_arabic_only(stripped) or _is_label(stripped):
            continue
        for pat in addr_patterns:
            if re.search(pat, stripped, re.IGNORECASE):
                siege = stripped
                break
        if siege:
            break

    # 8. Edition Date
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
