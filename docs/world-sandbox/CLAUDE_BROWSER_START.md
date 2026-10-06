# Build handoff - persistent world sandbox

Repository: `SEST-HOBBY/Seapower-mods`
Branch: `feature/world-campaign-draft`
Start with every document in `docs/world-sandbox/`.

## The request

Build toward an ongoing world sandbox with persistent mission gameplay, resupplying and multi-phased combat. Prioritise play over story. The first prototype is ONE mission in which the same forces fight, withdraw, replenish and fight again, surviving save/reload. Do not build the superseded WC01-WC03 story/convoy mission chain.

The user uses browser Claude, not local Claude Code. Do repository work in the available development environment. Real Sea Power tests belong on the gaming PC and must be marked pending when that runtime is unavailable.

## Before editing runtime files

Confirm branch, HEAD and baseline divergence. Inspect existing sandbox mission sources, native mission triggers and victory handling, save/load behaviour, campaign helpers, the current SEST/RE-power supply implementations and the winning mod definitions. No blind branch merging, rebase, force-push or default-branch changes.

Produce a small capability/mapping audit with exact file/line references. Separate evidence of ammunition transfer from ship fuel, supplier-restocking, aircraft-stock replenishment and repairs. A search with no results is not proof that the engine cannot do something; an undocumented key is not proof that it can.

Investigate the intended single-mission route first. Native Task Force Mode is a possible tool, not a requirement. Cross-mission variables and a dynamic campaign generator must not be casually presented as a persistent scenario API.

Use the canonical catalog and load order. Resolve unit, variant, squadron, ammunition and system references through winning files, including aliases/extensions. Verify actual source ownership and pending/missing assets. Do not hard-code a historic mod count, fabricate IDs or add unverified requested aircraft/weapons merely because a research report names them.

Select valid mission geography. Inspect an existing working regional sandbox as a spatial starting point where available, without changing it. Separate named real bases from actual installed game objects. Use validated water/land placement and usable aircraft recovery locations.

## First implementation

Create an opt-in prototype in a new namespace, proposed `integration/missions/world_sandbox/`, after checking for collisions. Do not wire it into automatic installation, the consolidated pack or Workshop yet. Inspect all write paths before borrowing a builder so old campaign outputs cannot be overwritten.

Implement a compact live mission with at least two combat opportunities and a real replenishment interval. Keep existing hull identities, damage and magazines; finite opposing forces; valid aircraft support; a finite supplier; and simple neutral activity. Do not finish the mission after the first engagement.

Start with native, attested events and finite preallocated reserves. Dynamic spawning, an external director or runtime plugin is optional and requires evidence, dependency review, save/load testing and approval before it becomes mandatory. Distant or hidden units are not automatically free of performance cost.

Do not reset stocks at a phase boundary or replace the fleet with pristine copies. Do not inherit unlimited port supply unnoticed. Supplier exhaustion, disruption and compatibility failures must be observable. Where port restocking or another service is unproved, expose the limitation and use an honestly finite temporary model rather than a fake economy.

Test and record every relevant item in `gameplay-and-tests.md`. Static tests should cover reference resolution, output isolation, IDs, event links and forbidden automatic resets. Runtime tests must demonstrate actual transfers, continuous combat and save/load behaviour. Do not claim playtesting from generated files.

## Scope and presentation

Minimal briefings: where the force is, usable support, rules of engagement, known contacts and optional tasks. No character/lore package or narrative gating. No AI imagery; reuse authorised assets or use plain functional presentation.

Keep existing campaigns, global unit behaviour, load order and production outputs unchanged. A fix to a shared mechanic should be isolated and reviewed separately, not smuggled into a mission draft.

Commit with professional messages, no AI attribution or co-author trailers. Use this feature branch, not a new `claude/*` branch. Do not publish or merge without approval.

Deliver the audited capability table, smallest useful prototype, actual automated-test results, pending/runtime test card, known limitations, changed paths and commit ID. Then expand to two separated operating areas inside the same persistent mission before widening world coverage. Do not respond by creating dozens of story missions or only an encyclopedia.
