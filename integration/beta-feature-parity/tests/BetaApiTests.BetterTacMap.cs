using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using System.Runtime.CompilerServices;
using System.Runtime.Serialization;
using System.Security.Cryptography;
using AnchorChain;
using HarmonyLib;
using Mono.Cecil;
using SeaPower;
using SeapowerUI;
using SeapowerUI.ViewModels;
using CilOp = Mono.Cecil.Cil.OpCodes;

// R6: BetterTacMap (Workshop 3768036424). Metadata, reflection and bridge
// checks only; no Harmony patch is applied and no plugin or game code runs
// beyond the bridges' own managed field logic.
static partial class BetaApiTests
{
    const string BetterTacMapAudit = "attr-load-overload=1, attr-scene-ctor=1, attr-tactical-getter=2, layer-ctor=1, layers-by-id=3, " +
        "layers-by-name=1, layers-list=1, line3-refresh=1, locations=1, retype-display-state=4";

    static string BetterTacMapSha(string path)
    {
        using var sha=SHA256.Create();
        return BitConverter.ToString(sha.ComputeHash(File.ReadAllBytes(path))).Replace("-","").ToLowerInvariant();
    }

    static void R6_BetterTacMap(R6Context context)
    {
        const BindingFlags all=BindingFlags.NonPublic|BindingFlags.Public|BindingFlags.Static|BindingFlags.Instance|BindingFlags.DeclaredOnly;
        string source=Path.Combine(context.Workshop,"3768036424","BetterTacMap.dll");
        byte[] bytes=File.ReadAllBytes(source);
        Check(BetterTacMapSha(source)=="f1bdd2c2e5cec7579c3e47750950b1cb5521b5e4e630138aec8c483b6737ac08","BetterTacMap fixture is the captured, pinned image");
        var log=new List<string>();
        string adapted=BetaAssemblyPolicy.Prepare(source,context.Native,context.Cache,log.Add);
        foreach (string line in log) Console.WriteLine(line);
        Check(adapted!=source && File.Exists(adapted) && !String.Equals(Path.GetFullPath(adapted),Path.GetFullPath(source),StringComparison.OrdinalIgnoreCase),
            "BetterTacMap: private adapted image generated");
        Check(bytes.SequenceEqual(File.ReadAllBytes(source)),"BetterTacMap: author bytes unchanged");
        Check(log.Count==1 && log[0]=="ADAPTED BetterTacMap in private cache: "+BetterTacMapAudit+"; original Workshop DLL and asset paths preserved.",
            "BetterTacMap: logged audit is exactly the expected audit");
        string again=BetaAssemblyPolicy.Prepare(source,context.Native,Path.Combine(context.Cache,"btm-repeat"),_=>{});
        Check(BetterTacMapSha(again)==BetterTacMapSha(adapted),"BetterTacMap: adaptation is deterministic");

        // The written image, read back with Cecil.
        using (var module=ModuleDefinition.ReadModule(adapted,new ReaderParameters { AssemblyResolver=context.Resolver }))
        using (var game=ModuleDefinition.ReadModule(context.Native)) {
            TypeDefinition T(string name) => Types(module.Types).Single(t=>t.FullName=="BetterTacMap.Patches."+name || t.FullName=="BetterTacMap."+name);
            string Op(Mono.Cecil.Cil.Instruction i) => i.OpCode.Name+(i.Operand is MemberReference m ? " "+m.FullName : "");
            var register=T("MapLayerRegistrationPatch").Methods.Single(m=>m.Name=="Register");
            var ops=register.Body.Instructions.Select(Op).ToList();
            const string byId="callvirt System.Collections.Generic.IReadOnlyDictionary`2<System.Int32,SeapowerUI.MapLayer> SeapowerUI.MapDisplayState::get_LayersById()";
            const string byName="callvirt System.Collections.Generic.IReadOnlyDictionary`2<System.String,SeapowerUI.MapLayer> SeapowerUI.MapDisplayState::get_LayersByName()";
            const string list="callvirt System.Collections.ObjectModel.ObservableCollection`1<SeapowerUI.MapLayer> SeapowerUI.MapDisplayState::get_Layers()";
            const string castId="castclass System.Collections.Generic.Dictionary`2<System.Int32,SeapowerUI.MapLayer>";
            const string castName="castclass System.Collections.Generic.Dictionary`2<System.String,SeapowerUI.MapLayer>";
            const string bridge="call SeapowerUI.MapLayer AnchorChain.BetaCompatibilityCalls::BetterTacMapNewLayer(System.Int32,System.String,System.Boolean,SeapowerUI.MapDisplayState)";
            IEnumerable<int> At(string op) => Enumerable.Range(0,ops.Count).Where(i=>ops[i]==op);
            Check(register.Parameters[0].Name=="instance" && register.Parameters[0].ParameterType.FullName=="SeapowerUI.MapDisplayState",
                "BetterTacMap: Register takes the MapDisplayState");
            Check(At(byId).Count()==3 && At(byId).All(i=>ops[i-1]=="ldarg.0" && ops[i+1]==castId && ops[i+2]=="ldarg.1"),
                "BetterTacMap: Register reads LayersById three times through Tactical's getter, cast to its Dictionary");
            Check(At(byName).Count()==1 && At(byName).All(i=>ops[i-1]=="ldarg.0" && ops[i+1]==castName && ops[i+2]=="ldarg.2"),
                "BetterTacMap: Register writes LayersByName through Tactical's getter, cast to its Dictionary");
            Check(At(list).Count()==1 && At(list).All(i=>ops[i-1]=="ldarg.0" && ops[i+1]=="ldloc.0"),"BetterTacMap: Register adds to Tactical's Layers");
            Check(At(bridge).Count()==1 && At(bridge).All(i=>ops[i-1]=="ldarg.0" && ops[i-2]=="ldc.i4.1" && ops[i-3]=="ldarg.2" && ops[i-4]=="ldarg.1" &&
                ops[i-5]=="ldloc.0" && ops[i+1].StartsWith("stfld SeapowerUI.MapLayer BetterTacMap.Patches.MapLayerRegistrationPatch/<>c__DisplayClass")),
                "BetterTacMap: Register builds its layer with the internal-constructor bridge and its own owner");
            Check(register.Body.Instructions.Where(i=>i.OpCode.FlowControl==Mono.Cecil.Cil.FlowControl.Branch || i.OpCode.FlowControl==Mono.Cecil.Cil.FlowControl.Cond_Branch)
                .All(i=>i.OpCode.OperandType!=Mono.Cecil.Cil.OperandType.ShortInlineBrTarget),"BetterTacMap: rewritten Register uses long branches");
            Check(T("MapLayerRegistrationPatch").Methods.Single(m=>m.Name=="EnsureRegistered").Parameters.Single().ParameterType.FullName=="SeapowerUI.MapDisplayState",
                "BetterTacMap: EnsureRegistered takes the MapDisplayState");
            foreach (string name in new[] { "GizmoLayerManagerConstructorPatch", "GizmoLayerManagerInstanceGetterPatch" }) {
                var postfix=T(name).Methods.Single(m=>m.Name=="Postfix");
                Check(postfix.Parameters.Single().Name=="__result" && postfix.Parameters.Single().ParameterType.FullName=="SeapowerUI.MapDisplayState" &&
                    postfix.Body.Instructions.Select(Op).SequenceEqual(new[] { "nop", "ldarg.0",
                        "call System.Void BetterTacMap.Patches.MapLayerRegistrationPatch::EnsureRegistered(SeapowerUI.MapDisplayState)", "nop", "ret" }),
                    "BetterTacMap: "+name+".Postfix(MapDisplayState __result) registers on the Tactical owner");
                var attribute=T(name).CustomAttributes.Single(a=>a.AttributeType.FullName=="HarmonyLib.HarmonyPatch");
                Check(attribute.Constructor.Parameters.Select(p=>p.ParameterType.FullName).SequenceEqual(new[] { "System.Type", "System.String", "HarmonyLib.MethodType" }) &&
                    ((TypeReference)attribute.ConstructorArguments[0].Value).FullName=="SeapowerUI.MapDisplayState" &&
                    (string)attribute.ConstructorArguments[1].Value=="Tactical" && (int)attribute.ConstructorArguments[2].Value==1,
                    "BetterTacMap: "+name+" targets the MapDisplayState.Tactical getter");
            }
            var cleanup=T("DestroyedUnitCleanupPatch").Methods.Single(m=>m.Name=="Postfix").Body.Instructions;
            Check(Op(cleanup[0])=="ldarg.0" && Op(cleanup[1])=="call System.Void AnchorChain.BetaCompatibilityCalls::BetterTacMapRefreshLine3(SeapowerUI.MapUnitViewModel)" &&
                Op(cleanup[2])=="nop" && Op(cleanup[3])=="ldsfld System.Boolean BetterTacMap.BetterTacMapMod::IsEnabled",
                "BetterTacMap: the Update postfix first refreshes line 3, then runs the author's cleanup");
            var load=T("ModSettings").Methods.Single(m=>m.Name=="Load").Body.Instructions.Select(Op).ToList();
            Check(load.Count(o=>o=="call System.String AnchorChain.BetaAssemblyPolicy::OriginalLocation(System.Reflection.Assembly)")==1 &&
                !load.Any(o=>o.Contains("Assembly::get_Location")),"BetterTacMap: settings.cfg is read beside the Workshop DLL");
            var loadPatch=T("ModDrawingLoadPatch").CustomAttributes.Single(a=>a.AttributeType.FullName=="HarmonyLib.HarmonyPatch");
            Check(loadPatch.Constructor.Parameters.Select(p=>p.ParameterType.FullName).SequenceEqual(new[] { "System.Type", "System.String", "System.Type[]" }) &&
                ((CustomAttributeArgument[])loadPatch.ConstructorArguments[2].Value).Length==0,"BetterTacMap: LoadDrawingData is pinned to its parameterless overload");
            var eta=T("WaypointEtaModePatch").Methods.Single(m=>m.Name=="ConstructorPostfix").CustomAttributes.Single(a=>a.AttributeType.FullName=="HarmonyLib.HarmonyPatch");
            var sceneCtor=game.GetType("SeapowerUI.ViewModels.SceneMapViewModel").Methods.Single(m=>m.IsConstructor && !m.IsStatic);
            Check((int)eta.ConstructorArguments[0].Value==3 && ((CustomAttributeArgument[])eta.ConstructorArguments[1].Value)
                .Select(a=>((TypeReference)a.Value).FullName).SequenceEqual(sceneCtor.Parameters.Select(p=>p.ParameterType.FullName)),
                "BetterTacMap: the ETA constructor postfix lists the beta's ten constructor parameters");
            bool stale=false; int resolved=0; var missing=new List<string>();
            foreach (var type in Types(module.Types)) {
                foreach (var attribute in type.CustomAttributes.Concat(type.Methods.SelectMany(m=>m.CustomAttributes)))
                    stale|=attribute.ConstructorArguments.Any(a=>(a.Value as TypeReference)?.Name=="GizmoLayerManager");
                foreach (var method in type.Methods) {
                    stale|=method.Parameters.Any(p=>p.ParameterType.Name=="GizmoLayerManager");
                    if (!method.HasBody) continue;
                    foreach (var instruction in method.Body.Instructions) {
                        var member=instruction.Operand as MemberReference;
                        if (member==null) continue;
                        stale|=member.DeclaringType?.Name=="GizmoLayerManager" || member.FullName=="System.Void SeapowerUI.MapLayer::.ctor(System.Int32,System.String,System.Boolean)";
                        if (member.DeclaringType?.Scope is not AssemblyNameReference scope || (scope.Name!="Seapower-Scripts" && scope.Name!="AnchorChain")) continue;
                        try {
                            if (member is MethodReference call) { if (call.Resolve()==null) throw new Exception("unresolved method"); resolved++; }
                            else if (member is FieldReference field) { if (field.Resolve()==null) throw new Exception("unresolved field"); resolved++; }
                        } catch (Exception ex) { missing.Add(method.FullName+": "+member.FullName+" "+ex.Message); }
                    }
                }
            }
            foreach (string failure in missing) Console.WriteLine("MISSING BetterTacMap/"+failure);
            Check(!stale,"BetterTacMap: no signature, operand or attribute still names GizmoLayerManager or the stable MapLayer constructor");
            Check(missing.Count==0 && resolved>120,"BetterTacMap: all "+resolved+" Seapower-Scripts and bridge method/field operands resolve against the beta");
            var inspect=typeof(BetaAssemblyPolicy).GetMethod("InvalidNativeFields",BindingFlags.Static|BindingFlags.NonPublic);
            Check(((List<string>)inspect.Invoke(null,new object[] { module, game })).Count==0,"BetterTacMap: no field type changed between class and struct");
        }

        // The loaded image: provenance, real IL through the runtime's reader,
        // and HarmonyX's own target resolution for every patch method.
        var loaded=Assembly.LoadFile(adapted);
        Check(BetaAssemblyPolicy.OriginalLocation(loaded)==Path.GetFullPath(source),"BetterTacMap: OriginalLocation of the loaded image is its Workshop path");
        Type P(string name) => loaded.GetType("BetterTacMap.Patches."+name,true);
        var registerInfo=P("MapLayerRegistrationPatch").GetMethod("Register",all);
        var registerIl=PatchProcessor.GetOriginalInstructions(registerInfo);
        Check(registerIl.Any(i=>(i.operand as MethodInfo)==typeof(BetaCompatibilityCalls).GetMethod(nameof(BetaCompatibilityCalls.BetterTacMapNewLayer))) &&
            registerIl.Count(i=>(i.operand as MethodInfo)==typeof(MapDisplayState).GetProperty("LayersById").GetGetMethod())==3 &&
            registerIl.Count(i=>(i.operand as Type)==typeof(Dictionary<int,MapLayer>))==3 && registerIl.Count(i=>(i.operand as Type)==typeof(Dictionary<string,MapLayer>))==1,
            "BetterTacMap: the runtime reads the rewritten Register against the beta members");
        foreach (var method in new[] { registerInfo, P("MapLayerRegistrationPatch").GetMethod("EnsureRegistered",all),
            P("GizmoLayerManagerConstructorPatch").GetMethod("Postfix",all), P("GizmoLayerManagerInstanceGetterPatch").GetMethod("Postfix",all),
            P("DestroyedUnitCleanupPatch").GetMethod("Postfix",all), loaded.GetType("BetterTacMap.ModSettings",true).GetMethod("Load",all) }) {
            RuntimeHelpers.PrepareMethod(method.MethodHandle);
            Check(true,"BetterTacMap: rewritten "+method.DeclaringType.Name+"."+method.Name+" JIT-compiles");
        }

        var harmonyAssembly=typeof(Harmony).Assembly;
        var harmony=new Harmony("sest.r6.bettertacmap.readonly");
        var processor=harmonyAssembly.GetType("HarmonyLib.PatchClassProcessor",true);
        var processorCtor=processor.GetConstructor(new[] { typeof(Harmony), typeof(Type) });
        var containers=processor.GetField("containerAttributes",all);
        var patchMethods=processor.GetField("patchMethods",all);
        var original=harmonyAssembly.GetType("HarmonyLib.PatchTools",true).GetMethod("GetOriginalMethod",all);
        var info=harmonyAssembly.GetType("HarmonyLib.AttributePatch",true).GetField("info",all);
        var targets=new Dictionary<string,MethodBase>();
        foreach (var type in loaded.GetTypes()) {
            var instance=processorCtor.Invoke(new object[] { harmony, type });
            if (containers.GetValue(instance)==null) continue;
            foreach (var patch in (IList)patchMethods.GetValue(instance)) {
                var attribute=(HarmonyMethod)info.GetValue(patch);
                MethodBase target=null;
                try { target=(MethodBase)original.Invoke(null,new object[] { attribute }); }
                catch (TargetInvocationException ex) { Console.WriteLine("BetterTacMap target of "+type.Name+"."+attribute.method.Name+" throws "+ex.InnerException.Message); }
                Check(target!=null,"BetterTacMap: HarmonyX resolves "+type.Name+"."+attribute.method.Name+" on the beta");
                targets[type.Name+"."+attribute.method.Name]=target;
                BetterTacMapBinds(attribute.method,target);
            }
        }
        var tactical=typeof(MapDisplayState).GetProperty("Tactical",BindingFlags.Public|BindingFlags.Static).GetGetMethod();
        Check(targets.Count==21,"BetterTacMap: all 21 attribute patch methods resolve (actual="+targets.Count+")");
        Check(targets["GizmoLayerManagerConstructorPatch.Postfix"]==tactical && targets["GizmoLayerManagerInstanceGetterPatch.Postfix"]==tactical,
            "BetterTacMap: both registration postfixes target MapDisplayState.Tactical");
        Check(targets["ModDrawingLoadPatch.Postfix"]==typeof(SaveLoadManager).GetMethod("LoadDrawingData",BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Static,null,Type.EmptyTypes,null),
            "BetterTacMap: the load postfix targets parameterless LoadDrawingData");
        Check(targets["WaypointEtaModePatch.ConstructorPostfix"]==typeof(SceneMapViewModel).GetConstructors(BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Instance).Single(),
            "BetterTacMap: the ETA postfix targets the beta SceneMapViewModel constructor");
        Check(targets["ModDrawingSavePatch.Postfix"].GetParameters().Select(p=>p.ParameterType).SequenceEqual(new[] { typeof(IniHandler), typeof(MapDrawingLayer) }),
            "BetterTacMap: the save patches target WriteDrawingData(IniHandler, MapDrawingLayer)");
        // SameTaskforceContextMenuPatch.Apply patches by hand: AccessTools.Method(UnitSelectedState, "HandleUnit").
        var handle=AccessTools.Method(AccessTools.TypeByName("SeapowerUI.ViewModels.UnitSelectedState"),"HandleUnit");
        Check(handle!=null,"BetterTacMap: UnitSelectedState.HandleUnit resolves for the manual patch");
        BetterTacMapBinds(P("SameTaskforceContextMenuPatch").GetMethod("Postfix",all),handle);

        // Bridges: the internal members they bind, and native results on fixtures.
        var holder=typeof(BetaCompatibilityCalls).GetNestedType("BetterTacMapNative",BindingFlags.NonPublic);
        object H(string name) => holder.GetField(name,BindingFlags.NonPublic|BindingFlags.Static).GetValue(null);
        var entry=(Type)H("Entry"); var entryCtor=(ConstructorInfo)H("EntryCtor"); var layerCtor=(ConstructorInfo)H("LayerCtor");
        Check(entry.IsValueType && entry.IsNestedAssembly && entry.DeclaringType==typeof(GizmoLayerManager),"BetterTacMap bridge: Entry is beta's internal GizmoLayerManager.Entry");
        var native=PatchProcessor.GetOriginalInstructions(typeof(MapDisplayState).GetConstructor(BindingFlags.Instance|BindingFlags.NonPublic|BindingFlags.Public,null,new[] { typeof(bool) },null));
        Check(native.Count(i=>i.opcode==OpCodes.Newobj && i.operand is ConstructorInfo c && c.DeclaringType==typeof(MapLayer))==1 &&
            native.Single(i=>i.opcode==OpCodes.Newobj && i.operand is ConstructorInfo c && c.DeclaringType==typeof(MapLayer)).operand.Equals(layerCtor),
            "BetterTacMap bridge: builds layers with the constructor beta's MapDisplayState uses");
        var e=entryCtor.Invoke(new object[] { 505, "BETTERMINIMAP_DISTRESS", true });
        Check((int)entry.GetField("Number").GetValue(e)==505 && (string)entry.GetField("Name").GetValue(e)=="BETTERMINIMAP_DISTRESS" && (bool)entry.GetField("InMenu").GetValue(e),
            "BetterTacMap bridge: Entry carries the stable (layerNumber, name, visibleInMenu)");
        bool threw=false;
        try { BetaCompatibilityCalls.BetterTacMapNewLayer(500,"BETTERMINIMAP_DEPTH",true,null); } catch (ArgumentNullException) { threw=true; }
        Check(threw,"BetterTacMap bridge: a layer without its Tactical owner is refused");
        BetterTacMapLine3Fixture();
    }

    // HarmonyX binds a patch parameter by the original's parameter name, or as
    // __instance, __result, __state, ___field or one of its special names.
    static void BetterTacMapBinds(MethodInfo patch, MethodBase target)
    {
        foreach (var parameter in patch.GetParameters()) {
            var type=parameter.ParameterType.IsByRef ? parameter.ParameterType.GetElementType() : parameter.ParameterType;
            bool ok=parameter.Name switch {
                "__instance" => !target.IsStatic && type.IsAssignableFrom(target.DeclaringType),
                "__result" => target is MethodInfo method && method.ReturnType!=typeof(void) && (type==method.ReturnType || type.IsAssignableFrom(method.ReturnType)),
                "__state" or "__exception" or "__originalMethod" or "__runOriginal" or "__args" => true,
                string name when name.StartsWith("___") => AccessTools.Field(target.DeclaringType,name.Substring(3)) is FieldInfo field && type.IsAssignableFrom(field.FieldType),
                _ => target.GetParameters().SingleOrDefault(p=>p.Name==parameter.Name) is ParameterInfo match &&
                    (match.ParameterType==parameter.ParameterType || match.ParameterType==type || type.IsAssignableFrom(match.ParameterType)),
            };
            Check(ok,"BetterTacMap: "+patch.DeclaringType.Name+"."+patch.Name+" parameter "+parameter.Name+" binds to "+target.DeclaringType.Name+"."+target.Name);
        }
    }

    // Native line-3 visibility (UpdateContactInfoLine3 IL_0000-0030), run as
    // the real beta IL up to its stloc.2, against the bridge on fixtures.
    static void BetterTacMapLine3Fixture()
    {
        var update=typeof(MapUnitViewModel).GetMethod("UpdateContactInfoLine3",BindingFlags.Instance|BindingFlags.NonPublic|BindingFlags.Public);
        var method=new DynamicMethod("BetterTacMapNativeLine3",typeof(bool),new[] { typeof(MapUnitViewModel) },typeof(MapUnitViewModel),true);
        var il=method.GetILGenerator(); int copied=0;
        foreach (var instruction in PatchProcessor.GetOriginalInstructions(update,il)) {
            foreach (var mark in instruction.labels) il.MarkLabel(mark);
            if (instruction.opcode==OpCodes.Stloc_2) { il.Emit(OpCodes.Ret); break; }
            if (instruction.operand==null || instruction.opcode.OperandType==System.Reflection.Emit.OperandType.InlineNone) il.Emit(instruction.opcode);
            else if (instruction.operand is FieldInfo field) il.Emit(instruction.opcode,field);
            else if (instruction.operand is Label target) il.Emit(instruction.opcode,target);
            else if (instruction.operand is LocalBuilder local) il.Emit(instruction.opcode,local);
            else throw new Exception("Uninspected native line-3 operand: "+instruction.operand);
            copied++;
        }
        Check(copied==25,"BetterTacMap: native line-3 visibility prefix copied (actual="+copied+")");
        var shown=(Func<MapUnitViewModel,bool>)method.CreateDelegate(typeof(Func<MapUnitViewModel,bool>));
        const BindingFlags fields=BindingFlags.Instance|BindingFlags.NonPublic|BindingFlags.Public;
        void Set(object owner, string name, object value) => owner.GetType().GetField(name,fields).SetValue(owner,value);
        object Get(object owner, string name) => owner.GetType().GetField(name,fields).GetValue(owner);
        var view=(MapUnitViewModel)FormatterServices.GetUninitializedObject(typeof(MapUnitViewModel));
        var label=(MapLabelCandidate)FormatterServices.GetUninitializedObject(typeof(MapLabelCandidate));
        var head=(MapLabelLine)FormatterServices.GetUninitializedObject(typeof(MapLabelLine));
        int cases=0;
        foreach (bool hasLabel in new[] { false, true }) foreach (bool realized in new[] { false, true })
        foreach (bool hasHead in new[] { false, true }) foreach (int prefix in new[] { 0, 2, 3, 4 }) {
            Set(view,"Label",hasLabel ? label : null); Set(label,"Realized",realized); Set(label,"HeadLine",hasHead ? head : null); Set(label,"Prefix",prefix);
            if (shown(view)!=BetaCompatibilityCalls.BetterTacMapLine3Shown(view)) throw new Exception("Line-3 visibility differs from native: "+hasLabel+realized+hasHead+prefix);
            cases++;
        }
        Check(cases==32,"BetterTacMap bridge: line-3 visibility equals the native beta IL on all 32 fixtures");

        void Stale() { Set(view,"_line3Initialized",true); Set(view,"_contactInfoLine3","Depth: 120 ft"); }
        bool Cleared() => !(bool)Get(view,"_line3Initialized") && Get(view,"_contactInfoLine3")==null;
        Set(view,"Label",label); Set(label,"Realized",true); Set(label,"HeadLine",null); Set(label,"Prefix",3); Stale();
        Check(BetaCompatibilityCalls.BetterTacMapRefreshLine3At(view,10) && Cleared(),
            "BetterTacMap bridge: a shown line 3 clears _line3Initialized and _contactInfoLine3, so the next Update rebuilds it");
        Stale();
        Check(!BetaCompatibilityCalls.BetterTacMapRefreshLine3At(view,10.4) && !Cleared(),"BetterTacMap bridge: no second refresh within 0.5 s");
        Check(BetaCompatibilityCalls.BetterTacMapRefreshLine3At(view,10.5) && Cleared(),"BetterTacMap bridge: refreshes again after 0.5 s");
        Set(label,"Realized",false); Stale();
        Check(!BetaCompatibilityCalls.BetterTacMapRefreshLine3At(view,20) && !Cleared(),"BetterTacMap bridge: a hidden line 3 is left to the native suppression");
        Set(view,"Label",null); Stale();
        Check(!BetaCompatibilityCalls.BetterTacMapRefreshLine3At(view,30) && !Cleared(),"BetterTacMap bridge: a view without a label is left alone");
        Check(!BetaCompatibilityCalls.BetterTacMapRefreshLine3At(null,40),"BetterTacMap bridge: a null view is ignored");
        // BuilderEquals(builder, null) is false, so the cleared text forces set_ContactInfoLine3.
        var equals=typeof(MapUnitViewModel).GetMethod("BuilderEquals",BindingFlags.Static|BindingFlags.NonPublic|BindingFlags.Public);
        Check(!(bool)equals.Invoke(null,new object[] { new System.Text.StringBuilder(""), null }) &&
            (bool)equals.Invoke(null,new object[] { new System.Text.StringBuilder("Depth: 120 ft"), "Depth: 120 ft" }),
            "BetterTacMap: native BuilderEquals treats the cleared text as changed");
    }
}
