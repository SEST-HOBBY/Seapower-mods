using System;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

static partial class BetaApiTests
{
    // WorldShipyard.cs binds these members of the inspected Dynamic Campaign
    // Mod 0.25.0.1 shipyard by name. Read from the image with Cecil only: no
    // author code runs. A DCM update that moves them turns the feature off
    // (WorldShipyard.Bind logs and keeps DCM's shipyard); this pins the image.
    static void WorldShipyardPins(ModuleDefinition dcm)
    {
        var view = dcm.GetType("DynamicCampaignMod.UI.Strategy.ProcurementViewModel");
        var entry = dcm.GetType("DynamicCampaignMod.Core.Data.CatalogueEntry");
        var row = dcm.GetType("DynamicCampaignMod.UI.Strategy.CatalogueRow");
        Check(view != null && entry != null && row != null, "World shipyard: ProcurementViewModel, CatalogueEntry and CatalogueRow exist");
        var tab = view.Fields.SingleOrDefault(f => f.Name == "_tab");
        Check(tab != null && tab.FieldType.Resolve()?.IsEnum == true && tab.FieldType.Resolve().DeclaringType == view &&
              view.Fields.Any(f => f.Name == "_sim"), "World shipyard: ProcurementViewModel._tab is its nested Tab enum and _sim exists");
        var tabs = tab.FieldType.Resolve().Fields.Where(f => f.HasConstant).ToDictionary(f => f.Name, f => Convert.ToInt32(f.Constant));
        Check(tabs.Count == 3 && tabs["Ships"] == 0 && tabs["Aircraft"] == 1 && tabs["Ground"] == 2, "World shipyard: Tab is Ships=0, Aircraft=1, Ground=2");
        foreach (var (field, type) in new[] { ("unit", "System.String"), ("aircraft", "System.Boolean"), ("ground", "System.Boolean") })
            Check(entry.Fields.Any(f => f.Name == field && f.FieldType.FullName == type), "World shipyard: CatalogueEntry." + field + " is " + type);

        MethodDefinition Closure(string closure, string method, string returns)
        {
            var type = view.NestedTypes.SingleOrDefault(t => t.Name == closure);
            var m = type?.Methods.SingleOrDefault(x => x.Name == method);
            Check(m != null && !m.IsStatic && m.ReturnType.FullName == returns && m.Parameters.Count == 1 &&
                  m.Parameters[0].Name == "e" && m.Parameters[0].ParameterType.FullName == entry.FullName,
                  "World shipyard: " + closure + "." + method + "(CatalogueEntry e) returns " + returns);
            return m;
        }
        var filter = Closure("<>c__DisplayClass128_0", "<Refresh>b__5", "System.Boolean");
        Check(filter.DeclaringType.Fields.Any(f => f.Name == "<>4__this" && f.FieldType.FullName == view.FullName), "World shipyard: Refresh closure holds <>4__this");
        var calls = filter.Body.Instructions.Where(i => i.Operand is MemberReference).Select(i => ((MemberReference)i.Operand).Name).ToList();
        Check(calls.Count(n => n == "_tab") == 2 && calls.Contains("LiftOf") && calls.Contains("ground") && calls.Contains("aircraft"),
              "World shipyard: the tab filter decides Ships/Amphibious by _tab and Invasions.LiftOf only");
        var key = Closure("<>c__DisplayClass135_0", "<Group>b__3", "System.Int32");
        Check(key.Body.Instructions.Any(i => i.OpCode == OpCodes.Callvirt && i.Operand is MethodReference c && c.Name == "CostOf" && c.DeclaringType.Name == "Shipyards"),
              "World shipyard: <Group>b__3 is the section's cost sort key (Shipyards.CostOf)");
        // Group's per-section closure (<Group>b__2) orders by <Group>b__3, then builds each card with Card.
        var section = key.DeclaringType.Methods.SingleOrDefault(m => m.Name == "<Group>b__2");
        var refs = section?.HasBody == true ? section.Body.Instructions.Where(i => i.Operand is MethodReference).Select(i => ((MethodReference)i.Operand).Name).ToList() : null;
        Check(refs != null && refs.IndexOf("<Group>b__3") >= 0 && refs.IndexOf("OrderBy") > refs.IndexOf("<Group>b__3") &&
              refs.IndexOf("Card") > refs.IndexOf("OrderBy") && refs.IndexOf("Select") > refs.IndexOf("Card"),
              "World shipyard: each section is ordered by <Group>b__3 and its cards built by Card");
        var card = view.Methods.SingleOrDefault(m => m.Name == "Card");
        Check(card != null && !card.IsStatic && card.ReturnType.FullName == row.FullName && card.Parameters.Count == 1 &&
              card.Parameters[0].Name == "entry" && card.Parameters[0].ParameterType.FullName == entry.FullName,
              "World shipyard: ProcurementViewModel.Card(CatalogueEntry entry) returns CatalogueRow");
        var name = row.Properties.SingleOrDefault(p => p.Name == "Name");
        Check(name != null && name.PropertyType.FullName == "System.String" && name.SetMethod != null && name.GetMethod != null,
              "World shipyard: CatalogueRow.Name is a string with a setter");
        // Name is display-only: no DCM code reads it back.
        Check(!Types(dcm.Types).SelectMany(t => t.Methods).Where(m => m.HasBody && m.DeclaringType != row)
                  .SelectMany(m => m.Body.Instructions).Any(i => i.Operand is MethodReference c && c.Name == "get_Name" && c.DeclaringType.FullName == row.FullName),
              "World shipyard: CatalogueRow.Name is only read by the card's XAML binding");
    }
}
