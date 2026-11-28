using System;
using System.IO;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;

static partial class BetaApiTests
{
    // WorldSideChoice.cs binds these members of the inspected Dynamic Campaign
    // Mod 1.0.4 start page by name. Read from the image with Cecil only.
    static void WorldSideChoicePins(ModuleDefinition dcm)
    {
        const string Definition = "DynamicCampaignMod.Core.Data.CampaignDefinition", Side = "DynamicCampaignMod.Core.Data.SideDefinition";
        const string Menu = "SeapowerUI.ViewModels.MenuSystemViewModel";
        var definition = dcm.GetType(Definition);
        var side = dcm.GetType(Side);
        var screen = dcm.GetType("DynamicCampaignMod.UI.Start.StartScreen");
        var model = dcm.GetType("DynamicCampaignMod.UI.Start.StartScreenViewModel");
        Check(definition != null && side != null && screen != null && model != null, "GCO side choice: CampaignDefinition, SideDefinition, StartScreen and StartScreenViewModel exist");
        foreach (var (type, field) in new[] { (definition, "id"), (side, "id"), (side, "name"), (side, "color") })
            Check(type.Fields.Any(f => f.Name == field && !f.IsStatic && f.FieldType.FullName == "System.String"), "GCO side choice: " + type.Name + "." + field + " is a string");
        Check(definition.Fields.Any(f => f.Name == "sides" && f.FieldType.FullName == "System.Collections.Generic.List`1<" + Side + ">"),
              "GCO side choice: CampaignDefinition.sides is a List<SideDefinition>");

        // The one choice DCM makes: PlayerSide's requested id, else the first playable side.
        var pick = definition.Methods.SingleOrDefault(m => m.Name == "PlayerSide");
        Check(pick != null && !pick.IsStatic && pick.ReturnType.FullName == Side && pick.Parameters.Count == 1 &&
              pick.Parameters[0].Name == "requestedId" && pick.Parameters[0].ParameterType.FullName == "System.String",
              "GCO side choice: CampaignDefinition.PlayerSide(string requestedId) returns a SideDefinition");
        var looked = pick.Body.Instructions.Where(i => i.Operand is MethodReference c).Select(i => ((MethodReference)i.Operand).Name).ToList();
        Check(pick.Body.Instructions[0].OpCode == OpCodes.Ldarg_0 && pick.Body.Instructions[1].OpCode == OpCodes.Ldarg_1 &&
              looked.Take(2).SequenceEqual(new[] { "Side", "get_Playable" }),
              "GCO side choice: PlayerSide looks the requested id up with Side(id) and keeps it only when the side is playable");

        // The start page: the constructor asks PlayerSide(null) once and keeps
        // that side's id as StartOptions.PlayerSideId.
        var ctor = model.Methods.Single(m => m.IsConstructor && !m.IsStatic);
        var asks = ctor.Body.Instructions.Where(i => i.Operand is MethodReference c && c.Resolve() == pick).ToList();
        Check(asks.Count == 1 && asks[0].Previous.OpCode == OpCodes.Ldnull, "GCO side choice: StartScreenViewModel's constructor calls PlayerSide(null) once");
        Check(ctor.Body.Instructions.SkipWhile(i => i != asks[0]).Take(8).Any(i => i.OpCode == OpCodes.Stfld && i.Operand is FieldReference f &&
              f.Name == "PlayerSideId" && f.DeclaringType.Name == "StartOptions"),
              "GCO side choice: the constructor writes that side's id to StartOptions.PlayerSideId");

        // StartScreen.Show(campaign): keeps the current window for Back, builds
        // the view model, loads StartScreen.xaml and makes the page current.
        var show = screen.Methods.SingleOrDefault(m => m.Name == "Show");
        Check(show != null && show.IsStatic && show.ReturnType.FullName == "System.Void" && show.Parameters.Count == 1 &&
              show.Parameters[0].ParameterType.FullName == Definition, "GCO side choice: StartScreen.Show(CampaignDefinition) is static void");
        var steps = show.Body.Instructions.Where(i => i.Operand is MethodReference).Select(i => (MethodReference)i.Operand).ToList();
        int get = steps.FindIndex(c => c.Name == "get_CurrentWindow" && c.DeclaringType.FullName == Menu);
        int build = steps.FindIndex(c => c.Name == ".ctor" && c.DeclaringType.FullName == model.FullName);
        int set = steps.FindIndex(c => c.Name == "set_CurrentWindow" && c.DeclaringType.FullName == Menu);
        Check(get >= 0 && build > get && set > build && steps.Count(c => c.Name == "set_CurrentWindow") == 1 &&
              steps.Count(c => c.Name == "get_CurrentWindow") == 1 && steps.Count(c => c.Name == ".ctor" && c.DeclaringType.FullName == model.FullName) == 1,
              "GCO side choice: Show reads CurrentWindow once, then builds one StartScreenViewModel, then sets CurrentWindow once");
        Check(show.Body.Instructions.Any(i => i.OpCode == OpCodes.Ldstr && (string)i.Operand == "StartScreen.xaml") &&
              steps.Any(c => c.Name == "set_Content") && steps.Any(c => c.Name == "set_DataContext"),
              "GCO side choice: Show loads StartScreen.xaml as the page's content");
        var xaml = dcm.Resources.OfType<EmbeddedResource>().SingleOrDefault(r => r.Name == "StartScreen.xaml");
        string text = xaml == null ? "" : new StreamReader(xaml.GetResourceStream()).ReadToEnd();
        int scroll = text.IndexOf("x:Name=\"CampaignScroll\"", StringComparison.Ordinal);
        Check(scroll > 0 && text.IndexOf("<StackPanel>", scroll, StringComparison.Ordinal) > scroll &&
              text.IndexOf("<StackPanel>", scroll, StringComparison.Ordinal) < text.IndexOf("{Binding OurFlags}", scroll, StringComparison.Ordinal) &&
              text.IndexOf("{Binding OurFlags}", scroll, StringComparison.Ordinal) < text.IndexOf("{Binding SideLine}", scroll, StringComparison.Ordinal),
              "GCO side choice: StartScreen.xaml's CampaignScroll holds a StackPanel with the flags, then the side line");
    }
}
