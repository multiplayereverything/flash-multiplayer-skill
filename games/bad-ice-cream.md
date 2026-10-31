# Bad Ice-Cream Online

Relay id `bic`. Entry in [DIRECTORY.md](../DIRECTORY.md).

**Retired 2026-10-28.** The released `BadIceCream_online.swf` is now the game with only the level-start fix, played
online in [Ruffle Together](https://github.com/multiplayereverything/ruffle-together) (lockstep co-op inside Ruffle: only
key presses travel). The relay mod described below (host snapshots, F9 panel, DIRECT, the launcher lobby bridge)
isn't released any more; its lessons stand.

Tile arcade game for two (Nitrome, 2010), AS3 SWF 9, unobfuscated, from a Poki build.

- **Path:** local multiplayer to online. The game already had a 2-player mode on one keyboard; P2's keys now come from the network.
- **Sync:** the host runs everything. Every frame the state changed (and at least every 25 frames) it sends `SN`: wave, scores, a run-length ice grid, every entity's position and frame, and the sounds played. The guest runs no game logic: it applies the snapshot and draws. Guest input is `K|bits` on change and every 12 frames.
- **Why not lockstep:** `Math.random` and timeline scripts are everywhere, and update order decides kills and fruit.
- **Hooks:** patched copies of 5 game classes (input, level loop, controller, sound filter, the Poki SDK), compiled over the originals after `CheckNamespaces` showed no broken subclasses.
- **Also fixed:** the Poki build never started a level outside Poki's page (it waits for an ad), and froze a second in (a page call throws every frame).
- **Launcher lobby:** with `lobby=1` the same relay messages go through `LobbyBridge` to the launcher's bridge; no F9
  panel. `loaded` goes once the game is past its intro; the launcher's `go` is the guest's `J`. A dropped guest's P2
  stands still and gets the level again on `back`. Lobby version `2` (`bic-online 2`).
- **DIRECT** next to RELAY (MODE button; RELAY is the default and the mode is never saved): `H|`/`J|` on the relay's
  legacy room on the host's PC, no room code. The host admits a friend only after its version message (`VE|`) and
  answers a second friend with `FU|id`.
- **Fixed after release 2:** guest keys latched for 3 host frames (a tap was lost under jitter); a guest that joins
  from its preloader waits for its intro before loading the level; the guest runs fruit's per-frame update itself
  (the pop-in clip loops while the host is paused); snapshots are applied on arrival, between frames.
- **Sweep:** all 40 levels with random play on both sides stay in sync (lab, 2 players). Open: breaker attack
  clips' callbacks are fixed by doing the guest's frame switches in `Event.RENDER`; teleporting cherries follow
  the host's labels.
- **Flash Player 32:** both windows, either one mixed with Ruffle, and DIRECT pass the lab (28/28 each).
- **Launcher lobby:** played through the launcher's real lobby code (round, link drop and reconnect, host leaving).
- **Lab:** host and guest windows, `--solo`, a control build without the ad fix that must fail, `--host-leaves`,
  `--delay 80 --jitter 40`, `--lobby` (plus `--drop`, `--host-leaves`, `--delay 80`) through the fake bridge, `--direct`
  (plus `--third`, `--host-leaves`, lag, a wrong version), `--third`, `--late-join`, `--help-hold 100`.
- **Lessons:** send the snapshot before the popup message; never switch a fruit's frame during its appear animation; drop snapshots left over from the previous level.
