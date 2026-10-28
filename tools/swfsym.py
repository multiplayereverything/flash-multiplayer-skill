"""Links a library sprite to an AS3 class with a new SymbolClass tag right after the sprite's definition.

  python -I swfsym.py in.swf out.swf <characterId> <class.Name>

Used when a game's sprite has no class (no linkage), so the mod can `new` it: the class must already be in the
SWF's ABC (a stub from AddClasses, compiled by -importScript as `public dynamic class X extends MovieClip`).
"""
import struct
import sys
import zlib


DEFINES = {2, 6, 7, 10, 11, 14, 20, 21, 22, 32, 33, 34, 35, 36, 37, 39, 46, 48, 60, 75, 83, 84, 87, 90}


def link(data, char_id, name):
    """A new SymbolClass tag right after the character's Define tag (a link before the definition makes Ruffle
    register the character twice)."""
    sig, ver = data[:3], data[3]
    body = bytearray(zlib.decompress(data[8:]) if sig == b"CWS" \
                else data[8:])
    nbits = body[0] >> 3
    pos = (5 + 4 * nbits + 7) // 8 + 4
    while pos < len(body):
        cl = struct.unpack("<H", body[pos:pos + 2])[0]
        code, ln = cl >> 6, cl & 0x3F
        hdr = 2
        if ln == 0x3F:
            ln = struct.unpack("<I", body[pos + 2:pos + 6])[0]
            hdr = 6
        end = pos + hdr + ln
        if code in DEFINES and struct.unpack("<H", body[pos + hdr:pos + hdr + 2])[0] == char_id:
            entry = struct.pack("<HH", 1, char_id) + name.encode() + bytes(1)
            body[end:end] = struct.pack("<HI", (76 << 6) | 0x3F, len(entry)) + entry
            out = bytes(body)
            return (b"CWS" + bytes([ver]) + struct.pack("<I", len(out) + 8) + zlib.compress(out, 9)) if sig == b"CWS" \
                else (b"FWS" + bytes([ver]) + struct.pack("<I", len(out) + 8) + out)
        if code == 0:
            break
        pos = end
    raise ValueError("character %d is not defined at the top level" % char_id)


if __name__ == "__main__":
    src, dst, cid, cls = sys.argv[1:5]
    open(dst, "wb").write(link(open(src, "rb").read(), int(cid), cls))
    print("linked sprite %s to %s" % (cid, cls))
