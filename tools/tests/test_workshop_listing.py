"""docs/campaigns/southern-watch/workshop-listing.md, the paste-ready Steam
text: every block is Steam BBCode with one line per paragraph or list item,
its tags balanced, and under Steam's 8,000 characters. Until 23 Oct 2026 the
description and the collection description were plain text wrapped at 76
columns, and Steam, which keeps every line break, broke their sentences."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "docs/campaigns/southern-watch/workshop-listing.md"
STEAM_LIMIT = 8000
# The BBCode a Workshop description and its change notes render.
TAGS = {"h1", "h2", "h3", "b", "i", "u", "strike", "spoiler", "noparse", "hr",
        "url", "list", "olist", "*", "quote", "code", "table", "tr", "th", "td", "img"}
UNPAIRED = {"*", "hr"}
TAG = re.compile(r"\[(/?)([a-z0-9*]+)(?:=[^\]]*)?\]")


def blocks():
    """{section heading: fenced block text} for every ``` block in the listing."""
    found, heading = {}, None
    lines = LISTING.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        if lines[i].startswith("## "):
            heading = lines[i][3:].strip()
        elif lines[i].strip() == "```" and heading:
            j = lines.index("```", i + 1)
            found[heading] = "\n".join(lines[i + 1:j])
            i = j
        i += 1
    return found


class WorkshopListing(unittest.TestCase):
    def setUp(self):
        self.blocks = blocks()

    def test_every_paste_block_is_there(self):
        for name in ("Title", "Short description", "Description", "Collection description (3812390790)"):
            self.assertIn(name, self.blocks)
        self.assertTrue(any(name.startswith("Change log:") for name in self.blocks))

    def test_no_block_is_hard_wrapped(self):
        for name, text in self.blocks.items():
            lines = text.splitlines()
            for n, (line, after) in enumerate(zip(lines, lines[1:] + [""]), 1):
                with self.subTest(block=name, line=n):
                    self.assertFalse(line[:1].isspace(), f"indented line: {line!r}")
                    self.assertNotIn("•", line, "a typed bullet: use [list] and [*]")
                    # Two prose lines in a row are one paragraph wrapped: Steam
                    # would break the sentence where the line ends.
                    prose = line.strip() and not line.startswith("[")
                    self.assertFalse(prose and after.strip() and not after.startswith("["),
                                     f"wrapped paragraph at: {line!r}")

    def test_tags_are_steam_bbcode_and_balanced(self):
        for name, text in self.blocks.items():
            with self.subTest(block=name):
                stack = []
                for close, tag in TAG.findall(text):
                    self.assertIn(tag, TAGS, f"[{tag}] is not Steam BBCode")
                    if tag in UNPAIRED:
                        continue
                    if close:
                        self.assertTrue(stack and stack[-1] == tag, f"[/{tag}] closes nothing open")
                        stack.pop()
                    else:
                        stack.append(tag)
                self.assertEqual(stack, [], f"left open: {stack}")

    def test_under_steams_limit(self):
        for name, text in self.blocks.items():
            with self.subTest(block=name):
                self.assertLessEqual(len(text), STEAM_LIMIT)
        # The newest log is pasted with the one before it when that one was
        # never uploaded (the listing's own instruction).
        logs = [text for name, text in self.blocks.items() if name.startswith("Change log:")]
        self.assertLessEqual(len("\n\n".join(logs[:2])), STEAM_LIMIT)


if __name__ == "__main__":
    unittest.main()
