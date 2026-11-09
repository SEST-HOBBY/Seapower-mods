using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text.RegularExpressions;

namespace Sest.RuntimeFixes;

internal static class CombatHistory
{
	private sealed class SavedId
	{
		internal string Value;
	}

	internal const string SessionKey = "SestCombatSessionV1";

	private static CombatHistoryStore store;

	private static object mission;

	private static CombatGameRecord pending;

	private static ConditionalWeakTable<object, SavedId> restored = new ConditionalWeakTable<object, SavedId>();

	private static object context;

	internal static string CurrentId => (pending != null) ? pending.Id : null;

	internal static List<CombatGameRecord> Games => (store != null) ? store.Games : new List<CombatGameRecord>();

	internal static bool ReadOnly => store != null && store.ReadOnly;

	internal static void Open(string path)
	{
		store = new CombatHistoryStore(path);
		mission = null;
		context = null;
		pending = null;
		restored = new ConditionalWeakTable<object, SavedId>();
	}

	internal static void RestoreSession(string id, object taskforce)
	{
		if (taskforce != null && !string.IsNullOrEmpty(id) && Regex.IsMatch(id, "\\A[0-9a-f]{32}\\z"))
		{
			restored.Remove(taskforce);
			restored.Add(taskforce, new SavedId
			{
				Value = id
			});
		}
	}

	internal static void Observe(object current, CombatGameRecord capture)
	{
		if (store == null)
		{
			return;
		}
		if (!object.ReferenceEquals(current, mission) || (capture != null && !object.ReferenceEquals(capture.Context, context)))
		{
			Finish();
			mission = current;
			pending = null;
			context = capture?.Context;
		}
		if (current != null && capture != null)
		{
			SavedId value = null;
			bool flag = capture.Context != null && restored.TryGetValue(capture.Context, out value);
			string text = ((!flag) ? null : value.Value);
			if (flag)
			{
				restored.Remove(capture.Context);
			}
			if (pending == null)
			{
				capture.Id = text ?? Guid.NewGuid().ToString("N");
			}
			else if (text != null && text != pending.Id)
			{
				Finish();
				capture.Id = text;
			}
			else
			{
                if (string.IsNullOrEmpty(pending.Source) && capture.Source.StartsWith("DCM:", StringComparison.Ordinal))
                {
                    pending.Source = capture.Source; pending.MissionIndex = capture.MissionIndex;
                }
				capture.Id = pending.Id;
				capture.Source = pending.Source;
				capture.MissionIndex = pending.MissionIndex;
				capture.Status = pending.Status;
				capture.EndedUtc = pending.EndedUtc;
			}
			pending = capture;
		}
	}

	internal static void Finish()
	{
		if (store == null || pending == null)
		{
			return;
		}
		if (pending.EndedUtc == 0)
		{
			pending.EndedUtc = DateTime.UtcNow.Ticks;
		}
		try
		{
			store.Put(pending);
		}
		catch (Exception error)
		{
			Api.LogFailure("combat game history could not be saved; native saves retained", error);
		}
	}

	internal static void CompleteCampaign(string source, int index, bool replay, CombatGameRecord capture)
	{
		if (pending != null)
		{
			Refresh(capture);
			pending.Source = source;
			pending.MissionIndex = index;
			pending.Status = ((!replay) ? "Completed" : "Replay");
			pending.EndedUtc = DateTime.UtcNow.Ticks;
			Finish();
		}
	}

	internal static void Refresh(CombatGameRecord capture)
	{
		if (pending == null || capture == null || capture.Context == null || !object.ReferenceEquals(capture.Context, pending.Context))
		{
			return;
		}
		foreach (CombatSideRecord old in pending.Sides)
		{
			CombatSideRecord combatSideRecord = capture.Sides.FirstOrDefault((CombatSideRecord s) => s.Name == old.Name);
			if (combatSideRecord == null || Shrank(old.Spent, combatSideRecord.Spent) || Shrank(old.Platforms, combatSideRecord.Platforms) || Shrank(old.Stores, combatSideRecord.Stores))
			{
				return;
			}
		}
		capture.Id = pending.Id;
		capture.Name = pending.Name;
		capture.Source = pending.Source;
		capture.MissionIndex = pending.MissionIndex;
		capture.Status = pending.Status;
		capture.EndedUtc = pending.EndedUtc;
		pending = capture;
	}

	private static bool Shrank(InventoryLedger old, InventoryLedger next)
	{
		return old.Ammo.Any((KeyValuePair<string, long> p) => InventoryLedger.Get(next.Ammo, p.Key) < p.Value);
	}
}
