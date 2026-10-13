#!/usr/bin/env python3
"""The facts of one Workshop refresh, side by side with the previous capture.

    python3 tools/workshop_refresh_summary.py               # write the summary
    python3 tools/workshop_refresh_summary.py --since <ref> # compare with that commit
    python3 tools/workshop_refresh_summary.py --since-export <ref>

Reads what tools/capture-context.ps1 and tools/export-mod-configs.ps1 wrote
(data/install-snapshot/, mods-source/) and the canonical lists
(data/load-order.tokens.txt, data/mod-catalog.json), plus the authors' change
notes the player copies from Steam (data/install-snapshot/workshop-change-notes.txt,
optional), and writes data/install-snapshot/workshop-refresh-summary.txt. The previous capture is
the last commit that changed workshop-subscriptions.txt before the one being
summarised, unless --since names another. Exported files are compared with
the previous EXPORT instead - the last commit that changed
mods-source/_export-manifest.csv before this capture - since an export can
be committed between two captures (11 Oct 2026) and would otherwise be
counted again; --since-export names another.

The four inventories, as the refresh procedure names them:
  A  Steam's own record of the subscriptions on this PC (appworkshop_1286220.acf)
  B  Workshop folders on disk (workshop-subscriptions.txt)
  C  the canonical order's Workshop ids (data/load-order.tokens.txt)
  D  the catalog's installed entries (status active, deprecated or wip)
capture-context.ps1 writes A only as a count and its differences from B, so
A is reported that way. Facts only: no compatibility judgement is made here.
"""
import argparse
import csv
import io
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "data" / "install-snapshot"
SUBS = "data/install-snapshot/workshop-subscriptions.txt"
MANIFEST = "mods-source/_export-manifest.csv"
SEST_OWN = {"3812461539"}   # SEST's own Workshop item (export-mod-configs.ps1 $SestOwnWorkshopIds)
OUT = SNAP / "workshop-refresh-summary.txt"
NOTES = SNAP / "workshop-change-notes.txt"   # authors' Steam change notes, pasted by the player
INSTALLED = {"active", "deprecated", "wip"}
DETAIL = 12          # changed files listed per mod; the rest are counted


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True).stdout


def at(ref, rel):
    """A file's text at a commit, or None."""
    out = subprocess.run(["git", "-C", str(ROOT), "show", f"{ref}:{rel}"], capture_output=True)
    return out.stdout.decode("utf-8-sig", "replace") if out.returncode == 0 else None


def previous_capture():
    hist = git("log", "--format=%H", "-n", "2", "--", SUBS).split()
    if not hist:
        return None
    changed = git("status", "--porcelain", "--", SUBS).strip()
    return hist[0] if changed else (hist[1] if len(hist) > 1 else None)


def previous_export():
    """The last commit that changed the export manifest before this capture began."""
    start = None if git("status", "--porcelain", "--", SUBS).strip() else \
        (git("log", "--format=%H", "-n", "1", "--", SUBS).split() or [None])[0]
    ref = f"{start}^" if start else "HEAD"
    hist = git("log", "--format=%H", "-n", "1", ref, "--", MANIFEST).split()
    return hist[0] if hist else None


def live_sest(live, assets):
    """Where the live Mod Manager list takes SEST from, and how many local SEST folders exist."""
    rows = re.findall(r"^\s*(\d+)\.\s+(\S+)\s+(on|off)\b", live, re.M)
    hits = [f"{tok} at {pos} ({state}{', Workshop copy' if tok in SEST_OWN else ''})"
            for pos, tok, state in rows if tok in SEST_OWN or tok.startswith("SEST_")]
    m = re.search(r"^SEST folders present:\s*(\d+)", assets, re.M)
    return ", ".join(hits) or "none", (m.group(1) if m else "not captured")


def folders(text):
    """{id: (name, updated)} from workshop-subscriptions.txt's id lines."""
    out = {}
    for line in (text or "").splitlines():
        m = re.match(r"^(\d{6,})\s+(.*?)\s+updated (\S+)\s*$", line)
        if m:
            out[m.group(1)] = (m.group(2), m.group(3))
    return out


def field(text, label):
    m = re.search(rf"^{re.escape(label)}\s*:\s*(.*)$", text or "", re.M)
    return m.group(1).strip() if m else "not captured"


def ids_after(text, label):
    m = re.search(rf"^{re.escape(label)} \((\d+)\):[ \t]*(.*)$", text or "", re.M)
    return (int(m.group(1)), m.group(2).split()) if m else (None, [])


def game_version():
    log = (ROOT / "mods-source" / "_vanilla" / "changelog.txt")
    head = log.read_text(encoding="utf-8", errors="replace").splitlines()[:12] if log.is_file() else []
    line = next((l.strip() for l in head if "Build" in l), "no Build line in the changelog head")
    build = (SNAP / "game-build.txt").read_text(encoding="utf-8", errors="replace") \
        if (SNAP / "game-build.txt").is_file() else ""
    return line, field(build, "steam buildid"), field(build, "product version")


def tokens():
    return [l.strip() for l in (ROOT / "data" / "load-order.tokens.txt").read_text(encoding="utf-8-sig").splitlines()
            if l.strip() and not l.lstrip().startswith("#")]


def manifest(text):
    return {r["WorkshopId"]: r for r in csv.DictReader(io.StringIO(text or ""))} if text else {}


def dlls(text):
    """{(root, path): sha256} from plugin-dlls.txt."""
    out, root = {}, None
    for line in (text or "").splitlines():
        m = re.match(r"^\[(.+?)\]\s+\d+ DLL", line)
        if m:
            root = m.group(1)
            continue
        m = re.match(r"^\s{2}(.+?)\s{2,}\d+\s+([0-9a-f]{64}|unreadable)\s", line)
        if m and root:
            out[(root, m.group(1))] = m.group(2)
    return out


def file_changes(since):
    """{id: [(A/D/M/R, path inside the mod)]} for mods-source/<id> since a commit."""
    out = {}
    for line in git("diff", "--name-status", "-M", since, "--", "mods-source").splitlines():
        cols = line.split("\t")
        parts = cols[-1].split("/")
        if len(parts) > 2 and parts[1].isdigit():
            out.setdefault(parts[1], []).append((cols[0][0], "/".join(parts[2:])))
    return out


def listing(ids, names):
    return [f"  {i}  {names.get(i, '')}".rstrip() for i in sorted(ids)] or ["  (none)"]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--since", help="the commit holding the previous capture")
    ap.add_argument("--since-export", help="the commit holding the previous export")
    args = ap.parse_args()
    since = args.since or previous_capture()
    since_export = args.since_export or previous_export()

    subs_now = (ROOT / SUBS).read_text(encoding="utf-8", errors="replace")
    subs_then = at(since, SUBS) if since else None
    b_now, b_then = folders(subs_now), folders(subs_then)
    names = {i: n for i, (n, _) in {**b_then, **b_now}.items()}
    for i in SEST_OWN:
        names[i] = f"{names.get(i, 'SEST')} [SEST's own Workshop item]"
    catalog = json.loads((ROOT / "data" / "mod-catalog.json").read_text(encoding="utf-8-sig"))
    for m in catalog["mods"]:
        names.setdefault(m["workshop_id"], m.get("title", ""))
    order = tokens()
    c = {t for t in order if t.isdigit()}
    sest = [t for t in order if not t.isdigit()]
    d = {m["workshop_id"] for m in catalog["mods"] if m.get("status") in INSTALLED}
    every_catalogued = {m["workshop_id"] for m in catalog["mods"]}
    historical = sorted(m["workshop_id"] for m in catalog["mods"] if m.get("status") not in INSTALLED)
    b = set(b_now)

    live = (SNAP / "load-order.live.txt").read_text(encoding="utf-8", errors="replace") \
        if (SNAP / "load-order.live.txt").is_file() else ""
    live_entries = re.search(r"entries parsed: (\d+)", live)
    assets = (SNAP / "streaming-assets.txt").read_text(encoding="utf-8", errors="replace") \
        if (SNAP / "streaming-assets.txt").is_file() else ""
    sest_live, sest_local = live_sest(live, assets)
    env = (SNAP / "environment.txt").read_text(encoding="utf-8", errors="replace") \
        if (SNAP / "environment.txt").is_file() else ""
    changelog_line, buildid, unity = game_version()

    updated = sorted(i for i in b & set(b_then) if b_now[i][1] != b_then[i][1])
    exported = file_changes(since_export) if since_export else {}
    man_now = manifest((ROOT / "mods-source" / "_export-manifest.csv").read_text(encoding="utf-8-sig"))
    man_then = manifest(at(since_export, MANIFEST)) if since_export else {}
    dll_now = dlls((SNAP / "plugin-dlls.txt").read_text(encoding="utf-8", errors="replace")
                   if (SNAP / "plugin-dlls.txt").is_file() else "")
    dll_then = dlls(at(since, "data/install-snapshot/plugin-dlls.txt") if since else "")
    updates = SNAP / "workshop-updates.txt"

    tracked = field(subs_now, "ids Steam tracks locally")
    pending = field(subs_now, "NeedsDownload / NeedsUpdate")
    _, tracked_not_disk = ids_after(subs_now, "tracked but NOT on disk")
    _, disk_not_tracked = ids_after(subs_now, "on disk but NOT tracked")

    L = ["WORKSHOP REFRESH SUMMARY", "",
         "Written by tools/workshop_refresh_summary.py from data/install-snapshot/ and the",
         "canonical lists. Facts only; compatibility is judged in a later review.", "",
         f"capture date           : {field(env, 'captured')}",
         f"repo commit captured at: {field(env, 'repo commit')} ({field(env, 'repo branch')})",
         f"previous capture       : {since[:12] if since else 'none found'}",
         f"previous export        : {since_export[:12] if since_export else 'none found'}",
         f"Sea Power              : {changelog_line}",
         f"  Steam build id       : {buildid}",
         f"  engine               : Unity {unity}", "",
         "COUNTS",
         f"  A Steam-tracked subscriptions : {tracked}",
         f"  B Workshop folders on disk    : {len(b)}",
         f"  C canonical Workshop ids      : {len(c)}",
         f"  D catalog installed entries   : {len(d)}",
         f"  SEST entries in the order     : {len(sest)} ({', '.join(sest)})",
         f"  SEST in the live order        : {sest_live}",
         f"  local SEST folders (StreamingAssets): {sest_local}",
         f"  canonical Mod Manager entries : {len(order)}",
         f"  live Mod Manager entries      : {live_entries.group(1) if live_entries else 'not captured'}",
         f"  pending (NeedsDownload / NeedsUpdate): {pending}", ""]
    L += ["SINCE THE PREVIOUS CAPTURE", "  new folders:"] + listing(b - set(b_then), names)
    L += ["  removed folders:"] + listing(set(b_then) - b, names)
    L += ["  updated on the Workshop (folder date changed - the folder's last-write time, which",
          "  an update that only rewrites files inside existing subfolders does not move; the",
          "  exported files below are the full record):"] + [
        f"  {i}  {names.get(i, '')}  {b_then[i][1]} -> {b_now[i][1]}" for i in updated]
    if not updated:
        L.append("  (none)")
    L += [f"  exported files changed since the previous export "
          f"({since_export[:12] if since_export else 'none'}; A added, D removed, M modified, R renamed):"]
    for i in sorted(exported):
        rows = sorted(exported[i], key=lambda r: ("DARM".index(r[0]) if r[0] in "DARM" else 4, r[1]))
        count = {k: sum(1 for s, _ in rows if s == k) for k in "ADMR"}
        L.append(f"  {i}  {names.get(i, '')}  files {man_then.get(i, {}).get('FilesCopied', '-')} -> "
                 f"{man_now.get(i, {}).get('FilesCopied', '-')}  "
                 f"(A {count['A']}, D {count['D']}, M {count['M']}, R {count['R']})")
        L += [f"      {s} {path}" for s, path in rows[:DETAIL]]
        if len(rows) > DETAIL:
            L.append(f"      ... and {len(rows) - DETAIL} more")
    if not exported:
        L.append("  (none)")
    changed_dlls = sorted(k for k in dll_now if dll_then.get(k) not in (None, dll_now[k]))
    L += ["  plugin DLLs changed:"] + ([f"  [{r}] {p}" for r, p in changed_dlls] if dll_then else
                                      ["  (no earlier plugin-dlls.txt to compare with)"])
    if dll_then and not changed_dlls:
        L.append("  (none)")
    L += ["  plugin DLLs new:"] + ([f"  [{r}] {p}" for r, p in sorted(set(dll_now) - set(dll_then))]
                                  if dll_then else ["  (first capture)"]) + [""]
    L += ["INVENTORY", "  subscribed + downloaded + canonical + catalogued: "
          f"{len(b & c & d)}", "  subscribed but unplaced (B not C):"] + listing(b - c, names)
    L += ["  canonical but not downloaded (C not B):"] + listing(c - b, names)
    L += ["  canonical but not catalogued (C not D):"] + listing(c - d, names)
    L += ["  catalogued installed but not on disk (D not B):"] + listing(d - b, names)
    L += ["  new uncatalogued subscriptions (B not in any catalog entry):"] + listing(b - every_catalogued, names)
    L += [f"  historical catalog entries (status not installed): {len(historical)}",
          f"  Steam-tracked but not on disk: {' '.join(tracked_not_disk) or '(none)'}",
          f"  on disk but not Steam-tracked: {' '.join(disk_not_tracked) or '(none)'}", ""]
    notes = [l for l in NOTES.read_text(encoding="utf-8-sig").splitlines()
             if not l.startswith("#")] if NOTES.is_file() else []
    while notes and not notes[0].strip():
        notes.pop(0)
    L += ["AUTHORS' CHANGE NOTES (data/install-snapshot/workshop-change-notes.txt)"]
    L += [f"  {l}" if l.strip() else "" for l in notes] or [
        "  none recorded (copy them from each item's Steam Change Notes page)"]
    L += ["", "EXPORTER UPDATE CHECK (export-mod-configs.ps1 -CheckUpdates)"]
    L += ["  " + l for l in updates.read_text(encoding="utf-8-sig", errors="replace").splitlines() if l.strip()] \
        if updates.is_file() else ["  not captured (data/install-snapshot/workshop-updates.txt absent)"]
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} (previous capture {since[:12] if since else 'none'})")


if __name__ == "__main__":
    main()
