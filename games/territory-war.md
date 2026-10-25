# Territory War Online

Relay id `tw`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Turn-based team artillery with sticks (Afro-Ninja, 2007), AS2 SWF 8.

- **Path:** local multiplayer to online. Red against blue on up to 4 PCs; each team's sticks are shared out in turn between that team's players.
- **Sync:** the host runs the real match and sends `SN` every frame (changed sticks, everything every 40 frames). On your turn you walk, aim and charge the power meter locally and send `AIM` and `FIRE`; the host checks the turn and fires through the game's own code.
- **Why:** `hitTest` and timer results can differ between players, so only one copy decides.
- **Build:** the mod is compiled into new DoAction tags on frame 3 (`InsertAction.java`); every original tag stays byte-identical. Frame 3, because the title stops there and tags on frame 4 never ran.
- **Hooks:** ten `_root.HUD*` functions wrapped lazily every frame (the game defines them later and redefines some on frame 522), and `_global.Key` replaced by a wrapper because Ruffle ignores `Key.isDown = f`.
- **Lab:** solo, 2 players, 3 players with a late joiner from the public list, vs CPU, wrong code, wrong version; host and guest compare a state hash at every turn start.
