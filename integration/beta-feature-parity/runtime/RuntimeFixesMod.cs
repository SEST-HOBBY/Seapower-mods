using System;
using System.IO;
using System.Reflection;
using System.Security.Cryptography;
using AnchorChain;

namespace Sest.RuntimeFixes;

[ACPlugin("io.github.sest-hobby.runtime-fixes", "SEST Runtime Fixes Beta", "1.7.0", null, null)]
public sealed class RuntimeFixesMod : IAnchorChainMod
{
	public void TriggerEntryPoint()
	{
		try
		{
			Assembly assembly = Api.FindType("SeaPower.ObjectBase").Assembly;
			string text;
			using (FileStream inputStream = File.OpenRead(assembly.Location))
			{
				using SHA256 sHA = SHA256.Create();
				text = BitConverter.ToString(sHA.ComputeHash(inputStream)).Replace("-", string.Empty).ToLowerInvariant();
			}
			if (text != "3f56861f09e867f315b194c81a7a2450154ccc6bb5afb769b4956dfd4a00503a")
			{
				Api.Log("inactive: uninspected native assembly " + text);
				return;
			}
			string fullName = Directory.GetParent(typeof(RuntimeFixesMod).Assembly.Location).Parent.FullName;
			string path = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "AppData", "LocalLow", "Triassic Games", "Sea Power", "usersettings.ini");
			if (!Policy.PackEnabled(File.ReadAllLines(path), new DirectoryInfo(fullName).Name))
			{
				Api.Log("inactive: owning pack is not enabled in usersettings.ini; restart after enabling it");
				return;
			}
			string[] lines = File.ReadAllLines(Path.Combine(fullName, "plugins", "sest_runtime.ini"));
			// Beta only: both default to on when the pack's options file predates them.
			if (Policy.TextOption(lines, "ModifierRegistry", "1") == "1")
			{
				try
				{
					ModifierRegistry.Install(assembly, fullName);
				}
				catch (Exception error9)
				{
					Api.LogFailure("modifier file check not installed", error9);
				}
			}
			if (Policy.TextOption(lines, "HideVersionWatermark", "1") == "1")
			{
				try
				{
					VersionWatermark.Install(assembly);
				}
				catch (Exception error10)
				{
					Api.LogFailure("version watermark not hidden", error10);
				}
			}
			if (Policy.OptionEnabled(lines, "TowedSensorGuard"))
			{
				try
				{
					TowedSensorGuard.Install(assembly);
				}
				catch (Exception error)
				{
					Api.LogFailure("towed sensor correction not installed", error);
				}
			}
			if (Policy.OptionEnabled(lines, "TerrainClearance"))
			{
				try
				{
					TerrainClearance.Install(assembly);
				}
				catch (Exception error2)
				{
					Api.LogFailure("terrain correction not installed", error2);
				}
			}
			if (Policy.OptionEnabled(lines, "TaskForceDebrief"))
			{
				try
				{
					TaskForceDebrief.Install(assembly);
				}
				catch (Exception error3)
				{
					Api.LogFailure("debrief correction not installed", error3);
				}
			}
			if (Policy.OptionEnabled(lines, "PreparationMap"))
			{
				try
				{
					PreparationMap.Install(assembly);
				}
				catch (Exception error4)
				{
					Api.LogFailure("preparation map refresh not installed", error4);
				}
			}
			if (Policy.OptionEnabled(lines, "CampaignCombatCosts"))
			{
				try
				{
					CampaignCosts.Install(assembly);
				}
				catch (Exception error5)
				{
					Api.LogFailure("campaign combat costs not installed", error5);
				}
			}
			if (Policy.OptionEnabled(lines, "CombatCostInventories"))
			{
				try
				{
					CampaignInventory.Install(assembly);
				}
				catch (Exception error6)
				{
					Api.LogFailure("combat cost inventory capture not installed", error6);
				}
			}
			// Beta only, default on: MissionAwards=0 in [Runtime] turns the
			// runtime mission ribbons off; native awards are unaffected.
			if (Policy.TextOption(lines, "MissionAwards", "1") == "1")
			{
				try
				{
					MissionAwards.Install(assembly);
				}
				catch (Exception error11)
				{
					Api.LogFailure("runtime mission awards not installed", error11);
				}
			}
			if (!Policy.OptionEnabled(lines, "CumulativeCombatCosts"))
			{
				return;
			}
			try
			{
				F11CombatCosts.Install(assembly, Path.Combine(Path.GetDirectoryName(path), "SEST", "combat-history-v1.txt"));
			}
			catch (Exception error7)
			{
				Api.LogFailure("F11 cumulative combat costs not installed", error7);
			}
		}
		catch (Exception error8)
		{
			Api.LogFailure("inactive", error8);
		}
	}
}
