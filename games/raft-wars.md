# Raft Wars Online

Relay id `raftwars`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Turn-based artillery campaign (BubbleBox, 2007), AS2 SWF 8, obfuscated.

## Now: Ruffle Together (released build)
The game has no local multiplayer of its own (its two-player branch is dead code) and aims with the mouse, so the
mod adds local turn co-op with no netcode (`build.py --coop`, one file `coop.as`), and Ruffle Together puts it online.
- **Release:** 1.3, flash-games 6512f82 (2026-10-31). `--coop-keys gun-mayhem-2`, 2-4 players. Tested on Ruffle
  Together 1.0.4; not rechecked on 1.0.7 or 1.0.8.
- **Players:** the player count is the room's (`coop.players`). PLAYERS on the main menu starts there and can't go
  above it. 1 player = the original game, untouched.
- **Turns:** `operateCannon(1)` is wrapped; player turns rotate P1..PN. On your turn you aim with your own keys
  (up/down angle, left/right power, fire, ammo, from the `gun-mayhem-2` map) or your own mouse
  (`coop.mouseX/Y/Down(owner)`). Friends' mice stay in "host" mode, so nobody can press battle buttons on someone
  else's turn. A shared banner names the turn.
- **Shop:** each friend's click is hit-tested against the buy buttons and DONE and calls the game's own `onRelease`,
  so the game's prices and limits apply.
- **Leaving:** a friend who leaves is skipped (`coop.events` "leave N"). If they were aiming, the turn goes to the
  next player on that frame.
- **Lockstep:** Ruffle Together steps timers by one frame, so the game's `setInterval` timers (which call
  `Math.random`) fire on the same frame everywhere; the per-frame `random()` is synced too.
- **Proof:** `--coop-replay` identical twice and with jitter (the no-clock control differs); coop-lab with 2, 3 and
  4 players over the relay and direct, every player `desync_at=none`; leave tests (idle and mid-turn); windows_lab
  PASS. Solo = original: the replay's object dumps (`COOP_DESCRIBE_AT`) of the original and the co-op build are
  identical once the mod's own clip is left out.
- **Lab methods:** a lab-only build leaves the first battle like a win and opens the shop with credits, and traces
  the shop buttons' bounds; a headless session tool with `--leave N:SECONDS` (idle and mid-turn leave); per-count
  key maps (`gun-mayhem-2` cut to N slots).
- **Not proven:** two real PCs.

## Lessons
- Leaving in turn-based games: `owner = turn % players` hands empty slots turns and the game stalls; read
  `coop.events` and skip leavers.
- A PLAYERS menu that goes above `coop.players` stalls on the empty slots.
- Read `coop.events` in one place per frame: each call empties it.
- Mouse-aim proofs must target inside the aim range and log aim, mouse and cannon.
- The coop-lab's `lab.py` with a relative `--exe` prints nothing and exits 0.
- `lab.py` passes no `--save-directory`.

## Before: the relay mod

- **Path:** single player to co-op: 2-4 players on the brothers' raft, turns rotating through the room (host, P2, P3, P4, host...).
- **Connect:** ONLINE (room codes on the global relay) by default; a MODE button switches to DIRECT IP (`H|name`/`J|name` to the relay the host runs on their own PC). DIRECT is saved only when the player picks it. In a direct room the host checks the version (READY carries it) and the 4-player limit itself and answers `BYE|reason`, and guests end their session on `X`, because the legacy room does neither.
- **Sync:** host mirror snapshot every 2nd frame; guests play back 4 host frames behind with interpolation, plus effect and sound events. The turn owner aims locally (`AIM` at 10/s so others see it move, only values in the game's -60..60) and sends `FIRE` with the ammo; the host checks the stock. Shared credits in the shop: guests send `BUY`, the host applies the game's own cost and limit checks; the host presses DONE.
- **Why:** `random()` runs every frame and timers run on the wall clock, so lockstep is impossible. The game's versus mode is dead code.
- **Build:** FFDec's AS1/2 deobfuscator recovers frame 4 (the whole game); the build imports a new frame-5 script (the game's own 10 lines plus the mod) and wraps the game's timeline functions at runtime, so the obfuscated frame is never recompiled.
- **Hooks:** guests can't move the timeline themselves: `gotoAndStop` and friends are replaced and protected, and only the host's `GO|frame` moves it. The game's mouse listener is parked while the panel is open.
- **Leaving:** a player who leaves is skipped; if they leave while aiming, the host takes that shot.
- **Lab:** every scenario in RELAY and DIRECT: 3 players with a late join (mid-battle, in the shop, in the intro), 4 players plus a 5th refused, host leaving, guest leaving mid-aim, wrong version, 80+40 ms lag, solo, and the whole campaign end (win level 10, everyone reaches the ending); 0 script errors. Guests fire rockets and buy the raft upgrade, and a state check compares every object at each turn (0 px).
- **Bugs the lab found late:** when the dog on the upgraded raft sank, guests removed its parent clip (the whole penguin container) and lost every penguin; the state check listed penguins that had already sunk (an "intermittent" missing object); a guest streamed the enemy's leftover aim (315) at the start of its turn. Two of them stayed hidden because the lab dropped a FAIL that came after a PASS.
- **Real mouse:** `lab.py --realmouse` posts mouse messages to one guest's Ruffle window (the cursor never moves); the game's own listener aims and fires on every guest turn, and the host shows the aim live.
- **Traffic:** about 3 KB/s from the host per guest (17 snapshots/s at ~190 bytes).
- **Untested:** Flash Player 32 (no projector on the test PC), two real PCs.
