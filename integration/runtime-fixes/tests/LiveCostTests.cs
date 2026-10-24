// Contract stand-ins for the native modal and time controls. No UI code ships.
using System;
using System.Collections.Generic;
using System.Reflection;
using Sest.RuntimeFixes;

namespace Noesis { public class UIElement { } }
namespace UnityEngine
{
    public enum KeyCode { F10,F9 }
    public static class Input
    {
        public static bool Press;
        public static KeyCode Last;
        public static bool GetKeyDown(KeyCode key) { Last=key;bool value=Press;Press=false;return value; }
    }
}
namespace SeaPower
{
    public class GameMain { public bool _initialized=true;void Update() { } }
    public class DelegateCommand
    {
        readonly Action<object> callback;
        public DelegateCommand(Action<object> action) { callback=action; }
        public void Execute(object value) { callback(value); }
    }
    public static class GameTime
    {
        public static float TimeCompression { get; set; }=8;
        public static bool Muted;
        public static void Pause(bool force) { TimeCompression=0;Muted=true; }
        public static void UnPause() { TimeCompression=1;Muted=false; }
    }
    public class MissionPopupData { public string Text; }
    public static class RichMissionMessages
    {
        public static int Created;
        public static MissionPopupData FormatPopupMessageText(string popupString,ObjectBase target)
        { return new MissionPopupData{Text=popupString}; }
        public static SeapowerUI.Modal CreateMissionPopupModal(MissionPopupData messageData,Noesis.UIElement context,
            bool pauseOnLoad,bool stopTimeOnClose,DateTime? navalMessageDateTime,IList<SeapowerUI.RichMissionMessageObjectiveRow> previewObjectives)
        {
            Created++;
            var window=new SeapowerUI.Modal{Text=messageData.Text};
            window.ActionCommand=new DelegateCommand(x=>{window.IsLoaded=false;GameTime.UnPause();});
            return window;
        }
    }
}
namespace SeapowerUI
{
    public class RichMissionMessageObjectiveRow { }
    public class MainGameView : Noesis.UIElement { public static MainGameView Instance=new MainGameView(); }
    public class Modal
    {
        public object ActionCommand { get; set; }
        public bool IsLoaded { get; set; }
        public string Text;
    }
    public class CustomRoutedCommand
    {
        public Modal Last;
        public void Execute(object value,Noesis.UIElement context)
        { Last=(Modal)value;Last.IsLoaded=true;SeaPower.GameTime.Pause(true); }
    }
    public static class WindowHostCommands
    { public static CustomRoutedCommand OpenWindowCommand { get; private set; }=new CustomRoutedCommand(); }
}

static class LiveCostTests
{
    static int checks;
    static void Check(bool value,string label) { checks++;if(!value)throw new Exception("live costs: "+label); }
    static void Show(SeaPower.GameMain main) { UnityEngine.Input.Press=true;LiveCombatCosts.Postfix(main); }
    static void Close() { ((SeaPower.DelegateCommand)SeapowerUI.WindowHostCommands.OpenWindowCommand.Last.ActionCommand).Execute(null); }
    internal static int Run()
    {
        CampaignInventory.Bind(Assembly.GetExecutingAssembly());
        var tf=new SeaPower.Taskforce();SeaPower.Globals._playerTaskforce=tf;SeaPower.Globals._enemyTaskforce=new SeaPower.Taskforce();
        tf._weaponsSpent["round"]=new SeaPower.WeaponsSpent{_number=4};
        tf._unitStatusRegister.Add(new SeaPower.UnitRegister{IniRef="radar",IniFolder="land_units",ObjectType=SeaPower.ObjectBase.ObjectType.LandUnit,Count=1,IsDestroyed=true});
        LiveCombatCosts.Bind(Assembly.GetExecutingAssembly(),"F10");
        var main=new SeaPower.GameMain();
        string text=CampaignCosts.LiveSummary();
        Check(text.Contains("Land $600K"),"land losses appear in standalone live summary");
        Check(text.Contains("Expended $80"),"native expenditure uses selected mode");
        Check(text.Contains("+ ?"),"uncaptured historic magazines remain incomplete");
        int before=SeaPower.RichMissionMessages.Created;
        LiveCombatCosts.Postfix(main);Check(SeaPower.RichMissionMessages.Created==before,"no key leaves UI untouched");
        Show(new SeaPower.GameMain{_initialized=false});Check(SeaPower.RichMissionMessages.Created==before,"no modal before gameplay initialized");
        UnityEngine.Input.Press=false;SeaPower.GameTime.TimeCompression=8;Show(main);
        Check(SeaPower.RichMissionMessages.Created==before+1,"key opens one native modal");
        Check(SeapowerUI.WindowHostCommands.OpenWindowCommand.Last.Text.Contains("SEST COMBAT COSTS|"),"native message format contains costs");
        Check(SeaPower.GameTime.TimeCompression==0 && SeaPower.GameTime.Muted,"native modal pauses the game");
        Show(main);Check(SeaPower.RichMissionMessages.Created==before+1,"repeated key does not stack popups");
        Close();Check(SeaPower.GameTime.TimeCompression==8 && !SeaPower.GameTime.Muted,"close restores prior compression and audio");
        SeaPower.GameTime.Pause(true);Show(main);Close();
        Check(SeaPower.GameTime.TimeCompression==0 && SeaPower.GameTime.Muted,"already paused remains paused");
        SeaPower.GameTime.TimeCompression=16;Show(main);SeapowerUI.MainGameView.Instance=new SeapowerUI.MainGameView();Close();
        Check(SeaPower.GameTime.TimeCompression==1,"changed game context is not overwritten with old compression");
        LiveCombatCosts.Bind(Assembly.GetExecutingAssembly(),"f9");Show(main);Check(UnityEngine.Input.Last==UnityEngine.KeyCode.F9,"hotkey configurable without changing F11");Close();
        bool rejected=false;try{LiveCombatCosts.Bind(Assembly.GetExecutingAssembly(),"invalid");}catch(ArgumentException){rejected=true;}
        before=SeaPower.RichMissionMessages.Created;Show(main);Check(rejected && SeaPower.RichMissionMessages.Created==before,"invalid config fails closed");
        return checks;
    }
}
