"""Extract files from Midnight Club II (USA).xiso.iso (XDVDFS) and unpack Dave archives."""
import os
import struct
import sys

ISO_PATH = os.path.join(os.environ.get('MC_RESEARCH_ASSETS', ''), 'Midnight Club II xbox/Midnight Club II (USA).xiso.iso')
OUT_DIR = os.path.join(os.environ.get('RECOMP_DIR', ''), 'research/mc2_xbox')


def list_xdvdfs(f):
    f.seek(0x10000)
    magic = f.read(20)
    if magic != b"MICROSOFT*XBOX*MEDIA":
        raise ValueError(f"Unexpected magic: {magic}")
    root_sec, root_sz = struct.unpack("<II", f.read(8))
    all_entries = []

    def walk_dir(sec, sz, prefix=""):
        f.seek(sec * 2048)
        d = f.read(sz)
        visited = set()
        entries = []

        def parse_node(off):
            if off in visited or off + 14 > len(d):
                return
            visited.add(off)
            lc, rc, esec, esz, attr, nlen = struct.unpack("<HHIIBB", d[off : off + 14])
            if nlen == 0 or off + 14 + nlen > len(d):
                return
            name = d[off + 14 : off + 14 + nlen].decode("latin1")
            entries.append((name, esec, esz, attr))
            if lc != 0 and lc != 0xFFFF:
                parse_node(lc * 4)
            if rc != 0 and rc != 0xFFFF:
                parse_node(rc * 4)

        parse_node(0)
        for name, esec, esz, attr in entries:
            rel = f"{prefix}/{name}" if prefix else name
            is_dir = bool(attr & 0x10)
            all_entries.append((rel, esec, esz, is_dir))
            if is_dir and esz > 0:
                walk_dir(esec, esz, rel)

    walk_dir(root_sec, root_sz)
    return all_entries


def extract_file(f, sec, sz, dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) == sz:
        print(f"  [skip] {dest_path} already exists ({sz} bytes)")
        return
    f.seek(sec * 2048)
    remaining = sz
    chunk_size = 4 * 1024 * 1024
    with open(dest_path, "wb") as out:
        while remaining > 0:
            to_read = min(remaining, chunk_size)
            buf = f.read(to_read)
            if not buf:
                break
            out.write(buf)
            remaining -= len(buf)
    print(f"  [extracted] {dest_path} ({sz} bytes)")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(ISO_PATH, "rb") as f:
        entries = list_xdvdfs(f)
        print(f"Found {len(entries)} entries in XDVDFS:")
        for rel, sec, sz, is_dir in entries:
            kind = "DIR " if is_dir else "FILE"
            f.seek(sec * 2048)
            hdr = f.read(4) if not is_dir and sz >= 4 else b""
            hdr_str = repr(hdr) if hdr else ""
            print(f"  {kind} {rel:45} sec={sec:<8} sz={sz:<12} {hdr_str}")

        # Extract core executable, lists, and Dave archives (skip huge streams_*.dat and dashupdate.xbe unless needed)
        extract_targets = {
            "default.xbe",
            "assets_x.dat",
            "cache_x.dat",
            "ui_asyncx.dat",
            "songs.lst",
            "streams.lst",
        }
        for rel, sec, sz, is_dir in entries:
            if is_dir:
                continue
            if rel in extract_targets or rel.startswith("audio/"):
                dest = os.path.join(OUT_DIR, "disc", rel.replace("/", os.sep))
                extract_file(f, sec, sz, dest)


if __name__ == "__main__":
    main()
