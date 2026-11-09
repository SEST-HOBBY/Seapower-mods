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

    static void R6_MissileControlCurrent(R6Context context)
    {
        var assembly = CurrentPrepared(context, "MissileControlMod", out string image);
        var compatibility = assembly.GetType("MissileControlMod.Compatibility", true);
        // Runs the author's complete real startup dry run, not a reimplementation
        // of its count check. It installs no Harmony patch and starts no Unity object.
        CurrentInvoke(compatibility, "ValidateGame");
        Check(true, "Missile Control 0.1.18 full author startup validator passes");
        var hooks = assembly.GetType("MissileControlMod.Hooks", true);
        var course = typeof(WeaponBase).GetMethod("setCourseTowardsPosition", CurrentAll);
        var source = PatchProcessor.GetOriginalInstructions(course, (ILGenerator)null);
        var rewritten = ((IEnumerable<CodeInstruction>)hooks.GetMethod("SteeringLimits", CurrentAll).Invoke(null, new object[] { source })).ToList();
        Check(rewritten.Count(i => i.operand is MethodInfo m && m.Name == "EffectiveGLimitedRate") == 1,
            "Actual current steering transpiler replaces exactly one native G-limited helper");
        Check(rewritten.Count(i => i.operand is MethodInfo m && m.Name == "EffectiveG") == 1,
            "Actual far-field max-G site receives the author's effective-G behavior");
        Check(rewritten.Count(i => i.operand is MethodInfo m && m.Name == "FarFieldTurnRate") == 1,
            "Native far-field turn calculation remains in the real instruction stream");
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

    static void CurrentStartupHolds(R6Context context)
    {
        string[] held = {
            "3820576916/AlpineExteriorCameras.dll", "3819522350/AlpineExteriorCameras.dll",
            "3819522350/K5KrakenContactStrike.dll", "3804868806/XQ58Shadow.dll",
            "3804868806/AlpineSeaPower.dll", "3796349767/AlpineSeaPower.dll",
            "3810611344/BellSystemsFixtureTilt.dll",
            "3810611344/MV75CrewEscape.dll",
        };
        foreach (string relative in held) {
            string source = Path.Combine(context.Workshop, relative);
            byte[] before = File.ReadAllBytes(source);
            var messages = new List<string>();
            Check(BetaAssemblyPolicy.Prepare(source, context.Native, context.Cache, messages.Add) == null,
                "Captured rejected image held before registration: " + relative);
            Check(before.SequenceEqual(File.ReadAllBytes(source)), "Held author image retained: " + relative);
            Check(messages.Count == 1 && messages[0].Contains("before CLR load") && messages[0].Contains("Data retained"),
                "Held image explains feature availability: " + relative);
            using var metadata = ModuleDefinition.ReadModule(source);
            Check(!AppDomain.CurrentDomain.GetAssemblies().Any(a => a.GetName().Name == metadata.Assembly.Name.Name),
                "Rejected image never entered CLR: " + relative);
        }
        CurrentEc2Startup(context);
    }

    static void CurrentEc2Startup(R6Context context)
    {
        string source = Path.Combine(context.Workshop, "3813033771", "EC2CommsJamming.dll");
        byte[] before = File.ReadAllBytes(source);
        string hash;
        using (var sha = System.Security.Cryptography.SHA256.Create())
            hash = BitConverter.ToString(sha.ComputeHash(before)).Replace("-", "").ToLowerInvariant();
        var messages = new List<string>();
        string prepared = BetaAssemblyPolicy.Prepare(source, context.Native, context.Cache, messages.Add);
        if (hash == "f933cec252c0c2ba99192e3f14b0f333d11456005c496a49d8b532d3e3187f81")
        {
            Check(prepared == null && messages.Single().Contains("Data retained"), "Earlier rejected EC-2 image remains held before registration");
            Check(before.SequenceEqual(File.ReadAllBytes(source)), "Earlier EC-2 author bytes retained");
            return;
        }
        Check(hash == "b6e7f8e705106b948588b6ed1a9e3d19e48e30d74d5b7fef431d2a9f6401d22c", "Current EC-2 image is the inspected 22:57 capture");
        Check(prepared == source && before.SequenceEqual(File.ReadAllBytes(source)), "Updated EC-2 is admitted without a private rewrite or author-file change");
        // Invoke only the author's pure build-contract validator, never its
        // plugin entrypoint or Harmony installers. The new image accepts this
        // native build itself; the old exact-hash hold must not block it.
        var assembly = Assembly.LoadFrom(source);
        var strings = assembly.GetType("<PrivateImplementationDetails>{069DC387-A350-4807-AFC1-E74C900DD3F4}.1FB7A22C-FA48-414E-8637-E3EC1E425B87", true);
        string expected = (string)strings.GetMethod("Y", CurrentAll).Invoke(null, null);
        var guard = assembly.GetType("AlpineRuntimeInternal.BuildContract", true).GetMethod("A", CurrentAll, null,
            new[] { typeof(Assembly), typeof(string), typeof(string), typeof(string).MakeByRefType() }, null);
        object[] args = { assembly, context.Native, expected, null };
        var verdict = guard.Invoke(null, args);
        Check(verdict.ToString() == "ExactBuild", "Updated EC-2's actual author guard accepts the captured native game exactly");
        Check(string.IsNullOrEmpty((string)args[3]), "Updated EC-2 author validator reports no contract rejection");
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
