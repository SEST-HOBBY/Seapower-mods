using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using AnchorChain;
using HarmonyLib;
using Mono.Cecil;
using SeaPower;

static partial class BetaApiTests
{
    const BindingFlags TopoAll = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance;

    // R15: Topographic Map 1.7.0 (32b00107), the 21 November capture's globe
    // image. Only its metre-domain shallow-water constant is adapted; the
    // flat-map image is held by the native-member check (BetaApiTests.cs).
    static void R6_Topography170(R6Context context)
    {
        string source = Path.Combine(context.Workshop, "3826122523", "SeaPowerTopo.dll");
        byte[] original = File.ReadAllBytes(source);
        string hash; using (var sha = System.Security.Cryptography.SHA256.Create()) hash = BitConverter.ToString(sha.ComputeHash(original)).Replace("-", "").ToLowerInvariant();
        Check(hash == "32b00107bbdeb705c6bb91045b0bb5396f5815724a239b8c8f78026e1382b206", "Topography fixture is the inspected 1.7.0 author image");
        var messages = new List<string>();
        string prepared = BetaAssemblyPolicy.Prepare(source, context.Native, context.Cache, messages.Add);
        Check(prepared != null && prepared != source && File.Exists(prepared), "Globe Topography is admitted through a private adapter");
        Check(original.SequenceEqual(File.ReadAllBytes(source)), "Original globe Topography DLL retained byte for byte");
        // 1.7.0 adds one Assembly.Location read (Rats.Shared.ModState), which the
        // generic pass points at the original file.
        Check(messages.Single().Contains("locations=1, shallow-threshold=1"), "Topography audit covers exactly the inspected fix and the location bridge");
        using (var before = ModuleDefinition.ReadModule(source, new ReaderParameters { AssemblyResolver = context.Resolver }))
        using (var after = ModuleDefinition.ReadModule(prepared, new ReaderParameters { AssemblyResolver = context.Resolver })) {
            Check(TopoMissingOperands(before) == 0 && TopoMissingOperands(after) == 0, "Every Topography native operand resolves, before and after");
            int unchanged = 0;
            foreach (var t in Types(before.Types)) foreach (var method in t.Methods.Where(m => m.HasBody)) {
                if (t.FullName == "SeaPowerTopo.Render.Raster" && method.Name == "SimHeight") continue;
                var actual = after.GetType(t.FullName).Methods.Single(m => m.FullName == method.FullName);
                if (t.FullName == "Rats.Shared.ModState" && method.Name == "TickedInModManager") {
                    // The only other rewrite: its Assembly.Location read now asks
                    // BetaAssemblyPolicy.OriginalLocation; everything else is as written.
                    var was = TopoInstructions(method); var now = TopoInstructions(actual);
                    var changed = Enumerable.Range(0, was.Length).Where(n => n >= now.Length || was[n] != now[n]).ToArray();
                    Check(was.Length == now.Length && changed.Length == 1 && was[changed[0]].Contains("System.Reflection.Assembly::get_Location()") &&
                        now[changed[0]].StartsWith("call ") && now[changed[0]].Contains("AnchorChain.BetaAssemblyPolicy::OriginalLocation("),
                        "Topography's own-location read is the one bridged call: " + String.Join(" | ", changed.Select(n => was[n] + " -> " + (n < now.Length ? now[n] : "?"))));
                    unchanged++; continue;
                }
                Check(TopoInstructions(method).SequenceEqual(TopoInstructions(actual)), "Unchanged Topography behavior: " + method.FullName);
                unchanged++;
            }
            Console.WriteLine("Topography unchanged method bodies: " + unchanged);
        }
        var assembly = Assembly.LoadFile(prepared);
        Check(assembly.GetTypes().Length > 50, "Adapted Topography completes CLR type discovery, including renderer and ECS-visible fields");
        Check(BetaAssemblyPolicy.OriginalLocation(assembly) == source, "Topography original asset provenance retained");
        TopoBindings(assembly);
        TopoScaling(assembly);
        TopoRejectChangedShape(source, context, true);
    }

    static int TopoMissingOperands(ModuleDefinition module)
    {
        int missing = 0, inspected = 0;
        foreach (var type in Types(module.Types)) foreach (var method in type.Methods.Where(m => m.HasBody))
            foreach (var i in method.Body.Instructions) {
                if (i.Operand is not MemberReference member || member.DeclaringType?.Scope is not AssemblyNameReference scope || scope.Name != "Seapower-Scripts") continue;
                inspected++;
                if (member is MethodReference call && call.Resolve() == null) missing++;
                if (member is FieldReference field && field.Resolve() == null) missing++;
            }
        // 1.7.0 names 90 native operands (1.6.2: 96): it no longer uses the
        // native DEM cache handles (DEMHandle.Dispose x2, DEMHandle.get_Chunk,
        // TerrainLoader.IsDEMChunkAvailable/TryGetCached, UncompressedDEMChunk._data).
        Check(inspected >= 90, "Complete Topography native-operand scan: " + inspected);
        return missing;
    }

    // 1.7.0 moved the author's game reflection into Rats.Shared.GameReflection
    // and its hook lists into Rats.Shared.HookRegistry features declared by
    // MissionHooks.Declare and SeaPowerTopo.Hooks.Declare (SeaPowerTopo.GameApi
    // and Patches.GameHooks/MapHooks no longer exist).
    static void TopoBindings(Assembly assembly)
    {
        var api = assembly.GetType("Rats.Shared.GameReflection", true);
        var entry = api.GetField("LayerEntryType", TopoAll).GetValue(null) as Type;
        Check(entry != null, "Author map-layer entry type resolves on the current native image");
        Check(api.GetField("LayerCtor", TopoAll).GetValue(null) is ConstructorInfo ctor && ctor.GetParameters().Select(p => p.ParameterType)
                .SequenceEqual(new[] { typeof(SeapowerUI.MapDisplayState), entry.MakeByRefType(), typeof(bool) }),
            "Author map-layer reflection resolves the current internal constructor");
        // paletteDark is filled lazily by IsDark; check the same Getter call it makes.
        var getter = api.GetMethod("Getter", TopoAll).MakeGenericMethod(typeof(SeaPower.LiveMap.MapPalette), typeof(bool));
        Check(getter.Invoke(null, new object[] { "IsDark" }) is Delegate, "Author day/night palette getter binds on the current native image");
        int count = 0;
        foreach (var declare in new[] { assembly.GetType("Rats.Shared.MissionHooks", true).GetMethod("Declare", TopoAll), assembly.GetType("SeaPowerTopo.Hooks", true).GetMethod("Declare", TopoAll) }) {
            var il = PatchProcessor.GetOriginalInstructions(declare);
            for (int n = 0; n < il.Count; n++) {
                if (!(il[n].operand is MethodInfo hook && hook.DeclaringType.FullName == "Rats.Shared.Feature" && hook.Name == "Hook")) continue;
                Check(il[n - 7].opcode == OpCodes.Ldstr && il[n - 6].opcode == OpCodes.Ldstr, "Author hook target is named by string");
                string nativeType = (string)il[n - 7].operand, nativeMethod = (string)il[n - 6].operand;
                Type[] args = il[n - 5].opcode == OpCodes.Ldnull ? null : (il[n - 5].operand as FieldInfo)?.Name == "EmptyTypes" ? Type.EmptyTypes : throw new Exception("Unexpected Topography hook arguments: " + nativeType + "." + nativeMethod);
                Type targetType = typeof(ObjectBase).Assembly.GetType(nativeType, true);
                Check(AccessTools.Method(targetType, nativeMethod, args) != null, "Real Topography hook target resolves: " + nativeType + "." + nativeMethod);
                count++;
            }
        }
        Check(count == 3, "Both mission lifecycle targets and deferred map-render target checked without applying patches");
        var start = PatchProcessor.GetOriginalInstructions(assembly.GetType("SeaPowerTopo.Plugin", true).GetMethod("Start", TopoAll));
        Check(start.Any(i => i.operand is MethodInfo m && m.Name == "Start" && m.DeclaringType.FullName == "Rats.Shared.ModEntry" &&
                m.IsGenericMethod && m.GetGenericArguments()[0].FullName == "SeaPowerTopo.TopoHost"), "Author startup runs through ModEntry.Start<TopoHost>");
        var mapDeclare = PatchProcessor.GetOriginalInstructions(assembly.GetType("SeaPowerTopo.Hooks", true).GetMethod("Declare", TopoAll));
        int map = mapDeclare.FindIndex(i => i.opcode == OpCodes.Ldstr && (string)i.operand == "Map");
        var stage = assembly.GetType("Rats.Shared.HookStage", true);
        int afterNoesis = Convert.ToInt32(Enum.Parse(stage, "AfterNoesis"));
        // ModEntry.Starts (from Start) applies only HookStage.Load (0); the
        // AfterNoesis (1) map hook is applied from ModHost.PollStageTwo.
        Check(map >= 0 && mapDeclare[map + 1].opcode == OpCodes.Ldc_I4_1 && afterNoesis == 1 &&
            TopoAppliesStage(assembly.GetType("Rats.Shared.ModEntry", true).GetMethod("Starts", TopoAll), OpCodes.Ldc_I4_0) &&
            TopoAppliesStage(assembly.GetType("Rats.Shared.ModHost", true).GetMethod("PollStageTwo", TopoAll), OpCodes.Ldc_I4_1),
            "Author startup still defers the Noesis map patch (HookStage.AfterNoesis) until ModHost.PollStageTwo sees the UI");
    }

    static bool TopoAppliesStage(MethodInfo method, OpCode stage)
    {
        var il = PatchProcessor.GetOriginalInstructions(method);
        int apply = il.FindIndex(i => i.operand is MethodInfo m && m.Name == "ApplyStage" && m.DeclaringType.FullName == "Rats.Shared.HookRegistry");
        return apply > 0 && il[apply - 1].opcode == stage;
    }

    // Clone the ACTUAL pure arithmetic IL, avoiding game/Unity type initializers.
    // This compares the author's metre-domain raster math with native world-
    // unit scaling and the native metre/world conversion, not a duplicate formula.
    static DynamicMethod TopoArithmetic(MethodInfo source)
    {
        var dynamic = new DynamicMethod("TopoCheck_" + source.Name, source.ReturnType,
            source.GetParameters().Select(p => p.ParameterType).ToArray(), typeof(BetaApiTests), true);
        var il = dynamic.GetILGenerator();
        foreach (var local in source.GetMethodBody().LocalVariables) il.DeclareLocal(local.LocalType);
        foreach (var instruction in PatchProcessor.GetOriginalInstructions(source, il)) {
            Check(instruction.blocks.Count == 0, "Pure terrain arithmetic has no exception regions");
            foreach (var label in instruction.labels) il.MarkLabel(label);
            object operand = instruction.operand;
            if (operand == null) il.Emit(instruction.opcode);
            else if (operand is float f) il.Emit(instruction.opcode, f);
            else if (operand is double d) il.Emit(instruction.opcode, d);
            else if (operand is byte b) il.Emit(instruction.opcode, b);
            else if (operand is short s) il.Emit(instruction.opcode, s);
            else if (operand is int n) il.Emit(instruction.opcode, n);
            else if (operand is Label label) il.Emit(instruction.opcode, label);
            else throw new Exception("Unexpected terrain-arithmetic dependency: " + operand);
        }
        return dynamic;
    }

    static void TopoScaling(Assembly assembly)
    {
        var raster = assembly.GetType("SeaPowerTopo.Render.Raster", true).GetMethod("SimHeight", TopoAll);
        var sim = (Func<float,float,float,float>)TopoArithmetic(raster).CreateDelegate(typeof(Func<float,float,float,float>));
        var native = (Func<double,double>)TopoArithmetic(typeof(TerrainUtils).GetMethod("ScaleDEMHeight", new[] { typeof(double) })).CreateDelegate(typeof(Func<double,double>));
        var toWorld = (Func<float,float>)TopoArithmetic(typeof(Utils).GetMethod("heightInMeterToUnity", new[] { typeof(float) })).CreateDelegate(typeof(Func<float,float>));
        var toMetres = (Func<float,float>)TopoArithmetic(typeof(Utils).GetMethod("unityHeightToMeter", new[] { typeof(float) })).CreateDelegate(typeof(Func<float,float>));
        float maxError = 0;
        for (int value = short.MinValue; value <= short.MaxValue; value++) {
            float expected = toMetres((float)native(toWorld(value)));
            float actual = sim(value, 1f, 2f);
            float error = Math.Abs(actual - expected); maxError = Math.Max(maxError, error);
            if (error > Math.Max(0.01f, Math.Abs(expected) * 0.000001f)) throw new Exception("Topography/native height mismatch at DEM metre " + value + ": " + actual + " / " + expected);
        }
        Check(true, "All 65,536 signed DEM sample values match native terrain scaling in metres within float round-trip tolerance");
        foreach (float value in new[] { -50.0001f, -50f, -49.9999f, -49f, -48f, -47.999f, -1f, -0.001f, -0f, 0f, 0.001f, 1f, 500f, 8849f }) {
            float expected = toMetres((float)native(toWorld(value)));
            Check(Math.Abs(sim(value, 1f, 2f) - expected) <= Math.Max(0.01f, Math.Abs(expected) * 0.000001f),
                "Terrain/shoreline/aircraft altitude sample agrees with native units: " + value);
        }
        Check(sim(-49f, 1f, 2f) == -196f && sim(-50f, 1f, 2f) == -100f, "Current native 50 m shallow-water transition is retained");
        Console.WriteLine("Topography native scaling: all 65536 int16 samples; maximum float round-trip difference " + maxError + " m.");
    }

    static void TopoRejectChangedShape(string source, R6Context context, bool current)
    {
        var factory = typeof(BetaAssemblyPolicy).GetMethod("Topography170Adapter", BindingFlags.NonPublic | BindingFlags.Static);
        object adapter = factory.Invoke(null, null);
        var rewrite = (Delegate)adapter.GetType().GetField("RewriteMethod", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(adapter);
        Type scopeType = rewrite.Method.GetParameters()[0].ParameterType;
        foreach (bool constructor in new[] { true, false }) {
            using var module = ModuleDefinition.ReadModule(source);
            using var native = ModuleDefinition.ReadModule(context.Native);
            var method = module.GetType(constructor ? "SeaPowerTopo.Terrain.HeightReader" : "SeaPowerTopo.Render.Raster").Methods
                .Single(m => m.Name == (constructor ? ".ctor" : "SimHeight"));
            if (constructor) {
                if (current) method.Body.Instructions.RemoveAt(0);
                else method.Body.Instructions.Single(i => i.Offset == 0x003e).OpCode = Mono.Cecil.Cil.OpCodes.Nop;
            }
            else method.Body.Instructions.Single(i => i.Offset == 0x0011).Operand = -47f;
            object scope = Activator.CreateInstance(scopeType, true);
            scopeType.GetField("Module", TopoAll).SetValue(scope, module);
            scopeType.GetField("Native", TopoAll).SetValue(scope, native);
            scopeType.GetField("Count", TopoAll).SetValue(scope, (Action<string>)(_ => {}));
            bool rejected = false;
            try { rewrite.DynamicInvoke(scope, method.DeclaringType, method); }
            catch (TargetInvocationException ex) when (ex.InnerException is InvalidOperationException) { rejected = true; }
            Check(rejected, "Changed author Topography shape is rejected: " + (constructor ? "constructor" : "shoreline"));
        }
    }
}
