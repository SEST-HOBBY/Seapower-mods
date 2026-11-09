// R10: Sea Power Topographic Map 1.5.0 globe image, Workshop 3826122523.
// The captured 261107 game removed the two world scaling options. Preserve
// the author's map renderer in metres, with the current native fixed factors
// and the native 50 m shallow-water boundary. The flat-map DLL stays held.
using System;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    internal const string TopographyHash = "cba22efb544775821c5f5d461a90059225bd5526228d7d6f76e708eeef299619";

    private static ImageAdapter TopographyAdapter() => new ImageAdapter {
        Name = "Topography", Hashes = new[] { TopographyHash },
        RequireNative = TopographyRequireNative,
        RewriteMethod = TopographyRewrite,
        ExpectedAudit = "depth-scale=2, land-scale=2, shallow-threshold=1",
    };

    private static void TopographyRequireNative(ModuleDefinition native)
    {
        CurrentNativeSnapshot(native);
        var globals = native.GetType("SeaPower.Globals");
        if (globals.Fields.Any(f => f.Name == "_heightMultiplier" || f.Name == "_underWaterDepthFactor"))
            throw new InvalidOperationException("Inspected native terrain-option removal changed");
        var methods = native.GetType("SeaPower.TerrainUtils").Methods;
        var scale = methods.Single(m => m.Name == "ScaleDEMHeight" && ParameterTypes(m, "System.Double"));
        var constants = scale.Body.Instructions.Where(i => i.OpCode == OpCodes.Ldc_R8).Select(i => (double)i.Operand).ToArray();
        if (!scale.IsPublic || !scale.IsStatic || scale.ReturnType.FullName != "System.Double" || scale.Body.CodeSize != 66 ||
            constants.Length != 5 || constants[0] != 0d || constants[1] != 1d || constants[3] != 2d || constants[4] != 2d)
            throw new InvalidOperationException("Inspected native terrain scaling changed");
        var toUnity = native.GetType("SeaPower.Utils").Methods.Single(m => m.Name == "heightInMeterToUnity" && ParameterTypes(m, "System.Single"));
        var factors = toUnity.Body.Instructions.Where(i => i.OpCode == OpCodes.Ldc_R4).Select(i => (float)i.Operand).ToArray();
        if (factors.Length != 1 || Math.Abs(constants[2] / factors[0] + 50d) > 0.00001d)
            throw new InvalidOperationException("Inspected native shallow-water units/boundary changed");
    }

    private static bool TopographyRewrite(AdapterScope scope, TypeDefinition type, MethodDefinition method)
    {
        if (type.FullName == "SeaPowerTopo.Terrain.HeightReader" && method.Name == ".ctor") {
            if (method.IsStatic || !ParameterTypes(method, "System.Collections.Generic.HashSet`1<System.String>") || method.Body.CodeSize != 133)
                throw new InvalidOperationException("Inspected Topography height-reader constructor changed");
            var sites = new[] { (Offset: 0x003e, Name: "_heightMultiplier", Value: 1f, Audit: "land-scale"),
                (Offset: 0x0051, Name: "_heightMultiplier", Value: 1f, Audit: "land-scale"),
                (Offset: 0x005c, Name: "_underWaterDepthFactor", Value: 2f, Audit: "depth-scale"),
                (Offset: 0x006f, Name: "_underWaterDepthFactor", Value: 2f, Audit: "depth-scale") };
            foreach (var site in sites) {
                var instruction = method.Body.Instructions.Single(i => i.Offset == site.Offset);
                if (instruction.OpCode != OpCodes.Ldsfld || instruction.Operand is not FieldReference field ||
                    field.DeclaringType.FullName != "SeaPower.Globals" || field.Name != site.Name || field.FieldType.FullName != "System.Single")
                    throw new InvalidOperationException("Inspected Topography terrain-option read changed");
                instruction.OpCode = OpCodes.Ldc_R4; instruction.Operand = site.Value; scope.Count(site.Audit);
            }
        }
        if (type.FullName == "SeaPowerTopo.Render.Raster" && method.Name == "SimHeight") {
            if (!method.IsStatic || method.ReturnType.FullName != "System.Single" || method.Body.CodeSize != 34 ||
                !ParameterTypes(method, "System.Single", "System.Single", "System.Single"))
                throw new InvalidOperationException("Inspected Topography metre-scaling method changed");
            var threshold = method.Body.Instructions.Single(i => i.Offset == 0x0011);
            if (threshold.OpCode != OpCodes.Ldc_R4 || !Equals(threshold.Operand, -48f))
                throw new InvalidOperationException("Inspected Topography shallow-water boundary changed");
            // This method receives DEM METRES. Native ScaleDEMHeight receives
            // UNITY heights; its -0.744... boundary is -50 m, not -0.744 m.
            // Keep the original per-pixel implementation and its units.
            threshold.Operand = -50f; scope.Count("shallow-threshold");
        }
        return false;
    }
}
