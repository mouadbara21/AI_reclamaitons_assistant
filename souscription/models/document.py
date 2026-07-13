"""
Pydantic data models for structured verification outputs.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date
from souscription.models.enums import DocumentType, FormeJuridique

class Gerant(BaseModel):
    nom_complet: str
    cin: str
    qualite: str = "Gerant"  # e.g. Gerant, Associe, Admin

class ExtractedDocument(BaseModel):
    document_type: DocumentType
    raw_text: str = ""

class ExtractedModelJ(ExtractedDocument):
    document_type: DocumentType = DocumentType.MODEL_J
    denomination: str
    rc_number: str
    rc_city: str
    ice: str
    forme_juridique: str
    capital_social: Optional[float] = None
    siege_social: str
    date_immatriculation: Optional[str] = None
    activite: str
    gerants: List[Gerant] = []
    date_certification: str  # For recency checking

class ExtractedDocumentIF(ExtractedDocument):
    document_type: DocumentType = DocumentType.DOCUMENT_IF
    raison_sociale: str
    if_number: str
    rc_number: str
    rc_city: str
    ice: str
    tp_number: str
    forme_juridique: str
    siege_social: str
    date_edition: str

class ExtractedICECertificate(ExtractedDocument):
    document_type: DocumentType = DocumentType.ICE_CERTIFICATE
    denomination: str
    ice: str
    if_number: str
    rc_number: str
    rc_city: str
    sigle: Optional[str] = None
    date_edition: str

class ExtractedTaxeProfessionnelle(ExtractedDocument):
    document_type: DocumentType = DocumentType.TAXE_PROFESSIONNELLE
    raison_sociale: str
    if_number: str
    ice: str
    rc_number: str
    tp_number: str
    cni: Optional[str] = None
    siege_social: str
    date_edition: str

class ExtractedRIB(ExtractedDocument):
    document_type: DocumentType = DocumentType.RIB
    raison_sociale: str
    rib: str
    swift_code: Optional[str] = None
    date_edition: Optional[str] = None

class ExtractedDomiciliation(ExtractedDocument):
    document_type: DocumentType = DocumentType.CATEGORIE_DOMICILIATION
    domiciliary_company: str
    domiciliary_rc: str
    domiciled_company: str
    siege_social: str
    date_effective: str
    date_edition: str
    stamp_rc: Optional[str] = None
    stamp_if: Optional[str] = None
    stamp_company_name: Optional[str] = None

class ExtractedStatuts(ExtractedDocument):
    document_type: DocumentType = DocumentType.STATUTS
    capital_social: Optional[float] = None
    forme_juridique: Optional[str] = None
    gerant_name: Optional[str] = None
