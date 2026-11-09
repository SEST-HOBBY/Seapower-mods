using System;
using System.IO;
using System.Reflection;
using System.Runtime.Serialization;
using System.Windows.Input;

static class WorldBattleFlowTests
{
    const BindingFlags All = BindingFlags.Instance | BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic;
    static int checks;
    static void Check(bool ok, string reason) { checks++; if (!ok) throw new Exception(reason); }
    static object Call(object target, string name, params object[] args) =>
        (target as Type ?? target.GetType()).GetMethod(name, All).Invoke(target is Type ? null : target, args);
    static void Set(object target, string name, object value) => target.GetType().GetField(name, All).SetValue(target, value);
    sealed class OriginalCommand : ICommand
    {
        internal int Executed;
        public event EventHandler CanExecuteChanged { add { } remove { } }
        public bool CanExecute(object value) => true;
        public void Execute(object value) { Executed++; }
    }
    static void Main(string[] args)
    {
        string refs = Path.GetFullPath(args[0]);
        AppDomain.CurrentDomain.AssemblyResolve += (s, e) => {
            string file = Path.Combine(refs, new AssemblyName(e.Name).Name + ".dll");
            return File.Exists(file) ? Assembly.LoadFrom(file) : null;
        };
        var ui = Assembly.LoadFrom(Path.GetFullPath(args[1]));
        var gateType = ui.GetType("Sest.UiFixes.WorldBattleOpeningGate", true);
        object gate = Activator.CreateInstance(gateType, true), first = new object(), replay = new object();
        Func<object, bool, bool, double, bool, bool> offer = (g, world, ready, elapsed, paused) =>
            (bool)Call(gate, "Offer", g, world, ready, elapsed, paused);
        Check(!offer(first, true, false, 0, true), "Loading a battle must not consume its opening checklist");
        Check(offer(first, true, true, 0, true), "A fully loaded paused opening offers preparation");
        Check(!offer(first, true, true, 0, true), "Closing preparation while still paused cannot reopen it");
        Check(offer(replay, true, true, 0, true), "A restarted mission gets its own opening checklist");
        Check(!offer(new object(), false, true, 0, true), "Ordinary missions and the strategy map are untouched");
        Check(offer(first, true, true, 0, true), "A later world battle is offered preparation after map return");
        object resumed = new object();
        Check(!offer(resumed, true, true, 400, true), "A paused mid-battle save must not be interrupted");
        Check(!offer(resumed, true, true, 0, true), "Later clock changes cannot invent a new opening");
        object unpaused = new object();
        Check(!offer(unpaused, true, true, 0, false), "An explicit player unpause is respected");
        Check(!offer(unpaused, true, true, 0, true), "Pausing again cannot reintroduce opening setup");
        Check(!offer(null, true, true, 0, true), "A missing game cannot show preparation");
        Check(!offer(new object(), true, true, double.NaN, true), "Invalid mission time cannot create an opening");
        Call(gate, "Reset");
        Check(offer(first, true, true, 0, true), "Scene teardown clears the one-time opening gate");

        var flow = ui.GetType("Sest.UiFixes.WorldBattleFlow", true);
        var campaign = Assembly.LoadFrom(Path.GetFullPath(args[2]));
        Check((bool)Call(flow, "Bind", campaign), "Current DCM, native pause-menu and game lifecycle bindings resolve");
        Check(!(bool)Call(flow, "Bind", ui), "An uninspected optional mod cannot install world-battle hooks");
        var native = Assembly.LoadFrom(Path.Combine(refs, "Seapower-Scripts.dll"));
        var buttonType = native.GetType("SeapowerUI.ViewModels.PauseMenuButton", true);
        var original = new OriginalCommand();
        object button = FormatterServices.GetUninitializedObject(buttonType);
        Set(button, "contentSection", "PauseMenu"); Set(button, "contentKey", "Exit");
        Set(button, "buttonContent", "Exit"); Set(button, "<ButtonCommand>k__BackingField", original);
        Set(button, "<ButtonEnabled>k__BackingField", false); Set(button, "<ButtonVisible>k__BackingField", true);
        Call(flow, "Relabel", button, false);
        Check((string)buttonType.GetProperty("ButtonContent").GetValue(button, null) == "Exit", "Normal mission Exit caption stays unchanged");
        Call(flow, "Relabel", button, true);
        Check((string)buttonType.GetProperty("ButtonContent").GetValue(button, null) == "End battle...", "World battle Exit is clearly named");
        Check(ReferenceEquals(buttonType.GetProperty("ButtonCommand").GetValue(button, null), original), "Original native exit command is retained by identity");
        Check(!(bool)buttonType.GetProperty("ButtonEnabled").GetValue(button, null) &&
            (bool)buttonType.GetProperty("ButtonVisible").GetValue(button, null), "Presentation does not bypass native availability");
        Check(original.Executed == 0, "Relabelling cannot execute the exit action");
        Set(button, "contentKey", "RestartMission"); Set(button, "buttonContent", "Restart");
        Call(flow, "Relabel", button, true);
        Check((string)buttonType.GetProperty("ButtonContent").GetValue(button, null) == "Restart", "Other pause-menu actions retain their wording and commands");

        var text = ui.GetType("Sest.UiFixes.UiText", true);
        const string warning = "Unresolved combat will be assessed by the campaign.";
        string clarified = (string)Call(text, "WorldExitQuestion", warning, false);
        Check(clarified.EndsWith(warning, StringComparison.Ordinal), "The complete original campaign consequence warning is preserved");
        Check((string)Call(text, "WorldExitQuestion", warning, true) == clarified, "Both native debrief BackEnabled states keep the clarification and complete original warning");
        Check(Call(text, "WorldExitQuestion", null, false) == null, "No missing confirmation is fabricated");
        Console.WriteLine("World battle opening, replay, native exit-command preservation and binding checks passed: " + checks);
    }
}
