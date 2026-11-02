# Data fields

## compute and onUpdate

- `compute(info)` runs about once a second, also while the timer is stopped. Read sensors there, keep smoothing buffers there.
- `onUpdate(dc)` draws. It can run more often than `compute` and once per slot when the user puts the field in several slots.
- `info.timerState == Activity.TIMER_STATE_ON` before adding to anything that should only count while running (graphs, baselines).
- `onTimerLap()` and `onTimerReset()` for laps and new activities. Reset every per-activity variable in `onTimerReset`.

## Picking the layout

```monkeyc
var ds = System.getDeviceSettings();
if (h >= ds.screenHeight * 8 / 10)       { drawFull(dc); }   // 1-field page
else if (h < ds.screenHeight * 22 / 100) { drawStrip(dc); }  // 5-6 field pages
else if (w >= ds.screenWidth * 8 / 10)   { drawWide(dc); }   // half screen
else                                      { drawSmall(dc); }  // quarter
```

The simulator's Data Fields > Layout menu offers 1, 2, 3 A, 3 B and 4 fields. It has no strip layout: test the strip in code.

## Margins on round screens

`getObscurityFlags()` says which edges of the slot touch the round bezel. A slot touching the top or bottom edge is narrow at that edge: use about 19 % side margins there, 13 % elsewhere, and about 20 % top or bottom margin on an obscured edge.

## Background

`getBackgroundColor()` is black or white depending on the user's settings. Draw on it, with darker accent colors on white. Do not hardcode black.

## Optional data

| Data | Guard | Note |
|---|---|---|
| Power | `info has :currentPower` | missing on many watches |
| Training Effect | `info has :trainingEffect` | |
| Start location | `info has :startLocation` | null indoors |
| Workout step | `Activity has :getCurrentWorkoutStep` | API 3.2 |
| Alerts | `WatchUi.DataField has :showAlert` | `WatchUi.DataFieldAlert` view |
| HR zones | `UserProfile.getHeartRateZones(UserProfile.getCurrentSport())` | needs `UserProfile` permission, 6 bounds |

## Workout heart-rate targets

`Activity.getCurrentWorkoutStep().step` is a `WorkoutStep` or a `WorkoutIntervalStep` (use `.activeStep`). With `targetType == WORKOUT_STEP_TARGET_HEART_RATE`, `targetValueLow/High` hold the target. The SDK docs do not state the unit. FIT files encode values above 100 as bpm + 100 and values up to 100 as % of max heart rate; assuming the same here is **unverified on a watch**.

## Values that are not there

Steps, fat or carbohydrate burned and the next alarm time are not available to a data field. Do not promise them.

## Derived metrics that held up

- Grade over 15 s of rolling altitude and distance, `null` under 15 m travelled or beyond ±45 %.
- Grade-adjusted pace: speed × C(i) / C(0), with Minetti 2002 running cost `C(i) = 155.4i⁵ − 30.4i⁴ − 43.3i³ + 46.3i² + 19.5i + 3.6`, grade clamped to ±30 %.
- Cardiac drift: efficiency = speed / heart rate; baseline averaged from minute 3 to 13, current as a ~5 min moving average, drift = (base − now) / base. Only while running faster than 1.5 m/s.
- Heart-rate ring: give each zone the same arc length and map heart rate piecewise inside its zone. A linear map over unequal zones puts the marker in the next zone's arc before the zone changes.
