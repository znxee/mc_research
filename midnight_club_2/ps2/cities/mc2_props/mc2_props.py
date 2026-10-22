"""mc2_props.py - inventario dos props de uma cidade do Midnight Club 2.

Os props do MC2 nao vivem nos .hood: eles tem um arquivo proprio,
<cidade>.prop, com tres partes em TEXTO:

    prop_count / fixed_prop_count / gfx_prop_count / num_prop_types
    prop_template <nome> { animation numparts FixedObject Obstacle
                           GfxOnly Drivable Far }        -- um por TIPO
    prop <n> { matrix { 4 linhas de 3 floats } prop_template: <nome> }

A matriz e a mesma Matrix34 do resto do porte: tres linhas de rotacao e uma
de translacao. Cada tipo tambem tem um .pdef ao lado (name, lods, sphere) e
modelos <nome>_<lod>.xmod na pasta models.

Uso:
    python mc2_props.py --cidade <.../city/losangeles> --saida output/la_props
"""
import argparse
import collections
import json
import os
import re


def le_prop(caminho):
    """(cabecalho, tipos, colocacoes) do <cidade>.prop.

    Dois detalhes que so aparecem lendo o arquivo inteiro:

    - Ha TRES listas de colocacao, cada uma renumerando a partir de zero: as
      normais (prop_count), as fixas (fixed_prop_count) e as so-grafico
      (gfx_prop_count). Um `prop 0` depois do primeiro abre a lista seguinte.
    - Um template com `numparts` maior que zero contem blocos `part N { name,
      offset }` ANINHADOS, e as flags (FixedObject, Obstacle, GfxOnly,
      Drivable, Far) vem DEPOIS deles. Fechar o template no primeiro `}` perde
      as flags de 59 dos 96 tipos de LA, e elas saem como desconhecidas em vez
      de dar erro - por isso a profundidade de chaves e contada.
    """
    cab, tipos, colocacoes = {}, {}, []
    nome_atual = None
    matriz = None
    prof = 0
    parte = None
    secoes = ['normal', 'fixed', 'gfx']
    secao = 0
    visto_zero = False
    for linha in open(caminho, encoding='latin1'):
        t = linha.strip()
        if not t:
            continue
        if t == '}':
            prof = max(0, prof - 1)
            if prof == 0:
                nome_atual = None
                matriz = None
            elif prof == 1:
                parte = None
            continue
        if t.endswith('{'):
            prof += 1
            g = re.match(r'^prop_template\s+(\S+)\s*\{', t)
            if g:
                nome_atual = g.group(1)
                tipos[nome_atual] = {'partes': []}
                continue
            g = re.match(r'^prop\s+(\d+)\s*\{', t)
            if g:
                if int(g.group(1)) == 0:
                    if visto_zero:
                        secao += 1
                    visto_zero = True
                matriz = []
                continue
            if re.match(r'^part\s+\d+\s*\{', t) and nome_atual:
                parte = {}
                tipos[nome_atual]['partes'].append(parte)
            continue
        g = re.match(r'^(prop_count|fixed_prop_count|gfx_prop_count|'
                     r'num_prop_types):\s*(\d+)', t)
        if g:
            cab[g.group(1)] = int(g.group(2))
            continue
        g = re.match(r'^prop_template:\s*(\S+)', t)
        if g and matriz is not None:
            colocacoes.append((g.group(1),
                               matriz[-4:] if len(matriz) >= 4 else matriz,
                               secoes[min(secao, len(secoes) - 1)]))
            matriz = None
            continue
        g = re.match(r'^(\w+):\s*(.+?)\s*$', t)
        if g and nome_atual:
            campo, valor = g.group(1), g.group(2)
            if parte is not None:
                parte[campo] = valor
            else:
                tipos[nome_atual][campo] = valor
            continue
        if matriz is not None:
            n = t.split()
            if len(n) == 3:
                try:
                    matriz.append(tuple(float(v) for v in n))
                except ValueError:
                    pass
    return cab, tipos, colocacoes


def le_pdef(caminho):
    """name / lods / sphere de um .pdef."""
    fora = {}
    for linha in open(caminho, encoding='latin1'):
        t = linha.strip()
        g = re.match(r'^name:\s*(\S+)', t)
        if g:
            fora['name'] = g.group(1)
        g = re.match(r'^lods:\s*(\d+)\s*:\s*([\d ]*)', t)
        if g:
            fora['n_lods'] = int(g.group(1))
            fora['lods'] = [int(v) for v in g.group(2).split()]
        g = re.match(r'^sphere:\s*(.+)', t)
        if g:
            v = g.group(1).split()
            if len(v) == 4:
                fora['sphere'] = [float(x) for x in v]
    return fora


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--cidade', required=True, help='pasta .../city/<nome>')
    p.add_argument('--saida', required=True, help='prefixo dos arquivos de saida')
    a = p.parse_args(argv)

    nome_cidade = os.path.basename(a.cidade.rstrip('/\\'))
    prop = os.path.join(a.cidade, nome_cidade + '.prop')
    modelos = os.path.join(a.cidade, 'models')
    cab, tipos, colocacoes = le_prop(prop)
    print('%s.prop: %s' % (nome_cidade, cab))
    print('  templates lidos: %d   colocacoes lidas: %d' % (len(tipos), len(colocacoes)))

    disponiveis = {f.lower() for f in os.listdir(modelos)} if os.path.isdir(modelos) else set()
    usos = collections.Counter(n.lower() for n, _, _ in colocacoes)
    por_secao = collections.Counter(s for _, _, s in colocacoes)
    print('  por secao: %s' % dict(por_secao))

    linhas = []
    for nome in sorted(tipos):
        t = tipos[nome]
        pdef = os.path.join(a.cidade, nome + '.pdef')
        d = le_pdef(pdef) if os.path.isfile(pdef) else {}
        lods = d.get('lods', [])
        achados = [l for l in lods
                   if ('%s_%d.xmod' % (nome, l)).lower() in disponiveis]
        linhas.append({
            'nome': nome,
            'instancias': usos.get(nome.lower(), 0),
            'FixedObject': t.get('FixedObject', '?'),
            'Obstacle': t.get('Obstacle', '?'),
            'GfxOnly': t.get('GfxOnly', '?'),
            'Drivable': t.get('Drivable', '?'),
            'Far': t.get('Far', '?'),
            'animation': t.get('animation', '?'),
            'numparts': t.get('numparts', '?'),
            'pdef': os.path.isfile(pdef),
            'lods_declarados': lods,
            'lods_com_xmod': achados,
            'raio': round(d['sphere'][3], 2) if 'sphere' in d else None,
        })

    tsv = a.saida + '_tipos.tsv'
    with open(tsv, 'w', encoding='utf-8', newline='\n') as f:
        cols = ['nome', 'instancias', 'FixedObject', 'Obstacle', 'GfxOnly',
                'Drivable', 'Far', 'animation', 'numparts', 'pdef',
                'lods_declarados', 'lods_com_xmod', 'raio']
        f.write('\t'.join(cols) + '\n')
        for r in sorted(linhas, key=lambda x: -x['instancias']):
            f.write('\t'.join(str(r[c]) for c in cols) + '\n')

    js = a.saida + '_colocacao.json'
    json.dump([{'tipo': n, 'secao': s, 'matriz': m} for n, m, s in colocacoes],
              open(js, 'w'), indent=0)

    print('  -> %s' % tsv)
    print('  -> %s (%d colocacoes)' % (js, len(colocacoes)))

    # conferencia contra o que o proprio arquivo declara
    if cab.get('num_prop_types') != len(tipos):
        print('  AVISO: num_prop_types diz %s, li %d'
              % (cab.get('num_prop_types'), len(tipos)))
    esperado = {'normal': cab.get('prop_count'),
                'fixed': cab.get('fixed_prop_count'),
                'gfx': cab.get('gfx_prop_count')}
    for k, v in esperado.items():
        if v is not None and por_secao.get(k, 0) != v:
            print('  AVISO: %s_count diz %s, li %d' % (k, v, por_secao.get(k, 0)))
    sem_modelo = [r['nome'] for r in linhas if not r['lods_com_xmod']]
    sem_pdef = [r['nome'] for r in linhas if not r['pdef']]
    nunca = [r['nome'] for r in linhas if r['instancias'] == 0]
    print('  tipos sem nenhum .xmod: %d %s' % (len(sem_modelo), sem_modelo[:6]))
    print('  tipos sem .pdef:        %d %s' % (len(sem_pdef), sem_pdef[:6]))
    print('  tipos nunca colocados:  %d %s' % (len(nunca), nunca[:6]))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
