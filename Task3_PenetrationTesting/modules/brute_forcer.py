"""
brute_forcer.py
Credential testing module for AUTHORISED lab use.

This module is deliberately scoped to services you control. It refuses to run
against non-private / non-loopback addresses unless you pass --i-have-authorisation,
which exists so the safety prompt is a conscious, logged choice rather than a default.

Supported protocols: SSH, FTP, HTTP Basic Auth.
Intended targets: your own VM, localhost, DVWA, Metasploitable, etc.
"""

import argparse
import ipaddress
import socket
import sys
import time
from datetime import datetime

# Third-party libs used for protocol handling.
# pip install paramiko requests
try:
    import paramiko
except ImportError:
    paramiko = None
try:
    import requests
    from requests.auth import HTTPBasicAuth
except ImportError:
    requests = None
import ftplib


def _is_lab_target(host):
    """Allow loopback and RFC1918 private ranges by default."""
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(host))
    except (ValueError, socket.gaierror):
        return False
    return ip.is_loopback or ip.is_private


def load_wordlist(path):
    with open(path, "r", errors="ignore") as fh:
        return [line.strip() for line in fh if line.strip()]


class BruteForcer:
    def __init__(self, host, port, delay=0.0):
        self.host = host
        self.port = port
        self.delay = delay  # throttle between attempts; be a good citizen even in a lab

    # ---- SSH ----
    def try_ssh(self, username, password):
        if paramiko is None:
            raise RuntimeError("paramiko not installed (pip install paramiko)")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(self.host, port=self.port or 22, username=username,
                           password=password, timeout=5,
                           allow_agent=False, look_for_keys=False)
            return True
        except paramiko.AuthenticationException:
            return False
        except Exception as e:
            print(f"[!] SSH error: {e}")
            return False
        finally:
            client.close()

    # ---- FTP ----
    def try_ftp(self, username, password):
        try:
            with ftplib.FTP() as ftp:
                ftp.connect(self.host, self.port or 21, timeout=5)
                ftp.login(username, password)
                return True
        except ftplib.error_perm:
            return False
        except Exception as e:
            print(f"[!] FTP error: {e}")
            return False

    # ---- HTTP Basic Auth ----
    def try_http(self, username, password, path="/"):
        if requests is None:
            raise RuntimeError("requests not installed (pip install requests)")
        url = f"http://{self.host}:{self.port or 80}{path}"
        try:
            r = requests.get(url, auth=HTTPBasicAuth(username, password), timeout=5)
            return r.status_code not in (401, 403)
        except Exception as e:
            print(f"[!] HTTP error: {e}")
            return False

    def run(self, protocol, users, passwords, **kw):
        attempt = getattr(self, f"try_{protocol}")
        total = len(users) * len(passwords)
        print(f"[*] {protocol.upper()} brute force on {self.host}:{self.port} "
              f"({total} combinations) {datetime.now():%H:%M:%S}")
        found = []
        n = 0
        for user in users:
            for pw in passwords:
                n += 1
                if attempt(user, pw, **kw):
                    print(f"[+] SUCCESS  {user}:{pw}")
                    found.append((user, pw))
                    break  # stop on first hit for this user
                if self.delay:
                    time.sleep(self.delay)
            sys.stdout.write(f"\r[*] {n}/{total} tried")
            sys.stdout.flush()
        print()
        return found


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lab credential tester (authorised use only)")
    parser.add_argument("host")
    parser.add_argument("protocol", choices=["ssh", "ftp", "http"])
    parser.add_argument("-p", "--port", type=int, default=0)
    parser.add_argument("-U", "--userlist", required=True)
    parser.add_argument("-P", "--passlist", required=True)
    parser.add_argument("--delay", type=float, default=0.1)
    parser.add_argument("--path", default="/", help="URL path for http mode")
    parser.add_argument("--i-have-authorisation", action="store_true",
                        help="Required to target a non-private address")
    args = parser.parse_args()

    if not _is_lab_target(args.host) and not args.i_have_authorisation:
        sys.exit("[ABORT] Target is not loopback/private. This tool is for your own lab. "
                 "If you have written authorisation for this host, re-run with "
                 "--i-have-authorisation.")

    users = load_wordlist(args.userlist)
    passwords = load_wordlist(args.passlist)
    bf = BruteForcer(args.host, args.port, args.delay)
    extra = {"path": args.path} if args.protocol == "http" else {}
    bf.run(args.protocol, users, passwords, **extra)
