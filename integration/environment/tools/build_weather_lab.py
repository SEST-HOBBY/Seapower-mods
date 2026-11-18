"""ENV-01: build the MNO Environmental Playtest (Weather Lab) from an installed vanilla mission.

Never edits its source. Writes a new local mod folder:

    <output>/MNO-Environmental-Playtest/_info.ini
    <output>/MNO-Environmental-Playtest/missions/MNO Weather Lab - <source>.ini
    <output>/MNO-Environmental-Playtest/PLAYTEST_META.json

Modes:
  front       eight accelerated stages built in (clouds, rain, thunderstorm, sea state, fog
              and recovery), one every --interval seconds (default 300).
  procedural  stages sampled from the seeded procedural field at --lat/--lon, one per
              --interval seconds of mission time standing for --hours-per-stage of weather.

Status: BUILD-TESTED. Whether the game applies each stage is NOT TESTED IN GAME; see
docs/environment/ENV-PC-PLAYTEST.md.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from mno_env import RULES_VERSION  # noqa: E402
from mno_env.mission_adapter import native_state  # noqa: E402
from mno_env.mission_ini import PatchRefused, WeatherState, patch, read_mission_bytes, write_mission_text  # noqa: E402

FOLDER = "MNO-Environmental-Playtest"
FRONT = [
    WeatherState("Broken", 3),
    WeatherState("Broken_3", 4, rain=True),
    WeatherState("Overcast", 5, rain=True),
    WeatherState("Overcast", 7, rain=True, thunderstorm=True),
    WeatherState("Overcast", 8, rain=True, fog=True, thunderstorm=True),
    WeatherState("Broken_3", 6, rain=True, fog=True),
    WeatherState("Broken_2", 4, rain=False, fog=False),
    WeatherState("Scattered", 2),
]
EN_DESCRIPTION = ("MNO environmental test mission (not a release). Scripted weather changes every {interval} seconds: "
                  "clouds, rain, thunderstorm, sea state, fog, then recovery. Synthetic and accelerated. "
                  "The rest of the source scenario is unchanged.")
INFO = ("[Language_en]\nName=MNO - Environmental Playtest\n"
        "Description=Local test missions for Modern Naval Operations environment development. Not a release; remove "
        "this folder after testing.\n\n[Compatibility]\nApproximateVersion={version}\n")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _stages_at(st, t0, lat, lon, frames, hours_per_stage):
    return [native_state(st.sample(t0 + int(k * hours_per_stage * 3600), lat, lon).values, initial=(k == 0))
            for k in range(frames)]


def _variety(stages) -> tuple:
    """How much a stage list changes: distinct consecutive states, then total sea-state swing."""
    changes = sum(1 for a, b in zip(stages, stages[1:]) if a != b)
    swing = max(s.sea_state for s in stages) - min(s.sea_state for s in stages)
    kinds = len({(s.clouds, s.rain, s.thunderstorm) for s in stages})
    return (changes, kinds, swing)


def procedural_stages(lat, lon, frames, hours_per_stage, seed, start):
    """Stages sampled from the procedural field. Without --lat/--lon, the sample point is
    chosen deterministically: ahead of each storm along its track, at several distances, the
    candidate whose weather changes most over the stages wins (a front passing over)."""
    from mno_env import procedural
    from mno_env.clock import MnoEnvState, to_seconds
    from mno_env.geo import wrap_lon
    hours = max(int(math.ceil(hours_per_stage * (frames - 1))), 6)
    snap = procedural.generate(seed, start, hours=((hours + 5) // 6) * 6, step_hours=6)
    st = MnoEnvState(snap)
    t0 = to_seconds(start)
    if lat is None or lon is None:
        best = None
        for sm in procedural.active_storms(seed, start + dt.timedelta(hours=hours_per_stage * (frames - 1) / 2)):
            east = 1.0 if sm["kind"] == "extratropical" else -1.0  # tropical cyclones move west before recurving
            for ahead in (0.5, 1.0, 1.5, 2.0):
                for side in (-0.5, 0.0, 0.5):
                    clat = max(-70.0, min(70.0, sm["lat"] + side * sm["radius"]))
                    clon = wrap_lon(sm["lon"] + east * ahead * sm["radius"] / max(0.3, math.cos(math.radians(clat))))
                    score = _variety(_stages_at(st, t0, clat, clon, frames, hours_per_stage))
                    if best is None or score > best[0]:
                        best = (score, clat, clon)
        if best is None:
            best = (None, -54.0, -49.0)
        lat, lon = best[1], best[2]
    out = _stages_at(st, t0, lat, lon, frames, hours_per_stage)
    return out, {"snapshot_id": snap["snapshot_id"], "sample_lat": round(lat, 3), "sample_lon": round(lon, 3),
                 "variety": list(_variety(out))}


def mission_place_time(text: str) -> tuple[float, float, dt.datetime, int]:
    """Map centre and start of a mission. [Environment] Date=Y,M,D and Time=H,M are taken as
    LOCAL solar time and converted to UTC with round(longitude/15) hours: an ASSUMPTION
    (the file states no zone); returns (lat, lon, start_utc, offset_hours)."""
    import re
    def get(key):
        m = re.search(r"(?m)^" + key + r"[ \t]*=[ \t]*([^\r\n/]+)", text)
        if not m:
            raise ValueError(f"mission has no {key}")
        return m.group(1).strip()
    lat, lon = float(get("MapCenterLatitude")), float(get("MapCenterLongitude"))
    y, mo, d = (int(x) for x in get("Date").split(",")[:3])
    hh, mm = (int(x) for x in get("Time").split(",")[:2])
    off = round(lon / 15)
    local = dt.datetime(y, mo, d, hh, mm, tzinfo=dt.timezone.utc)
    return lat, lon, local - dt.timedelta(hours=off), off


def real_stages(lat, lon, start_utc, frames, hours_per_stage, source, raw_dir=None, offline=False):
    """Stages from official data at the mission's own place: ERA5 (recorded) or the ECMWF IFS
    forecast. A 5x5 grid at 0.5 degree around the point is fetched (two requests)."""
    from mno_env import openmeteo
    from mno_env.clock import MnoEnvState, to_seconds
    from mno_env.grid import LatLonGrid
    step = max(1, int(round(hours_per_stage)))
    hour0 = start_utc.replace(minute=0, second=0, microsecond=0)
    lat0 = min(88.0, max(-90.0, round(lat * 2) / 2 - 1.0))          # keep all five rows inside +-90
    lon0 = ((round(lon * 2) / 2 - 1.0 + 180.0) % 360.0) - 180.0      # inside [-180, 180)
    grid = LatLonGrid(lon0, lat0, 0.5, 0.5, 5, 5)
    span_h = math.ceil((start_utc - hour0).total_seconds() / 3600 + step * (frames - 1)) + 1
    snap = openmeteo.fetch_snapshot(source, grid, hour0, span_h, 1, campaign_start=hour0,
                                    raw_dir=raw_dir, offline=offline,
                                    statement=f"Recorded/forecast weather at the mission's own place and date ({hour0:%Y-%m-%d %H:%M}Z); not a forecast of any campaign year.")
    st = MnoEnvState(snap)
    t0 = to_seconds(start_utc.replace(second=0, microsecond=0))  # the mission's own minute, not the hour before
    out = []
    for k in range(frames):
        v = st.sample(t0 + k * step * 3600, lat, lon).values
        out.append(native_state(v, initial=(k == 0)))
    return out, {"snapshot_id": snap["snapshot_id"], "provider": snap["provenance"]["provider"],
                 "licence": snap["provenance"]["licence"], "attribution": snap["provenance"]["attribution"],
                 "source_start_utc": snap["campaign_mapping"]["source_start_utc"],
                 "sample_start_utc": start_utc.replace(second=0, microsecond=0).isoformat().replace("+00:00", "Z"),
                 "sample_lat": lat, "sample_lon": lon,
                 "hours_per_stage": step, "payload_sha256": snap["integrity"]["payload_sha256"]}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--source", type=Path, required=True, help="vanilla mission .ini (read only)")
    p.add_argument("--output", type=Path, required=True, help="folder that will receive " + FOLDER)
    p.add_argument("--mode", choices=("front", "procedural", "real"), default="front",
                   help="real = official data at the mission's own place and time (needs internet once)")
    p.add_argument("--real-source", choices=("era5", "ifs"), default="era5",
                   help="era5 = recorded weather on the mission's own date; ifs = today's ECMWF forecast at its place")
    p.add_argument("--real-start", default=None, help="override the start (UTC, e.g. 2026-11-18T00:00:00Z)")
    p.add_argument("--raw-dir", type=Path, default=None, help="save/replay the API responses here")
    p.add_argument("--offline", action="store_true", help="real mode from --raw-dir only, no network")
    p.add_argument("--interval", type=int, default=300)
    p.add_argument("--frames", type=int, default=8)
    p.add_argument("--lat", type=float, default=None, help="procedural sample point; default: the mission's map centre")
    p.add_argument("--storm-chaser", action="store_true",
                   help="procedural mode: sample wherever a passing storm gives the most varied stages, anywhere on the globe")
    p.add_argument("--lon", type=float, default=None)
    p.add_argument("--seed", default="mno-weather-lab-1")
    p.add_argument("--start-utc", default="2028-09-14T06:00:00Z")
    p.add_argument("--hours-per-stage", type=float, default=None,
                   help="hours of weather per stage (default: 1 in real mode, 3 in procedural mode)")
    p.add_argument("--game-version", default="0.9.3")
    p.add_argument("--mission-time", default="keep", help="HH,MM local start time for daylight testing, or keep")
    p.add_argument("--referenced-weather", choices=("refuse", "strip"), default="refuse")
    a = p.parse_args(argv)
    if not 2 <= a.frames <= 12:
        p.error("--frames must be 2..12")
    src_bytes = a.source.read_bytes()
    src_hash = sha256(src_bytes)
    target = a.output / FOLDER
    if target.exists():
        print(f"REFUSED: {target} already exists; inspect and remove it yourself (this tool never overwrites).", file=sys.stderr)
        return 3
    mission_time = None
    if a.mission_time != "keep":
        try:
            hh, mm = (int(x) for x in a.mission_time.split(","))
            if not (0 <= hh <= 23 and 0 <= mm <= 59):
                raise ValueError
            mission_time = (hh, mm)
        except ValueError:
            p.error("--mission-time must be HH,MM (00-23, 00-59) or keep")
    real_start = None
    if a.mode == "real":
        if a.hours_per_stage is not None and (a.hours_per_stage < 1 or a.hours_per_stage != int(a.hours_per_stage)):
            p.error("--hours-per-stage must be a whole number of hours (1 or more) in real mode")
        if a.real_start:
            try:
                real_start = dt.datetime.fromisoformat(a.real_start.replace("Z", "+00:00"))
            except ValueError:
                p.error(f"--real-start {a.real_start!r} is not an ISO date-time")
            if real_start.tzinfo is None:
                p.error("--real-start needs a time zone; add Z for UTC (e.g. 2025-09-14T06:00:00Z)")
            real_start = real_start.astimezone(dt.timezone.utc)
    if a.mode == "front":
        if a.frames > len(FRONT):
            p.error(f"front mode has {len(FRONT)} stages")
        stages, data_ref = FRONT[: a.frames], "built-in accelerated front"
    elif a.mode == "real":
        try:
            lat, lon, start, off = mission_place_time(read_mission_bytes(src_bytes))
            tz = dt.timedelta(hours=off)
            if mission_time is not None:  # the weather must match the clock the player will see
                start = (start + tz).replace(hour=mission_time[0], minute=mission_time[1]) - tz
            if real_start is not None:
                start = real_start
                local = start + tz
                if mission_time is None:  # set the mission clock to the chosen weather time
                    mission_time = (local.hour, local.minute)
                elif mission_time != (local.hour, local.minute):
                    p.error(f"--real-start is {local:%H:%M} local (UTC{off:+d} assumed) but --mission-time says "
                            f"{mission_time[0]:02d}:{mission_time[1]:02d}; give one of them")
            elif a.real_source == "ifs":  # today's forecast, at the mission's local clock time
                today_local = (dt.datetime.now(dt.timezone.utc) + tz).date()
                local = start + tz
                start = dt.datetime(today_local.year, today_local.month, today_local.day, local.hour, local.minute,
                                    tzinfo=dt.timezone.utc) - tz
            hps = a.hours_per_stage if a.hours_per_stage is not None else 1.0
            stages, data_ref = real_stages(lat, lon, start, a.frames, hps, a.real_source, a.raw_dir, a.offline)
            data_ref["utc_offset_assumed_h"] = off
        except Exception as exc:  # network, rate limit, missing keys: nothing is written
            print(f"REFUSED: real weather unavailable: {exc}", file=sys.stderr)
            return 5
    else:
        start = dt.datetime.fromisoformat(a.start_utc.replace("Z", "+00:00"))
        hps = a.hours_per_stage if a.hours_per_stage is not None else 3.0
        lat, lon = a.lat, a.lon
        if (lat is None or lon is None) and not a.storm_chaser:
            try:
                lat, lon, _, _ = mission_place_time(read_mission_bytes(src_bytes))
            except (ValueError, PatchRefused) as exc:
                p.error(f"procedural mode needs the mission's map centre or --lat/--lon ({exc})")
        stages, data_ref = procedural_stages(lat, lon, a.frames, hps, a.seed, start)
    description = EN_DESCRIPTION.format(interval=a.interval)
    if a.mode == "real":
        description = (f"MNO environmental test mission (not a release). Real weather at this map's centre from "
                       f"{data_ref['sample_start_utc']} ({'ERA5 reanalysis, recorded' if a.real_source == 'era5' else 'ECMWF IFS forecast'}), "
                       f"{'one real hour' if data_ref['hours_per_stage'] == 1 else str(data_ref['hours_per_stage']) + ' real hours'} "
                       f"every {a.interval} seconds. {data_ref['attribution']}. "
                       "The rest of the source scenario is unchanged.")
    try:
        text = read_mission_bytes(src_bytes)
        result, report = patch(text, stages, interval_s=a.interval, en_description=description,
                               referenced_weather=a.referenced_weather, mission_time=mission_time)
    except (PatchRefused, ValueError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    if sha256(a.source.read_bytes()) != src_hash:
        print("FAIL: the source changed while building; nothing written.", file=sys.stderr)
        return 4
    out_bytes = write_mission_text(result)
    mission = target / "missions" / f"MNO Weather Lab - {a.source.stem}.ini"
    mission.parent.mkdir(parents=True)
    mission.write_bytes(out_bytes)
    info = INFO.format(version=a.game_version).encode("utf-8")
    (target / "_info.ini").write_bytes(info)
    meta = {
        "status": "GENERATED - NOT TESTED IN GAME",
        "rules_version": RULES_VERSION,
        "source": str(a.source), "source_sha256": src_hash, "source_bytes": len(src_bytes),
        "mission": str(mission.relative_to(a.output)), "mission_sha256": sha256(out_bytes),
        "info_sha256": sha256(info),
        "mode": a.mode, "data": data_ref,
        "mission_time": "keep" if mission_time is None else f"{mission_time[0]},{mission_time[1]}", "interval_s": a.interval,
        "stages": [{"at_s": 0, **stages[0].__dict__}] + [{"at_s": x["time_s"], **x["state"]} for x in report.appended],
        "report": {k: v for k, v in report.__dict__.items() if k not in ("appended",)},
        "proves": "scenario-wide native weather changes at fixed mission times, if each stage is seen in game",
        "does_not_prove": "spatial weather cells, live environment graphics, GCO overlay, any physics effect",
    }
    (target / "PLAYTEST_META.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(target), "mission_sha256": meta["mission_sha256"], "source_sha256": src_hash,
                      "source_unchanged": True, "stages": len(stages), "triggers": [report.number_of_triggers_before, report.number_of_triggers_after],
                      "disabled_weather_only": report.disabled_weather_only, "stripped": report.stripped_mixed,
                      "warnings": report.warnings, "game_tested": False}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
