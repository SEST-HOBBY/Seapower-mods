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
            var outcomeType = dcm.GetType("DynamicCampaignMod.Core.State.OrderOutcome", true);
            object outcome = System.Runtime.Serialization.FormatterServices.GetUninitializedObject(outcomeType);
            Set(outcome, "Id", 501); Set(outcome, "OrderId", 41); Set(outcome, "SideId", "blue");
            Set(outcome, "Status", Enum.Parse(outcomeType.GetField("Status").FieldType, "Completed"));
            Set(outcome, "Kind", Enum.Parse(outcomeType.GetField("Kind").FieldType, "CoverConvoy"));
            Set(outcome, "Issued", new DateTime(2028, 10, 1)); Set(outcome, "At", new DateTime(2028, 10, 2));
            Set(outcome, "Title", "Escort completed"); Set(outcome, "Moot", false);
            object completed = Call(world, "CompletedOrder", outcome, scope, "blue");
            Check(completed != null && !(bool)Field(completed, "Manual"), "Captured successful accepted Admiralty outcomes become separate non-battle evidence");
            var orderEvents = (IList)Activator.CreateInstance(typeof(List<>).MakeGenericType(entry));
            foreach (var kind in new[] { "CoverConvoy", "CoverConvoy", "CoverConvoy", "Shadow", "ClearRoute" })
            {
                Set(outcome, "Kind", Enum.Parse(outcomeType.GetField("Kind").FieldType, kind));
                Set(outcome, "Id", 501 + orderEvents.Count);
                orderEvents.Add(Call(world, "CompletedOrder", outcome, scope, "blue"));
            }
            Call(expanded, "Merge", orderEvents); Call(expanded, "Merge", orderEvents);
            Check(Progress(expanded, scope, "admiralty-service") == 5 && Progress(expanded, scope, "convoy-protection") == 3 && Progress(expanded, scope, "operational-versatility") == 3, "Admiralty, convoy and varied-duty awards use deduplicated completed native orders");
            Check(Progress(expanded, scope, "joint-command") == 26, "Admiralty evidence does not inflate manual battle counts");
            expanded = Open(Path.Combine(dir, "expanded.txt"));
            Check(Progress(expanded, scope, "admiralty-service") == 5, "New order evidence survives restart in the compatible v1 record");
            Check(Call(world, "CompletedOrder", outcome, scope, "red") == null, "Other-side orders cannot earn this coalition's awards");
            foreach (string status in new[] { "Offered", "Active", "Failed", "Declined", "Lapsed", "Cancelled", "Pending" })
            {
                Set(outcome, "Status", Enum.Parse(outcomeType.GetField("Status").FieldType, status));
                Check(Call(world, "CompletedOrder", outcome, scope, "blue") == null, "Non-completed order excluded: " + status);
            }
            Set(outcome, "Status", Enum.Parse(outcomeType.GetField("Status").FieldType, "Completed"));
            Set(outcome, "Moot", true); Check(Call(world, "CompletedOrder", outcome, scope, "blue") == null, "Moot completion is not player service");
            Set(outcome, "Moot", false); Set(outcome, "Issued", DateTime.MinValue);
            Check(Call(world, "CompletedOrder", outcome, scope, "blue") == null, "Unaccepted order without issued time is excluded");
            Set(outcome, "Issued", new DateTime(2028, 10, 3));
            Check(Call(world, "CompletedOrder", outcome, scope, "blue") == null, "Completion before issue is rejected");
            Set(outcome, "Issued", new DateTime(2028, 10, 1)); Set(outcome, "OrderId", 0);
            Check(Call(world, "CompletedOrder", outcome, scope, "blue") == null, "Operation summary cannot count again as a phase order");
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
            var opening = rt.GetType("Sest.RuntimeFixes.WorldOpeningBriefing", true);
            var paperType = dcm.GetType("DynamicCampaignMod.Core.Sim.Briefing", true);
            object paper = Activator.CreateInstance(paperType, true);
            Set(paper, "Subject", "SITREP 001 - GENERAL SITUATION"); Set(paper, "DateTimeGroup", "01 OCT '28 & <UTC>");
            Set(paper, "From", "Coalition HQ"); Set(fakeState, "Definition", revised);
            Call(paper, "Add", "OLD ROSTER", new List<string> { new string('x', 12000) });
            Call(opening, "AfterOpening", fakeState, paper);
            Check(((IList)Field(paper, "Sections")).Count == 8 && (string)Field(paper, "From") == "Coalition HQ", "World opening replaces long rosters with eight sections and retains native header evidence");
            object[] paperArgs = { paper, "AUTHOR PAPER" };
            opening.GetMethod("AfterPaper", All).Invoke(null, paperArgs);
            var formatted = new XmlDocument(); formatted.LoadXml((string)paperArgs[1]);
            var textNodes = formatted.SelectNodes("//*[local-name()='TextBlock']").Cast<XmlElement>().ToList();
            Check(textNodes.All(x => x.GetAttribute("TextWrapping") == "Wrap"), "Every opening-paper text block wraps within the native window");
            Check(textNodes.Any(x => x.GetAttribute("Text") == "01 OCT '28 & <UTC>"), "Opening-paper markup safely escapes punctuation and XML characters");
            Check(textNodes.Sum(x => x.GetAttribute("Text").Length) < 3500 && !((string)paperArgs[1]).Contains("Courier New"), "Opening brief stays concise and inherits the game's readable font");
            var commandSection = textNodes.Single(x => x.GetAttribute("Text").StartsWith("Renown opens"));
            Check(commandSection.GetAttribute("FontWeight") == "Normal", "Body paragraphs use normal weight rather than all-bold briefing text");
            object foreign = Activator.CreateInstance(paperType, true); Set(foreign, "Subject", "OTHER CAMPAIGN");
            object foreignDefinition = Activator.CreateInstance(def.GetType(), true); Set(foreignDefinition, "id", "other.campaign");
            object foreignState = System.Runtime.Serialization.FormatterServices.GetUninitializedObject(fakeState.GetType()); Set(foreignState, "Definition", foreignDefinition);
            Call(foreign, "Add", "ORIGINAL", new List<string> { "Author's briefing" }); Call(opening, "AfterOpening", foreignState, foreign);
            paperArgs = new object[] { foreign, "AUTHOR PAPER" }; opening.GetMethod("AfterPaper", All).Invoke(null, paperArgs);
            Check((string)Field(foreign, "Subject") == "OTHER CAMPAIGN" && ((IList)Field(foreign, "Sections")).Count == 1 && (string)paperArgs[1] == "AUTHOR PAPER", "Other campaign openings and paper rendering remain unchanged");
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
