# Intrusion 2 Online (in progress)

Relay id `intrusion2`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Side-scrolling shooter with Box2D ragdolls, AS3 SWF 9 (18 MB), partly obfuscated.

- **Path:** single player to co-op, up to 4.
- **Sync:** each PC runs its own hero (no input lag); remote heroes are real game heroes fed by the network's input and steered to the reported position (snap beyond 150 px). The host owns enemies, damage (replayed as `DM` through a gated `Damage()`), triggers and level flow.
- **Hooks:** around a remote hero's update, the game's own demo-input seam, mouse position, `world.hero` and the HUD are swapped and restored in `finally`. Enemies target the nearest living hero through one loop patch instead of 35 classes. The freeze area is the union of every player's view.
- **Build:** game classes are copied from the decompiled export at build time and patched there (an asserted edit list), so the mod's source has no game code; staging is case-sensitive because two classes differ only in case; a damage gate is inserted into 41 files by one rule.
- **Status:** 3-player lab passing (build, remote heroes, online screen); not released yet.
