# Southern Watch — build notes

What was built from `campaign-bible.md`, where it departs from the bible, and —
more importantly — what has **not** been demonstrated.

## What exists

| Thing | Where |
|---|---|
| The campaign | `integration/campaign/SEST_Campaign/campaigns/sest-southern-watch/campaign.ini` — a `Type=Linear` campaign of twelve missions and three free events |
| Core missions | the same twelve, shipped twice: under `campaigns/…/missions/` for the campaign and under `missions/SEST Southern Watch/` so the mission browser lists them too. The builder writes one copy and `tools/check_campaign_coverage.py` fails if the two ever differ |
| Dispatches | `missions/SEST Southern Watch - Dispatches/` — the eight optional episodes (Allied Dispatch ×3, Red Line, Range Week, Future Front, Cold Sea, plus the relief-perimeter episode) |
| Briefings | a `_briefing/BriefingText_en.xml` beside every mission, with SITUATION / TASK / FORCES / MODS IN PLAY. The mod list is generated from the roster, so it cannot drift from the order of battle |
| Source | `integration/campaign/campaign_data.py` (the script) and `build_pack.py` (the machinery) |
| Coverage report | `docs/campaign-coverage.md`, regenerated on every build |

`python3 integration/campaign/build_pack.py` builds it; `tools/build_all.py`
runs it in order with the other sixteen packs and consolidates it into
`SEST_Integration`.

## Where this departs from the bible, and why

- **All twenty missions were built, not the three-mission vertical slice.** The
  request that started this was a campaign incorporating every mod, and
  coverage is only provable once every mod has somewhere to be. The bible's
  own sequencing advice still stands for *playing*: SW01 → SW02 → SW06 is the
  slice to test first, and it is the slice to fix first if something is wrong.
- **SW09 is written around survival and a service window, not replenishment.**
  The bible flags `ran_aor_supply` as a Teide stand-in with no demonstrated
  supply mechanism. The mission therefore asks you to hold the window and
  withdraw; Collins is placed surfaced, and the surfacing rule stays a house
  rule stated in the briefing rather than a scripted one.
- **No `MissionImage`, `BackgroundImage` or `TileImagePath` keys.** Every one
  would point at a `.png` this repo cannot produce. A dangling art reference is
  worse than a plain campaign card.
- **Theatres follow the position evidence.** Each is somewhere a mission in
  this repo (or in the stock game) has already put a unit of that kind — see
  below. That is why the Levant, the Gulf and the Med do not appear: the
  collection's own missions have never sailed there, so there is no proven
  water to snap to.
- **The bible's `plan_type_055_2026` / `plan_type_052d_p3` / `plan_type_054a_p5`
  advice was followed.** `plan_ddg_type_055` and friends resolve to files under
  `mods-source/3594891803/PLAN mod test/vessels/`, which is two directories
  deep and therefore a path the game never loads. The builder's index excludes
  unreachable paths for exactly this reason.

## How positions were chosen

Every sea and land position is **snapped** to a point some already-loading
mission put a unit of that kind on — the repo's own missions plus the stock
missions and the two stock campaigns, about 5,300 distinct points after
de-duplication. The furthest any station anchor had to move is in the coverage
report's header (36 NM at the time of writing, in the western Timor Sea where
the pool is thinnest). Aircraft are airborne and are placed directly.

`lat = MapCenterLatitude + z/60`, `lon = MapCenterLongitude + x/60`: checked
against the two RAAF bases NORTHERN FRONT II places, which resolve to within a
mile of the real Darwin and Scherger.

This makes a ship-on-land placement very unlikely. It does not make it
impossible, and it says nothing about depth, reef or channel width.

## What has NOT been demonstrated

Static resolution is not a play test. None of the following is established by
anything in this repository:

- that any mission loads in game, or that every texture and model appears;
- that a helicopter can recover aboard the ship it is assigned to;
- that the tankers can actually pass fuel to the receivers in the same mission;
- that replenishment transfers anything, in SW09 or anywhere else;
- that the `UnitsInTheArea` victory triggers fire where intended, that the
  protected-unit failure resolves before victory in the same update, or that
  the neutral-loss handler prevents a win;
- that any mission's unit count is comfortable on a particular PC;
- that the mod-supplied campaign is surfaced by the Mod Manager at all. The
  missions are shipped a second time under `missions/` precisely so the
  campaign's content is playable either way.

What *is* established, on every build: every `Type=`, `LoadoutVariant=`,
`SquadronReference=` and `VariantReference=` in all twenty missions resolves
against the file that wins the current load order, and every enabled mod is
reached by something the campaign places — or carries a written reason why it
cannot be.

## Checking it

```bash
python3 tools/check_campaign_coverage.py    # coverage + references, from the BUILT files
python3 tools/preflight.py "01 White Water" # one campaign mission, the usual way
python3 tools/build_all.py --from-scratch   # the regression gate
```

`check_campaign_coverage.py` deliberately re-derives everything from the built
mission files rather than from `campaign_data.py`, so it still tells the truth
after a mod update that the builder's roster has not caught up with.
