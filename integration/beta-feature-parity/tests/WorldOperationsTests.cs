using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Xml;
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
            Check(Ribbons(store, scope).Count == 25 && Ribbons(store, scope).Select(x => Field(x, "Id")).Distinct().Count() == 25, "Expanded world catalogue has 25 stable unique awards");
            var thresholds = new Dictionary<string, int> { { "meridian", 3 }, { "iron-meridian", 10 }, { "joint-command", 20 }, { "sustained-command", 50 }, { "operational-watch", 5 }, { "enduring-watch", 15 },
                { "expeditionary-command", 3 }, { "global-command", 6 }, { "admiralty-service", 5 }, { "operational-versatility", 3 }, { "convoy-protection", 3 }, { "surveillance-service", 3 }, { "route-security", 3 },
                { "europe", 2 }, { "europe-veteran", 5 }, { "pacific", 2 }, { "pacific-veteran", 5 } };
            Check(thresholds.All(t => (int)Field(Ribbons(store, scope).Single(x => (string)Field(x, "Id") == t.Key), "Required") == t.Value), "Award thresholds stay as published, including watch, sustained and expeditionary awards");
            var expanded = Open(Path.Combine(dir, "expanded.txt"));
            var activeDays = Events(scope, 100, 20, true, "europe");
            for (int n = 0; n < activeDays.Count; n++) Set(activeDays[n], "At", new DateTime(2028, 10, 1).AddDays(n).Ticks);
            Call(expanded, "Merge", activeDays);
            Check(Progress(expanded, scope, "joint-command") == 20 && Progress(expanded, scope, "enduring-watch") == 20, "Command and watch progress use manual reports and distinct campaign days");
            Check(Progress(expanded, scope, "europe-veteran") == 20, "Theatre veteran retains the original positioned evidence rule");
            var regions = new[] { "middle-east", "africa", "americas", "southern", "pacific" };
            for (int n = 0; n < regions.Length; n++) Call(expanded, "Merge", Events(scope, 200 + n, 1, true, regions[n]));
            Call(expanded, "Merge", Events(scope, 300, 1, true, "unknown-region"));
            Check(Progress(expanded, scope, "global-command") == 6, "Cross-theatre service counts six known regions and ignores unknown labels");

            var recordType = rt.GetType("Sest.RuntimeFixes.CombatGameRecord", true);
            var sideType = rt.GetType("Sest.RuntimeFixes.CombatSideRecord", true);
            var historyRows = (IList)Activator.CreateInstance(typeof(List<>).MakeGenericType(recordType));
            long eventAt = new DateTime(2028, 10, 1).Ticks;
            for (int i = 0; i < 4; i++)
            {
                object row = Activator.CreateInstance(recordType, true);
                Set(row, "Id", "record" + i); Set(row, "Source", "DCM:" + scope + ":" + eventAt);
                Set(row, "MissionIndex", i == 2 ? 99 : 0); Set(row, "EndedUtc", i == 3 ? 5L : (long)i);
                // record3 has the shape of the owner's 9 Nov fragments (cc9b4184,
                // 60f303a1, 8220f559): DCM-stamped, the same engagement, no sides.
                if (i != 3) { object side = Activator.CreateInstance(sideType, true); Set(side, "Name", "Player"); ((IList)Field(row, "Sides")).Add(side); }
                historyRows.Add(row);
            }
            var evidence = Events(scope, 0, 1);
            Set(evidence[0], "Key", scope + ":0:" + eventAt);
            var selected = (IList)Call(rt.GetType("Sest.RuntimeFixes.WorldOperations", true), "RecordedGames", historyRows, evidence, scope);
            Check(selected.Count == 1 && (string)Field(selected[0], "Id") == "record1", "World costs select the latest replay with an actual matching completed report");
            Check(selected.Count == 1 && ((IList)Field(selected[0], "Sides")).Count == 1, "A later empty 0-side fragment cannot replace the attempt with recorded costs");
            Set(evidence[0], "Manual", false);
            Check(((IList)Call(rt.GetType("Sest.RuntimeFixes.WorldOperations", true), "RecordedGames", historyRows, evidence, scope)).Count == 0, "Auto-resolves do not acquire invented itemised cost history");

            var vm = Activator.CreateInstance(rt.GetType("Sest.RuntimeFixes.CumulativeCombatCostsViewModel", true));
            var viewType = rt.GetType("Sest.RuntimeFixes.CampaignCosts+CostView", true);
            object body = Enum.Parse(rt.GetType("Sest.RuntimeFixes.CostLineKind", true), "Body");
            Func<string, string, bool, object> report = (title, subtitle, isWorld) => {
                object page = Activator.CreateInstance(viewType, true);
                Set(page, "Title", title); Set(page, "Subtitle", subtitle); Set(page, "World", isWorld);
                Call(page, "AddDetail", body, "Recorded battle row"); return page;
            };
            Func<int> revision = () => (int)vm.GetType().GetProperty("Revision", All).GetValue(vm, null);
            var view = report("WORLD CAMPAIGN OPERATIONS", "Campaign test | 1 Oct 2028 06:00", true);
            Call(vm, "Set", view, true);
            Check((string)vm.GetType().GetProperty("Title").GetValue(vm, null) == "WORLD CAMPAIGN OPERATIONS", "Operations window has its own native title");
            int shownRevision = revision();
            Call(vm, "Set", view, true);
            Check(revision() == shownRevision, "The same report on the next frame is neither re-joined nor re-rendered");
            Set(view, "Subtitle", "Campaign test | 1 Oct 2028 06:01");
            Call(vm, "Set", view, true);
            Check((string)vm.GetType().GetProperty("Subtitle").GetValue(vm, null) == "Campaign test | 1 Oct 2028 06:01" && revision() == shownRevision, "The campaign clock updates its bound line without rebuilding the report rows");
            Call(vm, "Set", report("WORLD CAMPAIGN OPERATIONS", "Campaign test | 1 Oct 2028 07:00", true), true);
            Check(revision() == shownRevision, "A rebuilt world report with unchanged rows does not rebuild the native panels");
            Call(vm, "Set", report(null, null, false), true);
            Check((string)vm.GetType().GetProperty("Title").GetValue(vm, null) == "CUMULATIVE COMBAT COSTS" && revision() == shownRevision + 1, "Normal mission costs retain their title and a changed report renders once");

            string dcmPath = Path.Combine(workshop, "3813157776", "DynamicCampaignMod.dll");
            var dcm = Assembly.LoadFrom(dcmPath);
            Call(rt.GetType("Sest.RuntimeFixes.WorldOperations", true), "Bind");
            var world = rt.GetType("Sest.RuntimeFixes.WorldOperations", true);
            var nativeRules = typeof(SeaPower.GameMain).Assembly.GetType("SeapowerUI.ViewModels.LinearCampaignTaskForceRibbonRules", true);
            var specs = ((IEnumerable)Call(nativeRules, "SplitPipeList", "fictional|real_a,Australia|real_b,US")).Cast<object>().ToList();
            Check(specs.Count == 3, "Captured native outer award grammar separates pipe-delimited specs");
            object parsed = Call(nativeRules, "TryParseMissionRibbonAwardSpec", "real_a,Australia");
            Check((string)parsed.GetType().GetProperty("RibbonId", All).GetValue(parsed, null) == "real_a" &&
                ((IEnumerable)parsed.GetType().GetProperty("Nations", All).GetValue(parsed, null)).Cast<string>().SequenceEqual(new[] { "Australia" }), "Captured native award parser retains the commander-nation selector");
            Check((bool)Call(world, "EnterFrame", 101) && !(bool)Call(world, "EnterFrame", 101) && (bool)Call(world, "EnterFrame", 102), "Tactical, tracker and strategic callbacks cannot toggle F11 twice in one frame");
            var sessionType = dcm.GetType("DynamicCampaignMod.Game.Session.CampaignSession", true);
            var battleType = dcm.GetType("DynamicCampaignMod.Game.Battle.BattleSession", true);
            Check(battleType.GetField("Plan", All) == null && battleType.GetProperty("Plan", All) != null, "Captured battle plan is a property, not a field");
            object sim = System.Runtime.Serialization.FormatterServices.GetUninitializedObject(dcm.GetType("DynamicCampaignMod.Core.Sim.CampaignSim", true));
            object fakeState = System.Runtime.Serialization.FormatterServices.GetUninitializedObject(dcm.GetType("DynamicCampaignMod.Core.State.CampaignState", true));
            object def = System.Runtime.Serialization.FormatterServices.GetUninitializedObject(dcm.GetType("DynamicCampaignMod.Core.Data.CampaignDefinition", true));
            // Deserialize the shipped definition into the captured author's
            // actual types, then exercise the live progress display against it.
            var json = Assembly.LoadFrom(Path.Combine(args[0], "Newtonsoft.Json.dll")).GetType("Newtonsoft.Json.JsonConvert", true);
            object revised = json.GetMethod("DeserializeObject", new[] { typeof(string), typeof(Type) }).Invoke(null, new object[] {
                File.ReadAllText("integration/world-sandbox/SEST_World_Campaign/dynamic_campaigns/sest-world-regions-2028/campaign.json"), def.GetType() });
            Check(((IList)Field(revised, "bases")).Count == 196, "Captured DCM deserializes all 196 revised world bases");
            var stages = (IList)((IDictionary)Field(revised, "ranks"))["blue"];
            Check(stages.Count == 8 && (int)Field(stages[7], "renown") == 10500, "Captured native rank definitions accept all eight reachable command stages");
            // Admiralty fixtures come from DCM's own completion path: Admiralty.End
            // on a standalone order papers it (Paper(AdmiraltyOrder)); End on an
            // operation's last phase skips the phase and papers the whole
            // operation once (OnPhaseEnded -> EndOperation -> Paper(AdmiraltyOperation)).
            var outcomeType = dcm.GetType("DynamicCampaignMod.Core.State.OrderOutcome", true);
            var orderKind = dcm.GetType("DynamicCampaignMod.Core.State.OrderKind", true);
            var orderStatus = dcm.GetType("DynamicCampaignMod.Core.State.OrderStatus", true);
            var templateType = dcm.GetType("DynamicCampaignMod.Core.State.OperationTemplate", true);
            var admiraltyType = dcm.GetType("DynamicCampaignMod.Core.Sim.Admiralty", true);
            var liveOrderType = dcm.GetType("DynamicCampaignMod.Core.State.AdmiraltyOrder", true);
            var operationType = dcm.GetType("DynamicCampaignMod.Core.State.AdmiraltyOperation", true);
            var dcmEnd = admiraltyType.GetMethod("End", All);
            Func<int, DateTime, object> campaignAt = (firstId, now) => {
                object live = Activator.CreateInstance(dcm.GetType("DynamicCampaignMod.Core.State.CampaignState", true), true);
                Set(live, "PlayerSideId", "blue"); Set(live, "_nextId", firstId); Set(live, "Now", now);
                return live;
            };
            Func<object, object> admiraltyOf = live => { object a = System.Runtime.Serialization.FormatterServices.GetUninitializedObject(admiraltyType); Set(a, "_state", live); return a; };
            Func<object, string, int, int, int, string, DateTime, object> addOrder = (live, kind, id, operation, phase, status, accepted) => {
                object o = Activator.CreateInstance(liveOrderType, true);
                Set(o, "Id", id); Set(o, "SideId", "blue"); Set(o, "Kind", Enum.Parse(orderKind, kind)); Set(o, "Title", kind + " task " + id);
                Set(o, "Status", Enum.Parse(orderStatus, status)); Set(o, "Offered", accepted.AddHours(-3)); Set(o, "Issued", accepted);
                Set(o, "OperationId", operation); Set(o, "Phase", phase); Set(o, "RewardPoints", 50); Set(o, "RewardRenown", 40); Set(o, "PenaltyRenown", 20);
                ((IList)Field(live, "AdmiraltyOrders")).Add(o); return o;
            };
            Func<object, object, string, object> endOrder = (live, o, status) => dcmEnd.Invoke(admiraltyOf(live), new object[] { o, Enum.Parse(orderStatus, status), true, null, false });
            // An accepted operation (Accept sets Active and Issued) whose earlier
            // phases are done and whose final phase now ends.
            Func<object, int, string, string[], string, DateTime, object> runOperation = (live, id, template, phases, last, accepted) => {
                object op = Activator.CreateInstance(operationType, true);
                Set(op, "Id", id); Set(op, "SideId", "blue"); Set(op, "Name", template.ToUpperInvariant()); Set(op, "Template", Enum.Parse(templateType, template));
                Set(op, "Status", Enum.Parse(orderStatus, "Active")); Set(op, "Offered", accepted.AddHours(-3)); Set(op, "Issued", accepted);
                Set(op, "BonusPoints", 120); Set(op, "BonusRenown", 100); Set(op, "PenaltyRenown", 50);
                ((IList)Field(live, "Operations")).Add(op);
                object final = null;
                for (int n = 0; n < phases.Length; n++)
                {
                    final = addOrder(live, phases[n], id + 1 + n, id, n + 1, n + 1 < phases.Length ? "Completed" : "Active", accepted.AddHours(n));
                    ((IList)Field(op, "Phases")).Add(id + 1 + n);
                }
                endOrder(live, final, last);
                return op;
            };
            var accepted0 = new DateTime(2028, 10, 1, 8, 0, 0);
            object campaign = campaignAt(500, new DateTime(2028, 10, 3, 6, 0, 0));
            Set(campaign, "Definition", revised);
            foreach (var spec in new[] { Tuple.Create("CoverConvoy", 41), Tuple.Create("CoverConvoy", 42), Tuple.Create("CoverConvoy", 43), Tuple.Create("Shadow", 44) })
                endOrder(campaign, addOrder(campaign, spec.Item1, spec.Item2, 0, 0, "Active", accepted0), "Completed");
            endOrder(campaign, addOrder(campaign, "Intercept", 45, 0, 0, "Active", accepted0), "Failed");
            runOperation(campaign, 60, "ConvoyRun", new[] { "ClearRoute", "CoverConvoy", "DefendBase" }, "Completed", accepted0);
            runOperation(campaign, 70, "FleetAction", new[] { "Shadow", "FleetAction" }, "Completed", accepted0);
            runOperation(campaign, 80, "SeaControl", new[] { "Barrier", "Interdict", "Blockade" }, "Completed", accepted0);
            runOperation(campaign, 90, "ConvoyRun", new[] { "ClearRoute", "CoverConvoy", "DefendBase" }, "Failed", accepted0);
            var papers = ((IList)Field(campaign, "Outcomes")).Cast<object>().ToList();
            Func<object, string, object> value = (o, f) => o.GetType().GetField(f, All).GetValue(o);
            Check(papers.Count == 9 && papers.All(o => (int)value(o, "OrderId") <= 50) && papers.Count(o => (int)value(o, "OperationId") > 0) == 4,
                "DCM papers each standalone order and each whole operation once, and no operation phase");
            object convoyRun = papers.Single(o => (int)value(o, "OperationId") == 60);
            Check((int)value(convoyRun, "OrderId") == 0 && value(convoyRun, "Template").ToString() == "ConvoyRun" && value(convoyRun, "Status").ToString() == "Completed" &&
                (DateTime)value(convoyRun, "Issued") == accepted0, "A completed convoy run is papered with OrderId 0, its template and its acceptance time");
            Func<object, string, object> evidenceFor = (o, coalition) => Call(world, "CompletedOrder", o, scope, coalition) ?? Call(world, "CompletedOperation", o, scope, coalition);
            var orderEvents = (IList)Activator.CreateInstance(typeof(List<>).MakeGenericType(entry));
            foreach (var result in papers) { object e = evidenceFor(result, "blue"); if (e != null) orderEvents.Add(e); }
            Check(orderEvents.Count == 7 && orderEvents.Cast<object>().All(e => !(bool)Field(e, "Manual")), "Completed orders and operations become separate non-battle evidence; failed ones do not");
            Check(Call(world, "CompletedOrder", convoyRun, scope, "blue") == null && Call(world, "CompletedOperation", papers[0], scope, "blue") == null, "An operation result is never read as an order, nor an order as an operation");
            Call(expanded, "Merge", orderEvents); Call(expanded, "Merge", orderEvents);
            Check(Progress(expanded, scope, "admiralty-service") == 7 && Progress(expanded, scope, "convoy-protection") == 4 && Progress(expanded, scope, "route-security") == 1 &&
                Progress(expanded, scope, "surveillance-service") == 2 && Progress(expanded, scope, "operational-versatility") == 5,
                "Each completed order and operation counts once: convoy runs for convoy protection and route security, fleet actions for surveillance");
            Check(Progress(expanded, scope, "joint-command") == 26, "Admiralty evidence does not inflate manual battle counts");
            // Reload a save from before those completions and complete them again:
            // new outcome ids and times, same orders, operations and acceptance.
            object replay = campaignAt(900, new DateTime(2028, 10, 4, 9, 0, 0));
            Set(replay, "Definition", revised);
            endOrder(replay, addOrder(replay, "CoverConvoy", 41, 0, 0, "Active", accepted0), "Completed");
            runOperation(replay, 60, "ConvoyRun", new[] { "ClearRoute", "CoverConvoy", "DefendBase" }, "Completed", accepted0);
            var replayed = (IList)Activator.CreateInstance(typeof(List<>).MakeGenericType(entry));
            foreach (var result in ((IList)Field(replay, "Outcomes")).Cast<object>()) replayed.Add(evidenceFor(result, "blue"));
            Call(expanded, "Merge", replayed);
            Check(Progress(expanded, scope, "admiralty-service") == 7 && Progress(expanded, scope, "route-security") == 1, "A completion replayed after reloading a save counts once");
            expanded = Open(Path.Combine(dir, "expanded.txt"));
            Check(Progress(expanded, scope, "admiralty-service") == 7 && Progress(expanded, scope, "convoy-protection") == 4, "Order and operation evidence survives restart in the compatible v1 record");
            Check(evidenceFor(convoyRun, "red") == null && evidenceFor(papers[0], "red") == null, "Other-side orders and operations cannot earn this coalition's awards");
            object outcome = papers[0];
            foreach (string status in new[] { "Offered", "Active", "Failed", "Declined", "Lapsed", "Cancelled", "Pending" })
            {
                Set(outcome, "Status", Enum.Parse(outcomeType.GetField("Status").FieldType, status)); Set(convoyRun, "Status", Enum.Parse(outcomeType.GetField("Status").FieldType, status));
                Check(evidenceFor(outcome, "blue") == null && evidenceFor(convoyRun, "blue") == null, "Non-completed order or operation excluded: " + status);
            }
            Set(outcome, "Status", Enum.Parse(outcomeType.GetField("Status").FieldType, "Completed")); Set(convoyRun, "Status", Enum.Parse(outcomeType.GetField("Status").FieldType, "Completed"));
            Set(outcome, "Issued", DateTime.MinValue);
            Check(evidenceFor(outcome, "blue") == null, "An order completed while only on offer (Issued reset by DCM) is excluded");
            Set(outcome, "Issued", new DateTime(2028, 10, 9));
            Check(evidenceFor(outcome, "blue") == null, "Completion before acceptance is rejected");
            Set(outcome, "Issued", accepted0);
            // Legacy 1.6.3 evidence still counts once, and is not added again.
            string legacy = (string)Call(world, "LegacyOrderKey", outcome, scope);
            Check(legacy == scope + ":admiralty:CoverConvoy:" + (int)value(outcome, "Id") + ":" + ((DateTime)value(outcome, "At")).Ticks, "Runtime 1.6.3's outcome key is recognised for the transition");
            string legacyFile = Path.Combine(dir, "legacy.txt");
            Func<string, string> b64 = t => Convert.ToBase64String(System.Text.Encoding.UTF8.GetBytes(t));
            long at163 = new DateTime(2028, 10, 2).Ticks;
            Func<string, long, string> line = (key, at) => string.Join("\t", b64(scope), b64(key), at.ToString(), "0", b64("Escort completed"), b64(""));
            File.WriteAllLines(legacyFile, new[] { "SEST-WORLD-SERVICE-1",
                line(scope + ":admiralty:CoverConvoy:501:" + at163, at163),
                line(scope + ":admiralty:CoverConvoy:502:" + (at163 + 1), at163),
                line(scope + ":admiralty:Unknown:503:" + at163, at163),
                line(scope + ":admiralty:CoverConvoy:504", at163),
                line(scope + ":admiralty-order:Shadow:44:" + (at163 + 1), at163),
                line(scope + ":admiralty-operation:Unknown:60:" + at163, at163),
                line(scope + ":admiralty-operation:ConvoyRun:0:" + at163, at163) });
            object legacyStore = Open(legacyFile);
            Check(!(bool)ledger.GetProperty("ReadOnly", All).GetValue(legacyStore, null) && Progress(legacyStore, scope, "admiralty-service") == 1 && Progress(legacyStore, scope, "convoy-protection") == 1,
                "A valid 1.6.3 order line counts once; tick mismatches, unknown kinds or templates, short keys, ids of 0 and acceptance after completion do not");
            // Older binaries keep reading the extended file safely.
            string current = Path.Combine(dir, "expanded.txt");
            foreach (var old in new[] { "R12-Final-20261110", "R12-Ribbons-20261110", "R12-WorldMapCosts-20261109" })
            {
                var prior = Assembly.Load(File.ReadAllBytes(Path.Combine("integration/beta-feature-parity/candidates", old, "SEST.RuntimeFixes.dll")));
                var priorLedger = prior.GetType("Sest.RuntimeFixes.WorldServiceLedger", true);
                object read = Activator.CreateInstance(priorLedger, All, null, new object[] { current }, null);
                var ribbons = ((IEnumerable)priorLedger.GetMethod("Ribbons", All).Invoke(read, new object[] { scope })).Cast<object>().ToList();
                Func<string, int> priorProgress = id => { object r = ribbons.Single(x => (string)x.GetType().GetField("Id", All).GetValue(x) == id); return (int)r.GetType().GetField("Progress", All).GetValue(r); };
                Check(!(bool)priorLedger.GetProperty("ReadOnly", All).GetValue(read, null) && priorProgress("iron-meridian") == 26 && ((IEnumerable)priorLedger.GetProperty("Entries", All).GetValue(read, null)).Cast<object>().Count() == ((IEnumerable)ledger.GetProperty("Entries", All).GetValue(expanded, null)).Cast<object>().Count(),
                    "Previous Runtime " + old + " reads the extended record without read-only mode, keeps every line and counts the same manual battles");
            }
            // R13: each result is recorded when DCM files it (a postfix on the
            // real Admiralty.Queue), so a paper read within one sample counts.
            Assembly.LoadFrom(Path.Combine(refs, "0Harmony.dll"));
            Call(world, "AttachOutcomeObserver");
            var filedList = (IList)world.GetField("filed", All).GetValue(null);
            Check(HarmonyLib.Harmony.GetPatchInfo(admiraltyType.GetMethod("Queue", All))?.Postfixes.Select(x => x.owner).SequenceEqual(new[] { "io.github.sest-hobby.world-admiralty-outcome" }) == true,
                "World Operations observes DCM's real Admiralty.Queue");
            Func<object, List<object>> outcomesOf = live => ((IList)Field(live, "Outcomes")).Cast<object>().ToList();
            Func<object, List<string>> keysOf = store => ((IEnumerable)ledger.GetProperty("Entries", All).GetValue(store, null)).Cast<object>().Where(e => !(bool)Field(e, "Manual")).Select(e => (string)Field(e, "Key")).OrderBy(k => k, StringComparer.Ordinal).ToList();
            Action<object> fixture = live => {
                foreach (var spec in new[] { Tuple.Create("CoverConvoy", 41), Tuple.Create("CoverConvoy", 42), Tuple.Create("CoverConvoy", 43), Tuple.Create("Shadow", 44) })
                    endOrder(live, addOrder(live, spec.Item1, spec.Item2, 0, 0, "Active", accepted0), "Completed");
                endOrder(live, addOrder(live, "Intercept", 45, 0, 0, "Active", accepted0), "Failed");
                runOperation(live, 60, "ConvoyRun", new[] { "ClearRoute", "CoverConvoy", "DefendBase" }, "Completed", accepted0);
                runOperation(live, 70, "FleetAction", new[] { "Shadow", "FleetAction" }, "Completed", accepted0);
                runOperation(live, 80, "SeaControl", new[] { "Barrier", "Interdict", "Blockade" }, "Completed", accepted0);
                runOperation(live, 90, "ConvoyRun", new[] { "ClearRoute", "CoverConvoy", "DefendBase" }, "Failed", accepted0);
            };
            Action<object, object> useState = (live, store) => {
                world.GetField("state", All).SetValue(null, live); world.GetField("ledger", All).SetValue(null, store);
                world.GetField("scope", All).SetValue(null, scope); world.GetField("side", All).SetValue(null, "blue");
                world.GetField("serviceSignature", All).SetValue(null, null); world.GetField("nextMerge", All).SetValue(null, 0d);
            };
            var readPaper = admiraltyType.GetMethod("Read", All);
            filedList.Clear();
            object filedCampaign = campaignAt(500, new DateTime(2028, 10, 3, 6, 0, 0));
            Set(filedCampaign, "Definition", revised);
            fixture(filedCampaign);
            var filedPapers = outcomesOf(filedCampaign);
            Check(filedList.Count == 9 && filedList.Cast<object>().Select(f => Field(f, "Outcome")).SequenceEqual(filedPapers) && filedList.Cast<object>().All(f => (string)Field(f, "Scope") == scope && (string)Field(f, "Side") == "blue"),
                "every filed result reaches SEST by reference, with its campaign and coalition");
            var unreadKeys = filedPapers.Select(o => evidenceFor(o, "blue")).Where(e => e != null).Select(e => (string)Field(e, "Key")).OrderBy(k => k, StringComparer.Ordinal).ToList();
            foreach (var filedPaper in filedPapers) readPaper.Invoke(admiraltyOf(filedCampaign), new[] { filedPaper });
            Check(outcomesOf(filedCampaign).Count == 0, "the real Admiralty.Read removes each paper before SEST samples");
            object filedStore = Open(Path.Combine(dir, "filed.txt"));
            useState(filedCampaign, filedStore);
            Call(world, "UpdateService");
            Check(keysOf(filedStore).SequenceEqual(unreadKeys) && unreadKeys.Count == 7 && filedList.Count == 0 && Progress(filedStore, scope, "admiralty-service") == 7 && Progress(filedStore, scope, "route-security") == 1,
                "papers read before the next sample are recorded, key for key as the unread scan records them, and released once merged");
            // Unread and filed copies of the same results: each counts once.
            object both = campaignAt(700, new DateTime(2028, 10, 3, 7, 0, 0));
            Set(both, "Definition", revised);
            fixture(both);
            var evidenceBoth = (IList)Call(world, "AdmiraltyEvidence", outcomesOf(both), scope, "blue", filedList);
            Check(evidenceBoth.Count == 7 && filedList.Count == 9, "an outcome both unread and filed is evaluated once (7 entries, not 14)");
            useState(both, filedStore);
            Call(world, "UpdateService");
            Check(keysOf(filedStore).SequenceEqual(unreadKeys) && filedList.Count == 0, "the same orders and acceptance times from another save count once");
            // An order captured while only on offer: OnCaptured resets Issued
            // after Queue returns; the deferred evaluation excludes it.
            object captured = campaignAt(800, new DateTime(2028, 10, 3, 8, 0, 0));
            Set(captured, "Definition", revised);
            object offered = addOrder(captured, "CapturePort", 46, 0, 0, "Offered", accepted0);
            Set(offered, "BaseId", "sest-test-port"); Set(offered, "WarPlan", 1);
            object port = Activator.CreateInstance(dcm.GetType("DynamicCampaignMod.Core.Data.BaseDefinition", true), true);
            Set(port, "id", "sest-test-port"); Set(port, "name", "Test Port");
            admiraltyType.GetMethod("OnCaptured", All).Invoke(admiraltyOf(captured), new object[] { port, "blue" });
            Check(filedList.Count == 1 && outcomesOf(captured).Count == 1 && (DateTime)Field(Field(filedList[0], "Outcome"), "Issued") == DateTime.MinValue,
                "DCM's real OnCaptured files the order taken while on offer, then resets its Issued");
            Check(((IList)Call(world, "AdmiraltyEvidence", new List<object>(), scope, "blue", filedList)).Count == 0, "that result is not counted: SEST keeps the reference and evaluates it after OnCaptured returns");
            filedList.Clear();
            // A paper filed and read within one sample still changes the evidence signature.
            useState(captured, filedStore);
            var signature = world.GetMethod("EvidenceSignature", All);
            Func<string> evidenceSignature = () => (string)signature.Invoke(null, new object[] { new List<object>(), outcomesOf(captured) });
            string quiet = evidenceSignature();
            endOrder(captured, addOrder(captured, "Shadow", 47, 0, 0, "Active", accepted0), "Completed");
            foreach (var quickPaper in outcomesOf(captured)) readPaper.Invoke(admiraltyOf(captured), new[] { quickPaper });
            Check(outcomesOf(captured).Count == 0 && evidenceSignature() != quiet, "a result filed and read between two samples still triggers a merge");
            // A write failure keeps the filed results for the 30 s retry.
            string blocker = Path.Combine(dir, "blocker");
            File.WriteAllText(blocker, "not a directory");
            object blocked = Open(Path.Combine(blocker, "service.txt"));
            useState(captured, blocked);
            Call(world, "UpdateService");
            Check(filedList.Count == 1 && (double)world.GetField("nextMerge", All).GetValue(null) > 0, "an unwritable record keeps the filed result and schedules a retry");
            File.Delete(blocker);
            world.GetField("nextMerge", All).SetValue(null, 0d);
            Call(world, "UpdateService");
            Check(filedList.Count == 0 && File.Exists(Path.Combine(blocker, "service.txt")) && Progress(Open(Path.Combine(blocker, "service.txt")), scope, "surveillance-service") == 1,
                "after the record becomes writable the result is written once and released");
            // Legacy 1.6.3 evidence still suppresses re-adding a filed result.
            endOrder(captured, addOrder(captured, "CoverConvoy", 501, 0, 0, "Active", new DateTime(2028, 10, 1)), "Completed");
            object legacyFiled = Field(filedList[filedList.Count - 1], "Outcome");
            Set(legacyFiled, "Id", 501); Set(legacyFiled, "At", new DateTime(at163));
            world.GetField("ledger", All).SetValue(null, legacyStore);
            Check(((IList)Call(world, "AdmiraltyEvidence", new List<object>(), scope, "blue", filedList)).Count == 0, "a filed result Runtime 1.6.3 already recorded under its outcome key is not added again");
            // Closing the campaign before the next sample still records what was filed.
            filedList.Clear();
            object closing = campaignAt(900, new DateTime(2028, 10, 3, 9, 0, 0));
            Set(closing, "Definition", revised);
            endOrder(closing, addOrder(closing, "HuntSubmarine", 48, 0, 0, "Active", accepted0), "Completed");
            object closingStore = Open(Path.Combine(dir, "closing.txt"));
            useState(null, closingStore);
            world.GetMethod("FlushFiled", All).Invoke(null, null);
            Check(filedList.Count == 0 && keysOf(closingStore).Count == 1 && keysOf(closingStore)[0].StartsWith(scope + ":admiralty-order:HuntSubmarine:48:", StringComparison.Ordinal),
                "results filed just before the campaign closes are recorded under their own campaign");
            world.GetField("state", All).SetValue(null, null);
            var opening = rt.GetType("Sest.RuntimeFixes.WorldOpeningBriefing", true);
            var paperType = dcm.GetType("DynamicCampaignMod.Core.Sim.Briefing", true);
            Set(fakeState, "Definition", revised);
            object paper = Activator.CreateInstance(paperType, true);
            Set(paper, "Subject", "SITREP 001 - GENERAL SITUATION"); Set(paper, "DateTimeGroup", "01 OCT '28 & <UTC>");
            Set(paper, "From", "COALITION MARITIME HEADQUARTERS"); Set(paper, "To", "ALL COMMANDS"); Set(paper, "Info", "FILE"); Set(paper, "Closing", "COMMANDER, BLUE COALITION sends.");
            // Sections as Story.BuildOpening writes them, with a long live roster.
            string roster = "Tracked at sea, identified: " + string.Join("; ", Enumerable.Range(1, 400).Select(n => "Surface Action Group " + n + " off Jask"));
            var dcmSections = new[] {
                Tuple.Create("SITUATION", new[] { "We are at war with Red Coalition.", "In Red Coalition hands: Bandar Abbas Naval Base; Jask Naval Base." }),
                Tuple.Create("ENEMY FORCES", new[] { roster, "Enemy submarines are not held by our sensors. Assume them on every approach." }),
                Tuple.Create("FRIENDLY FORCES", new[] { "Carrier groups: CSG 12 at Diego Garcia.", "Amphibious: ARG 3.", "At sea: Convoy 58." }),
                Tuple.Create("COMMANDER'S INTENT", new[] { "Keep the supply lines open." }),
                Tuple.Create("COMMAND AND SIGNAL", new[] { "Admiralty orders follow by separate message.", "Contact reports by FLASH precedence; losses and battle damage by IMMEDIATE." }) };
            foreach (var section in dcmSections) Call(paper, "Add", section.Item1, section.Item2.ToList());
            string told = (string)Call(paper, "Text");
            sessionType.GetField("_definition", All).SetValue(null, revised);
            Func<object, string> renderPaper = p => { object[] a = { p, "AUTHOR PAPER" }; opening.GetMethod("AfterPaper", All).Invoke(null, a); return (string)a[1]; };
            string rendered = renderPaper(paper);
            Check((string)Call(paper, "Text") == told && ((IList)Field(paper, "Sections")).Count == 5 && (string)Field(paper, "Subject") == "SITREP 001 - GENERAL SITUATION",
                "Showing the opening changes no DCM briefing data, so SITREP 001 is told and saved exactly as DCM wrote it");
            var formatted = new XmlDocument(); formatted.LoadXml(rendered);
            var textNodes = formatted.SelectNodes("//*[local-name()='TextBlock']").Cast<XmlElement>().ToList();
            var texts = textNodes.Select(x => x.GetAttribute("Text")).ToList();
            Check(textNodes.All(x => x.GetAttribute("TextWrapping") == "Wrap"), "Every opening-paper text block wraps within the native window");
            Check(texts.Contains("01 OCT '28 & <UTC>"), "Opening-paper markup safely escapes punctuation and XML characters");
            int dcmStart = texts.IndexOf("SITREP 001 - GENERAL SITUATION");
            Check(dcmStart > 0 && texts.Take(dcmStart).Sum(t => t.Length) < 3500 && texts.Take(dcmStart).Count(t => t == "SITUATION" || t == "BATTLE HANDOVER" || t == "SCENARIO") == 3 && !rendered.Contains("Courier New"),
                "The concise SEST brief comes first, stays short and inherits the game's readable font");
            Check(dcmSections.All(section => texts.IndexOf(section.Item1, dcmStart) > dcmStart && section.Item2.All(texts.Contains)) && texts.Contains("From: COALITION MARITIME HEADQUARTERS") && texts.Contains("COMMANDER, BLUE COALITION sends."),
                "DCM's live situation report follows in full: every section, roster, sender and signature");
            Check(textNodes.Single(x => x.GetAttribute("Text").StartsWith("Renown opens")).GetAttribute("FontWeight") == "Normal", "Body paragraphs use normal weight rather than all-bold briefing text");
            object asTold = paperType.GetMethod("Parse", All).Invoke(null, new object[] { told });
            Check(renderPaper(asTold).Contains(roster.Substring(0, 200)) && renderPaper(asTold).Contains("INITIAL OPERATIONS BRIEF"), "Reading SITREP 001 again from Messages renders DCM's saved text the same way");
            Set(asTold, "Subject", "SITREP 001 - GENERAL SITUATION (RE-ISSUED)");
            Check(renderPaper(asTold).Contains("SITREP 001 - GENERAL SITUATION (RE-ISSUED)"), "A re-issued SITREP keeps DCM's re-issue subject");
            object orderPaper = Activator.CreateInstance(paperType, true); Set(orderPaper, "Subject", "OPERATION TIDEWAY"); Call(orderPaper, "Add", "TASK", new List<string> { "Escort the convoy." });
            Check(renderPaper(orderPaper) == "AUTHOR PAPER", "Other papers in this world keep the author's rendering");
            object foreignDefinition = Activator.CreateInstance(revised.GetType(), true); Set(foreignDefinition, "id", "other.campaign");
            sessionType.GetField("_definition", All).SetValue(null, foreignDefinition);
            Check(renderPaper(paper) == "AUTHOR PAPER", "Other campaigns' opening papers remain unchanged");
            sessionType.GetField("_definition", All).SetValue(null, null);
            Check(renderPaper(paper) == "AUTHOR PAPER", "No campaign loaded leaves the paper unchanged");
            using (var actual = AssemblyDefinition.ReadAssembly(dcmPath))
            using (var candidate = AssemblyDefinition.ReadAssembly(runtime))
            {
                var story = actual.MainModule.GetType("DynamicCampaignMod.Core.Sim.Story");
                Check(story.Methods.Single(m => m.Name == "BuildOpening").Body.Instructions.Any(i => i.OpCode.Code == Mono.Cecil.Cil.Code.Ldstr && (string)i.Operand == (string)opening.GetField("OpeningSubject", All).GetValue(null)) &&
                    story.Methods.Single(m => m.Name == "TellOpening").Body.Instructions.Any(i => i.Operand is MethodReference r && r.Name == "Text" && r.DeclaringType.Name == "Briefing"),
                    "Captured DCM tells its own opening text under the subject SEST recognises");
                var own = candidate.MainModule.GetType("Sest.RuntimeFixes.WorldOpeningBriefing");
                Check(!own.Methods.Where(m => m.HasBody).SelectMany(m => m.Body.Instructions).Any(i => i.Operand is string text && (text == "BuildOpening" || text == "OpeningAsTold" || text == "Story")),
                    "SEST no longer patches DCM's opening builders, only the paper renderer");
            }
            using (var actual = AssemblyDefinition.ReadAssembly(dcmPath))
            using (var candidate = AssemblyDefinition.ReadAssembly(runtime))
            {
                var nativeRoot = actual.MainModule.GetType("DynamicCampaignMod.UI.CampaignUI").Methods.Single(m => m.Name == "AttachBars").Body.Instructions
                    .Select(i => i.Operand).OfType<FieldReference>().First(f => f.Name == "Instance");
                var costRoot = candidate.MainModule.GetType("Sest.RuntimeFixes.NativeCombatSurface").Methods.Single(m => m.Name == "Root");
                Check(nativeRoot.DeclaringType.FullName == "SeapowerUI.CampaignView" && costRoot.Body.Instructions.Select(i => i.Operand).OfType<FieldReference>().Any(f => f.FullName == nativeRoot.FullName), "World cost report targets the actual captured DCM campaign view, distinct from tactical and linear campaign views");
                var resource = actual.MainModule.Resources.OfType<EmbeddedResource>().Single(r => r.Name == "StrategyBar.xaml");
                string bar; using (var reader = new StreamReader(resource.GetResourceStream())) bar = reader.ReadToEnd();
                var layout = new XmlDocument(); layout.LoadXml(bar);
                var economyButton = layout.SelectNodes("//*[local-name()='ToggleButton']").Cast<XmlElement>().Single(x => x.GetAttribute("IsChecked").Contains("EconomyOpen"));
                Check(economyButton.ParentNode.LocalName == "StackPanel" && layout.SelectNodes("//*[local-name()='Style']").Cast<XmlElement>().Any(x => x.GetAttribute("x:Key") == "ToolButton"), "Map cost shortcut anchors to the captured Economy strip and normal button style");
            }
            var xp = (IDictionary)Activator.CreateInstance(fakeState.GetType().GetField("Renown", All).FieldType);
            xp.Add("blue", 299); Set(fakeState, "Renown", xp);
            var retainedRanks = (IDictionary)Activator.CreateInstance(fakeState.GetType().GetField("Ranks", All).FieldType);
            Set(fakeState, "Ranks", retainedRanks); Set(fakeState, "Definition", revised);
            var tasks = (IList)Activator.CreateInstance(fakeState.GetType().GetField("AdmiraltyOrders", All).FieldType);
            var orderType = dcm.GetType("DynamicCampaignMod.Core.State.AdmiraltyOrder", true);
            for (int i = 0; i < 3; i++)
            {
                object order = Activator.CreateInstance(orderType, true);
                Set(order, "SideId", i == 1 ? "red" : "blue"); Set(order, "Title", new[] { "Escort supply convoy", "Enemy task", "Already completed" }[i]);
                Set(order, "Status", Enum.Parse(orderType.GetField("Status").FieldType, i == 2 ? "Completed" : "Offered"));
                Set(order, "RewardRenown", 125); Set(order, "RewardPoints", 60); Set(order, "PenaltyRenown", 20);
                Set(order, "Deadline", new DateTime(2028, 10, 3)); Set(order, "OfferLapses", new DateTime(2028, 10, 2)); tasks.Add(order);
            }
            Set(fakeState, "AdmiraltyOrders", tasks);
            Func<object> progressView = () => {
                object page = Activator.CreateInstance(view.GetType(), true);
                Call(world, "Progression", page, fakeState, revised, "blue"); return page;
            };
            Func<object, string> progressText = page => string.Join("\n", ((IEnumerable)Field(page, "Summary")).Cast<string>().Concat(((IEnumerable)Field(page, "Details")).Cast<string>()));
            object progress = progressView(); string displayed = progressText(progress);
            Check(displayed.Contains("Command stage 1/8") && displayed.Contains("1 to go"), "Next milestone is clear immediately before promotion");
            Check(displayed.Contains("+125 renown | +60 credits") && displayed.Contains("Offer expires 2 Oct"), "Actual task rewards and offer expiry appear without invented supply payouts");
            Check(!displayed.Contains("Enemy task") && !displayed.Contains("Already completed"), "Task display excludes enemy and completed assignments");
            Check((int)xp["blue"] == 299 && tasks.Count == 3, "Opening progress does not grant renown or mutate native task state");
            xp["blue"] = 300; Check(progressText(progressView()).Contains("Command stage 2/8"), "Exact promotion boundary advances the displayed stage");
            xp["blue"] = 10500; displayed = progressText(progressView());
            Check(displayed.Contains("Command stage 8/8") && displayed.Contains("Final command stage reached") && !displayed.Contains("to go"), "Final stage has no phantom ninth milestone");
            object yards = System.Runtime.Serialization.FormatterServices.GetUninitializedObject(dcm.GetType("DynamicCampaignMod.Core.Sim.Shipyards", true));
            Set(yards, "_state", fakeState);
            Check((int)Call(yards, "RankOf", "blue") == 7, "Author's actual procurement engine reaches the eighth stage");
            retainedRanks["blue"] = 3; xp["blue"] = 299;
            Check(progressText(progressView()).Contains("Command stage 4/8") && (int)Call(yards, "RankOf", "blue") == 3, "Display matches native retained promotion after a renown penalty");
            object plan = System.Runtime.Serialization.FormatterServices.GetUninitializedObject(dcm.GetType("DynamicCampaignMod.Core.State.BattlePlan", true));
            object engagement = System.Runtime.Serialization.FormatterServices.GetUninitializedObject(dcm.GetType("DynamicCampaignMod.Core.State.Engagement", true));
            Set(sim, "State", fakeState); Set(plan, "Engagement", engagement); Set(engagement, "Id", 1559); Set(engagement, "At", new DateTime(2028, 10, 1));
            sessionType.GetProperty("Sim", All).GetSetMethod(true).Invoke(null, new[] { sim });
            sessionType.GetField("_definition", All).SetValue(null, def);
            sessionType.GetProperty("Active", All).GetSetMethod(true).Invoke(null, new object[] { true });
            Check((bool)Call(world, "ReadContext") && (bool)world.GetProperty("StrategicActive", All).GetValue(null, null), "Real captured session getters expose the strategic context");
            Call(world, "OpenCosts");
            Check((int)world.GetProperty("Tab", All).GetValue(null, null) == 2 && (bool)world.GetField("shown", All).GetValue(null), "Map shortcut opens cumulative combat costs directly");
            Call(world, "ToggleMapReport"); Check(!(bool)world.GetField("shown", All).GetValue(null), "F11 closes an open world report");
            Call(world, "SelectTab", 0); Call(world, "ToggleMapReport");
            Check((int)world.GetProperty("Tab", All).GetValue(null, null) == 2 && (bool)world.GetField("shown", All).GetValue(null), "F11 opens Costs directly even after using Overview");
            Call(world, "ToggleMapReport");
            // The open tab is rebuilt from what it shows, not on a timer: the
            // campaign clock alone never rebuilds it (RU-5, WSA-4).
            world.GetField("ledger", All).SetValue(null, expanded); world.GetField("scope", All).SetValue(null, scope); world.GetField("side", All).SetValue(null, "blue");
            foreach (int tab in new[] { 0, 1, 2, 3 })
            {
                Call(world, "SelectTab", tab);
                string before = (string)Call(world, "Signature");
                Set(fakeState, "Now", new DateTime(2028, 10, 1, 6, tab, 0));
                Check((string)Call(world, "Signature") == before, "The campaign clock alone does not rebuild world tab " + tab);
            }
            string service = (string)Call(world, "Signature");
            Call(expanded, "Merge", Events(scope, 400, 1));
            Check((string)Call(world, "Signature") != service, "A new service-record entry rebuilds the Service tab");
            Call(world, "SelectTab", 2); string costs = (string)Call(world, "Signature");
            Call(expanded, "Merge", Events(scope, 401, 1));
            Check((string)Call(world, "Signature") != costs, "A new battle report rebuilds Combat Costs");
            object servicePage = Activator.CreateInstance(viewType, true); Call(world, "Service", servicePage);
            string serviceText = string.Join("\n", ((IEnumerable)Field(servicePage, "Summary")).Cast<string>().Concat(((IEnumerable)Field(servicePage, "Details")).Cast<string>()));
            Check(serviceText.Contains("7 qualifying Admiralty tasks (4 orders, 3 operations)") && serviceText.Contains("each multi-phase operation once when its final phase completes") &&
                serviceText.Contains("Route Security counts convoy-run operations") && !serviceText.Contains("non-moot"), "Service text states exactly which Admiralty results count");
            Check(serviceText.Contains("SEST records each result when Dynamic Campaign Mod files it, whether or not its paper has been read (Runtime 1.6.5 and later).") &&
                serviceText.Contains("orders from 1.6.3, operations from 1.6.4") && !serviceText.Contains("waits unread"), "Service text says results are recorded when filed, not only while their paper is unread");
            Call(world, "SelectTab", 2);
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
                Tuple.Create("Core.State.CampaignState", "Now,PlayerSideId,Points,Renown,Ranks,Reports,BaseOwner,TaskForces,Squadrons,BuildOrders,AdmiraltyOrders,Operations,Outcomes"),
                Tuple.Create("Core.State.OrderOutcome", "Id,SideId,OrderId,OperationId,Status,At,Issued,Title,Kind,Template,Moot"),
                Tuple.Create("Core.State.AdmiraltyOrder", "Id,SideId,Status,Title,Deadline,OfferLapses,RewardRenown,RewardPoints,PenaltyRenown"),
                Tuple.Create("Core.Sim.Briefing", "Sections,Subject,DateTimeGroup,From,Closing"),
                Tuple.Create("Core.Data.CampaignDefinition", "id,name,bases,ranks,catalogue"),
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
