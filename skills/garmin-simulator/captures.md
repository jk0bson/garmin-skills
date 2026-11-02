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
