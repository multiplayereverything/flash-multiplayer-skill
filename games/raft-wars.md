# Raft Wars Online

Relay id `raftwars`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Turn-based artillery campaign (BubbleBox, 2007), AS2 SWF 8, obfuscated.

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
