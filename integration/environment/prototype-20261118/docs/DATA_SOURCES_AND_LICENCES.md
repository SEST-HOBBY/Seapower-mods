# Public data sources, provenance and distribution cautions

**18 November 2026, Australia/Brisbane.** This package embeds **only a procedurally generated weather field** and **public-domain Natural Earth low-resolution coastline geometry**. It does not ship ECMWF, Open-Meteo or EUMETSAT datasets. Data licences matter independently of the code licence.

| Provider | Product | Intended use | Link / caveat |
|---|---|---|---|
| ECMWF | IFS open forecasts 0.25° and (since 20 Oct 2026) 0.1° | High-fidelity global wind/cloud/pressure forecast snapshots and ocean-wave streams | https://www.ecmwf.int/en/forecasts/datasets/open-data ; CC BY 4.0 attribution and terms; real-time dissemination and local caches |
| Copernicus C3S | ERA5 historical reanalysis | Replay sampled historical weather or calibrate future fictional campaign scenarios | https://cds.climate.copernicus.eu/ ; verify provider and product terms |
| Open-Meteo | Historical Weather and Forecast APIs | Small-scale testing of source-verified hourly records via included `tools/import_openmeteo.py` | https://open-meteo.com/en/docs/historical-weather-api ; check API access/commercial redistribution terms; NOT a complete gridded global field |
| Open-Meteo | Marine Weather API | Example wave/current provider for later maritime weather integration | https://open-meteo.com/en/docs/marine-weather-api ; point sampling, uncertain coast/ice region validity |
| EUMETSAT OSI SAF | Sea-ice concentration / edge / drift, e.g. OSI-401-d, OSI-405-d | Sea-ice concentration and motion field | https://osi-saf.eumetsat.int/products/sea-ice-products ; CC BY 4.0, polar stereographic grids, differing temporal and spatial resolutions |
| British Antarctic Survey / SCAR | Antarctic boundary/ice shelf fronts | Reference fixed ice-shelf geography, update on longer scales | https://www.bas.ac.uk ; verify exact dataset attribution and geospatial licence |
| Natural Earth | Public-domain simplified world polygons | Viewer coastline outline only | https://www.naturalearthdata.com/about/terms-of-use/ ; public domain |
| R.A.T.S. Topographic Map (Kanalratte) | MIT Sea Power globe overlay source reference | Architecture research only; no code copied into the current build | https://github.com/struckl/SeaPowerTopo ; attribute and preserve licence if future implementation reuses code |

## Data lineage required for a reusable SEST weather platform

Each delivered tile must carry provider/product/version; acquired at UTC; valid at UTC; forecast issuance time or reanalysis time; source URL; data licence; checksum; units; coordinate reference; latitude/longitude envelope; spatial/temporal resolution; masks; missing-value markers; and uncertainty/quality flags.

For fictional **2028–2029 campaign dates**, historical replay must retain **both** actual meteorological year/timestamp and fictional campaign year/timestamp. An observed historical reanalysis replayed into a fictitious future is **not a weather forecast of that future**. When constructing synthetic projected future climate, clearly describe the scenario assumptions and lack of forecast certainty. Forecast systems should never silently be treated as climate projections.

For production, distribute **preprocessed, versioned, regional static forecast tiles** and let GCO run offline. Separate optional online refresh into an external ETL tool; never make a live web request from Unity's frame loop. The one-file HTML is a visual prototype only.
