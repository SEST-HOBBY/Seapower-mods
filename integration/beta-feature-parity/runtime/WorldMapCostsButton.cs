using System;
using System.Linq;
using Noesis;

namespace Sest.RuntimeFixes;

// A normal button beside DCM's Economy control. Preserve every author's
// existing command and binding; the new entry opens the same F11 report.
internal static class WorldMapCostsButton
{
    private static FrameworkElement view;
    private static StackPanel strip;
    private static Button button;
    private static double nextProbe;
    private static bool failed;

    internal static void Ensure(FrameworkElement current, double now)
    {
        if (NoesisTeardown.InProgress || failed) return;
        if (ReferenceEquals(view, current) && button != null) return;
        if (now < nextProbe) return;
        nextProbe = now + 1;
        Remove();
        if (current == null || !current.IsLoaded) return;
        try
        {
            var economy = NativeCombatSurface.Walk(current).OfType<ToggleButton>().FirstOrDefault(b =>
                BindingOperations.GetBinding(b, ToggleButton.IsCheckedProperty)?.Path?.Path == "EconomyOpen");
            var parent = economy == null ? null : VisualTreeHelper.GetParent(economy) as StackPanel;
            if (parent == null) return;
            var entry = new Button {
                Name = "SestWorldCombatCosts", Focusable = false, Width = 44f, Height = 44f,
                Padding = new Thickness(0f),
                ToolTip = "Cumulative Combat Costs (F11): recorded weapons expenditure, losses and battle history in estimated USD.",
                Content = new TextBlock { Text = "Combat\nCosts", TextAlignment = TextAlignment.Center,
                    TextWrapping = TextWrapping.Wrap, FontSize = 10f, FontWeight = FontWeight.DemiBold }
            };
            if (current.TryFindResource("ToolButton") is Style style) entry.Style = style;
            entry.Click += Open;
            parent.Children.Insert(parent.Children.IndexOf(economy) + 1, entry);
            view = current; strip = parent; button = entry;
            Api.Log("world-map Combat Costs button attached beside Economy; F11 opens cumulative combat costs");
        }
        catch (Exception ex)
        {
            failed = true;
            Api.LogFailure("world-map cost shortcut unavailable; F11 retained", ex);
        }
    }

    private static void Open(object sender, RoutedEventArgs args)
    {
        WorldOperations.OpenCosts();
        args.Handled = true;
    }

    internal static void Remove()
    {
        if (!NoesisTeardown.InProgress && button != null)
        {
            button.Click -= Open;
            strip?.Children.Remove(button);
        }
        button = null; strip = null; view = null;
    }
}
