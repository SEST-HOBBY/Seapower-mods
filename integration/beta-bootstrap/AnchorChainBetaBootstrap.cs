// SEST beta compatibility bridge, not a replacement for Anchor Chain.
// The 261026 BepInEx log shows the upstream preloader's Awake running BEFORE
// FileManager has listed Workshop directories. Delay its normal LoadPlugins()
// call until those same directories have settled; change no game assemblies.
// No Harmony patches, game DLL references, or hash-gate bypasses.
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using BepInEx;
using UnityEngine;

namespace SEST.Beta
{
    [BepInPlugin("io.sest.anchorchain.beta.bootstrap", "SEST Beta Anchor Chain Bootstrap", "0.1.0")]
    public sealed class AnchorChainBetaBootstrap : BaseUnityPlugin
    {
        // Captured 28 October on the Sea Power PUBLIC BETA, not a semver guess.
        private const string BetaGameHash =
            "3005bc6d4221a921008778a18dec06515d98c63d3afb6a3a2835b985ab2e7d62";
        private const string AnchorChainWorkshopId = "3380210757";
        private const int MaxTicks = 120; // 60 seconds, then stop cleanly.
        private const int StableTicksRequired = 6; // 3 seconds of unchanged directories.
        private bool _attempted;

        private void Awake()
        {
            string nativeDll = Path.Combine(Application.dataPath, "Managed", "Seapower-Scripts.dll");
            try
            {
                if (!File.Exists(nativeDll) || !String.Equals(Hash(nativeDll), BetaGameHash,
                    StringComparison.OrdinalIgnoreCase))
                {
                    Logger.LogWarning("Beta bootstrap inactive: uninspected game assembly. No patches installed.");
                    return;
                }
            }
            catch (Exception ex)
            {
                Logger.LogWarning("Beta bootstrap inactive: failed game build verification: " + ex.Message);
                return;
            }
            Logger.LogInfo("Build 261026 verified; waiting for Workshop directories before Anchor Chain discovery.");
            StartCoroutine(DeferredLoad());
        }

        private IEnumerator DeferredLoad()
        {
            string previous = null;
            int stable = 0;
            for (int attempt = 0; attempt < MaxTicks; attempt++)
            {
                if (_attempted)
                    yield break;

                List<string> roots = GetGameModDirectories();
                string candidate = FindAnchorChain(roots);
                string signature = String.Join("\n", roots.OrderBy(x => x, StringComparer.OrdinalIgnoreCase).ToArray())
                    + "\n" + (candidate ?? "");
                if (candidate != null && String.Equals(signature, previous, StringComparison.Ordinal))
                    stable++;
                else
                    stable = 0;
                previous = signature;

                if (candidate != null && stable >= StableTicksRequired)
                {
                    _attempted = true;
                    try
                    {
                        if (WasAlreadyStarted())
                        {
                            Logger.LogInfo("Anchor Chain already initialized. Nothing to retry.");
                        }
                        else
                        {
                            LoadAnchorChain(candidate);
                        }
                    }
                    catch (Exception ex)
                    {
                        Logger.LogError("Deferred Anchor Chain discovery failed: " + ex);
                    }
                    yield break;
                }
                yield return new WaitForSecondsRealtime(0.5f);
            }
            Logger.LogWarning("Anchor Chain was not found in ready FileManager directories after 60 seconds. No further retry.");
        }

        private List<string> GetGameModDirectories()
        {
            var output = new List<string>();
            try
            {
                Type type = AppDomain.CurrentDomain.GetAssemblies()
                    .Select(a => a.GetType("SeaPower.FileManager", false))
                    .FirstOrDefault(t => t != null);
                if (type == null)
                    return output;

                const BindingFlags flags = BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic;
                PropertyInfo singleton = type.GetProperty("Instance", flags);
                object manager = singleton != null ? singleton.GetValue(null, null) : null;
                if (manager == null)
                {
                    FieldInfo singletonField = type.GetField("Instance", flags);
                    if (singletonField != null)
                        manager = singletonField.GetValue(null);
                }
                if (manager == null)
                    return output;

                const BindingFlags memberFlags = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;
                PropertyInfo dirsProp = type.GetProperty("Directories", memberFlags);
                object raw = dirsProp != null ? dirsProp.GetValue(manager, null) : null;
                if (raw == null)
                {
                    FieldInfo dirsField = type.GetField("Directories", memberFlags);
                    if (dirsField != null)
                        raw = dirsField.GetValue(manager);
                }
                var dirs = raw as IEnumerable;
                if (dirs == null)
                    return output;

                foreach (object entry in dirs)
                {
                    if (entry == null)
                        continue;
                    var info = entry as DirectoryInfo;
                    if (info == null)
                    {
                        PropertyInfo property = entry.GetType().GetProperty("DirectoryInfo",
                            BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);
                        if (property != null)
                            info = property.GetValue(entry, null) as DirectoryInfo;
                    }
                    if (info != null && Directory.Exists(info.FullName))
                        output.Add(info.FullName);
                }
            }
            catch (Exception ex)
            {
                Logger.LogWarning("Beta FileManager discovery not ready: " + ex.GetType().Name);
            }
            return output.Distinct(StringComparer.OrdinalIgnoreCase).ToList();
        }

        private string FindAnchorChain(List<string> roots)
        {
            var matches = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (string root in roots)
            {
                // The real Anchor Chain Workshop item is ID 3380210757.
                // Search only its registered roots, not every arbitrary DLL on disk.
                if (root.IndexOf(AnchorChainWorkshopId, StringComparison.OrdinalIgnoreCase) >= 0)
                    FindUnder(root, matches);
                else
                {
                    string child = Path.Combine(root, AnchorChainWorkshopId);
                    if (Directory.Exists(child))
                        FindUnder(child, matches);
                    string direct = Path.Combine(root, "AnchorChain.dll");
                    if (File.Exists(direct))
                        matches.Add(Path.GetFullPath(direct));
                    string plugins = Path.Combine(root, "plugins", "AnchorChain.dll");
                    if (File.Exists(plugins))
                        matches.Add(Path.GetFullPath(plugins));
                }
            }
            if (matches.Count > 1)
            {
                Logger.LogWarning("Multiple AnchorChain.dll files in registered mod directories; refusing ambiguous bootstrap.");
                return null;
            }
            return matches.FirstOrDefault();
        }

        private static void FindUnder(string path, HashSet<string> found)
        {
            try
            {
                foreach (string file in Directory.GetFiles(path, "AnchorChain.dll", SearchOption.AllDirectories))
                    found.Add(Path.GetFullPath(file));
            }
            catch (IOException) { }
            catch (UnauthorizedAccessException) { }
        }

        private bool WasAlreadyStarted()
        {
            // If the upstream preloader succeeded on another game build/timing,
            // never double-load its mods or reapply their Harmony patches.
            foreach (Assembly asm in AppDomain.CurrentDomain.GetAssemblies())
            {
                Type loader = asm.GetType("AnchorChain.AnchorChainLoader", false);
                if (loader == null)
                    continue;
                FieldInfo directories = loader.GetField("_allDirectories",
                    BindingFlags.Static | BindingFlags.NonPublic);
                object value = directories != null ? directories.GetValue(null) : null;
                if (value == null)
                    return true; // unknown loader state: fail closed
                PropertyInfo count = value.GetType().GetProperty("Count");
                if (count == null)
                    return true;
                return Convert.ToInt32(count.GetValue(value, null)) != 0;
            }
            return false;
        }

        private void LoadAnchorChain(string dll)
        {
            AssemblyName identity = AssemblyName.GetAssemblyName(dll);
            if (!String.Equals(identity.Name, "AnchorChain", StringComparison.Ordinal)
                || identity.Version != new Version(1, 1, 0, 0))
            {
                Logger.LogWarning("Anchor Chain assembly identity/version not expected; declining retry.");
                return;
            }
            Assembly chain = AppDomain.CurrentDomain.GetAssemblies()
                .FirstOrDefault(a => a.GetName().Name == "AnchorChain");
            if (chain == null)
                chain = Assembly.LoadFile(dll);
            Type loaderType = chain.GetType("AnchorChain.AnchorChainLoader", true);
            MethodInfo method = loaderType.GetMethod("LoadPlugins",
                BindingFlags.Public | BindingFlags.Instance);
            if (method == null)
                throw new MissingMethodException(loaderType.FullName, "LoadPlugins");
            // Invoke the upstream loader's normal entry point, which already
            // resolves configs/dependencies and respects game-registered mods.
            method.Invoke(Activator.CreateInstance(loaderType), null);
            Logger.LogInfo("Deferred Anchor Chain LoadPlugins invoked from registered Workshop mod.");
        }

        private static string Hash(string path)
        {
            using (var file = File.OpenRead(path))
            using (var sha = SHA256.Create())
            {
                return BitConverter.ToString(sha.ComputeHash(file)).Replace("-", "").ToLowerInvariant();
            }
        }
    }
}
