using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using System.Security.Cryptography;
using AnchorChain;
using HarmonyLib;
using Noesis;
using UnityEngine;

namespace Sest.UiFixes
{
    [ACPlugin("io.github.sest-hobby.contacts-input-fix", "SEST UI Follow-up Beta", "1.4.13", null, new[] { "io.github.sest-hobby.runtime-fixes" })]
    public sealed class ContactsFix : IAnchorChainMod
    {
        internal const BindingFlags All = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance;
        const string ContactHash = "a1b8b450df0933df61984651fe2b19138acd605aa4b526bbfc23565d8295015e";
        const string RuntimeHash = BuildPins.RuntimeSha256;
        static readonly string[] NativeHashes = {
            "499675cda59912054924ae42297bce7a82b12ca00957dabd684105a24aa353a9",
            "7b1fd6a6b90d0692297906f5907a1b4a2072bf3bf25a983b36aaa5b5c043ebdd"
        };
        static bool installed;
        static PropertyInfo mainKey;

        internal static Type Find(string name)
        {
            return AppDomain.CurrentDomain.GetAssemblies().Select(a => a.GetType(name, false)).FirstOrDefault(t => t != null)
                ?? throw new MissingMemberException(name);
        }
        internal static void Require(Assembly a, string expected) { RequireAny(a, expected); }
        // Returns which inspected image is loaded; any other hash throws.
        internal static string RequireAny(Assembly a, params string[] expected)
        {
            string actual;
            using (var stream = File.OpenRead(BetaAssemblyPolicy.OriginalLocation(a)))
            using (var sha = SHA256.Create())
                actual = BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
            if (Array.IndexOf(expected, actual) < 0) throw new InvalidOperationException("Uninspected assembly: " + a.GetName().Name);
            return actual;
        }
        internal static void Log(string text) { Debug.Log("[SEST UI Follow-up] " + text); }

        public void TriggerEntryPoint()
        {
            if (installed) return;
            Harmony harmony = null;
            try
            {
                var pack = Directory.GetParent(typeof(ContactsFix).Assembly.Location).Parent.FullName;
                var settings = System.IO.Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
                    "AppData", "LocalLow", "Triassic Games", "Sea Power", "usersettings.ini");
                var runtime = Find("Sest.RuntimeFixes.Policy");
                Require(runtime.Assembly, RuntimeHash);
                var enabled = runtime.GetMethod("PackEnabled", All);
                if (!(bool)enabled.Invoke(null, new object[] { File.ReadAllLines(settings), new DirectoryInfo(pack).Name }))
                { Log("inactive: owning pack is disabled"); return; }
                var behaviour = Find("ContactLog.ContactLogBehaviour");
                Require(behaviour.Assembly, ContactHash);
                Require(typeof(SeaPower.ObjectBase).Assembly, NativeHashes[0]);
                Require(typeof(Noesis.GUI).Assembly, NativeHashes[1]);
                var shortcut = Find("BepInEx.Configuration.KeyboardShortcut");
                mainKey = shortcut.GetProperty("MainKey", All);
                if (mainKey == null) throw new MissingMemberException("KeyboardShortcut.MainKey");
                var matches = behaviour.GetMethod("Matches", All, null,
                    new[] { shortcut, typeof(Event) }, null);
                if (matches == null || !matches.IsStatic || matches.ReturnType != typeof(bool))
                    throw new MissingMethodException("Inspected ContactLogBehaviour.Matches");
                var bridge = Find("Sest.RuntimeFixes.ContactWindowBridge");
                var tick = bridge.GetMethod("AfterTick", All);
                if (tick == null) throw new MissingMethodException("ContactWindowBridge.AfterTick");
                harmony = new Harmony("io.github.sest-hobby.contacts-input-fix");
                harmony.Patch(matches, prefix: new HarmonyMethod(typeof(ContactsFix), nameof(BeforeMatches)));
                harmony.Patch(tick, transpiler: new HarmonyMethod(typeof(ContactsFix), nameof(LogicalParents)));
                installed = true;
                Log("1.4.13 beta input fix installed; full Runtime 1.6.3 paired; Contacts time-control behavior retained.");
            }
            catch (Exception error)
            {
                if (harmony != null) harmony.UnpatchSelf();
                while (error is TargetInvocationException && error.InnerException != null) error = error.InnerException;
                Log("inactive; original behavior retained: " + error.GetType().Name + ": " + error.Message);
            }
            if (installed)
            {
                // Each UI module has its own rollback boundary; neither can
                // remove the independently installed, PC-confirmed input fix.
                ContactsSurfaceFix.Install();
                FormationUiMode.Install();
                PerformanceReview.Install();
                UiRefinements.Install();
                TerrainCleanup.Install();
                CostCatalogueCache.Install();
                StutterDiagnostics.Install();
            }
        }

        public static bool BeforeMatches(object __0, Event __1, ref bool __result)
        {
            int key = Convert.ToInt32(mainKey.GetValue(__0, null));
            if (key != 0 && __1 != null && InputPolicy.MayMatch(key, (int)__1.type)) return true;
            __result = false;
            return false;
        }

        // Contact Log builds its controls in the logical tree. Its tab buttons
        // need not have the same immediate parent in the rendered visual tree.
        // Keep the original SEST movement/placement logic and change only these lookups.
        public static DependencyObject UiParent(DependencyObject child)
        {
            var element = child as FrameworkElement;
            return element != null && element.Parent != null ? element.Parent : VisualTreeHelper.GetParent(child);
        }

        public static IEnumerable<CodeInstruction> LogicalParents(IEnumerable<CodeInstruction> input)
        {
            var original = typeof(VisualTreeHelper).GetMethod("GetParent", new[] { typeof(DependencyObject) });
            var replacement = typeof(ContactsFix).GetMethod(nameof(UiParent));
            var result = input.ToList();
            int count = 0;
            foreach (var code in result)
            {
                if ((code.opcode == OpCodes.Call || code.opcode == OpCodes.Callvirt) && Equals(code.operand, original))
                {
                    code.opcode = OpCodes.Call;
                    code.operand = replacement;
                    count++;
                }
            }
            if (count != 3) throw new InvalidOperationException("Contacts parent audit mismatch: " + count);
            return result;
        }
    }
}
