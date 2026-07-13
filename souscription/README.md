# PortNet Document Verification Pipeline

Automated document verification system for operator subscription submissions at PortNet Morocco.

## Overview

When an economic operator subscribes to PortNet, they submit 7-9 administrative documents (Modèle J, Document IF, ICE Certificate, Taxe Professionnelle, RIB Attestation, Statuts, CIN, and category justification). This pipeline:

1. **Classifies** each uploaded PDF by detecting structural anchor text
2. **Extracts** fields using PyMuPDF (digital PDFs) or OCR (scanned images)
3. **Validates** checksums (RIB mod-97, ICE mod-97, MRZ 7-3-1)
4. **Cross-references** all documents against each other and the digital form data
5. **Generates** a structured validation report (VALID / WARNING / INVALID)

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the full test suite
python -m pytest tests/ -v
```

## Project Structure

```
souscription/
├── config/            # Thresholds, regex registry, settings
├── models/            # Pydantic data schemas
├── utils/             # Text cleaning, fuzzy matching, numeral normalization
├── validators/        # Checksums, format checks, recency, cross-reference
├── extractors/        # Document-specific parsers + OCR
├── pipeline/          # Classifier + orchestrator
└── tests/             # Unit + integration tests
```

## Key Algorithms

- **RIB Validation**: `int(rib_24_digits) % 97 == 0`
- **ICE Validation**: `key = 97 - ((base_13 × 100) % 97)`
- **MRZ Check Digits**: ICAO Doc 9303 weights `7, 3, 1`
- **Fuzzy Name Matching**: `rapidfuzz.token_set_ratio ≥ 85%`
- **Fuzzy Address Matching**: `rapidfuzz.token_set_ratio ≥ 75%`

## OCR Status

Currently uses mock OCR for the 2 scanned sample documents. For production, deploy PaddleOCR or Tesseract — see `extractors/ocr_extractor.py`.
