# Campaign narrative revision — 26 September 2026

This revision integrates the additional campaign work through
`d546858240ea948b6f76af27fcd6c5afa8c3ac41` with the earlier narrative and layout
review. It covers all 51 missions and 36 story pages: Southern Watch and its
dispatches, Southern Reach, and Tasman Shield. Authoring sources and generated
campaign files are updated together, including the consolidated pack.

## Additional content retained

- New names, bearings, force descriptions and dates remain the starting point
  for the revised prose, including the northbound SW06 transport and D8's date.
- The New Zealand nation-key fixes, RNZAF Poseidon and Swedish GlobalEye
  assignments, civil-airway routes and gates, and asset attribution remain
  unchanged from the latest base.
- The paragraph-aware press layout, in-world security markings and boxed deck
  log notes are retained and combined with the earlier readability fixes.
- The existing small menu tiles are unchanged. The rejected icon artwork and
  its generator are not included.

## Story, orders and dialogue

Campaign descriptions now explain the conflict, opposing organisations and
operational progression without mission counts, purchase language or what-if
labels. Story pages and briefings distinguish Meridian's commercial and armed
security businesses, the southern contractor and protection group, and the
Russian detachment. Recurring officers and civilian voices remain.

The ceasefire takes effect on 27 November; the first convoy passage is on
28 November. The dated deck log, situation report and mission briefing now
agree. The final southern log anticipates the 2 March passage. These are text
corrections, with no change to the mission calendar.

All 34 ISR suggestions from the additional review have a recorded disposition
in [isr-dialogue-notes.md](isr-dialogue-notes.md). Existing messages identify
collection or reporting sources, separate confirmed classifications from
assessments, and explain which contacts need local confirmation. Satellite
radar imagery, AIS, patrol reports, airborne radar and acoustic records are
used for their distinct roles. Illustrative coordinates, timestamps, guaranteed
tracking from takeoff, and satellite fixes of submerged boats are not carried
into event messages.

These edits do not implement timed ISR updates, sensor fusion, track decay or
new reveals. Existing persistent reveals remain persistent. A future dynamic
report feature needs actual runtime observations; extrapolating an authored
route is not a live contact report.

Orders and outcomes are matched more closely to the existing conditions:

- Steel Highway requires at least three arrivals, including both Kokoda Star
  and Coral Pioneer.
- The Open Door checks one relief-aircraft arrival while requiring both
  transports to survive.
- Southern Lifeline, Macquarie Passage and Cook Strait describe their timed
  position checks rather than promising continuous dwell or measured transfer.
- Recovery and handover reports avoid claiming a checked landing where the
  condition is an area arrival. Several outcomes no longer assert unobserved
  enemy withdrawals or optional classifications.
- The 1988 PITCH BLACK dispatch is the exercise that went live at 0412 (see
  the review below); its denied message reports the Bear at its release area
  and the umpires closing the serial.

## Layout

Briefings retain paragraph breaks and separately spaced task lines. Operational
message headings replace victory/defeat and faction labels. Mod-provider lists
remain in the technical installation and coverage files.

Deck logs separate the date, ship and master, align times beside wrapped
remarks, and size the master's note before reserving its space. Signals wrap
long metadata and analyst notes. Intelligence summaries set the organisation
and reference/date on one line when they fit, then the subject. These renderers reject vertical overflow instead
of dropping or clipping content. Fiction banners are absent from the narrative.

## Verification

- Complete campaign build: 51 missions, 36 story pages, 563 source-pack files.
- Consolidation: 691 files from 17 component packs.
- Coverage: 94 shipped mission copies, 1,396 placed unit references; all 159
  enabled mods and SEST packs accounted for.
- All 224 source-pack XML files and 224 consolidated copies parse successfully.
- All 562 mirrored campaign files match byte for byte; campaign-owned subtree
  inventories also match, with no stale extra files. The consolidated root
  `_info.ini` is composed separately.
- Every mission's non-language sections match the latest base. Source-data
  comparison finds 263 changed display-text leaves and no mechanics changes.
  Campaign conditions, schedules, allocation rules and asset references are
  unchanged apart from display strings and corresponding section comments.
- All four deck logs, both opening press pages, two intelligence summaries and
  two long signal pages were visually checked. Layout checks pass. Existing
  menu-tile bytes match the base.
- Generated INI/XML contains no fiction banners, substitute-model tags or
  mod-provider headings. `git diff --check` passes.

Commands run:

```sh
python3 integration/campaign/build_pack.py
python3 tools/consolidate_packs.py
python3 tools/check_campaign_coverage.py
git diff --check
```

This is static and rendered-page verification. The in-game briefing panes,
story scaling, displayed messages and runtime trigger behaviour still require
a Sea Power play test. The existing test cards retain those checks.

## Review of this revision (26 September)

Three reviewers checked this revision: mechanics and reproducibility, facts
and narrative, and page layout. They confirmed that it changes display text
only. Their 27 findings, and what was done about each, are listed here. The
revision's prose remains the baseline; only these points changed.

**Message format**

| Finding | Done |
|---|---|
| Blocking: SW D7 and SW O1 denied messages had a second `\|` inside the body. The game reads a message as `Title\|Body\|Button` | Both now read `SENDER: text`. `build_pack.check_message_texts()` runs in `render()` and stops the build, naming the mission and key, on a `\|` in brief, win, lose, timeout, stage-lost or denied text, or in any intel text |
| All rewritten intel used `SENDER \| text`; no evidence that intel text accepts `\|` | 37 strings in both campaigns now use `SENDER: text`, with the same senders. Generated INI files: 156 intel values, none with `\|`; 1,300 message values, each with exactly the builder's own `Title\|` separator |
| `TITLE_FIX` was dead after MODS IN PLAY went | Deleted |
| build-notes still listed MODS IN PLAY | The briefing row lists SITUATION / FROM / COMMANDER'S INTENT / TASK / FORCES / TIME / RULES OF ENGAGEMENT |
| Both red-side banners read "Command report."; TIME no longer said the main task fails | "Opposing force prevailed." / "Opposing force defeated."; TIME ends "...and the main task will be recorded as failed." |

**Facts and story**

| Finding | Done |
|---|---|
| Blocking: D7 read as a pure exercise, but the Bear must be shot down with live weapons. This reopened review-disposition "nobody is shooting anything real" | Brief, intent, intro, win, denied message and the dispatch description say the serial went live at 0412: a live round at the range ship, and aggressors answering with real missiles. The umpires still score the tanker |
| Reveal messages sent the player to confirm contacts that `UnitRevealTime=-1` keeps on the plot | SW02, SW04, SW06 (and its brief: "it stays on your plot for the rest of the morning"), SW11, SR05, SR07, SR10, TS01, TS02, TS03 (both), TS04, TS05 and TS12 say the contact is held on the plot for the operation. Only contacts a reveal does not cover are left to local sensors |
| Southern Reach task group was "newly allocated" | INFO_DESC and the opening page: the task group that held the north |
| INFO_DESC tied TS10A/B to the final relief passage | They decide which opposing detachments rejoin the carrier group for the western-Tasman fleet action (TS11) |
| D4 put the Australian patrol across the corridor and used a Tu-95MS as the sensor | About 120 NM west-south-west of the auxiliary, closing north-east; the escorts' and fighters' sensors update it |
| 5 January INTSUM put the formation south of the Casey route | With the fishing fleet at the ice edge, across the route to Casey |
| TS11 said "engage" for a scored destroy objective | Intro and intent: sink the Type 052D, and Liaoning if the opportunity permits |
| O1 denied text read as recoverable; "recovery handover distance" | Salvor alongside with her crane working, recovery failed; "inside a mile and a half" |
| SW03 "complete the pickup" for an area check | Lifter over the rig, crew boarding; the order is the return |
| SW12 first light read as 27 November | Ceasefire 0000 on 27 November; the first convoy sails at first light today (28th) |
| SW01 window lost the empty-deck warning | The Seahawk is not automatic: allocate an MH-60R and assign it to Ship's Flight under Air Tasking, or the deck sails empty |
| 12 November INTSUM para 4 quoted the objective rules | Guidance in voice: seventy-minute window, a silent battery is worth more than a destroyed one, the civilian buildings are not targets |
| 8 November Ward memo: wrong "tomorrow" | Para 4: packages still airborne lose their fuel and the next day's sorties are replanned |
| SR epilogue asserted crew losses | "Whatever it cost is in the task group's report"; "any crews lost" |

**Layout**

| Finding | Done |
|---|---|
| SW Meridian INTSUM fell to 18pt | `intsum()` sets ref/date on the organisation line when they fit, drops the half-line counted after the last paragraph, and keeps a trailing "  - Cdre Mercer" intact. Para 4 is two lines. Now 22pt; SR 03b INTSUM 24 to 26pt |
| Speaker tags collapsed to one space | "A:  " / "B:  " in both intercepts; the dialogue column aligns |
| SR 04 sitrep body contradicted "THE STATIONS ARE SUPPLIED"; 21pt | The stations have their winter; the fuel margin depends on which tankers came through. 23pt |
| "Force allocation" jargon on the SR opening page | Removed (see the task-group line) |
| "12 / kn." split in the 6 December log | "twelve knots" |
| One-word widow in the 28 February master's note | Two lines |
| SR 02 and 06 sitreps stepped down to 21pt | Both 23pt with the facts kept. SR 02 no longer strands one line at the head of the right column. SW 03b and SR 05b stay at 24pt (not in scope) |
| Briefing loose ends | Bullets use `Margin="0,0,0,4"`; defeat banners read "Operation failed." (Taskforce1DefeatMessage, StageLostMessage, Denied), and the neutral-loss body says the operation has failed |

[isr-dialogue-notes.md](isr-dialogue-notes.md) rows 5, 7-9, 13, 18, 19, 22, 24,
25 and 31-34 now describe the current wording.

Verification: `build_pack.py` and `consolidate_packs.py` succeed.
`check_campaign_coverage.py`, `check_load_order.py`, `check_dependencies.py`,
`preflight.py`, and `preflight.py` run on each of the 51 campaign missions by
name, all exit 0. All 188 briefing XML files parse, and `git diff --check`
passes. Thirteen story pages changed; each was viewed as rendered. Type sizes
that moved: SW 00b 18 to 22pt; SR 02, 04 and 06 sitreps 21 to 23pt; SR 03b
24 to 26pt. Nothing got smaller. In-game display of messages and intel still
needs the play test in the test cards.
