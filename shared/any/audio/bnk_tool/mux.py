"""MUX: rebuild a .bnk from an original file used as template + a manifest.json
(produced by demux.py, possibly edited) + a folder of stream files (originals or
user-supplied replacements in the same codec). No audio is re-encoded: raw stream
bytes are spliced in as-is, and only offset/size table fields are patched."""
import json
import os
import struct

from .extradata_codec import patch_extradata
from .genh import is_genh_file, read_genh, GenhError
from .ps_adpcm import set_ps_adpcm_loop, clear_ps_adpcm_loop
from .spu_pitch import sample_rate_to_center
from .td import generate_td_from_manifest


class BnkMuxError(Exception):
    pass


def _pack_at(buf: bytearray, offset: int, size: int, value: int, big_endian: bool):
    fmt = {1: "B", 2: "H", 4: "I", 8: "Q"}[size]
    struct.pack_into((">" if big_endian else "<") + fmt, buf, offset, value & ((1 << (size * 8)) - 1))


def _unpack_at(buf, offset: int, size: int, big_endian: bool):
    fmt = {1: "B", 2: "H", 4: "I", 8: "Q"}[size]
    return struct.unpack_from((">" if big_endian else "<") + fmt, buf, offset)[0]


def load_manifest(manifest_path: str) -> dict:
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def mux(original_bnk_path: str, manifest_path: str, out_path: str, overrides: dict = None,
        td_renames: dict = None, write_td: bool = True) -> str:
    """
    original_bnk_path: the untouched .bnk this manifest was extracted from (used as template).
    manifest_path: manifest.json from demux() (in the folder holding the stream files).
    out_path: where to write the rebuilt .bnk.
    overrides: optional {stream_index: {"loop_start":int, "loop_end":int, "loop_length":int,
               "num_samples":int, "channels":int, "atrac9_info":int, "loop_flag":bool}}
    td_renames: optional {sound_index: new_name} to relabel a sound in the regenerated
                .td sidecar without touching the .bnk itself (patch-in-place can't add or
                remove sounds, only rename/replace existing ones).
    write_td: if the manifest carries per-stream sound_index info, also write an updated
              .td file (same basename as out_path) so the game can still find sounds by name.
    """
    overrides = overrides or {}
    manifest = load_manifest(manifest_path)
    manifest_dir = os.path.dirname(os.path.abspath(manifest_path))

    with open(original_bnk_path, "rb") as f:
        original = f.read()

    if len(original) != manifest["source_size"]:
        raise BnkMuxError(
            f"o arquivo original fornecido tem tamanho diferente do esperado pelo manifest "
            f"({len(original)} vs {manifest['source_size']}); use o .bnk original correto como template")

    big_endian = manifest["big_endian"]
    data_offset = manifest["data_offset"]
    data_size = manifest["data_size"]
    sblk_version = manifest["sblk_version"]

    buf = bytearray(original)

    all_streams = manifest["streams"]
    zlsd_streams = [s for s in all_streams if s.get("is_zlsd")]
    streams = sorted([s for s in all_streams if not s.get("is_zlsd")], key=lambda s: s["entry_data_offset"])

    report = []
    for s in zlsd_streams:
        idx = s["index"]
        ov = overrides.get(idx, overrides.get(str(idx), {}))
        stream_file = ov.get("file")
        if stream_file:
            report.append(
                f"aviso: stream #{idx} vem da secao ZLSD (prefetch externo); MUX ainda nao da suporte a "
                f"substituir esses streams, a substituicao fornecida foi ignorada")

    new_data = bytearray()
    cursor = data_offset
    running_delta = 0

    for s in streams:
        idx = s["index"]
        entry_pos = s["entry_data_offset"]
        old_total = s["entry_total_size"]

        if entry_pos < cursor:
            raise BnkMuxError(f"stream #{idx}: sobreposicao detectada na secao de dados (offsets inconsistentes)")

        # verbatim gap/padding before this entry, if any
        if entry_pos > cursor:
            new_data += original[cursor:entry_pos]

        ov = dict(overrides.get(idx, overrides.get(str(idx), {})))

        stream_file = ov.get("file") or s["file"]
        if not os.path.isabs(stream_file):
            stream_file = os.path.join(manifest_dir, stream_file)
        with open(stream_file, "rb") as sf:
            raw_file_bytes = sf.read()

        auto_ov = {}
        extradata_len = len(s["extradata_hex"]) // 2
        bitstream_loop_codec = s["codec"] in ("PSX", "HEVAG") and extradata_len == 0 and not s.get("embedded_header")

        if is_genh_file(raw_file_bytes):
            try:
                gh = read_genh(raw_file_bytes)
            except GenhError as e:
                raise BnkMuxError(f"stream #{idx}: arquivo .genh invalido ({e})")
            payload = raw_file_bytes[gh["start_offset"]:gh["start_offset"] + gh["data_size"]]

            if gh["channels"] != s["channels"]:
                auto_ov["channels"] = gh["channels"]

            loop_changed = (gh["loop_flag"] != s.get("loop_flag") or
                            (gh["loop_flag"] and (gh["loop_start_sample"] != s.get("loop_start")
                                                   or gh["loop_end_sample"] != s.get("loop_end"))))
            if loop_changed and bitstream_loop_codec:
                if gh["loop_flag"]:
                    payload, ok = set_ps_adpcm_loop(payload, s["channels"], s["interleave"],
                                                     gh["loop_start_sample"], gh["loop_end_sample"])
                    if ok:
                        report.append(
                            f"stream #{idx}: loop do .genh gravado no fluxo PS-ADPCM "
                            f"({gh['loop_start_sample']}-{gh['loop_end_sample']})")
                    else:
                        report.append(
                            f"aviso: stream #{idx}: loop do .genh ({gh['loop_start_sample']}-"
                            f"{gh['loop_end_sample']}) nao cai em limite de frame (multiplo de 28 "
                            f"amostras); loop nao foi alterado")
                else:
                    payload = clear_ps_adpcm_loop(payload, s["channels"], s["interleave"])
                    report.append(f"stream #{idx}: loop removido do fluxo PS-ADPCM")
            elif loop_changed:
                auto_ov["loop_flag"] = gh["loop_flag"]
                if gh["loop_flag"]:
                    auto_ov["loop_start"] = gh["loop_start_sample"]
                    auto_ov["loop_length"] = max(0, gh["loop_end_sample"] - gh["loop_start_sample"])

            if s["codec"] == "MPEG":
                auto_ov["num_samples"] = gh["num_samples"]

            sr_field_kind = "float" if s.get("sample_rate_float_field") else (
                "center" if s.get("center_note_field") else None)
            if sr_field_kind and gh["sample_rate"] and gh["sample_rate"] != s["sample_rate"]:
                ov.setdefault("sample_rate", gh["sample_rate"])
        else:
            payload = raw_file_bytes

        ov = {**auto_ov, **ov}

        if "sample_rate" in ov:
            target_sr = ov["sample_rate"]
            if s.get("sample_rate_float_field"):
                f = s["sample_rate_float_field"]
                struct.pack_into((">" if big_endian else "<") + "f", buf, f["offset"], float(target_sr))
                report.append(f"stream #{idx}: sample_rate ajustado para {target_sr} Hz")
            elif s.get("center_note_field") and s.get("center_fine_field"):
                cn, cf, achieved = sample_rate_to_center(target_sr)
                _pack_at(buf, s["center_note_field"]["offset"], 1, cn, big_endian)
                _pack_at(buf, s["center_fine_field"]["offset"], 1, cf, big_endian)
                report.append(f"stream #{idx}: sample_rate ajustado para {achieved} Hz (pedido: {target_sr} Hz)")
            else:
                report.append(
                    f"aviso: stream #{idx}: sample_rate pedido ({target_sr} Hz) nao pode ser aplicado "
                    f"(esta versao nao guarda sample_rate por stream)")

        postdata = b"\x00" * s["postdata_size"]

        if s.get("embedded_header"):
            # extradata_hex here is [u64 name_size][name][u64 remaining_size][real extradata].
            # Reuse the name-header bytes verbatim and only patch the "remaining size" field,
            # to avoid re-encoding the name ourselves.
            full_prefix = bytearray(bytes.fromhex(s["extradata_hex"]))
            name_size = s["stream_name_size"]
            remaining_off = 8 + name_size
            real_extradata = bytearray(full_prefix[remaining_off + 8:])
            if auto_ov and len(real_extradata) == 0:
                report.append(
                    f"aviso: stream #{idx}: loop/channels do .genh nao puderam ser aplicados (este stream "
                    f"nao tem metadados extras na tabela para guardar isso)")
            if ov:
                real_extradata = patch_extradata(s["codec"], big_endian, real_extradata, ov)
            new_remaining = len(real_extradata) + len(payload) + len(postdata)
            fmt = ">Q" if big_endian else "<Q"
            struct.pack_into(fmt, full_prefix, remaining_off, new_remaining)
            entry_bytes = bytes(full_prefix[:remaining_off + 8]) + bytes(real_extradata) + payload + postdata
        else:
            extradata = bytearray(bytes.fromhex(s["extradata_hex"]))
            if auto_ov and len(extradata) == 0:
                report.append(
                    f"aviso: stream #{idx}: loop/channels do .genh nao puderam ser aplicados (este codec/"
                    f"versao nao guarda esses metadados na tabela; loop de PS-ADPCM fica embutido no "
                    f"proprio fluxo de audio)")
            if ov:
                extradata = patch_extradata(s["codec"], big_endian, extradata, ov)
            entry_bytes = bytes(extradata) + payload + postdata

        new_total = len(entry_bytes)
        delta = new_total - old_total

        new_relative_offset = (entry_pos - data_offset) + running_delta

        off_field = s.get("stream_offset_field")
        if off_field:
            _pack_at(buf, off_field["offset"], off_field["size"], new_relative_offset, big_endian)

        size_field = s.get("stream_size_field")
        size_field_was_explicit = s.get("stream_size_field_original_value", 0) != 0
        if size_field and size_field_was_explicit:
            _pack_at(buf, size_field["offset"], size_field["size"], new_total, big_endian)
        elif delta != 0 and not s.get("embedded_header"):
            report.append(
                f"aviso: stream #{idx} mudou de tamanho; este banco usa deteccao por varredura (campo de "
                f"tamanho fica 0 no original e permanece 0), entao o novo audio precisa terminar com um "
                f"frame de silencio/fim valido para o tamanho ser detectado corretamente")

        flags_field = s.get("stream_flags_field")
        if flags_field and "loop_flag" in ov:
            cur_flags = _unpack_at(buf, flags_field["offset"], flags_field["size"], big_endian)
            if ov["loop_flag"]:
                cur_flags |= 0x40
            else:
                cur_flags &= ~0x40
            _pack_at(buf, flags_field["offset"], flags_field["size"], cur_flags, big_endian)

        new_data += entry_bytes
        cursor = entry_pos + old_total
        running_delta += delta

        if delta != 0:
            report.append(f"stream #{idx}: tamanho {old_total} -> {new_total} bytes (delta {delta:+d})")

    # trailing gap after the last entry
    if cursor < data_offset + data_size:
        new_data += original[cursor:data_offset + data_size]
    elif cursor > data_offset + data_size:
        raise BnkMuxError("streams ultrapassam o tamanho original da secao de dados (manifest inconsistente)")

    new_data_size = len(new_data)
    total_delta = new_data_size - data_size

    _pack_at(buf, 0x14, 4, new_data_size, big_endian)

    zlsd_offset = manifest.get("zlsd_offset") or 0
    if zlsd_offset and zlsd_offset > data_offset:
        _pack_at(buf, 0x18, 4, zlsd_offset + total_delta, big_endian)
        # zlsd internal table also carries an offset field per zlsd-stream; those are
        # relative to each zlsd entry itself (not to data_offset) so they don't shift.

    out_bytes = bytes(buf[:data_offset]) + bytes(new_data) + bytes(buf[data_offset + data_size:])

    with open(out_path, "wb") as f:
        f.write(out_bytes)

    if write_td and any(s.get("sound_index") is not None for s in all_streams):
        td_text = generate_td_from_manifest(manifest, renames=td_renames)
        td_out_path = os.path.splitext(out_path)[0] + ".td"
        with open(td_out_path, "w", encoding="latin-1") as f:
            f.write(td_text)
        report.append(f".td atualizado escrito em: {td_out_path}")

    return out_path, report
