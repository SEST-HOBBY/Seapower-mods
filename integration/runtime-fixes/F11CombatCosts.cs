using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;

namespace Sest.RuntimeFixes
{
    // Adds views to the existing CombatCosts overlay. The author's data,
    // recording and Mission view remain its own. No tracker DLL ships here.
    internal static class F11CombatCosts
    {
        const string TrackerHash="74afa9028fc0c52b93f415263504f51ecf8d056a624feaebcc8053ba5a1c0ac3";
        static Assembly game;
        static bool attached,stopped,menuShown,wasLive;
        static double nextAttach,nextCapture,nextData;
        static FieldInfo ready,visible,missionActive,mission,top,right,scale,opacity,label,title,muted,button,popup,toggle,missionPath;
        static MethodInfo styles,keyDown,getKey;
        static int selected=0,scope=0,page;
        static string selectedGame;
        static List<CombatGameRecord> campaign=new List<CombatGameRecord>(),past=new List<CombatGameRecord>();
        static string[] body=new string[0];
        static string dataView;
        [ThreadStatic]static Frame frame;
        internal sealed class Frame
        {
            internal object Owner;
            internal int Tab;
            internal bool Extra,Native;
            internal Frame Previous;
        }
        static double Now { get { return (double)Stopwatch.GetTimestamp()/Stopwatch.Frequency; } }
        static FieldInfo Field(Type type,string name,Type expected=null)
        {
            var f=type.GetField(name,Api.All);
            if(f==null||(expected!=null&&f.FieldType!=expected))throw new MissingFieldException(type.FullName,name);
            return f;
        }
        internal static void Install(Assembly native,string historyPath)
        {
            game=native;CampaignCosts.BindMenu(game);CombatHistory.Open(historyPath);
            missionPath=Field(Api.Type(game,"SeaPower.Globals"),"currentMissionFilePath",typeof(string));
            var update=Api.Method(Api.Type(game,"SeaPower.GameMain"),"Update",typeof(void));
            var destroy=Api.Method(Api.Type(game,"SeaPower.GameMain"),"OnDestroy",typeof(void));
            try
            {
                Api.Postfix(update,typeof(F11CombatCosts),"Poll","io.github.sest-hobby.f11-cost-bootstrap");
                Api.Hooks(destroy,typeof(F11CombatCosts),"BeforeDestroy",null,"io.github.sest-hobby.f11-cost-bootstrap");
                // Anchor Chain can load SEST before the tracker. Attach as
                // soon as that assembly arrives, even before a first mission.
                AppDomain.CurrentDomain.AssemblyLoad+=TrackerLoaded;
            }
            catch{stopped=true;throw;}
            Api.Log("cumulative combat costs awaiting the enabled Combat Cost Tracker; F10 viewer retired");
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
                    if(digest!=TrackerHash){stopped=true;Api.Log("F11 extension inactive: uninspected Combat Cost Tracker "+digest);return;}
                    Bind(assembly);
                    Type overlay=Api.Type(assembly,"WeaponCostsMod.Overlay"),display=Api.Type(assembly,"WeaponCostsMod.DisplayValues");
                    const string owner="io.github.sest-hobby.cumulative-combat-costs";
                    Api.Postfix(Api.Method(overlay,"Update",typeof(void)),typeof(F11CombatCosts),"AfterUpdate",owner);
                    Api.Hooks(Api.Method(overlay,"OnGUI",typeof(void)),typeof(F11CombatCosts),"BeforeGUI","AfterGUI",owner,"FinallyGUI");
                    Api.Hooks(Api.Method(overlay,"Toolbar",typeof(void),typeof(float),typeof(float),typeof(float)),typeof(F11CombatCosts),"BeforeToolbar","AfterToolbar",owner);
                    Api.Postfix(Api.Method(display,"get_Description",typeof(string)),typeof(F11CombatCosts),"Description",owner);
                    Api.Postfix(Api.Method(overlay,"ContentHeight",typeof(float),typeof(List<>).MakeGenericType(Api.Type(assembly,"WeaponCostsMod.OverlayLine"))),typeof(F11CombatCosts),"SideHeight",owner);
                    Api.Postfix(Api.Method(overlay,"<OnGUI>b__24",typeof(float),Api.Type(assembly,"WeaponCostsMod.ComparisonLine")),typeof(F11CombatCosts),"LineHeight",owner);
                    Api.Hooks(Api.Method(overlay,"DrawComparison",typeof(void),typeof(float),typeof(float),typeof(float),typeof(float),typeof(List<>).MakeGenericType(Api.Type(assembly,"WeaponCostsMod.ComparisonLine"))),typeof(F11CombatCosts),"Comparison",null,owner);
                    Api.Hooks(Api.Method(overlay,"DrawFaction",typeof(void),typeof(float),typeof(float),typeof(string),typeof(List<>).MakeGenericType(Api.Type(assembly,"WeaponCostsMod.OverlayLine")),typeof(float)),typeof(F11CombatCosts),"Faction",null,owner);
                    Api.Log("Cumulative Combat Costs and Last games embedded in original F11; Task Force menu access installed");
                }
                catch(Exception e){stopped=true;attached=false;Api.LogFailure("F11 extension not installed; original tracker retained",e);}
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
            ready=Field(type,"ready",typeof(bool));visible=Field(type,"visible",typeof(bool));
            missionActive=Field(type,"missionActive",typeof(bool));mission=Field(type,"mission");
            top=Field(type,"top",typeof(float));right=Field(type,"right",typeof(float));scale=Field(type,"scale",typeof(float));opacity=Field(type,"opacity",typeof(float));
            label=Field(type,"label");title=Field(type,"title");muted=Field(type,"muted");button=Field(type,"buttonStyle");popup=Field(type,"popup",typeof(string));toggle=Field(type,"toggle");
            styles=Api.Method(type,"Styles",typeof(void));
            var input=Api.FindType("UnityEngine.Input");var code=Api.FindType("UnityEngine.KeyCode");
            keyDown=Api.Method(input,"GetKeyDown",typeof(bool),code);getKey=Api.Method(input,"GetKey",typeof(bool),code);
            CostGUI.Bind();attached=true;stopped=false;menuShown=false;wasLive=false;selected=0;scope=0;page=0;selectedGame=null;nextData=nextCapture=0;
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
                if(live!=wasLive)
                {selected=live?0:1;if(!live)scope=0;menuShown=false;selectedGame=null;page=0;nextData=0;wasLive=live;}
                if(!live&&CampaignCosts.TaskForceMenuAvailable()&&!Modified()&&(bool)keyDown.Invoke(null,new[]{toggle.GetValue(__instance)}))menuShown=!menuShown;
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
        internal static bool BeforeGUI(object __instance,out Frame __state)
        {
            __state=null;if(!attached||stopped||!(bool)ready.GetValue(__instance))return true;
            try
            {
                bool live=(bool)missionActive.GetValue(__instance);
                if(!live)
                {
                    if(menuShown&&CampaignCosts.TaskForceMenuAvailable())DrawMenu(__instance);
                    return false; // original draws nothing outside a mission
                }
                if(!(bool)visible.GetValue(__instance))return true;
                __state=new Frame{Owner=__instance,Tab=selected,Native=true,Previous=frame};frame=__state;
                return true;
            }
            catch(Exception e){Fail(e);return true;}
        }
        internal static void AfterGUI(Frame __state)
        {if(__state!=null)frame=__state.Previous;}
        internal static Exception FinallyGUI(Exception __exception,Frame __state)
        {AfterGUI(__state);return __exception;}
        static void Fail(Exception e)
        {stopped=true;frame=null;Api.LogFailure("F11 extension disabled; original tracker retained",e);}
        internal static bool BeforeToolbar()
        {return frame==null||frame.Tab==0;}
        internal static void Description(ref string __result)
        {
            if(frame==null)return;
            string text=frame.Tab==0?__result:"USD estimates. Saved quantities are repriced with the configured price basis.";
            __result=text+"\n\n";
        }
        internal static void LineHeight(ref float __result)
        {
            if(frame!=null&&frame.Tab!=0){__result=frame.Extra?0:450;frame.Extra=true;}
        }
        internal static void SideHeight(ref float __result)
        {if(frame!=null&&frame.Tab!=0)__result=0;}
        internal static void AfterToolbar(object __instance,float __0,float __1,float __2)
        {
            if(frame==null)return;
            try
            {
                // Native description starts at y+27. Reserve two blank
                // lines below it and put the tabs inside that same panel.
                string description=frame.Tab==0?CostGUI.NativeDescription(__instance):"USD estimates. Saved quantities are repriced with the configured price basis.";
                float height=CostGUI.Height(description,muted.GetValue(__instance),476);
                Tabs(__instance,__0+12,__1+27+Math.Max(22,height),true);
            }
            catch(Exception e){Fail(e);}
        }
        internal static bool Comparison(object __instance,float __0,float __1,float __2,float __3)
        {
            if(frame==null||frame.Tab==0)return true;
            try{DrawBody(__instance,__0,__3+6,frame.Tab);}catch(Exception e){Fail(e);}
            return false;
        }
        internal static bool Faction(){return frame==null||frame.Tab==0;}
        static object ButtonStyle(object owner)
        {return button.GetValue(owner) ?? CostGUI.DefaultButton();}
        static void Tabs(object owner,float x,float y,bool live)
        {
            var style=ButtonStyle(owner);
            string[] names={live?"This mission":"This mission (in game)","Cumulative Combat Costs","Last games"};
            float[] widths={156,272,176};float at=x;
            for(int i=0;i<3;i++)
            {
                if(CostGUI.Button(at,y,widths[i]-4,24,names[i],style)&&(live||i!=0))
                {selected=i;selectedGame=null;page=0;popup.SetValue(owner,null);nextData=0;}
                at+=widths[i];
            }
        }
        static void RefreshData(int tab)
        {
            string view=tab+":"+scope+":"+selectedGame;
            if(Now<nextData&&view==dataView)return;dataView=view;nextData=Now+1;
            campaign=CampaignCosts.SavedGames();var recorded=CombatHistory.Games;
            past=recorded.Concat(campaign.Where(r=>!recorded.Any(a=>a.Source==r.Source&&a.MissionIndex==r.MissionIndex&&a.Status=="Completed"))).ToList();
            past=past.OrderByDescending(r=>r.EndedUtc).ThenByDescending(r=>r.MissionIndex).ToList();
            if(tab==1)body=CampaignCosts.GameLines(scope==0?campaign:scope==1?recorded:new List<CombatGameRecord>{CampaignCosts.CaptureLive("Current mission")},true);
            else if(selectedGame!=null)
            {var r=past.FirstOrDefault(x=>x.Id==selectedGame);body=r==null?new[]{"Game record is no longer available."}:CampaignCosts.GameLines(new[]{r},true);}
        }
        static void Text(object owner,float x,float y,string text,bool heading=false)
        {CostGUI.Label(x,y,604,22,text,heading?title.GetValue(owner):label.GetValue(owner));}
        static void DrawBody(object owner,float x,float y,int tab)
        {
            RefreshData(tab);var style=ButtonStyle(owner);
            if(tab==1)
            {
                Text(owner,x,y,"Cumulative Combat Costs",true);y+=28;
                if(CostGUI.Button(x,y,168,24,"This campaign",style)){scope=0;nextData=0;}
                if(CostGUI.Button(x+174,y,220,24,"Recorded game sessions",style)){scope=1;nextData=0;}
                bool live=(bool)missionActive.GetValue(owner);
                if(live&&CostGUI.Button(x+400,y,204,24,"Current mission detail",style)){scope=2;nextData=0;}
                y+=29;
                Text(owner,x,y,scope==0?"Completed missions in this campaign save; current play is separate.":scope==1?"All locally recorded ended sessions, including retries and replays.":"Current mission: expenditure, all registered losses and captured lost stores.");y+=24;
                foreach(string line in body){Text(owner,x,y,line);y+=22;}
                Text(owner,x,y+8,"Crew, repairs, operating fuel and unrepresented cargo are outside this account.");
                return;
            }
            Text(owner,x,y,"Last games",true);y+=28;
            if(selectedGame!=null)
            {
                var record=past.FirstOrDefault(r=>r.Id==selectedGame);
                if(CostGUI.Button(x,y,110,24,"Back to games",style)){selectedGame=null;nextData=0;return;}y+=29;
                if(record!=null){Text(owner,x,y,Clean(record.Name,78));y+=23;Text(owner,x,y,When(record)+" / "+record.Status);y+=24;}
                foreach(string line in body){Text(owner,x,y,line);y+=22;}
                return;
            }
            Text(owner,x,y,"Recorded sessions and earlier debriefs available in this campaign save.");y+=25;
            int pages=Math.Max(1,(past.Count+5)/6);page=Math.Min(page,pages-1);
            foreach(var record in past.Skip(page*6).Take(6))
            {
                string text=When(record)+"  "+Clean(record.Name,50)+"  / "+record.Status;
                if(CostGUI.Button(x,y,604,30,text,style)){selectedGame=record.Id;nextData=0;}y+=35;
            }
            if(past.Count==0){Text(owner,x,y,"No game history yet. Earlier standalone games were not recorded.");y+=30;}
            y+=8;
            if(CostGUI.Button(x,y,80,24,"Previous",style))page=Math.Max(0,page-1);
            if(CostGUI.Button(x+86,y,80,24,"Next",style))page=Math.Min(pages-1,page+1);
            Text(owner,x+182,y,"Page "+(page+1)+" / "+pages);y+=31;
            if(CombatHistory.ReadOnly)Text(owner,x,y,"History file needs review; its existing data has been preserved.");
        }
        static string Clean(string text,int length)
        {text=(text ?? "Game").Replace('<','(').Replace('>',')').Replace('\n',' ').Replace('\r',' ');return text.Length>length?text.Substring(0,length-1)+"…":text;}
        static string When(CombatGameRecord record)
        {return record.EndedUtc==0?"Saved debrief":new DateTime(record.EndedUtc,DateTimeKind.Utc).ToLocalTime().ToString("dd MMM HH:mm");}
        static void DrawMenu(object owner)
        {
            styles.Invoke(owner,null);if(selected==0)selected=1;
            var old=frame;frame=new Frame{Owner=owner,Tab=selected,Previous=old};
            try
            {
                CostGUI.Panel((float)top.GetValue(owner),(float)right.GetValue(owner),(float)scale.GetValue(owner),(float)opacity.GetValue(owner),(x,y)=>{
                    Text(owner,x+12,y+5,"COMBAT COSTS / F11",true);
                    Text(owner,x+12,y+30,"Task Force menu");Tabs(owner,x+12,y+56,false);
                    DrawBody(owner,x+12,y+90,frame.Tab);
                });
            }
            finally{frame=old;}
        }
        // Accessors used by the GUI wrapper while the description postfix is
        // suppressed; it must measure the original string, not its own gaps.
        internal static string UnextendedDescription(object owner)
        {
            var display=owner.GetType().GetField("display",Api.All).GetValue(owner);var old=frame;frame=null;
            try{return (string)display.GetType().GetProperty("Description",Api.All).GetValue(display,null);}
            finally{frame=old;}
        }
    }

    internal static class CostGUI
    {
        static Type gui,rect,style,texture;
        static ConstructorInfo rectangle,content,colour,vector;
        static MethodInfo label,button,height,drawTexture,trs;
        static PropertyInfo matrix,color,depth,screenWidth,screenHeight,white,whiteTexture,identity,skin,skinButton;
        internal static void Bind()
        {
            gui=Api.FindType("UnityEngine.GUI");rect=Api.FindType("UnityEngine.Rect");style=Api.FindType("UnityEngine.GUIStyle");texture=Api.FindType("UnityEngine.Texture");
            var text=Api.FindType("UnityEngine.GUIContent");var rgba=Api.FindType("UnityEngine.Color");var vec=Api.FindType("UnityEngine.Vector3");var quat=Api.FindType("UnityEngine.Quaternion");var mat=Api.FindType("UnityEngine.Matrix4x4");
            rectangle=rect.GetConstructor(new[]{typeof(float),typeof(float),typeof(float),typeof(float)});content=text.GetConstructor(new[]{typeof(string)});
            colour=rgba.GetConstructor(new[]{typeof(float),typeof(float),typeof(float),typeof(float)});vector=vec.GetConstructor(new[]{typeof(float),typeof(float),typeof(float)});
            label=Api.Method(gui,"Label",typeof(void),rect,typeof(string),style);button=Api.Method(gui,"Button",typeof(bool),rect,typeof(string),style);
            height=Api.Method(style,"CalcHeight",typeof(float),text,typeof(float));drawTexture=Api.Method(gui,"DrawTexture",typeof(void),rect,texture);
            matrix=gui.GetProperty("matrix",Api.All);color=gui.GetProperty("color",Api.All);depth=gui.GetProperty("depth",Api.All);
            var screen=Api.FindType("UnityEngine.Screen");screenWidth=screen.GetProperty("width",Api.All);screenHeight=screen.GetProperty("height",Api.All);
            white=rgba.GetProperty("white",Api.All);whiteTexture=Api.FindType("UnityEngine.Texture2D").GetProperty("whiteTexture",Api.All);identity=quat.GetProperty("identity",Api.All);
            trs=Api.Method(mat,"TRS",mat,vec,quat,vec);skin=gui.GetProperty("skin",Api.All);skinButton=Api.FindType("UnityEngine.GUISkin").GetProperty("button",Api.All);
            if(rectangle==null||content==null||colour==null||vector==null||matrix==null||color==null||depth==null||screenWidth==null||screenHeight==null||white==null||whiteTexture==null||identity==null||skin==null||skinButton==null)throw new MissingMemberException("Unity cost overlay GUI API");
        }
        static object Rect(float x,float y,float w,float h){return rectangle.Invoke(new object[]{x,y,w,h});}
        internal static void Label(float x,float y,float w,float h,string text,object face){label.Invoke(null,new[]{Rect(x,y,w,h),text,face});}
        internal static bool Button(float x,float y,float w,float h,string text,object face){return (bool)button.Invoke(null,new[]{Rect(x,y,w,h),text,face});}
        internal static object DefaultButton(){return skinButton.GetValue(skin.GetValue(null,null),null);}
        internal static float Height(string text,object face,float width){return (float)height.Invoke(face,new[]{content.Invoke(new object[]{text}),width});}
        internal static string NativeDescription(object owner){return F11CombatCosts.UnextendedDescription(owner);}
        internal static void Panel(float top,float right,float requestedScale,float alpha,Action<float,float> draw)
        {
            object oldMatrix=matrix.GetValue(null,null),oldColor=color.GetValue(null,null),oldDepth=depth.GetValue(null,null);
            try
            {
                float width=(int)screenWidth.GetValue(null,null),height=(int)screenHeight.GetValue(null,null);
                float zoom=Math.Max(0.25f,Math.Min(requestedScale,Math.Min((width-12)/652f,(height-12)/570f)));
                matrix.SetValue(null,trs.Invoke(null,new[]{vector.Invoke(new object[]{0f,0f,0f}),identity.GetValue(null,null),vector.Invoke(new object[]{zoom,zoom,1f})}),null);
                depth.SetValue(null,-50,null);float x=Math.Max(0,width/zoom-640-right),y=Math.Max(0,Math.Min(top,height/zoom-560));
                color.SetValue(null,colour.Invoke(new object[]{0.035f,0.055f,0.075f,alpha}),null);
                drawTexture.Invoke(null,new[]{Rect(x,y,640,550),whiteTexture.GetValue(null,null)});color.SetValue(null,white.GetValue(null,null),null);
                draw(x,y);
            }
            finally{matrix.SetValue(null,oldMatrix,null);color.SetValue(null,oldColor,null);depth.SetValue(null,oldDepth,null);}
        }
    }
}
