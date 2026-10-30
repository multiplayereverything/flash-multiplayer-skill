"""Replays a co-op SWF twice from the same input script in Ruffle Together and checks both runs match.

  python -I replay_check.py --exe ruffle_desktop.exe --swf dist/Game_coop.swf --keys example.keys
      --script example-2p.txt --frames 1500 [--shots 100,800,1400] [--out replays]

Writes <out>/run1.txt and run2.txt (one "frame fingerprint" line per frame) and, with --shots, PNGs of the first
run. Exit code 0 only if both runs wrote every frame and the files are identical. Look at the PNGs: a run that
sat on the title screen also matches.
"""
import argparse
import filecmp
import os
import subprocess
import sys


def replay(args, out, shots):
    cmd = [args.exe, "--coop-replay", args.swf, "--coop-keys", args.keys, "--coop-script", args.script,
           "--coop-frames", str(args.frames), "--coop-out", out]
    if shots:
        cmd += ["--coop-shot", shots]
    r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if not os.path.exists(out):
        sys.exit("replay wrote nothing:\n" + (r.stdout + r.stderr)[-2000:])
    lines = open(out, encoding="utf-8").read().split()
    return len(lines) // 2


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--exe", required=True, help="Ruffle Together's ruffle_desktop.exe")
    ap.add_argument("--swf", required=True)
    ap.add_argument("--keys", required=True, help="a built-in key map name or a .keys file")
    ap.add_argument("--script", required=True)
    ap.add_argument("--frames", type=int, default=1500)
    ap.add_argument("--shots", default="", help="frames to save as PNG from the first run, e.g. 100,800")
    ap.add_argument("--out", default="replays")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    first, second = os.path.join(args.out, "run1.txt"), os.path.join(args.out, "run2.txt")
    n1 = replay(args, first, args.shots)
    n2 = replay(args, second, "")
    same = filecmp.cmp(first, second, shallow=False)
    print("run 1: %d frames, run 2: %d frames, identical: %s" % (n1, n2, same))
    if args.shots:
        print("screenshots: %s/run1.<frame>.png - look at them" % args.out)
    sys.exit(0 if same and n1 == n2 == args.frames else 1)


if __name__ == "__main__":
    main()
