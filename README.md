# Seapower-mods

Custom loadouts, upgrade variants, cross-mod fixes and missions for a
**Sea Power: Naval Combat in the Missile Age** install with **137 locally observed
Workshop mods** plus one **SEST Integration Pack** (138 Mod Manager entries).
SEST contains the repository's upgrades; Workshop mods remain separate installations.

**Snapshot review pending:** the supplied 2026-09-16 ZIP contains 170 more files than
its export manifest records. Builds against it are provisional. Obtain a fresh export
before deployment; see [the inventory audit](docs/workshop-inventory-20260916.md).

Everything here is built around interoperability: a mod is known by three names — a
catalog slug (`us-naval-aviation`), a Steam Workshop id (`3737267013`, which names its
`mods-source/` export and its load-order token), and the display name the Mod Manager
shows — and `data/mod-catalog.json` is the table that joins them, including the
`local_packs` registry of the 19 SEST source packs.

## Layout

| Path | Contents |
|---|---|
| `data/mod-catalog.json` | **The registry.** Per mod: slug, `workshop_id`, faction, type, status, dependencies, overlap facts. Plus `local_packs`, the SEST pack roster with build order |
| `data/load-order.tokens.txt` | **The load order.** One token per line; what `set-mod-order.ps1` writes into `usersettings.ini`. The consolidated pack is the single tier-0 entry |
| `data/active-mission.txt` | The mission the tooling works on when you do not name one |
| `data/deploy-missions.txt` | **The keep list.** Which missions the installer ships into the game; everything else stays in the repo only |
| `data/raw-workshop-list.txt` | Historical subscription list from August 2026 |
| `docs/` | Generated catalog and load-order docs, conflict watchlist, design notes, setup runbook |
| `integration/<pack>/` | One SEST pack per topic: a builder plus its generated `SEST_*` output |
| `integration/dist/SEST_Integration/` | **The deployable** — all packs merged by `tools/consolidate_packs.py`; the only thing the installer copies into the game |
| `integration/missions/` | Playable missions and the scripts that refine them |
| `mods-source/` | Supplied local Workshop text configs and their export manifest, plus `_vanilla/`; see the snapshot audit |
| `tools/` | Builders, checkers, generators, and the PowerShell scripts that talk to the game |

## Commands

Linux / repo side:

```bash
python3 tools/check_inventory.py           # folder IDs, catalog, order and manifest integrity
python3 tools/build_all.py --from-scratch   # rebuild all 19 packs + the consolidated dist;
                                            # a clean `git status` after = the regression gate
python3 tools/preflight.py                  # resolve every reference the active mission makes
python3 tools/check_load_order.py           # every SEST override still outranks its target
python3 tools/check_dependencies.py         # every pack's upstreams exported and ordered
python3 tools/check_scenarios.py           # carved scenarios: counts, formations, sections
python3 tools/check_mod_conflicts.py <id>   # what a newly added mod would collide with
python3 tools/generate_catalog.py           # docs/mod-catalog.md      <- data/mod-catalog.json
python3 tools/generate_load_order.py        # load-order docs + preview <- canonical tokens + catalog
```

Gaming PC (PowerShell, from the repo root, `-ExecutionPolicy Bypass` because a default
Windows install refuses unsigned local scripts):

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1        # deploy SEST_Integration
powershell -ExecutionPolicy Bypass -File .\tools\set-mod-order.ps1 -AddMissing # game CLOSED: apply order
powershell -ExecutionPolicy Bypass -File .\tools\export-mod-configs.ps1 -IncludeVanilla  # refresh mods-source/
powershell -ExecutionPolicy Bypass -File .\tools\prune-missions.ps1              # dry run: what the
                                                                                  # mission browser would lose
```

`docs/setup-runbook.md` is the full walkthrough.

## Why one pack

A SEST patch is a whole-file replacement that must sit **above** the mod it patches; if
anything outranks it, the patch silently does nothing. Fifteen separate packs meant
fifteen chances for a reshuffle to break one — which is exactly how a pack once went
inert unnoticed. Consolidated, tier 0 is a single entry and that failure class is gone
by construction. The per-pack sources remain the build units; `tools/consolidate_packs.py`
merges them with hard errors on any conflict (identical files dedupe, language and
systems files merge key-by-key the way the game itself merges them across mods).

## Adding a pack

1. Create `integration/<name>/` with a builder that writes `SEST_<Name>/`.
2. Register it in `local_packs` in `data/mod-catalog.json` (add `build_after` if it reads
   sibling pack output). That alone consolidates it into `SEST_Integration` on the next
   `build_all` and deploys it with the installer — the load order does not change.
3. Loadout-name keys are global across mods: prefix yours (`SEST_...`) or the
   consolidator will fail the build on the first clash — that check exists because two
   unprefixed keys were silently fighting over display strings in-game.
4. `python3 tools/build_all.py --from-scratch`, then the inventory and compatibility
   checks must pass before deployment.
