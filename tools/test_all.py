"""Self-test for the hub's tools. Each check also has a twin that must fail, so a broken check can't pass.

  python -I tools/test_all.py        prints ALL OK, or the failing checks and exits 1

Needs only Python. It builds tiny SWF files in a temp folder; no game files are used.
"""
import copy
import json
import os
import struct
import subprocess
import sys
import tempfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_public  # noqa: E402
import directory  # noqa: E402
import set_use_network as sun  # noqa: E402

failures = []


def ok(name, cond):
    print(("PASS  " if cond else "FAIL  ") + name)
    if not cond:
        failures.append(name)


def tiny_swf(version=9, file_attributes=True):
    rect = bytes([0x50, 0x00, 0x00, 0x00, 0x00, 0x00])  # nbits=10: 5 + 4*10 bits, 6 bytes
    body = rect + struct.pack("<HH", 30 << 8, 1)
    if file_attributes:
        body += struct.pack("<H", (69 << 6) | 4) + bytes([0x08, 0, 0, 0])
    body += struct.pack("<H", 1 << 6)  # ShowFrame
    body += struct.pack("<H", 0)       # End
    return b"FWS" + bytes([version]) + struct.pack("<I", len(body) + 8) + body


def test_use_network(tmp):
    data = tiny_swf()
    out, found = sun.set_use_network(data)
    ok("set_use_network sets the flag on SWF 9", found and sun.has_use_network(out) and out[:3] == b"CWS")
    ok("twin: the untouched file has no flag", not sun.has_use_network(data))
    out6, found6 = sun.set_use_network(tiny_swf(6, False))
    ok("SWF 6 without FileAttributes is recompressed and reported", not found6 and out6[:3] == b"CWS")
    body = zlib.decompress(out[8:])
    ok("length field matches the body", struct.unpack("<I", out[4:8])[0] == len(body) + 8)
    p = os.path.join(tmp, "t.swf")
    open(p, "wb").write(data)
    r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "swfheader.py"), p], capture_output=True, text=True)
    ok("swfheader reads a tiny SWF", r.returncode == 0 and "SWF9" in r.stdout and "AS3=False" in r.stdout)


def test_check_public(tmp):
    clean = os.path.join(tmp, "clean.md")
    open(clean, "w").write("Relay relay.example.com:25600, local 127.0.0.1:7801, path C:\\Users\\<name>\\game\n")
    ok("check_public passes clean text", check_public.main([clean]) == 0)
    cases = {
        "a GitHub token": "token = ghp_" + "A" * 30,
        "a personal Windows path": "C:\\Users\\" + "somebody" + "\\Desktop\\x",
        "an email address": "mail me at someone" + "@gmail.com",
        "a home network IP": "server 192.168." + "1.20",
        "a VPN IP": "radmin 26.92." + "1.2",
        "a password": "password = \"" + "hunter22" + "\"",
        "a private key": "-----BEGIN RSA PRIVATE" + " KEY-----",
    }
    for what, line in cases.items():
        p = os.path.join(tmp, "bad.md")
        open(p, "w").write(line + "\n")
        ok("twin: check_public catches " + what, check_public.main([p]) == 1)
    swf = os.path.join(tmp, "game.swf")
    open(swf, "wb").write(tiny_swf())
    ok("twin: check_public refuses a SWF file", check_public.main([swf]) == 1)


def test_directory():
    d = directory.load()
    ok("data/games.json is valid", directory.check(d) == [])
    md = directory.render(d)
    ok("DIRECTORY.md renders every game", all(("`%s`" % g["id"]) in md for g in d["games"]))
    for what, change in {
        "a duplicate id": lambda x: x["games"].append(copy.deepcopy(x["games"][0])),
        "an unknown status": lambda x: x["games"][0].update(status="done"),
        "a released entry without a link": lambda x: x["games"][0].update(release=None),
        "a missing write-up": lambda x: x["games"][0].update(writeup="games/nope.md"),
    }.items():
        bad = copy.deepcopy(d)
        change(bad)
        ok("twin: directory check catches " + what, directory.check(bad) != [])
    current = open(directory.OUT, encoding="utf-8").read() if os.path.exists(directory.OUT) else ""
    ok("DIRECTORY.md is up to date (run tools/directory.py render)", current == md)


def test_skills():
    root = os.path.dirname(HERE)
    names = sorted(os.listdir(os.path.join(root, "skills")))
    for n in names:
        p = os.path.join(root, "skills", n, "SKILL.md")
        text = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
        head = text.split("---")[1] if text.startswith("---") else ""
        ok("skill %s has name and description" % n, ("name: %s" % n) in head and "description:" in head)
        refs = [w for w in text.split("`") if w.startswith(("references/", "tools/", "templates/", "games/"))]
        for ref in [r for r in refs if "<" not in r]:
            ok("skill %s: %s exists" % (n, ref), os.path.exists(os.path.join(root, ref.split(" ")[0])))


def test_relay(tmp):
    import socket
    import time
    root = os.path.dirname(HERE)
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    games = os.path.join(tmp, "games.json")
    open(games, "w").write(open(os.path.join(root, "relay", "games.example.json")).read())
    proc = subprocess.Popen([sys.executable, "-I", os.path.join(root, "relay", "init.py"), "--port", str(port),
                             "--bind", "127.0.0.1", "--games", games, "--no-mods-info"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def ask(line):
        for _ in range(50):
            try:
                with socket.create_connection(("127.0.0.1", port), 2) as c:
                    c.sendall(line + b"\0")
                    time.sleep(0.2)
                    return c.recv(256)
            except OSError:
                time.sleep(0.1)
        return b""
    try:
        ok("relay lists rooms for a known game", ask(b"RELAY|1|LIST|tw").startswith(b"LIST|"))
        ok("twin: relay refuses an unknown game", ask(b"RELAY|1|LIST|nope").startswith(b"E|"))
        ok("relay gives a host a room code", ask(b"RELAY|1|HOST|bowman|1|1|test").startswith(b"ROOM|"))
    finally:
        proc.kill()
        proc.wait()


with tempfile.TemporaryDirectory() as tmp:
    test_use_network(tmp)
    test_check_public(tmp)
    test_relay(tmp)
test_directory()
test_skills()
print()
print("ALL OK" if not failures else "%d FAILED: %s" % (len(failures), "; ".join(failures)))
sys.exit(1 if failures else 0)
