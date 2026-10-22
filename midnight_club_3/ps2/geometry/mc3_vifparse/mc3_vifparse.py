"""Parser de VIF de verdade: STCYCL/STROW/UNPACK com mascara.

O meu leitor antigo assumia o layout do proprio emissor (UNPACK direto 0x69) e
lia os valores de preenchimento do STROW como se fossem vertices. Os pacotes que
o JOGO monta usam STROW + UNPACK, e o unpack de posicao e V3-16 mascarado.
"""
import struct

def unpack_elems(vn, vl):
    return (vn + 1), (32 >> vl if vl else 32)

def parse_packet(d, off, qw):
    """Devolve lista de (addr, [valores decodificados]) dos UNPACK do packet."""
    fim = off + 16 * qw
    o = off
    row = [0, 0, 0, 0]
    out = []
    while o + 4 <= fim:
        code = struct.unpack_from('<I', d, o)[0]
        cmd = (code >> 24) & 0xFF
        num = (code >> 16) & 0xFF
        imm = code & 0xFFFF
        o += 4
        if cmd == 0x00:                      # NOP
            continue
        if cmd == 0x01:                      # STCYCL
            continue
        if cmd == 0x30:                      # STROW: 4 words
            if o + 16 <= fim:
                row = list(struct.unpack_from('<4i', d, o))
            o += 16
            continue
        if cmd in (0x31, 0x32, 0x33):        # STCOL/STMASK/STMOD-ish
            o += 16 if cmd == 0x31 else 4
            continue
        if (cmd & 0x60) == 0x60:             # UNPACK
            vn = (cmd >> 2) & 3
            vl = cmd & 3
            n_el, bits = unpack_elems(vn, vl)
            addr = imm & 0x3FF
            cnt = num if num else 256
            vals = []
            if bits == 16:
                need = cnt * n_el * 2
                if o + need <= fim:
                    raw = struct.unpack_from('<%dh' % (cnt * n_el), d, o)
                    vals = [raw[i * n_el:(i + 1) * n_el] for i in range(cnt)]
                o += need
            elif bits == 32:
                need = cnt * n_el * 4
                if o + need <= fim:
                    raw = struct.unpack_from('<%di' % (cnt * n_el), d, o)
                    vals = [raw[i * n_el:(i + 1) * n_el] for i in range(cnt)]
                o += need
            elif bits == 8:
                need = cnt * n_el
                if o + need <= fim:
                    raw = struct.unpack_from('<%db' % (cnt * n_el), d, o)
                    vals = [raw[i * n_el:(i + 1) * n_el] for i in range(cnt)]
                o += need
            o = (o + 3) & ~3
            out.append((addr, n_el, bits, vals, list(row)))
            continue
        break                                 # comando desconhecido: para
    return out
