"""The r16 battle sea-ice hand-off (handoff/r16-sea-ice) is pinned to the SHA-256 of the weather
sources its generator reads (make_sea_ice_data.py SOURCES: seaice.py, geo.py, ice.py and three
data files). Any edit to one of them, even a comment, makes the bundled SeaIceData.g.cs and
sea_ice_edges.json stale, and r16's SeaIceModel gate would then refuse them. This test catches
that drift here, on the weather branch, before the hand-off is applied."""
import hashlib
import json
import re
import unittest
from pathlib import Path

ENV = Path(__file__).resolve().parents[1]
HANDOFF = ENV / "handoff" / "r16-sea-ice"
EDGES = HANDOFF / "tools" / "sea_ice_edges.json"
DATA_CS = HANDOFF / "integration" / "beta-feature-parity" / "runtime" / "SeaIceData.g.cs"
GENERATOR = HANDOFF / "tools" / "make_sea_ice_data.py"

REGENERATE = ("regenerate the hand-off: cd integration/environment/handoff/r16-sea-ice && "
              "python3 tools/make_sea_ice_data.py --env <this checkout>/integration/environment --full "
              "(about 6 minutes on 4 cores; see its README)")


@unittest.skipUnless(EDGES.exists(), "no r16 sea-ice hand-off in this checkout")
class TestHandoffIsCurrent(unittest.TestCase):
    def test_source_hashes_match_the_weather_sources(self):
        sources = json.loads(EDGES.read_text(encoding="utf-8"))["sources"]
        listed = re.search(r"SOURCES = \((.*?)\)\n", GENERATOR.read_text(encoding="utf-8"), re.S).group(1)
        self.assertEqual(sorted(sources), sorted(re.findall(r"'([^']+)'", listed)), "the generator's SOURCES and the stamped list differ")
        for rel, digest in sorted(sources.items()):
            now = hashlib.sha256((ENV / rel).read_bytes()).hexdigest()
            self.assertEqual(now, digest, rel + " changed since the hand-off was generated: " + REGENERATE)

    def test_csharp_data_carries_the_same_stamp(self):
        sources = json.loads(EDGES.read_text(encoding="utf-8"))["sources"]
        text = DATA_CS.read_text(encoding="utf-8")
        self.assertIn('SourceSeaIcePy = "' + sources["mno_env/seaice.py"] + '"', text, REGENERATE)


if __name__ == "__main__":
    unittest.main()
