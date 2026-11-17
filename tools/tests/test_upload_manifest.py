#!/usr/bin/env python3
"""The release's upload manifest and the tool that keeps it (tools/refresh_upload_manifest.py).

    python3 -m unittest discover -s tools/tests -p 'test_upload_manifest.py' -v
"""
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def tool():
    spec = importlib.util.spec_from_file_location("refresh_upload_manifest",
                                                  ROOT / "tools/refresh_upload_manifest.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Refresh(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tool = tool()

    def tree(self, temp, files, manifest):
        root = Path(temp)
        for rel, data in files.items():
            path = root / self.tool.DIST / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        path = root / self.tool.MANIFEST
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest, separators=(",", ":")) + "\n", encoding="utf-8")
        return root

    def test_a_rebuild_is_listed_and_every_other_field_is_kept(self):
        stale = {"format": 1, "release_revision": "R12", "file_count": 2,
                 "files": [{"path": "_info.ini", "bytes": 3, "sha256": hashlib.sha256(b"old").hexdigest()},
                           {"path": "gone.ini", "bytes": 1, "sha256": hashlib.sha256(b"x").hexdigest()}],
                 "ribbons": {"total": 75}}
        with tempfile.TemporaryDirectory() as temp:
            root = self.tree(temp, {"_info.ini": b"new!", "vessels/b.ini": b"b", "vessels/a.ini": b"a",
                                    "a.txt": b"t"}, stale)
            said = []
            self.assertFalse(self.tool.refresh(root, check=True, out=said.append))
            self.assertEqual(json.loads((root / self.tool.MANIFEST).read_text(encoding="utf-8")), stale)  # --check writes nothing
            self.assertIn("lists 2 file(s)", said[0])
            self.assertIn("holds 4 (3 not listed, 1 listed and gone, 1 changed)", said[0])
            self.assertFalse(self.tool.refresh(root, out=said.append))
            text = (root / self.tool.MANIFEST).read_text(encoding="utf-8")
            written = json.loads(text)
            # One line, compact, a trailing newline: the form the PC scripts have always been given.
            self.assertEqual(text, json.dumps(written, separators=(",", ":")) + "\n")
            self.assertEqual({k: v for k, v in written.items() if k not in ("files", "file_count")},
                             {"format": 1, "release_revision": "R12", "ribbons": {"total": 75}})
            self.assertEqual(written["file_count"], 4)
            # Ordered by path parts, as pathlib sorts relative paths: a folder's files stay together.
            self.assertEqual([e["path"] for e in written["files"]],
                             ["_info.ini", "a.txt", "vessels/a.ini", "vessels/b.ini"])
            self.assertEqual(written["files"][0], {"path": "_info.ini", "bytes": 4,
                                                   "sha256": hashlib.sha256(b"new!").hexdigest()})
            self.assertTrue(self.tool.refresh(root, check=True, out=said.append))
            self.assertTrue(self.tool.refresh(root, out=said.append))        # nothing to rewrite

    def test_an_empty_pack_is_not_written_into_the_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            root = self.tree(temp, {}, {"file_count": 1, "files": [{"path": "a", "bytes": 1, "sha256": "0"}]})
            (root / self.tool.DIST).mkdir(parents=True, exist_ok=True)
            with self.assertRaises(SystemExit):
                self.tool.refresh(root, out=lambda line: None)

    def test_the_committed_manifest_lists_the_built_pack(self):
        # What the owner's PC holds the upload to (tools/prepare-workshop-upload.ps1,
        # tools/install-workshop-release-data.ps1): a rebuild that is not followed by
        # tools/refresh_upload_manifest.py leaves a release the PC refuses.
        manifest = json.loads((ROOT / self.tool.MANIFEST).read_text(encoding="utf-8"))
        files = self.tool.listing(ROOT / self.tool.DIST)
        if not files:
            self.skipTest("pack not built")
        added, removed, changed = self.tool.compare(manifest, files)
        self.assertEqual((added[:5], removed[:5], changed[:5]), ([], [], []),
                         "run python3 tools/refresh_upload_manifest.py after the rebuild")
        self.assertEqual(manifest["file_count"], len(files))


if __name__ == "__main__":
    unittest.main()
