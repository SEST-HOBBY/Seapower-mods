namespace Sest.UiFixes
{
    internal sealed class CleanupBatchGate
    {
        internal int Pending { get; private set; }
        float first, last;
        internal void Request(float now)
        { if (Pending == 0) first = now; last = now; Pending++; }
        internal int Take(float now)
        {
            if (Pending == 0 || (now - last < 0.35f && now - first < 2f)) return 0;
            int count = Pending; Pending = 0; return count;
        }
        internal void Clear() { Pending = 0; first = last = 0; }
    }
}
