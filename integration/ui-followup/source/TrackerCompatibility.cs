using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;

namespace Sest.UiFixes
{
    // The captured Runtime stays unchanged. Only its inspected deferred
    // tracker pin changes in memory, after the current overlay ABI is checked.
    internal static class TrackerCompatibility
    {
        internal const string PreviousHash = "74afa9028fc0c52b93f415263504f51ecf8d056a624feaebcc8053ba5a1c0ac3";
        internal const string CurrentHash = "8f7195ff1540d1901446b3783789c84e1f76bebe943da7606afd85f9dd3d78bc";
        static Type overlayType;
        static FieldInfo visibility, expanded;

        // Runtime 1.5.0 expects a boolean FieldInfo. Tracker 0.8 stores that
        // state in Overlay.visibility.Expanded; forward reads AND close writes.
        sealed class ExpandedField : FieldInfo
        {
            public override FieldAttributes Attributes => FieldAttributes.Private;
            public override RuntimeFieldHandle FieldHandle => throw new NotSupportedException("Projected visibility field has no IL field token");
            public override Type FieldType => typeof(bool);
            public override Type DeclaringType => overlayType;
            public override Type ReflectedType => overlayType;
            public override string Name => "visible";
            public override object GetValue(object owner) => expanded.GetValue(visibility.GetValue(owner));
            public override void SetValue(object owner, object value, BindingFlags flags, Binder binder, CultureInfo culture)
                => expanded.SetValue(visibility.GetValue(owner), value, flags, binder, culture);
            public override object[] GetCustomAttributes(bool inherit) => Array.Empty<object>();
            public override object[] GetCustomAttributes(Type attributeType, bool inherit) => Array.Empty<object>();
            public override bool IsDefined(Type attributeType, bool inherit) => false;
        }

        public static bool BeforeField(Type __0, string __1, Type __2, ref FieldInfo __result)
        {
            if (__0 != overlayType || __1 != "visible" || __2 != typeof(bool)) return true;
            __result = new ExpandedField();
            return false;
        }

        internal static void ValidateTracker(Type overlay)
        {
            foreach (string name in new[] { "ready", "missionActive" })
            {
                var field = overlay.GetField(name, ContactsFix.All);
                if (field == null || field.IsStatic || field.FieldType != typeof(bool))
                    throw new MissingFieldException(overlay.FullName, name);
            }
            var mission = overlay.GetField("mission", ContactsFix.All);
            var toggle = overlay.GetField("toggle", ContactsFix.All);
            if (mission == null || mission.IsStatic || toggle == null || toggle.IsStatic ||
                toggle.FieldType.FullName != "UnityEngine.KeyCode")
                throw new MissingMemberException("Tracker mission/toggle contract");
            var state = overlay.GetField("visibility", ContactsFix.All);
            var value = state == null ? null : state.FieldType.GetField("Expanded", ContactsFix.All);
            if (state == null || state.IsStatic || state.FieldType.FullName != "WeaponCostsMod.OverlayVisibility" ||
                value == null || value.IsStatic || value.FieldType != typeof(bool))
                throw new MissingMemberException("Tracker 0.8 visibility state");
            foreach (string name in new[] { "Update", "OnGUI", "LoadConfig" })
            {
                Type[] args = name == "LoadConfig" ? new[] { typeof(bool) } : Type.EmptyTypes;
                var method = overlay.GetMethod(name, ContactsFix.All, null, args, null);
                if (method == null || method.IsStatic || method.ReturnType != typeof(void))
                    throw new MissingMethodException(overlay.FullName, name);
            }
            overlayType = overlay; visibility = state; expanded = value;
        }

        internal static void Install()
        {
            var harmony = new Harmony("io.github.sest-hobby.tracker-080-compatibility");
            try
            {
                var overlay = ContactsFix.Find("WeaponCostsMod.Overlay");
                ContactsFix.Require(overlay.Assembly, CurrentHash);
                ValidateTracker(overlay);
                var bridge = ContactsFix.Find("Sest.RuntimeFixes.F11CombatCosts");
                var poll = bridge.GetMethod("Poll", ContactsFix.All, null, Type.EmptyTypes, null);
                var stopped = bridge.GetField("stopped", ContactsFix.All);
                var field = bridge.GetMethod("Field", ContactsFix.All, null, new[] { typeof(Type), typeof(string), typeof(Type) }, null);
                if (poll == null || !poll.IsStatic || poll.ReturnType != typeof(void) ||
                    stopped == null || !stopped.IsStatic || stopped.FieldType != typeof(bool) ||
                    field == null || !field.IsStatic || field.ReturnType != typeof(FieldInfo))
                    throw new MissingMemberException("Captured Runtime 1.5.0 tracker bridge");
                harmony.Patch(field, prefix: new HarmonyMethod(typeof(TrackerCompatibility), nameof(BeforeField)));
                harmony.Patch(poll, transpiler: new HarmonyMethod(typeof(TrackerCompatibility), nameof(Rewrite)));
                stopped.SetValue(null, false);
                ContactsFix.Log("stable Combat Cost Tracker 0.8 bridge compatibility installed; Runtime 1.5.0 retained.");
            }
            catch (Exception error)
            {
                harmony.UnpatchSelf();
                ContactsFix.Log("Tracker 0.8 bridge compatibility inactive; original tracker retained: " + error.Message);
            }
        }

        public static IEnumerable<CodeInstruction> Rewrite(IEnumerable<CodeInstruction> input)
        {
            var result = input.ToList();
            if (result.Count(c => c.opcode == OpCodes.Ldstr && Equals(c.operand, PreviousHash)) != 1)
                throw new InvalidOperationException("Captured Runtime tracker pin audit changed");
            foreach (var code in result)
                if (code.opcode == OpCodes.Ldstr && Equals(code.operand, PreviousHash)) code.operand = CurrentHash;
            return result;
        }
    }
}
