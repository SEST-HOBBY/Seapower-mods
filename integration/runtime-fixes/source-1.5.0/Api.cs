using System;
using System.Reflection;

namespace Sest.RuntimeFixes {
internal static class Api
{
	internal const BindingFlags All = BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static;

	internal static Type FindType(string name)
	{
		Assembly[] assemblies = AppDomain.CurrentDomain.GetAssemblies();
		foreach (Assembly assembly in assemblies)
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
		Type type = FindType("HarmonyLib.Harmony");
		Type type2 = FindType("HarmonyLib.HarmonyMethod");
		MethodInfo methodInfo = null;
		MethodInfo[] methods = type.GetMethods(BindingFlags.Instance | BindingFlags.Public);
		foreach (MethodInfo methodInfo2 in methods)
		{
			if (methodInfo2.Name != "Patch")
			{
				continue;
			}
			ParameterInfo[] parameters = methodInfo2.GetParameters();
			if (parameters.Length < 2 || parameters[0].ParameterType != typeof(MethodBase))
			{
				continue;
			}
			ParameterInfo[] array = parameters;
			foreach (ParameterInfo parameterInfo in array)
			{
				if (parameterInfo.Name == "postfix" && parameterInfo.ParameterType == type2)
				{
					methodInfo = methodInfo2;
					break;
				}
			}
			if (methodInfo != null)
			{
				break;
			}
		}
		ConstructorInfo constructor = type2.GetConstructor(new Type[1] { typeof(MethodInfo) });
		if (methodInfo == null || constructor == null)
		{
			throw new MissingMethodException("Harmony.Patch(..., postfix)");
		}
		object obj = ((before != null) ? constructor.Invoke(new object[1] { owner.GetMethod(before, BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static) }) : null);
		object obj2 = ((after != null) ? constructor.Invoke(new object[1] { owner.GetMethod(after, BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static) }) : null);
		object obj3 = ((finalizer != null) ? constructor.Invoke(new object[1] { owner.GetMethod(finalizer, BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static) }) : null);
		object obj4 = ((transpiler != null) ? constructor.Invoke(new object[1] { owner.GetMethod(transpiler, BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static) }) : null);
		ParameterInfo[] parameters2 = methodInfo.GetParameters();
		object[] array2 = new object[parameters2.Length];
		array2[0] = target;
		for (int k = 1; k < array2.Length; k++)
		{
			if (parameters2[k].Name == "postfix")
			{
				array2[k] = obj2;
			}
			if (parameters2[k].Name == "prefix")
			{
				array2[k] = obj;
			}
			if (parameters2[k].Name == "finalizer")
			{
				array2[k] = obj3;
			}
			if (parameters2[k].Name == "transpiler")
			{
				array2[k] = obj4;
			}
		}
		if (obj3 != null && !Array.Exists(parameters2, (ParameterInfo p) => p.Name == "finalizer"))
		{
			throw new MissingMethodException("Harmony.Patch(..., finalizer)");
		}
		if (obj4 != null && !Array.Exists(parameters2, (ParameterInfo p) => p.Name == "transpiler"))
		{
			throw new MissingMethodException("Harmony.Patch(..., transpiler)");
		}
		methodInfo.Invoke(Activator.CreateInstance(type, harmonyId), array2);
	}
}

}
