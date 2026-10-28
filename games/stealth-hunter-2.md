# Stealth Hunter 2 Online

Relay id `sh2`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Stealth campaign (RacSeven), AS3 SWF 11, obfuscated and wrapped: the real game is an inner SWF stored in a binaryData tag with its first and last 999 bytes swapped.

- **Path:** single player to co-op, 2-4 players.
- **Sync:** host snapshot `P` at 15 Hz (players as `@id`, actors as `Class#n`), events for alarms, objectives and minigames, a 1 Hz roster. Guests smooth (close 35% of the gap each frame) and extrapolate up to one interval. Later each player moves their own character locally (`ME` about 30/s) and the host's copy walks to it, so guards still hear footsteps.
- **Hooks:** recompiling any subclassed class broke its protected namespace (#1070), so the mod uses new subclasses (`RemoteBuddy`), an engine component that runs after every entity update, and whole rewrites of classes nothing subclasses. Each remote player has its own keyboard object; while it updates, the game's keyboard and player are swapped to it.
- **Rule chosen:** any player's death fails the mission for the team.
- **Lab:** 2, 3 and 4 players, solo, lag, a campaign sweep through every level, Flash Player windows reporting through the relay's `D|` lines.
- **Flash Player:** a Flash Player host with a Ruffle friend gave an error storm on the friend; the mod became Ruffle only.
- **Connections:** RELAY (room codes on the central relay) is the default; DIRECT (`H|name` / `J|name` to a relay on
  the host's PC) uses port 7790 when the address has none.
- **1.1 (2026-10-28):** three fixes found by the 3-4 player lab, each with a lab step that makes the fault happen on
  purpose and failed before the fix: lock-gone messages resent with the periodic trigger state (a friend that missed
  one kept "Pick Lock" on an open door), a dropped level load asked for again (a friend stayed in level 0's map for a
  whole 4-player run, then 308 script errors at the checkpoint restart), and friends follow the host to the menu
  (after the finale they loaded it again). Lab on one PC: 2p 178/178 (relay and direct), 3p 282/282, 4p 389/390,
  solo 9/9, sweep 2385/2386. Not played between two PCs on this build.
