using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using Mono.Cecil;

static class WorldOperationsTests
{
    const BindingFlags All = BindingFlags.Instance | BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic;
    static int checks;
    static Type ledger, entry;
    static void Check(bool ok, string why) { checks++; if (!ok) throw new Exception(why); }
    static object Call(object value, string method, params object[] args) => (value as Type ?? value.GetType()).GetMethod(method, All).Invoke(value is Type ? null : value, args);
    static object Field(object value, string field) => value.GetType().GetField(field, All).GetValue(value);
    static void Set(object value, string field, object data) => value.GetType().GetField(field, All).SetValue(value, data);
    static object Open(string path) => Activator.CreateInstance(ledger, All, null, new object[] { path }, null);
    static IList Events(string scope, int start, int count, bool manual = true, string theatre = "")
    {
        var list = (IList)Activator.CreateInstance(typeof(List<>).MakeGenericType(entry));
        for (int i = start; i < start + count; i++)
        {
            object e = Activator.CreateInstance(entry, true);
            Set(e, "Scope", scope); Set(e, "Key", scope + ":battle:" + i);
            Set(e, "At", new DateTime(2028, 10, 1).AddHours(i).Ticks);
            Set(e, "Where", "Test battle " + i); Set(e, "Theatre", theatre); Set(e, "Manual", manual);
            list.Add(e);
        }
        return list;
    }
    static List<object> Ribbons(object store, string scope) => ((IEnumerable)Call(store, "Ribbons", scope)).Cast<object>().ToList();
    static int Progress(object store, string scope, string id) => (int)Field(Ribbons(store, scope).Single(x => (string)Field(x, "Id") == id), "Progress");

    static void Main(string[] args)
    {
        string refs = Path.GetFullPath(args[0]), runtime = Path.GetFullPath(args[1]), workshop = Path.GetFullPath(args[2]);
        AppDomain.CurrentDomain.AssemblyResolve += (s, e) => { string p = Path.Combine(refs, new AssemblyName(e.Name).Name + ".dll"); return File.Exists(p) ? Assembly.LoadFrom(p) : null; };
        var rt = Assembly.LoadFrom(runtime);
        ledger = rt.GetType("Sest.RuntimeFixes.WorldServiceLedger", true);
        entry = ledger.GetNestedType("Entry", All);
        string dir = Path.Combine(Path.GetTempPath(), "SEST-World-Test-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(dir);
        try
        {
            string path = Path.Combine(dir, "service.txt"), scope = "sest.world_sandbox_2028.regional:blue";
            object store = Open(path);
            Check(Progress(store, scope, "meridian") == 0, "Empty record has no fictional service progress");
            Call(store, "Merge", Events(scope, 0, 3, true, "europe"));
            byte[] first = File.ReadAllBytes(path);
            Check(Progress(store, scope, "meridian") == 3 && Progress(store, scope, "europe") == 3, "Completed manual reports count towards global and evidenced theatre service");
            Call(store, "Merge", Events(scope, 0, 3, true, "europe"));
            Check(first.SequenceEqual(File.ReadAllBytes(path)), "Reloaded reports are idempotent and do not rewrite unchanged ledger");
            store = Open(path);
            Check(Progress(store, scope, "meridian") == 3, "Service events survive process restart");
            Call(store, "Merge", Events(scope, 3, 9, false, "europe"));
            Check(Progress(store, scope, "meridian") == 3, "Auto-resolves never earn manual-command service");
            Call(store, "Merge", Events("other:red", 0, 20, true, "europe"));
            Check(Progress(store, scope, "meridian") == 3, "Other coalition/campaign service is separate");
            Call(store, "Merge", Events(scope, 30, 7));
            Check(Progress(store, scope, "iron-meridian") == 10 && Progress(store, scope, "europe") == 3, "Missing positions count globally without inventing theatre evidence");
            Check(Ribbons(store, scope).All(x => ((string[])Field(x, "Colours")).All(c => c.Length == 7 && c[0] == '#')), "Every ribbon has declared stripe colours");
            Check((string)Call(ledger, "Theatre", 35d, 380d) == "europe", "Unwrapped east longitude normalises for service evidence");
            Check((string)Call(ledger, "Theatre", 15d, 190d) == "pacific", "Dateline battle belongs to Pacific evidence region");
            Check((string)Call(ledger, "Theatre", double.NaN, 10d) == "", "Invalid coordinates cannot earn theatre service");
            string future = Path.Combine(dir, "future.txt"); File.WriteAllText(future, "SEST-WORLD-SERVICE-999\nkeep this");
            byte[] preserved = File.ReadAllBytes(future); object unknown = Open(future);
            Check((bool)ledger.GetProperty("ReadOnly", All).GetValue(unknown, null), "Unknown schema enters read-only mode");
            Call(unknown, "Merge", Events(scope, 0, 1));
            Check(preserved.SequenceEqual(File.ReadAllBytes(future)), "Unknown-format record is preserved byte for byte");
            Check(!Directory.EnumerateFiles(dir, "*.tmp").Any(), "Atomic updates leave no temporary files");

            var recordType = rt.GetType("Sest.RuntimeFixes.CombatGameRecord", true);
            var historyRows = (IList)Activator.CreateInstance(typeof(List<>).MakeGenericType(recordType));
            long eventAt = new DateTime(2028, 10, 1).Ticks;
            for (int i = 0; i < 3; i++)
            {
                object row = Activator.CreateInstance(recordType, true);
                Set(row, "Id", "record" + i); Set(row, "Source", "DCM:" + scope + ":" + eventAt);
                Set(row, "MissionIndex", i == 2 ? 99 : 0); Set(row, "EndedUtc", (long)i);
                historyRows.Add(row);
            }
            var evidence = Events(scope, 0, 1);
            Set(evidence[0], "Key", scope + ":0:" + eventAt);
            var selected = (IList)Call(rt.GetType("Sest.RuntimeFixes.WorldOperations", true), "RecordedGames", historyRows, evidence, scope);
            Check(selected.Count == 1 && (string)Field(selected[0], "Id") == "record1", "World costs select the latest replay with an actual matching completed report");
            Set(evidence[0], "Manual", false);
            Check(((IList)Call(rt.GetType("Sest.RuntimeFixes.WorldOperations", true), "RecordedGames", historyRows, evidence, scope)).Count == 0, "Auto-resolves do not acquire invented itemised cost history");

            var vm = Activator.CreateInstance(rt.GetType("Sest.RuntimeFixes.CumulativeCombatCostsViewModel", true));
            var view = Activator.CreateInstance(rt.GetType("Sest.RuntimeFixes.CampaignCosts+CostView", true), true);
            Set(view, "Title", "WORLD CAMPAIGN OPERATIONS"); Set(view, "Subtitle", "Campaign test"); Set(view, "World", true);
            Call(vm, "Set", view, true);
            Check((string)vm.GetType().GetProperty("Title").GetValue(vm, null) == "WORLD CAMPAIGN OPERATIONS", "Operations window has its own native title");
            Set(view, "Title", null); Set(view, "Subtitle", null); Set(view, "World", false); Call(vm, "Set", view, true);
            Check((string)vm.GetType().GetProperty("Title").GetValue(vm, null) == "CUMULATIVE COMBAT COSTS", "Normal mission costs retain their title");

            string dcmPath = Path.Combine(workshop, "3813157776", "DynamicCampaignMod.dll");
            var dcm = Assembly.LoadFrom(dcmPath);
            Call(rt.GetType("Sest.RuntimeFixes.WorldOperations", true), "Bind");
            var world = rt.GetType("Sest.RuntimeFixes.WorldOperations", true);
            var sessionType = dcm.GetType("DynamicCampaignMod.Game.Session.CampaignSession", true);
            var battleType = dcm.GetType("DynamicCampaignMod.Game.Battle.BattleSession", true);
            Check(battleType.GetField("Plan", All) == null && battleType.GetProperty("Plan", All) != null, "Captured battle plan is a property, not a field");
            object sim = System.Runtime.Serialization.FormatterServices.GetUninitializedObject(dcm.GetType("DynamicCampaignMod.Core.Sim.CampaignSim", true));
            object fakeState = System.Runtime.Serialization.FormatterServices.GetUninitializedObject(dcm.GetType("DynamicCampaignMod.Core.State.CampaignState", true));
            object def = System.Runtime.Serialization.FormatterServices.GetUninitializedObject(dcm.GetType("DynamicCampaignMod.Core.Data.CampaignDefinition", true));
            object plan = System.Runtime.Serialization.FormatterServices.GetUninitializedObject(dcm.GetType("DynamicCampaignMod.Core.State.BattlePlan", true));
            object engagement = System.Runtime.Serialization.FormatterServices.GetUninitializedObject(dcm.GetType("DynamicCampaignMod.Core.State.Engagement", true));
            Set(sim, "State", fakeState); Set(plan, "Engagement", engagement); Set(engagement, "Id", 1559); Set(engagement, "At", new DateTime(2028, 10, 1));
            sessionType.GetProperty("Sim", All).GetSetMethod(true).Invoke(null, new[] { sim });
            sessionType.GetField("_definition", All).SetValue(null, def);
            sessionType.GetProperty("Active", All).GetSetMethod(true).Invoke(null, new object[] { true });
            Check((bool)Call(world, "ReadContext") && (bool)world.GetProperty("StrategicActive", All).GetValue(null, null), "Real captured session getters expose the strategic context");
            sessionType.GetProperty("Active", All).GetSetMethod(true).Invoke(null, new object[] { false });
            battleType.GetProperty("Plan", All).GetSetMethod(true).Invoke(null, new[] { plan });
            Check((bool)Call(world, "ReadContext") && !(bool)world.GetProperty("StrategicActive", All).GetValue(null, null), "Battle context survives the author closing the strategic scene");
            world.GetField("scope", All).SetValue(null, scope);
            object stamped = Activator.CreateInstance(recordType, true); Call(world, "Stamp", stamped);
            Check((int)Field(stamped, "MissionIndex") == 1559 && ((string)Field(stamped, "Source")).StartsWith("DCM:" + scope + ":"), "Live battle costs are stamped through the actual Plan property");
            battleType.GetProperty("Plan", All).GetSetMethod(true).Invoke(null, new object[] { null });
            Check((bool)Call(world, "ReadContext") && !(bool)world.GetProperty("StrategicActive", All).GetValue(null, null), "Completed-battle evidence survives the gap before the strategy scene reloads");
            sessionType.GetProperty("Active", All).GetSetMethod(true).Invoke(null, new object[] { true });
            Check((bool)Call(world, "ReadContext") && (bool)world.GetProperty("StrategicActive", All).GetValue(null, null), "Returning to the world map restores Operations context");
            sessionType.GetProperty("Active", All).GetSetMethod(true).Invoke(null, new object[] { false });
            sessionType.GetProperty("Sim", All).GetSetMethod(true).Invoke(null, new object[] { null });
            sessionType.GetField("_definition", All).SetValue(null, null);
            Check(!(bool)Call(world, "ReadContext"), "Campaign teardown releases the retained context");
            foreach (var spec in new[] {
                Tuple.Create("Core.State.CampaignState", "Now,PlayerSideId,Points,Renown,Ranks,Reports,BaseOwner,TaskForces,Squadrons,BuildOrders,AdmiraltyOrders,Operations"),
                Tuple.Create("Core.State.BattleReport", "EngagementId,Where,At,AutoResolved,PlayerSideId"),
                Tuple.Create("Core.State.Engagement", "Id,Point,At"),
                Tuple.Create("Core.Geo.GeoPoint", "Lat,Lon"),
                Tuple.Create("Core.State.Hull", "UnitIni,Name,Fuel,Damage"),
                Tuple.Create("Core.State.Squadron", "Name,SideId,BaseId,Airframes"),
                Tuple.Create("Core.State.Airframe", "UnitIni,Status") })
                foreach (var f in spec.Item2.Split(',')) Check(dcm.GetType("DynamicCampaignMod." + spec.Item1, true).GetField(f, All) != null, "Captured world binding resolves: " + spec.Item1 + "." + f);
            var strike = Assembly.LoadFrom(Path.Combine(workshop, "3806686336", "CoordinatedStrikeTool.dll"));
            Call(rt.GetType("Sest.RuntimeFixes.CoordinatedStrikeRefinements", true), "Bind", strike);
            Check(true, "Current strike style, plan and cost bindings resolve without applying GUI hooks");
        }
        finally { Directory.Delete(dir, true); }
        Console.WriteLine("World service, lifecycle, UI model and optional-mod binding checks passed: " + checks);
    }
}
