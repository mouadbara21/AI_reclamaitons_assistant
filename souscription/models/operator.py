"""
Pydantic model representing form data submitted by the operator.
"""

from pydantic import BaseModel, Field
from typing import Optional, List

class FormGerant(BaseModel):
    nom: str
    prenom: str
    cin: str

class OperatorFormData(BaseModel):
    raison_sociale: str
    ice: str
    rc_number: str
    rc_city: str
    if_number: str
    tp_number: str
    siege_social: str
    gerants: List[FormGerant] = []
    rib: Optional[str] = None
