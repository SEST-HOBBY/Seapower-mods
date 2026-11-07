using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;

namespace Sest.UiFixes
{
    internal static class CostCatalogueCache
    {
        static readonly ScopeValueCache cache = new ScopeValueCache();
        static Type priceType;
        static bool installed;
        static long hits, misses, builds, invalidations;
        static readonly FieldInfo labels = typeof(CodeInstruction).GetField("labels");
        // Harmony's framework Label reference is missing from the netstandard
        // compiler facade. IList keeps the actual runtime labels intact.
        static IList Labels(CodeInstruction instruction) { return (IList)labels.GetValue(instruction); }
        internal static void Install()
        {
            var hooks = new Harmony("io.github.sest-hobby.cost-catalogue-cache");
            try
            {
                var campaign = ContactsFix.Find("Sest.RuntimeFixes.CampaignCosts");
                ContactsFix.Require(campaign.Assembly, "7ba6d6d9c58b6c3db31d731e951ed7ea3979925bdff054c9b92482dbe69c9986");
                var target = campaign.GetMethod("Prices", ContactsFix.All, null, Type.EmptyTypes, null);
                priceType = campaign.Assembly.GetType("Sest.RuntimeFixes.CombatPrices", true);
                if (target == null || !target.IsStatic || target.ReturnType != priceType || target.GetMethodBody().ExceptionHandlingClauses.Count != 0)
                    throw new MissingMethodException("Inspected price-catalogue factory");
                var overlay = ContactsFix.Find("WeaponCostsMod.Overlay");
                ContactsFix.Require(overlay.Assembly, "74afa9028fc0c52b93f415263504f51ecf8d056a624feaebcc8053ba5a1c0ac3");
                var reload = overlay.GetMethod("LoadConfig", ContactsFix.All, null, new[] { typeof(bool) }, null);
                if (reload == null || reload.ReturnType != typeof(void)) throw new MissingMethodException("Inspected tracker config reload");
                hooks.Patch(target, transpiler: new HarmonyMethod(typeof(CostCatalogueCache), nameof(Reuse)));
                hooks.Patch(reload, postfix: new HarmonyMethod(typeof(CostCatalogueCache), nameof(Clear)));
                installed = true;
                ContactsFix.Log("Cost catalogues: reuse successful price factory results within each mission; clear on mission changes and tracker config reload. Live expenditure, losses, history and refresh cadence retained.");
            }
            catch (Exception e)
            {
                hooks.UnpatchSelf(); Clear();
                ContactsFix.Log("Cost catalogue cache inactive; original pricing retained: " + e.Message);
            }
        }
        public static IEnumerable<CodeInstruction> Reuse(IEnumerable<CodeInstruction> input, ILGenerator generator)
        {
            var body = input.ToList();
            if (priceType == null || body.Count(c => c.opcode == OpCodes.Ret) != 2 || body.Any(c => c.blocks.Count != 0))
                throw new InvalidOperationException("Price factory return/exception-region audit changed");
            var get = typeof(CostCatalogueCache).GetMethod(nameof(Get));
            var remember = typeof(CostCatalogueCache).GetMethod(nameof(Remember));
            var original = generator.DefineLabel();
            var pop = new CodeInstruction(OpCodes.Pop); Labels(pop).Add(original);
            var result = new List<CodeInstruction> {
                new CodeInstruction(OpCodes.Call, get), new CodeInstruction(OpCodes.Dup),
                new CodeInstruction(OpCodes.Brfalse, original),
                new CodeInstruction(OpCodes.Castclass, priceType), new CodeInstruction(OpCodes.Ret), pop
            };
            foreach (var instruction in body)
            {
                if (instruction.opcode.OperandType == OperandType.ShortInlineBrTarget)
                {
                    string name = instruction.opcode.Name.Replace(".s", "").Replace('.', '_');
                    instruction.opcode = (OpCode)typeof(OpCodes).GetField(name,
                        BindingFlags.Public | BindingFlags.Static | BindingFlags.IgnoreCase).GetValue(null);
                }
                if (instruction.opcode == OpCodes.Ret)
                {
                    // Branches to a return must also pass through Remember.
                    var duplicate = new CodeInstruction(OpCodes.Dup);
                    foreach (var label in Labels(instruction)) Labels(duplicate).Add(label);
                    Labels(instruction).Clear();
                    result.Add(duplicate); result.Add(new CodeInstruction(OpCodes.Call, remember));
                }
                result.Add(instruction);
            }
            return result;
        }
        public static object Get()
        {
            object scope = PerformanceReview.MissionContext;
            object value = cache.Get(scope);
            if (scope != null) { if (value == null) misses++; else hits++; }
            return value;
        }
        public static void Remember(object value)
        {
            object scope = PerformanceReview.MissionContext;
            cache.Remember(scope, value);
            if (scope != null && value != null) builds++;
        }
        public static void Clear() { cache.Clear(); invalidations++; }
        internal static void Report()
        {
            if (!installed) return;
            ContactsFix.Log("Cost catalogue reuse (30 s): " + hits + " hit(s), " + misses + " miss(es), " + builds +
                " successful build(s), " + invalidations + " invalidation(s). Quantities and report rows still use the original live refresh.");
            hits = misses = builds = invalidations = 0;
        }
    }
}
