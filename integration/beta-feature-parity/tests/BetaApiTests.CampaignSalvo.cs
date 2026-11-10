using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using AnchorChain;
using Mono.Cecil;
using Mono.Cecil.Cil;

static partial class BetaApiTests
{
    const string SalvoOld = "ShipAntiShipMissileAutoEngagementBlocked", SalvoNew = "AutoEngageAmmoBlocked";
    const string SalvoFeature = "the battle AI holding the game's single anti-ship shots while it masses a salvo";

    static void R6_CampaignSalvo(R6Context context)
    {
        string source = Path.Combine(context.Workshop, "3813157776", "DynamicCampaignMod.dll");
        var log = new List<string>();
        string prepared = BetaAssemblyPolicy.Prepare(source, context.Native, context.Cache, log.Add);
        Check(log.Count(l => l.StartsWith("ADAPTED DynamicCampaignMod", StringComparison.Ordinal) &&
            l.Contains("salvo-applied=1, salvo-fact=1, salvo-target=1")) == 1, "DCM audit names all three salvo-hold sites once");
        using var before = ModuleDefinition.ReadModule(source);
        using var after = ModuleDefinition.ReadModule(prepared);
        var old = before.GetType("DynamicCampaignMod.Game.Patches.SalvoHoldPatch");
        var patch = after.GetType(old.FullName);
        var attr = patch.CustomAttributes.Single(a => a.AttributeType.FullName == "HarmonyLib.HarmonyPatch");
        Check(Equals(attr.ConstructorArguments[1].Value, SalvoNew), "DCM salvo hold targets the current native automatic-fire blocker");
        Check(patch.Methods.Single(m => m.Name == "Applied").Body.Instructions.Any(i => i.OpCode == OpCodes.Ldstr && Equals(i.Operand, SalvoNew)), "DCM Works audit looks up the same adapted target");
        foreach (var name in new[] { "Holds", "Postfix" })
            Check(TopoInstructions(old.Methods.Single(m => m.Name == name)).SequenceEqual(TopoInstructions(patch.Methods.Single(m => m.Name == name))), "Author anti-ship-only predicate and native-block-preserving postfix retained: " + name);
        IEnumerable<(MethodDefinition Method, Instruction Site)> Literals(ModuleDefinition module, string text) =>
            Types(module.Types).SelectMany(t => t.Methods).Where(m => m.HasBody)
                .SelectMany(m => m.Body.Instructions.Where(i => i.OpCode == OpCodes.Ldstr && Equals(i.Operand, text)).Select(i => (m, i)));
        Check(Literals(before, SalvoOld).Count() == 2 && !Literals(after, SalvoOld).Any() &&
            after.GetType("DynamicCampaignMod.Game.Patches.SalvoHoldPatch").CustomAttributes.All(a => a.ConstructorArguments.All(c => !Equals(c.Value, SalvoOld))),
            "No DCM reference to the removed 261026 blocker remains");
        var fact = Literals(after, SalvoNew).Single(s => s.Method.DeclaringType.FullName == "DynamicCampaignMod.Game.GameFacts").Site;
        Check(fact.Previous.OpCode == OpCodes.Ldstr && Equals(fact.Previous.Operand, "AI") && Equals(fact.Next.Operand, SalvoFeature) &&
            (fact.Next.Next.Operand as MethodReference)?.Name == "Method", "GameFacts registers AI.AutoEngageAmmoBlocked as a method fact for the salvo hold");
        // Everything else in the GameFacts table is unchanged.
        var oldFacts = TopoInstructions(before.GetType("DynamicCampaignMod.Game.GameFacts").Methods.Single(m => m.Name == ".cctor"));
        var newFacts = TopoInstructions(after.GetType("DynamicCampaignMod.Game.GameFacts").Methods.Single(m => m.Name == ".cctor"));
        var changed = Enumerable.Range(0, Math.Min(oldFacts.Length, newFacts.Length)).Where(i => oldFacts[i] != newFacts[i]).ToList();
        // The existing bearing-reflection rule already renames the table's
        // GeoPosition.CourseTo fact; the salvo fact is the only other change.
        Check(oldFacts.Length == newFacts.Length && changed.Select(i => oldFacts[i] + " -> " + newFacts[i]).OrderBy(x => x, StringComparer.Ordinal)
            .SequenceEqual(new[] { "ldstr CourseTo -> ldstr HeadingToPosition", "ldstr " + SalvoOld + " -> ldstr " + SalvoNew }),
            "GameFacts table differs only in the adapted bearing and salvo-hold member names");
        using var native = ModuleDefinition.ReadModule(context.Native);
        var target = native.GetType("SeaPower.AI").Methods.Single(m => m.Name == SalvoNew);
        Check(target.ReturnType.FullName == "System.Boolean" && target.Parameters.Select(p => p.Name).SequenceEqual(new[] { "ap", "targetObject" }), "Harmony parameter names and return type match the real beta target");

        // Run DCM's own fact lookup on the adapted image: the salvo-hold
        // feature's member facts must all resolve, so GameFacts.Has keeps it on.
        var loaded = AppDomain.CurrentDomain.GetAssemblies().FirstOrDefault(a => !a.IsDynamic && !String.IsNullOrEmpty(a.Location) &&
            String.Equals(Path.GetFullPath(a.Location), Path.GetFullPath(prepared), StringComparison.Ordinal)) ?? Assembly.LoadFile(prepared);
        const BindingFlags all = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance;
        var facts = ((IEnumerable)loaded.GetType("DynamicCampaignMod.Game.GameFacts", true).GetField("Facts", all).GetValue(null)).Cast<object>().ToList();
        object Get(object o, string f) => o.GetType().GetField(f, all).GetValue(o);
        var salvo = facts.Where(f => (string)Get(f, "Feature") == SalvoFeature).ToList();
        Check(salvo.Select(f => (string)Get(f, "What")).OrderBy(x => x, StringComparer.Ordinal)
            .SequenceEqual(new[] { "AI." + SalvoNew, "AI._baseObject", "AI._defensiveMissileTargets" }), "Salvo-hold feature lists the current blocker and its two AI fields");
        Check(!facts.Any(f => ((string)Get(f, "What")).Contains(SalvoOld)), "No GameFacts entry names the removed blocker");
        foreach (var entry in salvo) {
            var member = ((Func<object>)Get(entry, "Find"))() as MemberInfo;
            Check(member != null && member.DeclaringType == typeof(SeaPower.AI), "Salvo-hold game fact resolves on 261107: " + Get(entry, "What"));
        }
        var blocker = ((Func<object>)Get(salvo.Single(f => (string)Get(f, "What") == "AI." + SalvoNew), "Find"))() as MethodInfo;
        Check(blocker != null && blocker.Name == SalvoNew && (string)Get(salvo.Single(f => (string)Get(f, "What") == "AI." + SalvoNew), "Kind") == "method" &&
            blocker.GetParameters().Select(p => p.ParameterType).SequenceEqual(new[] { typeof(SeaPower.AmmunitionParameters), typeof(SeaPower.ObjectBase) }),
            "GameFacts entry for AI.AutoEngageAmmoBlocked resolves to the native method");

        CampaignSalvoScope(native);
    }

    // Scope of the hold on the new target. The 261026 blocker was called
    // only from SelectLauncherAmmoForAutoEngage and SelectAmmunition. The
    // 261107 blocker is also called from gun-ammunition selection and from the
    // air engagement director. DCM's Holds admits only Missile (2) ammunition
    // with an ASuW (2) target and a shooter in BattleSession.SalvoShooters,
    // which DCM fills only from surface groups and submarines. Assert that the
    // new paths pass only Projectile ammunition or an aircraft shooter, so the
    // hold covers exactly the shots it covered on 261026.
    static void CampaignSalvoScope(ModuleDefinition native)
    {
        var all = Types(native.Types).SelectMany(t => t.Methods).Where(m => m.HasBody).ToList();
        string[] Callers(string type, string name) => all.Where(m => m.Body.Instructions.Any(i => i.Operand is MethodReference r &&
                r.Name == name && r.DeclaringType.FullName == type))
            .Select(m => m.DeclaringType.FullName + "::" + m.Name).Distinct().OrderBy(n => n, StringComparer.Ordinal).ToArray();
        bool Same(string[] actual, params string[] expected) => actual.SequenceEqual(expected.OrderBy(n => n, StringComparer.Ordinal));
        var ai = native.GetType("SeaPower.AI");
        Check(Same(Callers("SeaPower.AI", SalvoNew), "SeaPower.AI::SelectLauncherAmmoForAutoEngage", "SeaPower.AI::SelectAmmunition",
            "SeaPower.AI::SelectGunAmmoForAutoEngage", "SeaPower.AI::DirectorAmmoBlocked"), "Native automatic-fire blocker has the four inspected callers");
        Check(ProjectileOnly(ai.Methods.Single(m => m.Name == "SelectGunAmmoForAutoEngage"), SalvoNew), "Gun-ammunition path reaches the blocker only for Projectile ammunition");
        Check(Same(Callers("SeaPower.AI", "DirectorAmmoBlocked"), "SeaPower.AI::DirectorPlanShot", "SeaPower.AI::DirectorPlanGunShot"), "Director blocker has the two inspected callers");
        Check(ProjectileOnly(ai.Methods.Single(m => m.Name == "DirectorPlanGunShot"), "DirectorAmmoBlocked"), "Director gun path reaches the blocker only for Projectile ammunition");
        Check(Same(Callers("SeaPower.AI", "DirectorPlanShot"), "SeaPower.AirEngagementDirector::BuildPairs"), "Director missile path is planned only by the air engagement director");
        var build = native.GetType("SeaPower.AirEngagementDirector").Methods.Single(m => m.Name == "BuildPairs");
        var plan = build.Body.Instructions.Where(i => i.Operand is MethodReference r && r.Name == "DirectorPlanShot").ToList();
        Check(plan.Count == 1 && AircraftShooter(build, plan[0]), "Air engagement director plans shots only for its aircraft");
        Check(Same(Callers("SeaPower.AI", "SelectLauncherAmmoForAutoEngage"), "SeaPower.AI::BidOnEngagement", "SeaPower.AI::AutoAttackOpponentInRange",
            "SeaPower.AI::FireTaskforceCuedMissiles", "SeaPower.AI::FireSubmarineMissileVolley", "SeaPower.AI::ReconsiderHeldAirShot"),
            "Launcher path has the 261026 callers plus the aircraft-only held-shot review");
        Check(ai.Methods.Single(m => m.Name == "ReconsiderHeldAirShot").Body.Instructions.Take(16).Any(i => i.OpCode == OpCodes.Castclass &&
            ((TypeReference)i.Operand).FullName == "SeaPower.Aircraft"), "Held-shot review runs only for aircraft");
        Check(Same(Callers("SeaPower.AI", "SelectAmmunition"), "SeaPower.AI::AutoAttackByClick"), "Click-attack path is unchanged from 261026");
    }

    // ldloc ap; ldfld AmmunitionParameters::_type; ldc.i4.1; bne.un skip;
    // then only argument loads (including the same ap) before the call.
    static bool ProjectileOnly(MethodDefinition method, string call)
    {
        var calls = method.Body.Instructions.Where(i => i.Operand is MethodReference r && r.Name == call).ToList();
        return calls.Count == 1 && calls.All(c => {
            var gate = c.Previous; int loads = 0;
            while (gate != null && (gate.OpCode.Code.ToString().StartsWith("Ldarg") || gate.OpCode.Code.ToString().StartsWith("Ldloc"))) { gate = gate.Previous; loads++; }
            if (gate == null || loads < 3 || (gate.OpCode != OpCodes.Bne_Un && gate.OpCode != OpCodes.Bne_Un_S)) return false;
            var skip = (Instruction)gate.Operand;
            var type = gate.Previous; var field = type?.Previous; var ap = field?.Previous;
            return type?.OpCode == OpCodes.Ldc_I4_1 && field?.Operand is FieldReference f && f.Name == "_type" &&
                f.DeclaringType.FullName == "SeaPower.AmmunitionParameters" && ap != null && ap.OpCode == gate.Next.Next.OpCode &&
                Equals(ap.Operand, gate.Next.Next.Operand) && skip.Offset > c.Offset;
        });
    }

    // BuildPairs: ldloc <Aircraft shooter>; ldfld ObjectBase::_ai; ... callvirt DirectorPlanShot
    static bool AircraftShooter(MethodDefinition method, Instruction call)
    {
        var ai = call.Previous;
        while (ai != null && !(ai.Operand is FieldReference f && f.Name == "_ai" && f.DeclaringType.FullName == "SeaPower.ObjectBase")) ai = ai.Previous;
        var shooter = ai?.Previous;
        VariableDefinition local = shooter?.OpCode.Code switch {
            Code.Ldloc_0 => method.Body.Variables[0], Code.Ldloc_1 => method.Body.Variables[1], Code.Ldloc_2 => method.Body.Variables[2],
            Code.Ldloc_3 => method.Body.Variables[3], Code.Ldloc_S or Code.Ldloc => shooter.Operand as VariableDefinition, _ => null };
        return local?.VariableType.FullName == "SeaPower.Aircraft";
    }
}
