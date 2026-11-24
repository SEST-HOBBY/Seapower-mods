// Multi-Stage Missiles 1.7.18 (MultiStageMissiles.dll, 33a8841b, Workshop
// 3784474738) on 0.9.3-261123 (ea653e49). Its chaff submunition builds a
// throwaway WeaponSystemChaff and hands it to ChaffCloud.launchChaffEffect.
// 261123 changed two members that path names:
//  - WeaponSystemChaff._ammoInUse is a read-only property (round 0's Ammo).
//    SubmunitionPayloadApi.LaunchChaff stores a new Ammunition into it once.
//    Nothing reads it back: the throwaway system is never registered, and
//    ChaffCloud reads only the system's effect object, effect position and
//    parameters. The store becomes pop; pop (chaff-ammo-discard).
//  - launchChaffEffect gained an optional int32 cartridges = 1. The one call
//    passes that default (chaff-cartridges), and the author's own startup
//    check in SubmunitionPayloadApi.Validate asks for the 4-argument
//    signature instead of the 3-argument one (chaff-validate-signature), so
//    it keeps the torpedo-drop and chaff payloads on.
// The StageSimulation, ImpactPool and Propulsion transpilers and the
// Torpedo.OnFixedUpdate hook are judged by the author's own validators
// (R6_MultiStageChaff runs them).
using System;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    internal const string MultiStageChaffHash = "33a8841b0884bc7effaa59700f3c852e151d1d9bf0e7263b4f3a22a07c9b98f3";
    internal const string MultiStageChaffAudit = "chaff-ammo-discard=1, chaff-cartridges=1, chaff-validate-signature=1, locations=2";
    private const string MultiStagePayloadApi = "MultiStageMissilesAnchorChain.SubmunitionPayloadApi";

    private static ImageAdapter MultiStageChaffAdapter() => new ImageAdapter {
        Name = "MultiStageChaff", Hashes = new[] { MultiStageChaffHash },
        RequireNative = MultiStageChaffRequireNative,
        RewriteMethod = MultiStageChaffRewrite,
        RewriteCall = MultiStageChaffCall,
        ExpectedAudit = MultiStageChaffAudit,
    };

    private static ModuleDefinition multiStageChaffNative;

    private static void MultiStageChaffRequireNative(ModuleDefinition native)
    {
        CurrentNativeSnapshot(native);
        if (ReferenceEquals(multiStageChaffNative, native)) return;
        ChaffRoundAmmoGetter(native);
        var cloud = native.GetType("SeaPower.ChaffCloud");
        var launch = cloud.Methods.Where(m => m.Name == "launchChaffEffect").ToList();
        var cartridges = launch.Count == 1 ? launch[0].Parameters.LastOrDefault() : null;
        if (launch.Count != 1 || !launch[0].HasThis || launch[0].ReturnType.FullName != "System.Void" ||
            !ParameterTypes(launch[0], "SeaPower.WeaponSystemChaff", "UnityEngine.GameObject", "UnityEngine.GameObject", "System.Int32") ||
            cartridges.Name != "cartridges" || !cartridges.IsOptional || !cartridges.HasConstant || !Equals(cartridges.Constant, 1))
            throw new InvalidOperationException("Inspected 261123 chaff cloud launch signature changed");
        // The discarded store is safe only while the cloud never reaches the
        // parent system's rounds or ammunition, and no other game code reaches
        // the cloud's parent system.
        var cloudTypes = Types(new[] { cloud }).ToList();
        bool RoundOrAmmo(MemberReference member) =>
            member.DeclaringType?.FullName == "SeaPower.WeaponSystemChaff/Round" ||
            (member.DeclaringType?.FullName == "SeaPower.WeaponSystemChaff" && (member.Name == "_rounds" || member.Name == "get__ammoInUse")) ||
            (member is TypeReference type && type.FullName == "SeaPower.WeaponSystemChaff/Round");
        if (cloudTypes.SelectMany(t => t.Methods).Where(m => m.HasBody).SelectMany(m => m.Body.Instructions)
                .Any(i => i.Operand is MemberReference member && RoundOrAmmo(member)) ||
            cloudTypes.SelectMany(t => t.Methods).Any(m => m.ReturnType.FullName == "SeaPower.WeaponSystemChaff") ||
            cloud.Fields.SingleOrDefault(f => f.Name == "_parentSystem")?.IsPrivate != true ||
            Types(native.Types).Where(t => !cloudTypes.Contains(t)).SelectMany(t => t.Methods).Where(m => m.HasBody)
                .SelectMany(m => m.Body.Instructions)
                .Any(i => i.Operand is FieldReference f && f.Name == "_parentSystem" && f.DeclaringType.FullName == "SeaPower.ChaffCloud"))
            throw new InvalidOperationException("Inspected 261123 chaff cloud use of its parent system changed");
        var ammunition = native.GetType("SeaPower.Ammunition").Methods.Count(m => m.IsConstructor && !m.IsStatic &&
            ParameterTypes(m, "SeaPower.AmmunitionParameters"));
        var system = native.GetType("SeaPower.WeaponSystemChaff").Methods.Count(m => m.IsConstructor && !m.IsStatic &&
            ParameterTypes(m, "SeaPower.ObjectBase", "SeaPower.WeaponParameters"));
        if (ammunition != 1 || system != 1)
            throw new InvalidOperationException("Inspected 261123 chaff system and ammunition constructors changed");
        multiStageChaffNative = native;
    }

    private static bool MultiStageChaffRewrite(AdapterScope scope, TypeDefinition type, MethodDefinition method)
    {
        var il = method.Body.Instructions;
        var stores = il.Where(i => i.Operand is FieldReference f && f.Name == "_ammoInUse" &&
            f.DeclaringType.FullName == "SeaPower.WeaponSystemChaff").ToList();
        bool launch = type.FullName == MultiStagePayloadApi && method.Name == "LaunchChaff";
        if (stores.Count != 0 && !launch)
            throw new InvalidOperationException("Uninspected Multi-Stage chaff ammunition access in " + type.FullName + "::" + method.Name);
        if (launch) {
            var store = stores.Count == 1 ? stores[0] : null;
            if (method.Body.CodeSize != 602 || store == null || store.Offset != 0x017d || store.OpCode != OpCodes.Stfld ||
                !(store.Previous.OpCode == OpCodes.Newobj && store.Previous.Operand is MethodReference ctor &&
                  ctor.FullName == "System.Void SeaPower.Ammunition::.ctor(SeaPower.AmmunitionParameters)") ||
                il.Count(i => i.Operand is MethodReference c && c.Name == "launchChaffEffect") != 1)
                throw new InvalidOperationException("Inspected Multi-Stage chaff submunition launch changed");
            // stfld consumes the system and the new Ammunition; pop both.
            store.OpCode = OpCodes.Pop; store.Operand = null;
            method.Body.GetILProcessor().InsertAfter(store, Instruction.Create(OpCodes.Pop));
            scope.Count("chaff-ammo-discard");
        }
        if (type.FullName == MultiStagePayloadApi && method.Name == "Validate") {
            var name = il.SingleOrDefault(i => i.Offset == 0x00df);
            var length = il.SingleOrDefault(i => i.Offset == 0x00e4);
            var last = il.SingleOrDefault(i => i.Offset == 0x010b);
            var check = il.SingleOrDefault(i => i.Offset == 0x0111);
            if (method.Body.CodeSize != 778 || name == null || length == null || last == null || check == null ||
                name.OpCode != OpCodes.Ldstr || !Equals(name.Operand, "launchChaffEffect") ||
                length.OpCode != OpCodes.Ldc_I4_3 || length.Next.OpCode != OpCodes.Newarr ||
                (length.Next.Operand as TypeReference)?.FullName != "System.Type" ||
                !(last.OpCode == OpCodes.Call && last.Operand is MethodReference getType &&
                  getType.FullName == "System.Type System.Type::GetTypeFromHandle(System.RuntimeTypeHandle)") ||
                last.Previous.OpCode != OpCodes.Ldtoken || (last.Previous.Operand as TypeReference)?.FullName != "UnityEngine.GameObject" ||
                last.Next != check.Previous || check.Previous.OpCode != OpCodes.Stelem_Ref ||
                !(check.OpCode == OpCodes.Call && check.Operand is MethodReference require &&
                  require.FullName == "System.Reflection.MethodInfo " + MultiStagePayloadApi + "::RequireVoid(System.Type,System.String,System.Type[])") ||
                il.Count(i => i.OpCode == OpCodes.Ldstr && Equals(i.Operand, "launchChaffEffect")) != 1)
                throw new InvalidOperationException("Inspected Multi-Stage chaff payload validator changed");
            length.OpCode = OpCodes.Ldc_I4_4;
            var writer = method.Body.GetILProcessor();
            foreach (var extra in new[] { Instruction.Create(OpCodes.Dup), Instruction.Create(OpCodes.Ldc_I4_3),
                Instruction.Create(OpCodes.Ldtoken, scope.Module.TypeSystem.Int32), Instruction.Create(OpCodes.Call, (MethodReference)last.Operand),
                Instruction.Create(OpCodes.Stelem_Ref) }) writer.InsertBefore(check, extra);
            scope.Count("chaff-validate-signature");
        }
        return false;
    }

    private static bool MultiStageChaffCall(AdapterScope scope, TypeDefinition type, MethodDefinition method, Instruction instruction, MethodReference call)
    {
        if (call.DeclaringType.FullName != "SeaPower.ChaffCloud" || call.Name != "launchChaffEffect") return false;
        if (type.FullName != MultiStagePayloadApi || method.Name != "LaunchChaff" || instruction.OpCode != OpCodes.Callvirt ||
            !call.HasThis || call.ReturnType.FullName != "System.Void" ||
            !ParameterTypes(call, "SeaPower.WeaponSystemChaff", "UnityEngine.GameObject", "UnityEngine.GameObject"))
            throw new InvalidOperationException("Uninspected Multi-Stage chaff cloud launch in " + type.FullName + "::" + method.Name);
        AppendDefaults(scope.Module, scope.Native, method, instruction, call, "chaff-cartridges");
        scope.Count("chaff-cartridges");
        return true;
    }
}
