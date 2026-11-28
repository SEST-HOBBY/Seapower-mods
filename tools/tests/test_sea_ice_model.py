"""SEST battle sea ice: the Python mirror (tools/sea_ice_model.py), the
committed tables (tools/sea_ice_edges.json, tools/sea_ice_arctic_edge.json)
and the C# data files (runtime/SeaIceData.g.cs, SeaIceArcticData.g.cs) agree
with each other and with the weather branch's mno_env/seaice.py (when that
checkout is present; the comparison uses hard_cap=True, the weather branch's
own path without SEST's Arctic edge)."""
import datetime as dt
import json
import os
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import sea_ice_model as m  # noqa: E402

ENV = Path(os.environ.get('SEST_ENV_DIR', '/home/user/sest-env-read/integration/environment'))
DATA_CS = ROOT / 'integration/beta-feature-parity/runtime/SeaIceData.g.cs'
ARCTIC_CS = ROOT / 'integration/beta-feature-parity/runtime/SeaIceArcticData.g.cs'
ANTARCTIC_CS = ROOT / 'integration/beta-feature-parity/runtime/SeaIceAntarcticData.g.cs'


class SeaIceModelTests(unittest.TestCase):
    def test_review_points(self):
        # The adversarial review ran seaice.py: 10 March 36E 72N 18.7 %, 74N 62.3 %; 12 Jan 68S 42W 37.1 %.
        doc = m.table()
        for y, mo, d, lat, lon, pct in doc['review_points']:
            self.assertAlmostEqual(m.concentration(lat, lon, dt.date(y, mo, d), hard_cap=True), pct, places=9)
        self.assertAlmostEqual(m.concentration(72, 36, dt.date(2029, 3, 10), hard_cap=True), 18.7, places=1)
        self.assertAlmostEqual(m.concentration(74, 36, dt.date(2029, 3, 10), hard_cap=True), 62.3, places=1)
        self.assertAlmostEqual(m.concentration(-68, -42, dt.date(2029, 1, 12), hard_cap=True), 37.1, places=1)

    def test_hemisphere_seasons(self):
        self.assertGreater(m.concentration(79, 36, dt.date(2029, 3, 15)), m.concentration(79, 36, dt.date(2029, 9, 15)) + 40)
        self.assertGreater(m.concentration(-62, -40, dt.date(2029, 9, 15)), m.concentration(-62, -40, dt.date(2029, 2, 20)) + 40)
        self.assertEqual(m.concentration(39.9, 120.5, dt.date(2029, 1, 15)), 0.0)
        self.assertEqual(m.concentration(-60, 0, dt.date(2029, 3, 10)) == 0.0, False)

    def test_north_knee(self):
        # SEST soft knee over NORTH_EDGE_CAP (same as SeaIceModel.NorthEdge): no perfect circle at the minimum.
        self.assertAlmostEqual(m.north_edge(70.0), 70.0, places=4)
        self.assertAlmostEqual(m.north_edge(86.5), 80.5 + 0.35 * 6.0, places=2)
        day = dt.date(2028, 10, 1)
        self.assertGreater(m.concentration(89.9, 0, day), 90)

        def heavy(lon):
            return next(t / 20 for t in range(1400, 1800) if m.concentration(t / 20, lon, day) >= 60)
        lats = [heavy(lon) for lon in (-20, 0, 20, 40)]
        self.assertGreater(max(lats) - min(lats), 0.75, lats)
        self.assertAlmostEqual(m.concentration(70, -60, dt.date(2029, 3, 15)), m.concentration(70, -60, dt.date(2029, 3, 15), hard_cap=True), places=2)

    def test_antarctic_edge_table(self):
        # tools/make_sea_ice_antarctic.py: NSIDC's 2016-2025 median 15 % edge, degrees South; 80.0 = no pack ice.
        doc = json.loads(m.ANTARCTIC_JSON.read_text(encoding='utf-8'))
        self.assertEqual([len(r) for r in doc['edges']], [360] * 12)
        self.assertEqual(doc['source']['files'], 120)
        self.assertTrue(all(50.0 <= v <= 80.0 for row in doc['edges'] for v in row))
        text = ANTARCTIC_CS.read_text(encoding='utf-8')
        block = re.search(r'internal static readonly double\[\] Edge =\s*\{(.*?)\};', text, re.S).group(1)
        values = [float(v) for v in re.findall(r'-?\d+\.\d+', re.sub(r'//[^\n]*', '', block))]
        self.assertEqual(values, [v for row in doc['edges'] for v in row])
        self.assertIn(doc['source']['sha256_of_shp_files'], text)

    def test_measured_antarctic_edge(self):
        # On a mid-month date the southern 15 % line is the table's edge (SeaIceModel.AntarcticEdge).
        for month, lon in ((1, -120.5), (5, 60.5), (8, 0.5), (12, 160.5)):  # 31-day months: day 16 is mid-month
            want = json.loads(m.ANTARCTIC_JSON.read_text(encoding='utf-8'))['edges'][month - 1][int(lon + 179.5)]
            got = next(t / 100 for t in range(5000, 8000) if m.concentration(-t / 100, lon, dt.date(2029, month, 16)) >= 15)
            self.assertAlmostEqual(got, want, delta=0.02)  # 0.01-degree scan
        self.assertLess(m.concentration(-66, 0, dt.date(2029, 2, 20)), 1.0)       # Dronning Maud Land open in February
        self.assertGreater(m.concentration(-74, -45, dt.date(2029, 2, 20)), 60.0)  # the western Weddell keeps its pack
        self.assertLess(m.antarctic_edge(0, dt.date(2029, 9, 16)), 57.0)          # September pack to 55S south of Africa

    def test_arctic_edge_table(self):
        doc = json.loads(m.ARCTIC_JSON.read_text(encoding='utf-8'))
        self.assertEqual([len(r) for r in doc['edges']], [360] * 12)
        self.assertEqual(doc['source']['files'], 120)
        text = ARCTIC_CS.read_text(encoding='utf-8')
        block = re.search(r'internal static readonly double\[\] Edge =\s*\{(.*?)\};', text, re.S).group(1)
        values = [float(v) for v in re.findall(r'-?\d+\.\d+', re.sub(r'//[^\n]*', '', block))]
        self.assertEqual(values, [v for row in doc['edges'] for v in row])
        self.assertIn(doc['source']['sha256_of_shp_files'], text)

    def test_arctic_edge_follows_nsidc(self):
        table = m.arctic_table()

        def edge15(lon, day, start=66.0):
            return next(t / 100 for t in range(int(start * 100), 9000) if m.concentration(t / 100, lon, day) >= 15)
        # On a mid-month date (16th of a 31-day month) the 15 % line is the table's, across the sector.
        for month in (1, 3, 8, 10, 12):
            day = dt.date(2029, month, 16)
            self.assertEqual(m.arctic_month(day), (month - 1, 0.0))
            for lon in (-9.5, 30.5, 50.5, 100.5, 140.5, 170.5, -140.5):
                want = table[month - 1][int(lon + 179.5)]
                if want >= 73.0:
                    self.assertAlmostEqual(edge15(lon, day, 72.0), want, delta=0.02, msg=(month, lon))
        # The two failures the owner saw (1 October, GCO): no ring round the pole, and the measured shape:
        # Barents and Kara open to about 81N, the Laptev and East Siberian edge at 77-80N.
        oct1 = dt.date(2028, 10, 1)
        self.assertGreater(edge15(40, oct1), 81.0)
        self.assertGreater(edge15(80, oct1), 81.0)
        for lon in (120, 140, 160):
            self.assertTrue(76.5 < edge15(lon, oct1) < 80.0, lon)
        # Winter: the southern Barents Sea is open water (2016-2025), the Kara and Laptev are full of ice,
        # the White Sea and the Gulf of Alaska keep seaice.py's ice.
        mar10 = dt.date(2029, 3, 10)
        self.assertLess(m.concentration(72, 36, mar10), 1.0)
        self.assertLess(m.concentration(69.8, 36, mar10), 5.0)  # Murman coast
        self.assertGreater(m.concentration(79, 36, mar10), 60.0)
        self.assertGreater(m.concentration(75, 120, mar10), 95.0)
        self.assertGreater(m.concentration(74, 70, mar10), 95.0)
        self.assertGreater(m.concentration(73, 140, dt.date(2029, 11, 20)), 90.0)  # Laptev/ESS freeze-up
        for lat, lon in ((65.5, 38.0), (59.0, -145.0), (63.0, 22.0)):
            self.assertAlmostEqual(m.concentration(lat, lon, mar10), m.concentration(lat, lon, mar10, hard_cap=True), places=6)
        # Outside the sector (Baffin Bay, Canadian islands) nothing changes.
        self.assertEqual(m.arctic_weight(-60.0), 0.0)
        self.assertEqual(m.arctic_weight(-100.0), 0.0)
        for lon in (0.0, 90.0, 180.0, -140.0):
            self.assertEqual(m.arctic_weight(lon), 1.0)

    def test_chukchi_joins_the_arctic_edge(self):
        # No seam where the Chukchi Sea's regional mask meets its neighbours north of 72N.
        for day in (dt.date(2028, 10, 1), dt.date(2029, 9, 15), dt.date(2029, 3, 15)):
            for lat in (73.0, 75.0, 77.0, 78.5):
                a, b = m.concentration(lat, -155.5, day), m.concentration(lat, -154.5, day)
                self.assertLess(abs(a - b), 5.0, (day, lat, a, b))
                a, b = m.concentration(lat, 179.5, day), m.concentration(lat, -179.5, day)
                self.assertLess(abs(a - b), 5.0, (day, lat, a, b))
        self.assertGreater(m.concentration(68, -168, dt.date(2029, 3, 15)), 85)  # the regional winter ice stays

    def test_marginal_seas(self):
        # Sea of Okhotsk: heavy in March, ice-free July to October (NSIDC G02135 regional extent).
        self.assertGreater(m.concentration(59, 145, dt.date(2029, 3, 15)), 85)
        for mo in (7, 8, 9, 10):
            self.assertEqual(m.concentration(59, 145, dt.date(2029, mo, 15)), 0.0)
            self.assertEqual(m.concentration(62, -168, dt.date(2029, mo, 15)), 0.0)
        self.assertGreater(m.concentration(62, -168, dt.date(2029, 3, 15)), 85)  # northern Bering shelf
        # Chukchi Sea: fully ice-covered December to April, so no seam at Bering Strait in winter
        for mo in (1, 2, 3, 4):
            vals = [m.concentration(lat, -168, dt.date(2029, mo, 15)) for lat in (65.6, 66.5, 67.5, 68.5)]
            self.assertLess(max(vals) - min(vals), 20, (mo, vals))
        self.assertLess(m.concentration(68, -168, dt.date(2029, 9, 15)), 15)  # open in September
        self.assertEqual(m.table()['marginal']['seas'], ['okhotsk', 'bering', 'chukchi'])
        self.assertEqual(len(m.table()['common_marginal']), 365)
        self.assertEqual(len(m.table()['leap_marginal']), 366)

    def test_leap_rows(self):
        doc = m.table()
        self.assertEqual(len(doc['common']), 365)
        self.assertEqual(len(doc['leap']), 366)
        self.assertEqual(doc['leap'][59][:2], [2, 29])
        self.assertEqual(doc['units'], {})  # empty on purpose: every ship is class "none"

    def test_csharp_table_matches_json(self):
        text = DATA_CS.read_text(encoding='utf-8')
        doc = m.table()
        for name, key in (('Common', 'common'), ('Leap', 'leap')):
            block = re.search(r'internal static readonly double\[\] ' + name + r' =\s*\{(.*?)\};', text, re.S).group(1)
            values = [float(v) for v in re.findall(r'(-?\d+\.\d+(?:e-?\d+)?)', re.sub(r'//[^\n]*', '', block))]
            expected = [v for row in doc[key] for v in row[2:]]
            self.assertEqual(values, expected, name)
        self.assertIn(doc['sources']['mno_env/seaice.py'], text)

    def test_csharp_marginal_matches_json(self):
        text = DATA_CS.read_text(encoding='utf-8')
        mg = m.table()['marginal']
        for name, key in (('NoIce', 'no_ice'), ('Width', 'width'), ('Max', 'max')):
            const = re.search(r'internal const double Marginal' + name + r' = (-?\d+\.\d+);', text)
            self.assertIsNotNone(const, name)
            self.assertEqual(float(const.group(1)), mg[key], name)
        for sea in mg['seas']:
            block = re.search(r'internal static readonly int\[\] MarginalRows' + sea.capitalize() + r' =\s*\{(.*?)\};', text, re.S).group(1)
            values = [int(v) for v in re.findall(r'-?\d+', block)]
            self.assertEqual(values, [v for row in mg['rows'][sea] for v in row], sea)
        for name, key in (('CommonMarginal', 'common_marginal'), ('LeapMarginal', 'leap_marginal')):
            block = re.search(r'internal static readonly double\[\] ' + name + r' =\s*\{(.*?)\};', text, re.S).group(1)
            values = [float(v) for v in re.findall(r'(-?\d+\.\d+(?:e-?\d+)?)', re.sub(r'//[^\n]*', '', block))]
            expected = [v for row in m.table()[key] for v in row]
            self.assertEqual(len(values), len(mg['seas']) * (366 if key == 'leap_marginal' else 365), name)
            self.assertEqual(values, expected, name)

    def test_longitude_wraps_before_the_model(self):
        # A map grid west of -180 (a view across the antimeridian) must read the same ice as the wrapped
        # longitude: ice_order's Okhotsk branch used raw lon, so 58N -205 read 95 % pack against ~1 % at 155E.
        for day, lat, lon in ((dt.date(2029, 4, 15), 58, 155), (dt.date(2029, 1, 10), 56, 150), (dt.date(2029, 3, 15), 59, 145),
                              (dt.date(2029, 3, 15), 62, -168), (dt.date(2029, 3, 10), 74, 36), (dt.date(2029, 1, 12), -68, -42)):
            want = m.concentration(lat, lon, day)
            for shifted in (lon - 360.0, lon + 360.0):
                self.assertAlmostEqual(m.concentration(lat, shifted, day), want, places=9, msg=(day, lat, shifted))
        self.assertLess(m.concentration(58, -205, dt.date(2029, 4, 15)), 5.0)

    @unittest.skipUnless((ENV / 'mno_env/seaice.py').exists(), 'weather branch checkout not present')
    def test_mirror_matches_seaice_py(self):
        sys.path.insert(0, str(ENV))
        from mno_env import seaice
        doc = m.table()
        for key, year in (('common', 2029), ('leap', 2028)):
            for mo, d, north, south, sh in doc[key][::23]:
                e = m.edges_on(dt.date(year, mo, d))
                ref = seaice.edges_on(dt.datetime(year, mo, d, 12, tzinfo=dt.timezone.utc), doc['baseline'])
                for k in ('north', 'south', 'sh_summer'):
                    self.assertAlmostEqual(e[k], ref[k], places=9, msg=(year, mo, d, k))
                for sea in doc['marginal']['seas']:
                    self.assertAlmostEqual(e['marginal'][sea], ref['marginal'][sea], places=9, msg=(year, mo, d, sea))
                for lat in (-80, -70, -66, -62, -58, -45, 45, 58, 62, 66, 70, 72, 74, 78, 85):
                    for lon in (-175, -168, -160, -100, -55, -42, -25, 8, 22, 36, 120.5, 138, 143.6, 147, 152, 162.5):
                        self.assertAlmostEqual(m.concentration(lat, lon, dt.date(year, mo, d), hard_cap=True), seaice.ice_at(lat, lon, e), places=9)


if __name__ == '__main__':
    unittest.main()
