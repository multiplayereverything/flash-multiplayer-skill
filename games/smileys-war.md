# Smileys War (2007)

| | |
|---|---|
| Engine | AS2, SWF 8, 500x375, 35 fps; game code in main-timeline frame scripts and sprite frame-1 scripts; Macromedia V2 components (List, ComboBox) on the menus |
| Path | single player (one human against bots) to local multiplayer, 2-4 humans, played online through Ruffle Together |
| Sync | Ruffle Together lockstep: no netcode in the SWF; `--coop-keys smileys-war`; every player's mouse through the co-op API |
| Build | 3 new DoAction tags compiled by FFDec (`InsertAction`) at the end of 3 main-timeline frames; every original tag byte-for-byte (checked by the build) |
| QA | `--coop-replay` determinism, solo = original fingerprint check, coop-lab 2/3/4 players relay + direct, windows_lab; not played between two real PCs |

## The game
Side-view platform shooter: smileys walk (A/D), jump (W), aim and fire with the mouse, 9 weapons (1-9 or wheel),
on maps of polygons. Modes: Deathmatch, Rambo (one player is Rambo), Team deathmatch; an arena screen picks 2-6
players, the mode, the goal and the map, plus a Challenge campaign. Player 1 is the clip `smiley` (sprite with a
frame-1 script that sets its own `onEnterFrame`, `onMouseDown/Up` and a wheel listener); every other player is a
bot, `smiley_comp`. Frame `create_players` attaches `smiley0` and then the bots as `smiley1..n`, and every bullet,
explosion and pickup loops over `"smiley" + i`, so any clip named that way is a player to the game.

## How the mod adds players
- A HUMANS 1-4 button on the arena screen (drawn by script next to the player count, removed when the screen
  changes). Humans take the first bot slots; bots fill the rest. Challenges stay one human.
- A controller clip (only with 2+ humans) waits until bot k has run its own setup, then replaces it with the human
  sprite at the same name and depth, copying tag, team, rambo flag and spawn point. When the new clip's own
  frame-1 script has run, the controller swaps its `onEnterFrame` for a copy of the human code with per-slot keys.
  Waiting for the clip's own setup (`onEnterFrame` and `guns_ammo` defined) avoids the "when does an attached clip's
  frame 1 run" question entirely.
- The game's camera follows player 1's mouse; with 2+ humans one shared view follows the middle of the living
  humans (same target point and easing). A camera per PC is not possible in lockstep.
- Aim goes through one function: in a session, `ExternalInterface.call("coop.mouseX"/"coop.mouseY"/"coop.mouseDown",
  slot)` for every slot (player 1 included); keyboard aim (an angle turned with two keys) as the fallback, switched
  by input only, so every PC switches on the same frame. `coop.localSlot` only adds "YOU" to a label's text.
- With 1 human nothing runs in a match: a scripted solo run gives the same fingerprint as the original on every
  frame except the arena screen while the HUMANS button is shown.

## Lockstep traps found
- **Sound clips removed in `onSoundComplete`:** each effect plays on a fresh empty clip that the game removes when
  the sound ends. When a sound ends depends on each PC's audio device, so the stage differs (a real two-window
  desync of the untouched game). Headless replays never see it (no audio, sounds never end). Fix: the mod's
  `sound()` leaves the empty clip; the game recreates the container at every map load.
- **V2 component menus in two real windows:** one List row's highlight clip ended 1 px apart on the arena screen.
  Cause not established (Ruffle Together steps timers per frame); setting the global styles `openDuration` and
  `selectionDuration` to 0 (no menu animation) made the next runs pass.
- `hitTest(x, y, true)` against map polygons is fine (geometry, same build on every PC).
- Headless replay draws no device-font text: labels in `_sans` only show in a real window.

## Lab tricks
- A lab-only probe: empty clips whose `_x/_y` are each player's kills and deaths, read from the display-list dump
  (`COOP_DESCRIBE_AT`), since traces don't reach the replay log. It proved human-vs-human kills (keyboard aim and
  per-slot mouse) and bot scoring.
- Clicking a V2 ComboBox in a script: open it, then click the row at 22.6 px steps below it.
