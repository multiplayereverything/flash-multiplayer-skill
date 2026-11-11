# Portal: The Flash Version Together

Released 1.0: flash-games 946dc3a, `games/portalflash/PortalFlash_online.swf` (SHA-256 `efc7ec4f...`), 2-4 players,
minimum Ruffle Together 1.0.8, launch `--coop-keys gun-mayhem-2 --coop-players 2-4` (the SWF sets its own map with
`coop.keys`). QA (hub level): lab-3p+. No launcher record yet. Entry in [DIRECTORY.md](../DIRECTORY.md).

Portal: The Flash Version (We Create Stuff, 2007), version 1.1.1, the Web Design Museum's copy. AS2, SWF 8, 45 fps,
800x450, no wrapper, no obfuscation. A single-screen puzzle game: one frame-5 script runs everything; the physics
objects are the player and the boxes, with the player special-cased.

- **Path B.** Players 2-4 are `duplicateMovieClip` copies of the player with its own clip script. A swap function sets
  the variable `_root.p1` to player k (found before the clip of the same name) and loads that player's own globals
  (carried box, reload, health, alive, death reason, walk-in), so the game's own code runs for each player. The rewrite
  wraps every "the player" block of the frame loop in a loop over players, and runs the game's portal, step and map
  functions for players 2-4 with the swap.
- **One portal pair for the team:** anyone shoots either colour and the last shot wins. Chambers are designed for one
  pair, and the game's portals, wall holes, masks, steps, balls, turret rays and teleport all assume exactly one.
- **The team:** one death restarts the chamber for everyone; a player at the exit waits hidden inside the door; the
  chamber ends when everyone is through. One box each; grabbing a box a friend holds takes it.
- **Mice:** each player's own mouse through `addProperty` getters, read at the same moment the original reads its
  mouse (traps.md).

## QA
Lab-tested on one PC: replays 2/3/4 identical, solo = the original, coop-lab 2/3/4 relay and direct, a leave test, every
chamber to the credits with 2-4 players (a lab walks the players to each exit), two real windows, physical keys in real
windows.

Not proven: the live relay, two PCs, people playing it.

## Lab
The lab build takes commands through player 2's mouse (x = 799, y = the command number; no menu reads it). The mod's
own tools find the frame of each `# @name` mark in an input script, read lab probes from `COOP_DESCRIBE_AT` dumps, and
gate on memory and the number of Ruffle processes. A chamber scan stores each level's counts of boxes, buttons,
turrets, doors and so on in an empty clip's position, to pick the rooms for "every player can do everything".

## Lessons
- FFDec can't recompile the game's own big `if`: split its body into `_root` functions (traps.md).
- "The exit waits for everyone" needs a once-a-frame check, or a leave by the last player in the room hangs the level.
- Count level restarts in long lab runs: a run can stay in sync while looping in one chamber.
