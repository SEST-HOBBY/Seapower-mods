using System;
using System.Reflection;

namespace Sest.RuntimeFixes {
internal static class Api
{
	internal const BindingFlags All = BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static;

	internal static Type FindType(string name)
	{
		foreach (Assembly assembly in AppDomain.CurrentDomain.GetAssemblies())
		{
			Type type = assembly.GetType(name, throwOnError: false);
			if (type != null)
			{
				return type;
			}
		}
		throw new MissingMemberException(name);
	}

	internal static Type Type(Assembly assembly, string name)
	{
		Type type = assembly.GetType(name, throwOnError: false);
		if (type == null)
		{
			throw new MissingMemberException(name);
		}
		return type;
	}

	internal static MethodInfo Method(Type type, string name, Type returns, params Type[] parameters)
	{
		MethodInfo method = type.GetMethod(name, BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static, null, parameters, null);
		if (method == null || method.ReturnType != returns)
		{
			throw new MissingMethodException(type.FullName, name);
		}
		return method;
	}

	internal static void Log(string message)
	{
		message = "[SEST Runtime] " + message;
		try
		{
			Method(FindType("UnityEngine.Debug"), "Log", typeof(void), typeof(object)).Invoke(null, new object[1] { message });
		}
		catch
		{
			Console.WriteLine(message);
		}
	}

	internal static void LogFailure(string label, Exception error)
	{
		while (error is TargetInvocationException && error.InnerException != null)
		{
			error = error.InnerException;
		}
		Log(label + ": " + error.GetType().Name + ": " + error.Message);
	}

	internal static void Postfix(MethodInfo target, Type owner, string callback, string harmonyId)
	{
		Hooks(target, owner, null, callback, harmonyId);
	}

	internal static void Hooks(MethodInfo target, Type owner, string before, string after, string harmonyId, string finalizer = null, string transpiler = null)
	{
		Type harmony = FindType("HarmonyLib.Harmony");
		Type hm = FindType("HarmonyLib.HarmonyMethod");
		MethodInfo patch = null;
		foreach (MethodInfo candidate in harmony.GetMethods(BindingFlags.Instance | BindingFlags.Public))
		{
			if (candidate.Name != "Patch")
			{
				continue;
			}
			ParameterInfo[] ps = candidate.GetParameters();
			if (ps.Length < 2 || ps[0].ParameterType != typeof(MethodBase))
			{
				continue;
			}
			foreach (ParameterInfo p in ps)
			{
				if (p.Name == "postfix" && p.ParameterType == hm)
				{
					patch = candidate;
					break;
				}
			}
			if (patch != null)
			{
				break;
			}
		}
		ConstructorInfo constructor = hm.GetConstructor(new[] { typeof(MethodInfo) });
		if (patch == null || constructor == null)
		{
			throw new MissingMethodException("Harmony.Patch(..., postfix)");
		}
		object prefix = before == null ? null : constructor.Invoke(new object[] { owner.GetMethod(before, All) });
		object postfix = after == null ? null : constructor.Invoke(new object[] { owner.GetMethod(after, All) });
		object finish = finalizer == null ? null : constructor.Invoke(new object[] { owner.GetMethod(finalizer, All) });
		object transpile = transpiler == null ? null : constructor.Invoke(new object[] { owner.GetMethod(transpiler, All) });
		ParameterInfo[] parameters = patch.GetParameters();
		object[] args = new object[parameters.Length];
		args[0] = target;
		for (int i = 1; i < args.Length; i++)
		{
			if (parameters[i].Name == "postfix") args[i] = postfix;
			if (parameters[i].Name == "prefix") args[i] = prefix;
			if (parameters[i].Name == "finalizer") args[i] = finish;
			if (parameters[i].Name == "transpiler") args[i] = transpile;
		}
		if (finish != null && !Array.Exists(parameters, p => p.Name == "finalizer")) throw new MissingMethodException("Harmony.Patch(..., finalizer)");
		if (transpile != null && !Array.Exists(parameters, p => p.Name == "transpiler")) throw new MissingMethodException("Harmony.Patch(..., transpiler)");
		patch.Invoke(Activator.CreateInstance(harmony, harmonyId), args);
	}
}

}
