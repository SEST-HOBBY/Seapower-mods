using System;
using System.Collections.Generic;
using System.Globalization;

namespace Sest.RuntimeFixes;

// The pure rules of SEST's battle sea ice (SeaIce=1 in [Runtime]): ice
// access and speed (a port of the weather branch's mno_env/ice.py), the
// ship speed-cap state machine, the submarine hold under ice, the
// position-keyed concentration cache, the deterministic lead/floe field,
// and the ice-sheet mesher. No Unity or game types: SeaIceTests.exe runs
// all of it under Mono, and the sheet mesher runs on a worker thread.

internal enum IceAccess { Open = 0, Caution = 1, Restricted = 2, Blocked = 3 }

// The one ice edge for every ice rule and every ice picture: the battle
// sheet and its floes, the ship speed cap, the submarine hold, channels, bow
// pieces, breaking sounds and noise, the ice term in the ocean noise, and the
// campaign map's fill, edge line, readout and group speed. Below it there is
// no ice for any of them; at or above it the ice is drawn and acts, so
// whatever slows a ship is on screen. Default 10 %: the first ice.py
// threshold of class none (caution), so the stock speed bands are unchanged
// and the sheet and the map now start where the slowing starts (review,
// 23 Nov: slowed at Bear Island in 13 % ice under a 15 % sheet edge).
// SeaIceEdgePercent in [Runtime] moves it for all of them together (15 is the
// NSIDC extent line); out of range or unreadable: the default, one log line.
internal static class IceEdge
{
    internal const double Default = 10.0, Min = 5.0, Max = 30.0;
    private static double percent = Default;
    private static string configured;
    internal static double Percent => percent;

    // The ini text (Policy.TextOption(lines, "SeaIceEdgePercent", "")). Returns
    // the log line on the first call and on a different text, null otherwise,
    // so SeaIce and CampaignIce can both call it and the log says it once.
    internal static string Configure(string text)
    {
        text = (text ?? "").Trim();
        if (configured != null && configured == text) return null;
        configured = text;
        string why;
        percent = Parse(text, out why);
        return "ice edge " + percent.ToString("0.#", System.Globalization.CultureInfo.InvariantCulture) + " % (" + why + "): ice is drawn, slows ships, holds submarines and shows on the campaign map from here";
    }

    internal static double Parse(string text, out string why)
    {
        if (string.IsNullOrWhiteSpace(text)) { why = "default"; return Default; }
        if (double.TryParse(text.Trim(), System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out double v) && v >= Min && v <= Max)
        { why = "SeaIceEdgePercent"; return v; }
        why = "SeaIceEdgePercent=" + text.Trim() + " ignored, outside " + Min.ToString("0", System.Globalization.CultureInfo.InvariantCulture) + "-" + Max.ToString("0", System.Globalization.CultureInfo.InvariantCulture) + "; default";
        return Default;
    }

    // NaN (unknown) is neither: the callers keep their own NaN rules.
    internal static bool Below(double percentHere) => percentHere < percent;

    // Tests only: put the edge back to a known value.
    internal static void ResetForTests(double value = Default) { percent = value; configured = null; }
}

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
        if (IceEdge.Below(percent)) return IceAccess.Open; // not drawn, so it does not slow (IceEdge)
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
        // under the ice edge nothing is drawn, so nothing holds the hull back: the
        // 1 pp hysteresis applies between ice states, never below the edge (IceEdge)
        if (IceEdge.Below(percent)) { State = IceAccess.Open; return State; }
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

// A local metric frame around a battle origin: east/north kilometres <->
// degrees. The lead field and the sheet chunks are anchored in it, so they do
// not move when the game recentres its floating Unity origin
// (Globals._currentCenterTile). Below PolarFromLatitude it is equirect about
// the origin's latitude (exact north-south, east-west scale cos(lat)/cos(lat0):
// within 1 % over the sheet's 100 km below 70 degrees, but 30 % off at 87N and
// undefined at the pole, where cos(lat0) was clamped to 0.05). At or poleward of
// PolarFromLatitude (SeaIcePolarFrameLatitude, default 85) it is azimuthal
// equidistant about the nearer pole, axes turned so north is true north at the
// origin: north-south exact, east-west within 0.2 % at 85-90 degrees, and the
// pole itself an ordinary point.
internal readonly struct IceFrame
{
    internal const double KmPerDegree = 111.32;
    internal const double DefaultPolarFromLatitude = 85;
    internal static double PolarFromLatitude = DefaultPolarFromLatitude;
    internal readonly double Lat0, Lon0, CosLat0;
    internal readonly bool Polar;
    private readonly double hemi, r0; // +1 north / -1 south; origin's distance from that pole, km
    internal IceFrame(double lat0, double lon0) : this(lat0, lon0, Math.Abs(lat0) >= PolarFromLatitude) { }
    internal IceFrame(double lat0, double lon0, bool polar)
    {
        Lat0 = Math.Max(-90, Math.Min(90, lat0)); Lon0 = lon0;
        CosLat0 = Math.Max(0.05, Math.Cos(Lat0 * Math.PI / 180));
        Polar = polar;
        hemi = Lat0 >= 0 ? 1 : -1;
        r0 = (90 - hemi * Lat0) * KmPerDegree;
    }
    internal string Kind => Polar ? "polar (azimuthal equidistant about the " + (hemi > 0 ? "North" : "South") + " Pole)" : "equirect";
    internal void ToKm(double lat, double lon, out double east, out double north)
    {
        if (Polar)
        {
            double r = (90 - hemi * lat) * KmPerDegree, a = SeaIceModel.LonDelta(lon, Lon0) * Math.PI / 180;
            east = r * Math.Sin(a);
            north = hemi * (r0 - r * Math.Cos(a));
            return;
        }
        north = (lat - Lat0) * KmPerDegree;
        east = SeaIceModel.LonDelta(lon, Lon0) * KmPerDegree * CosLat0;
    }
    internal void ToGeo(double east, double north, out double lat, out double lon)
    {
        if (Polar)
        {
            double y = r0 - hemi * north, r = Math.Sqrt(east * east + y * y);
            lat = hemi * (90 - r / KmPerDegree);
            lon = r < 1e-9 ? Lon0 : SeaIceModel.WrapLon(Lon0 + Math.Atan2(east, y) * 180 / Math.PI);
            return;
        }
        lat = Lat0 + north / KmPerDegree;
        lon = SeaIceModel.WrapLon(Lon0 + east / (KmPerDegree * CosLat0));
    }
    // The origin of a battle: the first position asked about, rounded to a whole degree.
    internal static IceFrame Around(double lat, double lon) => new IceFrame(Math.Round(lat), Math.Round(SeaIceModel.WrapLon(lon)));
}

// The battle's calendar date from the Environment's own fields (Year, Month,
// Day, Hour, Minutes, Seconds), without the exception Environment.DateTime
// throws while they are still zero (a scene whose mission has not set its clock:
// SceneCreator.LoadMission calls SetupMissionEnvironment only after
// CreateTaskforces, and the campaign map's Environment is never dated). The
// game's own default for a missing Date= is 1970-01-01, which is valid here.
internal static class IceDate
{
    internal static bool TryFrom(int year, int month, int day, int hour, int minute, double seconds, out DateTime date)
    {
        date = default;
        if (year < 1900 || year > 2200 || month < 1 || month > 12 || day < 1 || day > DateTime.DaysInMonth(year, month)) return false;
        if (hour < 0 || hour > 23 || minute < 0 || minute > 59 || double.IsNaN(seconds) || double.IsInfinity(seconds)) return false;
        int s = (int)Math.Max(0, Math.Min(59, Math.Floor(seconds)));
        date = new DateTime(year, month, day, hour, minute, s);
        return true;
    }
    internal static string Describe(int year, int month, int day, int hour, int minute) =>
        year.ToString("0000", CultureInfo.InvariantCulture) + "-" + month.ToString("00", CultureInfo.InvariantCulture) + "-" + day.ToString("00", CultureInfo.InvariantCulture) + " " + hour.ToString("00", CultureInfo.InvariantCulture) + ":" + minute.ToString("00", CultureInfo.InvariantCulture);
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

    internal static double Value(double x, double y, uint seed)
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
    // The truth the sheet's near chunks draw and the submarine rule reads: floes below about 60 %
    // (SeaIceFloes), the pack field above. PackInside is the pack field alone (far chunks).
    internal static double Inside(double eastKm, double northKm, double fraction, uint seed) => SeaIceFloes.Inside(eastKm, northKm, fraction, seed);
    internal static double PackInside(double eastKm, double northKm, double fraction, uint seed) => Quantile(fraction) - Noise(eastKm, northKm, seed);

    internal static bool IsIce(double eastKm, double northKm, double fraction, uint seed) => Inside(eastKm, northKm, fraction, seed) > 0;

    // Open water at the centre and FootprintMeters fore, aft and abeam.
    internal static bool FootprintOpen(double eastKm, double northKm, double fraction, uint seed, double footprintMeters)
    {
        double r = footprintMeters / 1000.0;
        return !IsIce(eastKm, northKm, fraction, seed) && !IsIce(eastKm + r, northKm, fraction, seed) && !IsIce(eastKm - r, northKm, fraction, seed)
            && !IsIce(eastKm, northKm + r, fraction, seed) && !IsIce(eastKm, northKm - r, fraction, seed);
    }

    // The sheet draws ice only where the modelled concentration reaches the
    // ice edge (IceEdge.Percent, 10 % by default: where the speed rule starts),
    // so its outer edge is the modelled ice edge; inside it the ice share is
    // the concentration.
    internal static double DrawnFraction(double percent, double edgePercent) => percent >= edgePercent ? Math.Min(1.0, percent / 100.0) : 0.0;

    // Pressure-ridge relief 0..1: sharp ridged noise, elongated.
    internal static double Ridge(double eastKm, double northKm, uint seed)
    {
        double v = Value(eastKm / 0.05 + northKm / 0.21, northKm / 0.05 - eastKm / 0.33, seed ^ 0x1234567u);
        double r = 1 - Math.Abs(2 * v - 1);
        return r * r * r * r;
    }
}

// Discrete floes for open and close drift ice (SeaIceFloeField=1, default on;
// owner's 23 Nov look at MNO Ice 01, about 51 %: the pack noise drew a few
// large solid sheets and their channels vanished in large chunks). Below
// SeaIceFloeFullPercent (default 44 %) the ice is a field of separate floes;
// from SeaIceFloePackPercent (default 60 %, never above the submarine rule's
// heavy-ice percent) it is the pack field above (SeaIceField's lead noise,
// unchanged, so heavy pack and the submarine rule read exactly as before);
// between, the two are blended (smoothstep), which still reads as floes.
// Floes sit on three world-anchored grids (cells 360 m, 150 m and 64 m, one
// candidate floe per cell, centre jittered inside the middle half): number per
// area grows 6.25 x per step while size falls 2.4 x, so the count of floes
// larger than D goes about as D^-2 (open drift ice: many small floes, few big
// ones). A floe is a convex polygon of 7 facets (one of 32 fixed shapes,
// turned and stretched up to 1.6 : 1 per floe). Each floe has a threshold t
// (0..1, hashed) and covers a point when t + rho^2 < q, rho being the
// point's polygon distance in units of the floe's nominal radius (half the
// cell): floes appear one by one as q rises and grow as sqrt(q - t), so
// sparse ice is small floes far apart and close ice is larger floes in
// contact. QStar(x) = min over floes of t + rho^2 (capped at QCap) is
// continuous, so the mesher contours it like the pack field, and the share of
// points with QStar below q is calibrated once (the same quantile method as
// the pack field), so the ice-covered share is still the concentration.
// Carved channels (IceCarve): a floe whose centre lies in a channel and whose
// current radius is at most SeaIceFloePushM (default 60 m) is pushed out of
// the channel whole (not drawn); larger floes are cut by the channel's ragged
// edge as before. The carve marks chunks dirty PushReachM further out, so a
// pushed floe that straddles two chunks goes from both.
internal static class SeaIceFloes
{
    internal const double DefaultFullPercent = 44, DefaultPackPercent = 60, MinGapPercent = 4;
    internal const double DefaultPushM = 60, MaxPushM = 150;
    internal static volatile bool On = true;         // SeaIceFloeField (volatile: a failed calibration on a pool thread switches it off)
    internal static double FullPercent = DefaultFullPercent, PackPercent = DefaultPackPercent; // SeaIceFloeFullPercent, SeaIceFloePackPercent
    internal static double PushM = DefaultPushM;      // SeaIceFloePushM (0: floes are only cut, never pushed)
    internal static readonly double[] CellM = { 360, 150, 64 };
    internal const double RadiusShare = 0.5, Jitter = 0.5, QCap = 2.5, MinAspect = 0.62;
    internal const int Facets = 7, Shapes = 32, Steps = 8;
    private static readonly double[] nx = new double[Shapes * Facets], ny = new double[Shapes * Facets], inv = new double[Shapes * Facets];
    internal static readonly double MaxCirc;          // largest centre-to-corner distance of any shape, in nominal radii
    private static volatile double[][] tables;        // Steps + 1 quantile tables, blend 0 (floes) .. 1 (pack)
    private static readonly object tableLock = new object();

    static SeaIceFloes()
    {
        double worst = 0;
        for (int s = 0; s < Shapes; s++)
        {
            for (int m = 0; m < Facets; m++)
            {
                uint h = Mix(7, s, m, 0xF10E5u);
                double a = 2 * Math.PI * (m + 0.36 * (U(h, 1) - 0.5)) / Facets;
                int k = s * Facets + m;
                nx[k] = Math.Cos(a); ny[k] = Math.Sin(a);
                inv[k] = 1.0 / (0.8 + 0.4 * U(h, 2));
            }
            worst = Math.Max(worst, Circumradius(s));
        }
        MaxCirc = worst;
    }

    // The polygon's farthest corner from its centre (nominal radii), by sampling directions.
    internal static double Circumradius(int shape)
    {
        double worst = 0;
        for (int d = 0; d < 720; d++)
        {
            double a = 2 * Math.PI * d / 720, cx = Math.Cos(a), cy = Math.Sin(a), g = 0;
            for (int m = 0; m < Facets; m++) g = Math.Max(g, (cx * nx[shape * Facets + m] + cy * ny[shape * Facets + m]) * inv[shape * Facets + m]);
            worst = Math.Max(worst, 1 / g);
        }
        return worst;
    }

    // How far beyond a channel's edge a pushed floe can reach, metres (IceCarve's dirty marks).
    // PushReachSlack: in the blend (pack weight up to PushMaxWeight) the lead noise can grow a pushed floe
    // beyond the radius measured at its centre; the dirty marks allow for half as much again.
    internal const double PushMaxWeight = 0.5, PushReachSlack = 1.5;
    internal static double PushReachM => On && PushM > 0 ? PushM * MaxCirc * PushReachSlack : 0;

    // The ini values, checked: full 15..85, pack 20..heavy, at least MinGapPercent apart; else the defaults
    // (pack capped at the heavy percent). Returns a note for the log when something was refused.
    internal static string Configure(bool on, double full, double pack, double pushM, double heavyPercent)
    {
        string note = "";
        On = on;
        if (!(full >= 15 && full <= 85)) { if (!double.IsNaN(full)) note += " SeaIceFloeFullPercent refused;"; full = DefaultFullPercent; }
        if (!(pack >= 20 && pack <= 98)) { if (!double.IsNaN(pack)) note += " SeaIceFloePackPercent refused;"; pack = DefaultPackPercent; }
        if (pack > heavyPercent) { note += " pack field from " + heavyPercent.ToString("0", System.Globalization.CultureInfo.InvariantCulture) + " % (the submarine rule's heavy ice);"; pack = heavyPercent; }
        if (pack - full < MinGapPercent) { note += " floe band too narrow, defaults used;"; full = Math.Min(DefaultFullPercent, pack - MinGapPercent); }
        if (!(pushM >= 0 && pushM <= MaxPushM)) { if (!double.IsNaN(pushM)) note += " SeaIceFloePushM refused;"; pushM = DefaultPushM; }
        FullPercent = full; PackPercent = pack; PushM = pushM;
        return note;
    }

    // Blend weight of the pack field for an ice fraction 0..1: 0 floes, 1 pack (smoothstep from FullPercent to PackPercent).
    internal static double PackWeight(double fraction)
    {
        if (!On) return 1;
        double lo = FullPercent / 100, hi = PackPercent / 100;
        if (!(fraction > lo)) return 0;
        if (fraction >= hi) return 1;
        double t = (fraction - lo) / (hi - lo);
        return t * t * (3 - 2 * t);
    }

    private static uint Mix(int level, int i, int j, uint seed)
    {
        unchecked
        {
            uint h = (uint)i * 0x8da6b343u ^ (uint)j * 0xd8163841u ^ (seed ^ (uint)(level + 1) * 0x9E3779B9u) * 0xcb1ab31fu;
            h ^= h >> 13; h *= 0x85ebca6bu; h ^= h >> 16; h *= 0xc2b2ae35u; h ^= h >> 16;
            return h;
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

    // One candidate floe: centre (metres), threshold, nominal radius (metres), shape, turn, stretch.
    internal struct Floe
    {
        internal double X, Y, T, R, Cos, Sin, Stretch;
        internal int Shape, Level, I, J;
    }

    internal static Floe Candidate(int level, int i, int j, uint seed)
    {
        double L = CellM[level];
        uint h = Mix(level, i, j, seed);
        double a = Math.PI * U(h, 4);
        return new Floe
        {
            X = (i + 0.5 + Jitter * (U(h, 1) - 0.5)) * L, Y = (j + 0.5 + Jitter * (U(h, 2) - 0.5)) * L,
            T = U(h, 3), R = RadiusShare * L, Cos = Math.Cos(a), Sin = Math.Sin(a), Stretch = 1 + (1 / MinAspect - 1) * U(h, 5),
            Shape = (int)(U(h, 6) * Shapes) % Shapes, Level = level, I = i, J = j,
        };
    }

    // Polygon distance of a point (metres) from a floe, in nominal radii (1 on the nominal outline).
    internal static double Rho(in Floe f, double x, double y)
    {
        double dx = x - f.X, dy = y - f.Y;
        double u = (dx * f.Cos + dy * f.Sin) / f.R, v = (dy * f.Cos - dx * f.Sin) / f.R * f.Stretch;
        double g = 0;
        int b = f.Shape * Facets;
        for (int m = 0; m < Facets; m++) { double d = (u * nx[b + m] + v * ny[b + m]) * inv[b + m]; if (d > g) g = d; }
        return g;
    }

    // The floe scalar at a point (metres east/north): min over floes of t + rho^2, capped at QCap.
    // push (null: none) drops floes a channel pushed aside; q is the local threshold (for their current radius).
    internal static double QStar(double x, double y, uint seed, Push push = null)
    {
        double best = QCap;
        for (int level = 0; level < CellM.Length; level++)
        {
            double L = CellM[level], reach = MaxCirc * RadiusShare * L;
            int ci = (int)Math.Floor(x / L), cj = (int)Math.Floor(y / L);
            for (int dj = -1; dj <= 1; dj++)
                for (int di = -1; di <= 1; di++)
                {
                    // the cheap parts of Candidate first (threshold, centre); the turn's trig only for a floe that can win
                    int i = ci + di, j = cj + dj;
                    uint h = Mix(level, i, j, seed);
                    double t = U(h, 3);
                    if (t >= best) continue;
                    double ex = x - (i + 0.5 + Jitter * (U(h, 1) - 0.5)) * L, ey = y - (j + 0.5 + Jitter * (U(h, 2) - 0.5)) * L;
                    if (t + (ex * ex + ey * ey) / (reach * reach) >= best) continue; // rho >= distance / farthest corner
                    var f = Candidate(level, i, j, seed);
                    double r = Rho(f, x, y), v = f.T + r * r;
                    if (v >= best) continue;
                    if (push != null && push.Pushed(f)) continue;
                    best = v;
                }
        }
        return best;
    }

    // Floes a channel pushed out whole, per chunk build (one carve snapshot; decisions cached per floe).
    internal sealed class Push
    {
        private readonly IceCarveSnapshot carve;
        private readonly double maxM;
        private readonly uint seed;
        private readonly Func<double, double, double> fractionAt; // drawn ice fraction 0..1 at east/north km (the model, not the chunk's lattice)
        private readonly Dictionary<long, bool> seen = new Dictionary<long, bool>();
        internal readonly int ExcludeUnit;     // the hull contact test: this ship's own segments newer than
        internal readonly double ExcludeAfter; // ExcludeAfter push nothing for it (the mesher: none excluded)
        internal int Count;
        internal Push(IceCarveSnapshot carve, double maxM, uint seed, Func<double, double, double> fractionAt, int excludeUnit = int.MinValue, double excludeAfter = double.PositiveInfinity)
        {
            this.carve = carve; this.maxM = maxM; this.seed = seed; this.fractionAt = fractionAt;
            ExcludeUnit = excludeUnit; ExcludeAfter = excludeAfter;
        }
        internal bool Over(IceCarveSnapshot snapshot) => ReferenceEquals(snapshot, carve);

        // One decision per floe, made at its centre only (channel, concentration, size), so every sample of
        // the floe, in this chunk and in the chunk next door (same snapshot), agrees: a floe goes whole or stays whole.
        internal bool Pushed(in Floe f)
        {
            if (carve == null || !(maxM > 0) || fractionAt == null) return false;
            long key = ((long)f.Level << 58) ^ ((long)(f.I & 0x1FFFFFFF) << 29) ^ (f.J & 0x1FFFFFFF);
            if (seen.TryGetValue(key, out bool p)) return p;
            p = false;
            double e = f.X / 1000, n = f.Y / 1000;
            if (carve.Field(e, n, ExcludeUnit, ExcludeAfter) < 0)
            {
                double fr = fractionAt(e, n);
                if (fr > 0 && PackWeight(fr) <= PushMaxWeight)
                {
                    double q = EffectiveQ(e, n, fr, seed);
                    p = f.R * Math.Sqrt(Math.Max(0, q - f.T)) <= maxM; // the floe's radius at its centre's concentration
                }
            }
            seen[key] = p;
            if (p) Count++;
            return p;
        }
    }

    internal static string FailedNote = ""; // set once if the calibration failed (floes then off: the pack field everywhere)

    // The calibration, built once (first use or Warm); null, with floes switched off, if it failed.
    internal static bool FailCalibrationForTests; // tests only: make the next calibration throw

    // Tests only: forget the calibration so the next use builds it again.
    internal static void ResetCalibration() { lock (tableLock) { tables = null; FailedNote = ""; } }

    private static double[][] Tables()
    {
        var t = tables;
        if (t != null || !On) return t;
        lock (tableLock)
        {
            if (tables != null || !On) return tables;
            try { if (FailCalibrationForTests) throw new InvalidOperationException("forced by the tests"); tables = Calibrate(); }
            catch (Exception e) { On = false; FailedNote = e.GetType().Name + ": " + e.Message; tables = null; }
            return tables;
        }
    }

    private static double[][] Calibrate()
    {
        const int n = 65536;
        uint seed = SeaIceField.SeedOf(20290310);
        var qs = new double[n];
        var ns = new double[n];
        for (int k = 0; k < n; k++)
        {
            int i = k & 255, j = k >> 8;
            double e = i * 0.0731 + j * 0.0113, no = j * 0.0697 + i * 0.0071;
            qs[k] = QStar(e * 1000, no * 1000, seed);
            ns[k] = SeaIceField.Noise(e, no, seed);
        }
        var all = new double[Steps + 1][];
        var g = new double[n];
        for (int s = 0; s <= Steps; s++)
        {
            double w = (double)s / Steps;
            for (int k = 0; k < n; k++) g[k] = (1 - w) * qs[k] + w * ns[k];
            Array.Sort(g);
            var q = new double[257];
            for (int k = 0; k <= 256; k++) q[k] = g[Math.Min(n - 1, (int)((long)k * (n - 1) / 256))];
            q[0] -= 1e-9; q[256] += 1e-9;
            all[s] = q;
            for (int k = 1; k <= 256; k++) if (!(q[k] >= q[k - 1])) throw new InvalidOperationException("floe calibration not monotone");
        }
        return all;
    }

    // The blended scalar's level below which a point is ice, for an ice fraction p, in table s.
    internal static double Threshold(int s, double p)
    {
        if (!(p > 0)) return -1.0;
        if (p >= 1) return QCap + 2;
        var q = Tables()[s];
        double f = p * 256, k = Math.Floor(f);
        int i = Math.Min(255, (int)k);
        return q[i] + (q[i + 1] - q[i]) * (f - i);
    }

    // > 0 inside ice, < 0 in open water, at east/north km for an ice fraction 0..1 (the mesher's scalar).
    internal static double Inside(double eastKm, double northKm, double fraction, uint seed, Push push = null)
    {
        double s = PackWeight(fraction);
        if (s >= 1 || Tables() == null) return SeaIceField.PackInside(eastKm, northKm, fraction, seed);
        if (!(fraction > 0)) return -1.0;
        double q0 = Threshold(0, fraction);
        double qs = QStar(eastKm * 1000, northKm * 1000, seed, push);
        if (s <= 0) return q0 - qs;
        double noise = SeaIceField.Noise(eastKm, northKm, seed);
        double x = s * Steps;
        int k = Math.Min(Steps - 1, (int)Math.Floor(x));
        double w0 = (double)k / Steps, w1 = (double)(k + 1) / Steps, a = x - k;
        double v0 = Threshold(k, fraction) - ((1 - w0) * qs + w0 * noise), v1 = Threshold(k + 1, fraction) - ((1 - w1) * qs + w1 * noise);
        return v0 + (v1 - v0) * a;
    }

    // The floe-scalar level below which a point is ice at (east, north) km: Inside is linear in QStar,
    // Inside = A - (1 - s) QStar, so the level is A / (1 - s) (s the pack weight; q0 for pure floes).
    internal static double EffectiveQ(double eastKm, double northKm, double fraction, uint seed)
    {
        double s = PackWeight(fraction);
        if (s >= 1 || Tables() == null) return QCap;
        if (s <= 0) return Threshold(0, fraction);
        double noise = SeaIceField.Noise(eastKm, northKm, seed), x = s * Steps;
        int k = Math.Min(Steps - 1, (int)Math.Floor(x));
        double w0 = (double)k / Steps, w1 = (double)(k + 1) / Steps, a = x - k;
        double A = (Threshold(k, fraction) - w0 * noise) * (1 - a) + (Threshold(k + 1, fraction) - w1 * noise) * a;
        double B = (1 - w0) * (1 - a) + (1 - w1) * a;
        return B > 1e-9 ? A / B : QCap;
    }

    // Warm the calibration off the main thread (the first chunk build would otherwise wait about 0.4 s).
    internal static bool Warm() => Tables() != null;
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
                if (TrySlot(i, j, cellKm, fractionAt, seed, out var s)) list.Add(s);
            }
        list.Sort((a, b) => Dist(a, camEastKm, camNorthKm).CompareTo(Dist(b, camEastKm, camNorthKm)));
        if (list.Count > cap) list.RemoveRange(cap, list.Count - cap);
        return list;
    }
    // The candidate floe of cell (i, j), kept when its hash is below the drawn fraction there.
    private static bool TrySlot(int i, int j, double cellKm, Func<double, double, double> fractionAt, uint seed, out FloeSlot s)
    {
        uint h = Mix(i, j, seed);
        double e = (i + 0.15 + 0.7 * U(h, 1)) * cellKm, n = (j + 0.15 + 0.7 * U(h, 2)) * cellKm;
        s = new FloeSlot { East = e, North = n, SizeM = cellKm * 1000 * (0.35 + 0.5 * U(h, 4)), YawDeg = 360 * U(h, 5), Id = ((long)i << 32) ^ (uint)j };
        return U(h, 3) < fractionAt(e, n);
    }

    // Is the point on a fallback floe as SeaIceSheet's Floes driver draws it: a cube SizeM along its
    // local x and 0.7 SizeM along its local z, turned by Quaternion.Euler(0, yaw, 0) (local x = (cos yaw,
    // -sin yaw) and local z = (sin yaw, cos yaw) in east/north)? A floe is at most 0.85 cells long, so
    // only the point's cell and its eight neighbours can hold one that covers it.
    internal static bool Covers(double eastKm, double northKm, double cellKm, Func<double, double, double> fractionAt, uint seed)
    {
        int ci = (int)Math.Floor(eastKm / cellKm), cj = (int)Math.Floor(northKm / cellKm);
        for (int j = cj - 1; j <= cj + 1; j++)
            for (int i = ci - 1; i <= ci + 1; i++)
            {
                if (!TrySlot(i, j, cellKm, fractionAt, seed, out var s)) continue;
                double de = (eastKm - s.East) * 1000, dn = (northKm - s.North) * 1000;
                double y = s.YawDeg * Math.PI / 180, cy = Math.Cos(y), sy = Math.Sin(y);
                double lx = de * cy - dn * sy, lz = de * sy + dn * cy;
                if (Math.Abs(lx) <= s.SizeM * 0.5 && Math.Abs(lz) <= s.SizeM * 0.35) return true;
            }
        return false;
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

// Hull contact with the drawn ice (SeaIceContact=1, default on). The area
// concentration still sets how hard the ice is (the ice.py access table, the
// breaking intensity, the submarine's heavy-ice threshold); whether a hull
// meets it is decided on the ice the player sees:
// - IceSurface: one query for the visual and the rules. Sheet mode reads
//   IceMesher.NodeInside at the near chunk's own interpolated concentration
//   (IceMesher.Lattice and LatticePercent, the functions Build uses, cached per
//   1 km chunk) and in the near chunk's own regime (IceMesher.FloeRegime: the
//   separate floes of SeaIceFloes where the chunk holds drift ice, below about
//   60 %, else the pack field), then cuts the carved channels as the near
//   chunks do: a point in a channel (IceCarveSnapshot.OpennessAt > 0, the
//   test's own ship's fresh track excepted, as for the channel easing) is open
//   water, and so are the small floes pushed out of a channel (SeaIceFloes.Push
//   on the same snapshot, with the same exclusion). Floe mode reads the fallback floes (FloePlacement.Covers,
//   the same slots the Floes driver places) below the heavy-ice percent only
//   (the sparse cubes never open the pack; they are not cut by channels).
// - IceHullContact.Sample: 7 stations from 'near' metres abaft the stern to
//   'near' metres ahead of the stem, each on the centreline and 'near' metres
//   outside either side (21 points), weighted 0.5 at the stern to 1.5 at the
//   bow, where a hull meets the ice. Share = weighted share on ice.
// - Gain = share / fullShare, at most 1 (35 % of the footprint on ice: the
//   full area rule). The speed rule's ice here, ahead and reference are all
//   multiplied by the gain (IceCarve.CapInContact), and so is the breaking
//   intensity (pieces, sounds, breaking noise): contact can only ease the
//   area rule, never harden it, and a hull in open water between floes is not
//   slowed and makes no breaking sound.
// - IceContactState: the gain rises at once and falls with a 1.5 s game-time
//   time constant (0 below 0.05), so a hull sliding along a floe edge does
//   not flicker.
// - Submarines: a held boat is one under heavy ice (unchanged threshold) whose
//   footprint, sampled the same way on the sheet's field, touches ice anywhere.
internal sealed class IceSurface
{
    internal const double FloeCellKm = 0.12; // SeaIceSheet's Floes driver grid
    internal const double ChunkKm = 1.0;     // SeaIceSheet's near (level 0) chunk, IceCarve.ChunkKm
    private const int MaxLattices = 64;      // a hull footprint spans at most 4 chunks; ships in ice, a few each
    // A near chunk's lattice and its regime, exactly as IceMesher.Build decides them for a Detail chunk.
    private sealed class ChunkField
    {
        internal double[] Lattice;
        internal bool Floes;
    }
    private readonly Func<double, double, double> percentAt, floeFraction;
    private readonly Dictionary<long, ChunkField> lattices = new Dictionary<long, ChunkField>();
    private readonly uint seed;
    private readonly double edgePercent, floesBelowPercent;
    internal readonly bool Floes;
    internal readonly Func<double, double, bool> Drawn, Sheet; // cached delegates (no allocation per sample)
    internal int LatticeBuilds;
    internal int LatticeCount => lattices.Count;
    // The carved channels the near chunks cut (null: none), and the ship whose own fresh track does not count.
    // push: the floes the channels push out, for all ships (pushAll, kept per snapshot) or, with an
    // exclusion, with that ship's own fresh track left out as for the cut (rebuilt per test: its
    // decisions depend on the exclusion).
    private IceCarveSnapshot carve;
    private SeaIceFloes.Push push, pushAll;
    private int excludeUnit = int.MinValue;
    private double excludeAfter = double.PositiveInfinity;

    // percentAt(eastKm, northKm): the concentration the sheet reads (the tile cache through the battle frame).
    // floes: the fallback floes are what is drawn; they decide contact only below floesBelowPercent (the
    // heavy-ice percent: the sparse cubes must not open the pack for ships or submarines).
    internal IceSurface(Func<double, double, double> percentAt, uint seed, double edgePercent, bool floes, double floesBelowPercent = 100)
    {
        this.percentAt = percentAt ?? throw new ArgumentNullException(nameof(percentAt));
        this.seed = seed;
        this.edgePercent = edgePercent;
        this.floesBelowPercent = floesBelowPercent;
        Floes = floes;
        floeFraction = (e, n) => SeaIceField.DrawnFraction(this.percentAt(e, n), this.edgePercent);
        Drawn = IceAt;
        Sheet = SheetIceAt;
    }

    // The channels to cut for the next samples (main thread, before IceHullContact.Sample): the carve's
    // published snapshot (what the near chunks are built from; null: channels off), excluding the
    // segments of excludeUnit newer than excludeAfter (game seconds; the ship's own fresh track).
    internal void Channels(IceCarveSnapshot snapshot, int excludeUnit = int.MinValue, double excludeAfter = double.PositiveInfinity)
    {
        if (double.IsNaN(excludeAfter)) excludeAfter = double.PositiveInfinity;
        if (!ReferenceEquals(snapshot, carve)) { carve = snapshot; pushAll = null; }
        this.excludeUnit = excludeUnit;
        this.excludeAfter = excludeAfter;
        if (snapshot == null || !(SeaIceFloes.PushM > 0)) { push = null; return; }
        bool all = excludeUnit == int.MinValue || double.IsPositiveInfinity(excludeAfter);
        if (all) push = pushAll ?? (pushAll = new SeaIceFloes.Push(snapshot, SeaIceFloes.PushM, seed, floeFraction));
        else if (push == null || push == pushAll || !push.Over(snapshot) || push.ExcludeUnit != excludeUnit || push.ExcludeAfter != excludeAfter)
            push = new SeaIceFloes.Push(snapshot, SeaIceFloes.PushM, seed, floeFraction, excludeUnit, excludeAfter);
    }

    private ChunkField ChunkAt(double eastKm, double northKm, out double u, out double v)
    {
        double fi = Math.Floor(eastKm / ChunkKm), fj = Math.Floor(northKm / ChunkKm);
        long key = ((long)fi << 32) ^ (uint)(int)fj;
        if (!lattices.TryGetValue(key, out var chunk))
        {
            if (lattices.Count >= MaxLattices) lattices.Clear();
            var l = IceMesher.Lattice(fi * ChunkKm, fj * ChunkKm, ChunkKm, percentAt);
            chunk = new ChunkField { Lattice = l, Floes = SeaIceFloes.On && IceMesher.FloeRegime(l, edgePercent) };
            lattices[key] = chunk;
            LatticeBuilds++;
        }
        u = Math.Max(0, Math.Min(4, 4 * (eastKm - fi * ChunkKm) / ChunkKm));
        v = Math.Max(0, Math.Min(4, 4 * (northKm - fj * ChunkKm) / ChunkKm));
        return chunk;
    }

    // The near chunk's own interpolated concentration (IceMesher.Lattice / LatticePercent, cached per chunk).
    internal double PercentAt(double eastKm, double northKm)
    {
        var c = ChunkAt(eastKm, northKm, out double u, out double v);
        return IceMesher.LatticePercent(c.Lattice, u, v);
    }

    // Ice in the sheet's field, as the near chunks contour it: the chunk's regime (floes or pack), then
    // the channels cut (a point in a channel, or on a floe pushed out of one, is open water).
    internal bool SheetIceAt(double eastKm, double northKm)
    {
        var c = ChunkAt(eastKm, northKm, out double u, out double v);
        double fr = SeaIceField.DrawnFraction(IceMesher.LatticePercent(c.Lattice, u, v), edgePercent);
        if (!(IceMesher.NodeInside(eastKm, northKm, fr, seed, c.Floes, c.Floes ? push : null) > 0)) return false;
        return carve == null || !(carve.OpennessAt(eastKm, northKm, excludeUnit, excludeAfter) > 0);
    }

    // Ice as drawn: the fallback floes in floe mode below floesBelowPercent, else the sheet's field.
    internal bool IceAt(double eastKm, double northKm)
    {
        if (Floes && PercentAt(eastKm, northKm) < floesBelowPercent) return FloePlacement.Covers(eastKm, northKm, FloeCellKm, floeFraction, seed);
        return SheetIceAt(eastKm, northKm);
    }
}

internal struct HullContact
{
    internal double Share;      // weighted share of the footprint on ice, 0..1
    internal int Samples, OnIce;
    internal bool Any => OnIce > 0;
}

internal static class IceHullContact
{
    internal const int Stations = 7;
    internal const double SternWeight = 0.5, BowWeight = 1.5;
    internal const double DefaultNearM = 10, MaxNearM = 50, DefaultFullShare = 0.35, MinFullShare = 0.05;
    internal const double DefaultLengthM = 100, DefaultBeamM = 15;

    // eastKm/northKm: the hull's centre in the battle frame; headingDeg: true heading (clockwise from north).
    internal static HullContact Sample(double eastKm, double northKm, double headingDeg, double lengthM, double beamM, double nearM, Func<double, double, bool> iceAt)
    {
        var r = new HullContact();
        if (iceAt == null || double.IsNaN(eastKm) || double.IsNaN(northKm) || double.IsInfinity(eastKm) || double.IsInfinity(northKm)) return r;
        if (!(lengthM > 0) || double.IsInfinity(lengthM)) lengthM = DefaultLengthM;
        if (!(beamM > 0) || double.IsInfinity(beamM)) beamM = DefaultBeamM;
        if (!(nearM >= 0) || double.IsInfinity(nearM)) nearM = DefaultNearM;
        if (double.IsNaN(headingDeg) || double.IsInfinity(headingDeg)) headingDeg = 0;
        double h = headingDeg * Math.PI / 180, fe = Math.Sin(h), fn = Math.Cos(h); // forward, east/north
        double se = fn, sn = -fe;                                                  // starboard
        double half = (lengthM / 2 + nearM) / 1000, side = (beamM / 2 + nearM) / 1000;
        double sum = 0, ice = 0;
        for (int k = 0; k < Stations; k++)
        {
            double t = (double)k / (Stations - 1);   // 0 stern .. 1 bow
            double along = -half + 2 * half * t;
            double w = SternWeight + (BowWeight - SternWeight) * t;
            for (int a = -1; a <= 1; a++)
            {
                double e = eastKm + fe * along + se * a * side, n = northKm + fn * along + sn * a * side;
                r.Samples++;
                sum += w;
                if (iceAt(e, n)) { r.OnIce++; ice += w; }
            }
        }
        r.Share = sum > 0 ? ice / sum : 0;
        return r;
    }

    // How much of the area rule applies: 0 off the ice, 1 once fullShare of the footprint is on it.
    internal static double Gain(double share, double fullShare)
    {
        if (double.IsNaN(share) || share <= 0) return 0;
        if (!(fullShare > 0)) return 1;
        return Math.Min(1, share / fullShare);
    }
}

// The gain per hull over time: up at once (a hull that meets ice is slowed and heard at once), down with
// a ReleaseS time constant of game time, and 0 below MinGain (so the breaking sound, whose loop starts at
// a floor volume for any intensity above 0, stops about 4.5 s after the hull clears the ice). An unknown
// target counts as full contact (the area rule).
internal sealed class IceContactState
{
    internal const double ReleaseS = 1.5, MinGain = 0.05, MaxStepS = 60;
    internal double Gain = double.NaN;
    private double t = double.NaN;

    internal double Update(double target, double now)
    {
        if (double.IsNaN(target)) target = 1;
        target = target < MinGain ? 0 : Math.Min(1, target);
        if (double.IsNaN(Gain) || double.IsNaN(t) || double.IsNaN(now) || now < t || target >= Gain) { Gain = target; t = now; return Gain; }
        double dt = Math.Min(MaxStepS, now - t);
        t = now;
        Gain = Math.Max(target, Gain * Math.Exp(-dt / ReleaseS));
        if (Gain < MinGain) Gain = target;
        return Gain;
    }
}

// One chunk of the ice sheet as plain arrays (metres, x east, y up, z north,
// relative to the chunk centre), built by marching squares over
// SeaIceField.Inside on a (Cells+1)^2 grid. Top faces at the freeboard plus
// ridge relief; with Underside a closed slab: the underside at -draft and
// one-sided outward walls along every boundary edge of the top (the ice
// contour and the chunk border), so the slab is watertight and the sea
// surface inside it never shows. Unity's front faces are clockwise as seen by
// the viewer; Normals hold one unit normal per vertex (top: the polygon's
// face normal, or straight up with FlatNormals; underside: down; walls:
// horizontal, outward). A carve snapshot (ship channels, IceCarve) cuts open
// water into the field before contouring.
internal sealed class IceChunkMesh
{
    internal float[] Vertices = new float[0]; // xyz triples
    internal float[] Normals = new float[0];  // xyz triples, one per vertex
    internal int[] Triangles = new int[0];
    internal int CarvedCells, ContourWalls, BorderWalls;
    internal int Grid;          // cells per side
    internal int PushedFloes;   // floes a channel pushed out whole
    internal bool Floes;        // contoured the floe field (a near chunk with drift ice)
    internal bool[] Solid = new bool[0]; // Grid x Grid, row by row from the south-west: all four corners ice
    internal int IceCells, OpenCells;
    internal double MeanFraction;
    internal int TriangleCount => Triangles.Length / 3;
}

internal struct IceChunkSpec
{
    internal double CentreEastKm, CentreNorthKm, SizeKm;
    internal int Cells;
    internal bool Underside;      // closed slab: underside and outward walls along the contour and the chunk border
    internal bool FlatNormals;    // top normals straight up (far chunks: no specular shimmer from coarse ridges)
    internal double FreeboardM, DraftM, RidgeM, EdgePercent;
    internal uint Seed;
    internal IceCarveSnapshot Carve; // ship channels cut into the field (null: none)
    internal bool Detail;         // near chunk: draw discrete floes (SeaIceFloes) where the ice is drift ice; false: the pack field only
    internal int FloeCells;       // with Detail: cells per side when any of the chunk is drift ice (0: Cells)
}

internal static class IceMesher
{
    // The chunk's 5 x 5 concentration lattice (percent), corners e0/n0 (km) to e0/n0 + size.
    // Shared with the hull contact test (IceSurface), which must read exactly the drawn ice.
    internal static double[] Lattice(double e0, double n0, double sizeKm, Func<double, double, double> percentAt)
    {
        var lattice = new double[25];
        for (int j = 0; j < 5; j++)
            for (int i = 0; i < 5; i++)
                lattice[j * 5 + i] = percentAt(e0 + sizeKm * i / 4, n0 + sizeKm * j / 4);
        return lattice;
    }

    // Bilinear concentration inside the lattice; u, v in lattice steps, 0..4.
    internal static double LatticePercent(double[] lattice, double u, double v)
    {
        int a = Math.Min(3, (int)u), b = Math.Min(3, (int)v);
        double tu = u - a, tv = v - b;
        return (lattice[b * 5 + a] * (1 - tu) + lattice[b * 5 + a + 1] * tu) * (1 - tv) + (lattice[(b + 1) * 5 + a] * (1 - tu) + lattice[(b + 1) * 5 + a + 1] * tu) * tv;
    }

    // The scalar a chunk contours at a grid node, before channels are cut: > 0 ice. The one place the
    // drawn field is chosen, read by the mesher and the hull contact test alike: floes (a near chunk
    // with drift ice in its lattice: SeaIceFloes, with the floes pushed out of channels) or the pack field.
    internal static double NodeInside(double eastKm, double northKm, double fraction, uint seed, bool floes = false, SeaIceFloes.Push push = null) =>
        fraction <= 0 ? -1.0 : floes ? SeaIceFloes.Inside(eastKm, northKm, fraction, seed, push) : SeaIceField.PackInside(eastKm, northKm, fraction, seed);

    // percentAt(eastKm, northKm): concentration percent. Sampled on a 5 x 5 lattice per chunk and
    // interpolated, so a chunk costs 25 model evaluations however fine its grid.
    internal static IceChunkMesh Build(IceChunkSpec s, Func<double, double, double> percentAt)
    {
        double e0 = s.CentreEastKm - s.SizeKm / 2, n0 = s.CentreNorthKm - s.SizeKm / 2;
        var lattice = Lattice(e0, n0, s.SizeKm, percentAt);
        bool floes = s.Detail && SeaIceFloes.On && FloeRegime(lattice, s.EdgePercent);
        int n = Math.Max(2, floes && s.FloeCells > s.Cells ? s.FloeCells : s.Cells);
        double h = s.SizeKm / n;
        var push = floes && s.Carve != null && SeaIceFloes.PushM > 0 ? new SeaIceFloes.Push(s.Carve, SeaIceFloes.PushM, s.Seed, (e, nn) => SeaIceField.DrawnFraction(percentAt(e, nn), s.EdgePercent)) : null;
        var f = new double[(n + 1) * (n + 1)];
        double sum = 0;
        int carved = 0;
        for (int j = 0; j <= n; j++)
            for (int i = 0; i <= n; i++)
            {
                double p = LatticePercent(lattice, 4.0 * i / n, 4.0 * j / n);
                double fr = SeaIceField.DrawnFraction(p, s.EdgePercent);
                sum += fr;
                double v0 = NodeInside(e0 + i * h, n0 + j * h, fr, s.Seed, floes, push);
                if (v0 > 0 && s.Carve != null)
                {
                    double g = s.Carve.Field(e0 + i * h, n0 + j * h);
                    if (g < 0) { v0 = Math.Min(v0, 0.5 * g); carved++; }
                }
                f[j * (n + 1) + i] = v0;
            }
        var solid = new bool[n * n];
        var mesh = new IceChunkMesh { MeanFraction = sum / f.Length, CarvedCells = carved, Grid = n, Solid = solid, PushedFloes = push != null ? push.Count : 0, Floes = floes };
        var verts = new List<float>(4096);
        var norms = new List<float>(4096);
        var tris = new List<int>(4096);
        var poly = new double[8 * 3];
        var cross = new bool[8];
        for (int j = 0; j < n; j++)
            for (int i = 0; i < n; i++)
            {
                double f0 = f[j * (n + 1) + i], f1 = f[j * (n + 1) + i + 1], f2 = f[(j + 1) * (n + 1) + i + 1], f3 = f[(j + 1) * (n + 1) + i];
                if (f0 <= 0 && f1 <= 0 && f2 <= 0 && f3 <= 0) { mesh.OpenCells++; continue; }
                mesh.IceCells++;
                if (f0 > 0 && f1 > 0 && f2 > 0 && f3 > 0) solid[j * n + i] = true;
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
                // the top polygon's face normal (Newell; the corner walk is counter-clockwise seen from above)
                double nx = 0, ny = 0, nz = 0;
                for (int k = 0; k < count; k++)
                {
                    int a = (baseTop + k) * 3, b = (baseTop + (k + 1) % count) * 3;
                    nx += (verts[a + 1] - verts[b + 1]) * (verts[a + 2] + verts[b + 2]);
                    ny += (verts[a + 2] - verts[b + 2]) * (verts[a] + verts[b]);
                    nz += (verts[a] - verts[b]) * (verts[a + 1] + verts[b + 1]);
                }
                // Newell over (x east, z north) counter-clockwise gives -y; Unity's up is +y
                nx = -nx; ny = -ny; nz = -nz;
                double len = Math.Sqrt(nx * nx + ny * ny + nz * nz);
                if (s.FlatNormals || !(len > 1e-12) || ny <= 0) { nx = 0; ny = 1; nz = 0; len = 1; }
                for (int k = 0; k < count; k++) Add(norms, nx / len, ny / len, nz / len);
                for (int k = 1; k + 1 < count; k++) { tris.Add(baseTop); tris.Add(baseTop + k + 1); tris.Add(baseTop + k); }
                if (!s.Underside) continue;
                int baseBottom = verts.Count / 3;
                for (int k = 0; k < count; k++)
                {
                    Add(verts, (e0 + poly[k * 3] * h - s.CentreEastKm) * 1000, -s.DraftM, (n0 + poly[k * 3 + 1] * h - s.CentreNorthKm) * 1000);
                    Add(norms, 0, -1, 0);
                }
                for (int k = 1; k + 1 < count; k++) { tris.Add(baseBottom); tris.Add(baseBottom + k); tris.Add(baseBottom + k + 1); }
                // walls along every boundary edge of the top: the contour (two consecutive crossing points)
                // and the chunk border (both ends on one border line); one-sided, facing outward
                for (int k = 0; k < count; k++)
                {
                    int m = (k + 1) % count;
                    bool contour = cross[k] && cross[m];
                    double xk = poly[k * 3], yk = poly[k * 3 + 1], xm = poly[m * 3], ym = poly[m * 3 + 1];
                    bool border = (xk == 0 && xm == 0) || (xk == n && xm == n) || (yk == 0 && ym == 0) || (yk == n && ym == n);
                    if (!contour && !border) continue;
                    int w = verts.Count / 3;
                    int ta = baseTop + k, tb = baseTop + m, ba = baseBottom + k, bb = baseBottom + m;
                    Copy(verts, ta); Copy(verts, tb); Copy(verts, bb); Copy(verts, ba);
                    // outward: to the right of the counter-clockwise edge direction
                    double dx = (xm - xk) * h, dz = (ym - yk) * h, dl = Math.Sqrt(dx * dx + dz * dz);
                    double ox = dl > 0 ? dz / dl : 0, oz = dl > 0 ? -dx / dl : 0;
                    for (int q = 0; q < 4; q++) Add(norms, ox, 0, oz);
                    tris.Add(w); tris.Add(w + 1); tris.Add(w + 2); tris.Add(w); tris.Add(w + 2); tris.Add(w + 3);
                    if (contour) mesh.ContourWalls++; else mesh.BorderWalls++;
                }
            }
        mesh.Vertices = verts.ToArray();
        mesh.Normals = norms.ToArray();
        mesh.Triangles = tris.ToArray();
        return mesh;
    }

    // Is any of the chunk drift ice (drawn, and below the pack blend's top)? Then a near chunk draws floes.
    internal static bool FloeRegime(double[] lattice, double edgePercent)
    {
        foreach (double p in lattice) if (p >= edgePercent && SeaIceFloes.PackWeight(p / 100) < 1) return true;
        return false;
    }

    // The ocean clip mask of a chunk (Ceto clip overlay: white removes the sea surface): solid cells
    // whose neighbours within `erode` cells are solid too, so the clip always lies inside the slab and
    // never opens a hole in a lead or at the ice edge.
    internal static bool[] ClipMask(bool[] solid, int n, int erode)
    {
        var mask = new bool[n * n];
        if (solid == null || solid.Length != n * n) return mask;
        for (int j = 0; j < n; j++)
            for (int i = 0; i < n; i++)
            {
                bool ok = solid[j * n + i];
                for (int dj = -erode; ok && dj <= erode; dj++)
                    for (int di = -erode; ok && di <= erode; di++)
                    {
                        int a = i + di, b = j + dj;
                        if (a < 0 || b < 0 || a >= n || b >= n) continue; // the chunk border: the slab's border wall closes it
                        ok = solid[b * n + a];
                    }
                mask[j * n + i] = ok;
            }
        return mask;
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
