# Recon

Find out what the SWF is before writing anything. Put the answers at the top of the mod's `MODLOG.md` and the system
map in `CODE_MAP.md`.

## 1. The file
```bash
python tools/swfheader.py game.swf
```
| Field | What it decides |
|---|---|
| `AS3=True` (DoABC tags) | AS3 route: `importScript` + stub classes (`references/build.md`, AS3) |
| `AS3=False`, `doaction>0` | AS2/AVM1 route: new DoAction tags, splicing, patched frame scripts or p-code |
| SWF version 6 | no FileAttributes tag (no UseNetwork flag), case-insensitive identifiers, no `try/catch`, no `getNextHighestDepth`; Flash Player 32 won't open sockets from it, so plan Ruffle-only. Never raise the version: from SWF 7 `undefined+1` is NaN and old code breaks |
| `attrs` bit 0 | UseNetwork. The build sets it so Flash Player lets a local SWF open sockets |
| fps | Sets snapshot rates and lab timeouts |
| frames | Many frames with DoAction: logic lives on the timeline; 1-2 frames: a document class (AS3) or a loader |

Also check:
- **Wrappers.** An outer SWF that decrypts an inner one from a binaryData tag (Stealth Hunter 2: blob 24, first and
  last 999 bytes swapped). Unwrap, patch the inner SWF, wrap again. Also build a `_direct.swf` (inner only) for tests.
- **Sponsor preloaders and portal SDKs.** Click-to-continue preloaders block a self-driving lab. Poki-style builds wait
  forever for an ad callback, and `ExternalInterface.call` with no page throws #2067 every frame; patch both.
- **Site locks** (`_url` or `loaderInfo.url` checks) and **obfuscation** (`§xx§` names in AS3, invalid identifiers in AS2).

## 2. Export
```bash
java -jar ffdec-cli.jar -export script decompiled/ game.swf
# AS2 obfuscated: readable copy for reading only
java -jar ffdec-cli.jar -config autoDeobfuscate=1,deobfuscateAs12RemoveInvalidNamesAssignments=1,as12DeobfuscatorExecutionLimit=200000 -export script decompiled_deob/ game.swf
# AS2 p-code, when you need opcodes
java -jar ffdec-cli.jar -format script:pcode -export script pcode/ game.swf
# Display tree, for obfuscated AS2 games without hookable functions
java -jar ffdec-cli.jar -swf2xml game.swf game.xml && python tools/swfmap.py game.xml
python tools/swfinfo.py game.swf        # frame labels
```
`decompiled/` is for reading. It never goes into the mod's source, a release or a public repo.

## 3. The system map
Find the one place each system runs through, and check that the shipped game really calls it. One table per mod:

| System | Where (class/function or frame) | Notes |
|---|---|---|
| Frame loop | e.g. `Controller.loop`, `CoreEngine.efHandler`, `_root.UpdateGame`, a clip's `onEnterFrame` | who calls whom each frame, in which order |
| Level load / start / end | | what's rebuilt, in which order objects are created (net ids come from this) |
| Player and input | `Key.isDown`, an `Input` class, mouse listeners | where the one player is stored (`_root.knight`, `world.hero`, `engine.player`) |
| Enemies' target | | do they read "the player" directly? |
| Damage, death, respawn | | |
| Pickups, score, money | | |
| Win and lose | | does losing mean "the player died"? |
| Randomness | `Math.random`, AS2 `random()` | how many files call it, at spawn or every frame |
| Timers | `getTimer`, `setInterval`, wall-clock deltas | wall-clock logic rules out lockstep |
| Pause, focus loss | | |
| Saves | SharedObject names and keys | co-op must not overwrite single-player saves |
| Sounds | | the guest plays the host's sounds or its own |
| Menus and flow | frame labels | where to put the ONLINE button |

The `CODE_MAP.md` of Bad Ice-Cream Online is the model: packages, boot and screens, main loop, level format, players
and input, enemies, pathfinding, popups, saves, then known bugs of the original game.

## 4. Pick the route
With the map, choose the sync model (`references/network.md`) and the injection method (`references/build.md`), and
write both, with the reason, in `MODLOG.md`. Then build the lab (`references/lab.md`) before any feature.
