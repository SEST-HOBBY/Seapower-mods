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
using SeapowerUI;

// R6: MissileControlMod 0.1.16 (Euromod Anchor Chain Expansion Pack, Workshop
// 3784474738). Metadata, reflection and bridge checks only: the author's
// transpilers run on instruction lists, no Harmony patch is applied and no
// plugin entry point or Unity gameplay runs.
static partial class BetaApiTests
{
    public sealed class MissileControlModLimits { public float G, Rate; }

    const BindingFlags MissileControlModAll = BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static | BindingFlags.Instance | BindingFlags.DeclaredOnly;

    // An independent structural rendering of a Cecil instruction: opcode,
    // then declaring type, name, static/instance and parameter types, float
    // constants by their bits, branch targets by index.
    static string MissileControlModDescribe(Mono.Cecil.Cil.Instruction instruction, IList<Mono.Cecil.Cil.Instruction> body)
    {
        string name = instruction.OpCode.Name;
        switch (instruction.Operand) {
            case FieldReference field: return name + " " + field.DeclaringType.FullName + "::" + field.Name + ":" + field.FieldType.FullName;
            case MethodReference method:
                return name + (method.HasThis ? " instance " : " static ") + method.DeclaringType.FullName + "::" + method.Name + "(" +
                    String.Join(",", method.Parameters.Select(p => p.ParameterType.FullName)) + "):" + method.ReturnType.FullName;
            case float value: return name + " 0x" + BitConverter.ToInt32(BitConverter.GetBytes(value), 0).ToString("X8");
            case Mono.Cecil.Cil.Instruction target: return name + " ->" + body.IndexOf(target);
            case null: return name;
            default: return name + " " + instruction.Operand;
        }
    }

    static void R6_MissileControlMod(R6Context context)
    {
        string source = Path.Combine(context.Workshop, "3784474738/MissileControlMod.dll");
        byte[] bytes = File.ReadAllBytes(source);
        using (var sha = System.Security.Cryptography.SHA256.Create())
            Check(BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant() == "2d6a68dfe9f0527e451f9c073faa017017a4e75c69e82c27fc70e45f1329c581",
            "MissileControlMod fixture is the pinned 0.1.16 image");
        var log = new List<string>();
        string adapted = BetaAssemblyPolicy.Prepare(source, context.Native, context.Cache, log.Add);
        foreach (string line in log) Console.WriteLine(line);
        Check(adapted != null && adapted != source && File.Exists(adapted), "MissileControlMod private API image generated");
        Check(bytes.SequenceEqual(File.ReadAllBytes(source)), "MissileControlMod author bytes retained");
        Check(log.Count == 1 && log[0] == "ADAPTED MissileControlMod in private cache: file=1, locations=2, steering-shape=1; original Workshop DLL and asset paths preserved.",
            "MissileControlMod audit is file=1, locations=2, steering-shape=1");

        MissileControlModWrittenImage(source, adapted, context);
        var assembly = Assembly.LoadFile(adapted);
        Check(BetaAssemblyPolicy.OriginalLocation(assembly) == source, "MissileControlMod keeps its Workshop path for the Mod Manager guard");

        // The author's own reference validator, the second blocker on the
        // beta: it reads every MissileControlMod/SeaPowerModSupport body and
        // resolves each member token through the CLR.
        var compatibility = assembly.GetType("MissileControlMod.Compatibility", true);
        var validate = compatibility.GetMethod("ValidateReferences", MissileControlModAll);
        try { validate.Invoke(null, new object[] { assembly }); }
        catch (TargetInvocationException ex) { throw new Exception("MissileControlMod ValidateReferences fails on the adapted image: " + ex.InnerException); }
        Check(true, "The author's ValidateReferences resolves every operand of the adapted image");

        // The author's whole startup validator (the one that throws on the
        // beta and makes InitializeWhenModEnabled log 'Disabled; native
        // behavior retained'): reflection, Compatibility.Read and the author's
        // own transpilers on instruction lists only; it installs no patch.
        try { compatibility.GetMethod("ValidateGame", MissileControlModAll).Invoke(null, null); }
        catch (TargetInvocationException ex) { throw new Exception("MissileControlMod ValidateGame fails on the adapted image: " + ex.InnerException); }
        Check(true, "The author's Compatibility.ValidateGame passes on the beta with the adapted image");
        MissileControlModSteering(assembly, compatibility);
        MissileControlModFormula();
        MissileControlModPatchParameters(assembly);
        MissileControlModRejections(source, context);
    }

    // Each rule fails closed on a shape it was not written for. The hooks are
    // read from the registered adapter by reflection and run on altered
    // in-memory copies; nothing is written or loaded.
    static void MissileControlModRejections(string source, R6Context context)
    {
        var policy = typeof(BetaAssemblyPolicy);
        var adapter = policy.GetMethod("MissileControlModAdapter", BindingFlags.NonPublic | BindingFlags.Static).Invoke(null, null);
        object Hook(string name) => adapter.GetType().GetField(name, BindingFlags.NonPublic | BindingFlags.Instance).GetValue(adapter);
        string Rejected(Action action)
        {
            try { action(); return null; }
            catch (TargetInvocationException ex) when (ex.InnerException is InvalidOperationException) { return ex.InnerException.Message; }
            catch (InvalidOperationException ex) { return ex.Message; }
        }
        var readers = new ReaderParameters { AssemblyResolver = context.Resolver, InMemory = true };
        using (var module = ModuleDefinition.ReadModule(source, readers)) {
            var hooks = module.GetType("MissileControlMod.Hooks");
            var limits = hooks.Methods.Single(m => m.Name == "SteeringLimits");
            limits.Body.GetILProcessor().InsertBefore(limits.Body.Instructions[0], Mono.Cecil.Cil.Instruction.Create(Mono.Cecil.Cil.OpCodes.Nop));
            var rewrite = (Delegate)Hook("RewriteMethod");
            Check(Rejected(() => rewrite.DynamicInvoke(null, hooks, limits)) == "Inspected MissileControlMod steering-limit transpiler changed",
                "An altered Hooks.SteeringLimits is rejected");
            var audio = module.GetType("SeaPowerModSupport.EffectAudio");
            var diagnostics = audio.Methods.Single(m => m.Name == "EnableDiagnostics");
            var call = diagnostics.Body.Instructions.Single(i => (i.Operand as MethodReference)?.Name == "GetFile");
            call.Previous.OpCode = Mono.Cecil.Cil.OpCodes.Ldarg_3;
            var rewriteCall = (Delegate)Hook("RewriteCall");
            Check(Rejected(() => rewriteCall.DynamicInvoke(null, audio, diagnostics, call, call.Operand))?.StartsWith("Inspected MissileControlMod FileManager.GetFile call changed") == true,
                "An altered EnableDiagnostics GetFile call is rejected");
        }
        using (var native = ModuleDefinition.ReadModule(context.Native, readers)) {
            var require = (Action<ModuleDefinition>)Hook("RequireNative");
            require(native);
            Check(true, "The pinned beta passes the MissileControlMod native shape checks");
            var limit = native.GetType("SeaPower.WeaponBase").Methods.Single(m => m.Name == "GLimitedTurnRate");
            limit.Body.Instructions.Single(i => i.Operand is float f && f == 9.8f).Operand = 9.81f;
            Check(Rejected(() => require(native)) == "Inspected beta WeaponBase.GLimitedTurnRate changed", "A changed native G-limit formula is rejected");
        }
    }

    static void MissileControlModWrittenImage(string source, string adapted, R6Context context)
    {
        using var module = ModuleDefinition.ReadModule(adapted, new ReaderParameters { AssemblyResolver = context.Resolver });
        MethodDefinition Method(string type, string name) => Types(module.Types).Single(t => t.FullName == type).Methods.Single(m => m.Name == name);
        string Describe(Mono.Cecil.Cil.Instruction i, IList<Mono.Cecil.Cil.Instruction> body) => MissileControlModDescribe(i, body);

        var limits = Method("MissileControlMod.Hooks", "SteeringLimits").Body.Instructions;
        string sequence = "System.Collections.Generic.IEnumerable`1<HarmonyLib.CodeInstruction>";
        var expected = new[] { "ldarg.0", "call static AnchorChain.BetaCompatibilityCalls::MissileControlModSteeringShape(" + sequence + "):" + sequence,
            "ldc.i4.1", "ldsfld MissileControlMod.Compatibility::LegacyCourse:System.Reflection.MethodInfo", "ldnull",
            "call static System.Reflection.MethodInfo::op_Equality(System.Reflection.MethodInfo,System.Reflection.MethodInfo):System.Boolean",
            "brtrue ->9", "ldc.i4.1", "br ->10", "ldc.i4.2", "ldc.i4.2",
            "call static MissileControlMod.Hooks::PatchSteeringLimits(" + sequence + ",System.Int32,System.Int32,System.Int32):" + sequence, "ret" };
        var actual = limits.Select(i => Describe(i, limits)).ToArray();
        foreach (string line in actual.Except(expected)) Console.WriteLine("STEERING-LIMITS " + line);
        Check(actual.SequenceEqual(expected), "Hooks.SteeringLimits passes its source through MissileControlModSteeringShape, with long branches");

        var diagnostics = Method("SeaPowerModSupport.EffectAudio", "EnableDiagnostics").Body.Instructions;
        var file = diagnostics.Where(i => (i.Operand as MethodReference)?.Name == "GetLegacyFile").ToList();
        Check(file.Count == 1 && Describe(file[0], diagnostics) ==
                "call static AnchorChain.BetaCompatibilityCalls::GetLegacyFile(SeaPower.FileManager,System.String,System.String):System.String" &&
            file[0].Previous.OpCode == Mono.Cecil.Cil.OpCodes.Ldnull && file[0].Previous.Previous.OpCode == Mono.Cecil.Cil.OpCodes.Ldarg_3,
            "EffectAudio.EnableDiagnostics looks its file up through GetLegacyFile");
        Check(!module.GetMemberReferences().Any(m => m.DeclaringType.FullName == "SeaPower.FileManager" && m.Name == "GetFile"),
            "No FileManager.GetFile(string,string) reference remains");

        var guard = Method("ACModActivation.Guard", "Allow").Body.Instructions;
        Check(guard.Count(i => i.OpCode == Mono.Cecil.Cil.OpCodes.Call && (i.Operand as MethodReference)?.FullName ==
                "System.String AnchorChain.BetaAssemblyPolicy::OriginalLocation(System.Reflection.Assembly)") == 2 &&
            !Types(module.Types).SelectMany(t => t.Methods).Where(m => m.HasBody).SelectMany(m => m.Body.Instructions)
                .Any(i => (i.Operand as MethodReference)?.Name == "get_Location"),
            "Both Mod Manager guard location reads use OriginalLocation");

        // Every Seapower-Scripts member the written image references resolves
        // against the beta assembly, operands and tokens alike.
        var missing = new List<string>(); int resolved = 0;
        foreach (var member in module.GetMemberReferences()) {
            if (member.DeclaringType?.Scope is not AssemblyNameReference scope || scope.Name != "Seapower-Scripts") continue;
            IMemberDefinition definition = null;
            try { definition = member is MethodReference m ? m.Resolve() : member is FieldReference f ? f.Resolve() : null; } catch (Exception) { }
            if (definition == null) missing.Add(member.FullName); else resolved++;
        }
        foreach (var type in Types(module.Types)) foreach (var method in type.Methods.Where(m => m.HasBody))
            foreach (var instruction in method.Body.Instructions) {
                if (instruction.Operand is not MemberReference member || member.DeclaringType?.Scope is not AssemblyNameReference scope ||
                    scope.Name != "Seapower-Scripts") continue;
                IMemberDefinition definition = null;
                try {
                    definition = member is MethodReference m ? m.Resolve() : member is FieldReference f ? f.Resolve() :
                        member is TypeReference t ? t.Resolve() : null;
                } catch (Exception) { }
                if (definition == null) missing.Add(type.FullName + "." + method.Name + ": " + member.FullName); else resolved++;
            }
        foreach (string failure in missing) Console.WriteLine("MISSING MissileControlMod " + failure);
        Check(missing.Count == 0 && resolved > 200, "Every MissileControlMod Seapower-Scripts method, field and type operand resolves on the beta (" + resolved + ")");

        // Negative control: the author's image really carries the missing member.
        using var original = ModuleDefinition.ReadModule(source, new ReaderParameters { AssemblyResolver = context.Resolver });
        var stale = original.GetMemberReferences().OfType<MethodReference>().Where(m => m.DeclaringType.FullName == "SeaPower.FileManager" && m.Name == "GetFile").ToList();
        Check(stale.Count == 1 && stale[0].Parameters.Select(p => p.ParameterType.FullName).SequenceEqual(new[] { "System.String", "System.String" }) &&
            stale[0].Resolve() == null, "The author's GetFile(string,string) does not exist on the beta");
    }

    static void MissileControlModSteering(Assembly assembly, Type compatibility)
    {
        var hooks = assembly.GetType("MissileControlMod.Hooks", true);
        var steering = hooks.GetMethod("SteeringLimits", MissileControlModAll);
        var legacySteering = hooks.GetMethod("LegacySteeringLimits", MissileControlModAll);
        var patch = hooks.GetMethod("PatchSteeringLimits", MissileControlModAll);
        var read = compatibility.GetMethod("Read", MissileControlModAll);
        var course = AccessTools.Method(typeof(WeaponBase), "setCourseTowardsPosition", new[] { typeof(UnityEngine.Vector3), typeof(bool), typeof(bool) });
        var legacy = AccessTools.Method(typeof(WeaponBase), "setCourseTowardsPositionLegacy", new[] { typeof(UnityEngine.Vector3), typeof(bool), typeof(bool), typeof(float) });
        var formula = typeof(BetaCompatibilityCalls).GetMethod(nameof(BetaCompatibilityCalls.MissileControlModGLimitedTurnRate));
        Check(course != null && legacy != null && compatibility.GetField("LegacyCourse", MissileControlModAll)?.GetValue(null) != null,
            "The author's LegacyCourse binds on the beta, so it expects 1/1/2");
        List<CodeInstruction> Run(MethodInfo transpiler, List<CodeInstruction> body, params object[] extra)
        {
            try { return ((IEnumerable<CodeInstruction>)transpiler.Invoke(null, new object[] { body }.Concat(extra).ToArray())).ToList(); }
            catch (TargetInvocationException ex) when (ex.InnerException != null) { throw ex.InnerException; }
        }
        int Calls(List<CodeInstruction> list, string name) => list.Count(i => (i.operand as MethodInfo)?.Name == name);

        // Negative control: the author's unchanged check on beta's stream.
        string failure = null;
        try { Run(patch, PatchProcessor.GetOriginalInstructions(course), 1, 1, 2); } catch (Exception ex) { failure = ex.Message; }
        Check(failure == "Native steering limit hook shape changed: 0/0/2", "Without the bridge the author's check fails as captured: " + failure);

        // Harmony's reader (the real patch) and the author's own Read (its validator).
        foreach (var (label, body) in new[] { ("Harmony", PatchProcessor.GetOriginalInstructions(course)),
            ("Compatibility.Read", (List<CodeInstruction>)read.Invoke(null, new object[] { course })) }) {
            int before = body.Count;
            var result = Run(steering, body);
            Check(result.Count == before + 4 + 2 * 4 && Calls(result, "EffectiveG") == 1 && Calls(result, "EffectiveRate") == 3 &&
                result.Count(i => Equals(i.operand, formula)) == 1 && Calls(result, "GLimitedTurnRate") == 0,
                "Adapted SteeringLimits wraps the beta loads 1/1/2 (" + label + ")");
            string Text(CodeInstruction i) => i.opcode.Name + (i.operand is MemberInfo m ? " " + m.DeclaringType.Name + "." + m.Name : "");
            var head = result.Take(14).Select(Text).ToArray();
            var want = new[] { "ldarg.0", "ldfld WeaponBase._ap", "ldfld AmmunitionParameters._maxTurnG", "ldarg.0", "call Hooks.EffectiveG",
                "ldarg.0", "ldfld WeaponBase._ap", "ldfld AmmunitionParameters._maxTurnRateDegrees", "ldarg.0", "call Hooks.EffectiveRate",
                "ldarg.0", "call ObjectBase.getVelocityInKnots", "call BetaCompatibilityCalls.MissileControlModGLimitedTurnRate", "stloc.0" };
            foreach (string line in head) Console.WriteLine("STEERING " + label + " " + line);
            Check(head.SequenceEqual(want), "Stable evaluation order EffectiveG, EffectiveRate, speed (" + label + ")");
        }
        var original = PatchProcessor.GetOriginalInstructions(course);
        var copy = original.Select(i => (i.opcode, i.operand)).ToList();
        BetaCompatibilityCalls.MissileControlModSteeringShape(original).ToList();
        Check(original.Select(i => (i.opcode, i.operand)).SequenceEqual(copy), "The bridge leaves the caller's instructions unchanged");

        var legacyBody = PatchProcessor.GetOriginalInstructions(legacy);
        var passed = BetaCompatibilityCalls.MissileControlModSteeringShape(legacyBody).ToList();
        Check(passed.Count == legacyBody.Count && passed.Zip(legacyBody, ReferenceEquals).All(x => x), "Bridge is a no-op on setCourseTowardsPositionLegacy");
        var legacyResult = Run(legacySteering, PatchProcessor.GetOriginalInstructions(legacy));
        Check(Calls(legacyResult, "EffectiveRate") == 3, "The author's LegacySteeringLimits still finds 0/1/2 on the beta");
        var shifted = PatchProcessor.GetOriginalInstructions(course);
        shifted.Insert(0, new CodeInstruction(OpCodes.Nop));
        shifted[2].labels.Add(default);
        Check(BetaCompatibilityCalls.MissileControlModSteeringShape(shifted).Count() == shifted.Count, "A labelled prologue passes through unchanged");
    }

    static void MissileControlModFormula()
    {
        // Execute beta's real GLimitedTurnRate IL with only its two
        // AmmunitionParameters loads rebound to a plain fixture, as
        // HailGuardFixture does; WeaponBase's static initializer never runs.
        var native = AccessTools.Method(typeof(WeaponBase), "GLimitedTurnRate", new[] { typeof(AmmunitionParameters), typeof(float) });
        var method = new DynamicMethod("MissileControlModNativeLimit", typeof(float), new[] { typeof(MissileControlModLimits), typeof(float) }, typeof(BetaApiTests), true);
        var il = method.GetILGenerator(); int rebound = 0;
        var body = PatchProcessor.GetOriginalInstructions(native, il);
        foreach (var instruction in body) {
            foreach (var label in instruction.labels) il.MarkLabel(label);
            object operand = instruction.operand;
            if (operand is FieldInfo field && field.DeclaringType == typeof(AmmunitionParameters) && (field.Name == "_maxTurnG" || field.Name == "_maxTurnRateDegrees")) {
                operand = typeof(MissileControlModLimits).GetField(field.Name == "_maxTurnG" ? "G" : "Rate"); rebound++;
            }
            if (operand == null) il.Emit(instruction.opcode);
            else if (operand is FieldInfo target) il.Emit(instruction.opcode, target);
            else if (operand is MethodInfo call) il.Emit(instruction.opcode, call);
            else if (operand is float constant) il.Emit(instruction.opcode, constant);
            else if (operand is Label jump) il.Emit(instruction.opcode, jump);
            else if (operand is LocalBuilder local) il.Emit(instruction.opcode, local);
            else throw new Exception("Uninspected GLimitedTurnRate operand: " + operand);
        }
        Check(rebound == 2, "Fixture rebinds exactly the two native limit loads");
        var nativeLimit = (Func<MissileControlModLimits, float, float>)method.CreateDelegate(typeof(Func<MissileControlModLimits, float, float>));
        int Bits(float value) => BitConverter.ToInt32(BitConverter.GetBytes(value), 0);
        int compared = 0, mismatched = 0;
        void Compare(float g, float rate, float knots)
        {
            compared++;
            float a = nativeLimit(new MissileControlModLimits { G = g, Rate = rate }, knots), b = BetaCompatibilityCalls.MissileControlModGLimitedTurnRate(g, rate, knots);
            if (Bits(a) != Bits(b) && !(float.IsNaN(a) && float.IsNaN(b))) { if (mismatched++ < 5) Console.WriteLine("LIMIT MISMATCH " + g + "/" + rate + "/" + knots + ": " + a + " vs " + b); }
        }
        var edges = new[] { 0f, -0f, 1e-30f, 0.5f, 1f, 9.8f, 20f, 35f, 50f, 70f, 100f, 360f, 600f, 1500f, 3000f, 1e30f, -1f, -50f,
            float.MaxValue, float.Epsilon, float.PositiveInfinity, float.NegativeInfinity, float.NaN };
        foreach (float g in edges) foreach (float rate in edges) foreach (float knots in edges) Compare(g, rate, knots);
        var random = new Random(261026);
        for (int i = 0; i < 200000; i++)
            Compare((float)(random.NextDouble() * 100), (float)(random.NextDouble() * 400), (float)(random.NextDouble() * 4000));
        Check(mismatched == 0, "MissileControlModGLimitedTurnRate matches native GLimitedTurnRate bit for bit over " + compared + " inputs");
        // The AIM-9X example of the verification: MaxTurnG 50, MaxTurnRate 100.
        Check(Math.Abs(nativeLimit(new MissileControlModLimits { G = 50, Rate = 100 }, 600) - 90.96f) < 0.05f &&
            Math.Abs(BetaCompatibilityCalls.MissileControlModGLimitedTurnRate(50, 100, 1500) - 36.38f) < 0.05f &&
            Math.Abs(BetaCompatibilityCalls.MissileControlModGLimitedTurnRate(70, 100, 1500) - 50.93f) < 0.05f,
            "G-limited AIM-9X rates: 91.0 deg/s at 600 kt, 36.4 at 1,500 kt, 50.9 with +20 g");

        // Operation for operation: the bridge is the native body with the two
        // field loads turned into arguments.
        using var anchor = ModuleDefinition.ReadModule(typeof(BetaAssemblyPolicy).Assembly.Location);
        using var game = ModuleDefinition.ReadModule(native.Module.Assembly.Location);
        var bridgeBody = anchor.GetType("AnchorChain.BetaCompatibilityCalls").Methods.Single(m => m.Name == nameof(BetaCompatibilityCalls.MissileControlModGLimitedTurnRate)).Body.Instructions;
        var nativeBody = game.GetType("SeaPower.WeaponBase").Methods.Single(m => m.Name == "GLimitedTurnRate").Body.Instructions;
        var map = new Dictionary<string, string> { ["ldarg.1"] = "ldarg.2", ["ldloc.0"] = "ldarg.0", ["ldloc.1"] = "ldarg.1", ["stloc.1"] = "starg.s",
            ["ldloc.2"] = "ldloc.0", ["stloc.2"] = "stloc.0", ["ldloc.3"] = "ldloc.1", ["stloc.3"] = "stloc.1", ["ble.un.s"] = "ble.un" };
        string Shape(Mono.Cecil.Cil.Instruction i, IList<Mono.Cecil.Cil.Instruction> all, bool mapped)
        {
            string text = MissileControlModDescribe(i, all);
            string name = i.OpCode.Name.Replace("ble.un.s", "ble.un");
            if (mapped && map.TryGetValue(i.OpCode.Name, out string to)) name = to;
            return i.Operand is Mono.Cecil.Cil.Instruction || i.Operand is Mono.Cecil.ParameterDefinition ? name : name + text.Substring(i.OpCode.Name.Length);
        }
        var nativeShape = nativeBody.Skip(6).Select(i => Shape(i, nativeBody, true)).ToArray();
        var bridgeShape = bridgeBody.Select(i => Shape(i, bridgeBody, false)).ToArray();
        foreach (string line in bridgeShape) Console.WriteLine("LIMIT IL " + line);
        Check(nativeShape.SequenceEqual(bridgeShape), "The bridge's IL is native GLimitedTurnRate's with arguments for the two loads");
    }

    static void MissileControlModPatchParameters(Assembly assembly)
    {
        // HarmonyX binds a patch parameter by the original's parameter name, or
        // as __instance, __result, __state or __originalMethod.
        Type Hooks(string name) => assembly.GetType("MissileControlMod." + name, true);
        var missile = typeof(Missile);
        var bindings = new (MethodBase target, string owner, string patch)[] {
            (AccessTools.Method(missile, "Container_Launch"), "Hooks", "Launched"),
            (AccessTools.Method(missile, "OnFixedUpdate"), "Hooks", "BeforeTick"),
            (AccessTools.Method(missile, "OnFixedUpdate"), "Hooks", "AfterTick"),
            (AccessTools.Method(typeof(WeaponBase), "setCourseTowardsPosition"), "Hooks", "Course"),
            (AccessTools.Method(missile, "PerformMoveForward"), "Hooks", "BeforeMove"),
            (AccessTools.Method(missile, "PerformMoveForward"), "Hooks", "AfterMove"),
            (AccessTools.Method(missile, "ScheduleFlightEffects"), "Hooks", "AllowSchedule"),
            (AccessTools.Method(AccessTools.Inner(missile, "ToBearing"), "takeAction"), "Hooks", "ToBearing"),
            (AccessTools.Method(missile, "SaveStateToFile"), "Hooks", "Save"),
            (AccessTools.Method(missile, "LoadStateFromFile"), "Hooks", "Load"),
            (AccessTools.Method(missile, "CalculateInterceptAimPoint"), "Hooks", "EarlyInterceptPlanner"),
            (AccessTools.Method(AccessTools.Inner(missile, "Launch"), "takeAction"), "Hooks", "InitialDuration"),
            (AccessTools.Method(AccessTools.Inner(missile, "GoToSurface"), "takeAction"), "Hooks", "SurfaceInitialDuration"),
            (AccessTools.Method(typeof(WeaponBase), "CommonLaunchSettings"), "LowLow", "Launched"),
            (AccessTools.Method(missile, "SaveStateToFile"), "LowLow", "Save"),
            (AccessTools.Method(missile, "LoadStateFromFile"), "LowLow", "Load"),
            (AccessTools.Method(missile, "LoadStateFromFile"), "LowLow", "Loaded"),
            (AccessTools.Method(typeof(GizmoLayer), "AddGizmo"), "LowLowMap", "Added") };
        foreach (var (target, owner, name) in bindings) {
            Check(target != null, "MissileControlMod patch target exists on the beta: " + owner + "." + name);
            var patch = Hooks(owner).GetMethod(name, MissileControlModAll);
            Check(patch != null && patch.IsStatic, "MissileControlMod patch method exists: " + owner + "." + name);
            var returns = (target as MethodInfo)?.ReturnType ?? typeof(void);
            foreach (var parameter in patch.GetParameters()) {
                var type = parameter.ParameterType.IsByRef ? parameter.ParameterType.GetElementType() : parameter.ParameterType;
                bool ok = parameter.Name switch {
                    "__instance" => type.IsAssignableFrom(target.DeclaringType),
                    "__result" => returns != typeof(void) && type == returns,
                    "__originalMethod" => type == typeof(MethodBase),
                    "source" => type == typeof(IEnumerable<CodeInstruction>),
                    _ => target.GetParameters().SingleOrDefault(p => p.Name == parameter.Name) is ParameterInfo match && match.ParameterType == type,
                };
                Check(ok, "MissileControlMod patch parameter binds on the beta: " + owner + "." + name + "(" + parameter.Name + ")");
            }
        }
    }
}
