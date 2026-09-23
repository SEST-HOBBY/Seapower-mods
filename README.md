# Seapower-mods

Custom loadouts, upgrade variants, cross-mod fixes and missions for a
**Sea Power: Naval Combat in the Missile Age** install with **128 active Workshop
subscriptions** — all shipped as one deployable mod, the **SEST Integration Pack**.

Everything here is built around interoperability: a mod is known by three names — a
catalog slug (`us-naval-aviation`), a Steam Workshop id (`3737267013`, which names its
`mods-source/` export and its load-order token), and the display name the Mod Manager
shows — and `data/mod-catalog.json` is the table that joins them, including the
`local_packs` registry of the 17 SEST source packs.

## Layout

| Path | Contents |
|---|---|
| `data/mod-catalog.json` | **The registry.** Per mod: slug, `workshop_id`, faction, type, status, dependencies, overlap facts. Plus `local_packs`, the SEST pack roster with build order |
| `data/load-order.tokens.txt` | **The load order.** One token per line; what `set-mod-order.ps1` writes into `usersettings.ini`. The consolidated pack is the single tier-0 entry |
| `data/active-mission.txt` | The mission the tooling works on when you do not name one |
| `data/raw-workshop-list.txt` | The raw subscription list (source of record) |
| `docs/` | Generated catalog and load-order docs, conflict watchlist, design notes, setup runbook |
| `docs/campaigns/southern-watch/` | The campaign bible and its build notes — including what the campaign has **not** been shown to do |
| `integration/<pack>/` | One SEST pack per topic: a builder plus its generated `SEST_*` output |
| `integration/dist/SEST_Integration/` | **The deployable** — all packs merged by `tools/consolidate_packs.py`; the only thing the installer copies into the game |
| `integration/missions/` | Playable missions and the scripts that refine them |
| `integration/campaign/` | **SEST Southern Watch** — a native Task Force Mode campaign (twelve main missions, four optional operations, two contingencies) plus eight dispatches, built so that every enabled mod is reached by something it places or prices |
| `mods-source/` | Byte-faithful export of every subscribed mod's text configs, plus `_vanilla/` |
| `tools/` | Builders, checkers, generators, and the PowerShell scripts that talk to the game |

## Commands

Linux / repo side:

```bash
python3 tools/build_all.py --from-scratch   # rebuild all 17 packs + the consolidated dist;
                                            # a clean `git status` after = the regression gate
python3 tools/preflight.py                  # resolve every reference the active mission makes
python3 tools/check_load_order.py           # every SEST override still outranks its target
python3 tools/check_dependencies.py         # every pack's upstreams exported and ordered
python3 tools/check_mod_conflicts.py <id>   # what a newly added mod would collide with
python3 tools/check_campaign_coverage.py    # every enabled mod still reached by the campaign
python3 tools/generate_catalog.py           # docs/mod-catalog.md      <- data/mod-catalog.json
python3 tools/generate_load_order.py        # docs/load-order-full.md  <- catalog + tiers
```

Gaming PC (PowerShell, from the repo root, `-ExecutionPolicy Bypass` because a default
Windows install refuses unsigned local scripts):

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1        # deploy SEST_Integration
powershell -ExecutionPolicy Bypass -File .\tools\set-mod-order.ps1 -AddMissing # game CLOSED: apply order
powershell -ExecutionPolicy Bypass -File .\tools\export-mod-configs.ps1 -IncludeVanilla  # refresh mods-source/
```

`docs/setup-runbook.md` is the full walkthrough.

## The campaign

`integration/campaign/` builds **SEST Southern Watch — The Northern Lifeline**:
twelve connected missions in October–November 2028 in which Australia and its
regional partners keep the northern sea routes open, four optional operations
and two contingencies that the core reads back, plus eight dispatches
(allied rotations, an opposing-force passage, a weapons range, an openly
speculative 2034 branch and a 1988 exercise). `docs/campaigns/southern-watch/`
holds the design bible it was built from and the build notes.

It runs on the game's **native Task Force Mode**, the same system the stock
Pacific Strike campaign uses: you requisition a task force from a priced
roster (`player_task_force_roster.ini`), and losses, damage, magazines and
crew experience carry forward. Every key was read out of the exported stock
campaign before it was used, and every price is checked against the variant or
squadron the winning file actually offers — a price naming a fit the hull no
longer has fails the build. None of the economy has been exercised in game;
`docs/campaigns/southern-watch/build-notes.md` says so in detail.

Its point is coverage. 128 subscriptions are a lot of content to own and never
see, so the campaign is built so that **every mod in the canonical load order,
and every SEST pack, is reached by something it places** — and "reached" is
computed the way the game resolves files, not from the folder list:

| class | what it means |
|---|---|
| `unit` | the mod's copy of the placed unit's file wins the load order |
| `variant` / `squadron` | it wins the `_variants` / `_squadrons` file the mission names |
| `store` | it wins an ammunition file the placed unit's chosen loadout hangs |
| `roster` | the requisition roster prices it, so the player can buy it |
| `library` | it wins nothing a mission can name — UI, effects, a bare dependency marker — and applies install-wide |
| `shadowed` | everything it ships is outranked; nothing it contains can load |

`docs/campaign-coverage.md` is the generated table, one row per mod.
`tools/check_campaign_coverage.py` re-derives the whole thing from the **built**
mission files, so it keeps telling the truth after a mod update the builder's
roster has not caught up with. Positions are never invented: every sea and land
station snaps to a point some already-loading mission put a unit of that kind
on. What none of this proves — that the missions load, that helicopters
recover, that replenishment transfers anything — is listed in
`docs/campaigns/southern-watch/build-notes.md`.

## Why one pack

A SEST patch is a whole-file replacement that must sit **above** the mod it patches; if
anything outranks it, the patch silently does nothing. Separate packs meant
one chance per pack for a reshuffle to break one — which is exactly how a pack once went
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
4. `python3 tools/build_all.py --from-scratch` then the four checkers must be green.
