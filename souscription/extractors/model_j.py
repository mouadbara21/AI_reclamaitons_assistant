"""
Parser for Modèle J (Registre de Commerce) documents.
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

def parse_model_j(text: str) -> ExtractedModelJ:
    """
    Parses the text content of a Modèle J document and returns structured Pydantic object.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # 1. Dénomination / Raison Sociale
    denom = ""
    for i, line in enumerate(lines):
        if "Dénomination" in line:
            # Look at subsequent lines
            for j in range(1, 4):
                if i + j < len(lines):
                    next_line = lines[i + j]
                    # Skip labels, sigle headers, and corrupted greek lines
                    if is_corrupted_greek(next_line) or "sigle" in next_line.lower():
                        continue
                    denom = clean_whitespace(next_line)
                    break
            break
            
    # 2. RC number (Registre du Commerce)
    rc_num = ""
    rc_match = re.search(r'Copie des Inscriptions Portées au registre analytique N°\s*:\s*(\d+)', text, re.IGNORECASE)
    if not rc_match:
        rc_match = re.search(r'analytique N°\s*:\s*(\d+)', text, re.IGNORECASE)
    if rc_match:
        rc_num = rc_match.group(1)
        
    # 3. City of Registry
    rc_city = "Casablanca"  # Default fallback based on standard court header
    city_match = re.search(r'Tribunal de commerce\s*\n\s*(.*?)\n', text, re.IGNORECASE)
    if city_match:
        # Check if the extracted city is corrupted greek
        val = clean_whitespace(city_match.group(1))
        if not is_corrupted_greek(val):
             rc_city = val
        else:
             # Find another occurrence of city (e.g. "Casablanca , Le Secrétaire greffier")
             sec_match = re.search(r'([A-Za-z]+)\s*,\s*Le Secrétaire greffier', text)
             if sec_match:
                  rc_city = sec_match.group(1)
        
    # 4. ICE (15 digits)
    ice = ""
    ice_match = re.search(r'\(N° I.C.E\)\s*:\s*(\d+)', text, re.IGNORECASE)
    if not ice_match:
        ice_match = re.search(r'00\d{13}|\b\d{15}\b', text)
    if ice_match:
        ice = ice_match.group(0).replace(":", "").replace(" ", "").strip()
        ice = re.sub(r'\D', '', ice)
        
    # 5. Forme Juridique
    forme = "SOCIETE A RESPONSABILITE LIMITEE A ASSOCIE UNIQUE"  # fallback
    forme_match = re.search(r'Forme Juridique\s*\n\s*(.*?)\n', text, re.IGNORECASE)
    if forme_match:
        val = clean_whitespace(forme_match.group(1))
        if not is_corrupted_greek(val):
             forme = val
        else:
             # Look at next line
             for i, line in enumerate(lines):
                  if "Forme Juridique" in line:
                       if i + 2 < len(lines) and not is_corrupted_greek(lines[i+2]):
                            forme = lines[i+2]
                            break
        
    # 6. Capital Social
    capital = None
    capital_match = re.search(r'Capital Social\(Devise\)\s*\n\s*([\d\s,\.]+)\s*MAD', text, re.IGNORECASE)
    if not capital_match:
         capital_match = re.search(r'Capital Social.*?([\d\s,\.]+)\s*MAD', text, re.IGNORECASE)
    if capital_match:
        try:
            val_str = capital_match.group(1).replace(",", ".").replace(" ", "")
            # remove non-digit characters except dot
            val_str = re.sub(r'[^\d\.]', '', val_str)
            capital = float(val_str)
        except Exception:
            pass
            
    # 7. Siège Social
    siege = ""
    for i, line in enumerate(lines):
        if "Siège Social" in line or "Siege Social" in line:
             for j in range(1, 4):
                  if i + j < len(lines):
                       next_line = lines[i + j]
                       if is_corrupted_greek(next_line):
                            continue
                       siege = clean_whitespace(next_line)
                       break
             break
        
    # 8. Date Immatriculation
    date_immat = ""
    date_match = re.search(r'Date Immatriculation\s*\n\s*([\d/]+)', text, re.IGNORECASE)
    if date_match:
        date_immat = date_match.group(1)
    else:
        # Fallback: search for date pattern in lines following "Date Immatriculation"
        for i, line in enumerate(lines):
            if "Date Immatriculation" in line:
                if i + 1 < len(lines) and re.match(r'\d{2}/\d{2}/\d{4}', lines[i+1]):
                    date_immat = lines[i+1]
                elif i + 2 < len(lines) and re.match(r'\d{2}/\d{2}/\d{4}', lines[i+2]):
                    date_immat = lines[i+2]
                break
        
    # 9. Activité
    activite = ""
    for i, line in enumerate(lines):
        if "Activité" in line or "Activite" in line:
             for j in range(1, 4):
                  if i + j < len(lines):
                       next_line = lines[i + j]
                       if is_corrupted_greek(next_line):
                            continue
                       activite = clean_whitespace(next_line)
                       break
             break
        
    # 10. Dirigeants / Gérants
    gerants_list = []
    gerant_matches = re.finditer(r'([A-Z\s]+)\s*\(\s*C\.I\.N\.\s*:\s*([A-Z0-9]+)\)', text)
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
        date_certification=date_cert
    )
