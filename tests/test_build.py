import btlz
import build
import enfont
import insert
import tilemap
from conftest import ROOT
from extract import read_tsv


def test_identity_build(rom):
    out, writes = build.build(rom, {})
    assert writes == []
    assert out == rom


def test_compress_roundtrip(rom):
    for i in range(build.NRES):
        data, _ = btlz.decompress(rom, btlz.res_offset(rom, i))
        packed = btlz.compress(data)
        assert btlz.decompress(packed, 0) == (data, len(packed)), hex(i)


def test_recompress_all_decodes_same(rom):
    out, writes = build.build(rom, {}, recompress_all=True)
    assert len(out) == build.EXP_END
    moved = [w for w in writes if w.endswith("-ptr")]
    assert moved  # some resources grow and must relocate to banks F0-FF
    for i in range(build.NRES):
        assert btlz.decompress(out, btlz.res_offset(out, i))[0] == btlz.decompress(rom, btlz.res_offset(rom, i))[0]
    c = build.CHECKSUM
    assert out[:c] + out[c + 4:btlz.TABLE] == rom[:c] + rom[c + 4:btlz.TABLE]  # code before the table untouched
    assert build.verify(rom, out, writes) == []


def test_checksum(rom):
    assert build.checksum(rom) == rom[build.CHECKSUM:build.CHECKSUM + 4]  # 3 MB mirrored sum


def test_english_build(rom):
    """The real build (this checkout's script): romdiff-clean with its write log inside tools/ranges.txt, header
    checksum right, every resource pointer lands on a resource that decodes to what insert.py made, and every
    block with English is rebuilt."""
    edits = insert.edits(rom=rom)
    out, writes = build.build(rom, edits)
    assert build.verify(rom, out, writes) == []
    assert build.checksum(out) == out[build.CHECKSUM:build.CHECKSUM + 4]
    for i in range(build.NRES):
        want = edits.get(i) or btlz.decompress(rom, btlz.res_offset(rom, i))[0]
        assert btlz.decompress(out, btlz.res_offset(out, i))[0] == want, hex(i)
    english = {b for b in tilemap.TABLES if any(r[3] for r in read_tsv(ROOT / "script" / f"{b:02X}.tsv"))}
    assert english <= set(edits)
    assert {enfont.FONT_OF[b] for b in english} <= set(edits)


def test_verify_catches(rom):
    out, writes = build.build(rom, {0x47: b"\x00" * 0x1000})
    bad = bytearray(out)
    bad[0x8000] ^= 1  # code byte, no write behind it
    assert any("outside" in e for e in build.verify(rom, bytes(bad), writes))
    assert any("outside tools/ranges.txt" in e for e in build.verify(rom, out, writes + ["8000 00 01 stray"]))


def test_edit_relocates_when_too_big(rom):
    data, _ = btlz.decompress(rom, btlz.res_offset(rom, 0x47))
    noisy = bytes((i * 7919) & 0xFF for i in range(len(data)))  # incompressible: cannot fit the old slot
    out, _ = build.build(rom, {0x47: noisy})
    assert btlz.res_offset(out, 0x47) == build.EXP_START
    assert btlz.decompress(out, build.EXP_START)[0] == noisy
