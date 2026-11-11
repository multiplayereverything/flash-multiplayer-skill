# Build

Only games that need local co-op added (path B) or a few lines changed get a build; a local-multiplayer game
usually plays in Ruffle Together untouched. Every build starts from the untouched game SWF and ends with
`dist/<Game>_coop.swf`, the one file every player needs (byte for byte).

Tools: Java 21, FFDec 26.x CLI (`ffdec-cli.jar`; set `FFDEC` to its path), Python 3.10+.
`run()` in every build script fails on a non-zero exit **or** on output matching `SEVERE|Exception|\berror\b`:
FFDec often exits 0 after a compile error. Keep the log (`build/import.log`).

## AS3 (AVM2)
Template: `templates/build/build_as3.py` (simple) or `templates/build/build_as3_patches.py` (patches applied to fresh
decompiled copies, so the mod's source holds no game code: the one to start from).

1. **Stage** `src/` (the mod's own classes, package `mycoop`) into `build/as/`.
2. **Patch game classes at build time** (patches variant): copy only the listed classes from
   `decompiled/scripts/` into `build/as/`, then apply `EDITS = [(file, old, new, count)]`, asserting each count.
   Whole-file `REWRITES` for small classes you replace outright.
3. **Stubs for new classes.** `-importScript` silently ignores classes that don't exist yet, so add empty ones first:
   ```bash
   java -cp "<ffdec dir>/lib/*" tools/ffdec/AddClasses.java game.swf build/stubs.swf mycoop.Coop mycoop.Players ...
   ```
   It adds `public class X {}` to the ABC tag that holds the document class (avoids verify error 1014).
4. **Compile:**
   ```bash
   java -jar ffdec-cli.jar -importScript build/stubs.swf build/patched.swf build/as
   ```
   Compiles the new classes into the stubs and replaces every game class that has a file at the same path.
   It prints nothing useful on success: prove a replacement with a `trace` marker in a headless session.
5. **Namespace guard:**
   ```bash
   java -cp "<ffdec dir>/lib/*" tools/ffdec/CheckNamespaces.java game.swf build/patched.swf
   ```
   Exits 1 when a recompiled class's protected namespace changed and one of its subclasses wasn't recompiled: that
   gives #1070 at runtime. On obfuscated games this rules out recompiling any class that has subclasses; hook with new
   subclasses, an engine component, or polling instead.
6. Copy to `dist/`.

Extras that came up:
- Case-colliding class names (`Snowball` and `snowball`): stage into a case-sensitive folder
  (`fsutil file setCaseSensitiveInfo build\as enable`) or importScript compiles over the symbol class.
- Constructor-assigned `public const` fields throw #1074 once recompiled: patch them to `var`.
- A field named like a symbol class binds to the class: qualify it with `this.`.
- Obfuscated names: use the `§xx§` names exactly as FFDec prints them (the file for `§ "§` is `§ %22§.as`). Reach
  typed members through `*`-typed statics.
- Wrapped games: unwrap the inner SWF from its binaryData blob, patch it, wrap it back with
  `ffdec -replace outer.swf out.swf <id> blob.bin`.

## AS2 (AVM1)
None of the AS2 mods recompile game logic. The mod's code is added next to the game's and wraps it at run time
(replace a `_root` function with one that calls the original, every frame if the game redefines it). Pick the
injection method:

| Method | Use when | Template |
|---|---|---|
| **A. New DoAction tags** | the default: clean, the game's tags stay byte-identical | `templates/build/build_as2_insert.py` + `tools/ffdec/InsertAction.java` |
| **B. Compile in spare slots, then splice** | obfuscated games whose scripts don't survive a recompile | `templates/build/build_as2_splice.py` |
| **C. Export, patch, import frame scripts** | you must change a few clip events or button handlers | the steps below |

**A.** `java -cp "<ffdec dir>/lib/*" tools/ffdec/InsertAction.java game.swf out.swf <frame> coop.as boot.as ...`
compiles each file into its own DoAction tag before that frame's ShowFrame. Then the build checks every original tag
is unchanged and in order, and only type-12 tags were added. Inject on a frame the game reaches and stays on long
enough (Territory War: frame 3, because the title stops there and frame-4 tags never ran).

**B.** Stage each mod file as `frame_N/DoAction.as` in one of the game's tiny `stop()` slots, run `-importScript` into
a scratch SWF, pull the compiled DoAction tags out, and splice them unchanged into the untouched SWF before the target
frame's ShowFrame. About 8 files per scratch run.

**C.** `ffdec -export script build/export game.swf`, copy only the scripts you change to `build/as/scripts/...`, patch
them with exact strings that must match once, then `ffdec -importScript game.swf out.swf build/as`. Only staged
scripts are replaced. Use a per-run build folder (`build/run<pid>`) so two builds can't wipe each other.

AS2 build rules:
- **32 KB branch limit** ("offset larger than maximum allowed for SI16"): never wrap the mod in one big `if`. Keep
  top-level functions, guard only the setup call, keep each file under 32 KB.
- **SWF 6:** run `tools/case_scan.py` (identifiers that collide when case is ignored: `var n` overwrites `N`), check
  the header version byte after the build, and don't use `try/catch`.
- **Statement-level duplication for "the player"** (when a game has one hero variable such as `_root.duck` read in
  many scripts): FFDec prints one statement per line with braces on their own lines, so method C's export parses into
  a tree. Re-emit each run of consecutive statements that mention the hero once per extra hero, inside
  `if(_root.extraHero != undefined){...}` with the hero renamed, and turn calls like `nextFrame` into a per-hero
  "done" call. Recurse into an `if`/`while` whose test doesn't mention the hero. Solo is unchanged because the extra
  clips don't exist. [Duck Life 4]
- **Register swap for "the player"** (one player kept in `_root` variables, one big `_root.onEnterFrame`): rename the
  loop (`onEnterFrame = function` to `modLoop = function`) and run it once per player from a frame-1 tick. Before
  each extra player's turn swap that player's variables into `_root` (and `_root._x/_y` as their camera, so the
  game's own camera, clamps and shake work per player), and swap back after. Shared-world lines (enemy loop, timers,
  depth raises) run only in player 1's turn. Clips with their own scripts find their owner by walking `_parent` to a
  clip tagged with a slot. Solo is identical because every helper returns the original's answer. [My Friend Pedro]
- **Patch AS2 classes without recompiling:** one frame-1 DoAction replaces methods on the class prototypes at run time,
  only when `coop.players > 1`, so solo is the original by construction. Wait until the game's `_root` functions
  exist before installing. [Madness]
- **Fixed player numbers** (`_root.all.p3`, `pID == 2`, `while(i <= 4)`): add the extra players before the level
  spawns anything so they are players 2..N, then rewrite every fixed number from 2 up to `n + offset` (N - 1) with a
  regex at build time. Turn "player 1 out" into "every player out" with a helper that equals the original test when
  the offset is 0. Solo stays byte-identical. [Chaos Faction 2]
- **Code that loops over enemies, then hits "the player" once** (explosions, thrown bodies): call the game's function
  again for each other player with the loop counts set to 0, so only the player part runs. [Dad 'n Me]
- **Path A key sets that change by mode** (P1 moves to other keys in 2-player mode): pin the game's key variables to
  the map's codes after its own `controls()`, and replace `_root.controls` too (a Settings menu calls it again).
  [Chaos Faction 2]
- **Before rewriting exported scripts,** re-import every script unchanged and compare a replay with the original.
  Hobo's 5368 scripts were identical on every frame, which proved FFDec's AS1/AS2 round trip safe for that game.
  [Hobo]
- **A copy of the game per player** (AS3; a world built around its one player, such as a level that rotates around
  it): a document-class subclass loads one more copy of the SWF per friend with `loadBytes` into its own
  `ApplicationDomain(null)`, places each copy far apart on the stage, and gives each slot a `coop.camera` on its own
  copy. Write each copy's keys through `applicationDomain.getDefinition`, and keep every slot's game codes off the
  keys the game reads hard-coded. Details in [Run 2](../games/run-2.md) and [Run](../games/run.md). [Run 2, Run]
- **Run the game's own player script per player** (AS2, when the player script comes in many variants per level):
  `duplicateMovieClip` copies of the level's player carry its clip events, so each copy runs the level's own script.
  Keep the original body for solo and add a co-op body made by asserted regex substitutions (key reads through the
  copy's slot, global flags made clip-local, the goal test for the whole team). [The World's Hardest Game 2]
- SWF 6 and 7 hide `ExternalInterface`: unhide it before calling `coop.*` (ruffle-coop's AS2 helper does it).
