"""SWF 6 is case-insensitive: lists identifiers in src/bmnet that differ only by case.

  python tools/case_scan.py

Expected: bmn/BMN (_global.BMN is a property read, never a local) and lab/LAB (_root.lab vs bmn.LAB).
"""
import collections
import glob
import os
import re

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "bmnet")
ALLOWED = {"bmn", "lab"}

bad = 0
everything = collections.defaultdict(set)
for path in sorted(glob.glob(os.path.join(SRC, "*.as"))):
    code = open(path, encoding="utf-8").read()
    code = re.sub(r'"(?:[^"\\\n]|\\.)*"', "", code)
    code = re.sub(r"//[^\n]*", "", code)
    seen = collections.defaultdict(set)
    for name in set(re.findall(r"[A-Za-z_]\w*", code)):
        seen[name.lower()].add(name)
        everything[name.lower()].add(name)
    clashes = {k: sorted(v) for k, v in seen.items() if len(v) > 1 and k not in ALLOWED}
    print(os.path.basename(path), clashes or "ok")
    bad += len(clashes)
# the files share one object (bmn), so its property names must not clash across files either
clashes = {k: sorted(v) for k, v in everything.items() if len(v) > 1 and k not in ALLOWED}
print("all files", clashes or "ok")
bad += len(clashes)
raise SystemExit(1 if bad else 0)
