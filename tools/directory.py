"""The Flash multiplayer directory: data/games.json -> DIRECTORY.md.

  python tools/directory.py check     validate data/games.json (exit 1 on problems)
  python tools/directory.py render    validate, then rewrite DIRECTORY.md
  python tools/directory.py find <text>   search by game, id, engine or sync model

Run `render` after adding or changing an entry, and commit both files together.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "games.json")
OUT = os.path.join(ROOT, "DIRECTORY.md")

FIELDS = ["id", "game", "developer", "year", "engine", "swf", "path", "players", "sync", "status", "qa",
          "flash_player", "release", "writeup"]
ENGINES = {"AS2", "AS3"}
PATHS = {"local-to-online": "local multiplayer to online", "single-to-coop": "single player to co-op",
         "single-to-versus": "single player to versus", "fix-existing": "fix an existing online mod"}
STATUS = ["idea", "in-progress", "built", "released"]
QA = {"none": "not tested", "lab-2p": "lab, 2 players", "lab-3p+": "lab, 3+ players and late join",
      "played-online": "played between two PCs on different networks"}
ID = re.compile(r"^[a-z0-9][a-z0-9-]{1,23}$")


def load():
    return json.load(open(DATA, encoding="utf-8"))


def check(d):
    problems = []
    if d.get("schema") != 1:
        problems.append("schema must be 1")
    seen = set()
    for i, g in enumerate(d.get("games", [])):
        where = "games[%d] (%s)" % (i, g.get("id"))
        for f in FIELDS:
            if f not in g:
                problems.append("%s: missing %s" % (where, f))
        extra = set(g) - set(FIELDS)
        if extra:
            problems.append("%s: unknown fields %s" % (where, sorted(extra)))
        if not ID.match(str(g.get("id", ""))):
            problems.append("%s: id must be 2-24 chars of a-z, 0-9, -" % where)
        if g.get("id") in seen:
            problems.append("%s: duplicate id" % where)
        seen.add(g.get("id"))
        if g.get("engine") not in ENGINES:
            problems.append("%s: engine must be one of %s" % (where, sorted(ENGINES)))
        if g.get("path") not in PATHS:
            problems.append("%s: path must be one of %s" % (where, sorted(PATHS)))
        if g.get("status") not in STATUS:
            problems.append("%s: status must be one of %s" % (where, STATUS))
        if g.get("qa") not in QA:
            problems.append("%s: qa must be one of %s" % (where, sorted(QA)))
        if g.get("status") == "released" and not g.get("release"):
            problems.append("%s: released entries need a release link" % where)
        if not re.match(r"^\d(-\d+)?$", str(g.get("players", ""))):
            problems.append("%s: players like '2' or '2-4'" % where)
        w = g.get("writeup")
        if w and not os.path.exists(os.path.join(ROOT, w)):
            problems.append("%s: writeup %s does not exist" % (where, w))
        for f in ("sync", "game"):
            if "|" in str(g.get(f, "")):
                problems.append("%s: %s must not contain |" % (where, f))
    return problems


def render(d):
    games = sorted(d["games"], key=lambda g: (STATUS.index(g["status"]) * -1, g["game"].lower()))
    lines = [
        "# Directory",
        "",
        "Every Flash game in this hub: what was done, how it syncs, and how it was proven. Generated from",
        "`data/games.json` by `python tools/directory.py render`; edit the JSON, not this file.",
        "",
        "| Game | Relay id | Engine | Path | Players | Sync | Status | Proven by | Flash Player | Release |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for g in games:
        name = g["game"] + (" (%s)" % g["year"] if g.get("year") else "")
        if g.get("writeup"):
            name = "[%s](%s)" % (name, g["writeup"])
        rel = "[download](%s)" % g["release"] if g.get("release") else ""
        lines.append("| %s | `%s` | %s (SWF %s) | %s | %s | %s | %s | %s | %s | %s |" % (
            name, g["id"], g["engine"], g["swf"], PATHS[g["path"]], g["players"], g["sync"], g["status"],
            QA[g["qa"]], g["flash_player"], rel))
    lines += ["", "**Proven by:** %s." % "; ".join("`%s` %s" % kv for kv in QA.items()),
              "Only `played-online` means two real players on two networks tried it.", ""]
    return "\n".join(lines)


def main(argv):
    if not argv or argv[0] not in ("check", "render", "find"):
        raise SystemExit(__doc__)
    d = load()
    if argv[0] == "find":
        q = " ".join(argv[1:]).lower()
        for g in d["games"]:
            if q in json.dumps(g).lower():
                print("%-12s %-28s %s %s, %s, %s" % (g["id"], g["game"], g["engine"], g["status"], g["players"], g["sync"]))
        return 0
    problems = check(d)
    for p in problems:
        print("problem: " + p)
    if problems:
        return 1
    if argv[0] == "render":
        open(OUT, "w", encoding="utf-8", newline="\n").write(render(d))
        print("DIRECTORY.md: %d games" % len(d["games"]))
    else:
        print("data/games.json: OK, %d games" % len(d["games"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
