"""Stand-in for the Multiplayer Everything launcher's lobby bridge, for a lab run where every window is started
the way the launcher's lobby starts it (FlashVars lobby=1, room, role, slot, bridgePort, sessionToken, seed).
From Bad Ice-Cream Online.

  python -I fake_bridge.py --port 7796 --tokens <hex32>,<hex32>[,...] [--names Host,Guest] [--delay MS]

Every game connects to the same port and is told apart by its session token (slot = position in --tokens; the
real launcher gives each game its own port, a game can't tell the difference). As the launchers would together:
- answers a Flash <policy-file-request/> (then closes, like Flash expects);
- needs {"t":"hello","token":...} first (anything else, or a wrong token, closes the connection), answers welcome;
- keeps what arrives for a game that hasn't connected yet and hands it over after welcome;
- sends {"t":"go"} to everyone once every game said {"t":"loaded"};
- routes {"t":"send","to":-1|slot,"d":...} as {"t":"msg","from":slot,"d":...}, with an optional one-way delay;
- the host's game closes -> everyone else gets {"t":"end"}; another game closes -> the rest get {"t":"leave","slot":n};
- {"t":"log","text":"LAB drop <slot>"} from the host: the others get {"t":"drop","slot":n}, that slot's traffic is
  lost for --drop-ms, then {"t":"back","slot":n} (the launcher keeps a dropped slot for 30 seconds).
Prints "LAB| PASS|FAIL <check> | <evidence>" lines for the lab runner, and "BRIDGE ..." notes.
"""
import argparse
import json
import socket
import threading
import time

POLICY_REQUEST = b"<policy-file-request/>"
POLICY = (b'<?xml version="1.0"?><cross-domain-policy><allow-access-from domain="*" to-ports="*"/>'
          b"</cross-domain-policy>\0")

out_lock = threading.Lock()


def say(line):
    with out_lock:
        print(line, flush=True)


def check(what, ok, evidence):
    say("LAB| %s %s | %s" % ("PASS" if ok else "FAIL", what, evidence))


def who(slot):
    return "host" if slot == 0 else "player %d" % (slot + 1)


class Bridge:
    def __init__(self, tokens, names, room, delay_ms, drop_ms):
        self.n = len(tokens)
        self.tokens = {t: i for i, t in enumerate(tokens)}
        self.players = [{"slot": i, "name": names[i] if i < len(names) else "Player %d" % (i + 1)}
                        for i in range(self.n)]
        self.room, self.delay, self.drop_ms = room, delay_ms / 1000.0, drop_ms
        self.conn = {}
        self.pending = {i: [] for i in range(self.n)}
        self.loaded = set()
        self.go_sent = False
        self.dropped = {}         # slot -> until
        self.routed = 0
        self.cv = threading.Condition()
        self.outq = []            # (due, seq, slot, obj)
        self.seq = 0
        threading.Thread(target=self.sender, daemon=True).start()

    def to_game(self, slot, obj, delay=0.0):
        with self.cv:
            self.seq += 1
            self.outq.append((time.time() + delay, self.seq, slot, obj))
            self.outq.sort(key=lambda e: (e[0], e[1]))
            self.cv.notify()

    def sender(self):
        while True:
            with self.cv:
                while not self.outq or self.outq[0][0] > time.time():
                    self.cv.wait(0.005 if self.outq else 0.5)
                _, _, slot, obj = self.outq.pop(0)
                s = self.conn.get(slot)
                if s is None:
                    self.pending[slot].append(obj)
                    continue
            try:
                s.sendall(json.dumps(obj, separators=(",", ":")).encode("utf-8") + b"\0")
            except OSError:
                pass

    def serve(self, s):
        buf, policy_checked, slot = b"", False, None
        try:
            while True:
                data = s.recv(65536)
                if not data:
                    break
                buf += data
                if not policy_checked:
                    if len(buf) < len(POLICY_REQUEST) and POLICY_REQUEST.startswith(buf):
                        continue
                    policy_checked = True
                    if buf.startswith(POLICY_REQUEST):
                        say("BRIDGE policy request answered")
                        s.sendall(POLICY)
                        return
                while b"\0" in buf:
                    raw, buf = buf.split(b"\0", 1)
                    try:
                        m = json.loads(raw.decode("utf-8"))
                    except ValueError:
                        check("game messages are JSON", False, repr(raw[:80]))
                        continue
                    if slot is None:
                        slot = self.hello(s, m)
                        if slot is None:
                            return
                    else:
                        self.on_game(slot, m)
        except OSError:
            pass
        finally:
            s.close()
            if slot is not None:
                self.gone(slot)

    def hello(self, s, m):
        if not isinstance(m, dict) or m.get("t") != "hello":
            check("first message is hello", False, json.dumps(m)[:80])
            return None
        slot = self.tokens.get(m.get("token"))
        if slot is None:
            say("BRIDGE refused a hello with a wrong token")
            return None
        check("%s game says hello with its token" % who(slot), True, "slot %d" % slot)
        with self.cv:
            self.conn[slot] = s
            self.to_game(slot, {"t": "welcome", "slot": slot, "role": "host" if slot == 0 else "client",
                                "room": self.room, "seed": 12345, "name": self.players[slot]["name"],
                                "players": self.players})
            for obj in self.pending[slot]:
                self.to_game(slot, obj)
            self.pending[slot] = []
        return slot

    def on_game(self, slot, m):
        t = m.get("t") if isinstance(m, dict) else None
        if t == "loaded":
            if slot not in self.loaded:
                self.loaded.add(slot)
                check("%s game says loaded" % who(slot), not self.go_sent, "after welcome, before go")
            if len(self.loaded) == self.n and not self.go_sent:
                self.go_sent = True
                say("BRIDGE go")
                for i in range(self.n):
                    self.to_game(i, {"t": "go"})
        elif t == "send":
            to = m.get("to", -1)
            now = time.time()
            if self.dropped.get(slot, 0) > now:
                return
            for other in range(self.n):
                if other != slot and to in (-1, other) and self.dropped.get(other, 0) <= now:
                    self.routed += 1
                    self.to_game(other, {"t": "msg", "from": slot, "d": m.get("d")}, self.delay)
        elif t == "log":
            text = str(m.get("text", ""))
            if text.startswith("LAB drop") and slot == 0:
                parts = text.split()
                lost = int(parts[2]) if len(parts) > 2 else 1
                say("BRIDGE dropping %s for %d ms" % (who(lost), self.drop_ms))
                self.dropped[lost] = time.time() + self.drop_ms / 1000.0
                self.event("drop", lost)
                threading.Timer(self.drop_ms / 1000.0, lambda: self.event("back", lost)).start()
        elif t == "chat":
            say("BRIDGE chat %s: %s" % (who(slot), m.get("text")))
        else:
            check("game messages are known", False, "t=%r from %s" % (t, who(slot)))

    def event(self, kind, slot):
        for i in range(self.n):
            if i != slot:
                self.to_game(i, {"t": kind, "slot": slot, "name": self.players[slot]["name"]})

    def gone(self, slot):
        with self.cv:
            self.conn.pop(slot, None)
        say("BRIDGE %s game closed; %d messages routed" % (who(slot), self.routed))
        if slot == 0:
            for i in range(1, self.n):
                self.to_game(i, {"t": "end"})
        else:
            self.event("leave", slot)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--tokens", required=True, help="session tokens, host first, comma-separated")
    ap.add_argument("--names", default="Host,Guest")
    ap.add_argument("--room", default="LOBBY")
    ap.add_argument("--delay", type=int, default=0, help="one-way delay of game traffic in ms")
    ap.add_argument("--drop-ms", type=int, default=1500)
    a = ap.parse_args()
    b = Bridge(a.tokens.split(","), a.names.split(","), a.room, a.delay, a.drop_ms)
    ls = socket.socket()
    ls.bind(("127.0.0.1", a.port))
    ls.listen(16)
    say("BRIDGE listening on 127.0.0.1:%d, room %s, %d players" % (a.port, a.room, b.n))
    while True:
        s, _ = ls.accept()
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        threading.Thread(target=b.serve, args=(s,), daemon=True).start()


if __name__ == "__main__":
    main()
