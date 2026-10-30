# Playbook

Technique pages for making a Flash game play online in Ruffle Together. Each page is about one thing, and each skill in
`.claude/skills/` points to the pages for its step. When a technique is missing or wrong, fix the page and say which
game taught you.

| Page | What it covers | Used by |
|---|---|---|
| [recon.md](recon.md) | Reading the SWF: version, wrappers, obfuscation, where each system runs | flash-start, flash-map |
| [build.md](build.md) | Getting code into the SWF: AS3 importScript, AS2 DoAction tags, splicing | flash-inject |
| [ruffle-together.md](ruffle-together.md) | How Ruffle Together works, the co-op API, key maps, the pinned build | flash-coop, flash-lab, flash-ship |
| [traps.md](traps.md) | Every trap found so far, with the game that hit it | all phases |
| [release.md](release.md) | The co-op SWF, its launch line, mods-info, the launcher entry | flash-ship, flash-share |
| [coop-api.md](coop-api.md) | Every call Ruffle Together offers a game (co-op API v2), and what it does by itself | flash-coop, flash-lab |
| [tools.md](tools.md) | The scripts in `tools/` and the templates in `templates/`, and what each does | all phases |
| [relay-protocol.md](relay-protocol.md) | The relay's messages, for running your own relay | flash-ship |

## Status of the relay
Ruffle Together is the only route for players now. The relay (`relay/`) is still in the repo for people who run their
own server, so the relay pages describe that setup and are not the main path. The pinned build for the mods is in
[ruffle-together.md](ruffle-together.md).
