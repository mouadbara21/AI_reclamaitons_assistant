"""
Document classifier module to route files based on text anchor keywords.
"""

from souscription.models.enums import DocumentType

def classify_text(text: str) -> DocumentType:
    """
    Classifies the document type based on key text anchors (case-insensitive).
    Ordering is critical to avoid false positives (e.g., Modèle J contains the word 'domiciliation').
    """
    if not text:
        return DocumentType.UNKNOWN
        
    text_upper = text.upper()
    
    # 1. Check for Modèle J (Extrait du Registre de Commerce) first
    # Modèle J is highly unique and contains specific registrar keywords.
    if "INSCRIPTIONS PORTES" in text_upper or "REGISTRE ANALYTIQUE" in text_upper:
        return DocumentType.MODEL_J
        
    # 2. Document IF (Notification du Numero d'Identification Fiscale)
    if "IDENTIFICATION FISCALE" in text_upper or "AAC140B" in text_upper:
        return DocumentType.DOCUMENT_IF
        
    # 3. ICE Certificate
    if "IDENTIFIANT COMMUN DE L'ENTREPRISE" in text_upper or "CERTIFICAT DE L'IDENTIFIANT" in text_upper:
        return DocumentType.ICE_CERTIFICATE
        
    # 4. Taxe Professionnelle
    if "TAXE PROFESSIONNELLE" in text_upper or "AAC060B" in text_upper:
        return DocumentType.TAXE_PROFESSIONNELLE
        
    # 5. Attestation de domiciliation
    # Check after other structural documents because they might mention 'domiciliation' as a field value.
    if "ATTESTATION DE DOMICILIATION" in text_upper or "ATTESTATION DE DOMICILE" in text_upper:
        # If it has "registre analytique", it's a Modèle J containing a domiciliation entry.
        if "REGISTRE ANALYTIQUE" in text_upper or "INSCRIPTIONS PORTES" in text_upper:
            return DocumentType.MODEL_J
        return DocumentType.CATEGORIE_DOMICILIATION
        
    # 6. Attestation RIB
    if "ATTESTATION DE RIB" in text_upper or "ATTESTATION BANCAIRE" in text_upper:
        return DocumentType.RIB
        
    # 7. Statuts de la société
    if "STATUTS" in text_upper and ("SOCIETE A RESPONSABILITE LIMITEE" in text_upper or "DENOMINATION" in text_upper):
        return DocumentType.STATUTS
        
    # Fallback to Registre de Commerce
    if "REGISTRE DE COMMERCE" in text_upper:
        return DocumentType.MODEL_J
        
    return DocumentType.UNKNOWN
