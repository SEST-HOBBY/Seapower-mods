using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Security.Cryptography;

namespace Sest.RuntimeFixes {
internal static class F11CombatCosts
{
	private const string TrackerHash = "74afa9028fc0c52b93f415263504f51ecf8d056a624feaebcc8053ba5a1c0ac3";

	private static bool attached;

	private static bool stopped;

	private static bool menuShown;

	private static bool wasLive;

	private static double nextAttach;

	private static double nextCapture;

	private static double nextLines;

	private static FieldInfo ready;

	private static FieldInfo visible;

	private static FieldInfo missionActive;

	private static FieldInfo mission;

	private static FieldInfo toggle;

	private static FieldInfo missionPath;

	private static MethodInfo keyDown;

	private static MethodInfo getKey;

	private static CampaignCosts.CostView view;

	private static string campaignScope;

	private static double Now
	{
		get { return (double)Stopwatch.GetTimestamp() / (double)Stopwatch.Frequency; }
	}

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
		missionPath = Field(Api.Type(native, "SeaPower.Globals"), "currentMissionFilePath", typeof(string));
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

	private static void TrackerLoaded(object sender, AssemblyLoadEventArgs args)
	{
		if (attached || stopped)
		{
			return;
		}
		try
		{
			if (args.LoadedAssembly.GetType("WeaponCostsMod.Overlay", throwOnError: false) == null)
			{
				return;
			}
			nextAttach = 0.0;
			Poll();
		}
		catch (Exception error)
		{
			stopped = true;
			Api.LogFailure("deferred F11 attachment unavailable", error);
		}
	}

	internal static void Poll()
	{
		if (attached || stopped || Now < nextAttach)
		{
			return;
		}
		nextAttach = Now + 1.0;
		foreach (Assembly assembly in AppDomain.CurrentDomain.GetAssemblies())
		{
			if (assembly.GetType("WeaponCostsMod.Overlay", throwOnError: false) == null)
			{
				continue;
			}
			try
			{
				string digest;
				using (FileStream stream = File.OpenRead(assembly.Location))
				{
					using (SHA256 sha = SHA256.Create())
					{
						digest = BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", string.Empty).ToLowerInvariant();
					}
				}
				if (digest != TrackerHash)
				{
					stopped = true;
					Api.Log("F11 campaign totals inactive: uninspected Combat Cost Tracker " + digest);
					return;
				}
				Bind(assembly);
				Type overlay = Api.Type(assembly, "WeaponCostsMod.Overlay");
				Api.Postfix(Api.Method(overlay, "Update", typeof(void)), typeof(F11CombatCosts), "AfterUpdate", "io.github.sest-hobby.cumulative-combat-costs");
				Api.Hooks(Api.Method(overlay, "OnGUI", typeof(void)), typeof(F11CombatCosts), "BeforeGUI", null, "io.github.sest-hobby.cumulative-combat-costs");
				Api.Log("F11 campaign combat costs installed: native movable windows, mission detail and complete scrollable campaign history");
			}
			catch (Exception error)
			{
				stopped = true;
				attached = false;
				Api.LogFailure("F11 campaign totals not installed; original tracker retained", error);
			}
			return;
		}
	}

	internal static void BeforeDestroy()
	{
		NativeCombatSurface.Close();
		if (CombatHistory.CurrentId == null)
		{
			return;
		}
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

	internal static void Bind(Assembly tracker)
	{
		Type type = Api.Type(tracker, "WeaponCostsMod.Overlay");
		ready = Field(type, "ready", typeof(bool));
		visible = Field(type, "visible", typeof(bool));
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
		Type code = Api.FindType("UnityEngine.KeyCode");
		foreach (string name in new[] { "LeftControl", "RightControl", "LeftAlt", "RightAlt", "LeftShift", "RightShift" })
		{
			if ((bool)getKey.Invoke(null, new[] { Enum.Parse(code, name) }))
			{
				return true;
			}
		}
		return false;
	}

	internal static void AfterUpdate(object __instance)
	{
		if (!attached || stopped || !(bool)ready.GetValue(__instance))
		{
			return;
		}
		try
		{
			bool live = (bool)missionActive.GetValue(__instance);
			if (!NativeCombatSurface.EnsureReady(live))
			{
				return;
			}
			if (live != wasLive)
			{
				menuShown = false;
				wasLive = live;
				nextLines = 0.0;
				view = null;
				NativeCombatSurface.Close();
			}
			if (!live && CampaignCosts.TaskForceMenuAvailable() && !Modified() && (bool)keyDown.Invoke(null, new[] { toggle.GetValue(__instance) }))
			{
				menuShown = !menuShown;
				nextLines = 0.0;
			}
			if (Now >= nextCapture)
			{
				nextCapture = Now + 0.5;
				string path = missionPath == null ? null : (string)missionPath.GetValue(null);
				string name = string.IsNullOrWhiteSpace(path) ? "Game" : Path.GetFileNameWithoutExtension(path);
				if (name.Length > 256)
				{
					name = name.Substring(0, 256);
				}
				CombatHistory.Observe(live ? mission.GetValue(__instance) : null, live ? CampaignCosts.CaptureLive(name) : null);
			}
			SyncWindow(__instance, live);
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
		return !attached || stopped || !(bool)ready.GetValue(__instance) || !NativeCombatSurface.Ready;
	}

	private static void SyncWindow(object owner, bool live)
	{
		bool open = live ? (bool)visible.GetValue(owner) : (menuShown && CampaignCosts.TaskForceMenuAvailable());
		string identity = live ? "live" : (open ? CampaignCosts.CurrentSource() : campaignScope);
		if (identity != campaignScope)
		{
			campaignScope = identity;
			view = null;
			nextLines = 0.0;
		}
		if (open && (view == null || Now >= nextLines))
		{
			view = live ? CampaignCosts.LiveView(CampaignCosts.CaptureLive("Current mission")) : CampaignCosts.CampaignView(CampaignCosts.SavedGames());
			nextLines = Now + (live ? 0.5 : 2.0);
		}
		NativeCombatSurface.Tick(live, open, view, identity, delegate
		{
			if (live)
			{
				visible.SetValue(owner, false);
			}
			else
			{
				menuShown = false;
			}
		}, Now);
	}
}

}
