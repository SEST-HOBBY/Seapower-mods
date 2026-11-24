using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using AnchorChain;
using HarmonyLib;
using Mono.Cecil;
using Mono.Cecil.Cil;
using SeaPower;

static partial class BetaApiTests
{
    // Jiutian Reference Units is loaded only by the UAV collection's own
    // entry (a nested loader). These checks run its pinned adapter directly
    // and never load the image into the CLR, so the loader's companion
    // checks still see an AppDomain without it.
    static void R6_Jiutian261123(R6Context context)
    {
        const string hash = "230f38f674fb4ba54c0c4ca265c8723fb1818af2c108322b069fe179f70fc5f8";
        string source = Path.Combine(context.Workshop, "3836566168", "JiutianReferenceUnits.dll");
        byte[] original = File.ReadAllBytes(source);
        Check(Sha256Of(source) == hash, "Jiutian fixture is the inspected 1.4.7 author image");
        var messages = new List<string>();
        Check(BetaAssemblyPolicy.Prepare(source, context.Native, context.Cache, messages.Add) == null && messages.Count == 0,
            "On its own, the BepInEx-only Jiutian image is a silent library skip (it loads through its entry)");

        string adapted = AdaptPinnedImage(context, source, hash, out string audit);
        Check(audit == "launch-range-lookup=1", "Jiutian rewrite audit is exactly launch-range-lookup=1 (actual: " + audit + ")");
        Check(original.SequenceEqual(File.ReadAllBytes(source)), "Original Jiutian DLL retained byte for byte");

        using (var before = ModuleDefinition.ReadModule(source, new ReaderParameters { AssemblyResolver = context.Resolver }))
        using (var after = ModuleDefinition.ReadModule(adapted, new ReaderParameters { AssemblyResolver = context.Resolver })) {
            var changed = new List<string>(); int compared = 0;
            foreach (var t in Types(before.Types)) foreach (var method in t.Methods.Where(m => m.HasBody)) {
                var written = after.GetType(t.FullName).Methods.Single(m => m.FullName == method.FullName);
                compared++;
                if (!TopoInstructions(method).SequenceEqual(TopoInstructions(written))) changed.Add(t.FullName + "::" + method.Name);
            }
            Check(compared == 229 && changed.SequenceEqual(new[] { "JiutianFH901Flight::Register" }),
                "Of " + compared + " Jiutian bodies only JiutianFH901Flight.Register differs (actual: " + String.Join(", ", changed) + ")");

            var register = after.GetType("JiutianFH901Flight").Methods.Single(m => m.Name == "Register");
            var il = register.Body.Instructions;
            int at = il.IndexOf(il.Single(i => i.OpCode == OpCodes.Ldstr && Equals(i.Operand, "EffectiveMaxLaunchRange")));
            var local = (VariableDefinition)il[at + 3].Operand;
            string Shape(Instruction i) => i.OpCode.Name + (i.Operand is VariableDefinition v ? " V_" + v.Index : i.Operand is TypeReference t ? " " + t.FullName :
                i.Operand is MethodReference m ? " " + m.DeclaringType.FullName + "::" + m.Name : "");
            var shape = il.Skip(at + 1).Take(16).Select(Shape).ToArray();
            Check(shape.SequenceEqual(new[] {
                "ldc.i4.2", "newarr System.Type", "stloc.s V_6",
                "ldloc.s V_6", "ldc.i4.0", "ldtoken SeaPower.ObjectBase", "call System.Type::GetTypeFromHandle", "stelem.ref",
                "ldloc.s V_6", "ldc.i4.1", "ldtoken System.Single", "call System.Type::GetTypeFromHandle", "stelem.ref",
                "ldloc.s V_6", "ldnull", "call HarmonyLib.AccessTools::Method" }) && local.VariableType.FullName == "System.Type[]",
                "The launch-range lookup asks for (ObjectBase, float): " + String.Join("; ", shape));
            var postfix = after.GetType("JiutianFH901Flight").Methods.Single(m => m.Name == "AfterEffectiveRange");
            Check(postfix.Parameters.Select(p => p.Name).SequenceEqual(new[] { "__instance", "__0", "__result" }) &&
                postfix.Parameters[1].ParameterType.FullName == "SeaPower.ObjectBase" && postfix.Parameters[2].ParameterType.IsByReference,
                "The author's postfix binds the launcher by index (__0), so it fits the 261123 signature unchanged");
        }

        // What the rewritten lookup finds on the real 261123 game image.
        var found = AccessTools.Method(typeof(AmmunitionParameters), "EffectiveMaxLaunchRange", new[] { typeof(ObjectBase), typeof(float) }, null);
        var stale = AccessTools.Method(typeof(AmmunitionParameters), "EffectiveMaxLaunchRange", new[] { typeof(ObjectBase) }, null);
        Check(found != null && found.ReturnType == typeof(float) && stale == null,
            "On 261123 the widened lookup finds EffectiveMaxLaunchRange and the author's (ObjectBase) lookup finds nothing");
        Check(!AppDomain.CurrentDomain.GetAssemblies().Any(a => a.GetName().Name == "JiutianReferenceUnits"), "The Jiutian image never enters the CLR in these checks");
        var adapter = typeof(BetaAssemblyPolicy).GetMethod("AdapterFor", TacAll).Invoke(null, new object[] { hash });
        Check(adapter != null && (string)adapter.GetType().GetField("Name", TacAll).GetValue(adapter) == "Jiutian261123",
            "Jiutian 1.4.7 is pinned to its 261123 adapter by exact hash");
    }
}
