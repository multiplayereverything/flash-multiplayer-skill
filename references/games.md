# The mods this skill comes from

Borrow from the one closest to your game. Players counts include the host.

| Mod (relay id) | Game | Engine | Players | Sync model | Build |
|---|---|---|---|---|---|
| Bad Ice-Cream Online (`bic`) | tile arcade, 2-player co-op | AS3 SWF 9, unobfuscated | 2 | host snapshot every frame on change (at least every 25), guest runs no logic, sounds by name | patched game classes + stubs; Poki ad wait and ExternalInterface fixed |
| Stealth Hunter 2 Online (`sh2`) | stealth campaign | AS3 SWF 11, obfuscated, wrapped | 2-4 | host snapshot at 15 Hz + events, smoothing and extrapolation; later each player moves their own character (`ME`) and the host follows | subclasses and an engine component (no recompiles of subclassed classes); unwrap/wrap; `_direct.swf` for tests |
| Air Battle Online (`airbattle`) | Box2D physics, level-based | AS3 SWF 9 | 2-4 | host snapshot every frame (moved bodies + 1 s keyframe) + events calling the game's own functions; guest holds poses after its step | 26 patched classes + stubs; offline message, relay and mods-info checks |
| Intrusion 2 Online (`intrusion2`) | side-scrolling shooter, Box2D | AS3 SWF 9, partly obfuscated | 2-4 | each PC runs its own hero; remote heroes are real heroes fed by input and steered; host owns enemies, damage (`DM`), triggers | patches on fresh decompiled copies at build time (`EDITS` list), case-sensitive staging, damage gate across 41 files |
| Gun Mayhem 2 Online (`gm2`) | platform brawler with local 4-player | AS2 in SWF 9 | 2-4 | input lockstep from the host, seeded RNG via p-code, snapshot + RNG every 35 frames; private key codes per slot | p-code patch + frame script import; keeps a DIRECT mode as second choice |
| Territory War Online (`tw`) | turn-based teams (artillery) | AS2 SWF 8 | 2-4 (red/blue seats) | host runs the match, `SN` per frame; the turn owner aims and charges locally and sends `FIRE`; per-turn hash compare in the lab | new DoAction tags on frame 3 (`InsertAction.java`); `_global.Key` wrapper |
| Bow Man Online (`bowman`) | 2 archers, turns | AS2 SWF 6 | 2 | events only (`FIRE`, `LAND`), both fly the arrow, host corrects; positions rounded to twips | export, patch exactly once, append, import; case scan; Ruffle only |
| Ultimate Crab Battle Online (`ucb`) | boss-fight shmup, single player | AS2 SWF 6, obfuscated | 2-4 co-op | own ship local, shots to the host, a "world mirror" of every `_root` clip by depth path (delta every 3 frames, full every 68); shared HP; late join mid-fight | patched tiny scripts + mod setup on frame 1; `swfmap.py` for the display tree |
| Raft Wars Online (`raftwars`) | turn-based artillery campaign | AS2 SWF 8, obfuscated | 2-4 co-op on one raft | turns rotate through players; host mirror snapshot every 2nd frame, guests play back 4 frames behind; timeline guard on guests; shared credits in the shop | deobfuscated frame-5 export cached + mod appended |
| Intrusion Online (`intrusion`) | platform shooter | AS2 SWF 8, obfuscated | 2-4 co-op | own soldier local; host stand-ins for guests inheriting the hero prototype; `_root.knight` swapped to the nearest player around each enemy update; damage and pickups sent to owners | compile in spare `stop()` slots, splice DoAction tags into the untouched SWF |

## Why each model
- Lockstep worked only for Gun Mayhem 2, which already had local 4-player, after every random call was replaced with a
  seeded one and a periodic snapshot repaired drift.
- Everywhere else, `Math.random`/`random()` in many files, wall-clock timers, timeline scripts and Box2D made two
  copies of the world drift, so the host's world is the only world.
- Turn-based games let the turn owner aim locally because a round trip on the power meter overshoots.
- Action games let each player move locally because waiting a round trip for your own jump feels broken; the host still
  owns everything that can hurt or reward.
- Obfuscated AS2 games without functions to hook (Ultimate Crab Battle) mirror clip frames and positions instead.
