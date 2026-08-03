"""
Parser for Taxe Professionnelle (Business Tax) registration documents.

Layout reference (AAC060B form):
  Text layer order for this document:
    Line 232: Modèle AAC060B-17I
    Line 236: CNI ou CS
    Line 237: Le contribuable désigné ci-dessous :
    Line 240: 32770927                    ← IF value
    Line 243: Est inscrit(e) au rôle de la taxe professionnelle de la commune de
    Line 244: COM.URB.CASABLANCA
    Line 250: 25200117                    ← TP value
    Line 254: Nom et prénom (s) / Raison sociale   ← LABEL (NOT value!)
    Line 257: 429045                      ← RC value
    Line 259: Immeubles Les Quatre Temps...  ← Address value
    Line 261: Identifiant commun de l'entreprise « ICE »  ← LABEL
    Line 262: 001512572000078             ← ICE value
    Line 267: ATTESTATIOND'INSCRIPTION
    Line 268: A LA TAXE PROFESSIONNELLE
    Line 290: MEDI TELECOM S.A.           ← Company name (at the end!)
"""

import re
from souscription.models.document import ExtractedTaxeProfessionnelle
from souscription.utils.text_cleaner import clean_whitespace


def _is_arabic_only(line: str) -> bool:
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
        "Nom et prénom", "Raison sociale", "CNI ou CS",
        "Le contribuable", "ci-dessous", "Est inscrit",
        "rôle de la taxe", "commune de", "Année",
        "N° d'identification", "En qualité de",
        "Principale activité", "Autres activités",
        "registre de commerce", "Identifiant commun",
        "Date de début", "Date d'édition",
        "Code de vérification", "Visa de l'administration",
        "ATTESTATION", "TAXE PROFESSIONNELLE",
        "Adresse", "AAC060B", "Modèle",
    ]
    stripped = line.strip()
    if not stripped or len(stripped) < 3:
        return True
    for lbl in labels:
        if lbl.lower() in stripped.lower():
            return True
    if stripped.endswith(':') and len(stripped) < 50:
        return True
    return False


def parse_taxe_professionnelle(text: str) -> ExtractedTaxeProfessionnelle:
    """
    Parses the text of a Taxe Professionnelle certificate and returns
    a structured Pydantic object.
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

    # 2. Identifiant Fiscal (IF) — near "identification fiscale" anchor
    if_num = ""
    if_anchor = re.search(r"N°\s*d'identification\s+fiscale\s*\n\s*(\d{7,9})", text, re.IGNORECASE)
    if if_anchor:
        if_num = if_anchor.group(1)
    else:
        if_anchor = re.search(r'(?:Identifiant|I\.?F)(?:\s+Fiscal)?\s*[:\-]?\s*(\d{7,9})', text, re.IGNORECASE)
        if if_anchor:
            if_num = if_anchor.group(1)
        elif all_8:
            if_num = all_8[0]

    # 3. TP Number (Taxe Professionnelle number)
    tp_num = ""
    tp_anchor = re.search(
        r"(?:N°\s*d'identification\s+à\s+la\s+)?[Tt]axe\s+[Pp]rofessionnelle\s*[:\-N°]*\s*(\d{7,9})",
        text, re.IGNORECASE)
    if tp_anchor:
        tp_num = tp_anchor.group(1)
    else:
        for candidate in all_8:
            if candidate != if_num and candidate not in ice:
                tp_num = candidate
                break

    # 4. RC Number
    rc_num = ""
    rc_anchor = re.search(
        r'(?:N°\s*du\s+)?(?:R\.?C\.?|[Rr]egistre\s+de\s+[Cc]ommerce)\s*[:\-N°]*\s*(\d{3,12})',
        text, re.IGNORECASE)
    if rc_anchor:
        rc_num = rc_anchor.group(1)

    # 5. Raison Sociale / Company Name
    # The company name in the AAC060B form appears as a standalone line
    # containing the legal form suffix (S.A., SARL, etc.)
    # It often appears near the end of the document (e.g. line 290)
    denom = ""
    for line in lines:
        stripped = clean_whitespace(line)
        if _is_arabic_only(stripped) or _is_label(stripped):
            continue
        if re.search(r'\b(?:S\.A\.?|SARL|S\.A\.R\.L)\b', stripped, re.IGNORECASE):
            if len(stripped) > 3:
                denom = stripped
                # Don't break - take the LAST match as it's likely the actual
                # company name (the first match might be something else)

    # Fallback: if no legal-form suffix found, look for prominent uppercase line
    if not denom:
        for line in reversed(lines):
            stripped = clean_whitespace(line)
            if (_is_arabic_only(stripped) or _is_label(stripped)
                    or len(stripped) < 5):
                continue
            if stripped.isupper():
                denom = stripped
                break

    # 6. CNI / CIN of representative
    cni = None
    cni_match = re.search(r'\b([A-Z]{1,2}\d{5,7})\b', text)
    if cni_match:
        cni = cni_match.group(1)

    # 7. Siège Social (address)
    # The address may not contain RUE/AVENUE — it could be "Immeubles..."
    siege = ""
    # Look for "Adresse" anchor and get the next data line
    for i, line in enumerate(lines):
        if re.search(r'^Adresse$', line.strip(), re.IGNORECASE):
            # Look at subsequent lines for address data
            for j in range(1, 4):
                if i + j < len(lines):
                    candidate = clean_whitespace(lines[i + j])
                    if (not _is_arabic_only(candidate) and not _is_label(candidate)
                            and len(candidate) > 10):
                        siege = candidate
                        break
            if siege:
                break

    # Fallback: find address by pattern matching
    if not siege:
        for line in lines:
            stripped = clean_whitespace(line)
            if _is_arabic_only(stripped) or _is_label(stripped):
                continue
            if re.search(
                r'(?:Immeubles|Rue|Avenue|Boulevard|Bd|Lot|Quartier|Hay|Résidence|Zone)\s+.{10,}',
                stripped, re.IGNORECASE
            ):
                siege = stripped
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
