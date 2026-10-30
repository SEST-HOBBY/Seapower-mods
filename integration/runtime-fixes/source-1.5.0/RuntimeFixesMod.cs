using System;
using System.IO;
using System.Reflection;
using System.Security.Cryptography;
using AnchorChain;

namespace Sest.RuntimeFixes {
[ACPlugin("io.github.sest-hobby.runtime-fixes", "SEST Runtime Fixes", "1.5.0", null, null)]
public sealed class RuntimeFixesMod : IAnchorChainMod
{
	public void TriggerEntryPoint()
	{
		try
		{
			Assembly game = Api.FindType("SeaPower.ObjectBase").Assembly;
			// Sea Power 0.8.7 Build 261021, from the player's 23 October 2026 export; verify_native_api.py checks it.
			const string inspected = "eab2297ba92c6013958bdb2cf16d5794a4731330818ce353f89dc2241e16a3bd";
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
			if (Policy.OptionEnabled(config, "TowedSensorGuard"))
			{
				try { TowedSensorGuard.Install(game); }
				catch (Exception e) { Api.LogFailure("towed sensor correction not installed", e); }
			}
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
			if (Policy.OptionEnabled(config, "PreparationMap"))
			{
				try { PreparationMap.Install(game); }
				catch (Exception e) { Api.LogFailure("preparation map refresh not installed", e); }
			}
			if (Policy.OptionEnabled(config, "CampaignCombatCosts"))
			{
				try { CampaignCosts.Install(game); }
				catch (Exception e) { Api.LogFailure("campaign combat costs not installed", e); }
			}
			if (Policy.OptionEnabled(config, "CombatCostInventories"))
			{
				try { CampaignInventory.Install(game); }
				catch (Exception e) { Api.LogFailure("combat cost inventory capture not installed", e); }
			}
			if (Policy.OptionEnabled(config, "CumulativeCombatCosts"))
			{
				try { F11CombatCosts.Install(game, Path.Combine(Path.GetDirectoryName(settings), "SEST", "combat-history-v1.txt")); }
				catch (Exception e) { Api.LogFailure("F11 cumulative combat costs not installed", e); }
			}
		}
		catch (Exception e) { Api.LogFailure("inactive", e); }
	}
}

}
