"""extract.py: original ROM text blocks -> script/<BB>.tsv (id, kind, jp, en), one row per line or field.

    python -X utf8 tools/extract.py
Re-running keeps every existing `en` cell (matched by id) and refuses to drop a row that has one.
Format, ids and kinds: script/README.md. Codec: tools/tilemap.py, tables tbl/*.tbl.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import check_rom  # noqa: E402
import tilemap  # noqa: E402

SCRIPT = ROOT / "script"
HEADER = "id\tkind\tjp\ten"


def read_tsv(path):
    """[(id, kind, jp, en)] from a script file."""
    rows = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines()[1:], 2):
        f = line.split("\t")
        if len(f) != 4:
            raise ValueError(f"{path.name}:{n}: {len(f)} fields, want 4")
        rows.append(tuple(f))
    return rows


def main():
    check_rom.check()
    rom = tilemap.ROOT.joinpath("rom", "Battle Tycoon - Flash Hiders SFX (Japan) (Rev 1).sfc").read_bytes()
    SCRIPT.mkdir(exist_ok=True)
    total = 0
    for b in sorted(tilemap.TABLES):
        path = SCRIPT / f"{b:02X}.tsv"
        old = {r[0]: r[3] for r in read_tsv(path)} if path.exists() else {}
        rows = tilemap.entries(b, tilemap.block_data(rom, b), tilemap.load_table(b))
        lost = [i for i, en in old.items() if en and i not in {r[0] for r in rows}]
        if lost:
            sys.exit(f"{path.name}: would drop translated rows {lost[:5]}")
        path.write_text("\n".join([HEADER] + [f"{i}\t{k}\t{jp}\t{old.get(i, '')}" for i, k, jp in rows]) + "\n",
                        encoding="utf-8")
        total += len(rows)
        print(f"{path.relative_to(ROOT)}: {len(rows)} rows")
    print(f"{total} rows")


if __name__ == "__main__":
    main()
