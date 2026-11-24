using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq.Expressions;
using System.Reflection;
using System.Runtime.CompilerServices;
using UnityEngine;
using UnityEngine.Rendering;

namespace Sest.RuntimeFixes
{
    // Antarctic ice-shelf cliffs and icebergs inside Sea Power battles. A DROP-IN for the r16 battle
    // runtime (integration/beta-feature-parity/runtime on feature/mno-r16), NOT yet PC-tested.
    // Everything is OFF unless the owner sets it in plugins/sest_runtime.ini [Runtime]:
    //   IceShelves=1              shelf fronts drawn as ice cliffs; ships and submarines kept out
    //   Icebergs=1                icebergs from the climatology, drifting and (with a sea temperature) melting
    //   IceFeaturesDiagnostics=1  log lines (binding, battle origin, counts, the speed rule's holds)
    // Options (all optional; out-of-range values fall back to the default):
    //   IceShelfViewKm=30         draw cliffs within this distance of the camera (5-80)
    //   IceShelfStandoffNm=2      submarine stand-off from a front (0.5-10; data default 2 nm, an estimate)
    //   IcebergRadiusNm=25        bergs exist within this distance of the camera (5-60)
    //   IcebergViewKm=30          bergs are drawn within this distance (2-60), and never beyond their
    //                             class's day visual range (icebergs.visual_detection_nm)
    //   IcebergMaxDrawn=400       at most this many berg objects (20-3000)
    //   IcebergSeed=0             the generator seed (icebergs.generate's seed; same seed, same bergs)
    //   IcebergSstC=              sea temperature for melt, C (-2 to 15). Unset: no decay in the battle
    //                             (the game exposes no sea temperature this runtime has inspected).
    //
    // Game access is by reflection only (Api.FindType, named members, compiled getters), bound at
    // Install; any missing member logs one line and leaves that part out (fail closed). Unity types
    // are used directly, as in SeaIceSheet.cs (UnityEngine.CoreModule is a build reference).
    //
    // Where the inputs come from (the same places as SeaIceBattle / SeaIceSheet):
    // - battle date: Environment.get_DateTime (the mission clock; UTC in a Dynamic Campaign Mod battle);
    // - position: Utils.worldPositionFromUnityToLongLat(camera, Globals._currentCenterTile) for the
    //   camera, ObjectBase._geoPosition for units; placement through Utils.longLatToLocalV3;
    // - sea state: Environment.get_SeaState (diagnostics: radar factor of the nearest berg);
    // - game time: GameTime.missionElapsedTime when bound, else Unity's Time.time.
    //
    // The no-go rule (IceShelves=1): a postfix on Compartments.UpdateWantedVelocityInKnots, the same
    // hook SeaIceBattle caps ship speed in, for own AND AI units. It only lowers the wanted speed
    // (ShelfSpeedState). A hull whose direction of travel would take it into a shelf (surface) or
    // inside the stand-off of a front (submarine) keeps steerage way until it reaches the limit,
    // then stops closing; a move along or away from the front is never capped. Both postfixes may
    // run on one hull; each only lowers the speed, so their order does not matter.
    //
    // Visual only: no collider (a collider would also stop shells, torpedoes and sensor rays). The
    // bergs are not radar or sonar contacts: the sensor hooks (IcebergField.RadarDetectionNm,
    // FalseContact) are pure logic, logged with IceFeaturesDiagnostics=1, and not wired to the
    // game's sensors (no sensor member has been inspected for it).
    public sealed class IceFeaturesDriver : MonoBehaviour
    {
        private void Update() { IceFeaturesBattle.Tick(); }
    }

    internal static class IceFeaturesBattle
    {
        internal const string HarmonyId = "io.github.sest-hobby.ice-features";
        internal static bool ShelvesOn, BergsOn, Diagnostics, NoGoOn, VisualsOn;
        internal static double ShelfViewKm = 30, StandoffNm = IceFeaturesData.SubmarineStandoffNm, BergRadiusNm = 25, BergViewKm = 30, SstC = double.NaN;
        internal static int MaxDrawn = 400;
        internal static string Seed = "0";
        internal static string State = "not installed";
        internal static readonly List<string> Parts = new List<string>();
        internal static int Holds, Stops, PostfixCalls;
        internal static GameObject Root;

        // ---- bound game members ----
        private static Type envType, geoType;
        private static FieldInfo envInstance, geoLat, geoLon, geoHeight;
        private static MethodInfo envDate, envSeaState, toLocal, toGeo, yawToHeading, missionTime;
        private static FieldInfo centerTile;
        private static Func<object, object> baseObject, submarineOf, geoOf;
        private static Func<object, bool> sinking, immobile, isPlayer;
        private static Func<object, float> wantedGet;
        private static Action<object, float> wantedSet;
        private static Func<object, float[]> telegraph, telegraphSubmerged;
        private static MethodInfo isSubmerged;

        // ---- install ----------------------------------------------------------------------------

        internal static void Install(Assembly game, string[] lines) => Install(lines, Api.FindType);

        internal static void Install(string[] lines, Func<string, Type> find)
        {
            try
            {
                ShelvesOn = Policy.TextOption(lines, "IceShelves", "0") == "1";
                BergsOn = Policy.TextOption(lines, "Icebergs", "0") == "1";
                Diagnostics = Policy.TextOption(lines, "IceFeaturesDiagnostics", "0") == "1";
                Parts.Clear();
                if (!ShelvesOn && !BergsOn) { State = "off"; if (Diagnostics) Api.Log("ice features off (IceShelves=0, Icebergs=0)"); return; }
                ShelfViewKm = Number(lines, "IceShelfViewKm", 30, 5, 80);
                StandoffNm = Number(lines, "IceShelfStandoffNm", IceFeaturesData.SubmarineStandoffNm, 0.5, 10);
                BergRadiusNm = Number(lines, "IcebergRadiusNm", 25, 5, 60);
                BergViewKm = Number(lines, "IcebergViewKm", 30, 2, 60);
                MaxDrawn = (int)Number(lines, "IcebergMaxDrawn", 400, 20, 3000);
                SstC = Number(lines, "IcebergSstC", double.NaN, -2, 15);
                string seed = Policy.TextOption(lines, "IcebergSeed", "0").Trim();
                Seed = seed.Length > 0 && seed.Length <= 64 ? seed : "0";
                SelfCheck();
                BindCommon(find);
                if (ShelvesOn) Part("no-go rule for ships and submarines", () => { BindUnits(find); Api.Postfix(Api.Method(find("SeaPower.Compartments"), "UpdateWantedVelocityInKnots", typeof(void)), typeof(IceFeaturesBattle), nameof(SpeedPostfix), HarmonyId + ".no-go"); NoGoOn = true; });
                Part("visuals", () => { BindVisuals(find); Root = new GameObject("SEST ice features"); UnityEngine.Object.DontDestroyOnLoad(Root); Root.AddComponent<IceFeaturesDriver>(); VisualsOn = true; });
                State = "installed (" + string.Join(", ", Parts.ToArray()) + ")";
                Api.Log("ice features installed (" + (ShelvesOn ? "ice shelves" : "") + (ShelvesOn && BergsOn ? " and " : "") + (BergsOn ? "icebergs" : "") + "; " + string.Join(", ", Parts.ToArray()) +
                    "): Natural Earth 1:10m shelves (fronts about 2003-2012, estimate; outline simplified " + F(IceFeaturesData.ShelfToleranceKm) + " km), submarine stand-off " + F(StandoffNm) + " nm (estimate)" +
                    (BergsOn ? "; iceberg climatology ESTIMATE, seed " + Seed + ", radius " + F(BergRadiusNm) + " nm, " + (double.IsNaN(SstC) ? "no melt (IcebergSstC unset)" : "melt at " + F(SstC) + " C") : ""));
            }
            catch (Exception e)
            {
                ShelvesOn = BergsOn = NoGoOn = VisualsOn = false;
                State = "failed";
                Api.LogFailure("ice features not installed; battles keep the native sea", e);
            }
        }

        private static void Part(string name, Action install)
        {
            try { install(); Parts.Add(name); }
            catch (Exception e) { Api.LogFailure("ice features: " + name + " not installed; native behaviour kept", e); }
        }

        internal static double Number(string[] lines, string option, double fallback, double min, double max)
        {
            string text = Policy.TextOption(lines, option, "");
            return double.TryParse(text, NumberStyles.Float, CultureInfo.InvariantCulture, out double v) && v >= min && v <= max ? v : fallback;
        }

        // The tables first: a broken table installs nothing.
        private static void SelfCheck()
        {
            IceShelves.Load();
            int ross = IceShelves.ShelfAt(-80.0, -175.0);
            if (ross < 0 || IceFeaturesData.ShelfName[ross] != "Ross Ice Shelf") throw new InvalidOperationException("ice-shelf table check failed");
            double r = new PyRandom("mno-icebergs-selfcheck").Random();
            double d = IcebergField.Density(45.0, -49.0, 5.0)[(int)BergCategory.Small];
            if (r != IceFeaturesData.SelfCheckRandom || Math.Abs(d - IceFeaturesData.SelfCheckDensitySmall) > 1e-12 * Math.Max(1, d)) throw new InvalidOperationException("iceberg table check failed: " + r.ToString("R", CultureInfo.InvariantCulture) + ", " + d.ToString("R", CultureInfo.InvariantCulture));
        }

        private static MemberInfo Member(Type t, string name)
        {
            for (var x = t; x != null; x = x.BaseType)
            {
                var f = x.GetField(name, Api.All);
                if (f != null) return f;
                var p = x.GetProperty(name, Api.All);
                if (p != null && p.GetGetMethod(true) != null) return p;
            }
            throw new MissingMemberException(t.FullName, name);
        }

        private static Type TypeOf(MemberInfo m) => m is FieldInfo f ? f.FieldType : ((PropertyInfo)m).PropertyType;

        // A compiled getter object -> T over a field or property (boxing only when T is object).
        private static Func<object, T> Getter<T>(Type owner, string name)
        {
            var m = Member(owner, name);
            if (typeof(T) != typeof(object) && TypeOf(m) != typeof(T)) throw new MissingMemberException(owner.FullName, name + " : " + typeof(T).Name);
            var p = Expression.Parameter(typeof(object), "o");
            Expression body = m is FieldInfo f ? Expression.Field(Expression.Convert(p, owner), f) : Expression.Property(Expression.Convert(p, owner), (PropertyInfo)m);
            if (body.Type != typeof(T)) body = Expression.Convert(body, typeof(T));
            return Expression.Lambda<Func<object, T>>(body, p).Compile();
        }

        private static void BindCommon(Func<string, Type> find)
        {
            envType = find("SeaPower.Environment");
            var single = find("SeaPower.Singleton`1").MakeGenericType(envType);
            envInstance = single.GetField("_instance", BindingFlags.Static | BindingFlags.NonPublic | BindingFlags.Public);
            if (envInstance == null) throw new MissingFieldException("Singleton<Environment>._instance");
            envDate = Api.Method(envType, "get_DateTime", typeof(DateTime));
            try { envSeaState = Api.Method(envType, "get_SeaState", typeof(int)); } catch { envSeaState = null; }
            geoType = find("SeaPower.GeoPosition");
            geoLat = geoType.GetField("_latitude", Api.All); geoLon = geoType.GetField("_longitude", Api.All); geoHeight = geoType.GetField("_height", Api.All);
            if (geoLat == null || geoLon == null || geoLat.FieldType != typeof(double) || geoLon.FieldType != typeof(double)) throw new MissingFieldException("GeoPosition._latitude / _longitude : double");
            try { missionTime = Api.Method(find("SeaPower.GameTime"), "get_missionElapsedTime", typeof(double)); } catch { missionTime = null; }
        }

        private static void BindUnits(Func<string, Type> find)
        {
            var comp = find("SeaPower.Compartments");
            var ob = find("SeaPower.ObjectBase");
            var sub = find("SeaPower.Submarine");
            baseObject = Getter<object>(comp, "_baseObject");
            submarineOf = Getter<object>(comp, "_submarine");
            sinking = Getter<bool>(comp, "_isSinking");
            immobile = Getter<bool>(comp, "_immobile");
            telegraph = Getter<float[]>(comp, "_telegraphVelocities");
            telegraphSubmerged = Getter<float[]>(comp, "_telegraphVelocitiesSubmerged");
            var wanted = comp.GetProperty("WantedVelocityInKnots", Api.All);
            var set = wanted?.GetSetMethod(true);
            if (wanted == null || wanted.PropertyType != typeof(float) || set == null) throw new MissingMemberException("Compartments.WantedVelocityInKnots { get; set; } : float");
            wantedGet = Getter<float>(comp, "WantedVelocityInKnots");
            var p = Expression.Parameter(typeof(object), "o");
            var v = Expression.Parameter(typeof(float), "v");
            wantedSet = Expression.Lambda<Action<object, float>>(Expression.Call(Expression.Convert(p, comp), set, v), p, v).Compile();
            geoOf = Getter<object>(ob, "_geoPosition");
            if (TypeOf(Member(ob, "_geoPosition")) != geoType) throw new MissingMemberException("ObjectBase._geoPosition : GeoPosition");
            try { isPlayer = Getter<bool>(ob, "IsPlayerObject"); } catch { isPlayer = null; }
            yawToHeading = Api.Method(find("SeaPower.Utils"), "UnityYawToTrueHeading", typeof(float), typeof(float), geoType);
            isSubmerged = Api.Method(sub, "isSubmerged", typeof(bool));
            if (!typeof(Component).IsAssignableFrom(ob)) throw new MissingMemberException("ObjectBase is not a UnityEngine.Component");
        }

        private static void BindVisuals(Func<string, Type> find)
        {
            var utils = find("SeaPower.Utils");
            toLocal = Api.Method(utils, "longLatToLocalV3", typeof(Vector3), geoType, typeof(Vector2));
            toGeo = Api.Method(utils, "worldPositionFromUnityToLongLat", geoType, typeof(Vector3), typeof(Vector2));
            centerTile = find("SeaPower.Globals").GetField("_currentCenterTile", Api.All);
            if (centerTile == null || centerTile.FieldType != typeof(Vector2) || !centerTile.IsStatic) throw new MissingFieldException("Globals._currentCenterTile : Vector2");
        }

        // ---- small helpers ----------------------------------------------------------------------

        private static string F(double v) => v.ToString("0.##", CultureInfo.InvariantCulture);

        internal static object Env()
        {
            var e = envInstance?.GetValue(null);
            if (e is UnityEngine.Object u && u == null) return null; // destroyed Unity object
            return e;
        }

        internal static DateTime Date(object env)
        {
            try { return (DateTime)envDate.Invoke(env, null); }
            catch { return new DateTime(2029, 1, 1); }
        }

        internal static int SeaState(object env)
        {
            try { return envSeaState != null ? (int)envSeaState.Invoke(env, null) : -1; } catch { return -1; }
        }

        internal static double Now() => missionTime != null ? (double)missionTime.Invoke(null, null) : Time.time;

        private static object Geo(double lat, double lon)
        {
            object g = Activator.CreateInstance(geoType);
            geoLat.SetValue(g, lat);
            geoLon.SetValue(g, lon);
            if (geoHeight != null) geoHeight.SetValue(g, Convert.ChangeType(0, geoHeight.FieldType, CultureInfo.InvariantCulture));
            return g;
        }

        private static Vector3 Local(double lat, double lon, Vector2 tile) => (Vector3)toLocal.Invoke(null, new[] { Geo(lat, lon), (object)tile });

        internal static float MetersToUnity(double m) => (float)(m / 0.3048 / 220.472656); // the game's 220.472656 ft per Unity unit (SubIceRule)

        // ---- (a) the no-go rule -------------------------------------------------------------------

        private sealed class Hull
        {
            internal readonly ShelfSpeedState Speed = new ShelfSpeedState();
            internal double NextSample = double.NegativeInfinity, NextFar = double.NegativeInfinity;
            internal double Here = double.NaN, Ahead = double.NaN;
            internal int LastSign;
            internal bool Sub, Submerged, WasCapped;
        }
        private static readonly ConditionalWeakTable<object, Hull> hulls = new ConditionalWeakTable<object, Hull>();
        private const double FarNm = 20;      // clearance beyond this: no front nearby
        private const double MaxClosingKn = 60; // fastest closing speed assumed for the far-skip (design value)

        // Compartments.UpdateWantedVelocityInKnots postfix (main thread, every unit, every step).
        internal static void SpeedPostfix(object __instance)
        {
            if (!NoGoOn) return;
            try
            {
                PostfixCalls++;
                var ob = baseObject(__instance);
                if (ob == null || sinking(__instance) || immobile(__instance)) return;
                float wanted = wantedGet(__instance);
                if (Math.Abs(wanted) < 0.01f) return;
                var hull = hulls.GetOrCreateValue(__instance);
                double now = Now();
                if (now < hull.NextFar && now > hull.NextFar - 3600 * 24) return; // far from any front (checked below)
                object g = geoOf(ob);
                double lat = (double)geoLat.GetValue(g), lon = (double)geoLon.GetValue(g);
                int sign = wanted < 0 ? -1 : 1;
                if (now >= hull.NextSample || now < hull.NextSample - 2 || sign != hull.LastSign)
                {
                    hull.NextSample = now + 1.0;
                    hull.LastSign = sign;
                    var subObj = submarineOf(__instance);
                    hull.Sub = subObj != null;
                    hull.Submerged = hull.Sub && (bool)isSubmerged.Invoke(subObj, null);
                    hull.Here = IceShelves.Clearance(lat, lon, FarNm);
                    if (hull.Here >= FarNm)
                    {
                        // nothing within 20 nm: look again when a 60 kn hull could have closed half of it
                        hull.NextFar = now + (FarNm / 2) / MaxClosingKn * 3600;
                        if (hull.WasCapped) hull.WasCapped = false;
                        return;
                    }
                    float yaw = ((Component)ob).transform.eulerAngles.y;
                    float heading = (float)yawToHeading.Invoke(null, new object[] { yaw, g });
                    if (sign < 0) heading += 180f;
                    double ahead = double.PositiveInfinity;
                    foreach (var nm in ShelfSpeedState.AheadNm)
                    {
                        IceFeatureGeo.Destination(lat, lon, heading, nm, out double la, out double lo);
                        ahead = Math.Min(ahead, IceShelves.Clearance(la, lo, FarNm));
                    }
                    hull.Ahead = ahead;
                }
                if (double.IsNaN(hull.Here)) return;
                double limit = hull.Sub ? StandoffNm : 0.0;
                var arr = hull.Submerged ? telegraphSubmerged(__instance) : telegraph(__instance);
                float flank = 0;
                if (arr != null) for (int i = 0; i < arr.Length; i++) flank = Math.Max(flank, Math.Abs(arr[i]));
                float capped = hull.Speed.Cap(wanted, flank, hull.Here, hull.Ahead, limit);
                if (capped != wanted)
                {
                    wantedSet(__instance, capped);
                    Holds++;
                    if (hull.Speed.Stopped) Stops++;
                }
                bool binding = capped != wanted;
                if (Diagnostics && binding != hull.WasCapped)
                    Api.Log("ice features: " + ((UnityEngine.Object)ob).name + (hull.Sub ? " (submarine" + (hull.Submerged ? ", submerged)" : ")") : "") + " at " + F(lat) + ", " + F(lon) + (binding ?
                        ": held at the ice-shelf " + (hull.Sub ? "stand-off (" + F(limit) + " nm, estimate)" : "front") + ", clearance " + F(hull.Here) + " nm, " + F(hull.Ahead) + " nm ahead; " + wanted.ToString("0.0", CultureInfo.InvariantCulture) + " -> " + capped.ToString("0.0", CultureInfo.InvariantCulture) + " kn" + (isPlayer != null && isPlayer(ob) ? " (player unit)" : "") :
                        ": released"));
                hull.WasCapped = binding;
            }
            catch (Exception e) { NoGoOn = false; Api.LogFailure("ice features: no-go rule failed and is off for this session; native speed kept", e); }
        }

        // ---- (b) visuals ------------------------------------------------------------------------

        private static Material shelfMaterial, bergMaterial;
        private static string shaderName = "";
        private static object lastEnv;
        private static bool failed;
        private static float nextLayout, nextReport;
        private static Vector2 lastTile = new Vector2(float.NaN, float.NaN);
        private static double battleStart = double.NaN, lastNow = double.NaN;
        private static double genLat = double.NaN, genLon = double.NaN;
        private static DateTime battleDate;
        private sealed class Piece { internal GameObject Go; internal Mesh Mesh; internal double Lat, Lon; internal int Tris; }
        private static readonly Dictionary<long, Piece> pieces = new Dictionary<long, Piece>();
        private sealed class Drawn { internal Berg Berg; internal GameObject Go; internal Mesh Mesh; }
        private static readonly Dictionary<string, Berg> bergs = new Dictionary<string, Berg>();
        private static readonly Dictionary<string, Drawn> drawn = new Dictionary<string, Drawn>();
        internal static int PieceCount => pieces.Count;
        internal static int BergCount => bergs.Count;
        internal static int DrawnCount => drawn.Count;
        internal static IEnumerable<GameObject> PieceObjects() { foreach (var p in pieces.Values) yield return p.Go; }
        internal static IEnumerable<GameObject> BergObjects() { foreach (var d in drawn.Values) yield return d.Go; }
        internal static IEnumerable<Berg> Bergs() => bergs.Values;
        internal static IEnumerable<Berg> DrawnBergs() { foreach (var d in drawn.Values) yield return d.Berg; }

        internal static void Tick()
        {
            if (failed || !VisualsOn || Root == null) return;
            try
            {
                var env = Env();
                var cam = Camera.main;
                if (cam == null) foreach (var c in Camera.allCameras) if (c != null && c.enabled) { cam = c; break; }
                if (env == null || cam == null) { if (lastEnv != null || pieces.Count > 0 || drawn.Count > 0) Clear(); lastEnv = null; return; }
                if (!ReferenceEquals(env, lastEnv)) { Clear(); lastEnv = env; StartBattle(env); }
                if (shelfMaterial == null) { shelfMaterial = MakeMaterial(0.80, 0.82, 0.86, out shaderName); bergMaterial = MakeMaterial(0.74, 0.80, 0.86, out _); if (shelfMaterial == null) throw new InvalidOperationException("no usable shader"); }
                var tile = (Vector2)centerTile.GetValue(null);
                object camGeo = toGeo.Invoke(null, new object[] { cam.transform.position, tile });
                double camLat = (double)geoLat.GetValue(camGeo), camLon = (double)geoLon.GetValue(camGeo);
                double now = Now();
                double dt = double.IsNaN(lastNow) ? 0 : now - lastNow;
                if (dt < 0 || dt > 3600) dt = 0; // a clock jump (load, rewind): no drift this frame
                lastNow = now;
                float real = Time.realtimeSinceStartup;
                bool tileMoved = tile != lastTile;
                if (BergsOn) StepBergs(dt);
                if (tileMoved || real >= nextLayout || real < nextLayout - 10)
                {
                    nextLayout = real + 2f;
                    lastTile = tile;
                    if (ShelvesOn) LayoutShelves(camLat, camLon, tile);
                    if (BergsOn) LayoutBergs(camLat, camLon, tile, now);
                }
                if (Diagnostics && (real >= nextReport || real < nextReport - 60)) { nextReport = real + 30f; Report(env, camLat, camLon); }
            }
            catch (Exception e)
            {
                failed = true;
                Api.LogFailure("ice features: visuals failed and are off for this session", e);
                try { Clear(); } catch { }
            }
        }

        private static void StartBattle(object env)
        {
            battleDate = Date(env);
            battleStart = Now();
            lastNow = double.NaN;
            genLat = genLon = double.NaN;
            if (Diagnostics) Api.Log("ice features: battle date " + battleDate.ToString("yyyy-MM-dd HH:mm", CultureInfo.InvariantCulture) + "; shader " + shaderName + "; game clock " + (missionTime != null ? "GameTime.missionElapsedTime" : "Time.time"));
        }

        // The first shader of the list that loads, set up matt (as SeaIceSheet's IceLook does). The
        // colours are a visual choice (bright, faintly blue ice), not a measured albedo.
        internal static readonly string[] Shaders = { "Legacy Shaders/Diffuse", "Diffuse", "Standard", "Legacy Shaders/VertexLit", "Unlit/Color" };

        private static Material MakeMaterial(double r, double g, double b, out string used)
        {
            used = "";
            foreach (var name in Shaders)
            {
                Shader shader = null;
                try { shader = Shader.Find(name); } catch { }
                if (shader == null || !shader.isSupported) continue;
                var m = new Material(shader) { name = "SEST ice features" };
                m.color = new Color((float)r, (float)g, (float)b, 1f);
                if (m.HasProperty("_Glossiness")) m.SetFloat("_Glossiness", 0.1f);
                if (m.HasProperty("_Metallic")) m.SetFloat("_Metallic", 0f);
                if (m.HasProperty("_SpecularHighlights")) m.SetFloat("_SpecularHighlights", 0f);
                if (m.HasProperty("_GlossyReflections")) m.SetFloat("_GlossyReflections", 0f);
                used = name;
                return m;
            }
            return null;
        }

        private static GameObject NewObject(string name, Material mat, IceMeshData data, out Mesh mesh)
        {
            var go = new GameObject(name);
            go.transform.SetParent(Root.transform, false);
            mesh = new Mesh { name = name };
            var v = new Vector3[data.Vertices];
            for (int i = 0; i < v.Length; i++) v[i] = new Vector3(data.V[3 * i], data.V[3 * i + 1], data.V[3 * i + 2]);
            mesh.vertices = v;
            mesh.triangles = data.T.ToArray();
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var r = go.AddComponent<MeshRenderer>();
            r.sharedMaterial = mat;
            r.shadowCastingMode = ShadowCastingMode.Off;
            r.receiveShadows = true;
            r.reflectionProbeUsage = ReflectionProbeUsage.Off;
            return go;
        }

        // Anchor at (lat, lon), local east/north metres to Unity through two more conversions 1 km
        // away (as SeaIceSheet.Place); up through the game's 220.472656 ft per Unity unit.
        private static void Place(GameObject go, double lat, double lon, Vector2 tile)
        {
            var p = Local(lat, lon, tile);
            IceFeatureGeo.Displace(lat, lon, 1.0 / IceFeatureGeo.KmPerNm, 0, out double latE, out double lonE);
            IceFeatureGeo.Displace(lat, lon, 0, 1.0 / IceFeatureGeo.KmPerNm, out double latN, out double lonN);
            Vector3 east = (Local(latE, lonE, tile) - p) / 1000f, north = (Local(latN, lonN, tile) - p) / 1000f;
            float yaw = Mathf.Atan2(east.z, east.x) * Mathf.Rad2Deg;
            var t = go.transform;
            t.position = new Vector3(p.x, 0f, p.z);
            t.rotation = Quaternion.Euler(0, -yaw, 0);
            t.localScale = new Vector3(east.magnitude, MetersToUnity(1.0), north.magnitude);
        }

        // Local metres of (lat, lon) around an anchor (equirectangular about the anchor; pieces and
        // bergs are at most a few km across).
        private static void LocalMeters(double lat0, double lon0, double lat, double lon, out double e, out double n)
        {
            n = (lat - lat0) * 111320.0;
            e = IceFeatureGeo.LonDelta(lon, lon0) * 111320.0 * Math.Cos(IceFeatureGeo.Radians(lat0));
        }

        private const int MaxPieceSegments = 24;

        private static void LayoutShelves(double camLat, double camLon, Vector2 tile)
        {
            var segs = IceShelves.SegmentsNear(camLat, camLon, ShelfViewKm);
            segs.Sort();
            var want = new HashSet<long>();
            int i = 0;
            while (i < segs.Count)
            {
                int start = segs[i], count = 1;
                IceShelves.Segment(start, out _, out _, out _, out _, out int feature0);
                while (i + count < segs.Count && segs[i + count] == start + count && count < MaxPieceSegments)
                {
                    IceShelves.Segment(start + count, out double la, out double lo, out _, out _, out int f);
                    IceShelves.Segment(start + count - 1, out _, out _, out double pla, out double plo, out int pf);
                    if (f != feature0 || la != pla || lo != plo) break; // another line
                    count++;
                }
                long key = ((long)start << 16) | (uint)count;
                want.Add(key);
                if (!pieces.ContainsKey(key)) pieces[key] = BuildPiece(start, count, feature0);
                i += count;
            }
            var drop = new List<long>();
            foreach (var kv in pieces) if (!want.Contains(kv.Key)) drop.Add(kv.Key);
            foreach (var k in drop) { Destroy(pieces[k].Go, pieces[k].Mesh); pieces.Remove(k); }
            foreach (var p in pieces.Values) Place(p.Go, p.Lat, p.Lon, tile);
        }

        private static Piece BuildPiece(int start, int count, int feature)
        {
            var e = new double[count + 1];
            var n = new double[count + 1];
            IceShelves.Segment(start, out double lat0, out double lon0, out _, out _, out _);
            for (int k = 0; k <= count; k++)
            {
                double la, lo;
                if (k < count) IceShelves.Segment(start + k, out la, out lo, out _, out _, out _);
                else IceShelves.Segment(start + count - 1, out _, out _, out la, out lo, out _);
                LocalMeters(lat0, lon0, la, lo, out e[k], out n[k]);
            }
            IceShelves.Cliff(feature, out double fb, out double dr);
            int side = IceShelves.SideOf(start);
            var data = CliffMesher.Build(e, n, side == 0 ? 1 : side, fb, dr, CliffMesher.DefaultTopWidthM);
            var go = NewObject("SEST ice-shelf front", shelfMaterial, data, out Mesh mesh);
            return new Piece { Go = go, Mesh = mesh, Lat = lat0, Lon = lon0, Tris = data.Triangles };
        }

        private static void StepBergs(double dt)
        {
            if (!(dt > 0) || bergs.Count == 0) return;
            foreach (var b in bergs.Values)
            {
                IcebergField.Drift(b, dt);
                // wave erosion off (sea state 0): the game's sea state is a WMO code, not the
                // wind-derived sea state of the Martin and Adcroft formula
                if (!double.IsNaN(SstC)) IcebergField.Melt(b, dt, SstC, 0.0, 0.0);
            }
        }

        private static void LayoutBergs(double camLat, double camLon, Vector2 tile, double now)
        {
            // generate around the camera when it moved half the radius from the last generation centre
            if (double.IsNaN(genLat) || IceFeatureGeo.GreatCircleNm(genLat, genLon, camLat, camLon) > BergRadiusNm / 2)
            {
                genLat = camLat; genLon = camLon;
                double dLat = BergRadiusNm / 60.0, dLon = Math.Min(179.0, BergRadiusNm / 60.0 / Math.Max(0.05, Math.Cos(IceFeatureGeo.Radians(camLat))));
                List<Berg> made;
                try { made = IcebergField.Generate(Math.Max(-89.9, camLat - dLat), Math.Min(89.9, camLat + dLat), IceFeatureGeo.WrapLon(camLon - dLon), IceFeatureGeo.WrapLon(camLon + dLon), battleDate, Seed, sstC: SstC, maxBergs: 5000); }
                catch (InvalidOperationException e) { made = new List<Berg>(); if (Diagnostics) Api.Log("ice features: " + e.Message + "; no new bergs here"); }
                double age = double.IsNaN(battleStart) ? 0 : Math.Max(0, now - battleStart);
                foreach (var b in made)
                {
                    if (bergs.ContainsKey(b.Id)) continue;
                    if (age > 0) { IcebergField.Drift(b, age); if (!double.IsNaN(SstC)) IcebergField.Melt(b, age, SstC, 0.0, 0.0); }
                    bergs[b.Id] = b;
                }
                // forget bergs far outside the radius (they come back the same if the camera returns)
                var far = new List<string>();
                foreach (var b in bergs.Values) if (IceFeatureGeo.GreatCircleNm(camLat, camLon, b.Lat, b.Lon) > BergRadiusNm * 2) far.Add(b.Id);
                foreach (var id in far) bergs.Remove(id);
            }
            // draw the nearest bergs within the view and within their class's day visual range
            var cand = new List<KeyValuePair<double, Berg>>();
            foreach (var b in bergs.Values)
            {
                if (b.Gone) continue;
                double km = IceFeatureGeo.GreatCircleNm(camLat, camLon, b.Lat, b.Lon) * IceFeatureGeo.KmPerNm;
                double seeKm = IcebergField.VisualDetectionNm((int)b.Category, BergViewKm, 15.0, b.HeightM) * IceFeatureGeo.KmPerNm;
                if (km <= Math.Min(BergViewKm, Math.Max(seeKm, 1.0))) cand.Add(new KeyValuePair<double, Berg>(km, b));
            }
            cand.Sort((a, b) => a.Key.CompareTo(b.Key));
            var keep = new HashSet<string>();
            for (int i = 0; i < cand.Count && i < MaxDrawn; i++) keep.Add(cand[i].Value.Id);
            var drop = new List<string>();
            foreach (var kv in drawn) if (!keep.Contains(kv.Key)) drop.Add(kv.Key);
            foreach (var id in drop) { Destroy(drawn[id].Go, drawn[id].Mesh); drawn.Remove(id); }
            foreach (var id in keep)
            {
                if (!drawn.TryGetValue(id, out var d))
                {
                    var b = bergs[id];
                    var go = NewObject("SEST iceberg " + b.CategoryName, bergMaterial, BergMesher.Build(b), out Mesh mesh);
                    d = new Drawn { Berg = b, Go = go, Mesh = mesh };
                    drawn[id] = d;
                }
                Place(d.Go, d.Berg.Lat, d.Berg.Lon, tile);
            }
        }

        private static void Report(object env, double camLat, double camLon)
        {
            int ss = SeaState(env);
            var line = "ice features at camera " + F(camLat) + ", " + F(camLon) + ": " + pieces.Count + " cliff pieces, " + bergs.Count + " bergs (" + drawn.Count + " drawn), holds " + Holds + " (" + Stops + " stops)";
            Berg near = null; double best = double.PositiveInfinity;
            foreach (var b in bergs.Values) { double d = IceFeatureGeo.GreatCircleNm(camLat, camLon, b.Lat, b.Lon); if (!b.Gone && d < best) { best = d; near = b; } }
            if (near != null)
            {
                int c = (int)near.Category;
                line += "; nearest berg " + near.CategoryName + " " + F(near.LengthM) + " m long, " + F(near.HeightM) + " m high, draft " + F(near.DraftM) + " m at " + F(best) + " nm" +
                    (ss >= 0 ? ", radar factor " + F(IcebergField.RadarFactor(c, ss)) + " at sea state " + ss + " (estimate), radar range about " + F(IcebergField.RadarDetectionNm(c, ss, 20.0, near.HeightM)) + " nm" : "") +
                    ", sonar false-contact index " + F(IcebergField.SonarFalseContactIndex(c)) + " (design index, not a probability)";
            }
            Api.Log(line);
        }

        private static void Destroy(GameObject go, Mesh mesh)
        {
            if (mesh != null) UnityEngine.Object.Destroy(mesh);
            if (go != null) UnityEngine.Object.Destroy(go);
        }

        internal static void Clear()
        {
            foreach (var p in pieces.Values) Destroy(p.Go, p.Mesh);
            pieces.Clear();
            foreach (var d in drawn.Values) Destroy(d.Go, d.Mesh);
            drawn.Clear();
            bergs.Clear();
            genLat = genLon = double.NaN;
            battleStart = lastNow = double.NaN;
            lastTile = new Vector2(float.NaN, float.NaN);
        }

        // tests: forget everything between installs
        internal static void ResetForTests()
        {
            Clear();
            failed = false; lastEnv = null; shelfMaterial = bergMaterial = null;
            nextLayout = nextReport = 0;
            Holds = Stops = PostfixCalls = 0;
            NoGoOn = VisualsOn = ShelvesOn = BergsOn = false;
            Root = null;
        }
    }
}
