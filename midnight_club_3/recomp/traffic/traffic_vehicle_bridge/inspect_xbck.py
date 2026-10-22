"""Read-only Dave archive probe for a vehicle XBCK's serialized shader bytes."""

import mmap
import struct
import sys


CHARS = "\0 #$()-./?0123456789_abcdefghijklmnopqrstuvwxyz~\x7f"


def u32(mm, at):
    return struct.unpack_from("<I", mm, at)[0]


def main(archive, needle):
    with open(archive, "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
        magic = mm[:4]
        count, info = u32(mm, 4), u32(mm, 8)
        print(f"magic={magic!r} entries={count} info={info:08X} bytes={len(mm)}")
        prev = ""
        hits = []
        for i in range(count):
            e = 0x800 + i * 16
            name_at = u32(mm, e) + info + 0x800
            off, full, comp = u32(mm, e + 4), u32(mm, e + 8), u32(mm, e + 12)
            if magic == b"Dave":
                at = name_at
                bits = []
                while True:
                    if len(bits) < 2 or (bits[0] >= 0x38 and len(bits) < 3):
                        word = int.from_bytes(mm[at:at + 3], "little")
                        at += 3
                        bits.extend((word >> (6 * k)) & 63 for k in range(4))
                    keep = 0
                    if bits[0] >= 0x38:
                        keep = (bits[1] - 0x20) * 8 + bits[0] - 0x38
                        bits = bits[2:]
                    else:
                        break
                    break
                name = prev[:keep]
                while True:
                    if not bits:
                        word = int.from_bytes(mm[at:at + 3], "little")
                        at += 3
                        bits.extend((word >> (6 * k)) & 63 for k in range(4))
                    c = bits.pop(0)
                    if not c or c >= len(CHARS):
                        break
                    name += CHARS[c]
            else:
                name = mm[name_at:mm.find(b"\0", name_at)].decode("ascii", "replace")
            prev = name
            if needle.lower() in name.lower():
                hits.append((name, off, full, comp))
        for name, off, full, comp in hits:
            print(f"{name} offset={off:08X} full={full:08X} packed={comp:08X}")
            if full == comp and off + full <= len(mm):
                print("header", mm[off:off + 32].hex(" "))
                for rel in (0x5ce0, 0x5ce4):
                    if rel + 16 < full:
                        print(f"+{rel:05X}", mm[off + rel:off + rel + 16].hex(" "))
        if not hits:
            print("No matching name")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
