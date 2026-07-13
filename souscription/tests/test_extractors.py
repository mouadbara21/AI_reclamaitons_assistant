"""
Unit tests for the document-specific field extractors.

Tests each extractor against the actual sample PDFs in the workspace
to verify regex patterns extract correct values.
"""

import pytest
import os
from souscription.extractors.text_extractor import extract_pdf_text
from souscription.extractors.ocr_extractor import run_ocr
from souscription.extractors.model_j import parse_model_j
from souscription.extractors.document_if import parse_document_if
from souscription.extractors.ice_certificate import parse_ice_certificate
from souscription.extractors.taxe_professionnelle import parse_taxe_professionnelle
from souscription.extractors.attestation_rib import parse_attestation_rib
from souscription.extractors.categorie_operateur import parse_domiciliation
from souscription.extractors.statuts import parse_statuts

SOUSCRIPTION_DIR = r"c:\for me\Portnet internship\AI_reclamations_assistant\souscription"


class TestModelJExtractor:
    """Tests for Modèle J (Registre de Commerce) extractor."""

    @pytest.fixture
    def model_j_data(self):
        path = os.path.join(SOUSCRIPTION_DIR, "Model-J.pdf")
        if not os.path.exists(path):
            pytest.skip("Model-J.pdf not found in workspace")
        text = extract_pdf_text(path)
        return parse_model_j(text)

    def test_extracts_denomination(self, model_j_data):
        assert model_j_data.denomination != "", "Denomination should not be empty"
        assert len(model_j_data.denomination) >= 3, "Denomination too short"

    def test_extracts_rc_number(self, model_j_data):
        assert model_j_data.rc_number.isdigit(), "RC number should be numeric"
        assert model_j_data.rc_number == "429045"

    def test_extracts_ice(self, model_j_data):
        assert len(model_j_data.ice) == 15, "ICE should be 15 digits"
        assert model_j_data.ice.isdigit(), "ICE should be all digits"
        assert model_j_data.ice == "002225298000015"

    def test_extracts_certification_date(self, model_j_data):
        assert model_j_data.date_certification != "", "Certification date should not be empty"
        assert "/" in model_j_data.date_certification, "Date should contain /"

    def test_extracts_gerants(self, model_j_data):
        # Modèle J should list at least one gérant
        if model_j_data.gerants:
            gerant = model_j_data.gerants[0]
            assert gerant.cin != "", "Gérant CIN should not be empty"
            assert gerant.nom_complet != "", "Gérant name should not be empty"


class TestDocumentIFExtractor:
    """Tests for Document IF (Identifiant Fiscal) extractor."""

    @pytest.fixture
    def doc_if_data(self):
        path = os.path.join(SOUSCRIPTION_DIR, "document IF.pdf")
        if not os.path.exists(path):
            pytest.skip("document IF.pdf not found in workspace")
        text = extract_pdf_text(path)
        return parse_document_if(text)

    def test_extracts_ice(self, doc_if_data):
        assert len(doc_if_data.ice) == 15, "ICE should be 15 digits"
        assert doc_if_data.ice == "001884310000033"

    def test_extracts_rc_with_city(self, doc_if_data):
        assert doc_if_data.rc_number != "", "RC number should not be empty"
        assert doc_if_data.rc_city != "", "RC city should not be empty"

    def test_extracts_date(self, doc_if_data):
        assert doc_if_data.date_edition != "", "Edition date should not be empty"


class TestICECertificateExtractor:
    """Tests for ICE Certificate extractor."""

    @pytest.fixture
    def ice_data(self):
        path = os.path.join(SOUSCRIPTION_DIR, "ICE.pdf")
        if not os.path.exists(path):
            pytest.skip("ICE.pdf not found in workspace")
        text = extract_pdf_text(path)
        return parse_ice_certificate(text)

    def test_extracts_ice(self, ice_data):
        assert len(ice_data.ice) == 15, "ICE should be 15 digits"
        assert ice_data.ice == "001535820000069"

    def test_extracts_denomination(self, ice_data):
        assert ice_data.denomination != "", "Denomination should not be empty"

    def test_extracts_rc(self, ice_data):
        assert ice_data.rc_number != "", "RC number should not be empty"


class TestTaxeProfessionnelleExtractor:
    """Tests for Taxe Professionnelle extractor."""

    @pytest.fixture
    def tp_data(self):
        path = os.path.join(SOUSCRIPTION_DIR, "taxe_professionelle.pdf")
        if not os.path.exists(path):
            pytest.skip("taxe_professionelle.pdf not found in workspace")
        text = extract_pdf_text(path)
        return parse_taxe_professionnelle(text)

    def test_extracts_ice(self, tp_data):
        assert len(tp_data.ice) == 15, "ICE should be 15 digits"

    def test_extracts_if(self, tp_data):
        assert tp_data.if_number != "", "IF number should not be empty"
        assert tp_data.if_number.isdigit(), "IF should be numeric"

    def test_extracts_date(self, tp_data):
        assert tp_data.date_edition != "", "Edition date should not be empty"


class TestAttestationRIBExtractor:
    """Tests for RIB attestation extractor (uses mock OCR)."""

    @pytest.fixture
    def rib_data(self):
        path = os.path.join(SOUSCRIPTION_DIR, "AttestationRIB-Bank of affrica.pdf")
        if not os.path.exists(path):
            pytest.skip("RIB PDF not found in workspace")
        text = run_ocr(path)
        return parse_attestation_rib(text)

    def test_extracts_rib(self, rib_data):
        assert len(rib_data.rib) == 24, f"RIB should be 24 digits, got {len(rib_data.rib)}"
        assert rib_data.rib == "011780000009210006415609"

    def test_extracts_owner(self, rib_data):
        assert rib_data.raison_sociale != "", "Owner name should not be empty"
        assert "MEDI TELECOM" in rib_data.raison_sociale.upper()

    def test_extracts_swift(self, rib_data):
        assert rib_data.swift_code == "BMCEMAMC"

    def test_extracts_date(self, rib_data):
        assert rib_data.date_edition == "25/04/2022"


class TestDomiciliationExtractor:
    """Tests for Attestation de Domiciliation extractor (uses mock OCR)."""

    @pytest.fixture
    def dom_data(self):
        # The filename may use Unicode right single quote (U+2019) or ASCII apostrophe
        import glob
        pattern = os.path.join(SOUSCRIPTION_DIR, "Copie d*un document justifiant*")
        matches = glob.glob(pattern)
        if not matches:
            pytest.skip("Domiciliation PDF not found in workspace")
        path = matches[0]
        text = run_ocr(path)
        return parse_domiciliation(text)

    def test_extracts_domiciliary_rc(self, dom_data):
        assert dom_data.domiciliary_rc == "289895"

    def test_extracts_stamp_rc(self, dom_data):
        assert dom_data.stamp_rc == "289895"

    def test_extracts_stamp_if(self, dom_data):
        assert dom_data.stamp_if == "14458189"

    def test_extracts_effective_date(self, dom_data):
        assert dom_data.date_effective == "05/01/2026"

    def test_extracts_edition_date(self, dom_data):
        assert dom_data.date_edition == "27/02/2026"
