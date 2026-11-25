# Iceberg climatology and generator

Status: BUILD-TESTED (offline). Not loaded by the game. OFF by default.

Files:

- `integration/environment/mno_env/icebergs.py`: the code.
- `integration/environment/data/iceberg-climatology.json`: every number, each with a source and a confidence.
- `integration/environment/tests/test_icebergs.py`: the tests.

## What it does

- `density(lat, lon, month)` gives bergs per 10,000 km2 of water for each size class.
- `generate(bbox, when, seed)` gives a repeatable list of bergs for an area and a date.
- Each berg has a class, length, width, height, draft, mass, position and drift.
- With a sea temperature, each berg also gets its expected remaining life.
- Sensor hooks give radar range, visual range and a sonar false-contact index.

## How much to trust it

Read this before you use the numbers.

- **Size classes: medium confidence.** They are the IIP scale (NOAA JetStream). The source page could not be re-read this session.
- **North Atlantic season: medium confidence for February to July.** It comes from IIP counts of bergs crossing 48N. The IIP report was not re-read this session.
- **Densities: estimates.** We found no citable table of bergs per area. Each density is an order of magnitude only. The JSON says `estimate` next to each one.
- **Melt formula: medium confidence.** It is the Martin and Adcroft (2010) form of the Bigg et al. (1997) scheme. The coefficients are recalled. They were not re-checked against the papers this session.
- **Sensor numbers: mixed.** The growler radar range is sourced. Most of the rest are estimates.

## Size classes

The classes are the International Ice Patrol (IIP) scale, as NOAA JetStream gives it (https://www.noaa.gov/jetstream/icebergs-max). Growler and bergy bit sizes are also in ECCC MANICE chapter 1.

The IIP and MANICE scales differ for medium, large and very large bergs. MANICE (9th ed., 2005) gives 61-120 m, 121-200 m and over 200 m long. The USCG NAVCEN Iceberg_Formation.pdf table gives the same 121-200 m. This model uses the IIP lengths throughout.

| Class | Height above water | Waterline length | Source |
|---|---|---|---|
| growler | under 1 m | under 5 m | IIP; MANICE (about 20 m2) |
| bergy bit | 1 to 5 m | 5 to 15 m | MANICE (100-300 m2) |
| small | 5 to 15 m | 15 to 60 m | IIP |
| medium | 16 to 45 m | 61 to 122 m | IIP (MANICE: 61 to 120 m) |
| large | 46 to 75 m | 123 to 213 m | IIP (MANICE: 121 to 200 m) |
| very large | over 75 m | over 213 m | IIP (MANICE: over 200 m) |
| tabular (small) | 20 to 50 m | 200 m to 2.8 km | see below |

Notes:

- The class "very large" has no upper limit. The model caps it at 110 m high and 450 m long. That cap is an estimate. The largest berg seen on the northern Grand Banks was about 320 m long and 10 Mt (Hibernia EIS).
- The US Coast Guard says there is no agreed scale outside the North Atlantic.
- "Tabular" here means a small tabular berg. Its freeboard follows the Ross Ice Shelf front, 15-50 m (USGS ROSETTA-Ice). Its length stops at 2.8 km, the side of an 8 km2 square. 8 km2 is the "small iceberg" limit of Tournadre et al. (2016).
- Giant bergs are never generated. The US National Ice Center tracks bergs of 10 nmi or more by name. Load those from an observation file with `ice.load_icebergs`.

Mapping to the coarser `ice.py` bands: growler and bergy bit go to `growler`. Small and medium go to `small`. Large and very large go to `medium`. Tabular goes to `large`.

## Shape and mass

- Draft is 0.6 to 0.7 of the length for non-tabular bergs (Annals of Glaciology, Labrador data 1973-78). Draft is never less than the height. It is capped at 600 m (Jakobshavn, Enderlin et al. 2016).
- Width is 0.6 to 0.9 of the length. This is an estimate.
- Non-tabular mass = 0.6 x length x width x (height + draft) x 900 kg/m3. The 0.6 is an estimate. With it, a 120 m berg comes out near 0.7 Mt. The Labrador data give a median near 0.4 Mt and a mean near 2.2 Mt.
- Tabular mass uses 917 kg/m3 (BedMachine). Freeboard is 0.11 to 0.15 of the thickness. That is derived from 917/1027 plus firn, so it is an estimate.
- Mass is rounded to two significant figures. More would be false precision.

## Where bergs are

The table has 17 regions. Each is one or more latitude and longitude boxes. The first box that holds a point wins. Everywhere else has no bergs. That includes the tropics, the Mediterranean, the Baltic and the North Sea.

| Region | Peak density (bergs per 10,000 km2) | Season |
|---|---|---|
| Grand Banks, south of 48N | about 0.6 in May (derived from IIP) | IIP counts |
| Labrador shelf and NE Newfoundland | 3 (estimate) | spring peak (estimate) |
| Baffin Bay and Davis Strait | 4 (estimate) | near flat |
| Hudson Strait and Frobisher Bay | 0.4 (estimate) | near flat |
| South-west Greenland and Cape Farewell (West Greenland Current route) | 2.5 (estimate) | near flat |
| East Greenland shelf and Denmark Strait | 1.5 (estimate) | near flat |
| Canadian Archipelago and Nares Strait | 0.2 (estimate) | near flat |
| Barents Sea and Svalbard, north of 74N | 0.3 (estimate) | summer peak (estimate) |
| South-east Barents Sea, 70-74N, 40-58E | 0.1 (estimate) | summer peak (estimate) |
| Kara Sea and Franz Josef Land | 0.2 (estimate) | summer peak (estimate) |
| South Georgia and Scotia Sea | 3 (estimate) | flat |
| Weddell outflow and Iceberg Alley | 5 (estimate) | flat |
| Amundsen and Bellingshausen | 1 (estimate) | flat |
| Ross Sea | 1 (estimate) | flat |
| East Antarctic coast | 2 (estimate) | flat |
| Southern Ocean, South Atlantic | 0.3 (estimate) | flat |
| Southern Ocean, other sectors | 0.03 (estimate) | flat |

The Grand Banks density is worked out, not guessed:

- IIP mean bergs crossing 48N, 1983-2024: Feb 22, Mar 121, Apr 191, May 209, Jun 115, Jul 41. That is about 715 a year (IIP 2024 North Atlantic Iceberg Summary). These came from the research session. They could not be re-read here: navcen.uscg.gov was blocked.
- The other 16 a year are spread over August to January. That split is an estimate. Table 1 of the IIP 2024 summary gives the real monthly means for every month. Put them in once it can be read.
- Density = crossings x 0.5 month residence / 1,713,000 km2. The residence is an estimate.
- 1,713,000 km2 is the water area of the Grand Banks boxes. It is derived from the boxes with the bundled land mask. The model spreads the bergs over the whole boxes, so the divisor must be their area. An earlier version used 500,000 km2 and made about 3.5 times too many bergs.
- So at the May peak the boxes hold about 105 bergs (209 x 0.5), about 0.6 per 10,000 km2.
- For comparison, the IIP 2019 report gives a 1900-2018 mean of 492 a year (NSIDC G10028, doi:10.7265/z6e8-3027). The 2018 report already gives 492 for 1900-2017, so check this against G10028. The 1983-2014 mean is 787.

Other densities sit inside the orders of magnitude the research gave: about 1-10 per 10,000 km2 off Newfoundland and in the Weddell outflow, and about 0.1-1 in the Barents Sea.

Small pieces: each berg comes with 3 growlers and 2 bergy bits. Both counts are estimates. The IIP does not count growlers. Break-up into small bergs is about 80 % of the mass loss of large Antarctic bergs, and basal melt about 18 % (Tournadre, Bouhier, Girard-Ardhuin and Remy 2015). Small bergs are mainly made by break-up of large ones (Tournadre et al. 2016).

Antarctic regions have no season. We found no monthly source. The ALTIBERG product (CERSAT/Ifremer) should replace them once it can be read.

The boxes have hard edges. Density can step at a box edge.

## How the generator works

- The globe is cut into cells of 0.5 degree.
- Each cell has its own random stream. The stream is seeded by the seed, the date and the cell.
- So the same cell always holds the same bergs, whatever the bounding box. A smaller box gives a subset of a bigger one.
- The count in each cell is drawn from a Poisson distribution.
- A berg never sits on land. It also never sits on an Antarctic ice shelf. The land test uses `geo.default_land_mask()`. The shelf test uses the Natural Earth shelves in `ice.py`.
- Pass `edges` from `seaice.edges_on(when)` to mark bergs frozen into sea ice. Those bergs are kept. Sea ice also damps wave erosion.
- Pass `water_depth_m` to mark grounded bergs. A grounded berg does not drift. `mno_env` has no bathymetry of its own.
- More than `max_bergs` bergs raises an error. Use a smaller box.

## Drift

- Drift = ocean current + a fraction of the wind.
- The fraction is 2 % for small bergs (Garrett et al. 1985; Smith 1993).
- It is 1.7 % for large and very large bergs (Bigg et al. 1997 use 1.6-1.8 %).
- It is 1 % for tabular bergs. That is an estimate. Wagner, Dell and Eisenman (2017) show that deep keels follow the deeper current.
- If you give no current, each region has a current proxy. Every proxy is an estimate. Some regions have none, so their drift is the wind term only.

## Melt and remaining life

The melt has three parts, in metres per day (Martin and Adcroft 2010; Bigg et al. 1997):

- Basal: 0.58 |du|^0.8 (Tw - Tf) / L^0.2.
- Side convection: 7.62e-3 Tw + 1.29e-3 Tw^2.
- Wave erosion: (1/12) Ss (1 + cos(pi A^3)) (Tw + 2). A is the sea-ice fraction. Ss is the sea state.

Rules:

- With no sea state given, Ss comes from the wind: 1.5 sqrt(w) + 0.1 w.
- Life ends when a side or the thickness drops under 1 m.
- Life is capped at 1,825 days. Bigg et al. (1997) found all model bergs melted within about 5 years. Confidence: medium. The paper was not read this session.
- Roll-over and break-up are not modelled.

Check: a 40 m berg in 5 C water at sea state 4 lasts about 4 days. That fits field data. Small Grand Banks bergs can lose a third of their mass in one day.

## Sensor hooks

Radar, conventional X-band, calm sea:

- Growler: 0.5 nm, or not seen at all (Canadian Coast Guard, high confidence).
- Bergy bit: 1 nm (vendor brochure, medium confidence).
- Small to tabular: 4 to 20 nm. These are estimates. A low-grade source gives 2-9 nm for bergs.
- Enhanced radar: growler 2 nm, bergy bit 4 nm (vendor brochure; a CCG trial gave beyond 3 nm).
- Range is cut by sea state. Growlers are lost from sea state 4 and bergy bits from sea state 5. This follows the rule of thumb that small ice is lost in clutter from about sea state 3-4. The table is an estimate.
- Range is never beyond the radar horizon to the berg top (4/3 earth).

Visual:

- Range is the least of three things: the visibility, the geographic range, and a small-ice cap.
- Geographic range = 2.07 (sqrt(eye height) + sqrt(berg height)) nm. Bowditch (2019, Vol. 1, Appendix B) gives the distance to the horizon as 1.17 sqrt(h in feet) = 2.07 sqrt(h in metres) nm.
- The small-ice cap is 1 nm for growlers and 2 nm for bergy bits. This is an estimate.
- A moonless night multiplies the range by 0.25. This is an estimate.

Sonar:

- `sonar_false_contact_index` is a design index from 0 to 1. It is not a probability. We found no citable false-contact rates.
- The index rises with size. It halves when the keel ends well above the sonar depth.
- Break-up noise of a large berg is about 220 dB rms re 1 uPa at 1 m, 1-440 Hz (Dziak et al. 2013).

## Known gaps

- There is no per-cell density data. The Abramov (1996) atlas for the Barents and Kara Seas and the ALTIBERG fields for the Southern Ocean are the sources to read.
- These hosts were blocked in the research session: data-ww3.ifremer.fr, arxiv.org, www.inter.dfo-mpo.gc.ca, navcen.uscg.gov. Someone must allow them in the session's network settings before the primary texts can be read.
- No verified record of a submarine hitting an iceberg was found. None is assumed.
- Collision and hull damage are not modelled.
- Some real berg sources have no region yet. These are the Alaskan tidewater glaciers (Prince William Sound, Glacier Bay), the Patagonian fjords and the Svalbard and Greenland fjord heads at fine scale. Their densities would be estimates too.
- The Gulf of St Lawrence gets no modelled bergs. The Grand Banks boxes stop at 57.5W north of 46.5N, so Cabot Strait is outside them too. A few real bergs do enter through the Strait of Belle Isle.
- Iceland's south and east waters get no modelled bergs. Real bergs there are rare.
- Foxe Basin gets no modelled bergs. It has no tidewater glacier source.
- The Norwegian Sea and the Finnmark coast get no modelled bergs. The Barents boxes start at 74N west of 40E. Bergs south of that are exceptional (Vinje and Kvambekk 1991; Keghouche et al. 2010).
