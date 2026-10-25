# Release

## 1. The relay profile (mods-info)
The live relay learns which games it accepts from mods-info (github.com/multiplayereverything/mods-info): one file per
mod, `mods/<id>.json`, with a `relay` block (`"mode": "star"`, `"max_players": N`). It picks up a merged file within
about 10 minutes. Until then the relay answers `E|Unknown game '<id>'` and you test with a local relay.

1. Pick a short lowercase id not already in mods-info's `index.json`.
2. Fill `mods/<id>.json`: id, name, latest and minimum version, download URL, relay block, notice.
3. Run the repo's `python tools/validate.py` (it rewrites `index.json` and the README table), and open a pull request.
   Ask the maintainer before pushing anything there.
4. After the merge, check the live relay accepts the id (a `RELAY|1|LIST|<id>` answers `LIST|...`, not `E|`).

The mod downloads `servers.json` and `mods/<id>.json` in the background (about 5 s timeout, never blocking the game),
keeps the last good copy in its SharedObject, and picks the server: player-typed > mods-info > cached > built-in
`195.60.166.57:25569`. Flash Player can't make HTTP requests from a local SWF, so the mod then asks the relay it
reaches with `RELAY|1|INFO|<id>`. Below `min_version`, the main server is refused with the update line; a player-typed
server still works. Templates: `templates/as3/NetModInfo.as`, `templates/as2/modinfo.as` (set `N.GAME_ID` first).

## 2. The game file
Release builds (`*_online.swf`, never lab or test builds) go to the flash-games repo the launcher downloads from. Its
README explains the layout: `games/<launcher id>/<file>`, a one-line note per file in `tools/file-notes.json`, then
`tools/update-catalog.ps1` rewrites `catalog.json` (size, SHA-256, date). Commit the file and the catalog together.
Check after pushing that the raw download's SHA-256 matches the catalog.

## 3. The launcher
The Multiplayer Everything Flash launcher lists each game with a "Play online" action first (Ruffle with
`--tcp-connections allow` and FlashVars `online=1`, `name=<player>`; `join=<CODE>` from its room list), then local or
offline play. It shows "Not on the server yet" when the relay doesn't know the id.

## 4. Before every public push
- No game files except the release SWF in the flash-games repo. No decompiled code, ever, anywhere.
- No tokens, keys, passwords, `.env` files, SSH or server logins.
- No personal paths (`C:\Users\<name>\...`), emails, or home-network and VPN addresses. The public relay address is fine.
- Scan the staged diff, for example:
  ```bash
  git diff --cached | grep -nIiE "users[\\/]|token|passw|secret|api.?key|ghp_|BEGIN .*PRIVATE|@gmail|192\.168\.|10\.[0-9]+\.[0-9]+\.[0-9]+"
  ```

## 5. Report
| Feature | What it does | How | Tested |
|---|---|---|---|
Use ✅ with lab evidence, ⚠️ with why not. Internet play between two networks stays ⚠️ until two real players tried it.
