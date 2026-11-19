using System;
using System.Reflection;

namespace Sest.RuntimeFixes;

// Presentation only, and only in the World campaign. Dynamic Campaign Mod's
// shipyard (ProcurementViewModel) puts a unit on the Amphibious tab when it
// has ground.lift and nowhere else; its catalogue entry carries no date. Here
// lift ships are also listed under Ships (they stay under Amphibious, and a
// hull bought from either tab is the same entry with the same lift), and each
// row names the class's service years after its name (WorldShipyardYears.cs,
// generated from the collection's ServiceDate keys).
// Row order is the author's: since 1.0.0 the player sorts the list by column,
// and SEST's former in-service-first order is not applied.
// Catalogue, unlock ranks, costs, class limits, purchases and saves are unchanged.
internal static class WorldShipyard
{
    private const string HarmonyId = "io.github.sest-hobby.world-shipyard";
    private const int Year = 2028;
    private static MethodInfo inTab, fillRow;
    private static FieldInfo rowEntry, unit, aircraft, ground;
    private static PropertyInfo name;
    private static int shipsTab;
    private static bool installed, failed;

    // Never throws: a throw here would reach WorldOperations.Poll's catch and
    // stop all of World Operations. On any mismatch DCM's shipyard is kept.
    internal static void Bind(Assembly campaign)
    {
        try
        {
            var view = campaign.GetType("DynamicCampaignMod.UI.Strategy.ProcurementViewModel", true);
            var entry = campaign.GetType("DynamicCampaignMod.Core.Data.CatalogueEntry", true);
            var row = campaign.GetType("DynamicCampaignMod.UI.Strategy.ShipyardRow", true);
            var tally = campaign.GetType("DynamicCampaignMod.Core.Sim.ClassLimits+Tally", true);
            var tab = view.GetNestedType("Tab", Api.All);
            if (tab == null || !tab.IsEnum || !Enum.IsDefined(tab, "Ships"))
                throw new MissingMemberException("captured ProcurementViewModel.Tab.Ships");
            shipsTab = Convert.ToInt32(Enum.Parse(tab, "Ships"));
            inTab = view.GetMethod("InTab", Api.All, null, new[] { entry, tab }, null);
            if (inTab == null || inTab.IsStatic || inTab.ReturnType != typeof(bool) || inTab.GetParameters()[0].Name != "e" || inTab.GetParameters()[1].Name != "tab")
                throw new MissingMemberException("captured shipyard tab filter InTab(CatalogueEntry e, Tab tab)");
            fillRow = view.GetMethod("FillRow", Api.All, null, new[] { row, tally }, null);
            rowEntry = row.GetField("Entry", Api.All);
            name = row.GetProperty("Name", Api.All);
            if (fillRow == null || fillRow.IsStatic || fillRow.ReturnType != typeof(void) || fillRow.GetParameters()[0].Name != "row" ||
                rowEntry == null || rowEntry.IsStatic || rowEntry.FieldType != entry ||
                name?.PropertyType != typeof(string) || name.GetSetMethod(true) == null || name.GetGetMethod(true) == null)
                throw new MissingMemberException("captured shipyard FillRow(ShipyardRow row, Tally limits), ShipyardRow.Entry and ShipyardRow.Name");
            unit = entry.GetField("unit", Api.All);
            aircraft = entry.GetField("aircraft", Api.All);
            ground = entry.GetField("ground", Api.All);
            if (unit?.FieldType != typeof(string) || aircraft?.FieldType != typeof(bool) || ground?.FieldType != typeof(bool))
                throw new MissingMemberException("captured CatalogueEntry unit/aircraft/ground");
        }
        catch (Exception ex)
        {
            inTab = fillRow = null;
            rowEntry = unit = aircraft = ground = null;
            name = null;
            Api.LogFailure("World shipyard presentation unavailable; Dynamic Campaign Mod's own shipyard retained", ex);
        }
    }

    // Installed from the first Poll after DCM's assembly is found, which is
    // before a campaign is loaded. That matters for the tab filter: DCM
    // builds its per-tab lists once, in ProcurementViewModel's constructor.
    // Patching a method of that class runs its static constructor (three
    // Noesis brushes), as patching Card did on 0.25.0.1.
    internal static void Install()
    {
        if (installed || failed || inTab == null || fillRow == null) return;
        installed = true;
        try
        {
            Api.Postfix(inTab, typeof(WorldShipyard), nameof(AfterTab), HarmonyId);
            Api.Postfix(fillRow, typeof(WorldShipyard), nameof(AfterFillRow), HarmonyId);
            Api.Log("world shipyard installed: lift ships also listed under Ships, service years after each ship's name; row order, catalogue, costs and saves unchanged");
        }
        catch (Exception ex)
        {
            failed = true;
            Api.LogFailure("World shipyard presentation unavailable; Dynamic Campaign Mod's own shipyard retained", ex);
        }
    }

    private static void Fail(Exception ex)
    {
        failed = true;
        Api.LogFailure("World shipyard presentation stopped; Dynamic Campaign Mod's own shipyard retained", ex);
    }

    private static bool Ship(object entry, out string id)
    {
        id = null;
        if (failed || entry == null || unit == null || (bool)aircraft.GetValue(entry) || (bool)ground.GetValue(entry)) return false;
        id = unit.GetValue(entry) as string;
        return id != null && WorldOpeningBriefing.IsWorldCampaign();
    }

    // Postfix on InTab(CatalogueEntry e, Tab tab): a lift ship is listed on
    // Ships too. Its Amphibious listing (Tab.Ground) is left as DCM decides
    // it, and so is the Ground-tab question OrderSelected asks of an entry.
    internal static void AfterTab(object __0, object __1, ref bool __result)
    {
        if (__result) return;
        try
        {
            if (__1 == null || Convert.ToInt32(__1) != shipsTab) return;
            if (Ship(__0, out var id) && WorldShipyardYears.ShipsTabToo.Contains(id)) __result = true;
        }
        catch (Exception ex) { Fail(ex); }
    }

    // Postfix on FillRow(ShipyardRow row, Tally limits): the row's display
    // name gains the service years. FillRow sets Name afresh from
    // Shipyards.NameOf each time it runs, so the years are added once per
    // fill. Name is only read by the row's XAML binding; DCM sorts and
    // groups by the entry, not by this text.
    internal static void AfterFillRow(object __0)
    {
        try
        {
            if (__0 == null || rowEntry == null || !Ship(rowEntry.GetValue(__0), out var id) || !WorldShipyardYears.Ships.TryGetValue(id, out var years)) return;
            string label = Label(years.First, years.Last);
            string shown = name.GetValue(__0, null) as string ?? "";
            if (label.Length > 0 && !shown.EndsWith(label, StringComparison.Ordinal)) name.SetValue(__0, shown + label, null);
        }
        catch (Exception ex) { Fail(ex); }
    }

    // Calendar years only. DCM's own IN SERVICE column on the same row is a
    // count of hulls against the class limit ("2 / 4"), so the words
    // "in service" are not used here.
    internal static string Label(int first, int last) =>
        last != 0 ? (first != 0 && first <= last ? " \u00b7 " + first + "-" + last : " \u00b7 until " + last) :
        first == 0 ? "" :
        first > Year ? " \u00b7 from " + first :
        " \u00b7 since " + first;
}
