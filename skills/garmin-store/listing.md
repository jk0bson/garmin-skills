# The upload form

| Item | Limit | Note |
|---|---|---|
| Title | 50 characters, one per language | put search words in it |
| Description | 4000 characters, one per language | no `<` or `>` |
| What's New | one per language | do not just repeat "Version x.y.z" |
| Cover | 500×500, under 300 KB | |
| Hero | 1440×720, under 2 MB | **the only image that is per language**: add it in each language tab |
| Cover, screenshots | cover under 300 KB; 5 screenshots maximum, under 150 KB each | **shared by all languages**: they sit outside the language tabs, so the form has one set for the whole listing (verified in the live form on 2026-11-27: after uploading, the same 5 screenshots show in every language tab while each tab keeps its own hero); an animated GIF counts as one of the 5 |
| Version | must be higher than every earlier upload | the portal shows `1.2.0` as "1.2" |

## Description structure that works

1. One or two sentences: what it does and for whom.
2. WHY / FEATURES: short lines, each a benefit.
3. SETUP or CONTROLS: how to install the data field or which button does what. Write menu paths as sentences ("open Run settings, then Data Screens"), not with `>`.
4. QUICK FAQ: free? needs the phone? permissions? how to report a bug (model + what you saw, contact e-mail).
5. SUPPORT: a tip link, if any. With a tip link, select "Ask for Tips" in the Monetization section.

## After Submit

- "Version update pending" for up to about 2 hours before changes show.
- New apps were taking up to 2 weeks of review in October 2026, after a wave of mass-produced watch faces. Plan launches two weeks ahead.

## Categories

Select every activity the app really works in, including its subtypes (a running data field: treadmill, street, trail, track, indoor, virtual, obstacle, ultra). Do not select sports where its units or labels make no sense.

## Refused or unlisted

From developer forum reports, not an official list.

Copies of Garmin's own watch faces, the Garmin logo or brand, licensed characters without rights, safety apps (incident detection, radar), extreme sports (diving, skydiving, base jumping), medical claims without a "not medical advice" notice.

## Check before uploading

`scripts/check_listing.py STORE_FOLDER` reads `store.json`, `description_<lang>.txt`, `whats_new.txt` and `images/`, and exits with 1 when something would be refused: a title over 50 characters, a description over 4000 or containing `<` or `>`, a cover that is not 500×500 under 300 KB, a hero that is not 1440×720 under 2 MB in each language, more than 5 screenshots or one over 150 KB. A screenshot that is not 900×900 (450×450 for a GIF) is a note, not an error. Tested on a real listing (clean) and on a copy with a 51-character title, a `>`, a wrong cover and a missing hero (4 errors).

## Language codes

The form's language list uses two-letter codes (`en`, `de`, `fr`, `es`, `it`, `nl`, `pl`, `pt_BR`, `ja`...; 28 in all, read from the live form): use the same codes in `store.json` and in file names. The three-letter codes (`eng`, `deu`, `fre`, `spa`, `ita`, `dut`, `pol`) belong to `<iq:language>` in `manifest.xml`, not to the store. `check_listing.py` rejects a code the form does not offer. In the form, "Add" next to the language list creates a tab; only one tab's fields are in the page at a time (`app-title-<lang>`, `app-desc-<lang>`, `app-whats-new-<lang>`).

## One title per language

Each language tab has its own title, limited to 50 characters. Write the search words people use in that language (running / course à pied / Laufen) instead of translating the English title word for word, and keep the name first so the app stays recognizable. Reported by developers, not verified here: the store search favors the title of the language the user browses in.
