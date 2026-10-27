namespace Sest.UiFixes
{
    internal enum CompassDestination { Hidden, Main3D, Detached3D, Pip3D }
    internal static class CompassRouting
    {
        internal static CompassDestination Choose(bool hudVisible, bool fullMap, bool detached, bool pip3D)
        {
            if (!hudVisible) return CompassDestination.Hidden;
            if (detached) return CompassDestination.Detached3D;
            if (!fullMap) return CompassDestination.Main3D;
            return pip3D ? CompassDestination.Pip3D : CompassDestination.Hidden;
        }
    }
}
