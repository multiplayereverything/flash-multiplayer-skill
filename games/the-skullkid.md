# The Skullkid Together

Released 1.0: flash-games e8db705, `games/theskullkid/TheSkullkid_online.swf`, proven on Ruffle Together 1.0.8,
2 players. QA (hub level): lab-2p. Entry in [DIRECTORY.md](../DIRECTORY.md).

The Skullkid (2002; the title screen says "made by chance"), SWF 6, AS1/AS2, 550x400, 18 fps, 13 root frames, about
5 minutes: a chainsaw floor (saw through desks, a copier, employees), a shootout (duck and stand to shoot, one health
bar), a boss. The copy used came from webdesignmuseum.org.

- **Path B, 2 players.** The kid is about 150 px wide on a 550 px screen and every floor is one corridor, so two fit.
- **Play:** on floor 1 each kid walks and saws alone, and whoever reaches a screen edge scrolls (the other is
  dragged). On floors 2-3 the team walks together and each shoots or saws alone.
- **Key map:** the SWF calls `coop.keys`: slot 0 gets the game's codes (arrows, Space, S), slot 1 codes the game never
  reads (Home, End, PgUp, PgDn, Insert); `local:` is arrows, Space, S. Launch `--coop-keys gun-mayhem-2
  --coop-players 2`. The game's input is `onClipEvent(keyDown)` + `Key.getCode()`, so player 2's kid is driven by the
  mod from `coop.buttons(1)` press and release edges, copying each controls clip's handler.
- **Route:** an AS2 rewrite (81 scripts, every regex asserts its count) and FFDec `-importScript`, plus `coop.as` as a
  new DoAction on frame 1 (`tools/ffdec/InsertAction.java`). Player 2 is a `duplicateMovieClip` of the kid per floor.
  The kid's own walk animations moved `_root.skullkid._x`; they are rewritten to `_parent._x` so a copy moves itself.

## QA
On the Ruffle Together 1.0.8 release exe: solo = the original, 4810 of 4810 frames over the whole game; replays twice
identical to the ending with both players, with only P1 acting and with only P2 acting; losing the shootout and
retrying; coop-lab relay (40 ms + jitter) and direct, 4900 frames, no desync; leave tests on floor 1 and mid-shootout
(the host plays on in sync, P2's kid is removed: traced); physical keys posted to two real windows on the launch line
and in solo, PASS; the whole game in two real windows to the ending (team health held full there).

Not proven: played by people, two PCs, the central relay.

## Lab
Scripts that play without reacting: a fight planner reads each shootout's timing from the employees' own frame scripts
(check frame, damage frames, loop) and a replay finds each fight's start tick; the boss's blocking tick is found the
same way. Tick-exact in replays; input delay moves them in sessions.

## Lessons
- Input on `keyDown` only, with no key repeat in scripted sessions, made the boss unkillable (traps.md).
- A dragged second hero entering a scroll zone starts scrolling with no key held: keep dragged heroes out of zones.
- A walk animation that moves `_root.hero` from the hero's own frames moves player 1 when a copy plays it.
