using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
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
    private static bool stopped, shown, wasStrategic, mergeReported;
    private static double nextBind, nextSample, nextView, nextMerge;
    private static CampaignCosts.CostView report;
    private static object state, definition, currentPlan;
    private static string scope = "", campaignName = "", side = "";
    // The evidence last merged, and the view last built: a view is rebuilt
    // only when the data its tab shows has changed (RU-5).
    private static string serviceSignature, viewSignature;
    // One price catalogue per world-map visit. The UI cache is mission-scoped
    // and returns nothing on the map, where each build took up to ~300 ms.
    private static CombatPrices mapPrices;
    private static string[] integrations;
    private static readonly Dictionary<int, Tuple<long, string>> positions = new Dictionary<int, Tuple<long, string>>();
    // Manual reports in the loaded save. They also link Combat Costs when the
    // profile service record is read-only or could not be written.
    private static readonly List<WorldServiceLedger.Entry> liveReports = new List<WorldServiceLedger.Entry>();
    // Admiralty results as Dynamic Campaign Mod files them (a postfix on
    // Admiralty.Queue, the only place a result is added). Kept by reference and
    // evaluated at the next service sample: Admiralty.OnCaptured resets an
    // unaccepted order's Issued after Queue returns. The unread-paper scan
    // stays as the fallback, so a result read within one sample still counts.
    internal sealed class Filed
    {
        internal object Outcome;
        internal string Scope, Side;
    }
    private sealed class SameObject : IEqualityComparer<object>
    {
        internal static readonly SameObject Instance = new SameObject();
        public new bool Equals(object x, object y) => ReferenceEquals(x, y);
        public int GetHashCode(object value) => System.Runtime.CompilerServices.RuntimeHelpers.GetHashCode(value);
    }
    private const int FiledLimit = 512;
    private static readonly List<Filed> filed = new List<Filed>();
    private static readonly object filedLock = new object();
    private static int filedRevision;
    private static bool filedDropReported, filedFailureReported, queueAttached;
    private static MethodInfo admiraltyQueue;
    internal static int Tab { get; private set; }
    internal static bool StrategicActive { get; private set; }
    private static double Now => (double)Stopwatch.GetTimestamp() / Stopwatch.Frequency;

    internal static void Install(string file)
    {
        ledger = new WorldServiceLedger(file);
        NativeCombatSurface.Bind();
        Api.Log("World Operations enabled: F11 overview, forces, costs and independent service record; Dynamic Campaign Mod state and saves are read, never written");
    }

    // Selecting the open tab again refreshes it (Forces is a snapshot).
    internal static void SelectTab(int value)
    {
        if (value < 0 || value > 3) return;
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
        try
        {
            var admiralty = a.GetType("DynamicCampaignMod.Core.Sim.Admiralty", true);
            var queue = admiralty.GetMethod("Queue", Api.All, null, new[] { a.GetType("DynamicCampaignMod.Core.State.OrderOutcome", true) }, null);
            if (queue == null || queue.IsStatic || queue.ReturnType != typeof(void) || admiralty.GetField("_state", Api.All)?.FieldType != a.GetType("DynamicCampaignMod.Core.State.CampaignState", true))
                throw new MissingMemberException("captured DCM Admiralty.Queue(OrderOutcome)");
            admiraltyQueue = queue;
        }
        catch (Exception ex)
        {
            admiraltyQueue = null;
            Api.LogFailure("Admiralty filing observation unavailable; unread papers are still recorded", ex);
        }
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
            if (!queueAttached && admiraltyQueue != null)
            {
                queueAttached = true;
                AttachOutcomeObserver();
            }
            bool active = ReadContext();
            if (active && !EnterFrame(UnityEngine.Time.frameCount)) return;
            bool inBattle = currentPlan != null;
            if (StrategicActive != wasStrategic)
            {
                shown = false; report = null; nextSample = 0; mapPrices = null; integrations = null;
                WorldMapCostsButton.Remove();
                if (StrategicActive) CombatHistory.Observe(null, null);
                if (wasStrategic) NativeCombatSurface.Close();
                wasStrategic = StrategicActive;
            }
            if (!active) { FlushFiled(); state = null; scope = ""; positions.Clear(); liveReports.Clear(); serviceSignature = null; mapPrices = null; return; }
            if (Now >= nextSample)
            {
                nextSample = Now + 1;
                side = S(state, "PlayerSideId");
                string nextScope = S(definition, "id") + ":" + side;
                if (nextScope != scope) { scope = nextScope; positions.Clear(); liveReports.Clear(); serviceSignature = null; report = null; mapPrices = null; }
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
                nextView = Now + 1;
                string signature = Signature();
                if (report == null || signature != viewSignature) { report = View(); viewSignature = Signature(); }
                // The clock is a bound line: updating it never rebuilds rows.
                string subtitle = Subtitle();
                if (report.Subtitle != subtitle) report.Subtitle = subtitle;
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
        var reports = Rows(Get(state, "Reports"));
        var outcomes = Rows(Get(state, "Outcomes"));
        // Merge only when DCM's reports, unread or filed results or observed
        // positions change, and retry a failed write later instead of every second.
        if (EvidenceSignature(reports, outcomes) == serviceSignature || Now < nextMerge) return;
        var events = new List<WorldServiceLedger.Entry>();
        liveReports.Clear();
        foreach (var r in reports)
        {
            if (S(r, "PlayerSideId") != side) continue;
            int id = Convert.ToInt32(Get(r, "EngagementId"));
            var at = (DateTime)Get(r, "At");
            string theatre = positions.TryGetValue(id, out var p) && p.Item1 == at.Ticks ? p.Item2 : "";
            var entry = new WorldServiceLedger.Entry { Scope = scope, Key = scope + ":" + id + ":" + at.Ticks, At = at.Ticks, Where = Clean(Get(r, "Where"), 512), Manual = !(bool)Get(r, "AutoResolved"), Theatre = theatre };
            events.Add(entry);
            if (entry.Manual) liveReports.Add(entry);
        }
        var taken = TakeFiled();
        events.AddRange(AdmiraltyEvidence(outcomes, scope, side, taken));
        try
        {
            ledger.Merge(events);
            ReleaseFiled(taken);
            serviceSignature = EvidenceSignature(reports, outcomes);
            mergeReported = false;
        }
        catch (Exception ex)
        {
            // The record is profile data, not a reason to close World
            // Operations: keep the window, costs and live evidence.
            nextMerge = Now + 30;
            if (!mergeReported) { mergeReported = true; Api.LogFailure("world service record not updated; World Operations stays open and retries in 30 s", ex); }
        }
    }

    private static string EvidenceSignature(List<object> reports, List<object> outcomes)
    {
        var last = reports.Count == 0 ? null : reports[reports.Count - 1];
        int revision, count;
        lock (filedLock) { revision = filedRevision; count = filed.Count; }
        return scope + "|" + reports.Count + "|" + (last == null ? "" : S(last, "EngagementId") + ":" + ((DateTime)Get(last, "At")).Ticks) + "|" +
            outcomes.Count + "|" + (outcomes.Count == 0 ? "" : S(outcomes[outcomes.Count - 1], "Id")) + "|" + positions.Count + "|" + ledger.Revision + "|" + ledger.ReadOnly +
            "|" + revision + "|" + count;
    }

    internal static void AttachOutcomeObserver()
    {
        try
        {
            Api.Postfix(admiraltyQueue, typeof(WorldOperations), nameof(Queued), "io.github.sest-hobby.world-admiralty-outcome");
            Api.Log("World Operations records each Admiralty result when Dynamic Campaign Mod files it; unread papers are also scanned");
        }
        catch (Exception ex)
        {
            Api.LogFailure("Admiralty filing observation unavailable; unread papers are still recorded", ex);
        }
    }

    // Postfix on DCM's Admiralty.Queue(OrderOutcome). Only the reference and
    // its campaign are kept; nothing of the outcome is read here. Never throws
    // into DCM's simulation.
    internal static void Queued(object __instance, object __0)
    {
        try
        {
            if (stopped || __instance == null || __0 == null) return;
            object filedState = Get(__instance, "_state");
            if (filedState == null) return;
            string filedSide = S(filedState, "PlayerSideId");
            // The current campaign's own definition when it is the live one,
            // so these keys match the unread scan's exactly.
            object filedDefinition = ReferenceEquals(filedState, state) && definition != null ? definition : Get(filedState, "Definition");
            var entry = new Filed { Outcome = __0, Scope = S(filedDefinition, "id") + ":" + filedSide, Side = filedSide };
            lock (filedLock)
            {
                if (filed.Count >= FiledLimit)
                {
                    filed.RemoveAt(0);
                    if (!filedDropReported) { filedDropReported = true; Api.Log("World Operations: more than " + FiledLimit + " Admiralty results waiting; the oldest is left to the unread-paper scan"); }
                }
                filed.Add(entry);
                filedRevision++;
            }
        }
        catch (Exception ex)
        {
            if (!filedFailureReported) { filedFailureReported = true; Api.LogFailure("Admiralty result not observed; unread papers are still recorded", ex); }
        }
    }

    private static List<Filed> TakeFiled()
    {
        lock (filedLock) return filed.ToList();
    }

    private static void ReleaseFiled(List<Filed> taken)
    {
        if (taken.Count == 0) return;
        var done = new HashSet<object>(taken, SameObject.Instance);
        lock (filedLock) filed.RemoveAll(f => done.Contains(f));
    }

    // When the campaign closes before the next sample: record what was filed,
    // each under the campaign it was filed in.
    private static void FlushFiled()
    {
        int count;
        lock (filedLock) count = filed.Count;
        if (count == 0 || ledger == null || Now < nextMerge) return;
        var taken = TakeFiled();
        try
        {
            ledger.Merge(AdmiraltyEvidence(new List<object>(), "", "", taken));
            ReleaseFiled(taken);
            mergeReported = false;
        }
        catch (Exception ex)
        {
            nextMerge = Now + 30;
            if (!mergeReported) { mergeReported = true; Api.LogFailure("world service record not updated; filed Admiralty results are retried in 30 s", ex); }
        }
    }

    // The unread papers in this save, then every result filed since the last
    // merge, each outcome once and under the unchanged keys and rules.
    internal static List<WorldServiceLedger.Entry> AdmiraltyEvidence(IEnumerable<object> unread, string campaignScope, string playerSide, IEnumerable<Filed> taken)
    {
        var seen = new HashSet<object>(SameObject.Instance);
        var events = new List<WorldServiceLedger.Entry>();
        void Add(object outcome, string inScope, string inSide)
        {
            if (outcome == null || !seen.Add(outcome)) return;
            var entry = CompletedOrder(outcome, inScope, inSide) ?? CompletedOperation(outcome, inScope, inSide);
            // A result Runtime 1.6.3 already recorded under its outcome key
            // keeps that single entry.
            if (entry != null && !ledger.Contains(LegacyOrderKey(outcome, inScope))) events.Add(entry);
        }
        foreach (var outcome in unread) Add(outcome, campaignScope, playerSide);
        foreach (var f in taken) Add(f.Outcome, f.Scope, f.Side);
        return events;
    }

    // A standalone Admiralty order's result: DCM's Paper(AdmiraltyOrder) sets
    // OrderId and leaves OperationId 0. Phases of an operation are never
    // papered (Admiralty.End skips Paper when OperationId != 0).
    internal static WorldServiceLedger.Entry CompletedOrder(object outcome, string campaignScope, string playerSide)
    {
        if (!Completed(outcome, playerSide) || Convert.ToInt32(Get(outcome, "OrderId")) <= 0 || Convert.ToInt32(Get(outcome, "OperationId")) != 0) return null;
        return TaskEvidence(outcome, campaignScope, WorldServiceLedger.OrderPrefix, S(outcome, "Kind"), Convert.ToInt32(Get(outcome, "OrderId")));
    }

    // A whole multi-phase operation's result: Paper(AdmiraltyOperation) sets
    // OperationId and Template and leaves OrderId 0. It is papered once, when
    // the final phase completes, so each operation counts once.
    internal static WorldServiceLedger.Entry CompletedOperation(object outcome, string campaignScope, string playerSide)
    {
        if (!Completed(outcome, playerSide) || Convert.ToInt32(Get(outcome, "OrderId")) != 0 || Convert.ToInt32(Get(outcome, "OperationId")) <= 0) return null;
        return TaskEvidence(outcome, campaignScope, WorldServiceLedger.OperationPrefix, S(outcome, "Template"), Convert.ToInt32(Get(outcome, "OperationId")));
    }

    private static bool Completed(object outcome, string playerSide)
    {
        if (outcome == null || S(outcome, "SideId") != playerSide || S(outcome, "Status") != "Completed" || (bool)Get(outcome, "Moot") ||
            Convert.ToInt32(Get(outcome, "Id")) <= 0) return false;
        var issued = (DateTime)Get(outcome, "Issued");
        // Accepting sets Issued; an order DCM completed while still only on
        // offer has its Issued reset to default (Admiralty.OnCaptured).
        return issued != DateTime.MinValue && (DateTime)Get(outcome, "At") >= issued;
    }

    // Keyed on the order or operation and its acceptance time, both kept in
    // saves, so a completion replayed after reloading counts once (WSA-6).
    private static WorldServiceLedger.Entry TaskEvidence(object outcome, string campaignScope, string prefix, string kind, int id) => new WorldServiceLedger.Entry {
        Scope = campaignScope,
        Key = campaignScope + prefix + kind + ":" + id + ":" + ((DateTime)Get(outcome, "Issued")).Ticks,
        At = ((DateTime)Get(outcome, "At")).Ticks, Manual = false, Where = Clean(Get(outcome, "Title"), 512), Theatre = ""
    };

    internal static string LegacyOrderKey(object outcome, string campaignScope) =>
        campaignScope + WorldServiceLedger.LegacyOrderPrefix + S(outcome, "Kind") + ":" + Convert.ToInt32(Get(outcome, "Id")) + ":" + ((DateTime)Get(outcome, "At")).Ticks;

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

    private static string Subtitle() => campaignName + " | " + ((DateTime)Get(state, "Now")).ToString("d MMM yyyy HH:mm", CultureInfo.InvariantCulture) + " | F11 closes | Drag title bar to move";

    // What the open tab shows, without building it. The campaign clock is
    // excluded: it is shown in the bound subtitle.
    internal static string Signature()
    {
        var b = new StringBuilder(scope).Append('|').Append(Tab).Append('|').Append(campaignName);
        int Size(string field) => (Get(state, field) as ICollection)?.Count ?? -1;
        switch (Tab)
        {
            case 0:
                b.Append('|').Append(Dict(Get(state, "Points"), side)).Append('|').Append(Lookup(Get(state, "Renown"), side)).Append('|').Append(Lookup(Get(state, "Ranks"), side));
                var owners = Get(state, "BaseOwner") as IDictionary;
                b.Append('|').Append(owners == null ? 0 : owners.Values.Cast<object>().Count(x => Convert.ToString(x) == side));
                b.Append('|').Append(Size("TaskForces")).Append('|').Append(Size("Squadrons")).Append('|').Append(Size("BuildOrders")).Append('|').Append(Size("Operations"));
                foreach (var order in Rows(Get(state, "AdmiraltyOrders"))) b.Append('|').Append(S(order, "Id")).Append(':').Append(S(order, "Status"));
                break;
            case 1:
                // A snapshot: rebuilt when task forces or squadrons are added
                // or removed, or when Forces is selected again.
                b.Append('|').Append(Size("TaskForces")).Append('|').Append(Size("Squadrons")).Append('|').Append(mapPrices != null);
                break;
            case 2:
                var games = CombatHistory.Games;
                b.Append('|').Append(Dict(Get(state, "Points"), side)).Append('|').Append(ledger.Revision).Append('|').Append(ledger.ReadOnly).Append('|').Append(liveReports.Count)
                 .Append('|').Append(games.Count).Append('|').Append(games.Count == 0 ? "" : games[0].Id + ":" + games[0].EndedUtc).Append('|').Append(mapPrices != null);
                break;
            case 3:
                b.Append('|').Append(ledger.Revision).Append('|').Append(ledger.ReadOnly);
                break;
        }
        return b.ToString();
    }

    private static CombatPrices MapPrices() => mapPrices ?? (mapPrices = CampaignCosts.Catalogue());

    private static CampaignCosts.CostView View()
    {
        var v = new CampaignCosts.CostView { Title = Tab == 2 ? "CUMULATIVE COMBAT COSTS" : "WORLD CAMPAIGN OPERATIONS", Subtitle = Subtitle(), World = true };
        v.Notes[0] = "Campaign credits and USD catalogue estimates are separate. Orders and purchases stay in the native campaign panels.";
        v.Notes[1] = "Service record belongs to this profile and coalition across saves. Native commander records and saves are unchanged.";
        v.Notes[2] = "";
        v.AddSummary(CostLineKind.Basis, "Coalition " + side + " | " + new[] { "Overview", "Forces", "Combat Costs", "Service" }[Tab]);
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
        v.AddDetail(CostLineKind.Body, "Dynamic Campaign Mod: connected | Campaign map integration: active");
        if (integrations == null)
        {
            string[] types = { "WeaponCostsMod.Overlay", "SeaPowerTopo.Plugin", "IdentifyExpanded.Plugin" };
            string[] names = { "Combat Cost Tracker", "Topographic Map", "Identify Expanded" };
            var assemblies = AppDomain.CurrentDomain.GetAssemblies();
            // A loaded assembly alone does not prove the author's entrypoint ran.
            integrations = types.Select((t, i) => names[i] + ": " + (assemblies.Any(a => a.GetType(t, false) != null) ? "assembly detected; check its in-game controls" : "not detected by this panel")).ToArray();
        }
        foreach (var line in integrations) v.AddDetail(CostLineKind.Item, line);
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
        v.AddDetail(CostLineKind.Body, "RENOWN AND BUDGET: battle results and completed, accepted Admiralty tasks. Look for escort, area-control, shadowing and multi-phase assignments when offered. Read each task's conditions; routine movement or ending a battle alone earns no task reward. SEST's Admiralty service ribbons (Service tab) count each completed standalone order, and each whole operation once its final phase completes.");
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
        var prices = MapPrices();
        var total = new CombatAmount();
        int ships = 0, airframes = 0;
        v.AddDetail(CostLineKind.Basis, "Snapshot at " + ((DateTime)Get(state, "Now")).ToString("d MMM yyyy HH:mm", CultureInfo.InvariantCulture) + ". Select Forces again to refresh fuel, damage and readiness.");
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
        // Profile record plus the loaded save's own reports: a read-only or
        // unwritable record cannot hide this campaign's costs (RU-7).
        var completed = ledger.Entries.Where(e => e.Scope == scope && e.Manual).Concat(liveReports.Where(e => e.Scope == scope))
            .GroupBy(e => e.Key, StringComparer.Ordinal).Select(g => g.First()).ToList();
        var games = RecordedGames(CombatHistory.Games, completed, scope);
        if (ledger.ReadOnly) v.AddDetail(CostLineKind.Body, "The profile service record is read-only because its saved format could not be validated; the file is kept unchanged. Costs below use this save's battle reports.");
        v.AddDetail(CostLineKind.Basis, completed.Count + " completed manual battle reports | " + games.Count + " with SEST itemised cost history. Reloaded attempts use the latest record for the same engagement.");
        var costs = CampaignCosts.PricedCampaignView(games, MapPrices());
        foreach (var row in costs.SummaryRows) v.AddSummary(row.Kind, row.Text);
        foreach (var row in costs.DetailRows) v.AddDetail(row.Kind, row.Text);
        v.Notes[0] = "USD totals cover SEST-recorded battles for this campaign and coalition across saves. Older battles and auto-resolved battles may lack itemised USD evidence.";
        v.Notes[1] = costs.Notes[1]; v.Notes[2] = costs.Notes[2];
    }

    internal static List<CombatGameRecord> RecordedGames(IEnumerable<CombatGameRecord> history, IEnumerable<WorldServiceLedger.Entry> reports, string scope)
    {
        var keys = new HashSet<string>(reports.Where(e => e.Scope == scope && e.Manual).Select(e => e.Key), StringComparer.Ordinal);
        // A record with no sides is a fragment (restart, or End battle while
        // loading); it must not outrank the attempt that has costs (RU-12).
        var games = history.Where(g => g.Sides.Count > 0 && g.Source.StartsWith("DCM:" + scope + ":", StringComparison.Ordinal))
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
        var tasks = ledger.AdmiraltyTasks(scope);
        int operations = tasks.Count(t => t.Operation);
        v.AddSummary(CostLineKind.Basis, "Fictional SEST profile awards | " + ledger.Entries.Count(e => e.Scope == scope && e.Manual) + " manual battles | " + tasks.Count + " qualifying Admiralty tasks (" + (tasks.Count - operations) + " orders, " + operations + " operations)");
        if (ledger.ReadOnly) v.AddDetail(CostLineKind.Body, "Service record is read-only because its saved format could not be validated. The existing file has been retained.");
        foreach (var r in ribbons.OrderByDescending(r => r.Earned))
        {
            string name = r.Name + " | " + (r.Earned ? "AWARDED" : r.Progress + "/" + r.Required);
            v.Details.Add(name);
            v.DetailRows.Add(new CostReportLine(r.Earned ? CostLineKind.Ribbon : CostLineKind.Mission, name, r.Earned ? r.Colours : null));
            v.AddDetail(CostLineKind.Breakdown, r.Citation);
        }
        v.AddDetail(CostLineKind.Section, "CITATION AND EVIDENCE");
        v.AddDetail(CostLineKind.Body, "Battle service counts completed manual reports; auto-resolved battles do not qualify. Theatre awards require observed battle coordinates. Watch ribbons count distinct campaign calendar days with a manual battle.");
        v.AddDetail(CostLineKind.Body, "Admiralty ribbons count accepted tasks that Dynamic Campaign Mod reports as completed: each standalone order once, and each multi-phase operation once when its final phase completes (its phases are not counted separately). Convoy Protection counts convoy-escort orders and convoy-run operations; Route Security counts convoy-run operations, whose first phase clears the convoy's route; Maritime Surveillance counts shadowing orders and fleet-action operations, which open with a shadowing phase. Sea-control and amphibious operations count towards the Commendation and Versatility. Failed, lapsed, declined and cancelled tasks do not count.");
        v.AddDetail(CostLineKind.Body, "SEST records each result when Dynamic Campaign Mod files it, whether or not its paper has been read (Runtime 1.6.5 and later). Earlier results count only if their paper was still unread under a Runtime that recorded them (orders from 1.6.3, operations from 1.6.4). A completion replayed after reloading a save counts once.");
        v.AddDetail(CostLineKind.Body, "Campaign, operation and real national award representations appear in Task Force Service Records. National awards use scenario qualifications and commander-nation filters. World service awards do not add renown, credits or supplies. Unrecorded bravery, logistics or ROE conditions are not inferred from spending.");
    }
}
