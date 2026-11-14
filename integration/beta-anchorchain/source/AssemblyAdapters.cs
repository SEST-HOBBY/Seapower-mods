using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    // R6 (7 Nov 2026): later adapters live one per file,
    // AssemblyAdapters.<Plugin>.cs. Each file defines one private static
    // method named <Plugin>Adapter that returns an ImageAdapter. The loader
    // finds them by reflection, so adding an adapter edits no shared list.
    internal sealed class ImageAdapter
    {
        internal string Name;
        // The pinned author images; any other hash loads unadapted, as before.
        internal string[] Hashes = Array.Empty<string>();
        // Exact InvalidNativeFields findings this adapter re-encodes. The
        // written image is checked again and must have none left.
        internal string[] AcceptedNativeFields = Array.Empty<string>();
        // An assembly whose dependents the policy otherwise skips; set only by
        // that assembly's own adapter.
        internal string ReleasesDependentsOf;
        // Asserts the native shapes the rewrites rely on; throws on a mismatch.
        internal Action<ModuleDefinition> RequireNative;
        // Runs once for every method with a body, before the shared rules.
        // Returns true when the shared instruction loop must skip the method.
        internal Func<AdapterScope, TypeDefinition, MethodDefinition, bool> RewriteMethod;
        // Runs for every call instruction, before the shared call rules.
        // Returns true when it handled the instruction.
        internal Func<AdapterScope, TypeDefinition, MethodDefinition, Instruction, MethodReference, bool> RewriteCall;
        // Runs once after every method has been visited.
        internal Action<AdapterScope> Finish;
        internal string ExpectedAudit;
    }

    internal sealed class AdapterScope
    {
        internal ModuleDefinition Module, Native;
        internal Action<string> Count;
        internal MethodReference Bridge(string name)
            => Module.ImportReference(typeof(BetaCompatibilityCalls).GetMethod(name)
                ?? throw new InvalidOperationException("Missing beta bridge " + name));
        internal void ExpandBranches(MethodDefinition method)
        {
            foreach (var instruction in method.Body.Instructions) ExpandBranch(instruction);
        }
        internal void Replace(MethodDefinition method, Instruction instruction, params Instruction[] extra)
            => ReplaceCall(method, instruction, extra);
    }

    private static ImageAdapter[] adapters;
    internal static IReadOnlyList<ImageAdapter> Adapters => adapters ??= typeof(BetaAssemblyPolicy)
        .GetMethods(BindingFlags.NonPublic | BindingFlags.Static)
        .Where(m => m.ReturnType == typeof(ImageAdapter) && m.GetParameters().Length == 0 && m.Name.EndsWith("Adapter", StringComparison.Ordinal))
        .OrderBy(m => m.Name, StringComparer.Ordinal)
        .Select(m => (ImageAdapter)m.Invoke(null, null))
        .ToArray();

    internal static ImageAdapter AdapterFor(string hash) => Adapters.SingleOrDefault(a => a.Hashes.Contains(hash));

    // For the managed tests: each R6 adapter must have its own checks.
    public static string[] AdapterNames() => Adapters.Select(a => a.Name).ToArray();

    internal const string CampaignHash = "eacdb9a4c0353edd24543b631826e61f7cbcfc4f1a78de4fa80527aa5a2208f4";
    internal const string GroupHash = "6230e8e78e2ba7ba222241d0c3dcc881d2507ebeeb4eab24b6401cc9144283dd";
    internal const string StrikeHash = "093b8ad6478641948b0eaca720427e5cef3c8b4440142f6c33b16339dc2fc941";

    private static string AdaptCapturedImage(ModuleDefinition module, ModuleDefinition native, string hash)
    {
        bool identify = hash == IdentifyHash, campaign = hash == CampaignHash,
            group = hash == GroupHash, strike = hash == StrikeHash;
        var adapter = AdapterFor(hash);
        if (!(identify || campaign || group || strike || adapter != null)) return null;
        adapter?.RequireNative?.Invoke(native);
        var counts = new SortedDictionary<string, int>(StringComparer.Ordinal);
        void Count(string name) => counts[name] = counts.TryGetValue(name, out int value) ? value + 1 : 1;
        if (campaign) CampaignSalvoTarget(module, native, Count);
        var scope = adapter == null ? null : new AdapterScope { Module = module, Native = native, Count = Count };
        MethodReference Bridge(string name) => module.ImportReference(typeof(BetaCompatibilityCalls).GetMethod(name));
        var location = module.ImportReference(typeof(BetaAssemblyPolicy).GetMethod(nameof(OriginalLocation)));
        var heading = native.GetType("SeaPower.GeoPosition").Methods.Single(m => m.Name == "HeadingToPosition" &&
            m.Parameters.Count == 1 && m.ReturnType.FullName == "System.Single");

        foreach (var type in Types(module.Types)) foreach (var method in type.Methods.ToArray()) {
            if (!method.HasBody) continue;
            if (adapter?.RewriteMethod != null && adapter.RewriteMethod(scope, type, method)) continue;
            if (campaign && type.FullName == "DynamicCampaignMod.Game.GameFacts" && method.Name == "AnyProperty") {
                method.Body.Instructions.Clear(); method.Body.Variables.Clear(); method.Body.ExceptionHandlers.Clear();
                var il = method.Body.GetILProcessor();
                il.Append(Instruction.Create(OpCodes.Ldarg_0)); il.Append(Instruction.Create(OpCodes.Ldarg_1));
                il.Append(Instruction.Create(OpCodes.Call, Bridge(nameof(BetaCompatibilityCalls.CampaignProperty))));
                il.Append(Instruction.Create(OpCodes.Ret)); Count("facts-property");
                continue;
            }
            bool attackLookup = campaign && method.Body.Instructions.Any(i => i.OpCode == OpCodes.Ldstr && Equals(i.Operand, "SetAttackAtWaypointTask"));
            // Insertions can extend existing short-branch distances. Expand all
            // short branches once; instruction targets and EH bounds stay valid.
            foreach (var instruction in method.Body.Instructions.ToArray()) {
                ExpandBranch(instruction);
                if (campaign && instruction.OpCode == OpCodes.Ldstr && Equals(instruction.Operand, "CourseTo")) {
                    instruction.Operand = "HeadingToPosition"; Count("bearing-reflection");
                }
                if (campaign && instruction.Operand is FieldReference field && field.DeclaringType.FullName == "SeaPower.Globals") {
                    if (field.Name == "_secondEnemyTaskforce" && instruction.OpCode == OpCodes.Ldsfld) {
                        instruction.OpCode = OpCodes.Call;
                        instruction.Operand = module.ImportReference(typeof(BetaCompatibilityCalls).GetProperty(nameof(BetaCompatibilityCalls.SecondaryEnemyTaskforce)).GetGetMethod());
                        Count("secondary-side");
                    }
                    else if (field.Name == "currentMissionFilePath" && instruction.OpCode == OpCodes.Ldsfld) {
                        instruction.OpCode = OpCodes.Call;
                        instruction.Operand = module.ImportReference(native.GetType("SeaPower.Globals").Methods.Single(m => m.Name == "get_currentMissionFilePath"));
                        Count("mission-get");
                    }
                    else if (field.Name == "currentMissionFilePath" && instruction.OpCode == OpCodes.Stsfld) {
                        instruction.OpCode = OpCodes.Call; instruction.Operand = Bridge(nameof(BetaCompatibilityCalls.SetCampaignMissionPath));
                        Count("mission-set");
                    }
                }
                // Build 261106 promotes these author-visible fields to native
                // properties. Keep native getter/setter behavior in charge.
                if (instruction.Operand is FieldReference promoted &&
                    (campaign && promoted.DeclaringType.FullName == "SeaPower.AI" && promoted.Name == "_objectToDestroy")) {
                    string accessor = instruction.OpCode == OpCodes.Ldfld ? "get_" :
                        instruction.OpCode == OpCodes.Stfld ? "set_" : throw new InvalidOperationException("Uninspected promoted field opcode");
                    var actual = native.GetType(promoted.DeclaringType.FullName).Methods.Single(m => m.Name == accessor + promoted.Name &&
                        m.HasThis && (accessor == "get_" ? m.Parameters.Count == 0 && m.ReturnType.FullName == promoted.FieldType.FullName :
                        m.Parameters.Count == 1 && m.Parameters[0].ParameterType.FullName == promoted.FieldType.FullName));
                    instruction.OpCode = OpCodes.Call;
                    instruction.Operand = module.ImportReference(actual);
                    Count("attack-property");
                }
                if (instruction.Operand is not MethodReference call) continue;
                if (adapter?.RewriteCall != null && adapter.RewriteCall(scope, type, method, instruction, call)) continue;
                string owner = call.DeclaringType.FullName;
                if (owner == "System.Reflection.Assembly" && call.Name == "get_Location" && call.Parameters.Count == 0) {
                    instruction.OpCode = OpCodes.Call; instruction.Operand = location; Count("locations");
                }
                else if (owner == "SeaPower.UI_Parameters" && call.Name.StartsWith("get_TM_") && !call.HasThis && call.Parameters.Count == 0 &&
                    (call.ReturnType.FullName == "Noesis.Color" || call.ReturnType.FullName == "Noesis.SolidColorBrush" || call.ReturnType.FullName == "System.Single")) {
                    string key=call.Name.Substring(7);
                    if (key.EndsWith("_Brush")) key=key.Substring(0,key.Length-6);
                    string api=call.ReturnType.FullName == "Noesis.Color" ? "MapColor" : call.ReturnType.FullName == "Noesis.SolidColorBrush" ? "MapBrush" : "MapValue";
                    var reader=native.GetType("SeaPower.UI_Parameters").Methods.Single(m=>m.Name==api && m.Parameters.Count==2);
                    ReplaceCall(method,instruction,Instruction.Create(OpCodes.Ldstr,key),Instruction.Create(OpCodes.Ldc_I4_0),
                        Instruction.Create(OpCodes.Call,module.ImportReference(reader))); Count("ui");
                }
                else if (group && owner == "SeapowerUI.MapFormationViewModel" && call.Name == "get_MembershipDisplay" && call.HasThis && call.Parameters.Count == 0) {
                    // Native formation labels moved to MapLabelRegistry. This
                    // old collection identity check must never match another
                    // ItemsControl; retain the author's explicit binding/name
                    // checks and all its TextBlock/container handling.
                    instruction.OpCode = OpCodes.Call; instruction.Operand = Bridge(nameof(BetaCompatibilityCalls.LegacyFormationMembership));
                    Count("formation-membership");
                }
                else if (strike && owner == "SeaPower.ObjectBase" && call.Name == "GetMaxEngagementRanges" && call.Parameters.Count == 6) {
                    AppendDefaults(module,native,method,instruction,call,"engagement-ranges"); Count("engagement-ranges");
                }
                else if (campaign && owner == "SeaPower.TerrainUtils" && call.Name == "GetHeightAt" &&
                    !call.HasThis && ParameterTypes(call, "SeaPower.GeoPosition", "System.Boolean", "System.Boolean")) {
                    AppendDefaults(module, native, method, instruction, call, "terrain-height"); Count("terrain-height");
                }
                else if (campaign && owner == "SeaPower.Aircraft" && call.Name == "UpdateFuelConsumption" &&
                    call.HasThis && ParameterTypes(call, "System.Single")) {
                    // The captured campaign only requests a display refresh,
                    // passing zero distance. Native 261106 separates burning
                    // fuel from this refresh and takes no distance argument.
                    if (instruction.Previous.OpCode != OpCodes.Ldc_R4 || !Equals(instruction.Previous.Operand, 0f))
                        throw new InvalidOperationException("Uninspected campaign fuel-consumption distance");
                    var refresh = native.GetType(owner).Methods.Single(m => m.Name == call.Name && m.HasThis &&
                        m.Parameters.Count == 0 && m.ReturnType.FullName == "System.Void");
                    ReplaceCall(method, instruction, Instruction.Create(OpCodes.Pop), Instruction.Create(OpCodes.Call, module.ImportReference(refresh)));
                    Count("fuel-refresh");
                }
                else if ((identify || campaign) && owner == "SeaPower.GeoPosition" && call.Name == "CourseTo" &&
                    call.HasThis && call.Parameters.Count == 1 && call.ReturnType.FullName == "System.Single") {
                    instruction.Operand = module.ImportReference(heading); Count("bearings");
                }
                else if (campaign && ((owner == "SeaPower.FileManager" && (call.Name == "GetDirectories" || call.Name == "GetFiles") && call.Parameters.Count == 1) ||
                    (owner == "SeaPower.MissionManager" && call.Name == "DoUnload" && call.Parameters.Count == 0) ||
                    (owner == "SeaPower.ReactionTime" && call.Name == "Acquisition" && call.Parameters.Count == 2) ||
                    // 8 Nov image adds nation=null; retain native INI-based nation inference.
                    (owner == "SeaPower.LoadoutSummary" && call.Name == "HasNightCapableSensors" &&
                        ParameterTypes(call, "SeaPower.IniHandler", "System.String", "System.Boolean")) ||
                    (owner == "SeaPower.ObjectBase" && call.Name == "SetAttackAtWaypointTask" && call.Parameters.Count == 10))) {
                    AppendDefaults(module, native, method, instruction, call, call.Name); Count(call.Name);
                }
                else if (campaign && owner == "SeaPower.ConstantSpeed" && call.Name == ".ctor" && instruction.OpCode == OpCodes.Newobj &&
                    ParameterTypes(call, "System.Single", "SeaPower.ObjectBase")) {
                    instruction.OpCode = OpCodes.Call; instruction.Operand = Bridge(nameof(BetaCompatibilityCalls.ConstantSpeedRequest)); Count("speed-make");
                }
                else if (campaign && owner == "SeaPower.ObjectBase" && call.Name == "SetSpeedCommand" &&
                    ParameterTypes(call, "SeaPower.ISpeedCommand")) {
                    instruction.OpCode = OpCodes.Call; instruction.Operand = Bridge(nameof(BetaCompatibilityCalls.SetSpeedRequest)); Count("speed-set");
                }
                else if (attackLookup && owner == "HarmonyLib.AccessTools" && call.Name == "Method" && call.Parameters.Count == 4) {
                    instruction.OpCode = OpCodes.Call; instruction.Operand = Bridge(nameof(BetaCompatibilityCalls.CampaignMethod)); Count("attack-reflection");
                }
                else if (identify && type.FullName == "IdentifyExpanded.BroadcastService" && method.Name == "TryStartEnemyHail" &&
                    owner == "SeaPower.ObjectBase" && call.Name == "get_IsPlayerUnit") {
                    instruction.OpCode = OpCodes.Call; instruction.Operand = Bridge(nameof(BetaCompatibilityCalls.SkipEnemyHailCandidate)); Count("hail-guard");
                }
                else if (identify && type.FullName == "IdentifyExpanded.BroadcastService" && method.Name == "FindSender" &&
                    owner == "SeaPower.ObjectBase" && call.Name == "get_IsPlayerUnit") {
                    instruction.OpCode = OpCodes.Call; instruction.Operand = Bridge(nameof(BetaCompatibilityCalls.IsInitializedPlayerUnit)); Count("sender-guard");
                }
            }
        }
        adapter?.Finish?.Invoke(scope);
        // Audits are against the captured images, not guesses about filename or
        // version. Unexpected counts reject the private image before CLR load.
        string audit = String.Join(", ", counts.Select(x => x.Key + "=" + x.Value));
        string expected = adapter != null ? adapter.ExpectedAudit : identify ? "bearings=10, hail-guard=1, locations=2, sender-guard=3, ui=5" :
            campaign ? "Acquisition=1, DoUnload=1, GetDirectories=1, GetFiles=1, HasNightCapableSensors=1, SetAttackAtWaypointTask=2, attack-property=14, attack-reflection=1, bearing-reflection=1, bearings=1, facts-property=1, fuel-refresh=1, mission-get=3, mission-set=1, salvo-applied=1, salvo-fact=1, salvo-target=1, secondary-side=6, speed-make=1, speed-set=1, terrain-height=1, ui=24" :
            group ? "formation-membership=1" : "engagement-ranges=1, ui=4";
        if (audit != expected) throw new InvalidOperationException(module.Assembly.Name.Name + " beta rewrite audit changed: " + audit);
        return audit;
    }

    private static bool ParameterTypes(MethodReference method, params string[] names)
        => method.Parameters.Select(p => p.ParameterType.FullName).SequenceEqual(names);

    private static void AppendDefaults(ModuleDefinition module, ModuleDefinition native, MethodDefinition method,
        Instruction instruction, MethodReference old, string reason)
    {
        var actual = native.GetType(old.DeclaringType.FullName).Methods.Single(m => m.Name == old.Name && m.HasThis == old.HasThis &&
            m.ReturnType.FullName == old.ReturnType.FullName && m.Parameters.Count > old.Parameters.Count &&
            m.Parameters.Take(old.Parameters.Count).Select(p => p.ParameterType.FullName).SequenceEqual(old.Parameters.Select(p => p.ParameterType.FullName)) &&
            m.Parameters.Skip(old.Parameters.Count).All(p => p.IsOptional && p.HasConstant));
        var extra = new List<Instruction>();
        foreach (var parameter in actual.Parameters.Skip(old.Parameters.Count)) {
            object value = parameter.Constant;
            if (value == null) extra.Add(Instruction.Create(OpCodes.Ldnull));
            else if (value is bool boolean) extra.Add(Instruction.Create(OpCodes.Ldc_I4, boolean ? 1 : 0));
            else if (value is int number) extra.Add(Instruction.Create(OpCodes.Ldc_I4, number));
            else throw new InvalidOperationException("Uninspected beta optional default: " + reason + "/" + parameter.Name);
        }
        extra.Add(Instruction.Create(instruction.OpCode, module.ImportReference(actual)));
        ReplaceCall(method,instruction,extra.ToArray());
    }

    private static void ReplaceCall(MethodDefinition method, Instruction instruction, params Instruction[] extra)
    {
        // Retain the old instruction object as the FIRST argument insertion:
        // branches/EH starts aimed at the old call must execute the defaults too.
        instruction.OpCode = extra[0].OpCode; instruction.Operand = extra[0].Operand;
        var il = method.Body.GetILProcessor(); var previous = instruction;
        foreach (var added in extra.Skip(1)) { il.InsertAfter(previous, added); previous = added; }
    }

    private static void ExpandBranch(Instruction instruction)
    {
        switch (instruction.OpCode.Code) {
            case Code.Br_S: instruction.OpCode=OpCodes.Br; break;
            case Code.Brfalse_S: instruction.OpCode=OpCodes.Brfalse; break;
            case Code.Brtrue_S: instruction.OpCode=OpCodes.Brtrue; break;
            case Code.Beq_S: instruction.OpCode=OpCodes.Beq; break;
            case Code.Bge_S: instruction.OpCode=OpCodes.Bge; break;
            case Code.Bge_Un_S: instruction.OpCode=OpCodes.Bge_Un; break;
            case Code.Bgt_S: instruction.OpCode=OpCodes.Bgt; break;
            case Code.Bgt_Un_S: instruction.OpCode=OpCodes.Bgt_Un; break;
            case Code.Ble_S: instruction.OpCode=OpCodes.Ble; break;
            case Code.Ble_Un_S: instruction.OpCode=OpCodes.Ble_Un; break;
            case Code.Blt_S: instruction.OpCode=OpCodes.Blt; break;
            case Code.Blt_Un_S: instruction.OpCode=OpCodes.Blt_Un; break;
            case Code.Bne_Un_S: instruction.OpCode=OpCodes.Bne_Un; break;
            case Code.Leave_S: instruction.OpCode=OpCodes.Leave; break;
        }
    }
}
