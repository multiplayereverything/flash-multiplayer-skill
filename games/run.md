# Run Together

Released 1.0: flash-games 076481f, `games/run/Run_online.swf` (SHA-256 `a379b53f...4d3b`), 2-4 players, proven on
Ruffle Together 1.0.8, launch `--coop-keys gun-mayhem-2 --coop-players 2-4`. QA (hub level): lab-3p+.
Entry in [DIRECTORY.md](../DIRECTORY.md). The sequel's mod is [Run 2](run-2.md).

Run (2008, Joseph Cloutier, Kongregate), a 3D tunnel runner, AS3 SWF 10. Its runner and key reader live in statics of
the level class, drawn by a software renderer that draws one tunnel.

- **Path B, a copy of the game per player** (the Run 2 design). Several runners in one tunnel would mean rewriting the
  renderer and physics, so a subclass of the game's obfuscated main class, made the document class, loads
  `loaderInfo.bytes` once per friend with `loadBytes` into a new ApplicationDomain, places copy N at x = 2000 * N and
  points slot N's `coop.camera` at it.
- **Keys:** the SWF calls `coop.keys` with its own map. Every copy on a PC hears every key on the stage, so each copy
  gets its own key codes every frame (slot 0 37/39/38, slot 1 65/68/87, slot 2 74/76/73, slot 3 numpad 100/102/104),
  none of them a code the game reads hard-coded (Space, P, R). On their own PC every player presses arrows or A/D and
  Space/Up/W. Slot 0 also has P/Esc (pause): every copy reads P, so it pauses everyone, and each player resumes with
  their own jump.
- **Menus:** only the host's mouse reaches the game and the menus are mouse-driven, so the copies follow the host:
  whenever the host starts a game (any mode, level, speed), each copy takes the same settings and starts its own next
  level the way the menu does. A copy already in a game goes back to its menu first and starts on the next frame.
  After that everyone plays at their own pace; the host going back to the menu doesn't touch the friends. A friend's
  camera shows their own copy on the game screen and the host's screen otherwise.
- **Mouse-only popups:** the costume-unlocked popup has only mouse buttons and stranded a friend's copy, so each slot's
  own fresh jump press takes the costume or closes the popup.
- **Saves:** friends' copies read the host's progress, then save to `run-coop-pN`. Friends' music is muted.
- **Leaving:** the leaver's copy is unloaded after its listeners are removed (traps.md).

## QA
On the 1.0.8 release exe: replays identical twice for 2/3/4 players; 1 player = the original (fingerprint file
identical); headless sessions 2/3/4 through a local relay (40 ms + jitter) and direct, no desync and no AVM errors;
leave tests (3 direct, 4 relay) clean; the host starting a new game while a friend is mid-level; all 50 Adventure levels
in 4 players' copies to the ending (a lab warp puts each runner past its level's end every 120 frames, and the game's
own level-complete path runs), in sync over 14 000 frames; physical keys 24/24 in two real windows on the launcher's
line; two real windows smooth with 2 players and with 4 games (one late frame when 3 copies build their levels at once).

Not proven: the central relay, real people on two PCs.

## Lessons
- `unloadAndStop` leaves a loaded copy's listeners running: remove them first.
- Headless runs can spend minutes on a text-heavy frame (no device fonts): run the original in the same harness first.
- In copy-per-player games, mouse-only screens strand friends, and only the host's start of a game should be followed.
- Patch lab switches into the staged copy at build time, so the release bytes stay the proven ones.
