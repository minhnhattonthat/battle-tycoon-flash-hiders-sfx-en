"""release.py: build -> tests -> smoke -> jp_left -> visual-QA gate -> BPS (re-applied, compared) -> zip.

    python -X utf8 tools/release.py [--version 1.0] [--force]

Stops at the first failure. Writes release/BattleTycoon_EN_v<version>.{bps,zip} + README.txt (local, gitignored)
and keeps the playable patched image in build/bt_en_v<version>.sfc. Refuses to overwrite an existing version's
files without --force. The build writes the header checksum itself (build.py). The QA tour is tools/tour.py; this
script refuses a build whose sha1 differs from the one the full tour shot (work/qa/tour/rom.sha1). The debug tool
is Lua only (tools/debug/warp.lua) and the release build takes no --marker/--qa, so no debug code is in the ROM.
Never publishes anything.
"""
import argparse
import hashlib
import re
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import enfont  # noqa: E402
import tilemap  # noqa: E402
from skill import SCRIPTS  # noqa: E402

ROM = ROOT / "rom" / "Battle Tycoon - Flash Hiders SFX (Japan) (Rev 1).sfc"
BUILT = ROOT / "build" / "bt_en.sfc"
QA = ROOT / "work" / "qa"
NAME = "BattleTycoon_EN"
PY = [sys.executable, "-X", "utf8"]
JP = re.compile(r"[぀-ヿ㐀-鿿ｦ-ﾟ]")


def run(*cmd):
    print("+", " ".join(map(str, cmd)), flush=True)
    if subprocess.run([*PY, *map(str, cmd)], cwd=ROOT).returncode:
        sys.exit(f"release: failed: {Path(str(cmd[0])).name}")


def hashes(data):
    return f"CRC32 {zlib.crc32(data):08X}, MD5 {hashlib.md5(data).hexdigest()}, SHA-1 {hashlib.sha1(data).hexdigest()}"


def text_dump(rom, path):
    """Every text block of the build decoded to one line per script row, cp932 for jp_left --sjis. The English glyph
    cells are left out of each table, so only glyphs still Japanese decode as Japanese. Rows in script/keep_jp.txt
    (kept on purpose, D11) are skipped. Returns the rows that still show Japanese."""
    keep = {s.split()[0] for s in (ROOT / "script" / "keep_jp.txt").read_text(encoding="utf-8").splitlines()
            if s.strip() and not s.startswith("#")}
    lines = []
    for b in sorted(tilemap.TABLES):
        base = enfont.BASE[enfont.FONT_OF[b]]
        en = range(base, base + (len(enfont.CHARS) + 1) // 2)
        table = {n: v for n, v in tilemap.load_table(b).items() if n not in en}
        lines += [f"{i} {s}" for i, _, s in tilemap.entries(b, tilemap.block_data(rom, b), table) if i not in keep]
    path.write_bytes("\n".join(lines).encode("cp932", errors="replace"))
    return [s for s in lines if JP.search(s)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--force", action="store_true", help="overwrite this version's existing release files")
    a = ap.parse_args()
    out = ROOT / "release"
    patch, zpath = out / f"{NAME}_v{a.version}.bps", out / f"{NAME}_v{a.version}.zip"
    if (patch.exists() or zpath.exists()) and not a.force:
        sys.exit(f"release: {patch.name} or {zpath.name} exists; pass --force to overwrite")

    run(ROOT / "tools" / "build.py")
    run(ROOT / "tools" / "check.py")
    run(Path(SCRIPTS) / "emu.py", BUILT, "--out", QA / "smoke", "--route", ROOT / "tools" / "routes" / "boot.txt",
        "--smoke")
    built = BUILT.read_bytes()
    work = ROOT / "work" / "release"
    work.mkdir(parents=True, exist_ok=True)
    left = text_dump(built, work / "text.txt")
    run(Path(SCRIPTS) / "jp_left.py", work / "text.txt", "--sjis", "--min", "1")
    if left:
        sys.exit("release: Japanese left in the build:\n" + "\n".join(left[:20]))
    shot = (QA / "tour" / "rom.sha1").read_text().strip() if (QA / "tour" / "rom.sha1").exists() else "none"
    if shot != hashlib.sha1(built).hexdigest():
        sys.exit(f"release: the QA tour shot build {shot}, not this one: run tools/tour.py, then the visual-QA gate")
    run(Path(SCRIPTS) / "qa_gate.py", "check", QA / "manifest.tsv", QA / "verdicts")

    final = ROOT / "build" / f"bt_en_v{a.version}.sfc"
    final.write_bytes(built)
    out.mkdir(exist_ok=True)
    run(ROOT / "tools" / "bps.py", "make", ROM, final, patch)
    check = work / "reapplied.sfc"
    run(ROOT / "tools" / "bps.py", "apply", ROM, patch, check)
    if check.read_bytes() != built:
        sys.exit("release: the re-applied patch differs from the build")
    check.unlink()
    readme = (ROOT / "docs" / "README.release.txt").read_text(encoding="utf-8")
    readme = (readme.replace("{VERSION}", a.version).replace("{BASE}", hashes(ROM.read_bytes()))
              .replace("{PATCHED}", hashes(built)))
    (out / "README.txt").write_text(readme, encoding="utf-8", newline="\r\n")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(patch, patch.name)
        z.write(out / "README.txt", "README.txt")
    print(f"release: {zpath.relative_to(ROOT)} (patch sha1 {hashlib.sha1(patch.read_bytes()).hexdigest()}); "
          f"playable image {final.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
