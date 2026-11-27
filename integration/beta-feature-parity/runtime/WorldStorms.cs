using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Security.Cryptography;
using AnchorChain;

namespace Sest.RuntimeFixes;

// Placed storms for Dynamic Campaign Mod 1.0.4 (b816459d): a campaign folder
// that holds sest-weather.json beside campaign.json gets its storms as DCM
// WeatherSystems inside DCM's own WeatherModel, so the weather layer, the
// storm list (past track, forecast points, cone), map hover, the contact
// screen, the battle [Environment] DCM writes, and DCM's route and deck rules
// all see the same storm. DCM files and saves are not changed; a campaign
// without the sidecar is untouched. WorldStorms=0 in [Runtime] turns it off.
//
// Two postfixes:
// - WeatherModel.For(CampaignDefinition, int), the only producer of models
//   (every consumer, WeatherEffects included, goes through For(state)):
//   it reads the definition's sidecar once (CampaignDefinition.FilePath's
//   folder) and ties the storms to the returned model INSTANCE. When a
//   model's storms change (first tie, or a campaign without storms reusing a
//   model with the same theatre, seed and bounds), that model's snapshot and
//   grid caches are cleared under its own _lock. Because the tie is on the
//   instance, WeatherEffects._model, which caches the instance for the
//   campaign's life, gets the storms with no field reset, and a sim that
//   samples weather before CampaignSession.Prepare does too.
// - WeatherModel.Build(DateTime) (private): each active storm is appended to
//   the new Snapshot's Actives and added to its Bins with Build's exact
//   asymmetric clamping (StormSidecar.BinRange). The snapshot is not yet
//   published (SnapshotAt stores it after Build returns), so this is safe on
//   DCM's worker threads.
// - WeatherModel.SnapshotAt(DateTime) and Grid(GeoBounds, double, DateTime):
//   a prefix notes the model's tie generation and a postfix drops the entry
//   just stored from the cache when the generation changed meanwhile. DCM
//   builds a snapshot or grid outside its _lock and stores it afterwards, so
//   without this a build that started under the old storm set (or before a
//   Stop) could be cached after Invalidate cleared the model.
// Stop() bumps every tied model's generation and clears its caches, so no
// cached hour keeps a placed storm once the feature is off.
// Fixed-weather zones are not part of this version: Compose returns the
// WeatherSample struct by value, and a postfix cannot change it.
internal static partial class WorldStorms
{
    private const string CampaignHash = "b816459dba7fb76b56460006aeabd4e5cce0fe930f8025a72b040af039d07c25";
    private const string HarmonyId = "io.github.sest-hobby.world-storms";
    private const string Retained = "Dynamic Campaign Mod's own weather retained";
    // Generation: bumped (under gate) whenever the model's set changes or the
    // feature stops; 0 for a model never tied.
    // Failed: the definition's sidecar could not be read at FailedAt (Now);
    // Failure and FileTime are that read's reason and the file's write time.
    private sealed class Holder
    {
        internal StormSet Set; internal int Generation;
        internal bool Failed; internal double FailedAt; internal string Failure; internal DateTime FileTime;
    }
    internal sealed class StormSet
    {
        internal string Path;
        internal StormSpec[] Specs;
        internal object[] Systems;
        internal DateTime[] Born, Dies;
    }

    internal static bool Diagnostics;
    private static bool waiting, bound, installed, stopped, localWanted;
    private static double nextBind;
    private static Assembly game;
    private static double Now => (double)Stopwatch.GetTimestamp() / Stopwatch.Frequency;
    private static readonly object gate = new object();
    private static readonly ConditionalWeakTable<object, Holder> definitions = new ConditionalWeakTable<object, Holder>();
    private static readonly ConditionalWeakTable<object, Holder> models = new ConditionalWeakTable<object, Holder>();
    // The tied models, for Stop (a ConditionalWeakTable cannot be enumerated
    // on Unity's Mono); and the model For returned last, for the map layer.
    private static readonly List<WeakReference> tied = new List<WeakReference>();
    private static WeakReference lastModel;
    private static readonly HashSet<string> loggedHours = new HashSet<string>(StringComparer.Ordinal);
    private static readonly Dictionary<int, string> loggedBattle = new Dictionary<int, string>();
    private static readonly DateTime Epoch = new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc);

    private static Type modelType, snapshotType, activeType, systemType, pointType, kindType, basinType, definitionType, boundsType;
    private static MethodInfo forDefinition, build, snapshotAt, grid, systemAt, reachNm, label, weatherOf, special;
    private static FieldInfo filePath, defBounds, latMin, latMax, lonMin, lonMax, modelBounds, modelLock, snapshots, snapshotOrder, grids;
    private static FieldInfo actives, bins, binLat0, binLon0, binRows, binCols, climate;
    private static FieldInfo aSystem, aPoint, aReach, aLabel;
    private static FieldInfo sId, sName, sKind, sBasin, sBorn, sLife, sTrack, sPeakWind, sPeakDepth;
    private static FieldInfo pLat, pLon, pVmax, pDp, pR, pOuter, pEnv, pU, pV, pTropical;
    private static FieldInfo bId, bWord;
    private static FieldInfo eId, ePoint, eAt, gLat, gLon;
    private static FieldInfo wSeaState, wWindFrom, wWindKnots, wClouds, wStorm, wTyphoon;
    private static MethodInfo snapshotsClear, orderClear, gridsClear;

    // From RuntimeFixesMod, after the native image check. Never throws.
    // Binding is lazy and independent of every other SEST feature: now if
    // DCM is already loaded, else when its assembly loads, with a poll from
    // GameMain.Update every 2 s as the fallback (as WorldOperations.Bind).
    // mapLayer: also add the tactical map's Weather layer (WorldStormsMap.cs).
    internal static void Start(Assembly native, bool diagnostics, bool mapLayer = false) => Start(native, diagnostics, mapLayer, false);

    // localView: also the local battle weather view (LocalWeatherView.cs).
    internal static void Start(Assembly native, bool diagnostics, bool mapLayer, bool localView)
    {
        Diagnostics = diagnostics;
        game = native;
        mapWanted = mapLayer && native != null;
        localWanted = localView && native != null;
        try
        {
            if (TryBind()) return;
            waiting = true;
            AppDomain.CurrentDomain.AssemblyLoad += Loaded;
            Api.Postfix(Api.Method(Api.Type(native, "SeaPower.GameMain"), "Update", typeof(void)), typeof(WorldStorms), nameof(Poll), HarmonyId + ".bootstrap");
            Api.Log("world storms awaiting Dynamic Campaign Mod 1.0.4");
        }
        catch (Exception ex) { Stop("world storms unavailable; " + Retained, ex); }
    }

    private static void Loaded(object sender, AssemblyLoadEventArgs args)
    {
        try
        {
            if (waiting && args.LoadedAssembly.GetType("DynamicCampaignMod.Game.Session.CampaignSession", false) != null) { nextBind = 0; Poll(); }
        }
        catch (Exception ex) { Stop("world storms unavailable; " + Retained, ex); }
    }

    internal static void Poll()
    {
        if (!waiting || stopped || Now < nextBind) return;
        nextBind = Now + 2;
        try { TryBind(); }
        catch (Exception ex) { Stop("world storms unavailable; " + Retained, ex); }
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

    // Never throws. Every live tied model gets a new generation (so a build
    // in flight is not cached) and empty caches (so DCM rebuilds every hour
    // without placed storms), each in its own try.
    private static void Stop(string label, Exception ex)
    {
        bool first;
        var live = new List<object>();
        lock (gate)
        {
            first = !stopped; stopped = true; waiting = false;
            foreach (var w in tied)
            {
                object m = w.Target;
                if (m == null) continue;
                if (models.TryGetValue(m, out var held)) held.Generation++;
                live.Add(m);
            }
        }
        if (first) Api.LogFailure(label, ex);
        int cleared = 0;
        foreach (var m in live)
        {
            try { Invalidate(m); cleared++; }
            catch (Exception e) { try { Api.LogFailure("world storms: a weather model's cache was not cleared", e); } catch { } }
        }
        if (first && cleared > 0) try { Api.Log("world storms: placed storms removed from " + cleared + " weather model(s); their cached snapshots were cleared"); } catch { }
    }

    internal static int GenerationOf(object model)
    {
        lock (gate) return models.TryGetValue(model, out var held) ? held.Generation : 0;
    }

    // The model For returned last (any campaign), or null.
    internal static object LastModel => lastModel?.Target;

    private static void Member(string name, bool ok)
    {
        if (Diagnostics) Api.Log("world storms bind: " + name + (ok ? " ok" : " MISSING"));
        if (!ok) throw new MissingMemberException("captured " + name);
    }
    private static FieldInfo F(Type t, string name, Type expected, string shown = null)
    {
        var f = t.GetField(name, Api.All);
        Member((shown ?? t.Name) + "." + name + " : " + (expected?.Name ?? "?"), f != null && !f.IsStatic && (expected == null || f.FieldType == expected));
        return f;
    }
    private static MethodInfo M(Type t, string name, Type returns, bool isStatic, params Type[] args)
    {
        var m = t.GetMethod(name, Api.All, null, args, null);
        Member(t.Name + "." + name + "(" + string.Join(", ", args.Select(x => x.Name)) + ") : " + returns.Name, m != null && m.ReturnType == returns && m.IsStatic == isStatic);
        return m;
    }

    // Hash-locked, all members checked; false (one log line) on any mismatch.
    internal static bool Bind(Assembly a)
    {
        try
        {
            using (var sha = SHA256.Create())
            using (var stream = File.OpenRead(BetaAssemblyPolicy.OriginalLocation(a)))
                if (BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant() != CampaignHash)
                    throw new InvalidOperationException("world storms require the inspected Dynamic Campaign Mod 1.0.4 image (b816459d)");
            const string sim = "DynamicCampaignMod.Core.Sim.";
            dcm = a;
            modelType = a.GetType(sim + "WeatherModel", true);
            snapshotType = a.GetType(sim + "WeatherModel+Snapshot", true);
            activeType = a.GetType(sim + "WeatherModel+Active", true);
            systemType = a.GetType(sim + "WeatherSystem", true);
            pointType = a.GetType(sim + "TrackPoint", true);
            kindType = a.GetType(sim + "SystemKind", true);
            basinType = a.GetType(sim + "TropicalBasin", true);
            definitionType = a.GetType("DynamicCampaignMod.Core.Data.CampaignDefinition", true);
            boundsType = a.GetType("DynamicCampaignMod.Core.Data.GeoBounds", true);
            var climateType = a.GetType(sim + "ClimateField", true);
            Member("TrackPoint and Active value types, SystemKind Tropical=3 Gale=2", pointType.IsValueType && activeType.IsValueType && kindType.IsEnum &&
                Convert.ToInt32(Enum.Parse(kindType, "Tropical")) == 3 && Convert.ToInt32(Enum.Parse(kindType, "Gale")) == 2);

            forDefinition = M(modelType, "For", modelType, true, definitionType, typeof(int));
            build = M(modelType, "Build", snapshotType, false, typeof(DateTime));
            snapshotAt = M(modelType, "SnapshotAt", snapshotType, false, typeof(DateTime));
            grid = M(modelType, "Grid", a.GetType(sim + "WeatherGrid", true), false, boundsType, typeof(double), typeof(DateTime));
            systemAt = M(systemType, "At", pointType, false, typeof(DateTime));
            reachNm = M(systemType, "ReachNm", typeof(double), false, pointType.MakeByRefType());
            label = M(modelType, "Label", typeof(string), true, systemType, pointType, climateType);

            filePath = F(definitionType, "FilePath", typeof(string));
            defBounds = F(definitionType, "bounds", boundsType);
            latMin = F(boundsType, "latMin", typeof(double)); latMax = F(boundsType, "latMax", typeof(double));
            lonMin = F(boundsType, "lonMin", typeof(double)); lonMax = F(boundsType, "lonMax", typeof(double));
            modelBounds = F(modelType, "Bounds", boundsType);
            modelLock = F(modelType, "_lock", typeof(object));
            snapshots = F(modelType, "_snapshots", typeof(Dictionary<,>).MakeGenericType(typeof(long), snapshotType));
            snapshotOrder = F(modelType, "_snapshotOrder", typeof(Queue<long>));
            grids = F(modelType, "_grids", typeof(List<>).MakeGenericType(a.GetType(sim + "WeatherGrid", true)));
            snapshotsClear = snapshots.FieldType.GetMethod("Clear", Type.EmptyTypes);
            orderClear = snapshotOrder.FieldType.GetMethod("Clear", Type.EmptyTypes);
            gridsClear = grids.FieldType.GetMethod("Clear", Type.EmptyTypes);

            actives = F(snapshotType, "Actives", typeof(List<>).MakeGenericType(activeType), "Snapshot");
            bins = F(snapshotType, "Bins", typeof(List<int>[]), "Snapshot");
            binLat0 = F(snapshotType, "BinLat0", typeof(double), "Snapshot"); binLon0 = F(snapshotType, "BinLon0", typeof(double), "Snapshot");
            binRows = F(snapshotType, "BinRows", typeof(int), "Snapshot"); binCols = F(snapshotType, "BinCols", typeof(int), "Snapshot");
            climate = F(snapshotType, "Climate", climateType, "Snapshot");
            aSystem = F(activeType, "System", systemType, "Active"); aPoint = F(activeType, "Point", pointType, "Active");
            aReach = F(activeType, "ReachNm", typeof(double), "Active"); aLabel = F(activeType, "Label", typeof(string), "Active");

            sId = F(systemType, "Id", typeof(string)); sName = F(systemType, "Name", typeof(string)); sKind = F(systemType, "Kind", kindType);
            sBasin = F(systemType, "Basin", basinType); sBorn = F(systemType, "Born", typeof(DateTime)); sLife = F(systemType, "LifeHours", typeof(double));
            sTrack = F(systemType, "Track", pointType.MakeArrayType()); sPeakWind = F(systemType, "PeakWind", typeof(double)); sPeakDepth = F(systemType, "PeakDepth", typeof(double));
            pLat = F(pointType, "Lat", typeof(double)); pLon = F(pointType, "Lon", typeof(double)); pVmax = F(pointType, "Vmax", typeof(double));
            pDp = F(pointType, "Dp", typeof(double)); pR = F(pointType, "R", typeof(double)); pOuter = F(pointType, "Outer", typeof(double));
            pEnv = F(pointType, "Env", typeof(double)); pU = F(pointType, "U", typeof(double)); pV = F(pointType, "V", typeof(double));
            pTropical = F(pointType, "Tropical", typeof(bool));
            bId = F(basinType, "Id", typeof(string)); bWord = F(basinType, "Word", typeof(string));
            Member("WeatherSystem() and TropicalBasin() constructors", systemType.GetConstructor(Api.All, null, Type.EmptyTypes, null) != null &&
                basinType.GetConstructor(Api.All, null, Type.EmptyTypes, null) != null);

            // Diagnostics only: the battle weather DCM writes as [Environment].
            var battles = a.GetType(sim + "Battles", true);
            var engagement = a.GetType("DynamicCampaignMod.Core.State.Engagement", true);
            var battleWeather = a.GetType(sim + "BattleWeather", true);
            var geo = a.GetType("DynamicCampaignMod.Core.Geo.GeoPoint", true);
            weatherOf = M(battles, "WeatherOf", battleWeather, false, engagement);
            eId = F(engagement, "Id", typeof(int)); ePoint = F(engagement, "Point", geo); eAt = F(engagement, "At", typeof(DateTime));
            gLat = geo.GetField("Lat", Api.All); gLon = geo.GetField("Lon", Api.All);
            Member("GeoPoint.Lat, Lon", gLat?.FieldType == typeof(double) && gLon?.FieldType == typeof(double));
            wSeaState = F(battleWeather, "SeaState", typeof(int)); wWindFrom = F(battleWeather, "WindFrom", typeof(string));
            wWindKnots = F(battleWeather, "WindKnots", typeof(int)); wClouds = F(battleWeather, "Clouds", typeof(string));
            wStorm = F(battleWeather, "Storm", typeof(string)); wTyphoon = F(battleWeather, "Typhoon", typeof(bool));
            special = battleWeather.GetProperty("Special", Api.All)?.GetGetMethod(true);
            Member("BattleWeather.Special : String", special?.ReturnType == typeof(string));
            bound = true;
            if (Diagnostics) Api.Log("world storms bind: all members of Dynamic Campaign Mod 1.0.4 (b816459d) bound");
            return true;
        }
        catch (Exception ex)
        {
            bound = false;
            Stop("world storms unavailable; " + Retained, ex);
            return false;
        }
    }

    internal static void Install()
    {
        if (!bound || installed || stopped) return;
        try
        {
            Api.Postfix(forDefinition, typeof(WorldStorms), nameof(AfterFor), HarmonyId);
            Api.Postfix(build, typeof(WorldStorms), nameof(AfterBuild), HarmonyId);
            Api.Hooks(snapshotAt, typeof(WorldStorms), nameof(BeforeCache), nameof(AfterSnapshotAt), HarmonyId);
            Api.Hooks(grid, typeof(WorldStorms), nameof(BeforeCache), nameof(AfterGrid), HarmonyId);
            if (Diagnostics) Api.Postfix(weatherOf, typeof(WorldStorms), nameof(AfterWeatherOf), HarmonyId + ".diagnostics");
            installed = true;
            Api.Log("world storms installed: campaigns with " + StormSidecar.FileName + " beside campaign.json get its storms in Dynamic Campaign Mod's weather model; other campaigns unchanged" +
                    (Diagnostics ? "; diagnostics on" : ""));
        }
        catch (Exception ex) { Stop("world storms unavailable; " + Retained, ex); }
        if (installed && mapWanted) InstallMap(game);
        if (installed && localWanted) LocalWeatherView.Install(game);
    }

    private static string Num(double v, string f = "0.00") => v.ToString(f, CultureInfo.InvariantCulture);
    private static string LatLon(double lat, double lon) =>
        Num(Math.Abs(lat)) + (lat < 0 ? "S " : "N ") + Num(Math.Abs(lon > 180 ? lon - 360 : lon)) + ((lon > 180 ? lon - 360 : lon) < 0 ? "W" : "E");

    // Postfix on WeatherModel.For(CampaignDefinition definition, int seed).
    internal static void AfterFor(object __0, object __result)
    {
        if (__result != null) lastModel = new WeakReference(__result);
        if (stopped || !installed || __result == null) return;
        try
        {
            var set = __0 == null ? null : SetFor(__0, __result);
            lock (gate)
            {
                models.TryGetValue(__result, out var held);
                if (ReferenceEquals(held?.Set, set)) return;
                if (held == null)
                {
                    held = new Holder();
                    models.Add(__result, held);
                    tied.RemoveAll(w => !w.IsAlive);
                    tied.Add(new WeakReference(__result));
                }
                held.Set = set;
                held.Generation++;
            }
            Invalidate(__result);
            Api.Log(set != null
                ? "world storms: " + set.Systems.Length + " storm(s) from " + set.Path + " tied to the weather model; its cached snapshots were cleared"
                : "world storms: weather model reused by a campaign without " + StormSidecar.FileName + "; placed storms removed from it and its cached snapshots cleared");
        }
        catch (Exception ex) { Stop("world storms stopped; " + Retained, ex); }
    }

    // A model's snapshots and grids are rebuilt on the next query, now
    // through AfterBuild. Under the model's own lock, as SnapshotAt and Grid
    // store under it.
    internal static void Invalidate(object model)
    {
        lock (modelLock.GetValue(model))
        {
            snapshotsClear.Invoke(snapshots.GetValue(model), null);
            orderClear.Invoke(snapshotOrder.GetValue(model), null);
            gridsClear.Invoke(grids.GetValue(model), null);
        }
    }

    // A snapshot or grid DCM stored while the model's tie generation changed
    // (a re-tie or a Stop during the build) is dropped from the cache, so the
    // next query rebuilds it under the current set. The value this one call
    // returns is not changed.
    internal static void BeforeCache(object __instance, out int __state)
    {
        __state = 0;
        try { if (__instance != null) __state = GenerationOf(__instance); } catch { }
    }

    internal static void AfterSnapshotAt(object __instance, object __result, int __state)
    {
        if (__instance == null || __result == null || modelLock == null) return;
        try
        {
            if (GenerationOf(__instance) == __state) return;
            bool dropped = false;
            lock (modelLock.GetValue(__instance))
            {
                var cache = (IDictionary)snapshots.GetValue(__instance);
                foreach (DictionaryEntry e in cache)
                {
                    if (!ReferenceEquals(e.Value, __result)) continue;
                    long key = (long)e.Key;
                    cache.Remove(key);
                    var order = (Queue<long>)snapshotOrder.GetValue(__instance);
                    var keep = order.Where(k => k != key).ToList();
                    order.Clear();
                    foreach (long k in keep) order.Enqueue(k);
                    dropped = true;
                    break;
                }
            }
            if (dropped && Diagnostics) Api.Log("world storms: a snapshot built while the model's storms changed was not kept in its cache");
        }
        catch (Exception ex) { Api.LogFailure("world storms: stale snapshot check", ex); }
    }

    internal static void AfterGrid(object __instance, object __result, int __state)
    {
        if (__instance == null || __result == null || modelLock == null) return;
        try
        {
            if (GenerationOf(__instance) == __state) return;
            bool dropped;
            lock (modelLock.GetValue(__instance)) dropped = ((IList)grids.GetValue(__instance)).Contains(__result);
            if (dropped) lock (modelLock.GetValue(__instance)) ((IList)grids.GetValue(__instance)).Remove(__result);
            if (dropped && Diagnostics) Api.Log("world storms: a weather grid built while the model's storms changed was not kept in its cache");
        }
        catch (Exception ex) { Api.LogFailure("world storms: stale grid check", ex); }
    }

    // The definition's storms, read once per definition object; null when
    // its folder has no sidecar or the sidecar is rejected. A sidecar that
    // cannot be read (locked, no access, a bad path) gives null and is tried
    // again on a For RetrySeconds or more after the failed read, not on every
    // For (DCM and the battle views call For every few seconds); a repeat of
    // the same failure on an unchanged file is not logged again. Nothing
    // else stops. The file is read outside gate.
    internal static double RetrySeconds = 30;
    internal static StormSet SetFor(object definition, object model)
    {
        Holder known;
        lock (gate)
        {
            if (definitions.TryGetValue(definition, out known) && (!known.Failed || Now - known.FailedAt < RetrySeconds)) return known.Set;
        }
        var set = Read(definition, model, known, out Holder failed);
        lock (gate)
        {
            if (definitions.TryGetValue(definition, out var cached))
            {
                // Another thread's read got there first: its set, if it read one.
                if (!cached.Failed) return cached.Set;
                definitions.Remove(definition);
            }
            definitions.Add(definition, failed ?? new Holder { Set = set });
            return set;
        }
    }

    private static bool Unreadable(Exception ex) =>
        ex is IOException || ex is UnauthorizedAccessException || ex is ArgumentException || ex is NotSupportedException || ex is System.Security.SecurityException;

    private static StormSet Read(object definition, object model, Holder before, out Holder failed)
    {
        failed = null;
        string file = filePath.GetValue(definition) as string;
        if (string.IsNullOrEmpty(file))
        {
            if (Diagnostics) Api.Log("world storms: campaign definition has no file path (built in); no sidecar read");
            return null;
        }
        string path = null, text;
        try
        {
            string folder = Path.GetDirectoryName(file);
            path = folder == null ? null : Path.Combine(folder, StormSidecar.FileName);
            if (path == null || !File.Exists(path))
            {
                if (Diagnostics) Api.Log("world storms: no sidecar at " + path + "; DCM weather unchanged for this campaign");
                return null;
            }
            text = File.ReadAllText(path);
        }
        catch (Exception ex) when (Unreadable(ex))
        {
            failed = new Holder { Failed = true, FailedAt = Now, Failure = ex.GetType().Name + ": " + ex.Message, FileTime = WriteTime(path) };
            if (before != null && before.Failed && before.Failure == failed.Failure && before.FileTime == failed.FileTime) return null;
            Api.Log("world storms: " + new string((path ?? file).Select(c => c < ' ' ? '?' : c).ToArray()) + " unreadable (" + ex.GetType().Name + ": " + ex.Message + "); no storms placed for this campaign, other campaigns unaffected");
            return null;
        }
        var specs = StormSidecar.Parse(text, out string error);
        if (specs == null)
        {
            Api.Log("world storms: " + path + " rejected (" + error + "); no storms placed");
            return null;
        }
        object b = modelBounds.GetValue(model) ?? defBounds.GetValue(definition);
        double lo = b == null ? -180 : (double)lonMin.GetValue(b), hi = b == null ? 180 : (double)lonMax.GetValue(b);
        var set = new StormSet { Path = path, Specs = specs.ToArray(), Systems = new object[specs.Count], Born = new DateTime[specs.Count], Dies = new DateTime[specs.Count] };
        for (int k = 0; k < specs.Count; k++)
        {
            set.Systems[k] = NewSystem(specs[k], lo, hi);
            set.Born[k] = specs[k].Born;
            set.Dies[k] = specs[k].Dies;
        }
        Api.Log("world storms: sidecar " + path + ": " + string.Join("; ", specs.Select(s => "sest-" + s.Id + " " + s.Kind + " " + s.Name + " " +
            s.Born.ToString("yyyy-MM-dd HH:mm'Z'", CultureInfo.InvariantCulture) + " to " + s.Dies.ToString("yyyy-MM-dd HH:mm'Z'", CultureInfo.InvariantCulture) +
            ", peak " + Num(s.Waypoints.Max(w => w.Wind), "0") + " kn")));
        return set;
    }

    private static DateTime WriteTime(string path)
    {
        try { return path == null ? DateTime.MinValue : File.GetLastWriteTimeUtc(path); }
        catch (Exception ex) when (Unreadable(ex)) { return DateTime.MinValue; }
    }

    // A DCM WeatherSystem as NewTropical / NewExtratropical build them.
    internal static object NewSystem(StormSpec s, double lonLo, double lonHi)
    {
        var points = StormSidecar.Track(s, lonLo, lonHi, out double life);
        var track = Array.CreateInstance(pointType, points.Length);
        double peakWind = 0, peakDepth = 0;
        for (int i = 0; i < points.Length; i++)
        {
            var t = points[i];
            object p = Activator.CreateInstance(pointType);
            pLat.SetValue(p, t.Lat); pLon.SetValue(p, t.Lon); pVmax.SetValue(p, t.Vmax); pDp.SetValue(p, t.Dp);
            pR.SetValue(p, t.R); pOuter.SetValue(p, t.Outer); pEnv.SetValue(p, t.Env); pU.SetValue(p, t.U); pV.SetValue(p, t.V);
            pTropical.SetValue(p, t.Tropical);
            track.SetValue(p, i);
            peakWind = Math.Max(peakWind, t.Vmax); peakDepth = Math.Max(peakDepth, t.Dp);
        }
        object sys = Activator.CreateInstance(systemType, true);
        sId.SetValue(sys, "sest-" + s.Id);
        sName.SetValue(sys, s.Name);
        sKind.SetValue(sys, Enum.ToObject(kindType, s.Tropical ? 3 : 2));
        if (s.Tropical)
        {
            // Category reads only Basin.Word ("<Word> (category n)"); this basin
            // is in no theatre, so DCM's Season never draws from it.
            object basin = Activator.CreateInstance(basinType, true);
            bId.SetValue(basin, "sest");
            bWord.SetValue(basin, s.Kind);
            sBasin.SetValue(sys, basin);
        }
        sBorn.SetValue(sys, DateTime.SpecifyKind(s.Born, DateTimeKind.Utc));
        sLife.SetValue(sys, life);
        sTrack.SetValue(sys, track);
        sPeakWind.SetValue(sys, peakWind);
        sPeakDepth.SetValue(sys, peakDepth);
        return sys;
    }

    // Postfix on the private WeatherModel.Build(DateTime utc).
    internal static void AfterBuild(object __instance, DateTime __0, object __result)
    {
        if (stopped || __instance == null || __result == null) return;
        StormSet set;
        lock (gate)
        {
            if (!models.TryGetValue(__instance, out var held) || held.Set == null) return;
            set = held.Set;
        }
        try { Inject(set, __0, __result); }
        catch (Exception ex) { Stop("world storms stopped; " + Retained, ex); }
    }

    internal static int Inject(StormSet set, DateTime utc, object snapshot)
    {
        var list = (IList)actives.GetValue(snapshot);
        int native = list.Count, added = 0;
        object field = climate.GetValue(snapshot);
        var cells = (List<int>[])bins.GetValue(snapshot);
        double lat0 = (double)binLat0.GetValue(snapshot), lon0 = (double)binLon0.GetValue(snapshot);
        int rows = (int)binRows.GetValue(snapshot), cols = (int)binCols.GetValue(snapshot);
        for (int k = 0; k < set.Systems.Length; k++)
        {
            // Build's own test: skip when utc < Born or utc > Dies.
            if (utc < set.Born[k] || utc > set.Dies[k]) continue;
            object sys = set.Systems[k];
            object point = systemAt.Invoke(sys, new object[] { utc });
            double reach = (double)reachNm.Invoke(sys, new[] { point });
            string text = (string)label.Invoke(null, new[] { sys, point, field });
            object active = Activator.CreateInstance(activeType);
            aSystem.SetValue(active, sys); aPoint.SetValue(active, point); aReach.SetValue(active, reach); aLabel.SetValue(active, text);
            list.Add(active);
            int index = list.Count - 1, touched = 0;
            double lat = (double)pLat.GetValue(point), lon = (double)pLon.GetValue(point);
            StormSidecar.BinRange(lat, lon, reach, lat0, lon0, rows, cols, out int r0, out int r1, out int c0, out int c1);
            for (int r = r0; r <= r1; r++)
                for (int c = c0; c <= c1; c++)
                {
                    int cell = r * cols + c;
                    (cells[cell] ?? (cells[cell] = new List<int>())).Add(index);
                    touched++;
                }
            added++;
            if (Diagnostics) LogHour(set.Specs[k], utc, text, lat, lon, (double)pVmax.GetValue(point), reach, touched, native);
        }
        return added;
    }

    private static void LogHour(StormSpec s, DateTime utc, string text, double lat, double lon, double vmax, double reach, int touched, int native)
    {
        long hour = (long)Math.Floor((utc - Epoch).TotalHours);
        lock (gate)
        {
            // Once per storm and campaign hour, however many snapshots
            // (every distinct time, forecasts included) that hour builds.
            if (loggedHours.Count > 20000) loggedHours.Clear();
            if (!loggedHours.Add(s.Id + "@" + hour.ToString(CultureInfo.InvariantCulture))) return;
        }
        Api.Log("world storms: " + utc.ToString("yyyy-MM-dd HH", CultureInfo.InvariantCulture) + ":00Z sest-" + s.Id + " \"" + text + "\" at " + LatLon(lat, lon) +
                ", " + Num(vmax, "0") + " kn, reach " + Num(reach, "0") + " nm, " + touched + " bins, beside " + native + " DCM systems");
    }

    // Diagnostics: postfix on Battles.WeatherOf(Engagement), the weather the
    // contact screen shows and Battles.Plan stores for battle_{id}.ini
    // [Environment] (SeaState=, Clouds=, WindDirection=, Weather=Special).
    internal static void AfterWeatherOf(object __0, object __result)
    {
        if (!Diagnostics || __0 == null || __result == null) return;
        try
        {
            int id = (int)eId.GetValue(__0);
            object p = ePoint.GetValue(__0);
            var at = (DateTime)eAt.GetValue(__0);
            string env = "SeaState=" + wSeaState.GetValue(__result) + " Clouds=" + (wClouds.GetValue(__result) ?? "Scattered") +
                         " WindDirection=" + (wWindFrom.GetValue(__result) ?? "NE") + " Weather=" + (special.Invoke(__result, null) ?? "(none)") +
                         " (WindKnots=" + wWindKnots.GetValue(__result) + " Typhoon=" + wTyphoon.GetValue(__result) + " Storm=" + (wStorm.GetValue(__result) ?? "(none)") + ")";
            lock (gate)
            {
                if (loggedBattle.TryGetValue(id, out string last) && last == env) return;
                loggedBattle[id] = env;
            }
            Api.Log("world storms: contact " + id + " at " + LatLon((double)gLat.GetValue(p), (double)gLon.GetValue(p)) + " " +
                    at.ToString("yyyy-MM-dd HH:mm'Z'", CultureInfo.InvariantCulture) + " battle [Environment]: " + env);
        }
        catch (Exception ex) { Api.LogFailure("world storms battle-weather diagnostics", ex); }
    }
}
