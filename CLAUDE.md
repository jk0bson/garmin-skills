# Maintaining garmin-skills

Agent skills for Garmin Connect IQ (Monkey C). This file is for editing this repo; plugin users never load it.

## Self-learning rule

Whenever you fix a `monkeyc` error, a `-w` warning, a simulator bug or a Garmin API trap while building an app, **add a short, actionable rule (1 to 3 lines) right away** to the matching file under `skills/`, then say in your reply which rule you added and where.

| Topic | File |
|---|---|
| input, touch, buttons, vibration | `skills/garmin-app/input.md` |
| data fields, Activity.Info, complications' units | `skills/garmin-app/data-fields.md` |
| memory, watch faces, always-on, background, settings | `skills/garmin-app/memory-and-api.md` |
| web requests | `skills/garmin-app/network.md` |
| compiler errors, tests, builds | `skills/garmin-app/testing.md` |
| colors, fonts, layout | `skills/garmin-design/*.md` |
| simulator | `skills/garmin-simulator/*.md` |
| store listing and images | `skills/garmin-store/*.md` |

## Rules for rules

- Say what was seen and where: "verified on fr165", "seen in Crystal Face, not verified here", "SDK docs, not verified here". Never present an unverified claim as fact.
- Keep the real story (the shower drop, the brown that turned olive, the 14 overflowing labels): it is why the rule is believed.
- Keep every `SKILL.md` under 100 lines; code, commands and long lists go in the secondary files.
- One home per topic: update the existing rule instead of adding a second one elsewhere.
- Never rename `skills/garmin-app`, `garmin-design`, `garmin-simulator`, `garmin-store` or `.claude-plugin/`: installs depend on them.
- From other repos, take ideas in our own words; never copy code from GPL or unlicensed projects.
- Bump `version` in `.claude-plugin/plugin.json` for every user-facing change, or `/plugin marketplace update` will not see it.
