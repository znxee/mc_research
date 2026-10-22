"""
mc3_modloader.py - mod overlay for Midnight Club 3 PS2, using the engine's own
                   ZIP fallback

The trick is that the engine already has an override mechanism, it just shipped
switched off. When a loose file fails to open, the resource opener replaces the
last `/` of the path with `.zip` and looks for the basename inside:

    ASSETS/resources/city/atlanta_bnd.pck   missing
    -> ASSETS/resources/city.zip, entry "atlanta_bnd.pck"

It walks local file headers and reads uncompressed-size bytes RAW, so entries
must be STORED - there is no inflate in the game. The whole thing is gated on one
byte at VA 0x618D00 (file offset 0x478D80) that nothing in the game ever writes.
Confirmed working in game.

So the arrangement is the inverse of the obvious one: **vanilla goes into the
zips, mods stay loose on top.** The loose file wins, the zip is only consulted on
failure, so installing a mod is copying a file and uninstalling is deleting it -
vanilla comes back by itself. No hardlinks, no junctions, no composed tree, and
7.9 GB of loose files collapses into a handful of archives.

    python mc3_modloader.py enable   --elf SLUS.ELF        turn the flag on
    python mc3_modloader.py pack     ASSETS/resources/city  vanilla -> city.zip
    python mc3_modloader.py install  mods/meu_predio        copy over the tree
    python mc3_modloader.py remove   mods/meu_predio        delete what it added
    python mc3_modloader.py check    ASSETS/resources/city  validate .pck headers
    python mc3_modloader.py audit-native HOSTFS --source-root PROJECT --out report.json

A mod folder mirrors the asset tree, e.g. mods/meu_predio/resources/city/*.pck.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import zipfile

FLAG_VA = 0x618D00

# The type id a .pck must carry, by how its path looks. A wrong id makes the
# loader return 0 in silence and eleven of the thirteen consumers then spin on a
# `while(1);` left over from a stripped assert - a black screen with no message.
# That is the single failure this tool exists to catch before the game boots.
TIPOS = [
    ('_bnd', 9), ('_fog', 4), ('_traffic', 60), ('_peds', 33),
    ('hudmap', 44), ('/prop/', 64), ('_midnight_', 67),
]


def flag_offset(elf):
    d = open(elf, 'rb').read()
    phoff, = struct.unpack_from('<I', d, 28)
    _t, p_off, p_va, _pa, p_filesz = struct.unpack_from('<5I', d, phoff)
    off = FLAG_VA - p_va + p_off
    if not (p_off <= off < p_off + p_filesz):
        raise SystemExit('%s: 0x%X is outside the loaded segment' % (elf, FLAG_VA))
    return d, off


def enable(elf, out):
    d, off = flag_offset(elf)
    print('%s: flag byte at file 0x%06X = %02X' % (os.path.basename(elf), off, d[off]))
    if d[off] == 1:
        print('  already on')
        return
    b = bytearray(d)
    b[off] = 1
    open(out, 'wb').write(bytes(b))
    print('  wrote %s with the ZIP fallback on (one byte)' % out)


def pck_info(path):
    """(type id, ok, why) for a .pck, or (None, True, '') for anything else."""
    if not path.lower().endswith('.pck'):
        return None, True, ''
    with open(path, 'rb') as f:
        h = f.read(16)
    if len(h) < 16:
        return None, False, 'shorter than a header'
    _base, tipo, ver, size = struct.unpack('<4I', h)
    real = os.path.getsize(path) - 128
    if ver != 1:
        return tipo, False, 'version %d, the loader only accepts 1' % ver
    if size != real:
        return tipo, False, 'body size %d but the file holds %d' % (size, real)
    p = path.replace('\\', '/').lower()
    for marca, esperado in TIPOS:
        if marca in p and tipo != esperado:
            return tipo, False, ('type id %d, but a path like this is loaded as %d'
                                 % (tipo, esperado))
    return tipo, True, ''


def check(raiz):
    mau = tot = 0
    for dirpath, _dirs, files in os.walk(raiz):
        for f in files:
            p = os.path.join(dirpath, f)
            tipo, ok, why = pck_info(p)
            if tipo is None:
                continue
            tot += 1
            if not ok:
                mau += 1
                print('  BAD  %s: %s' % (os.path.relpath(p, raiz), why))
    print('%d .pck checked, %d rejected' % (tot, mau))
    return mau


def pack(pasta, apagar):
    """Move the loose files of ONE directory into `<directory>.zip`.

    Not recursive on purpose: the game derives the archive name from the last
    separator of the path it wanted, so a file in `resources/city/` is only ever
    looked up in `resources/city.zip`. Subdirectories need their own archive.
    """
    pasta = pasta.rstrip('/\\')
    alvo = pasta + '.zip'
    files = [f for f in sorted(os.listdir(pasta))
             if os.path.isfile(os.path.join(pasta, f))]
    if not files:
        raise SystemExit('%s has no files directly in it' % pasta)
    with zipfile.ZipFile(alvo, 'w', zipfile.ZIP_STORED) as z:
        for f in files:
            z.write(os.path.join(pasta, f), f)
    # read it back before touching the originals
    with zipfile.ZipFile(alvo) as z:
        dentro = {i.filename: i for i in z.infolist()}
        for f in files:
            i = dentro.get(f)
            if i is None or i.compress_type != zipfile.ZIP_STORED:
                raise SystemExit('%s did not round-trip as stored - originals kept' % f)
            if i.file_size != os.path.getsize(os.path.join(pasta, f)):
                raise SystemExit('%s changed size - originals kept' % f)
    print('%s: %d files -> %s (%d bytes, stored)'
          % (pasta, len(files), os.path.basename(alvo), os.path.getsize(alvo)))
    if apagar:
        for f in files:
            os.remove(os.path.join(pasta, f))
        print('  removed the loose originals; the game now reads them from the zip')
    else:
        print('  loose originals kept - they still WIN over the zip, so nothing '
              'changes until you pass --apagar')


def pack_tudo(raiz, apagar, minimo):
    """Pack EVERY directory of the tree, one archive each.

    There is no single `assets.zip`: the game derives the archive name from the
    path by replacing its LAST separator with `.zip`, so
    `ASSETS/resources/city/x.pck` is only ever looked for in
    `ASSETS/resources/city.zip`. One global archive would only serve files
    sitting directly under ASSETS. So a tree of 22513 files becomes a few dozen
    archives, not one.

    Directories with fewer than `minimo` files are left loose - an archive that
    holds two files buys nothing and only adds a place for the two to disagree.
    """
    feitas = puladas = 0
    for dirpath, _dirs, files in os.walk(raiz):
        if dirpath == raiz:
            continue                      # ASSETS/<file> would need assets.zip
        reais = [f for f in files if os.path.isfile(os.path.join(dirpath, f))]
        if len(reais) < minimo:
            puladas += 1
            continue
        pack(dirpath, apagar)
        feitas += 1
    print()
    print('%d diretorios empacotados, %d pulados por terem menos de %d arquivos'
          % (feitas, puladas, minimo))


def _pares(mod, raiz):
    for dirpath, _dirs, files in os.walk(mod):
        for f in files:
            src = os.path.join(dirpath, f)
            yield src, os.path.join(raiz, os.path.relpath(src, mod))


def install(mod, raiz, force):
    ruins = [(s, pck_info(s)) for s, _d in _pares(mod, raiz)]
    ruins = [(s, w) for s, (_t, ok, w) in ruins if not ok]
    if ruins and not force:
        for s, w in ruins:
            print('  BAD  %s: %s' % (os.path.relpath(s, mod), w))
        raise SystemExit('refusing to install; a bad header is a silent black '
                         'screen, not an error message. --force to override')
    n = 0
    for src, dst in _pares(mod, raiz):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        n += 1
    print('installed %d files from %s' % (n, mod))
    print('  they are loose, so they win over the zips; removing them restores vanilla')


def remove(mod, raiz):
    n = 0
    for _src, dst in _pares(mod, raiz):
        if os.path.isfile(dst):
            os.remove(dst)
            n += 1
    print('removed %d files; vanilla comes back from the zips' % n)


def audit_native(hostfs, source_roots, out):
    """Read-only source/build provenance for native PS2 modules, not a port claim.

    Roots are project roots containing mods/ and output/mods/. Pass active roots
    first; archived copies are intentionally not searched recursively.
    """
    hostfs = Path(hostfs).resolve()
    roots = [Path(p).resolve() for p in source_roots]
    config = hostfs / 'mc3boot.ini'
    def fingerprint(path):
        data = path.read_bytes()
        return {'path': str(path), 'bytes': len(data),
                'sha256': hashlib.sha256(data).hexdigest()}
    requests, section = [], ''
    for number, raw in enumerate(config.read_text(encoding='utf-8-sig').splitlines(), 1):
        line = raw.lstrip(' \t').rstrip(' \t\r')
        if not line or line[0] in ';#':
            continue
        if line.startswith('['):
            if ']' in line:
                section = line[1:line.index(']')].strip(' \t\r')
            continue
        if section == 'mods' and '=' in line:
            key, value = (s.strip(' \t\r') for s in line.split('=', 1))
            requests.append({'name': key, 'value': value, 'line': number,
                             'enabled': not value.startswith('0')})
    by_name = {}
    for request in requests:
        by_name.setdefault(request['name'], []).append(request)
    names = sorted(set(by_name) | {p.name for p in hostfs.glob('*.mod')})
    modules = []
    for name in names:
        # A module may use a PS2 device prefix; audit only a local basename.
        basename = name.replace('\\', '/').rsplit('/', 1)[-1].rsplit(':', 1)[-1]
        stem = Path(basename).stem
        binary = hostfs / basename
        candidates = []
        for root in roots:
            for base in (root / 'mods', root / 'modloader' / 'mods'):
                for suffix in ('.cpp', '.c'):
                    path = base / stem / (stem + suffix)
                    if path.is_file() and path not in candidates:
                        candidates.append(path)
        sources = [fingerprint(p) for p in candidates]
        builds = []
        binary_info = fingerprint(binary) if binary.is_file() else None
        if binary_info:
            with binary.open('rb') as stream:
                header = stream.read(32)
            if len(header) == 32:
                magic, version, entry, size, relocations, base, hooks, count = struct.unpack('<8I', header)
                binary_info['module_header'] = {
                    'magic_valid': magic == 0x4D43334D, 'version': version,
                    'entry_offset': entry, 'code_bytes': size, 'relocation_count': relocations,
                    'link_base': base, 'hook_table_offset': hooks, 'hook_count': count,
                    'body_and_relocations_present': binary_info['bytes'] >= 32 + size + relocations * 12}
        for root in roots:
            path = root / 'output' / 'mods' / basename
            if path.is_file():
                info = fingerprint(path)
                info['matches_installed'] = bool(binary_info and info['sha256'] == binary_info['sha256'])
                builds.append(info)
        dependencies, unresolved, visited = [], [], set()
        # Only quoted local includes. System/toolchain headers are not copied.
        def visit(path):
            path = path.resolve()
            if path in visited:
                return
            visited.add(path)
            dependencies.append(fingerprint(path))
            text = path.read_text(encoding='utf-8', errors='replace')
            for include in re.findall(r'^\s*#\s*include\s*"([^"]+)"', text, re.M):
                locations = [path.parent / include]
                for root in roots:
                    locations.extend([root / include, root / 'modloader' / include,
                                      root / 'modloader' / 'payload' / include])
                found = next((p for p in locations if p.is_file()), None)
                if found:
                    visit(found)
                else:
                    unresolved.append({'from': str(path), 'include': include})
        if candidates:
            visit(candidates[0])
        lexical = []
        for dep in dependencies:
            text = Path(dep['path']).read_text(encoding='utf-8', errors='replace')
            # Lexical evidence includes comments/macros; it is not a call graph.
            evidence = {token: len(re.findall(pattern, text)) for token, pattern in (
                ('MC3_HOOK', r'\bMC3_HOOK\s*\('),
                ('MC3_CALL', r'\bMC3_CALL\d*\s*\('),
                ('assembly', r'\b(?:__asm__|__asm|asm)\b'),
                ('hex_constants', r'\b0x[0-9a-fA-F]{6,}\b'))}
            lexical.append({'path': dep['path'], **evidence})
        modules.append({'name': name, 'requests': by_name.get(name, []),
                        'installed': binary_info, 'source_candidates': sources,
                        'selected_source': str(candidates[0]) if candidates else None,
                        'local_dependencies': dependencies, 'unresolved_local_includes': unresolved,
                        'build_outputs': builds, 'lexical_evidence': lexical})
    boot_sources = []
    for root in roots:
        path = root / 'modloader' / 'boot' / 'mc3boot.c'
        if path.is_file():
            boot_sources.append(fingerprint(path))
    report = {'format_version': 1, 'hostfs': str(hostfs), 'configuration': fingerprint(config),
              'source_roots_in_priority_order': [str(p) for p in roots],
              'boot_sources': boot_sources, 'modules': modules,
              'summary': {'installed_modules': sum(m['installed'] is not None for m in modules),
                          'configured_entries': len(requests),
                          'enabled_entries': sum(r['enabled'] for r in requests),
                          'modules_with_source': sum(bool(m['selected_source']) for m in modules),
                          'modules_without_source': [m['name'] for m in modules if not m['selected_source']],
                          'unresolved_local_includes': sum(len(m['unresolved_local_includes']) for m in modules)},
              'limitations': ['Source presence and matching build hashes do not prove a reproducible build.',
                              'Lexical evidence is not a resolved dependency or hook graph.',
                              'No assets or module binaries are copied; nothing in HostFS is changed.']}
    destination = Path(out).resolve()
    if destination == hostfs or hostfs in destination.parents or any(
            destination == r or r in destination.parents for r in roots):
        raise SystemExit('audit output must be outside HostFS and source roots')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(report['summary'], ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('acao', choices=('enable', 'pack', 'pack-tudo', 'install',
                                    'remove', 'check', 'audit-native'))
    ap.add_argument('alvo', nargs='?')
    ap.add_argument('--elf', help='the executable, for `enable`')
    ap.add_argument('--out', help='where `enable` writes the patched executable')
    ap.add_argument('--raiz', default=os.path.join(os.environ.get('MC3_HOSTFS', ''), 'ASSETS'),
                    help='the loose ASSETS tree the game reads')
    ap.add_argument('--apagar', action='store_true',
                    help='`pack` deletes the loose originals after verifying the zip')
    ap.add_argument('--minimo', type=int, default=4,
                    help='pack-tudo ignora diretorio com menos arquivos que isso')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--source-root', action='append', default=[],
                    help='audit-native project root, repeat in source priority order')
    a = ap.parse_args()

    if a.acao == 'audit-native':
        if not a.alvo or not a.out or not a.source_root:
            raise SystemExit('audit-native needs HOSTFS, --out JSON and --source-root PROJECT')
        audit_native(a.alvo, a.source_root, a.out)
    elif a.acao == 'enable':
        if not a.elf:
            raise SystemExit('enable needs --elf')
        enable(a.elf, a.out or os.path.splitext(a.elf)[0] + '_ZIP.ELF')
    elif a.acao == 'pack':
        pack(a.alvo, a.apagar)
    elif a.acao == 'pack-tudo':
        pack_tudo(a.alvo or a.raiz, a.apagar, a.minimo)
    elif a.acao == 'check':
        raise SystemExit(1 if check(a.alvo or a.raiz) else 0)
    elif a.acao == 'install':
        install(a.alvo, a.raiz, a.force)
    else:
        remove(a.alvo, a.raiz)


if __name__ == '__main__':
    main()
