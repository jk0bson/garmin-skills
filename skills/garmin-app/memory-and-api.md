# Memory and API limits

Each device's `compiler.json` (in the SDK's `Devices` folder) gives its limits under `appTypes[].memoryLimit`. Read it for the devices you ship to; the table only gives examples from SDK 9.2, in KB.

| Type | Recent watches | Exceptions |
|---|---|---|
| Watch face | 128 | 48–96 on old watches |
| Data field | 256 (e.g. FR165/265/965, vívoactive 5, Venu 3) | 128 on e.g. fēnix 8, fēnix 9 Pro, Enduro 3, FR970, Instinct 3 AMOLED; 32 on old watches |
| App | 768 | 512 on FR255 and FR255S |
| Background task | 64 | |
| Glance | 64 | |

## Background and network

- Background events at most every 5 minutes, 30 seconds each; a watch face only while it is active.
- Internet only through the phone (`Communications.makeWebRequest`). A data field cannot use it. Error codes and request rules: [network.md](network.md).
- Some watches give a background task only 32 KB: keep what it holds and returns small, and measure it on those watches (seen in Tesla-Link, not verified here).

## Watch faces

- Garmin data (Body Battery, recovery, sunrise and sunset) comes from `Toybox.Complications` with the `ComplicationSubscriber` permission. The weather location can be empty on a real watch; sunrise/sunset complications are the reliable source (verified on FR165).
- `Activity.getActivityInfo()` is `null` in a watch face almost all the time (no activity running): read all-day data from `ActivityMonitor` and `SensorHistory` (seen on Instinct 3 by another developer, not verified here).
- A watch face cannot read HRV status, training load, training readiness or sleep duration. Training Status (API 4.2) and Sleep Score (API 6.0.2) exist only as complications, and `subscribeToUpdates` returns `false` on a watch that does not publish them. Do not promise the rest (seen on Instinct 3 by another developer, not verified here).
- AMOLED always-on (`onEnterSleep`): at most about 10 % of pixels lit, nothing fixed for more than about 3 minutes; shift a few pixels every minute. `onPartialUpdate` (seconds) exists only on MIP screens. Check with the simulator's File > View Screen Heat Map.

## Activity recording

- The activity name is fixed in `createSession`, before the start: a final score cannot go in the name.
- `FitContributor` adds summary fields, including text (`DATA_TYPE_STRING` with `:count`). How Garmin Connect shows them is **unverified**; check a real activity.

## Does this watch have the API?

`Devices/<id>/<id>.api.debug.xml` (next to `compiler.json`) lists every symbol the device exposes: `grep -c WatchFaceConfig ".../Devices/fr165/fr165.api.debug.xml"`. A name that appears only in documentation text, with no function entry, is not there. Still guard with `has` at run time.

## Settings

| Way | Where the user changes it | Note |
|---|---|---|
| `<watchface-config>` | Garmin's own editor on the watch (styles, complications, data and accent colors) | API 5.1+, not on every watch: guard with `Application has :WatchFaceConfig`, read `WatchFaceConfig.getSettings(null)` |
| `settings.xml` + Properties | the phone (Garmin Connect) | every watch |
| `AppBase.getSettingsView` + `Menu2` | your own menu on the watch | same Properties; watch faces and data fields |

Properties, from the SDK docs, not verified here:
- `Properties.getValue` throws on a key that `properties.xml` does not declare.
- A background task can read Properties but not `setValue` them.
- `type="number"` is 32-bit: use `type="long"` for timestamps.
- User settings go in Properties, internal state in `Application.Storage`.

## No garbage collector

Monkey C counts references: two objects that point at each other (view and app, child and parent) are never freed. Hold the back link as `parent.weak()` and read it with `.get()`, which returns `null` once the parent is gone (SDK docs, not verified here).

## One watch face for old and new watches

From Crystal Face (117 watches) and its fork (seen in Crystal Face, not verified here):
- **Exclude code per memory tier at compile time.** Tag costly code with annotations (`(:hasComplications)` / `(:noComplications)` on two versions of the same function) and drop one per watch with `<device>.excludeAnnotations = ...` in `monkey.jungle`. Small watches get a lighter build instead of an out-of-memory crash.
- **Ship always-on code only to AMOLED watches:** `<device>.sourcePath = $(<device>.sourcePath);always-on-source`.
- **Switch to always-on lazily.** `onEnterSleep` / `onExitSleep` only set a flag and call `requestUpdate`; the next `onUpdate` swaps the layout, drops the normal screen's drawables to free memory and reloads them on the way back.
- **A watch face can start asleep.** On Venu firmware 2.80 `onEnterSleep` was not called at start-up, and the face crashed on a `null` it expected to be set. Never assume a sleep callback ran before the first draw.
- **`onPartialUpdate`:** guard with `WatchFace has :onPartialUpdate`, clip to the seconds' previous box with `setClip`, clear it, draw the new seconds; call `dc.clearClip()` at the top of every full `onUpdate`.
- **A complication value can be `null`** (seen in low-power mode): keep what is on screen and return.
- **`Background.exit(data)` can throw** when the data is too large: wrap it in `try` and send only what the face needs.
- **Check pending web requests in `onExitSleep`** (when the user looks at the watch) instead of on a timer.
