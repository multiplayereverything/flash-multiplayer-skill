# My Friend Pedro (work in progress)

| | |
|---|---|
| Game | My Friend Pedro by DeadToast, published by Adult Swim; Newgrounds 641215 |
| Engine | AS2, SWF 7; one player kept in `_root` variables, one big `_root.onEnterFrame` runs the game |
| Path | B, single player to co-op: players 2-4 added on one shared world, each with their own camera and HUD |
| Sync | Ruffle Together 1.0.6 lockstep, no netcode |
| Status | WIP: not released, not committed. Directory id `myfriendpedro` |

Entry in [DIRECTORY.md](../DIRECTORY.md).

## The game
A side-on shooter where a banana talks you through each level. The game knows one player: about 50 `_root` variables
(position, speed, ammo, aim, state) and clips such as `_root.playerL`, all moved by one `_root.onEnterFrame`. The
camera is `_root._x/_y` itself, with the game's own clamps and shake.

## How the mod adds players: the register swap
- The game's `onEnterFrame = function` is rewritten to `mfpLoop = function`, so the mod decides when it runs.
- A frame-1 tick runs that loop once per player. Before each extra player's turn it swaps that player's ~50 variables
  into `_root`, and swaps `_root._x/_y` to that player's camera, so the game's own camera, clamps and shake work per
  player. After the turn everything is swapped back.
- Shared-world lines (the enemy loop, timers, depth raises) run only in player 1's turn (`if(mfpSlot==0)`).
- Clips that run their own scripts (reload frames, the HUD) find their owner's variables by walking `_parent` up to
  a clip tagged with a slot.
- Each player has a private HUD: a `duplicateMovieClip` of the game's HUD per slot, shown with `coop.hud` and
  `coop.only(slot, path)`. The fade and death overlay copy their alpha from player 1's HUD; level-end logic stays in
  the real HUD only.
- 1 player is the original: every helper returns the original's answer.

## Test method: the exit jump without bots
To reach the credits without a bot that can play: read each level's exit-trigger PlaceObject translate from
`-swf2xml` (twips / 20). In the lab build, find the `_root` child at that exact `_x/_y` and move a hero to the
centre of its `getBounds`, so the game's real trigger fires. Rotate which player does it per level.

## QA
Proven, all on one PC:
- 1 player = original: identical fingerprints over 1702 frames (menus into the talk). No fighting, older build.
- Direct session, 2 players, 4000 frames: in sync. Older build.
- Lab replay, 2 players, to the credits: with god mode and teleports to each level's real exit trigger.

Not proven:
- 3-4 players.
- The relay.
- A leave test.
- Replays matching twice.
- Death and retry without god mode.
- Lifts.
- Real windows (one run showed 29.4 of 32 fps).
- Two real PCs.

## Lessons
- In Ruffle a `_root` variable shadows a child clip of the same name: `_root.playerL = otherHeroClip` redirects all
  game code during a turn, so `delete _root.playerL` after the turn.
- Comparing clip references misses a new clip with the same name (a stale reference re-resolves by path), and
  `coop.hud` marks the object, not the path: call it every frame for clips re-attached under the same name.
- A level's `onEnterFrame` runs before that frame's own script: set up per-level copies only once the frame script
  ran (the mod waits for `typeof _root.crosshair.onPress == "function"`).
- A per-player private HUD is a copy of the game's HUD per slot plus `coop.hud` and `coop.only`; mirror overlays from
  player 1's HUD and keep level-end logic in the real one.
- FFDec exports `onClipEvent(load)` and `onClipEvent(enterFrame)` of one PlaceObject as separate files: a rewrite
  rule matched by folder hit the load script and broke import ("Parsing finished before end of file"); match the
  file name too.
