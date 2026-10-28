"""Synthetic read-only geometry tests; no game content is modified."""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import audit_beta_map_geometry as geo


class BetaGeometryTests(unittest.TestCase):
    def make_file(self, content, name='mission.ini'):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / name
        path.write_text(content, encoding='utf-8')
        return path

    def test_macquarie_sest_waypoint_grammar(self):
        # The forms SEST missions use: orders after '/', a depth word in the
        # height field, an empty token and a closing Loop.
        p = self.make_file("""[Environment]
MapCenterLatitude=-54.3
MapCenterLongitude=158.3
[Taskforce1Vessel1]
RelativePositionInNM=0,0,0
Waypoints=-42,0,-39/SetTelegraph,3|30,Periscope,-20||12,0,9/SetTelegraph,2/SetSensors,AirSearch_Off,SurfaceSearch_Off|Loop
[Taskforce2Vessel1]
RelativePositionInNM=5,0,5
Waypoints=6,0,6/AttackAtWaypoint,plan_yj18a,Taskforce1Vessel1,2|7,BelowLayer,7|loop
""")
        row = geo.analyze(p)
        self.assertEqual(row['priority'], 'P1')
        self.assertEqual(row['waypoints'], 5)
        self.assertEqual(row['points'], 7)
        self.assertEqual(row['dynamic_waypoints'], 0)
        self.assertNotIn('run time', row['notes'])
        self.assertNotIn('play area', row['notes'])
        self.assertEqual(row['north_south_nm_est'], 48.0)   # z from -39 to 9
        self.assertLess(row['globe_east_west_nm_est'], row['legacy_east_west_nm'])

    def test_loop_ends_the_route(self):
        center = (0.0, 0.0)
        points, unplaced = geo.waypoint_points('60,0,0|LOOP|600,0,600', center)
        self.assertEqual(points, [(0.0, 1.0)])
        self.assertEqual(unplaced, 0)

    def test_keyword_leg_is_counted_not_mapped(self):
        # Course,heading,distance,height is placed from the unit at run time.
        p = self.make_file("""[Environment]
MapCenterLatitude=10
MapCenterLongitude=120
[A]
RelativePositionInNM=0,0,0
Waypoints=10,0,10|Course,90,20,0/SetTelegraph,2|Loop
""")
        row = geo.analyze(p)
        self.assertEqual(row['waypoints'], 1)
        self.assertEqual(row['dynamic_waypoints'], 1)
        self.assertIn('1 waypoint placed at run time', row['notes'])

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

    def test_play_area_caveat_is_printed_once(self):
        p = self.make_file("""[Environment]
MapCenterLatitude=0
MapCenterLongitude=0
[A]
RelativePositionInNM=0,0,0
""")
        rows = geo.scan([p.parent])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            geo.print_report(rows)
        self.assertEqual(out.getvalue().count('play area'), 1)
        self.assertIn('1 of 1 missions set no play-area key', out.getvalue())



if __name__ == '__main__':
    unittest.main()
