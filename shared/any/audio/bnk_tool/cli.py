"""Interactive terminal menu for MUX/DEMUX of Sony .bnk (989SND/SCREAM) files."""
import os
import sys
import json

from .parser import parse_bnk, BnkParseError
from .demux import demux
from .mux import mux, BnkMuxError
from .model import FULL_SUPPORT_VERSIONS, DEMUX_ONLY_VERSIONS, EXPERIMENTAL_MUX_VERSIONS
from .builder import build_bnk_v3, SoundSpec, grain_from_genh, BuildError, sounds_from_genh_folder


def _ask(prompt, default=None):
    suffix = f" [{default}]" if default is not None else ""
    while True:
        val = input(f"{prompt}{suffix}: ").strip().strip('"')
        if not val and default is not None:
            return default
        if val:
            return val
        print("  (obrigatorio)")


def _ask_path(prompt, default=None, must_exist=True):
    while True:
        val = _ask(prompt, default)
        if not must_exist or os.path.exists(val):
            return val
        print(f"  arquivo/pasta nao encontrado: {val}")


def _ask_yesno(prompt, default=True):
    d = "S/n" if default else "s/N"
    while True:
        val = input(f"{prompt} ({d}): ").strip().lower()
        if not val:
            return default
        if val in ("s", "sim", "y", "yes"):
            return True
        if val in ("n", "nao", "não", "no"):
            return False


def _print_support_note(sblk_version, support_tier):
    if support_tier == "full":
        return
    if support_tier == "demux_only":
        print(f"  aviso: versao SBlk 0x{sblk_version:02x} so tem suporte a leitura/extracao (DEMUX). "
              f"Reconstrucao (MUX) desse stream nao e viavel com seguranca (nao ha campo de tamanho).")
    elif support_tier == "experimental":
        print(f"  aviso: versao SBlk 0x{sblk_version:02x} tem suporte experimental (nao testado contra "
              f"arquivos reais). Confira o resultado com cuidado antes de usar no jogo.")
    else:
        print(f"  aviso: versao SBlk 0x{sblk_version:02x} nao e reconhecida por este suporte de tabela; "
              f"a extracao pode falhar.")


def cmd_info(path=None):
    path = path or _ask_path("Caminho do arquivo .bnk")
    try:
        h = parse_bnk(path)
    except BnkParseError as e:
        print(f"Erro ao interpretar o arquivo: {e}")
        return
    print()
    for line in h.summary_lines():
        print(line)
    _print_support_note(h.sblk_version, h.support_tier)
    print()
    print(f"{'#':>4} {'nome':<24} {'codec':<8} {'ch':>2} {'sample_rate':>11} {'loop':<6} {'tamanho':>10}")
    for s in h.streams:
        loop = f"{s.loop_start}-{s.loop_end}" if s.loop_flag else "nao"
        print(f"{s.index:>4} {s.name[:24]:<24} {s.codec:<8} {s.channels:>2} {s.sample_rate:>11} "
              f"{loop:<6} {s.stream_size:>10}")
        for w in s.warnings:
            print(f"       ! {w}")
    return h


def cmd_demux():
    path = _ask_path("Caminho do arquivo .bnk a extrair")
    default_out = os.path.splitext(path)[0] + "_extracted"
    out_dir = _ask("Pasta de saida", default_out)
    use_genh = _ask_yesno(
        "Extrair como .genh (com cabecalho, editavel/tocavel em qualquer player com vgmstream)?", default=True)
    td_path = None
    default_td = os.path.splitext(path)[0] + ".td"
    if os.path.exists(default_td):
        if _ask_yesno(f"Encontrado {os.path.basename(default_td)} - usar para nomear as streams?", default=True):
            td_path = default_td
    elif _ask_yesno("Tem um arquivo .td para nomear as streams?", default=False):
        td_path = _ask_path("Caminho do .td")
    try:
        manifest_path = demux(path, out_dir, use_genh=use_genh, td_path=td_path)
    except BnkParseError as e:
        print(f"Erro ao interpretar o arquivo: {e}")
        return
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)
    print()
    print(f"OK: {len(manifest['streams'])} streams extraidos para: {out_dir}")
    print(f"Manifest: {manifest_path}")
    tier = manifest["support_tier"]
    if tier != "full":
        _print_support_note(manifest["sblk_version"], tier)
    n_genh = sum(1 for s in manifest["streams"] if s["container"] == "genh")
    n_raw = sum(1 for s in manifest["streams"] if s["container"] == "raw")
    if n_genh:
        print(f"{n_genh} stream(s) extraidos como .genh")
    if n_raw:
        print(f"{n_raw} stream(s) extraidos como raw (codec sem equivalente GENH)")
    any_warn = [s for s in manifest["streams"] if s["warnings"]]
    if any_warn:
        print(f"({len(any_warn)} streams com avisos - veja o manifest.json ou rode a opcao Info para detalhes)")


def cmd_mux():
    print("MUX precisa de: o .bnk ORIGINAL (usado como modelo/template) + a pasta gerada pelo DEMUX (com "
          "manifest.json e os streams, originais ou substituidos).")
    original = _ask_path("Caminho do arquivo .bnk ORIGINAL (template)")
    folder = _ask_path("Pasta com o manifest.json (gerada pelo DEMUX)")
    manifest_path = folder if folder.lower().endswith(".json") else os.path.join(folder, "manifest.json")
    if not os.path.exists(manifest_path):
        print(f"manifest.json nao encontrado em: {manifest_path}")
        return

    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    print(f"\n{len(manifest['streams'])} streams neste banco:")
    for s in manifest["streams"]:
        zlsd = " [ZLSD]" if s.get("is_zlsd") else ""
        print(f"  #{s['index']:<3} {s['name'][:24]:<24} {s['codec']:<8} arquivo atual: {s['file']}{zlsd}")

    overrides = {}
    print("\nDigite o numero de um stream para substituir o audio (ou ENTER para terminar a selecao).")
    print("O arquivo de substituicao deve estar no MESMO CODEC (ja codificado corretamente) - "
          "nenhum reencode e feito por esta ferramenta. Pode ser um .genh (o cabecalho e removido "
          "automaticamente e loop/canais editados no .genh sao aplicados quando possivel) ou o raw puro.")
    while True:
        idx_s = input("Stream # a substituir (ENTER para parar): ").strip()
        if not idx_s:
            break
        if not idx_s.isdigit() or int(idx_s) not in [s["index"] for s in manifest["streams"]]:
            print("  numero invalido")
            continue
        idx = int(idx_s)
        new_file = _ask_path(f"  novo arquivo de audio para stream #{idx}")
        ov = {"file": new_file}
        if _ask_yesno("  ajustar tambem a flag de loop deste stream?", default=False):
            ov["loop_flag"] = _ask_yesno("  stream deve fazer loop?", default=True)
        overrides[idx] = ov

    td_renames = {}
    if manifest.get("td") and _ask_yesno("\nRenomear algum sound (afeta so o .td, nao o .bnk)?", default=False):
        by_index = {}
        for s in manifest["streams"]:
            if s.get("sound_index") is not None:
                by_index.setdefault(s["sound_index"], s["name"])
        for i in sorted(by_index):
            print(f"  sound #{i}: {by_index[i]}")
        while True:
            idx_s = input("Sound # para renomear (ENTER para parar): ").strip()
            if not idx_s:
                break
            if not idx_s.isdigit() or int(idx_s) not in by_index:
                print("  numero invalido")
                continue
            new_name = _ask(f"  novo nome para sound #{idx_s}")
            td_renames[int(idx_s)] = new_name

    default_out = os.path.splitext(original)[0] + "_new.bnk"
    out_path = _ask("Caminho do .bnk de saida", default_out)
    if os.path.abspath(out_path) == os.path.abspath(original):
        print("Por seguranca, o arquivo de saida nao pode ser igual ao original.")
        return

    try:
        path, report = mux(original, manifest_path, out_path, overrides=overrides, td_renames=td_renames)
    except BnkMuxError as e:
        print(f"Erro ao remontar o arquivo: {e}")
        return

    print(f"\nOK: arquivo remontado em: {path}")
    for line in report:
        print(f"  - {line}")


def _cmd_build_folder():
    folder = _ask_path("Pasta com os arquivos .genh")
    try:
        sounds = sounds_from_genh_folder(folder)
    except BuildError as e:
        print(f"Erro: {e}")
        return None

    print(f"\n{len(sounds)} sound(s) detectado(s) pelo nome dos arquivos:")
    for snd in sounds:
        grain_info = ", ".join(f"{g.sample_rate}Hz" for g in snd.grains)
        print(f"  {snd.name}  ({len(snd.grains)} grain(s): {grain_info})")

    if not _ask_yesno("\nUsar esses nomes/agrupamentos?", default=True):
        return None
    return sounds


def _cmd_build_manual():
    sounds = []
    while True:
        name = input("\nNome do sound (ENTER para terminar): ").strip()
        if not name:
            break
        grains = []
        while True:
            genh_path = input(
                f"  arquivo .genh para '{name}' (ENTER para parar de adicionar audio a este sound): "
            ).strip().strip('"')
            if not genh_path:
                break
            if not os.path.exists(genh_path):
                print("  arquivo nao encontrado")
                continue
            try:
                g = grain_from_genh(genh_path)
            except BuildError as e:
                print(f"  erro: {e}")
                continue
            if _ask_yesno(f"  sample_rate atual: {g.sample_rate} Hz - trocar?", default=False):
                g.sample_rate = int(_ask("  novo sample_rate (Hz)"))
            grains.append(g)
        if not grains:
            print(f"  sound '{name}' sem audio, ignorado")
            continue
        sounds.append(SoundSpec(name=name, grains=grains))
    return sounds


def cmd_build():
    print("BUILD cria um .bnk NOVO do zero, sem precisar de um arquivo original como modelo.")
    print("Aviso: alguns campos da tabela (nao lidos pelo vgmstream) foram preenchidos com valores")
    print("observados em bancos reais - validado no vgmstream, mas nao no motor do jogo em si.")
    print("Teste no jogo antes de usar em producao.")
    print("Cada 'sound' (nome que o jogo usa) pode ter 1+ variacoes de audio (grains), cada uma um")
    print(".genh mono em PSX (PS-ADPCM) ou PCM16.")

    print("\n1) Pasta com varios .genh de uma vez (nomeia os sounds pelo nome dos arquivos)")
    print("2) Adicionar um sound de cada vez, manualmente")
    modo = input("> ").strip()

    if modo == "1":
        sounds = _cmd_build_folder()
        if sounds is None:
            return
    else:
        sounds = _cmd_build_manual()

    if not sounds:
        print("nenhum sound definido, cancelado")
        return

    out_path = _ask("Caminho do .bnk de saida", "novo.bnk")
    try:
        bnk_bytes, manifest, td_text = build_bnk_v3(sounds)
    except BuildError as e:
        print(f"Erro ao construir: {e}")
        return

    with open(out_path, "wb") as f:
        f.write(bnk_bytes)
    td_path = os.path.splitext(out_path)[0] + ".td"
    with open(td_path, "w", encoding="latin-1") as f:
        f.write(td_text)

    print(f"\nOK: {len(sounds)} sound(s) / {len(manifest['streams'])} stream(s)")
    print(f".bnk: {out_path}")
    print(f".td:  {td_path}")
    print("Lembrete: teste no jogo antes de usar em producao.")


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]

    if argv:
        return _main_args(argv)

    print("=" * 60)
    print(" BNK MUX/DEMUX - Sony 989SND/SCREAM (.bnk/.mus/.sbk)")
    print(" baseado no leitor bnk_sony.c do VGMStream")
    print("=" * 60)
    while True:
        print("\n1) DEMUX  - extrair streams de um .bnk")
        print("2) MUX    - remontar um .bnk a partir de streams (usa um .bnk original como modelo)")
        print("3) BUILD  - criar um .bnk novo do zero (sem modelo)")
        print("4) Info   - mostrar informacoes/streams de um .bnk")
        print("5) Sair")
        choice = input("> ").strip()
        try:
            if choice == "1":
                cmd_demux()
            elif choice == "2":
                cmd_mux()
            elif choice == "3":
                cmd_build()
            elif choice == "4":
                cmd_info()
            elif choice == "5":
                break
            else:
                print("opcao invalida")
        except KeyboardInterrupt:
            print("\ncancelado")
        except Exception as e:
            print(f"Erro inesperado: {e}")


def _main_args(argv):
    import argparse
    p = argparse.ArgumentParser(prog="bnkmux", description="MUX/DEMUX de arquivos .bnk Sony (989SND/SCREAM)")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_demux = sub.add_parser("demux", help="extrai streams de um .bnk")
    p_demux.add_argument("bnk")
    p_demux.add_argument("out_dir")
    p_demux.add_argument("--raw", action="store_true",
                          help="extrai raw puro em vez de .genh (sem cabecalho)")
    p_demux.add_argument("--td", help="arquivo .td para nomear as streams")

    p_mux = sub.add_parser("mux", help="remonta um .bnk a partir de um manifest (usa modelo)")
    p_mux.add_argument("original_bnk")
    p_mux.add_argument("manifest")
    p_mux.add_argument("out_bnk")
    p_mux.add_argument("--replace", action="append", default=[],
                        help="INDEX=arquivo, pode ser repetido para substituir varios streams")
    p_mux.add_argument("--rename", action="append", default=[],
                        help="SOUND_INDEX=novo_nome, renomeia um sound no .td gerado")

    p_build = sub.add_parser("build", help="cria um .bnk novo do zero, sem modelo")
    p_build.add_argument("out_bnk")
    build_src = p_build.add_mutually_exclusive_group(required=True)
    build_src.add_argument("--dir", help="pasta com varios .genh; um sound por nome de arquivo "
                            "(agrupando 001_NOME.genh + 002_NOME.genh no mesmo sound)")
    build_src.add_argument("--spec", help='JSON: {"sounds":[{"name":.., '
                            '"grains":[{"file":"x.genh","sample_rate":40000}]}]}')

    p_info = sub.add_parser("info", help="mostra informacoes de um .bnk")
    p_info.add_argument("bnk")

    args = p.parse_args(argv)

    if args.cmd == "demux":
        manifest_path = demux(args.bnk, args.out_dir, use_genh=not args.raw, td_path=args.td)
        print(f"OK: {manifest_path}")
    elif args.cmd == "info":
        cmd_info(args.bnk)
    elif args.cmd == "mux":
        overrides = {}
        for item in args.replace:
            idx_s, _, fpath = item.partition("=")
            overrides[int(idx_s)] = {"file": fpath}
        td_renames = {}
        for item in args.rename:
            idx_s, _, new_name = item.partition("=")
            td_renames[int(idx_s)] = new_name
        path, report = mux(args.original_bnk, args.manifest, args.out_bnk, overrides=overrides,
                            td_renames=td_renames)
        print(f"OK: {path}")
        for line in report:
            print(f"  - {line}")
    elif args.cmd == "build":
        if args.dir:
            sounds = sounds_from_genh_folder(args.dir)
        else:
            with open(args.spec, encoding="utf-8") as f:
                spec = json.load(f)
            sounds = []
            for snd in spec["sounds"]:
                grains = []
                for gspec in snd["grains"]:
                    g = grain_from_genh(gspec["file"])
                    if gspec.get("sample_rate"):
                        g.sample_rate = gspec["sample_rate"]
                    if "loop_flag" in gspec:
                        g.loop_flag = gspec["loop_flag"]
                    grains.append(g)
                sounds.append(SoundSpec(name=snd["name"], grains=grains,
                                         priority=snd.get("priority", 0x78), td_flag=snd.get("td_flag", 1)))
        bnk_bytes, manifest, td_text = build_bnk_v3(sounds)
        with open(args.out_bnk, "wb") as f:
            f.write(bnk_bytes)
        td_path = os.path.splitext(args.out_bnk)[0] + ".td"
        with open(td_path, "w", encoding="latin-1") as f:
            f.write(td_text)
        print(f"OK: {args.out_bnk}")
        print(f"OK: {td_path}")


if __name__ == "__main__":
    main()
