using System;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    private const string SalvoHoldPatch = "DynamicCampaignMod.Game.Patches.SalvoHoldPatch";
    private const string CampaignFacts = "DynamicCampaignMod.Game.GameFacts";
    internal const string SalvoHoldFeature = "the battle AI holding the game's single anti-ship shots while it masses a salvo";

    // 261107 merged the 261026 ShipAntiShipMissileAutoEngagementBlocked into
    // AI.AutoEngageAmmoBlocked. Its new gun and air-director callers cannot
    // reach the author's hold: they pass only Projectile ammunition or an
    // aircraft shooter, while Holds admits only Missile/ASuW ammunition from a
    // ship or submarine in BattleSession.SalvoShooters. The managed test
    // R6_CampaignSalvo asserts that scope on the pinned native image.
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
        // The author names the old blocker in three places: the Harmony
        // target, the Works audit, and the GameFacts entry that turns the
        // feature off when the member is missing. All three move together.
        var sites = Types(module.Types).SelectMany(t => t.Methods).Where(m => m.HasBody)
            .SelectMany(m => m.Body.Instructions.Where(i => i.OpCode == OpCodes.Ldstr && Equals(i.Operand, oldName)).Select(i => (Method: m, Site: i)))
            .ToList();
        var applied = sites.Where(s => s.Method.DeclaringType.FullName == SalvoHoldPatch && s.Method.Name == "Applied").ToList();
        var facts = sites.Where(s => s.Method.DeclaringType.FullName == CampaignFacts && s.Method.Name == ".cctor").ToList();
        if (sites.Count != 2 || applied.Count != 1 || facts.Count != 1)
            throw new InvalidOperationException("Inspected DCM salvo-hold member references changed");
        var patch = module.GetType(SalvoHoldPatch);
        var attribute = patch.CustomAttributes.Single(a => a.AttributeType.FullName == "HarmonyLib.HarmonyPatch");
        if (attribute.ConstructorArguments.Count != 2 || attribute.ConstructorArguments[0].Value is not TypeReference t ||
            t.FullName != "SeaPower.AI" || !Equals(attribute.ConstructorArguments[1].Value, oldName))
            throw new InvalidOperationException("Inspected DCM salvo-hold target changed");
        // GameFacts..cctor registers the member as: ldstr "AI"; ldstr member;
        // ldstr feature; call GameFacts.Method(type, name, feature); stelem.ref
        var fact = facts[0].Site;
        if (fact.Previous?.OpCode != OpCodes.Ldstr || !Equals(fact.Previous.Operand, "AI") ||
            fact.Next?.OpCode != OpCodes.Ldstr || !Equals(fact.Next.Operand, SalvoHoldFeature) ||
            fact.Next.Next?.OpCode != OpCodes.Call || fact.Next.Next.Operand is not MethodReference register ||
            register.DeclaringType.FullName != CampaignFacts || register.Name != "Method" ||
            !ParameterTypes(register, "System.String", "System.String", "System.String") || fact.Next.Next.Next?.OpCode != OpCodes.Stelem_Ref)
            throw new InvalidOperationException("Inspected DCM salvo-hold game fact changed");
        attribute.ConstructorArguments[1] = new CustomAttributeArgument(module.TypeSystem.String, newName);
        count("salvo-target");
        applied[0].Site.Operand = newName; count("salvo-applied");
        fact.Operand = newName; count("salvo-fact");
        // The author's Holds predicate still admits only anti-ship missiles.
        // Postfix only ever changes false -> true; native blocks are retained.
    }
}
