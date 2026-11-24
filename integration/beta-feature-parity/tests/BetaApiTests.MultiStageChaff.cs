using System;
using System.IO;
using System.Linq;
using System.Reflection;
using AnchorChain;
using Mono.Cecil;
using SeaPower;
using UnityEngine;

static partial class BetaApiTests
{
    // Multi-Stage Missiles 1.7.18 (33a8841b) on 0.9.3-261123: the chaff
    // submunition drops its store to the retired _ammoInUse field, passes the
    // native cartridges default, and the author's payload validator asks for
    // the 261123 signature. The author's full startup validator chain runs.
    static void R6_MultiStageChaff(R6Context context)
    {
        string source = Path.Combine(context.Workshop, "3784474738", "MultiStageMissiles.dll");
        string prepared = ChaffPrepared(context, source, "33a8841b0884bc7effaa59700f3c852e151d1d9bf0e7263b4f3a22a07c9b98f3",
            "MultiStageMissiles", "MultiStageChaffAudit");
        if (prepared == null) return;
        var launch = typeof(ChaffCloud).GetMethod("launchChaffEffect", ChaffAll);
        Check(launch.GetParameters().Select(p => p.ParameterType).SequenceEqual(new[] { typeof(WeaponSystemChaff), typeof(GameObject), typeof(GameObject), typeof(int) }) &&
            launch.GetParameters()[3].IsOptional && Equals(launch.GetParameters()[3].DefaultValue, 1),
            "On 261123 launchChaffEffect takes an optional cartridges = 1");
        Check(typeof(ChaffCloud).GetMethod("launchChaffEffect", (BindingFlags)60, null, new[] { typeof(WeaponSystemChaff), typeof(GameObject), typeof(GameObject) }, null) == null,
            "The author's unadapted 3-argument lookup would fail on 261123 and switch the payloads off");
        const string Api = "MultiStageMissilesAnchorChain.SubmunitionPayloadApi";
        using (var author = ModuleDefinition.ReadModule(source, new ReaderParameters { AssemblyResolver = context.Resolver }))
        using (var adapted = ModuleDefinition.ReadModule(prepared, new ReaderParameters { AssemblyResolver = context.Resolver })) {
            var authorTypes = Types(author.Types).ToList(); var adaptedTypes = Types(adapted.Types).ToList();
            Check(authorTypes.Select(t => t.FullName).SequenceEqual(adaptedTypes.Select(t => t.FullName)), "Adapted Multi-Stage image has the author's types");
            var changed = new System.Collections.Generic.List<string>(); int compared = 0;
            for (int t = 0; t < authorTypes.Count; t++) for (int m = 0; m < authorTypes[t].Methods.Count; m++) {
                var written = authorTypes[t].Methods[m]; var actual = adaptedTypes[t].Methods[m];
                Check(written.FullName == actual.FullName, "Adapted Multi-Stage method order is the author's: " + written.FullName);
                if (!written.HasBody) continue;
                compared++;
                Check(!actual.Body.Instructions.Any(i => i.Operand is FieldReference f && f.Name == "_ammoInUse"), "Adapted Multi-Stage no longer names _ammoInUse: " + actual.FullName);
                if (!TopoInstructions(written).SequenceEqual(TopoInstructions(actual))) changed.Add(actual.DeclaringType.Name + "::" + actual.Name);
            }
            changed.Sort(StringComparer.Ordinal);
            var locationMethods = Types(adapted.Types).SelectMany(t => t.Methods).Where(m => m.HasBody && m.Body.Instructions.Any(i =>
                i.Operand is MethodReference c && c.Name == "OriginalLocation" && c.DeclaringType.FullName == typeof(BetaAssemblyPolicy).FullName))
                .Select(m => m.DeclaringType.Name + "::" + m.Name);
            var expectedChanged = new[] { "SubmunitionPayloadApi::LaunchChaff", "SubmunitionPayloadApi::Validate" }.Concat(locationMethods)
                .Distinct().OrderBy(x => x, StringComparer.Ordinal).ToList();
            Check(changed.SequenceEqual(expectedChanged), "Of " + compared + " Multi-Stage bodies only LaunchChaff, Validate and the location reads differ (actual: " + string.Join(", ", changed) + ")");
            var body = adapted.GetType(Api).Methods.Single(m => m.Name == "LaunchChaff").Body.Instructions;
            var ammo = body.Single(i => i.OpCode == Mono.Cecil.Cil.OpCodes.Newobj && i.Operand is MethodReference c && c.DeclaringType.FullName == "SeaPower.Ammunition");
            Check(ammo.Next.OpCode == Mono.Cecil.Cil.OpCodes.Pop && ammo.Next.Next.OpCode == Mono.Cecil.Cil.OpCodes.Pop,
                "The throwaway chaff system's ammunition store is discarded (pop; pop)");
            var call = body.Single(i => i.Operand is MethodReference c && c.Name == "launchChaffEffect");
            Check(call.OpCode == Mono.Cecil.Cil.OpCodes.Callvirt && ((MethodReference)call.Operand).Parameters.Count == 4 &&
                call.Previous.OpCode == Mono.Cecil.Cil.OpCodes.Ldc_I4 && Equals(call.Previous.Operand, 1),
                "The chaff cloud launch passes the native default cartridges = 1");
            var validate = adapted.GetType(Api).Methods.Single(m => m.Name == "Validate").Body.Instructions;
            int name = validate.IndexOf(validate.Single(i => i.OpCode == Mono.Cecil.Cil.OpCodes.Ldstr && Equals(i.Operand, "launchChaffEffect")));
            Check(validate[name + 1].OpCode == Mono.Cecil.Cil.OpCodes.Ldc_I4_4 && validate.Skip(name).Take(30).Count(i => i.OpCode == Mono.Cecil.Cil.OpCodes.Ldtoken &&
                (i.Operand as TypeReference)?.FullName == "System.Int32") == 1,
                "The author's payload validator asks RequireVoid for the 4-argument launchChaffEffect");
        }
        var assembly = Assembly.LoadFile(prepared);
        Check(assembly.GetTypes().Length > 50, "Adapted Multi-Stage Missiles completes CLR type discovery on 261123");
        Check(BetaAssemblyPolicy.OriginalLocation(assembly) == source, "Multi-Stage Missiles original asset provenance retained");
        var api = assembly.GetType(Api, true);
        foreach (string name in new[] { "LaunchChaff", "Validate" }) {
            System.Runtime.CompilerServices.RuntimeHelpers.PrepareMethod(api.GetMethod(name, ChaffAll).MethodHandle);
            Check(true, "Rewritten Multi-Stage method compiles on 261123: " + name);
        }
        // The author's own startup chain (MultiStageMissilesMod.InitializeWhenModEnabled,
        // then SubmunitionPayloadApi.Install), without Harmony patching.
        foreach (string validator in new[] { "SeaPowerModSupport.FileApi", "SeaPowerModSupport.NativeLaunchState",
            "MultiStageMissilesAnchorChain.SeaPowerTimeCompatibility", "MultiStageMissilesAnchorChain.ThermalApi",
            "MultiStageMissilesAnchorChain.SubmunitionApi", "MultiStageMissilesAnchorChain.SubmunitionImpactDiagnostics",
            "MultiStageMissilesAnchorChain.ImpactSpeedEffects", "MultiStageMissilesAnchorChain.PropulsionApi", Api }) {
            CurrentInvoke(assembly.GetType(validator, true), "Validate");
            Check(true, "Multi-Stage author startup validator passes on 261123: " + validator + ".Validate");
        }
        Check(api.GetField("ChaffFactory", ChaffAll).GetValue(null) != null && api.GetField("TorpedoMachine", ChaffAll).GetValue(null) != null &&
            api.GetField("TorpedoDrop", ChaffAll).GetValue(null) != null,
            "The author's payload validator bound the chaff factory and torpedo-drop state on 261123");
        ChaffRejects(source, context, "MultiStageChaffAdapter", Api, "LaunchChaff",
            method => method.Body.Instructions.Single(i => i.Operand is FieldReference f && f.Name == "_ammoInUse").Previous.OpCode = Mono.Cecil.Cil.OpCodes.Ldnull,
            "Multi-Stage chaff store without its new Ammunition");
        ChaffRejects(source, context, "MultiStageChaffAdapter", Api, "Validate",
            method => method.Body.Instructions.Single(i => i.Offset == 0x00df).Operand = "launchChaffEffects",
            "Multi-Stage payload validator naming another member");
        ChaffRejects(source, context, "MultiStageChaffAdapter", Api, "Install",
            method => method.Body.GetILProcessor().InsertBefore(method.Body.Instructions.Last(), Mono.Cecil.Cil.Instruction.Create(Mono.Cecil.Cil.OpCodes.Ldfld,
                method.Module.GetMemberReferences().OfType<FieldReference>().First(f => f.Name == "_ammoInUse"))),
            "Multi-Stage _ammoInUse access outside the inspected chaff launch");
    }
}
