"""SEST UI Follow-up (SEST.ContactsFix.dll) ships as recorded and fits the runtime it pins.

The DLL is built outside the repository (it needs the game's own NoesisGUI),
so nothing here can rebuild it. What can be held: the committed DLL and its
source/ against integration/ui-followup/plugin-build.json, the copies in the
pack and the dist against the committed DLL, and the runtime hash the source
pins against the runtime DLL the pack actually ships. A runtime that differs
by one byte turns the whole plugin off on every PC ("inactive; original
behavior retained"), so that mismatch must fail here first.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "integration/ui-followup"
SOURCE = PLUGIN / "source"
RUNTIME = ROOT / "integration/runtime-fixes"
# build_pack.write_contacts_fix copies the DLL into the campaign pack's
# plugins/, and consolidate_packs.py carries it into the dist.
PACKS = (ROOT / "integration/campaign/SEST_Campaign/plugins",
         ROOT / "integration/dist/SEST_Integration/plugins")
HEX = r"([0-9a-f]{64})"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest():
    return json.loads((PLUGIN / "plugin-build.json").read_text(encoding="utf-8"))


def source(name):
    return (SOURCE / name).read_text(encoding="utf-8")


def one(pattern, text, what):
    found = re.findall(pattern, text)
    if len(found) != 1:
        raise AssertionError(f"{what}: expected one match of {pattern!r}, found {len(found)}")
    return found[0]


class ContactsFixRecord(unittest.TestCase):
    def setUp(self):
        self.manifest = manifest()

    def test_the_committed_dll_is_the_recorded_one(self):
        dll = PLUGIN / self.manifest["binary"]
        self.assertEqual(dll.name, "SEST.ContactsFix.dll")
        self.assertEqual(sha256(dll), self.manifest["sha256"])
        self.assertEqual(dll.stat().st_size, self.manifest["bytes"])
        self.assertEqual([p.name for p in PLUGIN.rglob("*.dll")], ["SEST.ContactsFix.dll"],
                         "only the plugin itself is committed: no game, loader or stand-in DLL")

    def test_the_source_is_the_recorded_source(self):
        recorded = self.manifest["sources"]
        present = {p.relative_to(ROOT).as_posix() for p in SOURCE.rglob("*") if p.is_file()}
        self.assertEqual(present, set(recorded), "add or remove a source file in plugin-build.json too")
        for name, expected in recorded.items():
            with self.subTest(source=name):
                self.assertEqual(sha256(ROOT / name), expected,
                                 "The DLL is built off the repository: a source edit needs a rebuilt, "
                                 "re-recorded DLL (integration/ui-followup/README.md)")

    def test_the_attribute_names_the_recorded_version(self):
        plugin = self.manifest["plugin"]
        attribute = f'[ACPlugin("{plugin["id"]}", "{plugin["name"]}", "{plugin["version"]}", null, null)]'
        self.assertIn(attribute, source("ContactsFix.cs"))
        # The same three strings, length-prefixed, in the DLL's attribute blob.
        blob = b"".join(bytes([len(s)]) + s for s in (plugin["id"].encode(), plugin["name"].encode(),
                                                      plugin["version"].encode()))
        self.assertTrue(blob in (PLUGIN / self.manifest["binary"]).read_bytes(),
                        "the DLL's ACPlugin attribute is not the recorded id, name and version")


class PinnedHashes(unittest.TestCase):
    """The hashes ContactsFix accepts, read from its source."""

    def setUp(self):
        self.manifest = manifest()
        self.runtime = json.loads((RUNTIME / "plugin-build.json").read_text(encoding="utf-8"))

    def runtime_pins(self):
        return {
            "ContactsFix.cs RuntimeHash":
                one(r'const string RuntimeHash = "' + HEX + '"', source("ContactsFix.cs"), "RuntimeHash"),
            "CostCatalogueCache.cs":
                one(r'Require\(campaign\.Assembly, "' + HEX + '"\)', source("CostCatalogueCache.cs"),
                    "CostCatalogueCache runtime pin"),
            "DiagnosticModules.cs":
                one(r'"SEST\.RuntimeFixes", "' + HEX + '"', source("DiagnosticModules.cs"),
                    "DiagnosticModules runtime pin"),
        }

    def test_every_runtime_pin_is_the_shipped_runtime(self):
        shipped = sha256(RUNTIME / self.runtime["binary"])
        self.assertEqual(shipped, self.runtime["sha256"])
        for where, pinned in self.runtime_pins().items():
            with self.subTest(pin=where):
                self.assertEqual(pinned, self.runtime["sha256"],
                                 "SEST.ContactsFix.dll accepts only the runtime it pins; with any other it "
                                 "stays inactive. Rebuild it for the new runtime hash, or keep the runtime.")
        self.assertEqual(self.manifest["pins"]["runtime"]["sha256"], self.runtime["sha256"])

    def test_the_dll_carries_the_same_runtime_pin(self):
        # The source was compiled into this DLL: the literal is in its #US heap.
        dll = (PLUGIN / self.manifest["binary"]).read_bytes()
        self.assertTrue(self.runtime["sha256"].encode("utf-16-le") in dll,
                        "the committed DLL was not compiled with the shipped runtime's hash")

    def test_the_other_pins_are_the_recorded_ones(self):
        fix = source("ContactsFix.cs")
        native = re.findall(r'"' + HEX + '"', fix[fix.index("NativeHashes"):fix.index("};", fix.index("NativeHashes"))])
        read = {
            "contact_log": one(r'const string ContactHash = "' + HEX + '"', fix, "ContactHash"),
            "game_scripts": native[0],
            "noesis": native[1],
        }
        self.assertEqual(len(native), 2)
        pins = self.manifest["pins"]
        for key, value in read.items():
            with self.subTest(pin=key):
                self.assertEqual(pins[key]["sha256"], value)
        dll = (PLUGIN / self.manifest["binary"]).read_bytes()
        for key, value in read.items():
            with self.subTest(in_dll=key):
                self.assertTrue(value.encode("utf-16-le") in dll, f"{key} pin not in the DLL")
        self.assertEqual(one(r'"ContactLog", "' + HEX + '"', source("DiagnosticModules.cs"), "ContactLog timing"),
                         read["contact_log"])
        # The game build the runtime itself is gated to.
        self.assertTrue(read["game_scripts"].encode("utf-16-le") in (RUNTIME / self.runtime["binary"]).read_bytes(),
                        "the runtime is gated to another game build than ContactsFix")


class PackCopies(unittest.TestCase):
    def test_every_pack_copy_is_the_committed_dll(self):
        dll = PLUGIN / manifest()["binary"]
        for folder in PACKS:
            with self.subTest(copy=f"{folder.relative_to(ROOT)}/{dll.name}"):
                self.assertTrue((folder / dll.name).is_file(),
                                "not in the pack: build_pack.write_contacts_fix, then "
                                "python3 tools/build_all.py --from-scratch")
                self.assertEqual((folder / dll.name).read_bytes(), dll.read_bytes(),
                                 "Rebuild: python3 tools/build_all.py --from-scratch")

    def test_no_source_or_stand_in_ships(self):
        for folder in PACKS:
            with self.subTest(pack=folder.relative_to(ROOT).as_posix()):
                names = {p.name for p in folder.iterdir()}
                self.assertFalse({p.name for p in SOURCE.iterdir()} & names)
                self.assertNotIn("AnchorChain.dll", names)


def mono_toolchain():
    prefix = os.environ.get("SEST_MONO_PREFIX")
    env = os.environ.copy()
    if prefix:
        p = Path(prefix).resolve()
        env["MONO_CFG_DIR"] = str(p / "etc")
        env["MONO_PATH"] = str(p / "usr/lib/mono/4.5")
        env["LD_LIBRARY_PATH"] = str(p / "usr/lib") + os.pathsep + env.get("LD_LIBRARY_PATH", "")
        mono = p / "usr/bin/mono"
        if mono.is_file():
            return [str(mono), str(p / "usr/lib/mono/4.5/mcs.exe")], str(mono), env
    if shutil.which("mcs") and shutil.which("mono"):
        return ["mcs"], "mono", env
    return None


# The five pure-logic suites, as source/build.py compiles them, and the
# receipt line each prints.
SUITES = {
    "InputPolicyTests": (["InputPolicy.cs", "InputPolicyTests.cs"],
                         r"^(\d+) input regression cases passed$"),
    "FormationModeTests": (["FormationModeState.cs", "FormationModeTests.cs"],
                           r"^(\d+) formation mode regression checks passed$"),
    "PerformancePolicyTests": (["LookupCache.cs", "FlightFlagReader.cs", "UiRefreshGate.cs",
                                "PerformancePolicyTests.cs"],
                               r"^Performance/type-safety checks passed: (\d+)$"),
    "UiRefinementTests": (["UiText.cs", "CompassRouting.cs", "FormationBoundsGate.cs", "UiRefinementTests.cs"],
                          r"^Preparation/compass scenario checks passed: (\d+)$"),
    "StutterPolicyTests": (["CleanupBatchGate.cs", "FrameWindow.cs", "StutterPolicyTests.cs"],
                           r"^Terrain cleanup/frame pacing checks passed: (\d+)$"),
}


class PureLogicSuites(unittest.TestCase):
    """The parts of ContactsFix that need no game assembly, compiled with Mono mcs."""

    def setUp(self):
        self.toolchain = mono_toolchain()
        if self.toolchain is None:
            self.skipTest("no Mono: install mono-mcs or set SEST_MONO_PREFIX")

    def test_the_five_suites_pass(self):
        mcs, mono, env = self.toolchain
        with tempfile.TemporaryDirectory(prefix="sest-contactsfix-") as tmp:
            for name, (files, receipt) in SUITES.items():
                with self.subTest(suite=name):
                    exe = Path(tmp) / f"{name}.exe"
                    build = subprocess.run(mcs + ["-nologo", "-optimize+", "-target:exe", f"-out:{exe}"]
                                           + [str(SOURCE / f) for f in files],
                                           env=env, capture_output=True, text=True, timeout=300)
                    self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
                    run = subprocess.run([mono, str(exe)], env=env, capture_output=True, text=True, timeout=300)
                    self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
                    self.assertRegex(run.stdout.strip(), re.compile(receipt, re.M))
                    self.assertGreater(int(re.search(receipt, run.stdout.strip(), re.M)[1]), 0)


if __name__ == "__main__":
    unittest.main()
