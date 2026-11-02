# Tests and builds

## Commands

```sh
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
