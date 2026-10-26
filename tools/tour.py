"""QA tour (phase 8): from each warp savestate, play a route (+ A mash) and write a contact sheet per stop.

    python -X utf8 tools/tour.py [NAME..] [--jp] [--jobs 4]
English: build/bt_en.sfc from work/states/en/ (regen.py --rom build/bt_en.sfc --tag en first) -> work/qa/tour/<name>/.
--jp: the original from work/states/ -> work/qa/tour_jp/<name>/ (the game's own behaviour, for reviewers).
Then: qa_gate.py init work/qa/manifest.tsv work/qa/tour (references/emulator-qa.md §Visual QA).
"""
import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

ORIG = ROOT / "rom" / "Battle Tycoon - Flash Hiders SFX (Japan) (Rev 1).sfc"
EN = ROOT / "build" / "bt_en.sfc"

CURSOR = "8:a,120:-," + ",".join(["8:down,90:-"] * 7)  # open the place menu, walk the cursor (descriptions)
STORY = dict(frames=9000, shot=120, mash=240)  # 2 shots per page: one with the page fully typed
# name: (warp state, frames, shot every, mash every (0 = none), route)
STOPS = {
    "intro": ("intro", 1500, 60, 0, "1500:-"),
    "title": ("title", 600, 60, 0, "600:-"),
    "modesel": ("modesel", 900, 60, 0, "60:-,8:right,120:-,8:right,120:-,8:left,120:-,8:down,120:-"),
    "option": ("option", 900, 60, 0, "60:-," + ",".join(["8:down,90:-"] * 6)),
    "vs_select": ("vs_select", 600, 60, 0, "600:-"),
    "map": ("map", 1200, 60, 0, "60:-," + ",".join(["8:right,90:-"] * 12)),
    "panel_d5_t3": ("panel_d5_t3", 300, 100, 0, "300:-"),
    "panel_d9_t2": ("panel_d9_t2", 300, 100, 0, "300:-"),
    "plate_calnarsa": ("plate_calnarsa", 300, 100, 0, "300:-"),
    "plate_harman": ("plate_harman", 300, 100, 0, "300:-"),
    **{f"{p}_cursor": (p, 1200, 45, 0, CURSOR) for p in ("file_center", "item_shop", "arena", "inn")},
    **{f"{p}_mash": (p, 2400, 60, 90, "30:-") for p in ("file_center", "item_shop", "arena", "inn", "map_menu")},
    "file_center_password": ("file_center", 1500, 30, 0,
                             "8:a,600:-,8:a,200:-,8:down,60:-,8:a,300:-,8:a,200:-"),  # 2nd A opens the menu
    "inn_status": ("inn_status", 300, 100, 0, "300:-"),
    "inn_option": ("inn_option", 900, 60, 0, "60:-," + ",".join(["8:down,90:-"] * 6)),
    "street_battle": ("street_battle", 2400, 60, 90, "30:-"),
    "venue": ("venue", 2400, 60, 90, "30:-"),
    "game_over": ("game_over", 1200, 60, 0, "1200:-"),
    "ending": ("ending", 6000, 120, 240, "30:-"),
    "credits": ("credits", 12000, 120, 0, "12000:-"),
    **{f"story_{c}_{n}": (f"story_{c}_{n}", STORY["frames"], STORY["shot"], STORY["mash"], "30:-")
       for c in ("bang", "tiria", "ottoh", "harman", "spenoza", "calnarsa", "seena", "guston", "pachet")
       for n in (1, 2, 3)},
}


def run(name, jp):
    state_scene, frames, shot, mash, route = STOPS[name]
    rom, states, out = (ORIG, "states", "tour_jp") if jp else (EN, "states/en", "tour")
    state = ROOT / "work" / states / f"{state_scene}.mss"
    out = ROOT / "work" / "qa" / out / name
    if not state.exists():
        return name, False, f"no state {state}"
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(rom), "--out", str(out),
           "--state-in", str(state), "--route-str", route.replace(":", " ").replace(",", ";"),
           "--frames", str(frames), "--shot-every", str(shot), "--timeout", "900"]
    if mash:
        cmd += ["--mash", str(mash)]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode:
        return name, False, (p.stdout.strip().splitlines() or [""])[-1]
    return name, *sheets(out)


def sheets(out):
    """Full-size sheets of the frames that changed (text readable without opening frames): out/sheet*.png."""
    for old in out.glob("sheet*.png"):
        old.unlink()
    p = subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "sheet.py"), str(out),
                        "--changed", "0.01", "--div", "1", "--max", "12", "--out", str(out / "sheet.png")],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode == 0, (p.stdout.strip().splitlines() or [""])[-1][:100]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*")
    ap.add_argument("--jp", action="store_true")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--sheets-only", action="store_true", help="remake the sheets from the frames already shot")
    a = ap.parse_args()
    names = a.names or list(STOPS)
    unknown = [n for n in names if n not in STOPS]
    if unknown:
        sys.exit(f"unknown stop(s): {unknown}")
    bad = []
    with ThreadPoolExecutor(a.jobs) as ex:
        job = (lambda n: (n, *sheets(ROOT / "work" / "qa" / ("tour_jp" if a.jp else "tour") / n))) \
            if a.sheets_only else (lambda n: run(n, a.jp))
        for name, ok, last in ex.map(job, names):
            print(f"{'ok  ' if ok else 'FAIL'} {name:22} {last}", flush=True)
            if not ok:
                bad.append(name)
    print(f"{len(names) - len(bad)}/{len(names)} stops toured")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
