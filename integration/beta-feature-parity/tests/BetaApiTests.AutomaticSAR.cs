using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using AnchorChain;
using HarmonyLib;
using Mono.Cecil;
using SeaPower;

// R6: Automatic SAR (Workshop 3774105087) on beta Build 261106. Metadata,
// reflection and bridge checks only: no Harmony patch is applied, no plugin
// entry point runs, and no Unity gameplay is needed.
static partial class BetaApiTests
{
    const string AutomaticSARHash = "bcd193256a8078652bacb4a0055d713fc0e7b0c1fe0d76d5152acf733b937361";
    const string AutomaticSARAudit = "bearings=1, generic-filter=1, lerp-body=1, local-retype=2, mach-make=1, speed-interface=2, " +
        "speed-kind=2, speed-make=2, speed-read=2, speed-set=3, sub-speed=1, terrain-height=5, ui-forwarder=1";
    const string AutomaticSARBridge = "AnchorChain.BetaCompatibilityCalls";

    sealed class AutomaticSARSpeedStub : ISpeedCommand
    {
        public SpeedKind Kind { get; set; }
        public int Telegraph => 0;
        public bool AvoidingCavitation => false;
        public float CommandSpeedInKnots => 0;
        public float SpeedInKnots => 0;
        public float SpeedInMach => 0;
        public float MachLimit => 0;
        public bool SpeedIsOverriden => false;
        public float OverridenSpeedInKnots => 0;
        public float GetDemandedSpeedInKnots(ObjectBase unit) => 0;
        public float GetDemandedSpeedInMetresPerSecond(ObjectBase unit) => 0;
        public void Update(ObjectBase unit) { }
        public void OverrideSpeed(float speed) { }
        public void CancelSpeedOverride() { }
    }

    // A decoy with the forwarder's name and shape on another type.
    sealed class AutomaticSARDecoy { public void SetSpeedCommand<T>(ref T order) { } }

    static string AutomaticSARText(Mono.Cecil.Cil.Instruction instruction, IList<Mono.Cecil.Cil.Instruction> body)
    {
        object operand = instruction.Operand;
        string name = instruction.OpCode.Name;
        // The loader widens every short branch; compare branches by target index.
        if (operand is Mono.Cecil.Cil.Instruction || operand is Mono.Cecil.Cil.Instruction[]) name = name.EndsWith(".s") ? name.Substring(0, name.Length - 2) : name;
        string text = operand switch {
            null => "",
            Mono.Cecil.Cil.Instruction target => " #" + body.IndexOf(target),
            Mono.Cecil.Cil.Instruction[] targets => " (" + String.Join(",", targets.Select(t => "#" + body.IndexOf(t))) + ")",
            MemberReference member => " " + member.FullName,
            Mono.Cecil.Cil.VariableDefinition variable => " V" + variable.Index,
            ParameterDefinition parameter => " A" + parameter.Index,
            string literal => " \"" + literal + "\"",
            _ => " " + Convert.ToString(operand, CultureInfo.InvariantCulture),
        };
        return name + text;
    }

    static List<string> AutomaticSARTexts(MethodDefinition method)
        => method.Body.Instructions.Select(i => AutomaticSARText(i, method.Body.Instructions)).ToList();

    // A run of instruction texts, found exactly once in the method.
    static int AutomaticSARRun(MethodDefinition method, params string[] texts)
    {
        var all = AutomaticSARTexts(method); var hits = new List<int>();
        for (int i = 0; i + texts.Length <= all.Count; i++)
            if (texts.Select((t, k) => all[i + k] == t).All(x => x)) hits.Add(i);
        return hits.Count == 1 ? hits[0] : -1;
    }

    // Class/value-type encoding of every Seapower-Scripts type in a signature.
    static void AutomaticSAREncoding(TypeReference type, string where, List<string> errors)
    {
        if (type == null) return;
        if (type is GenericInstanceType generic) { foreach (var argument in generic.GenericArguments) AutomaticSAREncoding(argument, where, errors); AutomaticSAREncoding(generic.ElementType, where, errors); return; }
        if (type is TypeSpecification specification) { AutomaticSAREncoding(specification.ElementType, where, errors); return; }
        if (type is GenericParameter || type.Scope is not AssemblyNameReference scope || scope.Name != "Seapower-Scripts") return;
        var definition = type.Resolve();
        if (definition == null) errors.Add(where + ": unresolved " + type.FullName);
        else if (definition.IsValueType != type.IsValueType) errors.Add(where + ": " + type.FullName + " encoded as " + (type.IsValueType ? "value" : "class"));
    }

    static GeoPosition AutomaticSARStableInterpolate(GeoPosition a, GeoPosition b, float t)
    {
        // Stable 261021: HeadingRangeMeters(b).Item2 (flat Vector2 of
        // (lon, lat) times 111120.000000012), CourseTo (atan2 of -(a-b)),
        // GeoOffsetByDistanceOnHeading (d/60 on a flat lat/lon plane).
        float x = (float)a.Longitude - (float)b.Longitude, y = (float)a.Latitude - (float)b.Latitude;
        float meters = (float)((double)(float)Math.Sqrt(x * x + y * y) * 111120.000000012);
        float distance = meters / 1852f * t;
        float course = (float)Math.Atan2(-(a.Longitude - b.Longitude), -(a.Latitude - b.Latitude)) * 180f / 3.1415927f;
        double dLon = distance * 0.016666666666666666 * Math.Sin(course * 0.017453292519943295);
        double dLat = distance * 0.016666666666666666 * Math.Cos(course * 0.017453292519943295);
        return new GeoPosition(a.Latitude + dLat, a.Longitude + dLon, a._height);
    }

    static void R6_AutomaticSAR(R6Context context)
    {
        const BindingFlags all = BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static | BindingFlags.Instance;
        string source = Path.Combine(context.Workshop, "3774105087", "AutomaticSAR.dll");
        byte[] bytes = File.ReadAllBytes(source);
        using (var sha = SHA256.Create())
            Check(BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant() == AutomaticSARHash, "AutomaticSAR fixture is the pinned 3 Nov image");
        var log = new List<string>();
        string adapted = BetaAssemblyPolicy.Prepare(source, context.Native, context.Cache, log.Add);
        foreach (string line in log) Console.WriteLine(line);
        Check(adapted != null && adapted != source && File.Exists(adapted), "AutomaticSAR private image generated");
        Check(bytes.SequenceEqual(File.ReadAllBytes(source)), "AutomaticSAR author bytes retained");
        Check(log.Count == 1 && log[0] == "ADAPTED AutomaticSAR in private cache: " + AutomaticSARAudit + "; original Workshop DLL and asset paths preserved.",
            "AutomaticSAR adaptation logs its exact audit");

        using var author = ModuleDefinition.ReadModule(source, new ReaderParameters { AssemblyResolver = context.Resolver });
        using var module = ModuleDefinition.ReadModule(adapted, new ReaderParameters { AssemblyResolver = context.Resolver });
        var methods = Types(module.Types).SelectMany(t => t.Methods).Where(m => m.HasBody).ToList();

        // Every Seapower-Scripts method and field operand resolves on the beta.
        var missing = new List<string>(); int resolved = 0;
        foreach (var method in methods) foreach (var instruction in method.Body.Instructions) {
            var member = instruction.Operand as MemberReference;
            if (member?.DeclaringType?.Scope is not AssemblyNameReference scope || scope.Name != "Seapower-Scripts") continue;
            try {
                if (member is MethodReference call) { if (call.Resolve() == null) throw new Exception("unresolved method"); resolved++; }
                else if (member is FieldReference field) { if (field.Resolve() == null) throw new Exception("unresolved field"); resolved++; }
            } catch (Exception ex) { missing.Add(method.Name + ": " + member.FullName + " " + ex.Message); }
        }
        foreach (string failure in missing) Console.WriteLine("MISSING AutomaticSAR/" + failure);
        Console.WriteLine("AutomaticSAR resolved native operands: " + resolved);
        Check(missing.Count == 0 && resolved > 200, "Every AutomaticSAR Seapower-Scripts method/field operand resolves on the beta");
        Check(!module.GetMemberReferences().Any(m => (m.DeclaringType.FullName == "SeaPower.GeoPosition" && m.Name == "CourseTo") ||
            m.DeclaringType.FullName == "SeaPower.ConstantSpeed" || m.DeclaringType.FullName == "SeaPower.ConstantMach" ||
            m.FullName == "System.Void SeaPower.ObjectBase::SetSpeedCommand(SeaPower.ISpeedCommand)"),
            "No stable-only GeoPosition/speed member is referenced");
        var encoding = new List<string>();
        foreach (var type in Types(module.Types)) foreach (var field in type.Fields) AutomaticSAREncoding(field.FieldType, type.FullName + "." + field.Name, encoding);
        foreach (var method in Types(module.Types).SelectMany(t => t.Methods)) {
            AutomaticSAREncoding(method.ReturnType, method.FullName, encoding);
            foreach (var parameter in method.Parameters) AutomaticSAREncoding(parameter.ParameterType, method.FullName, encoding);
            if (!method.HasBody) continue;
            foreach (var variable in method.Body.Variables) AutomaticSAREncoding(variable.VariableType, method.FullName + " local", encoding);
            foreach (var instruction in method.Body.Instructions) {
                if (instruction.Operand is MethodReference call) {
                    AutomaticSAREncoding(call.ReturnType, call.FullName, encoding);
                    foreach (var parameter in call.Parameters) AutomaticSAREncoding(parameter.ParameterType, call.FullName, encoding);
                    if (call.DeclaringType is GenericInstanceType owner) AutomaticSAREncoding(owner, call.FullName, encoding);
                    if (call is GenericInstanceMethod instance) foreach (var argument in instance.GenericArguments) AutomaticSAREncoding(argument, call.FullName, encoding);
                }
                else if (instruction.Operand is FieldReference field) AutomaticSAREncoding(field.FieldType, field.FullName, encoding);
            }
        }
        foreach (string error in encoding) Console.WriteLine("ENCODING AutomaticSAR " + error);
        Check(encoding.Count == 0, "No AutomaticSAR field, local or signature encodes a changed beta value type");

        // The rewritten IL, as written.
        var coordinator = module.GetType("AutomaticSAR.RescueCoordinator");
        MethodDefinition Method(TypeDefinition type, string name) => type.Methods.Single(m => m.Name == name);
        var lerp = Method(coordinator, "InterpolateGeoPosition");
        Check(lerp.Body.Variables.Count == 0 && AutomaticSARTexts(lerp).SequenceEqual(new[] { "ldarg.0", "ldarg.1", "ldarg.2",
            "call SeaPower.GeoPosition " + AutomaticSARBridge + "::AutomaticSARInterpolateGeoPosition(SeaPower.GeoPosition,SeaPower.GeoPosition,System.Single)", "ret" }),
            "InterpolateGeoPosition is the straight lat/lon bridge");
        Check(AutomaticSARRun(Method(coordinator, "GetHelicopterOvershootWaypoint"), "ldloca.s V1", "ldloc.0",
            "call System.Single SeaPower.GeoPosition::HeadingToPosition(SeaPower.GeoPosition)",
            "call SeaPower.GeoPosition SeaPower.GeoPosition::GeoOffsetByDistanceOnHeading(System.Single,System.Single)", "ret") >= 0,
            "Helicopter overshoot waypoint uses the beta bearing");
        Check(AutomaticSARRun(Method(coordinator, "SetRescueSpeed"), "ldarg.0", "ldloc.0",
            "newobj System.Void AutomaticSAR.RescueCoordinator/SarConstantSpeed::.ctor(System.Single)",
            "call System.Void " + AutomaticSARBridge + "::AutomaticSARSetCustomSpeedCommand(SeaPower.ObjectBase,SeaPower.ISpeedCommand)", "ret",
            "ldarg.0", "ldloc.0", "ldarg.0", "call SeaPower.SpeedRequest " + AutomaticSARBridge + "::ConstantSpeedRequest(System.Single,SeaPower.ObjectBase)",
            "call System.Void " + AutomaticSARBridge + "::SetSpeedRequest(SeaPower.ObjectBase,SeaPower.SpeedRequest)", "ret") >= 0,
            "Rescue speed: submarine installs SarConstantSpeed, ships send the native knots request");
        foreach (var (name, slot, kind, read, make) in new[] {
            ("SetVtolKnotSpeed", 0, "AutomaticSARConstantKnotsCommand", "get_SpeedInKnots", "SeaPower.SpeedRequest " + AutomaticSARBridge + "::ConstantSpeedRequest(System.Single,SeaPower.ObjectBase)"),
            ("SetVtolMachSpeed", 2, "AutomaticSARConstantMachCommand", "get_SpeedInMach", "SeaPower.SpeedRequest " + AutomaticSARBridge + "::AutomaticSARMachRequest(System.Single,SeaPower.ObjectBase)") }) {
            var vtol = Method(coordinator, name);
            Check(vtol.Body.Variables[slot].VariableType.FullName == "SeaPower.ISpeedCommand" &&
                AutomaticSARRun(vtol, "call SeaPower.ISpeedCommand " + AutomaticSARBridge + "::" + kind + "(SeaPower.ISpeedCommand)", "stloc." + slot, "ldloc." + slot) >= 0 &&
                AutomaticSARRun(vtol, "ldloc." + slot, "callvirt System.Single SeaPower.ISpeedCommand::" + read + "()") >= 0 &&
                AutomaticSARRun(vtol, "call " + make, "call System.Void " + AutomaticSARBridge + "::SetSpeedRequest(SeaPower.ObjectBase,SeaPower.SpeedRequest)", "ret") >= 0,
                "VTOL speed step reads the beta speed kind and sends a request: " + name);
        }
        var moveNext = Method(module.GetType("AutomaticSAR.PlayerCommandPatch").NestedTypes.Single(t => t.Name == "<TargetMethods>d__0"), "MoveNext");
        var moveTexts = AutomaticSARTexts(moveNext);
        int filter = AutomaticSARRun(moveNext, "stloc.2", "ldloc.2", "callvirt System.Boolean System.Reflection.MethodBase::get_IsGenericMethodDefinition()");
        int speedTest = moveTexts.IndexOf("ldstr \"SetSpeedCommand\"");
        Check(filter >= 0 && moveTexts[filter + 3] == moveTexts[speedTest + 2].Replace("brfalse", "brtrue") &&
            moveTexts[filter + 4] == "ldloc.2" && moveTexts[filter + 6] == "ldstr \"setWaypointTask\"",
            "TargetMethods skips generic method definitions before its name tests, to the loop increment");
        var walk = Method(coordinator, "WasCalledDirectlyFromGameUi");
        var walkTexts = AutomaticSARTexts(walk);
        int head = AutomaticSARRun(walk, "ldloc.2", "ldloc.3", "ldelem.ref",
            "call System.Boolean " + AutomaticSARBridge + "::AutomaticSARIsGenericSpeedForwarder(System.Diagnostics.StackFrame)");
        int increment = AutomaticSARRun(walk, "ldloc.3", "ldc.i4.1", "add", "stloc.3");
        Check(head >= 0 && increment >= 0 && walkTexts[head + 4] == "brtrue #" + increment && walkTexts[head + 5] == "ldloc.s V5" &&
            walkTexts[head + 6] == "ldstr \"AutomaticSAR.\"" && walkTexts.Contains("brtrue #" + head) &&
            walkTexts[walkTexts.IndexOf("brtrue #" + head) - 1] == "ldloc.1",
            "UI stack walk skips the beta SetSpeedCommand<T> forwarder frame after the patched frame");
        var sarSpeed = coordinator.NestedTypes.Single(t => t.Name == "SarConstantSpeed");
        Check(AutomaticSARTexts(Method(sarSpeed, "get_Kind")).SequenceEqual(new[] { "ldc.i4.3", "ret" }) &&
            Method(sarSpeed, "get_Kind").ReturnType.FullName == "SeaPower.SpeedKind" && Method(sarSpeed, "get_Kind").ReturnType.IsValueType &&
            AutomaticSARTexts(Method(sarSpeed, "get_Telegraph")).SequenceEqual(new[] { "ldc.i4.0", "ret" }) &&
            Method(sarSpeed, "get_Kind").IsVirtual && Method(sarSpeed, "get_Telegraph").IsVirtual,
            "SarConstantSpeed reports Kind=Constant and Telegraph=0 like a beta knots request");
        // Every other author body is unchanged apart from widened branches.
        var targets = new HashSet<string> { "InterpolateGeoPosition", "GetHelicopterOvershootWaypoint", "SetRescueSpeed", "SetVtolKnotSpeed",
            "SetVtolMachSpeed", "WasCalledDirectlyFromGameUi" };
        int compared = 0; var changed = new List<string>();
        var written = methods.ToDictionary(m => m.FullName);
        foreach (var original in Types(author.Types).SelectMany(t => t.Methods).Where(m => m.HasBody)) {
            if ((original.DeclaringType.FullName == "AutomaticSAR.RescueCoordinator" && targets.Contains(original.Name))) continue;
            if (original.DeclaringType.Name == "<TargetMethods>d__0" && original.Name == "MoveNext") continue;
            // Build 261106 adds only demPeak=false to five terrain calls.
            // Normalize those exact sites before comparing all other IL.
            foreach (var call in original.Body.Instructions.Where(i => i.Operand is MethodReference m &&
                m.DeclaringType.FullName == "SeaPower.TerrainUtils" && m.Name == "GetHeightAt" && m.Parameters.Count == 3).ToArray()) {
                using var terrainNative=ModuleDefinition.ReadModule(context.Native);
                var nativeHeight=terrainNative.GetType("SeaPower.TerrainUtils").Methods.Single(m=>m.Name=="GetHeightAt");
                var proc=original.Body.GetILProcessor();
                // Retain branch targets at the first inserted argument.
                var opcode=call.OpCode; call.OpCode=Mono.Cecil.Cil.OpCodes.Ldc_I4; call.Operand=0;
                proc.InsertAfter(call,Mono.Cecil.Cil.Instruction.Create(opcode,author.ImportReference(nativeHeight)));
            }
            if (!written.TryGetValue(original.FullName, out var copy) || !AutomaticSARTexts(original).SequenceEqual(AutomaticSARTexts(copy)) ||
                !original.Body.Variables.Select(v => v.VariableType.FullName).SequenceEqual(copy.Body.Variables.Select(v => v.VariableType.FullName)))
                changed.Add(original.FullName);
            compared++;
        }
        foreach (string name in changed) Console.WriteLine("CHANGED AutomaticSAR " + name);
        Check(changed.Count == 0 && compared > 170, "Untargeted AutomaticSAR bodies are byte-for-byte the author's IL (" + compared + " compared)");

        // Reflection on the loaded private image.
        var loaded = Assembly.LoadFile(adapted);
        Check(BetaAssemblyPolicy.OriginalLocation(loaded) == source, "AutomaticSAR keeps its Workshop location");
        var sar = loaded.GetType("AutomaticSAR.RescueCoordinator+SarConstantSpeed", true);
        var map = sar.GetInterfaceMap(typeof(ISpeedCommand));
        Check(map.TargetMethods.Length == 14 && map.TargetMethods.All(m => m.DeclaringType == sar), "SarConstantSpeed implements all 14 beta ISpeedCommand members");
        var command = (ISpeedCommand)Activator.CreateInstance(sar, all, null, new object[] { 12.5f }, CultureInfo.InvariantCulture);
        Check(command.Kind == SpeedKind.Constant && command.Telegraph == 0 && command.GetDemandedSpeedInKnots(null) == 12.5f && !command.AvoidingCavitation,
            "SarConstantSpeed holds 12.5 kn without the cavitation flag and reports a constant-knots kind");
        var rescue = loaded.GetType("AutomaticSAR.RescueCoordinator", true);
        Check(rescue.GetMethod("SetVtolKnotSpeed", all).GetMethodBody().LocalVariables[0].LocalType == typeof(ISpeedCommand) &&
            rescue.GetMethod("SetVtolMachSpeed", all).GetMethodBody().LocalVariables[2].LocalType == typeof(ISpeedCommand),
            "Retyped VTOL locals decode on the beta");
        foreach (string name in targets) {
            var body = PatchProcessor.GetOriginalInstructions(rescue.GetMethod(name, all));
            Check(body.Count > 0 && body.All(i => !(i.operand is MethodBase m) || m.DeclaringType != null), "Rewritten IL binds at runtime: " + name);
        }
        var rescueSpeed = PatchProcessor.GetOriginalInstructions(rescue.GetMethod("SetRescueSpeed", all));
        Check(rescueSpeed.Count(i => (i.operand as MethodInfo)?.DeclaringType?.FullName == AutomaticSARBridge) == 3, "Rescue speed binds its three AnchorChain bridges");
        Check(!(bool)rescue.GetMethod("WasCalledDirectlyFromGameUi", all).Invoke(null, null), "Rewritten UI stack walk JITs and finds no game UI frame here");

        // Speed bridges against the native beta speed types.
        var knotsOrder = new ConstantSpeed(9.5f, null).ToRequest();
        var machOrder = new ConstantMach(0.8f, null).ToRequest();
        var knotsRequest = BetaCompatibilityCalls.ConstantSpeedRequest(9.5f, null);
        var machRequest = BetaCompatibilityCalls.AutomaticSARMachRequest(0.8f, null);
        Check(knotsRequest.Equals(knotsOrder) && knotsRequest.Kind == SpeedKind.Constant && knotsRequest.Value == 9.5f && knotsRequest.Step == 0,
            "Knots bridge returns the native ConstantSpeed request");
        Check(machRequest.Equals(machOrder) && machRequest.Kind == SpeedKind.Mach && machRequest.Value == 0.8f && machRequest.Step == 0,
            "Mach bridge returns the native ConstantMach request");
        var state = new SpeedState(); var twelve = SpeedRequest.Knots(12f);
        Check(state.Apply(ref twelve, null) && state.Kind == SpeedKind.Constant && state.SpeedInKnots == 12f, "Native SpeedState takes a 12 kn request");
        Check(ReferenceEquals(BetaCompatibilityCalls.AutomaticSARConstantKnotsCommand(state), state) &&
            BetaCompatibilityCalls.AutomaticSARConstantMachCommand(state) == null, "A native constant-knots state reads as the stable ConstantSpeed");
        Check(ReferenceEquals(BetaCompatibilityCalls.AutomaticSARConstantKnotsCommand(command), command) &&
            BetaCompatibilityCalls.AutomaticSARConstantMachCommand(command) == null, "The installed SarConstantSpeed reads as a constant-knots command");
        var machStub = new AutomaticSARSpeedStub { Kind = SpeedKind.Mach };
        var telegraphStub = new AutomaticSARSpeedStub { Kind = SpeedKind.Telegraph };
        Check(ReferenceEquals(BetaCompatibilityCalls.AutomaticSARConstantMachCommand(machStub), machStub) &&
            BetaCompatibilityCalls.AutomaticSARConstantKnotsCommand(machStub) == null &&
            BetaCompatibilityCalls.AutomaticSARConstantKnotsCommand(telegraphStub) == null && BetaCompatibilityCalls.AutomaticSARConstantMachCommand(telegraphStub) == null &&
            BetaCompatibilityCalls.AutomaticSARConstantKnotsCommand(null) == null && BetaCompatibilityCalls.AutomaticSARConstantMachCommand(null) == null,
            "Speed-kind bridges match only their own kind");
        Check(!typeof(IDisposable).IsAssignableFrom(typeof(SpeedState)) && !typeof(IDisposable).IsAssignableFrom(sar),
            "Installing the SAR command disposes neither the beta SpeedState nor SarConstantSpeed");
        var speedCommand = typeof(BetaCompatibilityCalls).GetNestedType("AutomaticSARSpeedCommand", BindingFlags.NonPublic);
        var property = (PropertyInfo)speedCommand.GetField("Property", all).GetValue(null);
        var value = (PropertyInfo)speedCommand.GetField("Value", all).GetValue(null);
        var hasValue = (PropertyInfo)speedCommand.GetField("HasValue", all).GetValue(null);
        Check(property?.DeclaringType == typeof(ObjectBase) && value?.PropertyType == typeof(ISpeedCommand) && value.CanWrite &&
            hasValue?.PropertyType == typeof(bool), "Custom-command bridge binds ObjectBase.SpeedCommand.Value/HasValue");

        // Route interpolation: the stable straight lat/lon line.
        var interpolate = rescue.GetMethod("InterpolateGeoPosition", all);
        var legs = new[] { (new GeoPosition(-33.5, 151.25, 4), new GeoPosition(-33.1, 151.9, 0)), (new GeoPosition(60, 5, 0), new GeoPosition(60, 5.6667, 0)),
            (new GeoPosition(12, -40, 0), new GeoPosition(11.2, -40.3, 0)) };
        foreach (var (a, b) in legs) foreach (float t in new[] { 0f, 0.1f, 0.5f, 0.9f, 1f }) {
            var bridge = BetaCompatibilityCalls.AutomaticSARInterpolateGeoPosition(a, b, t);
            var stable = AutomaticSARStableInterpolate(a, b, t);
            var image = (GeoPosition)interpolate.Invoke(null, new object[] { a, b, t });
            Check(Math.Abs(bridge.Latitude - stable.Latitude) < 1e-5 && Math.Abs(bridge.Longitude - stable.Longitude) < 1e-5 && bridge._height == a._height,
                "Interpolation matches stable 261021 at t=" + t + " from " + a);
            Check(image.Latitude == bridge.Latitude && image.Longitude == bridge.Longitude && image._height == bridge._height,
                "Private InterpolateGeoPosition returns the bridge result");
        }
        var east = new GeoPosition(10, 179.9, 0); var west = new GeoPosition(10.2, -179.9, 0);
        var middle = BetaCompatibilityCalls.AutomaticSARInterpolateGeoPosition(east, west, 0.5f);
        var end = BetaCompatibilityCalls.AutomaticSARInterpolateGeoPosition(east, west, 1f);
        Check(Math.Abs(middle.Latitude - 10.1) < 1e-6 && Math.Abs(Math.Abs(middle.Longitude) - 180) < 1e-6 &&
            Math.Abs(end.Longitude + 179.9) < 1e-6, "A date-line leg is sampled across the short way");

        // Generic forwarder frame test.
        var forwarder = typeof(ObjectBase).GetMethods(BindingFlags.Public | BindingFlags.Instance).Single(m => m.Name == "SetSpeedCommand" && m.IsGenericMethodDefinition);
        var concrete = typeof(ObjectBase).GetMethods(BindingFlags.Public | BindingFlags.Instance).Single(m => m.Name == "SetSpeedCommand" && !m.IsGenericMethod);
        Check(BetaCompatibilityCalls.AutomaticSARIsGenericSpeedForwarderMethod(forwarder) &&
            BetaCompatibilityCalls.AutomaticSARIsGenericSpeedForwarderMethod(forwarder.MakeGenericMethod(typeof(ConstantSpeed))) &&
            BetaCompatibilityCalls.AutomaticSARIsGenericSpeedForwarderMethod(forwarder.MakeGenericMethod(typeof(TelegraphSpeed))),
            "The beta SetSpeedCommand<T> forwarder is recognised, open or instantiated");
        Check(!BetaCompatibilityCalls.AutomaticSARIsGenericSpeedForwarderMethod(concrete) &&
            !BetaCompatibilityCalls.AutomaticSARIsGenericSpeedForwarderMethod(typeof(ObjectBase).GetMethods(BindingFlags.Public | BindingFlags.Instance).First(m => m.Name == "setOrder")) &&
            !BetaCompatibilityCalls.AutomaticSARIsGenericSpeedForwarderMethod(typeof(AutomaticSARDecoy).GetMethod("SetSpeedCommand")) &&
            !BetaCompatibilityCalls.AutomaticSARIsGenericSpeedForwarderMethod(null) &&
            !BetaCompatibilityCalls.AutomaticSARIsGenericSpeedForwarder(new StackFrame()) && !BetaCompatibilityCalls.AutomaticSARIsGenericSpeedForwarder(null),
            "The patched concrete SetSpeedCommand, other commands and look-alikes are not skipped");

        // PlayerCommandPatch targets: the author's lookup on the beta, then the adapted one.
        var names = new[] { "setWaypointTask", "SetWaypointTask", "SetAttackAtWaypointTask", "RemoveWaypoints", "setOrder", "SetSpeedCommand" };
        var expected = typeof(ObjectBase).GetMethods(BindingFlags.Instance | BindingFlags.Public).Where(m => names.Contains(m.Name) && !m.IsGenericMethodDefinition)
            .Cast<MethodBase>().Concat(new MethodBase[] { AccessTools.Method(typeof(Helicopter), "setPresetHeight"),
                AccessTools.Method(typeof(Vessel), "setTelegraph"), AccessTools.Method(typeof(Submarine), "setTelegraph") }).ToList();
        var authorTargets = ((IEnumerable<MethodBase>)Assembly.LoadFile(source).GetType("AutomaticSAR.PlayerCommandPatch", true)
            .GetMethod("TargetMethods", all).Invoke(null, null)).ToList();
        Check(authorTargets.Count == 12 && authorTargets[0].IsGenericMethodDefinition && authorTargets[0].Name == "SetSpeedCommand",
            "The author's lookup yields the open generic SetSpeedCommand<T> first on the beta, as captured");
        var patch = loaded.GetType("AutomaticSAR.PlayerCommandPatch", true);
        var adaptedTargets = ((IEnumerable<MethodBase>)patch.GetMethod("TargetMethods", all).Invoke(null, null)).ToList();
        Check(adaptedTargets.Count == 11 && adaptedTargets.SequenceEqual(expected) && expected.All(m => m != null && !m.IsGenericMethodDefinition) &&
            adaptedTargets.Any(m => m.Name == "SetSpeedCommand" && m.GetParameters().Single().ParameterType == typeof(SpeedRequest).MakeByRefType()) &&
            adaptedTargets.Count(m => m.Name == "SetAttackAtWaypointTask") == expected.Count(m => m.Name == "SetAttackAtWaypointTask"),
            "Adapted TargetMethods yields the 11 concrete beta command methods");

        // HarmonyX binds a patch parameter by the original's name, as
        // __instance or __result, or ___field: check every patch against the
        // real beta target(s).
        int bound = 0;
        foreach (var type in loaded.GetTypes()) {
            var attribute = type.CustomAttributes.SingleOrDefault(a => a.AttributeType.FullName == "HarmonyLib.HarmonyPatch");
            if (attribute == null) continue;
            List<MethodBase> originals = attribute.ConstructorArguments.Count == 2
                ? new List<MethodBase> { AccessTools.Method((Type)attribute.ConstructorArguments[0].Value, (string)attribute.ConstructorArguments[1].Value) }
                : ((IEnumerable<MethodBase>)type.GetMethod("TargetMethods", all).Invoke(null, null)).ToList();
            Check(originals.Count > 0 && originals.All(m => m != null), "Patch target exists on the beta: " + type.FullName);
            foreach (var patchMethod in type.GetMethods(all).Where(m => m.Name == "Prefix" || m.Name == "Postfix"))
            foreach (var original in originals) foreach (var parameter in patchMethod.GetParameters()) {
                bool ok;
                if (parameter.Name == "__instance") ok = !original.IsStatic && parameter.ParameterType.IsAssignableFrom(original.DeclaringType);
                else if (parameter.Name == "__result") ok = original is MethodInfo info && parameter.ParameterType.IsAssignableFrom(info.ReturnType);
                else if (parameter.Name.StartsWith("___")) {
                    var field = AccessTools.Field(original.DeclaringType, parameter.Name.Substring(3));
                    ok = field != null && parameter.ParameterType.IsAssignableFrom(field.FieldType);
                }
                else ok = original.GetParameters().Any(p => p.Name == parameter.Name && p.ParameterType == parameter.ParameterType);
                Check(ok, "Patch parameter binds: " + type.Name + "." + patchMethod.Name + "(" + parameter.Name + ") on " + original.DeclaringType.Name + "." + original.Name);
                bound++;
            }
        }
        Check(bound == 20, "All AutomaticSAR patch parameters were checked (" + bound + ")");
    }
}
