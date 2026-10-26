# Your relay

Every online mod made with this hub connects to a relay: a small server that gives the host a room code and passes
messages between the host and their friends. Nobody playing needs port forwarding; only the relay needs one open TCP
port. **Run your own.** Python 3.7+, standard library only, one process for every game you make.

| File | What |
|---|---|
| `init.py` | the server: one port, room codes, public room lists, safety limits |
| `relay-flash.py` | star mode, used by Flash mods: guest messages reach the host as `G|<id>|<msg>`, host messages go to every guest |
| `relay-unity.py` | tunnel mode for games with their own TCP protocol (not needed for Flash, kept because `init.py` loads it) |
| `relay-common.py` | shared parts: limits, rooms, the optional mods-info reader |
| `relay.py` | the old entry point, kept for older lab scripts: it just starts `init.py` |
| `games.example.json` | profiles for the ten mods in this hub's directory, as examples |
| `tests/test_relay.py` | 38 tests with fake clients (star, tunnel, version 2, limits, mods-info): `python tests/test_relay.py` |

The full protocol (handshakes, star and tunnel, version 2 passwords, room sizes, `ROOMS`, `PROBE`) is in
`../references/relay-protocol.md`.

## 1. Try it on your PC
```bash
cp games.example.json games.json          # then keep only your games, or add yours
python init.py --port 7790 --log
```
Point a mod's SERVER field (or its `relay=` FlashVar) at `127.0.0.1:7790` and host. Labs start their own copy on their
own port with `--bind 127.0.0.1 --games tools/lab_games.json --no-mods-info` (see `references/lab.md`).

## 2. Add your game
`games.json` next to `init.py`, one entry per game:
```json
{
  "mygame": { "name": "My Game Online", "mode": "star", "max_players": 4, "framing": "nul", "versions": [], "idle": 300 }
}
```
| Key | Meaning |
|---|---|
| id (the key) | the relay id your mod sends in `RELAY|1|HOST|<id>|...`: lowercase letters, digits, `-` |
| `mode` | `star` for Flash |
| `max_players` | including the host, 2-16 |
| `framing` | `nul` for Flash (XMLSocket and the AS3 Socket client both end messages with NUL) |
| `versions` | protocol versions a host may use; `[]` = any. A joiner must always match its host |
| `idle` | seconds without traffic before a room closes |

Restart the relay. An unknown id is refused with `E|Unknown game '<id>' on this server`.

## 3. Put it online
The relay needs one public TCP port. Any of these work:
- **A small VPS** (any provider, the cheapest plan is plenty): copy this folder, open the port in the firewall, run it
  as a service (below).
- **A Python game-server host** (Pterodactyl-style panels): upload the folder, start `init.py`; it reads the port from
  `SERVER_PORT` and shows your address from `SERVER_IP`.
- **Your own PC**, if you can forward one port on your router to it, or through a TCP tunnel service that gives you a
  public `host:port`.

Example service on Linux (`/etc/systemd/system/flash-relay.service`):
```ini
[Unit]
Description=Flash mod relay
After=network-online.target

[Service]
WorkingDirectory=/opt/flash-relay
ExecStart=/usr/bin/python3 init.py --port 25600
Restart=always
User=nobody

[Install]
WantedBy=multi-user.target
```
`sudo systemctl enable --now flash-relay`, then open the port (`sudo ufw allow 25600/tcp`). Pick any free port; the
relay refuses one that's already in use.

Check it from another network with the hub's checker (known game, a room with a friend, messages both ways):
```bash
python tools/check_server.py --game mygame --server your.host:25600 --mode star
```
`FAIL known game` with `Unknown game` means the relay runs but `games.json` lacks the id; no answer means the port
isn't reachable (firewall, wrong port, or the service isn't running).

## 4. Build your relay into your mods
In each mod, set the built-in relay to your address (`GLOBAL_RELAY = "your.host:25600"` in AS2, the `builtIn` address
passed to `NetModInfo.pick` in AS3) and the default port to yours. Players can still type another server in the
panel's SERVER field.

## 5. Optional: mods-info
If you might move the relay or want to tell players about updates without a rebuild, publish the starter kit in
`../modsinfo/` (format, template, validator) as its own public repo. Then:
- start the relay with `--mods-info https://raw.githubusercontent.com/<you>/<repo>/main/` so it learns new games from
  those files and answers `RELAY|1|INFO|<id>` for Flash Player, which can't download them itself;
- set the mod's mods-info bases to the same URL (`MODINFO_BASES` in AS2, `BASES` in `NetModInfo.as`).

Without mods-info, leave both empty: the mod uses its built-in address and the relay uses `games.json`.

## Limits and privacy
Per IP: 32 connections, 4 rooms, 20 wrong codes a minute. 10 s to send the first line, 600 star messages a second per
connection (throttled), 256 KB per message, idle rooms closed. Logs mask IP addresses and nothing is stored. Change
limits with the flags in `python init.py --help`.

Don't put your server's login details, keys or your home IP in a public repo; only the address players connect to.
