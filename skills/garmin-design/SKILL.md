---
name: garmin-design
description: Designs and reviews what a Garmin watch screen shows, covering round screens from 218 to 466 px, AMOLED and 64-color MIP palettes, bitmap fonts, text that fits its slot, arcs, icons and white backgrounds. Use when drawing a Connect IQ watch face, data field or app screen, or when text, colors or placement look wrong on some watches.
---

# Garmin screen design

This skill makes one design read well on every round Garmin screen, from a 218 px MIP Forerunner to a 466 px AMOLED fēnix. A screen that looks right on one watch is only a first draft.

Monkey C behavior belongs to `garmin-app`. Capturing screens belongs to `garmin-simulator`.

## Design for nine screen sizes, test one of each

Round Connect IQ screens come in 218, 240, 260, 280 (MIP, 64 colors) and 360, 390, 416, 454, 466 px (AMOLED). Before calling a screen done, run it on one watch per size with the longest values it can show ([screens.md](screens.md)).

## Place from measured heights, not fixed pixels

AMOLED fonts are taller than MIP fonts at the same nominal size. Position with fractions of the slot and `dc.getFontHeight()`, and center with `TEXT_JUSTIFY_VCENTER` on fonts whose line height is trimmed to the glyphs.

## Use your own bitmap fonts for numbers that matter

System fonts differ per watch and many small screens have no vector fonts. Generate a BMFont `.fnt` + `.png` per screen size with only the characters you draw, store the glyph coverage in the color AND the alpha channel or nothing is antialiased on the watch, and trim the line height to the glyphs ([fonts.md](fonts.md)).

## Keep accents out of fonts you center

A font whose character set includes `É` or `À` reserves room above the capitals, so `VCENTER` puts capitals too low. A zone pill read "Z4" off-center until it got its own font with only `Z`, digits and `-`.

## Check that every digit reads as itself

Some typefaces draw `1` as a bare stroke, so "Z1" reads "ZI" and "101" reads "IOI" at a glance. Look at `1`, `7`, `0` and `O` large before picking a typeface; patch the glyph in the font generator if needed.

## Every label fits its slot in every language

Measure each label's pixel width in every language against the slot it lands in. French and German labels run 30 % longer. Drop the unit, then abbreviate, never let two labels touch ([screens.md](screens.md)).

## Pick MIP colors yourself

MIP screens show 64 colors, channel values 00/55/AA/FF only. The compiler rounds badly (a brown turned olive green). Keep separate palettes for AMOLED, MIP and white backgrounds, and choose each MIP color by eye from the 64 ([colors.md](colors.md)).

## Draw arcs with `drawArc`

Arcs built from polygons look hand-drawn on a real watch. `dc.drawArc` is smooth. An arc from an angle to itself draws a full circle: guard zero-length arcs.

## A moving marker must not cover what it points at

A needle or bitmap drawn over text erases it. Size markers against the text around them on every screen size; a needle long enough to read on 390 px touched the heart icon at low zones.

## Draw icons once, large

Draw the launcher icon at 1024 px, reduce it with LANCZOS to each `launcherIcon` size from the device's `compiler.json`, and save one per `resources-round-WxH/drawables/`. Use the 64-color palette for MIP sizes.
