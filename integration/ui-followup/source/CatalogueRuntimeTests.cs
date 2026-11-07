using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;

// Runs the actual captured Runtime 1.5.0 factory body, including its two return
// paths, before and after the shipped transpiler. Only the virtual file reader
// is replaced with deterministic data. No Unity native API or detour is used.
static class CatalogueRuntimeTests
{
    const BindingFlags All = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance;
    static int checks, catalogReads, unitReads;
    static bool missing, fail, currentYear;
    static Assembly runtime, own;
    public sealed class Life { public bool Initialized = true; public bool Closing; }
    public sealed class Ini
    {
        readonly Dictionary<string, Dictionary<string, string>> value;
        public Ini(Dictionary<string, Dictionary<string, string>> data) { value = data; }
        public Dictionary<string, Dictionary<string, string>> Data() { return value; }
    }
    public static object Open(string folder, string name, string alias, bool load)
    {
        catalogReads++;
        if (fail) throw new IOException("Synthetic reader failure");
        var result = new Dictionary<string, Dictionary<string, string>>();
        if (missing && name == "weaponcosts") return new Ini(result);
        result["Costs"] = new Dictionary<string, string> { ["UseCurrentYearCosts"] = currentYear.ToString(), ["CurrentYear"] = "2026", ["OverrideInline"] = "False" };
        return new Ini(result);
    }
    public static object Unit(string folder, string reference, bool first, bool second)
    {
        unitReads++;
        int seed = reference.Contains("ship") ? 100000 : reference.Contains("air") ? 20000 : reference.Contains("land") ? 5000 : 100;
        string amount = reference.Contains("missing") ? "invalid" : seed.ToString();
        return new Ini(new Dictionary<string, Dictionary<string, string>> {
            ["General"] = new Dictionary<string, string> {
                ["WeaponCosts"] = amount, ["VesselCosts"] = amount, ["AircraftCosts"] = amount, ["LandCosts"] = amount,
                ["CurrentYearCost"] = (seed * 2).ToString(), ["WeaponCostCategory"] = reference.Contains("ignored") ? "Ignore" : "SAM"
            }
        });
    }
    static void Check(bool value, string why) { checks++; if (!value) throw new Exception(why); }
    static void Set(Type type, string name, object value) { type.GetField(name, All).SetValue(null, value); }
    static void Context(Life life)
    {
        Type type = own.GetType("Sest.UiFixes.PerformanceReview", true);
        Set(type, "game", life); Set(type, "initialized", typeof(Life).GetField("Initialized")); Set(type, "closing", typeof(Life).GetField("Closing"));
    }
    static FieldInfo labels;
    static IList Labels(CodeInstruction instruction) { return (IList)labels.GetValue(instruction); }
    static List<CodeInstruction> Read(MethodInfo method, ILGenerator generator)
    {
        var opcodes = typeof(OpCodes).GetFields(BindingFlags.Public | BindingFlags.Static).Where(f => f.FieldType == typeof(OpCode)).Select(f => (OpCode)f.GetValue(null)).ToDictionary(o => (ushort)o.Value);
        byte[] bytes = method.GetMethodBody().GetILAsByteArray();
        foreach (var local in method.GetMethodBody().LocalVariables) generator.DeclareLocal(local.LocalType, local.IsPinned);
        var instructions = new List<Tuple<int, CodeInstruction>>();
        var targets = new Dictionary<int, Label>();
        Func<int, Label> label = offset => { if (!targets.TryGetValue(offset, out var value)) targets[offset] = value = generator.DefineLabel(); return value; };
        int position = 0;
        while (position < bytes.Length)
        {
            int offset = position; ushort value = bytes[position++];
            if (value == 0xfe) value = (ushort)(0xfe00 | bytes[position++]);
            OpCode opcode = opcodes[value]; object operand = null;
            switch (opcode.OperandType)
            {
                case OperandType.InlineNone: break;
                case OperandType.ShortInlineI: operand = (sbyte)bytes[position++]; break;
                case OperandType.InlineI: operand = BitConverter.ToInt32(bytes, position); position += 4; break;
                case OperandType.InlineI8: operand = BitConverter.ToInt64(bytes, position); position += 8; break;
                case OperandType.ShortInlineR: operand = BitConverter.ToSingle(bytes, position); position += 4; break;
                case OperandType.InlineR: operand = BitConverter.ToDouble(bytes, position); position += 8; break;
                case OperandType.ShortInlineVar: operand = bytes[position++]; break;
                case OperandType.InlineVar: operand = (short)BitConverter.ToUInt16(bytes, position); position += 2; break;
                case OperandType.ShortInlineBrTarget: { int delta = (sbyte)bytes[position++]; operand = label(position + delta); break; }
                case OperandType.InlineBrTarget: { int delta = BitConverter.ToInt32(bytes, position); position += 4; operand = label(position + delta); break; }
                case OperandType.InlineSwitch:
                {
                    int count = BitConverter.ToInt32(bytes, position); position += 4; int end = position + count * 4;
                    var items = new Label[count]; for (int i = 0; i < count; i++) { items[i] = label(end + BitConverter.ToInt32(bytes, position)); position += 4; }
                    operand = items; break;
                }
                default:
                {
                    int token = BitConverter.ToInt32(bytes, position); position += 4;
                    if (opcode.OperandType == OperandType.InlineString) operand = method.Module.ResolveString(token);
                    else if (opcode.OperandType == OperandType.InlineSig) throw new Exception("Unexpected calli signature");
                    else operand = method.Module.ResolveMember(token);
                    break;
                }
            }
            instructions.Add(Tuple.Create(offset, new CodeInstruction(opcode, operand)));
        }
        foreach (var pair in instructions) if (targets.TryGetValue(pair.Item1, out var target)) Labels(pair.Item2).Add(target);
        Check(targets.Keys.All(k => instructions.Any(i => i.Item1 == k)), "Every original branch resolves");
        return instructions.Select(i => i.Item2).ToList();
    }
    static void Emit(ILGenerator generator, CodeInstruction instruction)
    {
        foreach (object label in Labels(instruction)) generator.MarkLabel((Label)label);
        var opcode = instruction.opcode; object operand = instruction.operand;
        if (operand == null) generator.Emit(opcode);
        else if (operand is Label branch) generator.Emit(opcode, branch);
        else if (operand is Label[] branches) generator.Emit(opcode, branches);
        else if (operand is MethodInfo method) generator.Emit(opcode, method);
        else if (operand is ConstructorInfo ctor) generator.Emit(opcode, ctor);
        else if (operand is FieldInfo field) generator.Emit(opcode, field);
        else if (operand is Type type) generator.Emit(opcode, type);
        else if (operand is string text) generator.Emit(opcode, text);
        else if (operand is int integer) generator.Emit(opcode, integer);
        else if (operand is long wide) generator.Emit(opcode, wide);
        else if (operand is sbyte small) generator.Emit(opcode, small);
        else if (operand is byte index) generator.Emit(opcode, index);
        else if (operand is short index2) generator.Emit(opcode, index2);
        else if (operand is float single) generator.Emit(opcode, single);
        else if (operand is double real) generator.Emit(opcode, real);
        else throw new Exception("Unexpected IL operand: " + operand.GetType());
    }
    static object ReadPrice(object prices, string kind, string reference)
    {
        return prices.GetType().GetMethod("Read", All).Invoke(prices, new object[] { kind, reference, kind == "weapon" ? "ammunition" : kind == "vessel" ? "vessels" : kind == "land" ? "land_units" : "aircraft", null });
    }
    static string Describe(object price, int quantity)
    {
        Type type = price.GetType();
        decimal? amount = (decimal?)type.GetField("Amount", All).GetValue(price);
        return (amount * quantity)?.ToString() + "/" + type.GetField("Category", All).GetValue(price) + "/" + type.GetField("Ignored", All).GetValue(price);
    }
    static void Run(string referenceFolder, string runtimePath, string ownPath)
    {
        runtime = Assembly.LoadFrom(runtimePath); own = Assembly.LoadFrom(ownPath);
        labels = typeof(CodeInstruction).GetField("labels");
        Type costs = runtime.GetType("Sest.RuntimeFixes.CampaignCosts", true);
        Set(costs, "openVirtual", typeof(CatalogueRuntimeTests).GetMethod("Open"));
        Set(costs, "openUnit", typeof(CatalogueRuntimeTests).GetMethod("Unit"));
        Set(costs, "data", typeof(Ini).GetMethod("Data"));
        var original = costs.GetMethod("Prices", All);
        Type cache = own.GetType("Sest.UiFixes.CostCatalogueCache", true);
        Set(cache, "priceType", original.ReturnType);
        var dynamic = new DynamicMethod("CapturedPricesWithCache", original.ReturnType, Type.EmptyTypes, original.Module, true);
        var generator = dynamic.GetILGenerator();
        var body = Read(original, generator);
        Check(body.Count(i => i.opcode == OpCodes.Ret) == 2, "Actual captured factory has two returns");
        var rewritten = ((IEnumerable<CodeInstruction>)cache.GetMethod("Reuse", All).Invoke(null, new object[] { body, generator })).ToArray();
        foreach (var instruction in rewritten) Emit(generator, instruction);
        Func<object> cached = () => dynamic.Invoke(null, null);
        Action clear = () => cache.GetMethod("Clear", All).Invoke(null, null);
        var life = new Life(); Context(life); clear();
        string[] kinds = { "weapon", "vessel", "aircraft", "land", "weapon", "weapon" };
        string[] refs = { "test-missile", "test-ship", "test-air", "test-land", "missing-price", "ignored-price" };
        object first = null;
        for (int report = 0; report < 180; report++)
        {
            object expected = original.Invoke(null, null); int before = catalogReads; object actual = cached();
            if (report == 0) first = actual;
            Check(ReferenceEquals(first, actual), "Reuse same successful pricing object within mission");
            Check(catalogReads - before == (report == 0 ? 5 : 0), "No repeated virtual catalogue opens");
            for (int i = 0; i < refs.Length; i++)
                Check(Describe(ReadPrice(expected, kinds[i], refs[i]), report + 1) == Describe(ReadPrice(actual, kinds[i], refs[i]), report + 1), "Live quantities and all price/missing/ignored results agree");
        }
        Check(catalogReads == 180 * 5 + 5, "180 original builds versus one cached build");
        clear(); currentYear = true; object current = cached();
        Check(!ReferenceEquals(first, current), "Tracker reload invalidates cached price basis");
        Check((bool)current.GetType().GetField("Current", All).GetValue(current), "New config basis is observed");
        Check(Describe(ReadPrice(current, "weapon", "test-missile"), 3).StartsWith("600/"), "Reloaded current-year amount and live quantity");
        Context(new Life()); object nextMission = cached(); Check(!ReferenceEquals(current, nextMission), "New mission invalidates cache");
        Context(new Life { Closing = true }); int outside = catalogReads; cached(); cached(); Check(catalogReads - outside == 10, "Closing/menu path uses original fresh factory");
        Context(new Life { Initialized = false }); outside = catalogReads; cached(); cached(); Check(catalogReads - outside == 10, "Loading path does not reuse mission catalogues");
        Context(new Life()); clear(); missing = true; outside = catalogReads;
        Check(cached() == null && cached() == null && catalogReads - outside == 2, "Missing catalogue results retry instead of becoming sticky nulls");
        missing = false; Check(cached() != null, "Recovery from missing catalogue");
        clear(); fail = true; bool threw = false;
        try { cached(); } catch (TargetInvocationException) { threw = true; }
        Check(threw, "Reader exception is propagated unchanged through the factory");
        fail = false; Check(cached() != null, "Failed load does not poison next attempt");
        clear(); Context(null); outside = catalogReads; cached(); cached(); Check(catalogReads - outside == 10, "No live mission means no cached catalogue");
        Console.WriteLine("Captured Runtime factory/transpiler checks passed: " + checks + "; identical changing-quantity results across 180 refreshes; successful catalogue opens reduced from 900 to 5 in that sequence. No game/native execution.");
    }
    static void Main(string[] args)
    {
        string folder = Path.GetFullPath(args[0]);
        AppDomain.CurrentDomain.AssemblyResolve += (sender, request) => {
            string path = Path.Combine(folder, new AssemblyName(request.Name).Name + ".dll");
            return File.Exists(path) ? Assembly.LoadFrom(path) : null;
        };
        Assembly.LoadFrom(Path.Combine(folder, "0Harmony.dll"));
        Run(folder, Path.GetFullPath(args[1]), Path.GetFullPath(args[2]));
    }
}
