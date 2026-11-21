using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq.Expressions;
using System.Reflection;
using System.Runtime.CompilerServices;
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
internal static class SeaIceBattle
{
    internal const string HarmonyId = "io.github.sest-hobby.sea-ice";
    internal static readonly SeaIceTileCache Cache = new SeaIceTileCache();
    internal static bool Diagnostics, NoiseOn, ShipsOn, SubsOn, BlockBlow;
    internal static double HeavyPercent = SubIceRule.DefaultHeavyPercent, KeelMeters = SubIceRule.DefaultKeelMeters, EdgePercent = 15;
    internal static double NoiseMaxOverride = double.NaN;
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
        internal float NextMark = -1e9f;
        internal int LastSign;
        internal int Capability = -1;
        internal float LastMessage = -1e9f;
        internal bool Capped;
    }
    private static readonly ConditionalWeakTable<Compartments, Hull> hulls = new ConditionalWeakTable<Compartments, Hull>();

    private sealed class Hold
    {
        internal float Until = -1e9f, LastMessage = -1e9f;
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
    private struct SurfaceMark { internal double Lat, Lon; internal float Y, Seen; }
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
        EdgePercent = Number(lines, "SeaIceEdgePercent", 15, 1, 60);
        KeelUnity = SubIceRule.MetersToUnity(KeelMeters);
        NoiseMaxOverride = Number(lines, "SeaIceNoiseMax", double.NaN, 0, 25.5);
        // The model and its data first: a broken table installs nothing.
        double check = SeaIceModel.Concentration(74.0, 36.0, new DateTime(2029, 3, 10, 12, 0, 0, DateTimeKind.Utc));
        if (!(Math.Abs(check - 62.28) < 0.05)) throw new InvalidOperationException("sea-ice table check failed: " + check.ToString("0.00", CultureInfo.InvariantCulture));
        envInstance = typeof(Singleton<Environment>).GetField("_instance", BindingFlags.Static | BindingFlags.NonPublic);
        if (envInstance == null) throw new MissingFieldException("Singleton<Environment>._instance");
        envMap = typeof(Environment).GetField("_environmentMap", Api.All);
        envMapReady = typeof(Environment).GetField("_isEnvironmentMapInitialized", Api.All);
        mainGameViewModel = typeof(Globals).GetField("_mainGameViewModel", Api.All);
        raiseAlert = mainGameViewModel?.FieldType.GetMethod("RaiseAlert", Api.All, null, new[] { typeof(ObjectBase), typeof(string) }, null);
        var parts = new List<string>();
        if (NoiseOn) Part("ocean noise", parts, () => Api.Postfix(Api.Method(typeof(Environment), "getFloeIce", typeof(float), typeof(GeoPosition)), typeof(SeaIceBattle), nameof(FloeIcePostfix), HarmonyId + ".noise"));
        if (ShipsOn) Part("ship speed", parts, InstallShips);
        if (SubsOn) Part("submarines", parts, InstallSubs);
        Api.Log("sea ice installed (" + string.Join(", ", parts) + "): seasonal concentration from the weather branch's seaice.py climatology (NSIDC monthly extents, edge shape fitted by eye), baseline " + SeaIceData.Baseline +
            "; heavy ice " + HeavyPercent.ToString("0", CultureInfo.InvariantCulture) + " %, keel clearance " + KeelMeters.ToString("0", CultureInfo.InvariantCulture) + " m, sheet edge " + EdgePercent.ToString("0", CultureInfo.InvariantCulture) + " %");
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

    private static float Now() => Time.time;

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
                if (MarkUnits) { var rest = hulls.GetOrCreateValue(__instance); float t = Now(); if (t >= rest.NextMark) { rest.NextMark = t + 1f; MarkSurface(ob, t); } }
                return;
            }
            var env = Env();
            if (env == null) return;
            var g = ob._geoPosition;
            var date = Date(env);
            double c = Cache.Percent(g._latitude, g._longitude, date);
            var hull = hulls.GetOrCreateValue(__instance);
            float now = Now();
            if (MarkUnits && now >= hull.NextMark) { hull.NextMark = now + 1f; MarkSurface(ob, now); }
            if (c < 1 && hull.Speed.State == IceAccess.Open) return;
            if (hull.Capability < 0) hull.Capability = IceRules.CapabilityOf(ob._obp != null ? ob._obp._objectIniName : null);
            int sign = wanted < 0 ? -1 : 1;
            if (now >= hull.NextAhead || sign != hull.LastSign)
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
            float capped = hull.Speed.Cap(wanted, flank, c, hull.Ahead, hull.Capability, hull.HereRaw);
            bool binding = capped != wanted;
            if (binding)
            {
                setWanted(__instance, capped);
                SpeedCaps++;
                if (ob.IsPlayerObject && now - hull.LastMessage > 30f)
                {
                    hull.LastMessage = now;
                    Alert(ob, hull.Speed.SteerageOnly ? "Held by pack ice (" + Pct(c) + "): heavier ice ahead, steerage way only (" + capped.ToString("0", CultureInfo.InvariantCulture) + " kn); back out or turn toward open water." :
                        "In ice (" + Pct(c) + ", " + hull.Speed.State.ToString().ToLowerInvariant() + "): speed limited to " + Math.Abs(capped).ToString("0", CultureInfo.InvariantCulture) + " kn" + (hull.Speed.Escaping ? " (working out of the ice)" : "") + ".");
                }
            }
            if (Diagnostics && binding != hull.Capped)
                Api.Log("sea ice speed: " + ob.name + " at " + Geo(g) + " ice " + Pct(c) + " (model " + Pct(hull.HereRaw) + ") lightest ahead " + Pct(hull.Ahead) + " class " + IceRules.Capabilities[hull.Capability] + " state " + hull.Speed.State + (binding ? " capped " + wanted.ToString("0.0", CultureInfo.InvariantCulture) + " -> " + capped.ToString("0.0", CultureInfo.InvariantCulture) + " kn (flank " + flank.ToString("0.0", CultureInfo.InvariantCulture) + (hull.Speed.Escaping ? ", escaping" : hull.Speed.SteerageOnly ? ", steerage way" : "") + ")" : " released"));
            hull.Capped = binding;
        }
        catch (Exception e) { ShipsOn = false; Fail("ship speed", e); }
    }

    private static void MarkSurface(ObjectBase ob, float now)
    {
        var g = ob._geoPosition;
        surface[ob.GetInstanceID()] = new SurfaceMark { Lat = g._latitude, Lon = g._longitude, Y = ob.transform.position.y, Seen = now };
        if (surface.Count > 1024)
        {
            var old = new List<int>();
            foreach (var kv in surface) if (now - kv.Value.Seen > 5f) old.Add(kv.Key);
            foreach (var k in old) surface.Remove(k);
        }
    }

    // Surface units seen in the last 5 s of game time, as (east km, north km, waterline Unity y) in the frame.
    internal static void SurfaceUnits(IceFrame frame, List<Vector3> into)
    {
        into.Clear();
        float now = Now();
        foreach (var m in surface.Values)
        {
            if (now - m.Seen > 5f || m.Seen > now + 1f) continue;
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
        float now = Now();
        if (now < h.Until) return h.Held;
        h.Until = now + 0.5f;
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
        float now = Now();
        if (!once && now - h.LastMessage < 20f) return;
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
        if (failed.Add(part)) Api.LogFailure("sea ice: " + part + " stopped for this session; native behaviour restored", e);
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
                    + ", access(none) " + IceRules.Access(c, 0) + ", terrain " + (TerrainUtils.GetHeightAt(g, false, false, false) * SubIceRule.FeetPerUnity).ToString("0", CultureInfo.InvariantCulture) + " ft";
                if (sel is Submarine s) unit += ", submarine " + (s.isSubmerged() ? "submerged " + (-s.transform.position.y * SubIceRule.FeetPerUnity).ToString("0", CultureInfo.InvariantCulture) + " ft" : "surfaced") + (s.isSubmerged() ? (Held(s) ? ", HELD under ice" : ", free" + (holds.TryGetValue(s, out var h) && h.Lead ? " (lead)" : "")) : "");
            }
            Api.Log("sea ice @ " + Date(env).ToString("yyyy-MM-dd HH:mm", CultureInfo.InvariantCulture) + ": " + unit + "; last 10 s: speed caps " + SpeedCaps + ", depth clamps " + SubClamps + ", orders clamped " + OrderClamps + ", blows refused " + BlowsRefused  + ", masts refused " + MastsRefused + ", keeping targets clamped " + TargetClamps + ", rises stopped " + RisesStopped + ", manual control overridden " + ManualOverrides + ", orders given back " + OrdersRestored + ", snorkel states held " + SnorkelHolds + ", getFloeIce calls " + FloeCalls + "; tile cache " + Cache.Count + " (hits " + Cache.Hits + ", misses " + Cache.Misses + ")");
            SpeedCaps = SubClamps = OrderClamps = BlowsRefused = MastsRefused = FloeCalls = TargetClamps = RisesStopped = ManualOverrides = OrdersRestored = SnorkelHolds = 0;
        }
        catch (Exception e) { Api.LogFailure("sea ice diagnostics", e); }
    }
}
