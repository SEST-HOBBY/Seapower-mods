"""integration/media-pack/build_media.py on stand-in photographs: the sizes it
makes and refuses, the portrait panel, the menu darkening, and the records."""
import csv
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("build_media", ROOT / "integration/media-pack/build_media.py")
bm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bm)


def source(id_, kind="still", uses=("loading",), lic="LicenseRef-PD-USGov", focus=(0.5, 0.5)):
    return {"id": id_, "priority": "P1", "kind": kind, "category": "isr", "title": f"{id_}.jpg",
            "page": f"https://commons.wikimedia.org/wiki/File:{id_}.jpg", "creator": "U.S. Navy",
            "license": lic, "uses": list(uses), "stage": "ship" if kind == "still" else "deferred",
            "focus": list(focus), "note": ""}


def pixel(path, xy):
    """The colour at `xy`, or the image size when `xy` is None."""
    from PIL import Image
    with Image.open(path) as im:
        return im.size if xy is None else im.getpixel(xy)


class BuildMediaTest(unittest.TestCase):
    def setUp(self):
        from PIL import Image
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        shapes = {"big": (4500, 3000), "portrait": (2252, 2976), "wide": (6003, 2095),
                  "small": (2100, 1500), "tampered": (4000, 2250)}
        files = []
        for id_, size in shapes.items():
            p = self.root / "source/images/isr" / f"{id_}.jpg"
            p.parent.mkdir(parents=True, exist_ok=True)
            Image.new("RGB", size, (200, 180, 160)).save(p, "JPEG")
            digest = hashlib.sha256(p.read_bytes()).hexdigest()
            files.append({"id": id_, "file": f"source/images/isr/{id_}.jpg", "page": "", "license": "Public domain",
                          "license_url": "", "artist": "Petty Officer Example", "original_width": size[0],
                          "original_height": size[1], "sha256": digest if id_ != "tampered" else "0" * 64,
                          "retrieved_at": "2026-10-10T00:00:00Z"})
        sources = [source("big", uses=("loading", "menu")), source("portrait", focus=(0.8, 0.5)),
                   source("wide", lic="CC0-1.0"), source("small"), source("tampered"), source("refused"),
                   source("missing"), source("loop", kind="video", lic="CC-BY-3.0", uses=("menu-video",))]
        (self.root / "sources.json").write_text(json.dumps({
            "allowed_licenses": {}, "rejected": [{"title": "Virginia_class_submarine.jpg", "reason": "metadata"}],
            "sources": sources}), encoding="utf-8")
        (self.root / "source/fetched.json").write_text(json.dumps({
            "files": files, "refused": [{"id": "refused", "reason": "file page licence 'CC BY-NC 2.0'"}]}),
            encoding="utf-8-sig")
        self.out = self.root / "game_ready"
        self.rows = {r["id"]: r for r in bm.build(self.root, self.out, quiet=True)}

    def tearDown(self):
        self.tmp.cleanup()

    def sizes(self, kind, id_):
        return {p.parent.name: pixel(p, None) for p in sorted(self.out.glob(f"{kind}/*/{id_}.jpg"))}

    def test_a_large_master_gives_every_size(self):
        self.assertEqual(self.sizes("loading", "big"),
                         {"1080p": (1920, 1080), "1440p": (2560, 1440), "2160p": (3840, 2160)})

    def test_no_size_is_upscaled(self):
        self.assertEqual(set(self.sizes("loading", "small")), {"1080p"})      # 2100 px wide
        self.assertEqual(set(self.sizes("loading", "wide")), {"1080p", "1440p"})  # 2095 tall -> 3724 wide

    def test_a_portrait_sits_on_a_dark_panel_at_full_height(self):
        f = self.out / "loading/1080p/portrait.jpg"
        self.assertEqual(pixel(f, None), (1920, 1080))
        left = pixel(f, (20, 540))
        self.assertTrue(all(abs(a - b) <= 4 for a, b in zip(left, bm.SOLID)), left)   # the panel
        self.assertGreater(sum(pixel(f, (1600, 540))), 450)                            # the photograph, right

    def test_menu_versions_are_darker_and_only_for_menu_sources(self):
        lit = pixel(self.out / "loading/1080p/big.jpg", (960, 540))
        dim = pixel(self.out / "menu/static/1080p/big.jpg", (960, 540))
        self.assertLess(sum(dim), sum(lit) * 0.75)
        self.assertEqual(self.sizes("menu/static", "small"), {})

    def test_the_solid_fallback_is_written_at_every_size(self):
        for label in bm.SIZES:
            self.assertTrue((self.out / f"menu/fallback/solid/solid_0b1115_{label}.png").is_file())

    def test_statuses(self):
        self.assertEqual(self.rows["big"]["status"], "ready")
        self.assertTrue(self.rows["tampered"]["status"].startswith("sha256 mismatch"))
        self.assertTrue(self.rows["refused"]["status"].startswith("refused: file page licence"))
        self.assertTrue(self.rows["missing"]["status"].startswith("awaiting download"))
        self.assertTrue(self.rows["loop"]["status"].startswith("deferred"))
        self.assertEqual(self.rows["loop"]["attribution_required"], "true")
        self.assertFalse(list(self.out.glob("*/*/tampered.jpg")))

    def test_the_manifest_and_credits(self):
        with open(self.root / "media_manifest.csv", encoding="utf-8") as fh:
            ids = [r["id"] for r in csv.DictReader(fh)]
        self.assertEqual(ids, ["big", "portrait", "wide", "small", "tampered", "refused", "missing", "loop"])
        text = (self.root / "ATTRIBUTION.md").read_text(encoding="utf-8")
        self.assertIn("- Creator: Petty Officer Example", text)
        self.assertIn("Creative Commons Zero v1.0", text)
        self.assertIn("CC BY 3.0 - attribution required", text)
        self.assertIn("Virginia_class_submarine.jpg", text)
        self.assertNotIn("## tampered", text)


if __name__ == "__main__":
    unittest.main()
