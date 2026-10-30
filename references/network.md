# Network

## The relay (star mode)
Your relay (`relay/`): one TCP port for every game you make, built into each mod as its server (mods-info may name
another, and players can type one). Messages
are NUL-terminated UTF-8 text: AS2 `XMLSocket.send` adds the NUL itself, AS3 uses a raw `flash.net.Socket`
(`writeUTFBytes(s); writeByte(0); flush()`), which works better in Ruffle than AS3 XMLSocket.

| Client sends (first line) | Relay answers |
|---|---|
| `RELAY|1|HOST|<game>|<version>|<public 0/1>|<room name>` | `ROOM|<code>|<max>`, then `W|0` |
| `RELAY|1|JOIN|<game>|<version>|<CODE>|<name>` | `W|<id>` (1, 2, ...) |
| `RELAY|1|LIST|<game>` (own connection) | `LIST|code,players,max,name;...` |
| `RELAY|1|INFO|<game>` (own connection) | `INFO|servers|<json>` then `INFO|mod|<json>` |
| any refusal | `E|<reason>` then close (wrong code, version mismatch, room full, unknown game) |

After the handshake: the host hears `J|id|name`, `L|id` and every guest message as `G|id|<msg>` (the relay sets the id,
so a guest can't fake another). A host message goes to every guest unchanged. Host leaves: guests get `X`. `D|<text>`
is printed by the relay with `--log` and not forwarded (useful for lab lines from Flash Player windows). Limits: 600
messages/s per connection (throttled), 256 KB per message, 300 s idle.

Clean every name (drop `| ; , \r \n \t \0`) and code (uppercase, `0`→`O`, `1`→`I`, alphabet
`ABCDEFGHJKLMNPQRSTUVWXYZ23456789`, 5 characters). Never use a relay letter (`W J L G X E D ROOM LIST INFO`) for your
own message type: one mod lost every guest by sending `E|`.

Templates: AS3 `templates/as3/RelayClient.as`, AS2 `templates/as2/relay.as`. In every socket handler first check
`this == N.sock`, so a stale socket's late event is ignored. Handle each incoming message in its own try/catch (AS3):
Flash Player hides script errors, and one throwing message froze a mod's whole stream.

## The launcher's lobby bridge (second transport)
The Multiplayer Everything launcher can run the room itself: central server or
direct IP, passwords, version check, ready-up, a "loaded" barrier, chat, kick, reconnect. It starts each player's
game with FlashVars `lobby=1`, `room`, `role` (`host`/`client`), `slot` (0 = host), `bridgePort`, `sessionToken`
(32 hex), `seed`, plus the game action's own (`name`). The game then opens one socket to `127.0.0.1:bridgePort`
and shows no HOST/JOIN panel. Each message is one JSON object, NUL after it; the bridge answers Flash's policy request
on the same port.

| Game to launcher | Launcher to game |
|---|---|
| `{"t":"hello","token":...}` first (a wrong token closes) | `welcome` (`slot`, `role`, `room`, `seed`, `name`, `players`) |
| `{"t":"loaded"}`: ready to play | `go`: every game said loaded |
| `{"t":"send","to":-1\|slot,"d":...}` | `msg` (`from`, `d`) |
| `chat`, `log` (a line in the launcher's log) | `drop` / `back` (slot kept 30 s), `leave`, `end` (host's game closed), `closed` |

The cheap way in: keep the relay messages and make the bridge a second transport. `templates/as3/LobbyBridge.as`
(with `NetJson.as`) has RelayClient's callbacks and turns bridge events into relay text: the host's `welcome` is
`onRoom`, `go` is `J|slot|name` for each other player, `msg` is `G|slot|d`, `leave` is `L|slot`; a client's `welcome`
is `W|slot` and the host's `msg` arrives as the bare message. `drop`/`back` come out as `DR|slot`/`BK|slot`: keep
the player's character idle, and on back resend what a late joiner gets. Send each message as a JSON string in `d`.
Send `loaded` only once the game can take the host's first message (past preloader and intro), since `go` is what
tells the host the others are there. Lab: `templates/lab/fake_bridge.py` plays the launchers (all games on one lab
port, told apart by token; drop/back on a `log` line). [Bad Ice-Cream]

## Version
`GAME` is the relay id (`bic`, `sh2`, `tw`...); `VERSION` is the protocol (`bic-1`, `sh2net-7`). The relay refuses a
joiner whose version differs from the host's. The launcher's lobby has its own version string in `launcher.json`
(`online.lobby.version`) and appends the SWF's hash, so only identical builds meet. Change it whenever any message changes. The mods-info version (latest,
min) is the release version, a separate string. An offline test checks they agree with the docs.

## Choosing the sync model
| Game type | Model | Used by |
|---|---|---|
| Turn-based (artillery, archers) | Host runs the match. On your turn you aim and charge locally (no round-trip overshoot) and send the result: `AIM|...` at ~10/s for others to watch, `FIRE|kind|angle|power`. The host checks turn owner and ammo and fires through the game's own code. Others draw the host's state (`SN` per frame, changed objects only, full every ~40 frames) or replay events (`FIRE`, then `LAND` with the true position). | Territory War, Raft Wars, Bow Man |
| Arcade, tile or physics, small | Host-authoritative snapshot each frame (on change, at least every N frames) plus events (sounds, popups, effects). Guests run no game logic: they apply the snapshot and draw. | Bad Ice-Cream, Air Battle |
| Action platformer or shooter | Each player moves their own character locally (no input lag) and sends its pose and shots. The host owns enemies, damage, pickups and triggers; damage to a player is sent back to its owner. Remote characters are real game characters fed by input and steered to the reported pose, or tinted puppets. | Intrusion 1 and 2, Ultimate Crab Battle, Stealth Hunter 2 (later) |
| Already local multiplayer and nearly deterministic | Input lockstep driven by the host: `F|frame|inputs` every frame, a 2-frame jitter buffer, seeded RNG replacing `Math.random`/`random()`, a full snapshot plus RNG state every ~35 frames, hard wait only when a guest is >15 frames behind. | Gun Mayhem 2 |

Lockstep without a host failed or was rejected everywhere else, inside a Flash mod: Ruffle and Flash Player differ in `hitTest`, timers and
trig, `Math.random` and timeline scripts run everywhere, Box2D drifts within a second, and wall-clock timers differ.
It works in **Ruffle Together** (`references/ruffle-together.md`), because there every player runs the same emulator
build and the emulator makes the clock, randomness, timers and sound endings the same on every PC: no seeding, no
snapshots, and nothing to sync in the SWF.

## Messages
Text, `|` between fields, `;` between entities, `,` inside one. Types are 1-3 capital letters. Typical set:

| Direction | Message | Purpose |
|---|---|---|
| host → all | `LV|level|...|run` | start a level; `run` increases each start so stale messages are dropped |
| host → all | `S|run|frame|...` or `SN|...` | snapshot (only what moved, plus a keyframe every ~1 s) |
| host → all | `RO|id:slot:name;...` / `PL|...` | roster at ~1 Hz |
| host → all | `PU|...`, `END|...`, `MN` | popup or result, level end, back to menu |
| host → one | `@<id>|...` prefix, or a `target` field | catch-up for a late joiner |
| guest → host | `K|bits` | input on change and every ~12 frames (`1 L, 2 R, 4 U, 8 D, 16 fire`) |
| guest → host | `P|state` / `ME|x|y|vx|vy` | own pose, for the local-movement model |
| guest → host | `RD|level|entityCount` | "I built the level", with a count the host compares |
| both | `PI|t` / `PO|t` | ping every ~50 frames, for the corner tag |
| both | `LB|...` | lab commands and results |

Sizes seen: Air Battle 40 snapshots/s, ~250 B each, 10-12 KB/s per guest. Stealth Hunter 2 15 Hz. All fine for the relay.

Numbers: AS2 `String(n)` keeps 15 digits and Ruffle truncates `_x` to twips, so send positions rounded the way the game
will read them back (`round(v*20)/20`) or send the remainder too; otherwise snapshots themselves cause drift.

## Identity: which object is which
Both sides build the level from the same data, so objects are created in the same order. Use the creation index as the
net id (per class if needed), registered in the game's own add-object function. AS2 instance names (`instance123`)
differ between PCs; depth paths don't. The guest sends its entity count in `RD`, and the host flags a mismatch.

## Smoothness on the guest
- One snapshot per frame and no interpolation is fine for tile games at 25-30 fps (Bad Ice-Cream).
- A 2-snapshot jitter buffer that catches up when more than 4 pile up (Air Battle).
- Smoothing (close 35% of the gap per frame) plus extrapolation for up to one interval (Stealth Hunter 2).
- Play back 4 host frames behind with interpolation (Raft Wars).
- Physics games: the guest may still step Box2D for debris, then put every synced body back at the host pose with zero
  velocity. Never sync derived bodies (a propeller that follows its hull).
- Remote poses: snap beyond a distance (150 px, 2.5 tiles), ease below it.

## Join, leave, late join
- **Guest leaves** (`L|id`): free its slot; its character stands still, goes down, is skipped in turns, or a teammate or
  the CPU takes it. If it was aiming, the host takes the shot.
- **Host leaves** (`X` or close): reset the session and show "The host left (reason)" on every guest, then back to the
  menu or level select. Keep the `E|reason` that arrives before a close as the message.
- **Silence timeout:** 10 s without traffic either way ends the session.
- **Late join:** resend `LV` to the joiner (or restart a 1-player level as 2-player), spawn its character at once and
  tell everyone, send a catch-up message (deaths, coins, checkpoint), and make the next snapshot a full one.
- **Reset on disconnect:** every session field back to its start value; an offline test checks it.

## What the host owns
Physics, AI, damage, pickups, triggers, level flow, score and money, randomness, timers, sounds (send sound names in the
snapshot, or hook the sound manager), and saves. Guests don't write saves; co-op progress uses its own SharedObject so
single-player saves are never touched.
