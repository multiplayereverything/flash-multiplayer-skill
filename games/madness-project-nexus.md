# Madness: Project Nexus (Classic)

| | |
|---|---|
| Game | Madness: Project Nexus (Classic) by Michael Swain and Matt "Krinkels" Jolly; Newgrounds 592473 |
| Engine | AS2 classes, SWF 10 |
| Path | single player to co-op, 1-4 players |
| Sync | Ruffle Together lockstep, no netcode |
| Build | one DoAction on frame 1 replaces class methods on their prototypes at run time, only in a session of 2+ |
| Release | 1.4, flash-games `7e41e79`, `games/madnessprojectnexus/MadnessProjectNexus_online.swf` |
| Launcher | keys `stealth-hunter-2`, Ruffle Together 1.0.8 |

Entry in [DIRECTORY.md](../DIRECTORY.md). Directory id `madnessprojectnexus`.

## How the mod adds players
- No script is recompiled. One DoAction on frame 1 waits until frame 25's `_root` functions exist, then replaces
  class methods on their prototypes, and only when `coop.players > 1`. Solo is the original by construction.
- Friends are teammates copied from the leader, each with their own camera, HUD and reticle.
- A downed player gets up 8 s later while anyone is still up.

## QA
On Ruffle Together 1.0.8:
- Solo frame-identical to the original.
- Replays identical at 2/3/4 players.
- Coop-lab 2-4 through the relay and direct, plus the leave test: 32/32 players in sync.
- Physical keys and the arena name box pass in 2 windows and solo. 4 windows pass about half the time (likely lost
  focus).
- Bots that can't die and refill their clips finished every stage and reached the ending at 2 and 4 players, in
  separate runs on 1.2 to 1.4.

Not proven:
- Two real PCs, or any human player.
- One unbroken run through the whole story.
- The central relay, only run on 1.0.
- In a long bot run character parts grow to absurd scale. 1.0.8 stops the crash this caused, not the growth; cause
  not found.

## Process
- Of seven bot stalls, four were the bot, two were mod bugs and one was the game's own dead end. Dump what the game
  still counts before blaming the mod.
- Name empty clips `LAB<n>_<state>` and read them in `--describe` dumps to find a crash deep in a long replay.
- Long `--coop-replay` runs on a shared PC can fail with "memory allocation ... failed": check free commit memory and
  run them alone.
- The mod's own tools: a physical-keys lab (keys on the launcher line, held keys with real key-repeat timing, counts
  presses, logs foreground changes, retries after re-activating), a name-box lab, and one script that runs the whole
  release check.

## Lessons
- Patch an AS2 class without recompiling: one frame-1 DoAction replaces prototype methods only when
  `coop.players > 1`, after frame 25's `_root` functions exist.
- In AVM1 `undefined >= n` is true (it compiles to `!(a<b)`): a "sit out" check removed the leader.
- Never `attachMovie` at a fixed depth in the game's world: player 2's reticle at 100001 deleted a boss's retreat
  point. Use `getNextHighestDepth`.
- Copying a character with the game's replicate function left its weapons' `myOwner` undefined, which blocked doors,
  weapon swap and pick-up: set the owner on every copied weapon.
- `getInstanceAtDepth(NaN)` finds a clip in Ruffle, so a free-depth loop starting at NaN never ends: guard it, in a
  session only.
- Ruffle Together 1.0.6 took physical keys only from the launch line's `local:` line; 1.0.7+ also from `coop.keys`. On
  1.0.6 the mod counts a `coop.typed` character as that button held 4 frames (kept to avoid a re-release).
- A game text box can drop typed characters just because it is full (it holds 11, "Enter Name" is 10): clear it
  first.
- Ruffle desktop died with "thread 'main' has overflowed its stack" after ~1.5 h of a bot run: Lyon's stroke
  tessellator on a shape at absurd scale. Fixed in Ruffle Together 1.0.8.
