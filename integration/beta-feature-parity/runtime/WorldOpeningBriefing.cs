using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Security;
using System.Text;

namespace Sest.RuntimeFixes;

// Only our world's opening paper. Keep native message history, window layout,
// pause/close/guide commands and every other author's briefing unchanged.
internal static class WorldOpeningBriefing
{
    private const string CampaignId = "sest.world_sandbox_2028.regional";
    private const string Subject = "INITIAL OPERATIONS BRIEF - GLOBAL MARITIME OPERATIONS 2028";
    private static FieldInfo sections, subject, dtg;
    private static MethodInfo add;
    private static MethodInfo[] openings;
    private static MethodInfo render;
    private static bool installed;

    internal static void Bind(Assembly campaign)
    {
        var paper = campaign.GetType("DynamicCampaignMod.Core.Sim.Briefing", true);
        var story = campaign.GetType("DynamicCampaignMod.Core.Sim.Story", true);
        sections = paper.GetField("Sections", Api.All);
        subject = paper.GetField("Subject", Api.All);
        dtg = paper.GetField("DateTimeGroup", Api.All);
        add = paper.GetMethod("Add", Api.All);
        if (sections == null || subject?.FieldType != typeof(string) || dtg?.FieldType != typeof(string) ||
            add == null || add.GetParameters().Length != 2)
            throw new MissingMemberException("captured world-opening briefing structure");
        var methods = new List<MethodInfo>();
        foreach (string name in new[] { "BuildOpening", "OpeningAsTold" })
        {
            var method = story.GetMethod(name, Api.All);
            if (method == null || method.ReturnType != paper || method.GetParameters()[0].ParameterType.FullName != "DynamicCampaignMod.Core.State.CampaignState")
                throw new MissingMemberException("captured opening report: " + name);
            methods.Add(method);
        }
        openings = methods.ToArray();
        render = campaign.GetType("DynamicCampaignMod.Core.Sim.BriefingPaper", true).GetMethod("Paper", Api.All);
        if (render?.ReturnType != typeof(string)) throw new MissingMemberException("captured opening-paper renderer");
    }

    internal static void Install()
    {
        if (installed || openings == null) return;
        foreach (var method in openings)
            Api.Postfix(method, typeof(WorldOpeningBriefing), nameof(AfterOpening), "io.github.sest-hobby.world-opening");
        Api.Postfix(render, typeof(WorldOpeningBriefing), nameof(AfterPaper), "io.github.sest-hobby.world-opening");
        installed = true;
        Api.Log("world opening brief installed: short sections, wrapped paragraphs and native close/guide controls");
    }

    internal static void AfterOpening(object __0, object __result)
    {
        if (__0 == null || __result == null) return;
        var definition = __0.GetType().GetField("Definition", Api.All)?.GetValue(__0);
        if (Convert.ToString(definition?.GetType().GetField("id", Api.All)?.GetValue(definition)) != CampaignId) return;
        ((IList)sections.GetValue(__result)).Clear();
        subject.SetValue(__result, Subject);
        void Section(string title, params string[] paragraphs) => add.Invoke(__result, new object[] { title, paragraphs.ToList() });
        Section("SITUATION", "1 October 2028. Maritime confrontation spans several theatres. Your coalition's dispersed forces have incomplete intelligence and finite stocks.");
        Section("MISSION", "Protect coalition bases and sea communications. Keep supply routes open and prevent forward positions from becoming isolated.");
        Section("THREAT", "Expect surface groups, submarines and land-based aviation. Reports are estimates; identify contacts before committing weapons. Civil traffic remains present.");
        Section("EXECUTION", "Concentrate locally, maintain air cover and retain a reserve. Accept Admiralty assignments whose conditions and deadlines your force can meet.");
        Section("SUSTAINMENT", "Check fuel, magazines and base stocks before sailing. Set supply priorities, escort exposed convoys and use airlift for urgent ammunition. Load replenishment ships from friendly port stocks.");
        Section("COMMAND", "Renown opens eight command stages. Escort, surveillance and area-control assignments can earn renown and credits when offered and completed. F11 or Combat Costs beside Economy opens cumulative combat costs; Overview shows command progress.");
        Section("BATTLE HANDOVER", "Begin engagements paused, prepare aircraft and issue orders, then unpause. Esc > End battle... returns through the debrief without requiring victory. The campaign assesses losses, expenditure and unresolved fighting.");
        Section("SCENARIO", "Hypothetical 2028 coalition access, deployments and stocks. Real facility locations do not establish current national policy or readiness.");
    }

    internal static void AfterPaper(object __0, ref string __result)
    {
        if (__0 == null || subject == null || Convert.ToString(subject.GetValue(__0)) != Subject) return;
        __result = Format(Convert.ToString(dtg.GetValue(__0)), ((IEnumerable)sections.GetValue(__0)).Cast<object>().Select(row => {
            var t = row.GetType();
            return Tuple.Create(Convert.ToString(t.GetField("Item1").GetValue(row)),
                ((IEnumerable)t.GetField("Item2").GetValue(row)).Cast<object>().Select(Convert.ToString).ToArray());
        }));
    }

    internal static string Format(string time, IEnumerable<Tuple<string, string[]>> rows)
    {
        string E(string value) => SecurityElement.Escape(value ?? "") ?? "";
        var x = new StringBuilder("<Border xmlns='http://schemas.microsoft.com/winfx/2006/xaml/presentation' Background='#FF17212B' Padding='18'><StackPanel>");
        x.Append("<TextBlock Text='INITIAL OPERATIONS BRIEF' FontSize='18' FontWeight='DemiBold' Foreground='#FFF0F3F5' TextWrapping='Wrap' Margin='0,0,0,4'/>");
        x.Append("<TextBlock Text='Global Maritime Operations 2028' FontSize='13' Foreground='#FFB6C8D4' TextWrapping='Wrap' Margin='0,0,0,4'/>");
        x.Append("<TextBlock Text='").Append(E(time)).Append("' FontSize='11' Foreground='#FF9BAEBB' TextWrapping='Wrap' Margin='0,0,0,8'/>");
        foreach (var row in rows)
        {
            x.Append("<TextBlock Text='").Append(E(row.Item1)).Append("' FontSize='12' FontWeight='DemiBold' Foreground='#FFB6C8D4' TextWrapping='Wrap' Margin='0,12,0,5'/>");
            foreach (var paragraph in row.Item2)
                x.Append("<TextBlock Text='").Append(E(paragraph)).Append("' FontSize='14' FontWeight='Normal' Foreground='#FFDCE4EA' TextWrapping='Wrap' Margin='0,0,0,5'/>");
        }
        return x.Append("</StackPanel></Border>").ToString();
    }
}
