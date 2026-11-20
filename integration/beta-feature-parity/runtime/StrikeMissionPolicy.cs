using System;
using System.Collections.Generic;

namespace Sest.RuntimeFixes;

// The fire-mission decisions, kept free of Unity and the strike tool so the
// managed tests can run them directly. StrikeMission feeds them the author's
// own leg state (status, salvo, launched, launch time) and acts on the answer.
internal static class StrikeMissionPolicy
{
	// The native engage order is issued this many game seconds before the
	// author's computed launch time, so the launcher's own reaction delay
	// does not make every automatic shot late.
	internal const float OrderLead = 1f;

	// An order is never issued more than this many game seconds after the
	// launch time: the time on target is gone, and the author marks it late.
	internal const float LateLimit = 45f;

	// If the native engage task has gone without a launch (blocked, out of
	// arc, no channel), the order may be repeated after this many seconds...
	internal const float RetryAfter = 15f;

	// ...but never more than this many times per leg.
	internal const int MaxOrders = 3;

	// LegStatus.Ok in the author's enum.
	internal const int StatusOk = 0;

	internal static int ShotsToOrder(bool armed, bool locked, bool arming, bool targetAlive, int status, bool fired, int salvo, int launched, float launchTime, float now, int ordersSent, bool taskPending, float lastOrderAt)
	{
		if (!armed || !locked || arming || !targetAlive || fired || status != StatusOk)
		{
			return 0;
		}
		int remaining = salvo - Math.Max(0, launched);
		if (remaining <= 0 || taskPending || ordersSent >= MaxOrders)
		{
			return 0;
		}
		if (now < launchTime - OrderLead || now > launchTime + LateLimit)
		{
			return 0;
		}
		if (ordersSent > 0 && now - lastOrderAt < RetryAfter)
		{
			return 0;
		}
		return remaining;
	}

	// One time on target for every target in the mission: the latest of the
	// targets' earliest impacts, or the player's requested time when that is
	// later still. Null when no target can be timed.
	internal static float? CommonImpact(IEnumerable<float> earliestImpacts, float? requested)
	{
		float? latest = null;
		foreach (float t in earliestImpacts)
		{
			if (!float.IsNaN(t) && !float.IsInfinity(t) && (!latest.HasValue || t > latest.Value))
			{
				latest = t;
			}
		}
		if (requested.HasValue && (!latest.HasValue || requested.Value > latest.Value))
		{
			return requested;
		}
		return latest;
	}

	// Rounds still to fly per shooter and weapon, across every target of the
	// mission, against what the shooter carries. Returns the over-committed
	// keys with (planned, carried).
	internal static List<KeyValuePair<string, int[]>> OverCommitted(IEnumerable<KeyValuePair<string, int>> plannedRounds, Func<string, int> carried)
	{
		var totals = new Dictionary<string, int>(StringComparer.Ordinal);
		var order = new List<string>();
		foreach (var pair in plannedRounds)
		{
			if (pair.Value <= 0)
			{
				continue;
			}
			if (!totals.ContainsKey(pair.Key))
			{
				totals[pair.Key] = 0;
				order.Add(pair.Key);
			}
			totals[pair.Key] += pair.Value;
		}
		var result = new List<KeyValuePair<string, int[]>>();
		foreach (string key in order)
		{
			int have = Math.Max(0, carried(key));
			if (totals[key] > have)
			{
				result.Add(new KeyValuePair<string, int[]>(key, new[] { totals[key], have }));
			}
		}
		return result;
	}

	// Picker ordering, like the Contacts window: hostile first, then the
	// chosen column. relation: 0 hostile, 1 unknown, 2 neutral, 3 friendly.
	internal enum Sort { Threat, Range, Name, Speed }

	internal static int Compare(Sort sort, int relationA, double rangeA, string nameA, double speedA, int relationB, double rangeB, string nameB, double speedB)
	{
		int c;
		switch (sort)
		{
		case Sort.Range:
			c = Nan(rangeA).CompareTo(Nan(rangeB));
			break;
		case Sort.Name:
			c = string.Compare(nameA ?? "", nameB ?? "", StringComparison.OrdinalIgnoreCase);
			break;
		case Sort.Speed:
			c = -Nan(speedA, double.MinValue).CompareTo(Nan(speedB, double.MinValue));
			break;
		default:
			c = relationA.CompareTo(relationB);
			if (c == 0)
			{
				c = Nan(rangeA).CompareTo(Nan(rangeB));
			}
			break;
		}
		return c != 0 ? c : string.Compare(nameA ?? "", nameB ?? "", StringComparison.OrdinalIgnoreCase);
	}

	private static double Nan(double value, double fallback = double.MaxValue) => double.IsNaN(value) ? fallback : value;

	// Search box: every space-separated word must appear in one of the fields.
	internal static bool Matches(string search, params string[] fields)
	{
		if (string.IsNullOrWhiteSpace(search))
		{
			return true;
		}
		foreach (string word in search.Split(new[] { ' ' }, StringSplitOptions.RemoveEmptyEntries))
		{
			bool found = false;
			foreach (string field in fields)
			{
				if (field != null && field.IndexOf(word, StringComparison.OrdinalIgnoreCase) >= 0)
				{
					found = true;
					break;
				}
			}
			if (!found)
			{
				return false;
			}
		}
		return true;
	}

	internal static string Compass(double degrees)
	{
		if (double.IsNaN(degrees) || double.IsInfinity(degrees))
		{
			return "-";
		}
		double d = degrees % 360.0;
		if (d < 0)
		{
			d += 360.0;
		}
		return (Math.Round(d) % 360.0).ToString("000", System.Globalization.CultureInfo.InvariantCulture);
	}
}
