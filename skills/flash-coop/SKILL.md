---
name: flash-coop
description: Add players to a Flash game for Ruffle Together - local co-op in a single-player SWF (extra heroes driven by coop.buttons or their own key codes, "the player" pointing at the right copy, cameras, name tags, the player count), a game's own key map with coop.keys, and the co-op API's one rule (gameplay uses only shared answers). Use for path B games, turn-based games that need each slot's keys, or any SWF built to call coop.* through ExternalInterface.
---

# Flash co-op

Paths here are relative to the hub root, two folders up from this file (`../../`), where `references/`, `tools/`, `templates/`, `games/` and `DIRECTORY.md` live.

Read `references/ruffle-together.md` first (the co-op API, "Adding players to a single-player game"). Ruffle
Together keeps every PC's game the same; your job is only to make the game have more than one player.

Checklist:
- **How many?** `coop.players` (or a PLAYERS menu button). With 1 player, or outside Ruffle Together, the game must
  be the untouched original.
- **Each player's input:** `coop.buttons(slot)` / `coop.button(slot, "FIRE")`, or key codes the game never reads
  that the key map gives each slot, routed to that player's copy before the game sees them. Every player's mouse:
  `coop.mouseX/mouseY/mouseDown(slot)`.
- **Every place that reads "the player"** (`CODE_MAP.md`): enemies' target, pickups, damage, doors, level end,
  camera. Point each at the right copy, or try every copy in hit tests.
- **The screen:** one camera on the players' middle, or `coop.camera(slot, x, y, zoom)` for every slot each frame
  (picture only, so each PC may follow its own player); `coop.hud(path)` keeps a HUD on screen; `coop.label` puts
  names above the players.
- **Turn-based:** read each slot's keys from a map with enough slots and act only on the turn owner's.
- **The game's own key map:** `coop.keys(text)` on frame 1, when every player should press the original keys on
  their own PC.
- **Leaving:** `coop.events` says `leave N`; that player holds nothing from then on. Decide what their hero does;
  a turn-based game must skip their turn.
- **Every player can do everything:** enemies target every player, pickups, refills and the game's actions work for
  every player, and nothing only P1 can trigger blocks the rest (found missing before: ammo refilling only P1, a
  final ride moving one soldier, P2-P4 aiming only with keys). Aim with each player's own mouse via
  `coop.mouseX/mouseY(slot)`; only the host's mouse reaches the game's own.

**The one rule:** gameplay may use only shared answers. `coop.localSlot`, `coop.isHost` and `coop.ping` differ
between PCs: use them for text, colours and sounds on this PC only. A local value that moves, shows or creates
anything makes the PCs' games split (OUT OF SYNC).

Helpers: `ruffle-coop/tools/coop-api/as2/RuffleTogether.as` and `as3/RuffleTogether.as` wrap every call and answer
like a single-player game outside Ruffle Together. `ruffle-coop/tools/coop-api/demo/` shows every call on screen.

Desync? Ruffle Together writes a report of what differs on each PC. Look for a local answer reaching gameplay, a
sound removed in `onSoundComplete` on an old build, or objects ordered by something only one PC has
(`references/traps.md`, Process).
