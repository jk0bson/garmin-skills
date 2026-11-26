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

- Write a script that measures every label from the `.fnt` advances at every size and prints the ones wider than their slot. It found 14 overflowing labels that no screenshot had shown. A short version:

```python
import math, os, re, sys, xml.etree.ElementTree as ET
# python3 label_width.py FONT PROJECT STRINGS_XML ID_REGEX DY MARGIN   e.g. label . resources-fre/strings/strings.xml '^L' 0.55 0.85
# DY: line distance from the center in radii (0 = middle); MARGIN: share of the chord the text may use
font, proj, xml, ids, dy, margin = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], float(sys.argv[5]), float(sys.argv[6])
labels = [(e.get('id'), (e.text or '').strip()) for e in ET.parse(xml).getroot().iter('string') if re.search(ids, e.get('id', ''))]
for d in sorted(os.listdir(proj)):
    m = re.fullmatch(r'resources-round-(\d+)x\d+', d)
    if not m: continue
    size = int(m[1]); r = size / 2
    with open(f'{proj}/{d}/fonts/{font}.fnt', encoding='utf-8') as f:
        adv = {int(c): int(a) for c, a in re.findall(r'char id=(\d+).*?xadvance=(\d+)', f.read())}
    room = 2 * math.sqrt(r * r - (dy * r) ** 2) * margin
    over = [f'{i} {sum(adv.get(ord(c), 0) for c in t)}px' for i, t in labels if sum(adv.get(ord(c), 0) for c in t) > room]
    print(size, f'room {room:.0f}px', 'OVER ' + ', '.join(over) if over else 'ok')
```

  Run it once per language folder (`resources-fre`, `resources-deu`, ...), with the `.fnt` files of the project. Tested on zonely: all labels fit at 0.55 radius; at 0.85 radius with a 0.5 margin it flags MARATHON, ALL. TOUR and ACCÉLÈRE on the small screens.
- Fallback order: full label with unit, label without unit, abbreviation in the strings file.

## Audit copy

Cycle every data choice through every slot with extreme values on the nine sizes and log overlaps: the method is in `garmin-simulator` ([captures.md](../garmin-simulator/captures.md)).

## Always-on shift

On AMOLED always-on screens, move the content a few pixels every minute: pick a vertical offset from a short table with `clock.min % n` and add it to every `y` (seen in Crystal Face, not verified here). Pixel and time limits are in `garmin-app` ([memory-and-api.md](../garmin-app/memory-and-api.md)).
