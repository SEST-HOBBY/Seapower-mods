"""`mno.environment.snapshot.v1`: versioned, provenance-carrying environment snapshots. BUILD-TESTED.

A snapshot is one dataset on one regular lat/lon grid with one or more valid times. It is
plain JSON (optionally gzip) so that tools outside Sea Power can read it. The schema is in
`integration/environment/schemas/mno.environment.snapshot.v1.schema.json`; `validate()` is the
conformance check and is stricter than the JSON schema (cross-field rules, checksums, units).

Field values are either a JSON list of numbers/null, or a packed object
{"encoding": "int16-scaled-b64", "scale": s, "offset": o, "missing": -32768, "data": "<base64>"}
that decodes to value = raw*scale + offset (little-endian int16).
"""
from __future__ import annotations

import base64
import datetime as dt
import gzip
import hashlib
import json
import math
import struct
from pathlib import Path

from .grid import LatLonGrid

SCHEMA = "mno.environment.snapshot.v1"

# Canonical fields: units, physical range, and which kinds are allowed.
# kind: observed | analysis | reanalysis | forecast | derived_risk | synthetic | procedural
FIELDS = {
    "msl_pressure_hpa": ("hPa", 850.0, 1090.0),
    "wind_u10_ms": ("m s-1", -90.0, 90.0),
    "wind_v10_ms": ("m s-1", -90.0, 90.0),
    "wind_speed10_ms": ("m s-1", 0.0, 100.0),
    "cloud_fraction_pct": ("%", 0.0, 100.0),
    "precip_rate_mm_h": ("mm h-1", 0.0, 500.0),
    "snowfall_rate_mm_h": ("mm h-1 water equivalent", 0.0, 200.0),
    "air_temp_2m_c": ("degC", -90.0, 60.0),
    "visibility_km": ("km", 0.0, 100.0),
    "wave_hs_m": ("m", 0.0, 25.0),
    "wave_dir_deg": ("degree_from_north_coming_from", 0.0, 360.0),
    "wave_tm_s": ("s", 0.0, 30.0),
    "wave_tp_s": ("s", 0.0, 40.0),
    "current_u_ms": ("m s-1", -5.0, 5.0),
    "current_v_ms": ("m s-1", -5.0, 5.0),
    "sst_c": ("degC", -2.5, 40.0),
    "sea_ice_conc_pct": ("%", 0.0, 100.0),
    "sea_ice_type_code": ("code: 1 open water, 2 first-year, 3 multi-year, 4 ambiguous", 1.0, 4.0),
    "ice_drift_u_ms": ("m s-1", -2.0, 2.0),
    "ice_drift_v_ms": ("m s-1", -2.0, 2.0),
    "convective_risk_idx": ("index 0..1 (derived, not observed lightning)", 0.0, 1.0),
}
DATA_CLASSES = {"observed", "analysis", "reanalysis", "forecast", "synthetic", "procedural", "derived"}
FIELD_KINDS = {"observed", "analysis", "reanalysis", "forecast", "derived_risk", "synthetic", "procedural"}
MAPPING_MODES = {"historical_analogue", "current_analogue", "procedural", "synthetic_demo"}
REQUIRED_PROVENANCE = ("provider", "product", "product_version", "licence", "attribution", "source_url",
                       "downloaded_utc", "source_time_utc", "forecast_issue_utc")
INT16_MISSING = -32768


class SnapshotError(ValueError):
    pass


def utc(s: str) -> dt.datetime:
    """Parse an ISO-8601 UTC timestamp that must end in Z."""
    if not isinstance(s, str) or not s.endswith("Z"):
        raise SnapshotError(f"timestamp must be ISO-8601 UTC ending in Z: {s!r}")
    try:
        return dt.datetime.fromisoformat(s[:-1]).replace(tzinfo=dt.timezone.utc)
    except ValueError as exc:
        raise SnapshotError(f"bad timestamp {s!r}: {exc}") from None


def iso(t: dt.datetime) -> str:
    if t.tzinfo is None:
        raise SnapshotError("naive datetime; campaign and source times are always UTC")
    return t.astimezone(dt.timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds") + "Z"


def pack_int16(values, scale: float, offset: float = 0.0) -> dict:
    raw = []
    for v in values:
        if v is None or (isinstance(v, float) and math.isnan(v)):
            raw.append(INT16_MISSING)
            continue
        q = round((v - offset) / scale)
        if not -32767 <= q <= 32767:
            raise SnapshotError(f"value {v} does not fit int16 with scale {scale}")
        raw.append(q)
    return {"encoding": "int16-scaled-b64", "scale": scale, "offset": offset, "missing": INT16_MISSING,
            "data": base64.b64encode(struct.pack(f"<{len(raw)}h", *raw)).decode("ascii")}


def unpack(values):
    if isinstance(values, list):
        return values
    if not isinstance(values, dict) or values.get("encoding") != "int16-scaled-b64":
        raise SnapshotError("unknown field encoding")
    blob = base64.b64decode(values["data"], validate=True)
    if len(blob) % 2:
        raise SnapshotError("packed field has an odd byte length")
    raw = struct.unpack(f"<{len(blob) // 2}h", blob)
    s, o, miss = float(values["scale"]), float(values.get("offset", 0.0)), int(values.get("missing", INT16_MISSING))
    return [None if r == miss else r * s + o for r in raw]


def payload_digest(snap: dict) -> str:
    """SHA-256 over the canonical JSON of grid + fields + times (the data, not the wrapper)."""
    body = {"grid": snap.get("grid"), "fields": snap.get("fields"), "times": snap.get("times")}
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def seal(snap: dict) -> dict:
    snap.setdefault("integrity", {})["payload_sha256"] = payload_digest(snap)
    return snap


def dumps(snap: dict) -> bytes:
    return json.dumps(snap, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def write(snap: dict, path: Path) -> str:
    """Write deterministically (gzip mtime 0 when the name ends .gz). Returns the file SHA-256."""
    data = dumps(snap)
    if str(path).endswith(".gz"):
        data = gzip.compress(data, compresslevel=9, mtime=0)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)
    return hashlib.sha256(data).hexdigest()


def read(path: Path) -> dict:
    data = Path(path).read_bytes()
    if data[:2] == b"\x1f\x8b":
        try:
            data = gzip.decompress(data)
        except (OSError, EOFError) as exc:
            raise SnapshotError(f"{path}: damaged gzip: {exc}") from None
    try:
        return json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SnapshotError(f"{path}: not readable JSON: {exc}") from None


def validate(snap: dict, *, now_utc: dt.datetime | None = None) -> list[str]:
    """Return a list of conformance errors; empty means the snapshot conforms."""
    err: list[str] = []
    if not isinstance(snap, dict):
        return ["snapshot is not an object"]
    if snap.get("schema") != SCHEMA:
        err.append(f"schema must be {SCHEMA}")
    for key in ("snapshot_id", "created_utc", "data_class", "provenance", "campaign_mapping", "grid", "fields", "times", "integrity"):
        if key not in snap:
            err.append(f"missing {key}")
    if err:
        return err
    dclass = snap["data_class"]
    if dclass not in DATA_CLASSES:
        err.append(f"data_class {dclass!r} not one of {sorted(DATA_CLASSES)}")
    prov = snap["provenance"]
    for key in REQUIRED_PROVENANCE:
        if key not in prov:
            err.append(f"provenance.{key} missing (use null only where the doc says it may be null)")
    for key in ("provider", "product", "licence", "attribution"):
        if not prov.get(key):
            err.append(f"provenance.{key} must be non-empty")
    if dclass in ("synthetic", "procedural") and "SYNTHETIC" not in str(prov.get("product", "")).upper() and "PROCEDURAL" not in str(prov.get("product", "")).upper():
        err.append("synthetic/procedural snapshots must say SYNTHETIC or PROCEDURAL in provenance.product")
    try:
        created = utc(snap["created_utc"])
        if prov.get("downloaded_utc") is not None:
            utc(prov["downloaded_utc"])
        src_t = utc(prov["source_time_utc"]) if prov.get("source_time_utc") is not None else None
        issue = utc(prov["forecast_issue_utc"]) if prov.get("forecast_issue_utc") is not None else None
    except SnapshotError as exc:
        err.append(str(exc))
        return err
    if dclass == "forecast" and issue is None:
        err.append("forecast snapshots need provenance.forecast_issue_utc")
    if dclass in ("observed", "analysis", "reanalysis") and issue is not None:
        err.append(f"{dclass} snapshot must not carry a forecast issue time")
    if now_utc is not None and created > now_utc + dt.timedelta(minutes=5):
        err.append("created_utc is in the future")
    mapping = snap["campaign_mapping"]
    if mapping.get("mode") not in MAPPING_MODES:
        err.append(f"campaign_mapping.mode must be one of {sorted(MAPPING_MODES)}")
    if mapping.get("mode") in ("historical_analogue", "current_analogue") and dclass in ("synthetic", "procedural"):
        err.append("an analogue mapping needs real source data, not a synthetic/procedural snapshot")
    if not isinstance(mapping.get("offset_seconds"), int):
        err.append("campaign_mapping.offset_seconds must be an integer number of seconds")
    if "statement" not in mapping or "not a forecast" not in str(mapping.get("statement", "")).lower():
        err.append("campaign_mapping.statement must say the mapped data is not a forecast of the campaign years")
    g = snap["grid"]
    try:
        grid = LatLonGrid.from_dict(g)
    except (KeyError, TypeError, ValueError):
        err.append("grid needs lon_min, lat_min, lon_step, lat_step, nx, ny")
        return err
    if g.get("crs") != "EPSG:4326" or g.get("type") != "regular_latlon":
        err.append("grid must be type regular_latlon in EPSG:4326 (reproject polar sources first)")
    if grid.nx < 2 or grid.ny < 2 or grid.lon_step <= 0 or grid.lat_step <= 0:
        err.append("grid needs nx, ny >= 2 and positive steps")
    if grid.lat_min < -90 or grid.lat(grid.ny - 1) > 90 + 1e-9:
        err.append("grid latitudes outside -90..90")
    if not -180 <= grid.lon_min < 360:
        err.append("grid lon_min must be in [-180, 360)")
    if grid.nx * grid.lon_step > 360 + grid.lon_step + 1e-9:
        err.append("grid wraps longitude more than once")
    fields = snap["fields"]
    if not isinstance(fields, dict) or not fields:
        err.append("fields must be a non-empty object")
        return err
    for name, meta in fields.items():
        if name not in FIELDS:
            err.append(f"field {name!r} is not a canonical field")
            continue
        units, lo, hi = FIELDS[name]
        if meta.get("units") != units:
            err.append(f"{name}: units must be {units!r}, got {meta.get('units')!r}")
        kind = meta.get("kind")
        if kind not in FIELD_KINDS:
            err.append(f"{name}: kind {kind!r} not one of {sorted(FIELD_KINDS)}")
        if dclass in ("synthetic", "procedural") and kind not in ("synthetic", "procedural", "derived_risk"):
            err.append(f"{name}: a {dclass} snapshot cannot label a field {kind!r}")
        if name == "convective_risk_idx" and kind != "derived_risk":
            err.append("convective_risk_idx must be kind derived_risk (it is not an observed lightning field)")
        if kind == "derived_risk" and not meta.get("derivation"):
            err.append(f"{name}: derived fields need a derivation note")
        if "uncertainty" not in meta:
            err.append(f"{name}: uncertainty missing (an object; may say {{'type': 'unknown'}})")
    times = snap["times"]
    if not isinstance(times, list) or not times:
        err.append("times must be a non-empty list")
        return err
    prev = None
    for k, frame in enumerate(times):
        try:
            valid = utc(frame["valid_utc"])
        except (KeyError, SnapshotError) as exc:
            err.append(f"times[{k}]: {exc}")
            continue
        if prev is not None and valid <= prev:
            err.append(f"times[{k}]: valid_utc not strictly increasing")
        prev = valid
        lead = frame.get("lead_hours")
        if issue is not None:
            if valid < issue:
                err.append(f"times[{k}]: valid before forecast issue")
            elif lead is None or abs(lead - (valid - issue).total_seconds() / 3600) > 1e-6:
                err.append(f"times[{k}]: lead_hours must equal valid - issue")
        elif lead is not None:
            err.append(f"times[{k}]: lead_hours set without a forecast issue time")
        vals = frame.get("values", {})
        if set(vals) != set(fields):
            err.append(f"times[{k}]: values must cover exactly the declared fields")
        for name, arr in vals.items():
            if name not in FIELDS:
                continue
            try:
                data = unpack(arr)
            except (SnapshotError, ValueError, KeyError, TypeError) as exc:
                err.append(f"times[{k}].{name}: {exc}")
                continue
            if len(data) != grid.size:
                err.append(f"times[{k}].{name}: {len(data)} values for a {grid.nx}x{grid.ny} grid")
                continue
            _, lo, hi = FIELDS[name]
            fill = fields.get(name, {}).get("fill_value")
            bad = 0
            for v in data:
                if v is None or v == fill:
                    continue
                if not isinstance(v, (int, float)) or isinstance(v, bool) or math.isnan(v) or not lo - 1e-6 <= v <= hi + 1e-6:
                    bad += 1
            if bad:
                err.append(f"times[{k}].{name}: {bad} values outside {lo}..{hi} or non-numeric")
    if src_t is not None and dclass in ("observed", "analysis", "reanalysis") and prev is not None:
        first = utc(times[0]["valid_utc"])
        if not first <= src_t <= prev:
            err.append("provenance.source_time_utc outside the snapshot's valid times")
    if snap["integrity"].get("payload_sha256") != payload_digest(snap):
        err.append("integrity.payload_sha256 does not match the data (corrupted or edited)")
    return err


def require_valid(snap: dict) -> dict:
    errors = validate(snap)
    if errors:
        raise SnapshotError("; ".join(errors[:8]) + (f" (+{len(errors) - 8} more)" if len(errors) > 8 else ""))
    return snap


def field_values(snap: dict, frame: int, name: str) -> list:
    return unpack(snap["times"][frame]["values"][name])


def memory_bytes(snap: dict) -> dict:
    """Bytes per decoded float64 field-slice and per packed int16 slice (planning numbers)."""
    grid = LatLonGrid.from_dict(snap["grid"])
    return {"cells": grid.size, "float32_slice_bytes": grid.size * 4, "int16_slice_bytes": grid.size * 2,
            "slices": len(snap["times"]) * len(snap["fields"])}
