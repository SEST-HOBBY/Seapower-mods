using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reflection;
using SeaPower;
using UnityEngine;
using UnityEngine.Rendering;
using Environment = SeaPower.Environment;

namespace Sest.RuntimeFixes;

// The ice's ship effects in a battle, driven by SeaIceSheet's Update (main
// thread). The rules are pure (SeaIceWake.cs); this file is the Unity side.
// - Bow pieces (SeaIceBreakup=1): broken floe pieces from IcePieceSim, one
//   shared procedural prism mesh (IcePieceMesh) on the sheet's own material,
//   pooled objects (SeaIcePieceCap, default 120), placed every frame from
//   battle-frame metres through the game's geo -> Unity conversion, riding
//   Ceto's waves, sinking and shrinking at the end of their life. Only the
//   three nearest breakers within 3 km of the camera spawn pieces, at full
//   rate within 1 km and fewer out to 3 km (IceBreakRule.PieceWeight), and a
//   distant ship's piece never takes the slot of a nearer one's.
// - Sounds (SeaIceSound=1): for the three nearest ships breaking ice within
//   5 km of the camera, a looped 3D AudioSource at the bow (SeaIceSoundClip,
//   default the game's own hull wash "audio/ships/Ship-Flow" pitched down to a
//   grinding rush, volume and pitch by IceBreakRule). One-shot cracks only
//   when the owner names a clip (SeaIceCrackClip, default empty: no cracks;
//   the game has no ice sound, and its weapon sounds read as hits), rate
//   limited on real time and only at 1x or slower. Above 2x time compression
//   every breaking sound is muted. Clips are loaded through the game's
//   ResourceLoader.getAudioClipResource, the audio types by reflection
//   (UnityEngine.AudioModule is not a build reference), and each source is
//   routed to the ship's own audio mixer group when it has one, so the game's
//   volume settings apply. No sound file is shipped.
// - Refreeze: IceCarve.Advance once a second of game time (the mission clock).
// Any failure turns the part off with one log line; a part switched off (here
// or by the ship hook's failure) has its loops stopped and its pieces hidden on
// the next frame.
internal static class SeaIceEffects
{
    private static GameObject root;
    private static Mesh pieceMesh;
    private static IcePieceSim sim;
    private static GameObject[] pieceGos = new GameObject[0];
    private static readonly Dictionary<int, double> spawnAcc = new Dictionary<int, double>();
    private static float nextReport;
    private static bool piecesLive, soundLive;
    private static int cap = IcePieceSim.DefaultCap;
    private static string loopName = "audio/ships/Ship-Flow", crackName = "";
    private static double soundVolume = 1.0;

    internal static void Install(string[] lines, GameObject parent)
    {
        root = parent;
        if (int.TryParse(Policy.TextOption(lines, "SeaIcePieceCap", ""), NumberStyles.Integer, CultureInfo.InvariantCulture, out int c) && c >= IcePieceSim.MinCap && c <= IcePieceSim.MaxCap) cap = c;
        loopName = Policy.TextOption(lines, "SeaIceSoundClip", loopName).Trim();
        crackName = Policy.TextOption(lines, "SeaIceCrackClip", crackName).Trim();
        if (double.TryParse(Policy.TextOption(lines, "SeaIceSoundVolume", ""), NumberStyles.Float, CultureInfo.InvariantCulture, out double v) && v >= 0 && v <= 2) soundVolume = v;
        sim = new IcePieceSim(cap, 0x1CEB4EAu);
        if (SeaIceBattle.SoundOn) Sound.Bind();
        Api.Log("sea ice effects: bow pieces " + (SeaIceBattle.BreakupOn ? "on, cap " + sim.Cap : "off") + "; breaking sounds " + (SeaIceBattle.SoundOn ? Sound.State + "; loop clip '" + loopName + "', crack clip '" + (crackName.Length > 0 ? crackName : "(none)") + "'" : "off") + "; channels " + (SeaIceBattle.CarveOn ? "on" : "off"));
    }

    internal static void Tick(Environment env, IceFrame frame, double camE, double camN, Vector2 tile, Camera cam, Material material)
    {
        double now = SeaIceBattle.Now(), frameS = SeaIceBattle.FrameS();
        float dt = Time.deltaTime, real = Time.realtimeSinceStartup;
        if (SeaIceBattle.CarveOn)
        {
            try { SeaIceBattle.AdvanceCarve(now); SeaIceBattle.Carve.Publish(real); }
            catch (Exception e) { SeaIceBattle.CarveOn = false; Api.LogFailure("sea ice channels stopped for this session", e); }
        }
        SeaIceBattle.SweepNoise();
        // a part switched off (its own failure, or the ship hook's): stop what it left running, once
        if (!SeaIceBattle.BreakupOn && piecesLive) HidePieces();
        if (!SeaIceBattle.SoundOn && soundLive) { soundLive = false; try { Sound.StopAll(); } catch { } }
        if (!SeaIceBattle.BreakupOn && !SeaIceBattle.SoundOn) return;
        try
        {
            // the local basis at the camera: Unity position of a frame point, per metre east and north
            frame.ToGeo(camE, camN, out double lat, out double lon);
            frame.ToGeo(camE + 1, camN, out double latE, out double lonE);
            frame.ToGeo(camE, camN + 1, out double latN, out double lonN);
            var p0 = Utils.longLatToLocalV3(new GeoPosition { _latitude = lat, _longitude = lon, _height = 0 }, tile);
            var east = (Utils.longLatToLocalV3(new GeoPosition { _latitude = latE, _longitude = lonE, _height = 0 }, tile) - p0) / 1000f;
            var north = (Utils.longLatToLocalV3(new GeoPosition { _latitude = latN, _longitude = lonN, _height = 0 }, tile) - p0) / 1000f;
            float unitPerM = SubIceRule.MetersToUnity(1.0);
            var near = new List<(SeaIceBattle.Breaker b, double dist, double e, double n, double headingRad, Vector3 bow)>();
            foreach (var b in SeaIceBattle.Breakers.Values)
            {
                if (!SeaIceBattle.IsCurrent(b, now, frameS) || !(b.Intensity > 0)) continue;
                var t = b.Ob.transform;
                var bow = t.position + t.forward * (float)(b.LengthM * 0.45 * unitPerM);
                var g = Utils.worldPositionFromUnityToLongLat(bow, tile);
                frame.ToKm(g._latitude, g._longitude, out double e, out double n);
                double d = Math.Sqrt((e - camE) * (e - camE) + (n - camN) * (n - camN));
                if (d > 8) continue;
                double heading = Utils.UnityYawToTrueHeading(t.eulerAngles.y, g) * Math.PI / 180;
                near.Add((b, d, e, n, heading, bow));
            }
            near.Sort((x, y) => x.dist.CompareTo(y.dist));
            if (SeaIceBattle.BreakupOn) { piecesLive = true; Pieces(near, dt, p0, east, north, camE, camN, unitPerM, material); }
            if (SeaIceBattle.SoundOn) { soundLive = true; Sound.Tick(near.Where(x => x.dist <= 5).Select(x => (x.b, x.bow)).Take(3).ToList(), real, SeaIceBattle.Compression()); }
            Report();
        }
        catch (Exception e)
        {
            SeaIceBattle.BreakupOn = false; SeaIceBattle.SoundOn = false;
            Api.LogFailure("sea ice bow pieces and breaking sounds stopped for this session", e);
            Clear();
        }
    }

    private static void Pieces(List<(SeaIceBattle.Breaker b, double dist, double e, double n, double headingRad, Vector3 bow)> near, float dt, Vector3 p0, Vector3 east, Vector3 north, double camE, double camN, float unitPerM, Material material)
    {
        if (sim == null || sim.Cap == 0 || material == null) return; // no sheet material (floe fallback): no pieces rather than untextured ones
        // the nearest breakers only, weighted by distance (near the camera first; distant ones get few or none)
        int ships = 0;
        foreach (var x in near)
        {
            double w = IceBreakRule.PieceWeight(x.dist);
            if (!(w > 0) || ships >= IceBreakRule.PieceShips) break;
            ships++;
            int id = x.b.Ob.GetInstanceID();
            spawnAcc.TryGetValue(id, out double acc);
            sim.Spawn(x.e * 1000, x.n * 1000, x.headingRad, x.b.SpeedKn * 0.514444, x.b.BeamM / 2, x.b.Intensity, dt, ref acc, w);
            spawnAcc[id] = acc;
        }
        if (spawnAcc.Count > 256) spawnAcc.Clear();
        sim.Step(dt);
        if (pieceGos.Length != sim.Cap) pieceGos = new GameObject[sim.Cap];
        int frame = Time.frameCount;
        for (int i = 0; i < sim.Cap; i++)
        {
            ref var p = ref sim.Pieces[i];
            var go = pieceGos[i];
            if (!p.Alive) { if (go != null && go.activeSelf) go.SetActive(false); continue; }
            if (go == null) go = pieceGos[i] = MakePiece(material);
            if (!go.activeSelf) go.SetActive(true);
            var tr = go.transform;
            var pos = p0 + east * (float)(p.E - camE * 1000) + north * (float)(p.N - camN * 1000);
            float y = ((i + frame) & 1) == 0 || p.Age < 0.1f ? SeaIceSheet.WaveAt(pos.x, pos.z) - IcePieceSim.SinkAt(p.Age, p.Life) * unitPerM : tr.position.y;
            tr.position = new Vector3(pos.x, y, pos.z);
            tr.rotation = Quaternion.Euler(p.Pitch, p.Yaw, p.Roll);
            float s = p.Size * IcePieceSim.ScaleAt(p.Age, p.Life) * unitPerM;
            tr.localScale = new Vector3(s, s * 0.45f, s * 0.8f);
        }
    }

    private static GameObject MakePiece(Material material)
    {
        if (pieceMesh == null)
        {
            IcePieceMesh.Build(7, 0x51CEu, out float[] v, out float[] n, out int[] t);
            pieceMesh = new Mesh { name = "SEST sea ice piece" };
            var vv = new Vector3[v.Length / 3]; var nn = new Vector3[vv.Length];
            for (int i = 0; i < vv.Length; i++) { vv[i] = new Vector3(v[i * 3], v[i * 3 + 1], v[i * 3 + 2]); nn[i] = new Vector3(n[i * 3], n[i * 3 + 1], n[i * 3 + 2]); }
            pieceMesh.vertices = vv; pieceMesh.normals = nn; pieceMesh.triangles = t;
            var uv = new Vector2[vv.Length];
            for (int i = 0; i < vv.Length; i++) uv[i] = new Vector2(vv[i].x * 0.05f, vv[i].z * 0.05f);
            pieceMesh.uv = uv;
            pieceMesh.RecalculateBounds();
        }
        var go = new GameObject("SEST sea ice piece");
        go.transform.SetParent(root.transform, false);
        go.AddComponent<MeshFilter>().sharedMesh = pieceMesh;
        var r = go.AddComponent<MeshRenderer>();
        if (material != null) r.sharedMaterial = material;
        r.shadowCastingMode = ShadowCastingMode.Off;
        r.receiveShadows = true;
        r.reflectionProbeUsage = ReflectionProbeUsage.Off;
        return go;
    }

    private static void Report()
    {
        if (!SeaIceBattle.Diagnostics) return;
        float real = Time.realtimeSinceStartup;
        if (real < nextReport) return;
        nextReport = real + 10f;
        Api.Log("sea ice effects: bow pieces " + (SeaIceBattle.BreakupOn && sim != null ? sim.Alive + " alive of cap " + sim.Cap + " (" + sim.Spawned + " spawned, " + sim.Recycled + " recycled while full, " + sim.Refused + " not spawned for a nearer ship's, this battle)" : "off") +
            "; sounds " + (SeaIceBattle.SoundOn ? Sound.Describe() : "off"));
    }

    internal static void Clear()
    {
        HidePieces();
        soundLive = false;
        Sound.StopAll();
    }

    private static void HidePieces()
    {
        piecesLive = false;
        sim?.Clear();
        spawnAcc.Clear();
        foreach (var go in pieceGos) if (go != null) go.SetActive(false);
    }

    internal static void DestroyPooled()
    {
        Clear();
        foreach (var go in pieceGos) if (go != null) UnityEngine.Object.Destroy(go);
        pieceGos = new GameObject[0];
        if (pieceMesh != null) { UnityEngine.Object.Destroy(pieceMesh); pieceMesh = null; }
        Sound.DestroyAll();
    }

    // Breaking sounds, all by reflection over UnityEngine.AudioModule.
    private static class Sound
    {
        internal static string State = "not bound";
        private static Type sourceType, clipType, rolloffType;
        private static PropertyInfo pClip, pLoop, pSpatial, pVolume, pPitch, pMin, pMax, pRolloff, pDoppler, pPlayOnAwake, pMixer, pIsPlaying;
        private static MethodInfo mPlay, mStop, mOneShot, mGetClip;
        private static FieldInfo loaderInstance;
        private static object loopClip, crackClip;
        private static bool loaded;
        private static readonly IceSoundGate gate = new IceSoundGate();
        private sealed class Voice { internal GameObject Go; internal Component Loop, Crack; internal float Volume, NextCrack; internal int Ship; internal bool Mixed; } // NextCrack: real seconds
        private static readonly List<Voice> voices = new List<Voice>();
        private static int loopsStarted, mutedFrames;
        private static uint rng = 0xBEEFu;

        internal static void Bind()
        {
            try
            {
                var asms = AppDomain.CurrentDomain.GetAssemblies();
                sourceType = asms.Select(a => a.GetType("UnityEngine.AudioSource", false)).FirstOrDefault(t => t != null);
                clipType = asms.Select(a => a.GetType("UnityEngine.AudioClip", false)).FirstOrDefault(t => t != null);
                rolloffType = asms.Select(a => a.GetType("UnityEngine.AudioRolloffMode", false)).FirstOrDefault(t => t != null);
                if (sourceType == null || clipType == null || rolloffType == null) { Off("UnityEngine.AudioSource/AudioClip not loaded"); return; }
                PropertyInfo P(string n) => sourceType.GetProperty(n, BindingFlags.Instance | BindingFlags.Public) ?? throw new MissingMemberException("AudioSource." + n);
                pClip = P("clip"); pLoop = P("loop"); pSpatial = P("spatialBlend"); pVolume = P("volume"); pPitch = P("pitch"); pMin = P("minDistance"); pMax = P("maxDistance");
                pRolloff = P("rolloffMode"); pDoppler = P("dopplerLevel"); pPlayOnAwake = P("playOnAwake"); pMixer = P("outputAudioMixerGroup"); pIsPlaying = P("isPlaying");
                mPlay = sourceType.GetMethod("Play", Type.EmptyTypes) ?? throw new MissingMethodException("AudioSource.Play()");
                mStop = sourceType.GetMethod("Stop", Type.EmptyTypes) ?? throw new MissingMethodException("AudioSource.Stop()");
                mOneShot = sourceType.GetMethod("PlayOneShot", new[] { clipType, typeof(float) }) ?? throw new MissingMethodException("AudioSource.PlayOneShot(AudioClip, float)");
                mGetClip = typeof(ResourceLoader).GetMethod("getAudioClipResource", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic, null, new[] { typeof(string) }, null);
                if (mGetClip == null || mGetClip.ReturnType != clipType) throw new MissingMethodException("ResourceLoader.getAudioClipResource(string) : AudioClip");
                loaderInstance = typeof(Singleton<ResourceLoader>).GetField("_instance", BindingFlags.Static | BindingFlags.NonPublic);
                if (loaderInstance == null) throw new MissingFieldException("Singleton<ResourceLoader>._instance");
                State = "bound (AudioSource, ResourceLoader.getAudioClipResource)";
            }
            catch (Exception e) { Off("binding failed: " + e.Message); }
        }

        private static void Off(string why)
        {
            SeaIceBattle.SoundOn = false;
            State = "off: " + why;
            Api.Log("sea ice breaking sounds off: " + why);
        }

        private static object Load(string name)
        {
            if (string.IsNullOrEmpty(name)) return null;
            var loader = loaderInstance.GetValue(null);
            if (loader == null) return null;
            var clip = mGetClip.Invoke(loader, new object[] { name });
            return clip is UnityEngine.Object o && o == null ? null : clip;
        }

        private static float U() { rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5; return (rng & 0xFFFFFF) / 16777216f; }

        // real: Time.realtimeSinceStartup; compression: the game's time compression
        internal static void Tick(List<(SeaIceBattle.Breaker b, Vector3 bow)> ships, float real, double compression)
        {
            float now = real;
            double gain = IceBreakRule.SoundGain(compression);
            bool cracks = IceBreakRule.CracksAllowed(compression);
            if (gain <= 0) { mutedFrames++; ships = new List<(SeaIceBattle.Breaker b, Vector3 bow)>(); } // muted: every voice fades out and stops
            if (sourceType == null) return;
            if (!loaded)
            {
                if (ships.Count == 0) return;
                loaded = true;
                loopClip = Load(loopName);
                crackClip = Load(crackName);
                Api.Log("sea ice breaking sounds: loop clip '" + loopName + "' " + (loopClip != null ? "loaded" : "NOT FOUND (set SeaIceSoundClip=<audio resource>)") + ", crack clip " + (crackName.Length == 0 ? "none (SeaIceCrackClip empty, the default)" : "'" + crackName + "' " + (crackClip != null ? "loaded (cracks at 1x or slower only)" : "NOT FOUND (set SeaIceCrackClip=<audio resource>, or empty for none)")));
                if (loopClip == null && crackClip == null) { Off("no clip found"); return; }
            }
            // voices follow their ship; ships without a voice take a free one
            var want = new Dictionary<int, (SeaIceBattle.Breaker b, Vector3 bow)>();
            foreach (var s in ships) want[s.b.Ob.GetInstanceID()] = s;
            foreach (var v in voices)
            {
                if (v.Go == null) continue;
                bool has = v.Ship != 0 && want.ContainsKey(v.Ship);
                double target = has ? IceBreakRule.LoopVolume(want[v.Ship].b.Intensity) * soundVolume * gain : 0;
                v.Volume = Mathf.MoveTowards(v.Volume, (float)target, Time.unscaledDeltaTime * 0.8f);
                if (has)
                {
                    var sh = want[v.Ship];
                    v.Go.transform.position = sh.bow;
                    if (v.Loop != null) pPitch.SetValue(v.Loop, (float)IceBreakRule.LoopPitch(sh.b.Intensity), null);
                    if (crackClip != null && cracks && (now >= v.NextCrack || now < v.NextCrack - 60f))
                    {
                        v.NextCrack = now + (float)IceBreakRule.CrackInterval(sh.b.Intensity, U());
                        if (gate.TryPlay(now, IceBreakRule.CrackShortS * 0.35))
                        {
                            pPitch.SetValue(v.Crack, 1.35f + 0.4f * U(), null);
                            mOneShot.Invoke(v.Crack, new[] { crackClip, (object)(float)(0.25 * soundVolume * (0.5 + 0.5 * sh.b.Intensity)) });
                        }
                    }
                    want.Remove(v.Ship);
                }
                if (v.Loop != null) pVolume.SetValue(v.Loop, v.Volume, null);
                if (!has && v.Volume <= 0.001f && v.Ship != 0)
                {
                    if (v.Loop != null) mStop.Invoke(v.Loop, null);
                    v.Ship = 0;
                }
            }
            foreach (var kv in want)
            {
                var v = voices.FirstOrDefault(x => x.Go != null && x.Ship == 0);
                if (v == null) { if (voices.Count >= 3) break; v = NewVoice(); voices.Add(v); }
                v.Ship = kv.Key; v.Volume = 0; v.NextCrack = now + 0.5f + U();
                v.Go.transform.position = kv.Value.bow;
                Mix(v, kv.Value.b.Ob);
                if (v.Loop != null) { pVolume.SetValue(v.Loop, 0f, null); mPlay.Invoke(v.Loop, null); loopsStarted++; }
            }
        }

        private static Voice NewVoice()
        {
            var go = new GameObject("SEST sea ice breaking sound");
            go.transform.SetParent(root.transform, false);
            var v = new Voice { Go = go };
            if (loopClip != null) { v.Loop = Source(go); pClip.SetValue(v.Loop, loopClip, null); pLoop.SetValue(v.Loop, true, null); }
            v.Crack = Source(go);
            return v;
        }

        private static Component Source(GameObject go)
        {
            var src = go.AddComponent(sourceType);
            pPlayOnAwake.SetValue(src, false, null);
            pSpatial.SetValue(src, 1f, null);
            pDoppler.SetValue(src, 0f, null);
            pRolloff.SetValue(src, Enum.ToObject(rolloffType, 0), null); // Logarithmic
            pMin.SetValue(src, SubIceRule.MetersToUnity(60), null);
            pMax.SetValue(src, SubIceRule.MetersToUnity(5000), null);
            pVolume.SetValue(src, 0f, null);
            return src;
        }

        // The ship's own mixer group (its engine or flow source), so the game's sound volume applies.
        private static void Mix(Voice v, ObjectBase ob)
        {
            try
            {
                var own = ob != null ? ob.GetComponentInChildren(sourceType, true) : null;
                var group = own != null ? pMixer.GetValue(own, null) : null;
                if (group == null) return;
                if (v.Loop != null) pMixer.SetValue(v.Loop, group, null);
                pMixer.SetValue(v.Crack, group, null);
                v.Mixed = true;
            }
            catch { }
        }

        internal static string Describe()
        {
            int playing = 0, mixed = 0;
            foreach (var v in voices) { if (v.Ship != 0) playing++; if (v.Mixed) mixed++; }
            return State + "; " + playing + " loops playing (" + loopsStarted + " started, " + mixed + " on the ship's mixer group), cracks " + gate.Plays + " played, " + gate.Refused + " held back by the rate limit, " + mutedFrames + " frames muted by time compression above " + IceBreakRule.MaxSoundCompression.ToString("0", CultureInfo.InvariantCulture) + "x, this battle; loop clip " + (loopClip != null ? "'" + loopName + "'" : loaded ? "missing" : "not loaded yet") + ", crack clip " + (crackClip != null ? "'" + crackName + "'" : loaded ? "none" : "not loaded yet");
        }

        internal static void StopAll()
        {
            foreach (var v in voices)
            {
                try { if (v.Loop != null && v.Go != null) mStop.Invoke(v.Loop, null); } catch { }
                v.Ship = 0; v.Volume = 0;
            }
        }

        internal static void DestroyAll()
        {
            foreach (var v in voices) if (v.Go != null) UnityEngine.Object.Destroy(v.Go);
            voices.Clear();
            loaded = false; loopClip = crackClip = null;
            gate.Plays = gate.Refused = 0; loopsStarted = 0; mutedFrames = 0;
        }
    }
}

// Ceto's clip overlays, by reflection (Assets.dll is not a build reference): a
// WaveOverlay(position, rotation, halfSize, duration) with an OverlayClipTexture,
// registered with Ocean.Instance.OverlayManager.Add, moved by Position,
// Rotation, HalfSize and UpdateOverlay, removed by Kill (OverlayManager.Update
// drops killed overlays). The same calls the game makes for its shockwave
// rings (ShockwaveWaterRing). Ceto renders clip overlays into its clip map
// (Ocean.clipOverlaySize) and the ocean is not drawn where the map is white.
// Every overlay is made with OverlayClipTexture.ignoreQuerys = true (bound like
// tex; missing, no overlay is made): Ceto's wave queries then skip it
// (OverlayManager.GetQueryableContaining), so the game's per-compartment
// QueryWaves calls do not loop over the ice overlays, and the camera under
// the pack is never reported as clipped, which would switch Ceto's
// UnderWaterPostEffect off there (disableOnClip). Drawing is unchanged: the
// clip map takes every drawable overlay.
internal static class CetoClip
{
    internal static string State = "not bound";
    private static ConstructorInfo ctor;
    private static Type clipType;
    private static FieldInfo clipTex, clipAlpha, clipIgnore;
    private static PropertyInfo pClip, pPosition, pHalf, pRotation, pKill, pManager, pHasClip;
    private static MethodInfo mUpdate, mAdd;
    private static FieldInfo fClipSize;
    private static bool failed;
    internal static int Created, Killed;

    internal static bool Ready => ctor != null && !failed && SeaIceSheet.OceanNow() != null;

    internal static void Bind()
    {
        try
        {
            var asms = AppDomain.CurrentDomain.GetAssemblies();
            Type T(string n) => asms.Select(a => a.GetType(n, false)).FirstOrDefault(t => t != null) ?? throw new TypeLoadException(n + " not loaded");
            var overlay = T("Ceto.WaveOverlay");
            var ocean = T("Ceto.Ocean");
            var manager = T("Ceto.OverlayManager");
            clipType = T("Ceto.OverlayClipTexture");
            ctor = overlay.GetConstructor(new[] { typeof(Vector3), typeof(float), typeof(Vector2), typeof(float) }) ?? throw new MissingMethodException("WaveOverlay(Vector3, float, Vector2, float)");
            const BindingFlags I = BindingFlags.Instance | BindingFlags.Public;
            PropertyInfo P(Type t, string n) => t.GetProperty(n, I) ?? throw new MissingMemberException(t.Name + "." + n);
            pClip = P(overlay, "ClipTex"); pPosition = P(overlay, "Position"); pHalf = P(overlay, "HalfSize"); pRotation = P(overlay, "Rotation"); pKill = P(overlay, "Kill");
            mUpdate = overlay.GetMethod("UpdateOverlay", I, null, Type.EmptyTypes, null) ?? throw new MissingMethodException("WaveOverlay.UpdateOverlay()");
            pManager = P(ocean, "OverlayManager");
            mAdd = manager.GetMethod("Add", I, null, new[] { overlay }, null) ?? throw new MissingMethodException("OverlayManager.Add(WaveOverlay)");
            pHasClip = manager.GetProperty("HasClipOverlay", I);
            fClipSize = ocean.GetField("clipOverlaySize", I);
            clipTex = clipType.GetField("tex", I) ?? throw new MissingFieldException("OverlayClipTexture.tex");
            clipAlpha = clipType.GetField("alpha", I);
            clipIgnore = clipType.GetField("ignoreQuerys", I);
            if (clipIgnore == null || clipIgnore.FieldType != typeof(bool)) throw new MissingFieldException("OverlayClipTexture.ignoreQuerys : bool (wave queries and the underwater effect would see the ice)");
            State = "bound (WaveOverlay + OverlayClipTexture via OverlayManager.Add, ignoreQuerys)";
        }
        catch (Exception e) { ctor = null; State = "unavailable (" + e.Message + "); thickness and placement only"; Api.Log("sea ice ocean clip: " + State); }
    }

    internal static object Create(Vector3 pos, float rotation, Vector2 halfSize, Texture tex)
    {
        if (!Ready) return null;
        try
        {
            var o = ctor.Invoke(new object[] { pos, rotation, halfSize, 1e7f });
            var c = Activator.CreateInstance(clipType);
            clipIgnore.SetValue(c, true); // before ClipTex is assigned: wave queries never see this overlay
            clipTex.SetValue(c, tex);
            clipAlpha?.SetValue(c, 1f);
            pClip.SetValue(o, c, null);
            mUpdate.Invoke(o, null);
            var manager = pManager.GetValue(SeaIceSheet.OceanNow(), null);
            if (manager == null) return null;
            mAdd.Invoke(manager, new[] { o });
            Created++;
            return o;
        }
        catch (Exception e) { Fail(e); return null; }
    }

    internal static void Move(object o, Vector3 pos, float rotation, Vector2 halfSize)
    {
        if (o == null || failed) return;
        try { pPosition.SetValue(o, pos, null); pRotation.SetValue(o, rotation, null); pHalf.SetValue(o, halfSize, null); mUpdate.Invoke(o, null); }
        catch (Exception e) { Fail(e); }
    }

    internal static void Kill(object o)
    {
        if (o == null || ctor == null) return;
        try { pKill.SetValue(o, true, null); Killed++; } catch { }
    }

    private static void Fail(Exception e)
    {
        if (failed) return;
        failed = true;
        State = "stopped (" + e.GetType().Name + ")";
        Api.LogFailure("sea ice ocean clip overlays stopped for this session; the closed slabs remain", e);
    }

    internal static string Describe()
    {
        string extra = "";
        try
        {
            var ocean = SeaIceSheet.OceanNow();
            if (ocean != null && pManager != null)
            {
                var m = pManager.GetValue(ocean, null);
                extra = ", Ceto OverlayManager.HasClipOverlay " + (m != null && pHasClip != null ? pHasClip.GetValue(m, null) : "?") + ", Ocean.clipOverlaySize " + (fClipSize != null ? fClipSize.GetValue(ocean) : "?");
            }
        }
        catch { }
        return State + "; " + Created + " created, " + Killed + " killed" + extra;
    }
}
