// Enhanced Decoy Mod 0.5.4 (EnhancedDecoyMod.dll, 7cd4f160, Workshop
// 3784474738) on 0.9.3-261123 (ea653e49). The image reads the field
// WeaponSystemChaff._ammoInUse at 33 sites and never writes it or takes its
// address. 261123 moved chaff launchers to a list of rounds and made
// _ammoInUse a read-only property: get__ammoInUse() returns round 0's Ammo,
// or null when the launcher has no rounds. Each field read becomes a call to
// that getter: the stack shape is the same, and a null launcher still throws
// NullReferenceException at the same site. On a launcher with several rounds
// the mod sees only round 0's ammunition, as the native getter defines it.
// Its transpilers on AI.ProcessContacts, ObjectBase.LaunchChaff and
// WeaponSystemCIWS.AquireTarget are judged by the author's own validators
// (R6_EnhancedDecoy runs them); if one fails, the mod disables itself.
using System;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    internal const string EnhancedDecoyHash = "7cd4f160dae75147a84bcc671d791db3012278497decffe80431d262d9ad7548";
    internal const string EnhancedDecoyAudit = "chaff-round-ammo=33, locations=2";

    private static ImageAdapter EnhancedDecoyAdapter() => new ImageAdapter {
        Name = "EnhancedDecoy", Hashes = new[] { EnhancedDecoyHash },
        RequireNative = EnhancedDecoyRequireNative,
        RewriteMethod = EnhancedDecoyRewrite,
        ExpectedAudit = EnhancedDecoyAudit,
    };

    private static void EnhancedDecoyRequireNative(ModuleDefinition native)
    {
        CurrentNativeSnapshot(native);
        ChaffRoundAmmoGetter(native);
    }

    // The 261123 read-only _ammoInUse property, asserted exactly: no field and
    // no setter of that name, one parameterless instance getter returning
    // SeaPower.Ammunition, whose body reads _rounds[0].Ammo. Also used by the
    // Multi-Stage Missiles chaff adapter.
    private static MethodDefinition ChaffRoundAmmoGetter(ModuleDefinition native)
    {
        var chaff = native.GetType("SeaPower.WeaponSystemChaff");
        var round = chaff?.NestedTypes.SingleOrDefault(t => t.Name == "Round");
        var getters = chaff?.Methods.Where(m => m.Name == "get__ammoInUse").ToList();
        var body = getters?.Count == 1 && getters[0].HasBody ? getters[0].Body.Instructions : null;
        if (chaff == null || round == null || body == null ||
            chaff.Fields.Any(f => f.Name == "_ammoInUse") ||
            chaff.Methods.Any(m => m.Name == "set__ammoInUse") ||
            chaff.Properties.SingleOrDefault(p => p.Name == "_ammoInUse")?.SetMethod != null ||
            !getters[0].HasThis || getters[0].IsStatic || getters[0].HasParameters ||
            getters[0].ReturnType.FullName != "SeaPower.Ammunition" || getters[0].Body.CodeSize != 34 ||
            body.Count(i => i.OpCode == OpCodes.Ldfld && i.Operand is FieldReference f &&
                f.DeclaringType.FullName == "SeaPower.WeaponSystemChaff" && f.Name == "_rounds") != 2 ||
            body.Count(i => i.OpCode == OpCodes.Ldfld && i.Operand is FieldReference a &&
                a.DeclaringType.FullName == "SeaPower.WeaponSystemChaff/Round" && a.Name == "Ammo" &&
                a.FieldType.FullName == "SeaPower.Ammunition") != 1 ||
            body.Count(i => i.OpCode == OpCodes.Ldnull) != 1)
            throw new InvalidOperationException("Inspected 261123 chaff round ammunition getter changed");
        return getters[0];
    }

    private static bool EnhancedDecoyRewrite(AdapterScope scope, TypeDefinition type, MethodDefinition method)
    {
        MethodReference getter = null;
        foreach (var instruction in method.Body.Instructions) {
            if (!(instruction.Operand is FieldReference field && field.Name == "_ammoInUse" &&
                field.DeclaringType.FullName == "SeaPower.WeaponSystemChaff")) continue;
            if (instruction.OpCode != OpCodes.Ldfld || field.FieldType.FullName != "SeaPower.Ammunition")
                throw new InvalidOperationException("Uninspected Enhanced Decoy chaff ammunition access in " + type.FullName + "::" + method.Name);
            getter ??= scope.Module.ImportReference(ChaffRoundAmmoGetter(scope.Native));
            instruction.OpCode = OpCodes.Callvirt;
            instruction.Operand = getter;
            scope.Count("chaff-round-ammo");
        }
        return false;
    }
}
