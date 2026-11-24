// Topographic Map 1.8.0 keeps the metre-domain shallow-water threshold.
// Its mod-manager lookup now runs in the shared R.A.T.S. Rigging assembly.
using System;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    internal const string Topography180Hash = "50be459b47b78653a5d4709a83153ac11398512869be1d803646989aca77a6ea";

    private static ImageAdapter Topography180Adapter() => new ImageAdapter {
        Name = "Topography180", Hashes = new[] { Topography180Hash },
        RequireNative = TopographyRequireNative,
        RewriteMethod = Topography180Rewrite,
        ExpectedAudit = "shallow-threshold=1",
    };

    private static bool Topography180Rewrite(AdapterScope scope, TypeDefinition type, MethodDefinition method)
    {
        if (type.FullName == "SeaPowerTopo.Terrain.HeightReader" && method.Name == ".ctor") {
            if (method.Body.CodeSize != 106 || method.Body.Instructions[0].OpCode != OpCodes.Ldarg_0 || !ParameterTypes(method, "System.Collections.Generic.HashSet`1<System.String>", "System.Boolean") ||
                method.Body.Instructions.Any(i => i.Operand is FieldReference f && f.DeclaringType.FullName == "SeaPower.Globals"))
                throw new InvalidOperationException("Inspected Topographic Map 1.8.0 author option fallback changed");
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
