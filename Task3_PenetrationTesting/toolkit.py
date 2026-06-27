#!/usr/bin/env python3
"""
toolkit.py
Unified CLI for the modular penetration-testing toolkit.

    python toolkit.py scan   192.168.56.101 -p 1-1024
    python toolkit.py banner 192.168.56.101 -p 22,80,443
    python toolkit.py brute  192.168.56.101 ssh -U users.txt -P pass.txt

AUTHORISED USE ONLY. Run these modules against systems you own or have
explicit written permission to test. Unauthorised access is illegal under
the Computer Misuse Act 1990 (UK) and equivalent laws elsewhere.
"""

import argparse
import sys
from modules import PortScanner, BannerGrabber
from modules.brute_forcer import BruteForcer, load_wordlist, _is_lab_target


def parse_ports(spec):
    if "-" in spec:
        lo, hi = map(int, spec.split("-"))
        return range(lo, hi + 1)
    return [int(x) for x in spec.split(",")]


def cmd_scan(args):
    PortScanner(args.target, args.timeout, args.threads).scan(parse_ports(args.ports))


def cmd_banner(args):
    BannerGrabber(args.target).enumerate(parse_ports(args.ports))


def cmd_brute(args):
    if not _is_lab_target(args.target) and not args.i_have_authorisation:
        sys.exit("[ABORT] Non-private target. Re-run with --i-have-authorisation "
                 "only if you hold written permission for this host.")
    users = load_wordlist(args.userlist)
    passwords = load_wordlist(args.passlist)
    extra = {"path": args.path} if args.protocol == "http" else {}
    BruteForcer(args.target, args.port, args.delay).run(
        args.protocol, users, passwords, **extra)


def build_parser():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("scan", help="TCP port scan")
    s.add_argument("target")
    s.add_argument("-p", "--ports", default="1-1024")
    s.add_argument("-t", "--timeout", type=float, default=1.0)
    s.add_argument("-T", "--threads", type=int, default=100)
    s.set_defaults(func=cmd_scan)

    b = sub.add_parser("banner", help="Grab service banners")
    b.add_argument("target")
    b.add_argument("-p", "--ports", default="21,22,25,80,443")
    b.set_defaults(func=cmd_banner)

    f = sub.add_parser("brute", help="Credential test (lab only)")
    f.add_argument("target")
    f.add_argument("protocol", choices=["ssh", "ftp", "http"])
    f.add_argument("-p", "--port", type=int, default=0)
    f.add_argument("-U", "--userlist", required=True)
    f.add_argument("-P", "--passlist", required=True)
    f.add_argument("--delay", type=float, default=0.1)
    f.add_argument("--path", default="/")
    f.add_argument("--i-have-authorisation", action="store_true")
    f.set_defaults(func=cmd_brute)
    return p


if __name__ == "__main__":
    args = build_parser().parse_args()
    args.func(args)
