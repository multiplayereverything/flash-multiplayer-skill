# Contributing

Humans and agents follow the same flow. Agents: [AGENTS.md](AGENTS.md) has the full rules; this page is the short version.

1. **Fork** the repo and branch `game/<game-slug>` (or `directory/<what>` for a directory-only fix, `tool/<what>` for a tool).
2. **Directory:** edit `data/games.json` (fields and allowed values in [tools/directory.py](tools/directory.py)), then run
   `python tools/directory.py render` and commit the regenerated `DIRECTORY.md`. Every entry needs a QA level and a source.
3. **Write-up:** `games/<game-slug>.md`. Path, key map, how the players were added, build route, lab runs, lessons. No game code.
4. **Traps:** a new trap goes into `references/traps.md` under its section, with the game's name in brackets.
5. **Key maps:** a new key map also goes to Ruffle Together, so it is built in there. Say so in the PR.
6. **Check** before you open the PR:
   - `python -I tools/test_all.py` prints `ALL OK`
   - `python tools/check_public.py` prints `0 problem(s)`
7. **Open a draft PR** with the template filled in. One game per PR. Maintainers take drafts out of draft when they are ready.

## QA levels

Pick the highest level you actually reached, and say how in the PR.

| Level | Means |
|---|---|
| `none` | Not tested beyond reading the SWF. Fine to submit. |
| `lab-2p` | [flash-lab](skills/flash-lab/SKILL.md) steps 0-9 passed with 2 players. |
| `lab-3p+` | The same steps passed with 3 and 4 players. |
| `played-online` | Real people played on separate PCs over the relay. Two windows on one PC never count. |

Please don't claim a level you didn't reach. `none` is a good answer.

## Please don't

- Add game files or assets: SWFs, art, audio, ROMs, save files, or download links to them. The release is a separate, linked thing.
- Add decompiled or disassembled game code, or anything that copies it.
- Paste personal info: names, emails, usernames in local paths, tokens, keys, private invite links or chat logs.
- Change `DIRECTORY.md` by hand. Edit `data/games.json` and render it.

## Starting a game nobody covers

Open a **"I'm working on a game"** issue first so others can find you and avoid doing the same work. Spotted a Flash game
that isn't in the directory yet? The **"New Flash game or mod"** issue form is enough; someone's agent can turn it into an entry.

Chat with other players and modders on [Discord](https://discord.gg/2SJggtHqPR).
