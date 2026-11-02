---
name: garmin-store
description: Prepares and reviews a Connect IQ Store listing, covering titles, descriptions, What's New, cover, hero and screenshot images, the site's limits, categories, pricing and what makes a watch app, face or data field get downloaded and sold. Use when publishing or updating a Garmin app on apps.garmin.com.
---

# Connect IQ Store listings

This skill turns a working Connect IQ project into a listing that passes the upload form on the first try and gives people a reason to install it.

Making the screenshots in the simulator belongs to `garmin-simulator`.

## Respect the form's hard limits

Titles of at most 50 characters, descriptions of at most 4000, no `<` or `>` anywhere in a description (the form rejects "Settings > Data Screens"), a 500×500 cover, a 1440×720 hero for **each** language, at most 5 screenshots under 150 KB each, and a version higher than the last upload ([listing.md](listing.md)). Check all of it with a script before opening the site.

## Lead with the problem it solves

A title that says what people search for beats a bare name: "zonely: Run in the right zone", "Racket Score: 6 Racket Sports". One sentence of promise, then features, setup, FAQ.

## Show the real thing, composed

Raw simulator screenshots sell poorly and the site upscales 390 px images into mush. Compose 900×900 images: a short headline in large type, one line under it, the real watch screen large in a round bezel ([images.md](images.md)). Every watch screen comes from the real app in the simulator, never a mockup.

## Put motion first

An animated GIF of the app actually working is the strongest first image. Keep it at 450 px to stay under 150 KB.

## Never claim what you did not test

A public description that says "works with Strava" or "vibrates" when you only saw the simulator becomes a 1-star review. Write what you verified; phrase the rest as "may".

## Name every permission

Each permission in the manifest (`UserProfile`, `Fit`, `FitContributor`, sensors) gets a plain sentence in the description saying why the app asks for it.

## Decide free or paid before the first upload

Turning a free app paid later pulls it for a new review and makes existing users buy it. A watch face cannot have a paywall or a trial: the time is its main function ([selling.md](selling.md)).

## Earn reviews, never fake them

Ask for a review in one line at the end of the description, share it where runners or players gather, reply to every review. Fake reviews can get the app removed.
