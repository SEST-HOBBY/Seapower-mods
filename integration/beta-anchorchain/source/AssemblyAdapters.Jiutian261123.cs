// Jiutian Reference Units 1.4.7 (230f38f6, Chinese UAV collection 3836566168),
// a companion that UAVWorkshopEntry loads by itself. JiutianFH901Flight.Register
// looks up AmmunitionParameters.EffectiveMaxLaunchRange by reflection with the
// parameter list (ObjectBase). Build 261123 adds an optional run depth (float,
// default -1), so that lookup finds nothing, Harmony.Patch(null) throws, and
// Register, which has no try/catch, stops Awake before the FH-901 range,
// mission, launch, altitude, camera, propeller and ASW-door modules register.
// This adapter widens the lookup's Type[] to (ObjectBase, float). The author's
// postfix AfterEffectiveRange(__instance, __0, ref __result) binds by index,
// so it fits the 261123 signature unchanged. SEST's own Cecil code; the image
// reads no Assembly.Location, so its private cache copy is safe.
using System;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    internal const string Jiutian147Hash = "230f38f674fb4ba54c0c4ca265c8723fb1818af2c108322b069fe179f70fc5f8";

    private static ImageAdapter Jiutian261123Adapter() => new ImageAdapter {
        Name = "Jiutian261123", Hashes = new[] { Jiutian147Hash },
        RequireNative = Jiutian261123RequireNative,
        RewriteMethod = Jiutian261123Rewrite,
        ExpectedAudit = "launch-range-lookup=1",
    };

    private static bool Jiutian261123Rewrite(AdapterScope scope, TypeDefinition type, MethodDefinition method)
    {
        if (type.FullName != "JiutianFH901Flight" || method.Name != "Register") return false;
        if (!method.IsStatic || !ParameterTypes(method, "BepInEx.Logging.ManualLogSource"))
            throw new InvalidOperationException("Inspected Jiutian launch-range lookup changed");
        var il = method.Body.Instructions;
        var names = il.Where(i => i.OpCode == OpCodes.Ldstr && Equals(i.Operand, "EffectiveMaxLaunchRange")).ToList();
        if (names.Count != 1) throw new InvalidOperationException("Inspected Jiutian launch-range lookup changed");
        int at = il.IndexOf(names[0]);
        bool Is(int index, OpCode code) => index >= 0 && index < il.Count && il[index].OpCode == code;
        bool Token(int index, string name) => Is(index, OpCodes.Ldtoken) && (il[index].Operand as TypeReference)?.FullName == name;
        bool TypeOf(int index) => Is(index, OpCodes.Call) && il[index].Operand is MethodReference m &&
            m.Name == "GetTypeFromHandle" && m.DeclaringType.FullName == "System.Type";
        var local = Is(at + 3, OpCodes.Stloc_S) ? il[at + 3].Operand as VariableDefinition : null;
        bool Local(int index, OpCode code) => Is(index, code) && il[index].Operand == local;
        bool lookup = Is(at + 11, OpCodes.Call) && il[at + 11].Operand is MethodReference accessor &&
            accessor.Name == "Method" && accessor.DeclaringType.FullName == "HarmonyLib.AccessTools" &&
            ParameterTypes(accessor, "System.Type", "System.String", "System.Type[]", "System.Type[]");
        if (!Token(at - 2, "SeaPower.AmmunitionParameters") || !TypeOf(at - 1) ||
            !Is(at + 1, OpCodes.Ldc_I4_1) || !Is(at + 2, OpCodes.Newarr) || (il[at + 2].Operand as TypeReference)?.FullName != "System.Type" ||
            local == null || local.Index != 6 || local.VariableType.FullName != "System.Type[]" ||
            !Local(at + 3, OpCodes.Stloc_S) || !Local(at + 4, OpCodes.Ldloc_S) || !Is(at + 5, OpCodes.Ldc_I4_0) ||
            !Token(at + 6, "SeaPower.ObjectBase") || !TypeOf(at + 7) || !Is(at + 8, OpCodes.Stelem_Ref) ||
            !Local(at + 9, OpCodes.Ldloc_S) || !Is(at + 10, OpCodes.Ldnull) || !lookup)
            throw new InvalidOperationException("Inspected Jiutian launch-range lookup changed");
        // new Type[] { typeof(ObjectBase) } -> new Type[] { typeof(ObjectBase), typeof(float) }
        il[at + 1].OpCode = OpCodes.Ldc_I4_2;
        var p = method.Body.GetILProcessor();
        var previous = il[at + 8];
        foreach (var added in new[] {
            p.Create(OpCodes.Ldloc_S, local), p.Create(OpCodes.Ldc_I4_1),
            p.Create(OpCodes.Ldtoken, scope.Module.TypeSystem.Single),
            p.Create(OpCodes.Call, (MethodReference)il[at + 7].Operand), p.Create(OpCodes.Stelem_Ref) }) {
            p.InsertAfter(previous, added); previous = added;
        }
        scope.Count("launch-range-lookup");
        return false;
    }

    private static void Jiutian261123RequireNative(ModuleDefinition native)
    {
        CurrentNativeSnapshot(native);
        RequireLaunchRangeWithRunDepth(native);
    }

    // 261123: exactly one EffectiveMaxLaunchRange, instance, float32
    // (ObjectBase launcher, [opt] float32 runDepthFeet = -1).
    private static void RequireLaunchRangeWithRunDepth(ModuleDefinition native)
    {
        var ranges = native.GetType("SeaPower.AmmunitionParameters").Methods.Where(m => m.Name == "EffectiveMaxLaunchRange").ToList();
        if (ranges.Count != 1 || !ranges[0].HasThis || !ranges[0].IsPublic || ranges[0].ReturnType.FullName != "System.Single" ||
            !ParameterTypes(ranges[0], "SeaPower.ObjectBase", "System.Single") || ranges[0].Parameters[0].IsOptional ||
            !ranges[0].Parameters[1].IsOptional || !ranges[0].Parameters[1].HasConstant || !Equals(ranges[0].Parameters[1].Constant, -1f))
            throw new InvalidOperationException("Inspected 261123 EffectiveMaxLaunchRange(ObjectBase, [opt] float = -1) changed");
    }
}
