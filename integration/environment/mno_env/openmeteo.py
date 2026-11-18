"""Official model data through Open-Meteo's JSON API -> mno.environment.snapshot.v1. BUILD-TESTED.

Open-Meteo redistributes official model output as JSON, which avoids GRIB readers:
- `era5`: ECMWF ERA5 reanalysis (Copernicus Climate Change Service), hourly, 1940 to about
  five days ago, 0.25 degree. data_class "reanalysis". This is the weather that HAPPENED.
- `ifs`: ECMWF IFS HRES open-data forecast (0.25 degree), up to about 10 days ahead.
  data_class "forecast".
- waves from the Marine API: `era5_ocean` (ECMWF ERA5 ocean-wave reanalysis) with `era5`;
  `ecmwf_wam025` (ECMWF WAM 0.25 degree forecast) with `ifs`.
Each call asks for many grid points at once (comma-separated coordinates); the API answers
with one object per point, in order. Points over land have no wave values (None).

Conversions: precipitation is the sum over the preceding hour, so mm per hour directly; wind
speed (m/s) and direction (degrees, coming FROM) -> u = -s sin d, v = -s cos d; CAPE is turned
into `convective_risk_idx` = min(1, CAPE/1500) x min(1, precip/1 mm/h), a DERIVED risk, not
observed lightning. A field whose values are all missing (e.g. IFS visibility) is dropped.

Licences: Open-Meteo data CC BY 4.0 ("Weather data by Open-Meteo.com"); ERA5 contains
modified Copernicus Climate Change Service information; ECMWF open data CC BY 4.0.
Free API use is for non-commercial purposes; check https://open-meteo.com/en/terms before
shipping any converted data with MNO.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from .grid import LatLonGrid
from .ingest import IngestError, build
from .snapshot import iso, pack_int16, seal

# int16 packing scales (value = raw x scale): keeps a year of coarse data small on disk
PACK_SCALES = {"msl_pressure_hpa": 0.1, "cloud_fraction_pct": 0.1, "precip_rate_mm_h": 0.01, "air_temp_2m_c": 0.01,
               "wind_u10_ms": 0.01, "wind_v10_ms": 0.01, "convective_risk_idx": 0.001, "visibility_km": 0.01,
               "wave_hs_m": 0.01, "wave_dir_deg": 0.1, "wave_tm_s": 0.01}

WEATHER_VARS = ("pressure_msl", "cloud_cover", "precipitation", "temperature_2m", "wind_speed_10m",
                "wind_direction_10m", "cape", "visibility")
WAVE_VARS = ("wave_height", "wave_direction", "wave_period")
EXPECTED_UNITS = {"pressure_msl": "hPa", "cloud_cover": "%", "precipitation": "mm", "temperature_2m": "°C",
                  "wind_speed_10m": "m/s", "wind_direction_10m": "°", "cape": "J/kg", "visibility": "m",
                  "wave_height": "m", "wave_direction": "°", "wave_period": "s"}
ENDPOINTS = {"era5": "https://archive-api.open-meteo.com/v1/archive", "ifs": "https://api.open-meteo.com/v1/forecast",
             "marine": "https://marine-api.open-meteo.com/v1/marine"}
BATCH = 50


class RateLimited(IngestError):
    pass


def grid_points(grid: LatLonGrid) -> list[tuple[float, float]]:
    return [(round(grid.lat(j), 4), round(((grid.lon(i) + 180) % 360) - 180, 4)) for j in range(grid.ny) for i in range(grid.nx)]


def urls(source: str, points, start: dt.datetime, end: dt.datetime, waves: bool = True) -> list[tuple[str, str]]:
    """[(kind, url)] for weather and (optionally) waves, BATCH points per request."""
    if source not in ("era5", "ifs"):
        raise ValueError("source must be era5 or ifs")
    out = []
    for k in range(0, len(points), BATCH):
        chunk = points[k:k + BATCH]
        base = {"latitude": ",".join(str(p[0]) for p in chunk), "longitude": ",".join(str(p[1]) for p in chunk),
                "start_date": start.date().isoformat(), "end_date": end.date().isoformat(), "timezone": "GMT"}
        w = dict(base, hourly=",".join(WEATHER_VARS), wind_speed_unit="ms")
        w["models"] = "era5" if source == "era5" else "ecmwf_ifs025"
        out.append(("weather", ENDPOINTS[source] + "?" + urllib.parse.urlencode(w)))
        if waves:
            m = dict(base, hourly=",".join(WAVE_VARS))
            m["models"] = "era5_ocean" if source == "era5" else "ecmwf_wam025"  # name the wave model; never a blend
            out.append(("marine", ENDPOINTS["marine"] + "?" + urllib.parse.urlencode(m)))
    return out


# Free-tier limits (Open-Meteo terms, checked 18 Nov 2026): under 10,000 calls a day, 5,000 an
# hour and 600 a minute, per internet address. A request costs
#   locations x max(1, variables/10 x max(1, days/14))
# calls, so batching locations saves HTTP requests but not quota. The pacer keeps a rolling
# record of what was spent and waits before a request would pass these budgets.
MINUTE_BUDGET = 540
HOUR_BUDGET = 4600
_now = time.monotonic   # replaced in tests
_sleep = time.sleep     # replaced in tests
_spent: list = []       # (monotonic time, cost)


def request_cost(url: str) -> float:
    q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    locs = len(q.get("latitude", [""])[0].split(","))
    nvars = len(q.get("hourly", [""])[0].split(","))
    try:
        d0 = dt.date.fromisoformat(q["start_date"][0])
        d1 = dt.date.fromisoformat(q["end_date"][0])
        days = (d1 - d0).days + 1
    except (KeyError, ValueError):
        days = 7
    return locs * max(1.0, nvars / 10.0 * max(1.0, days / 14.0))


def _pace(cost: float) -> None:
    while True:
        now = _now()
        _spent[:] = [(t, c) for t, c in _spent if now - t < 3600]
        minute = sum(c for t, c in _spent if now - t < 60)
        hour = sum(c for _, c in _spent)
        fits = minute + cost <= MINUTE_BUDGET and hour + cost <= HOUR_BUDGET
        if fits or not _spent:  # a single request larger than a budget goes alone, into an empty window
            _spent.append((now, cost))
            return
        if hour + cost > HOUR_BUDGET:
            oldest = min(t for t, _ in _spent)
            wait = 3600 - (now - oldest) + 1
        else:
            recent = [t for t, _ in _spent if now - t < 60]
            wait = (60 - (now - min(recent)) + 1) if recent else 1.0
        _sleep(max(1.0, wait))


def _immutable(url: str) -> bool:
    """Reanalysis responses never change, so a saved copy can stand in for a new request.
    Forecast responses change every model run, so online runs always fetch them fresh."""
    return "archive-api." in url or "models=era5_ocean" in url


def fetch(url: str, raw_dir: Path | None = None, offline: bool = False, pause_s: float = 0.0, log=None) -> list:
    """GET one URL (or replay it from raw_dir). Always returns a list of per-point objects.
    Raises RateLimited at the DAILY limit; waits through minute and hour limits."""
    import hashlib
    key = hashlib.sha256(url.encode()).hexdigest()[:24] + ".json"
    saved = raw_dir is not None and (Path(raw_dir) / key).exists()
    if saved and (offline or _immutable(url)):
        data = json.loads((Path(raw_dir) / key).read_text(encoding="utf-8"))
    elif offline:
        raise IngestError(f"offline and no saved response for {url[:90]}...")
    else:
        req = urllib.request.Request(url, headers={"User-Agent": "MNO-environment-tools/1"})
        cost = request_cost(url)
        waits = 0
        attempt = 0
        while True:
            _pace(cost)
            try:
                with urllib.request.urlopen(req, timeout=90) as r:
                    data = json.loads(r.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", "replace")
                if exc.code == 429 and "Daily" in body:
                    raise RateLimited("Open-Meteo daily request limit reached for this internet address; run again tomorrow") from None
                if exc.code == 429 and ("Hourly" in body or "Minutely" in body) and waits < 16:
                    pause = 300 if "Hourly" in body else 65
                    if log:
                        log(f"  {'hourly' if pause == 300 else 'per-minute'} limit: waiting {pause} s, then continuing")
                    _sleep(pause)
                    waits += 1
                    continue
                if exc.code in (429, 500, 502, 503, 504) and attempt < 4:
                    attempt += 1
                    _sleep(10 * attempt)
                    continue
                raise IngestError(f"HTTP {exc.code}: {body[:200]}") from None
            except (urllib.error.URLError, ConnectionError, TimeoutError) as exc:
                if attempt < 4:
                    attempt += 1
                    _sleep(10 * attempt)
                    continue
                raise IngestError(f"network error after 5 tries: {exc}") from None
        if pause_s:
            _sleep(pause_s)
        if raw_dir is not None and _complete(data):  # never keep a response with unpublished hours
            Path(raw_dir).mkdir(parents=True, exist_ok=True)
            tmp = Path(raw_dir) / (key + ".tmp")
            tmp.write_text(json.dumps(data), encoding="utf-8")
            tmp.replace(Path(raw_dir) / key)
    if isinstance(data, dict):
        if data.get("error"):
            raise IngestError(f"Open-Meteo error: {data.get('reason')}")
        data = [data]
    return data


def _complete(data) -> bool:
    """False when a response ends in hours that are null at every point although earlier hours
    have values: data not yet published (ERA5 runs about five days late). Such a response must
    not be saved, or a later rerun would replay the gap forever."""
    objs = data if isinstance(data, list) else [data]
    if not objs or not all(isinstance(o, dict) and "hourly" in o for o in objs):
        return False
    n = len(objs[0]["hourly"].get("time", []))
    for key in ("pressure_msl", "wave_height"):
        cols = [o["hourly"].get(key) for o in objs if o["hourly"].get(key) is not None]
        if not cols:
            continue
        have = [any(c[i] is not None for c in cols if i < len(c)) for i in range(n)]
        if any(have) and not have[-1]:
            return False
    return True


def align(points, responses: list, what: str) -> list:
    """Return responses in the order of `points`. The docs do not promise that a
    multi-location answer keeps the request order, so each response is matched to the requested
    point nearest its returned (grid-snapped) latitude/longitude. Raises if the match is not
    one-to-one."""
    if len(responses) != len(points):
        raise IngestError(f"{what}: {len(responses)} responses for {len(points)} points")
    if any("latitude" not in r or "longitude" not in r for r in responses):
        return responses  # older saved fixtures without coordinates: keep the order as sent

    def d2(p, r):
        dlon = ((r["longitude"] - p[1] + 180) % 360) - 180
        return (r["latitude"] - p[0]) ** 2 + dlon ** 2
    # Normal case: the answer keeps the request order. Open-Meteo snaps each point to its model
    # cell (and the marine API may pick a nearby sea cell), so allow about one coarse cell.
    if all(d2(p, r) <= 1.0 ** 2 for p, r in zip(points, responses)):
        return responses
    out = [None] * len(points)
    for r in responses:
        k = min(range(len(points)), key=lambda i: d2(points[i], r))
        if out[k] is not None:
            raise IngestError(f"{what}: two responses match point {points[k]}; cannot tell them apart")
        out[k] = r
    return out


def _check_units(obj: dict, names) -> None:
    units = obj.get("hourly_units", {})
    for n in names:
        if units.get(n) == "undefined":  # the model does not provide this variable: values are null
            obj["hourly"][n] = [None] * len(obj["hourly"]["time"])
            continue
        if n in units:
            want = EXPECTED_UNITS[n]
            if units[n] not in (want if isinstance(want, tuple) else (want,)):
                raise IngestError(f"{n}: unit {units[n]!r}, expected {want!r}")


def assemble(points, weather: list, marine: list | None, times: list[dt.datetime]) -> dict:
    """{valid time: {canonical field: [value per point]}} from per-point responses."""
    if len(weather) != len(points) or (marine is not None and len(marine) != len(points)):
        raise IngestError("response count does not match the requested points")
    want = [iso(t)[:16] for t in times]
    frames = {t: {} for t in times}
    cols = {n: [] for n in ("msl_pressure_hpa", "cloud_fraction_pct", "precip_rate_mm_h", "air_temp_2m_c",
                            "wind_u10_ms", "wind_v10_ms", "convective_risk_idx", "visibility_km",
                            "wave_hs_m", "wave_dir_deg", "wave_tm_s")}
    per_time = {t: {n: [] for n in cols} for t in times}
    for k, w in enumerate(weather):
        _check_units(w, WEATHER_VARS)
        h = w["hourly"]
        index = {s: i for i, s in enumerate(h["time"])}
        m = marine[k] if marine is not None else None
        mi = {}
        if m is not None:
            _check_units(m, WAVE_VARS)
            mi = {s: i for i, s in enumerate(m["hourly"]["time"])}
        for t, s in zip(times, want):
            if s not in index:
                raise IngestError(f"point {k}: no data for {s}Z")
            i = index[s]
            g = lambda n: (h.get(n) or [None] * len(h["time"]))[i]  # noqa: E731
            spd, dirn, pr = g("wind_speed_10m"), g("wind_direction_10m"), g("precipitation")
            u = v = None
            if spd is not None and dirn is not None:
                u, v = -spd * math.sin(math.radians(dirn)), -spd * math.cos(math.radians(dirn))
            cape = g("cape")
            risk = None if cape is None or pr is None else min(1.0, cape / 1500.0) * min(1.0, pr / 1.0)
            vis = g("visibility")
            row = per_time[t]
            row["msl_pressure_hpa"].append(g("pressure_msl"))
            row["cloud_fraction_pct"].append(g("cloud_cover"))
            row["precip_rate_mm_h"].append(None if pr is None else max(0.0, pr))
            row["air_temp_2m_c"].append(g("temperature_2m"))
            row["wind_u10_ms"].append(u)
            row["wind_v10_ms"].append(v)
            row["convective_risk_idx"].append(risk)
            row["visibility_km"].append(None if vis is None else min(100.0, vis / 1000.0))
            for src, dst in (("wave_height", "wave_hs_m"), ("wave_direction", "wave_dir_deg"), ("wave_period", "wave_tm_s")):
                val = None
                if m is not None and s in mi:
                    val = (m["hourly"].get(src) or [None] * len(mi))[mi[s]]
                row[dst].append(val)
    for t in times:
        frames[t] = {n: vals for n, vals in per_time[t].items()}
    present = [n for n in cols if any(v is not None for t in times for v in frames[t][n])]
    core = [n for n in ("msl_pressure_hpa", "wind_u10_ms") if n in present]
    if not core:
        raise IngestError("no pressure or wind values at all (dates not yet published, or not available for this model)")
    if marine is not None and "wave_hs_m" in present:
        for t in times:
            if all(v is None for v in frames[t]["wave_hs_m"]):
                raise IngestError(f"no wave data for {iso(t)} at any point (not yet published?); end the request earlier")
    for t in times:  # ERA5 is published about five days late: a tail of empty hours is not data
        if core and all(v is None for n in core for v in frames[t][n]):
            raise IngestError(f"no data for {iso(t)} at any point (not yet published?); end the request earlier")
    return {t: {n: frames[t][n] for n in present} for t in times}


def to_snapshot(source: str, grid: LatLonGrid, frames: dict, *, campaign_start: dt.datetime,
                source_start: dt.datetime, created: dt.datetime, statement: str | None = None, pack: bool = False) -> dict:
    if source_start.tzinfo is None or campaign_start.tzinfo is None \
            or source_start.utcoffset() != dt.timedelta(0) or campaign_start.utcoffset() != dt.timedelta(0):
        raise ValueError("source and campaign times must be UTC")
    times = sorted(frames)
    names = list(frames[times[0]])
    has_waves = any(n.startswith("wave_") for n in names)
    kind = "reanalysis" if source == "era5" else "forecast"
    kinds = {n: ("derived_risk" if n == "convective_risk_idx" else kind) for n in names}
    deriv = {"convective_risk_idx": "min(1, CAPE/1500 J/kg) x min(1, precipitation / 1 mm/h); a risk index, not observed lightning"}
    if source == "era5":
        prov = {"provider": "Open-Meteo (ECMWF ERA5" + (" / ERA5-Ocean" if has_waves else "") + ", Copernicus C3S)",
                "product": "ERA5 hourly reanalysis via Open-Meteo Historical API" + (" and Marine API" if has_waves else ""),
                "product_version": "era5" + (" + era5_ocean" if has_waves else ""),
                "licence": "CC BY 4.0 (Open-Meteo); contains modified Copernicus Climate Change Service information",
                "attribution": "Weather data by Open-Meteo.com; Copernicus Climate Change Service (ERA5" + (", ERA5-Ocean" if has_waves else "") + ")",
                "source_url": ENDPOINTS["era5"] + (" ; " + ENDPOINTS["marine"] if has_waves else ""),
                "downloaded_utc": iso(created), "source_time_utc": iso(times[0]), "forecast_issue_utc": None}
        issue = None
    else:
        issue = times[0]
        prov = {"provider": "Open-Meteo (ECMWF IFS" + (" and ECMWF WAM" if has_waves else "") + " open data)",
                "product": "ECMWF IFS 0.25 deg forecast via Open-Meteo" + (" with ECMWF WAM 0.25 deg waves" if has_waves else ""),
                "product_version": "ecmwf_ifs025" + (" + ecmwf_wam025" if has_waves else ""),
                "licence": "CC BY 4.0 (Open-Meteo; ECMWF open data)",
                "attribution": "Weather data by Open-Meteo.com; Copyright ECMWF",
                "source_url": ENDPOINTS["ifs"] + (" ; " + ENDPOINTS["marine"] if has_waves else ""), "downloaded_utc": iso(created), "source_time_utc": iso(times[0]),
                "forecast_issue_utc": iso(issue),
                "issue_time_note": "the API does not report the model run; the first valid time is used as the issue time"}
    offset = int((campaign_start - source_start).total_seconds())
    mapping = {"mode": "historical_analogue" if source == "era5" else "current_analogue", "offset_seconds": offset,
               "campaign_start_utc": iso(campaign_start), "source_start_utc": iso(source_start),
               "statement": statement or (
                   f"Recorded weather (ERA5) from {iso(source_start)} replayed from campaign {iso(campaign_start)}; real past weather, not a forecast of the campaign date."
                   if source == "era5" else
                   f"ECMWF forecast for {iso(source_start)} onwards replayed from campaign {iso(campaign_start)}; a real forecast of the source dates, not a forecast of the campaign date.")}
    frames_list = [(t, (None if issue is None else (t - issue).total_seconds() / 3600.0), frames[t]) for t in times]
    sid = (f"openmeteo-{source}-{source_start:%Y%m%dT%H%M}-{len(times)}f-"
           f"{(times[-1] - times[0]).total_seconds() / 3600:g}h-{grid.lat_min:g}_{grid.lon_min:g}-{grid.lat_step:g}x{grid.lon_step:g}-{grid.nx}x{grid.ny}"
           f"{'-waves' if has_waves else '-nowaves'}" + (f"-got{created:%Y%m%dT%H%M}" if source != "era5" else ""))
    snap = build(snapshot_id=sid, data_class=kind, provenance=prov, mapping=mapping, grid=grid, frames=frames_list,
                 kinds=kinds, derivations=deriv, created=created,
                 uncertainty={n: {"type": "model", "note": "reanalysis/model value at grid point; no per-point uncertainty from the API"} for n in names})
    if pack:
        for fr in snap["times"]:
            fr["values"] = {n: pack_int16(v, PACK_SCALES[n]) for n, v in fr["values"].items()}
        seal(snap)
    return snap


def fetch_snapshot(source: str, grid: LatLonGrid, start: dt.datetime, hours: int, step_hours: int, *,
                   campaign_start: dt.datetime, waves: bool = True, raw_dir: Path | None = None,
                   offline: bool = False, created: dt.datetime | None = None, statement: str | None = None,
                   pack: bool = False, snapshot_id: str | None = None, log=None) -> dict:
    if start.tzinfo is None or campaign_start.tzinfo is None:
        raise ValueError("start and campaign_start must carry a time zone (use Z for UTC)")
    start = start.astimezone(dt.timezone.utc)
    campaign_start = campaign_start.astimezone(dt.timezone.utc)
    if start.minute or start.second or start.microsecond:
        raise ValueError(f"start must be a whole UTC hour, got {start.isoformat()}")
    times = [start + dt.timedelta(hours=h) for h in range(0, hours + 1, step_hours)]
    pts = grid_points(grid)
    weather, marine = [], ([] if waves else None)
    todo = urls(source, pts, times[0], times[-1], waves)
    for n, (kind, url) in enumerate(todo, start=1):
        if log and len(todo) > 4:
            log(f"    request {n}/{len(todo)} ({kind})")
        q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        chunk = list(zip((float(x) for x in q["latitude"][0].split(",")), (float(x) for x in q["longitude"][0].split(","))))
        part = align(chunk, fetch(url, raw_dir, offline, log=log), kind)
        (weather if kind == "weather" else marine).extend(part)
    frames = assemble(pts, weather, marine, times)
    created = created or dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    snap = to_snapshot(source, grid, frames, campaign_start=campaign_start, source_start=start, created=created,
                       statement=statement, pack=pack)
    if snapshot_id:
        snap["snapshot_id"] = snapshot_id
    return snap
