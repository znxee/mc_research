"""Roda o PCSX2 pela linha de comando e devolve o que o console do EE/IOP disse.

Fecha o laço de iteração sem savestate: monta o arquivo, roda, le o log,
corrige, repete. Antes disso cada rodada custava um boot manual do usuario.

O QUE FOI PRECISO, e as duas coisas foram medidas e nao supostas:

  * O CAMINHO PRECISA DE BARRA INVERTIDA. Com 'Y:/MC3HostFS/mc3boot.elf' o
    PCSX2 responde "Requested filename does not exist" mesmo com o arquivo la;
    com 'Y:\\MC3HostFS\\mc3boot.elf' ele carrega.
  * O CONSOLE DO EE VEM DESLIGADO. No PCSX2.ini, EnableEEConsole e
    EnableIOPConsole nascem false e EnableFileLogging ja e true - ligando os
    dois, tudo que o EE e o IOP imprimem cai no arquivo de log.

O que isso da de graca, e e o achado que mais vale: o console do IOP loga CADA
`open`. Num boot do modloader saem as oito linhas na ordem - mc3mod.bin, o ELF
do jogo, mc3boot.ini e cada .mod marcado '= 1'. Da para ver o que o carregador
abriu, com que flag e em que ordem, sem tirar savestate.

RESSALVA: o relatorio do proprio mc3boot NAO aparece aqui. Ele usa scr_printf,
que escreve no framebuffer da tela, e nao printf, que vai para o console. Um
mod que queira ser lido por esta ferramenta tem que usar o console.

    python mc3_pcsx2.py --elf Y:\\MC3HostFS\\mc3boot.elf --segundos 40
"""
import argparse
import os
import re
import subprocess
import sys
import time

PCSX2 = os.path.join(os.environ.get('MC3_PCSX2_DIR', ''), 'pcsx2-qt.exe')
INI = os.path.join(os.environ.get('MC3_PCSX2_DATA', ''), 'inis/PCSX2.ini')
LOG = os.path.join(os.environ.get('MC3_PCSX2_DATA', ''), 'logs/cli_teste.txt')

# O que vale a pena mostrar de um log de 600 linhas.
INTERESSE = re.compile(
    r'open name|ELF Loading|Disc override|Error|error|EE DECI2|'
    r'is executing|Loaded,|failed|Exception|assert', re.I)


def console_ligado(caminho):
    """(ee, iop) - os dois toggles nascem false num PCSX2 novo."""
    if not os.path.isfile(caminho):
        return None, None
    s = open(caminho, encoding='utf-8', errors='replace').read()
    return ('EnableEEConsole = true' in s, 'EnableIOPConsole = true' in s)


PERFIL_DEBUG = r'Y:	emp\pcsx2_debug'


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument('--elf', default=os.path.join(os.environ.get('MC3_HOSTFS', ''), 'mc3boot.elf'),
                    help='caminho do ELF; PRECISA de barra invertida')
    ap.add_argument('--segundos', type=float, default=40.0)
    ap.add_argument('--log', default=LOG)
    ap.add_argument('--tudo', action='store_true', help='imprime o log inteiro')
    ap.add_argument('--debug', action='store_true',
                    help='usa o perfil Y:/temp/pcsx2_debug: pausa no primeiro '
                         'TLB Miss, abre o debugger e carrega os simbolos do '
                         'ELF de debug. NAO serve para medir excecoes - com '
                         'PauseOnTLBMiss o PCSX2 pausa a VM e NAO escreve a '
                         'linha no log (o Console.Error fica no ramo else de '
                         'vtlb.cpp), entao a contagem sai zerada.')
    a = ap.parse_args()

    ee, iop = console_ligado(INI)
    if ee is False or iop is False:
        print('  AVISO: console do %s desligado no PCSX2.ini - o log vai sair mudo'
              % (' e '.join([n for n, v in (('EE', ee), ('IOP', iop)) if not v])))

    if os.path.exists(a.log):
        os.remove(a.log)
    cmd = [PCSX2]
    if a.debug:
        # -datapath troca o diretorio de dados inteiro, entao o perfil de debug
        # tem o proprio PCSX2.ini sem contaminar o normal. BIOS e memory cards
        # ja sao caminhos absolutos e os savestates apontam para os mesmos.
        cmd += ['-datapath', PERFIL_DEBUG, '-debugger']
    else:
        cmd += ['-batch', '-nogui']
    cmd += ['-logfile', a.log, '--', a.elf]
    t0 = time.time()
    p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        p.wait(timeout=a.segundos)
        motivo = 'saiu sozinho'
    except subprocess.TimeoutExpired:
        p.kill()
        p.wait()
        motivo = 'encerrado no tempo'
    print('  %s em %.1fs' % (motivo, time.time() - t0))

    if not os.path.isfile(a.log):
        raise SystemExit('nao gerou log em %s' % a.log)
    linhas = open(a.log, encoding='utf-8', errors='replace').read().splitlines()
    print('  log: %d linhas' % len(linhas))
    for l in linhas:
        if a.tudo or INTERESSE.search(l):
            print('   ' + l[:160])


if __name__ == '__main__':
    main()
