using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using AnchorChain;
using Mono.Cecil;

// R16 (24 Nov 2026) loader interoperability: hash-pinned BepInEx-only Workshop
// plugins started by SEST's loader, the duplicate-assembly gate, R.A.T.S.
// Keel's holds and the Chinese UAV pack's companion preload. Pure metadata
// and policy checks; no plugin entry point or Unity object runs.
static partial class BetaApiTests
{
    const BindingFlags LoaderAll = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance;
    const string RadarPowerHash = "7a50ebd334e1b73384ebe01d03a63d2719f1a5542db4691228c1fe515de223a0";
    const string TubeLaunchHash = "d7efad594edb8cd2c97e95f991cc462fe5c774f58054a783d5ec7924c280edb7";
    const string EditorHash = "be708ae173363bcb0d78e9bf139faa0a8fe4211ef1ef37ffc7141aa559dd4269";
    const string TacMapHash = "bdc418647e5a4d9dc98d532ea813d4a9158d9171e70ffb753e39bfca1152b142";
    const string UavEntryHash = "965e604935f6304d4b1f466d11c78512daf3c065ea3bac1f3b6ffe3e12490140";
    const string JiutianHash = "230f38f674fb4ba54c0c4ca265c8723fb1818af2c108322b069fe179f70fc5f8";

    static object PolicyCall(string name, params object[] arguments)
    {
        var method = typeof(BetaAssemblyPolicy).GetMethod(name, LoaderAll) ?? throw new Exception("Missing policy member " + name);
        try { return method.Invoke(null, arguments); }
        catch (TargetInvocationException ex) { throw new Exception(name + " failed: " + ex.InnerException); }
    }
    static readonly Type LoaderRunner = typeof(BetaAssemblyPolicy).Assembly.GetType("AnchorChain.WorkshopBepInRunner", true);
    static object PolicyField(string name) => typeof(BetaAssemblyPolicy).GetField(name, LoaderAll).GetValue(null);
    static T Member<T>(object instance, string name) => (T)instance.GetType().GetField(name, LoaderAll).GetValue(instance);
    static string ShaOf(string path)
    {
        using var stream = File.OpenRead(path); using var sha = System.Security.Cryptography.SHA256.Create();
        return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
    }
    static List<string> PrepareLogged(R6Context context, string source, out string prepared)
    {
        var messages = new List<string>();
        prepared = BetaAssemblyPolicy.Prepare(source, context.Native, context.Cache, messages.Add);
        foreach (string message in messages) Console.WriteLine(message);
        return messages;
    }

    static void R6_WorkshopBepIn(R6Context context)
    {
        var pins = (System.Collections.IDictionary)PolicyField("WorkshopBepInPlugins");
        Check(pins.Count == 4 && new[] { RadarPowerHash, TubeLaunchHash, EditorHash, TacMapHash }.All(pins.Contains),
            "Exactly the four reviewed BepInEx-only images are pinned: Echidna radar power, Echidna tube launch, Ghost Shark editor, Better Tac Map");
        var host = (Dictionary<string, string>)PolicyField("HostSatisfiedDependencies");
        Check(host.Count == 1 && host.ContainsKey("dev.sewerlabs.seapowerkeel.stub"),
            "The only host-satisfied dependency is R.A.T.S. Keel's starter marker");
        var bepinBase = typeof(BepInEx.BaseUnityPlugin);
        foreach (var (relative, hash, guid, typeName) in new[] {
            ("3843495110/EchidnaRadarPower.dll", RadarPowerHash, "ran.echidna.radarpower", "Ran.Echidna.EchidnaRadarPower"),
            ("3843501029/EchidnaTubeLaunch.dll", TubeLaunchHash, "ran.echidna.tubelaunch", "Ran.Echidna.EchidnaTubeLaunch"),
            ("3843501029/GhostSharkEditor.dll", EditorHash, "ran.ghostshark.editor", "GhostShark.Editor.GhostSharkEditor") }) {
            string source = Path.Combine(context.Workshop, relative);
            Check(ShaOf(source) == hash, "Captured image is the pinned one: " + relative);
            byte[] before = File.ReadAllBytes(source);
            var messages = PrepareLogged(context, source, out string prepared);
            Check(prepared == source && messages.Count == 0,
                "Pinned BepInEx plugin is admitted unchanged, with no rewrite and no log line, from its Workshop path: " + relative + " -> " + String.Join(" | ", messages));
            Check(before.SequenceEqual(File.ReadAllBytes(source)), "Author bytes retained: " + relative);
            var pin = PolicyCall("WorkshopBepInFor", hash);
            Check(Member<string>(pin, "Guid") == guid && Member<string>(pin, "TypeName") == typeName && Member<bool>(pin, "KeelStarterMarker"),
                "Pin records the plugin GUID, type and its Keel starter marker: " + relative);
            // As Main.LoadPluginsCore after Assembly.LoadFile: the pinned type exists and is a BepInEx plugin.
            var type = Assembly.LoadFile(prepared).GetType(typeName, true);
            Check(type.IsSubclassOf(bepinBase) && !type.IsAbstract, "Pinned plugin type loads and derives from BaseUnityPlugin: " + typeName);
        }
        // Start order: radar power, then tube launch, then the editor.
        var order = LoaderRunner.GetMethod("Order", LoaderAll);
        var after = new Dictionary<string, string[]> { ["ran.ghostshark.editor"] = new[] { "ran.echidna.radarpower" },
            ["ran.echidna.tubelaunch"] = new[] { "ran.echidna.radarpower" }, ["ran.echidna.radarpower"] = new string[0] };
        var skipped = new Dictionary<string, string>();
        var none = new HashSet<string>();
        var started = (List<string>)order.Invoke(null, new object[] { after, skipped, none });
        Check(started.SequenceEqual(new[] { "ran.echidna.radarpower", "ran.echidna.tubelaunch", "ran.ghostshark.editor" }) && skipped.Count == 0,
            "Start order is radar power, then tube launch, then the editor (actual: " + String.Join(", ", started) + ")");
        after.Remove("ran.echidna.radarpower"); skipped.Clear();
        started = (List<string>)order.Invoke(null, new object[] { after, skipped, none });
        Check(started.Count == 0 && skipped.Count == 2 && skipped.Values.All(v => v.StartsWith("needs ran.echidna.radarpower")),
            "Echidna not ticked: each Ghost Shark plugin gets exactly one 'needs ran.echidna.radarpower' line");
        skipped.Clear();
        started = (List<string>)order.Invoke(null, new object[] { after, skipped, new HashSet<string> { "ran.echidna.radarpower" } });
        Check(started.SequenceEqual(new[] { "ran.echidna.tubelaunch", "ran.ghostshark.editor" }) && skipped.Count == 0,
            "Radar power already started by BepInEx (in Chainloader.PluginInfos) counts as met: both dependents start (actual: " + String.Join(", ", started) + "; skipped: " + String.Join(" | ", skipped.Values) + ")");
        skipped.Clear();
        started = (List<string>)order.Invoke(null, new object[] { new Dictionary<string, string[]> { ["a"] = new[] { "b" }, ["b"] = new[] { "a" } }, skipped, none });
        Check(started.Count == 0 && skipped.Count == 2 && skipped.Values.All(v => v == "dependency cycle"), "A dependency cycle ends within the loop budget");
        var keel = LoaderRunner.GetMethod("KeelRunning", LoaderAll);
        Check(keel.Invoke(null, new object[] { new[] { "mscorlib", "SeaPowerKeel.Patcher" }, new string[0] }) != null &&
            keel.Invoke(null, new object[] { new string[0], new[] { "dev.sewerlabs.seapowerkeel.stub" } }) != null &&
            keel.Invoke(null, new object[] { new[] { "mscorlib", "SensorView" }, new[] { "io.github.seapower_modders.anchorchain" } }) == null,
            "Keel counts as running only when its loader, patcher or stub is loaded or its starter GUID is registered");
        Check((string)LoaderRunner.GetField("HostName", LoaderAll).GetValue(null) == "SEST Workshop BepInEx plugins",
            "Runner host object has its own SEST name");

        // Refusals on the pinned images' own metadata, one reason each.
        string radar = Path.Combine(context.Workshop, "3843495110/EchidnaRadarPower.dll");
        string tube = Path.Combine(context.Workshop, "3843501029/EchidnaTubeLaunch.dll");
        string Refusal(string source, string hash, Action<ModuleDefinition> change)
        {
            using var module = ModuleDefinition.ReadModule(source, new ReaderParameters { InMemory = true, AssemblyResolver = context.Resolver });
            change(module);
            return (string)PolicyCall("WorkshopBepInRefusal", module, source, PolicyCall("WorkshopBepInFor", hash));
        }
        TypeDefinition Plugin(ModuleDefinition m) => Types(m.Types).Single(t => t.CustomAttributes.Any(a => a.AttributeType.FullName == "BepInEx.BepInPlugin"));
        CustomAttribute Attribute(ModuleDefinition m, string name) => Plugin(m).CustomAttributes.First(a => a.AttributeType.FullName == name);
        Check(Refusal(radar, RadarPowerHash, m => { }) == null && Refusal(tube, TubeLaunchHash, m => { }) == null, "Unchanged pinned metadata is admitted");
        var cases = new (string Why, string Source, string Hash, Action<ModuleDefinition> Change, string Expected)[] {
            ("metadata differs", radar, RadarPowerHash, m => { var a = Attribute(m, "BepInEx.BepInPlugin"); a.ConstructorArguments[2] = new CustomAttributeArgument(a.ConstructorArguments[2].Type, "0.3.0"); }, "differs from the pin"),
            ("extra dependency", radar, RadarPowerHash, m => { var a = Attribute(m, "BepInEx.BepInDependency"); var copy = new CustomAttribute(a.Constructor);
                copy.ConstructorArguments.Add(new CustomAttributeArgument(a.ConstructorArguments[0].Type, "other.unreviewed.plugin")); copy.ConstructorArguments.Add(a.ConstructorArguments[1]);
                Plugin(m).CustomAttributes.Add(copy); }, "unpinned dependency other.unreviewed.plugin"),
            ("minimum above provider", tube, TubeLaunchHash, m => { var a = Plugin(m).CustomAttributes.Single(x => x.AttributeType.FullName == "BepInEx.BepInDependency" && x.ConstructorArguments[1].Value is string);
                a.ConstructorArguments[1] = new CustomAttributeArgument(a.ConstructorArguments[1].Type, "0.3.0"); }, "0.2.9 is below its minimum 0.3.0"),
            ("BepInProcess", radar, RadarPowerHash, m => { var bepin = m.AssemblyReferences.Single(r => r.Name == "BepInEx");
                var ctor = new MethodReference(".ctor", m.TypeSystem.Void, new TypeReference("BepInEx", "BepInProcess", m, bepin)) { HasThis = true };
                ctor.Parameters.Add(new ParameterDefinition(m.TypeSystem.String)); Plugin(m).CustomAttributes.Add(new CustomAttribute(ctor)); }, "BepInEx.BepInProcess is not supported"),
            ("BepInIncompatibility", radar, RadarPowerHash, m => { var bepin = m.AssemblyReferences.Single(r => r.Name == "BepInEx");
                var ctor = new MethodReference(".ctor", m.TypeSystem.Void, new TypeReference("BepInEx", "BepInIncompatibility", m, bepin)) { HasThis = true };
                ctor.Parameters.Add(new ParameterDefinition(m.TypeSystem.String)); Plugin(m).CustomAttributes.Add(new CustomAttribute(ctor)); }, "BepInEx.BepInIncompatibility is not supported"),
            ("references Keel", radar, RadarPowerHash, m => m.AssemblyReferences.Add(new AssemblyNameReference("SeaPowerKeel", new Version(1, 0))), "references another loader's API (SeaPowerKeel)"),
            ("references Anchor Chain", radar, RadarPowerHash, m => m.AssemblyReferences.Add(new AssemblyNameReference("AnchorChain", new Version(1, 2))), "references another loader's API (AnchorChain)"),
            ("second plugin type", radar, RadarPowerHash, m => { var extra = new TypeDefinition("Extra", "Second", Mono.Cecil.TypeAttributes.Public, Plugin(m).BaseType);
                extra.CustomAttributes.Add(new CustomAttribute(Attribute(m, "BepInEx.BepInPlugin").Constructor)); m.Types.Add(extra); }, "2 BepInPlugin types"),
            ("Keel's own image", radar, RadarPowerHash, m => m.Assembly.Name.Name = "SeaPowerKeel.Stub", "another mod loader's own image"),
        };
        foreach (var c in cases) {
            string refusal = Refusal(c.Source, c.Hash, c.Change);
            Check(refusal != null && refusal.Contains(c.Expected), "Pinned image refused when " + c.Why + " (" + refusal + ")");
        }
        // Wrong file name or folder: the exact pinned bytes elsewhere get one line.
        foreach (var (folder, file, expected) in new[] { ("elsewhere", "EchidnaRadarPower.dll", "not inside Workshop folder 3843495110"),
            ("3843495110", "RadarPower.dll", "pinned as EchidnaRadarPower.dll") }) {
            string copy = Path.Combine(context.Cache, "bepin-" + folder, folder, file);
            Directory.CreateDirectory(Path.GetDirectoryName(copy)); File.Copy(radar, copy, true);
            var messages = PrepareLogged(context, copy, out string prepared);
            Check(prepared == null && messages.Count == 1 && messages[0].StartsWith("SKIPPED before CLR load: " + file + "; ") && messages[0].Contains(expected),
                "Pinned bytes outside their pinned place are held with one line: " + expected);
        }
        // An unpinned BepInEx-only image keeps today's silent library skip.
        var silent = PrepareLogged(context, Path.Combine(context.Workshop, "3836566168/JiutianReferenceUnits.dll"), out string unpinned);
        Check(unpinned == null && silent.Count == 0, "Unpinned BepInEx-only images are not started and log nothing (Jiutian loads only through its own entry)");

        // Better Tac Map: pinned for start; its 261123 rewrite is its own adapter.
        string tacMap = Path.Combine(context.Workshop, "3768036424/BetterTacMap.dll");
        Check(ShaOf(tacMap) == TacMapHash && Refusal(tacMap, TacMapHash, m => { }) == null,
            "Better Tac Map 0.2.0 (toemel.bettertacmap, BetterTacMap.BetterTacMapMod, no dependencies) matches its start pin");
        var tacMessages = PrepareLogged(context, tacMap, out string tacPrepared);
        if (PolicyCall("AdapterFor", TacMapHash) != null)
            Check(tacPrepared != null && tacPrepared != tacMap && tacMessages.Count == 1 && tacMessages[0].StartsWith("ADAPTED BetterTacMap"),
                "With its pinned adapter, Better Tac Map is admitted as a private image and started by SEST's loader");
        if (tacPrepared != null && tacPrepared != tacMap) {
            // A byte-identical second copy maps to the same cache image, which may
            // already be loaded (locked on Windows): it is reused, not rewritten,
            // so the duplicate gate reports the copy with its one line.
            string tacCopy = Path.Combine(context.Cache, "dup-tac", "3768036424", "BetterTacMap.dll");
            Directory.CreateDirectory(Path.GetDirectoryName(tacCopy)); File.Copy(tacMap, tacCopy, true);
            DateTime written = File.GetLastWriteTimeUtc(tacPrepared);
            var copyMessages = PrepareLogged(context, tacCopy, out string copyPrepared);
            Check(copyPrepared == tacPrepared && File.GetLastWriteTimeUtc(tacPrepared) == written && !File.Exists(tacPrepared + ".tmp"),
                "A byte-identical second Better Tac Map reuses the cache image this process wrote, with no rewrite and no .tmp file");
            var gateType = typeof(BetaAssemblyPolicy).GetNestedType("DuplicateGate", LoaderAll);
            object gate = Activator.CreateInstance(gateType, true); var gateLines = new List<string>();
            var admit = gateType.GetMethod("Admit", LoaderAll);
            Check((bool)admit.Invoke(gate, new object[] { tacMap, tacPrepared, (Action<string>)gateLines.Add }) &&
                !(bool)admit.Invoke(gate, new object[] { tacCopy, copyPrepared, (Action<string>)gateLines.Add }) &&
                gateLines.Count == 1 && gateLines[0].StartsWith("SKIPPED duplicate before CLR load: 3768036424\\BetterTacMap.dll is byte-identical to 3768036424\\BetterTacMap.dll"),
                "The adapted duplicate then gets the gate's one line, not a load error: " + String.Join(" | ", gateLines));
        }
        else
            Check(tacPrepared == null && tacMessages.Count == 1 && tacMessages[0].StartsWith("SKIPPED before CLR load: BetterTacMap.dll; names ") &&
                tacMessages[0].Contains("EffectiveMaxLaunchRange"),
                "Without its adapter, Better Tac Map's missing 261123 members hold it with one line");

        // R.A.T.S. Keel's patcher in BepInEx/patchers: one warning from the
        // bootstrap (a takeover stops SEST's loader before Main runs), read only.
        var bootstrap = Assembly.LoadFrom(Path.Combine(Path.GetDirectoryName(typeof(BetaAssemblyPolicy).Assembly.Location), "SEST.BetaSafeBootstrap.dll"))
            .GetType("SEST.BetaAnchor.Bootstrap", true).GetMethod("KeelPatcherWarning", LoaderAll)
            ?? throw new Exception("Missing bootstrap member KeelPatcherWarning");
        Check(typeof(BetaAssemblyPolicy).GetMethod("KeelPatcherWarning", LoaderAll) == null, "The Keel patcher warning has one home, the bootstrap");
        string patchers = Path.Combine(context.Cache, "bepinex-patchers");
        Directory.CreateDirectory(patchers);
        Check(bootstrap.Invoke(null, new object[] { patchers }) == null, "No Keel warning without its patcher");
        File.WriteAllBytes(Path.Combine(patchers, "SeaPowerKeel.Patcher.dll"), new byte[] { 1, 2, 3 });
        string warning = (string)bootstrap.Invoke(null, new object[] { patchers });
        Check(warning != null && warning.Contains("SeaPowerKeel.Patcher.dll") && warning.Contains("KeelSetup.exe Restore") && !warning.Contains("\n") &&
            File.ReadAllBytes(Path.Combine(patchers, "SeaPowerKeel.Patcher.dll")).SequenceEqual(new byte[] { 1, 2, 3 }),
            "Keel's installed patcher gives one warning line and is left untouched");
    }

    static void R6_DuplicateGate(R6Context context)
    {
        var gateType = typeof(BetaAssemblyPolicy).GetNestedType("DuplicateGate", LoaderAll);
        object gate = Activator.CreateInstance(gateType, true);
        var admit = gateType.GetMethod("Admit", LoaderAll); var release = gateType.GetMethod("Release", LoaderAll);
        var messages = new List<string>();
        bool Admit(string path) => (bool)admit.Invoke(gate, new object[] { path, path, (Action<string>)messages.Add });
        string first = Path.Combine(context.Workshop, "3822119548/SensorView.dll"), second = Path.Combine(context.Workshop, "3838468198/SensorView.dll");
        Check(ShaOf(first) == ShaOf(second), "Both captured Sensor View items ship the same SensorView.dll");
        Check(Admit(first) && messages.Count == 0, "The first SensorView in Mod Manager order is admitted");
        Check(!Admit(second) && messages.Count == 1 && messages[0].StartsWith("SKIPPED duplicate before CLR load: 3838468198\\SensorView.dll is byte-identical to 3822119548\\SensorView.dll (dc3976dc)"),
            "The byte-identical later copy is skipped with one line: " + String.Join(" | ", messages));
        string variant = Path.Combine(context.Cache, "dup-variant", "3899999999", "SensorView.dll");
        Directory.CreateDirectory(Path.GetDirectoryName(variant));
        using (var module = ModuleDefinition.ReadModule(first, new ReaderParameters { InMemory = true, AssemblyResolver = context.Resolver })) { module.Mvid = Guid.NewGuid(); module.Write(variant); }
        messages.Clear();
        Check(!Admit(variant) && messages.Count == 1 && messages[0].Contains("is a second SensorView; 3822119548\\SensorView.dll (dc3976dc) loads, earlier in Mod Manager order"),
            "A different image with the same assembly name is skipped with one line naming the copy that loads");
        release.Invoke(gate, new object[] { first }); messages.Clear();
        Check(Admit(second) && messages.Count == 0, "When the first copy fails to load, the gate releases its name and a later good copy may load");
        string garbage = Path.Combine(context.Cache, "dup-variant", "garbage.dll"); File.WriteAllText(garbage, "not an assembly"); messages.Clear();
        Check(!Admit(garbage) && messages.Count == 1 && messages[0].Contains("assembly name unreadable"), "An unreadable name fails closed with one line");
        string rigging = Path.Combine(context.Workshop, "3833019654/SeaPowerRigging.dll"); messages.Clear();
        Check(Admit(rigging) && messages.Count == 0, "The shared reviewed Rigging copy passes the gate once");
        Check(!Admit(Path.Combine(context.Workshop, "3826122523/SeaPowerRigging.dll")) && messages.Count == 1,
            "A second Rigging copy never reaches the CLR beside the first");
        // A same-named assembly BepInEx or another loader loaded first (a copy in BepInEx/plugins) is the one copy.
        var elsewhere = gateType.GetMethod("LoadedElsewhere", LoaderAll);
        string tacMap = Path.Combine(context.Workshop, "3768036424/BetterTacMap.dll");
        string line = (string)elsewhere.Invoke(null, new object[] { tacMap, tacMap, new[] { "mscorlib", "BetterTacMap" } });
        Check(line != null && line.StartsWith("SKIPPED duplicate before CLR load: 3768036424\\BetterTacMap.dll; an assembly named BetterTacMap is already loaded"),
            "A Workshop copy whose assembly name is already loaded in the process is not loaded beside it: " + line);
        Check(elsewhere.Invoke(null, new object[] { tacMap, tacMap, new[] { "mscorlib", "SensorView" } }) == null &&
            elsewhere.Invoke(null, new object[] { garbage, garbage, new[] { "BetterTacMap" } }) == null,
            "A free name, or an unreadable one (already refused by Admit), gives no line");
        // "First in Mod Manager order" is a list order, not HashSet enumeration.
        Check(typeof(AnchorChainLoader).GetField("_allDirectories", LoaderAll).FieldType == typeof(List<DirectoryInfo>),
            "The loader keeps ticked folders in a list, in Mod Manager order");
        // Sensor View's add-ons still load beside the one SensorView.
        foreach (string relative in new[] { "3838471268/SensorView.Satellite.dll", "3838472767/SensorView.ColourBlindPalette.dll", "3822119548/SensorView.dll" }) {
            var lines = PrepareLogged(context, Path.Combine(context.Workshop, relative), out string prepared);
            Check(prepared == Path.Combine(context.Workshop, relative) && lines.Count == 0, "Sensor View image admitted unchanged: " + relative);
        }
    }

    static void R6_KeelHolds(R6Context context)
    {
        foreach (string relative in new[] { "3835527459/SeaPowerKeel.dll", "3835527459/SeaPowerKeel.Patcher.dll", "3835527459/copy-to-BepInEx-plugins/SeaPowerKeel.Stub.dll" }) {
            string source = Path.Combine(context.Workshop, relative); byte[] before = File.ReadAllBytes(source);
            var messages = PrepareLogged(context, source, out string prepared);
            Check(prepared == null && messages.Count == 1 && messages[0].StartsWith("SKIPPED before CLR load: " + Path.GetFileName(source) + "; R.A.T.S. Keel ") &&
                messages[0].Contains("not admitted under SEST") && messages[0].Contains("held by design") && !messages[0].Contains("author port"),
                "Keel image held by hash with one by-design line: " + relative);
            Check(before.SequenceEqual(File.ReadAllBytes(source)), "Keel file left untouched: " + relative);
            Check(!AppDomain.CurrentDomain.GetAssemblies().Any(a => a.GetName().Name == Path.GetFileNameWithoutExtension(source)), "Keel image never enters the CLR: " + relative);
        }
        var holds = (Dictionary<string, string>)PolicyField("StartupHolds");
        Check(holds.Count == 11 && holds.Count(h => h.Value.StartsWith("R.A.T.S. Keel ")) == 3, "StartupHolds: the eight author-verdict holds plus Keel's three images");
        // A re-uploaded Keel image (new hash) is still never admitted.
        string changed = Path.Combine(context.Cache, "keel-changed", "SeaPowerKeel.Stub.dll");
        Directory.CreateDirectory(Path.GetDirectoryName(changed));
        using (var module = ModuleDefinition.ReadModule(Path.Combine(context.Workshop, "3835527459/copy-to-BepInEx-plugins/SeaPowerKeel.Stub.dll"), new ReaderParameters { InMemory = true, AssemblyResolver = context.Resolver })) {
            module.Mvid = Guid.NewGuid(); module.Write(changed);
        }
        var lines = PrepareLogged(context, changed, out string admitted);
        Check(admitted == null && lines.Count == 1 && lines[0].Contains("R.A.T.S. Keel's own loader image, which SEST does not start"),
            "A Keel image at any other hash is held by name with one line");
        // Sensor View's ExtendedGuidance add-on shares the EG profile switch.
        string addOn = Path.Combine(context.Workshop, "3838469336/SensorView.ExtendedGuidance.dll");
        lines = PrepareLogged(context, addOn, out admitted);
        Check(admitted == null && lines.Count == 1 && lines[0].StartsWith("SKIPPED before CLR load: SensorView.ExtendedGuidance.dll; ") && lines[0].Contains("SEST profile"),
            "Sensor View's ExtendedGuidance add-on is held with ExtendedGuidance, with one line");
    }

    static void R6_UavCompanions(R6Context context)
    {
        string folder = Path.Combine(context.Workshop, "3836566168"), entry = Path.Combine(folder, "UAVWorkshopEntry.dll");
        Check(ShaOf(entry) == UavEntryHash, "Captured UAV entry is the pinned nested loader");
        var companions = (System.Collections.IDictionary)PolicyField("NestedLoaderCompanions");
        var list = ((ValueTuple<string, string>[])companions[UavEntryHash]);
        Check(list.Select(c => c.Item1).SequenceEqual(new[] { "SPX.PLANMissileMissionControl", "JiutianReferenceUnits", "WZ7GearRuntime", "CCA53536.Runtime", "MetricRadiusCompat" }) &&
            list.All(c => ShaOf(Path.Combine(folder, c.Item1 + ".dll")) == c.Item2),
            "The five companions are pinned by hash in the entry's own load order");
        var before = Directory.GetFiles(folder).ToDictionary(f => f, File.ReadAllBytes);
        var messages = PrepareLogged(context, entry, out string prepared);
        Check(prepared == entry && messages.All(m => m.StartsWith("ADAPTED ")), "The UAV entry is admitted after all five companions pass: " + String.Join(" | ", messages));
        var preloads = BetaAssemblyPolicy.CompanionPreloads(entry);
        if (PolicyCall("AdapterFor", JiutianHash) != null) {
            Check(preloads.Count == 2 && preloads[0] == Path.Combine(folder, "SPX.PLANMissileMissionControl.dll") && preloads[1] != Path.Combine(folder, "JiutianReferenceUnits.dll") &&
                File.Exists(preloads[1]) && Path.GetFileName(preloads[1]) == "JiutianReferenceUnits.dll" && messages.Count(m => m.StartsWith("ADAPTED JiutianReferenceUnits")) == 1,
                "Jiutian is adapted in the private cache and preloaded, after SPX, before the entry");
            using var module = ModuleDefinition.ReadModule(preloads[1], new ReaderParameters { AssemblyResolver = context.Resolver });
            using var game = ModuleDefinition.ReadModule(context.Native);
            var unresolved = (List<string>)PolicyCall("UnresolvedNativeMembers", module, game);
            Check(unresolved.Count == 0, "The preloaded Jiutian image names only game members 261123 has (" + String.Join("; ", unresolved) + ")");
        } else
            Check(preloads.Count == 0 && messages.Count == 0, "With no companion adapter, nothing is preloaded and the entry loads its own companions");
        Check(before.All(f => f.Value.SequenceEqual(File.ReadAllBytes(f.Key))), "Author files in the UAV folder are untouched");
        Check(!AppDomain.CurrentDomain.GetAssemblies().Any(a => list.Any(c => c.Item1 == a.GetName().Name) || a.GetName().Name == "UAVWorkshopEntry"),
            "Prepare loads neither the entry nor a companion into the CLR");
        // A changed or missing companion holds the entry with one line.
        string copy = Path.Combine(context.Cache, "uav-copy", "3836566168");
        Directory.CreateDirectory(copy);
        foreach (string file in Directory.GetFiles(folder)) File.Copy(file, Path.Combine(copy, Path.GetFileName(file)), true);
        string copiedEntry = Path.Combine(copy, "UAVWorkshopEntry.dll");
        Check(BetaAssemblyPolicy.Prepare(copiedEntry, context.Native, context.Cache, _ => { }) == copiedEntry, "An identical copy of the pack is admitted");
        File.Copy(Path.Combine(folder, "MetricRadiusCompat.dll"), Path.Combine(copy, "WZ7GearRuntime.dll"), true);
        var changed = PrepareLogged(context, copiedEntry, out string held);
        Check(held == null && changed.Count == 1 && changed[0].StartsWith("SKIPPED before CLR load: UAVWorkshopEntry.dll; companion WZ7GearRuntime (f99bd456) is not the reviewed image 08ec072b"),
            "A changed companion holds the nested loader with one line");
        File.Copy(Path.Combine(folder, "WZ7GearRuntime.dll"), Path.Combine(copy, "WZ7GearRuntime.dll"), true);
        File.Delete(Path.Combine(copy, "CCA53536.Runtime.dll"));
        changed = PrepareLogged(context, copiedEntry, out held);
        Check(held == null && changed.Count == 1 && changed[0] == "SKIPPED before CLR load: UAVWorkshopEntry.dll; companion CCA53536.Runtime is missing. Data retained.",
            "A missing companion holds the nested loader with one line");
    }
}
