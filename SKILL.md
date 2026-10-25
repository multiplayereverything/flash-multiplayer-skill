---
name: flash-multiplayer
description: Turn a single-player or local-multiplayer Flash game (.swf, AS2/AVM1 or AS3/AVM2) into an online multiplayer mod that plays through the Multiplayer Everything global mod relay, with room codes and no port forwarding. Covers recon of the SWF, injecting code with FFDec (AS3 importScript plus stub classes, AS2 new DoAction tags, spliced or patched frame scripts, p-code), host-authoritative sync for turn-based, realtime and physics games, input injection for remote players, the in-game online panel, the self-driving Ruffle lab, and releasing to the flash-games repo and mods-info. Built from the Bad Ice-Cream, Stealth Hunter 2, Gun Mayhem 2, Air Battle, Intrusion 1 and 2, Territory War, Bow Man, Ultimate Crab Battle and Raft Wars mods. Use this whenever someone wants to make a Flash game online, co-op, versus or multiplayer, add room codes or a relay to a SWF, or debug a Flash mod's sync, build or lab, even if they only say "make this swf multiplayer".
---

# Flash multiplayer

A Flash game knows one player and one keyboard. These mods add online play without touching the original file:
the build injects code into a copy of the SWF, the host's game runs the real game, and the other players' games
show the host's world and send their own input. Everything goes through the global mod relay, a text relay in
star mode: the host gets a 5-letter room code and friends type it or pick the room from a public list.

Read the reference that matches the step you're on. This page is the route and the checklist.

| Step | Reference |
|---|---|
| Find out what the SWF is, and where each system lives | `references/recon.md` |
| Build: AS3 (`importScript` + stubs) or AS2 (new DoAction tags, splice, patch, p-code) | `references/build.md` |
| Choose the sync model, write messages, handle join, leave and late join | `references/network.md` |
| Hook the game: remote input, "the player" swaps, guest gates | `references/hooking.md` |
| The online panel, online by default, FlashVars | `references/ui.md` |
| The self-driving lab and the offline checks | `references/lab.md` |
| Every trap found so far (Ruffle, Flash Player 32, FFDec, AS2, AS3) | `references/traps.md` |
| How each of the 10 mods was done, to borrow the closest one | `references/games.md` |
| Relay profile, mods-info, flash-games repo, launcher | `references/release.md` |

## The route
1. **Recon.** Read the SWF header (`tools/swfheader.py`): SWF version,
   AS2 or AS3, fps, size, wrappers or sponsor preloaders, obfuscation. Export with FFDec, then map each system to the
   one place it runs through: frame loop, level load, player and input, enemies' target, damage, pickups, win and
   lose, randomness, pause, saves, sounds. Write it in `CODE_MAP.md`.
2. **Pick the sync model** from the game type (`references/network.md`):
   turn-based → the host runs the match and the player whose turn it is aims locally and sends the shot;
   arcade or physics → host-authoritative snapshots every frame plus events, guests run no game logic;
   action platformer or shooter → each player moves their own character locally, the host owns enemies and damage;
   already deterministic with local multiplayer → input lockstep from the host plus seeded RNG and periodic snapshots.
3. **Build the lab first** (`references/lab.md`): a lab build that hosts, joins and plays itself in small Ruffle windows
   through a local relay, printing `LAB| PASS/FAIL` lines. Then a solo control run that proves single player is
   unchanged. Every feature after that gets a lab check.
4. **First slice:** two windows see each other move, through the local relay.
5. **The rest of the sync**, one system at a time, each with a check: level changes, enemies, damage, pickups, score,
   death and respawn, win and lose, pause, the host leaving. Then 3 and 4 players and a late join.
6. **The panel and mods-info** (`references/ui.md`, `references/release.md`): Online is the default and usually the
   only mode.
7. **Release:** the `*_online.swf` to the flash-games repo, a launcher entry, and `mods/<id>.json` in mods-info.

## Rules that held on every mod
- **Never edit the original SWF.** Every build starts from the untouched file. Patches are applied by script, match
  exact text, and assert the match count; a silent miss cost one mod 7 lab step types.
- **Never publish decompiled code.** Decompiled game code is for reading only. Keep the mod's source free of game
  code: copy game classes into the build folder at build time and patch them there (`templates/build/build_as3_patches.py`).
- **One host, one world.** The host's game runs AI, physics, damage, randomness, timers, level flow, score and saves.
  Other players send input or requests. Don't run two copies of the world and hope they agree: Ruffle and Flash
  Player differ in the last bit of `hitTest`, timers and trig, and Box2D drifts within a second.
- **Online is the default.** HOST gives a room code on the main relay, JOIN takes one. Direct IP or LAN, if a mod
  keeps them at all, is the second choice, and a saved setting never keeps a player on Direct unless they chose it.
- **One version string.** The relay refuses a joiner whose version differs from the host's. Change it whenever a
  message changes.
- **Solo is unchanged.** With no session, the mod must take the original path. The lab's `--solo` run proves it.
- **A run counts only with 0 AVM errors.** Known bugs of the original game are listed by full stack and reported apart.
- **Never drive the user's keyboard or mouse.** Lab builds take scripted input and ignore real keys; Ruffle windows open
  small, topmost and without focus. Stop only the processes the lab started.
- **Ruffle desktop first**, Flash Player 32 second. Flash Player can't load HTTP from a local SWF and can't open
  sockets from SWF 6 files; some mods are Ruffle-only, and that's fine when it's written down.
- **Nothing private in public repos.** No tokens, keys, passwords, personal paths, emails or home-network IPs in the
  mod, its docs, mods-info or the flash-games repo. Scan before every push.

## Tools in this skill
| Path | What |
|---|---|
| `tools/ffdec/AddClasses.java` | AS3: adds empty stub classes so `-importScript` can compile new classes (it can't add classes itself) |
| `tools/ffdec/CheckNamespaces.java` | AS3: fails the build when a recompiled class's protected namespace changed and a subclass wasn't recompiled (#1070) |
| `tools/ffdec/ListClasses.java` | AS3: lists the classes and static traits in a built SWF |
| `tools/ffdec/InsertAction.java` | AS2: compiles `.as` files into new DoAction tags on a chosen frame, leaving every original tag untouched |
| `tools/swfheader.py` | SWF version, AS2 or AS3, stage, fps, frames, DoAction count |
| `tools/swfinfo.py` | Frame labels of the main timeline and sprites |
| `tools/swfmap.py` | Display tree from FFDec `-swf2xml`, for obfuscated AS2 games |
| `tools/case_scan.py` | SWF 6: finds identifiers that collide when case is ignored |
| `tools/wincap.py` | Screenshot of a window by PID (PrintWindow, BitBlt fallback), never focusing it |
| `templates/as3/RelayClient.as` | AS3 star-mode relay client: host, join, list, INFO |
| `templates/as3/NetModInfo.as`, `NetJson.as` | AS3 mods-info reader with cache and relay INFO fallback |
| `templates/as2/relay.as` | AS2 session layer on XMLSocket (SWF 6 safe) |
| `templates/as2/modinfo.as` | AS2 mods-info reader (LoadVars, then relay INFO) |
| `templates/build/*.py` | Build scripts: AS3 simple, AS3 with patches on fresh decompiled copies, AS2 insert, AS2 splice |
| `templates/lab/*` | Lab runners (AS3 and AS2), relay profile, relay and mods-info checks, message coverage check |

The templates come from working mods. Each says what to rename (package, game id, version, ports, FlashVars). They
need `FFDEC` (path to `ffdec-cli.jar`, FFDec 26.x), Java 21, Python 3.10+ and Ruffle desktop.

## Report
End each step with a table: Feature | What it does | How | Tested (✅ with the lab evidence, or ⚠️ with why not).
Anything only tested on one PC, not between two networks, is ⚠️.
