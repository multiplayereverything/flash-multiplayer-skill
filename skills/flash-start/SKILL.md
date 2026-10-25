---
name: flash-start
description: Start here for any Flash game someone wants to play online with friends. Reads the SWF (AS2 or AS3, version, wrappers, obfuscation), checks the hub's directory for an existing mod, picks the path (take local multiplayer online, add multiplayer to a single-player game, or fix an existing online mod) and the sync model, and writes the plan before any code. Use whenever the user names a .swf or a Flash game and says multiplayer, online, co-op, versus, "play with friends" or "room codes".
---

# Flash start

Paths here are relative to the hub root, two folders up from this file (`../../`), where `references/`, `tools/`, `templates/`, `games/` and `DIRECTORY.md` live.

The first hour decides the whole mod. Don't write code in this step.

1. **Is it done already?** `python tools/directory.py find <game>`, or read `DIRECTORY.md`. If an entry exists, read its
   write-up in `games/` and take path C.
2. **Read the file:** `python tools/swfheader.py game.swf`. Note AS2 or AS3, SWF version, fps, frames, FileAttributes.
   Look for a wrapper (an inner SWF in binaryData), a sponsor preloader, a portal SDK (ad waits) and obfuscation.
   `references/recon.md` has what each finding means.
3. **Does the game already have multiplayer on one keyboard?** Check the menus and the input code (a second key set,
   a player number on the player class).
4. **Pick the path:**

| Path | When | Done before by |
|---|---|---|
| A. Local multiplayer to online | the game has 2+ players on one keyboard | Bad Ice-Cream, Gun Mayhem 2, Territory War, Bow Man |
| B. Single player to multiplayer | one player only; add co-op (or versus where it fits) | Stealth Hunter 2, Air Battle, Ultimate Crab Battle, Raft Wars, Intrusion 1 and 2 |
| C. Fix or update an existing online mod | the directory has it | any entry; read its write-up and the mod's own AGENTS.md first |

5. **Pick the sync model** from the game type (`references/network.md`, "Choosing the sync model"): turn-based, arcade or
   physics snapshots, action with local movement, or lockstep for nearly deterministic local-multiplayer games. Pick the
   closest mod in `references/games.md` and say which one you're borrowing from.
6. **Pick the injection route** (`references/build.md`): AS3 importScript + stubs; AS2 new DoAction tags (default),
   splice for obfuscated games, patched frame scripts, or p-code for lockstep.
7. **Pick a relay id** (short, lowercase, not in `DIRECTORY.md` or mods-info) and a lab port nobody else uses.
8. **Write the plan** at the top of the mod's `MODLOG.md`: path, model and why, route, relay id, players, lab port,
   what's out of scope. Show it to the user before building.

Next: `flash-map` (the system map), then `flash-lab` before any feature.
