import json, os, re
import pytest
from conftest import ROOT

SKILLS = os.path.join(ROOT, "skills")
NAMES = ["garmin-app", "garmin-design", "garmin-simulator", "garmin-store"]       # installs depend on these names


@pytest.mark.parametrize("name", NAMES)
def test_skill_is_short_and_named(name):
    text = open(os.path.join(SKILLS, name, "SKILL.md"), encoding="utf-8").read()
    assert len(text.splitlines()) < 100
    meta = re.match(r"---\nname: (.+)\ndescription: (.+)\n---\n", text)
    assert meta and meta[1] == name and meta[2].strip()


def test_markdown_links_resolve():
    broken = []
    for d, _, files in os.walk(SKILLS):
        for f in files:
            if not f.endswith(".md"): continue
            path = os.path.join(d, f)
            for target in re.findall(r"\]\(([^)]+)\)", open(path, encoding="utf-8").read()):
                t = target.split("#")[0]
                if t and not re.match(r"(https?:|mailto:)", t) and not os.path.exists(os.path.join(d, t)):
                    broken.append(f"{os.path.relpath(path, ROOT)} -> {target}")
    assert not broken


def test_plugin_files():
    plugin = json.load(open(os.path.join(ROOT, ".claude-plugin", "plugin.json")))
    market = json.load(open(os.path.join(ROOT, ".claude-plugin", "marketplace.json")))
    assert plugin["name"] == "garmin" and re.fullmatch(r"\d+\.\d+\.\d+", plugin["version"])
    assert market["plugins"][0]["name"] == "garmin"
