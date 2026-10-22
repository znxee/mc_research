"""mc3_campos.py - que offsets de uma estrutura o jogo REALMENTE toca

Quando um campo esta zerado no arquivo e zerado na RAM, a pergunta util nao e
"o que ele guarda" e sim "alguem chega nele". Este script responde isso por
varredura, e a resposta tem valor: um offset que ninguem toca e um BURACO, nao
um campo desconhecido - e da para parar de procurar.

Como funciona: acha toda leitura do ponteiro global da estrutura
(`lw rt, 0x5b40(rs)` para o mcCity), segue o registrador ate o fim da funcao ou
ate ele ser redefinido, e anota todo acesso `imm(rt)`. Sai um mapa de offset ->
(modos de acesso, quantos lugares).

    python mc3_campos.py                 # o mapa inteiro do mcCity
    python mc3_campos.py 0x1C8           # so um offset
    python mc3_campos.py --ctor 0x259160 # o que o construtor toca via `this`

DUAS LIMITACOES QUE IMPORTAM, e nao ha como contornar por varredura:

1. So pega acesso pelo GLOBAL. Metodo que recebe `this` por argumento nao
   aparece - foi assim que mcCity::InitGlobalLighting escapou, e e por isso que
   +0x1A4, +0x1B0 e +0x1BC saem como "ninguem toca" mesmo sendo a iluminacao
   global. Use junto com --ctor e com uma varredura do modulo.
2. Procurar o offset solto no ELF inteiro da falso positivo a rodo: 0x1C8 sozinho
   aparece 45 vezes em estruturas de outros modulos. Confirme sempre que a base
   e o global ou que a funcao esta na faixa do modulo certo.

Confirmar que ninguem toca exige as tres varreduras: global, construtor e
modulo. So entao vale dizer "buraco".
"""
import os
import argparse
import collections
import struct

ELF = os.environ.get('MC3_ELF_DIR', '')
BASE, OFF, SZ = 0x1A0000, 0x80, 0x004D7074
GLOBAL_MCCITY = 0x5B40          # o imm de `lw rt, 0x5b40(rs)`
MODULO_CIDADE = (0x244000, 0x262000)

OPS = {0x20: 'lb', 0x21: 'lh', 0x23: 'lw', 0x24: 'lbu', 0x25: 'lhu',
       0x28: 'sb', 0x29: 'sh', 0x2B: 'sw', 0x31: 'lwc1', 0x39: 'swc1',
       0x37: 'ld', 0x3F: 'sd'}
ESCRITA = {'sb', 'sh', 'sw', 'swc1', 'sd'}


def _redefine(w, r):
    """O registrador `r` foi reescrito por esta instrucao?"""
    op = w >> 26
    if op in (0x09, 0x0D, 0x0F, 0x23, 0x24, 0x25, 0x20, 0x21, 0x37):
        return ((w >> 16) & 31) == r
    if op == 0 and (w & 0x3F) in (0x21, 0x2D, 0x20, 0x25, 0x2A, 0x2B, 0x24):
        return ((w >> 11) & 31) == r
    return False


def mapa(F, imm_global=GLOBAL_MCCITY, teto=0x2300):
    acc = collections.defaultdict(lambda: [set(), set()])
    for off in range(OFF, OFF + SZ - 4, 4):
        w = struct.unpack_from('<I', F, off)[0]
        if (w >> 26) != 0x23 or (w & 0xFFFF) != imm_global:
            continue
        rt = (w >> 16) & 31
        o = off + 4
        while o < OFF + SZ - 4 and o - off < 0x1800:
            w2 = struct.unpack_from('<I', F, o)[0]
            op = w2 >> 26
            if op == 0 and (w2 & 0x3F) == 8 and ((w2 >> 21) & 31) == 31:
                break                                   # jr $ra
            if op in OPS and ((w2 >> 21) & 31) == rt:
                i = w2 & 0xFFFF
                if i < teto:
                    acc[i][0].add(OPS[op])
                    acc[i][1].add(off - OFF + BASE)
            if _redefine(w2, rt):
                break
            o += 4
    return acc


def por_this(F, ini, fim, reg):
    """Offsets que uma funcao toca via um registrador fixo (o `this`)."""
    acc = collections.defaultdict(set)
    for va in range(ini, fim, 4):
        w = struct.unpack_from('<I', F, va - BASE + OFF)[0]
        op = w >> 26
        if op in OPS and ((w >> 21) & 31) == reg:
            acc[w & 0xFFFF].add(OPS[op])
    return acc


def no_modulo(F, imm, faixa=MODULO_CIDADE):
    """Acessos a um offset dentro de uma faixa de codigo, base != $sp."""
    fora = []
    for va in range(faixa[0], faixa[1], 4):
        w = struct.unpack_from('<I', F, va - BASE + OFF)[0]
        op = w >> 26
        if op in OPS and (w & 0xFFFF) == imm and ((w >> 21) & 31) != 29:
            fora.append((va, OPS[op], (w >> 21) & 31))
    return fora


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('offset', nargs='?', help='so este offset (hex)')
    ap.add_argument('--ctor', help='endereco de um construtor, para ver o que ele toca via this')
    ap.add_argument('--reg', type=int, default=17, help='registrador do this no construtor (padrao s1=17)')
    ap.add_argument('--elf', default=ELF)
    a = ap.parse_args()
    F = open(a.elf, 'rb').read()

    if a.ctor:
        ini = int(a.ctor, 16)
        acc = por_this(F, ini, ini + 0x400, a.reg)
        print('offsets tocados via $r%d a partir de %08X:' % (a.reg, ini))
        for k in sorted(acc):
            print('   +0x%03X  %s' % (k, ','.join(sorted(acc[k]))))
        return

    acc = mapa(F)
    if a.offset:
        alvo = int(a.offset, 16)
        if alvo in acc:
            m, f = acc[alvo]
            print('+0x%03X pelo global: %s, em %d local(is): %s'
                  % (alvo, ','.join(sorted(m)), len(f),
                     [hex(x) for x in sorted(f)][:8]))
        else:
            print('+0x%03X: ninguem toca PELO GLOBAL' % alvo)
        n = no_modulo(F, alvo)
        print('+0x%03X no modulo da cidade (%06X..%06X): %d acesso(s)'
              % (alvo, MODULO_CIDADE[0], MODULO_CIDADE[1], len(n)))
        for va, mn, rs in n[:8]:
            print('   %s $r? , 0x%X($r%d) @ %08X' % (mn, alvo, rs, va))
        return

    print('%d offsets distintos tocados pelo global' % len(acc))
    for k in sorted(acc):
        m, f = acc[k]
        print('   +0x%03X  %-16s %2d local(is)  %s'
              % (k, ','.join(sorted(m)), len(f), 'ESCRITA' if m & ESCRITA else ''))


if __name__ == '__main__':
    main()
