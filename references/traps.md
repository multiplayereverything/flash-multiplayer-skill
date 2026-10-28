# Traps

Each one cost a real mod time. The mod it came from is in brackets.

## Ruffle
- A public static method named `init` on a new AS3 class can't be called (#1069 "Property init not found"). Name it
  `setup`. [Bad Ice-Cream]
- `Socket.timeout = ...` throws #1056 in Ruffle desktop. Wrap it in try/catch. [Bad Ice-Cream]
- No ACTIVATE/DEACTIVATE on focus change, so a key held through alt-tab stays down. Don't "release stale keys" either:
  Windows auto-repeats only the last key, and releasing others stopped players mid-walk. [Stealth Hunter 2]
- A fully covered window stops rendering and running frames. Its fps also drops as more windows run. [all]
- Sockets are polled once per frame: about 33 ms round trip on localhost at 30 fps. [Stealth Hunter 2]
- AS3 `IExternalizable` objects are serialized by public fields, not `writeExternal`; a deep object graph overflowed
  the native stack. Strip references before serializing. [Stealth Hunter 2]
- AS2 `Key.isDown = f` is ignored in SWF 8: replace `_global.Key` with a wrapper object instead. [Territory War]
- `_x` is truncated to twips (1316.65 reads back 1316.6), so hitTests differ from the host's. [Bow Man]
- A FlashVar named `end` never reached the script. [Raft Wars]
- A FlashVar with the name of a game function on `_root` (`direct`) arrives as that function. [Intrusion]
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

## Flash Player 32
- A SWF 9 game in the release projector gets no `loaderInfo.uncaughtErrorEvents`: errors inside Flash Player can't be
  counted by the lab. Run the same scenarios with one Ruffle window per pair (FP host + Ruffle friend and the reverse)
  so Ruffle's log covers the network side. [Bad Ice-Cream]
- Refuses every HTTP load from a local SWF (#2048, even with a crossdomain.xml): mods-info needs the relay INFO
  fallback. [Stealth Hunter 2, Air Battle]
- Refuses XMLSocket from a local SWF 6 file, even with an SWF 8 header and UseNetwork. SWF 6 mods are Ruffle-only.
  [Bow Man]
- Needs the UseNetwork flag to open sockets from a local file. [all]
- The release player shows no script errors: one throwing message froze the reader. Try/catch per message. [Stealth Hunter 2]
- Throttles hidden windows. Synthetic key messages never reach it. [Gun Mayhem 2]
- A Flash Player host with a Ruffle friend gave a per-frame "Invalid object" error storm on the friend; never solved,
  and that mod dropped Flash Player. [Stealth Hunter 2]
- Lab results from the projector: bake each window's flashvars into its own lab copy and send the LAB lines to the
  relay as `D|` debug lines (printed with `--log`, never forwarded). A window that leaves the room can't report any
  more, so report done before leaving. [Air Battle]
- Starting the mods-info download during session start changed lab timing; test builds skip it unless given a test
  URL. [Stealth Hunter 2]

## FFDec
- `-importScript` can't add new AS3 classes: add stubs first (`AddClasses.java`). It prints nothing on success, so
  prove a replacement with a trace. [Stealth Hunter 2, Intrusion 2]
- Some SWFs write the FileAttributes tag with the long header (6 bytes). Setting UseNetwork at "tag + 2" then
  flips a bit of its length and corrupts every tag after it. Find the flags byte after the real header. [Ultimate Assassin 3]
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
- A regex rename of identifiers also rewrote the relay's `"L"` string: guest departures were ignored. [Bow Man]
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
- A game-over clip that ends the game by itself after a timeout ends a guest's game before the host's; the next
  snapshot then pulls the guest back into the fight. Patch it to wait for the host on guests. [Ultimate Crab Battle]
- When every PC simulates every shot, short hit reactions (a 7-frame flinch) start a few frames apart. A mirror that
  corrects stopped clips at once cuts them off: correct only once this PC's clip has been at rest on the wrong frame
  for a few frames (crab pose corrections 0.22 -> 0.05 per snapshot). Never mirror the player's own launchers.
  [Ultimate Crab Battle]
- Always override `XMLSocket.onData`, or Flash parses messages as XML. [Bow Man]
- `x += f()` reads `x` before it calls `f`: a hook that changes `x` inside is overwritten; return the correction
  instead. [Bow Man]
- Random or timing-dependent changes to an object in flight (wind changing when another arrow lands, a random
  deflection) must be keyed to that object's own frame count, never to when a message arrives: guest copies run
  behind the host by the network delay, and a stalling host or guest moves the arrival by 30 frames. Start guest
  copies a few frames late and correct exactly when a report is still late. [Bow Man]
- A random event in the middle of a frame (step 3 of 6) can't be fixed by a report at the next frame: the guest's
  copy hits something in steps 4-6. Run the game's own deterministic test on the guest and hold the object there
  until the host's result arrives. [Bow Man]
- An arrow stuck in the ground has no `yanoe` clip, one stuck in an archer does: the game's deflection test only
  sees the latter. Read what a test actually reads before building a lab case for it. [Bow Man]
- Lab builds must set the lab relay before mods-info starts, or the INFO fallback asks the live server. [Ultimate Crab Battle]
  Safer: lab builds refuse the central relay's address outright (HOST, JOIN, LIST and INFO). [Territory War]
  Read the test mods-info URL when the download starts, not when the script loads. [Intrusion]
- Wrapping a class constructor in `_global` (`w.prototype = orig.prototype`) numbers every instance in creation
  order on every PC: a cheap net id for level objects. [Intrusion]
- A game's per-object `id` field can clash with yours: name the mod's fields `__pid`. [Intrusion]
- Off-screen culling, `Alive()` and `InGame()` read the global screen edges: with players apart, set the edges
  to the target player's view around each object's update, or enemies near a guest sleep and its bullets die.
  [Intrusion]
- Bullet constructors may reuse the shared `_root.p` point: capture the barrel position in a wrapper of the
  method that computes it. [Intrusion]
- Unnamed timeline parts (`instanceN`) are placed by the guest's own copy of the animation: skip them in a clip
  stream, it halves the bytes. [Intrusion]

- A mirror that removed `obj.mc._parent` for a vanished object took every penguin with it when the object was the
  raft's dog, which sits straight in the shared container (penguins have their own wrapper clip). Remove the
  object's own clip unless it lives in a per-object wrapper. [Raft Wars]
- A shared aim global still held the enemy's last value (315) when a player's turn began, so the host showed a
  wrong angle until the guest moved the mouse. Stream only values in the game's own aim range. [Raft Wars]

## AS3
- Applying snapshots between frames (socket events) was not enough for every clip: breaker attack clips still
  lost their `resumeWalk()` callback on the guest now and then. Queue the guest's frame switches and do them in
  `Event.RENDER` (`stage.invalidate()`, Flash Player 9+, works in Ruffle), after every frame script: 0 orphans in the
  sweep since. [Bad Ice-Cream]
- "Static" pickups that move by themselves (Bad Ice-Cream's teleporting cherries extend the static class, not the
  walking one) must follow the host's frame labels on the guest, never run their own `update()` there: it moves
  them with the guest's own `Math.random`. A per-object desync checker (guest snapshot vs host snapshot) finds this
  in minutes. [Bad Ice-Cream]
- Apply a guest's snapshot when it arrives (socket events come between frames), not inside the frame loop.
  Switching an object's frame in an ENTER_FRAME handler removes a child animation whose frame script is due that
  same frame; the script then runs with `parent == null` (#1009) and its callback into the game is lost. A probe
  showed it: switching a fruit exactly when its pop-in clip reached its callback frame threw from ENTER_FRAME and
  didn't from a Timer event. 67 of Bad Ice-Cream's clips call their parent like this. [Bad Ice-Cream]
- Timeline clips that call back into game code (a pop-in that ends with `parent.finishAppearAnimation()`, no
  `stop()`, so it loops) keep running on a guest that runs no game logic. If the guest switches the object's frame
  only when a snapshot arrives, the clip replays and a switch can orphan its frame script (#1009). Snapshots slow down
  while the host's game is paused (a help popup players read). Run on the guest, every frame, the same update the
  host's loop runs for such objects. Lab: hold the host's help popup open (`--help-hold 100`). [Bad Ice-Cream]
- A guest that gets the host's level while its own preloader or intro still runs: `gotoAndStop("game")` from
  there throws in `startGame`/frame scripts and the level never loads. Hold the level until the intro is over.
  Lab: the host plays alone, the guest window joins from its preloader (`--late-join`). [Bad Ice-Cream]
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
- After the campaign's last level the game goes to the level menu with a new, empty model; a host that kept
  sending snapshots from it made friends load the last level again. Send only on the game screen, and send a
  "host is in the menu" message so friends leave their level too. [Stealth Hunter 2]
- Assigning an Object where the game expects an Array throws #1034. Restore every swap in `finally`. [Intrusion 2]

## Games and portals
- Click-to-continue sponsor preloaders block labs: wait for them, or test the inner SWF. [Air Battle, Stealth Hunter 2]
- A portal score board on the end screen (BubbleBox's) shows the screen's MENU button only after it loads from the
  internet, so offline everyone is stuck there. Online, show MENU at once on the host. [Air Battle]
- Poki builds wait forever for an ad callback outside their page, and `ExternalInterface.call` throws #2067 each frame.
  The mod fixed both, online or not. [Bad Ice-Cream]
- A minigame's win path acts for the local player only: disable it on guests. [Stealth Hunter 2]
- MochiCrypt-wrapped games (`mochicrypt.Payload` binaryData) hide the real SWF: RC4 keyed with the payload's last
  32 bytes over the first 128 KB, then zlib. Unwrap it once and build from the inner SWF; the dead Mochi ad wait goes
  with it. [Ultimate Assassin series]
- A menu frame script that sets its level command back to 0 eats a command sent while the intro still plays:
  repeat it every frame until the screen changes. [Stealth Assassin]

## Launcher lobby
- Closing the game's bridge socket tells nobody: the launcher reports a `leave` when the game's process ends. Don't
  rely on an in-game "leave" in lobby mode. [Bad Ice-Cream]
- The launcher queues bridge messages for a game that hasn't connected yet and delivers them after `welcome`, so a
  client must not treat the first `msg` as proof the host just started. [Bad Ice-Cream]

## Process
- A one-shot "this changed" message (a door's lock gone) is lost on a friend that is still loading the room (its
  trigger list doesn't match yet), and a periodic state that doesn't carry the same field never repairs it. Resend
  such changes with the periodic state while they still hold. Lab: make a friend drop the next one. [Stealth Hunter 2]
- A short tap (4 frames) and its release can reach the host in the same frame when messages bunch (TCP, or the
  relay's order-keeping `--sim-jitter`), and the game never sees the key held. Latch newly pressed remote keys for
  a few host frames. [Bad Ice-Cream]
- In-game lab runners that count `age = frameNo - stepStart` with `stepStart = 0`: `frameNo` is already 1 on the
  first frame, so the first step's `age == 0` never fires. A title step before it hides the bug. [Bad Ice-Cream]
- With 7 other sessions' labs running (about 18 Ruffle windows), some windows sat on the game's preloader for good
  (its transition clip reset). Not reproducible alone. Let the runner spot it and run the scenario again, and keep
  each failing run's window logs (the next run overwrites them). [Bad Ice-Cream]
- The relay's legacy room answers a second `H|` with `E|A host is already connected` and keeps the socket open:
  a client that waits for the close hangs on CONNECTING. Finish on `E|` at once (`templates/as3/RelayClient.as`).
  [Bad Ice-Cream]
- Two sessions building the same mod wiped each other's files: one build folder per run. [Gun Mayhem 2]
- Host pacing capped at one skipped frame in three can't follow a friend whose PC runs below 2/3 speed: its backlog
  climbs to the hard wait limit and its input delay with it (GM2: 1 s at 14 fps). Skip every frame while a friend is
  well over its buffer. [Gun Mayhem 2]
- Sharing the hub checkout with other sessions: `git update-index` on the shared index replaced another session's
  staged file just as it committed. Commit your own files through a temporary index (`GIT_INDEX_FILE`). [Gun Mayhem 2]
- A friend that joins during a match gets a slot but no start message; if the host's wait counts every slot, the
  host waits for it forever. Count only players that got the start; the newcomer plays from the next match.
  [Gun Mayhem 2]
- The global relay sends `X` and closes the friends' sockets when the host leaves, so code that ends the match on
  "buffer ran dry after X" never runs: end the match in the socket's close handler too. [Gun Mayhem 2]
- Editing a bash lab script while it runs breaks the run (bash reads the file as it goes). [Gun Mayhem 2]
- Python heredocs with `\n` broke `.as` edits: do exact-match replacements from files. [Territory War]
- The relay's legacy `H|`/`J|` room (DIRECT) checks no version and takes 16 players. Have every guest send its
  version first and admit it only after that check (plus the player count); admitting on `J|` let a refused guest
  flash into the room with a boat. [Air Battle]
- A guest can finish a level by itself (a boat drifting into the open exit), so a lab's scripted shortcut steps must
  check whether the level is already over and note a skip instead of failing. [Air Battle]
- Ruffle desktop disappeared from `C:\Program Files` for a few minutes mid-session (a reinstall): let the lab also
  look for `tools/ruffle/ruffle.exe`. [Air Battle]
- An AS2 mods-info block copied without `N.GAME_ID` asks for `mods/undefined.json` and sends
  `RELAY|1|INFO|undefined`. Test it with a relay that knows the game only from a mods-info folder
  (`--mods-info file:///...`, no games.json). [Territory War]
- A lab script that opens the map view at turn start was refused: the game enables the map button only once the
  camera reaches the stick. Wait for the button's state, not a fixed delay. [Territory War]
- A lab that drives boats through shortcuts never tests the game's own input: also send real Flash KEY_DOWN/UP and
  MOUSE_DOWN events inside the SWF (`dispatchEvent` on the stage and the level container; never OS input). [Air Battle]
- Lab check on "key held, effect visible": compare only after the key stayed the same for 2 frames; stage listeners
  and the game's frame run in no fixed order. [Air Battle]
- A test tool that deletes and rewrites a folder the local relay is fetching from gives the relay a 404 at the wrong
  moment: rewrite files in place. [Air Battle]
- Save only what the player typed as the server: saving the address in use pinned an old server in three mods.
- A host connection can die without the friend's socket closing (seen on the live relay: the host was dropped,
  the guest heard nothing for 9 minutes). Ping both ways and end the session after ~15 s of silence. Test it with
  a relay that is suspended, not killed (NtSuspendProcess: sockets stay open). [Bow Man]
- A lab check that records only its first result hid two real bugs behind an earlier PASS: report every FAIL.
  [Raft Wars]
- A state check listing the objects from the battle's start reported penguins that had sunk as missing, which
  looked like an intermittent desync. Build checks from the live object lists. [Raft Wars]
- In the relay's legacy `H|`/`J|` room the relay sends `X` when the host leaves but keeps the guests connected:
  end the guest's session on `X` itself. [Raft Wars]
- A game's turn counter restarted at 0 in each battle, so a lab bot that remembered "already fired on turn N"
  never fired in the next battle and the run stalled. Reset turn-keyed lab state when a battle starts. [Raft Wars]
- A lab that calls the game's mouse handlers itself never tests the game's own aim-and-click path. Ruffle desktop
  accepts `WM_MOUSEMOVE`/`WM_LBUTTONDOWN`/`WM_LBUTTONUP` posted to its window without focus, so the lab can drive one
  window's mouse while the real cursor stays put: map the stage point below the 24-px menu bar, letterboxed, at the
  window's DPI. [Raft Wars]
- A host that sends its progress before the first Play sends `undefined` fields; a guest that joined at the menu
  then held NaN credits and lives. Send state only once it exists, and drop incomplete copies. [Raft Wars]
- Window captures (PrintWindow, then BitBlt) pick up whatever covers the lab window when other sessions' windows are
  on top. Capture inside the game: draw the stage into a BitmapData and print it; size it from the main timeline's
  `loaderInfo` (`stageWidth` is the window's size under noScale, 0 when minimized). [Ultimate Assassin series]
- Stopping a background shell on Windows leaves the lab it started running (and its relay holds the port): kill the
  lab's process tree by PID. [Ultimate Assassin series]
- A lab runner that blocks while it opens a new window takes the other windows' screenshots late; take pending
  shots first. [Stealth Assassin]
- "Wait N frames, then snap the guest's copy" counted the guest's frames, so a guest window at 20 fps snapped fine
  arrows. Send the host's frame count for the object and snap only when the guest's copy runs clearly past it.
  [Bow Man]
- A lab aim search run every frame dropped the guest window to 14 fps and looked exactly like a desync; run lab
  solvers once per turn, and log each window's frame rate. [Bow Man]
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
- Level objects that wait in a frozen spatial map until a camera reaches them enter the update list in an order
  that depends on each PC's camera. Give net ids where the game creates them, not where they first update.
  [Intrusion 2]
- A damage gate at the top of every `Damage()` override runs again in each `super.Damage()`: report a hit only
  from the outermost override (the first gate call seen per object class), or every hit counts twice. [Intrusion 2]
- Replaying a hit without the contact (hit point) throws in objects that read `contact.position`; send it along.
  [Intrusion 2]
- A game object updated by its level controller (a boss) is not in the world's object list: it needs its own
  registration and the nearest-player swap at the controller's call. [Intrusion 2]
- A teleported hero gets pulled back by camera bounds that open only after a level's scripted events: a lab fires
  the level exit through the trigger code instead of moving the hero there. [Intrusion 2]
- A screenshot fallback that copies the screen area of a lab window copies whatever covers it (other apps). Check
  with `WindowFromPoint` that the window itself shows at those points before copying. [Intrusion 2]
- Ruffle desktop wouldn't load a `file://` mods-info URL from a local SWF (timed out). Test the mods-info path
  through the relay instead: `--mods-info` with `pathlib.Path(...).as_uri()` (a hand-built URL with `C%3A` breaks
  urllib) and the mod's HTTP URL pointing at the relay port, so the download fails and `RELAY|1|INFO` answers.
  [Intrusion 2]
