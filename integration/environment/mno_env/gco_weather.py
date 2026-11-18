"""GCO long-run weather: plan, fetch (resumable) and load real recorded weather for a whole
campaign, with procedural fill. BUILD-TESTED offline; the downloads run on the owner's PC.

Spec: data/gco-weather-2028.json. Tasks, in fetch order:
  1. opening tiles (1 degree, chokepoints) and the opening grid (4 degree) for week 1;
  2. season chunks: 8-degree global grid, 14 days each, 26 per source year, for each source
     year in turn (2025 first).
Each task becomes one cached snapshot with a fixed id, so a rerun skips finished tasks and the
per-request raw responses make a half-finished task resume without repeating calls. When the
free API's daily limit is reached the build stops cleanly and the next run continues.
"""
from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass
from pathlib import Path

from . import openmeteo, procedural
from .cache import CacheError, MnoEnvDataProvider
from .clock import MnoEnvState, to_seconds
from .composite import MnoEnvComposite
from .grid import LatLonGrid
from .snapshot import utc

SPEC = Path(__file__).resolve().parents[1] / "data" / "gco-weather-2028.json"


@dataclass(frozen=True)
class Task:
    task_id: str
    layer: str          # tile | opening | season
    grid: LatLonGrid
    source_start: dt.datetime
    campaign_start: dt.datetime
    hours: int
    step_hours: int

    @property
    def points(self) -> int:
        return self.grid.nx * self.grid.ny

    def requests(self) -> int:
        return 2 * -(-self.points // openmeteo.BATCH)

    def location_calls(self) -> int:
        """Open-Meteo counts each location of a multi-location request; ranges over 14 days
        count extra. Planning number only (see docs/environment for the checked rule)."""
        days = self.hours / 24
        return 2 * self.points * max(1, -(-int(days) // 14))


def load_spec(path: Path = SPEC) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _source_for_year(spec: dict, year_index: int) -> dt.datetime:
    base = utc(spec["source_start_utc"])
    y = spec["season"]["source_years"][year_index]
    return base.replace(year=y)


def plan(spec: dict, years: int = 1) -> list[Task]:
    camp0 = utc(spec["campaign_start_utc"])
    src0 = utc(spec["source_start_utc"])
    days = spec["days_per_week"]
    tasks = []
    for t in spec["theatres"]:
        h, r = t["half_deg"], t["res"]
        n = int(round(2 * h / r)) + 1
        g = LatLonGrid(t["lon"] - h, t["lat"] - h, r, r, n, n)
        tasks.append(Task(f"gco-tile-{t['name']}-{src0:%Y%m%d}", "tile", g, src0, camp0, days * 24, 1))
    gl = spec["global"]
    ny = int(round((gl["lat_max"] - gl["lat_min"]) / gl["res"])) + 1
    tasks.append(Task(f"{gl['name']}-{src0:%Y%m%d}", "opening",
                      LatLonGrid(gl["lon_min"], gl["lat_min"], gl["res"], gl["res"], gl["nx"], ny), src0, camp0,
                      days * 24, spec["step_hours"]))
    se = spec["season"]
    res = se["res"]
    sg = LatLonGrid(-180.0, se["lat_min"], res, res, int(360 / res), int(round((se["lat_max"] - se["lat_min"]) / res)) + 1)
    for yi in range(min(years, len(se["source_years"]))):
        sstart = _source_for_year(spec, yi)
        cstart = camp0.replace(year=camp0.year + yi)
        for k in range(se["chunks_per_year"]):
            off = dt.timedelta(days=k * se["chunk_days"])
            tasks.append(Task(f"{se['name']}-{sstart:%Y}-{k:02d}", "season", sg, sstart + off, cstart + off,
                              se["chunk_days"] * 24, se["step_hours"]))
    return tasks


def run(tasks: list[Task], cache: Path, raw_dir: Path, *, offline: bool = False, log=print) -> dict:
    """Fetch every task not yet cached. Returns a progress summary; never raises for a rate limit."""
    prov = MnoEnvDataProvider(cache)
    have = {e["snapshot_id"] for e in prov.manifest()["snapshots"]}
    done = skipped = 0
    for i, t in enumerate(tasks):
        if t.task_id in have:
            skipped += 1
            continue
        try:
            snap = openmeteo.fetch_snapshot("era5", t.grid, t.source_start, t.hours, t.step_hours,
                                            campaign_start=t.campaign_start, raw_dir=raw_dir, offline=offline,
                                            pack=True, snapshot_id=t.task_id, log=log,
                                            statement=(f"ERA5 weather recorded from {t.source_start:%Y-%m-%d} replayed from campaign "
                                                       f"{t.campaign_start:%Y-%m-%d}; real past weather, not a forecast of 2028-2029."))
        except openmeteo.RateLimited as exc:
            log(f"stopped at task {i + 1}/{len(tasks)} ({t.task_id}): {exc}")
            return {"complete": False, "done": done, "already": skipped, "total": len(tasks), "stopped_at": t.task_id}
        prov.add(snap)
        done += 1
        log(f"[{i + 1}/{len(tasks)}] cached {t.task_id} ({t.points} points)")
    return {"complete": True, "done": done, "already": skipped, "total": len(tasks), "stopped_at": None}


class OnDemandProcedural:
    """Procedural weather for ANY campaign time: 72-hour windows generated when first needed
    (aligned to 72-hour blocks from the campaign start, at most four kept)."""

    WINDOW_H = 72

    def __init__(self, seed: str, campaign_start: dt.datetime, res_deg: float = 4.0):
        self.seed, self.start, self.res = seed, campaign_start, res_deg
        self._states: dict = {}
        self.fields = list(procedural.PACK)

    def _state(self, campaign_seconds: int) -> MnoEnvState:
        k = (campaign_seconds - to_seconds(self.start)) // (self.WINDOW_H * 3600)
        if k not in self._states:
            if len(self._states) >= 4:
                self._states.pop(next(iter(self._states)))
            w0 = self.start + dt.timedelta(hours=int(k) * self.WINDOW_H)
            self._states[k] = MnoEnvState(procedural.generate(self.seed, w0, hours=self.WINDOW_H, res_deg=self.res))
        return self._states[k]

    def sample(self, campaign_seconds: int, lat: float, lon: float, names=None):
        return self._state(campaign_seconds).sample(campaign_seconds, lat, lon, names)


def load_composite(cache: Path, seed: str, spec: dict | None = None) -> tuple[MnoEnvComposite, list[str]]:
    """Composite for a GCO save: every cached GCO snapshot (finest first), procedural fallback.
    Returns (composite, warnings). A corrupt or missing snapshot is skipped with a warning."""
    spec = spec or load_spec()
    order = {"tile": 0, "opening": 1, "season": 2}
    prov = MnoEnvDataProvider(cache)
    warnings, layers = [], []
    try:
        entries = prov.manifest()["snapshots"]
    except CacheError as exc:
        entries, _ = [], warnings.append(str(exc))
    for t in sorted(plan(spec, years=len(spec["season"]["source_years"])), key=lambda t: (order[t.layer], t.task_id)):
        if not any(e["snapshot_id"] == t.task_id for e in entries):
            continue
        try:
            # tiles feather in space and time, the opening grid in time (handover to the season), season chunks not at all
            layers.append((f"ERA5:{t.task_id}", MnoEnvState(prov.load(t.task_id)), t.layer == "tile", t.layer in ("tile", "opening")))
        except CacheError as exc:
            warnings.append(f"{t.task_id}: {exc}")
    fb = OnDemandProcedural(seed, utc(spec["campaign_start_utc"]))
    return MnoEnvComposite(layers, ("PROCEDURAL", fb)), warnings
