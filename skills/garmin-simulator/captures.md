# Audits and store captures

## Audit copy (every metric, every size)

1. Copy the project to a temporary folder with a script.
2. Insert an `audit()` call at the top of `onUpdate`: rotate the main data and each slot through all choices, rotate graph modes, and every third frame inject extremes (`10:00:00`, `12345`, `-35.0`, `1500 W`, `null` heart rate, zero speed).
3. Insert a `check()` after drawing that measures labels and values with `dc.getTextWidthInPixels` and prints `PROBLEM ...` when two of them overlap or a value is wider than its slot. Print every label and value too, to read formats.
4. Compile for one device per screen size, run each about 40 s with Activity Data playing, switch Layout through 1–4 fields and Background Color through white and black, capture each state.
5. Grep the logs for `PROBLEM`, `Error`, `Exception`; build one contact sheet of all captures and look at it.

This found a wrong label, 14 overflowing labels, a divide-by-zero and a needle covering an icon in one pass.

## Store captures

- One temporary copy per state (or one copy cycling states by clock time), values forced in `onUpdate`.
- One language per copy: copy the translated `strings.xml` over the default one and remove the other languages from the manifest.
- Capture on the most popular watch, crop exactly to the round screen.
- For an animated GIF, let the copy derive its state from `System.getTimer()`, capture once a second, and sort frames by a property that grows (graph fill) rather than by capture time.

## Contact sheet

One image of every capture, with its watch and size under it, shows a wrong color or a cut-off screen at a glance. Tested on 59 captures of aestify (`store/captures/<watch>/<language>/<state>.png`):

```python
import glob, os, sys
from PIL import Image, ImageDraw, ImageFont
# python3 contact_sheet.py CAPTURES_DIR sheet.png [CELL_PX] [COLUMNS]   e.g. store/captures sheet.png 160 8
# Expects CAPTURES_DIR/<watch>/<state>.png or <watch>/<language>/<state>.png; the label is that path.
src, out = sys.argv[1], sys.argv[2]
cell = int(sys.argv[3]) if len(sys.argv) > 3 else 160
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 8
files = sorted(glob.glob(os.path.join(src, "**", "*.png"), recursive=True))
if not files:
    sys.exit("no png under " + src)
font, label_h = ImageFont.load_default(), 28
rows = -(-len(files) // cols)
sheet = Image.new("RGB", (cols * (cell + 8) + 8, rows * (cell + label_h + 8) + 8), (40, 40, 44))
draw = ImageDraw.Draw(sheet)
for i, path in enumerate(files):
    im = Image.open(path).convert("RGBA")
    im.thumbnail((cell, cell), Image.LANCZOS)                     # keeps the aspect ratio: sizes stay comparable
    x, y = 8 + (i % cols) * (cell + 8), 8 + (i // cols) * (cell + label_h + 8)
    sheet.paste(im, (x + (cell - im.width) // 2, y + (cell - im.height) // 2), im)
    name = os.path.splitext(os.path.relpath(path, src))[0]
    draw.text((x, y + cell + 2), f"{name[-26:]}\n{Image.open(path).width}px", fill=(230, 230, 230), font=font)
sheet.save(out)
print(out, len(files), "captures,", sheet.size)
```
