// R6: TestRange 0.2.3 (Euromod Anchor Chain Expansion Pack, Workshop
// 3784474738). Metadata, reflection and bridge checks only: no Harmony patch
// is applied and no Unity gameplay runs. The only author code invoked is the
// author's own reflection validators (CountermeasureApi.Validate and
// Api.Require), which look members up and build a list; Api.Validate as a whole
// is not called because BindClock binds GameTime.
using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.Serialization;
using System.Security.Cryptography;
using AnchorChain;
using HarmonyLib;
using Mono.Cecil;
using Mono.Cecil.Cil;
using SeaPower;

static partial class BetaApiTests
{
    const string TestRangeHash = "672e34d8c946b9ca7086d10462d2b7c7be3f96260bd5ee08d2851020a5810491";
    const string TestRangeAudit = "jam-hook=1, jam-legacy=1, jam-standoff=1, launch-blocked-result=1, launch-result=1, locations=2, scan-files=1, sensor-data=1";
    const BindingFlags TestRangeAll = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance;

    static void R6_TestRange(R6Context context)
    {
        string source = Path.Combine(context.Workshop, "3784474738", "TestRange.dll");
        byte[] bytes = File.ReadAllBytes(source);
        Check(TestRangeSha(bytes) == TestRangeHash, "TestRange fixture is the pinned author image 672e34d8");
        var log = new List<string>();
        string adapted = BetaAssemblyPolicy.Prepare(source, context.Native, context.Cache, log.Add);
        foreach (string line in log) Console.WriteLine(line);
        Check(adapted != null && adapted != source && File.Exists(adapted), "TestRange private API image generated");
        Check(bytes.SequenceEqual(File.ReadAllBytes(source)), "TestRange author bytes retained");
        Check(log.Count == 1 && log[0] == "ADAPTED TestRange in private cache: " + TestRangeAudit + "; original Workshop DLL and asset paths preserved.",
            "TestRange audit is logged exactly");
        Check(BetaAssemblyPolicy.AdapterNames().Count(n => n == "TestRange") == 1, "TestRange adapter is registered once");

        TestRangeWrittenIl(adapted, context.Resolver);
        TestRangeCecilOperands(adapted, context.Resolver);

        var loaded = Assembly.LoadFile(adapted);
        Check(BetaAssemblyPolicy.OriginalLocation(loaded) == source, "TestRange private image reports its Workshop location");
        TestRangeMonoTokens(loaded, adapted, context.Resolver, 0, "adapted image");
        // The original image fails under Mono on exactly the two members the
        // captured beta JIT failures name; Cecil's Resolve accepts the second.
        TestRangeMonoTokens(Assembly.Load(bytes), source, context.Resolver, 2, "original image");

        TestRangeValidators(loaded);
        TestRangeBridges();
        TestRangeNativeShapes();
        TestRangeCatalogFixture(context.Cache);
    }

    static string TestRangeSha(byte[] bytes)
    {
        using var sha = SHA256.Create();
        return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant();
    }

    static string TestRangeIl(Instruction instruction)
    {
        string operand = instruction.Operand switch {
            null => null,
            Instruction target => "IL_" + target.Offset.ToString("x4"),
            MemberReference member => member.FullName,
            IFormattable number => number.ToString(null, CultureInfo.InvariantCulture),
            var other => other.ToString(),
        };
        return operand == null ? instruction.OpCode.Name : instruction.OpCode.Name + " " + operand;
    }

    static bool TestRangeHasRun(MethodDefinition method, params string[] run)
    {
        var text = method.Body.Instructions.Select(TestRangeIl).ToList();
        for (int i = 0; i + run.Length <= text.Count; i++)
            if (text.Skip(i).Take(run.Length).SequenceEqual(run)) return true;
        return false;
    }

    // Each rewrite's IL, read back from the written private image.
    static void TestRangeWrittenIl(string adapted, DefaultAssemblyResolver resolver)
    {
        const string handle = "call System.Type System.Type::GetTypeFromHandle(System.RuntimeTypeHandle)";
        using var module = ModuleDefinition.ReadModule(adapted, new ReaderParameters { AssemblyResolver = resolver });
        var validate = module.GetType("TestRange.CountermeasureApi").Methods.Single(m => m.Name == "Validate");
        Check(TestRangeHasRun(validate, "ldtoken SeaPower.ECM", handle, "ldstr StandoffNoiseFactor", "ldtoken System.Double", handle, "ldc.i4.0",
            "ldstr Combined", "ldc.i4.0", "ldc.i4.0", "ldc.i4.1", "newarr System.Type") &&
            TestRangeHasRun(validate, "ldloc.0",
                "call System.Collections.Generic.IEnumerable`1<System.Type> AnchorChain.BetaCompatibilityCalls::TestRangeStandoffArgs(System.Collections.Generic.IEnumerable`1<System.Type>,System.Collections.Generic.IEnumerable`1<System.Type>)",
                "call !!0[] System.Linq.Enumerable::ToArray<System.Type>(System.Collections.Generic.IEnumerable`1<!!0>)",
                "call System.Void TestRange.CountermeasureApi::Add(System.Type,System.String,System.Type,System.Boolean,System.String,System.Boolean,System.Boolean,System.Type[])"),
            "R1: the combined-jamming hook registers on instance double ECM.StandoffNoiseFactor through the bridge");
        Check(TestRangeHasRun(validate, "ldloc.0",
                "call System.Collections.Generic.IEnumerable`1<!!0> System.Linq.Enumerable::Concat<System.Type>(System.Collections.Generic.IEnumerable`1<!!0>,System.Collections.Generic.IEnumerable`1<!!0>)",
                "call !!0[] System.Linq.Enumerable::ToArray<System.Type>(System.Collections.Generic.IEnumerable`1<!!0>)",
                "call System.Void AnchorChain.BetaCompatibilityCalls::TestRangeLegacyCombined(System.Type,System.String,System.Type,System.Boolean,System.String,System.Boolean,System.Boolean,System.Type[])") &&
            validate.Body.Instructions.Count(i => i.OpCode == OpCodes.Ldstr && Equals(i.Operand, "CombinedJamUnit")) == 1,
            "R2: the removed 10-parameter registration goes to the checking bridge");

        var hooks = module.GetType("TestRange.CountermeasureHooks");
        var combined = hooks.Methods.Single(m => m.Name == "Combined");
        Check(combined.IsStatic && combined.ReturnType.FullName == "System.Boolean" &&
            combined.Parameters.Select(p => p.Name + ":" + p.ParameterType.FullName).SequenceEqual(new[] { "__instance:SeaPower.ECM", "__result:System.Double&" }) &&
            combined.Body.Instructions.Select(TestRangeIl).SequenceEqual(new[] {
                "volatile.", "ldsfld System.Boolean modreq(System.Runtime.CompilerServices.IsVolatile) TestRange.CountermeasurePolicy::JammingRestricted",
                "brfalse IL_002a", "ldarg.0", "ldfld SeaPower.ObjectBase SeaPower.ECM::_homeObject", "ldc.i4.2",
                "call System.Boolean TestRange.CountermeasurePolicy::Blocked(System.Object,System.Int32)", "brfalse IL_002a",
                "ldarg.1", "ldc.r8 0", "stind.r8", "ldc.i4.0", "ret", "ldc.i4.1", "ret" }),
            "R3: Combined is a StandoffNoiseFactor prefix that zeroes a blocked unit's jammer term, with long branches");

        var api = module.GetType("TestRange.Api").Methods.Single(m => m.Name == "Validate");
        Check(TestRangeHasRun(api, "ldtoken SeaPower.WeaponSystemLauncher", handle, "ldstr launch", "ldtoken System.Boolean") &&
            TestRangeHasRun(api, "ldtoken SeaPower.WeaponSystemHardpoint", handle, "ldstr launch", "ldtoken System.Void"),
            "R4: the launcher requirement expects bool; the hardpoint requirement keeps void");

        var defense = module.GetType("TestRange.DefenseHooks");
        var launch = defense.Methods.Single(m => m.Name == "Launch");
        var hardpoint = defense.Methods.Single(m => m.Name == "Hardpoint");
        string[] allows = { "ldarg.0", "ldfld SeaPower.ObjectBase SeaPower.BaseSystem::_baseObject", "ldarg.1", "ldarg.0",
            "ldfld SeaPower.Ammunition SeaPower.WeaponSystem::_ammoForEngage", "call System.String TestRange.DefenseHooks::Id(SeaPower.Ammunition)",
            "call System.Boolean TestRange.DefensePolicy::Allows(System.Object,System.Object,System.String)" };
        Check(launch.Parameters.Select(p => p.Name + ":" + p.ParameterType.FullName)
                .SequenceEqual(new[] { "__instance:SeaPower.WeaponSystemLauncher", "__1:SeaPower.ObjectBase", "__result:System.Boolean&" }) &&
            launch.Body.Instructions.Select(TestRangeIl).SequenceEqual(allows.Concat(new[] { "dup", "brtrue IL_0020", "ldarg.2", "ldc.i4.1", "stind.i1", "ret" })),
            "R5: a blocked launch still skips launch() and now reports it as launched");
        Check(hardpoint.Parameters.Count == 2 && hardpoint.Body.Instructions.Select(TestRangeIl).SequenceEqual(allows.Concat(new[] { "ret" })),
            "Hardpoint hook, which shared the author's body bytes, is unchanged");

        var ensure = module.GetType("TestRange.Panel").Methods.Single(m => m.Name == "EnsureCatalog");
        Check(TestRangeHasRun(ensure, "ldstr ammunition", "ldstr *.ini", "ldc.i4 31",
            "callvirt System.Collections.Generic.List`1<System.String> SeaPower.FileManager::GetFiles(System.String,System.String,SeaPower.LayerKind)"),
            "R6: the missile catalog scan passes kinds = LayerKind.All (31)");

        var sensor = module.GetType("TestRange.ResultHooks").NestedTypes.Single(t => t.Name == "<>c__DisplayClass13_0").Methods.Single(m => m.Name == "<Sensor>b__0");
        var data = sensor.Body.Instructions.Where(i => (i.Operand as FieldReference)?.Name == "SensorData").ToList();
        Check(data.Count == 1 && ((FieldReference)data[0].Operand).FieldType.IsValueType &&
            TestRangeIl(data[0].Next) == "ldfld System.Single SeaPower.SensorSystem/SensorDistanceData::Distance",
            "R7: SensorData is read with its beta value-type encoding, then Distance");

        var allow = module.GetType("ACModActivation.Guard").Methods.Single(m => m.Name == "Allow");
        Check(allow.Body.Instructions.Count(i => (i.Operand as MethodReference)?.FullName == "System.String AnchorChain.BetaAssemblyPolicy::OriginalLocation(System.Reflection.Assembly)") == 2 &&
            !allow.Body.Instructions.Any(i => (i.Operand as MethodReference)?.Name == "get_Location"),
            "Shared rule: both Guard.Allow Assembly.Location reads use OriginalLocation");
        Check(!module.Types.SelectMany(t => new[] { t }.Concat(t.NestedTypes)).SelectMany(t => t.Methods).Where(m => m.HasBody)
            .SelectMany(m => m.Body.Instructions).Any(i => i.OpCode.OperandType == OperandType.ShortInlineBrTarget),
            "No short branch remains in the private image");
    }

    // As for R5: every Seapower-Scripts method and field operand resolves in Cecil.
    static void TestRangeCecilOperands(string adapted, DefaultAssemblyResolver resolver)
    {
        using var module = ModuleDefinition.ReadModule(adapted, new ReaderParameters { AssemblyResolver = resolver });
        var missing = new List<string>(); int resolved = 0;
        foreach (var type in Types(module.Types)) foreach (var method in type.Methods.Where(m => m.HasBody))
            foreach (var instruction in method.Body.Instructions) {
                var member = instruction.Operand as MemberReference;
                if (member?.DeclaringType?.Scope is not AssemblyNameReference scope || scope.Name != "Seapower-Scripts") continue;
                try {
                    if (member is MethodReference call) { if (call.Resolve() == null) throw new Exception("unresolved method"); resolved++; }
                    else if (member is FieldReference field) { if (field.Resolve() == null) throw new Exception("unresolved field"); resolved++; }
                } catch (Exception ex) { missing.Add(method.Name + ": " + member.FullName + " " + ex.Message); }
            }
        foreach (string failure in missing) Console.WriteLine("MISSING TestRange/" + failure);
        Check(missing.Count == 0 && resolved > 100, "All TestRange native method/field operands resolve in Cecil (" + resolved + ")");
    }

    // Mono parses each signature against the beta types, so it also catches a
    // class/valuetype mismatch that Cecil's Resolve accepts.
    static void TestRangeMonoTokens(Assembly assembly, string path, DefaultAssemblyResolver resolver, int expectedFailures, string what)
    {
        using var module = ModuleDefinition.ReadModule(path, new ReaderParameters { AssemblyResolver = resolver });
        var tokens = new SortedSet<int>();
        foreach (var type in Types(module.Types)) foreach (var method in type.Methods.Where(m => m.HasBody))
            foreach (var instruction in method.Body.Instructions)
                if (instruction.Operand is MemberReference member && ((member is MethodReference || member is FieldReference) &&
                    member.DeclaringType?.Scope is AssemblyNameReference scope && scope.Name == "Seapower-Scripts" ||
                    member is TypeReference typeRef && typeRef.Scope is AssemblyNameReference owner && owner.Name == "Seapower-Scripts"))
                    tokens.Add(member.MetadataToken.ToInt32());
        var failures = new List<string>();
        foreach (int token in tokens) {
            try { if (assembly.ManifestModule.ResolveMember(token) == null) failures.Add(token.ToString("x8") + " null"); }
            catch (Exception ex) { failures.Add(token.ToString("x8") + " " + ex.GetType().Name); }
        }
        foreach (string failure in failures) Console.WriteLine("MONO " + what + ": " + failure);
        if (expectedFailures == 0)
            Check(failures.Count == 0 && tokens.Count >= 90, "Mono resolves every Seapower-Scripts member token of the TestRange " + what + " (" + tokens.Count + ")");
        else
            Check(failures.Count == 2 && failures[0].StartsWith("0a000058 ") && failures[1].StartsWith("0a00013f "),
                "TestRange " + what + " fails under Mono on exactly GetFiles(string,string) 0a000058 and SensorData 0a00013f");
    }

    // HarmonyX binds a patch parameter by the original's parameter name, by
    // __instance, __result, __state, __N (argument index) or ___field.
    static string TestRangeBinding(MethodInfo patch, MethodBase original, bool postfix)
    {
        if (!patch.IsStatic) return "patch is not static";
        if (!postfix && patch.ReturnType != typeof(bool) && patch.ReturnType != typeof(void)) return "prefix returns " + patch.ReturnType;
        var arguments = original.GetParameters();
        foreach (var parameter in patch.GetParameters()) {
            var type = parameter.ParameterType;
            bool Same(Type target) => type == target || (!target.IsByRef && type == target.MakeByRefType());
            string name = parameter.Name;
            if (name == "__instance") { if (original.IsStatic || !type.IsAssignableFrom(original.DeclaringType)) return name; }
            else if (name == "__result") {
                var result = (original as MethodInfo)?.ReturnType;
                if (result == null || result == typeof(void) || !Same(result) || (!postfix && !type.IsByRef)) return name + " vs " + result;
            }
            else if (name == "__state") { }
            else if (name.StartsWith("___", StringComparison.Ordinal)) {
                var field = AccessTools.Field(original.DeclaringType, name.Substring(3));
                if (field == null || !Same(field.FieldType)) return name;
            }
            else if (name.StartsWith("__", StringComparison.Ordinal) && int.TryParse(name.Substring(2), out int index)) {
                if (index >= arguments.Length || !Same(arguments[index].ParameterType)) return name;
            }
            else {
                var match = arguments.SingleOrDefault(a => a.Name == name);
                if (match == null || !Same(match.ParameterType)) return name;
            }
        }
        return null;
    }

    static void TestRangeValidators(Assembly loaded)
    {
        var vector = typeof(UnityEngine.Vector3);
        var jam = new[] { typeof(float), vector, typeof(Globals.Frequency), typeof(float), typeof(float), typeof(float), typeof(Crew), typeof(float) };
        Check(typeof(ECM).GetMethod("CombinedJamUnit", (BindingFlags)60, null, new[] { typeof(IEnumerable<ECM>) }.Concat(jam).ToArray(), null) == null &&
            typeof(ECM).GetMethod("CombinedJamUnit", (BindingFlags)60, null, new[] { typeof(IEnumerable<ECM>), typeof(ObjectBase) }.Concat(jam).ToArray(), null) == null,
            "The author's stable CombinedJamUnit lookups fail on the beta, as captured");

        // The author's own countermeasure validator, which stopped the plugin.
        var countermeasures = loaded.GetType("TestRange.CountermeasureApi", true);
        countermeasures.GetMethod("Validate", TestRangeAll).Invoke(null, null);
        var patches = ((IEnumerable)countermeasures.GetField("Patches", TestRangeAll).GetValue(null)).Cast<object>().ToList();
        var patchType = loaded.GetType("TestRange.CountermeasurePatch", true);
        var target = patchType.GetField("Target"); var hook = patchType.GetField("Hook"); var post = patchType.GetField("Postfix");
        var registered = patches.Select(p => ((MethodInfo)target.GetValue(p)).Name + "->" + ((MethodInfo)hook.GetValue(p)).Name + ((bool)post.GetValue(p) ? "(postfix)" : "")).ToList();
        Console.WriteLine("TestRange countermeasure patches: " + String.Join(", ", registered));
        Check(registered.SequenceEqual(new[] { "launchChaff->ChaffLaunch", "readyToLaunch->ChaffReady(postfix)", "jamWeapon->JamWeapon", "JamUnit->JamUnit",
            "StandoffNoiseFactor->Combined", "SelfScreenNoisePower->SelfScreen", "HasNoiseJammer->NoiseJammer", "IsBeingOffensivelyJammedBy->Offensive" }),
            "The adapted CountermeasureApi.Validate passes on the beta and registers all eight countermeasure hooks");
        var standoff = (MethodInfo)target.GetValue(patches[4]);
        Check(standoff.DeclaringType == typeof(ECM) && !standoff.IsStatic && standoff.ReturnType == typeof(double) &&
            standoff.GetParameters().Select(p => p.ParameterType).SequenceEqual(new[] { vector, typeof(Globals.Frequency), typeof(float) }),
            "The jammer filter targets instance double ECM.StandoffNoiseFactor(Vector3, Frequency, float)");
        foreach (var patch in patches) {
            var original = (MethodInfo)target.GetValue(patch); var method = (MethodInfo)hook.GetValue(patch);
            string error = TestRangeBinding(method, original, (bool)post.GetValue(patch));
            Check(error == null, "TestRange " + method.Name + " parameters bind to beta " + original.DeclaringType.Name + "." + original.Name + (error == null ? "" : ": " + error));
        }

        // The author's requirement for the launcher, as adapted Api.Validate calls it.
        var api = loaded.GetType("TestRange.Api", true);
        var require = api.GetMethod("Require", TestRangeAll);
        var launchArgs = new[] { typeof(int), typeof(ObjectBase), vector, vector, typeof(float) };
        var launch = (MethodInfo)require.Invoke(null, new object[] { typeof(WeaponSystemLauncher), "launch", typeof(bool), launchArgs });
        Check(launch != null && launch.ReturnType == typeof(bool) && launch.DeclaringType == typeof(WeaponSystemLauncher),
            "Api.Require finds the beta bool WeaponSystemLauncher.launch");
        bool voidFails = false;
        try { require.Invoke(null, new object[] { typeof(WeaponSystemLauncher), "launch", typeof(void), launchArgs }); }
        catch (TargetInvocationException ex) when (ex.InnerException is MissingMethodException) { voidFails = true; }
        Check(voidFails, "The author's stable void launcher requirement fails on the beta, as captured");
        var hardpoint = (MethodInfo)require.Invoke(null, new object[] { typeof(WeaponSystemHardpoint), "launch", typeof(void),
            new[] { typeof(ObjectBase), vector, vector, vector } });
        var defense = loaded.GetType("TestRange.DefenseHooks", true);
        foreach (var (name, original) in new (string, MethodBase)[] {
            ("Launch", launch), ("Hardpoint", hardpoint),
            ("Gun", AccessTools.Method(typeof(WeaponSystemGun), "fire", Type.EmptyTypes)),
            ("Ciws", AccessTools.Method(typeof(WeaponSystemCIWS), "FireAtTarget", Type.EmptyTypes)),
            ("Match", AccessTools.Method(typeof(ObjectBase), "DoesAmmoMatchTarget",
                new[] { typeof(AmmunitionParameters), typeof(ObjectBase), typeof(bool).MakeByRefType(), typeof(bool) })) }) {
            var method = defense.GetMethod(name, TestRangeAll);
            string error = original == null ? "target missing" : TestRangeBinding(method, original, false);
            Check(error == null, "TestRange defence hook " + name + " binds to its beta target" + (error == null ? "" : ": " + error));
        }
        var blocked = defense.GetMethod("Launch", TestRangeAll).GetParameters();
        Check(blocked.Length == 3 && blocked[2].Name == "__result" && blocked[2].ParameterType == typeof(bool).MakeByRefType(),
            "Launch prefix receives beta launch()'s bool result by reference");
    }

    static void TestRangeBridges()
    {
        var vector = typeof(UnityEngine.Vector3);
        var jam = new[] { typeof(float), vector, typeof(Globals.Frequency), typeof(float), typeof(float), typeof(float), typeof(Crew), typeof(float) };
        var native = typeof(ECM).GetMethods((BindingFlags)60).Single(m => m.Name == "StandoffNoiseFactor");
        var args = BetaCompatibilityCalls.TestRangeStandoffArgs(new[] { typeof(IEnumerable<ECM>) }, jam).ToArray();
        Check(args.SequenceEqual(native.GetParameters().Select(p => p.ParameterType)) &&
            native.GetParameters().Select(p => p.Name).SequenceEqual(new[] { "ownPosition", "frequency", "jamResistance" }),
            "TestRangeStandoffArgs returns beta ECM.StandoffNoiseFactor's parameter types (ownPosition, frequency, jamResistance)");
        Check(typeof(ECM).GetMethod("StandoffNoiseFactor", (BindingFlags)60, null, args, null) == native,
            "The author's GetMethod lookup with those types binds the native per-jammer term");
        bool Throws(Action action) { try { action(); return false; } catch (InvalidOperationException) { return true; } }
        Check(Throws(() => BetaCompatibilityCalls.TestRangeStandoffArgs(new[] { typeof(IEnumerable<ECM>), typeof(ObjectBase) }, jam)) &&
            Throws(() => BetaCompatibilityCalls.TestRangeStandoffArgs(new[] { typeof(IEnumerable<ECM>) }, jam.Take(7))) &&
            Throws(() => BetaCompatibilityCalls.TestRangeStandoffArgs(new[] { typeof(List<ECM>) }, jam)) &&
            Throws(() => BetaCompatibilityCalls.TestRangeStandoffArgs(null, jam)),
            "TestRangeStandoffArgs rejects any other registration shape");
        var legacy = new[] { typeof(IEnumerable<ECM>), typeof(ObjectBase) }.Concat(jam).ToArray();
        Check(!Throws(() => BetaCompatibilityCalls.TestRangeLegacyCombined(typeof(ECM), "CombinedJamUnit", typeof(float), true, "Combined", false, false, legacy)),
            "TestRangeLegacyCombined accepts the author's exact legacy registration on the beta");
        Check(Throws(() => BetaCompatibilityCalls.TestRangeLegacyCombined(typeof(ECM), "JamUnit", typeof(float), false, "JamUnit", false, false, jam)) &&
            Throws(() => BetaCompatibilityCalls.TestRangeLegacyCombined(typeof(ECM), "CombinedJamUnit", typeof(float), true, "Combined", false, true, legacy)) &&
            Throws(() => BetaCompatibilityCalls.TestRangeLegacyCombined(typeof(ObjectBase), "CombinedJamUnit", typeof(float), true, "Combined", false, false, legacy)),
            "TestRangeLegacyCombined rejects any other registration");
        var combined = typeof(ECM).GetMethods((BindingFlags)60).Where(m => m.Name == "CombinedJamUnit").ToList();
        Check(combined.Count == 1 && combined[0].GetParameters()[0].ParameterType == typeof(double) && combined[0].GetParameters()[0].Name == "supportNoiseFactor",
            "Beta CombinedJamUnit takes only the pre-summed supportNoiseFactor");
    }

    // The native flow the rewrites rely on, read from the real beta IL.
    static void TestRangeNativeShapes()
    {
        var standoff = typeof(ECM).GetMethods((BindingFlags)60).Single(m => m.Name == "StandoffNoiseFactor");
        var apply = typeof(RadarCalculator).GetMethod("ApplyJammingToDetectionRange", TestRangeAll);
        var body = PatchProcessor.GetOriginalInstructions(apply);
        var terms = body.Select((c, i) => (c, i)).Where(x => x.c.operand as MethodInfo == standoff).ToList();
        Check(terms.Count == 1 && body[terms[0].i + 1].opcode == System.Reflection.Emit.OpCodes.Add &&
            body.Count(c => (c.operand as MethodInfo)?.Name == "CombinedJamUnit") == 1,
            "Beta ApplyJammingToDetectionRange adds one StandoffNoiseFactor term per jammer into CombinedJamUnit's sum");
        var jamUnit = typeof(ECM).GetMethods((BindingFlags)60).Single(m => m.Name == "JamUnit");
        Check(PatchProcessor.GetOriginalInstructions(jamUnit).Count(c => c.operand as MethodInfo == standoff) == 1,
            "Beta ECM.JamUnit reaches StandoffNoiseFactor once, after TestRange's own JamUnit prefix");
        var update = PatchProcessor.GetOriginalInstructions(AccessTools.Method(typeof(WeaponSystemLauncher), "OnUpdate"));
        var launches = update.Select((c, i) => (c, i)).Where(x => (x.c.operand as MethodInfo)?.DeclaringType == typeof(WeaponSystemLauncher) &&
            ((MethodInfo)x.c.operand).Name == "launch").ToList();
        Check(launches.Count == 3 && launches.Count(x => update[x.i + 1].opcode == System.Reflection.Emit.OpCodes.Pop) == 2 &&
            launches.Count(x => update[x.i + 1].opcode == System.Reflection.Emit.OpCodes.Brtrue || update[x.i + 1].opcode == System.Reflection.Emit.OpCodes.Brtrue_S) == 1,
            "Beta OnUpdate branches on one launch() result and discards two");
        var window = PatchProcessor.GetOriginalInstructions(AccessTools.Method(typeof(DM), "DoTestWindow"));
        Check(window.Count(c => (c.operand as MethodInfo)?.DeclaringType == typeof(DM_MissileTest) && ((MethodInfo)c.operand).Name == "DrawUI") == 1,
            "Beta DM.DoTestWindow keeps the single Missile Test view call the author's transpiler replaces");
        var field = typeof(ObjectBase.EstimatedSensorRangeData).GetField("SensorData");
        Check(field.FieldType.IsValueType && field.FieldType.GetField("Distance")?.FieldType == typeof(float),
            "Beta EstimatedSensorRangeData.SensorData is a value type with a float Distance");
        var scan = typeof(FileManager).GetMethod("GetFiles", new[] { typeof(string), typeof(string), typeof(LayerKind) });
        Check(scan != null && scan.GetParameters()[2].IsOptional && Equals(scan.GetParameters()[2].DefaultValue, LayerKind.All) && (int)LayerKind.All == 31 &&
            typeof(FileManager).GetMethod("GetFiles", new[] { typeof(string), typeof(string) }) == null,
            "Beta GetFiles(path, pattern, kinds) defaults kinds to LayerKind.All = 31; the two-argument form is gone");
    }

    // Beta GetFiles with the appended LayerKind.All, then the author's own
    // name pipeline from Panel.EnsureCatalog, on a two-layer fixture.
    static void TestRangeCatalogFixture(string root)
    {
        string high = Path.Combine(root, "testrange-high"), low = Path.Combine(root, "testrange-low");
        foreach (string layer in new[] { high, low }) Directory.CreateDirectory(Path.Combine(layer, "ammunition"));
        File.WriteAllText(Path.Combine(high, "ammunition", "a.ini"), "[General]\n");
        File.WriteAllText(Path.Combine(low, "ammunition", "A.ini"), "[General]\n");
        File.WriteAllText(Path.Combine(low, "ammunition", "b.ini"), "[General]\n");
        File.WriteAllText(Path.Combine(low, "ammunition", "readme.txt"), "not an ini\n");
        var manager = (FileManager)FormatterServices.GetUninitializedObject(typeof(FileManager));
        typeof(FileManager).GetField("_fileIndex", BindingFlags.NonPublic | BindingFlags.Instance).SetValue(manager,
            new System.Collections.Concurrent.ConcurrentDictionary<string, HashSet<string>>(StringComparer.OrdinalIgnoreCase));
        typeof(FileManager).GetField("_layers", BindingFlags.NonPublic | BindingFlags.Instance).SetValue(manager,
            new FileLayerSnapshot(new[] { new FileLayer(high, LayerKind.All), new FileLayer(low, LayerKind.All) }));
        var files = manager.GetFiles("ammunition", "*.ini", (LayerKind)31);
        Console.WriteLine("TestRange catalog fixture files: " + String.Join(", ", files));
        var names = files.Select(Path.GetFileNameWithoutExtension).Distinct(StringComparer.OrdinalIgnoreCase)
            .OrderBy(x => x, StringComparer.OrdinalIgnoreCase).ToArray();
        Check(files.Count >= 2 && names.Length == 2 && String.Equals(names[0], "a", StringComparison.OrdinalIgnoreCase) && names[1] == "b",
            "Missile catalog scan with LayerKind.All lists every active layer's missiles once");
    }
}
