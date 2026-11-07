using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using System.Security.Cryptography;
using AnchorChain;
using HarmonyLib;
using Mono.Cecil;
using SeaPower;

// R6: OspreyMechanics 1.1.45 and its dependant OspreyDeckOps 1.1.36 (Workshop
// 3806466625). Metadata, reflection and bridge checks only: no plugin entry
// point runs, no Harmony patch is applied and no Unity gameplay is simulated.
static partial class BetaApiTests
{
    // Stands in for an ObjectBase in the bridge fixtures: the unit's SpeedState
    // (ObjectBase.Speed), the value ObjectBase.SpeedCommand holds, and beta
    // SetSpeedCommand(in SpeedRequest) with the plugin's prefix and postfix.
    public sealed class OspreyTestUnit
    {
        public readonly SpeedState State = new SpeedState();
        public ISpeedCommand Value;
        public int Notified;
        public OspreyHook Prefix, Postfix;
        public ISpeedCommand PrefixSaw, PostfixSaw;
        public SpeedState GetSpeed() => State;
        // Beta ObjectBase.SetSpeedCommand(in SpeedRequest request) (rid 32930):
        // Speed.ClearOverride(); if (!Speed.Apply(ref request, this)) return;
        // SpeedCommand.SetValueAndForceNotify(Speed). Harmony runs the postfix
        // on the early return too.
        public void SetSpeedCommand(ref SpeedRequest request)
        {
            if (Prefix != null) PrefixSaw = Prefix(this, ref request);
            State.ClearOverride();
            if (State.Apply(ref request, null)) { Value = State; Notified++; }
            if (Postfix != null) PostfixSaw = Postfix(this, ref request);
        }
    }
    public delegate ISpeedCommand OspreyHook(OspreyTestUnit unit, ref SpeedRequest request);
    public delegate void OspreySet(OspreyTestUnit unit, ISpeedCommand command);
    public delegate ISpeedCommand OspreyRead(OspreyTestUnit unit, ISpeedCommand current);

    const string OspreyMechanicsPin = "2349def7bf71a7df1f87b387645e4e146f66ba9bc6869a3e5001187a0a7ae98b";
    const string OspreyDeckOpsPin = "1ad2dfa167add7289e9038dd48d12bc129c7b3336af70cfa591912be6064f135";

    static string OspreySha(string path)
    {
        using var sha=SHA256.Create(); using var stream=File.OpenRead(path);
        return BitConverter.ToString(sha.ComputeHash(stream)).Replace("-","").ToLowerInvariant();
    }

    static void R6_OspreyMechanics(R6Context context)
    {
        const BindingFlags all=BindingFlags.NonPublic|BindingFlags.Public|BindingFlags.Static|BindingFlags.Instance|BindingFlags.DeclaredOnly;
        string source=Path.Combine(context.Workshop,"3806466625/OspreyMechanics.dll");
        string deck=Path.Combine(context.Workshop,"3806466625/OspreyDeckOps.dll");
        byte[] bytes=File.ReadAllBytes(source), deckBytes=File.ReadAllBytes(deck);
        Check(OspreySha(source)==OspreyMechanicsPin && OspreySha(deck)==OspreyDeckOpsPin, "Osprey fixture is the captured 3 Nov 2026 pair");

        // Policy: the image is adapted in the private cache with its exact audit.
        var adapterMethod=typeof(BetaAssemblyPolicy).GetMethod("OspreyMechanicsAdapter",BindingFlags.NonPublic|BindingFlags.Static);
        object adapter=adapterMethod.Invoke(null,null);
        string expected=(string)adapter.GetType().GetField("ExpectedAudit",BindingFlags.NonPublic|BindingFlags.Instance).GetValue(adapter);
        Check(expected=="hook-argument=2, hook-load=4, speed-field=2, speed-knots=2, speed-local=1, speed-make=5, speed-read=6, speed-set=5, speed-snapshot=1, speed-target=2",
            "OspreyMechanics expected audit is the reviewed one");
        var log=new List<string>();
        string adapted=BetaAssemblyPolicy.Prepare(source,context.Native,context.Cache,log.Add);
        foreach (string line in log) Console.WriteLine(line);
        Check(adapted!=null && adapted!=source && File.Exists(adapted), "Private OspreyMechanics image generated");
        Check(bytes.SequenceEqual(File.ReadAllBytes(source)), "OspreyMechanics author bytes retained");
        Check(log.Count==1 && log[0]=="ADAPTED OspreyMechanics in private cache: "+expected+"; original Workshop DLL and asset paths preserved.",
            "OspreyMechanics logged audit equals the adapter's ExpectedAudit");
        var deckLog=new List<string>();
        string deckPrepared=BetaAssemblyPolicy.Prepare(deck,context.Native,context.Cache,deckLog.Add);
        Check(deckPrepared==deck && deckLog.Count==0 && deckBytes.SequenceEqual(File.ReadAllBytes(deck)),
            "OspreyDeckOps is released unchanged from its Workshop path once OspreyMechanics is adapted");

        // Layout: exactly the two accepted findings before, none after.
        var invalid=typeof(BetaAssemblyPolicy).GetMethod("InvalidNativeFields",BindingFlags.NonPublic|BindingFlags.Static);
        var accepted=(string[])adapter.GetType().GetField("AcceptedNativeFields",BindingFlags.NonPublic|BindingFlags.Instance).GetValue(adapter);
        using (var game=ModuleDefinition.ReadModule(context.Native))
        using (var original=ModuleDefinition.ReadModule(source))
        using (var written=ModuleDefinition.ReadModule(adapted))
        using (var deckModule=ModuleDefinition.ReadModule(deck)) {
            var before=(List<string>)invalid.Invoke(null,new object[] { original,game });
            Check(before.OrderBy(x=>x,StringComparer.Ordinal).SequenceEqual(accepted.OrderBy(x=>x,StringComparer.Ordinal)),
                "Captured image has exactly the two accepted ConstantSpeed field findings");
            Check(((List<string>)invalid.Invoke(null,new object[] { written,game })).Count==0, "Adapted image has no class/struct field mismatch");
            Check(((List<string>)invalid.Invoke(null,new object[] { deckModule,game })).Count==0, "OspreyDeckOps has no class/struct field mismatch");
        }

        using var resolver=new DefaultAssemblyResolver();
        resolver.AddSearchDirectory(Path.GetDirectoryName(context.Native));
        resolver.AddSearchDirectory(Path.GetDirectoryName(typeof(BetaAssemblyPolicy).Assembly.Location));
        resolver.AddSearchDirectory(Path.GetDirectoryName(adapted));
        using (var image=ModuleDefinition.ReadModule(adapted,new ReaderParameters { AssemblyResolver=resolver })) {
            OspreyRewriteChecks(image);
            // Every Seapower-Scripts method and field operand binds to the beta.
            foreach (var (name,module) in new[] { ("OspreyMechanics",image), ("OspreyDeckOps",ModuleDefinition.ReadModule(deck,new ReaderParameters { AssemblyResolver=resolver })) }) {
                var missing=new List<string>(); int resolved=0, sibling=0;
                foreach (var type in Types(module.Types)) foreach (var method in type.Methods.Where(m=>m.HasBody))
                    foreach (var instruction in method.Body.Instructions) {
                        var member=instruction.Operand as MemberReference;
                        if (member?.DeclaringType?.Scope is not AssemblyNameReference scope ||
                            (scope.Name!="Seapower-Scripts" && scope.Name!="OspreyMechanics")) continue;
                        if (member is not MethodReference && member is not FieldReference) continue;
                        try {
                            object definition=member is MethodReference call ? (object)call.Resolve() : ((FieldReference)member).Resolve();
                            if (definition==null) throw new Exception("unresolved");
                            if (scope.Name=="OspreyMechanics") sibling++; else resolved++;
                        } catch (Exception ex) { missing.Add(name+"/"+method.Name+": "+member.FullName+" "+ex.Message); }
                    }
                foreach (string failure in missing) Console.WriteLine("MISSING "+failure);
                Check(missing.Count==0 && resolved>(name=="OspreyMechanics" ? 150 : 50) && (name=="OspreyMechanics" || sibling>0),
                    name+" native operands resolve against beta Build 261026 ("+resolved+" native, "+sibling+" OspreyMechanics)");
                if (name=="OspreyDeckOps") module.Dispose();
            }
        }

        // Reflection on the loaded private image.
        var loaded=Assembly.LoadFile(adapted);
        Check(BetaAssemblyPolicy.OriginalLocation(loaded)==source, "OspreyMechanics asset provenance is its Workshop path");
        foreach (string name in new[] { "OspreyRig.AutoHoverState", "OspreyRig.DipState" })
            Check(loaded.GetType(name,true).GetField("Command",BindingFlags.NonPublic|BindingFlags.Instance)?.FieldType==typeof(ISpeedCommand), name+".Command lays out as the beta ISpeedCommand");
        var hover=loaded.GetType("OspreyRig.HoverFlight",true); var sonar=loaded.GetType("OspreyRig.DippingSonar",true);
        var bridges=typeof(BetaCompatibilityCalls).GetMethods(BindingFlags.Public|BindingFlags.Static).Where(m=>m.Name.StartsWith("OspreyMechanics",StringComparison.Ordinal)).ToList();
        foreach (var (type,name,bridge,count) in new[] {
            (hover,"Order","OspreyMechanicsSetSpeedCommand",1), (hover,"SetAutoSpeed","OspreyMechanicsConstantSpeed",1), (hover,"OwnsSpeed","OspreyMechanicsSpeedCommand",1),
            (hover,"ClearAuto","OspreyMechanicsSetSpeedCommand",1), (hover,"WaypointUpdating","OspreyMechanicsSpeedCommand",2),
            (hover,"WaypointFinished","OspreyMechanicsSpeedCommand",2), (hover,"Install","OspreyMechanicsMethod",1),
            (hover,"SpeedCommandChanged","OspreyMechanicsIncomingSpeedCommand",3), (sonar,"OwnsSpeed","OspreyMechanicsSpeedCommand",1),
            (sonar,"Speed","OspreyMechanicsConstantSpeed",1), (sonar,"Restore","OspreyMechanicsSetSpeedCommand",1),
            (sonar,"WaypointUpdating","OspreyMechanicsSpeedSnapshot",1), (sonar,"Install","OspreyMechanicsMethod",1),
            (sonar,"SpeedCommandChanging","OspreyMechanicsIncomingSpeedCommand",1) }) {
            var method=type.GetMethods(all).Single(m=>m.Name==name);
            var body=PatchProcessor.GetOriginalInstructions(method);
            Check(body.Count(i=>Equals(i.operand,bridges.Single(b=>b.Name==bridge)))==count &&
                body.All(i=>(i.operand as MethodBase)?.DeclaringType?.FullName!="SeaPower.ConstantSpeed"),
                "Loaded "+type.Name+"."+name+" binds "+count+" x "+bridge+" and no ConstantSpeed member");
        }

        // HarmonyX binds patch parameters by the original's names. The author's
        // stable lookups fail on the beta exactly as captured; the bridge finds
        // SetSpeedCommand(in SpeedRequest request).
        bool ambiguous=false;
        try { AccessTools.Method(typeof(ObjectBase),"SetSpeedCommand",null,null); } catch (AmbiguousMatchException) { ambiguous=true; }
        Check(ambiguous && AccessTools.Method(typeof(ObjectBase),"SetSpeedCommand",new[] { typeof(ISpeedCommand) },null)==null,
            "The author's stable SetSpeedCommand lookups fail on the beta, as captured");
        var target=BetaCompatibilityCalls.OspreyMechanicsMethod(typeof(ObjectBase),"SetSpeedCommand",null,null);
        Check(target!=null && target==BetaCompatibilityCalls.OspreyMechanicsMethod(typeof(ObjectBase),"SetSpeedCommand",new[] { typeof(ISpeedCommand) },null) &&
            !target.IsGenericMethodDefinition && target.DeclaringType==typeof(ObjectBase) && target.GetParameters().Length==1 &&
            target.GetParameters()[0].Name=="request" && target.GetParameters()[0].ParameterType==typeof(SpeedRequest).MakeByRefType(),
            "Both SetSpeedCommand lookups resolve to beta SetSpeedCommand(in SpeedRequest request)");
        Check(BetaCompatibilityCalls.OspreyMechanicsMethod(typeof(FixedWingFlightPhysics),"GetMaxClimbPitch",null,null)==
                AccessTools.Method(typeof(FixedWingFlightPhysics),"GetMaxClimbPitch",null,null) &&
            BetaCompatibilityCalls.OspreyMechanicsMethod(typeof(GoToWaypointTask),"OnUpdate",null,null)==AccessTools.Method(typeof(GoToWaypointTask),"OnUpdate",null,null),
            "Other lookups pass through the bridge unchanged");
        foreach (var hook in new[] { hover.GetMethod("SpeedCommandChanged",all), sonar.GetMethod("SpeedCommandChanging",all) }) {
            Check(hook.GetParameters().Select(p=>p.Name).SequenceEqual(new[] { "__instance","request" }), hook.Name+" parameters are __instance, request");
            foreach (var parameter in hook.GetParameters()) {
                var match=target.GetParameters().SingleOrDefault(p=>p.Name==parameter.Name);
                Check(parameter.Name=="__instance" ? parameter.ParameterType.IsAssignableFrom(target.DeclaringType) :
                    match!=null && match.ParameterType==parameter.ParameterType, hook.Name+" parameter binds by name: "+parameter.Name);
            }
        }

        // OspreyDeckOps' OspreyMechanics references bind to the loaded private
        // image (by name, as Anchor Chain's LoadFile order has it in the game).
        var deckAssembly=Assembly.LoadFile(deck);
        var entry=deckAssembly.GetType("OspreyDeckOps.Mod",true).GetMethod("TriggerEntryPoint",all);
        var clock=PatchProcessor.GetOriginalInstructions(entry).Select(i=>i.operand as MethodInfo).Single(m=>m?.DeclaringType?.FullName=="OspreyRig.GameClock");
        Check(clock.DeclaringType.Assembly==loaded, "OspreyDeckOps binds OspreyRig.GameClock in the adapted OspreyMechanics image");
        Check(AppDomain.CurrentDomain.GetAssemblies().Count(a=>a.GetName().Name=="OspreyMechanics")==1, "Exactly one OspreyMechanics assembly is loaded");

        OspreyBridgeFixtures();
    }

    // Each rewrite's IL in the written image, by the methods it targets.
    static void OspreyRewriteChecks(ModuleDefinition image)
    {
        bool Bridge(Mono.Cecil.Cil.Instruction i, string name) => i.OpCode==Mono.Cecil.Cil.OpCodes.Call && i.Operand is MethodReference r &&
            r.DeclaringType.FullName=="AnchorChain.BetaCompatibilityCalls" && r.Name==name;
        MethodDefinition Method(string type, string name) => image.GetType(type).Methods.Single(m=>m.Name==name);
        var hover="OspreyRig.HoverFlight"; var sonar="OspreyRig.DippingSonar";
        Check(!image.GetTypeReferences().Any(t=>t.FullName=="SeaPower.ConstantSpeed") &&
            !image.GetMemberReferences().Any(m=>m.DeclaringType.FullName=="SeaPower.ConstantSpeed" ||
                (m.Name=="SetSpeedCommand" && m is MethodReference r && r.Parameters.Any(p=>p.ParameterType.FullName=="SeaPower.ISpeedCommand"))),
            "Adapted image has no ConstantSpeed or SetSpeedCommand(ISpeedCommand) reference");
        foreach (string type in new[] { "OspreyRig.AutoHoverState", "OspreyRig.DipState" })
            Check(image.GetType(type).Fields.Single(f=>f.Name=="Command").FieldType.FullName=="SeaPower.ISpeedCommand", type+".Command is ISpeedCommand");
        Check(Method(hover,"SetAutoSpeed").Body.Variables.Single().VariableType.FullName=="SeaPower.ISpeedCommand", "SetAutoSpeed local is ISpeedCommand");
        var counts=new Dictionary<string,int>();
        foreach (var type in Types(image.Types)) foreach (var method in type.Methods.Where(m=>m.HasBody)) foreach (var i in method.Body.Instructions)
            if (i.Operand is MethodReference r && r.DeclaringType.FullName=="AnchorChain.BetaCompatibilityCalls")
                counts[type.FullName+"::"+method.Name+"/"+r.Name]=counts.TryGetValue(type.FullName+"::"+method.Name+"/"+r.Name,out int n) ? n+1 : 1;
        var expected=new Dictionary<string,int> {
            [hover+"::Order/OspreyMechanicsConstantSpeed"]=1, [hover+"::Order/OspreyMechanicsSetSpeedCommand"]=1,
            [hover+"::SetAutoSpeed/OspreyMechanicsConstantSpeed"]=1, [hover+"::SetAutoSpeed/OspreyMechanicsSetSpeedCommand"]=1,
            [hover+"::ClearAuto/OspreyMechanicsConstantSpeed"]=1, [hover+"::ClearAuto/OspreyMechanicsSetSpeedCommand"]=1,
            [hover+"::OwnsSpeed/OspreyMechanicsSpeedCommand"]=1, [hover+"::WaypointUpdating/OspreyMechanicsSpeedCommand"]=2,
            [hover+"::WaypointFinished/OspreyMechanicsSpeedCommand"]=2, [hover+"::Install/OspreyMechanicsMethod"]=1,
            [hover+"::SpeedCommandChanged/OspreyMechanicsIncomingSpeedCommand"]=3,
            [sonar+"::OwnsSpeed/OspreyMechanicsSpeedCommand"]=1, [sonar+"::Speed/OspreyMechanicsConstantSpeed"]=1,
            [sonar+"::Speed/OspreyMechanicsSetSpeedCommand"]=1, [sonar+"::Restore/OspreyMechanicsSetSpeedCommand"]=1,
            [sonar+"::WaypointUpdating/OspreyMechanicsSpeedSnapshot"]=1, [sonar+"::WaypointUpdating/OspreyMechanicsConstantSpeed"]=1,
            [sonar+"::Install/OspreyMechanicsMethod"]=1, [sonar+"::SpeedCommandChanging/OspreyMechanicsIncomingSpeedCommand"]=1 };
        Check(counts.Count==expected.Count && expected.All(e=>counts.TryGetValue(e.Key,out int n) && n==e.Value),
            "Exactly the 23 audited bridge calls, in exactly the targeted methods ("+String.Join(", ",counts.Select(c=>c.Key+"="+c.Value))+")");
        // read/snapshot: unit; dup; get_SpeedCommand; get_Value; call bridge(unit, value)
        int reads=0;
        foreach (var type in new[] { hover, sonar }) foreach (var method in image.GetType(type).Methods.Where(m=>m.HasBody))
            foreach (var i in method.Body.Instructions.Where(i=>Bridge(i,"OspreyMechanicsSpeedCommand") || Bridge(i,"OspreyMechanicsSpeedSnapshot"))) {
                var value=i.Previous; var property=value?.Previous; var dup=property?.Previous;
                Check(value?.OpCode==Mono.Cecil.Cil.OpCodes.Callvirt && ((MethodReference)value.Operand).Name=="get_Value" &&
                    property?.OpCode==Mono.Cecil.Cil.OpCodes.Callvirt && ((MethodReference)property.Operand).Name=="get_SpeedCommand" &&
                    dup?.OpCode==Mono.Cecil.Cil.OpCodes.Dup, "Native SpeedCommand.Value read feeds its bridge: "+method.Name);
                reads++;
            }
        Check(reads==7, "Seven native SpeedCommand.Value reads are bridged");
        foreach (var (type,name) in new[] { (hover,"OwnsSpeed"), (sonar,"OwnsSpeed") })
            Check(Method(type,name).Body.Instructions.Count(i=>i.Operand is MethodReference r && r.DeclaringType.FullName=="SeaPower.ISpeedCommand" &&
                r.Name=="get_SpeedInKnots")==1, type+".OwnsSpeed reads ISpeedCommand.SpeedInKnots");
        foreach (var (type,name,loads) in new[] { (hover,"SpeedCommandChanged",3), (sonar,"SpeedCommandChanging",1) }) {
            var hook=Method(type,name);
            Check(hook.Parameters[1].Name=="request" && hook.Parameters[1].ParameterType.FullName=="SeaPower.SpeedRequest&" &&
                hook.Body.Instructions.Where(i=>Bridge(i,"OspreyMechanicsIncomingSpeedCommand")).All(i=>i.Previous.OpCode==Mono.Cecil.Cil.OpCodes.Ldarg_1 &&
                    i.Previous.Previous.OpCode==Mono.Cecil.Cil.OpCodes.Ldarg_0) &&
                hook.Body.Instructions.Count(i=>i.OpCode==Mono.Cecil.Cil.OpCodes.Ldarg_1)==loads, name+" loads request only through its bridge");
        }
        var changed=Method(hover,"SpeedCommandChanged");
        Check(changed.Body.ExceptionHandlers.Count==2 && changed.Body.ExceptionHandlers[1].TryStart.OpCode==Mono.Cecil.Cil.OpCodes.Ldarg_0 &&
            Bridge(changed.Body.ExceptionHandlers[1].TryStart.Next.Next,"OspreyMechanicsIncomingSpeedCommand"), "SpeedCommandChanged's second try still starts at its request load");
        foreach (var (type,ldstr) in new[] { (hover,"Install"), (sonar,"Install") }) {
            var lookup=Method(type,ldstr).Body.Instructions.Single(i=>Bridge(i,"OspreyMechanicsMethod"));
            var name=Method(type,ldstr).Body.Instructions.Where(i=>i.OpCode==Mono.Cecil.Cil.OpCodes.Ldstr && Equals(i.Operand,"SetSpeedCommand")).ToList();
            Check(name.Count==1 && lookup.Offset>name[0].Offset && lookup.Offset-name[0].Offset<=0x1b, type+".Install's SetSpeedCommand lookup uses the bridge");
        }
    }

    // Execute the ACTUAL compiled bridge IL with its ObjectBase operands
    // (get_Speed, SetSpeedCommand(in SpeedRequest)) rebound to OspreyTestUnit.
    // SpeedState, SpeedRequest and ConstantSpeed are the real beta types.
    static T OspreyRebind<T>(string name, ref int rebound) where T : Delegate
    {
        var bridge=typeof(BetaCompatibilityCalls).GetMethod(name,BindingFlags.Public|BindingFlags.Static);
        var invoke=typeof(T).GetMethod("Invoke");
        var method=new DynamicMethod(name+"Fixture",invoke.ReturnType,invoke.GetParameters().Select(p=>p.ParameterType).ToArray(),typeof(BetaApiTests),true);
        var il=method.GetILGenerator();
        foreach (var instruction in PatchProcessor.GetOriginalInstructions(bridge,il)) {
            foreach (var label in instruction.labels) il.MarkLabel(label);
            foreach (var block in instruction.blocks) {
                if (block.blockType==ExceptionBlockType.BeginExceptionBlock) il.BeginExceptionBlock();
                else if (block.blockType==ExceptionBlockType.BeginFinallyBlock) il.BeginFinallyBlock();
                else if (block.blockType!=ExceptionBlockType.EndExceptionBlock) throw new Exception("Uninspected bridge exception block: "+block.blockType);
            }
            var opcode=instruction.opcode; object operand=instruction.operand;
            if (opcode.OperandType==OperandType.ShortInlineBrTarget)
                opcode=(OpCode)typeof(OpCodes).GetField(opcode.Name.Replace(".s","").Replace(".","_"),BindingFlags.Public|BindingFlags.Static|BindingFlags.IgnoreCase).GetValue(null);
            if (operand is MethodInfo call && call.DeclaringType==typeof(ObjectBase)) {
                operand=call.Name=="get_Speed" ? typeof(OspreyTestUnit).GetMethod("GetSpeed") :
                    call.Name=="SetSpeedCommand" && call.GetParameters()[0].ParameterType==typeof(SpeedRequest).MakeByRefType() ? typeof(OspreyTestUnit).GetMethod("SetSpeedCommand") :
                    throw new Exception("Uninspected ObjectBase member in "+name+": "+call);
                rebound++;
            }
            if (opcode.OperandType==OperandType.InlineNone) il.Emit(opcode);
            else if (operand is MethodInfo target) il.Emit(opcode,target);
            else if (operand is ConstructorInfo constructor) il.Emit(opcode,constructor);
            else if (operand is FieldInfo field) il.Emit(opcode,field);
            else if (operand is Type type) il.Emit(opcode,type);
            else if (operand is Label targetLabel) il.Emit(opcode,targetLabel);
            else if (operand is LocalBuilder local) il.Emit(opcode,local);
            else if (operand is string text) il.Emit(opcode,text);
            else if (operand is float single) il.Emit(opcode,single);
            else if (operand is int number) il.Emit(opcode,number);
            else if (operand is sbyte small) il.Emit(opcode,small);
            else if (operand is byte index) il.Emit(opcode,index);
            else if (operand is short wide) il.Emit(opcode,wide);
            else throw new Exception("Uninspected bridge operand in "+name+": "+opcode+" "+operand);
            foreach (var block in instruction.blocks) if (block.blockType==ExceptionBlockType.EndExceptionBlock) il.EndExceptionBlock();
        }
        return (T)method.CreateDelegate(typeof(T));
    }

    static void OspreyBridgeFixtures()
    {
        // Constant speed: beta ConstantSpeed(k, unit).ToRequest() is Knots(k).
        foreach (float knots in new[] { 0f, 10f, 17.25f, 80f }) {
            var order=(BetaCompatibilityCalls.OspreyMechanicsSpeedOrder)BetaCompatibilityCalls.OspreyMechanicsConstantSpeed(knots,null);
            Check(order.Request.Equals(new ConstantSpeed(knots,null).ToRequest()) && order.Kind==SpeedKind.Constant && order.SpeedInKnots==knots &&
                order.GetDemandedSpeedInKnots(null)==knots, "Constant-speed order carries native ConstantSpeed.ToRequest() for "+knots+" kt");
        }
        // The real SpeedState semantics the ownership test relies on.
        var native=new SpeedState(); var twelve=SpeedRequest.Knots(12f);
        Check(native.Apply(ref twelve,null) && native.Request.Equals(SpeedRequest.Knots(12f)) && !native.Apply(ref twelve,null) &&
            native.GetDemandedSpeedInKnots(null)==12f, "Beta SpeedState stores the request as given and ignores an equal one");

        int rebound=0;
        var set=OspreyRebind<OspreySet>("OspreyMechanicsSetSpeedCommand",ref rebound);
        var read=OspreyRebind<OspreyRead>("OspreyMechanicsSpeedCommand",ref rebound);
        var snapshot=OspreyRebind<OspreyRead>("OspreyMechanicsSpeedSnapshot",ref rebound);
        var incoming=OspreyRebind<OspreyHook>("OspreyMechanicsIncomingSpeedCommand",ref rebound);
        Check(rebound==2, "Fixture rebinds exactly SetSpeedCommand(in SpeedRequest) and get_Speed (actual="+rebound+")");
        ISpeedCommand Make(float knots) => BetaCompatibilityCalls.OspreyMechanicsConstantSpeed(knots,null);

        var unit=new OspreyTestUnit { Prefix=incoming, Postfix=incoming };
        Check(read(unit,unit.Value)==null && snapshot(unit,unit.Value)==null, "Before any order the native null value passes through");
        var hover=Make(30f); set(unit,hover);
        Check(unit.Value==unit.State && unit.State.Request.Equals(SpeedRequest.Knots(30f)) && unit.Notified==1,
            "Plugin order goes through native SetSpeedCommand(in SpeedRequest)");
        Check(ReferenceEquals(unit.PrefixSaw,hover) && ReferenceEquals(unit.PostfixSaw,hover), "Both hooks see the plugin's own in-flight order");
        Check(ReferenceEquals(read(unit,unit.Value),hover), "Plugin owns the speed after its own order (stable ReferenceEquals holds)");
        var again=Make(30f); set(unit,again);
        Check(unit.Notified==1 && ReferenceEquals(read(unit,unit.Value),again) && ReferenceEquals(unit.PrefixSaw,again),
            "An equal plugin order changes no native state and the newest order owns the speed");
        var foreign=SpeedRequest.Knots(30f); unit.SetSpeedCommand(ref foreign);
        Check(ReferenceEquals(unit.PrefixSaw,unit.State) && ReferenceEquals(unit.PostfixSaw,unit.State) && ReferenceEquals(read(unit,unit.Value),unit.State),
            "A foreign identical order seen by the hooks ends ownership, as stable's replacement did");
        var dip=Make(12f); set(unit,dip);
        unit.Prefix=null; unit.Postfix=null;
        var player=SpeedRequest.Knots(50f); unit.SetSpeedCommand(ref player);
        Check(ReferenceEquals(read(unit,unit.Value),unit.State), "A foreign different order ends ownership by value");
        var resume=snapshot(unit,unit.Value);
        Check(resume is BetaCompatibilityCalls.OspreyMechanicsSpeedOrder captured && captured.Request.Equals(SpeedRequest.Knots(50f)) &&
            resume.GetDemandedSpeedInKnots(null)==unit.State.GetDemandedSpeedInKnots(null), "Snapshot captures the native request and demanded knots");
        unit.Prefix=incoming; unit.Postfix=incoming;
        var hold=Make(0f); set(unit,hold);
        Check(ReferenceEquals(snapshot(unit,unit.Value),hold), "Snapshot of a plugin-owned speed is the plugin's order itself");
        set(unit,resume);
        Check(unit.State.Request.Equals(SpeedRequest.Knots(50f)) && ReferenceEquals(read(unit,unit.Value),resume), "Re-applied snapshot restores the native request");
        var stop=SpeedRequest.Stop(); unit.SetSpeedCommand(ref stop);
        Check(ReferenceEquals(unit.PostfixSaw,unit.State) && unit.PostfixSaw.GetDemandedSpeedInKnots(null)==0f && read(unit,unit.Value)==unit.State,
            "A native stop reaches the postfix as the unit's SpeedState with 0 kt");
        var other=new OspreyTestUnit(); set(other,Make(20f));
        Check(read(unit,unit.Value)==unit.State && read(other,other.Value) is BetaCompatibilityCalls.OspreyMechanicsSpeedOrder, "Ownership is per unit");
        bool rejected=false;
        try { set(unit,unit.State); } catch (ArgumentException) { rejected=true; }
        Check(rejected && unit.State.Request.Equals(SpeedRequest.Stop()), "Set bridge accepts only orders made by its bridges");
    }
}
