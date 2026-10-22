#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MC3 Audio Studio - editor unificado de audio de veiculos do Midnight Club 3.

Junta em uma unica ferramenta:
- o visualizador de curvas de .pck (mc3_audio_curve_gui), agora com EDICAO real:
  campos do bloco, ranges (sample/RPM), pontos de curva (arraste no grafico ou edite
  na tabela) e parametros de profile - tudo gravado in-place no .pck (backup .bak);
- o bnk_tool (MUX/DEMUX de .bnk Sony/SCREAM): localiza o banco pelo nome que o
  bloco referencia (ex. E_350Z -> assets/audio/banks/E_350Z.bnk + e_350z.td),
  toca samples individuais e permite extrair/remontar bancos pelo menu;
- preview audivel: renderiza uma aproximacao do som do motor em um RPM fixo ou
  numa varredura de RPM, aplicando crossfade dos ranges + curva de volume,
  usando um decoder PS-ADPCM bit-exato com o vgmstream.

Uso:  python mc3_audio_studio.py [arquivo.pck]
"""
from __future__ import annotations

import json
import math
import os
import sys
import threading
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    import winsound
except ImportError:
    winsound = None

from bnk_tool.pck import (
    parse_pck, PckEditor, PckError, AudioBlock, ProfileBlock, RawAuxBlock, PckDocument,
    CURVE_FIELDS, BLOCK_SCALAR_FIELDS, CURVE_ROW_SLOTS, RANGE_ALLOCATED_COUNT,
    AUDIO_ROOT_MAGICS, AUDIO_BLOCK_MAGICS,
    find_bank_files, default_bank_search_dirs, fit_quadratic,
    aux_category_info,
)
from bnk_tool.audio_preview import BankSamples, EngineMixer, PreviewError, sample_wav, \
    evaluate_curve_segments
from bnk_tool.vehsim import parse_vehicle_perf, VehsimError
from bnk_tool.demux import demux as bnk_demux
from bnk_tool.mux import mux as bnk_mux, BnkMuxError
from bnk_tool.parser import parse_bnk, BnkParseError

CURVE_COLORS = {
    "volume_curve": "#7EC8FF",
    "pitch_curve": "#9DFF8F",
    "high_pitch_curve": "#E6C85C",
    "upshift_curve": "#D596FF",
    "downshift_curve": "#FF9C7E",
}

BLOCK_FIELD_LABELS = [
    ("min_rpm_rec", "Min RPM rec"),
    ("max_rpm_rec", "Max RPM rec"),
    ("near_dist", "Near dist"),
    ("far_dist", "Far dist"),
    ("warble_min_rpm", "Warble min RPM"),
    ("warble_max_rpm", "Warble max RPM"),
    ("warble_min_rpm_delta", "Warble min RPM d"),
    ("warble_min_vol_delta", "Warble min vol d"),
    ("warble_max_rpm_delta", "Warble max RPM d"),
    ("warble_max_vol_delta", "Warble max vol d"),
    ("warble_reverse_max_rpm_delta", "Warble rev RPM d"),
    ("warble_reverse_period_rate", "Warble rev period"),
    ("boost_mix_percent", "Boost mix %"),
    ("boost_mix_rate", "Boost mix rate"),
    ("high_pitch_curve_engage_gear", "HighPitch gear"),
]


class AudioStudio:
    BG = "#15161A"
    PANEL = "#1D1F26"
    PANEL2 = "#242731"
    FG = "#E6E8EF"
    MUTED = "#8D94A3"
    GRID = "#353945"
    ACCENT = "#E3C75F"
    WARN = "#FFB86C"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MC3 Audio Studio")
        self.root.geometry("1560x940")
        self.root.minsize(1180, 720)

        self.doc: PckDocument | None = None
        self.editor: PckEditor | None = None
        self.current_path: Path | None = None
        self.item_map = {}
        self.selected = None
        self.selected_key = None

        self.extra_bank_dirs: list[str] = []
        self.bank_cache: dict[str, BankSamples] = {}
        self.bank_paths: dict[str, tuple] = {}   # bank_name -> (bnk, td)
        self.perf_cache: dict[str, object] = {}  # "base"/"mods" -> VehiclePerf|None
        self.perf_variant = tk.StringVar(value="base")

        # curve editing state
        self.edit_curve_key = tk.StringVar(value="volume_curve")
        self.pending_segments: list[list[float]] | None = None
        self.drag_target = None

        self.curve_visible = {key: tk.BooleanVar(value=True) for key, _, _, _ in CURVE_FIELDS}
        self.curve_scale_mode = tk.StringVar(value="global")
        self.show_point_labels = tk.BooleanVar(value=True)

        self._render_thread = None
        self._tmp_wav: str | None = None
        self.undo_stack: list[tuple[str, bytes]] = []   # (label, buffer snapshot), max 10
        self.redo_stack: list[tuple[str, bytes]] = []
        self._setup_style()
        self._build_ui()

    # ------------------------------------------------------------------ style/ui
    def _setup_style(self):
        self.root.configure(bg=self.BG)
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(".", background=self.BG, foreground=self.FG, fieldbackground=self.PANEL,
                        bordercolor=self.GRID)
        style.configure("TFrame", background=self.BG)
        style.configure("Panel.TFrame", background=self.PANEL)
        style.configure("TLabel", background=self.BG, foreground=self.FG)
        style.configure("Muted.TLabel", background=self.BG, foreground=self.MUTED)
        style.configure("Accent.TLabel", background=self.BG, foreground=self.ACCENT)
        style.configure("TButton", background=self.PANEL2, foreground=self.FG, padding=4)
        style.map("TButton", background=[("active", "#303443")])
        style.configure("Treeview", background=self.PANEL, foreground=self.FG,
                        fieldbackground=self.PANEL, rowheight=22)
        style.configure("Treeview.Heading", background=self.PANEL2, foreground=self.FG)
        style.map("Treeview", background=[("selected", "#3A4052")], foreground=[("selected", "#FFFFFF")])
        style.configure("TCheckbutton", background=self.BG, foreground=self.FG)
        style.configure("TNotebook", background=self.BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.PANEL2, foreground=self.FG, padding=(8, 4))
        style.map("TNotebook.Tab", background=[("selected", self.PANEL)],
                  foreground=[("selected", "#FFFFFF")])
        style.configure("TEntry", fieldbackground=self.PANEL2, foreground=self.FG,
                        insertcolor=self.FG)
        style.configure("TCombobox", fieldbackground=self.PANEL2, foreground=self.FG)
        style.configure("TSpinbox", fieldbackground=self.PANEL2, foreground=self.FG)
        style.configure("Horizontal.TScale", background=self.BG)

    def _build_ui(self):
        self._build_menu()

        toolbar = ttk.Frame(self.root, style="Panel.TFrame")
        toolbar.pack(side=tk.TOP, fill=tk.X)
        ttk.Button(toolbar, text="Abrir PCK", command=self.open_pck_dialog).pack(side=tk.LEFT, padx=4, pady=4)
        self.save_btn = ttk.Button(toolbar, text="Salvar PCK", command=self.save_pck)
        self.save_btn.pack(side=tk.LEFT, padx=4, pady=4)
        ttk.Button(toolbar, text="Recarregar", command=self.reload_current).pack(side=tk.LEFT, padx=4, pady=4)

        ttk.Label(toolbar, text="Curvas:", style="Muted.TLabel").pack(side=tk.LEFT, padx=(20, 4))
        for key, label, _, _ in CURVE_FIELDS:
            ttk.Checkbutton(toolbar, text=label, variable=self.curve_visible[key],
                            command=self.redraw_canvas).pack(side=tk.LEFT, padx=3)
        ttk.Label(toolbar, text="Escala:", style="Muted.TLabel").pack(side=tk.LEFT, padx=(16, 4))
        ttk.Radiobutton(toolbar, text="0-1", variable=self.curve_scale_mode, value="global",
                        command=self.redraw_canvas).pack(side=tk.LEFT)
        ttk.Radiobutton(toolbar, text="Ajustar", variable=self.curve_scale_mode, value="fit",
                        command=self.redraw_canvas).pack(side=tk.LEFT)

        main = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        main.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        left = ttk.Frame(main, style="Panel.TFrame")
        right = ttk.Panedwindow(main, orient=tk.VERTICAL)
        main.add(left, weight=1)
        main.add(right, weight=4)

        ttk.Label(left, text="Estrutura do PCK", style="Accent.TLabel").pack(anchor="w", padx=8, pady=(8, 4))
        self.tree = ttk.Treeview(left, show="tree")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=(0, 8))
        sb = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.tree.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 8))
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        top_right = ttk.Frame(right)
        self.tabs = ttk.Notebook(right)
        right.add(top_right, weight=4)
        right.add(self.tabs, weight=3)

        self.summary = tk.Text(top_right, height=5, bg=self.PANEL, fg=self.FG,
                               insertbackground=self.FG, relief=tk.FLAT, wrap=tk.WORD)
        self.summary.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(8, 4))
        self.summary.configure(state=tk.DISABLED)

        self.canvas = tk.Canvas(top_right, bg=self.PANEL, highlightthickness=0)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=(4, 8))
        self.canvas.bind("<Configure>", lambda e: self.redraw_canvas())
        self.canvas.bind("<Button-1>", self.on_canvas_press)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)

        self._build_block_tab()
        self._build_ranges_tab()
        self._build_curves_tab()
        self._build_preview_tab()
        self._build_raw_tab()

        self.status = ttk.Label(self.root, text="Abra um .pck de veiculo (File > Abrir PCK).",
                                style="Muted.TLabel")
        self.status.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=2)

    def _build_menu(self):
        menubar = tk.Menu(self.root)
        fm = tk.Menu(menubar, tearoff=False)
        fm.add_command(label="Abrir PCK...", command=self.open_pck_dialog, accelerator="Ctrl+O")
        fm.add_command(label="Salvar PCK", command=self.save_pck, accelerator="Ctrl+S")
        fm.add_command(label="Salvar PCK como...", command=self.save_pck_as)
        fm.add_command(label="Recarregar", command=self.reload_current, accelerator="F5")
        fm.add_separator()
        fm.add_command(label="Exportar JSON da secao de audio...", command=self.export_json)
        fm.add_separator()
        fm.add_command(label="Sair", command=self.root.quit)
        menubar.add_cascade(label="Arquivo", menu=fm)

        em = tk.Menu(menubar, tearoff=False)
        em.add_command(label="Desfazer", command=self.undo, accelerator="Ctrl+Z")
        em.add_command(label="Refazer", command=self.redo, accelerator="Ctrl+Y")
        em.add_separator()
        em.add_command(label="Importar audio de outro PCK (conservador)...",
                       command=lambda: self.import_donor_dialog("conservative"))
        em.add_command(label="Importar audio de outro PCK (experimental)...",
                       command=lambda: self.import_donor_dialog("experimental"))
        menubar.add_cascade(label="Editar", menu=em)

        bm = tk.Menu(menubar, tearoff=False)
        bm.add_command(label="Definir pasta extra de bancos...", command=self.set_banks_dir)
        bm.add_command(label="Info do banco do bloco selecionado", command=self.show_bank_info)
        bm.add_separator()
        bm.add_command(label="Extrair banco (DEMUX)...", command=self.demux_bank_dialog)
        bm.add_command(label="Remontar banco (MUX)...", command=self.mux_bank_dialog)
        menubar.add_cascade(label="Bancos", menu=bm)

        self.root.config(menu=menubar)
        self.root.bind("<Control-o>", lambda e: self.open_pck_dialog())
        self.root.bind("<Control-s>", lambda e: self.save_pck())
        self.root.bind("<Control-z>", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())
        self.root.bind("<F5>", lambda e: self.reload_current())

    # ---- tabs ----
    def _build_block_tab(self):
        f = ttk.Frame(self.tabs)
        self.tabs.add(f, text="Bloco")
        self.block_vars = {}

        # header: bank name + rev sound + prefix option, kept in its own grid so the
        # scalar-field grid below can't wrap into these cells
        header = ttk.Frame(f)
        header.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(8, 2))
        ttk.Label(header, text="Bank name:").grid(row=0, column=0, sticky="e", padx=(4, 2), pady=2)
        self.bank_name_var = tk.StringVar()
        ttk.Entry(header, textvariable=self.bank_name_var, width=24).grid(
            row=0, column=1, sticky="w", padx=(0, 16), pady=2)
        ttk.Label(header, text="RevSound:").grid(row=0, column=2, sticky="e", padx=(4, 2), pady=2)
        self.rev_sound_var = tk.StringVar()
        ttk.Entry(header, textvariable=self.rev_sound_var, width=24).grid(
            row=0, column=3, sticky="w", padx=(0, 4), pady=2)
        self.update_prefixes_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(header, text="Trocar banco atualiza prefixo dos samples",
                        variable=self.update_prefixes_var).grid(
            row=1, column=0, columnspan=4, sticky="w", padx=4, pady=(2, 0))

        # scalar fields in a fixed 3-columns-of-pairs grid with reserved widths so long
        # labels never overlap the neighbouring entry
        fields = ttk.Frame(f)
        fields.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(6, 2))
        per_row = 3
        for c in range(per_row):
            fields.columnconfigure(c * 2, minsize=150)      # label column
            fields.columnconfigure(c * 2 + 1, minsize=95)   # entry column
        for i, (name, label) in enumerate(BLOCK_FIELD_LABELS):
            r, c = divmod(i, per_row)
            var = tk.StringVar()
            self.block_vars[name] = var
            ttk.Label(fields, text=label + ":").grid(
                row=r, column=c * 2, sticky="e", padx=(6, 2), pady=3)
            ttk.Entry(fields, textvariable=var, width=12).grid(
                row=r, column=c * 2 + 1, sticky="w", padx=(0, 12), pady=3)

        btns = ttk.Frame(f)
        btns.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(8, 4))
        ttk.Button(btns, text="Aplicar campos do bloco", command=self.apply_block_fields).pack(side=tk.LEFT, padx=4)
        ttk.Label(btns, text="(aplicar grava no buffer; use Salvar PCK para gravar no arquivo)",
                  style="Muted.TLabel").pack(side=tk.LEFT, padx=8)

    def _build_ranges_tab(self):
        f = ttk.Frame(self.tabs)
        self.tabs.add(f, text="Ranges")
        self.ranges_tree = ttk.Treeview(
            f, columns=("idx", "active", "sample", "min", "mid", "max"), show="headings", height=6)
        for col, text, width, anchor in [
            ("idx", "#", 40, "e"), ("active", "Ativo", 60, "center"), ("sample", "Sample", 320, "w"),
            ("min", "Min RPM", 100, "e"), ("mid", "Mid RPM", 100, "e"), ("max", "Max RPM", 100, "e"),
        ]:
            self.ranges_tree.heading(col, text=text)
            self.ranges_tree.column(col, width=width, anchor=anchor)
        self.ranges_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=(8, 4))
        self.ranges_tree.bind("<<TreeviewSelect>>", self.on_range_select)
        self.ranges_tree.bind("<Double-1>", lambda e: self.play_selected_range_sample())

        edit = ttk.Frame(f)
        edit.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(0, 8))
        self.range_vars = {k: tk.StringVar() for k in ("sample", "min", "mid", "max")}
        ttk.Label(edit, text="Sample:").pack(side=tk.LEFT)
        ttk.Entry(edit, textvariable=self.range_vars["sample"], width=34).pack(side=tk.LEFT, padx=4)
        for k, lbl in (("min", "Min"), ("mid", "Mid"), ("max", "Max")):
            ttk.Label(edit, text=lbl + ":").pack(side=tk.LEFT)
            ttk.Entry(edit, textvariable=self.range_vars[k], width=9).pack(side=tk.LEFT, padx=3)
        ttk.Button(edit, text="Aplicar range", command=self.apply_range).pack(side=tk.LEFT, padx=6)
        ttk.Label(edit, text="Ativos:").pack(side=tk.LEFT, padx=(12, 2))
        self.active_count_var = tk.StringVar()
        ttk.Spinbox(edit, from_=0, to=RANGE_ALLOCATED_COUNT, width=4,
                    textvariable=self.active_count_var).pack(side=tk.LEFT)
        ttk.Button(edit, text="Aplicar contagem", command=self.apply_active_count).pack(side=tk.LEFT, padx=4)
        ttk.Button(edit, text="▶ Tocar sample", command=self.play_selected_range_sample).pack(side=tk.LEFT, padx=12)

    def _build_curves_tab(self):
        f = ttk.Frame(self.tabs)
        self.tabs.add(f, text="Curvas (editar)")
        top = ttk.Frame(f)
        top.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(8, 2))
        ttk.Label(top, text="Curva em edicao:").pack(side=tk.LEFT)
        self.curve_combo = ttk.Combobox(top, textvariable=self.edit_curve_key, state="readonly",
                                        values=[k for k, _, _, _ in CURVE_FIELDS], width=18)
        self.curve_combo.pack(side=tk.LEFT, padx=6)
        self.curve_combo.bind("<<ComboboxSelected>>", lambda e: self.load_pending_curve())
        ttk.Button(top, text="+ segmento", command=self.add_curve_segment).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="- segmento", command=self.remove_curve_segment).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Copiar", command=self.copy_curve).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Colar", command=self.paste_curve).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Aplicar curva", command=self.apply_curve).pack(side=tk.LEFT, padx=10)
        ttk.Button(top, text="Reverter", command=self.load_pending_curve).pack(side=tk.LEFT, padx=4)
        ttk.Label(top, text="Arraste pontos no grafico; clique direito insere/apaga ponto.",
                  style="Muted.TLabel").pack(side=tk.LEFT, padx=10)

        self.seg_tree = ttk.Treeview(
            f, columns=("i", "x0", "y0", "cx", "cy", "x1", "y1"), show="headings", height=6)
        for col, text in [("i", "#"), ("x0", "X0"), ("y0", "Y0"), ("cx", "Ctrl X"),
                          ("cy", "Ctrl Y"), ("x1", "X1"), ("y1", "Y1")]:
            self.seg_tree.heading(col, text=text)
            self.seg_tree.column(col, width=90 if col != "i" else 40, anchor="e")
        self.seg_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=(4, 8))
        self.seg_tree.bind("<Double-1>", self.on_seg_double_click)

    def _build_preview_tab(self):
        f = ttk.Frame(self.tabs)
        self.tabs.add(f, text="Preview de audio")
        info = ttk.Frame(f)
        info.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(8, 4))
        self.bank_status = ttk.Label(info, text="Selecione um bloco de motor/escape.", style="Muted.TLabel")
        self.bank_status.pack(side=tk.LEFT)

        ctl = ttk.Frame(f)
        ctl.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)
        ttk.Label(ctl, text="RPM:").pack(side=tk.LEFT)
        self.rpm_var = tk.DoubleVar(value=2000.0)
        self.rpm_scale = ttk.Scale(ctl, from_=500, to=8000, variable=self.rpm_var, length=420)
        self.rpm_scale.pack(side=tk.LEFT, padx=6)
        self.rpm_label = ttk.Label(ctl, text="2000")
        self.rpm_label.pack(side=tk.LEFT, padx=4)
        self.rpm_scale.configure(command=lambda v: self.rpm_label.configure(text=f"{float(v):.0f}"))

        btns = ttk.Frame(f)
        btns.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)
        ttk.Button(btns, text="▶ Tocar neste RPM (2s)", command=self.play_at_rpm).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="▶ Varredura de RPM (6s)", command=self.play_sweep).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="■ Parar", command=self.stop_audio).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Salvar varredura como WAV...", command=self.export_sweep_wav).pack(side=tk.LEFT, padx=12)
        ttk.Label(btns, text="Preview aproximado: crossfade por range + curva de volume; pitch = RPM/MidRPM.",
                  style="Muted.TLabel").pack(side=tk.LEFT, padx=8)

        gears = ttk.Frame(f)
        gears.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)
        ttk.Button(gears, text="▶ Simular passagem de marchas",
                   command=self.play_gear_drive).pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(gears, text="Base (stock)", variable=self.perf_variant, value="base",
                        command=self.refresh_perf_label).pack(side=tk.LEFT, padx=4)
        ttk.Radiobutton(gears, text="Mods (full upgrade)", variable=self.perf_variant, value="mods",
                        command=self.refresh_perf_label).pack(side=tk.LEFT, padx=4)
        self.perf_label = ttk.Label(gears, text="", style="Muted.TLabel")
        self.perf_label.pack(side=tk.LEFT, padx=10)

        sf = ttk.Frame(f)
        sf.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=4)
        ttk.Label(sf, text="Samples do banco (duplo clique para tocar):", style="Muted.TLabel").pack(anchor="w")
        self.samples_list = tk.Listbox(sf, bg=self.PANEL2, fg=self.FG, height=6,
                                       selectbackground="#3A4052")
        self.samples_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=4)
        self.samples_list.bind("<Double-1>", lambda e: self.play_bank_sample())

    def _build_raw_tab(self):
        f = ttk.Frame(self.tabs)
        self.tabs.add(f, text="Raw / Avisos")
        self.raw_text = tk.Text(f, bg=self.PANEL, fg=self.FG, insertbackground=self.FG,
                                relief=tk.FLAT, wrap=tk.NONE)
        self.raw_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)

    # ------------------------------------------------------------------ file ops
    def open_pck_dialog(self):
        path = filedialog.askopenfilename(title="Abrir PCK de veiculo",
                                          filetypes=[("PCK", "*.pck"), ("Todos", "*.*")])
        if path:
            self.load_pck(Path(path))

    def load_pck(self, path: Path):
        try:
            doc = parse_pck(path)
        except (PckError, OSError) as exc:
            messagebox.showerror("Falha ao abrir PCK", str(exc))
            return
        self.doc = doc
        self.editor = PckEditor(doc)
        self.current_path = Path(path)
        self.selected = None
        self.selected_key = None
        self.pending_segments = None
        self.perf_cache.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.root.title(f"MC3 Audio Studio - {Path(path).name}")
        self.rebuild_tree()
        self.show_doc_summary()
        self.set_status(f"Carregado: {path}")

    def reload_current(self):
        if self.current_path:
            if self.editor and self.editor.dirty:
                if not messagebox.askyesno("Recarregar", "Ha edicoes nao salvas. Descartar e recarregar?"):
                    return
            self.load_pck(self.current_path)

    def save_pck(self):
        if not self.editor:
            return
        try:
            out = self.editor.save()
        except OSError as exc:
            messagebox.showerror("Falha ao salvar", str(exc))
            return
        self.editor.dirty = False
        self.set_status(f"Salvo: {out} (backup .bak criado na primeira gravacao)")

    def save_pck_as(self):
        if not self.editor:
            return
        path = filedialog.asksaveasfilename(defaultextension=".pck",
                                            filetypes=[("PCK", "*.pck")],
                                            initialfile=self.current_path.name if self.current_path else "")
        if not path:
            return
        out = self.editor.save(path, backup=False)
        self.set_status(f"Salvo como: {out}")

    def export_json(self):
        if not self.doc:
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path:
            return
        data = {
            "source": str(self.doc.path),
            "root_name": self.doc.root_name,
            "blocks": [{
                "key": b.key, "category": b.category, "bank": b.bank_name,
                "active_ranges": b.active_range_count,
                "ranges": [vars(r) for r in b.ranges],
                "curves": {k: {"count": c.point_count, "segments": [list(s) for s in c.segments]}
                            for k, c in b.curves.items()},
            } for b in self.doc.blocks],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self.set_status(f"JSON exportado: {path}")

    # ------------------------------------------------------------------ tree
    def rebuild_tree(self):
        self.tree.delete(*self.tree.get_children())
        self.item_map.clear()
        if not self.doc:
            return
        root_id = self.tree.insert("", "end", text=self.doc.path.name, open=True)
        self.item_map[root_id] = self.doc
        cats = {}
        for b in self.doc.blocks:
            cats.setdefault(b.category, []).append(b)
        for rb in self.doc.raw_aux_blocks:
            cats.setdefault(rb.category, []).append(rb)
        if self.doc.profiles:
            cats.setdefault("Common", []).extend(self.doc.profiles)
        order = ["Engine", "Exhaust", "Auxiliary / TurboBlower"]
        select_id = None
        for cat in order + sorted(k for k in cats if k not in order):
            if cat not in cats:
                continue
            cat_id = self.tree.insert(root_id, "end", text=cat,
                                      open=cat in ("Engine", "Exhaust"))
            self.item_map[cat_id] = cat
            for item in cats[cat]:
                label = getattr(item, "display_label", None) or getattr(item, "label", str(item))
                iid = self.tree.insert(cat_id, "end", text=label)
                self.item_map[iid] = item
                if getattr(item, "key", None) == self.selected_key:
                    select_id = iid
        if select_id:
            self.tree.selection_set(select_id)
            self.tree.see(select_id)

    def on_tree_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.item_map.get(sel[0])
        self.selected = item
        self.selected_key = getattr(item, "key", None)
        if isinstance(item, AudioBlock):
            self.show_block(item)
        elif isinstance(item, ProfileBlock):
            self.show_profile(item)
        elif isinstance(item, RawAuxBlock):
            self.show_raw_aux(item)
        elif isinstance(item, PckDocument):
            self.show_doc_summary()
        elif isinstance(item, str):
            info = aux_category_info(item)
            self.set_summary(f"Categoria: {item}\n\nPapel: {info['role']}\nEdicao: {info['edit']}")
        self.redraw_canvas()

    # ------------------------------------------------------------------ views
    def set_summary(self, text):
        self.summary.configure(state=tk.NORMAL)
        self.summary.delete("1.0", tk.END)
        self.summary.insert(tk.END, text)
        self.summary.configure(state=tk.DISABLED)

    def set_raw(self, text):
        self.raw_text.delete("1.0", tk.END)
        self.raw_text.insert(tk.END, text)

    def set_status(self, text):
        self.status.configure(text=text)

    def show_doc_summary(self):
        d = self.doc
        if not d:
            return
        lines = [
            f"{d.path}",
            f"Root: {d.root_name} | magic {AUDIO_ROOT_MAGICS.get(d.root_magic, hex(d.root_magic))}",
            f"Blocos: {len(d.blocks)} | Profiles: {len(d.profiles)} | Bancos referenciados: {', '.join(d.bank_names())}",
        ]
        if d.warnings:
            lines += ["Avisos: " + "; ".join(d.warnings)]
        self.set_summary("\n".join(lines))
        self.set_raw("")

    def show_block(self, b: AudioBlock):
        self.set_summary(
            f"{b.label} ({b.category}) | banco: {b.bank_name or '<vazio>'} | "
            f"RPM rec {b.min_rpm_rec:.0f}-{b.max_rpm_rec:.0f} | ranges ativos: {b.active_range_count}\n"
            f"magic: {AUDIO_BLOCK_MAGICS.get(b.magic, hex(b.magic))}"
            + ("\nAvisos: " + "; ".join(b.warnings) if b.warnings else ""))
        # block tab
        self.bank_name_var.set(b.bank_name)
        self.rev_sound_var.set(b.engine_rev_sound)
        for name, _label in BLOCK_FIELD_LABELS:
            v = getattr(b, name)
            self.block_vars[name].set(f"{v:.6g}" if isinstance(v, float) else str(v))
        self.active_count_var.set(str(b.active_range_count))
        # ranges tab
        self.ranges_tree.delete(*self.ranges_tree.get_children())
        for r in b.ranges:
            self.ranges_tree.insert("", "end", iid=str(r.index), values=(
                r.index, "sim" if r.active else "-", r.sample_name,
                f"{r.min_rpm:.6g}", f"{r.mid_rpm:.6g}", f"{r.max_rpm:.6g}"))
        # curves tab
        self.load_pending_curve()
        # raw tab
        lines = ["Curvas:"]
        for k, c in b.curves.items():
            lines.append(f"  {k}: count={c.point_count} off={c.file_off and hex(c.file_off)} "
                         f"pts_off={c.points_file_off and hex(c.points_file_off)} {c.warning}")
        self.set_raw("\n".join(lines))
        # preview tab
        self.update_preview_tab(b)

    def show_profile(self, p: ProfileBlock):
        self.set_summary(f"{p.label} | magic {hex(p.magic)}\n"
                         "Os 22 parametros aparecem na aba Ranges - duplo clique em um deles para editar.")
        self.ranges_tree.delete(*self.ranges_tree.get_children())
        for i, v in enumerate(p.params):
            self.ranges_tree.insert("", "end", iid=str(i),
                                    values=(i, "-", f"param[{i:02d}]", f"{v:.9g}", "", ""))
        lines = [f"[{i:02d}] {v:.9g}" for i, v in enumerate(p.params)]
        self.set_raw("Parametros do profile:\n" + "\n".join(lines))

    def _edit_profile_param(self, p: ProfileBlock):
        sel = self.ranges_tree.selection()
        if not sel or not self.editor:
            return
        idx = int(sel[0])
        cur = p.params[idx]
        new = simple_prompt(self.root, f"{p.label} - param[{idx:02d}]", f"{cur:.9g}")
        if new is None:
            return
        self.push_undo(f"param[{idx:02d}] de {p.label}")
        try:
            self.editor.set_profile_param(p, idx, float(new))
        except (ValueError, PckError) as exc:
            messagebox.showerror("Valor invalido", str(exc))
            self.undo_stack.pop()
            return
        self._after_edit()
        self.set_status(f"param[{idx:02d}] aplicado (nao salvo ainda).")

    def show_raw_aux(self, r: RawAuxBlock):
        info = aux_category_info(r.category)
        self.set_summary(
            f"{r.label} ({r.category}) | magic {hex(r.magic)} | tipo {r.kind}\n"
            f"Papel: {info['role']}\n"
            "Strings e floats candidatos na aba Ranges - duplo clique para editar (experimental).")
        # repurpose the ranges table: strings then float candidates, editable via prompt
        self.ranges_tree.delete(*self.ranges_tree.get_children())
        for e in r.found_string_entries:
            self.ranges_tree.insert("", "end", iid=f"s{e['rel_off']}",
                                    values=("str", f"+0x{e['rel_off']:X}", e["text"], "", "", ""))
        for e in r.float_preview:
            self.ranges_tree.insert("", "end", iid=f"f{e['rel_off']}",
                                    values=("f32", f"+0x{e['rel_off']:X}", f"{e['float']:.6g}",
                                            f"0x{e['u32']:08X}", "", ""))
        lines = [f"+0x{e['rel_off']:X}: {e['text']!r}" for e in r.found_string_entries]
        self.set_raw("Strings encontradas:\n" + "\n".join(lines[:60]))

    def _edit_aux_entry(self, r: RawAuxBlock):
        sel = self.ranges_tree.selection()
        if not sel or not self.editor:
            return
        iid = sel[0]
        kind, rel_off = iid[0], int(iid[1:])
        if kind == "s":
            entry = next((e for e in r.found_string_entries if e["rel_off"] == rel_off), None)
            if entry is None:
                return
            new = simple_prompt(self.root, f"{r.label} string +0x{rel_off:X}", entry["text"])
            if new is None or new == entry["text"]:
                return
            self.push_undo(f"aux string {r.label}")
            try:
                self.editor.set_aux_string(r, rel_off, new)
            except PckError as exc:
                messagebox.showerror("Erro", str(exc))
                self.undo_stack.pop()
                return
        else:
            entry = next((e for e in r.float_preview if e["rel_off"] == rel_off), None)
            if entry is None:
                return
            new = simple_prompt(self.root, f"{r.label} float +0x{rel_off:X} (experimental)",
                                f"{entry['float']:.6g}")
            if new is None:
                return
            try:
                value = float(new)
            except ValueError:
                return
            self.push_undo(f"aux float {r.label}")
            try:
                self.editor.set_aux_float(r, rel_off, value)
            except PckError as exc:
                messagebox.showerror("Erro", str(exc))
                self.undo_stack.pop()
                return
        self._after_edit()
        self.set_status(f"{r.label} +0x{rel_off:X} aplicado (nao salvo ainda).")

    # ------------------------------------------------------------------ edits
    def _current_block(self) -> AudioBlock | None:
        return self.selected if isinstance(self.selected, AudioBlock) else None

    def _after_edit(self):
        """Reparse the edited buffer so every view reflects the change."""
        self.doc = self.editor.reparse()
        self.editor.doc = self.doc
        self.perf_cache.clear()
        self.rebuild_tree()
        if self.selected_key:
            found = self.doc.block_by_key(self.selected_key)
            if not found:
                for p in self.doc.profiles:
                    if p.key == self.selected_key:
                        found = p
                        break
            if not found:
                for r in self.doc.raw_aux_blocks:
                    if r.key == self.selected_key:
                        found = r
                        break
            if found is not None:
                self.selected = found
                if isinstance(found, AudioBlock):
                    self.show_block(found)
                elif isinstance(found, ProfileBlock):
                    self.show_profile(found)
                elif isinstance(found, RawAuxBlock):
                    self.show_raw_aux(found)
        self.redraw_canvas()

    # ---- undo/redo (10-step buffer snapshots, like curve GUI v0.20) ----
    def push_undo(self, label: str):
        if not self.editor:
            return
        self.undo_stack.append((label, bytes(self.editor.buf)))
        if len(self.undo_stack) > 10:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def undo(self):
        if not self.editor or not self.undo_stack:
            self.set_status("Nada para desfazer.")
            return
        label, buf = self.undo_stack.pop()
        self.redo_stack.append((label, bytes(self.editor.buf)))
        self.editor.buf = bytearray(buf)
        self.editor.dirty = True
        self._after_edit()
        self.load_pending_curve()
        self.set_status(f"Desfeito: {label}")

    def redo(self):
        if not self.editor or not self.redo_stack:
            self.set_status("Nada para refazer.")
            return
        label, buf = self.redo_stack.pop()
        self.undo_stack.append((label, bytes(self.editor.buf)))
        self.editor.buf = bytearray(buf)
        self.editor.dirty = True
        self._after_edit()
        self.load_pending_curve()
        self.set_status(f"Refeito: {label}")

    # ---- donor import ----
    def import_donor_dialog(self, mode: str):
        if not self.editor:
            messagebox.showinfo("Importar", "Abra o PCK alvo primeiro.")
            return
        path = filedialog.askopenfilename(
            title=f"PCK doador ({'conservador' if mode == 'conservative' else 'experimental'})",
            filetypes=[("PCK", "*.pck"), ("Todos", "*.*")])
        if not path:
            return
        try:
            donor = parse_pck(path)
        except PckError as exc:
            messagebox.showerror("Falha ao abrir doador", str(exc))
            return
        if not messagebox.askyesno(
                "Confirmar importacao",
                f"Importar audio de {os.path.basename(path)} para {self.doc.path.name} "
                f"(modo {'conservador' if mode == 'conservative' else 'experimental'})?\n\n"
                "Conservador: bancos, prefixos de sample, RPMs e curvas de troca de marcha.\n"
                "Experimental: todos os campos seguros, ranges completos, todas as curvas, "
                "EngineRevSound, strings/floats auxiliares e Commons.\n\n"
                "A operacao pode ser desfeita com Ctrl+Z e nada e salvo ate voce salvar."):
            return
        self.push_undo(f"import {mode} de {os.path.basename(path)}")
        try:
            report = self.editor.import_from_document(donor, mode=mode)
        except PckError as exc:
            messagebox.showerror("Falha na importacao", str(exc))
            self.undo_stack.pop()
            return
        self._after_edit()
        self.load_pending_curve()
        counters = "\n".join(f"  {k}: {v}" for k, v in report.items()
                             if k != "warnings" and isinstance(v, int) and v)
        warns = report.get("warnings", [])
        msg = f"Importacao concluida:\n{counters}"
        if warns:
            msg += f"\n\nAvisos ({len(warns)}):\n" + "\n".join("  - " + w for w in warns[:10])
            if len(warns) > 10:
                msg += f"\n  ... e mais {len(warns) - 10}"
        messagebox.showinfo("Importacao", msg)
        self.set_status(f"Audio importado ({mode}) - use Salvar PCK para gravar.")

    def apply_block_fields(self):
        b = self._current_block()
        if not b or not self.editor:
            return
        self.push_undo("campos do bloco")
        changed_prefixes = 0
        try:
            if self.bank_name_var.get() != b.bank_name:
                changed_prefixes = self.editor.set_bank_name(
                    b, self.bank_name_var.get(),
                    update_sample_prefixes=self.update_prefixes_var.get())
            if self.rev_sound_var.get() != b.engine_rev_sound:
                self.editor.set_engine_rev_sound(b, self.rev_sound_var.get())
            for name, _label in BLOCK_FIELD_LABELS:
                raw = self.block_vars[name].get().strip()
                if not raw:
                    continue
                _rel, kind = BLOCK_SCALAR_FIELDS[name]
                value = int(float(raw)) if kind == "u32" else float(raw)
                if value != getattr(b, name):
                    self.editor.set_block_scalar(b, name, value)
        except (ValueError, PckError) as exc:
            messagebox.showerror("Valor invalido", str(exc))
            self.undo_stack.pop()
            return
        self._after_edit()
        extra = f" ({changed_prefixes} prefixos de sample atualizados)" if changed_prefixes else ""
        self.set_status(f"Campos do bloco aplicados{extra} (nao salvos ainda).")

    def on_range_select(self, _event=None):
        b = self._current_block()
        sel = self.ranges_tree.selection()
        if not b or not sel:
            return
        r = b.ranges[int(sel[0])]
        self.range_vars["sample"].set(r.sample_name)
        self.range_vars["min"].set(f"{r.min_rpm:.6g}")
        self.range_vars["mid"].set(f"{r.mid_rpm:.6g}")
        self.range_vars["max"].set(f"{r.max_rpm:.6g}")

    def apply_range(self):
        b = self._current_block()
        sel = self.ranges_tree.selection()
        if not b or not sel or not self.editor:
            return
        idx = int(sel[0])
        self.push_undo(f"range {idx}")
        try:
            self.editor.set_range(
                b, idx,
                sample_name=self.range_vars["sample"].get(),
                min_rpm=float(self.range_vars["min"].get()),
                mid_rpm=float(self.range_vars["mid"].get()),
                max_rpm=float(self.range_vars["max"].get()))
        except (ValueError, PckError) as exc:
            messagebox.showerror("Valor invalido", str(exc))
            self.undo_stack.pop()
            return
        self._after_edit()
        self.set_status(f"Range {idx} aplicado (nao salvo ainda).")

    def apply_active_count(self):
        b = self._current_block()
        if not b or not self.editor:
            return
        self.push_undo("contagem de ranges")
        try:
            self.editor.set_block_scalar(b, "active_range_count", int(self.active_count_var.get()))
        except (ValueError, PckError) as exc:
            messagebox.showerror("Valor invalido", str(exc))
            self.undo_stack.pop()
            return
        self._after_edit()
        self.set_status("Contagem de ranges ativos aplicada.")

    # ---- curve editing ----
    def load_pending_curve(self):
        b = self._current_block()
        if not b:
            self.pending_segments = None
            self.refresh_seg_table()
            return
        c = b.curves.get(self.edit_curve_key.get())
        self.pending_segments = [list(s) for s in (c.segments if c else [])]
        self.refresh_seg_table()
        self.redraw_canvas()

    def refresh_seg_table(self):
        self.seg_tree.delete(*self.seg_tree.get_children())
        if not self.pending_segments:
            return
        for i, seg in enumerate(self.pending_segments):
            self.seg_tree.insert("", "end", iid=str(i),
                                 values=(i, *(f"{v:.6g}" for v in seg)))

    def on_seg_double_click(self, event):
        item = self.seg_tree.identify_row(event.y)
        col = self.seg_tree.identify_column(event.x)
        if not item or col == "#1" or self.pending_segments is None:
            return
        seg_i = int(item)
        field_i = int(col[1:]) - 2  # x0 is column #2
        if not (0 <= field_i < 6):
            return
        cur = self.pending_segments[seg_i][field_i]
        new = simple_prompt(self.root, f"Segmento {seg_i}, campo {['X0','Y0','CtrlX','CtrlY','X1','Y1'][field_i]}",
                            f"{cur:.6g}")
        if new is None:
            return
        try:
            self.pending_segments[seg_i][field_i] = float(new)
        except ValueError:
            return
        self.refresh_seg_table()
        self.redraw_canvas()

    def add_curve_segment(self):
        if self.pending_segments is None:
            return
        if len(self.pending_segments) >= CURVE_ROW_SLOTS:
            messagebox.showinfo("Limite", f"Maximo de {CURVE_ROW_SLOTS} segmentos por curva.")
            return
        if self.pending_segments:
            x0, y0 = self.pending_segments[-1][4], self.pending_segments[-1][5]
        else:
            x0, y0 = 0.0, 0.5
        x1 = min(1.0, x0 + 0.2)
        self.pending_segments.append([x0, y0, (x0 + x1) / 2, y0, x1, y0])
        self.refresh_seg_table()
        self.redraw_canvas()

    def remove_curve_segment(self):
        if self.pending_segments:
            self.pending_segments.pop()
            self.refresh_seg_table()
            self.redraw_canvas()

    def apply_curve(self):
        b = self._current_block()
        if not b or not self.editor or self.pending_segments is None:
            return
        self.push_undo(f"curva {self.edit_curve_key.get()}")
        try:
            self.editor.set_curve_segments(b, self.edit_curve_key.get(),
                                           [tuple(s) for s in self.pending_segments])
        except PckError as exc:
            messagebox.showerror("Erro", str(exc))
            self.undo_stack.pop()
            return
        self._after_edit()
        self.set_status(f"Curva {self.edit_curve_key.get()} aplicada (nao salva ainda).")

    def copy_curve(self):
        if self.pending_segments is None:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(json.dumps({"mc3_curve": self.edit_curve_key.get(),
                                                "segments": self.pending_segments}))
        self.set_status(f"Curva {self.edit_curve_key.get()} copiada ({len(self.pending_segments)} segmentos).")

    def paste_curve(self):
        if self.pending_segments is None:
            return
        try:
            data = json.loads(self.root.clipboard_get())
            segs = data["segments"]
            assert isinstance(segs, list) and all(len(s) == 6 for s in segs)
            segs = [[float(v) for v in s] for s in segs][:CURVE_ROW_SLOTS]
        except Exception:
            messagebox.showinfo("Colar curva", "A area de transferencia nao contem uma curva copiada daqui.")
            return
        self.pending_segments = segs
        self.refresh_seg_table()
        self.redraw_canvas()
        self.set_status(f"Curva colada ({len(segs)} segmentos) - use Aplicar curva para gravar.")

    # ------------------------------------------------------------------ canvas
    def _plot_geometry(self):
        w = max(10, self.canvas.winfo_width())
        h = max(10, self.canvas.winfo_height())
        ml, mr, mt, mb = 70, 24, 26, 48
        return w, h, ml, mr, mt, mb

    def _plot_bounds(self, block):
        if self.curve_scale_mode.get() == "fit":
            xs, ys = [], []
            for key, _l, _p, _r in CURVE_FIELDS:
                if not self.curve_visible[key].get():
                    continue
                segs = self._segments_for(block, key)
                for s in segs:
                    xs += [s[0], s[2], s[4]]
                    ys += [s[1], s[3], s[5]]
            if xs:
                x0, x1 = min(xs), max(xs)
                y0, y1 = min(ys), max(ys)
                if math.isclose(x0, x1):
                    x0, x1 = x0 - 0.5, x1 + 0.5
                if math.isclose(y0, y1):
                    y0, y1 = y0 - 0.5, y1 + 0.5
                px, py = (x1 - x0) * 0.06, (y1 - y0) * 0.1
                return x0 - px, x1 + px, y0 - py, y1 + py
        return 0.0, 1.0, 0.0, 1.0

    def _segments_for(self, block, key):
        """Pending segments for the curve under edit, stored data otherwise."""
        if key == self.edit_curve_key.get() and self.pending_segments is not None:
            return [tuple(s) for s in self.pending_segments]
        c = block.curves.get(key)
        return c.segments if c else []

    def redraw_canvas(self):
        c = getattr(self, "canvas", None)
        if c is None:
            return
        c.delete("all")
        w, h, ml, mr, mt, mb = self._plot_geometry()
        c.create_rectangle(0, 0, w, h, fill=self.PANEL, outline="")
        block = self._current_block()
        if not block:
            c.create_text(w / 2, h / 2, text="Selecione um bloco de audio para ver/editar curvas.",
                          fill=self.MUTED, font=("Segoe UI", 11))
            return
        pw, ph = max(1, w - ml - mr), max(1, h - mt - mb)
        xmin, xmax, ymin, ymax = self._plot_bounds(block)

        def sx(x):
            return ml + (x - xmin) / (xmax - xmin) * pw

        def sy(y):
            return mt + (1 - (y - ymin) / (ymax - ymin)) * ph

        self._sx, self._sy = sx, sy
        self._inv = lambda px, py: (xmin + (px - ml) / pw * (xmax - xmin),
                                    ymin + (1 - (py - mt) / ph) * (ymax - ymin))

        for i in range(6):
            gx = ml + i / 5 * pw
            c.create_line(gx, mt, gx, mt + ph, fill=self.GRID)
            val = xmin + i / 5 * (xmax - xmin)
            c.create_text(gx, mt + ph + 14, text=f"{val:.3g}", fill=self.MUTED, font=("Consolas", 9))
            if block.max_rpm_rec > block.min_rpm_rec and self.curve_scale_mode.get() == "global":
                rpm = block.min_rpm_rec + val * (block.max_rpm_rec - block.min_rpm_rec)
                c.create_text(gx, mt + ph + 28, text=f"{rpm:.0f}rpm", fill="#677085", font=("Consolas", 8))
        for i in range(5):
            gy = mt + i / 4 * ph
            c.create_line(ml, gy, ml + pw, gy, fill=self.GRID)
            val = ymax - i / 4 * (ymax - ymin)
            c.create_text(ml - 8, gy, text=f"{val:.3g}", anchor="e", fill=self.MUTED, font=("Consolas", 9))
        c.create_rectangle(ml, mt, ml + pw, mt + ph, outline="#565B6B")
        c.create_text(ml, 10, anchor="w", text=f"{block.label} | {block.bank_name}",
                      fill=self.FG, font=("Segoe UI", 10, "bold"))
        edit_key = self.edit_curve_key.get()
        c.create_text(ml + pw, 10, anchor="e",
                      text=f"editando: {edit_key} (arraste os pontos)", fill=self.ACCENT,
                      font=("Segoe UI", 9))

        legend_y = mt + 8
        for key, label, _p, _r in CURVE_FIELDS:
            if not self.curve_visible[key].get():
                continue
            segs = self._segments_for(block, key)
            if not segs:
                continue
            color = CURVE_COLORS.get(key, "#FFFFFF")
            width = 3 if key == edit_key else 2
            for seg in segs:
                x0, y0, cx, cy, x1, y1 = seg
                a, b_, c_ = fit_quadratic((x0, y0), (cx, cy), (x1, y1))
                lo, hi = (x0, x1) if x0 <= x1 else (x1, x0)
                steps = 24
                pts = []
                for i in range(steps + 1):
                    x = lo + (hi - lo) * i / steps
                    pts.append((sx(x), sy(a * x * x + b_ * x + c_)))
                for p1, p2 in zip(pts, pts[1:]):
                    c.create_line(*p1, *p2, fill=color, width=width)
            # knots + control points (edited curve only gets handles)
            for si, seg in enumerate(segs):
                for pi, (px, py) in enumerate([(seg[0], seg[1]), (seg[2], seg[3]), (seg[4], seg[5])]):
                    X, Y = sx(px), sy(py)
                    if key == edit_key:
                        r = 5
                        if pi == 1:
                            c.create_rectangle(X - r, Y - r, X + r, Y + r, outline=color, width=2)
                        else:
                            c.create_oval(X - r, Y - r, X + r, Y + r, fill=color, outline="#FFFFFF")
                    elif pi != 1:
                        c.create_oval(X - 3, Y - 3, X + 3, Y + 3, fill=color, outline="")
            c.create_rectangle(ml + 8, legend_y - 5, ml + 20, legend_y + 7, fill=color, outline="")
            c.create_text(ml + 26, legend_y + 1, anchor="w", text=f"{label} ({len(segs)})",
                          fill=self.FG, font=("Segoe UI", 9))
            legend_y += 18

    # ---- canvas dragging ----
    def on_canvas_press(self, event):
        if self.pending_segments is None or not self._current_block():
            return
        best = None
        for si, seg in enumerate(self.pending_segments):
            for pi, (px, py) in enumerate([(seg[0], seg[1]), (seg[2], seg[3]), (seg[4], seg[5])]):
                X, Y = self._sx(px), self._sy(py)
                d = ((X - event.x) ** 2 + (Y - event.y) ** 2) ** 0.5
                if d < 10 and (best is None or d < best[0]):
                    best = (d, si, pi)
        self.drag_target = best[1:] if best else None

    def on_canvas_drag(self, event):
        if not self.drag_target or self.pending_segments is None:
            return
        si, pi = self.drag_target
        x, y = self._inv(event.x, event.y)
        seg = self.pending_segments[si]
        old_x, old_y = seg[pi * 2], seg[pi * 2 + 1]
        seg[pi * 2], seg[pi * 2 + 1] = x, y
        # keep chain continuity: shared endpoints move together
        if pi == 0 and si > 0:
            prev = self.pending_segments[si - 1]
            if math.isclose(prev[4], old_x, abs_tol=1e-6) and math.isclose(prev[5], old_y, abs_tol=1e-6):
                prev[4], prev[5] = x, y
        if pi == 2 and si + 1 < len(self.pending_segments):
            nxt = self.pending_segments[si + 1]
            if math.isclose(nxt[0], old_x, abs_tol=1e-6) and math.isclose(nxt[1], old_y, abs_tol=1e-6):
                nxt[0], nxt[1] = x, y
        self.redraw_canvas()

    def on_canvas_release(self, _event):
        if self.drag_target:
            self.drag_target = None
            self.refresh_seg_table()

    def on_canvas_right_click(self, event):
        """Right-click on a knot deletes the point (merging segments); right-click
        near the curve line inserts a new point at that position."""
        if self.pending_segments is None or not self._current_block():
            return
        segs = self.pending_segments
        # 1) near a knot? -> delete
        for si, seg in enumerate(segs):
            for pi in (0, 2):  # only endpoints, control points can't be deleted
                X, Y = self._sx(seg[pi * 2]), self._sy(seg[pi * 2 + 1])
                if ((X - event.x) ** 2 + (Y - event.y) ** 2) ** 0.5 < 9:
                    self._delete_knot(si, pi)
                    return
        # 2) near the drawn curve? -> insert a point there
        x, y = self._inv(event.x, event.y)
        for si, seg in enumerate(segs):
            lo, hi = (seg[0], seg[4]) if seg[0] <= seg[4] else (seg[4], seg[0])
            if lo <= x <= hi:
                a, b_, c_ = fit_quadratic((seg[0], seg[1]), (seg[2], seg[3]), (seg[4], seg[5]))
                cy = a * x * x + b_ * x + c_
                if abs(self._sy(cy) - event.y) < 16:
                    self._insert_knot(si, x, cy)
                    return

    def _insert_knot(self, seg_index: int, x: float, y: float):
        segs = self.pending_segments
        if len(segs) >= CURVE_ROW_SLOTS:
            self.set_status(f"Limite de {CURVE_ROW_SLOTS} segmentos atingido; nao da para inserir ponto.")
            return
        seg = segs[seg_index]
        a, b_, c_ = fit_quadratic((seg[0], seg[1]), (seg[2], seg[3]), (seg[4], seg[5]))

        def ev(px):
            return a * px * px + b_ * px + c_

        left = [seg[0], seg[1], (seg[0] + x) / 2, ev((seg[0] + x) / 2), x, y]
        right = [x, y, (x + seg[4]) / 2, ev((x + seg[4]) / 2), seg[4], seg[5]]
        segs[seg_index:seg_index + 1] = [left, right]
        self.refresh_seg_table()
        self.redraw_canvas()
        self.set_status(f"Ponto inserido em x={x:.3g} (Aplicar curva para gravar).")

    def _delete_knot(self, seg_index: int, point_index: int):
        segs = self.pending_segments
        if point_index == 0 and seg_index > 0:
            seg_index, point_index = seg_index - 1, 2  # shared boundary: treat as end of previous
        if point_index == 2 and seg_index + 1 < len(segs):
            # merge this segment with the next one
            a, b = segs[seg_index], segs[seg_index + 1]
            mid_x = (a[0] + b[4]) / 2
            av, bv, cv = fit_quadratic((a[0], a[1]), (a[2], a[3]), (a[4], a[5]))
            mid_y = av * mid_x * mid_x + bv * mid_x + cv
            merged = [a[0], a[1], mid_x, mid_y, b[4], b[5]]
            segs[seg_index:seg_index + 2] = [merged]
        elif point_index == 0 and seg_index == 0 and len(segs) > 1:
            segs.pop(0)
        elif point_index == 2 and seg_index == len(segs) - 1 and len(segs) > 1:
            segs.pop()
        else:
            self.set_status("Nao da para apagar o unico segmento; use '- segmento'.")
            return
        self.refresh_seg_table()
        self.redraw_canvas()
        self.set_status("Ponto apagado (Aplicar curva para gravar).")

    # ------------------------------------------------------------------ banks/preview
    def _bank_dirs(self):
        dirs = list(self.extra_bank_dirs)
        if self.current_path:
            dirs += default_bank_search_dirs(self.current_path)
        return dirs

    def resolve_bank(self, bank_name: str):
        if not bank_name:
            return None
        key = bank_name.upper()
        if key in self.bank_cache:
            return self.bank_cache[key]
        bnk, td = find_bank_files(bank_name, self._bank_dirs())
        if not bnk:
            return None
        try:
            bank = BankSamples(bnk, td)
        except (BnkParseError, OSError) as exc:
            self.set_status(f"Falha ao carregar banco {bank_name}: {exc}")
            return None
        self.bank_cache[key] = bank
        self.bank_paths[key] = (bnk, td)
        return bank

    def update_preview_tab(self, block: AudioBlock):
        bank = self.resolve_bank(block.bank_name)
        self.samples_list.delete(0, tk.END)
        if bank is None:
            self.bank_status.configure(
                text=f"Banco '{block.bank_name}' nao encontrado. Use Bancos > Definir pasta extra.")
            return
        bnk, td = self.bank_paths[block.bank_name.upper()]
        self.bank_status.configure(text=f"Banco: {bnk}" + (f" | td: {os.path.basename(td)}" if td else ""))
        for name in bank.names():
            self.samples_list.insert(tk.END, name)
        lo = max(200.0, block.min_rpm_rec * 0.7)
        hi = max(block.max_rpm_rec * 1.15, lo + 500)
        self.rpm_scale.configure(from_=lo, to=hi)
        mid = (block.min_rpm_rec + block.max_rpm_rec) / 2 or 2000
        self.rpm_var.set(mid)
        self.rpm_label.configure(text=f"{mid:.0f}")
        self.refresh_perf_label()  # may widen the slider to the engine's real RPM range

    def set_banks_dir(self):
        d = filedialog.askdirectory(title="Pasta extra onde procurar .bnk/.td")
        if d:
            self.extra_bank_dirs.insert(0, d)
            self.bank_cache.clear()
            self.bank_paths.clear()
            b = self._current_block()
            if b:
                self.update_preview_tab(b)
            self.set_status(f"Pasta de bancos adicionada: {d}")

    def _play_wav_bytes(self, wav: bytes):
        """winsound nao aceita SND_MEMORY junto com SND_ASYNC, entao gravamos num
        arquivo temporario e tocamos por nome de arquivo (que suporta async)."""
        if winsound is None:
            messagebox.showinfo("Sem audio", "winsound indisponivel nesta plataforma.")
            return
        import tempfile
        winsound.PlaySound(None, winsound.SND_PURGE)  # para o som anterior antes de sobrescrever
        if self._tmp_wav is None:
            fd, path = tempfile.mkstemp(suffix=".wav", prefix="mc3studio_")
            os.close(fd)
            self._tmp_wav = path
            import atexit

            def _cleanup(p=path):
                try:
                    if winsound is not None:
                        winsound.PlaySound(None, winsound.SND_PURGE)
                    os.unlink(p)
                except OSError:
                    pass
            atexit.register(_cleanup)
        with open(self._tmp_wav, "wb") as f:
            f.write(wav)
        winsound.PlaySound(self._tmp_wav, winsound.SND_FILENAME | winsound.SND_ASYNC)

    def stop_audio(self):
        if winsound is not None:
            winsound.PlaySound(None, winsound.SND_PURGE)

    def play_bank_sample(self):
        b = self._current_block()
        sel = self.samples_list.curselection()
        if not b or not sel:
            return
        name = self.samples_list.get(sel[0])
        bank = self.resolve_bank(b.bank_name)
        if bank is None:
            return
        try:
            self._play_wav_bytes(sample_wav(bank, name))
            self.set_status(f"Tocando sample {name}")
        except PreviewError as exc:
            messagebox.showerror("Erro", str(exc))

    def play_selected_range_sample(self):
        if isinstance(self.selected, ProfileBlock):
            self._edit_profile_param(self.selected)
            return
        if isinstance(self.selected, RawAuxBlock):
            self._edit_aux_entry(self.selected)
            return
        b = self._current_block()
        sel = self.ranges_tree.selection()
        if not b or not sel:
            return
        r = b.ranges[int(sel[0])]
        name = r.sample_name.split(":", 1)[1] if ":" in r.sample_name else r.sample_name
        if not name:
            return
        bank = self.resolve_bank(b.bank_name)
        if bank is None:
            self.set_status(f"Banco '{b.bank_name}' nao encontrado para tocar o sample.")
            return
        try:
            self._play_wav_bytes(sample_wav(bank, name))
            self.set_status(f"Tocando sample {name}")
        except PreviewError as exc:
            messagebox.showerror("Erro", str(exc))

    def _render_and_play(self, render_fn, what: str):
        b = self._current_block()
        if not b:
            return
        bank = self.resolve_bank(b.bank_name)
        if bank is None:
            messagebox.showinfo("Sem banco", f"Banco '{b.bank_name}' nao encontrado.")
            return
        if self._render_thread and self._render_thread.is_alive():
            self.set_status("Ja ha uma renderizacao em andamento...")
            return
        self.set_status(f"Renderizando {what}...")
        result: dict = {}

        def work():
            try:
                mixer = EngineMixer(b, bank)
                result["wav"] = render_fn(mixer)
            except Exception as exc:  # noqa: BLE001 - show any render error in the status bar
                result["err"] = str(exc)

        self._render_thread = threading.Thread(target=work, daemon=True)
        self._render_thread.start()

        def poll():
            # tkinter isn't thread-safe: the worker only fills `result`, and this
            # poller (always on the main thread) touches the UI / plays the audio
            if self._render_thread and self._render_thread.is_alive():
                self.root.after(100, poll)
                return
            if "err" in result:
                self.set_status(f"Falha no preview: {result['err']}")
            elif "wav" in result:
                self._play_wav_bytes(result["wav"])
                self.set_status(f"Tocando {what}.")

        self.root.after(100, poll)

    def play_at_rpm(self):
        rpm = float(self.rpm_var.get())
        self._render_and_play(lambda m: m.render_constant(rpm, 2.0), f"RPM {rpm:.0f}")

    def play_sweep(self):
        self._render_and_play(lambda m: m.render_sweep(duration=6.0), "varredura de RPM")

    # ---- performance (vehsim) integration ----
    def get_perf(self, variant: str = None):
        """VehiclePerf do pck aberto (cacheada); None se o pck nao tiver vehsim."""
        variant = variant or self.perf_variant.get()
        if variant in self.perf_cache:
            return self.perf_cache[variant]
        perf = None
        if self.editor is not None:
            try:
                # parse from the edited buffer so performance edits elsewhere show up
                perf = parse_vehicle_perf(bytes(self.editor.buf), variant)
            except VehsimError:
                perf = None
        self.perf_cache[variant] = perf
        return perf

    def refresh_perf_label(self):
        perf = self.get_perf()
        if perf is None:
            self.perf_label.configure(text="(sem dados de performance neste pck)")
            return
        e, t = perf.engine, perf.trans
        self.perf_label.configure(
            text=f"Idle {e.idle_rpm:.0f} | Max real {e.max_rpm:.0f} RPM | {t.forward_gears} marchas | "
                 f"troca {t.gear_change_time:.2f}s")
        # RPM slider covers the engine's real range (audio was often recorded lower;
        # the game pitch-stretches beyond max_rpm_rec, and so does the preview)
        self.rpm_scale.configure(from_=max(200.0, e.idle_rpm * 0.5), to=e.max_rpm * 1.05)

    def play_gear_drive(self):
        perf = self.get_perf()
        if perf is None:
            messagebox.showinfo(
                "Sem performance",
                "Este pck nao tem dados vehsim legiveis (ou e um psppck).\n"
                "A simulacao de marchas precisa deles.")
            return
        self._render_and_play(
            lambda m: m.render_gear_drive(perf, duration=12.0),
            f"passagem de {perf.trans.forward_gears} marchas ({perf.variant})")

    def export_sweep_wav(self):
        b = self._current_block()
        if not b:
            return
        bank = self.resolve_bank(b.bank_name)
        if bank is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV", "*.wav")])
        if not path:
            return
        try:
            wav = EngineMixer(b, bank).render_sweep(duration=6.0)
            with open(path, "wb") as f:
                f.write(wav)
            self.set_status(f"WAV salvo: {path}")
        except PreviewError as exc:
            messagebox.showerror("Erro", str(exc))

    # ------------------------------------------------------------------ bank tools
    def show_bank_info(self):
        b = self._current_block()
        if not b:
            messagebox.showinfo("Info", "Selecione um bloco com banco primeiro.")
            return
        bnk, td = find_bank_files(b.bank_name, self._bank_dirs())
        if not bnk:
            messagebox.showinfo("Info", f"Banco '{b.bank_name}' nao encontrado.")
            return
        try:
            h = parse_bnk(bnk)
        except BnkParseError as exc:
            messagebox.showerror("Erro", str(exc))
            return
        lines = h.summary_lines()
        lines.append("")
        for s in h.streams:
            loop = f"loop {s.loop_start}-{s.loop_end}" if s.loop_flag else "sem loop"
            lines.append(f"#{s.index:2d} {s.name or '-':<20} {s.codec} {s.sample_rate}Hz {loop} {s.stream_size}B")
        messagebox.showinfo(f"Banco {b.bank_name}", "\n".join(lines))

    def demux_bank_dialog(self):
        b = self._current_block()
        bnk = td = None
        if b:
            bnk, td = find_bank_files(b.bank_name, self._bank_dirs())
        if not bnk:
            bnk = filedialog.askopenfilename(title="Escolher .bnk para extrair",
                                             filetypes=[("BNK", "*.bnk"), ("Todos", "*.*")])
            if not bnk:
                return
        out_dir = filedialog.askdirectory(title="Pasta de saida para os .genh + manifest")
        if not out_dir:
            return
        try:
            manifest = bnk_demux(bnk, out_dir, use_genh=True, td_path=td)
        except (BnkParseError, OSError) as exc:
            messagebox.showerror("Falha no DEMUX", str(exc))
            return
        messagebox.showinfo("DEMUX concluido",
                            f"Streams extraidos para:\n{out_dir}\n\nManifest: {manifest}\n\n"
                            "Substitua os .genh desejados (mesmo codec) e use Remontar banco (MUX).")

    def mux_bank_dialog(self):
        orig = filedialog.askopenfilename(title="Arquivo .bnk ORIGINAL (modelo)",
                                          filetypes=[("BNK", "*.bnk")])
        if not orig:
            return
        folder = filedialog.askdirectory(title="Pasta do DEMUX (contendo manifest.json)")
        if not folder:
            return
        manifest = os.path.join(folder, "manifest.json")
        if not os.path.exists(manifest):
            messagebox.showerror("Erro", f"manifest.json nao encontrado em {folder}")
            return
        out = filedialog.asksaveasfilename(title="Salvar novo .bnk como", defaultextension=".bnk",
                                           filetypes=[("BNK", "*.bnk")])
        if not out:
            return
        try:
            path, report = bnk_mux(orig, manifest, out)
        except (BnkMuxError, OSError) as exc:
            messagebox.showerror("Falha no MUX", str(exc))
            return
        self.bank_cache.clear()
        messagebox.showinfo("MUX concluido", f"Novo banco: {path}\n\n" + "\n".join(report[:12]))


def simple_prompt(parent, title, initial):
    """Minimal modal text prompt (avoids tkinter.simpledialog styling issues)."""
    win = tk.Toplevel(parent)
    win.title(title)
    win.transient(parent)
    win.grab_set()
    win.configure(bg="#1D1F26")
    tk.Label(win, text=title, bg="#1D1F26", fg="#E6E8EF").pack(padx=12, pady=(10, 4))
    var = tk.StringVar(value=initial)
    entry = tk.Entry(win, textvariable=var, bg="#242731", fg="#E6E8EF", insertbackground="#E6E8EF")
    entry.pack(padx=12, pady=4, fill=tk.X)
    entry.select_range(0, tk.END)
    entry.focus_set()
    result = []

    def ok(_e=None):
        result.append(var.get())
        win.destroy()

    def cancel(_e=None):
        win.destroy()

    entry.bind("<Return>", ok)
    entry.bind("<Escape>", cancel)
    row = tk.Frame(win, bg="#1D1F26")
    row.pack(pady=(4, 10))
    tk.Button(row, text="OK", command=ok, width=8).pack(side=tk.LEFT, padx=4)
    tk.Button(row, text="Cancelar", command=cancel, width=8).pack(side=tk.LEFT, padx=4)
    parent.wait_window(win)
    return result[0] if result else None


def main(argv):
    root = tk.Tk()
    app = AudioStudio(root)
    if len(argv) >= 2 and Path(argv[1]).is_file():
        app.load_pck(Path(argv[1]))
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
