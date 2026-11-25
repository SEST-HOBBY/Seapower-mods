// SEST's own duplicate-image gate: each assembly name loads once per process,
// from the first copy in Mod Manager order. Later copies are skipped with one
// line before the CLR sees them. Author files are never touched.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;

namespace AnchorChain;

public static partial class BetaAssemblyPolicy
{
    internal sealed class DuplicateGate
    {
        private readonly Dictionary<string, (string Source, string Sha)> admitted = new(StringComparer.OrdinalIgnoreCase);
        private readonly Dictionary<string, string> nameBySource = new(StringComparer.OrdinalIgnoreCase);

        // source: the Workshop path; prepared: what Prepare returned (the
        // source itself or its private cache copy, which keeps the name).
        internal bool Admit(string source, string prepared, Action<string> log)
        {
            string name, sha;
            try { name = AssemblyName.GetAssemblyName(prepared).Name; sha = Hash(source); }
            catch (Exception e) when (e is IOException || e is UnauthorizedAccessException || e is BadImageFormatException || e is ArgumentException) {
                log("SKIPPED before CLR load: " + Label(source) + "; assembly name unreadable (" + e.GetType().Name + "). Data retained.");
                return false;
            }
            if (!admitted.TryGetValue(name, out var first)) {
                admitted[name] = (source, sha);
                nameBySource[Path.GetFullPath(source)] = name;
                return true;
            }
            log(first.Sha == sha
                ? "SKIPPED duplicate before CLR load: " + Label(source) + " is byte-identical to " + Label(first.Source) + " (" + sha.Substring(0, 8)
                    + "), which loads; untick one of the two items."
                : "SKIPPED duplicate before CLR load: " + Label(source) + " (" + sha.Substring(0, 8) + ") is a second " + name + "; "
                    + Label(first.Source) + " (" + first.Sha.Substring(0, 8) + ") loads, earlier in Mod Manager order. Untick one of the two items.");
            return false;
        }

        // The admitted copy then failed to load, so a later good copy may run.
        internal void Release(string source)
        {
            string key = Path.GetFullPath(source);
            if (nameBySource.TryGetValue(key, out var name)) { admitted.Remove(name); nameBySource.Remove(key); }
        }

        // A same-named assembly already in this process (a copy in
        // BepInEx/plugins, or another loader's) is the one copy; the Workshop
        // copy is not loaded beside it. Null when the name is free.
        internal static string LoadedElsewhere(string source, string prepared, IEnumerable<string> loadedNames)
        {
            string name;
            try { name = AssemblyName.GetAssemblyName(prepared).Name; }
            catch (Exception e) when (e is IOException || e is UnauthorizedAccessException || e is BadImageFormatException || e is ArgumentException) { return null; }
            return loadedNames.Contains(name, StringComparer.OrdinalIgnoreCase)
                ? "SKIPPED duplicate before CLR load: " + Label(source) + "; an assembly named " + name
                    + " is already loaded in this process (BepInEx/plugins or another loader), so this copy is not loaded beside it. Data retained."
                : null;
        }

        private static string Label(string path) => new FileInfo(path).Directory?.Name + "\\" + Path.GetFileName(path);
    }
}
