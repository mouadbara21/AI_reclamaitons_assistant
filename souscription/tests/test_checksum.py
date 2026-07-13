"""
Unit tests for the mathematical checksum algorithms (RIB and ICE validation).
"""

import pytest
from souscription.validators.checksum import validate_rib, validate_ice

def test_moroccan_rib_validation():
    # 1. Bank of Africa attestation (MEDI TELECOM)
    boa_rib = "011780000009210006415609"
    assert validate_rib(boa_rib) is True
    
    # 2. Banque Populaire (ASSOCIATION TIBU MAROC)
    bcp_rib = "190780212114011324000027"
    assert validate_rib(bcp_rib) is True
    
    # 3. Société Générale (TOTALENERGIES MARKETING MAROC)
    sg_rib = "022780000140000501240574"
    assert validate_rib(sg_rib) is True
    
    # 4. Failed/Invalid Tiznit RIB (AMGHAR LOUBNA)
    # The printed text in image was read as 022010000112002937581274 which failed
    tiznit_failed = "022010000112002937581274"
    assert validate_rib(tiznit_failed) is False
    
    # 5. Corrected Tiznit RIB (with 9 -> 6 correction)
    tiznit_corrected = "022010000112002637581274"
    assert validate_rib(tiznit_corrected) is True

def test_ice_validation():
    # 1. Modèle J ICE (GOAL EVENTS)
    assert validate_ice("002225298000015") is True
    
    # 2. Document IF ICE (3S EMBALLAGE)
    assert validate_ice("001884310000033") is True
    
    # 3. ICE Cert (PREFA MAROC)
    assert validate_ice("001535820000069") is True
    
    # 4. Invalid ICE (failed checksum)
    # E.g. typo on Goal Events: change 15 to 16
    assert validate_ice("002225298000016") is False
    
    # 5. Standard OMPIC example from icemaroc.com FAQ
    assert validate_ice("123456789000014") is True
