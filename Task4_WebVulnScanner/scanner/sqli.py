"""
sqli.py
Reflected SQL-injection check.

Submits classic SQLi payloads through form fields and URL parameters, then looks
for database error signatures in the response — a strong indicator the input is
not being sanitised. This is a detection heuristic, not exploitation.

Authorised use only.
"""

import re
from urllib.parse import urljoin
import requests

# Payloads chosen to provoke SQL errors rather than to extract data.
PAYLOADS = ["'", '"', "' OR '1'='1", "1' ORDER BY 1--", "')--"]

# Error fingerprints across common database engines.
DB_ERRORS = [
    r"you have an error in your sql syntax",
    r"warning: mysql",
    r"unclosed quotation mark after the character string",
    r"quoted string not properly terminated",
    r"pg_query\(\):",
    r"sqlite3\.OperationalError",
    r"ORA-\d{5}",
    r"sql syntax.*mariadb",
]
ERROR_RE = re.compile("|".join(DB_ERRORS), re.IGNORECASE)


def _response_has_db_error(text):
    match = ERROR_RE.search(text)
    return match.group(0) if match else None


def check_form(session, page_url, form):
    """Test each input in a form with SQLi payloads."""
    findings = []
    action = urljoin(page_url, form["action"])
    for payload in PAYLOADS:
        data = {}
        for field in form["inputs"]:
            if not field["name"]:
                continue
            data[field["name"]] = payload if field["type"] not in ("submit", "hidden") else field["value"]
        if not data:
            continue
        try:
            if form["method"] == "post":
                resp = session.post(action, data=data, timeout=8)
            else:
                resp = session.get(action, params=data, timeout=8)
        except requests.RequestException:
            continue
        sig = _response_has_db_error(resp.text)
        if sig:
            findings.append({
                "type": "SQL Injection",
                "severity": "High",
                "location": action,
                "method": form["method"].upper(),
                "payload": payload,
                "evidence": sig,
            })
            break  # one confirmed signature per form is enough
    return findings


def check_url_param(session, url):
    """Append a payload to a URL that already carries a query string."""
    findings = []
    if "?" not in url:
        return findings
    for payload in PAYLOADS:
        test = url + payload
        try:
            resp = session.get(test, timeout=8)
        except requests.RequestException:
            continue
        sig = _response_has_db_error(resp.text)
        if sig:
            findings.append({
                "type": "SQL Injection",
                "severity": "High",
                "location": test,
                "method": "GET",
                "payload": payload,
                "evidence": sig,
            })
            break
    return findings
