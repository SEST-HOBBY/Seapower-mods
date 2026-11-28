using System;
using System.Collections.Generic;
using System.Globalization;

namespace Sest.RuntimeFixes;

// The pure part of SEST's campaign-map sea ice (CampaignIce=1 in [Runtime]):
// the per-date ice raster over a Dynamic Campaign Mod theatre, its colours
// (fill, the ice edge line (IceEdge, 10 % by default) and the 60 % heavy-pack line), compositing it over
// DCM's straight-alpha RGBA32 weather image, the hover readout line and the
// group speed factor. No Unity, Noesis or DCM types: CampaignIceTests.exe runs
// all of it under Mono, and the raster is built on worker threads.
//
// One model for map, campaign movement and battle: every concentration comes
// from SeaIceModel (the weather branch's seaice.py climatology), at a pixel
// centre for the map, and through a SeaIceTileCache (0.05-degree tiles, the
// battle's own cache type) for a group's position.
internal static class CampaignIceStyle
{
    // The ice edge: IceEdge.Percent, the battle's own (10 % by default, where
    // a class-none group starts to slow; SeaIceEdgePercent=15 gives the NSIDC
    // extent line), so the fill and the cyan line start where the slowing does.
    internal static double EdgePercent => IceEdge.Percent;
    internal const double HeavyPercent = 60.0;  // heavy pack: "blocked" for ice class none (ice.py)
    // Straight RGBA. Fill: pale ice white-blue, opacity follows concentration
    // from 0.30 at the edge to 0.85 at the model's 98 % maximum.
    internal static readonly byte[] Fill = { 232, 244, 255 };
    internal static readonly byte[] EdgeLine = { 0, 200, 255 };   // cyan: reads on dark sea and on the fill
    internal static readonly byte[] HeavyLine = { 10, 40, 120 };  // navy: reads on the pale fill
    internal const double FillAlphaAtEdge = 0.30, FillAlphaAtMax = 0.85;

    internal static double FillAlpha(double percent)
    {
        if (!(percent >= EdgePercent)) return 0.0;
        double t = (percent - EdgePercent) / (SeaIceModel.MaxPercent - EdgePercent);
        if (t > 1) t = 1;
        return FillAlphaAtEdge + (FillAlphaAtMax - FillAlphaAtEdge) * t;
    }

    internal static string Category(double percent) =>
        percent >= HeavyPercent ? "heavy pack" : percent >= EdgePercent ? "pack ice" : "drift ice";

    // The map readout: null below 1 % or on land.
    internal static string HoverLine(double percent, bool water)
    {
        if (!water || double.IsNaN(percent) || percent < 1.0) return null;
        return "Ice " + Math.Round(percent).ToString("0", CultureInfo.InvariantCulture) + " % (" + Category(percent) + ")";
    }

    // The readout's second line: what the ice does to a group of ice class
    // "none" (every unit today, ice-capability.json is empty on purpose).
    internal static string HoverEffect(double percent, bool water)
    {
        if (HoverLine(percent, water) == null) return null;
        var access = IceRules.Access(percent, 0);
        if (access == IceAccess.Open) return null;
        double f = CampaignIceSpeed.Factor(percent, 0);
        string speed = Math.Round(f * 100).ToString("0", CultureInfo.InvariantCulture) + " % speed";
        return "Surface groups " + speed + (access == IceAccess.Blocked ? " (beset)" : "") + "; submarines pass under";
    }
}

// A group's speed in ice. The ice.py access level of each surface hull's ice
// class at the group's position sets a ceiling of factor x the group's FULL
// speed (DCM's Logistics.SpeedOf: what its slowest hull makes at the
// telegraph step, with damage, convoy and fuel limits), the slowest surface
// hull setting the factor; submarines pass under the ice, so a group of only
// submarines is never slowed. The ceiling goes into TaskForce.WeatherKnots,
// which DCM treats as an absolute limit: Movement.SpeedOf = min(ordered,
// WeatherKnots), and the AI's Rhythm.ClosingHours / Hold plan with
// min(Logistics.SpeedOf, WeatherKnots). "Blocked" (factor 0 in ice.py) is BesetFactor here, not 0: DCM's
// TaskForce.WeatherKnots <= 0 means "no cap" (Movement.WeatherCapOf returns
// +Infinity), HoursToRoutePoints returns an all-zero ETA array at 0 knots,
// and a group the ice grew over must still be able to work its way out.
internal static class CampaignIceSpeed
{
    internal const double BesetFactor = 0.1;
    internal const double CellDegrees = SeaIceTileCache.TileDegrees;

    internal static double Factor(double percent, int capability)
    {
        var a = IceRules.Access(percent, capability);
        return a == IceAccess.Blocked ? BesetFactor : IceRules.SpeedFactor[(int)a];
    }

    // capabilities: one entry per hull, -1 for a submarine. 1.0 when no
    // surface hull is in the group.
    internal static double GroupFactor(double percent, IList<int> capabilities)
    {
        double f = 1.0;
        foreach (int c in capabilities)
            if (c >= 0) f = Math.Min(f, Factor(percent, c));
        return f;
    }

    internal static bool GroupBeset(double percent, IList<int> capabilities)
    {
        foreach (int c in capabilities)
            if (c >= 0 && IceRules.Access(percent, c) == IceAccess.Blocked) return true;
        return false;
    }

    // The cap DCM's TaskForce.WeatherKnots gets: the weather cap (<= 0 = none)
    // or the ice cap (factor x full speed), whichever is lower. The ordered
    // speed plays no part, so a stopped or slow group is capped too. Nothing
    // is written for a group that can make no speed at all (0 would read as
    // "no cap").
    internal static double Cap(double weatherKnots, double fullKnots, double factor, out bool iceBinds)
    {
        iceBinds = false;
        if (!(factor < 1.0) || !(fullKnots > 0)) return weatherKnots;
        double ice = factor * fullKnots;
        if (weatherKnots > 0 && weatherKnots <= ice) return weatherKnots;
        iceBinds = true;
        return ice;
    }

    // DCM's two "held by weather" texts: Movement.SpeedText's, and the one
    // FleetViewModel.Line formats itself for a group out of fuel.
    internal const string HeavySeas = "(heavy seas)";
    internal const string IceText = "(ice)";
    internal const string OutOfFuelHeavySeas = "(out of fuel, heavy seas)";
    internal const string OutOfFuelIce = "(out of fuel, ice)";
    internal static string Text(string dcmText, bool iceBinds)
    {
        if (!iceBinds || dcmText == null) return dcmText;
        if (dcmText.Contains(HeavySeas)) dcmText = dcmText.Replace(HeavySeas, IceText);
        if (dcmText.Contains(OutOfFuelHeavySeas)) dcmText = dcmText.Replace(OutOfFuelHeavySeas, OutOfFuelIce);
        return dcmText;
    }
}

// The ice raster over a theatre box: row 0 is the southern row and column 0
// the western one, pixel centres at (south + (y + 0.5) cell, west + (x + 0.5)
// cell) -- DCM's own WeatherFrame layout (WaterOf, Image) and that of the
// RGBA32 texture GlobeDrape drapes (Unity's first row is the bottom one).
internal sealed class IceRaster
{
    internal readonly double South, West, Cell;
    internal readonly int Width, Height, DateKey;
    internal readonly float[] Percent;
    internal int IcePixels, HeavyPixels;
    internal double BuildMs, MaxPercent;

    internal IceRaster(double south, double west, double cell, int width, int height, DateTime date)
    {
        if (width <= 0 || height <= 0 || !(cell > 0)) throw new ArgumentException("ice raster size");
        South = south; West = west; Cell = cell; Width = width; Height = height;
        DateKey = SeaIceTileCache.DateKeyOf(date);
        Percent = new float[width * height];
        var sw = System.Diagnostics.Stopwatch.StartNew();
        var e = SeaIceModel.EdgesOn(date);
        for (int y = 0; y < height; y++)
        {
            double lat = south + (y + 0.5) * cell;
            int row = y * width;
            if (Math.Abs(lat) < 40) continue; // SeaIceModel.IceAt is 0 there (and wraps lon: west may pass -180)
            for (int x = 0; x < width; x++)
            {
                float c = (float)SeaIceModel.IceAt(lat, west + (x + 0.5) * cell, e);
                Percent[row + x] = c;
                if (c > MaxPercent) MaxPercent = c;
            }
        }
        BuildMs = sw.Elapsed.TotalMilliseconds;
    }

    internal double North => South + Height * Cell;
    internal double East => West + Width * Cell;
    internal double LatOf(int y) => South + (y + 0.5) * Cell;
    internal double LonOf(int x) => West + (x + 0.5) * Cell;
    internal bool Same(double south, double west, double cell, int width, int height, int dateKey) =>
        South == south && West == west && Cell == cell && Width == width && Height == height && DateKey == dateKey;

    // Theatre box -> raster size at the requested cell, coarsened so the
    // raster stays within maxPixels (a world-sized theatre at 0.1 degrees
    // would be 6.5 million pixels).
    internal static double CellFor(double latMin, double latMax, double lonMin, double lonMax, double cell, int maxPixels)
    {
        double area = Math.Max(0, latMax - latMin) * Math.Max(0, lonMax - lonMin);
        cell = Math.Max(cell, Math.Sqrt(area / maxPixels));
        for (int k = 0; k < 100; k++) // the Ceiling in SizeOf can add a row and a column
        {
            SizeOf(latMin, latMax, lonMin, lonMax, cell, out int w, out int h);
            if ((long)w * h <= maxPixels) break;
            cell *= 1.01;
        }
        return cell;
    }
    internal static void SizeOf(double latMin, double latMax, double lonMin, double lonMax, double cell, out int width, out int height)
    {
        width = Math.Max(1, (int)Math.Ceiling((lonMax - lonMin) / cell));
        height = Math.Max(1, (int)Math.Ceiling((latMax - latMin) / cell));
    }

    // What one pixel shows. 0 none, 1 fill, 2 the ice edge line, 3 the 60 %
    // heavy-pack line. A line pixel is a water pixel at or over the threshold
    // with a 4-neighbour under it (a land neighbour counts by its model value,
    // so the line runs on along a coast the edge meets, but is only drawn on
    // water). water == null: every pixel is water.
    internal int KindAt(int x, int y, bool[] water)
    {
        int i = y * Width + x;
        if (water != null && !water[i]) return 0;
        float c = Percent[i];
        if (!(c >= CampaignIceStyle.EdgePercent)) return 0;
        if (Below(x, y, CampaignIceStyle.EdgePercent)) return 2;
        if (c >= CampaignIceStyle.HeavyPercent && Below(x, y, CampaignIceStyle.HeavyPercent)) return 3;
        return 1;
    }

    private bool Below(int x, int y, double t)
    {
        if (x > 0 && Percent[y * Width + x - 1] < t) return true;
        if (x + 1 < Width && Percent[y * Width + x + 1] < t) return true;
        if (y > 0 && Percent[(y - 1) * Width + x] < t) return true;
        if (y + 1 < Height && Percent[(y + 1) * Width + x] < t) return true;
        return false;
    }

    // How strongly a line pixel draws its line (28 Nov 2026): 1 where the
    // threshold crosses the pixel centre, fading to LineAlphaMin where the
    // pixel's own value is a whole neighbour step past it. DCM's weather grid
    // is coarse near the pole, and a hard one-pixel line there read as
    // stair-steps; the fill shows through the faded part.
    internal const double LineAlphaMin = 0.35;
    internal double LineAlpha(int x, int y, double t)
    {
        double c = Percent[y * Width + x], step = 0;
        void Step(int i) { double d = c - Percent[i]; if (Percent[i] < t && d > step) step = d; }
        if (x > 0) Step(y * Width + x - 1);
        if (x + 1 < Width) Step(y * Width + x + 1);
        if (y > 0) Step((y - 1) * Width + x);
        if (y + 1 < Height) Step((y + 1) * Width + x);
        if (!(step > 0)) return 1.0;
        // The contour sits (c - t) / step of a pixel from this centre, towards the lower neighbour.
        double off = (c - t) / step;
        return Math.Max(LineAlphaMin, Math.Min(1.0, 1.0 - off));
    }

    // One ice pixel over px at o: the fill, then a line pixel's line at its alpha.
    internal void Shade(int x, int y, int kind, byte[] px, int o)
    {
        double c = Percent[y * Width + x];
        Colour(1, c, out byte r, out byte g, out byte b, out double a);
        Over(px, o, r, g, b, a);
        if (kind == 1) return;
        Colour(kind, c, out r, out g, out b, out _);
        Over(px, o, r, g, b, LineAlpha(x, y, kind == 2 ? CampaignIceStyle.EdgePercent : CampaignIceStyle.HeavyPercent));
    }

    // The ice alone: straight RGBA32, transparent where there is no ice.
    internal byte[] Paint(bool[] water)
    {
        var px = new byte[Width * Height * 4];
        int ice = 0, heavy = 0;
        for (int y = 0; y < Height; y++)
            for (int x = 0; x < Width; x++)
            {
                int k = KindAt(x, y, water);
                if (k == 0) continue;
                int i = y * Width + x;
                ice++;
                if (Percent[i] >= CampaignIceStyle.HeavyPercent) heavy++;
                Shade(x, y, k, px, i * 4);
            }
        IcePixels = ice; HeavyPixels = heavy;
        return px;
    }

    // Over DCM's weather image (WeatherFrame.Pixels, straight RGBA32 as
    // WeatherFrame.Pixel writes it): ice alpha-over the weather. Same size
    // only; returns the number of pixels changed.
    internal int Composite(byte[] pixels, bool[] water)
    {
        if (pixels == null || pixels.Length != Width * Height * 4) return -1;
        if (water != null && water.Length != Width * Height) water = null;
        int changed = 0;
        for (int y = 0; y < Height; y++)
            for (int x = 0; x < Width; x++)
            {
                int k = KindAt(x, y, water);
                if (k == 0) continue;
                Shade(x, y, k, pixels, (y * Width + x) * 4);
                changed++;
            }
        return changed;
    }

    internal static void Colour(int kind, double percent, out byte r, out byte g, out byte b, out double a)
    {
        byte[] c = kind == 2 ? CampaignIceStyle.EdgeLine : kind == 3 ? CampaignIceStyle.HeavyLine : CampaignIceStyle.Fill;
        r = c[0]; g = c[1]; b = c[2];
        a = kind == 1 ? CampaignIceStyle.FillAlpha(percent) : 1.0;
    }

    // Straight-alpha "over": out_a = a + d_a (1 - a); out_rgb = (src a + dst d_a (1 - a)) / out_a.
    internal static void Over(byte[] px, int o, byte r, byte g, byte b, double a)
    {
        double da = px[o + 3] / 255.0;
        double oa = a + da * (1 - a);
        if (oa <= 0) { px[o] = px[o + 1] = px[o + 2] = px[o + 3] = 0; return; }
        double k = da * (1 - a);
        px[o] = (byte)Math.Round(Math.Min(255.0, (r * a + px[o] * k) / oa));
        px[o + 1] = (byte)Math.Round(Math.Min(255.0, (g * a + px[o + 1] * k) / oa));
        px[o + 2] = (byte)Math.Round(Math.Min(255.0, (b * a + px[o + 2] * k) / oa));
        px[o + 3] = (byte)Math.Round(Math.Min(255.0, oa * 255));
    }
}

// The last rasters built, by box and date, shared by the worker threads that
// build DCM's weather frames: the concentration of a theatre is computed once
// per campaign date and box, not once per weather frame.
internal sealed class IceRasterCache
{
    private readonly object gate = new object();
    private readonly List<IceRaster> kept = new List<IceRaster>();
    private const int Keep = 3;
    internal int Builds, Hits;

    internal IceRaster Get(double south, double west, double cell, int width, int height, DateTime date)
    {
        int dk = SeaIceTileCache.DateKeyOf(date);
        lock (gate)
        {
            foreach (var r in kept)
                if (r.Same(south, west, cell, width, height, dk)) { Hits++; return r; }
        }
        var built = new IceRaster(south, west, cell, width, height, date);
        lock (gate)
        {
            Builds++;
            kept.Insert(0, built);
            if (kept.Count > Keep) kept.RemoveAt(kept.Count - 1);
        }
        return built;
    }
}
