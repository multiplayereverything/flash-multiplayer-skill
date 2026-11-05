# Fireboy & Watergirl in The Forest Temple Online

Id `fireboywatergirl` here, `fireboywatergirlforesttemple` in flash-games. Entry in [DIRECTORY.md](../DIRECTORY.md).

Oslo Albet's two-player puzzle platformer, AS3 with Box2D, SWF 9.

- **Path:** local multiplayer to online, exactly 2 players. Host is Fireboy, the friend is Watergirl. Each presses arrows or W/A/D on their own PC.
- **Key map:** built-in `fireboy-watergirl`: slot 0 `UP=38 LEFT=37 RIGHT=39 MENU=80`, slot 1 `UP=87 LEFT=65 RIGHT=68 MENU=80`. A file path and the built-in name count as different maps, so everyone has to switch together.
- **The players:** nothing added. The game already reads both sets of keys.
- **Build route:** only the ad, the hiscore loader and the sponsor links are stripped from the SWF.
- **Lab runs (Ruffle Together 1.0.3.6):** a 2000-frame script through menus, moving and jumping, pause from each slot, Watergirl dying in lava, Game Over and Retry. Replays identical 3 times, also with 15 ms jitter. Solo matches the original on every frame from 62 on; frames 0-61 are the preloader, where the ad box was. coop-lab relay and direct stayed in sync.
- **Not proven:** the script plays level 1 without finishing it, so level completion, saves and the ending were not reached. No two-window run, and no two-PC game.
