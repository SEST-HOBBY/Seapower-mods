import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import ENV_ROOT, HORMUZ, START, state, t0

from mno_env import ingest, overlay, polar, snapshot
from mno_env.grid import LatLonGrid
from mno_env.mission_adapter import (apply_plan, clouds_from_fraction, mission_weather_plan, native_state,
                                     sea_state_from_hs, wind_direction)

sys.path.insert(0, str(ENV_ROOT / "tools"))
import build_weather_lab  # noqa: E402


class TestAdapter(unittest.TestCase):
    def test_wmo_sea_state(self):
        self.assertEqual([sea_state_from_hs(h) for h in (0, 0.05, 0.3, 1.0, 2.0, 3.0, 5.0, 7.0, 12.0, 20.0)],
                         [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        self.assertEqual(sea_state_from_hs(None), 4)

    def test_clouds_and_wind(self):
        self.assertEqual([clouds_from_fraction(p) for p in (0, 12.5, 50, 87.5, 100)], ["Clear", "Scattered", "Broken", "Overcast", "Overcast"])
        self.assertEqual(wind_direction(0, -10), "N")   # blowing towards the south = from the north
        self.assertEqual(wind_direction(-10, 0), "E")
        self.assertEqual(wind_direction(7, 7), "SW")
        self.assertIsNone(wind_direction(0.1, 0.1))

    def test_native_state_rules(self):
        wet = {"cloud_fraction_pct": 100, "precip_rate_mm_h": 3.0, "air_temp_2m_c": 10, "convective_risk_idx": 0.9, "wave_hs_m": 3}
        s = native_state(wet, initial=False)
        self.assertTrue(s.rain and s.thunderstorm and not s.snow and not s.fog)
        self.assertFalse(native_state({**wet, "convective_risk_idx": None}, initial=False).thunderstorm)  # no rain-only storms
        self.assertFalse(native_state({**wet, "cloud_fraction_pct": 60}, initial=False).thunderstorm)
        cold = {**wet, "air_temp_2m_c": -2}
        self.assertTrue(native_state(cold, initial=True).snow)
        self.assertFalse(native_state(cold, initial=False).snow)  # never a snow trigger
        self.assertFalse(native_state(wet, initial=False).fog)   # no visibility field: no fog claim
        self.assertFalse(native_state({**wet, "visibility_km": 0.4}, initial=False).fog)  # rain explains it: not fog
        dry = {**wet, "precip_rate_mm_h": 0.0, "wind_u10_ms": 4.0, "wind_v10_ms": 0.0}
        self.assertTrue(native_state({**dry, "visibility_km": 0.4}, initial=False).fog)
        self.assertFalse(native_state({**dry, "visibility_km": 0.4, "wind_u10_ms": 16.0}, initial=False).fog)  # gale
        snowy = {**wet, "air_temp_2m_c": 5.0, "snowfall_rate_mm_h": 2.0}  # the snowfall field wins over temperature
        self.assertTrue(native_state(snowy, initial=True).snow)
        self.assertFalse(native_state(snowy, initial=False).rain)  # snowing later: no Rain trigger

    @unittest.skipUnless(HORMUZ.exists(), "vanilla export not present")
    def test_plan_into_mission(self):
        plan = mission_weather_plan(state(), t0(), -54.0, -49.0, duration_s=6 * 3600, step_s=1800)
        self.assertEqual(plan[0][0], 0)
        self.assertTrue(all(a[1] != b[1] for a, b in zip(plan, plan[1:])))
        text, rep = apply_plan(HORMUZ.read_bytes().decode("utf-8"), plan)
        self.assertEqual(len(rep.appended), len(plan) - 1)
        self.assertEqual([a["time_s"] for a in rep.appended], [t for t, _ in plan[1:]])


class TestIngest(unittest.TestCase):
    def test_accumulated_precip(self):
        acc = [[0.0, 0.0], [0.006, 0.0], [0.012, 0.00000005 * -1 + 0.0]]
        rates, clamped = ingest.accumulated_to_rate(acc, [0, 6, 12])
        self.assertAlmostEqual(rates[0][0], 1.0)   # 6 mm over 6 h
        self.assertAlmostEqual(rates[1][0], 1.0)
        self.assertEqual(rates[1][1], 0.0)
        self.assertEqual(clamped, 1)
        with self.assertRaises(ingest.IngestError):
            ingest.accumulated_to_rate([[0.01], [0.0]], [0, 6])  # decreasing: not from-start accumulation
        with self.assertRaises(ingest.IngestError):
            ingest.accumulated_to_rate([[0.0], [0.0]], [6, 6])
        self.assertEqual(ingest.hourly_accum_to_rate([0.0012, None, -0.0]), [1.2, None, 0.0])

    def test_units_and_layout(self):
        self.assertEqual(ingest.pa_to_hpa([101325.0]), [1013.25])
        self.assertAlmostEqual(ingest.k_to_c([273.15])[0], 0.0)
        self.assertEqual(ingest.frac_to_pct([0.5, 1.2]), [50.0, 100.0])
        vals = list(range(8))  # 4 columns x 2 rows, lon 0,90,180,270
        out, lon0 = ingest.rotate_0_360(vals, 4, 2, 0.0, 90.0)
        self.assertEqual((out, lon0), ([2, 3, 0, 1, 6, 7, 4, 5], -180.0))
        self.assertEqual(ingest.flip_north_to_south([1, 2, 3, 4], 2, 2), [3, 4, 1, 2])
        self.assertEqual(ingest.thin(list(range(16)), 4, 4, 2), ([0, 2, 8, 10], 2, 2))

    def test_osisaf_flags_and_polar(self):
        self.assertEqual(ingest.osisaf_conc([50, 60, -999, float("nan"), 120], [0, 1, 0, 0, 0], fill=-999), [50.0, None, None, None, 100.0])
        target = LatLonGrid(-180, -80, 10, 10, 36, 3)
        proj = polar.EPSG_3412
        vals = [80.0] * (40 * 40)
        out = ingest.polar_to_latlon(proj, -1_950_000, -1_950_000, 100_000, 100_000, 40, 40, vals, target)
        self.assertTrue(all(v is not None and abs(v - 80.0) < 1e-9 for v in out[:36]))   # -80: inside the grid everywhere
        self.assertTrue(all(v is None for v in out[-36:]))  # -60: outside a +-1,950 km window

    def test_built_snapshot_validates(self):
        g = LatLonGrid(-180, -90, 180, 90, 2, 3)
        snap = ingest.build(snapshot_id="t", data_class="reanalysis",
                            provenance={"provider": "ECMWF/C3S", "product": "ERA5 fixture", "product_version": "x", "licence": "CC BY 4.0",
                                        "attribution": "C3S", "source_url": "https://cds.climate.copernicus.eu/", "downloaded_utc": "2026-11-18T00:00:00Z",
                                        "source_time_utc": "2025-09-14T06:00:00Z", "forecast_issue_utc": None},
                            mapping={"mode": "historical_analogue", "offset_seconds": 94694400, "statement": "Historical analogue; not a forecast of 2028."},
                            grid=g, frames=[(START.replace(year=2025), None, {"msl_pressure_hpa": [1000] * 6, "precip_rate_mm_h": [0, 1, 2, 3, 4, 5]})],
                            kinds={"msl_pressure_hpa": "reanalysis", "precip_rate_mm_h": "reanalysis"}, created=START.replace(year=2026))
        self.assertEqual(snapshot.validate(snap), [])
        with self.assertRaises(ingest.IngestError):
            ingest.build(snapshot_id="t", data_class="observed", provenance={}, mapping={}, grid=g, frames=[], kinds={"rain": "observed"}, created=START)


class TestOverlay(unittest.TestCase):
    def test_equirect_roundtrip_and_seam(self):
        v = overlay.Equirect(720, 360)
        for px, py in ((0, 0), (719, 359), (360, 180), (12.25, 77.5)):
            lat, lon = v.pixel_to_geo(px, py)
            x, y = v.geo_to_pixel(lat, lon)
            self.assertAlmostEqual(x, px, places=6)
            self.assertAlmostEqual(y, py, places=6)
        west = overlay.debug_colour(*v.pixel_to_geo(0, 100))
        east = overlay.debug_colour(*v.pixel_to_geo(719, 100))
        self.assertEqual(west, east)  # both are the magenta antimeridian band: the seam is one band, not a break
        a = overlay.debug_colour(10.5, -170)
        b = overlay.debug_colour(10.5, 170)
        self.assertLess(sum(abs(x - y) for x, y in zip(a[:3], b[:3])), 200)

    def test_polar_window_full_coverage(self):
        w = overlay.PolarWindow(polar.EPSG_3976, 64, 4_500_000.0)
        buf = overlay.build_layer(w, None, None)
        self.assertEqual(len(buf), 64 * 64 * 4)
        self.assertTrue(all(buf[k + 3] > 0 for k in range(0, len(buf), 4)))  # no holes, poles included
        lat, lon = w.pixel_to_geo(31.5, 31.5)
        self.assertLess(lat, -89.99)
        x, y = w.geo_to_pixel(-60, 180)
        self.assertAlmostEqual(x, 31.5, places=6)
        self.assertGreater(y, 31.5)  # 180E is straight down in EPSG:3976

    def test_empty_field_renders_transparent(self):
        v = overlay.Equirect(16, 8)
        buf = overlay.build_layer(v, lambda lat, lon: None, "sea_ice_conc_pct")
        self.assertEqual(set(buf), {0})

    def test_memory_numbers(self):
        self.assertEqual(overlay.layer_bytes(2048, 1024), 8 * 1024 * 1024)
        self.assertEqual(overlay.layer_bytes(1024, 512, "R8"), 512 * 1024)


class TestWeatherLabTool(unittest.TestCase):
    @unittest.skipUnless(HORMUZ.exists(), "vanilla export not present")
    def test_build_refuse_and_hashes(self):
        before = hashlib.sha256(HORMUZ.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as d:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(build_weather_lab.main(["--source", str(HORMUZ), "--output", d]), 0)
            root = Path(d) / "MNO-Environmental-Playtest"
            meta = json.loads((root / "PLAYTEST_META.json").read_text())
            self.assertEqual(meta["source_sha256"], before)
            mission = root / meta["mission"].split("MNO-Environmental-Playtest/", 1)[1]
            self.assertEqual(hashlib.sha256(mission.read_bytes()).hexdigest(), meta["mission_sha256"])
            self.assertEqual(len(meta["stages"]), 8)
            self.assertEqual([s["at_s"] for s in meta["stages"]], [0, 300, 600, 900, 1200, 1500, 1800, 2100])
            self.assertIn("NOT TESTED IN GAME", meta["status"])
            self.assertIn("ApproximateVersion=0.9.3", (root / "_info.ini").read_text())
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(build_weather_lab.main(["--source", str(HORMUZ), "--output", d]), 3)  # never overwrites
        self.assertEqual(hashlib.sha256(HORMUZ.read_bytes()).hexdigest(), before)

    @unittest.skipUnless(HORMUZ.exists(), "vanilla export not present")
    def test_procedural_mode(self):
        with tempfile.TemporaryDirectory() as d:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(build_weather_lab.main(["--source", str(HORMUZ), "--output", d, "--mode", "procedural",
                                                         "--frames", "4", "--mission-time", "10,0"]), 0)
            meta = json.loads((Path(d) / "MNO-Environmental-Playtest" / "PLAYTEST_META.json").read_text())
            self.assertEqual(len(meta["stages"]), 4)
            self.assertEqual(meta["mission_time"], "10,0")
            self.assertEqual((meta["data"]["sample_lat"], meta["data"]["sample_lon"]), (25.78, 55.74))  # Hormuz's own map centre
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(build_weather_lab.main(["--source", str(HORMUZ), "--output", d + "/sc", "--mode", "procedural",
                                                         "--frames", "4", "--storm-chaser"]), 0)
            meta = json.loads((Path(d) / "sc" / "MNO-Environmental-Playtest" / "PLAYTEST_META.json").read_text())
            self.assertGreaterEqual(meta["data"]["variety"][0], 2)  # the chaser finds a front passing over

    @unittest.skipUnless(HORMUZ.exists(), "vanilla export not present")
    def test_quick_interval(self):
        with tempfile.TemporaryDirectory() as d:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(build_weather_lab.main(["--source", str(HORMUZ), "--output", d, "--interval", "60"]), 0)
            meta = json.loads((Path(d) / "MNO-Environmental-Playtest" / "PLAYTEST_META.json").read_text())
            self.assertEqual([s["at_s"] for s in meta["stages"]], [0, 60, 120, 180, 240, 300, 360, 420])
            ini = (Path(d) / "MNO-Environmental-Playtest" / "missions" / "MNO Weather Lab - Hormuz.ini").read_text(encoding="utf-8")
            self.assertIn("every 60 seconds", ini)


if __name__ == "__main__":
    unittest.main()
