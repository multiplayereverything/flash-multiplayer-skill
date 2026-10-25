"""Builds Intrusion Online from the untouched ../intrusion.swf.

  python build.py          dist/intrusion_online.swf (release)
  python build.py --lab    dist/intrusion_lab.swf (runs the scripted lab, prints LAB| traces, ignores real input)

The game's own scripts are obfuscated and don't survive a decompile/recompile, so no game script is ever
recompiled. Instead:
  1. FFDec compiles each file of src/ (in SOURCES order) into a spare script slot of a scratch copy
     (the one-line stop() scripts of frames 6, 8, 10...), eight files per FFDec run.
  2. Those compiled DoAction tags are copied, unchanged, into the original SWF at the end of frame 5
     (the menu frame, after its own script). They run every time the menu is entered; the mod's
     boot code runs once (it checks _global.INTR).
  3. The FileAttributes UseNetwork flag is set, so Flash Player lets a local SWF open sockets.
"""
import argparse
import os
import shutil
import struct
import subprocess
import sys
import zlib

MOD = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.join(MOD, "..", "intrusion.swf")
FFDEC = os.environ.get("FFDEC", os.path.join(MOD, "..", "..", "tools", "ffdec", "ffdec-cli.jar"))
SRC = os.path.join(MOD, "src")
BUILD = os.path.join(MOD, "build")
DIST = os.path.join(MOD, "dist")

# load order: each file becomes one DoAction tag; keep each under 32 KB of bytecode (AS2 jumps are 16-bit)
SOURCES = ["core.as", "relay.as", "modinfo.as", "session.as", "world.as", "players.as", "coop.as", "levelsync.as", "vehicle.as", "life.as", "fx.as", "ui.as", "menu.as", "lab.as", "boot.as"]
SLOTS = [6, 8, 10, 12, 14, 16, 18, 20]  # main-timeline frames whose stop() script is the compile target
INSERT_FRAME = 5  # the "menu" frame
LAB_FLAG = ("N.LAB = false;", "N.LAB = true;")


def swf_read(path):
    data = open(path, "rb").read()
    if data[:3] == b"CWS":
        body = zlib.decompress(data[8:])
    elif data[:3] == b"FWS":
        body = data[8:]
    else:
        sys.exit("%s: not a SWF" % path)
    nbits = body[0] >> 3
    start = (5 + 4 * nbits + 7) // 8 + 4
    return data[3], body[:start], body[start:]


def tags(raw):
    """[(code, whole tag bytes)] of the main timeline."""
    out, pos = [], 0
    while pos < len(raw):
        cl = struct.unpack("<H", raw[pos:pos + 2])[0]
        code, ln, hdr = cl >> 6, cl & 0x3F, 2
        if ln == 0x3F:
            ln, hdr = struct.unpack("<I", raw[pos + 2:pos + 6])[0], 6
        out.append((code, raw[pos:pos + hdr + ln]))
        pos += hdr + ln
        if code == 0:
            break
    return out


def frame_doactions(tag_list):
    """{frame number: [DoAction tag bytes]}"""
    res, frame = {}, 1
    for code, t in tag_list:
        if code == 12:
            res.setdefault(frame, []).append(t)
        elif code == 1:
            frame += 1
    return res


def stage(batch, lab):
    dest = os.path.join(BUILD, "as")
    shutil.rmtree(dest, ignore_errors=True)
    for i, name in enumerate(batch):
        text = open(os.path.join(SRC, name), encoding="utf-8").read()
        if name == "core.as":
            assert text.count(LAB_FLAG[0]) == 1, "core.as must contain exactly one " + LAB_FLAG[0]
            if lab:
                text = text.replace(*LAB_FLAG)
        slot = os.path.join(dest, "frame_%d" % SLOTS[i])
        os.makedirs(slot)
        open(os.path.join(slot, "DoAction.as"), "w", encoding="utf-8").write(text)
    return dest


def compile_batch(batch, lab, original):
    scripts = stage(batch, lab)
    scratch = os.path.join(BUILD, "compiled.swf")
    if os.path.exists(scratch):
        os.remove(scratch)
    r = subprocess.run(["java", "-jar", FFDEC, "-importScript", GAME, scratch, scripts],
                       capture_output=True, text=True, errors="replace")
    log = r.stdout + r.stderr
    open(os.path.join(BUILD, "import.log"), "a", encoding="utf-8").write(log)
    if r.returncode != 0 or "SEVERE" in log or "rror" in log or not os.path.exists(scratch):
        print(log[-4000:])
        sys.exit("ffdec -importScript failed for %s (see build/import.log)" % ", ".join(batch))
    compiled = frame_doactions(tags(swf_read(scratch)[2]))
    out = []
    for i, name in enumerate(batch):
        got = compiled.get(SLOTS[i], [])
        if len(got) != 1 or got == original.get(SLOTS[i]):
            sys.exit("%s: no compiled script found in frame %d" % (name, SLOTS[i]))
        if len(got[0]) > 60000:
            print("warning: %s compiles to %d bytes" % (name, len(got[0])))
        out.append(got[0])
    return out


def sources(lab):
    """lab.as (the scripted tests) only goes into lab builds."""
    return [f for f in SOURCES if lab or f != "lab.as"]


def compile_sources(lab):
    """FFDec runs once per batch of len(SLOTS) files."""
    original = frame_doactions(tags(swf_read(GAME)[2]))
    open(os.path.join(BUILD, "import.log"), "w").close()
    files, out = sources(lab), []
    for i in range(0, len(files), len(SLOTS)):
        out += compile_batch(files[i:i + len(SLOTS)], lab, original)
    return out


def splice(new_tags):
    ver, header, raw = swf_read(GAME)
    tl = tags(raw)
    result, frame, inserted, net = [], 1, False, False
    for code, t in tl:
        if code == 69 and not net:  # FileAttributes: UseNetwork
            t = bytearray(t)
            t[2] |= 1
            t, net = bytes(t), True
        if code == 1 and frame == INSERT_FRAME:
            result.extend(new_tags)
            inserted = True
        result.append(t)
        if code == 1:
            frame += 1
    if not (inserted and net):
        sys.exit("splice failed (frame %d found: %s, FileAttributes found: %s)" % (INSERT_FRAME, inserted, net))
    body = header + b"".join(result)
    return b"CWS" + bytes([ver]) + struct.pack("<I", len(body) + 8) + zlib.compress(body, 9)


def build(lab):
    os.makedirs(BUILD, exist_ok=True)
    os.makedirs(DIST, exist_ok=True)
    new_tags = compile_sources(lab)
    out = os.path.join(DIST, "intrusion_lab.swf" if lab else "intrusion_online.swf")
    open(out, "wb").write(splice(new_tags))
    print("built %s (%s)" % (os.path.relpath(out, MOD), ", ".join("%s %d B" % (n, len(t)) for n, t in zip(sources(lab), new_tags))))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--lab", action="store_true")
    build(ap.parse_args().lab)
