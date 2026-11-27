import json, os, re
import pytest
from PIL import Image, ImageDraw
from conftest import ROOT, FONT
import check_listing as cl
import store_assets as sa


def capture(path, size=390, ring=(40, 200, 120)):
    """a fake round watch screen: smooth gradient, a vivid ring at the edge, a few marks"""
    im = Image.new("RGB", (size, size))
    im.putdata([(x * 255 // size, y * 255 // size, 90) for y in range(size) for x in range(size)])
    d = ImageDraw.Draw(im)
    d.ellipse([4, 4, size - 5, size - 5], outline=ring, width=8)
    d.rectangle([size // 3, size // 3, size * 2 // 3, size // 2], fill=(250, 250, 250))
    im.save(path)


@pytest.fixture
def caps(tmp_path):
    d = tmp_path / "caps"
    (d / "en").mkdir(parents=True)
    for n, ring in zip("abcd", ((40, 200, 120), (250, 130, 30), (240, 60, 60), (80, 150, 255))):   # different, or the GIF merges frames
        capture(d / "en" / f"{n}.png", ring=ring)
    return d


def run(caps, tmp_path, preset, *extra):
    out = tmp_path / "images"
    args = ["--preset", preset, "--name", "demo", "--captures", str(caps), "--out", str(out), "--font", FONT,
            "--screen", "a|KICKER|Headline here|A short line under it", "--screen", "a,b|TWO|Two watches|Side by side|#3D8BFF",
            "--screen", "a,b,c|THREE|Three watches|Left, middle, right", "--screen", "d|FOUR|Last one|Done",
            "--hero", "a,b,c", "--hero-lines", "First line|Second line", "--hero-sub", "Small one|Small two",
            "--gif", "a,b,c,d", "--gif-text", "LIVE|Moving|Frames", *extra]
    sa.main(args)
    return out


@pytest.mark.parametrize("preset", ["watchface", "app", "datafield"])
def test_images_pass_check_listing(preset, caps, tmp_path, capsys):
    out = run(caps, tmp_path, preset, "--accent", "#FF7A1A,#3D8BFF")
    line = [l for l in capsys.readouterr().out.splitlines() if l.startswith('"screens"')][0]
    screens = json.loads("{" + line + "}")["screens"]
    assert screens[0] == "{lang}_0_anim.gif" and len(screens) == 5
    store = tmp_path / "store"
    store.mkdir()
    os.rename(out, store / "images")
    json.dump({"titres": {"en": "demo: a test"}, "langues": ["en"], "screens": screens}, open(store / "store.json", "w"))
    (store / "description_en.txt").write_text("A demo.")
    assert cl.check(str(store)) == ([], [])
    with Image.open(store / "images" / "en_0_anim.gif") as g:
        assert g.n_frames == 4 and g.size[0] <= 450


def test_language_in_names_and_per_language_captures(caps, tmp_path):
    out = run(caps, tmp_path, "app", "--lang", "en")
    assert sorted(os.listdir(out)) == ["cover_500x500.png", "en_0_anim.gif", "en_1_a.png", "en_2_a.png", "en_3_a.png", "en_4_d.png", "hero_1440x720_en.png"]


def test_flat_background_follows_the_screen_colour(caps, tmp_path):
    out = run(caps, tmp_path, "watchface", "--bg", "#EDEDE6")
    with Image.open(out / "en_2_a.png") as im:       # screenshot 2 asked for #3D8BFF
        assert im.convert("RGB").getpixel((5, 5)) == (0x3D, 0x8B, 0xFF)
    with Image.open(out / "en_1_a.png") as im:
        assert im.convert("RGB").getpixel((5, 5)) == (0xED, 0xED, 0xE6)


def test_thin_accent_survives_the_palette():
    """a 3 px vivid line on a big gradient: the mixed palette keeps it saturated"""
    im = Image.new("RGB", (400, 400))
    im.putdata([(30 + x // 3, 25 + y // 4, 40 + (x + y) // 8) for y in range(400) for x in range(400)])
    ImageDraw.Draw(im).rectangle([100, 200, 300, 202], fill=(91, 201, 79))
    q = im.quantize(palette=sa.mixed_palette(im, 64), dither=Image.Dither.NONE).convert("RGB")
    r, g, b = q.getpixel((200, 201))
    assert g > 150 and r < 140 and b < 140


def test_save_png_squeezes_under_the_limit(tmp_path):
    im = Image.new("RGB", (900, 900))
    im.putdata([((x * y) % 251, (x + 2 * y) % 253, (x ^ y) % 255) for y in range(900) for x in range(900)])
    p = tmp_path / "heavy.png"
    sa.save_png(im, str(p), 145)
    assert os.path.getsize(p) <= 145 * 1024
    with pytest.raises(SystemExit):
        sa.save_png(im, str(p), 1)


def test_fit_shrinks_then_gives_up():
    make = lambda s: sa.load_font(FONT, s)
    assert sa.fit("Short", make, 60, 800).size == 60
    f = sa.fit("A rather long headline for the width", make, 60, 400)
    assert f.size < 60 and f.getlength("A rather long headline for the width") <= 400
    with pytest.raises(SystemExit):
        sa.fit("x" * 200, make, 60, 100)


def test_hexcolor_and_slug():
    assert sa.hexcolor("#5BC94F") == (0x5B, 0xC9, 0x4F) and sa.hexcolor("ff0000") == (255, 0, 0)
    with pytest.raises(SystemExit):
        sa.hexcolor("green")
    assert sa.slug("Main Screen!") == "main_screen"


def test_bad_inputs_stop_with_a_message(caps, tmp_path):
    Image.new("RGB", (390, 300)).save(caps / "en" / "flat.png")
    with pytest.raises(SystemExit, match="square"):
        sa.main(["--preset", "app", "--name", "x", "--captures", str(caps), "--out", str(tmp_path / "o"), "--font", FONT, "--screen", "flat|K|H|S"])
    with pytest.raises(SystemExit, match="not found"):
        sa.main(["--preset", "app", "--name", "x", "--captures", str(caps), "--out", str(tmp_path / "o"), "--font", FONT, "--screen", "nope|K|H|S"])
    with pytest.raises(SystemExit, match="CAPTURES"):
        sa.main(["--preset", "app", "--name", "x", "--captures", str(caps), "--out", str(tmp_path / "o"), "--screen", "a|only|three"])
    with pytest.raises(SystemExit, match="at most 3"):
        sa.main(["--preset", "app", "--name", "x", "--captures", str(caps), "--out", str(tmp_path / "o"), "--font", FONT, "--screen", "a,b,c,d|K|H|S"])


def test_public_files_name_no_private_app_or_script():
    """the public repo says nothing about the author's own apps or tools"""
    private = re.compile("sauna|zonely|aestify|ephemera|retro" + "form|racket|a_envoyer|[.]/garmin |commun/|store_kit", re.I)
    for rel in ("skills/garmin-store/scripts/store_assets.py", "skills/garmin-release/SKILL.md"):
        text = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        assert not private.findall(text), rel
