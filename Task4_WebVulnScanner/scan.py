#!/usr/bin/env python3
"""
scan.py
Web Application Vulnerability Scanner — unified entry point.

Crawls a target web application and runs a set of vulnerability checks
(SQL injection, reflected XSS, missing security headers), then reports findings.

    python scan.py http://192.168.56.101/dvwa/
    python scan.py http://testphp.vulnweb.com/ --max-pages 15

AUTHORISED USE ONLY. Only scan web applications you own or have explicit
written permission to test. Unauthorised scanning may be illegal under the
Computer Misuse Act 1990 (UK) and equivalent laws elsewhere.
"""

import argparse
import sys
from scanner import Crawler, Reporter, sqli, xss, headers_check


def run_scan(base_url, max_pages, checks):
    crawler = Crawler(base_url, max_pages=max_pages)
    session = crawler.session
    pages, forms = crawler.crawl()

    findings = []

    if "headers" in checks:
        print("[*] Checking security headers...")
        findings += headers_check.check(session, base_url)

    if "sqli" in checks:
        print("[*] Testing for SQL injection...")
        for page_url, form in forms:
            findings += sqli.check_form(session, page_url, form)
        for url in pages:
            findings += sqli.check_url_param(session, url)

    if "xss" in checks:
        print("[*] Testing for reflected XSS...")
        for page_url, form in forms:
            findings += xss.check_form(session, page_url, form)
        for url in pages:
            findings += xss.check_url_param(session, url)

    return findings


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("url", help="Target base URL (must be authorised)")
    parser.add_argument("--max-pages", type=int, default=30,
                        help="Maximum pages to crawl (default 30)")
    parser.add_argument("--checks", default="sqli,xss,headers",
                        help="Comma list of checks: sqli,xss,headers")
    parser.add_argument("--no-report", action="store_true",
                        help="Skip saving JSON/CSV reports")
    args = parser.parse_args()

    if not args.url.startswith(("http://", "https://")):
        sys.exit("[ABORT] URL must start with http:// or https://")

    checks = [c.strip() for c in args.checks.split(",")]
    print(f"\n[*] Starting scan of {args.url}")
    print(f"[*] Checks enabled: {', '.join(checks)}\n")

    findings = run_scan(args.url, args.max_pages, checks)

    reporter = Reporter(args.url)
    reporter.summary(findings)
    if not args.no_report:
        reporter.save(findings)


if __name__ == "__main__":
    main()
