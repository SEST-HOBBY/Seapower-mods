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

    static int Main(string[] args)
    {
        string refs = Path.GetFullPath(args[0]), runtime = Path.GetFullPath(args[1]), workshop = Path.GetFullPath(args[2]);
        AppDomain.CurrentDomain.AssemblyResolve += (s, e) => { string p = Path.Combine(refs, new AssemblyName(e.Name).Name + ".dll"); return File.Exists(p) ? Assembly.LoadFrom(p) : null; };
        string dcm = Path.Combine(workshop, "3813157776", "DynamicCampaignMod.dll");
        Contracts(refs, dcm);
        Console.WriteLine("Native debrief award and DCM filing contracts passed: " + checks);
        return 0;
    }
}
