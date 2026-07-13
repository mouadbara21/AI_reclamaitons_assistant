"""
OCR extractor module for scanned image-only PDFs.
Includes mock fallback database for the sample scanned documents to allow local testing.

Production deployment: Replace `run_ocr()` body with PaddleOCR or Tesseract calls.
"""

import os
from souscription.models.enums import DocumentType

# Pre-transcribed mock texts for the two scanned sample documents in this workspace.
# In production, this dict would be empty and the real OCR engine would handle all files.
MOCK_OCR_DB = {
    "AttestationRIB-Bank of affrica.pdf": """
BANK OF AFRICA
BMCE GROUP

Pôle Corporate & Investment Banking
Direction des Grandes Entreprises

ATTESTATION DE RIB

Nous soussignés, BANK OF AFRICA, Société Anonyme au Capital de DHS 2.056.066.480,00
dont le Siège Social est à CASABLANCA 140, Avenue HASSAN II,

Attestons que la relation MEDI TELECOM dont le siège social est Immeubles Les Quatre
Temps La Colline Sidi Maarouf 20270 Casablanca est titulaire sur nos livres d'un compte courant sous
le numéro :

011780000009210006415609

Code Swift : BMCEMAMC

La présente Attestation, a été délivrée à la demande de l'intéressé, pour servir et valoir ce que de droit.

Fait à Casablanca 25/04/2022
""",

    "Copie d'un document justifiant la categorie de l'operateur .pdf": """
Attestation de domiciliation

Nous soussignés la société S... S.A.R.L, Société à responsabilité limitée, sise au
46, Boulevard Zerktouni, 1er étage Bureau N°3, Casablanca, inscrite au registre de commerce
de Casablanca sous le numéro 289895.

Déclare par la présente, domicilier la société L... SARL AU,
représentée par Mme CAL, de Nationalité Marocaine, titulaire CIN N°
BK123456, et ce à compter du 05/01/2026.

Au 46, Boulevard Zerktouni, 1er étage Bureau N°3, Casablanca.

Nous déclarons en outre avoir pris connaissance qu'en application des dispositions de l'article
93 du CRCP, les rôles d'impôts, états de produits et autres titres de perception régulièrement
émis sont exécutoires contre les redevables qui y sont inscrits, toutes autres personnes auprès
desquelles les redevables ont élu domicile fiscal, avec leur accord.

Les personnes auprès desquelles les redevables ont élu domicile fiscal avec leur accord,
peuvent, de ce fait, faire l'objet d'action en recouvrement au même titre que les redevables à
raison des créances dues aux titres de l'activité concernée par la durée de la domiciliation.

Fait à Casablanca, le 27/02/2026.

Société L... SARL
M... ANICHICH
RC: 289895 / IF: 14458189
"""
}


def _normalize_filename(name: str) -> str:
    """Normalize quote characters and whitespace in filenames for matching."""
    return name.replace("\u2019", "'").replace("\u2018", "'").strip()


def run_ocr(pdf_path: str) -> str:
    """
    Extracts text from a scanned image PDF.

    Current implementation: checks the mock database for known sample files.
    Production implementation: call PaddleOCR or Tesseract here.

    Args:
        pdf_path: Absolute path to the scanned PDF file.

    Returns:
        Extracted text content.

    Raises:
        NotImplementedError: If no mock text is available and no real OCR engine
            is configured.
    """
    fname = os.path.basename(pdf_path)
    normalized = _normalize_filename(fname)

    # 1. Direct match
    if fname in MOCK_OCR_DB:
        return MOCK_OCR_DB[fname]

    # 2. Normalized match (handles curly quotes vs straight quotes)
    for mock_name, text in MOCK_OCR_DB.items():
        if _normalize_filename(mock_name) == normalized:
            return text

    # 3. No match — suggest deploying a real OCR engine
    raise NotImplementedError(
        f"Real OCR is not configured for file: {fname}. "
        "Deploy PaddleOCR (recommended) or Tesseract and update this function."
    )
