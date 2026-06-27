"""
xss.py
Reflected cross-site scripting (XSS) check.

Injects a uniquely-marked script payload into inputs and checks whether it is
reflected back into the response unescaped. If the raw payload appears in the
HTML, the input is likely vulnerable to reflected XSS.

Authorised use only.
"""

from urllib.parse import urljoin
import requests

# Unique marker makes accidental matches very unlikely.
MARKER = "xSsT3st9182"
PAYLOADS = [
    f"<script>{MARKER}</script>",
    f"\"><svg onload={MARKER}>",
    f"'><img src=x onerror={MARKER}>",
]


def _reflected(payload, text):
    return payload in text


def check_form(session, page_url, form):
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
        if _reflected(payload, resp.text):
            findings.append({
                "type": "Reflected XSS",
                "severity": "High",
                "location": action,
                "method": form["method"].upper(),
                "payload": payload,
                "evidence": "Payload reflected unescaped in response body",
            })
            break
    return findings


def check_url_param(session, url):
    findings = []
    if "?" not in url:
        return findings
    for payload in PAYLOADS:
        test = url + payload
        try:
            resp = session.get(test, timeout=8)
        except requests.RequestException:
            continue
        if _reflected(payload, resp.text):
            findings.append({
                "type": "Reflected XSS",
                "severity": "High",
                "location": test,
                "method": "GET",
                "payload": payload,
                "evidence": "Payload reflected unescaped in response body",
            })
            break
    return findings
