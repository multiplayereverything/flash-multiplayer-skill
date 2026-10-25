# Flash Multiplayer

**Old Flash games, played online with your friends. Your agent builds the mod.**

Point your coding agent at this repo and name a Flash game. It reads the SWF, maps the game's code, builds an online
mod without touching the original file, tests it with self-playing copies of the game, and ships it. Friends join with
a 5-letter room code through the [Multiplayer Everything](https://discord.com/invite/P2MSSUf5GX) relay: nobody opens
ports, nobody types an IP.

[Quick start](#quick-start) · [How it works](#how-it-works) · [Games so far](#games-so-far) · [Tools](#tools) ·
[Share back](#share-back) · [FAQ](#faq)

## Quick start
Tell your agent (Claude Code, Codex, Gemini CLI, Cursor, ...), in the folder with the game's `.swf`:
```
Read https://github.com/multiplayereverything/flash-multiplayer-skill and follow AGENTS.md.
I want to play <game>.swf online with my friends.
```
To have the skills always on in Claude Code:
```bash
git clone https://github.com/multiplayereverything/flash-multiplayer-skill ~/flash-multiplayer
```
Then link the folder as `~/.claude/skills/flash-multiplayer` and each `skills/<name>` folder as
`~/.claude/skills/<name>` (or copy them). You need Java 21, [FFDec](https://github.com/jindrapetrik/jpexs-decompiler)
26.x, Python 3.10+ and [Ruffle](https://ruffle.rs) desktop. The agent asks before installing anything.

## How it works
Every Flash game here took one of three paths:

| | A. Local multiplayer to online | B. Single player to multiplayer | C. Fix an existing online mod |
|---|---|---|---|
| When | The game has 2+ players on one keyboard | One player only | It's in the [directory](DIRECTORY.md) already |
| How | The second player's keys come from the network; the host's game runs the match | The game's one player becomes several: remote characters, enemies that target anyone, a team that wins and loses together | Read its write-up and notes, fix in its lab, release |
| Examples | Bad Ice-Cream, Gun Mayhem 2, Territory War, Bow Man | Stealth Hunter 2, Air Battle, Ultimate Crab Battle, Raft Wars, Intrusion 1 and 2 | any |

Then the sync model follows from the kind of game:

| The game is... | Sync | Proven on |
|---|---|---|
| Turn-based (artillery, archers) | the host runs the match; the player whose turn it is aims locally and sends the shot | Territory War, Raft Wars, Bow Man |
| Arcade, tile or physics | the host sends a snapshot every frame; the other games only draw it | Bad Ice-Cream, Air Battle |
| Action platformer or shooter | everyone moves their own character; the host owns enemies, damage and pickups | Intrusion 1 and 2, Ultimate Crab Battle, Stealth Hunter 2 |
| Local multiplayer that's nearly deterministic | input lockstep from the host, seeded randomness, a repair snapshot every second | Gun Mayhem 2 |

And the build route from the file:

| The SWF is... | Code goes in by |
|---|---|
| AS3 (SWF 9+) | FFDec `importScript` with stub classes for the mod's new classes, patched game classes checked by a namespace guard |
| AS2, plain | new DoAction tags compiled next to the game's, every original tag untouched |
| AS2, obfuscated | compiled in a scratch copy, then the tags spliced into the untouched file |
| AS2 lockstep | p-code patches that replace every random call with a seeded one |

The phases, rules and skills are in [AGENTS.md](AGENTS.md).

## Games so far
| Game | Path | Players | Status |
|---|---|---|---|
| [Bad Ice-Cream](games/bad-ice-cream.md) | A | 2 | released |
| [Gun Mayhem 2](games/gun-mayhem-2.md) | A | 2-4 | released |
| [Territory War](games/territory-war.md) | A | 2-4 | released |
| [Bow Man](games/bow-man.md) | A | 2 | released (Ruffle) |
| [Stealth Hunter 2](games/stealth-hunter-2.md) | B | 2-4 | released (Ruffle) |
| [Air Battle](games/air-battle.md) | B | 2-4 | released |
| [Ultimate Crab Battle](games/ultimate-crab-battle.md) | B | 2-4 | released (Ruffle) |
| [Raft Wars](games/raft-wars.md) | B | 2-4 | released |
| [Intrusion](games/intrusion.md) | B | 2-4 | in progress |
| [Intrusion 2](games/intrusion-2.md) | B | 2-4 | in progress |

The [directory](DIRECTORY.md) has the details: relay id, engine, sync model and how each one was proven. The finished
builds are in [flash-games](https://github.com/Multiplayer-Everything-Team/flash-games), which the Multiplayer
Everything Flash launcher downloads from.

## Tools
Game-agnostic, in [`tools/`](tools). `python -I tools/test_all.py` checks them all (each check has a twin that must
fail) and prints `ALL OK`.

| Tool | What it does |
|---|---|
| `swfheader.py`, `swfinfo.py`, `swfmap.py` | SWF version, AS2 or AS3, fps, frames; frame labels; the display tree of obfuscated AS2 games |
| `ffdec/AddClasses.java`, `CheckNamespaces.java`, `ListClasses.java` | AS3: stub classes for `importScript`, the protected-namespace guard, class listing |
| `ffdec/InsertAction.java` | AS2: compile files into new DoAction tags on a frame |
| `set_use_network.py` | the flag Flash Player needs to open sockets from a local SWF |
| `case_scan.py` | SWF 6: names that collide when case is ignored |
| `wincap.py` | screenshot a test window by process id, never focusing it |
| `check_public.py` | refuses tokens, keys, passwords, personal paths, emails, home and VPN IPs, game files |
| `directory.py` | validates the directory and renders `DIRECTORY.md` |

[`templates/`](templates) has the relay clients and mods-info readers (AS3 and AS2), build scripts, the lab runners and
offline checks, all taken from the mods above.

## Share back
Every mod session ends by sending what it learned here: a directory entry with an honest QA level, a write-up, new
traps, a better tool. The next game starts where the last one stopped. The `flash-share` skill walks through it.
Pull requests welcome.

## FAQ
<details><summary>Do my friends need anything?</summary>
The mod's SWF and Ruffle desktop (or the Multiplayer Everything launcher, which sets both up). No accounts, no port
forwarding.
</details>

<details><summary>Flash Player or Ruffle?</summary>
Ruffle desktop first. Flash Player 32 works for some mods, but it can't load web files from a local SWF and won't open
sockets from SWF 6 games, so several mods are Ruffle only. Each write-up says which.
</details>

<details><summary>Does this hub contain the games?</summary>
No. No game files and no decompiled game code are here. The release builds live in the flash-games repo, where
rights holders can ask for removal.
</details>

<details><summary>Will it work for my game?</summary>
Most Flash games can be done. Local multiplayer games (path A) are the quickest; obfuscated single-player action games
take the longest. Check the directory first.
</details>
