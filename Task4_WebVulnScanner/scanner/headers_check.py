"""
headers_check.py
Passive security-header audit.

Checks the target's HTTP response for the presence of common security headers.
Missing headers aren't exploitable on their own but are widely flagged in real
assessments (and by tools like OWASP ZAP) as hardening gaps.

Authorised use only.
"""

import requests

EXPECTED_HEADERS = {
    "Content-Security-Policy": "Mitigates XSS and data-injection attacks",
    "X-Frame-Options": "Protects against clickjacking",
    "X-Content-Type-Options": "Prevents MIME-type sniffing",
    "Strict-Transport-Security": "Enforces HTTPS connections",
    "Referrer-Policy": "Controls referrer information leakage",
}


def check(session, url):
    findings = []
    try:
        resp = session.get(url, timeout=8)
    except requests.RequestException:
        return findings
    present = {k.lower() for k in resp.headers}
    for header, purpose in EXPECTED_HEADERS.items():
        if header.lower() not in present:
            findings.append({
                "type": "Missing Security Header",
                "severity": "Low",
                "location": url,
                "method": "GET",
                "payload": header,
                "evidence": f"{header} not set — {purpose}",
            })
    return findings
