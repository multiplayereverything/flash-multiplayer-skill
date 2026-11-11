# Intrusion Online

Released build: **Intrusion Together 2**, flash-games 64b185f (2026-10-31), local co-op for 2-4 soldiers in the SWF,
online through Ruffle Together 1.0.3.9+ (the SWF sets its own key map, so any `--coop-keys` works). QA: lab-3p+; no
run with real people on separate networks yet. The old relay mod (relay id `intrusion`, protocol `intrusion-1`, 0.2.0
unreleased) is retired and kept only for reference. Entry in [DIRECTORY.md](../DIRECTORY.md).

Side-scrolling shooter by vap (2008), AS2 SWF 8, 30 fps, obfuscated (every script starts with the same junk block;
the real code under it reads fine but doesn't recompile). The game knows one soldier, `_root.knight`, used in 200+
places, and its enemies are Verlet ragdolls.

## Intrusion Together (released)
- **Sync:** Ruffle Together lockstep, local co-op in the SWF; per-player `coop.camera` views over a shared midpoint
  camera; a leash teleports stragglers.
- **Why:** lockstep needs no world stream, no stand-ins and no protocol; every PC runs the same SWF with every
  player's keys. Solo (1 player, the default) wraps nothing, so it plays as shipped (0 pixels differ in a 2000-frame
  replay).
- **Slots:** slot 1 is whatever the game makes `_root.knight`; slots 2-4 are `new Hero(...)` next to it once it
  stands in a level. Each slot's `Update` runs with `_root.Key` = that slot's Key stand-in, which answers the
  game's key codes from `coop.buttons(slot)` (read once a frame), and for slots 2-4 with the game's aim point
  `_root.__xmouse/__ymouse` made from `coop.mouseX/Y(slot)` exactly as UpdateGame makes it from the host's mouse
  (`_root.globalToLocal`, `* 100 / actual_scale()`, clamped around that soldier) and `mouse_pressed` =
  `coop.mouseDown(slot)`. The host's own mouse is the game's.
- **Nearest player:** every other object's `Update` runs with `_root.knight` = the nearest living slot; the hit tests
  (`CollideKnight`, the beam test, `ExplodeKnight`) try every slot. If the game swaps a soldier's body during an
  update (stun ragdoll, Raptor), that slot takes the new object.
- **Shared camera:** player updates don't move it; one camera frames every living soldier (midpoint, zoom 55-100%),
  computed only from game state. It stays underneath the per-player views because it decides what the game keeps
  awake (the off-screen sleep grid). A level object that moves the camera itself (the final rocket) keeps it.
- **Per-player cameras:** every frame each slot gets `coop.camera(slot, x, y, z)`. `z = clamp(100 / level._xscale, 1,
  1.82)`, the same for all slots; (x, y) is that soldier's stage point through `objects_layer.localToGlobal`, clamped
  so the view stays inside the stage. A downed slot watches its nearest teammate. When a level's own camera moves
  (the rocket) and in the menus the cameras are switched off. `coop.hud("_root.ui")` and the overlay keep the HUD
  fixed. Replay fingerprints didn't change.
- **Leash:** a standing soldier more than 900 x 650 px from every teammate (what the shared camera fits at 55%) for
  30 frames is teleported next to the standing teammate with the most soldiers near them. Slots are checked highest
  first, so of two soldiers apart P2 joins P1; a soldier in the air is never a target. It resets x/oldx and y/oldy
  (Verlet), unhangs the soldier and gives 60 frames of invincibility. Added at the user's request after players got
  flung away.
- **Rules kept for lockstep:** no clock, no `coop.localSlot` in gameplay, no object-key loops; `LockControls` on a
  Hero locks every slot (cutscenes). Lives are shared; a dead slot respawns with its own fire key; team wipe = game over.
- **Controls:** `coop.keys(map)` at boot gives every PC the original controls (WASD or arrows, Space, 1-4, P) whatever
  the launcher passed; slot 1 presses the game's real codes so Space and P reach its menus and pause. The count is
  `coop.players` (the Players panel only shows it). With 1 player or no session nothing changes. Levels past 1 are
  untested in local co-op.
- **First release mistake (v1):** friends aimed with Q/E keys and slot 1's FIRE was code 90, so Space never reached
  the game's "click or Space" screens; players reported "not the original keys" and "can't aim with the mouse".
- **Lab:** windowed `lab.py --coop 4` (scripted per-slot keys, 7 checks: spawn, own keys, aim and shoot, jump, camera,
  respawn, enemy targets the nearest); ruffle-coop `tools/coop-lab/lab.py` with a 4-player menu script, 2600 frames:
  2p relay and direct, 3p and 4p relay, `desync_at=none` on every PC.
- **More test methods:** a headless session probe (2-4 `--coop-headless` on one port, printing every PC's traces);
  input scripts driving each slot's mouse (`move`/`click X Y slot`); a lab build that logs `SHOT Pn v vx,vy` when a
  slot adds a bullet; `windows_lab` with P2 running off to exercise the zoomed cameras.
- **Not proven:** levels past 1 in co-op, the final rocket ride for P2-P4, anything after `leave N` (a player who
  leaves just stands still), two real players on two networks.

## Relay mod (retired): path and sync
- **Path:** single player to co-op for up to 4 through the campaign. Released 0.1.0 in flash-games, replaced by
  Intrusion Together; kept for reference only.
- **Own soldier local:** each player's PC runs its soldier (no input lag) and sends a pose ~30/s: position, life
  and the soldier clip's props (frame, rotation, scale) two levels down. The host shows it as a clip `pl<id>`.
- **Host stand-ins:** each guest has an object on the host whose `__proto__` is a child of `Hero.prototype`
  (so `instanceof Hero` holds) and which answers `getx`, `CollideBody`, `Damage`, `PickWeapon`, `life` (a getter
  and setter with `addProperty`)... Whatever the world does to it is sent to its owner as an event.
- **Nearest player:** every object's `Update` is wrapped per instance; it runs with `_root.knight` set to the
  nearest living player and the screen edges set to that player's view. `CollideKnight`, the beam test and
  `ExplodeKnight` try every player; the one hit becomes `_root.knight` for the rest of that update, so the game's
  own `DamageKnight` lands on them. `Alive()` is wrapped the same way (bullets die off screen).
- **Culling:** the game puts off-screen objects to sleep in a grid. `IncludeObjects` runs once per player's
  screen; `ExcludeObjects` is replaced with the same cell test against every screen.
- **Guests draw the host's world:** the host wraps `objects_layer.attachMovie` to record linkage names and streams
  every clip near any player (changed props only, adaptive 11-30 snapshots/s, ~7 KB/s quiet, ~33 KB/s in an
  8-enemy fight). Guests attach the same linkage into their own layer, drop their own copy's level objects, keep
  player-side ones (`StunnedPlayer`).
- **Level:** triggers are numbered by creation order (the trigger classes' constructors are wrapped); the host
  sends `TR|gen|n` and guests run the same trigger function on their copy. Level clips driven by objects (doors,
  lifts) go by path. Late joiners get the trigger history (replayed without cutscene locks) and a keyframe.
- **Lives:** shared; a dead player asks the host, which takes a life and answers with a spawn point.
- **Vehicle:** a guest who climbs the Raptor gets it driven on the host with their keys and aim (a `_root.Key`
  stand-in during its update; host camera, zoom and HUD put back).

## Build
FFDec compiles each mod file into a spare `stop()` frame slot of a scratch copy (8 per run); the compiled DoAction
tags are spliced unchanged into the untouched SWF at the end of the menu frame. Release builds leave the lab file
out. See flash-inject.

## Relay mod: connection
RELAY (default): room codes, public list, Server box saved only when typed, mods-info with the relay INFO fallback.
DIRECT: `H|name` / `J|name` on the host's own relay (port 7790). The Online/Direct switch saves Direct only when
picked.

## Relay mod: lab
`tools/lab.py`: host + 2 guests (one joins mid-level) through a local relay, 46 checks: movement, enemy targets
the nearest player, guest shots kill on the host, hits and pickups reach the right PC, respawn for a team life,
trigger sync, level change, Raptor driving, fight bandwidth. Also `--direct`, `--solo`, `--scenario edges` (wrong
version, wrong code, host leaves), `--delay 80 --jitter 40`, `--modinfo http|relay`, `--release`,
`--solo --scenario levels`. Not tested: Flash Player 32, two PCs over the internet.

## Lessons
- A replay's player count is its key map's slot count: check "1 player = the original" with a 1-slot map, or the mod
  rightly plays 2 soldiers and the pixel diff fails.
- A game with one player variable that every object reads can take local co-op by swapping that variable per object
  update, but never set it to an empty slot: an undefined `_root.knight` for one frame broke the level-1 intro.
- Tests that place an enemy "near a guest" are only meaningful when the host is far away: the start area had a
  wall and a rock 400 px apart, so the lab moves the guest past the rock first.
- A failed lab step that ends a window's script makes the other windows fail later checks: read the first
  failure only.
- A screenshot step needs a pause after it: the runner captures asynchronously.
- `coop.hud` in a game that scrolls by moving `_root`: Ruffle Together up to 1.0.3.8 drew the HUD zoom x `_root._x`
  off screen; fixed in 1.0.3.9, so such games need 1.0.3.9+.
- If the mod's camera moves `_root` after the game pinned its HUD at `-_root._x`, the HUD lags a frame and is clipped
  while zooming; re-pin it right after the camera moves.
- Lab checks that depend on where P1 lands are flaky: move the soldier under test away first, and make walk checks
  jump.
- flash-games' `tools/update-catalog.ps1` rewrites every entry from the SWFs on disk and swept another session's
  pending lines into a commit: run `git status` first.
