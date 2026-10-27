# The lab

A lab build hosts, joins and plays itself. A Python runner starts a local relay and two to four small Ruffle windows,
reads their `trace()` output, takes screenshots, and prints a PASS/FAIL table. Build it before the features, so every
feature is proven by a check instead of guessed. Nobody's keyboard or mouse is used.

Templates: `templates/lab/lab_as3.py` (from Air Battle: relay, host, guests, late joiner, wrong-code window),
`templates/lab/lab_as2.py` (from Territory War: adds a per-turn state hash compare), `templates/lab/lab_games.json`.

## The runner
1. Build the lab SWF (`python -I build.py --lab`). Don't build while a lab is starting.
2. Refuse to start if the lab port is busy. Pick one port per mod and never share it; avoid ports real sessions use.
3. Start the hub's relay (`relay/init.py`, set `MOD_RELAY` to its path) on `127.0.0.1:<port>`:
   ```bash
   python init.py --port 7801 --bind 127.0.0.1 --log --games tools/lab_games.json --no-mods-info [--sim-delay 80 --sim-jitter 40]
   ```
   `lab_games.json`: `{"<id>": {"name": "...", "mode": "star", "max_players": 4, "framing": "nul", "versions": [], "idle": 300}}`.
   Wait until it accepts connections.
4. Start the host window:
   `ruffle.exe --tcp-connections allow -Plab=host -Prelay=127.0.0.1:<port> -Pname=Host <lab swf>`
   with `RUST_LOG=warn,avm_trace=info` (prints `trace()` to stdout), stdout to `logs/lab_host.log`, and
   `STARTUPINFO.wShowWindow = SW_SHOWNOACTIVATE`. Add `--storage memory -v 0` to keep it muted and out of real saves.
5. Pin each window small (about 420x360), topmost, tiled bottom-right, with `SWP_NOACTIVATE`. A fully covered Ruffle
   window stops running frames. Restore minimized windows without activating them.
6. Read `LAB| ROOM <code>` from the host log, start the guests with `-Pjoin=<code>`, and start the late joiner when the
   host prints `LAB| LATE`.
7. Poll the logs every 0.3 s. On `LAB| SNAP <name>`, capture that window by PID (`tools/wincap.py`) into
   `shots/<who>_<name>.png`.
8. Finish when every log has `LAB DONE`, or on timeout or a process exit. Kill the windows first, then the relay, by
   PID with `taskkill /PID <pid> /T /F`: only processes the lab started.
9. Print `| Window | Check | Result | Evidence |` from `LAB| PASS <check> | <evidence>` and `LAB| FAIL ...` lines.
   Exit 1 on any FAIL, an unfinished window, or any AVM error.

**AVM errors:** strip ANSI colour codes first (Ruffle puts them between "ERROR" and the module name), then count
`ERROR ... avm1|avm2` entries and AS2 `WARN ruffle_core::avm1` lines. Bugs of the original game go in a
`KNOWN_GAME_ERRORS` list as whole-stack regexes and are reported apart. Stop a run on an error storm (300+ repeats).

## The in-game runner
A `NetLab` class (AS3) or `lab.as` (AS2) runs steps: `[name, fn(age):Boolean, maxFrames]`. A step passes when its
function returns true; a timeout is a FAIL with the reason. The host directs guests with `LB|` messages. Scripted input
replaces the real one: the input layer's `labMode` ignores real keys and mouse, and `labSet(key, down)` drives the game.
AS2 variants: a key wrapper reading `N.labKeys`, a transparent shield clip that swallows real clicks, `Mouse.addListener`
replaced so the lab calls the handlers itself.

Lab lines can also go through the relay as `D|LAB ...`, which helps when a window (Flash Player) has no log.

## Runs to keep
| Run | Proves |
|---|---|
| default (2 players) | host and guest connect, see each other, play a level, end it |
| `--guests 2` / `--players 3`, `4` | 3-4 players and a late joiner, from the public list |
| `--solo` | no network: single player plays unchanged |
| a control run that must FAIL (e.g. a build without one fix) | the check can fail |
| `--host-leaves`, `--guest-leaves` | clean end of session with the reason on every window |
| `--wrong-code`, `--wrong-version` | refused with a readable reason |
| `--delay 80 --jitter 40` | still smooth and in sync with lag |
| `--modinfo <url>` with a local `http.server`, and `--modinfo-relay` | mods-info download and the relay INFO fallback |
| `--direct`, `--direct --third`, `--third` | DIRECT (the relay's legacy room) plays like RELAY; a second friend is turned away in both modes, and the host keeps its Player 2 |
| `--late-join` | the host plays alone, the guest joins mid-level (from its own preloader); the host restarts the level for 2 |
| `--help-hold 100` | the host's game stays paused (help popup) while the guest keeps drawing: what runs on timelines alone |
| `--lobby`, `--lobby --drop`, `--lobby --host-leaves` | started the way the launcher's lobby starts the game, through `templates/lab/fake_bridge.py`; a dropped connection that comes back |
| `--release-smoke` | the release build starts with the relay typed as a closed local port, never touching your live relay |

Turn games: compare a `LAB| HASH <turn> <state>` line between host and guest at every turn start.

## Offline checks (no Flash)
- `templates/lab/test_messages.py`: every message type that is sent has a handler and is documented; version strings
  agree; session reset clears every field. Its regexes are per mod.
- `templates/lab/relay_check.py`: raw-socket checks against the local relay (version refused, full room, wrong code,
  star traffic both ways, `X` on host leave).
- `templates/lab/modinfo_check.py`: a local HTTP mods-info end to end, plus the relay INFO fallback and `min_version`.

## Rules
- A run counts only with 0 AVM errors and every window finished.
- Look at the screenshots after UI or drawing changes; the checks don't see layout.
- Never send OS input to the user's windows. PostMessage to the lab's own Ruffle windows is the furthest any mod went
  (key messages reach Ruffle, never Flash Player).
- Ruffle windows can take more than 10 s to open while other labs run; wait up to 100 s.
- PrintWindow can return black for Ruffle's GPU surface; fall back to BitBlt. Declare 64-bit `argtypes`/`restype` in
  ctypes or windows aren't resized and captures come out black.
- Only test as far as you can see: anything not tried between two real PCs on different networks is ⚠️ in the report.
