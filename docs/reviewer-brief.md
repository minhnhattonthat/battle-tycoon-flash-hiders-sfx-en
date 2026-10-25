# Translation reviewer brief - Battle Tycoon: Flash Hiders SFX

You review one batch of a JP->English fan translation. Read-only: no edits, no git, no subagents.
Mechanical validity (ids, encodable characters, width, glossary spellings, honorific forms) is already enforced by
`tools/batches.py check` - judge translation quality. Return the report as your final message: subagents cannot
write files, so the controller saves it.

## Inputs (paths in your dispatch)
- Pairs file `work/tl/<batch>.pairs.txt`: every entry as `>> id | form limit | JP` / `   EN`, in game order.
  Read ALL of it. Story (`dlg`) entries are whole pages of a scene (ids 00 / 40 / 80 = scenes 1 / 2 / 3); a page
  without a speaker continues the previous speech. Menu (`menu`) entries are single lines of a 1-4 line message
  box, so a sentence may run across consecutive entries and a line may be empty on purpose.
- `glossary.md` (rulings at the top), `docs/style-reference.md` (voices), `docs/synopsis.md` (who is who), the
  translator's report (unverified claims).

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say
  what it means.
- Consistency: glossary names/terms exactly (a one-letter slip like "Bran" for "Plan" is what players notice);
  honorifics kept after names (Tiria-san, Spenoza-sama); voice matches the style reference.
- Things players caught that reviewers missed: jokes/wordplay losing their punch (this game: 最強/最狂 9D,
  主席/歯石 A1, おしたおし A1-49, Bomberhead/Thunderhead A1); abbreviated names or terms; stock phrases that read
  awkwardly in English ("... GET!"); item names that don't read as English (bad loanword guesses).
- Naturalness: would a fan-translation reader stumble? Register per speaker as in the style reference.

## Report
### Issues
#### Critical (meaning reversed, wrong speaker)
#### Important (clear mistranslation, glossary inconsistency, abbreviation, a joke that no longer works)
#### Minor (style - these are deferred to one polish pass)
Each: `id - JP gist - problem - suggested EN`.
### Assessment
Approved | Needs fixes - one sentence why.
