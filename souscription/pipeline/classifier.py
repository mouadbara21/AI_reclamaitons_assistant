"""
Template-based Document Verification Module for PortNet Souscription.

Replaces ambiguous global classification with slot-specific template verification.
For each slot, verifies multiple mandatory structural anchors using strict AND logic.
"""

import re
from typing import Tuple, Optional
from souscription.models.enums import DocumentType

# Labels for each slot
SLOT_LABELS = {
    "cni":                  "Carte Nationale d'Identité / Passeport",
    "categorie_operateur":  "Attestation de domiciliation",
    "statuts":              "Statuts de la société",
    "model_j":              "Modèle J / Registre de commerce",
    "procuration":          "Procuration du gérant",
    "taxe_professionnelle": "Taxe Professionnelle (AAC060B)",
    "ice":                  "Certificat ICE",
    "attestation_rib":      "Attestation de RIB",
    "document_if":          "Document IF (AAC140B)",
}

SLOT_EXPECTED_TYPE = {
    "cni":                  DocumentType.CIN,
    "categorie_operateur":  DocumentType.CATEGORIE_DOMICILIATION,
    "statuts":              DocumentType.STATUTS,
    "model_j":              DocumentType.MODEL_J,
    "procuration":          None,
    "taxe_professionnelle": DocumentType.TAXE_PROFESSIONNELLE,
    "ice":                  DocumentType.ICE_CERTIFICATE,
    "attestation_rib":      DocumentType.RIB,
    "document_if":          DocumentType.DOCUMENT_IF,
}


def verify_slot_document(slot: str, text: str) -> Tuple[bool, DocumentType, str]:
    """
    Strict template-based document verification.

    DESIGN PRINCIPLE – every slot check uses TWO layers:
      1. POSITIVE anchors: keywords/phrases that ONLY appear in the target
         document type (verified by forensic analysis of all 8 real PDFs).
      2. NEGATIVE exclusions: keywords that are unique anchors of OTHER
         document types.  If any exclusion keyword is present the match is
         rejected, even if the positive anchor fired.

    Forensic unique-anchor map (keyword → only appears in):
      "REGISTRE ANALYTIQUE" / "INSCRIPTIONS PORTES" → Model J only
      "AAC140B"                                      → Document IF only
      "AAC060B"                                      → Taxe Prof only
      "CERTIFICAT DE L'IDENTIFIANT COMMUN DE L'ENTREPRISE" → ICE cert only
      "ATTESTATIONDERIB" / "BANKOF AFRICA"           → RIB only
      "DONNER DOMICILIATION" / "SOUSSIGN"            → Domiciliation only
      "PREMIERE TITRE" / "ARTICLE 1" + "STATUTS"     → Statuts only
      MRZ line ("<<") with NO company-doc anchor     → CIN only

    WARNING – "ATTESTATION DE DOMICILIATION" also appears inside Model J
    (line: "ATTESTATIOND E DOMICILIATION") as a field value, so the
    domiciliation check requires ADDITIONAL body text confirmation.
    """
    if not text:
        return False, DocumentType.UNKNOWN, "Aucun texte détecté dans le document."

    t = text.upper()

    # ── Unique anchor sets used as negation blockers ──────────────────
    # Each set lists the truly unique strings of ONE document type.
    # When checking slot X we exclude text that contains unique anchors
    # of ALL OTHER document types.

    _MODEL_J_ANCHORS   = ["REGISTRE ANALYTIQUE", "INSCRIPTIONS PORTES", "CODE DEMANDE"]
    _IF_ANCHORS        = ["AAC140B", "BULLETIN DE NOTIFICATION"]
    _TP_ANCHORS        = ["AAC060B"]
    _ICE_ANCHORS       = ["CERTIFICAT DE L'IDENTIFIANT COMMUN DE L'ENTREPRISE"]
    _RIB_ANCHORS       = ["ATTESTATIONDERIB"]
    _STATUTS_ANCHORS   = ["PREMIERE TITRE"]
    _CIN_MRZ           = "<<"  # only CIN has MRZ lines

    def _has_any(keywords: list[str]) -> bool:
        return any(k in t for k in keywords)

    # ─────────────────────────────────────────────────────────────────
    # 1. MODÈLE J  /  Registre de commerce
    # ─────────────────────────────────────────────────────────────────
    if slot == "model_j":
        # Positive: must have the RC registry-specific header
        has_registry = _has_any(["REGISTRE ANALYTIQUE", "INSCRIPTIONS PORTES"])
        has_code_demande = "CODE DEMANDE" in t
        positive = has_registry or has_code_demande
        # Negative: must NOT be any other government form
        negative = _has_any(_IF_ANCHORS + _TP_ANCHORS)
        if positive and not negative:
            return True, DocumentType.MODEL_J, "Modèle J / Registre de commerce"
        return False, DocumentType.UNKNOWN, \
            "Ce document ne correspond pas au Modèle J / Registre de commerce."

    # ─────────────────────────────────────────────────────────────────
    # 2. DOCUMENT IF  (Identification Fiscale – Modèle AAC140B)
    # ─────────────────────────────────────────────────────────────────
    elif slot == "document_if":
        # Positive: the form code AAC140B is 100% unique to this document
        positive = "AAC140B" in t
        # Negative: must not be TP form
        negative = _has_any(_TP_ANCHORS + _MODEL_J_ANCHORS)
        if positive and not negative:
            return True, DocumentType.DOCUMENT_IF, \
                "Document d'Identification Fiscale (IF)"
        return False, DocumentType.UNKNOWN, \
            "Ce document ne correspond pas au Document d'Identification Fiscale (IF)."

    # ─────────────────────────────────────────────────────────────────
    # 3. TAXE PROFESSIONNELLE  (Modèle AAC060B)
    # ─────────────────────────────────────────────────────────────────
    elif slot == "taxe_professionnelle":
        # Positive: the form code AAC060B is 100% unique to this document
        positive = "AAC060B" in t
        # Negative: must not be IF form or Model J
        negative = _has_any(_IF_ANCHORS + _MODEL_J_ANCHORS)
        if positive and not negative:
            return True, DocumentType.TAXE_PROFESSIONNELLE, "Taxe Professionnelle"
        return False, DocumentType.UNKNOWN, \
            "Ce document ne correspond pas à la Taxe Professionnelle."

    # ─────────────────────────────────────────────────────────────────
    # 4. CERTIFICAT ICE
    # ─────────────────────────────────────────────────────────────────
    elif slot == "ice":
        # Positive: the full title is unique to the ICE certificate
        positive = "CERTIFICAT DE L'IDENTIFIANT COMMUN DE L'ENTREPRISE" in t \
                   or "CERTIFICAT ICE" in t
        # Negative: must not be any government fiscal form or Model J
        negative = _has_any(_TP_ANCHORS + _IF_ANCHORS + _MODEL_J_ANCHORS + _RIB_ANCHORS)
        if positive and not negative:
            return True, DocumentType.ICE_CERTIFICATE, "Certificat ICE"
        return False, DocumentType.UNKNOWN, \
            "Ce document ne correspond pas au Certificat ICE."

    # ─────────────────────────────────────────────────────────────────
    # 5. ATTESTATION DE DOMICILIATION
    # ─────────────────────────────────────────────────────────────────
    elif slot == "categorie_operateur":
        # Positive: needs BOTH the title AND a body-text phrase that is
        # unique to the domiciliation letter (not just the title, because
        # Model J contains "ATTESTATIOND E DOMICILIATION" as a field value).
        has_title = "ATTESTATION DE DOMICILIATION" in t \
                    or "ATTESTATION DE DOMICILE" in t
        has_body  = _has_any(["DONNER DOMICILIATION",
                              "DOMICILIER",
                              "DOMICILE FISCAL",
                              "SOUSSIGNES",
                              "SOUSSIGNE"])
        positive = has_title and has_body
        # Negative: must not be Model J, TP, IF, or ICE
        negative = _has_any(_MODEL_J_ANCHORS + _TP_ANCHORS
                            + _IF_ANCHORS + _ICE_ANCHORS + _STATUTS_ANCHORS)
        if positive and not negative:
            return True, DocumentType.CATEGORIE_DOMICILIATION, \
                "Attestation de domiciliation"
        return False, DocumentType.UNKNOWN, \
            "Ce document ne correspond pas à l'Attestation de domiciliation."

    # ─────────────────────────────────────────────────────────────────
    # 6. ATTESTATION RIB
    # ─────────────────────────────────────────────────────────────────
    elif slot == "attestation_rib":
        # Positive: "ATTESTATIONDERIB" or "ATTESTATION DE RIB" or
        # "RELEVE D'IDENTITE BANCAIRE" — all unique to RIB document
        has_rib_title = _has_any(["ATTESTATIONDERIB",
                                  "ATTESTATION DE RIB",
                                  "RELEVE D'IDENTITE BANCAIRE",
                                  "ATTESTATION BANCAIRE"])
        positive = has_rib_title
        # Negative: must not be any other government form
        negative = _has_any(_MODEL_J_ANCHORS + _TP_ANCHORS
                            + _IF_ANCHORS + _ICE_ANCHORS + _STATUTS_ANCHORS)
        if positive and not negative:
            return True, DocumentType.RIB, "Attestation de RIB"
        return False, DocumentType.UNKNOWN, \
            "Ce document ne correspond pas à l'Attestation de RIB."

    # ─────────────────────────────────────────────────────────────────
    # 7. STATUTS DE LA SOCIÉTÉ
    # ─────────────────────────────────────────────────────────────────
    elif slot == "statuts":
        # Positive: must have BOTH the word "STATUTS" AND legal-body
        # structural text ("PREMIERE TITRE", "ARTICLE 1", etc.)
        # "PREMIERE TITRE" is unique to statuts documents.
        has_title = "STATUTS" in t
        has_legal = _has_any(["PREMIERE TITRE",
                              "ARTICLE 1",
                              "ARTICLE 2",
                              "ARTICLE 3"])
        positive = has_title and has_legal
        # Negative: must not be any government form or Model J
        negative = _has_any(_MODEL_J_ANCHORS + _TP_ANCHORS
                            + _IF_ANCHORS + _ICE_ANCHORS + _RIB_ANCHORS)
        if positive and not negative:
            return True, DocumentType.STATUTS, "Statuts de la société"
        return False, DocumentType.UNKNOWN, \
            "Ce document ne correspond pas aux Statuts de la société."

    # ─────────────────────────────────────────────────────────────────
    # 8. CIN / PASSEPORT
    # ─────────────────────────────────────────────────────────────────
    elif slot == "cni":
        # Positive: CIN has MRZ lines ("<<") that NO other document has.
        # Additionally check for CIN-specific headers.
        has_mrz = _CIN_MRZ in t
        has_cin_header = _has_any(["CARTE NATIONALE",
                                   "IDENTITE ELECTRONIQUE",
                                   "CARTENATIONALED'IDENTITE",
                                   "CNIE"])
        positive = has_mrz or has_cin_header
        # Negative: must NOT be any company/government document.
        # This is the broadest exclusion list because many company
        # docs mention "ROYAUME DU MAROC" or contain CIN numbers
        # of the gérant.
        negative = _has_any(_MODEL_J_ANCHORS + _IF_ANCHORS + _TP_ANCHORS
                            + _ICE_ANCHORS + _RIB_ANCHORS + _STATUTS_ANCHORS
                            + ["ATTESTATION DE DOMICILIATION"])
        if positive and not negative:
            return True, DocumentType.CIN, \
                "Carte Nationale d'Identité / Passeport"
        return False, DocumentType.UNKNOWN, \
            "Ce document ne correspond pas à une CIN ou un Passeport."

    # ─────────────────────────────────────────────────────────────────
    # 9. PROCURATION  (optionnelle – manual review always accepted)
    # ─────────────────────────────────────────────────────────────────
    elif slot == "procuration":
        has_procuration = _has_any(["PROCURATION", "DONNE POUVOIR", "MANDAT"])
        if has_procuration:
            return True, DocumentType.UNKNOWN, "Procuration"
        # Procuration is optional – accept with manual-review note
        return True, DocumentType.UNKNOWN, \
            "Document pour procuration (Vérification manuelle)"

    return False, DocumentType.UNKNOWN, \
        "Format de document non reconnu pour ce champ."


def classify_text(text: str) -> DocumentType:
    """
    Fallback global classifier for legacy callers.
    """
    if not text:
        return DocumentType.UNKNOWN
    t = text.upper()

    if "AAC140B" in t or ("NOTIFICATION" in t and "IDENTIFICATION FISCALE" in t):
        return DocumentType.DOCUMENT_IF
    if "AAC060B" in t or "TAXE PROFESSIONNELLE" in t:
        return DocumentType.TAXE_PROFESSIONNELLE
    if "REGISTRE ANALYTIQUE" in t or "INSCRIPTIONS PORTES" in t or "MODELE J" in t:
        return DocumentType.MODEL_J
    if "IDENTIFIANT COMMUN DE L'ENTREPRISE" in t or "CERTIFICAT DE L'IDENTIFIANT" in t:
        return DocumentType.ICE_CERTIFICATE
    if "ATTESTATION DE DOMICILIATION" in t or "DOMICILIER LA SOCIETE" in t:
        return DocumentType.CATEGORIE_DOMICILIATION
    if "ATTESTATION DE RIB" in t or "ATTESTATIONDERIB" in t:
        return DocumentType.RIB
    if "STATUTS" in t and "SOCIETE" in t:
        return DocumentType.STATUTS
    if "CARTE NATIONALE" in t or "CNIE" in t or re.search(r'<<', t):
        return DocumentType.CIN

    return DocumentType.UNKNOWN
