# Chaos Faction 2 Online

Id `chaosfaction2`. Entry in [DIRECTORY.md](../DIRECTORY.md).

A platform fighter by Dissolute (Armor Games), AS2 SWF 8.

- **Path:** started as local multiplayer to online (the game's Keyboard 1 and Keyboard 2), then fighters 3-6 and the campaign were added to the SWF. Deathmatch is 2-6 players, the campaign 1-6. Survival stays single-player.
- **Version:** 1.2 (flash-games d19b8af, 2026-11-01), tested on the Ruffle Together 1.0.5 release exe. QA lab-3p+.
- **Key map:** built-in `chaos-faction-2`, `--coop-players 2-6`, Ruffle Together 1.0.5+. The game swaps player 1 between two key sets, so a session pins each player's codes in memory and leaves the saved bindings alone.
- **The players:** the campaign adds players 2..N on player 1's side before each level sets up. The build shifts every fixed fighter number in the level scripts by N - 1, and a level is lost only when every player is out. Anything that attached a fighter before the vs clip's first frame would break that shift.
- **Lab runs (Ruffle Together 1.0.5):** replays identical twice at 2, 4 and 6 players, including level 15 to the ending; 1 player identical to the original over 5000 campaign and 8000 Deathmatch frames; every level started and played with 3 players; every button of every slot changes the game; coop-lab relay and direct in sync at 2, 4 and 6 players; a friend killed at 75 s left the others in sync.
- **Not proven:** the two-window run was done on the 2-player build and wasn't repeated for 1.2. The run through level 15 uses a lab build that knocks enemies out. No game between two real PCs.
- **Limits:** only the host's mouse runs menus and picks the level, and only the host's Space pauses. NPC allies and enemies show off-screen pointers with fighter numbers N - 1 higher than the original.

## Lessons
- **Fixed fighter numbers** (`_root.all.p3`, `pID == 2`, `while(i <= 4)`): add the extra players before the level spawns anything, so they are fighters 2..N. Rewrite every fixed number of 2 or more to `n + offset` (offset N - 1) with a regex at build time. "Player 1 out, level lost" becomes "every player out" through a helper that equals the original when the offset is 0, so solo stays byte-identical.
- **Path A key sets that change by mode** (player 1 moves to `, / L .` in 2-player mode): after the game's `controls()`, pin its key variables to the map's codes, and replace `_root.controls`, since Settings calls it again.
- Idle test fighters get knocked out in seconds and drop their weapons: time single-button checks before first contact.
- Methods: `buttons_check` (press one button of one slot for 10 frames against a no-press run, and report the first frame whose fingerprint differs); lab-only coloured bars to read state in headless screenshots; a lab build that calls the game's own `die()` on every on-screen enemy every 60 frames to reach the real ending.
