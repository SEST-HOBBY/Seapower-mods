using System;
using System.Collections.Generic;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    // R6 (7 Nov 2026): BetterTacMap (Workshop 3768036424, ACPlugin
    // toemel.bettertacmap 0.1) as captured on 3 Nov 2026. On the beta its
    // PatchAll stops at GizmoLayerManagerConstructorPatch: Build 261026 made
    // SeapowerUI.GizmoLayerManager a static class with no instance, no
    // Layers/LayersById/LayersByName fields and no public MapLayer(int,
    // string, bool). The map's layers moved to the lazy, process-lifetime
    // MapDisplayState.Tactical, which both scene maps display. Eight patch
    // classes stay applied, the other ten, the hotkeys and the settings never
    // start. The rules below retarget exactly the captured sites.
    internal const string BetterTacMapHash = "f1bdd2c2e5cec7579c3e47750950b1cb5521b5e4e630138aec8c483b6737ac08";
    private const string BetterTacMapPatches = "BetterTacMap.Patches.";
    private const string BetterTacMapManager = "SeapowerUI.GizmoLayerManager";
    private const string BetterTacMapDisplayState = "SeapowerUI.MapDisplayState";
    private const string BetterTacMapLayersById = "System.Collections.Generic.Dictionary`2<System.Int32,SeapowerUI.MapLayer> SeapowerUI.GizmoLayerManager::LayersById";
    private const string BetterTacMapLayersByName = "System.Collections.Generic.Dictionary`2<System.String,SeapowerUI.MapLayer> SeapowerUI.GizmoLayerManager::LayersByName";
    private const string BetterTacMapLayersList = "System.Collections.ObjectModel.ObservableCollection`1<SeapowerUI.MapLayer> SeapowerUI.GizmoLayerManager::Layers";
    private const string BetterTacMapStableLayerCtor = "System.Void SeapowerUI.MapLayer::.ctor(System.Int32,System.String,System.Boolean)";
    private const string BetterTacMapPatchAttribute = "HarmonyLib.HarmonyPatch";
    // The only instance constructor of beta SceneMapViewModel (rid 11874).
    private static readonly string[] BetterTacMapSceneCtor = { "System.String", "SeaPower.GeoPosition", "SeapowerUI.ViewModels.InteractionStateManager",
        "SeapowerUI.ViewModels.MapDrawingLayer", "MapControl.MapRegistry", "SeapowerUI.ViewModels.PlayAreaViewModel", "System.Func`1<System.Boolean>",
        "System.Func`1<System.Boolean>", "System.Func`1<Unity.Mathematics.double3>", "System.Func`1<System.Boolean>" };

    private static ImageAdapter BetterTacMapAdapter() => new ImageAdapter {
        Name = "BetterTacMap",
        Hashes = new[] { BetterTacMapHash },
        RequireNative = BetterTacMapRequireNative,
        RewriteMethod = BetterTacMapRewriteMethod,
        Finish = BetterTacMapFinish,
        ExpectedAudit = "attr-load-overload=1, attr-scene-ctor=1, attr-tactical-getter=2, layer-ctor=1, layers-by-id=3, layers-by-name=1, " +
            "layers-list=1, line3-refresh=1, locations=1, retype-display-state=4",
    };

    // Every native shape the rewrites and the BetterTacMap bridges rely on.
    private static void BetterTacMapRequireNative(ModuleDefinition native)
    {
        void Require(bool ok, string what) { if (!ok) throw new InvalidOperationException("Inspected beta " + what + " changed"); }
        TypeDefinition Type(string name) => native.GetType(name) ?? throw new InvalidOperationException("Inspected beta " + name + " changed");
        string[] Ops(MethodDefinition m) => m.Body.Instructions.Select(i => i.OpCode.Name + (i.Operand is MemberReference r ? " " + r.FullName :
            i.Operand is string s ? " \"" + s + "\"" : i.Operand is Instruction || i.Operand == null ? "" : " " + i.Operand)).ToArray();

        // The layer owner: static, lazy, process-lifetime, the only writer of _tactical.
        var state = Type(BetterTacMapDisplayState);
        Require(state.IsPublic && state.IsClass && !state.IsValueType && state.IsSealed && !state.IsAbstract, "MapDisplayState kind");
        var tactical = state.Properties.SingleOrDefault(p => p.Name == "Tactical")?.GetMethod;
        Require(tactical != null && tactical.IsStatic && tactical.IsPublic && tactical.Parameters.Count == 0 &&
            tactical.ReturnType.FullName == BetterTacMapDisplayState && Ops(tactical).SequenceEqual(new[] {
                "ldsfld SeapowerUI.MapDisplayState SeapowerUI.MapDisplayState::_tactical", "dup", "brtrue.s", "pop", "ldc.i4.1",
                "newobj System.Void SeapowerUI.MapDisplayState::.ctor(System.Boolean)", "dup",
                "stsfld SeapowerUI.MapDisplayState SeapowerUI.MapDisplayState::_tactical", "ret" }), "MapDisplayState.Tactical");
        foreach (var (name, type) in new[] { ("get_Layers", "System.Collections.ObjectModel.ObservableCollection`1<SeapowerUI.MapLayer>"),
            ("get_LayersById", "System.Collections.Generic.IReadOnlyDictionary`2<System.Int32,SeapowerUI.MapLayer>"),
            ("get_LayersByName", "System.Collections.Generic.IReadOnlyDictionary`2<System.String,SeapowerUI.MapLayer>") }) {
            var getter = state.Methods.SingleOrDefault(m => m.Name == name);
            Require(getter != null && getter.IsPublic && getter.HasThis && getter.Parameters.Count == 0 && getter.ReturnType.FullName == type &&
                Ops(getter).SequenceEqual(new[] { "ldarg.0", "ldfld " + type + " SeapowerUI.MapDisplayState::<" + name.Substring(4) + ">k__BackingField", "ret" }),
                "MapDisplayState." + name);
        }
        // The castclass rewrites rely on these backing fields holding the
        // concrete Dictionary instances that ctor(bool) creates; only it writes them.
        var writers = Types(native.Types).SelectMany(t => t.Methods).Where(m => m.HasBody).SelectMany(m => m.Body.Instructions
            .Where(i => i.OpCode == OpCodes.Stfld && i.Operand is FieldReference f && f.DeclaringType.FullName == BetterTacMapDisplayState &&
                (f.Name == "<LayersById>k__BackingField" || f.Name == "<LayersByName>k__BackingField")).Select(i => (m, i))).ToList();
        Require(writers.Count == 2 && writers.All(w => w.m.DeclaringType == state && w.m.IsConstructor && !w.m.IsStatic &&
            BetterTacMapTypes(w.m, "System.Boolean") && w.i.Previous.OpCode.Code is Code.Ldloc_1 or Code.Ldloc_2 &&
            w.m.Body.Variables[w.i.Previous.OpCode.Code == Code.Ldloc_1 ? 1 : 2].VariableType.FullName ==
                (((FieldReference)w.i.Operand).Name == "<LayersById>k__BackingField"
                    ? "System.Collections.Generic.Dictionary`2<System.Int32,SeapowerUI.MapLayer>"
                    : "System.Collections.Generic.Dictionary`2<System.String,SeapowerUI.MapLayer>")), "MapDisplayState layer dictionaries");

        // GizmoLayerManager is static, so the author's ctor/Instance targets are gone.
        var manager = Type(BetterTacMapManager);
        Require(manager.IsAbstract && manager.IsSealed && !manager.Methods.Any(m => m.IsConstructor && !m.IsStatic) &&
            !manager.Properties.Any(p => p.Name == "Instance") && !manager.Fields.Any(f => f.Name is "Layers" or "LayersById" or "LayersByName"),
            "GizmoLayerManager shape");
        var entry = manager.NestedTypes.SingleOrDefault(t => t.Name == "Entry");
        var entryCtor = entry?.Methods.SingleOrDefault(m => m.IsConstructor && !m.IsStatic);
        Require(entry != null && entry.IsValueType && entry.IsNestedAssembly && entryCtor != null &&
            BetterTacMapTypes(entryCtor, "System.Int32", "System.String", "System.Boolean") && Ops(entryCtor).SequenceEqual(new[] {
                "ldarg.0", "ldarg.1", "stfld System.Int32 SeapowerUI.GizmoLayerManager/Entry::Number",
                "ldarg.0", "ldarg.2", "stfld System.String SeapowerUI.GizmoLayerManager/Entry::Name",
                "ldarg.0", "ldarg.3", "stfld System.Boolean SeapowerUI.GizmoLayerManager/Entry::InMenu", "ret" }), "GizmoLayerManager.Entry");

        // MapLayer(owner, ref Entry, visible) is the stable (number, name,
        // inMenu) constructor plus the owner; visible is stored without an event.
        var layer = Type("SeapowerUI.MapLayer");
        var layerCtors = layer.Methods.Where(m => m.IsConstructor && !m.IsStatic).ToList();
        Require(layerCtors.Count == 1 && layerCtors[0].IsAssembly && BetterTacMapTypes(layerCtors[0], BetterTacMapDisplayState,
            "SeapowerUI.GizmoLayerManager/Entry&", "System.Boolean") && Ops(layerCtors[0]).SequenceEqual(new[] {
                "ldarg.0", "ldc.i4.1", "stfld System.Boolean SeapowerUI.MapLayer::_visible", "ldarg.0", "call System.Void System.Object::.ctor()",
                "ldarg.0", "ldarg.1", "stfld SeapowerUI.MapDisplayState SeapowerUI.MapLayer::_owner",
                "ldarg.0", "ldarg.2", "ldfld System.Int32 SeapowerUI.GizmoLayerManager/Entry::Number", "stfld System.Int32 SeapowerUI.MapLayer::<LayerNumber>k__BackingField",
                "ldarg.0", "ldarg.2", "ldfld System.String SeapowerUI.GizmoLayerManager/Entry::Name", "stfld System.String SeapowerUI.MapLayer::<Name>k__BackingField",
                "ldarg.0", "ldarg.2", "ldfld System.Boolean SeapowerUI.GizmoLayerManager/Entry::InMenu", "call System.Void SeapowerUI.MapLayer::set_VisibleInMenu(System.Boolean)",
                "ldarg.0", "ldarg.3", "stfld System.Boolean SeapowerUI.MapLayer::_visible",
                "ldarg.0", "call T SeaPower.Singleton`1<SeaPower.LanguageResourceHandler>::get_Instance()", "ldstr \"MapLayers\"",
                "ldarg.2", "ldfld System.String SeapowerUI.GizmoLayerManager/Entry::Name", "ldc.i4.1", "ldc.i4.1",
                "callvirt System.String SeaPower.LanguageResourceHandler::getText(System.String,System.String,System.Boolean,System.Boolean)",
                "stfld System.String SeapowerUI.MapLayer::<DisplayName>k__BackingField", "ret" }), "MapLayer constructor");
        var setVisible = layer.Methods.SingleOrDefault(m => m.Name == "set_Visible");
        Require(setVisible != null && setVisible.IsPublic && BetterTacMapTypes(setVisible, "System.Boolean") &&
            Ops(setVisible).Contains("callvirt System.Void SeapowerUI.MapDisplayState::OnLayerChanged()"), "MapLayer.set_Visible");

        // The retargeted Harmony attributes.
        var save = Type("SeaPower.SaveLoadManager");
        var loads = save.Methods.Where(m => m.Name == "LoadDrawingData").ToList();
        Require(loads.Count == 2 && loads.Count(m => m.IsStatic && m.Parameters.Count == 0 && m.ReturnType.FullName == "System.Void") == 1,
            "SaveLoadManager.LoadDrawingData overloads");
        var writes = save.Methods.Where(m => m.Name == "WriteDrawingData").ToList();
        Require(writes.Count == 1 && writes[0].IsStatic && BetterTacMapTypes(writes[0], "SeaPower.IniHandler", "SeapowerUI.ViewModels.MapDrawingLayer") &&
            writes[0].Parameters[0].Name == "ini", "SaveLoadManager.WriteDrawingData");
        var scene = Type("SeapowerUI.ViewModels.SceneMapViewModel");
        var sceneCtors = scene.Methods.Where(m => m.IsConstructor && !m.IsStatic).ToList();
        Require(sceneCtors.Count == 1 && sceneCtors[0].IsPublic && BetterTacMapTypes(sceneCtors[0], BetterTacMapSceneCtor), "SceneMapViewModel constructor");

        // The line-3 refresh bridge: beta rebuilds line 3 only when its own
        // inputs change, and skips the setter when the rebuilt text equals
        // _contactInfoLine3. Clearing _line3Initialized and _contactInfoLine3
        // forces the next Update through both gates.
        var unit = Type("SeapowerUI.MapUnitViewModel");
        FieldDefinition Field(TypeDefinition owner, string name, string type)
        {
            var field = owner.Fields.SingleOrDefault(f => f.Name == name);
            Require(field != null && !field.IsStatic && field.FieldType.FullName == type, owner.Name + "." + name);
            return field;
        }
        Field(unit, "Label", "SeapowerUI.MapLabelCandidate"); Field(unit, "_line3Initialized", "System.Boolean");
        Field(unit, "_contactInfoLine3", "System.String");
        var candidate = Type("SeapowerUI.MapLabelCandidate");
        Field(candidate, "Realized", "System.Boolean"); Field(candidate, "Prefix", "System.Int32"); Field(candidate, "HeadLine", "SeapowerUI.MapLabelLine");
        var updates = unit.Methods.Where(m => m.Name == "Update").ToList();
        Require(updates.Count == 1 && updates[0].HasThis && updates[0].Parameters.Count == 0 && updates[0].Body.Instructions.Count(i =>
            i.OpCode == OpCodes.Call && (i.Operand as MethodReference)?.FullName ==
                "System.Void SeapowerUI.MapUnitViewModel::UpdateContactInfoLine3(UniRx.ReactiveProperty`1<SeapowerUI.ISelectableObject>)") == 1,
            "MapUnitViewModel.Update");
        var line3 = unit.Methods.Single(m => m.Name == "UpdateContactInfoLine3");
        var ops = Ops(line3);
        // IL_0000-0030: shown = Label != null && Label.Realized && Label.Prefix > (HeadLine != null ? 1 : 0) + 2.
        Require(ops.Take(25).SequenceEqual(new[] { "ldarg.0", "ldfld SeapowerUI.MapLabelCandidate SeapowerUI.MapUnitViewModel::Label", "stloc.0",
            "ldloc.0", "brfalse.s", "ldloc.0", "ldfld SeapowerUI.MapLabelLine SeapowerUI.MapLabelCandidate::HeadLine", "brtrue.s", "ldc.i4.0", "br.s",
            "ldc.i4.1", "ldc.i4.2", "add", "stloc.1", "ldloc.0", "brfalse.s", "ldloc.0", "ldfld System.Boolean SeapowerUI.MapLabelCandidate::Realized",
            "brfalse.s", "ldloc.0", "ldfld System.Int32 SeapowerUI.MapLabelCandidate::Prefix", "ldloc.1", "cgt", "br.s", "ldc.i4.0" }) &&
            ops.Count(o => o == "ldfld System.Boolean SeapowerUI.MapUnitViewModel::_line3Initialized") == 1 &&
            ops.Count(o => o == "stfld System.Boolean SeapowerUI.MapUnitViewModel::_line3Initialized") == 1 &&
            ops.Count(o => o == "ldfld System.String SeapowerUI.MapUnitViewModel::_contactInfoLine3") == 1 &&
            ops.Count(o => o == "call System.Boolean SeapowerUI.MapUnitViewModel::BuilderEquals(System.Text.StringBuilder,System.String)") == 1 &&
            ops.Count(o => o == "call System.Void SeapowerUI.MapUnitViewModel::set_ContactInfoLine3(System.String)") == 1, "MapUnitViewModel.UpdateContactInfoLine3");
        var builderEquals = unit.Methods.Single(m => m.Name == "BuilderEquals");
        Require(Ops(builderEquals).Take(2).SequenceEqual(new[] { "ldarg.1", "brfalse.s" }) &&
            builderEquals.Body.Instructions[1].Operand is Instruction nullTarget && nullTarget.OpCode == OpCodes.Ldc_I4_0 &&
            nullTarget.Next.OpCode == OpCodes.Ret, "MapUnitViewModel.BuilderEquals null text");
        var setter = unit.Methods.SingleOrDefault(m => m.Name == "set_ContactInfoLine3");
        Require(setter != null && setter.IsPublic && setter.Parameters.Count == 1 && setter.Parameters[0].Name == "value" &&
            Ops(setter).SequenceEqual(new[] { "ldarg.0", "ldfld System.String SeapowerUI.MapUnitViewModel::_contactInfoLine3", "ldarg.0", "ldarg.1",
                "stfld System.String SeapowerUI.MapUnitViewModel::_contactInfoLine3", "ldarg.1",
                "call System.Boolean System.String::op_Inequality(System.String,System.String)", "brfalse.s", "ldarg.0", "ldstr \"ContactInfoLine3\"",
                "callvirt System.Void SeapowerUI.MapUnitViewModel::OnPropertyChanged(System.String)", "ret" }), "MapUnitViewModel.set_ContactInfoLine3");
        var time = Type("SeaPower.GameTime").Methods.SingleOrDefault(m => m.Name == "get_unscaledTime");
        Require(time != null && time.IsStatic && time.IsPublic && time.ReturnType.FullName == "System.Double" &&
            ops.Contains("call System.Double SeaPower.GameTime::get_unscaledTime()"), "GameTime.unscaledTime");
    }

    private static bool BetterTacMapTypes(MethodReference method, params string[] names)
        => method.Parameters.Select(p => p.ParameterType.FullName).SequenceEqual(names);

    private static bool BetterTacMapIs(Instruction instruction, OpCode opcode, string operand = null)
        => instruction != null && instruction.OpCode == opcode && (operand == null
            ? instruction.Operand == null || instruction.Operand is Instruction
            : (instruction.Operand as MemberReference)?.FullName == operand);

    // The postfixes call the plugin's own EnsureRegistered, whose parameter
    // type this adapter may already have changed when they are visited.
    private static bool BetterTacMapIsEnsure(object operand)
        => operand is MethodDefinition ensure && ensure.DeclaringType.FullName == BetterTacMapPatches + "MapLayerRegistrationPatch" &&
            ensure.Name == "EnsureRegistered" && ensure.IsStatic && ensure.ReturnType.FullName == "System.Void" && ensure.Parameters.Count == 1 &&
            (ensure.Parameters[0].ParameterType.FullName == BetterTacMapManager || ensure.Parameters[0].ParameterType.FullName == BetterTacMapDisplayState);

    private static void BetterTacMapRequire(bool ok, MethodDefinition method, string what)
    {
        if (!ok) throw new InvalidOperationException("Inspected BetterTacMap " + method.DeclaringType.Name + "." + method.Name + " " + what + " changed");
    }

    // A GizmoLayerManager parameter becomes the MapDisplayState that beta's
    // Tactical getter returns; HarmonyX binds __result to it.
    private static void BetterTacMapRetype(AdapterScope scope, MethodDefinition method, string oldName, string newName)
    {
        var parameter = method.Parameters.FirstOrDefault();
        BetterTacMapRequire(method.IsStatic && parameter != null && parameter.Name == oldName && parameter.ParameterType.FullName == BetterTacMapManager,
            method, "parameter " + oldName);
        parameter.ParameterType = scope.Module.ImportReference(scope.Native.GetType(BetterTacMapDisplayState));
        parameter.Name = newName;
        scope.Count("retype-display-state");
    }

    private static bool BetterTacMapRewriteMethod(AdapterScope scope, TypeDefinition type, MethodDefinition method)
    {
        string name = type.FullName.StartsWith(BetterTacMapPatches, StringComparison.Ordinal) ? type.FullName.Substring(BetterTacMapPatches.Length) : null;
        if ((name == "GizmoLayerManagerConstructorPatch" || name == "GizmoLayerManagerInstanceGetterPatch") && method.Name == "Postfix") {
            // [HarmonyPatch(GizmoLayerManager, Constructor)] Postfix(__instance) and
            // [HarmonyPatch(GizmoLayerManager, "Instance", Getter)] Postfix(__result)
            // both become MapDisplayState.Tactical getter postfixes taking __result.
            var il = method.Body.Instructions;
            BetterTacMapRequire(method.ReturnType.FullName == "System.Void" && method.Parameters.Count == 1 && il.Count == 5 &&
                BetterTacMapIs(il[0], OpCodes.Nop) && BetterTacMapIs(il[1], OpCodes.Ldarg_0) && il[2].OpCode == OpCodes.Call && BetterTacMapIsEnsure(il[2].Operand) &&
                BetterTacMapIs(il[3], OpCodes.Nop) && BetterTacMapIs(il[4], OpCodes.Ret), method, "body");
            BetterTacMapRetype(scope, method, name == "GizmoLayerManagerConstructorPatch" ? "__instance" : "__result", "__result");
        }
        else if (name == "MapLayerRegistrationPatch" && method.Name == "EnsureRegistered") {
            BetterTacMapRequire(method.ReturnType.FullName == "System.Void" && method.Parameters.Count == 1 && method.Body.Instructions.Count(i =>
                i.OpCode == OpCodes.Call && (i.Operand as MethodReference)?.Name == "Register" && i.Operand is MethodDefinition) == 8, method, "registrations");
            BetterTacMapRetype(scope, method, "instance", "instance");
        }
        else if (name == "MapLayerRegistrationPatch" && method.Name == "Register") BetterTacMapRegister(scope, method);
        else if (name == "DestroyedUnitCleanupPatch" && method.Name == "Postfix") {
            // Stable called set_ContactInfoLine3 (the author's label Prefix) on
            // every MapUnitViewModel.Update; beta rebuilds line 3 only when its
            // own inputs change. This Postfix already runs after every Update.
            var il = method.Body.Instructions; var first = il[0];
            BetterTacMapRequire(method.IsStatic && method.ReturnType.FullName == "System.Void" && BetterTacMapTypes(method, "SeapowerUI.MapUnitViewModel") &&
                method.Parameters[0].Name == "__instance" && !method.Body.HasExceptionHandlers && BetterTacMapIs(first, OpCodes.Nop) &&
                BetterTacMapIs(il[1], OpCodes.Ldsfld, "System.Boolean BetterTacMap.BetterTacMapMod::IsEnabled") &&
                !il.Any(i => i.Operand == first || (i.Operand as Instruction[])?.Contains(first) == true), method, "entry");
            var gate = method.Body.GetILProcessor();
            gate.InsertBefore(first, Instruction.Create(OpCodes.Ldarg_0));
            gate.InsertBefore(first, Instruction.Create(OpCodes.Call, scope.Bridge(nameof(BetaCompatibilityCalls.BetterTacMapRefreshLine3))));
            scope.Count("line3-refresh");
        }
        // No other method may still use the removed stable members.
        else if (method.Body.Instructions.Any(i => (i.Operand as MemberReference)?.DeclaringType?.FullName == BetterTacMapManager ||
                (i.Operand as MemberReference)?.FullName == BetterTacMapStableLayerCtor) ||
            method.Parameters.Any(p => p.ParameterType.FullName == BetterTacMapManager))
            throw new InvalidOperationException("Uninspected BetterTacMap GizmoLayerManager use in " + method.FullName);
        return false;
    }

    // MapLayerRegistrationPatch.Register(GizmoLayerManager instance, int
    // layerNumber, string name, string displayName, ConfigEntry<bool>, bool):
    // the three stable fields become Tactical's getters (castclass to the
    // concrete Dictionary the beta constructor stores), and the stable public
    // MapLayer constructor becomes a bridge to the internal one.
    private static void BetterTacMapRegister(AdapterScope scope, MethodDefinition method)
    {
        BetterTacMapRequire(method.ReturnType.FullName == "SeapowerUI.MapLayer" && BetterTacMapTypes(method, BetterTacMapManager, "System.Int32",
            "System.String", "System.String", "BepInEx.Configuration.ConfigEntry`1<System.Boolean>", "System.Boolean"), method, "signature");
        var state = scope.Native.GetType(BetterTacMapDisplayState);
        MethodReference Getter(string name) => scope.Module.ImportReference(state.Methods.Single(m => m.Name == name && m.HasThis && m.Parameters.Count == 0));
        // Captured offset -> (operand, the instruction after it); each is loaded by ldarg.0.
        var sites = new Dictionary<int, (string Operand, OpCode Next)> {
            [0x10] = (BetterTacMapLayersById, OpCodes.Ldarg_1), [0x58] = (BetterTacMapLayersById, OpCodes.Ldarg_1),
            [0xd6] = (BetterTacMapLayersList, OpCodes.Ldloc_0), [0xe8] = (BetterTacMapLayersByName, OpCodes.Ldarg_2),
            [0xfb] = (BetterTacMapLayersById, OpCodes.Ldarg_1), [0x90] = (BetterTacMapStableLayerCtor, OpCodes.Stfld) };
        var seen = new HashSet<int>();
        foreach (var instruction in method.Body.Instructions.ToArray()) {
            var member = instruction.Operand as MemberReference;
            if (member?.DeclaringType?.FullName != BetterTacMapManager && member?.FullName != BetterTacMapStableLayerCtor) continue;
            BetterTacMapRequire(sites.TryGetValue(instruction.Offset, out var site) && seen.Add(instruction.Offset) && member.FullName == site.Operand &&
                instruction.Next?.OpCode == site.Next, method, "operand at IL_" + instruction.Offset.ToString("x4"));
            if (site.Operand == BetterTacMapStableLayerCtor) {
                // ldloc.0; ldarg.1 (layerNumber); ldarg.2 (name); ldc.i4.1 (visibleInMenu); newobj
                var p = instruction.Previous;
                BetterTacMapRequire(instruction.OpCode == OpCodes.Newobj && BetterTacMapIs(p, OpCodes.Ldc_I4_1) && BetterTacMapIs(p.Previous, OpCodes.Ldarg_2) &&
                    BetterTacMapIs(p.Previous.Previous, OpCodes.Ldarg_1) && BetterTacMapIs(p.Previous.Previous.Previous, OpCodes.Ldloc_0) &&
                    (instruction.Next.Operand as FieldReference)?.FullName == "SeapowerUI.MapLayer BetterTacMap.Patches.MapLayerRegistrationPatch/<>c__DisplayClass26_0::layer",
                    method, "layer constructor arguments");
                scope.Replace(method, instruction, Instruction.Create(OpCodes.Ldarg_0),
                    Instruction.Create(OpCodes.Call, scope.Bridge(nameof(BetaCompatibilityCalls.BetterTacMapNewLayer))));
                scope.Count("layer-ctor");
                continue;
            }
            BetterTacMapRequire(instruction.OpCode == OpCodes.Ldfld && BetterTacMapIs(instruction.Previous, OpCodes.Ldarg_0), method, "field load");
            var fieldType = ((FieldReference)member).FieldType;
            if (site.Operand == BetterTacMapLayersList) {
                scope.Replace(method, instruction, Instruction.Create(OpCodes.Callvirt, Getter("get_Layers")));
                scope.Count("layers-list");
            }
            else {
                bool byId = site.Operand == BetterTacMapLayersById;
                scope.Replace(method, instruction, Instruction.Create(OpCodes.Callvirt, Getter(byId ? "get_LayersById" : "get_LayersByName")),
                    Instruction.Create(OpCodes.Castclass, fieldType));
                scope.Count(byId ? "layers-by-id" : "layers-by-name");
            }
        }
        BetterTacMapRequire(seen.Count == sites.Count, method, "operand set");
        BetterTacMapRetype(scope, method, "instance", "instance");
    }

    // Attribute targets are rewritten after the instruction loop.
    private static void BetterTacMapFinish(AdapterScope scope)
    {
        var module = scope.Module;
        TypeDefinition Plugin(string name) => Types(module.Types).SingleOrDefault(t => t.FullName == BetterTacMapPatches + name)
            ?? throw new InvalidOperationException("Inspected BetterTacMap " + name + " changed");
        CustomAttribute Patch(ICustomAttributeProvider owner, string what, params string[] parameters)
        {
            var attributes = owner.CustomAttributes.Where(a => a.AttributeType.FullName == BetterTacMapPatchAttribute).ToList();
            if (attributes.Count != 1 || !BetterTacMapTypes(attributes[0].Constructor, parameters))
                throw new InvalidOperationException("Inspected BetterTacMap " + what + " HarmonyPatch changed");
            return attributes[0];
        }
        bool TypeArgument(CustomAttributeArgument argument, string name) => argument.Type.FullName == "System.Type" &&
            argument.Value is TypeReference type && type.FullName == name && type.Scope is AssemblyNameReference game && game.Name == "Seapower-Scripts";
        var sceneCtor = Plugin("WaypointEtaModePatch").Methods.SingleOrDefault(m => m.Name == "ConstructorPostfix")
            ?? throw new InvalidOperationException("Inspected BetterTacMap ConstructorPostfix changed");

        var ctorPatch = Patch(Plugin("GizmoLayerManagerConstructorPatch"), "constructor patch", "System.Type", "HarmonyLib.MethodType");
        var getterPatch = Patch(Plugin("GizmoLayerManagerInstanceGetterPatch"), "getter patch", "System.Type", "System.String", "HarmonyLib.MethodType");
        var loadPatch = Patch(Plugin("ModDrawingLoadPatch"), "load patch", "System.Type", "System.String");
        var etaPatch = Patch(sceneCtor, "ETA constructor patch", "HarmonyLib.MethodType", "System.Type[]");
        if (!TypeArgument(ctorPatch.ConstructorArguments[0], BetterTacMapManager) || !Equals(ctorPatch.ConstructorArguments[1].Value, 3) ||
            !TypeArgument(getterPatch.ConstructorArguments[0], BetterTacMapManager) || !Equals(getterPatch.ConstructorArguments[1].Value, "Instance") ||
            !Equals(getterPatch.ConstructorArguments[2].Value, 1) ||
            !TypeArgument(loadPatch.ConstructorArguments[0], "SeaPower.SaveLoadManager") || !Equals(loadPatch.ConstructorArguments[1].Value, "LoadDrawingData") ||
            !Equals(etaPatch.ConstructorArguments[0].Value, 3) || etaPatch.ConstructorArguments[1].Value is not CustomAttributeArgument[] stableScene ||
            stableScene.Length != 2 || !TypeArgument(stableScene[0], "SeaPower.GeoPosition") ||
            !TypeArgument(stableScene[1], "SeapowerUI.ViewModels.InteractionStateManager"))
            throw new InvalidOperationException("Inspected BetterTacMap HarmonyPatch arguments changed");

        TypeReference systemType = ctorPatch.Constructor.Parameters[0].ParameterType, methodType = ctorPatch.Constructor.Parameters[1].ParameterType;
        MethodReference Constructor(params TypeReference[] parameters)
        {
            var ctor = new MethodReference(".ctor", module.TypeSystem.Void, ctorPatch.AttributeType) { HasThis = true };
            foreach (var parameter in parameters) ctor.Parameters.Add(new ParameterDefinition(parameter));
            return ctor;
        }
        void Replace(ICustomAttributeProvider owner, CustomAttribute old, MethodReference ctor, params CustomAttributeArgument[] arguments)
        {
            var fresh = new CustomAttribute(ctor);
            foreach (var argument in arguments) fresh.ConstructorArguments.Add(argument);
            owner.CustomAttributes[owner.CustomAttributes.IndexOf(old)] = fresh;
        }
        // [HarmonyPatch(typeof(MapDisplayState), "Tactical", MethodType.Getter)] for both former GizmoLayerManager targets.
        var tactical = Constructor(systemType, module.TypeSystem.String, methodType);
        CustomAttributeArgument[] Tactical() => new[] {
            new CustomAttributeArgument(systemType, module.ImportReference(scope.Native.GetType(BetterTacMapDisplayState))),
            new CustomAttributeArgument(module.TypeSystem.String, "Tactical"), new CustomAttributeArgument(methodType, 1) };
        Replace(Plugin("GizmoLayerManagerConstructorPatch"), ctorPatch, tactical, Tactical()); scope.Count("attr-tactical-getter");
        Replace(Plugin("GizmoLayerManagerInstanceGetterPatch"), getterPatch, tactical, Tactical()); scope.Count("attr-tactical-getter");
        // [HarmonyPatch(typeof(SaveLoadManager), "LoadDrawingData", new Type[0])]:
        // the parameterless overload, stable's role (Map-null return, MissionIni, Map.DrawingLayer).
        var types = new ArrayType(systemType);
        Replace(Plugin("ModDrawingLoadPatch"), loadPatch, Constructor(systemType, module.TypeSystem.String, types),
            loadPatch.ConstructorArguments[0], loadPatch.ConstructorArguments[1], new CustomAttributeArgument(types, Array.Empty<CustomAttributeArgument>()));
        scope.Count("attr-load-overload");
        // [HarmonyPatch(MethodType.Constructor, <the beta's ten parameter types>)].
        var beta = scope.Native.GetType("SeapowerUI.ViewModels.SceneMapViewModel").Methods.Single(m => m.IsConstructor && !m.IsStatic);
        Replace(sceneCtor, etaPatch, etaPatch.Constructor, etaPatch.ConstructorArguments[0], new CustomAttributeArgument(types,
            beta.Parameters.Select(p => new CustomAttributeArgument(systemType, module.ImportReference(p.ParameterType))).ToArray()));
        scope.Count("attr-scene-ctor");

        // Nothing may still bind a removed stable member or target.
        foreach (var type in Types(module.Types)) {
            foreach (var attribute in type.CustomAttributes.Concat(type.Methods.SelectMany(m => m.CustomAttributes)))
                if (attribute.ConstructorArguments.Any(a => (a.Value as TypeReference)?.FullName == BetterTacMapManager))
                    throw new InvalidOperationException("BetterTacMap still targets GizmoLayerManager: " + type.FullName);
            foreach (var method in type.Methods) {
                if (method.Parameters.Any(p => p.ParameterType.FullName == BetterTacMapManager) || method.HasBody && method.Body.Instructions.Any(i =>
                    (i.Operand as MemberReference)?.DeclaringType?.FullName == BetterTacMapManager || (i.Operand as MemberReference)?.FullName == BetterTacMapStableLayerCtor))
                    throw new InvalidOperationException("BetterTacMap still uses GizmoLayerManager: " + method.FullName);
            }
        }
    }
}
