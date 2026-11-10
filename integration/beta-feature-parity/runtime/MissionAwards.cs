using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Text;
using SeapowerUI.ViewModels;

namespace Sest.RuntimeFixes;

// Beta 499675cd only (RuntimeFixesMod's native gate): SEST runtime mission
// ribbons. A campaign names them in its own key, which the game ignores:
//
//   [Mission<N>]
//   SestRuntimeRibbonAwards=<spec>[|<spec>...]
//   <spec>  = <ribbonId>[,<NationKey>...]?<term>[&<term>...]
//   <term>  = objective:<ObjectiveId>=completed|failed|cancelled|notfailed
//           | result>=<MissionDebriefViewModel.Result name>   e.g. result>=CostlyVictory
//           | nolaunch     no player weapon launched and no gun round fired;
//                          noisemakers, chaff, decoys (MOSS), sonobuoys and CIWS rounds excepted
//           | rescued>=<1-999>   survivors recovered by the player's task force
//
// The part before '?' is parsed by the native TryParseMissionRibbonAwardSpec
// and filtered by the native AllowsCommanderNation, so nation selectors mean
// exactly what they mean in TaskForceModeRibbonAwards (TaskForceCommanderNation).
// ';', '#' and '//' start an INI comment and must not appear in the value.
// Several specs may name one ribbon: the first that qualifies grants it.
//
// The native debrief snapshot grants its mission ribbons only after its own
// completion gate. A postfix on that grant adds each qualifying runtime ribbon
// as one more native award row, so the debrief rows, the commander's
// TaskForceCommanderRibbons set and the campaign save carry it exactly as a
// native award; the definition is the campaign's [Ribbon_<id>]. Rows are
// rewritten for each completion and the persistent set is distinct, so a
// ribbon is never held twice. Any binding or evaluation fault disables the
// feature for the session; native awards are always kept.
internal static class MissionAwards
{
    internal const string Key = "SestRuntimeRibbonAwards";
    private const string HarmonyId = "io.github.sest-hobby.mission-awards";
    private const int MaxSpecs = 32, MaxValue = 4096;

    internal enum TermKind { Objective, ResultAtLeast, NoLaunch, RescuedAtLeast }

    internal enum ObjectiveState { InProgress, Completed, Failed, Cancelled }

    internal sealed class Term
    {
        internal TermKind Kind;
        internal string Id = "", Text = "";
        internal ObjectiveState Want;
        internal bool NotFailed;
        internal int Number;
    }

    internal sealed class RuntimeSpec
    {
        internal string Raw, RibbonId;
        internal object Native;
        internal List<Term> Terms;
    }

    internal sealed class Evidence
    {
        internal int Index, Result, Rescued;
        internal string ResultName = "", Nation = "";
        internal readonly Dictionary<string, ObjectiveState> Objectives = new Dictionary<string, ObjectiveState>(StringComparer.OrdinalIgnoreCase);
        internal long OffensiveLaunched, OffensiveRounds, AllLaunched, AllRounds;
        internal bool WeaponsKnown;
        internal bool NoLaunch => WeaponsKnown && OffensiveLaunched == 0 && OffensiveRounds == 0;

        internal string Summary()
        {
            var b = new StringBuilder("result=").Append(ResultName).Append(", objectives=");
            b.Append(Objectives.Count == 0 ? "none" : string.Join(",", Objectives.Select(o => o.Key + ":" + o.Value)));
            b.Append(", launched=").Append(WeaponsKnown ? OffensiveLaunched.ToString(CultureInfo.InvariantCulture) : "unknown");
            b.Append(", rounds=").Append(WeaponsKnown ? OffensiveRounds.ToString(CultureInfo.InvariantCulture) : "unknown");
            if (WeaponsKnown) b.Append(" (all launched=").Append(AllLaunched).Append(", rounds=").Append(AllRounds).Append(')');
            b.Append(", rescued=").Append(Rescued).Append(", nation=").Append(Nation.Length == 0 ? "none" : Nation);
            return b.Length > 600 ? b.ToString(0, 600) : b.ToString();
        }
    }

    private sealed class Snapshot
    {
        internal object Mission, Debrief;
        internal int Index;
    }

    [ThreadStatic] private static Snapshot current;
    private static bool active;
    private static MethodInfo snapshotTarget, applyTarget, ruleSources, parseNative, readDefinition, addRows, allows, toRow, commanderNation, commanderState, readValue;
    private static PropertyInfo specId, stateRank, rankName, persistentData, managerObjectives, missionResult, survivorsRescued, debriefObjectives, unitsByReportId, unitAmmo, launched, projectileFired, ciwsRounds, ammoType, ammoSubType;
    private static FieldInfo campaignInstance, managerInstance, missionIndex, objectiveId, isCompleted, isFailed, isCanceled, completeOnEnd, failOnEnd, playerTaskforce, weaponReport;
    private static Type resultType;
    private static HashSet<int> exempt;

    private static FieldInfo Field(Type type, string name, Type expected)
    {
        FieldInfo field = type.GetField(name, Api.All);
        if (field == null || field.FieldType != expected) throw new MissingFieldException(type.FullName, name);
        return field;
    }

    private static PropertyInfo Property(Type type, string name, Type expected)
    {
        PropertyInfo property = type.GetProperty(name, Api.All);
        if (property == null || property.PropertyType != expected || property.GetGetMethod(true) == null) throw new MissingMemberException(type.FullName, name);
        return property;
    }

    internal static void Bind(Assembly game)
    {
        active = false;
        Type ini = Api.Type(game, "SeaPower.IniHandler");
        Type mission = Api.Type(game, "SeaPower.LinearCampaignMission");
        Type debrief = Api.Type(game, "SeapowerUI.ViewModels.MissionDebriefViewModel");
        Type rules = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceRibbonRules");
        Type spec = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceRibbonRules+MissionRibbonAwardSpec");
        Type definition = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceRibbonRules+LinearCampaignTaskForceRibbonDefinition");
        Type manager = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceCommanderManager");
        Type state = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceCommanderState");
        Type rank = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceCommanderRank");
        Type campaign = Api.Type(game, "SeaPower.LinearCampaign");
        Type missionManager = Api.Type(game, "SeaPower.MissionManager");
        Type objective = Api.Type(game, "SeaPower.MissionManager+MissionObjective");
        Type taskforce = Api.Type(game, "SeaPower.Taskforce");
        Type report = Api.Type(game, "SeaPower.TaskforceWeaponReport");
        Type unit = Api.Type(game, "SeaPower.WeaponReportUnitData");
        Type ammo = Api.Type(game, "SeaPower.WeaponReportAmmoData");
        Type kind = Api.Type(game, "SeaPower.Ammunition+Type");
        Type singleton = Api.Type(game, "SeaPower.Singleton`1");
        Type persistent = typeof(IDictionary<string, string>);
        if (Api.Type(game, typeof(LinearCampaignTaskForceRibbonAwardRow).FullName) != typeof(LinearCampaignTaskForceRibbonAwardRow))
            throw new MissingMemberException("native ribbon award row type");
        Type rows = typeof(IReadOnlyList<LinearCampaignTaskForceRibbonAwardRow>);
        snapshotTarget = Api.Method(Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel"), "SaveDebriefSnapshot", typeof(void), mission, debrief);
        applyTarget = Api.Method(rules, "ApplyMissionRibbonAwards", rows, ini, typeof(int), typeof(string));
        ruleSources = Api.Method(rules, "EnumerateCampaignRuleSources", typeof(IEnumerable<>).MakeGenericType(ini), ini);
        parseNative = Api.Method(rules, "TryParseMissionRibbonAwardSpec", spec, typeof(string));
        readDefinition = Api.Method(rules, "ReadRibbonDefinition", definition, ini, typeof(string));
        addRows = Api.Method(rules, "AddPersistentCommanderRibbonRows", typeof(void), persistent, typeof(IEnumerable<LinearCampaignTaskForceRibbonAwardRow>));
        allows = Api.Method(spec, "AllowsCommanderNation", typeof(bool), typeof(string));
        toRow = Api.Method(definition, "ToAwardRow", typeof(LinearCampaignTaskForceRibbonAwardRow), typeof(int), typeof(int), typeof(string), typeof(string));
        commanderNation = Api.Method(manager, "GetCommanderNation", typeof(string), persistent);
        commanderState = Api.Method(manager, "ReadCommanderState", state, ini, persistent);
        readValue = Api.Method(ini, "readValue", typeof(string), typeof(string), typeof(string), typeof(string), typeof(bool));
        specId = Property(spec, "RibbonId", typeof(string));
        stateRank = Property(state, "Rank", rank);
        rankName = Property(rank, "DisplayName", typeof(string));
        persistentData = Property(campaign, "PersistentData", typeof(Dictionary<string, string>));
        // The static instance fields, read directly: Singleton.get_Instance can
        // create a GameObject. The native grant has just called it.
        campaignInstance = Field(singleton.MakeGenericType(campaign), "_instance", campaign);
        managerInstance = Field(singleton.MakeGenericType(missionManager), "_instance", missionManager);
        managerObjectives = missionManager.GetProperty("Objectives", Api.All);
        if (managerObjectives == null || !typeof(IEnumerable).IsAssignableFrom(managerObjectives.PropertyType)) throw new MissingMemberException(missionManager.FullName, "Objectives");
        objectiveId = Field(objective, "_id", typeof(string));
        isCompleted = Field(objective, "_isCompleted", typeof(bool));
        isFailed = Field(objective, "_isFailed", typeof(bool));
        isCanceled = Field(objective, "_isCanceled", typeof(bool));
        completeOnEnd = Field(objective, "_completeOnMissionEnd", typeof(bool));
        failOnEnd = Field(objective, "_failOnMissionEnd", typeof(bool));
        missionIndex = Field(mission, "_index", typeof(int));
        resultType = Api.Type(game, "SeapowerUI.ViewModels.MissionDebriefViewModel+Result");
        missionResult = Property(debrief, "MissionResult", resultType);
        survivorsRescued = Property(debrief, "PlayerSurvivorsRescued", typeof(int));
        debriefObjectives = Property(debrief, "MissionObjectives", typeof(List<>).MakeGenericType(objective));
        playerTaskforce = Field(Api.Type(game, "SeaPower.Globals"), "_playerTaskforce", taskforce);
        weaponReport = Field(taskforce, "_weaponReport", report);
        unitsByReportId = Property(report, "UnitsByReportId", typeof(Dictionary<,>).MakeGenericType(typeof(string), unit));
        unitAmmo = Property(unit, "Ammo", typeof(Dictionary<,>).MakeGenericType(typeof(string), ammo));
        launched = Property(ammo, "Launched", typeof(int));
        projectileFired = Property(ammo, "ProjectileFired", typeof(int));
        ciwsRounds = Property(ammo, "CiwsRoundsFired", typeof(int));
        ammoType = Property(ammo, "AmmoType", kind);
        ammoSubType = Property(ammo, "AmmoSubType", kind);
        // Not weapon launches: countermeasures, decoys, sonobuoys, troops and
        // fuel tanks (the native report already ignores fuel tanks).
        exempt = new HashSet<int>(new[] { "Noisemaker", "Chaff", "MOSS", "Sonobuoy", "Paratrooper", "Fueltank" }.Select(n => Convert.ToInt32(Enum.Parse(kind, n), CultureInfo.InvariantCulture)));
        active = true;
    }

    internal static void Install(Assembly game)
    {
        Bind(game);
        try
        {
            Api.Hooks(snapshotTarget, typeof(MissionAwards), nameof(BeforeSnapshot), null, HarmonyId, nameof(AfterSnapshot));
            Api.Postfix(applyTarget, typeof(MissionAwards), nameof(AfterApply), HarmonyId);
        }
        catch
        {
            active = false;
            throw;
        }
        Api.Log("runtime mission awards installed: [Mission<N>] " + Key + " ribbons are granted through the native debrief award after its completion gate");
    }

    private static void Disable(Exception error)
    {
        active = false;
        current = null;
        Api.LogFailure("runtime mission awards disabled for this session; native awards retained", error);
    }

    internal static void BeforeSnapshot(object __0, object __1)
    {
        current = null;
        if (!active || __0 == null || __1 == null) return;
        try
        {
            current = new Snapshot { Mission = __0, Debrief = __1, Index = (int)missionIndex.GetValue(__0) };
        }
        catch (Exception error)
        {
            Disable(error);
        }
    }

    internal static Exception AfterSnapshot(Exception __exception)
    {
        current = null;
        return __exception;
    }

    internal static void AfterApply(object __0, int __1, string __2, ref IReadOnlyList<LinearCampaignTaskForceRibbonAwardRow> __result)
    {
        Snapshot snapshot = current;
        if (!active || snapshot == null || __0 == null || __1 < 1 || snapshot.Index != __1) return;
        current = null;
        try
        {
            IReadOnlyList<LinearCampaignTaskForceRibbonAwardRow> merged = Grant(__0, __1, __2, snapshot.Debrief, __result ?? Array.Empty<LinearCampaignTaskForceRibbonAwardRow>());
            if (merged != null) __result = merged;
        }
        catch (Exception error)
        {
            Disable(error);
        }
    }

    // The key as the native reader finds its own: [Mission<N>] first, then the
    // event's section, in every campaign rule source.
    internal static List<string> ReadValues(object ini, int index, string section)
    {
        var values = new List<string>();
        string mission = "Mission" + index.ToString(CultureInfo.InvariantCulture);
        foreach (object source in (IEnumerable)ruleSources.Invoke(null, new object[] { ini }))
        {
            if (source == null) continue;
            string value = (string)readValue.Invoke(source, new object[] { mission, Key, "", false });
            if (string.IsNullOrWhiteSpace(value) && !string.IsNullOrWhiteSpace(section))
                value = (string)readValue.Invoke(source, new object[] { section, Key, "", false });
            if (!string.IsNullOrWhiteSpace(value)) values.Add(value.Trim());
        }
        return values;
    }

    private static IReadOnlyList<LinearCampaignTaskForceRibbonAwardRow> Grant(object ini, int index, string section, object debrief, IReadOnlyList<LinearCampaignTaskForceRibbonAwardRow> native)
    {
        List<string> values = ReadValues(ini, index, section);
        if (values.Count == 0) return null;
        List<RuntimeSpec> specs = ParseSpecs(values, out string error);
        if (error != null)
        {
            Api.Log("debrief mission " + index + ": " + Key + " not evaluated, " + error + "; no runtime award, native awards retained");
            return null;
        }
        object owner = campaignInstance.GetValue(null);
        var data = owner == null ? null : (IDictionary<string, string>)persistentData.GetValue(owner, null);
        string nation = (string)commanderNation.Invoke(null, new object[] { data }) ?? "";
        object state = commanderState.Invoke(null, new object[] { ini, data });
        object rank = state == null ? null : stateRank.GetValue(state, null);
        string rankText = (rank == null ? null : (string)rankName.GetValue(rank, null)) ?? "";
        Evidence evidence = Collect(index, debrief, nation, PlayerWeaponReport());
        List<LinearCampaignTaskForceRibbonAwardRow> extra = Evaluate(specs, native, evidence, id =>
        {
            object definition = readDefinition.Invoke(null, new object[] { ini, id });
            return definition == null ? null : (LinearCampaignTaskForceRibbonAwardRow)toRow.Invoke(definition, new object[] { 1, index, rankText, "" });
        }, line => Api.Log("debrief mission " + index + ": " + line));
        if (extra.Count == 0) return null;
        List<LinearCampaignTaskForceRibbonAwardRow> merged = Merge(native, extra);
        // The native set union; null data is ignored as the native grant does.
        addRows.Invoke(null, new object[] { data, extra });
        return merged;
    }

    // One line per spec. Returns the new rows in spec order.
    internal static List<LinearCampaignTaskForceRibbonAwardRow> Evaluate(List<RuntimeSpec> specs, IReadOnlyList<LinearCampaignTaskForceRibbonAwardRow> native, Evidence evidence,
        Func<string, LinearCampaignTaskForceRibbonAwardRow> rowFor, Action<string> log)
    {
        var held = new HashSet<string>(native.Where(r => r != null).Select(r => r.Id ?? ""), StringComparer.OrdinalIgnoreCase);
        var extra = new List<LinearCampaignTaskForceRibbonAwardRow>();
        foreach (RuntimeSpec spec in specs)
        {
            string verdict;
            if (held.Contains(spec.RibbonId)) verdict = "already awarded";
            else if (!(bool)allows.Invoke(spec.Native, new object[] { evidence.Nation })) verdict = "not for this commander nation";
            else if (!Qualifies(spec.Terms, evidence, out string unmet)) verdict = "not met: " + unmet;
            else
            {
                LinearCampaignTaskForceRibbonAwardRow row = rowFor(spec.RibbonId);
                if (row == null) verdict = "not awarded: no [Ribbon_" + spec.RibbonId + "] definition";
                else
                {
                    extra.Add(row);
                    held.Add(spec.RibbonId);
                    verdict = "AWARDED";
                }
            }
            log("runtime ribbon " + spec.RibbonId + " " + verdict + " | " + spec.Raw + " | " + evidence.Summary());
        }
        return extra;
    }

    // The native order: Precedence, then DisplayName ignoring case (stable).
    internal static List<LinearCampaignTaskForceRibbonAwardRow> Merge(IEnumerable<LinearCampaignTaskForceRibbonAwardRow> native, IEnumerable<LinearCampaignTaskForceRibbonAwardRow> extra) =>
        native.Concat(extra).OrderBy(r => r.Precedence).ThenBy(r => r.DisplayName, StringComparer.OrdinalIgnoreCase).ToList();

    // Fail closed: one bad spec rejects the whole key.
    internal static List<RuntimeSpec> ParseSpecs(IEnumerable<string> values, out string error)
    {
        error = null;
        var specs = new List<RuntimeSpec>();
        foreach (string value in values)
        {
            if (value.Length > MaxValue) { error = "value longer than " + MaxValue + " characters"; return specs; }
            foreach (string piece in value.Split('|'))
            {
                string raw = piece.Trim();
                if (raw.Length == 0) continue;
                RuntimeSpec spec = ParseSpec(raw, out error);
                if (spec == null) { error = "spec '" + raw + "' " + error; return new List<RuntimeSpec>(); }
                specs.Add(spec);
                if (specs.Count > MaxSpecs) { error = "more than " + MaxSpecs + " specs"; return new List<RuntimeSpec>(); }
            }
        }
        return specs;
    }

    private static RuntimeSpec ParseSpec(string raw, out string error)
    {
        int split = raw.IndexOf('?');
        if (split < 0) { error = "has no '?' conditions"; return null; }
        object native = parseNative.Invoke(null, new object[] { raw.Substring(0, split).Trim() });
        string id = native == null ? null : (string)specId.GetValue(native, null);
        if (string.IsNullOrWhiteSpace(id)) { error = "has no ribbon id"; return null; }
        var terms = new List<Term>();
        foreach (string piece in raw.Substring(split + 1).Split('&'))
        {
            Term term = ParseTerm(piece.Trim());
            if (term == null) { error = "has an unknown or invalid condition '" + piece.Trim() + "'"; return null; }
            terms.Add(term);
        }
        error = null;
        return new RuntimeSpec { Raw = raw, Native = native, RibbonId = id, Terms = terms };
    }

    private static Term ParseTerm(string text)
    {
        string lower = text.ToLowerInvariant();
        if (lower == "nolaunch") return new Term { Kind = TermKind.NoLaunch, Text = "nolaunch" };
        if (lower.StartsWith("objective:", StringComparison.Ordinal))
        {
            string rest = text.Substring("objective:".Length);
            int eq = rest.IndexOf('=');
            if (eq <= 0) return null;
            string id = rest.Substring(0, eq).Trim();
            string want = rest.Substring(eq + 1).Trim().ToLowerInvariant();
            if (id.Length == 0) return null;
            var term = new Term { Kind = TermKind.Objective, Id = id, Text = "objective:" + id + "=" + want };
            switch (want)
            {
                case "completed": term.Want = ObjectiveState.Completed; break;
                case "failed": term.Want = ObjectiveState.Failed; break;
                case "cancelled": term.Want = ObjectiveState.Cancelled; break;
                case "notfailed": term.NotFailed = true; break;
                default: return null;
            }
            return term;
        }
        if (lower.StartsWith("result>=", StringComparison.Ordinal))
        {
            string name = text.Substring("result>=".Length).Trim();
            string match = Enum.GetNames(resultType).FirstOrDefault(n => string.Equals(n, name, StringComparison.OrdinalIgnoreCase));
            if (match == null) return null;
            return new Term { Kind = TermKind.ResultAtLeast, Number = Convert.ToInt32(Enum.Parse(resultType, match), CultureInfo.InvariantCulture), Id = match, Text = "result>=" + match };
        }
        if (lower.StartsWith("rescued>=", StringComparison.Ordinal))
        {
            if (!int.TryParse(text.Substring("rescued>=".Length).Trim(), NumberStyles.None, CultureInfo.InvariantCulture, out int count) || count < 1 || count > 999) return null;
            return new Term { Kind = TermKind.RescuedAtLeast, Number = count, Text = "rescued>=" + count };
        }
        return null;
    }

    internal static bool Qualifies(List<Term> terms, Evidence evidence, out string unmet)
    {
        foreach (Term term in terms)
        {
            bool ok;
            string actual;
            switch (term.Kind)
            {
                case TermKind.Objective:
                    bool known = evidence.Objectives.TryGetValue(term.Id, out ObjectiveState state);
                    ok = known && (term.NotFailed ? state != ObjectiveState.Failed : state == term.Want);
                    actual = known ? state.ToString() : "not in this mission";
                    break;
                case TermKind.ResultAtLeast:
                    ok = evidence.Result >= term.Number;
                    actual = evidence.ResultName;
                    break;
                case TermKind.NoLaunch:
                    ok = evidence.NoLaunch;
                    actual = evidence.WeaponsKnown ? "launched " + evidence.OffensiveLaunched + ", rounds " + evidence.OffensiveRounds : "weapon report unavailable";
                    break;
                case TermKind.RescuedAtLeast:
                    ok = evidence.Rescued >= term.Number;
                    actual = "rescued " + evidence.Rescued;
                    break;
                default:
                    ok = false;
                    actual = "unknown";
                    break;
            }
            if (!ok)
            {
                unmet = term.Text + " (" + actual + ")";
                return false;
            }
        }
        unmet = null;
        return true;
    }

    // The native debrief precedence (MissionDebriefViewModel.CalculateEndMissionData).
    internal static ObjectiveState StateOf(object objective)
    {
        if ((bool)isCanceled.GetValue(objective)) return ObjectiveState.Cancelled;
        if ((bool)isFailed.GetValue(objective)) return ObjectiveState.Failed;
        if ((bool)isCompleted.GetValue(objective)) return ObjectiveState.Completed;
        if ((bool)failOnEnd.GetValue(objective)) return ObjectiveState.Failed;
        if ((bool)completeOnEnd.GetValue(objective)) return ObjectiveState.Completed;
        return ObjectiveState.InProgress;
    }

    // The live Globals._playerTaskforce._weaponReport, which the native
    // snapshot writes to the campaign only after the awards.
    [MethodImpl(MethodImplOptions.NoInlining)]
    internal static object PlayerWeaponReport()
    {
        object taskforce = playerTaskforce.GetValue(null);
        return taskforce == null ? null : weaponReport.GetValue(taskforce);
    }

    internal static Evidence Collect(int index, object debrief, string nation, object report)
    {
        var evidence = new Evidence { Index = index, Nation = nation ?? "" };
        IEnumerable shown = ReadDebrief(debrief, evidence);
        // The mission's full list (hidden objectives too), then the debrief's own.
        object mission = managerInstance.GetValue(null);
        foreach (IEnumerable list in new[] { mission == null ? null : managerObjectives.GetValue(mission, null) as IEnumerable, shown })
        {
            if (list == null) continue;
            foreach (object objective in list)
            {
                string id = objective == null ? null : ((string)objectiveId.GetValue(objective))?.Trim();
                if (!string.IsNullOrEmpty(id) && !evidence.Objectives.ContainsKey(id)) evidence.Objectives.Add(id, StateOf(objective));
            }
        }
        CountWeapons(report, evidence);
        return evidence;
    }

    // The debrief's result, rescued survivors (clamped at 0 as the native
    // snapshot does) and objective list.
    [MethodImpl(MethodImplOptions.NoInlining)]
    internal static IEnumerable ReadDebrief(object debrief, Evidence evidence)
    {
        object result = missionResult.GetValue(debrief, null);
        evidence.Result = Convert.ToInt32(result, CultureInfo.InvariantCulture);
        evidence.ResultName = result.ToString();
        evidence.Rescued = Math.Max(0, (int)survivorsRescued.GetValue(debrief, null));
        return debriefObjectives.GetValue(debrief, null) as IEnumerable;
    }

    // Read-only: no Normalize or BuildTaskforceTotals. Any missing report,
    // negative count, inconsistent CIWS count or overflow leaves the weapons
    // unknown, and nolaunch then fails.
    internal static void CountWeapons(object report, Evidence evidence)
    {
        evidence.WeaponsKnown = false;
        evidence.OffensiveLaunched = evidence.OffensiveRounds = evidence.AllLaunched = evidence.AllRounds = 0;
        var units = report == null ? null : unitsByReportId.GetValue(report, null) as IDictionary;
        if (units == null) return;
        long offensiveLaunched = 0, offensiveRounds = 0, allLaunched = 0, allRounds = 0;
        try
        {
            foreach (object unit in units.Values)
            {
                if (unit == null) continue;
                if (!(unitAmmo.GetValue(unit, null) is IDictionary ammo)) continue;
                foreach (object row in ammo.Values)
                {
                    if (row == null) continue;
                    int l = (int)launched.GetValue(row, null), p = (int)projectileFired.GetValue(row, null), c = (int)ciwsRounds.GetValue(row, null);
                    if (l < 0 || p < 0 || c < 0 || c > p) return;
                    allLaunched = checked(allLaunched + l);
                    allRounds = checked(allRounds + p);
                    if (exempt.Contains(Convert.ToInt32(ammoType.GetValue(row, null), CultureInfo.InvariantCulture)) || exempt.Contains(Convert.ToInt32(ammoSubType.GetValue(row, null), CultureInfo.InvariantCulture))) continue;
                    offensiveLaunched = checked(offensiveLaunched + l);
                    offensiveRounds = checked(offensiveRounds + (p - c));
                }
            }
        }
        catch (OverflowException)
        {
            return;
        }
        evidence.OffensiveLaunched = offensiveLaunched;
        evidence.OffensiveRounds = offensiveRounds;
        evidence.AllLaunched = allLaunched;
        evidence.AllRounds = allRounds;
        evidence.WeaponsKnown = true;
    }
}
