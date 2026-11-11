# Stealth Assassin (2014)

| | |
|---|---|
| Engine | AS3, SWF 15, 720x560, one 5,900-line document class (`MainTimeline`) plus a `Guard` symbol class |
| Path | single player to co-op, up to 4 |
| Sync | release: lockstep in Ruffle Together, no netcode, 2-4 assassins, one per player, count from `coop.players`; the older relay mod is kept as a separate build: each PC moves its own assassin; the host's game runs guards, alarms, bullets, damage, targets, mission flow |
| Release | flash-games a26c0ce (`games/stealthassassin/StealthAssassin_online.swf`), tested on Ruffle Together 1.0.6, `--coop-keys stealth-assassin` (the API needs 1.0.3.7+) |
| Build | patches on a fresh copy of the decompiled MainTimeline (22 asserted edits) + new classes via `AddClasses` stubs |
| Relay id | `stealthassassin`, protocol `sa-1`, star mode |
| QA | release: lab-3p+ (see below); relay build: lab, 2-4 players with a late join, RELAY and DIRECT, 80 ms lag, solo control, a must-fail control run |

## Local co-op for Ruffle Together (first released 2026-10-29)
The game has no local multiplayer, so Ruffle Together had nothing to sync. The mod adds it, reusing the relay mod's
hooks with the network parts taken out (the same 22 patches point at a `CoopSA` class instead of `NetSA`):
- A PLAYERS 1-4 button on the mission menu. With 1 nothing changes: a scripted Tutorial run gives byte-identical
  screenshots on the original and the mod.
- P1 keeps arrows + Z + X; P2 W A S D + T + Y; P3 and P4 on the numpad (`--coop-keys stealth-assassin`). The extra keys are stopped before the game's handler, which also reads WASD for P1.
- Each extra assassin is a real game character moved by the game's own movement rules; the relay mod's per-guard
  swap makes guards see, chase and shoot it. One extra target per extra player; the game is over only when all are dead.
- Lockstep rules kept: no wall clock, pixel reads, sounds or Dictionary; `for each` only over arrays.
- Replays start with an empty save, so only the Tutorial is open: the lab build unlocks Easy before the menu.
- Text in a device font (`_sans`) is not drawn in `--coop-replay` screenshots; check it in a real window.
Proof: `--coop-replay` twice identical for 1-4 players; coop-lab relay and direct 2/3/4 players, 2700 frames, no
desync; windows_lab quiet and pressure pass (an idle PC matters: other labs on the same PC fail it, a known-good game too).

## What the first release got wrong (fixed 2026-11-06)
- **"Everyone moves the same player."** Co-op needed a click on the PLAYERS button; nobody clicked, the count stayed 1,
  and slot 1's WASD moved player 1 because the original game reads WASD too. The count now comes from `coop.players`,
  so the button only exists outside a session. A group with no save also had only the Tutorial, where extras never
  spawned: a session now opens Easy, and extras spawn in the Tutorial.
- **"The police go into the walls."** A guard that loses sight walks a straight line to the target's position at that
  moment. That is safe with one player, who has only just left view. Pointing each guard at the *nearest* assassin
  broke it: the nearest could be behind a wall, so sight was "lost" at once and the line ran through walls. A guard now
  changes target only to an assassin it can see within the game's own sight distance, and a wall on that walk ends
  the chase through the game's own routine. A lab-only trace that logs each guard entering a wall went from 3-5 entries
  in a run to 0, and the game's own logic gave 0 as the control.
- More targets: one extra per extra player plus one more, in co-op only. A friend who leaves (`coop.events`) drops as a body.

QA of the release (lab-3p+, Ruffle Together 1.0.6): replays twice identical at 2, 3 and 4 players; a 1-slot replay
byte-identical to the original; coop-lab relay and direct at 2, 3 and 4 players with no desync; a friend-leaves run;
windows_lab quiet and pressure pass.
Not proven: play between two real PCs on this build; the body left by a leaving friend wasn't seen on screen; only
Ruffle Together 1.0.6 was tested.
Possible issue, likely but NOT checked (from reading the code only): an unlock done for a co-op group with no save also
changes saved progress. That goes to the co-op save, not the solo save.

## The game
Top-down stealth: walk to the green target without being seen, touch it while moving to stab it, then reach the
escape that opens. Guards patrol, see in a 45° cone (186 px), chase, follow footprints and shoot; any guard that
sees you starts the alarm. Levels are data (`guardData()`, `tileData()`), single screen, `checkTile(x,y)` for walls.

## How the co-op works
- **One swap covers the AI.** The whole AI is one 2,400-line loop that reads `this.assassin`. At the head of each
  guard's turn (and of the touch loop) the mod sets `this.assassin`, `moving`, `cloakMode` and `health` to the
  nearest living player (the host's own assassin or a puppet `Guard` driven by a friend's poses) and restores them
  after the loop. Vision, chase, aim, alarms and touches all work for every player with two hook lines.
- **Damage to a puppet** happens in the host's game against a stand-in `health` of 99; on restore, the difference
  goes to the owner as `HT|run|slot|n` (0 = point blank, dead).
- **Extra targets** are more target guards (type 3) flagged `netExtra`; while one updates, `this.target` is swapped
  to it so the original target code walks it. Only the last target goes through the game's own kill (body, body
  search, escape); the others drop a body and leave the array. Spots come from the level: next to guard start
  points, in sight of them, on open floor, away from the player start and other guards.
- **Guests** skip the AI loop, ease guards to the host's snapshots (15/s), draw the host's bullets (`B`), and replay
  the host's kills by putting a stand-in assassin on the target for one touch check (`KT`), so the game's own kill
  animation and escape run on every screen.
- **Deaths:** `fail()` asks the mod first. A player who dies while a teammate lives leaves a corpse, loses input and
  watches; the game's own fail screen comes only when everyone is dead or time runs out (`GO`).

## Lab
`shared/lab/lab_runner.py` in the mod folder: a local hub relay on the mod's port, host + guests + a late joiner +
a wrong-code window, scripted through `LB|DO|seq|cmd` / `LB|RE|seq|...` (STATE, WALK, TP, GUARD, GOD, SNAP).
Checks: same mission on every screen (mission, target and guard counts), each sees the others move, guards within
3 px across screens, a real guard spots and shoots a guest's puppet, every target dead everywhere, a guest at the
escape completes the mission for all, the next mission follows, one death is not game over, all dead is.
A lab-only "god" flag keeps players alive through the shooting steps (hits are still counted).

## Lessons
- FFDec 26 can't recompile its own `§§goto(addrNNNN)`; when the label sits right after the loop it's a `break`.
- A menu frame script that resets the level command (`goto = 0`) eats a command sent during the intro: repeat it
  until the screen changes.
- Replaying a host event inside the game's own check must keep the request until the check really runs.
- Lab screenshots: take pending ones before starting a new window (window start can block for seconds).
- Lab-only switches through `--coop-option` and `coop.option(name)`, compiled only into the lab build: `GOD=1` (refill
  health), `ALL=1` (unlock every mission), `SOLO=1` (force the game's 1-player logic inside a session, as a control).
  Trace lines from a lab build come out on a headless session's stdout.
