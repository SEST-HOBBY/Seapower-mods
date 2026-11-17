using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using AnchorChain;
using HarmonyLib;
using UnityEngine;

namespace Sest.IdentifyDataPaths
{
    // Anchor Chain converts Before into the target plugin's After dependency.
    [ACPlugin("io.github.sest-hobby.identify-data-paths", "SEST Identify Data Paths", "1.1.0",
              new string[] { "com.fmsv.identifyexpanded" }, new string[] { "io.github.sest-hobby.runtime-fixes" })]
    public sealed class Plugin : IAnchorChainMod
    {
        internal const string HarmonyId = "io.github.sest-hobby.identify-data-paths";
        internal const string GameHash = "3f56861f09e867f315b194c81a7a2450154ccc6bb5afb769b4956dfd4a00503a";
        internal const string IdentifyHash = "9f0ec630e9d7659082bdce61743a87895de14f1903a44c68395f8f158af8afd7";
        internal const string HarmonyHash = "1a21cc03424fc82c3dd1346905d16494536b9595ae4162228d99fb7c285c1031";
        private static string dataPath;
        private static string streamingPath;

        public void TriggerEntryPoint()
        {
            try
            {
                var runtime = AppDomain.CurrentDomain.GetAssemblies().Single(a => a.GetName().Name == "SEST.RuntimeFixes");
                if (Hash(runtime.Location) != BuildPins.RuntimeSha256)
                    throw new InvalidOperationException("Uninspected paired SEST Runtime");
                var pack = Directory.GetParent(typeof(Plugin).Assembly.Location).Parent;
                var settings = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
                    "AppData", "LocalLow", "Triassic Games", "Sea Power", "usersettings.ini");
                var enabled = runtime.GetType("Sest.RuntimeFixes.Policy", true).GetMethod("PackEnabled",
                    BindingFlags.Static | BindingFlags.NonPublic | BindingFlags.Public);
                if (!(bool)enabled.Invoke(null, new object[] { File.ReadAllLines(settings), pack.Name }))
                { Debug.Log("[SEST Identify Paths] inactive: owning SEST pack is disabled."); return; }
                string native = Path.Combine(Application.dataPath, "Managed", "Seapower-Scripts.dll");
                Assembly[] matches = AppDomain.CurrentDomain.GetAssemblies()
                    .Where(a => a.GetName().Name == "IdentifyExpanded").ToArray();
                string identifySource = matches.Length == 1 ? BetaAssemblyPolicy.OriginalLocation(matches[0]) : "";
                if (Hash(native) != GameHash || matches.Length != 1 ||
                    Hash(identifySource) != IdentifyHash ||
                    new DirectoryInfo(Path.GetDirectoryName(identifySource)).Name != "3790594162" ||
                    Hash(typeof(Harmony).Assembly.Location) != HarmonyHash)
                {
                    Debug.Log("[SEST Identify Paths] inactive: uninspected game/plugin, duplicate assembly or non-Workshop source.");
                    return;
                }
                string target = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                    "SEST", "IdentifyExpanded");
                if (String.IsNullOrEmpty(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData)))
                    throw new InvalidOperationException("LocalApplicationData is unavailable");
                Directory.CreateDirectory(target);
                ApplyPatches(matches[0].GetType("IdentifyExpanded.ModPaths", true), target, Application.streamingAssetsPath);
                Debug.Log("[SEST Identify Paths] active: settings/audio use " + target + "; Workshop DLL unchanged.");
            }
            catch (Exception e)
            {
                try { new Harmony(HarmonyId).UnpatchSelf(); } catch { }
                Debug.LogWarning("[SEST Identify Paths] inactive: " + e.GetBaseException().Message);
            }
        }

        internal static void ApplyPatches(Type paths, string target, string originalStreaming)
        {
            MethodInfo mod = paths.GetProperty("ModDir", BindingFlags.Static | BindingFlags.Public)?.GetGetMethod();
            MethodInfo stream = paths.GetProperty("StreamingAssets", BindingFlags.Static | BindingFlags.Public)?.GetGetMethod();
            if (mod == null || stream == null || mod.ReturnType != typeof(string) || stream.ReturnType != typeof(string))
                throw new InvalidOperationException("Inspected path API is missing");
            dataPath = Path.GetFullPath(target);
            streamingPath = Path.GetFullPath(originalStreaming);
            Harmony h = new Harmony(HarmonyId);
            try
            {
                h.Patch(mod, prefix: new HarmonyMethod(typeof(Plugin), nameof(DataPrefix)));
                h.Patch(stream, prefix: new HarmonyMethod(typeof(Plugin), nameof(StreamingPrefix)));
                if ((string)mod.Invoke(null, null) != dataPath || (string)stream.Invoke(null, null) != streamingPath)
                    throw new InvalidOperationException("Path override did not verify");
            }
            catch { h.UnpatchSelf(); throw; }
        }

        private static bool DataPrefix(ref string __result) { __result = dataPath; return false; }
        private static bool StreamingPrefix(ref string __result) { __result = streamingPath; return false; }
        private static string Hash(string path)
        {
            if (!File.Exists(path)) return "";
            using (var s = File.OpenRead(path))
            using (var h = SHA256.Create())
                return BitConverter.ToString(h.ComputeHash(s)).Replace("-", "").ToLowerInvariant();
        }
    }
}
