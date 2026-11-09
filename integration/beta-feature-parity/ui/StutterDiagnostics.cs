using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using Unity.Profiling;
using Unity.Profiling.LowLevel.Unsafe;
using UnityEngine;

namespace Sest.UiFixes
{
    // Observe existing work. Never skip an original method, force a collection,
    // change a graphics setting, or enable the full Unity profiler.
    internal static class StutterDiagnostics
    {
        internal struct Stamp { internal long Time, Bytes; }
        sealed class MethodSample
        {
            internal readonly string Name;
            internal long Count, Ticks, Maximum, Bytes;
            internal MethodSample(MethodBase method) { Name = method.DeclaringType.FullName + "." + method.Name; }
            internal void Clear() { Count = Ticks = Maximum = Bytes = 0; }
        }
        sealed class Counter
        {
            internal string Name;
            internal ProfilerMarkerDataUnit Unit;
            internal ProfilerRecorder Recorder;
            internal long Count, Total, Maximum, Last;
            internal void Tick()
            {
                if (!Recorder.Valid || !Recorder.IsRunning) return;
                long value = Recorder.LastValue;
                if (value < 0) return;
                Count++; Total += value; Maximum = Math.Max(Maximum, value); Last = value;
            }
            internal void Clear() { Count = Total = Maximum = Last = 0; }
        }
        static readonly Dictionary<MethodBase, MethodSample> methods = new Dictionary<MethodBase, MethodSample>();
        static readonly List<Counter> counters = new List<Counter>();
        static readonly string[] wantedCounters = {
            "Main Thread", "Render Thread", "PlayerLoop", "GC.Collect", "GarbageCollector.CollectIncremental",
            "Gfx.WaitForPresentOnGfxThread", "Gfx.WaitForRenderThread", "GfxDevice.WaitForRenderThread", "WaitForTargetFPS",
            "CPU Main Thread Frame Time", "CPU Render Thread Frame Time", "CPU Main Thread Present Wait Time",
            "GPU Frame Time", "GC Allocated In Frame", "GC Used Memory", "GC Reserved Memory"
        };
        static Func<long> allocated;
        static bool active, failed, installed;
        static int frames, previous0, previous1, previous2, delta0, delta1, delta2, slowWithCollection;
        static long previousBytes, allocatedBytes;
        static string incremental = "unavailable";

        internal static void Install()
        {
            var hooks = new Harmony("io.github.sest-hobby.stutter-observations");
            try
            {
                var allocation = typeof(GC).GetMethod("GetAllocatedBytesForCurrentThread", Type.EmptyTypes);
                if (allocation != null)
                {
                    try { allocated = (Func<long>)Delegate.CreateDelegate(typeof(Func<long>), allocation); long before = allocated();
                        var probe = new byte[1024];
                        long after = allocated();
                        GC.KeepAlive(probe);
                        if (after <= before) allocated = null; }
                    catch { allocated = null; }
                }
                foreach (var known in DiagnosticModules.Known)
                {
                    var assembly = AppDomain.CurrentDomain.GetAssemblies().FirstOrDefault(a => a.GetName().Name == known[0]);
                    if (assembly == null) continue;
                    try
                    {
                        ContactsFix.Require(assembly, known[1]);
                        foreach (var type in assembly.GetTypes())
                            if (typeof(MonoBehaviour).IsAssignableFrom(type))
                                foreach (var method in type.GetMethods(ContactsFix.All | BindingFlags.DeclaredOnly))
                                    if (!method.IsStatic && !method.ContainsGenericParameters && !method.IsAbstract &&
                                        method.ReturnType == typeof(void) && method.GetParameters().Length == 0 &&
                                        (method.Name == "Update" || method.Name == "LateUpdate" || method.Name == "FixedUpdate" || method.Name == "OnGUI"))
                                        Watch(hooks, method);
                        if (known[0] == "SEST.RuntimeFixes")
                            foreach (var pair in new[] { "F11CombatCosts.AfterTick", "F11CombatCosts.SyncWindow", "CampaignCosts.Prices", "CampaignCosts.LiveView", "NativeCombatSurface.Tick", "PopOutBridge.EnsureBound" })
                            {
                                int split = pair.LastIndexOf('.');
                                var type = assembly.GetType("Sest.RuntimeFixes." + pair.Substring(0, split), true);
                                Watch(hooks, type.GetMethod(pair.Substring(split + 1), ContactsFix.All));
                            }
                    }
                    catch (Exception e) { ContactsFix.Log("Stutter observations skipped " + known[0] + ": " + e.Message); }
                }
                foreach (var type in new[] { typeof(SeaPower.GameMain), typeof(SeaPower.CameraManager) })
                    foreach (var method in type.GetMethods(ContactsFix.All | BindingFlags.DeclaredOnly))
                        if (method.ReturnType == typeof(void) && method.GetParameters().Length == 0 &&
                            (method.Name == "Update" || method.Name == "LateUpdate" || method.Name == "FixedUpdate" ||
                             method.Name == "OnUpdate" || method.Name == "OnLateUpdate"))
                            Watch(hooks, method);
                foreach (var method in typeof(NoesisView).GetMethods(ContactsFix.All | BindingFlags.DeclaredOnly))
                    if (method.Name == "RenderOffscreen") Watch(hooks, method);
                installed = true;
                ContactsFix.Log("Stutter observations installed: " + methods.Count + " timing hooks; main-thread allocation counter " + (allocated != null ? "available" : "unavailable") + ". Original methods and GC policy retained.");
            }
            catch (Exception e)
            {
                hooks.UnpatchSelf(); methods.Clear();
                ContactsFix.Log("Stutter observations inactive: " + e.Message);
            }
        }
        static void Watch(Harmony hooks, MethodInfo method)
        {
            if (method == null || methods.ContainsKey(method)) return;
            methods.Add(method, new MethodSample(method));
            try { hooks.Patch(method, prefix: new HarmonyMethod(typeof(StutterDiagnostics), nameof(Begin)), finalizer: new HarmonyMethod(typeof(StutterDiagnostics), nameof(Finish))); }
            catch { methods.Remove(method); throw; }
        }
        public static void Begin(out Stamp __state)
        {
            __state = default;
            try
            {
                if (!active || !PerformanceReview.Live) return;
                __state.Bytes = allocated != null ? allocated() : 0;
                __state.Time = Stopwatch.GetTimestamp();
            }
            catch (Exception e) { __state = default; Disable(e); }
        }
        public static Exception Finish(MethodBase __originalMethod, Stamp __state, Exception __exception)
        {
            try
            {
                if (__state.Time != 0 && methods.TryGetValue(__originalMethod, out var sample))
                {
                    long ticks = Stopwatch.GetTimestamp() - __state.Time;
                    sample.Count++; sample.Ticks += ticks; sample.Maximum = Math.Max(sample.Maximum, ticks);
                    if (allocated != null) sample.Bytes += Math.Max(0, allocated() - __state.Bytes);
                }
            }
            catch (Exception e) { Disable(e); }
            return __exception;
        }
        static void Start()
        {
            var available = new List<ProfilerRecorderHandle>();
            ProfilerRecorderHandle.GetAvailable(available);
            foreach (var handle in available)
            {
                var description = ProfilerRecorderHandle.GetDescription(handle);
                if (!wantedCounters.Contains(description.Name)) continue;
                var recorder = new ProfilerRecorder(handle, 1, ProfilerRecorderOptions.Default | ProfilerRecorderOptions.StartImmediately);
                if (recorder.Valid && recorder.IsRunning)
                    counters.Add(new Counter { Name = description.Name, Unit = description.UnitType, Recorder = recorder });
                else recorder.Dispose();
            }
            try { incremental = UnityEngine.Scripting.GarbageCollector.isIncremental.ToString(); } catch { }
            previous0 = GC.CollectionCount(0); previous1 = GC.CollectionCount(1); previous2 = GC.CollectionCount(2);
            previousBytes = allocated != null ? allocated() : 0;
            active = true;
            ContactsFix.Log("Stutter counter availability: " + (counters.Count == 0 ? "none in this player" : string.Join(", ", counters.Select(c => c.Name + " [" + c.Unit + "]"))) + "; incremental GC=" + incremental + ". Missing counters are unavailable, not zero. First window includes diagnostic startup.");
        }
        internal static void Tick(float wallSeconds)
        {
            if (!installed || failed || !PerformanceReview.Live) return;
            try
            {
                if (!active) { Start(); return; }
                frames++;
                int a = GC.CollectionCount(0), b = GC.CollectionCount(1), c = GC.CollectionCount(2);
                int d0 = Math.Max(0, a - previous0), d1 = Math.Max(0, b - previous1), d2 = Math.Max(0, c - previous2);
                delta0 += d0; delta1 += d1; delta2 += d2;
                if (wallSeconds > 0.05f && (d0 > 0 || d1 > 0 || d2 > 0)) slowWithCollection++;
                previous0 = a; previous1 = b; previous2 = c;
                if (allocated != null)
                {
                    long bytes = allocated(); allocatedBytes += Math.Max(0, bytes - previousBytes); previousBytes = bytes;
                }
                foreach (var counter in counters) counter.Tick();
            }
            catch (Exception e) { Disable(e); }
        }
        internal static void Report()
        {
            if (!active || failed) return;
            try
            {
                double ms = 1000.0 / Stopwatch.Frequency;
                ContactsFix.Log("Stutter memory (between Update observations; GC/frame overlap is correlation): frames=" + frames +
                    "; collections gen0/1/2=" + delta0 + "/" + delta1 + "/" + delta2 +
                    "; >50ms observations with collection=" + slowWithCollection +
                    "; main-thread allocated=" + (allocated != null ? (allocatedBytes / 1048576.0).ToString("F2") + " MiB" : "unavailable") +
                    "; incremental GC=" + incremental + ".");
                var measured = methods.Values.Where(s => s.Count != 0).ToArray();
                ContactsFix.Log("Stutter UI methods (elapsed; nested; do not add): " + string.Join(" | ", measured.OrderByDescending(s => s.Maximum).Take(10).Select(s =>
                    s.Name + " " + s.Count + "x avg " + (s.Ticks * ms / s.Count).ToString("F3") + " max " + (s.Maximum * ms).ToString("F2") + " ms")));
                if (allocated != null)
                    ContactsFix.Log("Stutter UI allocations (nested; main thread): " + string.Join(" | ", measured.OrderByDescending(s => s.Bytes).Take(6).Select(s => s.Name + " " + (s.Bytes / 1048576.0).ToString("F2") + " MiB")));
                foreach (var counter in counters.Where(c => c.Count != 0))
                    ContactsFix.Log("Stutter native counter: " + counter.Name + "; unit=" + counter.Unit + "; polls=" + counter.Count +
                        "; last=" + counter.Last + "; max=" + counter.Maximum + ". Marker values may persist between events; waits are not CPU/GPU attribution.");
                ClearWindow();
            }
            catch (Exception e) { Disable(e); }
        }
        static void ClearWindow()
        {
            frames = delta0 = delta1 = delta2 = slowWithCollection = 0; allocatedBytes = 0;
            foreach (var sample in methods.Values) sample.Clear();
            foreach (var counter in counters) counter.Clear();
        }
        static void Disable(Exception e)
        {
            End(); failed = true;
            ContactsFix.Log("Stutter observations stopped; original behavior retained: " + e.Message);
        }
        internal static void Reset() { End(); failed = false; ClearWindow(); }
        internal static void End()
        {
            active = false;
            foreach (var counter in counters)
                try { counter.Recorder.Dispose(); } catch { }
            counters.Clear();
        }
    }
}
