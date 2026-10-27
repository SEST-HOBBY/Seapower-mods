namespace Sest.UiFixes
{
    public static class InputPolicy
    {
        // Unity EventType.KeyDown=4, KeyUp=5, Used=12. KeyCode.None=0.
        public static bool MayMatch(int configuredKey, int eventType)
        {
            return configuredKey != 0 && eventType == 4;
        }
    }
}
