"""
Recency checks for uploaded documents (e.g. Modèle J must be < 90 days old).
"""

from datetime import datetime, timedelta
import re
from souscription.config.settings import MAX_DOCUMENT_AGE_DAYS

def parse_date(date_str: str) -> datetime:
    """
    Tries parsing date from multiple common formats used in Moroccan documents.
    """
    if not date_str:
        raise ValueError("Empty date string")
        
    cleaned_date = date_str.strip()
    
    # Common formats:
    # 08/08/2022 09:24:35
    # 25/04/2022
    # 27/01/2023
    # 20-12-2021
    # 05-03-2026
    formats = [
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(cleaned_date, fmt)
        except ValueError:
            continue
            
    # Try using dateutil as fallback if possible
    try:
        from dateutil import parser
        return parser.parse(cleaned_date, dayfirst=True)
    except Exception:
        pass
        
    raise ValueError(f"Unable to parse date string: {date_str}")

def check_recency(issue_date_str: str, submission_date: datetime = None) -> bool:
    """
    Checks if the issue date of a document is less than 90 days old at submission.
    """
    if submission_date is None:
        submission_date = datetime.now()
        
    try:
        issue_date = parse_date(issue_date_str)
    except ValueError:
        return False
        
    age = submission_date - issue_date
    return age <= timedelta(days=MAX_DOCUMENT_AGE_DAYS)
