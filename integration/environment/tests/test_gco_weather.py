import datetime as dt
import tempfile
import unittest
import urllib.parse
from pathlib import Path
from unittest import mock

from helpers import UTC

from mno_env import gco_weather, openmeteo
from mno_env.clock import to_seconds


def synth(url, raw_dir=None, offline=False, pause_s=1.0):
    """Open-Meteo-shaped responses for exactly the requested points and dates (FORMAT fixture;
    values encode the latitude so tests can tell layers apart)."""
    q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    lats = [float(x) for x in q["latitude"][0].split(",")]
    d0, d1 = dt.date.fromisoformat(q["start_date"][0]), dt.date.fromisoformat(q["end_date"][0])
    times = [f"{d0 + dt.timedelta(days=k)}T{h:02d}:00" for k in range((d1 - d0).days + 1) for h in range(24)]
    n = len(times)
    out = []
    for lat in lats:
        if "marine" in url:
            out.append({"hourly_units": {"wave_height": "m", "wave_direction": "°", "wave_period": "s"},
                        "hourly": {"time": times, "wave_height": [2.0] * n, "wave_direction": [270.0] * n, "wave_period": [8.0] * n}})
        else:
            out.append({"hourly_units": {"pressure_msl": "hPa", "cloud_cover": "%", "precipitation": "mm", "temperature_2m": "°C",
                                         "wind_speed_10m": "m/s", "wind_direction_10m": "°", "cape": "J/kg", "visibility": "undefined"},
                        "hourly": {"time": times, "pressure_msl": [1000.0 + lat / 10] * n, "cloud_cover": [50.0] * n,
                                   "precipitation": [0.0] * n, "temperature_2m": [15.0] * n, "wind_speed_10m": [5.0] * n,
                                   "wind_direction_10m": [180.0] * n, "cape": [0.0] * n, "visibility": [None] * n}})
    return out


class TestGcoWeather(unittest.TestCase):
    def test_plan(self):
        spec = gco_weather.load_spec()
        tasks = gco_weather.plan(spec, 1)
        self.assertEqual([t.layer for t in tasks].count("tile"), 5)
        self.assertEqual([t.layer for t in tasks].count("season"), 26)
        self.assertEqual(tasks[5].campaign_start, dt.datetime(2028, 9, 14, tzinfo=UTC))
        self.assertEqual(tasks[5].source_start, dt.datetime(2025, 9, 14, tzinfo=UTC))
        season = [t for t in tasks if t.layer == "season"]
        for a, b in zip(season, season[1:]):  # contiguous, no gaps or overlaps
            self.assertEqual(a.source_start + dt.timedelta(hours=a.hours), b.source_start)
        self.assertLess(season[-1].source_start + dt.timedelta(hours=season[-1].hours), dt.datetime(2026, 9, 15, tzinfo=UTC))
        y2 = [t for t in gco_weather.plan(spec, 2) if t.task_id.startswith("gco-season-2024")]
        self.assertEqual(y2[0].source_start.year, 2024)
        self.assertEqual(y2[0].campaign_start, dt.datetime(2029, 9, 14, tzinfo=UTC))
        self.assertEqual(len({t.task_id for t in gco_weather.plan(spec, 3)}), len(gco_weather.plan(spec, 3)))

    def test_resume_after_rate_limit_and_layering(self):
        spec = gco_weather.load_spec()
        tasks = gco_weather.plan(spec, 1)[:8]  # tiles, opening grid, first two season chunks
        calls = {"n": 0}

        def limited(url, raw_dir=None, offline=False, pause_s=1.0):
            calls["n"] += 1
            if calls["n"] > 12:
                raise openmeteo.RateLimited("daily limit")
            return synth(url)
        with tempfile.TemporaryDirectory() as d:
            cache = Path(d)
            with mock.patch.object(openmeteo, "fetch", limited):
                r1 = gco_weather.run(tasks, cache, cache / "raw", log=lambda *_: None)
            self.assertFalse(r1["complete"])
            with mock.patch.object(openmeteo, "fetch", synth):
                r2 = gco_weather.run(tasks, cache, cache / "raw", log=lambda *_: None)
            self.assertTrue(r2["complete"])
            self.assertEqual(r2["already"], r1["done"])
            comp, warn = gco_weather.load_composite(cache, "save-seed", spec)
            self.assertEqual(warn, [])
            t = to_seconds(dt.datetime(2028, 9, 15, 6, tzinfo=UTC))
            s = comp.sample(t, 26.5, 56.5)
            self.assertEqual(s.sources["msl_pressure_hpa"], "ERA5:gco-tile-hormuz-20250914")
            self.assertEqual(s.sources["sea_ice_conc_pct"], "PROCEDURAL")  # ice always from the NSIDC-calibrated field
            self.assertEqual(comp.sample(t, -40, -150).sources["msl_pressure_hpa"], "ERA5:gco-global-20250914")
            t2 = to_seconds(dt.datetime(2028, 9, 25, tzinfo=UTC))  # after the opening week, inside season chunk 0
            self.assertEqual(comp.sample(t2, 26.5, 56.5).sources["msl_pressure_hpa"], "ERA5:gco-season-2025-00")
            t3 = to_seconds(dt.datetime(2029, 3, 1, tzinfo=UTC))  # not downloaded in this test
            self.assertEqual(comp.sample(t3, 0, 0).sources["msl_pressure_hpa"], "PROCEDURAL")

    def test_corrupt_snapshot_is_skipped(self):
        spec = gco_weather.load_spec()
        tasks = gco_weather.plan(spec, 1)[:1]
        with tempfile.TemporaryDirectory() as d:
            with mock.patch.object(openmeteo, "fetch", synth):
                gco_weather.run(tasks, Path(d), Path(d) / "raw", log=lambda *_: None)
            f = next(Path(d).glob("gco-tile-*.json.gz"))
            f.write_bytes(f.read_bytes()[:100])
            comp, warn = gco_weather.load_composite(Path(d), "s", spec)
            self.assertTrue(warn and "corrupt" in warn[0])
            self.assertEqual(comp.sample(to_seconds(dt.datetime(2028, 9, 15, tzinfo=UTC)), 26.5, 56.5).sources["msl_pressure_hpa"], "PROCEDURAL")


if __name__ == "__main__":
    unittest.main()
