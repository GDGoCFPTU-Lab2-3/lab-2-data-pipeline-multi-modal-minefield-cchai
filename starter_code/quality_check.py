import re

# ==========================================
# ROLE 3: OBSERVABILITY & QA ENGINEER
# ==========================================
# Task: Implement quality gates to reject corrupt data or logic discrepancies.

# --- Configuration ---
MIN_CONTENT_LENGTH = 20

TOXIC_STRINGS = [
    'null pointer exception',
    'traceback (most recent call last)',
    'segmentation fault',
    'fatal error',
    'undefined reference',
    'stack overflow',
    'out of memory',
]

def _check_length(content: str) -> tuple[bool, str]:
    """Gate 1: Reject documents with content shorter than minimum threshold."""
    if len(content.strip()) < MIN_CONTENT_LENGTH:
        return False, f"Content too short ({len(content.strip())} chars, min={MIN_CONTENT_LENGTH})"
    return True, ""

def _check_toxic_strings(content: str) -> tuple[bool, str]:
    """Gate 2: Reject documents containing known error/toxic strings."""
    content_lower = content.lower()
    for toxic in TOXIC_STRINGS:
        if toxic in content_lower:
            return False, f"Toxic string detected: '{toxic}'"
    return True, ""

def _check_logic_discrepancy(document_dict: dict) -> tuple[bool, str]:
    """
    Gate 3: Flag discrepancies between comments and actual values.
    Example: if a comment says 'tax = 8%' but code sets tax_rate = 0.10 (10%).
    """
    content = document_dict.get("content", "")
    
    # Detect tax rate discrepancy: comment says one rate but number differs
    comment_match = re.search(r'tax\s*[=:]\s*(\d+)%', content, re.IGNORECASE)
    code_match = re.search(r'tax_rate\s*=\s*0\.(\d+)', content, re.IGNORECASE)
    
    if comment_match and code_match:
        comment_rate = int(comment_match.group(1))
        code_rate = int(code_match.group(1))
        if comment_rate != code_rate:
            return False, f"Logic discrepancy: comment says {comment_rate}% but code sets {code_rate}%"
    
    return True, ""

def run_quality_gate(document_dict: dict) -> bool:
    """
    Run all quality gates on a document dictionary.
    Returns True if the document passes all checks, False if it should be rejected.
    """
    if not document_dict:
        return False

    content = document_dict.get("content", "")
    doc_id = document_dict.get("document_id", "unknown")
    
    gates = [
        _check_length(content),
        _check_toxic_strings(content),
        _check_logic_discrepancy(document_dict),
    ]
    
    for passed, reason in gates:
        if not passed:
            print(f"  [QA REJECTED] doc_id='{doc_id}' | Reason: {reason}")
            return False
    
    return True
