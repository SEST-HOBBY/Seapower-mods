using System;

namespace Sest.UiFixes
{
    static class UiRefinementTests
    {
        static int checks;
        static void Check(bool value, string message) { checks++; if (!value) throw new Exception(message); }
        static void Route(bool hud, bool map, bool detached, bool pip, CompassDestination expected)
        { Check(CompassRouting.Choose(hud, map, detached, pip) == expected, "Wrong camera-compass destination"); }
        static void Main()
        {
            // Explicit scenario expectations: map-only never receives a compass,
            // while the actual detached world view takes precedence over local PiP.
            Route(true, true, true, true, CompassDestination.Detached3D);
            Route(true, true, true, false, CompassDestination.Detached3D);
            Route(true, false, true, true, CompassDestination.Detached3D);
            Route(true, false, true, false, CompassDestination.Detached3D);
            Route(true, true, false, true, CompassDestination.Pip3D);
            Route(true, true, false, false, CompassDestination.Hidden);
            Route(true, false, false, true, CompassDestination.Main3D);
            Route(true, false, false, false, CompassDestination.Main3D);
            for (int scene = 0; scene < 8; scene++)
                Route(false, (scene & 1) != 0, (scene & 2) != 0, (scene & 4) != 0, CompassDestination.Hidden);

            string truncated = UiText.PreparationTitle + "|Choose Start preparation to close this message. Keep the simulation paused";
            string full = truncated + "; select your ships|Start preparation";
            Check(UiText.Preparation(truncated) == UiText.PreparationMessage, "Captured truncated popup must be repaired");
            Check(UiText.Preparation(full) == UiText.PreparationMessage, "Old full preparation message must be repaired");
            Check(UiText.Preparation(truncated.ToLowerInvariant()) == UiText.PreparationMessage, "Preparation header case");
            Check(UiText.Preparation(null) == null, "Null popup must remain native");
            foreach (string other in new[] { "", "Other briefing|Mission orders|Close", "AIRCRAFT AND UNIT PREPARATION EXTRA|Keep", UiText.PreparationTitle })
                Check(UiText.Preparation(other) == other, "Unrelated briefing must remain unchanged");
            Check(!UiText.PreparationMessage.Contains(";"), "INI comment delimiter must not truncate preparation text");
            var parts = UiText.PreparationMessage.Split('|');
            Check(parts.Length == 3, "Native popup title/body/button fields");
            Check(parts[0] == UiText.PreparationTitle && parts[2] == "Start preparation", "Visible action must match instructions");
            string body = parts[1].Replace("\\n", "\n");
            foreach (string step in new[] { "1. Select", "2. Open Flight Deck", "3. Set course", "4. Review" })
                Check(body.Contains("\n" + step), "Preparation steps must render on separate lines");
            Check(body.Contains("keep the simulation paused") && body.Contains("first unpause"), "Opening preparation timing must be explained");
            Check(body.Length < 700, "Instructions must fit the native modal");
            var bounds = new FormationBoundsGate();
            Check(!bounds.Changed(1000, 500), "Initial dirty flag is already set by the author");
            int idleRefits = 0;
            for (int i = 0; i < 7500; i++) if (bounds.Changed(1000, 500)) idleRefits++;
            Check(idleRefits == 0, "Ten minutes of idle panel ticks must not invalidate fitting");
            Check(bounds.Changed(1000, 320), "Moving to a shorter monitor must refit even with unchanged window width");
            Check(!bounds.Changed(1000, 320), "A completed monitor change must not cause recurring refits");
            Check(bounds.Changed(850, 320), "Changing available width must refit");
            Check(!bounds.Changed(850.1f, 320.1f), "Subpixel noise must not cause refit cycles");
            Check(bounds.Changed(850.7f, 320.7f), "Accumulated bounds change must eventually refit");
            Check(!bounds.Changed(float.NaN, 320), "Invalid transient native dimensions must not enter the cache");
            Console.WriteLine("Preparation/compass scenario checks passed: " + checks);
        }
    }
}
