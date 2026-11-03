using System;
using System.IO;
using System.Linq;
using System.Reflection;
using AnchorChain;
using Mono.Cecil;
using HarmonyLib;
using System.Reflection.Emit;

static class AssemblyPolicyTests
{
    static int checks;
    static void Check(bool ok, string why) { checks++; if (!ok) throw new Exception(why); }
    static void Main(string[] args)
    {
        string workshop = Path.GetFullPath(args[0]), native = Path.GetFullPath(args[1]);
        string references = Path.GetDirectoryName(native);
        AppDomain.CurrentDomain.AssemblyResolve += (s,e) => {
            string path = Path.Combine(references, new AssemblyName(e.Name).Name + ".dll");
            return File.Exists(path) ? Assembly.LoadFrom(path) : null;
        };
        string cache = Path.Combine(Path.GetTempPath(), "SEST-Policy-" + Guid.NewGuid().ToString("N"));
        string identify = Path.Combine(workshop, "3790594162/IdentifyExpanded.dll");
        string extended = Path.Combine(workshop, "3784474738/ExtendedGuidance.dll");
        byte[] original = File.ReadAllBytes(identify);
        try {
            var messages = new System.Collections.Generic.List<string>();
            string blocked = BetaAssemblyPolicy.Prepare(extended, native, cache, messages.Add);
            Check(blocked == null, "Captured ECS-blocking ExtendedGuidance is rejected before CLR load");
            Check(!AppDomain.CurrentDomain.GetAssemblies().Any(x => x.GetName().Name == "ExtendedGuidance"), "Rejected ExtendedGuidance never entered the CLR assembly set");
            Check(messages.Any(x => x.Contains("SensorDistanceData")), "Block explains the captured field-layout failure");
            using (var module = ModuleDefinition.ReadModule(extended)) using (var game = ModuleDefinition.ReadModule(native)) {
                var inspect = typeof(BetaAssemblyPolicy).GetMethod("InvalidNativeFields", BindingFlags.Static | BindingFlags.NonPublic);
                var errors = (System.Collections.Generic.List<string>)inspect.Invoke(null, new object[] { module, game });
                foreach (var error in errors) Console.WriteLine("LAYOUT " + error);
                Check(errors.Any(x => x.Contains("RangeEntry.Value")), "Generic layout scan also finds the actual bad RangeEntry field");
            }
            string adapted = BetaAssemblyPolicy.Prepare(identify, native, cache, messages.Add);
            Check(adapted != identify && File.Exists(adapted), "Adapted Identify image is generated in a separate private cache");
            Check(File.ReadAllBytes(identify).SequenceEqual(original), "Workshop Identify DLL remains byte identical");
            var loaded = Assembly.LoadFile(adapted);
            Check(BetaAssemblyPolicy.OriginalLocation(loaded) == identify, "Adapted image retains Workshop asset provenance");
            var type = loaded.GetType("IdentifyExpanded.RammingService", true);
            var tick = type.GetMethod("Tick", BindingFlags.Public | BindingFlags.Static);
            var body = PatchProcessor.GetOriginalInstructions(tick, (ILGenerator)null);
            Check(body.Count(x => (x.operand as MethodInfo)?.Name == "HeadingToPosition") == 2, "Both real ramming bearing calls resolve to beta HeadingToPosition");
            Check(body.All(x => (x.operand as MethodInfo)?.Name != "CourseTo"), "The missing CourseTo member is absent from rewritten ramming IL");
            // No jobs exist, so the real adapted method can return before any
            // Unity native call. This reproduced the original eager-JIT failure.
            tick.Invoke(null, null);
            Check(true, "Real adapted RammingService.Tick JITs and runs with no jobs");
            Check(messages.Any(x => x.Contains("ADAPTED Identify")), "Geometry adaptation is reported");
            var origin = new SeaPower.GeoPosition(0, 0, 0);
            Check(Math.Abs(origin.HeadingToPosition(new SeaPower.GeoPosition(0, 1, 0)) - 90) < 0.01, "Beta bearing points east");
            Check(Math.Abs(origin.HeadingToPosition(new SeaPower.GeoPosition(1, 0, 0))) < 0.01, "Beta bearing points north");
            var west = new SeaPower.GeoPosition(0, 179, 0);
            Check(Math.Abs(west.HeadingToPosition(new SeaPower.GeoPosition(0, -179, 0)) - 90) < 0.01, "Beta bearing wraps the date line");
            int inspected=0, allowed=0;
            foreach (string dll in Directory.GetFiles(workshop, "*.dll", SearchOption.AllDirectories)) {
                if (String.Equals(dll, identify, StringComparison.OrdinalIgnoreCase)) continue;
                var prepared=BetaAssemblyPolicy.Prepare(dll, native, cache, messages.Add);
                inspected++; if (prepared != null) allowed++;
            }
            Check(inspected > 60 && allowed > 20, "Complete captured managed Workshop set passes metadata preparation without broad exclusion");
            Check(messages.Any(x => x.Contains("OspreyDeckOps")), "Dependent Osprey deck code is rejected before loading its quarantined dependency");
            Console.WriteLine("Metadata discovery: " + inspected + " other DLLs inspected, " + allowed + " plugin assemblies admitted; no plugin entrypoints executed.");
            Console.WriteLine("Assembly pre-load/Identify beta geometry checks passed: " + checks + "; no Unity gameplay.");
        } finally { if (Directory.Exists(cache)) Directory.Delete(cache, true); }
    }
}
