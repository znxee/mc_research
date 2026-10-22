"""mc3_vtables.py - dar NOME as estruturas do .pck, sem abrir a IDA

O `.pck` nao guarda vtable. Guarda um TOKEN: um numero como 0x0079FF88 que o
carregador troca pela vtable de verdade ao carregar (por isso o tokyo usa os
mesmos tokens deslocados de +0x488 - e uma tabela por build, nao um ponteiro).
Ler o token no arquivo nao diz nada; ler o MESMO campo numa savestate com a
cidade carregada diz tudo.

    arquivo:  ComponentData+0x28 = 0079FF88     <- token
    RAM:      ComponentData+0x28 = 00625098     <- vtable de verdade
    ELF:      vtable+0x08 = 0024C1D0            <- primeiro metodo
    simbolos: 0024C1D0 = mcCityModelType__dtor  <- a classe

E com 10946 enderecos nomeados em `simbolos/` (vindos do MC.MAP da build alpha
de outubro/2004 via mc3_symbols.py), o ultimo passo e uma consulta em tabela.

    python mc3_vtables.py --ram estado/eeMemory.bin
    python mc3_vtables.py --vt 0x625098
    python mc3_vtables.py --vt 0x625098 --tudo

O QUE ISSO JA RESOLVEU, so de rodar a primeira vez:

    MapRoot          parFileIO (+ thunk de mcSkyHatClass::FileIO)
    ComponentData    mcCityModelType
    UniqueComponent  mcCityModel
    Instance         mcInstCityModel
    Mesh             rmcModelGeom
    HoodDesc         rmcTexturePS2   <- o "descritor de hood" e uma TEXTURA

O ultimo derruba uma suposicao minha: eu tinha lido o bloco de 0xB0 apontado por
`hood+0x00` como "descritor de bairro com estado de GS nao decodificado". E um
`rmcTexturePS2` com o nome do bairro. Ou seja cada hood carrega o proprio atlas.
"""
import argparse
import io
import os
import struct

RAIZ = os.path.dirname(os.path.abspath(__file__))
ELF = os.environ.get('MC3_ELF_DIR', '')
BASE, OFF = 0x1A0000, 0x80

# Onde ficam os tokens. (rotulo, como chegar la) - a travessia e a mesma no
# arquivo e na RAM, e e o pareamento por POSICAO que traduz um no outro.
SLOTS = [
    ('MapRoot',          lambda M, U: [M]),
    ('HoodDesc',         lambda M, U: [U(h) for h in _hoods(M, U)]),
    ('UniqueComponent',  lambda M, U: _arr(M, U, 4, 8, 28)),
    ('Instance',         lambda M, U: _arr(M, U, 0x0C, 0x10, 96)),
]


def _hoods(M, U):
    hb = U(M + 0x18)
    return [hb + 20 * i for i in range(U(M + 0x14))]


def _arr(M, U, off_n, off_a, passo, limite=6):
    fora = []
    for h in _hoods(M, U):
        n, a = U(h + off_n), U(h + off_a)
        for k in range(min(n, limite)):
            fora.append(a + passo * k)
    return fora


def carrega_nomes():
    """{endereco: (nome, de onde veio)} - o primeiro arquivo a nomear ganha."""
    nomes = {}
    ordem = ('nomes_manuais.tsv', 'nomes.tsv', 'nomes_token.tsv',
             'nomes_grafo.tsv', 'nomes_vizinhos.tsv')
    for arq in ordem:
        cam = os.path.join(RAIZ, 'simbolos', arq)
        if not os.path.isfile(cam):
            continue
        for ln in io.open(cam, encoding='utf-8', errors='replace'):
            if ln.startswith('#') or not ln.strip():
                continue
            c = ln.rstrip('\n').split('\t')
            if len(c) < 2:
                continue
            try:
                a = int(c[0], 16)
            except ValueError:
                continue
            nomes.setdefault(a, (c[1], arq[6:-4]))
    return nomes


class Elf:
    def __init__(self, caminho=ELF):
        self.d = open(caminho, 'rb').read()

    def u32(self, va):
        o = va - BASE + OFF
        if not (0 <= o <= len(self.d) - 4):
            return None
        return struct.unpack_from('<I', self.d, o)[0]


def metodos(elf, vt, nomes, quantos=14):
    """[(offset, endereco, nome)] de uma vtable."""
    fora = []
    for k in range(quantos):
        v = elf.u32(vt + 4 * k)
        if v is None:
            break
        nome = ''
        if 0x1A0000 <= v < 0x680000:
            got = nomes.get(v)
            nome = '%s [%s]' % got if got else ''
        fora.append((4 * k, v, nome))
    return fora


def classe(elf, vt, nomes):
    """Um palpite de nome de classe: o prefixo comum dos metodos nomeados."""
    vistos = []
    for _o, _v, n in metodos(elf, vt, nomes):
        if not n:
            continue
        base = n.split(' [')[0]
        if '__' in base:
            vistos.append(base.split('__')[0])
    if not vistos:
        return ''
    # o mais frequente que nao seja um thunk
    from collections import Counter
    c = Counter(v for v in vistos if not v.startswith('virtual_function_thunk'))
    return c.most_common(1)[0][0] if c else vistos[0]


def varre(pck, ram, nomes, elf):
    """Pareia token (arquivo) com vtable (RAM) percorrendo os dois igual."""
    import sys
    sys.path.insert(0, os.path.join(RAIZ, 'experimental'))
    from mc2_to_mc3 import Pck
    p = Pck(pck)
    d = open(ram, 'rb').read()

    def Uram(a):
        return struct.unpack_from('<I', d, a)[0]

    def Upck(a):
        o = p.F(a)
        if not (0x80 <= o <= len(p.data) - 4):
            return 0
        return struct.unpack_from('<I', p.data, o)[0]

    def Uram2(a):
        if not (0x100000 <= a <= len(d) - 4):
            return 0
        return struct.unpack_from('<I', d, a)[0]

    M_ram = struct.unpack_from('<I', d, 0x615B40)[0]
    M_pck = p.V(0x80)
    if not (0x100000 <= M_ram < 0x2000000):
        raise SystemExit('a savestate nao tem cidade carregada')

    # campos que carregam token, por estrutura
    campos = {'MapRoot': (0x00,), 'HoodDesc': (0x04,),
              'UniqueComponent': (0x10,), 'Instance': (0x10,),
              'ComponentData': (0x28,), 'Mesh': (0x00,)}
    fora = []
    for rot, achar in SLOTS:
        a_ram = achar(M_ram, Uram)
        a_pck = achar(M_pck, Upck)
        for ar, ap in list(zip(a_ram, a_pck))[:8]:
            if not (0x100000 <= ar < 0x2000000):
                continue
            for c in campos[rot]:
                tok, vt = Upck(ap + c), Uram2(ar + c)
                if tok and vt:
                    fora.append((rot, tok, vt))
            if rot in ('UniqueComponent', 'Instance'):
                cdr, cdp = Uram2(ar + 0x0C), Upck(ap + 0x0C)
                t, v = Upck(cdp + 0x28), Uram2(cdr + 0x28)
                if t and v:
                    fora.append(('ComponentData', t, v))
                mr, mp = Uram2(cdr + 0x3C), Upck(cdp + 0x3C)
                t, v = (Upck(mp), Uram2(mr)) if (mr and mp) else (0, 0)
                if t and v:
                    fora.append(('Mesh', t, v))
    # unico por (rotulo, token)
    visto, saida = set(), []
    for rot, tok, vt in fora:
        k = (rot, tok)
        if k in visto:
            continue
        visto.add(k)
        saida.append((rot, tok, vt, classe(elf, vt, nomes)))
    return saida


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--ram', help='eeMemory.bin de uma savestate COM a cidade carregada')
    ap.add_argument('--pck', default='output/atlanta_backup/atlanta_midnight_clear.pck')
    ap.add_argument('--vt', help='so mostrar os metodos desta vtable (hex)')
    ap.add_argument('--tudo', action='store_true', help='mostrar metodos sem nome tambem')
    ap.add_argument('--elf', default=ELF)
    a = ap.parse_args()

    nomes = carrega_nomes()
    elf = Elf(a.elf)
    print('%d enderecos nomeados em simbolos/' % len(nomes))

    if a.vt:
        vt = int(a.vt, 16)
        print('vtable %08X   classe: %s' % (vt, classe(elf, vt, nomes) or '?'))
        for o, v, n in metodos(elf, vt, nomes, 20):
            if n or a.tudo:
                print('   +%02X %08X  %s' % (o, v, n))
        return

    if not a.ram:
        ap.error('--ram e obrigatorio (ou use --vt)')
    for rot, tok, vt, cls in varre(a.pck, a.ram, nomes, elf):
        print('%-16s token %08X -> vtable %08X   %s' % (rot, tok, vt, cls or '?'))
        for o, v, n in metodos(elf, vt, nomes):
            if n:
                print('      +%02X %s' % (o, n))


if __name__ == '__main__':
    main()
