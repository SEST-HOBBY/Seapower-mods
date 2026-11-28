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
            // Dynamic Campaign Mod still needs its adapter. Identify now uses the native API.
            // Sub Ammunition, Second Thrust and Automatic SAR were rebuilt by
            // their authors for 0.9 and, like the R5 pair, now load unchanged.
            var adaptedImages=new[] { "3813157776/DynamicCampaignMod.dll" };
            foreach (string relative in adaptedImages.Concat(new[] { "3790594162/IdentifyExpanded.dll", "3789188689/SubAmmunitionMod.dll", "3789188689/SecondThrustMod.dll",
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

            // Dynamic Campaign Mod 1.0.4 (28 Nov 2026 capture, b816459d; as 1.0.2, 18a2416e). Its author
            // ported it to the 0.9 API, so the adapted image differs from his
            // in four kinds of site only; everything else is as he wrote it.
            var campaignRewritten=new List<int>();
            using (var campaignAuthor=ModuleDefinition.ReadModule(Path.Combine(workshop,relatives["DynamicCampaignMod"]),new ReaderParameters { AssemblyResolver=resolver }))
            using (var campaignImage=ModuleDefinition.ReadModule(paths["DynamicCampaignMod"],new ReaderParameters { AssemblyResolver=resolver })) {
                var sites=Types(campaignImage.Types).SelectMany(t=>t.Methods).Where(m=>m.HasBody)
                    .SelectMany(m=>m.Body.Instructions.Select(i=>(Method: m, Site: i))).ToList();
                string At((MethodDefinition Method, Mono.Cecil.Cil.Instruction Site) s) => s.Method.DeclaringType.FullName+"::"+s.Method.Name;
                bool Calls(Mono.Cecil.Cil.Instruction i, string owner, string name) => i.Operand is MethodReference c && c.DeclaringType.FullName==owner && c.Name==name;
                // attack-property: AI._objectToDestroy is a property on 0.9.3.
                var attackFields=sites.Where(s=>s.Site.Operand is FieldReference f && f.DeclaringType.FullName=="SeaPower.AI" && f.Name=="_objectToDestroy").ToList();
                var attackReads=sites.Where(s=>Calls(s.Site,"SeaPower.AI","get__objectToDestroy")).ToList();
                var attackWrites=sites.Where(s=>Calls(s.Site,"SeaPower.AI","set__objectToDestroy")).ToList();
                Check(attackFields.Count==0 && attackReads.Count==12 && attackWrites.Count==2 &&
                    attackReads.Concat(attackWrites).All(s=>s.Site.OpCode==Mono.Cecil.Cil.OpCodes.Call && ((MethodReference)s.Site.Operand).Resolve()?.IsStatic==false) &&
                    attackReads.Concat(attackWrites).All(s=>s.Method.DeclaringType.FullName.StartsWith("DynamicCampaignMod.Game.Battle.BattleSession",StringComparison.Ordinal)) &&
                    attackReads.Concat(attackWrites).Select(s=>s.Method).Distinct().Count()==10,
                    "The adapted campaign reads AI._objectToDestroy 12 times and writes it twice, in 10 battle methods, through the native accessors and never as a field");
                Check(Types(campaignAuthor.Types).SelectMany(t=>t.Methods).Where(m=>m.HasBody).SelectMany(m=>m.Body.Instructions)
                    .Count(i=>i.Operand is FieldReference f && f.DeclaringType.FullName=="SeaPower.AI" && f.Name=="_objectToDestroy")==14,
                    "The author's image names AI._objectToDestroy as a field at the same 14 sites");
                // HasNightCapableSensors: the one direct query, now in NightSight.
                var nightCalls=sites.Where(s=>Calls(s.Site,"SeaPower.LoadoutSummary","HasNightCapableSensors")).ToList();
                Check(nightCalls.Count==1 && At(nightCalls[0])=="DynamicCampaignMod.Game.Battle.NightSight::OfLoadout" &&
                    ((MethodReference)nightCalls[0].Site.Operand).Parameters.Count==4 && nightCalls[0].Site.Previous.OpCode==Mono.Cecil.Cil.OpCodes.Ldnull,
                    "Exactly one real campaign night query, in NightSight.OfLoadout, supplies the new native default nation=null");
                // fuel-refresh: the zero-distance display refresh.
                var fuelCalls=sites.Where(s=>Calls(s.Site,"SeaPower.Aircraft","UpdateFuelConsumption")).ToList();
                Check(fuelCalls.Count==1 && At(fuelCalls[0])=="DynamicCampaignMod.Game.Battle.BattleSession::ApplyCampaignFuel" &&
                    ((MethodReference)fuelCalls[0].Site.Operand).Parameters.Count==0 && fuelCalls[0].Site.Previous.OpCode==Mono.Cecil.Cil.OpCodes.Pop &&
                    fuelCalls[0].Site.Previous.Previous.OpCode==Mono.Cecil.Cil.OpCodes.Ldc_R4 && Equals(fuelCalls[0].Site.Previous.Previous.Operand,0f),
                    "The one campaign fuel refresh, in BattleSession.ApplyCampaignFuel, drops its zero distance and calls the native parameterless refresh");
                // locations: the mod's copy check, startup log and broken-object report see the Workshop path.
                var locationCalls=sites.Where(s=>Calls(s.Site,typeof(BetaAssemblyPolicy).FullName,"OriginalLocation")).ToList();
                Check(locationCalls.Select(At).OrderBy(x=>x,StringComparer.Ordinal).SequenceEqual(new[] { "DynamicCampaignMod.DeferredPatcher::Location",
                        "DynamicCampaignMod.Game.Session.BrokenObjectsWatch::FileOf", "DynamicCampaignMod.Game.Session.BrokenObjectsWatch::Folder",
                        "DynamicCampaignMod.Plugin::PublicLocation" }) &&
                    !sites.Any(s=>Calls(s.Site,"System.Reflection.Assembly","get_Location")),
                    "The four Assembly.Location reads (Plugin.PublicLocation, DeferredPatcher.Location, BrokenObjectsWatch.FileOf/Folder) return the original Workshop path");
                // On 261123 the campaign calls only the map bridges of
                // AssemblyAdapters.Campaign261123.cs (checked in R6_Campaign261123).
                var mapBridges=new[] { "CampaignSideLook","CampaignGroupBrush","NewCampaignDrawingLayer","CampaignFlatTileLayer","CampaignGlobeToDispose" };
                Check(sites.Where(s=>(s.Site.Operand as MemberReference)?.DeclaringType?.FullName==typeof(BetaCompatibilityCalls).FullName)
                        .All(s=>mapBridges.Contains(((MemberReference)s.Site.Operand).Name)),
                    "The adapted campaign calls no SEST compatibility bridge but the 261123 map bridges");
                // Nothing else is rewritten: every other body is the author's.
                var authorTypes=Types(campaignAuthor.Types).ToList(); var adaptedTypes=Types(campaignImage.Types).ToList();
                Check(authorTypes.Select(t=>t.FullName).SequenceEqual(adaptedTypes.Select(t=>t.FullName)), "Adapted campaign image has the author's types");
                Check(authorTypes.Zip(adaptedTypes,(x,y)=>x.Methods.Select(m=>m.FullName).SequenceEqual(y.Methods.Select(m=>m.FullName))).All(same=>same),
                    "Adapted campaign types have the author's methods");
                var changed=new List<MethodDefinition>(); int compared=0;
                for (int type=0; type<authorTypes.Count; type++) for (int index=0; index<authorTypes[type].Methods.Count; index++) {
                    var written=authorTypes[type].Methods[index]; var adaptedMethod=adaptedTypes[type].Methods[index];
                    if (!written.HasBody) continue;
                    compared++;
                    if (!TopoInstructions(written).SequenceEqual(TopoInstructions(adaptedMethod))) changed.Add(adaptedMethod);
                }
                var rewritten=attackReads.Concat(attackWrites).Concat(nightCalls).Concat(fuelCalls).Concat(locationCalls).Select(s=>s.Method).Distinct().ToList();
                // 261123: the ten methods holding the map bridges (R6_Campaign261123) differ too.
                var mapMethods=new[] { "CampaignUI::OpenScene","ViewerPlot::.ctor","PaperPictures::KindIcon","DrawingTools::Restore","GlobeMap::Make",
                    "GlobeMap::Fail","<>c::<Install>b__79_5","IconPalette::Side","MapMirror::Fade","MapMirror::Create" };
                var expectedChanged=rewritten.Concat(changed.Where(m=>mapMethods.Contains(m.DeclaringType.Name+"::"+m.Name))).Distinct().ToList();
                Check(compared>40000 && changed.Count==26 && expectedChanged.Count==26 &&
                    changed.OrderBy(m=>m.FullName,StringComparer.Ordinal).SequenceEqual(expectedChanged.OrderBy(m=>m.FullName,StringComparer.Ordinal)),
                    "Of "+compared+" campaign method bodies, only the 16 holding a kept rewrite and the 10 holding a 261123 map bridge differ from the author's (actual: "+String.Join(", ",changed.Select(m=>m.DeclaringType.Name+"::"+m.Name))+")");
                campaignRewritten.AddRange(changed.Select(m=>m.MetadataToken.ToInt32()));
                // The menu's file lookups are the author's own layer-aware calls.
                var menu=campaignImage.GetType("DynamicCampaignMod.Game.Patches.CampaignMenuPatch").Methods.Single(m=>m.Name=="Postfix");
                var lookups=menu.Body.Instructions.Where(i=>Calls(i,"SeaPower.FileManager","GetDirectories") || Calls(i,"SeaPower.FileManager","GetFiles"))
                    .Select(i=>(MethodReference)i.Operand).ToList();
                Check(lookups.Select(c=>c.Name).SequenceEqual(new[] { "GetDirectories", "GetFiles" }) && !changed.Contains(menu) &&
                    lookups.All(c=>c.Parameters.Select(x=>x.ParameterType.FullName).SequenceEqual(new[] { "System.String", "SeaPower.LayerKind" })),
                    "The campaign menu's two file lookups are the author's own layer-aware calls, not rewritten");
                WorldShipyardPins(campaignImage);
                WorldSideChoicePins(campaignImage);
            }
            // R14, R15: author images that still name game members the game no longer has are
            // held before CLR load by the generic native-member check, with
            // the member named. On 261123 Enhanced Decoy, Multi-Stage Missiles and
            // Osprey Mechanics (with its deck code) load through their adapters
            // (R6_EnhancedDecoy, R6_MultiStageChaff, R6_OspreyMechanics); the
            // selector's 0.8.7-only Loadout Manager payload is still held.
            foreach (var (relative, member) in new[] {
                ("3606134711/LoadoutManager0_8_7.dll", "SeaPower.FileManager::FileExists(System.String)") }) {
                string source=Path.Combine(workshop,relative); byte[] bytes=File.ReadAllBytes(source);
                var messages=new List<string>();
                Check(BetaAssemblyPolicy.Prepare(source,native,cache,messages.Add)==null, "Image incompatible with 0.9.3 is held before CLR load: "+relative);
                Check(messages.Count==1 && messages[0].StartsWith("SKIPPED before CLR load: "+Path.GetFileName(source)+"; ") && messages[0].Contains(member),
                    "Hold names the missing game member or held library: "+relative+" -> "+String.Join(" | ",messages));
                Check(File.ReadAllBytes(source).SequenceEqual(bytes), "Held author bytes and data remain untouched: "+relative);
                Check(!AppDomain.CurrentDomain.GetAssemblies().Any(x=>x.GetName().Name==Path.GetFileNameWithoutExtension(source)), "Held image never enters CLR: "+relative);
            }
            string topo=BetaAssemblyPolicy.Prepare(Path.Combine(workshop,"3826122523/SeaPowerTopo.dll"),native,cache,Console.WriteLine);
            Check(topo!=null && topo!=Path.Combine(workshop,"3826122523/SeaPowerTopo.dll"),
                "The 3D topographic map in the same item resolves on 0.9.3 and is admitted through its shallow-water adapter (R6_Topography181)");

            foreach (var pair in paths) {
                var loaded=Assembly.LoadFile(pair.Value);
                Check(BetaAssemblyPolicy.OriginalLocation(loaded)==Path.Combine(workshop,relatives[pair.Key]), "Original asset provenance: "+pair.Key);
                if (pair.Key=="DynamicCampaignMod") {
                    var postfix=loaded.GetType("DynamicCampaignMod.Game.Patches.CampaignMenuPatch",true).GetMethod("Postfix",BindingFlags.NonPublic|BindingFlags.Static);
                    var instructions=PatchProcessor.GetOriginalInstructions(postfix);
                    Check(instructions.Count(i=>(i.operand as MethodInfo)?.Name=="GetDirectories")==1 && instructions.Count(i=>(i.operand as MethodInfo)?.Name=="GetFiles")==1 &&
                        instructions.Where(i=>(i.operand as MethodInfo)?.Name=="GetDirectories" || (i.operand as MethodInfo)?.Name=="GetFiles")
                            .All(i=>((MethodInfo)i.operand).DeclaringType==typeof(FileManager) && ((MethodInfo)i.operand).GetParameters().Last().ParameterType==typeof(LayerKind)),
                        "Real campaign menu IL resolves the layer-aware lookups on 0.9.3");
                    var night=typeof(LoadoutSummary).GetMethods(BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Static)
                        .Single(m=>m.Name=="HasNightCapableSensors");
                    var nation=night.GetParameters().Last();
                    Check(night.GetParameters().Length==4 && nation.Name=="nation" && nation.ParameterType==typeof(string) &&
                        nation.IsOptional && nation.DefaultValue==null,
                        "Current night-sensor query has the inspected optional nation=null inference contract");
                    // Every rewritten body resolves against the game in the CLR,
                    // and the runtime compiles it.
                    Check(campaignRewritten.Count==26, "Rewritten campaign bodies (16 kept rules, 10 holding 261123 map bridges) recorded for the CLR checks");
                    foreach (int token in campaignRewritten) {
                        var method=loaded.ManifestModule.ResolveMethod(token);
                        var body=PatchProcessor.GetOriginalInstructions(method);
                        Check(body.Count>0 && !body.Any(i=>i.operand is FieldInfo f && f.DeclaringType==typeof(AI) && f.Name=="_objectToDestroy"),
                            "Rewritten campaign IL resolves: "+method.DeclaringType.Name+"::"+method.Name);
                        System.Runtime.CompilerServices.RuntimeHelpers.PrepareMethod(method.MethodHandle);
                        Check(true, "Rewritten campaign method compiles: "+method.DeclaringType.Name+"::"+method.Name);
                    }
                    var battle=loaded.GetType("DynamicCampaignMod.Game.Battle.BattleSession",true);
                    foreach (string name in new[] { "LookTurn", "BackToMap", "Prepare", "OnSceneLoaded", "TablesOf", "Enemy" }) {
                        var methods=battle.GetMethods(BindingFlags.NonPublic|BindingFlags.Public|BindingFlags.Static).Where(m=>m.Name==name).ToList();
                        Check(methods.Count==1, "Real campaign battle method exists once: "+name);
                        Check(PatchProcessor.GetOriginalInstructions(methods[0]).Count>0,"Real campaign battle IL resolves: "+name);
                    }
                    // LookTurn builds the game's ConstantSpeed and passes it to
                    // SetSpeedCommand as the author wrote it. The retired
                    // speed rewrites made this method invalid on 1.0.0.
                    var look=battle.GetMethod("LookTurn",BindingFlags.NonPublic|BindingFlags.Public|BindingFlags.Static);
                    var lookBody=PatchProcessor.GetOriginalInstructions(look);
                    Check(lookBody.Any(i=>i.operand is ConstructorInfo c && c.DeclaringType.FullName=="SeaPower.ConstantSpeed") &&
                        lookBody.Any(i=>i.operand is MethodInfo m && m.Name=="SetSpeedCommand" && m.DeclaringType==typeof(ObjectBase)) &&
                        !lookBody.Any(i=>(i.operand as MemberInfo)?.DeclaringType==typeof(BetaCompatibilityCalls)),
                        "LookTurn keeps the author's native ConstantSpeed and SetSpeedCommand calls");
                    System.Runtime.CompilerServices.RuntimeHelpers.PrepareMethod(look.MethodHandle);
                    Check(true, "LookTurn compiles as the author wrote it");
                }
            }
            CurrentCaptureNativeScan(workshop, native, cache, resolver);
            FileLayerFixture(cache);
            HailGuardFixture();
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
