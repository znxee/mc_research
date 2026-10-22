"""mc3_obrigatorio.py - que campo do .pck de cidade NUNCA vem nulo no varejo

A pergunta pratica na hora de gerar uma cidade do zero nao e "o que esse campo
significa", e sim "posso deixar zero?". Este script responde pela evidencia:
percorre as cidades de varejo, conta cada campo de ponteiro que conhece e diz
em quantas vezes ele veio nulo.

    python mc3_obrigatorio.py <cidade.pck> [outra.pck ...]

COMO LER O RESULTADO, com cuidado:

  * campo com 0 nulos em milhares de objetos, nas quatro cidades, e um campo
    que o VAREJO sempre preenche. E a melhor evidencia disponivel de que o
    codigo o deref sem checar - mas e evidencia, nao prova: so a leitura do ELF
    prova que nao ha um teste antes.
  * campo com nulos e um campo que o jogo TOLERA vazio, e ai a prova e direta:
    o retail carrega esses arquivos. Exemplo ja conhecido: `lod[0]` do
    ComponentData vem nulo em 128 dos 651 componentes do atlanta, entao o
    caminho de desenho testa antes de seguir.

Para quem gera cidade: tratar a coluna "sempre preenchido" como obrigacao e a
coluna "tolera nulo" como liberdade. Um arquivo de poucos KB com quase tudo
zerado viola dezenas dessas obrigacoes de uma vez, e nao ha como saber qual
delas derrubou primeiro - por isso substituir dentro de uma cidade existente
funcionava e montar do zero nao.
"""
import argparse
import collections
import struct
import sys

BASE = 0x06800000
HDR = 0x80


class Pck:
    def __init__(self, caminho):
        self.d = open(caminho, 'rb').read()
        self.n = len(self.d)

    def u32(self, o):
        return struct.unpack_from('<I', self.d, o)[0] if 0 <= o <= self.n - 4 else None

    def u16(self, o):
        return struct.unpack_from('<H', self.d, o)[0] if 0 <= o <= self.n - 2 else None

    def off(self, va):
        if not va or not (BASE <= va < BASE + 0x01000000):
            return None
        o = va - BASE + HDR
        return o if 0 <= o < self.n else None


def censo(p, c):
    """c[(estrutura, campo)] = [total, nulos, fora_do_arquivo]"""
    u32, u16, off = p.u32, p.u16, p.off

    def conta(estrutura, campo, valor):
        r = c.setdefault((estrutura, campo), [0, 0, 0])
        r[0] += 1
        if not valor:
            r[1] += 1
        elif off(valor) is None:
            r[2] += 1

    R = HDR
    for campo, o in (('shader_group_va', 0x0C), ('sky_shader_group', 0x10),
                     ('hood_array_va', 0x18), ('cell_index_va', 0x1C),
                     ('palette_live', 0x2C), ('palette_source', 0x30),
                     ('sky_class', 0x190), ('city_model_class', 0x194),
                     ('inst_city_model_class', 0x198), ('camera_matrix', 0x19C),
                     ('env_map', 0x1D0), ('texture', 0x1D4),
                     ('texture_proxy', 0x228)):
        conta('MapRoot', campo, u32(R + o))
    for k in range(20):
        conta('MapRoot', 'textures[k]', u32(R + 0x1D8 + 4 * k))

    ci = off(u32(R + 0x1C))
    cell_count = u32(R + 0x268)
    if ci is not None:
        for campo, o in (('unique_array', 0x08), ('instance_array', 0x0C),
                         ('cells', 0x10), ('extra', 0x14)):
            conta('CellIndex', campo, u32(ci + o))
        cells = off(u32(ci + 0x10))
        extra = off(u32(ci + 0x14))
        if cells is not None and cell_count and cell_count < 0x100000:
            for i in range(cell_count):
                e = cells + 0x0C * i
                conta('CellRecord', 'unique_list', u32(e + 4))
                conta('CellRecord', 'instance_list', u32(e + 8))
        if extra is not None and cell_count and cell_count < 0x100000:
            for i in range(cell_count):
                conta('CellIndex+0x14', 'ponteiro por celula', u32(extra + 4 * i))

    vistas = set()

    def textura(o):
        if o is None or o in vistas:
            return
        vistas.add(o)
        conta('TexturePS2', 'nome', u32(o + 0x78))
        for k in range(4):
            conta('TexturePS2', 'nivel[k].dados', u32(o + 0x48 + 12 * k))

    def malha(o):
        if o is None or o in vistas:
            return
        vistas.add(o)
        conta('rmcModelGeom', '+0x0C material_table', u32(o + 0x0C))
        conta('rmcModelGeom', '+0x10 group_table', u32(o + 0x10))
        conta('rmcModelGeom', '+0x14 per_block', u32(o + 0x14))
        conta('rmcModelGeom', '+0x18', u32(o + 0x18))
        conta('rmcModelGeom', '+0x1C', u32(o + 0x1C))
        gc = u16(o + 8)
        gt = off(u32(o + 0x10))
        if gt is None or not gc or gc > 4096:
            return
        for g in range(gc):
            e = gt + 8 * g
            conta('GroupEntry', 'list', u32(e))
            lst, nb = off(u32(e)), u16(e + 4)
            if lst is None or not nb or nb > 4096:
                continue
            for k in range(nb):
                conta('BlockEntry', 'packet', u32(lst + 8 * k))
        pb = off(u32(o + 0x14))
        sc = u16(o + 0x0A)
        if pb is not None and sc and sc <= 4096:
            for k in range(sc):
                conta('+0x14 nivel 1', 'slot[k]', u32(pb + 4 * k))
                n2 = off(u32(pb + 4 * k))
                if n2 is None:
                    continue
                for g in range(gc):
                    conta('+0x14 nivel 2', 'contagens', u32(n2 + 8 * g))
                    conta('+0x14 nivel 2', 'vetores', u32(n2 + 8 * g + 4))
                    ea, eb = off(u32(n2 + 8 * g)), off(u32(n2 + 8 * g + 4))
                    if ea is None or eb is None:
                        continue
                    nb2 = u32(ea)
                    if not nb2 or nb2 > 4096:
                        continue
                    for j in range(nb2):
                        conta('+0x14 vetor', 'ponteiro por bloco', u32(eb + 4 * j))

    def componente(o):
        if o is None or o in vistas:
            return
        vistas.add(o)
        for campo, x in (('+0x04', 0x04), ('+0x08 nome', 0x08), ('+0x0C corrente', 0x0C),
                         ('+0x10', 0x10), ('+0x14', 0x14), ('+0x18', 0x18),
                         ('+0x28 tipo', 0x28)):
            conta('ComponentData', campo, u32(o + x))
        for k in range(10):
            conta('ComponentData', 'lod[0]' if k == 0 else 'lod[1..9]',
                  u32(o + 0x3C + 4 * k))
        for k in range(10):
            malha(off(u32(o + 0x3C + 4 * k)))

    ngrp, vgrp = u32(R + 0x08), off(u32(R + 0x0C))
    if vgrp is not None:
        for g in range(ngrp or 0):
            e = vgrp + 0x10 * g
            conta('ShaderGroupDesc', 'array_va', u32(e + 4))
            arr, ns = off(u32(e + 4)), u16(e + 8)
            if arr is None or not ns:
                continue
            for k in range(ns):
                conta('grupo de shader', 'slot[k]', u32(arr + 4 * k))
                s = off(u32(arr + 4 * k))
                if s is None:
                    continue
                f = u32(s + 4) or 0
                for i in range(max((f >> 22) & 7, 1)):
                    conta('shader', 'parametro[i]', u32(s + 8 + 4 * i))
                    textura(off(u32(s + 8 + 4 * i)))

    nh, vh = u32(R + 0x14), off(u32(R + 0x18))
    if vh is not None:
        for h in range(nh or 0):
            e = vh + 0x14 * h
            for campo, x in (('desc_va', 0x00), ('unique_array', 0x08),
                             ('instance_array', 0x10)):
                conta('HoodEntry', campo, u32(e + x))
            nu, au = u32(e + 4), off(u32(e + 8))
            ni, ai = u32(e + 0x0C), off(u32(e + 0x10))
            desc = off(u32(e))
            if desc is not None:
                textura(desc + 4)
            if au is not None and nu and nu < 0x100000:
                for k in range(nu):
                    conta('UniqueComponent', 'data_va', u32(au + 0x1C * k + 0x0C))
                    conta('UniqueComponent', 'type_va', u32(au + 0x1C * k + 0x10))
                    componente(off(u32(au + 0x1C * k + 0x0C)))
            if ai is not None and ni and ni < 0x100000:
                for k in range(ni):
                    conta('Instance', 'data_va', u32(ai + 0x60 * k + 0x0C))
                    conta('Instance', 'type_va', u32(ai + 0x60 * k + 0x10))
                    componente(off(u32(ai + 0x60 * k + 0x0C)))


def confere(referencias, alvo):
    """Medir a obrigacao no varejo e apontar o que o arquivo alvo viola.

    Um campo so entra como obrigatorio se o varejo o preencheu em TODAS as
    ocorrencias. Um campo que o alvo nem tem (contagem zero) nao e violacao: e
    ausencia, e vai listado a parte, porque uma cidade com zero instancias nao
    esta errada - so nao exercita aquele campo.
    """
    ref = collections.OrderedDict()
    for r in referencias:
        censo(Pck(r), ref)
    # DUAS classes de "nunca nulo", e a diferenca importa:
    #   ponteiro   nunca zero E sempre um endereco valido do arquivo
    #   nao-zero   nunca zero, mas nem sempre ponteiro - rmcModelGeom+0x18 e
    #              1 em 624 malhas, ponteiro em 408 e CDCDCDCD em 190. Um campo
    #              que vem CD e um campo que ninguem inicializa; chamar isso de
    #              obrigatorio seria forte demais.
    obrig = {k for k, (tot, nulos, f) in ref.items() if tot and nulos == 0 and not f}
    naozero = {k for k, (tot, nulos, f) in ref.items() if tot and nulos == 0 and f}

    alv = collections.OrderedDict()
    censo(Pck(alvo), alv)

    viola, ausente, ok = [], [], 0
    for k in sorted(obrig):
        if k not in alv or alv[k][0] == 0:
            ausente.append(k)
            continue
        tot, nulos, _f = alv[k]
        if nulos:
            viola.append((k, tot, nulos))
        else:
            ok += 1

    print('referencia: %d cidade(s)' % len(referencias))
    print('  %d campos SEMPRE ponteiro valido (obrigatorios)' % len(obrig))
    print('  %d campos nunca zero mas nem sempre ponteiro (conferidos a parte)'
          % len(naozero))
    for est, campo in sorted(naozero):
        tot, nulos, f = ref[(est, campo)]
        alvo_v = alv.get((est, campo))
        situacao = ('alvo: %d de %d nulos' % (alvo_v[1], alvo_v[0])) if alvo_v and alvo_v[0] else 'alvo nao exercita'
        print('     %-18s %-24s %d de %d fora do arquivo   %s'
              % (est, campo, f, tot, situacao))
    print()
    print('alvo: %s' % alvo)
    print()
    print('CUMPRE  %d de %d' % (ok, len(obrig)))
    print('VIOLA   %d' % len(viola))
    for (est, campo), tot, nulos in viola:
        print('   %-18s %-24s %d de %d nulos' % (est, campo, nulos, tot))
    print('NAO EXERCITA  %d  (o arquivo nao tem nenhuma ocorrencia)' % len(ausente))
    for est, campo in ausente:
        print('   %-18s %s' % (est, campo))
    return 1 if viola else 0


def main():
    ap = argparse.ArgumentParser(
        description=__doc__.strip().splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pcks', nargs='+')
    ap.add_argument('--conferir', metavar='PCK',
                    help='medir a obrigacao nos pcks de referencia e depois '
                         'CONFERIR este arquivo contra ela')
    a = ap.parse_args()

    if a.conferir:
        return confere(a.pcks, a.conferir)

    c = collections.OrderedDict()
    for caminho in a.pcks:
        censo(Pck(caminho), c)

    print('%d cidades' % len(a.pcks))
    print()
    print('%-18s %-24s %9s %9s %8s' % ('estrutura', 'campo', 'total', 'nulos', '%'))
    obrig, livres = [], []
    for (est, campo), (tot, nulos, fora) in c.items():
        pct = 100.0 * nulos / tot if tot else 0.0
        linha = '%-18s %-24s %9d %9d %7.1f%%' % (est, campo, tot, nulos, pct)
        if fora:
            linha += '   (%d fora do arquivo)' % fora
        print(linha)
        (obrig if nulos == 0 else livres).append('%s.%s' % (est, campo))

    print()
    print('NUNCA NULO no varejo - trate como obrigatorio (%d campos):' % len(obrig))
    for x in obrig:
        print('   %s' % x)
    print()
    print('TOLERA NULO - o jogo carrega assim (%d campos):' % len(livres))
    for x in livres:
        print('   %s' % x)
    return 0


if __name__ == '__main__':
    sys.exit(main())
