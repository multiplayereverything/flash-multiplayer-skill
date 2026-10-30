"""Self-test for the hub's tools. Each check also has a twin that must fail, so a broken check can't pass.

  python -I tools/test_all.py         prints ALL OK, or the failing checks and exits 1
  python -I tools/test_all.py --full  also runs the relay's 38-test suite (a few minutes)

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
import keys_check  # noqa: E402
import unmochi  # noqa: E402
import swfsym  # noqa: E402

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


def test_swfheader(tmp):
    data = tiny_swf()
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


def test_modsinfo():
    kit = os.path.join(os.path.dirname(HERE), "modsinfo")
    v = os.path.join(kit, "tools", "validate.py")
    r = subprocess.run([sys.executable, "-I", v, "--check"], capture_output=True, text=True, cwd=kit)
    ok("mods-info kit is valid and its index is current", r.returncode == 0)
    r = subprocess.run([sys.executable, "-I", v, "--test"], capture_output=True, text=True, cwd=kit)
    ok("mods-info validator's own tests pass", r.returncode == 0)


def test_relay_suite():
    t = os.path.join(os.path.dirname(HERE), "relay", "tests", "test_relay.py")
    r = subprocess.run([sys.executable, "-I", t], capture_output=True, text=True, timeout=900)
    last = (r.stdout.strip().splitlines() or [""])[-1]
    ok("relay test suite: " + last, r.returncode == 0)


def test_skills():
    root = os.path.dirname(HERE)
    names = sorted(os.listdir(os.path.join(root, ".claude", "skills")))
    for n in names:
        p = os.path.join(root, ".claude", "skills", n, "SKILL.md")
        text = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
        head = text.split("---")[1] if text.startswith("---") else ""
        ok("skill %s has name and description" % n, ("name: %s" % n) in head and "description:" in head)
        refs = [w for w in text.split("`") if w.startswith(("playbook/", "tools/", "templates/", "games/"))]
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
        chk = subprocess.run([sys.executable, "-I", os.path.join(HERE, "check_server.py"), "--game", "tw", "--server",
                              "127.0.0.1:%d" % port, "--mode", "star"], capture_output=True, text=True, timeout=60)
        ok("check_server passes against the relay", chk.returncode == 0 and "PASS room" in chk.stdout)
        bad = subprocess.run([sys.executable, "-I", os.path.join(HERE, "check_server.py"), "--game", "nope", "--server",
                              "127.0.0.1:%d" % port, "--mode", "star"], capture_output=True, text=True, timeout=60)
        ok("twin: check_server fails for an unknown game", bad.returncode != 0)
    finally:
        proc.kill()
        proc.wait()


def test_unmochi():
    inner = tiny_swf(10)
    key = bytes(range(32))
    payload = bytes(unmochi.rc4_payload(zlib.compress(inner) + key))
    def wrap(blob):
        body = bytes([0x50, 0, 0, 0, 0, 0]) + struct.pack("<HH", 30 << 8, 1)
        bd = struct.pack("<HI", 7, 0) + blob
        body += struct.pack("<HI", (87 << 6) | 0x3F, len(bd)) + bd
        sc = struct.pack("<HH", 1, 7) + b"mochicrypt.Payload" + bytes(1)
        body += struct.pack("<HI", (76 << 6) | 0x3F, len(sc)) + sc + struct.pack("<H", 0)
        return b"FWS" + bytes([10]) + struct.pack("<I", len(body) + 8) + body
    ok("unmochi recovers the inner SWF", unmochi.unwrap(wrap(payload)) == inner)
    broken = bytearray(payload)
    broken[-1] ^= 0xFF
    try:
        unmochi.unwrap(wrap(bytes(broken)))
        ok("twin: a wrong key is refused", False)
    except ValueError:
        ok("twin: a wrong key is refused", True)


def test_swfsym():
    sprite = struct.pack("<HH", 5, 1) + struct.pack("<H", 1 << 6) + struct.pack("<H", 0)
    body = bytes([0x50, 0, 0, 0, 0, 0]) + struct.pack("<HH", 30 << 8, 1)
    body += struct.pack("<HI", (39 << 6) | 0x3F, len(sprite)) + sprite + struct.pack("<H", 1 << 6) + struct.pack("<H", 0)
    swf = b"FWS" + bytes([10]) + struct.pack("<I", len(body) + 8) + body
    out = swfsym.link(swf, 5, "mod.Thing")
    tags = list(unmochi.tags(out[8:]))
    codes = [c for c, t in tags]
    ok("swfsym links a sprite right after its definition", codes[:2] == [39, 76] and b"mod.Thing" in tags[1][1]
       and struct.unpack("<HH", tags[1][1][:4]) == (1, 5))
    try:
        swfsym.link(swf, 6, "mod.Thing")
        ok("twin: an undefined sprite is refused", False)
    except ValueError:
        ok("twin: an undefined sprite is refused", True)


def test_keys_check():
    slots, local, shared = keys_check.parse("# two players\nslot 0: UP=38 FIRE=32\nslot 1: UP=87 FIRE=70\n"
                                            "local: UP=38,87 FIRE=32,70\n")
    ok("keys_check reads slots and local keys", len(slots) == 2 and slots[1]["FIRE"] == 70 and local["UP"] == [38, 87]
       and not shared)
    ok("keys_check reads a hot-seat map", keys_check.parse("shared\nslot 0: KEY1=49\n")[2])
    for bad, why in [("slot 1: UP=38\n", "slots out of order"), ("slot 0: JUMP=38\n", "an unknown button"),
                     ("slot 0: UP=999\n", "a key code Ruffle Together can't press"),
                     ("slot 0: UP=38,40\n", "two keys on one slot button"), ("local: UP=38\n", "no slots")]:
        try:
            keys_check.parse(bad)
            ok("twin: keys_check refuses " + why, False)
        except ValueError:
            ok("twin: keys_check refuses " + why, True)
    example = os.path.join(os.path.dirname(HERE), "templates", "ruffle-together", "example.keys")
    ok("the template key map parses", len(keys_check.parse(open(example, encoding="utf-8").read())[0]) == 2)


with tempfile.TemporaryDirectory() as tmp:
    test_swfheader(tmp)
    test_unmochi()
    test_swfsym()
    test_check_public(tmp)
    test_relay(tmp)
test_keys_check()
test_directory()
test_modsinfo()
test_skills()
if "--full" in sys.argv:
    test_relay_suite()
print()
print("ALL OK" if not failures else "%d FAILED: %s" % (len(failures), "; ".join(failures)))
sys.exit(1 if failures else 0)
