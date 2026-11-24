// Osprey Mechanics 1.1.46 (OspreyMechanics.dll, 7761f0a9, Workshop
// 3806466625) on 0.9.3-261123 (ea653e49). Its hover flight replaces
// FixedWingFlightPhysics' step while the rotors are vertical and burns fuel
// once per sub-step with Aircraft.UpdateFuelConsumption(distance), where
// distance = Mathf.Max(speed, 48.872334) * step. 261123 has no
// distance-based burn: UpdateFuelConsumption() only refreshes the readout,
// and the native fixed-wing step burns through
// AircraftPerformance.FuelFlow, BurnFuelAtRate and
// UpdateFuelConsumptionThrottled. The one call site, in
// OspreyRig.HoverFlight::Physics, now also passes the sub-step length and the
// physics component to BetaCompatibilityCalls.OspreyHoverFuel, which burns the
// way FixedWingFlightPhysics.FixedUpdateBody does at the author's floored
// hover speed. Osprey Deck Ops (fcbe4762, same item) needs no rewrite; once
// this adapter pins its library, HeldDependency no longer holds it.
using System;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    internal const string OspreyMechanicsHash = "7761f0a92dba79076da23663fcf546590851e0ee826b1488e00cd77d83bb494e";
    internal const string OspreyMechanicsAudit = "hover-fuel=1";

    private static ImageAdapter OspreyMechanicsAdapter() => new ImageAdapter {
        Name = "OspreyMechanics", Hashes = new[] { OspreyMechanicsHash },
        RequireNative = OspreyMechanicsRequireNative,
        RewriteCall = OspreyMechanicsCall,
        ExpectedAudit = OspreyMechanicsAudit,
    };

    private static void OspreyMechanicsRequireNative(ModuleDefinition native)
    {
        CurrentNativeSnapshot(native);
        var aircraft = native.GetType("SeaPower.Aircraft");
        var physics = native.GetType("SeaPower.FixedWingFlightPhysics");
        var motion = native.GetType("SeaPower.MotionController");
        var burn = aircraft?.Methods.Where(m => m.Name == "BurnFuelAtRate").ToList();
        var throttled = aircraft?.Methods.Where(m => m.Name == "UpdateFuelConsumptionThrottled").ToList();
        var flow = native.GetType("SeaPower.AircraftPerformance")?.Methods.Where(m => m.Name == "FuelFlow").ToList();
        var position = motion?.Methods.Where(m => m.Name == "get_Position").ToList();
        var body = physics?.Methods.SingleOrDefault(m => m.Name == "FixedUpdateBody" && m.HasThis && !m.HasParameters);
        bool Calls(Instruction i, string owner, string name) => i.Operand is MethodReference c && c.DeclaringType.FullName == owner && c.Name == name;
        if (aircraft == null || physics == null || motion == null || physics.BaseType?.FullName != motion.FullName ||
            burn.Count != 1 || !burn[0].IsPublic || !burn[0].HasThis || burn[0].ReturnType.FullName != "System.Void" ||
            !ParameterTypes(burn[0], "System.Single", "System.Single") ||
            // The bridge scales the rate by step/fixedDeltaTime because the native burn is rate * fixedDeltaTime.
            burn[0].Body.Instructions.Count(i => Calls(i, "SeaPower.GameTime", "get_fixedDeltaTime")) != 1 ||
            burn[0].Body.Instructions.Count(i => Calls(i, "SeaPower.ObjectBase", "BurnFuel")) != 1 ||
            throttled.Count != 1 || !throttled[0].IsPublic || !throttled[0].HasThis || throttled[0].HasParameters ||
            aircraft.Methods.Any(m => m.Name == "UpdateFuelConsumption" && m.HasParameters) ||
            flow.Count != 1 || !flow[0].IsPublic || !flow[0].IsStatic || flow[0].ReturnType.FullName != "System.Single" ||
            !ParameterTypes(flow[0], "SeaPower.AircraftPerfData&", "System.Single", "System.Single", "System.Single") ||
            physics.Fields.SingleOrDefault(f => f.Name == "_perf")?.FieldType.FullName != "SeaPower.AircraftPerfData" ||
            physics.Fields.SingleOrDefault(f => f.Name == "_physThrust")?.FieldType.FullName != "System.Single" ||
            position.Count != 1 || !position[0].IsFamily || !position[0].HasThis || position[0].ReturnType.FullName != "UnityEngine.Vector3" ||
            body == null)
            throw new InvalidOperationException("Inspected 261123 aircraft fuel burn contract changed");
        // The native fixed-wing step: altitude = Position.y * 67.2000656, then
        // FuelFlow(ref _perf, Velocity, altitude, _physThrust), BurnFuelAtRate(rate,
        // Velocity), UpdateFuelConsumptionThrottled(), only while fuel is above 0.
        var il = body.Body.Instructions;
        int Index(Func<Instruction, bool> match) { var found = il.FirstOrDefault(match); return found == null ? -1 : il.IndexOf(found); }
        int scale = Index(i => i.OpCode == OpCodes.Ldc_R4 && Equals(i.Operand, 67.2000656f));
        int mass = Index(i => i.OpCode == OpCodes.Ldfld && i.Operand is FieldReference f && f.Name == "_currentFuelMass");
        int fuel = Index(i => Calls(i, "SeaPower.AircraftPerformance", "FuelFlow"));
        int rate = Index(i => Calls(i, "SeaPower.Aircraft", "BurnFuelAtRate"));
        int refresh = Index(i => Calls(i, "SeaPower.Aircraft", "UpdateFuelConsumptionThrottled"));
        if (body.Body.CodeSize != 845 || scale < 0 || !(scale < mass && mass < fuel && fuel < rate && rate < refresh) ||
            il[fuel - 1].OpCode != OpCodes.Ldfld || (il[fuel - 1].Operand as FieldReference)?.Name != "_physThrust" ||
            il.Count(i => Calls(i, "SeaPower.AircraftPerformance", "FuelFlow")) != 1)
            throw new InvalidOperationException("Inspected 261123 fixed-wing fuel step changed");
    }

    private static bool OspreyMechanicsCall(AdapterScope scope, TypeDefinition type, MethodDefinition method, Instruction instruction, MethodReference call)
    {
        if (call.DeclaringType.FullName != "SeaPower.Aircraft" || call.Name != "UpdateFuelConsumption") return false;
        var step = method.Body.Variables.Count > 9 ? method.Body.Variables[9] : null;
        var multiply = instruction.Previous; var load = multiply?.Previous;
        if (type.FullName != "OspreyRig.HoverFlight" || method.Name != "Physics" || method.Body.CodeSize != 1194 ||
            !method.IsStatic || !ParameterTypes(method, "SeaPower.FixedWingFlightPhysics") ||
            instruction.OpCode != OpCodes.Callvirt || !call.HasThis || call.ReturnType.FullName != "System.Void" ||
            !ParameterTypes(call, "System.Single") || step == null || step.VariableType.FullName != "System.Single" ||
            multiply.OpCode != OpCodes.Mul || !(load.OpCode == OpCodes.Ldloc_S || load.OpCode == OpCodes.Ldloc) || load.Operand != step ||
            !(load.Previous.OpCode == OpCodes.Call && load.Previous.Operand is MethodReference max && max.Name == "Max" &&
              max.DeclaringType.FullName == "UnityEngine.Mathf") ||
            load.Previous.Previous.OpCode != OpCodes.Ldc_R4 || !Equals(load.Previous.Previous.Operand, 48.8723335f))
            throw new InvalidOperationException("Uninspected Osprey fuel consumption call in " + type.FullName + "::" + method.Name);
        scope.Replace(method, instruction, Instruction.Create(OpCodes.Ldloc, step), Instruction.Create(OpCodes.Ldarg_0),
            Instruction.Create(OpCodes.Call, scope.Bridge(nameof(BetaCompatibilityCalls.OspreyHoverFuel))));
        scope.Count("hover-fuel");
        return true;
    }
}
