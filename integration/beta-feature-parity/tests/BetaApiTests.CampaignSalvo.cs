using System;
using System.IO;
using System.Linq;
using AnchorChain;
using Mono.Cecil;
using Mono.Cecil.Cil;

static partial class BetaApiTests
{
    static void R6_CampaignSalvo(R6Context context)
    {
        string source = Path.Combine(context.Workshop, "3813157776", "DynamicCampaignMod.dll");
        string prepared = BetaAssemblyPolicy.Prepare(source, context.Native, context.Cache, Console.WriteLine);
        using var before = ModuleDefinition.ReadModule(source);
        using var after = ModuleDefinition.ReadModule(prepared);
        var old = before.GetType("DynamicCampaignMod.Game.Patches.SalvoHoldPatch");
        var patch = after.GetType(old.FullName);
        var attr = patch.CustomAttributes.Single(a => a.AttributeType.FullName == "HarmonyLib.HarmonyPatch");
        Check(Equals(attr.ConstructorArguments[1].Value, "AutoEngageAmmoBlocked"), "DCM salvo hold targets the current native automatic-fire blocker");
        Check(patch.Methods.Single(m => m.Name == "Applied").Body.Instructions.Any(i => i.OpCode == OpCodes.Ldstr && Equals(i.Operand, "AutoEngageAmmoBlocked")), "DCM Works audit looks up the same adapted target");
        foreach (var name in new[] { "Holds", "Postfix" })
            Check(TopoInstructions(old.Methods.Single(m => m.Name == name)).SequenceEqual(TopoInstructions(patch.Methods.Single(m => m.Name == name))), "Author anti-ship-only predicate and native-block-preserving postfix retained: " + name);
        using var native = ModuleDefinition.ReadModule(context.Native);
        var target = native.GetType("SeaPower.AI").Methods.Single(m => m.Name == "AutoEngageAmmoBlocked");
        Check(target.ReturnType.FullName == "System.Boolean" && target.Parameters.Select(p => p.Name).SequenceEqual(new[] { "ap", "targetObject" }), "Harmony parameter names and return type match the real beta target");
    }
}
