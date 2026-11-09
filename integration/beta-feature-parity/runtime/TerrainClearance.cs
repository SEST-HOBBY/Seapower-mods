using System;
using System.Linq.Expressions;
using System.Reflection;
using System.Runtime.CompilerServices;

namespace Sest.RuntimeFixes;

internal static class TerrainClearance
{
	private sealed class Match
	{
		internal bool Mst;
	}

	private static Type missile;

	private static Func<object, object> ammunition;

	private static Func<object, object> geo;

	private static Func<object, object> transform;

	private static Func<object, string> roundName;

	private static Func<object, string> stage;

	private static Func<object, bool> terrainFollowing;

	private static Func<object, float> heading;

	private static Func<object, float, float, float> highest;

	private static float clearance;

	private static bool active;

	private static bool reported;

	private static readonly ConditionalWeakTable<object, Match> rounds = new ConditionalWeakTable<object, Match>();

	internal static MethodInfo Bind(Assembly game)
	{
		Type type = Api.Type(game, "SeaPower.ObjectBase");
		Type type2 = Api.Type(game, "SeaPower.WeaponBase");
		Type type3 = Api.Type(game, "SeaPower.AmmunitionParameters");
		Type type4 = Api.Type(game, "SeaPower.TerrainUtils");
		missile = Api.Type(game, "SeaPower.Missile");
		ammunition = Getter<object>(type2, "_ap");
		roundName = Getter<string>(type3, "_ammunitionFileName");
		terrainFollowing = Getter<bool>(type3, "_terrainFollowFlight");
		geo = Getter<object>(type, "_geoPosition");
		transform = Getter<object>(type, "transform");
		PropertyInfo property = type2.GetProperty("_flightStage", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		if (property == null || !property.PropertyType.IsEnum)
		{
			throw new MissingMemberException("_flightStage enum");
		}
		Type stageType = property.PropertyType;
		string[] array = new string[10] { "ToBearing", "MaintainHeight", "MoveToLoftAlt", "MaintainLoftAlt", "MoveToSeaSkimming", "MaintainSeaSkimming", "MoveToFinalFlightAlt", "MaintainFinalFlightAlt", "AlignSensorToTarget", "TerminalApproach" };
		foreach (string text in array)
		{
			if (!Enum.IsDefined(stageType, text))
			{
				throw new MissingMemberException(stageType.Name, text);
			}
		}
		Func<object, object> stageValue = Getter<object>(type2, "_flightStage");
		stage = (object value) => Enum.GetName(stageType, stageValue(value));
		Type propertyType = type.GetProperty("transform", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static).PropertyType;
		ParameterExpression parameterExpression = Expression.Parameter(typeof(object), "transform");
		MemberExpression expression = Expression.Property(Expression.Convert(parameterExpression, propertyType), "eulerAngles");
		heading = Expression.Lambda<Func<object, float>>(Expression.Field(expression, "y"), new ParameterExpression[1] { parameterExpression }).Compile();
		Type propertyType2 = type.GetProperty("_geoPosition", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static).PropertyType;
		MethodInfo method = Api.Method(type4, "CrudeGetHighestTerrainHeightAhead", typeof(float), propertyType2, typeof(float), typeof(float), typeof(bool));
		ParameterExpression parameterExpression2 = Expression.Parameter(typeof(object), "geo");
		ParameterExpression parameterExpression3 = Expression.Parameter(typeof(float), "heading");
		ParameterExpression parameterExpression4 = Expression.Parameter(typeof(float), "distance");
		highest = Expression.Lambda<Func<object, float, float, float>>(Expression.Call(method, Expression.Convert(parameterExpression2, propertyType2), parameterExpression3, parameterExpression4, Expression.Constant(false)), new ParameterExpression[3] { parameterExpression2, parameterExpression3, parameterExpression4 }).Compile();
		clearance = (float)Api.Method(Api.Type(game, "SeaPower.Utils"), "heightInFeetToUnity", typeof(float), typeof(float)).Invoke(null, new object[1] { 500f });
		if (!Policy.Finite(clearance) || clearance <= 0f)
		{
			throw new InvalidOperationException("invalid altitude conversion");
		}
		active = true;
		return Api.Method(type4, "GetSafeAltitudeOverSurface", typeof(float), type, typeof(float), typeof(float), typeof(bool), typeof(bool));
	}

	private static Func<object, T> Getter<T>(Type type, string name)
	{
		ParameterExpression parameterExpression = Expression.Parameter(typeof(object), "instance");
		MemberExpression expression = Expression.PropertyOrField(Expression.Convert(parameterExpression, type), name);
		return Expression.Lambda<Func<object, T>>(Expression.Convert(expression, typeof(T)), new ParameterExpression[1] { parameterExpression }).Compile();
	}

	internal static void Install(Assembly game)
	{
		MethodInfo target = Bind(game);
		Api.Postfix(target, typeof(TerrainClearance), "Postfix", "io.github.sest-hobby.mst-terrain");
		Api.Log("MST terrain correction installed: RGM/UGM-109E5a cruise only, 500 ft over land ahead; native terminal profile retained");
	}

	internal static void Postfix(object __0, bool __4, ref float __result)
	{
		if (!active || !__4 || __0 == null || !missile.IsInstanceOfType(__0))
		{
			return;
		}
		try
		{
			object obj = ammunition(__0);
			if (obj != null && terrainFollowing(obj) && rounds.GetValue(obj, (object key) => new Match
			{
				Mst = Policy.IsMst(roundName(key))
			}).Mst && Policy.CruiseStage(stage(__0)))
			{
				float highestLand = highest(geo(__0), heading(transform(__0)), 1.1f);
				float num = Policy.Altitude(__result, highestLand, clearance);
				if (num > __result && !reported)
				{
					reported = true;
					Api.Log("MST land clearance applied; terrain remains collidable and missile uses native pitch/turn limits");
				}
				__result = num;
			}
		}
		catch (Exception error)
		{
			active = false;
			Api.LogFailure("terrain correction disabled for this session; native result retained", error);
		}
	}
}
