# Lab Setup & Demonstration Guide

A step-by-step walkthrough for building a safe, legal test environment and demonstrating every module of the toolkit. Follow this to produce the screenshots/recording for your deliverable's "Results" section.

---

## Why a lab?

You must **never** run these tools against systems you don't own or have written permission to test. A self-contained virtual lab gives you a legal target and keeps all traffic off your real network and off the internet.

---

## Part 1 — Build the lab (~20–30 min)

### What you need
- **VirtualBox** (free) — the hypervisor.
- **Metasploitable 2** — a deliberately vulnerable Linux VM with open FTP, SSH, HTTP and weak default credentials (`msfadmin` / `msfadmin`).
- Your own machine running the toolkit (the "attacker").

### Steps

1. **Install VirtualBox** from the official Oracle site for your OS.

2. **Download Metasploitable 2** (a free, widely used vulnerable VM distributed as a ZIP containing a `.vmdk` disk image). Search "Metasploitable 2 download Rapid7" for the current official source.

3. **Create the VM in VirtualBox:**
   - New → Name "Metasploitable2", Type: Linux, Version: Other Linux (64-bit).
   - Memory: 512 MB is plenty.
   - "Use an existing virtual hard disk file" → select the extracted `.vmdk`.

4. **Isolate the network — this is the important part:**
   - Select the VM → Settings → Network → Adapter 1.
   - Set "Attached to" → **Host-only Adapter**.
   - This puts the VM on a private network reachable only from your host, with no internet route. Nothing can leak out, and you can't accidentally hit a real target.

5. **Boot the VM.** Log in with `msfadmin` / `msfadmin`. Run `ifconfig` and note its IP (typically something like `192.168.56.101`). This is your `TARGET`.

> If you'd rather not run a full VM, **DVWA** (Damn Vulnerable Web Application) in a Docker container is a lighter alternative for the HTTP-based modules (`dirs`, `brute http`).

---

## Part 2 — Run the toolkit & capture evidence

Run these from your toolkit directory, replacing `192.168.56.101` with your VM's actual IP. Add `--report` to save JSON/CSV artefacts you can include in the submission. **Screenshot each step.**

### 1. Port scan — discover open services
```bash
python toolkit.py scan 192.168.56.101 -p 1-1024 -T 200 --report
```
Expect open ports like 21 (ftp), 22 (ssh), 23 (telnet), 80 (http), 3306 (mysql).

### 2. Banner grab — fingerprint the services
```bash
python toolkit.py banner 192.168.56.101 -p 21,22,80 --report
```
Captures version strings (e.g. the vsftpd / OpenSSH / Apache banners) useful for identifying known vulnerabilities.

### 3. Directory enumeration — find hidden web paths
```bash
python toolkit.py dirs http://192.168.56.101 -w wordlists/dirs.txt -x .php,.html --report
```
Metasploitable hosts apps like DVWA and Mutillidae, so you should see several hits.

### 4. Credential test — demonstrate weak-password risk
```bash
python toolkit.py brute 192.168.56.101 ssh -U wordlists/users.txt -P wordlists/passwords.txt --delay 0.2 --report
```
The sample wordlists include `msfadmin`, so this should recover the valid SSH login — a clean demonstration of why default credentials are dangerous. The target is private, so no authorisation flag is needed.

---

## Part 3 — Write up the results

For the deliverable, add a **Demonstration / Results** section to your documentation containing:

1. A one-line description of the lab (Metasploitable 2 on a host-only network).
2. The four annotated screenshots, in order, each with a sentence on what it shows.
3. One or two of the saved JSON/CSV reports from the `reports/` folder as evidence artefacts.
4. A short "Findings" paragraph: open ports → identified services → discovered paths → recovered credentials, framed as a mini assessment narrative.

That recon-to-credential-recovery arc is exactly the story a reviewer wants to see, and it maps directly onto the forensic-investigator-to-SOC analyst positioning you've been building.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Can't ping the VM | Confirm Adapter 1 is **Host-only**, and check the host-only network exists under VirtualBox → Tools → Network. |
| `paramiko`/`requests` import error | `pip install -r requirements.txt` |
| Scan finds nothing | Make sure you're scanning the VM's IP from `ifconfig`, not `127.0.0.1`. |
| Brute force too slow | Lower `--delay`, but keep some throttle to mimic responsible testing. |
