"""Prints frame labels of the main timeline and of chosen sprites: python swfinfo.py game.swf [spriteId ...]"""
import struct
import sys
import zlib


def tags(b, off, end):
    while off < end:
        cl = struct.unpack("<H", b[off:off + 2])[0]
        t, l = cl >> 6, cl & 63
        off += 2
        if l == 63:
            l = struct.unpack("<I", b[off:off + 4])[0]
            off += 4
        yield t, off, l
        off += l
        if t == 0:
            return


def labels(b, off, end):
    frame, out = 1, []
    for t, o, l in tags(b, off, end):
        if t == 1:
            frame += 1
        elif t == 43:
            out.append((frame, b[o:o + l].split(b"\0")[0].decode("latin1")))
    return frame - 1, out


d = open(sys.argv[1], "rb").read()
b = zlib.decompress(d[8:]) if d[:3] == b"CWS" else d[8:]
nb = b[0] >> 3
start = (5 + 4 * nb + 7) // 8 + 4
print("main", labels(b, start, len(b)))
want = {int(x) for x in sys.argv[2:]}
for t, o, l in tags(b, start, len(b)):
    if t == 39:
        sid = struct.unpack("<H", b[o:o + 2])[0]
        if sid in want:
            print(sid, labels(b, o + 4, o + l))
