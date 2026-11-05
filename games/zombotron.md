# Zombotron Online

Id `zombotron`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Ant Karlov's single-player action platformer (Armor Games, 2011), AS3 SWF 10 with Box2D, 10 levels, shops and checkpoints.

- **Path:** single player to co-op, 1-4 players.
- **Key map:** started with `--coop-keys gun-mayhem-2 --coop-players 2-4`, then the SWF sets its own map with `coop.keys`. Every hero reads `coop.buttons(slot)` and aims and fires with `coop.mouseX/Y/Down(slot)`.
- **The players:** extra heroes spawn at the level's respawn point, tinted, with their own panel and name tag. Enemies target every hero through physics sensors. Any living hero triggers sensors, and whoever reaches the exit takes the team on. The shop uses the coins of whoever opened it and follows their mouse.
- **Cameras:** a camera per player with `coop.camera`; player 1 sees exactly the original camera. Host options: `camera=team` (shared, zooms out to fit) and `zoom=0.5..1.5`. 1.1 added edge arrows with name and distance after a player thought friends were vanishing when one ran ahead.
- **Down and up:** jump to get up next to a friend after 2 s. When everyone is down, jump acts as the original Space (checkpoint or restart).
- **Leaving:** `leave N` frees that hero, panel, tag and camera.
- **Lab runs (Ruffle Together 1.0.3.8):** solo identical to the original; replays identical at 2, 3 and 4 players; lab build to the ending twice at each count, all 10 levels, each player taking exits, also with a player leaving on level 4; coop-lab relay and direct in sync; two real windows with no desync.
- **Not proven:** friendly fire and bump (host options, off by default) and zoom were checked by reading the code only. No two-PC game.
- **Limits:** friends' weapons, ammo and coins last for the session; only player 1's are saved. Menus, Space to start a level and pause are the host's.
