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
- Internet only through the phone (`Communications.makeWebRequest`). A data field cannot use it.

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
