# Bow Man Online

Relay id `bowman`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Two archers taking turns, AS2 SWF 6 (38 KB).

- **Path:** local multiplayer to online, 2 players, one archer each.
- **Sync:** events only. The shooter sends `FIRE` with angle and power; both games fly the same arrow; the host sends `LAND` with the true position, frame, HP and wind, and the guest corrects. Positions are rounded the way Ruffle stores `_x` (twips), or hit tests differ.
- **Build:** export the frame scripts, patch a few with strings that must match exactly once, append the mod to frame 1, import. The SWF stays version 6: raising it makes `undefined + 1` NaN and the arrow counter breaks.
- **SWF 6 traps:** identifiers are case-insensitive (`var n` overwrote `N`), there's no `try/catch` and no `getNextHighestDepth`; a regex rename once rewrote the relay's `"L"` string and guest departures were ignored.
- **Flash Player:** refuses XMLSocket from a local SWF 6 file, so this mod is Ruffle only.
- **Lab:** 7 scenarios through a local relay.
