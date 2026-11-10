// R6 bridges for the hash-pinned TestRange 0.2.3 private image. Both replace
// calls inside the author's CountermeasureApi.Validate registration of its
// combined-jamming hook; neither changes game code. Operands are matched by
// name, never by reference equality, and a mismatch throws, which the
// author's InitializeWhenModEnabled catch turns into the plugin's own
// "[TestRange] Initialization failed" stop, as on the beta today.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using SeaPower;

namespace AnchorChain;

public static partial class BetaCompatibilityCalls
{
    // TestRange's ECM.JamUnit argument list, CountermeasureApi.Validate IL_0099..IL_0107.
    private static readonly string[] TestRangeJamUnitTypes = { "System.Single", "UnityEngine.Vector3", "SeaPower.Globals+Frequency",
        "System.Single", "System.Single", "System.Single", "SeaPower.Crew", "System.Single" };
    private const BindingFlags TestRangeLookup = (BindingFlags)60; // Instance | Static | Public | NonPublic, as the author uses

    // A type's structural name: full name, with generic arguments spelled out.
    public static string TestRangeTypeName(Type type)
        => type == null ? "<null>" : type.IsGenericType && !type.IsGenericTypeDefinition
            ? type.GetGenericTypeDefinition().FullName + "<" + String.Join(",", type.GetGenericArguments().Select(TestRangeTypeName)) + ">"
            : type.FullName;

    private static bool TestRangeTypes(IEnumerable<Type> types, params string[] names)
        => types != null && types.Select(TestRangeTypeName).SequenceEqual(names);

    // Replaces Enumerable.Concat<Type> at CountermeasureApi.Validate IL_0164
    // (site 1). Stable summed each jammer's noise inside CombinedJamUnit; beta
    // RadarCalculator.ApplyJammingToDetectionRange IL_0036..IL_0047 sums
    // ECM.StandoffNoiseFactor(ownPosition, frequency, jamResistance) per jammer
    // and passes only the total to CombinedJamUnit(double, ...). Returns the
    // parameter types of that native beta method, which are JamUnit's
    // arguments 1, 2 and 7, so the author's Add binds the native per-jammer term.
    public static IEnumerable<Type> TestRangeStandoffArgs(IEnumerable<Type> legacyPrefix, IEnumerable<Type> jamArgs)
    {
        var prefix = legacyPrefix?.ToArray(); var jam = jamArgs?.ToArray();
        if (!TestRangeTypes(prefix, "System.Collections.Generic.IEnumerable`1<SeaPower.ECM>") || !TestRangeTypes(jam, TestRangeJamUnitTypes))
            throw new InvalidOperationException("Inspected TestRange combined-jamming registration changed");
        var standoff = typeof(ECM).GetMethods(TestRangeLookup).Where(m => m.Name == "StandoffNoiseFactor").ToArray();
        if (standoff.Length != 1 || standoff[0].IsStatic || TestRangeTypeName(standoff[0].ReturnType) != "System.Double" ||
            !TestRangeTypes(standoff[0].GetParameters().Select(p => p.ParameterType), TestRangeTypeName(jam[1]), TestRangeTypeName(jam[2]), TestRangeTypeName(jam[7])))
            throw new InvalidOperationException("Inspected beta ECM.StandoffNoiseFactor changed");
        return standoff[0].GetParameters().Select(p => p.ParameterType).ToArray();
    }

    // Replaces the call to CountermeasureApi.Add at CountermeasureApi.Validate
    // IL_01f9 (site 2), the registration of stable's 10-parameter
    // CombinedJamUnit(IEnumerable<ECM>, ObjectBase, ...). The beta ECM method
    // table has only CombinedJamUnit(double supportNoiseFactor, ObjectBase, ...),
    // which receives the sum that site 1's StandoffNoiseFactor hook already
    // filters, so nothing is registered. Stable's 9-parameter overload only
    // forwarded to this one, so site 1 covers both.
    public static void TestRangeLegacyCombined(Type type, string name, Type result, bool isStatic, string hook, bool postfix, bool optional, Type[] args)
    {
        if (TestRangeTypeName(type) != "SeaPower.ECM" || name != "CombinedJamUnit" || TestRangeTypeName(result) != "System.Single" || !isStatic ||
            hook != "Combined" || postfix || optional || args == null || args.Length != 10 ||
            !TestRangeTypes(args.Take(2), "System.Collections.Generic.IEnumerable`1<SeaPower.ECM>", "SeaPower.ObjectBase") ||
            !TestRangeTypes(args.Skip(2), TestRangeJamUnitTypes))
            throw new InvalidOperationException("Inspected TestRange legacy combined-jamming registration changed");
        var combined = type.GetMethods(TestRangeLookup).Where(m => m.Name == name).ToArray();
        if (combined.Length != 1 || !combined[0].IsStatic || combined[0].GetParameters().Length != 9 ||
            TestRangeTypeName(combined[0].GetParameters()[0].ParameterType) != "System.Double" || combined[0].GetParameters()[0].Name != "supportNoiseFactor")
            throw new InvalidOperationException("Inspected beta ECM.CombinedJamUnit changed: this adapter is for beta 0.8.7-261107 only");
    }
}
