# Bad Ice-Cream Online

Relay id `bic`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Tile arcade game for two (Nitrome, 2010), AS3 SWF 9, unobfuscated, from a Poki build.

- **Path:** local multiplayer to online. The game already had a 2-player mode on one keyboard; P2's keys now come from the network.
- **Sync:** the host runs everything. Every frame the state changed (and at least every 25 frames) it sends `SN`: wave, scores, a run-length ice grid, every entity's position and frame, and the sounds played. The guest runs no game logic: it applies the snapshot and draws. Guest input is `K|bits` on change and every 12 frames.
- **Why not lockstep:** `Math.random` and timeline scripts are everywhere, and update order decides kills and fruit.
- **Hooks:** patched copies of 5 game classes (input, level loop, controller, sound filter, the Poki SDK), compiled over the originals after `CheckNamespaces` showed no broken subclasses.
- **Also fixed:** the Poki build never started a level outside Poki's page (it waits for an ad), and froze a second in (a page call throws every frame).
- **Lab:** host and guest windows, `--solo`, a control build without the ad fix that must fail, `--host-leaves`, `--delay 80 --jitter 40`.
- **Lessons:** send the snapshot before the popup message; never switch a fruit's frame during its appear animation; drop snapshots left over from the previous level.
