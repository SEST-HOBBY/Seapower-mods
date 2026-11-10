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

    // One completed Admiralty task. Duty is the order kind, or "operation:"
    // plus the operation template; each counts once for versatility.
    internal sealed class AdmiraltyTask
    {
        internal string Kind;
        internal bool Operation;
        internal string Duty => Operation ? "operation:" + Kind : Kind;
    }

    private const string Header = "SEST-WORLD-SERVICE-1";
    // Admiralty evidence keys inside the unchanged six-field v1 line:
    //   <scope>:admiralty:<Kind>:<outcome id>:<completion ticks>     Runtime 1.6.3, still counted
    //   <scope>:admiralty-order:<Kind>:<order id>:<accepted ticks>   standalone order
    //   <scope>:admiralty-operation:<Template>:<operation id>:<accepted ticks>
    // The order and operation ids and their acceptance time survive reloading
    // a save, so replaying a completion does not count it twice. Older
    // binaries ignore every non-manual line except their own legacy keys.
    internal const string LegacyOrderPrefix = ":admiralty:", OrderPrefix = ":admiralty-order:", OperationPrefix = ":admiralty-operation:";
    private static readonly string[] Kinds = { "Intercept", "CoverConvoy", "HuntSubmarine", "Interdict", "Blockade", "CapturePort", "DefendBase", "Shadow", "Barrier", "ClearRoute", "FleetAction" };
    private static readonly string[] Templates = { "SeaControl", "Amphibious", "ConvoyRun", "FleetAction" };
    private readonly string path;
    private readonly Dictionary<string, Entry> entries = new Dictionary<string, Entry>(StringComparer.Ordinal);
    internal bool ReadOnly { get; private set; }
    // Changes whenever the in-memory record changes; views rebuild on it.
    internal int Revision { get; private set; }
    internal IEnumerable<Entry> Entries => entries.Values;
    internal bool Contains(string key) => entries.ContainsKey(key);

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
            Revision++;
        }
        finally { if (File.Exists(temp)) File.Delete(temp); }
    }

    internal List<Ribbon> Ribbons(string scope)
    {
        var manual = entries.Values.Where(e => e.Scope == scope && e.Manual).ToList();
        var tasks = AdmiraltyTasks(scope);
        int Count(string order, string operation) => tasks.Count(t => t.Operation ? t.Kind == operation : t.Kind == order);
        int days = manual.Where(e => e.At > 0).Select(e => new DateTime(e.At).Date).Distinct().Count();
        var regions = new[] { "europe", "middle-east", "africa", "americas", "southern", "pacific" };
        int theatres = manual.Where(e => regions.Contains(e.Theatre)).Select(e => e.Theatre).Distinct().Count();
        var all = new List<Ribbon> {
            Make("meridian", "Meridian Accord Service Ribbon", 3, manual.Count, "Completed three manually commanded world-campaign battles.", "#233C5B|#D8E4E8|#4E9192|#D1B46B|#4E9192|#D8E4E8|#233C5B"),
            Make("iron-meridian", "Iron Meridian Service Ribbon", 10, manual.Count, "Completed ten manually commanded world-campaign battles.", "#343C49|#BFAD78|#6D818C|#BFAD78|#343C49"),
            Make("joint-command", "Joint Maritime Command Ribbon", 20, manual.Count, "Completed twenty manually commanded world-campaign battles.", "#233C5B|#D1B46B|#E0E8E8|#D1B46B|#233C5B"),
            Make("sustained-command", "Sustained Command Service Ribbon", 50, manual.Count, "Completed fifty manually commanded world-campaign battles.", "#293A48|#D1B46B|#4E9192|#D1B46B|#293A48"),
            Make("operational-watch", "Operational Watch Ribbon", 5, days, "Commanded manual battles on five distinct campaign calendar days. This counts evidenced battle days, not assumed deployment time.", "#243B65|#DCE6E8|#5B858A|#DCE6E8|#243B65"),
            Make("enduring-watch", "Enduring Watch Ribbon", 15, days, "Commanded manual battles on fifteen distinct campaign calendar days.", "#243B65|#D9B65B|#5B858A|#D9B65B|#243B65"),
            Make("expeditionary-command", "Expeditionary Command Ribbon", 3, theatres, "Completed positioned manual battles in three different service theatres.", "#35564C|#D7C593|#DCE6E8|#D7C593|#35564C"),
            Make("global-command", "Global Maritime Command Ribbon", 6, theatres, "Completed positioned manual battles in all six service theatres.", "#233C5B|#D9B65B|#4E9192|#D9B65B|#233C5B"),
            Make("admiralty-service", "Admiralty Service Commendation", 5, tasks.Count, "Completed five accepted Admiralty tasks: standalone orders, or whole multi-phase operations counted once each. Failed, lapsed, declined and cancelled tasks do not qualify.", "#174B52|#DCE6E8|#D9B65B|#DCE6E8|#174B52"),
            Make("operational-versatility", "Operational Versatility Ribbon", 3, tasks.Select(t => t.Duty).Distinct().Count(), "Completed accepted Admiralty tasks of three different types; each order kind and each operation type counts once.", "#174B52|#8EA8C3|#D9B65B|#8EA8C3|#174B52"),
            Make("convoy-protection", "Convoy Protection Ribbon", 3, Count("CoverConvoy", "ConvoyRun"), "Completed three accepted convoy-escort orders or convoy-run operations.", "#255A72|#DCE6E8|#4E9192|#DCE6E8|#255A72"),
            Make("surveillance-service", "Maritime Surveillance Ribbon", 3, Count("Shadow", "FleetAction"), "Completed three accepted shadowing orders or fleet-action operations, which open with a shadowing phase.", "#344A6E|#B6C8D4|#35564C|#B6C8D4|#344A6E"),
            Make("route-security", "Route Security Ribbon", 3, Count(null, "ConvoyRun"), "Completed three accepted convoy-run operations, each clearing the convoy's route of submarines before the escort.", "#35564C|#D7C593|#255A72|#D7C593|#35564C")
        };
        foreach (var t in regions)
        {
            all.Add(Make(t, TheatreName(t) + " Service Ribbon", 2, manual.Count(e => e.Theatre == t), "Completed two manually commanded battles with a recorded engagement position in " + TheatreName(t) + ".", TheatreColours(t)));
            all.Add(Make(t + "-veteran", TheatreName(t) + " Veteran Ribbon", 5, manual.Count(e => e.Theatre == t), "Completed five manually commanded battles with a recorded engagement position in " + TheatreName(t) + ".", "#D9B65B|" + TheatreColours(t) + "|#D9B65B"));
        }
        return all;
    }

    // Typed keys are additive within the existing six-field v1 record. Old
    // battle entries and old binaries ignore these non-manual task events.
    internal List<AdmiraltyTask> AdmiraltyTasks(string scope)
    {
        var tasks = new List<AdmiraltyTask>();
        foreach (var e in entries.Values)
            if (e.Scope == scope && TryTask(e, out var task)) tasks.Add(task);
        return tasks;
    }

    internal static bool TryTask(Entry e, out AdmiraltyTask task)
    {
        task = null;
        if (e == null || e.Manual || e.Scope == null || e.Key == null) return false;
        bool legacy = e.Key.StartsWith(e.Scope + LegacyOrderPrefix, StringComparison.Ordinal);
        bool order = e.Key.StartsWith(e.Scope + OrderPrefix, StringComparison.Ordinal);
        bool operation = e.Key.StartsWith(e.Scope + OperationPrefix, StringComparison.Ordinal);
        if (!legacy && !order && !operation) return false;
        var parts = e.Key.Substring(e.Scope.Length + (legacy ? LegacyOrderPrefix : order ? OrderPrefix : OperationPrefix).Length).Split(':');
        if (parts.Length != 3 || !(operation ? Templates : Kinds).Contains(parts[0]) ||
            !int.TryParse(parts[1], NumberStyles.None, CultureInfo.InvariantCulture, out var id) || id <= 0 ||
            !long.TryParse(parts[2], NumberStyles.None, CultureInfo.InvariantCulture, out var ticks)) return false;
        // Legacy keys carry the completion time; the others the acceptance time.
        if (legacy ? ticks != e.At : ticks > e.At) return false;
        task = new AdmiraltyTask { Kind = parts[0], Operation = operation };
        return true;
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
