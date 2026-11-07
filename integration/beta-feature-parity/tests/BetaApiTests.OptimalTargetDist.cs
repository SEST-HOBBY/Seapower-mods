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
using CilOpCodes = Mono.Cecil.Cil.OpCodes;

static partial class BetaApiTests
{
    // R6: OptimalTargetDist 1.2.1.0 (Euromod, Workshop 3784474738). The adapter
    // changes SharedLaunchGroups.Transpiler's expected timer-write count from 3
    // to 4. Metadata and reflection only, plus the author's own transpilers run
    // over Harmony's copy of the beta OnUpdate IL; no Harmony patch is applied
    // and no game code runs.
    static void R6_OptimalTargetDist(R6Context context)
    {
        const BindingFlags all=BindingFlags.NonPublic|BindingFlags.Public|BindingFlags.Static|BindingFlags.Instance;
        const string audit="launch-layout=1, locations=2";
        const string slg="OptimalTargetDistAnchorChain.SharedLaunchGroups";
        string source=Path.Combine(context.Workshop,"3784474738/OptimalTargetDist.dll");
        byte[] bytes=File.ReadAllBytes(source);
        using (var sha=SHA256.Create())
            Check(BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-","").ToLowerInvariant()==
                "0ac35f8235d0a18a69e816ff1ed04f54212ecfa4d6a85b2350f1d9e5be5311d5", "OptimalTargetDist fixture is the pinned author image");
        var adapter=typeof(BetaAssemblyPolicy).GetMethod("OptimalTargetDistAdapter",BindingFlags.NonPublic|BindingFlags.Static).Invoke(null,null);
        Check((string)adapter.GetType().GetField("ExpectedAudit",all).GetValue(adapter)==audit, "OptimalTargetDist adapter declares the inspected audit");

        var log=new List<string>();
        string adapted=BetaAssemblyPolicy.Prepare(source,context.Native,context.Cache,log.Add);
        foreach (string line in log) Console.WriteLine(line);
        Check(adapted!=null && adapted!=source && File.Exists(adapted), "Private OptimalTargetDist image generated");
        Check(bytes.SequenceEqual(File.ReadAllBytes(source)), "OptimalTargetDist author bytes retained");
        Check(log.Count==1 && log[0]=="ADAPTED OptimalTargetDist in private cache: "+audit+"; original Workshop DLL and asset paths preserved.",
            "OptimalTargetDist logged audit equals the adapter's ExpectedAudit");

        // Instruction-by-instruction diff of every method: only short-to-long
        // branch forms, the two Guard.Allow location calls and the one layout
        // constant may differ.
        int layout=0, locations=0, branches=0, other=0;
        using (var author=ModuleDefinition.ReadModule(source,new ReaderParameters { AssemblyResolver=context.Resolver }))
        using (var image=ModuleDefinition.ReadModule(adapted,new ReaderParameters { AssemblyResolver=context.Resolver })) {
            var authorMethods=Types(author.Types).SelectMany(t=>t.Methods).Where(m=>m.HasBody).ToDictionary(m=>m.FullName);
            var imageMethods=Types(image.Types).SelectMany(t=>t.Methods).Where(m=>m.HasBody).ToDictionary(m=>m.FullName);
            Check(authorMethods.Keys.OrderBy(k=>k,StringComparer.Ordinal).SequenceEqual(imageMethods.Keys.OrderBy(k=>k,StringComparer.Ordinal)),
                "OptimalTargetDist image keeps every author method");
            foreach (var pair in authorMethods) {
                var before=pair.Value.Body.Instructions; var after=imageMethods[pair.Key].Body.Instructions;
                Check(before.Count==after.Count && pair.Value.Body.Variables.Count==imageMethods[pair.Key].Body.Variables.Count &&
                    pair.Value.Body.ExceptionHandlers.Count==imageMethods[pair.Key].Body.ExceptionHandlers.Count,
                    "OptimalTargetDist method shape retained: "+pair.Key);
                for (int i=0;i<before.Count;i++) {
                    var a=before[i]; var b=after[i];
                    string ta=OptimalTargetDistOperand(a,before), tb=OptimalTargetDistOperand(b,after);
                    if (a.OpCode==b.OpCode && ta==tb) continue;
                    if (a.OpCode.OperandType==Mono.Cecil.Cil.OperandType.ShortInlineBrTarget && b.OpCode.OperandType==Mono.Cecil.Cil.OperandType.InlineBrTarget &&
                        a.OpCode.Name+""==b.OpCode.Name+".s" && ta==tb) { branches++; continue; }
                    if (pair.Key.Contains("ACModActivation.Guard::Allow(") && a.OpCode==CilOpCodes.Callvirt &&
                        ta=="System.Reflection.Assembly::get_Location()" && b.OpCode==CilOpCodes.Call &&
                        tb=="AnchorChain.BetaAssemblyPolicy::OriginalLocation(System.Reflection.Assembly)") { locations++; continue; }
                    if (pair.Key.Contains(slg+"::Transpiler(") && a.OpCode==CilOpCodes.Ldc_I4_3 && b.OpCode==CilOpCodes.Ldc_I4_4 &&
                        a.Offset==0x03bc && a.Previous.OpCode==CilOpCodes.Ldloc_S && ((Mono.Cecil.Cil.VariableDefinition)a.Previous.Operand).Index==7 &&
                        b.Previous.OpCode==CilOpCodes.Ldloc_S && ((Mono.Cecil.Cil.VariableDefinition)b.Previous.Operand).Index==7 &&
                        b.Next.OpCode==CilOpCodes.Beq && b.Next.Operand==after[after.Count-2]) { layout++; continue; }
                    other++; Console.WriteLine("UNEXPECTED "+pair.Key+" #"+i+": "+a+" -> "+b);
                }
            }
            Check(layout==1 && locations==2 && other==0 && branches>0,
                "OptimalTargetDist IL differs only in the layout count, the two location calls and long branch forms (layout="+layout+
                ", locations="+locations+", other="+other+")");
            var transpiler=image.GetType(slg).Methods.Single(m=>m.Name=="Transpiler").Body.Instructions;
            Check(transpiler.Count(i=>i.OpCode==CilOpCodes.Ldc_I4_4 && i.Previous.OpCode==CilOpCodes.Ldloc_S &&
                ((Mono.Cecil.Cil.VariableDefinition)i.Previous.Operand).Index==7)==1 &&
                !transpiler.Any(i=>i.OpCode==CilOpCodes.Ldc_I4_3 && i.Previous.OpCode==CilOpCodes.Ldloc_S &&
                ((Mono.Cecil.Cil.VariableDefinition)i.Previous.Operand).Index==7),
                "Written SharedLaunchGroups.Transpiler expects four timer writes");
            Check(!Types(image.Types).SelectMany(t=>t.Methods).Where(m=>m.HasBody).SelectMany(m=>m.Body.Instructions)
                .Any(i=>(i.Operand as MethodReference)?.DeclaringType.FullName=="System.Reflection.Assembly" && ((MethodReference)i.Operand).Name=="get_Location"),
                "No Assembly.Location call remains in the OptimalTargetDist image");

            // Every Seapower-Scripts operand in the written image resolves on the beta.
            var missing=new List<string>(); int resolved=0;
            foreach (var type in Types(image.Types)) foreach (var method in type.Methods) {
                if (!method.HasBody) continue;
                foreach (var instruction in method.Body.Instructions) {
                    var member=instruction.Operand as MemberReference;
                    if (member?.DeclaringType?.Scope is not AssemblyNameReference scope || scope.Name!="Seapower-Scripts") continue;
                    try {
                        if (member is MethodReference call) { if (call.Resolve()==null) throw new Exception("unresolved method"); resolved++; }
                        else if (member is FieldReference field) { if (field.Resolve()==null) throw new Exception("unresolved field"); resolved++; }
                    } catch (Exception ex) { missing.Add(method.FullName+": "+member.FullName+" "+ex.Message); }
                }
            }
            foreach (string failure in missing) Console.WriteLine("MISSING OptimalTargetDist/"+failure);
            Check(missing.Count==0 && resolved>40, "All OptimalTargetDist native method/field operands resolve on the beta ("+resolved+")");
            Console.WriteLine("OptimalTargetDist resolved native operands: "+resolved);
        }

        var loaded=Assembly.LoadFile(adapted);
        Check(BetaAssemblyPolicy.OriginalLocation(loaded)==source, "Original asset provenance: OptimalTargetDist");
        var groups=loaded.GetType(slg,true);

        // The author's own API validation and loader lookup (reflection only).
        groups.GetMethod("ValidateApi",all).Invoke(null,null);
        var loader=(MethodInfo)groups.GetMethod("Loader",all).Invoke(null,null);
        var loadWeapons=typeof(ObjectBaseLoader).GetMethod("LoadWeaponSystems",BindingFlags.Public|BindingFlags.Static,null,
            new[] { typeof(IniHandler),typeof(ObjectBaseParameters),typeof(ObjectBase) },null);
        Check(loadWeapons!=null && loader==loadWeapons && loader.ReturnType==typeof(void), "SharedLaunchGroups binds beta LoadWeaponSystems(IniHandler, ObjectBaseParameters, ObjectBase)");

        // The real adapted transpiler over Harmony's copy of the beta OnUpdate.
        var onUpdate=typeof(WeaponSystemLauncher).GetMethod("OnUpdate",Type.EmptyTypes);
        var body=PatchProcessor.GetOriginalInstructions(onUpdate);
        var run=groups.GetMethod("Transpiler",all);
        var rewritten=(List<CodeInstruction>)run.Invoke(null,new object[] { body });
        var getKey=groups.GetMethod("GetKey",all);
        var systemName=typeof(BaseSystem).GetField("_systemName");
        Check(rewritten.Count==body.Count && body.Count==2158, "Adapted transpiler keeps the beta OnUpdate length ("+body.Count+")");
        var changed=Enumerable.Range(0,body.Count).Where(i=>rewritten[i].opcode!=body[i].opcode || !Equals(rewritten[i].operand,body[i].operand)).ToList();
        Console.WriteLine("OptimalTargetDist GetKey sites: "+String.Join(", ",changed));
        Check(changed.SequenceEqual(new[] { 1457, 1517, 1524, 1671, 1782, 1860, 1973 }), "Adapted transpiler rewrites exactly the seven beta shared-launch keys");
        string Kind(int i)
        {
            var field=(FieldInfo)body[i-2].operand; var next=body[i+1].operand as MethodInfo;
            if (field.Name=="_sharedLaunchIntervals" && next?.Name=="ContainsKey") return "contains";
            if (next?.Name=="get_Item") return field.Name=="_sharedLaunchIntervals" ? "interval" : "timer";
            if (field.Name=="_sharedLaunchTimers" && next?.DeclaringType==typeof(GameTime) && next.Name=="get_missionElapsedTime" &&
                (body[i+2].operand as MethodInfo)?.Name=="set_Item") return "write";
            return "other";
        }
        foreach (int i in changed)
            Check(body[i].opcode==OpCodes.Ldfld && Equals(body[i].operand,systemName) && body[i-1].opcode==OpCodes.Ldarg_0 &&
                body[i-2].opcode==OpCodes.Ldfld && (body[i-2].operand as FieldInfo)?.DeclaringType==typeof(ObjectBase) &&
                rewritten[i].opcode==OpCodes.Call && Equals(rewritten[i].operand,getKey) && getKey.GetParameters().Single().ParameterType==typeof(WeaponSystemLauncher),
                "Shared-launch key "+i+" now goes through SharedLaunchGroups.GetKey");
        Check(String.Join("/",changed.Select(Kind))=="contains/timer/interval/write/write/write/write",
            "Rewritten sites are 1 ContainsKey, 1 timer read, 1 interval read and 4 timer writes");
        // Index 1860 is the beta's new failed-launch stamp: it follows the
        // !_lastLaunchMalfunction test after launch() returned false.
        Check(body.Skip(1840).Take(18).Any(i=>(i.operand as FieldInfo)?.Name=="_lastLaunchMalfunction"),
            "The fourth write is the beta failed-launch branch, keyed by GetKey too");

        // RangeCorrection co-patches the same method; it still finds its two
        // MaxRangeRough calls after the shared-launch rewrite, as on stable.
        var range=loaded.GetType("OptimalTargetDistAnchorChain.RangeCorrection",true).GetMethod("LaunchTranspiler",all);
        var chained=(List<CodeInstruction>)range.Invoke(null,new object[] { rewritten });
        Check(chained.Count==body.Count && chained.Count(i=>(i.operand as MethodInfo)?.Name=="LaunchRange")==2 &&
            chained.Count(i=>Equals(i.operand,getKey))==7, "RangeCorrection still applies on top of the seven GetKey sites");

        // The unadapted author image fails exactly as captured on the PC.
        var authorAssembly=Assembly.Load(bytes);
        if (!ReferenceEquals(authorAssembly,loaded)) {
            var authorRun=authorAssembly.GetType(slg,true).GetMethod("Transpiler",all);
            string failure=null;
            try { authorRun.Invoke(null,new object[] { PatchProcessor.GetOriginalInstructions(onUpdate) }); }
            catch (TargetInvocationException ex) { failure=ex.InnerException?.GetType().Name+": "+ex.InnerException?.Message; }
            Check(failure=="NotSupportedException: Unrecognized launch layout: 1/1/1/4", "Unadapted author transpiler rejects the beta layout as captured ("+failure+")");
        }
        else Console.WriteLine("OptimalTargetDist negative control skipped: runtime reused the adapted assembly for the author bytes");

        // Patch parameters bind to the real beta targets: HarmonyX binds by the
        // original's parameter name, by __N position, or as __instance,
        // __state, __result or __exception.
        var loaded3=groups.GetMethod("Loaded",all).GetParameters();
        Check(loaded3.Select(p=>p.Name).SequenceEqual(new[] { "__0","__1","__2" }) &&
            loaded3.Select(p=>p.ParameterType).SequenceEqual(loadWeapons.GetParameters().Select(p=>p.ParameterType)),
            "SharedLaunchGroups.Loaded binds LoadWeaponSystems by position");
        var ammoPatch=loaded.GetType("OptimalTargetDistAnchorChain.AmmunitionParametersLoadPatch",true);
        var ammoTarget=(MethodInfo)ammoPatch.GetMethod("TargetMethod",all).Invoke(null,null);
        var ammoPost=ammoPatch.GetMethod("Postfix",all).GetParameters();
        Check(ammoTarget!=null && ammoTarget.DeclaringType==typeof(AmmunitionParameters) && !ammoTarget.IsStatic &&
            ammoPost[0].Name=="__instance" && ammoPost[0].ParameterType==typeof(AmmunitionParameters) &&
            ammoTarget.GetParameters().Any(p=>p.Name==ammoPost[1].Name && p.ParameterType==ammoPost[1].ParameterType),
            "AmmunitionParametersLoadPatch.Postfix binds the beta loadWeaponParameters");
        var select=loaded.GetType("OptimalTargetDistAnchorChain.SelectLauncherAmmoForAutoEngagePatch",true);
        var selectTarget=(MethodInfo)select.GetMethod("TargetMethod",all).Invoke(null,null);
        Check(selectTarget!=null && selectTarget.DeclaringType==typeof(AI) && selectTarget.GetParameters().Length==12,
            "SelectLauncherAmmoForAutoEngagePatch resolves the 12-parameter beta target");
        var stateType=select.GetMethod("Prefix",all).GetParameters().Single(p=>p.Name=="__state").ParameterType.GetElementType();
        foreach (string name in new[] { "Prefix","Postfix","Finalizer" })
            foreach (var parameter in select.GetMethod(name,all).GetParameters()) {
                bool ok=parameter.Name=="__state" ? (parameter.ParameterType.IsByRef ? parameter.ParameterType.GetElementType() : parameter.ParameterType)==stateType :
                    parameter.Name=="__exception" ? parameter.ParameterType==typeof(Exception) :
                    selectTarget.GetParameters().Any(p=>p.Name==parameter.Name && p.ParameterType==parameter.ParameterType);
                Check(ok, "SelectLauncherAmmoForAutoEngagePatch."+name+" parameter binds by name: "+parameter.Name);
            }
        foreach (var (typeName,methodName,owner) in new[] {
            ("OptimalTargetDistAnchorChain.AdaptiveLoft","AfterTune",typeof(Missile)),
            ("OptimalTargetDistAnchorChain.AdaptiveLoft","AfterAsyncTune",typeof(Missile)),
            ("OptimalTargetDistAnchorChain.LauncherAbortDiagnostics","Ending",typeof(WeaponSystem)) }) {
            var parameters=loaded.GetType(typeName,true).GetMethod(methodName,all).GetParameters();
            Check(parameters.Length==1 && parameters[0].Name=="__instance" && parameters[0].ParameterType==owner,
                typeName+"."+methodName+" binds only __instance");
        }
    }

    // Operand text for the diff: branch targets by index, members by
    // signature, everything else by value.
    static string OptimalTargetDistOperand(Mono.Cecil.Cil.Instruction instruction, IList<Mono.Cecil.Cil.Instruction> body)
    {
        switch (instruction.Operand) {
            case Mono.Cecil.Cil.Instruction target: return "->"+body.IndexOf(target);
            case Mono.Cecil.Cil.Instruction[] targets: return "->"+String.Join(",",targets.Select(body.IndexOf));
            case MethodReference method: return method.DeclaringType.FullName+"::"+method.Name+"("+String.Join(",",method.Parameters.Select(p=>p.ParameterType.FullName))+")";
            case FieldReference field: return field.DeclaringType.FullName+"::"+field.Name;
            case TypeReference type: return type.FullName;
            case Mono.Cecil.Cil.VariableDefinition variable: return "V_"+variable.Index;
            case ParameterDefinition parameter: return "A_"+parameter.Index;
            case null: return "";
            default: return Convert.ToString(instruction.Operand,System.Globalization.CultureInfo.InvariantCulture);
        }
    }
}
