#!/usr/bin/env python3
"""tools/make_sest_weather.py: the placed-storms sidecar builder (20 Nov 2026).

The rules mirror the runtime's StormSidecar.Parse
(integration/beta-feature-parity/runtime/StormSidecar.cs); the managed test
WorldStormsTests.cs parses the committed Hormuz sidecar with the runtime's
own reader, so the two are checked against the same bytes, and both this
test and WorldStormsTests run every edge case in sest_weather_cases.json and
must reach its accept/reject verdict.
    python3 -m unittest discover -s tools/tests -p 'test_make_sest_weather.py' -v
"""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import make_sest_weather as w  # noqa: E402

SPEC = {"storms": [{"id": "test-1", "name": "TESTA", "kind": "Cyclone", "track": [
    ["2028-01-15T00:00Z", 20.0, 64.0, 60, 200, 22],
    ["2028-01-15T12:00Z", 22.0, 62.0, 90, 240, 20],
    ["2028-01-16T00:00:00Z", 24.0, 60.0, 50, 180, 24]]}]}
CASES = Path(__file__).resolve().parent / "sest_weather_cases.json"


def case_bytes(case):
    """The file bytes of one edge case (WorldStormsTests encodes them the same way)."""
    text, enc = case["text"], case["encoding"]
    if enc == "hex":
        return bytes.fromhex(text)
    if enc == "utf-8-bom":
        return b"\xef\xbb\xbf" + text.encode("utf-8")
    if enc == "utf-16le-bom":
        return b"\xff\xfe" + text.encode("utf-16-le")
    assert enc == "utf-8", enc
    return text.encode("utf-8")
HORMUZ = ROOT / "integration/test-campaigns/Test_Campaigns/dynamic_campaigns/sest-test-hormuz-weather"


class Builder(unittest.TestCase):
    def test_spec_becomes_a_checked_sidecar(self):
        doc = w.build(SPEC)
        self.assertEqual(doc["format"], "sest-weather/1")
        s = doc["storms"][0]
        self.assertEqual([p["utc"] for p in s["waypoints"]],
                         ["2028-01-15T00:00:00Z", "2028-01-15T12:00:00Z", "2028-01-16T00:00:00Z"])
        self.assertEqual([p["rmw"] for p in s["waypoints"]], [22, 20, 24])
        self.assertEqual(w.check(doc), [])
        plain = copy.deepcopy(SPEC)
        for row in plain["storms"][0]["track"]:
            del row[5]
        self.assertTrue(all("rmw" not in p for p in w.build(plain)["storms"][0]["waypoints"]))
        partial = copy.deepcopy(SPEC)
        del partial["storms"][0]["track"][0][5]
        with self.assertRaisesRegex(w.SpecError, "rmw must be on every waypoint of the storm or on none"):
            w.build(partial)

    def test_output_is_deterministic_ascii_lf(self):
        with tempfile.TemporaryDirectory() as d:
            a = w.write(w.build(SPEC), Path(d) / "a" / w.FILE_NAME).read_bytes()
            b = w.write(w.build(copy.deepcopy(SPEC)), Path(d) / "b" / w.FILE_NAME).read_bytes()
        self.assertEqual(a, b)
        self.assertNotIn(b"\r", a)
        self.assertTrue(a.endswith(b"}\n"))
        a.decode("ascii")

    def test_every_rule_rejects(self):
        def broken(change):
            doc = w.build(SPEC)
            change(doc)
            return w.check(doc)
        cases = {
            "format": lambda d: d.update(format="sest-weather/2"),
            "unknown field": lambda d: d.update(extra=1),
            "no storms": lambda d: d.update(storms=[]),
            "id": lambda d: d["storms"][0].update(id="Bad Id"),
            "twice": lambda d: d["storms"].append(copy.deepcopy(d["storms"][0])),
            "name": lambda d: d["storms"][0].update(name=""),
            "long name": lambda d: d["storms"][0].update(name="X" * 25),
            "kind": lambda d: d["storms"][0].update(kind="Medicane"),
            "one waypoint": lambda d: d["storms"][0].update(waypoints=d["storms"][0]["waypoints"][:1]),
            "time order": lambda d: d["storms"][0]["waypoints"][2].update(utc="2028-01-15T06:00:00Z"),
            "time form": lambda d: d["storms"][0]["waypoints"][0].update(utc="2028-01-15 00:00"),
            "lat": lambda d: d["storms"][0]["waypoints"][0].update(lat=86),
            "wind": lambda d: d["storms"][0]["waypoints"][0].update(wind=200),
            "wind type": lambda d: d["storms"][0]["waypoints"][0].update(wind="60"),
            "radius": lambda d: d["storms"][0]["waypoints"][0].update(radius=10),
            "rmw": lambda d: d["storms"][0]["waypoints"][1].update(rmw=300),
            "nan": lambda d: d["storms"][0]["waypoints"][0].update(lon=float("nan")),
            "30 days": lambda d: d["storms"][0]["waypoints"][2].update(utc="2028-03-01T00:00:00Z"),
        }
        for name, change in cases.items():
            with self.subTest(name):
                self.assertTrue(broken(change), name)
        with self.assertRaises(w.SpecError):
            w.build({"storms": [{"id": "x", "name": "X", "kind": "Storm", "track": [["2028-01-15T00:00Z", 1, 2, 3]]}]})

    def test_edge_cases_reach_the_runtime_verdict(self):
        doc = json.loads(CASES.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(doc["cases"]), 60)
        names = [c["name"] for c in doc["cases"]]
        self.assertEqual(len(names), len(set(names)))
        self.assertTrue(any(c["accept"] for c in doc["cases"]) and any(not c["accept"] for c in doc["cases"]))
        for case in doc["cases"]:
            with self.subTest(case["name"]):
                errors = w.check_bytes(case_bytes(case))
                self.assertEqual(not errors, case["accept"], errors)

    def test_check_reads_bytes_as_the_runtime(self):
        good = w.dumps(w.build(SPEC))
        self.assertEqual(w.check_bytes(b"\xef\xbb\xbf" + good.encode()), [])
        self.assertEqual(w.check_bytes(b"\xff\xfe" + good.encode("utf-16-le")), [])
        self.assertIn("repeats key", w.check_bytes(good.replace('"format"', '"format": "x", "format"', 1).encode())[0])
        self.assertTrue(w.check_bytes(b"{"))
        self.assertTrue(w.check_bytes(good.replace('"test-1"', '"test-1\\n"').encode()))

    def test_interpolation_matches_the_runtime_rule(self):
        s = w.build(SPEC)["storms"][0]
        t = lambda h: datetime(2028, 1, 15, tzinfo=timezone.utc).replace(hour=h)
        self.assertEqual(w.position(s, t(0)), (20.0, 64.0, 60, 200))
        lat, lon, wind, radius = w.position(s, t(6))
        self.assertAlmostEqual(lat, 21.0)
        self.assertAlmostEqual(lon, 63.0)
        self.assertAlmostEqual(wind, 75)
        self.assertAlmostEqual(radius, 220)
        self.assertIsNone(w.position(s, datetime(2028, 1, 16, 1, tzinfo=timezone.utc)))
        self.assertAlmostEqual(w.distance_nm(0, 0, 1, 0), 60.04, places=1)

    def test_cli_writes_and_checks(self):
        with tempfile.TemporaryDirectory() as d:
            spec = Path(d) / "spec.json"
            spec.write_text(json.dumps(SPEC))
            out = Path(d) / w.FILE_NAME
            r = subprocess.run([sys.executable, str(ROOT / "tools/make_sest_weather.py"), str(spec), str(out)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            r = subprocess.run([sys.executable, str(ROOT / "tools/make_sest_weather.py"), "--check", str(out)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("sest-test-1: Cyclone TESTA", r.stdout)
            out.write_text(out.read_text().replace('"Cyclone"', '"Medicane"'))
            r = subprocess.run([sys.executable, str(ROOT / "tools/make_sest_weather.py"), "--check", str(out)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)
            self.assertIn("REJECTED", r.stdout)
            for bad, why in ((b"{\"format\": ", "JSON"), (b'{"format": 1, "format": 2}', "repeats key")):
                out.write_bytes(bad)
                r = subprocess.run([sys.executable, str(ROOT / "tools/make_sest_weather.py"), "--check", str(out)], capture_output=True, text=True)
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertIn("REJECTED", r.stdout)
                self.assertNotIn("Traceback", r.stderr)
            out.write_bytes(b"\xef\xbb\xbf" + w.dumps(w.build(SPEC)).encode())
            r = subprocess.run([sys.executable, str(ROOT / "tools/make_sest_weather.py"), "--check", str(out)], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class HormuzFixture(unittest.TestCase):
    """The committed test campaign's storm, as README-TESTS.txt describes it."""

    def test_committed_sidecar_is_the_builder_output(self):
        sys.path.insert(0, str(ROOT / "integration/test-campaigns"))
        import make_test_campaigns as campaigns
        path = HORMUZ / w.FILE_NAME
        self.assertEqual(path.read_bytes(), w.dumps(w.build(campaigns.HORMUZ_STORM)).encode("ascii"),
                         "rerun integration/test-campaigns/make_test_campaigns.py")
        doc = json.loads(path.read_text())
        campaign = json.loads((HORMUZ / "campaign.json").read_text())
        self.assertEqual(w.check(doc), [])
        self.assertEqual(w.check_campaign(doc, campaign), [])
        lines = campaigns.storm_check(doc, campaign)
        self.assertTrue(all(x.endswith("PASS") for x in lines), lines)
        self.assertEqual(doc["storms"][0]["kind"], "Cyclone")


if __name__ == "__main__":
    unittest.main()
