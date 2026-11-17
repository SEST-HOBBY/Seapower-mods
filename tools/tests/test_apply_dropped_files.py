#!/usr/bin/env python3
"""tools/apply_dropped_files.py: the export loses the files the game dropped, and only then.

    python3 -m unittest discover -s tools/tests -p 'test_apply_dropped_files.py' -v
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASE = "11-Nov-2026: 0.9.0 Build 261111 Public Release"
NEXT = "13-Nov-2026: 0.9.2 Build 261113 Public Release"


def tool():
    spec = importlib.util.spec_from_file_location("apply_dropped_files", ROOT / "tools/apply_dropped_files.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def listing(installed, paths, export=RELEASE):
    return ("# Files in mods-source\\_vanilla\\original that the installed game no longer ships.\n"
            f"# export   : {export}\n# installed: {installed}\n\n"
            f"compared: 3 file(s) of the export\nno longer shipped ({len(paths)}):\n"
            + "".join(f"  {p}\n" for p in paths))


class Apply(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tool = tool()

    def tree(self, temp, export_build, listed):
        root = Path(temp)
        original = root / self.tool.EXPORT / "original"
        (original / "missions" / "NATO").mkdir(parents=True)
        for rel in ("kept.ini", "dropped.ini", "missions/NATO/Don't Mess With Texas (Blue Side).ini"):
            (original / rel).write_text("x", encoding="utf-8")
        (root / self.tool.EXPORT / "changelog.txt").write_text(f"Change log\n\n{export_build}\n[FIX] x\n", encoding="utf-8")
        if listed is not None:
            (root / self.tool.LIST).parent.mkdir(parents=True)
            (root / self.tool.LIST).write_text(listed, encoding="utf-8")
        return root, original

    def test_the_listed_files_go_once_the_export_holds_that_build(self):
        gone = ["dropped.ini", "missions/NATO/Don't Mess With Texas (Blue Side).ini", "already/gone.ini"]
        with tempfile.TemporaryDirectory() as temp:
            root, original = self.tree(temp, NEXT, listing(NEXT, gone))
            said = []
            self.assertEqual(self.tool.apply(root, check=True, out=said.append), 1)       # two would go
            self.assertTrue((original / "dropped.ini").is_file())                         # --check removes nothing
            self.assertIn("3 listed, 2 still in", said[0])
            self.assertEqual(self.tool.apply(root, out=said.append), 0)
            self.assertFalse((original / "dropped.ini").exists())
            self.assertFalse((original / "missions/NATO/Don't Mess With Texas (Blue Side).ini").exists())
            self.assertTrue((original / "kept.ini").is_file())
            self.assertEqual(self.tool.apply(root, check=True, out=said.append), 0)       # nothing left to remove

    def test_a_list_taken_against_another_build_removes_nothing(self):
        # The capture ran with 0.9.2 installed and the export is still 0.9.0 (or the
        # PC is on a beta): the list is the newer game's, and the export keeps its files.
        with tempfile.TemporaryDirectory() as temp:
            root, original = self.tree(temp, RELEASE, listing(NEXT, ["dropped.ini"]))
            said = []
            self.assertEqual(self.tool.apply(root, out=said.append), 1)
            self.assertTrue((original / "dropped.ini").is_file())
            self.assertIn("for another game than the export", said[-1])

    def test_a_path_outside_the_export_is_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root, original = self.tree(temp, NEXT, listing(NEXT, ["../changelog.txt", "dropped.ini"]))
            self.assertEqual(self.tool.apply(root, out=lambda line: None), 1)
            self.assertTrue((root / self.tool.EXPORT / "changelog.txt").is_file())
            self.assertTrue((original / "dropped.ini").is_file())

    def test_a_capture_that_could_not_compare_or_wrote_no_list_says_so(self):
        with tempfile.TemporaryDirectory() as temp:
            root, original = self.tree(temp, NEXT, "# header\n# export   : x\n# installed: y\n\nnot compared: the install was not found\n")
            said = []
            self.assertEqual(self.tool.apply(root, out=said.append), 1)
            self.assertIn("not compared", said[0])
        with tempfile.TemporaryDirectory() as temp:
            root, original = self.tree(temp, NEXT, None)
            said = []
            self.assertEqual(self.tool.apply(root, out=said.append), 1)
            self.assertIn("is not there", said[0])
            self.assertTrue((original / "dropped.ini").is_file())


if __name__ == "__main__":
    unittest.main()
