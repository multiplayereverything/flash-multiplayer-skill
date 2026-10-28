# Ultimate Assassin 1, 2 and 3 (Games121)

| | UA1 | UA2 | UA3 |
|---|---|---|---|
| Engine | AS2, SWF 8 | AS3, SWF 10 | AS3, SWF 15 |
| Wrapper | none | MochiCrypt | MochiCrypt |
| Code | one `onClipEvent(enterFrame)` on the controller clip, obfuscated function names | one 3,205-line MainTimeline (`ee` loop) | one 4,959-line MainTimeline (`ee` loop) |
| Relay id / protocol | `ua1` / `ua1-1` | `ua2` / `ua2-1` | `ua3` / `ua3-1` |
| QA | lab, 2-4 players, late join, RELAY and DIRECT, lag | same | same |

Same family as Stealth Assassin (`games/stealth-assassin.md`): top-down stealth, kill the green target, reach the exit.
`ultimateassassin.swf` and `ultimateassassin2.swf` are the same file; it is Ultimate Assassin 2.

## How the co-op works (all three)
Each PC moves its own assassin; the host runs guards, bullets/catching, targets and level flow. As in Stealth
Assassin, the guard AI reads one "player" field (`oyn.adam` in UA2/UA3, `_root.adam` in UA1), so it is swapped to
the nearest living player around each guard's turn and to the player a bullet hits; friends are puppet copies of
the game's own assassin sprite. Extra targets (+1 per extra player, +1 per late joiner) come from the level:
next to guard start points, on open floor; only the last kill opens the exit. The dead watch; the game's own
fail flow runs only when everyone is dead. Online is the default (room codes, public list); DIRECT is a MODE button.

## UA2 and UA3 (AS3)
- **Unwrap first:** `tools/unmochi.py` gives the inner SWF; build and decompile from that.
- **No class for the assassin sprite:** `new` needs one. The build adds a SymbolClass tag that links the sprite to a
  new `dynamic class X extends MovieClip` (stub + `-importScript`), placed right after the sprite's DefineSprite:
  linked in the first SymbolClass tag (before the definition) Ruffle logs "Character ID collision" and the game
  breaks.
- **Guests skip the AI block but keep the cone drawing,** which sits after it in the same guard loop.
- **Levels:** UA3 picks a level on frame 15 (`dizi` is built there, frame 16 sets the guards up), UA2 on frame 19/20;
  extra targets are added between the two so the game's own setup prepares them.
- UA3's FileAttributes tag uses the long tag header (see traps).

## UA1 (AS2)
- The game loop's function names are control characters (`§\x01§`), so the loop isn't recompiled: five calls are
  patched into its p-code (`uaPre`, `uaGuList`, `uaPick`, `uaUnpick`, `uaPost`), and the mod's AS2 goes in as new
  DoAction tags.
- The guard loop's `for-in` source is replaced (guests get `{}`, the host gets the level's guards without the
  extras), and `_root.adam` is moved to the picked player per guard and put back after the loop.
- The "caught" function is wrapped at run time on the controller clip.

## Lab
One runner for the series (`lab_runner.py` in the mods' shared folder), the same scripted steps per game. Lessons:
- Pick lab levels that have guards (UA3's chapter 1 has none, UA2's first two teach).
- These games open the exit only while no guard sees anyone: the lab hides everyone out of every guard's sight first.
- Window captures fail when other windows cover the lab's. An in-game capture (draw the stage into a BitmapData
  at half size, print it as hex, the runner writes a PNG) works no matter what covers the window; size it from the
  main timeline's `loaderInfo`, not `stageWidth` (0 for a minimized window under `noScale`).
- On Windows, stopping a background shell doesn't stop the lab it started: kill the lab's process tree by PID.
