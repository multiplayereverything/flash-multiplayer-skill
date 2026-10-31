# Traps

Each one cost a real mod time. The mod it came from is in brackets.

## Ruffle
- A public static method named `init` on a new AS3 class can't be called (#1069 "Property init not found"). Name it
  `setup`. [Bad Ice-Cream]
- No ACTIVATE/DEACTIVATE on focus change, so a key held through alt-tab stays down. Don't "release stale keys" either:
  Windows auto-repeats only the last key, and releasing others stopped players mid-walk. [Stealth Hunter 2]
- A fully covered window stops rendering and running frames. Its fps also drops as more windows run. [all]
- AS3 `IExternalizable` objects are serialized by public fields, not `writeExternal`; a deep object graph overflowed
  the native stack. Strip references before serializing. [Stealth Hunter 2]
- AS2 `Key.isDown = f` is ignored in SWF 8: replace `_global.Key` with a wrapper object instead. [Territory War]
- `_x` is truncated to twips (1316.65 reads back 1316.6), so hitTests differ from the host's. [Bow Man]
- Ruffle logs `Unknown AVM1 opcode 137` hundreds of times for an obfuscator's junk bytes; the untouched SWF
  does too, so count them as the game's own errors. [Intrusion]
- Colour codes sit between "ERROR" and the module in its log: strip ANSI before counting errors. [Stealth Hunter 2]
- An attached clip's first-frame code runs during `attachMovie` (Flash Player runs it after). [Gun Mayhem 2]
- Right after start-up the SWF's later frames may not be loaded yet, and `gotoAndPlay` to an unloaded frame is
  ignored without an error: a guest joining from the loader restarted the fight on every snapshot. Wait for
  `_framesloaded == _totalframes` before jumping (and in the lab's boot). [Ultimate Crab Battle]
- Windows messages posted to an unfocused Ruffle window (PostMessage, not SendInput) move the mouse, hover and type
  keys, but never press a button (the game's own buttons ignore them too). Prove real clicks in Ruffle's web player
  (same core version, from unpkg) in the agent's own browser pane; prove real keys with posted key messages.
  Neither touches the user's keyboard, mouse or focus. [Ultimate Crab Battle]
- `--filesystem-access-mode` defaults to `ask`: any local file load (mods-info from disk, `LoadVars` of a path)
  opens a dialog the lab window waits on. Test mods-info through the relay's INFO instead. [Territory War]

## FFDec
- `-importScript` can't add new AS3 classes: add stubs first (`AddClasses.java`). It prints nothing on success, so
  prove a replacement with a trace. [Stealth Hunter 2, Intrusion 2]
- FFDec often exits 0 after a compile error: fail on `SEVERE|Exception|error` in its output. [all]
- Its compiler rejects its own decompiled `new [A,B,C][i]()` and `for each (x in a || b)`: use a local. [Bad Ice-Cream]
- One class per file; no `var a:String, b:String;` declarations. [global-mod-relay]
- `Input.getInstance().init(...)`: "Property init has package internal access". Use a typed local. [Air Battle]
- `super.update()` inside a closure won't compile: wrap it in a private method. [Stealth Hunter 2]
- Constructor-assigned `public const` throws #1074 once recompiled: make it `var`. [Intrusion 2]
- A field named like a symbol class binds to the class: use `this.field`. [Intrusion 2]
- Class names that differ only in case collide on a Windows folder: case-sensitive staging dir. [Intrusion 2]
- Duplicate static function names compile and fail at runtime (#1063). [Stealth Hunter 2]
- Recompiling a class of an obfuscated game renames its protected namespace: #1070 in subclasses that weren't
  recompiled. `CheckNamespaces.java` catches it. [Stealth Hunter 2]
- AS2 "offset larger than maximum allowed for SI16": a branch over 32 KB. No giant `if` around the mod. [Territory War, Gun Mayhem 2]
- `-deobfuscate` output is for reading only; on a wrapper SWF it wrote a 0-byte file. [Stealth Hunter 2]
- FFDec 26 decompiles some loop exits as `§§goto(addrNNNN)` + a label, then can't compile its own output ("goto is
  not available"). When the label sits right after the loop, delete both: it's a `break`. [Stealth Assassin]

## AS2 / AVM1
- Never name a function `stop` (or `play`, `gotoAndStop`...): it compiles to the timeline action. A clean-up silently
  never ran. [Gun Mayhem 2]
- SWF 6 is case-insensitive: `var n` overwrites `N`, `N.lab` is `N.LAB`. Run `tools/case_scan.py`. [Bow Man, Ultimate Crab Battle]
- SWF 6 has no `try/catch/throw`, no `getNextHighestDepth`, no `getInstanceAtDepth`. Use fixed high depths away from
  the game's (Bow Man used 1048568-1048571). [Bow Man, Ultimate Crab Battle]
- Never raise SWF 6 to 7+: `undefined + 1` becomes NaN and old counters break. [Bow Man]
- `String(number)` keeps 15 digits: send the remainder for exact state. [Gun Mayhem 2]
- `hitTest(x, y, true)` takes stage coordinates, so the camera position is gameplay state. [Gun Mayhem 2]
- `gamepaused` flags don't freeze timeline animations or `_root.onEnterFrame`: a netplay wait must freeze them all.
  [Gun Mayhem 2]
- Clips created later run their onEnterFrame first; a clip's onEnterFrame runs before the root frame script.
  So on the first frame at a match frame, the previous match's objects (`Team1`/`Team2`) were still there and the
  host's second match left the friends' sticks out: start a match on the second frame there. [Gun Mayhem 2, Raft Wars,
  Territory War]
- `gotoAndStop` to the frame you're on doesn't re-run it: go through the frame before. [Gun Mayhem 2]
- A shared spawn counter that cosmetic effects also bump (GM2's `pDepth`, depth and name of every spawn, wrapping
  at 9900) drifts between PCs, because effects differ (own RNG, frame scripts during waits). At the wrap a new clip
  replaces a different old one on each PC. Give effects their own depth band during a match. [Gun Mayhem 2]
- A clip told to `play()` this tick still shows its stopped frame until the next timeline phase, so a wait that
  freezes it on that tick must count it as playing, or the shot is lost on the PC that waited. But only if it sat
  on that frame last tick: a frame script that jumped back to the stopped frame (a reload's end) cancels the
  `play()`. Keep last tick's frame per clip. [Gun Mayhem 2]
- Pickups, crates and countdowns that ripen on their timeline (pickable from frame 20, `gamewin` on the last frame,
  a child clip's `_parent.play()` starting its parent) kept playing during waits, so the PC that waited more got
  them earlier. Find every timeline that gates gameplay (`_currentframe >=`, frame scripts setting state) and hold
  it in the wait. [Gun Mayhem 2]
- A clip that doesn't exist yet on frame 1 gives NaN when you set it: move its frame instead. [Territory War]
- Setting `_x` inside a tween freezes the tween. [Ultimate Crab Battle]
- A MovieClip with button handlers (`onRelease`, `onPress`...) takes the mouse for all its children: an `onRelease`
  on the online panel (to stop clicks reaching the game's buttons behind it) made every button in the panel dead to
  real clicks, and a lab that calls `onRelease()` directly never notices. Block clicks with a background clip *under*
  the buttons instead. [Ultimate Crab Battle]
- AS1 caps one function body at 64 KB of bytecode (FFDec: "Function body is too large to fit into UI16"): a mod
  wrapped in one setup function hits it; wrap each source file in its own. [Ultimate Crab Battle]
- Frame scripts run after every enterFrame handler, so a value you pin in `onEnterFrame` loses to the game's own
  `score += n` that frame. A text field bound to a variable shows the last value *written* (in Ruffle even through
  `addProperty`): to show the host's value, unbind it (`tf.variable = null`) and set `tf.text`. [Ultimate Crab Battle]
- `x += f()` reads `x` before it calls `f`: a hook that changes `x` inside is overwritten; return the correction
  instead. [Bow Man]
- An arrow stuck in the ground has no `yanoe` clip, one stuck in an archer does: the game's deflection test only
  sees the latter. Read what a test actually reads before building a lab case for it. [Bow Man]
- A game's per-object `id` field can clash with yours: name the mod's fields `__pid`. [Intrusion]
- Off-screen culling, `Alive()` and `InGame()` read the global screen edges: with players apart, set the edges
  to the target player's view around each object's update, or enemies near a guest sleep and its bullets die.
  [Intrusion]
- Bullet constructors may reuse the shared `_root.p` point: capture the barrel position in a wrapper of the
  method that computes it. [Intrusion]

- A mirror that removed `obj.mc._parent` for a vanished object took every penguin with it when the object was the
  raft's dog, which sits straight in the shared container (penguins have their own wrapper clip). Remove the
  object's own clip unless it lives in a per-object wrapper. [Raft Wars]

## AS3
- `flash.display.Sprite` is sealed: dynamic fields need a `MovieClip`. [Bad Ice-Cream]
- `var` is hoisted to function scope: a local `key` shadowed a `key()` method (#1006), and two locals with one name
  merge. Give each a unique name. [Stealth Hunter 2]
- Object key order isn't stable: sort by slot. [Stealth Hunter 2]
- The hoisting trap again, in the lab script: a later step added `var back:Boolean` to the same function as a
  takedown step's `var back:int`, so `DIR_X[back]` became undefined and the test player was placed at NaN,NaN.
  The check failed every run for two days and looked like a flaky sync test. Log the computed position. [Stealth Hunter 2]
- A level load asked for while another level is still building is dropped by the game, but `PlayLevelCommand`
  already set `currentLevelIndex`: the friend looked like it was in the new level and stayed in the old one.
  Check that the host's room exists in the loaded level; if not after 10 s, load again. [Stealth Hunter 2]
- Assigning an Object where the game expects an Array throws #1034. Restore every swap in `finally`. [Intrusion 2]

## Games and portals
- Click-to-continue sponsor preloaders block labs: wait for them, or test the inner SWF. [Air Battle, Stealth Hunter 2]
- A portal score board on the end screen (BubbleBox's) shows the screen's MENU button only after it loads from the
  internet, so offline everyone is stuck there. Online, show MENU at once on the host. [Air Battle]
- Poki builds wait forever for an ad callback outside their page, and `ExternalInterface.call` throws #2067 each frame.
  The mod fixed both, online or not. [Bad Ice-Cream]
- MochiCrypt-wrapped games (`mochicrypt.Payload` binaryData) hide the real SWF: RC4 keyed with the payload's last
  32 bytes over the first 128 KB, then zlib. Unwrap it once and build from the inner SWF; the dead Mochi ad wait goes
  with it. [Ultimate Assassin series]
- A menu frame script that sets its level command back to 0 eats a command sent while the intro still plays:
  repeat it every frame until the screen changes. [Stealth Assassin]

## Process
- Owning sticks per player starves a player when a team has more players than sticks (or loses sticks): rotate each team's turns round its players instead, counting the game's own turn changes. [Territory War]
- `--coop-replay` (1.0.3.8) never passes `--coop-option` to the game, and headless session fingerprints differ between runs even with a fixed `--coop-delay`; prove an option with a `trace` per decision read from the host's log (RUST_LOG=info). [Territory War]
- Turn ownership can be proven without game hooks: run a script where every non-owner presses keys (and the host clicks) against a twin with the same timing and mouse path but none of that input; the fingerprint files must be identical. [Territory War]
- `--coop-replay` always runs the key map's maximum player count, so `coop.players` there is the max (4), not the session's. [Territory War]
- Headless replay PNGs have no device fonts: `_sans` text is invisible. Debug with drawn bars whose widths encode values. [Territory War]
- Shared hot-seat keys hide script timing mistakes (any player's keys move any stick); re-check a script with shots once turns are owned. [Territory War]
- A single-player game goes on Ruffle Together by adding local co-op in the SWF (extra copies of the hero, each on
  key codes the game never reads, routed to that copy's own keyboard before the game sees them). Keeping P2-P4 with
  P1 (spawn next to P1, follow P1 between rooms, cutscene walking) is most of the work. [Stealth Hunter 2]
- A minigame opened by an extra local player locks only that player's keyboard (it opens "as" that player). If the
  extra players' keyboards follow P1's, P1 still being on re-enables it and its held action key opens another minigame
  every frame (81 screens stacked). Lock P1 too while any minigame is open, before that follow runs. [Stealth Hunter 2]
- Check a replay's screenshots, not only that two runs match: with another game's key map, P1's FIRE wasn't the
  title's Space, and three "no desync" runs had sat on the title screen. Click menus with the host's mouse instead.
  [Stealth Hunter 2]
- Local co-op in a game whose one player variable (`_root.knight`) every object reads: set it to the nearest slot around each object's `Update` and try every slot in the hit tests, but only once slot 1 exists; one frame with it undefined breaks level intros. [Intrusion]
- A hot-seat game (both players on the same keys, taking turns) still fits Ruffle Together, but its key map must give every slot the same game keys, merged: a key is down while anyone holds it. Per-slot press/release would let one player's release cancel another's hold. [Territory War]
- A turn-based game added to Ruffle Together can read each slot's own keys from an existing 4-slot map (Gun Mayhem 2's)
  and act only on the turn owner's: no new key map, and other players' keys on someone else's turn do nothing.
  [Raft Wars]
- `--coop-replay` runs before Ruffle sets up logging, so a game's `trace()` lines never appear; run a headless
  session (`--coop-headless` host and join) for traces, and use `COOP_DESCRIBE_AT=<frames>` with the replay for
  object dumps. [Raft Wars]
- "1 player = the original" can't be shown with the sync fingerprint once the mod adds any clip (it hashes the whole
  stage). Compare `COOP_DESCRIBE_AT` dumps of the original and the mod with the mod's own clip left out: the clock
  and random-number lines must match too. [Raft Wars]
- Headless Ruffle has no device fonts (`_sans` text is missing in replay screenshots); check HUD text in a real
  window. [Raft Wars]
- In a `--coop-script`, a click right after a new menu appears misses: the replay's pointer only hovers what it moves over. Move one pixel off and back before each click. [Territory War]
- Ruffle's `getBounds` returns NaN for AS2 Button instances; read `_x/_y/_width/_height` (via `localToGlobal`) to find click positions for a script. [Territory War]
- A game that plays each sound effect on a fresh empty clip and removes the clip in `Sound.onSoundComplete` desyncs
  Ruffle Together in real windows (the untouched game did): when a sound ends depends on each PC's audio device.
  Headless replays and sessions never show it, because their sounds never end. Keep the clip (or remove it after a
  fixed number of frames). Fixed in Ruffle Together itself since: sounds end on the frame clock. [Smileys War]
- AS2 `on(keyPress "a")` buttons hear only the typed character, not the key. Ruffle Together 1.0.3.6 and 1.0.3.7
  didn't type it for a pressed key (fixed in 1.0.3.8), so in those versions an A press in a replay or a game-set
  `coop.keys` map never reached the menu, in the untouched game too. Check menus by key in a replay, with
  screenshots; `on(keyPress "A")` (capital) still needs Shift, as in Flash. [Dad 'n Me]
- A game that sets its own key map with `coop.keys` on frame 1 can still be launched with any built-in map that has
  enough slots: the game's map replaces it on the next frame, the same on every PC. [Dad 'n Me]
- To swap a bot for a human, wait until the attached bot's own frame-1 script has run (its `onEnterFrame` and
  variables exist), then `removeMovieClip` it and attach the human sprite at the same name and depth with the bot's
  fields as `attachMovie`'s init object. Install your per-slot `onEnterFrame` only once the new clip's own setup has
  run too. That needs no assumption about when Ruffle runs an attached clip's first frame. [Smileys War]
- The lab-only probe trick: make an empty clip whose `_x/_y` hold the numbers you need (kills, deaths, last hit)
  and read them from the `COOP_DESCRIBE_AT` dump, since replays don't log traces. [Smileys War]
- Macromedia V2 menus (List/ComboBox) gave a 1 px desync of a row highlight in a two-window lab, cause unknown.
  Setting the global styles `openDuration` and `selectionDuration` to 0 (no animation) made the next runs pass.
  [Smileys War]
- `windows_lab.py` counts a frame late at > 1.25 frame times: 31 ms at 40 fps versus 50 ms at 25 fps, so a 40 fps game trips the 3-late-frame limit far more easily on a busy PC. [Territory War]
- With 7 other sessions' labs running (about 18 Ruffle windows), some windows sat on the game's preloader for good
  (its transition clip reset). Not reproducible alone. Let the runner spot it and run the scenario again, and keep
  each failing run's window logs (the next run overwrites them). [Bad Ice-Cream]
- Two sessions building the same mod wiped each other's files: one build folder per run. [Gun Mayhem 2]
- Sharing the hub checkout with other sessions: `git update-index` on the shared index replaced another session's
  staged file just as it committed. Commit your own files through a temporary index (`GIT_INDEX_FILE`). [Gun Mayhem 2]
- Editing a bash lab script while it runs breaks the run (bash reads the file as it goes). [Gun Mayhem 2]
- Python heredocs with `\n` broke `.as` edits: do exact-match replacements from files. [Territory War]
- Ruffle desktop disappeared from `C:\Program Files` for a few minutes mid-session (a reinstall): let the lab also
  look for `tools/ruffle/ruffle.exe`. [Air Battle]
- Lab check on "key held, effect visible": compare only after the key stayed the same for 2 frames; stage listeners
  and the game's frame run in no fixed order. [Air Battle]
- A lab check that records only its first result hid two real bugs behind an earlier PASS: report every FAIL.
  [Raft Wars]
- Window captures (PrintWindow, then BitBlt) pick up whatever covers the lab window when other sessions' windows are
  on top. Capture inside the game: draw the stage into a BitmapData and print it; size it from the main timeline's
  `loaderInfo` (`stageWidth` is the window's size under noScale, 0 when minimized). [Ultimate Assassin series]
- Stopping a background shell on Windows leaves the lab it started running (and its relay holds the port): kill the
  lab's process tree by PID. [Ultimate Assassin series]
- A lab runner that blocks while it opens a new window takes the other windows' screenshots late; take pending
  shots first. [Stealth Assassin]
- A lab runner crashed deleting the previous run's log (a killed Ruffle still held it) and printed nothing, so a
  filtered suite looked empty: retry the delete, and print a RESULT line even when the runner stops early. [Bow Man]
- The bash sandbox couldn't see Ruffle's folder in `C:\Program Files` while PowerShell could: copy Ruffle into the mod's
  `tools/ruffle/` and let the lab prefer that. [Bow Man]
- FFDec decompiles constants that the constructor assigns as `public const X:uint;`; recompiled, the assignment
  throws #1074 (read-only). Rewrite them to `var` in the staged copy. [Intrusion 2]
- Two classes whose names differ only in case (`Snowball` and the symbol class `snowball`): on Windows,
  `-importScript` compiles `Snowball.as` over both ("Variable snowball is not defined"). Stage into a folder made
  case-sensitive with `fsutil file setCaseSensitiveInfo <empty dir> enable` (no admin). [Intrusion 2]
- A field named like a symbol class (the hero's `ammo_pack`, also a pickup graphic) compiles to the class: the
  field stays null and the first hero spawn throws #1009. Qualify every use with `this.`. [Intrusion 2]
- A teleported hero gets pulled back by camera bounds that open only after a level's scripted events: a lab fires
  the level exit through the trigger code instead of moving the hero there. [Intrusion 2]
- A screenshot fallback that copies the screen area of a lab window copies whatever covers it (other apps). Check
  with `WindowFromPoint` that the window itself shows at those points before copying. [Intrusion 2]
