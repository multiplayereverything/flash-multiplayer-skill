---
name: flash-lab
description: Prove a Flash game works in Ruffle Together without a human - the release exe with throwaway saves, input scripts, replays that must match twice, 1 player against the untouched original frame by frame, a run to the ending, the coop-lab with 2-4 players and a leave test, a check that every player can do everything, two real windows, then two real PCs. Use before and after every change to a co-op SWF or key map, before a release, or when a session desyncs.
---

# Flash lab

Paths here are relative to the hub root, three folders up from this file (`../../../`), where `playbook/`, `tools/`, `templates/`, `games/` and `DIRECTORY.md` live.

The method is in `playbook/ruffle-together.md` (Testing). Start from `templates/ruffle-together/`:
`example-2p.txt` (an input script), `replay_check.py` (two replays that must match), `solo_check.py` (1 player
against the untouched game) and `example.keys` (`python -I tools/keys_check.py` checks a key map).

Order, with what counts as passed:

0. **The release exe and throwaway saves.** Copy the Ruffle Together release you'll ship for into the mod's
   `tools/` folder and test only with that, never a test build or the launcher's live copy (several games had to
   redo their proof). Every run gets `--save-directory <temp>`; every window its own `--cache-directory`.
1. **The key map parses:** `python -I tools/keys_check.py game.keys`.
2. **A replay gets into play:** an input script through the menus (only the host's mouse drives menus: move one
   pixel off and back before each click, or the game's own keys), then each player moves. Save `--coop-shot`
   screenshots and look at them; a run that sat on the title screen also "matches".
3. **Twice identical:** `replay_check.py` with 1, 2, 3 and 4 players (as many as the game has; a replay has as many
   players as its key map has `slot` lines, so keep a map per count). Passed = the two outputs are byte-identical
   over a long run (the shipped games used 2700-6400 frames).
4. **1 player is the original** (path B): `solo_check.py` compares the mod with a 1-slot key map against the untouched SWF
   frame by frame. Passed = every frame matches, except frames where the mod's own menu button shows, and those are
   listed. Where the mod adds a clip from the start, compare `COOP_DESCRIBE_AT` dumps with the mod's clip left out.
5. **Play to the end.** Every level type and the ending, not just level 1: most games stopped at level 1 or one
   match and missed bugs there. Use a lab build that skips ahead or a start-level hook, or a bot run (Dad 'n Me ran a
   bot to its ending, 9100 frames).
6. **Every player can do everything** (path B): by reading the code and in the lab, enemies target every player,
   every player can pick things up, refill and use the game's actions, and nothing only the host can do blocks the
   others. Per-player aim reads `coop.mouseX/mouseY(slot)`: only the host's mouse reaches the game's own.
7. **2, 3 and 4 players** in `ruffle-coop/tools/coop-lab/lab.py`, through a local relay with lag and directly.
   Passed = every player `desync_at=none` and `closed=no`.
8. **Leave test:** kill one friend's process mid-run (for example at 75 s). Passed = everyone else stays
   `desync_at=none` to the end, and the game copes with that player standing idle (turn-based games: their turn
   must not stall).
9. **Two real windows** (`ruffle-coop/tools/coop-lab/windows_lab.py`): a desync is a fail. Late frames alone are not,
   if the untouched original shows the same on that PC (run it as the baseline; busy PCs make it flaky). Check
   device-font text here: headless runs draw it empty.
10. **Two real PCs** over the relay, real people playing. Only this makes the QA level `played-online`.

A run counts only with 0 script errors beyond the original game's own. Never use the user's keyboard or mouse; stop
only the processes the lab started; one lab port per mod.

Hub tools test themselves: `python -I tools/test_all.py` prints `ALL OK`.
