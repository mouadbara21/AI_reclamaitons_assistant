"""
Parser for Modèle J (Registre de Commerce) documents.

CRITICAL LAYOUT NOTE:
  In the Model J PDF text layer, the VALUES appear BEFORE their labels.
  Example:
    Line 133: MEDI T ELECOM S.A.     ← VALUE
    Line 134: Sigle:                  ← next field
    Line 142: Dénomination            ← LABEL (appears AFTER the value!)

  This is because the PDF renders a two-column table and the text
  extraction reads left-to-right, top-to-bottom, which often places
  the value cell text before the label cell text.

  STRATEGY: Instead of "look after the label", we now search the
  raw text using known value-proximity patterns OR look backwards.
"""

import re
from typing import Optional
from souscription.models.document import ExtractedModelJ, Gerant
from souscription.utils.text_cleaner import clean_whitespace


def is_corrupted_greek(text: str) -> bool:
    """
    Detects if a string contains corrupted PDF encoding characters (Greek block U+0370 to U+03FF).
    """
    for char in text:
        if 0x0370 <= ord(char) <= 0x03FF:
            return True
    return False


def _is_label_line(line: str) -> bool:
    """Check if a line looks like a form field label rather than a value."""
    label_markers = [
        "Dénomination", "Siège Social", "Forme Juridique", "Capital Social",
        "Date Immatriculation", "Date Début", "Date Fin", "Activité",
        "Origine fonds", "Enseigne", "Sigle", "Dirigeant", "Qualité",
        "Représenté Par", "Copie Certifiée", "Succursales", "N° Chronologique",
        "Personnes Morales", "Identification de l'établissement",
        "Tribunal", "Registre du Commerce", "Royaume du Maroc",
        "Ministère de la Justice", "Page ", "P. Normale",
        "CODE DEMANDE", "NEANT", "CREATION",
    ]
    stripped = line.strip()
    # Arabic-only lines are labels
    if stripped and all(
        ('\u0600' <= c <= '\u06FF' or '\u0750' <= c <= '\u077F'
         or '\uFB50' <= c <= '\uFDFF' or '\uFE70' <= c <= '\uFEFF'
         or c in ' .:()،-/') for c in stripped
    ):
        return True
    for label in label_markers:
        if label.lower() in stripped.lower():
            return True
    return False


def parse_model_j(text: str) -> ExtractedModelJ:
    """
    Parses the text content of a Modèle J document and returns structured Pydantic object.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # 1. Dénomination / Raison Sociale
    # The company name appears as a standalone line that is NOT a label,
    # NOT Arabic, and typically contains "S.A." / "SARL" or is near line 133.
    # Best strategy: look for a line matching a company-name pattern
    # near the beginning of the French section of the document.
    denom = ""
    # Strategy A: Find by pattern — line containing S.A. or SARL or S.A.R.L
    for line in lines:
        if re.search(r'\b(?:S\.A\.|SARL|S\.A\.R\.L|S\.A)\b', line, re.IGNORECASE):
            candidate = clean_whitespace(line)
            # Exclude known labels and structure lines
            if not _is_label_line(candidate) and len(candidate) > 3:
                # Clean up OCR artifacts like "MEDI T ELECOM" → "MEDI TELECOM"
                denom = re.sub(r'\s+', ' ', candidate).strip()
                break

    # Strategy B: Look for standalone line after "Copie des Inscriptions"
    # and before "Sigle:" — the denomination is typically there
    if not denom:
        in_data_zone = False
        for i, line in enumerate(lines):
            if "Copie des Inscriptions" in line or "registre analytique" in line.lower():
                in_data_zone = True
                continue
            if in_data_zone:
                if is_corrupted_greek(line) or _is_label_line(line):
                    continue
                candidate = clean_whitespace(line)
                if len(candidate) > 3 and not re.match(r'^\d', candidate):
                    denom = candidate
                    break

    # 2. RC number (Registre du Commerce)
    rc_num = ""
    rc_match = re.search(r'registre analytique N°\s*:\s*(\d+)', text, re.IGNORECASE)
    if not rc_match:
        rc_match = re.search(r'RC N°\s*:\s*(\d+)', text, re.IGNORECASE)
    if rc_match:
        rc_num = rc_match.group(1)

    # 3. City of Registry
    rc_city = ""
    sec_match = re.search(r'([A-Za-z]+)\s*,\s*Le Secrétaire greffier', text)
    if sec_match:
        rc_city = sec_match.group(1)
    if not rc_city:
        city_match = re.search(r'Tribunal de\s*commerce\s*\n\s*(\w+)', text, re.IGNORECASE)
        if city_match:
            val = clean_whitespace(city_match.group(1))
            if not is_corrupted_greek(val):
                rc_city = val

    # 4. ICE (15 digits)
    ice = ""
    ice_match = re.search(r'\(N° I\.C\.E\)\s*:\s*(\d+)', text, re.IGNORECASE)
    if not ice_match:
        ice_match = re.search(r'00\d{13}', text)
    if ice_match:
        ice = re.sub(r'\D', '', ice_match.group(0))

    # 5. Forme Juridique
    forme = ""
    # In the text, the forme juridique value appears as a standalone line
    # like "SOCIETE ANONYME" BEFORE the "Forme Juridique" label
    forme_candidates = ["SOCIETE ANONYME", "SOCIETE A RESPONSABILITE LIMITEE",
                        "SARL AU", "S.A.R.L.A.U", "SARL"]
    for line in lines:
        for fc in forme_candidates:
            if fc in line.upper() and "Forme" not in line:
                forme = clean_whitespace(line)
                break
        if forme:
            break

    # 6. Capital Social
    capital = None
    capital_match = re.search(r'([\d\s,\.]+)\s*MAD', text, re.IGNORECASE)
    if capital_match:
        try:
            val_str = capital_match.group(1).replace(",", ".").replace(" ", "")
            val_str = re.sub(r'[^\d\.]', '', val_str)
            capital = float(val_str)
        except Exception:
            pass

    # 7. Siège Social
    # The address appears as a standalone data line containing street info
    # BEFORE the "Siège Social" label. Look for "Immeubles", "Rue", etc.
    siege = ""
    for line in lines:
        cleaned = clean_whitespace(line)
        if is_corrupted_greek(cleaned) or _is_label_line(cleaned):
            continue
        # Skip ICE / N° I.C.E lines
        if 'I.C.E' in cleaned or 'ICE' in cleaned.upper():
            continue
        # Match typical Moroccan address patterns
        if re.search(r'(?:Immeubles|Rue|Avenue|Boulevard|Bd|Lot|Quartier|Hay|Bloc|Résidence)',
                     cleaned, re.IGNORECASE) and len(cleaned) > 15:
            siege = cleaned
            break

    # 8. Date Immatriculation
    date_immat = ""
    # Look for a date pattern (DD/MM/YYYY) that appears near the data section,
    # after "CREATION" or after "Registre du Commerce" header
    dates_found = re.findall(r'(\d{2}/\d{2}/\d{4})', text)
    # Filter out certification timestamps (which have HH:MM:SS appended)
    cert_dates = set(re.findall(r'(\d{2}/\d{2}/\d{4})\s+\d{2}:\d{2}:\d{2}', text))
    for d in dates_found:
        if d not in cert_dates:
            date_immat = d
            break

    # 9. Activité
    activite = ""
    # The activity line typically contains trade descriptions
    activity_patterns = [
        r'(?:IMPORT|EXPORT|COMMERCE|TRANSPORT|SERVICE|FABRICATION|INDUSTRI)',
    ]
    for line in lines:
        cleaned = clean_whitespace(line)
        if is_corrupted_greek(cleaned) or _is_label_line(cleaned):
            continue
        for pat in activity_patterns:
            if re.search(pat, cleaned, re.IGNORECASE) and len(cleaned) > 5:
                activite = cleaned
                break
        if activite:
            break

    # 10. Dirigeants / Gérants
    gerants_list = []
    gerant_matches = re.finditer(r'([A-Z][A-Z\s]+)\s*\(\s*C\.I\.N\.\s*:\s*([A-Z0-9]+)\)', text)
    for m in gerant_matches:
        name = clean_whitespace(m.group(1))
        cin = clean_whitespace(m.group(2))
        qualite = "Gerant"
        gerants_list.append(Gerant(nom_complet=name, cin=cin, qualite=qualite))

    # 11. Certification Date
    date_cert = ""
    cert_matches = re.findall(r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})', text)
    if cert_matches:
        date_cert = cert_matches[0]

    # 12. Domicilié chez (Domiciliary entity in Modèle J)
    dom_name = None
    dom_rc = None
    dom_match = re.search(
        r'Domicili[ée]\s+chez\s*:\s*\[?\s*(.+?)\s*(?:N[°o]?\s*R\.?C\.?|R\.?C\.?)\s*:\s*(\d+)',
        text, re.IGNORECASE)
    if not dom_match:
        dom_match = re.search(r'Domicili[ée]\s+chez\s*:\s*\[?\s*([A-Za-z0-9\s]+)', text, re.IGNORECASE)
        if dom_match:
            dom_name = clean_whitespace(dom_match.group(1))
            rc_in_dom = re.search(r'\b(\d{4,8})\b', dom_name)
            if rc_in_dom:
                dom_rc = rc_in_dom.group(1)
                dom_name = clean_whitespace(
                    re.sub(r'(?:N[°o]?\s*)?R\.?C\.?\s*:?\s*\d+.*', '', dom_name, flags=re.IGNORECASE))
    else:
        dom_name = clean_whitespace(dom_match.group(1))
        dom_rc = clean_whitespace(dom_match.group(2))

    return ExtractedModelJ(
        raw_text=text,
        denomination=denom,
        rc_number=rc_num,
        rc_city=rc_city,
        ice=ice,
        forme_juridique=forme,
        capital_social=capital,
        siege_social=siege,
        date_immatriculation=date_immat,
        activite=activite,
        gerants=gerants_list,
        date_certification=date_cert,
        domiciliary_name=dom_name,
        domiciliary_rc=dom_rc
    )
