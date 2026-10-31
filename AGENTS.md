# Agent guide: Flash multiplayer hub

You're here because someone wants to play a Flash game online with friends. Every game here goes online through
[Ruffle Together](https://github.com/multiplayereverything/ruffle-together): every PC runs the same game in lockstep and
only key presses travel, so the SWF never gets network code. This hub has the method, the tools, a directory of every
Flash game done so far, and the skills in `.claude/skills/`. Follow the phases in order; each phase's skill says what to read.

## Phases
| # | Phase | Skill | Done when |
|---|---|---|---|
| 1 | Triage: what the SWF is, is it done already, which path | `.claude/skills/flash-start` | the plan is in the mod's `MODLOG.md` and the user has seen it |
| 2 | Map the game's code (path B) | `.claude/skills/flash-map` | `CODE_MAP.md` names the one place input, "the player", camera and menus run through |
| 3 | Tests, before features | `.claude/skills/flash-lab` | an input script gets into play, its replay matches twice, and the screenshots were looked at |
| 4 | Get code into the SWF (path B) | `.claude/skills/flash-inject` | the co-op build comes out of one source, original file untouched |
| 5 | Add the players | `.claude/skills/flash-coop` | each player has their own input and hero; 1 player is the original; 2-4 players pass the coop-lab |
| 6 | Ship | `.claude/skills/flash-ship` | the co-op SWF, key map and launch line are published |
| 7 | Share back | `.claude/skills/flash-share` | directory entry, write-up, new traps and tools in this hub |

The paths:
- **A. Local multiplayer to online:** the game already has 2+ players on one keyboard. A key map is usually all it
  needs (phases 1, 3, 6, 7).
- **B. Single player to multiplayer:** add local co-op to the SWF: more heroes on the same screen, each read from its
  own player slot. No network code.
- **C. Fix or update an existing one:** find it in `DIRECTORY.md`, read its write-up and the mod's own notes.

## Rules
1. **Never edit the original SWF**, and never put decompiled game code in the mod's source, a release or this hub.
2. **Gameplay uses only shared answers.** `coop.localSlot`, `coop.isHost` and `coop.ping` are for what one PC shows.
3. **1 player is the original.** With one player, or outside Ruffle Together, the game takes its own path.
4. **Proof comes from tests:** replays that match twice, screenshots looked at, the coop-lab with 2-4 players, two
   real windows. Never drive the user's keyboard or mouse. Stop only processes you started. One lab port per mod.
5. **Same bytes for everyone:** one co-op SWF per release, and the minimum Ruffle Together version written down.
6. **Ask before** installing tools, renting or changing a server, pushing anywhere public, or using the user's accounts.
7. **Nothing private in public:** `python tools/check_public.py` before every push.
8. **Honest QA levels.** `played-online` only after two real players on two networks played it.

## Layout
| Path | What |
|---|---|
| `.claude/skills/flash-multiplayer/SKILL.md` | the umbrella skill (`flash-multiplayer`): route and rules on one page |
| `.claude/skills/` | the seven phase skills |
| `playbook/` | the technique pages (index in `playbook/README.md`): Ruffle Together, recon, build, traps, release, the relay protocol |
| `games/` | one write-up per game in the directory |
| `data/games.json`, `DIRECTORY.md` | the directory (edit the JSON, then `python tools/directory.py render`) |
| `tools/` | the key-map checker, FFDec helpers, SWF readers, window capture, the public-data check, the directory tool, `test_all.py` |
| `templates/` | Ruffle Together examples (key map, input script, replay check) and build scripts |
| `relay/` | the relay server, if you run your own for Ruffle Together, with its tests |
| `modsinfo/` | optional mods-info starter kit, published as its own repo |

## Contributing
Contributors follow [CONTRIBUTING.md](CONTRIBUTING.md): a branch, one game per draft PR, and the template in
`.github/PULL_REQUEST_TEMPLATE.md`. CI runs `tools/test_all.py`, `tools/check_public.py` and the directory check on every PR.

## Before you finish
`python -I tools/test_all.py` prints `ALL OK`, `python tools/check_public.py` finds 0 problems, and the report table
(Feature | What it does | How | Tested) is in your last message.
