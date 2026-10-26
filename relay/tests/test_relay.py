"""Relay tests with fake clients. Starts relay.py on free local ports (never
7777/7778/27015/27020) and prints a PASS/FAIL table.

  python tests/test_relay.py [-k name]
Exit code 1 if any check fails.
"""
import json
import os
import random
import re
import socket
import struct
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RELAY = os.path.join(os.path.dirname(HERE), "init.py")   # the entry point (relay.py still launches it)
TEST_GAMES = os.path.join(HERE, "test_games.json")
RESERVED = {7777, 7778, 7779, 27015, 27016, 27020, 27021}
results = []
CODE_RE = re.compile(r"^[ABCDEFGHJKLMNPQRSTUVWXYZ23456789]{5}$")


def free_port():
    while True:
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        if port not in RESERVED:
            return port


class Server:
    def __init__(self, *args, env=None, port=None):
        self.port = port or free_port()
        cmd = [sys.executable, "-u", RELAY] + (["--port", str(self.port)] if port is None else [])
        cmd += list(args)
        if "--games" not in args:
            cmd += ["--games", TEST_GAMES]  # the relay has no built-in games; these stand in for real ones
        if "--mods-info" not in args:
            cmd.append("--no-mods-info")
        self.log_path = os.path.join(HERE, "logs", "relay_%d.log" % self.port)
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        self.proc = subprocess.Popen(cmd, stdout=open(self.log_path, "w"), stderr=subprocess.STDOUT,
                                     env=dict(os.environ, **(env or {})))
        for _ in range(100):
            try:
                socket.create_connection(("127.0.0.1", self.port), 0.2).close()
                break
            except OSError:
                time.sleep(0.05)
                if self.proc.poll() is not None:
                    break

    def log(self):
        return open(self.log_path, encoding="utf-8", errors="replace").read()

    def stop(self):
        self.proc.kill()
        self.proc.wait()


class Client:
    """A fake game client. sep: b"\\0" (Flash) or b"\\n" (C# tunnel control)."""

    def __init__(self, port, sep=b"\0"):
        self.sock = socket.create_connection(("127.0.0.1", port), 3)
        self.sock.settimeout(3)
        self.sep = sep
        self.buf = b""

    def send(self, text):
        self.sock.sendall(text.encode() + self.sep)

    def recv(self, timeout=3):
        """Next message, or None if the connection closed. Raises on timeout."""
        self.sock.settimeout(timeout)
        while self.sep not in self.buf:
            data = self.sock.recv(65536)
            if not data:
                return None
            self.buf += data
        msg, self.buf = self.buf.split(self.sep, 1)
        return msg.decode()

    def expect(self, prefix, timeout=3):
        msg = self.recv(timeout)
        if msg is None or not msg.startswith(prefix):
            raise AssertionError("expected %r, got %r" % (prefix, msg))
        return msg

    def silent(self, wait=0.4):
        """True if nothing arrives within wait seconds (connection still open)."""
        try:
            msg = self.recv(wait)
            return False if msg is not None else False
        except socket.timeout:
            return True

    def closed(self, timeout=3):
        try:
            while True:
                msg = self.recv(timeout)
                if msg is None:
                    return True
        except (socket.timeout, ConnectionError):
            return False

    def close(self):
        self.sock.close()


def host(port, game="sh2", public=1, name="Host", version="v1"):
    c = Client(port)
    c.send("RELAY|1|HOST|%s|%s|%d|%s" % (game, version, public, name))
    room = c.expect("ROOM|").split("|")
    c.expect("W|0")
    return c, room[1], int(room[2])


def join(port, code, game="sh2", name="Guest", version="v1"):
    c = Client(port)
    c.send("RELAY|1|JOIN|%s|%s|%s|%s" % (game, version, code, name))
    return c


def check(name, fn):
    if FILTER and FILTER not in name:
        return
    t = time.time()
    try:
        detail = fn() or ""
        results.append((name, True, detail))
    except Exception as ex:
        results.append((name, False, "%s: %s" % (type(ex).__name__, ex)))
    print("%s %s (%.1f s)" % ("PASS" if results[-1][1] else "FAIL", name, time.time() - t), flush=True)


# ---------------------------------------------------------------- star

def t_policy(s):
    c = socket.create_connection(("127.0.0.1", s.port), 3)
    c.sendall(b"<policy-file-request/>\0")
    data = b""
    while True:
        d = c.recv(4096)
        if not d:
            break
        data += d
    assert data.startswith(b'<?xml') and b'allow-access-from domain="*"' in data and data.endswith(b"\0"), data
    return "policy XML + NUL, then closed"


def t_unknown_game(s):
    c = Client(s.port)
    c.send("RELAY|1|HOST|nosuchgame|v1|1|x")
    msg = c.expect("E|")
    assert "Unknown game" in msg and c.closed()
    return msg


def t_two_rooms(s):
    h1, code1, mx = host(s.port, "sh2", name="SH2 host")
    h2, code2, _ = host(s.port, "gm2", name="GM2 host")
    assert CODE_RE.match(code1) and CODE_RE.match(code2) and code1 != code2, (code1, code2)
    assert mx == 4
    g1 = join(s.port, code1, "sh2", "alice")
    assert g1.expect("W|") == "W|1"
    assert h1.expect("J|") == "J|1|alice"
    g2 = join(s.port, code2, "gm2", "bob")
    assert g2.expect("W|") == "W|1"
    assert h2.expect("J|") == "J|1|bob"
    g1.send("k|37|1")
    assert h1.expect("G|") == "G|1|k|37|1"
    g2.send("I|5|9")
    assert h2.expect("G|") == "G|1|I|5|9"
    h1.send("P|1|snapshot-sh2")
    assert g1.expect("P|") == "P|1|snapshot-sh2"
    h2.send("F|7|keys-gm2")
    assert g2.expect("F|") == "F|7|keys-gm2"
    assert h1.silent() and h2.silent() and g1.silent() and g2.silent(), "crosstalk"
    for c in (h1, h2, g1, g2):
        c.close()
    return "codes %s/%s; G|id| tagging, broadcast and no crosstalk" % (code1, code2)


def t_spoofed_id(s):
    h, code, _ = host(s.port)
    g = join(s.port, code)
    g.expect("W|1")
    h.expect("J|1|")
    g.send("G|3|RD|1")  # pretending to be guest 3
    got = h.expect("G|")
    assert got == "G|1|G|3|RD|1", got
    h.close(); g.close()
    return got


def t_wrong_code(s):
    h, code, _ = host(s.port)
    bad = "ZZZZZ" if code != "ZZZZZ" else "YYYYY"
    g = join(s.port, bad)
    m1 = g.expect("E|")
    assert "No room" in m1 and g.closed()
    g = join(s.port, code, game="gm2")
    m2 = g.expect("E|")
    assert "another game" in m2
    g = join(s.port, code, version="v2")
    m3 = g.expect("E|")
    assert "Version mismatch" in m3
    g = join(s.port, code.lower())  # codes are case-insensitive
    g.expect("W|1")
    h.close(); g.close()
    return "%s / %s / %s; lower-case code joins" % (m1, m2, m3)


def t_full_room(s):
    h, code, mx = host(s.port)
    guests = []
    for i in range(mx - 1):
        g = join(s.port, code, name="g%d" % i)
        g.expect("W|")
        guests.append(g)
    extra = join(s.port, code, name="extra")
    msg = extra.expect("E|")
    assert "full" in msg and extra.closed()
    for c in guests + [h]:
        c.close()
    return "%d players in, 5th: %s" % (mx, msg)


def t_host_leaves(s):
    h, code, _ = host(s.port)
    g1 = join(s.port, code); g1.expect("W|")
    g2 = join(s.port, code); g2.expect("W|")
    h.close()
    assert g1.expect("X") == "X" and g2.expect("X") == "X"
    assert g1.closed() and g2.closed()
    g3 = join(s.port, code)
    msg = g3.expect("E|")
    assert "No room" in msg
    return "guests got X and were closed; code is gone"


def t_guest_leaves(s):
    h, code, _ = host(s.port)
    g1 = join(s.port, code); g1.expect("W|1"); h.expect("J|1")
    g2 = join(s.port, code); g2.expect("W|2"); h.expect("J|2")
    g1.close()
    assert h.expect("L|") == "L|1"
    g2.send("hello")
    assert h.expect("G|") == "G|2|hello"
    h.close(); g2.close()
    return "host got L|1; guest 2 unaffected"


def t_rooms_per_ip(s):
    time.sleep(0.3)  # rooms of earlier checks finish closing
    hosts = [host(s.port, name="h%d" % i)[0] for i in range(4)]
    c = Client(s.port)
    c.send("RELAY|1|HOST|sh2|v1|0|fifth")
    msg = c.expect("E|")
    assert "Too many rooms" in msg
    for h in hosts:
        h.close()
    time.sleep(0.3)
    h, code, _ = host(s.port, name="after")
    h.close()
    return "4 rooms ok, 5th: " + msg


def t_list(s):
    pub, code_pub, _ = host(s.port, "sh2", public=1, name="Fun Room")
    priv, code_priv, _ = host(s.port, "sh2", public=0, name="Secret")
    other, code_other, _ = host(s.port, "gm2", public=1, name="Other game")
    g = join(s.port, code_pub); g.expect("W|")
    c = Client(s.port)
    c.send("RELAY|1|LIST|sh2")
    msg = c.expect("LIST|")
    assert c.closed()
    rows = [r.split(",") for r in msg[5:].split(";") if r]
    codes = [r[0] for r in rows]
    assert code_pub in codes and code_priv not in codes and code_other not in codes, msg
    row = rows[codes.index(code_pub)]
    assert row[1:] == ["2", "4", "Fun Room"], row
    for x in (pub, priv, other, g):
        x.close()
    return msg


def t_legacy(s):
    g = Client(s.port)
    g.send("J|early")  # old relay: a friend may connect before the host
    g.expect("W|1")
    h = Client(s.port)
    h.send("H|oldhost")
    h.expect("W|0")
    assert h.expect("J|") == "J|1|early"
    g.send("RD|1")
    assert h.expect("G|") == "G|1|RD|1"
    h.send("PL|stuff")
    assert g.expect("PL|") == "PL|stuff"
    h2 = Client(s.port)
    h2.send("H|second")
    assert "already" in h2.expect("E|")
    h.close()
    assert g.expect("X") == "X"
    assert g.silent(), "legacy guests stay connected after X, like the old relay"
    g.close(); h2.close()
    return "H|/J| without a room behave like sh2_relay.py"


def t_handshake_timeout(s):
    c = Client(s.port)
    t = time.time()
    assert c.closed(timeout=5)
    took = time.time() - t
    assert took < 4, took
    return "silent client closed after %.1f s (limit 1.5 s in this run)" % took


def t_rate_limit(s):
    h, code, _ = host(s.port)
    g = join(s.port, code); g.expect("W|"); h.expect("J|")
    n = 300
    t = time.time()
    g.sock.sendall(b"".join(b"m%d\0" % i for i in range(n)))
    got = [h.expect("G|1|m", timeout=10) for _ in range(n)]
    took = time.time() - t
    assert got[-1] == "G|1|m%d" % (n - 1), "order or loss"
    assert took > (n - 20) / 100 * 0.8, "not throttled: %.2f s" % took
    h.close(); g.close()
    return "%d messages at 100/s limit took %.2f s, none lost, order kept" % (n, took)


def t_too_large(s):
    h, code, _ = host(s.port)
    g = join(s.port, code); g.expect("W|")
    try:
        g.sock.sendall(b"x" * 300000)
    except OSError:
        pass
    msg = g.expect("E|")
    assert "too large" in msg and g.closed()
    h.close()
    return msg


def t_idle(s):
    h, code, _ = host(s.port)
    g = join(s.port, code); g.expect("W|")
    t = time.time()
    assert g.expect("X", timeout=8) == "X"
    took = time.time() - t
    assert "idle" in s.log()
    h.close()
    return "quiet room closed after %.1f s (idle 2 s, checked every 2 s)" % took


def t_join_fails(s):
    h, code, _ = host(s.port)
    for i in range(5):
        g = join(s.port, "WRONG"[: 4] + "Z")
        g.expect("E|No room")
    g = join(s.port, code)
    msg = g.expect("E|")
    assert "Too many wrong" in msg
    h.close()
    return "after 5 wrong codes even the right one waits: " + msg


def t_server_port_env():
    port = free_port()
    s = Server(env={"SERVER_PORT": str(port)}, port=port)
    try:
        h, code, _ = host(port)
        h.close()
        assert "listening on 0.0.0.0:%d" % port in s.log()
        return "no arguments, SERVER_PORT=%d: listening there, room %s" % (port, code)
    finally:
        s.stop()


def t_busy_port():
    with socket.socket() as blocker:
        blocker.bind(("127.0.0.1", 0))
        blocker.listen(1)
        port = blocker.getsockname()[1]
        p = subprocess.run([sys.executable, RELAY, "--port", str(port)], capture_output=True, text=True, timeout=10)
        assert p.returncode != 0 and "already in use" in (p.stderr + p.stdout), (p.returncode, p.stderr)
        return "exit %d: %s" % (p.returncode, (p.stderr + p.stdout).strip().splitlines()[-1])


def t_games_json():
    import json
    import tempfile
    d = tempfile.mkdtemp()
    path = os.path.join(d, "games.json")
    games = json.load(open(TEST_GAMES))
    games["newgame"] = {"name": "New Game", "mode": "star", "max_players": 2}
    json.dump(games, open(path, "w"))
    s = Server("--games", path)
    try:
        h, code, mx = host(s.port, "newgame")
        g = join(s.port, code, "newgame"); g.expect("W|1")
        g2 = join(s.port, code, "newgame")
        assert "full" in g2.expect("E|")
        h2, _, _ = host(s.port, "sh2")  # the other games in the file are there too
        for c in (h, g, h2):
            c.close()
        return "games.json added 'newgame' (max 2 players) next to the other games"
    finally:
        s.stop()


# ---------------------------------------------------------------- tunnel

class TunnelHost:
    """Fake tunnel host: control connection plus one data connection per friend.
    Each data connection runs an echo-with-transform: bytes b -> (b + 1) % 256,
    so friends can check they talk to the host and to nobody else."""

    def __init__(self, port, game="tunnela", public=0, answer=True, v2=None):
        self.port = port
        self.ctl = Client(port, b"\n")
        if v2 is None:
            self.ctl.send("RELAY|1|HOST|%s|13|%d|Tunnel host" % (game, public))
        else:  # v2: dict(max=, password=, secret=, resume=code)
            if v2.get("resume"):
                self.ctl.send("RELAY|2|RESUME|%s|13|%s|%s|Next host" % (game, v2["resume"], v2.get("secret", "")))
            else:
                self.ctl.send("RELAY|2|HOST|%s|13|%d|%d|%s|%s|Tunnel host" % (
                    game, public, v2.get("max", 4), v2.get("password", ""), v2.get("secret", "")))
        r = self.ctl.expect("ROOM|").split("|")
        self.code, self.max = r[1], int(r[2])
        self.answer = answer
        self.data = []
        self.received = {}
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self):
        try:
            while True:
                msg = self.ctl.recv(timeout=60)
                if msg is None:
                    return
                if msg.startswith("OPEN|") and self.answer:
                    d = socket.create_connection(("127.0.0.1", self.port), 3)
                    d.sendall(("RELAY|1|DATA|%s\n" % msg[5:]).encode())
                    self.data.append(d)
                    threading.Thread(target=self.echo, args=(d,), daemon=True).start()
        except Exception:
            return

    def echo(self, d):
        d.settimeout(30)
        try:
            while True:
                b = d.recv(65536)
                if not b:
                    break
                d.sendall(bytes((x + 1) % 256 for x in b))
        except OSError:
            pass
        d.close()

    def close(self):
        self.ctl.close()


def tunnel_join(port, code, game="tunnela", version="13"):
    c = Client(port, b"\n")
    c.send("RELAY|1|JOIN|%s|%s|%s|friend" % (game, version, code))
    return c


def tunnel_join2(port, code, password="", game="v2test", version="13"):
    c = Client(port, b"\n")
    c.send("RELAY|2|JOIN|%s|%s|%s|%s|friend" % (game, version, code, password))
    return c


def list_rooms(port, game, v="2"):
    c = Client(port, b"\n")
    c.send("RELAY|%s|LIST|%s" % (v, game))
    rows = c.expect("LIST|")[5:]
    c.close()
    return [r.split(",") for r in rows.split(";") if r]


def recv_exact(sock, n, timeout=10):
    sock.settimeout(timeout)
    data = b""
    while len(data) < n:
        d = sock.recv(min(65536, n - len(data)))
        if not d:
            raise ConnectionError("closed after %d bytes" % len(data))
        data += d
    return data


def t_tunnel_pipe(s):
    th = TunnelHost(s.port)
    assert CODE_RE.match(th.code) and th.max == 4
    friends = []
    for i in range(3):
        f = tunnel_join(s.port, th.code)
        assert f.expect("OK") == "OK"
        friends.append(f)
    payloads = [bytes(random.getrandbits(8) for _ in range(200000)) for _ in friends]
    # all three friends send at once, then each reads its own transformed bytes
    for f, p in zip(friends, payloads):
        threading.Thread(target=f.sock.sendall, args=(f.buf + p,), daemon=True).start()
    for f, p in zip(friends, payloads):
        got = recv_exact(f.sock, len(p))
        assert got == bytes((x + 1) % 256 for x in p), "corrupted or crossed bytes"
    extra = tunnel_join(s.port, th.code)
    msg = extra.expect("E|")
    assert "full" in msg
    for f in friends:
        f.close()
    th.close()
    return "3 friends x 200 kB both ways through the host, bytes intact and isolated; 4th: " + msg


def t_tunnel_host_leaves(s):
    th = TunnelHost(s.port)
    f1 = tunnel_join(s.port, th.code); f1.expect("OK")
    f2 = tunnel_join(s.port, th.code); f2.expect("OK")
    f1.sock.sendall(b"\x01\x02")
    assert recv_exact(f1.sock, 2) == b"\x02\x03"
    th.close()
    for f in (f1, f2):
        f.sock.settimeout(3)
        assert f.sock.recv(10) == b"", "data connection should close"
    late = tunnel_join(s.port, th.code)
    assert "No room" in late.expect("E|")
    return "friends' data connections closed; the code is gone"


def t_tunnel_friend_leaves(s):
    th = TunnelHost(s.port)
    f1 = tunnel_join(s.port, th.code); f1.expect("OK")
    f2 = tunnel_join(s.port, th.code); f2.expect("OK")
    time.sleep(0.2)
    f1.close()
    time.sleep(0.3)
    assert sum(1 for d in th.data if d.fileno() == -1) >= 1, "host side of friend 1 should close"
    f2.sock.sendall(b"\x10")
    assert recv_exact(f2.sock, 1) == b"\x11"
    f3 = tunnel_join(s.port, th.code)
    assert f3.expect("OK") == "OK", "a freed slot can be reused"
    for c in (f2, f3, th):
        c.close()
    return "host's data connection for friend 1 closed; friend 2 fine; slot reused"


def t_tunnel_errors(s):
    th = TunnelHost(s.port)
    f = tunnel_join(s.port, "ZZZZZ" if th.code != "ZZZZZ" else "YYYYY")
    m1 = f.expect("E|")
    d = Client(s.port, b"\n")
    d.send("RELAY|1|DATA|deadbeef")
    m2 = d.expect("E|")
    th.close()
    mute = TunnelHost(s.port, answer=False)
    t = time.time()
    f = tunnel_join(s.port, mute.code)
    m3 = f.expect("E|", timeout=6)
    took = time.time() - t
    mute.close()
    return "%s / %s / host silent: '%s' after %.1f s" % (m1, m2, m3, took)


def t_tunnel_ping(s):
    c = Client(s.port, b"\n")
    c.send("RELAY|1|HOST|tunnelb|7|0|ping test")
    c.expect("ROOM|")
    for _ in range(3):
        c.send("PING")
        assert c.expect("PONG") == "PONG"
    c.close()
    return "PING -> PONG on the control connection"


def t_tunnel_two_games(s):
    a = TunnelHost(s.port, "tunnela")
    b = TunnelHost(s.port, "tunnelb")
    fa = tunnel_join(s.port, a.code, "tunnela"); fa.expect("OK")
    fb = tunnel_join(s.port, b.code, "tunnelb", version="13"); fb.expect("OK")
    fx = tunnel_join(s.port, a.code, "tunnelb")
    assert "another game" in fx.expect("E|")
    fa.sock.sendall(b"A" * 1000); fb.sock.sendall(b"B" * 1000)
    assert recv_exact(fa.sock, 1000) == b"B" * 1000 and recv_exact(fb.sock, 1000) == b"C" * 1000
    for c in (fa, fb, a, b):
        c.close()
    return "two tunnel games side by side, no crosstalk"


def t_star_and_tunnel(s):
    h, code, _ = host(s.port, "sh2")
    th = TunnelHost(s.port, "tunnela")
    g = join(s.port, code); g.expect("W|1"); h.expect("J|1")
    f = tunnel_join(s.port, th.code); f.expect("OK")
    g.send("hi"); f.sock.sendall(b"\x00\x00\x00")
    assert h.expect("G|") == "G|1|hi" and recv_exact(f.sock, 3) == b"\x01\x01\x01"
    for c in (h, g, f, th):
        c.close()
    return "a star room and a tunnel room on the same port at once"


def t_list_with_lag(s):
    # --sim-delay holds replies back; the LIST reply must still arrive before the close
    h, code, _ = host(s.port, "sh2")
    lister = Client(s.port)
    lister.send("RELAY|1|LIST|sh2")
    msg = lister.expect("LIST|")
    assert code in msg, msg
    for c in (h, lister):
        c.close()
    return "with 80 ms simulated delay: " + msg


def t_info():
    # RELAY|1|INFO|<game>: the relay serves the game's mods-info (fetched from a local web server here)
    import http.server, socketserver, tempfile, shutil
    root = tempfile.mkdtemp()
    os.makedirs(os.path.join(root, "mods"))
    servers = {"schema": 1, "servers": [{"id": "main", "name": "M", "address": "relay.example.com:25565", "status": "online",
                                        "notice": "a|pipe"}]}
    mod = {"schema": 1, "id": "sh2", "latest_version": "8"}
    open(os.path.join(root, "servers.json"), "w").write(json.dumps(servers, indent=2))
    open(os.path.join(root, "mods", "sh2.json"), "w").write(json.dumps(mod, indent=2))
    handler = lambda *a, **k: http.server.SimpleHTTPRequestHandler(*a, directory=root, **k)
    web = socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=web.serve_forever, daemon=True).start()
    s = Server("--mods-info", "http://127.0.0.1:%d/" % web.server_address[1])
    try:
        for _ in range(50):
            if "mods-info: refreshed" in s.log():
                break
            time.sleep(0.1)
        c = Client(s.port, b"\0")
        c.send("RELAY|1|INFO|sh2")
        a, b = c.expect("INFO|servers|"), c.expect("INFO|mod|")
        assert json.loads(a.split("|", 2)[2]) == servers and json.loads(b.split("|", 2)[2]) == mod, (a, b)
        n = Client(s.port, b"\n")
        n.send("RELAY|1|INFO|gm2")
        missing = n.expect("E|")
        assert "No mods-info for 'gm2'" in missing, missing
        for x in (c, n):
            x.close()
    finally:
        s.stop(); web.shutdown(); shutil.rmtree(root, ignore_errors=True)
    off = Server()
    try:
        o = Client(off.port, b"\n")
        o.send("RELAY|1|INFO|sh2")
        refused = o.expect("E|")
        o.close()
    finally:
        off.stop()
    return "INFO|servers + INFO|mod one line each (a '|' in a notice survives); no file: %s; --no-mods-info: %s" % (missing, refused)


def t_whitelist():
    # the game list comes from mods-info: a mod pushed there is served on the next refresh, a removed one is
    # refused for new rooms (open rooms keep going), a bad relay block is ignored, and games.json wins over both
    import http.server, socketserver, tempfile, shutil
    root = tempfile.mkdtemp()
    os.makedirs(os.path.join(root, "mods"))

    def mod(gid, mode, players):
        return {"schema": 1, "id": gid, "name": gid + " online", "relay": {"mode": mode, "max_players": players, "server": "main"}}

    def publish(mods):
        json.dump({"schema": 1, "mods": [{"id": m["id"], "name": m["id"], "file": "mods/%s.json" % m["id"]} for m in mods]},
                  open(os.path.join(root, "index.json"), "w"))
        for m in mods:
            json.dump(m, open(os.path.join(root, "mods", m["id"] + ".json"), "w"))

    json.dump({"schema": 1, "servers": [{"id": "main", "name": "M", "address": "", "status": "offline"}]},
              open(os.path.join(root, "servers.json"), "w"))
    publish([mod("newgame", "tunnel", 2), mod("sh2", "star", 3), mod("broken", "udp", 4)])
    handler = lambda *a, **k: http.server.SimpleHTTPRequestHandler(*a, directory=root, **k)
    web = socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=web.serve_forever, daemon=True).start()
    url = "http://127.0.0.1:%d/" % web.server_address[1]
    gpath = os.path.join(root, "games.json")
    json.dump({"newgame": {"max_players": 4}}, open(gpath, "w"))
    nogames = os.path.join(root, "none.json")
    json.dump({}, open(nogames, "w"))
    s = Server("--mods-info", url, "--mods-info-refresh", "1.5", "--games", nogames)  # only mods-info's games
    o = Server("--mods-info", url, "--games", gpath)
    try:
        for srv in (s, o):
            for _ in range(60):
                if "mods-info: refreshed" in srv.log():
                    break
                time.sleep(0.1)
        th = TunnelHost(s.port, "newgame")
        assert th.max == 2, th.max
        f = tunnel_join(s.port, th.code, "newgame"); f.expect("OK")
        h, code, star_max = host(s.port, "sh2")
        assert star_max == 3, "sh2 should take max_players 3 from mods-info, got %d" % star_max
        b = Client(s.port, b"\n")
        b.send("RELAY|1|HOST|broken|1|0|x")
        broken = b.expect("E|")
        assert "Unknown game 'broken'" in broken, broken
        over = TunnelHost(o.port, "newgame")
        assert over.max == 4, over.max
        # remove newgame from mods-info: new rooms refused after the next refresh, the open one keeps piping
        publish([mod("sh2", "star", 3)])
        for _ in range(60):
            if "-newgame" in s.log():
                break
            time.sleep(0.1)
        late = Client(s.port, b"\n")
        late.send("RELAY|1|HOST|newgame|13|0|late")
        gone = late.expect("E|")
        assert "Unknown game 'newgame'" in gone, gone
        f.sock.sendall(b"\x05\x06")
        assert recv_exact(f.sock, 2) == b"\x06\x07", "open room stopped piping"
        log_line = [l for l in s.log().splitlines() if "games: +" in l][:1]
        for c in (th, f, h, b, over, late):
            c.close()
        return "mods-info added newgame (max 2) and changed sh2; broken relay block ignored; games.json override max 4; " \
               "removed from mods-info -> %s, open room still pipes; log: %s" % (gone, log_line[0][9:90] if log_line else "?")
    finally:
        s.stop(); o.stop(); web.shutdown(); shutil.rmtree(root, ignore_errors=True)


def t_relay_py_launcher():
    # the old entry point (the mods' labs run relay.py) starts the same relay
    port = free_port()
    p = subprocess.Popen([sys.executable, "-I", os.path.join(os.path.dirname(HERE), "relay.py"), "--port", str(port), "--no-mods-info", "--no-discord",
                          "--games", TEST_GAMES],
                         stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    try:
        for _ in range(100):
            try:
                socket.create_connection(("127.0.0.1", port), 0.2).close()
                break
            except OSError:
                time.sleep(0.05)
        c = Client(port, b"\n")
        c.send("RELAY|1|LIST|sh2")
        reply = c.expect("LIST|")
        c.close()
        return "python -I relay.py -> " + reply
    finally:
        p.kill()


def t_tunnel_big_transfer(s):
    # a game that sends its world on join: about 2 MB in length-prefixed frames of 48 KiB or less
    th = TunnelHost(s.port, "v2test")
    assert th.max == 4
    f = tunnel_join(s.port, th.code, "v2test"); f.expect("OK")
    world = bytes(random.getrandbits(8) for _ in range(2 * 1024 * 1024))
    frames = b"".join(struct.pack("<IB", len(world[i:i + 49152]) + 1, 7) + world[i:i + 49152]
                      for i in range(0, len(world), 49152))
    threading.Thread(target=f.sock.sendall, args=(f.buf + frames,), daemon=True).start()
    got = recv_exact(f.sock, len(frames), timeout=20)
    assert got == bytes((x + 1) % 256 for x in frames), "world transfer corrupted"
    other = tunnel_join(s.port, th.code, "tunnela")
    assert "another game" in other.expect("E|")
    for c in (f, th):
        c.close()
    return "%d frames of 48 KiB (a 2 MB world) through the tunnel intact; a client of another game is refused" % (len(world) // 49152)


# ---------------------------------------------------------------- v2 (password, size, handoff)

PASS_HASH = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"


def t_v2_password(s):
    th = TunnelHost(s.port, "v2test", public=1, v2={"password": PASS_HASH})
    m1 = tunnel_join2(s.port, th.code, "").expect("E|")
    m2 = tunnel_join2(s.port, th.code, "0" * 64).expect("E|")
    m3 = tunnel_join(s.port, th.code, "v2test").expect("E|")   # a v1 client sends no password
    assert "password" in m1 and "Wrong password" in m2 and "password" in m3
    f = tunnel_join2(s.port, th.code, PASS_HASH)
    assert f.expect("OK") == "OK"
    f.sock.sendall(b"")
    assert recv_exact(f.sock, 1) == b""
    v2rows = [r for r in list_rooms(s.port, "v2test") if r[0] == th.code]
    v1rows = [r for r in list_rooms(s.port, "v2test", "1") if r[0] == th.code]
    assert v2rows and v2rows[0][3] == "1" and v2rows[0][1] == "2", v2rows
    assert not v1rows, "v1 lists must hide locked rooms"
    for c in (f, th):
        c.close()
    return "no/wrong/v1 password refused (%s | %s | %s); right hash pipes; v2 list shows locked=1, v1 list hides it" % (m1, m2, m3)


def t_v2_size(s):
    th = TunnelHost(s.port, "v2test", v2={"max": 2})
    assert th.max == 2
    f = tunnel_join2(s.port, th.code); f.expect("OK")
    m = tunnel_join2(s.port, th.code).expect("E|")
    assert "full" in m
    big = TunnelHost(s.port, "v2test", v2={"max": 9})
    assert big.max == 4, "size is capped by the game profile"
    for c in (f, th, big):
        c.close()
    return "host-chosen max 2 -> 3rd player refused (%s); max 9 capped to 4" % m


def t_v2_handoff(s):
    secret = "ab" * 32
    th = TunnelHost(s.port, "v2test", v2={"secret": secret})
    code = th.code
    f1 = tunnel_join2(s.port, code); f1.expect("OK")
    f2 = tunnel_join2(s.port, code); f2.expect("OK")
    th.close()
    for f in (f1, f2):
        f.sock.settimeout(3)
        assert f.sock.recv(10) == b"", "links to the old host must close"
    time.sleep(0.2)
    wait = tunnel_join2(s.port, code).expect("E|")
    assert wait.startswith("E|HANDOFF:"), wait
    bad = TunnelHost.__new__(TunnelHost)
    c = Client(s.port, b"\n")
    c.send("RELAY|2|RESUME|v2test|13|%s|%s|thief" % (code, "cd" * 32))
    refused = c.expect("E|")
    assert "Not allowed" in refused
    assert not [r for r in list_rooms(s.port, "v2test") if r[0] == code], "a room changing host isn't listed"
    nh = TunnelHost(s.port, "v2test", v2={"resume": code, "secret": secret})
    assert nh.code == code
    f3 = tunnel_join2(s.port, code); f3.expect("OK")
    f3.sock.sendall(b"\x09")
    assert recv_exact(f3.sock, 1) == b"\x0a"
    for x in (f3, nh):
        x.close()
    return "host left -> links closed, joins told %s; wrong secret refused; teammate RESUMEd the same code %s and a friend piped through" % (wait.split(":")[0], code)


def t_v2_handoff_expires():
    import json
    import tempfile
    d = tempfile.mkdtemp()
    path = os.path.join(d, "games.json")
    json.dump({"v2test": dict(V2TEST, handoff=1)}, open(path, "w"))
    s = Server("--games", path)
    try:
        th = TunnelHost(s.port, "v2test", v2={"secret": "ef" * 32})
        code = th.code
        th.close()
        time.sleep(4)
        m = tunnel_join2(s.port, code).expect("E|")
        assert "No room" in m, m
        nosecret = TunnelHost(s.port, "v2test", v2={})
        code2 = nosecret.code
        nosecret.close()
        time.sleep(0.3)
        m2 = tunnel_join2(s.port, code2).expect("E|")
        assert "No room" in m2, m2
        return "handoff window over -> room closed; a room without a secret closes at once"
    finally:
        s.stop()


def t_v2_handshake_errors(s):
    c = Client(s.port, b"\n")
    c.send("RELAY|2|RESUME|sh2|1|ABCDE|secret|star game")
    m1 = c.expect("E|")
    c = Client(s.port, b"\n")
    c.send("RELAY|2|HOST|v2test|1|0")
    m2 = c.expect("E|")
    c = Client(s.port, b"\n")
    c.send("RELAY|3|HOST|v2test|1|0|4|||x")
    m3 = c.expect("E|")
    return "%s / %s / %s" % (m1, m2, m3)


def star2_host(port, game="sh2", public=1, size=4, password="", version="1.0#abc", name="Lobby"):
    c = Client(port)
    c.send("RELAY|2|HOST|%s|%s|%d|%d|%s||%s" % (game, version, public, size, password, name))
    room = c.expect("ROOM|").split("|")
    c.expect("W|0")
    return c, room[1], int(room[2])


def star2_join(port, code, game="sh2", password="", version="1.0#abc", name="Guest"):
    c = Client(port)
    c.send("RELAY|2|JOIN|%s|%s|%s|%s|%s" % (game, version, code, password, name))
    return c


def rooms2(port, game):
    c = Client(port)
    c.send("RELAY|2|ROOMS|" + game)
    reply = c.expect("ROOMS|")[6:]
    c.close()
    return [r.split(",", 8) for r in reply.split(";") if r]


def t_v2_star(s):
    h, code, size = star2_host(s.port, size=3, password=PASS_HASH)
    assert size == 3
    m1 = star2_join(s.port, code).expect("E|")
    m2 = star2_join(s.port, code, password=PASS_HASH, version="1.0#zzz").expect("E|")
    assert "password" in m1 and "mismatch" in m2.lower(), (m1, m2)
    g = star2_join(s.port, code, password=PASS_HASH, name="Ann")
    g.expect("W|1")
    h.expect("J|1|Ann")
    h.send("@META|state=ingame|region=nl|ping=42")
    g.send("hi")
    h.expect("G|1|hi")
    h.send("all")
    assert g.expect("all") == "all", "the @META line must not reach guests"
    row = [r for r in rooms2(s.port, "sh2") if r[0] == code][0]
    assert row[1:8] == ["2", "3", "1", "ingame", "NL", "42", "1.0#abc"] and row[8] == "Lobby", row
    v1 = [r for r in list_rooms(s.port, "sh2", "1") if r[0] == code]
    assert not v1, "v1 lists hide locked rooms"
    # in a v1 room @META| is an ordinary game message
    h1, code1, _ = host(s.port)
    g1 = join(s.port, code1); g1.expect("W|")
    h1.expect("J|")
    h1.send("@META|state=ingame")
    assert g1.expect("@META") == "@META|state=ingame"
    for c in (g, h, g1, h1):
        c.close()
    return "star v2: size 3, password and exact version#hash checked (%s | %s), @META kept off the wire and shown by ROOMS: %s" % (m1, m2, ",".join(row))


def t_v2_probe(s, plain):
    # a normal relay refuses to test a loopback/private caller (s runs with --probe-private so the rest can run here)
    c = Client(plain.port)
    c.send("RELAY|2|PROBE|sh2|80")
    refused = c.expect("PROBE|")
    assert refused.startswith("PROBE|error|Can't test a private"), refused
    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)
    port = srv.getsockname()[1]

    def answer():
        conn, _ = srv.accept()
        conn.recv(64)
        conn.sendall(b"<cross-domain-policy></cross-domain-policy>\0")
        conn.close()
    threading.Thread(target=answer, daemon=True).start()
    c = Client(s.port)
    c.send("RELAY|2|PROBE|sh2|%d" % port)
    m1 = c.expect("PROBE|")
    srv.close()
    c = Client(s.port)
    c.send("RELAY|2|PROBE|sh2|%d" % port)
    m2 = c.expect("PROBE|")
    assert m1.startswith("PROBE|open") and m2.startswith("PROBE|closed"), (m1, m2)
    return "loopback caller refused by default (%s); with --probe-private: %s, then %s after the listener closed" % (refused[:40], m1, m2)


# RELAY|2 (password, host-chosen size, host handoff) is tested on a test-only tunnel game
V2TEST = {"name": "v2 test game", "mode": "tunnel", "max_players": 4, "versions": [], "idle": 300, "handoff": 30}
# plain tunnel games for the tunnel tests (no real mod is built in as a tunnel game)
TUNNEL_TEST = {"name": "tunnel test game", "mode": "tunnel", "max_players": 4, "versions": [], "idle": 300}


def v2_games():
    import tempfile
    path = os.path.join(tempfile.mkdtemp(), "games.json")
    games = json.load(open(TEST_GAMES))
    games.update({"v2test": V2TEST, "tunnela": TUNNEL_TEST, "tunnelb": TUNNEL_TEST})
    json.dump(games, open(path, "w"))
    return path


FILTER = None


def main():
    global FILTER
    sys.stdout.reconfigure(encoding="utf-8")
    if "-k" in sys.argv:
        FILTER = sys.argv[sys.argv.index("-k") + 1]
    s = Server("--handshake-timeout", "1.5", "--open-timeout", "2", "--games", v2_games(), "--probe-private")
    s_rate = Server("--msg-rate", "100", "--msg-burst", "20")
    s_idle = Server("--idle", "2")
    s_fail = Server("--join-fails", "5")
    s_lag = Server("--sim-delay", "80", "--sim-jitter", "30")
    try:
        check("Flash policy request on the game port", lambda: t_policy(s))
        check("unknown game id refused", lambda: t_unknown_game(s))
        check("star: two rooms of different games, no crosstalk", lambda: t_two_rooms(s))
        check("star: guest can't claim another id", lambda: t_spoofed_id(s))
        check("star: wrong code / game / version refused", lambda: t_wrong_code(s))
        check("star: full room refused", lambda: t_full_room(s))
        check("star: host leaves -> X to guests, room closed", lambda: t_host_leaves(s))
        check("star: guest leaves -> L to host", lambda: t_guest_leaves(s))
        check("star: rooms per IP limited", lambda: t_rooms_per_ip(s))
        check("public room list per game", lambda: t_list(s))
        check("legacy H|/J| default room", lambda: t_legacy(s))
        check("handshake timeout", lambda: t_handshake_timeout(s))
        check("message rate limit (throttle)", lambda: t_rate_limit(s_rate))
        check("message size limit", lambda: t_too_large(s))
        check("idle room closes", lambda: t_idle(s_idle))
        check("wrong-code guessing limited per IP", lambda: t_join_fails(s_fail))
        check("tunnel: 3 friends pipe bytes both ways", lambda: t_tunnel_pipe(s))
        check("tunnel: host leaves -> data connections close", lambda: t_tunnel_host_leaves(s))
        check("tunnel: friend leaves -> only its pipe closes", lambda: t_tunnel_friend_leaves(s))
        check("tunnel: wrong code, bad token, host not answering", lambda: t_tunnel_errors(s))
        check("tunnel: control keepalive", lambda: t_tunnel_ping(s))
        check("tunnel: two games side by side", lambda: t_tunnel_two_games(s))
        check("star and tunnel rooms on one port", lambda: t_star_and_tunnel(s))
        check("tunnel: 2 MB world in 48 KiB frames", lambda: t_tunnel_big_transfer(s))
        check("LIST reply survives simulated lag", lambda: t_list_with_lag(s_lag))
        check("INFO serves the game's mods-info", t_info)
        check("game list from mods-info (add, remove, override)", t_whitelist)
        check("relay.py still starts the relay", t_relay_py_launcher)
        check("v2: password, locked flag in lists", lambda: t_v2_password(s))
        check("v2: host-chosen room size", lambda: t_v2_size(s))
        check("v2: host handoff resumes the same code", lambda: t_v2_handoff(s))
        check("v2: handoff window expires", t_v2_handoff_expires)
        check("v2: bad handshakes refused", lambda: t_v2_handshake_errors(s))
        check("v2 star: password, size, version hash, @META and ROOMS", lambda: t_v2_star(s))
        check("v2: PROBE connects back to the caller", lambda: t_v2_probe(s, s_rate))
        check("SERVER_PORT pickup with no arguments", t_server_port_env)
        check("refuses to start on a busy port", t_busy_port)
        check("games.json adds a game", t_games_json)
    finally:
        for x in (s, s_rate, s_idle, s_fail, s_lag):
            x.stop()
    print("\n| Check | Result | Detail |\n|---|---|---|")
    for name, ok, detail in results:
        print("| %s | %s | %s |" % (name, "✅" if ok else "❌", str(detail).replace("|", "\\|")))
    failed = sum(1 for r in results if not r[1])
    print("\nRELAY TESTS %d/%d passed" % (len(results) - failed, len(results)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
