using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Security;
using System.Text;

namespace Sest.RuntimeFixes;

// Presentation only. DCM builds, tells and saves its own SITREP 001 unchanged
// (Story.TellOpening persists Briefing.Text() into CampaignState.Feed). When
// that paper is rendered for this world, SEST's concise brief is shown first
// and every DCM section follows in full, reflowed; nothing is written back.
internal static class WorldOpeningBriefing
{
    private const string CampaignId = "sest.world_sandbox_2028.regional";
    // Story.BuildOpening's subject; ReadSitrep appends " (RE-ISSUED)".
    internal const string OpeningSubject = "SITREP 001 - GENERAL SITUATION";
    internal static readonly string[][] Brief = {
        new[] { "SITUATION", "1 October 2028. Maritime confrontation spans several theatres. Your coalition's dispersed forces have incomplete intelligence and finite stocks." },
        new[] { "MISSION", "Protect coalition bases and sea communications. Keep supply routes open and prevent forward positions from becoming isolated." },
        new[] { "THREAT", "Expect surface groups, submarines and land-based aviation. Reports are estimates; identify contacts before committing weapons. Civil traffic remains present." },
        new[] { "EXECUTION", "Concentrate locally, maintain air cover and retain a reserve. Accept Admiralty assignments whose conditions and deadlines your force can meet." },
        new[] { "SUSTAINMENT", "Check fuel, magazines and base stocks before sailing. Set supply priorities, escort exposed convoys and use airlift for urgent ammunition. Load replenishment ships from friendly port stocks." },
        new[] { "COMMAND", "Renown opens eight command stages. Escort, surveillance and area-control assignments can earn renown and credits when offered and completed. F11 or Combat Costs beside Economy opens cumulative combat costs; Overview shows command progress." },
        new[] { "BATTLE HANDOVER", "Begin engagements paused, prepare aircraft and issue orders, then unpause. Esc > End battle... returns through the debrief without requiring victory. The campaign assesses losses, expenditure and unresolved fighting." },
        new[] { "SCENARIO", "Hypothetical 2028 coalition access, deployments and stocks. Real facility locations do not establish current national policy or readiness." }
    };
    private static FieldInfo sections, subject, dtg, from, closing, definitionId, item1, item2;
    private static PropertyInfo definition;
    private static MethodInfo render;
    private static bool installed, failed;

    internal static void Bind(Assembly campaign)
    {
        var paper = campaign.GetType("DynamicCampaignMod.Core.Sim.Briefing", true);
        sections = paper.GetField("Sections", Api.All);
        subject = paper.GetField("Subject", Api.All);
        dtg = paper.GetField("DateTimeGroup", Api.All);
        from = paper.GetField("From", Api.All);
        closing = paper.GetField("Closing", Api.All);
        var row = sections?.FieldType.IsGenericType == true && sections.FieldType.GetGenericTypeDefinition() == typeof(List<>) ? sections.FieldType.GetGenericArguments()[0] : null;
        item1 = row?.GetField("Item1");
        item2 = row?.GetField("Item2");
        if (subject?.FieldType != typeof(string) || dtg?.FieldType != typeof(string) || from?.FieldType != typeof(string) ||
            closing?.FieldType != typeof(string) || item1?.FieldType != typeof(string) || item2?.FieldType != typeof(List<string>))
            throw new MissingMemberException("captured world-opening briefing structure");
        render = campaign.GetType("DynamicCampaignMod.Core.Sim.BriefingPaper", true).GetMethod("Paper", Api.All, null, new[] { paper }, null);
        if (render?.ReturnType != typeof(string) || !render.IsStatic) throw new MissingMemberException("captured opening-paper renderer");
        definition = campaign.GetType("DynamicCampaignMod.Game.Session.CampaignSession", true).GetProperty("Definition", Api.All);
        definitionId = definition?.PropertyType.GetField("id", Api.All);
        if (definition?.GetGetMethod(true)?.IsStatic != true || definitionId?.FieldType != typeof(string))
            throw new MissingMemberException("captured campaign definition identity");
    }

    internal static void Install()
    {
        if (installed || render == null) return;
        Api.Postfix(render, typeof(WorldOpeningBriefing), nameof(AfterPaper), "io.github.sest-hobby.world-opening");
        installed = true;
        Api.Log("world opening brief installed: concise SEST brief above Dynamic Campaign Mod's full SITREP 001 when displayed; the sent and saved report is unchanged");
    }

    internal static bool IsWorldOpening(object paper)
    {
        if (paper == null || !(subject.GetValue(paper) is string title) || !title.StartsWith(OpeningSubject, StringComparison.Ordinal)) return false;
        var current = definition.GetValue(null, null);
        return current != null && definitionId.GetValue(current) as string == CampaignId;
    }

    // Postfix on BriefingPaper.Paper: only the returned markup changes. The
    // Briefing object, the message feed and the save are never modified.
    internal static void AfterPaper(object __0, ref string __result)
    {
        if (failed || __0 == null || sections == null) return;
        try
        {
            if (!IsWorldOpening(__0)) return;
            var rows = ((IEnumerable)sections.GetValue(__0) ?? new object[0]).Cast<object>().Where(r => r != null)
                .Select(r => Tuple.Create(item1.GetValue(r) as string ?? "", ((IEnumerable<string>)item2.GetValue(r) ?? new string[0]).ToArray())).ToList();
            __result = Format(dtg.GetValue(__0) as string, subject.GetValue(__0) as string, from.GetValue(__0) as string, rows, closing.GetValue(__0) as string);
        }
        catch (Exception ex)
        {
            failed = true;
            Api.LogFailure("world opening presentation unavailable; Dynamic Campaign Mod's own paper retained", ex);
        }
    }

    internal static string Format(string time, string title, string sender, IEnumerable<Tuple<string, string[]>> report, string signature)
    {
        string E(string value) => SecurityElement.Escape(value ?? "") ?? "";
        var x = new StringBuilder("<Border xmlns='http://schemas.microsoft.com/winfx/2006/xaml/presentation' Background='#FF17212B' Padding='18'><StackPanel>");
        void Line(string text, int size, string weight, string colour, string margin) =>
            x.Append("<TextBlock Text='").Append(E(text)).Append("' FontSize='").Append(size).Append("' FontWeight='").Append(weight)
             .Append("' Foreground='").Append(colour).Append("' TextWrapping='Wrap' Margin='").Append(margin).Append("'/>");
        Line("INITIAL OPERATIONS BRIEF", 18, "DemiBold", "#FFF0F3F5", "0,0,0,4");
        Line("Global Maritime Operations 2028", 13, "Normal", "#FFB6C8D4", "0,0,0,4");
        Line(time, 11, "Normal", "#FF9BAEBB", "0,0,0,8");
        foreach (var section in Brief)
        {
            Line(section[0], 12, "DemiBold", "#FFB6C8D4", "0,12,0,5");
            Line(section[1], 14, "Normal", "#FFDCE4EA", "0,0,0,5");
        }
        // DCM's live situation, in its own order and words.
        x.Append("<Border BorderBrush='#FF34434D' BorderThickness='0,1,0,0' Margin='0,16,0,0' Padding='0,12,0,0'><StackPanel>");
        Line(title, 14, "DemiBold", "#FFF0F3F5", "0,0,0,4");
        if (!string.IsNullOrWhiteSpace(sender)) Line("From: " + sender, 11, "Normal", "#FF9BAEBB", "0,0,0,4");
        Line("Dynamic Campaign Mod's situation report follows in full.", 11, "Normal", "#FF9BAEBB", "0,0,0,4");
        foreach (var row in report)
        {
            Line(row.Item1, 12, "DemiBold", "#FFB6C8D4", "0,12,0,5");
            foreach (var paragraph in row.Item2) Line(paragraph, 13, "Normal", "#FFDCE4EA", "0,0,0,5");
        }
        if (!string.IsNullOrWhiteSpace(signature)) Line(signature, 11, "Normal", "#FF9BAEBB", "0,10,0,0");
        return x.Append("</StackPanel></Border></StackPanel></Border>").ToString();
    }
}
