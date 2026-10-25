"""Self-driving test lab for Territory War Online: lab builds in Ruffle desktop, a PASS/FAIL table at the end.
No OS input is sent: nothing touches the user's keyboard or mouse. Ruffle windows open small in the bottom-right
corner without taking focus; lab builds ignore real keys and swallow clicks.

  python tools/lab.py                   host + guest (2v2 sticks), through a local relay on 127.0.0.1:7801
  python tools/lab.py --players 3       + a third player who joins after turn 2 (late join, shares red's sticks)
  python tools/lab.py --solo            one window, vs CPU, no network: the mod must leave local play alone
  python tools/lab.py --host-leaves     the host closes the room mid-match
  python tools/lab.py --guest-leaves    the guest leaves mid-match: the CPU must take over its sticks
  python tools/lab.py --vs-cpu          the host starts a Player 1 vs CPU game: the guest watches it
  python tools/lab.py --wrong-code      a guest types a code that doesn't exist: must be refused with a reason
  python tools/lab.py --wrong-version   a guest with another version string: must be refused with a reason
  options: --no-build  --timeout 420  --delay MS --jitter MS (relay-simulated lag)  --turns N  --size N

The relay is global-mods-server's init.py with tools/lab_games.json; it refuses to start if 7801 is busy.
Every process is started here and killed by its PID at the end. Exit code 1 if a check failed, a window didn't
finish, the host's and guests' turn-start states differ, or Ruffle logged an AVM error.
"""
import argparse
import ctypes
import ctypes.wintypes as wt
import os
import re
import socket
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wincap  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
ANSI = re.compile("\x1b\\[[0-9;]*m")
RUFFLE = os.environ.get("RUFFLE", "C:\\Program Files\\ruffle\\bin\\ruffle.exe")
RELAY = os.environ.get("MOD_RELAY", "init.py")  # path to the relay's init.py (global mod relay)
LAB_PORT = 7801
SW_SHOWNOACTIVATE = 4


def pin_small(pid, index, count):
    """Small, always-on-top, tiled bottom-right, never activated (a covered Ruffle window stops rendering)."""
    user32 = ctypes.windll.user32
    found = []

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(hwnd, _):
        p = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(p))
        if p.value == pid and user32.IsWindowVisible(hwnd):
            found.append(hwnd)
        return True

    for _ in range(40):
        user32.EnumWindows(cb, 0)
        if found:
            break
        time.sleep(0.25)
    if not found:
        return
    sw, sh = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    w, h = 420, 360
    x = sw - (count - index) * w
    HWND_TOPMOST, SWP_NOACTIVATE, SWP_SHOWWINDOW = -1, 0x0010, 0x0040
    user32.SetWindowPos(found[0], HWND_TOPMOST, x, sh - 48 - h, w, h, SWP_NOACTIVATE | SWP_SHOWWINDOW)


def ruffle(swf, log, flashvars):
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = SW_SHOWNOACTIVATE
    env = dict(os.environ, RUST_LOG="warn,avm_trace=info")
    cmd = [RUFFLE, "--tcp-connections", "allow"] + ["-P%s=%s" % kv for kv in flashvars.items()] + [swf]
    return subprocess.Popen(cmd, stdout=open(log, "w"), stderr=subprocess.STDOUT, env=env, startupinfo=si)


def read(path):
    try:
        return ANSI.sub("", open(path, encoding="utf-8", errors="replace").read())
    except OSError:
        return ""


def avm_errors(text):
    return [l for l in text.splitlines() if re.search(r"\bERROR\b", l) and re.search(r"avm|actionscript", l, re.I)]


def port_busy(port):
    s = socket.socket()
    try:
        s.bind(("127.0.0.1", port))
        return False
    except OSError:
        return True
    finally:
        s.close()


def hashes(text):
    return {int(n): h for n, h in re.findall(r"LAB\| HASH (\d+) (\S+)", text)}


def shoot(clients, name, shots):
    for who, _, proc in clients:
        hwnd = wincap.find_window(proc.pid)
        if hwnd:
            w, h, data = wincap.capture(hwnd)
            if w:
                wincap.write_png(os.path.join(shots, "%s_%s.png" % (who, name)), w, h, data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", action="store_true")
    ap.add_argument("--players", type=int, default=2)
    ap.add_argument("--host-leaves", action="store_true")
    ap.add_argument("--guest-leaves", action="store_true")
    ap.add_argument("--vs-cpu", action="store_true")
    ap.add_argument("--wrong-code", action="store_true")
    ap.add_argument("--wrong-version", action="store_true")
    ap.add_argument("--no-build", action="store_true")
    ap.add_argument("--timeout", type=int, default=420)
    ap.add_argument("--delay", type=int, default=0)
    ap.add_argument("--jitter", type=int, default=0)
    ap.add_argument("--turns", type=int, default=0, help="turns before the scripted end (default 6, 10 with 3 players)")
    ap.add_argument("--size", type=int, default=2, help="sticks per team")
    a = ap.parse_args()

    swf = os.path.join(MOD, "dist", "TerritoryWar_lab.swf")
    if not a.no_build:
        subprocess.run([sys.executable, "-I", os.path.join(MOD, "build.py"), "--lab"], check=True)
    logs = os.path.join(MOD, "logs")
    shots = os.path.join(MOD, "shots")
    os.makedirs(logs, exist_ok=True)
    os.makedirs(shots, exist_ok=True)
    turns = a.turns or (10 if a.players >= 3 else 6)
    procs, clients = [], []
    taken = set()
    try:
        if a.solo:
            log = os.path.join(logs, "lab_solo.log")
            p = ruffle(swf, log, {"lab": "solo", "labsize": str(a.size), "labturns": "5"})
            procs.append(p)
            clients.append(("solo", log, p))
            pin_small(p.pid, 0, 1)
        else:
            if port_busy(LAB_PORT):
                sys.exit("port %d is in use; stop whatever runs there first" % LAB_PORT)
            relay_log = os.path.join(logs, "lab_relay.log")
            cmd = [sys.executable, "-I", RELAY, "--port", str(LAB_PORT), "--bind", "127.0.0.1", "--log",
                   "--games", os.path.join(HERE, "lab_games.json"), "--no-mods-info"]
            if a.delay:
                cmd += ["--sim-delay", str(a.delay)]
            if a.jitter:
                cmd += ["--sim-jitter", str(a.jitter)]
            procs.append(subprocess.Popen(cmd, stdout=open(relay_log, "w"), stderr=subprocess.STDOUT))
            for _ in range(60):  # wait until the relay accepts connections
                try:
                    socket.create_connection(("127.0.0.1", LAB_PORT), 0.5).close()
                    break
                except OSError:
                    time.sleep(0.25)
            else:
                sys.exit("the relay didn't start; see " + relay_log)
            relay = "127.0.0.1:%d" % LAB_PORT
            host_log = os.path.join(logs, "lab_host.log")
            fv = {"lab": "host", "relay": relay, "name": "Host", "labplayers": "2", "labsize": str(a.size),
                  "labturns": str(turns)}
            if a.host_leaves:
                fv["end"] = "hostleaves"
            if a.vs_cpu:
                fv["labtype"] = "2"
            hp = ruffle(swf, host_log, fv)
            procs.append(hp)
            clients.append(("host", host_log, hp))
            count = max(2, a.players)
            pin_small(hp.pid, 0, count)
            code, start = None, time.time()
            while code is None and time.time() - start < 90 and hp.poll() is None:
                time.sleep(0.5)
                m = re.search(r"LAB\| ROOM ([A-Z0-9]{5})", read(host_log))
                code = m.group(1) if m else None
            if code is None:
                print("host never opened a room")
            else:
                gfv = {"lab": "guest", "relay": relay, "join": code, "name": "Guest"}
                if a.host_leaves:
                    gfv["end"] = "hostleaves"
                if a.guest_leaves:
                    gfv["end"] = "guestleaves"
                if a.vs_cpu:
                    gfv["labtype"] = "2"
                if a.wrong_code:
                    gfv = {"lab": "guest", "relay": relay, "labjoin": "type", "labcode": "ZZZZZ", "name": "Guest",
                           "expect": "refused"}
                if a.wrong_version:
                    gfv.update({"labversion": "tw-0", "expect": "refused"})
                guest_log = os.path.join(logs, "lab_guest.log")
                gp = ruffle(swf, guest_log, gfv)
                procs.append(gp)
                clients.append(("guest", guest_log, gp))
                pin_small(gp.pid, 1, count)

        start = time.time()
        late_started = a.players < 3 or a.solo
        while time.time() - start < a.timeout:
            time.sleep(0.3)
            host_text = read(clients[0][1]) if clients else ""
            if not late_started and re.search(r"LAB\| TURN 2 ", host_text):
                late_log = os.path.join(logs, "lab_late.log")
                lp = ruffle(swf, late_log, {"lab": "guest", "relay": "127.0.0.1:%d" % LAB_PORT, "labjoin": "list",
                                            "labcode": code, "name": "Late"})
                procs.append(lp)
                clients.append(("late", late_log, lp))
                pin_small(lp.pid, 2, 3)
                late_started = True
            for n in re.findall(r"LAB\| TURN (\d+) ", host_text):
                if n in ("1", "3", "5", "8") and ("turn" + n) not in taken:
                    taken.add("turn" + n)
                    time.sleep(1.5 if n != "1" else 4.0)
                    shoot(clients, "turn" + n, shots)
            for name in re.findall(r"LAB\| SNAP (\w+)", host_text):
                if name not in taken:
                    taken.add(name)
                    time.sleep(1.0)
                    shoot(clients, name, shots)
            for who, log, proc in clients[1:]:
                for name in re.findall(r"LAB\| SNAP (\w+)", read(log)):
                    if (who, name) not in taken:
                        taken.add((who, name))
                        time.sleep(0.5)
                        shoot([(who, log, proc)], name, shots)
            for who, log, proc in clients:
                t = read(log)
                for key, pat in (("aim", r"LAB\| SCRIPT 0 "),
                                 ("menu", r"LAB\| (?:GUEST|HOST) MENU"), ("solo", r"LAB\| PASS solo-turns")):
                    if (who, key) not in taken and re.search(pat, t):
                        taken.add((who, key))
                        time.sleep(0.8 if key != "aim" else 2.5)
                        shoot([(who, log, proc)], key, shots)
            refused = a.wrong_code or a.wrong_version
            unfinished = [c for c in clients if "LAB DONE" not in read(c[1]) and not (refused and c[0] == "host")]
            if not unfinished and late_started:
                break
            if any(p.poll() is not None for p in procs):
                break
    finally:
        # game windows first, then the relay, so no window sees the relay vanish before it is closed
        for p in reversed(procs):
            subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)

    ok = bool(clients) and (a.solo or len(clients) == max(2, a.players))
    print("\n| Window | Check | Result | Evidence |\n|---|---|---|---|")
    notes = []
    texts = {who: read(log) for who, log, _ in clients}
    for who, log, _ in clients:
        text = texts[who]
        for l in text.splitlines():
            if ("LAB| PASS " in l or "LAB| FAIL " in l) and not ((a.wrong_code or a.wrong_version) and who == "host"):
                rest = l.split("LAB| ", 1)[1].strip()
                verdict, rest = rest.split(" ", 1)
                what, _, evidence = rest.partition(" | ")
                print("| %s | %s | %s | %s |" % (who, what, verdict, evidence))
                ok = ok and verdict == "PASS"
        avm = avm_errors(text)
        finished = "LAB DONE" in text or (a.wrong_code or a.wrong_version) and who == "host"
        ok = ok and finished and not avm
        notes.append("%s: %s, %d AVM errors, log %s" % (who, "finished" if finished else "did NOT finish", len(avm),
                                                        os.path.relpath(log, MOD)))
        for l in avm[:4]:
            notes.append("   " + l[:220])
    required = []
    if a.guest_leaves:
        required.append(("host", "cpu-takeover"))
    if a.wrong_code or a.wrong_version:
        required.append(("guest", "refused"))
    if a.players >= 3:
        required.append(("late", "room-list"))
    for who, what in required:
        if not re.search(r"LAB\| PASS %s " % what, texts.get(who, "")):
            print("| %s | %s | FAIL | missing |" % (who, what))
            ok = False
    if not a.solo and clients and not (a.wrong_code or a.wrong_version):
        host = hashes(texts["host"])
        for who in texts:
            if who == "host":
                continue
            g = hashes(texts[who])
            both = sorted(set(host) & set(g))
            bad = [n for n in both if host[n] != g[n]]
            verdict = "PASS" if both and not bad else "FAIL"
            if a.host_leaves and not both:
                verdict = "PASS"
            ok = ok and verdict == "PASS"
            ev = "%d turn starts compared (%s)" % (len(both), ",".join(map(str, both)))
            if bad:
                ev += "; differ at %s: host %s / %s %s" % (bad[0], host[bad[0]], who, g[bad[0]])
            print("| %s | same state as host at turn start | %s | %s |" % (who, verdict, ev))
    print()
    for n in notes:
        print(n)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
