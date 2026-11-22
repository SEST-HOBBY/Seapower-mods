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
        Check(true, "Missile Control 0.1.18.1 full author startup validator passes on 0.9.3 (it disables itself without the steering-g-load fix)");
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
        Check(body.Count(i => i.operand is MethodInfo m && m.Name == "IsPlayerUnit" && m.DeclaringType.FullName == "IdentifyExpanded.TaskforceUtil") == 3,
            "All three Identify sender checks use the author’s taskforce-safe predicate");
        var guard = assembly.GetType("IdentifyExpanded.TaskforceUtil", true).GetMethod("IsPlayerUnit", CurrentAll);
        var guardCalls = PatchProcessor.GetOriginalInstructions(guard, (ILGenerator)null);
        Check(guardCalls.Any(i => i.operand is MethodInfo m && m.Name == "GetTaskforce") &&
            !guardCalls.Any(i => i.operand is MethodInfo m && m.Name == "get_IsPlayerUnit"), "Identify safely obtains the taskforce before evaluating ownership");
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
        CurrentGameHashGuards(context);
        NativePeDiscovery(context);
    }

    // R14, R15: run every Alpine-family author's own build-contract guard against
    // the captured game, the way the author's plugin calls it, and
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
            // Workshop folders can also contain native helpers such as version.dll.
            // The full capture scan still passes each file through the loader policy.
            ModuleDefinition metadata;
            try { metadata = ModuleDefinition.ReadModule(source); }
            catch (BadImageFormatException) when ((bool)typeof(BetaAssemblyPolicy)
                .GetMethod("IsNativePeLibrary", CurrentAll).Invoke(null, new object[] { source })) { continue; }
            using (metadata) {
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
                Check(prepared == source && messages.Count == 0, "Author guard accepts 0.9.3, so SEST admits the image unchanged: " + relative);
            } else {
                rejected++;
                Check(prepared == null && messages.Count == 1 && messages[0].Contains("before CLR load") && messages[0].Contains("Data retained"),
                    "Author guard rejects 0.9.3 (" + verdict + "), so SEST holds the image before registration: " + relative);
            }
        }
        Check(rejected == 6 && accepted == 10, "Captured Alpine-family set: 6 author guards reject 0.9.3 and 10 accept it (actual " + rejected + "/" + accepted + ")");
    }

    // R14: Exterior Cameras, XQ-58 Shadow and MV-75 Crew Escape guard with a
    // fixed list of accepted Seapower-Scripts.dll SHA-256 values instead of a
    // build contract. Read each author's own list from its image, compare it
    // with the captured game and require SEST's pre-load decision to match.
    static void CurrentGameHashGuards(R6Context context)
    {
        string game;
        using (var stream = File.OpenRead(context.Native)) using (var sha = System.Security.Cryptography.SHA256.Create())
            game = BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "");
        var rejected = new List<string>();
        foreach (string source in Directory.GetFiles(context.Workshop, "*.dll", SearchOption.AllDirectories).OrderBy(x => x, StringComparer.Ordinal)) {
            if (source.Contains(Path.DirectorySeparatorChar + "backups" + Path.DirectorySeparatorChar)) continue;
            if (source.StartsWith(Path.Combine(context.Workshop, "3812461539") + Path.DirectorySeparatorChar, StringComparison.Ordinal)) continue;
            string relative = source.Substring(context.Workshop.Length + 1).Replace('\\', '/');
            var texts = new List<int>(); var lists = new List<int>();
            try {
                using (var metadata = ModuleDefinition.ReadModule(source)) {
                    if (metadata.GetTypes().Any(t => t.FullName == "AlpineRuntimeInternal.BuildContract")) continue;
                    foreach (var type in metadata.GetTypes()) foreach (var method in type.Methods.Where(m => m.HasBody)) {
                        var body = method.Body.Instructions;
                        if (!body.Any(i => i.Operand is MethodReference m && m.Name == "ComputeHash") ||
                            !body.Any(i => i.Operand is TypeReference t && t.Scope is AssemblyNameReference s && s.Name == "Seapower-Scripts" &&
                                i.Next?.Next?.Next?.Operand is MethodReference l && l.Name == "get_Location")) continue;
                        foreach (var i in body) {
                            if (i.Operand is MethodReference compare && compare.DeclaringType.FullName == "System.String" &&
                                (compare.Name == "op_Equality" || compare.Name == "op_Inequality") &&
                                i.Previous?.Operand is MethodReference text && !text.HasThis && !text.HasParameters && text.ReturnType.FullName == "System.String")
                                texts.Add(text.Resolve().MetadataToken.ToInt32());
                            if (i.Operand is MethodReference index && index.Name == "IndexOf" && index.DeclaringType.FullName == "System.Array" &&
                                i.Previous?.Previous?.Operand is FieldReference list && list.FieldType.FullName == "System.String[]")
                                lists.Add(list.Resolve().MetadataToken.ToInt32());
                        }
                    }
                }
            } catch (BadImageFormatException) { continue; }
            if (texts.Count + lists.Count == 0) continue;
            byte[] before = File.ReadAllBytes(source);
            var messages = new List<string>();
            string prepared = BetaAssemblyPolicy.Prepare(source, context.Native, context.Cache, messages.Add);
            Check(before.SequenceEqual(File.ReadAllBytes(source)), "Author image retained: " + relative);
            // Read the author's list in the test process only; SEST's loader
            // never runs author code to make this decision.
            var module = Assembly.LoadFrom(source).ManifestModule;
            var allowed = texts.Select(t => (string)module.ResolveMethod(t).Invoke(null, null))
                .Concat(lists.SelectMany(f => (string[])module.ResolveField(f).GetValue(null)))
                .Where(h => h != null && h.Length == 64).Distinct(StringComparer.OrdinalIgnoreCase).ToList();
            bool accepts = allowed.Contains(game, StringComparer.OrdinalIgnoreCase);
            Console.WriteLine("Author game-hash guard " + relative + ": " + allowed.Count + " accepted builds; " + (accepts ? "accepts" : "rejects") + " 0.9.3");
            Check(allowed.Count > 0, "Author game-hash list read: " + relative);
            if (accepts) Check(prepared == source && messages.Count == 0, "Author game-hash guard accepts 0.9.3, so SEST admits the image unchanged: " + relative);
            else {
                rejected.Add(relative);
                Check(prepared == null && messages.Count == 1 && messages[0].StartsWith("SKIPPED before CLR load: ") && messages[0].Contains("Data retained"),
                    "Author game-hash guard rejects 0.9.3, so SEST holds the image before registration: " + relative);
            }
        }
        Check(rejected.SequenceEqual(new[] { "3804868806/XQ58Shadow.dll", "3810611344/MV75CrewEscape.dll",
            "3819522350/AlpineExteriorCameras.dll", "3820576916/AlpineExteriorCameras.dll" }),
            "Captured game-hash guards: Exterior Cameras (two items), XQ-58 Shadow and MV-75 Crew Escape reject 0.9.3 (actual: " + String.Join(", ", rejected) + ")");
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
