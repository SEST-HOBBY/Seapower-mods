// SEST beta-only bounded Anchor Chain startup.
 // This replaces the experimental PR #53 invoker. Inert unless explicitly
 // enabled after a successful probe launch. Does not modify upstream files.
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using BepInEx;
using UnityEngine;

namespace SEST.BetaAnchor
{
    [BepInPlugin("io.sest.beta.safeanchor", "SEST Beta Safe Anchor Chain", "0.2.0")]
    public sealed class Bootstrap : BaseUnityPlugin
    {
        private const string TargetGameSha256 =
            "3005bc6d4221a921008778a18dec06515d98c63d3afb6a3a2835b985ab2e7d62";
        private const string TargetPreloaderSha256 =
            "1ee1570f1e7f457ffa63c24ee4085b2cdea8069ea8cebf146de5ef027eaa3984";
        private const int MaxTicks = 120; // sixty seconds
        private const int ReadyTicks = 6; // three seconds
        private bool _attempted;
        private string _payloadDirectory;

        private void Awake()
        {
            try
            {
                var gameDir = new DirectoryInfo(Application.dataPath).Parent;
                if (gameDir == null)
                    throw new DirectoryNotFoundException("Sea Power game directory unavailable");
                var gameRoot = gameDir.FullName;
                var gameDll = Path.Combine(Application.dataPath, "Managed", "Seapower-Scripts.dll");
                var preloader = Path.Combine(gameRoot, "BepInEx", "plugins", "AnchorChain.Preloader.dll");
                if (!File.Exists(gameDll) || !File.Exists(preloader)
                    || !String.Equals(Sha256(gameDll), TargetGameSha256, StringComparison.OrdinalIgnoreCase)
                    || !String.Equals(Sha256(preloader), TargetPreloaderSha256, StringComparison.OrdinalIgnoreCase))
                {
                    Logger.LogWarning("Beta safe loader INACTIVE: uninspected game/preloader build.");
                    return;
                }
                _payloadDirectory = Path.Combine(gameRoot, "BepInEx", "config", "SEST-BetaAnchorChain");
                Logger.LogInfo("Beta 261026 verified. Startup probe only until explicit enable.flag is present.");
                StartCoroutine(ProbeDirectories());
            }
            catch (Exception ex)
            {
                Logger.LogError("Beta safe loader failed closed during probe setup: " + ex);
            }
        }

        private IEnumerator ProbeDirectories()
        {
            string oldSignature = null;
            int stable = 0;
            for (int i = 0; i < MaxTicks; i++)
            {
                List<string> roots;
                string status;
                roots = GetModDirectories(out status);
                bool registered = IsAnchorChainWorkshopRegistered(roots);
                string signature = String.Join("|", roots.OrderBy(x => x, StringComparer.OrdinalIgnoreCase).ToArray());
                bool ready = roots.Count > 0 && registered;
                if (ready && String.Equals(signature, oldSignature, StringComparison.Ordinal))
                    stable++;
                else
                    stable = 0;
                oldSignature = signature;

                if (i == 0 || i == 10 || i == 30 || i == 60 || i == MaxTicks - 1)
                    Logger.LogInfo("Safe probe tick=" + i + " roots=" + roots.Count
                        + " workshopRegistered=" + registered + " state=" + status);

                if (ready && stable >= ReadyTicks)
                {
                    bool enabled = File.Exists(Path.Combine(_payloadDirectory, "enable.flag"));
                    Logger.LogInfo("BETA SAFE BOOTSTRAP READY; enable=" + enabled
                        + " roots=" + roots.Count + " workshopRegistered=" + registered);
                    if (enabled)
                    {
                        _attempted = true;
                        try { LoadForkOnce(); }
                        catch (Exception ex) { Logger.LogError("Bounded loader failed closed: " + ex); }
                    }
                    yield break;
                }
                yield return new WaitForSecondsRealtime(0.5f);
            }
            Logger.LogWarning("Safe bootstrap never observed a stable, registered Workshop directory. Not loading any plugin.");
        }

        private List<string> GetModDirectories(out string status)
        {
            var result = new List<string>();
            status = "not ready";
            try
            {
                Type fileManager = AppDomain.CurrentDomain.GetAssemblies()
                    .Select(a => a.GetType("SeaPower.FileManager", false))
                    .FirstOrDefault(t => t != null);
                if (fileManager == null) { status = "FileManager class absent"; return result; }
                string singletonStatus;
                object instance = ReadMember(fileManager, null, "Instance", out singletonStatus);
                if (instance == null) { status = singletonStatus; return result; }

                string directoriesStatus;
                var raw = ReadMember(instance.GetType(), instance, "Directories", out directoriesStatus)
                    as IEnumerable;
                if (raw == null) { status = directoriesStatus; return result; }

                foreach (object entry in raw)
                {
                    if (entry == null)
                        continue;
                    DirectoryInfo dir = entry as DirectoryInfo;
                    if (dir == null)
                    {
                        string entryStatus;
                        dir = ReadMember(entry.GetType(), entry, "DirectoryInfo", out entryStatus)
                            as DirectoryInfo;
                    }
                    if (dir != null && dir.Exists)
                        result.Add(dir.FullName);
                }
                status = "instance=" + singletonStatus + "; directories=" + directoriesStatus;
            }
            catch (Exception ex)
            {
                status = "reflection " + ex.GetType().Name + ": " + ex.Message;
            }
            return result.Distinct(StringComparer.OrdinalIgnoreCase).ToList();
        }

        private static object ReadMember(Type type, object instance, string name, out string description)
        {
            const BindingFlags common = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly;
            BindingFlags flags = common | (instance == null ? BindingFlags.Static : BindingFlags.Instance);
            description = name + " not on hierarchy";
            for (Type declaring = type; declaring != null; declaring = declaring.BaseType)
            {
                try
                {
                    PropertyInfo property = declaring.GetProperty(name, flags);
                    if (property != null && property.GetIndexParameters().Length == 0)
                    {
                        object value = property.GetValue(instance, null);
                        description = declaring.FullName + "." + name + (value == null ? " null" : " property OK");
                        if (value != null) return value;
                    }
                    FieldInfo field = declaring.GetField(name, flags);
                    if (field != null)
                    {
                        object value = field.GetValue(instance);
                        description = declaring.FullName + "." + name + (value == null ? " null" : " field OK");
                        if (value != null) return value;
                    }
                }
                catch (Exception ex)
                {
                    description = "reflection failure " + ex.GetType().Name;
                }
            }
            return null;
        }

        private static bool IsAnchorChainWorkshopRegistered(List<string> roots)
        {
            foreach (string root in roots)
            {
                if (root.IndexOf("3380210757", StringComparison.OrdinalIgnoreCase) >= 0)
                    return true;
                if (Directory.Exists(Path.Combine(root, "3380210757")))
                    return true;
            }
            return false;
        }

        private void LoadForkOnce()
        {
            if (!_attempted) throw new InvalidOperationException("Loader invoked without one-shot gate.");
            string payload = Path.Combine(_payloadDirectory, "AnchorChain.dll");
            string hashFile = Path.Combine(_payloadDirectory, "AnchorChain.sha256");
            if (!File.Exists(payload) || !File.Exists(hashFile))
                throw new FileNotFoundException("Bounded loader payload or SHA256 manifest missing.");
            string expected = File.ReadAllText(hashFile).Trim();
            if (!Regex.IsMatch(expected, "^[0-9a-fA-F]{64}$")
                || !String.Equals(Sha256(payload), expected, StringComparison.OrdinalIgnoreCase))
                throw new InvalidDataException("Bounded loader payload does not match the staged SHA256.");
            AssemblyName identity = AssemblyName.GetAssemblyName(payload);
            if (!String.Equals(identity.Name, "AnchorChain", StringComparison.Ordinal)
                || identity.Version != new Version(1, 1, 0, 0))
                throw new InvalidDataException("Bounded loader assembly identity/version mismatch.");

            Assembly[] existing = AppDomain.CurrentDomain.GetAssemblies()
                .Where(a => a.GetName().Name == "AnchorChain").ToArray();
            if (existing.Length > 1)
                throw new InvalidOperationException("Multiple AnchorChain assemblies already loaded.");
            Assembly chain = existing.Length == 1 ? existing[0] : Assembly.LoadFile(payload);
            if (!String.Equals(Path.GetFullPath(chain.Location),
                    Path.GetFullPath(payload), StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("Upstream Anchor Chain already loaded from elsewhere; refuse double load.");

            Type loaderType = chain.GetType("AnchorChain.AnchorChainLoader", true);
            FieldInfo oneShot = loaderType.GetField("_startOnce",
                BindingFlags.NonPublic | BindingFlags.Static);
            if (oneShot == null)
                throw new InvalidOperationException("Expected patched loader one-shot gate not found.");
            if (Convert.ToInt32(oneShot.GetValue(null)) != 0)
            {
                Logger.LogWarning("Bounded loader already attempted initialization. No retry.");
                return;
            }
            MethodInfo entry = loaderType.GetMethod("LoadPlugins",
                BindingFlags.Public | BindingFlags.Instance);
            if (entry == null)
                throw new MissingMethodException("AnchorChain.AnchorChainLoader", "LoadPlugins");
            Logger.LogInfo("Starting bounded Anchor Chain 1.1.0 fork once.");
            entry.Invoke(Activator.CreateInstance(loaderType), null);
            Logger.LogInfo("Bounded Anchor Chain loader returned to bootstrap.");
        }

        private static string Sha256(string path)
        {
            using (var stream = File.OpenRead(path))
            using (var hash = SHA256.Create())
                return BitConverter.ToString(hash.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
        }
    }
}
