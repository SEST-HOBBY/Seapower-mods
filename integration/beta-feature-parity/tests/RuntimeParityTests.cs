using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Reflection;

// Compare persisted history/inventories and numerical policy directly with
// the captured Runtime 1.5.0 binary. No native APIs or game state are invoked.
static class RuntimeParityTests
{
    const BindingFlags All = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance;
    static int checks;
    static Type T(Assembly a, string n) { return a.GetType("Sest.RuntimeFixes." + n, true); }
    static object Call(Type t, object o, string n, params object[] args) { return t.GetMethod(n, All).Invoke(o, args); }
    static void Check(bool ok, string why) { checks++; if (!ok) throw new Exception(why); }
    static void Set(object o, string name, object value) { o.GetType().GetField(name, All).SetValue(o, value); }
    static object Record(Assembly a, int seed)
    {
        object record = Activator.CreateInstance(T(a, "CombatGameRecord"), true);
        Set(record, "Id", "test:" + seed); Set(record, "Name", "Mission / Å " + seed);
        Set(record, "Source", "campaign:test"); Set(record, "Status", "Ended");
        Set(record, "EndedUtc", new DateTime(2026, 11, 1, 0, 0, 0, DateTimeKind.Utc).AddMinutes(seed).Ticks);
        Set(record, "MissionIndex", seed);
        var sides = (IList)record.GetType().GetField("Sides", All).GetValue(record);
        foreach (string sideName in new[] { "Player", "Enemy", "Ally", "Neutral" })
        {
            object side = Activator.CreateInstance(T(a, "CombatSideRecord"), true); Set(side, "Name", sideName);
            foreach (string field in new[] { "Spent", "Platforms", "Stores" })
            {
                object ledger = side.GetType().GetField(field, All).GetValue(side);
                var ammo = new Dictionary<string, long> { ["test missile / " + sideName] = seed + 1, ["SAM"] = seed * 3 };
                Call(ledger.GetType(), ledger, "Add", "vessel", ammo, seed % 2 == 0);
                Call(ledger.GetType(), ledger, "Add", "aircraft", new Dictionary<string, long>(), false);
            }
            sides.Add(side);
        }
        return record;
    }
    static void Main(string[] args)
    {
        string refs = Path.GetFullPath(args[0]);
        AppDomain.CurrentDomain.AssemblyResolve += (s,e) => {
            string p = Path.Combine(refs, new AssemblyName(e.Name).Name + ".dll");
            return File.Exists(p) ? Assembly.LoadFrom(p) : null;
        };
        Assembly old = Assembly.LoadFile(Path.GetFullPath(args[1]));
        // Mono unifies LoadFile calls with the same assembly identity. A raw
        // image keeps the candidate separate for this read-only comparison.
        Assembly candidate = Assembly.Load(File.ReadAllBytes(Path.GetFullPath(args[2])));
        Check(!ReferenceEquals(old, candidate), "Captured and candidate assemblies loaded separately");
        Type before = T(old, "Policy"), after = T(candidate, "Policy");
        float[] values = { -100, 0, 0.5f, 100, 500, float.MaxValue, float.NaN, float.PositiveInfinity, float.NegativeInfinity };
        foreach (float n in values)
        {
            Check(Equals(Call(before, null, "Finite", n), Call(after, null, "Finite", n)), "Finite policy parity");
            foreach (float h in values) foreach (float c in values)
                Check(Equals(Call(before, null, "Altitude", n, h, c), Call(after, null, "Altitude", n, h, c)), "Terrain clearance policy parity");
        }
        foreach (string text in new[] { null, "", "usn_rgm-109e5a", "USN_UGM-109E5A.ini", "ammo/usn_rgm-109e5a.ini", "other", "ToBearing", "MaintainHeight", "TerminalApproach", "MoveToFinalFlightAlt" })
            foreach (string method in new[] { "IsMst", "CruiseStage" })
                Check(Equals(Call(before, null, method, text), Call(after, null, method, text)), "Missile selection/stage policy parity");
        foreach (string[] settings in new[] {
            new[] { "[LoadOrder]", "Mod1Directory=3812461539,True" },
            new[] { "[LoadOrder]", "Mod1Directory=3812461539,False" },
            new[] { "[Other]", "Mod1Directory=3812461539,True" },
            new[] { "[LoadOrder]", " Mod1Directory = 3812461539, true " },
        }) Check(Equals(Call(before, null, "PackEnabled", settings, "3812461539"), Call(after, null, "PackEnabled", settings, "3812461539")), "Pack-selection policy parity");
        for (int i = 0; i < 30; i++)
        {
            object oldRecord = Record(old, i), newRecord = Record(candidate, i);
            string oldText = (string)Call(oldRecord.GetType(), oldRecord, "Encode");
            string newText = (string)Call(newRecord.GetType(), newRecord, "Encode");
            Check(oldText == newText, "History encoding remains byte compatible");
            object newFromOld = Call(T(candidate, "CombatGameRecord"), null, "Decode", oldText);
            object oldFromNew = Call(T(old, "CombatGameRecord"), null, "Decode", newText);
            Check(newFromOld != null && (string)Call(newFromOld.GetType(), newFromOld, "Encode") == oldText, "Candidate reads captured history format");
            Check(oldFromNew != null && (string)Call(oldFromNew.GetType(), oldFromNew, "Encode") == newText, "Captured Runtime reads candidate history format");
        }
        foreach (string text in new[] { "", "invalid", "====", Convert.ToBase64String(new byte[] { 1, 2, 3 }) })
            Check(Equals(Call(T(old, "CombatGameRecord"), null, "Decode", text), Call(T(candidate, "CombatGameRecord"), null, "Decode", text)), "Invalid history rejection parity");
        Console.WriteLine("Runtime 1.5.0/beta reconstruction parity passed: " + checks + " assertions; numerical policy and cross-readable saved history/inventories; no game execution.");
    }
}
