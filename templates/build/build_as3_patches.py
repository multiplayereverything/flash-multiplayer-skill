"""Builds the co-op SWF for Ruffle Together from the untouched ../Game.swf (taken from the Intrusion 2 mod).

  python build.py    dist/Game_coop.swf

Steps: the game classes listed in patches.py are copied from ../decompiled/scripts/scripts/ and edited
(patches.py asserts every match), src/ (the mod's new classes, package mycoop) is staged next to them,
tools/AddClasses.java adds empty stubs for the new classes, ffdec -importScript compiles
every staged class into the SWF, and tools/CheckNamespaces.java refuses a build that would break a game
subclass.
"""
import os
import re
import shutil
import subprocess
import sys

MOD = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, MOD)
import patches  # noqa: E402

GAME = os.path.join(MOD, "..", "Game.swf")
OUT_NAME = "Game_coop.swf"
PACKAGE = "mycoop"
DECOMPILED = os.path.join(MOD, "..", "decompiled", "scripts", "scripts")
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


def stage():
    dest = os.path.join(BUILD, "as")
    if os.path.exists(dest):
        shutil.rmtree(dest)
    # The game has classes whose names differ only in case (Snowball and the symbol class snowball,
    # Spherobot/spherobot, Mine/mine). In a normal Windows folder ffdec -importScript finds Snowball.as for
    # the symbol class too and replaces it, so the staging folder is made case-sensitive (no admin needed;
    # folders created inside it inherit the flag).
    os.makedirs(dest)
    r = subprocess.run(["fsutil.exe", "file", "setCaseSensitiveInfo", dest, "enable"], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("can't make %s case-sensitive: %s" % (dest, (r.stdout + r.stderr).strip()))
    shutil.copytree(SRC, dest, dirs_exist_ok=True)
    for name in patches.files():
        src = os.path.join(DECOMPILED, name)
        text = patches.apply(name, open(src, encoding="utf-8").read())
        out = os.path.join(dest, name)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8", newline="\n").write(text)
    return dest


def new_classes():
    names = []
    for d, _, fs in os.walk(os.path.join(SRC, PACKAGE)):
        for f in fs:
            if f.endswith(".as"):
                rel = os.path.relpath(os.path.join(d, f), SRC)
                names.append(rel[:-3].replace("\\", ".").replace("/", "."))
    return sorted(names)


def build():
    os.makedirs(BUILD, exist_ok=True)
    os.makedirs(DIST, exist_ok=True)
    scripts = stage()
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
    out = os.path.join(DIST, OUT_NAME)
    shutil.copyfile(patched, out)
    print("built", os.path.relpath(out, MOD))
    return out


if __name__ == "__main__":
    build()
