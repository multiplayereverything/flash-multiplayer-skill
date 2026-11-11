# Intrusion 2 Online

Released: flash-games `games/intrusion2/Intrusion2_online.swf`, commit 924bd92, needs Ruffle Together 1.0.3.9+. QA
(hub level): lab-3p+. Entry in [DIRECTORY.md](../DIRECTORY.md).

Side-scrolling shooter with Box2D ragdolls, AS3 SWF 9 (18 MB), partly obfuscated.

- **Path:** single player to co-op, 2-4 players.
- **Sync:** Ruffle Together local co-op added to the SWF, lockstep. Every slot is a real game hero driven by
  `coop.buttons(slot)` plus its own mouse. Enemies target the nearest living hero. Lives are shared; a leash and a
  respawn next to a teammate keep the team together.
- **API used:** `coop.players`; `coop.keys` on boot (slot 0 gets the real codes, slots 1-3 keys the game never reads);
  `coop.buttons(slot)`; `coop.mouseX/Y/mouseDown(slot)`, aimed through the inverse of the level matrix as the game
  does for the host; `coop.name` tags; `coop.camera` for every slot each frame; `coop.hud`; `coop.events` `leave N`
  (the leaver's hero is removed and doesn't respawn).
- **Cameras:** the game's own camera zooms out to fit all living heroes. Each slot gets `coop.camera(s, x, y, z)` with
  z = 1 / level scale clamped to 1..1/0.55, and (x, y) the hero's stage point through the level matrix, clamped
  inside the stage; a downed slot follows the nearest living hero. Outside the play loop `coop.camera(s)` turns it off.
- **Crosshairs:** the game calls `Mouse.hide()` and draws only the host's crosshair, so the mod draws one coloured
  crosshair per slot at `coop.mouseX/Y(slot)` (shared answers, so sync-safe).
- **HUD:** the AS3 HUD is created in code on root; the mod names it `coophud`, marks it with `coop.hud("root.coophud")`
  and marks it again when the game makes a new HUD.
- **QA:** replays with 1-4 players identical twice; 1 player equal to the untouched original every frame from the
  start of level 1 (frame 532) to 3235; `lab.py` relay and direct with 2/3/4 players in sync for 3235 frames; leave
  test PASS. Flash Player untested.
- **Not proven:** two real PCs, a real window (name tags), the zoom-out in normal play (only shown with a debug build
  forcing it).
- **Old relay mod:** relay id `intrusion2` (each PC ran its own hero, host owned enemies and triggers, 3-player lab
  passing) is retired; it was never released.

## Lessons
- Per-player cameras in a game with its own zoom: let the game's camera zoom out to fit all living heroes and stop
  the heroes' own camera follows from pulling the zoom back to 1.
- If the game's fit list can't remove a hero cleanly, recreate the fit when the set of living heroes changes.
- A game that hides the mouse and draws only the host's crosshair needs one crosshair per slot from the shared mouse.
- An AS3 HUD made in code needs a `.name` before `coop.hud` can mark it, and a new mark each time it is rebuilt.
- To read values in a test, draw them as bars in the `coop.hud` clip and take `--coop-shot` (this proved the shared
  scale 0.55 and z 1.82).
- A leave test must kill a friend's process mid-level (`taskkill /T /F`); a friend reaching `--coop-frames` isn't a
  leave (the host waits ~60 s and reports it frozen).
- Solo replays need a 1-slot `.keys` file.
