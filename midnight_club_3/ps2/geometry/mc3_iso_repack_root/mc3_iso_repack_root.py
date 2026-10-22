"""Reempacota os arquivos modificados da raiz na cauda de uma ISO9660.

Mantem todos os arquivos/diretorios originais fora do conjunto gerenciado,
remove sobras .MOD antigas e escreve BANKS.DAT, ASSETS.DAT e o pacote do
modloader de forma contigua. Sem --aplicar faz somente o ensaio.
"""
import argparse
import hashlib
import os
import struct

SECTOR = 2048
PVD_LBA = 16
CHUNK = 8 * 1024 * 1024
DVD5_BYTES = 4_700_372_992
DVD5_SECTORS = DVD5_BYTES // SECTOR


def records(data):
    out = []
    pos = 0
    while pos < len(data) and data[pos]:
        size = data[pos]
        if size < 34 or pos + size > len(data):
            raise SystemExit(f'registro ISO invalido em +0x{pos:X}')
        out.append(bytes(data[pos:pos + size]))
        pos += size
    return out


def rec_name(rec):
    raw = rec[33:33 + rec[32]]
    if raw in (b'\0', b'\1'):
        return raw
    return raw.decode('ascii').upper()


def key(rec):
    raw = rec[33:33 + rec[32]]
    return raw.split(b';')[0]


def iso_name(filename):
    stem, ext = os.path.splitext(os.path.basename(filename))
    clean = lambda s: ''.join(c if (c.isalnum() or c == '_') else '_'
                              for c in s.upper())
    return f'{clean(stem)[:8]}.{clean(ext[1:])[:3]};1'


def make_record(name, lba, size):
    raw = name.encode('ascii')
    length = 33 + len(raw)
    if length & 1:
        length += 1
    rec = bytearray(length)
    rec[0] = length
    struct.pack_into('<I', rec, 2, lba)
    struct.pack_into('>I', rec, 6, lba)
    struct.pack_into('<I', rec, 10, size)
    struct.pack_into('>I', rec, 14, size)
    rec[25] = 0
    struct.pack_into('<H', rec, 28, 1)
    struct.pack_into('>H', rec, 30, 1)
    rec[32] = len(raw)
    rec[33:33 + len(raw)] = raw
    return bytes(rec)


def extent(rec):
    return struct.unpack_from('<I', rec, 2)[0], struct.unpack_from('<I', rec, 10)[0]


def sha256_path(path):
    h = hashlib.sha256()
    with open(path, 'rb') as src:
        while True:
            block = src.read(CHUNK)
            if not block:
                return h.hexdigest()
            h.update(block)


def sha256_extent(iso, lba, size):
    h = hashlib.sha256()
    iso.seek(lba * SECTOR)
    left = size
    while left:
        block = iso.read(min(CHUNK, left))
        if not block:
            raise SystemExit('fim inesperado da ISO durante verificacao')
        h.update(block)
        left -= len(block)
    return h.hexdigest()


def managed(name):
    base = name.split(';')[0]
    return (base.endswith('.MOD') or base in {
        'BANKS.DAT', 'ASSETS.DAT', 'MC3BOOT.ELF', 'MC3BOOT.INI',
        'MC3MOD.BIN', 'LEIAME.TXT', 'SLUS_213.55M', 'MC2.DAT', 'MCLA.DAT'
    })


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('iso')
    ap.add_argument('--staging', required=True)
    ap.add_argument('--aplicar', action='store_true')
    ap.add_argument('--first', action='append', default=[],
                    help='write this staged file (8.3 name, e.g. MC2.DAT) before the others')
    ap.add_argument('--expandir', action='store_true',
                    help='amplia o volume ISO ate DVD5 se a nova cauda nao couber')
    ap.add_argument('--sem-limite-dvd', action='store_true',
                    help='aceita camada 0 maior que DVD5 (OPL/PCSX2; '
                         'a imagem deixa de caber num disco gravado)')
    args = ap.parse_args()

    staged = []
    for item in sorted(os.scandir(args.staging), key=lambda e: e.name.upper()):
        if item.is_file():
            staged.append((iso_name(item.name), item.path, item.stat().st_size))
    names = [name for name, _, _ in staged]
    if len(names) != len(set(names)):
        raise SystemExit('nomes 8.3 colidem no staging')
    for required in ('BANKS.DAT;1', 'ASSETS.DAT;1', 'MC3BOOT.ELF;1',
                     'MC3BOOT.INI;1', 'SLUS_213.55M;1', 'SYSTEM.CNF;1'):
        if required not in names:
            raise SystemExit(f'falta {required} no staging')

    files = {name: path for name, path, _ in staged}
    if sha256_path(files['SLUS_213.55M;1']) != sha256_path(files['MC3BOOT.ELF;1']):
        raise SystemExit('SLUS_213.55M deve ser copia identica de MC3BOOT.ELF')
    with open(files['SYSTEM.CNF;1'], 'rb') as system_file:
        if rb'BOOT2 = cdrom0:\SLUS_213.55M;1' not in system_file.read():
            raise SystemExit('SYSTEM.CNF deve iniciar SLUS_213.55M')

    mode = 'r+b' if args.aplicar else 'rb'
    with open(args.iso, mode) as iso:
        iso.seek(PVD_LBA * SECTOR)
        pvd = iso.read(SECTOR)
        if pvd[1:6] != b'CD001':
            raise SystemExit('PVD ISO9660 nao encontrado')
        total = struct.unpack_from('<I', pvd, 80)[0]
        root_lba = struct.unpack_from('<I', pvd, 158)[0]
        root_size = struct.unpack_from('<I', pvd, 166)[0]
        if root_size > SECTOR:
            raise SystemExit('diretorio raiz ocupa mais de um setor')
        iso.seek(root_lba * SECTOR)
        old_root = iso.read(SECTOR)
        old = records(old_root[:root_size])
        old_by_name = {rec_name(r): r for r in old if rec_name(r) not in (b'\0', b'\1')}

        managed_records = [r for r in old
                           if isinstance(rec_name(r), str) and managed(rec_name(r))]
        if not managed_records:
            raise SystemExit('nenhum arquivo gerenciado encontrado na raiz')
        tail_start = min(extent(r)[0] for r in managed_records)

        keep = []
        for rec in old:
            name = rec_name(rec)
            if name in (b'\0', b'\1'):
                keep.append(rec)
            elif name == 'SYSTEM.CNF;1':
                keep.append(rec)
            elif not managed(name):
                lba, size = extent(rec)
                end = lba + (size + SECTOR - 1) // SECTOR
                if end > tail_start:
                    raise SystemExit(f'arquivo preservado {name} ocupa a cauda gerenciada')
                keep.append(rec)

        system = next(x for x in staged if x[0] == 'SYSTEM.CNF;1')
        sys_rec = old_by_name.get('SYSTEM.CNF;1')
        if not sys_rec:
            raise SystemExit('SYSTEM.CNF original nao encontrado')
        sys_lba, sys_old_size = extent(sys_rec)
        if system[2] > ((sys_old_size + SECTOR - 1) // SECTOR) * SECTOR:
            raise SystemExit('SYSTEM.CNF novo nao cabe no extent original')
        keep = [make_record('SYSTEM.CNF;1', sys_lba, system[2])
                if rec_name(r) == 'SYSTEM.CNF;1' else r for r in keep]

        tail_files = [x for x in staged if x[0] != 'SYSTEM.CNF;1']
        first = [f.upper() + ';1' for f in args.first]
        tail_files.sort(key=lambda x: (x[0] not in first, first.index(x[0]) if x[0] in first else 0))
        cursor = tail_start
        layout = []
        for name, path, size in tail_files:
            sectors = (size + SECTOR - 1) // SECTOR
            layout.append((name, path, size, cursor, sectors))
            cursor += sectors
        used_end = max(lba + (size + SECTOR - 1) // SECTOR
                       for rec in old for lba, size in (extent(rec),))
        old_slack = max(0, total - used_end)
        target_total = total
        if cursor > total:
            if not args.expandir:
                raise SystemExit(
                    f'cauda precisa {cursor-total} setores alem do volume; '
                    'repita com --expandir')
            target_total = cursor + old_slack
            if target_total > DVD5_SECTORS and not args.sem_limite_dvd:
                raise SystemExit(
                    f'volume expandido teria {target_total * SECTOR} bytes, '
                    f'acima do limite DVD5 de {DVD5_BYTES}')

        new_records = keep + [make_record(n, lba, size)
                              for n, _, size, lba, _ in layout]
        new_records.sort(key=key)
        root_body = b''.join(new_records)
        if len(root_body) > SECTOR:
            raise SystemExit(f'raiz precisa {len(root_body)} bytes, limite {SECTOR}')

        print(f'ISO: {args.iso}')
        volume_text = (str(total) if target_total == total
                       else f'{total} -> {target_total}')
        print(f'volume: {volume_text} setores; cauda: {tail_start}..{cursor} '
              f'({cursor-tail_start} setores); '
              f'livres no final: {target_total-cursor}')
        print(f'raiz: {len(old)} -> {len(new_records)} registros; '
              f'{len(root_body)}/{SECTOR} bytes')
        for name, _, size, lba, sectors in layout:
            print(f'  {name:<16} LBA {lba:>8}  {size:>10} bytes  {sectors:>7} setores')
        stale = sorted(name for name in old_by_name
                       if managed(name) and name not in names)
        if stale:
            print('removidos da raiz: ' + ', '.join(stale))

        if not args.aplicar:
            print('ENSAIO: nada gravado')
            return

        # Rewrite the compact tail. Sources are outside the ISO, so overlapping
        # old extents are safe. Pad every file to its declared sector boundary.
        if target_total > total:
            iso.truncate(target_total * SECTOR)
        for name, path, size, lba, sectors in layout:
            iso.seek(lba * SECTOR)
            with open(path, 'rb') as src:
                while True:
                    block = src.read(CHUNK)
                    if not block:
                        break
                    iso.write(block)
            pad = sectors * SECTOR - size
            if pad:
                iso.write(bytes(pad))

        iso.seek(sys_lba * SECTOR)
        with open(system[1], 'rb') as src:
            data = src.read()
        iso.write(data)
        iso.write(bytes(((sys_old_size + SECTOR - 1) // SECTOR) * SECTOR - len(data)))

        root_sector = bytearray(SECTOR)
        root_sector[:len(root_body)] = root_body
        # Root directory remains one complete sector. Update . and .. plus PVD.
        struct.pack_into('<I', root_sector, 10, SECTOR)
        struct.pack_into('>I', root_sector, 14, SECTOR)
        dot_len = root_sector[0]
        struct.pack_into('<I', root_sector, dot_len + 10, SECTOR)
        struct.pack_into('>I', root_sector, dot_len + 14, SECTOR)
        iso.seek(root_lba * SECTOR)
        iso.write(root_sector)

        # The PVD's own copy of the root record (offset 156) carries the root
        # size too, and the PS2 reads the directory by it: left at a retail
        # 732 bytes, every entry past that offset vanished for anything that
        # trusts the PVD (found on a clean dump, 2026-10-01).
        iso.seek(PVD_LBA * SECTOR)
        pvd_now = bytearray(iso.read(SECTOR))
        struct.pack_into('<I', pvd_now, 166, SECTOR)
        struct.pack_into('>I', pvd_now, 170, SECTOR)
        iso.seek(PVD_LBA * SECTOR)
        iso.write(pvd_now)

        if target_total != total:
            found_terminator = False
            for vd_lba in range(PVD_LBA, PVD_LBA + 32):
                iso.seek(vd_lba * SECTOR)
                vd = bytearray(iso.read(SECTOR))
                if len(vd) != SECTOR or vd[1:6] != b'CD001':
                    raise SystemExit(
                        f'descritor ISO9660 invalido no LBA {vd_lba}')
                kind = vd[0]
                if kind in (1, 2):
                    struct.pack_into('<I', vd, 80, target_total)
                    struct.pack_into('>I', vd, 84, target_total)
                    iso.seek(vd_lba * SECTOR)
                    iso.write(vd)
                if kind == 255:
                    found_terminator = True
                    break
            if not found_terminator:
                raise SystemExit('terminador de volume ISO9660 nao encontrado')
            iso.truncate(target_total * SECTOR)

        iso.flush()
        os.fsync(iso.fileno())

        # Verify every staged file byte-for-byte from its ISO extent.
        verify = {name: (path, size, lba) for name, path, size, lba, _ in layout}
        verify['SYSTEM.CNF;1'] = (system[1], system[2], sys_lba)
        for name, (path, size, lba) in verify.items():
            expected = sha256_path(path)
            actual = sha256_extent(iso, lba, size)
            if actual != expected:
                raise SystemExit(f'falha de hash apos gravar {name}')
        print(f'GRAVADO E VERIFICADO: {len(verify)} arquivos')


if __name__ == '__main__':
    main()