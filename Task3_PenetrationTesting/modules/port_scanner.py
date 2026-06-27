"""
port_scanner.py
TCP connect / SYN-style port scanner module.

Authorised use only: scan hosts you own or have written permission to test.
"""

import socket
import threading
import ipaddress
from queue import Queue
from datetime import datetime

# Common service map for quick identification
COMMON_PORTS = {
    21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns",
    80: "http", 110: "pop3", 139: "netbios", 143: "imap", 443: "https",
    445: "smb", 3306: "mysql", 3389: "rdp", 5432: "postgres",
    8080: "http-alt", 8443: "https-alt",
}


class PortScanner:
    def __init__(self, target, timeout=1.0, threads=100):
        self.target = self._resolve(target)
        self.timeout = timeout
        self.threads = threads
        self._queue = Queue()
        self._lock = threading.Lock()
        self.open_ports = []

    @staticmethod
    def _resolve(target):
        """Accept an IP or hostname; return a dotted-quad string."""
        try:
            ipaddress.ip_address(target)
            return target
        except ValueError:
            return socket.gethostbyname(target)

    def _grab_banner(self, sock):
        """Best-effort service banner read."""
        try:
            sock.settimeout(self.timeout)
            return sock.recv(1024).decode(errors="ignore").strip()
        except Exception:
            return ""

    def _scan_port(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(self.timeout)
            if sock.connect_ex((self.target, port)) == 0:
                banner = self._grab_banner(sock)
                service = COMMON_PORTS.get(port, "unknown")
                with self._lock:
                    self.open_ports.append((port, service, banner))
                    print(f"[+] {port:>5}/tcp open  {service:<10} {banner[:60]}")

    def _worker(self):
        while not self._queue.empty():
            self._scan_port(self._queue.get())
            self._queue.task_done()

    def scan(self, ports=range(1, 1025)):
        print(f"\n[*] Scanning {self.target} ({len(list(ports))} ports) "
              f"started {datetime.now():%H:%M:%S}")
        for p in ports:
            self._queue.put(p)

        workers = [threading.Thread(target=self._worker, daemon=True)
                   for _ in range(self.threads)]
        for w in workers:
            w.start()
        self._queue.join()

        self.open_ports.sort()
        print(f"[*] Done. {len(self.open_ports)} open port(s) found.\n")
        return self.open_ports


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Threaded TCP port scanner")
    parser.add_argument("target", help="IP or hostname (must be authorised)")
    parser.add_argument("-p", "--ports", default="1-1024",
                        help="Port range, e.g. 1-1024 or 22,80,443")
    parser.add_argument("-t", "--timeout", type=float, default=1.0)
    parser.add_argument("-T", "--threads", type=int, default=100)
    args = parser.parse_args()

    if "-" in args.ports:
        lo, hi = map(int, args.ports.split("-"))
        port_list = range(lo, hi + 1)
    else:
        port_list = [int(x) for x in args.ports.split(",")]

    PortScanner(args.target, args.timeout, args.threads).scan(port_list)
