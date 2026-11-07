namespace Sest.UiFixes
{
    internal static class UiText
    {
        internal const string PreparationTitle = "AIRCRAFT AND UNIT PREPARATION";
        internal const string PreparationMessage = PreparationTitle +
            "|Choose Start preparation and keep the simulation paused.\\n\\n" +
            "1. Select a ship or airfield on the map or in Formation Manager.\\n" +
            "2. Open Flight Deck, choose aircraft and loadouts, and queue their preparation.\\n" +
            "3. Set course, formation, weapon status and sensors.\\n" +
            "4. Review the force, then unpause to begin.\\n\\n" +
            "When flight-deck timings are enabled, the first unpause completes the opening preparation queue. " +
            "The mission clock and enemy action start at the same time.|Start preparation";
        internal static string Preparation(string text)
        {
            return text != null && text.StartsWith(PreparationTitle + "|", System.StringComparison.OrdinalIgnoreCase)
                ? PreparationMessage : text;
        }
    }
}
