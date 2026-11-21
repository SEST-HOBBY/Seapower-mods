using System;
using System.Collections.Generic;

namespace Sest.RuntimeFixes;

// The pure rules of SEST's battle sea ice (SeaIce=1 in [Runtime]): ice
// access and speed (a port of the weather branch's mno_env/ice.py), the
// ship speed-cap state machine, the submarine hold under ice, the
// position-keyed concentration cache, the deterministic lead/floe field,
// and the ice-sheet mesher. No Unity or game types: SeaIceTests.exe runs
// all of it under Mono, and the sheet mesher runs on a worker thread.

internal enum IceAccess { Open = 0, Caution = 1, Restricted = 2, Blocked = 3 }

internal static class IceRules
{
    // ice.py ACCESS_THRESHOLDS: capability -> (open below, caution below,
    // restricted below); at or above the last: blocked. DESIGN values for
    // game rules, not the IMO Polar Code / POLARIS method.
    internal static readonly string[] Capabilities = { "none", "ice_strengthened", "polar_class", "icebreaker" };
    private static readonly double[][] Thresholds =
    {
        new[] { 10.0, 30.0, 60.0 },
        new[] { 30.0, 60.0, 80.0 },
        new[] { 60.0, 90.0, 101.0 },
        new[] { 90.0, 101.0, 101.0 },
    };
    // ice.py ACCESS_SPEED
    internal static readonly double[] SpeedFactor = { 1.0, 0.7, 0.4, 0.0 };

    internal static int CapabilityIndex(string capability)
    {
        int i = Array.IndexOf(Capabilities, capability ?? "");
        if (i < 0) throw new ArgumentException("unknown ice capability " + capability);
        return i;
    }

    internal static double Threshold(int capability, int level) => Thresholds[capability][level];

    // ice.py access(); NaN (unknown ice) is "caution", as ice.py:44.
    internal static IceAccess Access(double percent, int capability)
    {
        if (double.IsNaN(percent)) return IceAccess.Caution;
        var t = Thresholds[capability];
        if (percent < t[0]) return IceAccess.Open;
        if (percent < t[1]) return IceAccess.Caution;
        if (percent < t[2]) return IceAccess.Restricted;
        return IceAccess.Blocked;
    }

    // ice-capability.json "units" (SeaIceData.Units: ini name, capability,
    // source). Empty today on purpose, so every ship is "none". A class is
    // never inferred from a name.
    private static Dictionary<string, int> units;
    internal static int CapabilityOf(string unitIni)
    {
        var map = units;
        if (map == null)
        {
            map = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
            for (int i = 0; i + 2 < SeaIceData.Units.Length; i += 3)
                if (!string.IsNullOrWhiteSpace(SeaIceData.Units[i + 2])) map[SeaIceData.Units[i]] = CapabilityIndex(SeaIceData.Units[i + 1]);
            units = map;
        }
        return unitIni != null && map.TryGetValue(unitIni, out int c) ? c : 0;
    }
}

// Speed cap for one hull. State machine over the ice.py access levels with
// 1 percentage point of hysteresis, so a ship sitting on a threshold does not
// flicker between two speeds. A hull that the rules would stop dead
// (blocked, factor 0) is never trapped:
// - astern is always allowed at "restricted" speed (EscapeFactor, 0.4 of
//   flank), whatever the ice astern;
// - ahead is allowed at 0.4 when the ice in the direction of travel is equal
//   or lighter than here (within EscapeEpsilon); the caller samples it from
//   the unquantised model several tile lengths away (AheadNm), never from the
//   0.05-degree tile cache, so two points in one tile cannot lock the hull;
// - ahead into heavier ice the hull keeps steerage way (MinWayFactor, 0.1 of
//   flank), so its rudder still turns it toward open water.
internal sealed class IceSpeedState
{
    internal const double Hysteresis = 1.0;
    internal const double EscapeFactor = 0.4;
    internal const double MinWayFactor = 0.1;
    internal const double EscapeEpsilon = 0.05; // percentage points: "equal" ice counts as escapable
    // Direction-of-travel samples, nautical miles (GeoOffsetByDistanceOnHeading's unit), taken
    // from the unquantised model; the farthest reach two 0.05-degree tiles (3 nm north-south)
    // beyond the hull. The lightest counts.
    internal static readonly float[] AheadNm = { 1f, 3f, 6f };
    internal IceAccess State = IceAccess.Open;
    internal double LastFactor = 1.0;
    internal bool Escaping, SteerageOnly;

    internal IceAccess Update(double percent, int capability)
    {
        if (double.IsNaN(percent)) { State = IceAccess.Caution; return State; }
        var raw = IceRules.Access(percent, capability);
        if (raw > State)
        {
            State = raw; // into heavier ice: immediately
        }
        else if (raw < State)
        {
            // out of it: only once the concentration is a margin below the threshold that set this state
            var lighter = IceRules.Access(percent + Hysteresis, capability);
            if (lighter < State) State = lighter;
        }
        return State;
    }

    // The lightest of the direction-of-travel samples; NaN when there are none.
    internal static double Lightest(IEnumerable<double> samples)
    {
        double best = double.NaN;
        foreach (var v in samples) if (!double.IsNaN(v) && (double.IsNaN(best) || v < best)) best = v;
        return best;
    }

    // wanted: the knots the native telegraph/speed command produced (negative astern).
    // flank: the hull's top telegraph speed in the current state (surface or submerged).
    // here: the concentration that sets the state (tile cache). inDirectionOfTravel: the lightest
    // unquantised sample ahead (astern when backing). reference: the unquantised concentration at
    // the hull, compared with inDirectionOfTravel (NaN: here is used).
    internal float Cap(float wanted, float flank, double here, double inDirectionOfTravel, int capability, double reference = double.NaN)
    {
        var state = Update(here, capability);
        double factor = IceRules.SpeedFactor[(int)state];
        Escaping = false;
        SteerageOnly = false;
        if (factor < EscapeFactor)
        {
            double at = double.IsNaN(reference) ? here : reference;
            bool lighter = !double.IsNaN(inDirectionOfTravel) && !double.IsNaN(at) && inDirectionOfTravel <= at + EscapeEpsilon;
            if (wanted < 0 || lighter) { factor = EscapeFactor; Escaping = true; }
            else if (factor < MinWayFactor) { factor = MinWayFactor; SteerageOnly = true; }
        }
        LastFactor = factor;
        if (!(flank > 0) || float.IsNaN(wanted)) return wanted;
        float cap = (float)(factor * flank);
        if (Math.Abs(wanted) <= cap) return wanted;
        return wanted < 0 ? -cap : cap;
    }
}

// The submarine rule. Heavy ice: concentration at or above HeavyPercent
// (60 %, ice.py's "blocked" for class none, the design's heavy pack). Under
// heavy ice a submarine may not come shallower than the keel clearance (30 m,
// a design constant for pressure-ridge keels, not data), may not raise a mast
// or snorkel, and may not blow to the surface, unless its whole footprint is
// open water in the lead field (SeaIceField), the same field the sheet draws.
internal static class SubIceRule
{
    internal const double DefaultHeavyPercent = 60.0;
    internal const double DefaultKeelMeters = 30.0;
    internal const double FootprintMeters = 45.0; // half a typical hull length, checked fore, aft and abeam

    internal static bool Holds(double percent, bool footprintOpen, double heavyPercent) =>
        !double.IsNaN(percent) && percent >= heavyPercent && !footprintOpen;

    // Native depth units: Unity units, 1 unit = 220.472656 ft (the game's own
    // constant, RelNMFromGeoPos IL_0087 and getLayerHeight IL_002e).
    internal const double FeetPerUnity = 220.472656;
    internal static float MetersToUnity(double meters) => (float)(meters / 0.3048 / FeetPerUnity);

    // DesiredAltitude is negative below the surface. Returns the clamped order.
    internal static float ClampDesiredAltitude(float desired, float keelUnity) => desired > -keelUnity ? -keelUnity : desired;

    // setDepth(depth): depth is positive Unity units below the surface.
    internal static float ClampOrderedDepth(float depth, float keelUnity) => depth < keelUnity ? keelUnity : depth;

    // Submarine.DepthKeeping's own _targetAltitude (negative below the surface) while held: it
    // raises the target above the clamped order for bottom clearance in shallow water and sets it
    // to 0 (surface) when that is shallower than periscope depth. Held, the target may be deeper
    // than the keel clearance as DepthKeeping wants; never shallower than the keel, and when the
    // terrain forbids the keel depth the boat holds its current depth instead of rising.
    internal static float ClampTargetAltitude(float target, float keelUnity, float currentY) =>
        target <= -keelUnity ? target : Math.Min(target, Math.Max(currentY, -keelUnity));

    // The highest y a held boat may reach (applyDepth backstop, also against pitch and manual
    // ballast): it only ratchets down while held, never below the keel clearance. NaN: not set.
    internal static float Ceiling(float previous, float y, float keelUnity) =>
        Math.Max(-keelUnity, float.IsNaN(previous) ? y : Math.Min(previous, y));

    // The order a held boat was given before the clamp (DesiredAltitude, negative below the
    // surface), kept so it is given back on release. From setDepth(depth):
    internal static void RememberOrderedDepth(float depth, float keelUnity, ref bool has, ref float order)
    {
        if (depth < keelUnity) { has = true; order = Math.Min(0f, -depth); }
        else has = false; // a legal order replaces the remembered one
    }

    // From a DesiredAltitude written some other way (seen by the fixed-step prefix before its clamp):
    internal static void RememberDesired(float desired, float keelUnity, ref bool has, ref float order)
    {
        const float eps = 1e-4f;
        if (desired > -keelUnity + eps) { has = true; order = Math.Min(0f, desired); }
        else if (desired < -keelUnity - eps) has = false;
    }

    // On release: give the remembered order back, unless the boat was given a new order meanwhile
    // (DesiredAltitude no longer the clamp value).
    internal static bool RestoreOnRelease(float desired, float keelUnity, bool has, float order, out float restored)
    {
        restored = desired;
        if (!has || Math.Abs(desired + keelUnity) > 1e-4f) return false;
        restored = order;
        return true;
    }

    // SubmarineStates.Snorkelling latches _depthReached after one snorkel attempt and never tries
    // again. Held, the state is kept from trying at all (depthReached reads true, so no refused
    // raise, no latch); on release it is cleared once, so the state tries again at the depth it
    // ordered in open water.
    internal static bool SnorkelDepthReached(bool held, bool depthReached, ref bool suppressed)
    {
        if (held) { suppressed = true; return true; }
        if (suppressed) { suppressed = false; return false; }
        return depthReached;
    }
}

// Concentration by position, cached per 0.05-degree tile and calendar date.
// getFloeIce(GeoPosition) has no unit (its caller getOceanNoise runs for the
// selected object every frame, for UI windows and for torpedo seekers at the
// weapon's own position), so the key is the position, never an instance id.
internal sealed class SeaIceTileCache
{
    internal const double TileDegrees = 0.05;
    internal const int Capacity = 8192;
    private readonly Dictionary<long, double> tiles = new Dictionary<long, double>();
    private readonly object gate = new object();
    private int dateKey = int.MinValue;
    internal int Hits, Misses, Clears;

    internal static long Key(double lat, double lon)
    {
        long y = (long)Math.Floor((lat + 90.0) / TileDegrees);
        long x = (long)Math.Floor((SeaIceModel.WrapLon(lon) + 180.0) / TileDegrees);
        return y * 100000L + x;
    }

    internal static void TileCentre(long key, out double lat, out double lon)
    {
        long y = key / 100000L, x = key % 100000L;
        lat = (y + 0.5) * TileDegrees - 90.0;
        lon = (x + 0.5) * TileDegrees - 180.0;
    }

    internal static int DateKeyOf(DateTime d) => d.Year * 10000 + d.Month * 100 + d.Day;

    internal double Percent(double lat, double lon, DateTime date)
    {
        if (double.IsNaN(lat) || double.IsNaN(lon) || double.IsInfinity(lat) || double.IsInfinity(lon)) return 0.0;
        if (Math.Abs(lat) < 39.9) return 0.0;
        long key = Key(lat, lon);
        int dk = DateKeyOf(date);
        lock (gate)
        {
            if (dk != dateKey || tiles.Count >= Capacity) { tiles.Clear(); dateKey = dk; Clears++; }
            if (tiles.TryGetValue(key, out double v)) { Hits++; return v; }
        }
        TileCentre(key, out double clat, out double clon);
        double c = SeaIceModel.Concentration(clat, clon, date);
        lock (gate)
        {
            if (dk == dateKey) tiles[key] = c;
            Misses++;
        }
        return c;
    }

    internal int Count { get { lock (gate) return tiles.Count; } }
}

// A local metric frame around a battle origin (equirect about the origin's
// latitude): east/north kilometres <-> degrees. The lead field and the sheet
// chunks are anchored in it, so they do not move when the game recentres its
// floating Unity origin (Globals._currentCenterTile).
internal readonly struct IceFrame
{
    internal const double KmPerDegree = 111.32;
    internal readonly double Lat0, Lon0, CosLat0;
    internal IceFrame(double lat0, double lon0)
    {
        Lat0 = lat0; Lon0 = lon0;
        CosLat0 = Math.Max(0.05, Math.Cos(lat0 * Math.PI / 180));
    }
    internal void ToKm(double lat, double lon, out double east, out double north)
    {
        north = (lat - Lat0) * KmPerDegree;
        east = SeaIceModel.LonDelta(lon, Lon0) * KmPerDegree * CosLat0;
    }
    internal void ToGeo(double east, double north, out double lat, out double lon)
    {
        lat = Lat0 + north / KmPerDegree;
        lon = SeaIceModel.WrapLon(Lon0 + east / (KmPerDegree * CosLat0));
    }
    // The origin of a battle: the first position asked about, rounded to a whole degree.
    internal static IceFrame Around(double lat, double lon) => new IceFrame(Math.Round(lat), Math.Round(SeaIceModel.WrapLon(lon)));
}

// The deterministic floe/lead field: two octaves of value noise (leads about
// 550 m, floes about 160 m), thresholded at the quantile of the local
// concentration, so the ice-covered share of any area is the concentration.
// Seeded by the battle date: the same tile on the same date always has the
// same leads, and the sheet, the submarine rule and the floe fallback read
// this one field.
internal static class SeaIceField
{
    internal const double LeadKm = 0.55, FloeKm = 0.16;
    private static readonly double[] quantiles = BuildQuantiles();

    internal static uint SeedOf(int dateKey) => unchecked((uint)dateKey * 2654435761u ^ 0x5EA1CEu);

    private static double Hash(int ix, int iy, uint seed)
    {
        unchecked
        {
            uint h = (uint)ix * 0x8da6b343u ^ (uint)iy * 0xd8163841u ^ seed * 0xcb1ab31fu;
            h ^= h >> 13; h *= 0x85ebca6bu; h ^= h >> 16; h *= 0xc2b2ae35u; h ^= h >> 16;
            return (h & 0xFFFFFF) / 16777216.0;
        }
    }

    private static double Value(double x, double y, uint seed)
    {
        double fx = Math.Floor(x), fy = Math.Floor(y);
        int ix = (int)fx, iy = (int)fy;
        double tx = x - fx, ty = y - fy;
        tx = tx * tx * (3 - 2 * tx); ty = ty * ty * (3 - 2 * ty);
        double a = Hash(ix, iy, seed), b = Hash(ix + 1, iy, seed), c = Hash(ix, iy + 1, seed), d = Hash(ix + 1, iy + 1, seed);
        return (a + (b - a) * tx) + ((c + (d - c) * tx) - (a + (b - a) * tx)) * ty;
    }

    // 0..1 at east/north kilometres.
    internal static double Noise(double eastKm, double northKm, uint seed) =>
        0.62 * Value(eastKm / LeadKm, northKm / LeadKm, seed) + 0.38 * Value(eastKm / FloeKm + 17.3, northKm / FloeKm - 9.1, seed ^ 0x9E3779B9u);

    private static double[] BuildQuantiles()
    {
        const int n = 65536;
        var s = new double[n];
        uint seed = SeedOf(20290310);
        for (int k = 0; k < n; k++)
        {
            int i = k & 255, j = k >> 8;
            s[k] = Noise(i * 0.0731 + j * 0.0113, j * 0.0697 + i * 0.0071, seed);
        }
        Array.Sort(s);
        var q = new double[257];
        for (int k = 0; k <= 256; k++) q[k] = s[Math.Min(n - 1, (int)((long)k * (n - 1) / 256))];
        q[0] = -1e-9; q[256] = 1.0 + 1e-9;
        return q;
    }

    // The noise level below which a point is ice for an ice fraction p (0..1).
    internal static double Quantile(double p)
    {
        if (!(p > 0)) return -1.0;
        if (p >= 1) return 2.0;
        double f = p * 256, k = Math.Floor(f);
        int i = (int)k;
        return quantiles[i] + (quantiles[i + 1] - quantiles[i]) * (f - k);
    }

    // > 0 inside ice, < 0 in open water: the scalar the mesher contours.
    internal static double Inside(double eastKm, double northKm, double fraction, uint seed) => Quantile(fraction) - Noise(eastKm, northKm, seed);

    internal static bool IsIce(double eastKm, double northKm, double fraction, uint seed) => Inside(eastKm, northKm, fraction, seed) > 0;

    // Open water at the centre and FootprintMeters fore, aft and abeam.
    internal static bool FootprintOpen(double eastKm, double northKm, double fraction, uint seed, double footprintMeters)
    {
        double r = footprintMeters / 1000.0;
        return !IsIce(eastKm, northKm, fraction, seed) && !IsIce(eastKm + r, northKm, fraction, seed) && !IsIce(eastKm - r, northKm, fraction, seed)
            && !IsIce(eastKm, northKm + r, fraction, seed) && !IsIce(eastKm, northKm - r, fraction, seed);
    }

    // The sheet draws ice only where the modelled concentration reaches the
    // edge threshold (15 %, NSIDC's extent line), so its outer edge is the
    // modelled ice edge; inside it the ice share is the concentration.
    internal static double DrawnFraction(double percent, double edgePercent) => percent >= edgePercent ? Math.Min(1.0, percent / 100.0) : 0.0;

    // Pressure-ridge relief 0..1: sharp ridged noise, elongated.
    internal static double Ridge(double eastKm, double northKm, uint seed)
    {
        double v = Value(eastKm / 0.05 + northKm / 0.21, northKm / 0.05 - eastKm / 0.33, seed ^ 0x1234567u);
        double r = 1 - Math.Abs(2 * v - 1);
        return r * r * r * r;
    }
}

// Floe fallback placement (when the sheet cannot be built): one candidate
// floe per FloeCell on a world-anchored grid in the battle frame, kept when
// its hash is below the drawn fraction, so density follows concentration and
// floes never pop while the camera pans.
internal struct FloeSlot
{
    internal double East, North, SizeM, YawDeg;
    internal long Id;
}

internal static class FloePlacement
{
    internal static List<FloeSlot> Slots(double camEastKm, double camNorthKm, double radiusKm, double cellKm, Func<double, double, double> fractionAt, uint seed, int cap)
    {
        var list = new List<FloeSlot>();
        int i0 = (int)Math.Floor((camEastKm - radiusKm) / cellKm), i1 = (int)Math.Floor((camEastKm + radiusKm) / cellKm);
        int j0 = (int)Math.Floor((camNorthKm - radiusKm) / cellKm), j1 = (int)Math.Floor((camNorthKm + radiusKm) / cellKm);
        double r2 = radiusKm * radiusKm;
        for (int j = j0; j <= j1; j++)
            for (int i = i0; i <= i1; i++)
            {
                uint h = Mix(i, j, seed);
                double e = (i + 0.15 + 0.7 * U(h, 1)) * cellKm, n = (j + 0.15 + 0.7 * U(h, 2)) * cellKm;
                double de = e - camEastKm, dn = n - camNorthKm;
                if (de * de + dn * dn > r2) continue;
                double p = fractionAt(e, n);
                if (!(U(h, 3) < p)) continue;
                list.Add(new FloeSlot { East = e, North = n, SizeM = cellKm * 1000 * (0.35 + 0.5 * U(h, 4)), YawDeg = 360 * U(h, 5), Id = ((long)i << 32) ^ (uint)j });
            }
        list.Sort((a, b) => Dist(a, camEastKm, camNorthKm).CompareTo(Dist(b, camEastKm, camNorthKm)));
        if (list.Count > cap) list.RemoveRange(cap, list.Count - cap);
        return list;
    }
    private static double Dist(FloeSlot s, double e, double n) => (s.East - e) * (s.East - e) + (s.North - n) * (s.North - n);
    private static uint Mix(int i, int j, uint seed)
    {
        unchecked
        {
            uint h = (uint)i * 0x27d4eb2du ^ (uint)j * 0x165667b1u ^ seed;
            h ^= h >> 15; h *= 0x85ebca6bu; h ^= h >> 13; return h;
        }
    }
    private static double U(uint h, int k)
    {
        unchecked
        {
            uint x = h ^ (uint)k * 0x9E3779B9u;
            x ^= x >> 16; x *= 0x7feb352du; x ^= x >> 15; x *= 0x846ca68bu; x ^= x >> 16;
            return (x & 0xFFFFFF) / 16777216.0;
        }
    }
}

// One chunk of the ice sheet as plain arrays (metres, x east, y up, z north,
// relative to the chunk centre), built by marching squares over
// SeaIceField.Inside on a (Cells+1)^2 grid. Top faces at the freeboard plus
// ridge relief, and for near chunks an underside at -draft and vertical
// edge walls, so the ice reads as a slab from a periscope or an underwater
// camera. Unity's front faces are clockwise as seen by the viewer.
internal sealed class IceChunkMesh
{
    internal float[] Vertices = new float[0]; // xyz triples
    internal int[] Triangles = new int[0];
    internal int IceCells, OpenCells;
    internal double MeanFraction;
    internal int TriangleCount => Triangles.Length / 3;
}

internal struct IceChunkSpec
{
    internal double CentreEastKm, CentreNorthKm, SizeKm;
    internal int Cells;
    internal bool Underside;      // underside and edge walls (near chunks)
    internal double FreeboardM, DraftM, RidgeM, EdgePercent;
    internal uint Seed;
}

internal static class IceMesher
{
    // percentAt(eastKm, northKm): concentration percent. Sampled on a 5 x 5 lattice per chunk and
    // interpolated, so a chunk costs 25 model evaluations however fine its grid.
    internal static IceChunkMesh Build(IceChunkSpec s, Func<double, double, double> percentAt)
    {
        int n = Math.Max(2, s.Cells);
        double h = s.SizeKm / n, e0 = s.CentreEastKm - s.SizeKm / 2, n0 = s.CentreNorthKm - s.SizeKm / 2;
        var lattice = new double[25];
        for (int j = 0; j < 5; j++)
            for (int i = 0; i < 5; i++)
                lattice[j * 5 + i] = percentAt(e0 + s.SizeKm * i / 4, n0 + s.SizeKm * j / 4);
        var f = new double[(n + 1) * (n + 1)];
        double sum = 0;
        for (int j = 0; j <= n; j++)
            for (int i = 0; i <= n; i++)
            {
                double u = 4.0 * i / n, v = 4.0 * j / n;
                int a = Math.Min(3, (int)u), b = Math.Min(3, (int)v);
                double tu = u - a, tv = v - b;
                double p = (lattice[b * 5 + a] * (1 - tu) + lattice[b * 5 + a + 1] * tu) * (1 - tv) + (lattice[(b + 1) * 5 + a] * (1 - tu) + lattice[(b + 1) * 5 + a + 1] * tu) * tv;
                double fr = SeaIceField.DrawnFraction(p, s.EdgePercent);
                sum += fr;
                f[j * (n + 1) + i] = fr <= 0 ? -1.0 : SeaIceField.Inside(e0 + i * h, n0 + j * h, fr, s.Seed);
            }
        var mesh = new IceChunkMesh { MeanFraction = sum / f.Length };
        var verts = new List<float>(4096);
        var tris = new List<int>(4096);
        var poly = new double[8 * 3];
        var cross = new bool[8];
        for (int j = 0; j < n; j++)
            for (int i = 0; i < n; i++)
            {
                double f0 = f[j * (n + 1) + i], f1 = f[j * (n + 1) + i + 1], f2 = f[(j + 1) * (n + 1) + i + 1], f3 = f[(j + 1) * (n + 1) + i];
                if (f0 <= 0 && f1 <= 0 && f2 <= 0 && f3 <= 0) { mesh.OpenCells++; continue; }
                mesh.IceCells++;
                // walk the cell's corners counter-clockwise seen from above (east right, north up)
                double[] cx = { i, i + 1, i + 1, i }, cy = { j, j, j + 1, j + 1 }, cf = { f0, f1, f2, f3 };
                int count = 0;
                for (int k = 0; k < 4; k++)
                {
                    int m = (k + 1) & 3;
                    if (cf[k] > 0) { poly[count * 3] = cx[k]; poly[count * 3 + 1] = cy[k]; poly[count * 3 + 2] = 1; cross[count] = false; count++; }
                    if ((cf[k] > 0) != (cf[m] > 0))
                    {
                        double t = cf[k] / (cf[k] - cf[m]);
                        poly[count * 3] = cx[k] + (cx[m] - cx[k]) * t; poly[count * 3 + 1] = cy[k] + (cy[m] - cy[k]) * t; poly[count * 3 + 2] = 0; cross[count] = true; count++;
                    }
                }
                if (count < 3) continue;
                int baseTop = verts.Count / 3;
                for (int k = 0; k < count; k++)
                {
                    double ek = e0 + poly[k * 3] * h, nk = n0 + poly[k * 3 + 1] * h;
                    double y = s.FreeboardM + (poly[k * 3 + 2] > 0 ? s.RidgeM * SeaIceField.Ridge(ek, nk, s.Seed) : 0);
                    Add(verts, (ek - s.CentreEastKm) * 1000, y, (nk - s.CentreNorthKm) * 1000);
                }
                for (int k = 1; k + 1 < count; k++) { tris.Add(baseTop); tris.Add(baseTop + k + 1); tris.Add(baseTop + k); }
                if (!s.Underside) continue;
                int baseBottom = verts.Count / 3;
                for (int k = 0; k < count; k++)
                    Add(verts, (e0 + poly[k * 3] * h - s.CentreEastKm) * 1000, -s.DraftM, (n0 + poly[k * 3 + 1] * h - s.CentreNorthKm) * 1000);
                for (int k = 1; k + 1 < count; k++) { tris.Add(baseBottom); tris.Add(baseBottom + k); tris.Add(baseBottom + k + 1); }
                // edge walls along the contour: consecutive crossing points of the polygon, drawn from both sides
                for (int k = 0; k < count; k++)
                {
                    int m = (k + 1) % count;
                    if (!cross[k] || !cross[m]) continue;
                    int w = verts.Count / 3;
                    int ta = baseTop + k, tb = baseTop + m, ba = baseBottom + k, bb = baseBottom + m;
                    Copy(verts, ta); Copy(verts, tb); Copy(verts, bb); Copy(verts, ba);
                    tris.Add(w); tris.Add(w + 1); tris.Add(w + 2); tris.Add(w); tris.Add(w + 2); tris.Add(w + 3);
                    tris.Add(w); tris.Add(w + 2); tris.Add(w + 1); tris.Add(w); tris.Add(w + 3); tris.Add(w + 2);
                }
            }
        mesh.Vertices = verts.ToArray();
        mesh.Triangles = tris.ToArray();
        return mesh;
    }

    private static void Add(List<float> v, double x, double y, double z) { v.Add((float)x); v.Add((float)y); v.Add((float)z); }
    private static void Copy(List<float> v, int index) { v.Add(v[index * 3]); v.Add(v[index * 3 + 1]); v.Add(v[index * 3 + 2]); }

    // The chunk layout around a camera: three nested levels of square chunks
    // aligned to each other (level k+1 chunks are 4 x level k), each level
    // covering a square of whole chunks of the next level, minus the area the
    // finer level already covers, so no two chunks overlap.
    internal struct ChunkKey : IEquatable<ChunkKey>
    {
        internal int Level, I, J;
        public bool Equals(ChunkKey o) => Level == o.Level && I == o.I && J == o.J;
        public override bool Equals(object o) => o is ChunkKey k && Equals(k);
        public override int GetHashCode() => (Level * 73856093) ^ (I * 19349663) ^ (J * 83492791);
        public override string ToString() => "L" + Level + "(" + I + "," + J + ")";
    }

    // sizes[k]: chunk edge km of level k (sizes[k+1] = 4 sizes[k]); spans[k]: chunks of level k+1 per side
    // covered by level k (even); the last level covers outerChunks x outerChunks of its own chunks.
    internal static List<ChunkKey> Layout(double camEastKm, double camNorthKm, double[] sizes, int[] spans, int outerChunks)
    {
        var keys = new List<ChunkKey>();
        int levels = sizes.Length;
        // coverage square of each level, in its own chunk indices: [lo, hi)
        var lo = new int[levels, 2];
        var hi = new int[levels, 2];
        for (int k = 0; k < levels; k++)
        {
            int span; double unit;
            if (k + 1 < levels) { span = spans[k]; unit = sizes[k + 1]; } else { span = outerChunks; unit = sizes[k]; }
            int ci = (int)Math.Round(camEastKm / unit), cj = (int)Math.Round(camNorthKm / unit);
            int i0 = ci - span / 2, j0 = cj - span / 2;
            int ratio = (int)Math.Round(unit / sizes[k]);
            lo[k, 0] = i0 * ratio; lo[k, 1] = j0 * ratio; hi[k, 0] = (i0 + span) * ratio; hi[k, 1] = (j0 + span) * ratio;
        }
        for (int k = 0; k < levels; k++)
            for (int j = lo[k, 1]; j < hi[k, 1]; j++)
                for (int i = lo[k, 0]; i < hi[k, 0]; i++)
                {
                    if (k > 0)
                    {
                        // skip chunks the finer level covers (it is aligned to this level's chunks)
                        int r = (int)Math.Round(sizes[k] / sizes[k - 1]);
                        int fi = i * r, fj = j * r;
                        if (fi >= lo[k - 1, 0] && fi < hi[k - 1, 0] && fj >= lo[k - 1, 1] && fj < hi[k - 1, 1]) continue;
                    }
                    keys.Add(new ChunkKey { Level = k, I = i, J = j });
                }
        return keys;
    }

    // Squared distance from the camera to a chunk centre (km^2).
    internal static double Dist(ChunkKey k, double camEastKm, double camNorthKm, double[] sizes)
    {
        double s = sizes[k.Level], de = (k.I + 0.5) * s - camEastKm, dn = (k.J + 0.5) * s - camNorthKm;
        return de * de + dn * dn;
    }

    // The build order: nearest first (a camera jump refills around the camera before the horizon).
    internal static List<ChunkKey> NearestFirst(IEnumerable<ChunkKey> keys, double camEastKm, double camNorthKm, double[] sizes)
    {
        var list = new List<ChunkKey>(keys);
        list.Sort((a, b) => Dist(a, camEastKm, camNorthKm, sizes).CompareTo(Dist(b, camEastKm, camNorthKm, sizes)));
        return list;
    }

    // Do two chunks (any levels) share area?
    internal static bool Overlaps(ChunkKey a, ChunkKey b, double[] sizes)
    {
        double sa = sizes[a.Level], sb = sizes[b.Level];
        double ax0 = a.I * sa, ax1 = ax0 + sa, ay0 = a.J * sa, ay1 = ay0 + sa;
        double bx0 = b.I * sb, bx1 = bx0 + sb, by0 = b.J * sb, by1 = by0 + sb;
        const double eps = 1e-9;
        return ax0 < bx1 - eps && bx0 < ax1 - eps && ay0 < by1 - eps && by0 < ay1 - eps;
    }

    // Double buffering: a superseded chunk (camera moved, or the date changed) stays drawn until
    // every wanted chunk over its area is ready (uploaded or found empty); one the layout no longer
    // reaches at all goes at once.
    internal static bool CanRetire(ChunkKey stale, IList<ChunkKey> wanted, Func<ChunkKey, bool> ready, double[] sizes)
    {
        for (int i = 0; i < wanted.Count; i++)
            if (Overlaps(stale, wanted[i], sizes) && !ready(wanted[i])) return false;
        return true;
    }
}

// Where the sheet sits (metres relative to mean sea level, up positive). The slab is rigid per
// chunk: top at the freeboard (plus ridges), underside at -draft, both relative to the chunk origin.
// - It rides the sea surface the chunk sees (Ceto QueryWaves at the chunk, or sea level 0) plus a
//   lift of half the sea state's significant wave height, which hides wave crests through the ice,
//   capped (MaxLift) so the underside stays UnderwaterMarginM below that surface: a held
//   submarine always has ice overhead. SeaIceSheetLiftM overrides the lift, inside the same cap.
// - The underside is also kept below the lowest wave sample over the chunk.
// - Near a surface unit (a ship, or a submarine surfaced in a lead) the top never rises above the
//   unit's waterline, so ships are not buried in the slab.
internal static class IceSheetRule
{
    internal const double UnderwaterMarginM = 1.0;
    internal const double NearUnitKm = 0.3;
    internal const double StaleSinkM = 0.15; // a superseded chunk sits this much lower until its replacement is drawn
    internal const double UploadBudgetMs = 2.0, RefillBudgetMs = 3.0;

    internal static double MaxLift(double draftM) => Math.Max(0.0, draftM - UnderwaterMarginM);

    internal static double Lift(double hsM, double overrideM, double draftM)
    {
        double l = double.IsNaN(overrideM) ? 0.5 * hsM : overrideM;
        if (double.IsNaN(l)) l = 0;
        return Math.Max(0.0, Math.Min(l, MaxLift(draftM)));
    }

    // seaMeanM / seaMinM: the mean and lowest wave sample over the chunk (0 without Ceto);
    // waterlineM: the lowest waterline of surface units near the chunk (NaN: none).
    internal static double ChunkY(double seaMeanM, double seaMinM, double liftM, double freeboardM, double draftM, double waterlineM)
    {
        if (double.IsNaN(seaMeanM)) seaMeanM = 0;
        if (double.IsNaN(seaMinM)) seaMinM = seaMeanM;
        double y = seaMeanM + Math.Max(0.0, Math.Min(liftM, MaxLift(draftM)));
        y = Math.Min(y, Math.Min(seaMeanM, seaMinM) + draftM - UnderwaterMarginM);
        if (!double.IsNaN(waterlineM)) y = Math.Min(y, waterlineM - freeboardM);
        return y;
    }

    // Per-frame upload budget: always at least one upload, then until the time budget is spent.
    // The budget grows while a refill is under way (many chunks missing), so a date change or a
    // camera jump refills in well under a second instead of 6 chunks per half second.
    internal static double Budget(int missing) => missing > 8 ? RefillBudgetMs : UploadBudgetMs;
    internal static bool MayUpload(int uploadedThisFrame, double elapsedMs, double budgetMs) => uploadedThisFrame == 0 || elapsedMs < budgetMs;
}
