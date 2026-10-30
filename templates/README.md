# Templates

Taken from working games. Rename before use:

| File | From | Change |
|---|---|---|
| `ruffle-together/example.keys` | | the key codes your game reads, one `slot` line per player (`python -I tools/keys_check.py` checks it) |
| `ruffle-together/example-2p.txt` | | the clicks and keys that get through your game's menus, then what each player does |
| `ruffle-together/replay_check.py` | | nothing: pass the Ruffle Together exe, the SWF, the key map and the script |
| `ruffle-together/solo_check.py` | | nothing: pass the co-op SWF, the untouched SWF, a 1-slot key map and a script; `--allow` the mod's own menu frames |
| `build/build_as3.py` | Bad Ice-Cream | `GAME`, `OUT_NAME`, `PACKAGE` (your new classes' package) |
| `build/build_as3_patches.py` | Intrusion 2 | the same, plus the `EDITS` list (yours goes in your own `patches.py`) and compile fixes |
| `build/build_as2_insert.py` | Territory War | `GAME`, `OUT_NAME`, the module list and the frame to insert on |
| `build/build_as2_splice.py` | Intrusion | `GAME`, `OUT_NAME`, the source list, spare slot frames, target frame |

The build scripts read FFDec from `FFDEC`. The co-op API helpers (`RuffleTogether.as` for AS2 and AS3) and a demo
SWF that uses every call are in ruffle-coop's `tools/coop-api/`.
