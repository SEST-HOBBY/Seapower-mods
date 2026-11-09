using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Security.Cryptography;
using AnchorChain;
using UnityEngine;

namespace Sest.RuntimeFixes;

// Presentation-only enhancement to the author's working strike planner.
// Selection, timing, readiness, salvo commands and launch logic stay authored.
internal static class CoordinatedStrikeRefinements
{
    private const string Hash = "093b8ad6478641948b0eaca720427e5cef3c8b4440142f6c33b16339dc2fc941";
    private sealed class Applied { }
    private sealed class Summary { internal double Next; internal string Text = "", Basis = ""; }
    private static readonly ConditionalWeakTable<object, Applied> themed = new ConditionalWeakTable<object, Applied>();
    private static readonly ConditionalWeakTable<object, Summary> summaries = new ConditionalWeakTable<object, Summary>();
    private static Type styles, panel;
    private static MethodInfo solid;
    private static bool attached, stopped;
    private static double next;
    private static double Now => (double)Stopwatch.GetTimestamp() / Stopwatch.Frequency;
    private static readonly Color Ink = Colour("DCE4EA"), Muted = Colour("9BAEBB"), Background = Colour("151D24"), Row = Colour("1C2730"), Alternate = Colour("24313A"), Accent = Colour("B7DEC5");
    private static Color Colour(string rgb) => new Color(Convert.ToByte(rgb.Substring(0, 2), 16) / 255f, Convert.ToByte(rgb.Substring(2, 2), 16) / 255f, Convert.ToByte(rgb.Substring(4, 2), 16) / 255f, 1f);

    internal static void Poll()
    {
        if (attached || stopped || Now < next) return;
        next = Now + 2;
        var a = AppDomain.CurrentDomain.GetAssemblies().FirstOrDefault(x => x.GetType("CoordinatedStrikeTool.StrikePanel", false) != null);
        if (a == null) return;
        try
        {
            using (var sha = SHA256.Create())
            using (var stream = File.OpenRead(BetaAssemblyPolicy.OriginalLocation(a)))
                if (BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant() != Hash)
                    throw new InvalidOperationException("uninspected Coordinated Strike Tool image");
            Bind(a);
            Api.Postfix(Api.Method(styles, "For", styles, styles, typeof(float)), typeof(CoordinatedStrikeRefinements), "AfterStyles", "io.github.sest-hobby.strike-presentation");
            Api.Postfix(Api.Method(panel, "DrawPlan", typeof(void)), typeof(CoordinatedStrikeRefinements), "AfterPlan", "io.github.sest-hobby.strike-presentation");
            attached = true;
            Api.Log("Coordinated Strike refinements attached: shared SEST colours, readable sections and planned/remaining weapon estimates; author controls retained");
        }
        catch (Exception ex) { stopped = true; Api.LogFailure("strike presentation unavailable; author UI retained", ex); }
    }

    internal static void Bind(Assembly assembly)
    {
        styles = assembly.GetType("CoordinatedStrikeTool.PanelStyles", true);
        panel = assembly.GetType("CoordinatedStrikeTool.StrikePanel", true);
        solid = Api.Method(styles, "Solid", typeof(Texture2D), typeof(Color));
        foreach (var name in new[] { "Window", "Section", "Text", "TextBold", "Muted", "Hint", "Body", "Row", "RowAlt", "Field", "Button", "Primary", "Toggle", "Segment" })
            if (styles.GetField(name, Api.All)?.FieldType != typeof(GUIStyle)) throw new MissingFieldException(styles.FullName, name);
        if (panel.GetField("_plan", Api.All) == null || panel.GetField("_s", Api.All)?.FieldType != styles)
            throw new MissingFieldException("inspected strike panel presentation fields");
        var leg = assembly.GetType("CoordinatedStrikeTool.StrikeLeg", true);
        foreach (var spec in new[] { Tuple.Create("AmmoName", typeof(string)), Tuple.Create("Salvo", typeof(int)), Tuple.Create("Launched", typeof(int)), Tuple.Create("Issue", typeof(string)) })
            if (leg.GetField(spec.Item1, Api.All)?.FieldType != spec.Item2) throw new MissingFieldException(leg.FullName, spec.Item1);
    }

    private static GUIStyle Style(object instance, string name) => (GUIStyle)styles.GetField(name, Api.All).GetValue(instance);
    private static void Paint(object instance, string name, Color text, Color? background = null)
    {
        var s = Style(instance, name);
        foreach (var state in new[] { s.normal, s.focused, s.onNormal, s.onFocused })
        {
            state.textColor = text;
            if (background.HasValue) state.background = (Texture2D)solid.Invoke(instance, new object[] { background.Value });
        }
        s.hover.textColor = text; s.active.textColor = text;
        s.onHover.textColor = text; s.onActive.textColor = text;
    }

    internal static void AfterStyles(object __result)
    {
        if (stopped || __result == null || themed.TryGetValue(__result, out _)) return;
        try
        {
            foreach (string name in new[] { "Text", "TextBold", "Body", "Big", "Status", "StripText", "SlimTextBold", "SlimStatus" }) Paint(__result, name, Ink);
            foreach (string name in new[] { "Muted", "Hint", "SlimMuted" }) Paint(__result, name, Muted);
            foreach (string name in new[] { "Section", "SlimSection", "LinkBold", "SlimLink" }) Paint(__result, name, Accent);
            Paint(__result, "Window", Ink, Background);
            foreach (string name in new[] { "Row", "SlimRow" }) Paint(__result, name, Ink, Row);
            foreach (string name in new[] { "RowAlt", "SlimRowAlt" }) Paint(__result, name, Ink, Alternate);
            Paint(__result, "Field", Ink, Background);
            foreach (string name in new[] { "Button", "Small", "Toggle", "Segment" }) Paint(__result, name, Ink, Alternate);
            Paint(__result, "Primary", Ink, Colour("355C50"));
            themed.Add(__result, new Applied());
        }
        catch (Exception ex) { stopped = true; Api.LogFailure("strike theme stopped; author controls retained", ex); }
    }

    internal static void AfterPlan(object __instance)
    {
        if (stopped) return;
        try
        {
            var summary = summaries.GetValue(__instance, _ => new Summary());
            if (Now >= summary.Next)
            {
                summary.Next = Now + 0.5;
                var plan = panel.GetField("_plan", Api.All).GetValue(__instance);
                var legs = plan?.GetType().GetField("Legs", Api.All)?.GetValue(plan) as IEnumerable;
                var prices = CampaignCosts.Catalogue();
                var planned = new CombatAmount(); var remaining = new CombatAmount();
                int groups = 0, rounds = 0, warnings = 0;
                if (legs != null) foreach (object leg in legs)
                {
                    var t = leg.GetType();
                    string ammo = (string)t.GetField("AmmoName", Api.All).GetValue(leg);
                    int salvo = Math.Max(0, Math.Min(100000, (int)t.GetField("Salvo", Api.All).GetValue(leg)));
                    int launched = Math.Max(0, (int)t.GetField("Launched", Api.All).GetValue(leg));
                    var price = prices?.Read("weapon", ammo, "ammunition") ?? new CombatPrice();
                    planned.Add(price, salvo); remaining.Add(price, Math.Max(0, salvo - launched));
                    groups++; rounds += salvo;
                    if (!string.IsNullOrWhiteSpace((string)t.GetField("Issue", Api.All).GetValue(leg))) warnings++;
                }
                summary.Text = groups + " strike legs | " + rounds + " planned rounds | " + warnings + " legs with notices\nPlanned weapons " + planned.Text + " | Remaining to launch " + remaining.Text;
                summary.Basis = "Estimated USD, " + (prices?.Basis ?? "catalogue unavailable") + " basis. + ? means missing prices. Planning estimate only; F11 records actual expenditure.";
            }
            var s = panel.GetField("_s", Api.All).GetValue(__instance);
            if (s == null) return;
            GUILayout.Space(8);
            GUILayout.Label("SEST STRIKE SUMMARY", Style(s, "Section"));
            GUILayout.Label(summary.Text, Style(s, "Body"));
            GUILayout.Label(summary.Basis, Style(s, "Hint"));
        }
        catch (Exception ex) { stopped = true; Api.LogFailure("strike estimate unavailable; author launch controls retained", ex); }
    }
}
