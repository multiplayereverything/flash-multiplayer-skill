---
name: flash-ship
description: Release a Flash game for Ruffle Together - the co-op SWF and its key map, the launch line (key map, player counts, host options), the minimum Ruffle Together version, a mods-info or launcher entry, an optional relay of your own, the README, and the public-data check before every push. Use when a game's lab passes and it should reach players.
---

# Flash ship

Paths here are relative to the hub root, two folders up from this file (`../../`), where `references/`, `tools/`, `templates/`, `games/` and `DIRECTORY.md` live.

Steps in `references/release.md`:
1. The lab's steps 0-9 green on the release candidate (`skills/flash-lab`), with the release exe: replays twice
   identical with screenshots looked at, 1 player = the original, a run to the ending, every player can do
   everything, the coop-lab with 2-4 players, the leave test, two real windows.
2. The key map: a built-in name, or a `.keys` file shipped next to the SWF (`tools/keys_check.py` clean). A map
   new to Ruffle Together goes to ruffle-coop so it's built in from the next release.
3. The co-op SWF (`dist/<Game>_coop.swf`, or the untouched game for path A) published where players download it,
   with its SHA-256 checked after upload. Every player needs the same bytes.
4. The launch line and its entry in mods-info or the launcher: key map, players, host options (`--coop-option`),
   and the minimum Ruffle Together version (a map built in from 1.0.3.7 doesn't exist in 1.0.3.6).
5. A relay: players can use the public Ruffle Together relay, or yours (`relay/README.md`, with a `ruffle-coop` game).
6. The mod's README: how to host and join, controls per player, what's known not to work.
7. Before every public push: `python tools/check_public.py` (no tokens, keys, passwords, personal paths, emails, home
   or VPN IPs, game files except the release SWF, decompiled code).

Report with a table: Feature | What it does | How | Tested. Internet play stays ⚠️ until two players on two networks
tried it.

Then `flash-share`.
