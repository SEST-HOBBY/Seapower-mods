using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using System.Runtime.CompilerServices;
using System.Security.Cryptography;
using System.Threading.Tasks;
using AnchorChain;
using UnityEngine;

namespace Sest.RuntimeFixes;

// Sea ice on Dynamic Campaign Mod 1.0.1's campaign map, and in its movement
// (CampaignIce=1 in [Runtime], default on; CampaignIceDiagnostics=1 logs,
// default off; CampaignIceMap=0 / CampaignIceMovement=0 leave one part out).
// Hash-locked to DCM 652fe464 like WorldStorms; bound lazily on its own (now,
// when DCM's assembly loads, or from a GameMain.Update poll every 2 s), never
// behind CumulativeCombatCosts. Every member is checked before anything is
// patched; a mismatch or a later exception logs one line and turns that part
// off ("campaign ice ... unavailable/stopped; Dynamic Campaign Mod's map and
// movement unchanged").
//
// The map is the game's globe. DCM drapes images on it with GlobeDrape (fog,
// land tint, weather, fleet areas: one textured sphere patch each, in one
// CommandBuffer). The weather layer's RGBA32 image (WeatherMapLayer._texture,
// filled by WeatherFrame.Build on a Task.Run thread, uploaded in TakeBuilt
// with LoadRawTextureData + Apply) is the only drape a mod can share without
// new Unity materials, so:
// - Weather layer ON: a postfix on the static WeatherFrame.Build(Request),
//   which runs on DCM's worker thread BEFORE the main thread uploads the
//   frame, composites the ice for the frame's own hour (Frame.Utc = the
//   timeline's ShownUtc) into Frame.Pixels over Request.Water. Every weather
//   layer (wind, sea state, rain, clouds, fog, storms) shows the ice, and the
//   forecast slider shows forecast-day ice. Build rewrites every pixel each
//   time (Image's Parallel.For calls Pixel for each), so a reused buffer
//   never accumulates ice.
// - Weather layer OFF (or before its first frame): WeatherMapLayer.Frame()
//   runs every map frame (CampaignUI's update) and calls Drape(false), which
//   lets go of GlobeDrape's weather slot (_draped false). A postfix on Frame
//   then drapes SEST's own ice-only texture in that slot, built for the
//   campaign's date (CampaignState.Now) at 0.1 degrees (coarser on huge
//   theatres, at most 1 M pixels) off the main thread and replaced when the
//   date changes. When the layer comes back, its own Drape(true) takes the
//   slot again (with the composited image). Detach (leaving the map) lets the
//   slot go (GlobeDrape.Weather(null, false)); its postfix destroys SEST's
//   textures. A theatre without ice drapes nothing. DCM's own "weather" perf
//   toggle (MapPerf.HideWeather, Cheats panel: Frame drapes off even with
//   the layer shown) hides SEST's ice too: nothing is draped while it is
//   set, and SEST's texture is taken off the slot. Three failed overlay
//   builds turn the ice-only overlay off for that map (one line); the count
//   starts again for the next map (a new layer, or Detach).
// - Hover: a postfix on WeatherMapLayer.ShowHover(MapBase) adds "Ice 72 %
//   (heavy pack)" and what it does to surface groups to the readout's body,
//   at the hovered point (MapBase.TryViewToGeoPosition, as ShowHover itself)
//   on the shown hour, over water only. The readout exists only while the
//   weather layer is shown (DCM's Hover returns otherwise).
// Movement: a postfix on WeatherEffects.UpdateCaps() (which rewrites every
// at-sea group's TaskForce.WeatherKnots on every call, StepTo and Update)
// lowers WeatherKnots to (ice factor x the group's full speed,
// Logistics.SpeedOf(group, catalogue): its slowest hull at the telegraph
// step, damage, convoy and fuel limits) when that is below DCM's own weather
// cap. WeatherKnots is an absolute ceiling, the same kind of value DCM's
// WeatherEffects.CapOf writes, so the group is capped whatever it is ordered
// to do, a stopped or slow group included. Its readers all see the ice:
// Movement.SpeedOf = min(OwnSpeedOf, WeatherCapOf) (Advance, MapKnots,
// HoursToRoutePoints: a group ordered faster than the cap is slowed to it),
// and the AI's Rhythm.ClosingHours and Rhythm.Hold, which take
// min(Logistics.SpeedOf, WeatherKnots) x MapFactor as the speed a group can
// make. Without a catalogue (never in a campaign) the cap falls back to the
// ordered speed (Movement.OwnSpeedOf). The factor is ice.py's access speed
// for the slowest surface hull's ice class (SeaIceRules; ice-capability.json
// is empty, so every hull is "none"), at the group's position on the
// campaign date (SeaIceTileCache, 0.05-degree tiles, cached per date);
// submarines (IUnitCatalog.IsSubmarine) pass under; "blocked" crawls at 0.1
// rather than stopping (CampaignIceSpeed.BesetFactor). Each group's factor
// is kept in its Held entry and worked out again only when its day, 0.05-
// degree tile, hulls or catalogue change; the per-step work goes through
// compiled field and method delegates (no boxing), and a group under 39.9
// degrees of latitude is left after one field read. WeatherKnots is
// [NonSerialized], so saves are unchanged. Movement.SpeedText postfix:
// "(heavy seas)" reads "(ice)" while the ice cap is the binding one;
// FleetViewModel.Line postfix: an out-of-fuel group's "(out of fuel, heavy
// seas)", which Line formats itself, reads "(out of fuel, ice)". Routing
// (NavGrid) is NOT changed in this version: routes still cross the pack, and
// the group slows in it.
internal static class CampaignIce
{
    private const string CampaignHash = "652fe464dc23ac3c0063e5ab09dc4656634f30d1d254c782498ef779cb30ac77";
    private const string HarmonyId = "io.github.sest-hobby.campaign-ice";
    private const string Unchanged = "Dynamic Campaign Mod's map and movement unchanged";
    internal const double OverlayCell = 0.1;
    internal const int OverlayMaxPixels = 1000000;

    internal static bool Diagnostics, MapWanted = true, MovementWanted = true;
    private static bool waiting, bound, installed, stopped, mapStopped, moveStopped, releasePending;
    private static double nextBind;
    private static Assembly dcm;
    private static double Now => (double)Stopwatch.GetTimestamp() / Stopwatch.Frequency;

    private static Type layerType, frameType, requestType, drapeType, simType, stateType, navType, geoType, boundsType, vmType;
    private static Type effectsType, catalogType, taskForceType, moverType, hullType, movementType, mapBaseType, geoPositionType;
    private static MethodInfo frameBuild, layerFrame, layerDetach, showHover, drapeWeather, isWater, shownUtc, continuous;
    private static MethodInfo updateCaps, speedText, ownSpeedOf, atSea, isSubmarine, isSubmarineIni, tryToGeo, logisticsSpeedOf, fleetLine;
    private static FieldInfo fPixels, fWidth, fHeight, fSouth, fWest, fCell, fNoImage, fUtc, rWater;
    private static FieldInfo lSim, lVm, lBounds, lRoot, lDraped, lHover, lHoverBody, lHoverAt;
    private static FieldInfo simState, simNav, stateNow, stateTaskForces, latMin, latMax, lonMin, lonMax, geoLat, geoLon, posLat, posLon;
    private static FieldInfo drapeTexture, drapeShown, effState, effCatalog, tfShips, tfWeatherKnots, moverPosition, moverName, moverId, hullIni, hideWeather;
    // The per-step movement path: compiled once in Bind (DynamicMethods in
    // DCM's own module), so nothing is boxed and no object[] is made.
    private static Func<object, bool> fAtSea;
    private static Func<object, double> fLat, fLon, fWeather, fOwn;
    private static Action<object, double> fSetWeather;
    private static Func<object, IList> fShips;
    private static Func<object, string> fIni;
    private static Func<object, object, double> fCapability;
    private static Func<object, string, bool> fIsSubmarine;
    private static Func<string, bool> fIsSubmarineIni;
    private static Func<bool> fHideWeather;

    internal static readonly IceRasterCache FrameRasters = new IceRasterCache();
    internal static readonly SeaIceTileCache Tiles = new SeaIceTileCache();
    internal static int FramesComposited;

    // From RuntimeFixesMod, before the CumulativeCombatCosts return. Never throws.
    internal static void Start(Assembly native, string[] lines)
    {
        try
        {
            Diagnostics = Policy.TextOption(lines, "CampaignIceDiagnostics", "0") == "1";
            MapWanted = Policy.TextOption(lines, "CampaignIceMap", "1") == "1";
            MovementWanted = Policy.TextOption(lines, "CampaignIceMovement", "1") == "1";
            if (TryBind()) return;
            waiting = true;
            AppDomain.CurrentDomain.AssemblyLoad += Loaded;
            Api.Postfix(Api.Method(Api.Type(native, "SeaPower.GameMain"), "Update", typeof(void)), typeof(CampaignIce), nameof(Poll), HarmonyId + ".bootstrap");
            if (Diagnostics) Api.Log("campaign ice awaiting Dynamic Campaign Mod 1.0.1");
        }
        catch (Exception ex) { Stop("campaign ice unavailable; " + Unchanged, ex); }
    }

    private static void Loaded(object sender, AssemblyLoadEventArgs args)
    {
        try
        {
            if (waiting && args.LoadedAssembly.GetType("DynamicCampaignMod.Game.Session.CampaignSession", false) != null) { nextBind = 0; Poll(); }
        }
        catch (Exception ex) { Stop("campaign ice unavailable; " + Unchanged, ex); }
    }

    internal static void Poll()
    {
        if (!waiting || stopped || Now < nextBind) return;
        nextBind = Now + 2;
        try { TryBind(); }
        catch (Exception ex) { Stop("campaign ice unavailable; " + Unchanged, ex); }
    }

    private static bool TryBind()
    {
        var a = AppDomain.CurrentDomain.GetAssemblies().FirstOrDefault(x => x.GetType("DynamicCampaignMod.Game.Session.CampaignSession", false) != null);
        if (a == null) return false;
        waiting = false;
        AppDomain.CurrentDomain.AssemblyLoad -= Loaded;
        if (Bind(a)) Install();
        return true;
    }

    private static void Stop(string label, Exception ex)
    {
        bool first = !stopped;
        stopped = true; waiting = false;
        if (first) Api.LogFailure(label, ex);
        StopMap(null, null);
    }

    // The map part off: SEST's texture leaves GlobeDrape's weather slot on the
    // next map frame or Detach (main thread; a stop can come from DCM's frame
    // worker), and DCM's own weather layer takes the slot again when shown.
    private static void StopMap(string label, Exception ex)
    {
        bool first = !mapStopped;
        mapStopped = true;
        releasePending = true;
        if (first && label != null) Api.LogFailure(label, ex);
    }

    // Main thread only: after a stop, SEST's texture is taken off once.
    private static bool Stopped()
    {
        if (!mapStopped) return false;
        if (releasePending)
        {
            releasePending = false;
            try { Overlay.Release(); } catch (Exception e) { try { Api.LogFailure("campaign ice map: the ice texture was not released", e); } catch { } }
        }
        return true;
    }

    private static void StopMovement(string label, Exception ex)
    {
        bool first = !moveStopped;
        moveStopped = true;
        if (first) Api.LogFailure(label, ex);
    }

    private static void Member(string name, bool ok)
    {
        if (Diagnostics) Api.Log("campaign ice bind: " + name + (ok ? " ok" : " MISSING"));
        if (!ok) throw new MissingMemberException("captured " + name);
    }
    private static FieldInfo F(Type t, string name, Type expected, bool isStatic = false)
    {
        var f = t.GetField(name, Api.All);
        Member(t.Name + "." + name + " : " + (expected?.Name ?? "?"), f != null && f.IsStatic == isStatic && (expected == null || f.FieldType == expected));
        return f;
    }
    private static MethodInfo M(Type t, string name, Type returns, bool isStatic, params Type[] args)
    {
        var m = t.GetMethod(name, Api.All, null, args, null);
        Member(t.Name + "." + name + "(" + string.Join(", ", args.Select(x => x.Name)) + ") : " + returns.Name, m != null && m.ReturnType == returns && m.IsStatic == isStatic);
        return m;
    }

    // Hash-locked, every member checked; false (one log line) on any mismatch.
    // game: Seapower-Scripts (MapBase.TryViewToGeoPosition, GeoPosition) for
    // the hover; null finds it among the loaded assemblies.
    internal static bool Bind(Assembly a, Assembly game = null)
    {
        try
        {
            using (var sha = SHA256.Create())
            using (var stream = File.OpenRead(BetaAssemblyPolicy.OriginalLocation(a)))
                if (BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant() != CampaignHash)
                    throw new InvalidOperationException("campaign ice requires the inspected Dynamic Campaign Mod 1.0.1 image (652fe464)");
            dcm = a;
            const string ns = "DynamicCampaignMod.";
            Type T(string n) => a.GetType(ns + n, true);
            layerType = T("UI.Map.WeatherMapLayer");
            frameType = T("Core.Sim.WeatherFrame");
            requestType = T("Core.Sim.WeatherFrame+Request");
            drapeType = T("UI.Map.GlobeDrape");
            simType = T("Core.Sim.CampaignSim");
            stateType = T("Core.State.CampaignState");
            navType = T("Core.Geo.NavGrid");
            geoType = T("Core.Geo.GeoPoint");
            boundsType = T("Core.Data.GeoBounds");
            vmType = T("UI.WeatherPanel.WeatherViewModel");
            effectsType = T("Core.Sim.WeatherEffects");
            catalogType = T("Core.Data.IUnitCatalog");
            taskForceType = T("Core.State.TaskForce");
            moverType = T("Core.State.Mover");
            hullType = T("Core.State.Hull");
            movementType = T("Core.Sim.Movement");
            var testBattles = T("Core.Sim.TestBattles");
            Member("GeoPoint is a value type", geoType.IsValueType && geoType.GetConstructor(new[] { typeof(double), typeof(double) }) != null);
            Member("TaskForce extends Mover", moverType.IsAssignableFrom(taskForceType));

            // Map: the frame build, its fields, the layer's lifecycle and drape.
            frameBuild = M(frameType, "Build", frameType, true, requestType);
            fPixels = F(frameType, "Pixels", typeof(byte[])); fWidth = F(frameType, "Width", typeof(int)); fHeight = F(frameType, "Height", typeof(int));
            fSouth = F(frameType, "South", typeof(double)); fWest = F(frameType, "West", typeof(double)); fCell = F(frameType, "CellDeg", typeof(double));
            fNoImage = F(frameType, "NoImage", typeof(bool)); fUtc = F(frameType, "Utc", typeof(DateTime));
            rWater = F(requestType, "Water", typeof(bool[]));
            layerFrame = M(layerType, "Frame", typeof(void), false);
            layerDetach = M(layerType, "Detach", typeof(void), false);
            lSim = F(layerType, "_sim", simType); lVm = F(layerType, "_vm", vmType); lBounds = F(layerType, "_bounds", boundsType);
            lRoot = F(layerType, "_root", typeof(Noesis.Grid)); lDraped = F(layerType, "_draped", typeof(bool));
            lHover = F(layerType, "_hover", typeof(Noesis.Border)); lHoverBody = F(layerType, "_hoverBody", typeof(Noesis.TextBlock));
            lHoverAt = F(layerType, "_hoverAt", typeof(Noesis.Point?));
            drapeWeather = M(drapeType, "Weather", typeof(void), true, typeof(Texture2D), typeof(bool), typeof(double), typeof(double), typeof(double), typeof(double));
            drapeTexture = F(drapeType, "_weatherTexture", typeof(Texture2D), true); drapeShown = F(drapeType, "_weatherShown", typeof(bool), true);
            simState = F(simType, "State", stateType); simNav = F(simType, "Nav", navType);
            stateNow = F(stateType, "Now", typeof(DateTime));
            stateTaskForces = F(stateType, "TaskForces", typeof(List<>).MakeGenericType(taskForceType));
            isWater = M(navType, "IsWater", typeof(bool), false, geoType);
            shownUtc = M(vmType, "get_ShownUtc", typeof(DateTime), false);
            latMin = F(boundsType, "latMin", typeof(double)); latMax = F(boundsType, "latMax", typeof(double));
            lonMin = F(boundsType, "lonMin", typeof(double)); lonMax = F(boundsType, "lonMax", typeof(double));
            continuous = M(boundsType, "Continuous", typeof(double), false, typeof(double));
            geoLat = F(geoType, "Lat", typeof(double)); geoLon = F(geoType, "Lon", typeof(double));
            var mapBase = game ?? AppDomain.CurrentDomain.GetAssemblies().FirstOrDefault(x => x.GetName().Name == "Seapower-Scripts");
            if (mapBase == null) throw new MissingMemberException("Seapower-Scripts is not loaded");
            mapBaseType = mapBase.GetType("MapControl.MapBase", true);
            geoPositionType = mapBase.GetType("SeaPower.GeoPosition", true);
            showHover = M(layerType, "ShowHover", typeof(void), false, mapBaseType);
            tryToGeo = M(mapBaseType, "TryViewToGeoPosition", typeof(bool), false, typeof(Noesis.Point), geoPositionType.MakeByRefType());
            posLat = F(geoPositionType, "_latitude", typeof(double)); posLon = F(geoPositionType, "_longitude", typeof(double));

            // Movement.
            updateCaps = M(effectsType, "UpdateCaps", typeof(void), false);
            effState = F(effectsType, "_state", stateType); effCatalog = F(effectsType, "_catalog", catalogType);
            speedText = M(movementType, "SpeedText", typeof(string), true, moverType);
            ownSpeedOf = M(movementType, "OwnSpeedOf", typeof(double), true, moverType);
            M(movementType, "WeatherCapOf", typeof(double), true, moverType);
            atSea = M(taskForceType, "get_AtSea", typeof(bool), false);
            tfShips = F(taskForceType, "Ships", typeof(List<>).MakeGenericType(hullType));
            tfWeatherKnots = F(taskForceType, "WeatherKnots", typeof(double));
            Member("TaskForce.WeatherKnots is [NonSerialized] (saves unchanged)", tfWeatherKnots.IsNotSerialized);
            moverPosition = F(moverType, "Position", geoType); moverName = F(moverType, "Name", typeof(string)); moverId = F(moverType, "Id", typeof(int));
            hullIni = F(hullType, "UnitIni", typeof(string));
            isSubmarine = M(catalogType, "IsSubmarine", typeof(bool), false, typeof(string));
            isSubmarineIni = M(testBattles, "IsSubmarineIni", typeof(bool), true, typeof(string));
            // The ice ceiling's base: the group's full speed, as the AI reads it.
            logisticsSpeedOf = M(T("Core.Sim.Logistics"), "SpeedOf", typeof(double), true, taskForceType, catalogType);
            Member("Logistics.SpeedOf is public (DCM's AI reads it with WeatherKnots)", logisticsSpeedOf.IsPublic);
            // The fleet list's out-of-fuel text, and DCM's weather perf toggle.
            fleetLine = M(T("UI.Strategy.FleetViewModel"), "Line", typeof(string), false, taskForceType, typeof(long));
            hideWeather = F(T("UI.Map.MapPerf"), "HideWeather", typeof(bool), true);
            Compile();
            Member("movement delegates compiled", fAtSea != null && fLat != null && fCapability != null && fIsSubmarine != null && fHideWeather != null);
            bound = true;
            if (Diagnostics) Api.Log("campaign ice bind: all members of Dynamic Campaign Mod 1.0.1 (652fe464) bound");
            return true;
        }
        catch (Exception ex)
        {
            bound = false;
            Stop("campaign ice unavailable; " + Unchanged, ex);
            return false;
        }
    }

    // ---- Compiled accessors (movement and the per-frame perf toggle) ----

    // A DynamicMethod hosted in DCM's own module, so its internal types and
    // fields are reachable without visibility checks.
    private static ILGenerator Il(string name, Type ret, Type[] args, out DynamicMethod dm)
    {
        dm = new DynamicMethod("sest_campaign_ice_" + name, ret, args, dcm.ManifestModule, true);
        return dm.GetILGenerator();
    }
    private static void Arg(ILGenerator il, int i, Type t)
    {
        il.Emit(OpCodes.Ldarg, (short)i);
        if (t.IsValueType) il.Emit(OpCodes.Unbox_Any, t);
        else if (t != typeof(object)) il.Emit(OpCodes.Castclass, t);
    }
    private static void Call(ILGenerator il, MethodInfo m) => il.Emit(m.IsStatic || m.DeclaringType.IsValueType ? OpCodes.Call : OpCodes.Callvirt, m);

    // object -> field (reference-type owner), or object -> outer.inner for a
    // struct field (Mover.Position.Lat).
    private static Func<object, TOut> Getter<TOut>(FieldInfo f, FieldInfo inner = null)
    {
        var il = Il("get_" + f.Name + (inner == null ? "" : "_" + inner.Name), typeof(TOut), new[] { typeof(object) }, out var dm);
        Arg(il, 0, f.DeclaringType);
        if (inner != null) { il.Emit(OpCodes.Ldflda, f); il.Emit(OpCodes.Ldfld, inner); }
        else il.Emit(OpCodes.Ldfld, f);
        il.Emit(OpCodes.Ret);
        return (Func<object, TOut>)dm.CreateDelegate(typeof(Func<object, TOut>));
    }
    private static Action<object, double> Setter(FieldInfo f)
    {
        var il = Il("set_" + f.Name, typeof(void), new[] { typeof(object), typeof(double) }, out var dm);
        Arg(il, 0, f.DeclaringType);
        il.Emit(OpCodes.Ldarg_1);
        il.Emit(OpCodes.Stfld, f);
        il.Emit(OpCodes.Ret);
        return (Action<object, double>)dm.CreateDelegate(typeof(Action<object, double>));
    }
    // An instance method with no argument, or a static one with one: object -> result.
    private static Func<object, TOut> Invoker<TOut>(MethodInfo m)
    {
        var il = Il(m.Name, typeof(TOut), new[] { typeof(object) }, out var dm);
        Arg(il, 0, m.IsStatic ? m.GetParameters()[0].ParameterType : m.DeclaringType);
        Call(il, m);
        il.Emit(OpCodes.Ret);
        return (Func<object, TOut>)dm.CreateDelegate(typeof(Func<object, TOut>));
    }
    // A static method with two arguments, or an instance one with one.
    private static Func<object, TArg, TOut> Invoker<TArg, TOut>(MethodInfo m)
    {
        var ps = m.GetParameters();
        var il = Il(m.Name + "2", typeof(TOut), new[] { typeof(object), typeof(TArg) }, out var dm);
        Arg(il, 0, m.IsStatic ? ps[0].ParameterType : m.DeclaringType);
        Arg(il, 1, m.IsStatic ? ps[1].ParameterType : ps[0].ParameterType);
        Call(il, m);
        il.Emit(OpCodes.Ret);
        return (Func<object, TArg, TOut>)dm.CreateDelegate(typeof(Func<object, TArg, TOut>));
    }
    private static Func<bool> StaticGetter(FieldInfo f)
    {
        var il = Il("get_" + f.Name, typeof(bool), Type.EmptyTypes, out var dm);
        il.Emit(OpCodes.Ldsfld, f);
        il.Emit(OpCodes.Ret);
        return (Func<bool>)dm.CreateDelegate(typeof(Func<bool>));
    }

    private static void Compile()
    {
        fAtSea = Invoker<bool>(atSea);
        fLat = Getter<double>(moverPosition, geoLat);
        fLon = Getter<double>(moverPosition, geoLon);
        fWeather = Getter<double>(tfWeatherKnots);
        fSetWeather = Setter(tfWeatherKnots);
        fShips = Getter<IList>(tfShips);
        fIni = Getter<string>(hullIni);
        fOwn = Invoker<double>(ownSpeedOf);
        fCapability = Invoker<object, double>(logisticsSpeedOf);
        fIsSubmarine = Invoker<string, bool>(isSubmarine);
        fIsSubmarineIni = (Func<string, bool>)Delegate.CreateDelegate(typeof(Func<string, bool>), isSubmarineIni);
        fHideWeather = StaticGetter(hideWeather);
    }

    internal static void Install()
    {
        if (!bound || installed || stopped) return;
        var parts = new List<string>();
        if (MapWanted)
        {
            try
            {
                Api.Postfix(frameBuild, typeof(CampaignIce), nameof(AfterFrameBuild), HarmonyId + ".map");
                Api.Postfix(layerFrame, typeof(CampaignIce), nameof(AfterLayerFrame), HarmonyId + ".map");
                Api.Postfix(layerDetach, typeof(CampaignIce), nameof(AfterLayerDetach), HarmonyId + ".map");
                Api.Postfix(showHover, typeof(CampaignIce), nameof(AfterShowHover), HarmonyId + ".map");
                parts.Add("map (ice on every weather layer, ice alone with the weather layer off, hover readout)");
            }
            catch (Exception ex) { StopMap("campaign ice map unavailable; Dynamic Campaign Mod's map unchanged", ex); }
        }
        else mapStopped = true;
        if (MovementWanted)
        {
            try
            {
                Api.Postfix(updateCaps, typeof(CampaignIce), nameof(AfterUpdateCaps), HarmonyId + ".movement");
                Api.Postfix(speedText, typeof(CampaignIce), nameof(AfterSpeedText), HarmonyId + ".movement");
                Api.Postfix(fleetLine, typeof(CampaignIce), nameof(AfterFleetLine), HarmonyId + ".movement");
                parts.Add("movement (surface groups slowed by ice class, submarines pass under; routes unchanged)");
            }
            catch (Exception ex) { StopMovement("campaign ice movement unavailable; Dynamic Campaign Mod's movement unchanged", ex); }
        }
        else moveStopped = true;
        installed = true;
        Api.Log("campaign ice installed: " + (parts.Count == 0 ? "nothing (CampaignIceMap=0 and CampaignIceMovement=0)" : string.Join("; ", parts)) +
                (Diagnostics ? "; diagnostics on" : ""));
    }

    private static string Num(double v, string f = "0.0") => v.ToString(f, CultureInfo.InvariantCulture);

    // ---- Map: the weather frame (worker thread) ----

    // Postfix on static WeatherFrame.Build(Request q). Runs where Build runs
    // (DCM's Task.Run worker), before TakeBuilt uploads the pixels. Only a
    // frame that got ice is counted, so "frame 1" in the log is the first
    // frame with ice drawn in it, even after a campaign without ice (Hormuz)
    // in the same game.
    internal static void AfterFrameBuild(object __0, object __result)
    {
        if (mapStopped || __result == null) return;
        try
        {
            int n = Composite(__0, __result);
            if (n <= 0) return;
            int count = System.Threading.Interlocked.Increment(ref FramesComposited);
            if (count == 1 || Diagnostics && (count <= 5 || count % 200 == 0))
                Api.Log("campaign ice map: weather frame " + ((DateTime)fUtc.GetValue(__result)).ToString("yyyy-MM-dd HH'Z'", CultureInfo.InvariantCulture) +
                        " composited with sea ice (" + n + " ice pixels; frame " + count + ")");
        }
        catch (Exception ex) { StopMap("campaign ice map stopped; " + Unchanged, ex); }
    }

    // The composite itself, separate so tests run it on a real frame.
    // -1: no image to draw on.
    internal static int Composite(object request, object frame)
    {
        if ((bool)fNoImage.GetValue(frame)) return -1;
        var pixels = (byte[])fPixels.GetValue(frame);
        if (pixels == null) return -1;
        int w = (int)fWidth.GetValue(frame), h = (int)fHeight.GetValue(frame);
        double south = (double)fSouth.GetValue(frame), west = (double)fWest.GetValue(frame), cell = (double)fCell.GetValue(frame);
        var raster = FrameRasters.Get(south, west, cell, w, h, (DateTime)fUtc.GetValue(frame));
        if (raster.MaxPercent < CampaignIceStyle.EdgePercent) return 0;
        bool[] water = request == null ? null : (bool[])rWater.GetValue(request);
        return raster.Composite(pixels, water);
    }

    // ---- Map: the ice alone, with the weather layer off ----

    // One overlay per map (the WeatherMapLayer instance): the texture for one
    // date and box, the build in flight, and what is draped.
    internal static class Overlay
    {
        internal static WeakReference Layer;
        internal static Texture2D Texture;
        internal static double South, North, West, East;
        internal const int MaxFailures = 3;
        internal static int DateKey = int.MinValue, Failures;
        internal static string BoxKey;
        internal static Task<Built> Building;
        internal static bool Logged, HiddenLogged;

        internal sealed class Built
        {
            internal IceRaster Raster;
            internal byte[] Pixels;
            internal string BoxKey;
            internal int DateKey;
            internal double Ms;
        }

        // Per map (a new layer instance, Detach, a stop): the texture goes and
        // the failure count starts again, so a bad build in one campaign does
        // not leave the next one without the ice-only overlay.
        internal static Texture2D Forget()
        {
            var t = Texture;
            Texture = null;
            DateKey = int.MinValue;
            BoxKey = null;
            Building = null;
            Layer = null;
            Failures = 0;
            return t;
        }

        internal static void Release()
        {
            var t = Forget();
            if (t == null) return;
            try
            {
                if (drapeTexture != null && ReferenceEquals(drapeTexture.GetValue(null), t))
                    drapeWeather.Invoke(null, new object[] { null, false, 0.0, 0.0, 0.0, 0.0 });
            }
            catch (Exception ex) { Api.LogFailure("campaign ice map: the ice texture was not taken off the globe", ex); }
            UnityEngine.Object.Destroy(t);
        }
    }

    // The overlay's raster on a worker: the model for every pixel, water only
    // asked of NavGrid where there is ice (IsWater on DCM's own worker, as
    // WeatherFrame.WaterOf does).
    internal static Overlay.Built BuildOverlay(double south, double west, double cell, int w, int h, DateTime date, Func<double, double, bool> water, string boxKey)
    {
        var sw = Stopwatch.StartNew();
        var raster = new IceRaster(south, west, cell, w, h, date);
        var mask = new bool[w * h];
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
            {
                int i = y * w + x;
                if (raster.Percent[i] >= CampaignIceStyle.EdgePercent) mask[i] = water == null || water(raster.LatOf(y), raster.LonOf(x));
            }
        var px = raster.Paint(mask);
        return new Overlay.Built { Raster = raster, Pixels = px, BoxKey = boxKey, DateKey = raster.DateKey, Ms = sw.Elapsed.TotalMilliseconds };
    }

    // Postfix on WeatherMapLayer.Frame() (main thread, every map frame).
    internal static void AfterLayerFrame(object __instance)
    {
        if (Stopped() || __instance == null) return;
        try
        {
            if (lRoot.GetValue(__instance) == null) return; // not attached
            // A texture Unity destroyed under us (an asset unload between
            // scenes): build it again.
            if (!ReferenceEquals(Overlay.Texture, null) && Overlay.Texture == null) { Overlay.Texture = null; Overlay.DateKey = int.MinValue; }
            if (Overlay.Layer == null || !ReferenceEquals(Overlay.Layer.Target, __instance))
            {
                Overlay.Release();
                Overlay.Layer = new WeakReference(__instance);
            }
            object sim = lSim.GetValue(__instance);
            object state = sim == null ? null : simState.GetValue(sim);
            object bounds = lBounds.GetValue(__instance);
            if (state == null || bounds == null) return;
            DateTime now = (DateTime)stateNow.GetValue(state);
            int dk = SeaIceTileCache.DateKeyOf(now);
            double s = (double)latMin.GetValue(bounds), n = (double)latMax.GetValue(bounds), w = (double)lonMin.GetValue(bounds), e = (double)lonMax.GetValue(bounds);
            string box = Num(s, "R") + "," + Num(n, "R") + "," + Num(w, "R") + "," + Num(e, "R");
            TakeOverlay();
            bool hidden = fHideWeather();
            if (!hidden && Overlay.Building == null && (dk != Overlay.DateKey || box != Overlay.BoxKey) && Overlay.Failures < Overlay.MaxFailures)
            {
                double cell = IceRaster.CellFor(s, n, w, e, OverlayCell, OverlayMaxPixels);
                IceRaster.SizeOf(s, n, w, e, cell, out int width, out int height);
                object nav = simNav.GetValue(sim);
                Func<double, double, bool> wet = nav == null ? null : (Func<double, double, bool>)((lat, lon) => (bool)isWater.Invoke(nav, new[] { Activator.CreateInstance(geoType, lat, lon) }));
                Overlay.DateKey = dk; Overlay.BoxKey = box;
                Overlay.Building = Task.Run(() => BuildOverlay(s, w, cell, width, height, now, wet, box));
            }
            bool draped = (bool)lDraped.GetValue(__instance);
            bool ours = Overlay.Texture != null && ReferenceEquals(drapeTexture.GetValue(null), Overlay.Texture);
            int action = DrapeAction(draped, hidden, Overlay.Texture != null, ours, ours && (bool)drapeShown.GetValue(null));
            if (action == TakeOff)
            {
                drapeWeather.Invoke(null, new object[] { null, false, 0.0, 0.0, 0.0, 0.0 });
                if (!Overlay.HiddenLogged)
                {
                    Overlay.HiddenLogged = true;
                    Api.Log("campaign ice map: Dynamic Campaign Mod's weather overlay is hidden (Cheats: weather); the sea ice is hidden with it");
                }
            }
            else if (action == DrapeIt)
            {
                drapeWeather.Invoke(null, new object[] { Overlay.Texture, true, Overlay.South, Overlay.North, Overlay.West, Overlay.East });
                if (!Overlay.Logged)
                {
                    Overlay.Logged = true;
                    Api.Log("campaign ice map: sea ice draped on the globe with the weather layer off (" + Overlay.Texture.width + " x " + Overlay.Texture.height +
                            ", " + Num(Overlay.South, "0.##") + " to " + Num(Overlay.North, "0.##") + " lat, " + Num(Overlay.West, "0.##") + " to " + Num(Overlay.East, "0.##") + " lon)");
                }
            }
        }
        catch (Exception ex) { StopMap("campaign ice map stopped; " + Unchanged, ex); }
    }

    internal const int Leave = 0, DrapeIt = 1, TakeOff = 2;
    // What AfterLayerFrame does with GlobeDrape's weather slot. layerDraped:
    // DCM's layer holds the slot (its own composited image); hideWeather:
    // DCM's MapPerf.HideWeather (Frame drapes off even with the layer shown,
    // and the ice-only texture must not take the slot back); ours: SEST's
    // texture is the slot's texture; shown: and the slot is shown.
    internal static int DrapeAction(bool layerDraped, bool hideWeather, bool haveTexture, bool ours, bool shown)
    {
        if (hideWeather) return ours && shown ? TakeOff : Leave;
        if (layerDraped || !haveTexture) return Leave;
        return ours && shown ? Leave : DrapeIt;
    }

    // A finished overlay build becomes the texture (main thread); the old one
    // is taken off the globe first when it was draped.
    private static void TakeOverlay()
    {
        var b = Overlay.Building;
        if (b == null || !b.IsCompleted) return;
        Overlay.Building = null;
        if (b.IsFaulted || b.IsCanceled)
        {
            Overlay.Failures++;
            Api.LogFailure("campaign ice map: the ice overlay was not built", (Exception)b.Exception?.GetBaseException() ?? new TaskCanceledException());
            if (Overlay.Failures == Overlay.MaxFailures)
                Api.Log("campaign ice map: the ice-only overlay failed " + Overlay.MaxFailures + " times and is off for this map (the weather layer still shows the ice; it is tried again on the next map)");
            return;
        }
        var built = b.Result;
        if (built.DateKey != Overlay.DateKey || built.BoxKey != Overlay.BoxKey) return; // superseded
        var old = Overlay.Texture;
        Texture2D tex = null;
        if (built.Raster.IcePixels > 0)
        {
            tex = new Texture2D(built.Raster.Width, built.Raster.Height, TextureFormat.RGBA32, false)
            { name = "SEST campaign sea ice", filterMode = FilterMode.Bilinear, wrapMode = TextureWrapMode.Clamp };
            tex.LoadRawTextureData(built.Pixels);
            tex.Apply(false);
        }
        Overlay.Texture = tex;
        Overlay.South = built.Raster.South; Overlay.North = built.Raster.North; Overlay.West = built.Raster.West; Overlay.East = built.Raster.East;
        if (old != null)
        {
            if (ReferenceEquals(drapeTexture.GetValue(null), old))
                drapeWeather.Invoke(null, tex != null ? new object[] { tex, true, Overlay.South, Overlay.North, Overlay.West, Overlay.East } : new object[] { null, false, 0.0, 0.0, 0.0, 0.0 });
            UnityEngine.Object.Destroy(old);
        }
        if (Diagnostics || !Overlay.Logged)
            Api.Log("campaign ice map: overlay for " + built.DateKey + ": " + built.Raster.Width + " x " + built.Raster.Height + " at " + Num(built.Raster.Cell, "0.###") +
                    " degrees, " + built.Raster.IcePixels + " ice pixels (15 %+), " + built.Raster.HeavyPixels + " heavy pack (60 %+), built in " + Num(built.Ms, "0") + " ms off the main thread" +
                    (tex == null ? "; no ice in this theatre, nothing draped" : ""));
    }

    // Postfix on WeatherMapLayer.Detach(): DCM has let go of the weather slot.
    internal static void AfterLayerDetach(object __instance)
    {
        if (Stopped()) return;
        try { if (Overlay.Layer != null && ReferenceEquals(Overlay.Layer.Target, __instance)) Overlay.Release(); }
        catch (Exception ex) { StopMap("campaign ice map stopped; " + Unchanged, ex); }
    }

    // ---- Map: the hover readout ----

    private static int hoverLogged;
    // Postfix on WeatherMapLayer.ShowHover(MapBase map).
    internal static void AfterShowHover(object __instance, object __0)
    {
        if (mapStopped || __instance == null || __0 == null) return;
        try
        {
            var hover = (Noesis.Border)lHover.GetValue(__instance);
            var body = (Noesis.TextBlock)lHoverBody.GetValue(__instance);
            var at = (Noesis.Point?)lHoverAt.GetValue(__instance);
            if (hover == null || body == null || !at.HasValue || hover.Visibility != Noesis.Visibility.Visible) return;
            var args = new object[] { at.Value, Activator.CreateInstance(geoPositionType) };
            if (!(bool)tryToGeo.Invoke(__0, args)) return;
            double lat = (double)posLat.GetValue(args[1]);
            object bounds = lBounds.GetValue(__instance);
            double lon = bounds == null ? (double)posLon.GetValue(args[1]) : (double)continuous.Invoke(bounds, new object[] { (double)posLon.GetValue(args[1]) });
            object sim = lSim.GetValue(__instance), vm = lVm.GetValue(__instance);
            object nav = sim == null ? null : simNav.GetValue(sim);
            if (vm == null || nav == null) return;
            string add = HoverText(lat, lon, (DateTime)shownUtc.Invoke(vm, null), (bool)isWater.Invoke(nav, new[] { Activator.CreateInstance(geoType, lat, lon) }));
            if (add == null) return;
            body.Text = string.IsNullOrEmpty(body.Text) ? add : body.Text + "\n" + add;
            if (hoverLogged++ == 0 || Diagnostics && hoverLogged <= 5)
                Api.Log("campaign ice map: hover readout at " + Num(lat, "0.00") + ", " + Num(lon, "0.00") + ": " + add.Replace("\n", " | "));
        }
        catch (Exception ex) { StopMap("campaign ice map stopped; " + Unchanged, ex); }
    }

    internal static string HoverText(double lat, double lon, DateTime utc, bool water)
    {
        double c = SeaIceModel.Concentration(lat, lon, utc);
        string line = CampaignIceStyle.HoverLine(c, water);
        if (line == null) return null;
        string effect = CampaignIceStyle.HoverEffect(c, water);
        return effect == null ? line : line + "\n" + effect;
    }

    // ---- Movement ----

    // One per group (ConditionalWeakTable on the TaskForce): what the ice did
    // on the last pass, and the cache of the ice work. Percent, Factor and
    // Beset are worked out again only when the day, the group's 0.05-degree
    // tile (SeaIceTileCache.Key), its hulls or the catalogue change.
    internal sealed class Held
    {
        internal bool Binds, Beset, CachedBeset;
        internal double Knots, Percent, Factor = 1.0, Capability, Own;
        internal long Hour = long.MinValue;
        internal int DayKey = int.MinValue, ShipCount = -1, ShipHash;
        internal long Tile = long.MinValue;
        internal object Catalog;
        internal int Refreshes;
    }
    internal static readonly ConditionalWeakTable<object, Held> Groups = new ConditionalWeakTable<object, Held>();
    private static readonly ConditionalWeakTable<object, Held>.CreateValueCallback NewHeld = _ => new Held();
    private static readonly Dictionary<string, bool> submarines = new Dictionary<string, bool>(StringComparer.Ordinal);
    private static bool capabilityFailed;
    internal static long Passes, GroupPasses;

    // Postfix on WeatherEffects.UpdateCaps(). StepTo runs UpdateCaps twice a
    // step (WeatherEffects.Update, then before Movement) and DCM rewrites
    // every WeatherKnots each time, so each pass applies the ice again; the
    // second one finds every group's ice work in its cache.
    internal static void AfterUpdateCaps(object __instance)
    {
        if (moveStopped || __instance == null) return;
        try
        {
            object state = effState.GetValue(__instance);
            if (state == null) return;
            object catalog = effCatalog.GetValue(__instance);
            DateTime now = (DateTime)stateNow.GetValue(state);
            var list = (IList)stateTaskForces.GetValue(state);
            if (list == null) return;
            Passes++;
            for (int i = 0; i < list.Count; i++)
                if (list[i] != null) Apply(list[i], now, catalog);
        }
        catch (Exception ex) { StopMovement("campaign ice movement stopped; Dynamic Campaign Mod's movement unchanged", ex); }
    }

    internal static bool IsSubmarine(string ini, object catalog)
    {
        if (string.IsNullOrEmpty(ini)) return false;
        lock (submarines) if (submarines.TryGetValue(ini, out bool known)) return known;
        bool sub;
        try { sub = catalog != null ? fIsSubmarine(catalog, ini) : fIsSubmarineIni(ini); }
        catch { sub = fIsSubmarineIni(ini); }
        lock (submarines) submarines[ini] = sub;
        return sub;
    }

    // The ceiling's base: what the group can make (DCM's Logistics.SpeedOf,
    // the speed the AI's ClosingHours and Hold use), or without a catalogue
    // the ordered speed.
    private static double CapabilityOf(object tf, object catalog)
    {
        if (catalog != null && !capabilityFailed)
        {
            try { return fCapability(tf, catalog); }
            catch (Exception ex)
            {
                capabilityFailed = true;
                Api.LogFailure("campaign ice movement: Logistics.SpeedOf failed; the ice cap uses the ordered speed from now on", ex);
            }
        }
        return fOwn(tf);
    }

    private static int HashOf(IList ships)
    {
        int h = 17;
        for (int i = 0; i < ships.Count; i++) h = h * 31 + RuntimeHelpers.GetHashCode(ships[i]);
        return h;
    }

    // One group after DCM's UpdateCaps wrote its WeatherKnots.
    internal static void Apply(object tf, DateTime now, object catalog)
    {
        GroupPasses++;
        var held = Groups.GetValue(tf, NewHeld);
        held.Binds = false; held.Beset = false;
        double lat = fLat(tf);
        if (!(Math.Abs(lat) >= 39.9)) { held.Percent = 0; return; } // SeaIceTileCache: no ice there (NaN too)
        if (!fAtSea(tf)) return;
        var ships = fShips(tf);
        if (ships == null || ships.Count == 0) return;
        double lon = fLon(tf);
        int day = SeaIceTileCache.DateKeyOf(now);
        long tile = SeaIceTileCache.Key(lat, lon);
        int count = ships.Count, hash = HashOf(ships);
        if (day != held.DayKey || tile != held.Tile || count != held.ShipCount || hash != held.ShipHash || !ReferenceEquals(catalog, held.Catalog))
        {
            double pc = Tiles.Percent(lat, lon, now);
            double factor = 1.0;
            bool beset = false;
            if (IceRules.Access(pc, 0) != IceAccess.Open) // "none" is the strictest class
            {
                var caps = new int[count];
                for (int i = 0; i < count; i++)
                {
                    object hull = ships[i];
                    string ini = hull == null ? null : fIni(hull);
                    caps[i] = IsSubmarine(ini, catalog) ? -1 : IceRules.CapabilityOf(ini);
                }
                factor = CampaignIceSpeed.GroupFactor(pc, caps);
                beset = CampaignIceSpeed.GroupBeset(pc, caps);
            }
            held.Percent = pc; held.Factor = factor; held.CachedBeset = beset;
            held.DayKey = day; held.Tile = tile; held.ShipCount = count; held.ShipHash = hash; held.Catalog = catalog;
            held.Refreshes++;
        }
        double c = held.Percent, f = held.Factor;
        bool groupBeset = held.CachedBeset;
        if (f >= 1) return;
        double full = CapabilityOf(tf, catalog);
        double weather = fWeather(tf);
        double cap = CampaignIceSpeed.Cap(weather, full, f, out bool binds);
        held.Capability = full;
        if (binds)
        {
            fSetWeather(tf, cap);
            held.Binds = true; held.Knots = cap; held.Beset = groupBeset;
        }
        long hour = now.Ticks / TimeSpan.TicksPerHour;
        if (Diagnostics && hour != held.Hour)
        {
            held.Hour = hour;
            held.Own = fOwn(tf);
            Api.Log("campaign ice @ " + now.ToString("yyyy-MM-dd HH:mm", CultureInfo.InvariantCulture) + ": " + (string)moverName.GetValue(tf) +
                    " at " + Num(lat, "0.00") + ", " + Num(lon, "0.00") + ": ice " + Num(c, "0") + " % (" + CampaignIceStyle.Category(c) + "), factor " + Num(f, "0.0#") +
                    (groupBeset ? " (beset)" : "") + ", full speed " + Num(full) + " kn, ordered " + Num(held.Own) + " kn, weather cap " + (weather > 0 ? Num(weather) + " kn" : "none") +
                    " -> " + (binds ? Num(cap) + " kn (ice)" : "unchanged"));
        }
    }

    // The ice record still stands: DCM has not rewritten the cap since.
    private static bool IceHolds(object tf) =>
        taskForceType.IsInstanceOfType(tf) && Groups.TryGetValue(tf, out var held) && held.Binds && fWeather(tf) == held.Knots;

    // Postfix on Movement.SpeedText(Mover).
    internal static void AfterSpeedText(object __0, ref string __result)
    {
        if (moveStopped || __0 == null || __result == null) return;
        try
        {
            if (IceHolds(__0)) __result = CampaignIceSpeed.Text(__result, true);
        }
        catch (Exception ex) { StopMovement("campaign ice movement stopped; Dynamic Campaign Mod's movement unchanged", ex); }
    }

    // Postfix on FleetViewModel.Line(TaskForce, long): the fleet list formats
    // an out-of-fuel group's speed itself ("{0:0} kn (out of fuel, heavy
    // seas)" when held), without SpeedText.
    internal static void AfterFleetLine(object __0, ref string __result)
    {
        if (moveStopped || __0 == null || __result == null) return;
        try
        {
            if (IceHolds(__0)) __result = CampaignIceSpeed.Text(__result, true);
        }
        catch (Exception ex) { StopMovement("campaign ice movement stopped; Dynamic Campaign Mod's movement unchanged", ex); }
    }
}
