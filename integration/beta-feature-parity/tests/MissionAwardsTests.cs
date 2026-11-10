using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using Mono.Cecil;
using Mono.Cecil.Cil;

// R13 contracts: the native debrief award path that Runtime 1.6.5's mission
// awards extend, the live weapon report and survivor count they read, and the
// Dynamic Campaign Mod filing path World Operations observes. Each check names
// the member it pins, so a later game or DCM image that moves one fails here
// before any PC test. Args: flat references, candidate runtime, Workshop tree.
static partial class MissionAwardsTests
{
    const BindingFlags All = BindingFlags.Instance | BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic;
    const string DcmHash = "eacdb9a4c0353edd24543b631826e61f7cbcfc4f1a78de4fa80527aa5a2208f4";
    static int checks;
    static void Check(bool ok, string why) { checks++; if (!ok) throw new Exception("FAILED: " + why); }

    static string Sha(string path)
    {
        using (var stream = File.OpenRead(path)) using (var sha = System.Security.Cryptography.SHA256.Create())
            return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
    }

    static string Sig(MethodReference m) => m.ReturnType.FullName + "(" + string.Join(",", m.Parameters.Select(p => p.ParameterType.FullName)) + ")";
    static string Owner(MethodReference m) => m.DeclaringType.GetElementType().FullName;
    static string Name(MethodReference m) => Owner(m) + "::" + m.Name;

    static TypeDefinition Type(ModuleDefinition module, string name)
    {
        var type = module.GetType(name);
        Check(type != null, "type " + name);
        return type;
    }

    static MethodDefinition Method(TypeDefinition type, string name, string signature)
    {
        var found = type.Methods.Where(m => m.Name == name && Sig(m) == signature).ToList();
        Check(found.Count == 1, type.FullName + "::" + name + " " + signature);
        return found[0];
    }

    static FieldDefinition Field(TypeDefinition type, string name, string fieldType, bool isStatic = false)
    {
        var field = type.Fields.SingleOrDefault(f => f.Name == name);
        Check(field != null && field.FieldType.FullName == fieldType && field.IsStatic == isStatic, type.FullName + "." + name + " : " + fieldType);
        return field;
    }

    static PropertyDefinition Property(TypeDefinition type, string name, string propertyType)
    {
        var property = type.Properties.SingleOrDefault(p => p.Name == name);
        Check(property != null && property.PropertyType.FullName == propertyType && property.GetMethod != null, type.FullName + "." + name + " : " + propertyType);
        return property;
    }

    static Func<Instruction, bool> Calls(string owner, string name) =>
        i => (i.OpCode.Code == Code.Call || i.OpCode.Code == Code.Callvirt) && i.Operand is MethodReference r && Owner(r) == owner && r.Name == name;
    static Func<Instruction, bool> Op(Code code) => i => i.OpCode.Code == code;

    // Each step must be found after the previous one, in IL order.
    static void InOrder(MethodDefinition method, string what, params Func<Instruction, bool>[] steps)
    {
        var body = method.Body.Instructions;
        int at = 0;
        for (int n = 0; n < steps.Length; n++)
        {
            while (at < body.Count && !steps[n](body[at])) at++;
            Check(at < body.Count, what + " (step " + (n + 1) + " of " + steps.Length + " in " + method.FullName + ")");
            at++;
        }
    }

    static IEnumerable<MethodDefinition> Bodies(ModuleDefinition module) => module.GetTypes().SelectMany(t => t.Methods).Where(m => m.HasBody);

    // Every method that calls or loads (ldftn) a method of this name and signature.
    static List<string> Callers(ModuleDefinition module, string owner, string name, string signature) =>
        Bodies(module).Where(m => m.Body.Instructions.Any(i => i.Operand is MethodReference r && r.Name == name && Owner(r) == owner && Sig(r) == signature && i.OpCode.Code != Code.Ldtoken))
            .Select(m => m.DeclaringType.FullName + "::" + m.Name).Distinct().OrderBy(x => x, StringComparer.Ordinal).ToList();

    static void Contracts(string refs, string dcmPath)
    {
        using (var game = AssemblyDefinition.ReadAssembly(Path.Combine(refs, "Seapower-Scripts.dll")))
            NativeContracts(game.MainModule);
        Check(Sha(dcmPath) == DcmHash, "captured Dynamic Campaign Mod 0.25.0.1 image");
        using (var dcm = AssemblyDefinition.ReadAssembly(dcmPath))
            CampaignContracts(dcm.MainModule);
    }

    const string Vm = "SeapowerUI.ViewModels.";
    const string Rules = Vm + "LinearCampaignTaskForceRibbonRules";
    const string Row = Vm + "LinearCampaignTaskForceRibbonAwardRow";
    const string Spec = Rules + "/MissionRibbonAwardSpec";
    const string Definition = Rules + "/LinearCampaignTaskForceRibbonDefinition";
    const string Debrief = Vm + "LinearCampaignTaskForceDebriefViewModel";
    const string MissionDebrief = Vm + "MissionDebriefViewModel";
    const string Manager = Vm + "LinearCampaignTaskForceCommanderManager";
    const string Ini = "SeaPower.IniHandler";
    const string Mission = "SeaPower.LinearCampaignMission";
    const string Rows = "System.Collections.Generic.IReadOnlyList`1<" + Row + ">";
    const string Persistent = "System.Collections.Generic.IDictionary`2<System.String,System.String>";

    static void NativeContracts(ModuleDefinition game)
    {
        // The debrief snapshot: the completion gate returns before any award,
        // ribbons are granted before the debrief rows, the weapon report and
        // the saves are written, and nothing re-reads the awards in between.
        var debrief = Type(game, Debrief);
        var snapshot = Method(debrief, "SaveDebriefSnapshot", "System.Void(" + Mission + "," + MissionDebrief + ")");
        Check(snapshot.IsStatic && snapshot.IsAssembly, "SaveDebriefSnapshot stays internal static");
        InOrder(snapshot, "SaveDebriefSnapshot: clear, gate, ribbon awards, debrief rows, weapon report, saves",
            Calls(Debrief, "ClearDebriefSnapshot"),
            Calls("SeaPower.LinearCampaignEvent", "get_IsComplete"),
            Calls(MissionDebrief, "get_MissionResult"),
            Calls(Mission, "get_RequiredResult"),
            Calls(Ini, "saveFile"), Op(Code.Ret),
            Calls(Rules, "ApplyMissionRibbonAwards"),
            Calls(Rules, "WriteDebriefRibbonRows"),
            Calls(Debrief, "SerializeRibbonAwardRows"),
            Calls(Debrief, "WriteWeaponReports"),
            Calls(Ini, "saveFile"),
            Calls("SeaPower.LinearCampaign", "SaveCampaignPersistentData"),
            Calls(Debrief, "PersistDebriefSectionsToCurrentCampaignSave"));
        Check(snapshot.Body.Instructions.Count(Calls(Rules, "ApplyMissionRibbonAwards")) == 1, "SaveDebriefSnapshot grants mission ribbons once");
        Check(Callers(game, Debrief, "SaveDebriefSnapshot", Sig(snapshot)).SequenceEqual(new[] {
            MissionDebrief + "/<WriteTaskForceMissionDebrief>d__120::MoveNext", MissionDebrief + "::ButtonExit_Click" }),
            "SaveDebriefSnapshot is called only by the debrief exit and the post-mission debrief load action");

        // The award overloads: the 2-argument one only from the snapshot, the
        // 3-argument one (the patched one) only from it and too large to inline.
        var rules = Type(game, Rules);
        var apply2 = Method(rules, "ApplyMissionRibbonAwards", Rows + "(" + Ini + "," + Mission + ")");
        var apply3 = Method(rules, "ApplyMissionRibbonAwards", Rows + "(" + Ini + ",System.Int32,System.String)");
        Check(apply3.IsStatic && apply3.Body.CodeSize >= 64, "3-argument ApplyMissionRibbonAwards is static and not inlinable (" + apply3.Body.CodeSize + " bytes)");
        Check(Callers(game, Rules, "ApplyMissionRibbonAwards", Sig(apply2)).SequenceEqual(new[] { Debrief + "::SaveDebriefSnapshot" }), "2-argument ApplyMissionRibbonAwards is called only by SaveDebriefSnapshot");
        Check(Callers(game, Rules, "ApplyMissionRibbonAwards", Sig(apply3)).SequenceEqual(new[] { Rules + "::ApplyMissionRibbonAwards" }) &&
            apply2.Body.Instructions.Any(i => i.Operand is FieldReference f && f.Name == "_index") && apply2.Body.Instructions.Any(Calls("SeaPower.LinearCampaignEvent", "get_EventName")),
            "3-argument ApplyMissionRibbonAwards is reached only from the 2-argument one, with mission._index and EventName");
        InOrder(apply3, "ApplyMissionRibbonAwards: commander nation, specs, rank, definitions, rows, persistent set, precedence order",
            Calls("SeaPower.Singleton`1", "get_Instance"), Calls("SeaPower.LinearCampaign", "get_PersistentData"), Calls(Manager, "GetCommanderNation"),
            Calls(Rules, "ReadMissionRibbonAwardSpecs"), Calls("System.Linq.Enumerable", "Where"), Calls("System.Linq.Enumerable", "GroupBy"),
            Calls(Manager, "ReadCommanderState"), Calls(Vm + "LinearCampaignTaskForceCommanderState", "get_Rank"), Calls(Vm + "LinearCampaignTaskForceCommanderRank", "get_DisplayName"),
            Calls(Rules, "ReadRibbonDefinition"), Calls(Definition, "ToAwardRow"),
            Calls(Rules, "AddPersistentCommanderRibbonRows"), Calls("System.Linq.Enumerable", "OrderBy"), Calls("System.StringComparer", "get_OrdinalIgnoreCase"), Calls("System.Linq.Enumerable", "ThenBy"));
        var nationFilter = Type(game, Rules + "/<>c__DisplayClass11_0").Methods.Single(m => m.Name == "<ApplyMissionRibbonAwards>b__0");
        Check(nationFilter.Body.Instructions.Any(Calls(Spec, "AllowsCommanderNation")), "native awards filter specs with MissionRibbonAwardSpec.AllowsCommanderNation");
        var c = Type(game, Rules + "/<>c");
        Check(c.Methods.Single(m => m.Name == "<ApplyMissionRibbonAwards>b__11_3").Body.Instructions.Any(Calls(Row, "get_Precedence")) &&
            c.Methods.Single(m => m.Name == "<ApplyMissionRibbonAwards>b__11_4").Body.Instructions.Any(Calls(Row, "get_DisplayName")),
            "native award rows are ordered by Precedence, then DisplayName");
        var toRow = apply3.Body.Instructions.First(Calls(Definition, "ToAwardRow"));
        Check(toRow.Previous.OpCode.Code == Code.Ldstr && (string)toRow.Previous.Operand == "" && toRow.Previous.Previous.OpCode.Code == Code.Ldloc_3 &&
            toRow.Previous.Previous.Previous.OpCode.Code == Code.Ldarg_1 && toRow.Previous.Previous.Previous.Previous.OpCode.Code == Code.Ldc_I4_1,
            "native rows are ToAwardRow(1, missionIndex, rank, \"\")");

        // The key reader the runtime key mirrors: [Mission{N}] first, then the
        // event's own section, in every campaign rule source.
        var reader = Type(game, Rules + "/<ReadMissionRibbonAwardSpecs>d__21").Methods.Single(m => m.Name == "MoveNext");
        InOrder(reader, "ReadMissionRibbonAwardSpecs: rule sources, [Mission{N}], event section, pipe list, native spec parser",
            Calls(Rules, "EnumerateCampaignRuleSources"),
            i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "Mission{0}", i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "TaskForceModeRibbonAwards", Calls(Ini, "readValue"),
            i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "TaskForceModeRibbonAwards", Calls(Ini, "readValue"),
            Calls(Rules, "SplitPipeList"), Calls(Rules, "TryParseMissionRibbonAwardSpec"));

        // The helpers the runtime calls, by exact signature.
        var sources = Method(rules, "EnumerateCampaignRuleSources", "System.Collections.Generic.IEnumerable`1<" + Ini + ">(" + Ini + ")");
        var parse = Method(rules, "TryParseMissionRibbonAwardSpec", Spec + "(System.String)");
        var define = Method(rules, "ReadRibbonDefinition", Definition + "(" + Ini + ",System.String)");
        var persist = Method(rules, "AddPersistentCommanderRibbonRows", "System.Void(" + Persistent + ",System.Collections.Generic.IEnumerable`1<" + Row + ">)");
        Method(rules, "SplitPipeList", "System.Collections.Generic.IEnumerable`1<System.String>(System.String)");
        Check(sources.IsStatic && parse.IsStatic && define.IsStatic && persist.IsStatic && persist.IsPublic, "ribbon-rule helpers are static (AddPersistentCommanderRibbonRows public)");
        InOrder(parse, "TryParseMissionRibbonAwardSpec splits on ',' and cuts the id before ':'",
            i => i.OpCode.Code == Code.Ldc_I4_S && (sbyte)i.Operand == 44, Calls("System.String", "Split"), i => i.OpCode.Code == Code.Ldc_I4_S && (sbyte)i.Operand == 58, Calls("System.String", "Split"), Calls(Rules, "NormalizeRibbonId"));
        Check(persist.Body.Instructions.Any(i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "TaskForceCommanderRibbons") && persist.Body.Instructions.Any(Calls("System.Linq.Enumerable", "Distinct")) &&
            persist.Body.Instructions.Any(Calls("System.Linq.Enumerable", "Contains")), "AddPersistentCommanderRibbonRows keeps TaskForceCommanderRibbons a distinct set");
        Check(define.Body.Instructions.Any(i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "Ribbon_") && define.Body.Instructions.Any(Calls(Rules, "OpenCommanderSettingsIni")),
            "ReadRibbonDefinition reads [Ribbon_<id>] from the commander settings file only");
        var spec = Type(game, Spec);
        Property(spec, "RibbonId", "System.String");
        var allows = Method(spec, "AllowsCommanderNation", "System.Boolean(System.String)");
        Check(!allows.IsStatic && Type(game, Spec + "/<>c__DisplayClass7_0").Methods.Single(m => m.Name == "<AllowsCommanderNation>b__0").Body.Instructions.Any(Calls(Manager, "IsSameNation")),
            "AllowsCommanderNation compares with LinearCampaignTaskForceCommanderManager.IsSameNation");
        Method(Type(game, Definition), "ToAwardRow", Row + "(System.Int32,System.Int32,System.String,System.String)");
        var row = Type(game, Row);
        Check(row.IsPublic, "LinearCampaignTaskForceRibbonAwardRow is public (the postfix's by-ref result type)");
        Property(row, "Id", "System.String"); Property(row, "DisplayName", "System.String"); Property(row, "Precedence", "System.Int32");
        var manager = Type(game, Manager);
        var nation = Method(manager, "GetCommanderNation", "System.String(" + Persistent + ")");
        Check(nation.Body.Instructions.Any(i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "TaskForceCommanderNation"), "GetCommanderNation reads TaskForceCommanderNation");
        Method(manager, "ReadCommanderState", Vm + "LinearCampaignTaskForceCommanderState(" + Ini + "," + Persistent + ")");
        Property(Type(game, Vm + "LinearCampaignTaskForceCommanderState"), "Rank", Vm + "LinearCampaignTaskForceCommanderRank");
        Property(Type(game, Vm + "LinearCampaignTaskForceCommanderRank"), "DisplayName", "System.String");
        Method(Type(game, Ini), "readValue", "System.String(System.String,System.String,System.String,System.Boolean)");
        Method(debrief, "SerializeRibbonAwardRows", "System.String(System.Collections.Generic.IEnumerable`1<" + Row + ">)");

        // The INI reader cuts a value at ';', '//' or '#', and rejoins the
        // parts of a value split on '='. The runtime key therefore never uses
        // ';' (the design's draft separator) and may contain '='.
        var ini = Type(game, Ini);
        var cctor = ini.Methods.Single(m => m.Name == ".cctor");
        InOrder(cctor, "IniHandler comment separators ';', '//', '#'",
            i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == ";", i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "//",
            i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "#", i => i.OpCode.Code == Code.Stsfld && ((FieldReference)i.Operand).Name == "commentsSeparators");
        var readFile = ini.Methods.Single(m => m.Name == "ReadFileToIni");
        InOrder(readFile, "ReadFileToIni drops everything after a comment separator, then rejoins '=' parts",
            i => i.OpCode.Code == Code.Ldsfld && ((FieldReference)i.Operand).Name == "commentsSeparators", Calls("System.String", "Split"), Op(Code.Ldelem_Ref),
            i => i.OpCode.Code == Code.Ldc_I4_S && (sbyte)i.Operand == 61, Calls("System.String", "Split"), i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "=");

        // Context the runtime reads without calling Singleton.get_Instance
        // (which can create a GameObject): the static _instance field.
        var singleton = Type(game, "SeaPower.Singleton`1");
        Check(singleton.Fields.Any(f => f.Name == "_instance" && f.IsStatic && f.FieldType.FullName == "T"), "Singleton<T>._instance is the static instance field");
        Check(Method(singleton, "get_Instance", "T()").Body.Instructions.Where(i => i.OpCode.Code == Code.Ldsfld).Select(i => ((FieldReference)i.Operand).Name).Contains("_instance"), "Singleton<T>.get_Instance returns _instance");
        Property(Type(game, "SeaPower.LinearCampaign"), "PersistentData", "System.Collections.Generic.Dictionary`2<System.String,System.String>");
        Property(Type(game, "SeaPower.MissionManager"), "Objectives", "TrulyObservableCollection`1<SeaPower.MissionManager/MissionObjective>");
        var objective = Type(game, "SeaPower.MissionManager/MissionObjective");
        Field(objective, "_id", "System.String");
        foreach (var flag in new[] { "_isCompleted", "_isFailed", "_isCanceled", "_completeOnMissionEnd", "_failOnMissionEnd" }) Field(objective, flag, "System.Boolean");
        var missionDebrief = Type(game, MissionDebrief);
        Property(missionDebrief, "MissionResult", MissionDebrief + "/Result");
        Property(missionDebrief, "PlayerSurvivorsRescued", "System.Int32");
        Property(missionDebrief, "MissionObjectives", "System.Collections.Generic.List`1<SeaPower.MissionManager/MissionObjective>");
        var result = Type(game, MissionDebrief + "/Result");
        var values = result.Fields.Where(f => f.IsStatic).ToDictionary(f => f.Name, f => (int)f.Constant);
        Check(values.Count == 18 && values["Incomplete"] == 0 && values["PyrrhicVictory"] == 9 && values["Draw"] == 10 && values["CostlyVictory"] == 11 && values["MajorVictory"] == 16 && values["DecisiveVictory"] == 17,
            "MissionDebriefViewModel.Result runs from Incomplete (0) to DecisiveVictory (17), compared numerically as the native gate does");
        Field(Type(game, Mission), "_index", "System.Int32");
        Property(Type(game, "SeaPower.LinearCampaignEvent"), "EventName", "System.String");
        // The native objective precedence the runtime repeats.
        InOrder(missionDebrief.Methods.Single(m => m.Name == "CalculateEndMissionData"), "debrief objective precedence: cancelled, failed, completed, fail at end, complete at end",
            i => i.OpCode.Code == Code.Ldfld && ((FieldReference)i.Operand).Name == "_isCanceled", i => i.OpCode.Code == Code.Ldfld && ((FieldReference)i.Operand).Name == "_isFailed",
            i => i.OpCode.Code == Code.Ldfld && ((FieldReference)i.Operand).Name == "_isCompleted", i => i.OpCode.Code == Code.Ldfld && ((FieldReference)i.Operand).Name == "_failOnMissionEnd",
            i => i.OpCode.Code == Code.Ldfld && ((FieldReference)i.Operand).Name == "_completeOnMissionEnd");

        // The rescued-survivor count: the debrief copies the player's counter.
        var ctor = missionDebrief.Methods.Single(m => m.Name == ".ctor");
        InOrder(ctor, "MissionDebriefViewModel..ctor copies Taskforce._survivorsResqued into PlayerSurvivorsRescued",
            i => i.OpCode.Code == Code.Ldsfld && ((FieldReference)i.Operand).Name == "_playerTaskforce", i => i.OpCode.Code == Code.Ldfld && ((FieldReference)i.Operand).Name == "_survivorsResqued",
            Calls(MissionDebrief, "set_PlayerSurvivorsRescued"));
        Field(Type(game, "SeaPower.Taskforce"), "_survivorsResqued", "System.Int32");

        // The live weapon report, written to the campaign only after awards.
        Field(Type(game, "SeaPower.Globals"), "_playerTaskforce", "SeaPower.Taskforce", true);
        Field(Type(game, "SeaPower.Taskforce"), "_weaponReport", "SeaPower.TaskforceWeaponReport");
        Property(Type(game, "SeaPower.TaskforceWeaponReport"), "UnitsByReportId", "System.Collections.Generic.Dictionary`2<System.String,SeaPower.WeaponReportUnitData>");
        Property(Type(game, "SeaPower.WeaponReportUnitData"), "Ammo", "System.Collections.Generic.Dictionary`2<System.String,SeaPower.WeaponReportAmmoData>");
        var ammo = Type(game, "SeaPower.WeaponReportAmmoData");
        foreach (var count in new[] { "Launched", "ProjectileFired", "CiwsRoundsFired" }) Property(ammo, count, "System.Int32");
        Property(ammo, "AmmoType", "SeaPower.Ammunition/Type"); Property(ammo, "AmmoSubType", "SeaPower.Ammunition/Type");
        var kinds = Type(game, "SeaPower.Ammunition/Type").Fields.Where(f => f.IsStatic).ToDictionary(f => f.Name, f => (int)f.Constant);
        Check(kinds["Noisemaker"] == 6 && kinds["Chaff"] == 7 && kinds["Sonobuoy"] == 11 && kinds["MOSS"] == 14 && kinds["Paratrooper"] == 15 && kinds["Fueltank"] == 16 && kinds["Torpedo"] == 5,
            "Ammunition.Type keeps the countermeasure, sonobuoy, paratrooper and fuel-tank values the runtime exempts by name");
        var write = Method(debrief, "WriteWeaponReports", "System.Void(" + Ini + ",System.Int32)");
        Check(write.Body.Instructions.Any(i => i.OpCode.Code == Code.Ldsfld && ((FieldReference)i.Operand).Name == "_playerTaskforce") &&
            write.Body.Instructions.Any(i => i.OpCode.Code == Code.Ldfld && ((FieldReference)i.Operand).Name == "_weaponReport"),
            "WriteWeaponReports saves the same live Globals._playerTaskforce._weaponReport the runtime reads");
        var extensions = Type(game, "SeaPower.TaskforceWeaponReportExtensions");
        var ignored = Method(extensions, "IsIgnoredAmmo", "System.Boolean(SeaPower.Ammunition/Type,SeaPower.Ammunition/Type)");
        Check(ignored.Body.Instructions.Where(i => i.OpCode.Code == Code.Ldc_I4_S).All(i => (sbyte)i.Operand == 16) && ignored.Body.Instructions.Count(i => i.OpCode.Code == Code.Ldc_I4_S) == 2,
            "IsIgnoredAmmo skips only Fueltank (16): countermeasures and sonobuoys are recorded");
        var ciws = Type(game, "SeaPower.TaskforceWeaponReportExtensions/<>c__DisplayClass14_0").Methods.Single(m => m.Name == "<RecordCiwsRoundsFired>b__0");
        Check(ciws.Body.Instructions.Any(Calls("SeaPower.WeaponReportAmmoData", "set_CiwsRoundsFired")) && ciws.Body.Instructions.Any(Calls("SeaPower.WeaponReportAmmoData", "set_ProjectileFired")) &&
            !ciws.Body.Instructions.Any(Calls("SeaPower.WeaponReportAmmoData", "set_Launched")), "RecordCiwsRoundsFired adds to CiwsRoundsFired and ProjectileFired, never Launched");
        var launch = Type(game, "SeaPower.TaskforceWeaponReportExtensions/<>c__DisplayClass1_0").Methods.Single(m => m.Name == "<RecordWeaponLaunch>b__0");
        Check(launch.Body.Instructions.Count(Calls("SeaPower.WeaponReportAmmoData", "set_Launched")) == 1 && launch.Body.Instructions.Count(i => i.Operand is MethodReference r && r.Name.StartsWith("set_")) == 1,
            "RecordWeaponLaunch adds only to Launched");
        Check(Callers(game, "SeaPower.TaskforceWeaponReportExtensions", "RecordProjectileFired", "System.Void(SeaPower.Taskforce,SeaPower.Projectile,System.Int32)").SequenceEqual(new[] { "SeaPower.Projectile::fire" }) &&
            Callers(game, "SeaPower.Projectile", "fire", "System.Void(UnityEngine.Vector3,UnityEngine.Vector3)").SequenceEqual(new[] { "SeaPower.GunBarrel::LaunchProjectile" }) &&
            Callers(game, "SeaPower.TaskforceWeaponReportExtensions", "RecordCiwsRoundsFired", "System.Void(SeaPower.Taskforce,SeaPower.WeaponSystemCIWS,System.Int32)").SequenceEqual(new[] { "SeaPower.WeaponSystemCIWS::OnFixedUpdate" }) &&
            Callers(game, "SeaPower.TaskforceWeaponReportExtensions", "RecordWeaponLaunch", "System.Void(SeaPower.Taskforce,SeaPower.WeaponBase,System.Int32)").SequenceEqual(new[] { "SeaPower.WeaponBase::CommonLaunchSettings", "SeaPower.WeaponContainer::RecordFailedLaunch" }),
            "gun rounds reach ProjectileFired only through GunBarrel, CIWS rounds only through WeaponSystemCIWS, launches only through WeaponBase and WeaponContainer");
    }

    const string Sim = "DynamicCampaignMod.Core.Sim.";
    const string State = "DynamicCampaignMod.Core.State.";
    const string Outcome = State + "OrderOutcome";

    static void CampaignContracts(ModuleDefinition dcm)
    {
        var admiralty = Type(dcm, Sim + "Admiralty");
        var queue = Method(admiralty, "Queue", "System.Void(" + Outcome + ")");
        Check(!queue.IsStatic, "Admiralty.Queue(OrderOutcome) is an instance method");
        var read = Method(admiralty, "Read", "System.Void(" + Outcome + ")");
        Field(admiralty, "_state", State + "CampaignState");
        var outcomes = "System.Collections.Generic.List`1<" + Outcome + ">";
        // Queue is the only place a result is added; Read the only removal.
        var touching = Bodies(dcm).Where(m => m.Body.Instructions.Any(i => i.Operand is FieldReference f && f.Name == "Outcomes" && f.DeclaringType.FullName == State + "CampaignState")).ToList();
        Func<string, List<string>> mutating = name => touching.Where(m => m.Body.Instructions.Any(i => i.Operand is MethodReference r && r.Name == name && r.DeclaringType.FullName == outcomes))
            .Select(m => m.DeclaringType.FullName + "::" + m.Name).ToList();
        Check(mutating("Add").SequenceEqual(new[] { Sim + "Admiralty::Queue" }), "only Admiralty.Queue adds to CampaignState.Outcomes");
        Check(mutating("RemoveAll").SequenceEqual(new[] { Sim + "Admiralty::Read" }), "only Admiralty.Read removes from CampaignState.Outcomes");
        Check(new[] { "Insert", "Remove", "RemoveAt", "Clear", "AddRange", "RemoveRange" }.All(n => mutating(n).Count == 0), "nothing else changes CampaignState.Outcomes");
        InOrder(queue, "Queue sets Rank and Promotion, then adds the outcome",
            i => i.OpCode.Code == Code.Stfld && ((FieldReference)i.Operand).Name == "Rank", i => i.OpCode.Code == Code.Stfld && ((FieldReference)i.Operand).Name == "Promotion",
            i => i.Operand is MethodReference r && r.Name == "Add" && r.DeclaringType.FullName == outcomes, Op(Code.Ret));
        Check(Callers(dcm, Sim + "Admiralty", "Queue", Sig(queue)).SequenceEqual(new[] { Sim + "Admiralty::Paper" }) &&
            admiralty.Methods.Count(m => m.Name == "Paper" && m.Body.Instructions.Any(i => i.Operand is MethodReference r && r.Name == "Queue")) == 2,
            "Queue is called only by the two Admiralty.Paper overloads");
        Check(Callers(dcm, Sim + "Admiralty", "Read", Sig(read)).SequenceEqual(new[] { "DynamicCampaignMod.UI.CampaignUI::CloseOutcome" }), "Read is called only when the player closes a paper");
        // Paper sets every field World Operations reads; the only later write
        // is OnCaptured resetting Issued after its call to Complete.
        foreach (var name in new[] { "Id", "Status", "At", "Issued", "Moot" })
        {
            var writers = Bodies(dcm).Where(m => m.Body.Instructions.Any(i => i.OpCode.Code == Code.Stfld && i.Operand is FieldReference f && f.Name == name && f.DeclaringType.FullName == Outcome))
                .Select(m => m.DeclaringType.FullName + "::" + m.Name).Distinct().ToList();
            Check(writers.SequenceEqual(new[] { Sim + "Admiralty::Paper" }), "only Admiralty.Paper stores OrderOutcome." + name);
        }
        var addressed = Bodies(dcm).Where(m => m.Body.Instructions.Any(i => i.OpCode.Code == Code.Ldflda && i.Operand is FieldReference f && f.DeclaringType.FullName == Outcome)).Select(m => m.DeclaringType.FullName + "::" + m.Name).ToList();
        Check(addressed.SequenceEqual(new[] { Sim + "Admiralty::OnCaptured" }), "only Admiralty.OnCaptured takes an OrderOutcome field's address");
        InOrder(admiralty.Methods.Single(m => m.Name == "OnCaptured"), "OnCaptured completes the offered order, then resets that outcome's Issued",
            Calls(Sim + "Admiralty", "Complete"), i => i.OpCode.Code == Code.Ldflda && ((FieldReference)i.Operand).Name == "Issued", Op(Code.Initobj));
        // The sim runs before the strategic UI tick that SEST's Poll follows.
        var driver = Type(dcm, "DynamicCampaignMod.Game.Session.CampaignDriver");
        InOrder(Method(driver, "Update", "System.Void()"), "CampaignDriver.Update runs the sim lambda before the CampaignUI.Tick lambda",
            i => i.OpCode.Code == Code.Ldftn && ((MethodReference)i.Operand).Name == "<Update>b__5", i => i.OpCode.Code == Code.Ldftn && ((MethodReference)i.Operand).Name == "<Update>b__11_12");
        Check(Type(dcm, "DynamicCampaignMod.Game.Session.CampaignDriver/<>c__DisplayClass11_0").Methods.Single(m => m.Name == "<Update>b__5").Body.Instructions.Any(Calls(Sim + "CampaignSim", "Run")) &&
            Type(dcm, "DynamicCampaignMod.Game.Session.CampaignDriver/<>c").Methods.Single(m => m.Name == "<Update>b__11_12").Body.Instructions.Any(Calls("DynamicCampaignMod.UI.CampaignUI", "Tick")),
            "the two lambdas are CampaignSim.Run and CampaignUI.Tick");
        // The fields World Operations reads, with their types.
        var campaignState = Type(dcm, State + "CampaignState");
        Field(campaignState, "Definition", "DynamicCampaignMod.Core.Data.CampaignDefinition");
        Field(campaignState, "PlayerSideId", "System.String");
        Field(campaignState, "Outcomes", outcomes);
        Field(Type(dcm, "DynamicCampaignMod.Core.Data.CampaignDefinition"), "id", "System.String");
        var outcome = Type(dcm, Outcome);
        Check(outcome.IsClass && !outcome.IsValueType, "OrderOutcome is a class: a filed reference sees later changes");
        foreach (var f in new[] { "Id:System.Int32", "SideId:System.String", "OrderId:System.Int32", "OperationId:System.Int32", "Status:" + State + "OrderStatus", "At:System.DateTime",
            "Issued:System.DateTime", "Title:System.String", "Kind:" + State + "OrderKind", "Template:" + State + "OperationTemplate", "Moot:System.Boolean" })
            Field(outcome, f.Split(':')[0], f.Substring(f.IndexOf(':') + 1));
    }

    // ---- Runtime 1.6.5 behaviour, on the captured native types ----

    static Assembly game, rt;
    static Type awards;
    static object Invoke(Type type, string name, params object[] args)
    {
        try { return type.GetMethod(name, All).Invoke(null, args); }
        catch (TargetInvocationException e) { throw e.InnerException; }
    }
    static void SetField(object target, string name, object value)
    {
        Type type = target as Type ?? target.GetType();
        FieldInfo field = null;
        for (Type t = type; field == null && t != null; t = t.BaseType) field = t.GetField(name, All);
        if (field == null) throw new MissingFieldException(type.FullName, name);
        field.SetValue(target is Type ? null : target, value);
    }
    // Fixtures without constructors; their finalizers (Noesis, Unity) must not run.
    static object Uninitialized(string type)
    {
        object value = System.Runtime.Serialization.FormatterServices.GetUninitializedObject(game.GetType(type, true));
        GC.SuppressFinalize(value);
        return value;
    }
    static object EnumValue(string type, string name) => System.Enum.Parse(game.GetType(type, true), name);
    static IList Specs(out string error, params string[] values)
    {
        object[] args = { values.ToList(), null };
        var specs = (IList)awards.GetMethod("ParseSpecs", All).Invoke(null, args);
        error = (string)args[1];
        return specs;
    }
    static object F(object o, string name) => o.GetType().GetField(name, All).GetValue(o);

    // The value a campaign.ini line yields through IniHandler.ReadFileToIni,
    // whose rules the contracts above pin: cut at ';', '//' or '#', trim, split
    // on '=' and rejoin the trimmed parts after the key.
    static string AsRead(string line)
    {
        string text = line.Split(new[] { ";", "//", "#" }, StringSplitOptions.None)[0].Trim();
        var parts = text.Split('=');
        return string.Join("=", parts.Skip(1).Select(p => p.Trim()));
    }

    static object Ammo(string type, int launch, int rounds, int ciws, string subType = "None")
    {
        object row = Activator.CreateInstance(game.GetType("SeaPower.WeaponReportAmmoData", true));
        foreach (var p in new[] { Tuple.Create("AmmoType", EnumValue("SeaPower.Ammunition+Type", type)), Tuple.Create("AmmoSubType", EnumValue("SeaPower.Ammunition+Type", subType)),
            Tuple.Create("Launched", (object)launch), Tuple.Create("ProjectileFired", (object)rounds), Tuple.Create("CiwsRoundsFired", (object)ciws), Tuple.Create("AmmoRef", (object)(type + launch + rounds)) })
            row.GetType().GetProperty(p.Item1).SetValue(row, p.Item2, null);
        return row;
    }
    static object Report(params object[] ammo)
    {
        object report = Activator.CreateInstance(game.GetType("SeaPower.TaskforceWeaponReport", true));
        var units = (IDictionary)report.GetType().GetProperty("UnitsByReportId").GetValue(report, null);
        object unit = Activator.CreateInstance(game.GetType("SeaPower.WeaponReportUnitData", true));
        var rows = (IDictionary)unit.GetType().GetProperty("Ammo").GetValue(unit, null);
        if (rows == null) { rows = (IDictionary)Activator.CreateInstance(unit.GetType().GetProperty("Ammo").PropertyType); unit.GetType().GetProperty("Ammo").SetValue(unit, rows, null); }
        for (int i = 0; i < ammo.Length; i++) rows.Add("ammo" + i, ammo[i]);
        units.Add("unit", unit);
        return report;
    }
    static object Weapons(object report)
    {
        object evidence = Activator.CreateInstance(awards.GetNestedType("Evidence", All), true);
        Invoke(awards, "CountWeapons", report, evidence);
        return evidence;
    }
    static bool NoLaunch(object evidence) => (bool)evidence.GetType().GetProperty("NoLaunch", All).GetValue(evidence, null);

    static object Objective(string id, int flags)
    {
        object o = Activator.CreateInstance(game.GetType("SeaPower.MissionManager+MissionObjective", true));
        SetField(o, "_id", id);
        string[] names = { "_isCanceled", "_isFailed", "_isCompleted", "_failOnMissionEnd", "_completeOnMissionEnd" };
        for (int n = 0; n < names.Length; n++) SetField(o, names[n], (flags & (1 << n)) != 0);
        return o;
    }

    static object MakeDefinition(string id, string name, int precedence)
    {
        var ctor = game.GetType("SeapowerUI.ViewModels.LinearCampaignTaskForceRibbonRules+LinearCampaignTaskForceRibbonDefinition", true).GetConstructors(All).Single();
        var p = ctor.GetParameters();
        var args = new object[p.Length];
        for (int i = 0; i < p.Length; i++)
            args[i] = p[i].ParameterType == typeof(int) ? (object)precedence : p[i].ParameterType == typeof(string) ? (i == 0 ? id : i == 1 ? name : "") : (object)new Dictionary<string, string>();
        return ctor.Invoke(args);
    }
    static object RowOf(object definition, int mission) => definition.GetType().GetMethod("ToAwardRow", All).Invoke(definition, new object[] { 1, mission, "Commander", "" });
    static string Id(object row) => (string)row.GetType().GetProperty("Id").GetValue(row, null);

    static object MakeDebrief(int result, int rescued, object report, params object[] objectives)
    {
        object debrief = Uninitialized("SeapowerUI.ViewModels.MissionDebriefViewModel");
        SetField(debrief, "<MissionResult>k__BackingField", System.Enum.ToObject(game.GetType("SeapowerUI.ViewModels.MissionDebriefViewModel+Result", true), result));
        SetField(debrief, "<PlayerSurvivorsRescued>k__BackingField", rescued);
        var list = (IList)Activator.CreateInstance(typeof(List<>).MakeGenericType(game.GetType("SeaPower.MissionManager+MissionObjective", true)));
        foreach (var o in objectives) list.Add(o);
        SetField(debrief, "<MissionObjectives>k__BackingField", list);
        fixtureReport = report;
        return debrief;
    }
    static object Evidence(string nation, int result, int rescued, object report, params object[] objectives) =>
        Invoke(awards, "Collect", 15, MakeDebrief(result, rescued, report, objectives), nation, report);

    // Globals' static constructor needs Unity, so the native grant test feeds
    // the player's weapon report through a Harmony prefix on the runtime's reader.
    static object fixtureReport;
    static string streamingAssets;
    static bool UseTempStreamingAssets(ref string __result) { __result = streamingAssets; return false; }
    static bool UseFixtureReport(ref object __result) { __result = fixtureReport; return false; }
    // The debrief view model's static constructor needs native Noesis, so its
    // auto-property values are read from their backing fields here instead.
    static bool UseDebriefFields(object debrief, object evidence, ref IEnumerable __result)
    {
        if (!(debrief is string))
        {
            object result = F(debrief, "<MissionResult>k__BackingField");
            SetField(evidence, "Result", System.Convert.ToInt32(result));
            SetField(evidence, "ResultName", result.ToString());
            SetField(evidence, "Rescued", Math.Max(0, (int)F(debrief, "<PlayerSurvivorsRescued>k__BackingField")));
            __result = (IEnumerable)F(debrief, "<MissionObjectives>k__BackingField");
            return false;
        }
        return true;
    }

    static List<string> Evaluate(IList specs, IList native, object evidence, Func<string, object> rowFor, List<string> log)
    {
        var method = awards.GetMethod("Evaluate", All);
        var extra = (IEnumerable)method.Invoke(null, new object[] { specs, native, evidence, RowFactory(method.GetParameters()[3].ParameterType, rowFor), new Action<string>(log.Add) });
        return extra.Cast<object>().Select(Id).ToList();
    }
    // Func<string, LinearCampaignTaskForceRibbonAwardRow> from Func<string, object>.
    static Delegate RowFactory(Type delegateType, Func<string, object> f)
    {
        var arg = System.Linq.Expressions.Expression.Parameter(typeof(string), "id");
        var call = System.Linq.Expressions.Expression.Convert(System.Linq.Expressions.Expression.Invoke(System.Linq.Expressions.Expression.Constant(f), arg), delegateType.GetGenericArguments()[1]);
        return System.Linq.Expressions.Expression.Lambda(delegateType, call, arg).Compile();
    }
    static IList NativeRows(params object[] rows)
    {
        var list = (IList)Activator.CreateInstance(typeof(List<>).MakeGenericType(game.GetType("SeapowerUI.ViewModels.LinearCampaignTaskForceRibbonAwardRow", true)));
        foreach (var r in rows) list.Add(r);
        return list;
    }

    static void Behaviour(string refs, string runtime)
    {
        game = Assembly.LoadFrom(Path.Combine(refs, "Seapower-Scripts.dll"));
        rt = Assembly.LoadFrom(runtime);
        Assembly.LoadFrom(Path.Combine(refs, "0Harmony.dll"));
        awards = rt.GetType("Sest.RuntimeFixes.MissionAwards", true);
        Invoke(awards, "Bind", game);
        Check((bool)awards.GetField("active", All).GetValue(null), "MissionAwards binds every member on the captured image");
        new HarmonyLib.Harmony("sest.tests.mission-awards-fixture").Patch(awards.GetMethod("ReadDebrief", All), prefix: new HarmonyLib.HarmonyMethod(typeof(MissionAwardsTests).GetMethod("UseDebriefFields", All)));
        Check((string)awards.GetField("Key", All).GetValue(null) == "SestRuntimeRibbonAwards", "the campaign key is SestRuntimeRibbonAwards");

        // Grammar.
        string error;
        var one = Specs(out error, "sest_rl05_passage?objective:Passage=completed&objective:Unseen=completed&nolaunch");
        Check(error == null && one.Count == 1 && (string)F(one[0], "RibbonId") == "sest_rl05_passage" && ((IList)F(one[0], "Terms")).Count == 3, "a spec is <native>?<term>&<term>...");
        var two = Specs(out error, " a?nolaunch | | b,China?rescued>=1 ", "c?result>=MajorVictory");
        Check(error == null && two.Count == 3 && (string)F(two[1], "RibbonId") == "b", "specs join with '|', across rule sources; blanks are ignored");
        var mixed = Specs(out error, "A:3,US?NoLaunch&Objective:Pilot=COMPLETED&Result>=majorvictory&RESCUED>=2&objective: Boat = notfailed");
        var terms = mixed.Count == 1 ? ((IList)F(mixed[0], "Terms")).Cast<object>().ToList() : new List<object>();
        Check(error == null && (string)F(mixed[0], "RibbonId") == "A" && terms.Count == 5 && (string)F(terms[2], "Id") == "MajorVictory" && (int)F(terms[2], "Number") == 16 &&
            (int)F(terms[3], "Number") == 2 && (string)F(terms[4], "Id") == "Boat" && (bool)F(terms[4], "NotFailed"), "terms ignore case and spaces; the id is the native one, cut before ':'");
        // Spaces before 'objective:''s ':' and around '>=' are accepted too;
        // the logged term is the normalised one.
        var spaced = Specs(out error, "s ? objective :Passage=completed & Objective : Boat = NotFailed & result >= CostlyVictory & RESCUED >=2 & rescued>= 3 & Result\t>=\tdraw");
        var spacedTerms = spaced.Count == 1 ? ((IList)F(spaced[0], "Terms")).Cast<object>().ToList() : new List<object>();
        Check(error == null && spacedTerms.Count == 6 && (string)F(spacedTerms[0], "Id") == "Passage" && (string)F(spacedTerms[1], "Id") == "Boat" && (bool)F(spacedTerms[1], "NotFailed") &&
            (int)F(spacedTerms[2], "Number") == 11 && (int)F(spacedTerms[3], "Number") == 2 && (int)F(spacedTerms[4], "Number") == 3 && (int)F(spacedTerms[5], "Number") == 10 &&
            spacedTerms.Select(x => (string)F(x, "Text")).SequenceEqual(new[] { "objective:Passage=completed", "objective:Boat=notfailed", "result>=CostlyVictory", "rescued>=2", "rescued>=3", "result>=Draw" }),
            "spaces around 'objective:''s ':' and around '>=' are ignored; the logged term is normalised");
        foreach (var bad in new[] { "a", "a?", "a?nofire", "a?nolaunch&", "?nolaunch", " ,?nolaunch", "a?rescued>=0", "a?rescued>=1000", "a?rescued>=x", "a?rescued>=-1", "a?rescued>=+1",
            "a?objective:x=done", "a?objective:=completed", "a?objective:x", "a?result>=Win", "a?result>=11", "a?launched<=0",
            "a?result> =Draw", "a?result > = Draw", "a?rescued> =1", "a?objectives:x=completed", "a?objective x=completed", "a?results>=Draw", "a?no launch" })
        {
            var rejected = Specs(out error, "ok?nolaunch|" + bad);
            Check(rejected.Count == 0 && error != null, "an invalid spec rejects the whole key (fail closed): " + bad);
        }
        Check(Specs(out error, new string('x', 4097) + "?nolaunch").Count == 0 && error != null, "an over-long value is rejected");
        Check(Specs(out error, string.Join("|", Enumerable.Range(0, 33).Select(n => "r" + n + "?nolaunch"))).Count == 0 && error != null, "more than 32 specs are rejected");
        // The INI reader: the delivered grammar survives it; the design draft's
        // ';' separator would have been cut to a bare id and never granted.
        string line = "SestRuntimeRibbonAwards = sest_rl05_passage?objective:Passage = completed&objective:Unseen=completed&nolaunch|sest_rlc1_recovery,US?objective:Pilot=completed&rescued>=1";
        var read = Specs(out error, AsRead(line));
        Check(error == null && read.Count == 2 && (string)F(read[1], "RibbonId") == "sest_rlc1_recovery", "the key survives IniHandler's '=' rejoin");
        string spacedLine = "SestRuntimeRibbonAwards = sest_rlc1_recovery ? objective : Pilot = completed & rescued >= 1 & result >= CostlyVictory";
        var spacedRead = Specs(out error, AsRead(spacedLine));
        Check(AsRead(spacedLine) == "sest_rlc1_recovery ? objective : Pilot=completed & rescued >=1 & result >=CostlyVictory" && error == null && spacedRead.Count == 1 &&
            ((IList)F(spacedRead[0], "Terms")).Count == 3, "spaced operators survive IniHandler's '=' rejoin, which keeps the space before '>='");
        Check(AsRead("SestRuntimeRibbonAwards=sest_x;objective:Passage=completed") == "sest_x" && Specs(out error, AsRead("SestRuntimeRibbonAwards=sest_x;objective:Passage=completed")).Count == 0 && error != null,
            "a ';' in the value starts an INI comment; such a key fails closed");

        // Commander nations through the native parser and filter.
        Func<object, string, bool> allows = (spec, nation) => (bool)F(spec, "Native").GetType().GetMethod("AllowsCommanderNation").Invoke(F(spec, "Native"), new object[] { nation });
        var nations = Specs(out error, "any?nolaunch", "cn,China?nolaunch", "two,China,US?nolaunch");
        Check(allows(nations[0], "") && allows(nations[0], "Australia") && allows(nations[1], "China") && !allows(nations[1], "US") && !allows(nations[1], "") &&
            allows(nations[2], "US") && !allows(nations[2], "Japan"), "nation selectors use the native AllowsCommanderNation: none means any commander, otherwise only those nations");
        Check(allows(nations[1], "china") == (bool)game.GetType("SeapowerUI.ViewModels.LinearCampaignTaskForceCommanderManager", true).GetMethod("IsSameNation", All).Invoke(null, new object[] { "China", "china" }),
            "nation case follows the native IsSameNation");

        // Objective precedence, all 32 combinations.
        for (int flags = 0; flags < 32; flags++)
        {
            string expected = (flags & 1) != 0 ? "Cancelled" : (flags & 2) != 0 ? "Failed" : (flags & 4) != 0 ? "Completed" : (flags & 8) != 0 ? "Failed" : (flags & 16) != 0 ? "Completed" : "InProgress";
            Check(Invoke(awards, "StateOf", Objective("o", flags)).ToString() == expected, "objective precedence cancelled, failed, completed, fail-at-end, complete-at-end: flags " + flags);
        }

        // Weapons: the owner's nolaunch rule on the real report types.
        Check(NoLaunch(Weapons(Report())), "an empty report is no launch");
        Check(!NoLaunch(Weapons(Report(Ammo("Torpedo", 1, 0, 0)))), "a torpedo launch disqualifies");
        Check(!NoLaunch(Weapons(Report(Ammo("Missile", 2, 0, 0)))), "a missile launch disqualifies");
        Check(!NoLaunch(Weapons(Report(Ammo("Projectile", 0, 10, 0)))), "gun rounds disqualify");
        foreach (var counter in new[] { "Noisemaker", "Chaff", "MOSS", "Sonobuoy", "Paratrooper", "Fueltank" })
        {
            object e = Weapons(Report(Ammo(counter, 4, 4, 0), Ammo("Projectile", 0, 300, 300)));
            Check(NoLaunch(e) && (long)F(e, "AllLaunched") == 4 && (long)F(e, "AllRounds") == 304, counter + " and CIWS rounds do not disqualify, and are still counted in the totals");
        }
        Check(NoLaunch(Weapons(Report(Ammo("Missile", 2, 0, 0, "Chaff")))), "a launcher's chaff sub-type is a countermeasure");
        Check(!NoLaunch(Weapons(Report(Ammo("Projectile", 0, 310, 300)))), "gun rounds beyond the CIWS rounds disqualify");
        object unknown = Weapons(Report(Ammo("Projectile", 0, 5, 9)));
        Check(!NoLaunch(unknown) && !(bool)F(unknown, "WeaponsKnown"), "more CIWS rounds than rounds fired makes the report unknown (fail closed)");
        Check(!NoLaunch(Weapons(Report(Ammo("Noisemaker", -1, 0, 0)))), "a negative count makes the report unknown");
        Check(!NoLaunch(Weapons(null)) && !(bool)F(Weapons(null), "WeaponsKnown"), "no weapon report fails nolaunch");
        Check(!NoLaunch(Weapons(Report(Ammo("Torpedo", int.MaxValue, 0, 0), Ammo("Torpedo", int.MaxValue, 0, 0), Ammo("Torpedo", 0, int.MaxValue, 0)))), "large counts stay counted");

        // Evidence and evaluation, with rows from the native definition type.
        var definitions = new Dictionary<string, object> { { "sest_rl05_passage", MakeDefinition("sest_rl05_passage", "Undersea Passage", 40) },
            { "sest_rlc1_recovery", MakeDefinition("sest_rlc1_recovery", "Personnel Recovery", 45) }, { "sest_undersea_operations", MakeDefinition("sest_undersea_operations", "Undersea Operations", 50) },
            { "alpha", MakeDefinition("alpha", "alpha", 40) } };
        Func<string, object> rowFor = id => definitions.TryGetValue(id, out var d) ? RowOf(d, 15) : null;
        var native = NativeRows(RowOf(definitions["sest_undersea_operations"], 15));
        var passage = Specs(out error, "sest_rl05_passage?objective:Passage=completed&objective:Unseen=completed&nolaunch");
        var log = new List<string>();
        object clean = Evidence("Australia", 11, 0, Report(Ammo("Noisemaker", 2, 2, 0)), Objective("Passage", 4), Objective("Unseen", 4), Objective("Boat", 16));
        Check(Evaluate(passage, native, clean, rowFor, log).SequenceEqual(new[] { "sest_rl05_passage" }) && log.Count == 1 && log[0].Contains("AWARDED") && log[0].Contains("launched=0"),
            "RL05: both objectives completed and nothing launched grants the ribbon, with one log line");
        Check(Evaluate(passage, native, Evidence("Australia", 11, 0, Report(Ammo("Torpedo", 1, 0, 0)), Objective("Passage", 4), Objective("Unseen", 4)), rowFor, log).Count == 0 && log.Last().Contains("not met: nolaunch"),
            "one torpedo launched: no runtime ribbon");
        Check(Evaluate(passage, native, Evidence("Australia", 11, 0, Report(), Objective("Passage", 4), Objective("Unseen", 2)), rowFor, log).Count == 0 && log.Last().Contains("objective:Unseen=completed (Failed)"),
            "a failed objective: no runtime ribbon");
        Check(Evaluate(passage, native, Evidence("Australia", 11, 0, Report(), Objective("Passage", 4)), rowFor, log).Count == 0 && log.Last().Contains("not in this mission"),
            "an objective missing from the mission evaluates false");
        var recovery = Specs(out error, "sest_rlc1_recovery?objective:Pilot=completed&rescued>=1");
        Check(Evaluate(recovery, native, Evidence("US", 14, 2, Report(Ammo("Missile", 4, 0, 0)), Objective("Pilot", 4)), rowFor, log).SequenceEqual(new[] { "sest_rlc1_recovery" }) && log.Last().Contains("rescued=2"),
            "RLC1: pilot recovered (rescued >= 1) grants, whatever was fired");
        Check(Evaluate(recovery, native, Evidence("US", 14, 0, Report(), Objective("Pilot", 4)), rowFor, log).Count == 0, "no survivor recovered: no recovery ribbon");
        Check(Evaluate(recovery, native, Evidence("US", 14, -3, Report(), Objective("Pilot", 4)), rowFor, log).Count == 0 && log.Last().Contains("rescued=0"), "a negative count is clamped to 0 as natively");
        var threshold = Specs(out error, "alpha?result>=MajorVictory");
        Check(Evaluate(threshold, native, Evidence("", 16, 0, Report()), rowFor, log).Count == 1 && Evaluate(threshold, native, Evidence("", 15, 0, Report()), rowFor, log).Count == 0,
            "result>= compares the native Result value");
        Check(Evaluate(Specs(out error, "sest_undersea_operations?nolaunch"), native, clean, rowFor, log).Count == 0 && log.Last().Contains("already awarded"),
            "a ribbon the native rules already granted is not added twice");
        Check(Evaluate(Specs(out error, "sest_rl05_passage?rescued>=1|sest_rl05_passage?nolaunch|sest_rl05_passage?nolaunch"), native, clean, rowFor, log).SequenceEqual(new[] { "sest_rl05_passage" }),
            "alternative specs for one ribbon: the first that qualifies grants it, once");
        Check(Evaluate(Specs(out error, "sest_rl05_passage,China?nolaunch"), native, clean, rowFor, log).Count == 0 && log.Last().Contains("commander nation") &&
            Evaluate(Specs(out error, "sest_rl05_passage,Australia?nolaunch"), native, clean, rowFor, log).Count == 1 &&
            Evaluate(Specs(out error, "sest_rl05_passage,US?nolaunch"), native, Evidence("", 11, 0, Report()), rowFor, log).Count == 0, "the commander nation selector is honoured; an empty nation gets only unselected specs");
        Check(Evaluate(Specs(out error, "undefined?nolaunch"), native, clean, rowFor, log).Count == 0 && log.Last().Contains("no [Ribbon_undefined] definition"), "a ribbon without a definition is not granted");
        log.Clear();
        Evaluate(Specs(out error, "a?nolaunch|b?nolaunch|c,China?nolaunch"), native, clean, rowFor, log);
        Check(log.Count == 3, "one log line per evaluated spec");

        // Merge order and the native row round trip.
        var merged = (IList)Invoke(awards, "Merge", NativeRows(RowOf(definitions["sest_undersea_operations"], 15), RowOf(definitions["sest_rl05_passage"], 15)), NativeRows(RowOf(definitions["alpha"], 15)));
        Check(merged.Cast<object>().Select(Id).SequenceEqual(new[] { "alpha", "sest_rl05_passage", "sest_undersea_operations" }), "merged rows follow the native order: Precedence, then DisplayName ignoring case");
        var debriefType = game.GetType("SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel", true);
        string serialized = (string)debriefType.GetMethod("SerializeRibbonAwardRows", All).Invoke(null, new object[] { merged });
        var parsed = ((IEnumerable)debriefType.GetMethod("ParseRibbonAwardRows", All).Invoke(null, new object[] { serialized })).Cast<object>().Select(Id).ToList();
        Check(parsed.SequenceEqual(new[] { "alpha", "sest_rl05_passage", "sest_undersea_operations" }), "the native debrief rows serialize and parse the runtime ribbon like a native one");

        // The persistent commander set: the native union, idempotent.
        var data = new Dictionary<string, string> { { "TaskForceCommanderRibbons", "sest_undersea_operations" } };
        var rules = game.GetType("SeapowerUI.ViewModels.LinearCampaignTaskForceRibbonRules", true);
        var addRows = rules.GetMethod("AddPersistentCommanderRibbonRows", All);
        addRows.Invoke(null, new object[] { data, NativeRows(RowOf(definitions["sest_rl05_passage"], 15)) });
        addRows.Invoke(null, new object[] { data, NativeRows(RowOf(definitions["sest_rl05_passage"], 15)) });
        Check(data["TaskForceCommanderRibbons"] == "sest_undersea_operations,sest_rl05_passage", "the Service Record set gains the runtime ribbon once, however often it is granted");
        addRows.Invoke(null, new object[] { null, NativeRows(RowOf(definitions["sest_rl05_passage"], 15)) });

        NativeGrant(definitions);
    }

    // The real install against the captured assembly with HarmonyLib, then the
    // real native ApplyMissionRibbonAwards with an in-memory campaign ini.
    static void NativeGrant(Dictionary<string, object> definitions)
    {
        var rules = game.GetType("SeapowerUI.ViewModels.LinearCampaignTaskForceRibbonRules", true);
        var iniType = game.GetType("SeaPower.IniHandler", true);
        var apply3 = rules.GetMethods(All).Single(m => m.Name == "ApplyMissionRibbonAwards" && m.GetParameters().Length == 3);
        // Install's own hook calls, as Cecil reads them: the prefix and finalizer
        // on SaveDebriefSnapshot and the postfix on the 3-argument grant. Under
        // mono only the grant can be patched (JIT of the snapshot body needs
        // Globals' Unity-only static constructor); its patch is the real one.
        using (var candidate = AssemblyDefinition.ReadAssembly(rt.Location))
        {
            var install = candidate.MainModule.GetType("Sest.RuntimeFixes.MissionAwards").Methods.Single(m => m.Name == "Install");
            InOrder(install, "MissionAwards.Install: Bind, SaveDebriefSnapshot prefix and finalizer, ApplyMissionRibbonAwards postfix",
                Calls("Sest.RuntimeFixes.MissionAwards", "Bind"),
                i => i.OpCode.Code == Code.Ldsfld && ((FieldReference)i.Operand).Name == "snapshotTarget", i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "BeforeSnapshot",
                i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "io.github.sest-hobby.mission-awards", i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "AfterSnapshot", Calls("Sest.RuntimeFixes.Api", "Hooks"),
                i => i.OpCode.Code == Code.Ldsfld && ((FieldReference)i.Operand).Name == "applyTarget", i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "AfterApply", Calls("Sest.RuntimeFixes.Api", "Postfix"));
        }
        var before = awards.GetMethod("BeforeSnapshot", All); var after = awards.GetMethod("AfterSnapshot", All); var post = awards.GetMethod("AfterApply", All);
        Check(before.GetParameters().Select(p => p.Name).SequenceEqual(new[] { "__0", "__1" }) && after.ReturnType == typeof(void) && after.GetParameters().Length == 0 &&
            post.GetParameters().Select(p => p.Name).SequenceEqual(new[] { "__0", "__1", "__2", "__result" }) && post.GetParameters()[3].ParameterType == apply3.ReturnType.MakeByRefType(),
            "the hook signatures are Harmony's positional arguments, a void finalizer (HarmonyX rethrows with the native stack) and the native result by reference");
        Invoke(rt.GetType("Sest.RuntimeFixes.Api", true), "Postfix", apply3, awards, "AfterApply", "io.github.sest-hobby.mission-awards");
        new HarmonyLib.Harmony("sest.tests.mission-awards-fixture").Patch(awards.GetMethod("PlayerWeaponReport", All), prefix: new HarmonyLib.HarmonyMethod(typeof(MissionAwardsTests).GetMethod("UseFixtureReport", All)));
        Func<MethodBase, string, List<string>> owners = (m, kind) => {
            var info = HarmonyLib.Harmony.GetPatchInfo(m);
            var patches = info == null ? null : kind == "Prefixes" ? info.Prefixes : kind == "Postfixes" ? info.Postfixes : info.Finalizers;
            return patches == null ? new List<string>() : patches.Select(p => p.owner).ToList();
        };
        Check(owners(apply3, "Postfixes").SequenceEqual(new[] { "io.github.sest-hobby.mission-awards" }), "Harmony accepts the by-ref result postfix on the 3-argument ApplyMissionRibbonAwards");

        // A campaign ini held in IniHandler's own cache (no file is read). Its
        // and Log's static constructors ask Unity for the StreamingAssets and
        // data paths, which a Harmony prefix answers with a temporary folder.
        streamingAssets = Path.Combine(Path.GetTempPath(), "SEST-MissionAwards-" + Guid.NewGuid().ToString("N"));
        var application = AppDomain.CurrentDomain.GetAssemblies().Select(a => a.GetType("UnityEngine.Application", false)).First(t => t != null);
        foreach (var path in new[] { "streamingAssetsPath", "dataPath" })
            new HarmonyLib.Harmony("sest.tests.mission-awards-fixture").Patch(application.GetProperty(path).GetGetMethod(), prefix: new HarmonyLib.HarmonyMethod(typeof(MissionAwardsTests).GetMethod("UseTempStreamingAssets", All)));
        // Native logging (SeaPower.Log) is then quiet: no Unity log handler here.
        SetField(game.GetType("SeaPower.Log", true), "_logLevel", System.Enum.ToObject(game.GetType("SeaPower.LogLevel", true), 0));
        object ini = Activator.CreateInstance(iniType, All, null, new object[] { "sest-mission-awards-test.ini" }, null);
        Action<string, Dictionary<string, string>> section = (name, values) => iniType.GetMethod("AddSection", All).Invoke(ini, new object[] { name, new Dictionary<string, string>(values, StringComparer.OrdinalIgnoreCase) });
        section("Mission15", new Dictionary<string, string> { { "TaskForceModeRibbonAwards", "sest_undersea_operations" },
            { "SestRuntimeRibbonAwards", AsRead("SestRuntimeRibbonAwards=sest_rl05_passage?objective:Passage=completed&objective:Unseen=completed&nolaunch|sest_rl05_us,US?nolaunch") } });
        section("Mission16", new Dictionary<string, string> { { "SestRuntimeRibbonAwards", "sest_rl05_passage?nolaunch|broken" } });
        section("RL17", new Dictionary<string, string> { { "SestRuntimeRibbonAwards", "sest_rl05_passage?nolaunch" } });
        foreach (var r in new[] { Tuple.Create("sest_undersea_operations", "Undersea Operations", "50"), Tuple.Create("sest_rl05_passage", "Undersea Passage", "40"), Tuple.Create("sest_rl05_us", "US Passage", "41") })
            section("Ribbon_" + r.Item1, new Dictionary<string, string> { { "DisplayName", r.Item2 }, { "Precedence", r.Item3 }, { "ImagePath", "ribbons/" + r.Item1 + ".png" } });
        // The campaign singleton the grant reads (its static _instance field),
        // with the commander's persistent data.
        object campaign = Uninitialized("SeaPower.LinearCampaign");
        var data = new Dictionary<string, string> { { "TaskForceCommanderNation", "Australia" }, { "TaskForceCommanderRibbons", "sest_undersea_operations" } };
        SetField(campaign, "<PersistentData>k__BackingField", data);
        SetField(game.GetType("SeaPower.Singleton`1", true).MakeGenericType(game.GetType("SeaPower.LinearCampaign", true)), "_instance", campaign);
        Func<int, object> missionAt = index => { object m = Uninitialized("SeaPower.LinearCampaignMission"); SetField(m, "_index", index); return m; };
        // The native grant's own row for mission 15, read by the native rules
        // from the same ini. (Running the native body itself needs Unity's
        // Singleton lookup; the contracts above pin it.)
        object nativeDefinition = rules.GetMethod("ReadRibbonDefinition", All).Invoke(null, new object[] { ini, "sest_undersea_operations" });
        Check(nativeDefinition != null, "the native rules read [Ribbon_<id>] from the in-memory campaign ini");
        Func<IList> native15 = () => NativeRows(nativeDefinition.GetType().GetMethod("ToAwardRow", All).Invoke(nativeDefinition, new object[] { 1, 15, "", "" }));
        Func<object, string> run = report => Grant(ini, 15, "", MakeDebrief(11, 0, report, Objective("Passage", 4), Objective("Unseen", 4)), native15());
        string granted = run(Report(Ammo("Noisemaker", 3, 3, 0)));
        Check(granted == "sest_rl05_passage,sest_undersea_operations" && data["TaskForceCommanderRibbons"] == "sest_undersea_operations,sest_rl05_passage",
            "the runtime ribbon joins the native one in the debrief rows and the commander's Service Record set; the US-only spec is skipped for an Australian commander (" + granted + ")");
        Check(run(Report(Ammo("Noisemaker", 3, 3, 0))) == granted && data["TaskForceCommanderRibbons"] == "sest_undersea_operations,sest_rl05_passage", "a replayed completion rewrites the same rows and keeps the set unchanged");
        Check(run(Report(Ammo("Torpedo", 1, 0, 0))) == "sest_undersea_operations", "a torpedo launch leaves only the native award");
        data["TaskForceCommanderNation"] = "US";
        Check(run(Report()) == "sest_rl05_passage,sest_rl05_us,sest_undersea_operations" && data["TaskForceCommanderRibbons"] == "sest_undersea_operations,sest_rl05_passage,sest_rl05_us",
            "a US commander (TaskForceCommanderNation) also receives the US-only runtime ribbon");
        data["TaskForceCommanderNation"] = "Australia";
        // Outside a debrief snapshot, or for another mission, nothing changes.
        IList plain = native15();
        object[] args = { ini, 15, "", plain };
        awards.GetMethod("AfterApply", All).Invoke(null, args);
        Check(ReferenceEquals(args[3], plain), "outside SaveDebriefSnapshot (no snapshot context) the native result is returned untouched");
        Invoke(awards, "BeforeSnapshot", missionAt(14), MakeDebrief(11, 0, Report()));
        awards.GetMethod("AfterApply", All).Invoke(null, args);
        Invoke(awards, "AfterSnapshot");
        Check(ReferenceEquals(args[3], plain), "a snapshot for another mission index adds nothing");
        Check(Grant(ini, 16, "", MakeDebrief(11, 0, Report()), NativeRows()) == "", "a key with an invalid spec grants nothing (fail closed)");
        Check(Grant(ini, 17, "RL17", MakeDebrief(11, 0, Report()), NativeRows()) == "sest_rl05_passage", "the key is also read from the mission event's own section, as natively");
        Check(Grant(ini, 18, "", MakeDebrief(11, 0, Report()), NativeRows()) == "", "a mission without the key is untouched");
        Check((bool)awards.GetField("active", All).GetValue(null), "parse problems do not disable the feature for other missions");
        // A fault inside the evaluation: native result kept, feature off.
        plain = native15(); args = new object[] { ini, 15, "", plain };
        Invoke(awards, "BeforeSnapshot", missionAt(15), "not a debrief");
        awards.GetMethod("AfterApply", All).Invoke(null, args);
        Invoke(awards, "AfterSnapshot");
        Check(ReferenceEquals(args[3], plain) && !(bool)awards.GetField("active", All).GetValue(null), "an evaluation fault keeps the native result and disables runtime awards for the session");
        Check(Grant(ini, 15, "", MakeDebrief(11, 0, Report(), Objective("Passage", 4), Objective("Unseen", 4)), native15()) == "sest_undersea_operations", "once disabled, native awards are unchanged");
        Invoke(awards, "Bind", game);
        // The prefix and finalizer, installed by Api.Hooks as Install installs
        // them, on a stand-in with SaveDebriefSnapshot's shape: the snapshot
        // context lasts only for the call, and a native fault leaves with its
        // type, message and original stack (HarmonyX rethrows past a void
        // finalizer; one that returns the exception throws it from the patch).
        Invoke(rt.GetType("Sest.RuntimeFixes.Api", true), "Hooks", typeof(MissionAwardsTests).GetMethod("SnapshotStandIn", All), awards, "BeforeSnapshot", null,
            "sest.tests.mission-awards-finalizer", "AfterSnapshot", null);
        snapshotSeen = null;
        SnapshotStandIn(missionAt(15), MakeDebrief(11, 0, Report()));
        Check(snapshotSeen != null && awards.GetField("current", All).GetValue(null) == null, "the prefix holds the snapshot context during the call and the finalizer clears it");
        Exception fault = null;
        snapshotSeen = null;
        try { SnapshotStandIn(missionAt(15), "fault"); }
        catch (Exception e) { fault = e; }
        Check(fault is InvalidOperationException && fault.Message == "native snapshot fault" && (fault.StackTrace ?? "").Contains("NativeFault") &&
            snapshotSeen != null && awards.GetField("current", All).GetValue(null) == null,
            "a native fault passes the void finalizer with its type, message and original stack, and the snapshot context is cleared");
        // The switch: MissionAwards=0 in [Runtime] turns the grants off; default on.
        var policy = rt.GetType("Sest.RuntimeFixes.Policy", true);
        Check((string)Invoke(policy, "TextOption", new[] { "[Runtime]", "MissionAwards=0" }, "MissionAwards", "1") == "0" &&
            (string)Invoke(policy, "TextOption", new[] { "[Runtime]", "TowedSensorGuard=1" }, "MissionAwards", "1") == "1", "MissionAwards=0 reads as off; a file without it leaves the awards on");
        using (var candidate = AssemblyDefinition.ReadAssembly(rt.Location))
            InOrder(candidate.MainModule.GetType("Sest.RuntimeFixes.RuntimeFixesMod").Methods.Single(m => m.Name == "TriggerEntryPoint"), "RuntimeFixesMod installs mission awards only after the native image check and only when MissionAwards is not 0",
                i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "499675cda59912054924ae42297bce7a82b12ca00957dabd684105a24aa353a9", i => i.OpCode.Code == Code.Ldstr && (string)i.Operand == "MissionAwards",
                Calls("Sest.RuntimeFixes.Policy", "TextOption"), Calls("Sest.RuntimeFixes.MissionAwards", "Install"));
        try { Directory.Delete(streamingAssets, true); } catch (DirectoryNotFoundException) { }
    }

    // SaveDebriefSnapshot's shape (its own body cannot be compiled under mono):
    // records the context the prefix set, and faults when the debrief is a string.
    static object snapshotSeen;
    [System.Runtime.CompilerServices.MethodImpl(System.Runtime.CompilerServices.MethodImplOptions.NoInlining)]
    static void NativeFault() { throw new InvalidOperationException("native snapshot fault"); }
    [System.Runtime.CompilerServices.MethodImpl(System.Runtime.CompilerServices.MethodImplOptions.NoInlining)]
    static void SnapshotStandIn(object mission, object debrief)
    {
        snapshotSeen = awards.GetField("current", All).GetValue(null);
        if (debrief is string) NativeFault();
    }

    // The postfix as Harmony calls it, inside a snapshot for that mission.
    static string Grant(object ini, int index, string section, object debrief, IList native)
    {
        object mission = Uninitialized("SeaPower.LinearCampaignMission");
        SetField(mission, "_index", index);
        Invoke(awards, "BeforeSnapshot", mission, debrief);
        try
        {
            object[] args = { ini, index, section, native };
            awards.GetMethod("AfterApply", All).Invoke(null, args);
            return string.Join(",", ((IEnumerable)args[3]).Cast<object>().Select(Id));
        }
        finally { Invoke(awards, "AfterSnapshot"); }
    }

    static int Main(string[] args)
    {
        string refs = Path.GetFullPath(args[0]), runtime = Path.GetFullPath(args[1]), workshop = Path.GetFullPath(args[2]);
        AppDomain.CurrentDomain.AssemblyResolve += (s, e) => { string p = Path.Combine(refs, new AssemblyName(e.Name).Name + ".dll"); return File.Exists(p) ? Assembly.LoadFrom(p) : null; };
        string dcm = Path.Combine(workshop, "3813157776", "DynamicCampaignMod.dll");
        Contracts(refs, dcm);
        int contracts = checks;
        Behaviour(refs, runtime);
        Console.WriteLine("Mission award and Admiralty filing checks passed: " + contracts + " native/DCM contracts, " + (checks - contracts) + " runtime behaviour assertions");
        return 0;
    }
}
