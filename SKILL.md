---
name: flash-multiplayer
description: Turn a single-player or local-multiplayer Flash game (.swf, AS2/AVM1 or AS3/AVM2) into an online multiplayer game: either played in Ruffle Together (lockstep inside the emulator, no netcode in the SWF, the first choice for local-multiplayer games) or as a mod that plays through your own relay server (included, Python, one port for every game), with room codes and no port forwarding for players. Covers recon of the SWF, injecting code with FFDec (AS3 importScript plus stub classes, AS2 new DoAction tags, spliced or patched frame scripts, p-code), host-authoritative sync for turn-based, realtime and physics games, input injection for remote players, the in-game online panel, the self-driving Ruffle lab, and releasing (your relay online, optional mods-info, publishing the build). Built from the Bad Ice-Cream, Stealth Hunter 2, Gun Mayhem 2, Air Battle, Intrusion 1 and 2, Territory War, Bow Man, Ultimate Crab Battle, Raft Wars, Stealth Assassin, Smileys War and Dad 'n Me mods. Use this whenever someone wants to make a Flash game online, co-op, versus or multiplayer, add room codes or a relay to a SWF, or debug a Flash mod's sync, build or lab, even if they only say "make this swf multiplayer".
---

# Flash multiplayer

A Flash game knows one player and one keyboard. These mods add online play without touching the original file:
the build injects code into a copy of the SWF, the host's game runs the real game, and the other players' games
show the host's world and send their own input. Everything goes through a relay you run (`relay/`, see `relay/README.md`), a text relay in
star mode: the host gets a 5-letter room code and friends type it or pick the room from a public list.

There is a shorter way for many games: **Ruffle Together** (`references/ruffle-together.md`), a Ruffle fork that
runs the same game on every PC in lockstep and sends only key presses. A game with local multiplayer often needs no
mod at all, just a key map; a single-player game needs local co-op added to the SWF, with no network code. Check it
first; build a relay mod when the game must run in Flash Player or the browser, or players must be in different
places at once.

This page is the route and the checklist. Paths here are relative to this file's folder, which holds the whole hub.
For each phase, read its own file in `skills/`: `skills/flash-start/SKILL.md`, `skills/flash-map/SKILL.md`,
`skills/flash-lab/SKILL.md`, `skills/flash-inject/SKILL.md`, `skills/flash-sync/SKILL.md`, `skills/flash-ship/SKILL.md`
and `skills/flash-share/SKILL.md`. The phase map is in `AGENTS.md`, and every game done so far is in `DIRECTORY.md`
(check it first: `python tools/directory.py find <game>`).

Read the reference that matches the step you're on.

| Step | Reference |
|---|---|
| Find out what the SWF is, and where each system lives | `references/recon.md` |
| Build: AS3 (`importScript` + stubs) or AS2 (new DoAction tags, splice, patch, p-code) | `references/build.md` |
| Play it in Ruffle Together instead: key maps, the co-op API, adding local co-op, replay tests | `references/ruffle-together.md` |
| Choose the sync model, write messages, handle join, leave and late join | `references/network.md` |
| Hook the game: remote input, "the player" swaps, guest gates | `references/hooking.md` |
| The online panel, online by default, FlashVars | `references/ui.md` |
| The self-driving lab and the offline checks | `references/lab.md` |
| Every trap found so far (Ruffle, Flash Player 32, FFDec, AS2, AS3) | `references/traps.md` |
| How each mod was done, to borrow the closest one | `references/games.md` |
| Run your own relay | `relay/README.md`, protocol in `references/relay-protocol.md` |
| Optional mods-info (server moves, update notices) | `modsinfo/README.md` |
| Your relay's game list, optional mods-info, publishing, a launcher | `references/release.md` |

## The route
1. **Recon.** Read the SWF header (`tools/swfheader.py`): SWF version,
   AS2 or AS3, fps, size, wrappers or sponsor preloaders, obfuscation. Export with FFDec, then map each system to the
   one place it runs through: frame loop, level load, player and input, enemies' target, damage, pickups, win and
   lose, randomness, pause, saves, sounds. Write it in `CODE_MAP.md`.
2. **Pick the sync model** from the game type (`references/network.md`). First ask whether Ruffle Together fits
   (`references/ruffle-together.md`): local multiplayer → a key map; single player → local co-op in the SWF. If it
   does, steps 3-7 become: replay and coop-lab checks, the co-op build, a key map, and the release line. Otherwise:
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
7. **Release:** your relay knows the game id, the mod has your relay built in, and the `*_online.swf` is published.

## Rules that held on every mod
- **Never edit the original SWF.** Every build starts from the untouched file. Patches are applied by script, match
  exact text, and assert the match count; a silent miss cost one mod 7 lab step types.
- **Never publish decompiled code.** Decompiled game code is for reading only. Keep the mod's source free of game
  code: copy game classes into the build folder at build time and patch them there (`templates/build/build_as3_patches.py`).
- **One host, one world.** The host's game runs AI, physics, damage, randomness, timers, level flow, score and saves.
  Other players send input or requests. Don't run two copies of the world and hope they agree: Ruffle and Flash
  Player differ in the last bit of `hitTest`, timers and trig, and Box2D drifts within a second.
- **Online is the default.** HOST gives a room code on your relay, JOIN takes one. Direct IP or LAN, if a mod
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
  mod, its docs or any public repo; your relay's public address is the only server detail that belongs there.
  `python tools/check_public.py` before every push.

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
| `tools/swfsym.py` | Links a sprite that has no class to a new AS3 class (SymbolClass tag right after its definition), so a mod can `new` it |
| `tools/unmochi.py` | Unwraps a MochiCrypt-protected SWF (RC4 + zlib payload) into the real game SWF |
| `tools/wincap.py` | Screenshot of a window by PID (PrintWindow, BitBlt fallback), never focusing it |
| `templates/as3/RelayClient.as` | AS3 star-mode relay client: host, join, list, INFO |
| `templates/as3/NetModInfo.as`, `NetJson.as` | AS3 mods-info reader with cache and relay INFO fallback |
| `templates/as2/relay.as` | AS2 session layer on XMLSocket (SWF 6 safe) |
| `templates/as2/modinfo.as` | AS2 mods-info reader (LoadVars, then relay INFO) |
| `templates/build/*.py` | Build scripts: AS3 simple, AS3 with patches on fresh decompiled copies, AS2 insert, AS2 splice |
| `relay/` | the relay server: run it locally for labs and online for players; `relay/tests/test_relay.py` |
| `tools/check_server.py` | checks a relay from outside: known game, a room with a friend, messages both ways |
| `modsinfo/` | optional mods-info starter kit: format, template, schema, validator |
| `templates/lab/*` | Lab runners (AS3 and AS2), relay profile, relay and mods-info checks, message coverage check |

The templates come from working mods. Each says what to rename (package, game id, version, ports, FlashVars). They
need `FFDEC` (path to `ffdec-cli.jar`, FFDec 26.x), Java 21, Python 3.10+ and Ruffle desktop.

## Report
End each step with a table: Feature | What it does | How | Tested (✅ with the lab evidence, or ⚠️ with why not).
Anything only tested on one PC, not between two networks, is ⚠️.
