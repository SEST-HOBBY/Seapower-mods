using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;

namespace Sest.RuntimeFixes;

internal sealed class InventoryLedger
{
	internal readonly Dictionary<string, long> Ammo = new Dictionary<string, long>(StringComparer.OrdinalIgnoreCase);

	internal readonly Dictionary<string, long> Captured = new Dictionary<string, long>(StringComparer.OrdinalIgnoreCase);

	internal readonly HashSet<object> Seen = new HashSet<object>();

	internal long Unknown;

	internal void Add(string kind, Dictionary<string, long> ammo, bool incomplete)
	{
		Captured[kind] = Get(Captured, kind) + 1;
		foreach (KeyValuePair<string, long> item in ammo)
		{
			Ammo[item.Key] = checked(Get(Ammo, item.Key) + item.Value);
		}
		if (incomplete)
		{
			Unknown++;
		}
	}

	internal static long Get(Dictionary<string, long> values, string key)
	{
		long value;
		return (!values.TryGetValue(key, out value)) ? 0 : value;
	}

	internal string Serialize()
	{
		List<string> list = new List<string>();
		list.Add("SEST-INVENTORY-1");
		list.Add(Unknown.ToString(CultureInfo.InvariantCulture));
		List<string> list2 = list;
		string[] array = new string[3] { "vessel", "aircraft", "land" };
		foreach (string text in array)
		{
			list2.Add(text + "\t" + Get(Captured, text));
		}
		List<string> list3 = new List<string>(Ammo.Keys);
		list3.Sort(StringComparer.OrdinalIgnoreCase);
		foreach (string item in list3)
		{
			list2.Add(Uri.EscapeDataString(item) + "\t" + Ammo[item].ToString(CultureInfo.InvariantCulture));
		}
		return Convert.ToBase64String(Encoding.UTF8.GetBytes(string.Join("\n", list2)));
	}

	internal static InventoryLedger Parse(string text)
	{
		if (string.IsNullOrWhiteSpace(text) || text.Length > 4000000)
		{
			return null;
		}
		try
		{
			string[] array = Encoding.UTF8.GetString(Convert.FromBase64String(text)).Split('\n');
			if (array.Length < 5 || array.Length > 100005 || array[0] != "SEST-INVENTORY-1")
			{
				return null;
			}
			if (!long.TryParse(array[1], NumberStyles.None, CultureInfo.InvariantCulture, out var result) || result < 0)
			{
				return null;
			}
			InventoryLedger inventoryLedger = new InventoryLedger();
			inventoryLedger.Unknown = result;
			InventoryLedger inventoryLedger2 = inventoryLedger;
			for (int i = 2; i < array.Length; i++)
			{
				string[] array2 = array[i].Split('\t');
				if (array2.Length != 2 || !long.TryParse(array2[1], NumberStyles.None, CultureInfo.InvariantCulture, out var result2) || result2 < 0 || result2 > 1000000000000L)
				{
					return null;
				}
				string text2 = Uri.UnescapeDataString(array2[0]);
				if (string.IsNullOrWhiteSpace(text2) || text2.Contains("\n") || text2.Contains("\r"))
				{
					return null;
				}
				Dictionary<string, long> dictionary = ((i >= 5) ? inventoryLedger2.Ammo : inventoryLedger2.Captured);
				if (dictionary.ContainsKey(text2))
				{
					return null;
				}
				dictionary.Add(text2, result2);
			}
			if (inventoryLedger2.Captured.Count != 3 || !inventoryLedger2.Captured.ContainsKey("vessel") || !inventoryLedger2.Captured.ContainsKey("aircraft") || !inventoryLedger2.Captured.ContainsKey("land"))
			{
				return null;
			}
			return inventoryLedger2;
		}
		catch (FormatException)
		{
			return null;
		}
	}
}
