"""
mc3_place_sim.py - run the city .pck loader's Place walk on the PC, before booting

Every mistake so far cost a boot of the console to discover, and the failure mode
is the worst possible one: an infinite loop with no message. This walks the same
graph the game walks, in the same order, and reports what the game would hit.

WHERE THE RULES COME FROM (all read out of the retail ELF, addresses noted so
they can be re-checked):

  mcCity::mcCity(datResource&)  0x259160   the actual reader; `mcCity::Place`
                                           only calls it. `*(datResource+4)` is
                                           the relocation delta.
  sub_2B3600                    0x2B3600   places one 16-byte group descriptor:
                                             +0x00 vtable  +0x04 data pointer
                                             +0x08 u16 COUNT (the one used)
                                             +0x0C linked-list next
  vtable(dword_615E48)[5]       0x2AF9E8   walks the pointer array. For each
                                           slot: relocate it, then dispatch on
                                           `*(obj+4) & 0x7F`:
                                             0 -> sub_2AFF20   1 -> sub_2B2A08
                                             2 -> sub_2B5B58
                                             anything else -> loc_2AFA88, which
                                             is `nop x5; b loc_2AFA88` - an
                                             INFINITE LOOP (a stripped assert).
  sub_2AFF20                    0x2AFF20   type 0: stamps the vtable, then runs
                                           0x2BA718 over `obj+0x08`, count 1.
  0x2BA718                      0x2BA718   dispatches on the BYTE at `+0x04` of
                                           that sub-object, values 0..3; the
                                           else branch is loc_2BA7E0, the same
                                           `nop x5; b` infinite loop.

WHAT THIS CHECKS, and why each one is a bug that actually happened here:

  * a tag outside the handled set        -> the game spins forever
  * the SAME object in more than one slot -> the walk has no "already placed"
    guard, so its handler runs once per slot and re-adds the delta to its
    internal pointers every time. This is what broke the generated file: 1329
    slots pointing at one shader.
  * a null slot                          -> not skipped; the code reads `*(0+4)`
  * a pointer outside the body           -> reads whatever is next in RAM

    python mc3_place_sim.py CIDADE.pck
    python mc3_place_sim.py CIDADE.pck --detalhe

ALWAYS run it on an untouched retail city first. A checker that fails the
shipped file is measuring itself, not the file - that already happened once here
with the AABB check.
"""

import argparse
import collections
import importlib.util
import os
import struct
import sys

_AQUI = os.path.dirname(os.path.abspath(__file__))
_SV = importlib.util.spec_from_file_location('mc3_view', os.path.join(_AQUI, 'mc3_view.py'))
_view = importlib.util.module_from_spec(_SV)
sys.modules['mc3_view'] = _view
_SV.loader.exec_module(_view)

TIPOS_OK = (0, 1, 2)          # 0x2AF9E8: tudo o mais cai no laco infinito
SUB_TIPOS_OK = (0, 1, 2, 3)   # 0x2BA718: idem


class Corpo:
    """O corpo do .pck, endereçado por VA como o jogo faz."""

    def __init__(self, path):
        self.d = open(path, 'rb').read()
        self.base_va, self.tipo, self.versao, self.corpo = struct.unpack_from('<4I', self.d, 0)
        self.base = self.base_va - 0x80

    def off(self, va):
        return va - self.base

    def dentro(self, va):
        o = self.off(va)
        return 0x80 <= o <= len(self.d) - 4

    def u32(self, va):
        return struct.unpack_from('<I', self.d, self.off(va))[0]

    def u16(self, va):
        return struct.unpack_from('<H', self.d, self.off(va))[0]

    def u8(self, va):
        return self.d[self.off(va)]


def checa_bloco(c, entrada):
    """None se o bloco esta coerente, ou a descricao do que nao fecha.

    A entrada de bloco e `[u32 endereco][u16 qwc][u16 nv]` e `gfxGeometry::Draw`
    (0x1ED930) monta com ela uma DMAtag `qwc | 0x30000000 | (endereco << 32)`.
    O `qwc` NAO e uma dica: e o contador da transferencia. Se ele nao bate com o
    tamanho real do packet, o VIF recebe pedaco a mais (le lixo como comando) ou
    a menos (o pacote fica sem a cauda que o fecha).

    E `nv` tem que bater com quantos vertices o stream de POSICAO desempacota,
    senao o mesh desenha um numero de triangulos diferente do que declarou.
    """
    va, qwc, nv = struct.unpack_from('<IHH', c.d, c.off(entrada))
    if not va:
        return None
    if not c.dentro(va):
        return 'packet fora do corpo (%08X)' % va
    if not qwc:
        return 'qwc zero'
    fim = va + 16 * qwc
    if not c.dentro(fim - 4):
        return 'packet de %d qw passa do fim do corpo' % qwc
    # NAO limitar nv a 256: isso era um filtro heuristico do leitor de AABB, e o
    # proprio atlanta tem blocos de 308, 404 e ate 525 vertices. O gabarito manda.
    if nv < 3:
        return 'nv = %d (menos de um triangulo)' % nv
    lotes = _view._vif_walk(c.d, c.off(va), 16 * qwc)
    if not lotes:
        return 'o stream VIF dessincroniza dentro dos %d qw declarados' % qwc
    achou = 0
    for lote in lotes:
        for _rel, cmd, _off, num in lote:
            if (cmd & 0x0F) == 0x04 and (cmd & 0x60) == 0x60:   # V3-16/V3-32 = posicao
                achou += num
    if achou and achou != nv:
        return 'nv declara %d mas o stream de posicao traz %d' % (nv, achou)
    return None


# Todo campo do MapRoot que `mcCity::mcCity` (0x259160) toca, na ordem do codigo.
# `modelado` diz se ESTE simulador percorre a estrutura ou apenas confere se o
# ponteiro e valido. O que nao e modelado nao esta sendo verificado - saber disso
# importa mais do que a lista de aprovacoes.
CAMPOS_MAPROOT = [
    (0x1D4, 'objeto via vtable[9]',      'sub_?  (a1+468)',        False),
    (0x1D8, '20 ponteiros via vtable[9]', 'laco de 20 (a1+472..)', False),
    (0x0C,  'descritores de shader',      'sub_2B3600 x n',        True),
    (0x10,  'mais um array de shader',    'sub_2B3600',            True),
    (0x18,  'tabela de hood',             'sub_25D4F0 x n',        True),
    (0x1C,  'indice plano da cidade',     'sub_25B9D8',            False),
    (0x2C,  'paleta A',                   'so relocado',           True),
    (0x30,  'paleta B',                   'so relocado',           True),
    (0x190, 'estrutura de 0x190',         'sub_25C998',            False),
    (0x194, 'estrutura de 0x194',         'sub_24C528',            False),
    (0x198, 'estrutura de 0x198',         'sub_2571B0',            False),
    (0x19C, 'ponteiro de 0x19C',          'so relocado',           False),
    (0x1CC, 'ponteiro de 0x1CC',          'so relocado',           False),
    (0x228, 'estrutura de 0x228',         'sub_2BA6B0',            False),
]


def cobertura(path, referencia):
    """O que o arquivo tem, o que a referencia tem, e o que este simulador cobre.

    Responde a pergunta que importa antes de bootar: **quais partes da cidade eu
    deixei vazias**. Um campo nulo nao trava o `Place` - todos sao guardados por
    `if (ptr)` - mas nada garante que quem consome a cidade depois tolere a
    ausencia. Esta tabela e a lista de suspeitos, em ordem.
    """
    c, r = Corpo(path), Corpo(referencia)
    print('%s   x   %s (referencia)' % (os.path.basename(path), os.path.basename(referencia)))
    print()
    print('  %-6s %-28s %-24s %-9s %-9s %s'
          % ('campo', 'o que e', 'quem percorre', 'ref', 'este', 'simulado'))
    faltando = []
    for off, oque, quem, mod in CAMPOS_MAPROOT:
        vr = r.u32(r.base_va + off)
        vc = c.u32(c.base_va + off)
        est = 'tem' if vc else 'VAZIO'
        if vr and not vc:
            faltando.append((off, oque, quem, mod))
        print('  +%-5X %-28s %-24s %-9s %-9s %s'
              % (off, oque[:28], quem[:24], 'tem' if vr else '-', est,
                 'sim' if mod else 'NAO'))
    print()
    n_mod = sum(1 for _o, _q, _w, m in CAMPOS_MAPROOT if m)
    print('  este simulador percorre %d de %d estruturas do MapRoot' % (n_mod, len(CAMPOS_MAPROOT)))
    if faltando:
        print('  %d campo(s) que a referencia tem e este arquivo NAO:' % len(faltando))
        for off, oque, quem, mod in faltando:
            print('     +0x%-4X %-28s (%s)%s' % (off, oque, quem,
                  '' if mod else '   <- e nem e verificado aqui'))
    else:
        print('  nenhum campo presente na referencia esta vazio aqui')
    return faltando


def simula(path, detalhe=False):
    c = Corpo(path)
    raiz = c.base_va                      # o MapRoot fica em file 0x80 = base VA
    prob = []
    def erro(cat, msg):
        prob.append((cat, msg))

    print('%s' % os.path.basename(path))
    print('  cabecalho: base %08X, tipo %d, versao %d, corpo %d (arquivo %d)'
          % (c.base_va, c.tipo, c.versao, c.corpo, len(c.d)))
    if c.tipo != 67:
        erro('cabecalho', 'tipo %d, nao 67 - o carregador sai calado' % c.tipo)
    if c.corpo != len(c.d) - 0x80:
        erro('cabecalho', 'corpo declarado %d, arquivo tem %d' % (c.corpo, len(c.d) - 0x80))

    n_grupos = c.u32(raiz + 0x08)
    p_grupos = c.u32(raiz + 0x0C)
    p_campo10 = c.u32(raiz + 0x10)
    n_hoods = c.u32(raiz + 0x14)
    p_hoods = c.u32(raiz + 0x18)
    print('  MapRoot: %d grupo(s) de shader, %d hood(s)' % (n_grupos, n_hoods))

    # mcCity::mcCity percorre os descritores de grupo e, depois, o +0x10 pela
    # MESMA funcao - +0x10 e outro array de shader, nao uma estrutura a parte
    descritores = []
    if p_grupos:
        if not c.dentro(p_grupos):
            erro('maproot', '+0x0C aponta fora do corpo (%08X)' % p_grupos)
        else:
            descritores += [p_grupos + 16 * i for i in range(n_grupos)]
    elif n_grupos:
        erro('maproot', '+0x0C NULO com contagem %d' % n_grupos)
    if p_campo10:
        if c.dentro(p_campo10):
            descritores.append(p_campo10)
        else:
            erro('maproot', '+0x10 aponta fora do corpo (%08X)' % p_campo10)
    else:
        erro('maproot', '+0x10 NULO - o PS2 le o endereco 0 em vez de falhar, e '
                        'o Place sai andando em lixo')
    for nome, campo in (('+0x18 hoods', p_hoods), ('+0x2C paletaA', c.u32(raiz + 0x2C)),
                        ('+0x30 paletaB', c.u32(raiz + 0x30)),
                        ('+0x1C', c.u32(raiz + 0x1C))):
        if not campo:
            erro('maproot', '%s NULO' % nome)
        elif not c.dentro(campo):
            erro('maproot', '%s fora do corpo (%08X)' % (nome, campo))

    # ---- o laco de 0x2AF9E8, uma vez por descritor
    donos = collections.defaultdict(list)     # objeto -> [(grupo, slot)]
    tags = collections.Counter()
    nulos = 0
    for gi, desc in enumerate(descritores):
        if not c.dentro(desc):
            continue
        dados = c.u32(desc + 4)
        n = c.u16(desc + 8)                    # `lhu a3, 4(a3)` com a3 = desc+4
        if not n:
            continue
        if not c.dentro(dados):
            erro('grupo %d' % gi, 'ponteiro de dados fora do corpo (%08X)' % dados)
            continue
        for k in range(n):
            va = dados + 4 * k
            if not c.dentro(va):
                erro('grupo %d' % gi, 'array passa do fim do corpo no slot %d' % k)
                break
            obj = c.u32(va)
            if not obj:
                nulos += 1
                continue
            if not c.dentro(obj):
                erro('grupo %d' % gi, 'slot %d aponta fora do corpo (%08X)' % (k, obj))
                continue
            donos[obj].append((gi, k))
            tags[c.u32(obj + 4) & 0x7F] += 1

    maior_array = max([c.u16(dd + 8) for dd in descritores if c.dentro(dd)] or [0])

    # ---- os tres testes que vieram do codigo
    ruins = sorted(t for t in tags if t not in TIPOS_OK)
    if ruins:
        # nao e veredito: um objeto colocado ANTES pelo dono dele tem o +0x04
        # reescrito, e ai o tipo lido aqui nao e o que o jogo vai ver
        print('  tipos vistos: %s' % ', '.join('%d(%d)' % (t, tags[t]) for t in sorted(tags)))
        print('    fora de {0,1,2}: %s  -- so travam se NAO forem colocados antes pelo dono'
              % ', '.join(str(t) for t in ruins))
    else:
        print('  tipos vistos: %s (todos tratados)'
              % ', '.join('%d(%d)' % (t, tags[t]) for t in sorted(tags)))

    repetidos = {o: v for o, v in donos.items() if len(v) > 1}
    if repetidos:
        pior = max(repetidos.values(), key=len)
        erro('repeticao',
             '%d objeto(s) aparecem em mais de um slot; o pior aparece %d vezes. '
             'O laco NAO tem guarda de "ja colocado": o handler roda uma vez por '
             'slot e re-soma o delta nos ponteiros internos a cada passada'
             % (len(repetidos), len(pior)))
        if detalhe:
            for o, v in sorted(repetidos.items(), key=lambda x: -len(x[1]))[:5]:
                print('     %08X aparece %d vezes: %s%s'
                      % (o, len(v), v[:4], ' ...' if len(v) > 4 else ''))

    print('  %d objetos distintos em %d slot(s) preenchido(s), %d nulo(s)'
          % (len(donos), sum(len(v) for v in donos.values()), nulos))
    if nulos:
        print('    (slot nulo NAO e pulado: o codigo le *(0+4). Funciona por '
              'acidente no PS2, mas e motivo pra preencher todos)')

    # ---- o MapRoot vai ate +0x228, nao ate +0x80
    #
    # `mcCity::mcCity` mexe em +0x190, +0x194, +0x198, +0x19C, +0x1CC e +0x228,
    # e num laco de 20 ponteiros a partir de +0x1D8. Um MapRoot de 0x80 bytes
    # deixa tudo isso caindo em cima do que vier depois no arquivo - foi o que
    # o construtor do zero fazia, e o carregador lia geometria como ponteiro.
    FIM_MAPROOT = 0x22C
    if len(c.d) - c.off(raiz) < FIM_MAPROOT:
        erro('maproot', 'o MapRoot tem so %d bytes ate o fim do corpo; mcCity usa '
                        'ate +0x228 (%d)' % (len(c.d) - c.off(raiz), FIM_MAPROOT))
    else:
        for off, quem in ((0x190, 'sub_25C998'), (0x194, 'sub_24C528'),
                          (0x198, 'sub_2571B0'), (0x228, 'sub_2BA6B0')):
            v = c.u32(raiz + off)
            if v and not c.dentro(v):
                erro('maproot', '+0x%X fora do corpo (%08X) e nao-nulo, entao %s '
                                'vai percorre-lo' % (off, v, quem))

    # ---- os hoods: sub_25D4F0 (passo 20), sub_24C598 (28), sub_257220 (96)
    #
    # O Place do hood e RASO: `+0x00` (o registro) e so relocado, nunca
    # percorrido, e o ComponentData de `+0x0C` idem. Tudo guardado por `if`,
    # entao ponteiro nulo com contagem zero e legitimo aqui.
    comps = []
    if p_hoods and c.dentro(p_hoods):
        for h in range(n_hoods):
            e = p_hoods + 20 * h
            if not c.dentro(e + 16):
                erro('hood %d' % h, 'entrada passa do fim do corpo')
                break
            rec, nu, au, ni, ai = struct.unpack_from('<5I', c.d, c.off(e))
            for nome, va in (('registro', rec), ('array unique', au), ('array instance', ai)):
                if va and not c.dentro(va):
                    erro('hood %d' % h, '%s fora do corpo (%08X)' % (nome, va))
            if au and c.dentro(au):
                for k in range(nu):
                    comp = au + 28 * k
                    if not c.dentro(comp + 24):
                        erro('hood %d' % h, 'array unique passa do fim no item %d' % k)
                        break
                    comps.append(comp)
            elif nu:
                erro('hood %d' % h, '%d uniques mas o array e NULO' % nu)
            if ai and c.dentro(ai):
                if not c.dentro(ai + 96 * ni - 4) and ni:
                    erro('hood %d' % h, 'array instance passa do fim do corpo')
            elif ni:
                erro('hood %d' % h, '%d instances mas o array e NULO' % ni)

    # ---- ponteiro pendurado em blob COPIADO
    #
    # Um valor na faixa de VA que aponta ALEM do fim do corpo. Sozinho isso nao
    # acusa nada - o proprio atlanta tem milhares, porque coordenada de vertice
    # as vezes parece endereco. O que acusa e a REPETICAO EXATA: um blob copiado
    # do doador e replicado N vezes carrega o mesmo ponteiro pendurado N vezes,
    # e coordenada nao faz isso. Foi assim que apareceu o segundo ponteiro do
    # bloco de shader (`+0x0C`), repetido 64 vezes.
    fim_corpo = c.base_va + c.corpo
    onde = collections.defaultdict(list)
    for o in range(0x80, len(c.d) - 4, 4):
        v = struct.unpack_from('<I', c.d, o)[0]
        if c.base_va <= v < c.base_va + 0x1000000 and v >= fim_corpo:
            onde[v].append(o)
    # o discriminante e o PASSO CONSTANTE: um blob replicado poe o mesmo ponteiro
    # sempre no mesmo offset interno, entao as ocorrencias ficam equidistantes.
    # Coordenada de vertice que por acaso parece VA nao faz isso - foi o que
    # reprovou o atlanta na primeira versao deste teste (65 valores, um deles
    # 434 vezes), e um checador que reprova o arquivo de fabrica esta medindo a
    # si mesmo.
    suspeitos = []
    for v, offs in onde.items():
        if len(offs) < 8:
            continue
        passos = {offs[i + 1] - offs[i] for i in range(len(offs) - 1)}
        if len(passos) == 1 and 8 <= passos.pop() <= 0x400:
            suspeitos.append((v, len(offs), offs[1] - offs[0]))
    # AVISO, nao reprovacao: nem com o passo constante da pra separar ponteiro de
    # dado com seguranca — o atlanta tem um valor repetido 14 vezes a cada 0xC
    # bytes que e array legitimo. Subir o limiar ate o retail passar seria
    # ajustar o teste ao gabarito. A garantia de verdade fica no construtor, em
    # `limpa()`, que zera todo ponteiro de blob copiado por construcao; isto aqui
    # so chama atencao pro que MERECE olhada.
    if suspeitos:
        v, n, passo = max(suspeitos, key=lambda x: x[1])
        print('  aviso: %d ponteiro(s) fora do corpo repetidos com PASSO '
              'CONSTANTE; o pior (%08X) aparece %d vezes a cada 0x%X bytes'
              % (len(suspeitos), v, n, passo))
        print('         (o atlanta tem 2 assim, entao isto sozinho nao reprova; '
              'olhar quando o passo for o tamanho de um blob que voce copia)')
        if detalhe:
            for v, n, passo in sorted(suspeitos, key=lambda x: -x[1])[:6]:
                print('     %08X x%d passo 0x%X' % (v, n, passo))

    # ---- MapRoot+0x1C: o indice plano da cidade
    #
    # Medido no atlanta: array1 sao os 651 componentes unique (651 de 651 batem)
    # e array2 as 3608 instances (3608 de 3608). `sub_25B9D8` reloca cada
    # ponteiro dos dois, e os dois arrays de scratch em +0x10/+0x14 sao
    # dimensionados por `mcCity+0x268` - que fica DENTRO do MapRoot, logo o
    # MapRoot precisa ter pelo menos 0x26C bytes.
    p1c = c.u32(raiz + 0x1C)
    if p1c and c.dentro(p1c + 0x18):
        n1, n2 = c.u32(p1c), c.u32(p1c + 4)
        a1, a2v = c.u32(p1c + 8), c.u32(p1c + 12)
        if n1 != len(comps):
            erro('+0x1C', 'declara %d componentes mas os hoods tem %d' % (n1, len(comps)))
        elif n1 and c.dentro(a1 + 4 * n1):
            no_indice = {c.u32(a1 + 4 * k) for k in range(n1)}
            faltam = {c.base_va + (x - c.base) for x in ()}   # placeholder
            falta = len(set(comps) - no_indice)
            if falta:
                erro('+0x1C', '%d componente(s) dos hoods fora do indice' % falta)
        for nome, va, n in (('array1', a1, n1), ('array2', a2v, n2)):
            if n and (not va or not c.dentro(va + 4 * n - 4)):
                erro('+0x1C', '%s invalido pra %d entradas' % (nome, n))
        escala = c.u32(raiz + 0x268) if len(c.d) - c.off(raiz) >= 0x26C else None
        if escala is None:
            erro('+0x1C', 'MapRoot menor que 0x26C: mcCity+0x268 (o tamanho dos '
                          'scratch de +0x10/+0x14) cai fora dele')
        else:
            for off, larg in ((0x10, 12), (0x14, 4)):
                va = c.u32(p1c + off)
                if escala and (not va or not c.dentro(va + larg * escala - 4)):
                    erro('+0x1C', 'scratch de +0x%X nao cabe %d registros de %d bytes'
                                  % (off, escala, larg))

    # ---- depois do Place: o que consome o hood le a geometria
    n_mesh = n_slot_ruim = n_bloco_ruim = n_cd_ruim = 0
    for comp in comps:
        cd = c.u32(comp + 0x0C)
        if not cd:
            continue
        if not c.dentro(cd + 0x60):
            erro('componente', 'ComponentData fora do corpo (%08X)' % cd)
            continue
        # ComponentData: dois campos sao CONSTANTES nos 651 do atlanta, e zerar
        # o de +0x28 (um token de vtable) produziu `Jump to unaligned address`
        # quando a camera chegou perto do modelo - chamada virtual por ponteiro
        # lido de lixo.
        if c.u32(cd + 0x00) != 1:
            n_cd_ruim += 1
        # +0x28 e vtable. O retail grava o TOKEN 0x0079FF88 e o jogo traduz pra
        # 0x00625098 na carga; um objeto gerado nao entra na lista do tradutor,
        # entao pra ele o certo e ja gravar o endereco traduzido. Os dois valem.
        if c.u32(cd + 0x28) not in (0x0079FF88, 0x00625098):
            n_cd_ruim += 1
            if detalhe and n_cd_ruim <= 4:
                print('     ComponentData %08X: +0x28 = %08X, esperado 0079FF88 '
                      '(token) ou 00625098 (traduzido)' % (cd, c.u32(cd + 0x28)))
        for slot in range(10):
            mp = c.u32(cd + 0x3C + 4 * slot)
            if not mp:
                continue
            if not c.dentro(mp + 0x14):
                erro('componente', 'mesh do slot %d fora do corpo (%08X)' % (slot, mp))
                continue
            n_mesh += 1
            # mesma historia do ComponentData: o retail grava o token 0x007A1E18
            # e o jogo traduz pra 0x00626D98; objeto gerado nao entra na lista do
            # tradutor, entao pra ele o certo e ja gravar o traduzido
            if c.u32(mp) not in (0x007A1E18, 0x00626D98):
                n_cd_ruim += 1
                if detalhe:
                    print('     mesh %08X: vtable %08X, esperado 007A1E18 ou 00626D98'
                          % (mp, c.u32(mp)))
            ngrp = c.u16(mp + 8)
            mt, gt = c.u32(mp + 0x0C), c.u32(mp + 0x10)
            if ngrp and (not mt or not c.dentro(mt + 2 * ngrp)):
                erro('mesh', '%08X: tabela de material invalida com %d grupo(s)' % (mp, ngrp))
                continue
            if ngrp and (not gt or not c.dentro(gt + 8 * ngrp)):
                erro('mesh', '%08X: tabela de grupos invalida com %d grupo(s)' % (mp, ngrp))
                continue
            for g in range(ngrp):
                idx = c.u16(mt + 2 * g)
                if idx >= maior_array:
                    n_slot_ruim += 1
                    if detalhe and n_slot_ruim <= 5:
                        print('     mesh %08X grupo %d: material %d >= %d slots'
                              % (mp, g, idx, maior_array))
                lp, cnt, _z = struct.unpack_from('<IHH', c.d, c.off(gt + 8 * g))
                if not lp or not c.dentro(lp + 8 * cnt):
                    erro('mesh', '%08X grupo %d: lista de blocos invalida' % (mp, g))
                    continue
                for b_ in range(cnt):
                    est = checa_bloco(c, lp + 8 * b_)
                    if est:
                        n_bloco_ruim += 1
                        if detalhe and n_bloco_ruim <= 6:
                            print('     mesh %08X grupo %d bloco %d: %s' % (mp, g, b_, est))
    if n_cd_ruim:
        erro('componentdata', '%d campo(s) constante(s) errado(s) em ComponentData '
                              '(+0x00 deve ser 1, +0x28 deve ser 0079FF88)' % n_cd_ruim)
    if n_bloco_ruim:
        erro('bloco', '%d bloco(s) com qwc que nao bate com o packet, ou nv que nao '
                      'bate com o stream de posicao' % n_bloco_ruim)
    if n_slot_ruim:
        erro('material', '%d grupo(s) com indice de material alem do fim do array '
                         'de shader (%d slots)' % (n_slot_ruim, maior_array))
    print('  %d componente(s) unique, %d mesh(es) alcancavel(is)' % (len(comps), n_mesh))

    # ---- o sub-objeto de +0x08 dos objetos de tipo 0 (0x2BA718)
    maus_sub = 0
    for obj, refs in donos.items():
        if (c.u32(obj + 4) & 0x7F) != 0:
            continue
        sub = c.u32(obj + 8)
        if not sub or not c.dentro(sub):
            erro('tipo 0', 'objeto %08X tem +0x08 invalido (%08X)' % (obj, sub))
            continue
        b = c.u8(sub + 4)
        if b not in SUB_TIPOS_OK:
            maus_sub += 1
            if detalhe and maus_sub <= 5:
                print('     sub-objeto de %08X: byte +0x04 = %d (fora de 0..3)' % (obj, b))
    if maus_sub:
        erro('tipo 0', '%d sub-objeto(s) com byte +0x04 fora de 0..3 -> loc_2BA7E0' % maus_sub)

    print()
    if prob:
        print('  %d PROBLEMA(S):' % len(prob))
        for cat, m in prob:
            print('    [%s] %s' % (cat, m))
    else:
        print('  nada que o codigo lido reprove')
    return not prob


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pck', nargs='+')
    ap.add_argument('--detalhe', action='store_true')
    ap.add_argument('--cobertura', metavar='REFERENCIA',
                    help='compara campo a campo com um .pck que funciona e diz o '
                         'que este simulador NAO verifica')
    a = ap.parse_args()
    if a.cobertura:
        for p in a.pck:
            cobertura(p, a.cobertura)
            print()
        raise SystemExit(0)
    ok = True
    for p in a.pck:
        ok = simula(p, a.detalhe) and ok
        print()
    raise SystemExit(0 if ok else 1)


if __name__ == '__main__':
    main()
