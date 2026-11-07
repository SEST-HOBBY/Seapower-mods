// ParallelRangeProbe 0.12.0 (R6). Used only by its hash-pinned private image.
using System;
using System.Collections;
using System.Reflection;
using System.Reflection.Emit;

namespace AnchorChain;

public static partial class BetaCompatibilityCalls
{
    // Called by the adapted WorkerExpansion.NativeSensorKernel.Read(MethodInfo)
    // with the instruction list it decoded, just before it returns. For beta
    // SeaPower.RadarCalculator.BaseMaxDetectionRangeMeter(float, float, float, float)
    // only, the single `ldsfld RadarCalculator::FourPiCubed` (IL_0026) becomes
    // `ldc.r4 <FourPiCubed>`: the value native reads there, which beta's
    // RadarCalculator..cctor sets once to Mathf.Pow(12.566371f, 3f) (the field
    // is static initonly). Every other method's list is left untouched, and
    // any other static field read in that method throws, so the plugin's own
    // FALLBACK path keeps the native game behaviour.
    public static void ParallelRangeProbeFoldDetectionConstant(IList code, MethodInfo source)
    {
        if (code == null || !ParallelRangeProbeIsDetection(source)) return;
        var four = source.DeclaringType.GetField("FourPiCubed", BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic);
        if (four == null || !ParallelRangeProbeIsFourPiCubed(four))
            throw new InvalidOperationException("Inspected beta RadarCalculator.FourPiCubed changed");
        const BindingFlags fields = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;
        int folded = 0;
        foreach (object instruction in code) {
            var type = instruction?.GetType();
            var opcode = type?.GetField("opcode", fields);
            var operand = type?.GetField("operand", fields);
            if (type?.FullName != "WorkerExpansion.NativeSensorKernel+Instruction" || opcode?.FieldType != typeof(OpCode) ||
                operand?.FieldType != typeof(object))
                throw new InvalidOperationException("Inspected ParallelRangeProbe sensor instruction changed");
            var op = (OpCode)opcode.GetValue(instruction);
            if (op == OpCodes.Ldsflda || op == OpCodes.Stsfld)
                throw new InvalidOperationException("Uninspected static field access in beta detection kernel");
            if (op != OpCodes.Ldsfld) continue;
            if (!(operand.GetValue(instruction) is FieldInfo field) || !ParallelRangeProbeIsFourPiCubed(field))
                throw new InvalidOperationException("Uninspected static read in beta detection kernel");
            opcode.SetValue(instruction, OpCodes.Ldc_R4);
            operand.SetValue(instruction, (float)four.GetValue(null));
            folded++;
        }
        if (folded != 1) throw new InvalidOperationException("Beta detection kernel fold count changed: " + folded);
    }

    // Structural match, never reference equality: declaring type, name,
    // static, parameter and return types.
    public static bool ParallelRangeProbeIsDetection(MethodInfo method)
    {
        if (method == null || !method.IsStatic || method.Name != "BaseMaxDetectionRangeMeter" ||
            method.DeclaringType?.FullName != "SeaPower.RadarCalculator" || method.ReturnType.FullName != "System.Single") return false;
        var parameters = method.GetParameters();
        if (parameters.Length != 4) return false;
        foreach (var parameter in parameters) if (parameter.ParameterType.FullName != "System.Single") return false;
        return true;
    }

    private static bool ParallelRangeProbeIsFourPiCubed(FieldInfo field)
        => field.Name == "FourPiCubed" && field.IsStatic && field.IsInitOnly &&
            field.DeclaringType?.FullName == "SeaPower.RadarCalculator" && field.FieldType.FullName == "System.Single";
}
