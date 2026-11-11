# Electricman 2 HS (2007)

| | |
|---|---|
| Engine | AS1/AS2, SWF 6, 640x400, 18 fps; 638 scripts, no wrapper, sitelock or obfuscation; a SharedObject save |
| Path | single player to co-op, 1-4 players on one shared screen |
| Sync | Ruffle Together lockstep, no netcode; `--coop-keys gun-mayhem-2 --coop-players 2-4` as the start map, then the SWF's own `coop.keys` |
| Build | 53 scripts rewritten as text from FFDec's export and compiled back with `-importScript`, plus one DoAction on frame 1 |
| Version | 1.1, flash-games cce0737 (1.0 was 0bafa6c, broken in real play); Ruffle Together 1.0.7 |
| QA | lab-3p+ on Ruffle Together 1.0.7: see below. Not played on two real PCs, a real keyboard or the live relay |

## The game
A one-screen arena fighter: one hero (`_root.em`) against a team of enemies (`m1..N`), a tournament of 19 matches over 6
rounds, ending with Death. Moves are read in one handler, and enemies test the hero's hit boxes against their own
position, so nearly everything that means "the hero" names `_root.em`.

## How the mod adds players
- Players 2-4 are `duplicateMovieClip` copies of the hero made when the fight's frame runs; Ruffle copies the clip
  handlers. Health bars and batteries are copies too. The aura clip asks a function for its colour, by the name of the
  hero it sits in.
- Each enemy keeps a target: the nearest hero who is up, changed only between its moves, with 60 px of hysteresis.
  "Was I hit" loops over every hero's boxes. A grabbed enemy belongs to the grabber.
- Values the game kept once on `_root` became per hero (who stands in front, grab candidate). Slow motion became a
  per-hero wish: the world is slow while any hero wants it, or a friend's idle frame would cancel it.
- Enemy totals (the win test) are read by one fixed clip, player 1's, even while player 1 is down. Letting "the first
  hero alive" read them could read a total no enemy had added to yet, and that is an instant false win.
- A hero out of health stays down until the match ends; the match is lost only when all are down. One extra enemy per
  extra player. Both are choices of the mod, not the game's.
- The score board's network form is hidden in a session, and a blank name on the new-player form becomes the host's
  room name, so a friend-less text box can't block the start.

## Lab runs (all on one PC)
- Solo = original over 6125 frames, plus 7 screenshots compared pixel by pixel. A whole solo tournament with the same
  god-mode code added to both the original and the mod: identical over 14119 frames, Death's ending included.
- Replays identical twice at 1-4 players. Coop-lab 2/3/4 through a local relay with lag and directly, in sync. Leave
  tests at 3 and 4. Two windows. Saving in a session and loading it in the next.
- The whole tournament through the real buttons to the ending at 2-4 players, with god mode on and fights cut short:
  that proves the path, not the balance.
- A counter of the moves each hero played: all 14 input-driven moves for every slot.

## 1.1 (2026-11-07, on Ruffle Together 1.0.7)
1.0 passed every lab above and was still broken in real play: wrong keys (a Ruffle Together bug, fixed in 1.0.7), and the game went
dead at the end of every fight and on leaving the training (`unloadMovie(this)`, in the original's lines too; guarded in the mod).
New in the lab: physical keys in real windows, checked by each hero's move, and whole scripts in real windows, the whole tournament
included. Both come out clean on 1.1.

Proven on Ruffle Together 1.0.7: physical keys in real windows at 2 and 4 players and solo, the whole tournament and lost
matches in real windows, replays, solo = original, coop-lab 2-4 through a relay and directly, leave tests.
Not proven: Ruffle Together 1.0.8 (stopped after only the 2-player keys test passed; the launcher record still says
1.0.7). Never played on two real PCs, a real keyboard or the live relay. The tournament run used god mode and short
fights, so the balance is unproven.

## Lessons
- A green solo fingerprint and good-looking screenshots hid two bugs: no player could press anything in a session, and
  1-player health bars never moved. See the traps with this game's name.
- Headless runs and replays miss an unload of the root: it runs as a future that `NullNavigatorBackend` drops. That
  covers any `loadMovie`/`unloadMovie` bug, so check those in a real window.
- When a key reached the slot but the move didn't happen, check the lab first: here the hero had drifted away from
  the probe enemy. Put the hero back on its spot when idle.
