"""Unwrap a MochiCrypt-protected SWF: decrypt the binaryData "mochicrypt.Payload" into the real game SWF.

  python -I tools/unmochi.py wrapped.swf inner.swf

MochiCrypt's Preloader.finish(): RC4 keyed with the payload's last 32 bytes, applied to the first
min(len - 32, 131072) bytes, then zlib. Build the mod from the inner SWF (the dead Mochi ad wait goes with it).
"""
import struct
import sys
import zlib


def tags(body):
    nbits = body[0] >> 3
    pos = (5 + 4 * nbits + 7) // 8 + 4
    while pos < len(body):
        cl = struct.unpack("<H", body[pos:pos + 2])[0]
        code, ln = cl >> 6, cl & 0x3F
        pos += 2
        if ln == 0x3F:
            ln = struct.unpack("<I", body[pos:pos + 4])[0]
            pos += 4
        yield code, body[pos:pos + ln]
        pos += ln
        if code == 0:
            break


def rc4_payload(d):
    """Decrypts (or encrypts: RC4 is symmetric) a payload in place: key = last 32 bytes."""
    d = bytearray(d)
    n = len(d) - 32
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + d[n + (i & 31)]) & 255
        S[i], S[j] = S[j], S[i]
    i = j = 0
    for k in range(min(n, 131072)):
        i = (i + 1) & 255
        u = S[i]
        j = (j + u) & 255
        v = S[j]
        S[i], S[j] = v, u
        d[k] ^= S[(u + v) & 255]
    return d


def unwrap(data):
    """The inner SWF's bytes; raises ValueError when there is no payload or it doesn't decrypt."""
    body = zlib.decompress(data[8:]) if data[:3] == b"CWS" else data[8:]
    blobs, names = {}, {}
    for code, t in tags(body):
        if code == 87:  # DefineBinaryData: id, reserved, data
            blobs[struct.unpack("<H", t[:2])[0]] = t[6:]
        elif code == 76:  # SymbolClass
            p = 2
            for _ in range(struct.unpack("<H", t[:2])[0]):
                cid = struct.unpack("<H", t[p:p + 2])[0]
                e = t.index(b"\0", p + 2)
                names[t[p + 2:e].decode("utf-8", "replace")] = cid
                p = e + 1
    if "mochicrypt.Payload" not in names or names["mochicrypt.Payload"] not in blobs:
        raise ValueError("no mochicrypt.Payload in this SWF")
    try:
        out = zlib.decompressobj().decompress(bytes(rc4_payload(blobs[names["mochicrypt.Payload"]])))
    except zlib.error as e:
        raise ValueError("payload doesn't decrypt: %s" % e)
    if out[:3] not in (b"FWS", b"CWS"):
        raise ValueError("payload isn't a SWF")
    return out


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    inner = unwrap(open(sys.argv[1], "rb").read())
    open(sys.argv[2], "wb").write(inner)
    print("%s: SWF %d, %d bytes" % (sys.argv[2], inner[3], len(inner)))
