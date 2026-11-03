using System;
using System.IO;
using System.Reflection;
class Probe {
 static int Main(string[] args) {
  AppDomain.CurrentDomain.AssemblyResolve += (s,e)=> {
   string n=new AssemblyName(e.Name).Name+".dll";
   string p=Path.Combine(args[0],n);
   if(File.Exists(p))return Assembly.LoadFrom(p);
   foreach(string d in Directory.GetDirectories(args[2],"*",SearchOption.AllDirectories)) {
    p=Path.Combine(d,n);if(File.Exists(p))return Assembly.LoadFrom(p);
   }
   return null;
  };
  var game=Assembly.LoadFrom(Path.Combine(args[0],"Seapower-Scripts.dll"));
  var rt=Assembly.LoadFrom(args[1]);int fails=0;
  foreach(string entry in new[]{"TowedSensorGuard.Bind","TerrainClearance.Bind","TaskForceDebrief.Bind","PreparationMap.Bind","CampaignCosts.Bind","CampaignCosts.BindLive","CampaignCosts.BindMenu","CampaignInventory.Bind","NativeCombatSurface.Bind","F11CombatCosts.BindMissionPath","VersionWatermark.Bind","ModifierRegistry.Bind"}) {
   try {
    int dot=entry.LastIndexOf('.');var t=rt.GetType("Sest.RuntimeFixes."+entry.Substring(0,dot),true);
    var m=t.GetMethod(entry.Substring(dot+1),BindingFlags.Static|BindingFlags.NonPublic|BindingFlags.Public);
    m.Invoke(null,m.GetParameters().Length==0?null:new object[]{game});
    Console.WriteLine("PASS "+entry);
   } catch(Exception e) {
    while(e.InnerException!=null)e=e.InnerException;
    Console.WriteLine("FAIL "+entry+" "+e.GetType().Name+": "+e.Message);fails++;
   }
  }
  var tracker=Assembly.LoadFrom(Path.Combine(args[2],"3807187341/CombatCosts.dll"));
  foreach(string name in new[]{"GameApi","VesselApi"}) {
   try { var type=tracker.GetType("WeaponCostsMod."+name,true);
    var values=name=="GameApi"?new object[]{game}:new object[]{game,(Action<string>)(x=>Console.WriteLine("TRACKER "+x))};
    Activator.CreateInstance(type,values);Console.WriteLine("PASS tracker "+name);
   } catch(Exception e){while(e.InnerException!=null)e=e.InnerException;Console.WriteLine("FAIL tracker "+name+" "+e.GetType().Name+": "+e.Message);fails++;}
  }
  foreach(string entry in new[]{"SeaPower.GameMain.Update","SeaPower.GameMain.OnDestroy","SeaPower.MissionManager.ResetData","SeaPower.CameraManager.OnLateUpdate"}) {
   int dot=entry.LastIndexOf('.');var type=game.GetType(entry.Substring(0,dot),true);
   var method=type.GetMethod(entry.Substring(dot+1),BindingFlags.Static|BindingFlags.Instance|BindingFlags.NonPublic|BindingFlags.Public,null,Type.EmptyTypes,null);
   if(method==null || method.ReturnType!=typeof(void)) {Console.WriteLine("FAIL deferred hook "+entry);fails++;}
   else Console.WriteLine("PASS deferred hook "+entry);
  }
  var noesis=Assembly.LoadFrom(Path.Combine(args[0],"Noesis.NoesisGUI.dll"));
  var wheel=game.GetType("SeapowerUI.SceneEdit.Behaviours.MapDragger",true).GetMethod("MapZoom",BindingFlags.Instance|BindingFlags.NonPublic|BindingFlags.Public,null,new[]{typeof(object),noesis.GetType("Noesis.MouseWheelEventArgs",true)},null);
  if(wheel==null || wheel.ReturnType!=typeof(void)) {Console.WriteLine("FAIL deferred map wheel hook");fails++;} else Console.WriteLine("PASS deferred map wheel hook");
  return fails==0?0:1;
 }
}
