# Driving the simulator on macOS

```sh
SDK="$HOME/Library/Application Support/Garmin/ConnectIQ/Sdks/<sdk>/bin"
open "$SDK/ConnectIQ.app"; sleep 8
"$SDK/monkeydo" app.prg fr165 > run.log 2>&1 &      # wait ~14 s; the window title shows the device
```

The process is called `simulator` for System Events.

## Menus

```sh
osascript -e 'tell application "System Events" to tell process "simulator"' \
  -e 'set frontmost to true' \
  -e 'click menu item "1 Field" of menu 1 of menu item "Layout" of menu 1 of menu bar item "Data Fields" of menu bar 1' \
  -e 'end tell'
```

- Data Fields > Layout (1 Field, 2 Fields, 3 Fields A, 3 Fields B, 4 Fields) and Background Color (White, Black) only exist while a data field runs.
- Settings > Language works only once an app runs: launch, change the language, relaunch. For English captures, compile a copy without the other languages instead.
- Settings > Set User Profile opens an editor; its table cells (heart-rate zones) need real mouse double-clicks, see below.
- File > Save Screen Capture saves the exact screen. Type the name without extension; `Cmd+Shift+G` to change folder. If the file exists, a "Replace?" box blocks everything.

## Buttons

`key code 36` START, `53` BACK, `126` UP, `125` DOWN, 1–2 s apart. Never send Escape twice: the second one is BACK and can quit the app.

## Real mouse events

System Events `click at` does not reach the watch screen or table cells. Post real events:

```js
// osascript -l JavaScript click.js X Y [count]
ObjC.import('CoreGraphics');
function run(a){ var p=$.CGPointMake(+a[0],+a[1]), c=a.length>2?+a[2]:1;
  for (var n=1;n<=c;n++){ ['LeftMouseDown','LeftMouseUp'].forEach(function(t){
    var e=$.CGEventCreateMouseEvent(null,$['kCGEvent'+t],p,$.kCGMouseButtonLeft);
    $.CGEventSetIntegerValueField(e,$.kCGMouseEventClickState,n); $.CGEventPost($.kCGHIDEventTap,e); }); delay(0.05); } }
```

Coordinates are in screen points (Retina pixels ÷ 2). Popup buttons that refuse a System Events click open with one real click.

## Screenshots

```sh
b=$(osascript -e 'tell application "System Events" to tell process "simulator" to get {position, size} of (first window whose name starts with "CIQ Simulator")' | tr -d ' ')
screencapture -x -R$b shot.png
```

Move the window to a fixed position first so every capture has the same crop.

## macOS details

- No `timeout` command.
- Unit tests: `monkeydo test.prg fr165 -t` prints PASS/FAIL per test.
