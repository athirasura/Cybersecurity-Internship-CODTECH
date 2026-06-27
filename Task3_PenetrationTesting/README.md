# Penetration Testing Toolkit

A modular, Python-based penetration-testing toolkit built as an internship deliverable. It bundles several common reconnaissance and assessment modules behind a single command-line interface.

> **Authorised use only.** Every module in this toolkit is intended to be run against systems you **own** or have **explicit written permission** to test. Unauthorised scanning or access is illegal under the UK Computer Misuse Act 1990 and equivalent legislation worldwide. The brute-force module is deliberately scoped to private/loopback addresses by default for this reason.

---

## Contents

- [Architecture](#architecture)
- [Installation](#installation)
- [Modules](#modules)
  - [Port Scanner](#1-port-scanner)
  - [Banner Grabber](#2-banner-grabber)
  - [Brute-Forcer](#3-brute-forcer)
- [Usage Examples](#usage-examples)
- [Building a Safe Test Lab](#building-a-safe-test-lab)
- [Project Structure](#project-structure)
- [Limitations & Future Work](#limitations--future-work)
- [Legal & Ethical Notice](#legal--ethical-notice)

---

## Architecture

The toolkit follows a simple plug-in pattern. Each capability lives in its own module under `modules/`, exposes a small class with a single public method, and is wired into a unified dispatcher (`toolkit.py`) via subcommands. This keeps modules independently testable and makes it easy to add new ones (e.g. a directory enumerator or a DNS resolver) without touching existing code.

```
toolkit.py  ──►  scan    ──►  PortScanner
            ──►  banner  ──►  BannerGrabber
            ──►  brute   ──►  BruteForcer
```

## Installation

Requires Python 3.8+.

```bash
git clone <your-repo-url> pentest_toolkit
cd pentest_toolkit
pip install -r requirements.txt
```

`requirements.txt` pulls in `paramiko` (SSH) and `requests` (HTTP). The port scanner and banner grabber rely only on the standard library.

## Modules

### 1. Port Scanner

A multithreaded TCP connect scanner. It opens a full TCP handshake to each target port, records which are open, maps well-known ports to service names, and attempts a quick banner read.

- **Threaded** worker pool (default 100 threads) for speed.
- **Hostname resolution** — accepts an IP or a DNS name.
- **Flexible port spec** — ranges (`1-1024`) or lists (`22,80,443`).

```bash
python toolkit.py scan 192.168.56.101 -p 1-1024 -T 200 -t 0.5
```

### 2. Banner Grabber

Connects to specified ports and reads service banners to help fingerprint the software and version running behind each port. Handles plain TCP and TLS-wrapped ports (443/8443), and sends a minimal HTTP probe where appropriate.

```bash
python toolkit.py banner 192.168.56.101 -p 21,22,25,80,443
```

### 3. Brute-Forcer

A credential-testing module for **lab services you control**. Supports SSH, FTP, and HTTP Basic Auth. It iterates username/password wordlists and reports valid pairs.

Safety design:
- Refuses non-private / non-loopback targets unless you explicitly pass `--i-have-authorisation`, making that a conscious decision rather than a silent default.
- Built-in `--delay` throttle between attempts.
- Stops after the first valid password per user.

```bash
python toolkit.py brute 192.168.56.101 ssh \
    -U wordlists/users.txt -P wordlists/passwords.txt --delay 0.2
```

## Usage Examples

A typical authorised assessment workflow against your own VM:

```bash
# 1. Discover open ports
python toolkit.py scan 192.168.56.101 -p 1-1024

# 2. Fingerprint the services found
python toolkit.py banner 192.168.56.101 -p 21,22,80

# 3. Test credential strength on a service you control
python toolkit.py brute 192.168.56.101 ssh -U wordlists/users.txt -P wordlists/passwords.txt
```

## Building a Safe Test Lab

To exercise this toolkit legally and reproducibly, stand up an intentionally vulnerable target in an isolated, host-only network:

- **Metasploitable 2/3** — classic vulnerable Linux VM (open FTP/SSH/HTTP, weak `msfadmin:msfadmin` credentials).
- **DVWA** (Damn Vulnerable Web Application) — for HTTP-auth testing.
- **VirtualBox host-only adapter** — keeps lab traffic off your real network and off the internet.

The sample wordlists in `wordlists/` are tuned for Metasploitable's default accounts so you can validate the brute-force module immediately.

## Project Structure

```
pentest_toolkit/
├── toolkit.py              # Unified CLI dispatcher
├── requirements.txt
├── README.md
├── modules/
│   ├── __init__.py
│   ├── port_scanner.py     # Threaded TCP port scanner
│   ├── banner_grabber.py   # Service banner / version enumeration
│   └── brute_forcer.py     # SSH/FTP/HTTP credential tester (lab-scoped)
└── wordlists/
    ├── users.txt
    └── passwords.txt
```

## Limitations & Future Work

- TCP connect scan only (no raw-socket SYN scan, which needs root and raw packet crafting).
- Banner grabbing is heuristic, not a full version-detection database like Nmap's.
- Possible extensions: UDP scanning, a directory/file enumerator, threaded brute-forcing, structured JSON/CSV report output, and a results logger.

## Legal & Ethical Notice

This toolkit is provided for **education and authorised testing only**. By using it you agree that you are solely responsible for ensuring you have permission to test the target. The author and this internship deliverable accept no liability for misuse. When in doubt, get written authorisation first and keep it on file.
