# Strike Force Heroes Together

Released 1.0: flash-games ae89473, `games/strikeforceheroes/StrikeForceHeroes_online.swf`, 2-4 players, Ruffle
Together 1.0.8, launch `--coop-keys gun-mayhem-2 --coop-players 2-4`. QA (hub level): lab-3p+.
Entry in [DIRECTORY.md](../DIRECTORY.md).

Strike Force Heroes (Sky9 Games, 2012). AS3, SWF 10, 800x600, 30 fps, Box2D. Path B: single player to co-op.

## Recon
- Light control-flow junk in FFDec's plain export; `-config autoDeobfuscate=1` exports clean source that recompiles to
  the same game: 16 core classes recompiled unchanged gave a replay identical to the original over 3248 frames. So the
  build patches game classes at build time (`templates/build/build_as3_patches.py`, regex edits that assert counts).
- Every match already has AI soldiers, so friends are more soldiers. Campaign scripts address bots by index, so friends
  are added after every bot.
- The game's "human" flag is true only for the player, in about 50 checks. Some are gameplay (damage scaling,
  semi-auto, the AI's auto-swap); most are player 1's HUD, save, camera shake and tutorial triggers. Friends are human,
  and those player-1 checks become a type test for the game's own player class.

## Players
- Player 1 keeps the game's own input (keyboard events, the host's mouse). The SWF sends its own map with `coop.keys`:
  slot 0 = the game's real keys, slots 1-3 = codes the game never reads. Friends are moved from `coop.buttons(slot)`
  and `coop.mouseX/Y/mouseDown(slot)`; a still mouse keeps its screen offset from that friend's camera.
- Friend k's soldier is the host's saved class k places after the host's (own guns, skill, streak, level) or the
  mission's class, on the host's team, with a copy of the host's campaign extras (spawn shifted 30 px per slot).
- A leaver's soldier dies once and never respawns.

## Screens
- `coop.camera` per slot: the game's camera keeps following player 1, friends' cameras centre on their soldier,
  clamped to the map.
- Effects, particles, pickups and mines are painted into one stage-size bitmap in player 1's screen coordinates. Each
  friend gets a bitmap of its own at its view, the paints are copied in, and each PC shows only its own (alpha). Which
  effects are made = on any player's screen; screen sounds = on this PC's player's screen.
- The HUD is moved to the root once the game is on stage and pinned with `coop.hud`; a panel of the mod's own covers
  player 1's numbers on friends' PCs (text and graphics only).

## QA
Replays twice identical with 2/3/4 players; 1 player = the original (3248 frames); a "view N" build (slot 0's camera
shows slot N's view) equals the real build frame for frame; every button of slots 1-3 changes the game on the frame it
is pressed. Sessions with 2/3/4 players on a local relay with lag and direct, no desync; 4 players with one killed at
50 s, no desync. The whole campaign (15 stages and the ending) in a 2-player relay session and 4-player replays, with a
lab build that ends each mission as won 300 frames in (not played). Two real windows: campaign stages 1-3 in sync;
physical keys posted to both windows on the launch line: every key of host and friend works, and the launch map's keys
and other slots' codes do nothing.

Not proven: physical keys for players 3-4 in windows, the central relay, two PCs.

## Lessons
- Removed clips kept running game code until garbage collection and desynced the menu after a match (traps.md).
- One key code Ruffle lacks (F1) made it refuse the whole `coop.keys` map, silently.
- An rng trace build (one `Math.random()` traced per frame on every PC) found the intermittent desync in two runs.
