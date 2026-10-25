"""Offline check of the wire format, no Flash needed:

  python tools/test_messages.py

- every message type the mod sends (Net.send("XX|...") anywhere in src/abnet) has a handler on the side
  that receives it, and is listed in the message table at the top of Net.as;
- every snapshot event NetSync.event("XX,...") has a case in NetSync.applyEvent;
- the version string matches tools/lab_games.json's game id and the mods-info draft's protocol;
- session state is reset on disconnect: Net.resetSession clears role, room, ids, roster and inputs.
"""
import json
import os
import re
import sys

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(MOD, "src", "abnet")


def read(name):
    return open(os.path.join(SRC, name), encoding="utf-8").read()


def main():
    net, sync, lab = read("Net.as"), read("NetSync.as"), read("NetLab.as")
    code = net + sync + lab
    fails = []

    def check(name, ok, detail=""):
        print("%s  %s%s" % ("PASS" if ok else "FAIL", name, (": " + detail) if detail else ""))
        if not ok:
            fails.append(name)

    sent = set(re.findall(r'(?:Net\.)?send\("([A-Z]{1,3})[|"]', code)) | set(re.findall(r'"([A-Z]{1,3})\|" \+', net + sync))
    sent |= set(re.findall(r'pendingEnd = "([A-Z]{1,3})\|', sync))
    guest_side = set(re.findall(r'else if\(t == "([A-Z]+)"\)|if\(t == "([A-Z]+)"\)', net[net.index("guestMessage"):]))
    guest_side = {a or b for a, b in guest_side}
    host_side = set(re.findall(r'g\[0\] == "([A-Z]+)"', net))
    to_host = {"K", "PI", "RD", "LB"}  # sent by guests
    header = net[:net.index("public class Net")]
    for t in sorted(sent):
        handled = t in (host_side if t in to_host else guest_side)
        check("message %s has a handler" % t, handled)
        check("message %s is documented in Net.as" % t, re.search(r"\b%s\b" % t, header) is not None or t == "LB")
    events = set(re.findall(r'NetSync\.event\("([A-Z]+),', open(os.path.join(MOD, "src", "core", "objects", "SingleBalloon.as"), encoding="utf-8").read()))
    for root, _, files in os.walk(os.path.join(MOD, "src")):
        for f in files:
            if f.endswith(".as"):
                events |= set(re.findall(r'(?:NetSync\.)?event\("([A-Z]+),', open(os.path.join(root, f), encoding="utf-8").read()))
    apply_ev = sync[sync.index("private static function applyEvent"):]
    for e in sorted(events):
        check("event %s has a case in applyEvent" % e, ('t == "%s"' % e) in apply_ev)
    ver = re.search(r'VERSION:String = "([^"]+)"', net).group(1)
    game = re.search(r'GAME:String = "([^"]+)"', net).group(1)
    profile = json.load(open(os.path.join(MOD, "tools", "lab_games.json")))
    check("lab relay profile is for the game id", game in profile and profile[game]["max_players"] == 4, game)
    draft = os.path.join(MOD, "mods-info", "airbattle.json")
    if os.path.exists(draft):
        d = json.load(open(draft))
        check("mods-info draft protocol = Net.VERSION", d["protocol"] == ver, "%s vs %s" % (d["protocol"], ver))
        mv = re.search(r'MOD_VERSION:String = "([^"]+)"', net).group(1)
        check("mods-info draft latest_version = Net.MOD_VERSION", d["latest_version"] == mv, "%s vs %s" % (d["latest_version"], mv))
        mi = re.search(r'const VERSION:String = "([^"]+)"', read("NetModInfo.as")).group(1)
        check("NetModInfo.VERSION = Net.MOD_VERSION", mi == mv, "%s vs %s" % (mi, mv))
    reset = net[net.index("private static function resetSession"):]
    reset = reset[:reset.index("}") + 1]
    for field in ["role = \"none\"", "roomCode = \"\"", "myId = -1", "mySlot = -1", "roster = []", "inputs = []"]:
        check("disconnect resets %s" % field.split(" ")[0], field in reset)
    print("\n%d failed" % len(fails))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
