// Sea Power Topographic Map globe image, Workshop 3826122523. R10 adapted
// 1.5.0 (cba22efb) and 1.6.0 (a6e75159). R14: the 14 November capture's 1.6.2
// (4490a285) keeps 1.6.0's author fallbacks for the removed world scaling
// options and its metre-domain shallow-water constant of -48 m, while 0.9.2's
// native ScaleDEMHeight still turns at -50 m. Only that constant is adapted.
// The flat-map DLL is held by the native-member check.
using System;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    internal const string Topography162Hash = "4490a285265314850f819b91fd3077e6ae37ca2c56020d69d90d1d31996380aa";

    private static ImageAdapter Topography162Adapter() => new ImageAdapter {
        Name = "Topography162", Hashes = new[] { Topography162Hash },
        RequireNative = TopographyRequireNative,
        RewriteMethod = Topography162Rewrite,
        ExpectedAudit = "shallow-threshold=1",
    };

    private static bool Topography162Rewrite(AdapterScope scope, TypeDefinition type, MethodDefinition method)
    {
        if (type.FullName == "SeaPowerTopo.Terrain.HeightReader" && method.Name == ".ctor") {
            if (method.Body.CodeSize != 115 || method.Body.Instructions[0].OpCode != OpCodes.Ldarg_0 || !ParameterTypes(method, "System.Collections.Generic.HashSet`1<System.String>") ||
                method.Body.Instructions.Any(i => i.Operand is FieldReference f && f.DeclaringType.FullName == "SeaPower.Globals"))
                throw new InvalidOperationException("Inspected Topographic Map 1.6.2 author option fallback changed");
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
