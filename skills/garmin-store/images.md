# Store images

## Screenshot layout (900×900)

- Dark textured background that suits the app (track lanes, pitch, wood), a soft glow in the accent color behind the watch.
- A small spaced-capitals kicker in the accent color, a headline of about 5 words, one muted line under it.
- The watch screen large, cropped exactly to the round screen, in a thin dark bezel with a drop shadow.
- Order: the main screen in real use, then the most popular modes, then the clever features. Keep popular first, not newest.

## Hero (1440×720, one per language)

Three watches on the left (main screen large, two others behind), the name and a two-line promise on the right.

## Crop the screen exactly

A crop a few pixels too wide, then masked to a circle, cuts off whatever sits at the screen's edge: a zone ring vanished from every image. Measure the ring or screen edge in one capture, crop all captures to that exact square, and mask with almost no inset.

## Staying under 150 KB

- Dark images compress well as optimized PNG.
- When too heavy, quantize to a mixed palette: half median-cut (smooth glows) and half fast-octree (small vivid colors), without dithering. 128 median-cut colors alone turned a green heart-rate grey; dithering pushed files over the limit.
- GIF at 450 px with one shared palette for all frames; halve the colors until it fits.

## Demo states

Hard-to-reach screens (minute 58 of a run, a coach alert, a hill) come from a temporary demo copy: see `garmin-simulator` ([captures.md](../garmin-simulator/captures.md)).

## Four directions

Keep every technical limit above whichever you pick: 900×900, under 150 KB, the real watch screen cropped exactly, 64-color MIP values on MIP screens. Only the mood changes. Colors are starting points.

| Style | Look | Fits |
|---|---|---|
| **Dark Atmospheric Glow** (default) | Dark textured background (track, sauna wood, pitch), soft glow in the accent color behind the watch, spaced-capitals kicker, headline of about 5 words | AMOLED watch faces, wellness timers, evening running |
| **Swiss Editorial** | Pale grey `#F4F5F7` or off-white, black type at high contrast, 1 px hairlines, one vivid accent (orange `#FF4500` or cobalt `#0055FF`) | score counters (tennis, padel, golf), timers, everyday tools; shows MIP screens in sunlight |
| **Tactical Instrument** | Matte slate `#14181C` with a faint topographic grid, tabular monospace digits, framed status badges, amber `#FFAA00` or phosphor green `#28C878` | hiking, sensor and battery tools, rugged watches (fēnix, Enduro, Instinct) |
| **Bold Sport Split** | Background cut into two flat blocks (or a diagonal): deep black against a saturated accent; the watch shifted right with a hard drop shadow; the promise in very large type on the left ("3 METRICS. 1 GLANCE.") | performance data fields: cycling, running, power, heart-rate zones |

Only the first has been used on real listings here. Check the other three on a light and a dark capture before relying on them: a pale background shows a white-background data field poorly.
