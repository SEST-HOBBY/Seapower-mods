import json
import math
import unittest

from helpers import HERE

from mno_env import geo, polar
from mno_env.grid import LatLonGrid, ProjectedGrid, bilinear, regrid_polar_to_latlon


class TestPolar(unittest.TestCase):
    def test_matches_proj_reference(self):
        ref = json.loads((HERE / "fixtures" / "proj_reference.json").read_text())
        self.assertIn("PROJ", ref["generator"])
        n = 0
        for code, pts in ref["points"].items():
            proj = polar.PROJECTIONS[code]
            for lat, lon, rx, ry in pts:
                x, y = proj.forward(lat, lon)
                self.assertAlmostEqual(x, rx, delta=1e-3, msg=f"{code} {lat},{lon}")
                self.assertAlmostEqual(y, ry, delta=1e-3, msg=f"{code} {lat},{lon}")
                la, lo = proj.inverse(rx, ry)
                self.assertAlmostEqual(la, lat, delta=1e-7)
                if abs(lat) < 89.9:
                    self.assertAlmostEqual(geo.lon_delta(lo, lon), 0.0, delta=1e-7)
                n += 1
        self.assertGreaterEqual(n, 20)

    def test_antimeridian_is_continuous_in_polar(self):
        for proj in (polar.EPSG_3412, polar.EPSG_3976, polar.EPSG_6932):
            a = proj.forward(-70, 179.999)
            b = proj.forward(-70, -179.999)
            self.assertLess(math.dist(a, b), 200.0)  # metres apart, not a hemisphere

    def test_pole(self):
        for proj in (polar.EPSG_3413, polar.EPSG_3976):
            x, y = proj.forward(90 if not getattr(proj, "south", False) else -90, 0)
            self.assertLess(math.hypot(x, y), 1e-6)


class TestGeo(unittest.TestCase):
    def test_wrap_and_campaign_frame(self):
        self.assertEqual(geo.wrap_lon(180), -180)
        self.assertEqual(geo.wrap_lon(-180), -180)
        self.assertAlmostEqual(geo.wrap_lon(202.055), -157.945)
        self.assertAlmostEqual(geo.campaign_lon(-117.2, -100, 258), 242.8)  # San Diego in GCO's frame
        self.assertAlmostEqual(geo.campaign_lon(10, -100, 258), 10)

    def test_great_circle_across_seam(self):
        d = geo.great_circle_nm((0, 179.5), (0, -179.5))
        self.assertAlmostEqual(d, 60.04, places=1)
        pts = geo.sample_leg((0, 179.5), (0, -179.5), 10)
        self.assertTrue(all(abs(p[1]) >= 179.4 for p in pts))

    def test_destination_inverse(self):
        p = geo.destination((-60, 170), 90, 300)
        self.assertAlmostEqual(geo.great_circle_nm((-60, 170), p), 300, places=6)

    def test_land_mask(self):
        m = geo.LandMask.from_file()
        self.assertTrue(m.is_land(48.85, 2.35))       # Paris
        self.assertTrue(m.is_land(-20, 135))          # Australia
        self.assertFalse(m.is_land(0, -150))          # Pacific
        self.assertFalse(m.is_land(-58, -65))         # Drake Passage
        self.assertTrue(m.is_land(-89, 0))            # South Pole
        # Natural Earth low resolution stops at the grounding line: shelves read as water.
        self.assertFalse(m.is_land(-81, -175))


class TestGrid(unittest.TestCase):
    def setUp(self):
        self.g = LatLonGrid(-180, -90, 90, 90, 4, 3)  # columns -180,-90,0,90; global

    def test_seam_interpolation(self):
        vals = [0, 0, 0, 100] * 3  # 100 at 90E, 0 at -180
        self.assertAlmostEqual(bilinear(self.g, vals, 0, 135), 50)
        self.assertAlmostEqual(bilinear(self.g, vals, 0, -135), 0)
        self.assertAlmostEqual(bilinear(self.g, [10, 0, 0, 30] * 3, 0, 179.999), 10, places=2)
        self.assertAlmostEqual(bilinear(self.g, [10, 0, 0, 30] * 3, 0, -179.999), 10, places=2)

    def test_duplicated_seam_column(self):
        g = LatLonGrid(-180, -90, 90, 90, 5, 3)  # -180..180 inclusive
        self.assertEqual(g.period_cols, 4)
        self.assertAlmostEqual(bilinear(g, [0, 0, 0, 100, 0] * 3, 0, 135), 50)

    def test_regional_grid_crossing_seam(self):
        g = LatLonGrid(170, -10, 10, 10, 3, 3)  # 170, 180, 190(-170)
        vals = [0, 10, 20] * 3
        self.assertAlmostEqual(bilinear(g, vals, 0, -175), 15)
        self.assertIsNone(bilinear(g, vals, 0, 0))

    def test_missing_corners(self):
        vals = [None, 10, 10, 10] * 3
        self.assertAlmostEqual(bilinear(self.g, vals, 0, -135), 10)
        self.assertIsNone(bilinear(self.g, [None] * 12, 0, 0))
        self.assertAlmostEqual(bilinear(self.g, [-999, 10, 10, 10] * 3, 0, -135, fill=-999), 10)

    def test_polar_regrid(self):
        # A 25 km south polar grid whose value is the latitude itself.
        proj = polar.EPSG_3412
        nx = ny = 160
        dx = 25_000.0
        x0 = y0 = -(nx - 1) / 2 * dx
        vals = []
        for j in range(ny):
            for i in range(nx):
                lat, lon = proj.inverse(x0 + i * dx, y0 + j * dx)
                vals.append(None if lat > -55 else lat)
        src = ProjectedGrid(proj, x0, y0, dx, dx, nx, ny)
        target = LatLonGrid(-180, -88, 2, 2, 180, 15)
        out = regrid_polar_to_latlon(src, vals, target)
        for j in range(target.ny):
            for i in (0, 1, 89, 90, 179):  # includes both sides of the seam
                v = out[j * target.nx + i]
                if target.lat(j) <= -74:  # inside the +-1,987 km window
                    self.assertAlmostEqual(v, target.lat(j), delta=0.05)
                elif target.lat(j) >= -62:   # outside it
                    self.assertIsNone(v)


if __name__ == "__main__":
    unittest.main()
