import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ("garmin-design", "garmin-simulator", "garmin-store"):
    sys.path.insert(0, os.path.join(ROOT, "skills", p, "scripts"))
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "Amarna-Medium.ttf")   # SIL OFL 1.1, see fonts/OFL.txt
