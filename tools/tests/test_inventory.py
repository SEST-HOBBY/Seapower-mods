"""Regression cases for drift that aggregate mod counts alone cannot detect."""
import csv
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_inventory import audit


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "mods-source"
        (self.source / "100").mkdir(parents=True)
        (self.root / "data").mkdir()
        self.content = b"Name=Example\n"
        self.file = self.source / "100/_info.ini"
        self.file.write_bytes(self.content)
        self.write_csv("_export-manifest.csv", [dict(WorkshopId="100", DisplayName="", FilesCopied=1, Bytes=len(self.content))])
        (self.root / "data/mod-catalog.json").write_text(json.dumps({"mods": [dict(workshop_id="100", status="active")]}))
        self.order = self.root / "data/load-order.tokens.txt"
        self.order.write_text("SEST_Integration\n100\n")

    def write_csv(self, name, rows):
        with (self.source / name).open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def test_blank_display_name_is_still_counted(self):
        counts, problems, hashes = audit(self.root)
        self.assertEqual(counts, dict(manifest=1, folders=1, catalog=1, order=1))
        self.assertEqual(problems, [])
        self.assertFalse(hashes)

    def test_equal_counts_with_different_ids_fail(self):
        self.order.write_text("SEST_Integration\n200\n")
        self.assertTrue(any("order: missing=['100']; extra=['200']" in p for p in audit(self.root)[1]))

    def test_overlay_export_retains_an_obsolete_file(self):
        (self.source / "100/deleted-upstream.ini").write_bytes(b"old config")
        self.assertTrue(any("disk 2 files" in p for p in audit(self.root)[1]))

    def test_duplicate_order_and_manifest_are_rejected(self):
        self.order.write_text("SEST_Integration\n100\n100\n")
        row = dict(WorkshopId="100", DisplayName="", FilesCopied=1, Bytes=len(self.content))
        self.write_csv("_export-manifest.csv", [row, row])
        problems = audit(self.root)[1]
        self.assertTrue(any("order: duplicate IDs 100" in p for p in problems))
        self.assertTrue(any("manifest: duplicate IDs 100" in p for p in problems))

    def test_hash_detects_equal_size_content_change(self):
        self.write_csv("_export-files.csv", [dict(WorkshopId="100", RelativePath="_info.ini", Bytes=len(self.content), SHA256=hashlib.sha256(self.content).hexdigest())])
        self.assertEqual(audit(self.root)[1], [])
        self.file.write_bytes(b"Name=Changed\n")
        self.assertTrue(any("content mismatch" in p for p in audit(self.root)[1]))

    def test_case_collisions_are_not_hidden_on_linux(self):
        (self.source / "100/_INFO.ini").write_bytes(self.content)
        self.assertTrue(any("Windows path collision" in p for p in audit(self.root)[1]))

    def test_file_manifest_cannot_escape_its_mod(self):
        self.write_csv("_export-files.csv", [dict(WorkshopId="100", RelativePath="../data/x.ini", Bytes=0, SHA256="")])
        self.assertTrue(any("Unsafe file-manifest path" in p for p in audit(self.root)[1]))


if __name__ == "__main__":
    unittest.main()
