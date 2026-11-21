using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;
using Sest.RuntimeFixes;

// Battle sea ice (runtime/SeaIceModel.cs, SeaIceRules.cs, SeaIceBattle.cs,
// SeaIceSheet.cs). Args: flat references, candidate runtime.
// 1 the C# model against seaice.py's own values (SeaIceGolden.g.cs, written by
//   tools/make_sea_ice_data.py from the weather branch), the review's points,
//   hemisphere seasons and leap-year rows;
// 2 the 0.05-degree tile cache; 3 the ice.py access table and the speed-cap
//   state machine (no hull is ever trapped: equal tile values, a real track
//   into and back out of the pack); 4 the submarine hold (DepthKeeping's
//   shallow-water target, the rise ceiling, orders given back on release,
//   the snorkelling state); 5 the lead field, floe placement, the sheet
//   mesher, its chunk layout, the double-buffered refill and the sheet height;
// 6 every Sea Power 0.9.3 member the runtime binds, with the IL facts the
//   design rests on (checked with Cecil, no game launch);
// 7 the candidate runtime: patch parameters that name game fields, and the
//   install order (before CumulativeCombatCosts' early return).
static class SeaIceTests
{
    static int checks;
    static void Check(bool ok, string why) { checks++; if (!ok) throw new Exception("FAILED: " + why); }
    static string F(double v) => v.ToString("0.000", CultureInfo.InvariantCulture);

    static int Main(string[] args)
    {
        try
        {
            Model();
            Cache();
            Speed();
            Track();
            Submarine();
            Snorkel();
            Field();
            Mesher();
            Sheet();
            if (args.Length >= 1) Bindings(args[0]);
            if (args.Length >= 2) Runtime(args[1]);
            Console.WriteLine("sea ice: " + checks + " checks passed");
            return 0;
        }
        catch (Exception e) { Console.WriteLine(e.Message); Console.WriteLine(e.StackTrace); return 1; }
    }

    static DateTime Noon(double y, double m, double d) => new DateTime((int)y, (int)m, (int)d, 12, 0, 0, DateTimeKind.Utc);

    static void Model()
    {
        var g = SeaIceGolden.Points;
        double worst = 0;
        for (int i = 0; i < g.Length; i += 6)
        {
            double c = SeaIceModel.Concentration(g[i + 3], g[i + 4], Noon(g[i], g[i + 1], g[i + 2]));
            worst = Math.Max(worst, Math.Abs(c - g[i + 5]));
        }
        Check(worst < 1e-9, "C# model equals seaice.ice_at at " + g.Length / 6 + " golden points (worst " + worst + ")");
        Console.WriteLine("model: " + g.Length / 6 + " golden points match seaice.py, worst difference " + worst.ToString("E1", CultureInfo.InvariantCulture) + " pp");
        var r = SeaIceGolden.Review;
        for (int i = 0; i < r.Length; i += 6)
        {
            double c = SeaIceModel.Concentration(r[i + 3], r[i + 4], Noon(r[i], r[i + 1], r[i + 2]));
            Check(Math.Abs(c - r[i + 5]) < 1e-9, "review point " + r[i + 3] + "," + r[i + 4]);
            Console.WriteLine("  " + (int)r[i] + "-" + ((int)r[i + 1]).ToString("00") + "-" + ((int)r[i + 2]).ToString("00") + " " + r[i + 3] + ", " + r[i + 4] + ": " + F(c) + " %");
        }
        var mar10 = new DateTime(2029, 3, 10, 12, 0, 0, DateTimeKind.Utc);
        Check(Math.Abs(SeaIceModel.Concentration(72, 36, mar10) - 18.7) < 0.05, "10 March 72N 36E 18.7 % (review)");
        Check(Math.Abs(SeaIceModel.Concentration(74, 36, mar10) - 62.3) < 0.05, "10 March 74N 36E 62.3 % (review)");
        Check(SeaIceModel.Concentration(67, 6, mar10) < 0.01, "Norwegian Sea open");
        // hemisphere seasons
        Check(SeaIceModel.Concentration(75, 36, Noon(2029, 3, 15)) > SeaIceModel.Concentration(75, 36, Noon(2029, 9, 15)) + 40, "Barents: March pack, September open");
        Check(SeaIceModel.Concentration(-62, -40, Noon(2029, 9, 15)) > SeaIceModel.Concentration(-62, -40, Noon(2029, 2, 20)) + 40, "Weddell: September pack, February open");
        Check(SeaIceModel.Concentration(-75, 0, Noon(2029, 3, 10)) > 0 && SeaIceModel.Concentration(75, 0, Noon(2029, 3, 10)) > 0, "both hemispheres");
        Check(SeaIceModel.Concentration(39.9, 120.5, Noon(2029, 1, 15)) == 0, "no ice below 40 degrees");
        Check(SeaIceModel.Concentration(89.9, 0, Noon(2029, 9, 15)) > 90, "central Arctic keeps its pack at the minimum (NORTH_EDGE_CAP)");
        double max = 0;
        for (double lat = 40; lat <= 90; lat += 0.5) max = Math.Max(max, SeaIceModel.Concentration(lat, 0, Noon(2029, 3, 1)));
        Check(max < SeaIceModel.MaxPercent + 1e-9, "never above 98 %");
        // leap and common rows: indexed by (month, day), not day of year
        Check(SeaIceData.Common.Length == 365 * 3 && SeaIceData.Leap.Length == 366 * 3, "731 rows");
        var feb29 = SeaIceModel.EdgesOn(new DateTime(2028, 2, 29));
        Check(feb29.North == SeaIceData.Leap[59 * 3], "29 February has its own row");
        Check(SeaIceModel.EdgesOn(new DateTime(2028, 3, 10)).North == SeaIceData.Leap[69 * 3] && SeaIceModel.EdgesOn(new DateTime(2029, 3, 10)).North == SeaIceData.Common[68 * 3], "10 March in a leap and a common year");
        Check(SeaIceModel.EdgesOn(new DateTime(2031, 3, 10, 23, 59, 0)).North == SeaIceData.Common[68 * 3], "any time of the date uses that date's noon row");
        Check(SeaIceModel.WrapLon(180) == -180 && SeaIceModel.WrapLon(-181) == 179 && SeaIceModel.LonDelta(-175, 179) == 6, "Python wrap_lon");
        Check(SeaIceData.Units.Length == 0 && IceRules.CapabilityOf("usn_ffg-7") == 0, "ice-capability.json units empty: every ship 'none'");
    }

    static void Cache()
    {
        var c = new SeaIceTileCache();
        var d = Noon(2029, 3, 10);
        double a = c.Percent(74.01, 36.01, d), b = c.Percent(74.04, 36.04, d);
        Check(a == b && c.Hits == 1 && c.Misses == 1, "one model call per 0.05-degree tile");
        SeaIceTileCache.TileCentre(SeaIceTileCache.Key(74.01, 36.01), out double tl, out double tn);
        Check(Math.Abs(tl - 74.025) < 1e-9 && Math.Abs(tn - 36.025) < 1e-9 && Math.Abs(a - SeaIceModel.Concentration(74.025, 36.025, d)) < 1e-12, "tile value is the tile centre's");
        Check(SeaIceTileCache.Key(70, 180) == SeaIceTileCache.Key(70, -180), "180E and 180W are one tile");
        c.Percent(74.01, 36.01, Noon(2029, 3, 11));
        Check(c.Clears == 2 && c.Count == 1, "a new date empties the cache");
        Check(c.Percent(10, 10, d) == 0 && c.Percent(double.NaN, 0, d) == 0, "tropics and NaN are open water without a model call");
        for (int i = 0; i < SeaIceTileCache.Capacity + 10; i++) c.Percent(60 + (i / 1000) * 0.05, -60 + (i % 1000) * 0.05, d);
        Check(c.Count <= SeaIceTileCache.Capacity, "bounded");
    }

    static void Speed()
    {
        int none = 0, strengthened = IceRules.CapabilityIndex("ice_strengthened"), polar = IceRules.CapabilityIndex("polar_class"), breaker = IceRules.CapabilityIndex("icebreaker");
        Check(IceRules.Access(9.9, none) == IceAccess.Open && IceRules.Access(10, none) == IceAccess.Caution && IceRules.Access(30, none) == IceAccess.Restricted && IceRules.Access(60, none) == IceAccess.Blocked, "ice.py thresholds, class none");
        Check(IceRules.Access(59, strengthened) == IceAccess.Caution && IceRules.Access(80, strengthened) == IceAccess.Blocked, "ice_strengthened");
        Check(IceRules.Access(98, polar) == IceAccess.Restricted && IceRules.Access(98, breaker) == IceAccess.Caution, "polar_class and icebreaker are never blocked by the model's 98 %");
        Check(IceRules.Access(double.NaN, none) == IceAccess.Caution, "unknown ice is caution (ice.py:44)");
        Check(IceRules.SpeedFactor.SequenceEqual(new[] { 1.0, 0.7, 0.4, 0.0 }), "ice.py ACCESS_SPEED");
        var s = new IceSpeedState();
        Check(s.Cap(20, 30, 5, 5, none) == 20, "open: unchanged");
        Check(Math.Abs(s.Cap(28, 30, 20, 20, none) - 21) < 1e-5, "caution: 0.7 x flank");
        Check(Math.Abs(s.Cap(28, 30, 45, 45, none) - 12) < 1e-5, "restricted: 0.4 x flank");
        Check(Math.Abs(s.Cap(28, 30, 70, 75, none) - 3) < 1e-5 && s.State == IceAccess.Blocked && s.SteerageOnly && !s.Escaping, "blocked at >= 60 %: ahead into heavier ice only steerage way (0.1 x flank), never dead in the water");
        Check(Math.Abs(s.Cap(-10, 30, 70, 55, none) + 10) < 1e-5 && s.Escaping, "backing out toward lighter ice: allowed");
        Check(Math.Abs(s.Cap(-20, 30, 70, 55, none) + 12) < 1e-5, "backing out at restricted speed (0.4)");
        Check(Math.Abs(s.Cap(-20, 30, 70, 90, none) + 12) < 1e-5 && s.Escaping, "astern always at 0.4 when blocked, whatever the sample astern says");
        Check(Math.Abs(s.Cap(-20, 30, 70, double.NaN, none) + 12) < 1e-5, "astern at 0.4 with no sample");
        Check(Math.Abs(s.Cap(20, 30, 70, 80, none) - 3) < 1e-5 && s.SteerageOnly, "ahead into heavier ice: steerage way");
        Check(Math.Abs(s.Cap(20, 30, 70, 64, none) - 12) < 1e-5 && s.Escaping, "ahead toward lighter ice: 0.4");
        // equal ice (the tile cache gives two points in one tile the same value) counts as escapable
        Check(Math.Abs(s.Cap(28, 30, 75.05, 75.05, none) - 12) < 1e-5 && s.Escaping, "equal ice ahead: 0.4, not 0");
        Check(Math.Abs(s.Cap(28, 30, 70, 70 + IceSpeedState.EscapeEpsilon * 0.9, none) - 12) < 1e-5 && Math.Abs(s.Cap(28, 30, 70, 70.2, none) - 3) < 1e-5, "within EscapeEpsilon equal, beyond it heavier");
        Check(Math.Abs(s.Cap(28, 30, 70, 71, none, 71.5) - 12) < 1e-5, "the comparison uses the unquantised reference when given");
        // quantised tile values: here, 0.5 nm ahead and 0.5 nm astern in one tile (the review's 74.625N 36E)
        var cache = new SeaIceTileCache();
        var d = Noon(2029, 3, 10);
        double here = cache.Percent(74.625, 36, d), ahead = cache.Percent(74.625 + 0.5 / 60, 36, d), astern = cache.Percent(74.625 - 0.5 / 60, 36, d);
        Check(here == ahead && here == astern && IceRules.Access(here, none) == IceAccess.Blocked, "the tile cache gives one value 0.5 nm ahead and astern (" + F(here) + " %)");
        var q = new IceSpeedState();
        Check(Math.Abs(q.Cap(30, 30, here, ahead, none) - 12) < 1e-5 && Math.Abs(q.Cap(-30, 30, here, astern, none) + 12) < 1e-5 && q.State == IceAccess.Blocked, "same quantised value ahead and astern: the hull still moves at 0.4 either way");
        Check(double.IsNaN(IceSpeedState.Lightest(new double[0])) && IceSpeedState.Lightest(new[] { 70, double.NaN, 62.5, 66 }) == 62.5, "lightest sample, NaN ignored");
        Check(IceSpeedState.AheadNm.Max() >= 2 * SeaIceTileCache.TileDegrees * 60 && IceSpeedState.AheadNm.Min() >= 1, "direction-of-travel samples reach two tiles (" + string.Join(", ", IceSpeedState.AheadNm) + " nm)");
        // hysteresis: from blocked, 59.5 % stays blocked; 58.9 % releases to restricted
        Check(Math.Abs(s.Cap(20, 30, 59.5, 70, none) - 3) < 1e-5 && s.State == IceAccess.Blocked, "hysteresis keeps the state within 1 pp");
        s.Cap(20, 30, 58.9, 58.9, none);
        Check(s.State == IceAccess.Restricted, "released 1 pp below the threshold");
        Check(new IceSpeedState().Cap(15, 0, 70, 70, none) == 15, "no telegraph table: native speed");
        Check(new IceSpeedState().Cap(15, 30, 70, 70, polar) == 15, "polar class keeps 12+ kn at 70 % (caution 0.7 x 30 = 21)");
    }

    // A class-none frigate on 36E on 10 March 2029, the way SpeedPostfix drives Cap: state from the tile
    // cache, the direction of travel from the raw model 1, 3 and 6 nm ahead (astern when backing).
    // Full ahead north into the pack, then full astern: it is never dead in the water and backs out.
    static void Track()
    {
        var cache = new SeaIceTileCache();
        var d = Noon(2029, 3, 10);
        var s = new IceSpeedState();
        double lat = 73.5, flank = 30, blockedAt = double.NaN, minAbs = double.MaxValue;
        int none = 0;
        Func<double, int, double> step = (wanted, seconds) =>
        {
            double v = 0;
            for (int t = 0; t < seconds; t += 10)
            {
                double here = cache.Percent(lat, 36, d), raw = SeaIceModel.Concentration(lat, 36, d);
                int sign = wanted < 0 ? -1 : 1;
                double lightest = IceSpeedState.Lightest(IceSpeedState.AheadNm.Select(nm => SeaIceModel.Concentration(lat + sign * nm / 60.0, 36, d)));
                v = s.Cap((float)wanted, (float)flank, here, lightest, none, raw);
                if (s.State == IceAccess.Blocked && double.IsNaN(blockedAt)) blockedAt = lat;
                minAbs = Math.Min(minAbs, Math.Abs(v));
                lat += v * 10 / 3600.0 / 60.0; // knots -> nm -> degrees of latitude
            }
            return v;
        };
        double vAhead = step(flank, 6 * 3600);
        Check(!double.IsNaN(blockedAt) && s.State == IceAccess.Blocked && Math.Abs(vAhead - 3) < 1e-4, "ahead into the pack: blocked from " + F(blockedAt) + "N, steerage way 3 kn at " + F(lat) + "N (ice " + F(cache.Percent(lat, 36, d)) + " %)");
        double deepest = lat;
        double vAstern = step(-flank, 3 * 3600);
        Check(minAbs > 0, "never dead in the water (slowest " + F(minAbs) + " kn)");
        Check(lat < blockedAt - 0.05 && s.State != IceAccess.Blocked, "full astern backs out: " + F(deepest) + "N -> " + F(lat) + "N, state " + s.State + ", last " + F(vAstern) + " kn");
        Console.WriteLine("  track 36E, 10 March 2029: blocked from " + F(blockedAt) + "N, steerage way to " + F(deepest) + "N, full astern back to " + F(lat) + "N (" + s.State + ", " + F(vAstern) + " kn), slowest " + F(minAbs) + " kn");
    }

    static void Submarine()
    {
        Check(Math.Abs(SubIceRule.MetersToUnity(30) - 0.44643) < 1e-4, "30 m = 0.446 Unity units (220.472656 ft per unit)");
        float keel = SubIceRule.MetersToUnity(30);
        Check(SubIceRule.Holds(70, false, 60) && !SubIceRule.Holds(70, true, 60) && !SubIceRule.Holds(59.9, false, 60) && !SubIceRule.Holds(double.NaN, false, 60), "held under heavy ice unless in a lead");
        Check(SubIceRule.ClampDesiredAltitude(0f, keel) == -keel && SubIceRule.ClampDesiredAltitude(-0.0f, keel) == -keel, "Surface order (DesiredAltitude -0) held at the keel");
        Check(SubIceRule.ClampDesiredAltitude(-0.08f, keel) == -keel, "periscope depth (about 55 ft) held");
        Check(SubIceRule.ClampDesiredAltitude(-1.5f, keel) == -1.5f, "deeper orders kept");
        Check(SubIceRule.ClampOrderedDepth(0f, keel) == keel && SubIceRule.ClampOrderedDepth(2f, keel) == 2f, "setDepth argument clamped");
        // DepthKeeping's shallow-water target while held
        Check(SubIceRule.ClampTargetAltitude(-1.0f, keel, -1.0f) == -1.0f, "a target deeper than the keel is kept");
        Check(SubIceRule.ClampTargetAltitude(0f, keel, -0.6f) == -keel, "the shallow-water surface target (0) becomes the keel when the boat is deeper");
        Check(SubIceRule.ClampTargetAltitude(0f, keel, -0.2f) == -0.2f, "bottom forbids the keel and the boat is shallower: it holds its depth, never rises");
        Check(SubIceRule.ClampTargetAltitude(-0.3f, keel, -0.2f) == -0.3f, "bottom-clearance target deeper than the boat: it may go down to it");
        for (float t = -0.44f; t <= 0.001f; t += 0.01f)
            foreach (float y in new[] { -2f, -0.6f, -keel, -0.3f, -0.1f, -0.01f })
                Check(SubIceRule.ClampTargetAltitude(t, keel, y) <= Math.Max(y, -keel) + 1e-6f, "held target never above max(depth, keel) (" + t + ", " + y + ")");
        // the ceiling: only ratchets down, never below the keel
        float ceil = SubIceRule.Ceiling(float.NaN, -0.08f, keel);
        Check(ceil == -0.08f, "a boat entering the pack at periscope depth: ceiling at its depth");
        ceil = SubIceRule.Ceiling(ceil, -0.2f, keel);
        Check(ceil == -0.2f && SubIceRule.Ceiling(ceil, -0.1f, keel) == -0.2f, "the ceiling ratchets down as the boat goes deeper, never up");
        Check(SubIceRule.Ceiling(ceil, -0.9f, keel) == -keel && SubIceRule.Ceiling(float.NaN, -0.9f, keel) == -keel, "deeper than the keel the ceiling is the keel");
        // manual ballast blow (key 0xa6: a negative depth-change rate) against the ceiling backstop
        float yb = -0.6f, c2 = float.NaN, rate = -0.01f;
        for (int i = 0; i < 2000; i++) { c2 = SubIceRule.Ceiling(c2, yb, keel); yb -= rate * 0.02f * 10; if (yb > c2) { yb = c2; if (rate < 0) rate = 0; } }
        Check(yb == -keel && rate == 0, "a manual blow from 200 ft stops at the keel with the upward rate zeroed");
        // orders kept across the hold
        bool has = false; float order = 0;
        SubIceRule.RememberOrderedDepth(0.08f, keel, ref has, ref order);
        Check(has && order == -0.08f, "periscope-depth order remembered");
        SubIceRule.RememberOrderedDepth(-5f, keel, ref has, ref order);
        Check(has && order == 0f, "an order above the surface is remembered as the surface");
        SubIceRule.RememberOrderedDepth(1.2f, keel, ref has, ref order);
        Check(!has, "a legal deeper order replaces the remembered one");
        SubIceRule.RememberDesired(-0.05f, keel, ref has, ref order);
        Check(has && order == -0.05f, "a shallow DesiredAltitude written another way is remembered");
        SubIceRule.RememberDesired(-keel, keel, ref has, ref order);
        Check(has && order == -0.05f, "the clamp value itself changes nothing");
        Check(SubIceRule.RestoreOnRelease(-keel, keel, true, -0.08f, out float back) && back == -0.08f, "released: the order is given back");
        Check(!SubIceRule.RestoreOnRelease(-1.2f, keel, true, -0.08f, out back) && back == -1.2f, "a new order given meanwhile is kept");
        Check(!SubIceRule.RestoreOnRelease(-keel, keel, false, 0, out back) && back == -keel, "nothing remembered: unchanged");
    }

    // SubmarineStates.Snorkelling with the hold: onEnter orders periscope depth (clamped and remembered);
    // onFixedUpdate raises the snorkel once at depth and latches _depthReached. Modelled with the game's
    // own conditions (OnAltitude = |y - DesiredAltitude| < threshold; the raise fails while held).
    static void Snorkel()
    {
        float keel = SubIceRule.MetersToUnity(30), pd = 0.08f;
        foreach (bool withFix in new[] { false, true })
        {
            float y = -0.6f, desired = 0;
            bool has = false, suppressed = false, depthReached = false, snorkelUp = false;
            float order = 0;
            int refused = 0;
            // onEnter: setPresetDepth(1) -> setDepth(pd), clamped while held
            SubIceRule.RememberOrderedDepth(pd, keel, ref has, ref order);
            desired = -SubIceRule.ClampOrderedDepth(pd, keel);
            for (int t = 0; t < 4000; t++)
            {
                bool held = t < 2000; // under the pack, then open water
                if (!held && has && withFix) { if (SubIceRule.RestoreOnRelease(desired, keel, has, order, out float back)) desired = back; has = false; }
                if (withFix) depthReached = SubIceRule.SnorkelDepthReached(held, depthReached, ref suppressed);
                bool onAltitude = Math.Abs(y - desired) < 0.005f;
                if (!depthReached && onAltitude) { if (held) refused++; else snorkelUp = true; depthReached = true; }
                y += Math.Sign(desired - y) * Math.Min(Math.Abs(desired - y), 0.002f);
            }
            if (!withFix) Check(!snorkelUp && refused == 1 && Math.Abs(y + keel) < 1e-3, "without the fix the state latches with the snorkel down at the keel (the review's case)");
            else Check(snorkelUp && refused == 0 && Math.Abs(y + pd) < 1e-3, "with the fix: no refused raise under the ice, periscope depth given back and the snorkel raised in open water");
        }
        bool s = false;
        Check(SubIceRule.SnorkelDepthReached(true, false, ref s) && s && !SubIceRule.SnorkelDepthReached(false, true, ref s) && !s && SubIceRule.SnorkelDepthReached(false, true, ref s), "held: reads reached; release: cleared once; then the state's own value");
    }

    static void Field()
    {
        uint seed = SeaIceField.SeedOf(20290310);
        foreach (double p in new[] { 0.15, 0.4, 0.6, 0.8, 0.95 })
        {
            int ice = 0, n = 0;
            for (int j = 0; j < 160; j++)
                for (int i = 0; i < 160; i++) { n++; if (SeaIceField.IsIce(100 + i * 0.137, -40 + j * 0.121, p, SeaIceField.SeedOf(20280105))) ice++; }
            double share = (double)ice / n;
            Check(Math.Abs(share - p) < 0.04, "ice share " + F(share) + " for fraction " + p);
        }
        Check(!SeaIceField.IsIce(1, 1, 0, seed) && SeaIceField.IsIce(1, 1, 1, seed), "0 % open, 100 % ice");
        Check(SeaIceField.IsIce(3.3, 4.4, 0.5, seed) == SeaIceField.IsIce(3.3, 4.4, 0.5, seed), "deterministic");
        int diff = 0;
        for (int i = 0; i < 400; i++) if (SeaIceField.IsIce(i * 0.21, i * 0.13, 0.5, seed) != SeaIceField.IsIce(i * 0.21, i * 0.13, 0.5, SeaIceField.SeedOf(20290311))) diff++;
        Check(diff > 100, "another date, another pattern (" + diff + "/400)");
        int leads = 0;
        for (int i = 0; i < 2000; i++) if (SeaIceField.FootprintOpen(i * 0.083, i * 0.051, 0.7, seed, 45)) leads++;
        Check(leads > 40 && leads < 600, "70 % ice still has submarine-size leads (" + leads + "/2000)");
        Check(SeaIceField.DrawnFraction(14.9, 15) == 0 && SeaIceField.DrawnFraction(15, 15) == 0.15 && SeaIceField.DrawnFraction(98, 15) == 0.98, "drawn only from the 15 % edge");
        // the frame
        var frame = new IceFrame(74, 36);
        frame.ToKm(74.5, 37, out double e, out double n2);
        frame.ToGeo(e, n2, out double lat, out double lon);
        Check(Math.Abs(lat - 74.5) < 1e-9 && Math.Abs(lon - 37) < 1e-9 && Math.Abs(n2 - 55.66) < 0.01 && Math.Abs(e - 111.32 * Math.Cos(74 * Math.PI / 180)) < 1e-6, "frame round trip");
        var w = new IceFrame(70, 180);
        w.ToKm(70, -179, out double we, out _);
        Check(Math.Abs(we - 111.32 * Math.Cos(70 * Math.PI / 180)) < 1e-6, "frame across 180");
        Check(IceFrame.Around(73.6, 35.4).Lat0 == 74 && IceFrame.Around(73.6, 35.4).Lon0 == 35, "battle origin rounded");
        // floe fallback placement
        Func<double, double, double> half = (a, b) => 0.5, full = (a, b) => 0.95, none = (a, b) => 0.0;
        var s1 = FloePlacement.Slots(0, 0, 3, 0.12, half, seed, 100000);
        var s2 = FloePlacement.Slots(0, 0, 3, 0.12, full, seed, 100000);
        Check(FloePlacement.Slots(0, 0, 3, 0.12, none, seed, 100000).Count == 0, "no floes in open water");
        double cells = Math.PI * 9 / (0.12 * 0.12);
        Check(Math.Abs(s1.Count / cells - 0.5) < 0.05 && Math.Abs(s2.Count / cells - 0.95) < 0.05, "floe density follows concentration (" + s1.Count + ", " + s2.Count + " of " + (int)cells + ")");
        Check(s1.All(x => x.East * x.East + x.North * x.North <= 9.0001), "inside the radius");
        var s3 = FloePlacement.Slots(0.05, 0, 3, 0.12, half, seed, 100000);
        int common = s1.Select(x => x.Id).Intersect(s3.Select(x => x.Id)).Count();
        Check(common > s1.Count * 0.9 && s1.Where(x => s3.Any(y => y.Id == x.Id)).All(x => s3.First(y => y.Id == x.Id).East == x.East), "world-anchored: a 50 m pan keeps the floes in place");
        var capped = FloePlacement.Slots(0, 0, 3, 0.12, full, seed, 300);
        double nth = s2.Select(x => x.East * x.East + x.North * x.North).OrderBy(x => x).ElementAt(299);
        Check(capped.Count == 300 && capped.Max(x => x.East * x.East + x.North * x.North) <= nth + 1e-12, "the cap keeps the nearest floes");
    }

    static void Mesher()
    {
        uint seed = SeaIceField.SeedOf(20290310);
        var spec = new IceChunkSpec { CentreEastKm = 0.5, CentreNorthKm = 0.5, SizeKm = 1, Cells = 32, Underside = true, FreeboardM = 0.5, DraftM = 2, RidgeM = 1.2, EdgePercent = 15, Seed = seed };
        var open = IceMesher.Build(spec, (e, n) => 10);
        Check(open.TriangleCount == 0 && open.IceCells == 0, "below the edge: nothing drawn");
        var heavy = IceMesher.Build(spec, (e, n) => 95);
        var mid = IceMesher.Build(spec, (e, n) => 50);
        // over 16 chunks (a single 1 km chunk is about two lead cells across, so its own share varies)
        int heavyCells = 0, openCells95 = 0;
        for (int k = 0; k < 16; k++)
        {
            var c = spec; c.CentreEastKm = 0.5 + (k % 4) * 1.0; c.CentreNorthKm = 0.5 + (k / 4) * 1.0;
            var m = IceMesher.Build(c, (e, n) => 95);
            heavyCells += m.IceCells; openCells95 += m.OpenCells;
        }
        Check(openCells95 < 16 * 1024 * 0.08 && heavy.TriangleCount > 3000, "95 %: nearly solid (" + openCells95 + " open cells of " + 16 * 1024 + ", " + heavy.TriangleCount + " triangles in one chunk)");
        Check(mid.IceCells > 300 && mid.IceCells < heavy.IceCells && mid.OpenCells > 50, "50 %: leads and floes (" + mid.IceCells + " ice cells)");
        float minX = float.MaxValue, maxX = float.MinValue, minY = float.MaxValue, maxY = float.MinValue;
        for (int i = 0; i < mid.Vertices.Length; i += 3) { minX = Math.Min(minX, mid.Vertices[i]); maxX = Math.Max(maxX, mid.Vertices[i]); minY = Math.Min(minY, mid.Vertices[i + 1]); maxY = Math.Max(maxY, mid.Vertices[i + 1]); }
        Check(minX >= -500.001 && maxX <= 500.001 && Math.Abs(minY + 2) < 1e-4 && maxY <= 0.5 + 1.2 + 1e-4, "vertices inside the chunk, underside at -2 m, top at freeboard + ridge");
        Check(mid.Triangles.All(t => t >= 0 && t < mid.Vertices.Length / 3) && mid.Vertices.Length / 3 < 65000, "valid 16-bit mesh");
        var topOnly = IceMesher.Build(new IceChunkSpec { CentreEastKm = 8, CentreNorthKm = 8, SizeKm = 16, Cells = 32, Underside = false, FreeboardM = 0.5, DraftM = 2, RidgeM = 0.6, EdgePercent = 15, Seed = seed }, (e, n) => 95);
        Check(topOnly.Vertices.Where((v, i) => i % 3 == 1).All(y => y >= 0.5f - 1e-4), "far chunks: top only");
        // front faces: top triangles clockwise seen from above (Unity), i.e. their normal points up
        int up = 0, down = 0;
        for (int t = 0; t < heavy.Triangles.Length; t += 3)
        {
            int a = heavy.Triangles[t] * 3, b = heavy.Triangles[t + 1] * 3, c = heavy.Triangles[t + 2] * 3;
            double ux = heavy.Vertices[b] - heavy.Vertices[a], uz = heavy.Vertices[b + 2] - heavy.Vertices[a + 2], vx = heavy.Vertices[c] - heavy.Vertices[a], vz = heavy.Vertices[c + 2] - heavy.Vertices[a + 2];
            double ny = uz * vx - ux * vz; // y of (b-a) x (c-a) in a left-handed frame's clockwise test
            if (Math.Abs(ny) < 1e-9) continue;
            if (ny > 0) up++; else down++;
        }
        Check(up > 1000 && down > 1000 && Math.Abs(up - down) < up * 0.1, "top and underside faces both present (" + up + " up, " + down + " down)");
        // gradient across a chunk: the 5 x 5 lattice follows the model
        var edge = IceMesher.Build(spec, (e, n) => e < 0.5 ? 5 : 90);
        Check(edge.IceCells > 300 && edge.OpenCells > 400, "the ice edge runs through the chunk");
        // chunk layout: nested levels, every point covered exactly once out to 48 km
        double[] sizes = { 1, 4, 16 };
        foreach (var cam in new[] { new[] { 0.3, 0.2 }, new[] { 7.9, -3.1 }, new[] { -41.0, 29.5 } })
        {
            var keys = IceMesher.Layout(cam[0], cam[1], sizes, new[] { 2, 2 }, 6);
            Check(keys.Count(k => k.Level == 0) == 64 && keys.Count(k => k.Level == 1) == 60 && keys.Count(k => k.Level == 2) == 32, "156 chunks: 64 x 1 km, 60 x 4 km, 32 x 16 km");
            var rnd = new Random(7);
            for (int t = 0; t < 3000; t++)
            {
                double e = cam[0] + (rnd.NextDouble() - 0.5) * 78, n = cam[1] + (rnd.NextDouble() - 0.5) * 78;
                int covered = keys.Count(k => e >= k.I * sizes[k.Level] && e < (k.I + 1) * sizes[k.Level] && n >= k.J * sizes[k.Level] && n < (k.J + 1) * sizes[k.Level]);
                Check(covered == 1, "point covered once (" + covered + ") at " + F(e) + "," + F(n));
                double d = Math.Max(Math.Abs(e - cam[0]), Math.Abs(n - cam[1]));
                var k0 = keys.First(k => e >= k.I * sizes[k.Level] && e < (k.I + 1) * sizes[k.Level] && n >= k.J * sizes[k.Level] && n < (k.J + 1) * sizes[k.Level]);
                if (d < 2) Check(k0.Level == 0, "the finest level within 2 km of the camera");
            }
        }
    }

    // The sheet's refill (double buffering, nearest first, time budget) and its height.
    static void Sheet()
    {
        double[] sizes = { 1, 4, 16 };
        var a = IceMesher.Layout(0, 0, sizes, new[] { 2, 2 }, 6);
        var b = IceMesher.Layout(3, 0, sizes, new[] { 2, 2 }, 6);
        var far = IceMesher.Layout(200, 0, sizes, new[] { 2, 2 }, 6);
        // nearest first after a camera jump
        var order = IceMesher.NearestFirst(IceMesher.Layout(30, 0, sizes, new[] { 2, 2 }, 6), 30.2, 0.3, sizes);
        Check(order[0].Level == 0 && 30.2 >= order[0].I && 30.2 < order[0].I + 1 && 0.3 >= order[0].J && 0.3 < order[0].J + 1, "after a jump the chunk under the camera is built first");
        for (int i = 1; i < order.Count; i++) Check(IceMesher.Dist(order[i - 1], 30.2, 0.3, sizes) <= IceMesher.Dist(order[i], 30.2, 0.3, sizes), "build queue sorted by distance");
        // overlaps
        var l1 = new IceMesher.ChunkKey { Level = 1, I = 0, J = 0 };
        Check(IceMesher.Overlaps(l1, new IceMesher.ChunkKey { Level = 0, I = 3, J = 3 }, sizes) && !IceMesher.Overlaps(l1, new IceMesher.ChunkKey { Level = 0, I = 4, J = 0 }, sizes) && !IceMesher.Overlaps(l1, new IceMesher.ChunkKey { Level = 1, I = 1, J = 0 }, sizes), "chunk overlap (edges do not count)");
        // double buffering: a stale chunk stays until every wanted chunk over it is ready
        var ready = new HashSet<IceMesher.ChunkKey>();
        Func<IceMesher.ChunkKey, bool> isReady = k => ready.Contains(k);
        var staleL1 = a.First(k => k.Level == 1 && !b.Contains(k) && b.Any(x => x.Level == 0 && IceMesher.Overlaps(k, x, sizes)));
        Check(!IceMesher.CanRetire(staleL1, b, isReady, sizes), "a superseded chunk stays drawn while its replacements build");
        var over = b.Where(x => IceMesher.Overlaps(staleL1, x, sizes)).ToList();
        foreach (var k in over.Take(over.Count - 1)) ready.Add(k);
        Check(!IceMesher.CanRetire(staleL1, b, isReady, sizes), "... until the last one is ready (" + over.Count + " replacements)");
        ready.Add(over.Last());
        Check(IceMesher.CanRetire(staleL1, b, isReady, sizes), "... then it goes");
        Check(a.All(k => IceMesher.CanRetire(k, far, x => false, sizes)), "after a 200 km jump the old chunks the layout no longer reaches go at once");
        // date change: same keys; the old chunk stays until the new one of the same key is ready
        ready.Clear();
        var k0 = a[0];
        Check(!IceMesher.CanRetire(k0, a, isReady, sizes), "date change: the old chunk stays until its rebuild is ready");
        foreach (var k in a) ready.Add(k);
        Check(IceMesher.CanRetire(k0, a, isReady, sizes), "date change: replaced once ready");
        // upload budget: refill of the whole 156-chunk layout in about a second, not 13 s
        Check(IceSheetRule.MayUpload(0, 50, 2) && IceSheetRule.MayUpload(2, 1.9, 2) && !IceSheetRule.MayUpload(1, 2.0, 2), "at least one upload per frame, then until the budget is spent");
        Check(IceSheetRule.Budget(156) == IceSheetRule.RefillBudgetMs && IceSheetRule.Budget(2) == IceSheetRule.UploadBudgetMs && IceSheetRule.RefillBudgetMs <= 3.0, "larger budget during a refill, at most 3 ms");
        int left = 156, frames = 0;
        while (left > 0) { frames++; double ms = 0; int u = 0; while (left > 0 && IceSheetRule.MayUpload(u, ms, IceSheetRule.Budget(left))) { ms += 1.0; u++; left--; } }
        Check(frames <= 60, "156 chunks at 1 ms each are uploaded in " + frames + " frames (the old cap: 6 per 0.5 s, about 13 s)");
        Console.WriteLine("  sheet refill: 156 chunks at 1 ms each in " + frames + " frames");
        // height: the underside always below the local sea surface, tops at or below a ship's waterline
        double draft = 2.0, free = 0.5;
        Check(Math.Abs(IceSheetRule.MaxLift(draft) - 1.0) < 1e-12 && Math.Abs(IceSheetRule.Lift(0.3, double.NaN, draft) - 0.15) < 1e-12 && IceSheetRule.Lift(5.0, double.NaN, draft) == 1.0 && IceSheetRule.Lift(14, 10, draft) == 1.0 && IceSheetRule.Lift(5, 0.5, draft) == 0.5, "lift: half Hs, capped at draft - 1 m (the override too)");
        foreach (double hs in new[] { 0, 0.05, 0.3, 0.875, 1.875, 3.25, 5.0, 7.5, 11.5, 14 })
            foreach (double over2 in new[] { double.NaN, 0, 0.5, 3, 10 })
                foreach (var sea in new[] { new[] { 0.0, 0.0 }, new[] { 0.4, -1.2 }, new[] { -0.8, -2.5 }, new[] { 1.5, 0.2 } })
                {
                    double lift = IceSheetRule.Lift(hs, over2, draft);
                    double y = IceSheetRule.ChunkY(sea[0], sea[1], lift, free, draft, double.NaN);
                    Check(y - draft <= sea[0] - IceSheetRule.UnderwaterMarginM + 1e-9 && y - draft <= sea[1] - IceSheetRule.UnderwaterMarginM + 1e-9, "underside at least 1 m below the sea surface (Hs " + hs + ", sea " + sea[0] + "/" + sea[1] + ")");
                    double ys = IceSheetRule.ChunkY(sea[0], sea[1], lift, free, draft, sea[0]);
                    Check(ys + free <= sea[0] + 1e-9, "ice top never above a nearby ship's waterline");
                }
        Check(IceSheetRule.ChunkY(0, 0, IceSheetRule.Lift(5.0, double.NaN, draft), free, draft, double.NaN) - draft == -1.0, "sea state 6 without Ceto: underside at -1 m (was +0.5 m)");
    }

    // ---- 6: Sea Power 0.9.3 bindings ----------------------------------------------------------

    static string Sig(MethodReference m) => m.ReturnType.FullName + "(" + string.Join(",", m.Parameters.Select(p => p.ParameterType.FullName)) + ")";
    static TypeDefinition T(ModuleDefinition m, string name) { var t = m.GetType(name); Check(t != null, "type " + name); return t; }
    static MethodDefinition M(TypeDefinition t, string name, string sig)
    {
        var found = t.Methods.Where(x => x.Name == name && Sig(x) == sig).ToList();
        Check(found.Count == 1, t.FullName + "::" + name + " " + sig + " (found: " + string.Join("; ", t.Methods.Where(x => x.Name == name).Select(Sig)) + ")");
        return found[0];
    }
    static FieldDefinition Fd(TypeDefinition t, string name, string type, bool isStatic = false)
    {
        var f = t.Fields.SingleOrDefault(x => x.Name == name);
        Check(f != null && f.FieldType.FullName == type && f.IsStatic == isStatic, t.FullName + "." + name + " : " + type + (f != null ? " (is " + f.FieldType.FullName + ")" : ""));
        return f;
    }
    static bool Calls(Instruction i, string owner, string name) => (i.OpCode.Code == Code.Call || i.OpCode.Code == Code.Callvirt) && i.Operand is MethodReference r && r.DeclaringType.GetElementType().FullName == owner && r.Name == name;
    static bool Field(Instruction i, Code op, string owner, string name) => i.OpCode.Code == op && i.Operand is FieldReference f && f.DeclaringType.FullName == owner && f.Name == name;
    static int Index(MethodDefinition m, Func<Instruction, bool> p, int from = 0)
    {
        var b = m.Body.Instructions;
        for (int i = from; i < b.Count; i++) if (p(b[i])) return i;
        return -1;
    }

    static void Bindings(string flat)
    {
        var resolver = new DefaultAssemblyResolver();
        resolver.AddSearchDirectory(flat);
        var game = ModuleDefinition.ReadModule(Path.Combine(flat, "Seapower-Scripts.dll"), new ReaderParameters { AssemblyResolver = resolver });
        const string G = "SeaPower.GeoPosition";
        var env = T(game, "SeaPower.Environment");
        var floe = M(env, "getFloeIce", "System.Single(" + G + ")");
        Check(floe.IsPublic && !floe.IsStatic, "getFloeIce public instance");
        var noise = M(env, "getOceanNoise", "System.Single(" + G + ")");
        Check(Index(noise, i => Calls(i, "SeaPower.Environment", "getFloeIce")) >= 0, "getOceanNoise adds getFloeIce");
        Check(Index(floe, i => Field(i, Code.Ldfld, "UnityEngine.Color32", "b")) >= 0, "native floe ice is the environment map's blue channel");
        M(env, "get_DateTime", "System.DateTime()");
        M(env, "get_SeaState", "System.Int32()");
        Fd(env, "_environmentMap", "UnityEngine.Color32[]");
        Fd(env, "_isEnvironmentMapInitialized", "System.Boolean");
        Check(T(game, "SeaPower.Singleton`1").Fields.Any(f => f.Name == "_instance" && f.IsStatic), "Singleton<T>._instance (read without auto-creating an Environment)");
        var geo = T(game, G);
        Fd(geo, "_latitude", "System.Double"); Fd(geo, "_longitude", "System.Double"); Fd(geo, "_height", "System.Double");
        M(geo, "GeoOffsetByDistanceOnHeading", G + "(System.Single,System.Single)");
        var utils = T(game, "SeaPower.Utils");
        Check(M(utils, "longLatToLocalV3", "UnityEngine.Vector3(" + G + ",UnityEngine.Vector2)").IsStatic, "Utils.longLatToLocalV3 (geo -> Unity, LCC or per-tile equirect)");
        Check(M(utils, "worldPositionFromUnityToLongLat", G + "(UnityEngine.Vector3,UnityEngine.Vector2)").IsStatic, "Utils.worldPositionFromUnityToLongLat (Unity -> geo)");
        M(utils, "UnityYawToTrueHeading", "System.Single(System.Single," + G + ")");
        Check(M(T(game, "SeaPower.TerrainUtils"), "GetHeightAt", "System.Single(" + G + ",System.Boolean,System.Boolean,System.Boolean)").IsStatic, "TerrainUtils.GetHeightAt (diagnostics: is the battle DEM land here?)");
        Fd(T(game, "SeaPower.Globals"), "_currentCenterTile", "UnityEngine.Vector2", true);
        Fd(T(game, "SeaPower.Globals"), "_mainGameViewModel", "SeapowerUI.ViewModels.MainGameViewModel", true);
        M(T(game, "SeapowerUI.ViewModels.MainGameViewModel"), "RaiseAlert", "System.Void(SeaPower.ObjectBase,System.String)");
        M(T(game, "SeaPower.RenderPosition"), "getSelectedObject", "SeaPower.ObjectBase()");
        var ob = T(game, "SeaPower.ObjectBase");
        Check(ob.Properties.Any(p => p.Name == "DesiredAltitude" && p.PropertyType.FullName == "UniRx.ReactiveProperty`1<System.Single>"), "ObjectBase.DesiredAltitude : ReactiveProperty<float>");
        Check(ob.Properties.Any(p => p.Name == "_geoPosition" && p.PropertyType.FullName == G), "ObjectBase._geoPosition");
        Fd(ob, "_obp", "SeaPower.ObjectBaseParameters"); Fd(ob, "_canUpdate", "System.Boolean");
        Fd(T(game, "SeaPower.ObjectBaseParameters"), "_objectIniName", "System.String");
        Check(ob.Properties.Any(p => p.Name == "IsPlayerObject"), "ObjectBase.IsPlayerObject");
        // speed
        var comp = T(game, "SeaPower.Compartments");
        var want = M(comp, "UpdateWantedVelocityInKnots", "System.Void()");
        Fd(comp, "_telegraphVelocities", "System.Single[]"); Fd(comp, "_telegraphVelocitiesSubmerged", "System.Single[]");
        Fd(comp, "_submarine", "SeaPower.Submarine"); Fd(comp, "_baseObject", "SeaPower.ObjectBase"); Fd(comp, "_isSinking", "System.Boolean"); Fd(comp, "_immobile", "System.Boolean");
        Check(Index(want, i => Field(i, Code.Ldfld, "SeaPower.Compartments", "_telegraphVelocitiesSubmerged")) >= 0, "UpdateWantedVelocityInKnots picks the submerged telegraph table");
        Check(comp.Properties.Any(p => p.Name == "WantedVelocityInKnots" && p.SetMethod != null), "Compartments.WantedVelocityInKnots setter");
        foreach (var owner in new[] { "SeaPower.Vessel", "SeaPower.Submarine" })
        {
            var t = T(game, owner);
            var fixedUpdate = M(t, "OnFixedUpdate", "System.Void()");
            var thrust = M(t, "applyMainThrust", "System.Void()");
            int u = Index(fixedUpdate, i => Calls(i, "SeaPower.Compartments", "UpdateWantedVelocityInKnots")), a = Index(fixedUpdate, i => Calls(i, owner, "applyMainThrust"));
            Check(u >= 0 && a > u, owner + ".OnFixedUpdate: UpdateWantedVelocityInKnots, then applyMainThrust");
            Check(Index(thrust, i => Calls(i, "SeaPower.Compartments", "get_WantedVelocityInKnots")) >= 0, owner + ".applyMainThrust reads WantedVelocityInKnots");
        }
        // submarines
        var sub = T(game, "SeaPower.Submarine");
        var fu = M(sub, "OnFixedUpdate", "System.Void()");
        int keep = Index(fu, i => Calls(i, "SeaPower.Submarine", "DepthKeeping")), apply = Index(fu, i => Calls(i, "SeaPower.Submarine", "applyDepth")), blowCall = Index(fu, i => Calls(i, "SeaPower.Submarine", "needToEmergencySurface"));
        int readDesired = Index(fu, i => Calls(i, "SeaPower.ObjectBase", "get_DesiredAltitude"));
        Check(readDesired >= 0 && keep > readDesired && apply > keep && blowCall > apply, "Submarine.OnFixedUpdate: reads DesiredAltitude, DepthKeeping, applyDepth, then needToEmergencySurface (the prefix clamp runs before all of them)");
        var dk = M(sub, "DepthKeeping", "System.Void()");
        int d0 = Index(dk, i => Calls(i, "SeaPower.ObjectBase", "get_DesiredAltitude"));
        Check(d0 >= 0 && d0 < 3 && Index(dk, i => Field(i, Code.Stfld, "SeaPower.Submarine", "_targetAltitude")) == d0 + 2, "DepthKeeping starts with _targetAltitude = DesiredAltitude.Value");
        var ad = M(sub, "applyDepth", "System.Void()");
        Check(ad.Body.Instructions.Take(3).Any(i => Calls(i, "SeaPower.Submarine", "DepthKeeping")), "applyDepth calls DepthKeeping first");
        Check(ad.Body.Instructions.Count(i => Field(i, Code.Stfld, "SeaPower.Submarine", "_targetAltitude")) == 2, "applyDepth writes _targetAltitude = 0 only in its two surfacing branches (reached when the boat is at the surface)");
        var sd = M(sub, "setDepth", "System.Void(System.Single)");
        Check(Index(sd, i => Calls(i, "SeaPower.ObjectBase", "get_DesiredAltitude")) >= 0, "setDepth writes DesiredAltitude = -depth");
        var preset = M(sub, "setPresetDepth", "System.Int32(System.Int32,System.Boolean)");
        Check(Index(preset, i => i.OpCode.Code == Code.Ldc_R4 && Math.Abs((float)i.Operand - 0.00453571f) < 1e-7) >= 0 && Index(preset, i => Calls(i, "SeaPower.Submarine", "setDepth")) >= 0, "presets: feet x 0.00453571 (1/220.47) -> Unity units -> setDepth");
        var blow = M(sub, "needToEmergencySurface", "System.Boolean()");
        Check(Index(blow, i => Calls(i, "SeaPower.Submarine", "set_WasEmergencySurfacingInitiated")) >= 0, "needToEmergencySurface sets WasEmergencySurfacingInitiated");
        Check(sub.Properties.Any(p => p.Name == "WasEmergencySurfacingInitiated" && p.SetMethod != null), "WasEmergencySurfacingInitiated setter");
        var es = M(T(game, "SubmarineStates.EmergencySurface"), "onFixedUpdate", "System.Void()");
        Check(Index(es, i => Calls(i, "SeaPower.Submarine", "setDepth")) >= 0, "EmergencySurface state orders setDepth(0) (clamped by the setDepth prefix)");
        foreach (var (name, sig) in new[] { ("isSubmerged", "System.Boolean()"), ("retractMasts", "System.Void()"), ("getRaisedMastsCount", "System.Int32()"), ("isSnorkelMastOut", "System.Boolean()"), ("toggleSnorkelMast", "System.Void(System.Boolean)"), ("togglePeriscopeMast", "System.Void(System.Boolean)"), ("toggleESMMast", "System.Void(System.Boolean)"), ("toggleRadarMast", "System.Void(System.Boolean)"), ("RaisePeriscopeMast", "System.Void()"), ("RaiseESMMast", "System.Void()") })
            M(sub, name, sig);
        // every raise path goes through SensorSystem.Enable(bool, bool) or SnorkelMastSystem.Enable(bool)
        foreach (var name in new[] { "togglePeriscopeMast", "toggleESMMast", "toggleRadarMast", "RaisePeriscopeMast", "RaiseESMMast" })
            Check(sub.Methods.Where(x => x.Name == name).All(x => Index(x, i => Calls(i, "SeaPower.SensorSystem", "Enable")) >= 0), name + " raises through SensorSystem.Enable");
        Check(Index(M(sub, "toggleSnorkelMast", "System.Void(System.Boolean)"), i => Calls(i, "SeaPower.SnorkelMastSystem", "Enable")) >= 0, "toggleSnorkelMast raises through SnorkelMastSystem.Enable");
        var sensor = T(game, "SeaPower.SensorSystem");
        M(sensor, "Enable", "System.Void(System.Boolean,System.Boolean)");
        Check(!game.Types.Where(t => t.BaseType != null && t.BaseType.FullName == "SeaPower.SensorSystem").Any(t => t.Methods.Any(x => x.Name == "Enable")), "no SensorSystem subclass overrides Enable");
        M(T(game, "SeaPower.SnorkelMastSystem"), "Enable", "System.Void(System.Boolean)");
        // manual height control (pitch and ballast keys)
        var phc = M(ob, "setPlayerHeightControl", "System.Void(System.Boolean)");
        Check(phc.IsPublic && !phc.IsStatic && !phc.IsVirtual && Index(phc, i => Field(i, Code.Stfld, "SeaPower.ObjectBase", "_playerHeightControl")) >= 0, "ObjectBase.setPlayerHeightControl(bool) public, writes _playerHeightControl");
        Fd(ob, "_playerHeightControl", "System.Boolean");
        var input = M(T(game, "SeaPower.InputHandler"), "handleVesselInputs", "System.Void()");
        foreach (var target in new[] { "changePitch", "changeBallast" })
        {
            var calls = input.Body.Instructions.Where(i => Calls(i, "SeaPower.Submarine", target)).ToList();
            Check(calls.Count == 2 && calls.All(c => { var b = input.Body.Instructions; int at = b.IndexOf(c); for (int k = at - 1; k >= Math.Max(0, at - 8); k--) if (Calls(b[k], "SeaPower.ObjectBase", "setPlayerHeightControl")) return b[k - 1].OpCode.Code == Code.Ldc_I4_1; return false; }), "InputHandler: setPlayerHeightControl(true) before each " + target);
        }
        Check(game.GetTypes().SelectMany(t => t.Methods).Where(x => x.HasBody).SelectMany(x => x.Body.Instructions.Select((i, n) => new { x, i, n })).Where(z => Calls(z.i, "SeaPower.ObjectBase", "setPlayerHeightControl") && z.n > 0 && z.x.Body.Instructions[z.n - 1].OpCode.Code == Code.Ldc_I4_1).All(z => z.x.DeclaringType.FullName == "SeaPower.InputHandler"), "only the input handler turns manual height control on");
        Check(Index(M(sub, "changeBallast", "System.Void(System.Single)"), i => Field(i, Code.Stfld, "SeaPower.Submarine", "_targetBallastDepthChangeRate")) >= 0 && Index(M(sub, "changePitch", "System.Void(System.Single)"), i => Calls(i, "SeaPower.Submarine", "setDepth")) >= 0, "changeBallast writes the ballast rate; changePitch ends in setDepth (dropped while held under manual control)");
        Check(ad.Body.Instructions.Count(i => Field(i, Code.Ldfld, "SeaPower.ObjectBase", "_playerHeightControl")) == 4, "applyDepth skips the target-depth rate, pitch, rate reset and target clamp under manual height control (cleared while held)");
        foreach (var f in new[] { "_targetAltitude", "_currentDepthChangeUsingTanks", "_targetBallastDepthChangeRate" }) Check(Fd(sub, f, "System.Single").IsPublic, "Submarine." + f + " public float");
        Check(Fd(sub, "_divingInProgress", "System.Boolean").IsPublic, "Submarine._divingInProgress public bool");
        Check(game.GetTypes().SelectMany(t => t.Methods).Where(x => x.HasBody && x.Body.Instructions.Any(i => Calls(i, "SeaPower.Submarine", "applyDepth"))).Select(x => x.DeclaringType.FullName + "::" + x.Name).SequenceEqual(new[] { "SeaPower.Submarine::OnFixedUpdate" }) && Index(fu, i => Field(i, Code.Ldfld, "SeaPower.Submarine", "_divingInProgress")) >= 0, "applyDepth is called only from OnFixedUpdate's diving branch (the postfix puts _divingInProgress back)");
        var dkb = dk.Body.Instructions;
        int zero = dkb.Count - 2;
        Check(Field(dkb[zero], Code.Stfld, "SeaPower.Submarine", "_targetAltitude") && dkb[zero - 1].OpCode.Code == Code.Ldc_R4 && (float)dkb[zero - 1].Operand == 0f && Index(dk, i => Field(i, Code.Ldfld, "SeaPower.ObjectBase", "_playerHeightControl")) >= 0, "DepthKeeping ends with the shallow-water _targetAltitude = 0 (clamped by the postfix)");
        // the snorkelling state
        var snork = T(game, "SubmarineStates.Snorkelling");
        Fd(snork, "_depthReached", "System.Boolean"); Fd(snork, "_submarine", "SeaPower.Submarine");
        var sf = M(snork, "onFixedUpdate", "System.Void()");
        int r0 = Index(sf, i => Field(i, Code.Ldfld, "SubmarineStates.Snorkelling", "_depthReached")), alt = Index(sf, i => Calls(i, "SeaPower.ObjectBase", "get_OnAltitude")), raise = Index(sf, i => Calls(i, "SeaPower.Submarine", "toggleSnorkelMast")), latch = Index(sf, i => Field(i, Code.Stfld, "SubmarineStates.Snorkelling", "_depthReached"));
        Check(r0 == 1 && alt > r0 && raise > alt && latch > raise, "Snorkelling.onFixedUpdate: if (!_depthReached && OnAltitude) { toggleSnorkelMast; _depthReached = true } (read first, so the prefix decides)");
        Check(Index(M(snork, "get_IsFinished", "System.Boolean()"), i => Field(i, Code.Ldfld, "SeaPower.Submarine", "_batteryCapacity")) >= 0 && Index(M(snork, "onEnter", "System.Void()"), i => Calls(i, "SeaPower.Submarine", "setPresetDepth")) >= 0, "Snorkelling ends on a full battery; onEnter orders a preset depth through setDepth");
        var onAlt = M(ob, "get_OnAltitude", "System.Boolean()");
        Check(Index(onAlt, i => Calls(i, "SeaPower.ObjectBase", "get_DesiredAltitude")) >= 0, "OnAltitude compares with DesiredAltitude (given back on release)");
        var bs = T(game, "SeaPower.BaseSystem");
        Fd(bs, "_baseObject", "SeaPower.ObjectBase"); Fd(bs, "_isSubmarineMast", "System.Boolean"); Fd(bs, "_systemType", "SeaPower.BaseSystem/SystemType");
        var st = bs.NestedTypes.Single(t => t.Name == "SystemType");
        Check((int)st.Fields.Single(f => f.Name == "SensorPeriscope").Constant == 3 && (int)st.Fields.Single(f => f.Name == "SensorESM").Constant == 8, "SystemType.SensorPeriscope = 3, SensorESM = 8");
        // Ceto (Assets.dll), by reflection at run time
        var assets = ModuleDefinition.ReadModule(Path.Combine(flat, "Assets.dll"), new ReaderParameters { AssemblyResolver = resolver });
        var ocean = T(assets, "Ceto.Ocean");
        Check(ocean.Properties.Any(p => p.Name == "Instance" && p.GetMethod != null && p.GetMethod.IsStatic), "Ceto.Ocean.Instance");
        M(ocean, "QueryWaves", "System.Single(System.Single,System.Single,System.Boolean)");
        Check(game.GetTypes().SelectMany(t => t.Methods).Where(x => x.HasBody).Any(x => x.Body.Instructions.Any(i => Calls(i, "Ceto.Ocean", "QueryWaves"))), "the game itself floats objects with QueryWaves");
        Console.WriteLine("bindings: every Sea Power 0.9.3 member the sea ice uses is present with the IL the design rests on");
    }

    // ---- 7: candidate runtime ----------------------------------------------------------------

    static void Runtime(string runtimePath)
    {
        var rt = ModuleDefinition.ReadModule(runtimePath);
        var battle = rt.GetType("Sest.RuntimeFixes.SeaIceBattle");
        Check(battle != null && rt.GetType("Sest.RuntimeFixes.SeaIceSheet") != null && rt.GetType("Sest.RuntimeFixes.SeaIceSheetDriver") != null, "runtime has the sea ice types");
        var speed = battle.Methods.Single(m => m.Name == "SpeedPostfix");
        var names = speed.Parameters.Select(p => p.Name).ToList();
        Check(names.SequenceEqual(new[] { "__instance", "____telegraphVelocities", "____telegraphVelocitiesSubmerged", "____submarine" }), "speed postfix injects _telegraphVelocities, _telegraphVelocitiesSubmerged and _submarine");
        Check(speed.Parameters[1].ParameterType.FullName == "System.Single[]" && speed.Parameters[3].ParameterType.FullName == "SeaPower.Submarine", "injected field types");
        var floe = battle.Methods.Single(m => m.Name == "FloeIcePostfix");
        Check(floe.Parameters.Select(p => p.ParameterType.FullName).SequenceEqual(new[] { "SeaPower.Environment", "SeaPower.GeoPosition", "System.Single&" }), "getFloeIce postfix signature");
        var sdp = battle.Methods.Single(m => m.Name == "SetDepthPrefix");
        Check(sdp.Parameters[1].ParameterType.FullName == "System.Single&" && sdp.ReturnType.FullName == "System.Boolean", "setDepth prefix takes the depth by ref and can drop changePitch's call");
        var snp = battle.Methods.Single(m => m.Name == "SnorkelStatePrefix");
        Check(snp.Parameters.Select(p => p.Name + ":" + p.ParameterType.FullName).SequenceEqual(new[] { "____submarine:SeaPower.Submarine", "____depthReached:System.Boolean&" }), "snorkelling-state prefix injects _submarine and _depthReached by ref");
        foreach (var n in new[] { "DepthKeepingPostfix", "ApplyDepthPostfix" })
            Check(battle.Methods.Single(m => m.Name == n).Parameters.Select(p => p.Name + ":" + p.ParameterType.FullName).SequenceEqual(new[] { "__instance:SeaPower.Submarine" }), n + " takes the submarine");
        Check(battle.Methods.Single(m => m.Name == "MastPrefix").ReturnType.FullName == "System.Boolean" && battle.Methods.Single(m => m.Name == "SnorkelPrefix").ReturnType.FullName == "System.Boolean", "mast prefixes can skip raising");
        var entry = rt.GetType("Sest.RuntimeFixes.RuntimeFixesMod").Methods.Single(m => m.Name == "TriggerEntryPoint");
        int ice = Index(entry, i => Calls(i, "Sest.RuntimeFixes.SeaIceBattle", "Install")), costs = Index(entry, i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "CumulativeCombatCosts");
        Check(ice > 0 && costs > ice, "sea ice installs before CumulativeCombatCosts' early return");
        Check(Index(entry, i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "SeaIce") > 0, "SeaIce switch read");
        Console.WriteLine("runtime: patch signatures and install order checked");
    }
}
