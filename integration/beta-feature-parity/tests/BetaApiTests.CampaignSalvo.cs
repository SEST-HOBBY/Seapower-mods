using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using AnchorChain;
using HarmonyLib;
using Mono.Cecil;
using Mono.Cecil.Cil;

static partial class BetaApiTests
{
    const string SalvoOld = "ShipAntiShipMissileAutoEngagementBlocked", SalvoNew = "AutoEngageAmmoBlocked";
    const string SalvoFeature = "the battle AI holding the game's single anti-ship shots while it masses a salvo";
    const string CampaignAudit = "HasNightCapableSensors=1, attack-property=14, drawing-layer=1, flat-tiles=2, fuel-refresh=1, globe-fail-guard=1, group-brush=2, locations=4, scheduler-timing=1, side-colour=8, terrain-background=1";

    // Dynamic Campaign Mod 1.0.2 (23 Nov 2026, 18a2416e) still names the
    // blocker Sea Power merged into AI.AutoEngageAmmoBlocked. Up to R15 SEST
    // renamed the author's three references onto the new blocker. It no
    // longer does: 1.0.0 widened the hold (1.0.1 and 1.0.2 keep it) to a "keep shots
    // clear" sweep that takes in allied aircraft, which the earlier
    // ship-and-submarine argument for the rename did not cover. These checks assert what happens instead:
    // the adapted image keeps the author's salvo code as written, the mod's
    // own game-member check finds that one member missing on 0.9.3 and
    // switches the feature off, and Harmony refuses the patch, so the game's
    // blocker is never touched.
    static void R6_CampaignSalvo(R6Context context)
    {
        string source = Path.Combine(context.Workshop, "3813157776", "DynamicCampaignMod.dll");
        var log = new List<string>();
        string prepared = BetaAssemblyPolicy.Prepare(source, context.Native, context.Cache, log.Add);
        var adaptedLines = log.Where(l => l.StartsWith("ADAPTED DynamicCampaignMod", StringComparison.Ordinal)).ToList();
        Check(adaptedLines.Count == 1 && adaptedLines[0].Contains(": " + CampaignAudit + ";") && !adaptedLines[0].Contains("salvo"),
            "DCM audit is exactly the four kept rewrites plus the 261123 map bridges, with no salvo-hold rename (" + String.Join(" | ", adaptedLines) + ")");
        using var before = ModuleDefinition.ReadModule(source);
        using var after = ModuleDefinition.ReadModule(prepared);
        using var native = ModuleDefinition.ReadModule(context.Native);

        // The game: the old name is gone, the merged blocker exists.
        var ai = native.GetType("SeaPower.AI");
        Check(!ai.Methods.Any(m => m.Name == SalvoOld) && !ai.Fields.Any(f => f.Name == SalvoOld) && !ai.Properties.Any(p => p.Name == SalvoOld),
            "0.9.3 has no AI member named " + SalvoOld);
        Check(ai.Methods.Count(m => m.Name == SalvoNew) == 1, "0.9.3 has the merged blocker AI." + SalvoNew);

        // The adapted image: the author's three references are untouched.
        IEnumerable<(MethodDefinition Method, Instruction Site)> Literals(ModuleDefinition module, string text) =>
            Types(module.Types).SelectMany(t => t.Methods).Where(m => m.HasBody)
                .SelectMany(m => m.Body.Instructions.Where(i => i.OpCode == OpCodes.Ldstr && Equals(i.Operand, text)).Select(i => (m, i)));
        string[] Sites(ModuleDefinition module) => Literals(module, SalvoOld).Select(s => s.Method.DeclaringType.FullName + "::" + s.Method.Name)
            .OrderBy(x => x, StringComparer.Ordinal).ToArray();
        var expectedSites = new[] { "DynamicCampaignMod.Game.GameFacts::.cctor", "DynamicCampaignMod.Game.Patches.SalvoHoldPatch::Applied" };
        Check(Sites(before).SequenceEqual(expectedSites) && Sites(after).SequenceEqual(expectedSites),
            "The author names the old blocker in GameFacts and SalvoHoldPatch.Applied, before and after adaptation");
        Check(!Literals(after, SalvoNew).Any(), "No reference to AI." + SalvoNew + " is written into the adapted image");
        var old = before.GetType("DynamicCampaignMod.Game.Patches.SalvoHoldPatch");
        var patch = after.GetType(old.FullName);
        foreach (var type in new[] { old, patch }) {
            var attr = type.CustomAttributes.Single(a => a.AttributeType.FullName == "HarmonyLib.HarmonyPatch");
            Check(attr.ConstructorArguments.Count == 2 && (attr.ConstructorArguments[0].Value as TypeReference)?.FullName == "SeaPower.AI" &&
                Equals(attr.ConstructorArguments[1].Value, SalvoOld), "DCM salvo hold still targets AI." + SalvoOld);
        }
        var salvoTypes = new[] { old }.Concat(old.NestedTypes).ToList();
        Check(salvoTypes.Count == 2 && salvoTypes.SelectMany(t => t.Methods).Count(m => m.HasBody) >= 5, "Inspected SalvoHoldPatch shape (patch class and its lambda class)");
        foreach (var type in salvoTypes) foreach (var method in type.Methods.Where(m => m.HasBody)) {
            var same = after.GetType(type.FullName).Methods.Single(m => m.FullName == method.FullName);
            Check(TopoInstructions(method).SequenceEqual(TopoInstructions(same)), "Author salvo-hold code retained as written: " + type.Name + "::" + method.Name);
        }
        Check(TopoInstructions(before.GetType("DynamicCampaignMod.Game.GameFacts").Methods.Single(m => m.Name == ".cctor"))
            .SequenceEqual(TopoInstructions(after.GetType("DynamicCampaignMod.Game.GameFacts").Methods.Single(m => m.Name == ".cctor"))),
            "The author's GameFacts table is retained as written");
        // Both readers of SalvoHoldPatch.Works ask GameFacts first:
        // ldstr feature; call GameFacts.Has; brfalse; call get_Works.
        var readers = Types(after.Types).SelectMany(t => t.Methods).Where(m => m.HasBody)
            .SelectMany(m => m.Body.Instructions.Where(i => i.Operand is MethodReference r && r.Name == "get_Works" && r.DeclaringType.FullName == old.FullName).Select(i => (Method: m, Site: i))).ToList();
        Check(readers.Select(r => r.Method.DeclaringType.FullName + "::" + r.Method.Name).OrderBy(x => x, StringComparer.Ordinal)
            .SequenceEqual(new[] { "DynamicCampaignMod.Game.Battle.BattleSession::KeepShotsClear", "DynamicCampaignMod.Game.Battle.BattleSession::PlanSalvos" }),
            "The salvo hold is read only by BattleSession.KeepShotsClear and PlanSalvos");
        Check(readers.All(r => r.Site.Previous.OpCode == OpCodes.Brfalse && r.Site.Previous.Previous.Operand is MethodReference has && has.Name == "Has" &&
            has.DeclaringType.FullName == "DynamicCampaignMod.Game.GameFacts" && Equals(r.Site.Previous.Previous.Previous.Operand, SalvoFeature)),
            "Both readers require GameFacts.Has(salvo hold) before SalvoHoldPatch.Works");

        // Run the mod's own game-member check on the adapted image, as its
        // patcher does at startup. It logs through Plugin.Log, which BepInEx
        // sets in the game; give it a log source here.
        var loaded = AppDomain.CurrentDomain.GetAssemblies().FirstOrDefault(a => !a.IsDynamic && !String.IsNullOrEmpty(a.Location) &&
            String.Equals(Path.GetFullPath(a.Location), Path.GetFullPath(prepared), StringComparison.Ordinal)) ?? Assembly.LoadFile(prepared);
        const BindingFlags all = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance;
        var pluginLog = loaded.GetType("DynamicCampaignMod.Plugin", true).GetField("Log", all);
        if (pluginLog.GetValue(null) == null) pluginLog.SetValue(null, Activator.CreateInstance(pluginLog.FieldType, "SEST-BetaApiTests"));
        var gameFacts = loaded.GetType("DynamicCampaignMod.Game.GameFacts", true);
        var essentialMissing = (List<string>)gameFacts.GetMethod("Check", all).Invoke(null, null);
        Check(essentialMissing.Count == 0, "DCM's own check finds every essential game member on 0.9.3 (" + String.Join(", ", essentialMissing) + ")");
        var facts = ((IEnumerable)gameFacts.GetField("Facts", all).GetValue(null)).Cast<object>().ToList();
        object Get(object o, string f) => o.GetType().GetField(f, all).GetValue(o);
        var missing = facts.Where(f => ((Func<object>)Get(f, "Find"))() == null).ToList();
        Check(facts.Count == 833 && missing.Count == 1 && (string)Get(missing[0], "What") == "AI." + SalvoOld && (string)Get(missing[0], "Feature") == SalvoFeature &&
            (string)Get(missing[0], "Kind") == "method" && !(bool)Get(missing[0], "Essential"),
            "Of DCM's 833 game facts, 0.9.3 misses only the non-essential method AI." + SalvoOld + " (missing: " + String.Join(", ", missing.Select(f => Get(f, "What"))) + ")");
        Check(facts.Where(f => (string)Get(f, "Feature") == SalvoFeature).Select(f => (string)Get(f, "What")).OrderBy(x => x, StringComparer.Ordinal)
            .SequenceEqual(new[] { "AI." + SalvoOld, "AI._baseObject", "AI._defensiveMissileTargets" }), "Salvo-hold feature lists the old blocker and its two AI fields");
        var off = (IDictionary)gameFacts.GetField("Off", all).GetValue(null);
        Check(off.Count == 1 && off.Contains(SalvoFeature) && ((IEnumerable<string>)off[SalvoFeature]).SequenceEqual(new[] { "AI." + SalvoOld }),
            "DCM's check switches off exactly one feature, the salvo hold, for the missing blocker (off: " + String.Join(" | ", off.Keys.Cast<string>()) + ")");
        var has = gameFacts.GetMethod("Has", all);
        Check(!(bool)has.Invoke(null, new object[] { SalvoFeature }), "GameFacts.Has reports the salvo hold off on 0.9.3");
        var features = facts.Select(f => (string)Get(f, "Feature")).Distinct().Where(f => f != SalvoFeature).ToList();
        Check(features.Count > 50 && features.All(f => (bool)has.Invoke(null, new object[] { f })), "GameFacts.Has leaves every other feature on");
        // The check does not gate AI._objectToDestroy: it accepts the 0.9.3
        // property for its three field entries, so those features stay on and
        // the loader's attack-property rewrite of the field accesses is needed.
        var attack = facts.Where(f => (string)Get(f, "What") == "AI._objectToDestroy").ToList();
        Check(attack.Count == 3 && attack.All(f => (string)Get(f, "Kind") == "field" && (string)Get(f, "FoundKind") == "property" && !off.Contains((string)Get(f, "Feature"))),
            "DCM's check finds AI._objectToDestroy as a property and leaves its three features on");

        // Harmony refuses the patch class (the mod's patcher catches this and
        // logs "Patch SalvoHoldPatch not applied"), Works reads false, and the
        // game's blocker carries no patch.
        var holdPatch = loaded.GetType(old.FullName, true);
        bool refused = false;
        try { new Harmony("sest.beta-api-tests.salvo").CreateClassProcessor(holdPatch).Patch(); }
        catch (HarmonyException) { refused = true; }
        Check(refused, "Harmony refuses SalvoHoldPatch on 0.9.3: its target method does not exist");
        Check(!(bool)holdPatch.GetProperty("Works", all).GetValue(null), "SalvoHoldPatch.Works reads false");
        var blocker = typeof(SeaPower.AI).GetMethod(SalvoNew, all);
        Check(blocker != null && Harmony.GetPatchInfo(blocker) == null, "The game's AI." + SalvoNew + " is left unpatched");
    }

    // Compares two method bodies by opcode and operand, with branch targets
    // as instruction indexes (moved here from the retired Topography checks).
    static string[] TopoInstructions(MethodDefinition method)
        => method.Body.Instructions.Select(i => {
            string op = i.OpCode.Name.EndsWith(".s", StringComparison.Ordinal) && i.Operand is Mono.Cecil.Cil.Instruction
                ? i.OpCode.Name.Substring(0, i.OpCode.Name.Length - 2) : i.OpCode.Name;
            string operand = i.Operand is Mono.Cecil.Cil.Instruction target ? "target:" + method.Body.Instructions.IndexOf(target) :
                i.Operand is Mono.Cecil.Cil.Instruction[] targets ? String.Join(",", targets.Select(t => method.Body.Instructions.IndexOf(t))) :
                i.Operand?.ToString();
            return op + " " + operand;
        }).ToArray();
}
