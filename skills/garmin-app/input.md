# Input on touch and button watches

Verified in the simulator on vívoactive 5, FR165, fēnix 7 Pro and Venu 4.

## The bug

`WatchUi.BehaviorDelegate` maps a screen tap to `onSelect()`, which is also START. `onTap()` is never reached, even when overridden. On watches without UP/DOWN buttons (vívoactive 5/6, Venu 4) every tap or drop of water on the screen started or paused the session.

## The fix

```monkeyc
class MyDelegate extends WatchUi.InputDelegate {
    function onKey(evt as WatchUi.KeyEvent) as Boolean {
        switch (evt.getKey()) {
            case WatchUi.KEY_ENTER: return start();     // START button
            case WatchUi.KEY_ESC:   return back();      // BACK button
            case WatchUi.KEY_UP:    return up();
            case WatchUi.KEY_DOWN:  return down();
            case WatchUi.KEY_MENU:  return menu();      // long press UP
        }
        return false;
    }
    function onTap(evt as WatchUi.ClickEvent) as Boolean {
        var xy = evt.getCoordinates();                  // decide by zone, never "any tap = START"
        return tapZone(xy[0], xy[1]);
    }
    function onSwipe(evt as WatchUi.SwipeEvent) as Boolean { return true; }   // swallow unless used
    function onHold(evt as WatchUi.ClickEvent) as Boolean { return true; }
    function onFlick(evt as WatchUi.FlickEvent) as Boolean { return true; }
    function onDrag(evt as WatchUi.DragEvent) as Boolean { return true; }
}
```

## Rules

- During a session, only physical buttons may start, pause or score. A tap may adjust a setting before the start.
- On button-less watches, give every action a tap zone (top, bottom, very bottom) and say so in the store description.
- Test a tap in the simulator with real mouse events (`CGEventPost`); System Events `click at` does not reach the watch screen.

## Watch face touch

In a watch face, `WatchFaceDelegate.onPress(evt)` gets the touch. Find the complication under `evt.getCoordinates()` and open Garmin's own widget with `Complications.exitTo(id)` inside a `try` (seen in Crystal Face, not verified here).

## Vibration and sound

Not every watch vibrates or beeps: test `Attention has :vibrate` and `Attention has :playTone` before calling them (seen in Tesla-Link, not verified here).
- Swipes: `onSwipe(evt)` with `evt.getDirection() == WatchUi.SWIPE_LEFT` (next page) or `SWIPE_RIGHT` (previous). Verified on FR165 in the simulator; `onFlick` takes the same call and compiles, but the simulator never fired it, so it is unverified.
- On touch watches, draw one button per action and test only its circle; a reset or delete button shows only while the timer is paused (`timer timer timer!`), so a wet finger cannot wipe a running timer.
