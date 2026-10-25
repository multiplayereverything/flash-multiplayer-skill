# Intrusion Online (in progress)

Relay id `intrusion`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Side-scrolling shooter, AS2 SWF 8, obfuscated. The game knows one soldier, `_root.knight`.

- **Path:** single player to co-op, up to 4.
- **Sync:** each player runs their own soldier locally and sends its pose; the host owns enemies, bullets, pickups and level flow. Each guest gets a stand-in object on the host that inherits the hero's prototype, so enemy code treats it as a player. Around each enemy, bullet and trigger update, `_root.knight` is swapped to the nearest living player. Damage, pickups and heals go back to their owner as events.
- **Build:** the game's scripts don't survive a recompile, so the mod is compiled in the game's spare `stop()` frame slots of a scratch copy, then its DoAction tags are spliced unchanged into the untouched SWF.
- **Status:** online panel on the main relay, lab passing; not released yet.
