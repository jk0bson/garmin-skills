#!/usr/bin/env python3
"""Write a realistic run or ride as a FIT activity (one record per second) to replay in the Connect IQ simulator:
Simulation > Activity Data > Data Source "FIT/GPX Playable File" > Load File, then Start and play.

Running (default): standing start, warm-up, about 5:15 /km, a 12 m hill and the descent, a final push.
Cycling: 7 to 11 m/s on a loop three times larger, a 4 % climb and descent; power is the sum of air drag (v cubed),
rolling resistance and slope, and drops to 0 while coasting downhill.
Heart rate follows effort with about 30 s of lag, GPS noise, cadence and power follow speed.
The route is an ellipse starting in Central Park, New York; move it with --lat and --lon.
Cadence in the file: strides per minute for running (steps / 2), rpm for cycling.

Usage: python3 demo_run.py [out.fit] [seconds] [--sport running|cycling] [--lat DEG] [--lon DEG] [--seed N]
No dependencies. The same seed gives the same route and values.
"""
import argparse, math, random, struct, time

FIT_EPOCH = 631065600          # 1989-12-31 00:00 UTC
LAT0, LON0 = 40.7812, -73.9665


def crc16(data, crc=0):
    t = [0x0000, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00, 0x2800, 0xE401,
         0xA001, 0x6C00, 0x7800, 0xB401, 0x5000, 0x9C01, 0x8801, 0x4400]
    for b in data:
        for nib in (b & 0xF, b >> 4):
            tmp = t[crc & 0xF]; crc = (crc >> 4) & 0x0FFF; crc ^= tmp ^ t[nib]
    return crc


class Fit:
    BASE = {"B": 0x02, "H": 0x84, "I": 0x86, "i": 0x85}

    def __init__(self):
        self.body = b""
        self.fmts = {}

    def define(self, local, glob, fields):   # fields: [(field number, struct format)]
        self.body += struct.pack("<BBBHB", 0x40 | local, 0, 0, glob, len(fields))
        for num, fmt in fields:
            self.body += struct.pack("<BBB", num, struct.calcsize(fmt), self.BASE[fmt])
        self.fmts[local] = "<" + "".join(f for _, f in fields)

    def data(self, local, *values):
        self.body += struct.pack("<B", local) + struct.pack(self.fmts[local], *values)

    def bytes(self):
        head = struct.pack("<BBHI4s", 14, 0x10, 2132, len(self.body), b".FIT")
        head += struct.pack("<H", crc16(head))
        out = head + self.body
        return out + struct.pack("<H", crc16(out))


def simulate(secs, seed=7, lat0=LAT0, lon0=LON0, sport="running"):
    random.seed(seed)
    bike = sport == "cycling"
    a, b = (1230.0, 690.0) if bike else (420.0, 230.0)    # loop half-axes (m)
    hr, v, dist, alt, noise, power = 92.0, 0.0, 0.0, 98.0, 0.0, 0
    out = []
    for t in range(secs):
        f = t / secs
        # wanted speed (m/s): start, cruise, hill, descent, final push
        if bike:
            if t < 4: want = 0.0
            elif t < 25: want = 6.5
            elif f < 0.40: want = 8.3
            elif f < 0.58: want = 5.0
            elif f < 0.72: want = 11.0
            elif f < 0.86: want = 8.8
            else: want = 9.8
        else:
            if t < 4: want = 0.0
            elif t < 25: want = 2.9
            elif f < 0.40: want = 3.17
            elif f < 0.58: want = 2.88
            elif f < 0.72: want = 3.35
            elif f < 0.86: want = 3.2
            else: want = 3.62
        v += (want - v) * (0.25 if want > v else 0.12)
        noise = noise * 0.85 + random.gauss(0, 0.05)
        speed = max(0.0, v + noise) if v > 0.5 else v
        if bike:
            grade = 0.04 if 0.40 <= f < 0.58 else (-0.04 if 0.58 <= f < 0.72 else math.sin(t / 23) * 0.004)
        else:
            grade = 0.07 if 0.40 <= f < 0.58 else (-0.06 if 0.58 <= f < 0.72 else math.sin(t / 23) * 0.006)
        alt += speed * grade
        dist += speed
        # heart rate: target from effort, ~30 s response, slight drift
        if bike:
            target = 90 + 0.30 * power + 6 * f if speed > 0.5 else 92     # power of the previous second: the lag is real
        else:
            target = 88 + 21 * speed + 160 * max(grade, -0.03) + 6 * f if speed > 0.5 else 92
        hr += (target - hr) / 28 + random.gauss(0, 0.6)
        if bike:
            # air drag 0.5*rho*CdA*v^3 + rolling Crr*m*g*v + slope m*g*v*grade, 80 kg rider and bike, 97.5 % drivetrain
            watts = (0.5 * 1.2 * 0.32 * speed ** 3 + 80 * 9.81 * speed * (0.005 + grade)) / 0.975
            cad_noise = random.gauss(0, 2) if speed > 0.8 else 0
            pow_noise = random.gauss(0, 6) if speed > 0.8 else 0
            power = max(0, round(watts + pow_noise)) if speed > 0.8 else 0
            cad = round(70 + 2.0 * speed + cad_noise) if power > 0 else 0     # no pedaling while coasting
        else:
            cad = round(150 + 7 * speed + random.gauss(0, 1.2)) if speed > 0.8 else 0
            power = round(70 * speed * 1.04 + 70 * 9.81 * speed * grade + random.gauss(0, 6)) if speed > 0.8 else 0
        ang = dist / (math.pi * (a + b)) * math.pi
        north, east = b * math.sin(ang), a * (1 - math.cos(ang))
        jit = random.gauss(0, 1.5)
        lat = lat0 + (north + jit) / 111320
        lon = lon0 + (east + jit) / (111320 * math.cos(math.radians(lat0)))
        out.append((t, lat, lon, alt, round(hr), cad, dist, speed, max(0, power)))
    return out


def semi(deg):
    return round(deg * 2 ** 31 / 180)


def write(path, secs, seed=7, lat0=LAT0, lon0=LON0, sport="running"):
    start = int(time.time()) - secs - FIT_EPOCH
    w = Fit()
    w.define(0, 0, [(0, "B"), (1, "H"), (2, "H"), (4, "I")])           # file_id: activity, Garmin
    w.data(0, 4, 1, 4315, start)
    w.define(1, 12, [(0, "B"), (1, "B")])                              # sport: 1 running, 2 cycling; sub-sport generic
    w.data(1, 2 if sport == "cycling" else 1, 0)
    w.define(2, 21, [(253, "I"), (0, "B"), (1, "B")])                  # event: timer
    w.data(2, start, 0, 0)
    w.define(3, 20, [(253, "I"), (0, "i"), (1, "i"), (2, "H"), (3, "B"), (4, "B"), (5, "I"), (6, "H"), (7, "H")])
    for t, lat, lon, alt, hr, cad, dist, speed, power in simulate(secs, seed, lat0, lon0, sport):
        # FIT running cadence is strides per minute (steps / 2); cycling cadence is rpm as is
        fit_cad = cad if sport == "cycling" else cad // 2
        w.data(3, start + t, semi(lat), semi(lon), round((alt + 500) * 5), hr, fit_cad,
               round(dist * 100), round(speed * 1000), power)
    w.data(2, start + secs, 0, 4)
    with open(path, "wb") as f:
        f.write(w.bytes())


if __name__ == "__main__":
    assert crc16(b"123456789") == 0xBB3D                                # CRC-16/ARC check value
    pts = simulate(300)
    assert 900 < pts[-1][6] < 1000 and 150 < max(p[4] for p in pts) < 175
    bike = simulate(300, sport="cycling")
    assert 2000 < bike[-1][6] < 2800 and max(p[8] for p in bike) > 100 and min(p[8] for p in bike) == 0
    ap = argparse.ArgumentParser(description="Write a FIT activity to replay in the Connect IQ simulator.")
    ap.add_argument("out", nargs="?", default="demo_run.fit")
    ap.add_argument("seconds", nargs="?", type=int, default=300)
    ap.add_argument("--sport", choices=["running", "cycling"], default="running")
    ap.add_argument("--lat", type=float, default=LAT0, help="start latitude (default: Central Park, New York)")
    ap.add_argument("--lon", type=float, default=LON0, help="start longitude")
    ap.add_argument("--seed", type=int, default=7, help="random seed: same seed, same file")
    args = ap.parse_args()
    if args.seconds < 30:
        ap.error("seconds must be at least 30")
    write(args.out, args.seconds, args.seed, args.lat, args.lon, args.sport)
    print(args.out, args.seconds, "s,", args.sport)
