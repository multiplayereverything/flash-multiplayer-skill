# Dad 'n Me Online

Id `dadnme`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Tom Fulp and Dan Paladin's single-player beat 'em up, AS2 SWF 6, 45 fps.

- **Path:** single player to co-op, 1-4 players on one shared screen.
- **Release:** 1.5, flash-games 16ac6ad, byte-identical to 1.2 (7a89553). Tested up to Ruffle Together 1.0.3.8, not
  rechecked on later versions.
- **Key map:** started with `--coop-keys gun-mayhem-2 --coop-players 2-4`, then the SWF sets its own map with `coop.keys`. Everyone presses arrows, A and S. Slot 0 sends the original codes; slots 1-3 send codes the game never reads otherwise, which go into each extra player's `button_*` fields. The engine keeps its keys on the player clip, so extra players only needed their own key fields.
- **The players:** one DoAction added after the game's own script in the game clip. Players 2-4 are tinted, with a HUD
  and a name each. Enemies go for their nearest player who is up. Boss hits land on every player in reach.
- **"The player":** the game finds its hero by the instance name `dude1`, a child clip. In Ruffle an AS2 stored
  property is found before a child of the same name, so the mod sets `game.dude1` to another player's clip for one
  call, then deletes it. Entry points are wrapped: player code runs for that player, enemy AI uses the nearest player
  who is up (kept 45 frames), boss hit tests run once per player.
- **Depths:** the game's depth counter is restored to a computed base: P1, or a boss's grab victim, or the first
  player up when P1 is down.
- **Enemy loops:** code that loops over enemies and then hits the player once gets an extra pass: called again with
  `dude1` = each other player and the loop counts (`total_kids`, `total_objects`) set to 0.
- **Down and up:** a player at 0 health lies down while someone else is up and gets up 6 s later with half health. Everyone down is the game's own game over.
- **Leaving:** `leave N` deletes that player's character, shadow and HUD, so an idle player can't hold the shared screen back.
- **Host option:** friendly fire, `--coop-option friendlyfire=1`. It was the first launcher setting (flash-games
  0754875): the settings list in `info.json` is copied by `update-catalog.ps1` into `catalog.json` "settings".
- **Camera lesson:** per-player cameras shipped as 1.3 and 1.4 and were removed; 1.5 is back to the shared screen.
- **Lab runs (hub level lab-3p+, up to Ruffle Together 1.0.3.8):** solo identical to the original on every frame;
  4 players with random keys identical twice; a bot run to the ending credits identical twice, also with a friend
  leaving; coop-lab 2/3/4 relay and direct in sync, also with friendly fire on and to the ending with a friend killed
  at 75 s.
- **Lab methods:** an in-SWF bot overrides `Key.isDown` per slot, and a lab-only fast-forward knocks out ordinary
  enemies every 6 s, so a 4-player run reaches the ending in about 9000 frames (the bots fight the bosses). Probe
  clips at depth 1041000+ are read with `COOP_DESCRIBE_AT`. Lab build variants force options, because replays never
  pass `--coop-option`. The host's mouse in a screen corner triggers lab-only actions. A coop-lab copy adds
  `--option` and `--leave-after`.
- **Not proven:** no two-window run of the mod itself (Ruffle Together's own session ran 2 real windows up to the
  park), no two-PC game, Flash Player untested.
- **Limits:** enemy health and kill goals are the original's, so 4 players clear levels faster.

## Lessons
- SWF 6 makes `Key.isDown` read-only: call `ASSetPropFlags(Key, "isDown", 0, 7)` before replacing it.
- In Ruffle an AS2 stored property wins over a child clip of the same name; set it for one call, then delete it.
- A scripted edit that replaced a span between markers silently deleted 5 functions. List the `^function` names
  after every scripted edit.
