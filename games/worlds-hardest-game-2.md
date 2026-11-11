# The World's Hardest Game 2 Together

Released 1.0: flash-games 1c1e46d, `games/worldshardestgame2/WorldsHardestGame2_online.swf`, proven on Ruffle Together
1.0.8, launch `--coop-keys gun-mayhem-2 --coop-players 2-4`. QA (hub level): lab-3p+.
Entry in [DIRECTORY.md](../DIRECTORY.md). The first game is [The World's Hardest Game](worlds-hardest-game.md).

The World's Hardest Game 2 (2008, Snubby Land; the copy used came from webdesignmuseum.org). AS2, SWF 9, 700x500,
30 fps, 50 one-screen levels plus a 4-level tutorial. Like the first game, but coins live on the player clip, keys open
doors in the wall clip, some levels have checkpoints, and there's a pause menu and 6 player colours.

- **Path B, 1-4 players, one shared screen.** The mod reads `coop.buttons(slot)`; it sets no key map of its own.
- **Run the game's own script per player.** The 37 player scripts come in 12 variants (goal on different checks,
  ordered checkpoints, tutorial, tip and finish exits), so instead of re-implementing movement (the first game's way),
  players 2-4 are `duplicateMovieClip` copies of the level's player, which carry the clip events. A rewrite keeps each
  original body for solo and adds a co-op body made by asserted regex substitutions: key reads go through the copy's
  own slot, the "ready to move" flag becomes clip-local, the goal test needs every player in the goal (and fires once),
  and the death count is kept per player too. Coins are taken by the first living player who touches them, and each
  coin's own give-back rule runs on its taker. The game's global "ready to move" keeps meaning "not paused".
- **Design choice:** a door opened by a key stays open for the level in co-op. The original closes every door on any
  death, which would close a door on a friend standing in it.

## QA
On the Ruffle Together 1.0.8 release exe: solo = the original over 5585 frames of random play with deaths; replays twice
identical with 2/3/4 players; bots (a path search over the game's own wall tests, enemies moved off) through all 50
levels to the finish screen with 2, 3 and 4 players, the 4-player run twice byte-identical; the team goal (one player
waiting in the goal with all coins doesn't end the level), per-player deaths adding up, coins going back on the taker's
death and a retired player's coins staying taken; coop-lab 2/3/4 relay (40 ms + jitter) and direct in sync; leave tests
with 2 and 4 players; 2 players on the live central relay; physical keys posted to 2 and 4 real windows on the launch
line and in solo, PASS; the HUD seen in 2 and 4 real windows.

Not proven: played by people, two PCs. The bots don't dodge enemies.

## Lab
Keys without clicks: a `--probe` build skips the preloader and menus to level 1, moves the enemies off the stage and puts
each player on an open spot, then traces button changes and movement starts. The lab posts key messages to each window
and checks that only that window's square moved, in the right direction.

## Lessons
- `duplicateMovieClip` copies carry clip events, so each copy can run the level's own script, rewritten once.
- A game typo in a reset path (a door reset on a misspelled path) must be allowed for by the rewrite's regex.
- Path-search bots must wait after a failed plan; per-level lab trackers should stamp items with a level id.
