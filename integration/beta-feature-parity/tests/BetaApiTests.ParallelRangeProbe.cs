using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using AnchorChain;
using Mono.Cecil;
using SeaPower;

static partial class BetaApiTests
{
    // R6: ParallelRangeProbe 0.12.0 (Workshop 3784474738). Metadata, reflection
    // and the WorkerExpansion sensor kernels only: no Harmony patch is applied,
    // no Unity gameplay runs, and no game getter is invoked.
    static void R6_ParallelRangeProbe(R6Context context)
    {
        const BindingFlags all = BindingFlags.NonPublic|BindingFlags.Public|BindingFlags.Static|BindingFlags.Instance;
        const string pinned = "2d04ed4ba00f8084ba2e653f1b271d91a722997b9e1b1bf823a3f411fffa9481";
        string source = Path.Combine(context.Workshop, "3784474738/ParallelRangeProbe.dll");
        byte[] bytes = File.ReadAllBytes(source);
        string hash;
        using (var sha = System.Security.Cryptography.SHA256.Create())
            hash = BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant();
        Check(hash == pinned, "ParallelRangeProbe fixture is the captured 0.12.0 image");

        var adapter = typeof(BetaAssemblyPolicy).GetMethod("ParallelRangeProbeAdapter", BindingFlags.NonPublic|BindingFlags.Static).Invoke(null, null);
        string expected = (string)adapter.GetType().GetField("ExpectedAudit", all).GetValue(adapter);
        Check(expected == "locations=2, radar-range-bool=1, sensor-constant-fold=1", "ParallelRangeProbe expected audit is the reviewed one");

        List<string> nativeDetection, nativeHorizon;
        var log = new List<string>();
        string adapted = BetaAssemblyPolicy.Prepare(source, context.Native, context.Cache, log.Add);
        foreach (string line in log) Console.WriteLine(line);
        Check(adapted != null && adapted != source && File.Exists(adapted), "ParallelRangeProbe private image generated");
        Check(bytes.SequenceEqual(File.ReadAllBytes(source)), "ParallelRangeProbe author bytes retained");
        Check(log.Count == 1 && log[0] == "ADAPTED ParallelRangeProbe in private cache: " + expected + "; original Workshop DLL and asset paths preserved.",
            "ParallelRangeProbe logged audit equals ExpectedAudit");

        var inspect = typeof(BetaAssemblyPolicy).GetMethod("InvalidNativeFields", BindingFlags.Static|BindingFlags.NonPublic);
        using (var module = ModuleDefinition.ReadModule(adapted, new ReaderParameters { AssemblyResolver=context.Resolver }))
        using (var game = ModuleDefinition.ReadModule(context.Native)) {
            var calculator = game.GetType("SeaPower.RadarCalculator");
            nativeDetection = calculator.Methods.Single(m => m.Name == "BaseMaxDetectionRangeMeter").Body.Instructions.Select(i => i.OpCode.Name).ToList();
            nativeHorizon = calculator.Methods.Single(m => m.Name == "getRadarHorizon").Body.Instructions.Select(i => i.OpCode.Name).ToList();
            Check(((List<string>)inspect.Invoke(null, new object[] { module, game })).Count == 0, "ParallelRangeProbe written image has no class/struct field mismatch");
            // Rewrite 1: the radar lookup's Type[] gains typeof(bool) as element 2.
            var ctor = module.GetType("WorkerExpansion.AuxAdapter").Methods.Single(m => m.IsConstructor && !m.IsStatic);
            var il = ctor.Body.Instructions.ToList();
            int name = il.FindIndex(i => i.OpCode == Mono.Cecil.Cil.OpCodes.Ldstr && Equals(i.Operand, "GetRangeInternal"));
            int require = il.FindIndex(name, i => (i.Operand as MethodReference)?.Name == "Require");
            var window = il.Skip(name).Take(require - name + 1).ToList();
            Check(window.Count(i => i.OpCode == Mono.Cecil.Cil.OpCodes.Ldc_I4_3 && i.Next.OpCode == Mono.Cecil.Cil.OpCodes.Newarr) == 1 &&
                !window.Any(i => i.OpCode == Mono.Cecil.Cil.OpCodes.Ldc_I4_2 && i.Next.OpCode == Mono.Cecil.Cil.OpCodes.Newarr),
                "Radar lookup allocates three parameter types");
            var tail = il.Skip(require - 6).Take(7).ToList();
            Check(tail[0].OpCode == Mono.Cecil.Cil.OpCodes.Stelem_Ref && tail[1].OpCode == Mono.Cecil.Cil.OpCodes.Dup &&
                tail[2].OpCode == Mono.Cecil.Cil.OpCodes.Ldc_I4_2 && tail[3].OpCode == Mono.Cecil.Cil.OpCodes.Ldtoken &&
                ((TypeReference)tail[3].Operand).FullName == "System.Boolean" && (tail[4].Operand as MethodReference)?.FullName ==
                    "System.Type System.Type::GetTypeFromHandle(System.RuntimeTypeHandle)" &&
                tail[5].OpCode == Mono.Cecil.Cil.OpCodes.Stelem_Ref && tail[6].OpCode == Mono.Cecil.Cil.OpCodes.Call,
                "Radar lookup stores typeof(bool) as the third parameter type before Require");
            Check(module.AssemblyReferences.Count(a => a.Name == "mscorlib") == 1, "Radar lookup reuses the author's corlib reference");
            // Rewrite 2: Read hands its decoded list to the fold bridge before returning.
            var read = module.GetType("WorkerExpansion.NativeSensorKernel").Methods.Single(m => m.Name == "Read").Body.Instructions;
            var end = read.Skip(read.Count - 5).ToList();
            Check(end[0].OpCode == Mono.Cecil.Cil.OpCodes.Ldloc_1 && end[1].OpCode == Mono.Cecil.Cil.OpCodes.Dup &&
                end[2].OpCode == Mono.Cecil.Cil.OpCodes.Ldarg_0 && end[3].OpCode == Mono.Cecil.Cil.OpCodes.Call &&
                ((MethodReference)end[3].Operand).FullName ==
                    "System.Void AnchorChain.BetaCompatibilityCalls::ParallelRangeProbeFoldDetectionConstant(System.Collections.IList,System.Reflection.MethodInfo)" &&
                end[4].OpCode == Mono.Cecil.Cil.OpCodes.Ret && read.Count(i => i.OpCode == Mono.Cecil.Cil.OpCodes.Ret) == 1 &&
                !read.Any(i => i.Operand is Mono.Cecil.Cil.Instruction target && (target == end[1] || target == end[4])),
                "Sensor IL reader returns through the fold bridge");
            Check(module.AssemblyReferences.Count(a => a.Name == "AnchorChain") == 1, "Fold bridge reuses the author's AnchorChain reference");
            var warm = module.GetType("WorkerExpansion.Auxiliary").Methods.Single(m => m.Name == "WarmRadar");
            Check(warm.Parameters.Select(p => p.Name).SequenceEqual(new[] { "__instance", "__0" }), "WarmRadar stays as the author wrote it");

            // Every Seapower-Scripts operand resolves on the beta except the two
            // dormant constructors of the modules that stay fail-closed.
            var missing = new List<string>(); int resolved = 0;
            foreach (var type in Types(module.Types)) foreach (var method in type.Methods.Where(m => m.HasBody))
                foreach (var instruction in method.Body.Instructions) {
                    var member = instruction.Operand as MemberReference;
                    if (member is not (MethodReference or FieldReference) ||
                        member.DeclaringType?.Scope is not AssemblyNameReference scope || scope.Name != "Seapower-Scripts") continue;
                    bool ok;
                    // Cecil's resolver also searches base types; require the
                    // member on the declaring type itself (a struct has no .ctor()).
                    try {
                        IMemberDefinition definition = member is MethodReference call ? call.Resolve() : member is FieldReference field ? field.Resolve() : null;
                        ok = definition != null && definition.DeclaringType.FullName == member.DeclaringType.GetElementType().FullName;
                    }
                    catch { ok = false; }
                    if (ok) resolved++; else missing.Add(type.FullName + "::" + method.Name + " " + member.FullName);
                }
            foreach (string failure in missing) Console.WriteLine("DORMANT " + failure);
            Console.WriteLine("ParallelRangeProbe native operands: " + resolved + " resolved, " + missing.Count + " dormant");
            Check(resolved > 20 && missing.Distinct().OrderBy(x => x, StringComparer.Ordinal).SequenceEqual(new[] {
                    "ParallelContacts.RangeValue::Copy System.Void SeaPower.SensorSystem/SensorDistanceData::.ctor()",
                    "ParallelRange.RangePrediction::Before System.Void SeaPower.MissileSimulator/KinematicRangeResult::.ctor()" }),
                "ParallelRangeProbe native operands resolve except the two fail-closed modules' class constructors");
        }

        var loaded = Assembly.LoadFile(adapted);
        Check(BetaAssemblyPolicy.OriginalLocation(loaded) == source, "ParallelRangeProbe original asset provenance");
        var options = typeof(ObjectBase).GetNestedType("SensorRangeOptions", all);
        // RangeReuse and Prediction stay off through the author's own guards.
        foreach (var (type, method) in new[] { ("ParallelRange.RangePrediction", "Before"), ("ParallelRange.RangePrediction", "After"),
                ("ParallelContacts.RangeReuse", "BeforeRange"), ("ParallelContacts.RangeReuse", "AfterRange") }) {
            string failure = null;
            try { loaded.GetType(type, true).GetMethod(method, all).GetParameters(); } catch (Exception ex) { failure = ex.Message; }
            Check(failure != null && failure.Contains("Expected reference type"), "Fail-closed module keeps its class-encoded signature: " + type + "." + method);
        }
        Check(typeof(SensorSystemRadar).GetMethod("GetRangeInternal", all, null, new[] { typeof(ObjectBase), options }, null) == null,
            "The author's stable radar lookup fails on the beta, as captured");

        // The adapted AuxAdapter constructor: pure reflection plus the two
        // DynamicMethod kernel copies. It must bind beta's real members.
        var auxType = loaded.GetType("WorkerExpansion.AuxAdapter", true);
        var aux = Activator.CreateInstance(auxType, all, null, new object[] { typeof(ObjectBase).Assembly }, null);
        MethodInfo Bound(string field) => (MethodInfo)auxType.GetField(field, all).GetValue(aux);
        var range = Bound("RadarRange");
        Check(range != null && range.DeclaringType == typeof(SensorSystemRadar) && !range.IsStatic &&
            range.ReturnType == typeof(SensorSystem).GetNestedType("SensorDistanceData", all) &&
            range.GetParameters().Select(p => p.ParameterType).SequenceEqual(new[] { typeof(ObjectBase), options, typeof(bool) }) &&
            range.GetParameters()[2].Name == "boundOnly", "Adapted radar lookup binds beta GetRangeInternal(targetObject, options, boundOnly)");
        var horizon = Bound("Horizon"); var detection = Bound("Detection");
        Check(horizon.DeclaringType == typeof(RadarCalculator) && horizon.Name == "getRadarHorizon" &&
            detection.DeclaringType == typeof(RadarCalculator) && detection.Name == "BaseMaxDetectionRangeMeter" &&
            Bound("VesselPriority").Name == "GetVesselEngagePriority" && Bound("SubPriority").Name == "GetSubmarineEngagePriority",
            "WorkerExpansion binds the beta horizon, detection and priority methods");

        // HarmonyX binds __instance, __result, __state, __originalMethod and
        // __N (argument N) to the real target. Check each WorkerExpansion hook.
        var auxiliary = loaded.GetType("WorkerExpansion.Auxiliary", true);
        foreach (var (hook, target) in new[] { ("BeforeHorizon", horizon), ("AfterSensor", horizon), ("BeforeDetection", detection),
                ("AfterSensor", detection), ("WarmRadar", range), ("BeforePriority", Bound("VesselPriority")), ("AfterPriority", Bound("VesselPriority")),
                ("BeforePriority", Bound("SubPriority")), ("AfterPriority", Bound("SubPriority")) }) {
            var targets = target.GetParameters();
            foreach (var parameter in auxiliary.GetMethod(hook, all).GetParameters()) {
                var type = parameter.ParameterType.IsByRef ? parameter.ParameterType.GetElementType() : parameter.ParameterType;
                bool binds = parameter.Name == "__instance" ? !target.IsStatic && type.IsAssignableFrom(target.DeclaringType) :
                    parameter.Name == "__result" ? type == target.ReturnType :
                    parameter.Name == "__state" ? true :
                    parameter.Name == "__originalMethod" ? type == typeof(MethodBase) :
                    parameter.Name.StartsWith("__") && int.TryParse(parameter.Name.Substring(2), out int index) && index < targets.Length &&
                        !parameter.ParameterType.IsByRef && targets[index].ParameterType == type;
                Check(binds, "WorkerExpansion " + hook + " parameter binds to beta " + target.Name + ": " + parameter.Name);
            }
        }

        // The fold bridge on the real decoded IL.
        var kernelType = loaded.GetType("WorkerExpansion.NativeSensorKernel", true);
        var readList = kernelType.GetMethod("Read", all);
        var instructionType = loaded.GetType("WorkerExpansion.NativeSensorKernel+Instruction", true);
        var opcodeField = instructionType.GetField("opcode", all); var operandField = instructionType.GetField("operand", all);
        var four = typeof(RadarCalculator).GetField("FourPiCubed", BindingFlags.Static|BindingFlags.NonPublic|BindingFlags.Public);
        float fourValue = (float)four.GetValue(null);
        Check(BitConverter.ToInt32(BitConverter.GetBytes(fourValue), 0) == BitConverter.ToInt32(BitConverter.GetBytes(UnityEngine.Mathf.Pow(12.566371f, 3f)), 0),
            "Beta FourPiCubed holds Mathf.Pow(12.566371f, 3f), as its static initialiser computes");
        var folded = ((IList)readList.Invoke(null, new object[] { detection })).Cast<object>().ToList();
        var nativeIl = nativeDetection;
        Check(folded.Count == nativeIl.Count && folded.Count == 26, "Folded detection kernel keeps beta's 26 instructions");
        int constants = 0;
        for (int i = 0; i < folded.Count; i++) {
            var op = (OpCode)opcodeField.GetValue(folded[i]);
            if (nativeIl[i] == "ldsfld") {
                Check(op == OpCodes.Ldc_R4 && operandField.GetValue(folded[i]) is float value &&
                    BitConverter.ToInt32(BitConverter.GetBytes(value), 0) == BitConverter.ToInt32(BitConverter.GetBytes(fourValue), 0),
                    "FourPiCubed read becomes the identical float constant");
                constants++;
            }
            else Check(op.Name == nativeIl[i], "Folded detection kernel keeps beta opcode " + i + ": " + nativeIl[i]);
        }
        Check(constants == 1, "Exactly one static read folded");
        var horizonList = (IList)readList.Invoke(null, new object[] { horizon });
        Check(horizonList.Count == nativeHorizon.Count && horizonList.Cast<object>().Select(x => ((OpCode)opcodeField.GetValue(x)).Name).SequenceEqual(nativeHorizon),
            "Horizon kernel IL passes through the bridge unchanged");
        IList Fixture(params FieldInfo[] reads) {
            var list = (IList)Activator.CreateInstance(typeof(List<>).MakeGenericType(instructionType));
            foreach (var field in reads) {
                var item = Activator.CreateInstance(instructionType, true);
                opcodeField.SetValue(item, OpCodes.Ldsfld); operandField.SetValue(item, field); list.Add(item);
            }
            return list;
        }
        string Fails(IList list, MethodInfo method) {
            try { BetaCompatibilityCalls.ParallelRangeProbeFoldDetectionConstant(list, method); return null; } catch (InvalidOperationException ex) { return ex.Message; }
        }
        Check(Fails(Fixture(typeof(string).GetField("Empty")), detection)?.Contains("Uninspected static read") == true, "Bridge refuses another static read");
        Check(Fails(Fixture(four, four), detection)?.Contains("fold count changed: 2") == true, "Bridge refuses a second FourPiCubed read");
        Check(Fails(Fixture(), detection)?.Contains("fold count changed: 0") == true, "Bridge refuses a detection kernel without the read");
        var untouched = Fixture(typeof(string).GetField("Empty"));
        Check(Fails(untouched, horizon) == null && (OpCode)opcodeField.GetValue(untouched[0]) == OpCodes.Ldsfld, "Bridge leaves other methods untouched");
        Check(!BetaCompatibilityCalls.ParallelRangeProbeIsDetection(typeof(Math).GetMethod("Pow")) &&
            BetaCompatibilityCalls.ParallelRangeProbeIsDetection(detection), "Bridge matches the detection kernel structurally");

        // The worker kernels the adapted constructor built, against beta's
        // own horizon method and beta's detection formula over fixture inputs.
        var kernel = auxType.GetField("Kernel", all).GetValue(aux);
        var calculate = kernelType.GetMethod("Calculate", all);
        var numbersType = calculate.GetParameters()[0].ParameterType;
        object Numbers(int kind, float a, float b, float c, float d, double threshold) {
            object numbers = Activator.CreateInstance(numbersType);
            foreach (var (field, value) in new (string, object)[] { ("Kind", kind), ("A", a), ("B", b), ("C", c), ("D", d), ("Threshold", threshold) })
                numbersType.GetField(field, all).SetValue(numbers, value);
            return numbers;
        }
        int Bits(float value) => BitConverter.ToInt32(BitConverter.GetBytes(value), 0);
        var random = new Random(261026); int sensorChecks = 0;
        for (int n = 0; n < 4000; n++) {
            float a = (float)(random.NextDouble() * 5000), b = (float)(random.NextDouble() * 5000), c = (float)(random.NextDouble() * 3), d = (float)(random.NextDouble() * 20000);
            double threshold = Math.Pow(10, -16 + random.NextDouble() * 6);
            float worker = (float)calculate.Invoke(kernel, new[] { Numbers(2, a, b, c, d, threshold) });
            float native = (float)Math.Pow((double)(a * 1000f * (b * b) * (c * c) * d) / (threshold * 1000.0 * (double)fourValue), 0.25);
            if (Bits(worker) != Bits(native)) throw new Exception("Detection kernel differs at " + a + "," + b + "," + c + "," + d + "," + threshold);
            float h1 = (float)(random.NextDouble() * 30000), h2 = (float)(random.NextDouble() * 30000), refraction = (float)(random.NextDouble() * 2);
            bool flag = n % 2 == 1;
            float workerHorizon = (float)calculate.Invoke(kernel, new[] { Numbers(flag ? 1 : 0, h1, h2, refraction, 0f, 0.0) });
            float horizonValue = (float)horizon.Invoke(null, new object[] { h1, h2, flag, refraction });
            if (Bits(workerHorizon) != Bits(horizonValue)) throw new Exception("Horizon kernel differs at " + h1 + "," + h2 + "," + flag + "," + refraction);
            sensorChecks++;
        }
        Check(sensorChecks == 4000, "Worker detection and horizon kernels equal beta bit for bit on 4000 fixture inputs");
    }
}
