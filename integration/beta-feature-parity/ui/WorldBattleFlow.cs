using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using AnchorChain;
using HarmonyLib;
using SeaPower;
using SeapowerUI;
using SeapowerUI.ViewModels;

namespace Sest.UiFixes
{
    // A new GameMain is also created for a replay. Offer once per battle, at
    // its first ready tick, and only while still paused at the opening; never
    // interrupt someone who has already unpaused and played on.
    internal sealed class WorldBattleOpeningGate
    {
        // Unpaused mission seconds still counted as the opening. The native
        // mission load pauses the clock (SceneCreator.LoadMission), so a fresh
        // battle is normally at or near 0 when the UI becomes ready.
        internal const double OpeningSeconds = 5;
        object observed;
        // sessionSeconds is GameTime.missionSessionTime: unpaused time in this
        // mission, reset on every mission load (GameInitializer.init ->
        // GameTime.OnStart -> InitGameTimes). GameTime.missionElapsedTime is
        // never reset after start-up, so it cannot identify an opening.
        internal bool Offer(object game, bool worldBattle, bool ready, double sessionSeconds, bool paused)
        {
            if (!worldBattle) { Reset(); return false; }
            if (game == null || !ready || ReferenceEquals(observed, game)) return false;
            observed = game;
            // Running at this point is the load's doing, not the player's:
            // Dynamic Campaign Mod's battles start with the clock running
            // (owner's PC, 21 Nov 2026), and no one can unpause within the
            // first seconds of a battle. The caller pauses before the
            // checklist opens. Past the allowance the clock is left alone.
            return sessionSeconds >= 0 && sessionSeconds <= OpeningSeconds;
        }
        internal void Reset() { observed = null; }
    }

    internal static class WorldBattleFlow
    {
        const string CampaignHash = "652fe464dc23ac3c0063e5ab09dc4656634f30d1d254c782498ef779cb30ac77";
        static readonly WorldBattleOpeningGate opening = new WorldBattleOpeningGate();
        static PropertyInfo active, buttonText;
        static Type messageBox;
        static FieldInfo initialized, closing, section, key;
        static MethodInfo ownsMission;
        static bool bound, unavailable, preparationFailed;
        static double nextBind;
        static object preparation;
        // For the first minute after a world battle's checklist opens, record
        // what starts the clock (one stack per change), so a PC log names it.
        static double openingUntil;
        static bool heldOnce;
        static float lastLoggedSpeed = -1;
        public static void AfterSpeedChange()
        {
            try
            {
                if (UnityEngine.Time.realtimeSinceStartupAsDouble > openingUntil) return;
                float speed = GameTime.TimeCompression;
                if (speed == lastLoggedSpeed) return;
                lastLoggedSpeed = speed;
                var frames = new System.Diagnostics.StackTrace(1, false).GetFrames() ?? new System.Diagnostics.StackFrame[0];
                var callers = string.Join(" <- ", frames.Take(6).Select(f => f.GetMethod()).Where(m => m != null)
                    .Select(m => (m.DeclaringType != null ? m.DeclaringType.Name + "." : "") + m.Name));
                ContactsFix.Log("World battle opening: clock speed now " + speed + " (paused=" + GameTime.IsPaused() + ") from " + callers);
            }
            catch { }
        }

        internal static bool Bind(Assembly campaign)
        {
            using (var sha = SHA256.Create())
            using (var stream = File.OpenRead(BetaAssemblyPolicy.OriginalLocation(campaign)))
                if (BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant() != CampaignHash)
                    return false;
            Type battle = campaign.GetType("DynamicCampaignMod.Game.Battle.BattleSession", true);
            active = battle.GetProperty("Active", ContactsFix.All);
            ownsMission = battle.GetProperty("IsOurMission", ContactsFix.All)?.GetGetMethod(true);
            var question = battle.GetMethod("LeaveConfirmation", ContactsFix.All, null, new[] { typeof(bool) }, null);
            initialized = typeof(GameMain).GetField("_initialized", ContactsFix.All);
            closing = typeof(GameMain).GetField("_closing", ContactsFix.All);
            section = typeof(PauseMenuButton).GetField("contentSection", ContactsFix.All);
            key = typeof(PauseMenuButton).GetField("contentKey", ContactsFix.All);
            buttonText = typeof(PauseMenuButton).GetProperty("ButtonContent", ContactsFix.All);
            messageBox = typeof(PauseMenuViewModel).Assembly.GetType("SeapowerUI.ViewModels.MessageBoxViewModel", true);
            if (active?.PropertyType != typeof(bool) || active.GetGetMethod(true)?.IsStatic != true ||
                ownsMission?.ReturnType != typeof(bool) || !ownsMission.IsStatic ||
                question?.ReturnType != typeof(string) || !question.IsStatic ||
                initialized?.FieldType != typeof(bool) || closing?.FieldType != typeof(bool) ||
                section?.FieldType != typeof(string) || key?.FieldType != typeof(string) ||
                buttonText?.PropertyType != typeof(string) || buttonText.GetSetMethod(true) == null)
                throw new MissingMemberException("inspected world-battle preparation and exit presentation");
            foreach (var name in new[] { "Header", "Message", "MessageBoxType", "AcknowledgeCommandLabel", "AcknowledgeCommand" })
                if (messageBox.GetProperty(name, ContactsFix.All)?.GetSetMethod(true) == null)
                    throw new MissingMemberException("inspected native preparation message box: " + name);
            return true;
        }

        static void TryAttach()
        {
            if (bound || unavailable || UnityEngine.Time.realtimeSinceStartupAsDouble < nextBind) return;
            nextBind = UnityEngine.Time.realtimeSinceStartupAsDouble + 2;
            var campaign = AppDomain.CurrentDomain.GetAssemblies().FirstOrDefault(a =>
                a.GetType("DynamicCampaignMod.Game.Battle.BattleSession", false) != null);
            if (campaign == null) return;
            var hooks = new Harmony("io.github.sest-hobby.world-battle-presentation");
            try
            {
                if (!Bind(campaign)) throw new InvalidOperationException("uninspected Dynamic Campaign Mod image");
                hooks.Patch(typeof(PauseMenuViewModel).GetMethod("InitialiseMissionPause", ContactsFix.All),
                    postfix: new HarmonyMethod(typeof(WorldBattleFlow), nameof(AfterPauseMenu)));
                hooks.Patch(typeof(PauseMenuButton).GetMethod("Button_LanguageChanged", ContactsFix.All),
                    postfix: new HarmonyMethod(typeof(WorldBattleFlow), nameof(AfterLanguage)));
                var question = campaign.GetType("DynamicCampaignMod.Game.Battle.BattleSession", true)
                    .GetMethod("LeaveConfirmation", ContactsFix.All, null, new[] { typeof(bool) }, null);
                hooks.Patch(question, postfix: new HarmonyMethod(typeof(WorldBattleFlow), nameof(AfterExitQuestion)));
                foreach (var setter in new[] { typeof(GameTime).GetMethod("SetTimeCompression", ContactsFix.All, null, new[] { typeof(float) }, null),
                                               typeof(GameTime).GetProperty("TimeCompression", ContactsFix.All)?.GetSetMethod(true) })
                    if (setter != null) hooks.Patch(setter, postfix: new HarmonyMethod(typeof(WorldBattleFlow), nameof(AfterSpeedChange)));
                bound = true;
                ContactsFix.Log("World battles: paused preparation checklist and End battle pause-menu label installed; original exit commands retained.");
            }
            catch (Exception e)
            {
                hooks.UnpatchSelf(); unavailable = true;
                ContactsFix.Log("World-battle presentation unavailable; original mission UI retained: " + e.Message);
            }
        }

        static bool IsBattle()
        {
            return bound && (bool)active.GetValue(null, null) && (bool)ownsMission.Invoke(null, null);
        }

        internal static void Relabel(PauseMenuButton button, bool worldBattle)
        {
            if (!worldBattle || button == null || (string)section.GetValue(button) != "PauseMenu" ||
                (string)key.GetValue(button) != "Exit") return;
            // Change only the caption. The original command, enabled state,
            // debrief and DCM's detailed leave/auto-resolution warning survive.
            buttonText.GetSetMethod(true).Invoke(button, new object[] { UiText.WorldEndBattleLabel });
        }

        public static void AfterPauseMenu(PauseMenuViewModel __instance)
        {
            if (!IsBattle() || __instance.PauseMenuButtons == null) return;
            foreach (var button in __instance.PauseMenuButtons) Relabel(button, true);
        }
        public static void AfterLanguage(PauseMenuButton __instance) { Relabel(__instance, IsBattle()); }
        public static void AfterExitQuestion(bool __0, ref string __result)
        {
            if (IsBattle()) __result = UiText.WorldExitQuestion(__result, __0);
        }

        internal static void Tick()
        {
            TryAttach();
            if (!bound || preparationFailed) return;
            try
            {
                bool battle = IsBattle();
                if (!battle) { opening.Reset(); preparation = null; heldOnce = false; return; }
                if (!Singleton<GameMain>.InstanceExists() || MainGameView.Instance == null) return;
                var game = Singleton<GameMain>.Instance;
                // While the checklist is open the battle stays paused. The
                // game counts itself paused whenever Time.timeScale is near
                // zero, which it is for a moment during the load, so the
                // checklist can open "paused" and the game then start its
                // clock behind it (owner's PC, 21 Nov 2026). Hold it here.
                if (preparation != null && !GameTime.IsPaused())
                {
                    GameTime.Pause(true);
                    if (!heldOnce)
                    {
                        heldOnce = true;
                        ContactsFix.Log("World battle: the clock started behind the open preparation checklist; paused again until the player starts it.");
                    }
                }
                bool ready = (bool)initialized.GetValue(game) && !(bool)closing.GetValue(game);
                if (!opening.Offer(game, true, ready, GameTime.missionSessionTime, GameTime.IsPaused())) return;
                bool wasRunning = !GameTime.IsPaused();
                if (wasRunning) GameTime.Pause(true);
                openingUntil = UnityEngine.Time.realtimeSinceStartupAsDouble + 60;
                // The game's message-box model is internal in the inspected
                // beta. Use its native host/template, as DCM itself does.
                var box = Activator.CreateInstance(messageBox, true);
                SetBox(box, "Header", UiText.WorldPreparationTitle);
                SetBox(box, "Message", UiText.WorldPreparationMessage);
                SetBox(box, "MessageBoxType", MessageBoxType.Info);
                SetBox(box, "AcknowledgeCommandLabel", "Start preparation");
                SetBox(box, "AcknowledgeCommand", new DelegateCommand(_ => ClosePreparation(box)));
                preparation = box;
                WindowHostCommands.OpenWindowCommand.Execute(box, MainGameView.Instance);
                ContactsFix.Log(wasRunning
                    ? "World battle loaded with the clock running; paused for the preparation checklist. Start preparation keeps the mission paused."
                    : "World battle preparation checklist opened while paused; Start preparation keeps the mission paused.");
            }
            catch (Exception e)
            {
                preparationFailed = true;
                ContactsFix.Log("World preparation checklist unavailable; original pause-menu exit retained: " + e.Message);
            }
        }

        static void SetBox(object box, string name, object value)
        {
            messageBox.GetProperty(name, ContactsFix.All).GetSetMethod(true).Invoke(box, new[] { value });
        }

        static void ClosePreparation(object box)
        {
            if (!ReferenceEquals(preparation, box) || MainGameView.Instance == null) return;
            WindowHostCommands.CloseWindowCommand.Execute(box, MainGameView.Instance);
            preparation = null;
            // Unpausing remains an explicit player action after preparation.
            // Closing a native message box can restore the clock it found;
            // hold the pause the checklist promises.
            if (!GameTime.IsPaused())
            {
                GameTime.Pause(true);
                ContactsFix.Log("World battle: the clock was running after the preparation checklist closed; paused again for the player to start.");
            }
        }

        internal static void End() { opening.Reset(); preparation = null; preparationFailed = false; }
    }
}
