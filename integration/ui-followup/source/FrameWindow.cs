using System;

namespace Sest.UiFixes
{
    internal sealed class FrameWindow
    {
        readonly int[] histogram = new int[1001];
        internal int Count { get; private set; }
        internal int Over50 { get; private set; }
        internal double Seconds { get; private set; }
        internal double MaxMs { get; private set; }
        internal void Add(double seconds)
        {
            if (seconds <= 0 || double.IsNaN(seconds) || double.IsInfinity(seconds)) return;
            double ms = seconds * 1000;
            Count++; Seconds += seconds; MaxMs = Math.Max(MaxMs, ms);
            if (ms > 50) Over50++;
            histogram[(int)Math.Min(1000, Math.Ceiling(ms))]++;
        }
        internal int P95Ms
        {
            get
            {
                if (Count == 0) return 0;
                int threshold = (int)Math.Ceiling(Count * 0.95), seen = 0;
                for (int i = 0; i < histogram.Length; i++) { seen += histogram[i]; if (seen >= threshold) return i; }
                return 1000;
            }
        }
        internal void Clear()
        { Array.Clear(histogram, 0, histogram.Length); Count = Over50 = 0; Seconds = MaxMs = 0; }
    }
}
