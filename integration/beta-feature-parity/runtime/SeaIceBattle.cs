using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Globalization;
using System.Linq.Expressions;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Threading;
using SeaPower;
using UnityEngine;
using Environment = SeaPower.Environment;

namespace Sest.RuntimeFixes;

// Seasonal sea ice inside Sea Power battles (SeaIce=1 in [Runtime], default
// on; SeaIceDiagnostics=1 logs, default off). The concentration at a geo
// position on the battle's calendar date is SeaIceModel's (the weather
// branch's seaice.py climatology), cached per 0.05-degree tile.
//
// Patches (each binds by name and signature against Sea Power 0.9.3
// aae79728; any failure logs one line and leaves that part out):
// - Environment.getFloeIce(GeoPosition) postfix: the native value is the
//   blue channel of a static, seasonless texture; it is replaced by the
//   model's concentration on the game's own scale (98 % = the native map's
//   largest ice value). getOceanNoise adds getFloeIce, so every sonar and
//   seeker at its own position, the Ocean Noise readout of the selected unit
//   and the sensor windows get the seasonal ice noise.
// - Compartments.UpdateWantedVelocityInKnots postfix: the wanted speed the
//   native telegraph/speed command produced is capped by the ice access of
//   the hull's class (ice-capability.json; empty, so "none"), against the
//   hull's own top telegraph speed (_telegraphVelocities or
//   _telegraphVelocitiesSubmerged, the arrays the method itself picks).
//   Vessel/Submarine.applyMainThrust read the capped value. A blocked hull
//   is never trapped: astern is always allowed at 0.4 of flank; ahead at 0.4
//   when the lightest of three unquantised samples 1, 3 and 6 nm along the
//   direction of travel is equal or lighter than the ice at the hull, else
//   at 0.1 of flank (steerage way, so the rudder can turn it out).
// - Submarine.OnFixedUpdate prefix: under heavy ice (60 %) a submerged
//   submarine's DesiredAltitude is held at or below the keel clearance
//   (30 m). That is the value OnFixedUpdate's depth branch (IL_0165-01eb)
//   and applyDepth's DepthKeeping copy into _targetAltitude every step,
//   before applyDepth's surfacing branches run, so a held submarine never
//   reaches them. The same prefix clears the player's manual height control
//   (ObjectBase.setPlayerHeightControl(false)): the pitch and ballast keys set
//   it, and applyDepth then ignores the target depth. Submarine.DepthKeeping
//   postfix: its shallow-water rise (bottom clearance, or 0 = surface when
//   that is above periscope depth) is clamped to the keel, or to the current
//   depth when the bottom forbids the keel. applyDepth postfix (backstop): a
//   held boat never rises above the deepest of its depth at the hold and the
//   keel, and upward ballast rates are zeroed there. setDepth prefix: orders
//   shallower than the keel are clamped (Surface, periscope depth, presets,
//   AI) and remembered; on release the remembered order is given back, so a
//   boat ordered to periscope depth goes there in open water.
//   SubmarineStates.Snorkelling.onFixedUpdate prefix: while held the state
//   does not try (and so cannot latch _depthReached with the snorkel down);
//   on release it tries again. needToEmergencySurface
//   postfix: no emergency blow under the pack (a design choice: a flooding
//   submarine under heavy ice must reach a lead), and
//   WasEmergencySurfacingInitiated is reset. SensorSystem.Enable and
//   SnorkelMastSystem.Enable prefixes: masts and the snorkel are not raised
//   while held; lowering (Disable) is never touched. Leads: the deterministic
//   lead field (SeaIceField) the ice sheet draws; a submarine whose footprint
//   is open water there may surface.
// Ship effects (SeaIceCarve=1, SeaIceBreakup=1, SeaIceSound=1, SeaIceBreakNoise=1,
// all default on, each failing closed with one log line): the speed postfix
// also records each surface ship's track through ice at or above the sheet's
// edge into the battle's IceCarve (channels 1.5 x beam wide that refreeze over
// SeaIceCarveMinutes, default 45 min of game time). Game time is the game's
// mission clock GameTime.missionElapsedTime, which follows time compression
// above 10x (Unity's Time.timeScale stops at GameTime._physicsTimeScaleCap,
// 10); on-screen message throttles and the sounds run on real time. In a
// channel the ice counts lighter for the speed rule (IceCarve.CapInChannel:
// the ice here, the lightest ice ahead and the reference all eased by the same
// openness; the ship's own last 2 minutes of track excluded). Submarines are
// NOT released under a channel: it is at most 120 m wide and brash-filled,
// while the hold needs the boat's whole footprint (45 m fore, aft and abeam)
// open in the lead field; the hold reads the lead field only. The breaking
// intensity per ship (IceBreakRule) drives the bow pieces and sounds
// (SeaIceEffects) and adds up to 8 dB of breaking noise to the ship's radiated
// noise: a postfix on SonarAcoustics.BroadbandTargetSLDB (the target source
// level Sonar.ProcessPassiveContact builds every passive contact from, on the
// sonar's worker tasks; the broadband bands derive from it) for the breaking
// ship's SensorData, so every passive sonar hears it louder; and, with the same
// dB, a Vessel.getNoise postfix, whose only live caller in 0.9.3 is
// SonarTickCache.BuildEntry (AswSimulation=1): the ship's level as an
// interferer, so a noisy icebreaker also masks contacts near it, as it would.
internal static class SeaIceBattle
{
    internal const string HarmonyId = "io.github.sest-hobby.sea-ice";
    internal static readonly SeaIceTileCache Cache = new SeaIceTileCache();
    internal static bool Diagnostics, NoiseOn, ShipsOn, SubsOn, BlockBlow;
    internal static double HeavyPercent = SubIceRule.DefaultHeavyPercent, KeelMeters = SubIceRule.DefaultKeelMeters;
    // The one ice edge (IceEdge): sheet, floes, channels, bow pieces, noise and speed all read it.
    internal static double EdgePercent => IceEdge.Percent;
    internal static double NoiseMaxOverride = double.NaN;
    internal static bool CarveOn, BreakupOn, SoundOn, BreakNoiseOn;
    internal static double CarveMinutes = IceCarve.DefaultRefreezeMinutes;
    // The battle's carved channels (main thread; the sheet's builders read immutable snapshots).
    internal static IceCarve Carve = new IceCarve();
    // Ships breaking ice now, by instance id (main thread): the effects driver reads them.
    internal sealed class Breaker
    {
        internal ObjectBase Ob;
        internal double Intensity, SpeedKn, Percent, BeamM = 15, LengthM = 100;
        internal double Seen;            // game seconds
        internal object Sensor;          // the ship's SensorData (the noise key)
        internal NoiseEntry Noise;
    }
    // The breaking noise per SensorData, read by the sonar's worker tasks: written on the main thread only.
    internal sealed class NoiseEntry { internal volatile float Db; }
    private sealed class RefEq : IEqualityComparer<object>
    {
        bool IEqualityComparer<object>.Equals(object a, object b) => ReferenceEquals(a, b);
        int IEqualityComparer<object>.GetHashCode(object o) => RuntimeHelpers.GetHashCode(o);
    }
    private static readonly ConcurrentDictionary<object, NoiseEntry> noiseBySensor = new ConcurrentDictionary<object, NoiseEntry>(new RefEq());
    private static double nextNoiseSweep = double.NegativeInfinity;
    internal static readonly Dictionary<int, Breaker> Breakers = new Dictionary<int, Breaker>();
    internal static int ChannelHelps, CarvePoints, NoiseAdds, InterfererAdds;
    private static double nextCarveAdvance = double.NegativeInfinity, nextCarveAdvanceReal = double.NegativeInfinity;
    // The game's clocks (GameTime, bound at install): mission seconds, time compression, game seconds per frame.
    private static Func<double> missionElapsed;
    private static Func<float> timeCompression, gameDeltaTime;
    internal static string ClockState = "not bound";
    internal static float KeelUnity = SubIceRule.MetersToUnity(SubIceRule.DefaultKeelMeters);
    private static FieldInfo envInstance, envMap, envMapReady;
    private static Func<ObjectBase, float> desiredAltitude;
    private static Action<ObjectBase, float> setDesiredAltitude;
    private static Action<Compartments, float> setWanted;
    private static Action<Submarine, bool> setBlowInitiated;
    private static Action<Submarine> retractMasts;
    private static FieldInfo playerHeightControl;
    private static FieldInfo mainGameViewModel;
    private static MethodInfo raiseAlert;

    private sealed class Battle
    {
        internal Environment Env;
        internal IceFrame Frame;
        internal bool HasFrame;
        internal float NoiseScale = float.NaN;
        internal uint Seed;
        internal bool HasSeed;
        internal string NoiseSource = "";
    }
    private static volatile Battle battle;

    private sealed class Hull
    {
        internal readonly IceSpeedState Speed = new IceSpeedState();
        internal double NextAhead, Ahead = double.NaN, HereRaw = double.NaN;
        internal readonly double[] Samples = new double[IceSpeedState.AheadNm.Length];
        internal double NextMark = -1e9, NextWake = -1e9;   // game seconds
        internal double Open;
        internal int LastSign;
        internal int Capability = -1;
        internal float LastMessage = -1e9f;                  // real seconds
        internal bool Capped;
    }
    private static readonly ConditionalWeakTable<Compartments, Hull> hulls = new ConditionalWeakTable<Compartments, Hull>();

    private sealed class Hold
    {
        internal double Until = -1e9;      // game seconds
        internal float LastMessage = -1e9f; // real seconds
        internal bool Held;
        internal double Percent;
        internal bool Lead;
        internal bool Applied;              // the fixed-step prefix has applied this hold
        internal bool HasOrder;             // the order the clamp replaced, given back on release
        internal float Order;
        internal float Ceiling = float.NaN; // highest y while held (applyDepth backstop)
        internal bool ManualTold, SnorkelSuppressed;
    }
    private static readonly ConditionalWeakTable<Submarine, Hold> holds = new ConditionalWeakTable<Submarine, Hold>();

    // Diagnostics counters (main thread).
    internal static int SpeedCaps, SubClamps, OrderClamps, BlowsRefused, MastsRefused, FloeCalls, TargetClamps, RisesStopped, ManualOverrides, OrdersRestored, SnorkelHolds;
    // Surface units (ships, boats surfaced in a lead) for the sheet: no ice top above their waterline.
    internal static bool MarkUnits;
    private struct SurfaceMark { internal double Lat, Lon, Seen; internal float Y; }
    private static readonly Dictionary<int, SurfaceMark> surface = new Dictionary<int, SurfaceMark>();
    private static float nextReport;
    private static bool floeLogged;

    internal static void Install(Assembly game, string[] lines)
    {
        Diagnostics = Policy.TextOption(lines, "SeaIceDiagnostics", "0") == "1";
        NoiseOn = Policy.TextOption(lines, "SeaIceNoise", "1") == "1";
        ShipsOn = Policy.TextOption(lines, "SeaIceShips", "1") == "1";
        SubsOn = Policy.TextOption(lines, "SeaIceSubmarines", "1") == "1";
        BlockBlow = Policy.TextOption(lines, "SeaIceBlockEmergencyBlow", "1") == "1";
        HeavyPercent = Number(lines, "SeaIceSubHeavyPercent", SubIceRule.DefaultHeavyPercent, 15, 98);
        KeelMeters = Number(lines, "SeaIceKeelMeters", SubIceRule.DefaultKeelMeters, 10, 120);
        string edgeLine = IceEdge.Configure(Policy.TextOption(lines, "SeaIceEdgePercent", ""));
        if (edgeLine != null) Api.Log("sea ice: " + edgeLine);
        // heavy ice under the edge would hold a boat under ice that is not drawn
        if (HeavyPercent < IceEdge.Percent) { Api.Log("sea ice: SeaIceSubHeavyPercent " + HeavyPercent.ToString("0", CultureInfo.InvariantCulture) + " is under the ice edge; using " + IceEdge.Percent.ToString("0.#", CultureInfo.InvariantCulture) + " %"); HeavyPercent = IceEdge.Percent; }
        KeelUnity = SubIceRule.MetersToUnity(KeelMeters);
        NoiseMaxOverride = Number(lines, "SeaIceNoiseMax", double.NaN, 0, 25.5);
        CarveOn = Policy.TextOption(lines, "SeaIceCarve", "1") == "1";
        BreakupOn = Policy.TextOption(lines, "SeaIceBreakup", "1") == "1";
        SoundOn = Policy.TextOption(lines, "SeaIceSound", "1") == "1";
        BreakNoiseOn = Policy.TextOption(lines, "SeaIceBreakNoise", "1") == "1";
        CarveMinutes = Number(lines, "SeaIceCarveMinutes", IceCarve.DefaultRefreezeMinutes, IceCarve.MinRefreezeMinutes, IceCarve.MaxRefreezeMinutes);
        Carve = new IceCarve(CarveMinutes);
        BindClock();
        // The model and its data first: a broken table installs nothing.
        double check = SeaIceModel.Concentration(74.0, 36.0, new DateTime(2029, 3, 10, 12, 0, 0, DateTimeKind.Utc));
        if (!(Math.Abs(check - 62.28) < 0.05)) throw new InvalidOperationException("sea-ice table check failed: " + check.ToString("0.00", CultureInfo.InvariantCulture));
        InstallFloes(lines); // after the table check (a broken table installs nothing) and after SeaIceSubHeavyPercent
        envInstance = typeof(Singleton<Environment>).GetField("_instance", BindingFlags.Static | BindingFlags.NonPublic);
        if (envInstance == null) throw new MissingFieldException("Singleton<Environment>._instance");
        envMap = typeof(Environment).GetField("_environmentMap", Api.All);
        envMapReady = typeof(Environment).GetField("_isEnvironmentMapInitialized", Api.All);
        mainGameViewModel = typeof(Globals).GetField("_mainGameViewModel", Api.All);
        raiseAlert = mainGameViewModel?.FieldType.GetMethod("RaiseAlert", Api.All, null, new[] { typeof(ObjectBase), typeof(string) }, null);
        var parts = new List<string>();
        if (NoiseOn) Part("ocean noise", parts, () => Api.Postfix(Api.Method(typeof(Environment), "getFloeIce", typeof(float), typeof(GeoPosition)), typeof(SeaIceBattle), nameof(FloeIcePostfix), HarmonyId + ".noise"));
        if (ShipsOn) Part("ship speed", parts, InstallShips);
        if (!parts.Contains("ship speed") && (CarveOn || BreakupOn || SoundOn || BreakNoiseOn)) { CarveOn = BreakupOn = SoundOn = BreakNoiseOn = false; Api.Log("sea ice: channels, bow pieces, breaking sounds and breaking noise off (they ride the ship speed postfix: SeaIceShips=0 or not installed)"); }
        if (missionElapsed == null && (CarveOn || BreakupOn || SoundOn || BreakNoiseOn)) { CarveOn = BreakupOn = SoundOn = BreakNoiseOn = false; Api.Log("sea ice: channels, bow pieces, breaking sounds and breaking noise off: the game clock is not bound (" + ClockState + ")"); }
        // the passive target level first: without it the interferer part alone would only mask other contacts
        if (BreakNoiseOn) Part("breaking noise", parts, () => Api.Postfix(TargetNoiseMethod(), typeof(SeaIceBattle), nameof(TargetNoisePostfix), HarmonyId + ".break-noise"));
        if (!parts.Contains("breaking noise")) BreakNoiseOn = false;
        if (BreakNoiseOn) Part("breaking noise as an interferer", parts, () => Api.Postfix(Api.Method(typeof(Vessel), "getNoise", typeof(float)), typeof(SeaIceBattle), nameof(NoisePostfix), HarmonyId + ".break-noise-interferer"));
        if (SubsOn) Part("submarines", parts, InstallSubs);
        Api.Log("sea ice installed (" + string.Join(", ", parts) + "; channels " + (CarveOn ? "on, refreeze " + CarveMinutes.ToString("0", CultureInfo.InvariantCulture) + " min" : "off") + ", bow pieces " + (BreakupOn ? "on" : "off") + ", breaking sounds " + (SoundOn ? "on" : "off") + "): seasonal concentration from the weather branch's seaice.py climatology (NSIDC monthly extents, edge shape fitted by eye), baseline " + SeaIceData.Baseline +
            "; heavy ice " + HeavyPercent.ToString("0", CultureInfo.InvariantCulture) + " %, keel clearance " + KeelMeters.ToString("0", CultureInfo.InvariantCulture) + " m, sheet edge " + EdgePercent.ToString("0.#", CultureInfo.InvariantCulture) + " % (the one ice edge: drawn, slowing, effects and campaign map alike)");
    }

    // The drift-ice floe field (SeaIceFloes; the field the sheet draws and IsIce/FootprintOpen read):
    // SeaIceFloeField=1 (default on), SeaIceFloeFullPercent (44), SeaIceFloePackPercent (60, capped at
    // SeaIceSubHeavyPercent so the submarine rule reads the pack field as before), SeaIceFloePushM (60).
    // The calibration is warmed on the thread pool; if it fails, floes switch off (the pack field
    // everywhere, as before) with one log line.
    private static void InstallFloes(string[] lines)
    {
        bool on = Policy.TextOption(lines, "SeaIceFloeField", "1") == "1";
        string note = SeaIceFloes.Configure(on, Number(lines, "SeaIceFloeFullPercent", double.NaN, -1e9, 1e9), Number(lines, "SeaIceFloePackPercent", double.NaN, -1e9, 1e9), Number(lines, "SeaIceFloePushM", double.NaN, -1e9, 1e9), HeavyPercent);
        if (!SeaIceFloes.On) { Api.Log("sea ice floes: off (SeaIceFloeField=0): the pack field at every concentration"); return; }
        Api.Log("sea ice floes: separate floes up to " + SeaIceFloes.FullPercent.ToString("0", CultureInfo.InvariantCulture) + " %, blended into the pack field by " + SeaIceFloes.PackPercent.ToString("0", CultureInfo.InvariantCulture) + " %; floes up to " + SeaIceFloes.PushM.ToString("0", CultureInfo.InvariantCulture) + " m pushed out of channels" + (note.Length > 0 ? ";" + note : ""));
        ThreadPool.QueueUserWorkItem(_ =>
        {
            try
            {
                var sw = System.Diagnostics.Stopwatch.StartNew();
                if (SeaIceFloes.Warm()) { if (Diagnostics) Api.Log("sea ice floes: calibrated in " + sw.ElapsedMilliseconds + " ms"); }
                else Api.Log("sea ice floes: calibration failed (" + SeaIceFloes.FailedNote + "); the pack field at every concentration");
            }
            catch (Exception e) { SeaIceFloes.On = false; Api.LogFailure("sea ice floes: off (the pack field at every concentration)", e); } // never let a pool thread throw
        });
    }

    private static double Number(string[] lines, string option, double fallback, double min, double max)
    {
        string text = Policy.TextOption(lines, option, "");
        return double.TryParse(text, NumberStyles.Float, CultureInfo.InvariantCulture, out double v) && v >= min && v <= max ? v : fallback;
    }

    private static void Part(string name, List<string> parts, Action install)
    {
        try { install(); parts.Add(name); }
        catch (Exception e) { Api.LogFailure("sea ice: " + name + " not installed; native behaviour kept", e); }
    }

    // SonarAcoustics.BroadbandTargetSLDB(SensorData sd, absSpeedKts, additionalNoise, cavitationIntensity,
    // aspectNoiseReductionDB, activePingNoiseSL, listenBand, cavitationOnsetKts): the target's broadband
    // source level, dB.
    internal static MethodInfo TargetNoiseMethod() => Api.Method(typeof(SonarAcoustics), "BroadbandTargetSLDB", typeof(float), typeof(SensorData), typeof(float), typeof(float), typeof(float), typeof(float), typeof(float), typeof(SonarParameters.SonarFrequency), typeof(float));

    // GameTime.missionElapsedTime (double, game seconds), TimeCompression and deltaTime (game seconds
    // this frame), as delegates. Missing: the ship effects stay off (Install), the submarine hold and
    // the surface marks fall back to Unity's Time.time.
    private static void BindClock()
    {
        try
        {
            var gt = typeof(GameTime);
            missionElapsed = (Func<double>)Delegate.CreateDelegate(typeof(Func<double>), Api.Method(gt, "get_missionElapsedTime", typeof(double)));
            timeCompression = (Func<float>)Delegate.CreateDelegate(typeof(Func<float>), Api.Method(gt, "get_TimeCompression", typeof(float)));
            gameDeltaTime = (Func<float>)Delegate.CreateDelegate(typeof(Func<float>), Api.Method(gt, "get_deltaTime", typeof(float)));
            ClockState = "GameTime.missionElapsedTime";
        }
        catch (Exception e) { missionElapsed = null; timeCompression = gameDeltaTime = null; ClockState = "unavailable (" + e.Message + ")"; Api.Log("sea ice: game clock " + ClockState); }
    }

    // Game seconds (the mission clock).
    internal static double Now() => missionElapsed != null ? missionElapsed() : Time.time;
    // Game seconds one frame spans now.
    internal static double FrameS() => gameDeltaTime != null ? gameDeltaTime() : Time.deltaTime;
    // The game's time compression (1 = real time).
    internal static double Compression() => timeCompression != null ? timeCompression() : Time.timeScale;

    private static void InstallShips()
    {
        var set = typeof(Compartments).GetProperty("WantedVelocityInKnots", Api.All)?.GetSetMethod(true);
        if (set == null) throw new MissingMethodException("Compartments.set_WantedVelocityInKnots");
        setWanted = (Action<Compartments, float>)Delegate.CreateDelegate(typeof(Action<Compartments, float>), set);
        foreach (var f in new[] { "_telegraphVelocities", "_telegraphVelocitiesSubmerged" })
            if (typeof(Compartments).GetField(f, Api.All)?.FieldType != typeof(float[])) throw new MissingFieldException("Compartments." + f);
        if (typeof(Compartments).GetField("_submarine", Api.All)?.FieldType != typeof(Submarine)) throw new MissingFieldException("Compartments._submarine");
        Api.Postfix(Api.Method(typeof(Compartments), "UpdateWantedVelocityInKnots", typeof(void)), typeof(SeaIceBattle), nameof(SpeedPostfix), HarmonyId + ".ships");
    }

    private static void InstallSubs()
    {
        var da = typeof(ObjectBase).GetProperty("DesiredAltitude", Api.All);
        var value = da?.PropertyType.GetProperty("Value");
        if (value == null || value.PropertyType != typeof(float)) throw new MissingMemberException("ObjectBase.DesiredAltitude.Value : float");
        var p = Expression.Parameter(typeof(ObjectBase), "o");
        var v = Expression.Parameter(typeof(float), "v");
        desiredAltitude = Expression.Lambda<Func<ObjectBase, float>>(Expression.Property(Expression.Property(p, da), value), p).Compile();
        setDesiredAltitude = Expression.Lambda<Action<ObjectBase, float>>(Expression.Assign(Expression.Property(Expression.Property(p, da), value), v), p, v).Compile();
        var blow = typeof(Submarine).GetProperty("WasEmergencySurfacingInitiated", Api.All)?.GetSetMethod(true);
        if (blow == null) throw new MissingMethodException("Submarine.set_WasEmergencySurfacingInitiated");
        setBlowInitiated = (Action<Submarine, bool>)Delegate.CreateDelegate(typeof(Action<Submarine, bool>), blow);
        retractMasts = (Action<Submarine>)Delegate.CreateDelegate(typeof(Action<Submarine>), Api.Method(typeof(Submarine), "retractMasts", typeof(void)));
        playerHeightControl = typeof(ObjectBase).GetField("_playerHeightControl", Api.All);
        if (playerHeightControl == null || playerHeightControl.FieldType != typeof(bool)) throw new MissingFieldException("ObjectBase._playerHeightControl : bool");
        Api.Method(typeof(ObjectBase), "setPlayerHeightControl", typeof(void), typeof(bool));
        foreach (var f in new[] { "_targetAltitude", "_currentDepthChangeUsingTanks", "_targetBallastDepthChangeRate" })
            if (typeof(Submarine).GetField(f, Api.All)?.FieldType != typeof(float)) throw new MissingFieldException("Submarine." + f + " : float");
        if (typeof(Submarine).GetField("_divingInProgress", Api.All)?.FieldType != typeof(bool)) throw new MissingFieldException("Submarine._divingInProgress : bool");
        var snorkelState = typeof(SubmarineStates.Snorkelling);
        if (snorkelState.GetField("_depthReached", Api.All)?.FieldType != typeof(bool) || snorkelState.GetField("_submarine", Api.All)?.FieldType != typeof(Submarine)) throw new MissingFieldException("SubmarineStates.Snorkelling._depthReached / _submarine");
        var depthKeeping = Api.Method(typeof(Submarine), "DepthKeeping", typeof(void));
        var applyDepth = Api.Method(typeof(Submarine), "applyDepth", typeof(void));
        var snorkelFixed = Api.Method(snorkelState, "onFixedUpdate", typeof(void));
        var fixedUpdate = Api.Method(typeof(Submarine), "OnFixedUpdate", typeof(void));
        var setDepth = Api.Method(typeof(Submarine), "setDepth", typeof(void), typeof(float));
        var needBlow = Api.Method(typeof(Submarine), "needToEmergencySurface", typeof(bool));
        var sensorEnable = Api.Method(typeof(SensorSystem), "Enable", typeof(void), typeof(bool), typeof(bool));
        var snorkelEnable = Api.Method(typeof(SnorkelMastSystem), "Enable", typeof(void), typeof(bool));
        Api.Hooks(fixedUpdate, typeof(SeaIceBattle), nameof(SubFixedPrefix), null, HarmonyId + ".sub-depth");
        Api.Hooks(setDepth, typeof(SeaIceBattle), nameof(SetDepthPrefix), null, HarmonyId + ".sub-order");
        Api.Postfix(depthKeeping, typeof(SeaIceBattle), nameof(DepthKeepingPostfix), HarmonyId + ".sub-keeping");
        Api.Postfix(applyDepth, typeof(SeaIceBattle), nameof(ApplyDepthPostfix), HarmonyId + ".sub-apply");
        Api.Hooks(snorkelFixed, typeof(SeaIceBattle), nameof(SnorkelStatePrefix), null, HarmonyId + ".sub-snorkel-state");
        if (BlockBlow) Api.Postfix(needBlow, typeof(SeaIceBattle), nameof(BlowPostfix), HarmonyId + ".sub-blow");
        Api.Hooks(sensorEnable, typeof(SeaIceBattle), nameof(MastPrefix), null, HarmonyId + ".sub-masts");
        Api.Hooks(snorkelEnable, typeof(SeaIceBattle), nameof(SnorkelPrefix), null, HarmonyId + ".sub-snorkel");
    }

    // ---- battle state ------------------------------------------------------------------------

    // The live Environment, without Singleton.Instance (which may create one outside a battle).
    internal static Environment Env()
    {
        var e = envInstance?.GetValue(null) as Environment;
        return e != null ? e : null; // UnityEngine.Object null check
    }

    private static Battle Current(Environment env)
    {
        var b = battle;
        if (b != null && ReferenceEquals(b.Env, env)) return b;
        b = new Battle { Env = env };
        battle = b;
        Carve = new IceCarve(CarveMinutes);
        Breakers.Clear();
        noiseBySensor.Clear();
        return b;
    }

    // The battle's calendar date: Environment.get_DateTime (the mission clock,
    // Year/Month/Day/Hour/Minutes/Seconds). Dynamic Campaign Mod writes
    // [Environment] Date= and Time= with ConvertTimeToLocal=False, so it is UTC there.
    internal static DateTime Date(Environment env)
    {
        try { return env.DateTime; }
        catch { return new DateTime(2029, 1, 1); }
    }

    // The battle frame: anchored at the first position asked about in this battle.
    internal static IceFrame Frame(Environment env, double lat, double lon)
    {
        var b = Current(env);
        if (!b.HasFrame) { b.Frame = IceFrame.Around(lat, lon); b.HasFrame = true; if (Diagnostics) Api.Log("sea ice: battle frame at " + b.Frame.Lat0.ToString("0.0", CultureInfo.InvariantCulture) + ", " + b.Frame.Lon0.ToString("0.0", CultureInfo.InvariantCulture) + "; date " + Date(env).ToString("yyyy-MM-dd HH:mm", CultureInfo.InvariantCulture)); }
        return b.Frame;
    }

    internal static double Percent(Environment env, GeoPosition g) => Cache.Percent(g._latitude, g._longitude, Date(env));

    // Is the point under ice in the lead field? (the field the sheet draws)
    internal static bool LeadAt(Environment env, GeoPosition g, double percent)
    {
        var frame = Frame(env, g._latitude, g._longitude);
        frame.ToKm(g._latitude, g._longitude, out double e, out double n);
        return SeaIceField.FootprintOpen(e, n, SeaIceField.DrawnFraction(percent, EdgePercent), Seed(env), SubIceRule.FootprintMeters);
    }

    // The lead pattern's seed: the battle's first calendar date, so leads do not
    // jump at midnight during a battle (the concentration still follows the date).
    internal static uint Seed(Environment env)
    {
        var b = Current(env);
        if (!b.HasSeed) { b.Seed = SeaIceField.SeedOf(SeaIceTileCache.DateKeyOf(Date(env))); b.HasSeed = true; }
        return b.Seed;
    }

    // ---- (a) ambient ocean noise -------------------------------------------------------------

    internal static void FloeIcePostfix(Environment __instance, GeoPosition __0, ref float __result)
    {
        if (!NoiseOn) return;
        try
        {
            var b = Current(__instance);
            if (float.IsNaN(b.NoiseScale)) Calibrate(b, __instance);
            if (float.IsNaN(b.NoiseScale)) return; // the native map is not read yet: native value this call
            float native = __result;
            double c = Cache.Percent(__0._latitude, __0._longitude, Date(__instance));
            if (IceEdge.Below(c)) c = 0; // no ice under the edge (IceEdge): none drawn, none heard
            __result = (float)(b.NoiseScale * c / SeaIceModel.MaxPercent);
            FloeCalls++;
            if (Diagnostics && !floeLogged) { floeLogged = true; Api.Log("sea ice noise: first getFloeIce at " + Geo(__0) + ": native " + native.ToString("0.00", CultureInfo.InvariantCulture) + ", model " + c.ToString("0.0", CultureInfo.InvariantCulture) + " % -> " + __result.ToString("0.00", CultureInfo.InvariantCulture) + " (" + b.NoiseSource + ")"); }
        }
        catch (Exception e) { NoiseOn = false; Fail("ocean noise", e); }
    }

    // 98 % maps to the native map's largest floe-ice value (blue / 10), so the
    // seasonal ice has the game's own loudness; 0 % adds nothing.
    private static void Calibrate(Battle b, Environment env)
    {
        if (!double.IsNaN(NoiseMaxOverride)) { b.NoiseScale = (float)NoiseMaxOverride; b.NoiseSource = "SeaIceNoiseMax=" + NoiseMaxOverride.ToString("0.0", CultureInfo.InvariantCulture); if (Diagnostics) Api.Log("sea ice noise scale: " + b.NoiseSource); return; }
        b.NoiseScale = 6f;
        b.NoiseSource = "no native ice in the environment map; fallback 6.0 at 98 % (set SeaIceNoiseMax to change)";
        try
        {
            if (envMapReady != null && !(bool)envMapReady.GetValue(env)) { b.NoiseScale = float.NaN; return; }
            if (envMap?.GetValue(env) is Color32[] map && map.Length > 0)
            {
                int max = 0;
                for (int i = 0; i < map.Length; i++) if (map[i].b > max) max = map[i].b;
                if (max > 0) { b.NoiseScale = max / 10f; b.NoiseSource = "native environment map maximum blue " + max + " -> " + b.NoiseScale.ToString("0.0", CultureInfo.InvariantCulture) + " at 98 %"; }
            }
        }
        catch (Exception e) { b.NoiseSource += " (" + e.GetType().Name + ")"; }
        if (Diagnostics) Api.Log("sea ice noise scale: " + b.NoiseSource);
    }

    // ---- (b) ship speed ----------------------------------------------------------------------

    internal static void SpeedPostfix(Compartments __instance, float[] ____telegraphVelocities, float[] ____telegraphVelocitiesSubmerged, Submarine ____submarine)
    {
        if (!ShipsOn) return;
        try
        {
            var ob = __instance._baseObject;
            if (ob == null || __instance._isSinking || __instance._immobile) return;
            bool submerged = ____submarine != null && ____submarine.isSubmerged();
            if (submerged) return; // submerged boats pass under the pack
            float wanted = __instance.WantedVelocityInKnots;
            if (Math.Abs(wanted) < 0.01f)
            {
                if (MarkUnits) { var rest = hulls.GetOrCreateValue(__instance); double t = Now(); if (t >= rest.NextMark || t < rest.NextMark - 2) { rest.NextMark = t + 1; MarkSurface(ob, t); } }
                SweepNoise();
                return;
            }
            var env = Env();
            if (env == null) return;
            var g = ob._geoPosition;
            var date = Date(env);
            double c = Cache.Percent(g._latitude, g._longitude, date);
            var hull = hulls.GetOrCreateValue(__instance);
            double now = Now();
            if (MarkUnits && (now >= hull.NextMark || now < hull.NextMark - 2)) { hull.NextMark = now + 1; MarkSurface(ob, now); }
            SweepNoise();
            // carved channels: record this ship's track, and ice in another ship's channel counts lighter
            double open = (CarveOn || BreakupOn || SoundOn || BreakNoiseOn) ? Wake(ob, env, g, c, now, hull) : 0;
            double cRaw = c;
            if (open > 0) { c = IceCarve.EffectivePercent(c, open); ChannelHelps++; }
            if (c < 1 && hull.Speed.State == IceAccess.Open) return;
            if (hull.Capability < 0) hull.Capability = IceRules.CapabilityOf(ob._obp != null ? ob._obp._objectIniName : null);
            int sign = wanted < 0 ? -1 : 1;
            if (now >= hull.NextAhead || now < hull.NextAhead - 2 || sign != hull.LastSign)
            {
                hull.LastSign = sign;
                hull.NextAhead = now + 1.0;
                float heading = Utils.UnityYawToTrueHeading(ob.transform.eulerAngles.y, g);
                if (wanted < 0) heading += 180f;
                // unquantised model, beyond one 0.05-degree tile: the tile cache would give "here" back
                hull.HereRaw = SeaIceModel.Concentration(g._latitude, g._longitude, date);
                for (int i = 0; i < IceSpeedState.AheadNm.Length; i++)
                {
                    var ahead = g.GeoOffsetByDistanceOnHeading(IceSpeedState.AheadNm[i], heading);
                    hull.Samples[i] = SeaIceModel.Concentration(ahead._latitude, ahead._longitude, date);
                }
                hull.Ahead = IceSpeedState.Lightest(hull.Samples);
            }
            float flank = 0;
            var arr = ____telegraphVelocities;
            if (arr != null) for (int i = 0; i < arr.Length; i++) flank = Math.Max(flank, Math.Abs(arr[i]));
            // in a channel the ice here, the lightest ice ahead and the reference are eased alike (escape test like with like)
            float capped = IceCarve.CapInChannel(hull.Speed, wanted, flank, cRaw, hull.Ahead, hull.Capability, hull.HereRaw, open);
            bool binding = capped != wanted;
            if (binding)
            {
                setWanted(__instance, capped);
                SpeedCaps++;
                float real = Time.realtimeSinceStartup;
                if (ob.IsPlayerObject && (real - hull.LastMessage > 30f || real < hull.LastMessage))
                {
                    hull.LastMessage = real;
                    Alert(ob, hull.Speed.SteerageOnly ? "Held by pack ice (" + Pct(c) + "): heavier ice ahead, steerage way only (" + capped.ToString("0", CultureInfo.InvariantCulture) + " kn); back out or turn toward open water." :
                        "In ice (" + Pct(c) + ", " + hull.Speed.State.ToString().ToLowerInvariant() + "): speed limited to " + Math.Abs(capped).ToString("0", CultureInfo.InvariantCulture) + " kn" + (hull.Speed.Escaping ? " (working out of the ice)" : "") + ".");
                }
            }
            if (Diagnostics && binding != hull.Capped)
                Api.Log("sea ice speed: " + ob.name + " at " + Geo(g) + " ice " + Pct(c) + (open > 0 ? " (channel: " + Pct(cRaw) + " x (1 - " + IceCarve.Relief.ToString("0.0", CultureInfo.InvariantCulture) + " x openness " + open.ToString("0.00", CultureInfo.InvariantCulture) + "))" : "") + " (model " + Pct(hull.HereRaw) + ") lightest ahead " + Pct(hull.Ahead) + " class " + IceRules.Capabilities[hull.Capability] + " state " + hull.Speed.State + (binding ? " capped " + wanted.ToString("0.0", CultureInfo.InvariantCulture) + " -> " + capped.ToString("0.0", CultureInfo.InvariantCulture) + " kn (flank " + flank.ToString("0.0", CultureInfo.InvariantCulture) + (hull.Speed.Escaping ? ", escaping" : hull.Speed.SteerageOnly ? ", steerage way" : "") + ")" : " released"));
            hull.Capped = binding;
        }
        catch (Exception e) { ShipsOn = false; Fail("ship speed", e); }
    }

    // The ship's wake in the ice, at most five times a second of game time (and once a frame): its
    // carve track, its breaking intensity for the effects and the noise, and the openness of another
    // ship's channel under it.
    private static double Wake(ObjectBase ob, Environment env, GeoPosition g, double c, double now, Hull hull)
    {
        if (now < hull.NextWake && now >= hull.NextWake - 1) return hull.Open;
        hull.NextWake = now + 0.2;
        try
        {
            double frameS = FrameS();
            int id = ob.GetInstanceID();
            var frame = Frame(env, g._latitude, g._longitude);
            frame.ToKm(g._latitude, g._longitude, out double e, out double n);
            double kn = ob.getVelocityInKnots();
            if (!Breakers.TryGetValue(id, out var br))
            {
                br = new Breaker { Ob = ob };
                var d = ob._obp != null ? ob._obp._dimensions : Vector3.zero;
                double x = Math.Abs(d.x) * 67.2000656, z = Math.Abs(d.z) * 67.2000656; // Unity units -> metres (the game's own factor)
                if (x > 0 && z > 0) { br.BeamM = Math.Max(4, Math.Min(80, Math.Min(x, z))); br.LengthM = Math.Max(10, Math.Min(400, Math.Max(x, z))); }
                if (Breakers.Count > 512) PruneBreakers(now, frameS);
                Breakers[id] = br;
            }
            hull.Open = 0;
            if (CarveOn)
            {
                // refreeze once a second of game time (the sheet's driver does too; this keeps the speed rule right without it)
                AdvanceCarve(now);
                if (c >= EdgePercent && Math.Abs(kn) >= IceBreakRule.MinSpeedKn) { int before = Carve.Added; Carve.Record(id, e, n, now, br.BeamM, frameS); if (Carve.Added != before) CarvePoints++; }
                else Carve.Break(id);
                // the last published snapshot (rebuilt at most every IceCarve.MinPublishS of real time)
                Carve.Publish(Time.realtimeSinceStartup);
                hull.Open = Carve.Published.OpennessAt(e, n, id, now - IceClock.Recent(IceCarve.OwnGraceS, frameS));
            }
            br.SpeedKn = kn;
            br.Percent = IceCarve.EffectivePercent(c, hull.Open);
            br.Intensity = IceBreakRule.Intensity(kn, br.Percent, EdgePercent);
            br.Seen = now;
            SetNoise(br, ob, BreakNoiseOn ? (float)IceBreakRule.Noise(br.Intensity) : 0f);
            return hull.Open;
        }
        catch (Exception x)
        {
            // everything this feeds goes off: the effects driver stops the sounds and hides the pieces on
            // its next frame (SeaIceEffects.Tick), the noise postfixes are gated by BreakNoiseOn
            CarveOn = BreakupOn = SoundOn = BreakNoiseOn = false;
            foreach (var b in noiseBySensor.Values) b.Db = 0;
            Fail("channels and breaking effects", x);
            return 0;
        }
    }

    // Refreeze once a second of game time, and at most five times a second of real time.
    internal static void AdvanceCarve(double now)
    {
        double real = Time.realtimeSinceStartup;
        if (!(now >= nextCarveAdvance || now < nextCarveAdvance - 2)) return;
        if (real < nextCarveAdvanceReal && real >= nextCarveAdvanceReal - 1) return;
        nextCarveAdvance = now + 1;
        nextCarveAdvanceReal = real + 0.2;
        Carve.Advance(now);
    }

    private static void SetNoise(Breaker br, ObjectBase ob, float db)
    {
        var sd = ob._sensorData;
        if (!ReferenceEquals(sd, br.Sensor))
        {
            if (br.Sensor != null) noiseBySensor.TryRemove(br.Sensor, out _);
            br.Sensor = sd;
            br.Noise = null;
        }
        if (sd == null) return;
        if (br.Noise == null) br.Noise = noiseBySensor.GetOrAdd(sd, _ => new NoiseEntry());
        br.Noise.Db = db;
    }

    // Main thread, at most four times a second of real time: ships not seen breaking lately add no noise.
    internal static void SweepNoise()
    {
        float real = Time.realtimeSinceStartup;
        if (real < nextNoiseSweep && real >= nextNoiseSweep - 1) return;
        nextNoiseSweep = real + 0.25;
        if (Breakers.Count == 0) return;
        double now = Now(), frameS = FrameS();
        foreach (var b in Breakers.Values)
            if (b.Noise != null && b.Noise.Db != 0 && (b.Ob == null || !IceClock.Fresh(now, b.Seen, 1, frameS))) b.Noise.Db = 0;
    }

    private static void PruneBreakers(double now, double frameS)
    {
        var old = new List<int>();
        foreach (var kv in Breakers) if (!IceClock.Fresh(now, kv.Value.Seen, 10, frameS) || kv.Value.Ob == null) old.Add(kv.Key);
        foreach (var k in old) { var b = Breakers[k]; if (b.Sensor != null) noiseBySensor.TryRemove(b.Sensor, out _); Breakers.Remove(k); }
    }

    // Is this breaker's state current (seen in the last second of game time, or the last three frames)?
    internal static bool IsCurrent(Breaker b, double now, double frameS) => b != null && b.Ob != null && IceClock.Fresh(now, b.Seen, 1, frameS);

    // The breaking noise of a target's SensorData, dB (0 for any other unit). Any thread.
    private static float NoiseOf(SensorData sd) => sd != null && noiseBySensor.TryGetValue(sd, out var n) ? n.Db : 0f;

    // SonarAcoustics.BroadbandTargetSLDB postfix (the sonar's worker tasks): the breaking ship's radiated
    // broadband level, from which every passive contact on it is built, is louder by the breaking noise.
    internal static void TargetNoisePostfix(SensorData __0, ref float __result)
    {
        if (!BreakNoiseOn) return;
        try
        {
            float db = NoiseOf(__0);
            if (!(db > 0)) return;
            __result += db;
            Interlocked.Increment(ref NoiseAdds);
        }
        catch (Exception e) { BreakNoiseOn = false; Fail("breaking noise", e); }
    }

    // Vessel.getNoise postfix: the same dB on the ship's level as an interferer (AswSimulation=1 masking).
    internal static void NoisePostfix(Vessel __instance, ref float __result)
    {
        if (!BreakNoiseOn) return;
        try
        {
            float db = __instance != null ? NoiseOf(__instance._sensorData) : 0f;
            if (!(db > 0)) return;
            __result += db;
            Interlocked.Increment(ref InterfererAdds);
        }
        catch (Exception e) { BreakNoiseOn = false; Fail("breaking noise", e); }
    }

    private static void MarkSurface(ObjectBase ob, double now)
    {
        var g = ob._geoPosition;
        surface[ob.GetInstanceID()] = new SurfaceMark { Lat = g._latitude, Lon = g._longitude, Y = ob.transform.position.y, Seen = now };
        if (surface.Count > 1024)
        {
            var old = new List<int>();
            double frameS = FrameS();
            foreach (var kv in surface) if (!IceClock.Fresh(now, kv.Value.Seen, 5, frameS)) old.Add(kv.Key);
            foreach (var k in old) surface.Remove(k);
        }
    }

    // Surface units seen in the last 5 s of game time (or three frames), as (east km, north km, waterline Unity y) in the frame.
    internal static void SurfaceUnits(IceFrame frame, List<Vector3> into)
    {
        into.Clear();
        double now = Now(), frameS = FrameS();
        foreach (var m in surface.Values)
        {
            if (!IceClock.Fresh(now, m.Seen, 5, frameS)) continue;
            frame.ToKm(m.Lat, m.Lon, out double e, out double n);
            into.Add(new Vector3((float)e, (float)n, m.Y));
        }
    }

    internal static void ClearSurfaceUnits() => surface.Clear();

    // ---- (c)-(e) submarines ------------------------------------------------------------------

    // Held under the ice now? Re-decided every half second of game time per boat.
    internal static bool Held(Submarine sub)
    {
        var h = holds.GetOrCreateValue(sub);
        double now = Now();
        if (now < h.Until && now >= h.Until - 2) return h.Held;
        h.Until = now + 0.5;
        var env = Env();
        if (env == null || sub == null) { h.Held = false; return false; }
        var g = sub._geoPosition;
        h.Percent = Percent(env, g);
        h.Lead = h.Percent >= HeavyPercent && LeadAt(env, g, h.Percent);
        h.Held = SubIceRule.Holds(h.Percent, h.Lead, HeavyPercent);
        return h.Held;
    }

    private static bool ManualControl(Submarine sub)
    {
        try { return playerHeightControl != null && (bool)playerHeightControl.GetValue(sub); }
        catch { return false; }
    }

    // The hold ends: give the remembered order back (unless a new one was given), forget the ceiling.
    private static void Release(Submarine sub, Hold h)
    {
        if (!h.Applied) return;
        h.Applied = false;
        h.Ceiling = float.NaN;
        h.ManualTold = false;
        float desired = desiredAltitude(sub);
        bool restored = SubIceRule.RestoreOnRelease(desired, KeelUnity, h.HasOrder, h.Order, out float back);
        if (restored) { setDesiredAltitude(sub, back); OrdersRestored++; }
        h.HasOrder = false;
        if (Diagnostics) Api.Log("sea ice submarine: " + sub.name + " released (" + Pct(h.Percent) + (h.Lead ? ", in a lead" : "") + ")" + (restored ? "; ordered depth " + (-back * SubIceRule.FeetPerUnity).ToString("0", CultureInfo.InvariantCulture) + " ft given back" : ""));
    }

    internal static void SubFixedPrefix(Submarine __instance)
    {
        if (!SubsOn) return;
        try
        {
            if (__instance == null || !__instance._canUpdate || !__instance.isSubmerged()) return;
            var h = holds.GetOrCreateValue(__instance);
            if (!Held(__instance)) { Release(__instance, h); return; }
            bool was = h.Applied;
            h.Applied = true;
            float desired = desiredAltitude(__instance);
            SubIceRule.RememberDesired(desired, KeelUnity, ref h.HasOrder, ref h.Order);
            float clamped = SubIceRule.ClampDesiredAltitude(desired, KeelUnity);
            if (clamped != desired) { setDesiredAltitude(__instance, clamped); SubClamps++; }
            h.Ceiling = SubIceRule.Ceiling(h.Ceiling, __instance.transform.position.y, KeelUnity);
            if (ManualControl(__instance))
            {
                // pitch and ballast keys: applyDepth would ignore the target depth; back to the depth order
                __instance.setPlayerHeightControl(false);
                ManualOverrides++;
                if (!h.ManualTold) { h.ManualTold = true; Tell(__instance, h, "Manual depth control overridden: ice overhead (" + Pct(h.Percent) + "). Pitch and ballast cannot lift the boat; holding below " + (KeelMeters / 0.3048).ToString("0", CultureInfo.InvariantCulture) + " ft until open water or a lead.", true); }
            }
            if (__instance.getRaisedMastsCount() > 0 || __instance.isSnorkelMastOut())
            {
                retractMasts(__instance);
                if (__instance.isSnorkelMastOut()) __instance.toggleSnorkelMast(false);
            }
            if (!was || clamped != desired) Tell(__instance, h, "Ice overhead (" + Pct(h.Percent) + "): cannot surface, come to periscope depth, snorkel or raise masts. Holding below " + (KeelMeters / 0.3048).ToString("0", CultureInfo.InvariantCulture) + " ft until open water or a lead.");
            if (!was && Diagnostics) Api.Log("sea ice submarine: " + __instance.name + " held at " + Geo(__instance._geoPosition) + " ice " + Pct(h.Percent) + "; depth " + (-__instance.transform.position.y * SubIceRule.FeetPerUnity).ToString("0", CultureInfo.InvariantCulture) + " ft, ordered " + (-desired * SubIceRule.FeetPerUnity).ToString("0", CultureInfo.InvariantCulture) + " ft -> " + (-clamped * SubIceRule.FeetPerUnity).ToString("0", CultureInfo.InvariantCulture) + " ft");
        }
        catch (Exception e) { SubsOn = false; Fail("submarines", e); }
    }

    // Held boats only, after the fixed-step prefix: DepthKeeping's shallow-water target.
    private static bool Applied(Submarine sub, out Hold h) => holds.TryGetValue(sub, out h) && h.Applied && Held(sub);

    internal static void DepthKeepingPostfix(Submarine __instance)
    {
        if (!SubsOn) return;
        try
        {
            if (__instance == null || !__instance.isSubmerged() || !Applied(__instance, out _)) return;
            float t = __instance._targetAltitude;
            float c = SubIceRule.ClampTargetAltitude(t, KeelUnity, __instance.transform.position.y);
            if (c != t) { __instance._targetAltitude = c; TargetClamps++; }
        }
        catch (Exception e) { SubsOn = false; Fail("submarines", e); }
    }

    // Backstop after applyDepth: no rise above the hold's ceiling, no upward ballast rate there, and
    // applyDepth's surfacing branch (_targetAltitude = 0, _divingInProgress = false) undone.
    internal static void ApplyDepthPostfix(Submarine __instance)
    {
        if (!SubsOn) return;
        try
        {
            if (__instance == null || !Applied(__instance, out var h) || float.IsNaN(h.Ceiling)) return;
            var t = __instance.transform;
            var p = t.position;
            if (p.y > h.Ceiling) { t.position = new Vector3(p.x, h.Ceiling, p.z); RisesStopped++; }
            if (p.y >= h.Ceiling - 0.01f)
            {
                if (__instance._currentDepthChangeUsingTanks < 0) __instance._currentDepthChangeUsingTanks = 0;
                if (__instance._targetBallastDepthChangeRate < 0) __instance._targetBallastDepthChangeRate = 0;
            }
            float target = SubIceRule.ClampTargetAltitude(__instance._targetAltitude, KeelUnity, t.position.y);
            if (target != __instance._targetAltitude) { __instance._targetAltitude = target; TargetClamps++; }
            if (!__instance._divingInProgress) { __instance._divingInProgress = true; RisesStopped++; } // applyDepth runs only while diving
        }
        catch (Exception e) { SubsOn = false; Fail("submarines", e); }
    }

    // SubmarineStates.Snorkelling: no snorkel attempt (and no latch) while held; a fresh one after release.
    internal static void SnorkelStatePrefix(Submarine ____submarine, ref bool ____depthReached)
    {
        if (!SubsOn) return;
        try
        {
            var sub = ____submarine;
            if (sub == null) return;
            var h = holds.GetOrCreateValue(sub);
            bool held = sub.isSubmerged() && Held(sub);
            if (!held) Release(sub, h); // the order back first, so OnAltitude compares against it
            bool before = ____depthReached, was = h.SnorkelSuppressed;
            ____depthReached = SubIceRule.SnorkelDepthReached(held, ____depthReached, ref h.SnorkelSuppressed);
            if (held && !was) SnorkelHolds++;
            if (Diagnostics && was != h.SnorkelSuppressed) Api.Log("sea ice submarine: " + sub.name + (held ? " snorkelling state waits under the ice (depth reached " + before + ")" : " snorkelling state tries again in open water"));
        }
        catch (Exception e) { SubsOn = false; Fail("submarines", e); }
    }

    internal static bool SetDepthPrefix(Submarine __instance, ref float __0)
    {
        if (!SubsOn) return true;
        try
        {
            if (__instance == null || !__instance.isSubmerged() || !Held(__instance)) return true;
            var h = holds.GetOrCreateValue(__instance);
            // Submarine.changePitch ends with setDepth(TargetPitch * 1000) under manual height control (the
            // pitch keys): not a depth order. Held, it is dropped and the depth order stays.
            if (ManualControl(__instance)) { ManualOverrides++; return false; }
            SubIceRule.RememberOrderedDepth(__0, KeelUnity, ref h.HasOrder, ref h.Order);
            float d = SubIceRule.ClampOrderedDepth(__0, KeelUnity);
            if (d != __0)
            {
                __0 = d; OrderClamps++;
                Tell(__instance, h, "Order refused: ice overhead (" + Pct(h.Percent) + "). Holding below " + (KeelMeters / 0.3048).ToString("0", CultureInfo.InvariantCulture) + " ft; the order is kept for open water.");
            }
        }
        catch (Exception e) { SubsOn = false; Fail("submarines", e); }
        return true;
    }

    internal static void BlowPostfix(Submarine __instance, ref bool __result)
    {
        if (!SubsOn || !__result) return;
        try
        {
            if (__instance == null || !__instance.isSubmerged() || !Held(__instance)) return;
            __result = false;
            setBlowInitiated(__instance, false);
            BlowsRefused++;
            Tell(__instance, holds.GetOrCreateValue(__instance), "Emergency blow impossible under the ice (" + Pct(holds.GetOrCreateValue(__instance).Percent) + "): make for a lead or open water.");
        }
        catch (Exception e) { SubsOn = false; Fail("submarines", e); }
    }

    internal static bool MastPrefix(SensorSystem __instance)
    {
        if (!SubsOn) return true;
        try
        {
            if (__instance == null || !(__instance._baseObject is Submarine sub)) return true;
            bool mast = __instance._isSubmarineMast || __instance._systemType == BaseSystem.SystemType.SensorPeriscope || __instance._systemType == BaseSystem.SystemType.SensorESM;
            if (!mast || !sub.isSubmerged() || !Held(sub)) return true;
            MastsRefused++;
            Tell(sub, holds.GetOrCreateValue(sub), "Mast stays down: ice overhead (" + Pct(holds.GetOrCreateValue(sub).Percent) + ").");
            return false;
        }
        catch (Exception e) { SubsOn = false; Fail("submarines", e); return true; }
    }

    internal static bool SnorkelPrefix(SnorkelMastSystem __instance)
    {
        if (!SubsOn) return true;
        try
        {
            if (__instance == null || !(__instance._baseObject is Submarine sub) || !sub.isSubmerged() || !Held(sub)) return true;
            MastsRefused++;
            Tell(sub, holds.GetOrCreateValue(sub), "Snorkel stays down: ice overhead (" + Pct(holds.GetOrCreateValue(sub).Percent) + ").");
            return false;
        }
        catch (Exception e) { SubsOn = false; Fail("submarines", e); return true; }
    }

    // ---- messages and diagnostics ------------------------------------------------------------

    private static void Tell(Submarine sub, Hold h, string text, bool once = false)
    {
        float now = Time.realtimeSinceStartup; // real time: at 1000x a game-time throttle would flood the screen
        if (!once && now - h.LastMessage < 20f && now >= h.LastMessage) return;
        h.LastMessage = now;
        if (sub.IsPlayerObject) Alert(sub, text);
        if (Diagnostics) Api.Log("sea ice submarine: " + sub.name + ": " + text);
    }

    private static bool alertFailed;
    private static void Alert(ObjectBase ob, string text)
    {
        if (alertFailed || raiseAlert == null) return;
        try
        {
            var vm = mainGameViewModel.GetValue(null);
            if (vm != null) raiseAlert.Invoke(vm, new object[] { ob, text });
        }
        catch (Exception e) { alertFailed = true; Api.LogFailure("sea ice: on-screen messages unavailable (the log keeps them under SeaIceDiagnostics=1)", e); }
    }

    private static readonly HashSet<string> failed = new HashSet<string>();
    private static void Fail(string part, Exception e)
    {
        bool first;
        lock (failed) first = failed.Add(part); // the noise postfix runs on the sonar's worker tasks
        if (first) Api.LogFailure("sea ice: " + part + " stopped for this session; native behaviour restored", e);
    }

    internal static string Pct(double c) => double.IsNaN(c) ? "?" : c.ToString("0", CultureInfo.InvariantCulture) + " %";
    internal static string Geo(GeoPosition g) => g._latitude.ToString("0.000", CultureInfo.InvariantCulture) + ", " + g._longitude.ToString("0.000", CultureInfo.InvariantCulture);

    // Every 10 s of real time under SeaIceDiagnostics=1 (called by the sheet driver's Update).
    internal static void Report(Environment env)
    {
        if (!Diagnostics || env == null) return;
        float now = Time.realtimeSinceStartup;
        if (now < nextReport) return;
        nextReport = now + 10f;
        try
        {
            string unit = "no unit selected";
            var rp = typeof(Singleton<RenderPosition>).GetField("_instance", BindingFlags.Static | BindingFlags.NonPublic)?.GetValue(null) as RenderPosition;
            ObjectBase sel = rp != null ? rp.getSelectedObject() : null;
            if (sel != null)
            {
                var g = sel._geoPosition;
                double c = Percent(env, g);
                unit = sel.name + " at " + Geo(g) + ": ice " + Pct(c) + ", ocean noise " + env.getOceanNoise(g).ToString("0.0", CultureInfo.InvariantCulture) + ", floe ice term " + env.getFloeIce(g).ToString("0.00", CultureInfo.InvariantCulture)
                    + ", access(none) " + IceRules.Access(c, 0) + (IceEdge.Below(c) ? ", under the " : ", drawn from the ") + EdgePercent.ToString("0.#", CultureInfo.InvariantCulture) + " % edge, terrain " + (TerrainUtils.GetHeightAt(g, false, false, false) * SubIceRule.FeetPerUnity).ToString("0", CultureInfo.InvariantCulture) + " ft";
                if (sel is Submarine s) unit += ", submarine " + (s.isSubmerged() ? "submerged " + (-s.transform.position.y * SubIceRule.FeetPerUnity).ToString("0", CultureInfo.InvariantCulture) + " ft" : "surfaced") + (s.isSubmerged() ? (Held(s) ? ", HELD under ice" : ", free" + (holds.TryGetValue(s, out var h) && h.Lead ? " (lead)" : "")) : "");
            }
            Api.Log("sea ice @ " + Date(env).ToString("yyyy-MM-dd HH:mm", CultureInfo.InvariantCulture) + ": " + unit + "; last 10 s: speed caps " + SpeedCaps + ", depth clamps " + SubClamps + ", orders clamped " + OrderClamps + ", blows refused " + BlowsRefused  + ", masts refused " + MastsRefused + ", keeping targets clamped " + TargetClamps + ", rises stopped " + RisesStopped + ", manual control overridden " + ManualOverrides + ", orders given back " + OrdersRestored + ", snorkel states held " + SnorkelHolds + ", getFloeIce calls " + FloeCalls + "; tile cache " + Cache.Count + " (hits " + Cache.Hits + ", misses " + Cache.Misses + ")");
            if (CarveOn || BreakupOn || SoundOn || BreakNoiseOn)
            {
                var snap = Carve.Published;
                int breaking = 0;
                double t = Now(), frameS = FrameS();
                foreach (var b in Breakers.Values) if (IsCurrent(b, t, frameS) && b.Intensity > 0) breaking++;
                Api.Log("sea ice channels: " + (CarveOn ? Carve.Count + " segments in " + snap.Cells + " carve cells (" + (IceCarveSnapshot.BucketKm * 1000).ToString("0", CultureInfo.InvariantCulture) + " m) over " + snap.ChunkCount + " chunks, " + Carve.Tracking + " tracks; last 10 s " + CarvePoints + " points added; " + Carve.Expired + " refrozen and " + Carve.Dropped + " dropped (cap " + IceCarve.MaxSegments + ") this battle; " + Carve.Publishes + " snapshots published (last: " + snap.ChunksBuilt + " chunks rebuilt, " + snap.ChunksShared + " shared); " + Carve.DirtyCount + " chunks waiting to rebuild; refreeze " + (Carve.RefreezeS / 60).ToString("0", CultureInfo.InvariantCulture) + " min of game time (clock " + ClockState + ", compression " + Compression().ToString("0.#", CultureInfo.InvariantCulture) + "x); speed eased by a channel " + ChannelHelps + " times" : "off") +
                    "; ships breaking ice " + breaking + "; breaking noise added to passive target levels " + NoiseAdds + " times, to interferer levels " + InterfererAdds + " times" + (BreakNoiseOn ? "" : " (off)"));
                CarvePoints = ChannelHelps = 0;
                Interlocked.Exchange(ref NoiseAdds, 0); Interlocked.Exchange(ref InterfererAdds, 0);
            }
            SpeedCaps = SubClamps = OrderClamps = BlowsRefused = MastsRefused = FloeCalls = TargetClamps = RisesStopped = ManualOverrides = OrdersRestored = SnorkelHolds = 0;
        }
        catch (Exception e) { Api.LogFailure("sea ice diagnostics", e); }
    }
}
