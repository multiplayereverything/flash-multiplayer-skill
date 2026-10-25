"""Set the UseNetwork flag of a SWF, so Flash Player lets a local file open sockets.

  python set_use_network.py game.swf [out.swf]

Rewrites in place without out.swf. The result is zlib-compressed (CWS). SWF files older than version 8 have no
FileAttributes tag; they are recompressed unchanged and the script says so (Flash Player won't open sockets from
them anyway; use Ruffle).
"""
import struct
import sys
import zlib


def body_of(data):
    if data[:3] == b"CWS":
        return zlib.decompress(data[8:])
    if data[:3] == b"FWS":
        return data[8:]
    raise SystemExit("not an uncompressed or zlib SWF (LZMA ZWS files: decompress with FFDec first)")


def first_tag_pos(body):
    nbits = body[0] >> 3
    return (5 + 4 * nbits + 7) // 8 + 4


def set_use_network(data):
    """Returns (new bytes, True if the flag is now set)."""
    body = body_of(data)
    pos = first_tag_pos(body)
    code = struct.unpack("<H", body[pos:pos + 2])[0] >> 6
    found = code == 69
    if found:
        body = body[:pos + 2] + bytes([body[pos + 2] | 1]) + body[pos + 3:]
    head = b"CWS" + data[3:4] + struct.pack("<I", len(body) + 8)
    return head + zlib.compress(body, 9), found


def has_use_network(data):
    body = body_of(data)
    pos = first_tag_pos(body)
    return struct.unpack("<H", body[pos:pos + 2])[0] >> 6 == 69 and bool(body[pos + 2] & 1)


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        raise SystemExit(__doc__)
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) == 3 else src
    out, found = set_use_network(open(src, "rb").read())
    open(dst, "wb").write(out)
    print(("UseNetwork set: " if found else "no FileAttributes tag (SWF < 8), recompressed only: ") + dst)
