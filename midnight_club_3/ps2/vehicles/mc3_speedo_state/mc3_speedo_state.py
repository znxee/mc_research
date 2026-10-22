"""mc3_speedo_state.py - read digital_speedometer.mod's state out of a savestate

The module keeps one struct behind its `state()` accessor, stamped with the
magic 'SHPK' so it can be found without knowing where the loader relocated the
module to. Everything the overlay decided is in there, which makes a savestate a
complete diagnosis: whether the font resolved, whether the three gauge redirects
were installed, and - the reason this file exists - whether the backing plate's
texture ever loaded.

    python mc3_speedo_state.py "X:/Documents/PCSX2/sstates/SLUS-21355 (B3FD5361).01.p2s"
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'modloader'))
import mc3_inject  # noqa: E402

MAGIC = 0x4B504853          # 'SHPK'

# Field order from digital_speedometer_state. Keep in sync with the .cpp.
FIELDS = ('magic', 'hook_calls', 'font_attempts', 'draw_calls', 'digital_font',
          'old_speedometer_disabled', 'old_tachometer_redirected',
          'old_gear_redirected', 'last_kilometres_per_hour', 'last_digits',
          'tachometer_calls', 'tachometer_draw_calls', 'last_rpm', 'last_gear',
          'badge_tex', 'badge_image', 'badge_attempts', 'badge_draws')
NAME_OFF = len(FIELDS) * 4          # char badge_name_buf[24]
FONT_OFF = NAME_OFF + 24            # char font_name_buf[16]


def find(ee):
    alvo = struct.pack('<I', MAGIC)
    out, i = [], 0
    while True:
        i = ee.find(alvo, i)
        if i < 0:
            return out
        if i % 4 == 0:
            out.append(i)
        i += 4


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    ee = mc3_inject.ee_from_savestate(argv[1])
    achados = find(ee)
    if not achados:
        print('nao achei o estado (magic SHPK). O mod rodou nesse savestate?')
        return 1

    a = achados[0]
    v = {n: struct.unpack_from('<I', ee, a + k * 4)[0]
         for k, n in enumerate(FIELDS)}
    print('digital_speedometer @ %08X' % a)
    print('  quadros           %d hook, %d desenhos' % (v['hook_calls'],
                                                        v['draw_calls']))
    print('  fonte             %08X  (%d tentativa(s))'
          % (v['digital_font'], v['font_attempts']))
    print('  redirects         velocimetro %d, tacometro %d, marcha %d'
          % (v['old_speedometer_disabled'], v['old_tachometer_redirected'],
             v['old_gear_redirected']))
    print('  leituras          %d km/h, %d rpm, marcha %d'
          % (v['last_kilometres_per_hour'], v['last_rpm'], v['last_gear']))
    nome = ee[a + NAME_OFF:a + NAME_OFF + 24].split(b'\0')[0]
    print('  placa             image %08X -> tex %08X'
          % (v['badge_image'], v['badge_tex']))
    print('                    %d tentativa(s), %d desenho(s)'
          % (v['badge_attempts'], v['badge_draws']))
    print('                    nome pedido: %r' % nome.decode('latin-1'))

    # The three states worth telling apart, because each has its own cause.
    if v['badge_tex'] and v['badge_draws']:
        print('  -> a placa carregou E desenhou. Se nao aparece na tela, o'
              ' problema e o blit: retangulo, UV ou estado de render.')
    elif v['badge_tex']:
        print('  -> carregou mas NAO desenhou: draw_badge saiu antes do blit,'
              ' ou o ponteiro nao passou em valid_game_pointer.')
    elif v['badge_image']:
        print('  -> a imagem carregou mas gfxSimpleTex::Create nao deu textura.')
    elif v['badge_attempts']:
        print('  -> gfxLoadImageAll devolveu 0 em %d tentativa(s): e o NOME ou'
              ' o arquivo, nao o desenho.' % v['badge_attempts'])
        print('     gfxLoadTexImage ja pede `texture/<nome>.tex` sozinho - os'
              ' globais off_61C288/off_61C290 valem "texture" e "tex" - entao o'
              ' nome tem de ser o BASENAME puro, sem pasta e sem extensao.')
        print('     pedido: %r' % nome.decode('latin-1'))
    else:
        print('  -> nem tentou carregar: draw_badge nao foi chamado.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
