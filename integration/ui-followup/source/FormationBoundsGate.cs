using System;

namespace Sest.UiFixes
{
    internal sealed class FormationBoundsGate
    {
        bool known;
        float width, height;
        internal bool Changed(float availableWidth, float availableHeight)
        {
            // Match the author's effective limits. A monitor switch can change
            // the available height without changing a manually saved window size.
            float w = Math.Max(0, availableWidth);
            float h = Math.Max(36, Math.Min(500, availableHeight));
            if (float.IsNaN(w) || float.IsNaN(h)) return false;
            if (!known) { known = true; width = w; height = h; return false; }
            if (Math.Abs(w - width) <= 0.5f && Math.Abs(h - height) <= 0.5f) return false;
            width = w; height = h;
            return true;
        }
    }
}
