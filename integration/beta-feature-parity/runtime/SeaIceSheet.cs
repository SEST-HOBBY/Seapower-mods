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
// cell. Every chunk is a closed slab (IceMesher: top, underside, one-sided
// outward walls along the ice contour and the chunk border; watertight), so
// the sea surface never shows between the top and the underside and the
// underside is seen from a periscope or an underwater camera. Near chunks are
// 2 m thick, far chunks 3.5 m (a higher lift cap: wave crests stay under the
// top at long range, where they read as mirror-like water through the pack).
// Far chunks have straight-up normals (no specular shimmer). Near (1 km and
// 4 km) chunks also register a Ceto clip overlay (the ocean's own mechanism,
// WaveOverlay + OverlayClipTexture, the overlay type the game builds for its
// shockwave rings) whose mask is the slab's solid interior eroded by one or
// two cells, so the ocean surface is not drawn inside the slab even when a
// crest rises above its top (SeaIceOceanClip=1, default on).
// Material (IceLook): the first of Legacy Diffuse / Diffuse (Lambert: lit by
// the sun and ambient, darker at night, takes fog, no Fresnel or environment
// reflection), Standard with highlights and glossy reflections off,
// VertexLit, unlit; albedo 0.80 (SeaIceAlbedo), smoothness 0.12
// (SeaIceSmoothness), metallic 0, faint blue tint, reflection probes off;
// SeaIceShader=<name> tries a named shader first. The choice, its keywords
// and values, and the scene's fog and ambient are logged.
// Channels carved by ships (IceCarve, SeaIceCarve=1): the 1 km chunks a
// channel touches are rebuilt (at most four at a time, the old mesh drawn
// until the new one is ready) at 64 cells (16 m) so a channel 1.5 x beam
// wide shows with ragged edges; coarser chunks do not show channels (their
// cells are 125 m and 500 m). Meshes are built on the
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
    internal static double FreeboardM = 0.5, DraftM = 2.0, DraftFarM = 3.5, RidgeM = 1.2, LiftOverrideM = double.NaN;
    internal static double Albedo = IceLook.DefaultAlbedo, Smoothness = IceLook.DefaultSmoothness;
    private static string shaderOverride = "", materialLine = "";
    internal static bool OceanClip = true;
    private const int CarveCells = 64, MaxRebuilding = 4;
    private static int rebuilding, rebuilds;
    private static readonly HashSet<IceMesher.ChunkKey> rebuildLater = new HashSet<IceMesher.ChunkKey>();
    internal static double Draft(int level) => level == 0 ? DraftM : DraftFarM;
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
        internal bool Building, Empty, Stale, HasY, Rebuild;
        internal int Triangles, Generation;
        internal double East, North;
        internal float StaleSince, Y;
        internal bool[] Clip;          // Ceto clip mask (Cells x Cells), near chunks
        internal int ClipCells;
        internal Texture2D ClipTex;
        internal object Overlay;       // Ceto.WaveOverlay
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
        Albedo = IceLook.Albedo(Policy.TextOption(lines, "SeaIceAlbedo", ""));
        Smoothness = IceLook.Smoothness(Policy.TextOption(lines, "SeaIceSmoothness", ""));
        shaderOverride = Policy.TextOption(lines, "SeaIceShader", "").Trim();
        OceanClip = Policy.TextOption(lines, "SeaIceOceanClip", "1") == "1";
        root = new GameObject("SEST sea ice");
        UnityEngine.Object.DontDestroyOnLoad(root);
        root.AddComponent<SeaIceSheetDriver>();
        SeaIceBattle.MarkUnits = true;
        BindCeto();
        if (OceanClip) CetoClip.Bind(); else CetoClip.State = "off (SeaIceOceanClip=0)";
        SeaIceEffects.Install(lines, root);
        Api.Log("sea ice sheet driver installed (" + (floeMode ? "floes by SeaIceSheetMode=floes" : "continuous sheet, floe fallback") + "); Ceto: " + cetoState + "; ocean clip: " + CetoClip.State + "; albedo " + Albedo.ToString("0.00", CultureInfo.InvariantCulture) + ", smoothness " + Smoothness.ToString("0.00", CultureInfo.InvariantCulture));
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

    internal static object OceanNow()
    {
        if (oceanInstance == null) return null;
        try { var o = oceanInstance.GetValue(null, null); return o == null || (o is UnityEngine.Object uo && uo == null) ? null : o; }
        catch { return null; }
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
            SeaIceEffects.Tick(env, frame, camE, camN, tile, cam, material);
            if (floeMode) { Floes.Tick(env, frame, camE, camN, date, tile, cam); Report(now, camGeo); return; }
            bool tileMoved = tile != lastTile;
            bool jumped = double.IsNaN(layoutE) || Math.Abs(camE - layoutE) > JumpKm || Math.Abs(camN - layoutN) > JumpKm;
            if (forceLayout || jumped || now >= nextLayout) { nextLayout = now + 0.5f; forceLayout = false; Layout(frame, camE, camN, date); }
            Fill();
            Rebuilds();
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
        Api.Log("sea ice visuals: " + mode + (material != null ? "; shader " + shaderName : "") + "; Ceto: " + cetoState + "; ocean clip: " + CetoClip.State);
        if (material != null && SeaIceBattle.Diagnostics) Api.Log("sea ice material: " + materialLine + "; " + SceneLight());
    }

    // The first shader of IceLook.Shaders that loads (SeaIceShader first when set), set up matt:
    // albedo SeaIceAlbedo with a faint blue tint over a small procedural noise texture (mean 1),
    // smoothness SeaIceSmoothness, metallic 0; on Standard, specular highlights and glossy
    // (environment) reflections switched off, so the pack never reads as a mirror.
    private static Material MakeMaterial(out string used)
    {
        used = "";
        var names = new List<string>();
        if (shaderOverride.Length > 0) names.Add(shaderOverride);
        names.AddRange(IceLook.Shaders);
        foreach (var name in names)
        {
            Shader shader = null;
            try { shader = Shader.Find(name); } catch { }
            if (shader == null) { if (SeaIceBattle.Diagnostics) Api.Log("sea ice sheet: Shader.Find(\"" + name + "\") = null"); continue; }
            if (!shader.isSupported) { if (SeaIceBattle.Diagnostics) Api.Log("sea ice sheet: shader " + name + " not supported here"); continue; }
            var m = new Material(shader) { name = "SEST sea ice" };
            var tex = new Texture2D(128, 128, TextureFormat.RGBA32, true) { name = "SEST sea ice noise", wrapMode = TextureWrapMode.Repeat, filterMode = FilterMode.Trilinear, anisoLevel = 4 };
            var px = new Color32[128 * 128];
            uint seed = 0xA5A5u;
            for (int j = 0; j < 128; j++)
                for (int i = 0; i < 128; i++)
                {
                    double n = SeaIceField.Noise(i / 12.0, j / 12.0, seed) * 0.6 + SeaIceField.Noise(i / 3.0, j / 3.0, seed + 7) * 0.4;
                    byte v = IceLook.TextureByte(n);
                    px[j * 128 + i] = new Color32(v, v, v, 255);
                }
            tex.SetPixels32(px);
            tex.Apply(true, true);
            m.mainTexture = tex;
            IceLook.Colour(IceLook.IsUnlit(name) ? Albedo * IceLook.UnlitScale : Albedo, out double r, out double g, out double b);
            m.color = new Color((float)r, (float)g, (float)b, 1f);
            if (m.HasProperty("_Glossiness")) m.SetFloat("_Glossiness", (float)Smoothness);
            if (m.HasProperty("_GlossMapScale")) m.SetFloat("_GlossMapScale", (float)Smoothness);
            if (m.HasProperty("_Metallic")) m.SetFloat("_Metallic", 0f);
            if (m.HasProperty("_SpecularHighlights")) m.SetFloat("_SpecularHighlights", 0f);
            if (m.HasProperty("_GlossyReflections")) m.SetFloat("_GlossyReflections", 0f);
            if (m.HasProperty("_Shininess")) m.SetFloat("_Shininess", 0.03f);
            if (m.HasProperty("_SpecColor")) m.SetColor("_SpecColor", Color.black);
            if (name == "Standard") foreach (var k in IceLook.StandardMattKeywords) m.EnableKeyword(k);
            m.DisableKeyword("_EMISSION");
            if (m.HasProperty("_EmissionColor")) m.SetColor("_EmissionColor", Color.black);
            used = name;
            float gloss = m.HasProperty("_Glossiness") ? m.GetFloat("_Glossiness") : 0f, metal = m.HasProperty("_Metallic") ? m.GetFloat("_Metallic") : 0f;
            materialLine = "shader " + name + " (render queue " + m.renderQueue + "), colour " + F(m.color.r) + "/" + F(m.color.g) + "/" + F(m.color.b) + " (albedo " + F(Albedo) + (IceLook.IsUnlit(name) ? " x unlit " + F(IceLook.UnlitScale) : "") + ", texture mean " + F(IceLook.TextureMean) + ")" +
                ", smoothness " + (m.HasProperty("_Glossiness") ? F(gloss) : "n/a (" + (name.Contains("Diffuse") ? "Lambert, no specular" : "no gloss property") + ")") + ", metallic " + (m.HasProperty("_Metallic") ? F(metal) : "n/a") +
                ", keywords [" + string.Join(" ", m.shaderKeywords ?? new string[0]) + "], emission off, reflection probes off, shadows received not cast; matt " + IceLook.Matt(gloss, metal);
            return m;
        }
        return null;
    }

    private static string F(double v) => v.ToString("0.00", CultureInfo.InvariantCulture);

    // The scene's light the matt material follows: fog, ambient, sun.
    private static string SceneLight()
    {
        try
        {
            var sun = RenderSettings.sun;
            return "scene fog " + (RenderSettings.fog ? RenderSettings.fogMode + " density " + RenderSettings.fogDensity.ToString("0.00000", CultureInfo.InvariantCulture) + " colour " + F(RenderSettings.fogColor.r) + "/" + F(RenderSettings.fogColor.g) + "/" + F(RenderSettings.fogColor.b) : "off (any fog is then the game's own post effect on depth, which covers opaque ice too)") +
                ", ambient " + RenderSettings.ambientMode + " " + F(RenderSettings.ambientLight.r) + "/" + F(RenderSettings.ambientLight.g) + "/" + F(RenderSettings.ambientLight.b) + " x " + F(RenderSettings.ambientIntensity) +
                ", sun " + (sun != null ? sun.name + " intensity " + F(sun.intensity) + " shadows " + sun.shadows : "none set");
        }
        catch (Exception e) { return "scene light unavailable (" + e.GetType().Name + ")"; }
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
        while (pendingAt < pending.Count && building < MaxBuilding)
        {
            var k = pending[pendingAt++];
            if (chunks.ContainsKey(k)) continue;
            double size = Sizes[k.Level];
            var c = new Chunk { Key = k, Building = true, East = (k.I + 0.5) * size, North = (k.J + 0.5) * size, Generation = generation };
            chunks[k] = c;
            StartBuild(c, env);
        }
    }

    // Channels: rebuild the drawn 1 km chunks the carve marked dirty (bounded: MaxRebuilding at a
    // time, the old mesh drawn until the new one is uploaded); a chunk still building is rebuilt
    // again once it is done; one not drawn is built with the channel when the layout wants it.
    private static void Rebuilds()
    {
        if (!SeaIceBattle.CarveOn) return;
        var env = SeaIceBattle.Env();
        if (env == null) return;
        foreach (var key in SeaIceBattle.Carve.TakeDirty(64))
        {
            IceCarve.ChunkOf(key, out int i, out int j);
            rebuildLater.Add(new IceMesher.ChunkKey { Level = 0, I = i, J = j });
        }
        if (rebuildLater.Count == 0) return;
        foreach (var k in rebuildLater.ToList())
        {
            if (rebuilding >= MaxRebuilding || building >= MaxBuilding) break;
            if (!chunks.TryGetValue(k, out var c) || c.Empty) { rebuildLater.Remove(k); continue; }
            if (c.Building) continue;
            rebuildLater.Remove(k);
            c.Building = true; c.Rebuild = true;
            rebuilding++;
            StartBuild(c, env);
        }
    }

    private static void StartBuild(Chunk c, Environment env)
    {
        var k = c.Key;
        uint seed = SeaIceBattle.Seed(env);
        var frame = layoutFrame;
        var date = layoutDate;
        double size = Sizes[k.Level];
        var carve = k.Level == 0 && SeaIceBattle.CarveOn ? SeaIceBattle.Carve.Published : null; // the published snapshot: the dirty marks handed out are in it
        if (carve != null && !carve.Touches(k.I, k.J)) carve = null;
        var spec = new IceChunkSpec { CentreEastKm = c.East, CentreNorthKm = c.North, SizeKm = size, Cells = carve != null ? CarveCells : Cells, Underside = true, FlatNormals = k.Level > 0, FreeboardM = FreeboardM, DraftM = Draft(k.Level), RidgeM = k.Level == 0 ? RidgeM : RidgeM * 0.5, EdgePercent = SeaIceBattle.EdgePercent, Seed = seed, Carve = carve };
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

    private static void Upload(IceFrame frame, Vector2 tile, Environment env)
    {
        double budget = IceSheetRule.Budget(pending.Count - pendingAt + building + done.Count);
        var frameClock = Stopwatch.StartNew();
        for (int u = 0; IceSheetRule.MayUpload(u, frameClock.Elapsed.TotalMilliseconds, budget) && done.TryDequeue(out var b);)
        {
            if (b.Generation != generation || !chunks.TryGetValue(b.Key, out var c) || !c.Building) continue;
            c.Building = false;
            if (c.Rebuild) { c.Rebuild = false; rebuilding = Math.Max(0, rebuilding - 1); rebuilds++; }
            buildMs += b.Ms; builds++;
            if (b.Mesh == null || b.Mesh.Triangles.Length == 0) { c.Empty = true; ToPool(c); continue; }
            u++;
            var sw = Stopwatch.StartNew();
            var go = c.Go != null ? c.Go : pool.Count > 0 ? pool.Pop() : NewChunkObject();
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
            if (b.Mesh.Normals.Length == b.Mesh.Vertices.Length)
            {
                var nr = new Vector3[nv];
                for (int i = 0; i < nv; i++) nr[i] = new Vector3(b.Mesh.Normals[i * 3], b.Mesh.Normals[i * 3 + 1], b.Mesh.Normals[i * 3 + 2]);
                mesh.normals = nr;
                mesh.triangles = b.Mesh.Triangles;
            }
            else { mesh.triangles = b.Mesh.Triangles; mesh.RecalculateNormals(); }
            mesh.RecalculateBounds();
            go.SetActive(true);
            c.Go = go; c.Mesh = mesh; c.Triangles = b.Mesh.TriangleCount;
            KillOverlay(c);
            c.Clip = OceanClip && CetoClip.Ready && b.Key.Level <= 1 ? IceMesher.ClipMask(b.Mesh.Solid, b.Mesh.Grid, b.Mesh.Grid >= CarveCells ? 2 : 1) : null;
            c.ClipCells = b.Mesh.Grid;
            Place(c, frame, tile, env);
            double ms = sw.Elapsed.TotalMilliseconds;
            uploadMs += ms; uploads++; worstUploadMs = Math.Max(worstUploadMs, ms);
        }
    }

    // Release stale chunks whose area the wanted chunks cover again (or after 10 s, whatever happens).
    private static void RetireCovered(float now)
    {
        if (stale.Count == 0) return;
        Func<IceMesher.ChunkKey, bool> ready = k => chunks.TryGetValue(k, out var c) && (!c.Building || c.Go != null);
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
        r.reflectionProbeUsage = ReflectionProbeUsage.Off;
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
        PlaceOverlay(c, p, -yaw, east.magnitude, north.magnitude);
    }

    // The chunk's Ceto clip overlay: created once the mask is known and the ocean is there, moved with
    // the chunk (a floating-origin recentre re-places every chunk at once).
    private static void PlaceOverlay(Chunk c, Vector3 p, float rotation, float unitPerMEast, float unitPerMNorth)
    {
        if (c.Clip == null || c.Stale || !CetoClip.Ready) { KillOverlay(c); return; }
        double half = Sizes[c.Key.Level] * 500.0;
        var halfSize = new Vector2((float)(half * unitPerMEast), (float)(half * unitPerMNorth));
        if (c.Overlay == null)
        {
            int n = c.ClipCells, solid = 0;
            if (n <= 0 || c.Clip.Length != n * n) { c.Clip = null; return; }
            if (c.ClipTex == null || c.ClipTex.width != n)
            {
                if (c.ClipTex != null) UnityEngine.Object.Destroy(c.ClipTex);
                c.ClipTex = new Texture2D(n, n, TextureFormat.RGBA32, false) { name = "SEST sea ice ocean clip", wrapMode = TextureWrapMode.Clamp, filterMode = FilterMode.Point };
            }
            var px = new Color32[n * n];
            for (int i = 0; i < px.Length; i++) { bool on = c.Clip[i]; if (on) solid++; px[i] = on ? new Color32(255, 255, 255, 255) : new Color32(0, 0, 0, 0); }
            if (solid == 0) { c.Clip = null; return; }
            c.ClipTex.SetPixels32(px); // row 0 is the south edge, column 0 the west edge, as the mesher's grid
            c.ClipTex.Apply(false, false);
            c.Overlay = CetoClip.Create(new Vector3(p.x, 0, p.z), rotation, halfSize, c.ClipTex);
        }
        else CetoClip.Move(c.Overlay, new Vector3(p.x, 0, p.z), rotation, halfSize);
    }

    private static void KillOverlay(Chunk c)
    {
        if (c.Overlay != null) { CetoClip.Kill(c.Overlay); c.Overlay = null; }
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
        double draft = Draft(c.Key.Level);
        double y = IceSheetRule.ChunkY(sum / 5, min, LiftMeters(env, draft), FreeboardM, draft, waterline) - (c.Stale ? IceSheetRule.StaleSinkM : 0);
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
    internal static double LiftMeters(Environment env) => LiftMeters(env, DraftM);
    internal static double LiftMeters(Environment env, double draft)
    {
        int ss = 0;
        try { ss = env != null ? env.SeaState : 0; } catch { }
        return IceSheetRule.Lift(SeaStateHs(ss), LiftOverrideM, draft);
    }

    // WMO sea state code, middle of each band, metres.
    internal static double SeaStateHs(int seaState)
    {
        double[] hs = { 0, 0.05, 0.3, 0.875, 1.875, 3.25, 5.0, 7.5, 11.5, 14 };
        return hs[Math.Max(0, Math.Min(hs.Length - 1, seaState))];
    }

    private static void ToPool(Chunk c)
    {
        KillOverlay(c);
        if (c.ClipTex != null) { UnityEngine.Object.Destroy(c.ClipTex); c.ClipTex = null; }
        c.Clip = null;
        if (c.Go != null) { c.Go.SetActive(false); pool.Push(c.Go); c.Go = null; }
    }

    // A chunk the layout no longer wants: drawn chunks become stale (kept until covered), others go.
    private static void Retire(IceMesher.ChunkKey k, float now)
    {
        if (!chunks.TryGetValue(k, out var c)) return;
        chunks.Remove(k);
        if (c.Rebuild) { c.Rebuild = false; rebuilding = Math.Max(0, rebuilding - 1); }
        if (c.Go == null) return;
        c.Stale = true; c.StaleSince = now;
        KillOverlay(c); // the replacement registers its own
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
        rebuildLater.Clear(); rebuilding = 0;
        pending = new List<IceMesher.ChunkKey>(); pendingAt = 0; wanted = new List<IceMesher.ChunkKey>();
        layoutE = layoutN = double.NaN;
        forceLayout = true;
        Floes.Clear();
        SeaIceEffects.Clear();
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
        SeaIceEffects.DestroyPooled();
        if (SeaIceBattle.Diagnostics) Api.Log("sea ice visuals: battle over, " + n + " chunk objects and " + f + " floes destroyed");
    }

    private static void Report(float now, GeoPosition camGeo)
    {
        if (!SeaIceBattle.Diagnostics || now < nextReport) return;
        nextReport = now + 10f;
        int active = 0, empty = 0, tris = 0, visible = 0, clips = 0, carved = 0;
        foreach (var c in chunks.Values)
        {
            if (c.Go != null) { active++; tris += c.Triangles; if (c.Go.GetComponent<MeshRenderer>().isVisible) visible++; if (c.Overlay != null) clips++; if (c.ClipCells >= CarveCells) carved++; }
            else if (c.Empty) empty++;
        }
        var env = SeaIceBattle.Env();
        var cam = Camera.main;
        float wave = cam != null ? WaveAt(cam.transform.position.x, cam.transform.position.z) : 0f;
        Api.Log("sea ice visuals (" + mode + "): camera at " + SeaIceBattle.Geo(camGeo) + " ice " + SeaIceBattle.Pct(SeaIceBattle.Cache.Percent(camGeo._latitude, camGeo._longitude, SeaIceBattle.Date(env))) + (cam != null && cam.transform.position.y < 0 ? " (camera under water)" : "") +
            "; chunks " + active + " drawn (" + visible + " visible), " + stale.Count + " stale kept until covered, " + retired + " retired, " + empty + " empty, " + building + " building, " + (pending.Count - pendingAt) + " queued, " + tris + " triangles; " + builds + " built in " + (builds > 0 ? buildMs / builds : 0).ToString("0.0", CultureInfo.InvariantCulture) + " ms each (thread pool), " + uploads + " uploads " + (uploads > 0 ? uploadMs / uploads : 0).ToString("0.00", CultureInfo.InvariantCulture) + " ms avg, worst " + worstUploadMs.ToString("0.00", CultureInfo.InvariantCulture) + " ms (main thread); lift " + LiftMeters(env).ToString("0.0", CultureInfo.InvariantCulture) + " m (cap " + IceSheetRule.MaxLift(DraftM).ToString("0.0", CultureInfo.InvariantCulture) + "), surface units " + units.Count + ", Ceto wave at camera " + (wave / SubIceRule.MetersToUnity(1)).ToString("0.0", CultureInfo.InvariantCulture) + " m; floes " + Floes.Count +
            "; slabs closed (near " + DraftM.ToString("0.0", CultureInfo.InvariantCulture) + " m, far " + DraftFarM.ToString("0.0", CultureInfo.InvariantCulture) + " m thick, far lift " + LiftMeters(env, DraftFarM).ToString("0.0", CultureInfo.InvariantCulture) + " m); ocean clip overlays " + clips + " (" + CetoClip.Describe() + "); channel chunks " + carved + " at " + CarveCells + " cells, " + rebuilds + " rebuilt in the last 10 s, " + rebuilding + " rebuilding, " + rebuildLater.Count + " waiting");
        if (material != null) Api.Log("sea ice material in use: " + materialLine);
        rebuilds = 0;
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
