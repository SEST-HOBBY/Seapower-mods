#!/usr/bin/env python3
"""Parse the measured derivation list out of the shipped CREDITS.txt -> credits_rows.json."""
import json, re
from pathlib import Path
S = Path(__file__).resolve().parent
t = Path("/home/claude/Seapower-mods/integration/dist/SEST_Integration/CREDITS.txt").read_text(encoding="utf-8")
sec = t.split("this list is what it patches.")[1].split("If you are the author")[0]
items, cur = {}, None
for l in sec.splitlines():
    m = re.match(r"^  (\S.*?)  \(workshop (\d+)(.*)\)$", l)
    if m:
        cur = m.group(2); items[cur] = {"title": m.group(1), "files": []}; continue
    m = re.match(r"^\s+(\d+)%\s+(\S+)(?: from (\S+))?$", l)
    if m and cur:
        items[cur]["files"].append((m.group(2), int(m.group(1)), m.group(3)))
print(len(items), "items,", sum(len(v["files"]) for v in items.values()), "files")
(S / "credits_rows.json").write_text(json.dumps(items, indent=1, ensure_ascii=False))
