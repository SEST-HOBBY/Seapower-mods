namespace Sest.UiFixes
{
    internal sealed class UiRefreshGate
    {
        object window;
        bool open;
        float next;
        internal bool Due(object currentWindow, bool currentOpen, float now)
        {
            bool changed = !object.ReferenceEquals(window, currentWindow) || open != currentOpen;
            window = currentWindow; open = currentOpen;
            if (currentWindow == null) return false;
            if (!changed && now < next) return false;
            next = now + 0.2f;
            return true;
        }
    }
}
