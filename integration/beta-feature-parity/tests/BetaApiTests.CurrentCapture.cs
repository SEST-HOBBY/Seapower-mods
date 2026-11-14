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
        int admitted=0, resolved=0; var missing=new List<string>(); var held=new List<string>();
        foreach (string source in Directory.GetFiles(workshop,"*.dll",SearchOption.AllDirectories).OrderBy(x=>x,StringComparer.Ordinal)) {
            // The installer replaces this item's captured older candidate with
            // the newly compiled five-file set, checked by the build/native tests.
            if (source.StartsWith(Path.Combine(workshop,"3812461539")+Path.DirectorySeparatorChar,StringComparison.Ordinal)) continue;
            var messages=new List<string>();
            string prepared=BetaAssemblyPolicy.Prepare(source,native,cache,messages.Add);
            foreach (string message in messages) Console.WriteLine(message);
            if (messages.Any(m=>m.StartsWith("SKIPPED before CLR load: ")))
                held.Add(source.Substring(workshop.Length+1).Replace('\\','/'));
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
        // R14: the complete set SEST holds before CLR load on the 14 November
        // 0.9.2 capture. A change here is a policy change and must be reviewed.
        var expectedHeld=new[] {
            "3766210676/SaronicCorsairStrikeUSV.dll", "3784474738/EnhancedDecoyMod.dll", "3784474738/ExtendedGuidance.dll",
            "3784474738/MultiStageMissiles.dll", "3796349767/AlpineSeaPower.dll", "3804868806/AlpineSeaPower.dll",
            "3806466625/OspreyDeckOps.dll", "3806466625/OspreyMechanics.dll", "3810611344/BellSystemsFixtureTilt.dll",
            "3813033771/EC2CommsJamming.dll", "3819522350/K5KrakenContactStrike.dll", "3826122523/SeaPowerTopoFlat.dll" };
        foreach (string name in held) Console.WriteLine("HELD "+name);
        Check(held.OrderBy(x=>x,StringComparer.Ordinal).SequenceEqual(expectedHeld),
            "The 0.9.2 capture's held set is exactly the reviewed twelve images (actual: "+String.Join(", ",held)+")");
        Console.WriteLine("Current capture metadata scan: "+admitted+" admitted images, "+resolved+" resolved native operands; no plugin entrypoints executed.");
    }
}
