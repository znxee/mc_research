"""mc3_shaderprog.py - ler o programa de bytes de um rmcShaderComplex

Cada PASSO de um rmcShaderComplex aponta, no seu +0x00, para uma tirinha de
bytes. Nao e struct: e um fluxo de comandos, e quem o executa e a rotina de
0x002B1F90, chamada por rmcShaderComplex::Bind (0x002B2168) depois de andar a
corrente de passos.

O FORMATO, lido direto do desmonte:

    comando = 1 byte de OPCODE + 1 ou 4 bytes de DADO
        opcode & 0x3F   indice do registrador (0..63)
        opcode & 0xC0   se ZERO o dado tem 1 byte; se nao, tem 4 (little endian)
        opcode == 0xFF  fim do programa

    lbu  t1, 0(t0)          ; opcode
    beq  t1, 255, fim       ; 0xFF termina
    andi v0, t1, 0xC0       ; largura do dado
    andi v0, t1, 0x3F       ; indice
    sll  v0, v0, 2
    addu v0, v0, 0x70000060 ; tabela ATUAL, no scratchpad
    addu v1, v0, 0x700000B8 ; tabela de PADRAO
    sw   a2, 0(v0)          ; grava o valor
                            ; e liga/desliga um bit em 0x7000010C conforme
                            ; o valor difira ou nao do padrao

Testado nos 66 programas alcancaveis da savestate de sd: os 66 decodificam ate
o 0xFF sem sobra nem falta. Nao e leitura plausivel, e o formato.

    python mc3_shaderprog.py --ram estado/eeMemory.bin
    python mc3_shaderprog.py --ram estado/eeMemory.bin --prog 0x0081F260

O QUE DA PARA LER DA TABELA, sem ter achado o consumidor de cada registrador:

    r8 e o BASECOLOR do passo, empacotado AABBGGRR, com o alfa pela METADE:
    alfa_gs = (a + 1) >> 1. Isto nao e mais leitura por analogia - bate campo a
    campo com o texto do .shadert:

        city/water.shadert  passo 0  basecolor 255 255 255 127 -> 40FFFFFF
                            passo 1  basecolor 255 255 255 200 -> 64FFFFFF
                            passo 2  basecolor 255 255 255 200 -> 64FFFFFF
        city/city_specular  passo 0  basecolor 127 127 127   0 -> 007F7F7F

    e quando a fonte NAO tem basecolor vale o padrao 255 255 255 255, que da
    exatamente o 80FFFFFF visto em road_reflector, city_texscroll_doublesided,
    train_ads, train_inside, train_people e ambient_wheel. Onze das dezessete
    formas de passo fecham assim. A mesma divisao por dois aparece no Draw do
    drwShaderCarDecal, achada pela fork de carros por outro caminho.

    As seis que NAO fecham (road_reflector 40FFFFFF, city_specular passo 1,
    city_specular_prop passo 1, train_shadow, black_matte, wheel_inner) sao o
    caso de mesmo nome com revisao diferente: o .shadert em disco nao e a versao
    que compilou aquele objeto.

O resto (r0, r1, r3, r4, r5, r7, r9, r11, r12) fica como numero. r3 quase
sempre vale 0001000A ou 00010044.
"""
import argparse
import collections
import os
import struct

VT_COMPLEX = 0x00626EC8
GLOBAL_MCCITY = 0x00615B40
SHADERLIB = os.path.join(os.environ.get('MC3_HOSTFS', ''), 'ASSETS/shaderlib')


class Ram:
    def __init__(self, caminho):
        self.d = open(caminho, 'rb').read()

    def u32(self, a):
        if not (0 <= a <= len(self.d) - 4):
            return 0
        return struct.unpack_from('<I', self.d, a)[0]

    def u16(self, a):
        if not (0 <= a <= len(self.d) - 2):
            return 0
        return struct.unpack_from('<H', self.d, a)[0]

    def texto(self, a, n=64):
        s = self.d[a:a + n].split(b'\0')[0]
        try:
            return s.decode('latin1')
        except Exception:
            return ''


def decodifica(ram, p, limite=256):
    """[(indice, valor, largo)] ate o 0xFF. None se nao terminar."""
    fora = []
    i = p
    while i < p + limite:
        op = ram.d[i]
        if op == 0xFF:
            return fora
        if op & 0xC0:
            v = (ram.d[i + 1] | (ram.d[i + 2] << 8)
                 | (ram.d[i + 3] << 16) | (ram.d[i + 4] << 24))
            i += 5
        else:
            v = ram.d[i + 1]
            i += 2
        fora.append((op & 0x3F, v, bool(op & 0xC0)))
    return None


def texto_do_programa(regs):
    return ' '.join('r%d=%s' % (i, ('%08X' % v) if largo else ('%02X' % v))
                    for i, v, largo in regs)


def complexos(ram):
    """[(endereco, nome)] de todo rmcShaderComplex com nome de .shadert real.

    O filtro pelo nome NAO e capricho: varrer so pela vtable acha 62 objetos e
    23 deles carregam caminho de corrida ou de musica naquele offset.
    """
    # RECURSIVO de proposito: 32 dos .shadert - e justamente os da CIDADE
    # (city_window, city_road, city_facade, city_specular, moon...) - so existem
    # em shaderlib/city. Listar apenas a raiz descartava em silencio os shaders
    # que mais interessam aqui.
    validos = None
    if os.path.isdir(SHADERLIB):
        validos = set()
        for raiz, _dirs, arqs in os.walk(SHADERLIB):
            validos.update(arqs)
    alvo = struct.pack('<I', VT_COMPLEX)
    fora = []
    i = 0
    while True:
        i = ram.d.find(alvo, i)
        if i < 0 or i > len(ram.d) - 0x40:
            break
        if i % 4 == 0:
            nome = ram.texto(i + 0x30)
            if validos is None or nome in validos:
                fora.append((i, nome))
        i += 4
    return fora


def passos(ram, complexo, limite=32):
    """Enderecos dos passos, andando a corrente do +0x1C."""
    fora = []
    r = complexo + 8
    while r and 0x100000 <= r < len(ram.d) - 0x20 and r not in fora:
        fora.append(r)
        if len(fora) >= limite:
            break
        r = ram.u32(r + 0x1C)
    return fora


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--ram', required=True, help='eeMemory.bin de uma savestate')
    ap.add_argument('--prog', help='decodificar so este endereco de programa (hex)')
    a = ap.parse_args()
    ram = Ram(a.ram)

    if a.prog:
        p = int(a.prog, 16)
        regs = decodifica(ram, p)
        if regs is None:
            raise SystemExit('nao achei o 0xFF em 256 bytes - isto e programa mesmo?')
        print('%08X  %s' % (p, texto_do_programa(regs)))
        return

    achados = complexos(ram)
    print('%d rmcShaderComplex com nome de .shadert real' % len(achados))
    ok = ruim = 0
    unico = collections.OrderedDict()
    for c, nome in achados:
        for k, r in enumerate(passos(ram, c)):
            p = ram.u32(r)
            if not (0x100000 <= p < len(ram.d) - 8):
                continue
            regs = decodifica(ram, p)
            if regs is None:
                ruim += 1
                continue
            ok += 1
            unico.setdefault((nome, k), set()).add(texto_do_programa(regs))
    print('%d programas decodificados ate o 0xFF, %d falharam' % (ok, ruim))
    print()
    for (nome, k), formas in unico.items():
        for t in sorted(formas):
            print('  %-42s passo %d   %s' % (nome, k, t))


if __name__ == '__main__':
    main()
