"""
FastAPI backend for PortNet Souscription Document Verification.

Endpoints:
  POST /api/souscription/upload        — Full submission (form data + all files)
  POST /api/souscription/verify-single — Quick single-file type check (real-time feedback)
  GET  /api/souscription/result/{id}   — Fetch validation report

Also serves the frontend static files.
"""

import os
import sys
import uuid
import shutil
import json
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# ─── Path setup so we can import the souscription package ─────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.database import (
    init_db,
    insert_souscription, insert_document,
    update_souscription_result, update_document_result,
    get_souscription,
)

# Pipeline imports
from souscription.models.operator import OperatorFormData, FormGerant
from souscription.pipeline.orchestrator import process_submission
from souscription.extractors.text_extractor import extract_pdf_text
from souscription.extractors.ocr_extractor import run_ocr
from souscription.pipeline.classifier import classify_text, verify_slot_document, SLOT_LABELS
from souscription.models.enums import DocumentType

# ─── Constants ────────────────────────────────────────────────────────
STORAGE_DIR = os.path.join(PROJECT_ROOT, "storage", "documents")
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
MAX_FILE_SIZE = 3 * 1024 * 1024  # 3 MB

# Mapping from form slot names to expected document types
SLOT_TO_EXPECTED_TYPE = {
    "cni":                  DocumentType.CIN,
    "categorie_operateur":  DocumentType.CATEGORIE_DOMICILIATION,
    "statuts":              DocumentType.STATUTS,
    "model_j":              DocumentType.MODEL_J,
    "procuration":          None,                   # Manual verification
    "taxe_professionnelle": DocumentType.TAXE_PROFESSIONNELLE,
    "ice":                  DocumentType.ICE_CERTIFICATE,
    "attestation_rib":      DocumentType.RIB,
    "document_if":          DocumentType.DOCUMENT_IF,
}

# Human-readable labels for document types (French)
DOCTYPE_LABELS = {
    DocumentType.MODEL_J:                  "Modèle J / Registre de commerce",
    DocumentType.DOCUMENT_IF:              "Document d'Identification Fiscale",
    DocumentType.ICE_CERTIFICATE:          "Certificat ICE",
    DocumentType.TAXE_PROFESSIONNELLE:     "Taxe Professionnelle",
    DocumentType.RIB:                      "Attestation de RIB",
    DocumentType.STATUTS:                  "Statuts de la société",
    DocumentType.CATEGORIE_DOMICILIATION:  "Attestation de domiciliation",
    DocumentType.CIN:                      "Carte Nationale d'Identité",
    DocumentType.UNKNOWN:                  "Type non reconnu",
}

# ─── App setup ────────────────────────────────────────────────────────
app = FastAPI(title="PortNet Souscription — Vérification Documentaire")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    os.makedirs(STORAGE_DIR, exist_ok=True)
    init_db()


# ─── Serve frontend ──────────────────────────────────────────────────

@app.get("/")
async def serve_root():
    colleague_index = os.path.join(PROJECT_ROOT, "souscription", "frontend", "index.html")
    if os.path.exists(colleague_index):
        return FileResponse(colleague_index)
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/index.html")
async def serve_index():
    colleague_index = os.path.join(PROJECT_ROOT, "souscription", "frontend", "index.html")
    if os.path.exists(colleague_index):
        return FileResponse(colleague_index)
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/souscription.html")
async def serve_souscription():
    return FileResponse(os.path.join(FRONTEND_DIR, "souscription.html"))


@app.get("/resultat.html")
async def serve_resultat():
    return FileResponse(os.path.join(FRONTEND_DIR, "resultat.html"))


# Serve static assets (CSS, JS, images, logos)
app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")
app.mount("/public", StaticFiles(directory=os.path.join(FRONTEND_DIR, "public")), name="public")
colleague_assets = os.path.join(PROJECT_ROOT, "souscription", "frontend", "assets")
if os.path.exists(colleague_assets):
    app.mount("/assets", StaticFiles(directory=colleague_assets), name="assets")


# ─── Helper: save file with GUID ─────────────────────────────────────

def save_uploaded_file(upload: UploadFile) -> tuple:
    """
    Save an uploaded file to storage with a GUID filename.
    Returns (guid, physical_path, file_size).
    Simulates PortNet's file server behavior.
    """
    file_guid = str(uuid.uuid4())
    # Keep the .pdf extension for the pipeline to recognise the file
    ext = os.path.splitext(upload.filename or "")[1] or ".pdf"
    physical_name = f"{file_guid}{ext}"
    physical_path = os.path.join(STORAGE_DIR, physical_name)

    # Write to disk
    with open(physical_path, "wb") as f:
        content = upload.file.read()
        f.write(content)
        file_size = len(content)

    upload.file.seek(0)  # Reset for potential re-reads
    return file_guid, physical_path, file_size


def replace_guids_in_obj(obj, guid_map: dict):
    """Recursively replace GUID filenames with human readable document names."""
    if isinstance(obj, str):
        res = obj
        for guid_key, name in guid_map.items():
            if guid_key in res:
                res = res.replace(guid_key, name)
        return res
    elif isinstance(obj, dict):
        return {k: replace_guids_in_obj(v, guid_map) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_guids_in_obj(item, guid_map) for item in obj]
    return obj


# ─── Helper: classify a single file ──────────────────────────────────

def classify_single_file(file_path: str) -> DocumentType:
    """Extract text and classify a single PDF."""
    try:
        raw_text = extract_pdf_text(file_path)
        is_scanned = len(raw_text.strip()) < 20
    except Exception:
        is_scanned = True
        raw_text = ""

    if is_scanned:
        try:
            raw_text = run_ocr(file_path)
        except Exception:
            raw_text = ""

    return classify_text(raw_text)


# ─── POST /api/souscription/verify-single ─────────────────────────────

@app.post("/api/souscription/verify-single")
async def verify_single(
    file: UploadFile = File(...),
    slot: str = Form(""),
):
    """
    Quick classification of a single uploaded file.
    Returns whether the detected type matches the expected slot.
    Used for real-time feedback under each upload field.
    """
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse({
            "status": "error",
            "message": "Seuls les fichiers PDF sont acceptés.",
            "detected_type": None,
            "detected_label": None,
            "is_correct_slot": False,
        })

    # Check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        return JSONResponse({
            "status": "error",
            "message": "Le fichier dépasse la taille maximale de 3 MO.",
            "detected_type": None,
            "detected_label": None,
            "is_correct_slot": False,
        })
    await file.seek(0)

    # Save temporarily for classification
    temp_guid = str(uuid.uuid4())
    temp_path = os.path.join(STORAGE_DIR, f"_temp_{temp_guid}.pdf")
    try:
        with open(temp_path, "wb") as f:
            f.write(content)

        # Extract text via vector extractor or OCR fallback
        try:
            raw_text = extract_pdf_text(temp_path)
            if len(raw_text.strip()) < 20:
                raw_text = run_ocr(temp_path, original_filename=file.filename)
        except Exception:
            try:
                raw_text = run_ocr(temp_path, original_filename=file.filename)
            except Exception:
                raw_text = ""

        # Manual verification slots (only procuration)
        if slot == "procuration":
            return JSONResponse({
                "status": "manual",
                "message": "Ce document sera vérifié manuellement par un agent.",
                "detected_type": "UNKNOWN",
                "detected_label": "Procuration",
                "is_correct_slot": True,
            })

        # Slot-specific template verification
        is_valid, doc_type, doc_label = verify_slot_document(slot, raw_text)

        if is_valid:
            return JSONResponse({
                "status": "success",
                "message": f"Document conforme : {doc_label}",
                "detected_type": doc_type.value if doc_type else "VALID",
                "detected_label": doc_label,
                "is_correct_slot": True,
            })
        else:
            expected_label = SLOT_LABELS.get(slot, "ce champ")
            return JSONResponse({
                "status": "error",
                "message": f"Ce document ne correspond pas au document requis pour ce champ ({expected_label}).",
                "detected_type": "UNKNOWN",
                "detected_label": doc_label,
                "is_correct_slot": False,
            })

    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ─── POST /api/souscription/upload ────────────────────────────────────

@app.post("/api/souscription/upload")
async def upload_souscription(
    raison_sociale: str = Form(...),
    ice: str = Form(...),
    rc_number: str = Form(...),
    rc_city: str = Form(...),
    if_number: str = Form(...),
    tp_number: str = Form(...),
    siege_social: str = Form(...),
    gerant_nom: str = Form(...),
    gerant_prenom: str = Form(...),
    gerant_cin: str = Form(...),
    rib: str = Form(""),
    # Files — each named by its slot
    cni: Optional[UploadFile] = File(None),
    categorie_operateur: Optional[UploadFile] = File(None),
    statuts: Optional[UploadFile] = File(None),
    model_j: Optional[UploadFile] = File(None),
    procuration: Optional[UploadFile] = File(None),
    taxe_professionnelle: Optional[UploadFile] = File(None),
    ice_doc: Optional[UploadFile] = File(None),
    attestation_rib: Optional[UploadFile] = File(None),
    document_if: Optional[UploadFile] = File(None),
):
    """
    Full souscription submission:
    1. Creates a souscription record in DB
    2. Saves each file under a GUID in storage/
    3. Runs the full verification pipeline
    4. Stores the result in DB
    5. Returns the souscription ID for the result page
    """

    # 1. Insert souscription in DB
    souscription_id = insert_souscription(
        raison_sociale=raison_sociale,
        ice=ice,
        rc_number=rc_number,
        rc_city=rc_city,
        if_number=if_number,
        tp_number=tp_number,
        siege_social=siege_social,
        gerant_nom=gerant_nom,
        gerant_prenom=gerant_prenom,
        gerant_cin=gerant_cin,
        rib=rib,
    )

    # 2. Process each uploaded file
    file_slots = {
        "cni": cni,
        "categorie_operateur": categorie_operateur,
        "statuts": statuts,
        "model_j": model_j,
        "procuration": procuration,
        "taxe_professionnelle": taxe_professionnelle,
        "ice": ice_doc,
        "attestation_rib": attestation_rib,
        "document_if": document_if,
    }

    file_paths_for_pipeline = []

    for slot_name, upload_file in file_slots.items():
        if upload_file is None or not upload_file.filename:
            continue

        # Validate PDF type
        if not upload_file.filename.lower().endswith(".pdf"):
            continue

        # Save with GUID (simulating PortNet file server)
        file_guid, physical_path, file_size = save_uploaded_file(upload_file)

        # Insert document record in DB
        insert_document(
            souscription_id=souscription_id,
            guid=file_guid,
            original_filename=upload_file.filename,
            document_slot=slot_name,
            file_path=physical_path,
            file_size_bytes=file_size,
        )

        # Send all files to the pipeline except optional manual procuration
        if slot_name not in ("procuration",):
            file_paths_for_pipeline.append(physical_path)

    # 3. Build OperatorFormData for cross-referencing
    form_data = OperatorFormData(
        raison_sociale=raison_sociale,
        ice=ice,
        rc_number=rc_number,
        rc_city=rc_city,
        if_number=if_number,
        tp_number=tp_number,
        siege_social=siege_social,
        gerants=[FormGerant(nom=gerant_nom, prenom=gerant_prenom, cin=gerant_cin)],
        rib=rib if rib else None,
    )

    # 4. Run the full verification pipeline
    try:
        report = process_submission(
            form=form_data,
            file_paths=file_paths_for_pipeline,
            submission_date=datetime.now(),
        )
    except Exception as e:
        # If pipeline crashes, mark as invalid
        update_souscription_result(
            souscription_id=souscription_id,
            overall_status="INVALID",
            validation_report={"error": str(e)},
            rejection_reasons=[f"Erreur interne du système de vérification: {str(e)}"],
        )
        return JSONResponse({
            "souscription_id": souscription_id,
            "overall_status": "INVALID",
            "message": f"Erreur lors de la vérification: {str(e)}",
        }, status_code=500)

    # Map GUID filenames to human readable display names
    guid_map = {}
    for slot_name, upload_file in file_slots.items():
        if upload_file and upload_file.filename:
            slot_label = SLOT_LABELS.get(slot_name, slot_name)
            # Find the corresponding physical path/guid
            for d in get_souscription(souscription_id).get("documents", []):
                if d.get("document_slot") == slot_name:
                    g = d.get("guid")
                    display_name = f"{upload_file.filename} [{slot_label}]"
                    guid_map[f"{g}.pdf"] = display_name
                    guid_map[g] = display_name

    # Convert report to dict
    report_dict = report.model_dump()

    # Clean report_dict and rejection_reasons
    report_dict = replace_guids_in_obj(report_dict, guid_map)
    cleaned_rejection_reasons = replace_guids_in_obj(report.rejection_reasons, guid_map)

    # 6. Store result in DB
    update_souscription_result(
        souscription_id=souscription_id,
        overall_status=report.overall_status.value,
        validation_report=report_dict,
        rejection_reasons=cleaned_rejection_reasons,
    )

    return JSONResponse({
        "souscription_id": souscription_id,
        "overall_status": report.overall_status.value,
        "redirect_url": f"/resultat.html?id={souscription_id}",
    })


# ─── GET /api/souscription/result/{id} ────────────────────────────────

@app.get("/api/souscription/result/{souscription_id}")
async def get_result(souscription_id: str):
    """
    Fetch the full validation report for a souscription.
    Used by the result page to display the outcome.
    """
    result = get_souscription(souscription_id)
    if not result:
        raise HTTPException(status_code=404, detail="Souscription introuvable")

    # Build fallback GUID map from DB documents
    guid_map = {}
    for doc in result.get("documents", []):
        guid = doc.get("guid")
        orig = doc.get("original_filename")
        slot = doc.get("document_slot")
        slot_label = SLOT_LABELS.get(slot, slot)
        if guid:
            display = f"{orig} [{slot_label}]" if orig else slot_label
            guid_map[f"{guid}.pdf"] = display
            guid_map[guid] = display

    if guid_map:
        if result.get("validation_report"):
            result["validation_report"] = replace_guids_in_obj(result["validation_report"], guid_map)
        if result.get("rejection_reasons"):
            result["rejection_reasons"] = replace_guids_in_obj(result["rejection_reasons"], guid_map)

    return JSONResponse(result)
