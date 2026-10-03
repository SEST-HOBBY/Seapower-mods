#!/usr/bin/env python3
"""Report what a game update changed in the vanilla export, and what in this
repo depends on each change.

A Sea Power update arrives as a fresh export of StreamingAssets into
mods-source/_vanilla/original (tools/export-mod-configs.ps1 -IncludeVanilla).
That export is the baseline every SEST pack is built against: builders fork
vanilla files, language_*/ and systems/ files merge with vanilla key by key,
and the missions field vanilla units by id. A changed vanilla file matters
only through what in this repo depends on it, and a plain diff cannot say
what that is.

This compares the export at a git revision (default: the last commit that
touched it) with the export now in the working tree, lists what was added,
removed and modified, and for each changed file reads the repo for its
dependants:

  1. OVERRIDDEN    a SEST pack ships the same path, so the pack's copy masks
                   the changed vanilla file. Says which pack, and whether the
                   pack's builder names the file in code (so a rebuild rebases
                   it), writes the file's folder from data (f"ammunition/
                   {id}.ini", a glob), or neither - a static copy someone must
                   re-fork by hand.
  2. MERGED        language_*/ and systems/ files merge key by key, so a pack's
                   copy adds to vanilla's rather than masking it. Lists the
                   keys the changed vanilla file and a SEST pack both define.
                   A key vanilla did not define before is a clash: the
                   builders refuse to shadow a vanilla key (see
                   build_missing_loadout_names() in
                   integration/collection-fixes/build_patch.py), so the next
                   build stops on it. In systems/ files a key the pack
                   carries at vanilla's own new value is a MIRROR instead:
                   Collection Fixes restores the game's weapons.ini sections
                   over stale mod copies, and must agree with the game. In
                   language_*/ files only a section the pack carries VERBATIM
                   (vanilla's keys, vanilla's values, nothing else) mirrors:
                   Collection Fixes ships the game's loading_tips.ini that
                   way over a mod's Chinese copy, and must follow the game.
  3. PLACED        unit files whose id a mission fields (Type=<id>), a flight
                   deck readies (FlightDeck_ReadyUpTaskN=<id>,...) or a
                   campaign roster sells (TaskForceModeAllowedRosterUnits= in
                   campaign.ini and player_task_force_roster.ini), in the
                   mission sources and the built campaigns. A removed one is a
                   mission that no longer loads.
  4. BUILDER-READ  a builder names the file: by path, by file name, or (for
                   unit files) by quoted id. Code lines count; comment,
                   docstring and description-template lines are shown but
                   marked. Builders are the .py
                   modules under integration/<dir>/ at any depth, the
                   campaign's mission modules included.
  5. NEW CONTENT   added unit files, as candidates to place, with their
                   UnitType and the nation and service date from the matching
                   squadrons or variants file.

Line-ending-only changes are set aside, since nothing here reads a file's
line endings. The game version is read from the head of
mods-source/_vanilla/changelog.txt at both ends and printed old -> new.
The export script overlays files and never deletes, so a file the game
dropped stays in the export until someone removes it by hand; "removed" here
means exactly that.

    python3 tools/check_vanilla_drift.py
    python3 tools/check_vanilla_drift.py --since a4d3c1c1

When the export has already been committed, the default revision is that
commit and the report shows no drift; pass --since with the export commit
before it (the header names it). A revision with no export under it is
refused rather than compared against nothing.

Exits 1 when a finding needs a human: a static override masking a changed
file, a merged-key clash, or a fielded unit removed. Reads only; runs no git
command that changes state.
"""
import argparse
import ast
import collections
import hashlib
import io
import os
import re
import subprocess
import sys
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VANILLA = Path("mods-source/_vanilla/original")
CHANGELOG = Path("mods-source/_vanilla/changelog.txt")
UNIT_DIRS = ("aircraft", "vessels", "submarines", "land_units", "ammunition")
COMPANIONS = ("_squadrons", "_variants")
# Where units are fielded: mission sources, built missions and campaigns, and
# the campaign buy lists.
FIELDED_GLOBS = (
    "integration/missions/*.ini",
    "integration/missions/scenarios/*.ini",
    "integration/dist/SEST_Integration/campaigns/*/missions/*.ini",
    "integration/dist/SEST_Integration/campaigns/*/campaign.ini",
    "integration/dist/SEST_Integration/campaigns/*/player_task_force_roster.ini",
    "integration/dist/SEST_Integration/missions/**/*.ini",
)
UNIT_REFS = (
    re.compile(r"^Type=(\S+)", re.M),                            # a placed unit
    re.compile(r"^FlightDeck_ReadyUpTask\d+=([^,\s]+)", re.M),   # an aircraft readied on a deck
)
ROSTER_LINE = re.compile(r"^TaskForceModeAllowedRosterUnits=(.*)$", re.M)  # id,Variant..|id,Squadron..
# "20-Jul-2026: 0.8.2 Build #358 (23444) Public Release" until Sep 2026;
# "01-Oct-2026: 0.8.3 Build 261001 Public Release" and "Build 260928b" since
# (no "#", no "(N)", a letter suffix): the build is whatever word follows.
VERSION_LINE = re.compile(
    r"^\s*(\d{1,2}-[A-Za-z]{3}-\d{4}):\s*(\d+(?:\.\d+)+)\s+Build\s+#?(\w+)\s*(?:\((\d+)\))?\s*(.*?)\s*$", re.M)
BANNER = "=" * 70


# ------------------------------------------------------------------ git
def git(root, *args, data=None, optional=False):
    """Stdout of a read-only git command run in root; None if optional and it fails."""
    proc = subprocess.run(["git", *args], cwd=root, input=data, capture_output=True)
    if proc.returncode:
        if optional:
            return None
        raise SystemExit(f"git {' '.join(args)}: {proc.stderr.decode('utf-8', 'replace').strip()}")
    return proc.stdout


def export_commits(root, count=2):
    """[(sha, date, subject)] of the last commits that touched the export, newest first."""
    out = git(root, "log", f"-{count}", "--format=%H%x09%ad%x09%s", "--date=short", "--", VANILLA.as_posix())
    return [tuple(line.split("\t", 2)) for line in out.decode("utf-8", "replace").splitlines() if line]


def resolve(root, rev):
    """Full commit sha for rev, or exit naming the bad revision."""
    sha = git(root, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}", optional=True)
    if not sha:
        raise SystemExit(f"--since {rev}: not a commit in this repository")
    return sha.decode().strip()


def tree_at(root, rev):
    """{path relative to the export: blob sha} as committed at rev."""
    tree = {}
    for entry in git(root, "ls-tree", "-r", "-z", rev, "--", VANILLA.as_posix()).split(b"\0"):
        if not entry:
            continue
        meta, _, path = entry.partition(b"\t")
        _, kind, sha = meta.split()
        if kind != b"blob":
            continue
        rel = Path(path.decode("utf-8", "surrogateescape")).relative_to(VANILLA)
        tree[rel.as_posix()] = sha.decode()
    return tree


def blob_sha(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def read_blobs(root, shas):
    """{sha: bytes} through one cat-file process, not one git show per file."""
    if not shas:
        return {}
    out = git(root, "cat-file", "--batch", data="".join(f"{s}\n" for s in shas).encode())
    blobs, pos = {}, 0
    while pos < len(out):
        end = out.index(b"\n", pos)
        header = out[pos:end].decode().split()
        pos = end + 1
        if len(header) < 3:          # "<sha> missing"
            continue
        size = int(header[2])
        blobs[header[0]] = out[pos:pos + size]
        pos += size + 1
    return blobs


def working_tree(root):
    base = root / VANILLA
    if not base.is_dir():
        raise SystemExit(f"no vanilla export at {base}")
    return {p.relative_to(base).as_posix(): p for p in sorted(base.rglob("*")) if p.is_file()}


class Drift:
    """Added, removed, modified and line-ending-only paths, with the bytes needed later."""

    def __init__(self):
        self.added, self.removed, self.modified, self.eol_only = [], [], [], []
        self.old, self.new = {}, {}
        self.count_then = self.count_now = 0

    def changed(self):
        """(path, change) for everything a dependant could care about."""
        return ([(r, "added") for r in self.added] + [(r, "removed") for r in self.removed]
                + [(r, "modified") for r in self.modified])


def compare(root, since):
    then = tree_at(root, since)
    if not then:
        raise SystemExit(f"--since {since[:8]}: no {VANILLA.as_posix()} is committed at that revision; "
                         f"pass an export commit (git log -- {VANILLA.as_posix()})")
    now = working_tree(root)
    drift = Drift()
    drift.count_then, drift.count_now = len(then), len(now)
    drift.added = sorted(set(now) - set(then))
    drift.removed = sorted(set(then) - set(now))
    for rel in drift.added:
        drift.new[rel] = now[rel].read_bytes()
    candidates = []
    for rel in sorted(set(now) & set(then)):
        data = now[rel].read_bytes()
        if blob_sha(data) != then[rel]:
            candidates.append(rel)
            drift.new[rel] = data
    blobs = read_blobs(root, sorted({then[r] for r in candidates}))
    for rel in candidates:
        old, new = blobs.get(then[rel], b""), drift.new[rel]
        if old.replace(b"\r\n", b"\n") == new.replace(b"\r\n", b"\n"):
            drift.eol_only.append(rel)
            del drift.new[rel]
        else:
            drift.modified.append(rel)
            drift.old[rel] = old
    return drift


# ------------------------------------------------------------------ parsing
def game_version(text):
    """The first changelog entry as {date, version, build, number, note}, or None."""
    m = VERSION_LINE.search(text or "")
    if not m:
        return None
    return dict(zip(("date", "version", "build", "number", "note"), m.groups()))


def describe(version):
    return f"{version['version']} Build #{version['build']} ({version['date']})" if version else "unknown"


def decode(data):
    return data.decode("utf-8-sig", errors="replace")


def parse_ini(text):
    """{section: {key: value}}; comments dropped, keys before any header under ''."""
    sections = collections.OrderedDict()
    current = sections.setdefault("", {})
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", ";", "//")):
            continue
        if line.startswith("["):
            name = line[1:line.index("]")] if "]" in line else line[1:]
            current = sections.setdefault(name.strip(), {})
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key and key not in current:
            current[key] = value.strip()
    return sections


def visible(value):
    """A value without its trailing // comment, which vanilla carries on most keys."""
    return value.split("//")[0].strip()


def shipped_by(root, rel):
    """Workshop mods (mods-source/<id>) that ship the same relative path as a
    vanilla file: a removed vanilla unit one of them ships is still a unit."""
    found = []
    for mod in sorted((root / "mods-source").iterdir()):
        if mod.name.startswith("_") or not mod.is_dir():
            continue
        if (mod / rel).is_file():
            found.append(mod.name)
    return found


def unit_of(rel):
    """(unit id, companion kind or None) for a file in a unit folder, else None."""
    p = Path(rel)
    if len(p.parts) != 2 or p.parts[0] not in UNIT_DIRS or p.suffix.lower() != ".ini":
        return None
    for suffix in COMPANIONS:
        if p.stem.lower().endswith(suffix):
            return p.stem[:-len(suffix)], suffix[1:]
    return p.stem, None


def merges(rel):
    return rel.startswith("language_") or rel.startswith("systems/")


def unit_refs(path, text):
    """Every unit id a mission, campaign or roster file names."""
    for pattern in UNIT_REFS:
        yield from pattern.findall(text)
    for value in ROSTER_LINE.findall(text):
        for entry in value.split("|"):
            if entry.strip():
                yield entry.split(",")[0].strip()
    if path.name.casefold() == "player_task_force_roster.ini":
        for section, keys in parse_ini(text).items():
            if section.startswith("Allowed"):
                yield from keys


# ------------------------------------------------------------------ the repo
def sest_packs(root):
    """[(pack name, pack dir)] for every integration/*/SEST_* outside dist."""
    return [(pack.name, pack) for pack in sorted((root / "integration").glob("*/SEST_*"))
            if pack.is_dir() and pack.parent.name != "dist"]


def pack_files(packs):
    """casefolded relative path -> [(pack name, pack dir, the pack's file)]."""
    index = collections.defaultdict(list)
    for name, pack in packs:
        for f in pack.rglob("*"):
            if f.is_file():
                index[f.relative_to(pack).as_posix().casefold()].append((name, pack, f))
    return index


def prose_lines(source):
    """Line numbers inside bare string statements, which is where docstrings live."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    lines = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            lines.update(range(node.lineno, node.end_lineno + 1))
    return lines


def string_lines(source):
    """({line: column where its # comment starts}, {lines inside multi-line
    strings}) from the tokenizer, so a '#' inside a string is not taken for a
    comment, a trailing comment is not code, and a path quoted in a pack's
    description template is told apart from one passed to a call."""
    columns, multiline = {}, set()
    try:
        for tok in tokenize.generate_tokens(io.StringIO(source).readline):
            if tok.type == tokenize.COMMENT:
                columns.setdefault(tok.start[0], tok.start[1])
            elif tok.type == tokenize.STRING and tok.start[0] != tok.end[0]:
                multiline.update(range(tok.start[0], tok.end[0] + 1))
    except (tokenize.TokenError, SyntaxError):
        pass
    return columns, multiline


def words(text):
    """The casefolded word tokens on a line. A file name at the end of a sentence
    carries its full stop, so leading and trailing dots and dashes are dropped."""
    return {w.strip(".-").casefold() for w in re.findall(r"[\w.\-]+", text)} - {""}


class Builders:
    """Every line of every builder module under integration/, indexed by the
    words on it.

    A builder is any .py under integration/<dir>/ at any depth - the campaign's
    mission modules live two levels down and name the units they field -
    except the built dist, the packs themselves, tests and caches.
    """

    def __init__(self, root):
        self.common = root / "integration" / "common"
        files = []
        for d in sorted((root / "integration").glob("*")):
            if d.is_dir() and d.name != "dist":
                files += [p for p in d.rglob("*.py") if not p.name.startswith("test_")
                          and not any(part == "__pycache__" or part.startswith("SEST_")
                                      for part in p.relative_to(d).parts)]
        self.lines, self.by_word = [], collections.defaultdict(list)
        for py in sorted(files):
            source = py.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
            prose = prose_lines(source)
            comments, templates = string_lines(source)
            for no, text in enumerate(source.split("\n"), 1):
                code = "" if no in prose or no in templates else text[:comments.get(no, len(text))]
                for word in words(text):
                    self.by_word[word].append(len(self.lines))
                self.lines.append((py, no, text, code, no in templates and no not in prose))

    def lines_with(self, tokens):
        """Indexes of the lines carrying every one of the tokens."""
        sets = [set(self.by_word.get(t, ())) for t in tokens]
        return set.intersection(*sets) if sets and all(sets) else set()

    def owns(self, hit, pack):
        """Whether the line is in the pack's own integration folder or in common/."""
        py = hit[0]
        return pack.parent in py.parents or py.parent == self.common

    def mentions(self, rel):
        """Lines that name rel, code first, then description templates, then comments:
        by path, by file name, or by quoted unit id.

        A file at the export root has only its name to go by, and builders
        write their own _info.ini and config files, so a root-level file must
        be named on a line that also says vanilla. Case is ignored throughout:
        the export has fr_alouette_II.ini and a builder may spell it either way.
        """
        p = Path(rel)
        posix, name = p.as_posix().casefold(), p.name.casefold()
        backslash = posix.replace("/", "\\")
        quoted = re.compile(rf"[\"']{re.escape(p.stem)}[\"']", re.I) if unit_of(rel) else None

        def named(text):
            low = text.casefold()
            if len(p.parts) == 1:
                return name in low and "vanilla" in low
            return (posix in low or backslash in low or name in low
                    or (quoted is not None and quoted.search(text) is not None))

        candidates = self.lines_with(words(p.name))
        if quoted:
            candidates |= self.lines_with(words(p.stem))
        hits = []
        for i in sorted(candidates):
            py, no, text, code, template = self.lines[i]
            kind = "code" if named(code) else None if not named(text) else "text" if template else "comment"
            if kind:
                hits.append((py, no, text.strip(), kind))
        return sorted(hits, key=lambda h: (("code", "text", "comment").index(h[3]), h[0], h[1]))

    def patterns(self, rel):
        """Code lines that build a path in the file's folder from data: an f-string
        placeholder or a glob star right after the folder name, as in
        f"ammunition/{rid}.ini", OUT / "ammunition" / f"{rid}.ini" or
        glob("ammunition/*.ini"). Such a builder ships the file without ever
        naming it, so these decide "static copy" when no line names the file."""
        p = Path(rel)
        hits = []
        for folder in p.parts[:-1]:
            joined = re.compile(re.escape(folder) + r"[\"']?\s*[/,]\s*(?:f?[\"'])?\s*[{*]", re.I)
            for i in sorted(self.lines_with(words(folder))):
                py, no, text, code, _ = self.lines[i]
                if joined.search(code):
                    hits.append((py, no, text.strip(), "code"))
        return sorted(set(hits), key=lambda h: (h[0], h[1]))


def fielded_units(root):
    """casefolded unit id -> sorted mission, campaign and roster files that field it."""
    used = collections.defaultdict(set)
    for pattern in FIELDED_GLOBS:
        for f in sorted(root.glob(pattern)):
            text = f.read_text(encoding="utf-8-sig", errors="replace")
            for uid in unit_refs(f, text):
                used[uid.casefold()].add(f.relative_to(root / "integration").as_posix())
    return {uid: sorted(files) for uid, files in used.items()}


def companion_facts(root, rel):
    """(companion file name, Nation, ServiceDate) from the unit's squadrons or variants file."""
    p = Path(rel)
    suffix = "_squadrons" if p.parts[0] == "aircraft" else "_variants"
    companion = root / VANILLA / p.parent / f"{p.stem}{suffix}.ini"
    if not companion.exists():
        return None, None, None
    default = parse_ini(companion.read_text(encoding="utf-8-sig", errors="replace")).get("Default", {})
    return companion.name, visible(default.get("Nation", "")), visible(default.get("ServiceDate", ""))


# ------------------------------------------------------------------ classify
class Report:
    def __init__(self):
        self.overridden, self.merged, self.placed = [], [], []
        self.builder_read, self.new_content, self.other = [], [], []
        self.findings = []


def shared_keys(rel, pack_text, old_text, new_text):
    """(clashes, changed, unchanged, mirrored) between a pack's merge file and
    vanilla's old and new copies.

    A key vanilla newly defines that the pack also defines is a CLASH - the
    builders refuse to shadow a vanilla key, so the next build stops on it.
    In systems/ files only, a pack key whose value IS vanilla's new value is
    the pack carrying the game's own definition forward (SEST Collection
    Fixes does this on purpose for the weapons.ini sections four aircraft
    mods' stale copies shadow), and is MIRRORED: listed, not a finding. A
    whole systems/ section vanilla now supplies stays a clash whatever its
    values. A language_*/ key mirrors only when the pack carries the whole
    section VERBATIM - vanilla's keys, vanilla's values, not one more - which
    is what build_vanilla_tips() does with loading_tips.ini; a section that
    adds names stays a clash on every new key, because build_missing_sensors()
    and build_missing_loadout_names() stop on the NAME, so the next build does."""
    pack_ini, old_ini, new_ini = parse_ini(pack_text), parse_ini(old_text), parse_ini(new_text)
    clashes, changed, unchanged, mirrored = [], [], 0, []
    for section, keys in pack_ini.items():
        was = old_ini.get(section)
        if rel.startswith("systems/") and section and section in new_ini and was is None:
            clashes.append((section, None))      # a whole definition vanilla now supplies
            continue
        verbatim = (rel.startswith("language_") and section in new_ini
                    and {k: visible(v) for k, v in keys.items()}
                    == {k: visible(v) for k, v in new_ini[section].items()})
        for key in keys:
            if section not in new_ini or key not in new_ini[section]:
                continue
            if was is None or key not in was:
                same = visible(keys[key]) == visible(new_ini[section][key])
                if (rel.startswith("systems/") and same) or verbatim:
                    mirrored.append((section, key))
                else:
                    clashes.append((section, key))
            elif visible(was[key]) != visible(new_ini[section][key]):
                changed.append((section, key, visible(was[key]), visible(new_ini[section][key])))
            else:
                unchanged += 1
    return clashes, changed, unchanged, mirrored


def classify(root, drift):
    shipped = pack_files(sest_packs(root))
    builders = Builders(root)
    fielded = fielded_units(root)
    report = Report()
    for rel, change in drift.changed():
        seen = False
        # Every mod carries its own _info.ini; a pack's is not a copy of vanilla's.
        owners = [] if rel.casefold() == "_info.ini" else shipped.get(rel.casefold(), [])
        if owners and merges(rel):
            entries = []
            for name, pack, own_file in owners:
                if change == "removed":
                    entries.append((name, [], [], 0, []))
                    continue
                clashes, changed, unchanged, mirrored = shared_keys(
                    rel, own_file.read_text(encoding="utf-8-sig", errors="replace"),
                    decode(drift.old.get(rel, b"")), decode(drift.new[rel]))
                entries.append((name, clashes, changed, unchanged, mirrored))
                for section, key in clashes:
                    what = f"[{section}]" if key is None else f"[{section}] {key}"
                    report.findings.append(f"{rel}: vanilla now defines {what}, which {name} also defines")
            report.merged.append((rel, change, entries))
            seen = True
        elif owners:
            entries = []
            for name, pack, _ in owners:
                own = [h for h in builders.mentions(rel) if h[3] == "code" and builders.owns(h, pack)]
                by_pattern = [] if own else [h for h in builders.patterns(rel) if builders.owns(h, pack)]
                entries.append((name, own, by_pattern))
                if not own and not by_pattern:
                    report.findings.append(f"{rel} ({change}): {name} ships a static copy that now masks it")
            report.overridden.append((rel, change, entries))
            seen = True
        unit = unit_of(rel)
        if unit:
            uid, via = unit
            places = fielded.get(uid.casefold())
            if places:
                # A unit the game dropped is still a unit if a Workshop mod
                # ships the same file (0.8.3 dropped its Tu-16N stub; the
                # Tu-16N mod's copy is what D7 fields): reported, not a finding.
                still = shipped_by(root, rel) if change == "removed" and via is None else []
                report.placed.append((rel, change, uid, via, places, still))
                seen = True
                if change == "removed" and via is None and not still:
                    report.findings.append(f"{rel}: removed, but {len(places)} file(s) field {uid}")
            if change == "added" and via is None:
                general = parse_ini(decode(drift.new[rel])).get("General", {})
                kind = visible(general.get("UnitType") or general.get("Type") or "")
                if rel.startswith("ammunition/") and general.get("TargetType"):
                    kind = f"{kind} {visible(general['TargetType'])}".strip()
                report.new_content.append((rel, kind) + companion_facts(root, rel))
                seen = True
            if change == "added" and via and f"{Path(rel).parent.as_posix()}/{uid}.ini" in drift.added:
                seen = True                      # shown with its unit's candidate line
        hits = builders.mentions(rel)
        if hits:
            report.builder_read.append((rel, change, hits))
            seen = True
        if not seen:
            report.other.append((rel, change))
    return report


# ------------------------------------------------------------------ output
def heading(number, title, count):
    print(f"\n{BANNER}\n{number}. {title} ({count})\n{BANNER}")


def where(root, hit):
    py, no, text, kind = hit
    mark = {"comment": "  (comment)", "text": "  (text)"}.get(kind, "")
    return f"{py.relative_to(root).as_posix()}:{no}  {text[:70]}{mark}"


def render(root, since, since_rev, drift, report, old_version, new_version, default_since):
    commits = export_commits(root)
    print(f"Vanilla drift since {since_rev[:8]}" + ("" if since_rev.startswith(since) else f" ({since})"))
    for sha, date, subject in commits:
        tag = "this revision" if sha == since_rev else "export commit"
        print(f"  {tag:<14} {sha[:8]} {date} {subject}")
    same = old_version == new_version
    print(f"Game version: {describe(old_version)} -> {describe(new_version)}"
          + ("  [unchanged]" if same and new_version else ""))
    print(f"Files under {VANILLA.as_posix()}: {drift.count_then} then, {drift.count_now} now")
    print(f"  added {len(drift.added)}, removed {len(drift.removed)}, modified {len(drift.modified)}, "
          f"line endings only {len(drift.eol_only)}")

    heading(1, "OVERRIDDEN - a SEST pack ships the same path", len(report.overridden))
    for rel, change, entries in report.overridden:
        print(f"   {rel}  {change}")
        for name, own, by_pattern in entries:
            if own:
                print(f"      {name}: builder-derived, a rebuild rebases it ({where(root, own[0])})")
            elif by_pattern:
                print(f"      {name}: builder-derived by pattern - the builder writes the folder from data "
                      f"({where(root, by_pattern[0])})")
            else:
                print(f"      {name}: STATIC COPY - no builder code names the file; re-fork it by hand")
    if not report.overridden:
        print("   none")

    heading(2, "MERGED - keys the changed file and a SEST pack both define", len(report.merged))
    for rel, change, entries in report.merged:
        print(f"   {rel}  {change}  (also shipped by {len(entries)} pack(s))")
        quiet = []
        for name, clashes, changed, unchanged, mirrored in entries:
            if not (clashes or changed or unchanged or mirrored):
                quiet.append(name)
                continue
            print(f"      {name}:")
            for section, key in clashes:
                what = f"[{section}]" if key is None else f"[{section}] {key}"
                print(f"         CLASH {what} is new in vanilla; the next build stops on it")
            if mirrored:
                shown = ", ".join(f"[{s}]" if k is None else f"[{s}] {k}" for s, k in mirrored[:6])
                more = f" and {len(mirrored) - 6} more" if len(mirrored) > 6 else ""
                print(f"         MIRROR {len(mirrored)} new vanilla key(s) the pack carries at "
                      f"vanilla's own value: {shown}{more}")
            for section, key, old, new in changed:
                print(f"         [{section}] {key}: vanilla value {old!r} -> {new!r}; the pack's copy masks it")
            if unchanged:
                print(f"         {unchanged} other shared key(s) unchanged in vanilla")
        if quiet and change == "removed":
            print(f"      vanilla no longer ships it; the packs' copies stand alone: {', '.join(quiet)}")
        elif quiet:
            print(f"      no shared keys: {', '.join(quiet)}")
    if not report.merged:
        print("   none")

    heading(3, "PLACED - units a mission, flight deck or campaign roster fields", len(report.placed))
    for rel, change, uid, via, places, still in report.placed:
        how = f" (via its {via} file)" if via else ""
        flag = "REMOVED" if change == "removed" and not via and not still else change
        shown = ", ".join(places[:3]) + (f", ... and {len(places) - 3} more" if len(places) > 3 else "")
        standing = f"; still shipped by {', '.join(still)}" if still else ""
        print(f"   {rel}  {flag}{how} - {uid} fielded by {len(places)} file(s): {shown}{standing}")
    if not report.placed:
        print("   none")

    heading(4, "BUILDER-READ - a builder names the file", len(report.builder_read))
    for rel, change, hits in report.builder_read:
        print(f"   {rel}  {change}")
        for hit in hits[:6]:
            print(f"      {where(root, hit)}")
        if len(hits) > 6:
            print(f"      ... and {len(hits) - 6} more line(s)")
    if not report.builder_read:
        print("   none")

    heading(5, "NEW CONTENT - added unit files, candidates to place", len(report.new_content))
    for rel, kind, companion, nation, service in report.new_content:
        facts = [f"UnitType={kind or '?'}"]
        if nation:
            facts.append(f"Nation={nation}")
        if service:
            facts.append(f"ServiceDate={service}")
        source = f"  (from {companion})" if companion else "  (no squadrons/variants file)"
        print(f"   {rel}  " + "  ".join(facts) + source)
    if not report.new_content:
        print("   none")

    heading(6, "LINE ENDINGS ONLY - content identical", len(drift.eol_only))
    for rel in drift.eol_only[:20]:
        print(f"   {rel}")
    if len(drift.eol_only) > 20:
        print(f"   ... and {len(drift.eol_only) - 20} more")
    if not drift.eol_only:
        print("   none")

    heading(7, "OTHER CHANGES - no pack, mission or builder names them", len(report.other))
    by_folder = collections.defaultdict(list)
    for rel, change in report.other:
        by_folder[Path(rel).parts[0] if len(Path(rel).parts) > 1 else "."].append((rel, change))
    for folder, items in sorted(by_folder.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        print(f"   {folder}: {len(items)}")
        for rel, change in items[:12]:
            print(f"      {rel}  {change}")
        if len(items) > 12:
            print(f"      ... and {len(items) - 12} more")
    if not report.other:
        print("   none")

    print(f"\n{BANNER}\nVERDICT\n{BANNER}")
    for finding in report.findings:
        print(f"   NEEDS A HUMAN: {finding}")
    total = len(drift.changed())
    if report.findings:
        print(f"Vanilla drift: {len(report.findings)} finding(s) need a human; {total} file(s) changed since {since_rev[:8]}")
        return 1
    if not total and not drift.eol_only:
        hint = ""
        if default_since and len(commits) > 1:
            hint = f"; if {since_rev[:8]} is the new export itself, run with --since {commits[1][0][:8]}"
        print(f"Vanilla drift: PASS - no drift since {since_rev[:8]}{hint}")
    else:
        print(f"Vanilla drift: PASS - {total} file(s) changed, {len(drift.eol_only)} line endings only, "
              f"nothing needs a human")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=" ".join(__doc__.split("\n\n")[0].split()))
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root (default: this checkout)")
    parser.add_argument("--since", help="git revision whose vanilla export is the baseline "
                                        "(default: the last commit that touched the export)")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    top = git(root, "rev-parse", "--show-toplevel", optional=True)
    if top is None or Path(top.decode().strip()).resolve() != root:
        raise SystemExit(f"{root} is not the top level of a git repository")
    default_since = args.since is None
    if default_since:
        commits = export_commits(root, 1)
        if not commits:
            raise SystemExit(f"no commit has touched {VANILLA.as_posix()}; pass --since")
        since = commits[0][0]
    else:
        since = args.since
    since_rev = resolve(root, since)
    drift = compare(root, since_rev)
    old_log = git(root, "show", f"{since_rev}:{CHANGELOG.as_posix()}", optional=True)
    new_log = root / CHANGELOG
    old_version = game_version(decode(old_log)) if old_log is not None else None
    new_version = game_version(new_log.read_text(encoding="utf-8-sig", errors="replace")) if new_log.exists() else None
    report = classify(root, drift)
    return render(root, since, since_rev, drift, report, old_version, new_version, default_since)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:          # piped into head; the verdict was never read
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(1)
