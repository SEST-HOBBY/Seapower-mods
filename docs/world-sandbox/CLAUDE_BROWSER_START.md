# Browser build handoff - populate the world from the research

Repository: `SEST-HOBBY/Seapower-mods`
Branch: `feature/world-campaign-draft`
Read `docs/world-sandbox/WORLD_POPULATION_PLAN.md` first, then the other documents here and the complete original reports at `docs/world-sandbox/research/R01.md`, `R02.md` and `R03.md`. These copies match the SHA-256 digests in `source-manifest.json`; no separate archive or sandbox access is required.

## Governing instruction

Use the research as the outline for constructing a populated world: installations, associated forces, support assets, deployed groups, logistics connections and routine activity in appropriate regions.

The world should support persistent mission gameplay, resupplying and multi-phase combat with minimal story. Do not misread that as a request to substitute a tiny combat/resupply prototype for the researched population work. The first deliverable is the WORLD POPULATION REGISTER AND PLACEMENT PLAN, not WC01-WC03, a narrative campaign or a mechanics-only demo.

## First work package

1. Confirm branch and current HEAD. Inspect the existing catalog, load-order resolver, SEST bases, sandbox mission sources, placement tools and relevant builders without changing published content.
2. Consolidate the three reports into one deduplicated, source-linked node register. Cover their full geographic scope now; regional implementation can follow incrementally. A headquarters, distribution centre, airfield and naval base are different node roles.
3. For each node, list source-described platform families and proposed population categories: resident, deployed, support, patrol, transit and reserve. Label proposed quantities and activity as scenario choices, not sourced current deployments.
4. Resolve these against the winning installed unit/variant/squadron/loadout files and dependencies. Record exact matches, clearly labelled representative proxies, unsupported functions and missing assets. Do not fabricate IDs, assume all advertised mods work or hard-code a historical subscription count.
5. Identify source and in-game location evidence. Author population packages while locations are being validated; do not stall the world outline on a single missing coordinate. Validate every actual placement and route before generating a playable object there.
6. Produce a regional placement overview plus source, mapping and missing-content reports. Give every physical asset one identity and allocation, avoiding duplicate copies at its home base and at sea.

Proposed data/output filenames are implementation choices, not existing files: a world-node register, force-allocation register, connections register and population-gap report. Reuse suitable repository conventions before creating parallel formats.

Preserve collection inventories already under way. Fetch and read the research from the updated draft ref without resetting another working branch or overwriting its results. The missing-source blocker is resolved; complete source extraction and join it to those mappings rather than repeating finished work.

## Then build the environment

Use a new opt-in namespace after checking collisions. Populate bases and forces in regional passes under the same world specification. Add routine patrols, transits, escorts and supported civilian activity, then wire verified services and sustained combat behaviour.

A small test scene is allowed to prove replenishment or save/load in parallel. It is not a gate that prevents authoring the remaining global population plan. Avoid defaulting to native Task Force chapters: the request is a sandbox, not a story progression.

Separate actual ship ammunition transfer, aircraft turnaround, supplier restocking, fuel and repair. Preserve finite resources and surviving-unit state; no automatic phase resets, duplicated reinforcements or invented logistics APIs. Source claims and static configuration do not establish runtime success.

Measure geography, active-unit population, save size, time compression and performance. Distinguish the authored world from tested concurrently active areas; do not promise global streaming or infer impossible scope from an untested assumption.

A single map centre with relative nautical-mile positions describes a coordinate representation; by itself it does not prove a maximum playable extent or require separate theatre missions. That conclusion remains unproven unless supported by an identified engine constraint or reproducible test. Distinguish limits in our conversion/build tools from limits in the game. Record placement and navigation behaviour at increasing offsets, long-distance geometry and coordinate wrapping, terrain availability, active-unit performance and save/reload behaviour. Existing mission extents are examples, not automatically the engine maximum. Keep one coherent populated world as the design target; propose a regional runtime split only against evidence and explain what happens to persistence. Do not promise that a fully active global mission is feasible either. Scope tests run alongside the global register, not instead of it.

## Boundaries and reporting

The user uses browser Claude, not local Claude Code. Perform repository work in the available environment; mark actual Sea Power tests pending when the gaming runtime is unavailable.

Keep existing campaigns, global units, load order, deployables and installers unchanged. Audit borrowed builder write paths. Do not force-push, change the default branch, merge unrelated branches, publish to Workshop or add mandatory plugins without approval. No `claude/*` branches, AI imagery or AI attribution in commits.

Verify precise real-world claims when they matter to the build. Do not turn research uncertainty into a refusal to prepare the outline; unknowns belong in the register. Report separately: source described, independently checked, collection mapped, placed, runtime active and playtested.

Return the populated-world outline and mapping first, then the actual changed files and tests as implementation progresses. Gameplay serves the world being populated; it does not replace that task.
