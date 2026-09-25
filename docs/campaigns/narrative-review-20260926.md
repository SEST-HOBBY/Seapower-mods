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
- The 1988 PITCH BLACK dispatch remains an exercise; its denied message reports
  the umpires' simulated-release decision.

## Layout

Briefings retain paragraph breaks and separately spaced task lines. Operational
message headings replace victory/defeat and faction labels. Mod-provider lists
remain in the technical installation and coverage files.

Deck logs separate the date, ship and master, align times beside wrapped
remarks, and size the master's note before reserving its space. Signals wrap
long metadata and analyst notes. Intelligence summaries separate organisation,
reference/date and subject. These renderers reject vertical overflow instead
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
