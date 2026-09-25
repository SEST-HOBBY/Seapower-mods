# Seapower-mods

Custom loadouts, upgrade variants, cross-mod fixes and missions for a
**Sea Power: Naval Combat in the Missile Age** install with **142 Workshop
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
| `docs/campaigns/<campaign>/` | One folder per campaign (`southern-watch/`, `southern-reach/`): the design bible, the build notes — including what the campaign has **not** been shown to do — the play-test card and the procedure that lines the gaming PC up with the branch |
| `integration/<pack>/` | One SEST pack per topic: a builder plus its generated `SEST_*` output |
| `integration/dist/SEST_Integration/` | **The deployable** — all packs merged by `tools/consolidate_packs.py`; the only thing the installer copies into the game |
| `integration/missions/` | Playable missions and the scripts that refine them |
| `integration/campaign/` | **Two native Task Force Mode campaigns in one pack.** *SEST Southern Watch* (twelve main missions, four optional operations, two contingencies, eight dispatches) and *SEST Southern Reach* (two chapters, 25 missions, 19 story pages; its data lives in `southern_reach/`), built so that every enabled mod is reached by something one of them places or prices |
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
python3 tools/check_campaign_coverage.py    # every enabled mod still reached by the campaigns (the pack union)
python3 integration/campaign/build_pack.py --dry-run --campaign southern-reach --only TS09   # one mission through every gate, nothing written
python3 tools/generate_catalog.py           # docs/mod-catalog.md      <- data/mod-catalog.json
python3 tools/generate_load_order.py        # docs/load-order-full.md  <- catalog + tiers
```

Gaming PC (PowerShell, from the repo root, `-ExecutionPolicy Bypass` because a default
Windows install refuses unsigned local scripts):

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\install-sest-packs.ps1        # deploy SEST_Integration + missions
powershell -ExecutionPolicy Bypass -File .\tools\set-mod-order.ps1 -AddMissing # game CLOSED: apply order
powershell -ExecutionPolicy Bypass -File .\tools\export-mod-configs.ps1 -IncludeVanilla  # refresh mods-source/
```

Missions install add-and-overwrite with no backup copies, so import anything edited in
game first (`tools\import-mission.ps1`); `install-sest-packs.ps1 -PurgeBackups` clears the
old `* backup-*.ini` copies out of the game once. The exporter mirrors deletions inside each
mod, so a file an author removed leaves `mods-source/` too: review its deletions in
`git status` before committing.

`docs/setup-runbook.md` is the full walkthrough.

## The campaigns

`integration/campaign/` builds two campaigns into one `SEST_Campaign` pack. The
first is **SEST Southern Watch — The Northern Lifeline**:
twelve connected missions in October–November 2028 in which Australia and its
regional partners keep the northern sea routes open, four optional operations
and two contingencies that the core reads back, plus eight dispatches
(allied rotations, an opposing-force passage, a weapons range, an openly
speculative 2034 branch and a 1988 exercise). `docs/campaigns/southern-watch/`
holds the design bible it was built from and the build notes.

The second is **SEST Southern Reach — Tasman Shield**: 25 missions in two
chapters, December 2028 to March 2029. *Southern Reach* (SR01–SR12) escorts the
Antarctic resupply season from Storm Bay to the ice edge at 60°S against a
"fisheries protection" group and a Russian boat; *Tasman Shield* (TS01–TS12,
with an optional pair) fights the same group through Fiordland, Cook Strait,
the Tasman, Bass Strait and the Bight to a ceasefire. Eighteen campaign
variables carry the consequences forward — a boat sunk under the Tasman is
absent from the Southern Convoy, an approach not held reinforces the group off
Sydney. Every position was proved against a Natural Earth coastline
(`integration/campaign/geo/`), because nothing in this repo had sailed that
water before. `docs/campaigns/southern-reach/` holds its bible, build notes,
test card and the review that was run on it before it was committed.

Both run on the game's **native Task Force Mode**, the same system the stock
Pacific Strike campaign uses: you requisition a task force from a priced
roster (`player_task_force_roster.ini`), and losses, damage, magazines and
crew experience carry forward. Every key was read out of the exported stock
campaign before it was used, and every price is checked against the variant or
squadron the winning file actually offers — a price naming a fit the hull no
longer has fails the build. None of the economy has been exercised in game;
each campaign's `build-notes.md` says so in detail.

Its point is coverage. 142 subscriptions are a lot of content to own and never
see, so the campaigns are built so that **every mod in the canonical load
order, and every SEST pack, is reached by something one of them places** — and
"reached" is
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

## Keeping the gaming PC in line

The PC deploys from the branch `data/deploy-branch.txt` names; `sync-sest.ps1`
refuses any other. The whole update loop is one command with the game closed:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\sync-sest.ps1
```

It pulls, builds nothing (the committed packs are the builders' own output),
copies `integration\dist\SEST_Integration` into StreamingAssets, rewrites the
load order, and hashes every deployed file back against the commit. The
step-by-step, with what each line of its output means and how to bring another
session's branch in first, is `docs/campaigns/southern-reach/install-alignment.md`.

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
