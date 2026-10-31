# Release

## 1. The key map
- A built-in map (`--coop-keys gun-mayhem-2`) needs nothing shipped.
- A new map is a `.keys` file next to the SWF, checked with `python -I tools/keys_check.py game.keys`. Send it to
  [ruffle-together](https://github.com/multiplayereverything/ruffle-together) (`desktop/src/coop/keys/`) so the next Ruffle
  Together release has it built in, and note which version first does.
- A game that sets its own map with `coop.keys` still needs a launch map with enough slots.

## 2. The game file
Ship the co-op build (`dist/<Game>_coop.swf`), or point players at the untouched game for a path A game. Every player
needs the **same bytes**: a rebuilt SWF is a new version for everyone. Put it where your players download it: a
release on your own repo, a page, or a launcher's catalog. If you keep several games in one repo, keep a catalog with
each file's size and SHA-256, commit the file and catalog together, and check after pushing that the downloaded file's
SHA-256 matches. Say in the README whose game it is and how rights holders can ask for removal.

## 3. The launch line
```
ruffle_desktop --coop-host-relay <relay> --coop-keys <map> --coop-players <N> [--coop-option NAME=VALUE] Game_coop.swf
ruffle_desktop --coop-join-relay <relay> --coop-code ABCDE --coop-keys <map> Game_coop.swf
```
Write down: the key map, the player counts (2-4), any host options the SWF reads (`coop.option`), and the minimum
Ruffle Together version (the first one with the map built in, or with the API calls the SWF uses).

## 4. mods-info and the launcher (optional)
A launcher (the Multiplayer Mods Launcher does this) keeps Ruffle Together up to date, starts the game with the right
line, and lists the host options as dropdowns. mods-info is small JSON files you host anywhere public (a GitHub repo
works): `servers.json` with the relay's address, and `mods/<id>.json` with the latest and minimum version, the
download link and a notice. Starter kit: `modsinfo/` (file format, a template mod file, `schema.json`,
`tools/validate.py`).

## 5. A relay (optional)
Players can use the public Ruffle Together relay (its address is in ruffle-coop's README). To run your own, use the
hub's `relay/` with a `ruffle-coop` star game (`relay/README.md`) and check it from another network:
`python tools/check_server.py --game ruffle-coop --server <host:port> --mode star`.

## 6. Before every public push
- No game files except the release SWF where you mean to publish it. No decompiled code, ever, anywhere.
- No tokens, keys, passwords, `.env` files, SSH or server login details.
- No personal paths (`C:\Users\<name>\...`), emails, or home-network and VPN addresses. A relay's public address is
  fine; your home IP is not.
- Run `python tools/check_public.py` in the repo (it scans what git would commit), or pass it the folders to scan.

## 7. Report
| Feature | What it does | How | Tested |
|---|---|---|---|

Use ✅ with lab evidence, ⚠️ with why not. Internet play between two networks stays ⚠️ until two real players tried it.
