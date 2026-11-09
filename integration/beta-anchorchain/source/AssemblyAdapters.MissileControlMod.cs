using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    // R6 (7 Nov 2026): Euromod's MissileControlMod 0.1.16 (Workshop 3784474738,
    // MVID 703df634-a543-4d42-b263-a60cea7c9675) as captured on 3 Nov 2026.
    // On the beta its own Compatibility.ValidateGame disables it twice over:
    // Hooks.SteeringLimits finds 0/0/2 instead of 1/1/2 AmmunitionParameters
    // loads in WeaponBase.setCourseTowardsPosition, because Build 261026 moved
    // the _maxTurnG/_maxTurnRateDegrees block verbatim into the new static
    // WeaponBase.GLimitedTurnRate; and ValidateReferences cannot resolve
    // FileManager.GetFile(string,string), used only by the uncalled
    // EffectAudio.EnableDiagnostics. The adapter re-exposes the two loads in
    // the stream the author's transpiler sees (MissileControlModSteeringShape),
    // retargets the dead GetFile call to the existing GetLegacyFile bridge, and
    // leaves the author's validators, counts and error paths in charge.
    internal const string MissileControlModHash = "2d6a68dfe9f0527e451f9c073faa017017a4e75c69e82c27fc70e45f1329c581";

    private static ImageAdapter MissileControlModAdapter() => new ImageAdapter {
        Name = "MissileControlMod",
        Hashes = new[] { MissileControlModHash },
        RequireNative = MissileControlModRequireNative,
        RewriteMethod = MissileControlModRewriteMethod,
        RewriteCall = MissileControlModRewriteCall,
        // steering-shape: Hooks.SteeringLimits; file: EffectAudio.EnableDiagnostics;
        // locations: the shared rule on ACModActivation.Guard.Allow IL_009a and IL_0119.
        ExpectedAudit = "file=1, locations=2, steering-shape=1",
    };

    private const string MissileControlModSequence = "System.Collections.Generic.IEnumerable`1<HarmonyLib.CodeInstruction>";

    // Native beta WeaponBase.GLimitedTurnRate (rid 45582, 68 bytes), the body
    // MissileControlModGLimitedTurnRate reproduces with the two field loads
    // taken as arguments. Float constants are compared by their bits.
    private static readonly string[] MissileControlModNativeGLimit = {
        "ldarg.0", "ldfld SeaPower.AmmunitionParameters::_maxTurnG:System.Single", "stloc.0",
        "ldarg.0", "ldfld SeaPower.AmmunitionParameters::_maxTurnRateDegrees:System.Single", "stloc.1",
        "ldc.r4 0x3F03B29A", "ldarg.1", "mul", "dup", "ldc.r4 0x43B40000", "ldloc.1", "div", "mul",
        "ldc.r4 0x40C90FDB", "div", "stloc.2", "ldc.r4 0x40000000",
        "call static System.MathF::Pow(System.Single,System.Single):System.Single",
        "ldloc.2", "ldc.r4 0x411CCCCD", "mul", "div", "stloc.3", "ldloc.3", "ldloc.0", "ble.un.s ->33",
        "ldloc.1", "ldloc.0", "ldloc.3", "div", "mul", "stloc.1", "ldloc.1", "ret" };

    // The prologue of beta WeaponBase.setCourseTowardsPosition (rid 45583,
    // IL_0000-IL_0011) that MissileControlModSteeringShape rewrites in Harmony's
    // stream.
    private static readonly string[] MissileControlModNativePrologue = {
        "ldarg.0", "ldfld SeaPower.WeaponBase::_ap:SeaPower.AmmunitionParameters", "ldarg.0",
        "call instance SeaPower.ObjectBase::getVelocityInKnots():System.Single",
        "call static SeaPower.WeaponBase::GLimitedTurnRate(SeaPower.AmmunitionParameters,System.Single):System.Single",
        "stloc.0" };

    // The author's Hooks.SteeringLimits (rid 130, 26 bytes):
    // PatchSteeringLimits(source, 1, Compatibility.LegacyCourse == null ? 2 : 1, 2).
    private static readonly string[] MissileControlModSteeringLimits = {
        "ldarg.0", "ldc.i4.1", "ldsfld MissileControlMod.Compatibility::LegacyCourse:System.Reflection.MethodInfo", "ldnull",
        "call static System.Reflection.MethodInfo::op_Equality(System.Reflection.MethodInfo,System.Reflection.MethodInfo):System.Boolean",
        "brtrue.s ->8", "ldc.i4.1", "br.s ->9", "ldc.i4.2", "ldc.i4.2",
        "call static MissileControlMod.Hooks::PatchSteeringLimits(" + MissileControlModSequence + ",System.Int32,System.Int32,System.Int32):" + MissileControlModSequence,
        "ret" };

    private static string MissileControlModDescribe(Instruction instruction, IList<Instruction> body)
    {
        string name = instruction.OpCode.Name;
        switch (instruction.Operand) {
            case FieldReference field:
                return name + " " + field.DeclaringType.FullName + "::" + field.Name + ":" + field.FieldType.FullName;
            case MethodReference method:
                return name + (method.HasThis ? " instance " : " static ") + method.DeclaringType.FullName + "::" + method.Name + "(" +
                    String.Join(",", method.Parameters.Select(p => p.ParameterType.FullName)) + "):" + method.ReturnType.FullName;
            case float value:
                return name + " 0x" + BitConverter.ToInt32(BitConverter.GetBytes(value), 0).ToString("X8", CultureInfo.InvariantCulture);
            case Instruction target:
                return name + " ->" + body.IndexOf(target);
            case null:
                return name;
            default:
                return name + " " + Convert.ToString(instruction.Operand, CultureInfo.InvariantCulture);
        }
    }

    private static string[] MissileControlModBody(MethodDefinition method)
        => method.Body.Instructions.Select(i => MissileControlModDescribe(i, method.Body.Instructions)).ToArray();

    private static bool MissileControlModSignature(MethodReference method, bool isStatic, string returnType, params string[] parameters)
        => method.HasThis != isStatic && method.ReturnType.FullName == returnType && ParameterTypes(method, parameters);

    // The native shapes the rewrites and bridges rely on, asserted on the pinned
    // beta image before any rewrite. A different beta fails closed.
    private static void MissileControlModRequireNative(ModuleDefinition native)
    {
        var weapon = native.GetType("SeaPower.WeaponBase");
        var ammunition = native.GetType("SeaPower.AmmunitionParameters");
        var objectBase = native.GetType("SeaPower.ObjectBase");
        if (weapon == null || ammunition == null || objectBase == null || ammunition.IsValueType)
            throw new InvalidOperationException("Inspected beta WeaponBase/AmmunitionParameters/ObjectBase changed");
        bool InstanceField(TypeDefinition type, string name, string fieldType)
        {
            var matches = type.Fields.Where(f => f.Name == name).ToList();
            return matches.Count == 1 && !matches[0].IsStatic && matches[0].FieldType.FullName == fieldType;
        }
        if (!InstanceField(weapon, "_ap", "SeaPower.AmmunitionParameters") || !InstanceField(ammunition, "_maxTurnG", "System.Single") ||
            !InstanceField(ammunition, "_maxTurnRateDegrees", "System.Single") || !InstanceField(ammunition, "_terminalVerticalTurnRate", "System.Single"))
            throw new InvalidOperationException("Inspected beta steering-limit fields changed");
        var knots = objectBase.Methods.Where(m => m.Name == "getVelocityInKnots").ToList();
        if (knots.Count != 1 || !MissileControlModSignature(knots[0], false, "System.Single"))
            throw new InvalidOperationException("Inspected beta ObjectBase.getVelocityInKnots changed");

        var limits = weapon.Methods.Where(m => m.Name == "GLimitedTurnRate").ToList();
        if (limits.Count != 1 || !limits[0].HasBody || !MissileControlModSignature(limits[0], true, "System.Single", "SeaPower.AmmunitionParameters", "System.Single") ||
            limits[0].Parameters[0].Name != "ap" || limits[0].Parameters[1].Name != "speedInKnots" || limits[0].Body.HasExceptionHandlers ||
            limits[0].Body.Variables.Count != 4 || limits[0].Body.Variables.Any(v => v.VariableType.FullName != "System.Single") ||
            !MissileControlModBody(limits[0]).SequenceEqual(MissileControlModNativeGLimit))
            throw new InvalidOperationException("Inspected beta WeaponBase.GLimitedTurnRate changed");

        var courses = weapon.Methods.Where(m => m.Name == "setCourseTowardsPosition").ToList();
        if (courses.Count != 1 || !courses[0].HasBody ||
            !MissileControlModSignature(courses[0], false, "System.Single", "UnityEngine.Vector3", "System.Boolean", "System.Boolean"))
            throw new InvalidOperationException("Inspected beta WeaponBase.setCourseTowardsPosition signature changed");
        var course = courses[0].Body.Instructions;
        var described = MissileControlModBody(courses[0]);
        int Loads(string field) => described.Count(d => d == "ldfld SeaPower.AmmunitionParameters::" + field + ":System.Single");
        // No branch or handler may enter the rewritten prologue: the bridge
        // inserts its loads before IL_0006.
        bool InPrologue(Instruction target) { int at = course.IndexOf(target); return at >= 1 && at <= 5; }
        bool prologueTargeted = course.Any(i => (i.Operand is Instruction t && InPrologue(t)) || (i.Operand is Instruction[] ts && ts.Any(InPrologue))) ||
            courses[0].Body.ExceptionHandlers.Any(h => InPrologue(h.TryStart) || InPrologue(h.HandlerStart) || (h.FilterStart != null && InPrologue(h.FilterStart)));
        if (!described.Take(MissileControlModNativePrologue.Length).SequenceEqual(MissileControlModNativePrologue) || prologueTargeted ||
            described.Count(d => d.Contains("::GLimitedTurnRate(")) != 1 || Loads("_maxTurnG") != 0 || Loads("_maxTurnRateDegrees") != 0 ||
            Loads("_terminalVerticalTurnRate") != 2 || described.Count(d => d.Contains("SeaPower.WeaponBase::setCourseTowardsPositionLegacy(")) != 1)
            throw new InvalidOperationException("Inspected beta WeaponBase.setCourseTowardsPosition shape changed");
        // The author binds Compatibility.LegacyCourse to this method; non-null,
        // it expects 1/1/2 from SteeringLimits and patches it with LegacySteeringLimits.
        if (weapon.Methods.Count(m => m.Name == "setCourseTowardsPositionLegacy" &&
            MissileControlModSignature(m, false, "System.Single", "UnityEngine.Vector3", "System.Boolean", "System.Boolean", "System.Single")) != 1)
            throw new InvalidOperationException("Inspected beta WeaponBase.setCourseTowardsPositionLegacy changed");

        // GetLegacyFile calls the native GetFile(string, LayerKind) with LayerKind.All.
        var files = native.GetType("SeaPower.FileManager")?.Methods.Where(m => m.Name == "GetFile").ToList();
        var layer = native.GetType("SeaPower.LayerKind");
        if (files == null || files.Count != 1 || !MissileControlModSignature(files[0], false, "System.String", "System.String", "SeaPower.LayerKind") ||
            layer == null || !layer.IsEnum || !layer.Fields.Any(f => f.Name == "All" && f.IsStatic && f.HasConstant))
            throw new InvalidOperationException("Inspected beta FileManager.GetFile changed");
    }

    private static bool MissileControlModRewriteMethod(AdapterScope scope, TypeDefinition type, MethodDefinition method)
    {
        if (type.FullName != "MissileControlMod.Hooks" || method.Name != "SteeringLimits") return false;
        if (!MissileControlModSignature(method, true, MissileControlModSequence, MissileControlModSequence) ||
            method.Parameters[0].Name != "source" || method.Body.HasExceptionHandlers || method.Body.HasVariables ||
            !MissileControlModBody(method).SequenceEqual(MissileControlModSteeringLimits))
            throw new InvalidOperationException("Inspected MissileControlMod steering-limit transpiler changed");
        // ldarg.0 (source) -> MissileControlModSteeringShape(source) -> the
        // author's unchanged PatchSteeringLimits. The shared loop then widens
        // the two short branches.
        var first = method.Body.Instructions[0];
        method.Body.GetILProcessor().InsertAfter(first, Instruction.Create(OpCodes.Call, scope.Bridge(nameof(BetaCompatibilityCalls.MissileControlModSteeringShape))));
        scope.Count("steering-shape");
        return false;
    }

    private static bool MissileControlModRewriteCall(AdapterScope scope, TypeDefinition type, MethodDefinition method,
        Instruction instruction, MethodReference call)
    {
        string owner = call.DeclaringType.FullName;
        // The shared rule rewrites these two; assert they are the inspected ones.
        if (owner == "System.Reflection.Assembly" && call.Name == "get_Location") {
            if (type.FullName != "ACModActivation.Guard" || method.Name != "Allow" || instruction.OpCode != OpCodes.Callvirt ||
                !MissileControlModSignature(call, false, "System.String"))
                throw new InvalidOperationException("Inspected MissileControlMod assembly location call changed: " + type.FullName + "." + method.Name);
            return false;
        }
        if (owner != "SeaPower.FileManager" || call.Name != "GetFile") return false;
        var body = method.Body.Instructions;
        int index = body.IndexOf(instruction);
        if (type.FullName != "SeaPowerModSupport.EffectAudio" || method.Name != "EnableDiagnostics" ||
            !MissileControlModSignature(method, false, "System.Void", "System.String", "System.Action`1<System.String>", "System.String") ||
            instruction.OpCode != OpCodes.Callvirt || !MissileControlModSignature(call, false, "System.String", "System.String", "System.String") ||
            index < 3 || index + 1 >= body.Count ||
            MissileControlModDescribe(body[index - 3], body) != "call static SeaPower.Singleton`1<SeaPower.FileManager>::get_Instance():!0" ||
            body[index - 2].OpCode != OpCodes.Ldarg_3 || body[index - 1].OpCode != OpCodes.Ldnull || body[index + 1].OpCode != OpCodes.Stloc_0)
            throw new InvalidOperationException("Inspected MissileControlMod FileManager.GetFile call changed: " + type.FullName + "." + method.Name);
        // Instance callvirt manager.GetFile(path, null) -> static
        // GetLegacyFile(manager, path, null) = manager.GetFile(path, LayerKind.All).
        instruction.OpCode = OpCodes.Call;
        instruction.Operand = scope.Bridge(nameof(BetaCompatibilityCalls.GetLegacyFile));
        scope.Count("file");
        return true;
    }
}
