using System;
using System.IO;
using System.Reflection;
using System.Security.Cryptography;
using AnchorChain;

namespace Sest.RuntimeFixes;

[ACPlugin("io.github.sest-hobby.runtime-fixes", "SEST Runtime Fixes Beta", "1.8.0", null, null)]
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
			if (text != "ea653e49632dbaaad16d33b9c51d79b3eec420e7c41954dbcd09d19157beb65a")
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
			// Beta only, default on: WorldSideChoice=0 in [Runtime] leaves
			// Global Command Operations' start page as Dynamic Campaign Mod
			// draws it (Blue only for Theatre Commander). Binds DCM on its own.
			if (Policy.TextOption(lines, "WorldSideChoice", "1") == "1")
			{
				WorldSideChoice.Start(assembly);
			}
			// Beta only, default on: WorldStorms=0 in [Runtime] keeps Dynamic
			// Campaign Mod's weather exactly as it is; a campaign gets placed
			// storms only when its folder holds sest-weather.json. Independent of
			// the combat-cost options below: it binds DCM on its own and never
			// throws. WorldStormsDiagnostics=1 (default off) logs the binding,
			// the sidecar, each storm once per campaign hour and each contact's
			// battle [Environment]. WorldStormsMapLayer=0 (default 1) leaves out the
			// "Weather" entry in the tactical map's Layers menu that draws the
			// campaign's storms in a Dynamic Campaign Mod battle. LocalWeatherView=0
			// (default 1) leaves out the local battle weather: in a Dynamic
			// Campaign Mod battle, sea state, wind, rain, thunder, snow and fog
			// follow the camera over the battle's time (LocalWeatherView.cs);
			// installed here, before the CumulativeCombatCosts return below,
			// like the storms. LocalWeatherAllBattles=0 (default 1) limits it to
			// campaigns with placed storms; LocalWeatherAircraft=0 (default 1)
			// drops the aircraft altitude holds; LocalWeatherAirSeaMaxM (default
			// 1500) is the height above which an aircraft view holds the sea;
			// LocalWeatherClouds=1 (default 0) lets clouds follow too;
			// LocalWeatherFollow=centre (default view) samples the battle centre.
			if (Policy.TextOption(lines, "WorldStorms", "1") == "1")
			{
				var localWeather = LocalWeatherOptions.Parse((name, fallback) => Policy.TextOption(lines, name, fallback));
				foreach (string bad in localWeather.Bad) Api.Log("world storms local weather: [Runtime] " + bad);
				LocalWeatherView.Configure(localWeather);
				WorldStorms.Start(assembly, Policy.TextOption(lines, "WorldStormsDiagnostics", "0") == "1",
					Policy.TextOption(lines, "WorldStormsMapLayer", "1") == "1",
					Policy.TextOption(lines, "LocalWeatherView", "1") == "1");
			}
			// Beta only, default on: SeaIce=0 in [Runtime] keeps battles as before.
			// Seasonal sea ice from the weather branch's climatology in any battle
			// (sonar ambient noise, ship speed by ice class, submarines held under
			// heavy ice, a visible ice sheet). Each part has its own switch
			// (SeaIceNoise, SeaIceShips, SeaIceSubmarines, SeaIceSheet, SeaIceMapLayer) and fails
			// closed with one log line; SeaIceDiagnostics=1 (default off) logs the
			// ice at the selected unit, speed caps, submarine holds and the sheet's
			// chunk counts and build cost. Independent of the combat-cost options.
			if (Policy.TextOption(lines, "SeaIce", "1") == "1")
			{
				try
				{
					SeaIceBattle.Install(assembly, lines);
					if (Policy.TextOption(lines, "SeaIceSheet", "1") == "1")
					{
						SeaIceSheet.Install(lines);
					}
					// SeaIceMapLayer=0 (default 1) leaves out the "Sea ice" entry in
					// the tactical map's Layers menu (edge and heavy-pack lines, pack
					// fill, hover readout; SeaIceMap.cs). Fails closed on its own.
					if (Policy.TextOption(lines, "SeaIceMapLayer", "1") == "1")
					{
						SeaIceMap.Install(assembly, lines);
					}
				}
				catch (Exception error12)
				{
					Api.LogFailure("sea ice not installed; battles keep the native ice", error12);
				}
			}
			// Beta only, default OFF: IceShelves=1 / Icebergs=1 in [Runtime] turn on
			// Antarctic ice-shelf cliffs (ships and submarines kept out, with a stand-off)
			// and icebergs from the weather branch's climatology (IceFeaturesBattle.cs).
			// Install never throws; each part fails closed with one log line, and with
			// neither switch set it binds nothing. IceFeaturesDiagnostics=1 logs.
			IceFeaturesBattle.Install(assembly, lines);
			// Beta only, default on: CampaignIce=0 in [Runtime] keeps Dynamic
			// Campaign Mod's campaign map and movement as they are. Sea ice on
			// the campaign globe (on every weather layer, and alone with the
			// weather layer off), "Ice 72 % (heavy pack)" in the map readout,
			// and surface groups slowed by the ice at their position
			// (CampaignIce.cs); CampaignIceMap=0 / CampaignIceMovement=0 leave
			// one part out, CampaignIceDiagnostics=1 (default off) logs. Binds
			// DCM 1.0.4 (b816459d) lazily on its own and fails closed with one
			// line; independent of SeaIce and of the combat-cost options.
			if (Policy.TextOption(lines, "CampaignIce", "1") == "1")
			{
				CampaignIce.Start(assembly, lines);
			}
			if (!Policy.OptionEnabled(lines, "CumulativeCombatCosts"))
			{
				return;
			}
			// Beta only, default OFF since 15 Nov: on the owner's PC Unity drew no IMGUI on
			// the Pop-Out monitor (probe repaint=False), so the button could not work.
			// StrikePopOut=1 in [Runtime] still turns it on for testing. Off, the
			// Coordinated Strike panel stays on the main screen without the button.
			CoordinatedStrikeRefinements.PopOutEnabled = Policy.TextOption(lines, "StrikePopOut", "0") == "1";
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
