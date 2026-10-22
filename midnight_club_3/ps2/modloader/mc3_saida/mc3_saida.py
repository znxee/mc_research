"""
mc3_saida.py - where generated files go

Every tool used to drop its output next to itself, so `tools/experimental/`
ended up with 121 build artefacts sitting among 11 scripts and it was no longer
obvious which files were code and which were the result of running it.

Generated files now land in `tools/output/` unless the caller names a path
explicitly. An explicit `--saida`/`--out` is always honoured as given: this only
supplies the DEFAULT, so nothing that already passes a path changes behaviour.
"""

import os

_AQUI = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(_AQUI, 'output')


def pasta():
    """The output directory, created on first use."""
    if not os.path.isdir(DIR):
        os.makedirs(DIR)
    return DIR


def caminho(nome):
    """`nome` resolved inside the output directory.

    A path that is already absolute, or that names a directory of its own, is
    returned untouched - the caller meant it.
    """
    if os.path.isabs(nome) or os.path.dirname(nome):
        return nome
    return os.path.join(pasta(), nome)
