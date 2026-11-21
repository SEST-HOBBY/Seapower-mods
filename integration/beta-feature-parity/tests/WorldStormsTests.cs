using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;

// Placed storms (runtime/WorldStorms.cs, runtime/StormSidecar.cs) against the
// captured Dynamic Campaign Mod 1.0.0 (6008e9c5), under Mono without Unity:
// every member binding, a WeatherSystem built from the committed Hormuz
// sidecar, the Build injection run on real WeatherModel instances through
// reflection, and models without a sidecar compared with untouched ones;
// every edge case in tools/tests/sest_weather_cases.json (found above the
// sidecar) through File.ReadAllText and StormSidecar.Parse, as the builder's
// test runs them through check_bytes; the stale-cache guard, an unreadable
// sidecar, Stop clearing tied models; and the tactical map's Weather layer:
// its geometry, the storms it collects from a real model, and every game and
// DCM member it binds (Seapower-Scripts.dll from the flat references).
//   mono WorldStormsTests.exe <flat refs> SEST.RuntimeFixes.dll DynamicCampaignMod.dll <hormuz sest-weather.json>
static class WorldStormsTests
{
    const BindingFlags All = BindingFlags.Instance | BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic;
    static int checks;
    static TextWriter console;
    static StringWriter log;
    static Type ws, sidecar, defType, boundsType, modelType, geoType, theatreType;
    static void Check(bool ok, string why)
    {
        checks++;
        if (!ok)
        {
            Console.SetOut(console);
            Console.WriteLine(log.ToString());
            throw new Exception("FAILED: " + why);
        }
    }
    static object Get(object value, string field)
    {
        Type t = value as Type ?? value.GetType();
        var f = t.GetField(field, All) ?? throw new MissingFieldException(t.FullName, field);
        return f.GetValue(value is Type ? null : value);
    }
    static object Prop(object value, string name) => value.GetType().GetProperty(name, All).GetValue(value, null);
    static void Set(object value, string field, object data) => value.GetType().GetField(field, All).SetValue(value, data);
    static object Call(object target, string name, Type[] types, params object[] args)
    {
        Type t = target as Type ?? target.GetType();
        var m = t.GetMethod(name, All, null, types, null) ?? throw new MissingMethodException(t.FullName, name);
        try { return m.Invoke(target is Type ? null : target, args); }
        catch (TargetInvocationException e) { throw e.InnerException; }
    }
    static DateTime Utc(string s) => DateTime.SpecifyKind(DateTime.ParseExact(s, "yyyy-MM-dd'T'HH:mm'Z'", CultureInfo.InvariantCulture), DateTimeKind.Utc);
    static object Geo(double lat, double lon) => Activator.CreateInstance(geoType, lat, lon);
    static object Bounds()
    {
        object b = Activator.CreateInstance(boundsType);
        Set(b, "latMin", 20.0); Set(b, "latMax", 31.0); Set(b, "lonMin", 47.0); Set(b, "lonMax", 65.0);
        return b;
    }
    // A CampaignDefinition as CampaignDefinition.Load leaves it: FilePath
    // names campaign.json in the folder that may hold the sidecar.
    static object Definition(string folder, string sidecarText)
    {
        Directory.CreateDirectory(folder);
        File.WriteAllText(Path.Combine(folder, "campaign.json"), "{}");
        string side = Path.Combine(folder, "sest-weather.json");
        if (sidecarText != null) File.WriteAllText(side, sidecarText); else if (File.Exists(side)) File.Delete(side);
        object d = Activator.CreateInstance(defType, true);
        Set(d, "FilePath", Path.Combine(folder, "campaign.json"));
        Set(d, "bounds", Bounds());
        Set(d, "weather", "atlantic");
        return d;
    }
    static object For(object definition, int seed) => Call(modelType, "For", new[] { defType, typeof(int) }, definition, seed);
    // Never through For: SEST ties no storms to it, so it is DCM's own model.
    static object Untouched(object definition, int seed)
    {
        object theatre = Call(theatreType, "Of", new[] { defType }, definition);
        return Activator.CreateInstance(modelType, All, null, new[] { theatre, seed, Bounds() }, null);
    }
    static object At(object model, double lat, double lon, DateTime utc) => Call(model, "At", new[] { geoType, typeof(DateTime) }, Geo(lat, lon), utc);
    static List<object> Storms(object model, DateTime utc) => ((IEnumerable)Call(model, "Storms", new[] { typeof(DateTime), typeof(int) }, utc, 72)).Cast<object>().ToList();
    static object Report(object model, DateTime utc, string id) => Storms(model, utc).FirstOrDefault(r => (string)Get(r, "Id") == id);
    static string Sample(object s) => string.Join("|", new[] { "WindKnots", "WindFromDeg", "SeaState", "Cloud", "Rain", "Thunderstorm", "Fog", "Typhoon", "PressureHpa", "StormId", "StormLabel" }
        .Select(f => Convert.ToString(Get(s, f), CultureInfo.InvariantCulture)));
    static object Snapshot(object model, DateTime utc) => Call(model, "Build", new[] { typeof(DateTime) }, utc);
    static int Lines(string text) => log.ToString().Split('\n').Count(l => l.Contains(text));

    static void Main(string[] args)
    {
        string refs = Path.GetFullPath(args[0]);
        AppDomain.CurrentDomain.AssemblyResolve += (s, e) => { string p = Path.Combine(refs, new AssemblyName(e.Name).Name + ".dll"); return File.Exists(p) ? Assembly.LoadFrom(p) : null; };
        Assembly.LoadFrom(Path.Combine(refs, "0Harmony.dll"));
        var rt = Assembly.LoadFrom(Path.GetFullPath(args[1]));
        var dcm = Assembly.LoadFrom(Path.GetFullPath(args[2]));
        string hormuz = File.ReadAllText(Path.GetFullPath(args[3]));
        string cases = null;
        for (var d = new DirectoryInfo(Path.GetDirectoryName(Path.GetFullPath(args[3]))); d != null && cases == null; d = d.Parent)
        {
            string c = Path.Combine(d.FullName, "tools", "tests", "sest_weather_cases.json");
            if (File.Exists(c)) cases = c;
        }
        if (cases == null) throw new FileNotFoundException("tools/tests/sest_weather_cases.json above " + args[3]);
        game = Assembly.LoadFrom(Path.Combine(refs, "Seapower-Scripts.dll"));
        console = Console.Out;
        log = new StringWriter();
        Console.SetOut(log);
        string dir = Path.Combine(Path.GetTempPath(), "SEST-WorldStorms-" + Guid.NewGuid().ToString("N"));
        try { Run(rt, dcm, hormuz, cases, dir); }
        finally { try { Directory.Delete(dir, true); } catch { } Console.SetOut(console); }
        // SEST_STORMS_LOG=1 prints the runtime's log lines, as the PC log would show them.
        if (Environment.GetEnvironmentVariable("SEST_STORMS_LOG") == "1") Console.Write(log.ToString());
        Console.WriteLine("World storms: " + checks + " checks passed against Dynamic Campaign Mod 1.0.0 (6008e9c5); no Unity, no PC gameplay claim.");
    }

    static Assembly game;
    static readonly HashSet<string> MapMembers = new HashSet<string> {
        "tactical", "layersByName", "layersById", "layersList", "layerVisible", "languageInstance", "languageDictionary", "dictionarySet", "layerCtor", "entryCtor",
        "parentMap", "tryToView", "tryToGeo", "rendered", "gameUpdate", "missionElapsed", "mainGameViewModel", "geoLat", "geoLon", "geoHeight", "geoType", "sceneMap", "displayMap",
        "battleActive", "battlePlan", "campaignSim", "forState", "galeRadius", "systemDies", "planEngagement", "simState" };
    static void Run(Assembly rt, Assembly dcm, string hormuz, string casesPath, string dir)
    {
        ws = rt.GetType("Sest.RuntimeFixes.WorldStorms", true);
        sidecar = rt.GetType("Sest.RuntimeFixes.StormSidecar", true);
        const string sim = "DynamicCampaignMod.Core.Sim.";
        defType = dcm.GetType("DynamicCampaignMod.Core.Data.CampaignDefinition", true);
        boundsType = dcm.GetType("DynamicCampaignMod.Core.Data.GeoBounds", true);
        modelType = dcm.GetType(sim + "WeatherModel", true);
        theatreType = dcm.GetType(sim + "WeatherTheatre", true);
        geoType = dcm.GetType("DynamicCampaignMod.Core.Geo.GeoPoint", true);

        // 1. The sidecar reader: the committed Hormuz file, then every rejection.
        string error;
        var parse = sidecar.GetMethod("Parse", All);
        var specs = (IList)parse.Invoke(null, new object[] { hormuz, null });
        Check(specs != null && specs.Count == 1, "the runtime reads the committed Hormuz sidecar that tools/make_sest_weather.py wrote");
        object darya = specs[0];
        Check((string)Get(darya, "Id") == "darya" && (string)Get(darya, "Name") == "DARYA" && (string)Get(darya, "Kind") == "Cyclone" &&
              ((IList)Get(darya, "Waypoints")).Count == 10, "Hormuz sidecar: Cyclone DARYA, 10 waypoints");
        string good = "{\"format\":\"sest-weather/1\",\"storms\":[{\"id\":\"t\",\"name\":\"T\",\"kind\":\"Storm\",\"waypoints\":[" +
                      "{\"utc\":\"2028-01-15T00:00:00Z\",\"lat\":24,\"lon\":60,\"wind\":50,\"radius\":300},{\"utc\":\"2028-01-16T00:00:00Z\",\"lat\":25,\"lon\":58,\"wind\":50,\"radius\":300}]}]}";
        var args1 = new object[] { good, null };
        Check(parse.Invoke(null, args1) != null && args1[1] == null, "a minimal sidecar parses");
        foreach (var bad in new[] {
            good.Replace("sest-weather/1", "sest-weather/2"), good.Replace("\"Storm\"", "\"Medicane\""), good.Replace("\"t\",\"name\"", "\"T T\",\"name\""),
            good.Replace("\"lat\":24", "\"lat\":86"), good.Replace("\"wind\":50,\"radius\":300}]", "\"wind\":500,\"radius\":300}]"),
            good.Replace("2028-01-16T00:00:00Z", "2028-01-14T00:00:00Z"), good.Replace("2028-01-16T00:00:00Z", "2028-01-16 00:00"),
            good.Replace("\"radius\":300}]", "\"radius\":300,\"gust\":1}]"), good.Replace("]}]}", "]}],}"), good + "x", good.Replace("\"lat\":24,", "\"lat\":24,\"lat\":24,"),
            good.Replace("\"lat\":24", "\"lat\":NaN"), good.Replace("\"wind\":50", "\"wind\":\"50\""), "[]", "" })
        {
            var a = new object[] { bad, null };
            Check(parse.Invoke(null, a) == null && a[1] is string reason && reason.Length > 0, "a bad sidecar is rejected whole with a reason: " + (bad.Length > 60 ? bad.Substring(0, 60) + "..." : bad));
        }

        // 1b. The shared edge cases: the file's bytes written as the case says,
        //     read back with File.ReadAllText (WorldStorms.Read), then Parse.
        //     tools/tests/test_make_sest_weather.py asserts the same verdicts
        //     through make_sest_weather.check_bytes, so the two agree.
        var json = sidecar.GetNestedType("Json", All);
        var casesDoc = (Dictionary<string, object>)json.GetMethod("Document", All).Invoke(Activator.CreateInstance(json, All, null, new object[] { File.ReadAllText(casesPath) }, null), null);
        var caseList = ((List<object>)casesDoc["cases"]).Cast<Dictionary<string, object>>().ToList();
        Check(caseList.Count >= 60 && caseList.Any(c => (bool)c["accept"]) && caseList.Any(c => !(bool)c["accept"]), "the shared edge-case file holds " + caseList.Count + " cases, both verdicts");
        Directory.CreateDirectory(dir);
        string caseFile = Path.Combine(dir, "case-sest-weather.json");
        foreach (var c in caseList)
        {
            string text = (string)c["text"], enc = (string)c["encoding"];
            byte[] bytes = enc == "hex" ? Enumerable.Range(0, text.Length / 2).Select(i => Convert.ToByte(text.Substring(2 * i, 2), 16)).ToArray()
                : enc == "utf-8-bom" ? new byte[] { 0xEF, 0xBB, 0xBF }.Concat(new System.Text.UTF8Encoding(false).GetBytes(text)).ToArray()
                : enc == "utf-16le-bom" ? new byte[] { 0xFF, 0xFE }.Concat(System.Text.Encoding.Unicode.GetBytes(text)).ToArray()
                : enc == "utf-8" ? new System.Text.UTF8Encoding(false).GetBytes(text) : throw new Exception("case encoding " + enc);
            File.WriteAllBytes(caseFile, bytes);
            var a = new object[] { File.ReadAllText(caseFile), null };
            bool accepted = parse.Invoke(null, a) != null;
            Check(accepted == (bool)c["accept"], "edge case \"" + c["name"] + "\": the runtime " + (accepted ? "accepts" : "rejects (" + a[1] + ")") +
                  ", the shared file says " + ((bool)c["accept"] ? "accept" : "reject"));
        }

        // 2. BinRange is Build's own: every native active of a real snapshot sits
        //    in exactly the bins the copy computes.
        object defA = Definition(Path.Combine(dir, "hormuz"), hormuz);
        object plain = Untouched(defA, 4242);
        DateTime t0 = Utc("2028-01-16T00:00Z");
        object snap = Snapshot(plain, t0);
        var acts = ((IList)Get(snap, "Actives")).Cast<object>().ToList();
        var cells = (List<int>[])Get(snap, "Bins");
        double lat0 = (double)Get(snap, "BinLat0"), lon0 = (double)Get(snap, "BinLon0");
        int rows = (int)Get(snap, "BinRows"), cols = (int)Get(snap, "BinCols");
        var range = sidecar.GetMethod("BinRange", All);
        Func<double, double, double, HashSet<int>> mine = (lat, lon, reach) =>
        {
            var a = new object[] { lat, lon, reach, lat0, lon0, rows, cols, 0, 0, 0, 0 };
            range.Invoke(null, a);
            var set = new HashSet<int>();
            for (int r = (int)a[7]; r <= (int)a[8]; r++) for (int c = (int)a[9]; c <= (int)a[10]; c++) set.Add(r * cols + c);
            return set;
        };
        Check(acts.Count > 0, "DCM's own model has native systems in the Hormuz snapshot (" + acts.Count + ")");
        for (int k = 0; k < acts.Count; k++)
        {
            object p = Get(acts[k], "Point");
            var expected = new HashSet<int>(Enumerable.Range(0, cells.Length).Where(i => cells[i] != null && cells[i].Contains(k)));
            Check(expected.SetEquals(mine((double)Get(p, "Lat"), (double)Get(p, "Lon"), (double)Get(acts[k], "ReachNm"))),
                  "StormSidecar.BinRange gives Build's bins (asymmetric clamp, no wrap) for native system " + Get(Get(acts[k], "System"), "Id"));
        }

        // 3. Binding: Start binds at once when DCM is loaded; every member.
        ws.GetField("Diagnostics", All).SetValue(null, true);
        Call(ws, "Start", new[] { typeof(Assembly), typeof(bool), typeof(bool) }, null, true, true);
        Check((bool)Get(ws, "bound") && (bool)Get(ws, "installed") && !(bool)Get(ws, "stopped"), "WorldStorms.Start binds and installs on the captured DCM without the native image or GameMain");
        // The map layer's members (WorldStormsMap.cs) are bound by BindMap, section 9.
        foreach (var f in ws.GetFields(All).Where(f => f.IsStatic && (typeof(MemberInfo).IsAssignableFrom(f.FieldType)) && !MapMembers.Contains(f.Name)))
            Check(f.GetValue(null) != null, "bound member is set: " + f.Name);
        Check(Lines("world storms bind: ") >= 60 && Lines(" MISSING") == 0 && Lines("all members of Dynamic Campaign Mod 1.0.0 (6008e9c5) bound") == 1,
              "diagnostics log one bind line per member (" + Lines("world storms bind: ") + "), none missing");
        Check(Lines("world storms installed") == 1 && Lines("diagnostics on") == 1, "one install line");
        var bind = ws.GetMethod("Bind", All);

        // 4. The Hormuz storm in a real model.
        object model = For(defA, 4242);
        Check(Lines("world storms: sidecar " + Path.Combine(dir, "hormuz", "sest-weather.json") + ": sest-darya Cyclone DARYA 2028-01-15 00:00Z to 2028-01-17 18:00Z, peak 90 kn") == 1,
              "the sidecar path found is logged with its storm");
        Check(Lines("1 storm(s) from ") == 1, "the storm is tied to the model once");
        object setObj = ws.GetMethod("SetFor", All).Invoke(null, new[] { defA, model });
        object sys = ((object[])Get(setObj, "Systems"))[0];
        var track = (Array)Get(sys, "Track");
        Check(track.Length == 12 && (double)Get(sys, "LifeHours") == 66 && (DateTime)Get(sys, "Born") == Utc("2028-01-15T00:00Z") &&
              Convert.ToInt32(Get(sys, "Kind")) == 3 && (string)Get(Get(sys, "Basin"), "Word") == "Cyclone" && (string)Get(sys, "Id") == "sest-darya" &&
              (double)Get(sys, "PeakWind") == 90, "WeatherSystem: Tropical, 66 h, ceil(66/6)+1 = 12 six-hourly points, basin word Cyclone, sest- id");
        object at24 = Call(sys, "At", new[] { typeof(DateTime) }, t0);
        Check(Math.Abs((double)Get(at24, "Lat") - 24.2) < 1e-9 && Math.Abs((double)Get(at24, "Lon") - 61.1) < 1e-9 && (double)Get(at24, "Vmax") == 90 &&
              (double)Get(at24, "Outer") == 240 && (double)Get(at24, "R") == 24 && (bool)Get(at24, "Tropical") && (double)Get(at24, "V") > 0 && (double)Get(at24, "U") < 0,
              "DCM's WeatherSystem.At returns the waypoint at a waypoint time, moving north-west, R = radius / 10");
        object mid = Call(sys, "At", new[] { typeof(DateTime) }, Utc("2028-01-15T18:00Z"));
        Check(Math.Abs((double)Get(mid, "Lat") - 22.7) < 1e-9 && Math.Abs((double)Get(mid, "Vmax") - 87.5) < 1e-9, "a 6-hourly point between waypoints is interpolated");

        double eyewall = 24.2 + 24.0 / 60;
        object inside = At(model, eyewall, 61.1, t0), native = At(plain, eyewall, 61.1, t0);
        Check((int)Get(inside, "SeaState") >= 8 && (double)Get(inside, "WindKnots") >= 64 && (bool)Get(inside, "Typhoon"),
              "At() in the eyewall (R north of the centre): sea state " + Get(inside, "SeaState") + ", " + Get(inside, "WindKnots") + " kn, Typhoon");
        Check((string)Get(inside, "StormLabel") == "Cyclone DARYA" && (string)Get(inside, "StormId") == "sest-darya", "and the storm label Cyclone DARYA");
        Check((string)Get(native, "StormId") != "sest-darya" && (int)Get(native, "SeaState") < (int)Get(inside, "SeaState"), "DCM's own model has no DARYA there");
        object centre = At(model, 24.2, 61.1, t0);
        Check((string)Get(centre, "StormLabel") == "Cyclone DARYA", "the centre itself carries the label (DCM's eye is calm: sea state " + Get(centre, "SeaState") + ")");
        double farLon = 61.1 - 500 / (60 * Math.Cos(24.2 * Math.PI / 180));
        object far = At(model, 24.2, farLon, t0), farNative = At(plain, 24.2, farLon, t0);
        Check((string)Get(far, "StormId") != "sest-darya" && Sample(far) == Sample(farNative) && (int)Get(far, "SeaState") < (int)Get(inside, "SeaState"),
              "500 nm west: no storm, exactly DCM's own sample (sea state " + Get(far, "SeaState") + ")");
        if (Environment.GetEnvironmentVariable("SEST_STORMS_LOG") == "1")
            foreach (var d in new[] { 0.0, 12, 24, 35, 50, 75, 100, 150, 200, 250, 300 })
                Console.WriteLine("profile DARYA 2028-01-16 00Z, " + d + " nm N/E/S/W: " + string.Join("  ", new[] { (d, 0.0), (0.0, d), (-d, 0.0), (0.0, -d) }.Select(o =>
                {
                    object x = At(model, 24.2 + o.Item1 / 60, 61.1 + o.Item2 / (60 * Math.Cos(24.2 * Math.PI / 180)), t0);
                    return "SS" + Get(x, "SeaState") + " " + ((double)Get(x, "WindKnots")).ToString("0") + "kn" + ((string)Get(x, "StormId") == "sest-darya" ? " L" : "");
                })));
        object battle = Call(model, "Battle", new[] { geoType, typeof(DateTime) }, Geo(eyewall, 61.1), t0);
        Check((string)Get(battle, "Storm") == "Cyclone DARYA" && (int)Get(battle, "SeaState") >= 8 && (bool)Get(battle, "Typhoon"),
              "Battle() (what battle_{id}.ini [Environment] is written from) carries the storm: SeaState=" + Get(battle, "SeaState") + " Weather=" + Prop(battle, "Special"));

        object report = Report(model, t0, "sest-darya");
        Check(report != null && (string)Get(report, "Name") == "DARYA" && Convert.ToInt32(Get(report, "Kind")) == 0, "the storm list has DARYA as a tropical storm");
        var past = ((IEnumerable)Prop(report, "Past")).Cast<object>().ToList();
        var forecast = ((IEnumerable)Prop(report, "Forecast")).Cast<object>().ToList();
        object now = Get(report, "Now");
        Check(past.Count >= 4 && forecast.Count == 1 && (double)Get(forecast[0], "ConeNm") == 80,
              "past track (" + past.Count + " points); DCM forecasts every 24 h only while the storm lives (Dies 17th 18Z: one point, cone 25+55 nm)");
        var early = ((IEnumerable)Prop(Report(model, Utc("2028-01-15T00:00Z"), "sest-darya"), "Forecast")).Cast<object>().Select(f => (double)Get(f, "ConeNm")).ToList();
        Check(early.SequenceEqual(new[] { 80.0, 135.0 }), "at Born: 24 and 48 h forecast points, cone 80 and 135 nm");
        Check(((string)Get(now, "Category")).StartsWith("Cyclone (category 2)") && (string)Get(now, "Label") == "Cyclone DARYA" && Math.Abs((double)Get(now, "WindKn") - 90) < 1e-9,
              "storm card: " + Get(now, "Category") + ", label " + Get(now, "Label") + ", " + Get(now, "WindKn") + " kn");
        Check(Report(plain, t0, "sest-darya") == null, "DCM's own model lists no DARYA");

        // Snapshot bins of the injected storm, and its life.
        object s2 = Snapshot(model, t0);
        var acts2 = ((IList)Get(s2, "Actives")).Cast<object>().ToList();
        int idx = acts2.FindIndex(a => (string)Get(Get(a, "System"), "Id") == "sest-darya");
        var cells2 = (List<int>[])Get(s2, "Bins");
        Check(idx == acts2.Count - 1 && acts2.Count == acts.Count + 1, "Build adds DARYA after DCM's own systems, which are unchanged in number");
        var got = new HashSet<int>(Enumerable.Range(0, cells2.Length).Where(i => cells2[i] != null && cells2[i].Contains(idx)));
        Check(got.SetEquals(mine(24.2, 61.1, 240)) && got.Count > 0, "DARYA is in exactly Build's bins for its reach (" + got.Count + " bins)");
        Check((string)Get(acts2[idx], "Label") == "Cyclone DARYA" && (double)Get(acts2[idx], "ReachNm") == 240, "Active label and reach as Build sets them");
        foreach (var off in new[] { "2028-01-14T23:00Z", "2028-01-17T19:00Z" })
            Check((string)Get(At(model, 21.0, 63.0, Utc(off)), "StormId") != "sest-darya" && Report(model, Utc(off), "sest-darya") == null, "no DARYA outside Born..Dies: " + off);
        Check(Report(model, Utc("2028-01-15T00:00Z"), "sest-darya") != null && Report(model, Utc("2028-01-17T18:00Z"), "sest-darya") != null, "DARYA at Born and at Dies (Build's inclusive test)");

        // 5. Diagnostics: one line per storm per campaign hour; battle [Environment].
        At(model, 23.0, 60.0, t0.AddMinutes(20)); At(model, 23.0, 60.0, t0.AddMinutes(40));
        Check(Lines("world storms: 2028-01-16 00:00Z sest-darya \"Cyclone DARYA\" at 24.20N 61.10E, 90 kn, reach 240 nm, ") == 1, "the injected storm is logged once for the hour 00Z");
        At(model, 23.0, 60.0, t0.AddMinutes(70));
        Check(Lines("world storms: 2028-01-16 01:00Z sest-darya") == 1, "and once for the next hour");
        object engagement = Activator.CreateInstance(dcm.GetType("DynamicCampaignMod.Core.State.Engagement", true), true);
        Set(engagement, "Id", 7); Set(engagement, "Point", Geo(eyewall, 61.1)); Set(engagement, "At", t0);
        ws.GetMethod("AfterWeatherOf", All).Invoke(null, new[] { engagement, battle });
        ws.GetMethod("AfterWeatherOf", All).Invoke(null, new[] { engagement, battle });
        Check(Lines("world storms: contact 7 at 24.60N 61.10E 2028-01-16 00:00Z battle [Environment]: SeaState=" + Get(battle, "SeaState")) == 1 && Lines("Storm=Cyclone DARYA)") == 1,
              "the contact's battle [Environment] is logged once while it is unchanged");

        // 6. Scope: a campaign without a sidecar that reuses the same model
        //    (same theatre, seed, bounds) loses the storm, and gets it back.
        object defB = Definition(Path.Combine(dir, "plain"), null);
        object same = For(defB, 4242);
        Check(ReferenceEquals(same, model), "DCM shares one model per theatre, seed and bounds");
        Check((string)Get(At(same, eyewall, 61.1, t0), "StormId") != "sest-darya" && Report(same, t0, "sest-darya") == null && Lines("placed storms removed from it") == 1,
              "a campaign without the sidecar on that model sees no storm (cached snapshots cleared)");
        Check(Sample(At(same, eyewall, 61.1, t0)) == Sample(native), "and exactly DCM's own weather");
        For(defA, 4242);
        Check((string)Get(At(model, eyewall, 61.1, t0), "StormId") == "sest-darya" && Lines("1 storm(s) from ") == 2, "back in the Hormuz campaign the storm returns");
        object other = For(defB, 999), otherPlain = Untouched(defB, 999);
        foreach (var p in new[] { (24.6, 61.1), (26.0, 56.7), (22.4, 61.8), (27.9, 50.3), (30.0, 64.0) })
            Check(Sample(At(other, p.Item1, p.Item2, t0)) == Sample(At(otherPlain, p.Item1, p.Item2, t0)) && Report(other, t0, "sest-darya") == null,
                  "a model without a sidecar is unchanged at " + p.Item1 + "N " + p.Item2 + "E");

        // 6b. The stale-cache guard. A snapshot built under the old storm set
        //     and stored after a re-tie cleared the cache (DCM's SnapshotAt
        //     stores outside its _lock) is dropped by the SnapshotAt postfix;
        //     the same for a grid. With no re-tie in between, both are kept.
        var before = ws.GetMethod("BeforeCache", All);
        var afterSnap = ws.GetMethod("AfterSnapshotAt", All);
        var afterGrid = ws.GetMethod("AfterGrid", All);
        Func<object, int> generation = m => { var a = new object[] { m, 0 }; before.Invoke(null, a); return (int)a[1]; };
        var cache = (IDictionary)Get(model, "_snapshots");
        var order = (Queue<long>)Get(model, "_snapshotOrder");
        int g1 = generation(model);
        Check(g1 > 0 && g1 == (int)Call(ws, "GenerationOf", new[] { typeof(object) }, model), "a tied model has a tie generation (" + g1 + ")");
        DateTime t5 = Utc("2028-01-16T05:00Z");
        object stale = Snapshot(model, t5);
        Check(((IList)Get(stale, "Actives")).Cast<object>().Any(a => (string)Get(Get(a, "System"), "Id") == "sest-darya"), "a snapshot built under the Hormuz tie holds DARYA");
        For(defB, 4242);
        int g2 = generation(model);
        Check(g2 != g1, "a re-tie to a campaign without storms changes the generation (" + g1 + " -> " + g2 + ")");
        cache[t5.Ticks] = stale; order.Enqueue(t5.Ticks);
        afterSnap.Invoke(null, new[] { model, stale, (object)g1 });
        Check(!cache.Contains(t5.Ticks) && !order.Contains(t5.Ticks) && Lines("a snapshot built while the model's storms changed was not kept") == 1,
              "the old-set snapshot stored after the clear is dropped from _snapshots and _snapshotOrder");
        Check((string)Get(At(model, eyewall, 61.1, t5), "StormId") != "sest-darya", "so the hour is rebuilt without DARYA");
        object kept = Snapshot(model, t5.AddHours(1));
        cache[t5.AddHours(1).Ticks] = kept; order.Enqueue(t5.AddHours(1).Ticks);
        afterSnap.Invoke(null, new[] { model, kept, (object)g2 });
        Check(cache.Contains(t5.AddHours(1).Ticks), "a snapshot whose generation did not change is kept");
        object area = Bounds();
        object grid = Call(model, "Grid", new[] { boundsType, typeof(double), typeof(DateTime) }, area, 2.0, t5);
        var grids = (IList)Get(model, "_grids");
        Check(grids.Contains(grid), "DCM keeps a grid it builds");
        afterGrid.Invoke(null, new[] { model, grid, (object)g2 });
        Check(grids.Contains(grid), "a grid built without a re-tie is kept");
        afterGrid.Invoke(null, new[] { model, grid, (object)(g2 - 1) });
        Check(!grids.Contains(grid) && Lines("a weather grid built while the model's storms changed was not kept") == 1, "a grid built across a re-tie is dropped");
        For(defA, 4242);
        Check(generation(model) != g2 && (string)Get(At(model, eyewall, 61.1, t0), "StormId") == "sest-darya", "re-tied to Hormuz: a new generation and DARYA again");

        // 6c. An unreadable sidecar (here a path DCM could never open: an
        //     illegal character) skips that campaign only, is logged, is not
        //     remembered (a later For tries again) and stops nothing.
        object defBad = Definition(Path.Combine(dir, "bad"), hormuz);
        Set(defBad, "FilePath", dir + "/bad\0x/campaign.json");
        object badModel = For(defBad, 31337);
        Check(Lines(" unreadable (ArgumentException") == 1 && Lines("no storms placed for this campaign, other campaigns unaffected") == 1 && !(bool)Get(ws, "stopped"),
              "an unreadable sidecar is logged once for that campaign and the feature keeps running");
        For(defBad, 31337);
        Check(Lines(" unreadable (ArgumentException") == 2, "and it is read again on the next For (not remembered)");
        Check(Report(badModel, t0, "sest-darya") == null && (string)Get(At(model, eyewall, 61.1, t0), "StormId") == "sest-darya", "no storm there; Hormuz still has DARYA");

        // 7. A Typhoon word, a 10-day life (past Build's 7-day DaySystems window)
        //    and an extratropical Storm.
        string longer = "{\"format\":\"sest-weather/1\",\"storms\":[" +
            "{\"id\":\"long\",\"name\":\"LONGA\",\"kind\":\"Typhoon\",\"waypoints\":[{\"utc\":\"2028-01-10T00:00:00Z\",\"lat\":22,\"lon\":63,\"wind\":135,\"radius\":300,\"rmw\":15}," +
            "{\"utc\":\"2028-01-20T00:00:00Z\",\"lat\":25,\"lon\":58,\"wind\":120,\"radius\":300,\"rmw\":15}]}," +
            "{\"id\":\"gale\",\"name\":\"GALEA\",\"kind\":\"Storm\",\"waypoints\":[{\"utc\":\"2028-01-18T00:00:00Z\",\"lat\":29,\"lon\":50,\"wind\":55,\"radius\":360}," +
            "{\"utc\":\"2028-01-20T00:00:00Z\",\"lat\":28,\"lon\":54,\"wind\":50,\"radius\":330}]}]}";
        object defC = Definition(Path.Combine(dir, "long"), longer);
        object mc = For(defC, 77);
        DateTime day9 = Utc("2028-01-19T00:00Z");
        object lr = Report(mc, day9, "sest-long"), gr = Report(mc, day9, "sest-gale");
        var longCones = ((IEnumerable)Prop(Report(mc, Utc("2028-01-12T00:00Z"), "sest-long"), "Forecast")).Cast<object>().Select(f => (double)Get(f, "ConeNm")).ToList();
        Check(longCones.SequenceEqual(new[] { 80.0, 135.0, 190.0 }), "a storm with 72 h left gets the 24/48/72 h forecast points and cone 25+55*day nm");
        Check(lr != null && ((string)Get(Get(lr, "Now"), "Category")).StartsWith("Typhoon (category 4)") && (string)Get(Get(lr, "Now"), "Label") == "Typhoon LONGA",
              "9 days after Born the typhoon is still listed: " + (lr == null ? "missing" : Get(Get(lr, "Now"), "Category")));
        Check(gr != null && Convert.ToInt32(Get(gr, "Kind")) == 1 && (string)Get(Get(gr, "Now"), "Label") == "Storm GALEA",
              "an extratropical Storm: Gale kind, label " + (gr == null ? "missing" : Get(Get(gr, "Now"), "Label")));
        object gp = Get(Get(gr, "Now"), "Point");
        double glat = (double)Get(gp, "Lat"), glon = (double)Get(gp, "Lon");
        object gale = At(mc, glat + 115.0 / 60, glon, day9);
        Check((string)Get(gale, "StormId") == "sest-gale" && (int)Get(gale, "SeaState") >= 7, "at its radius of maximum wind (radius / 3) the gale gives sea state " + Get(gale, "SeaState"));

        // 9. The tactical map's Weather layer (WorldStormsMap.cs, StormMapGeometry.cs).
        MapLayer(rt, model, sys, mc);

        // 8. Fail closed: a foreign image is refused and nothing else runs.
        //    Stop also clears every tied model: an hour cached with DARYA
        //    (t0 in the Hormuz model) no longer has it.
        Check((string)Get(At(model, eyewall, 61.1, t0), "StormId") == "sest-darya" && cache.Contains(t0.Ticks), "before the stop, the Hormuz model has DARYA cached at 16 Jan 00Z");
        var probe = new object[] { typeof(object).Assembly };
        Check(!(bool)bind.Invoke(null, probe) && (bool)Get(ws, "stopped") && Lines("world storms unavailable; Dynamic Campaign Mod's own weather retained") == 1,
              "Bind refuses an uninspected image with one log line and stops the feature");
        Check((string)Get(At(model, 21.0, 63.0, Utc("2028-01-15T13:00Z")), "StormId") != "sest-darya", "once stopped, a new snapshot gets no placed storm");
        Check(Lines("placed storms removed from 2 weather model(s); their cached snapshots were cleared") == 1 && (string)Get(At(model, eyewall, 61.1, t0), "StormId") != "sest-darya" && Report(model, t0, "sest-darya") == null &&
              Report(mc, day9, "sest-long") == null, "Stop cleared every tied model: no cached hour keeps a placed storm (no flicker)");
    }

    static void MapLayer(Assembly rt, object model, object sys, object mc)
    {
        var geo = rt.GetType("Sest.RuntimeFixes.StormMapGeometry", true);
        var stormType = rt.GetType("Sest.RuntimeFixes.MapStorm", true);
        Func<string, object[], object> G = (name, a) => Call(geo, name, geo.GetMethods(All).First(m => m.Name == name && m.GetParameters().Length == a.Length).GetParameters().Select(p => p.ParameterType).ToArray(), a);
        Func<double, double, double, double, double> dist = (a, b, c, d) => (double)G("DistanceNm", new object[] { a, b, c, d });

        // Geometry: rings, destinations, labels, time.
        Check(Math.Abs(dist(0, 0, 1, 0) - 60.04) < 0.01, "one degree of latitude is 60 nm (great circle, 3440.065 nm earth)");
        foreach (var r in new[] { 24.0, 160.0, 450.0 })
        {
            var ring = ((IEnumerable)G("Ring", new object[] { 26.0, 56.7, r, 72 })).Cast<double[]>().ToList();
            Check(ring.Count == 73 && ring[0][0] == ring[72][0] && ring[0][1] == ring[72][1] && ring.All(p => Math.Abs(dist(26.0, 56.7, p[0], p[1]) - r) < 1e-6 * r + 1e-6),
                  "a " + r + " nm ring: 72 segments, closed, every point " + r + " nm from the centre");
        }
        var wrap = ((IEnumerable)G("Ring", new object[] { 10.0, 179.5, 120.0, 72 })).Cast<double[]>().ToList();
        Check(wrap.All(p => p[1] > -180 && p[1] <= 180) && wrap.Any(p => p[1] < 0) && wrap.Any(p => p[1] > 0), "a ring across the antimeridian keeps longitudes in (-180, 180]");
        Check((double)G("NormalLon", new object[] { 361.0 }) == 1 && (double)G("NormalLon", new object[] { -190.0 }) == 170 && (double)G("NormalLon", new object[] { 180.0 }) == 180, "longitudes are normalised");
        Check(string.Join(" ", new[] { 1.0, 3, 6, 12 }.Select(h => (string)G("LeadText", new object[] { h }))) == "+1 h +3 h +6 h +12 h", "forecast labels read +1 h, +3 h, +6 h, +12 h");
        Check(string.Join(",", new[] { 20.0, 34, 50, 64, 100 }.Select(w => G("Severity", new object[] { w }).ToString())) == "0,1,2,3,4", "ring colour classes: below gale, gale, storm, hurricane force, major");
        Check((DateTime)G("BattleUtc", new object[] { Utc("2028-01-16T12:00Z"), 4.5 * 3600 }) == Utc("2028-01-16T16:30Z") &&
              (DateTime)G("Hour", new object[] { Utc("2028-01-16T16:30Z") }) == Utc("2028-01-16T16:00Z"), "battle UTC = Engagement.At + missionElapsedTime; snapshots by whole hour");
        Check((string)G("Compass", new object[] { 328.0 }) == "NW" && (string)G("Compass", new object[] { 10.0 }) == "N" && (string)G("Compass", new object[] { 100.0 }) == "E", "compass points");

        // Path data with a stand-in projection (x = 10 lon, y = -10 lat).
        var project = Delegate.CreateDelegate(geo.GetNestedType("Project", All), typeof(WorldStormsTests).GetMethod(nameof(FlatProject), All));
        var sb = new System.Text.StringBuilder();
        var square = new List<double[]> { new[] { 0.0, 0.0 }, new[] { 0.0, 1.0 }, new[] { 1.0, 1.0 }, new[] { 0.0, 0.0 } };
        Call(geo, "AppendPolyline", new[] { typeof(System.Text.StringBuilder), typeof(IList<double[]>), project.GetType(), typeof(double), typeof(bool) }, sb, square, project, 1000.0, true);
        Check(sb.ToString() == "M 0,0 L 10,0 L 10,-10 L 0,0 Z", "a polyline becomes path data in view units: " + sb);
        sb.Clear();
        var gap = new List<double[]> { new[] { 0.0, 0.0 }, new[] { 0.0, 1.0 }, new[] { 89.0, 2.0 }, new[] { 0.0, 3.0 }, new[] { 0.0, 4.0 } };
        Call(geo, "AppendPolyline", new[] { typeof(System.Text.StringBuilder), typeof(IList<double[]>), project.GetType(), typeof(double), typeof(bool) }, sb, gap, project, 1000.0, true);
        Check(sb.ToString() == "M 0,0 L 10,0 M 30,0 L 40,0", "a point the map cannot show (far side) breaks the line and leaves the ring open: " + sb);
        sb.Clear();
        var seam = new List<double[]> { new[] { 0.0, 179.0 }, new[] { 0.0, -179.0 } };
        Call(geo, "AppendPolyline", new[] { typeof(System.Text.StringBuilder), typeof(IList<double[]>), project.GetType(), typeof(double), typeof(bool) }, sb, seam, project, 100.0, false);
        Check(sb.ToString() == "M 1790,0 M -1790,0", "a jump across the map (a wrap) starts a new figure: " + sb);

        // The storms the layer collects from a real model, at the Group B pass.
        Check((bool)Call(ws, "BindMap", new[] { typeof(Assembly) }, game) && (bool)Get(ws, "mapBound") && !(bool)Get(ws, "mapStopped"),
              "the map layer binds every member it uses in Sea Power 0.9.3 (Seapower-Scripts aae79728) and Dynamic Campaign Mod 1.0.0");
        foreach (var name in MapMembers) Check(Get(ws, name) != null, "map layer member bound: " + name);
        foreach (var f in ws.GetFields(All).Where(f => f.IsStatic && (typeof(MemberInfo).IsAssignableFrom(f.FieldType))))
            Check(f.GetValue(null) != null, "after BindMap every bound member is set: " + f.Name);
        var ctor = (ConstructorInfo)Get(ws, "layerCtor");
        Check(ctor.DeclaringType.FullName == "SeapowerUI.MapLayer" && string.Join(", ", ctor.GetParameters().Select(p => p.ParameterType.Name)) == "MapDisplayState, Entry&, Boolean" && ctor.IsAssembly,
              "the Layers menu entry is made with MapLayer's internal .ctor(MapDisplayState, in Entry, bool), the one Topographic Map 1.7.0 uses");
        Check(((MethodInfo)Get(ws, "rendered")).DeclaringType.FullName == "MapControl.RenderedLayer" && ((MethodInfo)Get(ws, "tryToView")).GetParameters()[1].ParameterType.GetElementType().FullName == "Noesis.Point",
              "redraws follow RenderedLayer.OnRender (as Topographic Map), geo to view through MapBase.TryLocationToView(GeoPosition, out Point)");
        Check(Lines("world storms map bind: all members") == 1, "one bind line");

        DateTime tb = Utc("2028-01-16T16:20Z");
        var collect = ws.GetMethod("Collect", All);
        var storms = ((IEnumerable)collect.Invoke(null, new object[] { model, tb, 26.0, 56.7 })).Cast<object>().ToList();
        object d = storms.FirstOrDefault(s => (string)Get(s, "Id") == "sest-darya");
        Check(d != null && (bool)Get(d, "Placed") && (bool)Get(d, "Tropical") && (string)Get(d, "Label") == "Cyclone DARYA", "the layer collects DARYA from the model at the Group B pass (16 Jan 16:20Z)");
        object p16 = Call(sys, "At", new[] { typeof(DateTime) }, tb);
        Check(Math.Abs((double)Get(d, "Lat") - (double)Get(p16, "Lat")) < 1e-9 && Math.Abs((double)Get(d, "Lon") - (double)Get(p16, "Lon")) < 1e-9 && Math.Abs((double)Get(d, "WindKn") - (double)Get(p16, "Vmax")) < 1e-9,
              "at exactly DCM's own WeatherSystem.At position and wind for the battle time");
        double gale = (double)Call(modelType, "GaleRadiusNm", new[] { sys.GetType(), p16.GetType() }, sys, p16);
        Check(gale > 0 && (double)Get(d, "GaleNm") == gale && (double)Get(d, "CoreNm") == (double)Get(p16, "R") && Math.Abs((double)Get(d, "ReachNm") - (215 + (200 - 215) * (4 + 20 / 60.0) / 6)) < 1e-6,
              "rings: DCM's GaleRadiusNm (" + Math.Round(gale) + " nm) and the core R (" + Math.Round((double)Get(d, "CoreNm")) + " nm); reach " + Math.Round((double)Get(d, "ReachNm")) + " nm");
        double off = dist((double)Get(d, "Lat"), (double)Get(d, "Lon"), 26.0, 56.7);
        Check(off > 20 && off < 30, "about 20 nm from Group B (" + Math.Round(off) + " nm), as README-TESTS.txt says");
        var leads = ((IEnumerable)Get(d, "Leads")).Cast<object>().ToList();
        Check(leads.Select(l => (double)Get(l, "Hours")).SequenceEqual(new[] { 1.0, 3, 6, 12 }), "forecast points +1, +3, +6 and +12 h");
        foreach (var l in leads)
        {
            object q = Call(sys, "At", new[] { typeof(DateTime) }, tb.AddHours((double)Get(l, "Hours")));
            Check(Math.Abs((double)Get(l, "Lat") - (double)Get(q, "Lat")) < 1e-9 && Math.Abs((double)Get(l, "Lon") - (double)Get(q, "Lon")) < 1e-9,
                  "forecast +" + Get(l, "Hours") + " h is DCM's track at that time");
        }
        var late = ((IEnumerable)collect.Invoke(null, new object[] { model, Utc("2028-01-17T10:00Z"), 26.0, 56.7 })).Cast<object>().First(s => (string)Get(s, "Id") == "sest-darya");
        Check(((IEnumerable)Get(late, "Leads")).Cast<object>().Select(l => (double)Get(l, "Hours")).SequenceEqual(new[] { 1.0, 3, 6 }), "no forecast point after the storm dies (17 Jan 18Z): +1, +3, +6 h only at 10Z");
        Check(((IEnumerable)collect.Invoke(null, new object[] { model, Utc("2028-01-17T19:00Z"), 26.0, 56.7 })).Cast<object>().All(s => (string)Get(s, "Id") != "sest-darya"), "and no DARYA after it dies");
        Check(((IEnumerable)collect.Invoke(null, new object[] { model, tb, -40.0, -120.0 })).Cast<object>().All(s => (string)Get(s, "Id") != "sest-darya"), "a battle 1500+ nm away does not draw it");
        Check(((IDictionary)Get(model, "_snapshots")).Contains(Utc("2028-01-16T16:00Z").Ticks) && !((IDictionary)Get(model, "_snapshots")).Contains(tb.Ticks),
              "the layer reads the snapshot of the whole battle hour (16Z), not one per battle minute");
        string centre = (string)G("CentreText", new[] { d }), rings = (string)G("RingText", new[] { d }), motion = (string)G("MotionText", new[] { d });
        Check(centre == "Cyclone DARYA " + Math.Round((double)Get(d, "WindKn")) + " kn" && rings == "gale " + Math.Round(gale) + " nm, core " + Math.Round((double)Get(d, "CoreNm")) + " nm" &&
              motion.StartsWith("moving NW "), "labels: \"" + centre + "\", \"" + rings + "\", \"" + motion + "\"");
        var list = (IList)Activator.CreateInstance(typeof(List<>).MakeGenericType(stormType));
        list.Add(d);
        double hLat, hLon;
        var dest = new object[] { (double)Get(d, "Lat"), (double)Get(d, "Lon"), 0.0, 50.0, 0.0, 0.0 };
        geo.GetMethod("Destination", All).Invoke(null, dest);
        hLat = (double)dest[4]; hLon = (double)dest[5];
        string hover = (string)G("Hover", new object[] { list, hLat, hLon });
        Check(hover != null && hover.StartsWith("Cyclone DARYA ") && hover.Contains("50 nm from the centre, inside the gale ring"), "hover 50 nm north of the centre: " + (hover ?? "null").Replace("\n", " | "));
        Check(G("Hover", new object[] { list, 10.0, 80.0 }) == null, "no readout far outside the storm");
        // DCM's own storms are drawn too: the 10-day Typhoon LONGA and the
        // Storm GALEA of section 7 come back from that model as any storm would.
        var other = ((IEnumerable)collect.Invoke(null, new object[] { mc, Utc("2028-01-19T00:00Z"), 26.0, 56.0 })).Cast<object>().Select(s => (string)Get(s, "Label")).ToList();
        Check(other.Contains("Typhoon LONGA") && other.Contains("Storm GALEA"), "a typhoon and an extratropical storm are both collected: " + string.Join(", ", other));
    }

    static bool FlatProject(double lat, double lon, out double x, out double y)
    {
        x = 10 * lon; y = -10 * lat;
        return lat < 80;
    }
}
