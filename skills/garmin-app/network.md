# Web requests

`Communications.makeWebRequest` goes through the phone. Everything below is from Tesla-Link, a connected app on 80+ watches, except the codes, read in the SDK 9.2 docs.

## Error codes (SDK 9.2)

| Code | Name | What to do |
|---|---|---|
| -104 | `BLE_CONNECTION_UNAVAILABLE` | phone not connected: check `System.getDeviceSettings().phoneConnected` and say so |
| -101 | `BLE_QUEUE_FULL` | retry later, no message |
| -5 | `BLE_REQUEST_CANCELLED` | no message |
| -300 | `NETWORK_REQUEST_TIMED_OUT` | retry later |
| -400 | `INVALID_HTTP_BODY_IN_NETWORK_RESPONSE` | see 429 below |
| -402 | `NETWORK_RESPONSE_TOO_LARGE` | ask the server for less |
| -403 | `NETWORK_RESPONSE_OUT_OF_MEMORY` | see text responses below |

Other guides list other numbers for these names: trust the SDK's `Communications` page, not memory.

## Rules (seen in Tesla-Link, not verified here)

- **Ask for text, not JSON, when memory is tight.** A JSON response becomes a `Dictionary` that costs far more than the string; switching to `HTTP_RESPONSE_CONTENT_TYPE_TEXT_PLAIN` ended the -403 errors in a background task.
- **A 429 can arrive as -400.** Treat both as "too many requests" and wait (10 s there) before the next one.
- **Stay silent on -101 and -5.** They are not worth an error screen.
- **One request at a time.** Put user actions in a list; a `Timer` sends the next one only after the previous response came back, and a counter delays it after an error.
- **Check every field before reading it.** The server's data changed with the car's model and year; most crashes came from a missing field.
- **Share state through `Application.Storage`** (a token, the last data) between the background task, the app and the glance, not only through `Background.exit`. Stop the background task from fetching while the main app is open.
