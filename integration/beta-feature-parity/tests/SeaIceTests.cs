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
//   the snorkelling state); 5 the lead field, the drift-ice floe field
//   (share, size spread, blend into the pack, pack unchanged at 60 %+,
//   floes pushed out of channels), floe placement, the sheet
//   mesher, its chunk layout, the double-buffered refill and the sheet height;
//   5b the polar frame (85-90 degrees, the pole itself, the south) and the
//   battle date read from the clock's fields (an undated clock is no date);
// 6 every Sea Power 0.9.3 member the runtime binds, with the IL facts the
//   design rests on (checked with Cecil, no game launch);
// 7 the candidate runtime: patch parameters that name game fields, and the
//   install order (before CumulativeCombatCosts' early return);
// 8 ship effects (SeaIceWake.cs and the closed-slab mesher): material values,
//   closed-slab topology and normals, the ocean clip mask, carved channels
//   (geometry, ragged edges, refreeze timing, dirty chunks, bounds, the
//   speed rule in a channel with 'ahead' eased like 'here', incremental and
//   throttled snapshots, game-time windows at high time compression), bow
//   pieces (pool cap, lifetimes, motion, distance-weighted pool shares) and
//   the breaking intensity, sound rate limit, time-compression muting and
//   added noise;
// 9 the battle-map ice layer's pure part (SeaIceMapRules.cs; SeaIceMap.cs
//   draws it): grid, plan, rebuild decision, view box, lines, fill, land,
//   readout and opacity; its game members are in 6 and its install in 7;
// 10 hull contact (SeaIceRules.cs IceSurface, IceHullContact, IceContactState;
//   SeaIceWake.cs CapInContact and the contact intensity): the contact field
//   is the drawn one (the near sheet's lattice fraction and regime equal the
//   mesher's at every grid point, through the floe/pack blend, channels and
//   pushed floes cut alike; the floe query equals the placed floes), the
//   footprint (21 points, bow weighted, 'near' margin, heading), the gain and
//   its release, the speed rule never harder than the area rule and never
//   trapping, and tracks through patchy ice and the heavy pack.
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
            // The rest pins seaice.py's own Barents numbers (the review's 10 March 36E profile).
            SeaIceModel.MeasuredArctic = false;
            SeaIceModel.MeasuredAntarctic = false;
            Cache();
            Speed();
            Edge();
            Track();
            Submarine();
            Snorkel();
            Field();
            Floes();
            Polar();
            Mesher();
            Sheet();
            Look();
            Slab();
            Channels();
            Pieces();
            MapLayer();
            Contact();
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
            double c = SeaIceModel.ConcentrationWeatherBranch(g[i + 3], g[i + 4], Noon(g[i], g[i + 1], g[i + 2]));
            worst = Math.Max(worst, Math.Abs(c - g[i + 5]));
        }
        Check(worst < 1e-9, "C# model equals seaice.ice_at at " + g.Length / 6 + " golden points (worst " + worst + ")");
        Console.WriteLine("model: " + g.Length / 6 + " golden points match seaice.py, worst difference " + worst.ToString("E1", CultureInfo.InvariantCulture) + " pp");
        var r = SeaIceGolden.Review;
        for (int i = 0; i < r.Length; i += 6)
        {
            double c = SeaIceModel.ConcentrationWeatherBranch(r[i + 3], r[i + 4], Noon(r[i], r[i + 1], r[i + 2]));
            Check(Math.Abs(c - r[i + 5]) < 1e-9, "review point " + r[i + 3] + "," + r[i + 4]);
            Console.WriteLine("  " + (int)r[i] + "-" + ((int)r[i + 1]).ToString("00") + "-" + ((int)r[i + 2]).ToString("00") + " " + r[i + 3] + ", " + r[i + 4] + ": " + F(c) + " %");
        }
        var mar10 = new DateTime(2029, 3, 10, 12, 0, 0, DateTimeKind.Utc);
        Check(Math.Abs(SeaIceModel.ConcentrationWeatherBranch(72, 36, mar10) - 18.7) < 0.05, "10 March 72N 36E 18.7 % (review, seaice.py)");
        Check(Math.Abs(SeaIceModel.ConcentrationWeatherBranch(74, 36, mar10) - 62.3) < 0.05, "10 March 74N 36E 62.3 % (review, seaice.py)");
        Check(SeaIceModel.Concentration(67, 6, mar10) < 0.01, "Norwegian Sea open");
        // hemisphere seasons
        Check(SeaIceModel.Concentration(79, 36, Noon(2029, 3, 15)) > SeaIceModel.Concentration(79, 36, Noon(2029, 9, 15)) + 40, "Barents: March pack, September open");
        Check(SeaIceModel.Concentration(-62, -40, Noon(2029, 9, 15)) > SeaIceModel.Concentration(-62, -40, Noon(2029, 2, 20)) + 40, "Weddell: September pack, February open");
        Check(SeaIceModel.Concentration(-75, 0, Noon(2029, 3, 10)) > 0 && SeaIceModel.Concentration(75, 0, Noon(2029, 3, 10)) > 0, "both hemispheres");
        Check(SeaIceModel.Concentration(39.9, 120.5, Noon(2029, 1, 15)) == 0, "no ice below 40 degrees");
        Check(SeaIceModel.Concentration(89.9, 0, Noon(2029, 9, 15)) > 90, "central Arctic keeps its pack at the minimum (NORTH_EDGE_CAP)");
        // SEST soft knee (28 Nov 2026): no perfect circle of edge and heavy pack at the minimum.
        Check(Math.Abs(SeaIceModel.NorthEdge(70.0) - 70.0) < 1e-4 && Math.Abs(SeaIceModel.NorthEdge(86.5) - (80.5 + 0.35 * 6.0)) < 0.01,
            "the knee leaves a southern edge alone and keeps 35 % of the distance past 80.5N");
        Check(SeaIceModel.Concentration(89.9, 0, Noon(2028, 10, 1)) > 90 && SeaIceModel.Concentration(88.0, 120, Noon(2028, 9, 15)) > 90,
            "the central Arctic stays heavy pack at the minimum");
        double HeavyLat(double lon) { for (double lat = 70; lat < 90; lat += 0.05) if (SeaIceModel.Concentration(lat, lon, Noon(2028, 10, 1)) >= 60) return lat; return 90; }
        double heavyLo = 90, heavyHi = 0;
        foreach (double lon in new[] { -20.0, 0.0, 20.0, 40.0 }) { double h = HeavyLat(lon); heavyLo = Math.Min(heavyLo, h); heavyHi = Math.Max(heavyHi, h); }
        Check(heavyHi - heavyLo > 0.75 && heavyHi < 85.5, "1 October: the heavy-pack line from 20W to 40E follows the model's shape (" + F(heavyLo) + " to " + F(heavyHi) + " N), not one circle");
        Check(Math.Abs(SeaIceModel.ConcentrationWeatherBranch(70, -60, Noon(2029, 3, 15)) - SeaIceModel.Concentration(70, -60, Noon(2029, 3, 15))) < 0.01,
            "winter Baffin Bay ice is unchanged by the knee");
        // SEST measured Arctic edge (28 Nov 2026): NSIDC's 2016-2025 monthly edges from the Greenland Sea to the Beaufort Sea.
        Check(SeaIceArcticData.Edge.Length == 12 * 360, "Arctic edge table: 12 months x 360 meridians");
        double Edge15(double lon, DateTime d, double from = 66.0) { for (double lat = from; lat < 90; lat += 0.01) if (SeaIceModel.Concentration(lat, lon, d) >= 15) return lat; return 90; }
        double midWorst = 0;
        foreach (int month in new[] { 1, 3, 8, 10, 12 })
            foreach (double lon in new[] { -9.5, 30.5, 50.5, 100.5, 140.5, 170.5, -140.5 })
            {
                double want = SeaIceArcticData.Edge[(month - 1) * 360 + (int)(lon + 179.5)];
                if (want >= 73.0) midWorst = Math.Max(midWorst, Math.Abs(Edge15(lon, Noon(2029, month, 16), 72.0) - want));
            }
        Check(midWorst < 0.02, "on a mid-month date the 15 % line is NSIDC's median edge (worst " + F(midWorst) + " deg)");
        var oct1 = Noon(2028, 10, 1);
        Check(Edge15(40, oct1) > 81.0 && Edge15(80, oct1) > 81.0, "1 October: the Barents and Kara Seas are open to about 81N");
        bool siberia = true;
        foreach (double lon in new[] { 120.0, 140.0, 160.0 }) { double e15 = Edge15(lon, oct1); siberia &= e15 > 76.5 && e15 < 80.0; }
        Check(siberia, "1 October: the Laptev and East Siberian edge is at 77-80N, not one circle");
        Check(SeaIceModel.Concentration(72, 36, mar10) < 1.0 && SeaIceModel.Concentration(69.8, 36, mar10) < 5.0 && SeaIceModel.Concentration(79, 36, mar10) > 60.0,
            "10 March: the southern Barents Sea and the Murman coast are open water, the northern Barents is pack");
        Check(SeaIceModel.Concentration(75, 120, mar10) > 95.0 && SeaIceModel.Concentration(74, 70, mar10) > 95.0 && SeaIceModel.Concentration(73, 140, Noon(2029, 11, 20)) > 90.0,
            "the Kara and Laptev Seas fill in winter; the Laptev and East Siberian freeze by late November");
        bool kept = true;
        foreach (var p in new[] { (65.5, 38.0), (59.0, -145.0), (63.0, 22.0) })
            kept &= Math.Abs(SeaIceModel.Concentration(p.Item1, p.Item2, mar10) - SeaIceModel.ConcentrationWeatherBranch(p.Item1, p.Item2, mar10)) < 1e-6;
        Check(kept, "the White Sea, the Gulf of Alaska and the Gulf of Bothnia keep seaice.py's ice");
        Check(SeaIceModel.ArcticWeight(-60) == 0 && SeaIceModel.ArcticWeight(-100) == 0 && SeaIceModel.ArcticWeight(0) == 1 && SeaIceModel.ArcticWeight(90) == 1
              && SeaIceModel.ArcticWeight(SeaIceModel.WrapLon(180)) == 1 && SeaIceModel.ArcticWeight(-140) == 1, "the measured edge's sector: Greenland Sea to Beaufort Sea");
        double seam = 0;
        foreach (var d in new[] { oct1, Noon(2029, 9, 15), Noon(2029, 3, 15) })
            foreach (double lat in new[] { 73.0, 75.0, 77.0, 78.5 })
                seam = Math.Max(seam, Math.Max(Math.Abs(SeaIceModel.Concentration(lat, -155.5, d) - SeaIceModel.Concentration(lat, -154.5, d)),
                                               Math.Abs(SeaIceModel.Concentration(lat, 179.5, d) - SeaIceModel.Concentration(lat, -179.5, d))));
        Check(seam < 5.0 && SeaIceModel.Concentration(68, -168, Noon(2029, 3, 15)) > 85, "no seam at the Chukchi Sea's mask north of 72N (worst " + F(seam) + " points); its winter ice stays");
        // SEST measured Antarctic edge (28 Nov 2026): NSIDC's 2016-2025 monthly edges all round Antarctica.
        Check(SeaIceAntarcticData.Edge.Length == 12 * 360 && SeaIceAntarcticData.Edge.All(v => v >= 50.0 && v <= SeaIceAntarcticData.NoIce),
            "Antarctic edge table: 12 months x 360 meridians, 50S to " + SeaIceAntarcticData.NoIce + "S");
        double South15(double lon, DateTime d) { for (double lat = 50.0; lat < 80.0; lat += 0.01) if (SeaIceModel.Concentration(-lat, lon, d) >= 15) return lat; return 80.0; }
        // 31-day months: day 16 is exactly mid-month, so no mix with the next month.
        double southWorst = 0;
        foreach (int month in new[] { 1, 3, 5, 8, 10, 12 })
            foreach (double lon in new[] { -170.5, -120.5, -40.5, 0.5, 60.5, 120.5, 160.5 })
            {
                double want = SeaIceAntarcticData.Edge[(month - 1) * 360 + (int)(lon + 179.5)];
                if (want < 75.0) southWorst = Math.Max(southWorst, Math.Abs(South15(lon, Noon(2029, month, 16)) - want));
            }
        Check(southWorst < 0.02, "on a mid-month date the southern 15 % line is NSIDC's median edge (worst " + F(southWorst) + " deg)");
        Check(South15(0, Noon(2029, 9, 16)) < 57.0 && South15(0, Noon(2029, 9, 16)) > 54.0 && South15(-40, Noon(2029, 9, 16)) < 60.0,
            "September: the pack reaches 54-57S south of Africa and past 60S in the Weddell Sea");
        Check(SeaIceModel.Concentration(-66, 0, Noon(2029, 2, 20)) < 1.0 && SeaIceModel.Concentration(-74, -45, Noon(2029, 2, 20)) > 60.0,
            "February: open water off Dronning Maud Land, the western Weddell Sea keeps its pack");
        var antarcticOn = Noon(2029, 9, 16);
        Check(Math.Abs(SeaIceModel.ConcentrationWeatherBranch(-68, -42, Noon(2029, 1, 12)) - 37.1) < 0.05, "12 January 68S 42W 37.1 % (review, seaice.py's own path)");
        double southSeam = 0;
        foreach (double lat in new[] { 58.0, 62.0, 66.0 }) southSeam = Math.Max(southSeam, Math.Abs(SeaIceModel.Concentration(-lat, 179.5, antarcticOn) - SeaIceModel.Concentration(-lat, -179.5, antarcticOn)));
        Check(southSeam < 5.0, "no seam at the antimeridian in the south (worst " + F(southSeam) + " points)");
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
        // Longitude wraps before the model: map grids across the antimeridian run west of -180, and IceOrder's
        // Okhotsk branch read raw lon (15 April 58N: 0.9 % at 155E, 95 % at -205).
        var apr15 = Noon(2029, 4, 15);
        double wrapWorst = 0;
        for (double la = 40; la <= 80; la += 0.5)
            for (double lo = 130; lo <= 200; lo += 0.7)
            {
                double here = SeaIceModel.Concentration(la, lo, apr15);
                wrapWorst = Math.Max(wrapWorst, Math.Max(Math.Abs(SeaIceModel.Concentration(la, lo - 360, apr15) - here), Math.Abs(SeaIceModel.Concentration(la, lo + 360, apr15) - here)));
            }
        Check(wrapWorst < 1e-6 && SeaIceModel.Concentration(58, -205, apr15) < 5 && SeaIceModel.Concentration(56, -210, Noon(2029, 1, 10)) < 10,
              "the model wraps longitude first: a whole turn west or east reads the same ice (worst " + wrapWorst + ")");
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

    // The one ice edge (IceEdge): whatever slows, holds or breaks is drawn.
    static void Edge()
    {
        IceEdge.ResetForTests();
        Check(IceEdge.Default == IceRules.Threshold(0, 0) && IceEdge.Percent == 10, "the default edge is class none's first slowing threshold (10 %)");
        string why;
        Check(IceEdge.Parse("", out why) == 10 && why == "default" && IceEdge.Parse(" 15 ", out why) == 15 && why == "SeaIceEdgePercent" && IceEdge.Parse("12.5", out _) == 12.5, "SeaIceEdgePercent read as InvariantCulture");
        Check(IceEdge.Parse("4", out why) == 10 && why.Contains("ignored") && IceEdge.Parse("31", out _) == 10 && IceEdge.Parse("abc", out _) == 10 && IceEdge.Parse("12,5", out _) == 10 && IceEdge.Parse("NaN", out _) == 10,
              "out of 5-30 or unreadable: the default, said why");
        string first = IceEdge.Configure("15");
        Check(first != null && first.StartsWith("ice edge 15 % (SeaIceEdgePercent)") && IceEdge.Configure("15") == null && IceEdge.Percent == 15, "Configure logs once for SeaIce and CampaignIce together: " + first);
        Check(IceEdge.Configure("bad") != null && IceEdge.Percent == 10, "a bad value falls back to the default");
        // Bear Island, 10 March, 13 %: the default draws it and slows; SeaIceEdgePercent=15 does neither.
        IceEdge.ResetForTests();
        Check(IceRules.Access(13, 0) == IceAccess.Caution && SeaIceField.DrawnFraction(13, IceEdge.Percent) == 0.13, "13 % at the default edge: drawn (0.13) and caution");
        IceEdge.ResetForTests(15);
        Check(IceRules.Access(13, 0) == IceAccess.Open && SeaIceField.DrawnFraction(13, IceEdge.Percent) == 0 && IceRules.Access(15, 0) == IceAccess.Caution, "13 % under a 15 % edge: not drawn and not slowed");
        var hs = new IceSpeedState();
        hs.Update(20, 0); hs.Update(15.4, 0);
        bool held = hs.State == IceAccess.Caution;
        Check(held && hs.Update(14.99, 0) == IceAccess.Open && hs.Update(14.5, 0) == IceAccess.Open, "a raised edge: caution while drawn (15.4 %), open as soon as it is not (14.99 %), no hysteresis below the edge");
        IceEdge.ResetForTests();
        var hd = new IceSpeedState();
        hd.Update(20, 0); hd.Update(10.5, 0);
        bool cautionAtEdge = hd.State == IceAccess.Caution;
        hd.Update(9.5, 0);
        Check(cautionAtEdge && hd.State == IceAccess.Open, "default edge: 9.5 % coming out of the ice is open (not drawn, not slowed), 10.5 % caution");
        hd.Update(35, 0); hd.Update(29.5, 0);
        Check(hd.State == IceAccess.Restricted, "hysteresis between ice states is unchanged (restricted held at 29.5 %)");
        IceEdge.ResetForTests(15);
        // The invariant, at every edge the ini accepts, for every class and concentration.
        foreach (double edge in new[] { 5.0, 10.0, 12.5, 15.0, 30.0 })
        {
            IceEdge.ResetForTests(edge);
            bool ok = true;
            for (int cap = 0; cap < IceRules.Capabilities.Length; cap++)
            {
                // the hull's state machine too, down from heavy ice through the hysteresis band
                var walk = new IceSpeedState();
                for (double pc = 100; pc >= 0; pc -= 0.25)
                    if (walk.Update(pc, cap) != IceAccess.Open && SeaIceField.DrawnFraction(pc, IceEdge.Percent) <= 0) ok = false;
                for (double pc = 0; pc <= 100; pc += 0.25)
                {
                    bool drawn = SeaIceField.DrawnFraction(pc, IceEdge.Percent) > 0;
                    if (IceRules.Access(pc, cap) != IceAccess.Open && !drawn) ok = false;
                    if (IceBreakRule.Intensity(10, pc, IceEdge.Percent) > 0 && !drawn) ok = false;
                    if (pc < edge && IceRules.Access(pc, cap) != IceAccess.Open) ok = false;
                }
            }
            Check(ok, "edge " + edge + " %: every concentration that slows or breaks is drawn, and nothing under the edge acts");
        }
        IceEdge.ResetForTests();
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

    // Drift ice below 60 %: separate floes of many sizes (owner, 23 Nov: 51 % drew large solid sheets),
    // the share still the concentration, the pack field (and the submarine rule) unchanged from 60 %,
    // small floes pushed out of a channel whole.
    static void Floes()
    {
        uint seed = SeaIceField.SeedOf(20290115);
        Check(SeaIceFloes.On && SeaIceFloes.Warm(), "floe calibration builds");
        // the 3 x 3 cell window holds every floe that can reach a point (centre jitter + farthest corner at QCap)
        Check(SeaIceFloes.MaxCirc * SeaIceFloes.RadiusShare * Math.Sqrt(SeaIceFloes.QCap) < 1.5 - SeaIceFloes.Jitter / 2 - 0.1, "floe reach inside the 3 x 3 window (" + F(SeaIceFloes.MaxCirc * SeaIceFloes.RadiusShare * Math.Sqrt(SeaIceFloes.QCap)) + " cells)");
        foreach (double p in new[] { 0.15, 0.25, 0.35, 0.44, 0.5, 0.55, 0.6 })
        {
            int ice = 0, n = 0;
            for (int j = 0; j < 220; j++)
                for (int i = 0; i < 220; i++) { n++; if (SeaIceField.IsIce(40 + i * 0.0517, -7 + j * 0.0491, p, seed)) ice++; }
            // pure floes: within 2 %; in the blend the pack noise's own regional spread (550 m leads) shows, as in Field()
            Check(Math.Abs((double)ice / n - p) < (p <= 0.44 ? 0.02 : 0.04), "floe field share " + F((double)ice / n) + " for fraction " + p);
        }
        Check(SeaIceFloes.PackWeight(0.44) == 0 && SeaIceFloes.PackWeight(0.6) == 1 && SeaIceFloes.PackWeight(0.52) > 0 && SeaIceFloes.PackWeight(0.52) < 1 && SeaIceFloes.PackWeight(0.5) < SeaIceFloes.PackWeight(0.55), "floes to 44 %, pack from 60 %, a smooth blend between");
        // from 60 % (the submarine rule's heavy ice) the field is the pack field, bit for bit
        int same = 0;
        for (int i = 0; i < 3000; i++) { double e = i * 0.0373, nn = i * 0.0291, p = 0.6 + 0.38 * (i % 7) / 6; if (SeaIceField.Inside(e, nn, p, seed) == SeaIceField.PackInside(e, nn, p, seed)) same++; }
        Check(same == 3000, "60 % and above: the pack field unchanged (" + same + "/3000)");
        // continuity (the mesher contours it): neighbours 0.5 m apart differ by little
        double worst = 0;
        for (int i = 0; i < 20000; i++) { double e = 3 + i * 0.00731, nn = -2 + i * 0.00513; worst = Math.Max(worst, Math.Abs(SeaIceFloes.QStar(e * 1000, nn * 1000, seed) - SeaIceFloes.QStar(e * 1000 + 0.5, nn * 1000, seed))); }
        Check(worst < 0.1, "the floe scalar is continuous (worst step " + F(worst) + " over 0.5 m)");
        // separate floes: at 35 % no piece holds a tenth of the ice, at 51 % (in the blend) a fifth; the pack field: over 40 %
        foreach (double p in new[] { 0.35, 0.51 })
        {
            Pieces(p, 500, 8, (e, nn) => SeaIceField.IsIce(e, nn, p, seed), out int count, out double largest, out double median);
            Pieces(p, 500, 8, (e, nn) => SeaIceField.PackInside(e, nn, p, seed) > 0, out int oldCount, out double oldLargest, out _);
            Check(count > 500 && largest < (p < 0.4 ? 0.1 : 0.2) && median > 15 && median < 80 && oldLargest > 0.4, p + ": " + count + " floes in 16 km2, median " + F(median) + " m across, the largest " + F(largest) + " of the ice (pack field: " + oldCount + " pieces, the largest " + F(oldLargest) + ")");
        }
        // deterministic and world-anchored; another date, another pattern
        int diff = 0;
        for (int i = 0; i < 400; i++) if (SeaIceField.IsIce(i * 0.21, i * 0.13, 0.4, seed) != SeaIceField.IsIce(i * 0.21, i * 0.13, 0.4, SeaIceField.SeedOf(20290116))) diff++;
        Check(SeaIceField.IsIce(3.3, 4.4, 0.4, seed) == SeaIceField.IsIce(3.3, 4.4, 0.4, seed) && diff > 100, "floes deterministic; a new date, new floes (" + diff + "/400)");
        // configuration: the pack field never starts above the heavy-ice percent; bad values fall back
        string note = SeaIceFloes.Configure(true, 50, 75, 60, 60);
        Check(SeaIceFloes.PackPercent == 60 && SeaIceFloes.FullPercent == 50 && note.Contains("heavy"), "pack field capped at the submarine rule's heavy ice");
        SeaIceFloes.Configure(true, 58, 60, 999, 60);
        Check(SeaIceFloes.FullPercent <= 56 && SeaIceFloes.PushM == SeaIceFloes.DefaultPushM, "band at least " + SeaIceFloes.MinGapPercent + " % wide; push 0-150 m");
        SeaIceFloes.Configure(false, double.NaN, double.NaN, double.NaN, 60);
        Check(SeaIceFloes.PackWeight(0.3) == 1 && SeaIceField.Inside(1.1, 2.2, 0.3, seed) == SeaIceField.PackInside(1.1, 2.2, 0.3, seed) && SeaIceFloes.PushReachM == 0, "SeaIceFloeField=0: the pack field everywhere, no push reach");
        SeaIceFloes.Configure(true, double.NaN, double.NaN, double.NaN, 60);
        Check(SeaIceFloes.FullPercent == 44 && SeaIceFloes.PackPercent == 60 && SeaIceFloes.PushM == 60, "defaults 44 / 60 % / 60 m");
        // the mesher: near chunks with drift ice contour floes at FloeCells, closed; far chunks and heavy pack as before
        var spec = new IceChunkSpec { CentreEastKm = 0.5, CentreNorthKm = 0.5, SizeKm = 1, Cells = 32, Underside = true, FreeboardM = 0.5, DraftM = 2, RidgeM = 1.2, EdgePercent = 15, Seed = seed, Detail = true, FloeCells = 64 };
        foreach (double pct in new[] { 25.0, 51.0 })
        {
            var m = IceMesher.Build(spec, (e, nn) => pct);
            Check(m.Floes && m.Grid == 64 && m.Vertices.Length / 3 < 65000 && m.Triangles.All(t => t >= 0 && t < m.Vertices.Length / 3), pct + " %: floe chunk at 64 cells, " + m.Vertices.Length / 3 + " vertices (16-bit), " + m.TriangleCount + " triangles");
            Closed(m.Vertices, m.Triangles, "floe chunk " + pct + " %", out _);
            Normals(m.Vertices, m.Normals, m.Triangles, "floe chunk " + pct + " % (16 m cells, ridged slivers along many contours: same side)", 0.02);
        }
        var far = spec; far.Detail = false;
        var heavyNear = IceMesher.Build(spec, (e, nn) => 95);
        var heavyFar = IceMesher.Build(far, (e, nn) => 95);
        Check(!heavyNear.Floes && heavyNear.Grid == 32 && heavyNear.Vertices.SequenceEqual(heavyFar.Vertices) && heavyNear.Triangles.SequenceEqual(heavyFar.Triangles), "95 %: the near chunk is the pack mesh as before (no floes, 32 cells)");
        var farMid = IceMesher.Build(far, (e, nn) => 40);
        Check(!farMid.Floes && farMid.Grid == 32, "far chunks keep the pack field (their cells cannot show floes)");
        Check(IceMesher.Build(spec, (e, nn) => e < 0.5 ? 5 : 90).Floes == false && IceMesher.Build(spec, (e, nn) => e < 0.5 ? 5 : 40).Floes, "a chunk draws floes when any drawn part of it is drift ice");
        // channels: small floes whose centre the channel covers go whole; floes away from it stay
        var cut = new IceCarve(45);
        for (int k = 0; k <= 160; k++) cut.Record(3, 0.1 + k * 0.005, 0.5 + k * 0.001, k, 30);
        var cs = cut.Snapshot();
        var plain = IceMesher.Build(spec, (e, nn) => 40);
        var cspec = spec; cspec.Carve = cs; cspec.Cells = 64;
        var carved = IceMesher.Build(cspec, (e, nn) => 40);
        Check(carved.PushedFloes > 3 && carved.Grid == plain.Grid, "40 % with a channel: " + carved.PushedFloes + " floes pushed out whole, same 64 cells as before the channel");
        int farChanged = 0, farCells = 0;
        for (int j = 0; j < 64; j++)
            for (int i = 0; i < 64; i++)
            {
                double ce = (i + 0.5) / 64, cn = (j + 0.5) / 64, dist = Math.Abs((ce - 0.1) * 0.16 - (cn - 0.5) * 0.8) / Math.Sqrt(0.8 * 0.8 + 0.16 * 0.16) * 1000;
                if (dist < 60 + SeaIceFloes.PushReachM + 20) continue;
                farCells++;
                if (plain.Solid[j * 64 + i] != carved.Solid[j * 64 + i]) farChanged++;
            }
        Check(farCells > 1000 && farChanged == 0, "nothing changes more than a pushed floe's reach from the track (" + farChanged + " of " + farCells + " cells)");
        int inside = 0;
        for (int k = 0; k < carved.Triangles.Length; k += 3)
        {
            int a = carved.Triangles[k] * 3, b = carved.Triangles[k + 1] * 3, q = carved.Triangles[k + 2] * 3;
            if (carved.Vertices[a + 1] < 0 || carved.Vertices[b + 1] < 0 || carved.Vertices[q + 1] < 0) continue;
            double ce = 0.5 + (carved.Vertices[a] + carved.Vertices[b] + carved.Vertices[q]) / 3000, cn = 0.5 + (carved.Vertices[a + 2] + carved.Vertices[b + 2] + carved.Vertices[q + 2]) / 3000;
            double dist = Math.Abs((ce - 0.1) * 0.16 - (cn - 0.5) * 0.8) / Math.Sqrt(0.8 * 0.8 + 0.16 * 0.16) * 1000;
            if (ce > 0.15 && ce < 0.85 && dist < 10) inside++;
        }
        Check(inside == 0, "no floe top within 10 m of the track (" + inside + ")");
        Closed(carved.Vertices, carved.Triangles, "floe chunk with a channel", out _);
        // the neighbour chunk decides the same floes (one snapshot, one decision per floe)
        // two chunk builds whose own (lattice) fractions differ still make the same decision for every floe:
        // the decision is taken at the floe's centre from the model's fraction, never from the sample's
        Func<double, double, double> model = (e, nn) => 0.36 + 0.08 * e;
        var p1 = new SeaIceFloes.Push(cs, 60, seed, model); var p2 = new SeaIceFloes.Push(cs, 60, seed, model);
        int agree = 0;
        for (int i = 0; i < 4000; i++) { double e = (i % 80) * 0.0125, nn = 0.3 + (i / 80) * 0.008; if ((SeaIceFloes.Inside(e, nn, 0.38, seed, p1) > 0) == (SeaIceFloes.Inside(e, nn, 0.38, seed, p2) > 0)) agree++; SeaIceFloes.Inside(e, nn, 0.42, seed, p2); }
        int same2 = 0, asked = 0, pushedHere = 0;
        for (int lv = 0; lv < 3; lv++)
        {
            double L = SeaIceFloes.CellM[lv];
            for (int j = (int)Math.Floor(300 / L); j <= (int)Math.Floor(700 / L); j++)
                for (int i = 0; i <= (int)Math.Floor(1000 / L); i++) { var fl = SeaIceFloes.Candidate(lv, i, j, seed); asked++; bool a1 = p1.Pushed(fl); if (a1 == p2.Pushed(fl)) same2++; if (a1) pushedHere++; }
        }
        Check(agree == 4000 && same2 == asked && pushedHere > 3 && cs.TouchesNear(1, 0) && !cs.TouchesNear(3, 3), "push decisions agree between chunk builds at different local fractions (" + same2 + "/" + asked + ", " + pushedHere + " pushed); a chunk next to a channel takes the carve along");
        // in the blend (51 %) too: pushed floes go whole and nothing changes beyond their reach
        var plain51 = IceMesher.Build(spec, (e, nn) => 51);
        var carved51 = IceMesher.Build(cspec, (e, nn) => 51);
        int far51 = 0, cells51 = 0;
        for (int j = 0; j < 64; j++)
            for (int i = 0; i < 64; i++)
            {
                double ce = (i + 0.5) / 64, cn = (j + 0.5) / 64, dist = Math.Abs((ce - 0.1) * 0.16 - (cn - 0.5) * 0.8) / Math.Sqrt(0.8 * 0.8 + 0.16 * 0.16) * 1000;
                if (dist < 60 + SeaIceFloes.PushReachM + 20) continue;
                cells51++;
                if (plain51.Solid[j * 64 + i] != carved51.Solid[j * 64 + i]) far51++;
            }
        Check(carved51.Floes && carved51.PushedFloes > 0 && cells51 > 1000 && far51 == 0, "51 % (blend) with a channel: " + carved51.PushedFloes + " floes pushed, " + far51 + " of " + cells51 + " cells beyond the reach changed");
        Closed(carved51.Vertices, carved51.Triangles, "floe chunk 51 % with a channel", out _);
        // dirty marks reach the pushed floes' extent
        var near = new IceCarve(45);
        for (int k = 0; k <= 8; k++) near.Record(1, 0.2 + k * 0.03, 0.95, 10 + k, 30);
        near.Snapshot();
        var nd = near.TakeDirty(10);
        Check(nd.Contains(IceCarve.ChunkKey(0, 1)) && nd.Contains(IceCarve.ChunkKey(0, 0)), "a channel 50 m from a chunk border marks the next chunk too (push reach " + F(SeaIceFloes.PushReachM) + " m)");
        // fail closed: a calibration that throws switches floes off (the pack field everywhere) with a note
        SeaIceFloes.FailCalibrationForTests = true; SeaIceFloes.ResetCalibration();
        bool warmed = SeaIceFloes.Warm();
        Check(!warmed && !SeaIceFloes.On && SeaIceFloes.FailedNote.Contains("forced") && SeaIceField.Inside(1.1, 2.2, 0.3, seed) == SeaIceField.PackInside(1.1, 2.2, 0.3, seed)
            && IceMesher.Build(spec, (e, nn) => 30).Floes == false, "a failed floe calibration: floes off, the pack field everywhere, the note kept (" + SeaIceFloes.FailedNote + ")");
        SeaIceFloes.FailCalibrationForTests = false; SeaIceFloes.ResetCalibration();
        SeaIceFloes.Configure(true, double.NaN, double.NaN, double.NaN, 60);
        Check(SeaIceFloes.Warm() && SeaIceFloes.On && SeaIceFloes.FailedNote.Length == 0, "the next install calibrates again");
        Console.WriteLine("floes: share, sizes, blend, pack unchanged from 60 %, closed floe chunks, channel push, fail closed checked");
    }

    // Connected ice pieces on an N x N grid of cellM metres from (0, 0): count, largest share of the ice, median diameter (m).
    static void Pieces(double p, int N, double cellM, Func<double, double, bool> ice, out int count, out double largest, out double median)
    {
        var g = new bool[N * N];
        for (int j = 0; j < N; j++) for (int i = 0; i < N; i++) g[j * N + i] = ice(i * cellM / 1000, j * cellM / 1000);
        var seen = new bool[N * N]; var areas = new List<int>(); var st = new Stack<int>();
        for (int k = 0; k < N * N; k++)
        {
            if (!g[k] || seen[k]) continue;
            int a = 0; st.Push(k); seen[k] = true;
            while (st.Count > 0)
            {
                int c = st.Pop(); a++; int ci = c % N, cj = c / N;
                if (ci > 0 && g[c - 1] && !seen[c - 1]) { seen[c - 1] = true; st.Push(c - 1); }
                if (ci < N - 1 && g[c + 1] && !seen[c + 1]) { seen[c + 1] = true; st.Push(c + 1); }
                if (cj > 0 && g[c - N] && !seen[c - N]) { seen[c - N] = true; st.Push(c - N); }
                if (cj < N - 1 && g[c + N] && !seen[c + N]) { seen[c + N] = true; st.Push(c + N); }
            }
            areas.Add(a);
        }
        count = areas.Count;
        largest = areas.Count > 0 ? (double)areas.Max() / areas.Sum() : 0;
        var d = areas.Select(a => 2 * Math.Sqrt(a * cellM * cellM / Math.PI)).OrderBy(x => x).ToList();
        median = d.Count > 0 ? d[d.Count / 2] : 0;
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

    // ---- 8: ship effects ------------------------------------------------------------------------

    // The sheet's material values: matt, albedo 0.75-0.85 by default, configurable within bounds.
    static void Look()
    {
        Check(IceLook.Albedo("") == 0.80 && IceLook.Albedo("0.7") == 0.7 && IceLook.Albedo("1.5") == 0.80 && IceLook.Albedo("abc") == 0.80 && IceLook.Albedo("0.95") == 0.95 && IceLook.Albedo("0.49") == 0.80, "SeaIceAlbedo: default 0.80, 0.5-0.95 accepted, anything else the default");
        Check(IceLook.Smoothness("") == 0.12 && IceLook.Smoothness("0.2") == 0.2 && IceLook.Smoothness("0.9") == 0.12 && IceLook.Smoothness("-1") == 0.12, "SeaIceSmoothness: default 0.12, at most 0.4 (never a mirror)");
        Check(IceLook.DefaultAlbedo >= 0.75 && IceLook.DefaultAlbedo <= 0.85 && IceLook.Matt(IceLook.DefaultSmoothness, 0) && !IceLook.Matt(0.9, 0) && !IceLook.Matt(0.1, 1), "defaults are matt snow/ice: albedo 0.75-0.85, smoothness <= 0.25, metallic 0");
        foreach (double alb in new[] { 0.6, 0.8, 0.9 })
        {
            IceLook.Colour(alb, out double r, out double g, out double b);
            // mean drawn albedo: colour x mean texture value
            double mean = (r + g + b) / 3 * IceLook.TextureMean;
            Check(Math.Abs(mean - alb * (IceLook.Tint[0] + IceLook.Tint[1] + IceLook.Tint[2]) / 3) < 1e-9 && Math.Abs(g * IceLook.TextureMean - alb * IceLook.Tint[1]) < 1e-9, "the texture mean is divided out: drawn mean albedo " + F(mean) + " for " + alb);
            Check(b >= g && g >= r && b - r < 0.06, "faint blue tint (" + F(r) + "/" + F(g) + "/" + F(b) + ")");
        }
        byte lo = IceLook.TextureByte(0), hi = IceLook.TextureByte(1);
        Check(lo == (byte)Math.Round(255 * 0.88) && hi == 255 && IceLook.TextureByte(-3) == lo && IceLook.TextureByte(7) == hi, "noise texture 0.88..1.00, clamped");
        Check(IceLook.Shaders[0] == "Legacy Shaders/Diffuse" && Array.IndexOf(IceLook.Shaders, "Diffuse") < Array.IndexOf(IceLook.Shaders, "Standard") && Array.IndexOf(IceLook.Shaders, "Standard") < Array.IndexOf(IceLook.Shaders, "Unlit/Texture"), "Lambert first (no Fresnel or reflections), Standard (made matt) next, unlit last");
        Check(IceLook.StandardMattKeywords.Contains("_SPECULARHIGHLIGHTS_OFF") && IceLook.StandardMattKeywords.Contains("_GLOSSYREFLECTIONS_OFF"), "Standard: highlights and environment reflections off");
        Check(IceLook.IsUnlit("Unlit/Texture") && IceLook.IsUnlit("Hidden/Internal-Colored") && !IceLook.IsUnlit("Diffuse") && IceLook.UnlitScale < 1, "unlit fallbacks are drawn darker (they cannot follow the sun)");
        Console.WriteLine("material: albedo " + IceLook.DefaultAlbedo + ", smoothness " + IceLook.DefaultSmoothness + ", shaders " + string.Join(" > ", IceLook.Shaders));
    }

    // Closed manifold: every directed edge (by position) is matched by its reverse.
    static void Closed(float[] v, int[] t, string what, out int edges)
    {
        Func<int, string> key = i => Math.Round(v[i * 3], 3).ToString(CultureInfo.InvariantCulture) + "," + Math.Round(v[i * 3 + 1], 3).ToString(CultureInfo.InvariantCulture) + "," + Math.Round(v[i * 3 + 2], 3).ToString(CultureInfo.InvariantCulture);
        var count = new Dictionary<string, int>();
        for (int k = 0; k < t.Length; k += 3)
            for (int e = 0; e < 3; e++)
            {
                string a = key(t[k + e]), b = key(t[k + (e + 1) % 3]);
                if (a == b) continue; // a degenerate edge
                string d = a + ">" + b;
                count[d] = count.TryGetValue(d, out int c) ? c + 1 : 1;
            }
        int open = 0;
        foreach (var kv in count)
        {
            var parts = kv.Key.Split('>');
            count.TryGetValue(parts[1] + ">" + parts[0], out int back);
            if (back != kv.Value) open++;
        }
        edges = count.Count;
        Check(open == 0, what + ": watertight (" + open + " unmatched directed edges of " + count.Count + ")");
    }

    // Unit normals that agree with each triangle's front face (Unity: cross(b - a, c - a)).
    static void Normals(float[] v, float[] n, int[] t, string what, double minDot)
    {
        Check(n.Length == v.Length, what + ": one normal per vertex");
        for (int i = 0; i < n.Length; i += 3) Check(Math.Abs(Math.Sqrt(n[i] * n[i] + n[i + 1] * n[i + 1] + n[i + 2] * n[i + 2]) - 1) < 1e-4, what + ": unit normals");
        int bad = 0, faces = 0;
        double worst = 1;
        for (int k = 0; k < t.Length; k += 3)
        {
            int a = t[k] * 3, b = t[k + 1] * 3, c = t[k + 2] * 3;
            double ux = v[b] - v[a], uy = v[b + 1] - v[a + 1], uz = v[b + 2] - v[a + 2], wx = v[c] - v[a], wy = v[c + 1] - v[a + 1], wz = v[c + 2] - v[a + 2];
            double fx = uy * wz - uz * wy, fy = uz * wx - ux * wz, fz = ux * wy - uy * wx, fl = Math.Sqrt(fx * fx + fy * fy + fz * fz);
            if (fl < 1e-9) continue;
            faces++;
            foreach (int q in new[] { a, b, c })
            {
                double dot = (fx * n[q] + fy * n[q + 1] + fz * n[q + 2]) / fl;
                worst = Math.Min(worst, dot);
                if (dot < minDot) bad++;
            }
        }
        Check(bad == 0 && faces > 0, what + ": normals face the same way as the winding (worst dot " + F(worst) + ", " + bad + " bad of " + faces * 3 + ")");
    }

    static void Slab()
    {
        uint seed = SeaIceField.SeedOf(20290310);
        int checkedChunks = 0;
        foreach (double pct in new[] { 95.0, 50.0, 25.0 })
            foreach (var at in new[] { new[] { 0.5, 0.5 }, new[] { 3.5, -1.5 } })
            {
                var spec = new IceChunkSpec { CentreEastKm = at[0], CentreNorthKm = at[1], SizeKm = 1, Cells = 32, Underside = true, FreeboardM = 0.5, DraftM = 2, RidgeM = 1.2, EdgePercent = 15, Seed = seed };
                var m = IceMesher.Build(spec, (e, n) => pct);
                Closed(m.Vertices, m.Triangles, "closed slab " + pct + " % at " + at[0] + "," + at[1], out _);
                Normals(m.Vertices, m.Normals, m.Triangles, "closed slab " + pct + " %", 0.3);
                bool iceOnBorder = false;
                for (int i = 0; i < m.Vertices.Length; i += 3) if (m.Vertices[i + 1] >= 0.5f - 1e-4 && (Math.Abs(Math.Abs(m.Vertices[i]) - 500) < 1e-3 || Math.Abs(Math.Abs(m.Vertices[i + 2]) - 500) < 1e-3)) iceOnBorder = true;
                Check((m.BorderWalls > 0) == iceOnBorder && (pct > 90 || m.ContourWalls > 0) && (pct < 50 || m.BorderWalls > 0), "walls along the contour (" + m.ContourWalls + ") and wherever the top reaches the chunk border (" + m.BorderWalls + ")");
                // walls are one-sided now: no triangle repeats another with the opposite winding at the same place
                var seen = new HashSet<string>();
                int twins = 0;
                for (int k = 0; k < m.Triangles.Length; k += 3)
                {
                    var keyPts = new[] { m.Triangles[k], m.Triangles[k + 1], m.Triangles[k + 2] }.Select(i => Math.Round(m.Vertices[i * 3], 3) + ";" + Math.Round(m.Vertices[i * 3 + 1], 3) + ";" + Math.Round(m.Vertices[i * 3 + 2], 3)).OrderBy(x => x, StringComparer.Ordinal);
                    if (!seen.Add(string.Join("|", keyPts))) twins++;
                }
                Check(twins == 0, "no double-sided wall pairs (" + twins + ")");
                checkedChunks++;
            }
        // an edge through the chunk and a far 16 km chunk: closed too, far normals straight up on top
        var edge = IceMesher.Build(new IceChunkSpec { CentreEastKm = 0.5, CentreNorthKm = 0.5, SizeKm = 1, Cells = 32, Underside = true, FreeboardM = 0.5, DraftM = 2, RidgeM = 1.2, EdgePercent = 15, Seed = seed }, (e, n) => e < 0.5 ? 5 : 90);
        Closed(edge.Vertices, edge.Triangles, "closed slab across the ice edge", out _);
        var far = IceMesher.Build(new IceChunkSpec { CentreEastKm = 8, CentreNorthKm = 8, SizeKm = 16, Cells = 32, Underside = true, FlatNormals = true, FreeboardM = 0.5, DraftM = 3.5, RidgeM = 0.6, EdgePercent = 15, Seed = seed }, (e, n) => 70);
        Closed(far.Vertices, far.Triangles, "far chunk slab", out _);
        Normals(far.Vertices, far.Normals, far.Triangles, "far chunk", 0.3);
        int upTop = 0, tops = 0;
        for (int i = 0; i < far.Vertices.Length; i += 3) if (far.Vertices[i + 1] >= 0.5f - 1e-4 && far.Normals[i + 1] != 0f) { tops++; if (far.Normals[i + 1] == 1f && far.Normals[i] == 0f && far.Normals[i + 2] == 0f) upTop++; }
        Check(tops > 1000 && upTop == tops, "far chunk tops have straight-up normals (" + upTop + " of " + tops + "; the rest of the top-height vertices are wall edges, normals horizontal)");
        float farMin = far.Vertices.Where((x, i) => i % 3 == 1).Min();
        Check(Math.Abs(farMin + 3.5) < 1e-4, "far slab 3.5 m thick under the top");
        var heavy = IceMesher.Build(new IceChunkSpec { CentreEastKm = 0.5, CentreNorthKm = 0.5, SizeKm = 1, Cells = 64, Underside = true, FreeboardM = 0.5, DraftM = 2, RidgeM = 1.2, EdgePercent = 15, Seed = seed }, (e, n) => 95);
        Check(heavy.Vertices.Length / 3 < 200000 && heavy.Grid == 64 && heavy.Solid.Length == 64 * 64, "64-cell chunk: " + heavy.Vertices.Length / 3 + " vertices, " + heavy.TriangleCount + " triangles");
        // ocean clip mask: inside the solid ice only, eroded
        var solid = Enumerable.Repeat(true, 16 * 16).ToArray();
        Check(IceMesher.ClipMask(solid, 16, 1).All(x => x), "solid chunk: all clipped (the border wall closes the chunk edge)");
        solid[5 * 16 + 5] = false;
        var mask = IceMesher.ClipMask(solid, 16, 1);
        Check(!mask[5 * 16 + 5] && !mask[4 * 16 + 4] && !mask[6 * 16 + 6] && !mask[5 * 16 + 6] && mask[5 * 16 + 7] && mask[3 * 16 + 5], "one open cell: it and its neighbours are not clipped");
        var mid = IceMesher.Build(new IceChunkSpec { CentreEastKm = 0.5, CentreNorthKm = 0.5, SizeKm = 1, Cells = 32, Underside = true, FreeboardM = 0.5, DraftM = 2, RidgeM = 1.2, EdgePercent = 15, Seed = seed }, (e, n) => 50);
        var midMask = IceMesher.ClipMask(mid.Solid, mid.Grid, 1);
        Check(midMask.Count(x => x) > 0 && midMask.Select((x, i) => !x || mid.Solid[i]).All(x => x) && midMask.Count(x => x) < mid.Solid.Count(x => x), "50 %: the clip lies strictly inside the solid ice (" + midMask.Count(x => x) + " of " + mid.Solid.Count(x => x) + " solid cells)");
        Check(IceMesher.ClipMask(null, 4, 1).Length == 16 && IceMesher.ClipMask(new bool[3], 4, 1).All(x => !x), "no mask: nothing clipped");
        // the broken-piece prism
        IcePieceMesh.Build(7, 0x51CEu, out float[] pv, out float[] pn, out int[] pt);
        Closed(pv, pt, "bow piece prism", out _);
        Normals(pv, pn, pt, "bow piece prism", 0.99);
        Check(pv.Where((x, i) => i % 3 == 1).Max() == IcePieceMesh.Top && pv.Where((x, i) => i % 3 == 1).Min() == IcePieceMesh.Bottom, "piece floats a fifth above the water");
        Console.WriteLine("slab: " + checkedChunks + " near chunks, an edge chunk, a far chunk and the piece mesh are closed with consistent normals");
    }

    static void Channels()
    {
        var c = new IceCarve(45);
        Check(c.RefreezeS == 2700 && new IceCarve(1).RefreezeS == 2700 && new IceCarve(60).RefreezeS == 3600, "SeaIceCarveMinutes: 45 by default, 5-240 accepted");
        Check(IceCarve.HalfWidthM(30) == 22.5 && IceCarve.HalfWidthM(8) == IceCarve.MinHalfM && IceCarve.HalfWidthM(200) == IceCarve.MaxHalfM && IceCarve.HalfWidthM(double.NaN) == IceCarve.MinHalfM, "half width 1.5 x beam / 2, within 16-60 m");
        // a 30 m beam ship eastward along north 0.5 km, 5 m/s, sampled each second
        double t = 1000;
        for (int k = 0; k <= 120; k++) c.Record(7, 0.2 + k * 0.005, 0.5, t + k, 30);
        double tEnd = t + 120;
        int segCount = c.Count;
        Check(segCount >= 20 && segCount <= 24 && c.Tracking == 1, "a point every 25 m (sampled every 5 m): 20-24 segments over 600 m (" + segCount + ")");
        var snap = c.Snapshot();
        Check(ReferenceEquals(snap, c.Snapshot()), "the snapshot is cached until the carve changes");
        Check(snap.Field(0.5, 0.5) < -0.5 && snap.Field(0.5, 0.5 + 0.0225 * 1.4) > 0 && snap.Field(0.5, 0.5 + 0.015) < 0 && double.IsPositiveInfinity(snap.Field(3, 3)), "open on the track, ice beyond 1.3 x half width, nothing far away");
        // ragged edges: the channel width varies along the track around 1.5 x beam
        var widths = new List<double>();
        for (double e = 0.25; e <= 0.75; e += 0.01)
        {
            double up = 0, down = 0;
            for (double d = 0; d < 0.08; d += 0.0005) { if (snap.Field(e, 0.5 + d) < 0) up = d; if (snap.Field(e, 0.5 - d) < 0) down = d; }
            widths.Add((up + down) * 1000);
        }
        double meanW = widths.Average(), sd = Math.Sqrt(widths.Select(w => (w - meanW) * (w - meanW)).Average());
        Check(Math.Abs(meanW - 45) < 9 && sd > 1.5 && widths.Min() > 45 * 0.65 && widths.Max() < 45 * 1.35, "channel about 1.5 x beam wide (mean " + F(meanW) + " m), ragged (sd " + F(sd) + " m, " + F(widths.Min()) + "-" + F(widths.Max()) + " m)");
        Console.WriteLine("  channel: mean width " + F(meanW) + " m for a 30 m beam, sd " + F(sd) + " m");
        // openness for a follower and for the ship itself
        Check(snap.OpennessAt(0.5, 0.5) == 1 && snap.OpennessAt(0.5, 0.6) == 0, "fresh channel: openness 1 on the track, 0 off it");
        Check(snap.OpennessAt(0.5, 0.5, 7, tEnd - IceCarve.OwnGraceS) == 0 && snap.OpennessAt(0.5, 0.5, 8, tEnd - IceCarve.OwnGraceS) == 1, "the ship's own fresh track does not ease it; another ship's does");
        // the speed rule in a channel (class none, flank 30 kn)
        var lead = new IceSpeedState(); var follow = new IceSpeedState();
        float vLead = lead.Cap(28, 30, 65, 66, 0), vFollow = follow.Cap(28, 30, IceCarve.EffectivePercent(65, 1), IceCarve.EffectivePercent(66, 1), 0);
        Check(Math.Abs(vLead - 3) < 1e-4 && Math.Abs(vFollow - 21) < 1e-4, "65 % pack: the leader breaks ice at steerage way (" + vLead + " kn), a ship following in its fresh channel runs at caution speed (" + vFollow + " kn)");
        Check(Math.Abs(IceCarve.EffectivePercent(60, 1) - 12) < 1e-9 && IceCarve.EffectivePercent(60, 0) == 60 && Math.Abs(IceCarve.EffectivePercent(60, 0.5) - 36) < 1e-9 && double.IsNaN(IceCarve.EffectivePercent(double.NaN, 1)), "channel relief: c x (1 - 0.8 x openness)");
        var half = new IceSpeedState();
        Check(Math.Abs(half.Cap(28, 30, IceCarve.EffectivePercent(65, 0.5), 66, 0) - 12) < 1e-4, "a half-refrozen channel: restricted speed (12 kn)");
        // the review's case: 90 % pack, a channel refrozen to openness 0.25 (90 -> 72 %, still blocked), the
        // lightest ice ahead 80 %: 'ahead' is eased like 'here', so the escape speed (0.4 x flank) is kept
        var trapped = new IceSpeedState();
        float vTrapped = IceCarve.CapInChannel(trapped, 28, 30, 90, 80, 0, 90, 0.25);
        Check(trapped.State == IceAccess.Blocked && Math.Abs(vTrapped - 12) < 1e-4 && trapped.Escaping && !trapped.SteerageOnly, "blocked in a refreezing channel with lighter ice ahead: escape at 0.4 x flank (" + vTrapped + " kn), as without the channel");
        float vRaw = new IceSpeedState().Cap(28, 30, 90, 80, 0, 90);
        float vMixed = new IceSpeedState().Cap(28, 30, IceCarve.EffectivePercent(90, 0.25), 80, 0, IceCarve.EffectivePercent(90, 0.25));
        Check(vRaw == vTrapped && Math.Abs(vMixed - 3) < 1e-4, "without the channel the same 12 kn; comparing an eased 'here' with a raw 'ahead' (the defect) would give steerage way, " + vMixed + " kn");
        Check(IceCarve.CapInChannel(new IceSpeedState(), 28, 30, 90, 95, 0, 90, 0.25) == new IceSpeedState().Cap(28, 30, 90, 95, 0, 90) && IceCarve.CapInChannel(new IceSpeedState(), 28, 30, 65, 66, 0, 65.5, 0) == new IceSpeedState().Cap(28, 30, 65, 66, 0, 65.5), "heavier ice ahead stays steerage way in a channel too; openness 0 is the plain rule");
        Check(Math.Abs(IceCarve.CapInChannel(new IceSpeedState(), 28, 30, 65, 66, 0, 65, 1) - 21) < 1e-4, "a fresh channel through 65 % pack: caution speed (21 kn)");
        // dirty chunks: only the 1 km chunk the channel lies in
        var dirty = c.TakeDirty(100);
        Check(dirty.Count == 1 && dirty[0] == IceCarve.ChunkKey(0, 0) && c.DirtyCount == 0, "new segments mark only the chunk they touch (" + dirty.Count + ")");
        var border = new IceCarve(45);
        for (int k = 0; k <= 8; k++) border.Record(1, 0.98 + k * 0.005, 1.99, 10 + k, 30);
        Check(border.TakeDirty(10).Count == 0 && border.DirtyCount == 4, "dirty chunks wait until their change is published (a rebuild before would miss the channel)");
        Check(border.Publish(100) && !border.Publish(100.1) && border.Publishes == 1, "published once; nothing new: no second build");
        var bd = border.TakeDirty(1);
        Check(bd.Count == 1 && border.DirtyCount == 3, "a track across a chunk corner marks the four chunks it touches; TakeDirty is bounded (" + bd.Count + " taken, " + border.DirtyCount + " left)");
        border.TakeDirty(100);
        // refreeze: nothing before the first step; then steps of 1/12; gone after 45 min
        int v0 = c.Version;
        c.Advance(t + c.StepS * 0.5);
        Check(c.Version == v0 && c.DirtyCount == 0, "no change before the first refreeze step");
        c.Advance(tEnd + c.StepS * 6 + 0.01);
        var s6 = c.Snapshot();
        Check(c.Version > v0 && c.DirtyCount == 1 && Math.Abs(s6.OpennessAt(0.5, 0.5) - 0.5) < 1e-9, "after 6 of 12 steps (22.5 min): openness 0.5, the chunk marked again");
        Check(s6.Field(0.5, 0.5 + 0.0225 * 0.65 * 1.0) > 0 && s6.Field(0.5, 0.5) < 0, "half width halved: ice back at 65 % of the fresh half width");
        c.TakeDirty(100);
        c.Advance(tEnd + c.RefreezeS + 0.01);
        Check(c.Count == 0 && c.Expired == segCount && c.DirtyCount == 1 && c.Snapshot().Count == 0 && c.Snapshot().OpennessAt(0.5, 0.5) == 0, "refrozen after " + c.RefreezeS / 60 + " min of game time: segments gone, chunk rebuilt");
        Check(IceCarve.Openness(0) == 1 && IceCarve.Openness(IceCarve.Steps) == 0 && IceCarve.Openness(3) == 0.75, "openness steps");
        // a jump (respawn, teleport) or a long gap breaks the track; Break() too
        var j = new IceCarve(45);
        j.Record(1, 0, 0, 0, 20); j.Record(1, 3, 0, 1, 20);
        Check(j.Count == 0, "a 3 km jump starts a new track, no segment");
        j.Record(1, 3.05, 0, 2, 20); Check(j.Count == 1, "then carving continues");
        j.Record(1, 3.1, 0, 200, 20); Check(j.Count == 1, "a 3-minute gap starts a new track");
        j.Break(1); j.Record(1, 3.2, 0, 201, 20); Check(j.Count == 1 && j.Tracking == 1, "Break: the next point starts a new track");
        // bounded
        var big = new IceCarve(240);
        for (int k = 0; k < IceCarve.MaxSegments + 600; k++) big.Record(k % 5, (k / 5) * 0.03 + (k % 5) * 50, 0, k / 5, 20);
        Check(big.Count <= IceCarve.MaxSegments && big.Dropped > 0, "at most " + IceCarve.MaxSegments + " segments (" + big.Count + ", " + big.Dropped + " oldest dropped)");
        // the mesher cuts the channel into a 64-cell chunk and stays closed
        var cut = new IceCarve(45);
        for (int k = 0; k <= 160; k++) cut.Record(3, 0.1 + k * 0.005, 0.5 + k * 0.001, k, 30);
        var cs = cut.Snapshot();
        Check(cs.Touches(0, 0) && !cs.Touches(1, 1) && cs.Cells > 0, "the snapshot knows which chunks a channel reaches");
        uint seed = SeaIceField.SeedOf(20290310);
        var spec = new IceChunkSpec { CentreEastKm = 0.5, CentreNorthKm = 0.5, SizeKm = 1, Cells = 64, Underside = true, FreeboardM = 0.5, DraftM = 2, RidgeM = 1.2, EdgePercent = 15, Seed = seed };
        var plain = IceMesher.Build(spec, (e, n) => 95);
        spec.Carve = cs;
        var carved = IceMesher.Build(spec, (e, n) => 95);
        Check(carved.CarvedCells > 50 && carved.IceCells < plain.IceCells && plain.CarvedCells == 0, "95 % with a channel: " + carved.CarvedCells + " grid points opened, ice cells " + plain.IceCells + " -> " + carved.IceCells);
        int inside = 0;
        for (int k = 0; k < carved.Triangles.Length; k += 3)
        {
            int a = carved.Triangles[k] * 3, b = carved.Triangles[k + 1] * 3, q = carved.Triangles[k + 2] * 3;
            if (carved.Vertices[a + 1] < 0 || carved.Vertices[b + 1] < 0 || carved.Vertices[q + 1] < 0) continue;
            double ce = 0.5 + (carved.Vertices[a] + carved.Vertices[b] + carved.Vertices[q]) / 3000, cn = 0.5 + (carved.Vertices[a + 2] + carved.Vertices[b + 2] + carved.Vertices[q + 2]) / 3000;
            // distance to the track line (0.1, 0.5) -> (0.9, 0.66) in metres
            double tx = 0.8, ty = 0.16, tl = Math.Sqrt(tx * tx + ty * ty), dist = Math.Abs((ce - 0.1) * ty - (cn - 0.5) * tx) / tl * 1000;
            if (ce > 0.15 && ce < 0.85 && dist < 10) inside++;
        }
        Check(inside == 0, "no ice top within 10 m of the track (" + inside + " triangles)");
        Closed(carved.Vertices, carved.Triangles, "carved slab", out _);
        Normals(carved.Vertices, carved.Normals, carved.Triangles, "carved slab (16 m cells with ridges: steep facets, same side)", 0.05);
        // floating origin: the carve is in the battle frame, so recentring Unity changes nothing
        Check(cs.Field(0.5, 0.58) == cut.Snapshot().Field(0.5, 0.58), "geo-anchored (no Unity coordinates in the carve)");
        Snapshots();
        HighCompression();
        Console.WriteLine("channels: geometry, refreeze in " + IceCarve.Steps + " steps over 45 min, dirty chunks, bounds and the speed rule checked");
    }

    // Incremental, throttled snapshots: one snapshot per publish, only changed chunks rebuilt, the same
    // channels as a full build.
    static void Snapshots()
    {
        // ten ships in long tracks over 30 km: about 4000 segments
        var inc = new IceCarve(45); var full = new IceCarve(45);
        var rec = new List<(int u, double e, double n, double t)>();
        for (int k = 0; k < 4100; k++) { int u = k % 10; double step = k / 10; rec.Add((u, step * 0.03 + 0.003 * u, u * 3.0 + 0.2 + 0.05 * Math.Sin(step * 0.05), step * 4)); }
        foreach (var r in rec.Take(4000)) { inc.Record(r.u, r.e, r.n, r.t, 25); full.Record(r.u, r.e, r.n, r.t, 25); }
        var s0 = inc.Snapshot();
        int chunks0 = s0.ChunkCount;
        Check(inc.Count > 3500 && chunks0 > 100, "a large carve: " + inc.Count + " segments over " + chunks0 + " chunks");
        // one ship moves on 25 m: one new segment, one chunk rebuilt, the rest shared
        var r1 = rec[4000];
        inc.Record(r1.u, r1.e, r1.n, r1.t, 25); full.Record(r1.u, r1.e, r1.n, r1.t, 25);
        inc.Record(r1.u, r1.e + 0.03, r1.n, r1.t + 4, 25); full.Record(r1.u, r1.e + 0.03, r1.n, r1.t + 4, 25);
        var s1 = inc.Snapshot();
        Check(!ReferenceEquals(s0, s1) && s1.ChunksBuilt >= 1 && s1.ChunksBuilt <= 4 && s1.ChunksShared >= chunks0 - 4, "a new segment rebuilds only the chunks it reaches (" + s1.ChunksBuilt + " built, " + s1.ChunksShared + " shared of " + s1.ChunkCount + ")");
        // refreeze steps and expiries (the first 800 s of track), published incrementally, read the same as one full build
        inc.Advance(2700 + 800); full.Advance(2700 + 800);
        var a = inc.Snapshot();
        var b = full.Snapshot();
        Check(inc.Expired > 1000 && inc.Expired == full.Expired && full.Publishes == 1 && inc.Publishes == 3, "refrozen segments dropped (" + inc.Expired + "); the full carve built once, the incremental one three times");
        int diff = 0, inside = 0;
        for (double e = 0; e < 13; e += 0.0173)
            for (int u = 0; u < 10; u++)
            {
                double n = u * 3.0 + 0.2 + 0.05 * Math.Sin(e / 0.03 * 0.05) + 0.004 * Math.Sin(e * 17);
                double fa = a.Field(e, n), fb = b.Field(e, n);
                if (!(fa == fb || (double.IsPositiveInfinity(fa) && double.IsPositiveInfinity(fb)))) diff++;
                if (a.OpennessAt(e, n) != b.OpennessAt(e, n)) diff++;
                if (fa < 0) inside++;
            }
        Check(diff == 0 && inside > 300 && a.Count == b.Count && a.Cells == b.Cells && a.ChunkCount == b.ChunkCount, "incremental snapshots equal a full build after new segments and refreeze steps (" + inside + " points in channels, " + diff + " differences, " + a.Cells + " cells)");
        // throttle: at most one build per MinPublishS of real time; the speed rule reads the published one
        var th = new IceCarve(45);
        double real = 50, tt = 0;
        int builds = 0;
        for (int f = 0; f < 600; f++) // 10 s of real time at 60 fps, a segment every frame (high time compression)
        {
            real += 1.0 / 60; tt += 16;
            th.Record(1, f * 0.05, 0.5, tt, 30, 16);
            if (th.Publish(real)) builds++;
        }
        Check(builds <= 10 / IceCarve.MinPublishS + 1 && builds >= 10 / IceCarve.MinPublishS - 4 && th.Count > 500, "a segment every frame for 10 s: " + builds + " snapshots built (at most one per " + IceCarve.MinPublishS + " s), not " + th.Count);
        Check(th.Published.Count <= th.Count && th.Count - th.Published.Count <= 16, "the published snapshot lags by at most one throttle period (" + (th.Count - th.Published.Count) + " segments)");
        Console.WriteLine("  snapshots: " + s0.Count + " segments over " + chunks0 + " chunks; a new segment rebuilt " + s1.ChunksBuilt + " and shared " + s1.ChunksShared + "; a segment every frame for 10 s: " + builds + " builds");
    }

    // Game time at high compression: a frame spans up to minutes of game time.
    static void HighCompression()
    {
        Check(IceClock.Recent(1, 0.016) == 1 && IceClock.Recent(1, 83) == 249 && IceClock.Recent(5, double.NaN) == 5 && IceClock.Recent(5, -1) == 5, "recent window: the stated game seconds, or three frames of game time when longer");
        Check(IceClock.Fresh(100, 99.5, 1, 0.016) && !IceClock.Fresh(100, 98, 1, 0.016) && IceClock.Fresh(1000, 917, 1, 83) && !IceClock.Fresh(1000, 1500, 1, 83), "fresh at 1x within a second; at 5000x within three frames; never from the future");
        // 30 kn at 5000x and 30 fps: 166 game seconds and about 2.6 km per frame
        var c = new IceCarve(45);
        double ms = 30 * 0.514444, dtF = 5000 / 30.0;
        for (int f = 0; f <= 10; f++) c.Record(4, f * ms * dtF / 1000, 0.5, 1000 + f * dtF, 20, dtF);
        Check(c.Count == 10 && c.Tracking == 1, "30 kn at 5000x: every frame adds a segment (" + c.Count + "), neither a 'jump' nor a 'gap'");
        var j = new IceCarve(45);
        j.Record(4, 0, 0, 0, 20, dtF); j.Record(4, 60, 0, dtF, 20, dtF);
        Check(j.Count == 0, "a 60 km move in one 166 s frame is still a jump (no 60 km channel)");
        var g = new IceCarve(45);
        g.Record(4, 0, 0, 0, 20, 0.016); g.Record(4, 0.1, 0, 120, 20, 0.016);
        Check(g.Count == 0, "at 1x a 2-minute gap still starts a new track");
        // refreeze follows the mission clock: 45 min of game time is 2.7 s of real time at 1000x
        var r = new IceCarve(45);
        for (int k = 0; k <= 4; k++) r.Record(2, k * 0.03, 0.5, k * 16.7, 30, 16.7);
        double t0 = 4 * 16.7;
        int frames = 0;
        while (r.Count > 0 && frames < 1000) { frames++; r.Advance(t0 + frames * 16.7); }
        Check(frames > 150 && frames < 175, "at 1000x a channel refreezes in " + F(frames / 60.0) + " s of real time (45 min of game time)");
    }

    static void Contact()
    {
        uint seed = SeaIceField.SeedOf(20280310);
        // 1 the contact field is the drawn field: every grid point of near (1 km, Detail) chunks over
        //   concentration ramps that cross the edge (8-47 %: separate floes) and the floe/pack blend
        //   (42-66 %: floes, blend and pack), at both grid sizes the sheet builds, without and with a
        //   carved channel (cut, and small floes pushed out whole, by the same snapshot)
        Check(SeaIceFloes.On && SeaIceFloes.Warm(), "floe calibration warmed before the contact field is compared");
        Func<double, double, double> ramp = (e, n) => 8 + 9 * (e + 3) + 4 * (n - 2);
        Func<double, double, double> blend = (e, n) => 42 + 6 * (e + 3) + 2 * (n - 2);
        var track = new IceCarve(45);
        for (int k = 0; k <= 560; k++) track.Record(3, -2.95 + k * 0.005, 3.2 + k * 0.001, k, 30);
        var channel = track.Snapshot();
        int cellsChecked = 0, solidCells = 0, floeChunks = 0, pushedFloes = 0, cutCells = 0;
        for (int r = 0; r < 3; r++)
        {
            var field = r == 0 ? ramp : blend;
            bool carved = r == 2;
            var cut = carved ? channel : null;
            var sheet = new IceSurface(field, seed, 15, false);
            sheet.Channels(cut);
            foreach (int cells in new[] { 32, 64 })
                for (int k = 0; k < 9; k++)
                {
                    int ci = -3 + k % 3, cj = 2 + k / 3;
                    var spec = new IceChunkSpec { CentreEastKm = ci + 0.5, CentreNorthKm = cj + 0.5, SizeKm = 1, Cells = cells, Underside = true, FreeboardM = 0.5, DraftM = 2, RidgeM = 1.2, EdgePercent = 15, Seed = seed, Detail = true, Carve = cut };
                    var m = IceMesher.Build(spec, field);
                    int g = m.Grid;
                    double h = 1.0 / g;
                    if (m.Floes) floeChunks++;
                    pushedFloes += m.PushedFloes;
                    cutCells += m.CarvedCells;
                    var node = new bool[(g + 1) * (g + 1)];
                    for (int j = 0; j <= g; j++)
                        for (int i = 0; i <= g; i++) node[j * (g + 1) + i] = sheet.IceAt(ci + i * h, cj + j * h);
                    int open = 0;
                    for (int j = 0; j < g; j++)
                        for (int i = 0; i < g; i++)
                        {
                            bool a = node[j * (g + 1) + i], b = node[j * (g + 1) + i + 1], c = node[(j + 1) * (g + 1) + i + 1], d = node[(j + 1) * (g + 1) + i];
                            Check(m.Solid[j * g + i] == (a && b && c && d), "contact field = drawn field: chunk " + ci + "," + cj + " cell " + i + "," + j + " (" + g + " cells" + (carved ? ", channel" : "") + ")");
                            if (!a && !b && !c && !d) open++;
                            if (m.Solid[j * g + i]) solidCells++;
                            cellsChecked++;
                        }
                    Check(open == m.OpenCells, "open cells as the mesher counts them (" + open + " vs " + m.OpenCells + ")");
                }
        }
        Check(solidCells > cellsChecked / 10 && solidCells < cellsChecked * 9 / 10, "the ramp chunks hold both ice and water (" + solidCells + "/" + cellsChecked + ")");
        Check(floeChunks == 3 * 2 * 9 && pushedFloes > 3 && cutCells > 100, "every ramp chunk is a floe chunk (" + floeChunks + "), and the channel cuts cells (" + cutCells + ") and pushes floes (" + pushedFloes + ")");
        // a sharp edge: lattice nodes either below the edge or in the pack, none in the floe band, so the
        // near chunk is a pack chunk (FloeRegime), though its interpolated concentration crosses the band;
        // the contact field keeps the chunk's regime, not the point's own concentration
        Func<double, double, double> step = (e, n) => e < 0.4 ? 5 : 90;
        var stepSheet = new IceSurface(step, seed, 15, false);
        int stepCells = 0, stepBand = 0;
        foreach (int cells in new[] { 32, 64 })
        {
            var m = IceMesher.Build(new IceChunkSpec { CentreEastKm = 0.5, CentreNorthKm = 0.5, SizeKm = 1, Cells = cells, Underside = true, FreeboardM = 0.5, DraftM = 2, RidgeM = 1.2, EdgePercent = 15, Seed = seed, Detail = true }, step);
            int g = m.Grid;
            double h = 1.0 / g;
            Check(!m.Floes, "a sharp 5/90 % edge: the near chunk is a pack chunk");
            for (int j = 0; j < g; j++)
                for (int i = 0; i < g; i++)
                {
                    bool a = stepSheet.IceAt(i * h, j * h), b = stepSheet.IceAt((i + 1) * h, j * h), c = stepSheet.IceAt((i + 1) * h, (j + 1) * h), d = stepSheet.IceAt(i * h, (j + 1) * h);
                    Check(m.Solid[j * g + i] == (a && b && c && d), "contact field = drawn field at a sharp edge: cell " + i + "," + j + " (" + g + " cells)");
                    double p = stepSheet.PercentAt(i * h, j * h);
                    if (p >= 15 && p < SeaIceFloes.PackPercent) stepBand++;
                    stepCells++;
                }
        }
        Check(stepBand > 0, "the sharp edge's interpolated concentration crosses the floe band (" + stepBand + "/" + stepCells + " nodes)");
        // the channel is open water for the contact test, except the ship's own fresh track
        var onTrack = new IceSurface(blend, seed, 15, false);
        var noCut = new IceSurface(blend, seed, 15, false);
        int trackIce = 0, ownIce = 0, plainIce = 0;
        for (int k = 20; k < 540; k += 4)
        {
            double e = -2.95 + k * 0.005, n = 3.2 + k * 0.001;
            onTrack.Channels(channel); if (onTrack.IceAt(e, n)) trackIce++;
            onTrack.Channels(channel, 3, -1); if (onTrack.IceAt(e, n)) ownIce++;
            onTrack.Channels(channel, 4, -1); if (onTrack.IceAt(e, n)) trackIce++;
            if (noCut.IceAt(e, n)) plainIce++;
        }
        Check(trackIce == 0 && plainIce > 40 && ownIce == plainIce, "on a channel: open water (" + trackIce + "); another ship's exclusion changes nothing; the ship's own fresh track is neither cut nor pushes floes for it (" + ownIce + " of " + plainIce + " uncut points on ice)");
        var lin = new IceSurface((e, n) => 40 + 20 * e, seed, 15, false);
        Check(Math.Abs(lin.PercentAt(0.3, 0.6) - 46) < 1e-9 && Math.Abs(lin.PercentAt(-2.7, 5.1) - (40 - 54)) < 1e-9, "contact concentration: the chunk's own lattice, bilinear between 250 m nodes");
        Func<double, double, double> wavy = (e, n) => 50 + 30 * Math.Sin(3.1 * e) * Math.Cos(2.3 * n);
        var wv = new IceSurface(wavy, seed, 15, false);
        int seams = 0;
        for (int k = -20; k <= 20; k++) { double y = 0.137 * k; if (Math.Abs(wv.PercentAt(1 - 1e-12, y) - wv.PercentAt(1, y)) > 1e-6 || Math.Abs(wv.PercentAt(y, -2 - 1e-12) - wv.PercentAt(y, -2)) > 1e-6) seams++; }
        Check(seams == 0, "contact concentration is continuous across chunk seams (" + seams + " jumps)");
        var cached = new IceSurface(wavy, seed, 15, false);
        for (int k = 0; k < 50; k++) IceHullContact.Sample(0.98, 0.02, 30, 150, 20, 10, cached.Drawn);
        Check(cached.LatticeBuilds <= 4, "a footprint over a chunk corner builds at most 4 chunk lattices, once (" + cached.LatticeBuilds + " for 50 samples)");
        var roam = new IceSurface(wavy, seed, 15, false);
        for (int k = 0; k < 400; k++) roam.SheetIceAt(k * 1.3, k * 1.7);
        Check(roam.LatticeBuilds == 400 && roam.LatticeCount <= 64 && roam.SheetIceAt(0.1, 0.1) == wv.SheetIceAt(0.1, 0.1), "the lattice cache is bounded (cleared at 64 chunks) and rebuilds the same field");
        // 2 below the drawn edge there is nothing to meet (MNO Ice 02: 13 % with the stock 15 % edge)
        int hits13 = 0, hits13at10 = 0;
        var at13 = new IceSurface((e, n) => 13, seed, 15, false);
        var at13e10 = new IceSurface((e, n) => 13, seed, 10, false);
        for (int i = 0; i < 4000; i++) { double e = i * 0.0371, n = (i % 61) * 0.0433; if (at13.IceAt(e, n)) hits13++; if (at13e10.IceAt(e, n)) hits13at10++; }
        Check(hits13 == 0, "13 % ice with the 15 % edge: nothing drawn, no contact");
        Check(Math.Abs(hits13at10 / 4000.0 - 0.13) < 0.04, "13 % ice with a 10 % edge: about 13 % of points on ice (" + hits13at10 + "/4000)");
        Check(!new IceSurface((e, n) => 0, seed, 15, false).IceAt(1, 1) && new IceSurface((e, n) => 100, seed, 15, false).IceAt(1, 1), "open water and full ice");
        // 3 floe mode: a point is covered exactly when a placed floe's rectangle holds it
        Func<double, double, double> half = (e, n) => 0.5;
        var floes = new IceSurface((e, n) => 50, seed, 15, true);
        var slots = FloePlacement.Slots(0, 0, 1.2, IceSurface.FloeCellKm, half, seed, 100000);
        Check(slots.All(x => floes.IceAt(x.East, x.North)), "every placed floe's centre is covered");
        int covered = 0, mismatched = 0;
        for (int j = 0; j < 60; j++)
            for (int i = 0; i < 60; i++)
            {
                double e = -0.6 + i * 0.0201, n = -0.6 + j * 0.0199;
                bool on = floes.IceAt(e, n);
                bool any = slots.Any(x =>
                {
                    double de = (e - x.East) * 1000, dn = (n - x.North) * 1000, y = x.YawDeg * Math.PI / 180;
                    return Math.Abs(de * Math.Cos(y) - dn * Math.Sin(y)) <= x.SizeM / 2 && Math.Abs(de * Math.Sin(y) + dn * Math.Cos(y)) <= x.SizeM * 0.35;
                });
                if (on) covered++;
                if (on != any) mismatched++;
            }
        Check(mismatched == 0 && covered > 200 && covered < 2000, "floe query = placed floes (" + covered + " of 3600 points covered, " + mismatched + " mismatched)");
        // 3b floe mode never opens the heavy pack: from the heavy-ice percent the sheet's field decides,
        //    and the submarine rule always reads the sheet's field
        int heavyDiff = 0, lightDiff = 0, subDiff = 0, sheetOn = 0;
        var floes98 = new IceSurface((e, n) => 98, seed, 15, true, 60);
        var floes50 = new IceSurface((e, n) => 50, seed, 15, true, 60);
        var sheet98 = new IceSurface((e, n) => 98, seed, 15, false);
        for (int i = 0; i < 3000; i++)
        {
            double e = i * 0.0173, n = (i % 53) * 0.0291;
            if (floes98.IceAt(e, n) != sheet98.IceAt(e, n)) heavyDiff++;
            if (sheet98.IceAt(e, n)) sheetOn++;
            if (floes50.IceAt(e, n) != FloePlacement.Covers(e, n, IceSurface.FloeCellKm, (a, b) => 0.5, seed)) lightDiff++;
            if (IceHullContact.Sample(e, n, i % 360, 90, 9, 10, floes98.Sheet).Any != IceHullContact.Sample(e, n, i % 360, 90, 9, 10, sheet98.Sheet).Any) subDiff++;
        }
        Check(heavyDiff == 0 && sheetOn > 2700, "floe mode at 98 %: the sheet's field, not the sparse cubes (" + heavyDiff + " differences, " + sheetOn + "/3000 on ice)");
        Check(lightDiff == 0, "floe mode at 50 % (below the heavy-ice percent): the placed floes decide");
        Check(subDiff == 0, "the submarine footprint reads the sheet's field in floe mode");
        // 4 the footprint: 21 points, bow weighted, heading, near margin
        Func<double, double, bool> none = (e, n) => false, all = (e, n) => true;
        var z = IceHullContact.Sample(0, 0, 0, 100, 15, 10, none);
        Check(z.Samples == 21 && z.Share == 0 && !z.Any, "open water: 21 points, none on ice");
        Check(IceHullContact.Sample(0, 0, 0, 100, 15, 10, all).Share == 1, "full ice: share 1");
        Func<double, double, bool> eastOf20 = (e, n) => e > 0.025; // stations every 20 m from -60 m
        var bowIn = IceHullContact.Sample(0, 0, 90, 100, 15, 10, eastOf20);   // heading east, bow (+60 m) in the ice
        var sternIn = IceHullContact.Sample(0, 0, 270, 100, 15, 10, eastOf20); // heading west, stern in it
        Check(Math.Abs(bowIn.Share - (4.0 / 3 + 1.5) / 7) < 1e-9 && Math.Abs(sternIn.Share - (0.5 + 2.0 / 3) / 7) < 1e-9 && bowIn.OnIce == 6 && sternIn.OnIce == 6, "the same ice counts more under the bow (" + F(bowIn.Share) + ") than under the stern (" + F(sternIn.Share) + ")");
        Check(IceHullContact.Sample(0, 0, 0, 100, 15, 10, (e, n) => e > 0.05).OnIce == 0 && IceHullContact.Sample(0, 0, 90, 100, 15, 10, (e, n) => e > 0.05).OnIce == 3, "heading: true heading clockwise from north");
        Func<double, double, bool> beside = (e, n) => e > 0.0075 + 0.008; // ice 8 m off a 15 m beam's side
        Check(IceHullContact.Sample(0, 0, 0, 100, 15, 10, beside).OnIce == 7 && IceHullContact.Sample(0, 0, 0, 100, 15, 5, beside).OnIce == 0, "a floe within 'near' metres of the side counts, one beyond it does not");
        var bad = IceHullContact.Sample(0, 0, double.NaN, double.NaN, -3, double.NaN, all);
        Check(bad.Samples == 21 && bad.Share == 1 && IceHullContact.Sample(double.NaN, 0, 0, 100, 15, 10, all).Samples == 0 && IceHullContact.Sample(0, 0, 0, 100, 15, 10, null).Samples == 0, "bad dimensions fall back to defaults; a bad position or no field samples nothing");
        // 5 the gain and its release
        Check(IceHullContact.Gain(0, 0.35) == 0 && IceHullContact.Gain(0.35, 0.35) == 1 && Math.Abs(IceHullContact.Gain(0.175, 0.35) - 0.5) < 1e-12 && IceHullContact.Gain(1, 0.35) == 1 && IceHullContact.Gain(double.NaN, 0.35) == 0 && IceHullContact.Gain(0.1, 0) == 1, "gain: share / full share, at most 1");
        var st = new IceContactState();
        Check(st.Update(1, 100) == 1 && Math.Abs(st.Update(0, 101.5) - Math.Exp(-1)) < 1e-12 && Math.Abs(st.Update(0, 103) - Math.Exp(-2)) < 1e-12, "release: 1.5 s time constant of game time");
        Check(st.Update(0, 107) == 0, "0 below " + IceContactState.MinGain + " (the breaking sound stops)");
        Check(st.Update(0.6, 107.2) == 0.6 && st.Update(0.03, 107.4) < 0.6 && st.Update(0.03, 120) == 0, "up at once; a share below the minimum counts as none");
        Check(st.Update(0.2, 50) == 0.2 && st.Update(double.NaN, 50.2) == 1, "time going back restarts; unknown contact is the area rule");
        var jump = new IceContactState(); jump.Update(1, 0);
        Check(jump.Update(0, 1e6) == 0, "a long gap (time compression, pause) releases at once");
        // 6 the speed rule: gain 1 is the area rule; never harder than it; never trapped
        int none0 = IceRules.CapabilityIndex("none");
        var rnd = new Random(5);
        int harder = 0, changedAtOne = 0;
        for (int k = 0; k < 4000; k++)
        {
            double here = rnd.NextDouble() * 98, ahead = rnd.NextDouble() * 98, reference = here + rnd.NextDouble() - 0.5, open = rnd.Next(3) == 0 ? rnd.NextDouble() : 0, gain = rnd.NextDouble();
            float wanted = (float)(rnd.NextDouble() * 60 - 15), flank = 30;
            float area = IceCarve.CapInChannel(new IceSpeedState(), wanted, flank, here, ahead, none0, reference, open);
            float one = IceCarve.CapInContact(new IceSpeedState(), wanted, flank, here, ahead, none0, reference, open, 1);
            float contact = IceCarve.CapInContact(new IceSpeedState(), wanted, flank, here, ahead, none0, reference, open, gain);
            if (one != area) changedAtOne++;
            if (Math.Abs(contact) < Math.Abs(area) - 1e-4) harder++;
        }
        Check(changedAtOne == 0, "gain 1 (or SeaIceContact=0): exactly the area rule");
        Check(harder == 0, "contact never caps harder than the area rule (" + harder + " of 4000)");
        var esc = new IceSpeedState();
        IceCarve.CapInContact(esc, 20, 30, 70, 69, none0, 70, 0, 0.95);
        Check(esc.State == IceAccess.Blocked && esc.Escaping, "lighter ice ahead still escapes at any gain (blocked 66.5 % with 65.6 % ahead)");
        var free = new IceSpeedState();
        Check(IceCarve.CapInContact(free, 20, 30, 13, 13, none0, 13, 0, 0) == 20 && free.State == IceAccess.Open, "13 % area, hull between floes: not slowed");
        Check(IceCarve.CapInContact(new IceSpeedState(), 25, 30, 13, 13, none0, 13, 0, 1) == 21, "13 % area, hull on a floe: the caution cap 0.7 x flank");
        // 7 breaking intensity follows contact
        Check(IceBreakRule.Intensity(10, 50, 15, 0) == 0 && IceBreakRule.Intensity(10, 50, 15, 1) == IceBreakRule.Intensity(10, 50, 15) && Math.Abs(IceBreakRule.Intensity(10, 50, 15, 0.5) - 0.5 * IceBreakRule.Intensity(10, 50, 15)) < 1e-12 && IceBreakRule.Intensity(10, 50, 15, double.NaN) == IceBreakRule.Intensity(10, 50, 15), "no pieces, sound or breaking noise off the ice; scaled by the gain on it");
        // 8 tracks: a 120 m frigate at 10 kn for 3 km, sampled every 0.2 s of game time
        // (ahead = here: equal ice ahead, so a blocked hull escapes at 0.4 under both rules)
        double Touch(double percent, double edge, out double meanFactor, out double areaFactor)
        {
            var surf = new IceSurface((e, n) => percent, seed, edge, false);
            var state = new IceContactState();
            var speed = new IceSpeedState();
            var areaSpeed = new IceSpeedState();
            int on = 0, steps = 0; double factor = 0, area = 0;
            for (double t = 0, x = -1.5; x < 1.5; t += 0.2, x += 10 * 0.514444 * 0.2 / 1000)
            {
                double g = state.Update(IceHullContact.Gain(IceHullContact.Sample(x, 0.4, 90, 120, 14, 10, surf.IceAt).Share, 0.35), t);
                if (g > 0) on++;
                steps++;
                IceCarve.CapInContact(speed, 25, 30, percent, percent, none0, percent, 0, g);
                IceCarve.CapInChannel(areaSpeed, 25, 30, percent, percent, none0, percent, 0);
                factor += speed.LastFactor;
                area += areaSpeed.LastFactor;
            }
            meanFactor = factor / steps;
            areaFactor = area / steps;
            return (double)on / steps;
        }
        double t13 = Touch(13, 15, out double f13, out double a13), t13e = Touch(13, 10, out double f13e, out double a13e), t95 = Touch(95, 15, out double f95, out double a95), t40 = Touch(40, 15, out double f40, out double a40);
        Check(t13 == 0 && f13 == 1 && Math.Abs(a13 - 0.7) < 1e-9, "13 % under the 15 % edge: never touching, never slowed (the area rule: caution, 0.7, the whole way)");
        Check(t13e > 0.05 && t13e < 0.8 && f13e > a13e + 0.05, "13 % patches drawn from a 10 % edge: touching " + F(t13e) + " of the way, mean speed factor " + F(f13e) + " (area rule " + F(a13e) + ")");
        Check(t40 > 0.3 && t40 < 1 && f40 > a40 + 1e-9, "40 % pack: touching " + F(t40) + ", mean factor " + F(f40) + " (area rule " + F(a40) + ")");
        Check(t95 > 0.97 && Math.Abs(f95 - a95) < 0.01, "95 % pack: touching " + F(t95) + ", mean factor " + F(f95) + " (area rule " + F(a95) + "): unchanged");
        // 9 submarines under heavy ice: held unless the whole footprint (its own length and beam) is clear
        var pack = new IceSurface((e, n) => 70, seed, 15, false);
        int clear = 0, clearButCentreIce = 0;
        for (int i = 0; i < 3000; i++)
        {
            double e = i * 0.0613, n = (i % 97) * 0.0519;
            var k2 = IceHullContact.Sample(e, n, (i * 37) % 360, 110, 10, 10, pack.IceAt);
            if (!k2.Any) { clear++; if (pack.IceAt(e, n)) clearButCentreIce++; }
        }
        Check(clear > 15 && clear < 900 && clearButCentreIce == 0, "70 % pack still has hull-size leads (" + clear + "/3000), and a clear footprint is never on ice");
        Console.WriteLine("contact: drawn field at " + cellsChecked + " cells, floes, footprint, gain, speed rule; 3 km tracks touching/mean factor (area): 13 % edge 15 " + F(t13) + "/" + F(f13) + " (" + F(a13) + "), 13 % edge 10 " + F(t13e) + "/" + F(f13e) + " (" + F(a13e) + "), 40 % " + F(t40) + "/" + F(f40) + " (" + F(a40) + "), 95 % " + F(t95) + "/" + F(f95) + " (" + F(a95) + "); 70 % pack hull-size leads " + clear + "/3000");
    }

    static void Pieces()
    {
        Check(IceBreakRule.Intensity(0.5, 80, 15) == 0 && IceBreakRule.Intensity(10, 10, 15) == 0 && IceBreakRule.Intensity(double.NaN, 50, 15) == 0, "no breaking when stopped (< 1 kn) or in open water / below the edge");
        Check(IceBreakRule.Intensity(14, 80, 15) == 1 && IceBreakRule.Intensity(28, 95, 15) == 1 && IceBreakRule.Intensity(7, 80, 15) == 0.5 && IceBreakRule.Intensity(14, 40, 15) == 0.5 && IceBreakRule.Intensity(-7, 80, 15) == 0.5, "intensity by speed and concentration, capped at 1 (astern counts)");
        Check(IceBreakRule.PieceRate(0) == 0 && IceBreakRule.PieceRate(1) == IceBreakRule.MaxPiecesPerSecond && IceBreakRule.Noise(1) == IceBreakRule.MaxNoise && IceBreakRule.Noise(0) == 0 && IceBreakRule.Noise(3) == IceBreakRule.MaxNoise, "pieces and added noise scale with intensity");
        Check(IceBreakRule.LoopVolume(0) == 0 && IceBreakRule.LoopVolume(0.01) > 0 && IceBreakRule.LoopVolume(1) == IceBreakRule.LoopMaxVolume && IceBreakRule.LoopPitch(1) > IceBreakRule.LoopPitch(0), "loop volume and pitch rise with intensity");
        Check(IceBreakRule.CrackInterval(1, 0.5) < IceBreakRule.CrackInterval(0.2, 0.5) && IceBreakRule.CrackInterval(1, 0) >= IceBreakRule.CrackShortS * 0.7 - 1e-9, "cracks come faster when breaking harder, never faster than " + IceBreakRule.CrackShortS * 0.7 + " s");
        var gate = new IceSoundGate();
        int played = 0;
        for (int k = 0; k < 200; k++) if (gate.TryPlay(k * 0.05, 0.5)) played++;
        Check(played >= 19 && played <= 20 && gate.Refused == 200 - played, "one-shot sounds rate-limited to one per 0.5 s (" + played + " in 10 s)");
        // time compression: cracks only at 1x or slower, every breaking sound muted above 2x
        Check(IceBreakRule.CracksAllowed(1) && IceBreakRule.CracksAllowed(0.5) && IceBreakRule.CracksAllowed(double.NaN) && !IceBreakRule.CracksAllowed(2) && !IceBreakRule.CracksAllowed(10), "cracks at 1x or slower only");
        Check(IceBreakRule.SoundGain(1) == 1 && IceBreakRule.SoundGain(2) == 1 && IceBreakRule.SoundGain(3) == 0 && IceBreakRule.SoundGain(1000) == 0, "breaking sounds muted above 2x");
        // pieces by distance from the camera
        Check(IceBreakRule.PieceWeight(0) == 1 && IceBreakRule.PieceWeight(1) == 1 && IceBreakRule.PieceWeight(2) == 0.5 && IceBreakRule.PieceWeight(3) == 0 && IceBreakRule.PieceWeight(8) == 0 && IceBreakRule.PieceWeight(double.NaN) == 0, "piece share: 1 within 1 km, half at 2 km, none from 3 km");
        var shared = new IcePieceSim(60, 7);
        double aNear = 0, aMid = 0, aFar = 0;
        for (int k = 0; k < 600; k++) // 60 s: a breaker under the camera, one at 2 km, one at 8 km
        {
            shared.Spawn(0, k * 0.5, 0, 5, 10, 1, 0.1, ref aNear, IceBreakRule.PieceWeight(0.3));
            shared.Spawn(2000, k * 0.5, 0, 5, 10, 1, 0.1, ref aMid, IceBreakRule.PieceWeight(2));
            shared.Spawn(8000, k * 0.5, 0, 5, 10, 1, 0.1, ref aFar, IceBreakRule.PieceWeight(8));
            shared.Step(0.1f);
        }
        int near = shared.Pieces.Count(p => p.Alive && p.E < 1000), mid = shared.Pieces.Count(p => p.Alive && p.E > 1000 && p.E < 5000), far = shared.Pieces.Count(p => p.Alive && p.E > 5000);
        double nearAge = shared.Pieces.Where(p => p.Alive && p.E < 1000).Average(p => p.Age);
        Check(far == 0 && near > mid && near >= 40 && shared.Refused > 0, "the pool goes to the ship near the camera (" + near + " pieces) before one at 2 km (" + mid + "), none to one at 8 km (" + far + "); " + shared.Refused + " distant spawns refused");
        Check(nearAge > 4.5, "near pieces are recycled only for near ones, so they settle (mean age " + F(nearAge) + " s)");
        Console.WriteLine("  pieces by distance: " + near + " at the near ship, " + mid + " at 2 km, " + far + " at 8 km of a cap of 60 (near mean age " + F(nearAge) + " s)");
        // the pool: capped, oldest reused, every piece dies by its life
        var sim = new IcePieceSim(50, 42);
        Check(new IcePieceSim(5000, 1).Cap == IcePieceSim.MaxCap && new IcePieceSim(-3, 1).Cap == 0, "cap bounded 0-" + IcePieceSim.MaxCap);
        double acc = 0;
        Check(sim.Spawn(0, 0, 0, 5, 10, 0, 0.1, ref acc) == 0 && acc == 0, "intensity 0: no pieces");
        double e = 0, n = 0;
        int maxAlive = 0;
        for (int k = 0; k < 400; k++) // 40 s heading north at 5 m/s, full intensity
        {
            n += 0.5;
            sim.Spawn(e, n, 0, 5, 10, 1, 0.1, ref acc);
            sim.Step(0.1f);
            maxAlive = Math.Max(maxAlive, sim.Alive);
        }
        Check(maxAlive <= 50 && sim.Spawned == 200 && sim.Recycled > 0, "rate 5 per second: 200 spawned in 40 s, never more than the cap of 50 alive (" + maxAlive + "), oldest reused (" + sim.Recycled + ")");
        // where they are: abeam and aft of the bow, pushed outward
        int abeam = 0, aft = 0, live = 0;
        foreach (var p in sim.Pieces) { if (!p.Alive) continue; live++; if (Math.Abs(p.E) > 5) abeam++; if (p.N < n) aft++; }
        Check(live > 0 && abeam == live && aft == live, "pieces lie outboard of the hull (" + abeam + "/" + live + ") and aft of the moving bow (" + aft + "/" + live + ")");
        double before = sim.Pieces.Where(p => p.Alive).Average(p => Math.Abs(p.E));
        for (int k = 0; k < 20; k++) sim.Step(0.1f);
        double after = sim.Pieces.Where(p => p.Alive).Average(p => Math.Abs(p.E));
        Check(after > before, "they drift outward (" + F(before) + " -> " + F(after) + " m abeam)");
        var speeds = sim.Pieces.Where(p => p.Alive).Select(p => Math.Sqrt(p.Ve * p.Ve + p.Vn * p.Vn)).ToList();
        Check(speeds.All(v => v < 4), "water drag keeps them slow (fastest " + F(speeds.Max()) + " m/s)");
        for (int k = 0; k < 320; k++) sim.Step(0.1f);
        Check(sim.Alive == 0, "every piece is gone within " + IcePieceSim.MaxLife + " s of the ship stopping");
        Check(IcePieceSim.ScaleAt(0, 20) == 1 && IcePieceSim.ScaleAt(10, 20) == 1 && Math.Abs(IcePieceSim.ScaleAt(20, 20) - 0.3f) < 1e-6 && IcePieceSim.SinkAt(0, 20) == 0 && Math.Abs(IcePieceSim.SinkAt(20, 20) - IcePieceSim.SinkM) < 1e-6 && IcePieceSim.SinkAt(17, 20) > 0, "they settle at the end of their life: shrink to 0.3 and sink " + IcePieceSim.SinkM + " m");
        // deterministic for a seed
        var a1 = new IcePieceSim(20, 9); var a2 = new IcePieceSim(20, 9);
        double x1 = 0, x2 = 0;
        for (int k = 0; k < 50; k++) { a1.Spawn(0, k, 0.3, 4, 8, 0.7, 0.1, ref x1); a1.Step(0.1f); a2.Spawn(0, k, 0.3, 4, 8, 0.7, 0.1, ref x2); a2.Step(0.1f); }
        Check(a1.Pieces.Zip(a2.Pieces, (p, q) => p.Alive == q.Alive && p.E == q.E && p.N == q.N && p.Yaw == q.Yaw).All(z => z), "deterministic for a seed");
        Check(a1.Pieces.Where(p => p.Alive).All(p => Math.Abs(p.Pitch) <= 8 && Math.Abs(p.Roll) <= 8 && p.Size > 0.5 && p.Size < 6 && p.Life >= IcePieceSim.MinLife && p.Life <= IcePieceSim.MaxLife), "slight tumble (pitch and roll within 8 degrees), pieces 0.5-6 m, life 14-30 s");
        var none = new IcePieceSim(0, 1); double z0 = 0;
        Check(none.Spawn(0, 0, 0, 5, 10, 1, 1, ref z0) == 0, "SeaIcePieceCap=0: no pieces");
        Console.WriteLine("pieces: cap, lifetimes, motion and the breaking intensity checked");
    }

    // ---- 9: the battle-map ice layer ------------------------------------------------------------

    // 9 the battle-map ice layer's pure part (SeaIceMapRules.cs): the grid
    //   against SeaIceModel at every node, the plan (padding, snapped cells,
    //   size caps, no grid in the tropics), the edge and heavy-pack lines
    //   (on the 15 % / 60 % crossings, chained, stopping at land), the fill
    //   (bands, the clipped edge cells meeting the line, nothing on land),
    //   the view box (antimeridian, pole), the readout, and the campaign
    //   map's colours.
    static void MapLayer()
    {
        var date = Noon(2028, 3, 10);
        // Plan: the Barents view of MNO Ice 01 (73.5N 36E), about 4 x 12 degrees.
        IceMapGrid.Plan(71.5, 75.5, 30, 42, out double south, out double west, out double cl, out double cn, out int rows, out int cols);
        Check(cl == 0.1 && Math.Abs(cn - 0.4) < 1e-12 && rows <= IceMapGrid.MaxRows + 2 && cols <= IceMapGrid.MaxCols + 2, "Barents plan (6 degrees padded): 0.1 degree rows, longitude step x4 at 73.5N (cos 0.28): " + cl + " / " + cn + ", " + rows + " x " + cols);
        Check(south <= 70.5 && south + rows * cl >= 76.5 && west <= 27 && west + cols * cn >= 45, "the grid is padded a quarter view each side");
        Check(Math.Abs(south / cl - Math.Round(south / cl)) < 1e-6 && Math.Abs(west / cn - Math.Round(west / cn)) < 1e-6, "grid edges on whole cells (the same nodes after a small pan)");
        IceMapGrid.Plan(10, 30, 50, 70, out _, out _, out _, out _, out rows, out cols);
        Check(rows == 0 && cols == 0, "no grid between 40S and 40N (the model has no ice there)");
        IceMapGrid.Plan(40, 90, -180, 180, out _, out _, out cl, out cn, out rows, out cols);
        Check(rows > 0 && rows <= IceMapGrid.MaxRows + 2 && cols <= IceMapGrid.MaxCols + 2 && (rows + 1) * (cols + 1) <= 20000, "a whole-hemisphere view stays within the node cap: " + rows + " x " + cols + " at " + cl + " / " + cn);

        var g = IceMapGrid.For(71.5, 75.5, 30, 42, date);
        double worst = 0;
        for (int r = 0; r <= g.Rows; r++)
            for (int c = 0; c <= g.Cols; c++)
                worst = Math.Max(worst, Math.Abs(g.At(r, c) - SeaIceModel.Concentration(g.LatOf(r), g.LonOf(c), date)));
        Check(worst < 1e-4, "every node is SeaIceModel.Concentration on the battle date (worst " + worst + ")");
        Check(Math.Abs(IceMapGeometry.Sample(g, 74.0, 36.0) - 62.28) < 0.6, "the readout's sample at 74N 36E is the model's 62.3 % (" + F(IceMapGeometry.Sample(g, 74.0, 36.0)) + ")");
        Check(double.IsNaN(IceMapGeometry.Sample(g, 60, 36)), "outside the grid: no value");

        // Lines.
        var edge = IceMapGeometry.Contour(g, 15);
        var heavy = IceMapGeometry.Contour(g, 60);
        Check(edge.Count > 0 && heavy.Count > 0, "an edge line and a heavy-pack line in the Barents view: " + edge.Count + " / " + heavy.Count + " polylines");
        double off = 0; int pts = 0;
        foreach (var l in edge) foreach (var p in l) { off = Math.Max(off, Math.Abs(IceMapGeometry.Sample(g, p[0], p[1]) - 15)); pts++; }
        Check(off < 0.5, "every edge-line point is on the 15 % crossing (worst " + F(off) + " pp, " + pts + " points)");
        Check(edge.Max(l => l.Count) > g.Cols / 2, "the edge line is chained into long polylines, not loose segments (longest " + edge.Max(l => l.Count) + " points)");
        // 36E: the edge line crosses near 71.7N (the campaign map's check), the heavy line between 73.5 and 74.5N.
        var at36 = edge.SelectMany(l => l).Where(p => Math.Abs(p[1] - 36) < g.CellLon).Select(p => p[0]).ToList();
        Check(at36.Any(lat => Math.Abs(lat - 71.7) < 0.3), "the edge line crosses 36E near 71.7N, as on the campaign map: " + string.Join(", ", at36.Select(F)));
        var heavy36 = heavy.SelectMany(l => l).Where(p => Math.Abs(p[1] - 36) < g.CellLon).Select(p => p[0]).ToList();
        Check(heavy36.Any(lat => lat > 73.5 && lat < 74.5), "the heavy-pack line crosses 36E between 73.5 and 74.5N");

        // Fill.
        var bands = IceMapGeometry.Fill(g, 15);
        Check(bands.Length == IceMapStyle.BandFloors.Length && bands.Sum(b => b.Count) > 0 && g.IceCells > 100, "fill rings in " + bands.Count(b => b.Count > 0) + " bands, " + g.IceCells + " ice cells");
        foreach (var ring in bands.SelectMany(b => b))
        {
            Check(ring.Count >= 4 && ring[0][0] == ring[ring.Count - 1][0] && ring[0][1] == ring[ring.Count - 1][1], "every fill ring is closed");
            break;
        }
        bool inside = bands.SelectMany(b => b).SelectMany(x => x).All(p => IceMapGeometry.Sample(g, p[0], p[1]) >= 15 - 0.5);
        Check(inside, "no fill vertex lies on open water (all at or over the edge)");
        Check(bands[0].Any(ring => ring.Count >= 4 && ring.Count <= 7), "the cells the edge crosses are clipped to the ice side (the fill meets the line)");
        Check(bands[IceMapStyle.Band(95, 15)].Count > 0 && IceMapStyle.Band(14.9, 15) == -1 && IceMapStyle.Band(15, 15) == 0 && IceMapStyle.Band(62, 15) == 3, "bands: none under the edge, 15-30 first, 60-80 heavy");
        Check(Enumerable.Range(1, IceMapStyle.BandFloors.Length - 1).All(b => IceMapStyle.BandAlpha(b, 15) > IceMapStyle.BandAlpha(b - 1, 15)) && IceMapStyle.BandAlpha(4, 15) <= 0.6 + 1e-9 && IceMapStyle.BandAlpha(0, 15) >= 0.2,
              "fill opacity rises with concentration, 0.2 to 0.6 (campaign alphas x 0.70)");
        Check(CampaignIceStyle.EdgeLine[0] == 0 && CampaignIceStyle.EdgeLine[1] == 200 && CampaignIceStyle.HeavyLine[2] == 120 && CampaignIceStyle.Fill[0] == 232, "the map uses the campaign map's colours (cyan edge, navy heavy line, pale fill)");

        // Land: a land cell in the pack has no fill and no line.
        var landed = IceMapGrid.For(71.5, 75.5, 30, 42, date);
        landed.Land = new bool[landed.Rows * landed.Cols];
        for (int r = 0; r < landed.Rows; r++) for (int c = 0; c < landed.Cols; c++) landed.Land[r * landed.Cols + c] = landed.LonOf(c) >= 35 && landed.LonOf(c) < 37;
        double landW = Enumerable.Range(0, landed.Cols).Where(c => landed.Land[c]).Min(c => landed.LonOf(c)), landE = Enumerable.Range(0, landed.Cols).Where(c => landed.Land[c]).Max(c => landed.LonOf(c + 1));
        var landFill = IceMapGeometry.Fill(landed, 15).SelectMany(b => b).SelectMany(x => x).ToList();
        Check(landFill.Count > 0 && !landFill.Any(p => p[1] > landW + 1e-6 && p[1] < landE - 1e-6), "no fill inside land cells (" + F(landW) + " to " + F(landE) + "E)");
        Check(!IceMapGeometry.Contour(landed, 15).SelectMany(l => l).Any(p => p[1] > landW + 1e-6 && p[1] < landE - 1e-6), "the edge line stops at the coast");

        // Seasons: September has far less ice in the same view.
        var sep = IceMapGrid.For(71.5, 75.5, 30, 42, Noon(2028, 9, 10));
        IceMapGeometry.Fill(sep, 15);
        Check(sep.IceCells < g.IceCells / 2, "10 September: " + sep.IceCells + " ice cells against " + g.IceCells + " in March");

        // The view box.
        var view = new List<double[]> { new[] { 73.5, 36.0 }, new[] { 75.0, 30.0 }, new[] { 72.0, 42.0 } };
        Check(IceMapGeometry.BoxOf(view, false, out double s, out double n, out double w, out double e) && s == 72 && n == 75 && w == 30 && e == 42, "view box from the view points");
        var seam = new List<double[]> { new[] { 66.0, 179.0 }, new[] { 67.0, -178.0 }, new[] { 65.0, 177.0 } };
        Check(IceMapGeometry.BoxOf(seam, false, out s, out n, out w, out e) && w == 177 && e == 182, "a view across the antimeridian unwraps (177 to 182)");
        // A Bering view centred near 175W that shows the Sea of Okhotsk: its grid runs west of -180, and every node
        // has the ice of its wrapped longitude (no false 95 % pack over the Sea of Okhotsk).
        var apr15 = Noon(2029, 4, 15);
        var dl = IceMapGrid.For(50, 62, -215, -160, apr15);
        double dlWorst = 0;
        for (int r = 0; r <= dl.Rows; r++)
            for (int c = 0; c <= dl.Cols; c++)
                if (dl.LonOf(c) < -180 && Math.Abs(dl.LatOf(r)) <= 90)
                    dlWorst = Math.Max(dlWorst, Math.Abs(dl.At(r, c) - SeaIceModel.Concentration(dl.LatOf(r), dl.LonOf(c) + 360, apr15)));
        Check(dl.West < -205 && dlWorst < 1e-3, "a dateline grid west of -180 reads the wrapped longitude at every node (worst " + dlWorst + ")");
        var polar = new List<double[]> { new[] { 87.0, 29.5 }, new[] { 85.0, -150.0 }, new[] { 85.0, 30.0 } };
        Check(IceMapGeometry.PoleInView(polar) && IceMapGeometry.BoxOf(polar, true, out s, out n, out w, out e) && n == 90 && w == -180 && e == 180, "MNO Ice 04 at 87N: the pole in view takes the whole circle up to 90N");
        var pg = IceMapGrid.For(s, n, w, e, Noon(2029, 1, 1));
        Check(pg != null && pg.North <= 90 + 1e-9 && (pg.Rows + 1) * (pg.Cols + 1) <= 20000 && IceMapGeometry.Contour(pg, 15).Count == 0 && pg.MaxPercent > 97,
              "a polar grid stays within the cap, stops at 90N and is all heavy pack in January (no edge line in view)");
        Check(!IceMapGeometry.BoxOf(new List<double[]> { new[] { 70.0, 0.0 } }, false, out _, out _, out _, out _), "fewer than two points on the globe: no box");

        // The readout.
        Check(IceMapStyle.Hover(0.4, 60, 30) == null, "no readout under 1 %");
        Check(IceMapStyle.Hover(8, 60, 30) == "Ice 8 % (drift ice)\nships unhindered; submarines may surface", "drift ice readout: " + IceMapStyle.Hover(8, 60, 30));
        string h72 = IceMapStyle.Hover(72, 60, 30);
        Check(h72.StartsWith("Ice 72 % (heavy pack)\n", StringComparison.Ordinal) && h72.Contains("beset") && h72.Contains("submarines held below 30 m"), "heavy pack readout: " + h72);

        Check(IceMapStyle.Hover(95, 60, 30).Contains("ice class none beset (steerage way only)"), "a beset readout names steerage way, not 0 % speed");
        string h40 = IceMapStyle.Hover(40, 60, 30);
        Check(h40.Contains("ice class none ") && h40.Contains(" % speed") && h40.EndsWith("submarines may surface", StringComparison.Ordinal), "a speed-cap readout names the ice class it is for: " + h40);
        Check(IceMapStyle.Hover(72, 60, 30, false, true) == "Ice 72 % (heavy pack)\nsubmarines held below 30 m outside leads", "SeaIceShips off or stopped: no ship line");
        Check(IceMapStyle.Hover(72, 60, 30, true, false).EndsWith("(steerage way only)", StringComparison.Ordinal), "SeaIceSubmarines off or stopped: no submarine line");
        Check(IceMapStyle.Hover(72, 60, 30, false, false) == "Ice 72 % (heavy pack)", "both off: the concentration only");

        // The readout value is the battle's own tile value, not the drawn grid.
        var tiles = new SeaIceTileCache();
        foreach (var pt in new[] { new[] { 74.0, 36.0 }, new[] { 71.73, 36.02 }, new[] { 78.31, -179.99 }, new[] { 89.97, 12.0 }, new[] { -66.5, 140.0 }, new[] { 39.95, 0.0 }, new[] { 10.0, 0.0 } })
            Check(IceMapStyle.BattlePercent(pt[0], pt[1], date) == tiles.Percent(pt[0], pt[1], date), "readout = the battle's tile value at " + pt[0] + ", " + pt[1]);
        Check(tiles.Count > 0 && IceMapStyle.BattlePercent(double.NaN, 0, date) == 0, "readout leaves no NaN through");
        var coarse = IceMapGrid.For(-20, 90, -180, 180, date);
        double worstGap = 0;
        for (double la = 66; la <= 80; la += 0.37) for (double lo = 20; lo <= 60; lo += 0.53)
            worstGap = Math.Max(worstGap, Math.Abs(IceMapGeometry.Sample(coarse, la, lo) - IceMapStyle.BattlePercent(la, lo, date)));
        Check(worstGap > 1, "at whole-disk zoom the grid differs from the battle value (" + F(worstGap) + " pp), so the readout must not read the grid");

        // The map to draw on: a second tactical map does not take the overlay while the first is shown.
        Check(IceMapStyle.Adopt(true, false, false) && IceMapStyle.Adopt(true, true, false) && !IceMapStyle.Adopt(true, true, true) && !IceMapStyle.Adopt(false, false, false),
              "adopt a tactical map only when none is held or the held one is hidden");

        // Redraw throttle.
        Check(IceMapStyle.ProjectGap(0.05, 1) == 0.05 && Math.Abs(IceMapStyle.ProjectGap(0.05, 12) - 0.12) < 1e-12 && IceMapStyle.ProjectGap(0.05, 500) == 1.0 && IceMapStyle.ProjectGap(0.05, double.NaN) == 0.05,
              "redraws at least 50 ms apart and at most ~10 % of real time");

        // A box unwrapped around the other side of 180 degrees is still covered.
        var dateline = IceMapGrid.For(70, 74, 170, 190, date);
        Check(dateline.Covers(71, 73, 175, 185) && dateline.Covers(71, 73, -185, -175) && !dateline.Covers(71, 73, -150, -140), "a view centre that crossed 180 degrees keeps the grid");
        var across = IceMapGrid.For(71, 73, 175, 185, date);
        Check(IceMapGeometry.Check(across, 71, 73, 175, 185, date) == IceMapGeometry.Need.Keep && IceMapGeometry.Check(across, 71, 73, -185, -175, date) == IceMapGeometry.Need.Keep, "no rebuild for the same view unwrapped the other way");

        // The land cache.
        var lc = new IceLandCache();
        long k1 = IceLandCache.Key(0.1, 74.05, 36.05), k2 = IceLandCache.Key(0.1, 74.05, 36.05 - 360), k3 = IceLandCache.Key(0.2, 74.05, 36.05), k4 = IceLandCache.Key(0.1, 74.15, 36.05);
        Check(k1 == k2 && k1 != k3 && k1 != k4 && IceLandCache.Key(5, 89.5, 179.99) > 0, "land cache keys: by cell size and centre, longitudes wrapped");
        Check(!lc.TryGet(k1, out _) && lc.Misses == 1, "an unsampled cell is a miss");
        lc.Put(k1, true);
        Check(lc.TryGet(k1, out bool isLand) && isLand && lc.Hits == 1 && lc.Count == 1, "a sampled cell comes from the cache");

        // Opacity switch (SeaIceMapOpacity).
        Check(IceMapStyle.Scale("0.5") == 0.5 && IceMapStyle.Scale("") == IceMapStyle.FillScale && IceMapStyle.Scale("2") == IceMapStyle.FillScale && IceMapStyle.Scale("0.05") == IceMapStyle.FillScale && IceMapStyle.Scale("x") == IceMapStyle.FillScale,
              "SeaIceMapOpacity: 0.1-1 taken, anything else the default 0.70");
        Check(Math.Abs(IceMapStyle.BandAlpha(4, 15, 1.0) / IceMapStyle.BandAlpha(4, 15) - 1 / 0.70) < 1e-9, "the opacity scales every band");

        // Whole-disk views fit the node cap and cover the whole circle.
        foreach (var lat0 in new[] { 0.0, 45.0, 70.0, 89.0 })
        {
            IceMapGrid.Plan(Math.Max(-90, lat0 - 90), Math.Min(90, lat0 + 90), -180, 180, out double ps, out double pw, out double pcl, out double pcn, out int pr, out int pc);
            Check(pr > 0 && pr <= IceMapGrid.MaxRows + 2 && pc <= IceMapGrid.MaxCols + 2 && pw <= -180 + 1e-9 && pw + pc * pcn >= 180 - 1e-9 && ps + pr * pcl >= Math.Min(90, lat0 + 90) - 1e-9,
                  "whole disk around " + lat0 + "N: " + pr + " x " + pc + " at " + pcl + " / " + pcn + " covers the circle");
        }

        // The rebuild decision.
        Check(IceMapGeometry.Check(null, 71.5, 75.5, 30, 42, date) == IceMapGeometry.Need.Rebuild, "no grid yet: build one");
        Check(IceMapGeometry.Check(g, 71.8, 75.8, 31, 43, date) == IceMapGeometry.Need.Keep, "a small pan inside the padding keeps the grid");
        Check(IceMapGeometry.Check(g, 71.5, 75.5, 30, 42, date.AddDays(1)) == IceMapGeometry.Need.Rebuild, "a new calendar day rebuilds");
        Check(IceMapGeometry.Check(g, 73, 73.6, 35, 37, date) == IceMapGeometry.Need.Rebuild, "zooming in plans finer cells: rebuild");
        Check(IceMapGeometry.Check(g, 69.3, 73.3, 30, 42, date) == IceMapGeometry.Need.Rebuild, "a box past the padding rebuilds");
        Check(IceMapGeometry.Check(g, 10, 30, 50, 70, date) == IceMapGeometry.Need.Clear && IceMapGeometry.Check(null, 10, 30, 50, 70, date) == IceMapGeometry.Need.Keep, "a tropical view clears a held grid and builds none");

        // The probes and the box.
        var probes = IceMapGeometry.Probes(1600, 900);
        Check(probes.Length == 9 && probes[0][0] == 800 && probes[0][1] == 450 && probes.Count(p => p[0] == 0 || p[0] == 1600) == 6, "nine probes, the centre first");
        var geoProbes = new[] { new[] { 73.5, 36.0 }, new[] { 75.0, 30.0 }, new[] { 75.0, 42.0 }, new[] { 72.0, 42.0 }, new[] { 72.0, 30.0 }, new[] { 75.2, 36.0 }, new[] { 73.5, 42.5 }, new[] { 71.8, 36.0 }, new[] { 73.5, 29.5 } };
        Check(IceMapGeometry.BoxOfProbes(geoProbes, out s, out n, out w, out e) && s == 71.8 && n == 75.2 && w == 29.5 && e == 42.5, "box of nine probes");
        geoProbes[3] = null;
        Check(IceMapGeometry.BoxOfProbes(geoProbes, out s, out n, out w, out e) && s == -16.5 && n == 90 && w == -180 && e == 180, "a probe off the globe: the whole circle, 90 degrees either side of the centre");
        geoProbes[0] = null;
        Check(!IceMapGeometry.BoxOfProbes(geoProbes, out _, out _, out _, out _), "the centre off the globe: no box (nothing drawn)");

        // Fill rings: only whole, unbroken rings are drawn.
        var sb = new System.Text.StringBuilder();
        StormMapGeometry.Project flatProj = (double la, double lo, out double x, out double y) => { x = lo * 100; y = -la * 100; return true; };
        var cell = IceMapGeometry.Run(g, 10, 3, 6);
        Check(IceMapGeometry.AppendRing(sb, cell, flatProj, 1e6) && sb.ToString().StartsWith("M ", StringComparison.Ordinal) && sb.ToString().EndsWith(" Z", StringComparison.Ordinal) && sb.ToString().Split('L').Length == cell.Count - 1, "a ring is one closed figure: " + sb.ToString().Substring(0, 40));
        StormMapGeometry.Project limb = (double la, double lo, out double x, out double y) => { x = lo * 100; y = -la * 100; return lo < g.LonOf(5); };
        int before = sb.Length;
        Check(!IceMapGeometry.AppendRing(sb, cell, limb, 1e6) && sb.Length == before, "a ring cut by the limb is left out whole");
        Check(!IceMapGeometry.AppendRing(sb, cell, flatProj, 10) && sb.Length == before, "a ring with a jump (a wrap) is left out whole");

        // The land readout.
        Check(IceMapGeometry.LandAt(landed, 74.0, 36.0) && !IceMapGeometry.LandAt(landed, 74.0, 33.0) && !IceMapGeometry.LandAt(g, 74.0, 36.0), "the land mask under a point (no mask: water)");

        // Cost: the worst views stay small enough for the main thread.
        var sw = System.Diagnostics.Stopwatch.StartNew();
        var whole = IceMapGrid.For(-20, 90, -180, 180, date);
        int verts = IceMapGeometry.Contour(whole, 15).Sum(l => l.Count) + IceMapGeometry.Contour(whole, 60).Sum(l => l.Count) + IceMapGeometry.Fill(whole, 15).Sum(b => b.Sum(r => r.Count));
        Check((whole.Rows + 1) * (whole.Cols + 1) <= 17000 && verts < IceMapGrid.MaxVertices, "the whole northern disk: " + (whole.Rows + 1) * (whole.Cols + 1) + " nodes, " + verts + " vertices (cap " + IceMapGrid.MaxVertices + "), " + sw.ElapsedMilliseconds + " ms");
        Console.WriteLine("map layer: grid, lines, fill, land mask, view box and readout checked");
    }

    // ---- 5b: polar frame and the battle date ----------------------------------------------

    static double Hav(double lat1, double lon1, double lat2, double lon2)
    {
        double r = Math.PI / 180, dl = (lat2 - lat1) * r, dn = (lon2 - lon1) * r;
        double h = Math.Sin(dl / 2) * Math.Sin(dl / 2) + Math.Cos(lat1 * r) * Math.Cos(lat2 * r) * Math.Sin(dn / 2) * Math.Sin(dn / 2);
        return 2 * IceFrame.KmPerDegree * 180 / Math.PI * Math.Asin(Math.Min(1, Math.Sqrt(h)));
    }

    static void Polar()
    {
        Check(IceFrame.PolarFromLatitude == 85, "polar frame from 85 degrees by default");
        Check(!new IceFrame(74, 36).Polar && !IceFrame.Around(84.4, 10).Polar && IceFrame.Around(87.0, 30).Polar && IceFrame.Around(-86.6, 0).Polar, "equirect below 85, polar at 85 and beyond (both hemispheres)");
        // round trips, including the pole, the far side of the pole and across 180
        foreach (var o in new[] { new[] { 87.0, 30 }, new[] { 90.0, 10 }, new[] { -87.0, -60 }, new[] { 89.0, 179 } })
        {
            var f = new IceFrame(o[0], o[1]);
            foreach (var q in new[] { new[] { 87.5, 40 }, new[] { 86.2, 10 }, new[] { 89.9, 210 }, new[] { 88.0, -150 }, new[] { -86.0, -50 }, new[] { -89.5, 100 } })
            {
                if (Math.Sign(q[0]) != Math.Sign(o[0])) continue;
                f.ToKm(q[0], q[1], out double e, out double n);
                f.ToGeo(e, n, out double la, out double lo);
                Check(Math.Abs(la - q[0]) < 1e-9 && Math.Abs(SeaIceModel.LonDelta(lo, q[1])) < 1e-7 && !double.IsNaN(e + n), "polar round trip " + F(q[0]) + ", " + F(q[1]) + " in the frame at " + F(o[0]) + ", " + F(o[1]));
            }
        }
        var p = new IceFrame(87, 30);
        p.ToKm(87, 30, out double e0, out double n0);
        Check(Math.Abs(e0) < 1e-9 && Math.Abs(n0) < 1e-9, "the origin is 0, 0");
        p.ToKm(88, 30, out double e1, out double n1);
        Check(Math.Abs(e1) < 1e-9 && Math.Abs(n1 - 111.32) < 1e-6, "north is true north at the origin, 111.32 km a degree");
        p.ToKm(87, 31, out double e2, out _);
        Check(e2 > 0 && Math.Abs(e2 / Hav(87, 30, 87, 31) - 1) < 0.002, "east is true east, scale within 0.2 % (" + F(e2) + " km for 1 degree of longitude at 87N)");
        p.ToKm(90, 123, out double ep, out double np);
        Check(Math.Abs(ep) < 1e-9 && Math.Abs(np - 3 * 111.32) < 1e-6, "the pole is 334 km north of an 87N origin, whatever the longitude");
        // the sheet's reach (6 x 16 km rings, 96 km): km in the frame are km on the ground
        double worstPolar = 0, worstEquirect = 0;
        var eq = new IceFrame(87, 30, false);
        foreach (var d in new[] { new[] { 96.0, 0 }, new[] { -96.0, 0 }, new[] { 0, 96.0 }, new[] { 0, -96.0 }, new[] { 68.0, 68 }, new[] { -68.0, -68 } })
        {
            p.ToGeo(d[0], d[1], out double la, out double lo); p.ToGeo(d[0] + 1, d[1], out double la1, out double lo1);
            worstPolar = Math.Max(worstPolar, Math.Abs(Hav(la, lo, la1, lo1) - 1));
            eq.ToGeo(d[0], d[1], out la, out lo); eq.ToGeo(d[0] + 1, d[1], out la1, out lo1);
            worstEquirect = Math.Max(worstEquirect, Math.Abs(Hav(la, lo, la1, lo1) - 1));
        }
        Check(worstPolar < 0.01, "polar frame: 1 km east is 1 km on the ground within 1 % across the sheet at 87N (" + F(worstPolar) + ")");
        Check(worstEquirect > 0.25, "the R15 equirect frame was more than 25 % off at the sheet's edge at 87N (" + F(worstEquirect) + "): the regression this frame fixes");
        // a battle centred within half a degree of the pole: R15 clamped cos(90) to 0.05 and put points past 90N
        var pole = IceFrame.Around(89.6, 10);
        Check(pole.Lat0 == 90 && pole.Polar, "an 89.6N battle rounds to the pole and is polar");
        for (int i = 0; i < 16; i++)
        {
            double a = i * Math.PI / 8;
            pole.ToGeo(96 * Math.Cos(a), 96 * Math.Sin(a), out double la, out double lo);
            Check(la <= 90 && la > 89 && !double.IsNaN(lo), "around the pole every point is a real position (" + F(la) + ", " + F(lo) + ")");
        }
        // south: north is away from the pole, east is increasing longitude
        var s = new IceFrame(-87, 30);
        s.ToKm(-86, 30, out double se, out double sn);
        s.ToKm(-87, 31, out double se2, out _);
        Check(Math.Abs(se) < 1e-9 && Math.Abs(sn - 111.32) < 1e-6 && se2 > 0, "south polar frame: north toward the equator, east positive");

        // the battle date from the clock's fields
        Check(!IceDate.TryFrom(0, 0, 0, 0, 0, 0, out _), "an undated clock (all zero: Environment.DateTime throws) is no date, not 2029-01-01");
        Check(IceDate.TryFrom(2028, 4, 10, 12, 0, 0, out DateTime d1) && d1 == new DateTime(2028, 4, 10, 12, 0, 0), "MNO Ice 04: 2028-04-10 12:00");
        Check(IceDate.TryFrom(1970, 1, 1, 0, 0, 0, out _), "the game's own default for a missing Date= (1970,1,1) is a date");
        Check(!IceDate.TryFrom(2028, 2, 30, 12, 0, 0, out _) && IceDate.TryFrom(2028, 2, 29, 12, 0, 0, out _) && !IceDate.TryFrom(2029, 2, 29, 12, 0, 0, out _), "day checked against the month and leap years");
        Check(!IceDate.TryFrom(2028, 4, 10, 24, 0, 0, out _) && !IceDate.TryFrom(2028, 4, 10, 12, 60, 0, out _) && !IceDate.TryFrom(2028, 4, 10, 12, 0, double.NaN, out _), "hour 24, minute 60 and NaN seconds are no date");
        Check(IceDate.TryFrom(2028, 4, 10, 12, 0, 59.99, out DateTime d2) && d2.Second == 59 && IceDate.TryFrom(2028, 4, 10, 12, 0, 60f, out DateTime d3) && d3.Second == 59, "seconds 59.99 and a transient 60.0 read as 59 (no exception, no date jump)");
        Check(SeaIceTileCache.DateKeyOf(d1) != SeaIceTileCache.DateKeyOf(new DateTime(2029, 1, 1)), "the April date and the old fallback are different ice days");
        Console.WriteLine("polar frame and battle date checked");
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
    // The battle-map ice layer (SeaIceMap.Bind): the Layers menu entry, the
    // tactical map and its projection, and the IL facts its placement rests
    // on (the first RenderedLayer draws the globe texture; MapPanel arranges
    // an unpositioned child at the panel's size).
    static void MapBindings(ModuleDefinition game)
    {
        const string G = "SeaPower.GeoPosition", P = "Noesis.Point";
        var state = T(game, "SeapowerUI.MapDisplayState");
        Check(M(state, "get_Tactical", "SeapowerUI.MapDisplayState()").IsStatic, "MapDisplayState.Tactical (static)");
        M(state, "get_LayersByName", "System.Collections.Generic.IReadOnlyDictionary`2<System.String,SeapowerUI.MapLayer>()");
        M(state, "get_LayersById", "System.Collections.Generic.IReadOnlyDictionary`2<System.Int32,SeapowerUI.MapLayer>()");
        M(state, "get_Layers", "System.Collections.ObjectModel.ObservableCollection`1<SeapowerUI.MapLayer>()");
        var layer = T(game, "SeapowerUI.MapLayer");
        M(layer, "get_Visible", "System.Boolean()");
        Check(layer.Methods.Count(m => m.IsConstructor && !m.IsStatic && m.Parameters.Count == 3 && m.Parameters[0].ParameterType.FullName == "SeapowerUI.MapDisplayState" &&
              m.Parameters[1].ParameterType.FullName == "SeapowerUI.GizmoLayerManager/Entry&" && m.Parameters[2].ParameterType.FullName == "System.Boolean") == 1, "MapLayer.ctor(MapDisplayState, in GizmoLayerManager.Entry, bool)");
        var entry = T(game, "SeapowerUI.GizmoLayerManager/Entry");
        Check(entry.IsValueType && entry.Methods.Any(m => m.IsConstructor && Sig(m) == "System.Void(System.Int32,System.String,System.Boolean)"), "GizmoLayerManager.Entry(int, string, bool), a struct");
        var mapBase = T(game, "MapControl.MapBase");
        Check(M(mapBase, "TryLocationToView", "System.Boolean(" + G + "," + P + "&)").IsPublic, "MapBase.TryLocationToView public (called typed)");
        Check(M(mapBase, "TryViewToGeoPosition", "System.Boolean(" + P + "," + G + "&)").IsPublic, "MapBase.TryViewToGeoPosition public (called typed)");
        var panel = T(game, "MapControl.MapPanel");
        M(panel, "get_ParentMap", "MapControl.MapBase()");
        Check(mapBase.BaseType.FullName == "MapControl.MapPanel" && panel.BaseType.FullName == "Noesis.Panel", "MapBase : MapPanel : Noesis.Panel");
        var arrange = M(panel, "ArrangeOverride", "Noesis.Size(Noesis.Size)");
        Check(Index(arrange, i => i.Operand is MethodReference r && r.Name == "ArrangeElement" && r.Parameters.Count == 2 && r.Parameters[1].ParameterType.FullName == "Noesis.Size") >= 0,
              "MapPanel.ArrangeOverride arranges a child with no position at the panel's size (the ice canvas inside the map)");
        var renderedLayer = T(game, "MapControl.RenderedLayer");
        Check(renderedLayer.BaseType.FullName == "MapControl.MapPanel", "RenderedLayer : MapPanel");
        var render = M(renderedLayer, "OnRender", "System.Void(Noesis.DrawingContext)");
        Check(Index(render, i => Calls(i, "SeaPower.LiveMap.MapCamera", "get_MapTexture")) >= 0, "RenderedLayer.OnRender draws the live map's texture (the globe the ice goes over)");
        M(T(game, "SeapowerUI.ViewModels.MainGameViewModel"), "get_Map", "SeapowerUI.ViewModels.SceneMapViewModel()");
        M(T(game, "SeapowerUI.ViewModels.SceneMapViewModel"), "get_DisplayMap", "SeapowerUI.MapViewModel()");
        M(T(game, "SeaPower.GameMain"), "Update", "System.Void()");
        var lang = T(game, "SeaPower.LanguageResourceHandler");
        Check(lang.Methods.Any(m => m.Name == "get_LanguageDictionary" && m.ReturnType.FullName == "SeaPower.DictionaryWithFallbacks`2<System.String,System.String>"), "LanguageResourceHandler.LanguageDictionary");
        Check(T(game, "SeaPower.DictionaryWithFallbacks`2").Methods.Any(m => m.Name == "set_Item"), "DictionaryWithFallbacks indexer setter (the menu text)");
        Console.WriteLine("map layer bindings: Layers menu, tactical map, projection and placement checked");
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
        // the fields TryDate reads, and that get_DateTime is built from exactly them (so an all-zero clock throws there)
        foreach (var g in new[] { "get_Year", "get_Month", "get_Day", "get_Hour", "get_Minutes" }) M(env, g, "System.Int32()");
        M(env, "get_Seconds", "System.Single()");
        var dt = M(env, "get_DateTime", "System.DateTime()");
        Check(new[] { "get_Year", "get_Month", "get_Day", "get_Hour", "get_Minutes", "get_Seconds" }.All(g => Index(dt, i => Calls(i, "SeaPower.Environment", g)) >= 0) && Index(dt, i => i.OpCode.Code == Code.Newobj && ((MethodReference)i.Operand).DeclaringType.FullName == "System.DateTime") >= 0, "Environment.DateTime = new DateTime(Year, Month, Day, Hour, Minutes, (int)Seconds)");
        // mission loading: units first, then the clock, then IsLoadingDone; the Date= default is 1970,1,1 (never 2029)
        var sceneT = T(game, "SeaPower.SceneCreator");
        M(sceneT, "get_IsLoadingDone", "System.Boolean()");
        var lm = sceneT.NestedTypes.Where(t => t.Name.StartsWith("<LoadMission>", StringComparison.Ordinal)).SelectMany(t => t.Methods).Single(x => x.Name == "MoveNext");
        int ct = Index(lm, i => Calls(i, "SeaPower.SceneCreator", "CreateTaskforces")), sme = Index(lm, i => Calls(i, "SeaPower.Environment", "SetupMissionEnvironment"));
        int notDone = Index(lm, i => Calls(i, "SeaPower.SceneCreator", "set_IsLoadingDone")), done = -1;
        for (int k = 0; k < lm.Body.Instructions.Count; k++) if (Calls(lm.Body.Instructions[k], "SeaPower.SceneCreator", "set_IsLoadingDone") && lm.Body.Instructions[k - 1].OpCode.Code == Code.Ldc_I4_1) done = k;
        Check(ct > 0 && sme > ct && notDone >= 0 && notDone < ct && done > sme, "LoadMission: IsLoadingDone(false), CreateTaskforces, then SetupMissionEnvironment, then IsLoadingDone(true) (units exist before the clock is dated)");
        // no yield between the units and the clock: a healthy load never ticks a unit on an undated clock;
        // the undated window SEST can see is the frames before CreateTaskforces (asset loading yields)
        int yields = 0;
        for (int k = ct; k < sme; k++) if (lm.Body.Instructions[k].OpCode.Code == Code.Stfld && lm.Body.Instructions[k].Operand is FieldReference stateField && stateField.Name == "<>1__state") yields++;
        Check(ct > 0 && sme > ct && yields == 0, "LoadMission: CreateTaskforces and SetupMissionEnvironment run in the same coroutine step (no yield between)");
        int dateKey = Index(lm, i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "Date");
        Check(dateKey > 0 && dateKey < sme && lm.Body.Instructions[dateKey + 1].OpCode.Code == Code.Ldc_R4 && (float)lm.Body.Instructions[dateKey + 1].Operand == 1970f, "[Environment] Date= read as a Vector3 with default 1970,1,1");
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
        MapBindings(game);
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
        // ship effects: hull noise, speed and size, audio clips, the Diffuse shader, Ceto clip overlays
        var vessel = T(game, "SeaPower.Vessel");
        var gn = M(vessel, "getNoise", "System.Single()");
        Check(gn.IsVirtual && Index(gn, i => Field(i, Code.Ldfld, "SeaPower.SensorData", "_flowNoise")) >= 0 && Index(gn, i => Field(i, Code.Ldfld, "SeaPower.SensorData", "_baseNoise")) >= 0, "Vessel.getNoise: base noise + flow noise x knots (dB), the breaking noise adds to it");
        // the breaking noise: the passive target path is SonarAcoustics.BroadbandTargetSLDB, not getNoise
        var acoustics = T(game, "SeaPower.SonarAcoustics");
        var bt = M(acoustics, "BroadbandTargetSLDB", "System.Single(SeaPower.SensorData,System.Single,System.Single,System.Single,System.Single,System.Single,SeaPower.SonarParameters/SonarFrequency,System.Single)");
        Check(bt.IsStatic && bt.IsPublic && Index(bt, i => Field(i, Code.Ldfld, "SeaPower.SensorData", "_baseNoise")) >= 0 && Index(bt, i => Field(i, Code.Ldfld, "SeaPower.SensorData", "_flowNoise")) >= 0 && bt.Body.CodeSize > 64, "SonarAcoustics.BroadbandTargetSLDB(SensorData, ...): base + flow noise of the target, dB (" + bt.Body.CodeSize + " bytes of IL: not inlined)");
        var sonar = T(game, "SeaPower.Sonar");
        var ppc = sonar.Methods.Single(x => x.Name == "ProcessPassiveContact");
        int btCall = Index(ppc, i => Calls(i, "SeaPower.SonarAcoustics", "BroadbandTargetSLDB")), bandCall = Index(ppc, i => Calls(i, "SeaPower.SonarAcoustics", "BroadbandBandSLDB"));
        Check(btCall > 0 && Index(ppc, i => Field(i, Code.Ldfld, "SeaPower.ObjectBase", "_sensorData")) is int sdAt && sdAt > 0 && sdAt < btCall && bandCall > btCall, "Sonar.ProcessPassiveContact builds the target's level from BroadbandTargetSLDB(target._sensorData, ...), and its broadband bands from that level");
        Check(Index(ppc, i => Calls(i, "SeaPower.ObjectBase", "getNoise") || Calls(i, "SeaPower.Vessel", "getNoise")) < 0, "ProcessPassiveContact never calls getNoise (a getNoise postfix alone would not reach passive detection)");
        var noiseCallers = game.GetTypes().SelectMany(t => t.Methods.Concat(t.NestedTypes.SelectMany(n => n.Methods))).Where(x => x.HasBody && x.Body.Instructions.Any(i => Calls(i, "SeaPower.ObjectBase", "getNoise"))).Select(x => x.DeclaringType.Name + "::" + x.Name).Distinct().ToList();
        Check(noiseCallers.Any(n => n.EndsWith("::BuildEntry")), "ObjectBase.getNoise feeds SonarTickCache.BuildEntry (interferer levels, AswSimulation=1): " + string.Join(", ", noiseCallers));
        Check(game.GetTypes().Where(t => t.FullName.StartsWith("SeaPower.VesselLoader", StringComparison.Ordinal)).SelectMany(t => t.Methods).Where(x => x.HasBody).Any(x => { var b = x.Body.Instructions; int s = Index(x, i => Calls(i, "SeaPower.ObjectBase", "setSensorData")); return s > 0 && b[s - 1].OpCode.Code == Code.Newobj && ((MethodReference)b[s - 1].Operand).DeclaringType.FullName == "SeaPower.SensorData"; }), "every vessel gets its own SensorData (new SensorData then setSensorData): the noise key is per ship");
        // the game clock: missionElapsedTime follows time compression above Time.timeScale's cap
        var gt = T(game, "SeaPower.GameTime");
        foreach (var (gn2, gs) in new[] { ("get_missionElapsedTime", "System.Double()"), ("get_TimeCompression", "System.Single()"), ("get_deltaTime", "System.Single()") }) Check(M(gt, gn2, gs).IsStatic, "GameTime." + gn2 + " static");
        var upd = M(gt, "OnUpdateUnpaused", "System.Void()");
        Check(Index(upd, i => Calls(i, "SeaPower.GameTime", "set_missionElapsedTime")) > Index(upd, i => Calls(i, "SeaPower.GameTime", "set_deltaTime")) && Index(upd, i => Calls(i, "UnityEngine.Time", "get_timeScale")) >= 0, "GameTime.OnUpdateUnpaused: deltaTime = TimeCompression x Time.deltaTime / Time.timeScale, added to missionElapsedTime");
        Check(Index(M(gt, "set_TimeCompression", "System.Void(System.Single)"), i => Field(i, Code.Ldsfld, "SeaPower.GameTime", "_physicsTimeScaleCap")) >= 0, "set_TimeCompression caps Time.timeScale at _physicsTimeScaleCap (Time.time is not game time above it)");
        Check(!M(ob, "getVelocityInKnots", "System.Single()").IsStatic, "ObjectBase.getVelocityInKnots()");
        Fd(T(game, "SeaPower.ObjectBaseParameters"), "_dimensions", "UnityEngine.Vector3");
        var loaderT = T(game, "SeaPower.ObjectBaseLoader");
        Check(loaderT.Methods.Where(x => x.HasBody).Any(x => { var b = x.Body.Instructions; int s = Index(x, i => Field(i, Code.Stfld, "SeaPower.ObjectBaseParameters", "_dimensions")); return s > 0 && Calls(b[s - 1], "UnityEngine.Bounds", "get_size"); }), "_dimensions is the hull's renderer bounds size (Unity units; x 67.2 m)");
        var rl = T(game, "SeaPower.ResourceLoader");
        var gac = M(rl, "getAudioClipResource", "UnityEngine.AudioClip(System.String)");
        Check(!gac.IsStatic, "ResourceLoader.getAudioClipResource(string) : AudioClip (instance, via Singleton<ResourceLoader>._instance)");
        var allStr = new HashSet<string>(game.GetTypes().SelectMany(t => t.Methods).Where(x => x.HasBody).SelectMany(x => x.Body.Instructions).Where(i => i.OpCode.Code == Code.Ldstr).Select(i => (string)i.Operand));
        Check(allStr.Contains("audio/explosions/explosion_medium_distant") && allStr.Contains("audio/miscellaneous/teletype"), "the game loads its own sound effects by resource path through the same loader");
        Check(game.GetTypes().SelectMany(t => t.Methods).Where(x => x.HasBody).Any(x => { var b = x.Body.Instructions; for (int k = 1; k < b.Count; k++) if (Calls(b[k], "UnityEngine.Shader", "Find") && b[k - 1].OpCode.Code == Code.Ldstr && (string)b[k - 1].Operand == "Diffuse") return true; return false; }), "the game itself loads Shader.Find(\"Diffuse\") (so it is in the build)");
        var wo = T(assets, "Ceto.WaveOverlay");
        Check(wo.Methods.Any(x => x.IsConstructor && x.IsPublic && Sig(x) == "System.Void(UnityEngine.Vector3,System.Single,UnityEngine.Vector2,System.Single)"), "Ceto.WaveOverlay(Vector3 pos, float rotation, Vector2 halfSize, float duration)");
        foreach (var (pn, pt) in new[] { ("ClipTex", "Ceto.OverlayClipTexture"), ("Position", "UnityEngine.Vector3"), ("HalfSize", "UnityEngine.Vector2"), ("Rotation", "System.Single"), ("Kill", "System.Boolean") })
            Check(wo.Properties.Any(p => p.Name == pn && p.PropertyType.FullName == pt && p.SetMethod != null && p.SetMethod.IsPublic), "WaveOverlay." + pn + " : " + pt + " settable");
        M(wo, "UpdateOverlay", "System.Void()");
        var ltw = wo.Methods.Single(x => x.Name == "CalculateLocalToWorld");
        Check(Index(ltw, i => Calls(i, "UnityEngine.Quaternion", "Euler")) >= 0 && Index(ltw, i => Calls(i, "Ceto.WaveOverlay", "get_HalfSize")) >= 0, "overlay placement: TRS(position, Euler(0, Rotation, 0), HalfSize) (rotation in degrees, as the chunk's yaw)");
        var om = T(assets, "Ceto.OverlayManager");
        M(om, "Add", "System.Void(Ceto.WaveOverlay)");
        Check(Index(M(om, "Update", "System.Void()"), i => Calls(i, "Ceto.WaveOverlay", "get_Kill")) >= 0, "OverlayManager.Update drops killed overlays");
        Check(om.Properties.Any(p => p.Name == "HasClipOverlay" && p.PropertyType.FullName == "System.Boolean"), "OverlayManager.HasClipOverlay (diagnostics)");
        Check(ocean.Properties.Any(p => p.Name == "OverlayManager" && p.PropertyType.FullName == "Ceto.OverlayManager" && p.GetMethod != null && p.GetMethod.IsPublic), "Ocean.OverlayManager");
        Fd(ocean, "clipOverlaySize", "Ceto.OVERLAY_MAP_SIZE");
        var oct = T(assets, "Ceto.OverlayClipTexture");
        Fd(oct, "tex", "UnityEngine.Texture"); Fd(oct, "alpha", "System.Single");
        var ign = Fd(oct, "ignoreQuerys", "System.Boolean");
        Check(ign.IsPublic, "OverlayClipTexture.ignoreQuerys public");
        var gqc = om.Methods.Single(x => x.Name == "GetQueryableContaining");
        Check(Index(gqc, i => Field(i, Code.Ldfld, "Ceto.OverlayClipTexture", "ignoreQuerys")) >= 0 && Index(gqc, i => Calls(i, "Ceto.WaveOverlay", "Contains")) > Index(gqc, i => Field(i, Code.Ldfld, "Ceto.OverlayClipTexture", "ignoreQuerys")), "OverlayManager.GetQueryableContaining skips a clip overlay with ignoreQuerys before WaveOverlay.Contains (no Cos/Sin, no texture read)");
        var uwp = T(assets, "Ceto.UnderWaterPostEffect");
        Fd(uwp, "disableOnClip", "System.Boolean");
        var uwv = uwp.Methods.Single(x => x.Name == "UnderWaterIsVisible");
        Check(Index(uwv, i => Field(i, Code.Ldfld, "Ceto.UnderWaterPostEffect", "disableOnClip")) >= 0 && Index(uwv, i => Calls(i, "Ceto.Ocean", "QueryWaves")) >= 0 && Index(uwv, i => Field(i, Code.Stfld, "Ceto.WaveQuery", "overrideIgnoreQuerys")) < 0, "UnderWaterPostEffect.UnderWaterIsVisible: a clip query at the camera without overrideIgnoreQuerys (so ignoreQuerys overlays never switch the underwater effect off)");
        Check(oct.Methods.Any(x => x.IsConstructor && !x.HasParameters && x.IsPublic), "OverlayClipTexture() (alpha 1)");
        Check(game.GetTypes().SelectMany(t => t.Methods).Where(x => x.HasBody).Any(x => x.Body.Instructions.Any(i => Calls(i, "Ceto.OverlayManager", "Add"))) && game.GetTypes().SelectMany(t => t.Methods).Where(x => x.HasBody).Any(x => x.Body.Instructions.Any(i => i.OpCode.Code == Code.Newobj && i.Operand is MethodReference r && r.DeclaringType.FullName == "Ceto.WaveOverlay")), "the game itself builds WaveOverlays in code and adds them to the OverlayManager (shockwave rings)");
        Check(assets.GetTypes().SelectMany(t => t.Methods).Where(x => x.HasBody).Any(x => x.Body.Instructions.Any(i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "Ceto_Overlay_ClipMap")), "Ceto publishes its clip map to the ocean shader (Ceto_Overlay_ClipMap)");
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
        var iceInstall = battle.Methods.Single(m => m.Name == "Install");
        foreach (var key in new[] { "SeaIceWaitForMission", "SeaIcePolarFrameLatitude" })
            Check(Index(iceInstall, i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == key) > 0, key + " read by SeaIceBattle.Install");
        var envM = battle.Methods.Single(m => m.Name == "Env");
        Check(Index(envM, i => Calls(i, "Sest.RuntimeFixes.SeaIceBattle", "IsReady")) > 0, "Env() hands out only a loaded, dated Environment");
        Check(Index(battle.Methods.Single(m => m.Name == "FloeIcePostfix"), i => Calls(i, "Sest.RuntimeFixes.SeaIceBattle", "IsReady")) > 0, "the noise postfix checks readiness itself (it runs off the main thread)");
        var floeM = battle.Methods.Single(m => m.Name == "FloeIcePostfix");
        Check(Index(floeM, i => Calls(i, "Sest.RuntimeFixes.SeaIceBattle", "Current")) < 0 && Index(floeM, i => Calls(i, "Sest.RuntimeFixes.SeaIceBattle", "Existing")) > 0,
              "the noise postfix only reads the battle the main thread started (it never resets Breakers or the carve from a worker)");
        Check(Index(envM, i => Calls(i, "Sest.RuntimeFixes.SeaIceBattle", "Current")) > 0, "Env() starts the battle on the main thread (Current) for the noise postfix's Existing");
        var battleTick = battle.Methods.Single(m => m.Name == "BattleTickPostfix");
        Check(battleTick.Parameters.Count == 0 && Index(battleTick, i => Calls(i, "Sest.RuntimeFixes.SeaIceBattle", "Env")) > 0, "a GameMain.Update postfix starts the battle through Env() without the sheet or a moving ship (SeaIceSheet=0, ships at rest)");
        // Install's Part lambdas compile into the nested closure class
        Check(battle.NestedTypes.SelectMany(t => t.Methods).Where(m => m.HasBody).Any(m => Index(m, i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "BattleTickPostfix") >= 0 && Index(m, i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "Update") >= 0), "Install hooks BattleTickPostfix on GameMain.Update with the ocean noise");
        Check(battle.Methods.Single(m => m.Name == "Date").Body.Instructions.All(i => !(i.OpCode.Code == Code.Call && i.Operand is MethodReference r && r.Name == "get_DateTime")), "Date() no longer calls Environment.DateTime (no exception per call on an undated clock)");
        var noiseP = battle.Methods.Single(m => m.Name == "NoisePostfix");
        Check(noiseP.Parameters.Select(p => p.Name + ":" + p.ParameterType.FullName).SequenceEqual(new[] { "__instance:SeaPower.Vessel", "__result:System.Single&" }), "interferer-noise postfix takes the vessel and the noise by ref");
        var targetP = battle.Methods.Single(m => m.Name == "TargetNoisePostfix");
        Check(targetP.Parameters.Select(p => p.Name + ":" + p.ParameterType.FullName).SequenceEqual(new[] { "__0:SeaPower.SensorData", "__result:System.Single&" }), "passive target-noise postfix takes the target's SensorData and the level by ref");
        var tnm = battle.Methods.Single(m => m.Name == "TargetNoiseMethod");
        Check(Index(tnm, i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "BroadbandTargetSLDB") >= 0 && rt.GetTypes().Where(t => t.FullName.StartsWith("Sest.RuntimeFixes.SeaIceBattle", StringComparison.Ordinal)).SelectMany(t => t.Methods).Where(m => m.HasBody).Any(m => m.Body.Instructions.Any(i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "TargetNoisePostfix")), "the breaking noise is patched on SonarAcoustics.BroadbandTargetSLDB, the passive target path");
        var clock = battle.Methods.Single(m => m.Name == "BindClock");
        foreach (var gm in new[] { "get_missionElapsedTime", "get_TimeCompression", "get_deltaTime" })
            Check(Index(clock, i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == gm) >= 0, "game clock binds GameTime." + gm);
        Check(rt.GetTypes().SelectMany(t => t.Methods.Concat(t.NestedTypes.SelectMany(n => n.Methods))).Where(m => m.HasBody && (m.DeclaringType.FullName.StartsWith("Sest.RuntimeFixes.SeaIceBattle") || m.DeclaringType.FullName.StartsWith("Sest.RuntimeFixes.SeaIceEffects"))).All(m => m.Name == "Now" || m.Name == "BindClock" || !m.Body.Instructions.Any(i => Calls(i, "UnityEngine.Time", "get_time"))), "no game-time rule reads Unity's Time.time (only the unbound-clock fallback in Now)");
        var bind = rt.GetType("Sest.RuntimeFixes.CetoClip").Methods.Single(m => m.Name == "Bind");
        Check(Index(bind, i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "ignoreQuerys") >= 0, "the ocean clip binds OverlayClipTexture.ignoreQuerys (and makes no overlay without it)");
        var create = rt.GetType("Sest.RuntimeFixes.CetoClip").Methods.Single(m => m.Name == "Create");
        Check(Index(create, i => Field(i, Code.Ldsfld, "Sest.RuntimeFixes.CetoClip", "clipIgnore")) is int ci && ci > 0 && ci < Index(create, i => Field(i, Code.Ldsfld, "Sest.RuntimeFixes.CetoClip", "clipTex")), "Create sets ignoreQuerys before the texture and ClipTex");
        Check(!rt.GetTypes().SelectMany(t => t.Methods.Concat(t.NestedTypes.SelectMany(n => n.Methods))).Where(m => m.HasBody).SelectMany(m => m.Body.Instructions).Any(i => i.OpCode.Code == Code.Ldstr && ((string)i.Operand).Contains("explosion")), "no crack sound by default: the runtime names no explosion clip");
        var install = battle.Methods.Single(m => m.Name == "Install");
        foreach (var sw in new[] { "SeaIceCarve", "SeaIceBreakup", "SeaIceSound", "SeaIceBreakNoise", "SeaIceCarveMinutes", "SeaIceContact", "SeaIceContactNearM", "SeaIceContactFullShare" })
            Check(Index(install, i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == sw) >= 0, sw + " switch read");
        var floeInstall = battle.Methods.Single(m => m.Name == "InstallFloes");
        foreach (var sw in new[] { "SeaIceFloeField", "SeaIceFloeFullPercent", "SeaIceFloePackPercent", "SeaIceFloePushM" })
            Check(Index(floeInstall, i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == sw) >= 0, sw + " option read");
        Check(Index(install, i => i.OpCode.Code == Code.Call && i.Operand is MethodReference mr && mr.Name == "InstallFloes") > Index(install, i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "SeaIceSubHeavyPercent"), "floes configured after the heavy-ice percent (the pack field is capped at it)");
        var sheetInstall = rt.GetType("Sest.RuntimeFixes.SeaIceSheet").Methods.Single(m => m.Name == "Install");
        foreach (var sw in new[] { "SeaIceAlbedo", "SeaIceSmoothness", "SeaIceShader", "SeaIceOceanClip", "SeaIceFloeCells" })
            Check(Index(sheetInstall, i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == sw) >= 0, sw + " option read");
        var fx = rt.GetType("Sest.RuntimeFixes.SeaIceEffects");
        Check(fx != null && rt.GetType("Sest.RuntimeFixes.CetoClip") != null, "runtime has the effects driver and the Ceto clip binding");
        var fxInstall = fx.Methods.Single(m => m.Name == "Install");
        foreach (var sw in new[] { "SeaIcePieceCap", "SeaIceSoundClip", "SeaIceCrackClip", "SeaIceSoundVolume" })
            Check(Index(fxInstall, i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == sw) >= 0, sw + " option read");
        Check(rt.AssemblyReferences.All(r => r.Name != "Assets" && r.Name != "UnityEngine.AudioModule"), "Ceto and the audio types are bound by reflection (no Assets or AudioModule reference)");
        var map = rt.GetType("Sest.RuntimeFixes.SeaIceMap");
        Check(map != null && rt.GetType("Sest.RuntimeFixes.IceMapGrid") != null && rt.GetType("Sest.RuntimeFixes.IceMapGeometry") != null, "runtime has the battle-map ice layer");
        int mapInstall = Index(entry, i => Calls(i, "Sest.RuntimeFixes.SeaIceMap", "Install"));
        Check(mapInstall > ice && costs > mapInstall && Index(entry, i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "SeaIceMapLayer") > ice, "the map layer installs after the sea ice, behind SeaIceMapLayer, before CumulativeCombatCosts' early return");
        Check(map.Methods.Single(m => m.Name == "AfterMapRender").Parameters.Select(p => p.Name).SequenceEqual(new[] { "__instance" }) && map.Methods.Single(m => m.Name == "MapTick").Parameters.Count == 0, "map layer postfix signatures");
        var mapOptions = map.Methods.Single(m => m.Name == "Install");
        foreach (var sw in new[] { "SeaIceMapFill", "SeaIceMapOpacity", "SeaIceMapUnderUnits", "SeaIceMapLandMask" })
            Check(Index(mapOptions, i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == sw) >= 0, sw + " option read");
        var mapBind = map.Methods.Single(m => m.Name == "Bind");
        foreach (var name in new[] { "TryLocationToView", "TryViewToGeoPosition", "OnRender", "get_Tactical", "GetHeightAt" })
            Check(Index(mapBind, i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == name) >= 0, "the map layer binds " + name + " by name before it patches anything");
        Check(Index(mapOptions, i => Calls(i, "Sest.RuntimeFixes.SeaIceMap", "Bind")) < Index(mapOptions, i => Calls(i, "Sest.RuntimeFixes.Api", "Postfix")), "bound before patched");
        var tick = map.Methods.Single(m => m.Name == "MapTick");
        Check(Index(tick, i => Calls(i, "Sest.RuntimeFixes.SeaIceMap", "TryEnsureLayer")) >= 0, "the Layers menu entry is retried from every tick, not only on a grid rebuild");
        Check(tick.Body.Instructions.Count(i => Field(i, Code.Stsfld, "Sest.RuntimeFixes.SeaIceMap", "attachTries") && i.Previous != null && i.Previous.OpCode.Code == Code.Ldc_I4_0) >= 2,
              "the attach retry count starts again for each tactical map and after an attach succeeds (ten tries per map, not per session)");
        var hoverM = map.NestedTypes.Single(t => t.Name == "Overlay").Methods.Single(m => m.Name == "OnMove");
        Check(Index(hoverM, i => Calls(i, "Sest.RuntimeFixes.IceMapStyle", "BattlePercent")) >= 0 && Index(hoverM, i => Calls(i, "Sest.RuntimeFixes.IceMapGeometry", "Sample")) < 0, "the readout reads the battle's tile value, not the drawn grid");
        Check(Index(hoverM, i => Field(i, Code.Ldsfld, "Sest.RuntimeFixes.SeaIceBattle", "ShipsOn")) >= 0 && Index(hoverM, i => Field(i, Code.Ldsfld, "Sest.RuntimeFixes.SeaIceBattle", "SubsOn")) >= 0, "the readout follows SeaIceShips / SeaIceSubmarines");
        var render = map.Methods.Single(m => m.Name == "AfterMapRender");
        Check(Index(render, i => Calls(i, "Sest.RuntimeFixes.IceMapStyle", "Adopt")) >= 0, "a second tactical map does not take the overlay while the first is shown");
        var attach = map.NestedTypes.Single(t => t.Name == "Overlay").Methods.Single(m => m.Name == "Attach");
        Check(attach.Body.ExceptionHandlers.Any(h => h.HandlerType == ExceptionHandlerType.Catch), "drawing inside the map falls back to over the map when the insert throws");
        var mask = map.Methods.Single(m => m.Name == "AdvanceMask");
        Check(Index(mask, i => Calls(i, "Sest.RuntimeFixes.IceLandCache", "TryGet")) >= 0 && Index(mask, i => Calls(i, "Sest.RuntimeFixes.IceLandCache", "TryGet")) < Index(mask, i => Calls(i, "SeaPower.TerrainUtils", "GetHeightAt")), "land heights come from the cache first");
        Check(Index(mask, i => Field(i, Code.Stsfld, "Sest.RuntimeFixes.SeaIceMap", "grid")) > Index(mask, i => Calls(i, "Sest.RuntimeFixes.IceMapGeometry", "Fill")), "the new grid is drawn only once its geometry is built");
        Console.WriteLine("runtime: patch signatures and install order checked");
    }
}
