"""
banner_grabber.py
Service banner grabbing + lightweight enumeration.

Pulls service banners from open ports to help fingerprint software/versions.
Authorised targets only.
"""

import socket
import ssl
from datetime import datetime

PROBES = {
    "http":  b"HEAD / HTTP/1.0\r\n\r\n",
    "https": b"HEAD / HTTP/1.0\r\n\r\n",
    "smtp":  b"EHLO scanner.local\r\n",
    "ftp":   b"",
    "ssh":   b"",
}


class BannerGrabber:
    def __init__(self, target, timeout=3.0):
        self.target = target
        self.timeout = timeout

    def grab(self, port, use_tls=False, probe=b""):
        try:
            raw = socket.create_connection((self.target, port), self.timeout)
            sock = (ssl.create_default_context().wrap_socket(
                        raw, server_hostname=self.target)
                    if use_tls else raw)
            sock.settimeout(self.timeout)
            if probe:
                sock.sendall(probe)
            data = sock.recv(2048).decode(errors="ignore").strip()
            sock.close()
            return data
        except Exception as e:
            return f"<no banner: {e}>"

    def enumerate(self, ports):
        print(f"[*] Banner grab on {self.target} {datetime.now():%H:%M:%S}")
        results = {}
        for port in ports:
            use_tls = port in (443, 8443)
            probe = b"GET / HTTP/1.0\r\n\r\n" if port in (80, 443, 8080, 8443) else b""
            banner = self.grab(port, use_tls=use_tls, probe=probe)
            results[port] = banner
            print(f"[+] {port:>5}: {banner.splitlines()[0] if banner else ''}")
        return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Service banner grabber")
    parser.add_argument("target")
    parser.add_argument("-p", "--ports", default="21,22,25,80,443")
    args = parser.parse_args()
    ports = [int(x) for x in args.ports.split(",")]
    BannerGrabber(args.target).enumerate(ports)
