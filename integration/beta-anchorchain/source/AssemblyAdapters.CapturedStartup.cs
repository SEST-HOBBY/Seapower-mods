// R9: fixes for the exact author images which failed in the 8 November
// 22:23 Brisbane capture. Original Workshop images and assets are retained.
// R14: both images are unchanged in the 14 November 0.9.2 capture, and
// 0.9.2 keeps the native shapes each fix asserts below.
using System;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    internal const string CurrentTestRangeHash = "f1639294f24ffb7c89723ea8a42a1ab6d35147bee503395f87dad3759a5a981c";
    internal const string CurrentOptimalHash = "61068dd0863501dacf1217250b3f4702f3778d6c6bcad38ab4be46eaa0c7375a";

    private static ImageAdapter TestRangeCurrentAdapter() => new ImageAdapter {
        Name = "TestRangeCurrent", Hashes = new[] { CurrentTestRangeHash },
        RequireNative = CurrentSensorNative,
        RewriteMethod = CurrentSensorRewrite,
        ExpectedAudit = "locations=2, sensor-range-argument=1",
    };

    private static ImageAdapter OptimalTargetCurrentAdapter() => new ImageAdapter {
        Name = "OptimalTargetCurrent", Hashes = new[] { CurrentOptimalHash },
        RequireNative = CurrentLaunchNative,
        RewriteMethod = CurrentLaunchRewrite,
        ExpectedAudit = "aaw-native-fallback=1, launch-layout=1, locations=2",
    };

    private static void CurrentNativeSnapshot(ModuleDefinition native)
    {
        if (Hash(native.FileName) != "3f56861f09e867f315b194c81a7a2450154ccc6bb5afb769b4956dfd4a00503a")
            throw new InvalidOperationException("R14 requires the inspected 0.9.2-261113 game image");
    }

    private static void CurrentSensorNative(ModuleDefinition native)
    {
        CurrentNativeSnapshot(native);
        var sensor = native.GetType("SeaPower.ObjectBase").Methods.Single(m => m.Name == "GetSensorRange");
        var last = sensor.Parameters.Last();
        if (!sensor.HasThis || sensor.ReturnType.FullName != "SeaPower.ObjectBase/EstimatedSensorRangeData" ||
            !ParameterTypes(sensor, "SeaPower.ObjectBase", "SeaPower.Ammunition", "SeaPower.ObjectBase/SensorRangeOptions", "System.Boolean") ||
            last.Name != "rangeOnly" || !last.IsOptional || !last.HasConstant || !Equals(last.Constant, false))
            throw new InvalidOperationException("Inspected current sensor-range contract changed");
    }

    private static bool CurrentSensorRewrite(AdapterScope scope, TypeDefinition type, MethodDefinition method)
    {
        if (type.FullName != "TestRange.ResultApi" || method.Name != "Validate") return false;
        // Extend the reflection signature, not a game call. The existing
        // postfix uses only __instance, __0, __1 and __result, all unchanged.
        var il = method.Body.Instructions;
        var length = il.Single(i => i.Offset == 0x0329);
        var bind = il.Single(i => i.Offset == 0x0356);
        if (length.OpCode != OpCodes.Ldc_I4_3 || length.Next.OpCode != OpCodes.Newarr ||
            bind.OpCode != OpCodes.Call || bind.Operand is not MethodReference call ||
            call.FullName != "System.Void TestRange.ResultApi::Bind(System.Type,System.String,System.String,System.String,System.Type,System.Type[])" ||
            il.Single(i => i.Offset == 0x0310).Operand as string != "GetSensorRange" ||
            bind.Previous.OpCode != OpCodes.Stelem_Ref)
            throw new InvalidOperationException("Inspected current TestRange sensor registration changed");
        length.OpCode = OpCodes.Ldc_I4_4;
        var getType = (MethodReference)il.Single(i => i.Offset == 0x0350).Operand;
        var writer = method.Body.GetILProcessor();
        foreach (var extra in new[] { Instruction.Create(OpCodes.Dup), Instruction.Create(OpCodes.Ldc_I4_3),
            Instruction.Create(OpCodes.Ldtoken, scope.Module.TypeSystem.Boolean), Instruction.Create(OpCodes.Call, getType),
            Instruction.Create(OpCodes.Stelem_Ref) }) writer.InsertBefore(bind, extra);
        scope.Count("sensor-range-argument");
        return false;
    }

    private static void CurrentLaunchNative(ModuleDefinition native)
    {
        CurrentNativeSnapshot(native);
        var launcher = native.GetType("SeaPower.WeaponSystemLauncher");
        var update = launcher.Methods.Single(m => m.Name == "OnUpdate" && !m.HasParameters);
        var il = update.Body.Instructions;
        int Writes(string field) => il.Count(i => i.Operand is FieldReference f && f.Name == field &&
            f.DeclaringType.FullName == "SeaPower.ObjectBase");
        // The author checks and rewrites each individual dictionary access.
        // This native layout adds a fourth timer write on failed launch.
        if (Writes("_sharedLaunchTimers") != 5 || Writes("_sharedLaunchIntervals") != 2)
            throw new InvalidOperationException("Inspected current shared-launch accesses changed");
    }

    private static bool CurrentLaunchRewrite(AdapterScope scope, TypeDefinition type, MethodDefinition method)
    {
        if (type.FullName == "OptimalTargetDistAnchorChain.SharedLaunchGroups" && method.Name == "Transpiler") {
            var count = method.Body.Instructions.Single(i => i.Offset == 0x03bc);
            if (method.Body.CodeSize != 1062 || count.OpCode != OpCodes.Ldc_I4_3 ||
                count.Previous.OpCode != OpCodes.Ldloc_S || count.Previous.Operand is not VariableDefinition v || v.Index != 7 ||
                count.Next.OpCode != OpCodes.Beq_S)
                throw new InvalidOperationException("Inspected current OptimalTarget shared-launch validator changed");
            count.OpCode = OpCodes.Ldc_I4_4;
            scope.Count("launch-layout");
        }
        if (type.FullName == "OptimalTargetDistAnchorChain.AawInterception" && method.Name == "Install") {
            if (!method.IsStatic || method.HasParameters || method.ReturnType.FullName != "System.Void" || method.Body.CodeSize != 150)
                throw new InvalidOperationException("Inspected current AAW feature initializer changed");
            // This optional subfeature rejects the native target-validation
            // control flow. Leave it uninstalled; Ready stays false. Other
            // OptimalTarget features, including launch sharing, remain active.
            method.Body.Instructions.Clear();
            method.Body.ExceptionHandlers.Clear();
            method.Body.Variables.Clear();
            method.Body.Instructions.Add(Instruction.Create(OpCodes.Ret));
            scope.Count("aaw-native-fallback");
            return true;
        }
        return false;
    }
}
