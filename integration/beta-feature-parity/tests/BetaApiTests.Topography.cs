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

    static void R6_Topography(R6Context context)
    {
        string source = Path.Combine(context.Workshop, "3826122523", "SeaPowerTopo.dll");
        string flat = Path.Combine(context.Workshop, "3826122523", "SeaPowerTopoFlat.dll");
        byte[] original = File.ReadAllBytes(source), flatOriginal = File.ReadAllBytes(flat);
        var messages = new List<string>();
        string prepared = BetaAssemblyPolicy.Prepare(source, context.Native, context.Cache, messages.Add);
        Check(prepared != null && prepared != source && File.Exists(prepared), "Globe Topography is admitted through a private adapter");
        Check(original.SequenceEqual(File.ReadAllBytes(source)), "Original globe Topography DLL retained byte for byte");
        Check(messages.Single().Contains("depth-scale=2, land-scale=2, shallow-threshold=1"), "Topography audit covers exactly the inspected fixes");
        Check(BetaAssemblyPolicy.Prepare(flat, context.Native, context.Cache, Console.WriteLine) == null,
            "Flat-map-only Topography remains excluded on the globe game before CLR load");
        Check(flatOriginal.SequenceEqual(File.ReadAllBytes(flat)), "Flat-map author DLL retained");
        Check(!AppDomain.CurrentDomain.GetAssemblies().Any(a => a.GetName().Name == "SeaPowerTopoFlat"), "Flat-map image did not enter CLR");
        using (var before = ModuleDefinition.ReadModule(source, new ReaderParameters { AssemblyResolver = context.Resolver }))
        using (var after = ModuleDefinition.ReadModule(prepared, new ReaderParameters { AssemblyResolver = context.Resolver })) {
            Check(TopoMissingOperands(before) == 4, "Captured globe DLL reproduces exactly four removed native field reads");
            Check(TopoMissingOperands(after) == 0, "Every adapted Topography native operand resolves");
            var oldCtor = before.GetType("SeaPowerTopo.Terrain.HeightReader").Methods.Single(m => m.IsConstructor);
            var newCtor = after.GetType("SeaPowerTopo.Terrain.HeightReader").Methods.Single(m => m.IsConstructor);
            Check(newCtor.Body.Instructions.Count == oldCtor.Body.Instructions.Count, "Height-reader control flow and allocation count retained");
            foreach (string setting in new[] { "_heightMultiplier", "_underWaterDepthFactor" })
                Check(!newCtor.Body.Instructions.Any(i => i.Operand is FieldReference f && f.Name == setting), "Retired setting is absent from adapted constructor: " + setting);
            // Byte-level method semantics elsewhere are retained (branch encoding
            // is normalized by the loader, so compare operands and branch targets).
            int unchanged = 0;
            foreach (var t in Types(before.Types)) foreach (var method in t.Methods.Where(m => m.HasBody)) {
                if ((t.FullName == "SeaPowerTopo.Terrain.HeightReader" && method.Name == ".ctor") ||
                    (t.FullName == "SeaPowerTopo.Render.Raster" && method.Name == "SimHeight")) continue;
                var actual = after.GetType(t.FullName).Methods.Single(m => m.FullName == method.FullName);
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
        TopoRejectChangedShape(source, context);
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
        Check(inspected >= 96, "Complete Topography native-operand scan: " + inspected);
        return missing;
    }

    static string[] TopoInstructions(MethodDefinition method)
        => method.Body.Instructions.Select(i => {
            string op = i.OpCode.Name.EndsWith(".s", StringComparison.Ordinal) && i.Operand is Mono.Cecil.Cil.Instruction
                ? i.OpCode.Name.Substring(0, i.OpCode.Name.Length - 2) : i.OpCode.Name;
            string operand = i.Operand is Mono.Cecil.Cil.Instruction target ? "target:" + method.Body.Instructions.IndexOf(target) :
                i.Operand is Mono.Cecil.Cil.Instruction[] targets ? String.Join(",", targets.Select(t => method.Body.Instructions.IndexOf(t))) :
                i.Operand?.ToString();
            return op + " " + operand;
        }).ToArray();

    static void TopoBindings(Assembly assembly)
    {
        var api = assembly.GetType("SeaPowerTopo.GameApi", true);
        Check(api.GetField("LayerCtor", TopoAll).GetValue(null) is ConstructorInfo ctor && ctor.GetParameters().Length == 3,
            "Author map-layer reflection resolves the current internal constructor");
        Check(api.GetField("PaletteDark", TopoAll).GetValue(null) is Delegate, "Author day/night palette getter binds on the current native image");
        var patches = assembly.GetType("SeaPowerTopo.Patches", true);
        int count = 0;
        foreach (string list in new[] { "GameHooks", "MapHooks" }) foreach (object hook in (Array)patches.GetField(list, TopoAll).GetValue(null)) {
            var type = hook.GetType();
            string nativeType = (string)type.GetField("Type", TopoAll).GetValue(hook);
            string nativeMethod = (string)type.GetField("Method", TopoAll).GetValue(hook);
            var args = (Type[])type.GetField("Args", TopoAll).GetValue(hook);
            Type targetType = typeof(ObjectBase).Assembly.GetType(nativeType, true);
            Check(AccessTools.Method(targetType, nativeMethod, args) != null, "Real Topography hook target resolves: " + nativeType + "." + nativeMethod);
            count++;
        }
        Check(count == 3, "Both mission lifecycle targets and deferred map-render target checked without applying patches");
        var start = assembly.GetType("SeaPowerTopo.Plugin", true).GetMethod("Start", TopoAll);
        var startIl = PatchProcessor.GetOriginalInstructions(start);
        Check(startIl.Any(i => i.operand is MethodInfo m && m.Name == "ApplyGameHooks") &&
            !startIl.Any(i => i.operand is MethodInfo m && m.Name == "ApplyMapHooks"), "Author startup still defers the Noesis map patch until UI initialization");
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

    static void TopoRejectChangedShape(string source, R6Context context)
    {
        var factory = typeof(BetaAssemblyPolicy).GetMethod("TopographyAdapter", BindingFlags.NonPublic | BindingFlags.Static);
        object adapter = factory.Invoke(null, null);
        var rewrite = (Delegate)adapter.GetType().GetField("RewriteMethod", BindingFlags.NonPublic | BindingFlags.Instance).GetValue(adapter);
        Type scopeType = rewrite.Method.GetParameters()[0].ParameterType;
        foreach (bool constructor in new[] { true, false }) {
            using var module = ModuleDefinition.ReadModule(source);
            using var native = ModuleDefinition.ReadModule(context.Native);
            var method = module.GetType(constructor ? "SeaPowerTopo.Terrain.HeightReader" : "SeaPowerTopo.Render.Raster").Methods
                .Single(m => m.Name == (constructor ? ".ctor" : "SimHeight"));
            if (constructor) method.Body.Instructions.Single(i => i.Offset == 0x003e).OpCode = Mono.Cecil.Cil.OpCodes.Nop;
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
