# Your relay

Ruffle Together's room codes go through a relay: a small server that gives the host a room code and passes the
players' inputs between the host and their friends. Nobody playing needs port forwarding; only the relay needs one
open TCP port. Players can use the public Ruffle Together relay; run your own for tests or your own players.
Python 3.7+, standard library only, one process for every game.

| File | What |
|---|---|
| `init.py` | the server: one port, room codes, public room lists, safety limits |
| `relay-flash.py` | star mode, used by Ruffle Together: friends' messages reach the host as `G|<id>|<msg>`, the host's go to every friend |
| `relay-unity.py` | tunnel mode for games with their own TCP protocol (not needed here, kept because `init.py` loads it) |
| `relay-common.py` | shared parts: limits, rooms, the optional mods-info reader |
| `relay.py` | the old entry point, kept for older lab scripts: it just starts `init.py` |
| `games.example.json` | `ruffle-coop` (all you need), plus the ids older Flash mods used |
| `tests/test_relay.py` | 38 tests with fake clients (star, tunnel, version 2, limits, mods-info): `python tests/test_relay.py` |

The full protocol (handshakes, star and tunnel, version 2 passwords, room sizes, `ROOMS`, `PROBE`) is in
`../references/relay-protocol.md`.

## 1. Try it on your PC
```bash
cp games.example.json games.json          # then keep only your games, or add yours
python init.py --port 7790 --log
```
Host with `--coop-host-relay 127.0.0.1:7790` and join with `--coop-join-relay 127.0.0.1:7790 --coop-code <code>`.
ruffle-coop's coop-lab starts its own copy on its own port.

## 2. Add Ruffle Together
`games.json` next to `init.py` needs one entry, `ruffle-coop`, for every Ruffle Together game:
```json
{
  "ruffle-coop": { "name": "Ruffle Together", "mode": "star", "max_players": 4, "framing": "nul", "versions": [], "idle": 300 }
}
```
| Key | Meaning |
|---|---|
| id (the key) | `ruffle-coop`: the id Ruffle Together hosts and joins with |
| `mode` | `star` |
| `max_players` | including the host; Ruffle Together plays up to 4 |
| `framing` | `nul` (messages end with a NUL byte) |
| `versions` | versions a host may use; `[]` = any. Ruffle Together checks versions itself when friends join |
| `idle` | seconds without traffic before a room closes |

Restart the relay. An unknown id is refused with `E|Unknown game '<id>' on this server`. `games.example.json` also
lists the ids older Flash mods used; they're only needed for those builds.

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

## 4. Point Ruffle Together at it
`--coop-host-relay your.host:25600` and `--coop-join-relay your.host:25600 --coop-code ABCDE`. A launcher can take the
address from mods-info.

## 5. Optional: mods-info
If you might move the relay or want to tell players about updates without a new launcher, publish the starter kit in
`../modsinfo/` (format, template, validator) as its own public repo, with the relay's address in `servers.json`.
Start the relay with `--mods-info https://raw.githubusercontent.com/<you>/<repo>/main/` so it learns new games from
those files too.

## Limits and privacy
Per IP: 32 connections, 4 rooms, 20 wrong codes a minute. 10 s to send the first line, 600 star messages a second per
connection (throttled), 256 KB per message, idle rooms closed. Logs mask IP addresses and nothing is stored. Change
limits with the flags in `python init.py --help`.

Don't put your server's login details, keys or your home IP in a public repo; only the address players connect to.
