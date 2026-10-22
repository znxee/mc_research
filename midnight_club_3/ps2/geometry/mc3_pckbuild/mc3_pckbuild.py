"""mc3_pckbuild.py - build a .pck by letting the GAME do the packetizing

THE IDEA

The retail ELF has no resource writer - `datIsBuildingPageFile` (0x0042D230) is
literally `return 0` and `datRscBuilder::BeginStream` only reads. But it does not
need one: when the game loads a mesh in TEXT it builds the same object graph a
.pck holds, at the same offsets. `rmcModel::Create` parses into a temporary
mshMesh, hands it to `rmcModelGeom::Load`, and throws the mshMesh away; what
survives is the thing the file is an image of.

So the packetizer is the game. This drives it:

    PCSX2 (-elf, -nogui, -unlimited)  +  mesh_dump.mod
        |  the mod unloads the frontend, carves a PRIVATE heap with
        |  mcHeap::CreateMemTopHeap, pushes it, and calls rmcModel::Create
        v
    PINE (127.0.0.1:28011)            <- poll the report, trigger a savestate
        v
    <serial> (<crc>).<slot>.p2s       <- EE RAM, read with mc3_inject
        v
    .mesh.pck                          <- cut the heap range out and add 128 bytes

WHY THE PRIVATE HEAP MAKES THE LAST STEP FREE

`datRscBuilder::LoadBuild` reads a 128-byte header - [baseVA][type][version=1]
[body size] - allocates the body 128-aligned and hands `mcModelFactory::Create`
a datResource whose delta is `buffer - baseVA`. Every ctor then adds that delta
to its pointers.

The dump is a byte image of a contiguous heap starting at a known address. Set
`baseVA` to that address and the delta cancels exactly: a pointer stored as
`base + k` resolves to `buffer + k`. There is NO relocation pass to write. The
whole builder is a header plus a memcpy - which is the point of having the mod
allocate into a heap of its own instead of the general one.

USAGE

    python mc3_pckbuild.py drive                      # run the emulator end to end
    python mc3_pckbuild.py build savestate.p2s        # from a state you already have
    python mc3_pckbuild.py report savestate.p2s       # just show what the mod said

`drive` needs PINE enabled in PCSX2 (EnablePINE=true, PINESlot=28011 - both are
already set in this install) and mesh_dump.mod=1 in the HostFS mc3boot.ini.
"""
import argparse
import os
import socket
import struct
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'modloader'))
import mc3_inject
import mc3_saida

PCSX2 = os.path.join(os.environ.get('MC3_PCSX2_DIR', ''), 'pcsx2-qt.exe')
PCSX2_DATA = os.environ.get('MC3_PCSX2_DATA', '')
# mc3boot.elf, not the game ELF. It is the modloader's own booter: it reboots
# the PS2, reads mc3boot.ini and loads the .mod files itself, which is why its
# profile (CRC B3FD5361) has EnableCheats = false - the pnach route is not used.
# Booting slus_213.55.ELF directly instead loops forever on netcnf/eznetcnf/dev9
# ("unknown dev9 hardware") and never reaches the frontend.
ELF = os.path.join(os.environ.get('MC3_HOSTFS', ''), 'mc3boot.elf')
ISO = os.path.join(os.environ.get('MC3_HOSTFS', ''), 'MC3Stripped.iso')
PINE_HOST, PINE_PORT = '127.0.0.1', 28011

# mesh_dump.mod's report. Keep in sync with mods/mesh_dump/mesh_dump.cpp.
DUMP_ADDR = 0x0061CF00
# Two modules write this window and they number their states differently:
# mesh_dump unloads the frontend (2 = no heap, 4 = done), pck_tool keeps it and
# draws on screen (2 = converting, 3 = done, 4 = no heap). Reading one with the
# other's table would abort mid-conversion, so read_report normalises to a name.
DUMP_MAGIC = 0x4D433348          # 'MC3H', mesh_dump.mod
TOOL_MAGIC = 0x4D433354          # 'MC3T', pck_tool.mod
ESTADOS = {
    DUMP_MAGIC: {0: 'wait', 1: 'ready', 2: 'no_heap', 3: 'dumping',
                 4: 'done', 5: 'parked'},
    TOOL_MAGIC: {0: 'wait', 1: 'ready', 2: 'converting', 3: 'done',
                 4: 'no_heap'},
}
MODEL_STRIDE = 20
MODEL_BASE = 40

PCK_TYPE_MESH = 22               # what mcModelFactory::Create asks LoadBuild for


# ---------------------------------------------------------------------------
#  PINE
# ---------------------------------------------------------------------------

class PineNotReady(Exception):
    """The request was refused but the socket is still good - retry on it."""


class Pine(object):
    """The bit of PCSX2's IPC this needs: read a few words, and save a state.

    Requests are [u32 total length][u8 opcode][payload]; replies are
    [u32 total length][u8 result][payload], result 0 = OK. Reading the whole
    heap through this would be a million round trips, so the bulk capture goes
    through a savestate instead and PINE is used only to steer.
    """

    # Opcode numbers read out of pcsx2/PINE.cpp, not guessed: MsgRead32 = 2 and
    # MsgSaveState = 9. The 0x42 that used to sit here is from a different
    # PINE generation and this build answers it with IPC_FAIL.
    READ32 = 0x02
    SAVESTATE = 0x09

    def __init__(self, host=PINE_HOST, port=PINE_PORT, timeout=5.0):
        self.s = socket.create_connection((host, port), timeout=timeout)
        self.s.settimeout(timeout)

    def close(self):
        try:
            self.s.close()
        except OSError:
            pass

    def _call(self, body, reply_extra):
        self.s.sendall(struct.pack('<I', 4 + len(body)) + body)
        head = self._recv(4)
        total = struct.unpack('<I', head)[0]
        rest = self._recv(total - 4)
        if not rest or rest[0] != 0:
            # 0xFF is IPC_FAIL, and by far its commonest cause is
            # `!VMManager::HasValidVM()` - the VM has not started yet. The
            # CONNECTION is fine, so this must not tear it down: PINE's
            # MainLoop serves ONE client at a time (accept, ClientLoop, close),
            # so a client that drops a live socket and opens another leaves the
            # server blocked reading the first one, and every later connection
            # sits unaccepted in the backlog until it times out. That is
            # exactly what used to happen here.
            raise PineNotReady('PINE said IPC_FAIL (result %s)'
                               % (rest[0] if rest else 'none'))
        return rest[1:1 + reply_extra]

    def _recv(self, n):
        out = b''
        while len(out) < n:
            chunk = self.s.recv(n - len(out))
            if not chunk:
                raise IOError('PINE closed the connection')
            out += chunk
        return out

    def read32(self, addr):
        return struct.unpack('<I', self._call(
            struct.pack('<BI', self.READ32, addr), 4))[0]

    def savestate(self, slot):
        # MsgSaveState takes ONE byte, the slot. It is queued with
        # Host::RunOnCPUThread, so the reply comes back before the file exists.
        self._call(struct.pack('<BB', self.SAVESTATE, slot & 0xFF), 0)

    def status(self):
        return struct.unpack('<I', self._call(
            struct.pack('<B', self.STATUS), 4))[0]


# ---------------------------------------------------------------------------
#  the report
# ---------------------------------------------------------------------------

def read_report(dw):
    """The report of whichever module owns the window, by u32 reader."""
    magia = dw(DUMP_ADDR)
    if magia not in ESTADOS:
        return None
    r = {
        'magic': magia,
        'quem': 'pck_tool' if magia == TOOL_MAGIC else 'mesh_dump',
        'ticks': dw(DUMP_ADDR + 4),
        'state': dw(DUMP_ADDR + 8),
        'fase': ESTADOS[magia].get(dw(DUMP_ADDR + 8), '?'),
        'free_before': dw(DUMP_ADDR + 12),
        'free_after': dw(DUMP_ADDR + 16),
        'heap': dw(DUMP_ADDR + 20),
        'heap_base': dw(DUMP_ADDR + 24),
        'heap_len': dw(DUMP_ADDR + 28),
        'count': dw(DUMP_ADDR + 32),
        'running': dw(DUMP_ADDR + 36),
        'models': [],
    }
    for i in range(r['count']):
        e = DUMP_ADDR + MODEL_BASE + MODEL_STRIDE * i
        r['models'].append({'name': dw(e), 'obj': dw(e + 4),
                            'groups': dw(e + 8), 'matidx': dw(e + 12),
                            'geom': dw(e + 16)})
    return r


def dw_from_ram(ee):
    def dw(addr):
        o = addr & 0x01FFFFFF
        return struct.unpack_from('<I', ee, o)[0] if o + 4 <= len(ee) else 0
    return dw


def cstr(ee, addr, limit=96):
    o = addr & 0x01FFFFFF
    if o <= 0 or o >= len(ee):
        return ''
    e = ee.find(b'\0', o, o + limit)
    return ee[o:e if e > 0 else o].decode('latin1', 'replace')


# ---------------------------------------------------------------------------
#  the heap walk
# ---------------------------------------------------------------------------

def heap_high_water(ee, base, total):
    """Where the last live allocation ends, walked the way GetMemUsed walks it.

    memMemoryAllocator lays blocks out as [16-byte header][payload], the header
    holding a free flag in the low bit of the first byte and the payload size at
    +4 (that is `*(u32*)(p-12)` from the payload pointer GetMemUsed uses). A
    fresh memtop heap has no fragmentation to speak of, so walking it is exact.

    Falls back to trimming trailing zeros if the chain does not look sane -
    better a slightly long body than a wrong one, since the loader only reads
    what the pointers reach.
    """
    o = base & 0x01FFFFFF
    end = min(len(ee), o + total)
    p, last = o, o
    steps = 0
    while p + 16 <= end and steps < 1 << 20:
        size = struct.unpack_from('<I', ee, p + 4)[0]
        free = ee[p] & 1
        if size == 0 or size > total:
            break
        nxt = p + 16 + ((size + 15) & ~15)
        if nxt <= p or nxt > end:
            break
        if not free:
            last = nxt
        p = nxt
        steps += 1
    if steps == 0:
        blob = ee[o:end].rstrip(b'\0')
        return o + len(blob)
    return last


# ---------------------------------------------------------------------------
#  writing the .pck
# ---------------------------------------------------------------------------

def write_pck(ee, base_va, end_va, path, kind=PCK_TYPE_MESH):
    """Header plus a raw copy - see the module docstring for why that is all.

    `base_va` goes in word 0 so the loader's `buffer - baseVA` delta cancels
    against the addresses already stored in the graph.
    """
    o, e = base_va & 0x01FFFFFF, end_va & 0x01FFFFFF
    body = ee[o:e]
    if len(body) % 16:
        body += b'\0' * (16 - len(body) % 16)
    head = struct.pack('<IIII', base_va, kind, 1, len(body)) + b'\0' * 112
    with open(path, 'wb') as f:
        f.write(head + body)
    return len(head) + len(body)


def build_from_ram(ee, out, kind=PCK_TYPE_MESH):
    r = read_report(dw_from_ram(ee))
    if r is None:
        print('nao ha relatorio MC3H/MC3T nesse estado - o modulo nao rodou, ou '
              'outro modulo ficou com a janela (rode com city_slot6 e mc2_probe '
              'em 0 e leia o anel de log)')
        return 1
    show_report(r, ee)
    if r['fase'] != 'done' or not r['count']:
        print('  nada para construir: o modulo nao chegou ao fim')
        return 1

    if not os.path.isdir(out):
        os.makedirs(out)
    hw = heap_high_water(ee, r['heap_base'], r['heap_len'])
    print()
    print('  heap %08X + %d, ultimo bloco vivo termina em %08X (%d bytes usados)'
          % (r['heap_base'], r['heap_len'], hw | 0x00000000, hw - (r['heap_base'] & 0x01FFFFFF)))

    # Each model's graph starts at its own object and runs to the high water:
    # Load allocates the material table, the geometry array and the packets
    # AFTER the rmcModelGeom, so nothing it points at lies below it.
    feitos = 0
    for i, m in enumerate(r['models']):
        if not m['obj']:
            print('  [%d] %s -> NAO CARREGOU' % (i, cstr(ee, m['name']) or '?'))
            continue
        nome = cstr(ee, m['name']) or ('model%d' % i)
        arq = os.path.basename(nome).replace('.mod', '').replace('.mesh', '')
        arq = ''.join(c if c.isalnum() or c in '._-#' else '_' for c in arq)
        p = os.path.join(out, arq + '.mesh.pck')
        n = write_pck(ee, m['obj'], hw | (r['heap_base'] & ~0x01FFFFFF), p, kind)
        print('  [%d] %-34s -> %s  (%d bytes, %d grupos)'
              % (i, nome, os.path.basename(p), n, m['groups']))
        feitos += 1
    if feitos > 1:
        print()
        print('  AVISO: %d modelos num heap so. Cada .pck comeca no proprio objeto'
              ' e vai ate o fim do heap, entao os primeiros carregam a cauda dos'
              ' seguintes como peso morto. Para arquivo limpo, um modelo por'
              ' execucao.' % feitos)
    return 0


def show_report(r, ee=None):
    LEGIVEL = {'wait': 'aquecendo', 'ready': 'pronto',
               'converting': 'convertendo', 'dumping': 'construindo',
               'done': 'pronto/fim', 'no_heap': 'SEM HEAP',
               'parked': 'estacionado'}
    print('relatorio %s:' % r['quem'])
    print('  estado            = %s   (%d quadros)'
          % (LEGIVEL.get(r['fase'], '?%d' % r['state']), r['ticks']))
    if r['quem'] == 'pck_tool':
        # keeps the frontend on purpose, so free_after is never written
        print('  heap principal    = %d livre antes de pedir' % r['free_before'])
        print('  quadros desenhados= %d   %s'
              % (r['free_after'],
                 'o redirect de vtable pegou' if r['free_after']
                 else 'NAO DESENHOU - o DoRendering nao foi chamado'))
    else:
        print('  heap principal    = %d livre antes, %d depois'
              % (r['free_before'], r['free_after']))
        if r['free_after'] > r['free_before']:
            print('                      o frontend devolveu %d bytes (%.2f MB)'
                  % (r['free_after'] - r['free_before'],
                     (r['free_after'] - r['free_before']) / 1048576.0))
        elif r['state'] >= 1:
            print('                      SEM MUDANCA - o frontend nao era quem segurava')
    if r['fase'] == 'no_heap':
        print('  -> CreateMemTopHeap recusou. Peca menos que o livre acima em '
              'HEAP_BYTES, ou descarregue mais que a camada 8.')
    if r['running']:
        print('  -> TRAVOU construindo o modelo %d' % r['running'])


# ---------------------------------------------------------------------------
#  driving the emulator
# ---------------------------------------------------------------------------

def newest_state(slot):
    d = os.path.join(PCSX2_DATA, 'sstates')
    if not os.path.isdir(d):
        return None
    fim = '.%02d.p2s' % slot
    cand = [os.path.join(d, x) for x in os.listdir(d) if x.endswith(fim)]
    return max(cand, key=os.path.getmtime) if cand else None


def drive(a):
    if not os.path.isfile(PCSX2):
        print('PCSX2 nao esta em %s' % PCSX2)
        return 1
    alvo = a.elf or ELF
    antes = newest_state(a.slot)
    antes_t = os.path.getmtime(antes) if antes else 0

    cmd = [PCSX2, '-elf', alvo, '-fastboot']
    if not a.janela:
        cmd.append('-nogui')
    if a.turbo:
        cmd.append('-unlimited')
    # The positional argument is the DISC, not the ELF again: the game reads its
    # assets off the DVD and `-elf` only chooses what to execute.
    if os.path.isfile(ISO):
        cmd.append(ISO)
    print('$ %s' % ' '.join('"%s"' % c if ' ' in c else c for c in cmd))
    proc = subprocess.Popen(cmd)

    pine, r, falhas = None, None, 0
    limite = time.time() + a.timeout
    try:
        while time.time() < limite:
            time.sleep(2.0)
            if proc.poll() is not None:
                print('o emulador saiu antes da hora (codigo %s)' % proc.returncode)
                return 1
            if pine is None:
                try:
                    pine = Pine()
                    print('PINE conectado')
                except OSError:
                    continue
            try:
                r = read_report(pine.read32)
            except PineNotReady:
                # Not up yet. Keep the socket - see PineNotReady.
                r = None
                continue
            except (IOError, OSError) as e:
                falhas += 1
                if falhas in (1, 5, 20):
                    print('PINE: %s - tentativa %d' % (e, falhas))
                try:
                    pine.close()
                except Exception:
                    pass
                pine = None
                continue
            if r is None:
                continue
            if r['fase'] == 'done':
                print('o modulo terminou; salvando estado no slot %d' % a.slot)
                pine.savestate(a.slot)
                time.sleep(3.0)
                break
            if r['fase'] == 'no_heap':
                show_report(r)
                return 1
        else:
            print('estourou o tempo (%ds) sem o modulo terminar' % a.timeout)
            if r:
                show_report(r)
            return 1
    finally:
        if pine:
            pine.close()
        if proc.poll() is None:
            proc.terminate()

    novo = newest_state(a.slot)
    if not novo or os.path.getmtime(novo) <= antes_t:
        print('o savestate nao apareceu em %s/sstates' % PCSX2_DATA)
        return 1
    print('estado: %s' % novo)
    return build_from_ram(mc3_inject.ee_from_savestate(novo), saida(a), a.tipo)


def saida(a):
    return a.out or os.path.join(mc3_saida.pasta(), 'pck_do_jogo')


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd')

    d = sub.add_parser('drive', help='roda o emulador e constroi')
    d.add_argument('--elf', help='ELF a bootar (padrao: o do HostFS)')
    d.add_argument('--slot', type=int, default=9)
    d.add_argument('--timeout', type=int, default=300)
    d.add_argument('--janela', action='store_true', help='nao usar -nogui')
    d.add_argument('--turbo', action='store_true', default=True)
    d.add_argument('--tipo', type=lambda x: int(x, 0), default=PCK_TYPE_MESH)
    d.add_argument('--out')

    b = sub.add_parser('build', help='constroi a partir de um savestate')
    b.add_argument('estado')
    b.add_argument('--tipo', type=lambda x: int(x, 0), default=PCK_TYPE_MESH)
    b.add_argument('--out')

    s = sub.add_parser('report', help='so mostra o relatorio do savestate')
    s.add_argument('estado')

    a = ap.parse_args()
    if a.cmd == 'drive':
        return drive(a)
    if a.cmd == 'build':
        return build_from_ram(mc3_inject.ee_from_savestate(a.estado), saida(a), a.tipo)
    if a.cmd == 'report':
        ee = mc3_inject.ee_from_savestate(a.estado)
        r = read_report(dw_from_ram(ee))
        if r is None:
            print('sem relatorio MC3H nesse estado')
            return 1
        show_report(r, ee)
        for i, m in enumerate(r['models']):
            print('  [%d] obj %08X groups %-3d matidx %08X geom %08X  %s'
                  % (i, m['obj'], m['groups'], m['matidx'], m['geom'],
                     cstr(ee, m['name'])))
        return 0
    ap.print_help()
    return 1


if __name__ == '__main__':
    sys.exit(main())
