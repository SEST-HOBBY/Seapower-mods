using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using AnchorChain;
using HarmonyLib;
using Mono.Cecil;
using SeaPower;

static partial class BetaApiTests
{
    const BindingFlags ChaffAll = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance;

    // Enhanced Decoy Mod 0.5.4 (7cd4f160) on 0.9.3-261123: each read of the
    // retired _ammoInUse field and _chaff attacher goes to the launcher's
    // chaff-band round, the hook list names the 261123 signatures and
    // targets, two transpilers with no matching 261123 code are off, and the
    // author's own startup validators pass.
    static void R6_EnhancedDecoy(R6Context context)
    {
        string source = Path.Combine(context.Workshop, "3784474738", "EnhancedDecoyMod.dll");
        string prepared = ChaffPrepared(context, source, "7cd4f160dae75147a84bcc671d791db3012278497decffe80431d262d9ad7548",
            "EnhancedDecoyMod", "EnhancedDecoyAudit");
        if (prepared == null) return;
        var getter = typeof(WeaponSystemChaff).GetProperty("_ammoInUse", ChaffAll);
        Check(getter != null && getter.GetGetMethod(true) != null && getter.GetSetMethod(true) == null &&
            typeof(WeaponSystemChaff).GetField("_ammoInUse", ChaffAll) == null && getter.PropertyType == typeof(Ammunition),
            "On 261123 WeaponSystemChaff._ammoInUse is a read-only Ammunition property and no field");
        Check(typeof(WeaponSystemChaff).GetField("_chaff", ChaffAll) == null && typeof(WeaponSystemChaff).GetField("_rounds", ChaffAll) != null,
            "On 261123 WeaponSystemChaff has no single _chaff attacher, only _rounds");
        string bridges = typeof(BetaCompatibilityCalls).FullName;
        string[] hooksChanged = { ".cctor", "AttacherFor", "IsUpgradeReady", "Validate", "Patches", "CanLaunch", "LauncherReady", "ManualChaff" };
        var changed = new List<int>();
        using (var author = ModuleDefinition.ReadModule(source, new ReaderParameters { AssemblyResolver = context.Resolver }))
        using (var adapted = ModuleDefinition.ReadModule(prepared, new ReaderParameters { AssemblyResolver = context.Resolver })) {
            int fields = 0, calls = 0, locations = 0, attachers = 0, compared = 0, launches = 0, readies = 0;
            var authorTypes = Types(author.Types).ToList(); var adaptedTypes = Types(adapted.Types).ToList();
            Check(authorTypes.Select(t => t.FullName).SequenceEqual(adaptedTypes.Select(t => t.FullName)), "Adapted Enhanced Decoy image has the author's types");
            for (int t = 0; t < authorTypes.Count; t++) for (int m = 0; m < authorTypes[t].Methods.Count; m++) {
                var written = authorTypes[t].Methods[m]; var actual = adaptedTypes[t].Methods[m];
                bool bandHook = written.DeclaringType.FullName == "EnhancedDecoyMod.Hooks" && new[] { "CanLaunch", "LauncherReady", "ManualChaff" }.Contains(written.Name);
                Check(written.FullName == actual.FullName || bandHook && written.Name == actual.Name && written.ReturnType.FullName == actual.ReturnType.FullName &&
                    written.Parameters.Select(p => p.ParameterType.FullName + " " + p.Name).SequenceEqual(actual.Parameters.Take(written.Parameters.Count).Select(p => p.ParameterType.FullName + " " + p.Name)),
                    "Adapted Enhanced Decoy method order is the author's (launch hooks gain trailing parameters only): " + written.FullName);
                if (!written.HasBody) continue;
                compared++;
                bool Bridge(Mono.Cecil.Cil.Instruction i, string name) => i.OpCode == Mono.Cecil.Cil.OpCodes.Call && i.Operand is MethodReference c &&
                    c.Name == name && c.DeclaringType.FullName == bridges;
                int reads = written.Body.Instructions.Count(i => i.Operand is FieldReference f && f.Name == "_ammoInUse" && f.DeclaringType.FullName == "SeaPower.WeaponSystemChaff");
                int bridged = actual.Body.Instructions.Count(i => Bridge(i, "EnhancedDecoyChaffAmmo"));
                int attacher = actual.Body.Instructions.Count(i => Bridge(i, "EnhancedDecoyChaffAttacher"));
                int located = actual.Body.Instructions.Count(i => i.Operand is MethodReference c && c.Name == "OriginalLocation" &&
                    c.DeclaringType.FullName == typeof(BetaAssemblyPolicy).FullName);
                bool hooks = actual.DeclaringType.FullName == "EnhancedDecoyMod.Hooks" && hooksChanged.Contains(actual.Name);
                Check(!actual.Body.Instructions.Any(i => i.Operand is FieldReference f && f.Name == "_ammoInUse" && f.DeclaringType.FullName == "SeaPower.WeaponSystemChaff"),
                    "Adapted Enhanced Decoy no longer names the _ammoInUse field: " + actual.FullName);
                Check(bridged == reads, "Each Enhanced Decoy _ammoInUse read became one chaff-band bridge call: " + actual.FullName);
                Check(attacher == (hooks && (actual.Name == "AttacherFor" || actual.Name == "IsUpgradeReady") ? 1 : 0) &&
                    (attacher == 0 || !actual.Body.Instructions.Any(i => i.Operand is MethodReference c && c.Name == "GetValue" && c.DeclaringType.FullName == "System.Reflection.FieldInfo")),
                    "Only Hooks.AttacherFor and IsUpgradeReady read the attacher, through the same-round bridge: " + actual.FullName);
                // The mod's own launchChaff()/readyToLaunch() calls ask for Chaff.
                bool Wrapper(Mono.Cecil.Cil.Instruction i, string name) => i.Operand is MethodReference c && c.Name == name &&
                    c.DeclaringType.FullName == "SeaPower.WeaponSystemChaff" && c.Parameters.Count == 0;
                bool Banded(Mono.Cecil.Cil.Instruction i, string name, bool pop) => i.OpCode == Mono.Cecil.Cil.OpCodes.Callvirt &&
                    i.Operand is MethodReference c && c.Name == name && c.DeclaringType.FullName == "SeaPower.WeaponSystemChaff" &&
                    c.Parameters.Count == 1 && c.Parameters[0].ParameterType.FullName == "SeaPower.DecoyBand" && c.ReturnType.FullName == "System.Boolean" &&
                    i.Previous.OpCode == Mono.Cecil.Cil.OpCodes.Ldc_I4_0 && (!pop || i.Next.OpCode == Mono.Cecil.Cil.OpCodes.Pop);
                int ownLaunches = written.Body.Instructions.Count(i => Wrapper(i, "launchChaff")), ownReadies = written.Body.Instructions.Count(i => Wrapper(i, "readyToLaunch"));
                Check(!actual.Body.Instructions.Any(i => Wrapper(i, "launchChaff") || Wrapper(i, "readyToLaunch")) &&
                    actual.Body.Instructions.Count(i => Banded(i, "launchChaff", true)) == ownLaunches &&
                    actual.Body.Instructions.Count(i => Banded(i, "ReadyToLaunch", false)) == ownReadies,
                    "Each Enhanced Decoy launchChaff()/readyToLaunch() call became launchChaff(Chaff)/ReadyToLaunch(Chaff): " + actual.FullName);
                fields += reads; calls += bridged; locations += located; attachers += attacher; launches += ownLaunches; readies += ownReadies;
                bool same = TopoInstructions(written).SequenceEqual(TopoInstructions(actual));
                Check(same == (reads == 0 && located == 0 && !hooks && ownLaunches == 0 && ownReadies == 0),
                    "Only Enhanced Decoy bodies holding an ammunition read, a location read, a launch call or an inspected Hooks site differ: " + actual.FullName);
                if (!same) changed.Add(actual.MetadataToken.ToInt32());
            }
            Check(launches == 5 && readies == 4, "Enhanced Decoy: its 5 own launches and 4 readiness checks ask for the chaff band (" + launches + "/" + readies + ")");
            ChaffBandHookBodies(adapted.GetType("EnhancedDecoyMod.Hooks"));
            Check(fields == 33 && calls == 33 && locations == 2 && attachers == 2,
                "Enhanced Decoy: 33 _ammoInUse reads use the chaff-band bridge, 2 attacher reads the same-round bridge, 2 location reads keep the Workshop path (" +
                fields + "/" + calls + "/" + attachers + "/" + locations + ")");
            var cctor = adapted.GetType("EnhancedDecoyMod.Hooks").Methods.Single(m => m.Name == ".cctor").Body.Instructions;
            Check(cctor.Count(i => Equals(i.Operand, "_rounds")) == 1 && !cctor.Any(i => Equals(i.Operand, "_chaff")),
                "Enhanced Decoy Hooks..cctor looks up WeaponSystemChaff._rounds in place of _chaff");
            Console.WriteLine("Enhanced Decoy method bodies compared: " + compared + ", changed: " + changed.Count);
        }
        var assembly = Assembly.LoadFile(prepared);
        Check(assembly.GetTypes().Length > 50, "Adapted Enhanced Decoy completes CLR type discovery on 261123");
        Check(BetaAssemblyPolicy.OriginalLocation(assembly) == source, "Enhanced Decoy original asset provenance retained");
        foreach (int token in changed) {
            var method = assembly.ManifestModule.ResolveMethod(token);
            if (method.IsGenericMethodDefinition || method.DeclaringType.ContainsGenericParameters) continue;
            System.Runtime.CompilerServices.RuntimeHelpers.PrepareMethod(method.MethodHandle);
            Check(true, "Rewritten Enhanced Decoy method compiles on 261123: " + method.DeclaringType.Name + "::" + method.Name);
        }
        // The author's own startup sequence (Plugin.InitializeWhenModEnabled):
        // GameApi, DecoyMapApi, then Hooks, all inside one try whose catch
        // (System.Exception) calls UnpatchSelf and logs "Initialization rolled
        // back". Run here without its Harmony patching.
        ChaffWithoutUnityGlobals(assembly);
        CurrentInvoke(assembly.GetType("EnhancedDecoyMod.GameApi", true), "Validate");
        Check(chaffStaticNumbers.SequenceEqual(new[] { "Globals._ecmJamChanceReduction:Single", "Globals._ecmJamChanceBonus:Single" }),
            "Enhanced Decoy GameApi validator passes on 261123 and binds the two native ECM jam-chance statics: " + string.Join(", ", chaffStaticNumbers));
        Console.WriteLine("Enhanced Decoy API selected: " + assembly.GetType("EnhancedDecoyMod.GameApi", true).GetProperty("Description", ChaffAll).GetValue(null));
        var hooksType = assembly.GetType("EnhancedDecoyMod.Hooks", true);
        Exception hooksFailure = null;
        try { hooksType.GetMethod("Validate", ChaffAll).Invoke(null, null); }
        catch (TargetInvocationException ex) { hooksFailure = ex.InnerException; }
        Check(hooksFailure == null, "Enhanced Decoy's own hook validator (members, patch methods, ordering and every transpiler) passes on 261123: " + hooksFailure);
        ChaffPatchList(hooksType);
        ChaffTranspilers(hooksType);
        ChaffBridges(hooksType);
        ChaffBandHooks(hooksType);
        using (var author = ModuleDefinition.ReadModule(source, new ReaderParameters { AssemblyResolver = context.Resolver })) {
            var start = author.GetType("EnhancedDecoyMod.Plugin").Methods.Single(m => m.Name == "InitializeWhenModEnabled").Body;
            var guard = start.ExceptionHandlers.SingleOrDefault(h => h.HandlerType == Mono.Cecil.Cil.ExceptionHandlerType.Catch);
            var hookCall = start.Instructions.Single(i => i.Operand is MethodReference c && c.Name == "Validate" && c.DeclaringType.FullName == "EnhancedDecoyMod.Hooks");
            var patchCall = start.Instructions.First(i => i.Operand is MethodReference c && c.Name == "Patch" && c.DeclaringType.FullName == "HarmonyLib.Harmony");
            Check(guard != null && guard.CatchType.FullName == "System.Exception" &&
                hookCall.Offset >= guard.TryStart.Offset && hookCall.Offset < guard.TryEnd.Offset && patchCall.Offset > hookCall.Offset &&
                start.Instructions.SkipWhile(i => i != guard.HandlerStart).Take(6).Any(i => i.Operand is MethodReference c && c.Name == "UnpatchSelf") &&
                start.Instructions.Any(i => i.OpCode == Mono.Cecil.Cil.OpCodes.Ldstr && Equals(i.Operand, "Initialization rolled back: ")),
                "The author's startup still validates before its first patch, so a PC-side mismatch still unpatches and logs 'Initialization rolled back'");
        }
        // DecoyMapApi binds its map calls through compiled readers of Globals
        // statics; their compilation needs Globals' Unity-only constructor, so
        // the full map binding is left to the PC test. Anything else fails here.
        Exception map = null;
        try { assembly.GetType("EnhancedDecoyMod.DecoyMapApi", true).GetMethod("Validate", ChaffAll).Invoke(null, null); }
        catch (TargetInvocationException ex) { map = ex.InnerException; }
        Exception root = map; while (root?.InnerException != null && !(root is TypeInitializationException t && t.TypeName == "SeaPower.Globals")) root = root.InnerException;
        Check(map == null || (root is TypeInitializationException g && g.TypeName == "SeaPower.Globals"),
            "Enhanced Decoy map validator passes, or stops only at Globals' Unity-only constructor: " + map);
        Console.WriteLine("Enhanced Decoy DecoyMapApi.Validate: " + (map == null ? "passes" : "needs the Unity player (PC test)"));
        ChaffRejects(source, context, "EnhancedDecoyAdapter", null, null,
            method => method.Body.Instructions.First(i => i.Operand is FieldReference f && f.Name == "_ammoInUse").OpCode = Mono.Cecil.Cil.OpCodes.Ldflda,
            "Enhanced Decoy address-of _ammoInUse");
        void Rename(MethodDefinition method, string from, string to) => method.Body.Instructions.First(i => Equals(i.Operand, from)).Operand = to;
        ChaffRejects(source, context, "EnhancedDecoyAdapter", "EnhancedDecoyMod.Hooks", ".cctor",
            method => Rename(method, "_chaff", "_chaffAttacher"), "Enhanced Decoy attacher lookup by another name");
        ChaffRejects(source, context, "EnhancedDecoyAdapter", "EnhancedDecoyMod.GameApi", "Validate", method => {
            var first = method.Body.Instructions[0]; var writer = method.Body.GetILProcessor();
            writer.InsertBefore(first, Mono.Cecil.Cil.Instruction.Create(Mono.Cecil.Cil.OpCodes.Ldstr, "_chaff"));
            writer.InsertBefore(first, Mono.Cecil.Cil.Instruction.Create(Mono.Cecil.Cil.OpCodes.Pop));
        }, "Enhanced Decoy naming _chaff outside the inspected Hooks sites");
        ChaffRejects(source, context, "EnhancedDecoyAdapter", "EnhancedDecoyMod.Hooks", "AttacherFor",
            method => method.Body.Instructions.First(i => i.OpCode == Mono.Cecil.Cil.OpCodes.Castclass).OpCode = Mono.Cecil.Cil.OpCodes.Isinst,
            "Enhanced Decoy attacher read of another shape");
        ChaffRejects(source, context, "EnhancedDecoyAdapter", "EnhancedDecoyMod.Hooks", "Validate",
            method => Rename(method, "launchChaffEffect", "launchChaffEffects"), "Enhanced Decoy hook validator without its ordering check");
        ChaffRejects(source, context, "EnhancedDecoyAdapter", "EnhancedDecoyMod.Hooks", "Patches",
            method => Rename(method, "BeforeChaffUpdate", "BeforeUpdate"), "Enhanced Decoy ThreatFilter entry with another prefix");
        ChaffRejects(source, context, "EnhancedDecoyAdapter", "EnhancedDecoyMod.Hooks", "Patches",
            method => Rename(method, "IgnoreFilter", "Ignore"), "Enhanced Decoy patch list with one IgnoreFilter");
        ChaffRejects(source, context, "EnhancedDecoyAdapter", "EnhancedDecoyMod.Hooks", "Patches",
            method => Rename(method, "MoveCloud", "MoveDecoy"), "Enhanced Decoy ExpiryFilter entry with another prefix");
        ChaffRejects(source, context, "EnhancedDecoyAdapter", "EnhancedDecoyMod.ChaffLaunchPolicy", "TryLaunchSalvo",
            method => method.Body.Instructions.First(i => i.Operand is MethodReference m && m.Name == "launchChaff").OpCode = Mono.Cecil.Cil.OpCodes.Call,
            "Enhanced Decoy launch wrapper called without callvirt");
        ChaffRejects(source, context, "EnhancedDecoyAdapter", "EnhancedDecoyMod.GameApi", "Validate", method => {
            var wrapper = method.Module.GetMemberReferences().OfType<MethodReference>().First(m => m.Name == "readyToLaunch");
            var first = method.Body.Instructions[0]; var writer = method.Body.GetILProcessor();
            writer.InsertBefore(first, Mono.Cecil.Cil.Instruction.Create(Mono.Cecil.Cil.OpCodes.Ldnull));
            writer.InsertBefore(first, Mono.Cecil.Cil.Instruction.Create(Mono.Cecil.Cil.OpCodes.Callvirt, wrapper));
        }, "Enhanced Decoy readiness check outside the inspected launch methods");
        ChaffRejects(source, context, "EnhancedDecoyAdapter", "EnhancedDecoyMod.Hooks", "CanLaunch",
            method => method.Body.Instructions.Last(i => i.OpCode == Mono.Cecil.Cil.OpCodes.Ldc_I4_0).OpCode = Mono.Cecil.Cil.OpCodes.Ldc_I4_1,
            "Enhanced Decoy CanLaunch that runs the original after its salvo");
        ChaffRejects(source, context, "EnhancedDecoyAdapter", "EnhancedDecoyMod.Hooks", "LauncherReady",
            method => method.Body.Instructions[1].Operand = method.Body.Instructions.First(i => i.Operand is MethodReference m && m.Name == "IsUpgradeReady").Operand,
            "Enhanced Decoy LauncherReady without its scope check first");
        ChaffRejects(source, context, "EnhancedDecoyAdapter", "EnhancedDecoyMod.Hooks", "ManualChaff",
            method => method.Parameters[1].Name = "notify", "Enhanced Decoy ManualChaff with another parameter name");
    }

    // The author's Hooks.Patches() list as the adapted image builds it on
    // 261123: target, then P(refix), O (postfix), T(ranspiler), F(inalizer).
    static void ChaffPatchList(Type hooks)
    {
        var specs = (System.Collections.IEnumerable)hooks.GetMethod("Patches", ChaffAll).Invoke(null, null);
        Type specType = hooks.Assembly.GetType("EnhancedDecoyMod.PatchSpec", true);
        var listed = new List<string>();
        foreach (object spec in specs) {
            var target = (MethodBase)specType.GetField("Target", ChaffAll).GetValue(spec);
            var parts = new[] { "Prefix", "Postfix", "Transpiler", "Finalizer" }
                .Select(n => (n, (HarmonyMethod)specType.GetField(n, ChaffAll).GetValue(spec)))
                .Where(p => p.Item2 != null).Select(p => (p.Item1 == "Postfix" ? "O" : p.Item1.Substring(0, 1)) + ":" + p.Item2.method.Name);
            listed.Add(target.DeclaringType.Name + "::" + target + " " + string.Join(",", parts));
        }
        string[] expected = {
            "WeaponSystemChaff::Void OnUpdate() P:BeforeChaffUpdate,F:EndAutoUpdate",
            "WeaponSystemChaff::Void AutoRelease() T:ThreatFilter",
            "WeaponSystemChaff::Boolean ReadyToLaunch(SeaPower.DecoyBand) O:LauncherReady",
            "ObjectBase::Void LaunchChaff(Boolean, SeaPower.DecoyBand) P:ManualChaff,F:EndManualChaff",
            "WeaponSystemChaff::Boolean launchChaff(SeaPower.DecoyBand) P:CanLaunch",
            "ChaffCloud::Void launchChaffEffect(SeaPower.WeaponSystemChaff, UnityEngine.GameObject, UnityEngine.GameObject, Int32) O:Launched",
            "ChaffCloud::Void OnUpdateEveryFrame() P:MoveCloud",
            "SeekerBase::Boolean CheckCountermeasureLock(SeaPower.ObjectBase) P:CheckCandidate,O:CheckedCandidate",
            "SeekerBase::Boolean CheckCountermeasureLockBody(SeaPower.ObjectBase) T:CountermeasureGate",
            "SeekerBase::Boolean CheckCountermeasureLock() T:LockLossFilter",
            "ActiveRadarSeeker::Void searchForTarget() P:EnterRadar,F:ExitRadar",
            "ActiveRadarSeeker::Void createListOfPotentialContacts() T:IgnoreFilter",
        };
        Check(listed.Count == 35, "Enhanced Decoy builds its 33 hook entries plus the two moved transpiler entries on 261123 (" + listed.Count + ")");
        foreach (string entry in expected)
            Check(listed.Count(l => l == entry) == 1, "Enhanced Decoy 261123 hook entry: " + entry + " | " + string.Join(" | ", listed.Where(l => l.Split(' ')[0] == entry.Split(' ')[0])));
        Check(listed.Count(l => l.Contains("T:")) == 7 && !listed.Any(l => l.Contains("T:ExpiryFilter")) && listed.Count(l => l.Contains("T:IgnoreFilter")) == 1,
            "Enhanced Decoy 261123 hook list holds seven transpilers; ExpiryFilter and the radar-search IgnoreFilter are off");
        Console.WriteLine("Enhanced Decoy hook entries: " + listed.Count);
    }

    // Each moved or disabled transpiler, run as Harmony would: on the old
    // target the author's own pattern check throws; on the new target the
    // moved ones apply their two-instruction rewrite.
    static void ChaffTranspilers(Type hooks)
    {
        List<CodeInstruction> output = null, input = null;
        int Run(string transpiler, MethodBase target)
        {
            input = PatchProcessor.GetOriginalInstructions(target, null);
            var original = PatchProcessor.GetOriginalInstructions(target, null);
            var method = hooks.GetMethod(transpiler, ChaffAll);
            output = ((IEnumerable<CodeInstruction>)method.Invoke(null, new object[] { original })).ToList();
            return output.Count - input.Count;
        }
        bool CallTo(CodeInstruction i, string owner, string name) => (i.opcode == System.Reflection.Emit.OpCodes.Call || i.opcode == System.Reflection.Emit.OpCodes.Callvirt) &&
            i.operand is MethodInfo m && m.Name == name && m.DeclaringType.FullName == owner;
        bool Refuses(string transpiler, MethodBase target)
        {
            try { Run(transpiler, target); return false; } catch (Exception) { return true; }
        }
        var chaff = typeof(WeaponSystemChaff); var seeker = typeof(SeekerBase);
        var lockWrapper = seeker.GetMethod("CheckCountermeasureLock", ChaffAll, null, new[] { typeof(ObjectBase) }, null);
        var lockBody = seeker.GetMethod("CheckCountermeasureLockBody", ChaffAll, null, new[] { typeof(ObjectBase) }, null);
        Check(Refuses("ThreatFilter", chaff.GetMethod("OnUpdate", ChaffAll, null, Type.EmptyTypes, null)) &&
            Run("ThreatFilter", chaff.GetMethod("AutoRelease", ChaffAll)) == 2,
            "Enhanced Decoy ThreatFilter refuses 261123 OnUpdate (no threat-list read) and applies to AutoRelease");
        // The threat list is passed with ldarg.0, AutoRelease's own launcher.
        var threats = typeof(ObjectBase).GetField("_threats", ChaffAll);
        var filtered = output.Select((i, k) => (i, k)).Where(p => Equals(p.i.operand, threats)).Select(p => p.k).ToList();
        Check(filtered.Count == 1 && output[filtered[0] + 1].opcode == System.Reflection.Emit.OpCodes.Ldarg_0 &&
            CallTo(output[filtered[0] + 2], "EnhancedDecoyMod.Hooks", "FilterThreats") && !chaff.GetMethod("AutoRelease", ChaffAll).IsStatic &&
            hooks.GetMethod("FilterThreats", ChaffAll).GetParameters().Select(p => p.ParameterType).SequenceEqual(new[] { typeof(List<ObjectBase>), chaff }),
            "Enhanced Decoy ThreatFilter on AutoRelease passes its one threat list and the launcher (ldarg.0) to FilterThreats");
        Check(Refuses("CountermeasureGate", lockWrapper) && Run("CountermeasureGate", lockBody) == 2,
            "Enhanced Decoy CountermeasureGate refuses the 261123 profiler wrapper and applies to CheckCountermeasureLockBody");
        // Each cooldown access goes to the policy with ldarg.1, the body's
        // candidate (ObjectBase obj), as it was on the 0.9.2 method.
        var checkTime = (FieldInfo)hooks.GetField("CheckTime", ChaffAll).GetValue(null);
        string policy = "EnhancedDecoyMod.AirDecoyCountermeasurePolicy";
        int accesses = input.Count(i => Equals(i.operand, checkTime));
        var gated = output.Select((i, k) => (i, k)).Where(p => p.i.operand is MethodInfo m && m.DeclaringType.FullName == policy && m.Name.Contains("CheckTime")).ToList();
        Check(accesses == 2 && !output.Any(i => Equals(i.operand, checkTime)) && gated.Count == accesses &&
            gated.All(p => output[p.k - 1].opcode == System.Reflection.Emit.OpCodes.Ldarg_1 && ((MethodInfo)p.i.operand).GetParameters().Last().ParameterType == typeof(ObjectBase)) &&
            gated.Any(p => ((MethodInfo)p.i.operand).Name.StartsWith("Read")) && gated.Any(p => ((MethodInfo)p.i.operand).Name.StartsWith("Record")) &&
            lockBody.GetParameters().Single().ParameterType == typeof(ObjectBase) && lockBody.GetParameters()[0].Name == "obj" && !lockBody.IsStatic,
            "Enhanced Decoy CountermeasureGate sends the body's read and record of the cooldown time to the policy with the candidate (ldarg.1 = obj)");
        Check(Refuses("ExpiryFilter", typeof(ChaffCloud).GetMethod("OnUpdateEveryFrame", ChaffAll)),
            "Enhanced Decoy ExpiryFilter refuses 261123 ChaffCloud.OnUpdateEveryFrame, so it is off");
        Check(Refuses("IgnoreFilter", typeof(ActiveRadarSeeker).GetMethod("searchForTarget", ChaffAll)) &&
            Run("IgnoreFilter", typeof(ActiveRadarSeeker).GetMethod("createListOfPotentialContacts", ChaffAll)) == 1,
            "Enhanced Decoy IgnoreFilter refuses 261123 searchForTarget, so it is off there, and still applies to createListOfPotentialContacts");
        var ignored = output.Select((i, k) => (i, k)).Where(p => CallTo(p.i, "EnhancedDecoyMod.AirDecoyCountermeasurePolicy", "Ignored")).ToList();
        Check(ignored.Count == 1 && output[ignored[0].k - 1].opcode == System.Reflection.Emit.OpCodes.Ldarg_0 &&
            !output.Any(i => i.operand is MethodInfo m && m.Name == "Contains" && m.DeclaringType == typeof(List<ObjectBase>)) &&
            input.Count(i => i.operand is MethodInfo m && m.Name == "Contains" && m.DeclaringType == typeof(List<ObjectBase>)) == 1,
            "Enhanced Decoy IgnoreFilter replaces createListOfPotentialContacts' one ignore-list Contains with Ignored(list, contact, seeker = ldarg.0)");
    }

    // The two bridges choose the same round: the first whose band covers
    // chaff (Chaff or Both), else round 0; the adapted Hooks.AttacherFor
    // returns that round's attacher. WeaponSystemChaff's static constructor
    // builds a Unity ProfilerMarker, made empty here (see J36Systems).
    static void ChaffBridges(Type hooks)
    {
        InteropWithoutUnityProfiler();
        var roundsField = typeof(WeaponSystemChaff).GetField("_rounds", ChaffAll);
        Type roundType = roundsField.FieldType.GetGenericArguments()[0];
        T New<T>() => (T)System.Runtime.Serialization.FormatterServices.GetUninitializedObject(typeof(T));
        var ammo = new[] { New<Ammunition>(), New<Ammunition>(), New<Ammunition>() };
        var attachers = new[] { New<ChaffAttacher>(), New<ChaffAttacher>(), New<ChaffAttacher>() };
        var attacherFor = hooks.GetMethod("AttacherFor", ChaffAll);
        bool Picks(DecoyBand[] bands, int expected)
        {
            var system = New<WeaponSystemChaff>();
            var rounds = (System.Collections.IList)Activator.CreateInstance(roundsField.FieldType);
            for (int i = 0; i < bands.Length; i++) {
                object round = Activator.CreateInstance(roundType, true);
                roundType.GetField("Ammo").SetValue(round, ammo[i]);
                roundType.GetField("Attacher").SetValue(round, attachers[i]);
                roundType.GetField("Band").SetValue(round, bands[i]);
                rounds.Add(round);
            }
            roundsField.SetValue(system, rounds);
            object wantAmmo = expected < 0 ? null : ammo[expected], wantAttacher = expected < 0 ? null : attachers[expected];
            return ReferenceEquals(BetaCompatibilityCalls.EnhancedDecoyChaffAmmo(system), wantAmmo) &&
                ReferenceEquals(BetaCompatibilityCalls.EnhancedDecoyChaffAttacher(null, system), wantAttacher) &&
                ReferenceEquals(attacherFor.Invoke(null, new object[] { system }), wantAttacher);
        }
        Check(Picks(new[] { DecoyBand.Flare, DecoyBand.Chaff }, 1) && Picks(new[] { DecoyBand.Flare, DecoyBand.Both, DecoyBand.Chaff }, 1) &&
            Picks(new[] { DecoyBand.Chaff, DecoyBand.Chaff }, 0) && Picks(new[] { DecoyBand.Both }, 0),
            "Enhanced Decoy ammunition and attacher come from the first round covering chaff (Chaff or Both)");
        Check(Picks(new[] { DecoyBand.Chaff, DecoyBand.Flare }, 0),
            "Enhanced Decoy on a realistic split launcher (<name>~chaff round 0, <name>~flare round 1) uses the ~chaff round");
        // The native band test the launch and readiness code use: a Chaff
        // request never covers a Flare (~flare) round; Both covers all.
        var covers = typeof(WeaponSystemChaff).GetMethod("Covers", ChaffAll);
        bool Covers(DecoyBand round, DecoyBand request)
        {
            object r = Activator.CreateInstance(roundType, true); roundType.GetField("Band").SetValue(r, round);
            return (bool)covers.Invoke(null, new[] { r, (object)request });
        }
        Check(Covers(DecoyBand.Chaff, DecoyBand.Chaff) && Covers(DecoyBand.Both, DecoyBand.Chaff) && !Covers(DecoyBand.Flare, DecoyBand.Chaff) &&
            Covers(DecoyBand.Flare, DecoyBand.Both) && Covers(DecoyBand.Flare, DecoyBand.Flare) && !Covers(DecoyBand.Chaff, DecoyBand.Flare),
            "261123 launchChaff/ReadyToLaunch(Chaff) take only Chaff and Both rounds; a Both request also takes Flare rounds");
        Check(Picks(new[] { DecoyBand.Flare, DecoyBand.Flare }, 0) && Picks(new DecoyBand[0], -1),
            "Enhanced Decoy falls back to round 0 (the native _ammoInUse) with no chaff round, and to null with no rounds");
        bool Throws<E>(Action act) where E : Exception { try { act(); return false; } catch (E) { return true; } }
        Check(Throws<NullReferenceException>(() => BetaCompatibilityCalls.EnhancedDecoyChaffAmmo(null)) &&
            Throws<TargetException>(() => BetaCompatibilityCalls.EnhancedDecoyChaffAttacher(null, null)),
            "Enhanced Decoy bridges fail on a null launcher as the retired field reads did");
    }

    // The adapted launch hooks: a "band" argument for Harmony, a Flare guard
    // first, then the author's body; CanLaunch reports its salvo as launched.
    static void ChaffBandHookBodies(TypeDefinition hooks)
    {
        foreach (string name in new[] { "CanLaunch", "LauncherReady", "ManualChaff" }) {
            var method = hooks.Methods.Single(m => m.Name == name);
            var band = method.Parameters.SingleOrDefault(p => p.Name == "band");
            var il = method.Body.Instructions;
            bool guard = band != null && band.ParameterType.FullName == "SeaPower.DecoyBand" &&
                il[0].OpCode == Mono.Cecil.Cil.OpCodes.Ldarg && il[0].Operand == band && il[1].OpCode == Mono.Cecil.Cil.OpCodes.Ldc_I4_1 &&
                (il[2].OpCode == Mono.Cecil.Cil.OpCodes.Bne_Un_S || il[2].OpCode == Mono.Cecil.Cil.OpCodes.Bne_Un) &&
                (name == "CanLaunch" ? il[3].OpCode == Mono.Cecil.Cil.OpCodes.Ldc_I4_1 && il[4].OpCode == Mono.Cecil.Cil.OpCodes.Ret && il[2].Operand == il[5]
                    : il[3].OpCode == Mono.Cecil.Cil.OpCodes.Ret && il[2].Operand == il[4]);
            Check(guard, "Enhanced Decoy " + name + " returns to the native code for a Flare request before the author's body: " +
                string.Join("; ", il.Take(6).Select(i => i.OpCode + " " + i.Operand)));
        }
        var can = hooks.Methods.Single(m => m.Name == "CanLaunch");
        var result = can.Parameters.SingleOrDefault(p => p.Name == "__result");
        var cil = can.Body.Instructions;
        var salvo = cil.Single(i => i.Operand is MethodReference m && m.Name == "TryLaunchSalvo");
        var launched = (Mono.Cecil.Cil.Instruction)salvo.Next.Operand;
        Check(result != null && result.ParameterType.FullName == "System.Boolean&" && (salvo.Next.OpCode == Mono.Cecil.Cil.OpCodes.Brtrue_S || salvo.Next.OpCode == Mono.Cecil.Cil.OpCodes.Brtrue) &&
            launched.OpCode == Mono.Cecil.Cil.OpCodes.Ldarg && launched.Operand == result && launched.Next.OpCode == Mono.Cecil.Cil.OpCodes.Ldc_I4_1 &&
            launched.Next.Next.OpCode == Mono.Cecil.Cil.OpCodes.Stind_I1 && launched.Next.Next.Next.OpCode == Mono.Cecil.Cil.OpCodes.Ldc_I4_0 &&
            launched.Next.Next.Next.Next.OpCode == Mono.Cecil.Cil.OpCodes.Ret,
            "Enhanced Decoy CanLaunch sets launchChaff's result to true when its salvo ran, then skips the original");
    }

    // The loaded hooks with a Flare request leave everything to the game: no
    // author code runs (a null launcher or ship would throw in it).
    static void ChaffBandHooks(Type hooks)
    {
        var can = hooks.GetMethod("CanLaunch", ChaffAll); var ready = hooks.GetMethod("LauncherReady", ChaffAll); var manual = hooks.GetMethod("ManualChaff", ChaffAll);
        Check(can.GetParameters().Select(p => p.Name).SequenceEqual(new[] { "__instance", "band", "__result" }) &&
            ready.GetParameters().Select(p => p.Name).SequenceEqual(new[] { "__instance", "__result", "band" }) &&
            manual.GetParameters().Select(p => p.Name).SequenceEqual(new[] { "__instance", "message", "__state", "band" }) &&
            typeof(WeaponSystemChaff).GetMethod("launchChaff", new[] { typeof(DecoyBand) }).GetParameters()[0].Name == "band" &&
            typeof(WeaponSystemChaff).GetMethod("ReadyToLaunch", new[] { typeof(DecoyBand) }).GetParameters()[0].Name == "band" &&
            typeof(ObjectBase).GetMethod("LaunchChaff", new[] { typeof(bool), typeof(DecoyBand) }).GetParameters()[1].Name == "band",
            "Enhanced Decoy launch hooks take the native band by Harmony's parameter name");
        var args = new object[] { null, DecoyBand.Flare, false };
        Check((bool)can.Invoke(null, args) && !(bool)args[2], "Enhanced Decoy CanLaunch runs the native launch for a Flare request, result untouched");
        foreach (bool native in new[] { true, false }) {
            args = new object[] { null, native, DecoyBand.Flare };
            ready.Invoke(null, args);
            Check((bool)args[1] == native, "Enhanced Decoy LauncherReady keeps the native readiness (" + native + ") for a Flare request");
        }
        args = new object[] { null, true, null, DecoyBand.Flare };
        manual.Invoke(null, args);
        Check(args[2] == null, "Enhanced Decoy ManualChaff leaves a flare order to the game (no manual scope)");
        args = new object[] { null, false, null, DecoyBand.Chaff };
        manual.Invoke(null, args);
        Check(args[2] != null, "Enhanced Decoy ManualChaff still runs the author's body for a chaff order");
        Exception chaffLaunch = null;
        try { can.Invoke(null, new object[] { null, DecoyBand.Chaff, false }); } catch (TargetInvocationException ex) { chaffLaunch = ex.InnerException; }
        Exception bothLaunch = null;
        try { can.Invoke(null, new object[] { null, DecoyBand.Both, false }); } catch (TargetInvocationException ex) { bothLaunch = ex.InnerException; }
        Check(chaffLaunch is NullReferenceException && bothLaunch is NullReferenceException,
            "Enhanced Decoy CanLaunch applies the author's policy to Chaff and Both requests: " + chaffLaunch + " / " + bothLaunch);
        // ChaffCellsLoaded (postfix on every attacher's AddChaffAmmo, ~flare
        // included) returns at once in lazy mode, which 261123 selects.
        var inventory = hooks.Assembly.GetType("EnhancedDecoyMod.ChaffInventory", true);
        Check((bool)inventory.GetProperty("Lazy", ChaffAll).GetValue(null) && typeof(ChaffAttacher).GetField("_chaffClouds", ChaffAll) == null,
            "Enhanced Decoy runs in lazy mode on 261123, so ChaffCellsLoaded binds no attacher's cells");
    }

    // Globals' static constructor needs the Unity player, which this test
    // process does not have (see MissionAwardsTests). The author's
    // ApiBinding.OptionalStaticNumber compiles a reader for a Globals static,
    // which runs that constructor. Here, for a field that exists, is static
    // and numeric (the author's own acceptance test), the reader returns 0
    // instead; a missing or wrong field still goes through the author's code.
    static readonly List<string> chaffStaticNumbers = new List<string>();
    static bool ChaffStaticNumber(Type type, string name, ref Func<double> __result)
    {
        var field = type.GetField(name, (BindingFlags)60);
        if (field == null || !field.IsStatic || !(field.FieldType == typeof(float) || field.FieldType == typeof(double) || field.FieldType == typeof(int))) return true;
        chaffStaticNumbers.Add(type.Name + "." + name + ":" + field.FieldType.Name);
        __result = () => 0d;
        return false;
    }
    static void ChaffWithoutUnityGlobals(Assembly assembly)
    {
        new Harmony("sest.beta-api-tests.chaff").Patch(assembly.GetType("EnhancedDecoyMod.ApiBinding", true).GetMethod("OptionalStaticNumber", ChaffAll),
            prefix: new HarmonyMethod(typeof(BetaApiTests).GetMethod(nameof(ChaffStaticNumber), ChaffAll)));
    }

    // Prepare an exact author image and check its private image and audit.
    static string ChaffPrepared(R6Context context, string source, string expected, string name, string auditField)
    {
        byte[] original = File.ReadAllBytes(source);
        string hash; using (var sha = System.Security.Cryptography.SHA256.Create()) hash = BitConverter.ToString(sha.ComputeHash(original)).Replace("-", "").ToLowerInvariant();
        Check(hash == expected, name + " fixture is the inspected author image");
        var messages = new List<string>();
        string prepared = BetaAssemblyPolicy.Prepare(source, context.Native, context.Cache, messages.Add);
        string audit = (string)typeof(BetaAssemblyPolicy).GetField(auditField, ChaffAll).GetValue(null);
        Check(prepared != null && prepared != source && File.Exists(prepared), name + " is admitted through its 261123 adapter: " + string.Join(" | ", messages));
        Check(original.SequenceEqual(File.ReadAllBytes(source)), "Original " + name + " DLL retained byte for byte");
        Check(messages.Count == 1 && messages[0] == "ADAPTED " + name + " in private cache: " + audit + "; original Workshop DLL and asset paths preserved.",
            name + " logs one line with the inspected audit (" + audit + "): " + string.Join(" | ", messages));
        Console.WriteLine(messages.FirstOrDefault());
        return prepared == source ? null : prepared;
    }

    // The adapter's method rewrite refuses an author shape it was not written for.
    static void ChaffRejects(string source, R6Context context, string factory, string typeName, string methodName,
        Action<MethodDefinition> mutate, string why)
    {
        object adapter = typeof(BetaAssemblyPolicy).GetMethod(factory, ChaffAll).Invoke(null, null);
        var rewrite = (Delegate)adapter.GetType().GetField("RewriteMethod", ChaffAll).GetValue(adapter);
        Type scopeType = rewrite.Method.GetParameters()[0].ParameterType;
        using var module = ModuleDefinition.ReadModule(source, new ReaderParameters { AssemblyResolver = context.Resolver });
        using var native = ModuleDefinition.ReadModule(context.Native);
        bool Reads(MethodDefinition m) => m.Body.Instructions.Any(i => i.Operand is FieldReference f && f.Name == "_ammoInUse");
        var method = Types(module.Types).Where(t => typeName == null || t.FullName == typeName).SelectMany(t => t.Methods)
            .First(m => m.HasBody && (methodName == null ? Reads(m) : m.Name == methodName));
        var type = method.DeclaringType;
        mutate(method);
        object scope = Activator.CreateInstance(scopeType, true);
        scopeType.GetField("Module", ChaffAll).SetValue(scope, module);
        scopeType.GetField("Native", ChaffAll).SetValue(scope, native);
        scopeType.GetField("Count", ChaffAll).SetValue(scope, (Action<string>)(_ => {}));
        bool rejected = false;
        try { rewrite.DynamicInvoke(scope, type, method); }
        catch (TargetInvocationException ex) when (ex.InnerException is InvalidOperationException) { rejected = true; }
        Check(rejected, "Changed author shape is rejected before load: " + why);
    }
}
