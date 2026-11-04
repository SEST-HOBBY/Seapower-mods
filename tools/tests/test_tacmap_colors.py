"""SEST TacMap Colors carries the public beta's tactical map keys."""
import importlib.util
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("tacmap_build", ROOT / "integration/tacmap-colors/build_pack.py")
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)
REL = "ui/Default/Settings_UI_Tactical.ini"


def keys(text):
    return {m.group(1): m.group(2) for m in re.finditer(r"^([A-Za-z0-9_]+)=([^\s#/]+)", text, re.M)}


class BetaKeys(unittest.TestCase):
    def setUp(self):
        self.vanilla = (ROOT / "mods-source/_vanilla/original" / REL).read_text(encoding="utf-8-sig")
        self.built = (ROOT / "integration/tacmap-colors/SEST_TacMap_Colors" / REL).read_text(encoding="utf-8-sig")
        self.dist = (ROOT / "integration/dist/SEST_Integration" / REL).read_text(encoding="utf-8-sig")

    def test_thirty_two_beta_keys(self):
        self.assertEqual(sum(len(v) for v in BUILD.BETA_KEYS.values()), 32)

    def test_built_file_has_every_beta_key_at_the_beta_default(self):
        built = keys(self.built)
        for section, pairs in BUILD.BETA_KEYS.items():
            for key, value in pairs:
                self.assertEqual(built.get(key), value, key)

    def test_keys_sit_in_their_sections(self):
        for section, pairs in BUILD.BETA_KEYS.items():
            start = self.built.index(f"[{section}]")
            end = self.built.find("\n[", start + 1)
            body = self.built[start:end if end > 0 else None]
            for key, _ in pairs:
                self.assertIn(f"\n{key}=", body, f"{key} outside [{section}]")

    def test_stable_export_lacks_them_and_the_builder_adds_only_those(self):
        vanilla, built = keys(self.vanilla), keys(self.built)
        beta = {k for pairs in BUILD.BETA_KEYS.values() for k, _ in pairs}
        missing = beta - set(vanilla)
        self.assertEqual(set(built) - set(vanilla), missing)
        text, added = BUILD.add_beta_keys(self.vanilla)
        self.assertEqual(added, len(missing))
        again, added_again = BUILD.add_beta_keys(text)
        self.assertEqual((again, added_again), (text, 0))

    def test_stable_keys_unchanged_except_the_waypoint_edits(self):
        vanilla, built = keys(self.vanilla), keys(self.built)
        edited = {"WaypointsLineColor", "NightWaypointsLineColor", "WaypointSelectedColor", "NightWaypointSelectedColor",
                  "FormationMembershipLineColor", "NightFormationMembershipLineColor", "WaypointLineThickness"}
        for key, value in vanilla.items():
            if key not in edited:
                self.assertEqual(built.get(key), value, key)

    def test_dist_copy_matches_the_pack(self):
        self.assertEqual(self.dist, self.built)


if __name__ == "__main__":
    unittest.main()
