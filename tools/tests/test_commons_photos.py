"""integration/gallery/commons_photos.py: a reviewed Commons photo goes into the
gallery with its credit, becomes the unit's encyclopedia picture, and the
gallery builder notices a sheet that has not been applied."""
import csv
import hashlib
import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
GALLERY = ROOT / "integration" / "gallery"


def load():
    spec = importlib.util.spec_from_file_location("commons_photos", GALLERY / "commons_photos.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class CommonsPhotos(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.cp = load()
        # a private copy of the gallery files the importer writes
        src = self.tmp / "source"
        (src / "data").mkdir(parents=True)
        for rel in ("catalogue.js", "PHOTO_CREDITS.txt", "data/unit_image_mapping.csv"):
            shutil.copyfile(GALLERY / "source" / rel, src / rel)
        shutil.copyfile(GALLERY / "profiles.tsv", self.tmp / "profiles.tsv")
        self.cp.SOURCE, self.cp.STORE = src, self.tmp / "commons"
        self.cp.SHEET, self.cp.PROFILES = self.tmp / "commons-photos.csv", self.tmp / "profiles.tsv"
        # a kit run: one downloaded photo and its record
        kit = self.tmp / "kit"
        (kit / "downloaded" / "verified_file_pages").mkdir(parents=True)
        photo = kit / "downloaded" / "verified_file_pages" / "topolm.jpg"
        Image.new("RGB", (1200, 800), (90, 110, 70)).save(photo, "JPEG")
        self.kit, self.digest = kit, hashlib.sha256(photo.read_bytes()).hexdigest()
        fields = ["asset_group", "unit_ids", "unit_labels", "local_file", "author", "licence",
                  "licence_url", "source_page", "source_file_title", "direct_url",
                  "downloaded_url", "width", "height", "sha256", "changes", "date_checked"]
        with (kit / "ACQUIRED_IMAGES.csv").open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerow({"asset_group": "topolm", "unit_ids": "wp_ss-27_tel",
                        "unit_labels": "Topol-M mobile TEL",
                        "local_file": "downloaded/verified_file_pages/topolm.jpg",
                        "author": "Vitaly V. Kuzmin", "licence": "CC0", "licence_url": "",
                        "source_page": "https://commons.wikimedia.org/wiki/File:Topol-M-09-05-2011.jpg",
                        "source_file_title": "File:Topol-M-09-05-2011.jpg", "direct_url": "",
                        "downloaded_url": "", "width": "3072", "height": "2304",
                        "sha256": self.digest, "changes": "resized by Wikimedia Commons thumbnail service",
                        "date_checked": "2026-10-15"})
        self.review = self.tmp / "review.csv"

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write_review(self, decision="approve", verdict="same_type"):
        self.review.write_text("asset_group,decision,verdict,category,note\n"
                               f"topolm,{decision},{verdict},,\n", encoding="utf-8")

    def test_an_approved_photo_is_taken_in_applied_and_pictured(self):
        self.write_review()
        self.cp.intake(self.kit, self.review)
        (row,) = self.cp.sheet()
        self.assertEqual((row["asset_id"], row["category"], row["unit_ids"]),
                         ("topolm", "Land units", "wp_ss-27_tel"))
        self.cp.apply()
        cat = self.cp.load_catalogue()
        a = next(x for x in cat["assets"] if x["asset_id"] == "topolm")
        self.assertEqual(a["file"], "images/land/topolm_commons.jpg")
        self.assertEqual((a["license"], a["origin"]), ("CC0", "wikimedia_commons_reviewed"))
        self.assertTrue((self.cp.SOURCE / a["file"]).is_file())
        self.assertIn("topolm — Topol-M mobile TEL\nCreator: Vitaly V. Kuzmin",
                      (self.cp.SOURCE / "PHOTO_CREDITS.txt").read_text(encoding="utf-8"))
        self.assertIn("wp_ss-27_tel\ttopolm\tsame_type", self.cp.PROFILES.read_text(encoding="utf-8"))
        self.assertEqual(self.cp.stale(cat), [])
        self.cp.apply()                                   # a second run changes nothing
        self.assertEqual(self.cp.PROFILES.read_text(encoding="utf-8").count("wp_ss-27_tel\t"), 1)

    def test_a_rejected_photo_is_not_taken_in(self):
        self.write_review(decision="reject")
        self.cp.intake(self.kit, self.review)
        self.assertEqual(self.cp.sheet(), [])

    def test_a_context_photo_makes_no_encyclopedia_picture(self):
        self.write_review(verdict="context")
        self.cp.intake(self.kit, self.review)
        self.cp.apply()
        self.assertNotIn("wp_ss-27_tel\ttopolm", self.cp.PROFILES.read_text(encoding="utf-8"))

    def test_changed_bytes_are_refused(self):
        self.write_review()
        (self.kit / "downloaded" / "verified_file_pages" / "topolm.jpg").write_bytes(b"\xff\xd8 not it")
        with self.assertRaises(SystemExit):
            self.cp.intake(self.kit, self.review)

    def test_the_builder_notices_an_unapplied_sheet(self):
        self.write_review()
        self.cp.intake(self.kit, self.review)
        self.assertEqual(self.cp.stale(self.cp.load_catalogue()), ["topolm"])


if __name__ == "__main__":
    unittest.main()
