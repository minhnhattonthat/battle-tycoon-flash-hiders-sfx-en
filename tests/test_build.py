import btlz
import build


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
    assert out[:btlz.TABLE] == rom[:btlz.TABLE]  # code before the table untouched


def test_edit_relocates_when_too_big(rom):
    data, _ = btlz.decompress(rom, btlz.res_offset(rom, 0x47))
    noisy = bytes((i * 7919) & 0xFF for i in range(len(data)))  # incompressible: cannot fit the old slot
    out, _ = build.build(rom, {0x47: noisy})
    assert btlz.res_offset(out, 0x47) == build.EXP_START
    assert btlz.decompress(out, build.EXP_START)[0] == noisy
