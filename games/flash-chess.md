# Flash Chess Online

Released 1.0: flash-games f41daf4, `games/flashchess/FlashChess_online.swf` (SHA-256 `a062425c...e3da8`), 2 players,
Ruffle Together 1.0.8+ (uses `coop.mouse`, `coop.zone` and `coop.mouse.clicker`; tested only on 1.0.8). QA (hub
level): lab-2p. Entry in [DIRECTORY.md](../DIRECTORY.md).

Flash Chess (2002), Digital Vision Multimedia; the Web Design Museum's copy. SWF 5, AS1, 800x600, 100 fps, 75 KB. One
human against the computer; the game has no 2-player mode.

- **Path:** single player to versus. The host is blue (moves first); the friend is red in place of the computer.
- **Launch:** `--coop-keys bow-man --coop-players 2` (a built-in 2-slot map; the SWF sets its own).
- **Turns and mice:** `coop.mouse("zones")`, and each turn `coop.zone` over the board for the side to move only, so
  each player moves only their own pieces on their own turn, with their own mouse, through the game's own buttons. The
  wrapped handlers also check `coop.mouse.clicker`. Per-PC state (YOU MOVE, the win message) is shown with alpha on the
  game's own clips and the text of an existing field.
- **Leaving:** a leaver's red goes back to the computer.
- **SWF 5:** the mod gets the global object with `g.call(null)` and unhides `flash` and `setInterval` there, so the SWF
  stays at version 5 (traps.md).

## QA
Replays identical; solo = the original every frame (against the AI, both levels); clicks by the wrong player or on the
wrong turn provably change nothing (twin fingerprints); whole games to checkmate in coop-lab relay and direct, in sync;
leave tests on both turns; RESTART in a session. Real windows: only the friend's posted mouse moves and zones (traced
identically on both PCs).

Not proven: clicks in real windows, the host's mouse in real windows, the live relay, two PCs.

## Lab
The mod's own tools turn chess moves into an input script with per-slot mice, "must do nothing" clicks and a twin
mode; run every scripted check behind the memory gate one at a time; and drive two real windows with posted moves,
checked through `coop.mouse.hovered(slot)` traces.

## Lessons
- SWF 5 hides `_global`, `flash` and `onEnterFrame`; `g.call(null)` reaches the global object anyway.
- A twin test's "must do nothing" click by the side to move, on its own piece, is a real selection.
- Posted mouse presses still don't press buttons in real windows on 1.0.8.
