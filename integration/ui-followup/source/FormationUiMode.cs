using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using HarmonyLib;
using Noesis;
using SeaPower;
using SeapowerUI;
using SeapowerUI.ViewModels;
using UnityEngine;
using GameWindow = SeapowerUI.Window;
using Environment = System.Environment;

namespace Sest.UiFixes
{
    internal static class FormationUiMode
    {
        const BindingFlags All = ContactsFix.All;
        const string FormationHash = "6230e8e78e2ba7ba222241d0c3dcc881d2507ebeeb4eab24b6401cc9144283dd";
        static readonly FormationModeState mode = new FormationModeState();
        static ConditionalWeakTable<object, Entry> entries = new ConditionalWeakTable<object, Entry>();
        static PropertyInfo ready;
        static FieldInfo barField, barWindowField, controllerMainField, squadsField, enabledField, stateField, toolbarField;
        static MethodInfo detach, setVisible, findButtons, decorate, contains;
        static PropertyInfo popRoot, popInstance;
        static bool loaded, reported;
        static float nextUiTick;
        static string preferencePath;

        sealed class Entry
        {
            internal GameWindow Window;
            internal Button Button;
            internal Placement Stock, Enhanced, PendingPlacement;
            internal readonly LookupCache<GameWindow> Lookup = new LookupCache<GameWindow>();
            internal object Template;
            internal bool PartsStock;
            internal float NextParts;
            internal Panel Tools;
            internal Grid Chrome;
            internal ContentPresenter Presenter;
            internal Thumb Header;
            internal void ClearParts()
            {
                Button = null; Template = null; Tools = null; Chrome = null;
                Presenter = null; Header = null; NextParts = 0;
            }
        }

        sealed class Placement
        {
            internal float X, Y, Width, Height;
            internal bool AnchorRight, AnchorBottom;
            internal static Placement Capture(GameWindow w)
            {
                return new Placement { X = w.X, Y = w.Y, AnchorRight = w.AnchorRight, AnchorBottom = w.AnchorBottom,
                    Width = Valid(w.Width) ? w.Width : (Valid(w.ActualWidth) ? w.ActualWidth : 420),
                    Height = Valid(w.Height) ? w.Height : (Valid(w.ActualHeight) ? w.ActualHeight : 360) };
            }
            internal void Apply(GameWindow w, FrameworkElement bounds)
            {
                float width = Math.Max(Math.Max(100, w.MinWidth), Width);
                float height = Math.Max(Math.Max(100, w.MinHeight), Height);
                w.AnchorRight = AnchorRight; w.AnchorBottom = AnchorBottom;
                if (Valid(w.MaxWidth)) width = Math.Min(width, w.MaxWidth);
                if (Valid(w.MaxHeight)) height = Math.Min(height, w.MaxHeight);
                if (bounds != null && Valid(bounds.ActualWidth) && Valid(bounds.ActualHeight))
                {
                    width = Math.Min(width, bounds.ActualWidth);
                    height = Math.Min(height, bounds.ActualHeight);
                    w.X = Math.Max(0, Math.Min(Finite(X) ? X : 8, bounds.ActualWidth - width));
                    w.Y = Math.Max(0, Math.Min(Finite(Y) ? Y : 8, bounds.ActualHeight - height));
                }
                else { w.X = Math.Max(0, Finite(X) ? X : 8); w.Y = Math.Max(0, Finite(Y) ? Y : 8); }
                w.Width = width; w.Height = height;
                // The enhanced controller positions with a margin as well as X/Y.
                // The native window positions itself from X/Y and has its own margin.
                if (!mode.Stock) w.Margin = new Thickness(w.X, w.Y, 0, 0);
            }
        }

        static bool Finite(float value) { return !float.IsNaN(value) && !float.IsInfinity(value); }
        static bool Valid(float value) { return Finite(value) && value > 0; }
        static bool Ready { get { return ready != null && (bool)ready.GetValue(null, null); } }

        internal static void Install()
        {
            var harmony = new Harmony("io.github.sest-hobby.formation-ui-mode");
            try
            {
                var controller = ContactsFix.Find("SeaPowerSquadPanel.SquadManagerController");
                ContactsFix.Require(controller.Assembly, FormationHash);
                var plugin = ContactsFix.Find("SeaPowerSquadPanel.Plugin");
                var bar = ContactsFix.Find("SeaPowerSquadPanel.SquadBarController");
                var tools = ContactsFix.Find("SeaPowerSquadPanel.SquadBarTools");
                var pop = ContactsFix.Find("SeaPowerPopOut.PopOutScreen");
                ContactsFix.Require(pop.Assembly, ContactsSurfaceFix.PopOutHash);
                ready = ContactsFix.Find("Sest.RuntimeFixes.NativeCombatSurface").GetProperty("Ready", All);
                barField = controller.GetField("_bar", All);
                controllerMainField = controller.GetField("_main", All);
                barWindowField = bar.GetField("_window", All);
                squadsField = plugin.GetField("_squads", All);
                enabledField = plugin.GetField("_enabled", All);
                toolbarField = tools.GetField("_tools", All);
                stateField = controller.GetField("_state", All);
                setVisible = stateField.FieldType.GetMethod("SetVisible", All);
                detach = controller.GetMethod("Detach", All);
                findButtons = pop.GetMethod("FindButtonsPanel", All);
                decorate = pop.GetMethod("Decorate", All);
                popInstance = pop.GetProperty("Instance", All);
                var bridge = ContactsFix.Find("Sest.RuntimeFixes.PopOutBridge");
                contains = bridge.GetMethod("Contains", All);
                popRoot = bridge.GetProperty("Root", All);
                if (ready == null || barField == null || controllerMainField == null || barWindowField == null || squadsField == null || enabledField == null ||
                    stateField == null || setVisible == null || detach == null || findButtons == null || decorate == null ||
                    popInstance == null || contains == null || popRoot == null || toolbarField == null)
                    throw new MissingMemberException("Inspected Formation Manager stock/enhanced controls");
                preferencePath = System.IO.Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
                    "AppData", "LocalLow", "Triassic Games", "Sea Power", "SEST", "formation-ui-mode-v1.txt");
                var prefix = new HarmonyMethod(typeof(FormationUiMode), nameof(BeforePanelTick)) { priority = Priority.Last };
                harmony.Patch(controller.GetMethod("Tick", All), prefix: prefix);
                harmony.Patch(plugin.GetMethod("LateUpdate", All),
                    postfix: new HarmonyMethod(typeof(FormationUiMode), nameof(AfterPluginTick)) { priority = Priority.Last });
                harmony.Patch(tools.GetMethod("RefreshAppearance", All),
                    prefix: new HarmonyMethod(typeof(FormationUiMode), nameof(KeepToolbarVisible)));
                ContactsFix.Log("Formation UI mode control installed: cached Stock UI / Enhanced UI controls; mission/host/template invalidation, map grouping retained.");
            }
            catch (Exception error)
            {
                harmony.UnpatchSelf();
                ContactsFix.Log("Formation UI mode inactive; original Group Manager retained: " + error.Message);
            }
        }

        static void LoadPreference()
        {
            if (loaded) return;
            loaded = true;
            try { mode.Restore(File.Exists(preferencePath) ? File.ReadAllText(preferencePath) : null); }
            catch (Exception error) { Warn("Could not read UI choice; enhanced layout retained", error); }
        }

        static void SavePreference()
        {
            try
            {
                Directory.CreateDirectory(System.IO.Path.GetDirectoryName(preferencePath));
                File.WriteAllText(preferencePath, mode.Encode() + Environment.NewLine);
            }
            catch (Exception error) { Warn("UI choice changed for this session but could not be saved", error); }
        }

        // Do not set the author's Grid.Enabled: it controls both panel AND map
        // grouping. Gate just SquadManagerController.Tick when stock is selected.
        public static bool BeforePanelTick(object __instance, MainGameViewModel __0)
        {
            bool previous = mode.Stock;
            try
            {
                if (!Ready || __0 == null) return true;
                LoadPreference();
                previous = mode.Stock;
                var entry = entries.GetValue(__instance, _ => new Entry());
                var bar = ReferenceEquals(controllerMainField.GetValue(__instance), __0) ? barField.GetValue(__instance) : null;
                GameWindow window = ResolveWindow(__0, entry, bar);
                if (window != null && window.Maximized && mode.Pending.HasValue)
                    return !mode.Stock; // Keep a request pending until the window is restored.
                bool changed = mode.Commit();
                if (changed && !mode.Stock && window != null)
                {
                    entry.Stock = Placement.Capture(window);
                    entry.PendingPlacement = entry.Enhanced;
                    // A stock window opened after a save load must stay open when
                    // the enhanced visibility helper reattaches to the native button.
                    setVisible.Invoke(stateField.GetValue(__instance), new object[] { window.IsVisible });
                }
                if (mode.Stock && bar != null)
                {
                    if (window != null) entry.Enhanced = Placement.Capture(window);
                    detach.Invoke(__instance, null); // Original mod restores rows, templates and native chrome.
                    if (window != null)
                    {
                        var native = entry.Stock ?? Placement.Capture(window);
                        if (entry.Stock == null && entry.Enhanced != null)
                        {
                            native.X = entry.Enhanced.X; native.Y = entry.Enhanced.Y;
                            native.AnchorRight = entry.Enhanced.AnchorRight; native.AnchorBottom = entry.Enhanced.AnchorBottom;
                        }
                        entry.PendingPlacement = native;
                    }
                    entry.ClearParts();
                }
                if (changed)
                {
                    SavePreference();
                    ContactsFix.Log("Formation Manager switched to " + mode.Encode() + " UI; native model and current screen retained.");
                }
                return !mode.Stock;
            }
            catch (Exception error)
            {
                mode.Restore(previous ? "stock" : "enhanced");
                Warn("Formation layout switch failed; previous mode retained", error);
                return !mode.Stock;
            }
        }

        public static void AfterPluginTick(object __instance)
        {
            try
            {
                if (!Ready || Time.unscaledTime < nextUiTick) return;
                nextUiTick = Time.unscaledTime + 0.2f;
                var config = enabledField.GetValue(__instance);
                if (config == null || !(bool)config.GetType().GetProperty("Value").GetValue(config, null)) return;
                var controller = squadsField.GetValue(__instance);
                var main = Globals._mainGameViewModel;
                if (controller == null || main == null) return;
                LoadPreference();
                var entry = entries.GetValue(controller, _ => new Entry());
                var bar = ReferenceEquals(controllerMainField.GetValue(controller), main) ? barField.GetValue(controller) : null;
                var window = ResolveWindow(main, entry, bar);
                if (window == null || !window.IsVisible) return;
                if (!ReferenceEquals(entry.Window, window) || !ReferenceEquals(entry.Template, window.Template) || entry.PartsStock != mode.Stock)
                {
                    entry.ClearParts(); entry.Window = window; entry.Template = window.Template; entry.PartsStock = mode.Stock;
                }
                if (entry.Tools != null && !entry.Tools.IsDescendantOf(window)) entry.ClearParts();
                if (entry.Tools == null)
                {
                    if (Time.unscaledTime < entry.NextParts) return;
                    entry.NextParts = Time.unscaledTime + 0.5f;
                    if (!mode.Stock && bar != null)
                    {
                        foreach (var part in Walk(window))
                        {
                            if (part is StackPanel p && p.Name == "AirSquadTools") entry.Tools = p;
                            if (part is Grid g && g.Name == "AirSquadBackdrop") entry.Chrome = g;
                            if (entry.Tools != null && entry.Chrome != null) break;
                        }
                        if (entry.Chrome != null)
                            entry.Presenter = entry.Chrome.Children.Cast<UIElement>().OfType<ContentPresenter>().FirstOrDefault();
                    }
                    else
                    {
                        entry.Tools = findButtons.Invoke(null, new object[] { window }) as Panel;
                        entry.Header = Walk(window).OfType<Thumb>().FirstOrDefault(t => t.Name == "HeaderThumb");
                    }
                }
                var tools = entry.Tools;
                if (tools == null) return;
                if (!mode.Stock && bar != null)
                {
                    var toolbar = tools as StackPanel;
                    if (toolbar == null || entry.Chrome == null) { entry.Tools = null; return; }
                    // Reuse the existing 24 px tool row at the top. Moving its
                    // reserved margin from bottom to top keeps the content area size.
                    var margin = new Thickness(0, 24, 14, 0);
                    if (entry.Presenter != null && !entry.Presenter.Margin.Equals(margin)) entry.Presenter.Margin = margin;
                    if (toolbar.VerticalAlignment != VerticalAlignment.Top) toolbar.VerticalAlignment = VerticalAlignment.Top;
                    margin = new Thickness(0, 1, 20, 0);
                    if (!toolbar.Margin.Equals(margin)) toolbar.Margin = margin;
                    if (toolbar.Opacity != 1) toolbar.Opacity = 1;
                    if (!toolbar.IsHitTestVisible) toolbar.IsHitTestVisible = true;
                }
                else
                {
                    // Swapping templates does not reload the Window itself.
                    // Rebind native drag/scroll/resize parts only when the
                    // restored header differs from the game's cached one.
                    var header = entry.Header;
                    if (header != null && header != window.HeaderThumb) window.OnInitialized();
                    if (!tools.Children.Cast<UIElement>().OfType<FrameworkElement>().Any(b => b.Name == "PopOutButton"))
                    {
                        var screen = popInstance.GetValue(null, null);
                        if (screen != null) decorate.Invoke(screen, new object[] { window });
                    }
                }

                if (entry.Button == null || ContactsFix.UiParent(entry.Button) != tools)
                {
                    entry.Button = tools.Children.Cast<UIElement>().OfType<Button>().FirstOrDefault(b => b.Name == "SestFormationUiMode");
                    if (entry.Button == null)
                    {
                        entry.Button = (Button)Noesis.GUI.ParseXaml("<Button xmlns='http://schemas.microsoft.com/winfx/2006/xaml/presentation' Name='SestFormationUiMode' Height='20' Margin='0,0,3,0' FontSize='11' Padding='3,0' Focusable='False'/>");
                        entry.Button.Click += OnToggle;
                        int index = 0;
                        for (int i = 0; i < tools.Children.Count; i++)
                            if (tools.Children[i] is FrameworkElement f && (f.Name == "SestFormationPopOut" || f.Name == "PopOutButton"))
                            { index = i + 1; break; }
                        tools.Children.Insert(index, entry.Button);
                    }
                }
                bool compact = !mode.Stock && Valid(window.ActualWidth) && window.ActualWidth < 240;
                float buttonWidth = compact ? 32 : 88;
                if (entry.Button.Width != buttonWidth) entry.Button.Width = buttonWidth;
                string label = compact ? "UI" : (mode.Stock ? "Enhanced UI" : "Stock UI");
                if (!Equals(entry.Button.Content, label)) entry.Button.Content = label;
                string tip = window.Maximized ? "Restore the window before switching its layout" :
                    (mode.Stock ? "Switch to the enhanced Formation Manager" : "Restore the original Formation Manager; map icon grouping stays as configured");
                if (!Equals(entry.Button.ToolTip, tip)) entry.Button.ToolTip = tip;
                if (entry.Button.IsEnabled == window.Maximized) entry.Button.IsEnabled = !window.Maximized;
                if (entry.PendingPlacement != null && (mode.Stock || bar != null))
                {
                    FrameworkElement bounds = IsPopped(main.FormationManager) ? ContactsSurfaceFix.Surface() : MainGameView.Instance;
                    entry.PendingPlacement.Apply(window, bounds);
                    entry.PendingPlacement = null;
                }
            }
            catch (Exception error) { Warn("Formation UI control could not be refreshed", error); }
        }

        static void OnToggle(object sender, RoutedEventArgs args)
        {
            mode.Toggle(); // Never detach or rebuild a template during a routed click.
            args.Handled = true;
        }

        public static bool KeepToolbarVisible(object __instance)
        {
            try
            {
                if (!Ready || mode.Stock) return true;
                var toolbar = toolbarField.GetValue(__instance) as StackPanel;
                if (toolbar == null || !toolbar.Children.Cast<UIElement>().OfType<FrameworkElement>().Any(e => e.Name == "SestFormationUiMode")) return true;
                if (toolbar.Opacity != 1) toolbar.Opacity = 1;
                if (!toolbar.IsHitTestVisible) toolbar.IsHitTestVisible = true;
                return false; // Avoid hiding it only to reveal it again in a postfix.
            }
            catch (Exception error) { Warn("Formation toolbar could not be refreshed", error); return true; }
        }

        static bool IsPopped(object model) { return model != null && (bool)contains.Invoke(null, new[] { model }); }

        internal static void ClearCaches()
        {
            entries = new ConditionalWeakTable<object, Entry>();
            nextUiTick = 0;
        }

        static GameWindow ResolveWindow(MainGameViewModel main, Entry entry, object bar)
        {
            if (main.FormationManager == null) return null;
            FrameworkElement root = IsPopped(main.FormationManager) ? popRoot.GetValue(null, null) as FrameworkElement : MainGameView.Instance;
            var hint = bar == null ? null : barWindowField.GetValue(bar) as GameWindow;
            return entry.Lookup.Resolve(main.FormationManager, root, Time.unscaledTime, hint,
                w => ReferenceEquals(w.DataContext, main.FormationManager) && w.IsDescendantOf(root),
                () => Walk(root).OfType<GameWindow>().FirstOrDefault(w => ReferenceEquals(w.DataContext, main.FormationManager)));
        }

        static IEnumerable<DependencyObject> Walk(DependencyObject root)
        {
            if (root == null) yield break;
            var queue = new Queue<DependencyObject>(); queue.Enqueue(root);
            int count = 0;
            while (queue.Count > 0 && count++ < 20000)
            {
                var item = queue.Dequeue(); yield return item;
                for (int i = 0; i < VisualTreeHelper.GetChildrenCount(item); i++) queue.Enqueue(VisualTreeHelper.GetChild(item, i));
            }
        }

        static void Warn(string message, Exception error)
        {
            if (reported) return;
            reported = true;
            while (error is TargetInvocationException && error.InnerException != null) error = error.InnerException;
            ContactsFix.Log(message + ": " + error.GetType().Name + ": " + error.Message);
        }
    }
}
