using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Runtime.Serialization;
using AnchorChain;
using HarmonyLib;
using Mono.Cecil;
using SeaPower;

static partial class BetaApiTests
{
    const BindingFlags InteropAll = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance;

    // J-36 systems (0d4e89cc) on 0.9.3-261123: the high-speed drag and vector
    // flight patches find the aircraft parameters and drag power again, through
    // the native property and _perf.DragPower; nothing else changes.
    static void R6_J36Systems(R6Context context)
    {
        string source = Path.Combine(context.Workshop, "3801549552", "J36AfterburnerNozzle.dll");
        string prepared = InteropPrepared(context, source, "0d4e89ccf8ac4c81038f624af9ee50dfa9d0befd573d89fc7c42e98fdeb6a4d7",
            "J36AfterburnerNozzle", "J36SystemsAudit");
        if (prepared == null) return;
        Check(typeof(FixedWingFlightPhysics).GetField("_aircraftParameters", InteropAll) == null &&
            typeof(FixedWingFlightPhysics).GetProperty("_aircraftParameters", InteropAll)?.PropertyType == typeof(AircraftParameters) &&
            typeof(FixedWingFlightPhysics).GetField("_dragPower", InteropAll) == null &&
            typeof(FixedWingFlightPhysics).GetField("_perf", InteropAll)?.FieldType == typeof(AircraftPerfData),
            "On 261123 _aircraftParameters is a property, _dragPower is gone and drag power lives in _perf");
        const string Drag = "J36AfterburnerNozzle.J36HighSpeedDragPatch", Vector = "J36AfterburnerNozzle.J36VectorFlightPhysicsPatch";
        using (var author = ModuleDefinition.ReadModule(source, new ReaderParameters { AssemblyResolver = context.Resolver }))
        using (var adapted = ModuleDefinition.ReadModule(prepared, new ReaderParameters { AssemblyResolver = context.Resolver })) {
            var changed = InteropChangedMethods(author, adapted, "J-36");
            var expected = new[] { "J36HighSpeedDragPatch::Postfix", "J36HighSpeedDragPatch::Prefix", "J36VectorFlightPhysicsPatch::Prefix" }
                .Concat(InteropLocationMethods(adapted)).Distinct().OrderBy(x => x, StringComparer.Ordinal).ToList();
            Check(changed.SequenceEqual(expected), "Only the two FixedWingFlightPhysics patch bodies and the location reads differ (actual: " + string.Join(", ", changed) + ")");
            Check(InteropLocationMethods(adapted).Count() == 2, "Both J-36 Assembly.Location reads keep the Workshop path");
            int Bridged(string type, string method, string bridge) => adapted.GetType(type).Methods.Single(m => m.Name == method).Body.Instructions
                .Count(i => i.OpCode == Mono.Cecil.Cil.OpCodes.Call && i.Operand is MethodReference c && c.Name == bridge && c.DeclaringType.FullName == typeof(BetaCompatibilityCalls).FullName);
            Check(Bridged(Drag, "Prefix", "FixedWingParameters") == 1 && Bridged(Drag, "Prefix", "FixedWingDragPower") == 1 &&
                Bridged(Drag, "Prefix", "SetFixedWingDragPower") == 1 && Bridged(Drag, "Postfix", "SetFixedWingDragPower") == 1 &&
                Bridged(Vector, "Prefix", "FixedWingParameters") == 1,
                "Each read and write through the missing lookups calls its SEST bridge");
            foreach (var (type, method) in new[] { (Drag, "Prefix"), (Drag, "Postfix"), (Vector, "Prefix") }) {
                var body = adapted.GetType(type).Methods.Single(m => m.Name == method).Body.Instructions;
                Check(!body.Any(i => i.Operand is FieldReference f && (f.Name == "AircraftParametersField" || f.Name == "DragPowerField")) &&
                    !body.Any(i => i.Operand is MethodReference c && c.DeclaringType.FullName == "System.Reflection.FieldInfo" &&
                        ((type == Drag && c.Name == "SetValue") || (c.Name == "GetValue" && c.Parameters.Count == 1 && i.Previous.OpCode == Mono.Cecil.Cil.OpCodes.Ldarg_0 &&
                            i.Previous.Previous.OpCode == Mono.Cecil.Cil.OpCodes.Nop))) &&
                    body.Count(i => i.OpCode == Mono.Cecil.Cil.OpCodes.Ldc_I4_0 && i.Next.OpCode == Mono.Cecil.Cil.OpCodes.Nop && i.Next.Next.OpCode == Mono.Cecil.Cil.OpCodes.Nop) ==
                        (type == Drag && method == "Prefix" ? 2 : 1),
                    "The null guards on the two lookups are constant false and nothing reads them: " + type + "::" + method);
            }
            // The guard on the author's own Velocity lookup is kept as written.
            Check(adapted.GetType(Drag).Methods.Single(m => m.Name == "Prefix").Body.Instructions.Count(i => i.Operand is FieldReference f && f.Name == "VelocityProperty") == 2,
                "The Velocity lookup and its guard are the author's");
        }
        var assembly = Assembly.LoadFile(prepared);
        Check(BetaAssemblyPolicy.OriginalLocation(assembly) == source, "J-36 original asset provenance retained");
        Type drag = assembly.GetType(Drag, true), vector = assembly.GetType(Vector, true);
        foreach (var method in new[] { drag.GetMethod("Prefix", InteropAll), drag.GetMethod("Postfix", InteropAll), vector.GetMethod("Prefix", InteropAll) }) {
            RuntimeHelpers.PrepareMethod(method.MethodHandle);
            Check(true, "Rewritten J-36 method compiles on 261123: " + method.DeclaringType.Name + "::" + method.Name);
        }
        // The author's own lookups on 261123: the two retired ones stay null and
        // are no longer consulted; the others bind.
        RuntimeHelpers.RunClassConstructor(drag.TypeHandle); RuntimeHelpers.RunClassConstructor(vector.TypeHandle);
        object Static(Type type, string name) => type.GetField(name, InteropAll).GetValue(null);
        Check(Static(drag, "AircraftParametersField") == null && Static(drag, "DragPowerField") == null && Static(vector, "AircraftParametersField") == null,
            "The retired lookups still find nothing on 261123");
        Check(Static(drag, "VelocityProperty") != null && Static(vector, "TurnSpeedField") != null && Static(drag, "PhysicsType") == typeof(FixedWingFlightPhysics),
            "The author's Velocity and turnSpeed lookups bind on 261123, so both patches now run");
        // The bridges against a game physics object (no Unity player: built
        // without its constructor, its fields set directly).
        InteropWithoutUnityProfiler();
        var physics = (FixedWingFlightPhysics)FormatterServices.GetUninitializedObject(typeof(FixedWingFlightPhysics));
        var parameters = (AircraftParameters)FormatterServices.GetUninitializedObject(typeof(AircraftParameters));
        typeof(MotionController).GetField("_ap", InteropAll).SetValue(physics, parameters);
        Check(ReferenceEquals(BetaCompatibilityCalls.FixedWingParameters(physics), parameters), "FixedWingParameters returns the native _aircraftParameters property");
        var perf = typeof(FixedWingFlightPhysics).GetField("_perf", InteropAll);
        var data = (AircraftPerfData)perf.GetValue(physics); data.DragPower = 1.25f; data.VsRef = 7f; perf.SetValue(physics, data);
        Check(Equals(BetaCompatibilityCalls.FixedWingDragPower(physics), 1.25f), "FixedWingDragPower reads _perf.DragPower, boxed");
        BetaCompatibilityCalls.SetFixedWingDragPower(physics, 2.5f);
        data = (AircraftPerfData)perf.GetValue(physics);
        Check(data.DragPower == 2.5f && data.VsRef == 7f, "SetFixedWingDragPower writes only _perf.DragPower in place");
        // The rewritten postfix, as the author wrote it, restores the drag power its prefix scaled.
        var states = drag.GetField("States", InteropAll).GetValue(null);
        var state = states.GetType().GetMethod("GetOrCreateValue").Invoke(states, new object[] { physics });
        state.GetType().GetField("OriginalDragPower", InteropAll).SetValue(state, 0.75f);
        state.GetType().GetField("Modified", InteropAll).SetValue(state, true);
        drag.GetMethod("Postfix", InteropAll).Invoke(null, new object[] { physics });
        Check(((AircraftPerfData)perf.GetValue(physics)).DragPower == 0.75f && !(bool)state.GetType().GetField("Modified", InteropAll).GetValue(state),
            "The adapted high-speed drag postfix restores _perf.DragPower and clears its mark");
        // The adapted prefix leaves a non-J-36 aircraft alone.
        var settings = assembly.GetType("J36AfterburnerNozzle.PluginSettings", true);
        var flag = settings.GetField("<HighSpeedDrag>k__BackingField", InteropAll); object was = flag.GetValue(null);
        try {
            flag.SetValue(null, true);
            var other = (FixedWingFlightPhysics)FormatterServices.GetUninitializedObject(typeof(FixedWingFlightPhysics));
            typeof(MotionController).GetField("_ap", InteropAll).SetValue(other, parameters);
            drag.GetMethod("Prefix", InteropAll).Invoke(null, new object[] { other });
            object tried = states.GetType().GetMethod("TryGetValue").Invoke(states, new object[] { other, null });
            Check(!(bool)tried && ((AircraftPerfData)perf.GetValue(other)).DragPower == 0f, "The adapted high-speed drag prefix leaves other aircraft untouched");
        } finally { flag.SetValue(null, was); }
        var ini = typeof(AircraftParameters).GetField("_objectIniName", InteropAll);
        if (ini != null && ini.FieldType == typeof(string)) {
            ini.SetValue(parameters, "plaaf_j36");
            Check((bool)assembly.GetType("J36AfterburnerNozzle.J36Scope", true).GetMethod("IsJ36Parameters", InteropAll)
                .Invoke(null, new[] { BetaCompatibilityCalls.FixedWingParameters(physics) }), "The author's J-36 check recognises the parameters the bridge returns");
        }
        InteropRejects(source, context, "J36SystemsAdapter", Drag, "Postfix",
            method => method.Body.Instructions.First(i => i.Operand is FieldReference f && f.Name == "DragPowerField").Next.OpCode = Mono.Cecil.Cil.OpCodes.Ldarg_1,
            "J-36 drag lookup used in an uninspected way");
        InteropRejects(source, context, "J36SystemsAdapter", Drag, "HasTransform",
            method => {
                var il = method.Body.GetILProcessor(); var first = method.Body.Instructions[0];
                il.InsertBefore(first, il.Create(Mono.Cecil.Cil.OpCodes.Ldsfld, method.DeclaringType.Fields.Single(f => f.Name == "AircraftParametersField")));
                il.InsertBefore(first, il.Create(Mono.Cecil.Cil.OpCodes.Pop));
            },
            "J-36 fixed-wing lookup read outside the inspected patch bodies");
    }

    // Game types such as FixedWingFlightPhysics create a Unity ProfilerMarker
    // in their static constructors. Its constructor needs the Unity player's
    // corlib (ReadOnlySpan.GetPinnableReference), which this test process does
    // not have. Here it builds an empty marker instead; nothing is profiled.
    static Harmony interopProfiler;
    static void InteropWithoutUnityProfiler()
    {
        if (interopProfiler != null) return;
        var ctor = typeof(Unity.Profiling.ProfilerMarker).GetConstructor(new[] { typeof(string) });
        Check(ctor != null && ctor.DeclaringType.Assembly.GetName().Name == "UnityEngine.CoreModule", "Unity ProfilerMarker(string) is the engine's");
        interopProfiler = new Harmony("sest.beta-api-tests.no-profiler");
        interopProfiler.Patch(ctor, transpiler: new HarmonyMethod(typeof(BetaApiTests).GetMethod(nameof(InteropEmptyBody), InteropAll)));
    }
    static IEnumerable<CodeInstruction> InteropEmptyBody(IEnumerable<CodeInstruction> instructions) => new[] { new CodeInstruction(System.Reflection.Emit.OpCodes.Ret) };

    // Prepare an exact author image and check its private image and its one log line.
    static string InteropPrepared(R6Context context, string source, string expected, string name, string auditField)
    {
        byte[] original = File.ReadAllBytes(source);
        string hash; using (var sha = System.Security.Cryptography.SHA256.Create()) hash = BitConverter.ToString(sha.ComputeHash(original)).Replace("-", "").ToLowerInvariant();
        Check(hash == expected, name + " fixture is the inspected author image");
        var messages = new List<string>();
        string prepared = BetaAssemblyPolicy.Prepare(source, context.Native, context.Cache, messages.Add);
        string audit = (string)typeof(BetaAssemblyPolicy).GetField(auditField, InteropAll).GetValue(null);
        Check(prepared != null && prepared != source && File.Exists(prepared), name + " is admitted through its 261123 adapter: " + string.Join(" | ", messages));
        Check(original.SequenceEqual(File.ReadAllBytes(source)), "Original " + name + " DLL retained byte for byte");
        Check(messages.Count == 1 && messages[0] == "ADAPTED " + name + " in private cache: " + audit + "; original Workshop DLL and asset paths preserved.",
            name + " logs one line with the inspected audit (" + audit + "): " + string.Join(" | ", messages));
        Console.WriteLine(messages.FirstOrDefault());
        using (var module = ModuleDefinition.ReadModule(prepared, new ReaderParameters { AssemblyResolver = context.Resolver }))
            Check(InteropMissingOperands(module) == 0, name + ": every native operand of the adapted image resolves on 261123");
        return prepared == source ? null : prepared;
    }

    static int InteropMissingOperands(ModuleDefinition module)
    {
        int missing = 0;
        foreach (var method in Types(module.Types).SelectMany(t => t.Methods).Where(m => m.HasBody))
            foreach (var instruction in method.Body.Instructions) {
                var member = instruction.Operand as MemberReference;
                if (member?.DeclaringType?.Scope is not AssemblyNameReference scope || scope.Name != "Seapower-Scripts") continue;
                try { if ((member is MethodReference call ? (object)call.Resolve() : member is FieldReference field ? field.Resolve() : member) == null) missing++; }
                catch (Exception) { missing++; }
            }
        return missing;
    }

    // The author's types and methods, in order; the names of the bodies that differ.
    static List<string> InteropChangedMethods(ModuleDefinition author, ModuleDefinition adapted, string name)
    {
        var authorTypes = Types(author.Types).ToList(); var adaptedTypes = Types(adapted.Types).ToList();
        Check(authorTypes.Select(t => t.FullName).SequenceEqual(adaptedTypes.Select(t => t.FullName)), "Adapted " + name + " image has the author's types");
        var changed = new List<string>();
        for (int t = 0; t < authorTypes.Count; t++) {
            Check(authorTypes[t].Methods.Select(m => m.FullName).SequenceEqual(adaptedTypes[t].Methods.Select(m => m.FullName)),
                "Adapted " + name + " type has the author's methods: " + authorTypes[t].FullName);
            for (int m = 0; m < authorTypes[t].Methods.Count; m++) {
                var written = authorTypes[t].Methods[m]; var actual = adaptedTypes[t].Methods[m];
                if (written.HasBody && !TopoInstructions(written).SequenceEqual(TopoInstructions(actual))) changed.Add(actual.DeclaringType.Name + "::" + actual.Name);
            }
        }
        changed.Sort(StringComparer.Ordinal);
        return changed;
    }

    static IEnumerable<string> InteropLocationMethods(ModuleDefinition adapted)
        => Types(adapted.Types).SelectMany(t => t.Methods).Where(m => m.HasBody && m.Body.Instructions.Any(i =>
            i.Operand is MethodReference c && c.Name == "OriginalLocation" && c.DeclaringType.FullName == typeof(BetaAssemblyPolicy).FullName))
            .Select(m => m.DeclaringType.Name + "::" + m.Name);

    // The adapter refuses an author shape it was not written for, before load.
    static void InteropRejects(string source, R6Context context, string factory, string typeName, string methodName,
        Action<MethodDefinition> mutate, string why)
    {
        object adapter = typeof(BetaAssemblyPolicy).GetMethod(factory, InteropAll).Invoke(null, null);
        var rewriteMethod = (Delegate)adapter.GetType().GetField("RewriteMethod", InteropAll).GetValue(adapter);
        var rewriteCall = (Delegate)adapter.GetType().GetField("RewriteCall", InteropAll).GetValue(adapter);
        Type scopeType = (rewriteMethod ?? rewriteCall).Method.GetParameters()[0].ParameterType;
        using var module = ModuleDefinition.ReadModule(source, new ReaderParameters { AssemblyResolver = context.Resolver });
        using var native = ModuleDefinition.ReadModule(context.Native);
        var method = module.GetType(typeName).Methods.First(m => m.HasBody && m.Name == methodName);
        mutate(method);
        object scope = Activator.CreateInstance(scopeType, true);
        scopeType.GetField("Module", InteropAll).SetValue(scope, module);
        scopeType.GetField("Native", InteropAll).SetValue(scope, native);
        scopeType.GetField("Count", InteropAll).SetValue(scope, (Action<string>)(_ => {}));
        bool rejected = false;
        try {
            rewriteMethod?.DynamicInvoke(scope, method.DeclaringType, method);
            if (rewriteCall != null)
                foreach (var instruction in method.Body.Instructions.ToArray())
                    if (instruction.Operand is MethodReference call) rewriteCall.DynamicInvoke(scope, method.DeclaringType, method, instruction, call);
        }
        catch (TargetInvocationException ex) when (ex.InnerException is InvalidOperationException) { rejected = true; }
        Check(rejected, "Changed author shape is rejected before load: " + why);
    }
}
