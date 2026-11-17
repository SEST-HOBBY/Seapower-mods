"""ENV-04: ECMWF IFS open-data GRIB2 -> mno.environment.snapshot.v1. NOT RUN IN THIS REPOSITORY.

Offline by default. It converts GRIB2 files the owner has already downloaded; with
--download it calls the optional `ecmwf-opendata` client (pip install ecmwf-opendata).
Reading GRIB needs the optional `cfgrib` + `xarray` (and ecCodes). None of these is a
dependency of MNO; this tool is not part of any game build.

    py -3 tools/ingest_ecmwf_opendata.py --grib-dir D:/env/ifs/20261117T00 --issue 2026-11-17T00:00:00Z \
        --steps 0,6,12,18,24 --thin 4 --out D:/env/cache --mode current_analogue \
        --campaign-start 2028-11-17T00:00:00Z

Licence: ECMWF open data is CC BY 4.0 ("Copyright ECMWF"; see the provider's terms page).
Confirm the terms before redistributing any converted tile with MNO.

Fields: msl (Pa), 10u/10v (m/s), tcc (0-1), tp (m, accumulated from start), 2t (K).
Wave fields (swh, mwd, mwp) come from the separate ECMWF wave stream (`stream=wave`) and are
converted the same way when present. Thunderstorm risk is NOT derived from rain here.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mno_env import cache, ingest  # noqa: E402
from mno_env.clock import analogue_offset  # noqa: E402
from mno_env.grid import LatLonGrid  # noqa: E402
from mno_env.snapshot import iso, utc  # noqa: E402

PARAMS = {"msl": "msl_pressure_hpa", "10u": "wind_u10_ms", "10v": "wind_v10_ms", "tcc": "cloud_fraction_pct",
          "2t": "air_temp_2m_c", "tp": "precip_rate_mm_h", "swh": "wave_hs_m", "mwd": "wave_dir_deg", "mwp": "wave_tm_s"}


def read_grib(path: Path):
    try:
        import xarray as xr  # noqa: PLC0415
    except ImportError:
        raise SystemExit("cfgrib/xarray not installed: pip install cfgrib xarray (and ecCodes); "
                         "this converter is optional and not part of MNO") from None
    ds = xr.open_dataset(path, engine="cfgrib", backend_kwargs={"indexpath": ""})
    var = list(ds.data_vars)[0]
    lat, lon = ds["latitude"].values, ds["longitude"].values
    return ds[var].values, lat, lon, var


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--grib-dir", type=Path, required=True, help="files named <param>_<step>.grib2")
    p.add_argument("--issue", required=True, help="forecast issue time, UTC, e.g. 2026-11-17T00:00:00Z")
    p.add_argument("--steps", default="0,6,12,18,24")
    p.add_argument("--thin", type=int, default=4, help="keep every Nth cell (0.25 deg x 4 = 1 deg)")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--mode", choices=("current_analogue", "historical_analogue"), default="current_analogue")
    p.add_argument("--campaign-start", required=True)
    p.add_argument("--source-url", default="https://data.ecmwf.int/forecasts/")
    a = p.parse_args(argv)
    issue = utc(a.issue)
    steps = [int(s) for s in a.steps.split(",")]
    frames: dict[int, dict] = {s: {} for s in steps}
    grid = None
    tp_accum = []
    for param, name in PARAMS.items():
        files = [a.grib_dir / f"{param}_{s}.grib2" for s in steps]
        if not all(f.exists() for f in files):
            print(f"skip {param}: not all steps present", file=sys.stderr)
            continue
        for s, f in zip(steps, files):
            vals, lat, lon, _ = read_grib(f)
            ny, nx = vals.shape
            flat = [None if v != v else float(v) for v in vals.ravel().tolist()]
            if lat[0] > lat[-1]:
                flat = ingest.flip_north_to_south(flat, nx, ny)
            flat, lon0 = ingest.rotate_0_360(flat, nx, ny, float(min(lon)), float(abs(lon[1] - lon[0])))
            flat, tnx, tny = ingest.thin(flat, nx, ny, a.thin)
            grid = LatLonGrid(lon0, float(min(lat)), abs(float(lon[1] - lon[0])) * a.thin, abs(float(lat[1] - lat[0])) * a.thin, tnx, tny)
            if param == "msl":
                flat = ingest.pa_to_hpa(flat)
            elif param == "2t":
                flat = ingest.k_to_c(flat)
            elif param == "tcc":
                flat = ingest.frac_to_pct(flat)
            if param == "tp":
                tp_accum.append(flat)
            else:
                frames[s][name] = flat
    if grid is None:
        raise SystemExit("no complete parameter found")
    if tp_accum:
        rates, clamped = ingest.accumulated_to_rate(tp_accum, steps)
        frames[steps[0]].pop("precip_rate_mm_h", None)
        for s, r in zip(steps[1:], rates):
            frames[s]["precip_rate_mm_h"] = r  # interval rate valid over (previous step, s]
        print(f"precipitation: {clamped} negative differences clamped to 0", file=sys.stderr)
    usable = [s for s in steps if s != steps[0] or not tp_accum]
    names = sorted(set.intersection(*(set(frames[s]) for s in usable)))
    camp = utc(a.campaign_start)
    offset = (int((camp - issue).total_seconds()) if a.mode == "current_analogue"
              else analogue_offset(camp, issue.year))
    snap = ingest.build(
        snapshot_id=f"ecmwf-ifs-open-{a.issue.replace(':', '')}-thin{a.thin}",
        data_class="forecast",
        provenance={"provider": "ECMWF", "product": "IFS open data (HRES/oper)", "product_version": "as downloaded",
                    "licence": "CC BY 4.0", "attribution": "Copyright ECMWF; converted by MNO tools",
                    "source_url": a.source_url, "downloaded_utc": iso(dt.datetime.now(dt.timezone.utc).replace(microsecond=0)),
                    "source_time_utc": iso(issue), "forecast_issue_utc": iso(issue)},
        mapping={"mode": a.mode, "offset_seconds": offset, "campaign_start_utc": a.campaign_start,
                 "statement": "Real forecast data replayed as an analogue for the fictional campaign; not a forecast of 2028-2029."},
        grid=grid,
        frames=[(issue + dt.timedelta(hours=s), float(s), {n: frames[s][n] for n in names}) for s in usable],
        kinds={n: "forecast" for n in names},
        created=dt.datetime.now(dt.timezone.utc).replace(microsecond=0))
    cache.MnoEnvDataProvider(a.out).add(snap)
    print(f"cached {snap['snapshot_id']}: {grid.nx}x{grid.ny}, {len(usable)} steps, fields {names}")


if __name__ == "__main__":
    main()
