---
name: flash-ship
description: Release a Flash online mod: the release build, the mods-info file that makes the live relay accept the game, the flash-games repo and catalog the launcher downloads from, the launcher entry, the README, and the public-data check before every push. Use when a Flash mod's lab passes and it should reach players, or when the live server says "Unknown game".
---

# Flash ship

Paths here are relative to the hub root, two folders up from this file (`../../`), where `references/`, `tools/`, `templates/`, `games/` and `DIRECTORY.md` live.

Steps in `references/release.md`:
1. Lab green on the release candidate, including `--solo` and a 3-player run.
2. `mods/<id>.json` for mods-info (relay mode `star`, max players, versions, download link). Ask the maintainer before
   pushing there; the live relay accepts the id about 10 minutes after the merge.
3. The `*_online.swf` (never a lab build) into the flash-games repo, run that repo's `update-catalog.ps1` (in its tools folder), commit with the
   catalog, push, and check the raw download's SHA-256 against the catalog.
4. A launcher entry with "Play online" first.
5. The mod's README: how to host and join, controls, what syncs, known issues, Ruffle or Flash Player.
6. Before every public push: `python tools/check_public.py` (no tokens, keys, passwords, personal paths, emails, home
   or VPN IPs, game files except the release SWF, decompiled code).

Report with a table: Feature | What it does | How | Tested. Internet play stays ⚠️ until two players on two networks
tried it.

Then `flash-share`.
