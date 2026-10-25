# Ultimate Crab Battle Online

Relay id `ucb`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Single-player boss-fight shooter, AS2 SWF 6, obfuscated (no functions worth hooking).

- **Path:** single player to co-op, up to 4 ships against the same crab, one shared HP bar and continues.
- **Sync:** each player flies their own ship locally and sends its pose every 2 frames; shots go to the host as events and the host spawns them for real. A "world mirror" sends every `_root` clip up to 7 levels deep, keyed by depth path (instance names differ between PCs), as a delta every 3 frames and in full every 68.
- **Late join:** a friend can join mid-fight and drops straight in.
- **Host leaves:** guests see "The host closed the room." and keep playing alone.
- **Lab:** host, guest and late guest (3 players): 37 of 37 checks; also with 80+30 ms lag.
- **Lessons:** setting `_x` inside a tween freezes it; looping decorations drift with fps; Ruffle's fps drops as more windows run.
