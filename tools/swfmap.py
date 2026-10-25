"""Recon helper: reads FFDec's -swf2xml dump and prints the display tree.

  python tools/swfmap.py ../decompiled/ucb.xml tree        root timeline placements by frame
  python tools/swfmap.py ../decompiled/ucb.xml parents 88  where sprite 88 is placed
  python tools/swfmap.py ../decompiled/ucb.xml sprite 88   one sprite's frames, labels and children
  python tools/swfmap.py ../decompiled/ucb.xml exports     linkage names (attachMovie ids)
"""
import sys
import xml.etree.ElementTree as ET


def frames(tags):
    """[(frame number, label, [(depth, charId, name)])] for a tag list."""
    out, n, label, placed = [], 1, None, []
    for t in tags:
        ty = t.get("type")
        if ty in ("PlaceObject2Tag", "PlaceObject3Tag", "PlaceObjectTag"):
            placed.append((t.get("depth"), t.get("characterId"), t.get("name")))
        elif ty == "FrameLabelTag":
            label = t.get("name")
        elif ty == "ShowFrameTag":
            out.append((n, label, placed))
            n, label, placed = n + 1, None, []
    return out


def main():
    root = ET.parse(sys.argv[1]).getroot()
    tags = root.find("tags")
    sprites = {t.get("spriteId"): t for t in tags if t.get("type") == "DefineSpriteTag"}
    cmd = sys.argv[2]
    if cmd == "tree":
        for n, label, placed in frames(list(tags)):
            items = ["%s:%s%s" % (d, c, "=" + nm if nm else "") for d, c, nm in placed if c or nm]
            if label or items:
                print(n, label or "", " ".join(items))
    elif cmd == "parents":
        want = sys.argv[3]
        for sid, s in sprites.items():
            for n, label, placed in frames(list(s.find("subTags"))):
                for d, c, nm in placed:
                    if c == want:
                        print("sprite", sid, "frame", n, "depth", d, "name", nm)
        for n, label, placed in frames(list(tags)):
            for d, c, nm in placed:
                if c == want:
                    print("ROOT frame", n, "depth", d, "name", nm)
    elif cmd == "sprite":
        s = sprites[sys.argv[3]]
        fr = frames(list(s.find("subTags")))
        print("frames", len(fr))
        for n, label, placed in fr:
            items = ["%s:%s%s" % (d, c, "=" + nm if nm else "") for d, c, nm in placed if c or nm]
            if label or items:
                print(n, label or "", " ".join(items))
    elif cmd == "exports":
        for t in tags:
            if t.get("type") == "ExportAssetsTag":
                for item in t.iter():
                    if item.text and item.text.strip():
                        pass
                tg = [x.text for x in t.find("tags")] if t.find("tags") is not None else []
                nm = [x.text for x in t.find("names")] if t.find("names") is not None else []
                for a, b in zip(tg, nm):
                    print(a, b)


main()
