# Ultimate Flash Sonic Together

Released: flash-games 236472f, `games/ultimateflashsonic/UltimateFlashSonic_online.swf` (SHA-256 `fce6d3ee...f59f`),
2-4 players, minimum Ruffle Together 1.0.8 (tested only there). QA (hub level): lab-3p+. Launcher id
`ultimateflashsonic`, no launcher record yet. Entry in [DIRECTORY.md](../DIRECTORY.md).

Ultimate Flash Sonic (2004, menace.ch, a fan game). The copy used is the Web Design Museum's (SHA-256
`971048de...2b90`). SWF 5, AS1, 350x250, 35 fps, 359 frames; no wrapper, no obfuscation, no network calls, no saves.

- **SWF version:** SWF 5 can't reach `ExternalInterface` in Ruffle, so the mod re-encodes the game at SWF 6 with
  `tools/ffdec/SetVersion.java` (every tag written again; never just the header byte). The fingerprint matched the
  original on every frame.
- **Launch:** `--coop-keys gun-mayhem-2 --coop-players 2-4`. The SWF sets its own map with `coop.keys`: slot 0 arrows
  + Space; slots 1-3 W S A D + F, I K J L + H, numpad 8 5 4 6 + 0; YES = Enter, NO = Backspace; `local:` arrows/WASD,
  Space/Z.
- **The players:** the hero is one placed clip whose keys are its own variables (`up`, `left`, `jump`... = key codes).
  Players 2-4 are `duplicateMovieClip` copies with other key codes, so no key-reading code changed at all.
- **"The player":** 82 scripts name `_root.Sonic1`, and springs, rails and spikes hit-test the hero's shared ground
  sensor `_root.h`. Setting `_root.Sonic1` and `_root.h/h1/h2/h3` as variables (found before the clips of the same name)
  points the game's own code at another hero; `delete` restores player 1. The scripts are sorted into EACH (stateless
  effects: run once per hero), TOUCH (objects with state: once, nearest hero, hit tests true for whoever touches) and
  P1 (HUD, sounds, follower).
- **One shared screen:** the level exists only in a 3x3 window of 180 px tiles around one camera. The camera sits on the
  middle of the heroes who are up, the edges hold heroes in, and one held back (or off the top or bottom) for 3 s jumps
  to the one in front. A downed player falls off like the original death and comes back next to a friend; the original
  death runs only when nobody is up.

## QA
Replays identical with 2/3/4 players; solo = the original (fingerprint and screenshots); coop-lab 2/3/4 relay and direct
in sync; the whole game in sync over a local relay with 2 and 4 players (acts cut short by a lab build); leave tests with
2 and 4; physical keys and a leave in two real windows on the launch line; solo window keys.

Not proven: the central relay, two real PCs.

## Lab
The menus are mouse-only and real-window labs can't click, so a key-probe build starts the game itself (the frame the
preloader's START leads to, then the menu's own variables and its game frame). The mod's own tools include a key lab
with `--leave` (a friend closes their window and the heartbeats must show one hero fewer) and `--solo` (every key
reaches the game and none is a hero's key), and a memory and Ruffle-count gate.

## Lessons
- SWF 5 has no `_global` in Ruffle; raise it to 6 by re-encoding every tag (traps.md).
- SWF 6 case-insensitivity: a parameter `L` and a `var l` in one function are one variable; `case_scan.py` catches it.
- Filter a list before `removeMovieClip`: a removed clip has lost its own fields.
