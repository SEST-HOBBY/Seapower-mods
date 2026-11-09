using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace Sest.RuntimeFixes;

internal sealed class CombatGameRecord
{
	internal string Id;

	internal string Name;

	internal string Source = string.Empty;

	internal string Status = "Ended";

	internal int MissionIndex;

	internal long EndedUtc;

	internal DateTime? CompletedAt;

	internal object Context;

	internal readonly List<CombatSideRecord> Sides = new List<CombatSideRecord>();

	internal string Encode()
	{
		List<string> list = new List<string>();
		list.Add("SEST-COMBAT-GAME-1");
		list.Add(Id);
		list.Add(EndedUtc.ToString(CultureInfo.InvariantCulture));
		list.Add(Uri.EscapeDataString(Name ?? "Game"));
		list.Add(Uri.EscapeDataString(Source ?? string.Empty));
		list.Add(MissionIndex.ToString(CultureInfo.InvariantCulture));
		list.Add(Uri.EscapeDataString(Status ?? "Ended"));
		List<string> list2 = list;
		foreach (CombatSideRecord side in Sides)
		{
			list2.Add(Uri.EscapeDataString(side.Name) + "\t" + side.Spent.Serialize() + "\t" + side.Platforms.Serialize() + "\t" + side.Stores.Serialize());
		}
		return Convert.ToBase64String(Encoding.UTF8.GetBytes(string.Join("\n", list2)));
	}

	internal static CombatGameRecord Decode(string text)
	{
		if (string.IsNullOrWhiteSpace(text) || text.Length > 12000000)
		{
			return null;
		}
		try
		{
			string[] array = Encoding.UTF8.GetString(Convert.FromBase64String(text)).Split('\n');
			if (array.Length >= 7 && array.Length <= 11 && !(array[0] != "SEST-COMBAT-GAME-1") && Regex.IsMatch(array[1], "\\A[A-Za-z0-9:_-]{1,160}\\z") && long.TryParse(array[2], NumberStyles.None, CultureInfo.InvariantCulture, out var result) && result >= 0)
			{
				long num = result;
				DateTime maxValue = DateTime.MaxValue;
				if (num <= maxValue.Ticks && int.TryParse(array[5], NumberStyles.None, CultureInfo.InvariantCulture, out var result2) && result2 >= 0)
				{
					CombatGameRecord combatGameRecord = new CombatGameRecord();
					combatGameRecord.Id = array[1];
					combatGameRecord.EndedUtc = result;
					combatGameRecord.Name = Uri.UnescapeDataString(array[3]);
					combatGameRecord.Source = Uri.UnescapeDataString(array[4]);
					combatGameRecord.MissionIndex = result2;
					combatGameRecord.Status = Uri.UnescapeDataString(array[6]);
					CombatGameRecord combatGameRecord2 = combatGameRecord;
					if (combatGameRecord2.Name.Length > 512 || combatGameRecord2.Source.Length > 256 || combatGameRecord2.Status.Length > 80)
					{
						return null;
					}
					HashSet<string> hashSet = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
					for (int i = 7; i < array.Length; i++)
					{
						string[] array2 = array[i].Split('\t');
						if (array2.Length != 4)
						{
							return null;
						}
						CombatSideRecord combatSideRecord = new CombatSideRecord();
						combatSideRecord.Name = Uri.UnescapeDataString(array2[0]);
						combatSideRecord.Spent = InventoryLedger.Parse(array2[1]);
						combatSideRecord.Platforms = InventoryLedger.Parse(array2[2]);
						combatSideRecord.Stores = InventoryLedger.Parse(array2[3]);
						CombatSideRecord combatSideRecord2 = combatSideRecord;
						if (!new string[4] { "Player", "Enemy", "Ally", "Neutral" }.Contains(combatSideRecord2.Name) || !hashSet.Add(combatSideRecord2.Name) || combatSideRecord2.Spent == null || combatSideRecord2.Platforms == null || combatSideRecord2.Stores == null)
						{
							return null;
						}
						combatGameRecord2.Sides.Add(combatSideRecord2);
					}
					return combatGameRecord2;
				}
			}
			return null;
		}
		catch (FormatException)
		{
			return null;
		}
	}
}
