# Translator brief - Battle Tycoon: Flash Hiders SFX (SNES, 1995)

You translate part of the Japanese script of Battle Tycoon: Flash Hiders SFX into English for a fan patch. A light
comedy fighting game: nine fighters enter the yearly Battle Tycoon tournament; short bickering story scenes, menus
for registration, shop, inn and a betting arena.
Work only on the batches named in your dispatch, one at a time in the order given, each to a passing check before
the next. Do all translation yourself; do not dispatch subagents. Run commands from the repo root.

## Read first
1. `docs/style-reference.md` - voices per speaker and approved example pairs. Match this voice.
2. `work/tl/<batch>.terms.txt` - binding glossary rows for this batch; `glossary.md` has the rulings at the top
   (honorifics, punctuation) and the full tables.
3. `docs/synopsis.md` - who is who and each fighter's three scenes.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese`, in game order (use neighbours for context).
- `dlg` (story, batches b003-b011): one entry = one page of a story scene, `Speaker「...」`; a page without a
  speaker continues the previous page's speech. Limit `5x30`: the tool word-wraps your text at 30 letters per line
  and it must fit in 5 lines. Lines starting 00 / 40 / 80 in the id are scenes 1 / 2 / 3.
- `menu` / `choice` (b001): one entry = one line of a message box (`menu`, limit 20 letters, fewer when the line
  ends in a control) or one popup menu item (`choice`, 18). The game shows a message as 1-4 consecutive lines
  (usually 2: `47-09` + `47-0A`...): translate the message as a whole, split across the same lines, each within
  its limit. A line may be left empty (`id<TAB>` with nothing after) if the message fits in fewer lines. Special
  lines: `47-0D` follows a fighter name the game draws at the left (`Bang` + your text: "-san, then?" style, 10
  letters); `A8-10` follows an item name the game draws at the left (4 letters; may be empty) and `A8-11` is the
  next line ("...obtained!"); `A8-15` is the text before a YES/NO on the same line (8 letters).
- `name` / `item` (b002): fighter names (14 letters, use the glossary) and equipment names (16 letters). Each
  appears once even if the game stores it in several lists. Weapons per fighter type (knuckles, rods, claws,
  gloves, batons, arms, motors, katana), armour, accessories (stones, rings, orbs), shoes. Keep the katakana
  loanword's English (ライトナックル = Light Knuckle); Japanese sword names stay as names (コテツ = Kotetsu,
  マサムネ = Masamune). Name families keep one pattern (タイガーストーン / ストック / ジェム / オーブ = Tiger Stone /
  Tiger Stock / Tiger Gem / Tiger Orb). Title Case.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Plain ASCII: straight quotes, `...`, `--`; no tabs inside
the English, no Japanese or fullwidth characters, no `\uXXXX`, no controls (`{wait}` etc. are added by the tool).
Icons ♥ `<sweat>` `<anger>` may stay where the Japanese line has them (each takes 2 letters of width). In `dlg`,
`\n` forces a line break (rarely needed).

## Validate
`python -X utf8 tools/batches.py check <batch>` - fix every reported id until it prints `<batch>: OK`. It checks
ids, ASCII, width (exactly as the game draws it), glossary names and honorific forms.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese doesn't
  state; don't summarise or skip. Adapt wordplay so the joke still lands (no translator notes). Puns to watch:
  最強/最狂 (9D, see the style reference), 主席/歯石 (A1-0A/0C: Bang mistakes "Chairman" for something stuck to
  your teeth; find an English near-homophone gag), おしたおし/たおし (A1-49: "push him down... I mean, take him
  down"), スピノザボンバーヘッド / サンダーヘッド (A1-8A/8D: Bomberhead / Thunderhead).
- Entries that appear in the style reference's approved pairs: use that English verbatim.
- Story format: `Name: text` (no quotes around speech). Continuation pages have no name. Censored ♥♥♥♥ (9E-42)
  stays ♥♥♥♥.
- Names and terms exactly as in the glossary. Never abbreviate to fit; if a line can't fit without losing meaning,
  keep the meaning, shorten the phrasing, and if it still fails report `LONG: id`.
- Honorifics kept after names (Tiria-san, Spenoza-sama, Tiria-kun, Tiria-chan); Western name order.
  おねえさま (Rira/Rei to Calnarsa) = "Onee-sama". Punctuation map in `glossary.md` Style rules.
- Menus: short, natural UI English ("Save", "View Password", "Leave the Center"). YES/NO lines are not in the
  batch; a question before them should end in "?".
- Long silences: Ottoh's 「……………………」 = `Ottoh: ...`. A0-11/16 is a two-page gag of endless dots: fill
  both pages with dots (break them with spaces or `\n`; a word may not exceed 30 letters).

## Consistency
Never edit `glossary.md`. For a recurring name or term not in it, pick a form, use it consistently, and report it.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
