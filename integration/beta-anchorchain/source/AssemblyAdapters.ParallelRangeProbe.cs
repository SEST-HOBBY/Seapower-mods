using System;
using System.Collections.Generic;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    // R6 (7 Nov 2026): ParallelRangeProbe 0.12.0 ("Datalink Reuse and Contact
    // Jobs Trial", Euromod Anchor Chain Expansion Pack, Workshop 3784474738)
    // as captured on 3 Nov 2026. Its WorkerExpansion module stops itself on
    // the beta with "[WorkerExpansion 0.12.0] FALLBACK: Method
    // 'SeaPower.SensorSystemRadar.GetRangeInternal' not found." because
    // AuxAdapter looks the radar range up by the stable two-parameter list,
    // and behind that its sensor-kernel copier rejects the beta's new
    // `ldsfld RadarCalculator::FourPiCubed` in BaseMaxDetectionRangeMeter.
    // Two rewrites restore it; the plugin's own audits stay active.
    // RangeReuse and Prediction (TrajectoryPreview) are left to fail closed
    // through the author's own guards: their struct-encoded signatures are
    // not re-encoded, and Prediction's stable-algorithm kernel cannot match
    // the beta's Burst MissileSimulator.
    internal const string ParallelRangeProbeHash = "2d04ed4ba00f8084ba2e653f1b271d91a722997b9e1b1bf823a3f411fffa9481";
    private const string ParallelRangeProbeAux = "WorkerExpansion.AuxAdapter";
    private const string ParallelRangeProbeKernel = "WorkerExpansion.NativeSensorKernel";
    private const string ParallelRangeProbeInstructions = "System.Collections.Generic.List`1<WorkerExpansion.NativeSensorKernel/Instruction>";

    private static ImageAdapter ParallelRangeProbeAdapter() => new ImageAdapter {
        Name = "ParallelRangeProbe",
        Hashes = new[] { ParallelRangeProbeHash },
        RequireNative = ParallelRangeProbeRequireNative,
        RewriteMethod = ParallelRangeProbeRewriteMethod,
        // ACModActivation.Guard.Allow reads Assembly.Location twice; the
        // shared rule maps both to the Workshop path.
        ExpectedAudit = "locations=2, radar-range-bool=1, sensor-constant-fold=1",
    };

    // The beta shapes both rewrites and the fold bridge rely on.
    private static void ParallelRangeProbeRequireNative(ModuleDefinition native)
    {
        var radar = native.GetType("SeaPower.SensorSystemRadar")
            ?? throw new InvalidOperationException("Inspected beta SensorSystemRadar changed");
        var ranges = radar.Methods.Where(m => m.Name == "GetRangeInternal").ToList();
        var range = ranges.Count == 1 ? ranges[0] : null;
        if (range == null || !range.HasThis || range.IsStatic || range.Parameters.Count != 3 ||
            !ParameterTypes(range, "SeaPower.ObjectBase", "SeaPower.ObjectBase/SensorRangeOptions", "System.Boolean") ||
            range.Parameters[0].Name != "targetObject" || range.Parameters[1].Name != "options" || range.Parameters[2].Name != "boundOnly" ||
            range.ReturnType.FullName != "SeaPower.SensorSystem/SensorDistanceData")
            throw new InvalidOperationException("Inspected beta SensorSystemRadar.GetRangeInternal changed");
        // AuxAdapter resolves the return type as "SeaPower.SensorSystem+SensorDistanceData"
        // and the options as ObjectBase's nested SensorRangeOptions.
        if (native.GetType("SeaPower.SensorSystem/SensorDistanceData") == null ||
            native.GetType("SeaPower.ObjectBase").NestedTypes.Count(t => t.Name == "SensorRangeOptions") != 1)
            throw new InvalidOperationException("Inspected beta radar range types changed");

        var calculator = native.GetType("SeaPower.RadarCalculator")
            ?? throw new InvalidOperationException("Inspected beta RadarCalculator changed");
        var four = calculator.Fields.SingleOrDefault(f => f.Name == "FourPiCubed");
        if (four == null || !four.IsStatic || !four.IsInitOnly || four.FieldType.FullName != "System.Single")
            throw new InvalidOperationException("Inspected beta RadarCalculator.FourPiCubed changed");
        // .cctor: FourPiCubed = Mathf.Pow(12.566371f, 3f); nothing else writes it.
        var cctor = calculator.Methods.SingleOrDefault(m => m.IsConstructor && m.IsStatic);
        if (cctor == null || !ParallelRangeProbeSequence(cctor.Body.Instructions, 0,
                (OpCodes.Ldc_R4, o => o is float f && f == 12.566371f), (OpCodes.Ldc_R4, o => o is float f && f == 3f),
                (OpCodes.Call, o => ParallelRangeProbeCall(o, "UnityEngine.Mathf", "Pow", false, "System.Single", "System.Single", "System.Single")),
                (OpCodes.Stsfld, o => ParallelRangeProbeField(o, "SeaPower.RadarCalculator", "FourPiCubed", "System.Single")),
                (OpCodes.Ret, o => o == null)) || cctor.Body.Instructions.Count != 5 ||
            calculator.Methods.Any(m => m != cctor && m.HasBody && m.Body.Instructions.Any(i =>
                (i.OpCode == OpCodes.Stsfld || i.OpCode == OpCodes.Ldsflda) && i.Operand is FieldReference f && f.Name == "FourPiCubed")))
            throw new InvalidOperationException("Inspected beta RadarCalculator.FourPiCubed initialiser changed");

        // BaseMaxDetectionRangeMeter, rid 38777, 62 bytes, exactly as inspected.
        var detections = calculator.Methods.Where(m => m.Name == "BaseMaxDetectionRangeMeter").ToList();
        var detection = detections.Count == 1 ? detections[0] : null;
        if (detection == null || !detection.IsStatic || detection.ReturnType.FullName != "System.Single" ||
            !ParameterTypes(detection, "System.Single", "System.Single", "System.Single", "System.Single") ||
            detection.Body.Variables.Count != 0 || detection.Body.ExceptionHandlers.Count != 0 ||
            detection.Body.Instructions.Count != 26 || !ParallelRangeProbeSequence(detection.Body.Instructions, 0,
                (OpCodes.Ldarg_0, null), (OpCodes.Ldc_R4, o => o is float f && f == 1000f), (OpCodes.Mul, null),
                (OpCodes.Ldarg_1, null), (OpCodes.Ldarg_1, null), (OpCodes.Mul, null), (OpCodes.Mul, null),
                (OpCodes.Ldarg_2, null), (OpCodes.Ldarg_2, null), (OpCodes.Mul, null), (OpCodes.Mul, null),
                (OpCodes.Ldarg_3, null), (OpCodes.Mul, null), (OpCodes.Conv_R8, null),
                (OpCodes.Call, o => ParallelRangeProbeCall(o, "SeaPower.Globals", "get_RcsValues", false, "SeaPower.RCSValues")),
                (OpCodes.Ldfld, o => ParallelRangeProbeField(o, "SeaPower.RCSValues", "_minDetectableReturnPowerRadar", "System.Double")),
                (OpCodes.Ldc_R8, o => o is double d && d == 1000.0), (OpCodes.Mul, null),
                (OpCodes.Ldsfld, o => ParallelRangeProbeField(o, "SeaPower.RadarCalculator", "FourPiCubed", "System.Single")),
                (OpCodes.Conv_R8, null), (OpCodes.Mul, null), (OpCodes.Div, null),
                (OpCodes.Ldc_R8, o => o is double d && d == 0.25),
                (OpCodes.Call, o => ParallelRangeProbeCall(o, "System.Math", "Pow", false, "System.Double", "System.Double", "System.Double")),
                (OpCodes.Conv_R4, null), (OpCodes.Ret, null)))
            throw new InvalidOperationException("Inspected beta RadarCalculator.BaseMaxDetectionRangeMeter changed");

        // The horizon kernel the plugin also copies: no static field reads.
        var horizons = calculator.Methods.Where(m => m.Name == "getRadarHorizon").ToList();
        if (horizons.Count != 1 || !horizons[0].IsStatic || horizons[0].ReturnType.FullName != "System.Single" ||
            !ParameterTypes(horizons[0], "System.Single", "System.Single", "System.Boolean", "System.Single") ||
            horizons[0].Body.Instructions.Any(i => i.Operand is FieldReference))
            throw new InvalidOperationException("Inspected beta RadarCalculator.getRadarHorizon changed");
    }

    private static bool ParallelRangeProbeRewriteMethod(AdapterScope scope, TypeDefinition type, MethodDefinition method)
    {
        if (type.FullName == ParallelRangeProbeAux && method.IsConstructor && !method.IsStatic)
            ParallelRangeProbeRadarLookup(scope, method);
        else if (type.FullName == ParallelRangeProbeKernel && method.Name == "Read")
            ParallelRangeProbeFoldRead(scope, method);
        return false;
    }

    // Rewrite 1, 'radar-range-bool'. AuxAdapter::.ctor(Assembly) IL_0168-IL_019b:
    //   RadarRange = Require(radar, "GetRangeInternal", SensorDistanceData, false,
    //                        new Type[2] { ObjectBase, ObjectBase.SensorRangeOptions });
    // becomes new Type[3] { ..., typeof(bool) }, which binds beta's only overload
    // GetRangeInternal(ObjectBase targetObject, SensorRangeOptions options, bool boundOnly).
    // WarmRadar binds positionally (__instance, __0) and stays as written.
    private static void ParallelRangeProbeRadarLookup(AdapterScope scope, MethodDefinition method)
    {
        if (!ParameterTypes(method, "System.Reflection.Assembly") || method.Body.ExceptionHandlers.Count != 0)
            throw new InvalidOperationException("Inspected ParallelRangeProbe AuxAdapter constructor changed");
        var il = method.Body.Instructions;
        var names = il.Where(i => i.OpCode == OpCodes.Ldstr && Equals(i.Operand, "GetRangeInternal")).ToList();
        if (names.Count != 1) throw new InvalidOperationException("Inspected ParallelRangeProbe radar lookup changed");
        int start = il.IndexOf(names[0]) - 2;
        Func<object, bool> require = o => o is MethodReference m && m.DeclaringType.FullName == ParallelRangeProbeAux && m.Name == "Require" &&
            !m.HasThis && m.ReturnType.FullName == "System.Reflection.MethodInfo" &&
            ParameterTypes(m, "System.Type", "System.String", "System.Type", "System.Boolean", "System.Type[]");
        if (start < 0 || !ParallelRangeProbeSequence(il, start,
                (OpCodes.Ldarg_0, null), (OpCodes.Ldloc_2, null), (OpCodes.Ldstr, o => Equals(o, "GetRangeInternal")),
                (OpCodes.Ldarg_1, null), (OpCodes.Ldstr, o => Equals(o, "SeaPower.SensorSystem+SensorDistanceData")),
                (OpCodes.Ldc_I4_1, null),
                (OpCodes.Callvirt, o => ParallelRangeProbeCall(o, "System.Reflection.Assembly", "GetType", true, "System.Type", "System.String", "System.Boolean")),
                (OpCodes.Ldc_I4_0, null), (OpCodes.Ldc_I4_2, null), (OpCodes.Newarr, o => o is TypeReference t && t.FullName == "System.Type"),
                (OpCodes.Dup, null), (OpCodes.Ldc_I4_0, null), (OpCodes.Ldloc_1, null), (OpCodes.Stelem_Ref, null),
                (OpCodes.Dup, null), (OpCodes.Ldc_I4_1, null), (OpCodes.Ldloc_1, null), (OpCodes.Ldstr, o => Equals(o, "SensorRangeOptions")),
                (OpCodes.Ldc_I4_S, o => o is sbyte b && b == 60),
                (OpCodes.Callvirt, o => ParallelRangeProbeCall(o, "System.Type", "GetNestedType", true, "System.Type", "System.String", "System.Reflection.BindingFlags")),
                (OpCodes.Stelem_Ref, null), (OpCodes.Call, require),
                (OpCodes.Stfld, o => o is FieldReference f && f.DeclaringType.FullName == ParallelRangeProbeAux && f.Name == "RadarRange" &&
                    f.FieldType.FullName == "System.Reflection.MethodInfo")))
            throw new InvalidOperationException("Inspected ParallelRangeProbe radar lookup changed");
        // Straight-line code: nothing may branch into the window past its start.
        var window = new HashSet<Instruction>(il.Skip(start + 1).Take(22));
        if (il.Any(i => (i.Operand is Instruction target && window.Contains(target)) ||
                (i.Operand is Instruction[] targets && targets.Any(window.Contains))))
            throw new InvalidOperationException("Inspected ParallelRangeProbe radar lookup changed");
        // The author's own Type::GetTypeFromHandle reference, as used for every
        // other element of these Type[] arguments.
        var handle = il.Take(start).Select(i => i.Operand).OfType<MethodReference>().FirstOrDefault(m =>
            ParallelRangeProbeCall(m, "System.Type", "GetTypeFromHandle", false, "System.Type", "System.RuntimeTypeHandle"))
            ?? throw new InvalidOperationException("Inspected ParallelRangeProbe type-handle call changed");
        il[start + 8].OpCode = OpCodes.Ldc_I4_3; il[start + 8].Operand = null;
        var processor = method.Body.GetILProcessor(); var call = il[start + 21];
        foreach (var added in new[] { Instruction.Create(OpCodes.Dup), Instruction.Create(OpCodes.Ldc_I4_2),
                Instruction.Create(OpCodes.Ldtoken, scope.Module.TypeSystem.Boolean), Instruction.Create(OpCodes.Call, handle),
                Instruction.Create(OpCodes.Stelem_Ref) })
            processor.InsertBefore(call, added);
        scope.Count("radar-range-bool");
    }

    // Rewrite 2, 'sensor-constant-fold'. NativeSensorKernel::Read(MethodInfo)
    // ends `ldloc.1; ret` (IL_0203/IL_0204) with nothing branching to the ret.
    // The ret becomes `dup; ldarg.0; call ParallelRangeProbeFoldDetectionConstant; ret`,
    // so Copy sees beta's FourPiCubed read as the identical ldc.r4 constant and
    // its arithmetic gate passes; every other method's IL is returned untouched.
    private static void ParallelRangeProbeFoldRead(AdapterScope scope, MethodDefinition method)
    {
        var il = method.Body.Instructions;
        var exit = il.Count > 1 ? il[il.Count - 1] : null;
        if (!method.IsStatic || !ParameterTypes(method, "System.Reflection.MethodInfo") ||
            method.ReturnType.FullName != ParallelRangeProbeInstructions || method.Body.ExceptionHandlers.Count != 0 ||
            method.Body.Variables.Count < 2 || method.Body.Variables[1].VariableType.FullName != ParallelRangeProbeInstructions ||
            exit == null || exit.OpCode != OpCodes.Ret || exit.Previous.OpCode != OpCodes.Ldloc_1 ||
            il.Count(i => i.OpCode == OpCodes.Ret) != 1 ||
            il.Any(i => ReferenceEquals(i.Operand, exit) || (i.Operand is Instruction[] targets && targets.Contains(exit))))
            throw new InvalidOperationException("Inspected ParallelRangeProbe NativeSensorKernel.Read exit changed");
        scope.Replace(method, exit, Instruction.Create(OpCodes.Dup), Instruction.Create(OpCodes.Ldarg_0),
            Instruction.Create(OpCodes.Call, scope.Bridge(nameof(BetaCompatibilityCalls.ParallelRangeProbeFoldDetectionConstant))),
            Instruction.Create(OpCodes.Ret));
        scope.Count("sensor-constant-fold");
    }

    private static bool ParallelRangeProbeSequence(IList<Instruction> il, int start, params (OpCode code, Func<object, bool> operand)[] expected)
    {
        if (start < 0 || start + expected.Length > il.Count) return false;
        for (int i = 0; i < expected.Length; i++) {
            var instruction = il[start + i];
            if (instruction.OpCode != expected[i].code) return false;
            if (expected[i].operand == null ? instruction.Operand != null : !expected[i].operand(instruction.Operand)) return false;
        }
        return true;
    }

    private static bool ParallelRangeProbeCall(object operand, string owner, string name, bool instance, string returns, params string[] parameters)
        => operand is MethodReference method && method.DeclaringType.FullName == owner && method.Name == name &&
            method.HasThis == instance && method.ReturnType.FullName == returns && ParameterTypes(method, parameters);

    private static bool ParallelRangeProbeField(object operand, string owner, string name, string type)
        => operand is FieldReference field && field.DeclaringType.FullName == owner && field.Name == name && field.FieldType.FullName == type;
}
