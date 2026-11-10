using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Security.Cryptography;

namespace Sest.RuntimeFixes;

internal static class F11CombatCosts
{
	private const string TrackerHash = "8f7195ff1540d1901446b3783789c84e1f76bebe943da7606afd85f9dd3d78bc";

	private static bool attached;

	private static bool stopped;

	private static bool menuShown;

	private static bool wasLive;

	private static double nextAttach;

	private static double nextCapture;

	private static double nextLines;

	private static FieldInfo ready;

	private static FieldInfo visible;
	private static FieldInfo visibility;

	private static FieldInfo missionActive;

	private static FieldInfo mission;

	private static FieldInfo toggle;

	private static PropertyInfo missionPath;

	private static MethodInfo keyDown;

	private static MethodInfo getKey;

	private static CampaignCosts.CostView view;

	private static string campaignScope;

	private static double Now => (double)Stopwatch.GetTimestamp() / (double)Stopwatch.Frequency;

	private static FieldInfo Field(Type type, string name, Type expected = null)
	{
		FieldInfo field = type.GetField(name, BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		if (field == null || (expected != null && field.FieldType != expected))
		{
			throw new MissingFieldException(type.FullName, name);
		}
		return field;
	}

	internal static void Install(Assembly native, string historyPath)
	{
		CampaignCosts.BindMenu(native);
		CombatHistory.Open(historyPath);
        WorldOperations.Install(Path.Combine(Path.GetDirectoryName(historyPath), "world-service-v1.txt"));
		// Beta moved this value from a field to a property. Bind the exact
		// inspected getter instead of weakening the native-build guard.
		missionPath = BindMissionPath(native);
		MethodInfo target = Api.Method(Api.Type(native, "SeaPower.GameMain"), "Update", typeof(void));
		MethodInfo target2 = Api.Method(Api.Type(native, "SeaPower.GameMain"), "OnDestroy", typeof(void));
		try
		{
			Api.Postfix(target, typeof(F11CombatCosts), "Poll", "io.github.sest-hobby.f11-cost-bootstrap");
			Api.Hooks(target2, typeof(F11CombatCosts), "BeforeDestroy", null, "io.github.sest-hobby.f11-cost-bootstrap");
			AppDomain.CurrentDomain.AssemblyLoad += TrackerLoaded;
		}
		catch
		{
			stopped = true;
			throw;
		}
		Api.Log("F11 campaign panel awaiting the enabled Combat Cost Tracker");
		Poll();
	}

	internal static PropertyInfo BindMissionPath(Assembly native)
	{
		var property = Api.Type(native, "SeaPower.Globals").GetProperty("currentMissionFilePath", Api.All);
		if (property == null || property.PropertyType != typeof(string) ||
		    property.GetGetMethod(true) == null || !property.GetGetMethod(true).IsStatic)
			throw new MissingMemberException("beta Globals.currentMissionFilePath property");
		return property;
	}

	private static void TrackerLoaded(object sender, AssemblyLoadEventArgs args)
	{
		if (attached || stopped)
		{
			return;
		}
		try
		{
			if (!(args.LoadedAssembly.GetType("WeaponCostsMod.Overlay", throwOnError: false) == null))
			{
				nextAttach = 0.0;
				Poll();
			}
		}
		catch (Exception error)
		{
			stopped = true;
			Api.LogFailure("deferred F11 attachment unavailable", error);
		}
	}

	internal static void Poll()
	{
        WorldOperations.Poll();
        CoordinatedStrikeRefinements.Poll();
		if (attached || stopped || Now < nextAttach)
		{
			return;
		}
		nextAttach = Now + 1.0;
		Assembly[] assemblies = AppDomain.CurrentDomain.GetAssemblies();
		foreach (Assembly assembly in assemblies)
		{
			if (assembly.GetType("WeaponCostsMod.Overlay", throwOnError: false) == null)
			{
				continue;
			}
			try
			{
				string text;
				using (FileStream inputStream = File.OpenRead(assembly.Location))
				{
					using SHA256 sHA = SHA256.Create();
					text = BitConverter.ToString(sHA.ComputeHash(inputStream)).Replace("-", string.Empty).ToLowerInvariant();
				}
				if (text != "8f7195ff1540d1901446b3783789c84e1f76bebe943da7606afd85f9dd3d78bc")
				{
					stopped = true;
					Api.Log("F11 campaign totals inactive: uninspected Combat Cost Tracker " + text);
					break;
				}
				Bind(assembly);
				Type type = Api.Type(assembly, "WeaponCostsMod.Overlay");
				Api.Postfix(Api.Method(type, "Update", typeof(void)), typeof(F11CombatCosts), "AfterUpdate", "io.github.sest-hobby.cumulative-combat-costs");
				Api.Hooks(Api.Method(type, "OnGUI", typeof(void)), typeof(F11CombatCosts), "BeforeGUI", null, "io.github.sest-hobby.cumulative-combat-costs");
				Api.Log("F11 campaign combat costs installed: native movable windows, mission detail and complete scrollable campaign history");
				break;
			}
			catch (Exception error)
			{
				stopped = true;
				attached = false;
				Api.LogFailure("F11 campaign totals not installed; original tracker retained", error);
				break;
			}
		}
	}

	internal static void BeforeDestroy()
	{
		NativeCombatSurface.Close();
		if (CombatHistory.CurrentId != null)
		{
			try
			{
				CombatHistory.Refresh(CampaignCosts.CaptureLive("Game"));
			}
			catch (Exception error)
			{
				Api.LogFailure("final game cost refresh unavailable", error);
			}
			CombatHistory.Finish();
		}
	}

	internal static void Bind(Assembly tracker)
	{
		Type type = Api.Type(tracker, "WeaponCostsMod.Overlay");
		ready = Field(type, "ready", typeof(bool));
		visibility = Field(type, "visibility");
		visible = Field(visibility.FieldType, "Expanded", typeof(bool));
		missionActive = Field(type, "missionActive", typeof(bool));
		mission = Field(type, "mission");
		toggle = Field(type, "toggle");
		Type type2 = Api.FindType("UnityEngine.Input");
		Type type3 = Api.FindType("UnityEngine.KeyCode");
		keyDown = Api.Method(type2, "GetKeyDown", typeof(bool), type3);
		getKey = Api.Method(type2, "GetKey", typeof(bool), type3);
		NativeCombatSurface.Bind();
		attached = true;
		stopped = false;
		menuShown = false;
		wasLive = false;
		nextLines = (nextCapture = 0.0);
		view = null;
		campaignScope = null;
	}

	private static bool Modified()
	{
		Type enumType = Api.FindType("UnityEngine.KeyCode");
		string[] array = new string[6] { "LeftControl", "RightControl", "LeftAlt", "RightAlt", "LeftShift", "RightShift" };
		foreach (string value in array)
		{
			if ((bool)getKey.Invoke(null, new object[1] { Enum.Parse(enumType, value) }))
			{
				return true;
			}
		}
		return false;
	}

	internal static void AfterUpdate(object __instance)
	{
        WorldOperations.Poll();
        if (WorldOperations.StrategicActive) return;
		if (!attached || stopped || !(bool)ready.GetValue(__instance))
		{
			return;
		}
		try
		{
			bool flag = (bool)missionActive.GetValue(__instance);
			if (!NativeCombatSurface.EnsureReady(flag))
			{
				return;
			}
			if (flag != wasLive)
			{
				menuShown = false;
				wasLive = flag;
				nextLines = 0.0;
				view = null;
				NativeCombatSurface.Close();
			}
			if (!flag && CampaignCosts.TaskForceMenuAvailable() && !Modified() && (bool)keyDown.Invoke(null, new object[1] { toggle.GetValue(__instance) }))
			{
				menuShown = !menuShown;
				nextLines = 0.0;
			}
			if (Now >= nextCapture)
			{
				nextCapture = Now + 0.5;
				string text = ((!(missionPath == null)) ? ((string)missionPath.GetValue(null, null)) : null);
				string text2 = ((!string.IsNullOrWhiteSpace(text)) ? Path.GetFileNameWithoutExtension(text) : "Game");
				if (text2.Length > 256)
				{
					text2 = text2.Substring(0, 256);
				}
				CombatHistory.Observe((!flag) ? null : mission.GetValue(__instance), (!flag) ? null : CampaignCosts.CaptureLive(text2));
			}
			SyncWindow(__instance, flag);
		}
		catch (Exception error)
		{
			NativeCombatSurface.Close();
			stopped = true;
			Api.LogFailure("native cost window unavailable; original tracker retained", error);
		}
	}

	internal static bool BeforeGUI(object __instance)
	{
		if (WorldOperations.StrategicActive && NativeCombatSurface.Ready) return false;
        return !attached || stopped || !(bool)ready.GetValue(__instance) || !NativeCombatSurface.Ready;
	}

	private static void SyncWindow(object owner, bool live)
	{
		bool flag = (live ? ((bool)visible.GetValue(visibility.GetValue(owner))) : (menuShown && CampaignCosts.TaskForceMenuAvailable()));
		string text = (live ? "live" : ((!flag) ? campaignScope : CampaignCosts.CurrentSource()));
		if (text != campaignScope)
		{
			campaignScope = text;
			view = null;
			nextLines = 0.0;
		}
		if (flag && (view == null || Now >= nextLines))
		{
			view = ((!live) ? CampaignCosts.CampaignView(CampaignCosts.SavedGames()) : CampaignCosts.LiveView(CampaignCosts.CaptureLive("Current mission")));
			nextLines = Now + ((!live) ? 2.0 : 0.5);
		}
		NativeCombatSurface.Tick(live, flag, view, text, delegate
		{
			if (live)
			{
				visible.SetValue(visibility.GetValue(owner), false);
			}
			else
			{
				menuShown = false;
			}
		}, Now);
	}
}
