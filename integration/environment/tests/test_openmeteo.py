"""Open-Meteo / official model data. Fixtures are two REAL responses (ECMWF IFS forecast and
wave model, 20 points over the Drake Passage, issued for 18 Nov 2026) saved by the tool."""
import contextlib
import urllib.error
import urllib.parse
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

        def fake_fetch(url, raw_dir=None, offline=False, pause_s=1.0, **kw):
            # Real response objects, re-dated to the requested day; 25 points per request.
            src = weather if "archive" in url or "forecast" in url else marine
            day = url.split("start_date=")[1][:10]
            q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
            lats = [float(x) for x in q["latitude"][0].split(",")]
            lons = [float(x) for x in q["longitude"][0].split(",")]
            out = []
            for k in range(25):
                o = copy.deepcopy(src[k % len(src)])
                o["latitude"], o["longitude"] = lats[k], lons[k]
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

        def spy(url, raw_dir=None, offline=False, pause_s=1.0, **kw):
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


class TestQuotaAndOrder(unittest.TestCase):
    def setUp(self):
        self.clock = [0.0]
        self.slept = []
        openmeteo._spent.clear()
        self.p1 = mock.patch.object(openmeteo, "_now", lambda: self.clock[0])
        self.p2 = mock.patch.object(openmeteo, "_sleep", self._sleep)
        self.p1.start()
        self.p2.start()

    def tearDown(self):
        self.p1.stop()
        self.p2.stop()
        openmeteo._spent.clear()

    def _sleep(self, s):
        self.slept.append(s)
        self.clock[0] += s

    def test_cost_rule(self):
        pts = openmeteo.grid_points(LatLonGrid(0, 0, 1, 1, 10, 5))
        w, m = openmeteo.urls("era5", pts, START, START + dt.timedelta(days=6))
        self.assertEqual(openmeteo.request_cost(w[1]), 50)          # 8 variables, 7 days: 1 call per location
        _, wl = openmeteo.urls("era5", pts, START, START + dt.timedelta(days=27))[0]
        self.assertEqual(openmeteo.request_cost(wl), 50 * 0.8 * 2)  # 28 days: x2, 8/10 variables

    def test_pacer_stays_inside_minute_and_hour(self):
        for _ in range(200):  # 200 requests of 50 locations = 10,000 calls
            openmeteo._pace(50)
        spent = [(t, c) for t, c in openmeteo._spent]
        for t0, _ in spent:
            self.assertLessEqual(sum(c for t, c in spent if t0 <= t < t0 + 60), openmeteo.MINUTE_BUDGET)
        self.assertGreater(self.clock[0], 3600)  # 10,000 calls cannot fit in one hour

    def test_minute_limit_waits_then_continues(self):
        answers = [urllib.error.HTTPError("u", 429, "x", {}, io.BytesIO(b'{"error":true,"reason":"Minutely API request limit exceeded"}')),
                   io.BytesIO(b'[{"latitude":0,"longitude":0}]')]

        class R:
            def __init__(self, b): self.b = b
            def __enter__(self): return self
            def __exit__(self, *a): return False
            def read(self): return self.b.getvalue()

        def opener(req, timeout=0):
            a = answers.pop(0)
            if isinstance(a, Exception):
                raise a
            return R(a)
        with mock.patch.object(openmeteo.urllib.request, "urlopen", opener):
            out = openmeteo.fetch("https://archive-api.open-meteo.com/v1/archive?latitude=0&longitude=0&hourly=a&start_date=2025-09-14&end_date=2025-09-14")
        self.assertEqual(out, [{"latitude": 0, "longitude": 0}])
        self.assertIn(65, self.slept)

    def test_daily_limit_stops(self):
        def opener(req, timeout=0):
            raise urllib.error.HTTPError("u", 429, "x", {}, io.BytesIO(b'{"reason":"Daily API request limit exceeded"}'))
        with mock.patch.object(openmeteo.urllib.request, "urlopen", opener):
            with self.assertRaises(openmeteo.RateLimited):
                openmeteo.fetch("https://archive-api.open-meteo.com/v1/archive?latitude=0&longitude=0&hourly=a&start_date=2025-09-14&end_date=2025-09-14")

    def test_forecast_not_replayed_online(self):
        self.assertTrue(openmeteo._immutable("https://archive-api.open-meteo.com/v1/archive?x"))
        self.assertTrue(openmeteo._immutable("https://marine-api.open-meteo.com/v1/marine?models=era5_ocean"))
        self.assertFalse(openmeteo._immutable("https://api.open-meteo.com/v1/forecast?x"))

    def test_align(self):
        pts = [(0.0, 0.0), (0.0, 1.0), (1.0, 0.0)]
        resp = [{"latitude": 1.0, "longitude": 0.25, "id": "c"}, {"latitude": 0.25, "longitude": 0.0, "id": "a"},
                {"latitude": 0.0, "longitude": 1.0, "id": "b"}]
        self.assertEqual([r["id"] for r in openmeteo.align(pts, resp, "t")], ["a", "b", "c"])
        same = [{"latitude": 0.1, "longitude": 179.9}, {"latitude": 0.0, "longitude": -179.5}]
        self.assertEqual(openmeteo.align([(0.0, 179.75), (0.0, -179.5)], same, "t"), same)  # across 180
        with self.assertRaises(openmeteo.IngestError):
            openmeteo.align(pts, [resp[0], resp[0], resp[2]], "t")
        real = json.loads(next(p for p in RAW.iterdir() if "pressure_msl" in p.read_text()).read_text())
        self.assertEqual(openmeteo.align(openmeteo.grid_points(GRID), real, "t"), real)  # the API kept request order


class TestEmptyTail(unittest.TestCase):
    def test_unpublished_hours_refused(self):
        weather = json.loads(next(p for p in RAW.iterdir() if "pressure_msl" in p.read_text()).read_text())
        cut = copy.deepcopy(weather)
        for w in cut:
            for k, vals in w["hourly"].items():
                if k != "time":
                    w["hourly"][k] = [None if w["hourly"]["time"][i] >= "2026-11-18T12:00" else v for i, v in enumerate(vals)]
        with self.assertRaises(openmeteo.IngestError):
            openmeteo.assemble(openmeteo.grid_points(GRID), cut, None, [START, START + dt.timedelta(hours=12)])
        openmeteo.assemble(openmeteo.grid_points(GRID), cut, None, [START, START + dt.timedelta(hours=6)])
