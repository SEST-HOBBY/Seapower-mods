using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using System.Runtime.CompilerServices;
using HarmonyLib;
using SeapowerUI.ViewModels;
using UnityEngine;

namespace Sest.UiFixes
{
    internal static class FormationPerformance
    {
        static FieldInfo barField, windowField;
        static MethodInfo contains, invalidate;
        static ConditionalWeakTable<object, UiRefreshGate> chrome = new ConditionalWeakTable<object, UiRefreshGate>();
        static ConditionalWeakTable<object, FormationBoundsGate> bounds = new ConditionalWeakTable<object, FormationBoundsGate>();
        internal static void Clear()
        { chrome = new ConditionalWeakTable<object, UiRefreshGate>(); bounds = new ConditionalWeakTable<object, FormationBoundsGate>(); }
        internal static void Install()
        {
            var h = new Harmony("io.github.sest-hobby.formation-layout-work");
            try
            {
                var bar = ContactsFix.Find("SeaPowerSquadPanel.SquadBarController");
                ContactsFix.Require(bar.Assembly, "6230e8e78e2ba7ba222241d0c3dcc881d2507ebeeb4eab24b6401cc9144283dd");
                var resize = ContactsFix.Find("SeaPowerSquadPanel.SquadBarResize");
                invalidate = resize.GetMethod("InvalidateContent", ContactsFix.All);
                barField = ContactsFix.Find("SeaPowerSquadPanel.SquadManagerController").GetField("_bar", ContactsFix.All);
                windowField = bar.GetField("_window", ContactsFix.All);
                contains = ContactsFix.Find("Sest.RuntimeFixes.PopOutBridge").GetMethod("Contains", ContactsFix.All);
                if (barField == null || windowField == null || contains == null || invalidate == null) throw new MissingFieldException("Formation chrome contract");
                h.Patch(bar.GetMethod("DiscoverTrees", ContactsFix.All), transpiler: new HarmonyMethod(typeof(FormationPerformance), nameof(KeepRealInvalidation)));
                h.Patch(resize.GetMethod("Refresh", ContactsFix.All), prefix: new HarmonyMethod(typeof(FormationPerformance), nameof(BeforeResize)));
                h.Patch(ContactsFix.Find("Sest.RuntimeFixes.PopOutBridge").GetMethod("AfterFormation", ContactsFix.All),
                    prefix: new HarmonyMethod(typeof(FormationPerformance), nameof(BeforeChrome)));
                ContactsFix.Log("Formation performance: idle discovery no longer forces a full fitting search; actual size/content/drag invalidation retained. Pop-out chrome capped at 5 Hz.");
            }
            catch (Exception e) { h.UnpatchSelf(); ContactsFix.Log("Formation layout correction inactive: " + e.Message); }
        }
        public static void BeforeResize(object __instance, float __0, float __1)
        {
            if (bounds.GetValue(__instance, _ => new FormationBoundsGate()).Changed(__0, __1)) invalidate.Invoke(__instance, null);
        }
        public static bool BeforeChrome(object __0)
        {
            try
            {
                if (!UiRefinements.Ready || __0 == null) return false;
                var bar = barField.GetValue(__0);
                var window = bar == null ? null : windowField.GetValue(bar);
                bool detached = false;
                if (window is SeapowerUI.Window w && w.DataContext != null)
                    detached = (bool)contains.Invoke(null, new[] { w.DataContext });
                return chrome.GetValue(__0, _ => new UiRefreshGate()).Due(window, detached, Time.unscaledTime);
            }
            catch { return true; } // Original bridge owns its existing error boundary.
        }
        public static IEnumerable<CodeInstruction> KeepRealInvalidation(IEnumerable<CodeInstruction> input)
        {
            var target = ContactsFix.Find("SeaPowerSquadPanel.SquadBarResize").GetMethod("InvalidateContent", ContactsFix.All);
            var result = input.ToList(); int count = 0;
            foreach (var c in result)
                if ((c.opcode == OpCodes.Call || c.opcode == OpCodes.Callvirt) && Equals(c.operand, target))
                {
                    // Consume the existing resize-instance operand. EndContentSizes
                    // still invalidates on actual content changes, and Refresh and
                    // drag handlers still refit after dimensions/scale change.
                    c.opcode = OpCodes.Pop; c.operand = null; count++;
                }
            if (count != 1) throw new InvalidOperationException("Formation unconditional refit audit: " + count);
            return result;
        }
    }
}
