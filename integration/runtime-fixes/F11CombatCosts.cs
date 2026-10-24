using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Security.Cryptography;

namespace Sest.RuntimeFixes
{
    // F11 in a mission stays the author's own Combat Cost Tracker panel. In the
    // Task Force menu, where the tracker draws nothing, F11 shows the completed
    // campaign's totals. Information only: no tabs or buttons. No tracker DLL
    // ships here and nothing in a mission is redrawn.
    internal static class F11CombatCosts
    {
        const string TrackerHash="74afa9028fc0c52b93f415263504f51ecf8d056a624feaebcc8053ba5a1c0ac3";
        const int Listed=10;
        static bool attached,stopped,menuShown,wasLive;
        static double nextAttach,nextCapture,nextLines;
        static FieldInfo ready,missionActive,mission,scale,opacity,label,title,muted,toggle,missionPath;
        static MethodInfo styles,keyDown,getKey;
        static string[] lines=new string[0];
        static double Now { get { return (double)Stopwatch.GetTimestamp()/Stopwatch.Frequency; } }
        static FieldInfo Field(Type type,string name,Type expected=null)
        {
            var f=type.GetField(name,Api.All);
            if(f==null||(expected!=null&&f.FieldType!=expected))throw new MissingFieldException(type.FullName,name);
            return f;
        }
        internal static void Install(Assembly native,string historyPath)
        {
            CampaignCosts.BindMenu(native);CombatHistory.Open(historyPath);
            missionPath=Field(Api.Type(native,"SeaPower.Globals"),"currentMissionFilePath",typeof(string));
            var update=Api.Method(Api.Type(native,"SeaPower.GameMain"),"Update",typeof(void));
            var destroy=Api.Method(Api.Type(native,"SeaPower.GameMain"),"OnDestroy",typeof(void));
            try
            {
                Api.Postfix(update,typeof(F11CombatCosts),"Poll","io.github.sest-hobby.f11-cost-bootstrap");
                Api.Hooks(destroy,typeof(F11CombatCosts),"BeforeDestroy",null,"io.github.sest-hobby.f11-cost-bootstrap");
                // Anchor Chain can load SEST before the tracker. Attach as
                // soon as that assembly arrives, even before a first mission.
                AppDomain.CurrentDomain.AssemblyLoad+=TrackerLoaded;
            }
            catch{stopped=true;throw;}
            Api.Log("F11 campaign panel awaiting the enabled Combat Cost Tracker");
            Poll();
        }
        static void TrackerLoaded(object sender,AssemblyLoadEventArgs args)
        {
            if(attached||stopped)return;
            try
            {
                if(args.LoadedAssembly.GetType("WeaponCostsMod.Overlay",false)==null)return;
                nextAttach=0;Poll();
            }
            catch(Exception e){stopped=true;Api.LogFailure("deferred F11 attachment unavailable",e);}
        }
        internal static void Poll()
        {
            if(attached||stopped||Now<nextAttach)return;nextAttach=Now+1;
            foreach(var assembly in AppDomain.CurrentDomain.GetAssemblies())
            {
                if(assembly.GetType("WeaponCostsMod.Overlay",false)==null)continue;
                try
                {
                    string digest;
                    using(var stream=File.OpenRead(assembly.Location))using(var sha=SHA256.Create())
                        digest=BitConverter.ToString(sha.ComputeHash(stream)).Replace("-","").ToLowerInvariant();
                    if(digest!=TrackerHash){stopped=true;Api.Log("F11 campaign totals inactive: uninspected Combat Cost Tracker "+digest);return;}
                    Bind(assembly);
                    Type overlay=Api.Type(assembly,"WeaponCostsMod.Overlay");
                    const string owner="io.github.sest-hobby.cumulative-combat-costs";
                    Api.Postfix(Api.Method(overlay,"Update",typeof(void)),typeof(F11CombatCosts),"AfterUpdate",owner);
                    Api.Hooks(Api.Method(overlay,"OnGUI",typeof(void)),typeof(F11CombatCosts),"BeforeGUI",null,owner);
                    Api.Log("F11 campaign combat costs installed: Task Force menu totals; the mission panel is the tracker's own");
                }
                catch(Exception e){stopped=true;attached=false;Api.LogFailure("F11 campaign totals not installed; original tracker retained",e);}
                return;
            }
        }
        internal static void BeforeDestroy()
        {
            if(CombatHistory.CurrentId==null)return;
            try{CombatHistory.Refresh(CampaignCosts.CaptureLive("Game"));}
            catch(Exception e){Api.LogFailure("final game cost refresh unavailable",e);}
            CombatHistory.Finish();
        }
        // The test binder uses contract stand-ins. Production reaches this
        // only after the exact captured tracker hash is accepted above.
        internal static void Bind(Assembly tracker)
        {
            var type=Api.Type(tracker,"WeaponCostsMod.Overlay");
            ready=Field(type,"ready",typeof(bool));missionActive=Field(type,"missionActive",typeof(bool));mission=Field(type,"mission");
            scale=Field(type,"scale",typeof(float));opacity=Field(type,"opacity",typeof(float));
            label=Field(type,"label");title=Field(type,"title");muted=Field(type,"muted");toggle=Field(type,"toggle");
            styles=Api.Method(type,"Styles",typeof(void));
            var input=Api.FindType("UnityEngine.Input");var code=Api.FindType("UnityEngine.KeyCode");
            keyDown=Api.Method(input,"GetKeyDown",typeof(bool),code);getKey=Api.Method(input,"GetKey",typeof(bool),code);
            CostGUI.Bind();attached=true;stopped=false;menuShown=false;wasLive=false;nextLines=nextCapture=0;lines=new string[0];
        }
        static bool Modified()
        {
            var code=Api.FindType("UnityEngine.KeyCode");
            foreach(string name in new[]{"LeftControl","RightControl","LeftAlt","RightAlt","LeftShift","RightShift"})
                if((bool)getKey.Invoke(null,new[]{Enum.Parse(code,name)}))return true;
            return false;
        }
        internal static void AfterUpdate(object __instance)
        {
            if(!attached||stopped||!(bool)ready.GetValue(__instance))return;
            try
            {
                bool live=(bool)missionActive.GetValue(__instance);
                if(live!=wasLive){menuShown=false;wasLive=live;}
                if(!live&&CampaignCosts.TaskForceMenuAvailable()&&!Modified()&&(bool)keyDown.Invoke(null,new[]{toggle.GetValue(__instance)}))
                {menuShown=!menuShown;nextLines=0;}
                if(Now>=nextCapture)
                {
                    nextCapture=Now+0.5;
                    string path=missionPath==null?null:(string)missionPath.GetValue(null);
                    string name=String.IsNullOrWhiteSpace(path)?"Game":Path.GetFileNameWithoutExtension(path);
                    if(name.Length>256)name=name.Substring(0,256);
                    CombatHistory.Observe(live?mission.GetValue(__instance):null,live?CampaignCosts.CaptureLive(name):null);
                }
            }
            catch(Exception e){Api.LogFailure("one F11 history update unavailable",e);}
        }
        internal static bool BeforeGUI(object __instance)
        {
            if(!attached||stopped||!(bool)ready.GetValue(__instance)||(bool)missionActive.GetValue(__instance))return true;
            try
            {
                if(menuShown&&CampaignCosts.TaskForceMenuAvailable())DrawMenu(__instance);
                return false; // original draws nothing outside a mission
            }
            catch(Exception e){stopped=true;Api.LogFailure("F11 campaign totals disabled; original tracker retained",e);return true;}
        }
        static void DrawMenu(object owner)
        {
            styles.Invoke(owner,null);
            if(Now>=nextLines){lines=CampaignCosts.CampaignLines(CampaignCosts.SavedGames(),Listed);nextLines=Now+2;}
            object face=label.GetValue(owner),note=muted.GetValue(owner) ?? face;
            CostGUI.Panel((float)scale.GetValue(owner),(float)opacity.GetValue(owner),62+lines.Length*21,(x,y)=>{
                CostGUI.Label(x+12,y+6,616,24,"COMBAT COSTS / CAMPAIGN",title.GetValue(owner));
                CostGUI.Label(x+12,y+30,616,22,"Completed missions in this campaign. F11 closes.",note);
                y+=56;
                foreach(string line in lines)
                {CostGUI.Label(x+12,y,616,22,line,line.StartsWith("+ ?")||line.StartsWith("Crew")?note:face);y+=21;}
            });
        }
    }

    internal static class CostGUI
    {
        static ConstructorInfo rectangle,colour,vector;
        static MethodInfo label,drawTexture,trs;
        static PropertyInfo matrix,color,depth,screenWidth,screenHeight,white,whiteTexture,identity;
        internal static void Bind()
        {
            var gui=Api.FindType("UnityEngine.GUI");var rect=Api.FindType("UnityEngine.Rect");var style=Api.FindType("UnityEngine.GUIStyle");var texture=Api.FindType("UnityEngine.Texture");
            var rgba=Api.FindType("UnityEngine.Color");var vec=Api.FindType("UnityEngine.Vector3");var quat=Api.FindType("UnityEngine.Quaternion");var mat=Api.FindType("UnityEngine.Matrix4x4");
            rectangle=rect.GetConstructor(new[]{typeof(float),typeof(float),typeof(float),typeof(float)});
            colour=rgba.GetConstructor(new[]{typeof(float),typeof(float),typeof(float),typeof(float)});vector=vec.GetConstructor(new[]{typeof(float),typeof(float),typeof(float)});
            label=Api.Method(gui,"Label",typeof(void),rect,typeof(string),style);drawTexture=Api.Method(gui,"DrawTexture",typeof(void),rect,texture);
            matrix=gui.GetProperty("matrix",Api.All);color=gui.GetProperty("color",Api.All);depth=gui.GetProperty("depth",Api.All);
            var screen=Api.FindType("UnityEngine.Screen");screenWidth=screen.GetProperty("width",Api.All);screenHeight=screen.GetProperty("height",Api.All);
            white=rgba.GetProperty("white",Api.All);whiteTexture=Api.FindType("UnityEngine.Texture2D").GetProperty("whiteTexture",Api.All);identity=quat.GetProperty("identity",Api.All);
            trs=Api.Method(mat,"TRS",mat,vec,quat,vec);
            if(rectangle==null||colour==null||vector==null||matrix==null||color==null||depth==null||screenWidth==null||screenHeight==null||white==null||whiteTexture==null||identity==null)throw new MissingMemberException("Unity cost overlay GUI API");
        }
        static object Rect(float x,float y,float w,float h){return rectangle.Invoke(new object[]{x,y,w,h});}
        internal static void Label(float x,float y,float w,float h,string text,object face){label.Invoke(null,new[]{Rect(x,y,w,h),text,face});}
        // Middle of the left edge: the Task Force menu's mission information
        // fills the right side, where the tracker's own panel sits.
        internal static void Panel(float requestedScale,float alpha,float requestedHeight,Action<float,float> draw)
        {
            object oldMatrix=matrix.GetValue(null,null),oldColor=color.GetValue(null,null),oldDepth=depth.GetValue(null,null);
            try
            {
                float width=(int)screenWidth.GetValue(null,null),height=(int)screenHeight.GetValue(null,null),tall=Math.Min(640,requestedHeight);
                float zoom=Math.Max(0.25f,Math.Min(requestedScale,Math.Min((width-12)/652f,(height-12)/(tall+12))));
                matrix.SetValue(null,trs.Invoke(null,new[]{vector.Invoke(new object[]{0f,0f,0f}),identity.GetValue(null,null),vector.Invoke(new object[]{zoom,zoom,1f})}),null);
                depth.SetValue(null,-50,null);float x=10,y=Math.Max(0,(height/zoom-tall)/2);
                color.SetValue(null,colour.Invoke(new object[]{0.035f,0.055f,0.075f,alpha}),null);
                drawTexture.Invoke(null,new[]{Rect(x,y,640,tall),whiteTexture.GetValue(null,null)});color.SetValue(null,white.GetValue(null,null),null);
                draw(x,y);
            }
            finally{matrix.SetValue(null,oldMatrix,null);color.SetValue(null,oldColor,null);depth.SetValue(null,oldDepth,null);}
        }
    }
}
