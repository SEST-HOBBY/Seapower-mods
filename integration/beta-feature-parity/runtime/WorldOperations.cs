using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using AnchorChain;

namespace Sest.RuntimeFixes;

// Optional integration with the inspected author DCM image. No DCM type is
// present in this assembly's signatures; disabling DCM keeps normal F11 costs.
internal static class WorldOperations
{
    private const string CampaignHash = "eacdb9a4c0353edd24543b631826e61f7cbcfc4f1a78de4fa80527aa5a2208f4";
    private static readonly Dictionary<string, FieldInfo> fields = new Dictionary<string, FieldInfo>();
    private static Type session, battle;
    private static MethodInfo campaignTick;
    private static bool tickAttached;
    private static int lastFrame = int.MinValue;
    private static WorldServiceLedger ledger;
    private static bool stopped, shown, wasStrategic;
    private static double nextBind, nextSample, nextView;
    private static CampaignCosts.CostView report;
    private static object state, definition, currentPlan;
    private static string scope = "", campaignName = "", side = "";
    private static readonly Dictionary<int, Tuple<long, string>> positions = new Dictionary<int, Tuple<long, string>>();
    internal static int Tab { get; private set; }
    internal static bool StrategicActive { get; private set; }
    private static double Now => (double)Stopwatch.GetTimestamp() / Stopwatch.Frequency;

    internal static void Install(string file)
    {
        ledger = new WorldServiceLedger(file);
        NativeCombatSurface.Bind();
        Api.Log("World Operations enabled: F11 overview, forces, costs and independent service record; native saves remain unchanged");
    }

    internal static void SelectTab(int value)
    {
        if (value < 0 || value > 3 || value == Tab) return;
        Tab = value; report = null; nextView = 0;
    }

    internal static void OpenCosts()
    {
        if (!StrategicActive) return;
        Tab = 2; shown = true; report = null; nextView = 0;
    }

    internal static void ToggleMapReport()
    {
        if (!StrategicActive) return;
        if (shown) shown = false;
        else OpenCosts();
    }

    private static object Get(object value, string name)
    {
        if (value == null) return null;
        Type t = value as Type ?? value.GetType();
        string key = t.FullName + ":" + name;
        if (!fields.TryGetValue(key, out var f))
        {
            f = t.GetField(name, BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static);
            if (f == null) throw new MissingFieldException(t.FullName, name);
            fields.Add(key, f);
        }
        return f.GetValue(value is Type ? null : value);
    }
    private static object Prop(Type t, string name) => t.GetProperty(name, Api.All)?.GetValue(null, null);
    private static string S(object value, string field) => Convert.ToString(Get(value, field), CultureInfo.InvariantCulture) ?? "";
    private static List<object> Rows(object value) => (value as IEnumerable)?.Cast<object>().Where(x => x != null).ToList() ?? new List<object>();
    private static string Clean(object value, int limit = 160)
    {
        string text = Convert.ToString(value, CultureInfo.InvariantCulture) ?? "";
        text = text.Replace('\r', ' ').Replace('\n', ' ');
        return text.Length > limit ? text.Substring(0, limit) : text;
    }
    private static string Dict(object value, string key)
    {
        var d = value as IDictionary;
        return d != null && d.Contains(key) ? Clean(d[key]) : "Not recorded";
    }
    private static object Lookup(object value, string key)
    {
        var d = value as IDictionary;
        return d != null && d.Contains(key) ? d[key] : null;
    }

    private static void Bind()
    {
        if (session != null || Now < nextBind) return;
        nextBind = Now + 2;
        var a = AppDomain.CurrentDomain.GetAssemblies().FirstOrDefault(x => x.GetType("DynamicCampaignMod.Game.Session.CampaignSession", false) != null);
        if (a == null) return;
        using (var sha = SHA256.Create())
        using (var stream = File.OpenRead(BetaAssemblyPolicy.OriginalLocation(a)))
            if (BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant() != CampaignHash)
                throw new InvalidOperationException("World Operations requires the inspected Dynamic Campaign Mod image");
        session = a.GetType("DynamicCampaignMod.Game.Session.CampaignSession", true);
        battle = a.GetType("DynamicCampaignMod.Game.Battle.BattleSession", true);
        if (session.GetProperty("Active", Api.All)?.PropertyType != typeof(bool) || battle.GetProperty("Active", Api.All)?.PropertyType != typeof(bool))
            throw new MissingMemberException("inspected DCM session lifecycle");
        WorldOpeningBriefing.Bind(a);
        campaignTick = a.GetType("DynamicCampaignMod.UI.CampaignUI", true).GetMethod("Tick", Api.All, null, Type.EmptyTypes, null);
        if (campaignTick?.ReturnType != typeof(void)) throw new MissingMemberException("captured strategic UI update");
        Api.Log("World Operations attached to Dynamic Campaign Mod 0.25.0.1");
    }

    internal static bool ReadContext()
    {
        // DCM sets CampaignSession.Active=false when unloading its strategy
        // scene for battle. Sim/definition survive; BattleSession.Plan is a
        // PROPERTY and remains the authoritative live-battle context.
        bool onMap = session != null && (bool)Prop(session, "Active");
        currentPlan = battle == null ? null : Prop(battle, "Plan");
        object sim = session == null ? null : Prop(session, "Sim");
        // Sim is cleared by Teardown, not by temporary scene unloading.
        // Keep evidence through the return gap after Plan resets and before
        // the strategic scene has finished loading.
        bool active = sim != null;
        state = active ? Get(sim, "State") : null;
        definition = active ? Prop(session, "Definition") : null;
        active = active && state != null && definition != null;
        StrategicActive = active && onMap && currentPlan == null;
        return active;
    }

    internal static void Poll()
    {
        if (stopped || ledger == null) return;
        try
        {
            Bind();
            WorldOpeningBriefing.Install();
            if (!tickAttached && campaignTick != null)
            {
                Api.Postfix(campaignTick, typeof(WorldOperations), nameof(Poll), "io.github.sest-hobby.world-map-update");
                tickAttached = true;
            }
            bool active = ReadContext();
            if (active && !EnterFrame(UnityEngine.Time.frameCount)) return;
            bool inBattle = currentPlan != null;
            if (StrategicActive != wasStrategic)
            {
                shown = false; report = null; nextSample = 0;
                WorldMapCostsButton.Remove();
                if (StrategicActive) CombatHistory.Observe(null, null);
                if (wasStrategic) NativeCombatSurface.Close();
                wasStrategic = StrategicActive;
            }
            if (!active) { state = null; scope = ""; positions.Clear(); return; }
            if (Now >= nextSample)
            {
                nextSample = Now + 1;
                side = S(state, "PlayerSideId");
                string nextScope = S(definition, "id") + ":" + side;
                if (nextScope != scope) { scope = nextScope; positions.Clear(); report = null; }
                campaignName = Clean(Get(definition, "name"));
                RememberEngagement(inBattle ? currentPlan : null);
                UpdateService();
            }
            if (!StrategicActive || !NativeCombatSurface.EnsureReady(false)) return;
            WorldMapCostsButton.Ensure(Get(Prop(session, "UI"), "_strategyView") as Noesis.FrameworkElement, Now);
            if (UnityEngine.Input.GetKeyDown(UnityEngine.KeyCode.F11) && !Modified())
                ToggleMapReport();
            if (shown && (report == null || Now >= nextView))
            {
                report = View(); nextView = Now + (Tab == 1 ? 5 : 2);
            }
            NativeCombatSurface.Tick(false, shown, report, "world:" + scope + ":" + Tab, () => shown = false, Now);
        }
        catch (Exception ex)
        {
            if (wasStrategic) NativeCombatSurface.Close();
            WorldMapCostsButton.Remove();
            stopped = true; StrategicActive = false;
            Api.LogFailure("World Operations unavailable; native campaign and combat costs retained", ex);
        }
    }

    internal static bool EnterFrame(int frame)
    {
        if (frame == lastFrame) return false;
        lastFrame = frame;
        return true;
    }

    private static bool Modified() => UnityEngine.Input.GetKey(UnityEngine.KeyCode.LeftControl) || UnityEngine.Input.GetKey(UnityEngine.KeyCode.RightControl) || UnityEngine.Input.GetKey(UnityEngine.KeyCode.LeftAlt) || UnityEngine.Input.GetKey(UnityEngine.KeyCode.RightAlt) || UnityEngine.Input.GetKey(UnityEngine.KeyCode.LeftShift) || UnityEngine.Input.GetKey(UnityEngine.KeyCode.RightShift);

    private static void RememberEngagement(object plan)
    {
        if (plan == null) return;
        var e = Get(plan, "Engagement");
        if (e == null) return;
        var point = Get(e, "Point");
        int id = Convert.ToInt32(Get(e, "Id"));
        if (positions.Count > 4096) positions.Clear();
        positions[id] = Tuple.Create(((DateTime)Get(e, "At")).Ticks, WorldServiceLedger.Theatre(Convert.ToDouble(Get(point, "Lat")), Convert.ToDouble(Get(point, "Lon"))));
    }

    private static void UpdateService()
    {
        var events = new List<WorldServiceLedger.Entry>();
        foreach (var r in Rows(Get(state, "Reports")))
        {
            if (S(r, "PlayerSideId") != side) continue;
            int id = Convert.ToInt32(Get(r, "EngagementId"));
            var at = (DateTime)Get(r, "At");
            string theatre = positions.TryGetValue(id, out var p) && p.Item1 == at.Ticks ? p.Item2 : "";
            events.Add(new WorldServiceLedger.Entry { Scope = scope, Key = scope + ":" + id + ":" + at.Ticks, At = at.Ticks, Where = Clean(Get(r, "Where"), 512), Manual = !(bool)Get(r, "AutoResolved"), Theatre = theatre });
        }
        ledger.Merge(events);
    }

    internal static void Stamp(CombatGameRecord record)
    {
        if (stopped || state == null || battle == null || !(bool)Prop(battle, "Active")) return;
        var e = Get(Prop(battle, "Plan"), "Engagement");
        if (e != null)
        {
            record.Source = "DCM:" + scope + ":" + ((DateTime)Get(e, "At")).Ticks.ToString(CultureInfo.InvariantCulture);
            record.MissionIndex = Convert.ToInt32(Get(e, "Id"));
        }
    }

    private static CampaignCosts.CostView View()
    {
        var v = new CampaignCosts.CostView { Title = Tab == 2 ? "CUMULATIVE COMBAT COSTS" : "WORLD CAMPAIGN OPERATIONS", Subtitle = campaignName + " | F11 closes | Drag title bar to move", World = true };
        v.Notes[0] = "Campaign credits and USD catalogue estimates are separate. Orders and purchases stay in the native campaign panels.";
        v.Notes[1] = "Service record belongs to this profile and coalition across saves. Native commander records and saves are unchanged.";
        v.Notes[2] = "";
        v.AddSummary(CostLineKind.Basis, ((DateTime)Get(state, "Now")).ToString("d MMM yyyy HH:mm", CultureInfo.InvariantCulture) + " | Coalition " + side + " | " + new[] { "Overview", "Forces", "Combat Costs", "Service" }[Tab]);
        switch (Tab) {
            case 0: Overview(v); break;
            case 1: Forces(v); break;
            case 2: Costs(v); break;
            case 3: Service(v); break;
        }
        return v;
    }

    private static void Overview(CampaignCosts.CostView v)
    {
        v.AddSummary(CostLineKind.PlayerTotal, "Campaign budget: " + Dict(Get(state, "Points"), side) + " credits");
        Progression(v, state, definition, side);
        var owners = Get(state, "BaseOwner") as IDictionary;
        int ports = owners == null ? 0 : owners.Values.Cast<object>().Count(x => Convert.ToString(x) == side);
        v.AddDetail(CostLineKind.Section, "WORLD AND COMMAND");
        v.AddDetail(CostLineKind.Body, ports + " controlled bases / " + Rows(Get(definition, "bases")).Count + " world bases");
        v.AddDetail(CostLineKind.Body, Rows(Get(state, "TaskForces")).Count(x => S(x, "SideId") == side) + " task forces | " + Rows(Get(state, "Squadrons")).Count(x => S(x, "SideId") == side) + " shore squadrons");
        v.AddDetail(CostLineKind.Section, "LOGISTICS AND OPERATIONS");
        v.AddDetail(CostLineKind.Body, Rows(Get(state, "BuildOrders")).Count + " build orders | " + Rows(Get(state, "AdmiraltyOrders")).Count + " admiralty orders | " + Rows(Get(state, "Operations")).Count + " operations (all recorded sides)");
        v.AddDetail(CostLineKind.Body, "Use the campaign's forces, base and supply panels for routing, replenishment, convoys and ground operations. Changing the displayed USD basis does not change campaign prices.");
        v.AddDetail(CostLineKind.Section, "ENABLED INTEGRATIONS");
        string[] types = { "WeaponCostsMod.Overlay", "SeaPowerTopo.Plugin", "IdentifyExpanded.Plugin" };
        string[] names = { "Combat Cost Tracker", "Topographic Map", "Identify Expanded" };
        var assemblies = AppDomain.CurrentDomain.GetAssemblies();
        v.AddDetail(CostLineKind.Body, "Dynamic Campaign Mod: connected | Campaign map integration: active");
        for (int i = 0; i < types.Length; i++)
        {
            bool found = assemblies.Any(a => a.GetType(types[i], false) != null);
            // A loaded assembly alone does not prove the author's entrypoint ran.
            v.AddDetail(CostLineKind.Item, names[i] + ": " + (found ? "assembly detected; check its in-game controls" : "not detected by this panel"));
        }
        v.AddDetail(CostLineKind.Section, "CAMPAIGN CONTENT");
        v.AddDetail(CostLineKind.Body, "Global Maritime Operations 2028 uses hypothetical coalition access, forces and stocks. Revised facilities and command stages apply to new campaigns. Start a new campaign for the complete revised layout; existing saves keep their saved forces and stocks.");
    }

    // Read the author's live definitions and orders. No reward, stock or save
    // mutation here: DCM alone decides completion and applies its own rewards.
    internal static void Progression(CampaignCosts.CostView v, object gameState, object def, string ours)
    {
        int renown = Convert.ToInt32(Lookup(Get(gameState, "Renown"), ours) ?? 0);
        var stages = Rows(Lookup(Get(def, "ranks"), ours));
        int rank = Math.Max(0, stages.FindLastIndex(x => Convert.ToInt32(Get(x, "renown")) <= renown));
        // DCM keeps an announced promotion after a later renown penalty.
        rank = Math.Min(Math.Max(0, stages.Count - 1), Math.Max(rank, Convert.ToInt32(Lookup(Get(gameState, "Ranks"), ours) ?? 0)));
        if (stages.Count > 0)
        {
            v.AddSummary(CostLineKind.Breakdown, "Command stage " + (rank + 1) + "/" + stages.Count + ": " + Clean(Get(stages[rank], "name")) + " | Renown " + renown);
            v.AddDetail(CostLineKind.Section, "COMMAND PROGRESS");
            if (rank + 1 < stages.Count)
            {
                int target = Convert.ToInt32(Get(stages[rank + 1], "renown"));
                int unlocks = Rows(Get(def, "catalogue")).Count(x => S(x, "side") == ours && Convert.ToInt32(Get(x, "tier")) == rank + 1);
                v.AddDetail(CostLineKind.Body, "Next: " + Clean(Get(stages[rank + 1], "name")) + " at " + target + " renown | " + Math.Max(0, target - renown) + " to go | " + unlocks + " additional recruitment entries");
            }
            else v.AddDetail(CostLineKind.Body, "Final command stage reached. Continue operations to build renown and sustain your force.");
        }
        v.AddDetail(CostLineKind.Body, "RENOWN AND BUDGET: battle results and completed, accepted Admiralty tasks. Look for escort, area-control, shadowing and multi-phase assignments when offered. Read each task's conditions; routine movement or ending a battle alone earns no task reward.");
        v.AddDetail(CostLineKind.Body, "SUPPLIES: depot production feeds convoys; airlift moves urgent ammunition; loaded replenishment ships support forces at sea. Protect deliveries and raise a short base's supply priority. Credits fund purchases and are separate from physical stocks.");
        v.AddDetail(CostLineKind.Section, "CURRENT ADMIRALTY TASKS");
        var orders = Rows(Get(gameState, "AdmiraltyOrders")).Where(x => S(x, "SideId") == ours && (S(x, "Status") == "Offered" || S(x, "Status") == "Active")).OrderBy(x => (DateTime)Get(x, "Deadline")).ToList();
        foreach (var order in orders.Take(4))
        {
            bool offered = S(order, "Status") == "Offered";
            v.AddDetail(CostLineKind.Mission, Clean(Get(order, "Title")) + (offered ? " | Offered - accept in Admiralty" : " | Active"));
            v.AddDetail(CostLineKind.Item, "+" + Clean(Get(order, "RewardRenown")) + " renown | +" + Clean(Get(order, "RewardPoints")) + " credits on completion | Failure penalty: " + Clean(Get(order, "PenaltyRenown")) + " renown");
            var when = (DateTime)Get(order, offered ? "OfferLapses" : "Deadline");
            v.AddDetail(CostLineKind.Time, (offered ? "Offer expires " : "Deadline ") + when.ToString("d MMM HH:mm", CultureInfo.InvariantCulture) + " | Open Admiralty for task conditions and progress.");
        }
        if (orders.Count == 0) v.AddDetail(CostLineKind.Body, "No offered or active assignments recorded. Check Admiralty as campaign time advances; task availability follows the operational situation.");
        if (orders.Count > 4) v.AddDetail(CostLineKind.Body, (orders.Count - 4) + " more assignments in Admiralty.");
    }

    private static void Forces(CampaignCosts.CostView v)
    {
        var prices = CampaignCosts.Catalogue();
        var total = new CombatAmount();
        int ships = 0, airframes = 0;
        v.AddDetail(CostLineKind.Section, "COALITION FLEET");
        foreach (var force in Rows(Get(state, "TaskForces")).Where(x => S(x, "SideId") == side).OrderBy(x => S(x, "Name")))
        {
            v.AddDetail(CostLineKind.Mission, Clean(Get(force, "Name")));
            foreach (var hull in Rows(Get(force, "Ships")))
            {
                ships++;
                string uid = S(hull, "UnitIni");
                var price = prices?.Read("vessel", uid, "vessels") ?? new CombatPrice();
                total.Add(price, 1);
                v.AddDetail(CostLineKind.Item, Clean(Get(hull, "Name")) + " | " + Clean(uid) + " | " + (price.Amount.HasValue ? CombatAmount.Money(price.Amount.Value) : "Price unknown"));
                v.AddDetail(CostLineKind.Time, "Damage " + Convert.ToDouble(Get(hull, "Damage")).ToString("0.##", CultureInfo.InvariantCulture) + " | Fuel " + Convert.ToDouble(Get(hull, "Fuel")).ToString("0.##", CultureInfo.InvariantCulture) + " (native units) | " + Clean(price.Source));
            }
        }
        v.AddDetail(CostLineKind.Section, "SHORE AIR GROUPS");
        foreach (var squadron in Rows(Get(state, "Squadrons")).Where(x => S(x, "SideId") == side).OrderBy(x => S(x, "Name")))
        {
            var rows = Rows(Get(squadron, "Airframes"));
            airframes += rows.Count;
            v.AddDetail(CostLineKind.Mission, Clean(Get(squadron, "Name")) + " | " + Clean(Get(squadron, "BaseId")));
            foreach (var g in rows.GroupBy(x => S(x, "UnitIni")))
            {
                var price = prices?.Read("aircraft", g.Key, "aircraft") ?? new CombatPrice();
                total.Add(price, g.Count());
                v.AddDetail(CostLineKind.Item, g.Key + " x" + g.Count() + " | " + g.Count(x => S(x, "Status") == "Ready" || S(x, "Status") == "Armed") + " ready/armed | " + (price.Amount.HasValue ? CombatAmount.Money(price.Amount.Value * g.Count()) : "Price unknown"));
            }
        }
        v.AddSummary(CostLineKind.PlayerTotal, "Fleet and shore aircraft: " + total.Text + " estimated USD");
        v.AddSummary(CostLineKind.Breakdown, ships + " hulls | " + airframes + " shore aircraft | " + total.Unknown + " unpriced platforms");
        v.AddSummary(CostLineKind.Basis, prices == null ? "Price catalogue unavailable" : prices.Basis + " catalogue basis. Carrier aircraft, stores, cargo and ground units excluded from this roster subtotal.");
    }

    private static void Costs(CampaignCosts.CostView v)
    {
        v.AddDetail(CostLineKind.Basis, "Campaign budget: " + Dict(Get(state, "Points"), side) + " credits (separate from USD combat costs)");
        var completed = ledger.Entries.Where(e => e.Scope == scope && e.Manual).ToList();
        var games = RecordedGames(CombatHistory.Games, completed, scope);
        v.AddDetail(CostLineKind.Basis, completed.Count + " completed manual battle reports | " + games.Count + " with SEST itemised cost history. Reloaded attempts use the latest record for the same engagement.");
        var costs = CampaignCosts.CampaignView(games);
        foreach (var row in costs.SummaryRows) v.AddSummary(row.Kind, row.Text);
        foreach (var row in costs.DetailRows) v.AddDetail(row.Kind, row.Text);
        v.Notes[0] = "USD totals cover SEST-recorded battles for this campaign and coalition across saves. Older battles and auto-resolved battles may lack itemised USD evidence.";
        v.Notes[1] = costs.Notes[1]; v.Notes[2] = costs.Notes[2];
    }

    internal static List<CombatGameRecord> RecordedGames(IEnumerable<CombatGameRecord> history, IEnumerable<WorldServiceLedger.Entry> reports, string scope)
    {
        var keys = new HashSet<string>(reports.Where(e => e.Scope == scope && e.Manual).Select(e => e.Key), StringComparer.Ordinal);
        var games = history.Where(g => g.Source.StartsWith("DCM:" + scope + ":", StringComparison.Ordinal))
            .Where(g => keys.Contains(scope + ":" + g.MissionIndex + ":" + g.Source.Substring(g.Source.LastIndexOf(':') + 1)))
            .GroupBy(g => g.Source + ":" + g.MissionIndex).Select(g => g.OrderByDescending(x => x.EndedUtc).First()).ToList();
        foreach (var game in games)
        {
            if (long.TryParse(game.Source.Substring(game.Source.LastIndexOf(':') + 1), out var ticks) && ticks >= DateTime.MinValue.Ticks && ticks <= DateTime.MaxValue.Ticks)
                game.CompletedAt = new DateTime(ticks);
        }
        return games;
    }

    private static void Service(CampaignCosts.CostView v)
    {
        var ribbons = ledger.Ribbons(scope);
        int earned = ribbons.Count(r => r.Earned);
        v.AddSummary(CostLineKind.PlayerTotal, earned + " service ribbons earned");
        v.AddSummary(CostLineKind.Basis, "Fictional SEST profile awards | " + ledger.Entries.Count(e => e.Scope == scope && e.Manual) + " completed manual battles recorded");
        if (ledger.ReadOnly) v.AddDetail(CostLineKind.Body, "Service record is read-only because its saved format could not be validated. The existing file has been retained.");
        foreach (var r in ribbons.OrderByDescending(r => r.Earned))
        {
            string name = r.Name + " | " + (r.Earned ? "AWARDED" : r.Progress + "/" + r.Required);
            v.Details.Add(name);
            v.DetailRows.Add(new CostReportLine(r.Earned ? CostLineKind.Ribbon : CostLineKind.Mission, name, r.Earned ? r.Colours : null));
            v.AddDetail(CostLineKind.Breakdown, r.Citation);
        }
        v.AddDetail(CostLineKind.Section, "CITATION AND EVIDENCE");
        v.AddDetail(CostLineKind.Body, "Issued by Joint Maritime Campaign Headquarters. Completion comes from DCM battle reports. Auto-resolves do not count. Theatre awards require an engagement position observed during battle; an older report without coordinates earns global service progress only.");
        v.AddDetail(CostLineKind.Body, "Native Southern Watch, Southern Reach, Red Line and Sulu Line completion ribbons appear in their Task Force Service Records. Logistics, ROE and specialist performance awards require additional evidence and are not inferred from spending.");
    }
}
