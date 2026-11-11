"""The nation SEST's #!extend stubs give a variant or squadron section.

SEST Collection Fixes re-registers the post-1991, Russian-built hulls to the
game's Russia key with one #!extend stub per hull on its winning
`vessels/<uid>_variants.ini` (integration/collection-fixes/build_patch.py,
RU_REREGISTER). The game applies such a stub before the file it names: an
extend's keys come first and the first value of a key wins (IniHandler.open),
so a section's Nation= is the stub's where the stub sets one, else the file's.

Anything in this repo that reads a unit's registered nation from its winning
variants or squadrons file has to read the same layer, or it disagrees with
the game: the campaign builder's pick_nation, the mission-seed pass's
registered() and the world builder's operators(). This is the one reader all
three share.

Only SEST's own packs are indexed. No exported mod ships an #!extend onto a
variants or squadrons file (the collection-fixes builder refuses to stub a
file another mod already extends), so the SEST packs are the whole layer. The
index mirrors the game's scan (IniHandler.ScanForModifierFiles): every *.ini
under a pack, every `#!extend` line before the first section header, and a
comma-separated target list.
"""
import functools
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = re.compile(r"^(vessels|land_units|aircraft)/[^/]+_(variants|squadrons)\.ini$", re.I)
DIRECTIVE = "#!extend"


def packs(root=ROOT):
    """SEST pack folders, the consolidated dist excluded (it is a copy)."""
    return [p for p in sorted((Path(root) / "integration").glob("*/SEST_*"))
            if p.is_dir() and p.parent.name != "dist"]


def targets(lines):
    """The #!extend targets named before the first section header, from an
    iterable of a file's lines."""
    out = []
    for line in lines:
        s = line.strip().lstrip("﻿")
        if s.startswith("["):
            break
        if s.startswith(DIRECTIVE):
            for t in s[len(DIRECTIVE):].split(","):
                t = t.strip().replace("\\", "/")
                if t:
                    out.append(t)
    return out


def section_nations(text):
    """{section: Nation=} for every section that declares one, comments stripped."""
    out = {}
    for m in re.finditer(r"^\[([^\]\n]+)\][^\n]*\n(.*?)(?=^\[|\Z)", text, re.M | re.S):
        n = re.search(r"^[ \t]*Nation[ \t]*=[ \t]*(.*?)[ \t]*\r?$", m.group(2), re.M)
        value = n and re.split(r"\s*(?://|#|;)", n.group(1), maxsplit=1)[0].strip()
        if value:
            out.setdefault(m.group(1).strip(), value)
    return out


@functools.lru_cache(maxsize=None)
def index(root=ROOT):
    """{lower-cased 'kind/<uid>_variants.ini' or '..._squadrons.ini':
    {section: nation}} over every SEST pack's #!extend stubs."""
    out = {}
    for pack in packs(root):
        for f in sorted(pack.rglob("*.ini")):
            with open(f, encoding="utf-8-sig", errors="replace") as fh:
                names = [t for t in targets(fh) if TARGET.match(t)]
            if not names:
                continue
            nations = section_nations(f.read_text(encoding="utf-8-sig", errors="replace"))
            for t in names:
                slot = out.setdefault(t.lower(), {})
                for section, nation in nations.items():
                    slot.setdefault(section, nation)
    return out


def _key(rel):
    return rel.replace("\\", "/").lower()


def sections(rel, root=ROOT):
    """{section: nation} the stubs set on the file at `rel` ({} for none)."""
    return dict(index(root).get(_key(rel), {}))


def nation(rel, section, root=ROOT):
    """The Nation= the stubs give `section` of the file at `rel`, or None."""
    return index(root).get(_key(rel), {}).get(section)
