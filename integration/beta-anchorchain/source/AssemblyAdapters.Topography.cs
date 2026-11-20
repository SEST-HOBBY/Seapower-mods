// Sea Power Topographic Map globe image, Workshop 3826122523. R10 adapted
// 1.5.0 (cba22efb), 1.6.0 (a6e75159) and R14 1.6.2 (4490a285). R15: the 21
// November capture's 1.7.0 (32b00107) keeps the author fallbacks for the
// removed world scaling options and its metre-domain shallow-water constant
// of -48 m, while 0.9.3's native ScaleDEMHeight still turns at -50 m. Only
// that constant is adapted. 1.7.0's HeightReader .ctor gained an optional
// bool load parameter, and its shared ModState reads Assembly.Location
// (rewritten to the original location like other adapted images). The flat-map DLL (227ec990) is still held by the
// native-member check.
using System;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    internal const string Topography170Hash = "32b00107bbdeb705c6bb91045b0bb5396f5815724a239b8c8f78026e1382b206";

    private static ImageAdapter Topography170Adapter() => new ImageAdapter {
        Name = "Topography170", Hashes = new[] { Topography170Hash },
        RequireNative = TopographyRequireNative,
        RewriteMethod = Topography170Rewrite,
        // locations=1: 1.7.0's Rats.Shared.ModState.TickedInModManager reads
        // its own Assembly.Location (the Workshop folder name); the generic
        // pass points it at the original file, not the private cache copy.
        ExpectedAudit = "locations=1, shallow-threshold=1",
    };

    private static bool Topography170Rewrite(AdapterScope scope, TypeDefinition type, MethodDefinition method)
    {
        if (type.FullName == "SeaPowerTopo.Terrain.HeightReader" && method.Name == ".ctor") {
            if (method.Body.CodeSize != 106 || method.Body.Instructions[0].OpCode != OpCodes.Ldarg_0 || !ParameterTypes(method, "System.Collections.Generic.HashSet`1<System.String>", "System.Boolean") ||
                method.Body.Instructions.Any(i => i.Operand is FieldReference f && f.DeclaringType.FullName == "SeaPower.Globals"))
                throw new InvalidOperationException("Inspected Topographic Map 1.7.0 author option fallback changed");
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
}
