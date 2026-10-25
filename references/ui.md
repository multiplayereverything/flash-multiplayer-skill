# The online panel

Built in code inside the game (AS3: a top-level Sprite re-raised to the top each frame; AS2: drawing API and
`createTextField` with `_sans`, counter-moved against the camera with `ui._x = -_root._x`). It matches the game's HUD
style. No external windows or web pages.

## Opening it
- An **ONLINE** button in the game's own menu ("ONLINE PLAY", "VS Online", "PLAY ONLINE", "ONLINE CO-OP"), made with the
  game's own button class where there is one.
- **F9** (key code 120) anywhere, read from the real keyboard, propagation stopped. Esc closes it.
- FlashVar `online=1` opens it at start; `join=<CODE>` opens it and joins (the launcher's one-click join).

## Contents
| Part | Behaviour |
|---|---|
| Name | saved |
| HOST A ROOM | connects to the relay and shows the 5-letter code big, in the panel and in the corner tag |
| ROOM CODE + JOIN | Enter in the field joins; the code is cleaned (`0`→`O`, `1`→`I`) |
| PUBLIC ROOMS | `RELAY|1|LIST|<game>` on its own socket; Refresh; click a row to join |
| "List my room publicly" | on by default |
| SERVER | blank means the mod's built-in relay (yours). Saved only when the player typed it |
| Status line | the last relay reason (`E|...`), the mods-info notice or "update available" line |
| LEAVE | ends the session |

Corner tag, always visible during a session and clickable: `ONLINE  F9`, `HOST ABCDE 2/4  F9`, `P2  33 ms  F9`. A turn
banner where turns matter (`YOUR TURN` in green). Banners time out after about 5 s.

While the panel is open or a field has focus, game keys are off (clear the game's key state; AS2 park the game's Mouse
listener so a click on the panel doesn't fire a shot). Enter and Space press the focused button.

## Online is the default
- HOST and JOIN use room codes on your relay. Most mods have no other mode.
- A mod that keeps Direct IP or LAN starts on ONLINE and saves the mode only when the player presses the mode button
  (ignore old saved mode keys).
- Save only the server the player typed. A `relay=` FlashVar is for this run only. A saved value equal to the built-in
  relay counts as blank. Saving the address in use pins an old server forever and hides every later server move.
- Lab builds never save settings. SharedObjects at path "/" are shared by every local SWF in that player, and lab
  builds would leak their lab address into the real game.

## Words
Say what happened and what to do next: "Wrong room code. Check it with the host.", "The host left the room.",
"Online play needs version 1.2 or newer. Get it at ...", "The host picks the level." Empty lists say why they are empty
("No public rooms. Host one, or ask a friend for a code."). Contrast at least 4.5:1.

## FlashVars
| Name | Meaning |
|---|---|
| `join=<CODE>` | join this room at start |
| `name=<name>` | player name |
| `relay=host:port` | server for this run (never saved) |
| `online=1` | open the panel at start |
| `modinfo=<base url>` | test mods-info source |
| lab only: `lab=host|guest|solo`, `players`, `late`, `badcode`, `scenario` | test roles (avoid the name `end`: it never reached the script in Ruffle) |

AS3 reads them from `stage.loaderInfo.parameters`, AS2 from `_root`. Ruffle passes them as `-Pkey=value`.
