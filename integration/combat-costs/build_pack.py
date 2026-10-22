#!/usr/bin/env python3
"""Build data-only Combat Cost Tracker compatibility; never patch its DLL."""
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "integration"))
from common.costs import build, render_catalog, KINDS  # noqa: E402

OUT = Path(__file__).resolve().parent / "SEST_Combat_Costs"


def main():
    mappings = json.loads((Path(__file__).parent / "mappings.json").read_text())
    result = build(ROOT, mappings)
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "systems").mkdir(parents=True)
    for kind in KINDS:
        (OUT / "systems" / f"sest_{kind}_costs.ini").write_text(render_catalog(kind, result))
    (OUT / "_info.ini").write_text(
        "[Language_en]\nName=SEST Combat Cost Compatibility\n"
        "Description=Catalog spelling and reviewed same-family cost mappings for Combat Cost Tracker. "
        "Author estimates retain their reference basis; unsupported prices stay unknown.\n\n"
        "[Compatibility]\nApproximateVersion=0.8.7\n")
    report = ROOT / "docs/combat-costs"
    report.mkdir(parents=True, exist_ok=True)
    (report / "coverage.json").write_text(json.dumps(result, indent=2) + "\n")
    lines = ["SEST COMBAT COST COMPATIBILITY", "", "Requires enabled Combat Cost Tracker and Anchor Chain, then a full game restart.",
             "Only cost catalogs are extended; no weapon, aircraft or ship performance changes.",
             "Values are the tracker's existing USD estimates, not new procurement quotes.",
             "Source reference years remain the source's years; CurrentYearCost is independent.",
             "Task Force purchase points and ammo_prices.csv scores are never treated as USD.",
             "No global price preference, category visibility, overlay scale or currency is changed.",
             "Native tracking covers expended ammunition, vessels and aircraft; land-platform loss pricing is unsupported.", ""]
    for kind, data in result["coverage"].items():
        lines.append(f"{kind}: {len(result['extensions'][kind])} compatibility entries; "
                     f"SEST-priced historical/current {data['sest_historical_known']}/{data['sest_current_known']} "
                     f"of {data['sest_eligible']} eligible references.")
    lines += ["", "REVIEWED / NORMALIZED MAPPINGS"]
    for e in result["entries"]:
        values = ", ".join(k + "=" + (v or "unknown") for k, v in e["fields"].items())
        lines += [f"{e['kind']} {e['target']} <- {e['source'] or 'unknown'}: {values}", "  " + e["basis"]]
    lines += ["", "SEST REFERENCES STILL INCOMPLETE"]
    for kind, data in result["coverage"].items():
        for e in data["unknown"]:
            if e["owner"].startswith("SEST_"):
                modes = "/".join(k for k in ("historical", "current") if e[k + "_unknown"])
                lines.append(f"{kind} {e['id']}: {modes}")
    (OUT / "COST-COMPATIBILITY.txt").write_text("\n".join(lines) + "\n")
    for kind, data in result["coverage"].items():
        print(kind, len(result["extensions"][kind]), "new entries;", data["historical_known"], "/", data["eligible"], "historical known")


if __name__ == "__main__":
    main()
