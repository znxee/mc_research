# Mouse e teclado para freecam.mod

Depois do boot com `freecam.mod = defer`, abra `start_freecam.cmd`.
Requer Python 3, Windows e PINE ativo com a conexao livre. A camera e
processada no PS2 pelo modulo; este programa transmite os controles do PC.

Foque o PCSX2 e use P para ativar. WASD move, R/F sobe/desce, mouse olha,
Shift acelera, Ctrl reduz, Q/E inclina, O nivela, Z/X ajusta FOV,
M/N ajusta velocidade, T suaviza, H reposiciona. L solta o mouse;
End ou Ctrl+C no terminal encerra o auxiliar. Alt-Tab libera os controles.

Para conferir sem controlar nada:

```powershell
python freecam_input.py --status
```

Outra porta: `start_freecam.cmd --port 28012`.
O PCSX2 deve usar a mesma porta. O add-on antigo de telemetria ReShade
ocupa a unica conexao 28011; so desmarcar o efeito nao libera esse leitor.
Desligue o leitor e reinicie o emulador, ou escolha outra porta para o
freecam (a telemetria do add-on antigo para de receber ate restaurar a porta).

O programa verifica o processo em primeiro plano antes de ler comandos,
nao registra teclas e nao conecta a servidores externos. O mod recebe teclas
mantidas e deltas cumulativos, portanto nao depende de autorepeat do Windows.
Sem auxiliar tambem e possivel controlar o freecam usando o teclado USB do
jogo e as setas para olhar. Veja `../modloader/mods/freecam/README.md`.

Port por modderG, 2026-09-05; camera original por AlgumCorrupto (Paulo).
GPL-3.0, LICENSE.md incluso.
