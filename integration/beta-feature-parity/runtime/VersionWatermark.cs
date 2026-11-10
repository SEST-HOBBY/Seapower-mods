using System;
using System.Reflection;

namespace Sest.RuntimeFixes;

// Beta Build 261026 draws "Sea Power v0.8.7-261026" over the game view.
// SeaPower.VersionWatermark.OnStart keeps that text active whenever Steam
// reports a beta branch (SteamApps.GetCurrentBetaName), whatever the player's
// own [Debug] ShowVersionWatermark option says; only the game's config.ini
// can turn it off, and the game does not ship one that does. This hides that
// one object again after every OnStart, and any instance that started before
// the plugin loaded. Nothing else on the HUD is touched.
internal static class VersionWatermark
{
	private static Type watermark;

	private static MethodInfo gameObject;

	private static MethodInfo setActive;

	private static MethodInfo findObjects;

	private static object[] findArguments;

	private static bool reported;

	internal static MethodInfo Bind(Assembly game)
	{
		watermark = Api.Type(game, "SeaPower.VersionWatermark");
		MethodInfo target = Api.Method(watermark, "OnStart", typeof(void));
		Type component = watermark;
		while (component != null && component.FullName != "UnityEngine.Component")
		{
			component = component.BaseType;
		}
		if (component == null)
		{
			throw new MissingMemberException("SeaPower.VersionWatermark is not a UnityEngine.Component");
		}
		PropertyInfo property = component.GetProperty("gameObject", BindingFlags.Instance | BindingFlags.Public);
		if (property == null || property.GetGetMethod() == null)
		{
			throw new MissingMemberException("UnityEngine.Component.gameObject");
		}
		gameObject = property.GetGetMethod();
		setActive = Api.Method(property.PropertyType, "SetActive", typeof(void), typeof(bool));
		Type unityObject = component.BaseType;
		Type sortMode = unityObject.Assembly.GetType("UnityEngine.FindObjectsSortMode", throwOnError: false);
		findObjects = ((sortMode != null) ? unityObject.GetMethod("FindObjectsByType", BindingFlags.Static | BindingFlags.Public, null, new Type[2] { typeof(Type), sortMode }, null) : null);
		if (findObjects != null)
		{
			findArguments = new object[2] { watermark, Enum.ToObject(sortMode, 0) };
		}
		else
		{
			findObjects = unityObject.GetMethod("FindObjectsOfType", BindingFlags.Static | BindingFlags.Public, null, new Type[1] { typeof(Type) }, null);
			findArguments = new object[1] { watermark };
		}
		if (findObjects == null)
		{
			throw new MissingMethodException("UnityEngine.Object", "FindObjectsByType");
		}
		return target;
	}

	internal static void Install(Assembly game)
	{
		MethodInfo target = Bind(game);
		Api.Postfix(target, typeof(VersionWatermark), "AfterStart", "io.github.sest-hobby.version-watermark");
		int hidden = 0;
		foreach (object instance in (Array)findObjects.Invoke(null, findArguments))
		{
			if (instance != null && Hide(instance))
			{
				hidden++;
			}
		}
		Api.Log("version watermark hidden: the beta's own build text over the game view (" + hidden + " already present); HideVersionWatermark=0 in plugins/sest_runtime.ini keeps it");
	}

	public static void AfterStart(object __instance)
	{
		try
		{
			Hide(__instance);
		}
		catch (Exception error)
		{
			if (!reported)
			{
				reported = true;
				Api.LogFailure("version watermark stays visible", error);
			}
		}
	}

	private static bool Hide(object instance)
	{
		object target = gameObject.Invoke(instance, null);
		if (target == null)
		{
			return false;
		}
		setActive.Invoke(target, new object[1] { false });
		return true;
	}
}
