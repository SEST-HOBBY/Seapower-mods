import copy
import datetime as dt
import gzip
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

from helpers import START, UTC, procedural_snapshot, state, t0

from mno_env import procedural, snapshot
from mno_env.clock import (MnoEnvClock, MnoEnvState, analogue_offset, analogue_source_time, digest_samples,
                           from_seconds, to_seconds)
from mno_env.grid import LatLonGrid
from mno_env.ingest import build


def tiny(data_class="observed", kind="observed", issue=None, values=None, times=None):
    g = LatLonGrid(-180, -90, 180, 90, 2, 3)
    frames = times or [(START, None if issue is None else 0.0, {"sea_ice_conc_pct": values or [0, 0, 10, 20, 90, 95]})]
    prov = {"provider": "Fixture", "product": "fixture" if data_class not in ("synthetic", "procedural") else "SYNTHETIC fixture",
            "product_version": "1", "licence": "CC0", "attribution": "test", "source_url": None, "downloaded_utc": None,
            "source_time_utc": snapshot.iso(START), "forecast_issue_utc": None if issue is None else snapshot.iso(issue)}
    mapping = {"mode": "historical_analogue" if data_class not in ("synthetic", "procedural") else "procedural",
               "offset_seconds": 0, "statement": "Replayed analogue; not a forecast of 2028."}
    return build(snapshot_id="fixture-1", data_class=data_class, provenance=prov, mapping=mapping, grid=g, frames=frames,
                 kinds={"sea_ice_conc_pct": kind}, created=START)


class TestSnapshot(unittest.TestCase):
    def test_procedural_is_valid_and_deterministic(self):
        a = procedural_snapshot()
        self.assertEqual(snapshot.validate(a), [])
        b = procedural.generate("test-seed", START, hours=72)
        self.assertEqual(snapshot.dumps(a), snapshot.dumps(b))
        c = procedural.generate("other-seed", START, hours=72)
        self.assertNotEqual(a["integrity"]["payload_sha256"], c["integrity"]["payload_sha256"])

    def test_fixture_valid(self):
        self.assertEqual(snapshot.validate(tiny()), [])

    def assertInvalid(self, snap, fragment):
        errs = snapshot.validate(snap)
        self.assertTrue(any(fragment in e for e in errs), f"expected {fragment!r} in {errs}")

    def test_corruptions(self):
        s = tiny()
        s["times"][0]["values"]["sea_ice_conc_pct"][0] = 50
        self.assertInvalid(s, "payload_sha256")
        s = snapshot.seal(tiny()); s["fields"]["sea_ice_conc_pct"]["units"] = "fraction"; snapshot.seal(s)
        self.assertInvalid(s, "units must be")
        s = tiny(); s["times"][0]["values"]["sea_ice_conc_pct"][0] = float("nan")
        with self.assertRaises(ValueError):  # NaN cannot even be sealed/serialised
            snapshot.seal(s)
        s = tiny(values=[0, 0, 10, 20, 90, 150])
        self.assertInvalid(s, "outside")
        s = tiny(); s["times"][0]["values"]["sea_ice_conc_pct"] = [1, 2]; snapshot.seal(s)
        self.assertInvalid(s, "values for a 2x3 grid")
        s = tiny(); s["created_utc"] = "2028-09-14T06:00:00"
        self.assertInvalid(s, "ending in Z")
        s = tiny(); del s["provenance"]["licence"]
        self.assertInvalid(s, "licence")
        s = tiny(); s["campaign_mapping"]["statement"] = "real 2028 weather"
        self.assertInvalid(s, "not a forecast")

    def test_labelling_rules(self):
        self.assertInvalid(tiny(data_class="synthetic", kind="observed"), "cannot label")
        self.assertInvalid(tiny(data_class="forecast"), "forecast_issue_utc")
        self.assertInvalid(tiny(issue=START), "must not carry a forecast issue")
        s = tiny(data_class="synthetic", kind="synthetic"); s["campaign_mapping"]["mode"] = "historical_analogue"; snapshot.seal(s)
        self.assertInvalid(s, "analogue mapping needs real source data")

    def test_forecast_lead_and_order(self):
        issue = START
        frames = [(START + dt.timedelta(hours=6), 6.0, {"sea_ice_conc_pct": [0] * 6}),
                  (START + dt.timedelta(hours=12), 11.0, {"sea_ice_conc_pct": [0] * 6})]
        s = tiny(data_class="forecast", kind="forecast", issue=issue, times=frames)
        s["provenance"]["source_time_utc"] = snapshot.iso(issue); snapshot.seal(s)
        self.assertInvalid(s, "lead_hours must equal")
        frames = [(START + dt.timedelta(hours=12), 12.0, {"sea_ice_conc_pct": [0] * 6}),
                  (START + dt.timedelta(hours=6), 6.0, {"sea_ice_conc_pct": [0] * 6})]
        self.assertInvalid(tiny(data_class="forecast", kind="forecast", issue=issue, times=frames), "strictly increasing")

    def test_thunderstorm_is_never_observed(self):
        g = LatLonGrid(-180, -90, 180, 90, 2, 3)
        s = tiny()
        s["fields"]["convective_risk_idx"] = {"units": snapshot.FIELDS["convective_risk_idx"][0], "kind": "observed", "uncertainty": {}}
        s["times"][0]["values"]["convective_risk_idx"] = [0] * g.size
        snapshot.seal(s)
        self.assertInvalid(s, "derived_risk")

    def test_pack_roundtrip_and_files(self):
        vals = [0.0, 1.25, None, -3.5, 100.0]
        self.assertEqual(snapshot.unpack(snapshot.pack_int16(vals, 0.05)), [0.0, 1.25, None, -3.5, 100.0])
        with self.assertRaises(snapshot.SnapshotError):
            snapshot.pack_int16([1e9], 0.01)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "a.json.gz"
            h1 = snapshot.write(procedural_snapshot(), p)
            h2 = snapshot.write(procedural_snapshot(), Path(d) / "b.json.gz")
            self.assertEqual(h1, h2)  # deterministic gzip bytes
            self.assertEqual(snapshot.validate(snapshot.read(p)), [])
            p.write_bytes(p.read_bytes()[:500])
            with self.assertRaises(snapshot.SnapshotError):
                snapshot.read(p)
            q = Path(d) / "c.json.gz"
            q.write_bytes(gzip.compress(b"{not json", mtime=0))
            with self.assertRaises(snapshot.SnapshotError):
                snapshot.read(q)


class TestClock(unittest.TestCase):
    def test_utc_seconds(self):
        self.assertEqual(from_seconds(to_seconds(START)), START)
        with self.assertRaises(ValueError):
            to_seconds(dt.datetime(2028, 1, 1))

    def test_leap_day_analogue(self):
        feb29 = dt.datetime(2028, 2, 29, 12, tzinfo=UTC)
        self.assertEqual(analogue_source_time(feb29, 2025), dt.datetime(2025, 2, 28, 12, tzinfo=UTC))
        self.assertEqual(analogue_source_time(feb29, 2024), dt.datetime(2024, 2, 29, 12, tzinfo=UTC))
        off = analogue_offset(dt.datetime(2028, 9, 14, 6, tzinfo=UTC), 2025)
        self.assertEqual(from_seconds(to_seconds(START) - off), dt.datetime(2025, 9, 14, 6, tzinfo=UTC))

    def test_interpolation_weight_and_stale(self):
        st = state()
        s = st.sample(t0() + 3 * 3600, -50, 10)
        self.assertEqual((s.frame_before, s.frame_after, s.weight, s.stale), (0, 1, Fraction(1, 2), False))
        before = st.sample(t0() - 60, -50, 10)
        self.assertTrue(before.stale)
        self.assertEqual(before.values, st.sample(t0(), -50, 10).values)
        after = st.sample(t0() + 100 * 3600, -50, 10)
        self.assertTrue(after.stale)
        a, b = st.sample(t0(), -50, 10).values, st.sample(t0() + 6 * 3600, -50, 10).values
        mid = s.values
        for k in ("msl_pressure_hpa", "wave_hs_m"):
            self.assertAlmostEqual(mid[k], (a[k] + b[k]) / 2, places=3)

    def test_replay_fast_forward_reload_determinism(self):
        times = [t0() + k * 600 for k in range(0, 72 * 6, 7)]
        pts = [(-54, -49), (60, -30), (-65, 179.9), (-65, -179.9), (26.5, 56.3)]
        run1 = [state().sample(t, *p) for t in times for p in pts]
        clock = MnoEnvClock(t0())
        run2 = []
        st = MnoEnvState(procedural.generate("test-seed", START, hours=72))  # fresh process-equivalent
        for t in times:
            clock.advance(t - clock.campaign_seconds)  # fast-forward in uneven jumps
            run2 += [st.sample(clock.campaign_seconds, *p) for p in pts]
        self.assertEqual(digest_samples(run1), digest_samples(run2))
        other = MnoEnvState(procedural.generate("other-seed", START, hours=72))
        self.assertNotEqual(digest_samples(run1), digest_samples([other.sample(t, *p) for t in times for p in pts]))

    def test_clock_rules(self):
        c = MnoEnvClock(1000)
        self.assertEqual(c.preview(3600), 4600)
        self.assertEqual(c.campaign_seconds, 1000)  # scrubbing never advances the campaign
        with self.assertRaises(ValueError):
            c.preview(-1)
        with self.assertRaises(ValueError):
            c.advance(-5)
        c.paused = True
        c.advance(500)
        self.assertEqual(c.campaign_seconds, 1000)
        c.set(200, "load save B")
        self.assertEqual(c.history, [(1000, 200, "load save B")])

    def test_antimeridian_sampling_continuous(self):
        st = state()
        a = st.sample(t0(), -60, 179.99).values
        b = st.sample(t0(), -60, -179.99).values
        for k in a:
            self.assertAlmostEqual(a[k], b[k], delta=0.05 * (abs(a[k]) + 1), msg=k)

    def test_empty_or_invalid_grid_is_refused_by_validator(self):
        s = copy.deepcopy(procedural_snapshot())
        s["times"] = []
        self.assertTrue(snapshot.validate(s))


if __name__ == "__main__":
    unittest.main()
