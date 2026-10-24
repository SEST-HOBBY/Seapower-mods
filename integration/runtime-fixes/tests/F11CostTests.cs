// UI contract stand-ins. Tests drive SEST's real callbacks; no Unity/game code.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using Sest.RuntimeFixes;

namespace UnityEngine
{
    public enum KeyCode{F11,LeftControl,RightControl,LeftAlt,RightAlt,LeftShift,RightShift}
    public static class Input
    {
        public static bool Press,Modifier;
        public static bool GetKeyDown(KeyCode key){return key==KeyCode.F11&&Press;}
        public static bool GetKey(KeyCode key){return Modifier;}
    }
    public struct Rect { public float x,y,width,height;public Rect(float a,float b,float c,float d){x=a;y=b;width=c;height=d;} }
    public struct Color
    {public float r,g,b,a;public Color(float x,float y,float z,float w){r=x;g=y;b=z;a=w;}public static Color white{get{return new Color(1,1,1,1);}}}
    public struct Quaternion{public static Quaternion identity{get{return new Quaternion();}}}
    public struct Matrix4x4{public float Scale;public static Matrix4x4 TRS(Vector3 p,Quaternion q,Vector3 s){return new Matrix4x4{Scale=s.x};}}
    public class Texture{ }
    public class Texture2D:Texture{public static Texture2D whiteTexture{get;}=new Texture2D();}
    public class GUIContent{public string text;public GUIContent(string value){text=value;}}
    public class GUIStyle{public float CalcHeight(GUIContent c,float width){return (c.text.Count(x=>x=='\n')+1)*14;}}
    public class GUISkin{public GUIStyle button{get;}=new GUIStyle();}
    public static class Screen{public static int width{get;set;}=1920;public static int height{get;set;}=1080;}
    public static class GUI
    {
        public static Matrix4x4 matrix{get;set;}=new Matrix4x4{Scale=1};public static Color color{get;set;}=Color.white;
        public static int depth{get;set;}=8;public static GUISkin skin{get;}=new GUISkin();
        public static readonly List<string> Labels=new List<string>(),Buttons=new List<string>();
        public static string Click;public static bool Throw;public static int Backgrounds;public static Rect LastPanel;
        public static void Label(Rect r,string text,GUIStyle s){if(Throw)throw new Exception("mock GUI error");Labels.Add(text);}
        public static bool Button(Rect r,string text,GUIStyle s){Buttons.Add(text);if(Click==text){Click=null;return true;}return false;}
        public static void DrawTexture(Rect r,Texture t){Backgrounds++;LastPanel=r;}
        public static void Reset(){Labels.Clear();Buttons.Clear();Click=null;Throw=false;Backgrounds=0;Input.Press=false;Input.Modifier=false;}
    }
}
namespace SeaPower
{
    public class GameMain{void Update(){}void OnDestroy(){}}
    public static partial class Globals{public static string currentMissionFilePath="missions/Test mission.ini";}
    public partial class IniHandler{public string FilePath="test.ini";public string getFilePath(){return FilePath;}}
}
namespace SeapowerUI.ViewModels
{
    public static partial class LinearCampaignTaskForceModeRules
    {public static bool TaskForce=true;public static SeaPower.IniHandler OpenCampaignIni(){return State;}public static bool IsTaskForceModeEnabled(SeaPower.IniHandler ini){return TaskForce;}}
}
namespace WeaponCostsMod
{
    public class DisplayValues{public string Description{get{return "Original currency and basis description";}}}
    public class Overlay
    {
        public bool ready=true,visible=true,missionActive=true;public object mission=new object();
        public float top=14,right=10,scale=1,opacity=.8f;
        public UnityEngine.GUIStyle label=new UnityEngine.GUIStyle(),title=new UnityEngine.GUIStyle(),muted=new UnityEngine.GUIStyle(),buttonStyle=new UnityEngine.GUIStyle();
        public string popup="old";public UnityEngine.KeyCode toggle=UnityEngine.KeyCode.F11;public DisplayValues display=new DisplayValues();
        public void Styles(){}
    }
}

static class F11CostTests
{
    static int checks;
    static void Check(bool value,string label){checks++;if(!value)throw new Exception("F11: "+label);}
    static bool Draw(WeaponCostsMod.Overlay owner){UnityEngine.GUI.Reset();return F11CombatCosts.BeforeGUI(owner);}
    static void Press(WeaponCostsMod.Overlay owner,bool modifier=false)
    {UnityEngine.Input.Press=true;UnityEngine.Input.Modifier=modifier;F11CombatCosts.AfterUpdate(owner);UnityEngine.Input.Press=false;UnityEngine.Input.Modifier=false;}
    internal static int Run()
    {
        string path=Path.Combine(Path.GetTempPath(),"sest-f11-test-"+Guid.NewGuid().ToString("N")+".txt");
        try
        {
            CampaignCosts.BindMenu(Assembly.GetExecutingAssembly());CombatHistory.Open(path);
            F11CombatCosts.Bind(Assembly.GetExecutingAssembly());var owner=new WeaponCostsMod.Overlay();
            F11CombatCosts.AfterUpdate(owner);
            Check(Draw(owner)&&UnityEngine.GUI.Labels.Count==0&&UnityEngine.GUI.Buttons.Count==0,"in a mission F11 is the tracker's own panel, untouched");
            Press(owner);
            Check(Draw(owner)&&UnityEngine.GUI.Labels.Count==0,"F11 in a mission never opens SEST's panel");
            Check(owner.popup=="old"&&owner.visible,"tracker state untouched in a mission");

            owner.missionActive=false;owner.mission=null;F11CombatCosts.AfterUpdate(owner);
            Check(!Draw(owner)&&UnityEngine.GUI.Labels.Count==0,"Task Force menu panel starts closed");
            Press(owner);
            Check(!Draw(owner)&&UnityEngine.GUI.Labels.Contains("COMBAT COSTS / CAMPAIGN"),"F11 in the Task Force menu opens the campaign panel");
            Check(UnityEngine.GUI.Labels.Any(x=>x.StartsWith("Player total"))&&UnityEngine.GUI.Labels.Any(x=>x.Contains("Land $600K")),"campaign totals with land losses shown");
            Check(UnityEngine.GUI.Labels.Any(x=>x.StartsWith("1. Old mission"))&&UnityEngine.GUI.Labels.Any(x=>x.StartsWith("2. ")),"one line per completed mission");
            Check(UnityEngine.GUI.Buttons.Count==0&&UnityEngine.GUI.Backgrounds==1,"information only: one panel, no buttons or tabs");
            var panel=UnityEngine.GUI.LastPanel;
            Check(panel.x==10&&Math.Abs(panel.y+panel.height/2-540)<1&&panel.y>0,"panel at the middle of the left edge, clear of the mission information on the right");
            Check(UnityEngine.GUI.matrix.Scale==1&&UnityEngine.GUI.depth==8&&UnityEngine.GUI.color.a==1,"GUI state restored after drawing");
            Press(owner,true);Draw(owner);
            Check(UnityEngine.GUI.Labels.Count>0,"modified F11 ignored, as the tracker does");
            Press(owner);Draw(owner);
            Check(UnityEngine.GUI.Labels.Count==0,"second F11 closes the panel");
            Press(owner);owner.missionActive=true;F11CombatCosts.AfterUpdate(owner);owner.missionActive=false;F11CombatCosts.AfterUpdate(owner);Draw(owner);
            Check(UnityEngine.GUI.Labels.Count==0,"starting a mission closes the panel");
            SeapowerUI.ViewModels.LinearCampaignTaskForceModeRules.TaskForce=false;
            Press(owner);Draw(owner);
            Check(UnityEngine.GUI.Labels.Count==0,"no panel outside a Task Force campaign");
            SeapowerUI.ViewModels.LinearCampaignTaskForceModeRules.TaskForce=true;
            UnityEngine.GUI.Throw=true;bool failed=false;
            try{CostGUI.Panel(1,.8f,200,(x,y)=>CostGUI.Label(x,y,10,10,"fail",owner.label));}catch(TargetInvocationException){failed=true;}
            Check(failed&&UnityEngine.GUI.matrix.Scale==1&&UnityEngine.GUI.depth==8&&UnityEngine.GUI.color.a==1,"GUI state restored even on drawing failure");
            UnityEngine.GUI.Throw=false;F11CombatCosts.BeforeDestroy();Check(File.Exists(path),"teardown persists final observed session");
        }
        finally{if(File.Exists(path))File.Delete(path);}
        return checks;
    }
}
