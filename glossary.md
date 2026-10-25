# Glossary - Battle Tycoon: Flash Hiders SFX

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` enforces the Characters, Places and Terms tables (JP present -> EN present, Avoid absent)
and the honorific forms below. The "Guidance" table is not enforced.

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated, after a name: さん -san, 様 -sama, 君 -kun, ちゃん -chan (Tiria-san,
  Spenoza-sama, Tiria-kun, Tiria-chan). Name order: Western (given name first).
- Romanisation source: official English names where they exist, else an earlier fan patch, else Hepburn without
  macrons (none exists for this game, so minor names are Hepburn).
- Credits: English.
- Register / flavour: light comedy, keep light JP flavour (honorifics, Onee-sama). No translator notes.
- Abbreviations: full names and terms everywhere; never abbreviate to fit (D4). Report `LONG:` instead.

## Style rules
- Punctuation: 「」 dialogue -> `Name: text` (story pages, no quotes around the speech); 『』 -> "...";
  … / ・・・ -> `...`; ！？ -> `?!`; ！！ -> `!!` (keep the game's doubled marks); 〜 (drawl) -> a stretched vowel or
  `~`; （心の声） -> (aside) in parentheses. Plain ASCII only, plus the icons ♥ <sweat> <anger> where the
  Japanese line has them.
- Long silences (オットー「……………………」): `...` (keep the gag length only where the scene plays on it, A0-11).
- Voices: docs/style-reference.md.

## Characters
Official spellings from the game's own English graphics (res 0x00/0x0A: VS select and battle name tags).
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| バング | Bang | | hero; brash, calls himself 俺様; Jail Lance's son | Banga, Bung |
| ティリア | Tiria | | Bang's minder from his village, sharp-tongued | Tilia, Tiriya |
| オットー | Ottoh | | official spelling with -h; never speaks; last year's champion; Central Government Royal Guard | Otto |
| ハーマン | Harman | | woman; Royal Guard, Spenoza's bodyguard, adores him | Herman |
| スピノザ | Spenoza | | official spelling; Chairman of the Central Government; polite | Spinoza |
| サンダーヘッド | Thunderhead | | Spenoza's surname (Tiria garbles it as ボンバーヘッド Bomberhead) | |
| カルナーサ | Calnarsa | | brash woman, says あたい | Karnasa |
| シーナ | Seena | | polite girl (ですわ), Dairufa's servant, Spenoza's new secretary | Sheena, Shina |
| ガストン | Guston | | official spelling; old war-veteran heavy body, says わし / じゃ | Gaston |
| パチェット | Pachet | | woman, flirts with anyone pretty (ボウヤ, マイハニー); her speech turns rough and blunt at the end of A5 | Patchet |
| ジェイルランス | Jail Lance | | tag reads J.LANCE / JAIL LANCE; Bang's father | Jaillance |
| リラ | Rira | | Calnarsa's sidekick (Hepburn) | Lila, Lira |
| レイ | Rei | | Calnarsa's sidekick (Hepburn) | Ray |
| ダイルファー | Dairufa | | Seena's old master, in debt (Hepburn) | Dilfer |
| エルエー | L.A. | | the referee (credits: レフェリー エルエー), a little boy (Flash Hiders cast: エルエー（少年）) | Erue |
| 村人 | Villager | | speaker label | |
| 商人たち | Shopkeepers | | speaker label (9D) | |
| レポーター | Reporter | | speaker label | |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 中央政府 | Central Government | | 中央政府都市 = Central Government City | |
| ファイル管理センター | File Center | | センター alone = the Center; "File Management Center" (22) overflows the 20-letter list line A8-01 | |
| アイテムショップ | Item Shop | | ショップ alone = the shop | |
| 闇闘技場 | Underground Arena | | betting on fights | |
| 中央ゲート | Central Gate | | | |
| 選手宿舎 | Fighters' Lodge | | 宿舎 alone = the Lodge | |
| メインマップ | Main Map | | | |

## Terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| バトルタイクーン | Battle Tycoon | | the tournament (no "the" in the official logo; "the Battle Tycoon" reads fine in prose) | |
| 主席 | Chairman | | Spenoza's title; A1-0A/0C pun 主席 shuseki / 歯石 shiseki (tartar): adapt the pun | President |
| 親衛隊 | Royal Guard | | Ottoh and Harman | |
| ボランゾ | Boranzo | | Guston's kind of body ("a classic-build Boranzo") | |
| パスワード | password | | | |

## Guidance (not enforced)
| JP | EN | notes |
|---|---|---|
| 本戦 / 予戦 | finals / prelims (preliminaries) | |
| 優勝 / 優勝者 | win (the tournament) / champion | |
| 賞金 / 優勝賞金 | prize money / the winner's prize | |
| 護衛 | bodyguard | |
| 秘書 | secretary | |
| 旧大戦 / 大戦 | the Great War | Guston fought in it |
| 村 / 商店街 | the village / the shopkeepers (the market street) | Bang's home |
| オヤジ | (Bang -> his father) Pops; (others) the old man / old geezer | |
| オジさん | (Tiria -> Jail Lance) Mister | |
| おねえさま | (Rira, Rei -> Calnarsa) Onee-sama | |
| ご主人様 | master | |
| ファイル | file | save file slot |
| ランク | rank | |
| ステータス / オプション | Status / Options | menu items |
| バーサス | Versus (mode) | |
| ビジュアル | Visual | story scenes |

## Items
One English name per item (92 / A8 / B0 share them; `tools/batches.py` merges b002 into every copy), <= 16 letters,
Title Case, US spelling (Armor). Families: <X>ストーン/ストック/ジェム/オーブ = <X> Stone/Stock/Gem/Orb;
<X>リング/ピアス/ブレス = <X> Ring/Earring/Bracelet; イフレイス = Ifreis, ボルビック = Volvic, ウインディ = Windy.
Swords keep their names (Kotetsu, Masamune, Muramasa, Kusanagi, Excalibur). Full list: `script/92.tsv`, `A8.tsv`.

## Decisions from earlier batches
- b001 会場 -> Venue (A8-0C Battle Tycoon Venue); ビジュアルあ/い/う -> Visual 1/2/3; A8-10 (を after the item
  name) left blank, A8-11 "obtained!".
- b002 バンパイドドレス -> Vampire Dress (unclear word; reads as English), マジカルバッシュ -> Magical Kicks
  (バッシュ = basketball shoes).
- b007 主席/歯石 pun moved onto Spenoza's name: Bang "Chairman Spinach... the green stuff that gets stuck in your
  teeth", Tiria "That's spinach! It's Spenoza!". A1-49 おしたおし slip = "pin you down... I mean, take you down".
- b005 9F-09: Ottoh's one near-word "Wha..." (Harman finishes it) is intended.
- Credits (AF, by hand, `work/tl/AF.out.tsv` -> `batches.py credits`): staff readings from MobyGames (SNES and
  PC Engine Flash Hiders credits); エイジャの赤石 (Tatsuya Akaishi's pen name, a JoJo reference) = "Red Stone of Aja";
  ただのＫ = "Just K". Unconfirmed common readings: 前田直顕 Naoaki Maeda, 青柳久 Hisashi Aoyagi, 関洋一 Yoichi
  Seki, 藤井恵 Megumi Fujii.
