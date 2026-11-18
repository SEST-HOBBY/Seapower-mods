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
        for k, (lat0, lon0, vlat, vlon, _d, radius, _w) in enumerate(procedural.storms(seed)):
            speed = math.hypot(vlat, vlon) or 1.0
            for ahead in (0.5, 1.0, 1.5, 2.0):
                for side in (-0.5, 0.0, 0.5):
                    clat = max(-70.0, min(70.0, lat0 + radius * (ahead * vlat - side * vlon) / speed))
                    clon = wrap_lon(lon0 + radius * (ahead * vlon + side * vlat) / speed)
                    score = _variety(_stages_at(st, t0, clat, clon, frames, hours_per_stage))
                    if best is None or score > best[0]:
                        best = (score, clat, clon)
        lat, lon = best[1], best[2]
    out = _stages_at(st, t0, lat, lon, frames, hours_per_stage)
    return out, {"snapshot_id": snap["snapshot_id"], "sample_lat": round(lat, 3), "sample_lon": round(lon, 3),
                 "variety": list(_variety(out))}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--source", type=Path, required=True, help="vanilla mission .ini (read only)")
    p.add_argument("--output", type=Path, required=True, help="folder that will receive " + FOLDER)
    p.add_argument("--mode", choices=("front", "procedural"), default="front")
    p.add_argument("--interval", type=int, default=300)
    p.add_argument("--frames", type=int, default=8)
    p.add_argument("--lat", type=float, default=None, help="procedural sample point; default: on the first storm's track")
    p.add_argument("--lon", type=float, default=None)
    p.add_argument("--seed", default="mno-weather-lab-1")
    p.add_argument("--start-utc", default="2028-09-14T06:00:00Z")
    p.add_argument("--hours-per-stage", type=float, default=3.0)
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
    if a.mode == "front":
        if a.frames > len(FRONT):
            p.error(f"front mode has {len(FRONT)} stages")
        stages, data_ref = FRONT[: a.frames], "built-in accelerated front"
    else:
        start = dt.datetime.fromisoformat(a.start_utc.replace("Z", "+00:00"))
        stages, data_ref = procedural_stages(a.lat, a.lon, a.frames, a.hours_per_stage, a.seed, start)
    mission_time = None
    if a.mission_time != "keep":
        try:
            hh, mm = (int(x) for x in a.mission_time.split(","))
            mission_time = (hh, mm)
        except ValueError:
            p.error("--mission-time must be HH,MM or keep")
    try:
        text = read_mission_bytes(src_bytes)
        result, report = patch(text, stages, interval_s=a.interval, en_description=EN_DESCRIPTION.format(interval=a.interval),
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
        "mode": a.mode, "data": data_ref, "mission_time": a.mission_time, "interval_s": a.interval,
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
