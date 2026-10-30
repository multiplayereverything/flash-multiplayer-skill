---
name: flash-inject
description: Get a mod's code into a Flash game for Ruffle Together without editing the original file - AS3 importScript with stub classes and build-time patches, AS2 new DoAction tags or spliced tags for obfuscated games - with checks that every original tag survived. Use when a single-player game needs local co-op added, or a game needs a few lines changed (its own key map, a player count).
---

# Flash inject

Paths here are relative to the hub root, two folders up from this file (`../../`), where `references/`, `tools/`, `templates/`, `games/` and `DIRECTORY.md` live.

Path A games often need no injection at all: try a key map first. The route is in `references/build.md`. Start
from a template in `templates/build/` and rename what `templates/README.md` lists.

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
- makes one `dist/<Game>_coop.swf` (every player needs these exact bytes);
- checks AS2 output: original tags unchanged, SWF version unchanged, `tools/case_scan.py` clean for SWF 6.

When something breaks, look it up in `references/traps.md` (FFDec, AS2, AS3 sections) before guessing.

Then add the players (`skills/flash-coop`) and prove each change with a replay (`skills/flash-lab`).
