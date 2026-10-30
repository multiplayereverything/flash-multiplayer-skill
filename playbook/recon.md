# Recon

Find out what the SWF is before writing anything. Put the answers at the top of the mod's `MODLOG.md` and the system
map in `CODE_MAP.md`.

## 1. The file
```bash
python tools/swfheader.py game.swf
```
| Field | What it decides |
|---|---|
| `AS3=True` (DoABC tags) | AS3 route: `importScript` + stub classes (`playbook/build.md`, AS3) |
| `AS3=False`, `doaction>0` | AS2/AVM1 route: new DoAction tags, splicing or patched frame scripts |
| SWF version 6 | case-insensitive identifiers, no `try/catch`, no `getNextHighestDepth`, `ExternalInterface` hidden (unhide it for `coop.*`). Never raise the version: from SWF 7 `undefined+1` is NaN and old code breaks |
| fps | Frames per second: input scripts count in frames, so `wait 30` is a second at 30 fps |
| frames | Many frames with DoAction: logic lives on the timeline; 1-2 frames: a document class (AS3) or a loader |

Also check:
- **Wrappers.** An outer SWF that decrypts an inner one from a binaryData tag (Stealth Hunter 2: blob 24, first and
  last 999 bytes swapped). Unwrap, patch the inner SWF, wrap again. Also build a `_direct.swf` (inner only) for tests.
- **Sponsor preloaders and portal SDKs.** Click-to-continue preloaders need a click in every input script. Poki-style builds wait
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
| Level load / start / end | | what's rebuilt; where extra players must be added each level |
| Player and input | `Key.isDown`, an `Input` class, mouse listeners | where the one player is stored (`_root.knight`, `world.hero`, `engine.player`) |
| Enemies' target | | do they read "the player" directly? |
| Damage, death, respawn | | |
| Pickups, score, money | | |
| Win and lose | | does losing mean "the player died"? |
| Randomness | `Math.random`, AS2 `random()` | nothing to fix: Ruffle Together makes it the same on every PC |
| Timers | `getTimer`, `setInterval`, wall-clock deltas | nothing to fix: Ruffle Together's frame clock drives them |
| Pause, focus loss | | |
| Saves | SharedObject names and keys | Ruffle Together keeps a separate co-op save per SWF |
| Sounds | | sounds removed in `onSoundComplete` (see traps) |
| Menus and flow | frame labels | what starts the game: mouse, keys or `on(keyPress)` buttons, for input scripts |

The `CODE_MAP.md` of Bad Ice-Cream Online is the model: packages, boot and screens, main loop, level format, players
and input, enemies, pathfinding, popups, saves, then known bugs of the original game.

## 4. Pick the route
With the map, choose the path (a key map, or local co-op in the SWF: `playbook/ruffle-together.md`) and the
injection method (`playbook/build.md`), and write both, with the reason, in `MODLOG.md`. Then make a replay
get into play (`.claude/skills/flash-lab`) before any feature.
