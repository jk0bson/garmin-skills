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

For a screen that is hard to reach (minute 58 of a run, a coach alert, a hill), compile a temporary copy that forces the values in `onUpdate`, capture it, and never ship that copy.
