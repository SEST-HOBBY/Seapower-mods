"""ENV-04: OSI SAF sea-ice concentration NetCDF -> sea_ice_conc_pct snapshot. NOT RUN IN THIS REPOSITORY.

Offline: converts files the owner downloaded from the OSI SAF catalogue. Needs the optional
`netCDF4` package (pip install netCDF4). The polar grid is described by the file's own
projection variable; this tool supports the NSIDC polar stereographic grids (EPSG:3411,
3412, used by OSI-401 family products) and EASE-Grid 2.0 (EPSG:6931, 6932, used by the
OSI-450/430 climate records). Reprojection maths: mno_env/polar.py (checked against PROJ).

    py -3 tools/ingest_osisaf_ice.py --nh ice_conc_nh_polstere-100_multi_202611171200.nc \
        --sh ice_conc_sh_polstere-100_multi_202611171200.nc --res 0.5 --out D:/env/cache \
        --campaign-start 2028-11-17T12:00:00Z

Licence: EUMETSAT OSI SAF products are generally CC BY 4.0; check the product user manual.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mno_env import cache, ingest, polar  # noqa: E402
from mno_env.grid import LatLonGrid  # noqa: E402
from mno_env.snapshot import iso  # noqa: E402

GRID_MAP = {("stere", 70.0): polar.EPSG_3411, ("stere", -70.0): polar.EPSG_3412,
            ("laea", 90.0): polar.EPSG_6931, ("laea", -90.0): polar.EPSG_6932}


def read(path: Path):
    try:
        from netCDF4 import Dataset  # noqa: PLC0415
    except ImportError:
        raise SystemExit("netCDF4 not installed: pip install netCDF4 (optional, not part of MNO)") from None
    ds = Dataset(path)
    conc = ds.variables["ice_conc"]
    flag = ds.variables.get("status_flag")
    xc, yc = ds.variables["xc"][:], ds.variables["yc"][:]
    scale = 1000.0 if getattr(ds.variables["xc"], "units", "km") == "km" else 1.0
    crs = next(v for v in ds.variables.values() if hasattr(v, "grid_mapping_name"))
    if crs.grid_mapping_name == "polar_stereographic":
        proj = GRID_MAP[("stere", float(crs.standard_parallel))]
    else:
        proj = GRID_MAP[("laea", float(crs.latitude_of_projection_origin))]
    t = ds.variables["time"]
    from netCDF4 import num2date  # noqa: PLC0415
    when = num2date(t[0], t.units).replace(tzinfo=dt.timezone.utc)
    vals = conc[0].filled(float("nan")).ravel().tolist()
    st = flag[0].filled(-1).ravel().tolist() if flag is not None else None
    return proj, float(xc[0]) * scale, float(yc[0]) * scale, float(xc[1] - xc[0]) * scale, float(yc[1] - yc[0]) * scale, len(xc), len(yc), vals, st, when


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--nh", type=Path)
    p.add_argument("--sh", type=Path)
    p.add_argument("--res", type=float, default=0.5)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--campaign-start", required=True)
    p.add_argument("--product", default="OSI SAF sea ice concentration")
    a = p.parse_args(argv)
    grid = LatLonGrid(-180.0, -90.0, a.res, a.res, int(360 / a.res), int(180 / a.res) + 1)
    merged = [None] * grid.size
    when = None
    for path in (a.nh, a.sh):
        if not path:
            continue
        proj, x0, y0, dx, dy, nx, ny, vals, st, when = read(path)
        part = ingest.polar_to_latlon(proj, x0, y0, dx, dy, nx, ny, ingest.osisaf_conc(vals, st), grid)
        merged = [b if a_ is None else a_ for a_, b in zip(merged, part)]
    if when is None:
        raise SystemExit("give --nh and/or --sh")
    from mno_env.clock import analogue_offset  # noqa: PLC0415
    from mno_env.snapshot import utc  # noqa: PLC0415
    snap = ingest.build(
        snapshot_id=f"osisaf-ice-{when:%Y%m%dT%H%M}-{a.res}deg", data_class="observed",
        provenance={"provider": "EUMETSAT OSI SAF", "product": a.product, "product_version": "as downloaded",
                    "licence": "CC BY 4.0 (check product manual)", "attribution": "EUMETSAT OSI SAF",
                    "source_url": "https://osi-saf.eumetsat.int/products/sea-ice-products",
                    "downloaded_utc": iso(dt.datetime.now(dt.timezone.utc).replace(microsecond=0)),
                    "source_time_utc": iso(when), "forecast_issue_utc": None},
        mapping={"mode": "historical_analogue", "offset_seconds": analogue_offset(utc(a.campaign_start), when.year),
                 "campaign_start_utc": a.campaign_start,
                 "statement": "Observed ice of a past date replayed as an analogue; not a forecast of 2028-2029."},
        grid=grid, frames=[(when, None, {"sea_ice_conc_pct": merged})], kinds={"sea_ice_conc_pct": "observed"},
        uncertainty={"sea_ice_conc_pct": {"type": "product_total_uncertainty", "note": "see the file's total_standard_uncertainty"}},
        created=dt.datetime.now(dt.timezone.utc).replace(microsecond=0))
    cache.MnoEnvDataProvider(a.out).add(snap)
    print(f"cached {snap['snapshot_id']}")


if __name__ == "__main__":
    main()
