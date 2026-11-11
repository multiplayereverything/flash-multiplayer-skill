# Ultimate Crab Battle Online

Released 2.1: flash-games 5d8945e (2026-10-31), `UltimateCrabBattle_online.swf`, built on Ruffle Together 1.0.3.8,
`--coop-keys ultimate-crab-battle`, 2-4 players. QA (hub level): lab-3p+. Entry in [DIRECTORY.md](../DIRECTORY.md).

Single-player boss-fight shooter, AS2 SWF 6, obfuscated (FFDec's AS1/2 deobfuscator makes it readable, but there are
no functions worth hooking: the fight is timelines and clip events).

- **Path:** single player to co-op: local co-op added to the SWF, up to 4 ships against the same crab, one shared HP
  bar and continues. The relay mod 1.1.2 is retired and kept only as `_relay.swf`.
- **Players:** every player gets a ship from `coop.players`; there is no join step. `coop.keys` on frame 1 gives every
  slot and PC the game's own keys (arrows, A fire, Ctrl skip, 1-3 difficulty, Y/Z continue, N). Each ship follows
  `coop.buttons(slot)`.
- **"The player":** the game reads `_root.player` everywhere, so the instance name `player` moves between ships every
  2 frames; every ship gets hit, and enemies aiming at `_root.player` switch targets with it.
- **Leaving:** `coop.events` `leave N` hands `player` back to P1, then removes that ship.
- **One keyboard:** outside a session P2 plays with I J K L + U, P3 with T F G H + R, P4 with numpad 8 4 5 6 + 0; P2-P4
  press fire on the menu to join.
- **QA:** on the 1.0.3.8 release exe with a throwaway `--save-directory`: replays identical twice over 2700 frames;
  coop-lab with 2/3/4 players over relay and direct in sync; a friend leaving at frame 1500 with 3 and 4 players,
  the others in sync to the end; solo is the original (plain Ruffle lab).
- **Not proven:** two real PCs, two real windows, the leaver's ship disappearing on screen; not re-run after 1.0.3.8.
- **Lab tool:** a wrapper loads coop-lab's `lab.py` as a module and patches `player()` so each headless player gets its
  own `--save-directory` and `--cache-directory`, plus `--leave-at N`.

## Relay mod 1.1.2 (retired, kept as `_relay.swf`)
Relay id `ucb`. Each player flew their own ship locally and sent its pose every 2 frames; the host spawned the real
projectiles and a "world mirror" sent every `_root` clip by depth path. RELAY and DIRECT behind a MODE button; the
central relay never listed `ucb`, so DIRECT was the way in. Flash Player 32 can't play it online (it refuses sockets
from a local SWF 6 file). Its lab checked late join, host leaving, lag and real clicks in Ruffle's web player.

## Lessons
- When every slot's `coop.keys` map gives the same codes, `Key.isDown` sees everyone's keys at once (fine for menus);
  in the fight hide the movement and fire codes (37-40, 65) from the game and move every hero from `coop.buttons(slot)`.
- `--coop-replay` always counts as a session (`coop.players` answers even with `--coop-players 1`), so check solo in
  plain Ruffle.
- SWF 6: two locals differing only by case are one variable.
- A lab FlashVar path that feeds scripted keys must turn the co-op API off.
- From the relay mod: a click-blocking handler on a parent clip kills its buttons; AS1's 64 KB function-body cap;
  jumps to not-yet-loaded frames are ignored silently; frame scripts run after enterFrame handlers, and bound text
  fields show the last value written; setting `_x` inside a tween freezes it; Ruffle's fps drops as more windows run.
