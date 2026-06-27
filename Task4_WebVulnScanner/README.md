# Web Application Vulnerability Scanner

A Python-based scanner that crawls a web application and checks for common vulnerabilities — SQL injection, reflected cross-site scripting (XSS), and missing security headers. Built with `requests` and `BeautifulSoup` as an internship deliverable.

> **Authorised use only.** Scan only web applications you **own** or have **explicit written permission** to test. Unauthorised scanning may be illegal under the UK Computer Misuse Act 1990 and equivalent legislation elsewhere. Use the intentionally vulnerable practice apps listed in [Building a Safe Test Lab](#building-a-safe-test-lab).

---

## Features

- **Crawler** — discovers internal pages, links, and HTML forms to locate input points.
- **SQL injection check** — submits classic SQLi payloads and detects database error signatures across MySQL, PostgreSQL, SQLite, Oracle, and MSSQL.
- **Reflected XSS check** — injects uniquely-marked script payloads and detects unescaped reflection in the response.
- **Security-header audit** — flags missing hardening headers (CSP, X-Frame-Options, HSTS, etc.).
- **Reporting** — prints a severity-grouped summary and saves JSON + CSV artefacts to `reports/`.

## How it works

```
scan.py
  └─► Crawler        → collects pages + forms
        ├─► headers_check → passive header audit
        ├─► sqli          → error-based SQLi detection on forms & URL params
        └─► xss           → reflection-based XSS detection on forms & URL params
              └─► Reporter → summary + JSON/CSV
```

The vulnerability checks are **detection heuristics, not exploitation**. The SQLi module looks for error signatures that indicate unsanitised input; the XSS module checks whether a marked payload is reflected unescaped. Neither extracts data or runs attacks.

## Installation

Requires Python 3.8+.

```bash
pip install -r requirements.txt
```

This installs `requests` and `beautifulsoup4`.

## Usage

```bash
# Full scan (sqli + xss + headers), default 30 pages
python scan.py http://192.168.56.101/dvwa/

# Limit crawl depth
python scan.py http://192.168.56.101/ --max-pages 15

# Run only specific checks
python scan.py http://192.168.56.101/ --checks sqli,xss

# Skip saving reports
python scan.py http://192.168.56.101/ --no-report
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `url` | Target base URL (must start with http/https) | required |
| `--max-pages` | Maximum pages to crawl | 30 |
| `--checks` | Comma list: `sqli,xss,headers` | all three |
| `--no-report` | Don't write JSON/CSV reports | off |

## Example Output

```
[*] Starting scan of http://192.168.56.101/dvwa/
[*] Checks enabled: sqli, xss, headers

[*] Crawling http://192.168.56.101/dvwa/ (max 30 pages)
[*] Crawl complete: 12 pages, 4 forms found.

[*] Checking security headers...
[*] Testing for SQL injection...
[*] Testing for reflected XSS...

============================================================
  SCAN SUMMARY — http://192.168.56.101/dvwa/
============================================================
  [High] 2 finding(s):
    - SQL Injection @ .../vulnerabilities/sqli/ (GET)
    - Reflected XSS @ .../vulnerabilities/xss_r/ (GET)
  [Low] 5 finding(s):
    - Missing Security Header @ ... (GET)
============================================================
```

## Building a Safe Test Lab

Run the scanner against intentionally vulnerable applications in an isolated environment:

- **DVWA** (Damn Vulnerable Web Application) — purpose-built for SQLi/XSS practice.
- **OWASP Mutillidae II** — bundled with Metasploitable 2.
- **Metasploitable 2** on a VirtualBox host-only network — keeps all traffic off your real network and off the internet.

See `LAB_SETUP.md` for full setup and demonstration steps.

## Project Structure

```
web_vuln_scanner/
├── scan.py                  # Unified CLI entry point
├── requirements.txt
├── README.md
├── LAB_SETUP.md             # Lab build + demonstration guide
├── scanner/
│   ├── __init__.py
│   ├── crawler.py           # Page + form discovery
│   ├── sqli.py              # SQL injection detection
│   ├── xss.py               # Reflected XSS detection
│   ├── headers_check.py     # Security-header audit
│   └── reporter.py          # JSON/CSV reporting + summary
└── reports/                 # Saved artefacts (created at runtime)
```

## Limitations & Future Work

- Detects **reflected** XSS and **error-based** SQLi only — not stored XSS, blind/time-based SQLi, or DOM-based issues.
- No authentication handling, so it won't crawl past login forms (a session-login option is a natural extension).
- Possible additions: CSRF token detection, command-injection checks, rate limiting, and an HTML report output.

## Legal & Ethical Notice

This scanner is for **education and authorised testing only**. You are solely responsible for ensuring you have permission to test any target. When in doubt, get written authorisation first.
