# Cybersecurity Internship — CODTECH

A collection of Python-based cybersecurity projects completed during my internship with CODTECH. Each task is a self-contained tool with its own documentation, spanning defensive and offensive security: file integrity monitoring, data encryption, penetration testing, and web vulnerability scanning.

> **Authorised use only.** The tools in this repository are built for education and for testing systems you own or have explicit written permission to assess. Unauthorised use against systems you do not control may be illegal under the Computer Misuse Act 1990 (UK) and equivalent legislation elsewhere.

---

## Tasks

### Task 1 — File Integrity Monitoring
A tool that monitors files for unauthorised changes by calculating and comparing cryptographic hashes, flagging any files that have been modified, added, or removed.
📁 [`Task1_FileIntegrity`](./Task1_FileIntegrity)

### Task 2 — Encryption Tool
A utility for encrypting and decrypting files and data, demonstrating the practical application of cryptography to protect sensitive information.
📁 [`Task2_EncryptionTool`](./Task2_EncryptionTool)

### Task 3 — Penetration Testing Toolkit
A modular toolkit bundling several assessment modules — a multithreaded port scanner, a service banner grabber, an HTTP directory enumerator, and a lab-scoped credential tester — behind a single command-line interface, with JSON/CSV reporting and a full lab setup guide.
📁 [`Task3_PenetrationTesting`](./Task3_PenetrationTesting)

### Task 4 — Web Application Vulnerability Scanner
A scanner built with `requests` and `BeautifulSoup` that crawls a web application and checks for common vulnerabilities — SQL injection, reflected cross-site scripting (XSS), and missing security headers — with severity-grouped reporting and JSON/CSV output.
📁 [`Task4_WebVulnScanner`](./Task4_WebVulnScanner)

---

## Tech Stack

- **Language:** Python 3
- **Focus areas:** file integrity / hashing, cryptography, network reconnaissance, authorised penetration testing, and web application security
- Each task folder contains its own README with installation and usage instructions.

## About

These projects were completed as part of a CODTECH cybersecurity internship, building practical tooling across defensive (integrity monitoring, encryption) and offensive (reconnaissance, penetration testing, web vulnerability scanning) security domains.
