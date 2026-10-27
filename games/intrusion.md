# Intrusion Online

Relay id `intrusion`, protocol `intrusion-1`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Side-scrolling shooter by vap (2008), AS2 SWF 8, 30 fps, obfuscated (every script starts with the same junk block;
the real code under it reads fine but doesn't recompile). The game knows one soldier, `_root.knight`, used in 200+
places, and its enemies are Verlet ragdolls.

## Path and sync
- **Path:** single player to co-op for up to 4 through the campaign. Released 0.1.0 in flash-games.
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

## Connection
RELAY (default): room codes, public list, Server box saved only when typed, mods-info with the relay INFO fallback.
DIRECT: `H|name` / `J|name` on the host's own relay (port 7790). The Online/Direct switch saves Direct only when
picked.

## Lab
`tools/lab.py`: host + 2 guests (one joins mid-level) through a local relay, 46 checks: movement, enemy targets
the nearest player, guest shots kill on the host, hits and pickups reach the right PC, respawn for a team life,
trigger sync, level change, Raptor driving, fight bandwidth. Also `--direct`, `--solo`, `--scenario edges` (wrong
version, wrong code, host leaves), `--delay 80 --jitter 40`, `--modinfo http|relay`, `--release`,
`--solo --scenario levels`. Not tested: Flash Player 32, two PCs over the internet.

## Lessons
- Tests that place an enemy "near a guest" are only meaningful when the host is far away: the start area had a
  wall and a rock 400 px apart, so the lab moves the guest past the rock first.
- A failed lab step that ends a window's script makes the other windows fail later checks: read the first
  failure only.
- A screenshot step needs a pause after it: the runner captures asynchronously.
