# Browser handoff: research-led SEST world and Dynamic Campaign Mod

## Context and scope

The user wants the researched world populated, with persistent operations, resupply and multi-phase combat, and minimal story. Do not replace this with a three-mission narrative or make a tiny mechanics demo the main deliverable.

Repository: `SEST-HOBBY/Seapower-mods`.
World draft branch last verified at `50cad91b02719b831cf853dc60f4b4916e7fecb6` (`feature/world-campaign-draft`). Fetch and inspect current refs; this may no longer be the latest work on another session's branch. Preserve existing world/collection inventories. Do not reset, merge unrelated branches or touch published files.

Read the repo's `docs/world-sandbox/WORLD_POPULATION_PLAN.md`, `CLAUDE_BROWSER_START.md`, source manifest and `research/R01.md` through `R03.md`. They are already in the branch; no sandbox link is needed for the original research.

Also read this bundle's `REVERSE_ENGINEERING_REVIEW.md`, `dll-evidence.json`, `campaign-audit.json` and `selected-evidence.il.txt`. Its textual reference inputs are in `reference-inputs/`. The original DLL is a separate user attachment, not in this bundle.

Uploaded DLL SHA256: `0047b9e6429a1dcf6ae3a393725c8f928ad1b22014d7dbe05f019949715cd4a3`.
Plugin version: `0.24.0`; assembly: `0.24.0.0`; target framework `.NET Standard 2.1`.
Declared game window: `>=0.8.3`, `<0.9.0`.
This was a static CIL review. Nothing was executed, installed or playtested.

## First decision

Evaluate a separately named SEST campaign data pack using the existing Dynamic Campaign engine before proposing a binary fork or a new strategic engine. Its menu scanner searches `dynamic_campaigns` directories for `campaign.json`; this is observed implementation, not yet a tested public extension contract.

Keep the world register engine-neutral. A generated `dynamic_campaigns/sest-world-sandbox/campaign.json` is a candidate adapter output, not an existing file or an instruction to overwrite Bungalow's campaign. Verify schema, IDs, mod file discovery, author guidance and permissions before using this path.

This engine keeps a strategic world and generates local tactical encounters with results carried back. State clearly whether that meets the user's gameplay intention. Do not call it one continuously active global tactical mission, and do not call such a mission impossible just because native tactical files have a map centre. The inspected writer emits `GeoPosition=`.

## Read-only engineering review

Trace these exact areas, using the uploaded version or matching author source:

- CampaignMenuPatch.Postfix (0x06000949), CampaignDefinition.Load/Validate (0x060010c4/0x060010c5): data-pack discovery and schema.
- CampaignSim.StepTo (0x06000d01): world update ownership, strategic time and concurrent activities.
- MissionWriter.Text/WriteUnit (0x06000a37/0x06000a41), BattleSession.Launch/OnDebriefExit (0x06000994/0x06000a2c), BattleExit.Leave and Battles.Apply: spawn/readback identity and state.
- CampaignSave.Read/Write, Saves.Load/Save, Files.WriteSafely, StateInvariants.Check: saved-state coverage, upgrades and rollback.
- Logistics.ReplenishAtSea/SupplyShips, Supply, Replenishment, ShipStores and BattleSession.Fired (0x06000a23): campaign/native/SEST stock conservation.
- Detection.ShipSensors/FlightSensors and SensorProfile: role-based strategic ranges versus actual modern sensors.
- CarrierAir/CarrierWings/AirOperations: unique aircraft identities, loadouts, flight-deck compatibility, losses and recovery.
- GeoBounds.Continuous, GameGeo, NavGrid, MissionWriter.GameLon: dateline and globe-extension behavior.
- Victory, Invasions, Missions and ownership/side conversion: optional/free-play outcomes and neutral access instead of forcing 1985 conquest rules onto SEST.

Tokens are specific to the uploaded binary. Prefer supported source/APIs where available. Do not execute arbitrary uploaded code merely to inspect it. A local game test belongs in an isolated, backed-up test installation, not the published pack.

## Specific tests and mistakes to avoid

1. Inventory bridge: start 20 rounds, fire 10, receive 10 tactically, finish 20. Confirm the campaign knows both expenditure and supplier debit. Trace FiredBefore and other reconciliation before concluding there is a bug. No free ammunition, double charging or duplicated cargo.
2. Save/debrief: sink a supplier, damage a system, lose an aircraft, recover a survivor and reload. Check exact persisted fields. The writer hard-codes `CrewSkill=Trained`; do not promise crew XP carryover without evidence. Test result-read failure and pre-battle rollback paths.
3. Modernization: do not assume correct modern INIs automatically produce modern strategic detection, prices or support eligibility. Profiles such as Ship=70/150/20 NM are strategic abstractions, not guaranteed detections.
4. Identity: a class renamed Midway is still the class it instantiates. `Surface` includes submarine forces. `DateBased_` stores have resolver support. The absent China merchant list has a coalition/global fallback; do not invent a missing-reference defect.
5. Geography: test longitude seams, polar/high-latitude regions, straits, port approaches, path costs and encounter scaling. Regional authoring partitions do not require disconnected campaign saves.
6. Diplomacy: keep host/operator/access/combat alignment separate. More than two JSON side definitions do not prove every runtime subsystem supports multi-sided politics.

## Other material to compare

Prioritise exact installed Seapower-Scripts/AnchorChain/BepInEx/Harmony versions, the SEST and RE-power supply implementations, native Pacific Strike persistence, and Flight Deck Ops for the actual winning carrier definitions. AI Doctrine Overhaul is a comparison/conflict audit only, not a new dependency. Automatic SAR is optional; establish a persistent personnel result before advertising crew recovery. Inspect author source/licence before copying or publishing third-party implementation.

## Deliverable

Return a source-linked engine capability/limitation matrix and a concrete adapter feasibility assessment alongside the global population register. Separate: research facts, scenario allocation, resolved collection assets, static code behavior and runtime evidence. List any proposed code changes but do not apply a production refactor or publish anything under this review request.

Browser workflow only: do repository analysis in the available environment. Mark Sea Power execution pending when it is unavailable. No local Claude Code requirement, no force-push, no automatic branch merges, no AI imagery or attribution trailers.
