"""
Main orchestrator for the PortNet Document Verification pipeline.
"""

from typing import Dict, List, Any
import os
from souscription.models.enums import DocumentType, ValidationStatus
from souscription.models.operator import OperatorFormData
from souscription.models.validation_result import (
    FullValidationReport, DocumentValidationReport, FieldValidation, 
    CrossReferenceValidationReport
)

# Import extractors and parsers
from souscription.extractors.text_extractor import extract_pdf_text
from souscription.extractors.ocr_extractor import run_ocr
from souscription.pipeline.classifier import classify_text

from souscription.extractors.model_j import parse_model_j
from souscription.extractors.document_if import parse_document_if
from souscription.extractors.ice_certificate import parse_ice_certificate
from souscription.extractors.taxe_professionnelle import parse_taxe_professionnelle
from souscription.extractors.attestation_rib import parse_attestation_rib
from souscription.extractors.categorie_operateur import parse_domiciliation
from souscription.extractors.statuts import parse_statuts
from souscription.extractors.cni import parse_cni

# Import validators
from souscription.validators.checksum import validate_rib, validate_ice
from souscription.validators.recency import check_recency
from souscription.validators.cross_reference import check_cross_consistency

def process_submission(form: OperatorFormData, file_paths: List[str], submission_date: Any = None) -> FullValidationReport:
    """
    Ingests files, extracts data, performs local validation, runs cross-referencing,
    and returns a FullValidationReport.
    """
    doc_reports = []
    parsed_docs = {}
    rejection_reasons = []
    overall_status = ValidationStatus.VALID
    
    # helper to update overall validation status
    def update_overall_status(new_status: ValidationStatus):
        nonlocal overall_status
        if new_status == ValidationStatus.INVALID:
            overall_status = ValidationStatus.INVALID
        elif new_status == ValidationStatus.WARNING and overall_status == ValidationStatus.VALID:
            overall_status = ValidationStatus.WARNING

    # Phase 1: Ingestion, Extraction, Classification & Local Parsing
    for path in file_paths:
        fname = os.path.basename(path)
        if not os.path.exists(path):
            rejection_reasons.append(f"Mandatory file {fname} not found physically in folder.")
            update_overall_status(ValidationStatus.INVALID)
            continue
            
        # 1. Extraction: Check if text is extractable natively (Vector PDF)
        try:
            raw_text = extract_pdf_text(path)
            is_scanned = len(raw_text.strip()) < 20  # less than 20 chars means scanned image
        except Exception:
            is_scanned = True
            raw_text = ""
            
        # 2. Tier 2 fallback if scanned
        if is_scanned:
            try:
                raw_text = run_ocr(path)
            except NotImplementedError as e:
                # Real OCR missing/unsupported file
                doc_reports.append(DocumentValidationReport(
                    document_name=fname,
                    document_type="UNKNOWN",
                    status=ValidationStatus.INVALID,
                    message=str(e)
                ))
                update_overall_status(ValidationStatus.INVALID)
                rejection_reasons.append(f"Scanned file {fname} could not be parsed: OCR missing.")
                continue
                
        # 3. Classify Document Type
        doc_type = classify_text(raw_text)
        
        # 4. Parse fields locally
        local_checks = []
        doc_status = ValidationStatus.VALID
        
        def update_doc_status(new_s: ValidationStatus):
             nonlocal doc_status
             if new_s == ValidationStatus.INVALID:
                  doc_status = ValidationStatus.INVALID
             elif new_s == ValidationStatus.WARNING and doc_status == ValidationStatus.VALID:
                  doc_status = ValidationStatus.WARNING

        parsed_obj = None
        
        try:
            if doc_type == DocumentType.MODEL_J:
                parsed_obj = parse_model_j(raw_text)
                
                # Check recency (< 90 days)
                is_recent = check_recency(parsed_obj.date_certification, submission_date=submission_date)
                recency_status = ValidationStatus.VALID if is_recent else ValidationStatus.INVALID
                update_doc_status(recency_status)
                if not is_recent:
                     rejection_reasons.append(f"Modèle J ({fname}) is older than 90 days (Certified on {parsed_obj.date_certification}).")
                local_checks.append(FieldValidation(
                    field_name="Modèle J Recency Check",
                    expected_value="Less than 90 days old",
                    extracted_value=parsed_obj.date_certification,
                    status=recency_status,
                    message="Certified conforms with 90-day threshold" if is_recent else "Document has expired (older than 90 days)"
                ))
                
                # Check ICE Checksum
                ice_ok = validate_ice(parsed_obj.ice)
                ice_status = ValidationStatus.VALID if ice_ok else ValidationStatus.WARNING
                update_doc_status(ice_status)
                local_checks.append(FieldValidation(
                    field_name="ICE Checksum",
                    expected_value="Valid Mod97 Key",
                    extracted_value=parsed_obj.ice,
                    status=ice_status,
                    message="ICE check key matches first 13 digits" if ice_ok else "Warning: ICE has format checksum error (possible OCR mismatch)"
                ))
                
            elif doc_type == DocumentType.DOCUMENT_IF:
                parsed_obj = parse_document_if(raw_text)
                ice_ok = validate_ice(parsed_obj.ice)
                ice_status = ValidationStatus.VALID if ice_ok else ValidationStatus.WARNING
                update_doc_status(ice_status)
                local_checks.append(FieldValidation(
                    field_name="ICE Checksum",
                    expected_value="Valid Mod97 Key",
                    extracted_value=parsed_obj.ice,
                    status=ice_status,
                    message="ICE check key matches first 13 digits" if ice_ok else "Warning: ICE check key mismatch"
                ))
                
            elif doc_type == DocumentType.ICE_CERTIFICATE:
                parsed_obj = parse_ice_certificate(raw_text)
                ice_ok = validate_ice(parsed_obj.ice)
                ice_status = ValidationStatus.VALID if ice_ok else ValidationStatus.WARNING
                update_doc_status(ice_status)
                local_checks.append(FieldValidation(
                    field_name="ICE Checksum",
                    expected_value="Valid Mod97 Key",
                    extracted_value=parsed_obj.ice,
                    status=ice_status,
                    message="ICE check key matches first 13 digits" if ice_ok else "Warning: ICE check key mismatch"
                ))
                
            elif doc_type == DocumentType.TAXE_PROFESSIONNELLE:
                parsed_obj = parse_taxe_professionnelle(raw_text)
                ice_ok = validate_ice(parsed_obj.ice)
                ice_status = ValidationStatus.VALID if ice_ok else ValidationStatus.WARNING
                update_doc_status(ice_status)
                local_checks.append(FieldValidation(
                    field_name="ICE Checksum",
                    expected_value="Valid Mod97 Key",
                    extracted_value=parsed_obj.ice,
                    status=ice_status,
                    message="ICE check key matches first 13 digits" if ice_ok else "Warning: ICE check key mismatch"
                ))
                
            elif doc_type == DocumentType.RIB:
                parsed_obj = parse_attestation_rib(raw_text)
                rib_ok = validate_rib(parsed_obj.rib)
                rib_status = ValidationStatus.VALID if rib_ok else ValidationStatus.INVALID
                update_doc_status(rib_status)
                if not rib_ok:
                    rejection_reasons.append(f"RIB validation failed on {fname} (incorrect Modulo 97 check key).")
                local_checks.append(FieldValidation(
                    field_name="RIB Checksum",
                    expected_value="Divisible by 97",
                    extracted_value=parsed_obj.rib,
                    status=rib_status,
                    message="RIB is mathematically valid" if rib_ok else "RIB modulo 97 check failed (number is incorrect or forged)"
                ))
                
            elif doc_type == DocumentType.CATEGORIE_DOMICILIATION:
                parsed_obj = parse_domiciliation(raw_text)
                
                # Check domiciliation RC consistency
                # Valid if domiciliary RC is found in body/header OR stamp matches
                dom_rc = parsed_obj.domiciliary_rc or parsed_obj.stamp_rc
                dom_ok = bool(dom_rc)
                
                stamp_status = ValidationStatus.VALID if dom_ok else ValidationStatus.WARNING
                update_doc_status(stamp_status)
                local_checks.append(FieldValidation(
                    field_name="Domiciliation RC Check",
                    expected_value=dom_rc or "RC Domiciliataire",
                    extracted_value=dom_rc or "Missing",
                    status=stamp_status,
                    message=f"Domiciliary RC verified ({dom_rc})" if dom_ok else "Warning: Domiciliary RC missing in body text"
                ))
                
            elif doc_type == DocumentType.STATUTS:
                parsed_obj = parse_statuts(raw_text)
                local_checks.append(FieldValidation(
                    field_name="Boilerplate Check",
                    expected_value="SARL Structure",
                    extracted_value=parsed_obj.forme_juridique or "Unknown",
                    status=ValidationStatus.VALID,
                    message="Statuts document structure loaded"
                ))

            elif doc_type == DocumentType.CIN:
                parsed_obj = parse_cni(raw_text)
                cin_ok = bool(parsed_obj.cin_number or parsed_obj.raw_text)
                cin_status = ValidationStatus.VALID if cin_ok else ValidationStatus.WARNING
                update_doc_status(cin_status)
                local_checks.append(FieldValidation(
                    field_name="CIN Validation",
                    expected_value="CIN / CNIE Document",
                    extracted_value=parsed_obj.cin_number or "CIN détectée",
                    status=cin_status,
                    message=f"CIN extraite: {parsed_obj.cin_number}" if parsed_obj.cin_number else "Document CNI valide détecté"
                ))
                
            else:
                doc_reports.append(DocumentValidationReport(
                    document_name=fname,
                    document_type="UNKNOWN",
                    status=ValidationStatus.WARNING,
                    message="Document type could not be classified. Routed for manual index verification."
                ))
                update_overall_status(ValidationStatus.WARNING)
                continue
                
        except Exception as e:
            doc_reports.append(DocumentValidationReport(
                document_name=fname,
                document_type=doc_type.value,
                status=ValidationStatus.INVALID,
                message=f"Parsing error: {str(e)}"
            ))
            update_overall_status(ValidationStatus.INVALID)
            rejection_reasons.append(f"Could not parse document structure of {fname}: {str(e)}")
            continue
            
        # Store for cross referencing
        parsed_docs[fname] = parsed_obj
        update_overall_status(doc_status)
        doc_reports.append(DocumentValidationReport(
            document_name=fname,
            document_type=doc_type.value,
            status=doc_status,
            local_checks=local_checks
        ))

    # Phase 2: Inter-Document Consistency Matrix
    cross_status, cross_checks = check_cross_consistency(form, parsed_docs)
    update_overall_status(cross_status)
    
    # Collect critical cross ref errors as rejection reasons
    for cc in cross_checks:
         if cc.status == ValidationStatus.INVALID:
              rejection_reasons.append(cc.message)
              
    cross_report = CrossReferenceValidationReport(
         status=cross_status,
         checks=cross_checks
    )

    return FullValidationReport(
         overall_status=overall_status,
         document_reports=doc_reports,
         cross_reference_report=cross_report,
         rejection_reasons=list(set(rejection_reasons))
    )
