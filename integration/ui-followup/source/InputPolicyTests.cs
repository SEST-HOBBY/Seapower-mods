using System;
using Sest.UiFixes;
static class InputPolicyTests
{
    static void Main()
    {
        int cases = 0;
        // Reproduces the original failure: native time controls consume a key,
        // leaving EventType.Used and KeyCode.None. A disabled shortcut must fail.
        foreach (int eventType in new[] { 0, 1, 2, 3, 4, 5, 7, 8, 12 })
        {
            if (InputPolicy.MayMatch(0, eventType)) throw new Exception("Disabled shortcut matched");
            cases++;
        }
        foreach (int configuredKey in new[] { 32, 43, 45, 287 })
        {
            foreach (int eventType in new[] { 0, 1, 2, 3, 5, 7, 8, 12 })
            {
                if (InputPolicy.MayMatch(configuredKey, eventType)) throw new Exception("Consumed/non-key event matched");
                cases++;
            }
            if (!InputPolicy.MayMatch(configuredKey, 4)) throw new Exception("Custom key-down blocked");
            cases++;
        }
        Console.WriteLine(cases + " input regression cases passed");
    }
}
