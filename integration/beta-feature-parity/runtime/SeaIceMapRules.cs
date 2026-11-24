using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace Sest.RuntimeFixes;

// The pure part of SEST's battle-map sea ice (SeaIceMapLayer=1 in [Runtime],
// default on, needs SeaIce=1; SeaIceMap.cs draws it): the concentration grid over the part of the globe
// the tactical map shows, the ice edge and heavy-pack lines through it
// (marching squares, linear along each cell side), the fill polygons by
// concentration band, and the hover text. No Unity, Noesis or game types:
// SeaIceTests.exe runs all of it under Mono.
//
// Same model, same look as the campaign map (CampaignIceStyle): every value
// is SeaIceModel's at a grid node on the battle's calendar date; pale
// white-blue fill whose opacity follows the concentration (0.30 at the edge
// to 0.85 at 98 %), the edge line cyan, the heavy-pack line navy. The battle
// thresholds are the battle's own (SeaIceEdgePercent, SeaIceSubHeavyPercent;
// 15 and 60 by default, the campaign map's constants).
internal static class IceMapStyle
{
    // Fill bands (lower bounds, percent): a band is filled with the opacity of
    // its middle, so a few Paths draw the whole pack.
    internal static readonly double[] BandFloors = { 15, 30, 45, 60, 80 };
    internal const double LineEdgePx = 1.8, LineHeavyPx = 1.4;
    // The map fill is lighter than the campaign globe's: the top band stops
    // at 0.60 (SeaIceMapOpacity scales it, 0.1-1, default 0.70).
    internal const double FillScale = 0.70, MinScale = 0.1, MaxScale = 1.0;

    // SeaIceMapOpacity=<x>: a number in [0.1, 1], else the default.
    internal static double Scale(string text) =>
        double.TryParse(text, NumberStyles.Float, CultureInfo.InvariantCulture, out double v) && v >= MinScale && v <= MaxScale ? v : FillScale;

    internal static int Band(double percent, double edge)
    {
        if (!(percent >= edge)) return -1;
        int b = 0;
        for (int i = 1; i < BandFloors.Length; i++) if (percent >= Math.Max(edge, BandFloors[i])) b = i;
        return b;
    }

    internal static double BandAlpha(int band, double edge, double scale = FillScale)
    {
        double lo = Math.Max(edge, BandFloors[band]);
        double hi = band + 1 < BandFloors.Length ? BandFloors[band + 1] : SeaIceModel.MaxPercent;
        double mid = Math.Max(edge, (lo + hi) / 2);
        double t = (mid - edge) / Math.Max(1e-9, SeaIceModel.MaxPercent - edge);
        if (t > 1) t = 1;
        return scale * (CampaignIceStyle.FillAlphaAtEdge + (CampaignIceStyle.FillAlphaAtMax - CampaignIceStyle.FillAlphaAtEdge) * t);
    }

    // The readout: "Ice 72 % (heavy pack)" and, on a second line, what the
    // battle's own rules do there to a ship of ice class none and to a
    // submarine (a part switched off or stopped, SeaIceShips / SeaIceSubmarines,
    // is left out of the line); null under 1 %.
    internal static string Hover(double percent, double heavy, double keelMeters, bool shipsOn = true, bool subsOn = true)
    {
        string line = CampaignIceStyle.HoverLine(percent, true);
        if (line == null) return null;
        var access = IceRules.Access(percent, 0);
        string ships = !shipsOn ? null : access == IceAccess.Open ? "ships unhindered" : access == IceAccess.Blocked ? "ice class none beset (steerage way only)" :
            "ice class none " + Math.Round(IceRules.SpeedFactor[(int)access] * 100).ToString("0", CultureInfo.InvariantCulture) + " % speed";
        string subs = !subsOn ? null : percent >= heavy ? "submarines held below " + Math.Round(keelMeters).ToString("0", CultureInfo.InvariantCulture) + " m outside leads" : "submarines may surface";
        string second = ships != null && subs != null ? ships + "; " + subs : ships ?? subs;
        return second == null ? line : line + "\n" + second;
    }

    // The concentration the battle itself uses at a point: the value of its
    // 0.05-degree tile (SeaIceTileCache: tile centre, 0 between 39.9S and
    // 39.9N), computed without touching the battle's cache. The readout shows
    // this, not the drawn grid (cells up to 5 degrees at whole-disk zoom), so
    // it always matches the speed caps and the submarine hold.
    internal static double BattlePercent(double lat, double lon, DateTime date)
    {
        if (double.IsNaN(lat) || double.IsNaN(lon) || double.IsInfinity(lat) || double.IsInfinity(lon) || Math.Abs(lat) < 39.9) return 0.0;
        SeaIceTileCache.TileCentre(SeaIceTileCache.Key(lat, lon), out double clat, out double clon);
        return SeaIceModel.Concentration(clat, clon, date);
    }

    // Which tactical MapBase to draw on: a newly rendered tactical map is
    // adopted only when none is held or the held one is gone or hidden, so two
    // maps on the same view model (a popped-out map) do not swap the overlay
    // (and rebuild the grid) every frame.
    internal static bool Adopt(bool candidateTactical, bool haveCurrent, bool currentVisible) =>
        candidateTactical && (!haveCurrent || !currentVisible);

    // Re-projection throttle: at least ProjectEvery apart, and the last
    // redraw's cost x 10, so redraws take at most ~10 % of real time.
    internal static double ProjectGap(double minGap, double lastRedrawMs) =>
        lastRedrawMs > 0 ? Math.Max(minGap, Math.Min(1.0, 10 * lastRedrawMs / 1000.0)) : minGap;
}

// Land cells already sampled (TerrainUtils.GetHeightAt at the cell centre),
// by cell size and centre, so a pan that rebuilds the grid at the same zoom
// does not sample them again. Cleared at Capacity. Main thread only.
internal sealed class IceLandCache
{
    internal const int Capacity = 200000;
    private readonly Dictionary<long, bool> cells = new Dictionary<long, bool>();
    internal int Hits, Misses, Clears;

    internal static long Key(double cellLat, double lat, double lon)
    {
        long size = (long)Math.Round(cellLat * 100);                 // 5 .. 500
        long y = (long)Math.Round((lat + 90.0) * 100);               // 0 .. 18000
        long x = (long)Math.Round(SeaIceModel.PyMod(lon + 180.0, 360.0) * 100); // 0 .. 36000
        return (size * 20000 + y) * 40000 + x;
    }

    internal bool TryGet(long key, out bool land)
    {
        if (cells.TryGetValue(key, out land)) { Hits++; return true; }
        Misses++;
        return false;
    }

    internal void Put(long key, bool land)
    {
        if (cells.Count >= Capacity) { cells.Clear(); Clears++; }
        cells[key] = land;
    }

    internal int Count => cells.Count;
}

// A concentration grid: node (r, c) at (South + r CellLat, West + c CellLon),
// r = 0..Rows, c = 0..Cols; cell (r, c) lies between nodes r..r+1, c..c+1.
// West may run past 180 (a box across the antimeridian); SeaIceModel wraps.
internal sealed class IceMapGrid
{
    internal const double MinCell = 0.05;           // the battle tile size (SeaIceTileCache)
    internal const int MaxRows = 96, MaxCols = 160;  // at most 15,617 nodes
    internal const int MaxVertices = 60000;          // more: lines only, the fill left out (logged once)
    internal static readonly double[] Steps = { 0.05, 0.1, 0.2, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0 };

    internal readonly double South, West, CellLat, CellLon;
    internal readonly int Rows, Cols, DateKey;
    internal readonly float[] Node;   // (Rows + 1) x (Cols + 1), percent
    internal bool[] Land;             // Rows x Cols, cell centres; null = no mask
    internal int IceCells;
    internal double MaxPercent;

    internal IceMapGrid(double south, double west, double cellLat, double cellLon, int rows, int cols, DateTime date)
    {
        South = south; West = west; CellLat = cellLat; CellLon = cellLon; Rows = rows; Cols = cols;
        DateKey = SeaIceTileCache.DateKeyOf(date);
        Node = new float[(rows + 1) * (cols + 1)];
        var e = SeaIceModel.EdgesOn(date);
        for (int r = 0; r <= rows; r++)
        {
            double lat = Math.Max(-90, Math.Min(90, south + r * cellLat));
            for (int c = 0; c <= cols; c++)
            {
                double v = SeaIceModel.IceAt(lat, west + c * cellLon, e);
                Node[r * (cols + 1) + c] = (float)v;
                if (v > MaxPercent) MaxPercent = v;
            }
        }
    }

    internal float At(int r, int c) => Node[r * (Cols + 1) + c];
    internal double LatOf(int r) => South + r * CellLat;
    internal double LonOf(int c) => West + c * CellLon;
    internal double North => South + Rows * CellLat;
    internal double East => West + Cols * CellLon;
    internal bool IsLand(int r, int c) => Land != null && Land[r * Cols + c];
    internal double CellMean(int r, int c) => (At(r, c) + At(r, c + 1) + At(r + 1, c) + At(r + 1, c + 1)) / 4.0;

    // The box may be unwrapped around another longitude than the grid (a view
    // centre that crossed 180 degrees): it is tried shifted by whole turns.
    internal bool Covers(double s, double n, double w, double e)
    {
        if (!(s >= South - 1e-9 && n <= North + 1e-9)) return false;
        double shift = Math.Round((West + East - w - e) / 720.0) * 360.0;
        return w + shift >= West - 1e-9 && e + shift <= East + 1e-9;
    }

    // The grid for a visible box (degrees; w..e unwrapped, e > w): padded by a
    // quarter of the view on each side so small pans do not rebuild, cells
    // from the step list (square in km at the box's middle latitude: the
    // longitude step is the latitude step x a whole factor >= 1/cos lat),
    // edges snapped to whole cells so a rebuild at the same zoom gives the
    // same nodes. Null when the box has no polar water (never ice).
    internal static IceMapGrid For(double s, double n, double w, double e, DateTime date)
    {
        Plan(s, n, w, e, out double south, out double west, out double cellLat, out double cellLon, out int rows, out int cols);
        if (rows <= 0 || cols <= 0) return null;
        return new IceMapGrid(south, west, cellLat, cellLon, rows, cols, date);
    }

    internal static void Plan(double s, double n, double w, double e, out double south, out double west, out double cellLat, out double cellLon, out int rows, out int cols)
    {
        south = west = cellLat = cellLon = 0; rows = cols = 0;
        if (double.IsNaN(s) || double.IsNaN(n) || double.IsNaN(w) || double.IsNaN(e) || n <= s || e <= w) return;
        double padLat = (n - s) / 4, padLon = (e - w) / 4;
        s = Math.Max(-90, s - padLat); n = Math.Min(90, n + padLat);
        if (e - w + 2 * padLon >= 360) { w = -180; e = 180; } else { w -= padLon; e += padLon; }
        // no sea ice between 40S and 40N (SeaIceModel.IceAt)
        if (s > -40 && n < 40) return;
        double mid = Math.Abs((s + n) / 2);
        double cos = Math.Max(0.1, Math.Cos(Math.Min(89.0, mid) * Math.PI / 180));
        int k = (int)Math.Ceiling(1 / cos - 1e-9);
        cellLat = 0;
        foreach (double step in Steps)
            if ((n - s) / step <= MaxRows && (e - w) / (step * k) <= MaxCols) { cellLat = step; break; }
        if (cellLat == 0) cellLat = Math.Ceiling(Math.Max((n - s) / MaxRows, (e - w) / (k * MaxCols)) * 2) / 2;
        cellLon = cellLat * k;
        south = Math.Floor(s / cellLat) * cellLat;
        west = Math.Floor(w / cellLon) * cellLon;
        rows = Math.Min(MaxRows + 2, (int)Math.Ceiling((n - south) / cellLat - 1e-9));
        cols = Math.Min(MaxCols + 2, (int)Math.Ceiling((e - west) / cellLon - 1e-9));
        if (south + rows * cellLat > 90) rows = (int)Math.Floor((90 - south) / cellLat + 1e-9);
    }
}

internal static class IceMapGeometry
{
    // Does the drawn grid still serve this view? Rebuild on a new calendar
    // day, a box the grid does not cover, or a zoom that plans another cell
    // size; a view with no polar water needs no grid (Clear when one is held).
    internal enum Need { Keep, Rebuild, Clear }
    internal static Need Check(IceMapGrid g, double s, double n, double w, double e, DateTime date)
    {
        IceMapGrid.Plan(s, n, w, e, out _, out _, out double cellLat, out _, out int rows, out int cols);
        if (rows <= 0 || cols <= 0) return g == null ? Need.Keep : Need.Clear;
        if (g == null || g.DateKey != SeaIceTileCache.DateKeyOf(date) || Math.Abs(g.CellLat - cellLat) > 1e-9 || !g.Covers(s, n, w, e)) return Need.Rebuild;
        return Need.Keep;
    }

    // The nine view probes (centre first, then corners and side middles) of a
    // w x h view.
    internal static double[][] Probes(double w, double h) => new[]
    {
        new[] { w / 2, h / 2 }, new[] { 0.0, 0.0 }, new[] { w, 0.0 }, new[] { w, h }, new[] { 0.0, h },
        new[] { w / 2, 0.0 }, new[] { w, h / 2 }, new[] { w / 2, h }, new[] { 0.0, h / 2 }
    };

    // The box for the probes that reached the globe (null where one did
    // not). The centre must; a probe off the globe (the whole disk in view)
    // takes the whole circle and 90 degrees of latitude either side of the
    // centre, with the pole on that side.
    internal static bool BoxOfProbes(double[][] geo, out double s, out double n, out double w, out double e)
    {
        s = n = w = e = 0;
        if (geo == null || geo.Length == 0 || geo[0] == null) return false;
        var on = new List<double[]>();
        bool off = false;
        foreach (var p in geo) if (p == null) off = true; else on.Add(p);
        if (off)
        {
            s = Math.Max(-90, geo[0][0] - 90); n = Math.Min(90, geo[0][0] + 90); w = -180; e = 180;
            return true;
        }
        return BoxOf(on, PoleInView(on), out s, out n, out w, out e);
    }

    // The box the map shows, from view points turned to geo (lat, lon; points
    // off the globe left out): longitudes unwrapped around the first point (the
    // view centre), the whole circle when a pole is in view or the points span
    // more than 180 degrees. False when fewer than two points are on the globe.
    internal static bool BoxOf(IList<double[]> points, bool poleInView, out double s, out double n, out double w, out double e)
    {
        s = 90; n = -90; w = 1e9; e = -1e9;
        if (points == null || points.Count < 2) return false;
        double lon0 = points[0][1];
        foreach (var p in points)
        {
            if (p[0] < s) s = p[0];
            if (p[0] > n) n = p[0];
            double lon = lon0 + SeaIceModel.LonDelta(p[1], lon0);
            if (lon < w) w = lon;
            if (lon > e) e = lon;
        }
        if (poleInView || e - w > 180)
        {
            w = -180; e = 180;
            if (poleInView) { if (n > 0) n = 90; else s = -90; }
        }
        return n > s && e > w;
    }

    // Is a pole between the view points? The pole in view lies within the
    // farthest view point's distance of the centre (points[0]).
    internal static bool PoleInView(IList<double[]> points)
    {
        if (points == null || points.Count < 2) return false;
        double reach = 0;
        foreach (var p in points) reach = Math.Max(reach, StormMapGeometry.DistanceNm(points[0][0], points[0][1], p[0], p[1]));
        double toNorth = (90 - points[0][0]) * 60.0, toSouth = (points[0][0] + 90) * 60.0;
        return toNorth <= reach || toSouth <= reach;
    }

    // The point at fraction t along a cell side where the value crosses t.
    private static double Cross(double a, double b, double threshold)
    {
        double d = b - a;
        if (Math.Abs(d) < 1e-12) return 0.5;
        double f = (threshold - a) / d;
        return f < 0 ? 0 : f > 1 ? 1 : f;
    }

    // Side ids: south side of cell (r, c) = horizontal edge (r, c); west side
    // = vertical edge (r, c). Unique per grid.
    private static long HKey(IceMapGrid g, int r, int c) => ((long)r * (g.Cols + 1) + c) * 2;
    private static long VKey(IceMapGrid g, int r, int c) => ((long)r * (g.Cols + 1) + c) * 2 + 1;

    private static double[] HPoint(IceMapGrid g, int r, int c, double t) =>
        new[] { g.LatOf(r), g.LonOf(c) + Cross(g.At(r, c), g.At(r, c + 1), t) * g.CellLon };
    private static double[] VPoint(IceMapGrid g, int r, int c, double t) =>
        new[] { g.LatOf(r) + Cross(g.At(r, c), g.At(r + 1, c), t) * g.CellLat, g.LonOf(c) };

    // The threshold line (marching squares) as polylines of (lat, lon), cells
    // on land left out (the line stops at the coast; the map draws the coast).
    // A saddle cell joins its two ice corners when the cell's mean is ice, as
    // the fill polygon does (FillCell), so line and fill always agree.
    internal static List<List<double[]>> Contour(IceMapGrid g, double t)
    {
        var segs = new List<long[]>();
        var points = new Dictionary<long, double[]>();
        for (int r = 0; r < g.Rows; r++)
            for (int c = 0; c < g.Cols; c++)
            {
                if (g.IsLand(r, c)) continue;
                bool sw = g.At(r, c) >= t, se = g.At(r, c + 1) >= t, ne = g.At(r + 1, c + 1) >= t, nw = g.At(r + 1, c) >= t;
                int code = (sw ? 1 : 0) | (se ? 2 : 0) | (ne ? 4 : 0) | (nw ? 8 : 0);
                if (code == 0 || code == 15) continue;
                long S = HKey(g, r, c), N = HKey(g, r + 1, c), W = VKey(g, r, c), E = VKey(g, r, c + 1);
                int rr = r, cc = c;
                void Pt(long k)
                {
                    if (points.ContainsKey(k)) return;
                    points[k] = k == S ? HPoint(g, rr, cc, t) : k == N ? HPoint(g, rr + 1, cc, t) : k == W ? VPoint(g, rr, cc, t) : VPoint(g, rr, cc + 1, t);
                }
                void Add(long a, long b) { segs.Add(new[] { a, b }); Pt(a); Pt(b); }
                switch (code)
                {
                    case 1: case 14: Add(S, W); break;
                    case 2: case 13: Add(S, E); break;
                    case 4: case 11: Add(E, N); break;
                    case 8: case 7: Add(N, W); break;
                    case 3: case 12: Add(W, E); break;
                    case 6: case 9: Add(S, N); break;
                    case 5: case 10:
                        bool joined = g.CellMean(r, c) >= t;
                        // 5 = sw + ne ice; 10 = se + nw ice
                        if ((code == 5) == joined) { Add(S, E); Add(N, W); } else { Add(S, W); Add(E, N); }
                        break;
                }
            }
        // Chain the segments end to end (each side id is shared by at most two).
        var bySide = new Dictionary<long, List<int>>();
        for (int i = 0; i < segs.Count; i++)
            foreach (long k in segs[i])
            {
                if (!bySide.TryGetValue(k, out var l)) bySide[k] = l = new List<int>(2);
                l.Add(i);
            }
        var used = new bool[segs.Count];
        var lines = new List<List<double[]>>();
        for (int i = 0; i < segs.Count; i++)
        {
            if (used[i]) continue;
            used[i] = true;
            var chain = new LinkedList<long>(segs[i]);
            for (int end = 0; end < 2; end++)
            {
                while (true)
                {
                    long tip = end == 0 ? chain.Last.Value : chain.First.Value;
                    int next = -1;
                    foreach (int j in bySide[tip]) if (!used[j]) { next = j; break; }
                    if (next < 0) break;
                    used[next] = true;
                    long other = segs[next][0] == tip ? segs[next][1] : segs[next][0];
                    if (end == 0) chain.AddLast(other); else chain.AddFirst(other);
                }
            }
            var line = new List<double[]>(chain.Count);
            foreach (long k in chain) line.Add(points[k]);
            lines.Add(line);
        }
        return lines;
    }

    // The fill, one list of closed rings (lat, lon) per band: whole cells merged
    // into runs along each row (the long sides cut every <= 1 degree of
    // longitude so they follow the globe), and the cells the edge line crosses
    // clipped to the ice side of it (the lowest band), so the fill ends exactly
    // on the edge line. Cells on land are left out.
    internal static List<List<double[]>>[] Fill(IceMapGrid g, double edge)
    {
        var bands = new List<List<double[]>>[IceMapStyle.BandFloors.Length];
        for (int i = 0; i < bands.Length; i++) bands[i] = new List<List<double[]>>();
        int ice = 0;
        for (int r = 0; r < g.Rows; r++)
        {
            int runBand = -1, runStart = 0;
            for (int c = 0; c <= g.Cols; c++)
            {
                int band = -1;
                bool clipped = false;
                if (c < g.Cols && !g.IsLand(r, c))
                {
                    bool all = g.At(r, c) >= edge && g.At(r, c + 1) >= edge && g.At(r + 1, c) >= edge && g.At(r + 1, c + 1) >= edge;
                    bool any = g.At(r, c) >= edge || g.At(r, c + 1) >= edge || g.At(r + 1, c) >= edge || g.At(r + 1, c + 1) >= edge;
                    if (all) band = IceMapStyle.Band(g.CellMean(r, c), edge);
                    else if (any) clipped = true;
                }
                if (band != runBand)
                {
                    if (runBand >= 0) bands[runBand].Add(Run(g, r, runStart, c));
                    runBand = band; runStart = c;
                }
                if (clipped)
                {
                    var poly = FillCell(g, r, c, edge);
                    if (poly.Count >= 3) { bands[0].Add(poly); ice++; }
                }
                if (band >= 0) ice++;
            }
        }
        g.IceCells = ice;
        return bands;
    }

    // Cells c0..c1-1 of row r as one ring.
    internal static List<double[]> Run(IceMapGrid g, int r, int c0, int c1)
    {
        double s = g.LatOf(r), n = g.LatOf(r + 1), w = g.LonOf(c0), e = g.LonOf(c1);
        int steps = Math.Max(1, (int)Math.Ceiling((e - w) / 1.0));
        var ring = new List<double[]>(2 * steps + 3);
        for (int i = 0; i <= steps; i++) ring.Add(new[] { s, w + (e - w) * i / steps });
        for (int i = steps; i >= 0; i--) ring.Add(new[] { n, w + (e - w) * i / steps });
        ring.Add(ring[0]);
        return ring;
    }

    // The ice side of a cell the edge crosses: the corners SW, SE, NE, NW in
    // turn, each kept when at or over the edge, and a point on each side where
    // the value crosses it (Sutherland-Hodgman on the corner values). A saddle
    // cell gives one polygon through the cell: the joined case of Contour.
    internal static List<double[]> FillCell(IceMapGrid g, int r, int c, double edge)
    {
        int[][] corners = { new[] { r, c }, new[] { r, c + 1 }, new[] { r + 1, c + 1 }, new[] { r + 1, c } };
        var poly = new List<double[]>(8);
        for (int i = 0; i < 4; i++)
        {
            var a = corners[i]; var b = corners[(i + 1) % 4];
            double va = g.At(a[0], a[1]), vb = g.At(b[0], b[1]);
            bool ia = va >= edge, ib = vb >= edge;
            if (ia) poly.Add(new[] { g.LatOf(a[0]), g.LonOf(a[1]) });
            if (ia != ib)
            {
                double f = Cross(va, vb, edge);
                poly.Add(new[] { g.LatOf(a[0]) + (g.LatOf(b[0]) - g.LatOf(a[0])) * f, g.LonOf(a[1]) + (g.LonOf(b[1]) - g.LonOf(a[1])) * f });
            }
        }
        if (poly.Count >= 3) poly.Add(poly[0]);
        return poly;
    }

    // A fill ring in Path mini-language, only when every point projects and
    // no step jumps (a ring cut by the globe's limb or a wrap would fill a
    // wrong wedge, so it is left out). True when appended.
    internal static bool AppendRing(StringBuilder data, IList<double[]> ring, StormMapGeometry.Project project, double maxJump)
    {
        if (ring == null || ring.Count < 4) return false;
        var xs = new double[ring.Count]; var ys = new double[ring.Count];
        for (int i = 0; i < ring.Count; i++)
        {
            if (!project(ring[i][0], ring[i][1], out xs[i], out ys[i]) || double.IsNaN(xs[i]) || double.IsNaN(ys[i])) return false;
            if (i > 0 && (Math.Abs(xs[i] - xs[i - 1]) > maxJump || Math.Abs(ys[i] - ys[i - 1]) > maxJump)) return false;
        }
        for (int i = 0; i < ring.Count - 1; i++)
        {
            data.Append(i == 0 ? (data.Length > 0 ? " M " : "M ") : " L ");
            data.Append(xs[i].ToString("0.#", CultureInfo.InvariantCulture)).Append(',').Append(ys[i].ToString("0.#", CultureInfo.InvariantCulture));
        }
        data.Append(" Z");
        return true;
    }

    // Is the grid cell under a point land (the mask)? False without a mask.
    internal static bool LandAt(IceMapGrid g, double lat, double lon)
    {
        if (g?.Land == null) return false;
        double x = SeaIceModel.PyMod(lon - g.West, 360.0) / g.CellLon, y = (lat - g.South) / g.CellLat;
        if (x < 0 || y < 0 || x >= g.Cols || y >= g.Rows) return false;
        return g.IsLand((int)y, (int)x);
    }

    // The concentration at a point from the grid (bilinear between nodes), NaN
    // outside it: the readout uses the same values the map draws.
    internal static double Sample(IceMapGrid g, double lat, double lon)
    {
        if (g == null) return double.NaN;
        double x = SeaIceModel.PyMod(lon - g.West, 360.0) / g.CellLon, y = (lat - g.South) / g.CellLat;
        if (x < 0 || y < 0 || x > g.Cols || y > g.Rows) return double.NaN;
        int c = Math.Min(g.Cols - 1, (int)x), r = Math.Min(g.Rows - 1, (int)y);
        double fx = x - c, fy = y - r;
        double s = g.At(r, c) * (1 - fx) + g.At(r, c + 1) * fx, n = g.At(r + 1, c) * (1 - fx) + g.At(r + 1, c + 1) * fx;
        return s * (1 - fy) + n * fy;
    }
}
