#!/usr/bin/env python3
"""Generate Connect IQ bitmap fonts (BMFont .fnt + .png) for every round screen size in a manifest.

Only the characters you list are rendered. Coverage goes in RGB and alpha (antialiased on the watch) and the
line height is trimmed to the glyphs, so TEXT_JUSTIFY_VCENTER centers on the ink.

--font name:path.ttf:em:tracking:characters
  em         size on a 390 px screen, scaled for the other sizes
  tracking   extra letter spacing as a fraction of the em (0 for numbers)
  characters last, so it may contain ':'

Example:
  python3 bitmap_fonts.py --project . \
      --font "big:fonts/MyFont-SemiBold.ttf:96:0:0123456789:.-" \
      --font "label:fonts/MyFont-Medium.ttf:19:0.12:ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 /:-.%+"
Then load them with WatchUi.loadResource(Rez.Fonts.BigFont) and Rez.Fonts.LabelFont.
Requires Pillow.
"""
import argparse, json, os, re
from PIL import Image, ImageDraw, ImageFont

DEFAULT_DEVICES = os.path.expanduser("~/Library/Application Support/Garmin/ConnectIQ/Devices")


def build(out, name, ttf, size, chars, track):
    font = ImageFont.truetype(ttf, size)
    glyphs = []
    for ch in chars:
        l, t, r, b = font.getbbox(ch, anchor="ls")
        glyphs.append((ch, l, t, r, b, round(font.getlength(ch) + track * size)))
    top = min(g[2] for g in glyphs if g[0] != " ")
    base = -top
    pad, atlas_w = 2, 512
    x = y = row_h = 0
    placed = []
    for ch, l, t, r, b, adv in glyphs:
        w, h = r - l, b - t
        if ch == " " or w <= 0 or h <= 0:
            placed.append((ch, 0, 0, 0, 0, l, t, adv)); continue
        if x + w + pad > atlas_w:
            x, y, row_h = 0, y + row_h + pad, 0
        placed.append((ch, x, y, w, h, l, t, adv))
        x += w + pad; row_h = max(row_h, h)
    atlas_h = 1
    while atlas_h < y + row_h + pad:
        atlas_h *= 2
    img = Image.new("RGBA", (atlas_w, atlas_h), (0, 0, 0, 0))
    for ch, gx, gy, w, h, l, t, adv in placed:
        if w == 0: continue
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).text((-l, -t), ch, font=font, fill=255, anchor="ls")
        img.paste(Image.merge("RGBA", (mask, mask, mask, mask)), (gx, gy))   # coverage in color AND alpha
    img.save(os.path.join(out, name + ".png"))
    lines = [f'info face="{name}" size={size} bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=1 aa=1 padding=0,0,0,0 spacing=0,0 outline=0',
             f"common lineHeight={base + 1} base={base} scaleW={atlas_w} scaleH={atlas_h} pages=1 packed=0",
             f'page id=0 file="{name}.png"', f"chars count={len(placed)}"]
    for ch, gx, gy, w, h, l, t, adv in placed:
        lines.append(f"char id={ord(ch)} x={gx} y={gy} width={w} height={h} xoffset={l} yoffset={base + t} xadvance={adv} page=0 chnl=15")
    open(os.path.join(out, name + ".fnt"), "w").write("\n".join(lines) + "\n")


def screen_sizes(project, devices):
    """round screen sizes of the devices listed in the manifest"""
    ids = re.findall(r'iq:product id="([^"]+)"', open(os.path.join(project, "manifest.xml")).read())
    sizes = set()
    for d in ids:
        r = json.load(open(os.path.join(devices, d, "compiler.json")))["resolution"]
        if r["width"] == r["height"]:
            sizes.add(r["width"])
    return sorted(sizes)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", default=".", help="folder with manifest.xml")
    ap.add_argument("--devices", default=DEFAULT_DEVICES, help="Connect IQ Devices folder")
    ap.add_argument("--font", action="append", required=True, help="name:path.ttf:em:tracking:characters")
    args = ap.parse_args()
    fonts = []
    for spec in args.font:
        name, ttf, em, track, chars = spec.split(":", 4)
        fonts.append((name, ttf, int(em), chars, float(track)))

    def build_all(out, screen):
        os.makedirs(out, exist_ok=True)
        for name, ttf, em, chars, track in fonts:
            build(out, name, ttf, max(8, round(em * screen / 390)), chars, track)
        with open(os.path.join(out, "fonts.xml"), "w") as f:
            f.write("<fonts>\n" + "".join(f'    <font id="{n.capitalize()}Font" filename="{n}.fnt" antialias="true" />\n'
                                          for n, *_ in fonts) + "</fonts>\n")

    build_all(os.path.join(args.project, "resources", "fonts"), 260)   # fallback
    sizes = screen_sizes(args.project, args.devices)
    for s in sizes:
        build_all(os.path.join(args.project, f"resources-round-{s}x{s}", "fonts"), s)
    print("fonts for", sizes)


if __name__ == "__main__":
    main()
