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
- On-watch settings: `AppBase.getSettingsView` with `Menu2`, for watch faces and data fields.
- AMOLED always-on (`onEnterSleep`): at most about 10 % of pixels lit, nothing fixed for more than about 3 minutes; shift a few pixels every minute. `onPartialUpdate` (seconds) exists only on MIP screens. Check with the simulator's File > View Screen Heat Map.

## Activity recording

- The activity name is fixed in `createSession`, before the start: a final score cannot go in the name.
- `FitContributor` adds summary fields, including text (`DATA_TYPE_STRING` with `:count`). How Garmin Connect shows them is **unverified**; check a real activity.
