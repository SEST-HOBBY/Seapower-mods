using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.Serialization;
using System.Security.Cryptography;

// SEST fire missions in the Coordinated Strike panel: the auto-fire, timing
// and over-commitment rules; binding to the real strike tool, Contact Log and
// game images; and mission target handling on the author's own StrikePlan
// objects. No Unity scene, IMGUI drawing or engage order runs here.
// Arguments: <flat references> <SEST.RuntimeFixes.dll> <workshop library>
static class StrikeMissionTests
{
    const BindingFlags All = BindingFlags.Instance | BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic;
    static int checks;
    static void Check(bool ok, string why) { checks++; if (!ok) throw new Exception(why); }
    static object Call(Type type, string name, params object[] args) => type.GetMethod(name, All).Invoke(null, args);
    static string Sha(string path) { using (var sha = SHA256.Create()) using (var s = File.OpenRead(path)) return BitConverter.ToString(sha.ComputeHash(s)).Replace("-", "").ToLowerInvariant(); }

    static int Shots(Type policy, bool armed = true, bool locked = true, bool arming = false, bool alive = true, int status = 0, bool fired = false,
        int salvo = 2, int launched = 0, float launchTime = 100f, float now = 100f, int sent = 0, bool pending = false, float lastAt = float.NegativeInfinity) =>
        (int)Call(policy, "ShotsToOrder", armed, locked, arming, alive, status, fired, salvo, launched, launchTime, now, sent, pending, lastAt);

    static void Main(string[] args)
    {
        string refs = Path.GetFullPath(args[0]), runtime = Path.GetFullPath(args[1]), workshop = Path.GetFullPath(args[2]);
        AppDomain.CurrentDomain.AssemblyResolve += (s, e) => { string p = Path.Combine(refs, new AssemblyName(e.Name).Name + ".dll"); return File.Exists(p) ? Assembly.LoadFrom(p) : null; };
        var rt = Assembly.LoadFrom(runtime);
        Type policy = rt.GetType("Sest.RuntimeFixes.StrikeMissionPolicy", true);
        Type mission = rt.GetType("Sest.RuntimeFixes.StrikeMission", true);

        // Auto-fire: only armed, locked, not arming, target alive, leg Ok and not done.
        Check(Shots(policy) == 2, "A due, locked, in-range leg is ordered with its whole salvo");
        Check(Shots(policy, launched: 1) == 1, "A partly launched leg is ordered only its remaining rounds");
        Check(Shots(policy, armed: false) == 0, "Nothing is ordered while auto-fire is off");
        Check(Shots(policy, locked: false) == 0, "An unlocked plan is never fired");
        Check(Shots(policy, arming: true) == 0, "Nothing fires while the author is still readying launchers");
        Check(Shots(policy, alive: false) == 0, "A lost or destroyed target is not fired at");
        foreach (int status in new[] { 1, 2, 3 }) Check(Shots(policy, status: status) == 0, "A leg that is out of range, too close or has lost its target is held: status " + status);
        Check(Shots(policy, fired: true) == 0 && Shots(policy, launched: 2) == 0, "A completed leg is not fired again");
        Check(Shots(policy, pending: true) == 0, "No second order while the game still holds the first");
        Check(Shots(policy, now: 98.5f) == 0 && Shots(policy, now: 99.0f) == 2, "The order goes out one game second before the launch time, not earlier");
        Check(Shots(policy, now: 145f) == 2 && Shots(policy, now: 145.5f) == 0, "Nothing is ordered more than 45 s after its launch time");
        Check(Shots(policy, sent: 1, lastAt: 100f, now: 110f) == 0 && Shots(policy, sent: 1, lastAt: 100f, now: 115f) == 2, "A vanished order is retried after 15 s");
        Check(Shots(policy, sent: 3, lastAt: 0f, now: 120f) == 0, "At most three orders per leg");

        // One time on target for every target.
        Func<float[], float?, float?> common = (t, r) => (float?)Call(policy, "CommonImpact", (IEnumerable<float>)t, r);
        Check(common(new[] { 300f, 420f, 380f }, null) == 420f, "The common time on target is the latest earliest impact");
        Check(common(new[] { 300f, 420f }, 600f) == 600f, "A later requested time is kept");
        Check(common(new[] { 300f, 420f }, 350f) == 420f, "An earlier requested time cannot be made, so the latest earliest impact is used");
        Check(common(new float[0], null) == null && common(new[] { float.NaN }, null) == null, "No time on target without a timed target");

        // Rounds planned across targets against what each shooter carries.
        var planned = new List<KeyValuePair<string, int>> { new KeyValuePair<string, int>("A|harpoon", 4), new KeyValuePair<string, int>("A|harpoon", 6), new KeyValuePair<string, int>("B|sm2", 2), new KeyValuePair<string, int>("C|nsm", 0) };
        var carried = new Dictionary<string, int> { { "A|harpoon", 8 }, { "B|sm2", 2 }, { "C|nsm", 0 } };
        var over = (List<KeyValuePair<string, int[]>>)Call(policy, "OverCommitted", planned, new Func<string, int>(k => carried[k]));
        Check(over.Count == 1 && over[0].Key == "A|harpoon" && over[0].Value[0] == 10 && over[0].Value[1] == 8, "Ten Harpoons planned across two targets from a ship carrying eight is flagged; exact loads are not");

        // Picker ordering, search and bearings.
        Type sort = policy.GetNestedType("Sort", All);
        Func<string, int, double, string, double, int, double, string, double, int> cmp = (s, ra, ga, na, sa, rb, gb, nb, sb) =>
            (int)Call(policy, "Compare", Enum.Parse(sort, s), ra, ga, na, sa, rb, gb, nb, sb);
        Check(cmp("Threat", 0, 90, "B", 0, 1, 10, "A", 0) < 0, "Threat sort puts hostile tracks before nearer unknown ones");
        Check(cmp("Threat", 0, 20, "B", 0, 0, 40, "A", 0) < 0, "Threat sort then puts the nearer hostile first");
        Check(cmp("Range", 0, double.NaN, "A", 0, 3, 5, "B", 0) > 0, "Tracks without a range sort last by range");
        Check(cmp("Speed", 1, 0, "A", 30, 1, 0, "B", 450) > 0, "Speed sort is fastest first");
        Check(cmp("Name", 0, 0, "alpha", 0, 0, 0, "Bravo", 0) < 0, "Name sort ignores case");
        Func<string, string[], bool> match = (q, f) => (bool)Call(policy, "Matches", q, f);
        Check(match("", new[] { "x" }) && match("udaloy 4", new[] { "#4 Hostile", "Udaloy-class" }) && !match("kirov", new[] { "#4 Hostile", "Udaloy-class" }), "Search needs every word somewhere in the track's text");
        Check((string)Call(policy, "Compass", 359.7) == "000" && (string)Call(policy, "Compass", -90.0) == "270" && (string)Call(policy, "Compass", double.NaN) == "-", "Bearings read 000 to 359");

        // Real images: the pinned strike tool and Contact Log, and the game's engage order.
        string strikePath = Path.Combine(workshop, "3806686336", "CoordinatedStrikeTool.dll");
        string contactPath = Path.Combine(workshop, "3819427362", "ContactLog.dll");
        Check(Sha(strikePath) == "093b8ad6478641948b0eaca720427e5cef3c8b4440142f6c33b16339dc2fc941", "The inspected Coordinated Strike Tool image is the one tested");
        Check(Sha(contactPath) == (string)mission.GetField("ContactLogHash", All).GetValue(null), "The inspected Contact Log image is the one tested");
        var strike = Assembly.LoadFrom(strikePath);
        Call(mission, "Bind", strike);
        Check(true, "Strike panel, plan, leg, picker and native engage-order bindings resolve");
        Call(mission, "BindContactLog", Assembly.LoadFrom(contactPath));
        Check(true, "Contact Log store and record bindings resolve");

        // Mission targets on the author's own objects (no Unity calls).
        Type panelType = strike.GetType("CoordinatedStrikeTool.StrikePanel", true);
        Type planType = strike.GetType("CoordinatedStrikeTool.StrikePlan", true);
        Type legType = strike.GetType("CoordinatedStrikeTool.StrikeLeg", true);
        Type vehicleType = Type.GetType("SeaPower.Vehicle, Seapower-Scripts", true);
        object panel = FormatterServices.GetUninitializedObject(panelType);
        foreach (var f in panelType.GetFields(All).Where(f => f.Name == "_slowHandled" || f.Name == "_cued"))
            f.SetValue(panel, Activator.CreateInstance(f.FieldType));
        object first = Activator.CreateInstance(planType, true);
        panelType.GetField("_plan", All).SetValue(panel, first);
        mission.GetField("panel", All).SetValue(null, panel);
        var plans = (IList)mission.GetField("plans", All).GetValue(null);
        plans.Clear();
        PropertyInfo target = planType.GetProperty("Target", All);
        Func<object, IList> legs = p => (IList)planType.GetField("Legs", All).GetValue(p);
        object a = FormatterServices.GetUninitializedObject(vehicleType), b = FormatterServices.GetUninitializedObject(vehicleType), c = FormatterServices.GetUninitializedObject(vehicleType);

        Check(Call(mission, "AddTarget", a) == first && target.GetValue(first, null) == a && plans.Count == 1, "The first target fills the empty plan on show rather than adding a second plan");
        object leg = Activator.CreateInstance(legType, true);
        legType.GetField("AmmoName", All).SetValue(leg, "usn_rgm-84d");
        legType.GetField("Salvo", All).SetValue(leg, 4);
        legs(first).Add(leg);
        object second = Call(mission, "AddTarget", b);
        Check(second != first && planType.IsInstanceOfType(second) && target.GetValue(second, null) == b && plans.Count == 2, "A further target becomes its own author StrikePlan");
        Check(Call(mission, "AddTarget", b) == second && plans.Count == 2, "Adding a track already in the mission does not duplicate it");
        Check(Call(mission, "PlanFor", c) == null && Call(mission, "PlanFor", a) == first, "Tracks are found by their plotting-table vehicle");
        Call(mission, "CopyShooters", first, second);
        object copy = legs(second).Count == 1 ? legs(second)[0] : null;
        Check(copy != null && copy != leg && (string)legType.GetField("AmmoName", All).GetValue(copy) == "usn_rgm-84d" && (int)legType.GetField("Salvo", All).GetValue(copy) == 4 &&
            (int)legType.GetField("Launched", All).GetValue(copy) == 0, "Copy shooters makes fresh legs with the same weapon and salvo");
        Call(mission, "MakeActive", second);
        Check(panelType.GetField("_plan", All).GetValue(panel) == second, "Edit puts the chosen target's plan in the author's panel");
        Call(mission, "RemovePlan", second);
        Check(plans.Count == 1 && panelType.GetField("_plan", All).GetValue(panel) == first, "Removing the plan on show hands the panel the next target");
        Call(mission, "RemovePlan", first);
        Check(plans.Count == 1, "The last target is never removed; the author's own Reset handles that");
        Call(mission, "AddTarget", c);
        Call(mission, "Clear", "test");
        Check(plans.Count == 1 && plans[0] == first && !(bool)mission.GetField("armed", All).GetValue(null), "Leaving the mission keeps only the author's plan and disarms");

        Console.WriteLine("Strike fire mission checks passed: " + checks);
    }
}
