using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using System.Runtime.Serialization;
using AnchorChain;
using HarmonyLib;
using Mono.Cecil;
using SeaPower;
using SeapowerUI;
using SeapowerUI.ViewModels;

static partial class BetaApiTests
{
    public sealed class HailCandidate
    {
        public object Taskforce;
        public bool Player;
        public object GetTaskforce() => Taskforce;
        public bool IsPlayerUnit => Taskforce==null ? throw new Exception("Unsafe getter reached before taskforce assignment") : Player;
    }
    static int checks;
    static void Check(bool ok, string why) { checks++; if (!ok) throw new Exception(why); }
    static IEnumerable<TypeDefinition> Types(IEnumerable<TypeDefinition> roots)
    {
        foreach (var type in roots) { yield return type; foreach (var child in Types(type.NestedTypes)) yield return child; }
    }
    static void Main(string[] args)
    {
        string workshop=Path.GetFullPath(args[0]), native=Path.GetFullPath(args[1]);
        string references=Path.GetDirectoryName(native), cache=Path.Combine(Path.GetTempPath(), "SEST-Api-"+Guid.NewGuid().ToString("N"));
        AppDomain.CurrentDomain.AssemblyResolve += (s,e) => {
            string path=Path.Combine(references,new AssemblyName(e.Name).Name+".dll");
            return File.Exists(path) ? Assembly.LoadFrom(path) : null;
        };
        try {
            var paths=new Dictionary<string,string>();
            foreach (string relative in new[] { "3813157776/DynamicCampaignMod.dll", "3784474738/EnhancedDecoyMod.dll",
                "3789188689/SubAmmunitionMod.dll", "3789188689/SecondThrustMod.dll", "3790594162/IdentifyExpanded.dll",
                "3784474738/WeaponLauncherEffects.dll", "3784474738/SubModelStabilization.dll" }) {
                string source=Path.Combine(workshop,relative); byte[] bytes=File.ReadAllBytes(source);
                string adapted=BetaAssemblyPolicy.Prepare(source,native,cache,Console.WriteLine);
                Check(adapted != source && File.Exists(adapted), "Private API image generated: "+relative);
                Check(bytes.SequenceEqual(File.ReadAllBytes(source)), "Author bytes retained: "+relative);
                paths[Path.GetFileNameWithoutExtension(source)]=adapted;
            }
            Check(BetaAssemblyPolicy.Prepare(Path.Combine(workshop,"3789188689/SubAmmunitionMod.fixed.dll"),native,cache,Console.WriteLine)==null,
                "Captured duplicate is excluded even when enumerated before the canonical image");
            using var resolver=new DefaultAssemblyResolver(); resolver.AddSearchDirectory(references);
            resolver.AddSearchDirectory(Path.GetDirectoryName(typeof(BetaAssemblyPolicy).Assembly.Location));
            var missing=new List<string>(); int resolved=0;
            foreach (var pair in paths) {
                using var module=ModuleDefinition.ReadModule(pair.Value,new ReaderParameters { AssemblyResolver=resolver });
                foreach (var type in Types(module.Types)) foreach (var method in type.Methods) {
                    if (!method.HasBody) continue;
                    foreach (var instruction in method.Body.Instructions) {
                        var member=instruction.Operand as MemberReference;
                        if (member?.DeclaringType?.Scope is not AssemblyNameReference scope || scope.Name!="Seapower-Scripts") continue;
                        try {
                            if (member is MethodReference call) { if (call.Resolve()==null) throw new Exception("unresolved method"); resolved++; }
                            else if (member is FieldReference field) { if (field.Resolve()==null) throw new Exception("unresolved field"); resolved++; }
                        } catch (Exception ex) { missing.Add(pair.Key+"/"+method.Name+": "+member.FullName+" "+ex.Message); }
                    }
                }
            }
            foreach (string failure in missing) Console.WriteLine("MISSING "+failure);
            Check(missing.Count==0 && resolved>100, "All active direct native method/field operands resolve across seven adapted images");
            Console.WriteLine("Resolved native operands: "+resolved);
            using (var ammo=ModuleDefinition.ReadModule(paths["SubAmmunitionMod"],new ReaderParameters { AssemblyResolver=resolver })) {
                var calls=Types(ammo.Types).SelectMany(t=>t.Methods).Where(m=>m.HasBody).SelectMany(m=>m.Body.Instructions)
                    .Where(i=>i.Operand is MethodReference call && call.DeclaringType.FullName=="SeaPower.Utils" && call.Name=="openIniFile").ToList();
                Check(calls.Count==5 && calls.All(i=>((MethodReference)i.Operand).Parameters.Count==4 &&
                    i.Previous.OpCode==Mono.Cecil.Cil.OpCodes.Ldc_I4 && (int)i.Previous.Operand==0),
                    "All five real sub-ammunition INI sites append forceDisk=false");
            }

            // Reproduce the exact constructor-layout precondition behind the
            // screenshot, then run the real author's contact transpiler. Full
            // Hooks.Validate requires initialized Unity Globals and stays a PC check.
            var ctor=AccessTools.Constructor(typeof(WeaponContactViewModel),new[] { typeof(WeaponBase),typeof(Vehicle),typeof(MapUnitViewModel) });
            var body=PatchProcessor.GetOriginalInstructions(ctor);
            Check(body.Last(i=>i.opcode==OpCodes.Ret).labels.Count==0, "Captured beta ret really has no branch label");
            var epilogue=BetaCompatibilityCalls.FindDecoyContactExit(body,null);
            Check(epilogue.labels.Count>0, "Beta registration epilogue has its real merge label");
            var decoy=Assembly.LoadFile(paths["EnhancedDecoyMod"]);
            var hooks=decoy.GetType("EnhancedDecoyMod.Hooks",true);
            var rewritten=((IEnumerable<CodeInstruction>)hooks.GetMethod("ContactConstructor",BindingFlags.NonPublic|BindingFlags.Static)
                .Invoke(null,new object[] { body })).ToList();
            Check(rewritten.Count==body.Count+3 && rewritten.Any(i=>i.opcode==OpCodes.Brtrue && epilogue.labels.Contains((Label)i.operand)),
                "Decoy guard branches to contact registration, preserving beta's epilogue");
            Check(rewritten.Contains(epilogue) && ReferenceEquals(rewritten.Last(),body.Last()), "Original registration/return retained");

            foreach (var pair in paths.Where(x=>x.Key!="EnhancedDecoyMod")) {
                var loaded=Assembly.LoadFile(pair.Value);
                Check(BetaAssemblyPolicy.OriginalLocation(loaded)==Path.Combine(workshop,
                    pair.Key=="DynamicCampaignMod" ? "3813157776/DynamicCampaignMod.dll" :
                    pair.Key=="IdentifyExpanded" ? "3790594162/IdentifyExpanded.dll" :
                    pair.Key=="WeaponLauncherEffects" || pair.Key=="SubModelStabilization" ? "3784474738/"+pair.Key+".dll" : "3789188689/"+pair.Key+".dll"),
                    "Original asset provenance: "+pair.Key);
                if (pair.Key=="DynamicCampaignMod") {
                    var postfix=loaded.GetType("DynamicCampaignMod.Game.Patches.CampaignMenuPatch",true).GetMethod("Postfix",BindingFlags.NonPublic|BindingFlags.Static);
                    var instructions=PatchProcessor.GetOriginalInstructions(postfix);
                    Check(instructions.Any(i=>(i.operand as MethodInfo)?.Name=="GetDirectories") &&
                        instructions.Where(i=>(i.operand as MethodInfo)?.Name=="GetDirectories" || (i.operand as MethodInfo)?.Name=="GetFiles")
                            .All(i=>((MethodInfo)i.operand).GetParameters().Last().ParameterType==typeof(LayerKind)),
                        "Real campaign menu IL resolves the beta layer-aware lookups");
                    var battle=loaded.GetType("DynamicCampaignMod.Game.Battle.BattleSession",true);
                    foreach (string name in new[] { "LookTurn", "BackToMap", "Prepare", "OnSceneLoaded", "TablesOf", "Enemy" }) {
                        foreach (var method in battle.GetMethods(BindingFlags.NonPublic|BindingFlags.Public|BindingFlags.Static).Where(m=>m.Name==name))
                            Check(PatchProcessor.GetOriginalInstructions(method).Count>0,"Real campaign battle IL resolves: "+name);
                    }
                }
            }
            FileLayerFixture(cache);
            var speed=BetaCompatibilityCalls.ConstantSpeedRequest(17.25f,null);
            Check(speed.Kind==SpeedKind.Constant && speed.Value==17.25f,"Campaign constant speed preserves knots in the beta value type");
            HailGuardFixture();
            Check(BetaCompatibilityCalls.CampaignMethod(typeof(ObjectBase),"SetAttackAtWaypointTask",new[] { typeof(string),typeof(ObjectBase),typeof(GeoPosition),typeof(GeoPosition),typeof(int),typeof(VisualActionTask),typeof(EngageTask.SalvoType),typeof(float),typeof(bool),typeof(bool) },null).GetParameters().Length==12,
                "Campaign ASW capability check resolves the adapted native signature");
            Check(BetaCompatibilityCalls.CampaignProperty(typeof(Globals),"_secondEnemyTaskforce")?.PropertyType==typeof(Taskforce),
                "Secondary-side capability check resolves its concrete beta registry bridge");
            Check(typeof(Taskforce).GetProperty("Relations")?.PropertyType==typeof(SideRelations) &&
                typeof(SideRelations).GetProperty("Sides")?.PropertyType==typeof(IReadOnlyList<Taskforce>),
                "Secondary-side bridge binds beta's real registered-side types");
            LauncherAndStabilizationChecks(paths, resolver);
            R6Checks(new R6Context { Workshop=workshop, Native=native, Cache=cache, Resolver=resolver });
            // Taskforce's static profiler initialization needs the game Mono
            // intrinsics. Live registry evaluation remains part of the PC test.
            Console.WriteLine("Campaign/scenario beta API checks passed: "+checks+"; managed fixtures only, no Unity gameplay.");
        } finally { if (Directory.Exists(cache)) Directory.Delete(cache,true); }
    }
    // R6: each adapter's checks live in BetaApiTests.<Plugin>.cs as a static
    // void R6_<Plugin>(R6Context) method, run here in name order. Every
    // adapter the loader registers must have one.
    internal sealed class R6Context
    {
        internal string Workshop, Native, Cache;
        internal DefaultAssemblyResolver Resolver;
    }
    static void R6Checks(R6Context context)
    {
        var methods=typeof(BetaApiTests).GetMethods(BindingFlags.NonPublic|BindingFlags.Static)
            .Where(m=>m.Name.StartsWith("R6_",StringComparison.Ordinal) && m.GetParameters().Length==1 &&
                m.GetParameters()[0].ParameterType==typeof(R6Context))
            .OrderBy(m=>m.Name,StringComparer.Ordinal).ToList();
        foreach (string name in BetaAssemblyPolicy.AdapterNames())
            Check(methods.Any(m=>m.Name=="R6_"+name), "R6 adapter has its own managed checks: "+name);
        foreach (var method in methods) {
            int before=checks;
            try { method.Invoke(null,new object[] { context }); }
            catch (TargetInvocationException ex) when (ex.InnerException!=null) {
                System.Runtime.ExceptionServices.ExceptionDispatchInfo.Capture(ex.InnerException).Throw();
            }
            Console.WriteLine(method.Name.Substring(3)+" checks passed: "+(checks-before));
        }
    }
    // R5: WeaponLauncherEffects 1.0.18 and SubModelStabilization 1.1.2 from
    // Euromod's Anchor Chain Expansion Pack. Metadata and reflection only; no
    // Harmony patch is applied and no plugin or game code runs.
    static void LauncherAndStabilizationChecks(Dictionary<string,string> paths, DefaultAssemblyResolver resolver)
    {
        const BindingFlags all=BindingFlags.NonPublic|BindingFlags.Public|BindingFlags.Static|BindingFlags.Instance;
        using (var effects=ModuleDefinition.ReadModule(paths["WeaponLauncherEffects"],new ReaderParameters { AssemblyResolver=resolver })) {
            var post=effects.GetType("WeaponLauncherEffectsAnchorChain.WeaponContainerLaunchLauncherEffectsPatch").Methods.Single(m=>m.Name=="Postfix");
            var il=post.Body.Instructions;
            Check(post.Parameters.Count==3 && post.Parameters[2].Name=="__result" && post.Parameters[2].ParameterType.FullName=="System.Boolean",
                "Launcher postfix receives the beta launch result");
            Check(il[0].OpCode==Mono.Cecil.Cil.OpCodes.Ldarg_2 && il[1].OpCode==Mono.Cecil.Cil.OpCodes.Brtrue && il[2].OpCode==Mono.Cecil.Cil.OpCodes.Ret &&
                ReferenceEquals(il[1].Operand,il[3]), "A failed launch returns before the author's effect code");
            foreach (string name in new[] { "WeaponContainerLaunchLauncherEffectsPatch", "WeaponContainerMagazineLaunchLauncherEffectsPatch" }) {
                var target=effects.GetType("WeaponLauncherEffectsAnchorChain."+name).Methods.Single(m=>m.Name=="TargetMethod").Body.Instructions;
                Check(target.Count(i=>(i.Operand as MethodReference)?.Name=="LauncherEffectsMethod")==1 &&
                    !target.Any(i=>(i.Operand as MethodReference)?.DeclaringType.FullName=="HarmonyLib.AccessTools"),
                    "Launcher lookup goes through the bridge: "+name);
            }
            foreach (string name in new[] { "WeaponSystemLaunchNativeEffectsPatch", "WeaponContainerInitLauncherEffectsPatch" }) {
                var target=effects.GetType("WeaponLauncherEffectsAnchorChain."+name).Methods.Single(m=>m.Name=="TargetMethod").Body.Instructions;
                Check(target.Any(i=>(i.Operand as MethodReference)?.DeclaringType.FullName=="HarmonyLib.AccessTools") &&
                    !target.Any(i=>(i.Operand as MethodReference)?.Name=="LauncherEffectsMethod"), "Unchanged lookup keeps the author's call: "+name);
            }
        }
        var vector=typeof(UnityEngine.Vector3);
        var launch5=new[] { typeof(ObjectBase), vector, vector, typeof(float), typeof(string) };
        var magazine6=new[] { typeof(string), typeof(ObjectBase), vector, vector, typeof(float), typeof(float) };
        Check(AccessTools.Method(typeof(WeaponContainer),"launch",launch5,null)==null && AccessTools.Method(typeof(WeaponContainer),"LaunchFromMagazine",magazine6,null)==null,
            "The author's stable launcher lookups fail on the beta, as captured");
        var launch=BetaCompatibilityCalls.LauncherEffectsMethod(typeof(WeaponContainer),"launch",launch5,null);
        var magazine=BetaCompatibilityCalls.LauncherEffectsMethod(typeof(WeaponContainer),"LaunchFromMagazine",magazine6,null);
        Check(launch!=null && launch.ReturnType==typeof(bool) && launch.GetParameters().Length==6 && launch.GetParameters()[5].Name=="failedLaunch",
            "Bridge resolves beta WeaponContainer.launch with failedLaunch");
        Check(magazine!=null && magazine.ReturnType==typeof(bool) && magazine.GetParameters().Length==7 && magazine.GetParameters()[6].Name=="failedLaunch",
            "Bridge resolves beta WeaponContainer.LaunchFromMagazine with failedLaunch");
        Check(BetaCompatibilityCalls.LauncherEffectsMethod(typeof(WeaponContainer),"launch",new[] { typeof(int) },null)==null,
            "Any other launcher lookup passes through unchanged");
        using (var stabilizer=ModuleDefinition.ReadModule(paths["SubModelStabilization"],new ReaderParameters { AssemblyResolver=resolver })) {
            var patch=stabilizer.GetType("SubModelStabilizationAnchorChain.VesselLoaderStabilizationPatch");
            var post=patch.Methods.Single(m=>m.Name=="Postfix");
            Check(post.Parameters.Count==2 && post.Parameters[0].Name=="vesselIniName" && post.Parameters[1].Name=="vp" &&
                post.Parameters[1].ParameterType.FullName=="SeaPower.VesselParameters", "Stabilization postfix takes the caller's VesselParameters vp");
            var target=patch.Methods.Single(m=>m.Name=="TargetMethod").Body.Instructions;
            Check(target.Count(i=>(i.Operand as MethodReference)?.Name=="StabilizationMethod")==1 &&
                !target.Any(i=>(i.Operand as MethodReference)?.DeclaringType.FullName=="HarmonyLib.AccessTools"), "Vessel loader lookup goes through the bridge");
        }
        var batch=typeof(ResourceLoader).GetNestedType("ResourceBatch",all);
        var ten=new[] { typeof(string), typeof(string), typeof(string), typeof(int), typeof(GeoPosition), typeof(GeoPosition), typeof(Taskforce), batch, typeof(string), typeof(bool) };
        Check(batch!=null && AccessTools.Method(typeof(VesselLoader),"loadShipFromInternalResources",ten,null)==null,
            "The author's stable vessel loader lookup fails on the beta, as captured");
        var load=BetaCompatibilityCalls.StabilizationMethod(typeof(VesselLoader),"loadShipFromInternalResources",ten,null);
        Check(load!=null && load.ReturnType==typeof(void) && load.GetParameters().Length==11 && load.GetParameters()[0].Name=="vp" &&
            load.GetParameters()[0].ParameterType==typeof(VesselParameters) && load.GetParameters()[3].Name=="vesselIniName",
            "Bridge resolves the beta vessel loader with vp first");
        // HarmonyX binds a patch parameter by the original's parameter name, or
        // as __instance, __state or __result. Check the adapted patches against
        // the real beta targets by reflection.
        var launchPost=Assembly.LoadFile(paths["WeaponLauncherEffects"])
            .GetType("WeaponLauncherEffectsAnchorChain.WeaponContainerLaunchLauncherEffectsPatch",true).GetMethod("Postfix",all);
        Check(launchPost.GetParameters().Select(p=>p.Name).SequenceEqual(new[] { "__instance", "__state", "__result" }) &&
            launchPost.GetParameters()[0].ParameterType==typeof(WeaponContainer) && launchPost.GetParameters()[2].ParameterType==launch.ReturnType,
            "Launcher postfix binds __instance and __result to the beta launch");
        var stabilizerPost=Assembly.LoadFile(paths["SubModelStabilization"])
            .GetType("SubModelStabilizationAnchorChain.VesselLoaderStabilizationPatch",true).GetMethod("Postfix",all);
        foreach (var parameter in stabilizerPost.GetParameters()) {
            var match=load.GetParameters().SingleOrDefault(p=>p.Name==parameter.Name);
            Check(match!=null && match.ParameterType==parameter.ParameterType, "Stabilization postfix parameter binds by name: "+parameter.Name);
        }
    }
    static void HailGuardFixture()
    {
        // ObjectBase's static initializer needs Unity/newer game Mono intrinsics.
        // Execute the ACTUAL compiled bridge IL with only its two native member
        // operands rebound to plain test candidates. No fake game DLL is used.
        var method=new DynamicMethod("HailGuardFixture",typeof(bool),new[] { typeof(HailCandidate) },typeof(BetaApiTests),true);
        var il=method.GetILGenerator(); int rebound=0;
        var body=PatchProcessor.GetOriginalInstructions(typeof(BetaCompatibilityCalls).GetMethod("SkipEnemyHailCandidate"),il);
        foreach (var instruction in body) {
            foreach (var label in instruction.labels) il.MarkLabel(label);
            object operand=instruction.operand;
            if (operand is FieldInfo field && field.DeclaringType==typeof(ObjectBase) && field.Name=="_taskforce") {
                operand=typeof(HailCandidate).GetField("Taskforce"); rebound++;
            }
            if (operand is MethodInfo call && call.DeclaringType==typeof(ObjectBase) && call.Name=="get_IsPlayerUnit") {
                operand=typeof(HailCandidate).GetProperty("IsPlayerUnit").GetGetMethod(); rebound++;
            }
            if (operand is MethodInfo taskforce && taskforce.DeclaringType==typeof(ObjectBase) && taskforce.Name=="get__taskforce") {
                operand=typeof(HailCandidate).GetMethod("GetTaskforce"); rebound++;
            }
            if (operand==null) il.Emit(instruction.opcode);
            else if (operand is MethodInfo target) il.Emit(instruction.opcode,target);
            else if (operand is FieldInfo targetField) il.Emit(instruction.opcode,targetField);
            else if (operand is Label targetLabel) il.Emit(instruction.opcode,targetLabel);
            else throw new Exception("Uninspected hail predicate operand: "+operand);
        }
        Check(rebound==2,"Hail fixture rebinds exactly the native taskforce member and player-unit getter (actual="+rebound+")");
        var skip=(Func<HailCandidate,bool>)method.CreateDelegate(typeof(Func<HailCandidate,bool>));
        Check(skip(new HailCandidate()),"Real guard IL skips an unassigned candidate before its unsafe getter");
        Check(skip(null),"Real guard IL skips a null candidate");
        Check(skip(new HailCandidate { Taskforce=new object(),Player=true }),"Real guard IL skips a player unit");
        Check(!skip(new HailCandidate { Taskforce=new object(),Player=false }),"Real guard IL preserves an eligible non-player unit");
    }
    static void FileLayerFixture(string root)
    {
        string high=Path.Combine(root,"high"), low=Path.Combine(root,"low");
        foreach (string layer in new[] { high,low }) Directory.CreateDirectory(Path.Combine(layer,"dynamic_campaigns","test"));
        File.WriteAllText(Path.Combine(high,"dynamic_campaigns/test/campaign.json"),"{\"name\":\"higher priority\"}");
        File.WriteAllText(Path.Combine(low,"dynamic_campaigns/test/campaign.json"),"{\"name\":\"lower priority\"}");
        Directory.CreateDirectory(Path.Combine(high,"ammunition"));
        string ini=Path.Combine(high,"ammunition/test.ini"); File.WriteAllText(ini,"[SubAmmunition]\nSubAmmunitionName=child\n");
        var manager=(FileManager)FormatterServices.GetUninitializedObject(typeof(FileManager));
        typeof(FileManager).GetField("_fileIndex",BindingFlags.NonPublic|BindingFlags.Instance).SetValue(manager,
            new System.Collections.Concurrent.ConcurrentDictionary<string,HashSet<string>>(StringComparer.OrdinalIgnoreCase));
        typeof(FileManager).GetField("_layers",BindingFlags.NonPublic|BindingFlags.Instance).SetValue(manager,
            new FileLayerSnapshot(new[] { new FileLayer(high,LayerKind.All),new FileLayer(low,LayerKind.All) }));
        var folders=manager.GetDirectories("dynamic_campaigns",LayerKind.All);
        Check(folders.Count==1 && folders[0].Replace('\\','/')=="dynamic_campaigns/test","Native beta campaign directories merge active layers");
        var files=manager.GetFiles(folders[0],LayerKind.All);
        Check(files.Count==2 && files[0]==Path.Combine(high,"dynamic_campaigns/test/campaign.json"),"Native beta campaign file ordering retains layer priority");
        Check(BetaCompatibilityCalls.GetLegacyFile(manager,"ammunition/test.ini","")==ini,"Sub-ammunition lookup retains first active-layer match");
        // IniHandler's static initializer needs Unity's streamingAssetsPath.
        // Its live parser is a PC check; the real call operands/defaults are
        // checked above without substituting a fake parser or game assembly.
    }
}
