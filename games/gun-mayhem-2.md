# Gun Mayhem 2 Online

Relay id `gm2`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Platform brawler with local 4-player (KevinGu, 2012), AS2 code in a SWF 9 file.

- **Path:** local multiplayer to online, 2-4 players.
- **Sync:** input lockstep driven by the host. The host sends `F|frame|inputs` every frame, guests send theirs, a 2-frame jitter buffer absorbs lag, and the host waits only when a guest falls more than 15 frames behind. A full snapshot plus the RNG state goes out every 35 frames to repair drift.
- **Determinism work:** every `RandomNumber` opcode is replaced in p-code with a seeded Park-Miller RNG; spawn-time random rolls use a per-object RNG because Ruffle and Flash Player run an attached clip's first frame at different times; cosmetic effects use their own RNG; 8 sprites get a pause guard.
- **Input:** each online slot gets private key codes no real key makes, and each PC maps only its own keys into its own slot, so two slots bound to WASD don't move together.
- **Modes:** ONLINE (room codes) is the default; DIRECT (IP) is the second choice and is remembered only when picked.
- **Waits:** a wait (stall or pace) only skips the scripts; every timeline that gates gameplay keeps playing unless the mod holds it. The mod holds the guns, crates and power-ups (pickable from their timeline frame 20, started by a child clip's `_parent.play()`), the last-survivor countdown (its last frame sets `gamewin`), the arena loop and the roulette. The hard part is telling whether a held clip was playing: a gun told to fire this tick is still on its idle frame, so it counts as playing only if it was already sitting there last tick (a reload that jumps back to the idle frame cancels the shot's `play()`). During a match, cosmetic effects get their own depth band so the game's spawn counter `pDepth` stays the same on every PC.
- **Players joining and leaving:** only friends that got the match start count for waits (a friend joining mid-match froze the host forever) and play from the next match. When the global relay closes a friend's socket after the host left, the friend ends the match itself (stats screen).
- **Lab:** self-playing builds, a per-frame trace from every PC and a diff that keys frames by match seed. A one-frame difference is a frame script that ran during a wait (it heals next frame); a difference on the same field for two frames, or a checksum desync, fails. Knobs: late joiner, rematch on the next map, trace past frame 1200, spawn names per frame. 3 and 4 players, two matches with a late joiner and a host leaving all run with 0 desyncs, and posted key presses move only the presser's player (one PC, Ruffle).
- **Lessons:** never name an AS2 function `stop`; one build folder per run, or two builds wipe each other; never edit a bash lab script while it runs (bash reads it as it goes).
