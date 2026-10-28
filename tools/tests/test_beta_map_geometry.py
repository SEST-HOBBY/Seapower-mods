"""Synthetic read-only geometry tests; no game content is modified."""
import contextlib
import io
import json
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

    def test_far_high_centre_is_not_a_high_latitude_mission(self):
        # The Northern Front datum: centre in the North Atlantic, units at Darwin.
        p = self.make_file("""[Environment]
MapCenterLatitude=54.27
MapCenterLongitude=-26.28
[Darwin]
RelativePositionInNM=9429.85,low,-4001.8
Waypoints=9440,0,-4000|Loop
""")
        row = geo.analyze(p)
        self.assertEqual(row['priority'], 'P1')        # the centre still counts
        self.assertNotIn('high latitude', row['notes'])
        self.assertIn('map centre at 54.3 deg, positions below 50', row['notes'])
        self.assertGreater(row['centre_nearest_nm'], 6000)
        self.assertIn(f"map centre {row['centre_nearest_nm']:,.0f} NM from the nearest",
                      row['notes'])
        self.assertAlmostEqual(geo.great_circle_nm((0, 0), (1, 0)), 60.04, places=2)

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


CAMPAIGN = {
    "bounds": {"latMin": -62.0, "latMax": 74.0, "lonMin": -100.0, "lonMax": 258.0},
    "view": {"lat": 89.0, "lon": 300.0},
    "labels": [{"text": "cosmetic", "lat": 89.5, "lon": 400.0}],
    "bases": [
        {"id": "san_diego", "lat": 32.7, "lon": 242.8,
         "field": {"unit": "x", "lat": 32.7, "lon": 242.8}},
        {"id": "severomorsk", "lat": 69.07, "lon": 33.42},
        {"id": "darwin", "lat": -12.4, "lon": 130.8},
    ],
    "forces": [
        {"name": "Carl Vinson group", "at": [32.284, 242.9]},
        {"name": "Harbour", "base": "darwin"},
    ],
    "patrols": [
        {"force": "Fiji patrol", "points": [[-17.0, 179.8], [-17.5, 179.9],
                                            [-17.5, -179.8], [-17.0, -179.9]]},
    ],
    "traffic": {
        "lanes": [{"name": "Trans-Pacific", "points": [[30.0, 160.0], [24.0, 190.0],
                                                        [22.0, 202.2]]}],
        "airways": [{"name": "Honolulu to San Diego",
                     "points": [[21.32, 202.08], [32.73, 242.81]]}],
    },
}


class WorldSandboxCampaignTests(unittest.TestCase):
    def make_campaign(self, data, name='campaign.json'):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / name
        path.write_text(json.dumps(data), encoding='utf-8')
        return path

    def test_world_positions_and_seams(self):
        row = geo.analyze_campaign(self.make_campaign(CAMPAIGN))
        self.assertEqual(row['kind'], 'campaign')
        self.assertEqual(row['priority'], 'P1')
        # 3 bases + 1 airfield + 1 placed force + 4 patrol + 3 lane + 2 airway
        self.assertEqual(row['points'], 14)
        self.assertEqual(row['waypoints'], 9)
        # San Diego, its airfield, the carrier, two lane and two airway points
        self.assertEqual(row['lon_past_180'], 7)
        # Trans-Pacific 160 -> 190, and the Fiji ring twice (out and back)
        self.assertEqual(row['dateline_legs'], 3)
        self.assertEqual(row['high_lat_positions'], 1)
        self.assertEqual(row['outside_bounds'], 2)      # Fiji's -179.8, -179.9 < lonMin
        self.assertEqual(row['lat_max_abs'], 69.07)     # labels and view ignored
        self.assertEqual(row['lon_max'], 242.9)
        self.assertIn('route legs cross 180', row['notes'])
        seams = {(what, name) for what, name, _, _ in row['detail']['seam']}
        self.assertEqual(seams, {('lane', 'Trans-Pacific'), ('patrol', 'Fiji patrol')})

    def test_continuous_longitudes_without_a_seam(self):
        data = dict(CAMPAIGN, patrols=[], traffic={"airways": CAMPAIGN['traffic']['airways']},
                    bases=CAMPAIGN['bases'][:1])
        row = geo.analyze_campaign(self.make_campaign(data))
        self.assertEqual(row['dateline_legs'], 0)
        self.assertFalse(row['dateline'])
        self.assertEqual(row['priority'], 'P3')
        self.assertEqual(row['lon_past_180'], 5)

    def test_scan_reads_campaign_json_only(self):
        path = self.make_campaign(CAMPAIGN)
        (path.parent / 'lanes.json').write_text('{"a": [[0, 0], [1, 1]]}', encoding='utf-8')
        (path.parent / 'not-a-campaign').mkdir()
        (path.parent / 'not-a-campaign' / 'campaign.json').write_text('{"name": "x"}',
                                                                      encoding='utf-8')
        rows = geo.scan([path.parent])
        self.assertEqual([r['kind'] for r in rows], ['campaign'])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            geo.print_report(rows)
        self.assertIn('crosses 180: lane Trans-Pacific (30, 160) to (24, 190)', out.getvalue())
        self.assertIn('bases san_diego', out.getvalue())

    def test_default_roots_exist(self):
        for root in geo.DEFAULT_ROOTS:
            self.assertTrue(root.is_dir(), root)


if __name__ == '__main__':
    unittest.main()
