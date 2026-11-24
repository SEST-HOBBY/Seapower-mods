# Sea ice in the Sea of Okhotsk and the Bering Sea

Status: BUILD-TESTED (Python). Code: `integration/environment/mno_env/seaice.py`
(section "Marginal seas"). Tests: `integration/environment/tests/test_seaice.py`
(`TestMarginalSeas`).

## What was wrong

The old model moved one ice edge for the whole Arctic. The Arctic Basin has its
minimum in September. The Sea of Okhotsk does not follow it. Its ice peaks in late
February to early March and is gone by early July.

The old Okhotsk term was a fixed shift of 21 degrees of latitude, all year. So:

- The northern Sea of Okhotsk stayed iced all summer. At 59N 145E the model gave
  92 % on 15 July and 44 % on 15 August (baseline 2016_2025). With 1981_2010 it
  gave 97 / 90 / 78 % in July / August / September.
- It refroze too early. 59N 145E was back to 67 % on 15 October.
- Its regional extent in June to November was 3 to 7 times the observed value.
- The Shantar Islands corner (55N 137E) and the Tatar Strait never froze.
- The Bering Sea had only about half its observed winter extent.

## Reference data

All numbers below come from these sources. Estimates are marked.

1. NSIDC Sea Ice Index G02135 v4.0, regional monthly extent. File
   `N_Sea_Ice_Index_Regional_Monthly_Data_G02135_v4.0.xlsx` from
   <https://noaadata.apps.nsidc.org/NOAA/G02135/seaice_analysis/>. Downloaded
   2026-11-24. SHA-256
   `557eed67f84961fb017827b23c88aceeb6fc9bd5a33fe5e4f8078d860c9db084`.
   Regions are those of Meier et al. (2007), Annals of Glaciology 46. NSIDC's
   "Okhotsk" region includes the Sea of Japan and the Tatar Strait.
2. The daily file from the same folder,
   `N_Sea_Ice_Index_Regional_Daily_Data_G02135_v4.0.xlsx`, SHA-256
   `eaad90ba809b634b9bcc5baad09b15528e709e962c81fd4ea1f84c7fcbc0d315`. Used only
   for the key dates below.
3. The region mask `Arctic_region_mask_Meier_AnnGlaciol2007.txt`, SHA-256
   `56afd20963c5dd5f424a9ab4ba812e87b6a0ef1993eb67af1aedf42add4ac26e`,
   downloaded the same day with the regional files. The exact URL was not
   recorded. Verify it before relying on it.
4. Kimura and Wakatsuchi (1999), J. Geophys. Res. 104(C5): 11137. Ice forms first
   on the north-west shelf and spreads east and south, mainly by wind drift.
5. Rikiishi and Takatsuji, Annals of Glaciology. The ice edge runs south along
   east Sakhalin at about 35 cm/s with the East Sakhalin Current.
6. Annals of Glaciology (1990), on the Siberian High and Aleutian Low and the
   Okhotsk ice cover. By June only coastal ice is left, mostly in the north-west.
7. Drift ice first reaches Abashiri (Hokkaido) about 22 January in a normal year.
   Source: Japan Meteorological Agency normal, seen only through news reports.
   ESTIMATE.
8. Ice leaves Hokkaido about early April. Inferred from an NIPR report on the late
   1992/93 season. ESTIMATE.
9. A secondary source says floes stay in the Shantar bays until mid-July in some
   years. UNVERIFIED.

The JMA climatology pages (www.data.jma.go.jp) and a 2024 Journal of
Oceanography paper (doi:10.1007/s10872-024-00721-z) could not be read. The
session network blocks those hosts.

### NSIDC monthly median extent (thousand km2)

| Region, years | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Okhotsk 2016-2025 | 670 | 1005 | 1055 | 551 | 171 | 75 | 0 | 0 | 0 | 44 | 67 | 282 |
| Okhotsk 1981-2010 | 778 | 1101 | 1092 | 788 | 233 | 83 | 0 | 0 | 0 | 37 | 66 | 300 |
| Bering 2016-2025 | 469 | 583 | 622 | 542 | 212 | 34 | 3 | 0 | 1 | 12 | 37 | 181 |
| Bering 1981-2010 | 609 | 709 | 767 | 663 | 345 | 55 | 4 | 0 | 2 | 17 | 85 | 318 |

These are medians of each month over the years. The code stores them to one
decimal (`NSIDC_REGIONAL_MEDIAN_KKM2`).

Key dates from the daily file (median over years):

- Maximum: about 6-8 March.
- Extent below 100 thousand km2: about 1 June (2016-2025) or 6 June (1981-2010).
- Extent below 50 thousand km2: about 1-2 July.
- Extent above 100 thousand km2 again: about 2 December.

### Two corrections to the targets (ESTIMATES)

1. July to October are set to 0. In every recent year the NSIDC regional series
   is exactly 0 from about 1-3 July to 1 October. That looks like NSIDC's
   valid-ice mask, so the exact July date is partly an artefact.
2. The October value (10-50 thousand km2) is nearly the same every year. It looks
   like coastal land spill-over, not ice. It is set to 0, and the same amount is
   taken off November.

## How the new model works

Inside each of the two seas the model has its own edge.

- A fixed "ice order" field `s(lat, lon)` ranks where ice forms first and melts
  last. It is a hand-fitted shape, NOT data. Its terms follow sources 4 to 9:
  - Order falls to the east (warm Pacific water enters through the Kurils).
  - The Shantar Islands / Sakhalin Gulf corner keeps ice longest.
  - A tongue of ice runs south along east Sakhalin to Hokkaido.
  - Only the northern Tatar Strait freezes. Ice stops near 48N. (Estimate of
    47-48N. No edge-latitude source was found.)
  - The rest of the Sea of Japan stays open.
  - Bering Sea: ice forms first in Norton Sound, near Bering Strait and in the
    Gulf of Anadyr. The deep Aleutian Basin stays open.
- Concentration is a logistic in `s`. It is exactly 15 % at the regional edge. It
  reaches 90 % about 2.3 units inside it. Pack concentration is capped at 95 %
  for polynyas (estimate).
- For each date the regional edge is solved so that the sea's extent matches the
  NSIDC regional target. Extent means 1-degree ocean cells with 15 % or more,
  the same rule as the hemispheric model. Targets are interpolated between
  mid-month values, like the hemispheric ones.
- The seas are the 1-degree cells that fall in, or within about 75 km of, the
  NSIDC region mask (`_MARGINAL_ROWS`).

The hemispheric edge is solved exactly as before. So every cell outside the two
seas is unchanged.

There is no on/off switch. This corrects the existing default climatology. It
adds no new game feature.

## Results: before and after

All values are for the 15th of the month, 12:00 UTC.

### Regional extent (thousand km2, cells of the NSIDC region)

Baseline 2016_2025:

| | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Okhotsk before | 906 | 1021 | 1049 | 930 | 791 | 516 | 256 | 78 | 32 | 131 | 412 | 695 |
| Okhotsk after | 678 | 1006 | 1044 | 542 | 167 | 73 | 0 | 0 | 0 | 0 | 26 | 288 |
| Okhotsk NSIDC | 670 | 1005 | 1055 | 551 | 171 | 75 | 0 | 0 | 0 | 44 | 67 | 282 |
| Bering before | 156 | 257 | 274 | 194 | 48 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Bering after | 473 | 584 | 621 | 535 | 212 | 37 | 0 | 0 | 0 | 0 | 31 | 184 |
| Bering NSIDC | 469 | 583 | 622 | 542 | 212 | 34 | 3 | 0 | 1 | 12 | 37 | 181 |

Baseline 1981_2010:

| | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Okhotsk before | 1043 | 1182 | 1188 | 1067 | 882 | 679 | 412 | 242 | 173 | 327 | 559 | 816 |
| Okhotsk after | 783 | 1103 | 1082 | 783 | 227 | 80 | 0 | 0 | 0 | 0 | 33 | 302 |
| Okhotsk NSIDC | 778 | 1101 | 1092 | 788 | 233 | 83 | 0 | 0 | 0 | 37 | 66 | 300 |
| Bering before | 274 | 402 | 426 | 314 | 119 | 0 | 0 | 0 | 0 | 0 | 0 | 92 |
| Bering after | 609 | 709 | 766 | 658 | 339 | 53 | 0 | 0 | 0 | 0 | 69 | 321 |
| Bering NSIDC | 609 | 709 | 767 | 663 | 345 | 55 | 4 | 0 | 2 | 17 | 85 | 318 |

October and November "after" are below NSIDC on purpose (correction 2 above).

### Concentration at points (%, baseline 2016_2025)

| Point | | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 59N 145E, north coast | before | 98 | 98 | 98 | 98 | 98 | 98 | 92 | 44 | 22 | 67 | 97 | 98 |
| | after | 95 | 95 | 95 | 95 | 84 | 43 | 0 | 0 | 0 | 0 | 14 | 93 |
| 57N 150E, north basin | before | 98 | 98 | 98 | 98 | 98 | 94 | 39 | 3 | 1 | 8 | 81 | 97 |
| | after | 34 | 83 | 87 | 15 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| 55N 137E, Shantar corner | before | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| | after | 95 | 95 | 95 | 95 | 76 | 28 | 0 | 0 | 0 | 0 | 8 | 92 |
| 50N 146E, off Sakhalin | before | 80 | 90 | 91 | 83 | 58 | 12 | 0 | 0 | 0 | 0 | 3 | 37 |
| | after | 7 | 48 | 59 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 44.5N 144.5E, off Abashiri | before | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| | after | 6 | 44 | 55 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 51N 141E, Tatar Strait | before | 1 | 2 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| | after | 87 | 94 | 95 | 75 | 5 | 1 | 0 | 0 | 0 | 0 | 0 | 25 |
| 62N 168W, north Bering shelf | before | 3 | 8 | 9 | 4 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| | after | 92 | 94 | 95 | 94 | 22 | 0 | 0 | 0 | 0 | 0 | 0 | 16 |

Points 51N 157E (off south-west Kamchatka) and 48N 141E (south Tatar Strait)
are 0-1 % all year, before and after.

### Key dates in the new model

| | 1981_2010 | 2016_2025 | Reference |
|---|---|---|---|
| Ice (15 %) at 44.5N 144.5E, off Abashiri | 19 Jan to 11 Apr | 29 Jan to 29 Mar | about 22 Jan to early April (sources 7, 8; ESTIMATES) |
| Okhotsk extent below 100 thousand km2 | 12 Jun | 8 Jun | 6 Jun / 1 Jun (NSIDC daily) |
| Last Okhotsk ice | 13 Jul | 13 Jul | about 1-3 July below 50 thousand km2 (NSIDC daily) |
| Extent above 100 thousand km2 again | 23 Nov | 24 Nov | about 2 Dec (NSIDC daily) |

The model is about a week late in June and about a week early in November.
That comes from linear interpolation between mid-month targets.

### Mean concentration by part of the sea (%, baseline 2016_2025)

Targets are ESTIMATES from the research notes. They were scaled to NSIDC extent
and the literature's order. They add up to more ice than NSIDC's extent allows,
so the model cannot meet all of them. It keeps the order right and the extent
exact.

| Part | | Dec | Jan | Feb | Mar | Apr | May | Jun |
|---|---|---|---|---|---|---|---|---|
| NW shelf / Shantar (53-59N, west of 145E) | model | 52 | 84 | 94 | 94 | 77 | 34 | 14 |
| | estimate | 50-75 | 80-95 | 85-95 | 85-95 | 65-85 | 35-55 | 5-15 |
| North / Shelikhov (57N+, 145E+) | model | 17 | 46 | 73 | 79 | 38 | 6 | 1 |
| | estimate | 35-55 | 65-85 | 75-90 | 75-90 | 45-65 | 10-25 | 0-5 |
| East Sakhalin (48-54N, 142-148E) | model | 2 | 25 | 55 | 61 | 16 | 0 | 0 |
| | estimate | 10-30 | 55-80 | 75-90 | 75-90 | 35-60 | 5-20 | 0-5 |
| Central (50-57N, 148-156E) | model | 0 | 2 | 11 | 14 | 1 | 0 | 0 |
| | estimate | 5-15 | 25-45 | 50-70 | 50-70 | 15-35 | 0-5 | 0 |
| South, Hokkaido-Kurils (43-48N) | model | 0 | 4 | 22 | 28 | 2 | 0 | 0 |
| | estimate | 0 | 0-10 | 20-45 | 20-40 | 0-10 | 0 | 0 |
| Tatar Strait (48-52N) | model | 10 | 41 | 71 | 78 | 31 | 2 | 0 |
| | estimate | 15-35 | 55-80 | 65-85 | 55-80 | 10-30 | 0-5 | 0 |

July to October: 0 everywhere in the model and in the estimates. November: model
5 % on the NW shelf, 0 elsewhere (estimate 10-25 / 5-15 / 0).

The central basin is the weakest part. It is too open in winter.

## Proof that nothing else changed

Script: old `seaice.py` (git HEAD) against new, `ice_at` on a 0.5-degree global
grid. That is 144,000 points with |lat| >= 40, for the 15th of all 12 months, in
both baselines (24 dates). Result: 0 differences outside the two seas. The same
check on a 1-degree grid with `edges_on(res=2.0)` also gave 0 differences. The
hemispheric base edges are identical, bit for bit.

The test `test_other_regions_use_the_unchanged_hemispheric_model` repeats a small
version of this check on every test run.

## What it costs

The NSIDC hemispheric calibration is unchanged. `extent(h, edges[h])` still
matches the NSIDC hemispheric target, and those tests still pass.

But the ice that `ice_at` reports in the north now differs from that target by
the old model's error in these two seas. In million km2, baseline 2016_2025:

| | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NSIDC target | 13.50 | 14.30 | 14.50 | 13.75 | 12.55 | 10.70 | 7.85 | 5.45 | 4.65 | 6.25 | 9.45 | 11.85 |
| ice_at total | 13.59 | 14.62 | 14.84 | 13.70 | 12.09 | 10.29 | 7.59 | 5.39 | 4.62 | 6.12 | 9.10 | 11.63 |

The gap is at most 0.46 million km2 (May). Removing it would mean moving the
edge in every other Arctic region. That would break "keep every other region
unchanged". It is left for a later change, if wanted.

## Limits

- The `s` field is a hand-fitted shape. It is not data.
- The regional edge is solved on 1-degree cells. `edges_on(res=...)` calibrates
  only the hemispheric edge for the game grid, not the regional one.
- Cells just outside the NSIDC region still use the old shape. The sampled
  Pacific points east of the Kurils and Kamchatka have 0-6 % in winter.
- The Bering shape is rough. Near St Matthew Island (60N 175W) it gives only
  5 % in March (2016_2025). Recent Bering winters were very low (2018, 2019).
- Interpolating between mid-month targets makes melt-out about a week late.
- One test outside `test_seaice.py` changed: `test_procedural_v5` checked 52N
  150E > 50 % in March. In the new model that point is open, because NSIDC's
  March extent is spent on the north, Sakhalin and Hokkaido first. The test now
  checks 57N 145E.

## Battle runtime (C# port on origin/feature/mno-r16)

`integration/beta-feature-parity/runtime/SeaIceModel.cs` on that branch ports
`seaice.py`. `SeaIceData.g.cs` holds the per-date edges. The generator
`tools/make_sea_ice_data.py` writes it and stamps the SHA-256 of `seaice.py`.
Any change to `seaice.py` makes the port stale. It must be regenerated with that
branch's `tools/make_sea_ice_data.py`.

The old generator cannot do this alone. It passes edges without the new
`"marginal"` entry, and the C# port has no marginal-sea code. So a regenerated
set, with small patches to the generator, the Python mirror and
`SeaIceModel.cs`, is in
`integration/environment/handoff/r16-sea-ice/`. Its README says how to apply it.
