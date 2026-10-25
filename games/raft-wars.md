# Raft Wars Online

Relay id `raftwars`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Turn-based artillery campaign (BubbleBox, 2007), AS2 SWF 8, obfuscated.

- **Path:** single player to co-op: 2-4 players on the brothers' raft, turns rotating through the room (host, P2, P3, P4, host...).
- **Sync:** host mirror snapshot every 2nd frame; guests play back 4 host frames behind with interpolation, plus effect and sound events. The turn owner aims locally (`AIM` at 10/s so others see it move) and sends `FIRE`. Shared credits in the shop; the host presses DONE.
- **Why:** `random()` runs every frame and timers run on the wall clock, so lockstep is impossible. The game's versus mode is dead code.
- **Hooks:** guests can't move the timeline themselves: `gotoAndStop` and friends are replaced and protected, and only the host's `GO|frame` moves it. The game's mouse listener is parked while the panel is open.
- **Leaving:** a player who leaves is skipped; if they leave while aiming, the host takes that shot.
- **Lab:** 3 players with a late join, 80+40 ms lag, host leaving, solo: all pass with 0 script errors.
