using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using System.Runtime.CompilerServices;
using HarmonyLib;

namespace Sest.RuntimeFixes;

internal static class TowedSensorGuard
{
	private static FieldInfo sensor;

	private static FieldInfo sonar;

	private static FieldInfo owner;

	private static FieldInfo parameters;

	private static FieldInfo reference;

	private static MethodInfo active;

	private static PropertyInfo value;

	private static Type sonarType;

	private static ConditionalWeakTable<object, object> warned = new ConditionalWeakTable<object, object>();

	internal static void Bind(Assembly game)
	{
		Type type = Api.Type(game, "SeaPower.TowedSystem");
		sonarType = Api.Type(game, "SeaPower.SensorSystemSonar");
		sensor = type.GetField("_towedSensor", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		sonar = sonarType.GetField("_sonar", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		if (sensor == null || sonar == null)
		{
			throw new MissingMemberException("native towed sonar fields");
		}
		active = sonar.FieldType.GetMethod("get_IsActive", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		value = ((!(active == null)) ? active.ReturnType.GetProperty("Value", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static) : null);
		if (value == null || value.PropertyType != typeof(bool) || !value.CanWrite)
		{
			throw new MissingMemberException("native sonar active flag");
		}
		owner = Api.Type(game, "SeaPower.BaseSystem").GetField("_baseObject", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		parameters = Api.Type(game, "SeaPower.ObjectBase").GetField("_obp", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		reference = Api.Type(game, "SeaPower.ObjectBaseParameters").GetField("_objectIniName", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static);
		warned = new ConditionalWeakTable<object, object>();
	}

	internal static void Install(Assembly game)
	{
		Bind(game);
		Api.Hooks(Api.Method(Api.Type(game, "SeaPower.TowedSystem"), "OnFixedUpdate", typeof(void)), typeof(TowedSensorGuard), "BeforeUpdate", null, "io.github.sest-hobby.towed-sensor-guard", null, "Transpile");
		Api.Log("towed sensor correction installed: guarded native active-sonar retraction, mechanical behavior retained");
	}

	internal static bool BeforeUpdate(object __instance)
	{
		object obj = sensor.GetValue(__instance);
		if (obj != null && sonarType.IsInstanceOfType(obj) && sonar.GetValue(obj) == null)
		{
			Warn(__instance, "sonar link missing; only this incomplete towed system waits for its native sensor");
			return false;
		}
		return true;
	}

	private static void Warn(object system, string reason)
	{
		if (warned.TryGetValue(system, out var _))
		{
			return;
		}
		warned.Add(system, new object());
		string text = "unknown unit";
		try
		{
			object obj2 = owner.GetValue(system);
			object obj3 = ((obj2 != null) ? parameters.GetValue(obj2) : null);
			if (obj3 != null)
			{
				text = ((string)reference.GetValue(obj3)) ?? text;
			}
		}
		catch
		{
		}
		Api.Log("towed sensor " + text + ": " + reason);
	}

	internal static void ClearActiveSonar(object system)
	{
		object obj = sensor.GetValue(system);
		if (obj == null || !sonarType.IsInstanceOfType(obj))
		{
			Warn(system, "non-sonar sensor has no sonar active flag; native retraction continues");
			return;
		}
		object obj2 = sonar.GetValue(obj);
		if (obj2 == null)
		{
			Warn(system, "sonar link not ready during retraction");
			return;
		}
		object obj3 = active.Invoke(obj2, null);
		if (obj3 != null)
		{
			value.SetValue(obj3, false, null);
		}
	}

	internal static IEnumerable<CodeInstruction> Transpile(IEnumerable<CodeInstruction> input)
	{
		List<CodeInstruction> list = input.ToList();
		int num = -1;
		for (int i = 0; i + 6 < list.Count; i++)
		{
			if (!(list[i].opcode != OpCodes.Ldarg_0) && !(list[i + 1].opcode != OpCodes.Ldfld) && object.Equals(list[i + 1].operand, sensor) && !(list[i + 2].opcode != OpCodes.Isinst) && object.Equals(list[i + 2].operand, sonarType) && !(list[i + 3].opcode != OpCodes.Ldfld) && object.Equals(list[i + 3].operand, sonar) && !(list[i + 4].opcode != OpCodes.Callvirt) && object.Equals(list[i + 4].operand, active) && !(list[i + 5].opcode != OpCodes.Ldc_I4_0) && !(list[i + 6].opcode != OpCodes.Callvirt) && object.Equals(list[i + 6].operand, value.GetSetMethod(nonPublic: true)))
			{
				if (num != -1 || list.Skip(i + 1).Take(6).Any((CodeInstruction c) => c.labels.Count != 0))
				{
					throw new InvalidOperationException("towed correction pattern is ambiguous");
				}
				num = i;
			}
		}
		if (num < 0)
		{
			throw new InvalidOperationException("inspected towed retraction sequence missing");
		}
		CodeInstruction codeInstruction = new CodeInstruction(list[num]);
		list.RemoveRange(num, 7);
		list.InsertRange(num, new CodeInstruction[2]
		{
			codeInstruction,
			new CodeInstruction(OpCodes.Call, typeof(TowedSensorGuard).GetMethod("ClearActiveSonar", BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static))
		});
		return list;
	}
}
