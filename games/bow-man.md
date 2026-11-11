# Bow Man Online

Entry in [DIRECTORY.md](../DIRECTORY.md).

Two archers taking turns, AS2 SWF 6 (38 KB).

## Ruffle Together build 2.0
- **Path:** local multiplayer to online on Ruffle Together, 2 players, one archer each. No network code in the SWF.
- **Release:** 2.0 in flash-games edcc204 (`games/bowman/BowMan_online.swf`, the same file name as before),
  `--coop-keys bow-man`.
- **Controls (VS Human):** P1 W/S to aim, hold Space to draw and release to shoot; P2 I/K + Enter. Each player can also
  drag-aim with their own mouse through `coop.mouseX/Y/mouseDown(slot)`.
- **QA:** lab-2p, proven on Ruffle Together 1.0.3.6: replays identical twice (keys 3300 frames, mouse 900); the solo
  path equals the original over 1500 frames; coop-lab relay and direct, `desync_at=none`.
- **Not proven:** not rerun on 1.0.3.7+ (the run was interrupted); never played on two real PCs; a real mouse drag with
  power is untested (script clicks are one frame down); windows_lab fails on late frames only, and the untouched game
  fails the same way (Ruffle side; sync checks pass).

## Lessons
- **Per-slot mouse in turn-based AS2:** in a session, gate the game's `onClipEvent(mouseDown)` off and re-run its
  mouseDown/Move/Up each frame from `coop.mouseX/Y/mouseDown(slot)` with its own drag flag. Otherwise the host's normal
  mouse events steer P2's bow. Stage pixels to `_root` coordinates: `(mx - _root._x) * 100 / _root._xscale`.
- **"Solo = original" in `--coop-replay`:** build a test copy with the session check forced false, compare it with the
  untouched SWF, and show the real build diverges only where the session path starts.
- **Debug in headless replay** with one filled box per boolean, read from `--coop-shot`. `undefined == null` is true,
  so test with `===`.
- **A one-frame click still proves the turn gate:** delete one click and check the run stays identical up to the next
  scripted event.
- **SWF 6 traps** (true for any build of this SWF): identifiers are case-insensitive (`var n` overwrote `N`), there's
  no `try/catch` and no `getNextHighestDepth`; raising the SWF version makes `undefined + 1` NaN and breaks the arrow
  counter.

## Relay mod 1.1.1 (retired)
Kept locally only, not shipped. Relay id `bowman`, RELAY room codes or DIRECT to a relay on the host's PC. What it
taught:
- **Events-only sync:** `FIRE` with angle and power, the host's `LAND` with the true position. Positions had to be
  rounded the way Ruffle stores `_x` (twips), or hit tests differed.
- **Two arrows in flight** desynced through the wind change on landing and the game's random arrow-on-arrow
  deflection; the mod sent wind and deflection per arrow by its own flight-frame count.
- **Silent connections:** both sides ended the session after 15 s with no message.
- **Flash Player** refuses XMLSocket from a local SWF 6 file, so that mod was Ruffle only.
- A regex rename once rewrote the relay's `"L"` string and the idle state `"off"`: rename by exact match only.
