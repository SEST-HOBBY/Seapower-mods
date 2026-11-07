#!/usr/bin/env python3
"""SEST Cross-Deck: a stub's file name is ASCII, its #!extend line the real path.

The 28 Oct 2026 export brought fr_ffg_floréal (Charles De Gaulle & Modern
French Navy's Floréal), the first hull id with a letter outside ASCII. The
game applies an #!extend stub by the target its first line names, whatever
the file is called (IniHandler.ScanForModifierFiles reads every .ini in an
enabled mod's folders), so Cross-Deck names the file in ASCII (stub_name:
Unicode NFKD, accents dropped) and keeps the hull's real path on the
#!extend line. The pack checks need a build; run from the repository root:
    python3 -m unittest discover -s tools/tests -p 'test_cross_deck.py' -v
"""
import importlib.util
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STUBS = ROOT / "integration/cross-deck/SEST_Cross_Deck/vessels_overwrite"
DIST = ROOT / "integration/dist/SEST_Integration/vessels_overwrite"
EXTEND = re.compile(r"#!extend vessels/([^\n/]+)\.ini\n")


def builder():
    """integration/cross-deck/build_pack.py under a name of its own; the
    sys.path entry it adds for its import is taken back."""
    spec = importlib.util.spec_from_file_location(
        "sest_cross_deck_build_pack", ROOT / "integration/cross-deck/build_pack.py")
    module = importlib.util.module_from_spec(spec)
    saved = list(sys.path)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = saved
    return module


class StubName(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cd = builder()

    def test_an_ascii_id_keeps_its_name(self):
        self.assertEqual(self.cd.stub_name("ran_ffh_anzac"), "ran_ffh_anzac_CrossDeck_SEST.ini")
        self.assertEqual(self.cd.stub_name("pn_ffg-150"), "pn_ffg-150_CrossDeck_SEST.ini")

    def test_the_accents_are_dropped(self):
        for uid in ("fr_ffg_floréal", "fr_ffg_floréal"):     # composed, decomposed
            with self.subTest(uid=ascii(uid)):
                self.assertEqual(self.cd.stub_name(uid), "fr_ffg_floreal_CrossDeck_SEST.ini")

    def test_a_letter_with_no_plain_spelling_stops_the_build(self):
        for uid in ("de_fgs_straße", "jmsdf_ddh_いずも"):
            with self.subTest(uid=ascii(uid)):
                with self.assertRaises(SystemExit):
                    self.cd.stub_name(uid)

    def test_the_stub_names_the_real_path(self):
        text = self.cd.stub("fr_ffg_floréal", "3567256221", "france",
                            ["fr_as-565_sa", "fr_aliaca"], {"Panther / S-76": ["phl_h-76"]})
        self.assertTrue(text.startswith("#!extend vessels/fr_ffg_floréal.ini\n"))
        self.assertIn("(fr_ffg_floreal_CrossDeck_SEST.ini)", text)
        self.assertTrue(text.endswith(
            "[FlightDeck]\nAircraftSupported=fr_as-565_sa,fr_aliaca,phl_h-76\n"))

    def test_an_ascii_stub_is_unchanged(self):
        text = self.cd.stub("ran_ffh_anzac", "SEST_RAN_Fleet", "australia", ["ran_mh-60r"],
                            {"Seahawk (S-70B / SH-60 / MH-60)": ["usn_mh-60r"]})
        self.assertNotIn("in ASCII", text)
        self.assertTrue(text.isascii())


class BuiltStubs(unittest.TestCase):
    """The built pack and the consolidated one: every stub's name is ASCII and
    is the stub_name of the hull its #!extend line names."""

    @classmethod
    def setUpClass(cls):
        cls.cd = builder()
        cls.stubs = sorted(STUBS.glob("*_CrossDeck_SEST.ini"))

    def setUp(self):
        if not self.stubs:
            self.skipTest("SEST Cross-Deck not built")

    def test_every_name_is_the_ascii_spelling_of_its_target(self):
        targets = []
        for stub in self.stubs:
            with self.subTest(stub=stub.name):
                self.assertTrue(stub.name.isascii())
                head = EXTEND.match(stub.read_text(encoding="utf-8"))
                self.assertTrue(head)
                targets.append(head.group(1))
                self.assertEqual(stub.name, self.cd.stub_name(head.group(1)))
        self.assertEqual(len(targets), len(set(targets)))
        if all(t.isascii() for t in targets):
            self.skipTest("no hull id outside ASCII in this export")

    def test_no_path_in_the_pack_is_outside_ascii(self):
        root = STUBS.parent
        self.assertEqual([p.relative_to(root).as_posix() for p in root.rglob("*")
                          if not p.relative_to(root).as_posix().isascii()], [])

    def test_the_consolidated_pack_ships_the_same_stubs(self):
        shipped = sorted(DIST.glob("*_CrossDeck_SEST.ini"))
        self.assertEqual([p.name for p in shipped], [p.name for p in self.stubs])
        for built, dist in zip(self.stubs, shipped):
            with self.subTest(stub=built.name):
                self.assertEqual(dist.read_bytes(), built.read_bytes())


if __name__ == "__main__":
    unittest.main()
