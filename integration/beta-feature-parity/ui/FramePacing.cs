using UnityEngine;

namespace Sest.UiFixes
{
    internal static class FramePacing
    {
        static readonly FrameWindow window = new FrameWindow();
        static int lastFrame = -1;
        internal static void Clear() { window.Clear(); lastFrame = -1; StutterDiagnostics.Reset(); }
        internal static void Tick()
        {
            if (!PerformanceReview.Live || lastFrame == Time.frameCount) return;
            lastFrame = Time.frameCount;
            window.Add(Time.unscaledDeltaTime);
            StutterDiagnostics.Tick(Time.unscaledDeltaTime);
        }
        internal static void Report()
        {
            if (window.Count == 0) return;
            ContactsFix.Log("Frame pacing (30 s; wall time, not a CPU/GPU attribution): " + window.Count + " frames, " +
                (window.Count / window.Seconds).ToString("F1") + " fps avg, p95 " + (window.P95Ms == 1000 ? ">=1000" : "<=" + window.P95Ms) + " ms, max " +
                window.MaxMs.ToString("F1") + " ms, >50ms " + window.Over50 +
                "; actual VSync=" + QualitySettings.vSyncCount + "; target=" + Application.targetFrameRate +
                "; focused=" + Application.isFocused + "; resolution=" + Screen.width + "x" + Screen.height + ".");
            StutterDiagnostics.Report();
            CostCatalogueCache.Report();
            window.Clear();
        }
    }
}
