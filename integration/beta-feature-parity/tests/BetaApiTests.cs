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
            var paths=new Dictionary<string,string>(); var relatives=new Dictionary<string,string>();
            // R14: Dynamic Campaign Mod and Identify keep their private images.
            // Sub Ammunition, Second Thrust and Automatic SAR were rebuilt by
            // their authors for 0.9 and, like the R5 pair, now load unchanged.
            var adaptedImages=new[] { "3813157776/DynamicCampaignMod.dll", "3790594162/IdentifyExpanded.dll" };
            foreach (string relative in adaptedImages.Concat(new[] { "3789188689/SubAmmunitionMod.dll", "3789188689/SecondThrustMod.dll",
                "3774105087/AutomaticSAR.dll", "3784474738/WeaponLauncherEffects.dll", "3784474738/SubModelStabilization.dll" })) {
                string source=Path.Combine(workshop,relative); byte[] bytes=File.ReadAllBytes(source);
                string adapted=BetaAssemblyPolicy.Prepare(source,native,cache,Console.WriteLine);
                Check(adapted != null && File.Exists(adapted), "Current API image admitted: "+relative);
                if (adaptedImages.Contains(relative)) Check(adapted != source, "Private API image generated: "+relative);
                else Check(adapted == source, "Rebuilt author image needs no retired adapter: "+relative);
                Check(bytes.SequenceEqual(File.ReadAllBytes(source)), "Author bytes retained: "+relative);
                paths[Path.GetFileNameWithoutExtension(source)]=adapted; relatives[Path.GetFileNameWithoutExtension(source)]=relative;
            }
            Check(!File.Exists(Path.Combine(workshop,"3789188689/SubAmmunitionMod.fixed.dll")),
                "The captured 0.9 Sub Ammunition item no longer ships the duplicate .fixed image the loader used to exclude");
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
            Check(missing.Count==0 && resolved>100, "All active direct native method/field operands resolve across the current fixtures");
            Console.WriteLine("Resolved native operands: "+resolved);

            using (var campaignImage=ModuleDefinition.ReadModule(paths["DynamicCampaignMod"],new ReaderParameters { AssemblyResolver=resolver })) {
                var nightCalls=Types(campaignImage.Types).SelectMany(t=>t.Methods).Where(m=>m.HasBody)
                    .SelectMany(m=>m.Body.Instructions).Where(i=>i.Operand is MethodReference c &&
                    c.DeclaringType.FullName=="SeaPower.LoadoutSummary" && c.Name=="HasNightCapableSensors").ToList();
                Check(nightCalls.Count==1 && ((MethodReference)nightCalls[0].Operand).Parameters.Count==4 &&
                    nightCalls[0].Previous.OpCode==Mono.Cecil.Cil.OpCodes.Ldnull,
                    "Exactly one real campaign night query supplies the new native default nation=null");
            }
            // R14: author images that still name game members 0.9.2 removed are
            // held before CLR load by the generic native-member check, with
            // the member named; Osprey deck code is held with its library.
            foreach (var (relative, member) in new[] {
                ("3784474738/EnhancedDecoyMod.dll", "SeaPower.WeaponSystemChaff::_ammoInUse"),
                ("3784474738/MultiStageMissiles.dll", "SeaPower.ChaffCloud::launchChaffEffect"),
                ("3806466625/OspreyMechanics.dll", "SeaPower.Aircraft::UpdateFuelConsumption(System.Single)"),
                ("3826122523/SeaPowerTopoFlat.dll", "SeaPower.Globals::_alliedTaskforce"),
                ("3806466625/OspreyDeckOps.dll", "depends on OspreyMechanics, which names game members this build does not have") }) {
                string source=Path.Combine(workshop,relative); byte[] bytes=File.ReadAllBytes(source);
                var messages=new List<string>();
                Check(BetaAssemblyPolicy.Prepare(source,native,cache,messages.Add)==null, "Image incompatible with 0.9.2 is held before CLR load: "+relative);
                Check(messages.Count==1 && messages[0].StartsWith("SKIPPED before CLR load: "+Path.GetFileName(source)+"; ") && messages[0].Contains(member),
                    "Hold names the missing game member or held library: "+relative+" -> "+String.Join(" | ",messages));
                Check(File.ReadAllBytes(source).SequenceEqual(bytes), "Held author bytes and data remain untouched: "+relative);
                Check(!AppDomain.CurrentDomain.GetAssemblies().Any(x=>x.GetName().Name==Path.GetFileNameWithoutExtension(source)), "Held image never enters CLR: "+relative);
            }
            string topo=BetaAssemblyPolicy.Prepare(Path.Combine(workshop,"3826122523/SeaPowerTopo.dll"),native,cache,Console.WriteLine);
            Check(topo!=null && topo!=Path.Combine(workshop,"3826122523/SeaPowerTopo.dll"),
                "The 3D topographic map in the same item resolves on 0.9.2 and is admitted through its shallow-water adapter (R6_Topography162)");

            foreach (var pair in paths) {
                var loaded=Assembly.LoadFile(pair.Value);
                Check(BetaAssemblyPolicy.OriginalLocation(loaded)==Path.Combine(workshop,relatives[pair.Key]), "Original asset provenance: "+pair.Key);
                if (pair.Key=="DynamicCampaignMod") {
                    var postfix=loaded.GetType("DynamicCampaignMod.Game.Patches.CampaignMenuPatch",true).GetMethod("Postfix",BindingFlags.NonPublic|BindingFlags.Static);
                    var instructions=PatchProcessor.GetOriginalInstructions(postfix);
                    Check(instructions.Any(i=>(i.operand as MethodInfo)?.Name=="GetDirectories") &&
                        instructions.Where(i=>(i.operand as MethodInfo)?.Name=="GetDirectories" || (i.operand as MethodInfo)?.Name=="GetFiles")
                            .All(i=>((MethodInfo)i.operand).GetParameters().Last().ParameterType==typeof(LayerKind)),
                        "Real campaign menu IL resolves the beta layer-aware lookups");
                    var night=typeof(LoadoutSummary).GetMethods(BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Static)
                        .Single(m=>m.Name=="HasNightCapableSensors");
                    var nation=night.GetParameters().Last();
                    Check(night.GetParameters().Length==4 && nation.Name=="nation" && nation.ParameterType==typeof(string) &&
                        nation.IsOptional && nation.DefaultValue==null,
                        "Current night-sensor query has the inspected optional nation=null inference contract");
                    var battle=loaded.GetType("DynamicCampaignMod.Game.Battle.BattleSession",true);
                    foreach (string name in new[] { "LookTurn", "BackToMap", "Prepare", "OnSceneLoaded", "TablesOf", "Enemy" }) {
                        foreach (var method in battle.GetMethods(BindingFlags.NonPublic|BindingFlags.Public|BindingFlags.Static).Where(m=>m.Name==name))
                            Check(PatchProcessor.GetOriginalInstructions(method).Count>0,"Real campaign battle IL resolves: "+name);
                    }
                }
            }
            CurrentCaptureNativeScan(workshop, native, cache, resolver);
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
            // Current author releases include their beta fixes; legacy R5 tests
            // remain with the frozen R6 candidate.
            Check(paths["WeaponLauncherEffects"] == Path.Combine(workshop,"3784474738/WeaponLauncherEffects.dll"), "Current launcher author bytes load directly");
            Check(paths["SubModelStabilization"] == Path.Combine(workshop,"3784474738/SubModelStabilization.dll"), "Current stabilization author bytes load directly");
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
    static void HailGuardFixture()
    {
        PlayerGuardFixture("SkipEnemyHailCandidate", true, true, false);
        PlayerGuardFixture("IsInitializedPlayerUnit", false, true, false);
    }
    static void PlayerGuardFixture(string bridge, bool unassigned, bool player, bool nonplayer)
    {
        // ObjectBase's static initializer needs Unity/newer game Mono intrinsics.
        // Execute the ACTUAL compiled bridge IL with only its two native member
        // operands rebound to plain test candidates. No fake game DLL is used.
        var method=new DynamicMethod(bridge+"Fixture",typeof(bool),new[] { typeof(HailCandidate) },typeof(BetaApiTests),true);
        var il=method.GetILGenerator(); int rebound=0;
        var body=PatchProcessor.GetOriginalInstructions(typeof(BetaCompatibilityCalls).GetMethod(bridge),il);
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
        Check(skip(new HailCandidate())==unassigned,bridge+": unassigned candidate does not reach the unsafe getter");
        Check(skip(null)==unassigned,bridge+": null candidate is handled");
        Check(skip(new HailCandidate { Taskforce=new object(),Player=true })==player,bridge+": native player decision retained");
        Check(skip(new HailCandidate { Taskforce=new object(),Player=false })==nonplayer,bridge+": native non-player decision retained");
    }
    static void FileLayerFixture(string root)
    {
        string high=Path.Combine(root,"high"), low=Path.Combine(root,"low");
        foreach (string layer in new[] { high,low }) Directory.CreateDirectory(Path.Combine(layer,"dynamic_campaigns","test"));
        File.WriteAllText(Path.Combine(high,"dynamic_campaigns/test/campaign.json"),"{\"name\":\"higher priority\"}");
        File.WriteAllText(Path.Combine(low,"dynamic_campaigns/test/campaign.json"),"{\"name\":\"lower priority\"}");
        var manager=(FileManager)FormatterServices.GetUninitializedObject(typeof(FileManager));
        typeof(FileManager).GetField("_fileIndex",BindingFlags.NonPublic|BindingFlags.Instance).SetValue(manager,
            new System.Collections.Concurrent.ConcurrentDictionary<string,HashSet<string>>(StringComparer.OrdinalIgnoreCase));
        typeof(FileManager).GetField("_layers",BindingFlags.NonPublic|BindingFlags.Instance).SetValue(manager,
            new FileLayerSnapshot(new[] { new FileLayer(high,LayerKind.All),new FileLayer(low,LayerKind.All) }));
        var folders=manager.GetDirectories("dynamic_campaigns",LayerKind.All);
        Check(folders.Count==1 && folders[0].Replace('\\','/')=="dynamic_campaigns/test","Native beta campaign directories merge active layers");
        var files=manager.GetFiles(folders[0],LayerKind.All);
        Check(files.Count==2 && files[0]==Path.Combine(high,"dynamic_campaigns/test/campaign.json"),"Native beta campaign file ordering retains layer priority");
        // IniHandler's static initializer needs Unity's streamingAssetsPath.
        // Its live parser is a PC check; the real call operands/defaults are
        // checked above without substituting a fake parser or game assembly.
    }
}
