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
        // Pop-Out Windows 1.4.1 (23 Nov 2026, Sea Power 0.9.3) only.
        // PopOutScreen keeps root, host, hint, Instance, DisplayAvailable,
        // HostOpening, Decorate, Move, Place, Remember, Open and UpdateScreen
        // (same bodies apart from the SavedLayout/GameMouse renames). 1.3.0
        // moved the tracked window list to ScreenCutOut.Windows (PopOutScreen
        // .cutOut), FindButtonsPanel to SmartWindows.TitleBar and Flatten to
        // ScreenResources. 1.1.3 and 1.2.3 had the old layout and are no
        // longer accepted.
        internal const string PopOut14Hash = "c241a0d647cba1d71414fc20ac7b9a34f662e01a4533097db0a8841b8e7875f9";
        internal static readonly string[] PopOutHashes = { PopOut14Hash };
        internal static string RequirePopOut(Assembly pop) { return ContactsFix.RequireAny(pop, PopOutHashes); }
        static MethodInfo getRoot;
        static FieldInfo cutOut;
        static PropertyInfo windowsProperty;
        static FieldInfo hint;
        static PropertyInfo ready;
        static bool reportedHint;

        internal static void Install()
        {
            var harmony = new Harmony("io.github.sest-hobby.contacts-popout-surface-fix");
            try
            {
                var screen = ContactsFix.Find("SeaPowerPopOut.PopOutScreen");
                RequirePopOut(screen.Assembly);
                var bridge = ContactsFix.Find("Sest.RuntimeFixes.PopOutBridge");
                getRoot = bridge.GetProperty("Root", All).GetGetMethod(true);
                ready = ContactsFix.Find("Sest.RuntimeFixes.NativeCombatSurface").GetProperty("Ready", All);
                cutOut = screen.GetField("cutOut", All);
                windowsProperty = cutOut?.FieldType.GetProperty("Windows", All);
                hint = screen.GetField("hint", All);
                var move = ContactsFix.Find("Sest.RuntimeFixes.ContactWindowBridge").GetMethod("Move", All);
                if (getRoot == null || move == null || ready == null || cutOut == null || windowsProperty == null || hint == null)
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
                var windows = windowsProperty.GetValue(cutOut.GetValue(__instance), null) as IList;
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
