# Zombotron Online

Id `zombotron`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Ant Karlov's single-player action platformer (Armor Games, 2011), AS3 SWF 10 with Box2D, 10 levels, shops and checkpoints.

- **Path:** single player to co-op, 1-4 players.
- **Release:** 1.1, flash-games 5d3265d (1.0 was 9a5569e), Ruffle Together 1.0.3.8, hub QA level lab-3p+.
- **Key map:** started with `--coop-keys gun-mayhem-2 --coop-players 2-4`, then the SWF sets its own map with `coop.keys`. Every hero reads `coop.buttons(slot)` and aims and fires with `coop.mouseX/Y/Down(slot)`.
- **The players:** extra heroes spawn at the level's respawn point, tinted, with their own panel and name tag. Enemies target every hero through physics sensors. Any living hero triggers sensors, and whoever reaches the exit takes the team on. The shop uses the coins of whoever opened it and follows their mouse.
- **Cameras:** a camera per player with `coop.camera`; player 1 sees exactly the original camera. Host options:
  `camera=team` (shared, zooms out to fit) and `zoom=0.5..1.5`.
- **Edge arrows (1.1):** with a camera per player, testers said friends "disappeared" when one ran ahead (just off
  screen). Every PC builds an arrow for every (camera, teammate) pair, with name and distance, placed from shared
  camera values; only the local camera's arrows get alpha 1. Alpha is safe to set per PC; position and visibility
  are not. Proof: coop-lab with 21 players at `desync_at=none`, and two real windows each showing only its own
  arrows.
- **Down and up:** jump to get up next to a friend after 2 s. When everyone is down, jump acts as the original Space (checkpoint or restart).
- **Leaving:** `leave N` frees that hero, panel, tag and camera.
- **Lab runs (Ruffle Together 1.0.3.8):** solo identical to the original; replays identical at 2, 3 and 4 players;
  lab build to the ending twice at each count, all 10 levels, each player taking exits, also with a player leaving on
  level 4; coop-lab relay and direct in sync; two real windows with no desync. A level exit reached by a lab teleport
  hook runs the same path as a real exit (`TriggerSensor`), checked in a replay and in two real windows.
- **Not proven:** no two-PC game. Friendly fire and bump (host options, off by default) and zoom were checked by
  reading the code only.
- **Limits:** friends' weapons, ammo and coins last for the session; only player 1's are saved. Menus, Space to start a level and pause are the host's.

## Lessons
- With a camera per player, add off-screen markers or a team camera from the start.
- Per-player HUD bits under `coop.camera`: build them on every PC from shared values; set only alpha per PC.
- AddClasses put new class stubs in the preloader's frame-1 ABC tag: the preloader failed and the timeline looped
  silently. Put stubs into a real game class's ABC tag (`ADD_TO=<class>`).
- Key maps refuse codes with no key (F12=123, F24=135: "no key with code"). For a key the game never reads, use
  Insert (45).
