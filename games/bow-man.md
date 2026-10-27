# Bow Man Online

Relay id `bowman`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Two archers taking turns, AS2 SWF 6 (38 KB).

- **Path:** local multiplayer to online, 2 players, one archer each.
- **Connect:** RELAY (room codes, the default) or DIRECT (the host runs a relay on its own PC, friends type its IP:port; `H|name` / `J|name` to the relay's default room). A Mode button switches; DIRECT is saved only when picked. The DIRECT room has no size limit, so the host sends `FULL|id` to a third player, and `BYE` names its target: host messages reach every guest.
- **Sync:** events only. The shooter sends `FIRE` with angle and power; both games fly the same arrow; the host sends `LAND` with the true position, frame, HP, wind and its flight-frame count, and the guest corrects. Positions are rounded the way Ruffle stores `_x` (twips), or hit tests differ.
- **Shots while an arrow still flies** (turns flip on release, so players can) desynced through two effects: the wind change when an arrow lands, and the game's random arrow-on-arrow deflection. Each arrow now reads its wind through a hook (`addx += windFor(this) / 6`), and the host reports per arrow, by that arrow's own flight-frame count, a wind change (`AW`) or a deflection (`DEFL`, the course at the start of that frame). The guest starts arrows 3 frames late and replays them; when one still arrives late (a host stalls) it corrects exactly (n frames in the old wind: velocity off by n*dw/6, position by dw*n(n+1)/2). A deflection can happen mid-frame, so the guest runs the game's own deterministic distance test and holds both arrows there until the host's course arrives.
- **Build:** export the frame scripts, patch a few with strings that must match exactly once, append the mod to frame 1, import. The SWF stays version 6: raising it makes `undefined + 1` NaN and the arrow counter breaks.
- **SWF 6 traps:** identifiers are case-insensitive (`var n` overwrote `N`), there's no `try/catch` and no `getNextHighestDepth`; a regex rename once rewrote the relay's `"L"` string (guest departures were ignored) and the idle state `"off"` (into `"pOff"`).
- **Flash Player:** refuses XMLSocket from a local SWF 6 file, so this mod is Ruffle only.
- **Lab:** 9 scenarios, each in RELAY and DIRECT, plus `--solo`: default, `--mouse` (drags posted to the lab windows), `--delay/--jitter`, `--host-leaves`, `--guest-leaves`, `--late-join`, `--rapid` (each shot leaves 20 frames after the last), `--zoom`, `--deflect` (forces the deflection: arrows stuck in an archer keep the clip the game's test reads, ground arrows don't). Checks compare every arrow's landing on both screens and the guest's own copy (same hit or miss, no snapping, drift <= 5 px).
