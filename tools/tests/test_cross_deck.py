#!/usr/bin/env python3
"""SEST Cross-Deck: a stub's file name is ASCII, its #!extend line the real
path; and a deck outside the allied navies takes its campaign fits only.

The 28 Oct 2026 export brought fr_ffg_floréal (Charles De Gaulle & Modern
French Navy's Floréal), the first hull id with a letter outside ASCII. The
game applies an #!extend stub by the target its first line names, whatever
the file is called (IniHandler.ScanForModifierFiles reads every .ini in an
enabled mod's folders), so Cross-Deck names the file in ASCII (stub_name:
Unicode NFKD, accents dropped) and keeps the hull's real path on the
#!extend line.

Makran Line (11 Nov 2026) flies the Pakistani Pack's Z-9CE from the
Pakistan Navy's Tughril and Alamgir, whose lists leave it out. Pakistan is
not an allied navy here, so those two decks take that campaign fit and
nothing from the families (CampaignFitsOutsideTheAllies). The pack checks
need a build; run from the repository root:
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


PAKISTANI_DECKS = ("pns_ffg_oliver_hazard_perry_longhull", "pns_type_054a_p")


class CampaignFitsOutsideTheAllies(unittest.TestCase):
    """plan() skipped every deck whose navy is not allied. A deck in
    CAMPAIGN_DECK_TYPES is now planned whatever its navy, and one outside
    the allies takes its campaign fits and no family member: Makran Line's
    Z-9CE on the Pakistan Navy's two frigate classes (design step P2)."""

    @classmethod
    def setUpClass(cls):
        cls.cd = builder()
        cls.rows = {r[0]: r for r in cls.cd.plan()}

    def test_the_pakistani_decks_take_the_z9ce_and_nothing_else(self):
        for uid in PAKISTANI_DECKS:
            with self.subTest(deck=uid):
                _uid, owner, nat, sec, current, adds = self.rows[uid]
                self.assertEqual((owner, nat, sec), ("3812140001", "pakistan", "FlightDeck"))
                self.assertEqual(dict(adds), {self.cd.CAMPAIGN_FITS: ["plan_z-9ce"]})
                self.assertNotIn("plan_z-9ce", current)
                self.assertEqual(self.cd.nation("aircraft", "plan_z-9ce"), "pakistan")
                text = self.cd.stub(uid, owner, nat, current, adds)
                self.assertTrue(text.startswith(f"#!extend vessels/{uid}.ini\n"))
                self.assertIn("# takes the campaign fit below, which no family reaches", text)
                self.assertNotIn("one of each family", text)
                # The hull's own list, as its author wrote it, then the fit.
                self.assertTrue(text.endswith(
                    "[FlightDeck]\nAircraftSupported=" + ",".join(current) + ",plan_z-9ce\n"))

    def test_no_family_reaches_a_deck_outside_the_allies(self):
        outside = sorted(uid for uid, r in self.rows.items() if r[2] not in self.cd.ALLIES)
        self.assertEqual(outside, list(PAKISTANI_DECKS))
        for uid in outside:
            self.assertIn(uid, self.cd.CAMPAIGN_DECK_TYPES)
            self.assertEqual(list(self.rows[uid][5]), [self.cd.CAMPAIGN_FITS])
        # What keeping Pakistan out of ALLIES keeps off the Alamgir: her list
        # names members of four families (a Lynx, a Wasp, two Alouettes and a
        # Seasprite), and those families would add their allied members.
        self.assertNotIn("pakistan", self.cd.ALLIES)
        alamgir = set(self.rows["pns_ffg_oliver_hazard_perry_longhull"][4])
        self.assertEqual(sorted(f for f, ids in self.cd.FAMILIES.items() if alamgir & set(ids)),
                         ["Alouette / Ecureuil", "Lynx / Wildcat", "Seasprite", "Wasp / Scout"])

    def test_every_other_deck_is_planned_as_before(self):
        # Before: the Pakistani entries out of CAMPAIGN_DECK_TYPES, which is
        # the old rule (a non-allied deck skipped), since no other entry is
        # outside the allies. After: the two decks are the only difference.
        def stubs():
            return {uid: self.cd.stub(uid, o, n, c, a) for uid, o, n, _s, c, a in self.cd.plan()}
        saved = dict(self.cd.CAMPAIGN_DECK_TYPES)
        try:
            for uid in PAKISTANI_DECKS:
                del self.cd.CAMPAIGN_DECK_TYPES[uid]
            before = stubs()
        finally:
            self.cd.CAMPAIGN_DECK_TYPES.clear()
            self.cd.CAMPAIGN_DECK_TYPES.update(saved)
        after = stubs()
        self.assertEqual(sorted(set(after) - set(before)), list(PAKISTANI_DECKS))
        self.assertEqual(set(before) - set(after), set())
        for uid, text in before.items():
            self.assertEqual(after[uid], text, uid)
        # And the committed pack carries those stubs byte for byte: the next
        # rebuild adds the two Pakistani stubs and rewrites no other.
        built = {p.name: p.read_bytes() for p in STUBS.glob("*_CrossDeck_SEST.ini")}
        if not built:
            self.skipTest("SEST Cross-Deck not built")
        for uid, text in before.items():
            self.assertEqual(built.get(self.cd.stub_name(uid)), text.encode("utf-8"), uid)
        self.assertEqual(set(built) - {self.cd.stub_name(u) for u in after}, set())


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
