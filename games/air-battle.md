# Air Battle Online

Entry in [DIRECTORY.md](../DIRECTORY.md).

Box2D physics game played level by level (BubbleBox), AS3 SWF 9.

## Co-op build 2.0 (Ruffle Together)
- **Path:** single player to co-op, 1-4 balloon boats. Every PC runs the same game in lockstep in Ruffle Together;
  local co-op is added to the SWF, with no network code.
- **Release:** flash-games 90f9eda (`games/airbattle/AirBattle_online.swf`), `--coop-keys air-battle` (built in; the
  same slots as gun-mayhem-2: P1 arrows + Z fire + Down/X to turn the cannon, P2 W A D + T + S/Y, P3 and P4 numpad).
- **Changes:** 8 patched classes plus one Coop class:
  - per-slot keys, and a PLAYERS 1-4 picker on the main menu;
  - tinted balloons and P1-P4 tags;
  - enemies target the nearest flying boat;
  - ammo refills the boat that touched it (found through the balloon's owner body);
  - the level fails only when every boat is down;
  - fire is edge-triggered per slot; only slot 0 gets the stage mouse listener;
  - a downed boat can't shoot (only with more than 1 boat, so solo stays the original).
- **Box2D in lockstep was fine:** replays matched. The relay-era "physics drifts" note is about two PCs running physics
  on their own, not lockstep.
- **QA:** lab-3p+. Replays identical twice for 2, 3 and 4 boats; 1 player matches the untouched original object for
  object (frames 600-3000); coop-lab relay and direct with 2, 3 and 4 players, no desync; a 4-player leave test (one
  friend killed after 40 s), the other 3 in sync to the end. Last checked on 1.0.3.7 (2026-10-30), NOT re-checked on
  1.0.8.
- **Not proven:** windows_lab (it failed only on late frames, 4 against a limit of 3, at 100% CPU from other labs; a
  known-good build did worse at the same time); two real PCs; a mouse per slot (only P1 aims by mouse; the other slots
  turn the cannon by keys).
- **Tools:** the mod's own tools include a wrapper that loads coop-lab's `lab.py`, gives each player a temp
  `--save-directory` and adds `--leave-after S` (the flag is stripped from `sys.argv` before `lab.py`'s main builds
  its parser).

### Lessons
- Park each extra player (hold its spawn position, zero velocity) until that slot presses a key, or extra boats fall
  into the water.
- Ruffle gives a fill of alpha 0 no mouse hits; use 0.01.
- Never place or size co-op UI by TextField metrics: device fonts differ, they are about 0 headless, and positions are
  in the sync fingerprint.
- Ruffle window screenshots include a 24 px menu bar, while script clicks are in stage pixels.
- Chat on "/" (1.0.3.7+) opens only on the main-row slash (191); numpad "/" (111) doesn't clash.

## Relay mod 1.1.1 (retired)
Kept, not shipped. Relay id `airbattle`, ONLINE room codes on the central relay or DIRECT to a relay on the host's PC.
What it taught:
- **Snapshot sync:** the host sent only the bodies that moved every frame, a full keyframe once a second, and events
  that call the game's own functions on the guest. Guests put every synced body back at the host's pose.
- **Physics on two PCs** stepping on their own drifted apart within a second, so that mod didn't use lockstep.
- Never sync derived bodies (the propeller follows the hull).
- A launcher's `relay=` address must not be saved as the player's own.
- Admit DIRECT guests only after their version check.
- A portal score board can hide the last screen's MENU forever, so show it online.
- Flash Player 32 was tested with lab copies that had their flashvars baked in and reported through `D|` lines.
