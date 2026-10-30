---
name: flash-multiplayer
description: Make a single-player or local-multiplayer Flash game (.swf, AS2/AVM1 or AS3/AVM2) playable online with friends in Ruffle Together, a Ruffle fork where every PC runs the same game in lockstep and only key presses travel, with room codes and no port forwarding. Covers recon of the SWF, key maps, adding local co-op to a single-player game (FFDec: AS3 importScript plus stub classes, AS2 new DoAction tags or spliced tags), the co-op API (players, buttons, mouse, cameras, HUD, name tags, events), input scripts, replays and two-window tests, and releasing (the co-op SWF, its launch line, mods-info, an optional relay of your own). Built from the Bad Ice-Cream, Gun Mayhem 2, Territory War, Bow Man, Stealth Hunter 2, Raft Wars, Intrusion, Stealth Assassin, Smileys War, Fireboy & Watergirl and Dad 'n Me games. Use this whenever someone wants to make a Flash game online, co-op, versus or multiplayer, add players to a SWF, write a Ruffle Together key map, or debug a Ruffle Together game's desync, build or tests, even if they only say "make this swf multiplayer".
---

# Flash multiplayer

A Flash game knows one keyboard. **Ruffle Together** (`references/ruffle-together.md`) puts it online without any
network code in the game: every PC runs the same SWF in the same Ruffle build, only key presses and the mouse travel,
and every frame runs on every PC with every player's input. The host gets a 5-letter room code; friends join with it.

- A game with **local multiplayer** needs a key map, and usually nothing else.
- A **single-player** game needs local co-op added to the SWF (more heroes on the same screen, each read from its own
  player slot), still with no network code. The original file is never edited.

This page is the route and the checklist. Paths here are relative to this file's folder, which holds the whole hub.
For each phase, read its own file in `skills/`: `skills/flash-start/SKILL.md`, `skills/flash-map/SKILL.md`,
`skills/flash-lab/SKILL.md`, `skills/flash-inject/SKILL.md`, `skills/flash-coop/SKILL.md`, `skills/flash-ship/SKILL.md`
and `skills/flash-share/SKILL.md`. The phase map is in `AGENTS.md`, and every game done so far is in `DIRECTORY.md`
(check it first: `python tools/directory.py find <game>`).

Read the reference that matches the step you're on.

| Step | Reference |
|---|---|
| Ruffle Together: playing, key maps, the co-op API, adding players, tests, releasing | `references/ruffle-together.md` |
| Find out what the SWF is, and where each system lives | `references/recon.md` |
| Build: AS3 (`importScript` + stubs) or AS2 (new DoAction tags, splice, patched frame scripts) | `references/build.md` |
| Every trap found so far (Ruffle, Ruffle Together, FFDec, AS2, AS3) | `references/traps.md` |
| The co-op SWF, its launch line, mods-info, a launcher | `references/release.md` |
| Run your own relay (optional) | `relay/README.md`, protocol in `references/relay-protocol.md` |
| Optional mods-info (server moves, update notices) | `modsinfo/README.md` |

## The route
1. **Recon.** Read the SWF header (`tools/swfheader.py`): SWF version, AS2 or AS3, fps, size, wrappers or sponsor
   preloaders, obfuscation. Does it already have 2+ players on one keyboard?
2. **Local multiplayer:** write a key map (`references/ruffle-together.md`, Key maps), check it with
   `tools/keys_check.py`, and test it. Often that's the whole job.
3. **Single player:** export with FFDec and map each system to the one place it runs through: frame loop, input,
   "the player", camera, levels, menus, saves (`CODE_MAP.md`). Then add the players (`skills/flash-coop`): each
   one's input from its slot, every "the player" pointing at the right copy, a camera that keeps everyone in view.
4. **Test from the start** (`skills/flash-lab`): an input script that gets through the menus, a replay that matches
   twice with screenshots looked at, 1 player = the original, 2-4 players in the coop-lab, two real windows.
5. **Release** (`references/release.md`): the co-op SWF (or the untouched game), the key map, the launch line and the
   minimum Ruffle Together version.

## Rules that held on every game
- **Never edit the original SWF.** Every build starts from the untouched file. Patches are applied by script, match
  exact text, and assert the match count; a silent miss costs hours.
- **Never publish decompiled code.** Decompiled game code is for reading only. Keep the mod's source free of game
  code: copy game classes into the build folder at build time and patch them there (`templates/build/build_as3_patches.py`).
- **Shared answers only for gameplay.** `coop.localSlot`, `coop.isHost` and `coop.ping` differ between PCs; anything
  that moves, shows or creates an object must come from shared answers, or the games split (OUT OF SYNC).
- **1 player is the original.** With one player, or outside Ruffle Together, the game takes its own path.
- **Same bytes for everyone.** Every player needs the same SWF and the same Ruffle Together version.
- **Look at the screenshots.** Two matching replays that sat on the title screen prove nothing.
- **Never drive the user's keyboard or mouse.** Tests use input scripts; stop only the processes the test started.
- **Nothing private in public repos.** No tokens, keys, passwords, personal paths, emails or home-network IPs in the
  mod, its docs or any public repo. `python tools/check_public.py` before every push.

## Tools in this skill
| Path | What |
|---|---|
| `tools/keys_check.py` | Checks a Ruffle Together key map the way Ruffle Together reads it |
| `tools/swfheader.py` | SWF version, AS2 or AS3, stage, fps, frames, DoAction count |
| `tools/swfinfo.py` | Frame labels of the main timeline and sprites |
| `tools/swfmap.py` | Display tree from FFDec `-swf2xml`, for obfuscated AS2 games |
| `tools/ffdec/AddClasses.java` | AS3: adds empty stub classes so `-importScript` can compile new classes (it can't add classes itself) |
| `tools/ffdec/CheckNamespaces.java` | AS3: fails the build when a recompiled class's protected namespace changed and a subclass wasn't recompiled (#1070) |
| `tools/ffdec/ListClasses.java` | AS3: lists the classes and static traits in a built SWF |
| `tools/ffdec/InsertAction.java` | AS2: compiles `.as` files into new DoAction tags on a chosen frame, leaving every original tag untouched |
| `tools/case_scan.py` | SWF 6: finds identifiers that collide when case is ignored |
| `tools/swfsym.py` | Links a sprite that has no class to a new AS3 class (SymbolClass tag right after its definition), so a mod can `new` it |
| `tools/unmochi.py` | Unwraps a MochiCrypt-protected SWF (RC4 + zlib payload) into the real game SWF |
| `tools/wincap.py` | Screenshot of a window by PID (PrintWindow, BitBlt fallback), never focusing it |
| `tools/check_server.py` | Checks a relay from outside: known game, a room with a friend, messages both ways |
| `templates/ruffle-together/` | An example key map, an input script, and `replay_check.py` (two replays that must match) |
| `templates/build/*.py` | Build scripts for the co-op SWF: AS3 simple, AS3 with patches on fresh decompiled copies, AS2 insert, AS2 splice |
| `relay/` | The relay server Ruffle Together's room codes go through, if you run your own; `relay/tests/test_relay.py` |
| `modsinfo/` | Optional mods-info starter kit: format, template, schema, validator |

The templates come from working games. Each says what to rename. They need `FFDEC` (path to `ffdec-cli.jar`, FFDec
26.x), Java 21, Python 3.10+ and [Ruffle Together](https://github.com/multiplayereverything/ruffle-coop).

## Report
End each step with a table: Feature | What it does | How | Tested (✅ with the evidence, or ⚠️ with why not).
Anything only tested on one PC, not between two networks, is ⚠️.
