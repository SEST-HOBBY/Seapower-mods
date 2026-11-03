using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;

static class HookTests
{
    const BindingFlags All = BindingFlags.Static | BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic;
    static int checks;
    static void Check(bool ok, string why) { checks++; if (!ok) throw new Exception(why); }
    static List<CodeInstruction> Body(MethodInfo m) { return PatchProcessor.GetOriginalInstructions(m, (ILGenerator)null); }
    static MethodInfo M(Assembly a, string type, string name) { return a.GetType(type, true).GetMethod(name, All); }
    static void Main(string[] args)
    {
        string refs = Path.GetFullPath(args[0]), workshop = Path.GetFullPath(args[3]);
        AppDomain.CurrentDomain.AssemblyResolve += (s,e) => {
            string p = Path.Combine(refs, new AssemblyName(e.Name).Name + ".dll");
            return File.Exists(p) ? Assembly.LoadFrom(p) : null;
        };
        var native = Assembly.LoadFrom(Path.Combine(refs, "Seapower-Scripts.dll"));
        var runtime = Assembly.LoadFrom(Path.GetFullPath(args[1]));
        var ui = Assembly.LoadFrom(Path.GetFullPath(args[2]));
        var guard = runtime.GetType("Sest.RuntimeFixes.TowedSensorGuard", true);
        guard.GetMethod("Bind", All).Invoke(null, new object[] { native });
        var original = Body(M(native, "SeaPower.TowedSystem", "OnFixedUpdate"));
        var replaced = ((IEnumerable<CodeInstruction>)guard.GetMethod("Transpile", All).Invoke(null, new object[] { original })).ToArray();
        Check(replaced.Count(i => (i.operand as MethodInfo)?.Name == "ClearActiveSonar") == 1, "Actual beta towed-system retraction sequence patched once");
        var contacts = runtime.GetType("Sest.RuntimeFixes.ContactWindowBridge", true);
        var input = Body(contacts.GetMethod("AfterTick", All));
        var patched = ((IEnumerable<CodeInstruction>)M(ui, "Sest.UiFixes.ContactsFix", "LogicalParents").Invoke(null, new object[] { input })).ToArray();
        Check(patched.Count(i => (i.operand as MethodInfo)?.Name == "UiParent") == 3, "Actual beta runtime Contacts tick has all three parent lookups patched");
        var bridge = runtime.GetType("Sest.RuntimeFixes.PopOutBridge", true);
        var surface = ui.GetType("Sest.UiFixes.ContactsSurfaceFix", true);
        surface.GetField("getRoot", All).SetValue(null, bridge.GetProperty("Root", All).GetGetMethod(true));
        patched = ((IEnumerable<CodeInstruction>)surface.GetMethod("MoveSurface", All).Invoke(null, new object[] { Body(contacts.GetMethod("Move", All)) })).ToArray();
        Check(patched.Count(i => (i.operand as MethodInfo)?.Name == "Surface") == 1, "Actual Contacts move uses the scaled pop-out surface once");
        Check(patched.Count(i => (i.operand as MethodInfo)?.Name == "UiParent") == 2, "Actual Contacts move retains two corrected parent lookups");
        var pop = Assembly.LoadFrom(Path.Combine(workshop, "3826396311/SeaPowerPopOut.dll"));
        var screen = pop.GetType("SeaPowerPopOut.PopOutScreen", true);
        Check(screen.GetField("root", All).FieldType.FullName == "SeapowerUI.ScalableUserControl", "Updated Pop-Out root remains ScalableUserControl");
        foreach (string method in new[] { "HostOpening", "Decorate", "Move", "Place", "Open", "Remember", "UpdateScreen", "FindButtonsPanel" })
            Check(screen.GetMethod(method, All) != null, "Updated Pop-Out method: " + method);
        foreach (string field in new[] { "host", "windows", "hint", "items" })
            Check(screen.GetField(field, All) != null, "Updated Pop-Out field: " + field);
        Check(screen.GetProperty("Instance", All) != null && screen.GetProperty("DisplayAvailable", All) != null, "Updated Pop-Out singleton/display accessors");
        Console.WriteLine("Native/plugin hook checks passed: " + checks + " assertions using beta IL and current Pop-Out metadata; no Unity gameplay execution.");
    }
}
