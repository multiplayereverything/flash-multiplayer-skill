# Bad Ice-Cream Online

Relay id `bic`. Entry in [DIRECTORY.md](../DIRECTORY.md).

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
  (the pop-in clip loops while the host is paused).
- **Lab:** host and guest windows, `--solo`, a control build without the ad fix that must fail, `--host-leaves`,
  `--delay 80 --jitter 40`, `--lobby` (plus `--drop`, `--host-leaves`, `--delay 80`) through the fake bridge, `--direct`
  (plus `--third`, `--host-leaves`, lag, a wrong version), `--third`, `--late-join`, `--help-hold 100`.
- **Lessons:** send the snapshot before the popup message; never switch a fruit's frame during its appear animation; drop snapshots left over from the previous level.
