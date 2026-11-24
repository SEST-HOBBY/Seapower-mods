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

    // Enhanced Decoy Mod 0.5.4 (7cd4f160) on 0.9.3-261123: every read of the
    // retired _ammoInUse field goes through the native read-only property,
    // nothing else changes, and the author's own startup validators run.
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
        var changed = new List<int>();
        using (var author = ModuleDefinition.ReadModule(source, new ReaderParameters { AssemblyResolver = context.Resolver }))
        using (var adapted = ModuleDefinition.ReadModule(prepared, new ReaderParameters { AssemblyResolver = context.Resolver })) {
            int fields = 0, calls = 0, locations = 0, compared = 0;
            var authorTypes = Types(author.Types).ToList(); var adaptedTypes = Types(adapted.Types).ToList();
            Check(authorTypes.Select(t => t.FullName).SequenceEqual(adaptedTypes.Select(t => t.FullName)), "Adapted Enhanced Decoy image has the author's types");
            for (int t = 0; t < authorTypes.Count; t++) for (int m = 0; m < authorTypes[t].Methods.Count; m++) {
                var written = authorTypes[t].Methods[m]; var actual = adaptedTypes[t].Methods[m];
                Check(written.FullName == actual.FullName, "Adapted Enhanced Decoy method order is the author's: " + written.FullName);
                if (!written.HasBody) continue;
                compared++;
                int reads = written.Body.Instructions.Count(i => i.Operand is FieldReference f && f.Name == "_ammoInUse" && f.DeclaringType.FullName == "SeaPower.WeaponSystemChaff");
                int getters = actual.Body.Instructions.Count(i => i.OpCode == Mono.Cecil.Cil.OpCodes.Callvirt && i.Operand is MethodReference c &&
                    c.Name == "get__ammoInUse" && c.DeclaringType.FullName == "SeaPower.WeaponSystemChaff" && c.HasThis && c.Parameters.Count == 0);
                int located = actual.Body.Instructions.Count(i => i.Operand is MethodReference c && c.Name == "OriginalLocation" &&
                    c.DeclaringType.FullName == typeof(BetaAssemblyPolicy).FullName);
                Check(!actual.Body.Instructions.Any(i => i.Operand is FieldReference f && f.Name == "_ammoInUse" && f.DeclaringType.FullName == "SeaPower.WeaponSystemChaff"),
                    "Adapted Enhanced Decoy no longer names the _ammoInUse field: " + actual.FullName);
                Check(getters == reads + written.Body.Instructions.Count(i => i.Operand is MethodReference c && c.Name == "get__ammoInUse"),
                    "Each Enhanced Decoy _ammoInUse read became one getter call: " + actual.FullName);
                fields += reads; calls += getters; locations += located;
                bool same = TopoInstructions(written).SequenceEqual(TopoInstructions(actual));
                Check(same == (reads == 0 && located == 0), "Only Enhanced Decoy bodies holding an ammunition read or a location read differ: " + actual.FullName);
                if (!same) changed.Add(actual.MetadataToken.ToInt32());
            }
            Check(fields == 33 && calls == 33 && locations == 2, "Enhanced Decoy: 33 _ammoInUse reads now call the native getter, 2 location reads keep the Workshop path (" + fields + "/" + calls + "/" + locations + ")");
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
        // 0.5.4's hook validator still requires the single chaff attacher
        // field WeaponSystemChaff._chaff, which 261123 replaced with
        // _rounds[i].Attacher. The author's own check rejects 261123 there,
        // by name, before any transpiler is judged or any patch is applied.
        Exception hooks = null;
        try { assembly.GetType("EnhancedDecoyMod.Hooks", true).GetMethod("Validate", ChaffAll).Invoke(null, null); }
        catch (TargetInvocationException ex) { hooks = ex.InnerException; }
        Check(typeof(WeaponSystemChaff).GetField("_chaff", ChaffAll) == null, "261123 WeaponSystemChaff has no single _chaff attacher");
        Check(hooks is TypeInitializationException init && init.TypeName == "EnhancedDecoyMod.Hooks" &&
            init.InnerException is MissingFieldException missing && missing.Message.Contains("SeaPower.WeaponSystemChaff._chaff"),
            "Enhanced Decoy's own hook validator rejects 261123 by name (WeaponSystemChaff._chaff), not through the adapter: " + hooks);
        using (var author = ModuleDefinition.ReadModule(source, new ReaderParameters { AssemblyResolver = context.Resolver })) {
            var start = author.GetType("EnhancedDecoyMod.Plugin").Methods.Single(m => m.Name == "InitializeWhenModEnabled").Body;
            var guard = start.ExceptionHandlers.SingleOrDefault(h => h.HandlerType == Mono.Cecil.Cil.ExceptionHandlerType.Catch);
            var hookCall = start.Instructions.Single(i => i.Operand is MethodReference c && c.Name == "Validate" && c.DeclaringType.FullName == "EnhancedDecoyMod.Hooks");
            var patchCall = start.Instructions.First(i => i.Operand is MethodReference c && c.Name == "Patch" && c.DeclaringType.FullName == "HarmonyLib.Harmony");
            Check(guard != null && guard.HandlerType == Mono.Cecil.Cil.ExceptionHandlerType.Catch && guard.CatchType.FullName == "System.Exception" &&
                hookCall.Offset >= guard.TryStart.Offset && hookCall.Offset < guard.TryEnd.Offset && patchCall.Offset > hookCall.Offset &&
                start.Instructions.SkipWhile(i => i != guard.HandlerStart).Take(6).Any(i => i.Operand is MethodReference c && c.Name == "UnpatchSelf") &&
                start.Instructions.Any(i => i.OpCode == Mono.Cecil.Cil.OpCodes.Ldstr && Equals(i.Operand, "Initialization rolled back: ")),
                "So on 261123 the author's startup stops before its first patch, unpatches itself and logs one 'Initialization rolled back' line");
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
