"""Builds the co-op SWF for Ruffle Together from the untouched ../Game.swf (taken from the Bad Ice-Cream mod).

  python build.py    dist/Game_coop.swf

Steps: src/ is staged to build/as, tools/AddClasses.java adds empty stubs for the mod's new classes (package
`mycoop`), ffdec -importScript compiles every staged class into the SWF (game classes in src/ replace the game's
own), and tools/CheckNamespaces.java refuses a build that would break a game subclass.
"""
import os
import re
import shutil
import subprocess
import sys

MOD = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.join(MOD, "..", "Game.swf")
OUT_NAME = "Game_coop.swf"
PACKAGE = "mycoop"
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
    shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(SRC, dest)
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
