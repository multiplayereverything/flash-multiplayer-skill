# Stealth Hunter 2 Online

Entry in [DIRECTORY.md](../DIRECTORY.md).

Stealth campaign (RacSeven), AS3 SWF 11, obfuscated and wrapped: the real game is an inner SWF stored in a binaryData
tag with its first and last 999 bytes swapped.

## Co-op build 2.1 (Ruffle Together)
- **Path:** single player to co-op, 2-4 players. Every PC runs the same game in lockstep in Ruffle Together; local
  co-op is added to the SWF, with no network code.
- **Release:** 2.0 on 2026-10-29 (flash-games 5475a7f); 2.1 on 2026-10-31 (flash-games 4c01013) gives each player a
  camera of their own (`coop.camera`). Needs Ruffle Together 1.0.3.7+ (the camera API), `--coop-keys stealth-hunter-2`.
- **Players:** P2-P4 are extra Buddies, each on key codes of its own, tinted. The count comes from `coop.players` (or a
  PLAYERS menu button). Frame time is `getTimer()`, which Ruffle Together's frame clock drives.
- **Cameras:** one per player in 2.1. When `coop.has("camera")` is false, the 2.0 shared camera on the players'
  middle stays as the fallback.
- **QA:** lab-3p+. Proven on the 1.0.3.7 release exe: `--coop-replay` twice identical; coop-lab with 2, 3 and 4
  players, relay and direct, `desync_at=none` in all 18 results; one-window co-op lab 17/17 (1 player = original,
  slot keys move only their own player).
- **Not proven:** a friend leaving mid-game, Esc/MENU skipping cutscenes, and solo against the untouched original (all
  on 1.0.3.7); two real PCs.
- **Limit:** players more than 3 screens apart see black at the far edge.

### How the cameras work
- The tile engine blits the world into one screen-sized canvas at the camera's offset. Under `coop.camera` only P1's
  view was drawn. Growing a cull rect wasn't enough.
- After the game's update (its camera is done), the mod sets the engine camera to the corner of a region around every
  player's view, sets the viewport to the region's size and grows the render canvas in whole blocks.
- At the start of the next update the game's own camera and viewport are put back, so the simulation never sees the
  region. Each slot's `coop.camera` is its player's point inside the region.
- Screen-space layers (night tint, rain, vignettes) are stretched over the region while cameras are on.
- The HUD sits deep in the game's screen. While cameras are on it moves into a root child for `coop.hud`, and back for
  menus and cutscenes.
- HUD markers placed with the camera's x (a prompt over P1) are set again on EXIT_FRAME from P1's own camera and shown
  only on P1's PC (alpha by `coop.localSlot`, picture only).
- The game reads the mouse as camera x + the engine's mouse x during its update, so the engine is shifted by (game
  camera - region corner) for the update.

### Lab methods
- `--coop-replay` passes no FlashVars and draws only slot 0's camera. To check another slot's view, make a throwaway
  build where slot 0 uses slot N's camera. All views giving the same fingerprints proves the camera is picture only.
- coop-lab's `lab.py` has no `--save-directory`: pass `--exe` a `.cmd` wrapper that runs the release exe with
  `--save-directory <temp> %*`.

### Lessons
- A tile engine that blits into a screen-sized canvas needs a region around every view, not a bigger cull rect.
- Restore the game's camera before each update, so the region never reaches gameplay.
- Mouse reads built from the camera need the engine shifted back for the update.

## Relay mod 1.1 (retired)
The release is now the co-op build above. The relay mod (relay id `sh2`, RELAY room codes or DIRECT to a relay on the
host's PC, port 7790) is no longer the release. What it taught:
- **Sync:** a host snapshot at 15 Hz plus events; guests smoothed and extrapolated. Later each player moved their own
  character locally and the host's copy walked to it, so guards still heard footsteps.
- **Hooks:** recompiling any subclassed class broke its protected namespace (#1070), so the mod used new subclasses,
  an engine component that runs after every entity update, and whole rewrites of classes nothing subclasses. Each
  remote player had its own keyboard object, swapped in while it updated. The co-op build reuses these hooks.
- **Rule chosen:** any player's death fails the mission for the team.
- **Flash Player:** a Flash Player host with a Ruffle friend gave an error storm on the friend; the mod became Ruffle
  only.
- **1.1 (2026-10-28):** three fixes from the 3-4 player lab, each with a step that makes the fault happen on purpose:
  resend lock-gone messages with the periodic trigger state, ask again for a dropped level load, and have friends
  follow the host to the menu. Never played between two PCs.
