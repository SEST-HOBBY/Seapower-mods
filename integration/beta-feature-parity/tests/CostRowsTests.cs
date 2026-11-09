using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;

// Prices and item rows against in-memory catalogs: SEST's own catalog file
// supplies a section the merged catalog lacks, the merged catalog still wins
// where it has the section, every row names its source, and the saved
// quantity record is not changed by building the rows. No game execution.
static class CostRowsTests
{
    const BindingFlags All = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance;
    static int checks;
    static void Check(bool ok, string why) { checks++; if (!ok) throw new Exception(why); }
    static Dictionary<string, Dictionary<string, string>> Ini(params KeyValuePair<string, Dictionary<string, string>>[] sections)
    {
        var ini = new Dictionary<string, Dictionary<string, string>>();
        foreach (var s in sections) ini[s.Key] = s.Value;
        return ini;
    }
    static KeyValuePair<string, Dictionary<string, string>> Section(string name, params string[] pairs)
    {
        var keys = new Dictionary<string, string>();
        for (int i = 0; i + 1 < pairs.Length; i += 2) keys[pairs[i]] = pairs[i + 1];
        return new KeyValuePair<string, Dictionary<string, string>>(name, keys);
    }
    static object Prices(Assembly runtime, bool current)
    {
        var lists = new Dictionary<string, Dictionary<string, Dictionary<string, string>>> {
            ["weapon"] = Ini(Section("Costs", "UseCurrentYearCosts", current.ToString(), "CurrentYear", "2026"),
                             Section("usn_agm-114l", "WeaponCosts", "100000", "CurrentYearCost", "200000", "Category", "ATGM")),
            ["vessel"] = Ini(Section("Costs")), ["aircraft"] = Ini(Section("Costs")), ["land"] = Ini(),
        };
        var own = new Dictionary<string, Dictionary<string, Dictionary<string, string>>> {
            ["weapon"] = Ini(Section("sest_agr-30", "WeaponCosts", "70000", "CurrentYearCost", "150000", "Category", "ATGM"),
                             Section("usn_agm-114l", "WeaponCosts", "1", "CurrentYearCost", "1", "Category", "Wrong")),
            ["vessel"] = Ini(), ["aircraft"] = Ini(),
        };
        // Every round has a readable unit file (an anti-ship missile); only one
        // carries its own inline price. A round with no unit file at all is
        // Ignored by the existing category rule, as in Runtime 1.5.0.
        Func<string, string, Dictionary<string, string>> unit = (folder, reference) =>
            reference == "inline_round" ? new Dictionary<string, string> { ["WeaponCosts"] = "42", ["CurrentYearCost"] = "84", ["Type"] = "Missile", ["TargetType"] = "ASuW" }
                                        : new Dictionary<string, string> { ["Type"] = "Missile", ["TargetType"] = "ASuW" };
        Type type = runtime.GetType("Sest.RuntimeFixes.CombatPrices", true);
        var ctor = type.GetConstructors(All).Single(c => c.GetParameters().Length == 4);
        return ctor.Invoke(new object[] { lists, Ini(Section("Costs")), unit, own });
    }
    static object Read(object prices, string reference)
    {
        return prices.GetType().GetMethod("Read", All).Invoke(prices, new object[] { "weapon", reference, "ammunition", null });
    }
    static T Get<T>(object o, string field) { return (T)o.GetType().GetField(field, All).GetValue(o); }
    static void Main(string[] args)
    {
        string refs = Path.GetFullPath(args[0]);
        AppDomain.CurrentDomain.AssemblyResolve += (s, e) => {
            string p = Path.Combine(refs, new AssemblyName(e.Name).Name + ".dll");
            return File.Exists(p) ? Assembly.LoadFrom(p) : null;
        };
        var runtime = Assembly.LoadFrom(Path.GetFullPath(args[1]));
        object reference = Prices(runtime, false);
        object agr = Read(reference, "sest_agr-30");
        Check(Get<decimal?>(agr, "Amount") == 70000m, "SEST's own catalog prices the round the merged catalog lacks");
        Check(Get<string>(agr, "Source") == "sest_weapon_costs.ini [sest_agr-30]", "The row names SEST's catalog section: " + Get<string>(agr, "Source"));
        Check(Get<string>(agr, "Category") == "ATGM" && !Get<bool>(agr, "Ignored"), "Category comes with the fallback section");
        object hellfire = Read(reference, "usn_agm-114l");
        Check(Get<decimal?>(hellfire, "Amount") == 100000m && Get<string>(hellfire, "Source") == "weaponcosts.ini [usn_agm-114l]", "The merged catalog wins where it has the section");
        Check(Get<string>(hellfire, "Category") == "ATGM", "The merged section's category is kept");
        object unknown = Read(reference, "nothing");
        Check(!Get<decimal?>(unknown, "Amount").HasValue && Get<string>(unknown, "Source") == "no reference-year price", "An unpriced round says so: " + Get<string>(unknown, "Source"));
        Check(Get<string>(unknown, "Category") == "ASM" && !Get<bool>(unknown, "Ignored"), "An unpriced anti-ship missile keeps the tracker's fallback category and counts as unknown");
        object inline = Read(reference, "inline_round");
        Check(Get<decimal?>(inline, "Amount") == 42m && Get<string>(inline, "Source") == "ammunition/inline_round.ini", "A unit file's own price names that file: " + Get<string>(inline, "Source"));
        object current = Prices(runtime, true);
        Check(Get<decimal?>(Read(current, "sest_agr-30"), "Amount") == 150000m, "Current-year value from SEST's own catalog");
        Check(Get<string>(Read(current, "nothing"), "Source") == "no 2026 price", "The catalog year is the basis in the missing-price note: " + Get<string>(Read(current, "nothing"), "Source"));

        Type ledgerType = runtime.GetType("Sest.RuntimeFixes.InventoryLedger", true);
        object ledger = Activator.CreateInstance(ledgerType, true);
        var ammo = (Dictionary<string, long>)ledgerType.GetField("Ammo", All).GetValue(ledger);
        ammo["sest_agr-30"] = 3; ammo["nothing"] = 2; ammo["usn_agm-114l"] = 1; ammo["empty"] = 0;
        string before = (string)ledgerType.GetMethod("Serialize", All).Invoke(ledger, null);
        var rows = (IList)runtime.GetType("Sest.RuntimeFixes.CampaignCosts", true).GetMethod("Items", All).Invoke(null, new object[] { "Player weapons expended", ledger, reference });
        var texts = rows.Cast<object>().Select(r => Get<string>(r, "Text")).ToList();
        var kinds = rows.Cast<object>().Select(r => Get<object>(r, "Kind").ToString()).ToList();
        Check(texts.Count == 4, "A heading and three item rows, the zero-quantity key skipped: " + texts.Count);
        Check(texts[0].Trim() == "Player weapons expended" && kinds[0] == "Category", "The heading row");
        Check(texts[1].Trim() == "sest_agr-30 ×3 @ $70,000 = $210,000 | sest_weapon_costs.ini [sest_agr-30]", "Three AGR-30 rounds at the existing reference-year estimate: " + texts[1].Trim());
        Check(texts[2].Trim() == "usn_agm-114l ×1 @ $100,000 = $100,000 | weaponcosts.ini [usn_agm-114l]", "Rows are sorted by line total: " + texts[2].Trim());
        Check(texts[3].Trim() == "nothing ×2 @ ? = ? | no reference-year price" && kinds[3] == "Item", "An unpriced round shows ? and its note: " + texts[3].Trim());
        Check(before == (string)ledgerType.GetMethod("Serialize", All).Invoke(ledger, null), "Building rows leaves the saved quantity record unchanged");
        Check(Enum.GetNames(runtime.GetType("Sest.RuntimeFixes.CostLineKind", true)).Contains("Item"), "Item row kind exists for the native typography");
        Console.WriteLine("Cost row and SEST catalog fallback checks passed: " + checks + " assertions on in-memory catalogs; no game execution.");
    }
}
