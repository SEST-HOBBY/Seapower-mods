using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;

namespace Sest.RuntimeFixes;

// sest-weather.json, the placed-storms sidecar beside a campaign's
// campaign.json (written by tools/make_sest_weather.py). Pure C#, no DCM
// types: parsed by a strict JSON reader (the runtime does not reference
// Newtonsoft) and resampled into DCM's 6-hourly track shape here, so the
// reflection side (WorldStorms) only copies numbers into DCM objects.
// Any error rejects the whole file with one reason; nothing is half-applied.
//
// {
//   "format": "sest-weather/1",
//   "storms": [ { "id": "darya", "name": "DARYA", "kind": "Cyclone",
//     "waypoints": [ { "utc": "2028-01-15T00:00:00Z", "lat": 19.8, "lon": 64.6,
//                      "wind": 70, "radius": 220 }, ... ] } ]
// }
//
// wind is the maximum sustained wind in knots (DCM TrackPoint.Vmax); radius
// is the outer radius of the storm's wind field in nm (DCM's reach: Outer for
// a tropical storm, 3 x R for an extratropical one). An optional rmw sets a
// tropical storm's radius of maximum wind; by default it is radius / 10, as
// DCM's own NewTropical relates them (Outer = clamp(10 R, 180, 450)). rmw is
// all or nothing per storm: on every waypoint or on none (a partial rmw is
// rejected here and by tools/make_sest_weather.py, the same rule).
// tools/tests/sest_weather_cases.json holds edge cases that this reader and
// the builder's check must both accept or both reject (WorldStormsTests and
// test_make_sest_weather run the same file).
internal sealed class StormSpec
{
    internal string Id, Name, Kind;
    internal readonly List<StormWaypoint> Waypoints = new List<StormWaypoint>();
    internal bool Tropical => Kind != "Storm";
    internal DateTime Born => Waypoints[0].Utc;
    internal DateTime Dies => Waypoints[Waypoints.Count - 1].Utc;
}

internal struct StormWaypoint
{
    internal DateTime Utc;
    internal double Lat, Lon, Wind, Radius, Rmw;
}

// One DCM TrackPoint's numbers.
internal struct StormTrackPoint
{
    internal double Lat, Lon, Vmax, Dp, R, Outer, Env, U, V;
    internal bool Tropical;
}

internal static class StormSidecar
{
    internal const string FileName = "sest-weather.json";
    internal const string Format = "sest-weather/1";
    internal static readonly string[] Kinds = { "Cyclone", "Typhoon", "Hurricane", "Storm" };
    // DCM's own constants: WeatherModel.StepHours and NewTropical's depth law.
    internal const double StepHours = 6;
    internal const double DepthExponent = 1.5527950310559007;

    // null and an error on any problem; never throws.
    internal static List<StormSpec> Parse(string text, out string error)
    {
        error = null;
        try
        {
            var root = new Json(text).Document() as Dictionary<string, object>;
            if (root == null) throw new FormatException("the file is not a JSON object");
            Keys(root, "file", "format", "storms", "note");
            if (Text(root, "format", "file") != Format) throw new FormatException("format is not \"" + Format + "\"");
            var storms = List(root, "storms", "file");
            if (storms.Count < 1 || storms.Count > 16) throw new FormatException("storms must hold 1 to 16 storms");
            var result = new List<StormSpec>();
            var ids = new HashSet<string>(StringComparer.Ordinal);
            foreach (var item in storms)
            {
                var row = item as Dictionary<string, object> ?? throw new FormatException("a storm is not an object");
                Keys(row, "storm", "id", "name", "kind", "waypoints", "note");
                var s = new StormSpec { Id = Text(row, "id", "storm") };
                string where = "storm " + s.Id;
                if (s.Id.Length < 1 || s.Id.Length > 32 || !IdChars(s.Id)) throw new FormatException(where + ": id must be 1-32 of a-z, 0-9 and -");
                if (!ids.Add(s.Id)) throw new FormatException(where + ": id is used twice");
                s.Name = Text(row, "name", where).Trim(' ', '\t', '\r', '\n');
                if (s.Name.Length < 1 || s.Name.Length > 24 || !Printable(s.Name)) throw new FormatException(where + ": name must be 1-24 printable characters");
                s.Kind = Text(row, "kind", where);
                if (Array.IndexOf(Kinds, s.Kind) < 0) throw new FormatException(where + ": kind must be Cyclone, Typhoon, Hurricane or Storm");
                var points = List(row, "waypoints", where);
                if (points.Count < 2 || points.Count > 64) throw new FormatException(where + ": 2 to 64 waypoints are needed");
                foreach (var p in points)
                {
                    var w = p as Dictionary<string, object> ?? throw new FormatException(where + ": a waypoint is not an object");
                    Keys(w, where + " waypoint", "utc", "lat", "lon", "wind", "radius", "rmw");
                    var wp = new StormWaypoint
                    {
                        Utc = Utc(Text(w, "utc", where), where),
                        Lat = Number(w, "lat", where, -80, 85),
                        Lon = Number(w, "lon", where, -180, 360),
                        Wind = Number(w, "wind", where, 10, 185),
                        Radius = Number(w, "radius", where, 30, 600),
                    };
                    wp.Rmw = w.ContainsKey("rmw") ? Number(w, "rmw", where, 5, 80) : 0;
                    if (wp.Rmw > 0 && wp.Rmw >= wp.Radius) throw new FormatException(where + ": rmw must be less than radius");
                    if (s.Waypoints.Count > 0 && wp.Utc <= s.Waypoints[s.Waypoints.Count - 1].Utc) throw new FormatException(where + ": waypoint times must increase");
                    s.Waypoints.Add(wp);
                }
                int withRmw = s.Waypoints.Count(w => w.Rmw > 0);
                if (withRmw > 0 && withRmw < s.Waypoints.Count) throw new FormatException(where + ": rmw must be on every waypoint of the storm or on none");
                if ((s.Dies - s.Born).TotalHours > 30 * 24) throw new FormatException(where + ": a storm may last at most 30 days");
                result.Add(s);
            }
            return result;
        }
        catch (Exception ex) when (ex is FormatException || ex is OverflowException || ex is ArgumentException)
        {
            error = ex.Message;
            return null;
        }
    }

    // DCM's GeoBounds.Continuous: the copy of lon (lon, lon-360, lon+360)
    // nearest the bounds' centre; At and Grid look bins up in this frame.
    internal static double Continuous(double lon, double lonMin, double lonMax)
    {
        double centre = (lonMin + lonMax) / 2, best = lon;
        foreach (double c in new[] { lon - 360, lon + 360 })
            if (Math.Abs(c - centre) < Math.Abs(best - centre)) best = c;
        return best;
    }

    // The 6-hourly track DCM's WeatherSystem.At reads: ceil(life/6)+1 points,
    // point i at min(6 i, life) hours after the first waypoint, each linearly
    // interpolated between waypoints; U/V are the motion in knots (east,
    // north) over the 3 h either side, the way DCM's own points carry it.
    internal static StormTrackPoint[] Track(StormSpec s, double lonMin, double lonMax, out double life)
    {
        life = (s.Dies - s.Born).TotalHours;
        int n = (int)Math.Ceiling(life / StepHours) + 1;
        var track = new StormTrackPoint[n];
        for (int i = 0; i < n; i++)
        {
            double h = Math.Min(i * StepHours, life);
            var p = At(s, h, lonMin, lonMax);
            var a = At(s, Math.Max(0, h - 3), lonMin, lonMax);
            var b = At(s, Math.Min(life, h + 3), lonMin, lonMax);
            double dt = Math.Min(life, h + 3) - Math.Max(0, h - 3);
            double v = dt > 0 ? (b.Lat - a.Lat) * 60 / dt : 0;
            double u = dt > 0 ? (b.Lon - a.Lon) * 60 * Math.Cos(p.Lat * Math.PI / 180) / dt : 0;
            var t = new StormTrackPoint { Lat = p.Lat, Lon = p.Lon, Vmax = p.Wind, Env = 1, U = u, V = v, Tropical = s.Tropical };
            if (s.Tropical)
            {
                t.R = p.Rmw > 0 ? p.Rmw : Math.Max(8, Math.Min(45, p.Radius / 10));
                t.Outer = p.Radius;
                t.Dp = Math.Pow(p.Wind / 6.7, DepthExponent);
            }
            else
            {
                // Extratropical: DCM's reach is 3 R and Vmax = 1.7 Dp (NewExtratropical).
                t.R = p.Radius / 3;
                t.Outer = 0;
                t.Dp = p.Wind / 1.7;
            }
            track[i] = t;
        }
        return track;
    }

    private static StormWaypoint At(StormSpec s, double hours, double lonMin, double lonMax)
    {
        var at = s.Born.AddHours(hours);
        var w = s.Waypoints;
        int k = 0;
        while (k < w.Count - 2 && w[k + 1].Utc <= at) k++;
        var a = w[k]; var b = w[k + 1];
        double f = Math.Max(0, Math.Min(1, (at - a.Utc).TotalHours / (b.Utc - a.Utc).TotalHours));
        double la = Continuous(a.Lon, lonMin, lonMax), lb = Continuous(b.Lon, lonMin, lonMax);
        double rmw = a.Rmw > 0 && b.Rmw > 0 ? a.Rmw + (b.Rmw - a.Rmw) * f : 0;
        return new StormWaypoint
        {
            Utc = at, Lat = a.Lat + (b.Lat - a.Lat) * f, Lon = la + (lb - la) * f,
            Wind = a.Wind + (b.Wind - a.Wind) * f, Radius = a.Radius + (b.Radius - a.Radius) * f, Rmw = rmw
        };
    }

    // A copy of WeatherModel.Build IL_0297-IL_03c2 (DCM 1.0.1, 652fe464;
    // unchanged from 1.0.0, 6008e9c5): the bins an active system covers. The
    // low index is clamped with Max(0, ..) and the high with Min(N-1, ..)
    // only, so the range can be empty, and no longitude wrap is applied (the
    // point is already in the Continuous frame).
    internal static void BinRange(double lat, double lon, double reachNm, double binLat0, double binLon0, int rows, int cols,
                                  out int row0, out int row1, out int col0, out int col1)
    {
        double reachLat = reachNm / 60;
        double reachLon = reachNm / (60 * Math.Max(0.15, Math.Cos(lat * 3.1415926535897931 / 180)));
        row0 = Math.Max(0, (int)Math.Floor((lat - reachLat - binLat0) / 5));
        row1 = Math.Min(rows - 1, (int)Math.Floor((lat + reachLat - binLat0) / 5));
        col0 = Math.Max(0, (int)Math.Floor((lon - reachLon - binLon0) / 5));
        col1 = Math.Min(cols - 1, (int)Math.Floor((lon + reachLon - binLon0) / 5));
    }

    private static bool IdChars(string id)
    {
        foreach (char c in id) if (!(c >= 'a' && c <= 'z' || c >= '0' && c <= '9' || c == '-')) return false;
        return true;
    }
    private static bool Printable(string s)
    {
        foreach (char c in s) if (c < ' ' || c > '~') return false;
        return true;
    }
    private static void Keys(Dictionary<string, object> row, string where, params string[] allowed)
    {
        foreach (var k in row.Keys) if (Array.IndexOf(allowed, k) < 0) throw new FormatException(where + ": unknown field \"" + k + "\"");
    }
    private static string Text(Dictionary<string, object> row, string key, string where) =>
        row.TryGetValue(key, out var v) && v is string s ? s : throw new FormatException(where + ": " + key + " must be a string");
    private static List<object> List(Dictionary<string, object> row, string key, string where) =>
        row.TryGetValue(key, out var v) && v is List<object> l ? l : throw new FormatException(where + ": " + key + " must be a list");
    private static double Number(Dictionary<string, object> row, string key, string where, double min, double max)
    {
        if (!row.TryGetValue(key, out var v) || !(v is double d)) throw new FormatException(where + ": " + key + " must be a number");
        if (double.IsNaN(d) || d < min || d > max) throw new FormatException(where + ": " + key + " must be between " + min.ToString(CultureInfo.InvariantCulture) + " and " + max.ToString(CultureInfo.InvariantCulture));
        return d;
    }
    private static DateTime Utc(string text, string where)
    {
        if (!DateTime.TryParseExact(text, "yyyy-MM-dd'T'HH:mm:ss'Z'", CultureInfo.InvariantCulture,
                DateTimeStyles.AdjustToUniversal | DateTimeStyles.AssumeUniversal, out var t) || t.Year < 1901 || t.Year > 2099)
            throw new FormatException(where + ": utc must read like 2028-01-15T04:00:00Z");
        return DateTime.SpecifyKind(t, DateTimeKind.Utc);
    }

    // Strict JSON (RFC 8259): one value, no comments, no trailing commas,
    // no duplicate keys, finite numbers.
    private sealed class Json
    {
        private readonly string s;
        private int i;
        internal Json(string text) { s = text ?? ""; if (s.Length > 0 && s[0] == '﻿') i = 1; }
        internal object Document()
        {
            var v = Value(0);
            Space();
            if (i != s.Length) throw Bad("text after the JSON value");
            return v;
        }
        private FormatException Bad(string what) => new FormatException("JSON " + what + " at character " + i.ToString(CultureInfo.InvariantCulture));
        private void Space() { while (i < s.Length && (s[i] == ' ' || s[i] == '\t' || s[i] == '\r' || s[i] == '\n')) i++; }
        private object Value(int depth)
        {
            if (depth > 16) throw Bad("nesting too deep");
            Space();
            if (i >= s.Length) throw Bad("ends early");
            char c = s[i];
            if (c == '{')
            {
                i++;
                var o = new Dictionary<string, object>(StringComparer.Ordinal);
                Space();
                if (i < s.Length && s[i] == '}') { i++; return o; }
                while (true)
                {
                    Space();
                    if (i >= s.Length || s[i] != '"') throw Bad("expects a key");
                    string k = Str();
                    Space();
                    if (i >= s.Length || s[i] != ':') throw Bad("expects ':'");
                    i++;
                    if (o.ContainsKey(k)) throw Bad("repeats key \"" + k + "\"");
                    o[k] = Value(depth + 1);
                    Space();
                    if (i < s.Length && s[i] == ',') { i++; continue; }
                    if (i < s.Length && s[i] == '}') { i++; return o; }
                    throw Bad("expects ',' or '}'");
                }
            }
            if (c == '[')
            {
                i++;
                var a = new List<object>();
                Space();
                if (i < s.Length && s[i] == ']') { i++; return a; }
                while (true)
                {
                    a.Add(Value(depth + 1));
                    Space();
                    if (i < s.Length && s[i] == ',') { i++; continue; }
                    if (i < s.Length && s[i] == ']') { i++; return a; }
                    throw Bad("expects ',' or ']'");
                }
            }
            if (c == '"') return Str();
            if (Word("true")) return true;
            if (Word("false")) return false;
            if (Word("null")) return null;
            return Num();
        }
        private bool Word(string w)
        {
            if (string.CompareOrdinal(s, i, w, 0, w.Length) != 0) return false;
            i += w.Length;
            return true;
        }
        private string Str()
        {
            i++;
            var b = new StringBuilder();
            while (true)
            {
                if (i >= s.Length) throw Bad("string not closed");
                char c = s[i++];
                if (c == '"') return b.ToString();
                if (c < ' ') throw Bad("control character in a string");
                if (c != '\\') { b.Append(c); continue; }
                if (i >= s.Length) throw Bad("string not closed");
                char e = s[i++];
                switch (e)
                {
                    case '"': b.Append('"'); break;
                    case '\\': b.Append('\\'); break;
                    case '/': b.Append('/'); break;
                    case 'b': b.Append('\b'); break;
                    case 'f': b.Append('\f'); break;
                    case 'n': b.Append('\n'); break;
                    case 'r': b.Append('\r'); break;
                    case 't': b.Append('\t'); break;
                    case 'u':
                        if (i + 4 > s.Length || !int.TryParse(s.Substring(i, 4), NumberStyles.AllowHexSpecifier, CultureInfo.InvariantCulture, out int u)) throw Bad("bad \\u escape");
                        b.Append((char)u); i += 4; break;
                    default: throw Bad("bad escape");
                }
            }
        }
        private static bool Digit(char c) => c >= '0' && c <= '9';
        private double Num()
        {
            int start = i;
            if (i < s.Length && s[i] == '-') i++;
            if (i >= s.Length || !Digit(s[i])) throw Bad("expects a value");
            if (s[i] == '0') i++; else while (i < s.Length && Digit(s[i])) i++;
            if (i < s.Length && s[i] == '.') { i++; if (i >= s.Length || !Digit(s[i])) throw Bad("bad number"); while (i < s.Length && Digit(s[i])) i++; }
            if (i < s.Length && (s[i] == 'e' || s[i] == 'E'))
            {
                i++;
                if (i < s.Length && (s[i] == '+' || s[i] == '-')) i++;
                if (i >= s.Length || !Digit(s[i])) throw Bad("bad number");
                while (i < s.Length && Digit(s[i])) i++;
            }
            double d = double.Parse(s.Substring(start, i - start), NumberStyles.Float, CultureInfo.InvariantCulture);
            if (double.IsInfinity(d) || double.IsNaN(d)) throw Bad("number out of range");
            return d;
        }
    }
}
