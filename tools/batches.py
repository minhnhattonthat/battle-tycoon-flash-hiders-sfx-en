"""batches.py: translator batches from script/*.tsv, their check, merge back and reviewer pairs.

    python -X utf8 tools/batches.py split            work/tl/bNNN.tsv + bNNN.terms.txt (untranslated entries only)
    python -X utf8 tools/batches.py check b003       validate work/tl/b003.out.tsv; prints OK or one line per error
    python -X utf8 tools/batches.py merge b001 b003  check, then write the English into script/*.tsv
    python -X utf8 tools/batches.py pairs b003       work/tl/b003.pairs.txt for the reviewer
    python -X utf8 tools/batches.py credits          work/tl/AF.out.tsv (hand-made) -> script/AF.tsv, centred

Batches: b001 menus (47 90 91 92 A8), b002 names + items (one entry per distinct Japanese name, merged into every
copy), then one per story block 9D-A5. Credits (AF) are laid out by hand. Entries hide the layout: menu text without
its margin, cursor cells, controls or YES/NO (merge puts them back); a story entry is a whole page (insert.py wraps).
Input `id<TAB>speaker<TAB>form<TAB>limit<TAB>jp`; output `id<TAB>en`.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import enfont  # noqa: E402
import insert  # noqa: E402
import lint  # noqa: E402
import tilemap  # noqa: E402
from extract import HEADER, read_tsv  # noqa: E402

TL = ROOT / "work" / "tl"
MENU_BLOCKS = (0x47, 0x90, 0x91, 0x92, 0xA8)
FIELD_BLOCKS = (0x47, 0x90, 0x91, 0x92, 0xA8, 0xB0)
HONORIFICS = {"さん": "-san", "様": "-sama", "君": "-kun", "ちゃん": "-chan"}
ENFORCED = ("Characters", "Places", "Terms")
JP_TEXT = re.compile(r"[぀-ヿ一-鿿！-～]")


def script():
    return {b: read_tsv(ROOT / "script" / f"{b:02X}.tsv") for b in sorted(tilemap.TABLES)}


def ctrls(s):
    return [m[0] for m in tilemap.TOKEN.finditer(s) if m[0] in tilemap.CTRL_ENC]


def menu_layout(jp):
    """Menu row -> (lead, body, tail, limit): the English replaces `body`; merge writes lead + English + tail.
    A YES/NO tail keeps its column, so the English is padded with spaces to `limit`."""
    lead, rest = insert.lead_tokens(jp)
    slots = len(lead) - 3 * lead.count("<▲▼>")
    if "ＹＥＳ" in rest:
        body = rest[:rest.index("ＹＥＳ")].rstrip(tilemap.BLANK)
        return lead, body, "ＹＥＳ／ＮＯ", 2 * rest.index("ＹＥＳ")
    tail = "".join(ctrls(rest))
    body = tilemap.TOKEN.sub(lambda m: "" if m[0] in tilemap.CTRL_ENC else m[0], rest)
    return lead, body, tail, lint.MENU_END - 2 * slots - 2 * len(ctrls(rest))


def entries(rows, todo=True):
    """Batch entries {batch: [(id, speaker, form, limit, jp)]} (with `todo`, only those still lacking English),
    plus the row targets {id: [(block, row id)]} each entry's English goes to."""
    if not todo:
        rows = {b: [(i, k, jp, "") for i, k, jp, en in r] for b, r in rows.items()}
    out, targets = {}, {}
    menu = []
    for b in MENU_BLOCKS:
        for id_, kind, jp, en in rows[b]:
            if kind != "menu" or en:
                continue
            lead, body, tail, limit = menu_layout(jp)
            if not JP_TEXT.search(body):
                continue
            form = "choice" if lead.strip(tilemap.BLANK) else "menu"
            menu.append((id_, "", form, str(limit), body))
            targets[id_] = [(b, id_)]
    out["b001"] = menu
    seen, fields = {}, []
    for b in FIELD_BLOCKS:
        for id_, kind, jp, en in rows[b]:
            if kind not in ("name", "item"):
                continue
            key = (kind, jp.lstrip(tilemap.BLANK))
            if key not in seen:
                seen[key] = id_
                fields.append([id_, "", kind, "14" if kind == "name" else "16", key[1], bool(en)])
                targets[id_] = []
            targets[seen[key]].append((b, id_))
            if not en:
                fields[[f[0] for f in fields].index(seen[key])][5] = False
    out["b002"] = [tuple(f[:5]) for f in fields if not f[5]]
    for n, b in enumerate(tilemap.STORY):
        batch = []
        for prow, ctrl in insert.pages(rows[b]):
            if prow[0][3]:
                continue
            jp = "".join(tilemap.TOKEN.sub(lambda m: "" if m[0] in tilemap.CTRL_ENC else m[0], r[2])[1:]
                         for r in prow)
            speaker = jp.split("「")[0] if "「" in jp[:12] else ""
            batch.append((prow[0][0], speaker, "dlg", f"{insert.PAGE_LINES}x{insert.STORY_COLS}", jp))
            targets[prow[0][0]] = [(b, prow[0][0])]
        out[f"b{n + 3:03d}"] = batch
    return out, targets


def glossary():
    """[(jp, en, [avoid])] from the enforced tables of glossary.md."""
    out, section = [], None
    for line in (ROOT / "glossary.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
        elif section in ENFORCED and line.startswith("| ") and not line.startswith("| JP"):
            f = [c.strip() for c in line.strip("|").split("|")]
            out.append((f[0], f[1], [a.strip() for a in f[4].split(",") if a.strip()]))
    return out


def has_term(jp, term):
    """`term` in `jp` as a whole katakana run (レイ is not in フレイム); kanji terms match anywhere."""
    return re.search(rf"(?<![ァ-ヺー]){re.escape(term)}(?![ァ-ヺー])", jp) is not None


def read_batch(name):
    lines = (TL / f"{name}.tsv").read_text(encoding="utf-8").splitlines()
    return [tuple(line.split("\t")) for line in lines if line and not line.startswith("id\t")]


def read_out(name):
    """[(id, en)]; tolerates a header line and a trailing tab."""
    out = []
    for line in (TL / f"{name}.out.tsv").read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("id\t"):
            continue
        id_, _, en = line.partition("\t")
        out.append((id_.strip(), en.rstrip("\t").strip(" ")))
    return out


def row_of(rows, block, id_):
    return next(r for r in rows[block] if r[0] == id_)


def assemble(rows, block, id_, form, en):
    """English entry -> the `en` cell of one script row."""
    jp = row_of(rows, block, id_)[2]
    if form in ("menu", "choice"):
        lead, body, tail, limit = menu_layout(jp)
        if tail.startswith("ＹＥＳ"):
            en = en.ljust(limit)
        return lead + en + tail
    if form == "name":
        return tilemap.BLANK + en
    return en


def check(name, rows=None):
    rows = rows or script()
    entries_in = read_batch(name)
    try:
        got = read_out(name)
    except FileNotFoundError:
        return [f"{name}.out.tsv missing"]
    errs = []
    ids = [e[0] for e in entries_in]
    gids = [g[0] for g in got]
    for i in sorted(set(gids) - set(ids)):
        errs.append(f"{i}: not in the batch")
    for i in ids:
        if gids.count(i) != 1:
            errs.append(f"{i}: {gids.count(i)} times in the output (want 1)")
    en_of = dict(got)
    _, targets = entries(rows, todo=False)
    gloss = glossary()
    for k, (id_, speaker, form, limit, jp) in enumerate(entries_in):
        en = en_of.get(id_)
        if en is None:
            continue
        if not en and form not in ("menu", "choice"):
            errs.append(f"{id_}: empty")
            continue
        icons = [m[0] for m in insert.ICON.finditer(en)]
        bad = [c for c in insert.ICON.sub("", en) if not " " <= c <= "~"]
        if bad:
            errs.append(f"{id_}: not plain ASCII: {''.join(bad)!r}")
        if any(i not in jp for i in icons) or "{" in insert.ICON.sub("", en):
            errs.append(f"{id_}: controls/icons not allowed here (only icons the Japanese has): {en!r}")
        if "\\n" in en and form != "dlg":
            errs.append(f"{id_}: \\n only in story pages")
        block, rid = targets[id_][0]
        cell = assemble(rows, block, rid, form, en)
        if form == "dlg":
            c = next(c for p, c in insert.pages(rows[block]) if p[0][0] == rid)
            try:
                lines = insert.wrap_page(en, c)
                if len(lines) > insert.PAGE_LINES:
                    errs.append(f"{id_}: wraps to {len(lines)} lines > {insert.PAGE_LINES} (30 letters each)")
            except ValueError as e:
                errs.append(f"{id_}: {e}")
        else:
            if form in ("menu", "choice") and menu_layout(row_of(rows, block, rid)[2])[2].startswith("ＹＥＳ") \
                    and len(en) > int(limit):
                errs.append(f"{id_}: {len(en)} letters > {limit} (text before YES/NO)")
            enc = tilemap.encoder(tilemap.load_table(block), enfont.FONT_OF[block])
            try:
                top, bot = enc(cell)
                end = lint.end_of(block, rid, form if form in ("name", "item") else "menu")
                if lint.used_cols(top, bot) > end:
                    errs.append(f"{id_}: {len(en)} letters > {limit}: {en!r}")
            except ValueError as e:
                errs.append(f"{id_}: {e}")
        # glossary: menus may move a term to the next/previous line of the message
        ctx = en if form != "menu" and form != "choice" else " ".join(
            en_of.get(e[0], "") for e in entries_in[max(k - 1, 0):k + 2])
        for gjp, gen, avoid in gloss:
            if has_term(jp, gjp) and gen.lower() not in ctx.lower():
                errs.append(f"{id_}: glossary {gjp} -> {gen!r} missing")
            for a in avoid:
                if re.search(rf"\b{re.escape(a)}\b", en):
                    errs.append(f"{id_}: avoid spelling {a!r} (glossary: {gen})")
            for h, hen in HONORIFICS.items():
                if gjp + h in jp and gen + hen not in ctx:
                    errs.append(f"{id_}: {gjp}{h} -> {gen + hen!r} missing")
    return errs


def merge(names):
    rows = script()
    _, targets = entries(rows, todo=False)
    for name in names:
        errs = check(name, rows)
        if errs:
            sys.exit(f"{name}: {len(errs)} errors, not merged (run check)")
    for name in names:
        form_of = {e[0]: e[2] for e in read_batch(name)}
        for id_, en in read_out(name):
            for block, rid in targets[id_]:
                cell = assemble(rows, block, rid, form_of[id_], en)
                rows[block] = [(i, k, jp, cell if i == rid else e) for i, k, jp, e in rows[block]]
    for b, r in rows.items():
        (ROOT / "script" / f"{b:02X}.tsv").write_text(
            "\n".join([HEADER] + ["\t".join(x) for x in r]) + "\n", encoding="utf-8", newline="\n")
    print(f"merged {' '.join(names)}")


def center(en, par):
    """Credits line centred in the 32 tile columns (odd-column rows: 30, one column in): blank slots + a space."""
    if not en:
        return ""  # no lead either: a padding space is a glyph and would overwrite the .0 row's letters
    width = 30 if par else 32
    lead =max(width - len(en), 0) // 2
    return tilemap.BLANK * (lead // 2) + " " * (lead % 2) + en


def credits():
    """work/tl/AF.out.tsv (`id<TAB>English`, by hand) -> script/AF.tsv, each line centred; an empty English blanks
    the row (the staff roll puts surname and given name in two rows; the English full name takes one)."""
    path = ROOT / "script" / "AF.tsv"
    en_of = {i.strip(): en for i, _, en in (line.partition("\t") for line in
                                            (TL / "AF.out.tsv").read_text(encoding="utf-8").splitlines())
             if i.strip()}
    rows = read_tsv(path)
    unknown = set(en_of) - {r[0] for r in rows if r[1] == "credit"}
    if unknown:
        sys.exit(f"not credit rows: {sorted(unknown)}")
    rows = [(i, k, jp, (center(en_of[i].strip(), i.endswith(".1")) or tilemap.BLANK) if i in en_of else en)
            for i, k, jp, en in rows]
    path.write_text("\n".join([HEADER] + ["\t".join(x) for x in rows]) + "\n", encoding="utf-8", newline="\n")
    print(f"credits: {len(en_of)} rows")


def split():
    TL.mkdir(parents=True, exist_ok=True)
    if any(TL.glob("b*.tsv")):
        sys.exit(f"{TL} already has batch files: refusing to overwrite (move them away first)")
    out, _ = entries(script())
    gloss = glossary()
    for name, batch in out.items():
        if not batch:
            continue
        (TL / f"{name}.tsv").write_text(
            "id\tspeaker\tform\tlimit\tjp\n" + "".join("\t".join(e) + "\n" for e in batch),
            encoding="utf-8", newline="\n")
        text = "".join(e[4] for e in batch)
        terms = [f"{j}\t{e}" for j, e, _ in gloss if has_term(text, j)]
        (TL / f"{name}.terms.txt").write_text("\n".join(terms) + "\n", encoding="utf-8", newline="\n")
        print(f"{name}: {len(batch)} entries, {len(text)} JP chars, {len(terms)} terms")


def pairs(name):
    en_of = dict(read_out(name))
    lines = [f">> {i} | {f} {lim} | {s + ': ' if s else ''}{jp}\n   {en_of.get(i, '')}" for i, s, f, lim, jp in
             read_batch(name)]
    path = TL / f"{name}.pairs.txt"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(path.relative_to(ROOT))


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd, names = argv[0], argv[1:]
    if cmd == "split":
        split()
    elif cmd == "check":
        bad = 0
        for name in names:
            errs = check(name)
            for e in errs:
                print(f"{name} {e}")
            print(f"{name}: OK" if not errs else f"{name}: {len(errs)} errors")
            bad |= bool(errs)
        return int(bad)
    elif cmd == "merge":
        merge(names)
    elif cmd == "credits":
        credits()
    elif cmd == "pairs":
        for name in names:
            pairs(name)
    else:
        sys.exit(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
