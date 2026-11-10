using System;
using System.Globalization;

namespace Sest.RuntimeFixes;

internal sealed class CombatAmount
{
	internal decimal Known;

	internal long Unknown;

	internal long Count;

	internal long MissingRecords;

	internal bool Incomplete => Unknown > 0 || MissingRecords > 0;

	internal string Text => Money(Known) + ((!Incomplete) ? string.Empty : " + ?");

	internal void Add(CombatPrice price, long count)
	{
		checked
		{
			if (count > 0 && !price.Ignored)
			{
				Count += count;
				if (price.Amount.HasValue)
				{
					Known += price.Amount.Value * (decimal)count;
				}
				else
				{
					Unknown += count;
				}
			}
		}
	}

	internal void Merge(CombatAmount other)
	{
		Known += other.Known;
		checked
		{
			Unknown += other.Unknown;
			Count += other.Count;
			MissingRecords += other.MissingRecords;
		}
	}

	internal static CombatAmount Sum(params CombatAmount[] values)
	{
		CombatAmount combatAmount = new CombatAmount();
		foreach (CombatAmount other in values)
		{
			combatAmount.Merge(other);
		}
		return combatAmount;
	}

	internal static string Money(decimal value)
	{
		string[] array = new string[6]
		{
			string.Empty,
			"K",
			"M",
			"B",
			"T",
			"Q"
		};
		int num = 0;
		while (value >= 1000m && num < array.Length - 1)
		{
			value /= 1000m;
			num++;
		}
		int num2 = ((num != 0) ? ((!(value >= 100m)) ? ((value >= 10m) ? 1 : 2) : 0) : 0);
		value = Math.Round(value, num2, MidpointRounding.AwayFromZero);
		if (value >= 1000m && num < array.Length - 1)
		{
			value /= 1000m;
			num++;
			num2 = 2;
		}
		return "$" + value.ToString("F" + num2, CultureInfo.InvariantCulture) + array[num];
	}
}
