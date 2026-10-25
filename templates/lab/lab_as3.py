"""Scripted test lab: runs lab builds in Ruffle desktop and prints a PASS/FAIL table.
No OS input is sent; nothing touches the user's keyboard or mouse. Ruffle windows open small in
the bottom-right corner without taking focus, and lab builds ignore real keys and clicks.

  python tools/lab.py                  online: local relay + host + guest + a guest that joins mid-level
  python tools/lab.py --guests 1       host + one guest
  python tools/lab.py --solo           one window, no network: single player must work as before
  python tools/lab.py --host-leaves    the host closes the room at the end; guests must drop to the menu
  (a fourth window tries the wrong room code ZZZZZ and must be refused; --no-bad-code skips it)
  options: --no-build  --timeout 400  --delay MS --jitter MS (relay-simulated latency)  --level N

Online: starts the global relay (global-mods-server/init.py) on 127.0.0.1:7804 with the lab's
game profile (tools/lab_games.json), starts the host, reads "LAB| ROOM <code>" from its log, starts
guest 1 with join=<code> (the way the Flash launcher joins a room), and guest 2 once the host logs
"LAB| LATE" (its level is running). Waits for "LAB DONE" in every log, then kills every process it
started, by PID. Exit code 1 if a check failed, a window didn't finish, or Ruffle logged an AVM error.
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
ANSI = re.compile("\x1b\\[[0-9;]*m")  # Ruffle colours its log
RUFFLE = os.environ.get("RUFFLE", "C:\\Program Files\\ruffle\\bin\\ruffle.exe")
RELAY = os.environ.get("MOD_RELAY", "init.py")  # path to the relay's init.py (global mod relay)
LAB_PORT = 7804  # this mod's lab port; the other mods' labs use 7792-7803
SW_SHOWNOACTIVATE = 4


def pin_small(pid, index, count):
    """Small, always-on-top, tiled bottom-right, never activated: a fully covered
    Ruffle window stops rendering and then stops running frames."""
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
    w, h = 400, 340
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


# Errors of the original game under Ruffle, matched by their whole first line. None known yet.
KNOWN_GAME_ERRORS = []


def avm_errors(text):
    """AVM error entries (first line + stack), minus known game errors; returns (errors, known count)."""
    entries = re.findall(r"^\S+\s+ERROR\S*\s+\S*avm2[^\n]*\n(?:\s+at [^\n]*\n)*", text + "\n", re.M)
    known = [e for e in entries if any(k.search(e) for k in KNOWN_GAME_ERRORS)]
    return [e.splitlines()[0] for e in entries if e not in known], len(known)


def port_busy(port):
    s = socket.socket()
    try:
        s.bind(("127.0.0.1", port))
        return False
    except OSError:
        return True
    finally:
        s.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo", action="store_true")
    ap.add_argument("--guests", type=int, default=2, choices=[1, 2])
    ap.add_argument("--no-build", action="store_true")
    ap.add_argument("--timeout", type=int, default=400)
    ap.add_argument("--level", type=int, default=10)
    ap.add_argument("--delay", type=int, default=0, help="relay: one-way delay in ms")
    ap.add_argument("--jitter", type=int, default=0, help="relay: random extra delay 0..N ms")
    ap.add_argument("--host-leaves", action="store_true", help="online: the host closes the room at the end")
    ap.add_argument("--no-bad-code", action="store_true", help="online: skip the window that tries a wrong room code")
    a = ap.parse_args()

    swf = os.path.join(MOD, "dist", "AirBattle_lab.swf")
    if not a.no_build:
        subprocess.run([sys.executable, "-I", os.path.join(MOD, "build.py"), "--lab"], check=True)

    logs = os.path.join(MOD, "logs")
    shots = os.path.join(MOD, "shots")
    os.makedirs(logs, exist_ok=True)
    os.makedirs(shots, exist_ok=True)
    procs, clients = [], []
    common = {"level": str(a.level)}
    if a.host_leaves:
        common["end"] = "hostleaves"
    expected = 1 if a.solo else 1 + a.guests + (0 if a.no_bad_code else 1)
    try:
        if a.solo:
            log = os.path.join(logs, "lab_solo.log")
            p = ruffle(swf, log, dict(common, lab="solo", relay="127.0.0.1:%d" % LAB_PORT))
            procs.append(p)
            clients.append(("solo", log, p))
            pin_small(p.pid, 0, 1)
        else:
            if port_busy(LAB_PORT):
                sys.exit("port %d is in use; stop whatever runs there first" % LAB_PORT)
            relay_log = os.path.join(logs, "lab_relay.log")
            cmd = [sys.executable, "-I", RELAY, "--port", str(LAB_PORT), "--bind", "127.0.0.1",
                   "--games", os.path.join(HERE, "lab_games.json"), "--no-mods-info"]
            if a.delay:
                cmd += ["--sim-delay", str(a.delay)]
            if a.jitter:
                cmd += ["--sim-jitter", str(a.jitter)]
            procs.append(subprocess.Popen(cmd, stdout=open(relay_log, "w"), stderr=subprocess.STDOUT))
            time.sleep(1.0)
            relay = "127.0.0.1:%d" % LAB_PORT
            host_log = os.path.join(logs, "lab_host.log")
            hp = ruffle(swf, host_log, dict(common, lab="host", relay=relay, name="Hosty"))
            procs.append(hp)
            clients.append(("host", host_log, hp))
            pin_small(hp.pid, 0, expected)
            code, start = None, time.time()
            while code is None and time.time() - start < 90 and hp.poll() is None:
                time.sleep(0.5)
                m = re.search(r"LAB\| ROOM ([A-Z0-9]{5})", read(host_log))
                code = m.group(1) if m else None
            if code is None:
                print("host never opened a room")
            else:
                g1_log = os.path.join(logs, "lab_guest1.log")
                gp = ruffle(swf, g1_log, dict(common, lab="guest", relay=relay, join=code, name="Gus", vialist="1", labList="1"))
                procs.append(gp)
                clients.append(("guest1", g1_log, gp))
                pin_small(gp.pid, 1, expected)
                if not a.no_bad_code:
                    b_log = os.path.join(logs, "lab_badcode.log")
                    bp = ruffle(swf, b_log, dict(common, lab="guest", relay=relay, join="ZZZZZ", badcode="1", name="Wrong"))
                    procs.append(bp)
                    clients.append(("badcode", b_log, bp))
                    pin_small(bp.pid, expected - 1, expected)

        start, unfinished = time.time(), list(clients)
        taken = set()
        late_started = a.solo or a.guests < 2
        while unfinished and time.time() - start < a.timeout:
            time.sleep(0.3)
            if not late_started and "LAB| LATE" in read(clients[0][1]):
                late_started = True
                g2_log = os.path.join(logs, "lab_guest2.log")
                lp = ruffle(swf, g2_log, dict(common, lab="guest", relay=relay, join=code, name="Lata", late="1"))
                procs.append(lp)
                clients.append(("guest2", g2_log, lp))
                pin_small(lp.pid, 2, expected)
            for who, log, proc in clients:
                for name in re.findall(r"LAB\| SNAP (\w+)", read(log)):
                    if (who, name) not in taken:
                        taken.add((who, name))
                        hwnd = wincap.find_window(proc.pid)
                        w = 0
                        if hwnd and ctypes.windll.user32.IsIconic(hwnd):
                            # our own window got minimized: show it again, still without activating it
                            ctypes.windll.user32.ShowWindow(hwnd, SW_SHOWNOACTIVATE)
                            time.sleep(0.4)
                        if hwnd:
                            w, h, data = wincap.capture(hwnd)
                            if w:
                                wincap.write_png(os.path.join(shots, "%s_%s.png" % (who, name)), w, h, data)
                        if not w:
                            print("no screenshot for %s %s (window %s)" % (who, name, hwnd))
            unfinished = [c for c in clients if "LAB DONE" not in read(c[1])]
            if any(p.poll() is not None for p in procs):
                break
    finally:
        for p in procs:
            subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)

    ok = len(clients) == expected
    print("\n| Window | Check | Result | Evidence |\n|---|---|---|---|")
    notes = []
    for who, log, _ in clients:
        text = read(log)
        lab = [l.split("LAB| ", 1)[1].strip() for l in text.splitlines() if "LAB| " in l]
        for l in lab:
            if l.startswith(("PASS ", "FAIL ")):
                verdict, rest = l.split(" ", 1)
                what, _, evidence = rest.partition(" | ")
                print("| %s | %s | %s | %s |" % (who, what, verdict, evidence))
                ok = ok and verdict == "PASS"
        avm, known = avm_errors(text)
        finished = "LAB DONE" in text
        ok = ok and finished and not avm
        notes.append("%s: %s, %d AVM errors (+%d known game errors), log %s" % (
            who, "finished" if finished else "did NOT finish", len(avm), known, os.path.relpath(log, MOD)))
        for l in avm[:4]:
            notes.append("   " + l[:220])
    print()
    for n in notes:
        print(n)
    print("RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
