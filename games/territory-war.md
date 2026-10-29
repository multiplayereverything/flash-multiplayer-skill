# Territory War Online

Relay id `tw`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Turn-based team artillery with sticks (Afro-Ninja, 2007), AS2 SWF 8.

- **Path:** local multiplayer to online. Red against blue on up to 4 PCs; each team's sticks are shared out in turn between that team's players.
- **Sync:** the host runs the real match and sends `SN` every frame (changed sticks, everything every 40 frames). On your turn you walk, aim and charge the power meter locally and send `AIM` and `FIRE`; the host checks the turn and fires through the game's own code.
- **Why:** `hitTest` and timer results can differ between players, so only one copy decides.
- **Build:** the mod is compiled into new DoAction tags on frame 3 (`InsertAction.java`); every original tag stays byte-identical. Frame 3, because the title stops there and tags on frame 4 never ran.
- **Hooks:** ten `_root.HUD*` functions wrapped lazily every frame (the game defines them later and redefines some on frame 522), and `_global.Key` replaced by a wrapper because Ruffle ignores `Key.isDown = f`.
- **Connect:** ONLINE (room codes on the relay) is the default every launch; MODE: DIRECT IP is the second choice. DIRECT sends `H|name` / `J|name` to a relay on the host's PC (the legacy room); the guest sends `HI|version` and the host answers a wrong version or a 5th player with `KICK|id|reason`, and a guest closes on `X` (the legacy room keeps it connected). Only the DIRECT addresses are saved, never the mode.
- **Turn menu:** the game shows the same turn menu on every PC; on someone else's turn it's covered and dimmed ("Waiting: Blue: Guest's turn"), the Options buttons stay usable.
- **Bug worth knowing:** the second match in a room handed the guest's sticks to the host. On the first frame at frame 500 the mod's onEnterFrame ran before the game's frame script and read the previous match's teams (the loser's empty). A match now starts on the second frame there.
- **Lab:** 19 scenarios in both modes (`tools/suite.sh`): solo, 2 matches in a row, 3 and 4 players with late joiners (the 3rd from the public list), a 5th refused, lag, guest leaves, guest quits through the game's menu (CPU takes over), host leaves, wrong code, wrong version, vs CPU, mods-info through `RELAY|1|INFO|tw`; turn scripts cover grenade, gun, kick, walk, jump, map view, cancel and skip. Host and guests compare a state hash at every turn start (keyed by match). 42 windows, 0 AVM errors.
- **Ruffle Together:** fits as hot-seat (shared keys, merged across slots; `--coop-keys territory-war`, 2-4 players). The coop SWF is the untouched game. Replays twice identical over 4400 frames; coop-lab in sync with 2, 3 and 4 players over the relay and directly; windows_lab over its late-frame limit at 40 fps (no desync). Released with Ruffle Together 1.0.3.4 as `TerritoryWar_online.swf` (flash-games a1698f6); the relay mod stays in the mod folder.
