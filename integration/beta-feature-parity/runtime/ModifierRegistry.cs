using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Reflection;

namespace Sest.RuntimeFixes;

// Beta Build 261026 builds FileManager.Directories lazily. When a BepInEx
// plugin reads it before SteamManager has initialised (Anchor Chain's
// preloader and SEST's beta bootstrap both do, to find the chainloader), the
// list holds only the game's own folders. FileManager.OnStart later rebuilds
// it, but each SearchDirectory it constructs opens its mod's _info.ini through
// IniHandler.open, whose one-shot IniHandler.ScanForModifierFiles then runs
// against the stale three-folder list, because the rebuilt list is published
// only after every directory is constructed. The scan never runs again, so
// every #!extend, #!prepend and #!copy file of every Workshop mod is ignored
// for the whole session: SEST's cost catalogs, its Cross-Deck stubs and its
// Collection and Allied Fixes extends among them. The 2 Nov 2026 capture shows
// the result: neither cost reader found [sest_agr-30], which SEST's
// sest_weapon_costs.ini extends into weaponcosts.ini.
//
// The game's own Mod Manager "apply" calls IniHandler.invalidateCache and
// IniHandler.invalidateModifierRegistry before reloading the menu. This does
// the same once the Workshop folders are registered, which is when this
// plugin runs, and only when the registry really lacks the pack's own
// modifier files. Everything is read through the game's methods; no file is
// written and no scene is reloaded.
internal static class ModifierRegistry
{
	private static FieldInfo scanComplete;

	private static FieldInfo extendRegistry;

	private static FieldInfo prependRegistry;

	private static MethodInfo invalidateCache;

	private static MethodInfo invalidateRegistry;

	private static MethodInfo scan;

	private static PropertyInfo fileManager;

	private static PropertyInfo directories;

	internal static void Bind(Assembly game)
	{
		Type ini = Api.Type(game, "SeaPower.IniHandler");
		scanComplete = Field(ini, "_modifierScanComplete", typeof(bool));
		extendRegistry = Field(ini, "_extendRegistry", typeof(Dictionary<string, List<string>>));
		prependRegistry = Field(ini, "_prependRegistry", typeof(Dictionary<string, List<string>>));
		invalidateCache = Api.Method(ini, "invalidateCache", typeof(void));
		invalidateRegistry = Api.Method(ini, "invalidateModifierRegistry", typeof(void));
		scan = Api.Method(ini, "ScanForModifierFiles", typeof(void));
		if (!invalidateCache.IsStatic || !invalidateRegistry.IsStatic || !scan.IsStatic)
		{
			throw new MissingMethodException("SeaPower.IniHandler", "static invalidation");
		}
		Type manager = Api.Type(game, "SeaPower.FileManager");
		fileManager = Api.Type(game, "SeaPower.Singleton`1").MakeGenericType(manager).GetProperty("Instance", BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic);
		if (fileManager == null)
		{
			throw new MissingMemberException("SeaPower.Singleton<FileManager>.Instance");
		}
		directories = manager.GetProperty("Directories", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
		if (directories == null || !typeof(IEnumerable).IsAssignableFrom(directories.PropertyType))
		{
			throw new MissingMemberException("SeaPower.FileManager.Directories");
		}
	}

	private static FieldInfo Field(Type type, string name, Type expected)
	{
		FieldInfo field = type.GetField(name, BindingFlags.Static | BindingFlags.NonPublic | BindingFlags.Public);
		if (field == null || field.FieldType != expected)
		{
			throw new MissingFieldException(type.FullName, name);
		}
		return field;
	}

	internal static void Install(Assembly game, string packFolder)
	{
		Bind(game);
		int roots = Roots();
		if (!(bool)scanComplete.GetValue(null))
		{
			Api.Log("modifier files: the game has not scanned for #!extend files yet; " + roots + " search directories registered, nothing to repair");
			return;
		}
		int before = Registered(packFolder, out int targetsBefore);
		if (before > 0)
		{
			Api.Log("modifier files: the game's registry already holds " + before + " of this pack's #!extend and #!prepend files among " + targetsBefore + " targets; nothing to repair");
			return;
		}
		// The order matters: a new registry first, so that anything cached after
		// the clear was read with the complete list of mods.
		invalidateRegistry.Invoke(null, null);
		scan.Invoke(null, null);
		invalidateCache.Invoke(null, null);
		int after = Registered(packFolder, out int targetsAfter);
		Api.Log("modifier files repaired: the game's one-shot #!extend scan had run before the Workshop folders were registered (" + targetsBefore + " targets, none from this pack); rescanned " + roots + " search directories: " + targetsAfter + " targets, " + after + " files from this pack, ini cache cleared");
		if (after == 0)
		{
			Api.Log("modifier files: the rescan still holds none of this pack's #!extend files; its catalogs and stubs will not apply this session");
		}
	}

	private static int Roots()
	{
		object manager = fileManager.GetValue(null, null);
		if (manager == null)
		{
			return 0;
		}
		int count = 0;
		foreach (object item in (IEnumerable)directories.GetValue(manager, null))
		{
			count++;
		}
		return count;
	}

	internal static int Registered(string packFolder, out int targets)
	{
		targets = 0;
		int count = 0;
		string prefix = Normalize(packFolder);
		FieldInfo[] registries = new FieldInfo[2] { extendRegistry, prependRegistry };
		foreach (FieldInfo registry in registries)
		{
			if (!(registry.GetValue(null) is Dictionary<string, List<string>> entries))
			{
				continue;
			}
			targets += entries.Count;
			foreach (List<string> files in entries.Values)
			{
				foreach (string file in files)
				{
					if (!string.IsNullOrEmpty(file) && Normalize(file).StartsWith(prefix, StringComparison.OrdinalIgnoreCase))
					{
						count++;
					}
				}
			}
		}
		return count;
	}

	private static string Normalize(string path)
	{
		string text = Path.GetFullPath(path).Replace('\\', '/');
		return text.EndsWith("/") ? text : (text + "/");
	}
}
