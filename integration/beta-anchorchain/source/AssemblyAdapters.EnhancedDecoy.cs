// Enhanced Decoy Mod 0.5.4 (EnhancedDecoyMod.dll, 7cd4f160, Workshop
// 3784474738) on 0.9.3-261123 (ea653e49). The image was written for a chaff
// launcher with one attacher (WeaponSystemChaff._chaff) and one ammunition
// field (_ammoInUse). 261123 keeps a list of rounds instead, each with its own
// Ammo, Attacher and DecoyBand (Chaff, Flare, Both), and every launch and
// readiness path takes a band. Without this adapter the author's own startup
// check (Plugin.InitializeWhenModEnabled) throws before its first patch and
// the mod rolls itself back. Rewrites, each at its inspected site:
//  - chaff-band-ammo (33): each read of the _ammoInUse field calls a SEST
//    bridge: the native RoundAmmo(Chaff), the first round whose band covers
//    chaff (Chaff or Both), else the native round 0 getter (null with no
//    rounds). The mod handles only radar decoys (chaff and its AirDecoy);
//    in the author's build the launcher's one ammunition was chaff.
//  - chaff-attacher-field, chaff-attacher-read (1, 2): Hooks..cctor looks up
//    the launcher's round list (_rounds) instead of _chaff, and AttacherFor
//    and IsUpgradeReady read the attacher of that same round through a
//    bridge in place of FieldInfo.GetValue, so ammunition and clouds match.
//  - cloud-launch-signature (1): Hooks.Validate asks for
//    ChaffAttacher.launchChaffCloud(int cartridges); the author's ordering
//    check on it (cloud effect before taskforce registration) still runs.
//  - manual-band-signature, effect-cartridges-signature (1, 1): Hooks.Patches
//    asks for ObjectBase.LaunchChaff(bool message, DecoyBand band) and
//    ChaffCloud.launchChaffEffect(..., int cartridges). The author's patch
//    methods bind by name to message and parentSystem/mountObject, unchanged.
//  - launch-band-target, ready-band-target (1, 1): the CanLaunch prefix and
//    the LauncherReady postfix move from the parameterless launchChaff() and
//    readyToLaunch() to launchChaff(DecoyBand) and ReadyToLaunch(DecoyBand).
//    In 261123 the old names are 8-9 byte wrappers that pass Both. Only
//    InputHandler.OnUpdate and ObjectBase.HandleEngageTasks still call them;
//    the manual order (ObjectBase.LaunchChaff), LaunchChaffAgainst and the
//    non-realistic AutoRelease call the band versions directly, so a patch
//    on the wrappers would miss those.
//  - own-launch-band, own-ready-band (5, 4): the mod's own launchChaff() and
//    readyToLaunch() calls (AirDecoySwarm.LaunchNext, ChaffLaunchPolicy.Usable,
//    TryLaunchSalvo and LaunchAmmo, AirDecoyOrders.ProcessQueued and Launch)
//    call launchChaff(Chaff) and ReadyToLaunch(Chaff). Through the wrappers
//    they would ask for Both, which with Realistic Countermeasures on (a Both
//    ammunition split into <name>~chaff and <name>~flare rounds) would fire
//    the ~flare rounds in a chaff salvo and count ready flares as chaff.
//  - flare-pass-through (3): CanLaunch, LauncherReady and ManualChaff take
//    the native "band" argument (Harmony binds it by name) and return at once
//    for a Flare request, so a flare order or flare check is native. Chaff
//    and Both requests get the author's policy, as all requests did before.
//  - salvo-result (1): CanLaunch also takes ref bool __result and sets it
//    when its salvo ran (it then skips the original), so
//    ObjectBase.LaunchChaff logs ChaffOut as for a native launch.
//  - threat-filter-target (1): ThreatFilter moves from OnUpdate to
//    AutoRelease(), where 261123 now reads ObjectBase._threats (once, the
//    author's own one-match requirement); the BeforeChaffUpdate prefix and
//    EndAutoUpdate finalizer stay on OnUpdate, which calls AutoRelease. That
//    one read builds the threat list for both release paths, so it cannot be
//    limited to the non-realistic one: with Realistic Countermeasures on, an
//    upgrade-ready AirDecoy launcher (FilterThreats keeps radar threats only)
//    no longer releases flares automatically against IR missiles.
//  - countermeasure-gate-target (1): CountermeasureGate moves from
//    SeekerBase.CheckCountermeasureLock(ObjectBase), now a 40-byte profiler
//    wrapper, to CheckCountermeasureLockBody(ObjectBase obj), its only
//    callee, which holds the author's cooldown pattern exactly; the
//    CheckCandidate prefix and CheckedCandidate postfix stay on the wrapper.
//  - expiry-filter-off (1): ExpiryFilter needs two _defensiveEffectTime
//    reads in ChaffCloud.OnUpdateEveryFrame; 261123 has none there (the one
//    read is in get_Lifetime), so its transpiler is set to null, which the
//    author's PatchSpec, Validate and Harmony.Patch all accept. The MoveCloud
//    prefix stays. Effect: an air decoy is removed at its launch time plus
//    the native lifetime, not at AirDecoyController.TotalLifetime (powered
//    time plus fall time): sooner where the fall is longer, and later for a
//    swarm follower launched after its modelled sea impact.
//  - radar-ignore-filter-off (1): IgnoreFilter on ActiveRadarSeeker
//    .searchForTarget needs one ignore-list Contains; 261123 has two (its new
//    scan loop and the lock selection), so that transpiler is null too. The
//    EnterRadar/ExitRadar prefix and finalizer stay, and the same filter on
//    createListOfPotentialContacts still applies.
// The other transpilers (LockLossFilter, DefenseFilter, CiwsFilter,
// ContactConstructor, IgnoreFilter on createListOfPotentialContacts) match
// 261123 as written and are judged by the author's own Hooks.Validate
// (R6_EnhancedDecoy runs it). With Realistic Countermeasures on, 261123's
// AutoRelease launches rounds through LaunchRound, which no author hook
// sees; manual orders still go through launchChaff(band) and the hooks.
// ChaffCellsLoaded returns at once in the mod's lazy mode, which 261123
// selects (ChaffAttacher has no _chaffClouds), so it binds no attacher.
using System;
using System.Collections.Generic;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    internal const string EnhancedDecoyHash = "7cd4f160dae75147a84bcc671d791db3012278497decffe80431d262d9ad7548";
    internal const string EnhancedDecoyAudit = "chaff-attacher-field=1, chaff-attacher-read=2, chaff-band-ammo=33, cloud-launch-signature=1, " +
        "countermeasure-gate-target=1, effect-cartridges-signature=1, expiry-filter-off=1, flare-pass-through=3, launch-band-target=1, " +
        "locations=2, manual-band-signature=1, own-launch-band=5, own-ready-band=4, radar-ignore-filter-off=1, ready-band-target=1, " +
        "salvo-result=1, threat-filter-target=1";
    private const string EnhancedDecoyHooks = "EnhancedDecoyMod.Hooks";

    private static ImageAdapter EnhancedDecoyAdapter() => new ImageAdapter {
        Name = "EnhancedDecoy", Hashes = new[] { EnhancedDecoyHash },
        RequireNative = EnhancedDecoyRequireNative,
        RewriteMethod = EnhancedDecoyRewrite,
        ExpectedAudit = EnhancedDecoyAudit,
    };

    private static ModuleDefinition enhancedDecoyNative;

    private static void EnhancedDecoyRequireNative(ModuleDefinition native)
    {
        CurrentNativeSnapshot(native);
        if (ReferenceEquals(enhancedDecoyNative, native)) return;
        ChaffRoundAmmoGetter(native);
        var chaff = native.GetType("SeaPower.WeaponSystemChaff");
        var round = chaff.NestedTypes.Single(t => t.Name == "Round");
        var band = native.GetType("SeaPower.DecoyBand");
        FieldDefinition Field(TypeDefinition t, string name) => t?.Fields.SingleOrDefault(f => f.Name == name);
        bool Instance(FieldDefinition f, string type, bool isPublic) => f != null && !f.IsStatic && f.IsPublic == isPublic && f.FieldType.FullName == type;
        if (band == null || !band.IsEnum || band.Fields.Count(f => f.HasConstant) != 3 ||
            !Equals(Field(band, "Chaff")?.Constant, 0) || !Equals(Field(band, "Flare")?.Constant, 1) || !Equals(Field(band, "Both")?.Constant, 2) ||
            !Instance(Field(chaff, "_rounds"), "System.Collections.Generic.List`1<SeaPower.WeaponSystemChaff/Round>", false) ||
            !Instance(Field(round, "Ammo"), "SeaPower.Ammunition", true) || !Instance(Field(round, "Attacher"), "SeaPower.ChaffAttacher", true) ||
            !Instance(Field(round, "Band"), "SeaPower.DecoyBand", true))
            throw new InvalidOperationException("Inspected 261123 chaff round contract changed");
        // AccessTools.Field searches base types: none may hold the old name.
        for (var t = chaff; t != null; t = t.BaseType == null ? null : native.GetType(t.BaseType.FullName))
            if (t.Fields.Any(f => f.Name == "_chaff"))
                throw new InvalidOperationException("Inspected 261123 chaff round contract changed");
        // The bridge's selection: RoundAmmo(Chaff) returns the Ammo of the
        // first round that Covers the chaff band (Band Chaff or Both).
        var roundAmmo = chaff.Methods.Where(m => m.Name == "RoundAmmo").ToList();
        var covers = chaff.Methods.Where(m => m.Name == "Covers").ToList();
        var coversIl = covers.Count == 1 && covers[0].HasBody ? covers[0].Body.Instructions : null;
        var ammoIl = roundAmmo.Count == 1 && roundAmmo[0].HasBody ? roundAmmo[0].Body.Instructions : null;
        bool BandRead(Instruction i) => i.OpCode == OpCodes.Ldfld && i.Operand is FieldReference f && f.Name == "Band" &&
            f.DeclaringType.FullName == "SeaPower.WeaponSystemChaff/Round";
        if (ammoIl == null || !roundAmmo[0].IsPublic || !roundAmmo[0].HasThis || roundAmmo[0].ReturnType.FullName != "SeaPower.Ammunition" ||
            !ParameterTypes(roundAmmo[0], "SeaPower.DecoyBand") || roundAmmo[0].Body.CodeSize != 69 ||
            ammoIl.Count(i => i.Operand is FieldReference f && f.Name == "_rounds") != 1 ||
            ammoIl.Count(i => i.Operand is MethodReference m && m.Name == "Covers") != 1 ||
            ammoIl.Count(i => i.OpCode == OpCodes.Ldfld && i.Operand is FieldReference a && a.Name == "Ammo") != 1 ||
            coversIl == null || covers[0].HasThis || !ParameterTypes(covers[0], "SeaPower.WeaponSystemChaff/Round", "SeaPower.DecoyBand") ||
            covers[0].Body.CodeSize != 25 ||
            !(coversIl[0].OpCode == OpCodes.Ldarg_1 && coversIl[1].OpCode == OpCodes.Ldc_I4_2 && coversIl[2].OpCode == OpCodes.Beq_S &&
              coversIl[3].OpCode == OpCodes.Ldarg_0 && BandRead(coversIl[4]) && coversIl[5].OpCode == OpCodes.Ldarg_1 &&
              coversIl[6].OpCode == OpCodes.Beq_S && coversIl[7].OpCode == OpCodes.Ldarg_0 && BandRead(coversIl[8]) &&
              coversIl[9].OpCode == OpCodes.Ldc_I4_2 && coversIl[10].OpCode == OpCodes.Ceq && coversIl[11].OpCode == OpCodes.Ret &&
              coversIl[12].OpCode == OpCodes.Ldc_I4_1 && coversIl[13].OpCode == OpCodes.Ret && coversIl.Count == 14))
            throw new InvalidOperationException("Inspected 261123 chaff band round selection changed");
        // Signatures the author's Validate and Patches name, one overload each.
        MethodDefinition Only(string type, string name, string returns, params string[] parameters)
        {
            var found = native.GetType(type)?.Methods.Where(m => m.Name == name).ToList();
            if (found == null || found.Count != 1 || !found[0].HasThis || !found[0].HasBody || found[0].ReturnType.FullName != returns ||
                !ParameterTypes(found[0], parameters))
                throw new InvalidOperationException("Inspected 261123 " + type + "::" + name + " signature changed");
            return found[0];
        }
        Only("SeaPower.ChaffAttacher", "launchChaffCloud", "SeaPower.ChaffCloud", "System.Int32");
        var manual = Only("SeaPower.ObjectBase", "LaunchChaff", "System.Void", "System.Boolean", "SeaPower.DecoyBand");
        Only("SeaPower.ChaffCloud", "launchChaffEffect", "System.Void", "SeaPower.WeaponSystemChaff", "UnityEngine.GameObject", "UnityEngine.GameObject", "System.Int32");
        if (manual.Parameters[0].Name != "message" || manual.Parameters[1].Name != "band")
            throw new InvalidOperationException("Inspected 261123 SeaPower.ObjectBase::LaunchChaff signature changed");
        // The old names are wrappers that pass Both to the band versions.
        var launches = chaff.Methods.Where(m => m.Name == "launchChaff").ToList();
        var readies = chaff.Methods.Where(m => m.Name == "readyToLaunch" || m.Name == "ReadyToLaunch").ToList();
        var launch = launches.SingleOrDefault(m => ParameterTypes(m, "SeaPower.DecoyBand"));
        var ready = readies.SingleOrDefault(m => m.Name == "ReadyToLaunch" && ParameterTypes(m, "SeaPower.DecoyBand"));
        bool Wraps(MethodDefinition wrapper, MethodDefinition target, bool pop)
        {
            var il = wrapper?.HasBody == true ? wrapper.Body.Instructions : null;
            return il != null && wrapper.IsPublic && wrapper.HasThis && wrapper.Parameters.Count == 0 && target != null &&
                il.Count == (pop ? 5 : 4) && il[0].OpCode == OpCodes.Ldarg_0 && il[1].OpCode == OpCodes.Ldc_I4_2 &&
                il[2].OpCode == OpCodes.Call && il[2].Operand is MethodReference m && SameMethod(m, target) &&
                (!pop || il[3].OpCode == OpCodes.Pop) && il[il.Count - 1].OpCode == OpCodes.Ret;
        }
        if (launches.Count != 2 || readies.Count != 2 || launch == null || ready == null ||
            !launch.IsPublic || launch.ReturnType.FullName != "System.Boolean" || launch.Parameters[0].Name != "band" ||
            !ready.IsPublic || ready.ReturnType.FullName != "System.Boolean" || ready.Parameters[0].Name != "band" ||
            !Wraps(launches.Single(m => m != launch), launch, true) || !Wraps(readies.Single(m => m != ready), ready, false))
            throw new InvalidOperationException("Inspected 261123 chaff launch and readiness wrappers changed");
        // The automatic release's threat-list read moved from OnUpdate into
        // AutoRelease, which OnUpdate calls once.
        bool Threats(Instruction i) => i.OpCode == OpCodes.Ldfld && i.Operand is FieldReference f && f.Name == "_threats" &&
            f.DeclaringType.FullName == "SeaPower.ObjectBase";
        var update = chaff.Methods.Where(m => m.Name == "OnUpdate").ToList();
        var auto = chaff.Methods.Where(m => m.Name == "AutoRelease").ToList();
        if (update.Count != 1 || auto.Count != 1 || !auto[0].HasBody || auto[0].Parameters.Count != 0 || !auto[0].HasThis ||
            auto[0].ReturnType.FullName != "System.Void" || auto[0].Body.CodeSize != 761 || update[0].Parameters.Count != 0 ||
            update[0].Body.Instructions.Any(Threats) || auto[0].Body.Instructions.Count(Threats) != 1 ||
            update[0].Body.Instructions.Count(i => i.Operand is MethodReference m && SameMethod(m, auto[0])) != 1 ||
            Types(native.Types).SelectMany(t => t.Methods).Where(m => m.HasBody && m != update[0])
                .Any(m => m.Body.Instructions.Any(i => i.Operand is MethodReference c && c.Name == "AutoRelease" &&
                    c.DeclaringType.FullName == "SeaPower.WeaponSystemChaff")))
            throw new InvalidOperationException("Inspected 261123 chaff automatic release changed");
        // CheckCountermeasureLock(ObjectBase) is now a profiler wrapper whose
        // only work is one call to CheckCountermeasureLockBody(ObjectBase) with
        // the same seeker and candidate, the one caller of that body.
        var seeker = native.GetType("SeaPower.SeekerBase");
        var wrapper = seeker.Methods.Single(m => m.Name == "CheckCountermeasureLock" && ParameterTypes(m, "SeaPower.ObjectBase"));
        var bodies = seeker.Methods.Where(m => m.Name == "CheckCountermeasureLockBody").ToList();
        var wrapperIl = wrapper.Body.Instructions;
        var bodyCall = wrapperIl.Where(i => i.Operand is MethodReference m && m.Name == "CheckCountermeasureLockBody").ToList();
        if (bodies.Count != 1 || !bodies[0].HasThis || !bodies[0].HasBody || bodies[0].ReturnType.FullName != "System.Boolean" ||
            !ParameterTypes(bodies[0], "SeaPower.ObjectBase") || bodies[0].Parameters[0].Name != "obj" || wrapper.Parameters[0].Name != "obj" ||
            wrapper.Body.CodeSize != 40 || bodyCall.Count != 1 || bodyCall[0].OpCode != OpCodes.Call || !SameMethod((MethodReference)bodyCall[0].Operand, bodies[0]) ||
            bodyCall[0].Previous.OpCode != OpCodes.Ldarg_1 || bodyCall[0].Previous.Previous.OpCode != OpCodes.Ldarg_0 ||
            wrapperIl.Count(i => i.OpCode == OpCodes.Ldarg_1) != 1 || wrapperIl.Count(i => i.Operand is MethodReference) != 3 ||
            bodies[0].Body.Instructions.Any(i => i.OpCode == OpCodes.Starg || i.OpCode == OpCodes.Starg_S || i.OpCode == OpCodes.Ldarga || i.OpCode == OpCodes.Ldarga_S) ||
            Types(native.Types).SelectMany(t => t.Methods).Where(m => m.HasBody && m != wrapper)
                .Any(m => m.Body.Instructions.Any(i => i.Operand is MethodReference c && c.Name == "CheckCountermeasureLockBody")))
            throw new InvalidOperationException("Inspected 261123 countermeasure lock body changed");
        // ExpiryFilter rewrites two _defensiveEffectTime reads in the cloud's
        // per-frame update. 261123 reads it once, in get_Lifetime (corridor
        // clouds use _corridorLifetime), which UpdateEveryFrameBody calls.
        bool Effect(Instruction i) => i.OpCode == OpCodes.Ldfld && i.Operand is FieldReference f && f.Name == "_defensiveEffectTime";
        var cloud = native.GetType("SeaPower.ChaffCloud");
        var frame = cloud.Methods.Single(m => m.Name == "OnUpdateEveryFrame");
        var frameBody = cloud.Methods.Single(m => m.Name == "UpdateEveryFrameBody");
        var lifetime = cloud.Methods.Single(m => m.Name == "get_Lifetime");
        if (frame.Body.Instructions.Any(Effect) || frameBody.Body.Instructions.Any(Effect) || lifetime.Body.Instructions.Count(Effect) != 1 ||
            frameBody.Body.Instructions.Count(i => i.Operand is MethodReference m && SameMethod(m, lifetime)) != 2 ||
            frame.Body.Instructions.Count(i => i.Operand is MethodReference m && SameMethod(m, frameBody)) != 1)
            throw new InvalidOperationException("Inspected 261123 chaff cloud lifetime changed");
        // IgnoreFilter on ActiveRadarSeeker.searchForTarget requires one
        // ignore-list Contains; 261123 has two (the new scan loop and the lock
        // selection), so the author's own check would reject it.
        var search = native.GetType("SeaPower.ActiveRadarSeeker").Methods.Single(m => m.Name == "searchForTarget");
        if (search.Body.Instructions.Count(i => i.OpCode == OpCodes.Callvirt && i.Operand is MethodReference c && c.Name == "Contains" &&
                c.DeclaringType.FullName == "System.Collections.Generic.List`1<SeaPower.ObjectBase>") != 2)
            throw new InvalidOperationException("Inspected 261123 radar seeker ignore list changed");
        enhancedDecoyNative = native;
    }

    // The 261123 read-only _ammoInUse property, asserted exactly: no field and
    // no setter of that name, one parameterless instance getter returning
    // SeaPower.Ammunition, whose body reads _rounds[0].Ammo. Also used by the
    // Multi-Stage Missiles chaff adapter.
    private static MethodDefinition ChaffRoundAmmoGetter(ModuleDefinition native)
    {
        var chaff = native.GetType("SeaPower.WeaponSystemChaff");
        var round = chaff?.NestedTypes.SingleOrDefault(t => t.Name == "Round");
        var getters = chaff?.Methods.Where(m => m.Name == "get__ammoInUse").ToList();
        var body = getters?.Count == 1 && getters[0].HasBody ? getters[0].Body.Instructions : null;
        if (chaff == null || round == null || body == null ||
            chaff.Fields.Any(f => f.Name == "_ammoInUse") ||
            chaff.Methods.Any(m => m.Name == "set__ammoInUse") ||
            chaff.Properties.SingleOrDefault(p => p.Name == "_ammoInUse")?.SetMethod != null ||
            !getters[0].HasThis || getters[0].IsStatic || getters[0].HasParameters ||
            getters[0].ReturnType.FullName != "SeaPower.Ammunition" || getters[0].Body.CodeSize != 34 ||
            body.Count(i => i.OpCode == OpCodes.Ldfld && i.Operand is FieldReference f &&
                f.DeclaringType.FullName == "SeaPower.WeaponSystemChaff" && f.Name == "_rounds") != 2 ||
            body.Count(i => i.OpCode == OpCodes.Ldfld && i.Operand is FieldReference a &&
                a.DeclaringType.FullName == "SeaPower.WeaponSystemChaff/Round" && a.Name == "Ammo" &&
                a.FieldType.FullName == "SeaPower.Ammunition") != 1 ||
            body.Count(i => i.OpCode == OpCodes.Ldnull) != 1)
            throw new InvalidOperationException("Inspected 261123 chaff round ammunition getter changed");
        return getters[0];
    }

    private static bool EnhancedDecoyRewrite(AdapterScope scope, TypeDefinition type, MethodDefinition method)
    {
        var il = method.Body.Instructions;
        string at = type.FullName + "::" + method.Name;
        bool hooks = type.FullName == EnhancedDecoyHooks;
        foreach (var instruction in il) {
            if (!(instruction.Operand is FieldReference field && field.Name == "_ammoInUse" &&
                field.DeclaringType.FullName == "SeaPower.WeaponSystemChaff")) continue;
            if (instruction.OpCode != OpCodes.Ldfld || field.FieldType.FullName != "SeaPower.Ammunition")
                throw new InvalidOperationException("Uninspected Enhanced Decoy chaff ammunition access in " + at);
            instruction.OpCode = OpCodes.Call;
            instruction.Operand = scope.Bridge(nameof(BetaCompatibilityCalls.EnhancedDecoyChaffAmmo));
            scope.Count("chaff-band-ammo");
        }
        // The mod's own launches and readiness checks ask for the chaff band:
        // callvirt launchChaff() becomes ldc.i4.0 (Chaff); callvirt
        // launchChaff(DecoyBand); pop, and callvirt readyToLaunch() becomes
        // ldc.i4.0; callvirt ReadyToLaunch(DecoyBand). The original
        // instruction becomes the ldc, so a branch to it still lands first.
        var chaffType = scope.Native.GetType("SeaPower.WeaponSystemChaff");
        foreach (var instruction in il.ToList()) {
            if (!(instruction.Operand is MethodReference call && call.DeclaringType.FullName == "SeaPower.WeaponSystemChaff" &&
                (call.Name == "launchChaff" || call.Name == "readyToLaunch") && call.Parameters.Count == 0)) continue;
            bool launch = call.Name == "launchChaff";
            if (instruction.OpCode != OpCodes.Callvirt || !call.HasThis ||
                call.ReturnType.FullName != (launch ? "System.Void" : "System.Boolean") || !EnhancedDecoyOwnLaunches.Contains(at))
                throw new InvalidOperationException("Uninspected Enhanced Decoy chaff launch call in " + at);
            var target = chaffType.Methods.Single(m => m.Name == (launch ? "launchChaff" : "ReadyToLaunch") && ParameterTypes(m, "SeaPower.DecoyBand"));
            var writer0 = method.Body.GetILProcessor();
            var banded = Instruction.Create(OpCodes.Callvirt, scope.Module.ImportReference(target));
            instruction.OpCode = OpCodes.Ldc_I4_0; instruction.Operand = null;
            writer0.InsertAfter(instruction, banded);
            if (launch) writer0.InsertAfter(banded, Instruction.Create(OpCodes.Pop));
            scope.Count(launch ? "own-launch-band" : "own-ready-band");
        }
        if (hooks && (method.Name == "CanLaunch" || method.Name == "LauncherReady" || method.Name == "ManualChaff")) {
            EnhancedDecoyBandHook(scope, method);
            return false;
        }
        // Every other site that names a retired or retargeted member is one of
        // the inspected sites below; anything else is refused.
        bool Attacher(Instruction i) => i.Operand is FieldReference f && f.Name == "Attacher" && f.DeclaringType.FullName == EnhancedDecoyHooks;
        bool Name(Instruction i, params string[] names) => i.OpCode == OpCodes.Ldstr && names.Contains((string)i.Operand);
        var sites = il.Where(i => Attacher(i) || Name(i, "_chaff", "launchChaffCloud", "LaunchChaff", "launchChaff", "readyToLaunch",
            "launchChaffEffect", "ThreatFilter", "CountermeasureGate", "ExpiryFilter", "IgnoreFilter",
            "AutoRelease", "CheckCountermeasureLockBody")).ToList();
        string kind = !hooks ? null : method.Name == ".cctor" ? "cctor" : method.Name == "Validate" ? "validate" :
            method.Name == "Patches" ? "patches" : method.Name == "AttacherFor" || method.Name == "IsUpgradeReady" ? "read" : null;
        if (kind == null) {
            if (sites.Count != 0) throw new InvalidOperationException("Uninspected Enhanced Decoy chaff member name in " + at);
            return false;
        }
        var types = scope.Native;
        TypeReference Native(string name) => name == "System.Int32" ? scope.Module.TypeSystem.Int32 :
            scope.Module.ImportReference(types.GetType(name) ?? throw new InvalidOperationException("Missing native type " + name));
        if (kind == "cctor") {
            var name = sites.SingleOrDefault(i => Name(i, "_chaff"));
            var store = name?.Next?.Next;
            if (method.Body.CodeSize != 161 || sites.Count != 2 || name == null || !IsTypeOf(name.Previous, "SeaPower.WeaponSystemChaff") ||
                !(name.Next.OpCode == OpCodes.Call && name.Next.Operand is MethodReference lookup && lookup.Name == "Field" &&
                  lookup.DeclaringType.FullName == EnhancedDecoyHooks && ParameterTypes(lookup, "System.Type", "System.String")) ||
                store.OpCode != OpCodes.Stsfld || !Attacher(store) || !sites.Contains(store))
                throw new InvalidOperationException("Inspected Enhanced Decoy chaff attacher lookup changed");
            name.Operand = "_rounds";
            scope.Count("chaff-attacher-field");
            return false;
        }
        if (kind == "read") {
            var load = sites.Count == 1 ? sites[0] : null;
            var get = load?.Next?.Next;
            if (method.Body.CodeSize != (method.Name == "AttacherFor" ? 17 : 167) || load == null || load.OpCode != OpCodes.Ldsfld ||
                load.Next.OpCode != OpCodes.Ldarg_0 ||
                !(get.OpCode == OpCodes.Callvirt && get.Operand is MethodReference value && value.Name == "GetValue" &&
                  value.DeclaringType.FullName == "System.Reflection.FieldInfo" && ParameterTypes(value, "System.Object")) ||
                get.Next.OpCode != OpCodes.Castclass || (get.Next.Operand as TypeReference)?.FullName != "SeaPower.ChaffAttacher")
                throw new InvalidOperationException("Inspected Enhanced Decoy chaff attacher read changed in " + at);
            get.OpCode = OpCodes.Call; get.Operand = scope.Bridge(nameof(BetaCompatibilityCalls.EnhancedDecoyChaffAttacher));
            scope.Count("chaff-attacher-read");
            return false;
        }
        var writer = method.Body.GetILProcessor();
        // name; ldc.i4.0; newarr Type; call Hooks::Method -> one-type array.
        void OneType(Instruction name, string typeName, string newName, string count)
        {
            var length = name.Next; var array = length.Next; var call = array.Next;
            if (length.OpCode != OpCodes.Ldc_I4_0 || array.OpCode != OpCodes.Newarr || (array.Operand as TypeReference)?.FullName != "System.Type" ||
                !IsHooksMethod(call) || !IsTypeOf(name.Previous, null))
                throw new InvalidOperationException("Inspected Enhanced Decoy patch target changed in " + at + ": " + name.Operand);
            if (newName != null) name.Operand = newName;
            length.OpCode = OpCodes.Ldc_I4_1;
            foreach (var extra in new[] { Instruction.Create(OpCodes.Dup), Instruction.Create(OpCodes.Ldc_I4_0),
                Instruction.Create(OpCodes.Ldtoken, Native(typeName)), Instruction.Create(OpCodes.Call, (MethodReference)name.Previous.Operand),
                Instruction.Create(OpCodes.Stelem_Ref) }) writer.InsertBefore(call, extra);
            scope.Count(count);
        }
        // name; ldc.i4.N; newarr Type; stloc V; (ldloc V; ldc.i4.k; ldtoken; call; stelem.ref) x N; ldloc V; call Hooks::Method -> append one type.
        void AppendType(Instruction name, int count, string[] expected, string typeName, string counter)
        {
            var length = name.Next; var array = length.Next; var store = array.Next;
            var parts = new List<Instruction>(); var cursor = store.Next;
            for (int k = 0; k < count * 5 + 2; k++) { parts.Add(cursor); cursor = cursor?.Next; }
            var local = store.Operand as VariableDefinition;
            bool ok = (length.OpCode.Code == Code.Ldc_I4_1 && count == 1 || length.OpCode.Code == Code.Ldc_I4_3 && count == 3) &&
                array.OpCode == OpCodes.Newarr && (array.Operand as TypeReference)?.FullName == "System.Type" &&
                store.OpCode == OpCodes.Stloc_S && local != null && parts.All(p => p != null) && IsTypeOf(name.Previous, null);
            for (int k = 0; ok && k < count; k++) {
                var p = parts.Skip(k * 5).Take(5).ToArray();
                ok = p[0].OpCode == OpCodes.Ldloc_S && p[0].Operand == local && p[1].OpCode.Code == Code.Ldc_I4_0 + k &&
                    p[2].OpCode == OpCodes.Ldtoken && (p[2].Operand as TypeReference)?.FullName == expected[k] &&
                    p[3].OpCode == OpCodes.Call && p[3].Operand is MethodReference h && h.Name == "GetTypeFromHandle" &&
                    p[4].OpCode == OpCodes.Stelem_Ref;
            }
            var last = parts[count * 5]; var call = parts[count * 5 + 1];
            if (!ok || last.OpCode != OpCodes.Ldloc_S || last.Operand != local || !IsHooksMethod(call))
                throw new InvalidOperationException("Inspected Enhanced Decoy patch target changed in " + at + ": " + name.Operand);
            length.OpCode = count == 1 ? OpCodes.Ldc_I4_2 : OpCodes.Ldc_I4_4;
            foreach (var extra in new[] { Instruction.Create(OpCodes.Ldloc_S, local), Instruction.Create(count == 1 ? OpCodes.Ldc_I4_1 : OpCodes.Ldc_I4_3),
                Instruction.Create(OpCodes.Ldtoken, Native(typeName)), Instruction.Create(OpCodes.Call, (MethodReference)name.Previous.Operand),
                Instruction.Create(OpCodes.Stelem_Ref) }) writer.InsertBefore(last, extra);
            scope.Count(counter);
        }
        if (kind == "validate") {
            // launchChaffEffect is the name its ordering check compares.
            var name = sites.SingleOrDefault(i => Name(i, "launchChaffCloud"));
            if (method.Body.CodeSize != 695 || sites.Count != 2 || name == null || !IsTypeOf(name.Previous, "SeaPower.ChaffAttacher") ||
                sites.Count(i => Name(i, "launchChaffEffect")) != 1)
                throw new InvalidOperationException("Inspected Enhanced Decoy hook validator changed");
            OneType(name, "System.Int32", null, "cloud-launch-signature");
            return false;
        }
        // Patches(): each retargeted entry once, at its inspected owner.
        Instruction Site(string name, string owner)
        {
            var found = sites.Where(i => Name(i, name)).ToList();
            if (found.Count != 1 || (owner != null && !IsTypeOf(found[0].Previous, owner)))
                throw new InvalidOperationException("Inspected Enhanced Decoy patch list changed: " + name);
            return found[0];
        }
        if (method.Body.CodeSize != 2271 || sites.Count != 9)
            throw new InvalidOperationException("Inspected Enhanced Decoy patch list changed");
        OneType(Site("readyToLaunch", "SeaPower.WeaponSystemChaff"), "SeaPower.DecoyBand", "ReadyToLaunch", "ready-band-target");
        OneType(Site("launchChaff", "SeaPower.WeaponSystemChaff"), "SeaPower.DecoyBand", null, "launch-band-target");
        AppendType(Site("LaunchChaff", "SeaPower.ObjectBase"), 1, new[] { "System.Boolean" }, "SeaPower.DecoyBand", "manual-band-signature");
        AppendType(Site("launchChaffEffect", "SeaPower.ChaffCloud"), 3,
            new[] { "SeaPower.WeaponSystemChaff", "UnityEngine.GameObject", "UnityEngine.GameObject" }, "System.Int32", "effect-cartridges-signature");
        // A transpiler name is the fourth string of its entry: <target>;
        // prefix; postfix; transpiler; finalizer; newobj PatchSpec; Add.
        Instruction Entry(Instruction transpiler, string target, string prefix, string postfix, string finalizer)
        {
            bool Arg(Instruction i, string value) => value == null ? i.OpCode == OpCodes.Ldnull : Name(i, value);
            var post = transpiler.Previous; var pre = post?.Previous; var call = pre?.Previous;
            var final = transpiler.Next; var spec = final?.Next; var add = spec?.Next;
            var name = call?.Previous?.OpCode == OpCodes.Newarr ? call.Previous.Previous.Previous :
                call?.Previous?.OpCode == OpCodes.Ldloc_S ? call.Previous : null;
            while (name != null && !(name.OpCode == OpCodes.Ldstr && name.Next?.OpCode.Code >= Code.Ldc_I4_0 && name.Next.OpCode.Code <= Code.Ldc_I4_8))
                name = name.Previous;
            if (!IsHooksMethod(call) || !Arg(pre, prefix) || !Arg(post, postfix) || !Arg(final, finalizer) || name == null || !Name(name, target) ||
                !IsTypeOf(name.Previous, null) || name.Previous.Previous.Previous?.OpCode != OpCodes.Ldloc_3 ||
                !(spec.OpCode == OpCodes.Newobj && spec.Operand is MethodReference ctor && ctor.DeclaringType.FullName == "EnhancedDecoyMod.PatchSpec" &&
                  ParameterTypes(ctor, "System.Reflection.MethodBase", "System.String", "System.String", "System.String", "System.String")) ||
                !(add.OpCode == OpCodes.Callvirt && add.Operand is MethodReference adds && adds.Name == "Add") || add.Next?.OpCode != OpCodes.Ldloc_3)
                throw new InvalidOperationException("Inspected Enhanced Decoy patch entry changed: " + transpiler.Operand);
            return add;
        }
        // The same transpiler on a new entry right after the old one, whose
        // own transpiler becomes null: owner, method name, parameter types.
        var handle = (MethodReference)il.First(i => IsTypeOf(i, null)).Operand;
        var typeArray = (TypeReference)il.First(i => i.OpCode == OpCodes.Newarr && (i.Operand as TypeReference)?.FullName == "System.Type").Operand;
        void Move(Instruction transpiler, Instruction add, string owner, string target, string parameter, string count)
        {
            var name = transpiler.Operand;
            var extra = new List<Instruction> { Instruction.Create(OpCodes.Ldloc_3), Instruction.Create(OpCodes.Ldtoken, Native(owner)),
                Instruction.Create(OpCodes.Call, handle), Instruction.Create(OpCodes.Ldstr, target),
                Instruction.Create(parameter == null ? OpCodes.Ldc_I4_0 : OpCodes.Ldc_I4_1), Instruction.Create(OpCodes.Newarr, typeArray) };
            if (parameter != null) extra.AddRange(new[] { Instruction.Create(OpCodes.Dup), Instruction.Create(OpCodes.Ldc_I4_0),
                Instruction.Create(OpCodes.Ldtoken, Native(parameter)), Instruction.Create(OpCodes.Call, handle), Instruction.Create(OpCodes.Stelem_Ref) });
            // add <- newobj <- finalizer <- transpiler <- postfix <- prefix <- Hooks::Method
            extra.AddRange(new[] { Instruction.Create(OpCodes.Call, (MethodReference)transpiler.Previous.Previous.Previous.Operand),
                Instruction.Create(OpCodes.Ldnull), Instruction.Create(OpCodes.Ldnull), Instruction.Create(OpCodes.Ldstr, (string)name),
                Instruction.Create(OpCodes.Ldnull), Instruction.Create(OpCodes.Newobj, (MethodReference)add.Previous.Operand),
                Instruction.Create(OpCodes.Callvirt, (MethodReference)add.Operand) });
            transpiler.OpCode = OpCodes.Ldnull; transpiler.Operand = null;
            var previous = add;
            foreach (var instruction in extra) { writer.InsertAfter(previous, instruction); previous = instruction; }
            scope.Count(count);
        }
        void Off(Instruction transpiler, string count)
        {
            transpiler.OpCode = OpCodes.Ldnull; transpiler.Operand = null;
            scope.Count(count);
        }
        var filters = sites.Where(i => Name(i, "IgnoreFilter")).ToList();
        if (filters.Count != 2) throw new InvalidOperationException("Inspected Enhanced Decoy patch list changed: IgnoreFilter");
        var threat = Site("ThreatFilter", null); var gate = Site("CountermeasureGate", null); var expiry = Site("ExpiryFilter", null);
        var threatAdd = Entry(threat, "OnUpdate", "BeforeChaffUpdate", null, "EndAutoUpdate");
        var gateAdd = Entry(gate, "CheckCountermeasureLock", "CheckCandidate", "CheckedCandidate", null);
        Entry(expiry, "OnUpdateEveryFrame", "MoveCloud", null, null);
        Entry(filters[0], "searchForTarget", "EnterRadar", null, "ExitRadar");
        Entry(filters[1], "createListOfPotentialContacts", null, null, null);
        // OnUpdate and CheckCountermeasureLock(ObjectBase) keep their
        // prefixes, postfix and finalizer; their transpilers move to the
        // method that now holds the code they rewrite.
        Move(threat, threatAdd, "SeaPower.WeaponSystemChaff", "AutoRelease", null, "threat-filter-target");
        Move(gate, gateAdd, "SeaPower.SeekerBase", "CheckCountermeasureLockBody", "SeaPower.ObjectBase", "countermeasure-gate-target");
        // No 261123 method holds the code these two were written for (see
        // the header); the entries keep their prefixes and finalizer.
        Off(expiry, "expiry-filter-off");
        Off(filters[0], "radar-ignore-filter-off");
        return false;
    }

    // The author methods that call the launch and readiness wrappers
    // (5 launches, 4 readiness checks).
    private static readonly string[] EnhancedDecoyOwnLaunches = {
        "EnhancedDecoyMod.AirDecoySwarm::LaunchNext", "EnhancedDecoyMod.ChaffLaunchPolicy::Usable",
        "EnhancedDecoyMod.ChaffLaunchPolicy::TryLaunchSalvo", "EnhancedDecoyMod.ChaffLaunchPolicy::LaunchAmmo",
        "EnhancedDecoyMod.AirDecoyOrders::ProcessQueued", "EnhancedDecoyMod.AirDecoyOrders::Launch",
    };

    // CanLaunch (prefix on launchChaff(DecoyBand)), LauncherReady (postfix on
    // ReadyToLaunch(DecoyBand)) and ManualChaff (prefix on
    // ObjectBase.LaunchChaff(bool, DecoyBand)) gain a "band" parameter, which
    // Harmony fills by name, and return at once for a Flare request: the
    // native code runs as if the mod were absent (ManualChaff's state stays
    // null, which EndManualChaff already accepts). CanLaunch also gains
    // "ref bool __result" and sets it when its salvo ran, so the order log
    // shows ChaffOut. The author's bodies are otherwise unchanged.
    private static void EnhancedDecoyBandHook(AdapterScope scope, MethodDefinition method)
    {
        var il = method.Body.Instructions;
        var writer = method.Body.GetILProcessor();
        string Types(MethodDefinition m) => string.Join(",", m.Parameters.Select(p => p.ParameterType.FullName + " " + p.Name));
        bool Calls(Instruction i, string owner, string name) => i.OpCode == OpCodes.Call && i.Operand is MethodReference m &&
            m.Name == name && m.DeclaringType.FullName == owner;
        void Changed() => throw new InvalidOperationException("Inspected Enhanced Decoy launch hook changed: " + method.Name);
        if (!method.IsStatic || il.Any(i => i.Operand == il[0]) ||
            method.Body.ExceptionHandlers.Count != (method.Name == "ManualChaff" ? 1 : 0) ||
            method.Body.ExceptionHandlers.Any(h => h.TryStart == il[0] || h.HandlerStart == il[0])) Changed();
        var bandType = scope.Module.ImportReference(scope.Native.GetType("SeaPower.DecoyBand"));
        var band = new ParameterDefinition("band", ParameterAttributes.None, bandType);
        Instruction first = il[0];
        if (method.Name == "CanLaunch") {
            if (method.Body.CodeSize != 17 || il.Count != 8 || method.ReturnType.FullName != "System.Boolean" ||
                Types(method) != "SeaPower.WeaponSystemChaff __instance" ||
                il[0].OpCode != OpCodes.Ldarg_0 || !Calls(il[1], "EnhancedDecoyMod.ChaffLaunchPolicy", "TryLaunchSalvo") ||
                il[2].OpCode != OpCodes.Brtrue_S || il[2].Operand != il[6] || il[3].OpCode != OpCodes.Ldarg_0 ||
                !Calls(il[4], EnhancedDecoyHooks, "LaunchAllowed") || il[5].OpCode != OpCodes.Ret ||
                il[6].OpCode != OpCodes.Ldc_I4_0 || il[7].OpCode != OpCodes.Ret)
                Changed();
            var result = new ParameterDefinition("__result", ParameterAttributes.None, new ByReferenceType(scope.Module.TypeSystem.Boolean));
            method.Parameters.Add(band); method.Parameters.Add(result);
            // Salvo ran: *__result = true; return false (skip the original).
            var launched = il[6];
            launched.OpCode = OpCodes.Ldarg; launched.Operand = result;
            var one = Instruction.Create(OpCodes.Ldc_I4_1); var store = Instruction.Create(OpCodes.Stind_I1);
            writer.InsertAfter(launched, one); writer.InsertAfter(one, store); writer.InsertAfter(store, Instruction.Create(OpCodes.Ldc_I4_0));
            scope.Count("salvo-result");
            // Flare: return true (run the original).
            foreach (var extra in new[] { Instruction.Create(OpCodes.Ldarg, band), Instruction.Create(OpCodes.Ldc_I4_1),
                Instruction.Create(OpCodes.Bne_Un_S, first), Instruction.Create(OpCodes.Ldc_I4_1), Instruction.Create(OpCodes.Ret) })
                writer.InsertBefore(first, extra);
        }
        else {
            if (method.Name == "LauncherReady" ? method.Body.CodeSize != 81 || method.ReturnType.FullName != "System.Void" ||
                    Types(method) != "SeaPower.WeaponSystemChaff __instance,System.Boolean& __result" ||
                    il[0].OpCode != OpCodes.Ldarg_0 || !Calls(il[1], "EnhancedDecoyMod.ChaffLaunchPolicy", "ScopeReady")
                : method.Body.CodeSize != 160 || method.ReturnType.FullName != "System.Void" ||
                    Types(method) != "SeaPower.ObjectBase __instance,System.Boolean message,EnhancedDecoyMod.Hooks/ManualChaffState& __state" ||
                    il[0].OpCode != OpCodes.Ldarg_2 || !(il[1].OpCode == OpCodes.Newobj && il[1].Operand is MethodReference ctor &&
                        ctor.DeclaringType.FullName == "EnhancedDecoyMod.Hooks/ManualChaffState") || il[2].OpCode != OpCodes.Stloc_1)
                Changed();
            method.Parameters.Add(band);
            // Flare: return before the author's body.
            foreach (var extra in new[] { Instruction.Create(OpCodes.Ldarg, band), Instruction.Create(OpCodes.Ldc_I4_1),
                Instruction.Create(OpCodes.Bne_Un_S, first), Instruction.Create(OpCodes.Ret) })
                writer.InsertBefore(first, extra);
        }
        scope.Count("flare-pass-through");
    }

    // ldtoken <owner>; call Type::GetTypeFromHandle (any owner when null).
    private static bool IsTypeOf(Instruction handle, string owner)
        => handle?.OpCode == OpCodes.Call && handle.Operand is MethodReference h && h.Name == "GetTypeFromHandle" &&
            h.DeclaringType.FullName == "System.Type" && handle.Previous?.OpCode == OpCodes.Ldtoken &&
            (owner == null || (handle.Previous.Operand as TypeReference)?.FullName == owner);

    // A call operand naming that native method (no resolver needed).
    private static bool SameMethod(MethodReference call, MethodDefinition method)
        => call.Name == method.Name && call.DeclaringType.FullName == method.DeclaringType.FullName && call.HasThis == method.HasThis &&
            call.ReturnType.FullName == method.ReturnType.FullName &&
            call.Parameters.Select(p => p.ParameterType.FullName).SequenceEqual(method.Parameters.Select(p => p.ParameterType.FullName));

    private static bool IsHooksMethod(Instruction call)
        => call?.OpCode == OpCodes.Call && call.Operand is MethodReference m && m.Name == "Method" &&
            m.DeclaringType.FullName == EnhancedDecoyHooks && ParameterTypes(m, "System.Type", "System.String", "System.Type[]");
}
