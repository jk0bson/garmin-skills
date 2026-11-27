import os, subprocess, sys
import pytest
from PIL import Image
import bitmap_fonts as bf
from conftest import FONT, ROOT

SCRIPT = os.path.join(ROOT, "skills", "garmin-design", "scripts", "bitmap_fonts.py")


def make_project(tmp_path, product="fr165", size=390):
    """a project with a manifest and a fake SDK Devices folder holding one round device"""
    proj, dev = tmp_path / "proj", tmp_path / "Devices"
    (dev / product).mkdir(parents=True); proj.mkdir()
    (dev / product / "compiler.json").write_text(f'{{"resolution": {{"width": {size}, "height": {size}}}}}')
    (proj / "manifest.xml").write_text(f'<iq:manifest><iq:products><iq:product id="{product}"/></iq:products></iq:manifest>')
    return proj, dev


def run(proj, dev, *extra):
    return subprocess.run([sys.executable, SCRIPT, "--project", str(proj), "--devices", str(dev),
                           "--font", f"big_num:{FONT}:96:0:0123456789:.-",
                           "--font", f"label:{FONT}:19:0.12:ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 /:-.%+", *extra],
                          capture_output=True, text=True)


def test_font_id():
    assert bf.font_id("big") == "BigFont"
    assert bf.font_id("big_num") == "BigNumFont"
    assert bf.font_id("big-num") == "BigNumFont"


@pytest.mark.parametrize("platform, tail", [("darwin", "Library/Application Support/Garmin/ConnectIQ/Devices"),
                                            ("linux", ".Garmin/ConnectIQ/Devices")])
def test_default_devices_dir(monkeypatch, platform, tail):
    monkeypatch.setattr(sys, "platform", platform)
    assert bf.default_devices_dir().replace(os.sep, "/").endswith(tail)


def test_default_devices_dir_windows(monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setenv("APPDATA", "C:/Users/x/AppData/Roaming")
    assert bf.default_devices_dir().replace("\\", "/").endswith("Garmin/ConnectIQ/Devices")


def test_generates_fonts_for_every_size_and_a_fallback(tmp_path):
    proj, dev = make_project(tmp_path)
    r = run(proj, dev)
    assert r.returncode == 0, r.stderr
    for d in ("resources", "resources-round-390x390"):
        assert (proj / d / "fonts" / "big_num.fnt").exists() and (proj / d / "fonts" / "label.png").exists()
    xml = (proj / "resources-round-390x390" / "fonts" / "fonts.xml").read_text()
    assert 'id="BigNumFont"' in xml and 'id="LabelFont"' in xml


def test_coverage_is_in_color_and_alpha(tmp_path):
    """without it the watch draws hard edges: the main trick of the script"""
    proj, dev = make_project(tmp_path)
    run(proj, dev)
    r, g, b, a = Image.open(proj / "resources-round-390x390" / "fonts" / "big_num.png").convert("RGBA").split()
    assert list(r.getdata()) == list(a.getdata()) == list(g.getdata()) == list(b.getdata())
    assert max(a.getdata()) == 255 and len({v for v in a.getdata()}) > 10          # antialiased, not 0/255 only


def test_line_height_is_trimmed_to_the_ink(tmp_path):
    """the line starts at the tallest glyph and ends at the lowest pixel drawn (round digits dip below the baseline)"""
    proj, dev = make_project(tmp_path)
    run(proj, dev)
    fnt = (proj / "resources-round-390x390" / "fonts" / "big_num.fnt").read_text().splitlines()
    common = dict(kv.split("=") for kv in fnt[1].split()[1:])
    glyphs = [dict(kv.split("=") for kv in l.split()[1:]) for l in fnt if l.startswith("char id=")]
    assert min(int(g["yoffset"]) for g in glyphs) == 0
    lowest = max(int(g["yoffset"]) + int(g["height"]) for g in glyphs if int(g["width"]))
    assert int(common["lineHeight"]) == lowest + 1


def test_same_input_same_output(tmp_path):
    a, dev = make_project(tmp_path / "a"); b, _ = make_project(tmp_path / "b")
    run(a, dev); run(b, dev)
    for rel in ("resources/fonts/label.fnt", "resources-round-390x390/fonts/big_num.png"):
        assert (a / rel).read_bytes() == (b / rel).read_bytes()


def test_atlas_warning(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(bf, "ATLAS_MAX_H", 8)
    (tmp_path / "out").mkdir()
    bf.build(str(tmp_path / "out"), "label", FONT, 30, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", 0)
    assert "atlas" in capsys.readouterr().out


def test_strings_clean_and_missing(tmp_path):
    proj, dev = make_project(tmp_path)
    ok, bad = tmp_path / "ok.xml", tmp_path / "bad.xml"
    ok.write_text('<resources><string id="L0">ALLURE</string><string id="Title">Réglages</string></resources>')
    bad.write_text('<resources><string id="L0">ALLURE Œ</string><string id="Title">Réglages</string></resources>')
    assert run(proj, dev, "--strings", str(ok), "--ids", "^L").returncode == 0
    r = run(proj, dev, "--strings", str(bad), "--ids", "^L")
    assert r.returncode == 1 and "Œ" in r.stdout and "L0" in r.stdout
    assert "Title" not in r.stdout                          # --ids skips strings the system font draws
    assert "big_num" not in r.stdout                        # number-only fonts are not checked


def test_unknown_device_is_a_clear_error(tmp_path):
    proj, dev = make_project(tmp_path)
    (proj / "manifest.xml").write_text('<iq:manifest><iq:product id="nodevice"/></iq:manifest>')
    r = run(proj, dev)
    assert r.returncode != 0 and "nodevice" in (r.stderr + r.stdout)


def test_strings_read_only(tmp_path):
    """--strings without --font audits the existing .fnt files and writes nothing"""
    proj, dev = make_project(tmp_path)
    assert run(proj, dev).returncode == 0                    # generate the fonts once
    snap = lambda: {p: p.read_bytes() for p in proj.rglob("*") if p.is_file()}
    before = snap()
    bad = tmp_path / "bad.xml"
    bad.write_text('<resources><string id="LTitle">ABC~</string></resources>')
    ok = tmp_path / "ok.xml"
    ok.write_text('<resources><string id="LTitle">ABC 12</string></resources>')
    cmd = lambda x: subprocess.run([sys.executable, SCRIPT, "--project", str(proj), "--strings", str(x)],
                                   capture_output=True, text=True)
    assert cmd(ok).returncode == 0
    r = cmd(bad)
    assert r.returncode == 1 and "~" in r.stdout
    assert snap() == before
