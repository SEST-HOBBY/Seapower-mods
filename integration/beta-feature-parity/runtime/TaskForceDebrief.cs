using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;

namespace Sest.RuntimeFixes;

internal static class TaskForceDebrief
{
	private static MethodInfo readSnapshot;

	private static MethodInfo launchSection;

	private static MethodInfo launchPrefix;

	private static MethodInfo sectionExists;

	private static MethodInfo readDestroyed;

	private static MethodInfo sort;

	private static ConstructorInfo rowConstructor;

	private static FieldInfo missionIndex;

	private static PropertyInfo snapshotItems;

	private static PropertyInfo unitRows;

	private static bool active;

	internal static MethodInfo Bind(Assembly game)
	{
		Type type = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefViewModel");
		Type type2 = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceSaveManager");
		Type type3 = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceSnapshot");
		Type type4 = Api.Type(game, "SeaPower.LinearCampaignMission");
		Type type5 = Api.Type(game, "SeaPower.IniHandler");
		Type type6 = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefUnitRow");
		Type type7 = Api.Type(game, "SeapowerUI.ViewModels.LinearCampaignTaskForceBuilderRosterItem");
		Type propertyType = type7.GetProperty("CrewSkill", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static).PropertyType;
		readSnapshot = Api.Method(type2, "ReadSnapshot", type3, type5, typeof(string), typeof(string));
		launchSection = Api.Method(type2, "MissionLaunchSection", typeof(string), typeof(int));
		launchPrefix = Api.Method(type2, "MissionLaunchUnitPrefix", typeof(string), typeof(int));
		sectionExists = Api.Method(type5, "doesSectionExist", typeof(bool), typeof(string));
		readDestroyed = Api.Method(type5, "readValue", typeof(bool), typeof(string), typeof(string), typeof(bool), typeof(bool));
		snapshotItems = type3.GetProperty("Items", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		unitRows = type.GetProperty("UnitRows", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		missionIndex = type4.GetField("_index", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		if (snapshotItems == null || unitRows == null || missionIndex == null || missionIndex.FieldType != typeof(int))
		{
			throw new MissingMemberException("debrief snapshot/row/index API");
		}
		rowConstructor = type6.GetConstructor(new Type[11]
		{
			typeof(string),
			typeof(string),
			typeof(string),
			typeof(string),
			typeof(string),
			typeof(string),
			typeof(bool),
			typeof(bool),
			propertyType,
			typeof(int),
			typeof(string)
		});
		if (rowConstructor == null)
		{
			throw new MissingMethodException(type6.FullName, ".ctor");
		}
		sort = Api.Method(type, "SortDebriefUnitRows", typeof(IEnumerable<>).MakeGenericType(type6), typeof(IEnumerable<>).MakeGenericType(type6));
		active = true;
		return Api.Method(type, "ReadUnitRows", typeof(void), type5, type4);
	}

	internal static void Install(Assembly game)
	{
		MethodInfo target = Bind(game);
		Api.Postfix(target, typeof(TaskForceDebrief), "Postfix", "io.github.sest-hobby.taskforce-debrief");
		Api.Log("task-force debrief correction installed: append explicitly destroyed launch-snapshot hulls missing from section 3");
	}

	private static object Value(object obj, string name)
	{
		return obj.GetType().GetProperty(name, BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static).GetValue(obj, null);
	}

	private static string Text(object obj, string name)
	{
		return (Value(obj, name) as string) ?? string.Empty;
	}

	internal static void Postfix(object __instance, object __0, object __1)
	{
		if (!active || __instance == null || __0 == null || __1 == null)
		{
			return;
		}
		try
		{
			int num = (int)missionIndex.GetValue(__1);
			if (num < 1)
			{
				return;
			}
			string text = (string)launchSection.Invoke(null, new object[1] { num });
			if (!(bool)sectionExists.Invoke(__0, new object[1] { text }))
			{
				Api.Log("debrief mission " + num + ": exact launch snapshot absent; native rows retained");
				return;
			}
			object obj = readSnapshot.Invoke(null, new object[3]
			{
				__0,
				text,
				(string)launchPrefix.Invoke(null, new object[1] { num })
			});
			if (!(unitRows.GetValue(__instance, null) is IList list) || obj == null)
			{
				return;
			}
			HashSet<string> hashSet = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
			foreach (object item in list)
			{
				hashSet.Add(Text(item, "InstanceId"));
			}
			List<object> list2 = new List<object>();
			foreach (object item2 in (IEnumerable)snapshotItems.GetValue(obj, null))
			{
				if (item2 == null || !string.Equals(Text(item2, "UnitFolder"), "vessels", StringComparison.OrdinalIgnoreCase))
				{
					continue;
				}
				string text2 = Text(item2, "InstanceId");
				if (!string.IsNullOrWhiteSpace(text2) && !hashSet.Contains(text2) && !string.IsNullOrWhiteSpace(Text(item2, "UnitType")))
				{
					string text3 = "Mission_" + num + "_" + text2;
					if ((bool)sectionExists.Invoke(__0, new object[1] { text3 }) && (bool)readDestroyed.Invoke(__0, new object[4] { text3, "IsDestroyed", false, false }))
					{
						list2.Add(rowConstructor.Invoke(new object[11]
						{
							text2,
							Text(item2, "UnitType"),
							Text(item2, "UnitFolder"),
							Text(item2, "Category"),
							Text(item2, "VariantReference"),
							"Lost",
							true,
							false,
							Value(item2, "CrewSkill"),
							1,
							item2.GetType().GetProperty("Nation", Api.All)?.GetValue(item2, null) as string
						}));
						hashSet.Add(text2);
					}
				}
			}
			if (list2.Count == 0)
			{
				return;
			}
			IList list3 = (IList)Activator.CreateInstance(typeof(List<>).MakeGenericType(rowConstructor.DeclaringType));
			foreach (object item3 in list)
			{
				list3.Add(item3);
			}
			foreach (object item4 in list2)
			{
				list3.Add(item4);
			}
			List<object> list4 = new List<object>();
			foreach (object item5 in (IEnumerable)sort.Invoke(null, new object[1] { list3 }))
			{
				list4.Add(item5);
			}
			list.Clear();
			foreach (object item6 in list4)
			{
				list.Add(item6);
			}
			Api.Log("debrief mission " + num + ": restored " + list2.Count + " missing lost-hull row(s) for display only");
		}
		catch (Exception error)
		{
			active = false;
			Api.LogFailure("debrief correction disabled for this session", error);
		}
	}
}
