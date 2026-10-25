"""Builds Territory War Online from the untouched ../territory-war-279.swf.

  python build.py          dist/TerritoryWar_online.swf (release)
  python build.py --lab    dist/TerritoryWar_lab.swf (runs the lab scripts in src/lab.as, prints LAB| traces)

Steps: tools/InsertAction.java compiles each module in src/ (AS2, FFDec's compiler) into its own new DoAction
tag at the end of main-timeline frame 3, the first frame after the preloader. The game's own scripts are not
decompiled or recompiled. Then the FileAttributes UseNetwork flag is set so Flash Player lets a local SWF open
sockets. A check confirms the only changes are the added tags and that flag.
"""
import argparse
import os
import struct
import subprocess
import sys
import zlib

MOD = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.join(MOD, "..", "territory-war-279.swf")
FFDEC = os.environ.get("FFDEC", os.path.join(MOD, "..", "..", "tools", "ffdec", "ffdec-cli.jar"))
LIB = os.path.join(os.path.dirname(os.path.abspath(FFDEC)), "lib", "*")
SRC = os.path.join(MOD, "src")
BUILD = os.path.join(MOD, "build")
DIST = os.path.join(MOD, "dist")
MODULES = ["net.as", "host.as", "guest.as", "ui.as", "modinfo.as", "lab.as", "boot.as"]
FRAME = 3


def body(data):
    return zlib.decompress(data[8:]) if data[:3] == b"CWS" else data[8:]


def tag_list(b):
    nbits = b[0] >> 3
    off = (5 + 4 * nbits + 7) // 8 + 4
    out = []
    while off < len(b):
        start = off
        cl = struct.unpack("<H", b[off:off + 2])[0]
        t, ln = cl >> 6, cl & 63
        off += 2
        if ln == 63:
            ln = struct.unpack("<I", b[off:off + 4])[0]
            off += 4
        out.append((t, b[off:off + ln], start))
        off += ln
        if t == 0:
            break
    return out


def set_use_network(path):
    data = open(path, "rb").read()
    b = bytearray(body(data))
    nbits = b[0] >> 3
    off = (5 + 4 * nbits + 7) // 8 + 4
    if struct.unpack("<H", b[off:off + 2])[0] >> 6 != 69:
        sys.exit("network: first tag is not FileAttributes")
    b[off + 2] |= 1
    open(path, "wb").write(b"CWS" + bytes([data[3]]) + struct.pack("<I", len(b) + 8) + zlib.compress(bytes(b), 9))


def check(original, built, added):
    """Every original tag is still there, byte for byte and in order; the new ones are DoAction tags."""
    a = tag_list(body(open(original, "rb").read()))
    b = tag_list(body(open(built, "rb").read()))
    if len(b) != len(a) + added:
        sys.exit("check: expected %d added tags, got %d" % (added, len(b) - len(a)))
    i = j = 0
    extra = 0
    while i < len(a):
        ta, da, _ = a[i]
        tb, db, _ = b[j]
        if ta == tb and (da == db or ta == 69 and da[1:] == db[1:] and (da[0] | 1) == db[0]):
            i += 1
            j += 1
        elif tb == 12 and extra < added:
            extra += 1
            j += 1
        else:
            sys.exit("check: tag %d (type %d) changed" % (i, ta))
    return True


def build(lab):
    os.makedirs(BUILD, exist_ok=True)
    os.makedirs(DIST, exist_ok=True)
    staged = []
    for m in MODULES:
        s = open(os.path.join(SRC, m), encoding="utf-8").read()
        if m == "net.as" and lab:
            old = "_global.TWN.LAB = false;"
            assert s.count(old) == 1
            s = s.replace(old, "_global.TWN.LAB = true;")
        p = os.path.join(BUILD, m)
        open(p, "w", encoding="utf-8").write(s)
        staged.append(p)
    out = os.path.join(DIST, "TerritoryWar_lab.swf" if lab else "TerritoryWar_online.swf")
    patched = os.path.join(BUILD, "patched.swf")
    r = subprocess.run(["java", "-cp", LIB, os.path.join(MOD, "tools", "InsertAction.java"), GAME, patched, str(FRAME)]
                       + staged, capture_output=True, text=True, errors="replace")
    log = r.stdout + r.stderr
    open(os.path.join(BUILD, "insert.log"), "w", encoding="utf-8").write(log)
    if r.returncode != 0 or "SEVERE" in log or "Exception" in log:
        print(log[-4000:])
        sys.exit("compile failed")
    set_use_network(patched)
    check(GAME, patched, len(MODULES))
    os.replace(patched, out)
    print("built", os.path.relpath(out, MOD), "(%d modules, game tags unchanged)" % len(MODULES))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--lab", action="store_true")
    build(ap.parse_args().lab)
