# Agent guide: Flash multiplayer hub

You're here because someone wants to play a Flash game online with friends. This hub has the method, the tools, a
directory of every Flash game done so far, and the skills in `skills/`. Follow the phases in order; each phase's skill
says what to read.

## Phases
| # | Phase | Skill | Done when |
|---|---|---|---|
| 1 | Triage: what the SWF is, is it done already, which path and sync model | `skills/flash-start` | the plan is in the mod's `MODLOG.md` and the user has seen it |
| 2 | Map the game's code | `skills/flash-map` | `CODE_MAP.md` names the one place each system runs through |
| 3 | The lab, before features | `skills/flash-lab` | a lab build hosts and joins itself, and `--solo` passes |
| 4 | Get code into the SWF | `skills/flash-inject` | lab and release builds come out of one source, original file untouched |
| 5 | Sync, one system at a time | `skills/flash-sync` | each system has an owner, a message and a lab check; 3+ players and a late join pass |
| 6 | Ship | `skills/flash-ship` | release build in flash-games, mods-info file merged, launcher entry |
| 7 | Share back | `skills/flash-share` | directory entry, write-up, new traps and tools in this hub |

The paths:
- **A. Local multiplayer to online:** the game already has 2+ players on one keyboard. The second player's input
  comes from the network. Usually the fastest.
- **B. Single player to multiplayer:** add co-op (or versus where it fits). The game's one player has to become many.
- **C. Fix or update an existing online mod:** find it in `DIRECTORY.md`, read its write-up and the mod's own notes.

## Rules
1. **Never edit the original SWF**, and never put decompiled game code in the mod's source, a release or this hub.
2. **The host's game is the world.** Others send input or requests; the host decides and tells everyone.
3. **Online is the default.** HOST gives a room code on the main relay (`195.60.166.57:25569`, star mode), JOIN takes
   one. Direct IP or LAN, if kept at all, is the second choice. Save only the server the player typed.
4. **Single player stays unchanged.** Prove it with the lab's `--solo` run.
5. **Proof comes from the lab:** self-driving builds, 0 AVM errors, screenshots looked at. Never drive the user's
   keyboard or mouse. Stop only processes you started. One lab port per mod, never a port real sessions use.
6. **One version string**, changed whenever a message changes.
7. **Ruffle desktop first**, Flash Player 32 second; write down when a mod is Ruffle only.
8. **Ask before** installing tools, pushing to mods-info, or using the user's accounts.
9. **Nothing private in public:** `python tools/check_public.py` before every push.
10. **Honest QA levels.** `played-online` only after two real players on two networks played it.

## Layout
| Path | What |
|---|---|
| `SKILL.md` | the umbrella skill (`flash-multiplayer`): route and rules on one page |
| `skills/` | the seven phase skills |
| `references/` | recon, build, network, hooking, UI, lab, traps, the mods compared, release |
| `games/` | one write-up per game in the directory |
| `data/games.json`, `DIRECTORY.md` | the directory (edit the JSON, then `python tools/directory.py render`) |
| `tools/` | FFDec helpers, SWF readers, the UseNetwork flag, window capture, the public-data check, the directory tool, `test_all.py` |
| `templates/` | relay clients, mods-info readers, build scripts, lab runners, offline checks |

## Before you finish
`python -I tools/test_all.py` prints `ALL OK`, `python tools/check_public.py` finds 0 problems, and the report table
(Feature | What it does | How | Tested) is in your last message.
