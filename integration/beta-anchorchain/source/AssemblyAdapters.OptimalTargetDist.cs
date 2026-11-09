using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    // R6 (7 Nov 2026): Euromod's OptimalTargetDist 1.2.1.0 (Workshop 3784474738,
    // MVID e8cbcdcc-7c00-49df-b36a-214ab390f280) as captured on 3 Nov 2026.
    // On the beta its SystemGroup launch sharing (SharedLaunchGroups) disables
    // itself: the author's Transpiler dry run finds the shared-launch layout
    // 1/1/1/4 in WeaponSystemLauncher.OnUpdate, because Build 261026 added a
    // fourth _sharedLaunchTimers[_systemName] = GameTime.missionElapsedTime
    // write (IL_1608) on its new failed-launch branch, and the author's final
    // check expects exactly 1/1/1/3. Every per-site check the author wrote
    // already accepts the new site, which uses the same key, dictionaries and
    // clock as the other three. The adapter changes only the expected write
    // count, ldc.i4.3 -> ldc.i4.4 at Transpiler IL_03bc, so the author's own
    // loop rewrites all seven key loads to GetKey and its validator stays exact
    // to the beta layout. No bridge, retarget or appended default is needed.
    internal const string OptimalTargetDistHash = "0ac35f8235d0a18a69e816ff1ed04f54212ecfa4d6a85b2350f1d9e5be5311d5";

    private static ImageAdapter OptimalTargetDistAdapter() => new ImageAdapter {
        Name = "OptimalTargetDist",
        Hashes = new[] { OptimalTargetDistHash },
        RequireNative = OptimalTargetDistRequireNative,
        RewriteMethod = OptimalTargetDistRewriteMethod,
        // launch-layout: SharedLaunchGroups.Transpiler IL_03bc; locations: the
        // shared rule on ACModActivation.Guard.Allow IL_009a and IL_0119.
        ExpectedAudit = "launch-layout=1, locations=2",
    };

    private const string OptimalTargetDistType = "OptimalTargetDistAnchorChain.SharedLaunchGroups";
    private const string OptimalTargetDistSequence = "System.Collections.Generic.IEnumerable`1<HarmonyLib.CodeInstruction>";
    private const string OptimalTargetDistList = "System.Collections.Generic.List`1<HarmonyLib.CodeInstruction>";
    private const string OptimalTargetDistIntervals = "System.Collections.Generic.Dictionary`2<System.String,System.Single>";
    private const string OptimalTargetDistTimers = "System.Collections.Generic.Dictionary`2<System.String,System.Double>";

    // The author's SharedLaunchGroups.Transpiler (rid 5, 1062 bytes) from the
    // loop increment to the end: the 1/1/1/3 layout check (IL_03ab-IL_03bd),
    // its 'Unrecognized launch layout: ' throw, and the return of the rewritten
    // list. Only IL_03bc changes.
    private static readonly string[] OptimalTargetDistLayoutCheck = {
        "IL_0398 ldloc.s V_8", "IL_039a ldc.i4.1", "IL_039b add", "IL_039c stloc.s V_8",
        "IL_039e ldloc.s V_8", "IL_03a0 ldloc.0",
        "IL_03a1 callvirt instance " + OptimalTargetDistList + "::get_Count():System.Int32", "IL_03a6 blt IL_007b",
        "IL_03ab ldloc.s V_4", "IL_03ad ldc.i4.1", "IL_03ae bne.un.s IL_03bf",
        "IL_03b0 ldloc.s V_5", "IL_03b2 ldc.i4.1", "IL_03b3 bne.un.s IL_03bf",
        "IL_03b5 ldloc.s V_6", "IL_03b7 ldc.i4.1", "IL_03b8 bne.un.s IL_03bf",
        "IL_03ba ldloc.s V_7", "IL_03bc ldc.i4.3", "IL_03bd beq.s IL_0424",
        "IL_03bf ldc.i4.8", "IL_03c0 newarr System.Object", "IL_03c5 stloc.s V_18",
        "IL_03c7 ldloc.s V_18", "IL_03c9 ldc.i4.0", "IL_03ca ldstr 'Unrecognized launch layout: '", "IL_03cf stelem.ref",
        "IL_03d0 ldloc.s V_18", "IL_03d2 ldc.i4.1", "IL_03d3 ldloc.s V_4", "IL_03d5 box System.Int32", "IL_03da stelem.ref",
        "IL_03db ldloc.s V_18", "IL_03dd ldc.i4.2", "IL_03de ldstr '/'", "IL_03e3 stelem.ref",
        "IL_03e4 ldloc.s V_18", "IL_03e6 ldc.i4.3", "IL_03e7 ldloc.s V_5", "IL_03e9 box System.Int32", "IL_03ee stelem.ref",
        "IL_03ef ldloc.s V_18", "IL_03f1 ldc.i4.4", "IL_03f2 ldstr '/'", "IL_03f7 stelem.ref",
        "IL_03f8 ldloc.s V_18", "IL_03fa ldc.i4.5", "IL_03fb ldloc.s V_6", "IL_03fd box System.Int32", "IL_0402 stelem.ref",
        "IL_0403 ldloc.s V_18", "IL_0405 ldc.i4.6", "IL_0406 ldstr '/'", "IL_040b stelem.ref",
        "IL_040c ldloc.s V_18", "IL_040e ldc.i4.7", "IL_040f ldloc.s V_7", "IL_0411 box System.Int32", "IL_0416 stelem.ref",
        "IL_0417 ldloc.s V_18", "IL_0419 call static System.String::Concat(System.Object[]):System.String",
        "IL_041e newobj instance System.NotSupportedException::.ctor(System.String):System.Void", "IL_0423 throw",
        "IL_0424 ldloc.0", "IL_0425 ret" };

    // The same method's timestamp-write branch: V_7 counts only sites that the
    // author's DictionaryCall accepted as Dictionary<string,T>.set_Item(string,T)
    // after the native mission clock, so V_7 is the timer-write count.
    private static readonly string[] OptimalTargetDistWriteCounter = {
        "IL_02c4 call static " + OptimalTargetDistType + "::DictionaryCall(" + OptimalTargetDistList +
            ",System.Int32,System.Type,System.String,System.Type,System.Type[]):System.Boolean",
        "IL_02c9 brtrue.s IL_02d6", "IL_02cb ldstr 'Unrecognized shared-launch timestamp write.'",
        "IL_02d0 newobj instance System.NotSupportedException::.ctor(System.String):System.Void", "IL_02d5 throw",
        "IL_02d6 ldloc.s V_7", "IL_02d8 ldc.i4.1", "IL_02d9 add", "IL_02da stloc.s V_7", "IL_02dc br IL_0374" };

    internal static string OptimalTargetDistDescribe(Instruction instruction)
    {
        string name = "IL_" + instruction.Offset.ToString("x4", CultureInfo.InvariantCulture) + " " + instruction.OpCode.Name;
        switch (instruction.Operand) {
            case FieldReference field:
                return name + " " + field.DeclaringType.FullName + "::" + field.Name + ":" + field.FieldType.FullName;
            case MethodReference method:
                return name + (method.HasThis ? " instance " : " static ") + method.DeclaringType.FullName + "::" + method.Name + "(" +
                    String.Join(",", method.Parameters.Select(p => p.ParameterType.FullName)) + "):" + method.ReturnType.FullName;
            case TypeReference type:
                return name + " " + type.FullName;
            case VariableDefinition variable:
                return name + " V_" + variable.Index.ToString(CultureInfo.InvariantCulture);
            case Instruction target:
                return name + " IL_" + target.Offset.ToString("x4", CultureInfo.InvariantCulture);
            case string text:
                return name + " '" + text + "'";
            case double number:
                return name + " " + number.ToString("R", CultureInfo.InvariantCulture);
            case null:
                return name;
            default:
                return name + " " + Convert.ToString(instruction.Operand, CultureInfo.InvariantCulture);
        }
    }

    // One native shared-launch site in WeaponSystemLauncher.OnUpdate, as the
    // author's Transpiler matches it: ldfld ObjectBase::<dictionary>;
    // ldarg.0; ldfld BaseSystem::_systemName; then the dictionary operation.
    private static IEnumerable<string> OptimalTargetDistSite(int offset, string kind)
    {
        bool intervals = kind == "contains" || kind == "interval";
        string field = intervals ? "_sharedLaunchIntervals:" + OptimalTargetDistIntervals : "_sharedLaunchTimers:" + OptimalTargetDistTimers;
        string dictionary = intervals ? OptimalTargetDistIntervals : OptimalTargetDistTimers;
        string At(int delta) => "IL_" + (offset + delta).ToString("x4", CultureInfo.InvariantCulture);
        yield return At(0) + " ldfld SeaPower.ObjectBase::" + field;
        yield return At(5) + " ldarg.0";
        yield return At(6) + " ldfld SeaPower.BaseSystem::_systemName:System.String";
        if (kind == "contains") yield return At(11) + " callvirt instance " + dictionary + "::ContainsKey(!0):System.Boolean";
        else if (kind == "write") {
            yield return At(11) + " call static SeaPower.GameTime::get_missionElapsedTime():System.Double";
            yield return At(16) + " callvirt instance " + dictionary + "::set_Item(!0,!1):System.Void";
        }
        else yield return At(11) + " callvirt instance " + dictionary + "::get_Item(!0):!1";
    }

    // Native beta WeaponSystemLauncher.OnUpdate (rid 39805, 6548 bytes): the
    // seven sites the adapted Transpiler accepts, in order. IL_1608 is the new
    // failed-launch write (taken when launch() returns false and
    // !_lastLaunchMalfunction); stable 261021 has the other six only.
    private static readonly string[] OptimalTargetDistNativeSites = new[] {
        (0x113f, "contains"), (0x11e9, "timer"), (0x1200, "interval"),
        (0x13c1, "write"), (0x150a, "write"), (0x1608, "write"), (0x1775, "write") }
        .SelectMany(site => OptimalTargetDistSite(site.Item1, site.Item2)).ToArray();

    // Native beta ObjectBaseLoader.LoadWeaponSystems seeds a new SystemName's
    // timer at -1000.0, the value the author's Configure and InitialTimer use
    // for a group key.
    private static readonly string[] OptimalTargetDistNativeSeed = {
        "IL_0a81 ldfld SeaPower.ObjectBase::_sharedLaunchTimers:" + OptimalTargetDistTimers, "IL_0a86 ldloc.s V_10",
        "IL_0a88 ldc.r8 -1000", "IL_0a91 callvirt instance " + OptimalTargetDistTimers + "::Add(!0,!1):System.Void" };

    // Configure removes grouped SystemNames from both dictionaries. That is
    // safe only while no other native code reads them by name.
    private static readonly string[] OptimalTargetDistNativeUsers = {
        "SeaPower.ObjectBase::.ctor()",
        "SeaPower.ObjectBaseLoader::LoadWeaponSystems(SeaPower.IniHandler,SeaPower.ObjectBaseParameters,SeaPower.ObjectBase)",
        "SeaPower.WeaponSystemLauncher::OnUpdate()" };

    private static ModuleDefinition optimalTargetDistInspected;

    // The native shapes the author's SharedLaunchGroups binds, and the layout
    // the adapted count accepts, asserted on the pinned beta image before any
    // rewrite. A different beta fails closed.
    private static void OptimalTargetDistRequireNative(ModuleDefinition native)
    {
        if (ReferenceEquals(optimalTargetDistInspected, native)) return;
        var objectBase = native.GetType("SeaPower.ObjectBase");
        var baseSystem = native.GetType("SeaPower.BaseSystem");
        var launcher = native.GetType("SeaPower.WeaponSystemLauncher");
        var loader = native.GetType("SeaPower.ObjectBaseLoader");
        var clock = native.GetType("SeaPower.GameTime");
        if (objectBase == null || baseSystem == null || launcher == null || loader == null || clock == null ||
            objectBase.IsValueType || baseSystem.IsValueType || launcher.IsValueType)
            throw new InvalidOperationException("Inspected beta ObjectBase/BaseSystem/WeaponSystemLauncher/ObjectBaseLoader/GameTime changed");
        bool PublicField(TypeDefinition type, string name, string fieldType)
        {
            var matches = type.Fields.Where(f => f.Name == name).ToList();
            return matches.Count == 1 && matches[0].IsPublic && !matches[0].IsStatic && matches[0].FieldType.FullName == fieldType;
        }
        if (!PublicField(objectBase, "_sharedLaunchIntervals", OptimalTargetDistIntervals) ||
            !PublicField(objectBase, "_sharedLaunchTimers", OptimalTargetDistTimers) ||
            !PublicField(baseSystem, "_systemName", "System.String") || !PublicField(baseSystem, "_sectionName", "System.String") ||
            !PublicField(baseSystem, "_baseObject", "SeaPower.ObjectBase"))
            throw new InvalidOperationException("Inspected beta shared-launch fields changed");
        bool derives = false;
        for (TypeReference current = launcher.BaseType; current != null && !derives; current = current.Resolve()?.BaseType)
            derives = current.FullName == "SeaPower.BaseSystem";
        if (!derives) throw new InvalidOperationException("Inspected beta WeaponSystemLauncher base type changed");

        var elapsed = clock.Methods.Where(m => m.Name == "get_missionElapsedTime").ToList();
        if (elapsed.Count != 1 || elapsed[0].HasThis || elapsed[0].HasParameters || elapsed[0].ReturnType.FullName != "System.Double")
            throw new InvalidOperationException("Inspected beta GameTime.missionElapsedTime changed");
        var load = loader.Methods.Where(m => m.Name == "LoadWeaponSystems" &&
            ParameterTypes(m, "SeaPower.IniHandler", "SeaPower.ObjectBaseParameters", "SeaPower.ObjectBase")).ToList();
        if (load.Count != 1 || !load[0].IsPublic || !load[0].IsStatic || load[0].ReturnType.FullName != "System.Void" || !load[0].HasBody)
            throw new InvalidOperationException("Inspected beta ObjectBaseLoader.LoadWeaponSystems changed");
        var updates = launcher.Methods.Where(m => m.Name == "OnUpdate" && !m.HasParameters).ToList();
        if (updates.Count != 1 || !updates[0].IsPublic || updates[0].IsStatic || updates[0].ReturnType.FullName != "System.Void" || !updates[0].HasBody)
            throw new InvalidOperationException("Inspected beta WeaponSystemLauncher.OnUpdate changed");

        // Every shared-dictionary access in OnUpdate, in order, with the exact
        // key expression and operation the author's Transpiler matches.
        var code = updates[0].Body.Instructions;
        var sites = new List<string>();
        for (int i = 0; i < code.Count; i++) {
            if (code[i].Operand is not FieldReference field || field.DeclaringType.FullName != "SeaPower.ObjectBase" ||
                (field.Name != "_sharedLaunchIntervals" && field.Name != "_sharedLaunchTimers")) continue;
            int length = i + 3 < code.Count && code[i + 3].OpCode == OpCodes.Call ? 5 : 4;
            if (i + length > code.Count) throw new InvalidOperationException("Inspected beta WeaponSystemLauncher.OnUpdate shared-launch layout changed");
            sites.AddRange(code.Skip(i).Take(length).Select(OptimalTargetDistDescribe));
        }
        if (!sites.SequenceEqual(OptimalTargetDistNativeSites))
            throw new InvalidOperationException("Inspected beta WeaponSystemLauncher.OnUpdate shared-launch layout changed");

        var seed = load[0].Body.Instructions.Select(OptimalTargetDistDescribe).ToList();
        int seeds = Enumerable.Range(0, Math.Max(0, seed.Count - 3)).Count(k => seed.Skip(k).Take(4).SequenceEqual(OptimalTargetDistNativeSeed));
        if (seeds != 1) throw new InvalidOperationException("Inspected beta LoadWeaponSystems shared-launch timer seed changed");

        var users = new SortedSet<string>(StringComparer.Ordinal);
        foreach (var type in Types(native.Types)) foreach (var method in type.Methods) {
            if (!method.HasBody) continue;
            if (method.Body.Instructions.Any(i => i.Operand is FieldReference f && f.DeclaringType.FullName == "SeaPower.ObjectBase" &&
                (f.Name == "_sharedLaunchIntervals" || f.Name == "_sharedLaunchTimers")))
                users.Add(type.FullName + "::" + method.Name + "(" + String.Join(",", method.Parameters.Select(p => p.ParameterType.FullName)) + ")");
        }
        if (!users.SequenceEqual(OptimalTargetDistNativeUsers))
            throw new InvalidOperationException("Inspected beta shared-launch dictionary users changed: " + String.Join("; ", users));
        optimalTargetDistInspected = native;
    }

    private static bool OptimalTargetDistRewriteMethod(AdapterScope scope, TypeDefinition type, MethodDefinition method)
    {
        if (type.FullName != OptimalTargetDistType || method.Name != "Transpiler") return false;
        var body = method.Body;
        var locals = body.Variables;
        if (!method.IsStatic || method.ReturnType.FullName != OptimalTargetDistList || !ParameterTypes(method, OptimalTargetDistSequence) ||
            locals.Count != 19 || Enumerable.Range(4, 5).Any(k => locals[k].VariableType.FullName != "System.Int32") ||
            locals[18].VariableType.FullName != "System.Object[]" || body.ExceptionHandlers.Count != 1)
            throw new InvalidOperationException("Inspected OptimalTargetDist SharedLaunchGroups.Transpiler changed");
        var code = body.Instructions;
        var described = code.Select(OptimalTargetDistDescribe).ToList();
        int check = described.Count - OptimalTargetDistLayoutCheck.Length;
        int counter = described.IndexOf(OptimalTargetDistWriteCounter[0]);
        if (check < 0 || !described.Skip(check).SequenceEqual(OptimalTargetDistLayoutCheck) || counter < 0 ||
            !described.Skip(counter).Take(OptimalTargetDistWriteCounter.Length).SequenceEqual(OptimalTargetDistWriteCounter) ||
            described.Count(d => d.EndsWith(" stloc.s V_7", StringComparison.Ordinal)) != 2)
            throw new InvalidOperationException("Inspected OptimalTargetDist SharedLaunchGroups.Transpiler layout check changed");
        var count = code[check + Array.IndexOf(OptimalTargetDistLayoutCheck, "IL_03bc ldc.i4.3")];
        if (count.OpCode != OpCodes.Ldc_I4_3 || count.Offset != 0x03bc || count.Previous.OpCode != OpCodes.Ldloc_S ||
            ((VariableDefinition)count.Previous.Operand).Index != 7 || count.Next.OpCode != OpCodes.Beq_S)
            throw new InvalidOperationException("Inspected OptimalTargetDist SharedLaunchGroups.Transpiler layout check changed");
        // The beta's 1/1/1/4: one more timer write, in the same idiom.
        count.OpCode = OpCodes.Ldc_I4_4;
        scope.Count("launch-layout");
        return false;
    }
}
