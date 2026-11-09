using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Reflection;
using System.Runtime.CompilerServices;

namespace Sest.RuntimeFixes;

internal static class CampaignInventory
{
	internal sealed class Capture
	{
		internal object Unit;

		internal string Kind;

		internal string Reference;

		internal string Type;

		internal long Before;

		internal Dictionary<string, long> Ammo;

		internal bool Incomplete;
	}

	internal sealed class Prior
	{
		internal bool Snapshot;

		internal string Player;

		internal string Enemy;

		internal string PlayerSpent;

		internal string EnemySpent;
	}

	internal const string MissionSaveKey = "SestCombatInventoryV1";

	internal const string PlayerKey = "SestCombatInventoryPlayerV1";

	internal const string EnemyKey = "SestCombatInventoryEnemyV1";

	internal const string PlayerSpentKey = "SestCombatExpenditurePlayerV1";

	internal const string EnemySpentKey = "SestCombatExpenditureEnemyV1";

	private static ConditionalWeakTable<object, InventoryLedger> ledgers = new ConditionalWeakTable<object, InventoryLedger>();

	private static FieldInfo objectType;

	private static FieldInfo parameters;

	private static FieldInfo objectRef;

	private static FieldInfo registers;

	private static FieldInfo deck;

	private static FieldInfo deckAmmo;

	private static FieldInfo deckAccountable;

	private static FieldInfo player;

	private static FieldInfo enemy;

	private static FieldInfo index;

	private static PropertyInfo amounts;

	private static PropertyInfo registerRef;

	private static PropertyInfo registerType;

	private static PropertyInfo registerDestroyed;

	private static PropertyInfo registerCount;

	private static MethodInfo write;

	private static MethodInfo read;

	private static MethodInfo saveFile;

	private static MethodInfo openState;

	private static MethodInfo sectionName;

	private static MethodInfo hasSnapshot;

	private static MethodInfo persist;

	private static MethodInfo registerTarget;

	private static MethodInfo saveTarget;

	private static MethodInfo loadTarget;

	private static MethodInfo campaignTarget;

	private static FieldInfo weaponsSpent;

	private static FieldInfo spentNumber;

	private static bool active;

	private static FieldInfo Field(Type type, string name, Type expected = null)
	{
		FieldInfo field = type.GetField(name, BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		if (field == null || (expected != null && field.FieldType != expected))
		{
			throw new MissingFieldException(type.FullName, name);
		}
		return field;
	}

	private static PropertyInfo Property(Type type, string name, Type expected = null)
	{
		PropertyInfo property = type.GetProperty(name, BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		if (property == null || (expected != null && property.PropertyType != expected))
		{
			throw new MissingMemberException(type.FullName, name);
		}
		return property;
	}

	internal static void Bind(Assembly game)
	{
		Type type = Api.Type(game, "SeaPower.ObjectBase");
		Type type2 = Api.Type(game, "SeaPower.ObjectBaseParameters");
		Type type3 = Api.Type(game, "SeaPower.Taskforce");
		Type type4 = Api.Type(game, "SeaPower.UnitRegister");
		Type type5 = Api.Type(game, "SeaPower.IniHandler");
		Type type6 = Api.Type(game, "SeaPower.SaveLoadManager");
		Type type7 = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel");
		Type type8 = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceModeRules");
		Type type9 = Api.Type(game, "SeaPower.LinearCampaignMission");
		Type type10 = Api.Type(game, "SeapowerUI.ViewModels.MissionDebriefViewModel");
		Type type11 = Api.Type(game, "SeaPower.Globals");
		objectType = Field(type, "_type");
		parameters = Field(type, "_obp", type2);
		objectRef = Field(type2, "_objectIniName", typeof(string));
		amounts = Property(type, "AmmunitionAmountDictionary");
		registers = Field(type3, "_unitStatusRegister");
		registerRef = Property(type4, "IniRef", typeof(string));
		registerType = Property(type4, "ObjectType");
		registerDestroyed = Property(type4, "IsDestroyed", typeof(bool));
		registerCount = Property(type4, "Count", typeof(int));
		deck = Field(type2, "_flightDeck");
		deckAmmo = Field(deck.FieldType, "_currentAmmo");
		deckAccountable = Field(deck.FieldType, "_accountableAmmunition");
		if (!objectType.FieldType.IsEnum || !typeof(IEnumerable).IsAssignableFrom(amounts.PropertyType) || !typeof(IEnumerable).IsAssignableFrom(registers.FieldType) || (deckAmmo.FieldType != typeof(float) && deckAmmo.FieldType != typeof(double)))
		{
			throw new MissingMemberException("inventory collection API");
		}
		write = Api.Method(type5, "writeValue", typeof(void), typeof(string), typeof(string), typeof(string));
		read = Api.Method(type5, "readValue", typeof(string), typeof(string), typeof(string), typeof(string), typeof(bool));
		saveFile = Api.Method(type5, "saveFile", typeof(void), typeof(bool));
		openState = Api.Method(type8, "OpenCampaignStateIni", type5);
		sectionName = Api.Method(type7, "GetDebriefSectionName", typeof(string), typeof(int));
		hasSnapshot = Api.Method(type7, "HasDebriefSnapshot", typeof(bool), type5, typeof(int));
		persist = Api.Method(type7, "PersistDebriefSectionsToCurrentCampaignSave", typeof(void), type5, typeof(int));
		index = Field(type9, "_index", typeof(int));
		player = Field(type11, "_playerTaskforce", type3);
		enemy = Field(type11, "_enemyTaskforce", type3);
		registerTarget = Api.Method(type3, "RegisterUnitStatus", typeof(void), typeof(bool), type, typeof(bool), typeof(bool));
		weaponsSpent = Field(type3, "_weaponsSpent");
		spentNumber = Field(Api.Type(game, "SeaPower.WeaponsSpent"), "_number", typeof(int));
		saveTarget = Api.Method(type6, "WriteTaskforceAarData", typeof(void), type5, type3, typeof(string));
		loadTarget = Api.Method(type6, "LoadTaskforceAarData", typeof(void), type5, type3, typeof(string));
		campaignTarget = Api.Method(type7, "SaveDebriefSnapshot", typeof(void), type9, type10);
		active = true;
		ledgers = new ConditionalWeakTable<object, InventoryLedger>();
	}

	internal static void Install(Assembly game)
	{
		Bind(game);
		try
		{
			Api.Hooks(registerTarget, typeof(CampaignInventory), "BeforeRegister", "AfterRegister", "io.github.sest-hobby.combat-inventories");
			Api.Postfix(saveTarget, typeof(CampaignInventory), "AfterSave", "io.github.sest-hobby.combat-inventories");
			Api.Postfix(loadTarget, typeof(CampaignInventory), "AfterLoad", "io.github.sest-hobby.combat-inventories");
			Api.Hooks(campaignTarget, typeof(CampaignInventory), "BeforeCampaignSave", "AfterCampaignSave", "io.github.sest-hobby.combat-inventories");
		}
		catch
		{
			active = false;
			throw;
		}
		Api.Log("combat inventory capture installed: raw remaining quantities in versioned SEST keys; hull, airframe and land costs remain separate");
	}

	private static string Kind(string type)
	{
		switch (type.ToLowerInvariant())
		{
		case "vessel":
		case "submarine":
			return "vessel";
		case "aircraft":
		case "helicopter":
			return "aircraft";
		case "landunit":
			return "land";
		default:
			return null;
		}
	}

	private static long Count(object tf, string reference, string type)
	{
		long num = 0L;
		foreach (object item in (IEnumerable)registers.GetValue(tf))
		{
			if ((bool)registerDestroyed.GetValue(item, null) && string.Equals((string)registerRef.GetValue(item, null), reference, StringComparison.OrdinalIgnoreCase) && string.Equals(registerType.GetValue(item, null).ToString(), type, StringComparison.OrdinalIgnoreCase))
			{
				num = checked(num + (int)registerCount.GetValue(item, null));
			}
		}
		return num;
	}

	private static InventoryLedger Ledger(object tf)
	{
		InventoryLedger inventoryLedger = ledgers.GetOrCreateValue(tf);
		if (inventoryLedger.Captured.Count > 0)
		{
			bool flag = false;
			foreach (object item in (IEnumerable)registers.GetValue(tf))
			{
				if ((bool)registerDestroyed.GetValue(item, null) && (int)registerCount.GetValue(item, null) > 0)
				{
					flag = true;
					break;
				}
			}
			if (!flag)
			{
				ledgers.Remove(tf);
				inventoryLedger = new InventoryLedger();
				ledgers.Add(tf, inventoryLedger);
			}
		}
		return inventoryLedger;
	}

	internal static void BeforeRegister(object __instance, bool __0, object __1, bool __2, out Capture __state)
	{
		__state = null;
		if (!active || __0 || !__2 || __instance == null || __1 == null)
		{
			return;
		}
		try
		{
			InventoryLedger inventoryLedger = Ledger(__instance);
			if (inventoryLedger.Seen.Contains(__1))
			{
				return;
			}
			string type = objectType.GetValue(__1).ToString();
			string text = Kind(type);
			if (text == null)
			{
				return;
			}
			object value = parameters.GetValue(__1);
			if (value == null)
			{
				return;
			}
			Capture capture = new Capture();
			capture.Unit = __1;
			capture.Type = type;
			capture.Kind = text;
			capture.Reference = (string)objectRef.GetValue(value);
			capture.Ammo = new Dictionary<string, long>(StringComparer.OrdinalIgnoreCase);
			Capture capture2 = capture;
			capture2.Before = Count(__instance, capture2.Reference, type);
			try
			{
				foreach (object item in (IEnumerable)amounts.GetValue(__1, null))
				{
					string key = (string)item.GetType().GetProperty("Key").GetValue(item, null);
					int num = (int)item.GetType().GetProperty("Value").GetValue(item, null);
					if (num < 0)
					{
						capture2.Incomplete = true;
					}
					else if (num > 0)
					{
						capture2.Ammo[key] = checked(InventoryLedger.Get(capture2.Ammo, key) + num);
					}
				}
			}
			catch (Exception)
			{
				capture2.Incomplete = true;
			}
			object value2 = deck.GetValue(value);
			if (value2 != null)
			{
				if (Convert.ToDouble(deckAmmo.GetValue(value2), CultureInfo.InvariantCulture) != 0.0)
				{
					capture2.Incomplete = true;
				}
				foreach (DictionaryEntry item2 in (IDictionary)deckAccountable.GetValue(value2))
				{
					if (Convert.ToInt64(item2.Value, CultureInfo.InvariantCulture) > 0)
					{
						capture2.Incomplete = true;
					}
				}
			}
			__state = capture2;
		}
		catch (Exception error)
		{
			Api.LogFailure("one combat inventory capture unavailable", error);
		}
	}

	internal static void AfterRegister(object __instance, Capture __state)
	{
		if (!active || __state == null)
		{
			return;
		}
		try
		{
			if (Count(__instance, __state.Reference, __state.Type) == __state.Before + 1)
			{
				InventoryLedger orCreateValue = ledgers.GetOrCreateValue(__instance);
				if (orCreateValue.Seen.Add(__state.Unit))
				{
					orCreateValue.Add(__state.Kind, __state.Ammo, __state.Incomplete);
				}
			}
		}
		catch (Exception error)
		{
			Api.LogFailure("combat inventory record unavailable", error);
		}
	}

	private static string Read(object ini, string section, string key)
	{
		return (string)read.Invoke(ini, new object[4]
		{
			section,
			key,
			string.Empty,
			false
		});
	}

	private static void Write(object ini, string section, string key, string value)
	{
		write.Invoke(ini, new object[3] { section, key, value });
	}

	internal static void AfterSave(object __0, object __1, string __2)
	{
		if (!active || __0 == null || __1 == null)
		{
			return;
		}
		try
		{
			Write(__0, __2, "SestCombatInventoryV1", Ledger(__1).Serialize());
			if (CombatHistory.CurrentId != null)
			{
				Write(__0, __2, "SestCombatSessionV1", CombatHistory.CurrentId);
			}
		}
		catch (Exception error)
		{
			Api.LogFailure("combat inventory save supplement unavailable", error);
		}
	}

	internal static void AfterLoad(object __0, object __1, string __2)
	{
		if (!active || __0 == null || __1 == null)
		{
			return;
		}
		try
		{
			InventoryLedger value = InventoryLedger.Parse(Read(__0, __2, "SestCombatInventoryV1")) ?? new InventoryLedger();
			ledgers.Remove(__1);
			ledgers.Add(__1, value);
			CombatHistory.RestoreSession(Read(__0, __2, "SestCombatSessionV1"), __1);
		}
		catch (Exception error)
		{
			Api.LogFailure("combat inventory load supplement unavailable", error);
		}
	}

	internal static void BeforeCampaignSave(object __0, out Prior __state)
	{
		__state = null;
		if (!active || __0 == null)
		{
			return;
		}
		try
		{
			int num = (int)index.GetValue(__0);
			object obj = openState.Invoke(null, null);
			if (obj != null && num >= 1)
			{
				string section = (string)sectionName.Invoke(null, new object[1] { num });
				__state = new Prior
				{
					Snapshot = (bool)hasSnapshot.Invoke(null, new object[2] { obj, num }),
					Player = Read(obj, section, "SestCombatInventoryPlayerV1"),
					Enemy = Read(obj, section, "SestCombatInventoryEnemyV1"),
					PlayerSpent = Read(obj, section, "SestCombatExpenditurePlayerV1"),
					EnemySpent = Read(obj, section, "SestCombatExpenditureEnemyV1")
				};
			}
		}
		catch (Exception error)
		{
			Api.LogFailure("combat inventory campaign precheck unavailable", error);
		}
	}

	internal static void AfterCampaignSave(object __0, Prior __state)
	{
		if (!active || __0 == null || __state == null)
		{
			return;
		}
		try
		{
			int num = (int)index.GetValue(__0);
			object obj = openState.Invoke(null, null);
			if (obj == null || !(bool)hasSnapshot.Invoke(null, new object[2] { obj, num }))
			{
				return;
			}
			string section = (string)sectionName.Invoke(null, new object[1] { num });
			string value = ((!__state.Snapshot) ? Serialize(player.GetValue(null)) : __state.Player);
			string value2 = ((!__state.Snapshot) ? Serialize(enemy.GetValue(null)) : __state.Enemy);
			string value3 = ((!__state.Snapshot) ? SerializeSpent(player.GetValue(null)) : __state.PlayerSpent);
			string value4 = ((!__state.Snapshot) ? SerializeSpent(enemy.GetValue(null)) : __state.EnemySpent);
			if (!string.IsNullOrEmpty(value))
			{
				Write(obj, section, "SestCombatInventoryPlayerV1", value);
			}
			if (!string.IsNullOrEmpty(value2))
			{
				Write(obj, section, "SestCombatInventoryEnemyV1", value2);
			}
			if (!string.IsNullOrEmpty(value3))
			{
				Write(obj, section, "SestCombatExpenditurePlayerV1", value3);
			}
			if (!string.IsNullOrEmpty(value4))
			{
				Write(obj, section, "SestCombatExpenditureEnemyV1", value4);
			}
			if (!string.IsNullOrEmpty(value) || !string.IsNullOrEmpty(value2) || !string.IsNullOrEmpty(value3) || !string.IsNullOrEmpty(value4))
			{
				saveFile.Invoke(obj, new object[1] { false });
				try
				{
					persist.Invoke(null, new object[2] { obj, num });
				}
				catch (Exception error)
				{
					Api.LogFailure("combat inventory not copied to the campaign save; it lasts until the campaign reloads", error);
				}
			}
			if (CombatHistory.CurrentId != null)
			{
				CombatHistory.CompleteCampaign(CampaignCosts.CampaignSource(obj), num, __state.Snapshot, CampaignCosts.CaptureLive("Campaign mission " + num));
			}
		}
		catch (Exception error2)
		{
			Api.LogFailure("combat inventory campaign supplement unavailable; native records retained", error2);
		}
	}

	private static string Serialize(object tf)
	{
		return (tf != null) ? Ledger(tf).Serialize() : string.Empty;
	}

	internal static InventoryLedger Current(object tf)
	{
		return (!active || tf == null) ? null : Ledger(tf);
	}

	private static string SerializeSpent(object tf)
	{
		return (tf != null) ? Spent(tf).Serialize() : string.Empty;
	}

	internal static InventoryLedger Spent(object tf)
	{
		InventoryLedger inventoryLedger = new InventoryLedger();
		if (tf == null || weaponsSpent == null)
		{
			return null;
		}
		foreach (DictionaryEntry item in (IDictionary)weaponsSpent.GetValue(tf))
		{
			int num = (int)spentNumber.GetValue(item.Value);
			if (num < 0)
			{
				inventoryLedger.Unknown++;
			}
			else if (num > 0)
			{
				inventoryLedger.Ammo[(string)item.Key] = num;
			}
		}
		return inventoryLedger;
	}
}
