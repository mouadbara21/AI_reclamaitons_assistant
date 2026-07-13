"""
Cross-document validation engine implementing the Inter-Document Consistency Matrix.
"""

from typing import Dict, List, Any
import re
from souscription.models.operator import OperatorFormData
from souscription.models.document import (
    ExtractedModelJ, ExtractedDocumentIF, ExtractedICECertificate, 
    ExtractedTaxeProfessionnelle, ExtractedRIB, ExtractedDomiciliation
)
from souscription.models.validation_result import FieldValidation
from souscription.models.enums import ValidationStatus
from souscription.utils.fuzzy_match import match_names, match_addresses


def _safe_numeric_match(val1: str, val2: str) -> bool:
    """Compare two numeric-ish strings by extracting digits only.
    
    Handles cases like "370621/CASABLANCA" vs "370621" gracefully.
    Returns False if either value has no digits at all.
    """
    digits1 = re.sub(r'\D', '', val1)
    digits2 = re.sub(r'\D', '', val2)
    if not digits1 or not digits2:
        return False
    # Strip leading zeros and compare
    return digits1.lstrip('0') == digits2.lstrip('0')


def check_cross_consistency(form: OperatorFormData, docs: Dict[str, Any]) -> tuple[ValidationStatus, List[FieldValidation]]:
    """
    Cross-checks all extracted document variables against the form values.
    Returns (overall_cross_ref_status, list_of_fields_validated).
    """
    checks = []
    overall_status = ValidationStatus.VALID
    
    # helper to update overall status
    def update_status(new_status: ValidationStatus):
        nonlocal overall_status
        if new_status == ValidationStatus.INVALID:
            overall_status = ValidationStatus.INVALID
        elif new_status == ValidationStatus.WARNING and overall_status == ValidationStatus.VALID:
            overall_status = ValidationStatus.WARNING

    # 1. ICE CROSS-REFERENCE (Strict matching)
    for doc_name, doc in docs.items():
        doc_ice = getattr(doc, 'ice', None)
        if doc_ice:
            is_match = doc_ice.strip() == form.ice.strip()
            status = ValidationStatus.VALID if is_match else ValidationStatus.INVALID
            update_status(status)
            checks.append(FieldValidation(
                field_name="ICE",
                expected_value=form.ice,
                extracted_value=doc_ice,
                status=status,
                message=f"ICE match between Form and {doc_name}" if is_match else f"ICE mismatch! Form has {form.ice}, {doc_name} has {doc_ice}"
            ))

    # 2. RC NUMBER CROSS-REFERENCE (Strict numeric match, city fuzzy match)
    for doc_name, doc in docs.items():
        doc_rc = getattr(doc, 'rc_number', None)
        doc_city = getattr(doc, 'rc_city', None)
        
        # Exception for Attestation de Domiciliation: it contains DOMICILIARY's RC.
        # But we also have stamp_rc which represents the DOMICILED company's RC!
        # Let's check stamp_rc if present, otherwise ignore the main domiciliary rc for this direct company check.
        if isinstance(doc, ExtractedDomiciliation):
            if doc.stamp_rc:
                doc_rc = doc.stamp_rc
            else:
                # Domiciliation RC body text refers to the Domiciliary (host), so skip this check
                continue

        if doc_rc:
            is_match = _safe_numeric_match(doc_rc, form.rc_number)
            status = ValidationStatus.VALID if is_match else ValidationStatus.INVALID
            update_status(status)
            checks.append(FieldValidation(
                field_name="RC Number",
                expected_value=form.rc_number,
                extracted_value=doc_rc,
                status=status,
                message=f"RC match between Form and {doc_name}" if is_match else f"RC mismatch! Form has {form.rc_number}, {doc_name} has {doc_rc}"
            ))
            
        if doc_city:
            matches, score = match_names(form.rc_city, doc_city)
            status = ValidationStatus.VALID if matches else ValidationStatus.WARNING
            update_status(status)
            checks.append(FieldValidation(
                field_name="RC City",
                expected_value=form.rc_city,
                extracted_value=doc_city,
                status=status,
                score=score,
                message=f"RC City match ({score:.1f}%)" if matches else f"Fuzzy city mismatch ({score:.1f}%) between Form ({form.rc_city}) and {doc_name} ({doc_city})"
            ))

    # 3. IDENTIFIANT FISCAL (IF) CROSS-REFERENCE (Strict matching)
    for doc_name, doc in docs.items():
        doc_if = getattr(doc, 'if_number', None)
        if isinstance(doc, ExtractedDomiciliation):
            if doc.stamp_if:
                doc_if = doc.stamp_if
            else:
                continue
                
        if doc_if:
            is_match = _safe_numeric_match(doc_if, form.if_number)
            status = ValidationStatus.VALID if is_match else ValidationStatus.INVALID
            update_status(status)
            checks.append(FieldValidation(
                field_name="Identifiant Fiscal",
                expected_value=form.if_number,
                extracted_value=doc_if,
                status=status,
                message=f"IF match between Form and {doc_name}" if is_match else f"IF mismatch! Form has {form.if_number}, {doc_name} has {doc_if}"
            ))

    # 4. COMPANY NAME CROSS-REFERENCE (Fuzzy Matching >= 85%)
    for doc_name, doc in docs.items():
        # Get denomination fields
        doc_name_val = getattr(doc, 'denomination', getattr(doc, 'raison_sociale', None))
        
        # Exception for Domiciliation: Domiciled company is the one subscribing
        if isinstance(doc, ExtractedDomiciliation):
            doc_name_val = doc.domiciled_company
            
        if doc_name_val:
            matches, score = match_names(form.raison_sociale, doc_name_val)
            # Try matching sigle if available on ICE cert
            if not matches and isinstance(doc, ExtractedICECertificate) and doc.sigle:
                 matches, score = match_names(form.raison_sociale, doc.sigle)
                 
            status = ValidationStatus.VALID if matches else ValidationStatus.WARNING
            update_status(status)
            checks.append(FieldValidation(
                field_name="Company Name",
                expected_value=form.raison_sociale,
                extracted_value=doc_name_val,
                status=status,
                score=score,
                message=f"Name match ({score:.1f}%) with {doc_name}" if matches else f"Fuzzy name mismatch ({score:.1f}%) with {doc_name}"
            ))

    # 5. ADDRESS CROSS-REFERENCE (Fuzzy Matching >= 75%)
    for doc_name, doc in docs.items():
        doc_addr = getattr(doc, 'siege_social', None)
        if doc_addr:
            matches, score = match_addresses(form.siege_social, doc_addr)
            status = ValidationStatus.VALID if matches else ValidationStatus.WARNING
            update_status(status)
            checks.append(FieldValidation(
                field_name="Siège Social Address",
                expected_value=form.siege_social,
                extracted_value=doc_addr,
                status=status,
                score=score,
                message=f"Address match ({score:.1f}%) with {doc_name}" if matches else f"Fuzzy address mismatch ({score:.1f}%) with {doc_name}"
            ))

    # 6. GERANT CARD CROSS-REFERENCE
    # Compare each manager in the form to the Model J
    model_j_doc = None
    for doc in docs.values():
        if isinstance(doc, ExtractedModelJ):
            model_j_doc = doc
            break
            
    if model_j_doc and form.gerants:
        for fg in form.gerants:
            # Check if this manager's CIN is in Model J
            match_found = False
            for mg in model_j_doc.gerants:
                # Strict check on normalized CIN
                clean_fg_cin = re.sub(r'\s', '', fg.cin).upper()
                clean_mg_cin = re.sub(r'\s', '', mg.cin).upper()
                if clean_fg_cin == clean_mg_cin:
                    match_found = True
                    # Fuzzy match on manager name
                    form_fullname = f"{fg.prenom} {fg.nom}"
                    matches, score = match_names(form_fullname, mg.nom_complet)
                    status = ValidationStatus.VALID if matches else ValidationStatus.WARNING
                    update_status(status)
                    checks.append(FieldValidation(
                        field_name=f"Gerant Name ({fg.cin})",
                        expected_value=form_fullname,
                        extracted_value=mg.nom_complet,
                        status=status,
                        score=score,
                        message=f"Gerant name match ({score:.1f}%) for CIN {fg.cin}" if matches else f"Fuzzy name warning ({score:.1f}%) for CIN {fg.cin}"
                    ))
                    break
            
            if not match_found:
                update_status(ValidationStatus.INVALID)
                checks.append(FieldValidation(
                    field_name=f"Gerant CIN ({fg.cin})",
                    expected_value=fg.cin,
                    extracted_value="NOT_FOUND",
                    status=ValidationStatus.INVALID,
                    message=f"Form Gerant with CIN {fg.cin} is not listed in Modèle J!"
                ))

    # 7. RIB CROSS-REFERENCE
    rib_doc = None
    for doc in docs.values():
         if isinstance(doc, ExtractedRIB):
              rib_doc = doc
              break
    if rib_doc and form.rib:
         clean_form_rib = re.sub(r'\D', '', form.rib)
         is_match = clean_form_rib == rib_doc.rib
         status = ValidationStatus.VALID if is_match else ValidationStatus.INVALID
         update_status(status)
         checks.append(FieldValidation(
             field_name="RIB Number",
             expected_value=form.rib,
             extracted_value=rib_doc.rib,
             status=status,
             message="RIB matches document" if is_match else f"RIB mismatch! Form has {form.rib}, document has {rib_doc.rib}"
         ))

    return overall_status, checks
