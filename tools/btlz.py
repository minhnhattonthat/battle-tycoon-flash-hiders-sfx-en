"""Battle Tycoon resource archive + RLE codec (docs/re/compression.md).

Resource table at file 0x10082 (C1:0082), 4 bytes per entry: offset16, bank16; CPU bank = bank16 + $CB.
Each resource: 'F' (to WRAM) or 'V' (to VRAM), size16 (output bytes), word, word w (f0 = lo, f1 = hi), byte f2,
then commands until size bytes are written. Decoder: C0:1039 (WRAM) / C0:0Exx (VRAM, same codec).
Command byte c:
  c & 0xC0 == 0xC0: count by c & 0x30 (00: (c&15)+1, 10: ((c&15)<<8 | b)+1, 20: BE word+1); copy count literal
                    bytes. c & 0x30 == 0x30: (c&15)+1 bytes of f2.
  else, count by c & 0xC0 (00: (c&15)+1, 40: ((c&15)<<8 | b)+1, 80: BE word+1), then
    c & 0x30 == 0x30: read word w; count bytes of repeating [lo, hi]
    c & 0x30 == 0x00: read byte v; count bytes of v.   0x10: f0.   0x20: f1.
"""
import sys

TABLE = 0x10082


def res_offset(rom, i):
    e = TABLE + 4 * i
    o = rom[e] | rom[e + 1] << 8
    bank = (rom[e + 2] | rom[e + 3] << 8) + 0xCB
    return ((bank & 0x3F) << 16) | o


def decompress(rom, off):
    """Return (data, end_offset)."""
    p = off
    magic = rom[p]
    assert magic in (0x46, 0x56), hex(magic)
    size = rom[p + 1] | rom[p + 2] << 8
    f0, f1, f2 = rom[p + 5], rom[p + 6], rom[p + 7]
    p += 8
    out = bytearray()
    while len(out) < size:
        c = rom[p]; p += 1
        if c & 0xC0 == 0xC0:
            k = c & 0x30
            if k == 0x30:
                out += bytes([f2]) * ((c & 15) + 1)
                continue
            if k == 0x00:
                n = (c & 15) + 1
            elif k == 0x10:
                n = ((c & 15) << 8 | rom[p]) + 1; p += 1
            else:
                n = (rom[p] << 8 | rom[p + 1]) + 1; p += 2
            out += rom[p:p + n]; p += n
            continue
        k = c & 0xC0
        if k == 0x00:
            n = (c & 15) + 1
        elif k == 0x40:
            n = ((c & 15) << 8 | rom[p]) + 1; p += 1
        else:
            n = (rom[p] << 8 | rom[p + 1]) + 1; p += 2
        v = c & 0x30
        if v == 0x30:
            pat = rom[p:p + 2]; p += 2
            out += (pat * (n // 2 + 1))[:n]
        else:
            if v == 0x00:
                b = rom[p]; p += 1
            else:
                b = f0 if v == 0x10 else f1
            out += bytes([b]) * n
    return bytes(out[:size]), p


def _count(base, v, n):
    """Command bytes for a fill (base = 0x00) of n bytes with source v (0x00 byte, 0x10 f0, 0x20 f1, 0x30 word)."""
    n -= 1
    if n < 16:
        return bytes([v | n])
    if n < 4096:
        return bytes([0x40 | v | n >> 8, n & 0xFF])
    return bytes([0x80 | v, n >> 8, n & 0xFF])


def _literal(chunk):
    n = len(chunk) - 1
    if n < 16:
        return bytes([0xC0 | n]) + chunk
    if n < 4096:
        return bytes([0xD0 | n >> 8, n & 0xFF]) + chunk
    return bytes([0xE0, n >> 8, n & 0xFF]) + chunk


def compress(data):
    """Greedy encoder for the format above; decompress(compress(d)) == d (not byte-identical to the original's
    encoder, whose header bytes don't follow byte frequency; unchanged resources keep their original bytes)."""
    assert 0 < len(data) <= 0xFFFF, len(data)
    runs = {}
    i = 0
    while i < len(data):  # weigh each byte by the bytes it covers in runs of 2+
        j = i
        while j < len(data) and data[j] == data[i]:
            j += 1
        if j - i >= 2:
            runs[data[i]] = runs.get(data[i], 0) + j - i
        i = j
    top = sorted(runs, key=lambda b: -runs[b]) + [b for b in range(256) if b not in runs]
    f0, f1, f2 = top[:3]
    out = bytearray([0x46, len(data) & 0xFF, len(data) >> 8, 0, 0, f0, f1, f2])
    lit = bytearray()

    def flush():
        while lit:  # a literal command carries at most 65536 bytes
            out.extend(_literal(bytes(lit[:0x10000])))
            del lit[:0x10000]

    i, n = 0, len(data)
    while i < n:
        b = data[i]
        r = 1
        while i + r < n and data[i + r] == b:
            r += 1
        w = 2  # length of the alternating [data[i], data[i+1]] run
        while i + w < n and data[i + w] == data[i + (w & 1)]:
            w += 1
        if i + 1 >= n:
            w = 1
        if b in (f0, f1, f2) and r >= 2 or r >= 3 and r >= w:
            flush()
            if b == f2 and r <= 16 and b not in (f0, f1):
                out.append(0xF0 | r - 1)
            elif b in (f0, f1):
                out += _count(0, 0x10 if b == f0 else 0x20, r)
            else:
                out += _count(0, 0x00, r) + bytes([b])
            i += r
        elif w >= 4:
            flush()
            out += _count(0, 0x30, w) + data[i:i + 2]
            i += w
        else:
            lit.append(b)
            i += 1
    flush()
    return bytes(out)


if __name__ == "__main__":
    rom = open(sys.argv[1], "rb").read()
    i = int(sys.argv[2], 16)
    data, end = decompress(rom, res_offset(rom, i))
    print(f"res {i:#x} at {res_offset(rom, i):#x}..{end:#x} -> {len(data):#x} bytes", file=sys.stderr)
    if len(sys.argv) > 3:
        open(sys.argv[3], "wb").write(data)
