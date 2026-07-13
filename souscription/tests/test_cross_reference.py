"""
Unit tests for the cross-document consistency validation engine.
"""

import pytest
from souscription.models.operator import OperatorFormData, FormGerant
from souscription.models.document import (
    ExtractedModelJ, ExtractedDocumentIF, ExtractedICECertificate,
    ExtractedTaxeProfessionnelle, ExtractedRIB, ExtractedDomiciliation, Gerant
)
from souscription.models.enums import ValidationStatus
from souscription.validators.cross_reference import check_cross_consistency


@pytest.fixture
def sample_form():
    """A consistent form data entry for testing."""
    return OperatorFormData(
        raison_sociale="GOAL EVENTS SARL AU",
        ice="002225298000015",
        rc_number="429045",
        rc_city="Casablanca",
        if_number="50110965",
        tp_number="35778129",
        siege_social="34 RUE ALI ABDERREZAK RES AL MAMOUNE RACINE, Casablanca",
        gerants=[FormGerant(nom="HAYAT", prenom="JABRANE", cin="BE50973")],
        rib="011780000009210006415609"
    )


class TestICECrossReference:
    """Tests for ICE strict matching across documents."""

    def test_matching_ice_is_valid(self, sample_form):
        docs = {
            "model_j.pdf": ExtractedModelJ(
                raw_text="", denomination="GOAL EVENTS", rc_number="429045",
                rc_city="Casablanca", ice="002225298000015",
                forme_juridique="SARL AU", siege_social="34 Rue Ali Abderrezak",
                activite="Evenementiel", gerants=[], date_certification="08/08/2022"
            )
        }
        status, checks = check_cross_consistency(sample_form, docs)
        ice_checks = [c for c in checks if c.field_name == "ICE"]
        assert len(ice_checks) >= 1
        assert all(c.status == ValidationStatus.VALID for c in ice_checks)

    def test_mismatched_ice_is_invalid(self, sample_form):
        docs = {
            "model_j.pdf": ExtractedModelJ(
                raw_text="", denomination="GOAL EVENTS", rc_number="429045",
                rc_city="Casablanca", ice="002225298000016",  # Wrong ICE!
                forme_juridique="SARL AU", siege_social="34 Rue Ali Abderrezak",
                activite="Evenementiel", gerants=[], date_certification="08/08/2022"
            )
        }
        status, checks = check_cross_consistency(sample_form, docs)
        ice_checks = [c for c in checks if c.field_name == "ICE"]
        assert any(c.status == ValidationStatus.INVALID for c in ice_checks)
        assert status == ValidationStatus.INVALID


class TestRCCrossReference:
    """Tests for RC number matching."""

    def test_matching_rc_is_valid(self, sample_form):
        docs = {
            "doc_if.pdf": ExtractedDocumentIF(
                raw_text="", raison_sociale="GOAL EVENTS", if_number="50110965",
                rc_number="429045", rc_city="Casablanca", ice="002225298000015",
                tp_number="35778129", forme_juridique="SARL", siege_social="",
                date_edition="20/12/2021"
            )
        }
        status, checks = check_cross_consistency(sample_form, docs)
        rc_checks = [c for c in checks if c.field_name == "RC Number"]
        assert any(c.status == ValidationStatus.VALID for c in rc_checks)

    def test_mismatched_rc_is_invalid(self, sample_form):
        docs = {
            "doc_if.pdf": ExtractedDocumentIF(
                raw_text="", raison_sociale="GOAL EVENTS", if_number="50110965",
                rc_number="999999", rc_city="Casablanca", ice="002225298000015",
                tp_number="35778129", forme_juridique="SARL", siege_social="",
                date_edition="20/12/2021"
            )
        }
        status, checks = check_cross_consistency(sample_form, docs)
        rc_checks = [c for c in checks if c.field_name == "RC Number"]
        assert any(c.status == ValidationStatus.INVALID for c in rc_checks)


class TestNameFuzzyMatching:
    """Tests for company name fuzzy matching."""

    def test_similar_names_pass(self, sample_form):
        docs = {
            "model_j.pdf": ExtractedModelJ(
                raw_text="", denomination="GOAL EVENTS SARL AU",
                rc_number="429045", rc_city="Casablanca", ice="002225298000015",
                forme_juridique="SARL AU", siege_social="34 Rue Ali Abderrezak",
                activite="Evenementiel", gerants=[], date_certification="08/08/2022"
            )
        }
        status, checks = check_cross_consistency(sample_form, docs)
        name_checks = [c for c in checks if c.field_name == "Company Name"]
        assert any(c.status == ValidationStatus.VALID for c in name_checks)

    def test_different_names_warn(self, sample_form):
        docs = {
            "model_j.pdf": ExtractedModelJ(
                raw_text="", denomination="TOTALLY DIFFERENT COMPANY",
                rc_number="429045", rc_city="Casablanca", ice="002225298000015",
                forme_juridique="SARL AU", siege_social="34 Rue Ali Abderrezak",
                activite="Evenementiel", gerants=[], date_certification="08/08/2022"
            )
        }
        status, checks = check_cross_consistency(sample_form, docs)
        name_checks = [c for c in checks if c.field_name == "Company Name"]
        assert any(c.status == ValidationStatus.WARNING for c in name_checks)


class TestGerantCrossReference:
    """Tests for gérant CIN matching."""

    def test_matching_gerant_cin(self, sample_form):
        docs = {
            "model_j.pdf": ExtractedModelJ(
                raw_text="", denomination="GOAL EVENTS",
                rc_number="429045", rc_city="Casablanca", ice="002225298000015",
                forme_juridique="SARL AU", siege_social="34 Rue Ali Abderrezak",
                activite="Evenementiel",
                gerants=[Gerant(nom_complet="JABRANE HAYAT", cin="BE50973", qualite="Gerant")],
                date_certification="08/08/2022"
            )
        }
        status, checks = check_cross_consistency(sample_form, docs)
        gerant_checks = [c for c in checks if "Gerant" in c.field_name]
        assert len(gerant_checks) >= 1
        # CIN matches, so the gerant name check should run (VALID or WARNING)
        assert any(c.status in [ValidationStatus.VALID, ValidationStatus.WARNING] for c in gerant_checks)

    def test_missing_gerant_cin(self, sample_form):
        docs = {
            "model_j.pdf": ExtractedModelJ(
                raw_text="", denomination="GOAL EVENTS",
                rc_number="429045", rc_city="Casablanca", ice="002225298000015",
                forme_juridique="SARL AU", siege_social="34 Rue Ali Abderrezak",
                activite="Evenementiel",
                gerants=[Gerant(nom_complet="SOMEONE ELSE", cin="XY99999", qualite="Gerant")],
                date_certification="08/08/2022"
            )
        }
        status, checks = check_cross_consistency(sample_form, docs)
        gerant_checks = [c for c in checks if "Gerant" in c.field_name]
        assert any(c.status == ValidationStatus.INVALID for c in gerant_checks)


class TestRIBCrossReference:
    """Tests for RIB matching."""

    def test_matching_rib(self, sample_form):
        docs = {
            "rib.pdf": ExtractedRIB(
                raw_text="", raison_sociale="MEDI TELECOM",
                rib="011780000009210006415609"
            )
        }
        status, checks = check_cross_consistency(sample_form, docs)
        rib_checks = [c for c in checks if c.field_name == "RIB Number"]
        assert len(rib_checks) == 1
        assert rib_checks[0].status == ValidationStatus.VALID

    def test_mismatched_rib(self, sample_form):
        docs = {
            "rib.pdf": ExtractedRIB(
                raw_text="", raison_sociale="MEDI TELECOM",
                rib="000000000000000000000000"
            )
        }
        status, checks = check_cross_consistency(sample_form, docs)
        rib_checks = [c for c in checks if c.field_name == "RIB Number"]
        assert len(rib_checks) == 1
        assert rib_checks[0].status == ValidationStatus.INVALID
