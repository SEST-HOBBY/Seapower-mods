"""Open-Meteo / official model data. Fixtures are two REAL responses saved by the tool: the
ECMWF IFS 0.25 deg forecast and the ECMWF WAM 0.25 deg wave forecast, 20 points over the Drake
Passage, for 18 Nov 2026."""
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
        self.assertIn("ecmwf_wam025", s["provenance"]["product_version"])  # waves credited to the model that made them
        self.assertIn("marine-api", s["provenance"]["source_url"])
        self.assertIn("forecast", s["campaign_mapping"]["statement"])
        self.assertNotIn("Recorded", s["campaign_mapping"]["statement"])
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
        self.assertIn("models=ecmwf_wam025", openmeteo.urls("ifs", openmeteo.grid_points(GRID), START, START)[1][1])
        # the ERA5 request text must never change: saved downloads on the owner's PC are keyed by it
        self.assertEqual(u[0][1].split("?")[1].split("&hourly=")[1].split("&")[0],
                         "pressure_msl%2Ccloud_cover%2Cprecipitation%2Ctemperature_2m%2Cwind_speed_10m%2Cwind_direction_10m%2Ccape%2Cvisibility")
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


class TestIdsAndUtc(unittest.TestCase):
    def test_ids_differ_by_region_and_step(self):
        a = drake()
        frames = openmeteo.assemble(openmeteo.grid_points(GRID),
                                    json.loads(next(p for p in RAW.iterdir() if "pressure_msl" in p.read_text()).read_text()), None, [START])
        shifted = LatLonGrid(-60.0, -60.0, 2.0, 2.0, 5, 4)
        b = openmeteo.to_snapshot("ifs", shifted, frames, campaign_start=CAMPAIGN, source_start=START, created=CREATED)
        self.assertNotEqual(a["snapshot_id"], b["snapshot_id"])
        self.assertNotIn("ERA5-Ocean", openmeteo.to_snapshot("era5", GRID, frames, campaign_start=CAMPAIGN, source_start=START,
                                                              created=CREATED)["provenance"]["attribution"])  # no waves fetched

    def test_non_utc_start_is_converted(self):
        seen = []

        def spy(url, *a, **k):
            seen.append(url)
            raise openmeteo.RateLimited("stop")
        with mock.patch.object(openmeteo, "fetch", spy):
            with self.assertRaises(openmeteo.RateLimited):
                openmeteo.fetch_snapshot("era5", GRID, dt.datetime(2025, 9, 14, 2, tzinfo=dt.timezone(dt.timedelta(hours=4))),
                                         24, 6, campaign_start=CAMPAIGN)
        self.assertIn("start_date=2025-09-13", seen[0])  # 02:00+04 is 22:00Z the day before


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


@unittest.skipUnless(HORMUZ.exists(), "vanilla export not present")
class TestRealModeOptions(unittest.TestCase):
    def build(self, *args):
        from test_gco_weather import synth
        seen = []

        def spy(url, *a, **k):
            seen.append(url)
            return synth(url)
        d = tempfile.mkdtemp()
        with mock.patch.object(openmeteo, "fetch", spy), contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            rc = build_weather_lab.main(["--source", str(HORMUZ), "--output", d, "--mode", "real", *args])
        meta_p = Path(d) / "MNO-Environmental-Playtest" / "PLAYTEST_META.json"
        meta = json.loads(meta_p.read_text()) if meta_p.exists() else None
        ini = next((Path(d) / "MNO-Environmental-Playtest" / "missions").glob("*.ini")).read_text(encoding="utf-8") if meta else ""
        return rc, meta, ini, seen

    def test_explicit_three_hours_is_honoured(self):
        rc, meta, ini, _ = self.build("--hours-per-stage", "3", "--real-start", "2025-09-14T06:00:00Z")
        self.assertEqual(rc, 0)
        self.assertEqual(meta["data"]["hours_per_stage"], 3)
        self.assertIn("3 real hours every", ini)

    def test_real_start_sets_mission_clock(self):
        rc, meta, ini, _ = self.build("--real-start", "2025-09-14T06:00:00Z")
        self.assertEqual(meta["mission_time"], "10,0")  # 06:00Z at Hormuz (+4) = 10:00 local
        self.assertIn("Time=10,0", ini)
        with self.assertRaises(SystemExit):  # contradictory clocks: an argument error, not "unavailable"
            self.build("--real-start", "2025-09-14T06:00:00Z", "--mission-time", "12,0")
        for bad in (["--real-start", "2025-09-14T06:00:00"], ["--real-start", "garbage"], ["--hours-per-stage", "0.5"]):
            with self.assertRaises(SystemExit, msg=bad):
                self.build(*bad)
        rc, meta, ini, _ = self.build("--real-start", "2025-09-14T06:40:00Z")
        self.assertEqual(meta["data"]["sample_start_utc"], "2025-09-14T06:40:00Z")
        self.assertIn("from 2025-09-14T06:40:00Z", ini)

    def test_forecast_keeps_mission_local_time(self):
        rc, meta, _, seen = self.build("--real-source", "ifs", "--mission-time", "10,0")
        self.assertEqual(rc, 0)
        self.assertIn("models=ecmwf_ifs025", seen[0])
        self.assertTrue(meta["data"]["source_start_utc"].endswith("T06:00:00Z"))  # 10:00 local (+4)

    def test_bad_mission_time(self):
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            build_weather_lab.main(["--source", str(HORMUZ), "--output", tempfile.mkdtemp(), "--mode", "real", "--mission-time", "25,0"])

    def test_polar_grid_inside_range(self):
        from test_gco_weather import synth
        seen = []

        def spy(url, *a, **k):
            seen.append(url)
            return synth(url)
        with mock.patch.object(openmeteo, "fetch", spy):
            build_weather_lab.real_stages(89.8, 179.9, dt.datetime(2025, 9, 14, 6, tzinfo=UTC), 2, 1, "era5")
        q = urllib.parse.parse_qs(urllib.parse.urlparse(seen[0]).query)
        self.assertTrue(all(-90 <= float(x) <= 90 for x in q["latitude"][0].split(",")))
        self.assertTrue(all(-180 <= float(x) < 180 for x in q["longitude"][0].split(",")))


class TestSecondReview(unittest.TestCase):
    def test_incomplete_response_not_saved(self):
        weather = json.loads(next(p for p in RAW.iterdir() if "pressure_msl" in p.read_text()).read_text())
        self.assertTrue(openmeteo._complete(weather))
        cut = copy.deepcopy(weather)
        for w in cut:
            w["hourly"]["pressure_msl"][-1] = None
        self.assertFalse(openmeteo._complete(cut))

    def test_oversize_request_does_not_crash_pacer(self):
        openmeteo._spent.clear()
        with mock.patch.object(openmeteo, "_sleep", lambda s: None):
            openmeteo._pace(5000)
        openmeteo._spent.clear()

    def test_align_tolerates_sea_cell_snapping(self):
        pts = [(26.0, 56.0), (26.0, 56.5)]
        resp = [{"latitude": 26.0, "longitude": 56.5, "id": 0}, {"latitude": 26.0, "longitude": 56.5, "id": 1}]
        self.assertEqual([r["id"] for r in openmeteo.align(pts, resp, "marine")], [0, 1])

    def test_naive_and_half_hour_starts(self):
        with self.assertRaises(ValueError):
            openmeteo.fetch_snapshot("era5", GRID, START, 6, 6, campaign_start=dt.datetime(2028, 9, 14))
        with self.assertRaises(ValueError):
            openmeteo.fetch_snapshot("era5", GRID, dt.datetime(2025, 9, 14, 0, tzinfo=dt.timezone(dt.timedelta(hours=5, minutes=30))),
                                     6, 6, campaign_start=CAMPAIGN)

    def test_all_null_is_a_clear_error(self):
        weather = json.loads(next(p for p in RAW.iterdir() if "pressure_msl" in p.read_text()).read_text())
        empty = copy.deepcopy(weather)
        for w in empty:
            for k in w["hourly"]:
                if k != "time":
                    w["hourly"][k] = [None] * len(w["hourly"]["time"])
        with self.assertRaises(openmeteo.IngestError):
            openmeteo.assemble(openmeteo.grid_points(GRID), empty, None, [START])
