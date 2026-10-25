---
name: flash-ship
description: Release a Flash online mod: run your own relay server (included) and put it online, add the game to it, build its address into the mod, optional mods-info for server moves and update notices, publish the release build, a launcher entry, the README, and the public-data check before every push. Use when a Flash mod's lab passes and it should reach players, when someone needs a relay server, or when the server says "Unknown game".
---

# Flash ship

Paths here are relative to the hub root, two folders up from this file (`../../`), where `references/`, `tools/`, `templates/`, `games/` and `DIRECTORY.md` live.

Steps in `references/release.md`:
1. Lab green on the release candidate, including `--solo` and a 3-player run.
2. **Your relay** (`relay/README.md`): running where players can reach it, with the game's id in its `games.json`;
   the mod's built-in server is its public address. Check `RELAY|1|LIST|<id>` from another network.
3. Optional mods-info, so you can move the relay or announce updates without a rebuild.
4. The `*_online.swf` (never a lab build) published where players download it, with its SHA-256 checked after upload.
5. A launcher entry with "Play online" first, if you have a launcher.
6. The mod's README: how to host and join, controls, what syncs, known issues, Ruffle or Flash Player.
7. Before every public push: `python tools/check_public.py` (no tokens, keys, passwords, personal paths, emails, home
   or VPN IPs, game files except the release SWF, decompiled code).

Report with a table: Feature | What it does | How | Tested. Internet play stays ⚠️ until two players on two networks
tried it.

Then `flash-share`.
