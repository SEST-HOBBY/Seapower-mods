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
    // Runtime 1.5.0 remains byte-for-byte the captured, stable-game runtime.
    // Its bridge can accept 1.1.3 only after this companion's native/runtime
    // gates, the exact Pop-Out hash and every reflected bridge contract pass.
    internal static class PopOutCompatibility
    {
        internal const string PreviousHash = "d0027215eb78e95e4cb45f5e132a4ad50acd03606c681ba0996ece1f92434a63";
        const BindingFlags All = ContactsFix.All;

        internal static void ValidateScreen(Type screen)
        {
            var instance = screen.GetProperty("Instance", All);
            if (instance == null || instance.PropertyType != screen ||
                instance.GetGetMethod(true) == null || !instance.GetGetMethod(true).IsStatic)
                throw new MissingMemberException("PopOutScreen.Instance");
            var root = screen.GetField("root", All);
            var host = screen.GetField("host", All);
            var windows = screen.GetField("windows", All);
            var hint = screen.GetField("hint", All);
            var display = screen.GetProperty("DisplayAvailable", All);
            if (root == null || root.IsStatic || !typeof(FrameworkElement).IsAssignableFrom(root.FieldType) ||
                host == null || host.IsStatic || host.FieldType.FullName != "SeapowerUI.WindowHost" ||
                windows == null || windows.IsStatic || !typeof(IList).IsAssignableFrom(windows.FieldType) ||
                hint == null || hint.IsStatic || hint.FieldType != typeof(TextBlock) ||
                display == null || display.PropertyType != typeof(bool) || display.GetGetMethod(true) == null ||
                !display.GetGetMethod(true).IsStatic)
                throw new MissingMemberException("PopOutScreen host/surface contract");
            RequireMethod(screen, "HostOpening", "System.Boolean", false, "SeapowerUI.WindowHost", "System.Object");
            RequireMethod(screen, "Decorate", "System.Void", false, "SeapowerUI.Window");
            RequireMethod(screen, "Move", "System.Void", false, "System.Object", "System.Boolean", "System.Boolean");
            RequireMethod(screen, "Place", "System.Void", false, "SeapowerUI.Window", "System.String");
            RequireMethod(screen, "Open", "System.Boolean", false);
            RequireMethod(screen, "Remember", "System.Void", true, "SeapowerUI.Window");
            RequireMethod(screen, "UpdateScreen", "System.Void", false, "System.Boolean");
            RequireMethod(screen, "Flatten", "Noesis.ResourceDictionary", true, "Noesis.ResourceDictionary");
        }

        static void RequireMethod(Type screen, string name, string result, bool isStatic, params string[] parameters)
        {
            var matches = screen.GetMethods(All).Where(m => m.Name == name && m.IsStatic == isStatic &&
                m.ReturnType.FullName == result &&
                m.GetParameters().Select(p => p.ParameterType.FullName).SequenceEqual(parameters)).ToArray();
            if (matches.Length != 1) throw new MissingMethodException("PopOutScreen." + name);
        }

        internal static void Install()
        {
            var harmony = new Harmony("io.github.sest-hobby.popout-113-compatibility");
            try
            {
                var screen = ContactsFix.Find("SeaPowerPopOut.PopOutScreen");
                ContactsFix.Require(screen.Assembly, ContactsSurfaceFix.PopOutHash);
                ValidateScreen(screen);
                var bridge = ContactsFix.Find("Sest.RuntimeFixes.PopOutBridge");
                var target = bridge.GetMethod("EnsureBound", All, null, Type.EmptyTypes, null);
                var rejected = bridge.GetField("popRejected", All);
                if (target == null || !target.IsStatic || target.ReturnType != typeof(void) ||
                    rejected == null || !rejected.IsStatic || rejected.FieldType != typeof(bool))
                    throw new MissingMemberException("Captured Runtime 1.5.0 pop-out bridge");
                harmony.Patch(target, transpiler: new HarmonyMethod(typeof(PopOutCompatibility), nameof(Rewrite)));
                // If a native tick ran before this companion, permit a new,
                // still hash-checked attempt. No other bridge state is altered.
                rejected.SetValue(null, false);
                ContactsFix.Log("stable Pop-Out Windows 1.1.3 bridge compatibility installed; Runtime 1.5.0 retained.");
            }
            catch (Exception error)
            {
                harmony.UnpatchSelf();
                ContactsFix.Log("Pop-Out 1.1.3 bridge compatibility inactive; existing bridge retained: " + error.Message);
            }
        }

        public static IEnumerable<CodeInstruction> Rewrite(IEnumerable<CodeInstruction> input)
        {
            var codes = input.ToList();
            int pins = codes.Count(c => c.opcode == OpCodes.Ldstr && Equals(c.operand, PreviousHash));
            int messages = codes.Count(c => c.opcode == OpCodes.Ldstr &&
                Equals(c.operand, "native window bridge attached to Pop-Out Windows 1.0.1"));
            if (pins != 1 || messages != 1)
                throw new InvalidOperationException("Runtime pop-out audit mismatch: pins=" + pins + ", messages=" + messages);
            // Preserve every instruction, branch label and exception block.
            foreach (var code in codes)
                if (code.opcode == OpCodes.Ldstr && Equals(code.operand, PreviousHash))
                    code.operand = ContactsSurfaceFix.PopOutHash;
                else if (code.opcode == OpCodes.Ldstr &&
                    Equals(code.operand, "native window bridge attached to Pop-Out Windows 1.0.1"))
                    code.operand = "native window bridge attached to Pop-Out Windows 1.1.3 (stable companion)";
            return codes;
        }
    }
}
