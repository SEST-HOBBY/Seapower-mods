"""The runtime DLL the pack ships must be the one plugin-build.json records.

Normally build_plugin.py writes the DLL from the .cs files here, and a source
edit must not leave a stale committed DLL in the installer. While the
manifest's status is "captured-binary-source-not-recovered" the DLL is a
byte-for-byte capture (Runtime 1.5.0 from the owner's PC) whose source is not
in the repository: then the DLL is held to its recorded hash, the builder
must refuse to overwrite it, and the .cs files are only its fork base.

A scratch build (build_plugin.py --source DIR --output PATH) compiles another
folder, such as source-1.5.0/, to a path of its own and leaves the committed
DLL and record alone; --source without --output and an --output that names
the committed DLL are refused before any toolchain is touched.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
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


def builder_copy(tmp):
    """A copy of integration/runtime-fixes (and the stub it compiles with)
    under tmp, laid out as in the checkout. The builder is only ever run on
    such a copy: if its refusal ever broke, it would overwrite the copy's DLL
    and record, never the committed ones."""
    plugin = tmp / "integration/runtime-fixes"
    shutil.copytree(PLUGIN, plugin, ignore=shutil.ignore_patterns("__pycache__"))
    stubs = tmp / "integration/menu-background/stubs"
    stubs.mkdir(parents=True)
    shutil.copy2(ROOT / "integration/menu-background/stubs/AnchorChain.cs", stubs)
    return plugin


def run_builder(plugin, *args):
    # No SEST_MONO_PREFIX and an empty PATH: if the refusal broke, the build
    # would stop at "Install mono-mcs" instead of compiling.
    env = {k: v for k, v in os.environ.items() if k not in ("SEST_MONO_PREFIX", "PATH")}
    env["PATH"] = ""
    return subprocess.run([sys.executable, str(plugin / "build_plugin.py"), *args], cwd=plugin, env=env,
                          capture_output=True, text=True, timeout=60)


def toolchain_available():
    return bool(os.environ.get("SEST_MONO_PREFIX")) or bool(shutil.which("mcs") and shutil.which("mono"))


def run_builder_with_toolchain(plugin, *args):
    # The real toolchain, for a scratch build that compiles and runs the mocked tests.
    return subprocess.run([sys.executable, str(plugin / "build_plugin.py"), *args], cwd=plugin,
                          capture_output=True, text=True, timeout=900)


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
        with tempfile.TemporaryDirectory(prefix="sest-runtime-guard-") as tmp:
            plugin = builder_copy(Path(tmp))
            dll, record = plugin / self.manifest["binary"], plugin / "plugin-build.json"
            before = dll.read_bytes(), record.read_bytes()
            run = run_builder(plugin)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("refusing to overwrite", run.stderr)
            self.assertIn("captured SEST Runtime " + self.manifest["plugin"]["version"], run.stderr)
            self.assertIn("--replace-captured-binary", run.stderr)
            self.assertEqual((dll.read_bytes(), record.read_bytes()), before)

    def test_the_builder_refuses_when_the_captured_dll_is_missing(self):
        # Building then would write the fork base and a format-1 record over
        # the capture's provenance.
        with tempfile.TemporaryDirectory(prefix="sest-runtime-guard-") as tmp:
            plugin = builder_copy(Path(tmp))
            (plugin / self.manifest["binary"]).unlink()
            record = (plugin / "plugin-build.json").read_bytes()
            run = run_builder(plugin)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("refusing to overwrite", run.stderr)
            self.assertIn("itself is missing", run.stderr)
            self.assertFalse((plugin / self.manifest["binary"]).exists())
            self.assertEqual((plugin / "plugin-build.json").read_bytes(), record)


class BuilderFailsClosed(unittest.TestCase):
    """build_plugin.py treats a DLL its record does not account for as a capture."""

    def check_refusal(self, record_text, expect):
        with tempfile.TemporaryDirectory(prefix="sest-runtime-guard-") as tmp:
            plugin = builder_copy(Path(tmp))
            dll, record = plugin / "SEST.RuntimeFixes.dll", plugin / "plugin-build.json"
            record.write_text(record_text)
            before = dll.read_bytes()
            run = run_builder(plugin)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("refusing to overwrite", run.stderr)
            self.assertIn(expect, run.stderr)
            self.assertIn("--replace-captured-binary", run.stderr)
            self.assertEqual(dll.read_bytes(), before)
            self.assertEqual(record.read_text(), record_text)

    def test_an_unreadable_record(self):
        self.check_refusal('{"status": "captured-binary-source-not', "cannot be read")

    def test_a_record_that_is_not_an_object(self):
        self.check_refusal("[]\n", "not a JSON object")

    def test_a_built_record_of_another_dll(self):
        # As if a merge brought back the fork base's format-1 record beside
        # the captured DLL.
        base = json.loads((PLUGIN / "plugin-build.json").read_text()).get("fork_base", {})
        other = base.get("sha256", "0" * 64)
        old = {"format": 1, "binary": "SEST.RuntimeFixes.dll", "sha256": other, "inputs": base.get("inputs", {})}
        self.check_refusal(json.dumps(old, indent=2) + "\n", "records sha256 " + other)


class ScratchBuilds(unittest.TestCase):
    """build_plugin.py --source/--output writes elsewhere and never the committed DLL or record."""

    def setUp(self):
        self.manifest = json.loads((PLUGIN / "plugin-build.json").read_text())

    def test_source_without_output_is_refused(self):
        with tempfile.TemporaryDirectory(prefix="sest-runtime-scratch-") as tmp:
            plugin = builder_copy(Path(tmp))
            before = (plugin / "SEST.RuntimeFixes.dll").read_bytes(), (plugin / "plugin-build.json").read_bytes()
            run = run_builder(plugin, "--source", str(plugin / "source-1.5.0"))
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("--source needs --output", run.stderr)
            self.assertEqual(((plugin / "SEST.RuntimeFixes.dll").read_bytes(), (plugin / "plugin-build.json").read_bytes()), before)

    def test_output_naming_the_committed_dll_is_refused(self):
        with tempfile.TemporaryDirectory(prefix="sest-runtime-scratch-") as tmp:
            plugin = builder_copy(Path(tmp))
            before = (plugin / "SEST.RuntimeFixes.dll").read_bytes()
            run = run_builder(plugin, "--output", str(plugin / "SEST.RuntimeFixes.dll"))
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("names the committed DLL", run.stderr)
            self.assertEqual((plugin / "SEST.RuntimeFixes.dll").read_bytes(), before)

    def test_a_scratch_build_of_the_fork_base_reproduces_it(self):
        # The fork base compiles to its recorded hash through --source/--output,
        # its mocked regressions run, and the capture beside it stays as it was.
        if not toolchain_available():
            self.skipTest("no Mono toolchain (SEST_MONO_PREFIX or mcs on PATH)")
        with tempfile.TemporaryDirectory(prefix="sest-runtime-scratch-") as tmp:
            plugin = builder_copy(Path(tmp))
            dll, record = plugin / "SEST.RuntimeFixes.dll", plugin / "plugin-build.json"
            before = dll.read_bytes(), record.read_bytes()
            out = Path(tmp) / "scratch" / "SEST.RuntimeFixes.dll"
            run = run_builder_with_toolchain(plugin, "--source", str(plugin), "--output", str(out))
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("Runtime regressions passed", run.stdout)
            self.assertEqual(sha256(out), self.manifest["fork_base"]["sha256"])
            self.assertEqual((dll.read_bytes(), record.read_bytes()), before)


if __name__ == "__main__":
    unittest.main()
