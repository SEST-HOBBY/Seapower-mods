// R6: TestRange 0.2.3 (euromod.test-range, Workshop 3784474738) as captured
// on 3 Nov 2026. On beta Build 261026 the author's own validator stops the
// plugin: ECM.CombinedJamUnit(IEnumerable<ECM>, ...) is gone (the beta sums
// ECM.StandoffNoiseFactor per jammer in RadarCalculator.ApplyJammingToDetectionRange
// and passes the total in as a double), and WeaponSystemLauncher.launch now
// returns bool. Behind those, Panel.EnsureCatalog calls the removed
// FileManager.GetFiles(string, string), and the GetSensorRange postfix reads
// EstimatedSensorRangeData.SensorData encoded as a class, which the beta made
// a struct. The author's ExtendedGuidance gate is deliberately left as it is.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    internal const string TestRangeHash = "672e34d8c946b9ca7086d10462d2b7c7be3f96260bd5ee08d2851020a5810491";
    private const string TestRangeAudit = "jam-hook=1, jam-legacy=1, jam-standoff=1, launch-blocked-result=1, launch-result=1, locations=2, scan-files=1, sensor-data=1";
    private const string TestRangeTypeFromHandle = "call System.Type System.Type::GetTypeFromHandle(System.RuntimeTypeHandle)";
    private const string TestRangeAdd = "call System.Void TestRange.CountermeasureApi::Add(System.Type,System.String,System.Type,System.Boolean,System.String,System.Boolean,System.Boolean,System.Type[])";
    private const string TestRangeConcat = "call System.Collections.Generic.IEnumerable`1<!!0> System.Linq.Enumerable::Concat<System.Type>(System.Collections.Generic.IEnumerable`1<!!0>,System.Collections.Generic.IEnumerable`1<!!0>)";
    private const string TestRangeToArray = "call !!0[] System.Linq.Enumerable::ToArray<System.Type>(System.Collections.Generic.IEnumerable`1<!!0>)";
    private const string TestRangeBlocked = "call System.Boolean TestRange.CountermeasurePolicy::Blocked(System.Object,System.Int32)";
    private const string TestRangeHomeObject = "ldfld SeaPower.ObjectBase SeaPower.ECM::_homeObject";
    private const string TestRangeEnumerableEcm = "System.Collections.Generic.IEnumerable`1<SeaPower.ECM>";
    private static readonly string[] TestRangeJamUnitTypes = { "System.Single", "UnityEngine.Vector3", "SeaPower.Globals/Frequency",
        "System.Single", "System.Single", "System.Single", "SeaPower.Crew", "System.Single" };

    private static ImageAdapter TestRangeAdapter() => new ImageAdapter {
        Name = "TestRange",
        Hashes = new[] { TestRangeHash },
        RequireNative = TestRangeRequireNative,
        RewriteMethod = TestRangeRewriteMethod,
        Finish = TestRangeFinish,
        ExpectedAudit = TestRangeAudit,
    };

    // ---- Native shapes the rewrites and bridges rely on (beta 3005bc6d).
    private static void TestRangeRequireNative(ModuleDefinition native)
    {
        static void Need(bool ok, string what) { if (!ok) throw new InvalidOperationException("Inspected beta " + what + " changed"); }
        TypeDefinition Type(string name) { var type = native.GetType(name); Need(type != null, name); return type; }

        var ecm = Type("SeaPower.ECM");
        // The per-jammer support-noise term: the new hook point for the author's jammer filter.
        var standoff = ecm.Methods.Where(m => m.Name == "StandoffNoiseFactor").ToList();
        Need(standoff.Count == 1 && standoff[0].HasThis && !standoff[0].IsVirtual && standoff[0].IsPublic && standoff[0].HasBody &&
            standoff[0].ReturnType.FullName == "System.Double" &&
            TestRangeParameters(standoff[0], "UnityEngine.Vector3", "SeaPower.Globals/Frequency", "System.Single") &&
            standoff[0].Parameters.Select(p => p.Name).SequenceEqual(new[] { "ownPosition", "frequency", "jamResistance" }) &&
            standoff[0].Body.CodeSize == 160, "ECM.StandoffNoiseFactor");
        // Only the pre-summed CombinedJamUnit remains; no jammer list exists to filter.
        var combined = ecm.Methods.Where(m => m.Name == "CombinedJamUnit").ToList();
        Need(combined.Count == 1 && combined[0].IsStatic && combined[0].ReturnType.FullName == "System.Single" &&
            TestRangeParameters(combined[0], "System.Double", "SeaPower.ObjectBase", "System.Single", "SeaPower.Globals/Frequency",
                "System.Single", "System.Single", "System.Single", "SeaPower.Crew", "System.Single") &&
            combined[0].Parameters[0].Name == "supportNoiseFactor", "ECM.CombinedJamUnit");
        var jamUnit = ecm.Methods.Where(m => m.Name == "JamUnit").ToList();
        Need(jamUnit.Count == 1 && jamUnit[0].HasThis && jamUnit[0].ReturnType.FullName == "System.Single" &&
            TestRangeParameters(jamUnit[0], TestRangeJamUnitTypes) &&
            jamUnit[0].Body.Instructions.Count(i => TestRangeCalls(i, standoff[0])) == 1, "ECM.JamUnit");
        // The author's second registration is reached only when this exists.
        Need(ecm.Methods.Count(m => m.Name == "SelfScreenNoisePower" && m.IsStatic && m.ReturnType.FullName == "System.Single" &&
            TestRangeParameters(m, "SeaPower.ObjectBase", "SeaPower.Globals/Frequency", "System.Single")) == 1, "ECM.SelfScreenNoisePower");
        Need(ecm.Fields.Count(f => f.Name == "_homeObject" && !f.IsStatic && f.FieldType.FullName == "SeaPower.ObjectBase") == 1, "ECM._homeObject");

        // The support sum: one StandoffNoiseFactor term per jammer, added into the
        // double local that is CombinedJamUnit's first argument.
        var apply = Type("SeaPower.RadarCalculator").Methods.Where(m => m.Name == "ApplyJammingToDetectionRange").ToList();
        Need(apply.Count == 1 && apply[0].IsStatic && TestRangeParameters(apply[0], "System.Single", "System.Single", "UnityEngine.Vector3",
            "SeaPower.Globals/Frequency", "System.Single", "System.Single", "System.Collections.Generic.List`1<SeaPower.SensorSystemECM>",
            "SeaPower.Crew", "System.Single", "SeaPower.ObjectBase", "SeaPower.ObjectBase", "System.Boolean"), "RadarCalculator.ApplyJammingToDetectionRange");
        var applyIl = apply[0].Body.Instructions;
        var terms = applyIl.Where(i => TestRangeCalls(i, standoff[0])).ToList();
        var sums = applyIl.Where(i => TestRangeCalls(i, combined[0])).ToList();
        Need(terms.Count == 1 && sums.Count == 1 && terms[0].OpCode == OpCodes.Callvirt && terms[0].Next.OpCode == OpCodes.Add &&
            terms[0].Next.Next.OpCode == OpCodes.Stloc_0 && apply[0].Body.Variables[0].VariableType.FullName == "System.Double" &&
            TestRangeBack(sums[0], 9)?.OpCode == OpCodes.Ldloc_0, "RadarCalculator.ApplyJammingToDetectionRange support sum");

        // launch() reports success; one OnUpdate caller branches on it, two discard it.
        var launcher = Type("SeaPower.WeaponSystemLauncher");
        var launch = launcher.Methods.Where(m => m.Name == "launch").ToList();
        Need(launch.Count == 1 && launch[0].HasThis && launch[0].ReturnType.FullName == "System.Boolean" &&
            TestRangeParameters(launch[0], "System.Int32", "SeaPower.ObjectBase", "UnityEngine.Vector3", "UnityEngine.Vector3", "System.Single"),
            "WeaponSystemLauncher.launch");
        var update = launcher.Methods.Single(m => m.Name == "OnUpdate" && m.Parameters.Count == 0);
        var launches = update.Body.Instructions.Where(i => TestRangeCalls(i, launch[0])).ToList();
        Need(launches.Count == 3 && launches.Count(i => i.Next.OpCode == OpCodes.Pop) == 2 &&
            launches.Count(i => i.Next.OpCode == OpCodes.Brtrue || i.Next.OpCode == OpCodes.Brtrue_S) == 1, "WeaponSystemLauncher.OnUpdate launch result use");
        var hardpoint = Type("SeaPower.WeaponSystemHardpoint").Methods.Where(m => m.Name == "launch").ToList();
        Need(hardpoint.Count == 1 && hardpoint[0].ReturnType.FullName == "System.Void" &&
            TestRangeParameters(hardpoint[0], "SeaPower.ObjectBase", "UnityEngine.Vector3", "UnityEngine.Vector3", "UnityEngine.Vector3"),
            "WeaponSystemHardpoint.launch");

        // The layer-aware file scan; kinds defaults to LayerKind.All.
        var files = Type("SeaPower.FileManager").Methods.Where(m => m.Name == "GetFiles" && m.HasThis).ToList();
        Need(!files.Any(m => TestRangeParameters(m, "System.String", "System.String")), "FileManager.GetFiles(string, string) removal");
        var scan = files.Where(m => TestRangeParameters(m, "System.String", "System.String", "SeaPower.LayerKind")).ToList();
        Need(scan.Count == 1 && scan[0].ReturnType.FullName == "System.Collections.Generic.List`1<System.String>" &&
            scan[0].Parameters[2].Name == "kinds" && scan[0].Parameters[2].IsOptional && scan[0].Parameters[2].HasConstant &&
            Equals(scan[0].Parameters[2].Constant, 31), "FileManager.GetFiles(string, string, LayerKind)");
        Need(Type("SeaPower.LayerKind").Fields.Count(f => f.Name == "All" && f.HasConstant && Equals(f.Constant, 31)) == 1, "LayerKind.All");

        // SensorDistanceData is now a value type; Distance is unchanged.
        var estimate = Type("SeaPower.ObjectBase/EstimatedSensorRangeData");
        var data = estimate.Fields.Where(f => f.Name == "SensorData").ToList();
        Need(estimate.IsValueType && data.Count == 1 && data[0].FieldType.FullName == "SeaPower.SensorSystem/SensorDistanceData" &&
            data[0].FieldType.Resolve()?.IsValueType == true, "ObjectBase.EstimatedSensorRangeData.SensorData");
        Need(Type("SeaPower.SensorSystem/SensorDistanceData").Fields.Count(f => f.Name == "Distance" && !f.IsStatic && f.FieldType.FullName == "System.Single") == 1,
            "SensorSystem.SensorDistanceData.Distance");
    }

    // ---- Rewrites of the pinned author image. Offsets are the author's, read
    // before the shared loop expands any branch.
    private static bool TestRangeRewriteMethod(AdapterScope scope, TypeDefinition type, MethodDefinition method)
    {
        switch (type.FullName + "::" + method.Name) {
            case "TestRange.CountermeasureApi::Validate":
                TestRangeShape(method, true, "System.Void");
                TestRangeJamRegistrations(scope, method);
                return false;
            case "TestRange.CountermeasureHooks::Combined":
                TestRangeShape(method, true, "System.Void", TestRangeEnumerableEcm + "&");
                TestRangeCombinedHook(scope, type, method);
                return true;
            case "TestRange.Api::Validate":
                TestRangeShape(method, true, "System.Void");
                TestRangeLaunchRequirement(scope, method);
                return false;
            case "TestRange.DefenseHooks::Launch":
                TestRangeShape(method, true, "System.Boolean", "SeaPower.WeaponSystemLauncher", "SeaPower.ObjectBase");
                TestRangeBlockedLaunch(scope, method);
                return false;
            case "TestRange.Panel::EnsureCatalog":
                TestRangeShape(method, true, "System.Void");
                TestRangeCatalogScan(scope, method);
                return false;
            case "TestRange.ResultHooks/<>c__DisplayClass13_0::<Sensor>b__0":
                TestRangeShape(method, false, "System.Void");
                TestRangeSensorData(scope, method);
                return false;
        }
        return false;
    }

    // R1 jam-standoff and R2 jam-legacy: CountermeasureApi.Validate's two
    // registrations of the removed CombinedJamUnit overloads.
    private static void TestRangeJamRegistrations(AdapterScope scope, MethodDefinition method)
    {
        TestRangeExpect(method, 0x0107, "stloc.0");
        Instruction[] standoff = TestRangeExpect(method, 0x012f,
            "ldtoken SeaPower.ECM", TestRangeTypeFromHandle, "ldstr CombinedJamUnit", "ldtoken System.Single", TestRangeTypeFromHandle,
            "ldc.i4.1", "ldstr Combined", "ldc.i4.0", "ldc.i4.0", "ldc.i4.1", "newarr System.Type", "dup", "ldc.i4.0",
            "ldtoken " + TestRangeEnumerableEcm, TestRangeTypeFromHandle, "stelem.ref", "ldloc.0", TestRangeConcat, TestRangeToArray, TestRangeAdd);
        Instruction[] legacy = TestRangeExpect(method, 0x01ad,
            "ldtoken SeaPower.ECM", TestRangeTypeFromHandle, "ldstr CombinedJamUnit", "ldtoken System.Single", TestRangeTypeFromHandle,
            "ldc.i4.1", "ldstr Combined", "ldc.i4.0", "ldc.i4.0", "ldc.i4.2", "newarr System.Type", "dup", "ldc.i4.0",
            "ldtoken " + TestRangeEnumerableEcm, TestRangeTypeFromHandle, "stelem.ref", "dup", "ldc.i4.1", "ldtoken SeaPower.ObjectBase",
            TestRangeTypeFromHandle, "stelem.ref", "ldloc.0", TestRangeConcat, TestRangeToArray, TestRangeAdd);
        if (method.Body.Instructions.Count(i => i.OpCode == OpCodes.Ldstr && Equals(i.Operand, "CombinedJamUnit")) != 2)
            throw new InvalidOperationException("Inspected TestRange combined-jamming registrations changed");
        // Site 1: Add(typeof(ECM), "StandoffNoiseFactor", typeof(double), false, "Combined", false, false,
        // TestRangeStandoffArgs(new[] { typeof(IEnumerable<ECM>) }, jamUnitArgs).ToArray()).
        standoff[2].Operand = "StandoffNoiseFactor";
        standoff[3].Operand = scope.Module.TypeSystem.Double;
        standoff[5].OpCode = OpCodes.Ldc_I4_0;
        standoff[17].OpCode = OpCodes.Call; standoff[17].Operand = scope.Bridge(nameof(BetaCompatibilityCalls.TestRangeStandoffArgs));
        scope.Count("jam-standoff");
        // Site 2: the removed 10-parameter overload is checked, not registered.
        legacy[24].OpCode = OpCodes.Call; legacy[24].Operand = scope.Bridge(nameof(BetaCompatibilityCalls.TestRangeLegacyCombined));
        scope.Count("jam-legacy");
    }

    // R3 jam-hook: CountermeasureHooks.Combined becomes a StandoffNoiseFactor
    // prefix applying the author's per-jammer predicate <>c::<Combined>b__4_0.
    private static void TestRangeCombinedHook(AdapterScope scope, TypeDefinition type, MethodDefinition method)
    {
        if (method.Parameters[0].Name != "__0" || method.Body.CodeSize != 54 || method.Body.Variables.Count != 0 || method.Body.ExceptionHandlers.Count != 0)
            throw new InvalidOperationException("Inspected TestRange Combined hook changed");
        var original = TestRangeExpect(method, 0x0000,
            "volatile.", "ldsfld System.Boolean modreq(System.Runtime.CompilerServices.IsVolatile) TestRange.CountermeasurePolicy::JammingRestricted",
            "brfalse.s IL_0035", "ldarg.0", "ldind.ref", "brfalse.s IL_0035", "ldarg.0", "ldarg.0", "ldind.ref",
            "ldsfld System.Func`2<SeaPower.ECM,System.Boolean> TestRange.CountermeasureHooks/<>c::<>9__4_0", "dup", "brtrue.s IL_002f", "pop",
            "ldsfld TestRange.CountermeasureHooks/<>c TestRange.CountermeasureHooks/<>c::<>9",
            "ldftn System.Boolean TestRange.CountermeasureHooks/<>c::<Combined>b__4_0(SeaPower.ECM)",
            "newobj System.Void System.Func`2<SeaPower.ECM,System.Boolean>::.ctor(System.Object,System.IntPtr)", "dup",
            "stsfld System.Func`2<SeaPower.ECM,System.Boolean> TestRange.CountermeasureHooks/<>c::<>9__4_0",
            "call System.Collections.Generic.IEnumerable`1<!!0> System.Linq.Enumerable::Where<SeaPower.ECM>(System.Collections.Generic.IEnumerable`1<!!0>,System.Func`2<!!0,System.Boolean>)",
            "stind.ref", "ret");
        if (method.Body.Instructions.Count != original.Length || type.Methods.Count(m => m.Name == "Combined") != 1)
            throw new InvalidOperationException("Inspected TestRange Combined hook changed");
        var lambda = type.NestedTypes.Single(t => t.Name == "<>c").Methods.Single(m => m.Name == "<Combined>b__4_0");
        var predicate = TestRangeExpect(lambda, 0x0000, "ldarg.1", "brfalse.s IL_0013", "ldarg.1", TestRangeHomeObject, "ldc.i4.2",
            TestRangeBlocked, "ldc.i4.0", "ceq", "ret", "ldc.i4.1", "ret");
        if (lambda.Body.Instructions.Count != predicate.Length)
            throw new InvalidOperationException("Inspected TestRange Combined predicate changed");
        var restricted = (FieldReference)original[1].Operand;
        var home = (FieldReference)predicate[3].Operand;
        var blocked = (MethodReference)predicate[5].Operand;

        // bool Combined(ECM __instance, ref double __result): a blocked unit's
        // jammer contributes 0 to beta's support sum, which equals stable
        // dropping it from CombinedJamUnit's jammer list before the Sum.
        method.ReturnType = scope.Module.TypeSystem.Boolean;
        method.Parameters.Clear();
        method.Parameters.Add(new ParameterDefinition("__instance", Mono.Cecil.ParameterAttributes.None, home.DeclaringType));
        method.Parameters.Add(new ParameterDefinition("__result", Mono.Cecil.ParameterAttributes.None, new ByReferenceType(scope.Module.TypeSystem.Double)));
        method.Body.Instructions.Clear();
        var il = method.Body.GetILProcessor();
        var run = Instruction.Create(OpCodes.Ldc_I4_1);
        il.Append(Instruction.Create(OpCodes.Volatile));
        il.Append(Instruction.Create(OpCodes.Ldsfld, restricted));
        il.Append(Instruction.Create(OpCodes.Brfalse, run));
        il.Append(Instruction.Create(OpCodes.Ldarg_0));
        il.Append(Instruction.Create(OpCodes.Ldfld, home));
        il.Append(Instruction.Create(OpCodes.Ldc_I4_2));
        il.Append(Instruction.Create(OpCodes.Call, blocked));
        il.Append(Instruction.Create(OpCodes.Brfalse, run));
        il.Append(Instruction.Create(OpCodes.Ldarg_1));
        il.Append(Instruction.Create(OpCodes.Ldc_R8, 0.0));
        il.Append(Instruction.Create(OpCodes.Stind_R8));
        il.Append(Instruction.Create(OpCodes.Ldc_I4_0));
        il.Append(Instruction.Create(OpCodes.Ret));
        il.Append(run);
        il.Append(Instruction.Create(OpCodes.Ret));
        scope.Count("jam-hook");
    }

    // R4 launch-result: Api.Validate requires WeaponSystemLauncher.launch to
    // return bool, as it does on the beta. The Hardpoint launch stays void.
    private static void TestRangeLaunchRequirement(AdapterScope scope, MethodDefinition method)
    {
        var site = TestRangeExpect(method, 0x0100,
            "ldtoken SeaPower.WeaponSystemLauncher", TestRangeTypeFromHandle, "ldstr launch", "ldtoken System.Void", TestRangeTypeFromHandle,
            "ldc.i4.5", "newarr System.Type",
            "dup", "ldc.i4.0", "ldtoken System.Int32", TestRangeTypeFromHandle, "stelem.ref",
            "dup", "ldc.i4.1", "ldtoken SeaPower.ObjectBase", TestRangeTypeFromHandle, "stelem.ref",
            "dup", "ldc.i4.2", "ldtoken UnityEngine.Vector3", TestRangeTypeFromHandle, "stelem.ref",
            "dup", "ldc.i4.3", "ldtoken UnityEngine.Vector3", TestRangeTypeFromHandle, "stelem.ref",
            "dup", "ldc.i4.4", "ldtoken System.Single", TestRangeTypeFromHandle, "stelem.ref",
            "call System.Reflection.MethodInfo TestRange.Api::Require(System.Type,System.String,System.Type,System.Type[])",
            "stsfld System.Reflection.MethodInfo TestRange.Api::Launch",
            "ldtoken SeaPower.WeaponSystemHardpoint", TestRangeTypeFromHandle, "ldstr launch", "ldtoken System.Void");
        if (method.Body.Instructions.Count(i => i.OpCode == OpCodes.Ldstr && Equals(i.Operand, "launch")) != 2)
            throw new InvalidOperationException("Inspected TestRange launch requirement changed");
        site[3].Operand = scope.Module.TypeSystem.Boolean;
        scope.Count("launch-result");
    }

    // R5 launch-blocked-result: when DefenseHooks.Launch blocks a shot it now
    // reports success, so beta's OnUpdate follows stable's post-launch path
    // instead of its new failed-launch branch. Hardpoint shares the author's
    // body bytes and is left as it is.
    private static void TestRangeBlockedLaunch(AdapterScope scope, MethodDefinition method)
    {
        if (method.Parameters[0].Name != "__instance" || method.Parameters[1].Name != "__1" || method.Body.Variables.Count != 0 || method.Body.ExceptionHandlers.Count != 0)
            throw new InvalidOperationException("Inspected TestRange launch hook changed");
        var body = TestRangeExpect(method, 0x0000, "ldarg.0", "ldfld SeaPower.ObjectBase SeaPower.BaseSystem::_baseObject", "ldarg.1", "ldarg.0",
            "ldfld SeaPower.Ammunition SeaPower.WeaponSystem::_ammoForEngage",
            "call System.String TestRange.DefenseHooks::Id(SeaPower.Ammunition)",
            "call System.Boolean TestRange.DefensePolicy::Allows(System.Object,System.Object,System.String)", "ret");
        if (method.Body.Instructions.Count != body.Length) throw new InvalidOperationException("Inspected TestRange launch hook changed");
        var result = new ParameterDefinition("__result", Mono.Cecil.ParameterAttributes.None, new ByReferenceType(scope.Module.TypeSystem.Boolean));
        method.Parameters.Add(result);
        var il = method.Body.GetILProcessor(); var ret = body[7];
        il.InsertBefore(ret, Instruction.Create(OpCodes.Dup));
        il.InsertBefore(ret, Instruction.Create(OpCodes.Brtrue, ret));
        il.InsertBefore(ret, Instruction.Create(OpCodes.Ldarg_2));
        il.InsertBefore(ret, Instruction.Create(OpCodes.Ldc_I4_1));
        il.InsertBefore(ret, Instruction.Create(OpCodes.Stind_I1));
        scope.Count("launch-blocked-result");
    }

    // R6 scan-files: Panel.EnsureCatalog's missile scan appends kinds = LayerKind.All.
    private static void TestRangeCatalogScan(AdapterScope scope, MethodDefinition method)
    {
        var scan = TestRangeExpect(method, 0x000f,
            "call !0 SeaPower.Singleton`1<SeaPower.FileManager>::get_Instance()", "ldstr ammunition", "ldstr *.ini",
            "callvirt System.Collections.Generic.List`1<System.String> SeaPower.FileManager::GetFiles(System.String,System.String)");
        if (method.Body.Instructions.Count(i => i.Operand is MethodReference m && m.Name == "GetFiles") != 1)
            throw new InvalidOperationException("Inspected TestRange catalog scan changed");
        AppendDefaults(scope.Module, scope.Native, method, scan[3], (MethodReference)scan[3].Operand, "scan-files");
        if (scan[3].OpCode != OpCodes.Ldc_I4 || !Equals(scan[3].Operand, 31) || scan[3].Next.OpCode != OpCodes.Callvirt)
            throw new InvalidOperationException("Inspected beta FileManager.GetFiles default changed");
        scope.Count("scan-files");
    }

    // R7 sensor-data: the SENSOR_ASSESSMENT closure reads SensorData with its
    // beta value-type encoding; Distance is read from it unchanged.
    private static void TestRangeSensorData(AdapterScope scope, MethodDefinition method)
    {
        var read = TestRangeExpect(method, 0x00db, "ldarg.0",
            "ldflda SeaPower.ObjectBase/EstimatedSensorRangeData TestRange.ResultHooks/<>c__DisplayClass13_0::__result",
            "ldfld SeaPower.SensorSystem/SensorDistanceData SeaPower.ObjectBase/EstimatedSensorRangeData::SensorData",
            "ldfld System.Single SeaPower.SensorSystem/SensorDistanceData::Distance");
        var field = (FieldReference)read[2].Operand;
        if (field.FieldType.IsValueType || method.Body.Instructions.Count(i => (i.Operand as FieldReference)?.Name == "SensorData") != 1)
            throw new InvalidOperationException("Inspected TestRange sensor assessment changed");
        var actual = scope.Native.GetType("SeaPower.ObjectBase/EstimatedSensorRangeData").Fields.Single(f => f.Name == "SensorData");
        read[2].Operand = scope.Module.ImportReference(actual);
        if (!((FieldReference)read[2].Operand).FieldType.IsValueType)
            throw new InvalidOperationException("Beta SensorData import lost its value-type encoding");
        scope.Count("sensor-data");
    }

    // After every rewrite: no instruction operand of the private image may
    // still encode a Seapower-Scripts type with the wrong value/reference kind.
    // The shared InvalidNativeFields scan reads field definitions only.
    private static void TestRangeFinish(AdapterScope scope)
    {
        if (!nativeTypes.TryGetValue(scope.Native, out var definitions)) {
            definitions = Types(scope.Native.Types).ToDictionary(t => t.FullName);
            nativeTypes[scope.Native] = definitions;
        }
        var errors = new List<string>();
        foreach (var type in Types(scope.Module.Types)) foreach (var method in type.Methods.Where(m => m.HasBody))
            foreach (var instruction in method.Body.Instructions) {
                string where = type.FullName + "::" + method.Name;
                // Signature blobs carry the class/valuetype encoding; member
                // parents (TypeRef rows) do not, so they are not checked.
                if (instruction.Operand is FieldReference field) Check(field.FieldType, where, definitions, errors);
                else if (instruction.Operand is MethodReference call) {
                    Check(call.ReturnType, where, definitions, errors);
                    foreach (var parameter in call.Parameters) Check(parameter.ParameterType, where, definitions, errors);
                }
            }
        if (errors.Count != 0) throw new InvalidOperationException("TestRange private image keeps stale native encodings: " + String.Join("; ", errors.Take(4)));
    }

    // ---- Matching helpers.
    private static void TestRangeShape(MethodDefinition method, bool isStatic, string returnType, params string[] parameters)
    {
        if (method.IsStatic != isStatic || method.ReturnType.FullName != returnType || !TestRangeParameters(method, parameters) || method.HasGenericParameters)
            throw new InvalidOperationException("Inspected TestRange " + method.DeclaringType.FullName + "::" + method.Name + " signature changed");
    }

    private static bool TestRangeParameters(MethodReference method, params string[] types)
        => method.Parameters.Select(p => p.ParameterType.FullName).SequenceEqual(types);

    private static bool TestRangeCalls(Instruction instruction, MethodDefinition target)
        => (instruction.OpCode == OpCodes.Call || instruction.OpCode == OpCodes.Callvirt) && instruction.Operand is MethodReference call &&
            call.DeclaringType.FullName == target.DeclaringType.FullName && call.Name == target.Name && call.HasThis == target.HasThis &&
            call.ReturnType.FullName == target.ReturnType.FullName &&
            call.Parameters.Select(p => p.ParameterType.FullName).SequenceEqual(target.Parameters.Select(p => p.ParameterType.FullName));

    private static Instruction TestRangeBack(Instruction instruction, int count)
    {
        for (int i = 0; i < count && instruction != null; i++) instruction = instruction.Previous;
        return instruction;
    }

    // Expects the exact consecutive instructions, opcode and operand, starting
    // at the author's IL offset; throws with what it found otherwise.
    private static Instruction[] TestRangeExpect(MethodDefinition method, int offset, params string[] expected)
    {
        var start = method.Body.Instructions.FirstOrDefault(i => i.Offset == offset);
        var found = new List<Instruction>();
        for (var current = start; current != null && found.Count < expected.Length; current = current.Next) found.Add(current);
        for (int i = 0; i < expected.Length; i++) {
            string actual = i < found.Count ? TestRangeText(found[i]) : "<end>";
            if (actual != expected[i])
                throw new InvalidOperationException("Inspected TestRange " + method.DeclaringType.FullName + "::" + method.Name + " changed at IL_" +
                    (offset).ToString("x4") + "+" + i + ": expected '" + expected[i] + "', found '" + actual + "'");
        }
        return found.ToArray();
    }

    private static string TestRangeText(Instruction instruction)
    {
        string operand = instruction.Operand switch {
            null => null,
            Instruction target => "IL_" + target.Offset.ToString("x4"),
            MemberReference member => member.FullName,
            IFormattable number => number.ToString(null, CultureInfo.InvariantCulture),
            var other => other.ToString(),
        };
        return operand == null ? instruction.OpCode.Name : instruction.OpCode.Name + " " + operand;
    }
}
