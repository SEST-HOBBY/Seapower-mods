using System;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    private static void CampaignSalvoTarget(ModuleDefinition module, ModuleDefinition native, Action<string> count)
    {
        const string oldName = "ShipAntiShipMissileAutoEngagementBlocked", newName = "AutoEngageAmmoBlocked";
        var ai = native.GetType("SeaPower.AI");
        var target = ai.Methods.Single(m => m.Name == newName);
        if (ai.Methods.Any(m => m.Name == oldName) || target.IsStatic || target.IsPublic || target.Body.CodeSize != 39 ||
            target.ReturnType.FullName != "System.Boolean" || !ParameterTypes(target, "SeaPower.AmmunitionParameters", "SeaPower.ObjectBase") ||
            target.Parameters[0].Name != "ap" || target.Parameters[1].Name != "targetObject" ||
            !ai.Fields.Any(f => f.Name == "_baseObject" && f.FieldType.FullName == "SeaPower.ObjectBase"))
            throw new InvalidOperationException("Inspected beta automatic-fire blocker changed");
        var patch = module.GetType("DynamicCampaignMod.Game.Patches.SalvoHoldPatch");
        var attribute = patch.CustomAttributes.Single(a => a.AttributeType.FullName == "HarmonyLib.HarmonyPatch");
        if (attribute.ConstructorArguments.Count != 2 || attribute.ConstructorArguments[0].Value is not TypeReference t ||
            t.FullName != "SeaPower.AI" || !Equals(attribute.ConstructorArguments[1].Value, oldName))
            throw new InvalidOperationException("Inspected DCM salvo-hold target changed");
        attribute.ConstructorArguments[1] = new CustomAttributeArgument(module.TypeSystem.String, newName);
        count("salvo-target");
        var applied = patch.Methods.Single(m => m.Name == "Applied");
        var name = applied.Body.Instructions.Single(i => i.OpCode == OpCodes.Ldstr && Equals(i.Operand, oldName));
        name.Operand = newName; count("salvo-applied");
        // The author's Holds predicate still admits only anti-ship missiles.
        // Postfix only ever changes false -> true; native blocks are retained.
    }
}
