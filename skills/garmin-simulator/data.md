# Data for data fields

## Activity Data window

Simulation > Activity Data opens a window with:

- Data Source: "Data Simulation" (random values, often unrealistic: 1:55 /km pace), "FIT/GPX Playable File", "Workout FIT File".
- Load File: active once a file source is chosen. `Cmd+Shift+G`, paste the path, Enter twice. The window then shows the file's length, e.g. `00:00:00 / 00:04:59` for 5 minutes.
- Data Field Timer Controls: Start, Pause, Lap, Save, Discard, Workout Step.
- A play button and a progress slider. Playback runs in real time.

Order: choose the source, load the file, press Start (timer), then play.

## A realistic run in a FIT file

`scripts/demo_run.py` writes a FIT activity with one record per second: position, altitude, heart rate, cadence, distance, speed and power. The model: standing start, warm-up, about 5:15 /km, a 12 m hill and the descent, a final push; heart rate follows effort with about 30 s of lag; GPS noise.

```sh
python3 demo_run.py run.fit 300     # 5 minutes
python3 demo_run.py short.fit 60    # quick 1-minute check
python3 demo_run.py ride.fit 600 --sport cycling      # a ride: 7 to 11 m/s, power, rpm
python3 demo_run.py brussels.fit 300 --lat 50.85 --lon 4.35 --seed 3
```

Cycling power is air drag (v cubed) plus rolling resistance plus slope, for an 80 kg rider and bike, and falls to 0 W while coasting downhill; a short surge near 400 W where the speed carried into the climb is a model artifact. The sport message is 2 and cadence is written in rpm as is; running cadence is strides per minute (steps ÷ 2). The same `--seed` gives the same file apart from its start time. Running output is byte-for-byte what it was before these options, checked with the clock frozen.

It is synthetic, not a recorded run. A real run exported from Garmin Connect ("Export Original") replays the same way.

## Known differences

- The simulator recomputed distance from the GPS points: 1.01 km on screen for 946 m in the file.
- Cadence in FIT is strides per minute (steps ÷ 2).
- The watch's own HR zones apply (see Set User Profile), not the file's.
