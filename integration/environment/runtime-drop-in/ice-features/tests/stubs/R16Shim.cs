using System;
using System.Collections.Generic;
using System.Reflection;

// TEST ONLY. Minimal stand-ins for r16's runtime/Api.cs and runtime/Policy.cs (feature/mno-r16),
// with the same names and signatures the drop-in calls. r16's own files use C# 10 file-scoped
// namespaces, which mcs cannot parse, so they are not compiled here. Api.Postfix records the patch
// instead of calling Harmony; IceFeaturesTests checks the target and calls the callback itself.
// Policy.TextOption is a copy of r16's logic (the [Runtime] section, case-insensitive keys).
namespace Sest.RuntimeFixes
{
    internal static class Api
    {
        internal const BindingFlags All = BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static;
        internal static readonly List<string> Lines = new List<string>();
        internal sealed class Patch { internal MethodInfo Target; internal Type Owner; internal string Callback, Id; }
        internal static readonly List<Patch> Patches = new List<Patch>();

        internal static Type FindType(string name)
        {
            foreach (var assembly in AppDomain.CurrentDomain.GetAssemblies())
            {
                var type = assembly.GetType(name, false);
                if (type != null) return type;
            }
            throw new MissingMemberException(name);
        }

        internal static MethodInfo Method(Type type, string name, Type returns, params Type[] parameters)
        {
            var method = type.GetMethod(name, All, null, parameters, null);
            if (method == null || method.ReturnType != returns) throw new MissingMethodException(type.FullName, name);
            return method;
        }

        internal static void Log(string message) { Lines.Add("[SEST Runtime] " + message); }

        internal static void LogFailure(string label, Exception error)
        {
            while (error is TargetInvocationException && error.InnerException != null) error = error.InnerException;
            Log(label + ": " + error.GetType().Name + ": " + error.Message);
        }

        internal static void Postfix(MethodInfo target, Type owner, string callback, string harmonyId)
        {
            if (owner.GetMethod(callback, All) == null) throw new MissingMethodException(owner.FullName, callback);
            Patches.Add(new Patch { Target = target, Owner = owner, Callback = callback, Id = harmonyId });
        }
    }

    internal static class Policy
    {
        internal static string TextOption(string[] lines, string option, string fallback)
        {
            string a = string.Empty;
            foreach (string text in lines)
            {
                string t = text.Trim();
                if (t.StartsWith("[")) { a = t; continue; }
                int num = t.IndexOf('=');
                if (string.Equals(a, "[Runtime]", StringComparison.OrdinalIgnoreCase) && num >= 0 && string.Equals(t.Substring(0, num).Trim(), option, StringComparison.OrdinalIgnoreCase))
                    return t.Substring(num + 1).Trim();
            }
            return fallback;
        }
    }
}
