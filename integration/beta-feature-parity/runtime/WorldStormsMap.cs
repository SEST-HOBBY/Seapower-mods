using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Text;

namespace Sest.RuntimeFixes;

// The "Weather" layer on the in-battle tactical map (WorldStormsMapLayer=1 in
// [Runtime], default on; needs WorldStorms=1). In a Dynamic Campaign Mod
// battle it draws every storm of the campaign's weather model at the battle
// time: placed storms (sest-weather.json) and DCM's own tropical cyclones and
// gales alike, because both are Actives of DCM's snapshot. Per storm: a centre
// marker with DCM's label and wind, the gale-force ring (DCM's GaleRadiusNm),
// the core ring (TrackPoint.R, the radius of maximum wind) and the track
// ahead to +1, +3, +6 and +12 h with time labels; hovering the map inside a
// storm shows a readout. It moves with the battle clock.
//
// Game API, as R.A.T.S. Topographic Map 1.7.0 uses it on Sea Power 0.9.3:
// - the Layers menu entry: a SeapowerUI.MapLayer made with its internal
//   .ctor(MapDisplayState, in GizmoLayerManager.Entry, bool) and added to
//   MapDisplayState.Tactical's Layers, LayersByName and LayersById, its menu
//   text set in the language dictionary under "maplayers<name>";
// - the map: a postfix on MapControl.RenderedLayer.OnRender gives the
//   rendering MapBase (MapPanel.ParentMap); the tactical one is the map whose
//   DataContext is Globals._mainGameViewModel.Map.DisplayMap;
// - drawing: a Noesis Canvas in the map's parent Panel, next to the map, as
//   Topographic Map's legend and readout (MapDecoration.TryAttach); geo to
//   view through MapBase.TryLocationToView, view to geo (hover) through
//   TryViewToGeoPosition, view to canvas through UIElement.TranslatePoint.
// Battle time: DCM's BattleSession.Plan.Engagement.At plus
// GameTime.missionElapsedTime (seconds of game time). The model:
// WeatherModel.For(CampaignSession.Sim.State), else the model For returned
// last. Every member is bound by reflection before anything is installed;
// any failure stops only this layer, with one log line.
internal static partial class WorldStorms
{
    private const string MapHarmonyId = HarmonyId + ".map-layer";
    internal const string LayerName = "SEST_WEATHER";
    internal const string LayerText = "Weather (storms, gale rings, forecast track)";
    internal const int LayerNumber = 610;
    private static bool mapWanted, mapBound, mapInstalled, mapStopped;
    private static Assembly dcm;

    private static MethodInfo tactical, layersByName, layersById, layersList, layerVisible, languageInstance, languageDictionary, dictionarySet;
    private static ConstructorInfo layerCtor, entryCtor;
    private static MethodInfo parentMap, tryToView, tryToGeo, rendered, gameUpdate, missionElapsed;
    private static FieldInfo mainGameViewModel, geoLat, geoLon, geoHeight;
    private static MethodInfo sceneMap, displayMap;
    private static Type geoType;
    private static MethodInfo battleActive, battlePlan, campaignSim, forState, galeRadius, systemDies;
    private static FieldInfo planEngagement, simState;

    private static object layer;
    private static WeakReference mapRef, lastRejected;
    private static readonly HashSet<string> rejectedKinds = new HashSet<string>(StringComparer.Ordinal);
    private static object overlay;
    private static double nextRegister, nextCollect, nextReport;
    private static int redraws, reportRedraws;
    private static DateTime collectedFor;
    private static object collectedModel;
    private static string modelSource = "none";
    internal static List<MapStorm> Shown = new List<MapStorm>();

    // Bind the map layer's members: the game's (Seapower-Scripts) and the rest
    // of DCM's. False (one log line) when any is missing; storms are unaffected.
    internal static bool BindMap(Assembly game)
    {
        try
        {
            if (!bound || dcm == null) throw new InvalidOperationException("Dynamic Campaign Mod is not bound");
            Type T(Assembly a, string n) => Api.Type(a, n);
            var displayState = T(game, "SeapowerUI.MapDisplayState");
            var mapLayer = T(game, "SeapowerUI.MapLayer");
            var entry = T(game, "SeapowerUI.GizmoLayerManager+Entry");
            var mapPanel = T(game, "MapControl.MapPanel");
            var mapBase = T(game, "MapControl.MapBase");
            var renderedLayer = T(game, "MapControl.RenderedLayer");
            var language = T(game, "SeaPower.LanguageResourceHandler");
            geoType = T(game, "SeaPower.GeoPosition");
            var point = typeof(Noesis.Point);
            tactical = M(displayState, "get_Tactical", displayState, true);
            layersByName = M(displayState, "get_LayersByName", typeof(IReadOnlyDictionary<,>).MakeGenericType(typeof(string), mapLayer), false);
            layersById = M(displayState, "get_LayersById", typeof(IReadOnlyDictionary<,>).MakeGenericType(typeof(int), mapLayer), false);
            layersList = M(displayState, "get_Layers", typeof(System.Collections.ObjectModel.ObservableCollection<>).MakeGenericType(mapLayer), false);
            layerVisible = M(mapLayer, "get_Visible", typeof(bool), false);
            layerCtor = mapLayer.GetConstructor(Api.All, null, new[] { displayState, entry.MakeByRefType(), typeof(bool) }, null);
            Member("MapLayer.ctor(MapDisplayState, in GizmoLayerManager.Entry, Boolean)", layerCtor != null);
            entryCtor = entry.GetConstructor(Api.All, null, new[] { typeof(int), typeof(string), typeof(bool) }, null);
            Member("GizmoLayerManager.Entry.ctor(Int32, String, Boolean)", entry.IsValueType && entryCtor != null);
            languageInstance = M(T(game, "SeaPower.Singleton`1").MakeGenericType(language), "get_Instance", language, true);
            var dictionary = T(game, "SeaPower.DictionaryWithFallbacks`2").MakeGenericType(typeof(string), typeof(string));
            languageDictionary = M(language, "get_LanguageDictionary", dictionary, false);
            dictionarySet = M(dictionary, "set_Item", typeof(void), false, typeof(string), typeof(string));
            parentMap = M(mapPanel, "get_ParentMap", mapBase, false);
            Member("MapBase extends MapPanel, a Noesis.Panel", mapPanel.IsAssignableFrom(mapBase) && typeof(Noesis.Panel).IsAssignableFrom(mapPanel));
            tryToView = M(mapBase, "TryLocationToView", typeof(bool), false, geoType, point.MakeByRefType());
            tryToGeo = M(mapBase, "TryViewToGeoPosition", typeof(bool), false, point, geoType.MakeByRefType());
            rendered = M(renderedLayer, "OnRender", typeof(void), false, typeof(Noesis.DrawingContext));
            Member("RenderedLayer extends MapPanel", mapPanel.IsAssignableFrom(renderedLayer));
            geoLat = F(geoType, "_latitude", typeof(double)); geoLon = F(geoType, "_longitude", typeof(double)); geoHeight = F(geoType, "_height", typeof(double));
            Member("GeoPosition is a value type", geoType.IsValueType);
            mainGameViewModel = T(game, "SeaPower.Globals").GetField("_mainGameViewModel", Api.All);
            var mainGame = T(game, "SeapowerUI.ViewModels.MainGameViewModel");
            var scene = T(game, "SeapowerUI.ViewModels.SceneMapViewModel");
            Member("Globals._mainGameViewModel : MainGameViewModel (static)", mainGameViewModel != null && mainGameViewModel.IsStatic && mainGameViewModel.FieldType == mainGame);
            sceneMap = M(mainGame, "get_Map", scene, false);
            displayMap = M(scene, "get_DisplayMap", T(game, "SeapowerUI.MapViewModel"), false);
            gameUpdate = M(T(game, "SeaPower.GameMain"), "Update", typeof(void), false);
            BindBattle(game);
            galeRadius = M(modelType, "GaleRadiusNm", typeof(double), true, systemType, pointType);
            systemDies = M(systemType, "get_Dies", typeof(DateTime), false);
            mapBound = true;
            if (Diagnostics) Api.Log("world storms map bind: all members of Sea Power's tactical map and Dynamic Campaign Mod's battle session bound");
            return true;
        }
        catch (Exception ex)
        {
            mapBound = false;
            StopMap("world storms map layer unavailable; the placed storms themselves are unchanged", ex);
            return false;
        }
    }

    // The battle session members the map layer and the local weather view
    // (LocalWeatherView.cs) share: the DCM battle, its Engagement and clock,
    // and the running campaign's weather model. Throws on a mismatch; binds
    // once.
    private static bool battleBound;
    internal static void BindBattle(Assembly game)
    {
        if (battleBound) return;
        if (!bound || dcm == null) throw new InvalidOperationException("Dynamic Campaign Mod is not bound");
        Type T(Assembly a, string n) => Api.Type(a, n);
        missionElapsed = M(T(game, "SeaPower.GameTime"), "get_missionElapsedTime", typeof(double), true);
        var session = T(dcm, "DynamicCampaignMod.Game.Battle.BattleSession");
        var plan = T(dcm, "DynamicCampaignMod.Core.State.BattlePlan");
        var engagement = T(dcm, "DynamicCampaignMod.Core.State.Engagement");
        var campaign = T(dcm, "DynamicCampaignMod.Game.Session.CampaignSession");
        var simType = T(dcm, "DynamicCampaignMod.Core.Sim.CampaignSim");
        var state = T(dcm, "DynamicCampaignMod.Core.State.CampaignState");
        battleActive = M(session, "get_Active", typeof(bool), true);
        battlePlan = M(session, "get_Plan", plan, true);
        planEngagement = F(plan, "Engagement", engagement);
        campaignSim = M(campaign, "get_Sim", simType, true);
        simState = F(simType, "State", state);
        forState = M(modelType, "For", modelType, true, state);
        battleBound = true;
    }

    internal static Assembly DcmAssembly => dcm;

    // The running DCM battle's Engagement, or null outside one.
    internal static object BattleEngagement()
    {
        if (!(bool)battleActive.Invoke(null, null)) return null;
        object plan = battlePlan.Invoke(null, null);
        return plan == null ? null : planEngagement.GetValue(plan);
    }

    // The running DCM battle's BattlePlan, or null outside one.
    internal static object BattlePlan() => (bool)battleActive.Invoke(null, null) ? battlePlan.Invoke(null, null) : null;

    // Engagement.Point (a DCM GeoPoint) and Engagement.At, exactly as
    // Battles.WeatherOf passes them to Weather.At for the battle's [Environment].
    internal static object EngagementPoint(object engagement) => ePoint.GetValue(engagement);
    internal static DateTime EngagementStart(object engagement) => (DateTime)eAt.GetValue(engagement);

    // Engagement.Id, Point and the battle UTC (Engagement.At + GameTime.missionElapsedTime).
    internal static void EngagementOf(object engagement, out int id, out double lat, out double lon, out DateTime utc)
    {
        id = (int)eId.GetValue(engagement);
        object centre = ePoint.GetValue(engagement);
        lat = (double)gLat.GetValue(centre);
        lon = (double)gLon.GetValue(centre);
        utc = StormMapGeometry.BattleUtc((DateTime)eAt.GetValue(engagement), (double)missionElapsed.Invoke(null, null));
    }

    // True when the model carries the campaign's placed storms (sest-weather.json).
    internal static bool HasPlacedStorms(object model)
    {
        if (model == null) return false;
        lock (gate) return !stopped && models.TryGetValue(model, out var held) && held.Set != null && held.Set.Systems.Length > 0;
    }

    internal static string PlacedStormNames(object model)
    {
        lock (gate)
            return models.TryGetValue(model, out var held) && held.Set != null ? string.Join(", ", held.Set.Specs.Select(s => s.Kind + " " + s.Name)) : "";
    }

    private static void StopMap(string label, Exception ex)
    {
        bool first = !mapStopped;
        mapStopped = true;
        try { (overlay as Overlay)?.Detach(); } catch { }
        overlay = null;
        if (first) Api.LogFailure(label, ex);
    }

    internal static void InstallMap(Assembly game)
    {
        if (!mapWanted || mapInstalled || mapStopped || game == null) return;
        if (!BindMap(game)) return;
        try
        {
            Api.Postfix(rendered, typeof(WorldStorms), nameof(AfterMapRender), MapHarmonyId);
            Api.Postfix(gameUpdate, typeof(WorldStorms), nameof(MapTick), MapHarmonyId);
            mapInstalled = true;
            Api.Log("world storms map layer installed: a \"Weather\" entry in the tactical map's Layers menu draws the campaign's storms in Dynamic Campaign Mod battles" +
                    (Diagnostics ? "; diagnostics on" : ""));
        }
        catch (Exception ex) { StopMap("world storms map layer unavailable; the placed storms themselves are unchanged", ex); }
    }

    // Postfix on MapControl.RenderedLayer.OnRender(DrawingContext): note the
    // map being drawn. Cheap; nothing is changed during the render.
    internal static void AfterMapRender(object __instance)
    {
        if (mapStopped || __instance == null) return;
        try
        {
            object map = parentMap.Invoke(__instance, null);
            if (map == null || ReferenceEquals(map, mapRef?.Target) || ReferenceEquals(map, lastRejected?.Target)) return;
            if (IsTactical(map)) { mapRef = new WeakReference(map); return; }
            lastRejected = new WeakReference(map);
            if (Diagnostics)
            {
                string kind = ((Noesis.FrameworkElement)map).DataContext?.GetType().FullName ?? "(none)";
                if (rejectedKinds.Add(kind)) Api.Log("world storms map: a rendered map with view model " + kind + " is not the tactical map; not drawn on");
            }
        }
        catch (Exception ex) { StopMap("world storms map layer stopped; the placed storms themselves are unchanged", ex); }
    }

    private static object TacticalViewModel()
    {
        object main = mainGameViewModel.GetValue(null);
        object scene = main == null ? null : sceneMap.Invoke(main, null);
        return scene == null ? null : displayMap.Invoke(scene, null);
    }

    private static bool IsTactical(object map)
    {
        object vm = TacticalViewModel();
        return vm != null && ReferenceEquals(((Noesis.FrameworkElement)map).DataContext, vm);
    }

    private static int layerFailures;
    private static void TryEnsureLayer()
    {
        try { EnsureLayer(); }
        catch (Exception ex)
        {
            if (++layerFailures >= 5) throw;
            if (Diagnostics) Api.LogFailure("world storms map: the Layers menu entry could not be added yet (try " + layerFailures + " of 5)", ex);
        }
    }

    // The Layers menu entry, once per game session (MapDisplayState.Tactical
    // lives for the session); adopted when it is already there.
    internal static void EnsureLayer()
    {
        if (layer != null) return;
        object state = tactical.Invoke(null, null);
        var byName = (IDictionary)layersByName.Invoke(state, null);
        var byId = (IDictionary)layersById.Invoke(state, null);
        if (byName.Contains(LayerName)) { layer = byName[LayerName]; return; }
        int number = LayerNumber;
        while (byId.Contains(number)) number++;
        object words = languageDictionary.Invoke(languageInstance.Invoke(null, null), null);
        dictionarySet.Invoke(words, new object[] { ("MapLayers" + LayerName).ToLowerInvariant(), LayerText });
        object e = entryCtor.Invoke(new object[] { number, LayerName, true });
        object created = layerCtor.Invoke(new[] { state, e, true });
        ((IList)layersList.Invoke(state, null)).Add(created);
        byName[LayerName] = created;
        byId[number] = created;
        layer = created;
        Api.Log("world storms map: layer \"" + LayerText + "\" added to the tactical map's Layers menu (#" + number + "), " +
                ((bool)layerVisible.Invoke(created, null) ? "on" : "off"));
    }

    private static object Geo(double lat, double lon)
    {
        object g = Activator.CreateInstance(geoType);
        geoLat.SetValue(g, lat);
        geoLon.SetValue(g, StormMapGeometry.NormalLon(lon));
        geoHeight.SetValue(g, 0.0);
        return g;
    }

    internal static bool ToView(object map, double lat, double lon, out double x, out double y)
    {
        var args = new object[] { Geo(lat, lon), new Noesis.Point(0, 0) };
        bool ok = (bool)tryToView.Invoke(map, args);
        var p = (Noesis.Point)args[1];
        x = p.X; y = p.Y;
        return ok;
    }

    internal static bool ToGeo(object map, double x, double y, out double lat, out double lon)
    {
        var args = new object[] { new Noesis.Point((float)x, (float)y), Activator.CreateInstance(geoType) };
        bool ok = (bool)tryToGeo.Invoke(map, args);
        lat = (double)geoLat.GetValue(args[1]);
        lon = (double)geoLon.GetValue(args[1]);
        return ok;
    }

    // The campaign's weather model in a battle, and where it came from.
    internal static object BattleModel(out string source)
    {
        object sim = campaignSim.Invoke(null, null);
        object state = sim == null ? null : simState.GetValue(sim);
        if (state != null) { source = "the running campaign"; return forState.Invoke(null, new[] { state }); }
        source = "the model Dynamic Campaign Mod used last";
        return LastModel;
    }

    // DCM's storms at a time, from the snapshot of that whole hour (one
    // snapshot per battle hour, so DCM's 24-entry cache is not churned), each
    // positioned at the exact time by WeatherSystem.At. Tropical systems and
    // any system with gale-force wind; Highs and weak Lows are left out.
    internal static List<MapStorm> Collect(object model, DateTime utc, double nearLat, double nearLon)
    {
        var result = new List<MapStorm>();
        object snap = snapshotAt.Invoke(model, new object[] { StormMapGeometry.Hour(utc) });
        if (snap == null) return result;
        object field = climate.GetValue(snap);
        foreach (object active in (IList)actives.GetValue(snap))
        {
            object sys = aSystem.GetValue(active);
            if (sys == null) continue;
            int kind = Convert.ToInt32(sKind.GetValue(sys));
            var born = (DateTime)sBorn.GetValue(sys);
            var dies = (DateTime)systemDies.Invoke(sys, null);
            if (utc < born || utc > dies) continue;
            object p = systemAt.Invoke(sys, new object[] { utc });
            double gale = (double)galeRadius.Invoke(null, new[] { sys, p });
            if (kind != 3 && gale <= 0) continue;
            double env = (double)pEnv.GetValue(p);
            var s = new MapStorm
            {
                Id = (string)sId.GetValue(sys),
                Label = (string)label.Invoke(null, new[] { sys, p, field }),
                Tropical = kind == 3,
                Lat = (double)pLat.GetValue(p),
                Lon = StormMapGeometry.NormalLon((double)pLon.GetValue(p)),
                WindKn = (double)pVmax.GetValue(p) * (kind == 3 ? env : 1),
                GaleNm = gale,
                CoreNm = (double)pR.GetValue(p),
                ReachNm = (double)reachNm.Invoke(sys, new[] { p }),
            };
            s.Placed = s.Id != null && s.Id.StartsWith("sest-", StringComparison.Ordinal);
            foreach (double h in StormMapGeometry.LeadHours)
            {
                var t = utc.AddHours(h);
                if (t > dies) break;
                object q = systemAt.Invoke(sys, new object[] { t });
                s.Leads.Add(new MapStormLead
                {
                    Hours = h, Lat = (double)pLat.GetValue(q), Lon = StormMapGeometry.NormalLon((double)pLon.GetValue(q)),
                    WindKn = (double)pVmax.GetValue(q) * (kind == 3 ? (double)pEnv.GetValue(q) : 1)
                });
            }
            if (StormMapGeometry.Near(s, nearLat, nearLon)) result.Add(s);
        }
        return result;
    }

    // Postfix on GameMain.Update: everything the layer changes happens here,
    // on the game's main thread, at most once a frame.
    internal static void MapTick()
    {
        if (!mapInstalled || mapStopped) return;
        try
        {
            double now = Now;
            object map = mapRef?.Target;
            var view = overlay as Overlay;
            bool battle = (bool)battleActive.Invoke(null, null);
            // The menu entry once the game's tactical map exists (a battle, or
            // a rendered tactical map): MapDisplayState.Tactical reads the
            // game's options when it is first made, so not at start-up.
            if (layer == null && (battle || map != null) && now >= nextRegister) { nextRegister = now + 2; TryEnsureLayer(); }
            object plan = battle ? battlePlan.Invoke(null, null) : null;
            object engagement = plan == null ? null : planEngagement.GetValue(plan);
            if (engagement == null || map == null || layer == null)
            {
                view?.Show(false);
                return;
            }
            if (view == null || !ReferenceEquals(view.Map, map))
            {
                view?.Detach();
                overlay = view = Overlay.Attach(map);
                if (view == null) return;
                Shown = new List<MapStorm>();
                collectedFor = default;
                if (Diagnostics) Api.Log("world storms map: drawing on the tactical map (host " + view.HostName + ")");
            }
            bool on = (bool)layerVisible.Invoke(layer, null);
            view.Show(on);
            if (!on) return;
            object centre = ePoint.GetValue(engagement);
            double cLat = (double)gLat.GetValue(centre), cLon = (double)gLon.GetValue(centre);
            var utc = StormMapGeometry.BattleUtc((DateTime)eAt.GetValue(engagement), (double)missionElapsed.Invoke(null, null));
            bool changed = false;
            if (now >= nextCollect || Math.Abs((utc - collectedFor).TotalSeconds) >= 30)
            {
                nextCollect = now + 2;
                object model = BattleModel(out string source);
                if (model != null)
                {
                    Shown = Collect(model, utc, cLat, cLon);
                    if (!ReferenceEquals(model, collectedModel) || source != modelSource)
                    {
                        collectedModel = model; modelSource = source;
                        if (Diagnostics) Api.Log("world storms map: weather model from " + source);
                    }
                }
                else Shown = new List<MapStorm>();
                collectedFor = utc;
                changed = true;
            }
            if (view.Draw(Shown, changed)) { redraws++; reportRedraws++; }
            if (Diagnostics && now >= nextReport)
            {
                nextReport = now + 10;
                Api.Log("world storms map: " + reportRedraws + " redraw(s) in 10 s (" + redraws + " in all); battle " +
                        utc.ToString("yyyy-MM-dd HH:mm'Z'", CultureInfo.InvariantCulture) + " at " + LatLon(cLat, cLon) + "; " + Shown.Count + " storm(s)" +
                        (Shown.Count == 0 ? "" : ": " + string.Join("; ", Shown.Select(s => s.Id + " " + LatLon(s.Lat, s.Lon) + " " + Num(s.WindKn, "0") + " kn " +
                            Num(StormMapGeometry.DistanceNm(s.Lat, s.Lon, cLat, cLon), "0") + " nm off, gale " + Num(s.GaleNm, "0") + " nm"))));
                reportRedraws = 0;
            }
        }
        catch (Exception ex) { StopMap("world storms map layer stopped; the placed storms themselves are unchanged", ex); }
    }

    // The Noesis side: only ever created in the game (Noesis needs its native
    // runtime), so the managed tests never touch it.
    private sealed class Overlay
    {
        internal object Map;
        internal string HostName;
        private Noesis.FrameworkElement map;
        private Noesis.Panel host;
        private Noesis.Canvas canvas;
        private readonly Noesis.Path[] gale = new Noesis.Path[5];
        private Noesis.Path core, track, markers;
        private readonly List<Noesis.TextBlock> labels = new List<Noesis.TextBlock>();
        private Noesis.TextBlock hover;
        private Noesis.MouseEventHandler moved, left;
        private double probeX = double.NaN, probeY, probeX2, probeY2, width, height;
        private bool empty;
        private double originX = double.NaN, originY = double.NaN;

        private void Clear()
        {
            foreach (var p in gale) p.Data = null;
            core.Data = track.Data = markers.Data = null;
            foreach (var t in labels) t.Visibility = Noesis.Visibility.Collapsed;
            probeX = double.NaN;
        }
        private static readonly Noesis.Color[] Colours =
        {
            Noesis.Color.FromArgb(200, 190, 200, 210), Noesis.Color.FromArgb(230, 255, 225, 90), Noesis.Color.FromArgb(235, 255, 160, 40),
            Noesis.Color.FromArgb(240, 255, 75, 55), Noesis.Color.FromArgb(240, 235, 70, 220)
        };

        internal static Overlay Attach(object mapObject)
        {
            var fe = mapObject as Noesis.FrameworkElement;
            var parent = fe == null ? null : Noesis.VisualTreeHelper.GetParent(fe) as Noesis.Panel;
            if (parent == null) return null;
            var o = new Overlay { Map = mapObject, map = fe, host = parent, HostName = parent.GetType().Name };
            o.canvas = new Noesis.Canvas { IsHitTestVisible = false, Visibility = Noesis.Visibility.Collapsed };
            for (int i = 0; i < 5; i++) o.gale[i] = o.Line(Colours[i], 2f, null);
            o.core = o.Line(Noesis.Color.FromArgb(200, 255, 255, 255), 1.2f, "2 2");
            o.track = o.Line(Noesis.Color.FromArgb(230, 255, 255, 255), 1.6f, "4 3");
            o.markers = o.Line(Noesis.Color.FromArgb(255, 255, 255, 255), 1.5f, null);
            o.hover = o.Text(Noesis.Color.FromArgb(255, 240, 240, 240), 12, true);
            o.hover.Visibility = Noesis.Visibility.Collapsed;
            int at = parent.Children.IndexOf(fe);
            parent.Children.Insert(at < 0 ? parent.Children.Count : at + 1, o.canvas);
            o.moved = o.OnMove;
            o.left = (s, e) => o.hover.Visibility = Noesis.Visibility.Collapsed;
            fe.PreviewMouseMove += o.moved;
            fe.MouseLeave += o.left;
            return o;
        }

        private Noesis.Path Line(Noesis.Color colour, float thickness, string dashes)
        {
            var p = new Noesis.Path { Stroke = new Noesis.SolidColorBrush(colour), StrokeThickness = thickness, IsHitTestVisible = false };
            if (dashes != null) p.StrokeDashArray = dashes;
            canvas.Children.Add(p);
            return p;
        }

        private Noesis.TextBlock Text(Noesis.Color colour, float size, bool bold)
        {
            var t = new Noesis.TextBlock
            {
                Foreground = new Noesis.SolidColorBrush(colour), FontSize = size, IsHitTestVisible = false,
                Stroke = new Noesis.SolidColorBrush(Noesis.Color.FromArgb(220, 10, 14, 20)), StrokeThickness = 2.5f
            };
            if (bold) t.FontWeight = Noesis.FontWeights.Bold;
            canvas.Children.Add(t);
            return t;
        }

        internal void Show(bool on)
        {
            var v = on ? Noesis.Visibility.Visible : Noesis.Visibility.Collapsed;
            if (canvas.Visibility != v) canvas.Visibility = v;
            if (!on && hover.Visibility != Noesis.Visibility.Collapsed) hover.Visibility = Noesis.Visibility.Collapsed;
        }

        internal void Detach()
        {
            try { map.PreviewMouseMove -= moved; map.MouseLeave -= left; } catch { }
            try { host.Children.Remove(canvas); } catch { }
        }

        private void OnMove(object sender, Noesis.MouseEventArgs e)
        {
            try
            {
                if (canvas.Visibility != Noesis.Visibility.Visible || Shown.Count == 0) { hover.Visibility = Noesis.Visibility.Collapsed; return; }
                var p = e.GetPosition(map);
                string text = ToGeo(Map, p.X, p.Y, out double lat, out double lon) ? StormMapGeometry.Hover(Shown, lat, lon) : null;
                if (text == null) { hover.Visibility = Noesis.Visibility.Collapsed; return; }
                var c = map.TranslatePoint(p, canvas);
                hover.Text = text;
                Noesis.Canvas.SetLeft(hover, c.X + 16);
                Noesis.Canvas.SetTop(hover, c.Y + 12);
                hover.Visibility = Noesis.Visibility.Visible;
            }
            catch { hover.Visibility = Noesis.Visibility.Collapsed; }
        }

        // Redraw when the storms changed or the map moved (two probe points
        // shift when the map pans, zooms or turns). True when it redrew.
        internal bool Draw(List<MapStorm> storms, bool changed)
        {
            if (storms.Count == 0)
            {
                if (empty) return false;
                empty = true;
                Clear();
                return true;
            }
            empty = false;
            double cx = 0, cy = 0, x2 = 0, y2 = 0;
            bool probe = storms.Count > 0 && ToView(Map, storms[0].Lat, storms[0].Lon, out cx, out cy) & ToView(Map, storms[0].Lat + 1, storms[0].Lon, out x2, out y2);
            var origin = map.TranslatePoint(new Noesis.Point(0, 0), canvas);
            bool moved = !probe || Math.Abs(origin.X - originX) > 0.25 || Math.Abs(origin.Y - originY) > 0.25 || Math.Abs(cx - probeX) > 0.25 || Math.Abs(cy - probeY) > 0.25 || Math.Abs(x2 - probeX2) > 0.25 || Math.Abs(y2 - probeY2) > 0.25 ||
                         Math.Abs(map.ActualWidth - width) > 0.5 || Math.Abs(map.ActualHeight - height) > 0.5;
            if (!changed && !moved) return false;
            probeX = probe ? cx : double.NaN; probeY = cy; probeX2 = x2; probeY2 = y2;
            width = map.ActualWidth; height = map.ActualHeight;
            originX = origin.X; originY = origin.Y;
            double ox = origin.X, oy = origin.Y, jump = Math.Max(width, height) / 2;
            StormMapGeometry.Project project = (double lat, double lon, out double x, out double y) =>
            {
                bool ok = ToView(Map, lat, lon, out x, out y);
                x += ox; y += oy;
                return ok && x > ox - width && x < ox + 2 * width && y > oy - height && y < oy + 2 * height;
            };
            var galeData = new StringBuilder[5];
            for (int i = 0; i < 5; i++) galeData[i] = new StringBuilder();
            var coreData = new StringBuilder();
            var trackData = new StringBuilder();
            var markerData = new StringBuilder();
            int used = 0;
            foreach (var s in storms)
            {
                if (s.GaleNm > 0) StormMapGeometry.AppendPolyline(galeData[StormMapGeometry.Severity(s.WindKn)], StormMapGeometry.Ring(s.Lat, s.Lon, s.GaleNm), project, jump, true);
                if (s.CoreNm > 0) StormMapGeometry.AppendPolyline(coreData, StormMapGeometry.Ring(s.Lat, s.Lon, s.CoreNm, 36), project, jump, true);
                StormMapGeometry.AppendPolyline(trackData, StormMapGeometry.TrackAhead(s), project, jump);
                if (project(s.Lat, s.Lon, out double x, out double y))
                {
                    StormMapGeometry.AppendMarker(markerData, x, y, 5);
                    Label(used++, StormMapGeometry.CentreText(s) + "\n" + StormMapGeometry.RingText(s), x + 9, y - 30, Colours[StormMapGeometry.Severity(s.WindKn)], 13, true);
                }
                foreach (var l in s.Leads)
                {
                    if (!project(l.Lat, l.Lon, out double lx, out double ly)) continue;
                    StormMapGeometry.AppendMarker(markerData, lx, ly, 2.5);
                    Label(used++, StormMapGeometry.LeadText(l.Hours), lx + 6, ly - 8, Noesis.Color.FromArgb(235, 235, 235, 235), 11, false);
                }
            }
            for (int i = 0; i < 5; i++) gale[i].Data = new Noesis.StreamGeometry(galeData[i].ToString());
            core.Data = new Noesis.StreamGeometry(coreData.ToString());
            track.Data = new Noesis.StreamGeometry(trackData.ToString());
            markers.Data = new Noesis.StreamGeometry(markerData.ToString());
            for (int i = used; i < labels.Count; i++) labels[i].Visibility = Noesis.Visibility.Collapsed;
            return true;
        }

        private void Label(int index, string text, double x, double y, Noesis.Color colour, float size, bool bold)
        {
            while (labels.Count <= index) labels.Add(Text(colour, size, bold));
            var t = labels[index];
            t.Text = text;
            t.Foreground = new Noesis.SolidColorBrush(colour);
            t.FontSize = size;
            t.FontWeight = bold ? Noesis.FontWeights.Bold : Noesis.FontWeights.Normal;
            Noesis.Canvas.SetLeft(t, (float)x);
            Noesis.Canvas.SetTop(t, (float)y);
            t.Visibility = Noesis.Visibility.Visible;
        }
    }
}
