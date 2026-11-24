// Nested loaders: an admitted plugin that loads companion DLLs from its own
// folder by itself (Assembly.LoadFrom, then AddComponent of their plugin
// types) would bypass SEST's pre-load checks. For a pinned nested loader,
// Prepare checks every companion by hash first, through the same rules as
// any image (holds, native field layout, adapter, native members). A
// companion with a pinned adapter is written to the private cache, and the
// loader preloads it before the entry, so the entry's own "already in the
// AppDomain" lookup takes the adapted image. SEST's own code; no author code
// is copied.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Mono.Cecil;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    // Entry hash -> its companions, in the order the entry loads them.
    internal static readonly Dictionary<string, (string Name, string Hash)[]> NestedLoaderCompanions = new(StringComparer.Ordinal) {
        // Chinese UAV collection (3836566168) UAVWorkshopEntry 965e6049: its
        // UAVWorkshopBootstrap.Start loads these five by name from its folder,
        // unless an assembly of that name is already loaded.
        ["965e604935f6304d4b1f466d11c78512daf3c065ea3bac1f3b6ffe3e12490140"] = [
            ("SPX.PLANMissileMissionControl", "b3d15a9d959dfd66617f45669150f04681acfbeb1ff8e7119081f75dfa13fe2c"),
            ("JiutianReferenceUnits", "230f38f674fb4ba54c0c4ca265c8723fb1818af2c108322b069fe179f70fc5f8"),
            ("WZ7GearRuntime", "08ec072b332a6877ab9c951c32f5f4a24c4a44d91307c63dc8c03cfeb9ff5e62"),
            ("CCA53536.Runtime", "dfe4b0a507824155d55cfce10491e483e29ae0a2f8a08c52c7076824a2a2b377"),
            ("MetricRadiusCompat", "f99bd4564564bc8c2f1a7cb2ea6965afeae0a0bc8044f4ac69c428519e02eeae"),
        ],
    };

    private static readonly Dictionary<string, List<string>> companionPreloads = new(StringComparer.OrdinalIgnoreCase);

    // The companion images the loader must load, in order, before the entry
    // at source: empty unless a companion was adapted. Up to the last adapted
    // one, unadapted companions are listed by their Workshop path, as the
    // entry itself would load them.
    public static IReadOnlyList<string> CompanionPreloads(string source)
    {
        lock (pathLock) return companionPreloads.TryGetValue(Path.GetFullPath(source), out var list) ? list.ToArray() : Array.Empty<string>();
    }

    // Null when every companion passes, else "<name> <reason>".
    private static string PrepareCompanions(string source, (string Name, string Hash)[] companions, ModuleDefinition native,
        string nativePath, string cacheRoot, Action<string> log, List<string> preloads)
    {
        string folder = Path.GetDirectoryName(source);
        var images = new List<(string Path, string Prepared)>();
        int lastAdapted = -1;
        // Logged only once every companion passed, so a refusal stays one line.
        var adapted = new List<string>();
        foreach (var (name, pin) in companions) {
            string path = Path.Combine(folder, name + ".dll");
            if (!File.Exists(path)) return name + " is missing";
            string hash = Hash(path);
            if (hash != pin) return name + " (" + hash.Substring(0, 8) + ") is not the reviewed image " + pin.Substring(0, 8);
            if (StartupHolds.TryGetValue(hash, out var held)) return name + " is held (" + held + ")";
            if (IsNativePeLibrary(path)) return name + " is not a managed image";
            using var resolver = new DefaultAssemblyResolver();
            foreach (var directory in new[] { folder, Path.GetDirectoryName(nativePath),
                Path.GetDirectoryName(typeof(HarmonyLib.Harmony).Assembly.Location),
                Path.GetDirectoryName(typeof(BetaAssemblyPolicy).Assembly.Location) })
                if (!String.IsNullOrEmpty(directory)) resolver.AddSearchDirectory(directory);
            using var module = ModuleDefinition.ReadModule(path, new ReaderParameters {
                InMemory = true, ReadingMode = ReadingMode.Deferred, AssemblyResolver = resolver });
            if (module.Assembly.Name.Name != name) return name + " has assembly name " + module.Assembly.Name.Name;
            var adapter = AdapterFor(hash);
            var bad = InvalidNativeFields(module, native);
            if (adapter != null) bad.RemoveAll(finding => adapter.AcceptedNativeFields.Contains(finding));
            if (bad.Count != 0) return name + ": " + String.Join("; ", bad.Take(4));
            string audit;
            try { audit = AdaptCapturedImage(module, native, hash); }
            catch (Exception e) { return name + " adapter refused: " + e.Message; }
            var missing = UnresolvedNativeMembers(module, native);
            if (missing.Count != 0)
                return name + " names " + missing.Count + " game member(s) this build does not have: " + String.Join("; ", missing.Take(4));
            string prepared = path;
            if (audit != null) {
                prepared = WritePrivateImage(module, native, path, Path.Combine(cacheRoot, "beta-api-r16-261123", hash));
                adapted.Add("ADAPTED " + name + " in private cache: " + audit + "; companion of " + Path.GetFileName(source)
                    + ", preloaded before it; original Workshop DLL and asset paths preserved.");
                lastAdapted = images.Count;
            }
            images.Add((path, prepared));
        }
        foreach (string line in adapted) log(line);
        preloads.AddRange(images.Take(lastAdapted + 1).Select(image => image.Prepared));
        return null;
    }
}
