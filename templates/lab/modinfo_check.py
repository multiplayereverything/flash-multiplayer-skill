"""mods-info end to end, with a local copy of the files (testing.md): the game must take the relay address,
the update line and the minimum version from mods-info, never from a typed or built-in address.

  python tools/modinfo_check.py [--no-build]

Serves mods-info from an HTTP server on a free ephemeral port, starts the relay on 127.0.0.1:7804 with
--mods-info pointing at it, then runs three lab windows one after the other:
  A  download: modinfo=<http>, no relay flashvar, latest_version 1.1.0 -> host gets a room, "Update available"
  B  relay INFO (what Flash Player 32 needs): modinfo=<dead url>, relay=127.0.0.1:7804 -> source relay
  C  min_version 2.0.0 -> hosting on the official (mods-info) server is refused with the version line
"""
import functools
import http.server
import json
import os
import shutil
import subprocess
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lab  # noqa: E402

MOD = lab.MOD
SITE = os.path.join(MOD, "logs", "modinfo_site")


def write_site(latest, minimum):
    shutil.rmtree(SITE, ignore_errors=True)
    os.makedirs(os.path.join(SITE, "mods"))
    json.dump({"schema": 1, "servers": [{"id": "main", "name": "Lab relay", "address": "127.0.0.1:%d" % lab.LAB_PORT,
                                         "status": "online"}]}, open(os.path.join(SITE, "servers.json"), "w"))
    mod = json.load(open(os.path.join(MOD, "mods-info", "airbattle.json")))
    mod["latest_version"], mod["min_version"] = latest, minimum
    json.dump(mod, open(os.path.join(SITE, "mods", "airbattle.json"), "w"))
    json.dump({"schema": 1, "mods": [{"id": "airbattle", "name": mod["name"], "file": "mods/airbattle.json"}]},
              open(os.path.join(SITE, "index.json"), "w"))


def run_window(name, flashvars):
    log = os.path.join(MOD, "logs", "modinfo_%s.log" % name)
    p = lab.ruffle(os.path.join(MOD, "dist", "AirBattle_lab.swf"), log, flashvars)
    lab.pin_small(p.pid, 0, 1)
    try:
        start = time.time()
        taken = set()
        while time.time() - start < 90 and "LAB DONE" not in lab.read(log):
            time.sleep(0.3)
            for snap in __import__("re").findall(r"LAB\| SNAP (\w+)", lab.read(log)):
                if snap not in taken:
                    taken.add(snap)
                    hwnd = lab.wincap.find_window(p.pid)
                    if hwnd:
                        w, h, data = lab.wincap.capture(hwnd)
                        if w:
                            lab.wincap.write_png(os.path.join(MOD, "shots", "%s_%s.png" % (name, snap)), w, h, data)
    finally:
        subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
    text = lab.read(log)
    rows = [l.split("LAB| ", 1)[1] for l in text.splitlines() if "LAB| PASS" in l or "LAB| FAIL" in l]
    avm, _ = lab.avm_errors(text)
    return rows, "LAB DONE" in text, avm


def main():
    if "--no-build" not in sys.argv:
        subprocess.run([sys.executable, "-I", os.path.join(MOD, "build.py"), "--lab"], check=True)
    if lab.port_busy(lab.LAB_PORT):
        sys.exit("port %d is in use; stop whatever runs there first" % lab.LAB_PORT)
    write_site("1.1.0", "1.0.0")
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=SITE)
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    url = "http://127.0.0.1:%d/" % httpd.server_address[1]
    relay = subprocess.Popen([sys.executable, "-I", lab.RELAY, "--port", str(lab.LAB_PORT), "--bind", "127.0.0.1",
                              "--games", os.path.join(lab.HERE, "lab_games.json"), "--mods-info", url, "--log"],
                             stdout=open(os.path.join(MOD, "logs", "modinfo_relay.log"), "w"), stderr=subprocess.STDOUT)
    results, ok = [], True
    try:
        time.sleep(2.0)
        for name, fv, site in [
                ("A_download", {"lab": "modinfo", "modinfo": url, "expect": "host", "source": "download",
                                "line": "Update available: 1.1.0"}, ("1.1.0", "1.0.0")),
                ("B_relay", {"lab": "modinfo", "modinfo": "http://127.0.0.1:1/", "relay": "127.0.0.1:%d" % lab.LAB_PORT,
                             "expect": "host", "source": "relay", "line": "Update available: 1.1.0"}, ("1.1.0", "1.0.0")),
                ("C_too_old", {"lab": "modinfo", "modinfo": url, "expect": "refused", "source": "download",
                               "line": "needs version 2.0.0"}, ("2.0.0", "2.0.0"))]:
            write_site(*site)
            rows, done, avm = run_window(name, fv)
            for r in rows:
                results.append((name, r))
                ok = ok and r.startswith("PASS")
            ok = ok and done and not avm
            results.append((name, "%s, %d AVM errors" % ("finished" if done else "did NOT finish", len(avm))))
    finally:
        relay.terminate()
        httpd.shutdown()
    for name, r in results:
        print("| %s | %s |" % (name, r))
    print("RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
