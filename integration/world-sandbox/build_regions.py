#!/usr/bin/env python3
"""Generate an optional 2028 regional expansion without changing the base campaign.

The original campaign ID and save files remain untouched. All new places,
activities, access permissions and quantities are explicitly scenario choices.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PACK = HERE / "SEST_World_Campaign" / "dynamic_campaigns"
ORIGINAL = PACK / "sest-world-sandbox" / "campaign.json"
SPEC = HERE / "regions-2028.json"
VALIDATOR = HERE / "check_dynamic_campaign.py"
OLD = "ch_ffg_jvh"
NEW = "ch_ffg_jacob_van_heemskerck"


def build(base, cfg):
    """The variant as a dict: the original plus the spec, nothing else."""
    c = cfg["campaign"]
    new = json.loads(json.dumps(base))
    if base["id"] == c["id"]:
        raise ValueError("A region variant may not reuse the original campaign id")
    new["id"], new["name"], new["description"] = c["id"], c["name"], c["description"]
    used_bases = {b["id"] for b in new["bases"]}
    used_forces = {f["name"] for f in new["forces"]}
    original_bases, original_forces = len(new["bases"]), len(new["forces"])
    depots = {b["id"] for b in base["bases"] if b.get("depot")}
    for site in cfg["sites"]:
        b = site["base"]
        if b["id"] in used_bases:
            raise ValueError("duplicate regional base: " + b["id"])
        if b.get("supplyFrom") not in depots:
            raise ValueError("invalid regional supply depot: " + b["id"])
        used_bases.add(b["id"])
        new["bases"].append(b)
        for force in site["forces"]:
            f = dict(force, base=b["id"], side=b["side"])
            if f["name"] in used_forces:
                raise ValueError("duplicate regional force: " + f["name"])
            used_forces.add(f["name"])
            new["forces"].append(f)
    for force in cfg.get("otherForces", []):
        if force["name"] in used_forces or force["base"] not in used_bases:
            raise ValueError("invalid additional force: " + force["name"])
        used_forces.add(force["name"])
        new["forces"].append(force)
    for patrol in cfg.get("patrols", []):
        if patrol["force"] not in used_forces:
            raise ValueError("patrol without force: " + patrol["force"])
        new["patrols"].append(patrol)
    # Regional supply ships join the replenishment table; the original's own
    # figures are never changed, and a cargo force must carry one of them.
    for unit, load in sorted(cfg.get("replenishment", {}).items()):
        if unit in new["replenishment"] and new["replenishment"][unit] != load:
            raise ValueError("regional replenishment would change the original's " + unit)
        new["replenishment"][unit] = load
    for f in new["forces"]:
        if f.get("cargo") and not any(u.split()[0] in new["replenishment"] for u in f["units"]):
            raise ValueError("cargo force without a replenishment ship: " + f["name"])
    # The base campaign was repaired on the same source branch; retain this
    # guard so an older Workshop capture cannot silently reintroduce a blocker.
    if OLD in new["values"]:
        new["values"][NEW] = new["values"].pop(OLD)
    for row in new["catalogue"]:
        if row["unit"] == OLD:
            row["unit"] = NEW
    buy = [r["unit"] for r in new["catalogue"]]
    if OLD in buy or OLD in new["values"] or buy.count(NEW) != 1:
        raise ValueError("Chilean frigate migration missing or duplicated")
    if len(new["bases"]) != original_bases + len(cfg["sites"]):
        raise ValueError("incorrect base count")
    if len(new["forces"]) != original_forces + sum(len(s["forces"]) for s in cfg["sites"]) + len(cfg.get("otherForces", [])):
        raise ValueError("incorrect force count")
    return new


def render(campaign):
    """build_dynamic_campaign.py's serialisation, so both campaigns rebuild byte for byte."""
    return json.dumps(campaign, indent=2, ensure_ascii=True) + "\n"


def main():
    cfg = json.loads(SPEC.read_text(encoding="utf-8"))
    new = build(json.loads(ORIGINAL.read_text(encoding="utf-8")), cfg)
    output = PACK / cfg["campaign"]["folder"] / "campaign.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(new), encoding="utf-8")
    # The same validator used by the base campaign must also accept the variant.
    result = subprocess.run([sys.executable, str(VALIDATOR), str(output)],
                            capture_output=True, text=True)
    if result.returncode:
        raise ValueError(result.stdout + result.stderr)
    print(f"regional preview: {len(new['bases'])} bases; {len(new['forces'])} forces; "
          f"{len(new['patrols'])} patrols; {len(new['catalogue'])} buy entries")


if __name__ == "__main__":
    main()
