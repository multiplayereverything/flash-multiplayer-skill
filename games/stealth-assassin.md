# Stealth Assassin (2014)

| | |
|---|---|
| Engine | AS3, SWF 15, 720x560, one 5,900-line document class (`MainTimeline`) plus a `Guard` symbol class |
| Path | single player to co-op, up to 4 |
| Sync | each PC moves its own assassin; the host's game runs guards, alarms, bullets, damage, targets, mission flow |
| Build | patches on a fresh copy of the decompiled MainTimeline (22 asserted edits) + new classes via `AddClasses` stubs |
| Relay id | `stealthassassin`, protocol `sa-1`, star mode |
| QA | lab, 2-4 players with a late join, RELAY and DIRECT, 80 ms lag, solo control, a must-fail control run |

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
