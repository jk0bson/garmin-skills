---
name: garmin-release
description: Runs the pre-publication checklist of a Garmin Connect IQ app, watch face or data field, covering the release export for every manifest device, memory on the tightest watch (active and always-on), a read-only font audit, simulator captures, store images from store_assets.py and the final check_listing.py pass, plus the working protocol (read-only diagnosis, one project per change, a Verified / Not verified report). Use before uploading a first version or an update to apps.garmin.com.
---

# Releasing to the Connect IQ Store

This skill orders the checks that stand between a working project and an upload the store accepts. Each step points to the skill that holds the detail; run them in this order, because a late step can invalidate an early one.

## Working protocol

1. **Diagnose read-only first.** Before editing several files or generating images, read the project (manifest, sources, store folder, git status) and write a minimal plan: what changes, in which files, how it will be checked. Edit nothing until that plan exists.
2. **One project per change.** Every commit touches a single project folder. Do not carry other apps, agent settings or tool folders into it; look at `git status` before staging and stage paths by name.
3. **Report with two lists, never mixed.** End with **Verified** (what ran, with the numbers: memory in KB per device, tests passed, image sizes in KB) and **Not verified** (what was only read, assumed, or not run on a real watch). An empty Not verified list is almost never true: say what the simulator cannot show.

## Checklist

1. **Version.** Raise `version` on `iq:application` in `manifest.xml` above the last upload; the store refuses a version it has seen ([listing.md](../garmin-store/listing.md)).
2. **Export for every device.** `monkeyc -f monkey.jungle -o app.iq -y KEY -e -r -w` builds every device listed in `manifest.xml`. Wait for "N OUT OF N DEVICES BUILT" and read the warnings: a new `-w` warning is a defect ([testing.md](../garmin-app/testing.md)).
3. **Memory on the tightest watch.** Find the device with the smallest `memoryLimit` in its `compiler.json` ([memory-and-api.md](../garmin-app/memory-and-api.md)). Run it in the simulator and read the memory view in the normal screen **and** after the always-on or sleep screen has drawn once. `usedMemory` counts only the heap, not bitmaps: do not quote it as the whole story. AMOLED always-on: check File > View Screen Heat Map for under about 10 % lit pixels.
4. **Font audit, read-only.** `python3 bitmap_fonts.py --project P --strings STRINGS_FILE` without `--font` checks the `.fnt` files already in the project and writes nothing ([fonts.md](../garmin-design/fonts.md)). It cannot see text the system supplies: grep the sources for `FORMAT_MEDIUM`, `day_of_week`, `month` and other `Gregorian.info` names, which come back in the watch's language with glyphs your font may lack. Use your own strings per language instead.
5. **Captures from the simulator.** Real screens only, square, cropped to the screen, in every language you list and on the watch sizes you claim (218 to 280 px MIP, 390 px, 454 px and above AMOLED). See [captures.md](../garmin-simulator/captures.md). Hard states come from a demo copy, never from the shipped code.
6. **Store images with `store_assets.py`.** Pick the preset that matches what you ship, run it once per language, and keep the "screens" line it prints for `store.json` ([images.md](../garmin-store/images.md)):
   - `--preset watchface`: flat colour screens, one theme per image, a GIF that cycles themes.
   - `--preset app`: dark textured backdrop, glow, 1 to 3 bezelled watches.
   - `--preset datafield`: the same dark look on a track backdrop, one accent per zone or metric.
7. **Descriptions.** Titles at most 50 characters, descriptions at most 4000, no `<` or `>`, a plain sentence per permission, nothing claimed that was not tested ([SKILL.md](../garmin-store/SKILL.md)).
8. **Final gate.** `python3 check_listing.py STORE_FOLDER` must print "listing OK". Then look at every image once at full size: a green check does not see a cropped ring or a clipped word.

## Common failures

- A build that passes for one device and fails on another: step 2 exists for that.
- Placed text that overflows on AMOLED: those fonts are taller than MIP ones, so place from `dc.getFontHeight()`.
- A GIF that looks fine but is over 150 KB, or a hero for one language only: the gate catches both, so run it last, after the final regeneration.
- Editing an image script and shipping the old PNGs: regenerate, then run step 8 again.
