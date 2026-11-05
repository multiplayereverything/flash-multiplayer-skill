# Dad 'n Me Online

Id `dadnme`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Tom Fulp and Dan Paladin's single-player beat 'em up, AS2 SWF 6, 45 fps.

- **Path:** single player to co-op, 1-4 players on one shared screen.
- **Key map:** started with `--coop-keys gun-mayhem-2 --coop-players 2-4`, then the SWF sets its own map with `coop.keys`. Everyone presses arrows, A and S. Slot 0 sends the original codes; slots 1-3 send codes the game never reads otherwise, which go into each extra player's `button_*` fields. The engine keeps its keys on the player clip, so extra players only needed their own key fields.
- **The players:** one DoAction added after the game's own script in the game clip. Players 2-4 are tinted, with a HUD and a name each. Enemies go for their nearest player who is up. Boss hits land on every player in reach.
- **Down and up:** a player at 0 health lies down while someone else is up and gets up 6 s later with half health. Everyone down is the game's own game over.
- **Leaving:** `leave N` deletes that player's character, shadow and HUD, so an idle player can't hold the shared screen back.
- **Host option:** `--coop-option friendlyfire=1`.
- **Camera lesson:** per-player cameras shipped as 1.3 and 1.4, and the owner chose to go back to the shared screen in 1.5.
- **Lab runs (up to Ruffle Together 1.0.3.8):** solo identical to the original on every frame; 4 players with random keys identical twice; a bot run to the ending credits identical twice, also with a friend leaving; coop-lab 2/3/4 relay and direct in sync, also to the ending with a friend killed at 75 s. The bot build knocks out ordinary kids every 6 s to shorten the run; the bots fight the bosses.
- **Not proven:** the mod itself had no two-window run of its own (Ruffle Together's session ran 2 real windows up to the park), and no two-PC game.
- **Limits:** enemy health and kill goals are the original's, so 4 players clear levels faster.
