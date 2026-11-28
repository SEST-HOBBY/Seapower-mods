using System;
using System.Collections;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using AnchorChain;
using Noesis;

namespace Sest.RuntimeFixes;

// GCO only: a Blue/Red choice on Dynamic Campaign Mod's start page (owner,
// 28 Nov 2026: "cant seem to change sides"). DCM 1.0.4 shows no side choice:
// StartScreenViewModel's constructor takes CampaignDefinition.PlayerSide(null),
// the first playable side, and writes its id to StartOptions.PlayerSideId,
// which is what Theatre Commander starts with. While the start page of this
// world is being built, and only then, a null request is answered with the
// side chosen here, through PlayerSide's own argument, so DCM's own lookup
// still picks and checks the side. A click rebuilds the page with DCM's own
// StartScreen.Show after putting the campaign menu back as the current window,
// so the page's Back still returns to the campaign menu. Career is unchanged:
// it starts from the navy chosen on DCM's next page. No file, save or DCM
// state is written; another campaign's page is never touched.
internal static class WorldSideChoice
{
    private const string CampaignHash = "b816459dba7fb76b56460006aeabd4e5cce0fe930f8025a72b040af039d07c25";
    private const string CampaignId = "sest.world_sandbox_2028.regional";
    private const string HarmonyId = "io.github.sest-hobby.world-side-choice";
    private const string Retained = "Dynamic Campaign Mod's own start page retained";
    internal static readonly string[] SideIds = { "blue", "red" };
    internal const string RowName = "SestWorldSideChoice";
    private static Assembly game;
    private static MethodInfo show, playerSide;
    private static FieldInfo definitionId, sides, sideId, sideName, sideColour;
    private static PropertyInfo menuInstance, currentWindow;
    private static object campaignMenu, campaign;
    private static string chosen = SideIds[0];
    private static bool building, waiting, stopped, installed;
    private static double nextBind;
    private static double Now => (double)Stopwatch.GetTimestamp() / Stopwatch.Frequency;

    internal static string Chosen => chosen;

    // As WorldStorms.Start: now if DCM is loaded, else when its assembly
    // loads, with GameMain.Update every 2 s as the fallback.
    internal static void Start(Assembly native)
    {
        game = native;
        try
        {
            if (TryBind()) return;
            waiting = true;
            AppDomain.CurrentDomain.AssemblyLoad += Loaded;
            Api.Postfix(Api.Method(Api.Type(native, "SeaPower.GameMain"), "Update", typeof(void)), typeof(WorldSideChoice), nameof(Poll), HarmonyId + ".bootstrap");
        }
        catch (Exception ex) { Stop(ex); }
    }

    private static void Loaded(object sender, AssemblyLoadEventArgs args)
    {
        try
        {
            if (waiting && args.LoadedAssembly.GetType("DynamicCampaignMod.UI.Start.StartScreen", false) != null) { nextBind = 0; Poll(); }
        }
        catch (Exception ex) { Stop(ex); }
    }

    internal static void Poll()
    {
        if (!waiting || stopped || Now < nextBind) return;
        nextBind = Now + 2;
        try { TryBind(); }
        catch (Exception ex) { Stop(ex); }
    }

    private static bool TryBind()
    {
        var a = AppDomain.CurrentDomain.GetAssemblies().FirstOrDefault(x => x.GetType("DynamicCampaignMod.UI.Start.StartScreen", false) != null);
        if (a == null) return false;
        waiting = false;
        AppDomain.CurrentDomain.AssemblyLoad -= Loaded;
        Bind(a);
        Install();
        return true;
    }

    // Hash-locked; every member is checked before anything is patched.
    internal static void Bind(Assembly a)
    {
        using (var sha = SHA256.Create())
        using (var stream = File.OpenRead(BetaAssemblyPolicy.OriginalLocation(a)))
            if (BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant() != CampaignHash)
                throw new InvalidOperationException("the GCO side choice requires the inspected Dynamic Campaign Mod 1.0.4 image (b816459d)");
        var definition = a.GetType("DynamicCampaignMod.Core.Data.CampaignDefinition", true);
        var side = a.GetType("DynamicCampaignMod.Core.Data.SideDefinition", true);
        show = a.GetType("DynamicCampaignMod.UI.Start.StartScreen", true).GetMethod("Show", Api.All, null, new[] { definition }, null);
        if (show == null || !show.IsStatic || show.ReturnType != typeof(void)) throw new MissingMemberException("captured StartScreen.Show(CampaignDefinition)");
        playerSide = definition.GetMethod("PlayerSide", Api.All, null, new[] { typeof(string) }, null);
        if (playerSide == null || playerSide.IsStatic || playerSide.ReturnType != side || playerSide.GetParameters()[0].Name != "requestedId")
            throw new MissingMemberException("captured CampaignDefinition.PlayerSide(string requestedId)");
        definitionId = definition.GetField("id", Api.All);
        sides = definition.GetField("sides", Api.All);
        sideId = side.GetField("id", Api.All);
        sideName = side.GetField("name", Api.All);
        sideColour = side.GetField("color", Api.All);
        if (definitionId?.FieldType != typeof(string) || sides == null || !typeof(IEnumerable).IsAssignableFrom(sides.FieldType) ||
            sideId?.FieldType != typeof(string) || sideName?.FieldType != typeof(string) || sideColour?.FieldType != typeof(string))
            throw new MissingMemberException("captured CampaignDefinition.id/sides and SideDefinition.id/name/color");
        var menu = (game ?? a).GetType("SeapowerUI.ViewModels.MenuSystemViewModel", false) ?? Api.FindType("SeapowerUI.ViewModels.MenuSystemViewModel");
        var singleton = (game ?? a).GetType("SeaPower.Singleton`1", false) ?? Api.FindType("SeaPower.Singleton`1");
        menuInstance = singleton.MakeGenericType(menu).GetProperty("Instance", Api.All);
        currentWindow = menu.GetProperty("CurrentWindow", Api.All);
        if (menuInstance?.GetGetMethod(true)?.IsStatic != true || currentWindow?.PropertyType != typeof(object) || currentWindow.GetSetMethod(true) == null)
            throw new MissingMemberException("captured MenuSystemViewModel.Instance and CurrentWindow");
    }

    private static void Install()
    {
        if (installed || stopped || show == null) return;
        installed = true;
        Api.Hooks(show, typeof(WorldSideChoice), nameof(BeforeShow), nameof(AfterShow), HarmonyId, nameof(FinishShow));
        Api.Hooks(playerSide, typeof(WorldSideChoice), nameof(BeforePlayerSide), null, HarmonyId);
        Api.Log("GCO side choice installed: Blue or Red on Global Command Operations' start page; other campaigns' start pages unchanged");
    }

    private static void Stop(Exception ex)
    {
        bool first = !stopped;
        stopped = true; waiting = false; building = false;
        if (first) Api.LogFailure("GCO side choice unavailable; " + Retained, ex);
    }

    internal static bool IsWorld(object definition) =>
        definition != null && definitionId != null && definitionId.GetValue(definition) as string == CampaignId;

    // Prefix on StartScreen.Show. DCM keeps the current window (the campaign
    // menu) for the page's Back; a rebuild puts it back first, so it is the
    // same window every time.
    internal static void BeforeShow(object __0)
    {
        building = false;
        if (stopped || !IsWorld(__0)) return;
        try
        {
            campaign = __0;
            campaignMenu = currentWindow.GetValue(menuInstance.GetValue(null, null), null);
            building = true;
        }
        catch (Exception ex) { Stop(ex); }
    }

    // Prefix on CampaignDefinition.PlayerSide: only the start page's own
    // null request, only while this world's page is being built.
    internal static void BeforePlayerSide(object __instance, ref string __0)
    {
        if (building && __0 == null && !stopped && ReferenceEquals(__instance, campaign)) __0 = chosen;
    }

    internal static void FinishShow(Exception __exception)
    {
        building = false;
    }

    internal static void AfterShow(object __0)
    {
        if (stopped || !IsWorld(__0)) return;
        try
        {
            var page = currentWindow.GetValue(menuInstance.GetValue(null, null), null) as ContentControl;
            var column = ((page?.Content as FrameworkElement)?.FindName("CampaignScroll") as ScrollViewer)?.Content as StackPanel;
            if (column == null) throw new MissingMemberException("captured start page column CampaignScroll");
            if (column.Children.OfType<FrameworkElement>().Any(e => e.Name == RowName)) return;
            var flags = column.Children.OfType<WrapPanel>().FirstOrDefault();
            int at = flags == null ? Math.Min(1, column.Children.Count) : column.Children.IndexOf(flags) + 1;
            column.Children.Insert(at, Row(__0, column));
        }
        catch (Exception ex) { Stop(ex); }
    }

    private static FrameworkElement Row(object definition, FrameworkElement scope)
    {
        var row = new WrapPanel { Name = RowName, Orientation = Orientation.Horizontal, Margin = new Thickness(0f, 10f, 0f, 2f) };
        var label = new TextBlock { Text = "COMMAND", FontSize = 12f, FontWeight = FontWeight.DemiBold, VerticalAlignment = VerticalAlignment.Center,
            Margin = new Thickness(0f, 0f, 10f, 4f), Foreground = Ink("#FFB8C2C8") };
        row.Children.Add(label);
        foreach (var s in ((IEnumerable)sides.GetValue(definition)).Cast<object>())
        {
            string id = sideId.GetValue(s) as string;
            if (Array.IndexOf(SideIds, id) < 0) continue;
            bool on = id == chosen;
            string colour = sideColour.GetValue(s) as string;
            var button = new Button {
                Focusable = false, Tag = id, Margin = new Thickness(0f, 0f, 8f, 4f), Padding = new Thickness(12f, 5f, 12f, 5f),
                Background = on ? Ink(Opaque(colour, "#FF4A90E2")) : Ink("#FF1C2328"),
                BorderBrush = Ink(Opaque(colour, "#FF8A949A")), BorderThickness = new Thickness(on ? 2f : 1f),
                ToolTip = on ? "You command " + sideName.GetValue(s) + " as Theatre Commander." :
                    "Command " + sideName.GetValue(s) + " instead. Theatre Commander starts with this coalition; a Career starts from the navy you choose on the next page.",
                Content = new TextBlock { Text = Label(id, sideName.GetValue(s) as string), FontSize = 13f,
                    FontWeight = on ? FontWeight.DemiBold : FontWeight.Normal, Foreground = Ink("#FFFFFFFF") }
            };
            button.Click += Pick;
            row.Children.Add(button);
        }
        return row;
    }

    internal static string Label(string id, string name) => (id == "red" ? "RED" : "BLUE") + "  " + (name ?? "");

    // "#RRGGBB" from campaign.json; Noesis wants alpha first.
    internal static string Opaque(string colour, string fallback) =>
        colour != null && colour.Length == 7 && colour[0] == '#' && colour.Skip(1).All(Uri.IsHexDigit) ? "#FF" + colour.Substring(1) : fallback;

    private static Brush Ink(string argb) => new SolidColorBrush(Color.FromArgb(
        Convert.ToByte(argb.Substring(1, 2), 16), Convert.ToByte(argb.Substring(3, 2), 16), Convert.ToByte(argb.Substring(5, 2), 16), Convert.ToByte(argb.Substring(7, 2), 16)));

    private static void Pick(object sender, RoutedEventArgs args)
    {
        args.Handled = true;
        string id = (sender as FrameworkElement)?.Tag as string;
        if (stopped || id == null || id == chosen || campaign == null) return;
        try
        {
            chosen = id;
            currentWindow.SetValue(menuInstance.GetValue(null, null), campaignMenu, null);
            show.Invoke(null, new[] { campaign });
            Api.Log("GCO side choice: start page rebuilt for " + id);
        }
        catch (Exception ex) { Stop(ex); }
    }
}
