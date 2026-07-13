"""
Settings and configuration registry for the PortNet Document Verification system.
"""

# Thresholds for fuzzy string matching
FUZZY_NAME_THRESHOLD = 85.0       # Threshold for matching company names
FUZZY_ADDRESS_THRESHOLD = 75.0    # Threshold for matching addresses

# Document recency constraint in days (e.g. Modèle J must be < 90 days old)
MAX_DOCUMENT_AGE_DAYS = 90

# Standard formats for regex validations
ICE_PATTERN = r'\b00\d{13}\b|\b\d{15}\b'
IF_PATTERN = r'\b\d{7,9}\b'   # Identifiant Fiscal is typically 8 digits, but can be 7 or 9 sometimes
RC_PATTERN = r'\b\d{3,7}\b'   # Registre de commerce number
CNI_PATTERN = r'\b[A-Z]{1,2}\d{3,6}\b'  # Moroccan CNI (e.g. BE50973, CD862418)
RIB_PATTERN = r'\b\d{24}\b'
TP_PATTERN = r'\b\d{8}\b'     # Taxe Professionnelle number (typically 8 digits)
