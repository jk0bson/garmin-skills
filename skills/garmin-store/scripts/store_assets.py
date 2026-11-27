#!/usr/bin/env python3
"""Compose the Connect IQ Store images of one app from simulator captures: cover 500x500, hero 1440x720, up to 4 screenshots
900x900 and an animated GIF, named and sized to pass check_listing.py. Run it once per language (--lang).

Presets (the layouts that have shipped on real listings):
  watchface  flat background in the face's own colours (one per screenshot), no bezel, soft drop shadow, a quiet strip at the
             bottom, kicker / rule / headline / line; the GIF cycles the themes (the same for every language)
  app        dark textured backdrop, glow in the accent colour behind round bezelled watches (1 to 3 per screenshot)
  datafield  the same dark composition, track-lane backdrop by default; list several accents (zone colours) for a multi-colour rule

Captures are square PNGs of the watch screen (simulator window cropped to the screen): DIR/<lang>/<name>.png or DIR/<name>.png.
Colours are #RRGGBB. Every --screen is "CAPTURES|KICKER|HEADLINE|SUB" plus an optional "|#COLOR" (watchface: background; app and
datafield: glow); CAPTURES is a comma list (watches left to right for 2, left / middle / right for 3).

  store_assets.py --preset app --name "my app" --captures caps --out store/images --lang en --accent "#FF7A1A,#3D8BFF" \\
      --screen "main|LIVE|Your sessions|Rounds, heat and time" --screen "stats,list|MY STATS|The week|Minutes per day|#3D8BFF" \\
      --hero main,stats,list --hero-lines "Feel the heat,|round by round." --hero-sub "Sessions, stats,|and more." --gif a,b,c

Prints the "screens" line for store.json. Needs Pillow. Use --font (a .ttf, variable fonts get their weight axis) for the type.
"""
import argparse, math, os, re, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = 900
KB = 1024
PRESETS = {"watchface": dict(flat=True), "app": dict(flat=False, backdrop="waves"), "datafield": dict(flat=False, backdrop="track")}
BACKDROPS = ("court", "pitch", "tiles", "track", "waves", "wood")
IVORY, MUTED = (245, 240, 230), (138, 133, 120)
FLAT_LAYOUT = {1: [(450, 568, 600)], 2: [(262, 568, 400), (638, 568, 400)],
               3: [(265, 450, 350), (635, 450, 350), (450, 715, 350)], 4: [(290, 425, 305), (610, 425, 305), (290, 735, 305), (610, 735, 305)]}
DARK_LAYOUT = {1: [(450, 568, 580)], 2: [(300, 560, 470), (640, 600, 400)], 3: [(215, 610, 340), (450, 570, 420), (685, 610, 340)]}
SYSTEM_FONTS = ("DejaVuSans.ttf", "Arial.ttf", "Helvetica.ttc", "/System/Library/Fonts/Helvetica.ttc")


# ---------- small helpers ----------

def hexcolor(s):
    m = re.fullmatch(r"#?([0-9a-fA-F]{6})", s.strip())
    if not m:
        raise SystemExit(f"colour {s!r}: use #RRGGBB")
    return tuple(int(m[1][i:i + 2], 16) for i in (0, 2, 4))


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_") or "x"


def luminance(c):
    return .299 * c[0] + .587 * c[1] + .114 * c[2]


def load_font(path, size, weight=400):
    if path:
        f = ImageFont.truetype(path, int(size))
    else:
        for name in SYSTEM_FONTS:
            try:
                f = ImageFont.truetype(name, int(size)); break
            except OSError:
                continue
        else:
            f = ImageFont.load_default(int(size))
    try:   # variable font: set the weight axis, leave the others (optical size...) at their default
        f.set_variation_by_axes([min(a["maximum"], max(a["minimum"], weight)) if str(a["name"]).strip("b'\"") == "Weight" else a["default"]
                                 for a in f.get_variation_axes()])
    except (OSError, AttributeError, ValueError, KeyError):
        pass
    return f


def tracked(d, xy, text, f, fill, tracking, centered=False):
    widths = [f.getlength(c) for c in text]
    x, y = xy
    if centered:
        x -= (sum(widths) + tracking * (len(text) - 1)) / 2
    for c, w in zip(text, widths):
        d.text((x, y), c, font=f, fill=fill, anchor="ls"); x += w + tracking


def fit(text, make, size, maxw, tracking=0):
    """largest font (from size down to 12) in which text fits maxw; an error if even 12 is too wide"""
    def width(f): return f.getlength(text) + tracking * (len(text) - 1)
    while size > 12 and width(make(size)) > maxw:
        size -= 2
    f = make(size)
    if width(f) > maxw:
        raise SystemExit(f"text too long for the image: {text!r}")
    return f


# ---------- drawing ----------

def backdrop(w, h, kind):
    """a dark texture, barely visible: lines of a court, mown pitch, tiles, running-track lanes, waves or wooden slats"""
    c = Image.new("RGB", (w, h), (10, 10, 10)); d = ImageDraw.Draw(c); s = h / 720
    lw = max(2, int(3 * s))
    if kind == "court":
        c.paste((12, 13, 15), (0, 0, w, h))
        line = (30, 31, 34)
        x0, x1, y0, y1 = int(w * .06), int(w * .94), int(h * .08), int(h * .92)
        d.rectangle([x0, y0, x1, y1], outline=line, width=lw)
        d.line([(w // 2, y0), (w // 2, y1)], fill=(38, 39, 42), width=lw * 2)
        for x in (x0 + (x1 - x0) * .2, x1 - (x1 - x0) * .2):
            d.line([(x, y0), (x, y1)], fill=line, width=lw)
        d.line([(x0 + (x1 - x0) * .2, h // 2), (x1 - (x1 - x0) * .2, h // 2)], fill=line, width=lw)
    elif kind == "pitch":
        band = max(60, w // 12)
        for i, x in enumerate(range(0, w, band)):
            d.rectangle([x, 0, x + band, h], fill=(11, 19, 14) if i % 2 else (14, 24, 17))
        r = int(h * .3)
        d.ellipse([w // 2 - r, h // 2 - r, w // 2 + r, h // 2 + r], outline=(26, 40, 30), width=lw)
        d.line([(w // 2, 0), (w // 2, h)], fill=(26, 40, 30), width=lw)
    elif kind == "tiles":
        c.paste((14, 12, 11), (0, 0, w, h))
        t = max(70, w // 10)
        for x in range(0, w, t):
            d.line([(x, 0), (x, h)], fill=(22, 19, 17), width=2)
        for y in range(0, h, t):
            d.line([(0, y), (w, y)], fill=(22, 19, 17), width=2)
    elif kind == "track":
        c.paste((16, 11, 10), (0, 0, w, h))
        lane = max(38, h // 14)
        cx, cy = int(w * .5), int(h * 1.35)
        for i in range(14):
            r = int(h * .55) + i * lane
            d.ellipse([cx - r * 1.4, cy - r, cx + r * 1.4, cy + r], outline=(30, 21, 19), width=max(2, int(2 * s)))
    elif kind == "waves":
        c.paste((10, 11, 19), (0, 0, w, h))
        gap = max(48, h // 12)
        for i, y0 in enumerate(range(-gap, h + gap, gap)):
            d.line([(x, y0 + gap * .22 * math.sin(x / w * math.pi * 3 + i * .7)) for x in range(0, w + 8, 8)], fill=(22, 26, 46), width=max(2, int(2 * s)))
    elif kind == "wood":
        slat = max(40, h // 9)
        for i, y in enumerate(range(0, h, slat)):
            d.rectangle([0, y, w, y + slat - 3], fill=(19, 15, 12) if i % 2 else (16, 13, 10))
    if w == h and kind in ("court", "pitch"):   # square: the net / centre line becomes horizontal, hidden behind the watch
        c = c.transpose(Image.Transpose.ROTATE_90)
    return c


def glow(canvas, cx, cy, r, color, strength=.3):
    m = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=int(255 * strength))
    canvas.paste(color, (0, 0), m.filter(ImageFilter.GaussianBlur(r / 2.2)))


def watch(canvas, path, cx, cy, d, inset, bezel):
    """a capture as a disc, with a drop shadow; bezel=True adds a thin dark bezel. inset trims the simulator's edge: keep it near 0
    when something sits on the screen's edge (a ring), a little more when the capture still shows the simulator's corners"""
    im = Image.open(path).convert("RGB")
    if im.width != im.height:
        raise SystemExit(f"{os.path.basename(path)}: {im.width}x{im.height}, crop the capture to the square screen first")
    im = im.resize((d, d), Image.LANCZOS)
    big = d * 4
    mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask).ellipse([big * inset, big * inset, big * (1 - inset), big * (1 - inset)], fill=255)
    mask = mask.resize((d, d), Image.LANCZOS)
    if bezel:
        r = d // 2 + d // 26
        sh = Image.new("L", canvas.size, 0)
        ImageDraw.Draw(sh).ellipse([cx - r, cy - r + r // 10, cx + r, cy + r + r // 10], fill=200)
        canvas.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(r / 9)))
        ImageDraw.Draw(canvas).ellipse([cx - r, cy - r, cx + r, cy + r], fill=(22, 21, 20), outline=(70, 66, 60), width=max(2, r // 90))
    else:
        sh = Image.new("L", canvas.size, 0)
        sh.paste(mask, (cx - d // 2 + d // 40, cy - d // 2 + d // 25))
        canvas.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(d / 40)).point(lambda v: v * 45 // 100))
    canvas.paste(im, (cx - d // 2, cy - d // 2), mask)


def deco(c, paper, ink, kind):
    """the quiet strip at the bottom of a flat screenshot: a gauge line with ticks, a band of dots, or nothing"""
    d = ImageDraw.Draw(c)
    p = tuple((a * 3 + b) // 4 for a, b in zip(paper, ink))
    if kind == "gauge":
        d.line([(0, 800), (c.width, 800)], fill=p, width=3)
        for i in range(0, c.width + 1, c.width // 8):
            d.line([(i, 784), (i, 800)], fill=p, width=3)
    elif kind == "dots":
        for y in range(780, c.height, 14):
            for x in range((y // 14 % 2) * 7, c.width, 14):
                d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=p)


# ---------- saving under the store's limits ----------

def mixed_palette(im, colors=256):
    """half median-cut (smooth glows and gradients), half fast-octree (the few small vivid colours, an accent line, a ring):
    median-cut alone turns a thin green or orange accent grey"""
    half = colors // 2 if colors < 256 else colors * 3 // 4
    smooth = im.quantize(half, method=Image.Quantize.MEDIANCUT).getpalette()[:half * 3]
    vivid = im.quantize(colors - half, method=Image.Quantize.FASTOCTREE).getpalette()[:(colors - half) * 3]
    pal = Image.new("P", (1, 1)); pal.putpalette(smooth + vivid)
    return pal


def save_png(im, path, max_kb):
    """optimized PNG; if heavier than max_kb, the mixed palette (256 colours, then 128, 64, 32), never dithered"""
    im.save(path, optimize=True)
    colors = 256
    while os.path.getsize(path) > max_kb * KB and colors >= 32:
        im.quantize(palette=mixed_palette(im, colors), dither=Image.Dither.NONE).save(path, optimize=True)
        colors //= 2
    kb = os.path.getsize(path) / KB
    if kb > max_kb:
        raise SystemExit(f"{os.path.basename(path)}: {kb:.0f} KB, over {max_kb}")
    print(os.path.basename(path), im.size, f"{kb:.0f} KB")


def save_gif(frames, path, ms, max_kb=145):
    """one shared mixed palette for all frames; biggest size first (450 px, then down to 280), most colours first (256 down to 16)"""
    for size in (450, 400, 360, 320, 280):
        small = [f.resize((size, size), Image.LANCZOS) for f in frames]
        strip = Image.new("RGB", (size, size * len(small)))
        for i, f in enumerate(small):
            strip.paste(f, (0, i * size))
        for colors in (256, 128, 64, 32, 16):
            pal = mixed_palette(strip, colors)
            q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in small]
            q[0].save(path, save_all=True, append_images=q[1:], duration=ms, loop=0, optimize=True)
            if os.path.getsize(path) <= max_kb * KB:
                print(os.path.basename(path), f"{size}px {colors} colours", f"{os.path.getsize(path) // KB} KB")
                return
    raise SystemExit(f"{os.path.basename(path)}: over {max_kb} KB even at 280 px and 16 colours: fewer frames")


# ---------- one run = one language ----------

class Run:
    def __init__(self, a):
        self.a, self.lang = a, a.lang
        self.flat = PRESETS[a.preset]["flat"]
        self.accents = [hexcolor(c) for c in a.accent.split(",")]
        self.accent = self.accents[0]
        self.bg = hexcolor(a.bg)
        self.kind = a.backdrop or PRESETS[a.preset].get("backdrop")
        self.inset = .03 if self.flat else .004
        os.makedirs(a.out, exist_ok=True)

    def display(self, size, weight=600): return load_font(self.a.font, size, weight)
    def body(self, size, weight=400): return load_font(self.a.font_body or self.a.font, size, 600 if self.flat else weight)   # flat: bold small type, as on the references
    def ink(self, paper): return hexcolor(self.a.ink) if self.a.ink else ((10, 10, 10) if luminance(paper) > 128 else (242, 242, 242))
    def out(self, name): return os.path.join(self.a.out, name)

    def cap(self, name):
        for p in (os.path.join(self.a.captures, self.lang, name + ".png"), os.path.join(self.a.captures, name + ".png")):
            if os.path.exists(p):
                return p
        raise SystemExit(f"capture {name}.png not found in {self.a.captures}")

    def watch(self, c, name, cx, cy, d):
        watch(c, self.cap(name), cx, cy, d, self.inset, not self.flat)

    def trio(self, c, names, left, right, mid):
        """names = main[, left, right]; side watches first so the main one overlaps them"""
        for n, (x, y, d) in zip(names[1:3], (left, right)):
            self.watch(c, n, x, y, d)
        self.watch(c, names[0], *mid)

    # --- screenshots 900x900 ---
    def screen(self, names, kicker, headline, sub, color):
        if self.flat:
            paper = color or self.bg
            ink = self.ink(paper)
            c = Image.new("RGB", (W, W), paper)
            deco(c, paper, ink, self.a.deco)
            d = ImageDraw.Draw(c)
            tracked(d, (W / 2, 78), kicker, fit(kicker, lambda s: self.body(s, 600), 24, W - 80, 5), ink, 5, True)
            d.line([(W / 2 - 40, 98), (W / 2 + 40, 98)], fill=self.accent if luminance(paper) < 60 else ink, width=3)
            d.text((W / 2, 168), headline, font=fit(headline, self.display, 60, W - 80), fill=ink, anchor="ms")
            d.text((W / 2, 218), sub, font=fit(sub, self.body, 26, W - 80), fill=ink, anchor="ms")
            for n, pos in zip(names, FLAT_LAYOUT[len(names)]):
                self.watch(c, n, *pos)
            return c
        color = color or self.accent
        c = backdrop(W, W, self.kind)
        glow(c, W // 2, 575, 330, color, .3)
        d = ImageDraw.Draw(c)
        tracked(d, (W / 2, 82), kicker, fit(kicker, lambda s: self.body(s, 500), 24, W - 80, 7), color, 7, True)
        d.text((W / 2, 158), headline, font=fit(headline, lambda s: self.display(s, 400), 60, W - 80), fill=IVORY, anchor="ms")
        d.text((W / 2, 208), sub, font=fit(sub, lambda s: self.body(s, 300), 30, W - 80), fill=MUTED, anchor="ms")
        pos = DARK_LAYOUT[len(names)]
        for n, p in sorted(zip(names, pos), key=lambda t: t[1][2] > 400):   # biggest last, on top
            self.watch(c, n, *p)
        return c

    # --- cover 500x500 ---
    def cover(self, names):
        name, tail = self.a.name, self.a.name_accent
        text = name + tail
        if self.flat:
            c = Image.new("RGB", (1000, 1000), self.bg)
            self.trio(c, names, (290, 610, 470), (710, 610, 470), (500, 570, 560))
            ImageDraw.Draw(c).text((500, 200), text, font=fit(text, self.display, 150, 900), fill=self.ink(self.bg), anchor="ms")
        else:
            c = backdrop(1000, 1000, self.kind)
            glow(c, 500, 640, 420, self.accent, .28)
            self.watch(c, names[0], 500, 640, 500)
            d = ImageDraw.Draw(c)
            f = fit(text, lambda s: self.display(s, 300), 120, 900)
            x = 500 - f.getlength(text) / 2
            d.text((x, 190), name, font=f, fill=IVORY, anchor="ls")
            d.text((x + f.getlength(name), 190), tail, font=f, fill=self.accent, anchor="ls")
        save_png(c.resize((500, 500), Image.LANCZOS), self.out("cover_500x500.png"), 290)

    # --- hero 1440x720 ---
    def hero(self, names):
        lines = (self.a.hero_lines.split("|") + ["", ""])[:2]
        subs = (self.a.hero_sub.split("|") + ["", ""])[:2]
        name, tail = self.a.name, self.a.name_accent
        if self.flat:
            c = Image.new("RGB", (1440, 720), self.bg); ink = self.ink(self.bg); x = 860
            self.trio(c, names, (220, 390, 380), (600, 390, 380), (410, 370, 450))
            d = ImageDraw.Draw(c)
            d.text((x, 190), name + tail, font=fit(name + tail, self.display, 80, 1400 - x), fill=ink, anchor="ls")
            d.line([(x, 225), (x + 90, 225)], fill=self.accent, width=4)
            rows = ((lines[0], self.display, 64, 320), (lines[1], self.display, 64, 400), (subs[0], self.body, 24, 490), (subs[1], self.body, 24, 540))
            for t, make, size, y in rows:
                d.text((x, y), t, font=fit(t, make, size, 1400 - x), fill=ink, anchor="ls")
        else:
            c = backdrop(1440, 720, self.kind); x = 840
            glow(c, 410, 380, 380, self.accent, .28)
            self.trio(c, names, (205, 390, 360), (615, 390, 360), (410, 365, 450))
            d = ImageDraw.Draw(c)
            f = fit(name + tail, lambda s: self.display(s, 300), 46, 1400 - x)
            d.text((x, 190), name, font=f, fill=IVORY, anchor="ls")
            d.text((x + f.getlength(name), 190), tail, font=f, fill=self.accent, anchor="ls")
            for i in range(5):   # the rule: one stripe per accent colour, cycling
                d.rectangle([(x + i * 22, 222), (x + i * 22 + 18, 225)], fill=self.accents[i % len(self.accents)] if len(self.accents) > 1 else self.accent)
            rows = ((lines[0], lambda s: self.display(s, 300), 60, 312, IVORY), (lines[1], lambda s: self.display(s, 400), 60, 388, self.accent),
                    (subs[0], lambda s: self.body(s, 300), 30, 470, MUTED), (subs[1], lambda s: self.body(s, 300), 30, 518, MUTED))
            for t, make, size, y, col in rows:
                d.text((x, y), t, font=fit(t, make, size, 1400 - x), fill=col, anchor="ls")
        save_png(c, self.out(f"hero_1440x720_{self.lang}.png"), 1900)

    # --- GIF ---
    def gif(self, names):
        if self.flat:   # the themes cycle: the watch alone on the background
            frames = []
            for n in names:
                c = Image.new("RGB", (450, 450), self.bg)
                self.watch(c, n, 225, 225, 438)
                frames.append(c)
        else:
            kicker, head, sub = (self.a.gif_text.split("|") + ["", "", ""])[:3]
            frames = [self.screen([n], kicker, head, sub, None) for n in names]
        save_gif(frames, self.out(f"{self.lang}_0_{self.a.gif_name}.gif"), self.a.gif_ms)


def parse_screen(s):
    parts = s.split("|")
    if len(parts) not in (4, 5):
        raise SystemExit(f'--screen {s!r}: use "CAPTURES|KICKER|HEADLINE|SUB[|#COLOR]"')
    names = [n for n in parts[0].split(",") if n]
    if not 1 <= len(names) <= 4:
        raise SystemExit(f"--screen {s!r}: 1 to 4 captures")
    return names, parts[1], parts[2], parts[3], hexcolor(parts[4]) if len(parts) == 5 else None


def generate(a):
    r = Run(a)
    screens = [parse_screen(s) for s in a.screen]
    if not r.flat and any(len(s[0]) > 3 for s in screens):
        raise SystemExit("app and datafield presets: at most 3 watches per screenshot")
    if len(screens) + bool(a.gif) > 5:
        print("warning: the store takes 5 images in all; the GIF counts as one", file=sys.stderr)
    first = screens[0][0]
    r.cover((a.cover.split(",") if a.cover else first))
    r.hero((a.hero.split(",") if a.hero else first))
    if a.gif:
        r.gif(a.gif.split(","))
    files = []
    for i, (names, kicker, head, sub, color) in enumerate(screens, 1):
        files.append("{lang}_%d_%s.png" % (i, slug(names[0])))
        save_png(r.screen(names, kicker, head, sub, color), r.out(files[-1].format(lang=a.lang)), 145)
    gif_name = ["{lang}_0_%s.gif" % a.gif_name] if a.gif else []
    print('"screens":', str(gif_name + files).replace("'", '"'))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--preset", required=True, choices=sorted(PRESETS))
    p.add_argument("--name", required=True, help="the app name, in the cover and the hero")
    p.add_argument("--name-accent", default="", help="a tail of the name drawn in the accent colour (dark presets), e.g. ly")
    p.add_argument("--captures", required=True, metavar="DIR")
    p.add_argument("--out", required=True, metavar="DIR", help="the store/images folder")
    p.add_argument("--lang", default="en")
    p.add_argument("--accent", default="#FF7A1A", help="#RRGGBB, or several separated by commas (datafield zone colours)")
    p.add_argument("--bg", default="#141414", help="cover, hero and GIF background of the watchface preset; its default screenshot background")
    p.add_argument("--ink", help="text colour (watchface); default black or white by the background")
    p.add_argument("--font", help=".ttf for headlines and the name (default: a system font)")
    p.add_argument("--font-body", help=".ttf for small text (default: --font)")
    p.add_argument("--backdrop", choices=BACKDROPS, help="texture of the dark presets (app: waves, datafield: track)")
    p.add_argument("--deco", choices=("gauge", "dots", "none"), default="gauge", help="bottom strip of the watchface screenshots")
    p.add_argument("--screen", action="append", required=True, metavar="CAPS|KICKER|HEADLINE|SUB[|#COLOR]")
    p.add_argument("--cover", metavar="CAPS", help="main[,left,right]; default: the first screenshot's")
    p.add_argument("--hero", metavar="CAPS", help="main[,left,right]; default: the first screenshot's")
    p.add_argument("--hero-lines", default="", metavar='"LINE 1|LINE 2"')
    p.add_argument("--hero-sub", default="", metavar='"LINE 3|LINE 4"')
    p.add_argument("--gif", metavar="CAPS", help="the frames, in order (themes for a watchface)")
    p.add_argument("--gif-name", default="anim")
    p.add_argument("--gif-text", default="", metavar='"KICKER|HEADLINE|SUB"', help="app and datafield GIF frames")
    p.add_argument("--gif-ms", type=int, default=1000, help="milliseconds per frame")
    generate(p.parse_args(argv))


if __name__ == "__main__":
    main()
