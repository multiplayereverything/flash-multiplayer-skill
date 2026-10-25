"""Relay-side checks for the airbattle profile, against a local copy of the global relay (no Flash).

  python tools/relay_check.py           starts global-mods-server/init.py on 127.0.0.1:7804 (refuses a busy port)

Checks: a host gets a room code and shows in the public list; a friend with another version is refused;
three friends fit (4 players); a fifth player is refused; a wrong code is refused; guest -> host and
host -> guest messages pass in star mode; the host leaving sends X to the guests.
"""
import os
import socket
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RELAY = os.environ.get("MOD_RELAY", "init.py")  # path to the relay's init.py (global mod relay)
PORT = 7804
VERSION = "airbattle-1"


class Client:
    def __init__(self, line):
        self.s = socket.create_connection(("127.0.0.1", PORT), timeout=3)
        self.buf = b""
        self.s.sendall(line.encode() + b"\0")

    def recv(self, timeout=3.0):
        self.s.settimeout(timeout)
        while b"\0" not in self.buf:
            try:
                d = self.s.recv(65536)
            except socket.timeout:
                return None
            if not d:
                return None
            self.buf += d
        msg, self.buf = self.buf.split(b"\0", 1)
        return msg.decode()

    def until(self, prefix, timeout=3.0):
        end = time.time() + timeout
        while time.time() < end:
            m = self.recv(end - time.time())
            if m is None:
                return None
            if m.startswith(prefix):
                return m
        return None

    def send(self, msg):
        self.s.sendall(msg.encode() + b"\0")

    def close(self):
        self.s.close()


def main():
    probe = socket.socket()
    try:
        probe.bind(("127.0.0.1", PORT))
    except OSError:
        sys.exit("port %d is in use; stop whatever runs there first" % PORT)
    finally:
        probe.close()
    relay = subprocess.Popen([sys.executable, "-I", RELAY, "--port", str(PORT), "--bind", "127.0.0.1",
                              "--games", os.path.join(HERE, "lab_games.json"), "--no-mods-info"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    results = []

    def check(name, ok, evidence):
        results.append((name, ok, evidence))

    try:
        time.sleep(1.0)
        host = Client("RELAY|1|HOST|airbattle|%s|1|Hosty" % VERSION)
        room = host.until("ROOM|")
        code = room.split("|")[1] if room else ""
        check("host gets a room code", len(code) == 5 and room.endswith("|4"), room)
        lister = Client("RELAY|1|LIST|airbattle")
        rows = lister.recv() or ""
        lister.close()
        check("room is in the public list", code in rows, rows)
        bad = Client("RELAY|1|JOIN|airbattle|airbattle-0|%s|Old" % code)
        e = bad.recv()
        bad.close()
        check("another version is refused", e is not None and e.startswith("E|") and "ersion" in e, e)
        wrong = Client("RELAY|1|JOIN|airbattle|%s|QQQQQ|Lost" % VERSION)
        e = wrong.recv()
        wrong.close()
        check("a wrong code is refused", e is not None and e.startswith("E|"), e)
        guests = []
        for i in range(3):
            g = Client("RELAY|1|JOIN|airbattle|%s|%s|G%d" % (VERSION, code.lower(), i + 1))
            w = g.until("W|")
            guests.append((g, w))
        check("three friends fit (4 players)", all(w is not None for _, w in guests), ", ".join(str(w) for _, w in guests))
        fifth = Client("RELAY|1|JOIN|airbattle|%s|%s|Fifth" % (VERSION, code))
        e = fifth.recv()
        fifth.close()
        check("a fifth player is refused", e is not None and e.startswith("E|"), e)
        g1 = guests[0][0]
        g1.send("K|1|100|200|3")
        got = host.until("G|")
        check("guest -> host message", got is not None and got.endswith("|K|1|100|200|3"), got)
        host.send("RO|0:0:Hosty;1:1:G1")
        got = g1.until("RO|")
        check("host -> guest message", got == "RO|0:0:Hosty;1:1:G1", got)
        host.close()
        got = g1.until("X")
        check("host leaving tells the guests", got == "X", got)
        for g, _ in guests:
            g.close()
    finally:
        relay.terminate()
        try:
            relay.wait(5)
        except subprocess.TimeoutExpired:
            relay.kill()

    print("| Check | Result | Evidence |\n|---|---|---|")
    for name, ok, ev in results:
        print("| %s | %s | %s |" % (name, "PASS" if ok else "FAIL", ev))
    sys.exit(0 if all(ok for _, ok, _ in results) else 1)


if __name__ == "__main__":
    main()
