using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Runtime.Serialization;
using AnchorChain;
using HarmonyLib;
using Mono.Cecil;
using SeaPower;
using UnityEngine;

static partial class BetaApiTests
{
    // Osprey Mechanics 1.1.46 (7761f0a9) on 0.9.3-261123: the hover flight's one
    // distance-based fuel burn becomes the native rate-based burn at the
    // author's floored hover speed, and Osprey Deck Ops loads beside it.
    static void R6_OspreyMechanics(R6Context context)
    {
        string folder = Path.Combine(context.Workshop, "3806466625");
        string source = Path.Combine(folder, "OspreyMechanics.dll"), deck = Path.Combine(folder, "OspreyDeckOps.dll");
        string prepared = InteropPrepared(context, source, "7761f0a92dba79076da23663fcf546590851e0ee826b1488e00cd77d83bb494e",
            "OspreyMechanics", "OspreyMechanicsAudit");
        if (prepared == null) return;
        Check(typeof(Aircraft).GetMethod("UpdateFuelConsumption", InteropAll, null, new[] { typeof(float) }, null) == null,
            "On 261123 Aircraft has no distance-based UpdateFuelConsumption(float)");
        using (var author = ModuleDefinition.ReadModule(source, new ReaderParameters { AssemblyResolver = context.Resolver }))
        using (var adapted = ModuleDefinition.ReadModule(prepared, new ReaderParameters { AssemblyResolver = context.Resolver })) {
            var changed = InteropChangedMethods(author, adapted, "Osprey Mechanics");
            Check(changed.SequenceEqual(new[] { "HoverFlight::Physics" }), "Only HoverFlight.Physics differs from the author's (actual: " + string.Join(", ", changed) + ")");
            var body = adapted.GetType("OspreyRig.HoverFlight").Methods.Single(m => m.Name == "Physics").Body;
            var bridge = body.Instructions.Single(i => i.Operand is MethodReference c && c.Name == "OspreyHoverFuel");
            var reference = (MethodReference)bridge.Operand;
            Check(bridge.OpCode == Mono.Cecil.Cil.OpCodes.Call && reference.DeclaringType.FullName == typeof(BetaCompatibilityCalls).FullName &&
                bridge.Previous.OpCode == Mono.Cecil.Cil.OpCodes.Ldarg_0 &&
                (bridge.Previous.Previous.Operand as Mono.Cecil.Cil.VariableDefinition)?.Index == 9 &&
                bridge.Previous.Previous.Previous.OpCode == Mono.Cecil.Cil.OpCodes.Mul &&
                !body.Instructions.Any(i => i.Operand is MethodReference c && c.Name == "UpdateFuelConsumption"),
                "The hover burn passes distance, its sub-step and the physics to OspreyHoverFuel instead of UpdateFuelConsumption(float)");
            Check(body.Instructions.Count(i => i.Operand is MethodReference c && c.DeclaringType.FullName == typeof(BetaCompatibilityCalls).FullName) == 1,
                "The hover flight calls one SEST bridge");
        }
        // The deck code needs no rewrite: its own operands resolve, and its
        // library is now vouched for by the adapter, so it loads as written.
        var messages = new List<string>();
        byte[] deckBytes = File.ReadAllBytes(deck);
        string deckHash; using (var sha = System.Security.Cryptography.SHA256.Create()) deckHash = BitConverter.ToString(sha.ComputeHash(deckBytes)).Replace("-", "").ToLowerInvariant();
        Check(deckHash == "fcbe476223a1cc394911f0bd82451da810949f9791b73b2a3f0902641e3e406e", "Osprey Deck Ops fixture is the inspected author image");
        Check(BetaAssemblyPolicy.Prepare(deck, context.Native, context.Cache, messages.Add) == deck && messages.Count == 0,
            "Osprey Deck Ops loads unadapted beside its adapted library: " + string.Join(" | ", messages));
        using (var deckModule = ModuleDefinition.ReadModule(deck, new ReaderParameters { AssemblyResolver = context.Resolver })) {
            Check(deckModule.AssemblyReferences.Any(r => r.Name == "OspreyMechanics"), "Osprey Deck Ops references Osprey Mechanics by name");
            Check(InteropMissingOperands(deckModule) == 0, "Every Osprey Deck Ops native operand resolves on 261123");
        }
        var assembly = Assembly.LoadFile(prepared);
        Check(BetaAssemblyPolicy.OriginalLocation(assembly) == source, "Osprey Mechanics original asset provenance retained");
        Check(assembly.GetTypes().Length > 20, "Adapted Osprey Mechanics completes CLR type discovery on 261123");
        var physicsStep = assembly.GetType("OspreyRig.HoverFlight", true).GetMethod("Physics", InteropAll);
        RuntimeHelpers.PrepareMethod(physicsStep.MethodHandle);
        Check(true, "Rewritten HoverFlight.Physics compiles on 261123");
        OspreyHoverFuelFixture();
        Check(AppDomain.CurrentDomain.GetAssemblies().Count(a => a.GetName().Name == "OspreyMechanics") == 1,
            "One Osprey Mechanics assembly is loaded, the adapted image");
        InteropRejects(source, context, "OspreyMechanicsAdapter", "OspreyRig.HoverFlight", "Physics",
            method => method.Body.Instructions.Single(i => i.Operand is MethodReference c && c.Name == "UpdateFuelConsumption").Previous.Previous.Operand =
                method.Body.Variables[8],
            "Osprey hover burn over another distance");
        InteropRejects(source, context, "OspreyMechanicsAdapter", "OspreyRig.HoverFlight", "SafeSeaFloor",
            method => method.Body.GetILProcessor().InsertBefore(method.Body.Instructions.Last(), Mono.Cecil.Cil.Instruction.Create(Mono.Cecil.Cil.OpCodes.Call,
                method.Module.GetType("OspreyRig.HoverFlight").Methods.Single(m => m.Name == "Physics").Body.Instructions
                    .Select(i => i.Operand).OfType<MethodReference>().Single(c => c.Name == "UpdateFuelConsumption"))),
            "Osprey distance burn outside HoverFlight.Physics");
    }

    static readonly List<(float Rate, float Speed)> ospreyBurns = new List<(float, float)>();
    static int ospreyRefreshes;
    public static void OspreyRecordBurn(float kgPerSec, float speedMps) => ospreyBurns.Add((kgPerSec, speedMps));
    public static void OspreyRecordRefresh() => ospreyRefreshes++;
    // Both native bodies read GameTime, whose static constructor needs the
    // Unity player; the test records their arguments instead of running them.
    static IEnumerable<CodeInstruction> OspreyBurnBody(IEnumerable<CodeInstruction> instructions) => new[] {
        new CodeInstruction(System.Reflection.Emit.OpCodes.Ldarg_1), new CodeInstruction(System.Reflection.Emit.OpCodes.Ldarg_2),
        new CodeInstruction(System.Reflection.Emit.OpCodes.Call, typeof(BetaApiTests).GetMethod(nameof(OspreyRecordBurn), InteropAll)),
        new CodeInstruction(System.Reflection.Emit.OpCodes.Ret) };
    static IEnumerable<CodeInstruction> OspreyRefreshBody(IEnumerable<CodeInstruction> instructions) => new[] {
        new CodeInstruction(System.Reflection.Emit.OpCodes.Call, typeof(BetaApiTests).GetMethod(nameof(OspreyRecordRefresh), InteropAll)),
        new CodeInstruction(System.Reflection.Emit.OpCodes.Ret) };

    // OspreyHoverBurn (what OspreyHoverFuel runs with GameTime.fixedDeltaTime)
    // against game objects built without their Unity constructors.
    static void OspreyHoverFuelFixture()
    {
        InteropWithoutUnityProfiler();
        var wrapper = typeof(BetaCompatibilityCalls).GetMethod(nameof(BetaCompatibilityCalls.OspreyHoverFuel));
        var wrapperBody = PatchProcessor.GetOriginalInstructions(wrapper);
        Check(wrapperBody.Count(i => i.operand is MethodInfo m && m.DeclaringType == typeof(GameTime) && m.Name == "get_fixedDeltaTime") == 1 &&
            wrapperBody.Count(i => i.operand is MethodInfo m && m.Name == nameof(BetaCompatibilityCalls.OspreyHoverBurn)) == 1,
            "OspreyHoverFuel burns with the game's GameTime.fixedDeltaTime");
        var aircraft = (Aircraft)FormatterServices.GetUninitializedObject(typeof(Aircraft));
        var parameters = (AircraftParameters)FormatterServices.GetUninitializedObject(typeof(AircraftParameters));
        typeof(ObjectBase).GetField("_obp", InteropAll).SetValue(aircraft, parameters);
        var physics = (FixedWingFlightPhysics)FormatterServices.GetUninitializedObject(typeof(FixedWingFlightPhysics));
        typeof(MotionController).GetField("_poseCached", InteropAll).SetValue(physics, true);
        typeof(MotionController).GetField("_cachedPosition", InteropAll).SetValue(physics, new Vector3(0f, 9f, 0f));
        var perfField = typeof(FixedWingFlightPhysics).GetField("_perf", InteropAll);
        var perf = (AircraftPerfData)perfField.GetValue(physics);
        perf.FuelFlowCoef = 0.6f; perf.FuelShapeRef = 1f; perf.MaxDryThrust = 60000f; perf.MaxWetThrust = 60000f; perf.IdleThrust = 3000f;
        perf.EngineCount = 2; perf.Turboprop = true; perf.MaxPower = 4500f; perf.BypassRatio = 0f; perf.ReheatSfc = 0f;
        perfField.SetValue(physics, perf);
        typeof(FixedWingFlightPhysics).GetField("_physThrust", InteropAll).SetValue(physics, 20000f);
        var harmony = new Harmony("sest.beta-api-tests.osprey-fuel");
        try {
            harmony.Patch(typeof(Aircraft).GetMethod("BurnFuelAtRate", InteropAll), transpiler: new HarmonyMethod(typeof(BetaApiTests).GetMethod(nameof(OspreyBurnBody), InteropAll)));
            harmony.Patch(typeof(Aircraft).GetMethod("UpdateFuelConsumptionThrottled", InteropAll), transpiler: new HarmonyMethod(typeof(BetaApiTests).GetMethod(nameof(OspreyRefreshBody), InteropAll)));
            parameters._currentFuelMass = 0f;
            BetaCompatibilityCalls.OspreyHoverBurn(aircraft, 48.872334f * 0.05f, 0.05f, physics, 0.08f);
            Check(ospreyBurns.Count == 0 && ospreyRefreshes == 0, "No hover burn without fuel, as the native step");
            parameters._currentFuelMass = 1000f;
            BetaCompatibilityCalls.OspreyHoverBurn(aircraft, 1f, 0.05f, physics, 0f);
            Check(ospreyBurns.Count == 0 && ospreyRefreshes == 0, "No hover burn while the game step is zero (paused)");
            Exception missing = null;
            try { BetaCompatibilityCalls.OspreyHoverBurn(null, 1f, 0.05f, physics, 0.08f); } catch (NullReferenceException ex) { missing = ex; }
            Check(missing != null, "A missing aircraft fails as the author's callvirt did");
            // One 0.08 s game step, split by the author into 0.05 s and 0.03 s sub-steps,
            // at a hover speed below the author's 48.872334 m/s floor.
            float floor = Mathf.Max(20f, 48.8723335f);
            BetaCompatibilityCalls.OspreyHoverBurn(aircraft, floor * 0.05f, 0.05f, physics, 0.08f);
            BetaCompatibilityCalls.OspreyHoverBurn(aircraft, floor * 0.03f, 0.03f, physics, 0.08f);
            float expected = AircraftPerformance.FuelFlow(in perf, floor, 9f * 67.2000656f, 20000f);
            Check(ospreyBurns.Count == 2 && ospreyRefreshes == 2, "Each hover sub-step burns once and refreshes the throttled readout once");
            Check(ospreyBurns.All(b => Math.Abs(b.Speed - floor) < 0.001f), "The burn uses the author's floored hover speed (distance / sub-step)");
            float burned = ospreyBurns.Sum(b => b.Rate * 0.08f);
            Check(expected > 0f && Math.Abs(ospreyBurns[0].Rate - expected * 0.05f / 0.08f) < 1e-4f * expected &&
                Math.Abs(burned - expected * 0.08f) < 1e-4f * expected,
                "The two sub-steps burn the native fuel flow for the whole 0.08 s step, no more (" + burned + " kg against " + (expected * 0.08f) + " kg)");
        } finally {
            harmony.UnpatchSelf();
        }
    }
}
