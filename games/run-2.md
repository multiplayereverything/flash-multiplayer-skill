# Run 2 Together

Released 1.0: flash-games 8a4d0b9, `games/run2/Run2_online.swf`, proven on Ruffle Together 1.0.8, 2-4 players.
QA (hub level): lab-3p+. Entry in [DIRECTORY.md](../DIRECTORY.md).

Run 2 (2011), AS3 SWF 10, 550x400, 40 fps (the game sets 30 from its save), 5 frames, Away3D 3.x software 3D, name-
and flow-obfuscated. A copy was found on webdesignmuseum.org (Cloudflare blocks plain downloads; the page's own fetch
in a browser works).

## Why not one shared tunnel
The level turns around its one runner: step onto a wall and the whole tunnel rotates so it is the floor, and the
player is a static. Two runners would need two "downs".

## A copy of the game per player (new path B pattern)
- The document class is replaced by a subclass of it (`tools/ffdec/SetDocClass.java`); no game class is recompiled.
  Solo, it asks `coop.players` once and does nothing.
- In a session it calls `Loader.loadBytes(loaderInfo.bytes, new LoaderContext(false, new ApplicationDomain(null)))`
  once per friend, so each copy has its own statics. Copy N sits at x = 2000 * N on the stage and gets
  `coop.camera(N, 2000 * N + 275, 200, 1)`.
- Every frame it writes each copy's key statics through `contentLoaderInfo.applicationDomain.getDefinition(...)` and
  its public root fields (pause/reset keys), mutes friends' music, swaps a friend's save to `Run2-coop-pN` after the
  copy has read the host's progress, and lets friends pick a character with their own LEFT/RIGHT (the original picks
  by mouse only).
- **Key map:** `coop.keys` sets the game's map at session start, so the launch line is
  `--coop-keys gun-mayhem-2 --coop-players 2-4`. Each slot gets game codes the game never reads hard-coded (it reads
  Space, Enter, Esc and comma directly), so one player's key never reaches another player's copy: slot 0 37/39/38 +
  R 82 + P 80, slot 1 65/68/87 + 81, slot 2 74/76/73 + 85, slot 3 100/102/104 + 103;
  `local: LEFT=37,65 RIGHT=39,68 FIRE=32,38,87 ALT=82 MENU=80,27`.
- **Cost:** one copy runs 1100 frames headless in about 2 s; 4 copies drawn in two real windows held 30 fps.
- **Limits:** friends have no mouse in their copy (editor, options and pause are host only); you don't see the other
  runners; friends' progress isn't kept for the next session.

## QA
Replays identical with 2/3/4 players; solo = the original; every level and the bonus level to the end with 4 players
(completed by a lab warp, not played through); coop-lab 2/3/4 relay and direct; leave tests with 4 and 2 players;
physical keys in two real windows on the launcher line; two real windows smooth (2 players, and 4 games drawn).

Not proven: the central relay, two real PCs, people playing it.

## Lab
Lab builds switched by constant: `--view S` (every camera shows slot S; identical fingerprints prove the camera is
picture only), `--warp N` (completes every copy's level the game's own way every N frames), `--keys-probe` (traces the
game key codes each copy gets), `--copies 4` (4 copies with 2 players, to measure drawing). The mod's own tools also
run a headless host plus N friends with a leave test, a memory gate, and a physical-keys lab.

## Lessons
- A world built around its one player can still get local co-op: one copy of the SWF per player, each in its own
  ApplicationDomain with its own `coop.camera`.
- A headless session needs `--coop-script` on every player, or friends get no input and it still reports no desync.
- `loadBytes` content keeps getting `enterFrame` after `unloadAndStop()`: remove its loop listener first.
- Flow-obfuscated AS3: `-config autoDeobfuscate=1` for reading; hook through a document-class subclass.
