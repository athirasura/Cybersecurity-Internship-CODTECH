"""
crawler.py
Lightweight web crawler. Discovers internal links and HTML forms on a target
site so the vulnerability checks know where to probe.

Authorised use only: crawl sites you own or have written permission to test.
"""

from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup


class Crawler:
    def __init__(self, base_url, max_pages=30, timeout=8):
        self.base_url = base_url.rstrip("/")
        self.domain = urlparse(self.base_url).netloc
        self.max_pages = max_pages
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "vuln-scanner/1.0 (authorised testing)"})
        self.visited = set()
        self.forms = []   # list of (page_url, form_details)

    def _same_domain(self, url):
        return urlparse(url).netloc == self.domain

    def extract_forms(self, url, soup):
        """Parse every <form> on a page into a probe-ready description."""
        for form in soup.find_all("form"):
            details = {
                "action": form.attrs.get("action") or "",
                "method": (form.attrs.get("method") or "get").lower(),
                "inputs": [],
            }
            for tag in form.find_all(["input", "textarea", "select"]):
                details["inputs"].append({
                    "name": tag.attrs.get("name"),
                    "type": tag.attrs.get("type", "text"),
                    "value": tag.attrs.get("value", ""),
                })
            self.forms.append((url, details))

    def crawl(self):
        queue = [self.base_url]
        print(f"[*] Crawling {self.base_url} (max {self.max_pages} pages)")
        while queue and len(self.visited) < self.max_pages:
            url = queue.pop(0)
            if url in self.visited:
                continue
            try:
                resp = self.session.get(url, timeout=self.timeout)
            except requests.RequestException:
                continue
            self.visited.add(url)
            soup = BeautifulSoup(resp.text, "html.parser")
            self.extract_forms(url, soup)

            for link in soup.find_all("a", href=True):
                full = urljoin(url, link["href"]).split("#")[0]
                if self._same_domain(full) and full not in self.visited:
                    queue.append(full)

        print(f"[*] Crawl complete: {len(self.visited)} pages, {len(self.forms)} forms found.\n")
        return self.visited, self.forms
