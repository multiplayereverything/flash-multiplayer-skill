# Smileys War (2007)

| | |
|---|---|
| Engine | AS2, SWF 8, 500x375, 35 fps; game code in main-timeline frame scripts and sprite frame-1 scripts; Macromedia V2 components (List, ComboBox) on the menus |
| Path | single player (one human against bots) to local multiplayer, 2-4 humans, played online through Ruffle Together |
| Sync | Ruffle Together lockstep (1.0.6+): no netcode in the SWF; `--coop-keys smileys-war`; every player's mouse, camera and HUD through the co-op API |
| Build | 3 new DoAction tags compiled by FFDec (`InsertAction`) at the end of 3 main-timeline frames; every original tag byte-for-byte (checked by the build) |
| Release | flash-games f5a0aea, `SmileysWar_online.swf` (sha256 acdf7856...353a); tested only on Ruffle Together 1.0.6, not 1.0.7 or 1.0.8 |
| QA | lab-3p+: `--coop-replay` twice with jitter, solo = original fingerprint check, coop-lab 2/3/4 players relay + direct, a mid-match leave, windows_lab; never played between two real PCs |

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
- The world stays at (0,0) and every slot gets `coop.camera` each frame, with the game's own easing and lead towards
  the aim. `coop.hud` keeps the HUD, background and countdown on screen. The game shows only terrain pieces touching
  a hidden `_root.screen` clip, so that clip is made huge: which pieces show must not depend on one player's camera.
- Each PC's HUD shows its own player: the game's HUD script also decides who won, so it still runs, then the mod writes
  the local player's numbers over its text, the health bar's width and an alpha (the sync check compares none of them).
- HUMANS starts at `coop.players` and cycles 1..that; the total player count rises to HUMANS if it was set lower.
  Replays report the key map's slots (4), not the players in the session.
- A friend who leaves (`coop.events`): the game's bot sprite is attached at the same name and depth, with tag, team,
  flags and position as its init object; the player's name and score go back on the board after the bot's frame-1
  setup overwrites them. A slot that left stays a bot in later matches.
- Aim goes through one function: in a session, `ExternalInterface.call("coop.mouseX"/"coop.mouseY"/"coop.mouseDown",
  slot)` for every slot (player 1 included); keyboard aim (an angle turned with two keys) as the fallback, switched
  by input only, so every PC switches on the same frame. `coop.localSlot` only adds "YOU" to a label's text.
- With 1 human nothing runs in a match: a scripted solo run gives the same fingerprint as the original on every
  frame except the arena screen while the HUMANS button is shown.

## Lockstep traps found
- **Two desyncs this game found, both fixed in Ruffle Together 1.0.3.5:** clips removed in `onSoundComplete` (sounds
  now end on the frame clock) and a V2 List highlight 1 px apart (`_xmouse` now ignores window size). The mod's
  workarounds came out again: keeping the clips made "1 human = the original" fail once sounds really ended.
- **A still cursor under a camera:** Ruffle converts a cursor through the camera only when it moves, so a still
  mouse keeps its old game position while the camera follows the player. The mod remembers the offset from the
  camera when the value changes and aims at camera + offset, so the crosshair stays put on screen as in the original.
- **Shots use last frame's aim:** the game turns the gun after it fires. A scripted shot needs a mouse move the
  frame before, and check for terrain in the way before blaming the aim.
- `hitTest(x, y, true)` against map polygons is fine (geometry, same build on every PC).
- Headless replay draws no device-font text: labels in `_sans` only show in a real window.

## Lab tricks
- A lab-only probe: empty clips whose `_x/_y` are each player's kills and deaths, read from the display-list dump
  (`COOP_DESCRIBE_AT`), since traces don't reach the replay log. It proved human-vs-human kills (keyboard aim and
  per-slot mouse) and bot scoring.
- Clicking a V2 ComboBox in a script: open it, then click the row at 22.6 px steps below it.
- A copy of the coop-lab with `--leave-after` and a temporary `--save-directory` per player for the leave test.
- A lab build that treats a slot holding QUIT as leaving, to check the bot takeover in `COOP_DESCRIBE_AT`.
- Mouse aim under `coop.camera` in a replay: the script's mouse is a raw world point. Move it one pixel the frame
  before each press, and check for terrain in the line of fire.
