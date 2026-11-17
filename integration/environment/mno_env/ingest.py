"""ENV-04 ingestion transforms: provider fields -> canonical snapshot fields. BUILD-TESTED on arrays.

Reading GRIB or NetCDF files needs optional readers (cfgrib/eccodes, netCDF4 or h5py) that
are NOT dependencies of this package; tools/ingest_*.py import them only when run. Every
transform below works on plain Python lists so it is tested without those readers.

Conventions handled here, each with a test:
- ECMWF IFS `tp` is total precipitation in METRES ACCUMULATED FROM THE FORECAST START.
  The interval rate is (tp[k] - tp[k-1]) x 1000 / hours between steps, in mm/h. A small
  negative difference (packing noise) is clamped to 0 and counted; a large one is an error.
- ERA5 hourly `tp` is the accumulation over the PRECEDING HOUR (metres): rate = tp x 1000.
- `msl` Pa -> hPa; `2t` K -> degC; `tcc` 0..1 -> %; `10u`/`10v` m/s pass through.
- OSI SAF `ice_conc` is % on a polar grid (EPSG:3411/3412 or EASE2 6931/6932), with a
  status flag and land/missing fill values; it is reprojected by inverse mapping, and land
  or missing cells stay missing rather than becoming open water.
- Longitudes in 0..360 are rotated to -180..180 with the row kept intact.
"""
from __future__ import annotations

import datetime as dt
import math

from .grid import LatLonGrid, ProjectedGrid, regrid_polar_to_latlon
from .snapshot import FIELDS, SCHEMA, iso, seal

NEG_TOLERANCE_M = 1e-6  # 0.001 mm: GRIB packing noise


class IngestError(ValueError):
    pass


def accumulated_to_rate(accum_m: list[list], step_hours: list[float]) -> tuple[list[list], int]:
    """accum_m[k] is the field at step k (metres since forecast start). Returns (rates for
    steps 1..n in mm/h, number of clamped cells). Step 0 has no interval and is dropped."""
    if len(accum_m) != len(step_hours) or len(accum_m) < 2:
        raise IngestError("need two or more steps with their lead hours")
    out, clamped = [], 0
    for k in range(1, len(accum_m)):
        dh = step_hours[k] - step_hours[k - 1]
        if dh <= 0:
            raise IngestError("lead hours must increase")
        row = []
        for a, b in zip(accum_m[k - 1], accum_m[k]):
            if a is None or b is None:
                row.append(None)
                continue
            d = b - a
            if d < 0:
                if d < -NEG_TOLERANCE_M * 10:
                    raise IngestError(f"accumulation decreased by {d * 1000:.3f} mm: not an accumulated-from-start field")
                d, clamped = 0.0, clamped + 1
            row.append(d * 1000.0 / dh)
        out.append(row)
    return out, clamped


def hourly_accum_to_rate(tp_m: list) -> list:
    return [None if v is None else max(0.0, v) * 1000.0 for v in tp_m]


def pa_to_hpa(v):
    return [None if x is None else x / 100.0 for x in v]


def k_to_c(v):
    return [None if x is None else x - 273.15 for x in v]


def frac_to_pct(v):
    return [None if x is None else max(0.0, min(100.0, x * 100.0)) for x in v]


def rotate_0_360(values: list, nx: int, ny: int, lon_min: float, lon_step: float) -> tuple[list, float]:
    """Rotate rows of a global 0..360 grid so that it starts at -180. Returns (values, lon_min)."""
    if lon_min < 0:
        return list(values), lon_min
    period = int(round(360 / lon_step))
    if nx not in (period, period + 1):
        raise IngestError("rotate_0_360 needs a global grid")
    shift = next((i for i in range(nx) if lon_min + i * lon_step >= 180 - 1e-9), None)
    out = []
    for j in range(ny):
        row = values[j * nx:(j + 1) * nx][:period]
        row = row[shift:] + row[:shift]
        if nx == period + 1:
            row.append(row[0])
        out.extend(row)
    return out, lon_min + shift * lon_step - 360.0


def flip_north_to_south(values: list, nx: int, ny: int) -> list:
    """GRIB/NetCDF global grids usually store the northernmost row first; snapshots store south first."""
    return [v for j in range(ny - 1, -1, -1) for v in values[j * nx:(j + 1) * nx]]


def osisaf_conc(values: list, status: list | None, fill: float | None = None) -> list:
    """Keep concentration only where it is a valid measurement. OSI SAF status flags: 0 =
    nominal; non-zero flags (land, lake, climatology, missing...) become None. Product
    documentation for the exact flag table must be checked per product version."""
    out = []
    for k, v in enumerate(values):
        bad = v is None or (fill is not None and v == fill) or (isinstance(v, float) and math.isnan(v))
        if status is not None and status[k] not in (0, None):
            bad = True
        out.append(None if bad else max(0.0, min(100.0, float(v))))
    return out


def polar_to_latlon(projection, x0, y0, dx, dy, nx, ny, values, target: LatLonGrid) -> list:
    return regrid_polar_to_latlon(ProjectedGrid(projection, x0, y0, dx, dy, nx, ny), values, target)


def build(*, snapshot_id: str, data_class: str, provenance: dict, mapping: dict, grid: LatLonGrid,
          frames: list[tuple[dt.datetime, float | None, dict]], kinds: dict, uncertainty: dict | None = None,
          derivations: dict | None = None, created: dt.datetime) -> dict:
    """Assemble and seal a snapshot. frames: (valid time, lead hours or None, {field: values})."""
    fields = {}
    for name, kind in kinds.items():
        if name not in FIELDS:
            raise IngestError(f"{name} is not a canonical field")
        fields[name] = {"units": FIELDS[name][0], "fill_value": None, "kind": kind,
                        "uncertainty": (uncertainty or {}).get(name, {"type": "unknown"})}
        if derivations and name in derivations:
            fields[name]["derivation"] = derivations[name]
    times = []
    for valid, lead, vals in frames:
        missing = set(kinds) - set(vals)
        if missing:
            raise IngestError(f"{iso(valid)}: missing {sorted(missing)}")
        times.append({"valid_utc": iso(valid), "lead_hours": lead,
                      "values": {k: [None if v is None else round(float(v), 4) for v in vals[k]] for k in kinds}})
    snap = {"schema": SCHEMA, "snapshot_id": snapshot_id, "created_utc": iso(created), "data_class": data_class,
            "provenance": provenance, "campaign_mapping": mapping, "grid": grid.to_dict(), "fields": fields,
            "times": times, "integrity": {}}
    return seal(snap)


def thin(values: list, nx: int, ny: int, factor: int) -> tuple[list, int, int]:
    """Decimate a lat/lon grid by an integer factor (keeps every factor-th cell)."""
    if factor <= 1:
        return list(values), nx, ny
    nnx, nny = (nx + factor - 1) // factor, (ny + factor - 1) // factor
    return [values[j * nx + i] for j in range(0, ny, factor) for i in range(0, nx, factor)], nnx, nny
