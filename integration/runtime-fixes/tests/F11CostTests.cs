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
        public static string Click;public static bool Throw;public static int Backgrounds;
        public static void Label(Rect r,string text,GUIStyle s){if(Throw)throw new Exception("mock GUI error");Labels.Add(text);}
        public static bool Button(Rect r,string text,GUIStyle s){Buttons.Add(text);if(Click==text){Click=null;return true;}return false;}
        public static void DrawTexture(Rect r,Texture t){Backgrounds++;}
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
    static void Set(string field,object value){typeof(F11CombatCosts).GetField(field,BindingFlags.Static|BindingFlags.NonPublic).SetValue(null,value);}
    static F11CombatCosts.Frame Start(WeaponCostsMod.Overlay owner)
    {F11CombatCosts.Frame state;Check(F11CombatCosts.BeforeGUI(owner,out state),"live original OnGUI retained");return state;}
    static void End(F11CombatCosts.Frame state){F11CombatCosts.AfterGUI(state);F11CombatCosts.FinallyGUI(null,state);}
    internal static int Run()
    {
        string path=Path.Combine(Path.GetTempPath(),"sest-f11-test-"+Guid.NewGuid().ToString("N")+".txt");
        try
        {
            CampaignCosts.BindMenu(Assembly.GetExecutingAssembly());CombatHistory.Open(path);
            F11CombatCosts.Bind(Assembly.GetExecutingAssembly());var owner=new WeaponCostsMod.Overlay();UnityEngine.GUI.Reset();
            F11CombatCosts.AfterUpdate(owner);var frame=Start(owner);
            Check(F11CombatCosts.BeforeToolbar(),"native controls retained on mission tab");
            string description="Original";F11CombatCosts.Description(ref description);
            Check(description=="Original\n\n","header reserves tab space only inside overlay");
            float height=20;F11CombatCosts.LineHeight(ref height);Check(height==20,"mission row sizes unchanged");
            Check(F11CombatCosts.Comparison(owner,0,0,0,100)&&F11CombatCosts.Faction(),"original mission cost rows retained");
            float nativeSide=80;F11CombatCosts.SideHeight(ref nativeSide);Check(nativeSide==80,"native side height retained on mission tab");
            F11CombatCosts.AfterToolbar(owner,0,0,640);
            Check(UnityEngine.GUI.Buttons.Contains("Cumulative Combat Costs")&&UnityEngine.GUI.Buttons.Contains("Last games"),"both requested tabs inside original panel");
            End(frame);description="Original";F11CombatCosts.Description(ref description);Check(description=="Original","no sticky description change outside panel");
            frame=Start(owner);UnityEngine.GUI.Click="Cumulative Combat Costs";F11CombatCosts.AfterToolbar(owner,0,0,640);End(frame);
            frame=Start(owner);Check(!F11CombatCosts.BeforeToolbar(),"currency conversion toolbar not misapplied to own USD values");
            height=20;F11CombatCosts.LineHeight(ref height);Check(height==450,"custom body uses fixed readable height");
            F11CombatCosts.LineHeight(ref height);Check(height==0,"native extra rows do not shrink the custom view");
            float sideHeight=900;F11CombatCosts.SideHeight(ref sideHeight);Check(sideHeight==0,"hidden ally/neutral native rows do not shrink custom view");
            Check(!F11CombatCosts.Comparison(owner,12,378,278,100)&&!F11CombatCosts.Faction(),"custom totals replace native rows only on selected tab");
            Check(UnityEngine.GUI.Labels.Contains("Cumulative Combat Costs")&&UnityEngine.GUI.Labels.Any(x=>x.Contains("Land $600K")),"saved full material totals displayed in F11");
            Check(UnityEngine.GUI.Buttons.Contains("Current mission detail"),"complete live breakdown remains accessible in same F11");
            End(frame);
            Set("selected",2);frame=Start(owner);F11CombatCosts.Comparison(owner,12,378,278,100);End(frame);
            Check(UnityEngine.GUI.Labels.Contains("Last games")&&UnityEngine.GUI.Buttons.Any(x=>x.Contains("Old mission")),"earlier native debriefs available as last games");
            string pick=UnityEngine.GUI.Buttons.Last(x=>x.Contains("Old mission"));UnityEngine.GUI.Click=pick;
            frame=Start(owner);F11CombatCosts.Comparison(owner,12,378,278,100);End(frame);
            frame=Start(owner);F11CombatCosts.Comparison(owner,12,378,278,100);End(frame);
            Check(UnityEngine.GUI.Buttons.Contains("Back to games"),"history record opens drill-down");

            owner.missionActive=false;owner.mission=null;UnityEngine.Input.Press=false;F11CombatCosts.AfterUpdate(owner);UnityEngine.GUI.Reset();
            F11CombatCosts.Frame menuState;
            Check(!F11CombatCosts.BeforeGUI(owner,out menuState)&&UnityEngine.GUI.Labels.Count==0,"menu starts closed without altering original visibility");
            UnityEngine.Input.Press=true;F11CombatCosts.AfterUpdate(owner);UnityEngine.Input.Press=false;
            Check(!F11CombatCosts.BeforeGUI(owner,out menuState),"F11 draws inside original component between missions");
            Check(UnityEngine.GUI.Labels.Contains("Task Force menu")&&UnityEngine.GUI.Labels.Contains("Cumulative Combat Costs"),"Task Force menu opens cumulative view");
            Check(UnityEngine.GUI.matrix.Scale==1 && UnityEngine.GUI.depth==8 && UnityEngine.GUI.color.a==1,"GUI state restored after menu rendering");
            UnityEngine.Input.Press=true;UnityEngine.Input.Modifier=true;F11CombatCosts.AfterUpdate(owner);UnityEngine.GUI.Reset();F11CombatCosts.BeforeGUI(owner,out menuState);
            Check(UnityEngine.GUI.Labels.Count>0,"modified F11 ignored consistently with tracker");
            UnityEngine.Input.Press=true;F11CombatCosts.AfterUpdate(owner);UnityEngine.GUI.Reset();F11CombatCosts.BeforeGUI(owner,out menuState);
            Check(UnityEngine.GUI.Labels.Count==0,"second F11 hides menu view");
            SeapowerUI.ViewModels.LinearCampaignTaskForceModeRules.TaskForce=false;
            UnityEngine.Input.Press=true;F11CombatCosts.AfterUpdate(owner);UnityEngine.GUI.Reset();F11CombatCosts.BeforeGUI(owner,out menuState);
            Check(UnityEngine.GUI.Labels.Count==0,"no unrelated main-menu popups");SeapowerUI.ViewModels.LinearCampaignTaskForceModeRules.TaskForce=true;
            owner.missionActive=true;owner.visible=false;UnityEngine.GUI.Reset();F11CombatCosts.BeforeGUI(owner,out menuState);
            Check(menuState==null&&UnityEngine.GUI.Labels.Count==0,"hidden native overlay stays hidden in mission");
            owner.visible=true;frame=Start(owner);var original=new Exception("native error");
            Check(Object.ReferenceEquals(F11CombatCosts.FinallyGUI(original,frame),original),"finalizer preserves original exception");
            description="Original";F11CombatCosts.Description(ref description);Check(description=="Original","exception clears extension frame");
            UnityEngine.GUI.Throw=true;bool failed=false;try{CostGUI.Panel(14,10,1,.8f,(x,y)=>CostGUI.Label(x,y,10,10,"fail",owner.label));}catch(TargetInvocationException){failed=true;}
            Check(failed&&UnityEngine.GUI.matrix.Scale==1&&UnityEngine.GUI.depth==8&&UnityEngine.GUI.color.a==1,"GUI state restored even on drawing failure");
            UnityEngine.GUI.Throw=false;F11CombatCosts.BeforeDestroy();Check(File.Exists(path),"teardown persists final observed session");
        }
        finally{if(File.Exists(path))File.Delete(path);}
        return checks;
    }
}
