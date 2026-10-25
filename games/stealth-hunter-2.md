# Stealth Hunter 2 Online

Relay id `sh2`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Stealth campaign (RacSeven), AS3 SWF 11, obfuscated and wrapped: the real game is an inner SWF stored in a binaryData tag with its first and last 999 bytes swapped.

- **Path:** single player to co-op, 2-4 players.
- **Sync:** host snapshot `P` at 15 Hz (players as `@id`, actors as `Class#n`), events for alarms, objectives and minigames, a 1 Hz roster. Guests smooth (close 35% of the gap each frame) and extrapolate up to one interval. Later each player moves their own character locally (`ME` about 30/s) and the host's copy walks to it, so guards still hear footsteps.
- **Hooks:** recompiling any subclassed class broke its protected namespace (#1070), so the mod uses new subclasses (`RemoteBuddy`), an engine component that runs after every entity update, and whole rewrites of classes nothing subclasses. Each remote player has its own keyboard object; while it updates, the game's keyboard and player are swapped to it.
- **Rule chosen:** any player's death fails the mission for the team.
- **Lab:** 2, 3 and 4 players, solo, lag, a campaign sweep through every level, Flash Player windows reporting through the relay's `D|` lines.
- **Flash Player:** a Flash Player host with a Ruffle friend gave an error storm on the friend; the mod became Ruffle only.
