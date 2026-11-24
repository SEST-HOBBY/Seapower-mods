// Z-21 Gun and EOTS Synchronization (Z21GunMoveFire.dll, 6de88b8b, Workshop
// 3774746803) on 0.9.3-261123 (ea653e49). Mod's static constructor looks up
// WeaponSystem._containerBaseObject by reflection. No 0.9 build has that
// field: the container object is WeaponParameters._containerBaseObject, read
// through WeaponSystem._vwp. The lookup returns null (HarmonyX warns), so
// SyncOpticToGun(Helicopter, AlignUnitToTarget) returns at once and the
// EOTS does not follow the gun while the helicopter aligns to fire. The
// lookup now names WeaponParameters (container-field), and the one read
// through it calls a SEST bridge that goes through the system's _vwp
// (container-read). The rest-position and restored-gun paths are unchanged.
using System;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    internal const string Z21GunMoveFireHash = "6de88b8b12d469a7b6d6ab3f638431a0106db0f9cd3f330e15724cfbca35a3ae";
    internal const string Z21GunMoveFireAudit = "container-field=1, container-read=1";
    private const string Z21Mod = "Z21GunMoveFire.Mod";

    private static ImageAdapter Z21GunMoveFireAdapter() => new ImageAdapter {
        Name = "Z21GunMoveFire", Hashes = new[] { Z21GunMoveFireHash },
        RequireNative = Z21GunMoveFireRequireNative,
        RewriteMethod = Z21GunMoveFireRewrite,
        ExpectedAudit = Z21GunMoveFireAudit,
    };

    private static void Z21GunMoveFireRequireNative(ModuleDefinition native)
    {
        CurrentNativeSnapshot(native);
        var system = native.GetType("SeaPower.WeaponSystem");
        var parameters = native.GetType("SeaPower.WeaponParameters");
        var vwp = system?.Fields.SingleOrDefault(f => f.Name == "_vwp");
        var container = parameters?.Fields.SingleOrDefault(f => f.Name == "_containerBaseObject");
        // AccessTools.Field also searches base types: no game type WeaponSystem
        // derives from may hold the old name either.
        bool inherited = false;
        for (var t = system; t != null; t = t.BaseType == null ? null : native.GetType(t.BaseType.FullName))
            if (t.Fields.Any(f => f.Name == "_containerBaseObject")) inherited = true;
        var init = native.GetType("SeaPower.ObjectBaseLoader")?.Methods.Where(m => m.Name == "initWeaponParameters").ToList();
        var il = init?.Count == 1 && init[0].HasBody ? init[0].Body.Instructions : null;
        if (system == null || parameters == null || inherited || parameters.IsValueType || parameters.BaseType?.FullName != "System.Object" ||
            vwp == null || !vwp.IsPublic || vwp.IsStatic || vwp.FieldType.FullName != "SeaPower.WeaponParameters" ||
            container == null || !container.IsPublic || container.IsStatic || container.FieldType.FullName != "UnityEngine.GameObject" ||
            il == null || !init[0].IsStatic || init[0].ReturnType.FullName != "SeaPower.WeaponParameters" ||
            il.Count(i => i.OpCode == OpCodes.Newobj && i.Operand is MethodReference c && c.DeclaringType.FullName == "SeaPower.WeaponParameters") != 1 ||
            !il.Any(i => i.OpCode == OpCodes.Stfld && i.Operand is FieldReference f && f.DeclaringType.FullName == "SeaPower.WeaponParameters" &&
                f.Name == "_containerBaseObject"))
            throw new InvalidOperationException("Inspected 261123 weapon container object contract changed");
    }

    private static bool Z21GunMoveFireRewrite(AdapterScope scope, TypeDefinition type, MethodDefinition method)
    {
        var il = method.Body.Instructions;
        var uses = il.Where(i => i.Operand is FieldReference f && f.Name == "ContainerBaseObject" && f.DeclaringType.FullName == Z21Mod).ToList();
        var names = il.Where(i => i.OpCode == OpCodes.Ldstr && Equals(i.Operand, "_containerBaseObject")).ToList();
        bool cctor = type.FullName == Z21Mod && method.Name == ".cctor";
        bool sync = type.FullName == Z21Mod && method.Name == "SyncOpticToGun" &&
            ParameterTypes(method, "SeaPower.Helicopter", "SeaPower.AlignUnitToTarget");
        if (!cctor && !sync) {
            if (uses.Count != 0 || names.Count != 0)
                throw new InvalidOperationException("Uninspected Z-21 container lookup in " + type.FullName + "::" + method.Name);
            return false;
        }
        if (cctor) {
            var name = names.Count == 1 ? names[0] : null;
            var handle = name?.Previous; var token = handle?.Previous; var lookup = name?.Next; var store = lookup?.Next;
            if (method.Body.CodeSize != 226 || name == null || uses.Count != 1 || store != uses[0] || store.OpCode != OpCodes.Stsfld ||
                !(handle.OpCode == OpCodes.Call && handle.Operand is MethodReference h && h.Name == "GetTypeFromHandle") ||
                token.OpCode != OpCodes.Ldtoken || (token.Operand as TypeReference)?.FullName != "SeaPower.WeaponSystem" ||
                !(lookup.OpCode == OpCodes.Call && lookup.Operand is MethodReference field && field.Name == "Field" &&
                  field.DeclaringType.FullName == "HarmonyLib.AccessTools" && ParameterTypes(field, "System.Type", "System.String")))
                throw new InvalidOperationException("Inspected Z-21 container field lookup changed");
            token.Operand = scope.Module.ImportReference(scope.Native.GetType("SeaPower.WeaponParameters"));
            scope.Count("container-field");
            return false;
        }
        // SyncOpticToGun: a null guard on the lookup, then one read through it.
        var reads = uses.Where(i => i.Next.OpCode == OpCodes.Ldloc_0).ToList();
        var get = reads.Count == 1 ? reads[0].Next.Next : null;
        if (method.Body.CodeSize != 81 || uses.Count != 2 || names.Count != 0 || reads.Count != 1 ||
            method.Body.Variables[0].VariableType.FullName != "SeaPower.WeaponSystem" ||
            uses[0].Next.OpCode != OpCodes.Ldnull ||
            !(get.OpCode == OpCodes.Callvirt && get.Operand is MethodReference value && value.Name == "GetValue" &&
              value.DeclaringType.FullName == "System.Reflection.FieldInfo" && ParameterTypes(value, "System.Object")) ||
            get.Next.OpCode != OpCodes.Isinst || (get.Next.Operand as TypeReference)?.FullName != "UnityEngine.GameObject")
            throw new InvalidOperationException("Inspected Z-21 optic-to-gun container read changed");
        get.OpCode = OpCodes.Call; get.Operand = scope.Bridge(nameof(BetaCompatibilityCalls.WeaponContainerObject));
        scope.Count("container-read");
        return false;
    }
}
