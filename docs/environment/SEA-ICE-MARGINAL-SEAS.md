# Sea ice in the Sea of Okhotsk, the Bering Sea and the Chukchi Sea

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

A first fix (regional calibration of Okhotsk and Bering) had three faults of its own.
This version fixes them:

- **Wrong melt-out order in Okhotsk.** The hand-fitted order field let the north
  coast off Okhotsk town keep ice longest: 63 % at 59N 143.5E on 20 June, 39 % on
  1 July. The Shantar corner had only 8 % on 1 July. Observed, it is the other way
  round. The order field is now fitted to NSIDC maps (below).
- **A seam at Bering Strait.** The Bering side read 95 % in January to April. The
  Chukchi side, still on the hemispheric model, read 9-58 %. NSIDC has the Chukchi
  Sea fully ice-covered from December to April. The Chukchi Sea now has its own
  calibration too.
- **The Okhotsk March edge was not checked against an edge map.** It is now
  checked against the NSIDC 1981-2010 median ice edge.

## Reference data

All numbers below come from these sources. Estimates are marked.

1. NSIDC Sea Ice Index G02135 v4.0, regional monthly extent. File
   `N_Sea_Ice_Index_Regional_Monthly_Data_G02135_v4.0.xlsx` from
   <https://noaadata.apps.nsidc.org/NOAA/G02135/seaice_analysis/>. Downloaded
   2026-11-24. SHA-256
   `557eed67f84961fb017827b23c88aceeb6fc9bd5a33fe5e4f8078d860c9db084`.
   Regions are those of Meier, Stroeve and Fetterer (2007), "Whither Arctic sea
   ice? A clear signal of decline regionally, seasonally and extending beyond the
   satellite record", Annals of Glaciology 46:428-434. NSIDC's "Okhotsk" region
   includes the Sea of Japan and the Tatar Strait.
2. The daily file from the same folder,
   `N_Sea_Ice_Index_Regional_Daily_Data_G02135_v4.0.xlsx`, SHA-256
   `eaad90ba809b634b9bcc5baad09b15528e709e962c81fd4ea1f84c7fcbc0d315`. Used only
   for the key dates below.
3. The region mask, from the same folder:
   <https://noaadata.apps.nsidc.org/NOAA/G02135/seaice_analysis/Arctic_region_mask_Meier_AnnGlaciol2007.txt>.
   SHA-256 `56afd20963c5dd5f424a9ab4ba812e87b6a0ef1993eb67af1aedf42add4ac26e`.
   Codes used: 2 = Okhotsk and Japan, 3 = Bering, 12 = Chukchi.
4. NSIDC G02135 v4.0 monthly extent polygons for 2016-2025, every month:
   `north/monthly/shapefiles/shp_extent/MM_Mon/extent_N_YYYYMM_polygon_v4.0.zip`
   under <https://noaadata.apps.nsidc.org/NOAA/G02135/>. Downloaded 2026-11-24.
   For each 1-degree cell, the number of years (of 10) with 15 % or more in each
   month. Used to fit and check the order fields.
5. NSIDC G02135 v4.0 median ice edge, 1981-2010:
   `north/monthly/shapefiles/shp_median/median_extent_N_MM_1981-2010_polyline_v4.0.zip`
   (same host). Downloaded 2026-11-24. Used to check the Okhotsk March edge.
6. Kimura and Wakatsuchi (1999), J. Geophys. Res. 104(C5): 11137. Ice forms first
   on the north-west shelf and spreads east and south, mainly by wind drift. The
   north coast clears early.
7. Japan Meteorological Agency (JMA), Abashiri Local Meteorological Observatory.
   First drift ice (流氷初日): normal 22 January (1991-2020), 21 January
   (1981-2010). File `seaice_report2025-1.pdf` at
   data.jma.go.jp/abashiri/shosai/seaice_report/.
8. JMA Abashiri, `news20210326_seaice_umiake.pdf` at jma-net.go.jp/abashiri/news/.
   Last ice (流氷終日): normal 11 April (1981-2010). Sea opening (海明け): normal
   20 March (1981-2010). A secondary source quotes 6 April for 1991-2020.
9. Britannica, "Sea of Okhotsk", climate section. Floes stay into July, and
   sometimes August, "in the Sakhalin gulfs and around Shantar Island". The rest
   of the sea is clear by June. A secondary source.

Sources 7 to 9 were named by a review of this work. Their hosts are blocked in
this session, so they were not re-read here. Confidence: medium. The model agrees
with them (see "Key dates").

An earlier version also cited "Rikiishi and Takatsuji, Annals of Glaciology" for an
ice-edge speed of 35 cm/s, and an "Annals of Glaciology (1990)" paper. Neither
citation was complete and neither number drives the model. Both were dropped.

### NSIDC monthly median extent (thousand km2)

| Region, years | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Okhotsk 2016-2025 | 670 | 1005 | 1055 | 551 | 171 | 75 | 0 | 0 | 0 | 44 | 67 | 282 |
| Okhotsk 1981-2010 | 778 | 1101 | 1092 | 788 | 233 | 83 | 0 | 0 | 0 | 37 | 66 | 300 |
| Bering 2016-2025 | 469 | 583 | 622 | 542 | 212 | 34 | 3 | 0 | 1 | 12 | 37 | 181 |
| Bering 1981-2010 | 609 | 709 | 767 | 663 | 345 | 55 | 4 | 0 | 2 | 17 | 85 | 318 |
| Chukchi 2016-2025 | 830 | 830 | 830 | 830 | 811 | 681 | 494 | 191 | 49 | 177 | 454 | 766 |
| Chukchi 1981-2010 | 830 | 830 | 830 | 830 | 824 | 744 | 572 | 419 | 352 | 438 | 658 | 830 |

These are medians of each month over the years. The code stores them to one
decimal (`NSIDC_REGIONAL_MEDIAN_KKM2`). 830 thousand km2 is the whole Chukchi
region: it is full every January to April.

Key dates from the daily file (median over years, Okhotsk):

- Maximum: about 6-8 March.
- Extent below 100 thousand km2: about 1 June (2016-2025) or 6 June (1981-2010).
- Extent below 50 thousand km2: about 1-2 July.
- Extent above 100 thousand km2 again: about 2 December.

### Corrections to the targets (ESTIMATES)

For Okhotsk and Bering only:

1. July to October are set to 0. In every recent year the NSIDC regional series
   is exactly 0 from about 1-3 July to 1 October. That looks like NSIDC's
   valid-ice mask, so the exact July date is partly an artefact.
2. The October value (10-50 thousand km2) is nearly the same every year. It looks
   like coastal land spill-over, not ice. It is set to 0, and the same amount is
   taken off November.

The Chukchi Sea has real summer ice. Its targets are used as published. They are
used as a fraction of the full region (830.3 thousand km2). The model's 1-degree
cells hold about 834 thousand km2. Without the fraction, the model would have to
leave about 4 thousand km2 open in midwinter. It would open the cells next to
Bering Strait.

## How the model works

Inside each of the three seas the model has its own edge.

- A fixed "ice order" field `s(lat, lon)` ranks where ice forms first and melts
  last. Its terms are physical. Their sizes are fitted to NSIDC maps (source 4).
- Concentration is a logistic in `s`. It is exactly 15 % at the regional edge. It
  reaches 90 % about 2.3 units inside it. Pack concentration is capped at 95 %
  for polynyas (estimate).
- For each date the regional edge is solved so that the sea's extent matches the
  NSIDC regional target. Extent means 1-degree ocean cells with 15 % or more,
  the same rule as the hemispheric model. Targets are interpolated between
  mid-month values, like the hemispheric ones.
- The seas are the 1-degree cells that fall in, or within about 75 km of, the
  NSIDC region mask (`_MARGINAL_ROWS`).

### Sea of Okhotsk order field

`s = lat - 0.35 (lon - 140)`, plus:

- Shantar Islands and Sakhalin Gulf: +3.0 at 54.5N 139.7E (widths 0.8 degrees of
  latitude, 2.5 of longitude). NSIDC: June ice there in 5-9 of 10 years.
- Shelikhov Gulf: +4.0 at 61.5N 162.5E. NSIDC: June ice in 8-10 of 10 years.
- North coast off Okhotsk town: -2.5 north of about 57-58N, centred on 143E. NSIDC:
  no June ice at 57-59N 138-146E in 2016-2025.
- A tongue of ice along east Sakhalin to Hokkaido:
  `s = 52.9 + 0.3 (lat - 44.5) - ((lon - 143.6) / 2.5)^2` there.
- Only the northern Tatar Strait freezes. Ice stops near 48N. (Estimate of
  47-48N. No edge-latitude source was found.) The rest of the Sea of Japan stays
  open.

How it was fitted: for each month December to June, the model's 15 % cells were
compared with the cells NSIDC has iced in at least 5 of 10 years. The mismatch
area was made as small as possible. June counted 6 times and May twice, so the
melt-out order mattered most. Summed over those months, the mismatch fell from
2,358 thousand km2 (old hand-fitted field) to 1,413.

### Bering Sea order field

`s = lat + 0.235 x (degrees east of 180) + 0.12 x (degrees west of 180)`. Ice
forms first in Norton Sound, near Bering Strait and in the Gulf of Anadyr. The deep
Aleutian Basin stays open. This shape is fitted by eye to NSIDC/NIC maps. It is
not data. It was not refitted in this version.

### Chukchi Sea order field

`s = lat - 0.05 (lon + 160)`. The ice retreats north in summer and comes back from
the north in autumn. The west (Wrangel Island side) keeps it slightly longer.

Checked against the NSIDC polygons for May to December. Latitude alone fits about
as well (mismatch 497 against 517 thousand km2). But with latitude alone whole rows
of cells share one value, so the solved extent missed its target by up to 42
thousand km2. The small west term (an estimate) brings that under 4. A Bering
Strait term made the fit worse.

### Everything else

The hemispheric edge is solved exactly as before. So every cell outside the three
seas is unchanged. A test pins this with golden values taken from `seaice.py`
before any regional calibration (see "Proof").

There is no on/off switch. This corrects the existing default climatology. It
adds no new game feature.

## Results

All values are for the 15th of the month, 12:00 UTC.

### Regional extent (thousand km2, cells of the NSIDC region)

Baseline 2016_2025:

| | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Okhotsk, old model | 906 | 1021 | 1049 | 930 | 791 | 516 | 256 | 78 | 32 | 131 | 412 | 695 |
| Okhotsk, now | 677 | 1006 | 1043 | 547 | 167 | 75 | 0 | 0 | 0 | 0 | 27 | 291 |
| Okhotsk NSIDC | 670 | 1005 | 1055 | 551 | 171 | 75 | 0 | 0 | 0 | 44 | 67 | 282 |
| Bering, old model | 156 | 257 | 274 | 194 | 48 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Bering, now | 473 | 584 | 621 | 535 | 212 | 37 | 0 | 0 | 0 | 0 | 31 | 184 |
| Bering NSIDC | 469 | 583 | 622 | 542 | 212 | 34 | 3 | 0 | 1 | 12 | 37 | 181 |
| Chukchi, now | 834 | 834 | 834 | 834 | 814 | 683 | 492 | 192 | 49 | 180 | 461 | 771 |
| Chukchi NSIDC | 830 | 830 | 830 | 830 | 811 | 681 | 494 | 191 | 49 | 177 | 454 | 766 |

Baseline 1981_2010:

| | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Okhotsk, old model | 1043 | 1182 | 1188 | 1067 | 882 | 679 | 412 | 242 | 173 | 327 | 559 | 816 |
| Okhotsk, now | 789 | 1101 | 1087 | 780 | 229 | 82 | 0 | 0 | 0 | 0 | 34 | 304 |
| Okhotsk NSIDC | 778 | 1101 | 1092 | 788 | 233 | 83 | 0 | 0 | 0 | 37 | 66 | 300 |
| Bering, old model | 274 | 402 | 426 | 314 | 119 | 0 | 0 | 0 | 0 | 0 | 0 | 92 |
| Bering, now | 609 | 709 | 766 | 658 | 339 | 53 | 0 | 0 | 0 | 0 | 69 | 321 |
| Bering NSIDC | 609 | 709 | 767 | 663 | 345 | 55 | 4 | 0 | 2 | 17 | 85 | 318 |
| Chukchi, now | 834 | 834 | 834 | 834 | 829 | 742 | 572 | 423 | 357 | 445 | 661 | 834 |
| Chukchi NSIDC | 830 | 830 | 830 | 830 | 824 | 744 | 572 | 419 | 352 | 438 | 658 | 830 |

October and November Okhotsk and Bering are below NSIDC on purpose (correction 2).
Chukchi is about 0.5 % above NSIDC because its cells hold 834, not 830, thousand km2.

### Concentration at points (%, baseline 2016_2025)

| Point | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 59N 145E, north coast | 81 | 94 | 94 | 63 | 5 | 1 | 0 | 0 | 0 | 0 | 0 | 18 |
| 59N 143.5E, off Okhotsk town | 88 | 94 | 95 | 78 | 10 | 2 | 0 | 0 | 0 | 0 | 0 | 34 |
| 57N 150E, north basin | 11 | 61 | 73 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 55N 137E, Shantar corner | 95 | 95 | 95 | 94 | 70 | 25 | 0 | 0 | 0 | 0 | 8 | 88 |
| 54N 141.5E, Sakhalin Gulf | 84 | 94 | 95 | 69 | 6 | 1 | 0 | 0 | 0 | 0 | 0 | 23 |
| 61.5N 162.5E, Shelikhov Gulf | 95 | 95 | 95 | 95 | 91 | 71 | 0 | 0 | 0 | 0 | 39 | 94 |
| 52N 150E, central basin | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 50N 146E, off Sakhalin | 24 | 78 | 85 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| 44.5N 144.5E, off Abashiri | 4 | 39 | 53 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 51N 141E, Tatar Strait | 83 | 94 | 94 | 67 | 6 | 1 | 0 | 0 | 0 | 0 | 0 | 21 |
| 62N 168W, north Bering shelf | 92 | 94 | 95 | 94 | 22 | 0 | 0 | 0 | 0 | 0 | 0 | 16 |
| 66.5N 169W, Chukchi side of Bering Strait | 95 | 95 | 95 | 95 | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| 68N 168W, southern Chukchi | 95 | 95 | 95 | 95 | 81 | 2 | 0 | 0 | 0 | 0 | 0 | 33 |
| 72N 165W, northern Chukchi | 95 | 95 | 95 | 95 | 95 | 94 | 31 | 0 | 0 | 0 | 16 | 95 |

52N 150E is open all year. That matches the maps. In March 2016-2025, NSIDC has it
iced in only 2-3 of 10 years. The 1981-2010 median edge also lies north of it
(next section).

### Okhotsk March edge against the NSIDC median edge

Latitude where the 15 % line crosses each meridian, mid-March, baseline 1981_2010:

| Meridian | NSIDC median edge 1981-2010 (source 5) | Model now | Old regional model |
|---|---|---|---|
| 150E | 54.8N | 55.1N | 53.0N |
| 152E | 55.8N | 55.8N | 55.0N |
| 154.5E | 57.5N | 56.7N | 56.5N |

A test checks each crossing is within 1.5 degrees of the median edge.

### Key dates

| | 1981_2010 | 2016_2025 | Reference |
|---|---|---|---|
| Ice (15 %) at 44.5N 144.5E, off Abashiri | about 24 Jan to 8 Apr | about 1 Feb to 27 Mar | JMA normals: first ice 21-22 Jan, last ice 11 Apr (1981-2010) (sources 7, 8) |
| Okhotsk extent below 100 thousand km2 | 11 Jun | 7 Jun | 6 Jun / 1 Jun (NSIDC daily) |
| Last Okhotsk ice | 14 Jul | 14 Jul | about 1-3 July below 50 thousand km2 (NSIDC daily) |
| Extent above 100 thousand km2 again | 23 Nov | 24 Nov | about 2 Dec (NSIDC daily) |

The Abashiri dates were found in 2-day steps. The model is about a week late in June
and about a week early in November. That comes from linear interpolation between
mid-month targets.

## Proof that nothing else changed

`tests/fixtures/seaice-hemispheric-golden.json` holds golden values from `seaice.py`
before any regional calibration (git commit `ecdc78341`). It has the hemispheric
edges for the 15th of all 12 months and `ice_at` at 201 points outside the three
seas. The test `test_other_regions_use_the_unchanged_hemispheric_model` asserts
exact equality. It would fail if `base_edge_for`, `target_extent` or `edge_shape`
changed.

## What it costs

The NSIDC hemispheric calibration is unchanged. `extent(h, edges[h])` still
matches the NSIDC hemispheric target.

But the ice that `ice_at` reports in the north now differs from that target by the
old model's error in these three seas. In million km2, baseline 2016_2025:

| | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NSIDC target | 13.50 | 14.30 | 14.50 | 13.75 | 12.55 | 10.70 | 7.85 | 5.45 | 4.65 | 6.25 | 9.45 | 11.85 |
| ice_at total | 13.69 | 14.62 | 14.84 | 13.75 | 12.23 | 10.44 | 7.80 | 5.48 | 4.63 | 6.14 | 9.11 | 11.76 |

The gap is at most 0.34 million km2 (March). Removing it would mean moving the
edge in every other Arctic region. That would break "keep every other region
unchanged". It is left for a later change, if wanted.

## Limits

- The order fields are physical shapes with fitted sizes. They are not data.
- The regional edges are solved on 1-degree cells. `edges_on(res=...)` calibrates
  only the hemispheric edges for the game grid, not the regional ones.
- Cells just outside the NSIDC regions still use the old shape. The sampled
  Pacific points east of the Kurils and Kamchatka have 0-6 % in winter.
- The Bering shape is rough. Near St Matthew Island (60N 175W) it gives only
  5 % in March (2016_2025). Recent Bering winters were very low (2018, 2019).
- **New seams.** The Chukchi Sea now borders the hemispheric model on its west
  (East Siberian Sea, along about 180) and east (Beaufort Sea, about 155W) sides.
  The hemispheric model is too light near those coasts in winter. Largest step
  between neighbouring 0.5-degree points, baseline 2016_2025: about 52 points in
  January near 69N 180 (26-48 in February to April), and 56-87 points along the
  western border in June to November.
- **Bering Strait in May and December.** January to April the strait is smooth. In
  May and December the Chukchi side opens first at the strait (2-20 % at 65.5-66.5N
  170.5W) while the Bering side still reads about 95 %. The largest step is about
  95 points at 65.5N 168W. NSIDC has both sides iced in most years then. This comes
  from calibrating each sea to its own extent alone.
- Interpolating between mid-month targets makes melt-out about a week late.
- `test_procedural_v5` checks 57N 145E > 50 % in March, and 52N 150E < 15 %. The
  second matches the NSIDC median edge.

## Battle runtime (C# port on origin/feature/mno-r16)

`integration/beta-feature-parity/runtime/SeaIceModel.cs` on that branch ports
`seaice.py`. `SeaIceData.g.cs` holds the per-date edges. The generator
`tools/make_sea_ice_data.py` writes it and stamps the SHA-256 of `seaice.py`.
Any change to `seaice.py` makes the port stale. It must be regenerated.

The old generator cannot do this alone. It passes edges without the
`"marginal"` entry, and the C# port has no marginal-sea code. So a regenerated
set, with small patches to the generator, the Python mirror and
`SeaIceModel.cs`, is in `integration/environment/handoff/r16-sea-ice/`. Its
README says how to apply it. `tests/test_handoff_r16_sea_ice.py` fails as soon
as a source the hand-off was made from changes, and says how to regenerate it.
