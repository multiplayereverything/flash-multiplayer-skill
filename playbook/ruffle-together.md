# Ruffle Together

[Ruffle Together](https://github.com/multiplayereverything/ruffle-coop) is a fork of Ruffle desktop that plays a
local-multiplayer Flash game online with no netcode in the SWF. Every PC runs the same game in the same Ruffle build;
only key presses and the mouse travel, and every frame runs on every PC with every player's input (lockstep). The
emulator makes the game deterministic: `getTimer`, `Date`, timers, `Math.random`/`random()`, sound endings, script
time limits and window size are the same on every PC. Every 25 frames the PCs compare a fingerprint of the whole
stage; if they ever differ, every window says OUT OF SYNC and each PC writes a report.

Its own docs are the reference: the [user guide](https://github.com/multiplayereverything/ruffle-coop/blob/coop/docs/ruffle-together.md)
and the [co-op API](https://github.com/multiplayereverything/ruffle-coop/blob/coop/docs/coop-api.md). This page is
what a Flash mod needs from them.

## The paths

| The game... | What you build |
|---|---|
| already has 2-4 players on one keyboard | A key map. Often nothing in the SWF at all |
| is single player | Local co-op in the SWF: more heroes on the same screen, each read from its own slot. No network code |
| is turn-based | Each slot's keys from a key map; the game acts only on the turn owner's |

Why lockstep works here: every player runs the same emulator build, and its frame clock makes the clock, randomness,
timers and sound endings the same on every PC. The whole game, timeline scripts and physics included, stays
identical without seeding anything or sending snapshots.

What it needs: everyone has Ruffle Together (Windows release; the Multiplayer Mods Launcher installs and updates it)
and the **same SWF file** and **same version**; anything else is refused when they connect. Up to 4 players, no
joining a game already started, the host leaving ends it (a friend leaving doesn't), and the game runs at the
slowest PC's speed.

## Playing

```
ruffle_desktop --coop-host-relay <relay host:port> --coop-keys <map> --coop-players 2 Game.swf   (shows a room code)
ruffle_desktop --coop-join-relay <relay host:port> --coop-code ABCDE --coop-keys <map> Game.swf
```

or `--coop-host PORT` / `--coop-join IP:PORT` directly. Use the public Ruffle Together relay (its address is in
ruffle-coop's README), or run your own: the hub's `relay/` with a `ruffle-coop` game in its `games.json`. Host-only options: `--coop-players N`, `--coop-save coop|solo|new`,
`--coop-option NAME=VALUE`, `--coop-delay N`.

## Key maps

A key map says which game keys each player's buttons press (`slot N`, Flash key codes) and which keys a player
presses on their own PC (`local`). Every player gets the same map (refused otherwise).

```
# comment
shared                                    every slot presses the same keys (hot-seat games)
slot 0: UP=38 DOWN=40 LEFT=37 RIGHT=39 FIRE=90 ALT=88
slot 1: UP=87 DOWN=83 LEFT=65 RIGHT=68 FIRE=84 ALT=89
local: UP=38,87 DOWN=40,83 LEFT=37,65 RIGHT=39,68 FIRE=90,84 ALT=88,89
```

- Buttons: `UP DOWN LEFT RIGHT FIRE ALT KEY1 KEY2 KEY3 KEY4 VIEW QUIT YES NO MENU`. The number of slots is the
  number of players.
- `--coop-keys` takes a built-in name (bad-ice-cream, gun-mayhem-2, territory-war, bow-man, smileys-war,
  stealth-assassin, stealth-hunter-2, intrusion, intrusion-2, air-battle, ultimate-crab-battle, fireboy-watergirl) or
  a `.keys` file.
- A game can set its own map from frame 1 with `coop.keys(text)` (Dad 'n Me: every player presses the original
  arrows, A and S on their own PC). Launch it with any map that has enough slots; the game's replaces it.
- A key press also types the game key's character, so AS2 `on(keyPress "a")` menu buttons work from any map, in
  scripts and replays too (from Ruffle Together 1.0.3.8).
- Only the host's mouse reaches the game's own mouse; a game built for co-op reads every player's with the API.

## The co-op API (for SWFs made for Ruffle Together)

Calls go through `ExternalInterface.call("coop.<name>", ...)`, AS2 and AS3. The helpers
`tools/coop-api/as2/RuffleTogether.as` and `as3/RuffleTogether.as` in ruffle-coop wrap them and answer like single
player outside Ruffle Together, so one SWF works everywhere. SWF 6 and 7 must unhide `ExternalInterface` first (the
AS2 helper does it).

| Group | Calls |
|---|---|
| Players | `coop.players` (in a session when `ExternalInterface.available` and this is `> 0`), `coop.name(slot)`, `coop.version`, `coop.has(feature)`; local only: `coop.localSlot`, `coop.isHost`, `coop.ping(slot)` |
| Input | `coop.buttons(slot)` (bits), `coop.button(slot, "FIRE")`, `coop.mouseX/mouseY/mouseDown(slot)`, `coop.typed(slot)`, `coop.keys(text)` |
| Host settings | `coop.option(name)`, `coop.options` (from `--coop-option`) |
| Picture only | `coop.camera(slot, x, y, zoom)` (one camera per player; call it for every slot), `coop.hud(path)` (a root child that stays on screen), `coop.label(slot, path, text)` (a name tag) |
| Events | `coop.events`: `join N`, `leave N`, `chat N text`; read it once per frame |

**The one rule:** gameplay may use only shared answers. `localSlot`, `isHost` and `ping` differ between PCs: use
them for text, colours and sounds on this PC, never to move, show or create anything. The camera, HUD and labels
change only the picture, so each PC may follow its own player.

Every game also gets, without calling anything: typing into the selected text box from every player, chat (`/`),
play on when a friend leaves, and co-op saves (everyone starts from the host's co-op save for that SWF; every PC
keeps the same one).

## Adding players to a single-player game

- Extra heroes are copies of the game's own hero, each driven by its slot: `coop.buttons(slot)`, or key codes the
  game never reads routed to that copy before the game sees them. The game's one-player variable (`_root.hero`)
  has to point at the right copy wherever the game reads it (`playbook/traps.md`, Process).
- One screen: keep everyone in view (a camera on the players' middle), or give each player a camera with
  `coop.camera`.
- `coop.players` gives the player count; with 1 the game must be the untouched original.
- Keep P2-P4 with P1 between rooms and levels: spawn them next to P1, and move them along when P1 changes room.

## Testing

The full checklist, in order and with what counts as passed, is `.claude/skills/flash-lab/SKILL.md`. The pieces:

- `--coop-replay <swf> --coop-keys <map> --coop-script <file> --coop-frames N --coop-out <file>` runs the game
  headless from an input script and writes a fingerprint every frame. The same script must give the same file
  every time; add `--coop-shot 100,500` for PNGs, and look at them (a run that sat on the title screen also
  "matches").
- Scripts: `p0 UP|FIRE` (player 0 holds these from now), `wait 25`, `click X Y [slot]`, `move X Y`,
  `type 1 Sam{Enter}`.
- `--coop-headless --coop-frames N` runs a whole session without windows (host and join), to read `trace()` lines
  and `COOP RESULT ... desync_at=none`.
- ruffle-coop's `tools/coop-lab/lab.py` runs 2-4 headless players through a local relay with lag; its
  `windows_lab.py` runs two real windows. Real windows catch what headless can't (system fonts, audio).
- `COOP_DESCRIBE_AT=<frames>` with a replay dumps every object, the clock and the random state.

## Releasing

- Release the mod's SWF (never a lab build) like any other, and give players the launch line: the key map name or
  file, and `--coop-players`.
- In mods-info and the launcher, the game entry names the Ruffle Together key map, the player counts and the
  minimum Ruffle Together version it needs (a map built in from 1.0.3.7 doesn't exist in 1.0.3.6).
- Every player must use the same SWF bytes: a rebuilt SWF is a new version for everyone.

## The pinned build
Mods are tested on Ruffle Together **1.0.3.8** (release `v1.0.3.8`, published 2026-10-30). Everyone in a room must run
the same build: 1.0.3.7 and 1.0.3.8 players can't join each other.

| | |
|---|---|
| Zip | `RuffleTogether-1.0.3.8-windows-x64.zip`, SHA-256 `630847feb0443f50a677cfd5f09635aaaf772b018cc1fe13d94e3d14622c8a59` |
| Exe | `ruffle_desktop.exe`, SHA-256 `d269dd6e367e9462ca933803f63a302f135e5c6f5b659c2c790bd0c590934c7c` |
| Get it | `python -I tools/fetch_ruffle.py` downloads the release, checks both hashes and copies the exe |

Do not test on the stock Ruffle in `C:\Program Files\ruffle\bin` (no co-op flags), or on the older stable build
`048c81d` (1.0.3.3 code, can't join 1.0.3.7 or 1.0.3.8). When the pin changes, update `tools/fetch_ruffle.py` and this
section together, then check every mod's tests still pass.
