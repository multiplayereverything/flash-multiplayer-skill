"""Builds the Bad Ice-Cream online mod from the untouched ../BadIceCream.swf.

  python build.py                    dist/BadIceCream_online.swf (release)
  python build.py --lab              dist/BadIceCream_lab.swf (runs NetLab, prints LAB| traces)
  python build.py --lab --no-adfix   the lab without the ad fix: the control run

Steps: src/ is staged to build/as (lab builds set Net.LAB = true), tools/AddClasses.java adds
empty stubs for the new bicnet classes, ffdec -importScript compiles every staged class into
the SWF (game classes in src/ replace the game's own), tools/CheckNamespaces.java refuses a
build that would break a game subclass, and the FileAttributes UseNetwork flag is set so
Flash Player lets a local SWF open sockets.
"""
import argparse
import os
import re
import shutil
import struct
import subprocess
import sys
import zlib

MOD = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.join(MOD, "..", "BadIceCream.swf")
FFDEC = os.environ.get("FFDEC", os.path.join(MOD, "..", "..", "tools", "ffdec", "ffdec-cli.jar"))
SRC = os.path.join(MOD, "src")
BUILD = os.path.join(MOD, "build")
DIST = os.path.join(MOD, "dist")
LIB = os.path.join(os.path.dirname(os.path.abspath(FFDEC)), "lib", "*")


def run(cmd, what):
    r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    out = r.stdout + r.stderr
    if r.returncode != 0 or re.search(r"SEVERE|Exception|\berror\b", out, re.I) and "0 error" not in out.lower():
        print(out[-4000:])
        sys.exit(what + " failed")
    return out


def stage(lab, adfix):
    dest = os.path.join(BUILD, "as")
    shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(SRC, dest)
    if lab:
        p = os.path.join(dest, "bicnet", "Net.as")
        s = open(p, encoding="utf-8").read()
        old = "public static const LAB:Boolean = false;"
        assert s.count(old) == 1
        open(p, "w", encoding="utf-8").write(s.replace(old, "public static const LAB:Boolean = true;"))
    if not adfix:
        p = os.path.join(dest, "com", "poki", "PokiFlashSDK.as")
        s, n = re.subn(r"[ \t]*// MOD adfix begin.*?// MOD adfix end\n", "", open(p, encoding="utf-8").read(), flags=re.S)
        assert n == 1
        open(p, "w", encoding="utf-8").write(s)
    return dest


def new_classes():
    names = []
    for d, _, fs in os.walk(os.path.join(SRC, "bicnet")):
        for f in fs:
            if f.endswith(".as"):
                rel = os.path.relpath(os.path.join(d, f), SRC)
                names.append(rel[:-3].replace("\\", ".").replace("/", "."))
    return sorted(names)


def set_use_network(path):
    data = open(path, "rb").read()
    sig, ver = data[:3], data[3]
    body = zlib.decompress(data[8:]) if sig == b"CWS" else data[8:]
    nbits = body[0] >> 3
    off = (5 + 4 * nbits + 7) // 8 + 4
    code_len = struct.unpack("<H", body[off:off + 2])[0]
    if code_len >> 6 != 69:
        sys.exit("network: first tag is not FileAttributes")
    body = bytearray(body)
    body[off + 2] |= 1
    open(path, "wb").write(b"CWS" + bytes([ver]) + struct.pack("<I", len(body) + 8) + zlib.compress(bytes(body), 9))


def build(lab, adfix):
    name = "BadIceCream_lab.swf" if lab else "BadIceCream_online.swf"
    if not adfix:
        name = name.replace(".swf", "_noadfix.swf")
    os.makedirs(BUILD, exist_ok=True)
    os.makedirs(DIST, exist_ok=True)
    scripts = stage(lab, adfix)
    stubs = os.path.join(BUILD, "stubs.swf")
    run(["java", "-cp", LIB, os.path.join(MOD, "tools", "AddClasses.java"), GAME, stubs] + new_classes(), "add classes")
    patched = os.path.join(BUILD, "patched.swf")
    log = run(["java", "-jar", FFDEC, "-importScript", stubs, patched, scripts], "ffdec -importScript")
    open(os.path.join(BUILD, "import.log"), "w", encoding="utf-8").write(log)
    r = subprocess.run(["java", "-cp", LIB, os.path.join(MOD, "tools", "CheckNamespaces.java"), GAME, patched],
                       capture_output=True, text=True, errors="replace")
    if r.returncode != 0:
        print(r.stdout[-2000:] + r.stderr[-2000:])
        sys.exit("namespace check failed: a recompiled game class has subclasses that weren't recompiled")
    set_use_network(patched)
    out = os.path.join(DIST, name)
    shutil.copyfile(patched, out)
    print("built", os.path.relpath(out, MOD))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--lab", action="store_true")
    ap.add_argument("--no-adfix", action="store_true")
    a = ap.parse_args()
    build(a.lab, not a.no_adfix)
