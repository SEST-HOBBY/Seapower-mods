namespace Sest.UiFixes
{
    internal static class UiText
    {
        internal const string PreparationTitle = "AIRCRAFT AND UNIT PREPARATION";
        internal const string WorldPreparationTitle = "WORLD CAMPAIGN - BATTLE PREPARATION";
        internal const string WorldEndBattleLabel = "End battle...";
        internal const string WorldPreparationMessage =
            "SETUP PHASE - SIMULATION PAUSED\n\n" +
            "Choose Start preparation to close this briefing and arrange your force while paused.\n\n" +
            "1. Select a ship or airfield on the map or in Group Manager.\n" +
            "2. Open Flight Deck; choose aircraft, loadouts and preparation queues.\n" +
            "3. Set courses, formation, sensors and weapon status.\n" +
            "4. Review the force, then unpause to begin the battle.\n\n" +
            "The mission clock and enemy action begin when you unpause. Flight-deck timing follows the mission settings.\n\n" +
            "ENDING AN UNFINISHED BATTLE\n" +
            "Press Esc, choose End battle..., then leave the debrief to return to the world campaign. " +
            "Victory is not required. Review the campaign's warning before confirming; losses, expenditure and any unresolved fighting still apply.";
        internal static string WorldExitQuestion(string original, bool canGoBack)
        {
            // DCM passes the debrief's BackEnabled state, not a quit-game flag.
            // Preserve its complete warning in either return-to-map case.
            if (string.IsNullOrEmpty(original)) return original;
            return "END BATTLE AND RETURN TO CAMPAIGN\n\n" +
                "Victory is not required. Leaving does not grant a victory or undo combat. " +
                "The campaign's battle assessment and any unresolved-fighting consequences apply.\n\n" + original;
        }
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
