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
  foreach(string entry in new[]{"TowedSensorGuard.Bind","TerrainClearance.Bind","TaskForceDebrief.Bind","PreparationMap.Bind","CampaignCosts.Bind","CampaignCosts.BindLive","CampaignCosts.BindMenu","CampaignInventory.Bind","NativeCombatSurface.Bind","F11CombatCosts.BindMissionPath","VersionWatermark.Bind","ModifierRegistry.Bind","MissionAwards.Bind"}) {
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
  Assembly.LoadFrom(Path.Combine(args[0],"UnityEngine.InputLegacyModule.dll"));
  try {
   rt.GetType("Sest.RuntimeFixes.F11CombatCosts",true).GetMethod("Bind",BindingFlags.Static|BindingFlags.NonPublic).Invoke(null,new object[]{tracker});
   Console.WriteLine("PASS F11CombatCosts.Bind Tracker 0.8 visibility");
  } catch(Exception e) { while(e.InnerException!=null)e=e.InnerException;Console.WriteLine("FAIL tracker overlay bind "+e);fails++; }
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
  fails+=PopOutProvenance(args,rt);
  return fails==0?0:1;
 }
 // Group Manager 0.2.22 needs no rewrite and loads from its Workshop file.
 // The pop-out bridge must hash the Workshop file the loader recorded for an
 // image, also when the image runs from the private cache (Identify Expanded
 // here), and must still reject any other hash.
 static string Sha(string path) {
  using(var s=File.OpenRead(path)) using(var sha=System.Security.Cryptography.SHA256.Create())
   return BitConverter.ToString(sha.ComputeHash(s)).Replace("-","").ToLowerInvariant();
 }
 static int PopOutProvenance(string[] args,Assembly rt) {
  const string GroupHash="b0ccafb34e942c10617fe763ba71e2eb9f2b488f52ea234030871593af643ac4";
  const string PopOutHash="c241a0d647cba1d71414fc20ac7b9a34f662e01a4533097db0a8841b8e7875f9";
  string cache=Path.Combine(Path.GetTempPath(),"SEST-PopOut-Provenance-"+Guid.NewGuid().ToString("N"));
  int fails=0;
  void Check(bool ok,string what){Console.WriteLine((ok?"PASS ":"FAIL ")+what);if(!ok)fails++;}
  try {
   string source=Path.Combine(args[2],"3818251045","SeaPowerSquadPanel.dll"), pop=Path.Combine(args[2],"3826396311","SeaPowerPopOut.dll");
   Check(Sha(source)==GroupHash && Sha(pop)==PopOutHash,"captured Group Manager 0.2.22 and Pop-Out Windows 1.4.1 fixtures");
   var log=new System.Collections.Generic.List<string>();
   string native=Path.Combine(args[0],"Seapower-Scripts.dll");
   string prepared=AnchorChain.BetaAssemblyPolicy.Prepare(source,native,cache,log.Add);
   Check(prepared!=null && Path.GetFullPath(prepared)==Path.GetFullPath(source) && !log.Exists(l=>l.Contains("SeaPowerSquadPanel")),
    "Group Manager 0.2.22 loads from its Workshop file: no rewrite, no hold");
   var group=Assembly.LoadFile(Path.GetFullPath(source));
   var hash=rt.GetType("Sest.RuntimeFixes.PopOutBridge",true).GetMethod("HashMatches",BindingFlags.Static|BindingFlags.NonPublic);
   Check((bool)hash.Invoke(null,new object[]{group,GroupHash}),"formation pop-out bridge accepts the inspected Group Manager DLL");
   Check(!(bool)hash.Invoke(null,new object[]{group,new string('0',64)}),"formation pop-out bridge still rejects any other hash");
   string campaign=Path.Combine(args[2],"3813157776","DynamicCampaignMod.dll");
   string adapted=AnchorChain.BetaAssemblyPolicy.Prepare(campaign,native,cache,log.Add);
   Check(adapted!=null && adapted!=campaign && Sha(adapted)!=Sha(campaign) && log.Exists(l=>l.Contains("ADAPTED DynamicCampaignMod")),
    "an adapted author image runs from the private cache with bytes of its own");
   var cached=Assembly.LoadFile(adapted);
   Check(AnchorChain.BetaAssemblyPolicy.OriginalLocation(cached)==Path.GetFullPath(campaign),"loader records the adapted image's Workshop provenance");
   Check((bool)hash.Invoke(null,new object[]{cached,Sha(campaign)}) && !(bool)hash.Invoke(null,new object[]{cached,Sha(adapted)}),
    "an adapted image is hashed at its Workshop file, not at the cached copy");
   var popAssembly=Assembly.LoadFrom(pop);
   Check((bool)hash.Invoke(null,new object[]{popAssembly,PopOutHash}) && !(bool)hash.Invoke(null,new object[]{popAssembly,GroupHash}),
    "unadapted Pop-Out image is hashed at its own location");
  } catch(Exception e) { while(e.InnerException!=null)e=e.InnerException;Console.WriteLine("FAIL pop-out provenance "+e.GetType().Name+": "+e.Message);fails++; }
  finally { try { if(Directory.Exists(cache))Directory.Delete(cache,true); } catch {} }
  return fails;
 }
}
