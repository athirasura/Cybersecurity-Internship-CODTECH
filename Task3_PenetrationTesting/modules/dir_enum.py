"""
dir_enum.py
HTTP directory / file enumerator.

Requests paths from a wordlist against a target web server and reports those
that exist (non-404). Useful for discovering hidden directories and files on
web apps you are authorised to test.
"""

import threading
from queue import Queue
from datetime import datetime

try:
    import requests
except ImportError:
    requests = None

# Status codes generally worth reporting as "found"
INTERESTING = {200, 201, 204, 301, 302, 307, 401, 403}


class DirEnumerator:
    def __init__(self, base_url, threads=20, timeout=5, extensions=None):
        if requests is None:
            raise RuntimeError("requests not installed (pip install requests)")
        self.base_url = base_url.rstrip("/")
        self.threads = threads
        self.timeout = timeout
        self.extensions = extensions or [""]
        self._queue = Queue()
        self._lock = threading.Lock()
        self.found = []

    def _check(self, path):
        for ext in self.extensions:
            candidate = f"{path}{ext}" if ext else path
            url = f"{self.base_url}/{candidate.lstrip('/')}"
            try:
                r = requests.get(url, timeout=self.timeout, allow_redirects=False)
                if r.status_code in INTERESTING:
                    with self._lock:
                        self.found.append((candidate, r.status_code, len(r.content)))
                        print(f"[+] {r.status_code}  /{candidate}  ({len(r.content)} bytes)")
            except requests.RequestException:
                pass

    def _worker(self):
        while not self._queue.empty():
            self._check(self._queue.get())
            self._queue.task_done()

    def enumerate(self, wordlist):
        print(f"[*] Enumerating {self.base_url} "
              f"({len(wordlist)} paths) {datetime.now():%H:%M:%S}")
        for word in wordlist:
            self._queue.put(word.strip())

        workers = [threading.Thread(target=self._worker, daemon=True)
                   for _ in range(self.threads)]
        for w in workers:
            w.start()
        self._queue.join()

        self.found.sort()
        print(f"[*] Done. {len(self.found)} path(s) found.\n")
        return self.found


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="HTTP directory enumerator")
    parser.add_argument("url", help="Base URL, e.g. http://192.168.56.101")
    parser.add_argument("-w", "--wordlist", required=True)
    parser.add_argument("-x", "--extensions", default="",
                        help="Comma list, e.g. .php,.html,.txt")
    parser.add_argument("-T", "--threads", type=int, default=20)
    args = parser.parse_args()

    with open(args.wordlist, errors="ignore") as fh:
        words = [l.strip() for l in fh if l.strip()]
    exts = [""] + [e if e.startswith(".") else f".{e}"
                   for e in args.extensions.split(",") if e]
    DirEnumerator(args.url, args.threads, extensions=exts).enumerate(words)
