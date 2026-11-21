using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Threading;
using SeaPower;
using UnityEngine;
using Environment = SeaPower.Environment;
using UnityEngine.Rendering;

namespace Sest.RuntimeFixes;

// The visible pack ice of a battle (SeaIceSheet=1 in [Runtime], default on
// under SeaIce=1): a continuous ice sheet floating on the sea wherever the
// modelled concentration reaches the edge threshold (15 %), with leads and
// holes from the deterministic lead field (SeaIceField: the share of ice is
// the concentration, the pattern is fixed per place and date). Built in code
// from procedural meshes and one material on a game shader; no image files.
//
// Chunks in three nested levels around the camera (1 km chunks over an
// 8 km square, 4 km chunks to 32 km, 16 km chunks to 96 km), 32 x 32
// marching-squares cells each, so a level is about 31 m, 125 m and 500 m per
// cell. Near chunks have an underside at -2 m and edge walls, so periscope
// and underwater cameras see the ice from below. Meshes are built on the
// thread pool (pure arrays, IceMesher); builds are queued nearest first as
// soon as a slot frees (not only on the 0.5 s layout tick, and at once after
// a camera jump), and uploaded within a per-frame time budget (2 ms, 3 ms
// while a refill is under way; at least one per frame). The sheet is double
// buffered: a chunk the camera left, or every chunk at a date change, stays
// drawn (sunk 0.15 m) until the chunks replacing its area are ready, so the
// pack never blinks out to open water.
// Height (IceSheetRule): each chunk rides the sea surface Ceto reports at
// five points over it (sea level 0 without Ceto), plus half the sea state's
// significant wave height, capped so the underside stays at least 1 m below
// that surface (and below the lowest sample): a held submarine always has
// ice overhead. Near a surface unit the top is kept at or below its
// waterline, so ships are not buried in the slab.
// The sheet is anchored in the battle's geo frame and placed through the
// game's own Utils.longLatToLocalV3(geo, Globals._currentCenterTile), so it
// stays put when the game recentres its floating origin. It is visual only:
// no collider (ships are held by the speed cap; a collider would also stop
// torpedoes, shells and sensor rays). Submarines pass under it.
//
// If the sheet cannot be built (no usable shader, a mesh failure), the driver
// falls back to small flat floes (Unity cubes, scaled flat, default material)
// within 3 km of the camera, riding Ceto's waves (re-placed at once when the
// game recentres its origin, keeping each floe's wave height); the log says
// which ran. When the battle ends every chunk and floe object and its mesh
// is destroyed.
public sealed class SeaIceSheetDriver : MonoBehaviour
{
    private void Update() { SeaIceSheet.Tick(); }
}

internal static class SeaIceSheet
{
    private static readonly double[] Sizes = { 1.0, 4.0, 16.0 };
    private static readonly int[] Spans = { 2, 2 };
    private const int Outer = 6, Cells = 32;
    private const double JumpKm = 1.0;
    private static readonly int MaxBuilding = Math.Max(6, Math.Min(32, System.Environment.ProcessorCount * 2));
    internal static double FreeboardM = 0.5, DraftM = 2.0, RidgeM = 1.2, LiftOverrideM = double.NaN;
    private static GameObject root;
    private static Material material;
    private static string shaderName = "", mode = "off";
    private static bool started, failed, floeMode;
    private static int floeCap = 300;

    private sealed class Chunk
    {
        internal IceMesher.ChunkKey Key;
        internal GameObject Go;
        internal Mesh Mesh;
        internal bool Building, Empty, Stale, HasY;
        internal int Triangles, Generation;
        internal double East, North;
        internal float StaleSince, Y;
    }
    private sealed class Built
    {
        internal IceMesher.ChunkKey Key;
        internal IceChunkMesh Mesh;
        internal int Generation;
        internal double Ms;
    }
    private static readonly Dictionary<IceMesher.ChunkKey, Chunk> chunks = new Dictionary<IceMesher.ChunkKey, Chunk>();
    private static readonly Stack<GameObject> pool = new Stack<GameObject>();
    private static readonly List<Chunk> stale = new List<Chunk>();
    private static List<IceMesher.ChunkKey> wanted = new List<IceMesher.ChunkKey>(), pending = new List<IceMesher.ChunkKey>();
    private static int pendingAt;
    private static IceFrame layoutFrame;
    private static DateTime layoutDate;
    private static double layoutE = double.NaN, layoutN = double.NaN;
    private static bool forceLayout;
    private static readonly List<Vector3> units = new List<Vector3>();
    private static readonly ConcurrentQueue<Built> done = new ConcurrentQueue<Built>();
    private static int building, generation;
    private static Environment lastEnv;
    private static int lastDate;
    private static Vector2 lastTile = new Vector2(float.NaN, float.NaN);
    private static float nextLayout, nextPlace, nextReport;
    private static double buildMs, uploadMs, worstUploadMs;
    private static int builds, uploads, retired;

    // Ceto, by reflection (Assets.dll is not a build reference): a closed
    // delegate over Ocean.Instance.QueryWaves(x, z, true), rebound when the
    // instance changes.
    private static PropertyInfo oceanInstance;
    private static MethodInfo queryWaves;
    private static object oceanBound;
    private static Func<float, float, bool, float> waves;
    private static string cetoState = "not bound";

    internal static void Install(string[] lines)
    {
        LiftOverrideM = double.TryParse(Policy.TextOption(lines, "SeaIceSheetLiftM", ""), NumberStyles.Float, CultureInfo.InvariantCulture, out double lift) && lift >= 0 && lift <= 10 ? lift : double.NaN;
        floeMode = Policy.TextOption(lines, "SeaIceSheetMode", "sheet") == "floes";
        if (int.TryParse(Policy.TextOption(lines, "SeaIceFloeCount", ""), NumberStyles.Integer, CultureInfo.InvariantCulture, out int cap) && cap >= 10 && cap <= 2000) floeCap = cap;
        root = new GameObject("SEST sea ice");
        UnityEngine.Object.DontDestroyOnLoad(root);
        root.AddComponent<SeaIceSheetDriver>();
        SeaIceBattle.MarkUnits = true;
        BindCeto();
        Api.Log("sea ice sheet driver installed (" + (floeMode ? "floes by SeaIceSheetMode=floes" : "continuous sheet, floe fallback") + "); Ceto: " + cetoState);
    }

    private static void BindCeto()
    {
        try
        {
            var type = AppDomain.CurrentDomain.GetAssemblies().Select(a => a.GetType("Ceto.Ocean", false)).FirstOrDefault(t => t != null);
            if (type == null) { cetoState = "Ceto.Ocean not loaded; sea level 0 is used"; return; }
            oceanInstance = type.GetProperty("Instance", BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic);
            queryWaves = type.GetMethod("QueryWaves", BindingFlags.Instance | BindingFlags.Public, null, new[] { typeof(float), typeof(float), typeof(bool) }, null);
            cetoState = oceanInstance != null && queryWaves != null && queryWaves.ReturnType == typeof(float) ? "Ocean.Instance.QueryWaves(float, float, bool) found" : "QueryWaves not found; sea level 0 is used";
            if (!(oceanInstance != null && queryWaves != null && queryWaves.ReturnType == typeof(float))) { oceanInstance = null; queryWaves = null; }
        }
        catch (Exception e) { cetoState = "Ceto bind failed (" + e.GetType().Name + "); sea level 0 is used"; oceanInstance = null; queryWaves = null; }
    }

    internal static float WaveAt(float x, float z)
    {
        if (oceanInstance == null) return 0f;
        try
        {
            var o = oceanInstance.GetValue(null, null);
            if (o == null || (o is UnityEngine.Object uo && uo == null)) { waves = null; oceanBound = null; return 0f; }
            if (!ReferenceEquals(o, oceanBound))
            {
                waves = (Func<float, float, bool, float>)Delegate.CreateDelegate(typeof(Func<float, float, bool, float>), o, queryWaves);
                oceanBound = o;
                if (SeaIceBattle.Diagnostics) Api.Log("sea ice: Ceto QueryWaves delegate bound to the battle's ocean");
            }
            float y = waves(x, z, true);
            return float.IsNaN(y) || float.IsInfinity(y) ? 0f : y;
        }
        catch (Exception e) { oceanInstance = null; Api.LogFailure("sea ice: Ceto QueryWaves unavailable, sea level 0 is used", e); return 0f; }
    }

    internal static void Tick()
    {
        if (failed || root == null) return;
        try
        {
            var env = SeaIceBattle.Env();
            var cam = Camera.main;
            if (cam == null) { foreach (var c in Camera.allCameras) if (c != null && c.enabled) { cam = c; break; } }
            if (env == null || cam == null)
            {
                if (lastEnv != null || chunks.Count > 0 || stale.Count > 0 || Floes.Count > 0) Clear();
                if (env == null && (pool.Count > 0 || Floes.Spare > 0)) DestroyPooled(); // battle over: free the objects and meshes
                lastEnv = null;
                return;
            }
            SeaIceBattle.Report(env);
            if (!ReferenceEquals(env, lastEnv)) { Clear(); lastEnv = env; started = false; SeaIceBattle.ClearSurfaceUnits(); }
            if (!started) { Start(); started = true; }
            var tile = Globals._currentCenterTile;
            var camGeo = Utils.worldPositionFromUnityToLongLat(cam.transform.position, tile);
            var frame = SeaIceBattle.Frame(env, camGeo._latitude, camGeo._longitude);
            frame.ToKm(camGeo._latitude, camGeo._longitude, out double camE, out double camN);
            var date = SeaIceBattle.Date(env);
            int dk = SeaIceTileCache.DateKeyOf(date);
            if (dk != lastDate) { RetireAll(); lastDate = dk; }
            float now = Time.realtimeSinceStartup;
            if (floeMode) { Floes.Tick(env, frame, camE, camN, date, tile, cam); Report(now, camGeo); return; }
            bool tileMoved = tile != lastTile;
            bool jumped = double.IsNaN(layoutE) || Math.Abs(camE - layoutE) > JumpKm || Math.Abs(camN - layoutN) > JumpKm;
            if (forceLayout || jumped || now >= nextLayout) { nextLayout = now + 0.5f; forceLayout = false; Layout(frame, camE, camN, date); }
            Fill();
            SeaIceBattle.SurfaceUnits(frame, units);
            Upload(frame, tile, env);
            RetireCovered(now);
            if (tileMoved || now >= nextPlace)
            {
                nextPlace = now + 2f; lastTile = tile;
                foreach (var c in chunks.Values) if (c.Go != null) Place(c, frame, tile, env);
                foreach (var c in stale) if (c.Go != null) Place(c, frame, tile, env);
            }
            else Heave(frame, env);
            Report(now, camGeo);
        }
        catch (Exception e)
        {
            Api.LogFailure("sea ice sheet failed; " + (floeMode ? "no ice is drawn" : "falling back to floes"), e);
            Clear();
            if (floeMode) failed = true;
            floeMode = true;
            mode = "floes (sheet failed)";
        }
    }

    private static void Start()
    {
        if (material == null && !floeMode)
        {
            material = MakeMaterial(out shaderName);
            if (material == null) { floeMode = true; mode = "floes (no shader)"; Api.Log("sea ice sheet: no usable shader (Standard, Legacy Shaders/Diffuse, Diffuse, Unlit/Texture, Hidden/Internal-Colored); falling back to floes"); }
            else mode = "sheet";
        }
        else if (floeMode && mode == "off") mode = "floes";
        Api.Log("sea ice visuals: " + mode + (material != null ? "; shader " + shaderName : "") + "; Ceto: " + cetoState);
    }

    // The first game shader that loads, white-grey like snow-covered land, with
    // a small procedural noise texture so the surface is not flat white.
    private static Material MakeMaterial(out string used)
    {
        used = "";
        foreach (var name in new[] { "Standard", "Legacy Shaders/Diffuse", "Diffuse", "Unlit/Texture", "Hidden/Internal-Colored" })
        {
            var shader = Shader.Find(name);
            if (shader == null) { if (SeaIceBattle.Diagnostics) Api.Log("sea ice sheet: Shader.Find(\"" + name + "\") = null"); continue; }
            var m = new Material(shader) { name = "SEST sea ice" };
            var tex = new Texture2D(128, 128, TextureFormat.RGBA32, true) { name = "SEST sea ice noise", wrapMode = TextureWrapMode.Repeat, filterMode = FilterMode.Trilinear };
            var px = new Color32[128 * 128];
            uint seed = 0xA5A5u;
            for (int j = 0; j < 128; j++)
                for (int i = 0; i < 128; i++)
                {
                    double n = SeaIceField.Noise(i / 12.0, j / 12.0, seed) * 0.6 + SeaIceField.Noise(i / 3.0, j / 3.0, seed + 7) * 0.4;
                    byte v = (byte)(214 + 36 * n);
                    px[j * 128 + i] = new Color32((byte)(v - 6), (byte)(v - 2), v, 255);
                }
            tex.SetPixels32(px);
            tex.Apply(true, true);
            m.mainTexture = tex;
            m.color = new Color(0.94f, 0.96f, 0.98f, 1f);
            if (m.HasProperty("_Glossiness")) m.SetFloat("_Glossiness", 0.12f);
            if (m.HasProperty("_Metallic")) m.SetFloat("_Metallic", 0f);
            used = name;
            return m;
        }
        return null;
    }

    // The wanted chunk set around the camera. Chunks no longer wanted stay drawn as stale ones until
    // their area is covered again (RetireCovered); missing ones are queued nearest first (Fill).
    private static void Layout(IceFrame frame, double camE, double camN, DateTime date)
    {
        var keys = IceMesher.Layout(camE, camN, Sizes, Spans, Outer);
        var want = new HashSet<IceMesher.ChunkKey>(keys);
        foreach (var k in chunks.Keys.Where(k => !want.Contains(k)).ToList()) Retire(k, Time.realtimeSinceStartup);
        wanted = keys;
        pending = IceMesher.NearestFirst(keys.Where(k => !chunks.ContainsKey(k)), camE, camN, Sizes);
        pendingAt = 0;
        layoutFrame = frame; layoutDate = date; layoutE = camE; layoutN = camN;
    }

    // Start builds while a thread-pool slot is free, nearest first.
    private static void Fill()
    {
        if (pendingAt >= pending.Count || building >= MaxBuilding) return;
        var env = SeaIceBattle.Env();
        if (env == null) return;
        uint seed = SeaIceBattle.Seed(env);
        var frame = layoutFrame;
        var date = layoutDate;
        while (pendingAt < pending.Count && building < MaxBuilding)
        {
            var k = pending[pendingAt++];
            if (chunks.ContainsKey(k)) continue;
            double size = Sizes[k.Level];
            var c = new Chunk { Key = k, Building = true, East = (k.I + 0.5) * size, North = (k.J + 0.5) * size, Generation = generation };
            chunks[k] = c;
            var spec = new IceChunkSpec { CentreEastKm = c.East, CentreNorthKm = c.North, SizeKm = size, Cells = Cells, Underside = k.Level == 0, FreeboardM = FreeboardM, DraftM = DraftM, RidgeM = k.Level == 0 ? RidgeM : RidgeM * 0.5, EdgePercent = SeaIceBattle.EdgePercent, Seed = seed };
            int gen = generation;
            Interlocked.Increment(ref building);
            ThreadPool.QueueUserWorkItem(_ =>
            {
                var sw = Stopwatch.StartNew();
                IceChunkMesh mesh = null;
                try
                {
                    mesh = IceMesher.Build(spec, (e, n) => { frame.ToGeo(e, n, out double lat, out double lon); return SeaIceBattle.Cache.Percent(lat, lon, date); });
                }
                catch (Exception ex) { mesh = null; Api.LogFailure("sea ice sheet: a chunk was not built", ex); }
                done.Enqueue(new Built { Key = k, Mesh = mesh, Generation = gen, Ms = sw.Elapsed.TotalMilliseconds });
                Interlocked.Decrement(ref building);
            });
        }
    }

    private static void Upload(IceFrame frame, Vector2 tile, Environment env)
    {
        double budget = IceSheetRule.Budget(pending.Count - pendingAt + building + done.Count);
        var frameClock = Stopwatch.StartNew();
        for (int u = 0; IceSheetRule.MayUpload(u, frameClock.Elapsed.TotalMilliseconds, budget) && done.TryDequeue(out var b);)
        {
            if (b.Generation != generation || !chunks.TryGetValue(b.Key, out var c) || !c.Building) continue;
            c.Building = false;
            buildMs += b.Ms; builds++;
            if (b.Mesh == null || b.Mesh.Triangles.Length == 0) { c.Empty = true; continue; }
            u++;
            var sw = Stopwatch.StartNew();
            var go = pool.Count > 0 ? pool.Pop() : NewChunkObject();
            var mesh = go.GetComponent<MeshFilter>().sharedMesh;
            mesh.Clear();
            int nv = b.Mesh.Vertices.Length / 3;
            mesh.indexFormat = nv > 65000 ? IndexFormat.UInt32 : IndexFormat.UInt16;
            var v = new Vector3[nv];
            var uv = new Vector2[nv];
            float tiling = 1f / (b.Key.Level == 0 ? 60f : b.Key.Level == 1 ? 240f : 960f);
            for (int i = 0; i < nv; i++)
            {
                v[i] = new Vector3(b.Mesh.Vertices[i * 3], b.Mesh.Vertices[i * 3 + 1], b.Mesh.Vertices[i * 3 + 2]);
                uv[i] = new Vector2(v[i].x * tiling, v[i].z * tiling);
            }
            mesh.vertices = v;
            mesh.uv = uv;
            mesh.triangles = b.Mesh.Triangles;
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            go.SetActive(true);
            c.Go = go; c.Mesh = mesh; c.Triangles = b.Mesh.TriangleCount;
            Place(c, frame, tile, env);
            double ms = sw.Elapsed.TotalMilliseconds;
            uploadMs += ms; uploads++; worstUploadMs = Math.Max(worstUploadMs, ms);
        }
    }

    // Release stale chunks whose area the wanted chunks cover again (or after 10 s, whatever happens).
    private static void RetireCovered(float now)
    {
        if (stale.Count == 0) return;
        Func<IceMesher.ChunkKey, bool> ready = k => chunks.TryGetValue(k, out var c) && !c.Building;
        for (int i = stale.Count - 1; i >= 0; i--)
        {
            var s = stale[i];
            if (now - s.StaleSince < 10f && !IceMesher.CanRetire(s.Key, wanted, ready, Sizes)) continue;
            stale.RemoveAt(i);
            ToPool(s);
            retired++;
        }
    }

    private static GameObject NewChunkObject()
    {
        var go = new GameObject("SEST sea ice chunk");
        go.transform.SetParent(root.transform, false);
        go.AddComponent<MeshFilter>().sharedMesh = new Mesh { name = "SEST sea ice" };
        var r = go.AddComponent<MeshRenderer>();
        r.sharedMaterial = material;
        r.shadowCastingMode = ShadowCastingMode.Off;
        r.receiveShadows = true;
        return go;
    }

    // Chunk centre through the game's own geo -> Unity conversion, with the
    // local east/north basis from two more conversions 1 km away; metres up
    // through the game's 220.472656 ft per Unity unit.
    private static void Place(Chunk c, IceFrame frame, Vector2 tile, Environment env)
    {
        frame.ToGeo(c.East, c.North, out double lat, out double lon);
        frame.ToGeo(c.East + 1, c.North, out double latE, out double lonE);
        frame.ToGeo(c.East, c.North + 1, out double latN, out double lonN);
        var p = Utils.longLatToLocalV3(new GeoPosition { _latitude = lat, _longitude = lon, _height = 0 }, tile);
        var pe = Utils.longLatToLocalV3(new GeoPosition { _latitude = latE, _longitude = lonE, _height = 0 }, tile);
        var pn = Utils.longLatToLocalV3(new GeoPosition { _latitude = latN, _longitude = lonN, _height = 0 }, tile);
        Vector3 east = (pe - p) / 1000f, north = (pn - p) / 1000f;
        float yaw = Mathf.Atan2(east.z, east.x) * Mathf.Rad2Deg;
        float up = SubIceRule.MetersToUnity(1.0);
        var t = c.Go.transform;
        t.position = new Vector3(p.x, c.HasY ? c.Y : 0f, p.z);
        t.rotation = Quaternion.Euler(0, -yaw, 0);
        t.localScale = new Vector3(east.magnitude, up, north.magnitude);
        Height(c, env, false);
    }

    // The chunk's height from IceSheetRule: the sea surface over it (five Ceto samples), the capped
    // lift, the waterline of surface units on or near it; stale chunks sit a little lower. Rises are
    // smoothed, falls are immediate, so the underside and waterline limits always hold.
    private static void Height(Chunk c, Environment env, bool snap)
    {
        var t = c.Go.transform;
        double unitPerM = SubIceRule.MetersToUnity(1.0);
        double half = Sizes[c.Key.Level] * 500.0, q = half * 0.5;
        double sum = 0, min = double.MaxValue;
        for (int i = 0; i < 5; i++)
        {
            double dx = i == 1 ? q : i == 2 ? -q : 0, dz = i == 3 ? q : i == 4 ? -q : 0;
            var w = t.TransformPoint(new Vector3((float)dx, 0, (float)dz));
            double m = WaveAt(w.x, w.z) / unitPerM;
            sum += m; min = Math.Min(min, m);
        }
        double waterline = double.NaN, reach = Sizes[c.Key.Level] / 2 + IceSheetRule.NearUnitKm;
        for (int i = 0; i < units.Count; i++)
        {
            var u = units[i];
            if (Math.Abs(u.x - c.East) <= reach && Math.Abs(u.y - c.North) <= reach) // x, y: east, north km; z: waterline
            {
                double wl = u.z / unitPerM;
                waterline = double.IsNaN(waterline) ? wl : Math.Min(waterline, wl);
            }
        }
        double y = IceSheetRule.ChunkY(sum / 5, min, LiftMeters(env), FreeboardM, DraftM, waterline) - (c.Stale ? IceSheetRule.StaleSinkM : 0);
        float target = (float)(y * unitPerM);
        if (snap || !c.HasY || target < c.Y) c.Y = target;
        else c.Y += (target - c.Y) * Mathf.Clamp01(Time.deltaTime * 8f / 2f);
        c.HasY = true;
        var p = t.position;
        t.position = new Vector3(p.x, c.Y, p.z);
    }

    // Every eighth drawn chunk per frame rides the waves (about 20 chunks, 100 QueryWaves calls).
    private static int heaveFrame;
    private static void Heave(IceFrame frame, Environment env)
    {
        int phase = heaveFrame++ & 7, k = 0;
        foreach (var c in chunks.Values) if (c.Go != null && (k++ & 7) == phase) Height(c, env, false);
        foreach (var c in stale) if (c.Go != null && (k++ & 7) == phase) Height(c, env, false);
    }

    // Half the WMO significant wave height of the battle's sea state (SeaIceSheetLiftM overrides),
    // capped so the slab's underside stays below the sea surface (IceSheetRule.Lift).
    internal static double LiftMeters(Environment env)
    {
        int ss = 0;
        try { ss = env != null ? env.SeaState : 0; } catch { }
        return IceSheetRule.Lift(SeaStateHs(ss), LiftOverrideM, DraftM);
    }

    // WMO sea state code, middle of each band, metres.
    internal static double SeaStateHs(int seaState)
    {
        double[] hs = { 0, 0.05, 0.3, 0.875, 1.875, 3.25, 5.0, 7.5, 11.5, 14 };
        return hs[Math.Max(0, Math.Min(hs.Length - 1, seaState))];
    }

    private static void ToPool(Chunk c)
    {
        if (c.Go != null) { c.Go.SetActive(false); pool.Push(c.Go); c.Go = null; }
    }

    // A chunk the layout no longer wants: drawn chunks become stale (kept until covered), others go.
    private static void Retire(IceMesher.ChunkKey k, float now)
    {
        if (!chunks.TryGetValue(k, out var c)) return;
        chunks.Remove(k);
        if (c.Go == null) return;
        c.Stale = true; c.StaleSince = now;
        stale.Add(c);
    }

    // Date change: every drawn chunk is rebuilt for the new date and stays drawn until then.
    private static void RetireAll()
    {
        generation++;
        float now = Time.realtimeSinceStartup;
        foreach (var k in chunks.Keys.ToList()) Retire(k, now);
        chunks.Clear();
        forceLayout = true;
    }

    private static void Clear()
    {
        generation++;
        foreach (var c in chunks.Values) ToPool(c);
        chunks.Clear();
        foreach (var c in stale) ToPool(c);
        stale.Clear();
        pending = new List<IceMesher.ChunkKey>(); pendingAt = 0; wanted = new List<IceMesher.ChunkKey>();
        layoutE = layoutN = double.NaN;
        forceLayout = true;
        Floes.Clear();
    }

    // Battle over: destroy pooled chunk objects with their meshes, and the floe objects.
    private static void DestroyPooled()
    {
        int n = pool.Count;
        while (pool.Count > 0)
        {
            var go = pool.Pop();
            if (go == null) continue;
            var mf = go.GetComponent<MeshFilter>();
            if (mf != null && mf.sharedMesh != null) UnityEngine.Object.Destroy(mf.sharedMesh);
            UnityEngine.Object.Destroy(go);
        }
        int f = Floes.DestroySpare();
        if (SeaIceBattle.Diagnostics) Api.Log("sea ice visuals: battle over, " + n + " chunk objects and " + f + " floes destroyed");
    }

    private static void Report(float now, GeoPosition camGeo)
    {
        if (!SeaIceBattle.Diagnostics || now < nextReport) return;
        nextReport = now + 10f;
        int active = 0, empty = 0, tris = 0, visible = 0;
        foreach (var c in chunks.Values)
        {
            if (c.Go != null) { active++; tris += c.Triangles; if (c.Go.GetComponent<MeshRenderer>().isVisible) visible++; }
            else if (c.Empty) empty++;
        }
        var env = SeaIceBattle.Env();
        var cam = Camera.main;
        float wave = cam != null ? WaveAt(cam.transform.position.x, cam.transform.position.z) : 0f;
        Api.Log("sea ice visuals (" + mode + "): camera at " + SeaIceBattle.Geo(camGeo) + " ice " + SeaIceBattle.Pct(SeaIceBattle.Cache.Percent(camGeo._latitude, camGeo._longitude, SeaIceBattle.Date(env))) + (cam != null && cam.transform.position.y < 0 ? " (camera under water)" : "") +
            "; chunks " + active + " drawn (" + visible + " visible), " + stale.Count + " stale kept until covered, " + retired + " retired, " + empty + " empty, " + building + " building, " + (pending.Count - pendingAt) + " queued, " + tris + " triangles; " + builds + " built in " + (builds > 0 ? buildMs / builds : 0).ToString("0.0", CultureInfo.InvariantCulture) + " ms each (thread pool), " + uploads + " uploads " + (uploads > 0 ? uploadMs / uploads : 0).ToString("0.00", CultureInfo.InvariantCulture) + " ms avg, worst " + worstUploadMs.ToString("0.00", CultureInfo.InvariantCulture) + " ms (main thread); lift " + LiftMeters(env).ToString("0.0", CultureInfo.InvariantCulture) + " m (cap " + IceSheetRule.MaxLift(DraftM).ToString("0.0", CultureInfo.InvariantCulture) + "), surface units " + units.Count + ", Ceto wave at camera " + (wave / SubIceRule.MetersToUnity(1)).ToString("0.0", CultureInfo.InvariantCulture) + " m; floes " + Floes.Count);
        builds = uploads = retired = 0; buildMs = uploadMs = worstUploadMs = 0;
    }

    // The fallback: flat floes riding the waves near the camera.
    private static class Floes
    {
        private static readonly Dictionary<long, GameObject> live = new Dictionary<long, GameObject>();
        private static readonly Stack<GameObject> spare = new Stack<GameObject>();
        private static float nextPlace;
        private static int round;
        private static Vector2 placedTile = new Vector2(float.NaN, float.NaN);
        internal static int Count => live.Count;
        internal static int Spare => spare.Count;

        internal static void Tick(Environment env, IceFrame frame, double camE, double camN, DateTime date, Vector2 tile, Camera cam)
        {
            float now = Time.realtimeSinceStartup;
            // re-placed every second, and at once when the game recentres its floating origin
            if (now >= nextPlace || tile != placedTile)
            {
                nextPlace = now + 1f;
                placedTile = tile;
                var sw = Stopwatch.StartNew();
                uint seed = SeaIceBattle.Seed(env);
                var slots = FloePlacement.Slots(camE, camN, 3.0, 0.12, (e, n) =>
                {
                    frame.ToGeo(e, n, out double lat, out double lon);
                    double f = SeaIceField.DrawnFraction(SeaIceBattle.Cache.Percent(lat, lon, date), SeaIceBattle.EdgePercent);
                    return f;
                }, seed, floeCap);
                var keep = new HashSet<long>(slots.Select(s => s.Id));
                foreach (var id in live.Keys.Where(id => !keep.Contains(id)).ToList()) { live[id].SetActive(false); spare.Push(live[id]); live.Remove(id); }
                float rideM = SubIceRule.MetersToUnity(0.3);
                foreach (var s in slots)
                {
                    bool had = live.TryGetValue(s.Id, out var go);
                    if (!had)
                    {
                        go = spare.Count > 0 ? spare.Pop() : Make();
                        live[s.Id] = go;
                    }
                    frame.ToGeo(s.East, s.North, out double lat, out double lon);
                    var p = Utils.longLatToLocalV3(new GeoPosition { _latitude = lat, _longitude = lon, _height = 0 }, tile);
                    float size = SubIceRule.MetersToUnity(s.SizeM);
                    // an existing floe keeps its wave height; a new one gets it now (never snapped to 0)
                    float y = had ? go.transform.position.y : WaveAt(p.x, p.z) + rideM;
                    go.transform.position = new Vector3(p.x, y, p.z);
                    go.transform.rotation = Quaternion.Euler(0, (float)s.YawDeg, 0);
                    go.transform.localScale = new Vector3(size, SubIceRule.MetersToUnity(1.5), size * 0.7f);
                    go.SetActive(true);
                }
                if (SeaIceBattle.Diagnostics && round++ % 10 == 0) Api.Log("sea ice floes: " + live.Count + " placed in " + sw.Elapsed.TotalMilliseconds.ToString("0.0", CultureInfo.InvariantCulture) + " ms");
            }
            // a quarter of the floes ride the waves each frame
            int k = 0, phase = Time.frameCount & 3;
            foreach (var go in live.Values)
            {
                if ((k++ & 3) != phase) continue;
                var p = go.transform.position;
                go.transform.position = new Vector3(p.x, WaveAt(p.x, p.z) + SubIceRule.MetersToUnity(0.3), p.z);
            }
        }

        private static GameObject Make()
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = "SEST sea ice floe";
            go.transform.SetParent(root.transform, false);
            foreach (var c in go.GetComponents<Component>())
                if (c != null && c.GetType().Name.EndsWith("Collider", StringComparison.Ordinal)) UnityEngine.Object.Destroy(c);
            var r = go.GetComponent<Renderer>();
            if (r != null) { if (material != null) r.sharedMaterial = material; else r.material.color = new Color(0.92f, 0.95f, 0.97f); r.shadowCastingMode = ShadowCastingMode.Off; }
            return go;
        }

        internal static void Clear()
        {
            foreach (var go in live.Values) { if (go != null) { go.SetActive(false); spare.Push(go); } }
            live.Clear();
            placedTile = new Vector2(float.NaN, float.NaN);
        }

        // Battle over: the spare floes go (the cube mesh is Unity's shared primitive; an own material instance goes with it).
        internal static int DestroySpare()
        {
            int n = 0;
            while (spare.Count > 0)
            {
                var go = spare.Pop();
                if (go == null) continue;
                var r = go.GetComponent<Renderer>();
                if (r != null && r.sharedMaterial != null && r.sharedMaterial != material) UnityEngine.Object.Destroy(r.sharedMaterial);
                UnityEngine.Object.Destroy(go);
                n++;
            }
            return n;
        }
    }
}
