// MissileControlMod 0.1.16 bridges, used only by its hash-pinned private image.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;

namespace AnchorChain;

public static partial class BetaCompatibilityCalls
{
    // Lookups isolated in their own class, so a failed lookup cannot break
    // BetaCompatibilityCalls' other bridges; a null lookup leaves the stream
    // unchanged and the author's own shape check then disables the plugin.
    private static class MissileControlModSteering
    {
        internal const BindingFlags Instance = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly;
        internal static readonly FieldInfo MaxG = Field(typeof(SeaPower.AmmunitionParameters), "_maxTurnG", "System.Single");
        internal static readonly FieldInfo MaxRate = Field(typeof(SeaPower.AmmunitionParameters), "_maxTurnRateDegrees", "System.Single");
        internal static readonly MethodInfo Formula = typeof(BetaCompatibilityCalls).GetMethod(nameof(MissileControlModGLimitedTurnRate));

        static FieldInfo Field(Type type, string name, string fieldType)
        {
            var field = type.GetField(name, Instance);
            return field != null && field.FieldType.FullName == fieldType ? field : null;
        }
    }

    private static bool MissileControlModMethod(object operand, string type, string name, bool isStatic, string returnType, params string[] parameters)
        => operand is MethodInfo method && method.DeclaringType?.FullName == type && method.Name == name && method.IsStatic == isStatic &&
            method.ReturnType.FullName == returnType && method.GetParameters().Select(p => p.ParameterType.FullName).SequenceEqual(parameters);

    private static bool MissileControlModField(object operand, string type, string name, string fieldType)
        => operand is FieldInfo field && field.DeclaringType?.FullName == type && field.Name == name && !field.IsStatic &&
            field.FieldType.FullName == fieldType;

    // MissileControlMod's Hooks.SteeringLimits is PatchSteeringLimits(source, 1, 1, 2):
    // it wraps the one _maxTurnG and the one _maxTurnRateDegrees load of
    // WeaponBase.setCourseTowardsPosition with its EffectiveG/EffectiveRate.
    // Beta 261026 moved both loads, unchanged, into WeaponBase.GLimitedTurnRate:
    //     ldarg.0; ldfld _ap; ldarg.0; call getVelocityInKnots; call GLimitedTurnRate
    // This returns the stream the author's transpiler expects:
    //     ldarg.0; ldfld _ap; ldfld _maxTurnG; ldarg.0; ldfld _ap; ldfld _maxTurnRateDegrees;
    //     ldarg.0; call getVelocityInKnots; call MissileControlModGLimitedTurnRate
    // which computes what native GLimitedTurnRate(_ap, knots) computes. Any
    // other stream (setCourseTowardsPositionLegacy, another beta) passes through
    // unchanged, so the author's own check still fails closed.
    public static IEnumerable<CodeInstruction> MissileControlModSteeringShape(IEnumerable<CodeInstruction> source)
    {
        var list = source.ToList();
        int k = -1;
        for (int i = 0; i < list.Count; i++) {
            if (!MissileControlModMethod(list[i].operand, "SeaPower.WeaponBase", "GLimitedTurnRate", true, "System.Single",
                "SeaPower.AmmunitionParameters", "System.Single")) continue;
            if (k >= 0) return list;
            k = i;
        }
        if (k < 4 || list[k].opcode != OpCodes.Call || MissileControlModSteering.MaxG == null ||
            MissileControlModSteering.MaxRate == null || MissileControlModSteering.Formula == null ||
            list[k - 4].opcode != OpCodes.Ldarg_0 ||
            list[k - 3].opcode != OpCodes.Ldfld || !MissileControlModField(list[k - 3].operand, "SeaPower.WeaponBase", "_ap", "SeaPower.AmmunitionParameters") ||
            list[k - 2].opcode != OpCodes.Ldarg_0 ||
            list[k - 1].opcode != OpCodes.Call || !MissileControlModMethod(list[k - 1].operand, "SeaPower.ObjectBase", "getVelocityInKnots", false, "System.Single"))
            return list;
        for (int i = k - 3; i <= k; i++) if (list[i].labels.Count != 0 || list[i].blocks.Count != 0) return list;
        // A new call instruction: the incoming one carries no labels or blocks
        // (checked above), and the caller's instruction objects stay unchanged.
        list[k] = new CodeInstruction(OpCodes.Call, MissileControlModSteering.Formula);
        list.InsertRange(k - 2, new[] {
            new CodeInstruction(OpCodes.Ldfld, MissileControlModSteering.MaxG),
            new CodeInstruction(OpCodes.Ldarg_0),
            new CodeInstruction(OpCodes.Ldfld, list[k - 3].operand),
            new CodeInstruction(OpCodes.Ldfld, MissileControlModSteering.MaxRate) });
        return list;
    }

    // Mirrors native beta SeaPower.WeaponBase.GLimitedTurnRate(AmmunitionParameters
    // ap, float speedInKnots) operation for operation, with ap._maxTurnG and
    // ap._maxTurnRateDegrees taken as arguments: speed in m/s, the turn radius
    // at the configured turn rate, and the rate scaled down when the lateral
    // load exceeds the G limit.
    public static float MissileControlModGLimitedTurnRate(float maxTurnG, float maxTurnRateDegrees, float speedInKnots)
    {
        float speed = 0.5144439935684204f * speedInKnots;
        float radius = speed * (360f / maxTurnRateDegrees) / 6.2831855f;
        float lateralG = MathF.Pow(speed, 2f) / (radius * 9.8f);
        if (lateralG > maxTurnG) maxTurnRateDegrees *= maxTurnG / lateralG;
        return maxTurnRateDegrees;
    }
}
