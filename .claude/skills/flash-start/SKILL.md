---
name: flash-start
description: Start here for any Flash game someone wants to play online with friends. Reads the SWF (AS2 or AS3, version, wrappers, obfuscation), checks the hub's directory for existing work, and picks the path for Ruffle Together - a key map for a game that already has local multiplayer, local co-op added to the SWF for a single-player game, or fixing an existing one - and writes the plan before any code. Use whenever the user names a .swf or a Flash game and says multiplayer, online, co-op, versus, "play with friends" or "room codes".
---

# Flash start

Paths here are relative to the hub root, three folders up from this file (`../../../`), where `playbook/`, `tools/`, `templates/`, `games/` and `DIRECTORY.md` live.

Every game here goes online through **Ruffle Together** (`playbook/ruffle-together.md`): every PC runs the same
game in lockstep and only key presses travel, so the SWF never gets network code. The first hour decides how much
work the rest is. Don't write code in this step.

1. **Is it done already?** `python tools/directory.py find <game>`, or read `DIRECTORY.md`. If an entry exists, read its
   write-up in `games/` and take path C. Skip steps 2 to 7 and go straight to path C (`playbook/` and the mod's own notes). Also check Ruffle Together's built-in key maps
   (`playbook/ruffle-together.md`, Key maps).
2. **Read the file:** `python tools/swfheader.py game.swf`. Note AS2 or AS3, SWF version, fps, frames, FileAttributes.
   Look for a wrapper (an inner SWF in binaryData), a sponsor preloader, a portal SDK (ad waits) and obfuscation.
   `playbook/recon.md` has what each finding means.
3. **Does the game already have multiplayer on one keyboard?** Check the menus and the input code (a second key set,
   a player number on the player class).
4. **Pick the path:**

| Path | When | What you build | Done before by |
|---|---|---|---|
| A. Local multiplayer to online | the game has 2+ players on one keyboard | a key map, often nothing in the SWF | Bad Ice-Cream, Gun Mayhem 2, Territory War, Bow Man |
| B. Single player to multiplayer | one player only | local co-op in the SWF (more heroes, each read from its own slot), no network code | Stealth Hunter 2, Air Battle, Ultimate Crab Battle, Raft Wars, Intrusion, Stealth Assassin, Smileys War, Ultimate Assassin 1-3 |
| C. Fix or update an existing one | the directory has it | read its write-up and the mod's own AGENTS.md first | any entry |

5. **Path B only: how do the extra players fit?** One screen for everyone (a camera on the players' middle), or a
   camera per player (`coop.camera`). Turn-based games read each slot's keys and act on the turn owner's.
   `.claude/skills/flash-coop` has the details.
6. **Pick the injection route** for path B (`playbook/build.md`): AS3 importScript + stubs; AS2 new DoAction tags
   (default), or splice for obfuscated games.
7. **Write the plan** at the top of the mod's `MODLOG.md`: path, players, key map (built-in name or a new file),
   route, what's out of scope. Show it to the user before building.

Next: `flash-map` (the system map), then `flash-lab`.
