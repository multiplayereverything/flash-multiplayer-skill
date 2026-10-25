"""Refuse to publish private data or game files. Run before every push to a public repo.

  python check_public.py                 scan the files git would commit (staged + tracked) in this repo
  python check_public.py path [path...]  scan these files or folders

Exits 1 and lists every hit. Looks for: tokens and keys, passwords, private key blocks, personal Windows and
home paths, email addresses, private and VPN IP ranges, and files that must never be public (SWF, decompiled
folders, .env, SSH keys). The public relay address and localhost are allowed.
"""
import os
import re
import subprocess
import sys

ALLOWED_IPS = {"127.0.0.1", "0.0.0.0", "195.60.166.57"}
PATTERNS = [
    ("token or key", re.compile(r"\b(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|xox[abp]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16})")),
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("password or secret assignment", re.compile(r"(?i)\b(password|passwd|secret|api[_-]?key|auth[_-]?token)\s*[:=]\s*['\"][^'\"]{4,}['\"]")),
    ("personal path", re.compile(r"(?i)([A-Z]:[\\/]+Users[\\/]+(?!<|name|you|USER)[A-Za-z0-9._-]+|/home/(?!<|user\b)[a-z0-9._-]+|/Users/(?!<|name|you)[A-Za-z0-9._-]+)")),
    ("email address", re.compile(r"\b[A-Za-z0-9._%+-]+@(?!example\.)(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}\b")),
]
IP = re.compile(r"\b(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\b")
BAD_FILES = re.compile(r"(?i)(\.swf$|\.env$|(^|/)id_(rsa|ed25519)|(^|/)decompiled/|(^|/)decomp/|\.pem$|\.key$)")
EMAIL_OK = {"noreply@anthropic.com"}


def private_ip(a, b):
    return a == 10 or (a == 192 and b == 168) or (a == 172 and 16 <= b <= 31) or (a == 26) or (a == 25) or (a == 100 and 64 <= b <= 127)


def scan_text(name, text):
    hits = []
    for n, line in enumerate(text.splitlines(), 1):
        if "check_public: ok" in line:
            continue
        for what, rx in PATTERNS:
            for m in rx.finditer(line):
                if what == "email address" and m.group(0) in EMAIL_OK:
                    continue
                hits.append((name, n, what, m.group(0)))
        for m in IP.finditer(line):
            if m.group(0) in ALLOWED_IPS:
                continue
            a, b = int(m.group(1)), int(m.group(2))
            if private_ip(a, b):
                hits.append((name, n, "private or VPN IP", m.group(0)))
    return hits


def files_from_git():
    out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit("not a git repo: pass paths to scan")
    return [f for f in out.stdout.splitlines() if f]


def walk(paths):
    for p in paths:
        if os.path.isdir(p):
            for d, dirs, fs in os.walk(p):
                dirs[:] = [x for x in dirs if x != ".git"]
                for f in fs:
                    yield os.path.join(d, f)
        else:
            yield p


def main(argv):
    files = list(walk(argv)) if argv else files_from_git()
    hits = []
    for f in files:
        rel = f.replace("\\", "/")
        if BAD_FILES.search(rel) and "check_public: ok" not in rel:
            hits.append((rel, 0, "file that must not be public", os.path.basename(rel)))
            continue
        try:
            text = open(f, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        hits += scan_text(rel, text)
    me = os.path.basename(__file__)
    hits = [h for h in hits if not h[0].endswith(me)]
    for name, n, what, s in hits:
        print("%s:%d: %s: %s" % (name, n, what, s))
    print("check_public: %d file(s), %d problem(s)" % (len(files), len(hits)))
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
