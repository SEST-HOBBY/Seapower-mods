// J-36 afterburner and nozzle systems (J36AfterburnerNozzle.dll, 0d4e89cc,
// Workshop 3801549552) on 0.9.3-261123 (ea653e49). Two of its Harmony
// classes on SeaPower.FixedWingFlightPhysics look up members by reflection
// that this game does not have as fields:
//  - _aircraftParameters is a property (get__aircraftParameters, which
//    casts MotionController._ap), as it was in 0.9.2 and 261116, so
//    AccessTools.Field returns null;
//  - _dragPower is gone; the drag power now lives in the private struct
//    field _perf (AircraftPerfData.DragPower), which
//    AircraftPerformance.AirframeParasiticDrag reads during the flight step.
// J36HighSpeedDragPatch and J36VectorFlightPhysicsPatch therefore switch
// themselves off. In their Prefix/Postfix bodies only, each null check of
// those FieldInfos becomes the constant false, and each GetValue/SetValue
// through them calls a SEST bridge that reads the property or reads and
// writes _perf.DragPower. The postfix restores DragPower after each step, as
// the author wrote it. The static constructors still store the (null)
// lookups; nothing reads them afterwards. The other reflection the author
// guards for (GameTime.time, ObjectBase._damagedWingSide, _rootGameObject)
// stays the author's own null-checked code.
using System;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    internal const string J36SystemsHash = "0d4e89ccf8ac4c81038f624af9ee50dfa9d0befd573d89fc7c42e98fdeb6a4d7";
    internal const string J36SystemsAudit = "j36-drag-guard=2, j36-drag-read=1, j36-drag-write=2, j36-params-guard=2, j36-params-read=2, locations=2";
    private const string J36DragPatch = "J36AfterburnerNozzle.J36HighSpeedDragPatch";
    private const string J36VectorPatch = "J36AfterburnerNozzle.J36VectorFlightPhysicsPatch";

    private static ImageAdapter J36SystemsAdapter() => new ImageAdapter {
        Name = "J36Systems", Hashes = new[] { J36SystemsHash },
        RequireNative = J36SystemsRequireNative,
        RewriteMethod = J36SystemsRewrite,
        ExpectedAudit = J36SystemsAudit,
    };

    private static void J36SystemsRequireNative(ModuleDefinition native)
    {
        CurrentNativeSnapshot(native);
        var physics = native.GetType("SeaPower.FixedWingFlightPhysics");
        var property = physics?.Properties.SingleOrDefault(p => p.Name == "_aircraftParameters");
        var getter = property?.GetMethod;
        var perf = physics?.Fields.SingleOrDefault(f => f.Name == "_perf");
        var data = native.GetType("SeaPower.AircraftPerfData");
        var drag = data?.Fields.SingleOrDefault(f => f.Name == "DragPower");
        var parasitic = native.GetType("SeaPower.AircraftPerformance")?.Methods.Where(m => m.Name == "AirframeParasiticDrag").ToList();
        if (physics == null || physics.BaseType?.FullName != "SeaPower.MotionController" ||
            property == null || property.SetMethod != null || getter == null || !getter.IsPublic || !getter.HasThis || getter.HasParameters ||
            getter.ReturnType.FullName != "SeaPower.AircraftParameters" || getter.Body.CodeSize != 12 ||
            !getter.Body.Instructions.Any(i => i.OpCode == OpCodes.Ldfld && i.Operand is FieldReference ap &&
                ap.DeclaringType.FullName == "SeaPower.MotionController" && ap.Name == "_ap") ||
            physics.Fields.Any(f => f.Name == "_aircraftParameters" || f.Name == "_dragPower") ||
            perf == null || !perf.IsPrivate || perf.IsStatic || perf.FieldType.FullName != "SeaPower.AircraftPerfData" ||
            physics.Methods.Count(m => m.Name == "OnFixedUpdate" && m.HasThis && !m.HasParameters && m.ReturnType.FullName == "System.Void") != 1 ||
            data == null || !data.IsValueType || drag == null || !drag.IsPublic || drag.IsStatic || drag.FieldType.FullName != "System.Single" ||
            parasitic == null || parasitic.Count == 0 || !parasitic.All(m => m.IsStatic && m.Parameters.Count > 0 &&
                m.Parameters[0].ParameterType.FullName == "SeaPower.AircraftPerfData&" &&
                m.Body.Instructions.Any(i => i.OpCode == OpCodes.Ldfld && i.Operand is FieldReference d &&
                    d.DeclaringType.FullName == "SeaPower.AircraftPerfData" && d.Name == "DragPower")))
            throw new InvalidOperationException("Inspected 261123 fixed-wing parameters and drag power contract changed");
    }

    private static bool J36SystemsRewrite(AdapterScope scope, TypeDefinition type, MethodDefinition method)
    {
        bool dragPatch = type.FullName == J36DragPatch, vectorPatch = type.FullName == J36VectorPatch;
        if (!dragPatch && !vectorPatch) return false;
        bool Lookup(Instruction i) => i.Operand is FieldReference f && f.DeclaringType.FullName == type.FullName &&
            (f.Name == "AircraftParametersField" || f.Name == "DragPowerField");
        var sites = method.Body.Instructions.Where(Lookup).ToList();
        if (method.Name == ".cctor") {
            if (sites.Count != (dragPatch ? 2 : 1) || sites.Any(i => i.OpCode != OpCodes.Stsfld))
                throw new InvalidOperationException("Inspected J-36 reflection lookups changed in " + type.Name + "::.cctor");
            return false;
        }
        int size = dragPatch && method.Name == "Prefix" ? 306 : dragPatch && method.Name == "Postfix" ? 76 :
            vectorPatch && method.Name == "Prefix" ? 314 : 0;
        if (size == 0) {
            if (sites.Count != 0) throw new InvalidOperationException("Uninspected J-36 reflection use in " + type.Name + "::" + method.Name);
            return false;
        }
        int expected = dragPatch && method.Name == "Prefix" ? 5 : 2;
        if (method.Body.CodeSize != size || sites.Count != expected || method.Parameters.Count == 0 ||
            method.Parameters[0].Name != "__instance" || method.Parameters[0].ParameterType.FullName != "System.Object")
            throw new InvalidOperationException("Inspected J-36 " + type.Name + "::" + method.Name + " changed");
        static bool FieldInfoCall(Instruction i, OpCode op, string name, params string[] parameters) =>
            i != null && i.OpCode == op && i.Operand is MethodReference c && c.DeclaringType.FullName == "System.Reflection.FieldInfo" &&
            c.Name == name && ParameterTypes(c, parameters);
        foreach (var site in sites) {
            string field = ((FieldReference)site.Operand).Name;
            string kind = field == "DragPowerField" ? "j36-drag-" : "j36-params-";
            var next = site.Next; var call = next?.Next;
            if (site.OpCode != OpCodes.Ldsfld)
                throw new InvalidOperationException("Uninspected J-36 reflection store in " + type.Name + "::" + method.Name);
            if (next.OpCode == OpCodes.Ldnull && FieldInfoCall(call, OpCodes.Call, "op_Equality", "System.Reflection.FieldInfo", "System.Reflection.FieldInfo")) {
                // The member exists on 261123: "lookup == null" is false.
                site.OpCode = OpCodes.Ldc_I4_0; site.Operand = null;
                next.OpCode = OpCodes.Nop; call.OpCode = OpCodes.Nop; call.Operand = null;
                scope.Count(kind + "guard");
            }
            else if (next.OpCode == OpCodes.Ldarg_0 && FieldInfoCall(call, OpCodes.Callvirt, "GetValue", "System.Object")) {
                site.OpCode = OpCodes.Nop; site.Operand = null;
                call.OpCode = OpCodes.Call;
                call.Operand = scope.Bridge(field == "DragPowerField" ? nameof(BetaCompatibilityCalls.FixedWingDragPower) : nameof(BetaCompatibilityCalls.FixedWingParameters));
                scope.Count(kind + "read");
            }
            else if (field == "DragPowerField" && next.OpCode == OpCodes.Ldarg_0) {
                // The value is boxed between the receiver and SetValue; no call intervenes.
                var set = next.Next;
                while (set != null && set.OpCode.FlowControl != FlowControl.Call && set.OpCode.FlowControl != FlowControl.Branch &&
                    set.OpCode.FlowControl != FlowControl.Cond_Branch) set = set.Next;
                if (!FieldInfoCall(set, OpCodes.Callvirt, "SetValue", "System.Object", "System.Object") ||
                    set.Previous.OpCode != OpCodes.Box || (set.Previous.Operand as TypeReference)?.FullName != "System.Single")
                    throw new InvalidOperationException("Inspected J-36 drag power write changed in " + type.Name + "::" + method.Name);
                site.OpCode = OpCodes.Nop; site.Operand = null;
                set.OpCode = OpCodes.Call; set.Operand = scope.Bridge(nameof(BetaCompatibilityCalls.SetFixedWingDragPower));
                scope.Count(kind + "write");
            }
            else throw new InvalidOperationException("Uninspected J-36 reflection use in " + type.Name + "::" + method.Name);
        }
        return false;
    }
}
