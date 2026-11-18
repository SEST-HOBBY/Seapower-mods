"""Open-Meteo / official model data. Fixtures are two REAL responses (ECMWF IFS forecast and
wave model, 20 points over the Drake Passage, issued for 18 Nov 2026) saved by the tool."""
import contextlib
import copy
import datetime as dt
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from helpers import ENV_ROOT, HERE, HORMUZ, UTC

from mno_env import openmeteo, snapshot
from mno_env.clock import MnoEnvState, to_seconds
from mno_env.grid import LatLonGrid

sys.path.insert(0, str(ENV_ROOT / "tools"))
import build_weather_lab  # noqa: E402

RAW = HERE / "fixtures" / "openmeteo"
GRID = LatLonGrid(-70.0, -60.0, 2.0, 2.0, 5, 4)
START = dt.datetime(2026, 11, 18, 0, tzinfo=UTC)
CAMPAIGN = dt.datetime(2028, 11, 18, tzinfo=UTC)
CREATED = dt.datetime(2026, 11, 18, 15, tzinfo=UTC)


def drake():
    return openmeteo.fetch_snapshot("ifs", GRID, START, 24, 6, campaign_start=CAMPAIGN, raw_dir=RAW, offline=True, created=CREATED)


class TestOpenMeteo(unittest.TestCase):
    def test_offline_replay_of_real_responses(self):
        s = drake()
        self.assertEqual(snapshot.validate(s), [])
        self.assertEqual(s["data_class"], "forecast")
        self.assertIn("ECMWF", s["provenance"]["attribution"])
        self.assertNotIn("visibility_km", s["fields"])  # IFS returns none: dropped, not invented
        self.assertEqual(s["fields"]["convective_risk_idx"]["kind"], "derived_risk")
        self.assertEqual(s["campaign_mapping"]["offset_seconds"], int((CAMPAIGN - START).total_seconds()))
        st = MnoEnvState(s)
        v = st.sample(to_seconds(CAMPAIGN), -58, -65).values
        self.assertTrue(980 < v["msl_pressure_hpa"] < 1040)
        self.assertTrue(0 < v["wave_hs_m"] < 15)
        self.assertEqual(snapshot.dumps(s), snapshot.dumps(drake()))  # deterministic

    def test_requests(self):
        u = openmeteo.urls("era5", openmeteo.grid_points(GRID), START, START, waves=True)
        self.assertEqual([k for k, _ in u], ["weather", "marine"])
        self.assertIn("models=era5", u[0][1])
        self.assertIn("models=era5_ocean", u[1][1])
        self.assertIn("wind_speed_unit=ms", u[0][1])
        big = openmeteo.grid_points(LatLonGrid(-180, -80, 4, 4, 90, 41))
        self.assertEqual(len(openmeteo.urls("ifs", big, START, START, waves=False)), -(-len(big) // openmeteo.BATCH))
        with self.assertRaises(openmeteo.IngestError):
            openmeteo.fetch("https://example.invalid/x", RAW, offline=True)

    def test_units_and_undefined(self):
        weather = json.loads(next(p for p in RAW.iterdir() if "pressure_msl" in p.read_text()).read_text())
        bad = copy.deepcopy(weather)
        bad[0]["hourly_units"]["wind_speed_10m"] = "km/h"
        times = [START]
        with self.assertRaises(openmeteo.IngestError):
            openmeteo.assemble(openmeteo.grid_points(GRID), bad, None, times)
        und = copy.deepcopy(weather)
        for w in und:
            w["hourly_units"]["cape"] = "undefined"  # ERA5 for 1987 answers like this
        frames = openmeteo.assemble(openmeteo.grid_points(GRID), und, None, times)
        self.assertNotIn("convective_risk_idx", frames[START])
        self.assertIn("msl_pressure_hpa", frames[START])
        with self.assertRaises(openmeteo.IngestError):
            openmeteo.assemble(openmeteo.grid_points(GRID)[:5], weather, None, times)

    def test_wind_components(self):
        weather = json.loads(next(p for p in RAW.iterdir() if "pressure_msl" in p.read_text()).read_text())
        one = copy.deepcopy(weather[:1])
        one[0]["hourly"]["wind_speed_10m"][0] = 10.0
        one[0]["hourly"]["wind_direction_10m"][0] = 270  # from the west -> blowing east
        f = openmeteo.assemble([(0, 0)], one, None, [START])[START]
        self.assertAlmostEqual(f["wind_u10_ms"][0], 10.0)
        self.assertAlmostEqual(f["wind_v10_ms"][0], 0.0, places=9)


@unittest.skipUnless(HORMUZ.exists(), "vanilla export not present")
class TestRealWeatherLab(unittest.TestCase):
    def test_mission_place_time(self):
        lat, lon, start, off = build_weather_lab.mission_place_time(HORMUZ.read_bytes().decode("utf-8"))
        self.assertEqual((lat, lon, off), (25.78, 55.74, 4))
        self.assertEqual(start, dt.datetime(1987, 7, 20, 22, 20, tzinfo=UTC))  # 02:20 local -> 22:20Z the day before

    def test_real_mode_with_recorded_format(self):
        weather = json.loads(next(p for p in RAW.iterdir() if "pressure_msl" in p.read_text()).read_text())
        marine = json.loads(next(p for p in RAW.iterdir() if "wave_height" in p.read_text()).read_text())

        def fake_fetch(url, raw_dir=None, offline=False, pause_s=1.0):
            # Real response objects, re-dated to the requested day; 25 points per request.
            src = weather if "archive" in url or "forecast" in url else marine
            day = url.split("start_date=")[1][:10]
            out = []
            for k in range(25):
                o = copy.deepcopy(src[k % len(src)])
                o["hourly"]["time"] = [day + t[10:] for t in o["hourly"]["time"]]
                nxt = (dt.date.fromisoformat(day) + dt.timedelta(days=1)).isoformat()
                o["hourly"]["time"] += [nxt + t[10:] for t in o["hourly"]["time"]]
                for key, vals in o["hourly"].items():
                    if key != "time":
                        o["hourly"][key] = vals + vals
                out.append(o)
            return out

        with tempfile.TemporaryDirectory() as d, mock.patch.object(openmeteo, "fetch", fake_fetch):
            with contextlib.redirect_stdout(io.StringIO()):
                rc = build_weather_lab.main(["--source", str(HORMUZ), "--output", d, "--mode", "real",
                                             "--real-start", "2026-11-18T00:00:00Z", "--interval", "60"])
            self.assertEqual(rc, 0)
            root = Path(d) / "MNO-Environmental-Playtest"
            meta = json.loads((root / "PLAYTEST_META.json").read_text())
            self.assertEqual(len(meta["stages"]), 8)
            self.assertEqual(meta["data"]["hours_per_stage"], 1)
            ini = (root / "missions" / "MNO Weather Lab - Hormuz.ini").read_text(encoding="utf-8")
            self.assertIn("Weather data by Open-Meteo.com", ini)  # attribution shown in game

    def test_real_start_follows_mission_time(self):
        seen = []

        def spy(url, raw_dir=None, offline=False, pause_s=1.0):
            seen.append(url)
            raise openmeteo.RateLimited("stop after the first request")
        with tempfile.TemporaryDirectory() as d, mock.patch.object(openmeteo, "fetch", spy):
            with contextlib.redirect_stderr(io.StringIO()):
                build_weather_lab.main(["--source", str(HORMUZ), "--output", d, "--mode", "real", "--mission-time", "10,0"])
        self.assertIn("start_date=1987-07-21", seen[0])  # 10:00 local (+4) = 06:00Z on the 21st, not 22:20Z on the 20th
        self.assertIn("models=era5", seen[0])

    def test_rate_limit_writes_nothing(self):
        def limited(*a, **k):
            raise openmeteo.RateLimited("daily limit")
        with tempfile.TemporaryDirectory() as d, mock.patch.object(openmeteo, "fetch", limited):
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(build_weather_lab.main(["--source", str(HORMUZ), "--output", d, "--mode", "real"]), 5)
            self.assertFalse((Path(d) / "MNO-Environmental-Playtest").exists())


if __name__ == "__main__":
    unittest.main()
