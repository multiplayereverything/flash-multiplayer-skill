---
name: flash-inject
description: Get the mod's code into a Flash game without touching the original file: AS3 with FFDec importScript plus stub classes and the namespace guard, AS2 with new DoAction tags, spliced tags for obfuscated games, patched frame scripts or p-code; the UseNetwork flag; lab and release variants. Use when building or debugging a Flash mod's build, when FFDec reports compile errors, or when a patched game class breaks at runtime with #1070, #1074 or #1069.
---

# Flash inject

Paths here are relative to the hub root, two folders up from this file (`../../`), where `references/`, `tools/`, `templates/`, `games/` and `DIRECTORY.md` live.

The route is in `references/build.md`. Start from a template in `templates/build/` and rename what
`templates/README.md` lists.

| Game | Start from |
|---|---|
| AS3, unobfuscated | `templates/build/build_as3_patches.py` + `templates/build/patches.py` (game classes copied and patched at build time, so the mod's source has no game code) |
| AS3, tiny change | `templates/build/build_as3.py` |
| AS2, default | `templates/build/build_as2_insert.py` + `tools/ffdec/InsertAction.java` |
| AS2, obfuscated | `templates/build/build_as2_splice.py` |

Every build:
- fails on FFDec output matching `SEVERE|Exception|error`, not only on the exit code;
- adds stubs for new AS3 classes (`tools/ffdec/AddClasses.java`) and runs `tools/ffdec/CheckNamespaces.java`;
- applies every edit with an exact match and an asserted count;
- sets UseNetwork (`tools/set_use_network.py`; SWF 6 has no flag and is Ruffle only);
- makes `dist/<Game>_online.swf` and `dist/<Game>_lab.swf` from the same source;
- checks AS2 output: original tags unchanged, SWF version unchanged, `tools/case_scan.py` clean for SWF 6.

When something breaks, look it up in `references/traps.md` (FFDec, AS2, AS3 sections) before guessing.

Then hook the game (`references/hooking.md`) and prove each hook with a lab trace.
