using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using AnchorChain;
using Mono.Cecil;

static partial class BetaApiTests
{
    static void CurrentCaptureNativeScan(string workshop, string native, string cache, DefaultAssemblyResolver resolver)
    {
        var sentinel=BetaCompatibilityCalls.LegacyFormationMembership(null);
        Check(sentinel!=null && !sentinel.Cast<object>().Any() && ReferenceEquals(sentinel,BetaCompatibilityCalls.LegacyFormationMembership(null)),
            "Retired formation label collection uses a dedicated empty identity, preserving real ItemsControl sources");
        var fuel=HarmonyLib.PatchProcessor.GetOriginalInstructions(typeof(BetaCompatibilityCalls).GetMethod("OspreyFuelDistance"));
        var calls=fuel.Select(i=>i.operand as System.Reflection.MethodInfo).Where(m=>m!=null).Select(m=>m.Name).ToList();
        Check(calls.Count(n=>n=="UpdateFuelConsumption")==2 && calls.IndexOf("FuelForCruiseKm")<calls.IndexOf("BurnFuel") &&
            calls.LastIndexOf("UpdateFuelConsumption")>calls.IndexOf("BurnFuel"),
            "Osprey fuel bridge refreshes native rates, converts cruise distance, burns native kilograms, then refreshes display");
        int admitted=0, resolved=0; var missing=new List<string>();
        foreach (string source in Directory.GetFiles(workshop,"*.dll",SearchOption.AllDirectories).OrderBy(x=>x,StringComparer.Ordinal)) {
            // The installer replaces this item's captured older candidate with
            // the newly compiled five-file set, checked by the build/native tests.
            if (source.StartsWith(Path.Combine(workshop,"3812461539")+Path.DirectorySeparatorChar,StringComparison.Ordinal)) continue;
            string prepared=BetaAssemblyPolicy.Prepare(source,native,cache,Console.WriteLine);
            if (prepared==null) continue;
            admitted++;
            using var module=ModuleDefinition.ReadModule(prepared,new ReaderParameters { AssemblyResolver=resolver });
            foreach (var type in Types(module.Types)) foreach (var method in type.Methods.Where(m=>m.HasBody))
                foreach (var instruction in method.Body.Instructions) {
                    var member=instruction.Operand as MemberReference;
                    if (member?.DeclaringType?.Scope is not AssemblyNameReference scope || scope.Name!="Seapower-Scripts") continue;
                    try {
                        if (member is MethodReference call) { if(call.Resolve()==null) throw new Exception("method absent"); resolved++; }
                        else if(member is FieldReference field) { if(field.Resolve()==null) throw new Exception("field absent"); resolved++; }
                    } catch(Exception ex) { missing.Add(source.Substring(workshop.Length)+"/"+method.Name+": "+member.FullName+" "+ex.Message); }
                }
        }
        foreach(string failure in missing.Distinct()) Console.WriteLine("CURRENT-MISSING "+failure);
        Check(admitted>20 && resolved>6000 && missing.Count==0,"All admitted current author images resolve direct native method/field operands");
        Console.WriteLine("Current capture metadata scan: "+admitted+" admitted images, "+resolved+" resolved native operands; no plugin entrypoints executed.");
    }
}
