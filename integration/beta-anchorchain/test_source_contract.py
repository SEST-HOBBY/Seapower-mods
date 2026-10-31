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

class BetaSourceContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = MAIN.read_text(encoding="utf-8-sig")
        cls.boot = BOOT.read_text(encoding="utf-8")
        cls.build = BUILD.read_text(encoding="utf-8")
        cls.test = TEST.read_text(encoding="utf-8")

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
        self.assertIn('"enable-beta-261026"', self.boot)
        self.assertIn("if (enabled)", self.boot)
        self.assertIn('Logger.LogInfo("BETA SAFE BOOTSTRAP READY; enable="', self.boot)

    def test_beta_hash_gate_and_safe_fork_only(self):
        self.assertIn("3005bc6d4221a921008778a18dec06515d98c63d3afb6a3a2835b985ab2e7d62", self.boot)
        self.assertIn('Path.Combine(_payloadDirectory, "AnchorChain.dll")', self.boot)
        self.assertIn('GetField("_startOnce"', self.boot)
        self.assertIn("Sha256(payload), expected", self.boot)

    def test_staging_requires_separate_enable(self):
        self.assertIn('if ($Action -eq "Stage")', self.test)
        self.assertIn('elseif ($Action -eq "Enable")', self.test)
        self.assertIn('elseif ($Action -eq "Disable")', self.test)
        self.assertIn('elseif ($Action -eq "Remove")', self.test)
        self.assertIn("BETA SAFE BOOTSTRAP READY; enable=False", self.test)

    def test_build_is_non_installing(self):
        self.assertIn('Join-Path $OutDir "AnchorChain.dll"', self.build)
        self.assertIn('Join-Path $OutDir "SEST.BetaSafeBootstrap.dll"', self.build)
        self.assertNotIn("Copy-Item -LiteralPath $dest -Destination $plugins", self.build)
        self.assertNotIn("Copy-Item -LiteralPath $dest -Destination $upstream", self.build)

if __name__ == "__main__":
    unittest.main(verbosity=2)
