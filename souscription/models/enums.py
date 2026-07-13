"""
Shared enums representing document categories, legal forms, and validation statuses.
"""

from enum import Enum

class DocumentType(str, Enum):
    MODEL_J = "MODEL_J"
    DOCUMENT_IF = "DOCUMENT_IF"
    ICE_CERTIFICATE = "ICE_CERTIFICATE"
    TAXE_PROFESSIONNELLE = "TAXE_PROFESSIONNELLE"
    RIB = "RIB"
    STATUTS = "STATUTS"
    CATEGORIE_DOMICILIATION = "CATEGORIE_DOMICILIATION"
    CIN = "CIN"
    UNKNOWN = "UNKNOWN"

class ValidationStatus(str, Enum):
    VALID = "VALID"
    WARNING = "WARNING"
    INVALID = "INVALID"

class FormeJuridique(str, Enum):
    SARL = "SARL"
    SARL_AU = "SARL_AU"
    SA = "SA"
    SNC = "SNC"
    OTHER = "OTHER"
