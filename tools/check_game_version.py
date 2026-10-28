#!/usr/bin/env python3
"""Prove every SEST pack declares the installed game's version, and list the
Workshop mods the game will mark incompatible.

The Mod Manager reads [Compatibility] from each mod's _info.ini and lists
every mod the game does not accept as not compatible at each start-up. The
rule, read from the game's code (ModCompatibility.Matches and
SemanticVersion in Seapower-Scripts.dll, Sea Power 0.8.7), with the game's
version MAJOR.MINOR.PATCH (its pre-release part ignored):
  - an ExactVersion, if there is one, must equal it;
  - if not, an ApproximateVersion, if there is one, must be written
    MAJOR.MINOR.PATCH (SemVer 2.0; a -pre-release or +build part is ignored)
    with the game's MAJOR and MINOR and a PATCH no higher than the game's, so
    on 0.8.7 0.8.0 to 0.8.7 pass and 0.8.8, 0.9.0, 0.7.9, 0.8 and 0.8.7.1 do
    not (the stock comment on that key in the Workshop files says "checks
    MAJOR and MINOR match but will accept higher PATCH": the game's PATCH);
  - if neither, GreaterThan(EqualTo)Version, LessThan(EqualTo)Version and
    ExcludeVersions must admit it; a mod with none of these keys passes.
The ini is read as the game reads it: the first [Compatibility] section
only (the name is case-sensitive), key names in any case with the first of
a repeated key winning, lines starting with //, # or ; skipped and a value
cut off at the first ;, // or #. The pack's SETUP (step 3) marks the mods
made for an older game version compatible on the player's PC; see
integration/campaign/setup/sest-setup.ps1. Every SEST pack's version is a
literal in its builder, so correcting the built _info.ini alone is undone by
the next build; this reads both, and it exists because nothing else noticed
the literals going stale when the game moved on.

The game's version is the first "dd-Mon-yyyy: X.Y.Z Build #N" line of
data/install-snapshot/changelog.live.txt (written by tools/capture-context.ps1).
Without that snapshot it reads mods-source/_vanilla/changelog.txt and says so.
--version X.Y.Z overrides both, to see what a game update would do.

Four checks; each finding is a FAIL line and the run exits 1:
  1. every integration/*/SEST_*/_info.ini (dist excluded) and
     integration/dist/SEST_Integration/_info.ini declares ApproximateVersion
     equal to the game's X.Y.Z (stricter than the game, which would take any
     lower PATCH of the same MAJOR.MINOR), read and parsed as the game reads
     it (so 0.8.07 or 0.8 is not 0.8.7), and every builder that writes
     _info.ini has a built SEST_* folder to check (build_all.py --from-scratch
     deletes them before it builds, so a failed build leaves none);
  2. every ApproximateVersion= literal in the pack builders
     (integration/*/build_*.py, found by what they write rather than by
     whether their output exists) and tools/consolidate_packs.py equals it,
     parsed as the game parses it, and every builder that writes _info.ini
     carries one;
  3. no Workshop mod in data/load-order.tokens.txt declares an ExactVersion,
     or (having no ExactVersion or ApproximateVersion) a version range, that
     excludes the game: SETUP never rewrites those;
  4. mods-source/_vanilla/changelog.txt is not from a newer game than the
     snapshot's changelog, which would mean the export landed and the
     snapshot did not.
Workshop ApproximateVersion values are counted by how far they sit from the
game's, numerically per component. Listed as information: the mods more
than one minor version behind; the ones made for a newer game version,
which SETUP leaves alone unless they are on its reviewed list; and the ones
the game cannot read (not MAJOR.MINOR.PATCH, or a number above 2147483647),
which no game version accepts. SETUP marks those with a number too big and
those whose first two or three numbers (PATCH 0 when there are two) are no
higher than the game's version: on 0.8.7 it marks 0.8, 0.8.07 and 0.8.7.1
and leaves 0.8.08 and 0.8.8.1 alone.

--version and --bump take a version the game itself reads as
MAJOR.MINOR.PATCH (no leading zeros; --bump also no -pre-release or +build
part, since the literals it rewrites are plain X.Y.Z).

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
NEWER = "newer than the game"
NOT_SEMVER = "not MAJOR.MINOR.PATCH"
KINDS = ["match", "behind in patch only", "one minor behind", FAR_BEHIND,
         NEWER, NOT_SEMVER, "ExactVersion", "range only", "undeclared"]
# The game's SemanticVersion pattern (SemVer 2.0); its \d is written [0-9].
SEMVER = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
                    r"(?:-(?:0|[1-9][0-9]*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*)"
                    r"(?:\.(?:0|[1-9][0-9]*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*))*)?"
                    r"(?:\+[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*)?")
INT32_MAX = 2147483647
# What --bump writes: the literals are read back by LITERAL, digits and dots only.
PLAIN = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")
COMPAT_KEYS = ("ExactVersion", "ApproximateVersion", "GreaterThanVersion", "GreaterThanEqualToVersion",
               "LessThanVersion", "LessThanEqualToVersion", "ExcludeVersions")


def parse_version(text):
    """'0.8.2' -> (0, 8, 2); None when any component is not a number."""
    parts = text.strip().split(".")
    if not all(p.isascii() and p.isdigit() for p in parts):
        return None
    return tuple(int(p) for p in parts)


def parse_semver(text):
    """The game's reading of a version: (MAJOR, MINOR, PATCH), or None when it is not
    SemVer 2.0 or a number is above Int32 (the game then throws instead of answering)."""
    match = SEMVER.fullmatch(text)
    if not match:
        return None
    parts = tuple(int(match.group(i)) for i in (1, 2, 3))
    return parts if max(parts) <= INT32_MAX else None


def read_compat(path):
    """-> {key: value} for COMPAT_KEYS, as the game's ini reader sees [Compatibility].

    Each line stripped; one starting with //, # or ; skipped; the rest cut off at the
    first ;, // or # and stripped; only the first [Compatibility] section (case-sensitive;
    the game ignores a repeat in the same file); key names in any case, the first of a
    repeated key wins; a missing key reads "". Lines end at \r\n, \n or \r only.
    """
    found, inside = {}, False
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    for raw in re.split(r"\r\n|\n|\r", text):
        line = raw.strip()
        if re.match(r"(//|#|;)", line):
            continue
        line = re.split(r";|//|#", line, maxsplit=1)[0].strip()
        header = re.match(r"\[(.+)\]", line, re.S)
        if header:
            if inside:
                break
            inside = header.group(1) == "Compatibility"
            continue
        if not inside or "=" not in line:
            continue
        key, *rest = line.split("=")
        name = next((k for k in COMPAT_KEYS if k.lower() == key.strip().lower()), None)
        if name and name not in found:
            found[name] = "=".join(part.strip() for part in rest)
    return {key: found.get(key, "") for key in COMPAT_KEYS}


def judge(compat, game, version):
    """-> (kind, accepted, finding): how the game judges what read_compat found.

    kind is one of KINDS. finding completes "<mod> declares ..." for a declaration
    SETUP never rewrites (an ExactVersion, or a version range read because there is
    no ExactVersion or ApproximateVersion) when it excludes the game; otherwise None.
    """
    exact, approx = compat["ExactVersion"], compat["ApproximateVersion"]
    if exact:
        ok = parse_semver(exact) == game
        return "ExactVersion", ok, None if ok else f"ExactVersion={exact}, which excludes {version}"
    if approx:
        declared = parse_semver(approx)
        if declared is None:
            return NOT_SEMVER, False, None
        kind = classify(declared, game)
        return kind, kind in ("match", "behind in patch only"), None
    # Only now does the game read the range: GreaterThan before GreaterThanEqualTo,
    # LessThan before LessThanEqualTo, and any ExcludeVersions entry it can read.
    low_key = "GreaterThanVersion" if compat["GreaterThanVersion"] else "GreaterThanEqualToVersion"
    high_key = "LessThanVersion" if compat["LessThanVersion"] else "LessThanEqualToVersion"
    low, high = compat[low_key], compat[high_key]
    excluded = [v.strip() for v in compat["ExcludeVersions"].split(",") if v.strip()]
    if not (low or high or excluded):
        return "undeclared", True, None
    parts = []
    if low or high:
        parts.append((f"{low} {'<' if low_key == 'GreaterThanVersion' else '<='} " if low else "") + "v"
                     + (f" {'<' if high_key == 'LessThanVersion' else '<='} {high}" if high else ""))
    if excluded:
        parts.append("ExcludeVersions=" + ", ".join(excluded))
    text = "; ".join(parts)
    bounds = [parse_semver(value) for value in (low, high) if value]
    if None in bounds or any(parse_semver(v) is None and SEMVER.fullmatch(v) for v in excluded):
        return "range only", False, f"an unreadable range: {text}"
    low_v, high_v = (parse_semver(low) if low else None), (parse_semver(high) if high else None)
    ok = (game not in [parse_semver(v) for v in excluded]
          and (low_v is None or (game > low_v if low_key == "GreaterThanVersion" else game >= low_v))
          and (high_v is None or (game < high_v if high_key == "LessThanVersion" else game <= high_v)))
    return "range only", ok, None if ok else f"{text}, which excludes {version}"


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
        if parse_semver(override) is None:
            raise ValueError(f"--version {override!r} is not MAJOR.MINOR.PATCH as the game reads it")
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
    game = parse_semver(version)
    if game is None:
        raise ValueError(f"game version {version!r} is not MAJOR.MINOR.PATCH as the game reads it")
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
        # As the game reads it: the first [Compatibility] section, the first key.
        declared = read_compat(info)["ApproximateVersion"]
        tag = " (static: no builder writes it)" if info in static else ""
        if not declared:
            fail("packs", f"{rel(info)} declares no [Compatibility] ApproximateVersion{tag}")
        elif parse_semver(declared) != game:
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
            if parse_semver(value) != game:
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
    counts, unread, ranges, admitted = Counter(), [], 0, 0
    listed = {FAR_BEHIND: [], NEWER: [], NOT_SEMVER: []}
    for wid in ids:
        info = root / "mods-source" / wid / "_info.ini"
        if not info.exists():
            unread.append(wid)
            continue
        compat = read_compat(info)
        name = mod_name(read_ini(info), wid)
        kind, accepted, finding = judge(compat, game, version)
        counts[kind] += 1
        if kind == "range only":
            ranges += 1
            admitted += accepted
        if finding:
            fail("workshop", f"{wid} {name} declares {finding}")
        if kind in listed:
            approx = compat["ApproximateVersion"]
            listed[kind].append((parse_version(approx) or (), wid, name, approx))
    lines.append(f"Workshop mods in load order: {len(ids)}; {len(ids) - len(unread)} _info.ini read"
                 + (f"; {len(unread)} unreadable (not exported or no _info.ini): {', '.join(unread)}"
                    if unread else ""))
    lines.append(f"  ApproximateVersion vs {version}: "
                 + ", ".join(f"{counts[k]} {k}" for k in KINDS if counts[k]))
    lines.append(f"  Version ranges (read only without ExactVersion and ApproximateVersion): "
                 f"{ranges} declared, {admitted} admit {version}")
    below_minor = counts["one minor behind"] + counts[FAR_BEHIND]
    game_minor = ".".join(str(c) for c in game[:2])
    lines.append(f"INFO: {below_minor} mod(s) declare a minor version below {game_minor}, which the Mod Manager "
                 "lists as not compatible (it needs the game's MAJOR and MINOR and a PATCH no higher than the "
                 f"game's) and SETUP marks compatible; the {len(listed[FAR_BEHIND])} more than one minor behind:")
    for _, wid, name, approx in sorted(listed[FAR_BEHIND]):
        lines.append(f"  {approx:<8}{wid}  {name}")
    if listed[NEWER]:
        lines.append(f"INFO: {len(listed[NEWER])} mod(s) declare a newer game version than {version}, which the "
                     "Mod Manager lists as not compatible too; SETUP names them and leaves them alone unless "
                     "they are on its reviewed list:")
        for _, wid, name, approx in sorted(listed[NEWER]):
            lines.append(f"  {approx:<8}{wid}  {name}")
    if listed[NOT_SEMVER]:
        lines.append(f"INFO: {len(listed[NOT_SEMVER])} mod(s) declare an ApproximateVersion the game cannot read "
                     "(not MAJOR.MINOR.PATCH, or a number above 2147483647), which the Mod Manager lists as not "
                     "compatible on any game version; SETUP marks the ones with a number above 2147483647 and the "
                     "ones whose first two or three numbers (PATCH 0 when there are two) are no higher than "
                     f"{version}:")
        for _, wid, name, approx in sorted(listed[NOT_SEMVER]):
            lines.append(f"  {approx!r:<10}{wid}  {name}")

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
    if parse_semver(version) is None or not PLAIN.fullmatch(version):
        raise ValueError(f"--bump {version!r} is not MAJOR.MINOR.PATCH as the game reads it, "
                         "with no -pre-release or +build part")
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
