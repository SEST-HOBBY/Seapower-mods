using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;

namespace Sest.RuntimeFixes {
internal static class CampaignCosts
{
	internal sealed class CostView
	{
		internal readonly List<string> Summary = new List<string>();

		internal readonly List<string> Details = new List<string>();

		internal readonly List<CostReportLine> SummaryRows = new List<CostReportLine>();

		internal readonly List<CostReportLine> DetailRows = new List<CostReportLine>();

		internal readonly string[] Notes = new string[3] { "+ ? = missing prices or quantities, including older saves and deck stock pools.", "Estimates cover expended weapons, destroyed platforms and their remaining stores.", "Crew, repairs, fuel burn, cargo and damage to surviving units are excluded." };

		internal string[] Lines => Summary.Concat(Details).Concat(Notes).ToArray();

		internal void AddSummary(CostLineKind kind, string text)
		{
			Summary.Add(text);
			SummaryRows.Add(new CostReportLine(kind, text));
		}

		internal void AddDetail(CostLineKind kind, string text)
		{
			Details.Add(text);
			DetailRows.Add(new CostReportLine(kind, text));
		}
	}

	private sealed class Side
	{
		internal CombatAmount Weapons = new CombatAmount();

		internal CombatAmount Ships = new CombatAmount();

		internal CombatAmount Air = new CombatAmount();

		internal CombatAmount Land = new CombatAmount();

		internal CombatAmount Stores = new CombatAmount();

		internal CombatAmount Losses => CombatAmount.Sum(Ships, Air, Land);

		internal CombatAmount Total => CombatAmount.Sum(Weapons, Ships, Air, Land, Stores);

		internal void Merge(Side other)
		{
			Weapons.Merge(other.Weapons);
			Ships.Merge(other.Ships);
			Air.Merge(other.Air);
			Land.Merge(other.Land);
			Stores.Merge(other.Stores);
		}
	}

	private sealed class Mission
	{
		internal int Index;

		internal Side Player = new Side();

		internal Side Enemy = new Side();
	}

	private static MethodInfo openState;

	private static MethodInfo hasSnapshot;

	private static MethodInfo sectionName;

	private static MethodInfo parseRows;

	private static MethodInfo reports;

	private static MethodInfo totals;

	private static MethodInfo data;

	private static MethodInfo openVirtual;

	private static MethodInfo openUnit;

	private static MethodInfo filePath;

	private static MethodInfo openCampaign;

	private static MethodInfo taskforceEnabled;

	private static MethodInfo campaignSave;

	private static PropertyInfo summaryRows;

	private static PropertyInfo ammoRef;

	private static PropertyInfo ammoType;

	private static PropertyInfo launched;

	private static PropertyInfo fired;

	private static FieldInfo missionIndex;

	private static FieldInfo rowRef;

	private static FieldInfo rowFolder;

	private static FieldInfo rowType;

	private static FieldInfo rowCount;

	private static FieldInfo rowDestroyed;

	private static ConstructorInfo summaryConstructor;

	private static FieldInfo liveRegisters;

	private static PropertyInfo liveRef;

	private static PropertyInfo liveType;

	private static PropertyInfo liveCount;

	private static PropertyInfo liveDestroyed;

	private static readonly List<FieldInfo> liveSides = new List<FieldInfo>();

	private static bool active;

	private static bool missingListsReported;

	private static readonly HashSet<string> warned = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

	private static readonly string[,] SavedKeys = new string[2, 5]
	{
		{ "Player", "PlayerWeaponReport", "LossRows", "SestCombatInventoryPlayerV1", "SestCombatExpenditurePlayerV1" },
		{ "Enemy", "EnemyWeaponReport", "KillRows", "SestCombatInventoryEnemyV1", "SestCombatExpenditureEnemyV1" }
	};

	internal static MethodInfo Bind(Assembly game)
	{
		Type type = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel");
		Type type2 = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefRegisterSnapshotRow");
		Type type3 = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefSummaryRow");
		Type type4 = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceModeRules");
		Type type5 = Api.Type(game, "SeaPower.IniHandler");
		Type type6 = Api.Type(game, "SeaPower.LinearCampaignMission");
		Type type7 = Api.Type(game, "SeaPower.TaskforceWeaponReport");
		Type type8 = Api.Type(game, "SeaPower.WeaponReportAmmoData");
		Type type9 = Api.Type(game, "SeaPower.Utils");
		openState = Api.Method(type4, "OpenCampaignStateIni", type5);
		hasSnapshot = Api.Method(type, "HasDebriefSnapshot", typeof(bool), type5, typeof(int));
		sectionName = Api.Method(type, "GetDebriefSectionName", typeof(string), typeof(int));
		parseRows = Api.Method(type, "TryParseRegisterRows", typeof(bool), typeof(string), typeof(List<>).MakeGenericType(type2).MakeByRefType());
		reports = Api.Method(type, "TryReadWeaponReports", typeof(bool), type5, typeof(int), type7.MakeByRefType(), type7.MakeByRefType(), type7.MakeByRefType());
		totals = Api.Method(type7, "BuildTaskforceTotals", typeof(Dictionary<, >).MakeGenericType(typeof(string), type8));
		data = Api.Method(type5, "get_Data", typeof(Dictionary<string, Dictionary<string, string>>));
		openVirtual = Api.Method(type9, "openVirtualIniFile", type5, typeof(string), typeof(string), typeof(string), typeof(bool));
		openUnit = Api.Method(type9, "openIniFile", type5, typeof(string), typeof(string), typeof(bool), typeof(bool));
		summaryRows = type.GetProperty("SummaryRows", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		missionIndex = type6.GetField("_index", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		summaryConstructor = type3.GetConstructor(new Type[4]
		{
			typeof(string),
			typeof(string),
			typeof(bool),
			typeof(bool)
		});
		rowRef = Field(type2, "IniRef", typeof(string));
		rowFolder = Field(type2, "Folder", typeof(string));
		rowType = Field(type2, "ObjectType", typeof(string));
		rowCount = Field(type2, "Count", typeof(int));
		rowDestroyed = Field(type2, "IsDestroyed", typeof(bool));
		ammoRef = Property(type8, "AmmoRef", typeof(string));
		ammoType = type8.GetProperty("AmmoType", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		launched = Property(type8, "Launched", typeof(int));
		fired = Property(type8, "ProjectileFired", typeof(int));
		if (summaryRows == null || missionIndex == null || missionIndex.FieldType != typeof(int) || summaryConstructor == null || ammoType == null || !ammoType.PropertyType.IsEnum)
		{
			throw new MissingMemberException("campaign combat costs API");
		}
		active = true;
		missingListsReported = false;
		warned.Clear();
		return Api.Method(type, "Load", typeof(void), type6);
	}

	internal static void BindLive(Assembly game)
	{
		Bind(game);
		Type type = Api.Type(game, "SeaPower.Taskforce");
		Type type2 = Api.Type(game, "SeaPower.UnitRegister");
		liveRegisters = Field(type, "_unitStatusRegister", typeof(List<>).MakeGenericType(type2));
		liveRef = Property(type2, "IniRef", typeof(string));
		liveType = type2.GetProperty("ObjectType", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		liveCount = Property(type2, "Count", typeof(int));
		liveDestroyed = Property(type2, "IsDestroyed", typeof(bool));
		if (liveType == null || !liveType.PropertyType.IsEnum)
		{
			throw new MissingMemberException("live unit-register type");
		}
		Type type3 = Api.Type(game, "SeaPower.Globals");
		liveSides.Clear();
		string[] array = new string[4] { "_playerTaskforce", "_enemyTaskforce", "_allyTaskforce", "_neutralTaskforce" };
		foreach (string name in array)
		{
			FieldInfo field = type3.GetField(name, BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
			if (field != null && field.FieldType == type)
			{
				liveSides.Add(field);
			}
		}
		if (liveSides.Count < 2)
		{
			throw new MissingMemberException("live player/enemy task forces");
		}
	}

	internal static void BindMenu(Assembly game)
	{
		BindLive(game);
		Type type = Api.Type(game, "SeaPower.IniHandler");
		Type type2 = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceModeRules");
		filePath = Api.Method(type, "getFilePath", typeof(string));
		openCampaign = Api.Method(type2, "OpenCampaignIni", type);
		taskforceEnabled = Api.Method(type2, "IsTaskForceModeEnabled", typeof(bool), type);
		campaignSave = Api.Method(Api.Type(game, "SeaPower.SaveLoadManager"), "GetGlobalCampaignSaveFilePath", typeof(string));
	}

	internal static bool TaskForceMenuAvailable()
	{
		try
		{
			object obj = openCampaign.Invoke(null, null);
			return obj != null && (bool)taskforceEnabled.Invoke(null, new object[1] { obj });
		}
		catch
		{
			return false;
		}
	}

	internal static string CurrentSource()
	{
		return CampaignSource(openState.Invoke(null, null));
	}

	private static string Hash(string text)
	{
		using (SHA256 sHA = SHA256.Create()) {
		return BitConverter.ToString(sHA.ComputeHash(Encoding.UTF8.GetBytes(text))).Replace("-", string.Empty).ToLowerInvariant();
}
	}

	internal static string CampaignSource(object ini)
	{
		string text = ((!(campaignSave == null)) ? ((string)campaignSave.Invoke(null, null)) : null);
		if (string.IsNullOrWhiteSpace(text))
		{
			return LegacySource(ini);
		}
		return Hash("campaign:" + text.Trim().Replace('\\', '/').ToLowerInvariant());
	}

	private static string LegacySource(object ini)
	{
		return (!(filePath == null) && ini != null) ? Hash(((string)filePath.Invoke(ini, null)) ?? string.Empty) : null;
	}

	private static string SideName(string field)
	{
		string text = field.Replace("_", string.Empty).Replace("Taskforce", string.Empty);
		return char.ToUpperInvariant(text[0]) + text.Substring(1);
	}

	private static string PlatformKind(string type)
	{
		switch ((type ?? string.Empty).ToLowerInvariant())
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

	private static void RawPlatform(CombatSideRecord side, string reference, string type, long count)
	{
		string text = PlatformKind(type);
		if (text == null || string.IsNullOrWhiteSpace(reference) || count <= 0)
		{
			side.Platforms.Unknown++;
			return;
		}
		string key = text + ":" + reference;
		checked
		{
			side.Platforms.Ammo[key] = InventoryLedger.Get(side.Platforms.Ammo, key) + count;
			side.Platforms.Captured[text] = InventoryLedger.Get(side.Platforms.Captured, text) + count;
		}
	}

	private static void RawStores(CombatSideRecord side, InventoryLedger ledger)
	{
		side.Stores = ((ledger != null) ? InventoryLedger.Parse(ledger.Serialize()) : new InventoryLedger());
		if (ledger == null && side.Platforms.Ammo.Count > 0)
		{
			side.Stores.Unknown++;
		}
		if (ledger == null)
		{
			return;
		}
		string[] array = new string[3] { "vessel", "aircraft", "land" };
		foreach (string key in array)
		{
			if (InventoryLedger.Get(ledger.Captured, key) != InventoryLedger.Get(side.Platforms.Captured, key))
			{
				side.Stores.Unknown++;
			}
		}
	}

	internal static CombatGameRecord CaptureLive(string name)
	{
		CombatGameRecord combatGameRecord = new CombatGameRecord();
		combatGameRecord.Name = name;
		CombatGameRecord combatGameRecord2 = combatGameRecord;
		foreach (FieldInfo liveSide in liveSides)
		{
			object value = liveSide.GetValue(null);
			if (value == null)
			{
				continue;
			}
			if (liveSide.Name == "_playerTaskforce")
			{
				combatGameRecord2.Context = value;
			}
			CombatSideRecord combatSideRecord = new CombatSideRecord();
			combatSideRecord.Name = SideName(liveSide.Name);
			combatSideRecord.Spent = CampaignInventory.Spent(value) ?? new InventoryLedger
			{
				Unknown = 1L
			};
			CombatSideRecord combatSideRecord2 = combatSideRecord;
			foreach (object item in (IEnumerable)liveRegisters.GetValue(value))
			{
				if ((bool)liveDestroyed.GetValue(item, null))
				{
					RawPlatform(combatSideRecord2, (string)liveRef.GetValue(item, null), liveType.GetValue(item, null).ToString(), (int)liveCount.GetValue(item, null));
				}
			}
			RawStores(combatSideRecord2, CampaignInventory.Current(value));
			combatGameRecord2.Sides.Add(combatSideRecord2);
		}
		return combatGameRecord2;
	}

	private static CombatSideRecord CaptureSavedSide(object report, string weapons, string losses, string stores, string captured, string name)
	{
		CombatSideRecord combatSideRecord = new CombatSideRecord();
		combatSideRecord.Name = name;
		CombatSideRecord combatSideRecord2 = combatSideRecord;
		InventoryLedger inventoryLedger = InventoryLedger.Parse(captured);
		if (inventoryLedger != null)
		{
			combatSideRecord2.Spent = inventoryLedger;
		}
		else if (weapons == null || (weapons.Length > 0 && report == null))
		{
			combatSideRecord2.Spent.Unknown++;
		}
		else if (weapons.Length > 0)
		{
			foreach (DictionaryEntry item in (IDictionary)totals.Invoke(report, null))
			{
				object value = item.Value;
				long num = (long)(int)launched.GetValue(value, null) + (long)(int)fired.GetValue(value, null);
				if (num < 0)
				{
					combatSideRecord2.Spent.Unknown++;
					continue;
				}
				string key = (string)ammoRef.GetValue(value, null);
				combatSideRecord2.Spent.Ammo[key] = checked(InventoryLedger.Get(combatSideRecord2.Spent.Ammo, key) + num);
			}
		}
		if (losses == null)
		{
			combatSideRecord2.Platforms.Unknown++;
		}
		else if (losses.Length > 0)
		{
			object[] array = new object[2] { losses, null };
			if (!(bool)parseRows.Invoke(null, array) || array[1] == null)
			{
				combatSideRecord2.Platforms.Unknown++;
			}
			else
			{
				foreach (object item2 in (IEnumerable)array[1])
				{
					if ((bool)rowDestroyed.GetValue(item2))
					{
						RawPlatform(combatSideRecord2, (string)rowRef.GetValue(item2), (string)rowType.GetValue(item2), (int)rowCount.GetValue(item2));
					}
				}
			}
		}
		RawStores(combatSideRecord2, InventoryLedger.Parse(stores));
		return combatSideRecord2;
	}

	private static Dictionary<string, string> Recovered(Dictionary<string, string> values, int index, object[] reportsArgs, string source, string legacy)
	{
		Dictionary<string, string> dictionary = values;
		for (int i = 0; i < 2; i++)
		{
			if (CombatPrices.Get(values, SavedKeys[i, 3]) != null)
			{
				continue;
			}
			CombatSideRecord combatSideRecord = CaptureSavedSide(reportsArgs[2 + i], CombatPrices.Get(values, SavedKeys[i, 1]), CombatPrices.Get(values, SavedKeys[i, 2]), null, CombatPrices.Get(values, SavedKeys[i, 4]), SavedKeys[i, 0]);
			if (combatSideRecord.Platforms.Ammo.Count == 0 || combatSideRecord.Platforms.Unknown > 0 || combatSideRecord.Spent.Unknown > 0)
			{
				continue;
			}
			CombatSideRecord combatSideRecord2 = null;
			int num = 0;
			foreach (CombatGameRecord game in CombatHistory.Games)
			{
				if (game.MissionIndex != index || game.Status != "Completed" || game.Source == null || (game.Source != source && game.Source != legacy))
				{
					continue;
				}
				foreach (CombatSideRecord side in game.Sides)
				{
					if (side.Name == SavedKeys[i, 0] && Same(side.Platforms, combatSideRecord.Platforms) && combatSideRecord.Spent.Ammo.All((KeyValuePair<string, long> p) => InventoryLedger.Get(side.Spent.Ammo, p.Key) >= p.Value))
					{
						combatSideRecord2 = side;
						num++;
					}
				}
			}
			if (num == 1)
			{
				if (dictionary == values)
				{
					dictionary = new Dictionary<string, string>(values, StringComparer.OrdinalIgnoreCase);
				}
				dictionary[SavedKeys[i, 3]] = combatSideRecord2.Stores.Serialize();
				if (CombatPrices.Get(values, SavedKeys[i, 4]) == null)
				{
					dictionary[SavedKeys[i, 4]] = combatSideRecord2.Spent.Serialize();
				}
			}
		}
		return dictionary;
	}

	private static bool Same(InventoryLedger a, InventoryLedger b)
	{
		return a.Unknown == 0 && b.Unknown == 0 && a.Ammo.Count == b.Ammo.Count && a.Ammo.All((KeyValuePair<string, long> p) => InventoryLedger.Get(b.Ammo, p.Key) == p.Value);
	}

	internal static List<CombatGameRecord> SavedGames()
	{
		List<CombatGameRecord> list = new List<CombatGameRecord>();
		if (!TaskForceMenuAvailable())
		{
			return list;
		}
		object obj = openState.Invoke(null, null);
		if (obj == null)
		{
			return list;
		}
		string text = CampaignSource(obj);
		string legacy = LegacySource(obj);
		Dictionary<string, Dictionary<string, string>> dictionary = Data(obj);
		Dictionary<string, Dictionary<string, string>> definitions = Data(openCampaign.Invoke(null, null));
		foreach (KeyValuePair<string, Dictionary<string, string>> item in dictionary)
		{
			Match match = Regex.Match(item.Key, "\\AMission_([0-9]+)_TaskForceDebrief\\z");
			if (match.Success && int.TryParse(match.Groups[1].Value, out var result) && result >= 1 && (bool)hasSnapshot.Invoke(null, new object[2] { obj, result }))
			{
				object[] array = new object[5] { obj, result, null, null, null };
				try
				{
					reports.Invoke(null, array);
				}
				catch
				{
				}
				Dictionary<string, string> dictionary2 = Recovered(item.Value, result, array, text, legacy);
				string name = MissionTitle(definitions, result, CombatPrices.Get(dictionary2, "MissionName"));
				CombatGameRecord combatGameRecord = new CombatGameRecord();
				combatGameRecord.Id = "saved:" + text + ":" + result;
				combatGameRecord.Name = name;
				combatGameRecord.Source = text;
				combatGameRecord.MissionIndex = result;
				combatGameRecord.CompletedAt = CompletionDate(CombatPrices.Get(item.Value, "CompletedAt"));
				combatGameRecord.Status = ((dictionary2 != item.Value) ? "Saved debrief + local record" : "Saved debrief");
				CombatGameRecord combatGameRecord2 = combatGameRecord;
				for (int i = 0; i < 2; i++)
				{
					combatGameRecord2.Sides.Add(CaptureSavedSide(array[2 + i], CombatPrices.Get(dictionary2, SavedKeys[i, 1]), CombatPrices.Get(dictionary2, SavedKeys[i, 2]), CombatPrices.Get(dictionary2, SavedKeys[i, 3]), CombatPrices.Get(dictionary2, SavedKeys[i, 4]), SavedKeys[i, 0]));
				}
				list.Add(combatGameRecord2);
			}
		}
		list.Sort((CombatGameRecord a, CombatGameRecord b) => b.MissionIndex.CompareTo(a.MissionIndex));
		return list;
	}

	internal static string MissionTitle(Dictionary<string, Dictionary<string, string>> definitions, int index, string savedName)
	{
		if (definitions != null && definitions.TryGetValue("Mission" + index, out var value) && string.Equals(CombatPrices.Get(value, "Type"), "Mission", StringComparison.OrdinalIgnoreCase))
		{
			string text = CombatPrices.Get(value, "Name_en");
			string text2 = CombatPrices.Get(value, "MissionSequenceName_en");
			if (!string.IsNullOrWhiteSpace(text))
			{
				return (!string.IsNullOrWhiteSpace(text2)) ? (text2 + " - " + text) : text;
			}
		}
		return (!string.IsNullOrWhiteSpace(savedName)) ? savedName : "Completed mission";
	}

	private static Side PriceRaw(CombatSideRecord raw, CombatPrices prices)
	{
		Side side = new Side();
		foreach (KeyValuePair<string, long> item in raw.Spent.Ammo)
		{
			side.Weapons.Add(Price(prices, "weapon", item.Key, "ammunition"), item.Value);
		}
		side.Weapons.MissingRecords = raw.Spent.Unknown;
		foreach (KeyValuePair<string, long> item2 in raw.Platforms.Ammo)
		{
			int num = item2.Key.IndexOf(':');
			if (num < 1)
			{
				side.Ships.MissingRecords++;
				continue;
			}
			string text = item2.Key.Substring(0, num);
			string reference = item2.Key.Substring(num + 1);
			if (text != "vessel" && text != "aircraft" && text != "land")
			{
				side.Ships.MissingRecords++;
				continue;
			}
			CombatAmount combatAmount = ((text == "vessel") ? side.Ships : ((!(text == "aircraft")) ? side.Land : side.Air));
			combatAmount.Add(Price(prices, text, reference, (text == "vessel") ? "vessels" : ((!(text == "aircraft")) ? "land_units" : "aircraft")), item2.Value);
		}
		side.Ships.MissingRecords += raw.Platforms.Unknown;
		foreach (KeyValuePair<string, long> item3 in raw.Stores.Ammo)
		{
			side.Stores.Add(Price(prices, "weapon", item3.Key, "ammunition"), item3.Value);
		}
		side.Stores.MissingRecords = raw.Stores.Unknown;
		return side;
	}

	private static string Basis(CombatPrices prices)
	{
		return "USD estimates | " + ((!prices.Current) ? "Reference-year catalog prices" : ("Catalog year: " + prices.Basis));
	}

	private static CostLineKind TotalKind(string name)
	{
		return (name == "Player") ? CostLineKind.PlayerTotal : ((!(name == "Enemy")) ? CostLineKind.Amount : CostLineKind.EnemyTotal);
	}

	private static void Summary(CostView view, string name, Side side)
	{
		view.AddSummary(TotalKind(name), name + " total  " + side.Total.Text);
		view.AddSummary(CostLineKind.Breakdown, "   Weapons " + side.Weapons.Text + "  Ships " + side.Ships.Text + "  Aircraft " + side.Air.Text);
		view.AddSummary(CostLineKind.Breakdown, "   Land " + side.Land.Text + "  Stores lost with units " + side.Stores.Text);
	}

	internal static CostView CampaignView(List<CombatGameRecord> games)
	{
		CostView costView = new CostView();
		CombatPrices combatPrices = Prices();
		if (combatPrices == null)
		{
			costView.AddSummary(CostLineKind.Body, "Enable Combat Cost Tracker and restart to load prices.");
			return costView;
		}
		if (games.Count == 0)
		{
			costView.AddSummary(CostLineKind.Body, "No completed missions in this campaign yet.");
			costView.AddDetail(CostLineKind.Body, "Totals appear after the first mission debrief.");
			return costView;
		}
		Dictionary<string, Side> dictionary = new Dictionary<string, Side>();
		List<CostReportLine> list = new List<CostReportLine>();
		foreach (CombatGameRecord item in games.OrderByDescending((CombatGameRecord g) => g.MissionIndex))
		{
			List<string> list2 = new List<string>();
			foreach (CombatSideRecord side3 in item.Sides)
			{
				Side side = PriceRaw(side3, combatPrices);
				if (!dictionary.TryGetValue(side3.Name, out var value))
				{
					value = (dictionary[side3.Name] = new Side());
				}
				value.Merge(side);
				list2.Add(side3.Name + " " + side.Total.Text);
			}
			list.Add(new CostReportLine(CostLineKind.Mission, Clip(item.Name, 256)));
			list.Add(new CostReportLine(CostLineKind.Amount, "   " + string.Join(" | ", list2)));
			list.Add(new CostReportLine(CostLineKind.Time, "   Completed: " + ((!item.CompletedAt.HasValue) ? "Not recorded" : item.CompletedAt.Value.ToString("d MMM yyyy HH:mm'Z'", CultureInfo.InvariantCulture))));
		}
		costView.AddSummary(CostLineKind.Basis, Basis(combatPrices) + " | " + games.Count + " completed mission" + ((games.Count != 1) ? "s" : string.Empty) + ".");
		string[] array = new string[2] { "Player", "Enemy" };
		foreach (string text in array)
		{
			if (dictionary.TryGetValue(text, out var value2))
			{
				Summary(costView, text, value2);
			}
		}
		costView.AddDetail(CostLineKind.Section, "Completed missions, latest first");
		foreach (CostReportLine item2 in list)
		{
			costView.AddDetail(item2.Kind, item2.Text);
		}
		return costView;
	}

	internal static string[] CampaignLines(List<CombatGameRecord> games)
	{
		return CampaignView(games).Lines;
	}

	private static DateTime? CompletionDate(string value)
	{
		DateTime result;
		return (!DateTime.TryParse(value, CultureInfo.InvariantCulture, DateTimeStyles.RoundtripKind, out result)) ? null : new DateTime?(result);
	}

	private static string Full(CombatAmount amount)
	{
		return "$" + amount.Known.ToString("#,0.##", CultureInfo.InvariantCulture) + ((!amount.Incomplete) ? string.Empty : " + ?");
	}

	private static void Categories(CostView view, InventoryLedger ledger, CombatPrices prices, string noun)
	{
		SortedDictionary<string, CombatAmount> sortedDictionary = new SortedDictionary<string, CombatAmount>(StringComparer.OrdinalIgnoreCase);
		foreach (KeyValuePair<string, long> item in ledger.Ammo)
		{
			CombatPrice combatPrice = Price(prices, "weapon", item.Key, "ammunition");
			if (!combatPrice.Ignored)
			{
				string key = ((!string.IsNullOrEmpty(combatPrice.Category)) ? combatPrice.Category : "Other");
				if (!sortedDictionary.TryGetValue(key, out var value))
				{
					value = (sortedDictionary[key] = new CombatAmount());
				}
				value.Add(combatPrice, item.Value);
			}
		}
		foreach (KeyValuePair<string, CombatAmount> item2 in sortedDictionary)
		{
			view.AddDetail(CostLineKind.Category, "   " + item2.Key + ": " + item2.Value.Count.ToString("N0", CultureInfo.InvariantCulture) + " " + noun + " | " + Full(item2.Value));
		}
		if (ledger.Unknown > 0)
		{
			view.AddDetail(CostLineKind.Category, "   Some quantities were not captured (+ ?).");
		}
	}

	internal static CostView LiveView(CombatGameRecord game)
	{
		CostView costView = new CostView();
		CombatPrices combatPrices = Prices();
		if (combatPrices == null)
		{
			costView.AddSummary(CostLineKind.Body, "Enable Combat Cost Tracker and restart to load prices.");
			return costView;
		}
		costView.AddSummary(CostLineKind.Basis, Basis(combatPrices));
		foreach (CombatSideRecord side2 in game.Sides)
		{
			Side side = PriceRaw(side2, combatPrices);
			if (!(side2.Name != "Player") || !(side2.Name != "Enemy") || side.Total.Count != 0 || !(side.Total.Known == 0m))
			{
				costView.AddSummary(TotalKind(side2.Name), side2.Name + " total  " + side.Total.Text);
				costView.AddDetail(CostLineKind.Section, side2.Name + " - expenditure and losses");
				costView.AddDetail(CostLineKind.Body, "Weapons expended: " + Full(side.Weapons));
				Categories(costView, side2.Spent, combatPrices, "expended");
				costView.AddDetail(CostLineKind.Body, "Ships & submarines destroyed: " + side.Ships.Count + " | " + Full(side.Ships));
				costView.AddDetail(CostLineKind.Body, "Aircraft destroyed: " + side.Air.Count + " | " + Full(side.Air));
				costView.AddDetail(CostLineKind.Body, "Land units destroyed: " + side.Land.Count + " | " + Full(side.Land));
				costView.AddDetail(CostLineKind.Body, "Stores lost with destroyed units: " + Full(side.Stores));
				Categories(costView, side2.Stores, combatPrices, "lost");
				costView.AddDetail(CostLineKind.Spacer, string.Empty);
			}
		}
		return costView;
	}

	private static string Clip(string text, int length)
	{
		text = (text ?? "Mission").Replace('\n', ' ').Replace('\r', ' ').Trim();
		return (text.Length <= length) ? text : (text.Substring(0, length - 1) + "…");
	}

	private static FieldInfo Field(Type type, string name, Type expected)
	{
		FieldInfo field = type.GetField(name, BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		if (field == null || field.FieldType != expected)
		{
			throw new MissingFieldException(type.FullName, name);
		}
		return field;
	}

	private static PropertyInfo Property(Type type, string name, Type expected)
	{
		PropertyInfo property = type.GetProperty(name, BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		if (property == null || property.PropertyType != expected)
		{
			throw new MissingMemberException(type.FullName, name);
		}
		return property;
	}

	internal static void Install(Assembly game)
	{
		MethodInfo target = Bind(game);
		Api.Postfix(target, typeof(CampaignCosts), "Postfix", "io.github.sest-hobby.campaign-combat-costs");
		Api.Log("campaign combat costs installed: saved debrief weapons, ship, air and land losses; independent of tracker display");
	}

	private static Dictionary<string, Dictionary<string, string>> Data(object ini)
	{
		if (ini == null)
		{
			return new Dictionary<string, Dictionary<string, string>>();
		}
		return (Dictionary<string, Dictionary<string, string>>)data.Invoke(ini, null);
	}

	private static Dictionary<string, Dictionary<string, string>> Catalog(string name, string folder = "systems")
	{
		return Data(openVirtual.Invoke(null, new object[4] { folder, name, name, false }));
	}

	private static CombatPrices Prices()
	{
		Dictionary<string, Dictionary<string, Dictionary<string, string>>> dictionary = new Dictionary<string, Dictionary<string, Dictionary<string, string>>>();
		string[] array = new string[3] { "weapon", "vessel", "aircraft" };
		foreach (string text in array)
		{
			dictionary[text] = Catalog(text + "costs");
			if (CombatPrices.Section(dictionary[text], "Costs").Count == 0)
			{
				return null;
			}
		}
		dictionary["land"] = Catalog("sest_land_costs");
		return new CombatPrices(dictionary, Catalog("config", "systems/combatcosts"), delegate(string folder, string reference)
		{
			object ini = openUnit.Invoke(null, new object[4]
			{
				"/" + folder,
				"/" + reference + ".ini",
				false,
				true
			});
			return CombatPrices.Section(Data(ini), "General");
		});
	}

	private static CombatPrice Price(CombatPrices prices, string kind, string reference, string folder, string type = null)
	{
		try
		{
			CombatPrice combatPrice = prices.Read(kind, reference, folder, type);
			if (!combatPrice.Amount.HasValue && !combatPrice.Ignored)
			{
				Warn(kind + " " + reference + ": no " + prices.Basis + " price");
			}
			return combatPrice;
		}
		catch (Exception ex)
		{
			Warn(kind + " " + reference + ": " + ex.GetType().Name);
			return new CombatPrice();
		}
	}

	private static void Warn(string message)
	{
		if (warned.Count < 20 && warned.Add(message))
		{
			Api.Log("combat costs: " + message);
		}
	}

	private static void Weapons(Side side, CombatPrices prices, object report, string raw, string captured = null)
	{
		InventoryLedger inventoryLedger = InventoryLedger.Parse(captured);
		if (inventoryLedger != null)
		{
			foreach (KeyValuePair<string, long> item in inventoryLedger.Ammo)
			{
				side.Weapons.Add(Price(prices, "weapon", item.Key, "ammunition"), item.Value);
			}
			side.Weapons.MissingRecords = inventoryLedger.Unknown;
		}
		else if (raw == null)
		{
			side.Weapons.MissingRecords++;
		}
		else
		{
			if (raw.Length == 0)
			{
				return;
			}
			if (report != null)
			{
				foreach (DictionaryEntry item2 in (IDictionary)totals.Invoke(report, null))
				{
					object value = item2.Value;
					long num = (long)(int)launched.GetValue(value, null) + (long)(int)fired.GetValue(value, null);
					if (num < 0)
					{
						side.Weapons.MissingRecords++;
					}
					else
					{
						string reference = (string)ammoRef.GetValue(value, null);
						string type = ammoType.GetValue(value, null).ToString();
						side.Weapons.Add(Price(prices, "weapon", reference, "ammunition", type), num);
					}
				}
				return;
			}
			side.Weapons.MissingRecords++;
		}
	}

	private static void Losses(Side side, CombatPrices prices, string raw)
	{
		if (raw == null)
		{
			side.Ships.MissingRecords++;
		}
		else
		{
			if (raw.Length == 0)
			{
				return;
			}
			object[] array = new object[2] { raw, null };
			if ((bool)parseRows.Invoke(null, array) && array[1] != null)
			{
				foreach (object item in (IEnumerable)array[1])
				{
					if ((bool)rowDestroyed.GetValue(item))
					{
						int num = (int)rowCount.GetValue(item);
						if (num <= 0)
						{
							side.Ships.MissingRecords++;
						}
						else
						{
							string reference = (string)rowRef.GetValue(item);
							string folder = (string)rowFolder.GetValue(item);
							string type = (string)rowType.GetValue(item);
							AddPlatform(side, prices, reference, folder, type, num);
						}
					}
				}
				return;
			}
			side.Ships.MissingRecords++;
		}
	}

	private static void AddPlatform(Side side, CombatPrices prices, string reference, string folder, string type, int count)
	{
		string kind;
		CombatAmount combatAmount;
		if (string.Equals(type, "Vessel", StringComparison.OrdinalIgnoreCase) || string.Equals(type, "Submarine", StringComparison.OrdinalIgnoreCase))
		{
			kind = "vessel";
			folder = ((!string.IsNullOrWhiteSpace(folder)) ? folder : "vessels");
			combatAmount = side.Ships;
		}
		else if (string.Equals(type, "Aircraft", StringComparison.OrdinalIgnoreCase) || string.Equals(type, "Helicopter", StringComparison.OrdinalIgnoreCase))
		{
			kind = "aircraft";
			folder = "aircraft";
			combatAmount = side.Air;
		}
		else
		{
			if (!string.Equals(folder, "land_units", StringComparison.OrdinalIgnoreCase) && !string.Equals(type, "LandUnit", StringComparison.OrdinalIgnoreCase))
			{
				side.Ships.MissingRecords++;
				return;
			}
			kind = "land";
			folder = "land_units";
			combatAmount = side.Land;
		}
		combatAmount.Add(Price(prices, kind, reference, folder), count);
	}

	private static void Inventories(Side side, CombatPrices prices, string saved)
	{
		InventoryLedger inventoryLedger = InventoryLedger.Parse(saved);
		if (inventoryLedger == null)
		{
			if (side.Losses.Count > 0)
			{
				side.Stores.MissingRecords++;
			}
			return;
		}
		foreach (KeyValuePair<string, long> item in inventoryLedger.Ammo)
		{
			side.Stores.Add(Price(prices, "weapon", item.Key, "ammunition"), item.Value);
		}
		side.Stores.MissingRecords = inventoryLedger.Unknown;
		if (InventoryLedger.Get(inventoryLedger.Captured, "vessel") != side.Ships.Count || InventoryLedger.Get(inventoryLedger.Captured, "aircraft") != side.Air.Count || InventoryLedger.Get(inventoryLedger.Captured, "land") != side.Land.Count)
		{
			side.Stores.MissingRecords++;
		}
	}

	private static Mission Read(object ini, Dictionary<string, string> section, int index, CombatPrices prices)
	{
		Mission mission = new Mission();
		mission.Index = index;
		Mission mission2 = mission;
		object[] array = new object[5] { ini, index, null, null, null };
		try
		{
			reports.Invoke(null, array);
		}
		catch (Exception)
		{
			Warn("one native weapon report could not be parsed; retained captures are still used");
		}
		Weapons(mission2.Player, prices, array[2], CombatPrices.Get(section, "PlayerWeaponReport"), CombatPrices.Get(section, "SestCombatExpenditurePlayerV1"));
		Weapons(mission2.Enemy, prices, array[3], CombatPrices.Get(section, "EnemyWeaponReport"), CombatPrices.Get(section, "SestCombatExpenditureEnemyV1"));
		Losses(mission2.Player, prices, CombatPrices.Get(section, "LossRows"));
		Losses(mission2.Enemy, prices, CombatPrices.Get(section, "KillRows"));
		Inventories(mission2.Player, prices, CombatPrices.Get(section, "SestCombatInventoryPlayerV1"));
		Inventories(mission2.Enemy, prices, CombatPrices.Get(section, "SestCombatInventoryEnemyV1"));
		return mission2;
	}

	private static string Pair(CombatAmount player, CombatAmount enemy)
	{
		return "Player " + player.Text + " | Enemy " + enemy.Text;
	}

	private static string DebriefPair(CombatAmount player, CombatAmount enemy)
	{
		return "P " + player.Text + " | E " + enemy.Text;
	}

	internal static void Postfix(object __instance, object __0)
	{
		if (!active || __instance == null || __0 == null)
		{
			return;
		}
		IList list = null;
		int num = 0;
		try
		{
			int num2 = (int)missionIndex.GetValue(__0);
			object obj = openState.Invoke(null, null);
			if (obj == null || !(bool)hasSnapshot.Invoke(null, new object[2] { obj, num2 }))
			{
				return;
			}
			CombatPrices combatPrices = Prices();
			if (combatPrices == null)
			{
				if (!missingListsReported)
				{
					missingListsReported = true;
					Api.Log("combat costs: tracker price lists not enabled; debrief rows not shown");
				}
				return;
			}
			Dictionary<string, Dictionary<string, string>> dictionary = Data(obj);
			Mission mission = new Mission();
			Mission mission2 = null;
			int num3 = 0;
			string source = CampaignSource(obj);
			string legacy = LegacySource(obj);
			foreach (KeyValuePair<string, Dictionary<string, string>> item in dictionary)
			{
				Match match = Regex.Match(item.Key, "\\AMission_([0-9]+)_TaskForceDebrief\\z", RegexOptions.CultureInvariant);
				if (match.Success && int.TryParse(match.Groups[1].Value, out var result) && result >= 1 && string.Equals((string)sectionName.Invoke(null, new object[1] { result }), item.Key, StringComparison.OrdinalIgnoreCase) && (bool)hasSnapshot.Invoke(null, new object[2] { obj, result }))
				{
					object[] array = new object[5] { obj, result, null, null, null };
					try
					{
						reports.Invoke(null, array);
					}
					catch
					{
					}
					Mission mission3 = Read(obj, Recovered(item.Value, result, array, source, legacy), result, combatPrices);
					num3++;
					mission.Player.Merge(mission3.Player);
					mission.Enemy.Merge(mission3.Enemy);
					if (result == num2)
					{
						mission2 = mission3;
					}
				}
			}
			if (mission2 == null)
			{
				return;
			}
			List<object> rows = new List<object>();
			Action<string, string> action = delegate(string label, string value)
			{
				rows.Add(summaryConstructor.Invoke(new object[4] { label, value, false, false }));
			};
			action("Cost: Mission", DebriefPair(mission2.Player.Total, mission2.Enemy.Total));
			action("Cost: Campaign", DebriefPair(mission.Player.Total, mission.Enemy.Total));
			action("Details (USD)", "F11 - P: Player, E: Enemy");
			list = summaryRows.GetValue(__instance, null) as IList;
			if (list == null)
			{
				throw new InvalidOperationException("summary rows are not a mutable native collection");
			}
			num = list.Count;
			foreach (object item2 in rows)
			{
				list.Add(item2);
			}
			Api.Log("combat costs mission " + num2 + " (" + combatPrices.Basis + "): " + Pair(mission2.Player.Total, mission2.Enemy.Total) + "; campaign " + num3 + ": " + Pair(mission.Player.Total, mission.Enemy.Total) + "; saved quantities only; debrief re-pricing writes no data");
		}
		catch (Exception error)
		{
			if (list != null)
			{
				try
				{
					while (list.Count > num)
					{
						list.RemoveAt(list.Count - 1);
					}
				}
				catch
				{
				}
			}
			active = false;
			Api.LogFailure("campaign combat costs disabled for this session; native debrief retained", error);
		}
	}
}

}
