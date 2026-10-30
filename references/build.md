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
- SWF 6 and 7 hide `ExternalInterface`: unhide it before calling `coop.*` (ruffle-coop's AS2 helper does it).
