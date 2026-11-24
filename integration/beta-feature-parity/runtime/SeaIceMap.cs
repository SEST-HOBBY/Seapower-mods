using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.Reflection;
using System.Text;
using SeaPower;
using Environment = SeaPower.Environment;

namespace Sest.RuntimeFixes;

// Sea ice on the in-battle tactical map (SeaIceMapLayer=1 in [Runtime],
// default on; needs SeaIce=1). A "Sea ice" entry in the tactical map's Layers
// menu (added the first time a battle's map shows polar water, on) draws the
// concentration the battle itself uses (SeaIceModel on the battle's calendar
// date, SeaIceBattle.Date): the ice edge (SeaIceEdgePercent, 15 %) as a cyan
// line, the heavy pack (SeaIceSubHeavyPercent, 60 %) as a navy line, and a
// pale white-blue fill whose opacity rises with the concentration in five
// bands (SeaIceMapFill=0 leaves the fill out, SeaIceMapOpacity scales it;
// colours from CampaignIceStyle, so the battle map reads like the campaign
// globe). Hovering the map over ice shows "Ice 72 % (heavy pack)" and what it
// does to ships and submarines. Land cells (TerrainUtils.GetHeightAt > 0, the
// height the battle uses; SeaIceMapLandMask=0 skips it) are left out.
//
// The same mechanism as the Weather layer (WorldStormsMap.cs) and R.A.T.S.
// Topographic Map, without Dynamic Campaign Mod: a SeapowerUI.MapLayer made
// with its internal .ctor and added to MapDisplayState.Tactical; the
// rendering MapBase from a MapControl.RenderedLayer.OnRender postfix (the one
// whose DataContext is the tactical view model); a Noesis Canvas drawn from a
// GameMain.Update postfix. Placement (SeaIceMapUnderUnits=1, default): the
// canvas is a child of the map right after its first RenderedLayer (the layer
// that draws the globe texture, Topographic Map's shading included), so unit
// symbols, tracks and the Weather layer stay on top; when the map has no
// RenderedLayer child, or with SeaIceMapUnderUnits=0, it goes after the map in
// the map's parent Panel (as the Weather layer). Topographic Map draws into
// the globe texture (SeaPower.LiveMap.MapScene), so the ice shows on its
// looks too.
//
// Cost: one concentration grid per view (at most 97 x 161 nodes, SeaIceModel
// per node, ~3 ms), rebuilt only on a new calendar day, a zoom that plans
// another cell size or a pan past a quarter-view padding; the lines and fill
// are built once per grid in geo coordinates and only re-projected (at most
// every 50 ms real time) when the map moves. The land mask is sampled over
// several frames (3 ms a frame). Every member is bound before anything is
// installed; any failure stops only this layer, with one log line.
internal static class SeaIceMap
{
    private const string MapHarmonyId = SeaIceBattle.HarmonyId + ".map-layer";
    internal const string LayerName = "SEST_SEA_ICE";
    internal const string LayerText = "Sea ice (edge, pack, heavy pack)";
    internal const int LayerNumber = 611;
    internal const string CanvasName = "SestSeaIceMap";
    private const double CheckEvery = 0.25, ProjectEvery = 0.05, MaskBudgetMs = 3.0;

    internal static bool FillOn = true, UnderUnits = true, LandMaskOn = true;
    internal static double Opacity = IceMapStyle.FillScale;
    private static bool installed, stopped, maskFailed, fillCapped;

    private static MethodInfo tactical, layersByName, layersById, layersList, layerVisible, languageInstance, languageDictionary, dictionarySet;
    private static ConstructorInfo layerCtor, entryCtor;
    private static MethodInfo parentMap, rendered, gameUpdate, sceneMap, displayMap;
    private static FieldInfo mainGameViewModel;
    private static Type renderedLayerType;

    private static object layer;
    private static WeakReference mapRef, lastRejected;
    private static Overlay overlay;
    // grid: the one drawn (with edgeLines, heavyLines, fillBands; the hover
    // reads it); pending: the next one, land mask being sampled, swapped in
    // when its geometry is built, so a zoom keeps the old ice in place
    // (re-projected) instead of leaving it stale for the mask's frames.
    private static IceMapGrid grid, pending;
    private static DateTime gridDate, pendingDate;
    private static readonly IceLandCache landCache = new IceLandCache();
    private static double projectGap = ProjectEvery, lastRedrawMs, maxRedrawMs, nextAttach;
    private static int attachTries;
    private static int maskNext;
    private static bool geometryReady;
    private static List<List<double[]>> edgeLines, heavyLines;
    private static List<List<double[]>>[] fillBands;
    private static double nextCheck, nextRegister, nextReport;
    private static int rebuilds, redraws, layerFailures;

    private static double Now => (double)Stopwatch.GetTimestamp() / Stopwatch.Frequency;
    private static bool Diagnostics => SeaIceBattle.Diagnostics;

    internal static void Install(Assembly game, string[] lines)
    {
        if (installed || stopped) return;
        FillOn = Policy.TextOption(lines, "SeaIceMapFill", "1") == "1";
        UnderUnits = Policy.TextOption(lines, "SeaIceMapUnderUnits", "1") == "1";
        LandMaskOn = Policy.TextOption(lines, "SeaIceMapLandMask", "1") == "1";
        Opacity = IceMapStyle.Scale(Policy.TextOption(lines, "SeaIceMapOpacity", ""));
        try
        {
            Bind(game);
            Api.Postfix(rendered, typeof(SeaIceMap), nameof(AfterMapRender), MapHarmonyId);
            Api.Postfix(gameUpdate, typeof(SeaIceMap), nameof(MapTick), MapHarmonyId);
            installed = true;
            Api.Log("sea ice map layer installed: a \"Sea ice\" entry in the tactical map's Layers menu draws the ice edge (" + Pct(SeaIceBattle.EdgePercent) + "), the heavy pack (" + Pct(SeaIceBattle.HeavyPercent) + ")" +
                    (FillOn ? " and the pack fill (opacity x" + Opacity.ToString("0.00", CultureInfo.InvariantCulture) + ")" : "") +
                    "; " + (UnderUnits ? "under the unit symbols" : "over the map") + (LandMaskOn ? "; land masked" : "; no land mask"));
        }
        catch (Exception ex) { Stop("sea ice map layer unavailable; the ice in battles is unchanged", ex); }
    }

    private static void Member(string name, bool ok)
    {
        if (Diagnostics) Api.Log("sea ice map bind: " + name + (ok ? " ok" : " MISSING"));
        if (!ok) throw new MissingMemberException("Sea Power 0.9.3 " + name);
    }

    private static MethodInfo M(Type t, string name, Type returns, bool isStatic, params Type[] args)
    {
        var m = t.GetMethod(name, Api.All, null, args, null);
        Member(t.Name + "." + name, m != null && m.ReturnType == returns && m.IsStatic == isStatic);
        return m;
    }

    // Every game member the layer uses, by reflection, before anything is
    // patched; the projection members are then called directly (typed).
    internal static void Bind(Assembly game)
    {
        Type T(string n) => Api.Type(game, n);
        var displayState = T("SeapowerUI.MapDisplayState");
        var mapLayer = T("SeapowerUI.MapLayer");
        var entry = T("SeapowerUI.GizmoLayerManager+Entry");
        var mapPanel = T("MapControl.MapPanel");
        var mapBase = T("MapControl.MapBase");
        renderedLayerType = T("MapControl.RenderedLayer");
        var language = T("SeaPower.LanguageResourceHandler");
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
        languageInstance = M(T("SeaPower.Singleton`1").MakeGenericType(language), "get_Instance", language, true);
        var dictionary = T("SeaPower.DictionaryWithFallbacks`2").MakeGenericType(typeof(string), typeof(string));
        languageDictionary = M(language, "get_LanguageDictionary", dictionary, false);
        dictionarySet = M(dictionary, "set_Item", typeof(void), false, typeof(string), typeof(string));
        parentMap = M(mapPanel, "get_ParentMap", mapBase, false);
        Member("MapBase extends MapPanel, a Noesis.Panel", mapPanel.IsAssignableFrom(mapBase) && typeof(Noesis.Panel).IsAssignableFrom(mapPanel));
        Member("RenderedLayer extends MapPanel", mapPanel.IsAssignableFrom(renderedLayerType));
        M(mapBase, "TryLocationToView", typeof(bool), false, typeof(GeoPosition), point.MakeByRefType());
        M(mapBase, "TryViewToGeoPosition", typeof(bool), false, point, typeof(GeoPosition).MakeByRefType());
        rendered = M(renderedLayerType, "OnRender", typeof(void), false, typeof(Noesis.DrawingContext));
        mainGameViewModel = typeof(Globals).GetField("_mainGameViewModel", Api.All);
        var mainGame = T("SeapowerUI.ViewModels.MainGameViewModel");
        Member("Globals._mainGameViewModel : MainGameViewModel (static)", mainGameViewModel != null && mainGameViewModel.IsStatic && mainGameViewModel.FieldType == mainGame);
        sceneMap = M(mainGame, "get_Map", T("SeapowerUI.ViewModels.SceneMapViewModel"), false);
        displayMap = M(T("SeapowerUI.ViewModels.SceneMapViewModel"), "get_DisplayMap", T("SeapowerUI.MapViewModel"), false);
        gameUpdate = M(typeof(GameMain), "Update", typeof(void), false);
        if (LandMaskOn) M(typeof(TerrainUtils), "GetHeightAt", typeof(float), true, typeof(GeoPosition), typeof(bool), typeof(bool), typeof(bool));
    }

    private static void Stop(string label, Exception ex)
    {
        bool first = !stopped;
        stopped = true;
        try { overlay?.Detach(); } catch { }
        overlay = null;
        if (first) Api.LogFailure(label, ex);
    }

    // Postfix on MapControl.RenderedLayer.OnRender(DrawingContext): note the
    // tactical map. Nothing is changed during the render.
    internal static void AfterMapRender(object __instance)
    {
        if (stopped || __instance == null) return;
        try
        {
            object map = parentMap.Invoke(__instance, null);
            if (map == null || ReferenceEquals(map, mapRef?.Target) || ReferenceEquals(map, lastRejected?.Target)) return;
            bool tactical = IsTactical(map);
            var current = mapRef?.Target as Noesis.UIElement;
            if (IceMapStyle.Adopt(tactical, current != null, current != null && current.IsVisible)) mapRef = new WeakReference(map);
            else if (!tactical) lastRejected = new WeakReference(map);
        }
        catch (Exception ex) { Stop("sea ice map layer stopped; the ice in battles is unchanged", ex); }
    }

    private static bool IsTactical(object map)
    {
        object main = mainGameViewModel.GetValue(null);
        object scene = main == null ? null : sceneMap.Invoke(main, null);
        object vm = scene == null ? null : displayMap.Invoke(scene, null);
        return vm != null && ReferenceEquals(((Noesis.FrameworkElement)map).DataContext, vm);
    }

    // The Layers menu entry, once per game session; adopted when it is there.
    private static void EnsureLayer()
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
        Api.Log("sea ice map: layer \"" + LayerText + "\" added to the tactical map's Layers menu (#" + number + "), " + ((bool)layerVisible.Invoke(created, null) ? "on" : "off"));
    }

    // Typed projection (bound by name in Bind first).
    internal static bool ToView(MapControl.MapBase map, double lat, double lon, out double x, out double y)
    {
        var g = new GeoPosition { _latitude = lat, _longitude = StormMapGeometry.NormalLon(lon), _height = 0 };
        bool ok = map.TryLocationToView(g, out Noesis.Point p);
        x = p.X; y = p.Y;
        return ok;
    }

    internal static bool ToGeo(MapControl.MapBase map, double x, double y, out double lat, out double lon)
    {
        bool ok = map.TryViewToGeoPosition(new Noesis.Point((float)x, (float)y), out GeoPosition g);
        lat = g._latitude; lon = g._longitude;
        return ok && !double.IsNaN(lat) && !double.IsNaN(lon);
    }

    private static void ResetGrid()
    {
        grid = pending = null; geometryReady = false; edgeLines = heavyLines = null; fillBands = null; maskNext = 0;
    }

    private static void TryEnsureLayer(double now)
    {
        if (layer != null || now < nextRegister) return;
        nextRegister = now + 2;
        try { EnsureLayer(); }
        catch (Exception ex)
        {
            if (++layerFailures >= 5) throw;
            if (Diagnostics) Api.LogFailure("sea ice map: the Layers menu entry could not be added yet (try " + layerFailures + " of 5)", ex);
        }
    }

    // Postfix on GameMain.Update: everything the layer changes happens here,
    // on the main thread.
    internal static void MapTick()
    {
        if (!installed || stopped) return;
        try
        {
            double now = Now;
            var map = mapRef?.Target as MapControl.MapBase;
            Environment env = map == null ? null : SeaIceBattle.Env();
            if (env == null || map == null)
            {
                overlay?.Show(false);
                return;
            }
            if (overlay == null || !ReferenceEquals(overlay.Map, map))
            {
                overlay?.Detach();
                overlay = null;
                ResetGrid();
                if (now < nextAttach) return;
                overlay = Overlay.Attach(map, UnderUnits, renderedLayerType);
                if (overlay == null)
                {
                    // not in a Panel yet: try once a second, then give up with one line
                    nextAttach = now + 1;
                    if (++attachTries >= 10) { stopped = true; Api.Log("sea ice map layer stopped: the tactical map is not inside a Panel to draw in; the ice in battles is unchanged"); }
                    return;
                }
                if (Diagnostics) Api.Log("sea ice map: drawing on the tactical map (" + overlay.Placement + ")");
            }
            bool on = layer == null || (bool)layerVisible.Invoke(layer, null);
            overlay.Show(on && layer != null);
            if (!on) return;
            var date = SeaIceBattle.Date(env);
            if (now >= nextCheck)
            {
                nextCheck = now + CheckEvery;
                CheckView(map, date, now);
            }
            if (pending != null) AdvanceMask();
            var held = pending ?? grid;
            if (layer == null && held != null && held.MaxPercent >= 1) TryEnsureLayer(now);
            if (layer != null && geometryReady && overlay.Draw(grid, edgeLines, heavyLines, fillBands, now, projectGap, out double ms))
            {
                redraws++;
                lastRedrawMs = ms;
                if (ms > maxRedrawMs) maxRedrawMs = ms;
                projectGap = IceMapStyle.ProjectGap(ProjectEvery, ms);
            }
            if (Diagnostics && now >= nextReport)
            {
                nextReport = now + 10;
                Api.Log("sea ice map: " + date.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture) + "; " + (grid == null ? "no polar water in view" :
                    "grid " + grid.Rows + " x " + grid.Cols + " at " + grid.CellLat.ToString("0.##", CultureInfo.InvariantCulture) + " x " + grid.CellLon.ToString("0.##", CultureInfo.InvariantCulture) + " deg, " +
                    grid.South.ToString("0.0", CultureInfo.InvariantCulture) + " to " + grid.North.ToString("0.0", CultureInfo.InvariantCulture) + "N, max " + Pct(grid.MaxPercent) + ", " + grid.IceCells + " ice cells" +
                    (grid.Land == null ? "" : ", land mask")) + (pending == null ? "" : "; next grid " + pending.Rows + " x " + pending.Cols + (pending.Land == null ? "" : ", mask " + maskNext + " of " + pending.Land.Length)) +
                    "; " + rebuilds + " grid(s), " + redraws + " redraw(s), last " + lastRedrawMs.ToString("0.0", CultureInfo.InvariantCulture) + " ms, max " + maxRedrawMs.ToString("0.0", CultureInfo.InvariantCulture) + " ms; land cache " + landCache.Count + " (hits " + landCache.Hits + ", misses " + landCache.Misses + ")");
            }
        }
        catch (Exception ex) { Stop("sea ice map layer stopped; the ice in battles is unchanged", ex); }
    }

    private static void CheckView(MapControl.MapBase map, DateTime date, double now)
    {
        var probes = IceMapGeometry.Probes(map.ActualWidth, map.ActualHeight);
        var geo = new double[probes.Length][];
        for (int i = 0; i < probes.Length; i++)
            geo[i] = ToGeo(map, probes[i][0], probes[i][1], out double la, out double lo) ? new[] { la, lo } : null;
        if (!IceMapGeometry.BoxOfProbes(geo, out double s, out double n, out double w, out double e)) return;
        switch (IceMapGeometry.Check(pending ?? grid, s, n, w, e, date))
        {
            case IceMapGeometry.Need.Clear:
                ResetGrid();
                overlay.Clear();
                return;
            case IceMapGeometry.Need.Rebuild:
                var g = IceMapGrid.For(s, n, w, e, date);
                if (g == null) { ResetGrid(); overlay.Clear(); return; }
                // the drawn grid stays until this one's geometry is built
                pending = g;
                pendingDate = date;
                maskNext = 0;
                rebuilds++;
                if (LandMaskOn && !maskFailed && g.MaxPercent >= 1) g.Land = new bool[g.Rows * g.Cols];
                return;
        }
    }

    // The pending grid's land mask, 3 ms a frame (cells already sampled come
    // from the land cache), then its lines and fill; then it is the drawn grid.
    private static void AdvanceMask()
    {
        var g = pending;
        if (g.Land != null && maskNext < g.Land.Length)
        {
            var sw = Stopwatch.StartNew();
            try
            {
                while (maskNext < g.Land.Length && sw.Elapsed.TotalMilliseconds < MaskBudgetMs)
                {
                    int r = maskNext / g.Cols, c = maskNext % g.Cols;
                    // only cells that can hold ice need a height
                    if (Math.Max(Math.Max(g.At(r, c), g.At(r, c + 1)), Math.Max(g.At(r + 1, c), g.At(r + 1, c + 1))) >= 1)
                    {
                        double lat = g.LatOf(r) + g.CellLat / 2, lon = StormMapGeometry.NormalLon(g.LonOf(c) + g.CellLon / 2);
                        long key = IceLandCache.Key(g.CellLat, lat, lon);
                        if (!landCache.TryGet(key, out bool land))
                        {
                            float h = TerrainUtils.GetHeightAt(new GeoPosition { _latitude = lat, _longitude = lon, _height = 0 }, false, false, false);
                            land = h > 0f;
                            // -10000: no terrain or DEM loaded there yet; not cached, asked again next grid
                            if (h > -9999f) landCache.Put(key, land);
                        }
                        g.Land[maskNext] = land;
                    }
                    maskNext++;
                }
            }
            catch (Exception ex)
            {
                maskFailed = true;
                g.Land = null;
                Api.LogFailure("sea ice map: land mask off (the ice is drawn over land too)", ex);
            }
            if (g.Land != null && maskNext < g.Land.Length) return;
        }
        var sw2 = Stopwatch.StartNew();
        var edges = IceMapGeometry.Contour(g, SeaIceBattle.EdgePercent);
        var heavies = SeaIceBattle.HeavyPercent > SeaIceBattle.EdgePercent ? IceMapGeometry.Contour(g, SeaIceBattle.HeavyPercent) : new List<List<double[]>>();
        var bands = FillOn ? IceMapGeometry.Fill(g, SeaIceBattle.EdgePercent) : null;
        if (bands != null)
        {
            int verts = 0;
            foreach (var b in bands) foreach (var ring in b) verts += ring.Count;
            if (verts > IceMapGrid.MaxVertices)
            {
                bands = null;
                if (!fillCapped) { fillCapped = true; Api.Log("sea ice map: " + verts + " fill vertices in view (cap " + IceMapGrid.MaxVertices + "); lines only at this zoom"); }
            }
        }
        grid = g; gridDate = pendingDate; pending = null; maskNext = 0;
        edgeLines = edges; heavyLines = heavies; fillBands = bands;
        geometryReady = true;
        overlay.Invalidate();
        if (Diagnostics) Api.Log("sea ice map: geometry for " + g.Rows + " x " + g.Cols + " cells in " + sw2.Elapsed.TotalMilliseconds.ToString("0.0", CultureInfo.InvariantCulture) + " ms (" +
                                 edges.Count + " edge, " + heavies.Count + " heavy-pack polylines, " + g.IceCells + " ice cells" + (g.Land == null ? ", no land mask" : "") + ")");
    }

    internal static string Pct(double v) => v.ToString("0", CultureInfo.InvariantCulture) + " %";

    // The Noesis side: only ever created in the game, never in the managed tests.
    private sealed class Overlay
    {
        internal MapControl.MapBase Map;
        internal string Placement;
        private Noesis.Panel host;
        private Noesis.Canvas canvas;
        private readonly Noesis.Path[] fill = new Noesis.Path[IceMapStyle.BandFloors.Length];
        private Noesis.Path edge, heavy;
        private Noesis.TextBlock hover;
        private Noesis.MouseEventHandler moved, left;
        private double probeX = double.NaN, probeY, probeX2, probeY2, width, height, originX, originY, lastProject = -1;
        private bool dirty = true, empty = true;

        private static Noesis.Color C(byte[] rgb, double alpha) => Noesis.Color.FromArgb((byte)Math.Round(Math.Max(0, Math.Min(1, alpha)) * 255), rgb[0], rgb[1], rgb[2]);

        internal static Overlay Attach(MapControl.MapBase map, bool underUnits, Type renderedLayer)
        {
            var o = new Overlay { Map = map };
            o.canvas = new Noesis.Canvas { IsHitTestVisible = false, Visibility = Noesis.Visibility.Collapsed, Name = CanvasName };
            for (int i = 0; i < o.fill.Length; i++)
                o.fill[i] = o.Path(null, 0, C(CampaignIceStyle.Fill, IceMapStyle.BandAlpha(i, SeaIceBattle.EdgePercent, Opacity)));
            o.heavy = o.Path(CampaignIceStyle.HeavyLine, IceMapStyle.LineHeavyPx, default);
            o.edge = o.Path(CampaignIceStyle.EdgeLine, IceMapStyle.LineEdgePx, default);
            o.hover = new Noesis.TextBlock
            {
                Foreground = new Noesis.SolidColorBrush(Noesis.Color.FromArgb(255, 225, 245, 255)), FontSize = 12, IsHitTestVisible = false,
                Stroke = new Noesis.SolidColorBrush(Noesis.Color.FromArgb(220, 10, 14, 20)), StrokeThickness = 2.5f, Visibility = Noesis.Visibility.Collapsed
            };
            o.canvas.Children.Add(o.hover);
            if (underUnits)
            {
                // the first RenderedLayer child of the map: the globe texture
                int at = -1;
                for (int i = 0; i < map.Children.Count; i++)
                    if (renderedLayer.IsInstanceOfType(map.Children[i])) { at = i + 1; break; }
                if (at < 0) Api.Log("sea ice map: no globe layer inside the tactical map; drawn over the map instead");
                else
                {
                    try
                    {
                        map.Children.Insert(Math.Min(at, map.Children.Count), o.canvas);
                        o.host = map;
                        o.Placement = "in the map, after its globe layer (#" + (at - 1) + " of " + (map.Children.Count - 1) + "), under the unit symbols";
                    }
                    catch (Exception ex) { Api.LogFailure("sea ice map: could not draw inside the tactical map; drawn over the map instead", ex); }
                }
            }
            if (o.host == null)
            {
                var parent = Noesis.VisualTreeHelper.GetParent(map) as Noesis.Panel;
                if (parent == null) return null;
                int m = parent.Children.IndexOf(map);
                parent.Children.Insert(m < 0 ? parent.Children.Count : m + 1, o.canvas);
                o.host = parent;
                o.Placement = "over the map in " + parent.GetType().Name;
            }
            o.moved = o.OnMove;
            o.left = (s, e) => o.hover.Visibility = Noesis.Visibility.Collapsed;
            map.PreviewMouseMove += o.moved;
            map.MouseLeave += o.left;
            return o;
        }

        private Noesis.Path Path(byte[] stroke, double thickness, Noesis.Color fillColour)
        {
            var p = new Noesis.Path { IsHitTestVisible = false };
            if (stroke != null) { p.Stroke = new Noesis.SolidColorBrush(C(stroke, 0.9)); p.StrokeThickness = (float)thickness; }
            else p.Fill = new Noesis.SolidColorBrush(fillColour);
            canvas.Children.Add(p);
            return p;
        }

        internal void Show(bool on)
        {
            var v = on ? Noesis.Visibility.Visible : Noesis.Visibility.Collapsed;
            if (canvas.Visibility != v) { canvas.Visibility = v; if (on) dirty = true; }
            if (!on && hover.Visibility != Noesis.Visibility.Collapsed) hover.Visibility = Noesis.Visibility.Collapsed;
        }

        internal void Invalidate() { dirty = true; empty = false; }

        internal void Clear()
        {
            if (empty) return;
            empty = true;
            foreach (var p in fill) p.Data = null;
            edge.Data = heavy.Data = null;
            hover.Visibility = Noesis.Visibility.Collapsed;
        }

        internal void Detach()
        {
            try { Map.PreviewMouseMove -= moved; Map.MouseLeave -= left; } catch { }
            try { host.Children.Remove(canvas); } catch { }
        }

        private void OnMove(object sender, Noesis.MouseEventArgs e)
        {
            try
            {
                var g = grid;
                if (canvas.Visibility != Noesis.Visibility.Visible || g == null || !geometryReady) { hover.Visibility = Noesis.Visibility.Collapsed; return; }
                var p = e.GetPosition(Map);
                string text = null;
                // the battle's own value at the cursor (its 0.05-degree tile), not the drawn grid
                if (ToGeo(Map, p.X, p.Y, out double lat, out double lon) && !IceMapGeometry.LandAt(g, lat, lon))
                    text = IceMapStyle.Hover(IceMapStyle.BattlePercent(lat, lon, gridDate), SeaIceBattle.HeavyPercent, SeaIceBattle.KeelMeters, SeaIceBattle.ShipsOn, SeaIceBattle.SubsOn);
                if (text == null) { hover.Visibility = Noesis.Visibility.Collapsed; return; }
                var c = Map.TranslatePoint(p, canvas);
                hover.Text = text;
                Noesis.Canvas.SetLeft(hover, c.X + 16);
                Noesis.Canvas.SetTop(hover, c.Y - 40);
                hover.Visibility = Noesis.Visibility.Visible;
            }
            catch { hover.Visibility = Noesis.Visibility.Collapsed; }
        }

        // Re-project when the geometry changed or the map moved (the geo
        // under two fixed view points, the origin or the size shift: a pan,
        // zoom or globe turn), at most every 50 ms; a move inside that window
        // is drawn on the next frame after it.
        internal bool Draw(IceMapGrid g, List<List<double[]>> edges, List<List<double[]>> heavies, List<List<double[]>>[] bands, double now, double gap, out double ms)
        {
            ms = 0;
            double vw = Map.ActualWidth, vh = Map.ActualHeight;
            bool probe = ToGeo(Map, vw / 2, vh / 2, out double cx, out double cy) & ToGeo(Map, vw / 2 + 100, vh / 2, out double x2, out double y2);
            var origin = Map.TranslatePoint(new Noesis.Point(0, 0), canvas);
            const double Deg = 1e-7;
            bool moved = Math.Abs(origin.X - originX) > 0.25 || Math.Abs(origin.Y - originY) > 0.25 || Math.Abs(vw - width) > 0.5 || Math.Abs(vh - height) > 0.5 ||
                         probe && (double.IsNaN(probeX) || Math.Abs(cx - probeX) > Deg || Math.Abs(cy - probeY) > Deg || Math.Abs(x2 - probeX2) > Deg || Math.Abs(y2 - probeY2) > Deg);
            if (!dirty && !moved) return false;
            if (now - lastProject < gap) { dirty = true; return false; }
            lastProject = now;
            var cost = Stopwatch.StartNew();
            dirty = false; empty = false;
            probeX = probe ? cx : double.NaN; probeY = cy; probeX2 = x2; probeY2 = y2;
            width = Map.ActualWidth; height = Map.ActualHeight; originX = origin.X; originY = origin.Y;
            double ox = origin.X, oy = origin.Y, jump = Math.Max(width, height) / 2;
            StormMapGeometry.Project project = (double lat, double lon, out double x, out double y) =>
            {
                bool ok = ToView(Map, lat, lon, out x, out y);
                x += ox; y += oy;
                return ok;
            };
            for (int i = 0; i < fill.Length; i++)
            {
                if (bands == null) { fill[i].Data = null; continue; }
                var data = new StringBuilder();
                foreach (var ring in bands[i]) IceMapGeometry.AppendRing(data, ring, project, jump);
                fill[i].Data = data.Length == 0 ? null : new Noesis.StreamGeometry(data.ToString());
            }
            var ed = new StringBuilder();
            foreach (var l in edges) StormMapGeometry.AppendPolyline(ed, l, project, jump);
            edge.Data = ed.Length == 0 ? null : new Noesis.StreamGeometry(ed.ToString());
            var hd = new StringBuilder();
            foreach (var l in heavies) StormMapGeometry.AppendPolyline(hd, l, project, jump);
            heavy.Data = hd.Length == 0 ? null : new Noesis.StreamGeometry(hd.ToString());
            ms = cost.Elapsed.TotalMilliseconds;
            return true;
        }
    }
}
