using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Runtime.Serialization;
using AnchorChain;
using Mono.Cecil;
using SeaPower;
using UnityEngine;

static partial class BetaApiTests
{
    // Z-21 Gun and EOTS Synchronization (6de88b8b) on 0.9.3-261123: the gun's
    // container object is found through WeaponSystem._vwp again, so the EOTS
    // follows the gun while the helicopter aligns to fire.
    static void R6_Z21GunMoveFire(R6Context context)
    {
        string source = Path.Combine(context.Workshop, "3774746803", "Z21GunMoveFire.dll");
        string prepared = InteropPrepared(context, source, "6de88b8b12d469a7b6d6ab3f638431a0106db0f9cd3f330e15724cfbca35a3ae",
            "Z21GunMoveFire", "Z21GunMoveFireAudit");
        if (prepared == null) return;
        var container = typeof(WeaponParameters).GetField("_containerBaseObject", InteropAll);
        Check(HarmonyLib.AccessTools.Field(typeof(WeaponSystem), "_containerBaseObject") == null && container != null &&
            container.FieldType == typeof(GameObject) && typeof(WeaponSystem).GetField("_vwp", InteropAll)?.FieldType == typeof(WeaponParameters),
            "On 261123 the container object is WeaponParameters._containerBaseObject, reached through WeaponSystem._vwp");
        using (var author = ModuleDefinition.ReadModule(source, new ReaderParameters { AssemblyResolver = context.Resolver }))
        using (var adapted = ModuleDefinition.ReadModule(prepared, new ReaderParameters { AssemblyResolver = context.Resolver })) {
            var changed = InteropChangedMethods(author, adapted, "Z-21");
            Check(changed.SequenceEqual(new[] { "Mod::.cctor", "Mod::SyncOpticToGun" }), "Only Mod's static constructor and one SyncOpticToGun differ (actual: " + string.Join(", ", changed) + ")");
            var mod = adapted.GetType("Z21GunMoveFire.Mod");
            var lookup = mod.Methods.Single(m => m.Name == ".cctor").Body.Instructions.Single(i => i.OpCode == Mono.Cecil.Cil.OpCodes.Ldstr && Equals(i.Operand, "_containerBaseObject"));
            Check((lookup.Previous.Previous.Operand as TypeReference)?.FullName == "SeaPower.WeaponParameters", "The container lookup names WeaponParameters");
            var sync = mod.Methods.Single(m => m.Name == "SyncOpticToGun" && m.Parameters[1].ParameterType.FullName == "SeaPower.AlignUnitToTarget").Body.Instructions;
            var read = sync.Single(i => i.Operand is MethodReference c && c.Name == "WeaponContainerObject");
            Check(read.OpCode == Mono.Cecil.Cil.OpCodes.Call && ((MethodReference)read.Operand).DeclaringType.FullName == typeof(BetaCompatibilityCalls).FullName &&
                read.Previous.OpCode == Mono.Cecil.Cil.OpCodes.Ldloc_0 && read.Next.OpCode == Mono.Cecil.Cil.OpCodes.Isinst &&
                !sync.Any(i => i.Operand is MethodReference c && c.Name == "GetValue" && i.Previous.OpCode == Mono.Cecil.Cil.OpCodes.Ldloc_0),
                "The one container read goes through WeaponContainerObject");
        }
        var assembly = Assembly.LoadFile(prepared);
        Check(BetaAssemblyPolicy.OriginalLocation(assembly) == source, "Z-21 original asset provenance retained");
        var type = assembly.GetType("Z21GunMoveFire.Mod", true);
        RuntimeHelpers.RunClassConstructor(type.TypeHandle);
        object Static(string name) => type.GetField(name, InteropAll).GetValue(null);
        Check(Equals(Static("ContainerBaseObject"), container), "The author's container lookup now binds WeaponParameters._containerBaseObject (no HarmonyX warning)");
        foreach (string name in new[] { "StateHelicopter", "AlignmentWeapon", "ObjectIniName", "SystemBaseObject", "SystemMountObject",
            "GoingIntoFiringRange", "AlignmentTarget", "CurrentMaxLaunchRange" })
            Check(Static(name) != null, "The author's other Z-21 lookup binds on 261123: " + name);
        var syncMethod = type.GetMethod("SyncOpticToGun", InteropAll, null, new[] { typeof(Helicopter), typeof(AlignUnitToTarget) }, null);
        RuntimeHelpers.PrepareMethod(syncMethod.MethodHandle);
        Check(true, "Rewritten Z-21 SyncOpticToGun compiles on 261123");
        // The bridge against game objects built without their Unity constructors.
        InteropWithoutUnityProfiler();
        var system = (WeaponSystem)FormatterServices.GetUninitializedObject(typeof(WeaponSystem));
        Check(BetaCompatibilityCalls.WeaponContainerObject(container, null) == null && BetaCompatibilityCalls.WeaponContainerObject(container, new object()) == null &&
            BetaCompatibilityCalls.WeaponContainerObject(container, system) == null, "No system, another object or a system without parameters gives no container");
        var parameters = (WeaponParameters)FormatterServices.GetUninitializedObject(typeof(WeaponParameters));
        var gun = (GameObject)FormatterServices.GetUninitializedObject(typeof(GameObject));
        system._vwp = parameters; parameters._containerBaseObject = gun;
        Check(ReferenceEquals(BetaCompatibilityCalls.WeaponContainerObject(container, system), gun), "WeaponContainerObject returns the system's _vwp._containerBaseObject");
        // Running the adapted SyncOpticToGun itself needs UnityEngine.Object's
        // static constructor (its null checks), which needs the Unity player:
        // the EOTS-follows-gun result is the PC check (pla_z21 firing while aligning).
        InteropRejects(source, context, "Z21GunMoveFireAdapter", "Z21GunMoveFire.Mod", ".cctor",
            method => method.Body.Instructions.Single(i => i.OpCode == Mono.Cecil.Cil.OpCodes.Ldstr && Equals(i.Operand, "_containerBaseObject")).Previous.Previous.Operand =
                method.Module.GetType("Z21GunMoveFire.Mod").Methods.Single(m => m.Name == ".cctor").Body.Instructions
                    .First(i => i.OpCode == Mono.Cecil.Cil.OpCodes.Ldtoken && (i.Operand as TypeReference)?.FullName == "SeaPower.BaseSystem").Operand,
            "Z-21 container lookup on another type");
        InteropRejects(source, context, "Z21GunMoveFireAdapter", "Z21GunMoveFire.Mod", "SyncOpticToGun",
            method => method.Body.Instructions.Single(i => i.OpCode == Mono.Cecil.Cil.OpCodes.Ldloc_0 && i.Previous.Operand is FieldReference f && f.Name == "ContainerBaseObject").OpCode =
                Mono.Cecil.Cil.OpCodes.Ldarg_1,
            "Z-21 container read of another object");
    }
}
