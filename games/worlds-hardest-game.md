# The World's Hardest Game Online

Id `worldshardestgame`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Snubby Land's single-player puzzle game (sponsored by Armor Games, 2008), AS2 SWF 8, 30 levels of one screen each.

- **Path:** single player to co-op, 1-4 players on one shared screen.
- **Version:** 1.1 (flash-games c911045, 2026-11-06, sha256 7bacc92e...), Ruffle Together 1.0.6+.
- **Key map:** `--coop-keys gun-mayhem-2 --coop-players 2-4`, Ruffle Together 1.0.6+. That map's `local` line already has arrows and WASD, so the SWF reads `coop.buttons(slot)` and needs no map of its own.
- **The players:** squares in their own colour with the player's name above. `ColorMatrixFilter` tints the squares and keeps their black outline. 1.1 moved the HUD at the user's request after real play: each player's name and deaths sit at the right of the top bar in their colour, in place of the game's DEATHS total, sized by player count. The list also shows on the continue and finish screens. The footer only shows `AT GOAL n/m`. The finish screen keeps the game's own TOTAL DEATHS for the team, leavers included.
- **Rules chosen for co-op:** each player has their own checkpoint. Coins are shared, and a player's coins go back when that player dies. A level ends when all coins are taken and everyone is in the goal.
- **Leaving:** a friend who leaves is removed and their coins stay taken.
- **Lab runs (Ruffle Together 1.0.6):** solo identical to the original on every frame; replays byte-identical at 2, 3 and 4 players; bots through all 30 levels to the finish screen at each count, also with a player retired; coop-lab relay and direct in sync; a friend killed at 60 s left the others in sync; 2 and 4 headless players on the live central relay; 2 real windows passed. All of these were repeated on the 1.1 bytes with the same results, and a new check found each player's deaths always add up to the game's total.
- **Not proven:** the bots don't dodge, so enemies are off in the runs to the ending. Nobody has beaten this build in co-op with enemies on. Deaths were tested on levels 2 and 6 only. Controllers are untested. The user reported 1.0 "works great" in a 2-player session, setup unknown, so it is not proven to be two PCs over the relay: QA stays lab-3p+. 1.1 hasn't been played by people.
- **Release note:** a launcher install that already has the game doesn't pick up a changed `*_online.swf` (its saved `catalog.json` is never written), so players must download it again. Checked from the code only.
- **Limits:** only the host can press menus and continue screens, so an idle host blocks them. A friend who stops playing holds up the level until they arrive or leave. The game's web buttons run on every PC and may open a browser on each.
