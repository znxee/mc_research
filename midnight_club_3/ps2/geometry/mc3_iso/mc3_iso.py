"""Poe arquivos soltos na raiz de uma ISO de PS2 sem remonta-la.

Serve para levar o modloader para hardware real. No PCSX2 os arquivos ficam
soltos no HostFS; num PS2 de verdade nao ha HostFS, e o mc3boot procura cada
arquivo em host0: -> cdrom0: -> mass0:. Com tudo dentro da ISO o cdrom0:
responde, e o mesmo binario roda nos dois lugares.

POR QUE NAO REMONTAR A ISO. A imagem do MC3 tem 7,95 GB e nao ha remontador no
toolkit. Mas ela tem folga onde interessa, e isto foi MEDIDO nesta imagem:

    diretorio raiz   LBA 261, 732 bytes usados de um setor -> 1316 livres
    lacuna livre     LBA 9702, 445062 setores (869 MB) zerados
    descritores      so o primario, sem Joliet - um lugar so para atualizar

Entao da para escrever os arquivos numa lacuna, acrescentar os registros de
diretorio no espaco que sobra do setor da raiz, e corrigir o tamanho da raiz nos
dois lugares onde ele aparece. Nada se move e o arquivo nao muda de tamanho.

AVISO: a imagem do MC3 tem DOIS volumes ISO concatenados - o segundo comeca no
setor 2084960, com o seu proprio CD001. Este script so mexe no primeiro e nunca
escreve alem do volume declarado no PVD.

    python mc3_iso.py <iso> --add mc3boot.elf --add mc3mod.bin --aplicar

Sem --aplicar ele so relata o que faria, e mesmo com --aplicar ele confere que
os setores de destino estao zerados antes de escrever um byte.
"""
import argparse
import os
import struct

SETOR = 2048
PVD_LBA = 16


def nome_iso(base):
    """core.mod -> CORE.MOD;1. ISO9660 nivel 1: 8.3, maiusculo."""
    raiz, ext = os.path.splitext(os.path.basename(base))
    def limpa(s):
        return ''.join(c if (c.isalnum() or c == '_') else '_' for c in s.upper())
    return '%s.%s;1' % (limpa(raiz)[:8], limpa(ext[1:])[:3])


def le_registros(d, tam):
    out = []
    i = 0
    while i < tam and i < len(d) and d[i]:
        out.append(bytes(d[i:i + d[i]]))
        i += d[i]
    return out


def faz_registro(nome, lba, tamanho):
    n = nome.encode('ascii')
    L = 33 + len(n)
    if L % 2:
        L += 1                                 # o registro tem comprimento PAR
    r = bytearray(L)
    r[0] = L
    struct.pack_into('<I', r, 2, lba)
    struct.pack_into('>I', r, 6, lba)          # o campo big-endian tambem
    struct.pack_into('<I', r, 10, tamanho)
    struct.pack_into('>I', r, 14, tamanho)
    r[25] = 0                                  # flags: arquivo comum
    struct.pack_into('<H', r, 28, 1)           # numero do volume
    struct.pack_into('>H', r, 30, 1)
    r[32] = len(n)
    r[33:33 + len(n)] = n
    return bytes(r)


def chave(reg):
    """A ordem que o ISO9660 exige: por nome, sem a versao."""
    return reg[33:33 + reg[32]].split(b';')[0]


def lacunas(f, total):
    """Setores livres dentro do volume declarado, medindo o que esta em uso."""
    usados = []

    def anda(lba, tam):
        ns = (tam + SETOR - 1) // SETOR
        usados.append((lba, lba + ns))
        f.seek(lba * SETOR)
        d = f.read(ns * SETOR)
        i = 0
        while i < len(d) and d[i]:
            nl = d[i + 32]
            elba = struct.unpack_from('<I', d, i + 2)[0]
            etam = struct.unpack_from('<I', d, i + 10)[0]
            if not (nl == 1 and d[i + 33] in (0, 1)):
                if d[i + 25] & 2:
                    anda(elba, etam)
                else:
                    usados.append((elba, elba + (etam + SETOR - 1) // SETOR))
            i += d[i]

    f.seek(PVD_LBA * SETOR)
    pvd = f.read(SETOR)
    r = pvd[156:190]
    anda(struct.unpack_from('<I', r, 2)[0], struct.unpack_from('<I', r, 10)[0])
    usados.sort()
    livres = []
    fim = 32
    for a, b in usados:
        if a > fim:
            livres.append((fim, a - fim))
        fim = max(fim, b)
    if fim < total:
        livres.append((fim, total - fim))
    return livres


def main():
    ap = argparse.ArgumentParser(
        description=__doc__.strip().splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('iso')
    ap.add_argument('--add', action='append', default=[], metavar='ARQ',
                    help='arquivo a por na raiz; o nome 8.3 sai do proprio nome')
    ap.add_argument('--como', action='append', default=[], metavar='NOME.EXT',
                    help='nome ISO para o --add na mesma posicao')
    ap.add_argument('--boot', metavar='NOME.ELF',
                    help='reescreve o BOOT2 do SYSTEM.CNF para este nome')
    ap.add_argument('--aplicar', action='store_true', help='grava de verdade')
    a = ap.parse_args()

    f = open(a.iso, 'r+b' if a.aplicar else 'rb')
    f.seek(PVD_LBA * SETOR)
    pvd = bytearray(f.read(SETOR))
    total = struct.unpack_from('<I', pvd, 80)[0]
    raiz_lba = struct.unpack_from('<I', pvd, 156 + 2)[0]
    raiz_tam = struct.unpack_from('<I', pvd, 156 + 10)[0]
    print('%s: volume %d setores, raiz LBA %d, %d bytes usados de %d'
          % (os.path.basename(a.iso), total, raiz_lba, raiz_tam, SETOR))
    if raiz_tam > SETOR:
        raise SystemExit('a raiz ocupa mais de um setor; este script nao cobre isso')

    f.seek(raiz_lba * SETOR)
    setor_raiz = bytearray(f.read(SETOR))
    regs = le_registros(setor_raiz, raiz_tam)
    existentes = set(chave(r) for r in regs)

    livres = [l for l in lacunas(f, total) if l[1] > 4]
    livres.sort(key=lambda x: -x[1])
    if not livres:
        raise SystemExit('nenhuma lacuna livre no volume')
    lba_livre, n_livres = livres[0]
    print('  lacuna escolhida: LBA %d, %d setores (%.1f MB)'
          % (lba_livre, n_livres, n_livres * SETOR / 2.0 ** 20))

    novos = []
    cursor = lba_livre
    for k, caminho in enumerate(a.add):
        if not os.path.isfile(caminho):
            raise SystemExit('nao achei %s' % caminho)
        nome = a.como[k] if k < len(a.como) else nome_iso(caminho)
        if ';' not in nome:
            nome += ';1'
        if nome.split(';')[0].encode('ascii') in existentes:
            raise SystemExit('%s ja existe na raiz da ISO' % nome)
        dados = open(caminho, 'rb').read()
        ns = (len(dados) + SETOR - 1) // SETOR
        if cursor + ns > lba_livre + n_livres:
            raise SystemExit('a lacuna nao cabe %s' % nome)
        novos.append((nome, cursor, dados))
        print('     %-22s -> %-14s LBA %-8d %8d bytes (%d setores)'
              % (os.path.basename(caminho), nome, cursor, len(dados), ns))
        cursor += ns

    todos = regs + [faz_registro(n, l, len(d)) for n, l, d in novos]
    todos.sort(key=chave)
    corpo = b''.join(todos)
    print('  raiz: %d bytes -> %d bytes (limite %d)' % (raiz_tam, len(corpo), SETOR))
    if len(corpo) > SETOR:
        raise SystemExit('os registros novos nao cabem no setor da raiz')

    cnf = None
    if a.boot:
        for r in regs:
            if chave(r) == b'SYSTEM.CNF':
                lba = struct.unpack_from('<I', r, 2)[0]
                tam = struct.unpack_from('<I', r, 10)[0]
                f.seek(lba * SETOR)
                velho = f.read(tam).decode('ascii', 'replace')
                linhas = []
                for ln in velho.splitlines():
                    if ln.upper().startswith('BOOT2'):
                        ln = 'BOOT2 = cdrom0:\\%s' % a.boot
                    linhas.append(ln)
                novo = ('\r\n'.join(linhas) + '\r\n').encode('ascii')
                cnf = (lba, novo)
                print('  SYSTEM.CNF: %d -> %d bytes, BOOT2 = cdrom0:\\%s'
                      % (tam, len(novo), a.boot))
                break
        if cnf is None:
            raise SystemExit('nao achei SYSTEM.CNF na raiz')

    if not a.aplicar:
        print('')
        print('  ENSAIO - nada foi gravado. Repita com --aplicar.')
        return

    for nome, lba, dados in novos:
        ns = (len(dados) + SETOR - 1) // SETOR
        f.seek(lba * SETOR)
        if any(f.read(ns * SETOR)):
            raise SystemExit('LBA %d nao esta vazio; abortei sem escrever nada' % lba)

    for nome, lba, dados in novos:
        f.seek(lba * SETOR)
        f.write(dados + bytes((-len(dados)) % SETOR))
    if cnf:
        lba, novo = cnf
        f.seek(lba * SETOR)
        f.write(novo + bytes(SETOR - len(novo)))
        for i, r in enumerate(todos):
            if chave(r) == b'SYSTEM.CNF':
                rb = bytearray(r)
                struct.pack_into('<I', rb, 10, len(novo))
                struct.pack_into('>I', rb, 14, len(novo))
                todos[i] = bytes(rb)
        corpo = b''.join(todos)

    novo_setor = bytearray(SETOR)
    novo_setor[:len(corpo)] = corpo
    struct.pack_into('<I', novo_setor, 10, len(corpo))     # o proprio "."
    struct.pack_into('>I', novo_setor, 14, len(corpo))
    f.seek(raiz_lba * SETOR)
    f.write(novo_setor)
    struct.pack_into('<I', pvd, 156 + 10, len(corpo))
    struct.pack_into('>I', pvd, 156 + 14, len(corpo))
    f.seek(PVD_LBA * SETOR)
    f.write(pvd)
    f.close()
    print('')
    print('  gravado.')


if __name__ == '__main__':
    main()
