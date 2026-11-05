using System;
using System.Collections.Generic;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    internal const string CampaignHash = "eacdb9a4c0353edd24543b631826e61f7cbcfc4f1a78de4fa80527aa5a2208f4";
    internal const string DecoyHash = "bd173bd5087f5eb3d880b95f9b63fd4efbf90a94ba03097f7a6dcfc588eb1ed6";
    internal const string SubAmmoHash = "f16f9fc4a0ce9f37173af742a15876774f119c1affffb2288ab3b9e92fa0e3a4";
    internal const string SubAmmoDuplicateHash = "f4d7ddb5b54c53718dcfcda1135e4518f85779a9b7a88b6a3487ff13b7808a9e";
    internal const string SecondThrustHash = "5d8c362ec9c35ab5e054c52b2b2f766426700b8d8d9e1a4f4edd5ba4ae7b0a04";
    // R5 (5 Nov 2026): Euromod's Anchor Chain Expansion Pack (Workshop
    // 3784474738) as captured on 3 Nov 2026. WeaponLauncherEffects 1.0.18 and
    // SubModelStabilization 1.1.2 stop themselves on the beta because their
    // Harmony TargetMethod lookups use the stable parameter lists.
    internal const string LauncherEffectsHash = "e79113f4a38f7a034ed8ab42da2e14f931382d77fc522e2cd6d86d4d09dbf717";
    internal const string StabilizationHash = "09f6ec0eff66c6b09ae1565c5eaf797a579be2cc04b22bfccb0a7ef9e57a8eda";
    private const string LaunchPatch = "WeaponLauncherEffectsAnchorChain.WeaponContainerLaunchLauncherEffectsPatch";
    private const string MagazinePatch = "WeaponLauncherEffectsAnchorChain.WeaponContainerMagazineLaunchLauncherEffectsPatch";
    private const string StabilizationPatch = "SubModelStabilizationAnchorChain.VesselLoaderStabilizationPatch";

    private static string AdaptCapturedImage(ModuleDefinition module, ModuleDefinition native, string hash)
    {
        bool identify = hash == IdentifyHash, campaign = hash == CampaignHash, decoy = hash == DecoyHash,
            subAmmo = hash == SubAmmoHash || hash == SubAmmoDuplicateHash, thrust = hash == SecondThrustHash,
            launcherEffects = hash == LauncherEffectsHash, stabilization = hash == StabilizationHash;
        if (!(identify || campaign || decoy || subAmmo || thrust || launcherEffects || stabilization)) return null;
        if (launcherEffects) RequireLauncherSignatures(native);
        if (stabilization) RequireVesselLoaderSignature(native);
        var counts = new SortedDictionary<string, int>(StringComparer.Ordinal);
        void Count(string name) => counts[name] = counts.TryGetValue(name, out int value) ? value + 1 : 1;
        MethodReference Bridge(string name) => module.ImportReference(typeof(BetaCompatibilityCalls).GetMethod(name));
        var location = module.ImportReference(typeof(BetaAssemblyPolicy).GetMethod(nameof(OriginalLocation)));
        var heading = native.GetType("SeaPower.GeoPosition").Methods.Single(m => m.Name == "HeadingToPosition" &&
            m.Parameters.Count == 1 && m.ReturnType.FullName == "System.Single");

        foreach (var type in Types(module.Types)) foreach (var method in type.Methods) {
            if (!method.HasBody) continue;
            if (campaign && type.FullName == "DynamicCampaignMod.Game.GameFacts" && method.Name == "AnyProperty") {
                method.Body.Instructions.Clear(); method.Body.Variables.Clear(); method.Body.ExceptionHandlers.Clear();
                var il = method.Body.GetILProcessor();
                il.Append(Instruction.Create(OpCodes.Ldarg_0)); il.Append(Instruction.Create(OpCodes.Ldarg_1));
                il.Append(Instruction.Create(OpCodes.Call, Bridge(nameof(BetaCompatibilityCalls.CampaignProperty))));
                il.Append(Instruction.Create(OpCodes.Ret)); Count("facts-property");
                continue;
            }
            // Beta's WeaponContainer.launch returns false for a failed launch
            // and still removes the dud from _weapons. The author's launch
            // postfix spawns effects for whichever weapon left the container,
            // so it is gated on the launch result, as the author's own
            // magazine postfix already is.
            if (launcherEffects && type.FullName == LaunchPatch && method.Name == "Postfix") {
                if (!method.IsStatic || method.Parameters.Count != 2 || method.Parameters[0].Name != "__instance" ||
                    method.Parameters[1].Name != "__state" || method.Body.ExceptionHandlers.Count != 0)
                    throw new InvalidOperationException("Inspected WeaponLauncherEffects launch postfix changed");
                method.Parameters.Add(new ParameterDefinition("__result", Mono.Cecil.ParameterAttributes.None, module.TypeSystem.Boolean));
                var gate = method.Body.GetILProcessor(); var first = method.Body.Instructions[0];
                gate.InsertBefore(first, Instruction.Create(OpCodes.Ldarg_2));
                gate.InsertBefore(first, Instruction.Create(OpCodes.Brtrue, first));
                gate.InsertBefore(first, Instruction.Create(OpCodes.Ret));
                Count("launch-result");
            }
            // Beta's loadShipFromInternalResources is void and takes the
            // caller's VesselParameters first, as vp. HarmonyX binds a patch
            // parameter by the original's parameter name, so the postfix's
            // __result (the stable return value) becomes vp: the same object.
            if (stabilization && type.FullName == StabilizationPatch && method.Name == "Postfix") {
                if (!method.IsStatic || method.Parameters.Count != 2 || method.Parameters[0].Name != "vesselIniName" ||
                    method.Parameters[1].Name != "__result" || method.Parameters[1].ParameterType.FullName != "SeaPower.VesselParameters")
                    throw new InvalidOperationException("Inspected SubModelStabilization postfix changed");
                method.Parameters[1].Name = "vp"; Count("result-argument");
            }
            bool launcherTarget = launcherEffects && method.Name == "TargetMethod" && (type.FullName == LaunchPatch || type.FullName == MagazinePatch);
            bool stabilizationTarget = stabilization && method.Name == "TargetMethod" && type.FullName == StabilizationPatch;
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
                if (instruction.Operand is not MethodReference call) continue;
                string owner = call.DeclaringType.FullName;
                if (owner == "System.Reflection.Assembly" && call.Name == "get_Location" && call.Parameters.Count == 0) {
                    instruction.OpCode = OpCodes.Call; instruction.Operand = location; Count("locations");
                }
                else if ((launcherTarget || stabilizationTarget) && owner == "HarmonyLib.AccessTools" && call.Name == "Method" &&
                    call.Parameters.Count == 4 && !call.HasThis) {
                    instruction.OpCode = OpCodes.Call;
                    instruction.Operand = Bridge(launcherTarget ? nameof(BetaCompatibilityCalls.LauncherEffectsMethod) : nameof(BetaCompatibilityCalls.StabilizationMethod));
                    Count(launcherTarget ? "launch-reflection" : "target-method");
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
                else if ((identify || campaign) && owner == "SeaPower.GeoPosition" && call.Name == "CourseTo" &&
                    call.HasThis && call.Parameters.Count == 1 && call.ReturnType.FullName == "System.Single") {
                    instruction.Operand = module.ImportReference(heading); Count("bearings");
                }
                else if (subAmmo && owner == "SeaPower.GeoPosition" && call.Name == "OffsetVector" && call.HasThis &&
                    ParameterTypes(call,"UnityEngine.Vector3")) {
                    instruction.Operand=module.ImportReference(native.GetType("SeaPower.GeoPosition").Methods.Single(m=>m.Name=="OffsetByGridVector"));
                    Count("offset-grid");
                }
                else if (decoy && owner == "SeaPower.Vehicle" && call.Name == "get_ViewModel" && call.Parameters.Count == 0) {
                    instruction.OpCode=OpCodes.Call; instruction.Operand=Bridge(nameof(BetaCompatibilityCalls.VehicleViewModel)); Count("vehicle-view");
                }
                else if (decoy && owner == "SeapowerUI.ViewModels.WeaponContactViewModel" && call.Name == "set_LineToTargetColor") {
                    instruction.OpCode=OpCodes.Call; instruction.Operand=Bridge(nameof(BetaCompatibilityCalls.SetDecoyLineColor)); Count("contact-color");
                }
                else if ((subAmmo || thrust) && owner == "SeaPower.Utils" && call.Name == "openIniFile" &&
                    !call.HasThis && ParameterTypes(call, "System.String", "System.Boolean", "System.Boolean")) {
                    AppendDefaults(module, native, method, instruction, call, "ini"); Count("ini");
                }
                else if (subAmmo && owner == "SeaPower.FileManager" && call.Name == "GetFile" &&
                    call.HasThis && ParameterTypes(call, "System.String", "System.String")) {
                    instruction.OpCode = OpCodes.Call; instruction.Operand = Bridge(nameof(BetaCompatibilityCalls.GetLegacyFile)); Count("file");
                }
                else if (campaign && ((owner == "SeaPower.FileManager" && (call.Name == "GetDirectories" || call.Name == "GetFiles") && call.Parameters.Count == 1) ||
                    (owner == "SeaPower.MissionManager" && call.Name == "DoUnload" && call.Parameters.Count == 0) ||
                    (owner == "SeaPower.ReactionTime" && call.Name == "Acquisition" && call.Parameters.Count == 2) ||
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
                else if (decoy && type.FullName == "EnhancedDecoyMod.Hooks" && method.Name == "ContactConstructor" &&
                    call.Name == "FindLast" && owner.StartsWith("System.Collections.Generic.List`1<")) {
                    instruction.OpCode = OpCodes.Call; instruction.Operand = Bridge(nameof(BetaCompatibilityCalls.FindDecoyContactExit)); Count("contact-exit");
                }
                else if (identify && type.FullName == "IdentifyExpanded.BroadcastService" && method.Name == "TryStartEnemyHail" &&
                    owner == "SeaPower.ObjectBase" && call.Name == "get_IsPlayerUnit") {
                    instruction.OpCode = OpCodes.Call; instruction.Operand = Bridge(nameof(BetaCompatibilityCalls.SkipEnemyHailCandidate)); Count("hail-guard");
                }
            }
        }
        // Audits are against the captured images, not guesses about filename or
        // version. Unexpected counts reject the private image before CLR load.
        string audit = String.Join(", ", counts.Select(x => x.Key + "=" + x.Value));
        string expected = identify ? "bearings=10, hail-guard=1, locations=2, ui=5" :
            campaign ? "Acquisition=1, DoUnload=1, GetDirectories=1, GetFiles=1, SetAttackAtWaypointTask=2, attack-reflection=1, bearing-reflection=1, bearings=1, facts-property=1, mission-get=3, mission-set=1, secondary-side=6, speed-make=1, speed-set=1, ui=24" :
            decoy ? "contact-color=1, contact-exit=1, locations=2, ui=1, vehicle-view=4" : thrust ? "ini=1, locations=1" :
            launcherEffects ? "launch-reflection=2, launch-result=1, locations=2" :
            stabilization ? "locations=2, result-argument=1, target-method=1" : "file=1, ini=5, locations=1, offset-grid=2";
        if (audit != expected) throw new InvalidOperationException(module.Assembly.Name.Name + " beta rewrite audit changed: " + audit);
        return audit;
    }

    // The two shapes the R5 bridges rely on, asserted on the pinned native
    // image before any rewrite; a different beta fails closed.
    private static void RequireLauncherSignatures(ModuleDefinition native)
    {
        var container = native.GetType("SeaPower.WeaponContainer");
        foreach (var (name, count) in new[] { ("launch", 6), ("LaunchFromMagazine", 7) }) {
            var method = container.Methods.Single(m => m.Name == name);
            var last = method.Parameters.LastOrDefault();
            if (method.Parameters.Count != count || method.ReturnType.FullName != "System.Boolean" || last == null ||
                last.Name != "failedLaunch" || last.ParameterType.FullName != "System.Boolean" || !last.IsOptional ||
                !last.HasConstant || !Equals(last.Constant, false))
                throw new InvalidOperationException("Inspected beta WeaponContainer." + name + " shape changed");
        }
    }

    private static void RequireVesselLoaderSignature(ModuleDefinition native)
    {
        var load = native.GetType("SeaPower.VesselLoader").Methods.Single(m => m.Name == "loadShipFromInternalResources");
        if (load.Parameters.Count != 11 || load.ReturnType.FullName != "System.Void" || load.Parameters[0].Name != "vp" ||
            load.Parameters[0].ParameterType.FullName != "SeaPower.VesselParameters" || load.Parameters[3].Name != "vesselIniName" ||
            load.Parameters[3].ParameterType.FullName != "System.String")
            throw new InvalidOperationException("Inspected beta VesselLoader.loadShipFromInternalResources shape changed");
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
