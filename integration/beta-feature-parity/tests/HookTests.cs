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
    static string Sha(string path)
    {
        using (var stream = File.OpenRead(path)) using (var sha = System.Security.Cryptography.SHA256.Create())
            return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
    }
    // UI 1.4.15 accepts Pop-Out Windows 1.1.3 and the captured 1.2.0. 1.2.0
    // moved its pop-out control into a shared title menu; the stock Formation
    // Manager must recognise that entry instead of a PopOutButton.
    static void PopOutTitleMenu(Assembly ui, Assembly pop)
    {
        const string PopOut113 = "5709ed68af4623fceee3f3badc8e06bdb9b98f8e095fb0deac2685a9ebc5fc36";
        string actual = Sha(pop.Location);
        var surface = ui.GetType("Sest.UiFixes.ContactsSurfaceFix", true);
        var accepted = (string[])surface.GetField("PopOutHashes", All).GetValue(null);
        Check(accepted.Length == 2 && accepted.Contains(PopOut113) && accepted.Contains(actual) && actual == "a8f1092ac247032219ebf00aa773b91d14f4bb4a7f2575ca1a4594da57abd882",
            "UI accepts exactly Pop-Out Windows 1.1.3 and the captured 1.2.0");
        Check((string)surface.GetMethod("RequirePopOut", All).Invoke(null, new object[] { pop }) == actual, "Contacts surface, Formation UI and compass gates admit the captured Pop-Out image");
        bool rejected = false;
        try { ui.GetType("Sest.UiFixes.ContactsFix", true).GetMethod("RequireAny", All).Invoke(null, new object[] { pop, new[] { PopOut113 } }); }
        catch (TargetInvocationException e) when (e.InnerException is InvalidOperationException) { rejected = true; }
        Check(rejected, "Any other Pop-Out image is still refused");
        var known = (string[][])ui.GetType("Sest.UiFixes.DiagnosticModules", true).GetField("Known", All).GetValue(null);
        Check(known.Single(k => k[0] == "SeaPowerPopOut").Skip(1).SequenceEqual(accepted), "Timing observations accept the same two Pop-Out images");

        var formation = ui.GetType("Sest.UiFixes.FormationUiMode", true);
        formation.GetMethod("BindTitleMenu", All).Invoke(null, new object[] { pop });
        Check(formation.GetField("titleEntries", All).GetValue(null) != null && formation.GetField("titleEntryId", All).GetValue(null) != null &&
            formation.GetField("titleLookup", All).GetValue(null) != null, "Formation UI mode binds Pop-Out 1.2.0's title-menu entries");
        var add = Body(M(pop, "SeaPowerPopOut.PopOutScreen", "AddButton"));
        Check(add.Count(i => i.opcode == OpCodes.Ldstr && (string)i.operand == "popout") == 1 &&
            add.Count(i => (i.operand as MethodInfo)?.DeclaringType.FullName == "SeaPowerPopOut.SmartWindows.TitleMenu" && ((MethodInfo)i.operand).Name == "Set") == 1 &&
            !add.Any(i => i.opcode == OpCodes.Ldstr && (string)i.operand == "PopOutButton"),
            "Pop-Out 1.2.0 adds its control as the 'popout' title-menu entry, not as a PopOutButton");
        var set = Body(M(pop, "SeaPowerPopOut.SmartWindows.TitleMenu", "Set"));
        Check(set.Count(i => i.opcode == OpCodes.Ldstr && (string)i.operand == "SmartWindowsMenuButton") == 2 &&
            set.Any(i => (i.operand as FieldInfo)?.Name == "Entries") && set.Any(i => i.opcode == OpCodes.Stfld && (i.operand as FieldInfo)?.Name == "Id"),
            "TitleMenu reuses one SmartWindowsMenuButton and records entries by Id in TitleMenu.Entries");
        Check(M(pop, "SeaPowerPopOut.SmartWindows.TitleBar", "FindButtonsPanel").GetMethodBody().GetILAsByteArray()
            .SequenceEqual(M(pop, "SeaPowerPopOut.PopOutScreen", "FindButtonsPanel").GetMethodBody().GetILAsByteArray()),
            "TitleMenu uses the same title-bar panel the Formation UI reads");
    }
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
        foreach (string method in new[] { "HostOpening", "Decorate", "Move", "Place", "Open", "Remember", "UpdateScreen", "FindButtonsPanel", "Flatten" })
            Check(screen.GetMethod(method, All) != null, "Updated Pop-Out method: " + method);
        foreach (string field in new[] { "host", "windows", "hint", "items" })
            Check(screen.GetField(field, All) != null, "Updated Pop-Out field: " + field);
        Check(screen.GetProperty("Instance", All) != null && screen.GetProperty("DisplayAvailable", All) != null, "Updated Pop-Out singleton/display accessors");
        PopOutTitleMenu(ui, pop);
        Console.WriteLine("Native/plugin hook checks passed: " + checks + " assertions using beta IL and current Pop-Out metadata; no Unity gameplay execution.");
    }
}
