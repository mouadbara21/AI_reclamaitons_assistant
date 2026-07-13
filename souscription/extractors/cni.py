"""
Parser for CIN/CNIE (Carte Nationale d'Identité Électronique) documents.

Handles:
  - Front side: Visual fields (name, CIN number, photo)
  - Back side: Machine Readable Zone (MRZ) for TD1 format (3 lines × 30 chars)
  - MRZ check digit validation using ICAO Doc 9303 weights 7, 3, 1
"""

import re
from typing import Optional
from pydantic import BaseModel
from souscription.models.document import ExtractedDocument
from souscription.models.enums import DocumentType
from souscription.validators.checksum import calculate_mrz_check_digit


class ExtractedCNI(ExtractedDocument):
    """Structured fields extracted from a Moroccan CIN/CNIE."""
    document_type: DocumentType = DocumentType.CIN
    cin_number: str = ""
    last_name: str = ""
    first_name: str = ""
    date_of_birth: str = ""      # YYMMDD from MRZ
    sex: str = ""                 # M or F
    expiry_date: str = ""         # YYMMDD from MRZ
    nationality: str = "MAR"
    mrz_lines: list[str] = []
    mrz_valid: Optional[bool] = None  # None = no MRZ found


class MRZValidationResult(BaseModel):
    """Detailed results of MRZ check digit verification."""
    doc_number_cd_ok: bool = False
    dob_cd_ok: bool = False
    expiry_cd_ok: bool = False
    composite_cd_ok: bool = False
    all_ok: bool = False


def extract_mrz_lines(text: str) -> list[str]:
    """Extract the 3 MRZ lines (TD1, 30 chars each) from text.

    Robuste à l'OCR : on nettoie chaque ligne (on ne garde que A-Z 0-9 <),
    on accepte dès ~20 caractères avec assez de '<' (l'OCR tronque souvent les
    '<' de remplissage en fin de ligne), puis on complète à 30 (les '<' finaux
    sont des données optionnelles, sans effet sur les chiffres de contrôle).
    """
    candidates = []
    for line in text.split('\n'):
        clean = re.sub(r'[^A-Z0-9<]', '', line.upper())
        if len(clean) >= 20 and clean.count('<') >= 2:
            candidates.append(clean.ljust(30, '<')[:30])  # complète/tronque à 30

    # TD1 = 3 lignes ; on garde les 3 dernières (évite le bruit d'en-tête)
    if len(candidates) >= 3:
        return candidates[-3:]
    return candidates


def validate_mrz_td1(mrz_lines: list[str]) -> MRZValidationResult:
    """Validate MRZ check digits for TD1 format (3 lines × 30 chars).
    
    Check digit positions:
      - CD1: Line 1, pos 15 — computed over doc number (line 1, pos 6-14)
      - CD2: Line 2, pos 7  — computed over DOB (line 2, pos 1-6)
      - CD3: Line 2, pos 15 — computed over expiry date (line 2, pos 9-14)
      - CD4: Line 2, pos 30 — composite over multiple fields
    """
    result = MRZValidationResult()

    if len(mrz_lines) != 3:
        return result
    
    line1, line2, line3 = mrz_lines

    if len(line1) < 30 or len(line2) < 30:
        return result

    # CD1: Document number check digit
    doc_number = line1[5:14]    # Positions 6-14 (0-indexed: 5-13)
    cd1_actual = int(line1[14]) if line1[14].isdigit() else -1
    cd1_computed = calculate_mrz_check_digit(doc_number)
    result.doc_number_cd_ok = (cd1_actual == cd1_computed)

    # CD2: Date of birth check digit
    dob = line2[0:6]            # Positions 1-6 (0-indexed: 0-5)
    cd2_actual = int(line2[6]) if line2[6].isdigit() else -1
    cd2_computed = calculate_mrz_check_digit(dob)
    result.dob_cd_ok = (cd2_actual == cd2_computed)

    # CD3: Expiry date check digit
    expiry = line2[8:14]        # Positions 9-14 (0-indexed: 8-13)
    cd3_actual = int(line2[14]) if line2[14].isdigit() else -1
    cd3_computed = calculate_mrz_check_digit(expiry)
    result.expiry_cd_ok = (cd3_actual == cd3_computed)

    # CD4: Composite check digit
    # Computed over: doc_number + CD1 + DOB + CD2 + expiry + CD3 + optional data
    composite_data = line1[5:30] + line2[0:7] + line2[8:15] + line2[18:29]
    cd4_actual = int(line2[29]) if line2[29].isdigit() else -1
    cd4_computed = calculate_mrz_check_digit(composite_data)
    result.composite_cd_ok = (cd4_actual == cd4_computed)

    result.all_ok = all([
        result.doc_number_cd_ok,
        result.dob_cd_ok,
        result.expiry_cd_ok,
        result.composite_cd_ok
    ])

    return result


def parse_cni(text: str) -> ExtractedCNI:
    """
    Parses CIN/CNIE text content (front + back) and returns structured data.
    
    If MRZ is found on the back, validates all check digits automatically.
    If only the front is available, extracts what's visible.
    """
    # Try to extract MRZ lines
    mrz_lines = extract_mrz_lines(text)
    mrz_valid = None

    cin_number = ""
    last_name = ""
    first_name = ""
    dob = ""
    sex = ""
    expiry = ""

    if len(mrz_lines) == 3:
        # Full MRZ available — extract structured fields
        line1, line2, line3 = mrz_lines

        # Document number from MRZ (line 1, positions 6-14)
        cin_number = line1[5:14].replace('<', '').strip()

        # Date of birth (line 2, positions 1-6)
        dob = line2[0:6]

        # Sex (line 2, position 8)
        sex = line2[7]

        # Expiry date (line 2, positions 9-14)
        expiry = line2[8:14]

        # Name from line 3: SURNAME<<GIVEN<NAMES
        name_parts = line3.split('<<')
        if len(name_parts) >= 2:
            last_name = name_parts[0].replace('<', ' ').strip()
            first_name = name_parts[1].replace('<', ' ').strip()
        elif name_parts:
            last_name = name_parts[0].replace('<', ' ').strip()

        # Validate check digits
        mrz_result = validate_mrz_td1(mrz_lines)
        mrz_valid = mrz_result.all_ok
    else:
        # Front-only: try visual field extraction
        cin_match = re.search(r'\b([A-Z]{1,2}\d{5,7})\b', text)
        if cin_match:
            cin_number = cin_match.group(1)

        # Try to find name fields
        name_match = re.search(r'(?:Nom|NOM)\s*[:\-]?\s*([A-Za-zÀ-ÿ\s\-]+)', text)
        if name_match:
            last_name = name_match.group(1).strip()
        
        prenom_match = re.search(r'(?:Pr[ée]nom|PRENOM)\s*[:\-]?\s*([A-Za-zÀ-ÿ\s\-]+)', text)
        if prenom_match:
            first_name = prenom_match.group(1).strip()

    return ExtractedCNI(
        raw_text=text,
        cin_number=cin_number,
        last_name=last_name,
        first_name=first_name,
        date_of_birth=dob,
        sex=sex,
        expiry_date=expiry,
        mrz_lines=mrz_lines,
        mrz_valid=mrz_valid
    )


# Caractères possibles d'une MRZ (améliore fortement l'OCR).
_MRZ_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<"


def read_cnie_image(image_path: str) -> ExtractedCNI:
    """Lit une CNIE depuis une IMAGE (dos).

    La MRZ est en bas de la carte : on recadre le bas, on prétraite (gris +
    binarisation) et on OCR avec une liste de caractères restreinte (A-Z 0-9 <),
    ce qui fiabilise beaucoup la lecture des 3 lignes. Puis on parse + valide.
    """
    import numpy as np
    import pytesseract
    from PIL import Image
    from souscription.pipeline.preprocessor import preprocess

    img = np.array(Image.open(image_path).convert("RGB"))
    h = img.shape[0]
    crop = img[int(h * 0.55):, :]                 # ~45% inférieur = zone MRZ
    g = preprocess(crop, do_deskew=False)
    cfg = f"--psm 6 -c tessedit_char_whitelist={_MRZ_CHARS}"
    text = pytesseract.image_to_string(g, lang="eng", config=cfg)
    return parse_cni(text)
