# Bitmap fonts

## Why

System fonts change between watches, and small MIP screens have no vector fonts. A bitmap font makes numbers look the same everywhere and lets you pick the typeface.

## How

1. Pick an OFL typeface and keep its license file next to it.
2. For each round screen size, render only the characters you need (digits and `:.-` for numbers; capitals, accents and a few symbols for labels) at `em × size / 390`.
3. Write a BMFont text `.fnt` and an RGBA `.png` atlas. Put the glyph coverage in R, G, B and A: with coverage only in alpha, the watch draws hard edges.
4. Start the line at the tallest glyph and end it at the lowest descender, so `TEXT_JUSTIFY_VCENTER` centers on the ink. Number fonts without descenders get a line exactly as tall as the digits.
5. Save to `resources-round-WxH/fonts/` with a `fonts.xml`, plus a fallback in `resources/fonts/`.

`scripts/bitmap_fonts.py` does all of this from your manifest's device list.

## Pitfalls

- Accented capitals in a font raise its line box: centered text sits low. Give centered capital-only text (pills, badges) its own font without accents.
- Wide humanist typefaces (Amarna) are about 15 % wider than condensed ones (Barlow Condensed) at the same digit height: re-check every slot.
- Proportional digits make a centered number wobble slightly as it changes; acceptable centered, ugly left-aligned.
- Each extra font and size costs memory: a data field on fēnix 8 has 128 KB.
