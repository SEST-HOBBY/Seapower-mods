using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;

// Executes the shipped transpiler against the captured runtime's actual IL.
// No Unity rendering or game launch is performed.
static class PopOutCompatibilityTests
{
    const BindingFlags All = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance;
    static int checks;
    static void Check(bool value, string text) { checks++; if (!value) throw new Exception(text); }
    // Read original IL directly. Metadata tokens/branch offsets stay opaque:
    // the production transpiler must preserve them, never resolve or emit them.
    static List<CodeInstruction> Read(MethodInfo method)
    {
        var opcodes = typeof(OpCodes).GetFields(BindingFlags.Public | BindingFlags.Static)
            .Where(f => f.FieldType == typeof(OpCode)).Select(f => (OpCode)f.GetValue(null))
            .ToDictionary(o => (ushort)o.Value);
        byte[] bytes = method.GetMethodBody().GetILAsByteArray();
        var result = new List<CodeInstruction>(); int pos = 0;
        while (pos < bytes.Length)
        {
            ushort value = bytes[pos++];
            if (value == 0xfe) value = (ushort)(0xfe00 | bytes[pos++]);
            OpCode opcode = opcodes[value]; object operand = null;
            switch (opcode.OperandType)
            {
                case OperandType.InlineNone: break;
                case OperandType.ShortInlineI: operand = (sbyte)bytes[pos++]; break;
                case OperandType.ShortInlineVar: operand = bytes[pos++]; break;
                case OperandType.InlineVar: operand = BitConverter.ToUInt16(bytes, pos); pos += 2; break;
                case OperandType.ShortInlineBrTarget: operand = (sbyte)bytes[pos++]; break;
                case OperandType.InlineI8: operand = BitConverter.ToInt64(bytes, pos); pos += 8; break;
                case OperandType.InlineR: operand = BitConverter.ToDouble(bytes, pos); pos += 8; break;
                case OperandType.ShortInlineR: operand = BitConverter.ToSingle(bytes, pos); pos += 4; break;
                case OperandType.InlineSwitch:
                    int count = BitConverter.ToInt32(bytes, pos); pos += 4;
                    operand = bytes.Skip(pos).Take(count * 4).ToArray(); pos += count * 4; break;
                default:
                    int token = BitConverter.ToInt32(bytes, pos); pos += 4;
                    operand = opcode.OperandType == OperandType.InlineString ? (object)method.Module.ResolveString(token) : token;
                    break;
            }
            result.Add(new CodeInstruction(opcode, operand));
        }
        Check(pos == bytes.Length, "Complete original IL read");
        return result;
    }
    public static int Main(string[] args)
    {
        AppDomain.CurrentDomain.AssemblyResolve += (s, e) => {
            var path = Path.Combine(args[0], new AssemblyName(e.Name).Name + ".dll");
            return File.Exists(path) ? Assembly.LoadFrom(path) : null;
        };
        return Run(args);
    }
    [System.Runtime.CompilerServices.MethodImpl(System.Runtime.CompilerServices.MethodImplOptions.NoInlining)]
    static int Run(string[] args)
    {
        try
        {
            var own = Assembly.LoadFrom(args[2]);
            var patch = own.GetType("Sest.UiFixes.PopOutCompatibility", true);
            var rewrite = patch.GetMethod("Rewrite", All);
            var runtime = Assembly.LoadFrom(args[1]);
            var target = runtime.GetType("Sest.RuntimeFixes.PopOutBridge", true).GetMethod("EnsureBound", All);
            var before = Read(target);
            var labels = typeof(CodeInstruction).GetField("labels");
            var blocks = typeof(CodeInstruction).GetField("blocks");
            var operands = before.Select(c => c.operand).ToArray();
            var opcodes = before.Select(c => c.opcode).ToArray();
            var counts = before.Select(c => Tuple.Create(((IList)labels.GetValue(c)).Count, ((IList)blocks.GetValue(c)).Count)).ToArray();
            var after = ((IEnumerable<CodeInstruction>)rewrite.Invoke(null, new object[] { before })).ToList();
            Check(after.Count == before.Count, "Every runtime instruction retained");
            string expected = (string)own.GetType("Sest.UiFixes.ContactsSurfaceFix", true).GetField("PopOutHash", All).GetRawConstantValue();
            int changed = 0;
            for (int i = 0; i < before.Count; i++)
            {
                Check(ReferenceEquals(before[i], after[i]), "Original instruction retained");
                Check(opcodes[i] == after[i].opcode, "Original opcode retained");
                Check(counts[i].Item1 == ((IList)labels.GetValue(after[i])).Count && counts[i].Item2 == ((IList)blocks.GetValue(after[i])).Count,
                      "Original labels and exception blocks retained");
                if (!Equals(operands[i], after[i].operand))
                {
                    changed++;
                    Check(opcodes[i] == OpCodes.Ldstr, "Only string operands change");
                    Check(Equals(after[i].operand, expected) ||
                          Equals(after[i].operand, "native window bridge attached to Pop-Out Windows 1.1.3 (stable companion)"),
                          "Only the reviewed pin/message change");
                }
            }
            Check(changed == 2, "Exactly two string operands change");
            foreach (var bad in new[] { new List<CodeInstruction>(), after,
                new List<CodeInstruction> { new CodeInstruction(OpCodes.Ldstr, "uninspected") } })
            {
                bool rejected = false;
                try { rewrite.Invoke(null, new object[] { bad }); }
                catch (TargetInvocationException e) { rejected = e.InnerException is InvalidOperationException; }
                Check(rejected, "Changed or already rewritten runtime rejected");
            }
            var validate = patch.GetMethod("ValidateScreen", All);
            var popout = Assembly.LoadFrom(args[3]);
            validate.Invoke(null, new object[] { popout.GetType("SeaPowerPopOut.PopOutScreen", true) });
            Check(true, "Captured Pop-Out screen contracts accepted");
            bool invalid = false;
            try { validate.Invoke(null, new object[] { typeof(PopOutCompatibilityTests) }); }
            catch (TargetInvocationException e) { invalid = e.InnerException is MissingMemberException; }
            Check(invalid, "Incompatible screen rejected");
            if (args.Length > 4)
            {
                var tracker = Assembly.LoadFrom(args[4]);
                var trackerPatch = own.GetType("Sest.UiFixes.TrackerCompatibility", true);
                var validateTracker = trackerPatch.GetMethod("ValidateTracker", All);
                validateTracker.Invoke(null, new object[] { tracker.GetType("WeaponCostsMod.Overlay", true) });
                Check(true, "Actual captured Tracker 0.8 overlay contracts accepted");
                var bridge = runtime.GetType("Sest.RuntimeFixes.F11CombatCosts", true);
                var pollBody = Read(bridge.GetMethod("Poll", All));
                var originals = pollBody.Select(c => c.operand).ToArray();
                var rewritten = ((IEnumerable<CodeInstruction>)trackerPatch.GetMethod("Rewrite", All)
                    .Invoke(null, new object[] { pollBody })).ToList();
                Check(rewritten.Count == originals.Length, "Tracker bridge instruction count retained");
                int changedPins = 0;
                for (int i = 0; i < originals.Length; i++)
                {
                    Check(ReferenceEquals(pollBody[i], rewritten[i]), "Tracker bridge instructions retained");
                    if (!Equals(originals[i], rewritten[i].operand))
                    {
                        changedPins++;
                        Check(rewritten[i].opcode == OpCodes.Ldstr &&
                            Equals(rewritten[i].operand, trackerPatch.GetField("CurrentHash", All).GetRawConstantValue()),
                            "Only the tracker pin changes");
                    }
                }
                Check(changedPins == 1, "Exactly one tracker string operand changes");
                bool invalidTracker = false;
                try { validateTracker.Invoke(null, new object[] { typeof(PopOutCompatibilityTests) }); }
                catch (TargetInvocationException e) { invalidTracker = e.InnerException is MissingMemberException; }
                Check(invalidTracker, "Incompatible tracker rejected");
                var overlay = tracker.GetType("WeaponCostsMod.Overlay", true);
                var fieldArgs = new object[] { overlay, "visible", typeof(bool), null };
                Check(!(bool)trackerPatch.GetMethod("BeforeField", All).Invoke(null, fieldArgs), "Legacy visibility lookup is projected");
                var projected = (FieldInfo)fieldArgs[3];
                var owner = System.Runtime.Serialization.FormatterServices.GetUninitializedObject(overlay);
                var stateField = overlay.GetField("visibility", All);
                var state = Activator.CreateInstance(stateField.FieldType);
                stateField.SetValue(owner, state);
                Check((bool)projected.GetValue(owner), "Captured Tracker 0.8 starts expanded");
                projected.SetValue(owner, false);
                Check(!(bool)state.GetType().GetField("Expanded").GetValue(state), "Runtime close writes the author's actual state");
                state.GetType().GetMethod("Toggle").Invoke(state, new object[] { true });
                Check((bool)projected.GetValue(owner), "Author F11 toggle reopens the Runtime window");
                state.GetType().GetMethod("Toggle").Invoke(state, new object[] { false });
                Check((bool)projected.GetValue(owner), "Hidden HUD does not toggle visibility");
                var legacyField = bridge.GetMethod("Field", All);
                foreach (string name in new[] { "ready", "missionActive", "mission", "toggle" })
                    Check(legacyField.Invoke(null, new object[] { overlay, name, null }) is FieldInfo,
                        "Unchanged captured Runtime field binds actual Tracker 0.8: " + name);
            }
            Console.WriteLine("Stable Pop-Out compatibility checks passed: " + checks + "; actual Runtime 1.5.0 IL, captured PopOut 1.1.3 and Tracker 0.8 contracts; no game execution.");
            return 0;
        }
        catch (Exception e) { Console.Error.WriteLine(e); return 1; }
    }
}
