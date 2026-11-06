"""mc3_xbox_assets: list or extract the Rockstar "Dave" archives of MC3 Remix on Xbox (assets_x.dat, assets_x.dat_1..).

    mc3_xbox_assets.py list <archive> [pattern]        offset, size, stored size and name of each entry
    mc3_xbox_assets.py extract <archive> <folder>      one archive
    mc3_xbox_assets.py unpack <game folder> <folder> [prefix...]
        every file of the game's archives (assets_x.dat, then _1.._8: a later archive's copy wins, as in the
        game), optionally only those under the given prefixes, e.g. tune/

This tool reads no environment variables: the archives and the output folder are arguments.

Origin: the MC3 Xbox C++ decompilation (MC3-Decomp, tools/dave.py), written for mc_research by SaltySasha.

Format (read by the game's zipFile at 0x002b3d20 in default.xbe):
    0x000  "DAVE" (plain names) or "Dave" (packed names), file count, directory size, names size
    0x800  directory: per file name offset, data offset, size, stored size (deflate when they differ)
    then   names. Packed names use 6-bit characters, four per three bytes, from the table below; a name
           whose first code c0 is above 0x37 shares its first (c0 - 0x38) + 8 * (c1 & 0x1f) characters with
           the previous entry's name.
Entries with size 0 at a shared offset are folders.
"""
import os
import struct
import sys
import zlib

CHARS = '\0 #$()-./?0123456789_abcdefghijklmnopqrstuvwxyz~'


def codes(buf, pos):
    """6-bit codes of a packed name starting at byte pos (LSB first)."""
    bit = 0
    while True:
        byte, shift = divmod(bit, 8)
        v = buf[pos + byte] | (buf[pos + byte + 1] << 8 if pos + byte + 1 < len(buf) else 0)
        yield (v >> shift) & 0x3f
        bit += 6


def unpack_name(buf, pos):
    out = []
    for c in codes(buf, pos):
        if c == 0:
            break
        out.append(CHARS[c] if c < len(CHARS) else '?')
    return ''.join(out)


class Archive:
    def __init__(self, path):
        self.f = open(path, 'rb')
        magic, count, dirsize, namesize = struct.unpack('<4sIII', self.f.read(16))
        if magic not in (b'DAVE', b'Dave'):
            raise ValueError(f'{path}: not a Dave archive ({magic!r})')
        self.f.seek(0x800)
        d = self.f.read(dirsize)
        names = self.f.read(namesize)
        self.entries = []
        prev = ''
        for i in range(count):
            noff, off, size, csize = struct.unpack_from('<IIII', d, 16 * i)
            if magic == b'DAVE':
                name = names[noff:names.index(b'\0', noff)].decode('latin1')
            else:
                it = codes(names, noff)
                c0 = next(it)
                if c0 > 0x37:
                    c1 = next(it)
                    keep = (c0 - 0x38) + 8 * (c1 & 0x1f)
                    rest = []
                    for c in it:
                        if c == 0:
                            break
                        rest.append(CHARS[c] if c < len(CHARS) else '?')
                    name = prev[:keep] + ''.join(rest)
                else:
                    name = unpack_name(names, noff)
            prev = name
            self.entries.append((name, off, size, csize))

    def read(self, entry):
        name, off, size, csize = entry
        self.f.seek(off)
        data = self.f.read(csize)
        if len(data) != csize:
            raise SystemExit(f'{self.f.name}: truncated at {off} (wanted {csize} bytes, got {len(data)})')
        if csize != size:
            data = zlib.decompress(data, -15)
        return data


def extract_entries(a, root, prefixes=()):
    n = 0
    for e in a.entries:
        name, off, size, csize = e
        if name.endswith('/') or (size == 0 and csize == 0 and '.' not in os.path.basename(name)):
            continue
        if prefixes and not any(name.startswith(p) for p in prefixes):
            continue
        dst = os.path.join(root, *name.split('/'))
        if os.path.commonpath([os.path.abspath(root), os.path.abspath(dst)]) != os.path.abspath(root):
            raise SystemExit(f'refusing to write outside {root}: {name!r}')
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, 'wb') as f:
            f.write(a.read(e))
        n += 1
    return n


def main():
    if len(sys.argv) < 3 or sys.argv[1] in ('-h', '--help'):
        print(__doc__)
        return
    cmd, path = sys.argv[1], sys.argv[2]
    if cmd == 'unpack':
        root, prefixes = sys.argv[3], tuple(p.replace(chr(92), '/') for p in sys.argv[4:])
        for name in ['assets_x.dat'] + [f'assets_x.dat_{i}' for i in range(1, 9)]:
            p = os.path.join(path, name)
            if os.path.exists(p):
                print(f'{name}: {extract_entries(Archive(p), root, prefixes)} files')
        return
    a = Archive(path)
    if cmd == 'list':
        sys.stdout.reconfigure(errors='replace')
        pat = sys.argv[3] if len(sys.argv) > 3 else ''
        for e in a.entries:
            if pat in e[0]:
                print(f'{e[1]:10d} {e[2]:9d} {e[3]:9d} {e[0]}')
        print(len(a.entries), 'entries')
    elif cmd == 'extract':
        root = sys.argv[3]
        print(f'{extract_entries(a, root)} files -> {root}')


if __name__ == '__main__':
    main()
