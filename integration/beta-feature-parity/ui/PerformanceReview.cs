using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using System.Runtime.CompilerServices;
using HarmonyLib;
using UnityEngine;

namespace Sest.UiFixes
{
    internal static class PerformanceReview
    {
        const BindingFlags All = ContactsFix.All;
        const string MenuHash = "9dfd561db256aaa2455ff0039783b46cfbaf113b641c97f0815121d3a4502515";
        const string Cv16Hash = "c592e4c118643e04a2a62314066dacfd1662fbd4ba8a64dfdcd4583082cd2940";
        static FieldInfo initialized, closing, helicopterFlight, contactWindow;
        static ConditionalWeakTable<object, UiRefreshGate> contactRefresh = new ConditionalWeakTable<object, UiRefreshGate>();
        static object game;
        static float nextReport;
        static readonly Dictionary<MethodBase, int> slots = new Dictionary<MethodBase, int>();
        static readonly Sample[] samples = { new Sample("simulation"), new Sample("contact begin"),
            new Sample("contact step"), new Sample("cost capture"), new Sample("formation tick"),
            new Sample("formation layout"), new Sample("formation fit"), new Sample("formation discovery"),
            new Sample("formation chrome"), new Sample("SEST formation controls"), new Sample("Noesis update") };

        sealed class Sample
        {
            internal readonly string Name;
            internal long Count, Total, Max, Slow;
            internal Sample(string name) { Name = name; }
            internal void Add(long ticks)
            {
                Count++; Total += ticks; Max = Math.Max(Max, ticks);
                if (ticks * 1000.0 / Stopwatch.Frequency >= 16.7) Slow++;
            }
            internal void Clear() { Count = Total = Max = Slow = 0; }
            internal string Describe()
            {
                double k = 1000.0 / Stopwatch.Frequency;
                return Name + " " + Count + "x avg " + (Count == 0 ? 0 : Total * k / Count).ToString("F2") +
                    " max " + (Max * k).ToString("F2") + " ms, >=16.7ms " + Slow;
            }
        }

        internal static bool Live
        {
            get { return game != null && (bool)initialized.GetValue(game) && !(bool)closing.GetValue(game); }
        }

        internal static object MissionContext => Live ? game : null;

        internal static void Install()
        {
            var life = new Harmony("io.github.sest-hobby.performance-lifecycle");
            try
            {
                var main = typeof(SeaPower.GameMain);
                initialized = main.GetField("_initialized", All);
                closing = main.GetField("_closing", All);
                if (initialized == null || closing == null || initialized.FieldType != typeof(bool) || closing.FieldType != typeof(bool))
                    throw new MissingFieldException("Inspected GameMain lifecycle");
                life.Patch(main.GetMethod("Update", All), prefix: Hook(nameof(BeforeGame)), postfix: Hook(nameof(Report)));
                life.Patch(main.GetMethod("OnDestroy", All), prefix: Hook(nameof(EndGame)));
            }
            catch (Exception e) { life.UnpatchSelf(); ContactsFix.Log("Performance lifecycle inactive: " + e.Message); return; }

            var pictures = new Harmony("io.github.sest-hobby.performance-pictures");
            try
            {
                var film = ContactsFix.Find("Sest.MenuBackground.MenuFilmSwapper");
                ContactsFix.Require(film.Assembly, MenuHash);
                var log = ContactsFix.Find("Sest.MenuBackground.PictureLog");
                pictures.Patch(log.GetMethod("Tick", All), prefix: Hook(nameof(SkipDiagnostics)));
                pictures.Patch(log.GetMethod("Schedule", All), prefix: Hook(nameof(SkipDiagnostics)));
                pictures.Patch(film.GetMethod("Scan", All), prefix: Hook(nameof(OutsideMission)));
                var swap = ContactsFix.Find("Sest.MenuBackground.PictureSwap");
                pictures.Patch(swap.GetMethod("Tick", All), prefix: Hook(nameof(OutsideMission)));
                pictures.Patch(swap.GetMethod("Watch", All), prefix: Hook(nameof(OutsideMission)));
                ContactsFix.Log("Performance: picture diagnostics disabled; background texture/video discovery suspended during initialized missions and resumed for loading/menus.");
            }
            catch (Exception e) { pictures.UnpatchSelf(); ContactsFix.Log("Picture performance patch inactive: " + e.Message); }

            var contacts = new Harmony("io.github.sest-hobby.performance-contact-controls");
            try
            {
                contactWindow = ContactsFix.Find("ContactLog.NativeWindow").GetField("_window", All);
                if (contactWindow == null || contactWindow.FieldType != typeof(object))
                    throw new MissingFieldException("Inspected Contacts window reference");
                contacts.Patch(ContactsFix.Find("Sest.RuntimeFixes.ContactWindowBridge").GetMethod("AfterTick", All),
                    prefix: Hook(nameof(BeforeContactControls)));
                ContactsFix.Log("Performance: Contacts screen-button refresh capped at 5 Hz; window/open transitions refresh immediately, original contact polling retained.");
            }
            catch (Exception e) { contacts.UnpatchSelf(); ContactsFix.Log("Contacts control cadence patch inactive: " + e.Message); }

            var cv = new Harmony("io.github.sest-hobby.cv16-helicopter-flight-flag");
            try
            {
                var clearance = ContactsFix.Find("meltemi.CV16.plugin.ForwardRunwayClearancePatch");
                ContactsFix.Require(clearance.Assembly, Cv16Hash);
                helicopterFlight = typeof(SeaPower.Helicopter).GetField("_isInFlight", All);
                if (helicopterFlight == null || helicopterFlight.FieldType != typeof(bool))
                    throw new MissingFieldException("Inspected Helicopter._isInFlight");
                cv.Patch(clearance.GetMethod("IsClear", All), transpiler: Hook(nameof(ClearanceFlag)));
                ContactsFix.Log("CV16: clearance reads the helicopter's own flight flag; fixed-wing behavior and 30-second timeout retained.");
            }
            catch (Exception e) { cv.UnpatchSelf(); ContactsFix.Log("CV16 type correction inactive: " + e.Message); }

            var metrics = new Harmony("io.github.sest-hobby.performance-samples");
            try
            {
                MethodInfo[] methods = { typeof(SeaPower.GameMain).GetMethod("PerformFixedUpdate", All),
                    ContactsFix.Find("ContactLog.GameBridge").GetMethod("Begin", All),
                    ContactsFix.Find("ContactLog.GameBridge").GetMethod("Step", All),
                    ContactsFix.Find("Sest.RuntimeFixes.CampaignCosts").GetMethod("CaptureLive", All),
                    ContactsFix.Find("SeaPowerSquadPanel.SquadManagerController").GetMethod("Tick", All),
                    ContactsFix.Find("SeaPowerSquadPanel.SquadRowLayout").GetMethod("Apply", All),
                    ContactsFix.Find("SeaPowerSquadPanel.SquadRowLayout").GetMethod("FullScale", All),
                    ContactsFix.Find("SeaPowerSquadPanel.SquadBarController").GetMethod("DiscoverTrees", All),
                    ContactsFix.Find("Sest.RuntimeFixes.PopOutBridge").GetMethod("AfterFormation", All),
                    typeof(FormationUiMode).GetMethod("AfterPluginTick", All),
                    typeof(NoesisView).GetMethod("LateUpdate", All) };
                for (int i = 0; i < methods.Length; i++)
                {
                    if (methods[i] == null) throw new MissingMethodException(samples[i].Name);
                    slots.Add(methods[i], i);
                    metrics.Patch(methods[i], prefix: Hook(nameof(BeginSample)), finalizer: Hook(nameof(EndSample)));
                }
                ContactsFix.Log("Performance samples enabled: one aggregate line every 30 seconds; original simulation and contact polling cadence retained.");
            }
            catch (Exception e) { metrics.UnpatchSelf(); slots.Clear(); ContactsFix.Log("Performance samples inactive: " + e.Message); }
        }

        static HarmonyMethod Hook(string name) { return new HarmonyMethod(typeof(PerformanceReview), name); }
        public static bool SkipDiagnostics() { return false; }
        public static bool OutsideMission() { return !Live; }
        public static void BeforeGame(object __instance)
        {
            if (ReferenceEquals(game, __instance)) return;
            game = __instance; CostCatalogueCache.Clear(); nextReport = Time.unscaledTime + 30;
            FramePacing.Clear();
            foreach (var s in samples) s.Clear();
            contactRefresh = new ConditionalWeakTable<object, UiRefreshGate>();
            FormationUiMode.ClearCaches();
        }
        public static void EndGame()
        {
            game = null; CostCatalogueCache.Clear();
            FramePacing.Clear(); StutterDiagnostics.End(); TerrainCleanup.End();
            UiRefinements.End();
            contactRefresh = new ConditionalWeakTable<object, UiRefreshGate>();
            FormationUiMode.ClearCaches();
        }
        public static void Report()
        {
            UiRefinements.Tick();
            FramePacing.Tick();
            if (!Live || Time.unscaledTime < nextReport) return;
            nextReport = Time.unscaledTime + 30;
            ContactsFix.Log("Perf (30 s; nested measurements): " + string.Join(" | ", samples.Select(s => s.Describe())));
            FramePacing.Report();
            foreach (var s in samples) s.Clear();
        }
        public static void BeginSample(out long __state) { __state = Live ? Stopwatch.GetTimestamp() : 0; }
        public static bool BeforeContactControls(object __0, bool __1)
        {
            if (__0 == null) return true;
            return contactRefresh.GetValue(__0, _ => new UiRefreshGate()).Due(contactWindow.GetValue(__0), __1, Time.unscaledTime);
        }
        public static Exception EndSample(MethodBase __originalMethod, long __state, Exception __exception)
        {
            if (__state != 0 && slots.TryGetValue(__originalMethod, out int i)) samples[i].Add(Stopwatch.GetTimestamp() - __state);
            return __exception;
        }

        public static object ReadFlightFlag(FieldInfo field, object target)
        {
            if (target is UnityEngine.Object obj && obj == null) return true;
            return FlightFlagReader.Read(field, helicopterFlight, target);
        }
        public static IEnumerable<CodeInstruction> ClearanceFlag(IEnumerable<CodeInstruction> input)
        {
            var get = typeof(FieldInfo).GetMethod("GetValue", new[] { typeof(object) });
            var replacement = typeof(PerformanceReview).GetMethod(nameof(ReadFlightFlag));
            var code = input.ToList(); int count = 0;
            foreach (var c in code)
                if ((c.opcode == OpCodes.Call || c.opcode == OpCodes.Callvirt) && Equals(c.operand, get))
                { c.opcode = OpCodes.Call; c.operand = replacement; count++; }
            if (count != 1) throw new InvalidOperationException("CV16 flag-read audit mismatch: " + count);
            return code;
        }
    }
}
