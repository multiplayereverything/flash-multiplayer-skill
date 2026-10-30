---
name: flash-map
description: Map a Flash game's code before adding players for Ruffle Together - export the SWF with FFDec, find the one place each system runs through (frame loop, input, the player, camera, levels, menus, saves) and write CODE_MAP.md. Use after flash-start, before changing a SWF, or when you don't know where a game reads its keys or its player.
---

# Flash map

Paths here are relative to the hub root, two folders up from this file (`../../`), where `references/`, `tools/`, `templates/`, `games/` and `DIRECTORY.md` live.

1. Export (commands in `references/recon.md`): scripts, AS2 p-code when you need opcodes, `-swf2xml` plus
   `tools/swfmap.py` for obfuscated AS2 display trees, `tools/swfinfo.py` for frame labels. Keep exports in
   `decompiled/`, which is never published or copied into the mod's source.
2. For each system, find the **one** function or frame everything goes through, and confirm the shipped game calls it
   (a `trace` in a headless session is proof; reading code isn't).
3. Write `CODE_MAP.md` with the table in `references/recon.md`: system, where, notes. For Ruffle Together the ones
   that matter most:
   - **Input:** where the game reads keys (`Key.isDown`, key listeners, `on(keyPress)` buttons) and which key codes.
     That's the key map's `slot` lines.
   - **The player:** every place that reads "the player" (`_root.hero`, a class's single instance). Extra players
     need each of them to point at the right copy.
   - **Camera and screen edges:** what follows the player, culls off-screen objects or ends the level at an edge.
   - **Menus:** what starts the game (mouse, keys, keyPress buttons), so test scripts can get through them.
   - **Saves:** the SharedObject names; Ruffle Together keeps a co-op save per SWF.
4. List the original game's own script errors as you meet them, so they're never blamed on the mod.

Signs to note now, because they change the plan:
- An obfuscated AS3 game where game classes have subclasses: don't recompile those classes (`references/traps.md`, FFDec).
- `_root` functions defined on later frames or redefined: wrap them lazily every frame.
- SWF 6: case-insensitive names, no `try/catch` (`references/traps.md`, AS2).

Nothing about randomness or timers needs fixing: Ruffle Together makes them the same on every PC.

Next: `flash-lab`, then `flash-inject`.
