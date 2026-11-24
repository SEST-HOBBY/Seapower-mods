#!/usr/bin/env python3
"""Source-contract checks for the beta loader. NOT a Unity/gameplay test.

These are safety regressions against accidental reintroduction of PR #53's
unbounded retry path or automatic activation. Running this script does not
execute either DLL, access Steam or modify the game.
"""
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
MAIN = HERE / "source" / "Main.cs"
BOOT = HERE / "SEST.BetaSafeBootstrap.cs"
BUILD = HERE / "build.ps1"
TEST = HERE / "test.ps1"
PROJECT = HERE / "source" / "AnchorChain.csproj"
BOOTSTRAP_PROJECT = HERE / "bootstrap" / "SEST.BetaSafeBootstrap.csproj"

class BetaSourceContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = MAIN.read_text(encoding="utf-8-sig")
        cls.boot = BOOT.read_text(encoding="utf-8")
        cls.build = BUILD.read_text(encoding="utf-8")
        cls.test = TEST.read_text(encoding="utf-8")
        cls.project = PROJECT.read_text(encoding="utf-8")
        cls.bootstrap_project = BOOTSTRAP_PROJECT.read_text(encoding="utf-8")

    def test_fork_keeps_original_assembly_identity(self):
        self.assertIn("public class AnchorChainLoader : BaseUnityPlugin, Preloader.IPluginLoader", self.main)
        self.assertIn('[BepInPlugin("io.github.seapower_modders.anchorchain", "AnchorChain", "1.1.0")]', self.main)

    def test_bounded_loader_entry(self):
        self.assertIn("Interlocked.CompareExchange(ref _startOnce, 1, 0)", self.main)
        self.assertIn("LoadPluginsCore();", self.main)
        self.assertIn("catch (Exception ex)", self.main)

    def test_failed_plugin_never_retries(self):
        self.assertIn("HashSet<string> failedPlugins = new();", self.main)
        self.assertIn("failedPlugins.Add(guid);", self.main)
        self.assertIn("alreadyLoaded.Contains(x) || failedPlugins.Contains(x)", self.main)

    def test_aborts_if_no_progress(self):
        marker = "if (!loadedOne && currentLevel.Count != 0)"
        self.assertIn(marker, self.main)
        after = self.main.split(marker, 1)[1]
        self.assertIn("break;", after[:500])

    def test_finite_load_budget(self):
        self.assertIn("levelBudget = recognizedPlugins.Count + 1", self.main)
        self.assertIn("if (--levelBudget < 0)", self.main)

    def test_bootstrap_does_not_auto_activate(self):
        self.assertIn('"enable.flag"', self.boot)
        self.assertIn('"enable-093-261123-ea653e49"', self.boot)
        self.assertIn("if (enabled)", self.boot)
        self.assertIn('Logger.LogInfo("BETA SAFE BOOTSTRAP READY; enable="', self.boot)

    def test_beta_hash_gate_and_safe_fork_only(self):
        self.assertIn("ea653e49632dbaaad16d33b9c51d79b3eec420e7c41954dbcd09d19157beb65a", self.boot)
        self.assertIn('Path.Combine(_payloadDirectory, "AnchorChain.dll")', self.boot)
        self.assertIn('GetField("_startOnce"', self.boot)
        self.assertIn("Sha256(payload), expected", self.boot)

    def test_staging_requires_separate_enable(self):
        self.assertIn('if ($Action -eq "Stage")', self.test)
        self.assertIn('elseif ($Action -eq "Enable")', self.test)
        self.assertIn('elseif ($Action -eq "Disable")', self.test)
        self.assertIn('elseif ($Action -eq "Remove")', self.test)
        self.assertIn("BETA SAFE BOOTSTRAP READY; enable=False", self.test)

    def test_game_particle_system_reference(self):
        self.assertIn('<Reference Include="UnityEngine.ParticleSystemModule">', self.project)
        self.assertIn('UnityEngine.ParticleSystemModule.dll', self.project)
        self.assertIn('$particleModule', self.build)

    def test_bootstrap_uses_netstandard_sdk_not_framework_csc(self):
        self.assertIn("<TargetFramework>netstandard2.1</TargetFramework>", self.bootstrap_project)
        self.assertIn('<Reference Include="BepInEx">', self.bootstrap_project)
        self.assertIn('<Reference Include="UnityEngine.CoreModule">', self.bootstrap_project)
        self.assertIn(r'bootstrap\SEST.BetaSafeBootstrap.csproj', self.build)
        self.assertIn(r'bootstrap\bin\Release\netstandard2.1\SEST.BetaSafeBootstrap.dll', self.build)
        self.assertNotIn(r'Framework64\\v4.0.30319\\csc.exe', self.build)

    def test_build_is_non_installing(self):
        self.assertIn('Join-Path $OutDir "AnchorChain.dll"', self.build)
        self.assertIn('Join-Path $OutDir "SEST.BetaSafeBootstrap.dll"', self.build)
        self.assertNotIn("Copy-Item -LiteralPath $dest -Destination $plugins", self.build)
        self.assertNotIn("Copy-Item -LiteralPath $dest -Destination $upstream", self.build)

    def test_metadata_preparation_precedes_clr_loading(self):
        self.assertLess(self.main.index("BetaAssemblyPolicy.Prepare(asmPath"), self.main.index("Assembly.LoadFile(prepared)"))
        policy = (HERE / 'source' / 'AssemblyPolicy.cs').read_text()
        self.assertIn('"ExtendedGuidance"', policy)
        # R14: every admitted image is checked against the game's own members
        # after any rewrite, and before the CLR sees it.
        self.assertLess(policy.index('AdaptCapturedImage(module'), policy.index('UnresolvedNativeMembers(module, native)'))
        self.assertLess(policy.index('UnresolvedNativeMembers(module, native)'), policy.index('module.Write(temporary)'))
        self.assertIn('SKIPPED before CLR load', policy)
        self.assertIn('InvalidNativeFields', policy)

    def test_campaign_salvo_hold_and_speed_are_not_rewritten(self):
        # Dynamic Campaign Mod 1.0.2 (as 1.0.0 and 1.0.1): the loader no longer renames the mod's
        # salvo hold onto AI.AutoEngageAmmoBlocked (the mod switches that
        # feature off itself on 0.9.3), and no longer rewrites its speed
        # calls, which are valid as written. The managed checks are
        # R6_CampaignSalvo and the LookTurn checks in BetaApiTests.
        sources = "".join(path.read_text(encoding="utf-8-sig") for path in sorted((HERE / "source").glob("*.cs")))
        self.assertFalse((HERE / "source" / "AssemblyAdapters.CampaignSalvo.cs").exists())
        for retired in ("AutoEngageAmmoBlocked", "salvo-target", "salvo-applied", "salvo-fact",
                        "ConstantSpeedRequest", "SetSpeedRequest", "speed-make", "speed-set"):
            self.assertNotIn(retired, sources)
        # 1.0.1 added three Assembly.Location reads, kept in 1.0.2 (DeferredPatcher, BrokenObjectsWatch).
        # On 261123 the campaign audit lives in AssemblyAdapters.Campaign261123.cs,
        # the four inline rules plus the seven map bridges.
        self.assertIn('"HasNightCapableSensors=1, attack-property=14, drawing-layer=1, flat-tiles=2, fuel-refresh=1, globe-fail-guard=1, group-brush=2, locations=4, scheduler-timing=1, side-colour=8, terrain-background=1"', sources)
        self.assertNotIn('"HasNightCapableSensors=1, attack-property=14, fuel-refresh=1, locations=4"', sources)
        self.assertIn('"18a2416e6dd51bd574a5012405b088442b4ef84f54028c73cd7b396429be9929"', sources)
        self.assertNotIn("6008e9c53f8e26f13cfa72d05518f200db70c795a899187cd6106c14972fb400", sources)
        self.assertNotIn("652fe464dc23ac3c0063e5ab09dc4656634f30d1d254c782498ef779cb30ac77", sources)

    def test_loader_honours_mod_manager_ticks(self):
        # Anchor Chain 1.2.0 scans only ticked, existing Mod Manager folders,
        # loads nothing when Anchor Chain itself is unticked, and still finds
        # user configs in ACConfigs, which Mod Manager lists unticked.
        self.assertIn("FileManager.Instance.Directories.Select(dir => (Directory: dir.DirectoryInfo, dir.IsChecked))", self.main)
        self.assertIn("row.IsChecked && row.Directory is { Exists: true }", self.main)
        self.assertIn('row.IsChecked && row.Directory?.Name == "3380210757"', self.main)
        self.assertIn(".Append(Path.Join(configPath, fileName))", self.main)
        self.assertNotIn("ConvertAll(dir => dir.DirectoryInfo)", self.main)
        self.assertNotIn("_allDirectories.Add(new DirectoryInfo(_configPath))", self.main)

    def test_r16_loader_interop(self):
        # R16: pinned BepInEx-only Workshop plugins, the duplicate gate, Keel
        # holds and the nested-loader companion check (BetaApiTests R6_*).
        sources = {path.name: path.read_text(encoding="utf-8-sig") for path in sorted((HERE / "source").glob("*.cs"))}
        everything = "".join(sources.values())
        # No same-GUID shim: SEST never registers Keel's starter or Keel types.
        self.assertNotIn('BepInPlugin("dev.sewerlabs', everything)
        self.assertNotIn("namespace SeaPowerKeel", everything)
        self.assertNotIn("PluginInfos[", everything)
        self.assertNotIn("PluginInfos.Add", everything)
        policy = sources["WorkshopBepInPolicy.cs"]
        host = policy[policy.index("HostSatisfiedDependencies = new"):]
        host = host[:host.index("};")]
        self.assertEqual(host.count("] = "), 1)
        runner = sources["WorkshopBepInRunner.cs"]
        self.assertNotIn("HideAndDontSave", runner)
        self.assertIn("DontDestroyOnLoad(host)", runner)
        # Read-only toward Keel's files.
        for text in sources.values():
            for line in text.splitlines():
                if "Keel" in line:
                    self.assertNotIn("File.Delete", line)
                    self.assertNotIn("File.Move", line)
        # Gate after metadata preparation and before the CLR load; runner after the AC plugins.
        self.assertLess(self.main.index("BetaAssemblyPolicy.Prepare(asmPath"), self.main.index("duplicates.Admit(asmPath, prepared"))
        self.assertLess(self.main.index("duplicates.Admit(asmPath, prepared"), self.main.index("BetaAssemblyPolicy.CompanionPreloads(asmPath)"))
        self.assertLess(self.main.index("BetaAssemblyPolicy.CompanionPreloads(asmPath)"), self.main.index("Assembly.LoadFile(prepared)"))
        self.assertIn("duplicates.Release(asmPath)", self.main)
        self.assertLess(self.main.index("RunPending(recognizedPlugins"), self.main.index("WorkshopBepInRunner.Start(workshopBepIn"))
        self.assertIn("private static List<DirectoryInfo> _allDirectories", self.main)
        # Keel's patcher warning: in the bootstrap, before the preloader gate a takeover trips.
        self.assertLess(self.boot.index("KeelPatcherWarning(Paths.PatcherPluginPath)"), self.boot.index("Beta safe loader INACTIVE: uninspected"))
        self.assertNotIn("KeelPatcherWarning", self.main)
        prepare = sources["AssemblyPolicy.cs"]
        self.assertLess(prepare.index('== "ExtendedGuidance"'), prepare.index('== "SensorView.ExtendedGuidance"'))
        self.assertLess(prepare.index("WorkshopBepInRefusal(module, source, bepin)"), prepare.index("InvalidNativeFields(module, native)"))
        self.assertLess(prepare.index("UnresolvedNativeMembers(module, native)"), prepare.index("PrepareCompanions(source"))

if __name__ == "__main__":
    unittest.main(verbosity=2)
