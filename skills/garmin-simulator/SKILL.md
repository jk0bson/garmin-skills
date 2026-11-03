---
name: garmin-simulator
description: Drives the Connect IQ simulator on macOS to test and capture Garmin apps, watch faces and data fields, covering launching, menus, buttons, data field layouts, heart-rate zones, FIT playback of a realistic run, screenshots, multi-device audits and store captures. Use when running, testing or screenshotting a Connect IQ project in the simulator.
---

# Connect IQ simulator

This skill runs a Connect IQ project in the simulator, puts it in the state you want, checks it on every screen size and captures it. The simulator lies in small ways; each rule here works around one of them.

Screen rules belong to `garmin-design`. Composing store images belongs to `garmin-store`.

## Check the screen after every action

A key press, a menu click or a launch is sometimes lost. After each step, capture and look before the next one. A test that never looked at the screen tested nothing.

## Keep the simulator in front before typing

Keystrokes go to whatever app is in front. Typed text once landed in the code editor instead of a file dialog. Set the simulator frontmost and check it is still frontmost before every `keystroke` ([driving.md](driving.md)).

## Keep the display awake

`screencapture` fails with "could not create image from rect" when the display sleeps. Run `caffeinate -d -u -t <seconds> &` for the length of the capture session.

## Give data fields real data

Without data, a data field shows `--`. Use Simulation > Activity Data: "Data Simulation" for random values, or "FIT/GPX Playable File" with Load File to replay a realistic run ([data.md](data.md)). `scripts/demo_run.py` writes such a FIT file.

## Fix the simulator's heart-rate zones

The simulator's default Running zones were 128–255 bpm, so 152 bpm showed as zone 1. Set realistic zones in Settings > Set User Profile before judging zone colors.

## Clear stored settings between runs

App settings and storage persist across launches and devices. A capture showed an old setting instead of the new default. Use File > Reset All App Data before testing defaults.

## Test one device per screen size

Run an audit copy on the nine round sizes (218 to 466 px) with every data choice and extreme values, and read both the log and the screenshots ([captures.md](captures.md)).

## Capture demo states from a copy

Marketing states (minute 58, a hill, an alert) come from a temporary copy that forces values in `onUpdate`. Generate the copy with a script so the real code never changes.

## Restart when it hangs

If a launch never switches the window to the new device, or a capture or log comes back empty, quit the simulator (`pkill -x simulator`) and start again.
