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
    // R15's UI accepts only the captured Pop-Out Windows 1.4.0. Its pop-out
    // control is the "popout" entry of a shared title menu; the stock Formation
    // Manager must recognise that entry. 1.3.0's TitleMenu.Set also skips other
    // mods' windows (TitleMenu.Ours), so the runtime answers Ours for F11.
    static void PopOutTitleMenu(Assembly runtime, Assembly ui, Assembly pop)
    {
        const string PopOut123 = "6f3668aaebe366f4fecc3de5af6a1479f1765d50f176b2bd68b3434191ce3ce5";
        const string PopOut130 = "6372d8e8287bee780f5cd9b74417f11fef4cb35d355de2acd99105aa0a4acdd8";
        string actual = Sha(pop.Location);
        var surface = ui.GetType("Sest.UiFixes.ContactsSurfaceFix", true);
        var accepted = (string[])surface.GetField("PopOutHashes", All).GetValue(null);
        Check(accepted.Length == 1 && accepted[0] == actual && actual == PopOut130,
            "UI accepts exactly the captured Pop-Out Windows 1.4.0");
        Check((string)surface.GetMethod("RequirePopOut", All).Invoke(null, new object[] { pop }) == actual, "Contacts surface, Formation UI and compass gates admit the captured Pop-Out image");
        bool rejected = false;
        try { ui.GetType("Sest.UiFixes.ContactsFix", true).GetMethod("RequireAny", All).Invoke(null, new object[] { pop, new[] { PopOut123 } }); }
        catch (TargetInvocationException e) when (e.InnerException is InvalidOperationException) { rejected = true; }
        Check(rejected, "Any other Pop-Out image (here the former 1.2.3 pin) is refused");
        var known = (string[][])ui.GetType("Sest.UiFixes.DiagnosticModules", true).GetField("Known", All).GetValue(null);
        Check(known.Single(k => k[0] == "SeaPowerPopOut").Skip(1).SequenceEqual(accepted), "Timing observations accept the same Pop-Out image");

        var formation = ui.GetType("Sest.UiFixes.FormationUiMode", true);
        formation.GetMethod("BindTitleMenu", All).Invoke(null, new object[] { pop });
        Check(formation.GetField("titleEntries", All).GetValue(null) != null && formation.GetField("titleEntryId", All).GetValue(null) != null &&
            formation.GetField("titleLookup", All).GetValue(null) != null, "Formation UI mode binds Pop-Out 1.4.0's title-menu entries");
        var add = Body(M(pop, "SeaPowerPopOut.PopOutScreen", "AddButton"));
        Check(add.Count(i => i.opcode == OpCodes.Ldstr && (string)i.operand == "popout") == 1 &&
            add.Count(i => (i.operand as MethodInfo)?.DeclaringType.FullName == "SeaPowerPopOut.SmartWindows.TitleMenu" && ((MethodInfo)i.operand).Name == "Set") == 1 &&
            !add.Any(i => i.opcode == OpCodes.Ldstr && (string)i.operand == "PopOutButton"),
            "Pop-Out 1.4.0 adds its control as the 'popout' title-menu entry, not as a PopOutButton");
        var set = Body(M(pop, "SeaPowerPopOut.SmartWindows.TitleMenu", "Set"));
        Check(set.Count(i => i.opcode == OpCodes.Ldstr && (string)i.operand == "SmartWindowsMenuButton") == 2 &&
            set.Any(i => (i.operand as FieldInfo)?.Name == "Entries") && set.Any(i => i.opcode == OpCodes.Stfld && (i.operand as FieldInfo)?.Name == "Id"),
            "TitleMenu reuses one SmartWindowsMenuButton and records entries by Id in TitleMenu.Entries");
        Check(set.Take(8).Any(i => (i.operand as MethodInfo)?.Name == "Ours"), "1.3.0 TitleMenu.Set skips other mods' windows via Ours");
        // 1.3.0 removed PopOutScreen.FindButtonsPanel; the Formation UI now reads
        // the TitleBar copy, the same one TitleMenu.Set uses.
        var titleBar = M(pop, "SeaPowerPopOut.SmartWindows.TitleBar", "FindButtonsPanel");
        Check(titleBar != null && titleBar.IsStatic && set.Any(i => Equals(i.operand, titleBar)),
            "TitleMenu uses the same static title-bar panel lookup the Formation UI reads");

        // F11: the prefix on TitleMenu.Ours(Window) claims SEST's cost window
        // before Ours runs (and logs its "another mod's window" line).
        var ours = M(pop, "SeaPowerPopOut.SmartWindows.TitleMenu", "Ours");
        Check(ours != null && ours.IsStatic && ours.ReturnType == typeof(bool) && ours.GetParameters().Length == 1 &&
            ours.GetParameters()[0].ParameterType.FullName == "SeapowerUI.Window", "TitleMenu.Ours(SeapowerUI.Window) is the hooked target");
        var bridge = runtime.GetType("Sest.RuntimeFixes.PopOutBridge", true);
        var prefix = bridge.GetMethods(All).Single(m => m.Name == "OursForCosts");
        Check(prefix.ReturnType == typeof(bool) && prefix.GetParameters().Select(p => p.Name).SequenceEqual(new[] { "__0", "__result" }) &&
            prefix.GetParameters()[0].ParameterType == ours.GetParameters()[0].ParameterType && prefix.GetParameters()[1].ParameterType == typeof(bool).MakeByRefType(),
            "OursForCosts is a Harmony prefix over Ours' window argument and result");
        var costs = runtime.GetType("Sest.RuntimeFixes.CumulativeCombatCostsViewModel", true);
        var prefixBody = Body(prefix);
        Check(prefixBody.Any(i => i.opcode == OpCodes.Isinst && Equals(i.operand, costs)) &&
            prefixBody.Any(i => (i.operand as MethodInfo)?.Name == "get_DataContext"),
            "OursForCosts claims only windows whose DataContext is SEST's CumulativeCombatCostsViewModel");
        var args = new object[] { null, false };
        Check((bool)prefix.Invoke(null, args) && !(bool)args[1], "Any other window runs the original Ours and keeps its answer");
    }
    // Coordinated Strike pop-out: Pop-Out 1.4.0 cannot host the IMGUI F8
    // panel, so the runtime uses only its monitor surface and these members.
    static void StrikeSurface(Assembly runtime, Assembly pop)
    {
        var screen = pop.GetType("SeaPowerPopOut.PopOutScreen", true);
        Check(!pop.GetReferencedAssemblies().Any(r => r.Name == "UnityEngine.IMGUIModule"), "Pop-Out Windows 1.4.0 has no IMGUI path to host the F8 panel");
        Check(screen.GetField("screenDisplay", All)?.FieldType == typeof(int), "Pop-Out records the monitor it opened");
        // 1.3.0 moved the see-through list (keep) to ScreenCutOut, whose Collect returns it.
        var cut = pop.GetType("SeaPowerPopOut.ScreenCutOut", true);
        Check(cut.GetField("keep", All)?.FieldType.FullName.StartsWith("System.Collections.Generic.List`1[[UnityEngine.Rect,") == true &&
            cut.GetMethod("Collect", All)?.ReturnType == cut.GetField("keep", All).FieldType && screen.GetField("cutOut", All)?.FieldType == cut,
            "Pop-Out's see-through region is a List<UnityEngine.Rect> returned by PopOutScreen.cutOut's Collect");
        Check(screen.GetField("hint", All)?.FieldType.FullName == "Noesis.TextBlock", "Pop-Out's empty-monitor hint is a TextBlock");
        var late = Body(M(pop, "SeaPowerPopOut.PopOutScreen", "LateUpdate"));
        int collect = late.FindIndex(i => (i.operand as MethodInfo)?.DeclaringType == cut && ((MethodInfo)i.operand).Name == "Collect"),
            shape = late.FindIndex(i => (i.operand as MethodInfo)?.DeclaringType.FullName == "SeaPowerPopOut.MonitorWindow" && ((MethodInfo)i.operand).Name == "Shape");
        Check(collect >= 0 && shape > collect && late.Skip(collect + 1).Take(shape - collect - 1).All(i =>
                i.opcode == OpCodes.Ldarg_0 || (i.operand as FieldInfo)?.Name == "screenCamera" ||
                (i.operand as MethodInfo)?.Name == "get_pixelWidth" || (i.operand as MethodInfo)?.Name == "get_pixelHeight"),
            "The see-through region is Collect's result passed straight to MonitorWindow.Shape, so a Collect postfix can add the strike panel");
        var update = Body(M(pop, "SeaPowerPopOut.PopOutScreen", "UpdateScreen"));
        Check(update.Any(i => (i.operand as FieldInfo)?.Name == "hint") && update.Any(i => (i.operand as MethodInfo)?.Name == "set_Visibility"),
            "UpdateScreen resets the hint each frame; a postfix hides it while the strike panel is there");
        var claim = Body(M(pop, "SeaPowerPopOut.PopOutScreen", "ClaimMouse"));
        // 1.3.0 moved the Display.RelativeMouseAt call into GameMouse.OnDisplay.
        Check(claim.Any(i => (i.operand as MethodInfo)?.Name == "OnDisplay") && claim.Any(i => (i.operand as FieldInfo)?.Name == "screenDisplay") &&
            Body(M(pop, "SeaPowerPopOut.GameMouse", "OnDisplay")).Any(i => (i.operand as MethodInfo)?.Name == "RelativeMouseAt"),
            "Pop-Out claims the game mouse on its monitor through GameMouse.OnDisplay and Display.RelativeMouseAt");
        Check(M(pop, "SeaPowerPopOut.PopOutScreen", "Open").ReturnType == typeof(bool), "Pop-Out's Open reports whether its monitor surface is up");
        var bridge = runtime.GetType("Sest.RuntimeFixes.PopOutBridge", true);
        foreach (string member in new[] { "EnsureScreenBound", "HookStrikeSurface", "AfterCollect", "AfterUpdateScreen", "OursForCosts" })
            Check(bridge.GetMethods(All).Count(m => m.Name == member) == 1, "Runtime strike surface member, unique for Api.Hooks' by-name lookup: " + member);
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
        foreach (string method in new[] { "HostOpening", "Decorate", "Move", "Place", "Open", "Remember", "UpdateScreen" })
            Check(screen.GetMethod(method, All) != null, "Updated Pop-Out method: " + method);
        Check(pop.GetType("SeaPowerPopOut.SmartWindows.TitleBar", true).GetMethod("FindButtonsPanel", All)?.IsStatic == true &&
            pop.GetType("SeaPowerPopOut.ScreenResources", true).GetMethod("Flatten", All)?.IsStatic == true, "1.3.0 moved FindButtonsPanel/Flatten");
        Check(pop.GetType("SeaPowerPopOut.ScreenCutOut", true).GetProperty("Windows", All)?.PropertyType.FullName.StartsWith("System.Collections.Generic.List`1[[SeapowerUI.Window,") == true,
            "1.3.0 tracks pop-out windows in ScreenCutOut.Windows");
        foreach (string field in new[] { "host", "cutOut", "hint", "items" })
            Check(screen.GetField(field, All) != null, "Updated Pop-Out field: " + field);
        Check(screen.GetProperty("Instance", All) != null && screen.GetProperty("DisplayAvailable", All) != null, "Updated Pop-Out singleton/display accessors");
        PopOutTitleMenu(runtime, ui, pop);
        StrikeSurface(runtime, pop);
        Console.WriteLine("Native/plugin hook checks passed: " + checks + " assertions using beta IL and current Pop-Out metadata; no Unity gameplay execution.");
    }
}
