"""
Parser for Category Justification (Attestation de Domiciliation) documents.

Layout reference:
  - Title: "Attestation de domiciliation"
  - Body: "Nous soussignés la société [DOMICILIARY], ... inscrite au registre de commerce
           de [CITY] sous le numéro [RC]."
  - "Déclare ... domicilier la société [DOMICILED]"
  - "représentée par ... titulaire CIN N° [CIN]"
  - "à compter du [DATE]"
  - Footer: "Fait à [CITY], le [DATE]"
  - Stamp area: "RC: XXXXXX / IF: XXXXXXXX"
"""

import re
from souscription.models.document import ExtractedDomiciliation
from souscription.utils.text_cleaner import clean_whitespace


def parse_domiciliation(text: str) -> ExtractedDomiciliation:
    """
    Parses the text of an Attestation de Domiciliation and returns
    a structured Pydantic object.
    
    All values extracted via generic regex — no hardcoded defaults.
    """
    # 1. Domiciliary company (hosting entity)
    #    "Nous soussignés GOAL VOYAGES, sise à..." or "Nous soussignés la société [NAME], ..."
    domiciliary = ""
    dom_match = re.search(
        r'soussign[ée]s\s+(?:la\s+)?(?:soci[ée]t[ée]\s+)?([A-Z0-9\s\-]+?)\s*,\s*(?:sise|Soci[ée]t[ée]|SARL|S\.A\.R\.L)',
        text, re.IGNORECASE
    )
    if dom_match:
        domiciliary = clean_whitespace(dom_match.group(1))

    # 2. Domiciliary RC
    #    "registre de commerce ... sous le numéro [RC]" or "RC : 162657"
    domiciliary_rc = ""
    rc_match = re.search(
        r'registre\s+de\s+commerce\s+(?:de\s+\w+\s+)?sous\s+le\s+num[ée]ro\s+(\d{4,8})',
        text, re.IGNORECASE
    )
    if not rc_match:
        rc_match = re.search(r'\bR\.?C\.?\s*:?\s*(\d{4,8})\b', text, re.IGNORECASE)
    if rc_match:
        domiciliary_rc = rc_match.group(1)

    # 3. Domiciled company (hosted entity / client operator subscribing)
    #    "domicilier la société [NAME],"
    domiciled = ""
    domiciled_match = re.search(
        r'domicilier\s+(?:la\s+)?soci[ée]t[ée]\s+(.+?)\s*,',
        text, re.IGNORECASE
    )
    if domiciled_match:
        domiciled = clean_whitespace(domiciled_match.group(1))

    # 4. Siège social (address)
    #    "Au [ADDRESS], Casablanca" or "sise au [ADDRESS]"
    siege = ""
    siege_match = re.search(
        r'(?:Au|sise\s+au)\s+(\d+\s*,?\s*(?:Boulevard|Bd|Rue|Avenue|Av)\s+[^\n]{5,80})',
        text, re.IGNORECASE
    )
    if siege_match:
        siege = clean_whitespace(siege_match.group(1))
    else:
        # Fallback: any line with street keywords
        for line in text.split('\n'):
            if re.search(r'(Boulevard|Bd|Rue|Avenue)', line, re.IGNORECASE) and len(line.strip()) > 10:
                siege = clean_whitespace(line.strip())
                break

    # 5. Effective Date ("à compter du DD/MM/YYYY")
    date_eff = ""
    date_eff_match = re.search(r'compter\s+du\s+(\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
    if date_eff_match:
        date_eff = date_eff_match.group(1)

    # 6. Edition Date ("Fait à [CITY], le DD/MM/YYYY")
    date_ed = ""
    date_ed_match = re.search(r'Fait\s+[àa]\s+\w+\s*,?\s*le\s+(\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
    if date_ed_match:
        date_ed = date_ed_match.group(1)
    else:
        # Fallback: last date in text
        all_dates = re.findall(r'(\d{2}/\d{2}/\d{4})', text)
        if all_dates:
            date_ed = all_dates[-1]

    # 7. Stamp information ("RC: XXXXXX / IF: XXXXXXXX" or "R.C.: 429045 - TP:... - I.F.: 32770927")
    stamp_rc = None
    stamp_if = None
    stamp_company_name = None

    stamp_match = re.search(r'R\.?C\.?\s*:?\s*(\d+)\s*[/|\-].*?I\.?F\.?\s*:?\s*(\d+)', text, re.IGNORECASE)
    if not stamp_match:
        stamp_match = re.search(r'R\.?C\.?\s*:?\s*(\d+)', text, re.IGNORECASE)
        if stamp_match:
            stamp_rc = stamp_match.group(1)
        if_m = re.search(r'I\.?F\.?\s*:?\s*(\d+)', text, re.IGNORECASE)
        if if_m:
            stamp_if = if_m.group(1)
    else:
        stamp_rc = stamp_match.group(1)
        stamp_if = stamp_match.group(2)

    # Stamp company name: line immediately before stamp or header company name
    if stamp_match:
        stamp_pos = stamp_match.start()
        text_before_stamp = text[:stamp_pos].rstrip()
        prev_lines = [l.strip() for l in text_before_stamp.split('\n') if l.strip()]
        if prev_lines:
            stamp_company_name = clean_whitespace(prev_lines[-1])

    return ExtractedDomiciliation(
        raw_text=text,
        domiciliary_company=domiciliary,
        domiciliary_rc=domiciliary_rc,
        domiciled_company=domiciled,
        siege_social=siege,
        date_effective=date_eff,
        date_edition=date_ed,
        stamp_rc=stamp_rc,
        stamp_if=stamp_if,
        stamp_company_name=stamp_company_name
    )
