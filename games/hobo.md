# Hobo Online

Id `hobo`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Seething Swarm's single-player street brawler (Armor Games, 2008), AS1/AS2 SWF 6, 20 levels.

- **Path:** single player to co-op, 1-4 players on one shared screen.
- **Key map:** started with `--coop-keys gun-mayhem-2 --coop-players 2-4`, Ruffle Together 1.0.3.9+, then the SWF sets its own map with `coop.keys`. Everyone presses arrows, A and S.
- **The players:** every script names the hero `_root.hobo`, so a build tool rewrites the 1591 scripts that mean "the hobo" (FFDec export, text rules, FFDec import). With 1 player every rewritten script reads what the original read. Re-importing all 5368 scripts unchanged first proved recompiling was safe.
- **Screen:** walking scrolls the whole world, not the hero. A scroll that would push a friend off screen is refused, and with 2+ players the camera eases to the players' middle height.
- **Down and up:** at 0 health, with anyone else up, a player lies down for 8 s and gets up with half health. Everyone down is the game's own GAME OVER.
- **Leaving:** `leave N` removes that player and their HUD.
- **Lab runs (Ruffle Together 1.0.3.9 and 1.0.4):** solo identical to the original on every frame; replays identical at 2, 3 and 4 players; coop-lab relay and direct in sync; a friend killed after 60 s left the others in sync. Bot runs with a health floor went through levels 1 to 12.1 and 19 to 20.2.
- **Not proven:** the ending in co-op. The bot can't beat two scripted fights (the bench enemy at 12.1 and the dump-truck boss at 20.2). Nothing in the mod is known to block them. No two-window run, and no two-PC game.
- **Limits:** only player 1 triggers the stage-clear walk, as in the game's level script. Enemy numbers and health are the original's.
