using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.Linq;
using System.Reflection;

namespace Sest.RuntimeFixes;

// Local battle weather, first slice: in a Dynamic Campaign Mod battle whose
// campaign has placed storms (sest-weather.json, WorldStorms), the weather
// the player sees follows where they look. Only in a battle whose written
// weather is the model's own: at the battle start BattlePlan.Weather must be
// WeatherModel.Battle(Engagement.Point, Engagement.At) field for field, and
// BattlePlan.TestBattle false (DCM's Battle AI tests, TestBattles.Build, fix
// their weather at scattered cloud and sea state 2); any other battle keeps
// its own weather, with one log line saying why. Every 2 s real time the view point
// (the unit the camera is attached to, else the free camera's focus) is
// sampled from the campaign's own DCM weather model at the battle time
// (WeatherModel.For(state).Battle(point, utc): the same At(...).ToBattle()
// the battle's [Environment] was written from, at 10-minute steps of battle
// time counted from the exact Engagement.At), and the result reaches the
// game's one global weather through the setters Trigger.TryActionTrigger
// uses, with the hysteresis of LocalWeatherPolicy.cs:
// - sea state: Environment.setSeaState (sets the Ceto spectrum), whole sea
//   states only, at most one change per 25 s and only after the view has
//   stayed in the new weather 5 s;
// - wind direction: CloudsManager.set_CurrentWindDirection, then
//   DynamicSky.ForceUpdate, as often;
// - rain, thunder (IsLightning), snow, fog: Environment.set_Is*, each at
//   most once per 20 s;
// - clouds: held at the battle's own [Environment] value (changeCloudsCoverage
//   writes Session._missionClouds, which saves and CloudsManager.init read).
// The mission's own weather is the baseline: SaveLoadManager.WriteMissionToFile
// writes it (a prefix puts the baseline in the fields with the plain setters,
// a finalizer puts the view weather back), and it is restored visibly when
// the battle ends, the campaign loses its placed storms, or the feature stops.
// A mission trigger's Set Weather becomes the baseline: a postfix on
// Trigger.TryActionTrigger adopts every channel the trigger set (its
// _setSeaState ... _setFog tuples with Item1 true), even one set to the value
// the view had already applied; any other outside change is adopted by
// comparing the game against what SEST last applied, at every tick, save and
// restore. Saves and the restore diff the baseline against what the game
// holds (Environment/CloudsManager read back), not a cached copy.
// The game holds ONE weather, so everything that reads it (sensors, ship
// motion, flight decks, DCM's battle AI through BattleSession.ReadEnvironment)
// sees the view's weather; DCM's AI is not changed here.
// LocalWeatherView=0 under [Runtime] leaves it out; WorldStormsDiagnostics=1
// adds a view line every 10 s. Main thread only (a GameMain.Update postfix).
internal static class LocalWeatherView
{
    private const string HarmonyId = "io.github.sest-hobby.world-storms.local-weather";
    internal const double TickSeconds = 2;
    internal const double ReportSeconds = 10;
    private const string Off = "the battle keeps its own weather";

    private static bool bound, installed, stopped;
    private static double Now => (double)Stopwatch.GetTimestamp() / Stopwatch.Frequency;

    // Sea Power 0.9.3 (Seapower-Scripts aae79728).
    private static Type envType, cloudsType, skyType, renderType, sceneType, objectType, geoType, windType;
    private static MethodInfo envExists, envInstance, cloudsExists, cloudsInstance, skyExists, skyInstance, renderExists, renderInstance, sceneExists, sceneInstance;
    private static MethodInfo setSeaState, setSeaStateField, getSeaState, getRaining, setRaining, getLightning, setLightning, getSnowing, setSnowing, getFog, setFog, getClouds;
    private static MethodInfo getWind, setWind, forceUpdate, loadingDone, attached, selected, renderUnity, unitGeo, unitName, toLongLat, gameUpdate, writeMission, tryAction;
    private static FieldInfo centerTile, geoLat, geoLon;
    // Trigger's Set Weather actions: (bool set, value) tuples, and each tuple's Item1.
    private static FieldInfo tSea, tWind, tRain, tThunder, tSnow, tFog, tSeaSet, tWindSet, tRainSet, tThunderSet, tSnowSet, tFogSet;
    // Dynamic Campaign Mod 1.0.2 (18a2416e).
    private static MethodInfo modelBattle;
    private static ConstructorInfo geoPoint;
    private static FieldInfo bSeaState, bWindFrom, bWindKnots, bClouds, bRain, bSnow, bFog, bThunder, bTyphoon, bStorm, planTest, planWeather;

    // One battle.
    private static LocalWeatherController controller;
    private static GameWeather weather;
    private static int battleId = int.MinValue, quietBattle = int.MinValue;
    // The battle (its Engagement) found not to have the model's own weather.
    private static object offEngagement;
    private static double nextTick, nextReport;
    private static string heldClouds;

    private static void Member(string name, bool ok)
    {
        if (WorldStorms.Diagnostics) Api.Log("world storms local weather bind: " + name + (ok ? " ok" : " MISSING"));
        if (!ok) throw new MissingMemberException("captured " + name);
    }
    private static MethodInfo M(Type t, string name, Type returns, bool isStatic, params Type[] args)
    {
        var m = t.GetMethod(name, Api.All, null, args, null);
        Member(t.Name + "." + name + "(" + string.Join(", ", args.Select(x => x.Name)) + ") : " + returns.Name, m != null && m.ReturnType == returns && m.IsStatic == isStatic);
        return m;
    }
    private static FieldInfo F(Type t, string name, Type expected, bool isStatic = false)
    {
        var f = t.GetField(name, Api.All);
        Member(t.Name + "." + name + " : " + expected.Name, f != null && f.IsStatic == isStatic && f.FieldType == expected);
        return f;
    }
    private static void Singleton(Assembly game, Type t, out MethodInfo exists, out MethodInfo instance)
    {
        var s = Api.Type(game, "SeaPower.Singleton`1").MakeGenericType(t);
        exists = M(s, "InstanceExists", typeof(bool), true, typeof(bool));
        instance = M(s, "get_Instance", t, true);
    }

    // Every member, before anything is installed. False (one log line) on any mismatch.
    internal static bool Bind(Assembly game)
    {
        try
        {
            WorldStorms.BindBattle(game);
            Type T(string n) => Api.Type(game, n);
            envType = T("SeaPower.Environment");
            cloudsType = T("SeaPower.CloudsManager");
            skyType = T("SeaPower.DynamicSky");
            renderType = T("SeaPower.RenderPosition");
            sceneType = T("SeaPower.SceneCreator");
            objectType = T("SeaPower.ObjectBase");
            geoType = T("SeaPower.GeoPosition");
            windType = T("SeaPower.CloudsManager+WindDirection");
            Member("CloudsManager.WindDirection is the enum N NE E SE S SW W NW (0..7)", windType.IsEnum &&
                LocalWeatherPolicy.WindPoints.Select((n, i) => Enum.IsDefined(windType, n) && Convert.ToInt32(Enum.Parse(windType, n)) == i).All(x => x) &&
                Enum.GetNames(windType).Length == 8);
            Singleton(game, envType, out envExists, out envInstance);
            Singleton(game, cloudsType, out cloudsExists, out cloudsInstance);
            Singleton(game, skyType, out skyExists, out skyInstance);
            Singleton(game, renderType, out renderExists, out renderInstance);
            Singleton(game, sceneType, out sceneExists, out sceneInstance);

            setSeaState = M(envType, "setSeaState", typeof(void), false, typeof(int));
            setSeaStateField = M(envType, "set_SeaState", typeof(void), false, typeof(int));
            getSeaState = M(envType, "get_SeaState", typeof(int), false);
            getRaining = M(envType, "get_IsRaining", typeof(bool), false);
            setRaining = M(envType, "set_IsRaining", typeof(void), false, typeof(bool));
            getLightning = M(envType, "get_IsLightning", typeof(bool), false);
            setLightning = M(envType, "set_IsLightning", typeof(void), false, typeof(bool));
            getSnowing = M(envType, "get_IsSnowing", typeof(bool), false);
            setSnowing = M(envType, "set_IsSnowing", typeof(void), false, typeof(bool));
            getFog = M(envType, "get_IsFog", typeof(bool), false);
            setFog = M(envType, "set_IsFog", typeof(void), false, typeof(bool));
            getClouds = M(envType, "get_CloudsCoverage", typeof(string), false);
            getWind = M(cloudsType, "get_CurrentWindDirection", windType, false);
            setWind = M(cloudsType, "set_CurrentWindDirection", typeof(void), false, windType);
            forceUpdate = M(skyType, "ForceUpdate", typeof(void), false);
            loadingDone = M(sceneType, "get_IsLoadingDone", typeof(bool), false);

            attached = M(renderType, "get_IsCameraAttachedToTarget", typeof(bool), false);
            selected = M(renderType, "getSelectedObject", objectType, false);
            var utils = T("SeaPower.Utils");
            toLongLat = utils.GetMethods(Api.All).SingleOrDefault(m => m.Name == "worldPositionFromUnityToLongLat" && m.IsStatic && m.ReturnType == geoType && m.GetParameters().Length == 2);
            Member("Utils.worldPositionFromUnityToLongLat(Vector3, Vector2) : GeoPosition", toLongLat != null &&
                toLongLat.GetParameters()[0].ParameterType.FullName == "UnityEngine.Vector3" && toLongLat.GetParameters()[1].ParameterType.FullName == "UnityEngine.Vector2");
            var vector3 = toLongLat.GetParameters()[0].ParameterType;
            renderUnity = M(renderType, "getUnityPosition", vector3, false);
            centerTile = F(T("SeaPower.Globals"), "_currentCenterTile", toLongLat.GetParameters()[1].ParameterType, true);
            unitGeo = M(objectType, "getGeoPosition", geoType, false);
            unitName = M(objectType, "getUIDAndName", typeof(string), false);
            geoLat = F(geoType, "_latitude", typeof(double));
            geoLon = F(geoType, "_longitude", typeof(double));
            gameUpdate = M(T("SeaPower.GameMain"), "Update", typeof(void), false);
            var trigger = T("SeaPower.Trigger");
            tryAction = M(trigger, "TryActionTrigger", typeof(bool), false);
            FieldInfo Tuple(string name, Type value, out FieldInfo set)
            {
                var f = F(trigger, name, typeof(ValueTuple<,>).MakeGenericType(typeof(bool), value));
                set = f.FieldType.GetField("Item1");
                Member("Trigger." + name + ".Item1 : Boolean", set != null && set.FieldType == typeof(bool));
                return f;
            }
            tSea = Tuple("_setSeaState", typeof(int), out tSeaSet);
            tWind = Tuple("_setWindDirection", windType, out tWindSet);
            tRain = Tuple("_setRain", typeof(bool), out tRainSet);
            tThunder = Tuple("_setThunderstorm", typeof(bool), out tThunderSet);
            tSnow = Tuple("_setSnow", typeof(bool), out tSnowSet);
            tFog = Tuple("_setFog", typeof(bool), out tFogSet);
            var saveTypeEnum = T("SeaPower.SaveLoadManager+SaveType");
            writeMission = M(T("SeaPower.SaveLoadManager"), "WriteMissionToFile", typeof(string), true, saveTypeEnum, typeof(string), typeof(bool), typeof(string));

            var dcm = WorldStorms.DcmAssembly;
            const string sim = "DynamicCampaignMod.Core.Sim.";
            var model = Api.Type(dcm, sim + "WeatherModel");
            var point = Api.Type(dcm, "DynamicCampaignMod.Core.Geo.GeoPoint");
            var battle = Api.Type(dcm, sim + "BattleWeather");
            modelBattle = M(model, "Battle", battle, false, point, typeof(DateTime));
            geoPoint = point.GetConstructor(Api.All, null, new[] { typeof(double), typeof(double) }, null);
            Member("GeoPoint.ctor(Double lat, Double lon)", geoPoint != null && geoPoint.GetParameters().Select(p => p.Name).SequenceEqual(new[] { "lat", "lon" }));
            bSeaState = F(battle, "SeaState", typeof(int)); bWindFrom = F(battle, "WindFrom", typeof(string)); bWindKnots = F(battle, "WindKnots", typeof(int));
            bClouds = F(battle, "Clouds", typeof(string)); bRain = F(battle, "Rain", typeof(bool)); bSnow = F(battle, "Snow", typeof(bool));
            bFog = F(battle, "Fog", typeof(bool)); bThunder = F(battle, "Thunderstorm", typeof(bool)); bTyphoon = F(battle, "Typhoon", typeof(bool));
            bStorm = F(battle, "Storm", typeof(string));
            var plan = Api.Type(dcm, "DynamicCampaignMod.Core.State.BattlePlan");
            planTest = F(plan, "TestBattle", typeof(bool));
            planWeather = F(plan, "Weather", battle);
            bound = true;
            if (WorldStorms.Diagnostics) Api.Log("world storms local weather bind: all members of Sea Power 0.9.3 and Dynamic Campaign Mod 1.0.2 bound");
            return true;
        }
        catch (Exception ex)
        {
            bound = false;
            Stop("world storms local weather unavailable; " + Off, ex);
            return false;
        }
    }

    internal static void Install(Assembly game)
    {
        if (installed || stopped || game == null) return;
        if (!Bind(game)) return;
        try
        {
            Api.Postfix(gameUpdate, typeof(LocalWeatherView), nameof(Tick), HarmonyId);
            Api.Hooks(writeMission, typeof(LocalWeatherView), nameof(BeforeSave), null, HarmonyId, nameof(AfterSave));
            Api.Postfix(tryAction, typeof(LocalWeatherView), nameof(AfterTrigger), HarmonyId);
            installed = true;
            Api.Log("world storms local weather installed: in Dynamic Campaign Mod battles of campaigns with placed storms, sea state, wind, rain, thunder, snow and fog follow the camera (clouds stay the battle's own); saves keep the battle's own weather; mission triggers' weather becomes the battle's own" +
                    (WorldStorms.Diagnostics ? "; diagnostics on" : ""));
        }
        catch (Exception ex) { Stop("world storms local weather unavailable; " + Off, ex); }
    }

    // Never throws. The baseline goes back first when a battle is running.
    private static void Stop(string label, Exception ex)
    {
        bool first = !stopped;
        stopped = true;
        try { End("the feature stopped"); } catch { }
        if (first) Api.LogFailure(label, ex);
    }

    private static string Num(double v, string f = "0.00") => v.ToString(f, CultureInfo.InvariantCulture);
    private static string LatLon(double lat, double lon) =>
        Num(Math.Abs(lat)) + (lat < 0 ? "S " : "N ") + Num(Math.Abs(lon)) + (lon < 0 ? "W" : "E");

    // The game's weather, through the setters a mission trigger uses.
    internal sealed class GameWeather : IViewWeatherTarget
    {
        internal readonly object Env, Clouds;
        internal GameWeather(object env, object clouds) { Env = env; Clouds = clouds; }

        public ViewWeather Read() => new ViewWeather
        {
            SeaState = (int)getSeaState.Invoke(Env, null),
            Rain = (bool)getRaining.Invoke(Env, null),
            Lightning = (bool)getLightning.Invoke(Env, null),
            Snow = (bool)getSnowing.Invoke(Env, null),
            Fog = (bool)getFog.Invoke(Env, null),
            Wind = getWind.Invoke(Clouds, null).ToString(),
        };

        private object Wind(string name) => Enum.Parse(windType, name);

        // Trigger.TryActionTrigger's order: sea state, wind, rain, lightning,
        // snow, fog, then DynamicSky.ForceUpdate when the wind changed.
        public void Apply(ViewWeather w, IList<ViewChannel> changed)
        {
            if (changed.Contains(ViewChannel.Sea)) setSeaState.Invoke(Env, new object[] { w.SeaState });
            if (changed.Contains(ViewChannel.Wind)) setWind.Invoke(Clouds, new[] { Wind(w.Wind) });
            if (changed.Contains(ViewChannel.Rain)) setRaining.Invoke(Env, new object[] { w.Rain });
            if (changed.Contains(ViewChannel.Lightning)) setLightning.Invoke(Env, new object[] { w.Lightning });
            if (changed.Contains(ViewChannel.Snow)) setSnowing.Invoke(Env, new object[] { w.Snow });
            if (changed.Contains(ViewChannel.Fog)) setFog.Invoke(Env, new object[] { w.Fog });
            if (changed.Contains(ViewChannel.Wind) && (bool)skyExists.Invoke(null, new object[] { false }))
                forceUpdate.Invoke(skyInstance.Invoke(null, null), null);
        }

        // Plain setters only: no Ceto spectrum, no sky update (a save).
        public void WriteFields(ViewWeather w)
        {
            setSeaStateField.Invoke(Env, new object[] { w.SeaState });
            setRaining.Invoke(Env, new object[] { w.Rain });
            setLightning.Invoke(Env, new object[] { w.Lightning });
            setSnowing.Invoke(Env, new object[] { w.Snow });
            setFog.Invoke(Env, new object[] { w.Fog });
            setWind.Invoke(Clouds, new[] { Wind(w.Wind) });
        }
    }

    // DCM's battle weather at a point and time, as the view target.
    internal static ViewWeather Sample(object model, double lat, double lon, DateTime utc, string held, ViewWeather baseline, out string described)
    {
        object w = modelBattle.Invoke(model, new[] { geoPoint.Invoke(new object[] { lat, lon }), (object)DateTime.SpecifyKind(utc, DateTimeKind.Utc) });
        int ss = (int)bSeaState.GetValue(w);
        bool rain = (bool)bRain.GetValue(w), thunder = (bool)bThunder.GetValue(w), snow = (bool)bSnow.GetValue(w), fog = (bool)bFog.GetValue(w);
        string from = bWindFrom.GetValue(w) as string, storm = bStorm.GetValue(w) as string;
        var flags = new List<string>();
        if (rain) flags.Add("Rain");
        if (snow) flags.Add("Snow");
        if (fog) flags.Add("Fog");
        if (thunder) flags.Add("Thunderstorm");
        described = "SeaState=" + ss + " WindFrom=" + (from ?? "?") + " " + bWindKnots.GetValue(w) + " kn Weather=" + (flags.Count == 0 ? "(none)" : string.Join(",", flags)) +
                    " Clouds=" + (bClouds.GetValue(w) ?? "?") + (string.IsNullOrEmpty(storm) ? "" : " storm " + storm);
        return LocalWeatherPolicy.Target(ss, rain, thunder, snow, fog, from, held, baseline);
    }

    // The view point: the unit the camera is attached to, else the free
    // camera's focus (RenderPosition's transform, converted as RenderPosition
    // itself does: Utils.worldPositionFromUnityToLongLat with
    // Globals._currentCenterTile).
    internal static bool ViewPoint(out double lat, out double lon, out string source)
    {
        lat = lon = 0; source = null;
        if (!(bool)renderExists.Invoke(null, new object[] { false })) return false;
        object rp = renderInstance.Invoke(null, null);
        if (rp == null) return false;
        object unit = selected.Invoke(rp, null);
        object geo;
        if ((bool)attached.Invoke(rp, null) && unit != null)
        {
            geo = unitGeo.Invoke(unit, null);
            string name = null;
            try { name = unitName.Invoke(unit, null) as string; } catch { }
            source = "unit " + (string.IsNullOrEmpty(name) ? "(unnamed)" : name);
        }
        else
        {
            geo = toLongLat.Invoke(null, new[] { renderUnity.Invoke(rp, null), centerTile.GetValue(null) });
            source = "camera";
        }
        lat = (double)geoLat.GetValue(geo);
        lon = (double)geoLon.GetValue(geo);
        return !double.IsNaN(lat) && !double.IsNaN(lon);
    }

    private static bool Exists(MethodInfo exists) => (bool)exists.Invoke(null, new object[] { false });

    // Postfix on GameMain.Update (main thread), every TickSeconds.
    internal static void Tick()
    {
        if (!installed || stopped) return;
        double now = Now;
        if (now < nextTick) return;
        nextTick = now + TickSeconds;
        try { Step(now); }
        catch (Exception ex) { Stop("world storms local weather stopped; " + Off, ex); }
    }

    private static void Step(double now)
    {
        object engagement = WorldStorms.BattleEngagement();
        if (engagement == null) { End("the battle ended"); return; }
        if (!Exists(sceneExists) || !(bool)loadingDone.Invoke(sceneInstance.Invoke(null, null), null) || !Exists(envExists) || !Exists(cloudsExists)) return;
        object env = envInstance.Invoke(null, null), clouds = cloudsInstance.Invoke(null, null);
        WorldStorms.EngagementOf(engagement, out int id, out double cLat, out double cLon, out DateTime utc);
        if (controller != null && (id != battleId || !ReferenceEquals(env, weather.Env) || !ReferenceEquals(clouds, weather.Clouds)))
            End(id != battleId ? "another battle started" : "the battle's scene was replaced");
        object model = WorldStorms.BattleModel(out string source);
        if (!WorldStorms.HasPlacedStorms(model))
        {
            if (controller != null) End("the campaign's placed storms are gone");
            if (quietBattle != id)
            {
                quietBattle = id;
                Api.Log("world storms local weather: battle " + id + ": the campaign has no placed storms (" + StormSidecar.FileName + "); " + Off);
            }
            return;
        }
        if (controller == null)
        {
            if (ReferenceEquals(engagement, offEngagement)) return;
            string why = NotOwnWeather(WorldStorms.BattlePlan(), model, engagement);
            if (why != null)
            {
                offEngagement = engagement;
                Api.Log("world storms local weather: battle " + id + ": " + why + "; " + Off);
                return;
            }
            weather = new GameWeather(env, clouds);
            controller = new LocalWeatherController(weather);
            battleId = id;
            heldClouds = getClouds.Invoke(env, null) as string;
            nextReport = 0;
            Api.Log("world storms local weather: battle " + id + " at " + LatLon(cLat, cLon) + " " + utc.ToString("yyyy-MM-dd HH:mm'Z'", CultureInfo.InvariantCulture) +
                    " (" + WorldStorms.PlacedStormNames(model) + ", model from " + source + "): view weather on; baseline " + controller.Baseline + ", clouds held at " + (heldClouds ?? "?"));
        }
        if (!ViewPoint(out double lat, out double lon, out string from)) return;
        var at = LocalWeatherPolicy.SampleTime(WorldStorms.EngagementStart(engagement), utc);
        var target = Sample(model, lat, lon, at, heldClouds, controller.Baseline, out string sampled);
        var before = controller.Applied;
        var d = controller.Tick(now, target);
        if (controller.External != null) Api.Log("world storms local weather: " + controller.External);
        LocalWeatherGeo.OffsetNm(cLat, cLon, lat, lon, out double east, out double north);
        string where = from + " " + LatLon(lat, lon) + " (" + Num(east, "+0.0;-0.0") + " nm E, " + Num(north, "+0.0;-0.0") + " nm N of the battle centre)";
        if (d.Changed.Count > 0)
            Api.Log("world storms local weather: applied " + string.Join(", ", d.Changed.Select(c => Change(c, before, d.Applied))) + " at view " + where +
                    "; now " + d.Applied + (d.Held.Count == 0 ? "" : "; held " + string.Join("; ", d.Held)));
        if (WorldStorms.Diagnostics && now >= nextReport)
        {
            nextReport = now + ReportSeconds;
            Api.Log("world storms local weather: view " + where + ", battle " + utc.ToString("yyyy-MM-dd HH:mm'Z'", CultureInfo.InvariantCulture) + " (sampled " +
                    at.ToString("HH:mm'Z'", CultureInfo.InvariantCulture) + "): DCM " + sampled + "; target " + target + "; applied " + d.Applied +
                    "; baseline " + controller.Baseline + "; held " + (d.Held.Count == 0 ? "nothing" : string.Join("; ", d.Held)));
        }
    }

    // Null when the battle's written weather is the model's own; else why
    // the view stays off. plan: the DCM BattlePlan; the model's battle weather
    // is taken at Engagement.Point and the exact Engagement.At, as
    // Battles.WeatherOf did when it wrote the plan.
    internal static string NotOwnWeather(object plan, object model, object engagement)
    {
        if (plan == null) return "no battle plan";
        if ((bool)planTest.GetValue(plan))
            return "a Dynamic Campaign Mod Battle AI test battle (BattlePlan.TestBattle): its weather is the test's own fixed weather, not the campaign model's";
        object written = planWeather.GetValue(plan);
        if (written == null) return "the battle plan has no weather";
        object own = modelBattle.Invoke(model, new[] { WorldStorms.EngagementPoint(engagement), (object)WorldStorms.EngagementStart(engagement) });
        string diff = WeatherDiff(written, own);
        return diff == null ? null : "its written weather is not the campaign model's own at the Engagement point and time (" + diff + ")";
    }

    // The fields of two DCM BattleWeathers that differ ("SeaState 2 written, 8
    // model; Clouds ..."), or null when they are the same.
    internal static string WeatherDiff(object written, object own)
    {
        var diffs = new List<string>();
        foreach (var f in new[] { bSeaState, bWindFrom, bWindKnots, bClouds, bRain, bSnow, bFog, bThunder, bTyphoon, bStorm })
        {
            object a = f.GetValue(written), b = f.GetValue(own);
            if (!Equals(a, b)) diffs.Add(f.Name + " " + (a ?? "(none)") + " written, " + (b ?? "(none)") + " model");
        }
        return diffs.Count == 0 ? null : string.Join("; ", diffs);
    }

    internal static string Change(ViewChannel c, ViewWeather from, ViewWeather to)
    {
        switch (c)
        {
            case ViewChannel.Sea: return "sea state " + from.SeaState + " -> " + to.SeaState + " (setSeaState)";
            case ViewChannel.Wind: return "wind " + from.Wind + " -> " + to.Wind;
            case ViewChannel.Rain: return "rain " + (to.Rain ? "on" : "off");
            case ViewChannel.Lightning: return "thunder " + (to.Lightning ? "on" : "off");
            case ViewChannel.Snow: return "snow " + (to.Snow ? "on" : "off");
            default: return "fog " + (to.Fog ? "on" : "off");
        }
    }

    // The battle's own weather back, visibly, when its scene is still the
    // one the view layer changed; then forget the battle.
    private static void End(string why)
    {
        var c = controller;
        if (c == null) return;
        controller = null;
        var w = weather;
        weather = null;
        bool live = Exists(envExists) && Exists(cloudsExists) &&
                    ReferenceEquals(envInstance.Invoke(null, null), w.Env) && ReferenceEquals(cloudsInstance.Invoke(null, null), w.Clouds);
        if (!live)
        {
            Api.Log("world storms local weather: battle " + battleId + " closed (" + why + "); its scene is gone, nothing to restore");
            return;
        }
        var put = c.Restore();
        if (c.External != null) Api.Log("world storms local weather: " + c.External);
        Api.Log("world storms local weather: battle " + battleId + " (" + why + "): baseline restored " + c.Baseline +
                (put.Count == 0 ? " (the game already held the baseline)" : " (" + string.Join(", ", put) + " put back)"));
    }

    // Prefix and finalizer on SaveLoadManager.WriteMissionToFile: the save
    // file gets the battle's own weather, the screen keeps the view's.
    internal static void BeforeSave(ref bool __state)
    {
        __state = false;
        try
        {
            if (controller == null || !Exists(envExists) || !ReferenceEquals(envInstance.Invoke(null, null), weather.Env)) return;
            // Swapped unless BeforeSave says otherwise, so a WriteFields that
            // throws partway is still undone by AfterSave.
            __state = true;
            __state = controller.BeforeSave();
            if (controller.External != null) Api.Log("world storms local weather: save: " + controller.External);
            if (__state) Api.Log("world storms local weather: save: the battle's own weather written (" + controller.Baseline + "), not the view's (" + controller.Applied + ")");
        }
        catch (Exception ex) { Api.LogFailure("world storms local weather: save baseline", ex); }
    }

    internal static Exception AfterSave(bool __state, Exception __exception)
    {
        if (__state)
        {
            try { controller?.AfterSave(true); }
            catch (Exception ex) { Api.LogFailure("world storms local weather: view weather after the save", ex); }
        }
        return __exception;
    }

    // Postfix on Trigger.TryActionTrigger (true when its actions ran, the
    // Set Weather ones included): every weather channel the trigger set is
    // the mission's weather now, adopted into the baseline at once, whatever
    // its value (comparing values cannot see a trigger that sets what the
    // view already applied).
    internal static void AfterTrigger(object __instance, bool __result)
    {
        try
        {
            if (!__result || __instance == null || controller == null || stopped) return;
            var set = TriggerChannels(__instance);
            if (set.Count == 0) return;
            if (!Exists(envExists) || !ReferenceEquals(envInstance.Invoke(null, null), weather.Env)) return;
            controller.Reconcile(set);
            if (controller.External != null) Api.Log("world storms local weather: " + controller.External);
        }
        catch (Exception ex) { Stop("world storms local weather stopped; " + Off, ex); }
    }

    // The channels a Trigger's Set Weather actions set (Item1 true), in the trigger order.
    internal static List<ViewChannel> TriggerChannels(object trigger)
    {
        var set = new List<ViewChannel>();
        void Add(FieldInfo tuple, FieldInfo item1, ViewChannel c) { if ((bool)item1.GetValue(tuple.GetValue(trigger))) set.Add(c); }
        Add(tSea, tSeaSet, ViewChannel.Sea);
        Add(tWind, tWindSet, ViewChannel.Wind);
        Add(tRain, tRainSet, ViewChannel.Rain);
        Add(tThunder, tThunderSet, ViewChannel.Lightning);
        Add(tSnow, tSnowSet, ViewChannel.Snow);
        Add(tFog, tFogSet, ViewChannel.Fog);
        return set;
    }
}
