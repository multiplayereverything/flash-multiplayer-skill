---
name: flash-sync
description: Make a Flash game's players see the same game: host-authoritative sync over the global mod relay's star mode, message design, turn-based, snapshot, local-movement and lockstep models, remote input injection (key wrappers, private key codes, swapped player objects), net ids from creation order, smoothing, late join, leaving, saves and the online panel with Online as the default. Use when writing or debugging a Flash mod's network code, a desync, a frozen guest, players moving each other, or the HOST/JOIN panel.
---

# Flash sync

Paths here are relative to the hub root, two folders up from this file (`../../`), where `references/`, `tools/`, `templates/`, `games/` and `DIRECTORY.md` live.

Read in this order: `references/network.md` (the relay, the models, messages, identity, smoothing, join and leave),
`references/hooking.md` (getting remote players into a one-player game), `references/ui.md` (the panel).

Checklist for each system you sync (write the answer in the mod's `AGENTS.md`, "who owns what"):
- Who decides it? (Almost always the host.)
- What do guests send? (Input or a request, never the result.)
- What do guests see, and how smooth? (Snapshot, event replay, local prediction.)
- What happens on a late join, a guest leaving, the host leaving?
- What's the lab check that proves it?

Connection code: `templates/as3/RelayClient.as` or `templates/as2/relay.as`. Mods-info: `templates/as3/NetModInfo.as`
or `templates/as2/modinfo.as` (set `N.GAME_ID` first). Online on the main relay is the default; save only the server
the player typed.

Bump the version string whenever a message changes. Never reuse a relay letter (`W J L G X E D`) as a message type.

Desync? First check identity (creation order, instance names vs depth paths), number formatting (twips, 15 digits),
random calls on the guest, and update order (`references/traps.md`).
