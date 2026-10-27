# Ultimate Crab Battle Online

Relay id `ucb`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Single-player boss-fight shooter, AS2 SWF 6, obfuscated (FFDec's AS1/2 deobfuscator makes it readable, but there are
no functions worth hooking: the fight is timelines and clip events).

- **Path:** single player to co-op, up to 4 ships against the same crab, one shared HP bar and continues.
- **Connect:** RELAY (default: room codes, public list, mods-info) and DIRECT (`H|`/`J|` to a relay on the host's PC,
  IP:port) behind a MODE button. In DIRECT the host checks the version (`HELLO|name|version`, then `BYE|id|reason`)
  and caps the room at 4, because the relay's legacy room does neither; guests leave on `X` themselves.
- **Sync:** each player flies their own ship locally and sends its pose every 2 frames; shots go to the host as events
  and the host spawns the same projectile clips, which do the real damage. Remote torpedoes are held under their ship
  for the launcher's 6 frames; remote lasers replay the laser's explosions. A "world mirror" sends every `_root` clip
  up to 7 levels deep, keyed by depth path (instance names differ between PCs), as a delta every 3 frames and in full
  every 68. Stopped clips are corrected only once the guest's clip is at rest on the wrong frame for 8 frames; the
  player's own launchers are never mirrored. Crab HP, team HP and score come from the host; hits on a guest's own
  ship go to the host as `H|n`.
- **Late join:** a friend can join mid-fight, also straight from the loader screen (launcher `join=`), and drops in.
- **Host leaves:** guests see "The host closed the room." and keep playing alone.
- **Lab:** RELAY and DIRECT, 3 players with a late join, 4 players with a 5th refused, join from the loader, 80+30 ms
  lag, refusals, host leaving, mods-info over HTTP and over the relay, solo, release boot. At the end each guest's crab
  HP, team HP, the score shown on its HUD and the fight timeline equal the host's exactly. Control runs
  (`--no-torpedo-hold`, `--no-laser-fx`) show which checks can fail. Sessions start through the panel's own buttons,
  and the real-keyboard path is checked at boot. Real input: posted key messages to the lab window (F9, 1, Ctrl,
  arrows, A all work while hosting) and real browser clicks in Ruffle's web player (MODE, typing, HOST, X, ONLINE).
  That click test found 1.1.0's panel dead to real clicks (a handler on the panel clip); fixed in 1.1.1.
- **Lessons:** a click-blocking handler on a parent clip kills its buttons; AS1's 64 KB function-body cap; jumps to not-yet-loaded frames are ignored silently; frame scripts run
  after enterFrame handlers, and bound text fields show the last value written; a game-over timeout can end a guest's
  game first; setting `_x` inside a tween freezes it; Ruffle's fps drops as more windows run.
