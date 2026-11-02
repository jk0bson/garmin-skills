# Screens and layout

## One watch per screen size

| px | Type | Example watch |
|---|---|---|
| 218 | MIP, 64 colors | Forerunner 255S |
| 240 | MIP | fēnix 7S |
| 260 | MIP | fēnix 7, fēnix 8 Solar 47 mm |
| 280 | MIP | fēnix 7X, Enduro 3 |
| 360 | AMOLED | Forerunner 265S, Venu 2S |
| 390 | AMOLED | Forerunner 165 |
| 416 | AMOLED | epix Pro 47 mm |
| 454 | AMOLED | fēnix 8 47 mm |
| 466 | AMOLED | fēnix 9 Pro 51 mm |

Other watches share one of these sizes and the same resources folder (`resources-round-WxH`), so these nine cover the layout. Touch-only watches (vívoactive, Venu) still need an input check (`garmin-app`).

## Usable width on a round screen

At a distance `dy` from the center, the screen is `2·sqrt(r² − dy²)` wide. Text near the top and bottom gets much less room than at the center. Check the widest value of each line against that width, minus any ring drawn around the edge.

## Stress values

Render each slot with its longest real value, not a typical one: `10:00:00`, `1:52:40`, `12345`, `-35.0`, `+12.3%`, `--`, `-:--`. Pick the font per value: try the big font, fall back to smaller ones until the text fits the slot's width and height.

## Labels

- Write a script that measures every label from the `.fnt` advances at every size and prints the ones wider than their slot. It found 14 overflowing labels that no screenshot had shown.
- Fallback order: full label with unit, label without unit, abbreviation in the strings file.

## Audit copy

Build a temporary copy that, on every `onUpdate`, cycles every data choice through every slot, injects extreme values, and prints a line when two labels or values overlap. Run it on the nine sizes; read the log and the screenshots. Never ship the audit code.
