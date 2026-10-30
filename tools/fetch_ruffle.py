"""Fetch the pinned Ruffle Together release and check its hashes.

    python -I tools/fetch_ruffle.py                 # into the default folder below
    python -I tools/fetch_ruffle.py --dest <folder> # into your own folder

Downloads RuffleTogether-<VERSION>-windows-x64.zip from GitHub, checks the zip's SHA-256,
extracts ruffle_desktop.exe, checks its SHA-256, and copies it to <dest>/ruffle_desktop.exe.
Standard library only. Change the pin here when a new release is out, and update playbook/ruffle.md.
"""
import argparse
import hashlib
import os
import shutil
import sys
import tempfile
import urllib.request
import zipfile

VERSION = "1.0.3.8"
ZIP_NAME = "RuffleTogether-%s-windows-x64.zip" % VERSION
URL = "https://github.com/multiplayereverything/ruffle-coop/releases/download/v%s/%s" % (VERSION, ZIP_NAME)
ZIP_SHA256 = "630847feb0443f50a677cfd5f09635aaaf772b018cc1fe13d94e3d14622c8a59"
EXE_SHA256 = "d269dd6e367e9462ca933803f63a302f135e5c6f5b659c2c790bd0c590934c7c"
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
