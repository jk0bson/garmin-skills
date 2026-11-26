import hashlib, struct, subprocess, sys, os
import pytest
import demo_run
from conftest import ROOT

SCRIPT = os.path.join(ROOT, "skills", "garmin-simulator", "scripts", "demo_run.py")
# sha256 of the files the script wrote before the argparse/cycling change, with the clock at 1800000000
GOLDEN = {300: "462c5081e292dbf937457f900211159ebfb30cf4d0448c5016a059a960c60e61"}


def write_frozen(monkeypatch, path, secs, **kw):
    monkeypatch.setattr(demo_run.time, "time", lambda: 1800000000.0)
    demo_run.write(str(path), secs, **kw)
    return path.read_bytes()


def decode(data):
    """(sport, [record dicts]) of a FIT file made by demo_run"""
    p, end, defs, sport, recs = data[0], len(data) - 2, {}, None, []
    while p < end:
        h = data[p]; p += 1; lm = h & 0x0F
        if h & 0x40:
            n = data[p + 4]
            defs[lm] = (struct.unpack_from("<H", data, p + 2)[0], [(data[p + 5 + 3 * i], data[p + 6 + 3 * i]) for i in range(n)])
            p += 5 + 3 * n
        else:
            g, flds = defs[lm]; vals = {}
            for num, size in flds:
                vals[num] = int.from_bytes(data[p:p + size], "little", signed=(g == 20 and num in (0, 1))); p += size
            if g == 12: sport = vals[0]
            if g == 20: recs.append(vals)
    return sport, recs


def test_crc():
    assert demo_run.crc16(b"123456789") == 0xBB3D


def test_fit_header_and_crc(monkeypatch, tmp_path):
    data = write_frozen(monkeypatch, tmp_path / "a.fit", 60)
    assert data[8:12] == b".FIT" and struct.unpack_from("<I", data, 4)[0] == len(data) - 16
    assert struct.unpack("<H", data[-2:])[0] == demo_run.crc16(data[:-2])


def test_running_is_unchanged_byte_for_byte(monkeypatch, tmp_path):
    data = write_frozen(monkeypatch, tmp_path / "a.fit", 300)
    assert len(data) == 7621
    assert hashlib.sha256(data).hexdigest() == GOLDEN[300]


def test_running_cadence_is_strides_per_minute(monkeypatch, tmp_path):
    sport, recs = decode(write_frozen(monkeypatch, tmp_path / "a.fit", 300))
    assert sport == 1 and 70 < max(r[4] for r in recs) < 100          # steps / 2


def test_cycling_sport_cadence_and_power(monkeypatch, tmp_path):
    sport, recs = decode(write_frozen(monkeypatch, tmp_path / "b.fit", 600, sport="cycling"))
    pedaling = [r[4] for r in recs if r[4]]
    assert sport == 2
    assert 70 < sum(pedaling) / len(pedaling) < 100                    # rpm as is, not halved
    assert max(r[7] for r in recs) > 100 and min(r[7] for r in recs) == 0   # coasting downhill gives 0 W
    assert all(r[4] == 0 for r in recs if r[7] == 0)                  # no pedaling without power
    assert 5 < max(r[6] for r in recs) / 1000 < 14                     # m/s


def test_cycling_power_follows_physics():
    pts = demo_run.simulate(600, sport="cycling")
    flat = [p for p in pts if 150 < p[0] < 200]
    climb = [p for p in pts if 300 < p[0] < 340]
    assert sum(p[8] for p in climb) / len(climb) > sum(p[8] for p in flat) / len(flat) * 0.9   # slope costs watts even slower
    assert max(p[7] for p in pts) > max(p[7] for p in flat)


def test_seed_and_position(monkeypatch, tmp_path):
    a = write_frozen(monkeypatch, tmp_path / "a.fit", 100)
    assert a == write_frozen(monkeypatch, tmp_path / "b.fit", 100)
    assert a != write_frozen(monkeypatch, tmp_path / "c.fit", 100, seed=3)
    _, recs = decode(write_frozen(monkeypatch, tmp_path / "d.fit", 100, lat0=50.85, lon0=4.35))
    assert abs(recs[0][0] / 2**31 * 180 - 50.85) < 0.001 and abs(recs[0][1] / 2**31 * 180 - 4.35) < 0.001


def test_command_line(tmp_path):
    out = tmp_path / "x.fit"
    r = subprocess.run([sys.executable, SCRIPT, str(out), "60", "--sport", "cycling"], capture_output=True, text=True)
    assert r.returncode == 0 and out.exists()
    r = subprocess.run([sys.executable, SCRIPT, str(out), "10"], capture_output=True, text=True)
    assert r.returncode == 2 and "at least 30" in r.stderr
