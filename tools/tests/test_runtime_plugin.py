"""The runtime DLL the pack ships must be the one plugin-build.json records.

Normally build_plugin.py writes the DLL from the .cs files here, and a source
edit must not leave a stale committed DLL in the installer. While the
manifest's status is "captured-binary-source-not-recovered" the DLL is a
byte-for-byte capture (Runtime 1.5.0 from the owner's PC) whose source is not
in the repository: then the DLL is held to its recorded hash, the builder
must refuse to overwrite it, and the .cs files are only its fork base.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "integration/runtime-fixes"
CAPTURED = "captured-binary-source-not-recovered"
# write_runtime_fixes copies these into the campaign pack's plugins/, and
# consolidate_packs.py carries them into the dist.
SHIPPED = ("SEST.RuntimeFixes.dll", "sest_runtime.ini", "SEST_RUNTIME_README.txt")
PACKS = (ROOT / "integration/campaign/SEST_Campaign/plugins",
         ROOT / "integration/dist/SEST_Integration/plugins")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RuntimePluginBuild(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((PLUGIN / "plugin-build.json").read_text())

    def test_the_committed_binary_is_the_recorded_one(self):
        dll = PLUGIN / self.manifest["binary"]
        self.assertEqual(sha256(dll), self.manifest["sha256"])
        self.assertEqual([p.name for p in PLUGIN.glob("*.dll")], ["SEST.RuntimeFixes.dll"])

    def test_every_pack_copy_is_the_committed_one(self):
        for folder in PACKS:
            for name in SHIPPED:
                with self.subTest(copy=f"{folder.relative_to(ROOT)}/{name}"):
                    self.assertEqual((folder / name).read_bytes(), (PLUGIN / name).read_bytes(),
                                     "Rebuild: python3 tools/build_all.py --from-scratch")

    def test_compiled_binary_matches_its_reviewed_sources(self):
        if self.manifest.get("status") == CAPTURED:
            self.skipTest("captured binary: no source in the repository builds it")
        for name, expected in self.manifest["inputs"].items():
            with self.subTest(source=name):
                self.assertEqual(sha256(ROOT / name), expected,
                                 "Rebuild integration/runtime-fixes/build_plugin.py after editing runtime sources")


class CapturedRuntime(unittest.TestCase):
    """Only while plugin-build.json says the DLL is a capture."""

    def setUp(self):
        self.manifest = json.loads((PLUGIN / "plugin-build.json").read_text())
        if self.manifest.get("status") != CAPTURED:
            self.skipTest("the runtime DLL is built from the sources here")

    def test_the_manifest_says_what_the_capture_is(self):
        m = self.manifest
        self.assertEqual(m["provenance"]["files"][m["binary"]]["sha256"], m["sha256"])
        self.assertEqual(m["provenance"]["files"][m["binary"]]["bytes"], (PLUGIN / m["binary"]).stat().st_size)
        self.assertIn("fork base", m["source_note"])
        self.assertNotEqual(m["fork_base"]["sha256"], m["sha256"])
        # The ACPlugin attribute's version string, length-prefixed as in the
        # custom attribute blob: the capture is the version the manifest names.
        version = m["plugin"]["version"].encode()
        self.assertTrue(bytes([len(version)]) + version in (PLUGIN / m["binary"]).read_bytes(),
                        "the DLL's ACPlugin attribute does not carry the recorded version")

    def test_the_fork_base_sources_are_unchanged(self):
        # Editing the fork base changes nothing that ships while the DLL is a
        # capture. The builder itself is left out: it gained the refusal below.
        for name, expected in self.manifest["fork_base"]["inputs"].items():
            if name.endswith("build_plugin.py"):
                continue
            with self.subTest(source=name):
                self.assertEqual(sha256(ROOT / name), expected,
                                 "The shipped runtime is a captured binary; its fork base does not "
                                 "build it. Recover its source first (integration/runtime-fixes/README.md)")

    def test_the_builder_refuses_to_overwrite_it(self):
        dll = PLUGIN / self.manifest["binary"]
        before = dll.read_bytes()
        run = subprocess.run([sys.executable, str(PLUGIN / "build_plugin.py")],
                             capture_output=True, text=True, timeout=60)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("refusing to overwrite", run.stderr)
        self.assertIn("--replace-captured-binary", run.stderr)
        self.assertEqual(dll.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
