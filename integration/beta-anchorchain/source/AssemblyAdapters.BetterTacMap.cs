// Better Tac Map 0.2.0 (bdc41864, Workshop 3768036424; BepInPlugin
// toemel.bettertacmap, BaseUnityPlugin BetterTacMap.BetterTacMapMod) on
// 0.9.3-261123. SEST's loader starts it as a pinned BepInEx-only plugin; this
// file owns only its image rewrite. Three 261123 changes break it:
//  - EffectiveMaxLaunchRange gained an optional run depth (float, default -1);
//    its two call sites get the game's own default appended (launch-range).
//  - The global World type the image's EcsWorldAccess names was dropped from
//    Seapower-Scripts; both ldtoken operands now name Unity.Entities.World,
//    which has the two properties the mod reads. Its own assembly-scan
//    fallback stays (ecs-world).
//  - SaveLoadManager.WriteDrawingData is gone. Saves now build the player
//    drawing list in SavePlayerDrawings() and write it with
//    SaveMapContent.WriteSave(IniHandler ini, ...). ModDrawingSavePatch's
//    targets are split by rewriting its Harmony attributes only (no IL is
//    copied or changed): Prefix (detach mod drawings) on SavePlayerDrawings,
//    Postfix(IniHandler ini) (write [BetterTacMap]) on WriteSave, and
//    Finalizer (reattach) on WriteMissionToFile, the one method that calls
//    both, so a throw in SavePlayerDrawings or anywhere after it still
//    reattaches what the Prefix detached (drawing-save-split). Without this
//    PatchAll throws on that class and every later patch class is skipped.
// The shared locations rule maps its one Assembly.Location read (ModSettings).
using System;
using System.IO;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    internal const string BetterTacMap020Hash = "bdc418647e5a4d9dc98d532ea813d4a9158d9171e70ffb753e39bfca1152b142";
    internal const string BetterTacMap261123Audit = "drawing-save-split=3, ecs-world=2, launch-range=2, locations=1";

    private static ImageAdapter BetterTacMap261123Adapter() => new ImageAdapter {
        Name = "BetterTacMap261123", Hashes = new[] { BetterTacMap020Hash },
        RequireNative = BetterTacMap261123RequireNative,
        RewriteMethod = BetterTacMap261123Rewrite,
        RewriteCall = BetterTacMap261123Call,
        Finish = BetterTacMap261123Finish,
        ExpectedAudit = BetterTacMap261123Audit,
    };

    private static bool BetterTacMap261123Call(AdapterScope scope, TypeDefinition type, MethodDefinition method, Instruction instruction, MethodReference call)
    {
        if (call.DeclaringType.FullName != "SeaPower.AmmunitionParameters" || call.Name != "EffectiveMaxLaunchRange") return false;
        string at = type.FullName + "::" + method.Name;
        if (!call.HasThis || instruction.OpCode != OpCodes.Callvirt || !ParameterTypes(call, "SeaPower.ObjectBase") ||
            (at != "BetterTacMap.WeaponRange.WeaponRangeReader/<>c__DisplayClass2_0::<MaxRangeInMapDegrees>b__1" &&
             at != "BetterTacMap.Firing.WeaponMountReader::TryGetBestRangeUnity"))
            throw new InvalidOperationException("Uninspected Better Tac Map launch-range call in " + at);
        AppendDefaults(scope.Module, scope.Native, method, instruction, call, "launch-range");
        scope.Count("launch-range");
        return true;
    }

    private static bool BetterTacMap261123Rewrite(AdapterScope scope, TypeDefinition type, MethodDefinition method)
    {
        bool Removed(TypeReference t) => t != null && t.FullName == "World" && t.Scope is AssemblyNameReference s && s.Name == "Seapower-Scripts";
        var tokens = method.Body.Instructions.Where(i => i.OpCode == OpCodes.Ldtoken && Removed(i.Operand as TypeReference)).ToList();
        bool site = type.FullName == "BetterTacMap.Depth.EcsWorldAccess" && method.Name == "EnsureResolved";
        if (!site) {
            if (tokens.Count != 0) throw new InvalidOperationException("Uninspected Better Tac Map World token in " + type.FullName + "::" + method.Name);
            return false;
        }
        var il = method.Body.Instructions;
        bool Next(Instruction i, OpCode code, out Instruction next) { next = i?.Next; return next != null && next.OpCode == code; }
        bool Reads(Instruction token, string property, sbyte flags) =>
            Next(token, OpCodes.Call, out var handle) && handle.Operand is MethodReference m && m.Name == "GetTypeFromHandle" &&
            Next(handle, OpCodes.Ldstr, out var name) && Equals(name.Operand, property) &&
            Next(name, OpCodes.Ldc_I4_S, out var binding) && Equals(binding.Operand, flags) &&
            Next(binding, OpCodes.Call, out var get) && get.Operand is MethodReference g && g.Name == "GetProperty" &&
            g.DeclaringType.FullName == "System.Type" && ParameterTypes(g, "System.String", "System.Reflection.BindingFlags");
        // Static|Public (24) for the default world, Instance|Public (20) for its EntityManager.
        if (!method.IsStatic || method.Parameters.Count != 0 || method.Body.CodeSize != 389 || tokens.Count != 2 ||
            tokens[0].Offset != 0x15 || tokens[1].Offset != 0x2c ||
            !Reads(tokens[0], "DefaultGameObjectInjectionWorld", 24) || !Reads(tokens[1], "EntityManager", 20) ||
            !il.Any(i => i.OpCode == OpCodes.Ldstr && Equals(i.Operand, "Unity.Entities")))
            throw new InvalidOperationException("Inspected Better Tac Map ECS world lookup changed");
        var entities = scope.Module.AssemblyReferences.Single(r => r.Name == "Unity.Entities");
        var world = new TypeReference("Unity.Entities", "World", scope.Module, entities, false);
        foreach (var token in tokens) { token.Operand = world; scope.Count("ecs-world"); }
        return false;
    }

    private static void BetterTacMap261123Finish(AdapterScope scope)
    {
        var patch = scope.Module.GetType("BetterTacMap.Patches.ModDrawingSavePatch")
            ?? throw new InvalidOperationException("Inspected Better Tac Map drawing save patch changed");
        var attributes = patch.CustomAttributes.Where(a => a.AttributeType.FullName == "HarmonyLib.HarmonyPatch").ToList();
        var methods = patch.Methods.Where(m => !m.IsConstructor).ToList();
        MethodDefinition Patch(string name) => methods.SingleOrDefault(m => m.Name == name && m.IsStatic && m.IsPrivate && !m.HasCustomAttributes);
        var prefix = Patch("Prefix"); var postfix = Patch("Postfix"); var finalizer = Patch("Finalizer");
        var old = attributes.Count == 1 ? attributes[0] : null;
        if (old == null || patch.CustomAttributes.Count != 1 || methods.Count != 3 ||
            !ParameterTypes(old.Constructor, "System.Type", "System.String") || old.HasProperties || old.HasFields ||
            (old.ConstructorArguments[0].Value as TypeReference)?.FullName != "SeaPower.SaveLoadManager" ||
            !Equals(old.ConstructorArguments[1].Value, "WriteDrawingData") ||
            prefix == null || prefix.Parameters.Count != 0 || prefix.ReturnType.FullName != "System.Void" ||
            postfix == null || !ParameterTypes(postfix, "SeaPower.IniHandler") || postfix.Parameters[0].Name != "ini" || postfix.ReturnType.FullName != "System.Void" ||
            finalizer == null || !ParameterTypes(finalizer, "System.Exception") || finalizer.Parameters[0].Name != "__exception" ||
            finalizer.ReturnType.FullName != "System.Exception")
            throw new InvalidOperationException("Inspected Better Tac Map drawing save patch changed");
        var bare = new MethodReference(".ctor", scope.Module.TypeSystem.Void, old.AttributeType) { HasThis = true };
        var typeArgument = old.ConstructorArguments[0].Type; var nameArgument = old.ConstructorArguments[1].Type;
        CustomAttribute Target(TypeReference owner, string name)
        {
            var attribute = new CustomAttribute(old.Constructor);
            attribute.ConstructorArguments.Add(new CustomAttributeArgument(typeArgument, owner));
            attribute.ConstructorArguments.Add(new CustomAttributeArgument(nameArgument, name));
            return attribute;
        }
        var manager = (TypeReference)old.ConstructorArguments[0].Value;
        var content = scope.Module.ImportReference(scope.Native.GetType("SeaPower.SaveMapContent"));
        patch.CustomAttributes.Clear();
        patch.CustomAttributes.Add(new CustomAttribute(bare));
        prefix.CustomAttributes.Add(Target(manager, "SavePlayerDrawings")); scope.Count("drawing-save-split");
        postfix.CustomAttributes.Add(Target(content, "WriteSave")); scope.Count("drawing-save-split");
        // On the caller of both, not on WriteSave: the Prefix's method and
        // the Finalizer's must exit together, as on the old WriteDrawingData.
        finalizer.CustomAttributes.Add(Target(manager, "WriteMissionToFile")); scope.Count("drawing-save-split");
    }

    private static void BetterTacMap261123RequireNative(ModuleDefinition native)
    {
        CurrentNativeSnapshot(native);
        RequireLaunchRangeWithRunDepth(native);
        if (native.GetType("World") != null)
            throw new InvalidOperationException("Inspected 261123 removal of the global World type changed");
        // Unity.Entities.World, beside the game image, with the two properties EcsWorldAccess reads.
        if (!native.AssemblyReferences.Any(r => r.Name == "Unity.Entities"))
            throw new InvalidOperationException("Inspected 261123 Unity.Entities reference changed");
        string entitiesPath = Path.Combine(Path.GetDirectoryName(native.FileName), "Unity.Entities.dll");
        using (var entities = ModuleDefinition.ReadModule(entitiesPath, new ReaderParameters { ReadingMode = ReadingMode.Deferred })) {
            var world = entities.GetType("Unity.Entities.World");
            var injection = world?.Properties.SingleOrDefault(p => p.Name == "DefaultGameObjectInjectionWorld");
            var manager = world?.Properties.SingleOrDefault(p => p.Name == "EntityManager");
            if (entities.Assembly.Name.Name != "Unity.Entities" || world == null || !world.IsPublic || world.IsValueType ||
                injection?.GetMethod == null || !injection.GetMethod.IsStatic || !injection.GetMethod.IsPublic ||
                injection.PropertyType.FullName != "Unity.Entities.World" ||
                manager?.GetMethod == null || manager.GetMethod.IsStatic || !manager.GetMethod.IsPublic ||
                manager.PropertyType.FullName != "Unity.Entities.EntityManager")
                throw new InvalidOperationException("Inspected Unity.Entities.World properties changed");
        }
        // The 261123 drawing save path: WriteMissionToFile builds the player
        // list once with SavePlayerDrawings() and passes it to WriteSave; its
        // other branch passes null drawings and does not call SavePlayerDrawings,
        // so the patch's Postfix and Finalizer find nothing detached there.
        // WriteMissionToFile is the Finalizer's target, so it must be the one
        // method of that name (Harmony binds the target by name).
        var save = native.GetType("SeaPower.SaveLoadManager");
        var drawings = save.Methods.Where(m => m.Name == "SavePlayerDrawings").ToList();
        var load = save.Methods.Where(m => m.Name == "LoadDrawingData").ToList();
        var content = native.GetType("SeaPower.SaveMapContent");
        var writes = content?.Methods.Where(m => m.Name == "WriteSave").ToList();
        if (save.Methods.Any(m => m.Name == "WriteDrawingData") ||
            drawings.Count != 1 || !drawings[0].IsStatic || drawings[0].Parameters.Count != 0 ||
            drawings[0].ReturnType.FullName != "System.Collections.Generic.List`1<Seapower.MapContent.MapDrawing>" ||
            load.Count != 1 || !load[0].IsStatic || load[0].Parameters.Count != 0 ||
            content == null || !content.IsAbstract || !content.IsSealed || writes.Count != 1 || !writes[0].IsStatic || !writes[0].IsPublic ||
            !ParameterTypes(writes[0], "SeaPower.IniHandler", "SeaPower.MissionMapContentResult",
                "System.Collections.Generic.IEnumerable`1<Seapower.MapContent.MapDrawing>", "System.Nullable`1<System.DateTime>") ||
            writes[0].Parameters[0].Name != "ini")
            throw new InvalidOperationException("Inspected 261123 drawing save path changed");
        bool Calls(Instruction i, MethodDefinition target) => i.Operand is MethodReference r && r.Name == target.Name &&
            r.DeclaringType.FullName == target.DeclaringType.FullName;
        var callers = Types(native.Types).SelectMany(t => t.Methods).Where(m => m.HasBody && m.Body.Instructions.Any(i => Calls(i, drawings[0]))).ToList();
        var writers = Types(native.Types).SelectMany(t => t.Methods).Where(m => m.HasBody && m.Body.Instructions.Any(i => Calls(i, writes[0]))).ToList();
        if (callers.Count != 1 || callers[0].DeclaringType != save || callers[0].Name != "WriteMissionToFile" ||
            save.Methods.Count(m => m.Name == "WriteMissionToFile") != 1 ||
            writers.Count != 1 || writers[0] != callers[0])
            throw new InvalidOperationException("Inspected 261123 drawing save callers changed");
        var il = callers[0].Body.Instructions;
        var collect = il.Where(i => Calls(i, drawings[0])).ToList();
        var written = il.Where(i => Calls(i, writes[0])).Select(i => il.IndexOf(i)).ToList();
        int collected = collect.Count == 1 ? il.IndexOf(collect[0]) : -1;
        if (collect.Count != 1 || written.Count != 2 || collected < 0 || collected > written[0] ||
            il.Skip(collected + 1).Take(written[0] - collected - 1).Any(i => i.OpCode.FlowControl is FlowControl.Branch or FlowControl.Cond_Branch or FlowControl.Return or FlowControl.Throw) ||
            il[written[1] - 4].OpCode != OpCodes.Ldnull || il[written[1] - 5].OpCode != OpCodes.Ldnull ||
            il.Skip(written[0] + 1).Take(written[1] - written[0] - 1).Any(i => Calls(i, drawings[0])))
            throw new InvalidOperationException("Inspected 261123 drawing save order changed");
    }
}
