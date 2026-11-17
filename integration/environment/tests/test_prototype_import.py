"""The imported prototype is kept as supplied: its 11 tests still pass, and its generator
still reproduces the demo file whose SHA-256 is in its MANIFEST.json."""
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

from helpers import ENV_ROOT

PROTO = ENV_ROOT / "prototype-20261118"


class TestPrototype(unittest.TestCase):
    def test_eleven_prototype_tests_pass(self):
        loader = unittest.TestLoader()
        sys.path.insert(0, str(PROTO / "tests"))
        try:
            suite = loader.discover(str(PROTO / "tests"), top_level_dir=str(PROTO / "tests"))
            result = unittest.TestResult()
            suite.run(result)
        finally:
            sys.path.remove(str(PROTO / "tests"))
        self.assertEqual(result.testsRun, 11)
        self.assertEqual((result.failures, result.errors), ([], []))

    def test_demo_regenerates_manifest_hash(self):
        manifest = json.loads((PROTO / "MANIFEST.json").read_text())
        want = next(f["sha256"] for f in manifest["files"] if f["path"] == "data/demo_environment.json")
        spec = importlib.util.spec_from_file_location("proto_env_model", PROTO / "src" / "environment_model.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "demo.json"
            mod.build_demo(out)
            self.assertEqual(hashlib.sha256(out.read_bytes()).hexdigest(), want)

    def test_kept_sources_match_manifest(self):
        manifest = {f["path"]: f["sha256"] for f in json.loads((PROTO / "MANIFEST.json").read_text())["files"]}
        checked = 0
        for rel, digest in manifest.items():
            p = PROTO / rel
            if p.exists() and p.suffix in (".py", ".json", ".html") and rel != "MANIFEST.json":
                self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), digest, rel)
                checked += 1
        self.assertGreaterEqual(checked, 9)


if __name__ == "__main__":
    unittest.main()
