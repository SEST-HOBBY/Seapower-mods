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
    const BindingFlags TacAll = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance;

    static string Sha256Of(string path)
    {
        using var sha = System.Security.Cryptography.SHA256.Create();
        return BitConverter.ToString(sha.ComputeHash(File.ReadAllBytes(path))).Replace("-", "").ToLowerInvariant();
    }

    // Runs one pinned adapter on an author image the way Prepare does
    // (AdaptCapturedImage, then the native-member check), and writes the
    // result under the test cache. Used for images that SEST's loader starts
    // by another path (a pinned BepInEx plugin, a nested-loader companion),
    // so these checks do not depend on that start path.
    static string AdaptPinnedImage(R6Context context, string source, string hash, out string audit)
    {
        var native = (ModuleDefinition)typeof(BetaAssemblyPolicy).GetMethod("NativeModule", TacAll).Invoke(null, new object[] { context.Native });
        using var module = ModuleDefinition.ReadModule(source, new ReaderParameters { InMemory = true, AssemblyResolver = context.Resolver });
        Check(((List<string>)typeof(BetaAssemblyPolicy).GetMethod("InvalidNativeFields", TacAll).Invoke(null, new object[] { module, native })).Count == 0,
            "Native field layout check passes: " + Path.GetFileName(source));
        try { audit = (string)typeof(BetaAssemblyPolicy).GetMethod("AdaptCapturedImage", TacAll).Invoke(null, new object[] { module, native, hash }); }
        catch (TargetInvocationException ex) { throw new Exception("Adapter refused " + Path.GetFileName(source) + ": " + ex.InnerException); }
        var missing = (List<string>)typeof(BetaAssemblyPolicy).GetMethod("UnresolvedNativeMembers", TacAll).Invoke(null, new object[] { module, native });
        Check(missing.Count == 0, "Adapted " + Path.GetFileName(source) + " names only game members 261123 has (" + String.Join("; ", missing) + ")");
        string directory = Path.Combine(context.Cache, "r6-pinned", hash);
        Directory.CreateDirectory(directory);
        string target = Path.Combine(directory, module.Assembly.Name.Name + ".dll");
        module.Write(target);
        return target;
    }

    static void R6_BetterTacMap261123(R6Context context)
    {
        const string hash = "bdc418647e5a4d9dc98d532ea813d4a9158d9171e70ffb753e39bfca1152b142";
        const string audit = "drawing-save-split=3, ecs-world=2, launch-range=2, locations=1";
        string source = Path.Combine(context.Workshop, "3768036424", "BetterTacMap.dll");
        byte[] original = File.ReadAllBytes(source);
        Check(Sha256Of(source) == hash, "Better Tac Map fixture is the inspected 0.2.0 author image");
        Check((string)typeof(BetaAssemblyPolicy).GetField("BetterTacMap261123Audit", TacAll).GetValue(null) == audit, "Better Tac Map audit is the inspected 261123 audit");

        // The pinned BepInEx start belongs to the loader. Without it, Prepare
        // leaves this non-Anchor-Chain image alone and logs nothing; with it,
        // the image is admitted through this adapter with one ADAPTED line.
        var messages = new List<string>();
        string prepared = BetaAssemblyPolicy.Prepare(source, context.Native, context.Cache, messages.Add);
        Check(prepared == null ? messages.Count == 0 :
            prepared != source && messages.Count == 1 && messages[0].StartsWith("ADAPTED BetterTacMap in private cache: " + audit + ";"),
            "Better Tac Map through Prepare: silent library skip without the pinned start, one ADAPTED line with it: " + String.Join(" | ", messages));

        string adapted = AdaptPinnedImage(context, source, hash, out string actual);
        Check(actual == audit, "Better Tac Map rewrite audit is exactly " + audit + " (actual: " + actual + ")");
        Check(original.SequenceEqual(File.ReadAllBytes(source)), "Original Better Tac Map DLL retained byte for byte");

        using (var before = ModuleDefinition.ReadModule(source, new ReaderParameters { AssemblyResolver = context.Resolver }))
        using (var after = ModuleDefinition.ReadModule(adapted, new ReaderParameters { AssemblyResolver = context.Resolver })) {
            // Only the four methods holding a rewrite differ from the author's.
            var changed = new List<string>(); int compared = 0;
            foreach (var t in Types(before.Types)) foreach (var method in t.Methods.Where(m => m.HasBody)) {
                var written = after.GetType(t.FullName).Methods.Single(m => m.FullName == method.FullName);
                compared++;
                if (!TopoInstructions(method).SequenceEqual(TopoInstructions(written))) changed.Add(t.FullName + "::" + method.Name);
            }
            var expected = new[] { "BetterTacMap.Depth.EcsWorldAccess::EnsureResolved", "BetterTacMap.Firing.WeaponMountReader::TryGetBestRangeUnity",
                "BetterTacMap.ModSettings::MigrateLegacySettings", "BetterTacMap.WeaponRange.WeaponRangeReader/<>c__DisplayClass2_0::<MaxRangeInMapDegrees>b__1" };
            Check(compared == 186 && changed.OrderBy(x => x, StringComparer.Ordinal).SequenceEqual(expected),
                "Of " + compared + " Better Tac Map bodies only the four rewritten ones differ (actual: " + String.Join(", ", changed) + ")");

            var ranges = Types(after.Types).SelectMany(t => t.Methods).Where(m => m.HasBody).SelectMany(m => m.Body.Instructions)
                .Select(i => i.Operand as MethodReference).Where(r => r?.Name == "EffectiveMaxLaunchRange").ToList();
            Check(ranges.Count == 2 && ranges.All(r => r.Parameters.Select(p => p.ParameterType.FullName).SequenceEqual(new[] { "SeaPower.ObjectBase", "System.Single" })),
                "Both launch-range sites call the 261123 (ObjectBase, float) overload");
            var lastTwo = Types(after.Types).SelectMany(t => t.Methods).Where(m => m.HasBody)
                .SelectMany(m => m.Body.Instructions.Where(i => (i.Operand as MethodReference)?.Name == "EffectiveMaxLaunchRange")).ToList();
            Check(lastTwo.All(i => i.Previous.OpCode == Mono.Cecil.Cil.OpCodes.Ldc_R4 && Equals(i.Previous.Operand, -1f)),
                "Both launch-range sites pass the game's own default run depth (-1)");

            var ensure = after.GetType("BetterTacMap.Depth.EcsWorldAccess").Methods.Single(m => m.Name == "EnsureResolved");
            var tokens = ensure.Body.Instructions.Where(i => i.OpCode == Mono.Cecil.Cil.OpCodes.Ldtoken).Select(i => (TypeReference)i.Operand).ToList();
            Check(tokens.Count == 2 && tokens.All(t => t.FullName == "Unity.Entities.World" && ((AssemblyNameReference)t.Scope).Name == "Unity.Entities"),
                "EcsWorldAccess looks the world up on Unity.Entities.World");
            Check(!after.GetTypeReferences().Any(t => t.FullName == "World" && (t.Scope as AssemblyNameReference)?.Name == "Seapower-Scripts"),
                "The adapted image no longer names the removed global World type");
            Check(ensure.Body.Instructions.Any(i => Equals(i.Operand, "Unity.Entities")), "The author's assembly-scan fallback stays");

            var patch = after.GetType("BetterTacMap.Patches.ModDrawingSavePatch");
            var classAttribute = patch.CustomAttributes.Single();
            Check(classAttribute.AttributeType.FullName == "HarmonyLib.HarmonyPatch" && classAttribute.ConstructorArguments.Count == 0,
                "ModDrawingSavePatch keeps a bare class-level [HarmonyPatch]");
            string Target(string name) {
                var a = patch.Methods.Single(m => m.Name == name).CustomAttributes.Single();
                return ((TypeReference)a.ConstructorArguments[0].Value).FullName + "::" + a.ConstructorArguments[1].Value;
            }
            // The Finalizer sits on WriteMissionToFile, the one caller of both
            // SavePlayerDrawings and WriteSave, so a throw between them still
            // reattaches what the Prefix detached.
            Check(Target("Prefix") == "SeaPower.SaveLoadManager::SavePlayerDrawings" && Target("Postfix") == "SeaPower.SaveMapContent::WriteSave" &&
                Target("Finalizer") == "SeaPower.SaveLoadManager::WriteMissionToFile",
                "Drawing save patch split onto SavePlayerDrawings and WriteSave, reattaching on their caller WriteMissionToFile");
            foreach (var t in Types(before.Types).Where(t => t.FullName != patch.FullName)) {
                var mine = after.GetType(t.FullName);
                Check(t.CustomAttributes.Select(a => a.Constructor.FullName + String.Join(",", a.ConstructorArguments.Select(x => x.Value?.ToString())))
                    .SequenceEqual(mine.CustomAttributes.Select(a => a.Constructor.FullName + String.Join(",", a.ConstructorArguments.Select(x => x.Value?.ToString())))) &&
                    t.Methods.All(m => m.CustomAttributes.Count == mine.Methods.Single(x => x.FullName == m.FullName).CustomAttributes.Count),
                    "Other Harmony attributes are the author's: " + t.FullName);
            }
        }

        // The CLR view: the split attributes bind to real 261123 methods.
        var assembly = Assembly.LoadFile(adapted);
        var type = assembly.GetType("BetterTacMap.Patches.ModDrawingSavePatch", true);
        Check(type.GetCustomAttributes(typeof(HarmonyPatch), false).Length == 1, "Bare class-level HarmonyPatch instantiates");
        MethodInfo Original(string name) {
            var info = ((HarmonyPatch)type.GetMethod(name, TacAll).GetCustomAttributes(typeof(HarmonyPatch), false).Single()).info;
            return AccessTools.DeclaredMethod(info.declaringType, info.methodName);
        }
        var save = Original("Prefix"); var write = Original("Postfix"); var mission = Original("Finalizer");
        Check(save != null && save.DeclaringType == typeof(SaveLoadManager) && save.IsStatic && save.GetParameters().Length == 0,
            "Prefix resolves to SaveLoadManager.SavePlayerDrawings()");
        Check(write != null && write.DeclaringType == typeof(SaveMapContent) && write.GetParameters()[0].Name == "ini" &&
            write.GetParameters()[0].ParameterType == typeof(IniHandler),
            "Postfix(IniHandler ini) resolves to SaveMapContent.WriteSave, binding ini by name");
        Check(mission != null && mission.DeclaringType == typeof(SaveLoadManager) && mission.IsStatic &&
            typeof(SaveLoadManager).GetMethods(TacAll).Count(m => m.Name == "WriteMissionToFile") == 1,
            "Finalizer resolves to the one SaveLoadManager.WriteMissionToFile, which calls SavePlayerDrawings and WriteSave");
        // The guarantee itself: the Prefix's SavePlayerDrawings and the
        // Postfix's WriteSave both run inside WriteMissionToFile, so a throw
        // in either or between them leaves through the Finalizer.
        var game = (ModuleDefinition)typeof(BetaAssemblyPolicy).GetMethod("NativeModule", TacAll).Invoke(null, new object[] { context.Native });
        var body = game.GetType("SeaPower.SaveLoadManager").Methods.Single(m => m.Name == "WriteMissionToFile").Body.Instructions;
        Check(body.Any(i => (i.Operand as MethodReference)?.Name == "SavePlayerDrawings") &&
            body.Any(i => (i.Operand as MethodReference)?.Name == "WriteSave"),
            "WriteMissionToFile, the Finalizer's target, holds both the Prefix's SavePlayerDrawings and the Postfix's WriteSave");
        foreach (var (owner, name) in new[] { ("BetterTacMap.Depth.EcsWorldAccess", "EnsureResolved"),
            ("BetterTacMap.Firing.WeaponMountReader", "TryGetBestRangeUnity"),
            ("BetterTacMap.WeaponRange.WeaponRangeReader+<>c__DisplayClass2_0", "<MaxRangeInMapDegrees>b__1") }) {
            var method = assembly.GetType(owner, true).GetMethod(name, TacAll);
            System.Runtime.CompilerServices.RuntimeHelpers.PrepareMethod(method.MethodHandle);
            Check(true, "Rewritten Better Tac Map method compiles on 261123: " + owner + "::" + name);
        }
        var range = typeof(AmmunitionParameters).GetMethod("EffectiveMaxLaunchRange", new[] { typeof(ObjectBase), typeof(float) });
        Check(range != null && typeof(AmmunitionParameters).GetMethods().Count(m => m.Name == "EffectiveMaxLaunchRange") == 1,
            "261123 has the one (ObjectBase, float) launch-range overload");

        var adapter = typeof(BetaAssemblyPolicy).GetMethod("AdapterFor", TacAll).Invoke(null, new object[] { hash });
        Check(adapter != null && (string)adapter.GetType().GetField("Name", TacAll).GetValue(adapter) == "BetterTacMap261123",
            "Better Tac Map 0.2.0 is pinned to its 261123 adapter by exact hash");
    }
}
