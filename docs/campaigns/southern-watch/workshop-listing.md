# Workshop listing — paste-ready copy

Everything below is for the Steam Workshop page. The mod's own
`_info.ini` is the Mod Manager blurb and is generated; this is the longer
page a subscriber reads before they click. Nothing here is generated, so if
the campaign changes, this changes by hand.

A note before the copy: this pack **requires 135 other Workshop mods**. That
is not a footnote, it is the headline risk of publishing it. A subscriber who
skims the description, subscribes, and starts the campaign with forty of them
will get missions that are not the missions that were built. Say the number
early and say it plainly — the copy below does.

---

## Title

```
Southern Watch — The Northern Lifeline
```

## Short description (the card blurb)

```
A twelve-mission Task Force Mode campaign in the Arafura and Coral Seas,
October–November 2028. Escort, reconnaissance and a slow escalation into a
limited regional war. Heavy mod collection required — read the description.
```

## Description

```
SOUTHERN WATCH — THE NORTHERN LIFELINE

Twelve connected missions, 18 October to 28 November 2028. Australia and its
regional partners keep the northern sea routes open through a maritime
coercion campaign that escalates into a limited regional war.

It opens small. A merchant misses a rendezvous and you have one frigate, a
Seahawk on the deck and a lane full of working traffic — a bulker, a chartered
coaster, trawlers, the 0600 Denpasar service overhead. One contact in that
picture is armed and one is a decoy that has squawked as a merchant since it
sailed. Your weapons are tight. Identify before you shoot.

It does not stay small.

WHAT IT IS
  • Task Force Mode. You buy the force, and losses and expenditure carry
    forward. Losing a support ship costs you what that ship was doing.
  • Twelve core missions, plus four optional operations and two
    contingencies. What you do in an optional operation is read later: a
    contact briefing with a picture in it, a Korean destroyer in your screen,
    a tanker on the track, a rearm you earned by holding a service window.
  • Partners arrive on their own terms - a New Zealand Poseidon for one
    sortie, a Korean detachment for a fortnight, a Japanese pair, an American
    carrier under a bounded arrangement - and none of them is yours to keep.
  • Eight standalone dispatches in the mission browser: allied rotations, the
    opposing side's logistics problem, a weapons range, an openly speculative
    2034 branch, and a 1988 Cold War exercise.
  • Reconnaissance decisions that matter more often than fleet battles do.
    Several missions are about finding something, and the campaign map will
    not tell you where it is.
  • Civilian traffic in almost every mission. Neutral losses end operations.

WHAT IT NEEDS — READ THIS PART

This campaign is built on a large mod collection. It names units from
**135 Steam Workshop mods**. That is the point of it — the campaign exists to
give a very large collection somewhere purposeful to be used — but it means
subscribing to this alone is not enough.

You should not have to subscribe to them one at a time. Every one is set as
a Required Item on this page, so after subscribing here, open the Mod Manager
and press **Sync**. The game asks Steam for this mod's dependencies,
subscribes you to the ones you are missing and enables the ones you already
have — and it iterates, so their dependencies come too.

Then open this mod's folder and read the files in it:

  REQUIRED-MODS.txt — every Workshop mod the campaign names, with its ID
  LOAD-ORDER.txt    — the 143-entry Mod Manager order it was built against
  CREDITS.txt       — whose work this is built on

Put this pack at the TOP of your load order. It contains whole-file
replacements, and anything above it wins instead. Sync handles subscribing;
it does not handle ordering, and ordering is what decides which copy of a
shared file the game reads.

What the game does with a mission that names a unit you do not have has not
been tested. At best the unit is simply absent and the mission is an easier,
different one; at worst the mission does not load. Neither is the mission that
was built. If you are not going to work through the mod list, this is probably
not the download for you, and that is a fair thing to know in advance.

A few of those mods need a further download of their own and say so in their
own descriptions. SeaLifter is the one that catches people: subscribing to it
is not enough.

CREDIT WHERE IT IS DUE

This pack is a set of patches, and a Sea Power unit file is a whole-file
override - there is no way to change one line of somebody's aircraft without
shipping the whole aircraft. So 79 of the unit files here are another author's
file with edits in it, drawn from 28 different Workshop mods. HMAS Hobart is
Euromod's Alvaro de Bazan; the fifteen RAAF airbases are built off Modern US
Airbase's large airfield; the Super Hornets are US Navy 2027's.

CREDITS.txt inside the folder lists every one of them, which mod it came from
and how much of the file is unchanged. It is generated by diffing the shipped
files against the collection, not typed, so nothing can fall off it.

If you wrote one of those mods and would rather this pack did not carry a copy
of your file, say so and it will be changed.

FICTION

Every nation, unit, ship name, incident and date in this campaign is invented.
It is set in a near-future that does not exist and takes no position on any
real dispute, government or armed force. The "Meridian" escorts are not a real
navy. Where real countries appear, their conduct here is fiction.

ENGLISH ONLY

The text is English. The campaign map art is shared across every language the
game supports, so the mission cards and story pages appear whatever your
locale is set to, but the writing in them is not translated.

STATUS

First public release. The build is checked automatically — every unit,
squadron, loadout variant and weapon in all twenty-six missions is verified to
resolve against the mod that wins the load order, on every build. What that
does NOT check is balance. No mission here has been played to completion by
its author at the time of writing. Feedback on difficulty, pacing and anything
that turns out to be impossible is genuinely wanted.
```

## Tags

`Campaign`, `Missions`, `English`

## Screenshots, in this order

The pack generates its own art. The mission sheets are the stock 1184×640 and the backdrop and story images 1920×1080; the screenshot slots take those as they are
and are in `campaigns/sest-southern-watch/art/` inside the mod:

1. `00_campaign_background.png` — the theatre chart. Sets the scale of the
   thing before anything else does.
2. `southern_watch_01_sheet.png` — a mission card. Shows the format.
3. `00_opening_image.png` — the opening dispatch sheet. Shows there is a
   story layer.
4. `southern_watch_08_sheet.png` — the carrier mission's card, for the plot
   at its busiest.
5. An in-game screenshot of the campaign map with the backdrop behind it.
   **Take this one yourself** — there is no way to fake it, and it is the one
   a subscriber most wants to see.

## What NOT to put on the page

- The repository, the build tooling, or anything about how it was made. A
  subscriber cannot act on any of it.
- A claim that it is balanced or tested in play. It is not yet.
- A promise of translations, or of support for a specific mod list other than
  the one that ships.
