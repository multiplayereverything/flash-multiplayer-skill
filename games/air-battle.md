# Air Battle Online

Relay id `airbattle`. Entry in [DIRECTORY.md](../DIRECTORY.md).

Box2D physics game played level by level (BubbleBox), AS3 SWF 9.

- **Path:** single player to co-op, 2-4 balloon boats.
- **Sync:** the host sends `S` every frame (40/s, about 250 bytes): only the bodies that moved, plus a full keyframe once a second, and events that call the game's own functions on the guest (fire, pickups, explosions, sounds). Guests keep a 2-snapshot jitter buffer, still step Box2D for debris, then put every synced body back at the host's pose with zero velocity.
- **Why not lockstep:** physics on two PCs drifts apart within a second.
- **Hooks:** 26 patched game classes; enemies target the nearest living boat; only slot 0 reads the mouse; contacts are dropped on guests.
- **Late join:** a boat appears at once (`NP` to everyone, `LV` and `CU` catch-up to the joiner).
- **Lab:** host, a guest joining from the public list, a late guest joining by code, a wrong-code window: 37 of 37 checks, 0 script errors. Offline checks for messages, the relay and mods-info.
- **Lessons:** never sync derived bodies (the propeller follows the hull); a launcher's `relay=` address must not be saved as the player's own.
