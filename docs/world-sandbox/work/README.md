# World sandbox working evidence

Status: WORKING DATA. Produced on 6-7 October 2026 against `feature/world-campaign-draft` at `50cad91b` by review workflows (several agents, each followed by a skeptic that re-checked its output). Nothing here changes a campaign, unit, pack, load order or installer, and nothing was run in game.

These files are the inputs to the world-population register (`../WORLD_POPULATION_REGISTER.md`, in progress). They are kept so the register can be rebuilt and checked, not as finished documents.

| File | What it is | State |
|---|---|---|
| `source-register.json` | Every place-specific claim in R01-R03 with report and line (R01 97, R02 81, R03 196), consolidated into 69 world nodes, 37 named sea areas and routes, and a 26-item expansion backlog. Includes the source-fidelity checks. | Fidelity checked for all 69 nodes; the checks list the problems and missing claims the register applies. |
| `collection-inventory.json` | Six inventories of the winning unit files: US Navy / USMC / MSC; USAF, Army and fixed land systems; China; Russia; allies and host nations; installations, placement, supply and civilian traffic. Each mapping is labelled exact, proxy, missing_fit or none and gives its winning source. | Each inventory has a skeptic's `verify` block (corrections and missed assets). Apply the corrections before using an id. |
| `scope-and-performance.md` | Evidence on map extent, distant placement and performance. Every claim is tagged GAME (engine or stock data), BUILDER (SEST tooling) or UNMEASURED. | Complete. |
| `scope-probes.md` | In-game probe missions to measure what the repo cannot: distant placement, a two-region mission, the date line and high latitudes, unit-count steps, idle airbases, and save/load of damage, magazines and supply stock. | Design only; not built or run. |
| `scope-evidence.json` | The 75 individual findings behind the scope report. | Complete. |
| `scripts/` | The small scripts the scope report cites (`savespread.py`, `maxz.py`, `near.py`). | As used. |

Source claims record what a report says, with its line; repetition across reports is not corroboration. A mapping records that a unit file wins the load order and suits a role; it does not establish placement, runtime behaviour or playtest results.
