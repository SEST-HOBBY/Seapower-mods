using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text.RegularExpressions;

namespace Sest.RuntimeFixes
{
    // Original SEST code implementing the documented 0.7.1 data interface.
    // This class neither loads nor calls CombatCosts.dll.
    internal sealed class CombatPrice
    {
        internal decimal? Amount;
        internal string Category;
        internal bool Ignored;
    }

    internal sealed class CombatPrices
    {
        internal const decimal MaximumPrice = 1000000000000000m;
        readonly Dictionary<string, Dictionary<string, Dictionary<string, string>>> catalogs;
        readonly Func<string, string, Dictionary<string, string>> readUnit;
        readonly Dictionary<string, CombatPrice> cache = new Dictionary<string, CombatPrice>(StringComparer.OrdinalIgnoreCase);
        internal readonly bool Current;
        internal readonly string Basis;

        internal CombatPrices(Dictionary<string, Dictionary<string, Dictionary<string, string>>> lists,
            Dictionary<string, Dictionary<string, string>> config,
            Func<string, string, Dictionary<string, string>> unitReader)
        {
            catalogs = lists; readUnit = unitReader;
            var settings = Section(lists["weapon"], "Costs");
            var shared = Section(config, "Costs");
            string mode = Get(shared, "UseCurrentYearCosts") ?? Get(settings, "UseCurrentYearCosts");
            bool current; Current = Boolean.TryParse(mode, out current) && current;
            string year = Get(shared, "CurrentYear") ?? Get(settings, "CurrentYear");
            Basis = Current ? (String.IsNullOrWhiteSpace(year) ? "current" : year) : "reference-year";
        }

        internal static Dictionary<string, string> Section(Dictionary<string, Dictionary<string, string>> data, string key)
        {
            foreach (var pair in data)
                if (String.Equals(pair.Key.Trim(), key, StringComparison.OrdinalIgnoreCase)) return pair.Value;
            return new Dictionary<string, string>();
        }

        internal static string Get(Dictionary<string, string> data, string key)
        {
            foreach (var pair in data)
                if (String.Equals(pair.Key.Trim(), key, StringComparison.OrdinalIgnoreCase)) return pair.Value;
            return null;
        }

        internal static bool Preference(Dictionary<string, string> data, string key, bool fallback)
        {
            bool value;
            return Boolean.TryParse(Get(data,key), out value) ? value : fallback;
        }

        internal static string Resolve(Dictionary<string, string> own, Dictionary<string, string> global,
            Dictionary<string, string> entry, string field, string inlineField = null)
        {
            bool prefer = Preference(global, "OverrideInline", false);
            prefer = Preference(entry, "OverrideInline", prefer);
            prefer = Preference(entry, "Override" + field, prefer);
            string inline = Get(own, inlineField ?? field), listed = Get(entry, field);
            // A present blank wins; only an absent key falls back.
            return prefer ? (listed ?? inline) : (inline ?? listed);
        }

        internal static decimal? Parse(string value)
        {
            decimal result;
            return value != null && Decimal.TryParse(value, NumberStyles.AllowDecimalPoint,
                CultureInfo.InvariantCulture, out result) && result >= 0 && result <= MaximumPrice ? (decimal?)result : null;
        }

        internal static bool ValidCategory(string value)
        {
            return !String.IsNullOrWhiteSpace(value) && Regex.IsMatch(value, "\\A[A-Za-z0-9 _-]{1,20}\\z", RegexOptions.CultureInvariant);
        }

        static string Fallback(string ammoType, Dictionary<string, string> own)
        {
            switch ((ammoType ?? "").ToLowerInvariant())
            {
                case "missile":
                    string target = Get(own,"TargetType") ?? "";
                    if (String.Equals(target,"AAW",StringComparison.OrdinalIgnoreCase))
                        return String.Equals(Get(own,"AirLaunched"),"True",StringComparison.OrdinalIgnoreCase) ? "AAM" : "SAM";
                    if (String.Equals(target,"ASuW",StringComparison.OrdinalIgnoreCase)) return "ASM";
                    if (String.Equals(target,"ASW",StringComparison.OrdinalIgnoreCase)) return "ASW";
                    return "Other";
                case "asroc": case "rbu": case "airdepthcharge": return "ASW";
                case "torpedo": return "Torpedo";
                case "bomb": return "Bomb";
                case "projectile": return "Gun";
                case "aerialrocket": case "mlrs": return "Rocket";
                default: return "Ignore";
            }
        }

        internal CombatPrice Read(string kind, string reference, string folder, string ammoType = null)
        {
            reference=(reference ?? "").Trim().Replace('\\','/');
            int slash=reference.LastIndexOf('/');if(slash>=0)reference=reference.Substring(slash+1);
            if(reference.EndsWith(".ini",StringComparison.OrdinalIgnoreCase))reference=reference.Substring(0,reference.Length-4);
            string key = kind + ":" + reference + ":" + folder + ":" + ammoType;
            CombatPrice result;
            if (cache.TryGetValue(key,out result)) return result;
            var own = readUnit(folder,reference);
            var list = catalogs[kind];
            var global = Section(list,"Costs");
            var entry = Section(list,reference);
            string historical = kind == "weapon" ? "WeaponCosts" : kind == "vessel" ? "VesselCosts" :
                kind == "aircraft" ? "AircraftCosts" : "LandCosts";
            result = new CombatPrice { Amount = Parse(Resolve(own,global,entry,Current ? "CurrentYearCost" : historical)) };
            if (kind == "weapon")
            {
                string category = Resolve(own,global,entry,"Category","WeaponCostCategory");
                result.Category = String.IsNullOrEmpty(category) ? Fallback(ammoType ?? Get(own,"Type"),own) : category;
                result.Ignored = !ValidCategory(result.Category) || String.Equals(result.Category,"Ignore",StringComparison.OrdinalIgnoreCase);
            }
            cache.Add(key,result);
            return result;
        }
    }

    internal sealed class CombatAmount
    {
        internal decimal Known;
        internal long Unknown, Count, MissingRecords;
        internal bool Incomplete { get { return Unknown > 0 || MissingRecords > 0; } }
        internal void Add(CombatPrice price, long count)
        {
            if (count <= 0 || price.Ignored) return;
            Count = checked(Count + count);
            if (price.Amount.HasValue) Known = checked(Known + price.Amount.Value * count);
            else Unknown = checked(Unknown + count);
        }
        internal void Merge(CombatAmount other)
        {
            Known=checked(Known+other.Known); Unknown=checked(Unknown+other.Unknown);
            Count=checked(Count+other.Count); MissingRecords=checked(MissingRecords+other.MissingRecords);
        }
        internal static CombatAmount Sum(params CombatAmount[] values)
        {
            var result=new CombatAmount(); foreach (var value in values) result.Merge(value); return result;
        }
        internal string Text { get { return Money(Known) + (Incomplete ? " + ?" : ""); } }
        internal static string Money(decimal value)
        {
            string[] units={"","K","M","B","T","Q"}; int scale=0;
            while (value>=1000m && scale<units.Length-1) { value/=1000m; scale++; }
            int decimals = scale==0 ? 0 : value>=100m ? 0 : value>=10m ? 1 : 2;
            value=Math.Round(value,decimals,MidpointRounding.AwayFromZero);
            if (value>=1000m && scale<units.Length-1) { value/=1000m; scale++; decimals=2; }
            return "$"+value.ToString("F"+decimals,CultureInfo.InvariantCulture)+units[scale];
        }
    }
}
