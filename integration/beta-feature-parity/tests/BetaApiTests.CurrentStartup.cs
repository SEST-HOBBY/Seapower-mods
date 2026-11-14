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
    const BindingFlags CurrentAll = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance;

    static Assembly CurrentPrepared(R6Context context, string name, out string prepared)
    {
        string source = Path.Combine(context.Workshop, "3784474738", name + ".dll");
        byte[] before = File.ReadAllBytes(source);
        prepared = BetaAssemblyPolicy.Prepare(source, context.Native, context.Cache, Console.WriteLine);
        Check(prepared != null && prepared != source && File.Exists(prepared), "Current " + name + " gets a private compatibility image");
        Check(before.SequenceEqual(File.ReadAllBytes(source)), "Current author bytes retained: " + name);
        var assembly = Assembly.LoadFile(prepared);
        Check(BetaAssemblyPolicy.OriginalLocation(assembly) == source, "Current asset/config provenance retained: " + name);
        return assembly;
    }

    static void CurrentInvoke(Type type, string method, params object[] arguments)
    {
        try { type.GetMethod(method, CurrentAll).Invoke(null, arguments); }
        catch (TargetInvocationException ex) { throw new Exception(type.FullName + "." + method + " failed: " + ex.InnerException); }
    }

    static void R6_TestRangeCurrent(R6Context context)
    {
        var assembly = CurrentPrepared(context, "TestRange", out string image);
        CurrentInvoke(assembly.GetType("TestRange.CountermeasureApi", true), "Validate");
        Check(true, "Current Test Range countermeasure reflection validator passes");
        CurrentInvoke(assembly.GetType("TestRange.ResultApi", true), "Validate");
        Check(true, "Current Test Range full result-hook validator passes, including new sensor signature");
        var native = typeof(ObjectBase).GetMethod("GetSensorRange", CurrentAll);
        Check(native.GetParameters().Length == 4 && native.GetParameters().Last().Name == "rangeOnly" &&
            native.GetParameters().Last().IsOptional && Equals(native.GetParameters().Last().DefaultValue, false),
            "Native range-only argument is optional false and does not change postfix arguments");
        var postfix = assembly.GetType("TestRange.ResultHooks", true).GetMethod("Sensor", CurrentAll);
        Check(postfix.GetParameters().Select(p => p.Name).SequenceEqual(new[] { "__instance", "__0", "__1", "__result" }),
            "Existing sensor postfix binds unchanged source, target, ammunition and result");
        Check(PatchProcessor.GetOriginalInstructions(postfix, (ILGenerator)null).Count > 0,
            "Real sensor result hook resolves under Mono");
    }

    static void R6_IdentifySender(R6Context context)
    {
        string source = Path.Combine(context.Workshop, "3790594162", "IdentifyExpanded.dll");
        string prepared = BetaAssemblyPolicy.Prepare(source, context.Native, context.Cache, Console.WriteLine);
        var assembly = Assembly.LoadFile(prepared);
        var sender = assembly.GetType("IdentifyExpanded.BroadcastService", true).GetMethod("FindSender", CurrentAll);
        var body = PatchProcessor.GetOriginalInstructions(sender, (ILGenerator)null);
        Check(body.Count(i => i.operand is MethodInfo m && m.Name == "IsInitializedPlayerUnit" && m.DeclaringType == typeof(BetaCompatibilityCalls)) == 3,
            "All three real Identify sender player checks use the taskforce-safe predicate");
        Check(!body.Any(i => i.operand is MethodInfo m && m.DeclaringType == typeof(ObjectBase) && m.Name == "get_IsPlayerUnit"),
            "Identify sender selection and its diagnostic cannot call the unsafe native getter directly");
    }

    static void R6_OptimalTargetCurrent(R6Context context)
    {
        var assembly = CurrentPrepared(context, "OptimalTargetDist", out string image);
        var shared = assembly.GetType("OptimalTargetDistAnchorChain.SharedLaunchGroups", true);
        var update = typeof(WeaponSystemLauncher).GetMethod("OnUpdate", CurrentAll);
        var original = PatchProcessor.GetOriginalInstructions(update, (ILGenerator)null);
        var rewritten = ((IEnumerable<CodeInstruction>)shared.GetMethod("Transpiler", CurrentAll).Invoke(null, new object[] { original })).ToList();
        Check(rewritten.Count(i => i.operand is MethodInfo m && m.Name == "GetKey" && m.DeclaringType == shared) == 7,
            "Author transpiler accepts and groups all seven actual shared-launch accesses, including failed launch");
        var aaw = assembly.GetType("OptimalTargetDistAnchorChain.AawInterception", true);
        CurrentInvoke(aaw, "Install");
        Check(!(bool)aaw.GetProperty("Ready", CurrentAll).GetValue(null),
            "Incompatible optional AAW feature stays uninstalled and advertises Ready=false");
        Check(PatchProcessor.GetOriginalInstructions(aaw.GetMethod("Install", CurrentAll), (ILGenerator)null)
            .All(i => i.opcode == OpCodes.Ret), "Held AAW initializer cannot install a partial patch or report an exception");
        CurrentStartupHolds(context);
        NativePeDiscovery(context);
    }

    // R14: run every Alpine-family author's own build-contract guard against
    // the captured 0.9.2 game, the way the author's plugin calls it, and
    // require SEST's pre-load decision to match the author's verdict: an
    // image whose guard rejects this game is held before registration, and
    // an image whose guard accepts it is admitted unchanged.
    static void CurrentStartupHolds(R6Context context)
    {
        int rejected = 0, accepted = 0;
        foreach (string source in Directory.GetFiles(context.Workshop, "*.dll", SearchOption.AllDirectories).OrderBy(x => x, StringComparer.Ordinal)) {
            if (source.Contains(Path.DirectorySeparatorChar + "backups" + Path.DirectorySeparatorChar)) continue;
            string relative = source.Substring(context.Workshop.Length + 1);
            MethodReference expectedSource = null;
            using (var metadata = ModuleDefinition.ReadModule(source)) {
                if (!metadata.GetTypes().Any(t => t.FullName == "AlpineRuntimeInternal.BuildContract")) continue;
                foreach (var type in metadata.GetTypes()) foreach (var method in type.Methods.Where(m => m.HasBody))
                    foreach (var instruction in method.Body.Instructions)
                        if (instruction.Operand is MethodReference call && call.DeclaringType.FullName == "AlpineRuntimeInternal.BuildContract" &&
                            call.Name == "A" && call.Parameters.Count == 4 &&
                            instruction.Previous?.Previous?.Operand is MethodReference text && !text.HasParameters && text.ReturnType.FullName == "System.String")
                            expectedSource = text;
            }
            Check(expectedSource != null, "Author build guard call site found: " + relative);
            byte[] before = File.ReadAllBytes(source);
            var messages = new List<string>();
            string prepared = BetaAssemblyPolicy.Prepare(source, context.Native, context.Cache, messages.Add);
            Check(before.SequenceEqual(File.ReadAllBytes(source)), "Author image retained: " + relative);
            // Evaluate the guard in the test process only; SEST's loader never
            // runs author code to make this decision.
            var assembly = Assembly.LoadFrom(source);
            string expected = (string)assembly.GetType(expectedSource.DeclaringType.FullName.Replace('/', '+'), true)
                .GetMethod(expectedSource.Name, CurrentAll).Invoke(null, null);
            var guard = assembly.GetType("AlpineRuntimeInternal.BuildContract", true).GetMethod("A", CurrentAll, null,
                new[] { typeof(Assembly), typeof(string), typeof(string), typeof(string).MakeByRefType() }, null);
            object[] args = { assembly, context.Native, expected, null };
            string verdict = guard.Invoke(null, args).ToString();
            Console.WriteLine("Author guard " + relative + ": " + verdict + (string.IsNullOrEmpty((string)args[3]) ? "" : " (" + args[3] + ")"));
            if (verdict == "ExactBuild" || verdict == "UnchangedContract") {
                accepted++;
                Check(prepared == source && messages.Count == 0, "Author guard accepts 0.9.2, so SEST admits the image unchanged: " + relative);
            } else {
                rejected++;
                Check(prepared == null && messages.Count == 1 && messages[0].Contains("before CLR load") && messages[0].Contains("Data retained"),
                    "Author guard rejects 0.9.2 (" + verdict + "), so SEST holds the image before registration: " + relative);
            }
        }
        Check(rejected == 6 && accepted == 10, "Captured Alpine-family set: 6 author guards reject 0.9.2 and 10 accept it (actual " + rejected + "/" + accepted + ")");
    }

    static void NativePeDiscovery(R6Context context)
    {
        foreach (bool pe64 in new[] { false, true }) {
            string path = Path.Combine(context.Cache, pe64 ? "native64.dll" : "native32.dll");
            byte[] header = new byte[512];
            using (var stream = new MemoryStream(header)) using (var w = new BinaryWriter(stream)) {
                w.Write((ushort)0x5a4d); stream.Position = 0x3c; w.Write(0x80);
                stream.Position = 0x80; w.Write(0x00004550);
                stream.Position = 0x80 + 20; w.Write((ushort)(pe64 ? 240 : 224));
                stream.Position = 0x80 + 24; w.Write((ushort)(pe64 ? 0x20b : 0x10b));
                stream.Position = 0x80 + 24 + (pe64 ? 108 : 92); w.Write(16);
            }
            File.WriteAllBytes(path, header);
            var messages = new List<string>();
            Check(BetaAssemblyPolicy.Prepare(path, context.Native, context.Cache, messages.Add) == null,
                "Native PE helper excluded before Cecil metadata discovery: " + pe64);
            Check(messages.Single().Contains("native library") && header.SequenceEqual(File.ReadAllBytes(path)),
                "Native helper retained with a clear discovery status: " + pe64);
        }
        string corrupt = Path.Combine(context.Cache, "corrupt-managed.dll");
        File.WriteAllText(corrupt, "This is not a valid DLL");
        bool rejected = false;
        try { BetaAssemblyPolicy.Prepare(corrupt, context.Native, context.Cache, Console.WriteLine); }
        catch (BadImageFormatException) { rejected = true; }
        Check(rejected, "Malformed input still raises the existing metadata error instead of silently passing as native");
    }
}
