# Tests and builds

## Commands

```sh
SDK="$(cat "$HOME/Library/Application Support/Garmin/ConnectIQ/current-sdk.cfg")bin"   # active SDK; put $SDK/ before monkeyc and monkeydo
# Windows (not verified here): %APPDATA%\Garmin\ConnectIQ\current-sdk.cfg, tools are monkeyc.bat and monkeydo.bat
# Linux (not verified here): ~/.Garmin/ConnectIQ/current-sdk.cfg

# one device, with tests
monkeyc -f monkey.jungle -o test.prg -y developer_key -d fr165 -t -w
monkeydo test.prg fr165 -t

# release package for every device in the manifest
monkeyc -f monkey.jungle -o app.iq -y developer_key -e -r -w   # wait for "N OUT OF N DEVICES BUILT"
```

## Rules

- Put logic in a module (`MyLogic.mc`) and tests in `MyLogicTest.mc` with `(:test) function name(logger as Logger) as Boolean`.
- Keep each test to a few comparisons. One long condition mixing nullable values made `monkeyc -t` run out of Java heap; more memory did not help, splitting did.
- Cast a nullable result before comparing: `var v = Logic.f(x) as Float;`.
- Test the edge cases the watch will meet: `null`, zero, negative distance, absurd grade, 10-hour durations, imperial units.
- A failing build prints a Java stack trace: read the first non-`at` line.
- Compiling is not testing. Also run the field in the simulator on one device per screen size (`garmin-simulator`).

## Errors met

- `fillPolygon` wants `Array<[Numeric, Numeric]>`.
- `fitContributions.xml` needs a `unitLabel` that points at a real `@Strings.x`.
- "Cannot resolve type 'Duration'": add `import Toybox.Time`.
- macOS has no `timeout` command.
- A font loaded in `onLayout` into `var f as FontResource` warns about `Null` at `-l 2`: declare it `(:initialized) var f as FontResource;` (seen on Instinct 3 by another developer, not verified here).
- Strict typing (SDK docs, not verified here): a concrete type does not accept `null` (write `Number?`); `Array<String>` does not match `Array<String or Number>`; a null check on a member variable is forgotten after any function call, so copy the member to a local first.
- A UTF-8 byte-order mark at the start of a `strings.xml` broke the build: save resource XML without BOM (seen in Crystal Face, not verified here).
- After an SDK update, rebuild every device and re-read the manifest: fēnix E vanished from SDK 9.1.3 and came back later (seen in Tesla-Link, not verified here).

## Crashes from real users

The SDK's Error Reporting Application (ERA) downloads crash reports from watches running your store app. Tesla-Link fixed most of its 7.11 to 7.14 crashes from it (SDK tool, not yet used here).

## A minimal test

Logic in `source/Pace.mc`, tests in `source/PaceTest.mc`. Verified on fr165 with SDK 9.2: both PASS.

```monkeyc
// Pace.mc
import Toybox.Lang;
module Pace {
    function secPerKm(speed as Float?) as Number? {
        if (speed == null || speed < 0.5) { return null; }
        return (1000.0 / speed + 0.5).toNumber();
    }
}

// PaceTest.mc
import Toybox.Lang;
import Toybox.Test;
(:test)
function paceNullSpeed(logger as Logger) as Boolean {
    return Pace.secPerKm(null) == null;
}
(:test)
function paceFiveMinutes(logger as Logger) as Boolean {
    var v = Pace.secPerKm(3.3333) as Number;
    Test.assertEqualMessage(v, 300, "3.33 m/s should be 5:00 /km");
    return true;
}
```

The simulator must be running before `monkeydo test.prg fr165 -t`.
