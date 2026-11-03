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
}
```

## Rules

- During a session, only physical buttons may start, pause or score. A tap may adjust a setting before the start.
- On button-less watches, give every action a tap zone (top, bottom, very bottom) and say so in the store description.
- Test a tap in the simulator with real mouse events (`CGEventPost`); System Events `click at` does not reach the watch screen.
