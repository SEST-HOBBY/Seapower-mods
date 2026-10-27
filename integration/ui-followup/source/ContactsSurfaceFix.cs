using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using Noesis;

namespace Sest.UiFixes
{
    internal static class ContactsSurfaceFix
    {
        const BindingFlags All = ContactsFix.All;
        internal const string PopOutHash = "d0027215eb78e95e4cb45f5e132a4ad50acd03606c681ba0996ece1f92434a63";
        static MethodInfo getRoot;
        static FieldInfo trackedWindows;
        static FieldInfo hint;
        static PropertyInfo ready;
        static bool reportedHint;

        internal static void Install()
        {
            var harmony = new Harmony("io.github.sest-hobby.contacts-popout-surface-fix");
            try
            {
                var screen = ContactsFix.Find("SeaPowerPopOut.PopOutScreen");
                ContactsFix.Require(screen.Assembly, PopOutHash);
                var bridge = ContactsFix.Find("Sest.RuntimeFixes.PopOutBridge");
                getRoot = bridge.GetProperty("Root", All).GetGetMethod(true);
                ready = ContactsFix.Find("Sest.RuntimeFixes.NativeCombatSurface").GetProperty("Ready", All);
                trackedWindows = screen.GetField("windows", All);
                hint = screen.GetField("hint", All);
                var move = ContactsFix.Find("Sest.RuntimeFixes.ContactWindowBridge").GetMethod("Move", All);
                if (getRoot == null || move == null || ready == null || trackedWindows == null || hint == null)
                    throw new MissingMemberException("Inspected Contacts pop-out surface");
                harmony.Patch(move, transpiler: new HarmonyMethod(typeof(ContactsSurfaceFix), nameof(MoveSurface)));
                harmony.Patch(screen.GetMethod("UpdateScreen", All),
                    postfix: new HarmonyMethod(typeof(ContactsSurfaceFix), nameof(AfterScreenUpdate)));
                ContactsFix.Log("Contacts pop-out surface fix installed: use the scaled panel containing Items, retain original move/return rollback and placement.");
            }
            catch (Exception error)
            {
                harmony.UnpatchSelf();
                ContactsFix.Log("Contacts surface fix inactive; keyboard fix retained: " + error.Message);
            }
        }

        public static FrameworkElement Surface()
        {
            var root = getRoot.Invoke(null, null) as FrameworkElement;
            if (root == null) return null;
            // PopOutScreen.root is ScalableUserControl, NOT Panel. The inner Grid
            // is the scaled coordinate space used by the author's window Items.
            var items = root.FindName("Items") as ItemsControl;
            var panel = items == null ? null : ContactsFix.UiParent(items) as Panel;
            if (panel == null) throw new InvalidOperationException("Pop-out Items has no scaled parent panel; Contacts remains on its prior screen.");
            return panel;
        }

        public static IEnumerable<CodeInstruction> MoveSurface(IEnumerable<CodeInstruction> input)
        {
            var result = input.ToList();
            var parent = typeof(VisualTreeHelper).GetMethod("GetParent", new[] { typeof(DependencyObject) });
            var safeParent = typeof(ContactsFix).GetMethod(nameof(ContactsFix.UiParent));
            var surface = typeof(ContactsSurfaceFix).GetMethod(nameof(Surface));
            int roots = 0, parents = 0;
            foreach (var code in result)
            {
                if (code.opcode != OpCodes.Call && code.opcode != OpCodes.Callvirt) continue;
                if (Equals(code.operand, getRoot))
                { code.opcode = OpCodes.Call; code.operand = surface; roots++; }
                else if (Equals(code.operand, parent))
                { code.opcode = OpCodes.Call; code.operand = safeParent; parents++; }
            }
            if (roots != 1 || parents != 2) throw new InvalidOperationException("Contacts move audit mismatch: roots=" + roots + ", parents=" + parents);
            return result;
        }

        public static void AfterScreenUpdate(object __instance)
        {
            try
            {
                if (!(bool)ready.GetValue(null, null)) return;
                var label = hint.GetValue(__instance) as TextBlock;
                var windows = trackedWindows.GetValue(__instance) as IList;
                if (label == null || windows == null) return;
                // Standalone Contacts is tracked for the transparent monitor but is
                // not a WindowHost view model. It must also suppress the empty hint.
                foreach (var item in windows)
                    if (item is FrameworkElement element && element.Visibility == Visibility.Visible && ContactsFix.UiParent(element) != null)
                    { label.Visibility = Visibility.Collapsed; break; }
            }
            catch (Exception error)
            {
                if (!reportedHint) { reportedHint = true; ContactsFix.Log("Pop-out hint refresh skipped: " + error.Message); }
            }
        }
    }
}
