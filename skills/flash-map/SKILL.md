---
name: flash-map
description: Map a Flash game's code before modding it: export with FFDec (scripts, p-code, display tree, deobfuscated copies), find the one place each system runs through (frame loop, level load, player and input, enemy targeting, damage, pickups, win and lose, randomness, timers, pause, saves, sounds), and write CODE_MAP.md. Use after flash-start, or whenever a Flash mod needs a hook point and nobody knows where the game does something.
---

# Flash map

Paths here are relative to the hub root, two folders up from this file (`../../`), where `references/`, `tools/`, `templates/`, `games/` and `DIRECTORY.md` live.

1. Export (commands in `references/recon.md`): scripts, AS2 p-code when you need opcodes, `-swf2xml` plus
   `tools/swfmap.py` for obfuscated AS2 display trees, `tools/swfinfo.py` for frame labels. Keep exports in
   `decompiled/`, which is never published or copied into the mod's source.
2. For each system, find the **one** function or frame everything goes through, and confirm the shipped game calls it
   (a `trace` in a lab build is proof; reading code isn't).
3. Write `CODE_MAP.md` with the table in `references/recon.md`: system, where, notes. Add the object creation order of a
   level (net ids come from it), every place that reads "the player", every random call site count, and every save key.
4. List the original game's own script errors as you meet them: they go into the lab's `KNOWN_GAME_ERRORS`.

Signs to note now, because they change the plan:
- `Math.random` or `random()` in many files, wall-clock timers, Box2D: no lockstep (`references/network.md`).
- An obfuscated AS3 game where game classes have subclasses: don't recompile those classes (`references/hooking.md`).
- `_root` functions defined on later frames or redefined: wrap them lazily every frame.
- SWF 6: case-insensitive names, no `try/catch` (`references/traps.md`, AS2).

Next: `flash-lab`, then `flash-inject`.
