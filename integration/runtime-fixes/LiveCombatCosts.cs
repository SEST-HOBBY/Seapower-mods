using System;
using System.Reflection;

namespace Sest.RuntimeFixes
{
    // Uses the game's ordinary text modal. No Unity/Noesis/game DLL is shipped,
    // no tracker UI is patched, and closing restores the prior time compression.
    internal static class LiveCombatCosts
    {
        static MethodInfo keyDown,format,create,open,oldExecute,getTime,setTime,unpause,pause;
        static PropertyInfo action,loaded;
        static FieldInfo view,initialized;
        static ConstructorInfo command;
        static object[] keyArgs;
        static WeakReference popup;
        static bool active;

        internal static MethodInfo Bind(Assembly game,string key)
        {
            active=false;
            CampaignCosts.BindLive(game);
            Type input=Api.FindType("UnityEngine.Input"),keyCode=Api.FindType("UnityEngine.KeyCode");
            keyDown=Api.Method(input,"GetKeyDown",typeof(bool),keyCode);
            keyArgs=new[]{Enum.Parse(keyCode,key,true)};
            Type data=Api.Type(game,"SeaPower.MissionPopupData"),obj=Api.Type(game,"SeaPower.ObjectBase");
            Type modal=Api.Type(game,"SeapowerUI.Modal"),rich=Api.Type(game,"SeaPower.RichMissionMessages");
            Type element=Api.FindType("Noesis.UIElement"),rows=Api.Type(game,"SeapowerUI.RichMissionMessageObjectiveRow");
            format=Api.Method(rich,"FormatPopupMessageText",data,typeof(string),obj);
            create=Api.Method(rich,"CreateMissionPopupModal",modal,data,element,typeof(bool),typeof(bool),typeof(DateTime?),typeof(System.Collections.Generic.IList<>).MakeGenericType(rows));
            view=Api.Type(game,"SeapowerUI.MainGameView").GetField("Instance",Api.All);
            var routed=Api.Type(game,"SeapowerUI.CustomRoutedCommand");
            open=Api.Method(routed,"Execute",typeof(void),typeof(object),element);
            var host=Api.Type(game,"SeapowerUI.WindowHostCommands");
            var openProperty=host.GetProperty("OpenWindowCommand",Api.All);
            if(openProperty==null || view==null)throw new MissingMemberException("native modal host");
            openCommand=openProperty.GetValue(null,null);
            action=modal.GetProperty("ActionCommand",Api.All);loaded=modal.GetProperty("IsLoaded",Api.All);
            Type delegateCommand=Api.Type(game,"SeaPower.DelegateCommand");
            command=delegateCommand.GetConstructor(new[]{typeof(Action<object>)});
            oldExecute=Api.Method(delegateCommand,"Execute",typeof(void),typeof(object));
            var time=Api.Type(game,"SeaPower.GameTime");
            getTime=Api.Method(time,"get_TimeCompression",typeof(float));setTime=Api.Method(time,"set_TimeCompression",typeof(void),typeof(float));
            unpause=Api.Method(time,"UnPause",typeof(void));pause=Api.Method(time,"Pause",typeof(void),typeof(bool));
            Type main=Api.Type(game,"SeaPower.GameMain");initialized=main.GetField("_initialized",Api.All);
            if(action==null || loaded==null || loaded.PropertyType!=typeof(bool) || command==null || initialized==null || initialized.FieldType!=typeof(bool))
                throw new MissingMemberException("live costs modal/input API");
            active=true;popup=null;
            return Api.Method(main,"Update",typeof(void));
        }
        internal static void Install(Assembly game,string key)
        {
            var update=Bind(game,key);
            try{Api.Postfix(update,typeof(LiveCombatCosts),"Postfix","io.github.sest-hobby.live-combat-costs");}
            catch{active=false;throw;}
            Api.Log("live combat cost summary installed: "+key+"; native tracker remains on F11; prior pause/speed restored on close");
        }
        static object openCommand;
        internal static void Postfix(object __instance)
        {
            if(!active || __instance==null || !(bool)initialized.GetValue(__instance))return;
            try
            {
                if(!(bool)keyDown.Invoke(null,keyArgs))return;
                if(popup!=null && popup.IsAlive && (bool)loaded.GetValue(popup.Target,null))return;
                string body=CampaignCosts.LiveSummary();object context=view.GetValue(null);if(context==null)return;
                float prior=(float)getTime.Invoke(null,null);
                object message=format.Invoke(null,new object[]{"SEST COMBAT COSTS|[size=14]"+body.Replace("|","/")+"[/size]|Close",null});
                object window=create.Invoke(null,new object[]{message,context,true,false,null,null});
                object native=action.GetValue(window,null);
                if(native==null || !oldExecute.DeclaringType.IsInstanceOfType(native))throw new MissingMemberException("native close command");
                Action<object> close=parameter=>{
                    try{oldExecute.Invoke(native,new[]{parameter});}
                    finally
                    {
                        popup=null;
                        if(Object.ReferenceEquals(context,view.GetValue(null)))
                        {
                            if(prior>0)unpause.Invoke(null,null);else pause.Invoke(null,new object[]{true});
                            setTime.Invoke(null,new object[]{prior});
                        }
                    }
                };
                action.SetValue(window,command.Invoke(new object[]{close}),null);
                popup=new WeakReference(window);open.Invoke(openCommand,new[]{window,context});
            }
            catch(Exception e){active=false;Api.LogFailure("live combat cost summary disabled; capture and native controls retained",e);}
        }
    }
}
