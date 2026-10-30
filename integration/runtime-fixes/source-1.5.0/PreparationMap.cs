using System;
using System.Collections;
using System.Diagnostics;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;

namespace Sest.RuntimeFixes {
internal static class PreparationMap
{
	private sealed class Entry
	{
		internal bool Ready;

		internal object Record;

		internal double RetryAt;

		internal bool Reported;
	}

	private static FieldInfo initialized;

	private static FieldInfo closing;

	private static FieldInfo player;

	private static FieldInfo pending;

	private static PropertyInfo objects;

	private static MethodInfo paused;

	private static MethodInfo elapsed;

	private static MethodInfo owner;

	private static MethodInfo isUnit;

	private static MethodInfo disabled;

	private static MethodInfo destroyed;

	private static MethodInfo plotting;

	private static MethodInfo ownState;

	private static MethodInfo mapVehicle;

	private static MethodInfo baseObject;

	private static MethodInfo reactive;

	private static MethodInfo hasState;

	private static MethodInfo estimate;

	private static object session;

	private static object side;

	private static MethodInfo managerExists;

	private static MethodInfo managerInstance;

	private static ConditionalWeakTable<object, Entry> entries = new ConditionalWeakTable<object, Entry>();

	private static bool announced;

	internal static MethodInfo Bind(Assembly game)
	{
		Type type = Api.Type(game, "SeaPower.GameMain");
		Type type2 = Api.Type(game, "SeaPower.ObjectBase");
		Type type3 = Api.Type(game, "SeaPower.Taskforce");
		Type type4 = Api.Type(game, "SeaPower.Vehicle");
		Type type5 = Api.Type(game, "SeaPower.GameTime");
		initialized = type.GetField("_initialized", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		closing = type.GetField("_closing", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		player = Api.Type(game, "SeaPower.Globals").GetField("_playerTaskforce", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		objects = type3.GetProperty("TaskforceObjects", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		if (initialized == null || initialized.FieldType != typeof(bool) || closing == null || closing.FieldType != typeof(bool) || player == null || player.FieldType != type3 || objects == null || !typeof(IEnumerable).IsAssignableFrom(objects.PropertyType))
		{
			throw new MissingMemberException("preparation map context API");
		}
		paused = Api.Method(type5, "IsPaused", typeof(bool));
		elapsed = Api.Method(type5, "get_missionElapsedTime", typeof(double));
		owner = Api.Method(type2, "get__taskforce", type3);
		isUnit = Api.Method(type2, "isUnit", typeof(bool));
		disabled = Api.Method(type2, "get_Disabled", typeof(bool));
		destroyed = Api.Method(type2, "get_IsDestroyed", typeof(bool));
		plotting = Api.Method(type2, "get_PlottingTable", Api.Type(game, "SeaPower.PlottingTable"));
		ownState = Api.Method(type2, "UpdateOwnPlottingState", typeof(void));
		mapVehicle = Api.Method(type2, "GetMapVehicle", type4, type3);
		baseObject = Api.Method(type4, "get_BaseObject", type2);
		reactive = Api.Method(type4, "UpdateReactive", typeof(void));
		hasState = Api.Method(type4, "get_HasReactiveState", typeof(bool));
		PropertyInfo property = type4.GetProperty("PositionEstimate", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		if (property == null || !property.PropertyType.IsGenericType || property.PropertyType.GetGenericTypeDefinition() != typeof(Nullable<>))
		{
			throw new MissingMemberException("own-unit position estimate API");
		}
		estimate = Api.Method(type4, "get_PositionEstimate", property.PropertyType);
		Type type6 = Api.Type(game, "SeaPower.MissionManager");
		Type type7 = Api.Type(game, "SeaPower.Singleton`1").MakeGenericType(type6);
		pending = type6.GetField("UnitsToCompleteLaunchPreparations", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		if (pending == null || !typeof(ICollection).IsAssignableFrom(pending.FieldType))
		{
			throw new MissingMemberException("native preparation queue");
		}
		managerExists = Api.Method(type7, "InstanceExists", typeof(bool), typeof(bool));
		managerInstance = Api.Method(type7, "get_Instance", type6);
		Reset();
		return Api.Method(type, "Update", typeof(void));
	}

	internal static void Install(Assembly game)
	{
		Api.Postfix(Bind(game), typeof(PreparationMap), "AfterUpdate", "io.github.sest-hobby.preparation-map");
		Api.Postfix(Api.Method(Api.Type(game, "SeaPower.GameMain"), "OnDestroy", typeof(void)), typeof(PreparationMap), "Reset", "io.github.sest-hobby.preparation-map");
		Api.Postfix(Api.Method(Api.Type(game, "SeaPower.MissionManager"), "ResetData", typeof(void)), typeof(PreparationMap), "Reset", "io.github.sest-hobby.preparation-map");
		Api.Log("preparation map refresh installed: own units only, native preparation queue, restart cleanup, no simulation step");
	}

	internal static void Reset()
	{
		session = (side = null);
		announced = false;
		entries = new ConditionalWeakTable<object, Entry>();
	}

	private static bool Preparing()
	{
		if ((double)elapsed.Invoke(null, null) == 0.0)
		{
			return true;
		}
		if (!(bool)managerExists.Invoke(null, new object[1] { false }))
		{
			return false;
		}
		return pending.GetValue(managerInstance.Invoke(null, null)) is ICollection collection && collection.Count > 0;
	}

	internal static void AfterUpdate(object __instance)
	{
		Refresh(__instance, (double)Stopwatch.GetTimestamp() / (double)Stopwatch.Frequency);
	}

	internal static void Refresh(object game, double now)
	{
		try
		{
			if (game == null || !(bool)initialized.GetValue(game) || (bool)closing.GetValue(game) || !(bool)paused.Invoke(null, null) || !Preparing())
			{
				return;
			}
			object value = player.GetValue(null);
			if (value == null)
			{
				return;
			}
			if (!object.ReferenceEquals(session, game) || !object.ReferenceEquals(side, value))
			{
				session = game;
				side = value;
				entries = new ConditionalWeakTable<object, Entry>();
				announced = false;
			}
			if (!(objects.GetValue(value, null) is IEnumerable source))
			{
				return;
			}
			int num = 0;
			object[] array = source.Cast<object>().ToArray();
			foreach (object obj in array)
			{
				if (obj == null)
				{
					continue;
				}
				if (!entries.TryGetValue(obj, out var value2))
				{
					value2 = new Entry();
					entries.Add(obj, value2);
				}
				if (now < value2.RetryAt)
				{
					continue;
				}
				value2.RetryAt = now + 0.5;
				try
				{
					if (!object.ReferenceEquals(owner.Invoke(obj, null), value) || !(bool)isUnit.Invoke(obj, null) || (bool)disabled.Invoke(obj, null) || (bool)destroyed.Invoke(obj, null) || plotting.Invoke(obj, null) == null)
					{
						continue;
					}
					object obj2 = mapVehicle.Invoke(obj, new object[1] { value });
					if (value2.Ready && object.ReferenceEquals(obj2, value2.Record) && obj2 != null && (bool)hasState.Invoke(obj2, null) && estimate.Invoke(obj2, null) != null)
					{
						continue;
					}
					if (obj2 == null || !(bool)hasState.Invoke(obj2, null) || estimate.Invoke(obj2, null) == null)
					{
						ownState.Invoke(obj, null);
						obj2 = mapVehicle.Invoke(obj, new object[1] { value });
					}
					if (obj2 != null && object.ReferenceEquals(baseObject.Invoke(obj2, null), obj))
					{
						reactive.Invoke(obj2, null);
						if ((bool)hasState.Invoke(obj2, null) && estimate.Invoke(obj2, null) != null)
						{
							value2.Ready = true;
							value2.Record = obj2;
							num++;
						}
					}
				}
				catch (Exception error)
				{
					if (!value2.Reported)
					{
						value2.Reported = true;
						Api.LogFailure("one own-unit preparation marker not ready; native startup retained and refresh will retry", error);
					}
				}
			}
			if (num > 0 && !announced)
			{
				announced = true;
				Api.Log("preparation map initialized " + num + " own-unit plotting record(s) while paused; mission clock unchanged");
			}
		}
		catch (Exception error2)
		{
			Api.LogFailure("preparation map refresh unavailable; native map retained", error2);
		}
	}
}

}
