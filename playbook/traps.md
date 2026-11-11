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

- `unloadMovie(this)` right after `removeMovieClip(this)` unloads the **whole movie** in a real window: `this` reads as `""`
  and resolves to the root. Frames keep running and nothing is logged, but `_root._currentframe` reads 0. Headless runs and
  replays pass straight through, because that unload runs as a future that their `NullNavigatorBackend` drops (true of
  any `loadMovie`/`unloadMovie` bug, so test those in real windows). Search your game for
  `unloadMovie` and guard it with `if(this._name != undefined)`. Fixed in Ruffle Together 1.0.8; keep the guard while
  players may run older builds. [Electricman 2 HS]

- An AS2 variable is found before a child clip of the same name. Setting `_root.playerL = otherHero` (or
  `game.dude1 = otherHero`) for the length of a call makes the game's own code run for that hero; `delete` the variable
  afterwards to expose the real child again. Restore to a computed base (P1, a boss's grab victim, the first player up).
  [My Friend Pedro, Dad 'n Me]
- A stale clip reference re-resolves by path to a new clip of the same name, so `if (clip != lastClip)` never sees a
  re-attached clip. `coop.hud` marks the object, not the path: call it every frame for clips the game re-attaches.
  [My Friend Pedro]
- `getInstanceAtDepth(NaN)` finds a clip, so a "find a free depth" loop that starts at NaN never ends. [Madness]
- "thread 'main' has overflowed its stack" after a long run was the renderer tessellating a stroke at an absurd scale,
  not script recursion (AVM1's call limit gives an error, not a crash). Fixed in Ruffle Together 1.0.8. [Madness]
- `coop.hud` in a game that scrolls by moving `_root` was drawn off screen up to Ruffle Together 1.0.3.8 (fixed in
  1.0.3.9): such games need 1.0.3.9+. If your camera moves `_root` after the game pinned its HUD at `-_root._x`,
  re-pin the HUD right after, or it lags a frame and is clipped while zooming. [Intrusion]
- Key maps refuse codes Ruffle has no key for (F12 = 123, F24 = 135: "no key with code"). For a slot key the game
  never reads, use Insert (45). [Zombotron]
- Ruffle Together 1.0.6 took physical keys only from the launch line's `local:` line, so a game key missing there
  never arrived even with `coop.keys` (1.0.7+ reads both). On 1.0.6, counting a `coop.typed` character as that button
  held for 4 frames gets it through. [Madness]
- When every slot's map gives the same game key codes, `Key.isDown` sees everyone's keys at once: fine for menus, but
  in play hide the movement and fire codes from the game and move each hero from `coop.buttons(slot)`.
  [Ultimate Crab Battle]
- A mod that turns co-op on for "in a session" rather than `coop.players > 1` takes its co-op path in every
  `--coop-replay` (a replay is always a session): check solo in plain Ruffle, or switch on the count and replay with a
  1-slot map. [Ultimate Crab Battle, Intrusion 2]

- Content loaded with `loadBytes` keeps getting `enterFrame` after `unloadAndStop()` and removal; a game loop that
  reads `stage` then throws #1009 every frame. Remove the copy's loop listener before unloading. [Run 2]

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
- A clip that stays on the timeline unchanged over several frames is exported only on the frame that places it (on
  105 and 106, absent from 107's export). Rewrite asserts must count placements, not frames. [Duck Life 4]

- `onClipEvent(load)` and `onClipEvent(enterFrame)` of one placed clip export as separate files in one folder. A rewrite
  rule matched by folder hit the load script and broke the import ("Parsing finished before end of file"): match the
  file name too. [My Friend Pedro]
- `AddClasses` put new class stubs into a preloader's frame-1 ABC tag; the preloader class failed to load and the
  timeline looped with nothing thrown. Put stubs in the ABC tag of a real game class. [Zombotron]

- Flow-obfuscated AS3 (`§§goto` everywhere, won't compile): `-config autoDeobfuscate=1 -export script` gives
  readable code. To hook without recompiling any game class, subclass the document class in a new class and make
  that the document class (`tools/ffdec/SetDocClass.java`). [Run 2]

## AS2 / AVM1
- Never name a function `stop` (or `play`, `gotoAndStop`...): it compiles to the timeline action. A clean-up silently
  never ran. [Gun Mayhem 2]
- SWF 6 is case-insensitive: `var n` overwrites `N`, `N.lab` is `N.LAB`. Run `tools/case_scan.py`. [Bow Man, Ultimate Crab Battle]
- SWF 6 has no `try/catch/throw`, no `getNextHighestDepth`, no `getInstanceAtDepth`. Use fixed high depths away from
  the game's (Bow Man used 1048568-1048571). [Bow Man, Ultimate Crab Battle]
- Never raise SWF 6 to 7+: `undefined + 1` becomes NaN and old counters break. [Bow Man]
- In SWF 7+, a counter never set (`c = Number(_root.c) + 1`) stays NaN for good, and `NaN > 3` is false: a lab gate on
  it never opened. Set every counter before counting. [Duck Life 4]
- To replace a state clip, `createEmptyMovieClip(name, sameDepth)` alone replaces the old one. Removing the old clip
  after creating the new one removes the new one when the name hasn't changed. [Duck Life 4]
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

- A level's placed clip runs `onClipEvent(load)` after your first tick in Ruffle, and so does a fresh
  `duplicateMovieClip`. A position set in the same tick gets overwritten, so place clips one tick later.
  [The World's Hardest Game]
- `ColorMatrixFilter` recolours a sprite and keeps its black outline, which a `Color` transform can't.
  [The World's Hardest Game]
- The game's `and` can be the Flash 4 operator, where both sides run: `health <= 0 and cpDie(h)` calls `cpDie` every
  time, so the called function has to check again. [Hobo]
- In a game that walks by scrolling the world, two players walking the same way each undo the other's step and nobody
  reaches the screen limit, so the street runs away. Scroll for the group, not per step. [Hobo]

- SWF 6 and a frame-1 `var`: frame-level variables live on `_root`, so `for (var cpk...)` silently replaced the function
  `_root.cpK`, and calls to it did nothing. Name every helper and loop counter distinct ignoring case, and run
  `tools/case_scan.py <your src folder>`. [Electricman 2 HS]
- A fingerprint can't see `_xscale`: solo matched the original on every frame while the health bars never moved. Compare
  screenshots with the original too. [Electricman 2 HS]
- A game's shared per-frame totals (enemies add, the hero reads and clears) need one reader that never changes. "The
  first hero alive" can read right after a clear, before any enemy has added, and that reads as a win. [Electricman 2 HS]
- A single `_root.gamespeed` set by several heroes' frames: a friend's idle frame cancels another's slow motion. Keep a
  wish per hero and set the shared value from all of them. [Electricman 2 HS]
- `coop.label` sits at the top of the clip's bounds, and invisible hit boxes count. Hang the label on a small clip of
  its own that follows the head. It needs a real window to see: headless shots don't draw labels. [Electricman 2 HS]

- AVM1 `undefined >= n` is true (it compiles to `!(a < b)`): a "sit out" check removed the team leader. Test for a
  number first. [Madness]
- Never `attachMovie` at a fixed depth inside the game's world: it silently replaces what is there (a reticle deleted a
  boss's retreat point and the stage couldn't be finished). Use `getNextHighestDepth`. [Madness]
- Copying a character with the game's own copy function can leave fields pointing at the old owner (weapons'
  `myOwner`), which blocked doors and pick-ups for that friend. Check every back-reference on a copy. [Madness]
- A level's `onEnterFrame` runs before that frame's own script: set up per-level copies only once the frame script has
  run (wait for a handler it installs), or you copy undefined handlers and it overwrites your setup. [My Friend Pedro]
- SWF 6: `Key.isDown = f` fails silently (read-only). `ASSetPropFlags(Key, "isDown", 0, 7)` first, then assign.
  [Dad 'n Me]
- A call to a function that no longer exists does nothing and raises no error: a scripted edit between two markers
  deleted 5 functions and the build still passed. List the `^function` names after every scripted edit. [Dad 'n Me]

- Controls clips whose frame scripts switch the hero to a scroll walk on a mode change (entering a scroll zone), key
  or not, are harmless with one hero, but a second hero dragged by the scroll into a zone starts scrolling back with
  no key held and the world shakes. Keep dragged heroes out of the zones, and apply mode switches to added heroes
  only while the arrow is held. [The Skullkid]
- A hero's walk animation that moves `_root.hero._x` from its own frame script moves player 1 when a copy plays it:
  rewrite it to `_parent._x`. [The Skullkid]

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

- Box2D's proxy limit can be too low for added players: Zombotron's 512 crashed with 4 players, and 2048 works. Raise
  it only in a session, so 1 player stays the original. [Zombotron]

- A HUD the game creates in code on root: set its `.name` (`"coophud"`) and call `coop.hud("root.coophud")`; mark it
  again whenever the game makes a new HUD clip. [Intrusion 2]

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
- Green replays, coop-lab and two short windows can all pass on a game that dies at the end of its first fight. Play a whole
  script in real windows, and check a heartbeat from the game to its end. [Electricman 2 HS]
- A session with `--coop-script` never reads the keyboard, so no scripted lab proves real keys. Post key messages to the game's
  own windows on the launcher's line and check what the hero does. Posted focus can be lost to any focus change on the PC, so
  re-assert it before each press. Even then such labs sometimes lose keys partway (likely lost focus, not proven): rerun a
  failed one before blaming the mod. [Electricman 2 HS, Madness]
- Co-op that needs a menu click to turn on looks like "everyone moves one player" when nobody clicks. Take the count
  from `coop.players`, and check it in a session: `--coop-replay` reports the key map's slot count, not `--coop-players`,
  so test a smaller count with a `.keys` file that has that many slots. [Stealth Assassin]
- Enemy AI written for one player can assume its target is close when sight is lost and walk there in a straight
  line. Switching targets by distance alone sends it through walls: switch only to a player it can see, and test with
  a lab-only trace that logs each enemy entering a wall. [Stealth Assassin]
- Heroes moving in screenshots doesn't prove input works: knock-backs moved heroes who could press nothing. Count the moves
  each player has actually played. [Electricman 2 HS]
- `wincap.py` reads the screen area, so a covered game window captures whatever covers it, including the user's other
  apps. Check the image is the game before keeping it, and delete it unseen if not. [Electricman 2 HS]
- Sessions share a `flash-games` clone: staging whole files can publish another session's uncommitted catalog lines
  before their SWF is up. Check `git status` right before release, and push the file and its catalog line together.
  [Electricman 2 HS]
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
- Ruffle gives a fill of alpha 0 no mouse hits: use alpha 0.01 for invisible hit areas. [Air Battle]
- Never place or size co-op UI by TextField metrics: device-font sizes differ between PCs (about 0 headless), and
  positions are in the sync fingerprint. Use fixed sizes, positions and hit rects. [Air Battle]
- Ruffle window screenshots include a 24 px menu bar; replay script clicks are stage pixels. [Air Battle]
- Chat on "/" (1.0.3.7+) opens only on the main-row slash (191); a map using numpad "/" (111) doesn't clash.
  [Air Battle]
- Ruffle's `getBounds` returns NaN for AS2 Button instances; read `_x/_y/_width/_height` (via `localToGlobal`) to find click positions for a script. [Territory War]
- A game that culls by the screen (clips hide unless they touch a clip at the stage's size) loses everything off the
  stage under `coop.camera`, because the world no longer moves. Grow that clip so nothing is culled. [Smileys War]
- Under `coop.camera` a still cursor keeps its old game position while the camera moves. If the game expects a cursor
  fixed on screen, store the offset from the camera when `coop.mouseX/Y` change and aim at camera + offset. [Smileys War]
- Re-check a workaround when Ruffle Together fixes the bug behind it: keeping sound clips the game removes made
  "1 player = the original" fail once sounds ended on the frame clock. [Smileys War]
- AS2 `on(keyPress "a")` buttons hear only the typed character, not the key. Ruffle Together 1.0.3.6 and 1.0.3.7
  didn't type it for a pressed key (fixed in 1.0.3.8), so in those versions an A press in a replay or a game-set
  `coop.keys` map never reached the menu, in the untouched game too. Check menus by key in a replay, with
  screenshots; `on(keyPress "A")` (capital) still needs Shift, as in Flash. [Dad 'n Me]
- A game that sets its own key map with `coop.keys` on frame 1 can still be launched with any built-in map that has
  enough slots: the game's map replaces it on the next frame, the same on every PC. [Dad 'n Me]
- A mod that calls `coop.keys` only when `coop.players > 1` has no key map in solo, so a controller (TV mode) moves
  the player on the default map's arrows but can't attack: the punch keys (A, S) are on no button. Give solo its own
  map (`dad-n-me-solo`) and have the launcher pass `--coop-keys <map>` on the solo action too. [Dad 'n Me]
- To swap a bot for a human, wait until the attached bot's own frame-1 script has run (its `onEnterFrame` and
  variables exist), then `removeMovieClip` it and attach the human sprite at the same name and depth with the bot's
  fields as `attachMovie`'s init object. Install your per-slot `onEnterFrame` only once the new clip's own setup has
  run too. That needs no assumption about when Ruffle runs an attached clip's first frame. [Smileys War]
- The lab-only probe trick: make an empty clip whose `_x/_y` hold the numbers you need (kills, deaths, last hit)
  and read them from the `COOP_DESCRIBE_AT` dump, since replays don't log traces. [Smileys War]
- `windows_lab.py` counts a frame late at > 1.25 frame times: 31 ms at 40 fps versus 50 ms at 25 fps, so a 40 fps game trips the 3-late-frame limit far more easily on a busy PC. [Territory War]
- With 7 other sessions' labs running (about 18 Ruffle windows), some windows sat on the game's preloader for good
  (its transition clip reset). Not reproducible alone. Let the runner spot it and run the scenario again, and keep
  each failing run's window logs (the next run overwrites them). [Bad Ice-Cream]
- Lab load can take the PC down: 6 parallel 3000-frame replays with `COOP_DESCRIBE_AT` dumps every 150 frames, next to
  other sessions' labs, came just before a power loss (resource exhaustion in the log). Run at most 2 replays at once and
  wait while `Win32_OperatingSystem` FreeVirtualMemory is under 15 GB. [Duck Life 4]
- One lab SWF for every scenario, no rebuild: the script's first line `move F 0` puts the host's mouse at x = F; the
  lab code reads `coop.mouseX(0)` once loaded, sets up the state the scenario needs and does `gotoAndStop(F)`.
  [Duck Life 4]
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

### Per-player screens
- Per-PC HUD without breaking lockstep: when the HUD script also runs game logic (it decides the winner), let it run,
  then write the local player's numbers over its text, a bar's `_xscale` and `_alpha`. The sync check compares
  position, visibility, depth and frame only. [Smileys War]
- Per-player markers under `coop.camera`: build every (camera, teammate) marker on every PC, placed from shared camera
  values, and give only the local camera's markers alpha 1. Proven with 21 players at `desync_at=none`. [Zombotron]
- With a camera per player, testers said friends "disappeared" when one ran ahead: they were only off screen. Add
  off-screen markers or a team camera from the start. [Zombotron]
- Per-player cameras in a game with its own zoom: let the game's camera zoom out to fit every living hero (it decides
  what stays awake), and give each slot `coop.camera(s, x, y, z)` with z = 1 / level scale (clamped), the hero's stage
  point clamped inside the stage, a downed slot following the nearest living hero, and cameras off outside play.
  Details in [Intrusion 2](../games/intrusion-2.md) and [Intrusion](../games/intrusion.md). [Intrusion, Intrusion 2]
- A tile engine that blits the world into one screen-sized canvas at the camera's offset draws nothing outside P1's
  view under `coop.camera`, and growing a cull rect isn't enough. After the game's update, set the engine camera to
  the corner of a region around every player's view, size the viewport and canvas to it (whole blocks), and put
  the game's camera back at the start of the next update so the simulation never sees the region. Each slot's
  camera is its player's point inside the region. Stretch screen-space layers (night tint, rain) over the region,
  and shift mouse reads made during the update by (game camera - region corner). [Stealth Hunter 2]
- `coop.hud` needs a direct child of the root: move a deep HUD into one while the cameras are on and back for menus
  and cutscenes. Markers placed from the game's camera (a prompt over P1) must be set again on EXIT_FRAME from P1's
  own camera and shown only on P1's PC. [Stealth Hunter 2]
- `--coop-replay` draws only slot 0's camera: to check slot N's view, build a throwaway copy where slot 0 uses slot
  N's camera. Identical fingerprints for every view prove the camera is picture only. [Stealth Hunter 2]
- A game that calls `Mouse.hide()` and draws only the host's crosshair leaves friends with no cursor: draw one
  coloured crosshair per slot at `coop.mouseX/Y(slot)` (shared answers, sync-safe). [Intrusion 2]
- Locking a world-scrolling brawler's vertical camera for 2+ players halved the street depth and left enemies out of
  reach. Keep each player's limit in world terms and move one group camera to the players' middle height. [Hobo]

### Players, turns and leaving
- A player-count menu must start at `coop.players` and never go above it: slots nobody holds stall the game. A replay
  reports the key map's slot count (4), so scripts click from that value. [Raft Wars, Smileys War]
- Turn-based games after Ruffle Together 1.0.3.7: a leaver no longer ends the session, but `turn % players` keeps
  handing their slot turns. Mark "leave N" from `coop.events` and skip it; pass on a turn they were aiming. [Raft Wars]
- Per-slot mouse in a turn-based AS2 game: gate the game's own `onClipEvent(mouseDown)` off in a session and re-run
  its down/move/up each frame from `coop.mouseX/Y/mouseDown(slot)` with your own drag flag; otherwise the host's
  normal mouse events, which still fire, steer or shoot the other player's bow. Stage px to `_root`:
  `(mx - _root._x) * 100 / _root._xscale`. [Bow Man]
- Extra players spawned at a level's start can fall or die before their player acts: park each one (hold its spawn
  position, zero velocity) until that slot presses any key. [Air Battle]
- `coop.events` empties its list on every call: read it in one place per frame. [Raft Wars]
- A bot takes over a leaver: attach the game's own bot sprite at the same name and depth with the player's fields as
  the init object; restore name and score after the bot's own frame-1 setup. [Smileys War]
- A leave test must kill a friend's process mid-run (`taskkill /T /F`); a friend that just reaches `--coop-frames`
  isn't a leave (the host waits about 60 s and reports it frozen). [Intrusion 2, Raft Wars, Dad 'n Me]

### Labs
- ruffle-coop's coop-lab `lab.py` (as of 2026-11-11): a relative `--exe` prints nothing with exit code 0 (pass an
  absolute path and count the `COOP RESULT` lines); it passes no `--save-directory`, so give each player a temp one
  (and a `--cache-directory`); its local relay allows 4 players (the real one 8); its timeout is too short for 5-6
  players and it drops all output on timeout; it has no `--leave-after`. Without editing it: import it, patch
  `player()` or `subprocess.Popen` to add the flags, strip your own flags from `sys.argv` before its `main()` builds
  the parser; or pass `--exe` a `.cmd` wrapper that adds `--save-directory <temp> %*`.
  [Chaos Faction 2, Raft Wars, Ultimate Crab Battle, Dad 'n Me, Air Battle, Bow Man, Stealth Hunter 2]
- `windows_lab.py` passes no `--save-directory`, so its windows write the user's real co-op saves. [Chaos Faction 2]
- Lab-only switches: read `coop.option(name)` (GOD, ALL missions, SOLO as a same-session control) in the lab build
  only, set with `--coop-option` in headless sessions; replays never pass options, so build replay variants that force
  them. [Stealth Assassin, Dad 'n Me]
- "Solo = original" when the mod switches on for any session: build a test copy with the session check forced
  false and compare it with the untouched SWF, then show the real build diverges only where the session path
  starts. [Bow Man]
- In AS, `undefined == null` is true: debug checks need `===`. [Bow Man]
- A one-frame scripted `click` still proves a turn gate in a drag-to-shoot game (it fires a zero-power shot): delete
  one click and check the run stays identical up to the next scripted event. [Bow Man]
- A headless session (`--coop-headless` host and joiners) needs `--coop-script` on every player; each plays its own
  slot's lines. With the script on the host only, friends get no input and the session still reports
  `desync_at=none`. (coop-lab's `lab.py` already does this.) [Run 2]
- A game whose input is `onClipEvent(keyDown)` with `Key.getCode()` acts only on the press, and Ruffle Together's
  scripted sessions send no key repeat. The Skullkid's boss could never die: the saw and the boss's loop both start
  on the Space keyDown, and the death lands on the loop's restart tick and loses. Real Flash key repeat re-sent
  keyDown and moved the loop. Look for timelines a held key's repeat used to restart. [The Skullkid]
- A lab FlashVar path that feeds scripted keys must turn the co-op API off, or replays mix the two.
  [Ultimate Crab Battle]
- Reaching an ending without a bot: move a hero onto each level's real exit trigger (position from `-swf2xml`, twips
  / 20, the root child at that spot, the centre of its bounds), or call the game's own `die()` on every enemy every 60
  frames, or teleport onto the exit sensor. The game's real path then runs. Rotate which slot finishes.
  [My Friend Pedro, Chaos Faction 2, Zombotron]
- Prove every button of every slot without screenshots: press one button of one slot for 10 frames and report the
  first frame whose fingerprint differs from a no-press run. [Chaos Faction 2]
- Instrumentation can change the run: `_root.watch` and a per-instance `gotoAndStop` override both did. Renaming an
  empty clip's `_name` to a state string each frame (read in `COOP_DESCRIBE_AT`) didn't. [Hobo, Madness]
- Lab checks that depend on where P1 lands are flaky (an enemy spawned "next to" a soldier ends up nearer P1): move the
  soldier under test away first, and make walk checks jump. [Intrusion]
- When a key reached the slot but the move didn't happen, check the lab first: the hero had drifted away from the
  probe's enemy. Put it back on its spot whenever idle. [Electricman 2 HS]
- Idle test fighters get knocked out in seconds and drop their weapon: time single-button checks before first
  contact. [Chaos Faction 2]
- Mouse-aim proofs: put script targets inside the game's aim range (a shot aimed straight up clamped to the limit and
  proved nothing) and log aim, mouse and gun in the fire trace. [Raft Wars]
- A bot that stalls isn't always the bot: of seven stalls, four were the bot, two mod bugs, one the game's dead end.
  Dump what the game still counts (enemies, objectives) before blaming either. [Madness]
- Long replays on a shared PC fail with "memory allocation ... failed", and overlapping labs once ended in a power
  loss. Before each lab step wait until `FreeVirtualMemory` is 15 GB+ and fewer than 6 Ruffle processes run, and
  don't trust logs from a run a crash cut off. [Electricman 2 HS, Madness, Duck Life 4, The Skullkid]
- webdesignmuseum.org serves SWFs to a browser page but Cloudflare blocks curl: load the page in the agent's browser
  and save its own fetch (with the owner's OK), then check the SHA-256. [The Skullkid, Run 2]
- flash-games' `tools/update-catalog.ps1` rewrites every entry from the SWFs on disk, so it sweeps other sessions'
  pending lines into your commit. Run `git status` first. [Intrusion]
