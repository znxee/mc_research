# `tools/experimental/`

Scratch space for the Midnight Club 3 (PS2, Dub Edition Remix) toolkit. What
lives here is either a **library** the finished tools import, or a **probe**
written to answer one question about the game and kept because the answer is
recorded in its docstring.

Nothing here writes next to itself. **Every generated file goes to
`tools/output/`** (see `tools/mc3_saida.py`); pass an explicit `--saida`/`--out`
to override.

The finished tools live one directory up. Run them from anywhere:

```
python ../mc3_city_build.py --doador CITY.pck --saida out.pck
```

---

## The library

### `mc2_to_mc3.py`
Converts Midnight Club **2** geometry (`.xmod`, plain text) into an MC3 PS2 city
mesh, and is imported by almost everything else. Also usable directly:

```
python mc2_to_mc3.py --alvo MESHNAME --xmod MODEL.xmod --saida out.pck --escala 1.0
```

Module-level switches the importers set instead of passing arguments:

| name | meaning |
|---|---|
| `UV_FIXO` | one constant UV for every vertex — flat surface, good for judging shape |
| `NORMAIS` | emit the ITOP+2 normal stream (only 7.3% of retail city blocks have it) |
| `LUZ` | per-vertex palette index, 0..255. **Not a colour** — an index into the two 256-entry palettes at `MapRoot+0x2C`/`+0x30` |
| `MAX_VERTS` / `MAX_BLOCKS` | 48 and 88, measured across atlanta's 1353 city meshes |

Key functions: `read_xmod`, `strips_to_blocks` (MC2 hands out hundreds of
4-vertex strips; these get stitched with degenerate bridges into blocks that
respect both retail limits), `make_block` (one VIF packet, including the 16-byte
tail that closes it), `Pck` (load-in-place file with `append`/`save`).

---

## The probes

Each answers one question. They take `--saida` and otherwise name their own
output inside `tools/output/`.

| script | the question it answers |
|---|---|
| `teste_minimo.py` | what is the smallest change to a city that still loads |
| `teste_layout.py` | how the block/group tables have to be laid out |
| `teste_mesh_novo.py` | can a mesh be appended rather than edited in place |
| `teste_pipeline.py` | does the whole MC2 → MC3 path survive end to end |
| `teste_conta.py` | do the counts in the mesh header have to agree |
| `teste_plumbing.py` | which pointers the loader actually follows |
| `teste_vu.py`, `teste_vu2.py` | VU1 microcode and the city vertex packet |
| `city_roundtrip.py` | read a city, write it back, compare |
| `verify_mc2.py` | sanity-check the MC2 side before converting |

---

## The finished tools (one directory up)

| tool | what it does |
|---|---|
| `mc3_city_build.py` | builds a city `.pck` **from scratch**, or grafts one generated piece into a real city (`--enxerta paletas\|shaders\|hood\|hood1\|hood2`) |
| `mc3_place_sim.py` | **runs the loader's Place walk on the PC.** The single most useful tool here: it reports what the game would hang on, before booting |
| `mc3_hood_fill.py` | replaces every unique mesh of one hood, or ports a whole MC2 neighbourhood (`--mc2hood`) |
| `mc3_city_strip.py` | empties a city, keeping what matches `--manter` / `--perto` |
| `mc3_view.py` | renders a `.pck` to HTML/WebGL |
| `mc3_symbols.py` | carries function names from the 2004 alpha build to the retail ELF |
| `mc3_tex.py` | textures: `.tex`, flash `.pck`, and **pf05 packs** (`.ppf`) |
| `mc3_ida.py` | drives IDA headless — decompile, disasm, vtable, xrefs, script |

---

## Two rules worth keeping

**Run any new checker on an untouched retail file first.** A checker that fails
the shipped game is measuring itself, not your file. That has already happened
three times here — an AABB test, a vertex-count bound, and a dangling-pointer
sweep all rejected atlanta before they were corrected.

**"Empty" has two different shapes, and only the consumer's code says which.**
A field that is dereferenced without a guard needs a valid object with a zero
count; a field walked by `while (ptr)` or `if (ptr)` needs a plain NULL. Writing
a valid empty object where the code expects NULL makes a constructor run once
over zeros — which is a real crash that took a boot to find.
