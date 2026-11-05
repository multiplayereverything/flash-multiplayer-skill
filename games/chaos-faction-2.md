# Chaos Faction 2 Online

Id `chaosfaction2`. Entry in [DIRECTORY.md](../DIRECTORY.md).

A platform fighter by Dissolute (Armor Games), AS2 SWF 8.

- **Path:** started as local multiplayer to online (the game's Keyboard 1 and Keyboard 2), then fighters 3-6 and the campaign were added to the SWF. Deathmatch is 2-6 players, the campaign 1-6. Survival stays single-player.
- **Key map:** built-in `chaos-faction-2`, `--coop-players 2-6`, Ruffle Together 1.0.5+. The game swaps player 1 between two key sets, so a session pins each player's codes in memory and leaves the saved bindings alone.
- **The players:** the campaign adds players 2..N on player 1's side before each level sets up. The build shifts every fixed fighter number in the level scripts by N - 1, and a level is lost only when every player is out. Anything that attached a fighter before the vs clip's first frame would break that shift.
- **Lab runs (Ruffle Together 1.0.5):** replays identical twice at 2, 4 and 6 players, including level 15 to the ending; 1 player identical to the original over 5000 campaign and 8000 Deathmatch frames; every level started and played with 3 players; every button of every slot changes the game; coop-lab relay and direct in sync at 2, 4 and 6 players; a friend killed at 75 s left the others in sync.
- **Not proven:** the two-window run was done on the 2-player build and wasn't repeated for 1.2. The run through level 15 uses a lab build that knocks enemies out. No two-PC game.
- **Limits:** only the host's mouse runs menus and picks the level, and only the host's Space pauses. NPC allies and enemies show off-screen pointers with fighter numbers N - 1 higher than the original.
