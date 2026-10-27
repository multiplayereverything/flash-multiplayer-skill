# Air Battle Online

Relay id `airbattle`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Box2D physics game played level by level (BubbleBox), AS3 SWF 9.

- **Path:** single player to co-op, 2-4 balloon boats.
- **Sync:** the host sends `S` every frame (40/s, about 250 bytes): only the bodies that moved, plus a full keyframe once a second, and events that call the game's own functions on the guest (fire, pickups, explosions, sounds). Guests keep a 2-snapshot jitter buffer, still step Box2D for debris, then put every synced body back at the host's pose with zero velocity.
- **Why not lockstep:** physics on two PCs drifts apart within a second.
- **Hooks:** 26 patched game classes; enemies target the nearest living boat; only slot 0 reads the mouse; contacts are dropped on guests.
- **Late join:** a boat appears at once (`NP` to everyone, `LV` and `CU` catch-up to the joiner).
- **Connecting (1.1):** ONLINE room codes on the central relay by default; DIRECT as a second tab, `H|name` / `J|name` to the legacy room of a relay on the host's PC (port 7790). Only the first line differs. The legacy room has no version check, so guests send `VE|version` first and the host admits them only after it checks out (`KO|id|reason` for a wrong version or a fifth player). DIRECT is saved only when picked; launcher flashvars count for one run.
- **Cosmetic events (1.1):** wall sparks (`WP`: position, direction, strength) and shrapnel marks (`SH`) replay the game's own particle and mark code; guests draw exactly the host's count.
- **Lab:** host, a guest joining from the public list, a late guest joining by code, a wrong-code window (wrong version in DIRECT): RELAY 40/40, DIRECT 40/40, 4 players 50/50 (both modes), lag + host leaving 42/42, the last level 5/5, solo 14/14, 0 script errors. Levels 3, 5 and 17 also checked for desync (none). Offline checks for messages, the relay and mods-info.
- **Feel (1.1.1):** a guest's own cannon aim and burner flame follow its own mouse and keys at once (the host still flies the boat and decides the shots); name tags stack when boats are close. Lab `--realinput` sends real Flash KEY_DOWN/UP and MOUSE_DOWN events inside the SWF, so the game's own input path is what gets tested; 150 ms +-50 ms lag runs pass with exact positions.
- **Flash Player 32:** tested with lab copies that have their flashvars baked in (the projector takes none) and send their results to the relay as `D|` debug lines (the release player prints no trace). Flash Player host + Ruffle guest 29/29, all three windows in Flash Player with a late joiner 42/42.
- **Lessons:** never sync derived bodies (the propeller follows the hull); a launcher's `relay=` address must not be saved as the player's own; admit DIRECT guests only after their version check; a portal score board can hide the last screen's MENU forever, so show it online.
