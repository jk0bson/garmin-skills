import json, os, random
import pytest
from PIL import Image
import check_listing as cl


def png(path, size, noise=False):
    im = Image.new("RGB", size, (20, 24, 28))
    if noise:                                   # incompressible: a heavy file
        rnd = random.Random(1)
        im.putdata([(rnd.randrange(256), rnd.randrange(256), rnd.randrange(256)) for _ in range(size[0] * size[1])])
    im.save(path)


@pytest.fixture
def store(tmp_path):
    (tmp_path / "images").mkdir()
    json.dump({"titres": {"en": "zonely: Run in the right zone", "fr": "zonely : Courez dans la bonne zone"},
               "langues": ["en", "fr"], "cover": "cover_500x500.png", "hero": "hero_1440x720_{lang}.png",
               "screens": ["{lang}_1.png", "{lang}_2.png"]}, open(tmp_path / "store.json", "w"))
    for lang in ("en", "fr"):
        (tmp_path / f"description_{lang}.txt").write_text("A data field.\nOpen the Run settings, then Data Screens.")
        png(tmp_path / "images" / f"hero_1440x720_{lang}.png", (1440, 720))
        for i in (1, 2):
            png(tmp_path / "images" / f"{lang}_{i}.png", (900, 900))
    png(tmp_path / "images" / "cover_500x500.png", (500, 500))
    (tmp_path / "whats_new.txt").write_text("EN:\nBetter zones.\n\nFR:\nMeilleures zones.\n")
    return tmp_path


def test_clean_listing(store):
    assert cl.check(str(store)) == ([], [])


def test_title_and_description_limits(store):
    s = json.load(open(store / "store.json")); s["titres"]["en"] = "x" * 51
    json.dump(s, open(store / "store.json", "w"))
    (store / "description_fr.txt").write_text("y" * 4001)
    errors, _ = cl.check(str(store))
    assert any("title en: 51" in e for e in errors) and any("description fr: 4001" in e for e in errors)


@pytest.mark.parametrize("ch", ["<", ">"])
def test_angle_brackets_refused(store, ch):
    (store / "description_en.txt").write_text(f"Settings {ch} Data Screens")
    assert any("refuses" in e for e in cl.check(str(store))[0])
    (store / "description_en.txt").write_text("fine")
    (store / "whats_new.txt").write_text(f"EN:\na {ch} b\n\nFR:\nok\n")
    assert any("whats_new" in e and "refuses" in e for e in cl.check(str(store))[0])


def test_images(store):
    png(store / "images" / "cover_500x500.png", (900, 900))
    os.remove(store / "images" / "hero_1440x720_fr.png")
    png(store / "images" / "en_1.png", (900, 900), noise=True)
    errors, _ = cl.check(str(store))
    assert any("cover" in e and "900x900" in e for e in errors)
    assert any("hero_1440x720_fr" in e and "missing" in e for e in errors)
    assert any("en_1.png" in e and "KB" in e for e in errors)


def test_too_many_screens_and_odd_size_is_a_note(store):
    s = json.load(open(store / "store.json")); s["screens"] = [f"{{lang}}_{i}.png" for i in range(1, 7)]
    json.dump(s, open(store / "store.json", "w"))
    for lang in ("en", "fr"):
        for i in range(1, 7):
            png(store / "images" / f"{lang}_{i}.png", (800, 800) if i == 3 else (900, 900))
    errors, notes = cl.check(str(store))
    assert any("6 screenshots" in e for e in errors)
    assert any("en_3.png" in n and "800x800" in n for n in notes) and not any("en_3.png" in e for e in errors)


def test_missing_parts(store):
    os.remove(store / "description_fr.txt")
    (store / "whats_new.txt").write_text("EN:\nonly english\n")
    errors, _ = cl.check(str(store))
    assert any("description_fr.txt missing" in e for e in errors) and any("part FR" in e for e in errors)
    assert cl.check(str(store / "nowhere"))[0] == [f"store.json missing in {store / 'nowhere'}"]


def test_seven_languages_and_unknown_code(store):
    langs = ["en", "de", "fr", "es", "it", "nl", "pl"]
    s = json.load(open(store / "store.json")); s["langues"] = langs + ["eng"]
    s["titres"] = {l: f"title {l}" for l in langs + ["eng"]}
    json.dump(s, open(store / "store.json", "w"))
    (store / "whats_new.txt").write_text("".join(f"{l.upper()}:\nnew\n\n" for l in langs + ["eng"]))
    for l in langs + ["eng"]:
        (store / f"description_{l}.txt").write_text("ok")
        png(store / "images" / f"hero_1440x720_{l}.png", (1440, 720))
    errors, _ = cl.check(str(store))
    assert errors == [f"language eng: not a code of the store form ({' '.join(cl.PORTAL_LANGS)})"]   # the 7 portal codes pass, eng is the manifest's code
