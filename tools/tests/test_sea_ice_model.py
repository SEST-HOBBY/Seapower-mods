"""SEST battle sea ice: the Python mirror (tools/sea_ice_model.py), the
committed table (tools/sea_ice_edges.json) and the C# data file
(runtime/SeaIceData.g.cs) agree with each other and with the weather
branch's mno_env/seaice.py (when that checkout is present)."""
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


class SeaIceModelTests(unittest.TestCase):
    def test_review_points(self):
        # The adversarial review ran seaice.py: 10 March 36E 72N 18.7 %, 74N 62.3 %; 12 Jan 68S 42W 37.1 %.
        doc = m.table()
        for y, mo, d, lat, lon, pct in doc['review_points']:
            self.assertAlmostEqual(m.concentration(lat, lon, dt.date(y, mo, d)), pct, places=9)
        self.assertAlmostEqual(m.concentration(72, 36, dt.date(2029, 3, 10)), 18.7, places=1)
        self.assertAlmostEqual(m.concentration(74, 36, dt.date(2029, 3, 10)), 62.3, places=1)
        self.assertAlmostEqual(m.concentration(-68, -42, dt.date(2029, 1, 12)), 37.1, places=1)

    def test_hemisphere_seasons(self):
        self.assertGreater(m.concentration(75, 36, dt.date(2029, 3, 15)), m.concentration(75, 36, dt.date(2029, 9, 15)) + 40)
        self.assertGreater(m.concentration(-62, -40, dt.date(2029, 9, 15)), m.concentration(-62, -40, dt.date(2029, 2, 20)) + 40)
        self.assertEqual(m.concentration(39.9, 120.5, dt.date(2029, 1, 15)), 0.0)
        self.assertEqual(m.concentration(-60, 0, dt.date(2029, 3, 10)) == 0.0, False)

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
                        self.assertAlmostEqual(m.concentration(lat, lon, dt.date(year, mo, d)), seaice.ice_at(lat, lon, e), places=9)


if __name__ == '__main__':
    unittest.main()
