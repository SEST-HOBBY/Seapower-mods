# SEST World Sandbox - Dynamic Campaign Mod review

Prepared 10 October 2026 (Australia/Sydney). Read-only review of user-supplied files.

## Assessment

Treat this mod as the first candidate strategic runtime for the researched SEST world, not merely as another scenario to borrow from. The uploaded assembly contains a strategic simulation, a persistent state model, save/load infrastructure, and a bridge that generates tactical Sea Power encounters and reads their results back. The next useful decision is whether SEST can be a separate campaign data pack using that engine, before creating a competing engine or modifying the DLL.

The user's research still determines what populates the world: installations, roles, associated forces, logistics relationships and regional activity. The sample's fictional 1985 conquests and force assignments are not a replacement for R01-R03 or for collection mapping.

Important distinction: a persistent strategic world with generated tactical encounters is not the same product as one continuously active, worldwide tactical mission. This binary supports the former architecture in code. This review does not demonstrate the latter, global streaming, or successful full-globe performance. Choosing the former must not be disguised as proving the latter impossible.

## 1. Scope and evidence

The target DLL was not executed, installed, patched or uploaded to a public scanning service. No repository file, branch, load order, Workshop item or deployment was changed.

A custom standard-library PE/CLI metadata reader and CIL instruction decoder was used. This is not a C# decompilation with ILSpy, a source rebuild, a game playtest or a complete security assessment. Generic signatures can remain hexadecimal TypeSpec entries; exception-handler tables are not reconstructed. Zero decoding errors does not establish semantic correctness or compatibility.

The main evidence files are `dll-evidence.json`, `selected-evidence.il.txt` and `campaign-audit.json`. Method tokens below identify the supplied binary, not every release. The original textual inputs are in `reference-inputs/`. The DLL is deliberately not redistributed in this bundle.

### Uploaded binary identity

- SHA-256: `0047b9e6429a1dcf6ae3a393725c8f928ad1b22014d7dbe05f019949715cd4a3`
- Size: 2,717,184 bytes.
- Assembly version: `0.24.0.0`.
- AnchorChain plugin ID: `dynamiccampaignmod`; plugin version: `0.24.0`.
- Informational version: `0.24.0+d02ba54286f5e35ab17e1df098da3d8fb0e25e6e`. The suffix is embedded build metadata, not a verified publicly accessible source commit.
- Target framework: `.NET Standard 2.1`.
- Metadata: 1,773 type definitions, 9,813 method definitions, 9,796 method bodies, 21 embedded resources. Generated closures and state machines are included in those counts.
- All method bodies were instruction-decoded without an unsupported-opcode or method-length error.
- References include AnchorChain, BepInEx, 0Harmony, Seapower-Scripts, Noesis.NoesisGUI, UniRx, Newtonsoft.Json and Unity assemblies.

The supplied `_info.ini`, lines 1-7, labels the mod Alpha, names BepInEx and AnchorChain as requirements, and declares game compatibility `>=0.8.3` and `<0.9.0`. These are declared requirements, not proof that every build in that interval or the SEST collection works. This review concerns the uploaded version, not an independently established latest release.

## 2. What the campaign data contains

`campaign.json` describes Bungalow's Dynamic Campaign Pacific 1985, ID `bungalow.east_asia_1985`.

| Static content | Count |
|---|---:|
| Bases | 61: 27 NavalBase, 27 AirBase, 7 Port |
| Initial forces | 83: 55 Surface, 28 Air |
| Expanded initial unit specifications | 346 |
| Requisition catalogue entries | 130 |
| Unit-value entries | 157 |
| Patrol definitions | 13 |
| Opening invasion definitions | 2 |
| Merchant shipping lanes | 31 |
| Civilian airways | 19: 10 active, 9 suspended |

The 346 figure expands the sample's `xN` unit notation only. It excludes generated carrier air wings, garrisons, traffic and reinforcements, and is not a measured count of concurrently active tactical objects. `Surface` is used for sea forces, including submarines; do not invent a replacement type just because a force consists of submarines.

The scoped reference audit found no duplicate base IDs, force names or catalogue unit IDs; no missing base/port/supplyFrom references; no mismatched initial force/home sides; no missing patrol/invasion references; no missing values for initial or catalogue unit IDs; and no base anchor outside the authored rectangle. These checks do not validate installed game assets, variant/loadout resolution, terrain, every schema rule, balance or real-world accuracy.

Useful patterns include separate Guam naval and Andersen aviation nodes (lines 25-28), home base versus initial deployed `at` positions (137-175), class-specific supply capacities (336-343), and traffic that is separate from military convoys (572-669). The named Midway uses a Kitty Hawk unit definition (138-140): this is an example of a labelled proxy, not an exact-class mapping.

## 3. Reconstructed architecture

### Campaign discovery and loading

`CampaignMenuPatch.Postfix` (`0x06000949`) calls the game's file manager for directories under `dynamic_campaigns`. Its file predicate (`0x0600165c`) looks for a path ending in `campaign.json`. It passes the result to `CampaignDefinition.Load` (`0x060010c4`), which deserializes the JSON and calls `Validate` (`0x060010c5`). It then adds campaign menu entries.

Practical inference: a separate SEST-owned campaign directory and ID may be sufficient to introduce the researched world without a binary fork. A candidate layout is `dynamic_campaigns/sest-world-sandbox/campaign.json`; that is a proposal, not a created file or a proven public extension contract. Check the author-supported schema, effective file-manager resolution, campaign ID handling, menu discovery and version compatibility first.

The validator covers IDs, bounds, sides, bases, force specifications, links, patrols, capacities and other structural constraints. It accepts at least two declared sides; this does not prove complete multi-coalition diplomacy throughout simulation and battle conversion.

### Strategic world and simulation

`CampaignSession.Start` (`0x060008fb`) establishes catalog/state/simulation objects and checks unknown units. `CampaignSim.StepTo` (`0x06000d01`) calls systems for economy, shipyards, fuel burn, supply, replenishment, airlifts, air operations, carrier operations, movement, invasions, detection, enemy AI, alerts, reliefs and victory checks.

These calls establish real implementation paths, rather than configuration fields with no consumer. They do not independently establish correctness of every subsystem. The internal `Admiralty` class is part of this DLL and should not be confused with a separate Workshop mod of a similar name.

### Tactical encounter bridge

`TriassicCampaignFiles.Write` (`0x06000933`) creates native campaign scaffolding while disabling native background traffic. `MissionWriter.Text` (`0x06000a37`) emits native tactical mission settings and an environment map centre. `MissionWriter.WriteUnit` (`0x06000a41`) emits unit data including `GeoPosition=`, variants, loadouts, campaign tags and home-base information. `BattleSession.Launch` (`0x06000994`) loads the encounter.

On exit, `BattleSession.OnDebriefExit` (`0x06000a2c`) gathers results including survivors/losses, ammunition information, positions, aircraft and damage-related data. `BattleExit.Leave` (`0x06000bf0`) and `Battles.Apply` (`0x06000ccf`) reconcile results into the strategic state.

Thus a useful conceptual flow is:

`World definition -> persistent strategic simulation -> selected tactical encounter -> result reconciliation -> same strategic world`.

This is not a scripted WC01/WC02/WC03 story progression. It also does not mean every base or fleet in the strategic registry exists as a fully simulated 3D unit at all times.

## 4. Persistence: strong starting point, exact coverage still matters

`CampaignState` records fleets, squadrons, flights, base ownership, stocks, production/build orders, points, intelligence, pending engagements and identifiers. `Hull` includes ID, unit/variant/name, fuel, ammunition, damage, home, wing, launch/recovery data and cargo. `BaseStock` separates ship fuel, jet fuel and ammunition. `Airframe` records identity, status and a timing field.

`CampaignSave.Write/Read` (`0x06000a71`, `0x06000a76`) serialize campaign state; `Saves.Save/Load` (`0x06000924`, `0x06000925`) connect this to gameplay. Save headers identify campaign, format, mod version and timestamps. `Files.WriteSafely` (`0x0600091c`) uses a temporary file and a replace/move path. `StateInvariants.Check` (`0x06000ad2`) includes checks for duplicate identities and inconsistent ownership/state.

Important limitations to test:

- The inspected main-unit writer explicitly emits `CrewSkill=Trained`. Do not promise accumulated crew experience is preserved without tracing an actual persisted skill/experience mechanism.
- A stored `Damage` value is not proof that every damaged radar, launcher, propulsion component, fire or flooding state persists identically.
- The debrief code contains an error path that logs failure to read battle results and continues without that result. Another fallback points the player to a pre-battle autosave. These paths deserve tests for rollback, duplication and discarded losses.
- Test save/reload with aircraft airborne, units recovering, replenishment in progress, a supplier sunk and a pending encounter, not only a quiet map save.

## 5. Logistics: the highest-priority SEST integration boundary

The sample explicitly defines three replenishment ship classes and one tanker class. Those are plugin campaign capacities, not automatically the same as native tactical supply systems or SEST's supply-category tuning.

`Logistics.Update` (`0x06000e32`) calls repair/replenishment/loading routines. `Logistics.ReplenishAtSea` (`0x06000e35`) requires a valid target task force at sea and checks a distance of 5 nautical miles before passing supplier cargo to `SupplyShips` (`0x06000e38`). The routine mutates campaign cargo and receiver state. Treat that distance as a strategic abstraction, not as a claim about real replenishment distance or a replacement for SEST's alongside mechanics.

SEST's current player guide describes a different tactical mechanism, with supplier-specific distance/speed constraints, size ceilings and finite holds. The research goal is consistent with both, but the inventories must be reconciled explicitly. Supply-class categories such as AntiShip, LandAttack and Torpedo in this plugin are not interchangeable names for native `SupplyCategory` or SEST-prefixed categories.

### Specific accounting risk

`BattleSession.Fired` (`0x06000a23`) compares remembered starting ammunition with current ammunition, records positive differences and combines them with `FiredBefore` data. This is a reason to inspect native resupply interactions, not proof of an exploit.

Test case: start with 20 missiles; fire 10; receive 10 from a supplier; finish with 20. A simple net-stock comparison is zero. Verify where the transfer is captured, whether supplier cargo decreases once, whether firing remains charged correctly, and whether both states survive debrief and reload. Existing `FiredBefore` or other bridge paths may handle part of this; trace them before diagnosing a defect.

Required accounting invariant: opening stocks plus authorized deliveries/production minus consumption/losses must equal closing stocks, after accounting for cargo in transit. Moving ammunition between ships is not new production.

Also inspect category/weight conversion, non-magazine launchers, date-dependent rounds, separate ship/aviation stocks and the definition of repair/refuel services at ports. `ShipStores.Resolve` (`0x060008bc`) already handles `DateBased_` tokens; do not classify them as missing ammunition merely from their spelling.

## 6. Modernization does not stop at replacing 1985 unit IDs

The strategic detection model is visibly role-based. `Detection.ShipSensors` and `FlightSensors` choose `SensorProfile` values; the profile initializer (`0x0600101e`) sets presets. Examples, in the constructor order surface/air/subsurface nautical miles, are:

| Profile | Surface | Air | Subsurface |
|---|---:|---:|---:|
| Ship | 70 | 150 | 20 |
| ASW ship | 70 | 150 | 50 |
| AEW aircraft | 200 | 200 | 0 |
| ASW aircraft | 100 | 100 | 50 |
| Carrier | 200 | 200 | 50 |

These are strategic profile values, not guaranteed detection or the full tactical sensor solution. Adding a correct modern aircraft model does not by itself establish realistic strategic radar reach, low-observable effects, emissions, electronic warfare, track ageing or information sharing. Review the strategic abstraction separately from tactical INI fidelity.

Other adaptation questions include loadout/weapon classification, named-hull fallback, modern air-wing composition, sortie generation, support eligibility, economic values and shipyard availability. The JSON's tiers, prices and build days are game design data, not a factual procurement or ship-construction model.

## 7. Global geography and neutrality

The sample rectangle spans latitude -47 to 62 and longitude 90 to 210. Pearl Harbor uses 202.05 rather than -157.95; Midway similarly lies beyond 180. `GeoBounds.Continuous` (`0x060010ce`) selects an equivalent longitude near the bounds midpoint. `GameGeo.FromGame` and `MissionWriter.GameLon` bridge geographic conventions. Navigation classes include water/depth checks and path-search code.

This is positive evidence for broad geographic authoring and a dateline-crossing theatre. It is not evidence that extending the rectangle to the whole Earth will work unchanged. Test the 0/360 and -180/180 seams, high latitudes, straits, harbour approaches, land avoidance, navigation-grid cost, strategic update time, save size and encounter size.

Keep world authoring partitions separate from runtime restrictions: organise the register regionally, but do not turn that organisation into disconnected scenarios without evidence and a design decision.

The two-side sample, its red `comingSoon` flag, conquest-oriented opening and tactical Taskforce1/Taskforce2 conversion do not establish arbitrary diplomacy. Keep host, operator, access permission and combat coalition separate in the SEST registry, particularly for the Djibouti cluster. Trace ownership, targeting, capture and victory logic before attempting neutral installations or more than two combat alignments. Removing story paragraphs alone does not remove conquest/victory assumptions.

## 8. Other material to review, in priority order

1. **Upstream Dynamic Campaign author documentation/source and another campaign definition using the same engine.** Confirm supported custom-campaign discovery, schema/versioning, neutral/free-play possibilities, modern-unit assumptions, source availability and permission before any copied implementation. The uploaded files contain no source licence. The primary Workshop search identifies Bungalow's item as 3813157776, but a complete current author page/source package was not retrieved in this review.
2. **The exact installed `Seapower-Scripts.dll`, dependency versions, generated mission and before/after saves.** These are the most useful next technical artifacts. Follow the actual methods patched by this DLL, not a generic assumption that Unity's game assembly must be named Assembly-CSharp. Inspect owned local copies; do not put game binaries in the public repo.
3. **AnchorChain, BepInEx and Harmony lifecycle/patch handling.** Audit init/unload, save/load, scene/menu transitions, patch owner IDs and patches touching the same methods. INI load order is not a substitute for a method-level patch-conflict analysis.
4. **SEST Replenishment and RE-power (3605013271).** Review campaign-to-tactical inventory ownership and debit/credit rules before enabling both layers together. The current SEST implementation is a more relevant reference than treating stock RE-power as a complete modern support solution.
5. **Flight Deck Ops (3373960386), plus only the variant appropriate to the winning carrier definitions.** The author documents elevator, taxi, launch/recovery changes. Audit compatibility with carrier airframe IDs, deck queues, launch/recovery results and persistent losses. Some historical features are already native, so do not revive obsolete overrides blindly.
6. **Native Pacific Strike Task Force campaign/save/dynamic-generation mechanisms.** The repo's stock campaign contains `DynamicGenerationPersistent=True`; the existing builder uses an enemy-theatre roster. Compare native persistence with the plugin bridge and avoid running two competing strategic owners. This is a reference, not a request to convert the world into story chapters.
7. **AI Doctrine Overhaul (3654230227), as a comparison/conflict review only.** Its author describes changes to strike scheduling, concurrency and target handling. Compare these with the plugin's CampaignAI, CarrierAir and AirOperations before even considering enabling it. This is not a recommendation to resubscribe or add it as a dependency.
8. **Automatic SAR (3774105087), as an optional sustained-operations feature.** Its author describes rescue tasking for helicopters/ships/submarines and helicopter return when full. Establish whether rescues affect the strategic personnel/experience/economy model; do not assume that a tactical rescue automatically persists as recovered crews.

For deep follow-up decompilation use ILSpy/ilspycmd against matching references or inspect author-provided source. ILSpy was not used in this review. A proper decompiler improves navigation; it does not replace runtime verification.

## 9. Recommended build direction

Keep the research register engine-neutral. Separate world nodes, force identities, allocation, logistics links and activity from a generated engine-specific campaign definition. Add an adapter to Dynamic Campaign's JSON only after resolving its schema and extension boundary. Use real winning collection IDs and source provenance, with explicit exact/proxy/missing-fit/none outcomes.

Prefer a data-only integration if it can meet the requirements. If a small adapter is necessary for modern sensors or resupply reconciliation, define that narrow scope rather than immediately forking the entire engine. A one-continuous-tactical-world mode remains a separate, unproven engineering path.

Do the global population register and collection mapping now. In parallel, use a small controlled encounter as a validation fixture for inventory and save/load, not as a replacement for the researched world. Do not delay all global authoring until one harbour or mechanics experiment passes.

Acceptance tests: menu discovery and unknown-unit rejection; both sides' losses; no duplicate hull/airframe identity; interrupted/reloaded battle; flight recovery; tactical and strategic replenishment; supplier depletion/loss; damaged equipment persistence; neutral contacts; dateline transit; larger populations; and plugin updates against existing saves.

## 10. Public and repository references

These are author/official sources or the user's repo. They identify reference material, not a completed compatibility certification. Some Steam pages returned inconsistent cached dates/banners, so installation availability/latest-version claims are deliberately omitted.

- AnchorChain official repository: https://github.com/SeaPower-Modders/AnchorChain
- Harmony patching documentation: https://harmony.pardeike.net/articles/patching.html
- BepInEx development guide: https://docs.bepinex.dev/articles/dev_guide/plugin_tutorial/index.html
- ILSpy official project: https://github.com/icsharpcode/ILSpy
- RE-power author page: https://steamcommunity.com/sharedfiles/filedetails/?id=3605013271
- Flight Deck Ops author page: https://steamcommunity.com/sharedfiles/filedetails/?id=3373960386
- AI Doctrine Overhaul author page: https://steamcommunity.com/sharedfiles/filedetails/?id=3654230227
- Automatic SAR author page: https://steamcommunity.com/sharedfiles/filedetails/?id=3774105087
- Bungalow's Dynamic Campaign Mod primary search result: https://steamcommunity.com/sharedfiles/filedetails/?id=3813157776&l=thai
- SEST `docs/replenishment-in-play.md`, current fetched blob `5b6d09d60af088eda98dbbefd055dab4edd5cc23`.
- SEST stock `mods-source/_vanilla/original/campaigns/pacific-strike-task-force/campaign.ini` and `integration/campaign/build_pack.py`, search snapshot `b635ed45f6169c8deae64763864986ca2772cb50`.
- World draft branch confirmed at `50cad91b02719b831cf853dc60f4b4916e7fecb6`; it was not changed.

## Status

Completed: static metadata/CIL inspection; selected control-flow/call inspection; scoped JSON checks; reference recommendations; browser handoff.

Not completed or claimed: native game execution, mod installation, full C# reconstruction, source rebuild, security certification, all-unit collection resolution, full-globe runtime proof, resupply bridge playtest, new world build, or repository changes.
