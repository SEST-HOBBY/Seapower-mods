using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using Sest.RuntimeFixes;

// Local battle weather (runtime/LocalWeatherPolicy.cs, runtime/LocalWeatherView.cs)
// under Mono without Unity or Noesis:
// 1. the hysteresis state machine and 2. the baseline save/restore controller
//    (LocalWeatherPolicy.cs and StormMapGeometry.cs are compiled into this exe),
//    with an Apply that throws partway, a mission trigger just before a save
//    or the end, and a trigger that sets the value the view already applied;
// 3. the DCM-to-game mapping and the sample clock (anchored at Engagement.At);
// 4. the battle geo frame against the constants in the game's and DCM's IL;
// 5. every game and DCM member LocalWeatherView binds, in the built
//    SEST.RuntimeFixes.dll, against Seapower-Scripts aae79728 and DCM 1.0.2;
// 6. the real DCM 1.0.2 weather model with Cyclone DARYA placed, sampled
//    through the runtime's own LocalWeatherView.Sample at Groups D and E of
//    the Hormuz test campaign (its campaign.json read by DCM's own Load):
//    clearly different weather in one battle, the controller following a
//    camera jump between them, and the start-of-battle gate: a plan whose
//    written weather is the model's own runs the view, a DCM Battle AI test
//    (BattlePlan.TestBattle, or its overridden calm weather) does not.
//   mono LocalWeatherTests.exe <flat refs> SEST.RuntimeFixes.dll DynamicCampaignMod.dll <sest-test-hormuz-weather folder>
static class LocalWeatherTests
{
    const BindingFlags All = BindingFlags.Instance | BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic;
    static int checks;
    static TextWriter console;
    static StringWriter log;
    static void Check(bool ok, string why)
    {
        checks++;
        if (!ok)
        {
            Console.SetOut(console);
            Console.WriteLine(log.ToString());
            throw new Exception("FAILED: " + why);
        }
    }
    static object Get(object value, string field)
    {
        Type t = value as Type ?? value.GetType();
        var f = t.GetField(field, All) ?? throw new MissingFieldException(t.FullName, field);
        return f.GetValue(value is Type ? null : value);
    }
    static void Set(object value, string field, object data) => value.GetType().GetField(field, All).SetValue(value, data);
    static object Call(object target, string name, Type[] types, params object[] args)
    {
        Type t = target as Type ?? target.GetType();
        var m = t.GetMethod(name, All, null, types, null) ?? throw new MissingMethodException(t.FullName, name);
        try { return m.Invoke(target is Type ? null : target, args); }
        catch (TargetInvocationException e) { throw e.InnerException; }
    }
    static DateTime Utc(string s) => DateTime.SpecifyKind(DateTime.ParseExact(s, "yyyy-MM-dd'T'HH:mm'Z'", CultureInfo.InvariantCulture), DateTimeKind.Utc);
    static int Lines(string text) => log.ToString().Split('\n').Count(l => l.Contains(text));

    static void Main(string[] args)
    {
        string refs = Path.GetFullPath(args[0]);
        AppDomain.CurrentDomain.AssemblyResolve += (s, e) => { string p = Path.Combine(refs, new AssemblyName(e.Name).Name + ".dll"); return File.Exists(p) ? Assembly.LoadFrom(p) : null; };
        Assembly.LoadFrom(Path.Combine(refs, "0Harmony.dll"));
        var rt = Assembly.LoadFrom(Path.GetFullPath(args[1]));
        var dcm = Assembly.LoadFrom(Path.GetFullPath(args[2]));
        string folder = Path.GetFullPath(args[3]);
        var game = Assembly.LoadFrom(Path.Combine(refs, "Seapower-Scripts.dll"));
        console = Console.Out;
        log = new StringWriter();
        Console.SetOut(log);
        try
        {
            Hysteresis();
            Controller();
            Mapping();
            Geo(game, dcm);
            Bindings(rt, game, dcm);
            Sampling(rt, dcm, folder);
        }
        finally { Console.SetOut(console); }
        if (Environment.GetEnvironmentVariable("SEST_STORMS_LOG") == "1") Console.Write(log.ToString());
        Console.WriteLine("Local weather: " + checks + " checks passed (hysteresis, save/restore, IL geo constants, " +
                          "Sea Power 0.9.3 and Dynamic Campaign Mod 1.0.2 bindings, DARYA sampled at Groups D and E, own-weather gate); no Unity, no PC gameplay claim.");
    }

    static ViewWeather W(int ss, bool rain = false, bool thunder = false, string wind = "NE", bool fog = false, bool snow = false) =>
        new ViewWeather { SeaState = ss, Rain = rain, Lightning = thunder, Wind = wind, Fog = fog, Snow = snow };

    // 1. Hysteresis: confirm, dwell, whole steps, flag rate, wind.
    static void Hysteresis()
    {
        Check(LocalWeatherHysteresis.ConfirmSeconds >= 3 && LocalWeatherHysteresis.ConfirmSeconds <= 10 &&
              LocalWeatherHysteresis.SeaDwellSeconds >= 20 && LocalWeatherHysteresis.SeaDwellSeconds <= 30 &&
              LocalWeatherHysteresis.FlagDwellSeconds >= 20 && LocalWeatherHysteresis.WindDwellSeconds >= 20,
              "confirm " + LocalWeatherHysteresis.ConfirmSeconds + " s; sea state at most one change per " + LocalWeatherHysteresis.SeaDwellSeconds +
              " s; rain/thunder/snow/fog at most once per " + LocalWeatherHysteresis.FlagDwellSeconds + " s; wind per " + LocalWeatherHysteresis.WindDwellSeconds + " s");
        var h = new LocalWeatherHysteresis(W(3));
        var calm = W(3);
        var storm = W(9, true, true, "SE");
        Check(h.Step(0, calm).Changed.Count == 0, "no change while the target is the applied weather");
        var d = h.Step(100, storm);
        Check(d.Changed.Count == 0 && d.Applied.Equals(calm) && d.Held.Any(x => x.StartsWith("sea 3->9 confirming 0/5")) && d.Held.Any(x => x.StartsWith("rain on confirming")),
              "a new target is only pending at first: " + string.Join("; ", d.Held));
        d = h.Step(102, storm);
        Check(d.Changed.Count == 0, "still confirming 2 s later");
        d = h.Step(104, calm);
        Check(d.Changed.Count == 0 && d.Held.Count == 0, "the view went back before 5 s: nothing pending, nothing applied");
        h.Step(106, storm);
        h.Step(108, storm);
        d = h.Step(110, storm);
        Check(d.Changed.Count == 0, "the confirm restarts from the new arrival (4 s)");
        d = h.Step(112, storm);
        Check(d.Changed.SequenceEqual(new[] { ViewChannel.Sea, ViewChannel.Wind, ViewChannel.Rain, ViewChannel.Lightning }) && d.Applied.Equals(storm),
              "after 6 s in the storm: sea straight to 9 (one whole step), wind, rain and thunder, in the trigger order");
        Check(h.Step(114, storm).Changed.Count == 0, "applied: no further change");

        // Leaving: confirmed after 5 s, but the sea and wind wait out their dwell.
        h.Step(120, calm);
        d = h.Step(126, calm);
        Check(!d.Changed.Contains(ViewChannel.Sea) && d.Held.Any(x => x.StartsWith("sea 9->3: once per 25 s (11 s left)")) &&
              !d.Changed.Contains(ViewChannel.Rain) && d.Held.Any(x => x.StartsWith("rain off: once per 20 s (6 s left)")),
              "14 s after the last change: sea held 11 s more, rain 6 s more: " + string.Join("; ", d.Held));
        d = h.Step(132, calm);
        Check(d.Changed.SequenceEqual(new[] { ViewChannel.Rain, ViewChannel.Lightning }) && d.Applied.SeaState == 9, "at 20 s rain and thunder go off; the sea still waits");
        d = h.Step(137, calm);
        Check(d.Changed.SequenceEqual(new[] { ViewChannel.Sea, ViewChannel.Wind }) && d.Applied.Equals(calm), "at 25 s the sea goes straight back to 3 and the wind to NE");

        // A target flickering on one side (8, 9, 8) still confirms; the latest value is applied.
        h = new LocalWeatherHysteresis(W(3));
        h.Step(0, W(8)); h.Step(2, W(9)); h.Step(4, W(8));
        d = h.Step(6, W(9));
        Check(d.Changed.SequenceEqual(new[] { ViewChannel.Sea }) && d.Applied.SeaState == 9, "a target moving 8, 9, 8, 9 above the applied 3 confirms after 5 s and applies 9");
        // A target flickering across the applied value never applies.
        h = new LocalWeatherHysteresis(W(5));
        int applied = 0;
        for (int t = 0; t < 120; t += 2) applied += h.Step(t, W(t % 4 == 0 ? 6 : 5)).Changed.Count;
        Check(applied == 0, "a target flickering 5/6 at a boundary while 5 is applied changes nothing in 2 minutes");
        // At most one sea change per dwell, however the target moves.
        h = new LocalWeatherHysteresis(W(0));
        var times = new List<int>();
        for (int t = 0; t <= 300; t += 2) if (h.Step(t, W(t / 10 % 13)).Changed.Contains(ViewChannel.Sea)) times.Add(t);
        Check(times.Count >= 5 && times.Zip(times.Skip(1), (a, b) => b - a).All(g => g >= 25), "a target sweeping 0..12: sea changes at " + string.Join(", ", times) + " s, never closer than 25 s");
        // Reset (an outside change) drops pending changes but keeps the dwell.
        h = new LocalWeatherHysteresis(W(3));
        h.Step(0, W(9)); h.Step(6, W(9));
        h.Step(8, W(9, true));
        h.Reset(W(4));
        d = h.Step(10, W(9, true));
        Check(d.Changed.Count == 0 && h.Applied.SeaState == 4 && d.Held.Any(x => x.StartsWith("sea 4->9 confirming 0/5")), "after a reset the target confirms again from the new weather");
        d = h.Step(16, W(9, true));
        Check(!d.Changed.Contains(ViewChannel.Sea) && d.Changed.Contains(ViewChannel.Rain) && d.Held.Any(x => x.Contains("once per 25 s")),
              "and the sea's dwell from its last change (6 s) still holds after a reset, while rain applies");
        Check(W(7, true, true, "SW").ToString() == "SS7 rain thunder wind SW" && W(3).ToString() == "SS3 dry wind NE", "the log text: \"SS7 rain thunder wind SW\", \"SS3 dry wind NE\"");
    }

    sealed class Recorder : IViewWeatherTarget
    {
        internal ViewWeather Fields;
        internal readonly List<string> Calls = new List<string>();
        // Apply throws after this many setters (a setter or DynamicSky.ForceUpdate failing partway); -1 never.
        internal int FailAfter = -1;
        internal bool ReadFails;
        // The failing setter also leaves the game unreadable (Read throws from then on).
        internal bool UnreadableAfterFailure;
        public ViewWeather Read() => ReadFails ? throw new InvalidOperationException("read failed") : Fields;
        public void Apply(ViewWeather w, IList<ViewChannel> changed)
        {
            int done = 0;
            foreach (var c in changed)
            {
                if (FailAfter >= 0 && done++ >= FailAfter) { FailAfter = -1; ReadFails |= UnreadableAfterFailure; throw new TargetInvocationException(new InvalidOperationException("setter failed")); }
                switch (c)
                {
                    case ViewChannel.Sea: Fields.SeaState = w.SeaState; Calls.Add("setSeaState " + w.SeaState); break;
                    case ViewChannel.Wind: Fields.Wind = w.Wind; Calls.Add("wind " + w.Wind); break;
                    case ViewChannel.Rain: Fields.Rain = w.Rain; Calls.Add("rain " + w.Rain); break;
                    case ViewChannel.Lightning: Fields.Lightning = w.Lightning; Calls.Add("lightning " + w.Lightning); break;
                    case ViewChannel.Snow: Fields.Snow = w.Snow; Calls.Add("snow " + w.Snow); break;
                    case ViewChannel.Fog: Fields.Fog = w.Fog; Calls.Add("fog " + w.Fog); break;
                }
            }
        }
        public void WriteFields(ViewWeather w) { Fields = w; Calls.Add("fields " + w); }
    }

    // 2. The baseline: kept, written by every save, restored at the end; an
    //    outside change (a mission trigger) becomes the new baseline.
    static void Controller()
    {
        var env = new Recorder { Fields = W(3, wind: "N") };
        var c = new LocalWeatherController(env);
        Check(c.Baseline.Equals(W(3, wind: "N")) && c.Applied.Equals(c.Baseline), "the baseline is the game's weather when the battle's view layer starts");
        Check(!c.BeforeSave() && env.Calls.Count == 0, "a save with the view weather at the baseline writes nothing extra");
        var storm = W(9, true, true, "SE");
        c.Tick(0, storm); c.Tick(6, storm);
        Check(env.Fields.Equals(storm) && env.Calls.SequenceEqual(new[] { "setSeaState 9", "wind SE", "rain True", "lightning True" }),
              "the view weather reaches the game through the trigger setters: " + string.Join(", ", env.Calls));
        env.Calls.Clear();
        bool swapped = c.BeforeSave();
        Check(swapped && env.Fields.Equals(W(3, wind: "N")) && env.Calls.SequenceEqual(new[] { "fields SS3 dry wind N" }), "during a save the fields hold the baseline (plain setters, no Ceto)");
        c.AfterSave(swapped);
        Check(env.Fields.Equals(storm) && env.Calls.Last() == "fields SS9 rain thunder wind SE", "after the save the view weather is back");
        Check(c.Tick(8, storm).Changed.Count == 0 && c.External == null, "a save is not mistaken for an outside change");
        // A mission trigger sets sea state 5 mid-battle.
        env.Fields.SeaState = 5;
        var d = c.Tick(10, storm);
        Check(c.External != null && c.External.StartsWith("Sea changed outside") && c.Baseline.SeaState == 5 && c.Baseline.Rain == false && c.Applied.SeaState == 5 && d.Changed.Count == 0,
              "an outside sea-state change becomes the baseline's sea state, the rest of the baseline stays: " + c.External);
        env.Calls.Clear();
        var put = c.Restore();
        Check(put.SequenceEqual(new[] { ViewChannel.Wind, ViewChannel.Rain, ViewChannel.Lightning }) && env.Fields.Equals(W(5, wind: "N")) &&
              env.Calls.SequenceEqual(new[] { "wind N", "rain False", "lightning False" }), "the end of the battle restores the baseline visibly: " + string.Join(", ", env.Calls));
        Check(c.Restore().Count == 0 && !c.BeforeSave(), "restored: nothing more to restore or swap");
        FailedApply();
        TriggersAndSaves();
    }

    static bool Throws(Action a)
    {
        try { a(); return false; }
        catch (TargetInvocationException) { return true; }
    }

    // An Apply that throws partway (setSeaState ran, the wind setter or
    // DynamicSky.ForceUpdate threw): the game holds part of the view weather.
    static void FailedApply()
    {
        // The review's case: baseline SS3 NE, a tick moves sea to 7 and wind to SW, the wind setter throws.
        var env = new Recorder { Fields = W(3, wind: "NE") };
        var c = new LocalWeatherController(env);
        var storm = W(7, wind: "SW");
        c.Tick(0, storm);
        env.FailAfter = 1;
        Check(Throws(() => c.Tick(6, storm)) && env.Fields.Equals(W(7, wind: "NE")), "a setter throws after setSeaState 7: the game holds SS7, the wind is still NE");
        Check(c.Applied.Equals(env.Fields), "Applied is what the game holds after the failed Apply (read back), not the stale SS3: " + c.Applied);
        Check(c.BeforeSave() && env.Fields.Equals(W(3, wind: "NE")), "a save after the failed Apply still writes the baseline SS3 NE (diffed against what the game holds)");
        c.AfterSave(true);
        Check(env.Fields.Equals(W(7, wind: "NE")), "and puts the game's SS7 back after it");
        env.Calls.Clear();
        var put = c.Restore();
        Check(put.SequenceEqual(new[] { ViewChannel.Sea }) && env.Fields.Equals(W(3, wind: "NE")) && env.Calls.SequenceEqual(new[] { "setSeaState 3" }),
              "the stop path's Restore puts the half-applied sea state back (the half-failed tick is not taken for a trigger): " + string.Join(", ", env.Calls));
        Check(c.Baseline.Equals(W(3, wind: "NE")), "the baseline is unchanged by the failed Apply");

        // The Apply fails partway and the game cannot be read afterwards: Applied is the
        // hysteresis' target (never the stale weather), and Restore puts every channel back.
        env = new Recorder { Fields = W(3, wind: "NE") };
        c = new LocalWeatherController(env);
        c.Tick(0, storm);
        env.FailAfter = 1;
        env.UnreadableAfterFailure = true;
        bool threw = false;
        try { c.Tick(6, storm); } catch (TargetInvocationException) { threw = true; }
        Check(threw && c.Applied.Equals(storm), "with the game unreadable after the failed Apply, Applied is the change that was being applied (" + c.Applied + "), not the stale baseline");
        env.Calls.Clear();
        put = c.Restore();
        Check(put.Count == 6 && env.Fields.Equals(W(3, wind: "NE")), "and Restore, unable to read the game, puts every channel back: " + string.Join(", ", env.Calls));
        env.ReadFails = false;

        // Restore never trusts the cache: the game holds rain the cache does not know about
        // after a failed Apply that could not be read back.
        env = new Recorder { Fields = W(3, wind: "NE") };
        c = new LocalWeatherController(env);
        var wet = W(3, rain: true, thunder: true, wind: "NE");
        c.Tick(0, wet);
        env.FailAfter = 1;
        env.UnreadableAfterFailure = true;
        try { c.Tick(6, wet); } catch (TargetInvocationException) { }
        env.ReadFails = false;
        env.Calls.Clear();
        put = c.Restore();
        Check(put.SequenceEqual(new[] { ViewChannel.Rain }) && env.Fields.Equals(W(3, wind: "NE")),
              "the rain a failed Apply left on is put back from what the game holds (" + string.Join(", ", env.Calls) + ")");
    }

    // A mission trigger's Set Weather just before a save or the end; a trigger
    // setting the value the view already applied.
    static void TriggersAndSaves()
    {
        var env = new Recorder { Fields = W(3, wind: "N") };
        var c = new LocalWeatherController(env);
        var storm = W(7, wind: "N");
        c.Tick(0, storm); c.Tick(6, storm);
        Check(env.Fields.SeaState == 7 && c.Baseline.SeaState == 3, "the view has SS7 applied over the SS3 baseline");
        // A trigger sets rain on; the save comes before the next tick.
        env.Fields.Rain = true;
        env.Calls.Clear();
        bool swapped = c.BeforeSave();
        Check(swapped && c.Baseline.Equals(W(3, rain: true, wind: "N")) && env.Fields.Equals(W(3, rain: true, wind: "N")) && c.External != null && c.External.StartsWith("Rain changed outside"),
              "a trigger's rain within 2 s before a save is adopted: the save writes SS3 with rain (" + c.External + ")");
        c.AfterSave(swapped);
        Check(env.Fields.Equals(W(7, rain: true, wind: "N")), "and after the save the screen keeps the trigger's rain with the view's SS7");
        Check(c.Tick(8, storm).Changed.Count == 0 && c.External == null, "the next tick sees nothing new");
        // A trigger sets fog just before the battle ends.
        env.Fields.Fog = true;
        env.Calls.Clear();
        var put = c.Restore();
        Check(c.Baseline.Fog && env.Fields.Equals(W(3, rain: true, fog: true, wind: "N")) && put.SequenceEqual(new[] { ViewChannel.Sea }),
              "a trigger's fog just before the end is kept by the restore, which puts back only the sea: " + string.Join(", ", env.Calls));

        // A trigger sets the sea state to the value the view already applied (SS7):
        // only the trigger's own record (Trigger.TryActionTrigger's tuples) shows it.
        env = new Recorder { Fields = W(3, wind: "N") };
        c = new LocalWeatherController(env);
        c.Tick(0, storm); c.Tick(6, storm);
        c.Reconcile();
        Check(c.Baseline.SeaState == 3 && c.External == null, "comparing values alone cannot see a trigger that sets SS7 over the applied SS7");
        c.Reconcile(new[] { ViewChannel.Sea });
        Check(c.Baseline.SeaState == 7 && c.External != null && c.External.StartsWith("Sea set by a mission trigger"),
              "the trigger's channels are adopted whatever their value: baseline now SS7 (" + c.External + ")");
        Check(!c.BeforeSave(), "so a save writes the trigger's SS7 (nothing to swap)");
        env.Calls.Clear();
        Check(c.Restore().Count == 0 && env.Calls.Count == 0, "and the end keeps it");
        // The hysteresis restarts from the adopted weather.
        c = new LocalWeatherController(env = new Recorder { Fields = W(3, wind: "N") });
        c.Tick(0, storm); c.Tick(6, storm);
        c.Reconcile(new[] { ViewChannel.Sea, ViewChannel.Rain });
        Check(c.Baseline.Equals(W(7, wind: "N")) && c.External.StartsWith("Sea, Rain set by a mission trigger"), "every channel the trigger set is adopted, rain off included: " + c.External);
    }

    // 3. DCM BattleWeather -> view target; the sample clock.
    static void Mapping()
    {
        var b = W(3, wind: "NE");
        var t = LocalWeatherPolicy.Target(9, true, true, false, true, "SE", "overcast", b);
        Check(t.Equals(new ViewWeather { SeaState = 9, Rain = true, Lightning = true, Fog = true, Wind = "SE" }), "Rain, Thunderstorm, Fog -> IsRaining, IsLightning, IsFog; WindFrom SE");
        t = LocalWeatherPolicy.Target(9, true, true, true, true, "SE", "Clear", b);
        Check(!t.Rain && !t.Lightning && !t.Snow && !t.Fog && t.SeaState == 9, "under held clear clouds no weather flag (as SceneCreator.setWeatherConditions skips Weather= then)");
        Check(LocalWeatherPolicy.Target(15, false, false, false, false, "NNE", "broken", b).SeaState == 12 && LocalWeatherPolicy.Target(-1, false, false, false, false, "x", "broken", b).Wind == "NE",
              "sea state clamped to 0..12 (setSeaState's range); an unknown wind point keeps the baseline wind");
        var start = Utc("2028-01-15T08:07Z").AddSeconds(13);
        Check(LocalWeatherPolicy.SampleTime(start, start) == start && LocalWeatherPolicy.SampleTime(start, start.AddMinutes(9).AddSeconds(59)) == start &&
              LocalWeatherPolicy.SampleTime(start, start.AddMinutes(10)) == start.AddMinutes(10) && LocalWeatherPolicy.SampleTime(start, start.AddMinutes(27)) == start.AddMinutes(20) &&
              LocalWeatherPolicy.SampleTime(start, start.AddMinutes(-1)) == start && LocalWeatherPolicy.SampleTime(start, start).Kind == DateTimeKind.Utc,
              "samples at 10-minute steps of battle time from the exact Engagement.At (08:07:13, 08:17:13, ...): step 0 is the time [Environment] was written for " +
              "(DCM caches 24 snapshots keyed by the second)");
    }

    // A small IL reader: (opcode, operand) for every instruction.
    static readonly Dictionary<short, OpCode> Codes = typeof(OpCodes).GetFields(BindingFlags.Public | BindingFlags.Static).Select(f => (OpCode)f.GetValue(null)).ToDictionary(o => o.Value);
    static List<KeyValuePair<OpCode, object>> Il(MethodBase m)
    {
        var il = m.GetMethodBody().GetILAsByteArray();
        var list = new List<KeyValuePair<OpCode, object>>();
        int i = 0;
        while (i < il.Length)
        {
            short v = il[i] == 0xFE ? (short)(0xFE00 | il[i + 1]) : il[i];
            i += il[i] == 0xFE ? 2 : 1;
            var op = Codes[v];
            object operand = null;
            switch (op.OperandType)
            {
                case OperandType.InlineNone: break;
                case OperandType.ShortInlineBrTarget: case OperandType.ShortInlineI: case OperandType.ShortInlineVar: operand = il[i]; i += 1; break;
                case OperandType.InlineVar: i += 2; break;
                case OperandType.ShortInlineR: operand = BitConverter.ToSingle(il, i); i += 4; break;
                case OperandType.InlineR: operand = BitConverter.ToDouble(il, i); i += 8; break;
                case OperandType.InlineI8: i += 8; break;
                case OperandType.InlineSwitch: i += 4 + 4 * BitConverter.ToInt32(il, i); break;
                case OperandType.InlineMethod: operand = m.Module.ResolveMethod(BitConverter.ToInt32(il, i)); i += 4; break;
                default: operand = BitConverter.ToInt32(il, i); i += 4; break;
            }
            list.Add(new KeyValuePair<OpCode, object>(op, operand));
        }
        return list;
    }

    // 4. The battle frame: units are at the same lat/lon in the game as in DCM.
    static void Geo(Assembly game, Assembly dcm)
    {
        var utils = game.GetType("SeaPower.Utils", true);
        MethodInfo U(string name, int n) => utils.GetMethods(All).Single(m => m.Name == name && m.GetParameters().Length == n);
        var rel = Il(U("RelativeNMToGeo", 2));
        var nmToUnits = rel.Where(x => x.Key == OpCodes.Ldc_R4 && (float)x.Value != 0).Select(x => (double)(float)x.Value).ToList();
        Check(nmToUnits.Count == 2 && nmToUnits.All(x => Math.Abs(x - 27.5594959) < 1e-5), "Utils.RelativeNMToGeo: x and y nm * 27.5594959 Unity units");
        var offset = Il(U("GeoPosFromRelativeOffset", 2));
        var perDegree = offset.Where(x => x.Key == OpCodes.Ldc_R8).Select(x => (double)x.Value).ToList();
        Check(perDegree.SequenceEqual(new[] { 1653.5697936324739 }) && offset.Count(x => x.Key == OpCodes.Div) == 2,
              "Utils.GeoPosFromRelativeOffset: lon and lat += units / 1653.5697936324739 (one constant, both axes, no cos(lat))");
        double nmPerDegree = perDegree[0] / nmToUnits[0];
        Check(Math.Abs(nmPerDegree - LocalWeatherGeo.NmPerDegree) < 1e-4, "the game's battle frame is " + nmPerDegree.ToString("0.0000", CultureInfo.InvariantCulture) + " nm per degree = LocalWeatherGeo.NmPerDegree");
        var point = dcm.GetType("DynamicCampaignMod.Game.Battle.MissionWriter", true).GetMethods(All).Single(m => m.Name == "Point" && m.ReturnType == typeof(string));
        var sixty = Il(point).Where(x => x.Key == OpCodes.Ldc_R8).Select(x => (double)x.Value).ToList();
        Check(sixty.SequenceEqual(new[] { 60.0, 60.0 }), "DCM's MissionWriter.Point writes (lon - centre) * 60 and (lat - centre) * 60 nm: the same flat 60, so a unit's game lat/lon is DCM's");
        LocalWeatherGeo.OffsetNm(20.9, 65.5, 20.55, 64.77, out double e, out double n);
        LocalWeatherGeo.FromOffsetNm(20.9, 65.5, e, n, out double lat, out double lon);
        Check(Math.Abs(e - (64.77 - 65.5) * 60) < 1e-9 && Math.Abs(n - (20.55 - 20.9) * 60) < 1e-9 && Math.Abs(lat - 20.55) < 1e-12 && Math.Abs(lon - 64.77) < 1e-12,
              "OffsetNm and FromOffsetNm are MissionWriter.Point and GeoPosFromRelativeOffset, inverses");
        var view = Il(U("worldPositionFromUnityToLongLat", 2));
        var calls = view.Where(x => x.Key == OpCodes.Call).Select(x => ((MethodBase)x.Value).Name).ToList();
        Check(calls.Contains("worldPositionFromUnityToLongLatLCC") && calls.Contains("worldPositionFromUnityToLongLatEquirect") && calls.Contains("get_Data"),
              "Utils.worldPositionFromUnityToLongLat (what RenderPosition.OnUpdate converts the camera with, and the view uses) picks LCC or equirect on Globals.LCCTerrain.Enabled");
        var tile = Il(U("worldPositionFromUnityToLongLatEquirect", 2)).Where(x => x.Key == OpCodes.Ldc_R8).Select(x => (double)x.Value).ToList();
        Check(tile.Count(x => x == 330.71395874023438) == 2 && Math.Abs(perDegree[0] / 330.71395874023438 - 5) < 1e-9,
              "its equirect branch divides by 330.714 units per terrain tile, 1/5 degree (1653.5698 / 330.714 = 5)");
        var render = game.GetType("SeaPower.RenderPosition", true).GetMethod("OnUpdate", All, null, Type.EmptyTypes, null);
        Check(Il(render).Count(x => x.Key == OpCodes.Call && ((MethodBase)x.Value).Name == "worldPositionFromUnityToLongLat") >= 2,
              "RenderPosition.OnUpdate converts its transform with Utils.worldPositionFromUnityToLongLat, as the view's camera point does");
    }

    // 5. Every member LocalWeatherView binds, in the built runtime.
    static void Bindings(Assembly rt, Assembly game, Assembly dcm)
    {
        var ws = rt.GetType("Sest.RuntimeFixes.WorldStorms", true);
        var lv = rt.GetType("Sest.RuntimeFixes.LocalWeatherView", true);
        ws.GetField("Diagnostics", All).SetValue(null, true);
        Call(ws, "Start", new[] { typeof(Assembly), typeof(bool), typeof(bool) }, null, true, false);
        Check((bool)Get(ws, "installed") && !(bool)Get(ws, "localWanted"), "WorldStorms.Start(native, diagnostics, mapLayer) as before: no local view (the native image is null here)");
        Check(!(bool)Get(lv, "installed"), "LocalWeatherView is not installed by the three-argument Start");
        Check((bool)Call(lv, "Bind", new[] { typeof(Assembly) }, game) && (bool)Get(lv, "bound") && !(bool)Get(lv, "stopped"),
              "LocalWeatherView.Bind binds every member it uses in Sea Power 0.9.3 (Seapower-Scripts aae79728) and Dynamic Campaign Mod 1.0.2 (18a2416e)");
        foreach (var f in lv.GetFields(All).Where(f => f.IsStatic && (typeof(MemberInfo).IsAssignableFrom(f.FieldType))))
            Check(f.GetValue(null) != null, "local weather member bound: " + f.Name);
        Check(Lines("world storms local weather bind: ") >= 45 && Lines(" MISSING") == 0 && Lines("world storms local weather bind: all members") == 1,
              "one bind line per member (" + Lines("world storms local weather bind: ") + "), none missing");
        foreach (var name in new[] { "battleActive", "battlePlan", "planEngagement", "campaignSim", "simState", "forState", "missionElapsed" })
            Check(Get(ws, name) != null, "shared with the map layer (WorldStorms.BindBattle): " + name);
        var write = (MethodInfo)Get(lv, "writeMission");
        Check(write.DeclaringType.FullName == "SeaPower.SaveLoadManager" && write.IsPrivate && write.IsStatic &&
              string.Join(", ", write.GetParameters().Select(p => p.ParameterType.Name)) == "SaveType, String, Boolean, String",
              "the save hook is SaveLoadManager.WriteMissionToFile(SaveType, string, bool, string), SaveGame's only writer");
        Check(Il(write).Count(x => x.Key == OpCodes.Callvirt && ((MethodBase)x.Value).Name == "get_SeaState") == 1 &&
              Il(write).Count(x => x.Key == OpCodes.Callvirt && ((MethodBase)x.Value).Name == "get_IsRaining") == 1 &&
              Il(write).Count(x => x.Key == OpCodes.Callvirt && ((MethodBase)x.Value).Name == "get_CurrentWindDirection") == 1,
              "WriteMissionToFile reads SeaState, IsRaining and the wind in its own body (the swap around it covers them)");
        var body = Il((MethodInfo)Get(lv, "setSeaState"));
        Check(body.Any(x => x.Key == OpCodes.Stfld && x.Value is int t && game.ManifestModule.ResolveField(t).Name == "windSpeed" &&
                            game.ManifestModule.ResolveField(t).DeclaringType.FullName == "Ceto.WaveSpectrum") &&
              body.Any(x => x.Key == OpCodes.Call && ((MethodBase)x.Value).Name == "set_SeaState"),
              "Environment.setSeaState sets the field and Ceto's WaveSpectrum.windSpeed (the visible sea), once per call");
        var plain = Il((MethodInfo)Get(lv, "setSeaStateField"));
        Check(!plain.Any(x => (x.Key == OpCodes.Call || x.Key == OpCodes.Callvirt) && ((MethodBase)x.Value).DeclaringType.FullName.StartsWith("Ceto")),
              "Environment.set_SeaState (used during a save) does not touch Ceto");
        var change = game.GetType("SeaPower.Environment", true).GetMethod("changeCloudsCoverage", All, null, new[] { typeof(string) }, null);
        Check(Il(change).Any(x => x.Key == OpCodes.Stfld && x.Value is int t && game.ManifestModule.ResolveField(t).Name == "_missionClouds"),
              "why clouds are held: Environment.changeCloudsCoverage writes Session._missionClouds");
        var before = lv.GetMethod("BeforeSave", All);
        var after = lv.GetMethod("AfterSave", All);
        Check(before.GetParameters().Single().ParameterType == typeof(bool).MakeByRefType() && after.ReturnType == typeof(Exception) &&
              after.GetParameters().Select(p => p.Name).SequenceEqual(new[] { "__state", "__exception" }), "prefix BeforeSave(ref bool __state), finalizer AfterSave(bool __state, Exception __exception)");
        var afterTrigger = lv.GetMethod("AfterTrigger", All);
        Check(afterTrigger.IsStatic && afterTrigger.GetParameters().Select(p => p.Name).SequenceEqual(new[] { "__instance", "__result" }) && afterTrigger.GetParameters()[1].ParameterType == typeof(bool),
              "postfix AfterTrigger(object __instance, bool __result) on Trigger.TryActionTrigger");
        var tryAction = (MethodInfo)Get(lv, "tryAction");
        var actionIl = Il(tryAction);
        var rets = actionIl.Select((x, i) => new { x, i }).Where(y => y.x.Key == OpCodes.Ret).Select(y => y.i).ToList();
        Check(tryAction.DeclaringType.FullName == "SeaPower.Trigger" && tryAction.ReturnType == typeof(bool) && rets.Count == 3 &&
              actionIl[rets[0] - 1].Key == OpCodes.Ldc_I4_0 && actionIl[rets[1] - 1].Key == OpCodes.Ldc_I4_0 && actionIl[rets[2] - 1].Key == OpCodes.Ldc_I4_1,
              "Trigger.TryActionTrigger returns false only from its two early exits and true after running its actions (so __result true means the Set Weather actions ran)");
        string[] setters = { "set_SeaState", "set_CurrentWindDirection", "set_IsRaining", "set_IsLightning", "set_IsSnowing", "set_IsFog" };
        var called = actionIl.Where(x => x.Key == OpCodes.Callvirt && x.Value is MethodBase mb && setters.Contains(mb.Name)).Select(x => ((MethodBase)x.Value).Name).Distinct().ToList();
        Check(called.SequenceEqual(setters) && actionIl.Count(x => x.Key == OpCodes.Ldflda && x.Value is int t2 && game.ManifestModule.ResolveField(t2).Name.StartsWith("_set")) >= 12,
              "TryActionTrigger sets sea state, wind, rain, lightning, snow and fog from its _set* tuples, in that order: " + string.Join(", ", called));
        var trigger = System.Runtime.Serialization.FormatterServices.GetUninitializedObject(game.GetType("SeaPower.Trigger", true));
        Check(((IEnumerable)Call(lv, "TriggerChannels", new[] { typeof(object) }, trigger)).Cast<object>().Count() == 0, "a trigger with no Set Weather action sets no channel");
        Set(trigger, "_setSeaState", (true, 6));
        Set(trigger, "_setRain", (true, false));
        var trig = ((IEnumerable)Call(lv, "TriggerChannels", new[] { typeof(object) }, trigger)).Cast<object>().Select(x => x.ToString()).ToList();
        Check(trig.SequenceEqual(new[] { "Sea", "Rain" }), "a trigger setting sea state 6 and rain off names Sea and Rain (rain off included): " + string.Join(", ", trig));
        Call(lv, "AfterTrigger", new[] { typeof(object), typeof(bool) }, trigger, true);
        Check(!(bool)Get(lv, "stopped"), "outside a battle the trigger postfix does nothing");
        Call(lv, "BeforeSave", new[] { typeof(bool).MakeByRefType() }, false);
        Check((Exception)Call(lv, "AfterSave", new[] { typeof(bool), typeof(Exception) }, false, null) == null, "outside a battle the save hooks do nothing");
        Call(lv, "Tick", Type.EmptyTypes);
        Check(!(bool)Get(lv, "stopped"), "a tick when not installed does nothing");
        Call(lv, "Install", new[] { typeof(Assembly) }, new object[] { null });
        Check(!(bool)Get(lv, "installed"), "Install without the game assembly installs nothing");
    }

    // 6. The real model: Groups D and E of the Hormuz campaign at T.
    static readonly DateTime T = Utc("2028-01-15T08:00Z");
    static void Sampling(Assembly rt, Assembly dcm, string folder)
    {
        var ws = rt.GetType("Sest.RuntimeFixes.WorldStorms", true);
        var lv = rt.GetType("Sest.RuntimeFixes.LocalWeatherView", true);
        var defType = dcm.GetType("DynamicCampaignMod.Core.Data.CampaignDefinition", true);
        var modelType = dcm.GetType("DynamicCampaignMod.Core.Sim.WeatherModel", true);
        var geoType = dcm.GetType("DynamicCampaignMod.Core.Geo.GeoPoint", true);
        string file = Path.Combine(folder, "campaign.json");
        object def;
        try { def = defType.GetMethod("Load", BindingFlags.Public | BindingFlags.Static, null, new[] { typeof(string) }, null).Invoke(null, new object[] { file }); }
        catch (TargetInvocationException e) { throw e.InnerException; }
        Check(def != null && (string)Get(def, "FilePath") == file, "Dynamic Campaign Mod's own Load and Validate accept the Hormuz campaign with Groups D, E and Red D");
        var forces = ((IEnumerable)Get(def, "forces")).Cast<object>().ToDictionary(f => (string)Get(f, "name"), f => (double[])Get(f, "at"));
        Check(forces.ContainsKey("Group D - inside DARYA") && forces.ContainsKey("Group E - outside DARYA") && forces.ContainsKey("Red D - Makran raiders"), "the campaign has Groups D and E and Red D");
        double[] gd = forces["Group D - inside DARYA"], ge = forces["Group E - outside DARYA"];
        var bounds = Get(def, "bounds");
        Check((double)Get(bounds, "lonMax") >= 68 && ge[1] < (double)Get(bounds, "lonMax"), "the bounds take in Group E (lonMax " + Get(bounds, "lonMax") + ")");

        Func<int, object> For = seed => Call(modelType, "For", new[] { defType, typeof(int) }, def, seed);
        object model = For(4242);
        Check((bool)Call(ws, "HasPlacedStorms", new[] { typeof(object) }, model), "the campaign's model carries its placed storm, so the local view is active in its battles");
        Check((string)Call(ws, "PlacedStormNames", new[] { typeof(object) }, model) == "Cyclone DARYA", "named Cyclone DARYA");
        object theatre = Call(dcm.GetType("DynamicCampaignMod.Core.Sim.WeatherTheatre", true), "Of", new[] { defType }, def);
        object plainModel = Activator.CreateInstance(modelType, All, null, new[] { theatre, 4242, bounds }, null);
        Check(!(bool)Call(ws, "HasPlacedStorms", new[] { typeof(object) }, plainModel) && !(bool)Call(ws, "HasPlacedStorms", new[] { typeof(object) }, new object[] { null }),
              "a model without placed storms (and no model) leaves the battle's weather alone");

        object set = ws.GetMethod("SetFor", All).Invoke(null, new[] { def, model });
        object sys = ((object[])Get(set, "Systems"))[0];
        object c = Call(sys, "At", new[] { typeof(DateTime) }, T);
        double cLat = (double)Get(c, "Lat"), cLon = (double)Get(c, "Lon");
        double dd = StormMapGeometry.DistanceNm(cLat, cLon, gd[0], gd[1]), de = StormMapGeometry.DistanceNm(cLat, cLon, ge[0], ge[1]), sep = StormMapGeometry.DistanceNm(gd[0], gd[1], ge[0], ge[1]);
        double gale = (double)Call(modelType, "GaleRadiusNm", new[] { sys.GetType(), c.GetType() }, sys, c);
        // make_test_campaigns.local_check (Python) uses DCM's tropical radius rule: R*(Vmax*Env/34)^2, at most 0.8 Outer,
        // with R = clamp(Outer/10, 8, 45) from the sidecar's radius (StormSidecar.cs).
        double pR = (double)Get(c, "R"), pOuter = (double)Get(c, "Outer"), pV = (double)Get(c, "Vmax") * (double)Get(c, "Env");
        Check(Math.Abs(gale - Math.Min(0.8 * pOuter, pR * Math.Pow(pV / 34, 2))) < 1e-6 && Math.Abs(pR - Math.Max(8, Math.Min(45, pOuter / 10))) < 1e-6,
              "DCM's GaleRadiusNm is the rule make_test_campaigns.local_check applies: R " + pR.ToString("0.0") + ", Outer " + pOuter.ToString("0") + ", Vmax " + pV.ToString("0.0") + " -> " + gale.ToString("0.0") + " nm");
        Check(dd >= 30 && dd <= 50 && de > gale && sep <= 200 && dd < gale,
              "at 15 Jan 08:00Z DARYA is at " + cLat.ToString("0.00") + "N " + cLon.ToString("0.00") + "E: Group D " + dd.ToString("0") + " nm from the centre (inside the " +
              gale.ToString("0") + " nm gale ring), Group E " + de.ToString("0") + " nm (outside it), " + sep.ToString("0") + " nm apart (within the 200 nm open-sea join)");

        var vwType = rt.GetType("Sest.RuntimeFixes.ViewWeather", true);
        object baseline = Activator.CreateInstance(vwType);
        Set(baseline, "SeaState", 9); Set(baseline, "Wind", "S");
        var sample = lv.GetMethod("Sample", All);
        Func<object, double, double, DateTime, string, ViewWeather> S = (m, la, lo, t, held) =>
        {
            var a = new object[] { m, la, lo, t, held, baseline, null };
            object r = sample.Invoke(null, a);
            log.WriteLine("sample " + la + " " + lo + " " + t.ToString("HH:mm") + ": " + a[6]);
            return new ViewWeather { SeaState = (int)Get(r, "SeaState"), Rain = (bool)Get(r, "Rain"), Lightning = (bool)Get(r, "Lightning"), Snow = (bool)Get(r, "Snow"), Fog = (bool)Get(r, "Fog"), Wind = (string)Get(r, "Wind") };
        };
        var atD = S(model, gd[0], gd[1], T, "overcast");
        var atE = S(model, ge[0], ge[1], T, "overcast");
        Check(atD.SeaState >= 7 && atD.Rain && atE.SeaState <= 5 && !atE.Rain && atD.SeaState - atE.SeaState >= 3,
              "LocalWeatherView.Sample, DCM 1.0.2 with DARYA (seed 4242), 15 Jan 08:00Z: Group D " + atD + ", Group E " + atE);
        Console.SetOut(console);
        Console.WriteLine("Group D " + gd[0] + "N " + gd[1] + "E at 08:00Z: " + atD + " (" + dd.ToString("0") + " nm from DARYA at " + cLat.ToString("0.00") + "N " + cLon.ToString("0.00") + "E, gale ring " + gale.ToString("0") +
                          " nm); Group E " + ge[0] + "N " + ge[1] + "E: " + atE + " (" + de.ToString("0") + " nm); " + sep.ToString("0") + " nm apart");
        Console.SetOut(log);
        object battle = Call(model, "Battle", new[] { geoType, typeof(DateTime) }, Activator.CreateInstance(geoType, gd[0], gd[1]), T);
        Check((int)Get(battle, "SeaState") == atD.SeaState && (string)Get(battle, "Storm") == "Cyclone DARYA", "the sample is WeatherModel.Battle (At().ToBattle(), what [Environment] is written from), labelled Cyclone DARYA");
        object plainD = Call(plainModel, "Battle", new[] { geoType, typeof(DateTime) }, Activator.CreateInstance(geoType, gd[0], gd[1]), T);
        Check((int)Get(plainD, "SeaState") < atD.SeaState || !(bool)Get(plainD, "Rain"), "without DARYA Group D's weather is DCM's own background (SS" + Get(plainD, "SeaState") + ")");
        Check(S(model, ge[0], ge[1], T, "Clear").Equals(new ViewWeather { SeaState = atE.SeaState, Wind = atE.Wind }) && !S(model, gd[0], gd[1], T, "Clear").Rain,
              "with the battle's clouds held at Clear no rain is applied anywhere (the game draws none under a clear sky)");
        var window = new List<string>();
        for (var t = Utc("2028-01-15T07:00Z"); t <= Utc("2028-01-15T10:00Z"); t = t.AddMinutes(30))
        {
            var a = S(model, gd[0], gd[1], t, "overcast"); var b = S(model, ge[0], ge[1], t, "overcast");
            window.Add(t.ToString("HH:mm") + " D " + a.SeaState + (a.Rain ? "r" : "") + " E " + b.SeaState + (b.Rain ? "r" : ""));
            Check(a.SeaState >= 7 && a.Rain && b.SeaState <= 5 && a.SeaState - b.SeaState >= 3, "the window the README gives, " + t.ToString("HH:mm") + "Z: D " + a + ", E " + b);
        }
        // How often a new campaign shows the split (DCM draws new weather for each).
        int both = 0, dStorm = 0, eCalm = 0, n = 60;
        for (int k = 1; k <= n; k++)
        {
            object m = For(7919 * k);
            var a = S(m, gd[0], gd[1], T, "overcast"); var b = S(m, ge[0], ge[1], T, "overcast");
            if (a.SeaState >= 7) dStorm++;
            if (b.SeaState <= 5) eCalm++;
            if (a.SeaState >= 7 && b.SeaState <= 5) both++;
        }
        Check(dStorm >= 54 && eCalm >= 40 && both >= 40, "over " + n + " campaign seeds: Group D SS >= 7 in " + dStorm + ", Group E SS <= 5 in " + eCalm + ", both in " + both +
              " (README-TESTS.txt: if D and E read alike, start a new campaign)");
        Console.SetOut(console);
        Console.WriteLine("seeds: D SS>=7 " + dStorm + "/" + n + ", E SS<=5 " + eCalm + "/" + n + ", both " + both + "/" + n + "; window " + string.Join(", ", window));
        Console.SetOut(log);

        // The battle's written weather against the model's own (LocalWeatherView.NotOwnWeather).
        var planType = dcm.GetType("DynamicCampaignMod.Core.State.BattlePlan", true);
        var engType = dcm.GetType("DynamicCampaignMod.Core.State.Engagement", true);
        object eng = Activator.CreateInstance(engType, true);
        object centre = Activator.CreateInstance(geoType, gd[0], gd[1]);
        Set(eng, "Point", centre); Set(eng, "At", T);
        object plan = Activator.CreateInstance(planType, true);
        Set(plan, "Engagement", eng);
        // As Battles.Plan: Weather = Weather.At(state, Engagement.Point, Engagement.At) = WeatherModel.For(state).Battle(...).
        Set(plan, "Weather", Call(model, "Battle", new[] { geoType, typeof(DateTime) }, centre, T));
        for (int k = 1; k <= 30; k++) Call(model, "Battle", new[] { geoType, typeof(DateTime) }, Activator.CreateInstance(geoType, ge[0], ge[1]), T.AddMinutes(10 * k));
        Func<string> notOwn = () => (string)Call(lv, "NotOwnWeather", new[] { typeof(object), typeof(object), typeof(object) }, plan, model, eng);
        Check(notOwn() == null, "a battle DCM planned from the model: its written weather is the model's own at Engagement.Point and At (after 30 other samples), so the view runs");
        var at0 = LocalWeatherPolicy.SampleTime(T, T);
        Check(at0 == T && S(model, gd[0], gd[1], at0, "overcast").SeaState == (int)Get(Get(plan, "Weather"), "SeaState"),
              "at the battle centre at the start the view samples the exact Engagement.At, the written weather (SS" + Get(Get(plan, "Weather"), "SeaState") + ")");
        Set(plan, "TestBattle", true);
        string why = notOwn();
        Check(why != null && why.Contains("Battle AI test battle (BattlePlan.TestBattle)"), "a DCM Battle AI test battle (TestBattles.Build sets BattlePlan.TestBattle) keeps its own weather: " + why);
        Set(plan, "TestBattle", false);
        // TestBattles.Build's override: Scattered, sea state 2, wind <= 8 kn, no Typhoon/Thunderstorm/Fog/Snow/Rain.
        object test = Call(model, "Battle", new[] { geoType, typeof(DateTime) }, centre, T);
        Check(!ReferenceEquals(test, Get(plan, "Weather")), "WeatherModel.Battle returns a new BattleWeather each call");
        Set(test, "Clouds", "Scattered"); Set(test, "SeaState", 2); Set(test, "WindKnots", Math.Min((int)Get(test, "WindKnots"), 8));
        foreach (var f in new[] { "Typhoon", "Thunderstorm", "Fog", "Snow", "Rain" }) Set(test, f, false);
        Set(plan, "Weather", test);
        why = notOwn();
        Check(why != null && why.Contains("not the campaign model's own") && why.Contains("SeaState 2 written, " + atD.SeaState + " model") && why.Contains("Clouds Scattered written"),
              "a battle whose written weather was overridden (the AI test's calm) keeps it, the log says what differs: " + why);
        Set(plan, "Weather", null);
        Check(notOwn() == "the battle plan has no weather" && (string)Call(lv, "NotOwnWeather", new[] { typeof(object), typeof(object), typeof(object) }, null, model, eng) == "no battle plan",
              "no plan weather (or no plan): the view stays off");

        // The camera jumps from D to E and back in one battle (the pure
        // controller fed the runtime's samples; real seconds).
        var env = new Recorder { Fields = atD };
        var ctl = new LocalWeatherController(env);
        double now = 0;
        for (; now < 30; now += 2) ctl.Tick(now, atD);
        Check(env.Calls.Count == 0, "the camera on D in a battle started at D's weather: nothing changes");
        int firstSea = -1;
        for (; now < 120; now += 2) { ctl.Tick(now, atE); if (firstSea < 0 && env.Fields.SeaState == atE.SeaState) firstSea = (int)now - 30; }
        Check(env.Fields.Equals(atE) && firstSea >= 5 && firstSea <= 8, "jumping to E: E's weather applied " + firstSea + " s after the jump (" + string.Join(", ", env.Calls) + ")");
        env.Calls.Clear();
        int back = -1;
        for (; now < 200; now += 2) { ctl.Tick(now, atD); if (back < 0 && env.Fields.SeaState == atD.SeaState) back = (int)now - 120; }
        Check(env.Fields.Equals(atD) && back >= 5 && back <= 8, "and back to D: D's storm again after " + back + " s (" + string.Join(", ", env.Calls) + ")");
        env.Calls.Clear();
        for (int k = 0; k < 20; k++) { ctl.Tick(now, k % 2 == 0 ? atE : atD); now += 2; }
        Check(env.Calls.Count == 0, "jumping D/E every 2 s changes nothing (never confirmed)");
    }
}
