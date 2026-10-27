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

## Flash Player 32
- Refuses every HTTP load from a local SWF (#2048, even with a crossdomain.xml): mods-info needs the relay INFO
  fallback. [Stealth Hunter 2, Air Battle]
- Refuses XMLSocket from a local SWF 6 file, even with an SWF 8 header and UseNetwork. SWF 6 mods are Ruffle-only.
  [Bow Man]
- Needs the UseNetwork flag to open sockets from a local file. [all]
- The release player shows no script errors: one throwing message froze the reader. Try/catch per message. [Stealth Hunter 2]
- Throttles hidden windows. Synthetic key messages never reach it. [Gun Mayhem 2]
- A Flash Player host with a Ruffle friend gave a per-frame "Invalid object" error storm on the friend; never solved,
  and that mod dropped Flash Player. [Stealth Hunter 2]
- Starting the mods-info download during session start changed lab timing; test builds skip it unless given a test
  URL. [Stealth Hunter 2]

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
- A regex rename of identifiers also rewrote the relay's `"L"` string: guest departures were ignored. [Bow Man]
- `String(number)` keeps 15 digits: send the remainder for exact state. [Gun Mayhem 2]
- `hitTest(x, y, true)` takes stage coordinates, so the camera position is gameplay state. [Gun Mayhem 2]
- `gamepaused` flags don't freeze timeline animations or `_root.onEnterFrame`: a netplay wait must freeze them all.
  [Gun Mayhem 2]
- Clips created later run their onEnterFrame first; a clip's onEnterFrame runs before the root frame script.
  [Gun Mayhem 2, Raft Wars]
- `gotoAndStop` to the frame you're on doesn't re-run it: go through the frame before. [Gun Mayhem 2]
- A clip that doesn't exist yet on frame 1 gives NaN when you set it: move its frame instead. [Territory War]
- Setting `_x` inside a tween freezes the tween. [Ultimate Crab Battle]
- Always override `XMLSocket.onData`, or Flash parses messages as XML. [Bow Man]
- Lab builds must set the lab relay before mods-info starts, or the INFO fallback asks the live server. [Ultimate Crab Battle]
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

## AS3
- `flash.display.Sprite` is sealed: dynamic fields need a `MovieClip`. [Bad Ice-Cream]
- `var` is hoisted to function scope: a local `key` shadowed a `key()` method (#1006), and two locals with one name
  merge. Give each a unique name. [Stealth Hunter 2]
- Object key order isn't stable: sort by slot. [Stealth Hunter 2]
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
- Two sessions building the same mod wiped each other's files: one build folder per run. [Gun Mayhem 2]
- Python heredocs with `\n` broke `.as` edits: do exact-match replacements from files. [Territory War]
- The relay's legacy `H|`/`J|` room (DIRECT) checks no version and takes 16 players. Have every guest send its
  version first and admit it only after that check (plus the player count); admitting on `J|` let a refused guest
  flash into the room with a boat. [Air Battle]
- A guest can finish a level by itself (a boat drifting into the open exit), so a lab's scripted shortcut steps must
  check whether the level is already over and note a skip instead of failing. [Air Battle]
- Ruffle desktop disappeared from `C:\Program Files` for a few minutes mid-session (a reinstall): let the lab also
  look for `tools/ruffle/ruffle.exe`. [Air Battle]
- Save only what the player typed as the server: saving the address in use pinned an old server in three mods.
- A lab runner that blocks while it opens a new window takes the other windows' screenshots late; take pending
  shots first. [Stealth Assassin]
