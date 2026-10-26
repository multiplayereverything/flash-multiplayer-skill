# Templates

Taken from working mods. Rename before use:

| File | From | Change |
|---|---|---|
| `as3/RelayClient.as`, `NetModInfo.as`, `NetJson.as` | Air Battle Online | package `mynet`, `GAME_ID` and `VERSION` in `NetModInfo`, and its calls into your `Net` (`Net.log`, `Net.infoChanged`, `Net.address`, `Net.params`, `Net.LAB`) |
| `as3/LobbyBridge.as` | Bad Ice-Cream Online | package `mynet`; call it instead of RelayClient when FlashVar `lobby=1`, and handle `DR\|slot` / `BK\|slot` |
| `as2/relay.as` | Ultimate Crab Battle Online | `_global.MYN` fields listed in its header; the `removeShips()` call is a game hook |
| `as2/modinfo.as` | Territory War Online | set `N.GAME_ID` before `miStart()`; `_global.MY_MODINFO` is the test URL |
| `build/build_as3.py` | Bad Ice-Cream Online | game file, package, output names; drop the Poki ad-fix step |
| `build/build_as3_patches.py` | Intrusion 2 Online | the `EDITS` list (yours goes in your own `patches.py`), class list, compile fixes |
| `build/build_as2_insert.py` | Territory War Online | game file, frame, module list, lab flag line |
| `build/build_as2_splice.py` | Intrusion Online | game file, spare slot frames, target frame |
| `lab/lab_as3.py` | Air Battle Online | lab port, SWF name, FlashVars, `KNOWN_GAME_ERRORS` |
| `lab/lab_as2.py` | Territory War Online | the same, plus the hash check |
| `lab/lab_games.json` | | your id, name and max players |
| `lab/fake_bridge.py` | Bad Ice-Cream Online | nothing: pass the lab port and one session token per window (host first) |
| `lab/relay_check.py`, `modinfo_check.py`, `test_messages.py` | Air Battle Online | game id, version, message regexes |

The lab scripts read the relay path from the `MOD_RELAY` environment variable (the relay's `init.py`) and FFDec from
`FFDEC`.
