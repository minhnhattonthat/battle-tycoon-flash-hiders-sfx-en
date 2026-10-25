"""Warp to every scene in tools/debug/scenes.txt from a cold boot: proof shot + savestate per scene.

    python -X utf8 tools/debug/regen.py [NAME..] [--rom build/bt_en.sfc] [--jobs 4] [--sheet]
Writes work/qa/warp/<name>/arrived.png and work/states/<name>.mss; exits 1 if any scene did not log WARP OK.
Run it again after any code, font or graphics change (savestates keep the old VRAM and code).
"""
import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

ORIG = ROOT / "rom" / "Battle Tycoon - Flash Hiders SFX (Japan) (Rev 1).sfc"


def scene_names():
    names = []
    for line in (ROOT / "tools" / "debug" / "scenes.txt").read_text(encoding="utf-8").splitlines():
        words = line.split("#")[0].split()
        if words:
            names.append(words[0])
    return names


def run(name, rom, sheet):
    out = ROOT / "work" / "qa" / "warp" / name
    state = ROOT / "work" / "states" / f"{name}.mss"
    state.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(rom), "--out", str(out),
           "--script", str(ROOT / "tools" / "debug" / "warp.lua"), "--var", f"SCENE='{name}'",
           "--var", "WARP_EXIT=true", "--var", f"WARP_STATE=[[{state.as_posix()}]]",
           "--frames", "20000", "--shot-every", "600", "--timeout", "900"]
    if sheet:
        cmd.append("--sheet")
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = (out / "log.txt").read_text(encoding="utf-8", errors="replace") if (out / "log.txt").exists() else ""
    ok = f"WARP OK {name} " in log and (out / "arrived.png").exists()
    return name, ok, p.returncode, log.strip().splitlines()[-1:] or p.stdout.strip().splitlines()[-1:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--rom", default=str(ORIG))
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--sheet", action="store_true")
    args = ap.parse_args()
    all_names = scene_names()
    names = args.names or all_names
    unknown = [n for n in names if n not in all_names]
    if unknown:
        sys.exit(f"unknown scene(s): {unknown}")
    bad = []
    with ThreadPoolExecutor(args.jobs) as ex:
        for name, ok, code, last in ex.map(lambda n: run(n, args.rom, args.sheet), names):
            print(f"{'ok  ' if ok else 'FAIL'} {name:20} exit {code}  {last[0] if last else ''}", flush=True)
            if not ok:
                bad.append(name)
    print(f"{len(names) - len(bad)}/{len(names)} scenes reached")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
