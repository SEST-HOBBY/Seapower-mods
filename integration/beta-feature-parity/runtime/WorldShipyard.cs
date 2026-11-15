using System;
using System.Reflection;

namespace Sest.RuntimeFixes;

// Presentation only, and only in the World campaign. Dynamic Campaign Mod's
// shipyard (ProcurementViewModel) puts a unit on the Amphibious tab when it
// has ground.lift and nowhere else; its catalogue entry carries no date. Here
// lift ships are also listed under Ships (they stay under Amphibious, and a
// hull bought from either tab is the same entry with the same lift), cards in
// each section put ships in service in 2028 first, then retired ships with
// the most recently retired first, and each card names its service years
// (WorldShipyardYears.cs, generated from the collection's ServiceDate keys).
// Catalogue, unlock ranks, costs, purchases and saves are unchanged.
internal static class WorldShipyard
{
    private const string HarmonyId = "io.github.sest-hobby.world-shipyard";
    private const int Year = 2028;
    private static MethodInfo tabFilter, sortKey, card;
    private static FieldInfo owner, tab, unit, aircraft, ground;
    private static PropertyInfo name;
    private static bool installed, failed;

    // Never throws: a throw here would reach WorldOperations.Poll's catch and
    // stop all of World Operations. On any mismatch DCM's shipyard is kept.
    internal static void Bind(Assembly campaign)
    {
        try
        {
            var view = campaign.GetType("DynamicCampaignMod.UI.Strategy.ProcurementViewModel", true);
            var entry = campaign.GetType("DynamicCampaignMod.Core.Data.CatalogueEntry", true);
            var row = campaign.GetType("DynamicCampaignMod.UI.Strategy.CatalogueRow", true);
            tab = view.GetField("_tab", Api.All);
            if (tab == null || !tab.FieldType.IsEnum || tab.FieldType.DeclaringType != view || view.GetField("_sim", Api.All) == null)
                throw new MissingMemberException("captured ProcurementViewModel._tab/_sim");
            var refresh = view.GetNestedType("<>c__DisplayClass128_0", Api.All) ?? throw new MissingMemberException("captured Refresh closure");
            tabFilter = refresh.GetMethod("<Refresh>b__5", Api.All, null, new[] { entry }, null);
            owner = refresh.GetField("<>4__this", Api.All);
            if (tabFilter == null || tabFilter.IsStatic || tabFilter.ReturnType != typeof(bool) || tabFilter.GetParameters()[0].Name != "e" || owner?.FieldType != view)
                throw new MissingMemberException("captured shipyard tab filter <Refresh>b__5(CatalogueEntry e)");
            var group = view.GetNestedType("<>c__DisplayClass135_0", Api.All) ?? throw new MissingMemberException("captured Group closure");
            sortKey = group.GetMethod("<Group>b__3", Api.All, null, new[] { entry }, null);
            if (sortKey == null || sortKey.IsStatic || sortKey.ReturnType != typeof(int) || sortKey.GetParameters()[0].Name != "e")
                throw new MissingMemberException("captured shipyard card order <Group>b__3(CatalogueEntry e)");
            card = view.GetMethod("Card", Api.All, null, new[] { entry }, null);
            name = row.GetProperty("Name", Api.All);
            if (card == null || card.IsStatic || card.ReturnType != row || card.GetParameters()[0].Name != "entry" ||
                name?.PropertyType != typeof(string) || name.GetSetMethod(true) == null || name.GetGetMethod(true) == null)
                throw new MissingMemberException("captured shipyard Card(CatalogueEntry entry) and CatalogueRow.Name");
            unit = entry.GetField("unit", Api.All);
            aircraft = entry.GetField("aircraft", Api.All);
            ground = entry.GetField("ground", Api.All);
            if (unit?.FieldType != typeof(string) || aircraft?.FieldType != typeof(bool) || ground?.FieldType != typeof(bool))
                throw new MissingMemberException("captured CatalogueEntry unit/aircraft/ground");
        }
        catch (Exception ex)
        {
            tabFilter = sortKey = card = null;
            owner = tab = unit = aircraft = ground = null;
            name = null;
            Api.LogFailure("World shipyard ordering unavailable; Dynamic Campaign Mod's own shipyard retained", ex);
        }
    }

    internal static void Install()
    {
        if (installed || failed || tabFilter == null || sortKey == null || card == null) return;
        installed = true;
        try
        {
            Api.Postfix(tabFilter, typeof(WorldShipyard), nameof(AfterTab), HarmonyId);
            Api.Postfix(sortKey, typeof(WorldShipyard), nameof(AfterSortKey), HarmonyId);
            Api.Postfix(card, typeof(WorldShipyard), nameof(AfterCard), HarmonyId);
            Api.Log("world shipyard installed: lift ships also listed under Ships, in-service ships first, service years on each card; catalogue, costs and saves unchanged");
        }
        catch (Exception ex)
        {
            failed = true;
            Api.LogFailure("World shipyard ordering unavailable; Dynamic Campaign Mod's own shipyard retained", ex);
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

    // Postfix on <Refresh>b__5: a lift ship is shown on Ships (tab 0) too.
    // Its Amphibious listing (tab 2) is left as DCM decides it.
    internal static void AfterTab(object __instance, object __0, ref bool __result)
    {
        if (__result) return;
        try
        {
            if (!Ship(__0, out var id) || !WorldShipyardYears.ShipsTabToo.Contains(id)) return;
            if (Convert.ToInt32(tab.GetValue(owner.GetValue(__instance))) == 0) __result = true;
        }
        catch (Exception ex) { Fail(ex); }
    }

    // Postfix on <Group>b__3 (the card cost DCM orders a section by): ships
    // in service come first by cost, then retired ships, newest-retired first.
    // Ships with no ServiceDate keep their cost order among those in service.
    internal static void AfterSortKey(object __0, ref int __result)
    {
        try
        {
            if (!Ship(__0, out var id) || !WorldShipyardYears.Ships.TryGetValue(id, out var years) || years.Last == 0) return;
            int cost = Math.Min(Math.Max(__result, 0), 999_999);
            __result = (1 << 30) + (2100 - Math.Max(1950, Math.Min(years.Last, 2100))) * 1_000_000 + cost;
        }
        catch (Exception ex) { Fail(ex); }
    }

    // Postfix on Card: the display name gains the service years. Name is
    // only read by the card's XAML binding.
    internal static void AfterCard(object __0, object __result)
    {
        try
        {
            if (__result == null || !Ship(__0, out var id) || !WorldShipyardYears.Ships.TryGetValue(id, out var years)) return;
            string label = Label(years.First, years.Last);
            if (label.Length > 0) name.SetValue(__result, (name.GetValue(__result) as string ?? "") + label);
        }
        catch (Exception ex) { Fail(ex); }
    }

    internal static string Label(int first, int last) =>
        last != 0 ? " \u00b7 last in service " + last :
        first == 0 ? "" :
        first > Year ? " \u00b7 from " + first :
        " \u00b7 in service " + first + "-";
}
