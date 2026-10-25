import btlz

NRES = 0xB3


def test_resources_decode_back_to_back(rom):
    # every resource decodes to its declared size and ends exactly where the next one starts
    pos = btlz.res_offset(rom, 0)
    assert pos == 0x0B0000
    for i in range(NRES):
        assert btlz.res_offset(rom, i) == pos, hex(i)
        data, pos = btlz.decompress(rom, pos)
        assert len(data) == rom[btlz.res_offset(rom, i) + 1] | rom[btlz.res_offset(rom, i) + 2] << 8
    assert pos == 0x1F9D51


def test_registration_text_line(rom):
    # res 0x47 line 23 = "あなたの登録された" as font-0x46 cells (verified on screen)
    data, _ = btlz.decompress(rom, btlz.res_offset(rom, 0x47))
    words = [data[i] | data[i + 1] << 8 for i in range(0x580, 0x580 + 0x40, 2)]
    assert words[2:20] == [0x18C, 0x18D, 0x1E4, 0x1E5, 0x1CA, 0x1CB, 0x1EC, 0x1ED, 0x2EC, 0x2ED, 0x2EE, 0x2EF,
                           0x1C0, 0x1C1, 0x22E, 0x22F, 0x1CA, 0x1CB]
