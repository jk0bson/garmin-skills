# Garmin skills

[![tests](https://github.com/jk0bson/garmin-skills/actions/workflows/test.yml/badge.svg)](https://github.com/jk0bson/garmin-skills/actions/workflows/test.yml)

Agent skills for building Garmin **Connect IQ** apps, watch faces and data fields in Monkey C, and for getting them onto the Connect IQ Store.

Everything here comes from shipping real apps — a running data field, two watch faces, sport scorekeepers, a sauna timer — on 66 round watches from the 218 px Forerunner 255S to the 466 px fēnix 9 Pro. Each rule exists because a bug, a rejected upload or a bad screenshot taught it. What was not verified on a watch says so.

## Skills

- [**garmin-app**](skills/garmin-app/SKILL.md): Writes and reviews Monkey C that survives real watches: **touch vs button input**, **optional `Activity.Info` fields**, **data field layouts**, **sensor edge cases**, **settings**, **memory limits** and **unit tests that compile**.
- [**garmin-design**](skills/garmin-design/SKILL.md): Makes one design read well on **nine screen sizes**, with **AMOLED and 64-color MIP palettes**, **bitmap fonts**, **labels that fit in every language**, smooth **arcs** and **icons**.
- [**garmin-simulator**](skills/garmin-simulator/SKILL.md): Drives the Connect IQ simulator on macOS: **menus and buttons**, **data field layouts**, **heart-rate zones**, **FIT playback of a realistic run**, **multi-device audits** and **store captures**.
- [**garmin-store**](skills/garmin-store/SKILL.md): Prepares a listing that passes the upload form first time: **limits**, **descriptions**, **composed 900×900 images**, **GIF first**, **categories**, **free vs paid** and **reviews**.

## Scripts

- [`bitmap_fonts.py`](skills/garmin-design/scripts/bitmap_fonts.py): BMFont fonts for every round screen size in your manifest, antialiased on the watch, line height trimmed for true vertical centering. `--strings` lists the characters your translations use that a font lacks. Works on macOS, Windows and Linux.
- [`demo_run.py`](skills/garmin-simulator/scripts/demo_run.py): a believable run or ride (`--sport cycling`, with power from drag, rolling and slope) as a FIT file to replay in the simulator, anywhere on Earth (`--lat`, `--lon`). No dependencies.
- [`check_listing.py`](skills/garmin-store/scripts/check_listing.py): checks a store listing folder (title and description limits, `<` and `>`, image sizes and weights) before you upload it.

## Built with garmin-skills

Apps shipped with these skills, on the Connect IQ Store:

- [zonely: Run in the right zone](https://apps.garmin.com/apps/5f3035d0-fa84-465e-8905-552bcd735f19): running heart-rate zone data field
- [aestify: Minimal LCD Watch Face](https://apps.garmin.com/apps/6f94f08c-1e6c-4923-918a-4c0c9a86e77a): minimalist LCD watch face
- [ephemera: a poster for your wrist](https://apps.garmin.com/apps/5bd87ac8-4587-44f1-8326-af47c168b60b): poster-style watch face
- [sauna sauna sauna! premium: Sauna Sessions](https://apps.garmin.com/apps/ba6679b6-df26-4762-8364-df93915e1f6b): sauna session tracker (paid)
- [sauna sauna sauna! free: Sauna Session Timer](https://apps.garmin.com/apps/067014a3-41eb-4d6a-aff4-5d95e19760d2): sauna session timer
- [Racket Score: 6 Racket Sports](https://apps.garmin.com/apps/510d5ae7-8075-4ad6-b775-c83ee8138f4e): scorekeeper for 6 racket sports
- [goal goal goal!: Football & Futsal Score](https://apps.garmin.com/apps/93395c58-a751-4864-b716-0c28984afb2e): football and futsal scorekeeper
- [next next next!: Routines, step by step](https://apps.garmin.com/apps/dfb7afa2-26ae-4ca7-bce1-e5ea04a48f55): step-by-step routine timer

## Install

```bash
npx skills add jk0bson/garmin-skills
```

## Claude Code plugin

```text
/plugin marketplace add jk0bson/garmin-skills
/plugin install garmin@garmin-skills
```

## Requirements

The Connect IQ SDK and devices (SDK Manager). The simulator skill assumes macOS (`osascript`, `screencapture`). The scripts need Python 3; `bitmap_fonts.py` and `check_listing.py` also need Pillow.

## Tests

```bash
pip install pytest pillow
python -m pytest
```

The tests run the three scripts for real (a small OFL font is in `tests/fonts/`) and check the skills' structure, on Linux in GitHub Actions.

## License

MIT
