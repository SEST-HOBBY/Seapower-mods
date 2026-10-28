using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using HarmonyLib;
using Noesis;
using SeaPower;
using SeapowerUI;
using UnityEngine;

namespace Sest.UiFixes
{
    internal static class UiRefinements
    {
        static PropertyInfo ready;
        static FieldInfo windowField, tabField;
        static bool reported;
        static ConditionalWeakTable<object, ContactEntry> contacts = new ConditionalWeakTable<object, ContactEntry>();
        sealed class ContactEntry { internal Window Window; internal Button Button; internal object Template; internal bool Styled; }

        internal static void Install()
        {
            ready = ContactsFix.Find("Sest.RuntimeFixes.NativeCombatSurface").GetProperty("Ready", ContactsFix.All);
            var preparation = new Harmony("io.github.sest-hobby.preparation-instructions");
            try
            {
                preparation.Patch(typeof(RichMissionMessages).GetMethod("ParseMissionPopupText", ContactsFix.All),
                    prefix: new HarmonyMethod(typeof(UiRefinements), nameof(BeforePopup)));
                ContactsFix.Log("Preparation instructions: complete paused setup steps and Start preparation button installed.");
            }
            catch (Exception e) { preparation.UnpatchSelf(); ContactsFix.Log("Preparation text patch inactive: " + e.Message); }
            var input = new Harmony("io.github.sest-hobby.contacts-f9-quickload");
            try
            {
                input.Patch(typeof(InputHandler).GetMethod("LoadKeybindings", ContactsFix.All),
                    postfix: new HarmonyMethod(typeof(UiRefinements), nameof(AfterBindings)));
                if (Singleton<InputHandler>.InstanceExists()) AfterBindings(Singleton<InputHandler>.Instance);
            }
            catch (Exception e) { input.UnpatchSelf(); ContactsFix.Log("Quick-load key migration inactive: " + e.Message); }
            var spacing = new Harmony("io.github.sest-hobby.contacts-button-spacing");
            try
            {
                var native = ContactsFix.Find("ContactLog.NativeWindow");
                windowField = native.GetField("_window", ContactsFix.All);
                tabField = native.GetField("_tabContactsBtn", ContactsFix.All);
                if (windowField == null || tabField == null) throw new MissingFieldException("Inspected Contacts header");
                spacing.Patch(ContactsFix.Find("Sest.RuntimeFixes.ContactWindowBridge").GetMethod("AfterTick", ContactsFix.All),
                    postfix: new HarmonyMethod(typeof(UiRefinements), nameof(AfterContacts)));
                ContactsFix.Log("Contacts pop-out button: automatic height/width, explicit padding and centered text installed.");
            }
            catch (Exception e) { spacing.UnpatchSelf(); ContactsFix.Log("Contacts spacing patch inactive: " + e.Message); }
            CameraCompass.Install();
            FormationPerformance.Install();
        }
        internal static bool Ready => ready != null && (bool)ready.GetValue(null, null);
        public static void BeforePopup(ref string __0)
        {
            __0 = UiText.Preparation(__0);
        }
        public static void AfterBindings(InputHandler __instance)
        {
            if (__instance.KeyBindings == null) return;
            foreach (var binding in __instance.KeyBindings)
                if (binding.KeyAction == KeyAction.QuickLoad && binding.keyCodes.Count == 1 && binding.keyCodes[0] == KeyCode.F9)
                {
                    binding.keyCodes = new List<KeyCode> { KeyCode.LeftControl, KeyCode.F9 };
                    binding.DisplayString = "LeftControl+F9";
                    __instance.InputBindingDict[KeyAction.QuickLoad.ToString()] = "LeftControl+F9";
                    ContactsFix.Log("F9 reserved for Contacts; native quick-load moved to Ctrl+F9. Other custom quick-load keys retained.");
                }
        }
        public static void AfterContacts(object __0, bool __runOriginal)
        {
            if (!__runOriginal || !Ready || __0 == null) return;
            try
            {
                var window = windowField.GetValue(__0) as Window;
                if (window == null || !window.IsVisible) return;
                var entry = contacts.GetValue(__0, _ => new ContactEntry());
                if (!ReferenceEquals(entry.Window, window)) { entry.Window = window; entry.Button = null; entry.Template = null; entry.Styled = false; }
                if (entry.Button == null)
                {
                    var tab = tabField.GetValue(__0) as DependencyObject;
                    var panel = tab == null ? null : ContactsFix.UiParent(tab) as Panel;
                    entry.Button = panel?.Children.Cast<UIElement>().OfType<Button>().FirstOrDefault(b => b.Name == "SestContactsPopOut");
                }
                var b = entry.Button;
                if (b == null || (entry.Styled && ReferenceEquals(entry.Template, b.Template))) return;
                b.Height = float.NaN; b.MinHeight = 30; b.MaxHeight = float.PositiveInfinity;
                b.Width = float.NaN; b.MinWidth = 114; b.MaxWidth = float.PositiveInfinity;
                b.Padding = new Thickness(8, 3); b.Margin = new Thickness(8, 0, 2, 0);
                b.HorizontalContentAlignment = HorizontalAlignment.Center;
                b.VerticalContentAlignment = VerticalAlignment.Center;
                b.VerticalAlignment = VerticalAlignment.Stretch;
                entry.Template = b.Template;
                entry.Styled = true;
            }
            catch (Exception e) { if (!reported) { reported = true; ContactsFix.Log("Contacts header sizing skipped: " + e.Message); } }
        }
        internal static void Tick() { if (Ready) CameraCompass.Tick(); }
        internal static void End()
        {
            contacts = new ConditionalWeakTable<object, ContactEntry>();
            CameraCompass.End(); FormationPerformance.Clear();
        }
    }
}
