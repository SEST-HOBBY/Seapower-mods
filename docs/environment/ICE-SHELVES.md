# Ice shelves: attributes, fronts, navigation and sensors

Status: BUILD-TESTED (offline). Not loaded by the game. OFF by default.

Files:

- `integration/environment/mno_env/iceshelves.py`: the code.
- `integration/environment/data/ice-shelf-attributes.json`: every number, each with a source and a confidence.
- `integration/environment/data/ice-shelf-fronts-naturalearth-10m.json`: the shelf fronts (Natural Earth, public domain).
- `integration/environment/tools/convert_ice_shelf_fronts.py`: makes the fronts file from the Natural Earth download.
- `integration/environment/tests/test_ice_shelves.py`: the tests.

`mno_env/ice.py` changed in two small ways. Each shelf now records its feature number in the source file. And `ice.shelf_at`, `ice.distance_to_front_nm`, `ice.front_cliff` and `ice.shelf_navigation` now point to the new module. `routes.py` is unchanged. A route is still blocked only where it enters a shelf polygon.

## What it does

- `shelf_at(lat, lon)` gives the shelf at a point and its attributes. It gives `None` for open water, land, or an island or ice rise inside a shelf.
- `distance_to_front_nm(lat, lon)` gives the great-circle distance to the nearest front segment.
- `front_cliff(lat, lon)` gives the cliff height above water (freeboard) and the draft of the nearest front. Each has a range, a typical value, a basis and a confidence.
- `shelf_navigation(lat, lon, platform)` applies the game rule for a `surface` ship or a `submarine`.
- `shelf_events(lat, lon)` lists dated calvings and collapses. It also says whether the map still shows the lost ice.
- `point_features_near(lat, lon, radius_nm)` lists shelves and ice tongues that have no outline (most of the Arctic ones).
- `front_sensor_notes(lat, lon)` gives radar, sonar and weather notes for the nearest front.
- `unattributed_shelves()` lists the Natural Earth shelves that have no attributes yet.

## How much to trust it

Read this before you use the numbers.

- **Outlines: good enough for game rules.** They are Natural Earth 1:10m. That is a map, not a survey. The fronts date from about 2003 to 2012. This date range is an estimate. Natural Earth does not publish a date for each front.
- **Fronts: good.** They are Natural Earth's own "ice shelf edge" lines, from the same dataset as the polygons. The tests check that the Ross front lies at 77-79 S, not at the grounding line far to the south.
- **Areas: mixed.** Some come from Rignot et al. (2013), Table 1, but only through search snippets. Others come from secondary sources and are marked `low`.
- **Freeboard: one measurement.** Only the Ross cliff height is measured (15-50 m). Other freeboards are worked out from ice thickness. They are marked `estimate`.
- **Draft: all estimates.** Each draft is worked out from a thickness or a freeboard.
- **Water depth at the front: unknown.** It needs BedMachine Antarctica (NSIDC-0756), which was not read. The code gives only a lower bound: a floating front always has water deeper than its draft.
- **Stand-off distances: estimates.** No official figure was found.

## How freeboard and draft are worked out

An ice shelf floats. So its thickness sets its height above water and its depth below.

- Ice density is 917 kg/m3 and sea-water density is 1027 kg/m3 (BedMachine, Morlighem 2020, doi:10.5067/E1QL9HFQ7A8M).
- So solid ice shows 1 - 917/1027 = 10.7% of its thickness above water.
- Snow and firn on top make the shelf lighter. So the share can be higher. We use 10.7% to 15%. The 15% is a judgement.
- Draft is the rest: 85% to 89.3% of the thickness.
- Ranges are rounded outward to 5 m. That avoids false precision.

Example: 300 m of ice gives about 30-45 m of cliff and about 255-270 m of draft.

The "generic front" is used where a shelf has no value. Its thickness range is 150-325 m. That range spans the sourced fronts: Filchner 150-220 m, A68 235 m, Brunt 150 m, Abbot 200-325 m, Drygalski 300 m, and Ross and Amery under 300 m. It gives a cliff of 15-50 m (typical 30 m) and a draft of 125-295 m (typical 220 m). This matches the measured Ross cliff.

## Shelves with attributes

Areas marked "computed" are measured on the Natural Earth polygon by this code. They are not survey values.

| Shelf | Area (source) | Front cliff / draft | Dated events |
|---|---|---|---|
| Ross | about 500,800 km2 (Rignot 2013, medium) | cliff 15-50 m, typical 20-40 m (USGS, measured); draft 110-270 m (estimate) | B-15, March 2000, about 11,000 km2 |
| Filchner | about 430,000 km2 with Ronne (Wikipedia, medium) | thickness 150-220 m (1981 survey); cliff 15-35 m, draft 125-200 m (estimates) | A23a, August 1986, about 3,900-4,000 km2 |
| Ronne | with Filchner | no values | A-76, May 2021, 4,320 km2 |
| Larsen (C and D) | Larsen C 46,465 km2 before A68 (Rignot 2013) | thickness 235 +/- 9 m (A68); cliff 20-40 m, draft 190-220 m (estimates) | A68, 12 July 2017, about 5,800 km2 |
| Larsen B remnant | 11,512 km2 in 1995, 3,463 km2 in 2002 (secondary) | no values | collapse, 31 Jan to March 2002, about 3,250 km2 of 220 m ice |
| Larsen A remnant (by location) | largest past extent 2,500 km2 (low) | no values | disintegration, January 1995, about 1,600 km2 |
| Conger(-Glenzer) (by location) | 1,200 km2 lost (WHOI) | no values | collapse, about 15 March 2022 |
| Wilkins | about 16,577 km2 (low) | no values | break-ups 28 Feb 2008 (NASA) or March 2008 (BAS); 2009 |
| Riiser-Larsen with Brunt and Stancomb-Wills | Riiser-Larsen 48,180 km2 (low) | Brunt: 150 m thick (A81) | A74, February 2021, 1,270 km2; A81, 22 Jan 2023, 1,550 km2 |
| Nansen (by location) | about 50 by 35 km (NASA) | no values | calving 7 April 2016 (larger berg C33) |
| Pine Island (by location) | no sourced area | no values | calving 9 Feb 2020, about 300-350 km2 (B-49) |
| George VI (by location) | 23,434 km2 (Rignot 2013) | no values | none listed |
| Amery | 62,000-71,300 km2 (USGS) | under 300 m thick at the front; cliff up to about 45 m, draft up to about 270 m (estimates) | none listed |
| Getz | 34,018 km2 (Rignot 2013) | no values | none listed |
| Abbot (Natural Earth spells it Abbott) | about 30,000 km2 (Cochran 2014) | 200-325 m thick; cliff 20-50 m, draft 170-295 m (estimates) | none listed |
| Shackleton | 33,820 km2 (low) | no values | none listed |
| West | 16,370 km2 (low) | no values | none listed |
| Fimbul | 41,060 km2 (low; polygon is about 30,000 km2) | no values | none listed |
| Sulzberger | no sourced area | no values | none listed |
| Thwaites Glacier Tongue | no sourced numbers | no values | none listed |

"By location" means Natural Earth leaves the polygon unnamed. We matched it by its position. That match is marked `low` (George VI is `medium`, because its area also fits).

### Does the map still show the lost ice?

Each event gets a status:

- `after`: the map already shows the shelf after the loss. Examples: B-15 (2000) and Larsen B (the polygon is the small remnant).
- `before`: the map still shows ice that has gone. Examples: A-76 (2021), Brunt A74 and A81, Nansen 2016, Pine Island 2020, and the Conger collapse (2022). The Conger polygon is still drawn. A game that wants today's ice should treat that area as open water or fast ice.
- `unknown`: the event falls inside the 2003-2012 map epoch. Examples: Wilkins 2008 and A68 2017. We had no A68 outline to test against. So the northern Larsen C front may be wrong by up to the size of A68.

### Natural Earth shelves with no attributes

These named shelves have no attributes yet. They use the generic front.

Cook, Dibble Iceberg Tongue, Dotson, Ekström, Jelbart, Lazarev, Mertz Glacier Tongue, Moscow University, Nimis Glacier Tongue, Rennick Glacier, Stange, Totten Glacier, Venable, Voyeykov.

123 unnamed polygons also have no attributes. `unattributed_shelves()` gives the current list.

## Arctic shelves and tongues: points only

No citable outline was at hand for these. So they are listed as points, not polygons. Points never block a route. Their positions are approximate and marked `low`.

| Feature | What is known | Source |
|---|---|---|
| Ellesmere Island ice shelves | about 8,600 km2 around 1900; 563 km2 at the end of 2011 (54% less than in 2005); 535 km2 by 2015. No total after the July 2020 Milne calving was found. Taking off the Milne loss of about 80 km2 gives about 455 km2 (estimate). | ECCC; Carleton University WIRL |
| Milne | 30-31 July 2020: 187 to 106 km2 (about 43% lost); pieces of 55 and 24 km2; drained the last known epishelf lake in the Northern Hemisphere | Carleton University; ECCC |
| Ward Hunt | lost 45% of its area in 2008-2010; split in 2011, losing 39 km2; no sourced thickness | Carleton WIRL; Copland et al. |
| Petersen | lost over 60% of its area from 2003 to 2015; 12.6 km2 calved in August 2005 | Ann. Glaciol. |
| Smith | no data found; listed so the gap shows | none |
| Petermann Glacier tongue (Greenland) | 81 km long, then about 46-48 km after the 2010 and 2012 calvings; 2010 berg about 250-275 km2 (253 +/- 17 km2, Falkner et al. 2011, Eos; 275 km2, EGU2011-10857 abstract; medium confidence); mean 300 m thick; grounded about 600 m below sea level | Muenchow et al. 2014, J. Glaciol.; Falkner et al. 2011; EGU2011-10857 |
| 79N Glacier tongue (Greenland) | about 70-80 km long and 20 km wide; 80-100 m thick near the front; cliff about 8-15 m and draft about 65-90 m (estimates from 80-100 m thickness) | The Cryosphere 17:2851 (2023) |
| Drygalski Ice Tongue (Antarctica) | not in the Natural Earth file; about 300 m thick over its last 55 km; 80-140 km long, depending on epoch | J. Glaciol.; Ann. Glaciol. |

## Navigation rule

These are game rules. They are not navigation advice.

- **Surface ships never enter a shelf.** The front is a cliff. There is no way in.
- **Surface ships get a caution within 2 nm of a front.** Calving and capsizing bergs are the hazard. Growlers (under 1 m high) and bergy bits (1-5 m high) gather there (Bowditch, ch. 32). The 2 nm is an estimate: the top of a 1-2 nm judgement. No official figure was found.
- **Submarines never enter the cavity under a shelf.** The water under the shelf thins to nothing at the grounding line (BedMachine). There is no GNSS, no radio and no way to surface. The ice base is rough. The Ran research robot went over 1,000 km under ice and 17 km into a cavity. It was lost under the ice in 2024 (University of East Anglia).
- **Submarines keep 2 nm from a front.** Inside 2 nm the rule says "blocked". The front draft is about 125-295 m, so the ice face reaches normal submarine depths. Calved bergs nearby have drafts of the same order. The 2 nm is an estimate.

Charting: S-57 has no ice-shelf object. A shelf charts as ICEARE (code 66) with CATICE 5, "glacier", plus the ice-front line (IHO S-57 Ed 3.1). The paper-chart symbol is INT1 N60.1, the black ice front (IHO S-4 B-353.8).

## Sensor notes

Radar:

- A 20-50 m ice cliff gives a strong, large, land-like return. The face toward the radar is bright in radar images (ESA). Ships have long fixed the Ross front by radar range and bearing (J. Glaciol.).
- The detection range for a cliff is set by the radar horizon. A 25 m antenna and a 30 m cliff give about 23 nm (4/3 Earth radius; estimate).
- Small ice is the real danger. On normal marine radar a growler may show at about 0.5 nm, or not at all. In heavy seas it is lost in clutter (Canadian Coast Guard).

Sonar:

- An ice face reflects sound strongly. From the density and sound-speed contrast, about 40% of the pressure comes back at normal incidence, about -8 dB. This is an estimate. A rough face scatters much of it.
- Calving is loud. At a Greenland glacier a calving gave 225 +/- 10 dB re 1 uPa peak-to-peak, and at least 215 dB at Bowdoin Glacier (DOSITS 2022; JASA 2022).
- A large berg breaking up radiates about 220 dB re 1 uPa at 1 m, at 1-440 Hz (Dziak et al. 2013, Oceanography 26(2)).
- Ice cracking and bubble release raise the noise near fronts. Levels of 120-140 dB re 1 uPa2/Hz below 200 Hz are reported near glacier fronts (JASA 2022).

Weather:

- Katabatic winds pour off the ice. In Terra Nova Bay they reach over 20-35 m/s with air below -25 C. Off the Nansen edge the wind falls from 35 to 18 m/s over 99 km (NSF PAR 10372596).
- Over the open water of a polynya the heat flux reaches 2,000 W/m2. So sea smoke is likely. No fog climatology was found; this is an estimate.

## Datasets for a later upgrade

- **MEaSUREs Antarctic Boundaries v2 (NSIDC-0709).** Grounding line, shelf mask and fronts of 2007-2009. No use restrictions; cite doi:10.5067/AXE4121732AD.
- **SCAR Antarctic Digital Database v7.x.** The most current fronts. CC BY 4.0.
- **Greene et al. 2022 (Nature 609:948).** Yearly fronts 1997-2021, doi:10.5281/zenodo.5903643. Shelves lost 36,701 +/- 1,465 km2 (1.9%) in that time. Check the licence first.
- **Andreasen, Hogg and Selley 2023 (The Cryosphere 17:2059).** Fronts of 34 shelves, 2009-2019. Net change +5,305 km2.
- **BedMachine Antarctica (NSIDC-0756).** Thickness, draft and sea-floor depth. This would fill the water depth at each front.

Keep Natural Earth as the shipped default, because it is public domain. Stamp any newer front with its date.

## Gaps

- The full Rignot et al. (2013) Table 1. escholarship.org was blocked in this session.
- Sulzberger area, Ward Hunt thickness, Larsen C measured freeboard, Thwaites numbers, and the Smith Ice Shelf.
- Water depth at every front (BedMachine).
- An A68 outline, to test whether the Larsen C front predates it.
- The research tied berg D15A to the West Ice Shelf in 2016. That could not be confirmed, so it is left out.

## Rebuild the fronts file

1. Download `ne_10m_antarctic_ice_shelves_lines.geojson` from the natural-earth-vector repository.
2. Run `python3 tools/convert_ice_shelf_fronts.py PATH --downloaded-utc YYYY-MM-DDTHH:MM:SSZ` from `integration/environment`.

The tool works offline. It drops the closed rings around ice rises and islands, because their edge is grounded ice, not a front. It tags each segment with the polygon it lies on. The bundled file came from a download on 2026-11-24 (sha256 `0106dc9d...`, full value in the file).

## Tests

Run from `integration/environment`:

```
python3 -m unittest discover -s tests -t tests
```

`test_ice_shelves.py` checks that:

- every number has a source and a confidence, or a stated gap;
- worked-out freeboards and drafts follow the hydrostatic rule;
- every entry matches a Natural Earth name, and each unnamed match point falls in exactly one polygon;
- the Ross and Amery fronts lie at the seaward edge;
- the front distance matches dense sampling of the front lines;
- the dated-event status is right for B-15, Larsen B, Conger, A-76 and A68;
- the navigation rule blocks or cautions as described;
- the radar horizon and sonar reflection match the research figures;
- `routes.py` behaves as before.
