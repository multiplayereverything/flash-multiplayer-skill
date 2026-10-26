# Release

## 1. Your relay
Online play needs a relay that your players can reach. This hub ships one in `relay/` (Python, standard library only);
`relay/README.md` covers running it on your PC, a VPS or a Python game-server host, adding your game to its
`games.json`, and checking it from another network. One relay serves every game you make.

1. Pick a short lowercase relay id for the game (letters, digits, `-`).
2. Add it to your relay's `games.json` (`"mode": "star"`, `"max_players"`, `"framing": "nul"`) and restart the relay.
3. Build your relay's public address into the mod as the built-in server (`GLOBAL_RELAY`, default port).
4. Check from another network: `python tools/check_server.py --game <id> --server <host:port> --mode star`.

Players can always type another server in the panel's SERVER field (a friend's relay, a local test relay).

## 2. Optional: mods-info
mods-info is two small JSON files you host anywhere public (a GitHub repo works): `servers.json` with your relay's
current address and status, and `mods/<id>.json` with the latest and minimum version, the download link, a notice, and a
`relay` block (`mode`, `max_players`). With it you can move the relay or announce an update without rebuilding the mod.

- The mod downloads both in the background (about 5 s timeout, never blocking the game), keeps the last good copy in its
  SharedObject, and picks the server: player-typed > mods-info > cached > built-in.
- Flash Player can't make HTTP requests from a local SWF, so the mod then asks the relay it reaches with
  `RELAY|1|INFO|<id>`; start your relay with `--mods-info <base url>` so it can answer and learns new games from the
  same files.
- Below `min_version` the mod refuses your server with the update line; a typed server still works.
- Starter kit: `modsinfo/` (file format, a template mod file, `schema.json`, `tools/validate.py`). Copy it into its own
  public repo.
- Templates: `templates/as3/NetModInfo.as` (`BASES`), `templates/as2/modinfo.as` (`N.MODINFO_BASES`; set `N.GAME_ID`
  first). Leave the bases empty to skip it; the mod then uses its built-in address.

## 3. The game file
Ship only the release build (`*_online.swf`), never lab or test builds. Put it where your players download it: a
release on your own repo, a page, or a launcher's catalog. If you keep several games in one repo, keep a catalog with
each file's size and SHA-256, commit the file and catalog together, and check after pushing that the downloaded file's
SHA-256 matches. Say in the README whose game it is and how rights holders can ask for removal.

## 4. A launcher (optional)
A launcher that runs Ruffle with `--tcp-connections allow` and FlashVars `online=1`, `name=<player>` and
`join=<CODE>` (from a room list it reads with `RELAY|1|LIST|<id>`) gives players one-click hosting and joining. Put
"Play online" first, and show "not on the server yet" when your relay answers `E|Unknown game`.

## 5. Before every public push
- No game files except the release SWF where you mean to publish it. No decompiled code, ever, anywhere.
- No tokens, keys, passwords, `.env` files, SSH or server login details.
- No personal paths (`C:\Users\<name>\...`), emails, or home-network and VPN addresses. Your relay's public address is
  fine; your home IP is not.
- Run `python tools/check_public.py` in the repo (it scans what git would commit), or pass it the folders to scan.

## 6. Report
| Feature | What it does | How | Tested |
|---|---|---|---|
Use ✅ with lab evidence, ⚠️ with why not. Internet play between two networks stays ⚠️ until two real players tried it.
