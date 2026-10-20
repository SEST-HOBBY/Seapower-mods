// SEST's own runtime corrections. No game or third-party binary is embedded.
// Reflection keeps the build independent of proprietary assemblies. Installation
// is restricted to the inspected native build; missing APIs fail closed.
using System;
using System.IO;
using System.Reflection;
using System.Security.Cryptography;
using AnchorChain;

namespace Sest.RuntimeFixes
{
    [ACPlugin("io.github.sest-hobby.runtime-fixes", "SEST Runtime Fixes", "1.0.0")]
    public sealed class RuntimeFixesMod : IAnchorChainMod
    {
        public void TriggerEntryPoint()
        {
            try
            {
                Assembly game = Api.FindType("SeaPower.ObjectBase").Assembly;
                // Sea Power 0.8.6, supplied by the player's 20 October capture.
                const string inspected = "c913e31f2d73e526f2d28043f522f2be26f12534fd0421eedee3cd70eab9cdd8";
                string digest;
                using (var stream = File.OpenRead(game.Location))
                using (var sha = SHA256.Create())
                    digest = BitConverter.ToString(sha.ComputeHash(stream)).Replace("-", "").ToLowerInvariant();
                if (digest != inspected)
                {
                    Api.Log("inactive: uninspected native assembly " + digest);
                    return;
                }
                string root = Directory.GetParent(typeof(RuntimeFixesMod).Assembly.Location).Parent.FullName;
                string settings = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
                    "AppData", "LocalLow", "Triassic Games", "Sea Power", "usersettings.ini");
                if (!Policy.PackEnabled(File.ReadAllLines(settings), new DirectoryInfo(root).Name))
                {
                    Api.Log("inactive: owning pack is not enabled in usersettings.ini; restart after enabling it");
                    return;
                }
                string[] config = File.ReadAllLines(Path.Combine(root, "plugins", "sest_runtime.ini"));
                if (Policy.OptionEnabled(config, "TerrainClearance"))
                {
                    try { TerrainClearance.Install(game); }
                    catch (Exception e) { Api.LogFailure("terrain correction not installed", e); }
                }
                if (Policy.OptionEnabled(config, "TaskForceDebrief"))
                {
                    try { TaskForceDebrief.Install(game); }
                    catch (Exception e) { Api.LogFailure("debrief correction not installed", e); }
                }
            }
            catch (Exception e) { Api.LogFailure("inactive", e); }
        }
    }

    internal static class Api
    {
        internal const BindingFlags All = BindingFlags.Public | BindingFlags.NonPublic |
            BindingFlags.Instance | BindingFlags.Static;

        internal static Type FindType(string name)
        {
            foreach (Assembly assembly in AppDomain.CurrentDomain.GetAssemblies())
            {
                Type result = assembly.GetType(name, false);
                if (result != null) return result;
            }
            throw new MissingMemberException(name);
        }

        internal static Type Type(Assembly assembly, string name)
        {
            Type result = assembly.GetType(name, false);
            if (result == null) throw new MissingMemberException(name);
            return result;
        }

        internal static MethodInfo Method(Type type, string name, Type returns, params Type[] parameters)
        {
            MethodInfo method = type.GetMethod(name, All, null, parameters, null);
            if (method == null || method.ReturnType != returns) throw new MissingMethodException(type.FullName, name);
            return method;
        }

        internal static void Log(string message)
        {
            message = "[SEST Runtime] " + message;
            try { Method(FindType("UnityEngine.Debug"), "Log", typeof(void), typeof(object)).Invoke(null, new object[] { message }); }
            catch { Console.WriteLine(message); }
        }

        internal static void LogFailure(string label, Exception error)
        {
            while (error is TargetInvocationException && error.InnerException != null) error = error.InnerException;
            Log(label + ": " + error.GetType().Name + ": " + error.Message);
        }

        internal static void Postfix(MethodInfo target, Type owner, string callback, string harmonyId)
        {
            Type harmony = FindType("HarmonyLib.Harmony"), hm = FindType("HarmonyLib.HarmonyMethod");
            MethodInfo patch = null;
            foreach (MethodInfo candidate in harmony.GetMethods(BindingFlags.Instance | BindingFlags.Public))
            {
                if (candidate.Name != "Patch") continue;
                ParameterInfo[] ps = candidate.GetParameters();
                if (ps.Length < 2 || ps[0].ParameterType != typeof(MethodBase)) continue;
                foreach (ParameterInfo p in ps)
                    if (p.Name == "postfix" && p.ParameterType == hm) { patch = candidate; break; }
                if (patch != null) break;
            }
            ConstructorInfo constructor = hm.GetConstructor(new[] { typeof(MethodInfo) });
            if (patch == null || constructor == null) throw new MissingMethodException("Harmony.Patch(..., postfix)");
            object postfix = constructor.Invoke(new object[] { owner.GetMethod(callback, All) });
            ParameterInfo[] parameters = patch.GetParameters();
            object[] args = new object[parameters.Length];
            args[0] = target;
            for (int i = 1; i < args.Length; i++) if (parameters[i].Name == "postfix") args[i] = postfix;
            patch.Invoke(Activator.CreateInstance(harmony, harmonyId), args);
        }
    }
}
