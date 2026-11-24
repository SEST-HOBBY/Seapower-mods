// (build-roslyn.ps1 compiles every *.cs in source/, sorted; the csproj is not the build.)
// Dynamic Campaign Mod 1.0.2 (18a2416e) on 0.9.3-261123 (ea653e49). The build
// that moved the campaign map onto the missions' map removed or re-signed six
// members the mod names: CampaignMain.GetVisualPostureAndColour,
// GroupOfUnits.UnitColorBrush, MapDrawingLayer(), MapControl.MapTileLayer,
// Seapower.SceneEditor.Scheduler and MapTerrainBackground(MapPalette, MapTerrainEdits).
// The inline campaign rules in AssemblyAdapters.cs (attack-property,
// fuel-refresh, HasNightCapableSensors, locations) still run because
// campaign == true; this adapter adds the map rules and owns the audit.
using System;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    internal const string Campaign261123Audit = "HasNightCapableSensors=1, attack-property=14, drawing-layer=1, flat-tiles=2, fuel-refresh=1, globe-fail-guard=1, group-brush=2, locations=4, scheduler-timing=1, side-colour=8, terrain-background=1";

    private static ImageAdapter Campaign261123Adapter() => new ImageAdapter {
        Name = "Campaign261123", Hashes = new[] { CampaignHash },
        RequireNative = Campaign261123RequireNative,
        RewriteMethod = Campaign261123Rewrite,
        RewriteCall = Campaign261123Call,
        ExpectedAudit = Campaign261123Audit,
    };

    private static bool Campaign261123Rewrite(AdapterScope scope, TypeDefinition type, MethodDefinition method)
    {
        // MapPerf times Seapower.SceneEditor.Scheduler.Update; 261123 has no such
        // type. A null target sends MapPerf.Install down the author's own
        // MissingMethodException/catch ("Map perf: game scheduler not timed").
        if (type.FullName == "DynamicCampaignMod.UI.Map.MapPerf/<>c" && method.Name == "<Install>b__79_5") {
            var il = method.Body.Instructions;
            if (il.Count != 7 || method.Body.CodeSize != 23 || method.Body.HasExceptionHandlers ||
                method.ReturnType.FullName != "System.Reflection.MethodBase" ||
                il[0].OpCode != OpCodes.Ldtoken || (il[0].Operand as TypeReference)?.FullName != "Seapower.SceneEditor.Scheduler" ||
                (il[1].Operand as MethodReference)?.Name != "GetTypeFromHandle" ||
                il[2].OpCode != OpCodes.Ldstr || !Equals(il[2].Operand, "Update") ||
                il[3].OpCode != OpCodes.Ldnull || il[4].OpCode != OpCodes.Ldnull ||
                !(il[5].Operand is MethodReference lookup && lookup.Name == "Method" && lookup.DeclaringType.FullName == "HarmonyLib.AccessTools") ||
                il[6].OpCode != OpCodes.Ret)
                throw new InvalidOperationException("Inspected DCM scheduler timing target changed");
            il.Clear();
            var p = method.Body.GetILProcessor();
            p.Append(p.Create(OpCodes.Ldnull)); p.Append(p.Create(OpCodes.Ret));
            scope.Count("scheduler-timing");
            return true;
        }
        // The flat tile layer DCM takes off the campaign background is gone:
        // 261123's campaign map is already a MapInstance globe. The search now
        // honestly finds nothing; the local is retyped to Noesis.BaseComponent,
        // which every use of it (op_Inequality, Collection<object>.Remove) accepts.
        if (type.FullName == "DynamicCampaignMod.UI.Map.GlobeMap" && (method.Name == "Make" || method.Name == "Fail")) {
            var tiles = method.Body.Variables.Where(v => v.VariableType.FullName == "MapControl.MapTileLayer").ToList();
            var find = method.Body.Instructions.Where(i => i.OpCode == OpCodes.Call && i.Operand is GenericInstanceMethod g && g.Name == "OfType" &&
                g.DeclaringType.FullName == "System.Linq.Enumerable" && g.GenericArguments.Single().FullName == "MapControl.MapTileLayer").ToList();
            var first = find.Count == 1 ? find[0].Next : null;
            var store = first?.Next;
            bool stores = store != null && tiles.Count == 1 &&
                (store.OpCode.Code == Code.Stloc_1 ? tiles[0].Index == 1 :
                 (store.OpCode.Code is Code.Stloc_S or Code.Stloc) && store.Operand == tiles[0]);
            if (tiles.Count != 1 || find.Count != 1 || !stores ||
                !(first.OpCode == OpCodes.Call && first.Operand is GenericInstanceMethod f && f.Name == "FirstOrDefault" &&
                  f.DeclaringType.FullName == "System.Linq.Enumerable" && f.GenericArguments.Single().FullName == "MapControl.MapTileLayer"))
                throw new InvalidOperationException("Inspected DCM flat-tile lookup changed in GlobeMap." + method.Name);
            var bridge = scope.Bridge(nameof(BetaCompatibilityCalls.CampaignFlatTileLayer));
            tiles[0].VariableType = bridge.ReturnType;   // Noesis.BaseComponent
            find[0].Operand = bridge;                    // stays OpCodes.Call
            first.OpCode = OpCodes.Nop; first.Operand = null;
            scope.Count("flat-tiles");
        }
        return false;
    }

    private static bool Campaign261123Call(AdapterScope scope, TypeDefinition type, MethodDefinition method, Instruction instruction, MethodReference call)
    {
        string owner = call.DeclaringType.FullName, at = type.FullName + "::" + method.Name;
        if (owner == "SeaPower.CampaignMain" && call.Name == "GetVisualPostureAndColour" && !call.HasThis &&
            instruction.OpCode == OpCodes.Call && ParameterTypes(call, "SeapowerUI.ViewModels.MissionEditorViewModel/Side")) {
            instruction.Operand = scope.Bridge(nameof(BetaCompatibilityCalls.CampaignSideLook));
            scope.Count("side-colour"); return true;
        }
        if (owner == "SeapowerUI.ViewModels.GroupOfUnits" && (call.Name == "set_UnitColorBrush" || call.Name == "get_UnitColorBrush")) {
            if (call.Name != "set_UnitColorBrush" || !call.HasThis || !ParameterTypes(call, "Noesis.Brush") ||
                (at != "DynamicCampaignMod.Game.Mirror.MapMirror::Fade" && at != "DynamicCampaignMod.Game.Mirror.MapMirror::Create"))
                throw new InvalidOperationException("Uninspected DCM group brush use in " + at);
            instruction.OpCode = OpCodes.Call; instruction.Operand = scope.Bridge(nameof(BetaCompatibilityCalls.CampaignGroupBrush));
            scope.Count("group-brush"); return true;
        }
        if (owner == "SeapowerUI.ViewModels.MapDrawingLayer" && call.Name == ".ctor" && call.Parameters.Count == 0) {
            if (instruction.OpCode != OpCodes.Newobj || at != "DynamicCampaignMod.UI.Map.DrawingTools::Restore")
                throw new InvalidOperationException("Uninspected DCM drawing layer in " + at);
            instruction.OpCode = OpCodes.Call; instruction.Operand = scope.Bridge(nameof(BetaCompatibilityCalls.NewCampaignDrawingLayer));
            scope.Count("drawing-layer"); return true;
        }
        if (instruction.OpCode == OpCodes.Newobj && owner == "MapControl.MapTerrainBackground" && call.Name == ".ctor" &&
            ParameterTypes(call, "SeaPower.LiveMap.MapPalette", "SeaPower.LiveMap.MapTerrainEdits")) {
            // 261123 adds [opt] MapProcessedHeight = null; the game's own campaign globe passes null.
            AppendDefaults(scope.Module, scope.Native, method, instruction, call, "terrain-background");
            scope.Count("terrain-background"); return true;
        }
        if (at == "DynamicCampaignMod.UI.Map.GlobeMap::Fail" && owner == "SeapowerUI.MapViewModel" && call.Name == "get_Instance" &&
            call.HasThis && call.Parameters.Count == 0) {
            // 261123's MapInstance.Dispose already clears DisplayMap.Instance when it is
            // current, so this second dispose can only reach the game's own campaign globe.
            instruction.OpCode = OpCodes.Call; instruction.Operand = scope.Bridge(nameof(BetaCompatibilityCalls.CampaignGlobeToDispose));
            scope.Count("globe-fail-guard"); return true;
        }
        return false;
    }

    private static void Campaign261123RequireNative(ModuleDefinition native)
    {
        CurrentNativeSnapshot(native);
        const string Side = "SeapowerUI.ViewModels.MissionEditorViewModel/Side";
        var main = native.GetType("SeaPower.CampaignMain");
        var posture = main.Methods.Single(m => m.Name == "GetVisualPosture" && m.IsStatic && m.IsPublic && ParameterTypes(m, Side));
        var postures = posture.Body.Instructions.Where(i => i.OpCode.Code is Code.Ldc_I4_0 or Code.Ldc_I4_1 or Code.Ldc_I4_2)
            .Select(i => i.OpCode.Code).ToArray();
        var brush = native.GetType("SeaPower.UI_Parameters").Methods.Single(m => m.Name == "MapBrush" && m.IsStatic && m.IsPublic && ParameterTypes(m, "System.String", "System.Boolean"));
        var layerCtors = native.GetType("SeapowerUI.ViewModels.MapDrawingLayer").Methods.Where(m => m.IsConstructor && !m.IsStatic).ToList();
        var group = native.GetType("SeapowerUI.ViewModels.GroupOfUnits");
        var terrain = native.GetType("MapControl.MapTerrainBackground").Methods.Where(m => m.IsConstructor && !m.IsStatic).ToList();
        var dispose = native.GetType("MapControl.MapInstance").Methods.Single(m => m.Name == "Retire");
        if (main.Methods.Any(m => m.Name == "GetVisualPostureAndColour") || posture.ReturnType.FullName != "SeapowerUI.MapVisualPosture" ||
            posture.Body.CodeSize != 15 || !postures.SequenceEqual(new[] { Code.Ldc_I4_1, Code.Ldc_I4_1, Code.Ldc_I4_0, Code.Ldc_I4_2 }) ||
            brush.ReturnType.FullName != "Noesis.SolidColorBrush" || !brush.Parameters[1].IsOptional ||
            layerCtors.Count != 1 || !ParameterTypes(layerCtors[0], "SeapowerUI.ViewModels.InteractionStateManager", "SeaPower.GridFrame") ||
            !native.GetType("SeaPower.GridFrame").Methods.Any(m => m.Name == "get_Equirectangular" && m.IsStatic && m.IsPublic && m.Parameters.Count == 0) ||
            !native.GetType("SeapowerUI.ViewModels.CampaignViewModel").Methods.Any(m => m.Name == "get_StateManager" && m.IsPublic) ||
            native.GetType("MapControl.MapTileLayer") != null || native.GetType("Seapower.SceneEditor.Scheduler") != null ||
            group.Methods.Any(m => m.Name == "set_UnitColorBrush" || m.Name == "get_UnitColorBrush") ||
            !group.Methods.Any(m => m.Name == "set_VisualPosture" && m.IsPublic) ||
            !group.Interfaces.Any(i => i.InterfaceType.FullName == "SeapowerUI.IMapColorOverride") ||
            terrain.Count != 1 || !ParameterTypes(terrain[0], "SeaPower.LiveMap.MapPalette", "SeaPower.LiveMap.MapTerrainEdits", "SeaPower.LiveMap.MapProcessedHeight") ||
            !terrain[0].Parameters.Skip(1).All(p => p.IsOptional && p.HasConstant && p.Constant == null) ||
            !native.GetType("MapControl.MapInstance").Methods.Any(m => m.Name == "get_Name" && m.IsPublic) ||
            !dispose.Body.Instructions.Any(i => i.Operand is MethodReference r && r.Name == "set_Instance" && r.DeclaringType.FullName == "SeapowerUI.MapViewModel") ||
            native.GetType("SeapowerUI.ViewModels.CampaignMapViewModel").Fields.SingleOrDefault(f => f.Name == "_instance")?.FieldType.FullName != "MapControl.MapInstance")
            throw new InvalidOperationException("Inspected 261123 campaign map, side colour and drawing contract changed");
    }
}

