using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text.RegularExpressions;

namespace Sest.RuntimeFixes;

internal sealed class CombatPrices
{
	internal const decimal MaximumPrice = 1000000000000000m;

	private readonly Dictionary<string, Dictionary<string, Dictionary<string, string>>> catalogs;

	// SEST's own catalog files, read by their own file names. On the public
	// beta the game's one-shot modifier scan can miss every Workshop #!extend
	// file (see ModifierRegistry), so the merged weaponcosts.ini may lack the
	// sections that sest_weapon_costs.ini extends into it. These are the same
	// sections read without the merge; the merged catalog wins where it has
	// the section.
	private readonly Dictionary<string, Dictionary<string, Dictionary<string, string>>> own;

	private readonly Func<string, string, Dictionary<string, string>> readUnit;

	private readonly Dictionary<string, CombatPrice> cache = new Dictionary<string, CombatPrice>(StringComparer.OrdinalIgnoreCase);

	internal readonly bool Current;

	internal readonly string Basis;

	internal CombatPrices(Dictionary<string, Dictionary<string, Dictionary<string, string>>> lists, Dictionary<string, Dictionary<string, string>> config, Func<string, string, Dictionary<string, string>> unitReader)
		: this(lists, config, unitReader, null)
	{
	}

	internal CombatPrices(Dictionary<string, Dictionary<string, Dictionary<string, string>>> lists, Dictionary<string, Dictionary<string, string>> config, Func<string, string, Dictionary<string, string>> unitReader, Dictionary<string, Dictionary<string, Dictionary<string, string>>> ownLists)
	{
		catalogs = lists;
		own = ownLists ?? new Dictionary<string, Dictionary<string, Dictionary<string, string>>>();
		readUnit = unitReader;
		Dictionary<string, string> data = Section(lists["weapon"], "Costs");
		Dictionary<string, string> data2 = Section(config, "Costs");
		string value = Get(data2, "UseCurrentYearCosts") ?? Get(data, "UseCurrentYearCosts");
		Current = bool.TryParse(value, out var result) && result;
		string text = Get(data2, "CurrentYear") ?? Get(data, "CurrentYear");
		Basis = ((!Current) ? "reference-year" : ((!string.IsNullOrWhiteSpace(text)) ? text : "current"));
	}

	internal static Dictionary<string, string> Section(Dictionary<string, Dictionary<string, string>> data, string key)
	{
		foreach (KeyValuePair<string, Dictionary<string, string>> datum in data)
		{
			if (string.Equals(datum.Key.Trim(), key, StringComparison.OrdinalIgnoreCase))
			{
				return datum.Value;
			}
		}
		return new Dictionary<string, string>();
	}

	internal static string Get(Dictionary<string, string> data, string key)
	{
		foreach (KeyValuePair<string, string> datum in data)
		{
			if (string.Equals(datum.Key.Trim(), key, StringComparison.OrdinalIgnoreCase))
			{
				return datum.Value;
			}
		}
		return null;
	}

	internal static bool Preference(Dictionary<string, string> data, string key, bool fallback)
	{
		bool result;
		return (!bool.TryParse(Get(data, key), out result)) ? fallback : result;
	}

	internal static string Resolve(Dictionary<string, string> own, Dictionary<string, string> global, Dictionary<string, string> entry, string field, string inlineField = null)
	{
		return Resolve(own, global, entry, field, inlineField, out bool _);
	}

	// fromEntry says whether the catalog section, rather than the unit's own
	// file, supplied the value.
	internal static string Resolve(Dictionary<string, string> own, Dictionary<string, string> global, Dictionary<string, string> entry, string field, string inlineField, out bool fromEntry)
	{
		bool fallback = Preference(global, "OverrideInline", fallback: false);
		fallback = Preference(entry, "OverrideInline", fallback);
		fallback = Preference(entry, "Override" + field, fallback);
		string text = Get(own, inlineField ?? field);
		string text2 = Get(entry, field);
		fromEntry = ((!fallback) ? (text == null && text2 != null) : (text2 != null));
		return (!fallback) ? (text ?? text2) : (text2 ?? text);
	}

	internal static string CatalogName(string kind)
	{
		return (kind == "land") ? "sest_land_costs.ini" : (kind + "costs.ini");
	}

	internal static decimal? Parse(string value)
	{
		decimal result;
		return (value == null || !decimal.TryParse(value, NumberStyles.AllowDecimalPoint, CultureInfo.InvariantCulture, out result) || !(result >= 0m) || !(result <= 1000000000000000m)) ? null : new decimal?(result);
	}

	internal static bool ValidCategory(string value)
	{
		return !string.IsNullOrWhiteSpace(value) && Regex.IsMatch(value, "\\A[A-Za-z0-9 _-]{1,20}\\z", RegexOptions.CultureInvariant);
	}

	private static string Fallback(string ammoType, Dictionary<string, string> own)
	{
		switch ((ammoType ?? string.Empty).ToLowerInvariant())
		{
		case "missile":
		{
			string a = Get(own, "TargetType") ?? string.Empty;
			if (string.Equals(a, "AAW", StringComparison.OrdinalIgnoreCase))
			{
				return (!string.Equals(Get(own, "AirLaunched"), "True", StringComparison.OrdinalIgnoreCase)) ? "SAM" : "AAM";
			}
			if (string.Equals(a, "ASuW", StringComparison.OrdinalIgnoreCase))
			{
				return "ASM";
			}
			if (string.Equals(a, "ASW", StringComparison.OrdinalIgnoreCase))
			{
				return "ASW";
			}
			return "Other";
		}
		case "asroc":
		case "rbu":
		case "airdepthcharge":
			return "ASW";
		case "torpedo":
			return "Torpedo";
		case "bomb":
			return "Bomb";
		case "projectile":
			return "Gun";
		case "aerialrocket":
		case "mlrs":
			return "Rocket";
		default:
			return "Ignore";
		}
	}

	internal CombatPrice Read(string kind, string reference, string folder, string ammoType = null)
	{
		reference = (reference ?? string.Empty).Trim().Replace('\\', '/');
		int num = reference.LastIndexOf('/');
		if (num >= 0)
		{
			reference = reference.Substring(num + 1);
		}
		if (reference.EndsWith(".ini", StringComparison.OrdinalIgnoreCase))
		{
			reference = reference.Substring(0, reference.Length - 4);
		}
		string key = kind + ":" + reference + ":" + folder + ":" + ammoType;
		if (cache.TryGetValue(key, out var value))
		{
			return value;
		}
		Dictionary<string, string> dictionary = readUnit(folder, reference);
		Dictionary<string, Dictionary<string, string>> data = catalogs[kind];
		Dictionary<string, string> global = Section(data, "Costs");
		Dictionary<string, string> entry = Section(data, reference);
		string catalog = CatalogName(kind);
		if (entry.Count == 0 && own.TryGetValue(kind, out var ownData))
		{
			entry = Section(ownData, reference);
			catalog = "sest_" + kind + "_costs.ini";
		}
		string text = kind switch
		{
			"weapon" => "WeaponCosts",
			"vessel" => "VesselCosts",
			"aircraft" => "AircraftCosts",
			_ => "LandCosts",
		};
		CombatPrice combatPrice = new CombatPrice();
		combatPrice.Amount = Parse(Resolve(dictionary, global, entry, (!Current) ? text : "CurrentYearCost", null, out bool fromEntry));
		combatPrice.Source = ((!combatPrice.Amount.HasValue) ? ("no " + Basis + " price") : ((!fromEntry) ? (folder + "/" + reference + ".ini") : (catalog + " [" + reference + "]")));
		value = combatPrice;
		if (kind == "weapon")
		{
			string text2 = Resolve(dictionary, global, entry, "Category", "WeaponCostCategory");
			value.Category = ((!string.IsNullOrEmpty(text2)) ? text2 : Fallback(ammoType ?? Get(dictionary, "Type"), dictionary));
			value.Ignored = !ValidCategory(value.Category) || string.Equals(value.Category, "Ignore", StringComparison.OrdinalIgnoreCase);
		}
		cache.Add(key, value);
		return value;
	}
}
