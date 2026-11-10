using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    // R6 (7 Nov 2026): Automatic SAR (Workshop 3774105087, AutomaticSAR.dll,
    // [ACPlugin "local.automatic-sar" 0.1.0]) as captured on 3 Nov 2026. On the
    // beta its PatchAll throws: PlayerCommandPatch.TargetMethods yields the
    // open generic ObjectBase.SetSpeedCommand<T>(ref T) first, which HarmonyX
    // 2.9 cannot patch, so every later command patch is lost and the plugin
    // never finishes initializing. Its speed code also uses the stable
    // ISpeedCommand classes (ConstantSpeed, ConstantMach and its own
    // 12-member SarConstantSpeed), and its route sampling and helicopter
    // approach call the removed GeoPosition.CourseTo.
    internal const string AutomaticSARHash = "bcd193256a8078652bacb4a0055d713fc0e7b0c1fe0d76d5152acf733b937361";
    private const string AutomaticSARCoordinator = "AutomaticSAR.RescueCoordinator";
    private const string AutomaticSARTargets = "AutomaticSAR.PlayerCommandPatch/<TargetMethods>d__0";
    private const string AutomaticSARCommand = "AutomaticSAR.RescueCoordinator/SarConstantSpeed";
    private const string AutomaticSARStableSet = "System.Void SeaPower.ObjectBase::SetSpeedCommand(SeaPower.ISpeedCommand)";
    private const string AutomaticSARValue = "callvirt !0 UniRx.ReactiveProperty`1<SeaPower.ISpeedCommand>::get_Value()";

    private static ImageAdapter AutomaticSARAdapter() => new ImageAdapter {
        Name = "AutomaticSAR",
        Hashes = new[] { AutomaticSARHash },
        RequireNative = AutomaticSARRequireNative,
        RewriteMethod = AutomaticSARRewriteMethod,
        RewriteCall = AutomaticSARRewriteCall,
        Finish = AutomaticSARFinish,
        ExpectedAudit = "bearings=1, generic-filter=1, lerp-body=1, local-retype=2, mach-make=1, speed-interface=2, " +
            "speed-kind=2, speed-make=2, speed-read=2, speed-set=3, sub-speed=1, terrain-height=5, ui-forwarder=1",
    };

    // The beta shapes the rewrites and the AutomaticSAR bridges rely on.
    private static void AutomaticSARRequireNative(ModuleDefinition native)
    {
        void Require(bool ok, string what) { if (!ok) throw new InvalidOperationException("Inspected beta " + what + " changed"); }
        TypeDefinition Type(string name) => native.GetType(name) ?? throw new InvalidOperationException("Inspected beta " + name + " changed");
        var unit = Type("SeaPower.ObjectBase");
        var sets = unit.Methods.Where(m => m.Name == "SetSpeedCommand").ToList();
        var generic = sets.SingleOrDefault(m => m.HasGenericParameters);
        var concrete = sets.SingleOrDefault(m => !m.HasGenericParameters);
        Require(sets.Count == 2 && generic != null && concrete != null && generic.IsPublic && !generic.IsStatic &&
            generic.GenericParameters.Count == 1 && generic.ReturnType.FullName == "System.Void" && generic.Parameters.Count == 1 &&
            generic.Parameters[0].ParameterType is ByReferenceType reference && reference.ElementType == generic.GenericParameters[0] &&
            concrete.IsPublic && !concrete.IsStatic && concrete.ReturnType.FullName == "System.Void" && ParameterTypes(concrete, "SeaPower.SpeedRequest&"),
            "ObjectBase.SetSpeedCommand overloads");
        Require(unit.Methods.Any(m => m.Name == "get_SpeedCommand" && m.Parameters.Count == 0 &&
            m.ReturnType.FullName == "UniRx.ReactiveProperty`1<SeaPower.ISpeedCommand>") &&
            unit.Methods.Any(m => m.Name == "get_Speed" && m.Parameters.Count == 0 && m.ReturnType.FullName == "SeaPower.SpeedState"),
            "ObjectBase.SpeedCommand/Speed");
        var command = Type("SeaPower.ISpeedCommand");
        bool Member(TypeDefinition type, string name, string result, params string[] parameters)
            => type.Methods.Count(m => m.Name == name && !m.IsStatic && m.ReturnType.FullName == result && ParameterTypes(m, parameters)) == 1;
        Require(command.IsInterface && command.Methods.Count == 14 && Member(command, "get_Kind", "SeaPower.SpeedKind") &&
            Member(command, "get_Telegraph", "System.Int32") && Member(command, "get_SpeedInKnots", "System.Single") &&
            Member(command, "get_SpeedInMach", "System.Single") && Member(command, "GetDemandedSpeedInKnots", "System.Single", "SeaPower.ObjectBase"),
            "ISpeedCommand members");
        var state = Type("SeaPower.SpeedState");
        Require(state.Interfaces.Any(i => i.InterfaceType.FullName == "SeaPower.ISpeedCommand") &&
            !state.Interfaces.Any(i => i.InterfaceType.FullName == "System.IDisposable"), "SpeedState interfaces");
        var kind = Type("SeaPower.SpeedKind");
        object Constant(string name) => kind.Fields.SingleOrDefault(f => f.Name == name && f.HasConstant)?.Constant;
        Require(kind.IsEnum && kind.Fields.Single(f => f.Name == "value__").FieldType.FullName == "System.Byte" &&
            Equals(Constant("Constant"), (byte)3) && Equals(Constant("Mach"), (byte)4), "SpeedKind values");
        foreach (string name in new[] { "SeaPower.ConstantSpeed", "SeaPower.ConstantMach" }) {
            var order = Type(name);
            Require(order.IsValueType && order.Methods.Any(m => m.IsConstructor && !m.IsStatic && ParameterTypes(m, "System.Single", "SeaPower.ObjectBase")) &&
                Member(order, "ToRequest", "SeaPower.SpeedRequest") && !order.Methods.Any(m => m.Name.StartsWith("get_", StringComparison.Ordinal)),
                name + " order shape");
        }
        var request = Type("SeaPower.SpeedRequest");
        Require(request.IsValueType && new[] { "Knots", "Mach" }.All(name => request.Methods.Count(m => m.Name == name && m.IsStatic &&
            m.ReturnType.FullName == "SeaPower.SpeedRequest" && ParameterTypes(m, "System.Single")) == 1), "SpeedRequest.Knots/Mach");
        var geo = Type("SeaPower.GeoPosition");
        Require(geo.IsValueType && !geo.Methods.Any(m => m.Name == "CourseTo") && Member(geo, "HeadingToPosition", "System.Single", "SeaPower.GeoPosition") &&
            Member(geo, "GeoOffsetByDistanceOnHeading", "SeaPower.GeoPosition", "System.Single", "System.Single") &&
            Member(geo, "get_Latitude", "System.Double") && Member(geo, "get_Longitude", "System.Double") &&
            geo.Fields.Any(f => f.Name == "_height" && f.IsPublic && !f.IsStatic && f.FieldType.FullName == "System.Double") &&
            geo.Methods.Any(m => m.IsConstructor && !m.IsStatic && ParameterTypes(m, "System.Double", "System.Double", "System.Double") &&
                m.Parameters.Select(p => p.Name).SequenceEqual(new[] { "latitude", "longitude", "height" })),
            "GeoPosition members");
        Require(Type("SeaPower.Utils").Methods.Count(m => m.Name == "WrapAngle" && m.IsStatic && m.IsPublic &&
            m.ReturnType.FullName == "System.Double" && ParameterTypes(m, "System.Double")) == 1, "Utils.WrapAngle(double)");
    }

    // Instruction text without offsets: opcode, operand, branch targets as
    // their original IL offsets. Used to match the captured author IL exactly.
    private static string AutomaticSARText(Instruction instruction)
    {
        object operand = instruction.Operand;
        string text = operand switch {
            null => "",
            Instruction target => " IL_" + target.Offset.ToString("x4"),
            Instruction[] targets => " (" + String.Join(",", targets.Select(t => "IL_" + t.Offset.ToString("x4"))) + ")",
            MemberReference member => " " + member.FullName,
            VariableDefinition variable => " V" + variable.Index,
            ParameterDefinition parameter => " A" + parameter.Index,
            string literal => " \"" + literal + "\"",
            _ => " " + Convert.ToString(operand, CultureInfo.InvariantCulture),
        };
        return instruction.OpCode.Name + text;
    }

    // The one instruction run in the method with exactly these texts.
    private static Instruction[] AutomaticSARFind(MethodDefinition method, params string[] texts)
    {
        var list = method.Body.Instructions;
        Instruction[] found = null;
        for (int start = 0; start + texts.Length <= list.Count; start++) {
            int k = 0;
            while (k < texts.Length && AutomaticSARText(list[start + k]) == texts[k]) k++;
            if (k != texts.Length) continue;
            if (found != null) throw new InvalidOperationException("Inspected AutomaticSAR " + method.Name + " IL is ambiguous");
            found = list.Skip(start).Take(texts.Length).ToArray();
        }
        return found ?? throw new InvalidOperationException("Inspected AutomaticSAR " + method.Name + " IL changed");
    }

    private static bool AutomaticSARIs(MethodDefinition method, string name, bool isStatic, string result, params string[] parameters)
        => method.Name == name && method.IsStatic == isStatic && method.ReturnType.FullName == result && ParameterTypes(method, parameters);

    private static bool AutomaticSARRewriteMethod(AdapterScope scope, TypeDefinition type, MethodDefinition method)
    {
        if (type.FullName == AutomaticSARTargets && method.Name == "MoveNext") {
            if (!AutomaticSARIs(method, "MoveNext", false, "System.Boolean") || method.Body.ExceptionHandlers.Count != 0)
                throw new InvalidOperationException("Inspected AutomaticSAR TargetMethods iterator changed");
            AutomaticSARFilterGenericTargets(scope, method);
        }
        else if (type.FullName == AutomaticSARCoordinator) {
            if (method.Name == "InterpolateGeoPosition") AutomaticSARInterpolate(scope, method);
            else if (method.Name == "GetHelicopterOvershootWaypoint") AutomaticSAROvershoot(scope, method);
            else if (method.Name == "SetRescueSpeed") AutomaticSARRescueSpeed(scope, method);
            else if (method.Name == "SetVtolKnotSpeed") AutomaticSARVtolSpeed(scope, method, false);
            else if (method.Name == "SetVtolMachSpeed") AutomaticSARVtolSpeed(scope, method, true);
            else if (method.Name == "WasCalledDirectlyFromGameUi") AutomaticSARSkipForwarder(scope, method);
        }
        // Any stable-only speed type left in a type token or a local anywhere
        // else is a site this adapter did not inspect: fail closed.
        foreach (var variable in method.Body.Variables)
            if (AutomaticSARStableOrder(variable.VariableType))
                throw new InvalidOperationException("Uninspected AutomaticSAR stable speed local in " + method.FullName);
        foreach (var instruction in method.Body.Instructions)
            if (instruction.Operand is TypeReference token && AutomaticSARStableOrder(token))
                throw new InvalidOperationException("Uninspected AutomaticSAR stable speed type in " + method.FullName);
        return false;
    }

    private static bool AutomaticSARStableOrder(TypeReference type)
        => type.FullName == "SeaPower.ConstantSpeed" || type.FullName == "SeaPower.ConstantMach";

    // Every rewritten call is handled in RewriteMethod; any stable-only member
    // still referenced here is an uninspected site.
    private static bool AutomaticSARRewriteCall(AdapterScope scope, TypeDefinition type, MethodDefinition method, Instruction instruction, MethodReference call)
    {
        string owner = call.DeclaringType.FullName;
        if ((owner == "SeaPower.GeoPosition" && call.Name == "CourseTo") || call.FullName == AutomaticSARStableSet ||
            owner == "SeaPower.ConstantSpeed" || owner == "SeaPower.ConstantMach")
            throw new InvalidOperationException("Uninspected AutomaticSAR stable member " + call.FullName + " in " + method.FullName);
        return false;
    }

    // generic-filter: on the beta, typeof(ObjectBase).GetMethods yields the
    // open generic SetSpeedCommand<T>(ref T) first. HarmonyX cannot patch it,
    // and its failure stops PatchAll. Skip generic method definitions before
    // the name tests, exactly as a failed name test does; the concrete
    // SetSpeedCommand(ref SpeedRequest), which every speed order reaches, stays.
    private static void AutomaticSARFilterGenericTargets(AdapterScope scope, MethodDefinition method)
    {
        AutomaticSARFind(method,
            "ldarg.0", "ldtoken SeaPower.ObjectBase",
            "call System.Type System.Type::GetTypeFromHandle(System.RuntimeTypeHandle)", "ldloc.1",
            "callvirt System.Reflection.MethodInfo[] System.Type::GetMethods(System.Reflection.BindingFlags)");
        var start = AutomaticSARFind(method,
            "ldelem.ref", "stloc.2", "ldloc.2", "callvirt System.String System.Reflection.MemberInfo::get_Name()",
            "ldstr \"setWaypointTask\"", "call System.Boolean System.String::op_Equality(System.String,System.String)", "brtrue.s IL_00c9");
        var speed = AutomaticSARFind(method,
            "ldloc.2", "callvirt System.String System.Reflection.MemberInfo::get_Name()", "ldstr \"SetSpeedCommand\"",
            "call System.Boolean System.String::op_Equality(System.String,System.String)", "brfalse.s IL_00e0",
            "ldarg.0", "ldloc.2", "stfld System.Reflection.MethodBase AutomaticSAR.PlayerCommandPatch/<TargetMethods>d__0::<>2__current");
        var next = (Instruction)speed[4].Operand;
        AutomaticSARFind(method, "ldarg.0", "ldarg.0",
            "ldfld System.Int32 AutomaticSAR.PlayerCommandPatch/<TargetMethods>d__0::<>7__wrap2", "ldc.i4.1", "add",
            "stfld System.Int32 AutomaticSAR.PlayerCommandPatch/<TargetMethods>d__0::<>7__wrap2");
        if (next.Offset != 0x00e0 || AutomaticSARText(next) != "ldarg.0" ||
            AutomaticSARText(next.Next.Next) != "ldfld System.Int32 AutomaticSAR.PlayerCommandPatch/<TargetMethods>d__0::<>7__wrap2" ||
            method.Body.Instructions.Any(i => i.Operand == start[2] || (i.Operand is Instruction[] targets && targets.Contains(start[2]))))
            throw new InvalidOperationException("Inspected AutomaticSAR TargetMethods loop changed");
        // The plugin's own netstandard TypeRef, so no new corlib reference is added.
        var methodBase = scope.Module.GetTypeReferences().SingleOrDefault(t => t.FullName == "System.Reflection.MethodBase")
            ?? throw new InvalidOperationException("Inspected AutomaticSAR MethodBase reference changed");
        var isDefinition = new MethodReference("get_IsGenericMethodDefinition", scope.Module.TypeSystem.Boolean, methodBase) { HasThis = true };
        scope.ExpandBranches(method);
        var il = method.Body.GetILProcessor();
        il.InsertBefore(start[2], Instruction.Create(OpCodes.Ldloc_2));
        il.InsertBefore(start[2], Instruction.Create(OpCodes.Callvirt, isDefinition));
        il.InsertBefore(start[2], Instruction.Create(OpCodes.Brtrue, next));
        scope.Count("generic-filter");
    }

    // lerp-body: stable InterpolateGeoPosition offset the start by t times the
    // flat distance along the flat bearing, i.e. a straight lat/lon line. The
    // beta mixes a projected distance with a great-circle offset, which leaves
    // the 0.1 nm route-depth samples off the route on east-west legs.
    private static void AutomaticSARInterpolate(AdapterScope scope, MethodDefinition method)
    {
        if (!AutomaticSARIs(method, "InterpolateGeoPosition", true, "SeaPower.GeoPosition", "SeaPower.GeoPosition", "SeaPower.GeoPosition", "System.Single") ||
            method.Body.Variables.Count != 1 || method.Body.Variables[0].VariableType.FullName != "System.Single" ||
            method.Body.ExceptionHandlers.Count != 0 || method.Body.Instructions.Count != 15)
            throw new InvalidOperationException("Inspected AutomaticSAR InterpolateGeoPosition changed");
        AutomaticSARFind(method, "ldarg.0", "ldarg.1",
            "call System.Single AutomaticSAR.RescueCoordinator::DistanceBetweenGeoPositions(SeaPower.GeoPosition,SeaPower.GeoPosition)",
            "ldc.r4 1852", "div", "stloc.0", "ldarga.s A0", "ldloc.0", "ldarg.2", "mul", "ldarga.s A0", "ldarg.1",
            "call System.Single SeaPower.GeoPosition::CourseTo(SeaPower.GeoPosition)",
            "call SeaPower.GeoPosition SeaPower.GeoPosition::GeoOffsetByDistanceOnHeading(System.Single,System.Single)", "ret");
        method.Body.Instructions.Clear(); method.Body.Variables.Clear();
        var il = method.Body.GetILProcessor();
        il.Append(Instruction.Create(OpCodes.Ldarg_0)); il.Append(Instruction.Create(OpCodes.Ldarg_1)); il.Append(Instruction.Create(OpCodes.Ldarg_2));
        il.Append(Instruction.Create(OpCodes.Call, scope.Bridge(nameof(BetaCompatibilityCalls.AutomaticSARInterpolateGeoPosition))));
        il.Append(Instruction.Create(OpCodes.Ret));
        scope.Count("lerp-body");
    }

    // bearings: the helicopter waypoint 0.5 nm beyond the raft uses the beta
    // bearing that matches the beta's own GeoOffsetByDistanceOnHeading.
    private static void AutomaticSAROvershoot(AdapterScope scope, MethodDefinition method)
    {
        if (!AutomaticSARIs(method, "GetHelicopterOvershootWaypoint", true, "SeaPower.GeoPosition", "SeaPower.ObjectBase", "SeaPower.ObjectBase"))
            throw new InvalidOperationException("Inspected AutomaticSAR GetHelicopterOvershootWaypoint changed");
        var site = AutomaticSARFind(method, "ldc.r4 0.5", "ldarg.0", "callvirt SeaPower.GeoPosition SeaPower.ObjectBase::getGeoPosition()",
            "stloc.1", "ldloca.s V1", "ldloc.0", "call System.Single SeaPower.GeoPosition::CourseTo(SeaPower.GeoPosition)",
            "call SeaPower.GeoPosition SeaPower.GeoPosition::GeoOffsetByDistanceOnHeading(System.Single,System.Single)", "ret");
        var heading = scope.Native.GetType("SeaPower.GeoPosition").Methods.Single(m => m.Name == "HeadingToPosition" &&
            !m.IsStatic && m.ReturnType.FullName == "System.Single" && ParameterTypes(m, "SeaPower.GeoPosition"));
        site[6].Operand = scope.Module.ImportReference(heading);
        scope.Count("bearings");
    }

    // Ships get the native knots request (the request SetSpeedCommand<ConstantSpeed>
    // builds); submarines keep the author's uncapped SarConstantSpeed.
    private static void AutomaticSARRescueSpeed(AdapterScope scope, MethodDefinition method)
    {
        if (!AutomaticSARIs(method, "SetRescueSpeed", true, "System.Void", "SeaPower.ObjectBase", "System.Single"))
            throw new InvalidOperationException("Inspected AutomaticSAR SetRescueSpeed changed");
        var site = AutomaticSARFind(method, "isinst SeaPower.Submarine", "brfalse.s IL_0056", "ldarg.0", "ldloc.0",
            "newobj System.Void AutomaticSAR.RescueCoordinator/SarConstantSpeed::.ctor(System.Single)",
            "callvirt " + AutomaticSARStableSet, "ret", "ldarg.0", "ldloc.0", "ldarg.0",
            "newobj System.Void SeaPower.ConstantSpeed::.ctor(System.Single,SeaPower.ObjectBase)", "callvirt " + AutomaticSARStableSet, "ret");
        AutomaticSARCall(site[5], scope.Bridge(nameof(BetaCompatibilityCalls.AutomaticSARSetCustomSpeedCommand))); scope.Count("sub-speed");
        AutomaticSARCall(site[10], scope.Bridge(nameof(BetaCompatibilityCalls.ConstantSpeedRequest))); scope.Count("speed-make");
        AutomaticSARCall(site[11], scope.Bridge(nameof(BetaCompatibilityCalls.SetSpeedRequest))); scope.Count("speed-set");
    }

    // VTOL speed steps: 'current command as ConstantSpeed/ConstantMach' becomes
    // a SpeedKind test on the current ISpeedCommand, read through the interface.
    private static void AutomaticSARVtolSpeed(AdapterScope scope, MethodDefinition method, bool mach)
    {
        string order = mach ? "SeaPower.ConstantMach" : "SeaPower.ConstantSpeed";
        if (!(mach ? AutomaticSARIs(method, "SetVtolMachSpeed", true, "System.Void", "SeaPower.Aircraft", "System.Int32")
                   : AutomaticSARIs(method, "SetVtolKnotSpeed", true, "System.Void", "SeaPower.Aircraft", "System.Single")))
            throw new InvalidOperationException("Inspected AutomaticSAR " + method.Name + " changed");
        int slot = mach ? 2 : 0;
        string local = mach ? "2" : "0", value = mach ? "ldloc.1" : "ldarg.1";
        var test = AutomaticSARFind(method, AutomaticSARValue, "isinst " + order, "stloc." + local, "ldloc." + local,
            mach ? "brfalse.s IL_0076" : "brfalse.s IL_0039", "ldloc." + local,
            mach ? "callvirt System.Single SeaPower.ConstantMach::get_SpeedInMach()" : "callvirt System.Single SeaPower.ConstantSpeed::get_SpeedInKnots()",
            value, "sub", "call System.Single UnityEngine.Mathf::Abs(System.Single)");
        var make = AutomaticSARFind(method, "ldarg.0", value, "ldarg.0",
            "newobj System.Void " + order + "::.ctor(System.Single,SeaPower.ObjectBase)", "callvirt " + AutomaticSARStableSet, "ret");
        var variable = method.Body.Variables[slot];
        if (variable.VariableType.FullName != order || method.Body.Variables.Count(v => v.VariableType.FullName == order) != 1)
            throw new InvalidOperationException("Inspected AutomaticSAR " + method.Name + " locals changed");
        var command = scope.Module.ImportReference(scope.Native.GetType("SeaPower.ISpeedCommand"));
        variable.VariableType = command; scope.Count("local-retype");
        AutomaticSARCall(test[1], scope.Bridge(mach ? nameof(BetaCompatibilityCalls.AutomaticSARConstantMachCommand)
            : nameof(BetaCompatibilityCalls.AutomaticSARConstantKnotsCommand))); scope.Count("speed-kind");
        string getter = mach ? "get_SpeedInMach" : "get_SpeedInKnots";
        test[6].Operand = scope.Module.ImportReference(scope.Native.GetType("SeaPower.ISpeedCommand").Methods.Single(m => m.Name == getter));
        scope.Count("speed-read");
        if (mach) { AutomaticSARCall(make[3], scope.Bridge(nameof(BetaCompatibilityCalls.AutomaticSARMachRequest))); scope.Count("mach-make"); }
        else { AutomaticSARCall(make[3], scope.Bridge(nameof(BetaCompatibilityCalls.ConstantSpeedRequest))); scope.Count("speed-make"); }
        AutomaticSARCall(make[4], scope.Bridge(nameof(BetaCompatibilityCalls.SetSpeedRequest))); scope.Count("speed-set");
    }

    private static void AutomaticSARCall(Instruction instruction, MethodReference bridge)
    {
        instruction.OpCode = OpCodes.Call; instruction.Operand = bridge;
    }

    // ui-forwarder: every beta UI speed order calls the generic forwarder
    // ObjectBase.SetSpeedCommand<T>, which calls the patched concrete overload.
    // The author's stack walk takes the frame after the patched one as the
    // caller, so the forwarder ('SeaPower.') would hide the SeapowerUI caller
    // and a player's speed order would no longer cancel SAR. Skip that frame.
    private static void AutomaticSARSkipForwarder(AdapterScope scope, MethodDefinition method)
    {
        if (!AutomaticSARIs(method, "WasCalledDirectlyFromGameUi", true, "System.Boolean") || method.Body.Variables.Count != 6 ||
            method.Body.Variables[2].VariableType.FullName != "System.Diagnostics.StackFrame[]" ||
            method.Body.Variables[3].VariableType.FullName != "System.Int32" || method.Body.Variables[5].VariableType.FullName != "System.String")
            throw new InvalidOperationException("Inspected AutomaticSAR WasCalledDirectlyFromGameUi changed");
        var found = AutomaticSARFind(method, "stloc.s V5", "ldloc.1", "brtrue.s IL_00b3", "ldloc.s V5", "ldtoken SeaPower.ObjectBase");
        var head = AutomaticSARFind(method, "br.s IL_00e6", "ldloc.s V5", "ldstr \"AutomaticSAR.\"", "ldc.i4.4",
            "callvirt System.Boolean System.String::StartsWith(System.String,System.StringComparison)")[1];
        var next = AutomaticSARFind(method, "ldloc.3", "ldc.i4.1", "add", "stloc.3", "ldloc.3", "ldloc.2", "ldlen", "conv.i4", "blt IL_001b")[0];
        if (found[2].Operand != head || head.Offset != 0x00b3 || next.Offset != 0x00e6 ||
            method.Body.Instructions.Count(i => i.Operand == head) != 1)
            throw new InvalidOperationException("Inspected AutomaticSAR WasCalledDirectlyFromGameUi branch changed");
        scope.ExpandBranches(method);
        var name = (VariableDefinition)head.Operand;
        // Keep the branch target object: it now loads the frame array first.
        head.OpCode = OpCodes.Ldloc_2; head.Operand = null;
        var il = method.Body.GetILProcessor(); var previous = head;
        foreach (var added in new[] { Instruction.Create(OpCodes.Ldloc_3), Instruction.Create(OpCodes.Ldelem_Ref),
            Instruction.Create(OpCodes.Call, scope.Bridge(nameof(BetaCompatibilityCalls.AutomaticSARIsGenericSpeedForwarder))),
            Instruction.Create(OpCodes.Brtrue, next), Instruction.Create(OpCodes.Ldloc_S, name) }) {
            il.InsertAfter(previous, added); previous = added;
        }
        scope.Count("ui-forwarder");
    }

    // speed-interface: the beta ISpeedCommand adds Kind and Telegraph. The
    // author's SarConstantSpeed is a constant-knots command, so it reports
    // what the beta SpeedState reports for SpeedRequest.Knots: Constant, step 0.
    private static void AutomaticSARFinish(AdapterScope scope)
    {
        var command = scope.Module.GetType("AutomaticSAR.RescueCoordinator").NestedTypes.SingleOrDefault(t => t.FullName == AutomaticSARCommand);
        var names = new[] { ".ctor", "get_AvoidingCavitation", "get_CommandSpeedInKnots", "get_SpeedInKnots", "get_SpeedInMach", "get_MachLimit",
            "get_SpeedIsOverriden", "get_OverridenSpeedInKnots", "GetDemandedSpeedInKnots", "GetDemandedSpeedInMetresPerSecond", "Update",
            "OverrideSpeed", "CancelSpeedOverride" };
        if (command == null || command.IsValueType || command.Interfaces.Count != 1 || command.Interfaces[0].InterfaceType.FullName != "SeaPower.ISpeedCommand" ||
            !command.Methods.Select(m => m.Name).SequenceEqual(names))
            throw new InvalidOperationException("Inspected AutomaticSAR SarConstantSpeed changed");
        const MethodAttributes attributes = MethodAttributes.Public | MethodAttributes.HideBySig | MethodAttributes.SpecialName |
            MethodAttributes.NewSlot | MethodAttributes.Virtual | MethodAttributes.Final;
        var kind = new MethodDefinition("get_Kind", attributes, scope.Module.ImportReference(scope.Native.GetType("SeaPower.SpeedKind")));
        kind.Body.GetILProcessor().Append(Instruction.Create(OpCodes.Ldc_I4_3));   // SpeedKind.Constant
        kind.Body.GetILProcessor().Append(Instruction.Create(OpCodes.Ret));
        var step = new MethodDefinition("get_Telegraph", attributes, scope.Module.TypeSystem.Int32);
        step.Body.GetILProcessor().Append(Instruction.Create(OpCodes.Ldc_I4_0));   // SpeedRequest.Knots(...).Step
        step.Body.GetILProcessor().Append(Instruction.Create(OpCodes.Ret));
        command.Methods.Add(kind); scope.Count("speed-interface");
        command.Methods.Add(step); scope.Count("speed-interface");
    }
}
