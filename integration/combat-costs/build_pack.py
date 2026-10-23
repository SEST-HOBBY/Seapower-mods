#!/usr/bin/env python3
"""Build data-only Combat Cost Tracker compatibility; never patch its DLL.

    python3 integration/combat-costs/build_pack.py          # the pack, coverage.json and,
                                                            # when SEST_Campaign is built,
                                                            # the cost list
    python3 integration/combat-costs/build_pack.py --list   # the cost list only

The cost list (docs/combat-costs/cost-list.md and .csv) reads SEST_Campaign's
built missions, and SEST_Campaign builds after this pack, so tools/build_all.py
runs --list once every pack is built.
"""
import argparse
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "integration"))
from common.costs import (_build, cost_list, render_catalog, CAMPAIGN, KINDS)  # noqa: E402

HERE = Path(__file__).resolve().parent
OUT = HERE / "SEST_Combat_Costs"
REPORT = ROOT / "docs/combat-costs"


def write(path, text):
    """UTF-8 with LF on every platform: source titles are not all ASCII."""
    path.write_bytes(text.encode("utf-8"))


def inputs():
    return (json.loads((HERE / "mappings.json").read_text(encoding="utf-8")),
            json.loads((HERE / "research.json").read_text(encoding="utf-8")))


def write_list(mappings, research, built=None):
    md, table = cost_list(ROOT, mappings, research, built)
    REPORT.mkdir(parents=True, exist_ok=True)
    write(REPORT / "cost-list.md", md)
    write(REPORT / "cost-list.csv", table)
    print("cost list:", md.count("\n"), "lines,", table.count("\n") - 1, "CSV rows")


def compatibility_text(result):
    lines = ["SEST COMBAT COST COMPATIBILITY", "", "Requires enabled Combat Cost Tracker and Anchor Chain, then a full game restart.",
             "Only cost catalogs are extended; no weapon, aircraft or ship performance changes.",
             "Mapped values copy the tracker's existing USD estimates exactly; they are not new procurement quotes.",
             "SEST researched estimates are SEST's own figures, not the author's: each names its method,",
             "reference/source year and sources below and in the catalog comment above its section.",
             "Source reference years remain the source's years; CurrentYearCost is independent.",
             "Task Force purchase points and ammo_prices.csv scores are never treated as USD.",
             "No global price preference, category visibility, overlay scale or currency is changed.",
             "Native tracking covers expended ammunition, vessels and aircraft; land-platform loss pricing is unsupported.",
             "The full list of SEST's units and their prices is docs/combat-costs/cost-list.md in the SEST repository.", ""]
    for kind, data in result["coverage"].items():
        estimates = sum(1 for e in result["entries"] if e["kind"] == kind and e.get("estimate"))
        lines.append(f"{kind}: {len(result['extensions'][kind])} compatibility entries "
                     f"({estimates} SEST researched estimates); "
                     f"SEST-priced historical/current {data['sest_historical_known']}/{data['sest_current_known']} "
                     f"of {data['sest_eligible']} eligible references.")
    lines += ["", "REVIEWED / NORMALIZED MAPPINGS"]
    for e in result["entries"]:
        if e.get("estimate"):
            continue
        values = ", ".join(k + "=" + (v or "unknown") for k, v in e["fields"].items())
        lines += [f"{e['kind']} {e['target']} <- {e['source'] or 'unknown'}: {values}", "  " + e["basis"]]
    lines += ["", "SEST RESEARCHED ESTIMATES"]
    for e in result["entries"]:
        if not e.get("estimate"):
            continue
        est = e["estimate"]
        values = ", ".join(k + "=" + (v or "unknown") for k, v in e["fields"].items())
        how = []
        for label, year in (("historical", "reference year"), ("current", "source year")):
            how.append(f"{label}: {est[label + '_method']}, {year} {est[label + '_year']}"
                       if est.get(label) else f"{label}: unknown")
        lines += [f"{e['kind']} {e['target']}: {values}", "  " + e["basis"], "  " + "; ".join(how)]
        lines += ["  Source: " + s["title"] + " - " + s["url"] for s in e["sources"]]
    lines += ["", "SEST REFERENCES STILL INCOMPLETE"]
    for kind, data in result["coverage"].items():
        for e in data["unknown"]:
            if e["owner"].startswith("SEST_"):
                modes = "/".join(k for k in ("historical", "current") if e[k + "_unknown"])
                lines.append(f"{kind} {e['id']}: {modes}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--list", action="store_true",
                        help="write only docs/combat-costs/cost-list.md and .csv")
    args = parser.parse_args()
    mappings, research = inputs()
    if args.list:
        write_list(mappings, research)
        return
    built = _build(ROOT, mappings)
    result = built[0]
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "systems").mkdir(parents=True)
    for kind in KINDS:
        write(OUT / "systems" / f"sest_{kind}_costs.ini", render_catalog(kind, result))
    write(OUT / "_info.ini",
          "[Language_en]\nName=SEST Combat Cost Compatibility\n"
          "Description=Catalog spelling, reviewed same-family cost mappings and SEST researched estimates "
          "for Combat Cost Tracker. Author estimates retain their reference basis; SEST estimates name "
          "their method, year and sources; unsupported prices stay unknown.\n\n"
          "[Compatibility]\nApproximateVersion=0.8.7\n")
    REPORT.mkdir(parents=True, exist_ok=True)
    write(REPORT / "coverage.json", json.dumps(result, indent=2) + "\n")
    write(OUT / "COST-COMPATIBILITY.txt", compatibility_text(result))
    for kind, data in result["coverage"].items():
        print(kind, len(result["extensions"][kind]), "new entries;", data["historical_known"], "/", data["eligible"], "historical known")
    if (ROOT / CAMPAIGN / "missions").is_dir() and (ROOT / CAMPAIGN / "campaigns").is_dir():
        write_list(mappings, research, built)
    else:
        print("cost list skipped: SEST_Campaign is not built yet; tools/build_all.py writes it after the campaign")


if __name__ == "__main__":
    main()
