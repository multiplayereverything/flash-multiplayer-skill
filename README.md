# Flash multiplayer skill

An agent skill for turning a Flash game (`.swf`, AS2 or AS3) into an online multiplayer mod that plays through the
[Multiplayer Everything](https://discord.com/invite/P2MSSUf5GX) global mod relay: the host gets a 5-letter room code,
friends type it or pick the room from a public list, and nobody opens ports.

It's written down from ten working mods: Bad Ice-Cream, Stealth Hunter 2, Gun Mayhem 2, Air Battle, Intrusion and
Intrusion 2, Territory War, Bow Man, Ultimate Crab Battle and Raft Wars. The finished builds are in
[flash-games](https://github.com/Multiplayer-Everything-Team/flash-games).

## Install
Copy this folder into your agent's skills folder as `flash-multiplayer`. For Claude Code:
```bash
git clone https://github.com/multiplayereverything/flash-multiplayer-skill ~/.claude/skills/flash-multiplayer
```
Then ask for something like "make this swf multiplayer" in the game's folder.

## What's inside
| Path | What |
|---|---|
| `SKILL.md` | The route, the rules and the tool list |
| `references/` | Recon, build (AS3 and AS2), network, hooking, the online panel, the lab, traps, the ten mods, release |
| `tools/` | FFDec helpers (stub classes, namespace guard, DoAction insert), SWF header and frame-label readers, window capture |
| `templates/` | Relay clients and mods-info readers (AS3 and AS2), build scripts, lab runners and offline checks |

## Needs
Java 21, [FFDec](https://github.com/jindrapetrik/jpexs-decompiler) 26.x (set `FFDEC` to `ffdec-cli.jar`), Python 3.10+,
[Ruffle](https://ruffle.rs) desktop, and a copy of the relay for local tests.

## Not included
No game files and no decompiled game code. The templates are the mods' own network, build and test code; game-specific
parts are marked where you must change them.

## Updating
This skill is updated as the mods learn new things. Fixes and new traps are welcome as pull requests.
