#!/usr/bin/env python3
"""Prove every SEST pack declares the installed game's version, and list the
Workshop mods the game will mark incompatible.

The Mod Manager reads [Compatibility] from each mod's _info.ini. Its
ApproximateVersion check needs MAJOR and MINOR to match the game's and accepts
a higher PATCH (the stock comment on that key in the Workshop files, and
commit 673e50b as quoted in docs/interoperability-report.md), so a pack one
minor version behind is shown to the player as out of date; a mod whose
GreaterThanEqualToVersion / LessThanVersion range leaves the game out is
flagged incompatible. Every SEST pack's version is a literal in its builder,
so correcting the built _info.ini alone is undone by the next build; this
reads both, and it exists because nothing else noticed the literals going
stale when the game moved on.

The game's version is the first "dd-Mon-yyyy: X.Y.Z Build #N" line of
data/install-snapshot/changelog.live.txt (written by tools/capture-context.ps1).
Without that snapshot it reads mods-source/_vanilla/changelog.txt and says so.
--version X.Y.Z overrides both, to see what a game update would do.

Four checks; each finding is a FAIL line and the run exits 1:
  1. every integration/*/SEST_*/_info.ini (dist excluded) and
     integration/dist/SEST_Integration/_info.ini declares ApproximateVersion
     equal to the game's X.Y.Z, and every builder that writes _info.ini has a
     built SEST_* folder to check (build_all.py --from-scratch deletes them
     before it builds, so a failed build leaves none);
  2. every ApproximateVersion= literal in the pack builders
     (integration/*/build_*.py, found by what they write rather than by
     whether their output exists) and tools/consolidate_packs.py equals it,
     and every builder that writes _info.ini carries one;
  3. no Workshop mod in data/load-order.tokens.txt declares a version range
     that excludes the game;
  4. mods-source/_vanilla/changelog.txt is not from a newer game than the
     snapshot's changelog, which would mean the export landed and the
     snapshot did not.
Workshop ApproximateVersion values are counted by how far they sit from the
game's, numerically per component, and the mods more than one minor version
behind are listed as information.

    python3 tools/check_game_version.py                  # read-only
    python3 tools/check_game_version.py --version 0.9.0  # a game update, rehearsed
    python3 tools/check_game_version.py --bump 0.9.0     # rewrite the literals

--bump rewrites the ApproximateVersion literal in every builder and in every
static _info.ini (one whose pack has no builder writing _info.ini), prints each
file it changes, touches nothing else and is idempotent; it exits 1 when a
file needs a [Compatibility] section by hand. The builder-written _info.ini
files stay stale until python3 tools/build_all.py --from-scratch regenerates
them, so run that and then this check again.
"""
import argparse
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE_CHANGELOG = "data/install-snapshot/changelog.live.txt"
VANILLA_CHANGELOG = "mods-source/_vanilla/changelog.txt"
LOAD_ORDER = "data/load-order.tokens.txt"
CONSOLIDATOR = "tools/consolidate_packs.py"
REBUILD = "run python3 tools/build_all.py --from-scratch"

# Every day in the changelog so far is zero-padded; a "2-Oct-2026" line must
# still be read as the newest, not skipped for the one below it.
# "20-Jul-2026: 0.8.2 Build #358 (23444) Public Release" until Sep 2026;
# "01-Oct-2026: 0.8.3 Build 261001 Public Release" and "Build 260928b" since.
BUILD_LINE = re.compile(r"^(\d{1,2}-[A-Za-z]{3}-\d{4}):\s+(\d+(?:\.\d+)+)\s+Build\s+#?(\w+)", re.M)
# A version written out in full. consolidate_packs.py's "{version}" template
# and its own regex over the component packs do not match, by design.
LITERAL = re.compile(r"(ApproximateVersion=)(\d+(?:\.\d+)+)")
TEMPLATE = re.compile(r"ApproximateVersion=\{")
# (OUT / "_info.ini").write_text(...) or a helper such as write("_info.ini", ...)
# in a builder: the pack's manifest is generated, so the committed copy is not
# the place to edit it.
WRITES_INFO = re.compile(r"""["']_info\.ini["']\s*\)\s*\.write_(?:text|bytes)\(|\bwrite\w*\(\s*["']_info\.ini["']""")

FAR_BEHIND = "more than one minor behind"
KINDS = ["match", "behind in patch only", "one minor behind", FAR_BEHIND,
         "newer than the game", "range only", "undeclared", "unreadable"]


def parse_version(text):
    """'0.8.2' -> (0, 8, 2); None when any component is not a number."""
    parts = text.strip().split(".")
    if not all(p.isascii() and p.isdigit() for p in parts):
        return None
    return tuple(int(p) for p in parts)


def classify(declared, game):
    """How a declared ApproximateVersion sits against the game's, numerically."""
    if declared == game:
        return "match"
    if declared > game:
        return "newer than the game"
    major, minor = declared[0], declared[1] if len(declared) > 1 else 0
    game_major, game_minor = game[0], game[1] if len(game) > 1 else 0
    if (major, minor) == (game_major, game_minor):
        return "behind in patch only"
    if major == game_major and game_minor - minor == 1:
        return "one minor behind"
    return FAR_BEHIND


def build_line(path):
    """-> (version, date, build) from the first 'dd-Mon-yyyy: X.Y.Z Build #N' line of <path>; None without one."""
    if not path.exists():
        return None
    match = BUILD_LINE.search(path.read_text(encoding="utf-8-sig", errors="replace"))
    return (match.group(2), match.group(1), match.group(3)) if match else None


def read_game_version(root, override=None):
    """-> (version, where it came from). Raises ValueError when no changelog has a build line."""
    found = None
    for rel in (LIVE_CHANGELOG, VANILLA_CHANGELOG):
        line = build_line(root / rel)
        if line:
            version, date, build = line
            source = f"Build #{build} ({date}) from {rel}"
            if rel != LIVE_CHANGELOG:
                source += (f" - FALLBACK, {LIVE_CHANGELOG} is missing or has no build line; "
                           "run tools/capture-context.ps1")
            found = (version, source)
            break
    if override:
        override = override.strip()
        if parse_version(override) is None:
            raise ValueError(f"--version {override!r} is not numeric X.Y.Z")
        note = f" (changelog says {found[0]})" if found and found[0] != override else ""
        return override, "from --version" + note
    if found is None:
        raise ValueError(f"no 'dd-Mon-yyyy: X.Y.Z Build #N' line in {LIVE_CHANGELOG} or {VANILLA_CHANGELOG}")
    return found


def read_ini(path):
    """-> {section: {key: value}}, section and key names casefolded; comments, BOM and CRLF dropped."""
    sections, current = {}, ""
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith((";", "#")):
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            current = stripped[1:-1].strip().casefold()
            sections.setdefault(current, {})
            continue
        if "=" in stripped:
            key, _, value = stripped.partition("=")
            sections.setdefault(current, {})[key.strip().casefold()] = value.strip()
    return sections


def mod_name(sections, fallback):
    name = sections.get("language_en", {}).get("name")
    if name:
        return name
    for keys in sections.values():
        if keys.get("name"):
            return keys["name"]
    return fallback


def sest_packs(root):
    """The per-pack build outputs, then the consolidated pack when it has been built."""
    packs = sorted(p for p in (root / "integration").glob("*/SEST_*")
                   if p.is_dir() and p.parent.name != "dist")
    dist = root / "integration" / "dist" / "SEST_Integration"
    if dist.is_dir():
        packs.append(dist)
    return packs


def pack_builders(root, pack):
    """The scripts that generate <pack>: its folder's build_*.py, or the consolidator for dist."""
    if pack.parent.name == "dist":
        consolidator = root / CONSOLIDATOR
        return [consolidator] if consolidator.exists() else []
    return sorted(pack.parent.glob("build_*.py"))


def writes_info(builder):
    return bool(WRITES_INFO.search(builder.read_text(encoding="utf-8", errors="replace")))


def literals(path):
    """-> [(line number, value)] for every ApproximateVersion=X.Y.Z written out in <path>."""
    text = path.read_text(encoding="utf-8", errors="replace")
    return [(text.count("\n", 0, m.start()) + 1, m.group(2)) for m in LITERAL.finditer(text)]


def all_builders(root):
    """Every integration/*/build_*.py that writes _info.ini or carries a literal, then the consolidator.

    Found by what the script does, not by whether its SEST_* output exists:
    build_all.py --from-scratch deletes the outputs first, and a stale literal
    must not hide behind a build that failed.
    """
    found = [b for b in sorted((root / "integration").glob("*/build_*.py"))
             if writes_info(b) or literals(b)]
    consolidator = root / CONSOLIDATOR
    if consolidator.exists():
        found.append(consolidator)
    return found


def is_static(root, pack):
    """True when no builder regenerates this pack's _info.ini, so the committed file is the source."""
    return not any(writes_info(b) for b in pack_builders(root, pack))


def load_order_ids(root):
    path = root / LOAD_ORDER
    tokens = [s.strip() for s in path.read_text(encoding="utf-8-sig").splitlines()
              if s.strip() and not s.lstrip().startswith("#")]
    return [t for t in tokens if t.isascii() and t.isdigit()]


def audit(root, version):
    """-> (lines, problems, found): the report body, the FAIL findings, and how many per check."""
    game = parse_version(version)
    if game is None:
        raise ValueError(f"game version {version!r} is not numeric X.Y.Z")
    lines, problems, found = [], [], Counter()

    def rel(path):
        return path.relative_to(root).as_posix()

    def fail(check, text):
        problems.append(text)
        found[check] += 1

    # 1. What each built pack tells the Mod Manager.
    packs = sest_packs(root)
    builders = all_builders(root)
    static = [p / "_info.ini" for p in packs if is_static(root, p)]
    lines.append(f"SEST packs: {len(packs)} (integration/*/SEST_* and dist/SEST_Integration)")
    if not packs:
        fail("packs", f"no SEST pack found under {rel(root / 'integration')} (wrong --root, or nothing built)")
    for pack in packs:
        info = pack / "_info.ini"
        if not info.exists():
            fail("packs", f"{rel(pack)} has no _info.ini")
            continue
        declared = read_ini(info).get("compatibility", {}).get("approximateversion")
        tag = " (static: no builder writes it)" if info in static else ""
        if declared is None:
            fail("packs", f"{rel(info)} declares no [Compatibility] ApproximateVersion{tag}")
        elif parse_version(declared) != game:
            fail("packs", f"{rel(info)} declares {declared}, game is {version}{tag}")
        else:
            lines.append(f"  {rel(info)}  {declared}{tag}")
    consolidator = root / CONSOLIDATOR
    for builder in builders:
        if builder == consolidator:
            if not (root / "integration" / "dist" / "SEST_Integration").is_dir():
                fail("packs", f"integration/dist/SEST_Integration has not been built; {REBUILD}")
        elif writes_info(builder) and not any(p.is_dir() for p in builder.parent.glob("SEST_*")):
            fail("packs", f"{rel(builder.parent)} has no built SEST_* folder for {builder.name} to write; {REBUILD}")

    # 2. Where the builders get it from. A fix to the built file alone does not survive a rebuild.
    lines.append(f"Builders: {len(builders)} scanned for ApproximateVersion= literals")
    for builder in builders:
        hits = literals(builder)
        for line_no, value in hits:
            if parse_version(value) != game:
                fail("builders", f"{rel(builder)}:{line_no} writes ApproximateVersion={value}, game is {version}")
            else:
                lines.append(f"  {rel(builder)}:{line_no}  ApproximateVersion={value}")
        if hits or not writes_info(builder):
            continue
        if TEMPLATE.search(builder.read_text(encoding="utf-8", errors="replace")):
            lines.append(f"  {rel(builder)}  computes ApproximateVersion at build time, no literal")
        else:
            fail("builders", f"{rel(builder)} writes _info.ini with no ApproximateVersion literal")
    lines.append("Static _info.ini (edited by hand, not generated): "
                 + (", ".join(rel(p) for p in static) if static else "none"))

    # 3. The Workshop mods, as the Mod Manager will judge them against this game.
    ids = load_order_ids(root)
    counts, far_behind, unread, ranges, admitted = Counter(), [], [], 0, 0
    for wid in ids:
        info = root / "mods-source" / wid / "_info.ini"
        if not info.exists():
            unread.append(wid)
            continue
        sections = read_ini(info)
        compat = sections.get("compatibility", {})
        name = mod_name(sections, wid)
        low, high = compat.get("greaterthanequaltoversion"), compat.get("lessthanversion")
        if low or high:
            ranges += 1
            text = (f"{low} <= v < {high}" if low and high
                    else f"{low} <= v" if low else f"v < {high}")
            low_v = parse_version(low) if low else None
            high_v = parse_version(high) if high else None
            if (low and low_v is None) or (high and high_v is None):
                fail("workshop", f"{wid} {name} declares an unreadable range: {text}")
            elif (low_v is not None and game < low_v) or (high_v is not None and game >= high_v):
                fail("workshop", f"{wid} {name} declares {text}, which excludes {version}")
            else:
                admitted += 1
        approx = compat.get("approximateversion")
        if approx is None:
            counts["range only" if (low or high) else "undeclared"] += 1
            continue
        declared = parse_version(approx)
        if declared is None:
            counts["unreadable"] += 1
            lines.append(f"  {wid} {name} declares ApproximateVersion={approx!r}, which is not numeric")
            continue
        kind = classify(declared, game)
        counts[kind] += 1
        if kind == FAR_BEHIND:
            far_behind.append((declared, wid, name, approx))
    lines.append(f"Workshop mods in load order: {len(ids)}; {len(ids) - len(unread)} _info.ini read"
                 + (f"; {len(unread)} unreadable (not exported or no _info.ini): {', '.join(unread)}"
                    if unread else ""))
    lines.append(f"  ApproximateVersion vs {version}: "
                 + ", ".join(f"{counts[k]} {k}" for k in KINDS if counts[k]))
    lines.append(f"  Version ranges: {ranges} declared, {admitted} admit {version}")
    below_minor = counts["one minor behind"] + counts[FAR_BEHIND]
    game_minor = ".".join(str(c) for c in game[:2])
    lines.append(f"INFO: {below_minor} mod(s) declare a minor version below {game_minor}, which the Mod Manager "
                 f"shows as out of date (MAJOR and MINOR must match); the {len(far_behind)} more than one minor "
                 "behind:")
    for declared, wid, name, approx in sorted(far_behind):
        lines.append(f"  {approx:<8}{wid}  {name}")

    # 4. The export and the snapshot come from the same game, or the game version above is stale.
    live, export = build_line(root / LIVE_CHANGELOG), build_line(root / VANILLA_CHANGELOG)
    if live and export and parse_version(export[0]) > parse_version(live[0]):
        fail("snapshot", f"{VANILLA_CHANGELOG} is from {export[0]} Build #{export[2]} but {LIVE_CHANGELOG} "
                         f"says {live[0]}: the export is newer than the snapshot; run tools/capture-context.ps1")
    return lines, problems, found


def bump(root, version):
    """Rewrite every ApproximateVersion literal in the builders and the static _info.ini files.

    -> (changed, left): [(path, old values)] rewritten, and the files with no
    literal to rewrite (a builder that writes _info.ini, or a static _info.ini),
    which need a [Compatibility] section by hand. Nothing else is touched; a
    second run with the same version changes nothing.
    """
    version = version.strip()
    if parse_version(version) is None:
        raise ValueError(f"--bump {version!r} is not numeric X.Y.Z")
    targets = all_builders(root)
    for pack in sest_packs(root):
        if is_static(root, pack) and (pack / "_info.ini").exists():
            targets.append(pack / "_info.ini")
    changed, left = [], []
    for path in dict.fromkeys(targets):
        text = path.read_bytes().decode("utf-8")   # a BOM or CRLF survives the round trip
        old = sorted({m.group(2) for m in LITERAL.finditer(text)})
        if not old:
            if path.suffix == ".ini" or (writes_info(path) and not TEMPLATE.search(text)):
                left.append(path)
            continue
        new = LITERAL.sub(lambda m: m.group(1) + version, text)
        if new != text:
            path.write_bytes(new.encode("utf-8"))
            changed.append((path, old))
    return changed, left


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--version", metavar="X.Y.Z",
                        help="treat this as the installed game's version instead of reading the changelog")
    parser.add_argument("--bump", metavar="X.Y.Z",
                        help="rewrite the ApproximateVersion literals in the builders and static _info.ini files "
                             "(the only way this tool writes; --version is ignored with it)")
    args = parser.parse_args(argv)
    root = args.root.resolve()

    if args.bump:
        target = args.bump.strip()
        try:
            changed, left = bump(root, target)
        except (OSError, ValueError, UnicodeDecodeError) as exc:
            raise SystemExit(f"Game version bump could not read its inputs: {exc}")
        for path, old in changed:
            print(f"bump: {path.relative_to(root).as_posix()}  {', '.join(old)} -> {target}")
        for path in left:
            print(f"left alone: {path.relative_to(root).as_posix()} has no ApproximateVersion literal; "
                  "add a [Compatibility] section by hand")
        try:
            current = read_game_version(root)[0]
        except (OSError, ValueError):
            current = None
        if current and current != target:
            print(f"note: the changelog still reads {current}; re-export and run tools/capture-context.ps1 "
                  "once the game has updated")
        print(f"Bump to {target}: {len(changed)} file(s) rewritten, {len(left)} left for a hand edit; "
              "rebuild (python3 tools/build_all.py --from-scratch), then run this check")
        return bool(left)

    try:
        version, source = read_game_version(root, args.version)
        lines, problems, found = audit(root, version)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Game version check could not read its inputs: {exc}")
    print(f"Game version: {version} {source}")
    for line in lines:
        print(line)
    for problem in problems:
        print(f"FAIL: {problem}")
    print(f"Game version check: {'FAILED' if problems else 'PASS'} "
          f"({found['packs']} pack(s), {found['builders']} builder(s), "
          f"{found['workshop']} Workshop exclusion(s) against {version}"
          + ("; the snapshot lags the export" if found["snapshot"] else "") + ")")
    return bool(problems)


if __name__ == "__main__":
    raise SystemExit(main())
