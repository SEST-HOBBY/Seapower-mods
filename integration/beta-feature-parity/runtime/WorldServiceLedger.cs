using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;

namespace Sest.RuntimeFixes;

// An independent profile service record. Native campaign saves are read only.
internal sealed class WorldServiceLedger
{
    internal sealed class Entry
    {
        internal string Scope, Key, Where, Theatre;
        internal long At;
        internal bool Manual;
    }

    internal sealed class Ribbon
    {
        internal string Id, Name, Citation;
        internal string[] Colours;
        internal int Required, Progress;
        internal bool Earned => Progress >= Required;
    }

    private const string Header = "SEST-WORLD-SERVICE-1";
    private readonly string path;
    private readonly Dictionary<string, Entry> entries = new Dictionary<string, Entry>(StringComparer.Ordinal);
    internal bool ReadOnly { get; private set; }
    internal IEnumerable<Entry> Entries => entries.Values;

    internal WorldServiceLedger(string file)
    {
        path = file;
        if (!File.Exists(path)) return;
        try
        {
            if (new FileInfo(path).Length > 16000000) throw new InvalidDataException("service record too large");
            var lines = File.ReadAllLines(path, Encoding.UTF8);
            if (lines.Length == 0 || lines[0] != Header || lines.Length > 20001)
                throw new InvalidDataException("unknown service record format");
            foreach (var line in lines.Skip(1))
            {
                var e = Decode(line);
                if (entries.ContainsKey(e.Key)) throw new InvalidDataException("duplicate service event");
                entries.Add(e.Key, e);
            }
        }
        catch (Exception ex)
        {
            entries.Clear();
            ReadOnly = true;
            Api.LogFailure("world service record is read-only; existing file preserved", ex);
        }
    }

    private static string B64(string value) => Convert.ToBase64String(Encoding.UTF8.GetBytes(value ?? ""));
    private static string Text(string value) => Encoding.UTF8.GetString(Convert.FromBase64String(value));
    private static string Encode(Entry e) => string.Join("\t", B64(e.Scope), B64(e.Key), e.At.ToString(CultureInfo.InvariantCulture), e.Manual ? "1" : "0", B64(e.Where), B64(e.Theatre));
    private static Entry Decode(string line)
    {
        if (line.Length > 16384) throw new InvalidDataException("service entry too long");
        var p = line.Split('\t');
        if (p.Length != 6 || (p[3] != "0" && p[3] != "1")) throw new InvalidDataException("invalid service entry");
        var e = new Entry { Scope = Text(p[0]), Key = Text(p[1]), At = long.Parse(p[2], CultureInfo.InvariantCulture), Manual = p[3] == "1", Where = Text(p[4]), Theatre = Text(p[5]) };
        if (string.IsNullOrWhiteSpace(e.Scope) || string.IsNullOrWhiteSpace(e.Key) || e.Scope.Length > 256 || e.Key.Length > 512 || e.Where.Length > 512 || e.Theatre.Length > 32 || e.At < DateTime.MinValue.Ticks || e.At > DateTime.MaxValue.Ticks)
            throw new InvalidDataException("invalid service event values");
        return e;
    }

    // One batch/atomic write, regardless of how many historical reports were loaded.
    internal void Merge(IEnumerable<Entry> completed)
    {
        if (ReadOnly) return;
        var next = new Dictionary<string, Entry>(entries, StringComparer.Ordinal);
        bool changed = false;
        foreach (var item in completed)
        {
            var e = Decode(Encode(item));
            if (next.TryGetValue(e.Key, out var old))
            {
                // A later observed coordinate may add evidence, never erase it.
                if (old.Theatre.Length == 0 && e.Theatre.Length > 0 && old.Scope == e.Scope && old.At == e.At && old.Manual == e.Manual)
                { next[e.Key] = e; changed = true; }
            }
            else { next.Add(e.Key, e); changed = true; }
        }
        if (!changed) return;
        if (next.Count > 20000) throw new InvalidDataException("service record event limit reached");
        Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(path)));
        string temp = path + "." + Guid.NewGuid().ToString("N") + ".tmp";
        try
        {
            File.WriteAllLines(temp, new[] { Header }.Concat(next.Values.OrderBy(e => e.Key, StringComparer.Ordinal).Select(Encode)), new UTF8Encoding(false));
            if (File.Exists(path)) File.Replace(temp, path, null); else File.Move(temp, path);
            entries.Clear(); foreach (var pair in next) entries.Add(pair.Key, pair.Value);
        }
        finally { if (File.Exists(temp)) File.Delete(temp); }
    }

    internal List<Ribbon> Ribbons(string scope)
    {
        var manual = entries.Values.Where(e => e.Scope == scope && e.Manual).ToList();
        var all = new List<Ribbon> {
            Make("meridian", "Meridian Accord Service Ribbon", 3, manual.Count, "Completed three manually commanded world-campaign battles.", "#233C5B|#D8E4E8|#4E9192|#D1B46B|#4E9192|#D8E4E8|#233C5B"),
            Make("iron-meridian", "Iron Meridian Service Ribbon", 10, manual.Count, "Completed ten manually commanded world-campaign battles.", "#343C49|#BFAD78|#6D818C|#BFAD78|#343C49")
        };
        foreach (var t in new[] { "europe", "middle-east", "africa", "americas", "southern", "pacific" })
            all.Add(Make(t, TheatreName(t) + " Service Ribbon", 2, manual.Count(e => e.Theatre == t), "Completed two manually commanded battles with a recorded engagement position in " + TheatreName(t) + ".", TheatreColours(t)));
        return all;
    }

    private static Ribbon Make(string id, string name, int required, int progress, string citation, string colours) => new Ribbon { Id = id, Name = name, Required = required, Progress = progress, Citation = citation, Colours = colours.Split('|') };
    internal static string TheatreName(string id)
    {
        switch (id) {
            case "europe": return "European Waters";
            case "middle-east": return "Middle East and Indian Ocean";
            case "africa": return "African and Cape Routes";
            case "americas": return "Americas and Southern Ocean";
            case "southern": return "Allied Southern Flank";
            case "pacific": return "Pacific and East Asia";
            default: return "Position not recorded";
        }
    }
    private static string TheatreColours(string id)
    {
        switch (id) {
            case "europe": return "#283E69|#CBD6DD|#7B8EAB|#CBD6DD|#283E69";
            case "middle-east": return "#4F6659|#D4BC81|#B88962|#D4BC81|#4F6659";
            case "africa": return "#35564C|#B7A16A|#D7C593|#B7A16A|#35564C";
            case "americas": return "#3E536B|#D7E2E6|#9A5D59|#D7E2E6|#3E536B";
            case "southern": return "#344A6E|#DCE6EB|#759DAF|#DCE6EB|#344A6E";
            default: return "#255A72|#A5CFD4|#D4B96D|#A5CFD4|#255A72";
        }
    }

    internal static string Theatre(double lat, double lon)
    {
        if (double.IsNaN(lat) || double.IsNaN(lon) || double.IsInfinity(lat) || double.IsInfinity(lon) || lat < -90 || lat > 90) return "";
        lon = ((lon + 180) % 360 + 360) % 360 - 180;
        // Ordered, mutually exclusive evidence regions; campaign coordinates
        // themselves retain DCM's continuous longitude interval.
        if (lon >= -25 && lon <= 45 && lat >= 30) return "europe";
        if (lon >= 30 && lon < 100 && lat >= -5 && lat < 32) return "middle-east";
        if (lon >= -25 && lon < 55 && lat >= -40 && lat < 30) return "africa";
        if (lon < -25 && lon >= -130) return "americas";
        if (lat < -5 && lon >= 100) return "southern";
        if (lon >= 100 || lon < -130) return "pacific";
        return "";
    }
}
