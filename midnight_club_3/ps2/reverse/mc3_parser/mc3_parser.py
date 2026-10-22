"""mc3_parser.py - arrancar os NOMES dos campos das funcoes FileIO(datParser&)

As classes serializadas da RAGE registram cada campo num `datParser`, e o
registro carrega o nome como string literal. Isso quer dizer que os nomes dos
campos estao no ELF, ao lado do codigo que os liga ao offset - nao e preciso
adivinhar nada.

O padrao compilado e sempre o mesmo:

    jal  0x0055F7C0                 <- datParser::AddField
      a0 = o parser
      a1 = codigo do tipo
      a2 = ponteiro para o nome
      a3 = this + OFFSET DO CAMPO
      t0, t1 = extras

Entao basta seguir `a2` e `a3` de tras pra frente ate o `jal` e a tabela sai
inteira. `mcConditionVariables::FileIO` sozinha registra 41 campos.

    python mc3_parser.py 0x25CC60
    python mc3_parser.py --lista                # todas as FileIO conhecidas
    python mc3_parser.py 0x25CC60 --base 0x40   # somar a base do sub-objeto

O `--base` importa quando a classe e um sub-objeto: `mcConditionVariables` mora
em `mcCity+0x40` (o construtor de mcCity faz `addiu a0, this, 0x40` e chama o
construtor dela), entao um campo em `+0x10` dela e `mcCity+0x50`.
"""
import argparse
import io
import os
import struct

RAIZ = os.path.dirname(os.path.abspath(__file__))
ELF = os.environ.get('MC3_ELF_DIR', '')
BASE, OFF = 0x1A0000, 0x80
ADDFIELD = 0x0055F7C0

# Vistos ate agora. O significado e inferido do tamanho que cada campo ocupa
# entre um offset e o proximo, entao trate como pista e nao como certeza.
TIPOS = {}


class Elf:
    def __init__(self, caminho=ELF):
        self.d = open(caminho, 'rb').read()

    def u32(self, va):
        o = va - BASE + OFF
        if not (0 <= o <= len(self.d) - 4):
            return None
        return struct.unpack_from('<I', self.d, o)[0]

    def texto(self, va):
        o = va - BASE + OFF
        if not (0 <= o < len(self.d)):
            return None
        e = self.d.find(b'\0', o)
        if e < 0 or e - o > 96:
            return None
        s = self.d[o:e]
        if not s or any(c < 32 or c > 126 for c in s):
            return None
        return s.decode('latin1')


def campos(elf, ini, limite=0x800):
    """[(offset, nome, tipo)] registrados por uma FileIO.

    Interpretador de registrador burro de proposito: so `lui`, `addiu`, `ori`,
    `move` e `addu`. Nao segue desvio. Um laco que registra um array aparece
    como UMA entrada, a da primeira volta - e o que se quer, porque o nome e o
    mesmo em todas.
    """
    reg = [None] * 32
    reg[0] = 0
    this = None
    fora = []
    va = ini
    while va < ini + limite:
        w = elf.u32(va)
        if w is None:
            break
        op = w >> 26
        rs, rt, rd = (w >> 21) & 31, (w >> 16) & 31, (w >> 11) & 31
        imm = w & 0xFFFF
        sim = imm - 0x10000 if imm & 0x8000 else imm
        if va == ini:
            reg[4] = 'this'          # a0 = this na entrada
        if op == 0x0F:                                   # lui
            reg[rt] = imm << 16
        elif op == 0x09:                                 # addiu
            b = reg[rs]
            if b == 'this':
                reg[rt] = ('this', sim)
            elif isinstance(b, tuple):
                reg[rt] = (b[0], b[1] + sim)
            elif isinstance(b, int):
                reg[rt] = (b + sim) & 0xFFFFFFFF
            else:
                reg[rt] = None
        elif op == 0x0D:                                 # ori
            b = reg[rs]
            reg[rt] = (b | imm) if isinstance(b, int) else None
        elif op == 0 and (w & 0x3F) in (0x21, 0x2D):     # addu / daddu
            a, b = reg[rs], reg[rt]
            if b == 0 or rt == 0:
                reg[rd] = a
            elif a == 0 or rs == 0:
                reg[rd] = b
            else:
                reg[rd] = None
        elif op == 3:                                    # jal
            alvo = (w & 0x3FFFFFF) << 2
            # o delay slot ainda executa antes da chamada
            w2 = elf.u32(va + 4)
            if w2 is not None:
                o2, s2, t2 = w2 >> 26, (w2 >> 21) & 31, (w2 >> 16) & 31
                if o2 == 0x09:
                    b = reg[s2]
                    i2 = (w2 & 0xFFFF)
                    i2 = i2 - 0x10000 if i2 & 0x8000 else i2
                    if b == 'this':
                        reg[t2] = ('this', i2)
                    elif isinstance(b, tuple):
                        reg[t2] = (b[0], b[1] + i2)
                    elif isinstance(b, int):
                        reg[t2] = (b + i2) & 0xFFFFFFFF
                elif o2 == 0 and (w2 & 0x3F) in (0x21, 0x2D):
                    a, b = reg[s2], reg[(w2 >> 16) & 31]
                    d2 = (w2 >> 11) & 31
                    reg[d2] = a if (b == 0) else (b if a == 0 else None)
            if alvo == ADDFIELD:
                nome = None
                if isinstance(reg[6], int):
                    nome = elf.texto(reg[6])
                alvo_off = None
                if reg[7] == 'this':
                    alvo_off = 0
                elif isinstance(reg[7], tuple) and reg[7][0] == 'this':
                    alvo_off = reg[7][1]
                tipo = reg[5] if isinstance(reg[5], int) else None
                if nome is not None and alvo_off is not None:
                    fora.append((alvo_off, nome, tipo))
            va += 8
            continue
        elif op == 0 and (w & 0x3F) == 8:                # jr $ra
            if rs == 31:
                break
        va += 4
    return fora


CONHECIDAS = [
    (0x0025C7C8, 'mcSkyHatClass::FileIO'),
    (0x0025CC60, 'mcConditionVariables::FileIO'),
    (0x0025CAF0, 'mcStarField::FileIO'),
    (0x0024D8F8, 'mcGlow::FileIO'),
    (0x0024CCE8, 'lightGlowCondition::FileIO'),
    (0x001CDDA0, 'mcFbGlowTuneParams::FileIO'),
    (0x001D35B0, 'mcParticleFogTune::FileIO'),
    (0x001D6650, 'mcSpotlightTuneParams::FileIO'),
    (0x001DC8F0, 'mcSenseOfSpeed::FileIO'),
    (0x001DDBC8, 'mcColorFilter::FileIO'),
    (0x001A4030, 'mcLoadScreenTransition::FileIO'),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('func', nargs='?', help='endereco da FileIO (hex)')
    ap.add_argument('--base', default='0', help='offset do sub-objeto dentro do dono')
    ap.add_argument('--lista', action='store_true')
    ap.add_argument('--elf', default=ELF)
    a = ap.parse_args()
    elf = Elf(a.elf)

    if a.lista or not a.func:
        for va, nome in CONHECIDAS:
            c = campos(elf, va)
            print('%08X  %-34s %d campo(s)' % (va, nome, len(c)))
        return

    base = int(a.base, 16) if a.base.lower().startswith('0x') else int(a.base)
    c = campos(elf, int(a.func, 16))
    print('%d campo(s)%s' % (len(c), ('  (base +0x%X)' % base) if base else ''))
    for off, nome, tipo in c:
        print('  +0x%03X  %-34s tipo %s'
              % (off + base, nome, ('%d' % tipo) if tipo is not None else '?'))


if __name__ == '__main__':
    main()
