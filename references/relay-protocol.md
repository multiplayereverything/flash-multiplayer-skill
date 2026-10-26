# Relay protocol

The full protocol of the relay in `relay/`. Flash mods use star mode; tunnel mode is for games with their own
TCP protocol and is here for completeness. Run your own relay (`relay/README.md`).

One TCP port for every game. The first line a client sends picks the game, the role and the room. It ends with `\n`
or `\0`, and the relay ends its replies the same way (Flash `XMLSocket.send` appends `\0` by itself; other clients may write `\n`).

## Handshake (version 1)
```
RELAY|1|HOST|<game>|<version>|<public 0/1>|<room name>   -> ROOM|<code>|<max players>
                                                            star: then W|0, then the star protocol
                                                            tunnel: then OPEN|<token> per friend; send PING to keep alive (-> PONG)
RELAY|1|JOIN|<game>|<version>|<code>|<player name>       -> star: W|<id>     tunnel: OK, then raw bytes to/from the host
RELAY|1|DATA|<token>                                     tunnel host only: the data connection for one friend
RELAY|1|LIST|<game>                                      -> LIST|<code>,<players>,<max>,<name>;...   (public rooms)
RELAY|1|INFO|<game>                                      -> INFO|servers|<json> then INFO|mod|<json>  (the game's mods-info)
any refusal                                              -> E|<reason>, then the connection closes
```
- Names and versions must not contain `| ; ,` or line breaks.
- Codes: 5 characters from `ABCDEFGHJKLMNPQRSTUVWXYZ23456789`; joins ignore case and read `0`/`1` as `O`/`I`.
- A joiner's version must equal the host's (`E|Version mismatch: ...`).
- The relay answers Flash's `<policy-file-request/>` on the same port, so Flash sockets work.
- Old clients that send `H|name` / `J|name` with no handshake share one default star room (the original relay behaviour).
- INFO lines are one-line JSON, so split on the first two `|` only (a notice may contain `|`).

## Star mode (text relay)
- Host gets `W|0`; each guest gets `W|<id>` (1, 2, ...). The host is told `J|<id>|<name>` and `L|<id>` when a guest leaves.
- Guest message `msg` reaches the host as `G|<id>|msg` (the relay sets the id; a guest can't fake another's).
- A host message goes to every guest unchanged.
- Host leaves: guests get `X` and are disconnected. `E|<reason>` arrives just before a refusal closes the socket, so keep
  it as the "disconnected" reason.
- `D|<text>` lines are debug output: the relay prints them (with `--log`) and doesn't forward them.

## Tunnel mode (byte pipes)
- Host keeps the control connection open and sends `PING` now and then (the relay drops a host it hasn't heard from).
- For each friend the relay sends `OPEN|<token>`. Open a **new** connection, send `RELAY|1|DATA|<token>\n`, and treat that
  socket exactly like one your `TcpListener` accepted. The friend's socket, after `OK`, is a raw pipe to it.
- Host leaves: every friend's pipe closes. A friend leaving closes only its own pipe.

## Version 2 (tunnel only, optional)
```
RELAY|2|HOST|<game>|<version>|<public>|<max players>|<password hash or empty>|<handoff secret or empty>|<room name>
RELAY|2|JOIN|<game>|<version>|<code>|<password hash or empty>|<player name>
RELAY|2|RESUME|<game>|<version>|<code>|<handoff secret>|<player name>     a teammate re-hosts the same room
RELAY|2|LIST|<game>  -> LIST|<code>,<players>,<max>,<locked 0/1>,<name>;...
```
Hashes and secrets are opaque (send hex SHA-256). Host handoff needs the game's profile to allow it (`handoff` seconds).

### Version 2 in star rooms (Flash)
Star games take `RELAY|2|HOST` and `RELAY|2|JOIN` too: a password hash and a host-chosen room size, no `RESUME`.
```
RELAY|2|ROOMS|<game>  -> ROOMS|<code>,<players>,<max>,<locked>,<state>,<region>,<ping>,<version>,<name>;...
@META|state=lobby|ingame|region=<XX>|ping=<ms>     sent by a v2 star host: kept for ROOMS, not forwarded
RELAY|2|PROBE|<game>|<port>  -> PROBE|open|closed|other|<port>
```
- `PROBE` connects back to the caller's own public address (a direct-IP host checking its port forwarding); `open`
  only when a Flash policy file answers. Private and local callers get `PROBE|error|...`; 6 probes per IP a minute.
- A version `<version>#<hash>` is matched exactly on join (a launcher adds the SWF's hash, so only the same build
  joins); a games.json `versions` list sees only `<version>`.
- A v1 client can't join a password-locked room, and v1 `LIST` hides locked rooms; v2 `LIST` shows them flagged.

## Limits (per IP / connection)
32 connections and 4 rooms per IP, 20 wrong codes per IP per minute, 10 s to send the first line (512 bytes max),
star 600 messages/s (throttled, not dropped), 256 KB per message, tunnel 2 MB/s per direction, idle rooms close after
300 s without traffic. Logs mask IPs; nothing is stored.
