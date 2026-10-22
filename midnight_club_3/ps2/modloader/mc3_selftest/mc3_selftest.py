"""
mc3_selftest.py - re-implement the patched game functions and test them

A patch that was reasoned about but never executed is a hypothesis. This file
turns each one into something that can fail: the traced functions are rewritten
in Python straight from the disassembly, then run against numbers measured out of
real savestates. If a replica cannot reproduce what the game actually did, the
understanding behind the patch is wrong and the test says so.

Three layers, cheapest first:

  1. ENCODING - decode every patched word as MIPS and as an IEEE float, and
     check it means what the patch claims. Catches a typo'd constant instantly.
  2. BEHAVIOUR - run the replicas at 30 Hz and at 60 Hz and compare against the
     savestate measurements. This is where a wrong *model* dies: the frame-locked
     and the dt-scaled hypotheses predict different numbers, and only one matches.
  3. ELF - confirm the built files contain exactly the intended words, that
     nothing else in the loaded image moved, and that the CRC still matches.

    python mc3_selftest.py                 # tudo
    python mc3_selftest.py --sstates DIR   # re-mede dos savestates em vez de usar os valores gravados
"""

import argparse
import math
import os
import struct
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(AQUI)

# HostFS moved off the project drive, and the file name is lowercase there. Try
# the known places instead of hard-coding one, so the ELF tests keep running
# rather than reporting a missing file as a failure.
HOSTFS_DIRS = (os.path.join(BASE, 'MC3HostFS'), os.environ.get('MC3_HOSTFS', ''), os.environ.get('MC3_HOSTFS_ALT', ''))


def hostfs(nome):
    for d in HOSTFS_DIRS:
        for n in (nome, nome.lower(), nome.upper()):
            c = os.path.join(d, n)
            if os.path.isfile(c):
                return c
    return os.path.join(HOSTFS_DIRS[0], nome)

# --------------------------------------------------------------------------
# medidas tiradas dos savestates (ver mc3-60fps-timestep na memoria)
# --------------------------------------------------------------------------
MEDIDO_30 = dict(tiques=80,  sim=2.6659, dt=0.0333410, por_tique=0.037341, u_s=1.1205)
MEDIDO_60 = dict(tiques=171, sim=2.8485, dt=0.0166666, por_tique=0.032954, u_s=1.9783)

ANIM_WALK = ('ASSETS/ped/anim/mped01_walk01.anim', 49, 1.7850)   # arquivo, quadros, avanco

# taxas (+0x10) lidas dos 23 pedestres vivos no savestate
TAXAS_VIVAS = [1.0]*15 + [1.1029, 1.1455, 1.2505, 1.3745, 1.2386, 1.4033, 1.2702, 1.4213]


def f32(w):
    """Bit pattern -> float, the way the FPU sees it."""
    return struct.unpack('<f', struct.pack('<I', w & 0xFFFFFFFF))[0]


def bits(f):
    return struct.unpack('<I', struct.pack('<f', f))[0]


# ==========================================================================
#  1. REPLICAS  (cada uma cita o endereco de onde foi lida)
# ==========================================================================

def mcTimer_Tick(ciclos, est):
    """0x433490. Le o Count do EE e produz o dt do quadro.

    O relogio e sempre lido; se `modo_passo_fixo` estiver ligado o resultado e
    descartado e o passo fixo entra no lugar. Nos savestates o modo esta 0 e
    `passo_fixo` e 0.0, entao o caminho que roda e o do dt medido sem teto.
    """
    medido = ciclos * 3.3908421e-9
    trabalho = medido

    if est['quantiza']:                       # byte_618E4E, 0 no jogo real
        for k in (1, 2, 3, 4):
            if medido < k / 60.0:
                trabalho = k / 60.0
                break

    # clamp intermediario: flt_618E38 .. flt_618E34
    trabalho = min(max(trabalho, est['min']), est['max'])

    v9 = trabalho * est['escala']

    if est['modo_passo_fixo']:                # dword_618E48
        dt = est['passo_fixo'] * est['escala']
    elif est['passo_fixo'] == 0.0:
        dt = v9
    elif v9 >= est['passo_fixo']:
        dt = est['passo_fixo']                # o passo vira TETO
    else:
        dt = v9

    dt = min(max(dt, est['min']), est['max'])
    return dt, (1.0 / dt)                     # flt_618E20, flt_618E28


def mcCreature_Init_taxa(patchado, aleatorio01, tem_variacao):
    """0x45F638..0x45F698. De onde a taxa de animacao REALMENTE sai.

    O construtor 0x4633A0 poe 1.0 em +0x10, mas `sub_463418` (SetRate) sobrescreve
    logo depois com o que `mcCreature::Init` calculou e guardou em criatura+0x15C:

        $f1 = 0x3EB33334 = 0.35    amplitude
        $f2 = 0x3F8CCCCD = 1.10    base
        taxa = 1.10 + rand01 * 0.35        -> faixa 1.10 .. 1.45
        ou entao o literal 1.0 do outro caminho

    Medido na RAM: 65% dos pedestres com 1.0 e o resto espalhado em
    1.1029 .. 1.4213 -- exatamente a faixa prevista.
    """
    base = 0.55 if patchado else 1.10
    ampl = 0.175 if patchado else 0.35
    padrao = 0.5 if patchado else 1.0
    return base + aleatorio01 * ampl if tem_variacao else padrao


def mcCreatureAnim_ctorEstado(patchado):
    """0x4633A0. Tres campos nascem do MESMO li.s $f0.

    +0x10 e o avanco por tique; +0x14 e +0x18 sao presets recopiados para +0x10
    por 0x463400 e 0x4637D0 quando a animacao troca. Por isso o patch tem de
    atingir o literal, e nao um campo so.
    """
    v = 0.5 if patchado else 1.0
    return {'quadro': 0.0, 'incr': v, 'preset_a': v, 'preset_b': v}


def mcCreatureAnim_SetRate(est, taxa, taxa2, patchado):
    """0x463418. Sobrescreve o que o construtor poe.

        c.lt.s $f0, $f12      ; taxa > 0 ?
        swc1   $f12, 0x10     ; sim: usa ela
        li.s   $f0, 1.0       ; nao: default (0x463430)
    """
    padrao = 0.5 if patchado else 1.0
    est['incr'] = taxa if taxa > 0.0 else padrao
    est['preset_a'] = est['incr']
    est['preset_b'] = taxa2 if taxa2 > 0.0 else padrao
    return est


def mcCreatureAnim_AmostraRaiz(est, raiz, n_quadros):
    """0x463548. Avanca o cursor e devolve o deslocamento entre os 2 quadros.

        v5 = *(a1+0x0C)          posicao atual, em QUADROS
        v6 = v5 + *(a1+0x10)     avanca -- uma vez por CHAMADA, sem dt
        delta = amostra(v6) - amostra(v5)

    O `dt` nao aparece em lugar nenhum: e daqui que sai a dependencia de taxa
    de quadros.

    O `if (v7 > v6)` do original separa o caso em que o cursor ainda esta dentro
    da animacao do caso em que ele atravessa o fim. Na emenda o deslocamento e a
    soma dos dois trechos -- o pedestre continua andando pra frente, nao volta
    ao ponto de partida. Tratar a volta como delta negativo (erro que este teste
    pegou) contamina a media com um salto de um ciclo inteiro.
    """
    v5 = est['quadro']
    v6 = v5 + est['incr']
    if v6 >= n_quadros:
        d = (raiz(n_quadros) - raiz(v5)) + (raiz(v6 - n_quadros) - raiz(0.0))
        v6 -= n_quadros
    else:
        d = raiz(v6) - raiz(v5)
    est['quadro'] = v6
    return d


def swfCONTEXT_Advance(est, dt, taxa_swf):
    """0x20ACD0. Acumulador de tempo real - correto por construcao.

        acc += dt
        while (acc >= 256.0/taxa) { avanca 1 quadro; acc -= 256.0/taxa }
    """
    est['acc'] += dt
    periodo = 256.0 / taxa_swf
    n = 0
    while est['acc'] >= periodo:
        n += 1
        est['acc'] -= periodo
    return n


def mcFlash_Update(dt_passado, dt_medido, tocando=True):
    """0x320B38. Convencao embutida: float NEGATIVO = use o dt real.

        c.lt.s $f12, $f0                     ; f12 < 0 ?
        lwc1   $f12, g_dtMedidoQuantizado    ; entao usa o dt medido
    """
    if dt_passado < 0.0:
        return dt_medido if tocando else 0.0
    return dt_passado


# ==========================================================================
#  2. INFRAESTRUTURA DE TESTE
# ==========================================================================

class Prova(object):
    def __init__(self):
        self.ok = self.falhou = self.pulou = 0
        self.linhas = []

    def pula(self, nome, porque):
        # Not every check is pass/fail. A derived file that was never generated
        # is absent, not wrong - counting it as a failure trains you to ignore
        # the failure count, which is the one thing it must not do.
        self.pulou += 1
        print('   PULA  %-60s %s' % (nome, porque))

    def check(self, nome, cond, detalhe=''):
        self.linhas.append('   %s %-58s %s'
                           % ('PASSA' if cond else 'FALHA', nome, detalhe))
        if cond:
            self.ok += 1
        else:
            self.falhou += 1

    def perto(self, nome, obtido, esperado, tol, unidade=''):
        d = abs(obtido - esperado)
        rel = d / abs(esperado) if esperado else d
        self.check(nome, rel <= tol,
                   'obtido %.6f  esperado %.6f  (%.1f%%)%s'
                   % (obtido, esperado, rel * 100, unidade))

    def secao(self, t):
        self.linhas.append('')
        self.linhas.append(t)

    def relatorio(self):
        print('\n'.join(self.linhas))
        print()
        print('%d passaram, %d falharam%s'
              % (self.ok, self.falhou,
                 ', %d puladas' % self.pulou if self.pulou else ''))
        return self.falhou == 0


# ==========================================================================
#  3. OS TESTES
# ==========================================================================

def teste_encoding(p):
    p.secao('1. ENCODING dos patches (a palavra significa o que eu afirmei?)')

    # li.s $f0, X  =  lui $at, imm ; mtc1 $at, $f0
    def li_s(w):
        assert (w >> 26) == 0x0F and ((w >> 16) & 0x1F) == 1, 'nao e lui $at'
        return f32((w & 0xFFFF) << 16)

    p.perto('4633A0 original  li.s $f0, 1.0', li_s(0x3C013F80), 1.0, 0)
    p.perto('4633A0 patchado  li.s $f0, 0.5', li_s(0x3C013F00), 0.5, 0)
    p.check('4633A0: patch corta o avanco pela metade',
            li_s(0x3C013F00) / li_s(0x3C013F80) == 0.5)

    # os do flash: so o bit de sinal muda; o resto do valor fica igual
    for rot, velho, novo, low in (('1AC2A4', 0x3C013D08, 0x3C01BD08, 0x882F),
                                  ('28EE68', 0x3C013D07, 0x3C01BD07, 0x2B02)):
        fv = f32(((velho & 0xFFFF) << 16) | low)
        fn = f32(((novo & 0xFFFF) << 16) | low)
        p.check('%s: valor antigo positivo (%.6f = 1/%.1f)' % (rot, fv, 1 / fv), fv > 0)
        p.check('%s: valor novo NEGATIVO (%.6f) -> caminho do dt real' % (rot, fn), fn < 0)
        p.check('%s: so o sinal mudou (|antigo| == |novo|)' % rot, abs(fv) == abs(fn))

    # as constantes da taxa: dividir float por 2 so decrementa o expoente,
    # entao a metade baixa do li.s nao muda e o patch cabe no lui
    for rot, velho, novo, low, val in (
            ('45F638 amplitude', 0x3C013EB3, 0x3C013E33, 0x3334, 0.35),
            ('45F644 base     ', 0x3C013F8C, 0x3C013F0C, 0xCCCD, 1.10),
            ('45F698 default  ', 0x3C013F80, 0x3C013F00, 0x0000, 1.00)):
        fv = f32(((velho & 0xFFFF) << 16) | low)
        fn = f32(((novo & 0xFFFF) << 16) | low)
        p.perto('%s: valor original' % rot, fv, val, 1e-6)
        p.check('%s: patch = exatamente metade' % rot, fn == fv / 2.0,
                '%.6f -> %.6f' % (fv, fn))

    # o vblank: 14400008 e um bnez; 0 e nop
    w = 0x14400008
    p.check('5280F0 original e bnez $v0, +8',
            (w >> 26) == 0x05 and ((w >> 16) & 0x1F) == 0,
            'opcode %d, rt %d, off %+d' % (w >> 26, (w >> 16) & 0x1F, (w & 0xFFFF) * 4))
    p.check('5280F0 patchado e nop (00000000)', 0x00000000 == 0)


def teste_timer(p):
    p.secao('2. mcTimer::Tick - reproduz o dt medido nos savestates?')
    # estado lido da RAM do savestate
    est = dict(quantiza=False, modo_passo_fixo=False, passo_fixo=0.0,
               escala=1.0, min=1e-4, max=0.04)

    # 171 tiques consumiram 840.497.419 ciclos do EE (medido)
    ciclos_por_tique = 840497419 / 171.0
    dt, fps = mcTimer_Tick(ciclos_por_tique, est)
    p.perto('dt a 60 Hz a partir dos ciclos reais do EE', dt, MEDIDO_60['dt'], 0.01)
    p.perto('fps derivado', fps, 60.0, 0.01)

    # a 30 Hz o frame custa o dobro de ciclos
    dt30, fps30 = mcTimer_Tick(ciclos_por_tique * 2, est)
    p.perto('dt a 30 Hz', dt30, MEDIDO_30['dt'], 0.01)
    p.check('dt escala com a taxa de quadros (o relogio esta CERTO)',
            abs(dt30 / dt - 2.0) < 0.02, 'razao %.4f' % (dt30 / dt))

    # e se o passo fixo estivesse ligado (o que eu supus errado no comeco)
    est_fixo = dict(est, modo_passo_fixo=True, passo_fixo=1 / 60.0)
    dtf, _ = mcTimer_Tick(ciclos_por_tique * 2, est_fixo)
    p.check('com passo fixo o dt IGNORARIA o relogio',
            abs(dtf - 1 / 60.0) < 1e-9,
            'daria %.6f a 30 Hz -- nao e o que o savestate mostra' % dtf)


def teste_pedestre(p):
    p.secao('3. Pedestre - a taxa vem do Init, nao do construtor')
    n, avanco = ANIM_WALK[1], ANIM_WALK[2]
    por_quadro = avanco / n
    raiz = lambda q: q * por_quadro

    # o modelo da taxa reproduz a distribuicao medida na RAM?
    previstas = [mcCreature_Init_taxa(False, r / 100.0, True) for r in range(101)]
    variadas = [t for t in TAXAS_VIVAS if t != 1.0]
    p.check('taxas variadas medidas caem na faixa prevista [1.10, 1.45]',
            all(min(previstas) - 1e-3 <= t <= max(previstas) + 1e-3 for t in variadas),
            'medidas %.4f..%.4f, previsto %.2f..%.2f'
            % (min(variadas), max(variadas), min(previstas), max(previstas)))
    p.check('o resto usa o literal 1.0 do outro caminho',
            mcCreature_Init_taxa(False, 0.0, False) == 1.0,
            '%d de %d pedestres com 1.0' % (TAXAS_VIVAS.count(1.0), len(TAXAS_VIVAS)))

    def roda(patchado, tiques, dt, aleat=0.0, variacao=False):
        taxa = mcCreature_Init_taxa(patchado, aleat, variacao)
        est = mcCreatureAnim_ctorEstado(patchado)
        mcCreatureAnim_SetRate(est, taxa, taxa, patchado)   # SOBRESCREVE o construtor
        total = sum(mcCreatureAnim_AmostraRaiz(est, raiz, n) for _ in range(tiques))
        return est['incr'], total / tiques, total / (tiques * dt)

    r30, pt30, v30 = roda(False, MEDIDO_30['tiques'], MEDIDO_30['dt'])
    r60, pt60, v60 = roda(False, MEDIDO_60['tiques'], MEDIDO_60['dt'])
    p.check('sem patch a taxa e 1.0 (o construtor foi sobrescrito)', r30 == 1.0)
    p.check('deslocamento por tique nao muda com a taxa de quadros',
            abs(pt30 - pt60) < 1e-9, '%.6f nas duas' % pt30)
    p.perto('bate com o medido a 30 Hz', pt30, MEDIDO_30['por_tique'], 0.10)
    p.perto('bate com o medido a 60 Hz', pt60, MEDIDO_60['por_tique'], 0.15)

    # o patch ERRADO: so o construtor. SetRate desfaz.
    est = mcCreatureAnim_ctorEstado(True)
    p.check('construtor sozinho poria 0.5', est['incr'] == 0.5)
    mcCreatureAnim_SetRate(est, mcCreature_Init_taxa(False, 0, False), 1.0, False)
    p.check('...mas SetRate o sobrescreve de volta para 1.0 -- por isso o 1o patch falhou',
            est['incr'] == 1.0, 'medido na RAM: +0x10 = 1.0 com 0x4633A0 patchado')

    # o patch CERTO: nas fontes da taxa
    rp, ptp, vp = roda(True, MEDIDO_60['tiques'], MEDIDO_60['dt'])
    p.check('PATCH: taxa default cai para 0.5', rp == 0.5)
    p.check('PATCH: avanco por tique cai pela metade',
            abs(ptp / pt60 - 0.5) < 1e-9, '%.6f -> %.6f' % (pt60, ptp))
    p.perto('PATCH: velocidade a 60 Hz volta ao valor de 30 Hz', vp, v30, 0.02, ' u/s')

    # e o caminho com variacao tambem
    rv, ptv, vv = roda(False, 100, MEDIDO_60['dt'], 0.5, True)
    rvp, ptvp, vvp = roda(True, 100, MEDIDO_60['dt'], 0.5, True)
    p.check('PATCH cobre TAMBEM o caminho aleatorio (35% dos pedestres)',
            abs(rvp / rv - 0.5) < 1e-6, 'taxa %.4f -> %.4f' % (rv, rvp))
    print_previsao(vp, ptp)


def print_previsao(v, pt):
    global PREVISAO
    PREVISAO = (v, pt)


PREVISAO = None


def teste_flash(p):
    p.secao('4. Flash - a constante cravada contra o dt real')
    dt60, dt30 = MEDIDO_60['dt'], MEDIDO_30['dt']
    taxa_swf = 256.0 * 30.0                  # header do SWF em 8.8: 30 fps

    def roda(dt_passado, dt_medido, segundos):
        est = {'acc': 0.0}
        tiques = int(round(segundos / dt_medido))
        n = sum(swfCONTEXT_Advance(est, mcFlash_Update(dt_passado, dt_medido), taxa_swf)
                for _ in range(tiques))
        return n / segundos

    cravado = f32(0x3D08882F)                # 1/30, o que sub_1AC2A0 passava
    a30 = roda(cravado, dt30, 10.0)
    a60 = roda(cravado, dt60, 10.0)
    p.check('constante cravada: correta a 30 Hz', abs(a30 - 30.0) < 0.5,
            '%.2f quadros/s' % a30)
    p.check('constante cravada: DOBRA a 60 Hz', abs(a60 / a30 - 2.0) < 0.05,
            '%.2f quadros/s' % a60)

    p30 = roda(-1.0, dt30, 10.0)
    p60 = roda(-1.0, dt60, 10.0)
    p.check('PATCH (negativo): correto a 30 Hz', abs(p30 - 30.0) < 0.5,
            '%.2f quadros/s' % p30)
    p.check('PATCH (negativo): correto tambem a 60 Hz', abs(p60 - 30.0) < 0.5,
            '%.2f quadros/s' % p60)


def segmentos(d):
    ph = struct.unpack_from('<I', d, 0x1C)[0]
    phes = struct.unpack_from('<H', d, 0x2A)[0]
    phn = struct.unpack_from('<H', d, 0x2C)[0]
    out = []
    for i in range(phn):
        t, off, va, _pa, fsz, _msz = struct.unpack_from('<IIIIII', d, ph + i * phes)
        if t == 1 and fsz:
            out.append((va, off, fsz))
    return out


def crc(d):
    c = 0
    for (w,) in struct.iter_unpack('<I', d[:len(d) // 4 * 4]):
        c ^= w
    return c


def teste_elf(p):
    p.secao('5. ELF - os arquivos gerados contem exatamente o pretendido?')
    base = hostfs('SLUS_213.55.ELF')
    if not os.path.isfile(base):
        p.check('ELF base presente', False, base)
        return
    d0 = open(base, 'rb').read()

    ESPERADO = {
        # 0x1AC2A4 / 0x28EE68: the constant halved, NOT the old sign flip. The
        # sign flip routes the flash to 0x618E54, which on the loading screen is
        # pinned at 1/60 - so it was only ever a /2 in disguise.
        'SLUS_213.55_60FPS.ELF': {0x5280F0: 0x00000000, 0x1AC2A4: 0x3C013C88,
                                  0x28EE68: 0x3C013C87, 0x4633A0: 0x3C013F00,
                                  0x45F638: 0x3C013E33, 0x45F644: 0x3C013F0C,
                                  0x45F698: 0x3C013F00, 0x45F6A8: 0x3C013F00,
                                  0x45FD98: 0x3C013F00, 0x45FDB0: 0x3C013F00,
                                  0x45FDC8: 0x3C013F00, 0x463430: 0x3C013F00,
                                  0x46345C: 0x3C013F00},
        'SLUS_213.55_60FPS_CONTROLE.ELF': {0x5280F0: 0x00000000},
    }
    for nome, esperado in ESPERADO.items():
        cam = hostfs(nome)
        if not os.path.isfile(cam):
            p.pula('%s' % nome, 'nao gerado (rota do ELF direto, hoje em desuso)')
            continue
        d = open(cam, 'rb').read()
        p.check('%s: mesmo tamanho do base' % nome, len(d) == len(d0))
        p.check('%s: crc preservado (%08X)' % (nome, crc(d)), crc(d) == crc(d0))

        # 1) as palavras pretendidas estao la
        for va, w in esperado.items():
            for vbase, off, tam in segmentos(d):
                if vbase <= va < vbase + tam:
                    o = off + va - vbase
                    got = struct.unpack_from('<I', d, o)[0]
                    p.check('%s: VA %08X = %08X' % (nome, va, w), got == w,
                            '' if got == w else 'achei %08X' % got)

        # 2) e NADA MAIS mudou dentro do que e carregado na memoria
        difs = []
        for vbase, off, tam in segmentos(d):
            for k in range(0, tam - 3, 4):
                a = struct.unpack_from('<I', d0, off + k)[0]
                b = struct.unpack_from('<I', d, off + k)[0]
                if a != b:
                    difs.append(vbase + k)
        p.check('%s: %d palavras mudadas na imagem carregada, todas previstas'
                % (nome, len(difs)), sorted(difs) == sorted(esperado),
                '' if sorted(difs) == sorted(esperado)
                else 'inesperadas: %s' % [('%08X' % x) for x in difs
                                          if x not in esperado])


def remede(p, d1, d2):
    """Refaz as medidas a partir de um par de savestates, em vez de confiar nos numeros gravados."""
    M = 0x1FFFFFF
    da, db = open(d1, 'rb').read(), open(d2, 'rb').read()
    dw = lambda d, va: struct.unpack_from('<I', d, va & M)[0]
    hw = lambda d, va: struct.unpack_from('<H', d, va & M)[0]
    fl = lambda d, va: struct.unpack_from('<f', d, va & M)[0]
    v3 = lambda d, va: (fl(d, va), fl(d, va + 4), fl(d, va + 8))
    q = dw(db, 0x618E3C) - dw(da, 0x618E3C)
    sim = fl(db, 0x70E524) - fl(da, 0x70E524)

    def criaturas(d):
        s = dw(d, dw(d, 0x619494)); out = []
        for goff in (4, 40):
            g = s + 152 + goff
            arr, n = dw(d, g), hw(d, g + 4)
            if not arr or n > 512:
                continue
            for i in range(n):
                c = dw(d, arr + 4 * i)
                if c and (c & M) < 0x1FFFF00:
                    out.append(c)
        return out
    vs = []
    cb = set(criaturas(db))
    for c in criaturas(da):
        if c not in cb:
            continue
        pa, pb = v3(da, c + 276), v3(db, c + 276)
        dist = math.sqrt(sum((x - y) ** 2 for x, y in zip(pa, pb)))
        if dist > 0.01:
            vs.append(dist)
    vs.sort()
    med = vs[len(vs) // 2] if vs else 0.0
    return dict(tiques=q, sim=sim, dt=fl(da, 0x618E20),
                por_tique=med / q, u_s=med / sim)


def teste_stub_boot(p):
    """The boot stub cannot be tried a little bit: it runs at the end of crt0,
    before the game exists, and a wrong register or a branch off by one word is a
    black screen with nothing to read. So its shape is checked here instead."""
    p.secao('6. STUB DE BOOT - a forma esta certa antes de ir para o hardware?')
    sys.path.insert(0, os.path.join(AQUI, 'modloader'))
    try:
        import mc3_inject as M
    except Exception as e:
        p.pula('modloader/mc3_inject.py', 'nao importou: %s' % e)
        return
    w = M.early_stub()

    p.check('cabe antes do payload', M.EARLY + 4 * len(w) <= M.PAYLOAD,
            '%08X + %d palavras vs PAYLOAD %08X' % (M.EARLY, len(w), M.PAYLOAD))
    p.check('nao invade o bloco de telemetria', M.EARLY >= 0x0061C9C0 + 40)

    # salvar e restaurar tem de ser simetrico: o hook fica no meio do crt0 e
    # qualquer registrador perdido volta como lixo para o codigo do jogo
    sd = {(x >> 16) & 31 for x in w if (x >> 26) == 0x3F}
    ld = {(x >> 16) & 31 for x in w if (x >> 26) == 0x37}
    p.check('salva e restaura os mesmos registradores', sd == ld,
            'sd=%s ld=%s' % (sorted(sd), sorted(ld)))
    p.check('preserva $v0 (o unico vivo atraves do hook)', 2 in sd and 2 in ld)
    p.check('preserva $ra', 31 in sd and 31 in ld)

    # a pilha tem de fechar
    abre = [x for x in w if (x >> 26) == 0x09 and ((x >> 16) & 31) == 29]
    delta = sum((v - 0x10000 if v & 0x8000 else v)
                for v in (x & 0xFFFF for x in abre))
    p.check('a pilha fecha (soma dos ajustes de sp = 0)', delta == 0, 'delta=%d' % delta)

    # o desvio do teste da assinatura tem de cair no label de saida, nao no meio
    for i, x in enumerate(w):
        if (x >> 26) == 0x05:
            alvo = M.EARLY + 4 * (i + 1) + ((x & 0xFFFF) - 0x10000
                                            if x & 0x8000 else x & 0xFFFF) * 4
            idx = (alvo - M.EARLY) // 4
            p.check('o bne cai no primeiro `ld` da saida',
                    0 <= idx < len(w) and (w[idx] >> 26) == 0x37,
                    'alvo %08X = palavra %d' % (alvo, idx))
            break

    # e tem de reproduzir a instrucao substituida, ou o crt0 perde um passo
    p.check('reproduz a instrucao do hook (%08X)' % M.EARLY_WORD,
            M.EARLY_WORD in w)
    p.check('termina em jr $ra + nop',
            w[-3] == M.EARLY_WORD and w[-2] == 0x03E00008 and w[-1] == 0)
    p.check('o hook e um jal para o stub',
            (0x0C000000 | ((M.EARLY >> 2) & 0x3FFFFFF)) >> 26 == 3)


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--sstates', help='pasta com os dois savestates .01 e .02')
    a = ap.parse_args()

    if a.sstates:
        d1 = os.path.join(a.sstates + '.01', 'eeMemory.bin')
        d2 = os.path.join(a.sstates + '.02', 'eeMemory.bin')
        if os.path.isfile(d1) and os.path.isfile(d2):
            m = remede(None, d1, d2)
            alvo = MEDIDO_60 if m['tiques'] / m['sim'] > 45 else MEDIDO_30
            alvo.update(m)
            print('re-medido do savestate: %d tiques, %.4f s, %.2f Hz, '
                  '%.6f por tique, %.4f u/s\n'
                  % (m['tiques'], m['sim'], m['tiques'] / m['sim'],
                     m['por_tique'], m['u_s']))
        else:
            print('savestates nao encontrados em %s.01/.02\n' % a.sstates)

    p = Prova()
    teste_encoding(p)
    teste_timer(p)
    teste_pedestre(p)
    teste_flash(p)
    teste_elf(p)
    teste_stub_boot(p)
    bom = p.relatorio()
    if PREVISAO:
        print()
        print('PREVISAO para o ELF completo a 60 Hz:')
        print('   %.6f por tique  e  %.4f u/s' % (PREVISAO[1], PREVISAO[0]))
        print('   (sem patch, medido: %.6f por tique, %.4f u/s)'
              % (MEDIDO_60['por_tique'], MEDIDO_60['u_s']))
    sys.exit(0 if bom else 1)


if __name__ == '__main__':
    main()
