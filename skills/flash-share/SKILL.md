---
name: flash-share
description: Send what a Flash mod taught back to the hub: a directory entry with an honest QA level, a game write-up, new traps, tools and templates, all scanned for private data, as a commit or pull request. Use at the end of every Flash mod session, after a release, after a hard bug, or when the user says to update the skill.
---

# Flash share

Paths here are relative to the hub root, two folders up from this file (`../../`), where `references/`, `tools/`, `templates/`, `games/` and `DIRECTORY.md` live.

The next mod starts where this one stopped, but only if what you learned is written down here.

1. **Directory:** add or update the entry in `data/games.json` (fields and allowed values in `tools/directory.py`),
   then `python tools/directory.py render`. QA levels: `none`, `lab-2p`, `lab-3p+`, `played-online`. Use
   `played-online` only after two real players on two networks played it.
2. **Write-up:** `games/<game>.md`: path, sync model and why, build route, hooks, lab runs, lessons. No game code.
3. **Traps:** every new trap goes into `references/traps.md` under its section, with the mod's name in brackets.
4. **Tools and templates:** a tool that isn't game-specific goes into `tools/` (with a check in `tools/test_all.py`
   and a twin that must fail), a better template replaces the old one in `templates/`.
5. **Check:** `python -I tools/test_all.py` prints `ALL OK`, and `python tools/check_public.py` finds 0 problems.
6. Commit and push (or open a pull request). The message says what the mod learned, not just which files changed.
