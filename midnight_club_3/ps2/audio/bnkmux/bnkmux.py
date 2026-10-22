#!/usr/bin/env python
"""Entry point: interactive MUX/DEMUX tool for Sony .bnk (989SND/SCREAM) files.

Uso interativo:
    python bnkmux.py

Uso via linha de comando:
    python bnkmux.py demux arquivo.bnk pasta_saida [--td arquivo.td]
    python bnkmux.py mux original.bnk pasta_saida/manifest.json saida.bnk [--replace 2=novo.genh]
    python bnkmux.py build saida.bnk --dir pasta_com_genh
    python bnkmux.py build saida.bnk --spec spec.json
    python bnkmux.py info arquivo.bnk
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bnk_tool.cli import main

if __name__ == "__main__":
    main()
