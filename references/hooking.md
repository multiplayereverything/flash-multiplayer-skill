# Hooking the game

The game was written for one player, one keyboard and one world. Hooks make it see several players, take input from
the network, and let only the host decide.

## AS3: three ways in
1. **Patched copies of game classes** (unobfuscated games): the class is copied from `decompiled/` into the build at
   build time, edited with asserted exact replacements marked `// MOD`, and compiled over the original. Allowed only
   while `CheckNamespaces` reports 0 broken subclasses. Bad Ice-Cream patched 5 classes, Air Battle 26.
2. **New subclasses and engine components** (obfuscated games, where recompiling a class with subclasses breaks its
   protected namespace and gives #1070): `RemoteBuddy extends BuddyLee`; a `NetSync` added to the engine's own
   component set so it runs after every entity updates and before drawing.
3. **Polling** each frame from your own class, plus whole-class rewrites only of classes nothing subclasses.

## AS2: wrap at run time
- `_root` functions are properties: keep the original, replace it, call `orig.apply(_root, arguments)`. Same for class
  prototypes (`_global.Hero.prototype.Update`).
- **Wrap lazily:** run `ensureWrapped()` every frame and mark each wrapper (`f.__mymod = true`), because the game
  defines (and sometimes redefines) its functions on later frames.
- **Gate wrapper:** run the original only for the turn owner or only on the host. **wrapAfter:** call the original,
  then your hook (`findCurrentPlayer` → `onTurn`).
- Wrap `_root.attachMovie` and `Sound.prototype.start` to record effects and sounds for the snapshot.
- **Drive the mod from your own empty clip's `onEnterFrame`** at a fixed high depth, never `_root.onEnterFrame`: games
  replace it on later frames.
- **One state object** on `_global` (`_global.MYN`), and every closure re-reads it (`var N = _global.MYN;`).
- **Guest navigation guard:** on a guest, replace `_root.gotoAndStop/gotoAndPlay/play/nextFrame` (and protect them with
  `ASSetPropFlags`) so only the host's `GO|frame` moves the timeline. A guest that only draws must stub every game
  function the frames it visits call, because `gotoAndStop` runs that frame's script.
- Patched clip events call your hooks (`_global.MYN.mayAim(n)`, `fired(n)`); offline they return the original
  behaviour.

## Remote input
| How | Where |
|---|---|
| AS3: the input class answers the remote player's keys from the network (`isKeyDown` reads `Net.remoteDown(bits)` for P2's keys); the guest reads no game keys but forwards its real ones | Bad Ice-Cream |
| AS3: a player slot on each character; keys, aim and shots come from `Net.keysFor(slot)`; only slot 0 reads the mouse | Air Battle |
| AS3: each remote character has its own keyboard object fed by `inject(code, down)`; while it updates, the game's `keyboard` and `player` are swapped to it | Stealth Hunter 2 |
| AS3: around a remote hero's `Update()`, swap the game's own demo/override input seam, mouse position, `world.hero` and HUD; restore in `finally` | Intrusion 2 |
| AS2: replace `_global.Key` with a wrapper whose `isDown` returns the remote seat's bits while that seat has the turn (Ruffle ignores `Key.isDown = f`) | Territory War |
| AS2: `ASSetPropFlags(Key, "isDown", 0, 7)` then assign | Ultimate Crab Battle, Gun Mayhem 2 |
| AS2: give each online slot private key codes no real key makes (`1000 + 10*slot + action`), and translate only your own physical keys into your slot's codes, so two slots both bound to WASD don't move together | Gun Mayhem 2 |
| AS2: shadow `_root.Key` with a fake | Intrusion 1 |

Always keep reading F9 and the panel's keys from the real `Key`.

## "The player" swaps
Games store one player (`_root.knight`, `world.hero`, `engine.player`). Instead of patching 35 enemy classes:
- **Target swap:** around each enemy's, bullet's or trigger's update, set "the player" to the nearest living player,
  then restore it. One loop patch covers every class.
- **Stand-ins:** on the host, each guest gets an object inheriting the hero prototype, so enemy code treats it as a
  player; damage, pickups and heals are sent to its owner as events.
- Triggers and pits test every player. The freeze or activity area is the union of every player's view.
- The level fails only when every player is down (unless the design says one death fails the team).
- Focus-loss pause is disabled online.

## Guest gates
On a guest: no contact or damage events (Box2D contacts, `Damage()`), AI and weapons don't fire on their own, no saves,
and menus can't start, restart or quit a level ("The host picks the level."). Gate with one check
(`Net.isGuest`, `NetSync.replaying`), and auto-insert it where a signature repeats across many files (Intrusion 2
gated 41 `Damage()` overrides with one patch rule).

## Timing traps
- Timeline frame scripts drive logic: switching a clip's frame during its animation can call into a parent that isn't
  ready (#1009). Remove popups directly instead of playing their close animation.
- Send the snapshot before the popup message: the popup reads the score when it opens.
- AS3 Box2D contacts fire only inside `Step`. Hold poses after the guest's step.
- A level command may set the index at once and build a few frames later: wait until the world object changes.
- Remote copies outside a new room's grid cause #1010 every frame: keep them out during room switches.
- AS2 onEnterFrame order: clips created later run first; Ruffle runs an attached clip's first-frame code during
  `attachMovie`, Flash Player after it. Spawn-time random rolls get reordered, so per-object RNG in lockstep games.

## Rules
- Replace whole known blocks and assert the match count. Read files with LF line endings, write them back as they were.
- Mark every change `MOD` or route it through your package.
- With no session, every hook takes the original path.
