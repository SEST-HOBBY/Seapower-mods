using System;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

static partial class BetaApiTests
{
    // WorldShipyard.cs binds these members of the inspected Dynamic Campaign
    // Mod 1.0.1 shipyard (as 1.0.0) by name. Read from the image with Cecil only: no
    // author code runs. A DCM update that moves them turns the feature off
    // (WorldShipyard.Bind logs and keeps DCM's shipyard); this pins the image.
    // The 0.25.0.1 members the feature used to bind must be gone, so that a
    // capture of the older mod cannot pass as this one.
    static void WorldShipyardPins(ModuleDefinition dcm)
    {
        const string Entry = "DynamicCampaignMod.Core.Data.CatalogueEntry", Row = "DynamicCampaignMod.UI.Strategy.ShipyardRow";
        var view = dcm.GetType("DynamicCampaignMod.UI.Strategy.ProcurementViewModel");
        var entry = dcm.GetType(Entry);
        var row = dcm.GetType(Row);
        var tally = dcm.GetType("DynamicCampaignMod.Core.Sim.ClassLimits")?.NestedTypes.SingleOrDefault(t => t.Name == "Tally");
        Check(view != null && entry != null && row != null && tally != null, "World shipyard: ProcurementViewModel, CatalogueEntry, ShipyardRow and ClassLimits.Tally exist");

        Check(dcm.GetType("DynamicCampaignMod.UI.Strategy.CatalogueRow") == null, "World shipyard: 0.25.0.1's CatalogueRow is gone");
        Check(!view.Methods.Any(m => m.Name == "Card" || m.Name == "Group"), "World shipyard: 0.25.0.1's Card and Group are gone");
        Check(!Types(view.NestedTypes).SelectMany(t => t.Methods).Any(m => m.Name == "<Refresh>b__5" || m.Name == "<Group>b__3"),
              "World shipyard: 0.25.0.1's <Refresh>b__5 tab filter and <Group>b__3 sort key are gone");

        var tab = view.NestedTypes.SingleOrDefault(t => t.Name == "Tab");
        Check(tab != null && tab.IsEnum && view.Fields.Any(f => f.Name == "_tab" && f.FieldType.FullName == tab.FullName) &&
              view.Fields.Any(f => f.Name == "_sim"), "World shipyard: ProcurementViewModel._tab is its nested Tab enum and _sim exists");
        var tabs = tab.Fields.Where(f => f.HasConstant).ToDictionary(f => f.Name, f => Convert.ToInt32(f.Constant));
        Check(tabs.Count == 3 && tabs["Ships"] == 0 && tabs["Aircraft"] == 1 && tabs["Ground"] == 2, "World shipyard: Tab is Ships=0, Aircraft=1, Ground=2");
        foreach (var (field, type) in new[] { ("unit", "System.String"), ("aircraft", "System.Boolean"), ("ground", "System.Boolean") })
            Check(entry.Fields.Any(f => f.Name == field && !f.IsStatic && f.FieldType.FullName == type), "World shipyard: CatalogueEntry." + field + " is " + type);

        // Tab filter.
        var filter = view.Methods.SingleOrDefault(m => m.Name == "InTab");
        Check(filter != null && !filter.IsStatic && filter.ReturnType.FullName == "System.Boolean" && filter.Parameters.Count == 2 &&
              filter.Parameters[0].Name == "e" && filter.Parameters[0].ParameterType.FullName == Entry &&
              filter.Parameters[1].Name == "tab" && filter.Parameters[1].ParameterType.FullName == tab.FullName,
              "World shipyard: ProcurementViewModel.InTab(CatalogueEntry e, Tab tab) is an instance method returning bool");
        var used = filter.Body.Instructions.Where(i => i.Operand is MemberReference).Select(i => ((MemberReference)i.Operand).Name).ToList();
        Check(used.Contains("LiftOf") && used.Contains("ground") && used.Contains("aircraft") && used.Contains("unit") && !used.Contains("_tab") &&
              used.All(n => n == "LiftOf" || n == "ground" || n == "aircraft" || n == "unit" || n == "_sim" || n == "Invasions" || n == "UnitIni" || n == ".ctor"),
              "World shipyard: InTab decides Ships/Amphibious from its tab argument and Invasions.LiftOf only");
        // Who asks: the constructor, once per tab, to build the lists the
        // shipyard shows (so the postfix must be in place before a campaign
        // loads), and OrderSelected, which asks about Tab.Ground only.
        bool Calls(MethodDefinition m, MethodDefinition target) =>
            m.HasBody && m.Body.Instructions.Any(i => i.Operand is MethodReference c && c.Resolve() == target);
        var askers = Types(dcm.Types).SelectMany(t => t.Methods).Where(m => Calls(m, filter)).ToList();
        var listed = askers.SingleOrDefault(m => m.Name.StartsWith("<.ctor>"));
        var order = askers.SingleOrDefault(m => m.Name == "OrderSelected");
        Check(askers.Count == 2 && listed != null && listed.DeclaringType.DeclaringType == view && order != null && order.DeclaringType == view,
              "World shipyard: InTab is called from a constructor lambda and from OrderSelected only");
        var ctor = view.Methods.Single(m => m.IsConstructor && !m.IsStatic);
        Check(ctor.Body.Instructions.Any(i => i.OpCode == OpCodes.Ldftn && i.Operand == listed) &&
              Types(dcm.Types).SelectMany(t => t.Methods).Where(m => m.HasBody && m.Body.Instructions.Any(i => i.OpCode == OpCodes.Stfld &&
                  i.Operand is FieldReference f && f.Name == "_tabs" && f.DeclaringType.FullName == view.FullName)).SequenceEqual(new[] { ctor }),
              "World shipyard: the per-tab lists (_tabs) are built with InTab in the constructor and nowhere else");
        var asked = order.Body.Instructions.Single(i => i.Operand is MethodReference c && c.Resolve() == filter);
        Check(asked.Previous.OpCode == OpCodes.Ldc_I4_2, "World shipyard: OrderSelected asks InTab about Tab.Ground only");

        // Row name.
        var fill = view.Methods.SingleOrDefault(m => m.Name == "FillRow");
        Check(fill != null && !fill.IsStatic && fill.ReturnType.FullName == "System.Void" && fill.Parameters.Count == 2 &&
              fill.Parameters[0].Name == "row" && fill.Parameters[0].ParameterType.FullName == Row &&
              fill.Parameters[1].Name == "limits" && fill.Parameters[1].ParameterType.FullName == tally.FullName,
              "World shipyard: ProcurementViewModel.FillRow(ShipyardRow row, ClassLimits.Tally limits) is an instance method returning void");
        Check(row.Fields.Any(f => f.Name == "Entry" && !f.IsStatic && f.FieldType.FullName == Entry), "World shipyard: ShipyardRow.Entry is a CatalogueEntry field");
        var name = row.Properties.SingleOrDefault(p => p.Name == "Name");
        Check(name != null && name.PropertyType.FullName == "System.String" && name.SetMethod != null && !name.SetMethod.IsStatic && name.GetMethod != null,
              "World shipyard: ShipyardRow.Name is a string with a setter");
        var sets = fill.Body.Instructions.Where(i => i.Operand is MethodReference c && c.Resolve() == name.SetMethod).ToList();
        Check(sets.Count == 1 && sets[0].Previous.Operand is MethodReference named && named.Name == "NameOf" && named.DeclaringType.Name == "Shipyards" &&
              fill.Body.Instructions[0].OpCode == OpCodes.Ldarg_1 && fill.Body.Instructions[1].Operand is FieldReference read && read.Name == "Entry",
              "World shipyard: FillRow reads row.Entry and sets row.Name once, from Shipyards.NameOf");
        var build = view.Methods.SingleOrDefault(m => m.Name == "Row");
        Check(build != null && build.ReturnType.FullName == Row && Calls(build, fill) &&
              build.Body.Instructions.Any(i => i.OpCode == OpCodes.Stfld && i.Operand is FieldReference f && f.Name == "Entry" && f.DeclaringType.FullName == Row),
              "World shipyard: Row(CatalogueEntry, Tally) makes a ShipyardRow, sets its Entry and fills it with FillRow");
        // Name is display-only: no DCM code reads it back, so the service
        // years cannot reach the author's sorting, grouping or orders.
        Check(!Types(dcm.Types).SelectMany(t => t.Methods).Where(m => m.HasBody && m.DeclaringType != row)
                  .SelectMany(m => m.Body.Instructions).Any(i => i.Operand is MethodReference c && c.Name == "get_Name" && c.DeclaringType.FullName == Row),
              "World shipyard: ShipyardRow.Name is only read by the row's XAML binding");
    }
}
