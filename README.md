# Seapower-mods

Working repo for custom loadouts, upgrade variants, and cross-mod integration for a **Sea Power: Naval Combat in the Missile Age** install with **109 Workshop mods**.

## What's here

| Path | Contents |
|---|---|
| `data/raw-workshop-list.txt` | The raw subscription list (source of record, pasted 2026-08-23) |
| `data/mod-catalog.json` | Machine-readable catalog: faction, type, status, dependencies, load-order and overlap facts per mod |
| `docs/mod-catalog.md` | Human-readable catalog grouped by faction (generated — edit the JSON instead) |
| `docs/conflicts-and-load-order.md` | Deprecated-mod cleanup list, missing-dependency audit, conflict watchlist, recommended mod order, integration roadmap |
| `tools/generate_catalog.py` | Regenerates `docs/mod-catalog.md` from the JSON |
| `tools/export-mod-configs.ps1` | Run on the gaming PC: auto-finds the Sea Power install, copies each mod's text configs (INI/JSON/TXT…) into `mods-source/` — no heavy binaries |
| `mods-source/` *(not yet populated)* | The actual mod config files, once exported |

## Workflow

1. **Catalog & analysis** ✅ — done from the subscription list.
2. **Get real files in** — on the gaming PC, run `tools\export-mod-configs.ps1` in PowerShell from the repo root (add `-IncludeVanilla` to also capture the base game's unit/weapon definitions — recommended), then commit and push `mods-source/`.
3. **Conflict scan** — with files present: index every INI section, find duplicate unit/weapon IDs and colliding overrides.
4. **Build** — compatibility patches (F-35C Alt. Loadouts and Murder Hornet vs. Modern US Navy first), then custom loadouts and upgrade variants, shipped as one integration pack.

## Regenerating the catalog

```bash
python3 tools/generate_catalog.py
```
