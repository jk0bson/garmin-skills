---
name: garmin-app
description: Writes and reviews Garmin Connect IQ apps, watch faces and data fields in Monkey C, covering touch and button input, optional Activity.Info fields, data field layouts, sensor edge cases, settings, memory limits and unit tests that compile. Use when writing, fixing or reviewing Monkey C code for a Garmin watch.
---

# Garmin apps in Monkey C

This skill writes and reviews Connect IQ code that survives real watches: touch screens, missing sensors, odd field sizes and old devices. Every rule here was paid for by a real bug.

Screens, fonts and colors belong to `garmin-design`. Driving the simulator belongs to `garmin-simulator`. The store listing belongs to `garmin-store`.

## Never use BehaviorDelegate on touch watches

With a `BehaviorDelegate`, a tap on the screen arrives as `onSelect`, the same as START, and `onTap` is never called even when overridden. Water in the shower or a sleeve paused and started sessions on vívoactive and Venu. Use a `WatchUi.InputDelegate`: `onKey` for `KEY_ENTER` (START), `KEY_ESC` (BACK), `KEY_UP`, `KEY_DOWN`, `KEY_MENU`, and handle or swallow `onTap`, `onSwipe`, `onFlick` and `onHold` yourself ([input.md](input.md)).

## Guard every optional field with `has`

`info.currentPower`, `info.trainingEffect`, `info.startLocation` and newer APIs do not exist on every device. Reading one where it is missing crashes with "Could not find symbol". Write `(info has :currentPower) ? info.currentPower : null`, and `Activity has :getCurrentWorkoutStep` for module functions.

## Treat every sensor value as hostile

Distance can start slightly negative and print `-0.00`. Altitude jumps (GPS, simulator) turn into a 500 % grade. Heart rate arrives as `null`, `0` or `255`. Clamp or reject at the source: distance to `>= 0`, grade outside ±45 % to `null`, heart rate outside 30–240 to `null`. Show `--` for a missing value, never `0` ([data-fields.md](data-fields.md)).

## Every division needs a non-zero denominator

A graph scale built from `max - min` is zero when every bar is equal, as when the runner stands still with the timer on. Give every span a floor before dividing.

## Reset per-activity state in `onTimerReset`

A data field object can outlive one activity. Lap marks, rolling buffers, alert cooldowns and baselines that are not reset carry into the next run: an alert cooldown stored as "last alert at 2000 s" silenced the coach for the whole next activity.

## Lay out a data field from its slot, not the screen

The same field is drawn full screen, in half, in a quarter and in a thin strip. Choose the layout from `dc.getHeight()` and `dc.getWidth()` against `System.getDeviceSettings().screenHeight/Width`, keep clear of the rounded edges with `getObscurityFlags()`, and follow `getBackgroundColor()`, which can be white ([data-fields.md](data-fields.md)).

## Keep pure logic in a module with tests

Put every calculation (zones, pace, predictions, formatting) in a module with no drawing and no sensors, and test it with `(:test)` functions. Keep each test's condition short: one long `a != null && ... && b != null && ...` chain made the compiler loop until `OutOfMemoryError` in `-t` mode. Split it into several small tests ([testing.md](testing.md)).

## Name your string indexes

Labels loaded into an array and read as `_s[4]` drift when the list grows: a heart-rate label read the speed entry and showed "SPEED Z4". Use named constants or one function per label.

## Declare and bump the version yourself

Without `version="x.y.z"` on `iq:application`, the store picks a version on its own. Bump it before every upload: the store refuses a version it has already seen.

## Respect the memory budget

A data field gets 256 KB on FR165/265/965 but 128 KB on fēnix 8 and FR970, and 32 KB on old devices. Bitmap fonts and buffers count. Measure with `System.getSystemStats().usedMemory` in a test copy ([memory-and-api.md](memory-and-api.md)).
