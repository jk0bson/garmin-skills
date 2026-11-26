#!/usr/bin/env python3
"""Check a Connect IQ Store listing folder before uploading it. Exit status 1 if anything would be refused.

Folder layout (the same as a project's store/ folder):
  store.json                 {"titres": {"en": "..."}, "langues": ["en"], "cover": "cover_500x500.png",
                              "hero": "hero_1440x720_{lang}.png", "screens": ["{lang}_1_main.png", ...]}
  description_<lang>.txt     one per language
  whats_new.txt              optional, parts "EN:" and "FR:" on their own lines
  images/                    cover, hero and screens named in store.json

Checks: title at most 50 characters, description at most 4000, no < or > in descriptions or What's New,
cover 500x500 under 300 KB, hero 1440x720 under 2 MB per language, at most 5 screenshots per language,
each under 150 KB. A screenshot that is not 900x900 (450x450 for a GIF) is only a note.
Usage: python3 check_listing.py STORE_FOLDER      Needs Pillow for the image sizes.
"""
import json, os, re, sys

LIMITS = {"title": 50, "description": 4000, "cover_kb": 300, "hero_kb": 2048, "screen_kb": 150, "screens": 5}


def check_image(path, size, max_kb, errors, notes=None, allowed=None):
    from PIL import Image
    name = os.path.basename(path)
    if not os.path.exists(path):
        errors.append(f"{name}: file missing"); return
    kb = os.path.getsize(path) / 1024
    if kb > max_kb:
        errors.append(f"{name}: {kb:.0f} KB (max {max_kb})")
    with Image.open(path) as im:
        got = im.size
    if size and got != size:
        errors.append(f"{name}: {got[0]}x{got[1]} instead of {size[0]}x{size[1]}")
    if allowed and got not in allowed:
        notes.append(f"{name}: {got[0]}x{got[1]}, the store images here are {' or '.join('%dx%d' % a for a in allowed)}")


def check(folder):
    """return (errors, notes) for a store folder"""
    errors, notes = [], []
    path = os.path.join(folder, "store.json")
    if not os.path.exists(path):
        return [f"store.json missing in {folder}"], notes
    with open(path, encoding="utf-8") as f:
        store = json.load(f)
    langs = store.get("langues", ["en"])
    for lang in langs:
        title = store.get("titres", {}).get(lang, "")
        if not title:
            errors.append(f"title {lang} missing")
        elif len(title) > LIMITS["title"]:
            errors.append(f"title {lang}: {len(title)} characters (max {LIMITS['title']})")
        p = os.path.join(folder, f"description_{lang}.txt")
        if not os.path.exists(p):
            errors.append(f"description_{lang}.txt missing"); continue
        with open(p, encoding="utf-8") as f:
            text = f.read()
        if len(text) > LIMITS["description"]:
            errors.append(f"description {lang}: {len(text)} characters (max {LIMITS['description']})")
        if "<" in text or ">" in text:
            errors.append(f"description {lang}: the site refuses < and >")
    wn = os.path.join(folder, "whats_new.txt")
    if os.path.exists(wn):
        with open(wn, encoding="utf-8") as f:
            text = f.read()
        for lang in langs:
            if not re.search(rf"^\s*{lang.upper()}\s*:\s*$", text, re.M):
                errors.append(f"whats_new.txt: part {lang.upper()}: missing")
        if "<" in text or ">" in text:
            errors.append("whats_new.txt: the site refuses < and >")
    try:
        import PIL  # noqa: F401
    except ImportError:
        return errors + ["Pillow missing: image checks skipped (pip install pillow)"], notes
    img = os.path.join(folder, "images")
    check_image(os.path.join(img, store.get("cover", "cover_500x500.png")), (500, 500), LIMITS["cover_kb"], errors)
    screens = store.get("screens", [])
    if len(screens) > LIMITS["screens"]:
        errors.append(f"{len(screens)} screenshots in store.json (max {LIMITS['screens']})")
    for lang in langs:
        check_image(os.path.join(img, store.get("hero", "hero_1440x720_{lang}.png").format(lang=lang)),
                    (1440, 720), LIMITS["hero_kb"], errors)
        for name in screens:
            check_image(os.path.join(img, name.format(lang=lang)), None, LIMITS["screen_kb"], errors, notes,
                        [(900, 900), (450, 450)])
    return errors, notes


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    errors, notes = check(sys.argv[1])
    for n in notes:
        print("note:", n)
    for e in errors:
        print("ERROR:", e)
    print("listing OK" if not errors else f"{len(errors)} problem(s)")
    sys.exit(1 if errors else 0)
