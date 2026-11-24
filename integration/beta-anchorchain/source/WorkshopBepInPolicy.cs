// SEST's own admission of hash-pinned Workshop BepInEx plugins (images with a
// BepInPlugin and no ACPlugin). BepInEx never scans Workshop folders, so
// these start only when SEST's loader starts them. R.A.T.S. Keel is named
// here only by its public identifiers, so SEST can recognise it, refuse its
// images and say so; no Keel code is used or copied.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Mono.Cecil;

namespace AnchorChain;

internal sealed class WorkshopBepInPlugin
{
    internal string WorkshopId, File, Guid, Name, Version, TypeName;
    // GUIDs this plugin starts after; each must be another pin.
    internal string[] After = [];
    // True when the image names R.A.T.S. Keel's starter as a dependency.
    internal bool KeelStarterMarker;
}

public static partial class BetaAssemblyPolicy
{
    internal const string KeelStubGuid = "dev.sewerlabs.seapowerkeel.stub";

    // Exact author images reviewed against 0.9.3-261123 (ea653e49). A new
    // upload changes the hash and is not started until it is reviewed and
    // pinned again; its unit data still loads.
    internal static readonly Dictionary<string, WorkshopBepInPlugin> WorkshopBepInPlugins = new(StringComparer.Ordinal) {
        // RAN Echidna SRT-01: ECM mast power 0.2.9 (24 Nov review).
        ["7a50ebd334e1b73384ebe01d03a63d2719f1a5542db4691228c1fe515de223a0"] = new() { WorkshopId = "3843495110",
            File = "EchidnaRadarPower.dll", Guid = "ran.echidna.radarpower", Name = "Echidna ECM mast power", Version = "0.2.9",
            TypeName = "Ran.Echidna.EchidnaRadarPower", KeelStarterMarker = true },
        // RAN Ghost Shark XL-AUV: tube launch 0.2.2 and Mission Editor 0.6.12.
        ["d7efad594edb8cd2c97e95f991cc462fe5c774f58054a783d5ec7924c280edb7"] = new() { WorkshopId = "3843501029",
            File = "EchidnaTubeLaunch.dll", Guid = "ran.echidna.tubelaunch", Name = "Echidna tube launch", Version = "0.2.2",
            TypeName = "Ran.Echidna.EchidnaTubeLaunch", After = ["ran.echidna.radarpower"], KeelStarterMarker = true },
        ["be708ae173363bcb0d78e9bf139faa0a8fe4211ef1ef37ffc7141aa559dd4269"] = new() { WorkshopId = "3843501029",
            File = "GhostSharkEditor.dll", Guid = "ran.ghostshark.editor", Name = "Ghost Shark Mission Editor", Version = "0.6.12",
            TypeName = "GhostShark.Editor.GhostSharkEditor", After = ["ran.echidna.radarpower"], KeelStarterMarker = true },
        // Better Tac Map 0.2.0 (bdc41864). Its 261123 rewrite is a pinned
        // adapter (AssemblyAdapters.BetterTacMap.cs); without that adapter
        // the native-member check holds it with one line, as any image.
        ["bdc418647e5a4d9dc98d532ea813d4a9158d9171e70ffb753e39bfca1152b142"] = new() { WorkshopId = "3768036424",
            File = "BetterTacMap.dll", Guid = "toemel.bettertacmap", Name = "BetterTacMap", Version = "0.2.0",
            TypeName = "BetterTacMap.BetterTacMapMod" },
    };

    // A dependency that names the program expected to start a plugin, not an
    // API the plugin calls. For pinned images only, SEST's loader is that
    // starter. SEST registers nothing under this GUID, never writes it to
    // Chainloader.PluginInfos and never presents itself as Keel.
    internal static readonly Dictionary<string, string> HostSatisfiedDependencies = new(StringComparer.Ordinal) {
        [KeelStubGuid] = "R.A.T.S. Keel's starter; the pinned images call no Keel code, so SEST's loader starts them instead",
    };

    // Another mod loader's own images: never admitted, whatever their hash.
    internal static readonly HashSet<string> ForeignLoaderAssemblies = new(StringComparer.OrdinalIgnoreCase) {
        "SeaPowerKeel", "SeaPowerKeel.Patcher", "SeaPowerKeel.Stub" };

    internal static WorkshopBepInPlugin WorkshopBepInFor(string hash) =>
        hash != null && WorkshopBepInPlugins.TryGetValue(hash, out var pin) ? pin : null;

    // Pre-CLR check of a pinned image's own metadata. Null when admitted,
    // otherwise the one-line reason it is held.
    internal static string WorkshopBepInRefusal(ModuleDefinition module, string source, WorkshopBepInPlugin pin)
    {
        if (ForeignLoaderAssemblies.Contains(module.Assembly.Name.Name)) return "another mod loader's own image";
        if (!String.Equals(Path.GetFileName(source), pin.File, StringComparison.OrdinalIgnoreCase)) return "pinned as " + pin.File;
        if (!InWorkshopFolder(source, pin.WorkshopId)) return "not inside Workshop folder " + pin.WorkshopId;
        var foreign = module.AssemblyReferences.FirstOrDefault(r => ForeignLoaderAssemblies.Contains(r.Name) || r.Name == "AnchorChain");
        if (foreign != null) return "references another loader's API (" + foreign.Name + ")";
        var plugins = Types(module.Types).Where(t => t.CustomAttributes.Any(a => a.AttributeType.FullName == "BepInEx.BepInPlugin")).ToList();
        if (plugins.Count != 1) return plugins.Count + " BepInPlugin types, pinned 1";
        var type = plugins[0];
        if (type.FullName != pin.TypeName || type.BaseType?.FullName != "BepInEx.BaseUnityPlugin")
            return "plugin type is " + type.FullName + " : " + type.BaseType?.FullName + ", pinned " + pin.TypeName;
        if (Types(module.Types).Any(t => t.CustomAttributes.Any(a => a.AttributeType.FullName == "AnchorChain.ACPlugin")))
            return "also an Anchor Chain plugin";
        var meta = type.CustomAttributes.Single(a => a.AttributeType.FullName == "BepInEx.BepInPlugin").ConstructorArguments
            .Select(a => a.Value as string).ToArray();
        if (meta.Length != 3 || meta[0] != pin.Guid || meta[1] != pin.Name || meta[2] != pin.Version)
            return "plugin metadata (" + String.Join(", ", meta) + ") differs from the pin";
        bool marker = false;
        var after = new HashSet<string>(StringComparer.Ordinal);
        foreach (var attribute in type.CustomAttributes) {
            string name = attribute.AttributeType.FullName;
            if (name == "BepInEx.BepInIncompatibility" || name == "BepInEx.BepInProcess") return name + " is not supported";
            if (name != "BepInEx.BepInDependency") continue;
            string guid = attribute.ConstructorArguments.Count == 0 ? null : attribute.ConstructorArguments[0].Value as string;
            if (guid == null) return "unreadable BepInDependency";
            if (HostSatisfiedDependencies.ContainsKey(guid)) { marker = true; continue; }
            if (!pin.After.Contains(guid)) return "unpinned dependency " + guid;
            after.Add(guid);
            // The (guid, minimumVersion) form: the pinned provider must meet it.
            if (attribute.ConstructorArguments.Count == 2 && attribute.ConstructorArguments[1].Value is string minimum) {
                var provider = WorkshopBepInPlugins.Values.Single(p => p.Guid == guid);
                if (new Version(provider.Version) < new Version(minimum)) return guid + " " + provider.Version + " is below its minimum " + minimum;
            }
        }
        if (marker != pin.KeelStarterMarker || !after.SetEquals(pin.After)) return "dependencies differ from the pin";
        return null;
    }

    private static bool InWorkshopFolder(string source, string workshopId)
    {
        for (var dir = new FileInfo(source).Directory; dir != null; dir = dir.Parent)
            if (dir.Name == workshopId) return true;
        return false;
    }
}
