# Raze Together

Released 1.0: flash-games b831626, `games/raze/Raze_online.swf`, Ruffle Together 1.0.8, launch
`--coop-keys gun-mayhem-2 --coop-players 2-4`. QA (hub level): lab-3p+. Entry in [DIRECTORY.md](../DIRECTORY.md).

Raze (2010, Armor Games), an AS3 (SWF 9) Box2D arena shooter: one `Player` (keyboard and mouse), AI bots, Quick Match
(Deathmatch, Team Deathmatch, Elimination, Team Elimination, Juggernaut) and two 15-stage campaigns.

- **Path B.** The bytecode has control-flow obfuscation; FFDec `-config autoDeobfuscate=1` exports clean classes that
  compile. The `Game` class recompiled with no edits gave the same game as the original, frame for frame.
- **Only `Game` is recompiled**, with 4 edits: add the friends in its setup after the bots (before teams, juggernaut and
  score order), an after-frame hook at the end of its frame handler, and clean-up in its destructor.
- **Friends** are a new subclass of the game's unit class. They are built as non-human (so they don't write the one
  HUD), then AI is turned off; they count as human only around the move call (for crouching). Overrides give the spawn
  protection on respawn and let a friend reaching the score win for the players. Input comes from
  `coop.buttons/mouseX/mouseY/mouseDown(slot)`; slot 0 keeps the game's own keyboard and mouse.
- **Key map:** the SWF calls `coop.keys` when a match starts: slot 0 = W A S D, R, Q, E, Tab, P; slots 1-3 Insert
  only; the `local:` line adds arrows, Space, Shift, Enter, Ctrl.
- **Screen:** `coop.camera` per friend. The game's background and HUD move to the root (same draw order) and are pinned
  with `coop.hud`. A panel line per friend is one TextField per friend on every PC, with alpha picking the local one;
  the host's health, name and gun read-outs get alpha 0 on friends' PCs.

## QA
On the 1.0.8 release exe, one PC: solo = the original (2732 frames); replays 2/3/4 identical twice; coop-lab 2/3/4 relay
and direct in sync; leave tests with 2 and 4; 4 players through all 30 stages on a local relay in sync (a lab build
forces each stage's win after 450 frames of real play); keys and mice posted to two real windows on the launcher's
line, 34/34; two windows quiet PASS.

Not proven: the central relay, real players on two PCs, 3-4 players in real windows.

## Lab
The mod's own key lab posts keys to each window and clicks to the host window (stage to client mapping with the menu
bar and DPI), and the lab build traces the key codes and per-slot input state.

## Lessons
- Picture-only work done on one PC only desynced the session (traps.md): do the same work on every PC.
- A camera look-ahead from `coop.mouseX(slot) - camera` drifts; measure it from the hero to the aim point, capped.
- End-of-match buttons that are hit-tested text fields exist only once the game-over animation reaches them.
