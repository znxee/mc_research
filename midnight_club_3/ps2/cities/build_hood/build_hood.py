#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Monta a losangeles com um subconjunto de bairros de LA, reproduzindo a receita
da v9 (componentes locais + cadeia corrigida), e instala nas 9 variantes.

Uso:
    python build_hood.py l_downtown
    python build_hood.py l_downtown,l_ghetto          # cumulativo
    python build_hood.py l_downtown --so-monta         # so gera, nao instala

O .ppf, props, garage_props, fog, peds, traffic e bnd NAO sao tocados - o .ppf
ja e superset de LA inteira, entao cobre qualquer subconjunto de bairros.
"""
import argparse, os, subprocess, sys, shutil, hashlib

RAIZ = os.path.dirname(os.path.abspath(__file__))
PLACE = os.path.join(RAIZ, 'output', 'la729_place.tsv')
MODELOS = os.path.join(RAIZ, 'output', 'mc2_losangeles', 'model')
PCK_MALHA = os.path.join(RAIZ, 'output', 'city_v7_vif_relocation_20260906',
                         'la729_local_components_20260906')
TEXTURAS = os.path.join(RAIZ, 'output', 'la_tex_pck')
MAPA_ID = os.path.join(RAIZ, 'output', 'shader_texture_route_20260905',
                       'native_texture_map.tsv')
MAPA_TEX = os.path.join(RAIZ, 'output', 'la_texturas_por_modelo.json')
MANIF_PPF = os.path.join(RAIZ, 'output', 'shader_texture_route_20260905',
                         'candidate', 'losangeles_midnight_clear.manifest.json')
DOADOR = os.path.join(os.environ.get('MC3_HOSTFS', ''), 'ASSETS/resources/city/atlanta_midnight_clear.pck')
DESTINO = os.path.join(os.environ.get('MC3_HOSTFS', ''), 'ASSETS/resources/city')
VARIANTES = ['dawn_clear', 'dawn_cloudy', 'dawn_rainy',
             'dusk_clear', 'dusk_cloudy', 'dusk_rainy',
             'midnight_clear', 'midnight_cloudy', 'midnight_rainy']

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()

def filtra_place(hoods, saida):
    """Copia as 4 linhas de cabecalho + so as linhas dos hoods pedidos."""
    conj = set(hoods)
    linhas = open(PLACE, encoding='utf-8', errors='replace').read().splitlines()
    cab = linhas[:4]                      # comentarios + linha de colunas
    idx_hood = cab[3].split('\t').index('hood')
    corpo = []
    contagem = {}
    for ln in linhas[4:]:
        if not ln.strip():
            continue
        col = ln.split('\t')
        if len(col) <= idx_hood:
            continue
        h = col[idx_hood]
        if h in conj:
            corpo.append(ln)
            contagem[h] = contagem.get(h, 0) + 1
    with open(saida, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(cab) + '\n' + '\n'.join(corpo) + '\n')
    return contagem

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('hoods', help='nomes de hood separados por virgula (l_downtown,...)')
    ap.add_argument('--so-monta', action='store_true', help='nao instala nas 9 variantes')
    a = ap.parse_args()

    hoods = [h.strip() for h in a.hoods.split(',') if h.strip()]
    etiqueta = '_'.join(h.replace('l_', '') for h in hoods)
    place_tmp = os.path.join(RAIZ, 'output', 'hood_test_%s_place.tsv' % etiqueta)
    saida = os.path.join(RAIZ, 'output', 'losangeles_hood_%s.pck' % etiqueta)

    cont = filtra_place(hoods, place_tmp)
    if not cont:
        sys.exit('nenhuma linha para: %s' % hoods)
    print('bairros:', ', '.join('%s=%d' % (k, v) for k, v in sorted(cont.items())),
          '  total=%d' % sum(cont.values()))

    cmd = [sys.executable, os.path.join(RAIZ, 'mc3_city_build.py'),
           '--doador', DOADOR, '--place', place_tmp, '--modelos', MODELOS,
           '--pck-malha', PCK_MALHA, '--texturas', TEXTURAS,
           '--mapa-identidade', MAPA_ID, '--mapa-textura', MAPA_TEX,
           '--manifesto-ppf', MANIF_PPF, '--max-inst', '8511',
 '--saida', saida]
    print('>>', ' '.join('"%s"' % c if ' ' in c else c for c in cmd))
    r = subprocess.run(cmd)
    if r.returncode != 0 or not os.path.exists(saida):
        sys.exit('build falhou (rc=%d)' % r.returncode)
    print('gerado: %s  (%d bytes, sha %s)' % (saida, os.path.getsize(saida), sha(saida)[:8]))

    if a.so_monta:
        print('--so-monta: nao instalei.')
        return
    for v in VARIANTES:
        dst = os.path.join(DESTINO, 'losangeles_%s.pck' % v)
        shutil.copyfile(saida, dst)
    # confere
    alvo = sha(saida)
    ok = sum(1 for v in VARIANTES
             if sha(os.path.join(DESTINO, 'losangeles_%s.pck' % v)) == alvo)
    print('instalado em %d/9 variantes (hash conferido).' % ok)
    print('LEMBRETE: .ppf/props/peds/traffic/bnd intactos; reinicie sem savestate antigo.')

if __name__ == '__main__':
    main()
