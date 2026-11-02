# Colors

## Three palettes

| Screen | Use |
|---|---|
| AMOLED on black | full colors, e.g. zones `#5096FF #28C878 #FACD28 #FF821E #F03C3C` |
| MIP on black | only channel values 00/55/AA/FF, e.g. `#55AAFF #55FF55 #FFFF00 #FFAA00 #FF0000` |
| Any screen on white | darker values, e.g. `#0055FF #00AA00 #AAAA00 #FF5500 #AA0000` |

Detect AMOLED with `(ds has :requiresBurnInProtection) && ds.requiresBurnInProtection`, and the background with `getBackgroundColor()` in a data field.

## Rules

- Choose each MIP color by eye from the 64 available, keeping the hue family. Never let the compiler round an arbitrary color.
- Light pastel colors vanish on white: use the dark palette there.
- Text on a filled pill uses the background color, so it works on black and white.
- Color carries a zone or state; one color, one meaning across the screen.
- Users asked for fewer themes, not more: one theme that follows the watch background beat five.
