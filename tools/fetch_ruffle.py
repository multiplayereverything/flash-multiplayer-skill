"""Fetch the pinned Ruffle Together release and check its hashes.

    python -I tools/fetch_ruffle.py                 # into the default folder below
    python -I tools/fetch_ruffle.py --dest <folder> # into your own folder

Downloads RuffleTogether-<VERSION>-windows-x64.zip from GitHub, checks the zip's SHA-256,
extracts ruffle_desktop.exe, checks its SHA-256, and copies it to <dest>/ruffle_desktop.exe.
Standard library only. Change the pin here when a new release is out, and update playbook/ruffle-together.md.
"""
import argparse
import hashlib
import os
import shutil
import sys
import tempfile
import urllib.request
import zipfile

VERSION = "1.0.3.9"
ZIP_NAME = "RuffleTogether-%s-windows-x64.zip" % VERSION
URL = "https://github.com/multiplayereverything/ruffle-together/releases/download/v%s/%s" % (VERSION, ZIP_NAME)
ZIP_SHA256 = "d7d0a0560891193f6504b1d2fe19f2ee5cc6bbb20089be06b087eede746c4eb0"
EXE_SHA256 = "c459ed434c0fc185c27b424871d59d166508a7ff499fda26ad66b3fa0d928c27"
DEFAULT_DEST = os.path.join(os.environ.get("USERPROFILE", "~"), "Documents", "MultiplayerEverythingLauncher",
                            "players", "ruffle-together")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dest", default=DEFAULT_DEST, help="folder for ruffle_desktop.exe (default: the launcher's folder)")
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        zip_path = os.path.join(tmp, ZIP_NAME)
        print("downloading", URL)
        urllib.request.urlretrieve(URL, zip_path)
        got = sha256(zip_path)
        if got != ZIP_SHA256:
            sys.exit("zip SHA-256 mismatch: got %s, expected %s" % (got, ZIP_SHA256))
        with zipfile.ZipFile(zip_path) as z:
            member = next(n for n in z.namelist() if n.endswith("ruffle_desktop.exe"))
            z.extract(member, tmp)
        exe = os.path.join(tmp, member)
        got = sha256(exe)
        if got != EXE_SHA256:
            sys.exit("exe SHA-256 mismatch: got %s, expected %s" % (got, EXE_SHA256))
        os.makedirs(a.dest, exist_ok=True)
        out = os.path.join(a.dest, "ruffle_desktop.exe")
        shutil.copyfile(exe, out)
    print("ok", VERSION, out, EXE_SHA256)


if __name__ == "__main__":
    main()
