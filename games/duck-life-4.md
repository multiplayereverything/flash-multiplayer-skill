# Duck Life 4 Together (in progress, stopped)

Directory id `ducklife4`. Entry in [DIRECTORY.md](../DIRECTORY.md). Nothing released; stopped by the owner on 2026-11-07.

Duck-training game (Newgrounds 590576), AS2 SWF 15, 49 fps. Path B: single player to local co-op for 1-3 players,
online through Ruffle Together 1.0.8. Lab port 7828.

- **Races** take no input: they run on the ducks' stats. Every player's duck runs, and the team's first duck over the
  line counts as "the player". Prize and unlock are shared; the race-end and podium code are unchanged.
- **Minigames:** 11 of 15 are played together on one screen. The 4 that run on one duck (dive, cannon zoom, the cliff
  that scrolls the world, trampoline score) are played one player at a time. Each turn calls `coop.keys` with a map
  that gives real keys only to that player's slot, so nobody else can trigger the game's `on(keyPress)` handlers.
- **Tournaments** are a 3-duck relay in the original: the team becomes P1's, P2's and P3's ducks.
- **"The player":** each run of statements that mentions `_root.duck` is repeated once per extra duck (see
  [build.md](../playbook/build.md), statement-level duplication). Solo is unchanged because the extra duck clips
  don't exist.
- **Lab:** one lab SWF for every minigame and race. The script's first line `move F 0` picks the frame; `lab.as`
  reads `coop.mouseX(0)` once loaded, sets up a trained team and does `gotoAndStop(F)`.

## QA
One 3-player replay of one minigame (run once). Not proven: the other 14 minigames, races, solo = the original,
replays identical twice, coop-lab, leaving, physical keys, real windows. Never played on two PCs.

## Lessons
- Four traps went to [traps.md](../playbook/traps.md): the NaN counter, replacing a state clip, FFDec exporting a
  carried-over clip only on its placement frame, and lab load.
- Too many parallel replays with object dumps, next to other sessions' labs, preceded a power loss on the PC. Run at
  most 2 at once.
