"""Tira um savestate do PCSX2 sozinho, via PINE.

Reescrito depois de uma primeira versao falhar: o erro foi REABRIR o socket a
cada tentativa. O servidor PINE (Y:/pcsx2-master/pcsx2/PINE.cpp, MainLoop) serve
UM cliente por vez - accept, ClientLoop, close - entao um cliente que larga o
socket e abre outro deixa o servidor preso lendo o primeiro, e toda conexao
seguinte espera no backlog ate estourar o timeout. A correcao, tirada do
mc3_pckbuild.py: UM socket, mantido; se der IPC_FAIL (VM ainda nao subiu) segue
no MESMO socket; so reconecta em erro de I/O de verdade.

Lancamento igual ao do mc3_pckbuild: `-elf <elf> -fastboot -nogui <ISO>` - o
argumento posicional e o DISCO (o jogo le assets do DVD), o -elf so escolhe o
que executar.

    python mc3_savestate.py --segundos 50 --slot 3
"""
import argparse
import glob
import os
import socket
import struct
import subprocess
import time

PCSX2 = os.path.join(os.environ.get('MC3_PCSX2_DIR', ''), 'pcsx2-qt.exe')
ELF = os.path.join(os.environ.get('MC3_HOSTFS', ''), 'mc3boot.elf')
ISO = os.path.join(os.environ.get('MC3_HOSTFS', ''), 'MC3Stripped.iso')
SSTATES = os.path.join(os.environ.get('MC3_PCSX2_DATA', ''), 'sstates')
READ32, SAVESTATE = 0x02, 0x09


class Pine:
    def __init__(self, port=28011, timeout=5.0):
        self.s = socket.create_connection(('127.0.0.1', port), timeout=timeout)
        self.s.settimeout(timeout)

    def _call(self, body, reply_extra):
        self.s.sendall(struct.pack('<I', 4 + len(body)) + body)
        total = struct.unpack('<I', self._recv(4))[0]
        rest = self._recv(total - 4)
        if not rest or rest[0] != 0:
            raise NotReady(rest[0] if rest else -1)
        return rest[1:1 + reply_extra]

    def _recv(self, n):
        out = b''
        while len(out) < n:
            c = self.s.recv(n - len(out))
            if not c:
                raise IOError('PINE fechou')
            out += c
        return out

    def read32(self, addr):
        return struct.unpack('<I', self._call(struct.pack('<BI', READ32, addr), 4))[0]

    def savestate(self, slot):
        self._call(struct.pack('<BB', SAVESTATE, slot & 0xFF), 0)

    def close(self):
        try:
            self.s.close()
        except OSError:
            pass


class NotReady(Exception):
    pass


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument('--segundos', type=float, default=50.0)
    ap.add_argument('--slot', type=int, default=3)
    ap.add_argument('--elf', default=ELF)
    ap.add_argument('--timeout', type=float, default=140.0)
    a = ap.parse_args()

    antes = {f: os.path.getmtime(f) for f in glob.glob(os.path.join(SSTATES, '*.p2s'))}
    cmd = [PCSX2, '-elf', a.elf, '-fastboot', '-nogui']
    if os.path.isfile(ISO):
        cmd.append(ISO)
    proc = subprocess.Popen(cmd)
    print('  PCSX2 subindo; espera inicial %.0fs' % a.segundos)
    time.sleep(a.segundos)

    pine, salvou = None, False
    limite = time.time() + a.timeout
    try:
        while time.time() < limite:
            if proc.poll() is not None:
                raise SystemExit('  o emulador saiu antes da hora (%s)' % proc.returncode)
            if pine is None:
                try:
                    pine = Pine()
                    print('  PINE conectado')
                except OSError:
                    time.sleep(2)
                    continue
            try:
                pine.read32(0x00100000)     # so confirma que a VM responde
            except NotReady:
                time.sleep(2)               # VM ainda nao subiu; MESMO socket
                continue
            except (IOError, OSError):
                pine = None                 # erro real: reconecta
                continue
            # a VM responde: salva
            try:
                pine.savestate(a.slot)
                salvou = True
                print('  savestate disparado no slot %d' % a.slot)
                break
            except NotReady as e:
                print('  savestate recusado (result %s), tentando de novo' % e)
                time.sleep(2)
        if not salvou:
            raise SystemExit('  estourou o tempo sem salvar')
        # o save e assincrono; espera o arquivo
        for _ in range(30):
            time.sleep(0.5)
            for f in glob.glob(os.path.join(SSTATES, '*.p2s')):
                if os.path.getmtime(f) > antes.get(f, 0) + 0.1:
                    print('  SAVESTATE: %s (%d bytes)' % (f, os.path.getsize(f)))
                    return
        print('  salvou mas nao vi arquivo novo (verifique %s)' % SSTATES)
    finally:
        if pine:
            pine.close()
        proc.kill()
        proc.wait()


if __name__ == '__main__':
    main()
