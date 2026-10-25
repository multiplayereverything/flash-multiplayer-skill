---
name: flash-lab
description: Prove a Flash mod works without a human: a self-driving lab build, a Python runner that starts a local relay and 2-4 small unfocused Ruffle windows, scripted input, LAB PASS/FAIL lines, screenshots by window, AVM error counting, solo and must-fail control runs, lag, late join, host leaving, wrong code and version, plus offline message, relay and mods-info checks. Use before the first feature, after every change, and whenever someone asks if a Flash mod works or why a test failed.
---

# Flash lab

Paths here are relative to the hub root, two folders up from this file (`../../`), where `references/`, `tools/`, `templates/`, `games/` and `DIRECTORY.md` live.

The whole method is in `references/lab.md`. Start from `templates/lab/lab_as3.py` or `templates/lab/lab_as2.py`,
`templates/lab/lab_games.json`, and capture windows with `tools/wincap.py`.

Order:
1. Lab build + runner + relay, with one check: both windows report `ROOM` and `W|`.
2. `--solo`: the game plays unchanged with no network.
3. A control run that must FAIL, proving the checks can fail.
4. A check per feature as you build it.
5. 3 and 4 players with a late joiner from the public room list.
6. Host leaves, guest leaves, wrong code, wrong version, lag (`--sim-delay 80 --sim-jitter 40`).
7. Offline: `templates/lab/test_messages.py`, `relay_check.py`, `modinfo_check.py`.

A run counts only with 0 AVM errors and every window finished. Look at the screenshots after any UI change.
Never use the user's keyboard or mouse; stop only the processes the lab started; one lab port per mod.

Hub tools test themselves: `python -I tools/test_all.py` prints `ALL OK`.
