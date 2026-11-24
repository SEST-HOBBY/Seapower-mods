using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using Sest.RuntimeFixes;

// The ice-features drop-in (IceShelfRules.cs, IcebergField.cs, IceFeaturesData.g.cs and, with
// the stub game types, IceFeaturesBattle.cs). Built and run by build_drop_in.py with mcs/mono.
// 1 data tables and their source hashes;
// 2 shelves: containment on the simplified outline equals ice.IceShelf.contains on the same rings;
//   agreement with the full outline; front distance equals iceshelves.distance_to_front_nm; the
//   navigation rule; the culled front search;
// 3 the no-go speed rule: unit cases and a track toward the Ross front (surface and submarine);
// 4 icebergs: density, fractional month, sensor hooks, melt, drift step, all against Python;
// 5 the generator: the same bergs as icebergs.generate (ids, classes, positions, sizes, drift, life);
// 6 the battle part against stub game types (binding, switches, the speed postfix, meshes), when
//   tests/BattleTests.cs and tests/stubs are compiled in (build_drop_in.py does; r16's build need not).
internal static class IceFeaturesTests
{
    private static int checks;
    internal static void Check(bool ok, string why) { checks++; if (!ok) throw new Exception("FAILED: " + why); }
    private static double D(long bits) => BitConverter.Int64BitsToDouble(bits);
    private static string F(double v) => v.ToString("0.######", CultureInfo.InvariantCulture);

    private static int Main(string[] args)
    {
        try
        {
            Data();
            Shelves();
            SpeedRule();
            Track();
            Bergs();
            Generator();
            Behaviour();
            // the battle part needs the stub game types (tests/BattleTests.cs + tests/stubs); a build
            // inside r16 compiles only the pure files and this test, and skips it
            var battle = typeof(IceFeaturesTests).Assembly.GetType("BattleTests");
            if (battle != null) battle.GetMethod("Run", System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic).Invoke(null, null);
            else Console.WriteLine("battle part: skipped (no stub game types in this build)");
            Console.WriteLine("ice features: " + checks + " checks passed");
            return 0;
        }
        catch (Exception e) { while (e is System.Reflection.TargetInvocationException && e.InnerException != null) e = e.InnerException; Console.WriteLine(e.Message); Console.WriteLine(e.StackTrace); return 1; }
    }

    internal static void Count(int n) { checks += n; }

    private static void Data()
    {
        foreach (var h in new[] { IceFeaturesData.ShelvesSha256, IceFeaturesData.FrontsSha256, IceFeaturesData.AttributesSha256, IceFeaturesData.ClimatologySha256, IceFeaturesData.CoastSha256 })
            Check(h.Length == 64, "source hash present");
        IceShelves.Load();
        Check(IceFeaturesData.ShelfFeature.Length == IceFeaturesData.ShelfName.Length && IceFeaturesData.ShelfPoly.Length == IceFeaturesData.ShelfFeature.Length + 1, "shelf table lengths");
        Check(IceShelves.Lines == 200 && IceShelves.Segments > 5000, "200 Natural Earth front lines, " + IceShelves.Segments + " segments");
        Check(IceShelves.MaxLat < -60 && IceShelves.MinLat > -86, "all shelves between 86S and 60S");
        Check(IceFeaturesData.Categories.Length == 7 && IceFeaturesData.RadarSeaStateFactor.Length == 70, "seven iceberg classes, sea states 0..9");
        Check(IceFeaturesData.ShelfToleranceKm == 0.5, "documented simplification tolerance 0.5 km");
        Check(!IceFeaturesData.Bands.Contains("giant"), "giant bergs are never generated");
        Check(IceFeaturesData.ShelfStatus == "ESTIMATE" && IceFeaturesData.ClimatologyStatus == "ESTIMATE", "both tables say ESTIMATE");
        Console.WriteLine("data: " + IceFeaturesData.ShelfFeature.Length + " shelves (" + IceFeaturesData.ShelfPts.Length / 2 + " points after simplification), " + IceShelves.Segments + " front segments, " + (IceFeaturesData.CoastStart.Length - 1) + " land rings");
    }

    private static void Shelves()
    {
        var g = IceFeaturesGolden.Shelf;
        int rows = g.Length / 7, agree = 0;
        double worstD = 0;
        for (int i = 0; i < rows; i++)
        {
            double lat = D(g[7 * i]), lon = D(g[7 * i + 1]);
            int simp = (int)g[7 * i + 2], full = (int)g[7 * i + 3];
            double dist = D(g[7 * i + 4]);
            int s = IceShelves.ShelfAt(lat, lon);
            int f = s >= 0 ? IceFeaturesData.ShelfFeature[s] : -1;
            Check(f == simp, "containment equals ice.IceShelf.contains on the simplified rings at " + F(lat) + ", " + F(lon) + " (" + f + " vs " + simp + ")");
            if (f == full) agree++;
            double d = IceShelves.DistanceToFrontNm(lat, lon);
            worstD = Math.Max(worstD, Math.Abs(d - dist));
            Check(Math.Abs(d - dist) <= 1e-9 * Math.Max(1, dist), "front distance equals iceshelves.distance_to_front_nm at " + F(lat) + ", " + F(lon) + ": " + d + " vs " + dist);
            double dc = IceShelves.DistanceToFrontNm(lat, lon, out _, 10.0);
            Check(dist <= 10.0 ? Math.Abs(dc - dist) <= 1e-9 * Math.Max(1, dist) : double.IsInfinity(dc), "culled front search agrees within 10 nm");
            Check((int)IceShelves.Navigation(lat, lon, false, out _) == (int)g[7 * i + 5], "surface navigation status at " + F(lat) + ", " + F(lon));
            Check((int)IceShelves.Navigation(lat, lon, true, out _) == (int)g[7 * i + 6], "submarine navigation status at " + F(lat) + ", " + F(lon));
        }
        // near a front the speed rule's inside/outside comes from the nearest segment's side (full outline)
        int near = 0, sideOk = 0, unsafeMiss = 0;
        for (int i = 0; i < rows; i++)
        {
            double lat = D(g[7 * i]), lon = D(g[7 * i + 1]), dist = D(g[7 * i + 4]);
            if (!(dist >= 0.02 && dist <= IceShelves.SideNearNm)) continue;
            near++;
            bool insideFull = (int)g[7 * i + 3] >= 0;
            bool insideRule = IceShelves.Clearance(lat, lon, 20) < 0;
            if (insideRule == insideFull) sideOk++;
            else if (!insideRule) unsafeMiss++;
        }
        // Natural Earth's lines and polygons do not coincide everywhere: a few points just behind a
        // front line lie outside the polygon (ice rise, land). The rule counts them as shelf: safe.
        Check(unsafeMiss == 0, "near a front the rule never calls shelf ice open water");
        Check(near > 20 && sideOk >= near * 0.95, "near a front the rule's side matches the full outline (" + sideOk + "/" + near + ")");
        Console.WriteLine("shelves: the speed rule's side matches the full outline at " + sideOk + " of " + near + " golden points 0.02-0.54 nm from a front (the rest err toward 'shelf')");
        Check(agree == IceFeaturesGolden.ShelfAgree, "agreement with the full outline as in Python (" + agree + "/" + rows + ")");
        Check(IceFeaturesGolden.ShelfWorstMismatchKm <= IceFeaturesData.ShelfToleranceKm * 1.05 + 0.01, "every disagreement lies within the tolerance of the full outline");
        int ross = IceShelves.ShelfAt(-80.0, -175.0);
        Check(ross >= 0 && IceFeaturesData.ShelfName[ross] == "Ross Ice Shelf", "80S 175W is on the Ross Ice Shelf");
        Check(IceShelves.ShelfAt(-60.0, 0.0) < 0 && IceShelves.ShelfAt(45, -49) < 0, "open ocean is not a shelf");
        Check(IceShelves.Clearance(45, -49, 5) == 5, "far from Antarctica the clearance is the cap");
        IceShelves.Cliff(IceFeaturesData.ShelfFeature[ross], out double fb, out double dr);
        Check(fb == 30 && dr == 190, "Ross front: typical freeboard 30 m (20-40 m observed), draft 190 m (derived)");
        Console.WriteLine("shelves: " + rows + " golden points; containment exact on the simplified rings; " + agree + "/" + rows + " agree with the full outline (worst miss " + F(IceFeaturesGolden.ShelfWorstMismatchKm) + " km from its edge); front distance worst difference " + worstD.ToString("E1", CultureInfo.InvariantCulture) + " nm");
    }

    private static void SpeedRule()
    {
        var s = new ShelfSpeedState();
        Check(s.Cap(20, 30, 10, 9, 0) == 20 && !s.Capped, "far from the front: no cap");
        Check(s.Cap(20, 30, 0.5, 0.2, 0) == 20, "closing but the samples stay outside the limit: no cap");
        Check(Math.Abs(s.Cap(20, 30, 0.2, -0.1, 0) - 3) < 1e-6 && s.Capped && !s.Stopped, "sample inside the shelf, hull outside: steerage way (0.1 of flank)");
        Check(s.Cap(20, 30, -0.001, -0.3, 0) == 0 && s.Stopped, "at the front and closing: stop");
        Check(s.Cap(-10, 30, -0.001, -0.3, 0) == 0, "backing into the shelf is stopped too");
        Check(s.Cap(20, 30, -0.05, 0.2, 0) == 20, "moving out of the no-go zone is never capped");
        Check(s.Cap(20, 30, 0.1, 0.1, 0.0) == 20, "same clearance (along the front, outside): not capped");
        Check(s.Cap(20, 30, 1.0, 1.0, 2.0) == 20 && !s.Capped, "submarine inside the stand-off moving along the front: not trapped");
        Check(Math.Abs(s.Cap(20, 30, 2.5, 1.5, 2.0) - 3) < 1e-6, "submarine closing on the stand-off: steerage way");
        Check(s.Cap(2, 30, 2.5, 1.5, 2.0) == 2, "a slow order below the cap is kept");
        Check(s.Cap(0, 30, 0, -1, 0) == 0 && float.IsNaN(s.Cap(float.NaN, 30, 0, -1, 0)), "zero and NaN orders pass through");
    }

    // A hull ordered at 30 kn toward the Ross front, one second steps: it never enters the shelf
    // (surface) or the stand-off (submarine) by more than one step, then leaves at full speed.
    private static void Track()
    {
        int line = -1;
        for (int l = 0; l < IceFeaturesData.FrontFeature.Length && line < 0; l++)
        {
            int s = IceShelves.ShelfOfFeature(IceFeaturesData.FrontFeature[l]);
            if (s >= 0 && IceFeaturesData.ShelfName[s] == "Ross Ice Shelf" && IceFeaturesData.FrontStart[l + 1] - IceFeaturesData.FrontStart[l] > 50) line = l;
        }
        Check(line >= 0, "a Ross front line");
        int k = (IceFeaturesData.FrontStart[line] + IceFeaturesData.FrontStart[line + 1]) / 2;
        double flat = IceFeaturesData.FrontPts[2 * k + 1] / 1000.0, flon = IceFeaturesData.FrontPts[2 * k] / 1000.0;
        foreach (bool sub in new[] { false, true })
        {
            double limit = sub ? IceFeaturesData.SubmarineStandoffNm : ShelfSpeedState.SurfaceLimitNm;
            IceFeatureGeo.Destination(flat, flon, 0, 6.0, out double lat, out double lon); // 6 nm north, at sea
            Check(IceShelves.Clearance(lat, lon, 20) > limit, "track starts outside the no-go zone");
            var st = new ShelfSpeedState();
            double minClear = double.PositiveInfinity, heading = 180;
            int stoppedSteps = 0;
            for (int t = 0; t < 3600; t++)
            {
                double here = IceShelves.Clearance(lat, lon, 20);
                minClear = Math.Min(minClear, here);
                double ahead = double.PositiveInfinity;
                foreach (var nm in ShelfSpeedState.AheadNm) { IceFeatureGeo.Destination(lat, lon, heading, nm, out double a, out double b); ahead = Math.Min(ahead, IceShelves.Clearance(a, b, 20)); }
                float kn = st.Cap(30f, 30f, here, ahead, limit);
                if (st.Stopped) stoppedSteps++;
                IceFeatureGeo.Destination(lat, lon, heading, kn / 3600.0, out lat, out lon);
            }
            double step = 30.0 / 3600.0;
            Check(minClear >= limit - 0.1 * step - 1e-6, (sub ? "submarine" : "surface ship") + " stays out of the no-go zone (least clearance " + F(minClear) + " nm, limit " + F(limit) + ")");
            Check(stoppedSteps > 0, "the hull ends up stopped at the limit");
            if (!sub) Check(minClear * 1852 > 150, "surface ship: the bow of a 300 m hull (150 m ahead of its centre) stays seaward of the front (" + F(minClear * 1852 - 150) + " m to spare)");
            heading = 0;
            double before = IceShelves.Clearance(lat, lon, 20), ah = double.PositiveInfinity;
            foreach (var nm in ShelfSpeedState.AheadNm) { IceFeatureGeo.Destination(lat, lon, heading, nm, out double a, out double b); ah = Math.Min(ah, IceShelves.Clearance(a, b, 20)); }
            Check(st.Cap(30f, 30f, before, ah, limit) == 30f, "turned away from the front: full speed");
            Console.WriteLine("track to the Ross front (" + (sub ? "submarine" : "surface") + "): least clearance " + F(minClear) + " nm against a limit of " + F(limit) + " nm; stopped " + stoppedSteps + " s of 3600");
        }
    }

    private static void Bergs()
    {
        var g = IceFeaturesGolden.Density;
        double worst = 0;
        for (int i = 0; i < g.Length; i += 10)
        {
            var d = IcebergField.Density(D(g[i]), D(g[i + 1]), D(g[i + 2]));
            for (int c = 0; c < 7; c++) worst = Math.Max(worst, Math.Abs(d[c] - D(g[i + 3 + c])) / Math.Max(1e-12, Math.Abs(D(g[i + 3 + c]))));
        }
        Check(worst < 1e-12, "density equals icebergs.density at " + g.Length / 10 + " points x months (worst relative " + worst + ")");
        var fm = IceFeaturesGolden.FractionalMonth;
        for (int i = 0; i < fm.Length; i += 4)
            Check(IcebergField.FractionalMonth(new DateTime((int)fm[i], (int)fm[i + 1], (int)fm[i + 2])) == D(fm[i + 3]), "fractional month");
        var r = IceFeaturesGolden.Radar;
        for (int i = 0; i < IceFeaturesGolden.RadarCategory.Length; i++)
        {
            int c = IcebergField.CategoryIndex(IceFeaturesGolden.RadarCategory[i]);
            int ss = (int)r[4 * i];
            Check(IcebergField.RadarFactor(c, ss) == D(r[4 * i + 1]), "radar factor " + IceFeaturesGolden.RadarCategory[i] + " sea state " + ss);
            Check(Math.Abs(IcebergField.RadarDetectionNm(c, ss) - D(r[4 * i + 2])) < 0.0051, "radar detection " + IceFeaturesGolden.RadarCategory[i] + " sea state " + ss);
            Check(Math.Abs(IcebergField.RadarDetectionNm(c, ss, 40.0, 2.0, true) - D(r[4 * i + 3])) < 0.0051, "enhanced radar detection");
        }
        Check(IcebergField.RadarFactor(0, 4) == 0 && IcebergField.RadarFactor(1, 5) == 0, "growlers lost from sea state 4, bergy bits from 5");
        var v = IceFeaturesGolden.Visual;
        for (int i = 0; i < IceFeaturesGolden.VisualCategory.Length; i++)
            Check(Math.Abs(IcebergField.VisualDetectionNm(IcebergField.CategoryIndex(IceFeaturesGolden.VisualCategory[i]), D(v[3 * i]), night: v[3 * i + 1] == 1) - D(v[3 * i + 2])) < 0.0051, "visual detection " + IceFeaturesGolden.VisualCategory[i]);
        var so = IceFeaturesGolden.Sonar;
        for (int i = 0; i < IceFeaturesGolden.SonarCategory.Length; i++)
            Check(Math.Abs(IcebergField.SonarFalseContactIndex(IcebergField.CategoryIndex(IceFeaturesGolden.SonarCategory[i]), D(so[3 * i]), D(so[3 * i + 1])) - D(so[3 * i + 2])) < 1e-12, "sonar false-contact index " + IceFeaturesGolden.SonarCategory[i]);
        Check(IcebergField.FalseContact((int)BergCategory.Medium, 80, 100) && !IcebergField.FalseContact((int)BergCategory.Medium, 20, 200) && !IcebergField.FalseContact((int)BergCategory.Growler, 4, 10), "false-contact flag: medium berg with its keel near the sonar, not a growler");
        var m = IceFeaturesGolden.Melt;
        for (int i = 0; i < m.Length; i += 13)
        {
            double L = D(m[i]), W = D(m[i + 1]), H = D(m[i + 2]), Dr = D(m[i + 3]), sst = D(m[i + 4]), ss = D(m[i + 5]), wind = D(m[i + 6]), frac = D(m[i + 7]);
            int days = IcebergField.RemainingLifeDays(L, W, H, Dr, sst, ss, wind, frac, out bool capped);
            Check(days == (int)D(m[i + 8]) && capped == (m[i + 9] == 1), "remaining_life_days " + days + " vs " + D(m[i + 8]));
            IcebergField.MeltRates(sst, L, double.IsNaN(ss) ? IcebergField.SeaStateFromWind(double.IsNaN(wind) ? 0 : wind) : ss, frac, double.NaN, out double basal, out double conv, out double wave);
            Check(Math.Abs(basal - D(m[i + 10])) <= 1e-12 && Math.Abs(conv - D(m[i + 11])) <= 1e-12 && Math.Abs(wave - D(m[i + 12])) <= 1e-12, "melt_rates");
        }
        var dp = IceFeaturesGolden.Displace;
        for (int i = 0; i < dp.Length; i += 6)
        {
            IceFeatureGeo.Displace(D(dp[i]), D(dp[i + 1]), D(dp[i + 2]), D(dp[i + 3]), out double lat, out double lon);
            Check(Math.Abs(lat - D(dp[i + 4])) < 1e-9 && Math.Abs(lon - D(dp[i + 5])) < 1e-9, "geo.displace (drift step)");
        }
        Console.WriteLine("icebergs: density, fractional month, radar, visual, sonar, melt and the drift step match the Python module");
    }

    private static void Generator()
    {
        int total = 0, lifeOff = 0, dimOff = 0;
        foreach (var c in IceFeaturesGolden.Generate)
        {
            var bergs = IcebergField.Generate(c.Lat0, c.Lat1, c.Lon0, c.Lon1, new DateTime(c.Y, c.M, c.D), c.Seed, sstC: c.Sst);
            Check(bergs.Count == c.Id.Length, "same number of bergs as icebergs.generate in " + c.Seed + "/" + c.Y + "-" + c.M + " box (" + bergs.Count + " vs " + c.Id.Length + ")");
            for (int i = 0; i < bergs.Count; i++)
            {
                var b = bergs[i];
                var n = c.Num;
                int o = 11 * i;
                Check(b.Id == c.Id[i] && b.CategoryName == c.Cat[i] && b.Region == c.Region[i], "berg " + i + ": " + b.Id + " vs " + c.Id[i]);
                Check(Math.Abs(b.Lat - D(n[o])) <= 5.0001e-5 && Math.Abs(IceFeatureGeo.LonDelta(b.Lon, D(n[o + 1]))) <= 5.0001e-5, "berg position " + b.Id);
                bool dims = Math.Abs(b.LengthM - D(n[o + 2])) <= 0.1001 && Math.Abs(b.WidthM - D(n[o + 3])) <= 0.1001 && Math.Abs(b.HeightM - D(n[o + 4])) <= 0.01001 && Math.Abs(b.DraftM - D(n[o + 5])) <= 0.1001 && Math.Abs(b.MassT - D(n[o + 6])) <= 0.1 * Math.Abs(D(n[o + 6]));
                Check(dims, "berg size " + b.Id);
                if (b.LengthM != D(n[o + 2]) || b.WidthM != D(n[o + 3]) || b.HeightM != D(n[o + 4]) || b.DraftM != D(n[o + 5]) || b.MassT != D(n[o + 6])) dimOff++;
                Check(Math.Abs(b.U - D(n[o + 7])) <= 0.0005 && Math.Abs(b.V - D(n[o + 8])) <= 0.0005, "berg drift " + b.Id);
                Check(Math.Abs(b.LifeDays - D(n[o + 9])) <= 1 && (b.LifeCapped == (n[o + 10] == 1)), "berg life " + b.Id + ": " + b.LifeDays + " vs " + D(n[o + 9]));
                if (b.LifeDays != (int)D(n[o + 9])) lifeOff++;
                Check(!IcebergField.Land(b.Lat, b.Lon) && (b.Lat >= -60 || IceShelves.ShelfAt(b.Lat, b.Lon) < 0), "never on land or a shelf");
            }
            total += bergs.Count;
        }
        Check(dimOff <= total / 50 && lifeOff <= total / 50, "rounding-tie differences stay rare (" + dimOff + " sizes, " + lifeOff + " lives of " + total + ")");
        Console.WriteLine("generator: " + total + " bergs in " + IceFeaturesGolden.Generate.Length + " boxes equal icebergs.generate (ids, classes, regions, positions, sizes, drift, life; " + dimOff + " size and " + lifeOff + " life rounding differences)");
    }

    private static void Behaviour()
    {
        var when = new DateTime(2028, 5, 15);
        var big = IcebergField.Generate(43.0, 47.0, -51.0, -45.0, when, "0");
        var small = IcebergField.Generate(44.0, 46.0, -50.0, -47.0, when, "0");
        var ids = new HashSet<string>(big.Select(b => b.Id));
        Check(small.All(b => ids.Contains(b.Id)), "a smaller box gives a subset of a bigger one");
        Check(IcebergField.Generate(44.0, 46.0, -50.0, -47.0, when, "1").Select(b => b.Id).SequenceEqual(small.Select(b => b.Id)) == false, "another seed gives other bergs");
        Check(IcebergField.Generate(33, 40, 10, 25, when, "s").Count == 0, "no bergs in the Mediterranean");
        // expected count in the Grand Banks in May vs the density (Poisson: within 5 sigma)
        double expect = 0;
        for (double la = 43.25; la < 47; la += 0.5) for (double lo = -50.75; lo < -45; lo += 0.5)
            {
                double area = Math.Pow(6371.0 * Math.PI / 360.0, 2) * Math.Cos(la * Math.PI / 180);
                expect += IcebergField.Density(la, lo, IcebergField.FractionalMonth(when)).Sum() * area / 1e4;
            }
        Check(Math.Abs(big.Count - expect) < 5 * Math.Sqrt(expect) + 5, "Grand Banks count " + big.Count + " near the expected " + F(expect));
        // drift: 0.2 m/s south for one hour = 0.3888 nm
        var berg = big.First(b => b.Region == "grand_banks");
        double lat0 = berg.Lat, lon0 = berg.Lon;
        IcebergField.Drift(berg, 3600);
        Check(Math.Abs(IceFeatureGeo.GreatCircleNm(lat0, lon0, berg.Lat, berg.Lon) - 0.2 * IceFeatureGeo.KnotsPerMs) < 1e-6 && berg.Lat < lat0, "drift: 0.2 m/s south (Labrador Current proxy) for an hour");
        // decay
        var g = new Berg { Category = BergCategory.Growler, LengthM = 3, WidthM = 2.5, HeightM = 0.5, DraftM = 3 };
        Check(IcebergField.Melt(g, 3600, double.NaN, 3, 0) && g.LengthM == 3, "no sea temperature: no decay");
        int hours = 0;
        while (IcebergField.Melt(g, 3600, 4.0, 3, 0) && hours < 10000) hours++;
        Check(g.Gone && hours > 0 && hours < 24 * 10, "a growler at 4 C in sea state 3 melts within days (" + hours + " h)");
        int days = IcebergField.RemainingLifeDays(3, 2.5, 0.5, 3, 4.0, 3, double.NaN, 0, out _);
        Check(Math.Abs(hours / 24.0 - days) <= 1.5, "continuous decay agrees with remaining_life_days (" + hours + " h vs " + days + " d)");
        Check(new PyRandom("abc").Random() == new PyRandom("abc").Random(), "the stream is repeatable");
        // meshes: closed bergs wound outward (positive signed volume), sized by the class dims
        foreach (BergCategory cat in Enum.GetValues(typeof(BergCategory)))
        {
            var mesh = BergMesher.Build(cat, 120, 90, 40, 80, 12345u);
            double vol = 0, minY = double.MaxValue, maxY = double.MinValue;
            for (int t = 0; t < mesh.T.Count; t += 3)
            {
                int a = 3 * mesh.T[t], b = 3 * mesh.T[t + 1], c = 3 * mesh.T[t + 2];
                var V = mesh.V;
                vol += (V[a] * (V[b + 1] * V[c + 2] - V[b + 2] * V[c + 1]) - V[a + 1] * (V[b] * V[c + 2] - V[b + 2] * V[c]) + V[a + 2] * (V[b] * V[c + 1] - V[b + 1] * V[c])) / 6.0;
            }
            for (int i = 1; i < mesh.V.Count; i += 3) { minY = Math.Min(minY, mesh.V[i]); maxY = Math.Max(maxY, mesh.V[i]); }
            Check(vol > 0, cat + " berg mesh is closed and wound outward (volume " + F(vol) + " m3)");
            Check(Math.Abs(maxY - 40) < 1e-3 && Math.Abs(minY + 80) < 1e-3, cat + " berg mesh: top at the height, keel at the draft below the waterline");
        }
        var cliff = CliffMesher.Build(new[] { 0.0, 1000.0 }, new[] { 0.0, 0.0 }, +1, 30, 190, 1500);
        int faces = 0;
        for (int t = 0; t < cliff.T.Count; t += 3)
        {
            int a = 3 * cliff.T[t], b = 3 * cliff.T[t + 1], c = 3 * cliff.T[t + 2];
            var V = cliff.V;
            if (V[a + 2] != 0 || V[b + 2] != 0 || V[c + 2] != 0) continue; // the seaward face lies on z = 0
            double ux = V[b] - V[a], uy = V[b + 1] - V[a + 1], vx = V[c] - V[a], vy = V[c + 1] - V[a + 1];
            Check(ux * vy - uy * vx < 0, "seaward face points away from the shelf (south when the shelf is north)");
            faces++;
        }
        Check(faces == 2 && cliff.Triangles == 8, "one segment: face, top, underside and inland wall");
    }
}
