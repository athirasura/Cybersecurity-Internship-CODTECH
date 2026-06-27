# Lab Setup & Demonstration Guide

How to build a safe, legal environment to run the Web Application Vulnerability Scanner and capture evidence for your deliverable's "Results" section.

---

## Why a lab?

Never scan a web application you don't own or have written permission to test. A self-contained lab with an intentionally vulnerable app gives you a legal target where finding SQLi and XSS is the whole point.

---

## Part 1 — Build the lab

The fastest route is **DVWA** (Damn Vulnerable Web Application), which is purpose-built to contain SQL injection and XSS for practice.

### Option A — DVWA via Docker (quickest, ~5 min)

If you have Docker installed:
```bash
docker run --rm -it -p 8080:80 vulnerables/web-dvwa
```
DVWA is then at `http://localhost:8080`. Log in with `admin` / `password`, click "Create / Reset Database", and set the security level to **Low** (DVWA Security menu) so the vulnerabilities are active.

### Option B — Metasploitable 2 (also gives you Mutillidae)

1. Install **VirtualBox** and import **Metasploitable 2** (see the pentest toolkit's lab guide for full VM steps).
2. Set the VM's network adapter to **Host-only** so it's isolated.
3. Boot it, log in (`msfadmin` / `msfadmin`), run `ifconfig` to get its IP (e.g. `192.168.56.101`).
4. Vulnerable apps are served at `http://192.168.56.101/dvwa/` and `http://192.168.56.101/mutillidae/`.

---

## Part 2 — Run the scanner & capture evidence

From the scanner directory, replacing the URL with your lab target. **Screenshot each step.**

### 1. Full scan
```bash
python scan.py http://192.168.56.101/dvwa/ --max-pages 20
```
This crawls the app, then runs all three checks. Watch the live progress lines, then the severity-grouped summary at the end.

### 2. Show the saved reports
After the scan, look in the `reports/` folder:
```bash
ls reports/
cat reports/scan_*.json
```
The JSON and CSV are your evidence artefacts — include one in your submission.

### 3. (Optional) Targeted runs for cleaner screenshots
```bash
# SQL injection only
python scan.py http://192.168.56.101/dvwa/ --checks sqli

# XSS only
python scan.py http://192.168.56.101/dvwa/ --checks xss

# Security headers only
python scan.py http://192.168.56.101/dvwa/ --checks headers
```
Running checks individually produces focused output that's easy to annotate.

---

## Part 3 — Write up the results

Add a **Demonstration / Results** section to your documentation with:

1. A line describing the lab (DVWA at Low security on an isolated network).
2. Annotated screenshots: the crawl, the SQLi finding, the XSS finding, the header audit, and the final summary.
3. One saved JSON/CSV report as an evidence artefact.
4. A short "Findings" paragraph framing it as a mini assessment: pages crawled → forms found → SQLi confirmed via error signature → XSS confirmed via reflection → hardening gaps in headers.

That crawl-to-confirmed-vulnerability narrative is exactly what a reviewer wants, and it pairs naturally with the offensive-security story from your pentest toolkit task.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Scan finds no vulns on DVWA | Confirm DVWA security is set to **Low** and the database is initialised. |
| Crawler stops at login | DVWA needs a session; for the demo, point the scanner directly at a vulnerable page URL, or set security to Low after logging in via browser in the same session. |
| `requests`/`bs4` import error | `pip install -r requirements.txt` |
| Can't reach the VM | Confirm Adapter 1 is **Host-only** and use the IP from `ifconfig`. |
