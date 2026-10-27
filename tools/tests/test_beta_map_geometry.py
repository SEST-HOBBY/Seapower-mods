"""Synthetic read-only geometry tests; no game content is modified."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import audit_beta_map_geometry as geo


class BetaGeometryTests(unittest.TestCase):
    def make_file(self, content):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / 'mission.ini'
        path.write_text(content, encoding='utf-8')
        return path

    def test_macquarie_positions_and_dynamic_route(self):
        p = self.make_file("""[Environment]
MapCenterLatitude=-54.3
MapCenterLongitude=158.3
[Taskforce1Vessel1]
RelativePositionInNM=0,0,0
Waypoints=-42,0,-39|Turn,40,5,current|30,shallow,-20|Loop
""")
        row = geo.analyze(p)
        self.assertEqual(row['priority'], 'P1')
        self.assertEqual(row['points'], 3)
        self.assertEqual(row['waypoints'], 2)
        self.assertEqual(row['dynamic_waypoints'], 2)
        self.assertLess(row['globe_east_west_nm_est'], row['legacy_east_west_nm'])

    def test_dateline_shortest_span(self):
        p = self.make_file("""[Environment]
MapCenterLatitude=-12
MapCenterLongitude=179.5
[A]
RelativePositionInNM=0,0,0
[B]
RelativePositionInNM=120,0,0
""")
        row = geo.analyze(p)
        self.assertTrue(row['dateline'])
        self.assertEqual(row['priority'], 'P1')
        self.assertAlmostEqual(row['longitude_span_deg'], 2.0)

    def test_crosses_dateline_without_near_170_endpoints(self):
        # 160 E -> 160 W crosses the 180-degree seam even though neither
        # point passes the old +/-170 threshold.
        p = self.make_file("""[Environment]
MapCenterLatitude=0
MapCenterLongitude=160
[A]
RelativePositionInNM=0,0,0
[B]
RelativePositionInNM=2400,0,0
""")
        row = geo.analyze(p)
        self.assertTrue(row['dateline'])
        self.assertEqual(row['priority'], 'P1')
        self.assertAlmostEqual(row['longitude_span_deg'], 40.0)

    def test_zero_meridian_not_mistaken_for_dateline(self):
        self.assertEqual(geo.longitude_arc([350, 10]), (20, False))
        self.assertEqual(geo.longitude_arc([179, -179]), (2, True))
        self.assertEqual(geo.longitude_arc([179, 175]), (4, False))

    def test_parent_relative_is_not_georeferenced(self):
        p = self.make_file("""[Environment]
MapCenterLatitude=0
MapCenterLongitude=0
[A]
GeoPosition=0,0,0
[B]
PositionRelativeTo=A
RelativePositionInNM=10000,0,10000
Waypoints=12,0,9
""")
        row = geo.analyze(p)
        self.assertEqual(row['relative_sections'], 1)
        self.assertEqual(row['points'], 1)
        self.assertEqual(row['priority'], 'P3')

    def test_missing_center_and_bad_lat(self):
        self.assertIsNone(geo.analyze(self.make_file('[A]\nGeoPosition=0,0,0\n')))
        self.assertIsNone(geo.relative_point('0,0,9999', (0, 0)))
        self.assertEqual(geo.longitude_span([-179, 179]), 2)


if __name__ == '__main__':
    unittest.main()
