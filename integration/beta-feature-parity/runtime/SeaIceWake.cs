using System;
using System.Collections.Generic;

namespace Sest.RuntimeFixes;

// The pure rules behind the battle ice's ship effects (no Unity or game types,
// so SeaIceTests.exe runs all of it under Mono): the sheet's material values
// (IceLook), the channels ships carve and their refreezing (IceCarve and the
// immutable IceCarveSnapshot the mesher threads read), the broken floe pieces
// at the bow (IcePieceSim) and the breaking intensity that drives pieces,
// sound and the hull's added noise (IceBreakRule).

// The sheet's material: a matt, lit surface like the game's snow-covered land
// or a ship's deck, never a mirror. Albedo 0.80 (SeaIceAlbedo, 0.5-0.95),
// smoothness 0.12 (SeaIceSmoothness, 0-0.4), metallic 0; a faint blue tint, so
// the shaded side reads cold. The noise texture modulates the colour by
// TextureLow..TextureLow+TextureSpan (mean TextureMean); the colour is divided
// by that mean, so the drawn mean albedo is the configured one.
internal static class IceLook
{
    internal const double DefaultAlbedo = 0.80, MinAlbedo = 0.5, MaxAlbedo = 0.95;
    internal const double DefaultSmoothness = 0.12, MaxSmoothness = 0.4;
    internal const double TextureLow = 0.88, TextureSpan = 0.12;
    internal static readonly double[] Tint = { 0.955, 0.985, 1.0 };
    // Lambert first (the game itself loads "Diffuse" by name: no Fresnel, no
    // environment reflection, takes fog, sun and ambient); Standard only with
    // specular highlights and glossy reflections switched off; unlit last.
    internal static readonly string[] Shaders = { "Legacy Shaders/Diffuse", "Diffuse", "Standard", "Legacy Shaders/VertexLit", "Unlit/Texture", "Hidden/Internal-Colored" };
    internal static readonly string[] StandardMattKeywords = { "_SPECULARHIGHLIGHTS_OFF", "_GLOSSYREFLECTIONS_OFF" };

    internal static double Albedo(string text) => Parse(text, DefaultAlbedo, MinAlbedo, MaxAlbedo);
    internal static double Smoothness(string text) => Parse(text, DefaultSmoothness, 0, MaxSmoothness);

    private static double Parse(string text, double fallback, double min, double max)
    {
        return double.TryParse(text ?? "", System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out double v) && v >= min && v <= max ? v : fallback;
    }

    internal static double TextureMean => TextureLow + TextureSpan * 0.5;

    // Texture byte for a noise value 0..1.
    internal static byte TextureByte(double noise01) => (byte)Math.Round(255 * (TextureLow + TextureSpan * Math.Max(0, Math.Min(1, noise01))));

    // Material colour (linear 0..1) for an albedo: tinted and divided by the texture mean.
    internal static void Colour(double albedo, out double r, out double g, out double b)
    {
        double k = albedo / TextureMean;
        r = Math.Min(1, k * Tint[0]); g = Math.Min(1, k * Tint[1]); b = Math.Min(1, k * Tint[2]);
    }

    // Unlit shaders cannot follow the sun: drawn at the scene's ambient share instead of full albedo.
    internal static bool IsUnlit(string shader) => shader != null && (shader.StartsWith("Unlit/", StringComparison.Ordinal) || shader == "Hidden/Internal-Colored");
    internal const double UnlitScale = 0.6;

    // The chosen values are matt: low smoothness, no metal.
    internal static bool Matt(double smoothness, double metallic) => smoothness <= 0.25 && metallic == 0;
}

// One carved track segment, in the battle frame (km), with its open half width.
internal struct IceCarveSegment
{
    internal double E0, N0, E1, N1;   // km
    internal double T;                // game seconds when the ship passed the segment's end
    internal double HalfM;            // open half width when fresh, metres
    internal int Unit;                // ship instance id
    internal int Step;                // refreeze steps already applied (0..IceCarve.Steps)
}

// Channels carved by surface ships moving through ice at or above the sheet's
// edge (15 %). Each ship's track is recorded every SpacingM metres of travel,
// in the battle's geo frame (so it survives floating-origin recentres), and
// carved 1.5 x its beam wide (half width 16-60 m). A channel refreezes over
// RefreezeS of game time (SeaIceCarveMinutes, default 45 min; the game's
// mission clock, which follows time compression above 10x) in Steps equal
// steps: its width and its openness close linearly to nothing, then the
// segment is dropped. At most MaxSegments are kept (the oldest go first).
// Every change (a new segment, a refreeze step, an expiry) marks the 1 km
// sheet chunks the channel touches; the marks wait until the change is
// published in a snapshot, then those chunks (only) are rebuilt.
// Openness feeds the ship speed rule: in a channel the concentration counts
// as EffectivePercent = c x (1 - Relief x openness), a fresh channel through
// 60 % pack reading as 12 %. The ship's own fresh track (OwnGraceS) does not
// count, so a ship cannot ease itself.
// Snapshots are incremental and throttled: Publish(real seconds) builds at
// most one every MinPublishS of real time, and only the 1 km chunks that
// changed get new index objects; the others are shared with the previous
// snapshot. Snapshot() publishes at once (tests, diagnostics).
internal sealed class IceCarve
{
    internal const double WidthFactor = 1.5, MinHalfM = 16, MaxHalfM = 60, SpacingM = 25, Relief = 0.8, OwnGraceS = 120;
    internal const double JumpM = 2000, GapS = 60, ChunkKm = 1.0, MarginM = 10;
    // fastest plausible ship (m/s, about 78 kn): above it a move between two records is a jump
    internal const double MaxShipMs = 40;
    internal const double DefaultRefreezeMinutes = 45, MinRefreezeMinutes = 5, MaxRefreezeMinutes = 240;
    internal const double MinPublishS = 0.25; // real seconds between snapshot builds
    internal const int MaxSegments = 4096, Steps = 12;
    internal readonly double RefreezeS;
    private readonly List<IceCarveSegment> segs = new List<IceCarveSegment>();
    private struct Last { internal double E, N, T, HalfM; }
    private readonly Dictionary<int, Last> last = new Dictionary<int, Last>();
    private readonly HashSet<long> pending = new HashSet<long>(); // changed, not yet in the published snapshot
    private readonly HashSet<long> dirty = new HashSet<long>();   // published, waiting for the sheet to rebuild
    private IceCarveSnapshot snap;
    private double lastPublish = double.NegativeInfinity;
    internal int Version { get; private set; }
    internal int Added, Expired, Dropped, Publishes;

    internal IceCarve(double refreezeMinutes = DefaultRefreezeMinutes)
    {
        if (!(refreezeMinutes >= MinRefreezeMinutes && refreezeMinutes <= MaxRefreezeMinutes)) refreezeMinutes = DefaultRefreezeMinutes;
        RefreezeS = refreezeMinutes * 60;
        snap = new IceCarveSnapshot(segs, Version);
    }

    internal int Count => segs.Count;
    internal int Tracking => last.Count;
    internal double StepS => RefreezeS / Steps;

    internal static double HalfWidthM(double beamM)
    {
        if (double.IsNaN(beamM) || beamM <= 0) beamM = 15;
        return Math.Max(MinHalfM, Math.Min(MaxHalfM, beamM * WidthFactor / 2));
    }

    // Quantised openness 1 (fresh) .. 1/Steps; 0 once refrozen.
    internal static double Openness(int step) => step >= Steps ? 0 : 1 - (double)step / Steps;

    internal static double EffectivePercent(double percent, double openness)
    {
        if (double.IsNaN(percent)) return percent;
        return percent * (1 - Relief * Math.Max(0, Math.Min(1, openness)));
    }

    // The speed rule in a channel: the ice at the hull, the lightest ice ahead and the unquantised
    // reference all count lighter by the same openness, so the escape test (ahead <= here) compares
    // like with like and a channel never takes the escape speed away.
    internal static float CapInChannel(IceSpeedState s, float wanted, float flank, double here, double ahead, int capability, double reference, double openness)
    {
        if (!(openness > 0)) return s.Cap(wanted, flank, here, ahead, capability, reference);
        return s.Cap(wanted, flank, EffectivePercent(here, openness), EffectivePercent(ahead, openness), capability, EffectivePercent(reference, openness));
    }

    // The speed rule with the hull contact (SeaIceContact=1): after the channel's easing, the ice here,
    // the lightest ice ahead and the reference are all multiplied by the same gain (0 off the ice, 1 on
    // it), so the escape test still compares like with like (ahead <= here is kept by any gain) and
    // contact only ever eases the area rule. gain NaN or >= 1: exactly CapInChannel.
    internal static float CapInContact(IceSpeedState s, float wanted, float flank, double here, double ahead, int capability, double reference, double openness, double gain)
    {
        if (double.IsNaN(gain) || gain >= 1) return CapInChannel(s, wanted, flank, here, ahead, capability, reference, openness);
        double g = Math.Max(0, gain);
        return CapInChannel(s, wanted, flank, here * g, ahead * g, capability, reference * g, openness);
    }

    // A surface ship at (east, north) km, at game time t, in ice: extend its track. frameS is the
    // game time one frame spans (GameTime.deltaTime): at high time compression a ship moves hundreds
    // of metres between records, which is travel, not a jump or a gap.
    internal void Record(int unit, double eKm, double nKm, double t, double beamM, double frameS = 0)
    {
        double half = HalfWidthM(beamM);
        if (!last.TryGetValue(unit, out var l)) { last[unit] = new Last { E = eKm, N = nKm, T = t, HalfM = half }; return; }
        double d = Math.Sqrt((eKm - l.E) * (eKm - l.E) + (nKm - l.N) * (nKm - l.N)) * 1000;
        double dt = t - l.T;
        if (d > Math.Max(JumpM, MaxShipMs * dt) || dt > IceClock.Recent(GapS, frameS) || t < l.T) { last[unit] = new Last { E = eKm, N = nKm, T = t, HalfM = half }; return; }
        if (d < SpacingM) return;
        var s = new IceCarveSegment { E0 = l.E, N0 = l.N, E1 = eKm, N1 = nKm, T = t, HalfM = half, Unit = unit };
        segs.Add(s);
        Added++;
        MarkDirty(s, half);
        if (segs.Count > MaxSegments) { MarkDirty(segs[0], segs[0].HalfM); segs.RemoveAt(0); Dropped++; }
        last[unit] = new Last { E = eKm, N = nKm, T = t, HalfM = half };
        Version++;
    }

    // The ship left the ice (or the battle): its next point starts a new track.
    internal void Break(int unit) => last.Remove(unit);

    // Refreeze: apply the steps that are due, drop refrozen segments. Marks the chunks that change.
    internal void Advance(double t)
    {
        bool changed = false;
        for (int i = segs.Count - 1; i >= 0; i--)
        {
            var s = segs[i];
            int step = (int)Math.Floor(Math.Max(0, t - s.T) / StepS);
            if (step <= s.Step) continue;
            changed = true;
            MarkDirty(s, s.HalfM);
            if (step >= Steps) { segs.RemoveAt(i); Expired++; continue; }
            s.Step = step;
            segs[i] = s;
        }
        if (changed) Version++;
    }

    internal static long ChunkKey(int i, int j) => ((long)i << 32) ^ (uint)j;
    internal static void ChunkOf(long key, out int i, out int j) { i = (int)(key >> 32); j = (int)(key & 0xFFFFFFFFL); }

    private void MarkDirty(IceCarveSegment s, double halfM)
    {
        double r = (halfM * (1 + IceCarveSnapshot.RaggedAmp) + MarginM + SeaIceFloes.PushReachM) / 1000; // a pushed floe reaches beyond the edge
        int i0 = (int)Math.Floor((Math.Min(s.E0, s.E1) - r) / ChunkKm), i1 = (int)Math.Floor((Math.Max(s.E0, s.E1) + r) / ChunkKm);
        int j0 = (int)Math.Floor((Math.Min(s.N0, s.N1) - r) / ChunkKm), j1 = (int)Math.Floor((Math.Max(s.N0, s.N1) + r) / ChunkKm);
        for (int j = j0; j <= j1; j++)
            for (int i = i0; i <= i1; i++)
                if (IceCarveSnapshot.SegmentNearBox(s, r, i * ChunkKm, j * ChunkKm, (i + 1) * ChunkKm, (j + 1) * ChunkKm)) pending.Add(ChunkKey(i, j));
    }

    // Chunks changed and not rebuilt yet (published or still waiting for the next snapshot).
    internal int DirtyCount => dirty.Count + pending.Count;

    // Up to max dirty 1 km chunks (level 0 of the sheet) whose change is in the published snapshot,
    // removed from the set.
    internal List<long> TakeDirty(int max)
    {
        var list = new List<long>();
        foreach (var k in dirty) { if (list.Count >= max) break; list.Add(k); }
        foreach (var k in list) dirty.Remove(k);
        return list;
    }

    // The last published snapshot (never rebuilt here): what the speed rule and the mesher threads read.
    internal IceCarveSnapshot Published => snap;

    // Publish the changes if there are any and MinPublishS of real time has passed since the last build.
    internal bool Publish(double realNow)
    {
        if (pending.Count == 0 && snap.Version == Version) return false;
        if (realNow - lastPublish < MinPublishS && realNow >= lastPublish) return false;
        lastPublish = realNow;
        Build();
        return true;
    }

    // Publish now (whatever the throttle says) and return the current snapshot.
    internal IceCarveSnapshot Snapshot()
    {
        if (pending.Count > 0 || snap.Version != Version) Build();
        return snap;
    }

    private void Build()
    {
        snap = snap.With(segs, pending, Version);
        foreach (var k in pending) dirty.Add(k);
        pending.Clear();
        Publishes++;
    }
}

// The immutable view of the carve (mesher threads, the speed rule): per 1 km chunk, the segments
// that reach it with their current half width and openness, indexed in 250 m buckets. A new
// snapshot rebuilds only the chunks that changed and shares the rest with the one before.
internal sealed class IceCarveSnapshot
{
    internal const double BucketKm = 0.25, RaggedAmp = 0.3;
    private const int Per = 4; // buckets per chunk side: ChunkKm / BucketKm
    private const uint RagSeed = 0xC0FFEEu;
    internal readonly int Version;
    private readonly Dictionary<long, Chunk> chunks;
    private readonly int count, cells;
    internal readonly int ChunksBuilt, ChunksShared; // by the build that made this snapshot

    private sealed class Chunk
    {
        internal IceCarveSegment[] Segs;
        internal double[] Half, Open;  // current half width (m) and openness, per segment
        internal int[][] Buckets;      // Per x Per, row by row; null when empty
        internal int Cells;
    }

    // A full build.
    internal IceCarveSnapshot(List<IceCarveSegment> list, int version) : this(null, list, null, version) { }

    private IceCarveSnapshot(IceCarveSnapshot prev, List<IceCarveSegment> list, HashSet<long> changed, int version)
    {
        Version = version;
        count = list.Count;
        chunks = new Dictionary<long, Chunk>(prev != null ? prev.chunks.Count + (changed != null ? changed.Count : 0) : 16);
        if (prev != null)
            foreach (var kv in prev.chunks)
                if (!changed.Contains(kv.Key)) { chunks.Add(kv.Key, kv.Value); ChunksShared++; }
        // the segments of every chunk to (re)build
        var members = new Dictionary<long, List<int>>();
        for (int k = 0; k < list.Count; k++)
        {
            Range(list[k], out int i0, out int i1, out int j0, out int j1);
            int ci0 = FloorDiv(i0, Per), ci1 = FloorDiv(i1, Per), cj0 = FloorDiv(j0, Per), cj1 = FloorDiv(j1, Per);
            for (int cj = cj0; cj <= cj1; cj++)
                for (int ci = ci0; ci <= ci1; ci++)
                {
                    long key = IceCarve.ChunkKey(ci, cj);
                    if (changed != null && !changed.Contains(key)) continue;
                    if (!members.TryGetValue(key, out var m)) members[key] = m = new List<int>(8);
                    m.Add(k);
                }
        }
        foreach (var kv in members)
        {
            IceCarve.ChunkOf(kv.Key, out int ci, out int cj);
            var c = Make(list, kv.Value, ci, cj);
            if (c != null) { chunks[kv.Key] = c; ChunksBuilt++; }
        }
        foreach (var c in chunks.Values) cells += c.Cells;
    }

    // The next snapshot: the changed chunks rebuilt from the carve's segments, the others shared.
    internal IceCarveSnapshot With(List<IceCarveSegment> list, HashSet<long> changed, int version) => new IceCarveSnapshot(this, list, changed, version);

    private static int FloorDiv(int a, int b) => a >= 0 ? a / b : -((-a + b - 1) / b);

    private static double CurrentHalf(IceCarveSegment s) => s.HalfM * IceCarve.Openness(s.Step);

    // The 250 m buckets a segment's current channel (grown by its ragged edge) reaches.
    private static void Range(IceCarveSegment s, out int i0, out int i1, out int j0, out int j1)
    {
        double r = (CurrentHalf(s) * (1 + RaggedAmp) + 1) / 1000;
        i0 = (int)Math.Floor((Math.Min(s.E0, s.E1) - r) / BucketKm); i1 = (int)Math.Floor((Math.Max(s.E0, s.E1) + r) / BucketKm);
        j0 = (int)Math.Floor((Math.Min(s.N0, s.N1) - r) / BucketKm); j1 = (int)Math.Floor((Math.Max(s.N0, s.N1) + r) / BucketKm);
    }

    private static Chunk Make(List<IceCarveSegment> list, List<int> idx, int ci, int cj)
    {
        var c = new Chunk { Segs = new IceCarveSegment[idx.Count], Half = new double[idx.Count], Open = new double[idx.Count], Buckets = new int[Per * Per][] };
        var fill = new List<int>[Per * Per];
        for (int q = 0; q < idx.Count; q++)
        {
            var s = list[idx[q]];
            c.Segs[q] = s;
            c.Open[q] = IceCarve.Openness(s.Step);
            c.Half[q] = s.HalfM * c.Open[q];
            Range(s, out int i0, out int i1, out int j0, out int j1);
            for (int j = Math.Max(j0, cj * Per); j <= Math.Min(j1, cj * Per + Per - 1); j++)
                for (int i = Math.Max(i0, ci * Per); i <= Math.Min(i1, ci * Per + Per - 1); i++)
                {
                    int b = (j - cj * Per) * Per + (i - ci * Per);
                    (fill[b] ?? (fill[b] = new List<int>(4))).Add(q);
                }
        }
        for (int b = 0; b < fill.Length; b++) if (fill[b] != null) { c.Buckets[b] = fill[b].ToArray(); c.Cells++; }
        return c.Cells > 0 ? c : null;
    }

    internal int Count => count;
    internal int Cells => cells;
    internal int ChunkCount => chunks.Count;
    internal static readonly IceCarveSnapshot Empty = new IceCarveSnapshot(new List<IceCarveSegment>(), -1);

    // Does any channel reach this 1 km chunk (sheet level 0)?
    internal bool Touches(int chunkI, int chunkJ) => chunks.ContainsKey(IceCarve.ChunkKey(chunkI, chunkJ));

    // Does a channel reach this chunk or one next to it (a pushed floe can straddle the border)?
    internal bool TouchesNear(int chunkI, int chunkJ)
    {
        for (int dj = -1; dj <= 1; dj++)
            for (int di = -1; di <= 1; di++)
                if (Touches(chunkI + di, chunkJ + dj)) return true;
        return false;
    }

    private bool Bucket(double eKm, double nKm, out Chunk c, out int[] list)
    {
        list = null; c = null;
        int bi = (int)Math.Floor(eKm / BucketKm), bj = (int)Math.Floor(nKm / BucketKm);
        int ci = FloorDiv(bi, Per), cj = FloorDiv(bj, Per);
        if (!chunks.TryGetValue(IceCarve.ChunkKey(ci, cj), out c)) return false;
        list = c.Buckets[(bj - cj * Per) * Per + (bi - ci * Per)];
        return list != null;
    }

    // Distance from a point to a segment, metres.
    internal static double DistanceM(IceCarveSegment s, double eKm, double nKm)
    {
        double ax = s.E0 * 1000, ay = s.N0 * 1000, bx = s.E1 * 1000, by = s.N1 * 1000, px = eKm * 1000, py = nKm * 1000;
        double dx = bx - ax, dy = by - ay, l2 = dx * dx + dy * dy;
        double t = l2 > 0 ? Math.Max(0, Math.Min(1, ((px - ax) * dx + (py - ay) * dy) / l2)) : 0;
        double qx = ax + t * dx - px, qy = ay + t * dy - py;
        return Math.Sqrt(qx * qx + qy * qy);
    }

    internal static bool SegmentNearBox(IceCarveSegment s, double rKm, double x0, double y0, double x1, double y1)
    {
        // conservative: the segment's bounding box grown by r overlaps the box
        return Math.Min(s.E0, s.E1) - rKm < x1 && Math.Max(s.E0, s.E1) + rKm > x0 && Math.Min(s.N0, s.N1) - rKm < y1 && Math.Max(s.N0, s.N1) + rKm > y0;
    }

    // Ragged edge factor around 1 (+-30 %), fixed per place: value noise at about 14 m and 37 m.
    internal static double Ragged(double eKm, double nKm)
    {
        double v = 0.6 * SeaIceField.Value(eKm * 1000 / 14.0, nKm * 1000 / 14.0, RagSeed) + 0.4 * SeaIceField.Value(eKm * 1000 / 37.0 + 5.3, nKm * 1000 / 37.0 - 2.1, RagSeed ^ 0x55AA55u);
        return 1 + RaggedAmp * (2 * v - 1);
    }

    // The channel scalar at a point: negative inside a channel (about -1 on its centre line), positive
    // outside; +infinity far from any channel. The mesher takes min(ice, 0.5 x this). The ship's own
    // segments newer than excludeAfter (game seconds) do not count (the hull contact test's floe push,
    // as OpennessAt); the mesher counts every segment.
    internal double Field(double eKm, double nKm, int excludeUnit = int.MinValue, double excludeAfter = double.PositiveInfinity)
    {
        if (!Bucket(eKm, nKm, out var c, out var list)) return double.PositiveInfinity;
        double best = double.PositiveInfinity, rag = double.NaN;
        foreach (int k in list)
        {
            if (!(c.Half[k] > 0)) continue;
            if (c.Segs[k].Unit == excludeUnit && c.Segs[k].T > excludeAfter) continue;
            if (double.IsNaN(rag)) rag = Ragged(eKm, nKm);
            double hw = c.Half[k] * rag;
            double g = (DistanceM(c.Segs[k], eKm, nKm) - hw) / hw;
            if (g < best) best = g;
        }
        return best;
    }

    // Openness 0..1 of the channel a point lies in (0: none). The ship's own segments newer than
    // excludeAfter (game seconds) do not count.
    internal double OpennessAt(double eKm, double nKm, int excludeUnit = int.MinValue, double excludeAfter = double.PositiveInfinity)
    {
        if (!Bucket(eKm, nKm, out var c, out var list)) return 0;
        double best = 0;
        foreach (int k in list)
        {
            if (!(c.Half[k] > 0) || c.Open[k] <= best) continue;
            if (c.Segs[k].Unit == excludeUnit && c.Segs[k].T > excludeAfter) continue;
            if (DistanceM(c.Segs[k], eKm, nKm) <= c.Half[k] * Ragged(eKm, nKm)) best = c.Open[k];
        }
        return best;
    }
}

// Game-time windows: "seen recently" spans at least three frames of game time, so a check written
// for 1x (a second, five seconds) still holds when one frame covers a minute at 5000x.
internal static class IceClock
{
    internal static double Recent(double windowS, double frameS) => Math.Max(windowS, 3 * (frameS > 0 && !double.IsInfinity(frameS) ? frameS : 0));
    internal static bool Fresh(double now, double seen, double windowS, double frameS) => seen <= now + windowS && now - seen <= Recent(windowS, frameS);
}

// Broken floe pieces at a ship's bow: a fixed pool (Cap), each piece pushed
// outward and a little aft, drifting with water drag, tumbling slightly, then
// settling (sinking and shrinking over the last SettleShare of its life) into
// the channel edge. Positions are metres east/north in the battle frame, so the
// pieces survive floating-origin recentres. Each piece carries the weight of
// the ship that made it (IceBreakRule.PieceWeight: 1 near the camera, less
// farther out): when the pool is full a new piece takes the slot of the
// lowest-weight piece (the oldest among equals), and never one of a higher
// weight, so pieces at the ship the camera is on are not recycled for a
// distant breaker. Deterministic for a seed.
internal sealed class IcePieceSim
{
    internal struct Piece
    {
        internal bool Alive;
        internal double E, N;                 // metres in the battle frame
        internal float Ve, Vn;                // m/s
        internal float Yaw, Pitch, Roll, SpinYaw, SpinPitch, SpinRoll; // degrees, degrees per second
        internal float Size, Age, Life;       // metres, seconds
        internal float Weight;                // the spawning ship's share (0..1, by distance)
        internal int Serial;
    }
    internal const int DefaultCap = 120, MinCap = 0, MaxCap = 600;
    internal const float MinLife = 14, MaxLife = 30, SettleShare = 0.35f, DragS = 5f, SinkM = 0.6f;
    internal readonly Piece[] Pieces;
    private uint rng;
    private int serial;
    internal int Spawned, Recycled, Refused;

    internal IcePieceSim(int cap, uint seed)
    {
        Pieces = new Piece[Math.Max(MinCap, Math.Min(MaxCap, cap))];
        rng = seed == 0 ? 0x9E3779B9u : seed;
    }

    internal int Cap => Pieces.Length;
    internal int Alive { get { int n = 0; for (int i = 0; i < Pieces.Length; i++) if (Pieces[i].Alive) n++; return n; } }

    internal float U()
    {
        rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5;
        return (rng & 0xFFFFFF) / 16777216f;
    }

    // Spawn for one ship this step: bow at (e, n) metres, heading radians clockwise from north,
    // ship speed m/s, half beam m, intensity 0..1, accumulated count carried in acc; weight 0..1
    // (IceBreakRule.PieceWeight of the ship's distance from the camera) scales the rate and is the
    // pieces' claim on the pool.
    internal int Spawn(double bowE, double bowN, double headingRad, double speedMs, double halfBeamM, double intensity, double dt, ref double acc, double weight = 1)
    {
        if (double.IsNaN(weight)) weight = 0;
        weight = Math.Max(0, Math.Min(1, weight));
        if (Pieces.Length == 0 || !(intensity > 0) || !(dt > 0) || !(weight > 0)) { acc = 0; return 0; }
        acc += IceBreakRule.PieceRate(intensity) * weight * dt;
        int made = 0;
        double fe = Math.Sin(headingRad), fn = Math.Cos(headingRad); // forward
        double se = fn, sn = -fe;                                      // starboard
        while (acc >= 1)
        {
            acc -= 1;
            int slot = Free((float)weight);
            if (slot < 0) { acc = 0; break; }
            float side = U() < 0.5f ? -1f : 1f;
            double off = halfBeamM * (0.5 + 0.6 * U());
            double back = halfBeamM * 1.5 * U();
            double push = (0.6 + 1.4 * U()) * (0.5 + intensity);
            double aft = 0.15 * speedMs * (0.5 + U());
            ref var p = ref Pieces[slot];
            p = new Piece
            {
                Alive = true,
                E = bowE + side * se * off - fe * back,
                N = bowN + side * sn * off - fn * back,
                Ve = (float)(side * se * push - fe * aft),
                Vn = (float)(side * sn * push - fn * aft),
                Yaw = 360 * U(), Pitch = 6 * (U() - 0.5f), Roll = 6 * (U() - 0.5f),
                SpinYaw = 30 * (U() - 0.5f), SpinPitch = 16 * (U() - 0.5f), SpinRoll = 16 * (U() - 0.5f),
                Size = (float)(1.2 + 3.3 * U() * (0.5 + 0.5 * intensity)),
                Age = 0, Life = MinLife + (MaxLife - MinLife) * U(),
                Weight = (float)weight,
                Serial = ++serial,
            };
            made++; Spawned++;
        }
        return made;
    }

    // A free slot; when full the lowest-weight piece (oldest among equals), or -1 when every live
    // piece outweighs the new one.
    private int Free(float weight)
    {
        int victim = 0;
        for (int i = 0; i < Pieces.Length; i++)
        {
            if (!Pieces[i].Alive) return i;
            ref var p = ref Pieces[i];
            ref var v = ref Pieces[victim];
            if (p.Weight < v.Weight || (p.Weight == v.Weight && p.Serial < v.Serial)) victim = i;
        }
        if (Pieces[victim].Weight > weight + 1e-6f) { Refused++; return -1; }
        Recycled++;
        return victim;
    }

    internal void Step(float dt)
    {
        if (!(dt > 0)) return;
        float drag = (float)Math.Exp(-dt / DragS);
        for (int i = 0; i < Pieces.Length; i++)
        {
            ref var p = ref Pieces[i];
            if (!p.Alive) continue;
            p.Age += dt;
            if (p.Age >= p.Life) { p.Alive = false; continue; }
            p.E += p.Ve * dt; p.N += p.Vn * dt;
            p.Ve *= drag; p.Vn *= drag;
            p.Yaw += p.SpinYaw * dt;
            // the tumble decays as the piece settles
            p.Pitch = Math.Max(-8, Math.Min(8, p.Pitch + p.SpinPitch * dt * drag));
            p.Roll = Math.Max(-8, Math.Min(8, p.Roll + p.SpinRoll * dt * drag));
            p.SpinPitch *= drag; p.SpinRoll *= drag;
        }
    }

    // 1 until the settling share of the life, then down to 0.3 (shrink) at the end.
    internal static float ScaleAt(float age, float life)
    {
        float s = Settle(age, life);
        return 1 - 0.7f * s;
    }

    // Metres below the floating height: 0, then down to SinkM at the end.
    internal static float SinkAt(float age, float life) => SinkM * Settle(age, life);

    private static float Settle(float age, float life)
    {
        if (!(life > 0)) return 1;
        float start = life * (1 - SettleShare);
        return age <= start ? 0 : Math.Min(1, (age - start) / (life * SettleShare));
    }

    internal void Clear() { for (int i = 0; i < Pieces.Length; i++) Pieces[i].Alive = false; }
}

// How hard a ship is breaking ice: 0 when stopped (under MinSpeedKn), in open
// water or below the sheet's edge; rises with speed (full at FullSpeedKn) and
// with the effective concentration (full at FullPercent). It sets the piece
// rate, the sound and the hull's added radiated noise. Pieces go to the
// nearest PieceShips breakers within MaxPieceKm of the camera, at full rate
// within FullPieceKm and fewer farther out. Sounds follow time compression:
// cracks only at 1x or slower (on a real-time clock), every breaking sound
// muted above MaxSoundCompression.
internal static class IceBreakRule
{
    internal const double MinSpeedKn = 1.0, FullSpeedKn = 14, FullPercent = 80, MaxPiecesPerSecond = 5;
    internal const double MaxNoise = 8.0; // dB added to the ship's radiated broadband level at full intensity (the scale of BaseNoise and FlowNoise)
    internal const double LoopMinVolume = 0.12, LoopMaxVolume = 0.7, LoopMinPitch = 0.55, LoopMaxPitch = 0.8;
    internal const double CrackLongS = 6.0, CrackShortS = 1.4, GlobalCrackGapS = 0.5;
    internal const double FullPieceKm = 1.0, MaxPieceKm = 3.0, MaxSoundCompression = 2.0;
    internal const int PieceShips = 3;

    internal static double Intensity(double speedKn, double percent, double edgePercent)
    {
        speedKn = Math.Abs(speedKn);
        if (double.IsNaN(speedKn) || double.IsNaN(percent) || speedKn < MinSpeedKn || percent < edgePercent) return 0;
        return Math.Min(1, speedKn / FullSpeedKn) * Math.Min(1, percent / FullPercent);
    }

    // The intensity of a hull that meets the drawn ice only in part: the area's intensity times the
    // contact gain (0: in open water between floes, no pieces, sound or breaking noise).
    internal static double Intensity(double speedKn, double percent, double edgePercent, double contactGain)
    {
        double i = Intensity(speedKn, percent, edgePercent);
        if (double.IsNaN(contactGain) || contactGain >= 1) return i;
        return contactGain > 0 ? i * contactGain : 0;
    }

    internal static double PieceRate(double intensity) => MaxPiecesPerSecond * Math.Max(0, Math.Min(1, intensity));
    internal static double LoopVolume(double intensity) => intensity > 0 ? LoopMinVolume + (LoopMaxVolume - LoopMinVolume) * Math.Min(1, intensity) : 0;
    internal static double LoopPitch(double intensity) => LoopMinPitch + (LoopMaxPitch - LoopMinPitch) * Math.Max(0, Math.Min(1, intensity));
    // Seconds to the next crack for a uniform u 0..1: shorter when breaking harder.
    internal static double CrackInterval(double intensity, double u) => (CrackLongS + (CrackShortS - CrackLongS) * Math.Max(0, Math.Min(1, intensity))) * (0.7 + 0.6 * Math.Max(0, Math.Min(1, u)));
    internal static double Noise(double intensity) => MaxNoise * Math.Max(0, Math.Min(1, intensity));
    // A breaker's share of the piece pool by its distance from the camera: 1 within FullPieceKm, down to 0 at MaxPieceKm.
    internal static double PieceWeight(double distKm)
    {
        if (double.IsNaN(distKm) || distKm >= MaxPieceKm) return 0;
        if (distKm <= FullPieceKm) return 1;
        return (MaxPieceKm - distKm) / (MaxPieceKm - FullPieceKm);
    }
    // Breaking sounds at a time compression: full up to MaxSoundCompression, muted above.
    internal static double SoundGain(double compression) => compression > MaxSoundCompression ? 0 : 1;
    // One-shot cracks only at 1x or slower (an unknown compression counts as 1x).
    internal static bool CracksAllowed(double compression) => !(compression > 1.0001);
}

// Global rate limit for one-shot sounds: no two within the gap (the caller passes real seconds).
internal sealed class IceSoundGate
{
    private double next = double.NegativeInfinity;
    internal int Plays, Refused;
    internal bool TryPlay(double now, double gap)
    {
        if (now < next) { Refused++; return false; }
        next = now + gap;
        Plays++;
        return true;
    }
}

// The broken floe piece's shape: an irregular prism (Sides corners, radius about
// 0.5, from y = -0.8 to +0.2: a fifth floats above the water), closed, with flat
// face normals; the drawn piece is scaled to its size. One mesh serves the pool.
internal static class IcePieceMesh
{
    internal const float Top = 0.2f, Bottom = -0.8f;

    internal static void Build(int sides, uint seed, out float[] vertices, out float[] normals, out int[] triangles)
    {
        sides = Math.Max(3, sides);
        var rx = new double[sides]; var rz = new double[sides];
        uint h = seed == 0 ? 1u : seed;
        for (int k = 0; k < sides; k++)
        {
            h ^= h << 13; h ^= h >> 17; h ^= h << 5;
            double r = 0.38 + 0.12 * ((h & 0xFFFF) / 65535.0);
            double a = 2 * Math.PI * (k + 0.25 * ((h >> 16 & 0xFF) / 255.0 - 0.5)) / sides;
            rx[k] = r * Math.Sin(a); rz[k] = r * Math.Cos(a); // clockwise seen from above (north up, east right)
        }
        var v = new List<float>(); var n = new List<float>(); var t = new List<int>();
        // top: clockwise seen from above is a Unity front face from above
        int b0 = v.Count / 3;
        for (int k = 0; k < sides; k++) { v.Add((float)rx[k]); v.Add(Top); v.Add((float)rz[k]); n.Add(0); n.Add(1); n.Add(0); }
        for (int k = 1; k + 1 < sides; k++) { t.Add(b0); t.Add(b0 + k); t.Add(b0 + k + 1); }
        int b1 = v.Count / 3;
        for (int k = 0; k < sides; k++) { v.Add((float)rx[k]); v.Add(Bottom); v.Add((float)rz[k]); n.Add(0); n.Add(-1); n.Add(0); }
        for (int k = 1; k + 1 < sides; k++) { t.Add(b1); t.Add(b1 + k + 1); t.Add(b1 + k); }
        for (int k = 0; k < sides; k++)
        {
            int m = (k + 1) % sides;
            double dx = rx[m] - rx[k], dz = rz[m] - rz[k], l = Math.Sqrt(dx * dx + dz * dz);
            // the corner walk is clockwise from above, so outward is to the left of its direction
            float ox = (float)(-dz / l), oz = (float)(dx / l);
            int w = v.Count / 3;
            foreach (var (x, y, z) in new[] { (rx[k], Top, rz[k]), (rx[m], Top, rz[m]), (rx[m], Bottom, rz[m]), (rx[k], Bottom, rz[k]) })
            { v.Add((float)x); v.Add(y); v.Add((float)z); n.Add(ox); n.Add(0); n.Add(oz); }
            t.Add(w); t.Add(w + 2); t.Add(w + 1); t.Add(w); t.Add(w + 3); t.Add(w + 2);
        }
        vertices = v.ToArray(); normals = n.ToArray(); triangles = t.ToArray();
    }
}
