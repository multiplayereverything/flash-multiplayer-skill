"""Edits to game classes, applied at build time by build_as3_patches.py.

The game's classes are copied from ../decompiled/ into the build folder and edited there, so the mod's own
source never contains game code. Every edit names the file (as FFDec exported it, relative to the scripts
folder), the exact old text, the new text, and how many times the old text must appear.
"""

EDITS = [
    # ("com/example/game/Player.as",
    #  "      public function update() : void\n      {\n",
    #  "      public function update() : void\n      {\n         if(mynet.Net.skipUpdate(this)) { return; } // MOD\n",
    #  1),
]

# Whole-file rewrites: file -> function(text) -> text. Use for mechanical fixes such as turning
# constructor-assigned `public const` into `var` (#1074 after recompiling).
REWRITES = {}


def apply(name, text):
    text = text.replace("\r\n", "\n")
    if name in REWRITES:
        text = REWRITES[name](text)
    for f, old, new, count in EDITS:
        if f == name:
            n = text.count(old)
            assert n == count, "%s: expected %d match(es), found %d for:\n%s" % (f, count, n, old)
            text = text.replace(old, new)
    return text


def files():
    return sorted(set([e[0] for e in EDITS]) | set(REWRITES))
