using System;
using System.Collections.Generic;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    // R6 (7 Nov 2026): OspreyMechanics 1.1.45 (local.mv22.source.mechanics,
    // Workshop 3806466625) as captured on 3 Nov 2026. Its HoverFlight.Install
    // asks AccessTools.Method for ObjectBase.SetSpeedCommand by name only. The
    // beta has two overloads (SetSpeedCommand<T>(in T order) and
    // SetSpeedCommand(in SpeedRequest request)), so HarmonyX throws
    // AmbiguousMatchException, the plugin unpatches itself and its dependent
    // OspreyDeckOps is held back. Beyond that lookup the plugin uses the stable
    // speed model: ConstantSpeed as a class it stores in two fields and a local,
    // SetSpeedCommand(ISpeedCommand), ConstantSpeed.get_SpeedInKnots and
    // ReferenceEquals(unit.SpeedCommand.Value, its own command) as "the plugin
    // owns the speed". The rewrites below route exactly those sites through
    // BetaCompatibilityCalls.OspreyMechanics*; every other member it uses is
    // unchanged on the beta.
    internal const string OspreyMechanicsHash = "2349def7bf71a7df1f87b387645e4e146f66ba9bc6869a3e5001187a0a7ae98b";

    private const string OspreyMechanicsHover = "OspreyRig.HoverFlight";
    private const string OspreyMechanicsSonar = "OspreyRig.DippingSonar";

    private static ImageAdapter OspreyMechanicsAdapter() => new ImageAdapter {
        Name = "OspreyMechanics",
        Hashes = new[] { OspreyMechanicsHash },
        // The two stable class-typed fields. Finish re-types them to the beta
        // ISpeedCommand interface; Prepare checks the written image again.
        AcceptedNativeFields = new[] {
            "OspreyRig.AutoHoverState.Command: SeaPower.ConstantSpeed encoded as reference; native definition is value",
            "OspreyRig.DipState.Command: SeaPower.ConstantSpeed encoded as reference; native definition is value",
        },
        // OspreyDeckOps 1.1.36 binds GameClock, OspreyTypes and Controller.Core
        // only; it needs no rewrite. Its ACPlugin after=[local.mv22.source.mechanics]
        // still keeps it out if this image is not admitted.
        ReleasesDependentsOf = "OspreyMechanics",
        RequireNative = OspreyMechanicsRequireNative,
        RewriteMethod = OspreyMechanicsRewriteMethod,
        Finish = OspreyMechanicsFinish,
        ExpectedAudit = "hook-argument=2, hook-load=4, speed-field=2, speed-knots=2, speed-local=1, speed-make=5, " +
            "speed-read=6, speed-set=5, speed-snapshot=1, speed-target=2",
    };

    // Every speed-API site in the captured image, by original IL offset.
    // make: newobj ConstantSpeed(float, ObjectBase); set: callvirt
    // ObjectBase.SetSpeedCommand(ISpeedCommand); knots: callvirt
    // ConstantSpeed.get_SpeedInKnots; read: callvirt ObjectBase.get_SpeedCommand
    // then ReactiveProperty<ISpeedCommand>.get_Value; snapshot: the same pair
    // whose value DippingSonar keeps as ResumeSpeed; target: the two
    // SetSpeedCommand AccessTools.Method lookups.
    private static readonly Dictionary<string, (int Offset, string Kind)[]> OspreyMechanicsSites = new() {
        [OspreyMechanicsHover + "::Order(SeaPower.Aircraft,System.Single,System.Boolean)"] = new[] { (0x3d, "make"), (0x42, "set") },
        [OspreyMechanicsHover + "::SetAutoSpeed(OspreyRig.AutoHoverState,SeaPower.Aircraft,System.Single)"] = new[] { (0x1f, "make"), (0x35, "set") },
        [OspreyMechanicsHover + "::OwnsSpeed(OspreyRig.AutoHoverState,SeaPower.Aircraft)"] = new[] { (0x09, "read"), (0x26, "knots") },
        [OspreyMechanicsHover + "::ClearAuto(OspreyRig.AutoHoverState,SeaPower.Aircraft,System.Boolean,SeaPower.GoToWaypointTask,System.String)"] =
            new[] { (0xc3, "make"), (0xc8, "set") },
        [OspreyMechanicsHover + "::WaypointUpdating(SeaPower.GoToWaypointTask)"] = new[] { (0x114, "read"), (0x121, "read") },
        [OspreyMechanicsHover + "::WaypointFinished(SeaPower.GoToWaypointTask,System.Boolean)"] = new[] { (0x82, "read"), (0x8f, "read") },
        [OspreyMechanicsHover + "::Install(HarmonyLib.Harmony)"] = new[] { (0xef, "target") },
        [OspreyMechanicsSonar + "::OwnsSpeed(OspreyRig.DipState,SeaPower.Aircraft)"] = new[] { (0x0f, "read"), (0x26, "knots") },
        [OspreyMechanicsSonar + "::Speed(OspreyRig.DipState,SeaPower.Aircraft,System.Single)"] = new[] { (0x28, "make"), (0x39, "set") },
        [OspreyMechanicsSonar + "::Restore(OspreyRig.DipState,SeaPower.Aircraft,System.Boolean)"] = new[] { (0x1b, "set") },
        [OspreyMechanicsSonar + "::WaypointUpdating(SeaPower.GoToWaypointTask)"] = new[] { (0x105, "snapshot"), (0x119, "make") },
        [OspreyMechanicsSonar + "::Install(HarmonyLib.Harmony)"] = new[] { (0x144, "target") },
    };

    // The two SetSpeedCommand hooks: HoverFlight's postfix and DippingSonar's
    // prefix, with the IL offsets of every load of their speedCommand argument.
    private static readonly Dictionary<string, int[]> OspreyMechanicsHooks = new() {
        [OspreyMechanicsHover + "::SpeedCommandChanged(SeaPower.ObjectBase,SeaPower.ISpeedCommand)"] = new[] { 0x30, 0x133, 0x136 },
        [OspreyMechanicsSonar + "::SpeedCommandChanging(SeaPower.ObjectBase,SeaPower.ISpeedCommand)"] = new[] { 0x30 },
    };

    // ldtoken ObjectBase / GetTypeFromHandle / ldstr 'SetSpeedCommand' ahead of
    // each lookup, by offset.
    private static readonly Dictionary<int, int> OspreyMechanicsTargetName = new() { [0xef] = 0xe8, [0x144] = 0x129 };

    private static readonly HashSet<string> ospreyMechanicsDone = new(StringComparer.Ordinal);

    private static string OspreyMechanicsKey(TypeDefinition type, MethodDefinition method)
        => type.FullName + "::" + method.Name + "(" + String.Join(",", method.Parameters.Select(p => p.ParameterType.FullName)) + ")";

    private static void OspreyMechanicsRequireNative(ModuleDefinition native)
    {
        void Fail(string what) => throw new InvalidOperationException("Inspected beta " + what + " changed");
        bool Shape(MethodDefinition m, string returns, params string[] parameters)
            => m.ReturnType.FullName == returns && m.Parameters.Select(p => p.ParameterType.FullName).SequenceEqual(parameters);
        bool Codes(MethodDefinition m, params Code[] codes) => m.HasBody && m.Body.Instructions.Select(i => i.OpCode.Code).SequenceEqual(codes);
        bool Calls(Instruction i, string type, string name)
            => i.Operand is MethodReference r && r.DeclaringType.FullName == type && r.Name == name;

        var constant = native.GetType("SeaPower.ConstantSpeed");
        if (constant == null || !constant.IsValueType || constant.Methods.Count(m => m.IsConstructor && !m.IsStatic && m.IsPublic &&
            Shape(m, "System.Void", "System.Single", "SeaPower.ObjectBase")) != 1 ||
            !constant.Interfaces.Any(i => i.InterfaceType.FullName == "SeaPower.ISpeedOrder"))
            Fail("ConstantSpeed shape");
        // OspreyMechanicsConstantSpeed returns ConstantSpeed.ToRequest(): SpeedRequest.Knots(_speedInKnots).
        var toRequest = constant.Methods.SingleOrDefault(m => m.Name == "ToRequest" && Shape(m, "SeaPower.SpeedRequest"));
        if (toRequest == null || !Codes(toRequest, Code.Ldarg_0, Code.Ldfld, Code.Call, Code.Ret) ||
            !Calls(toRequest.Body.Instructions[2], "SeaPower.SpeedRequest", "Knots"))
            Fail("ConstantSpeed.ToRequest");

        // OspreyMechanicsSpeedOrder implements this exact interface.
        var command = native.GetType("SeaPower.ISpeedCommand");
        var members = new[] { "get_Kind", "get_Telegraph", "get_AvoidingCavitation", "get_CommandSpeedInKnots", "get_SpeedInKnots",
            "get_SpeedInMach", "get_MachLimit", "get_SpeedIsOverriden", "get_OverridenSpeedInKnots", "GetDemandedSpeedInKnots",
            "GetDemandedSpeedInMetresPerSecond", "Update", "OverrideSpeed", "CancelSpeedOverride" };
        if (command == null || !command.IsInterface || command.Methods.Count != members.Length ||
            !members.All(name => command.Methods.Count(m => m.Name == name) == 1) ||
            !Shape(command.Methods.Single(m => m.Name == "get_SpeedInKnots"), "System.Single") ||
            !Shape(command.Methods.Single(m => m.Name == "GetDemandedSpeedInKnots"), "System.Single", "SeaPower.ObjectBase"))
            Fail("ISpeedCommand shape");

        var request = native.GetType("SeaPower.SpeedRequest");
        if (request == null || !request.IsValueType ||
            request.Fields.SingleOrDefault(f => f.Name == "Kind" && f.IsPublic && f.FieldType.FullName == "SeaPower.SpeedKind") == null ||
            request.Fields.SingleOrDefault(f => f.Name == "Value" && f.IsPublic && f.FieldType.FullName == "System.Single") == null ||
            request.Fields.SingleOrDefault(f => f.Name == "Step" && f.IsPublic && f.FieldType.FullName == "System.Int32") == null ||
            request.Methods.Count(m => m.Name == "Knots" && m.IsStatic && Shape(m, "SeaPower.SpeedRequest", "System.Single")) != 1 ||
            request.Methods.Count(m => m.Name == "Equals" && !m.IsStatic && Shape(m, "System.Boolean", "SeaPower.SpeedRequest")) != 1)
            Fail("SpeedRequest shape");
        var kind = native.GetType("SeaPower.SpeedKind");
        if (kind == null || !kind.IsEnum || !new[] { ("None", 0), ("Zero", 1), ("Telegraph", 2), ("Constant", 3), ("Mach", 4) }
            .All(x => kind.Fields.Any(f => f.Name == x.Item1 && f.HasConstant && Convert.ToInt32(f.Constant) == x.Item2)))
            Fail("SpeedKind values");

        // SpeedState is the one ISpeedCommand the beta stores. Apply returns
        // false for an equal request and otherwise stores the request as given,
        // which is what request equality as "still the plugin's order" relies on.
        var state = native.GetType("SeaPower.SpeedState");
        var apply = state?.Methods.SingleOrDefault(m => m.Name == "Apply" && !m.IsStatic && Shape(m, "System.Boolean", "SeaPower.SpeedRequest&", "SeaPower.ObjectBase"));
        var getRequest = state?.Methods.SingleOrDefault(m => m.Name == "get_Request" && Shape(m, "SeaPower.SpeedRequest"));
        if (state == null || !state.Interfaces.Any(i => i.InterfaceType.FullName == "SeaPower.ISpeedCommand") || apply == null || getRequest == null ||
            !Codes(getRequest, Code.Ldarg_0, Code.Ldfld, Code.Ret) || ((FieldReference)getRequest.Body.Instructions[1].Operand).Name != "_request")
            Fail("SpeedState shape");
        var a = apply.Body.Instructions;
        if (a.Count < 15 || a[0].OpCode != OpCodes.Ldarg_0 || (a[1].Operand as FieldReference)?.Name != "_request" || a[2].OpCode != OpCodes.Ldarg_1 ||
            a[3].OpCode != OpCodes.Ldobj || !Calls(a[4], "SeaPower.SpeedRequest", "Equals") || a[5].OpCode.Code != Code.Brfalse_S ||
            a[6].OpCode != OpCodes.Ldc_I4_0 || a[7].OpCode != OpCodes.Ret ||
            a.Count(i => i.OpCode == OpCodes.Stfld && (i.Operand as FieldReference)?.Name == "_request") != 1 ||
            a.Single(i => i.OpCode == OpCodes.Stfld && (i.Operand as FieldReference)?.Name == "_request").Previous.OpCode != OpCodes.Ldobj ||
            a.Single(i => i.OpCode == OpCodes.Stfld && (i.Operand as FieldReference)?.Name == "_request").Previous.Previous.OpCode != OpCodes.Ldarg_1)
            Fail("SpeedState.Apply semantics");

        // Exactly the two overloads; the generic one forwards to the request
        // overload, so one Harmony target sees every speed order.
        var unit = native.GetType("SeaPower.ObjectBase");
        var overloads = unit.Methods.Where(m => m.Name == "SetSpeedCommand").ToList();
        var generic = overloads.SingleOrDefault(m => m.HasGenericParameters);
        var byRequest = overloads.SingleOrDefault(m => !m.HasGenericParameters);
        if (overloads.Count != 2 || generic == null || byRequest == null || generic.GenericParameters.Count != 1 ||
            generic.Parameters.Count != 1 || generic.Parameters[0].Name != "order" || !generic.Parameters[0].ParameterType.IsByReference ||
            !byRequest.IsPublic || byRequest.IsStatic || !Shape(byRequest, "System.Void", "SeaPower.SpeedRequest&") ||
            byRequest.Parameters[0].Name != "request" || byRequest.Parameters[0].ParameterType is RequiredModifierType ||
            generic.Body.Instructions.Count(i => i.OpCode == OpCodes.Call && Calls(i, "SeaPower.ObjectBase", "SetSpeedCommand") &&
                ParameterTypes((MethodReference)i.Operand, "SeaPower.SpeedRequest&")) != 1)
            Fail("ObjectBase.SetSpeedCommand overloads");
        // Mirrored by OspreyMechanicsSetSpeedCommand/OspreyMechanicsIncomingSpeedCommand:
        // Speed.ClearOverride(); if (!Speed.Apply(ref request, this)) return;
        // SpeedCommand.SetValueAndForceNotify(Speed).
        var b = byRequest.Body.Instructions;
        if (!Codes(byRequest, Code.Ldarg_0, Code.Call, Code.Callvirt, Code.Ldarg_0, Code.Call, Code.Ldarg_1, Code.Ldarg_0, Code.Callvirt,
                Code.Brtrue_S, Code.Ret, Code.Ldarg_0, Code.Call, Code.Ldarg_0, Code.Call, Code.Callvirt, Code.Ret) ||
            !Calls(b[1], "SeaPower.ObjectBase", "get_Speed") || !Calls(b[2], "SeaPower.SpeedState", "ClearOverride") ||
            !Calls(b[7], "SeaPower.SpeedState", "Apply") || !Calls(b[11], "SeaPower.ObjectBase", "get_SpeedCommand") ||
            !Calls(b[13], "SeaPower.ObjectBase", "get_Speed") || ((MethodReference)b[14].Operand).Name != "SetValueAndForceNotify")
            Fail("ObjectBase.SetSpeedCommand(in SpeedRequest) body");
        var speed = unit.Methods.SingleOrDefault(m => m.Name == "get_Speed" && Shape(m, "SeaPower.SpeedState"));
        var speedCommand = unit.Methods.SingleOrDefault(m => m.Name == "get_SpeedCommand" && Shape(m, "UniRx.ReactiveProperty`1<SeaPower.ISpeedCommand>"));
        if (speed == null || speedCommand == null || !speed.IsPublic || !speedCommand.IsPublic)
            Fail("ObjectBase.Speed/SpeedCommand");
        lock (ospreyMechanicsDone) ospreyMechanicsDone.Clear();
    }

    private static bool OspreyMechanicsRewriteMethod(AdapterScope scope, TypeDefinition type, MethodDefinition method)
    {
        string key = OspreyMechanicsKey(type, method);
        void Fail(string what) => throw new InvalidOperationException("Inspected OspreyMechanics " + key + " " + what + " changed");
        OspreyMechanicsSites.TryGetValue(key, out var sites);
        var seen = new HashSet<int>();

        if (OspreyMechanicsHooks.TryGetValue(key, out int[] loads)) {
            OspreyMechanicsRewriteHook(scope, method, loads, Fail);
            scope.Count("hook-argument");
        }
        if (key == OspreyMechanicsHover + "::SetAutoSpeed(OspreyRig.AutoHoverState,SeaPower.Aircraft,System.Single)") {
            var variables = method.Body.Variables;
            if (variables.Count != 1 || variables[0].VariableType.FullName != "SeaPower.ConstantSpeed" || variables[0].VariableType.IsValueType)
                Fail("ConstantSpeed local");
            variables[0].VariableType = scope.Module.ImportReference(scope.Native.GetType("SeaPower.ISpeedCommand"));
            scope.Count("speed-local");
        }

        var all = method.Body.Instructions.ToArray();
        foreach (var instruction in all) {
            if (instruction.Operand is not MemberReference member) continue;
            if (member is TypeReference token && token.FullName == "SeaPower.ConstantSpeed")
                Fail("ConstantSpeed type operand IL_" + instruction.Offset.ToString("x4"));
            string owner = member.DeclaringType?.FullName;
            string kind = OspreyMechanicsSiteKind(instruction);
            bool speedApi = owner == "SeaPower.ConstantSpeed" || (owner == "SeaPower.ObjectBase" &&
                (member.Name == "SetSpeedCommand" || member.Name == "get_SpeedCommand" || member.Name == "get_Speed"));
            if (kind == null && !speedApi) continue;
            var site = sites?.SingleOrDefault(s => s.Offset == instruction.Offset) ?? default;
            if (kind == "target" && site.Kind != "target") continue; // the plugin's other AccessTools.Method lookups
            if (kind == null || site.Kind != kind || !seen.Add(instruction.Offset))
                Fail("speed site IL_" + instruction.Offset.ToString("x4") + " (" + instruction.OpCode + " " + member.FullName + ")");
            switch (kind) {
                case "make":
                    scope.Replace(method, instruction, Instruction.Create(OpCodes.Call, scope.Bridge("OspreyMechanicsConstantSpeed")));
                    scope.Count("speed-make"); break;
                case "set":
                    scope.Replace(method, instruction, Instruction.Create(OpCodes.Call, scope.Bridge("OspreyMechanicsSetSpeedCommand")));
                    scope.Count("speed-set"); break;
                case "knots":
                    var knots = scope.Native.GetType("SeaPower.ISpeedCommand").Methods.Single(m => m.Name == "get_SpeedInKnots");
                    scope.Replace(method, instruction, Instruction.Create(OpCodes.Callvirt, scope.Module.ImportReference(knots)));
                    scope.Count("speed-knots"); break;
                case "read":
                case "snapshot":
                    // unit; get_SpeedCommand; get_Value  ->  unit; dup; get_SpeedCommand;
                    // get_Value; call bridge(unit, value). The native read stays as is.
                    var value = instruction.Next;
                    if (value == null || value.OpCode != OpCodes.Callvirt || value.Operand is not MethodReference getter ||
                        getter.Name != "get_Value" || getter.Parameters.Count != 0 || !getter.HasThis ||
                        getter.DeclaringType.FullName != "UniRx.ReactiveProperty`1<SeaPower.ISpeedCommand>" ||
                        OspreyMechanicsIsTarget(method, value))
                        Fail("speed read IL_" + instruction.Offset.ToString("x4"));
                    scope.ExpandBranches(method);
                    scope.Replace(method, value, Instruction.Create(OpCodes.Callvirt, getter),
                        Instruction.Create(OpCodes.Call, scope.Bridge(kind == "read" ? "OspreyMechanicsSpeedCommand" : "OspreyMechanicsSpeedSnapshot")));
                    scope.Replace(method, instruction, Instruction.Create(OpCodes.Dup), Instruction.Create(OpCodes.Callvirt, (MethodReference)member));
                    scope.Count(kind == "read" ? "speed-read" : "speed-snapshot"); break;
                case "target":
                    var name = all.SingleOrDefault(i => i.Offset == OspreyMechanicsTargetName[instruction.Offset]);
                    if (name?.OpCode != OpCodes.Ldstr || !Equals(name.Operand, "SetSpeedCommand") ||
                        name.Previous?.OpCode != OpCodes.Call || (name.Previous.Operand as MethodReference)?.Name != "GetTypeFromHandle" ||
                        name.Previous.Previous?.OpCode != OpCodes.Ldtoken || (name.Previous.Previous.Operand as TypeReference)?.FullName != "SeaPower.ObjectBase")
                        Fail("SetSpeedCommand lookup IL_" + instruction.Offset.ToString("x4"));
                    scope.Replace(method, instruction, Instruction.Create(OpCodes.Call, scope.Bridge("OspreyMechanicsMethod")));
                    scope.Count("speed-target"); break;
            }
        }
        if (sites != null && (seen.Count != sites.Length || sites.Any(s => !seen.Contains(s.Offset)))) Fail("speed sites");
        if (sites != null || loads != null) lock (ospreyMechanicsDone) if (!ospreyMechanicsDone.Add(key)) Fail("method identity");
        return false;
    }

    // The structural shape of each speed-API operand the plugin uses.
    private static string OspreyMechanicsSiteKind(Instruction instruction)
    {
        if (instruction.Operand is not MethodReference call) return null;
        string owner = call.DeclaringType.FullName;
        if (instruction.OpCode == OpCodes.Newobj && owner == "SeaPower.ConstantSpeed" && call.Name == ".ctor" && call.HasThis &&
            ParameterTypes(call, "System.Single", "SeaPower.ObjectBase")) return "make";
        if (instruction.OpCode == OpCodes.Callvirt && owner == "SeaPower.ObjectBase" && call.Name == "SetSpeedCommand" && call.HasThis &&
            !call.HasGenericParameters && call.ReturnType.FullName == "System.Void" && ParameterTypes(call, "SeaPower.ISpeedCommand")) return "set";
        if (instruction.OpCode == OpCodes.Callvirt && owner == "SeaPower.ConstantSpeed" && call.Name == "get_SpeedInKnots" && call.HasThis &&
            call.Parameters.Count == 0 && call.ReturnType.FullName == "System.Single") return "knots";
        if (instruction.OpCode == OpCodes.Callvirt && owner == "SeaPower.ObjectBase" && call.Name == "get_SpeedCommand" && call.HasThis &&
            call.Parameters.Count == 0 && call.ReturnType.FullName == "UniRx.ReactiveProperty`1<SeaPower.ISpeedCommand>") {
            var value = instruction.Next?.Operand as MethodReference;
            return value?.Name == "get_Value" ? (instruction.Next.Next?.OpCode == OpCodes.Dup ? "snapshot" : "read") : null;
        }
        if (instruction.OpCode == OpCodes.Call && owner == "HarmonyLib.AccessTools" && call.Name == "Method" && !call.HasThis &&
            call.ReturnType.FullName == "System.Reflection.MethodInfo" &&
            ParameterTypes(call, "System.Type", "System.String", "System.Type[]", "System.Type[]")) return "target";
        return null;
    }

    // The hook's speedCommand argument becomes "ref SpeedRequest request", the
    // name HarmonyX binds to beta SetSpeedCommand(in SpeedRequest request). Each
    // load of it becomes OspreyMechanicsIncomingSpeedCommand(__instance, ref request),
    // which hands the plugin's in-flight command back, as stable passed it.
    private static void OspreyMechanicsRewriteHook(AdapterScope scope, MethodDefinition method, int[] loads, Action<string> fail)
    {
        if (!method.IsStatic || method.ReturnType.FullName != "System.Void" || method.Parameters.Count != 2 ||
            method.Parameters[0].Name != "__instance" || method.Parameters[0].ParameterType.FullName != "SeaPower.ObjectBase" ||
            method.Parameters[1].Name != "speedCommand" || method.Parameters[1].ParameterType.FullName != "SeaPower.ISpeedCommand")
            fail("hook signature");
        var argument = method.Parameters[1];
        var uses = method.Body.Instructions.Where(i => i.Operand == argument || i.OpCode == OpCodes.Ldarg_1).ToList();
        // No ldarga/starg/ldarg.s on it: only the plain loads listed above.
        if (uses.Count != loads.Length || uses.Any(i => i.OpCode != OpCodes.Ldarg_1) || !uses.Select(i => i.Offset).SequenceEqual(loads))
            fail("speedCommand loads");
        argument.Name = "request";
        argument.ParameterType = new ByReferenceType(scope.Module.ImportReference(scope.Native.GetType("SeaPower.SpeedRequest")));
        scope.ExpandBranches(method);
        var bridge = scope.Bridge("OspreyMechanicsIncomingSpeedCommand");
        // The original instruction stays first, so the try that starts at
        // SpeedCommandChanged IL_0133 still starts with this load.
        foreach (var load in uses) {
            scope.Replace(method, load, Instruction.Create(OpCodes.Ldarg_0), Instruction.Create(OpCodes.Ldarg_1), Instruction.Create(OpCodes.Call, bridge));
            scope.Count("hook-load");
        }
    }

    private static bool OspreyMechanicsIsTarget(MethodDefinition method, Instruction instruction)
        => method.Body.Instructions.Any(i => i.Operand == instruction || (i.Operand is Instruction[] targets && targets.Contains(instruction))) ||
            method.Body.ExceptionHandlers.Any(h => h.TryStart == instruction || h.TryEnd == instruction || h.HandlerStart == instruction ||
                h.HandlerEnd == instruction || h.FilterStart == instruction);

    private static void OspreyMechanicsFinish(AdapterScope scope)
    {
        lock (ospreyMechanicsDone) {
            var missing = OspreyMechanicsSites.Keys.Concat(OspreyMechanicsHooks.Keys).Where(k => !ospreyMechanicsDone.Contains(k)).ToList();
            if (missing.Count != 0) throw new InvalidOperationException("Inspected OspreyMechanics methods changed: " + String.Join(", ", missing));
        }
        var command = scope.Module.ImportReference(scope.Native.GetType("SeaPower.ISpeedCommand"));
        foreach (string name in new[] { "OspreyRig.AutoHoverState", "OspreyRig.DipState" }) {
            var field = scope.Module.GetType(name)?.Fields.SingleOrDefault(f => f.Name == "Command");
            if (field == null || field.IsStatic || !field.IsAssembly || field.FieldType.FullName != "SeaPower.ConstantSpeed" || field.FieldType.IsValueType)
                throw new InvalidOperationException("Inspected OspreyMechanics " + name + ".Command changed");
            field.FieldType = command;
            scope.Count("speed-field");
        }
        if (Types(scope.Module.Types).SelectMany(t => t.Methods).Where(m => m.HasBody)
            .Any(m => m.Body.Variables.Any(v => v.VariableType.FullName == "SeaPower.ConstantSpeed")))
            throw new InvalidOperationException("Inspected OspreyMechanics ConstantSpeed locals changed");
    }
}
