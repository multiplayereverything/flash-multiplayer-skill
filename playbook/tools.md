# Tools

The scripts in `tools/` and the templates in `templates/`. Run every script with `python -I` from the repo root.

## Checks and readers
| Script | What it does |
|---|---|
| `tools/swfheader.py` | SWF version, AS2 or AS3, stage, fps, frames, DoAction count |
| `tools/swfinfo.py` | Frame labels of the main timeline and sprites |
| `tools/swfmap.py` | Display tree from FFDec `-swf2xml`, for obfuscated AS2 games |
| `tools/swfsym.py` | Links a library sprite with no class to an AS3 class (a new SymbolClass tag), so the mod can `new` it |
| `tools/case_scan.py` | SWF 6: finds identifiers that collide when case is ignored |
| `tools/keys_check.py` | Checks a `.keys` file: one `slot` line per player, valid key codes |
| `tools/unmochi.py` | Unwraps a MochiCrypt-protected SWF into the inner game SWF, so the mod is built from the game and not the ad wrapper |
| `tools/wincap.py` | Screenshot of a window by PID, never focusing it |

## Repo maintenance
| Script | What it does |
|---|---|
| `tools/directory.py` | `find`, `render` and `check` for `data/games.json` and `DIRECTORY.md` |
| `tools/check_public.py` | Scans the files that will be published for private data. Run before every push |
| `tools/fetch_ruffle.py` | Downloads the pinned Ruffle Together release and checks both hashes |
| `tools/test_all.py` | The repo's tests. Prints `ALL OK` when everything passes |

## FFDec helpers
`tools/ffdec/` holds Java helpers that FFDec runs during a build: `AddClasses.java` (empty stub classes so
`-importScript` can compile new classes), `CheckNamespaces.java` (fails the build on a protected-namespace change,
#1070), `ListClasses.java` (classes and static traits in a built SWF), `InsertAction.java` (compiles `.as` files into
new DoAction tags, leaving every original tag alone).

## Templates
| Path | What it is |
|---|---|
| `templates/build/build_as3.py` | AS3 build: importScript into a copy of the SWF (from Bad Ice-Cream) |
| `templates/build/build_as3_patches.py` | AS3 build with patches on fresh copies of the game's classes (from Intrusion 2) |
| `templates/build/build_as2_insert.py` | AS2 build: new DoAction tags on a chosen frame (from Territory War) |
| `templates/build/build_as2_splice.py` | AS2 build: spliced tags for obfuscated games (from Intrusion) |
| `templates/build/patches.py` | Exact-text edits to the game's classes, applied at build time to copies (the mod never holds game code) |
| `templates/ruffle-together/example.keys` | A key map to rename for your game |
| `templates/ruffle-together/example-2p.txt` | An input script for two players |
| `templates/ruffle-together/replay_check.py` | Runs a replay twice and checks the fingerprints match |
| `templates/ruffle-together/solo_check.py` | Runs the co-op SWF and the untouched SWF with one player and compares them |

The build scripts read FFDec from `FFDEC`. The co-op API helpers (`RuffleTogether.as`) and the demo SWF are in the
ruffle-coop repo under `tools/coop-api/`.
