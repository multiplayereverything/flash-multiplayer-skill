"""Checks that a co-op SWF with 1 player plays exactly like the untouched game: replays both in Ruffle Together
from the same input script and compares their fingerprints frame by frame.

  python -I solo_check.py --exe ruffle_desktop.exe --mod dist/Game_coop.swf --original ../Game.swf
      --keys solo.keys --script solo.txt --frames 3000 [--allow 10-40,95] [--out solo]

`--keys` must be a 1-slot map (one `slot 0:` line), so the replay has one player. `--allow` lists frames that may
differ (where the mod's own menu button shows); every other differing frame fails. Prints the differing frames as
ranges. Exit code 0 only if both runs wrote every frame and nothing outside --allow differs.
"""
import argparse
import os
import subprocess
import sys


def replay(args, swf, out):
    r = subprocess.run([args.exe, "--coop-replay", swf, "--coop-keys", args.keys, "--coop-script", args.script,
                        "--coop-frames", str(args.frames), "--coop-out", out], capture_output=True, text=True,
                       errors="replace")
    if not os.path.exists(out):
        sys.exit("replay of %s wrote nothing:\n%s" % (swf, (r.stdout + r.stderr)[-2000:]))
    prints = {}
    for line in open(out, encoding="utf-8"):
        parts = line.split()
        if len(parts) == 2:
            prints[int(parts[0])] = parts[1]
    return prints


def frames(spec):
    out = set()
    for part in filter(None, spec.split(",")):
        a, _, b = part.partition("-")
        out.update(range(int(a), int(b or a) + 1))
    return out


def ranges(numbers):
    out, run = [], []
    for n in sorted(numbers):
        if run and n == run[-1] + 1:
            run.append(n)
        else:
            if run:
                out.append(run)
            run = [n]
    if run:
        out.append(run)
    return ", ".join(str(r[0]) if len(r) == 1 else "%d-%d" % (r[0], r[-1]) for r in out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--exe", required=True, help="Ruffle Together's ruffle_desktop.exe (the release you ship for)")
    ap.add_argument("--mod", required=True, help="the co-op SWF")
    ap.add_argument("--original", required=True, help="the untouched game SWF")
    ap.add_argument("--keys", required=True, help="a 1-slot key map")
    ap.add_argument("--script", required=True)
    ap.add_argument("--frames", type=int, default=3000)
    ap.add_argument("--allow", default="", help="frames that may differ, e.g. 10-40,95")
    ap.add_argument("--out", default="solo")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    mod = replay(args, args.mod, os.path.join(args.out, "mod.txt"))
    original = replay(args, args.original, os.path.join(args.out, "original.txt"))
    differ = {f for f in range(args.frames) if mod.get(f) != original.get(f)}
    allowed = differ & frames(args.allow)
    bad = differ - allowed
    print("%d frames, %d differ (%d allowed)" % (args.frames, len(differ), len(allowed)))
    if allowed:
        print("allowed: " + ranges(allowed))
    if bad:
        print("DIFFER: " + ranges(bad))
    sys.exit(0 if not bad and len(mod) == len(original) == args.frames else 1)


if __name__ == "__main__":
    main()
