# Gun Mayhem 2 Online

Relay id `gm2`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Platform brawler with local 4-player (KevinGu, 2012), AS2 code in a SWF 9 file.

- **Path:** local multiplayer to online, 2-4 players.
- **Sync:** input lockstep driven by the host. The host sends `F|frame|inputs` every frame, guests send theirs, a 2-frame jitter buffer absorbs lag, and the host waits only when a guest falls more than 15 frames behind. A full snapshot plus the RNG state goes out every 35 frames to repair drift.
- **Determinism work:** every `RandomNumber` opcode is replaced in p-code with a seeded Park-Miller RNG; spawn-time random rolls use a per-object RNG because Ruffle and Flash Player run an attached clip's first frame at different times; cosmetic effects use their own RNG; 8 sprites get a pause guard.
- **Input:** each online slot gets private key codes no real key makes, and each PC maps only its own keys into its own slot, so two slots bound to WASD don't move together.
- **Modes:** ONLINE (room codes) is the default; DIRECT (IP) is the second choice and is remembered only when picked.
- **Lessons:** never name an AS2 function `stop`; one build folder per run, or two builds wipe each other.
