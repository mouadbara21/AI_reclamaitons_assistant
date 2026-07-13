"""
End-to-end integration tests for the PortNet Document Verification pipeline.
"""

import pytest
import os
from souscription.models.operator import OperatorFormData, FormGerant
from souscription.models.enums import ValidationStatus
from souscription.pipeline.orchestrator import process_submission

SOUSCRIPTION_DIR = r"c:\for me\Portnet internship\AI_reclamations_assistant\souscription"

def test_full_pipeline_success():
    # Setup mock form data matching the expected details for MEDI TELECOM / Bank of Africa
    # since we want to cross-reference multiple documents.
    # Note: in our test workspace, each sample document belongs to a different company:
    #   - Modèle J is for GOAL EVENTS / JABRANE HAYAT (BE50973) / ICE 002225298000015
    #   - Doc IF is for 3S EMBALLAGE / ICE 001884310000033 / RC 370621
    #   - ICE Cert is for PREFABRIQUES DU MAROC / ICE 001535820000069
    #   - Taxe Prof is for TAHA ELARACHIN / CNI CD862418 / ICE 002104146003851
    #   - RIB is for MEDI TELECOM / RIB 011780000009210006415609
    
    # Let's test checking individual documents separately by passing the appropriate form context
    # for each document, validating that they are parsed and pass local format/checksum checks.
    
    # Test 1: Validate Modèle J context
    from datetime import datetime
    form_model_j = OperatorFormData(
         raison_sociale="GOAL EVENTS",
         ice="002225298000015",
         rc_number="429045",
         rc_city="Casablanca",
         if_number="20751297",  # dummy, not on Modèle J
         tp_number="35778129",  # dummy
         siege_social="34 RUE ALI ABDERREZAK RES AL MAMOUNE RACINE , Casablanca",
         gerants=[FormGerant(nom="HAYAT", prenom="JABRANE", cin="BE50973")]
    )
    
    pdf_model_j = os.path.join(SOUSCRIPTION_DIR, "Model-J.pdf")
    
    # The document was certified on 08/08/2022. Sept 1st 2022 is less than 90 days after.
    submission_date = datetime(2022, 9, 1)
    report = process_submission(form_model_j, [pdf_model_j], submission_date=submission_date)
    
    # Assertions
    assert report.overall_status in [ValidationStatus.VALID, ValidationStatus.WARNING]
    assert len(report.document_reports) == 1
    doc_rep = report.document_reports[0]
    assert doc_rep.document_type == "MODEL_J"
    assert doc_rep.status in [ValidationStatus.VALID, ValidationStatus.WARNING]
    
    # Test 2: Validate RIB context
    form_rib = OperatorFormData(
         raison_sociale="MEDI TELECOM",
         ice="001512572000078", # dummy
         rc_number="12345",     # dummy
         rc_city="Casablanca",
         if_number="123456",    # dummy
         tp_number="123456",    # dummy
         siege_social="Immeubles Les Quatre Temps La Colline Sidi Maarouf 20270 Casablanca",
         rib="011780000009210006415609"
    )
    
    pdf_rib = os.path.join(SOUSCRIPTION_DIR, "AttestationRIB-Bank of affrica.pdf")
    
    report_rib = process_submission(form_rib, [pdf_rib])
    
    assert report_rib.overall_status in [ValidationStatus.VALID, ValidationStatus.WARNING]
    assert len(report_rib.document_reports) == 1
    doc_rep_rib = report_rib.document_reports[0]
    assert doc_rep_rib.document_type == "RIB"
    assert doc_rep_rib.status in [ValidationStatus.VALID, ValidationStatus.WARNING]
