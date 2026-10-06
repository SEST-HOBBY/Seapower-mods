# SEST World Sandbox - persistent gameplay draft

Status: design foundation only. No playable mission or new runtime system is claimed by this commit.

Branch: `feature/world-campaign-draft`
Baseline: `feature/northern-front-iii-export` at `20b3cf89f858df948a6e985f4c76190a708ea17d`.
Date: 7 October 2026, Australia/Brisbane.

## Direction

The user's clarification governs this draft: more persistent mission gameplay, resupplying and multi-phased combat; less story and more world sandbox.

**Build an ongoing operational sandbox, not another sequence of story missions.** The intended experience is to deploy forces, find and engage threats, withdraw, replenish and return to combat with the same surviving units. The operation should remain live while different groups are fighting, transiting, recovering aircraft or obtaining supplies.

A world database supports that gameplay. It is not the product by itself. Geography and installations from the three supplied research reports provide candidate operating areas and service-node roles, not a script the player must follow.

This replaces the initial proposed three-mission WC01-WC03 convoy chain. Do not implement that superseded approach as the main design. The first proof is ONE persistent scenario with multiple combat and replenishment cycles.

## First playable target

One continuous, saveable mission in a validated regional area, containing a modest player surface group, a compatible ammunition supplier, usable aviation support, finite opposing forces and a small amount of neutral traffic. Use actual installed units after resolving the current collection, rather than prescribing unverified unit IDs here.

The player must be able to:

1. Fight an initial engagement and spend ammunition.
2. Break contact, choose a replenishment rendezvous and receive a measurable transfer from a real supplier.
3. Rejoin a later engagement with the same surviving ships, remaining damage and changed inventories.
4. Save and reload without restoring spent stores, resurrecting losses or replaying completed events.

A later engagement is not a new mission file, a briefing-only consequence or a fresh copy of the task force. A supply ship that is empty or sunk must matter physically in the running mission.

Start small to prove the loop, not to redefine the final world scope as a regional story campaign. Expand geographical coverage after continuous play, supply behaviour and save/load survive testing.

## What matters most

| Priority | Required direction |
|---|---|
| Persistence | Existing units, losses, damage, magazines, aircraft and supported mission state continue through combat cycles and reloads. |
| Resupply | Actual compatible stores transfer under the installed system's limits; no automatic rearm between phases. |
| Multi-phase combat | Patrol, contact, engagement, withdrawal, servicing and renewed pressure occur inside the live mission. Different groups may occupy different phases simultaneously. |
| Player freedom | The player chooses where to concentrate, when to disengage, which ships to service and which opportunities to ignore. |
| World sandbox | Several operating areas and support networks are the destination; geographic expansion must not erase force identity or invent global simulation. |
| Minimal story | Brief operational messages, contact reports and optional objectives, not character scenes, mandatory narrative branches or long lore pages. |

Persistent does not mean an always-online server, an infinite supply economy or a promise of unlimited procedural spawning. Those are separate capabilities and are not established here.

## Document guide

- `gameplay-and-tests.md`: the gameplay contract, phase design, supply boundaries and acceptance tests.
- `research-seed.md`: how the uploaded research informs the world, its gaps and the repository evidence inspected.
- `CLAUDE_BROWSER_START.md`: the first implementation work package.
- `source-manifest.json`: original attachment identifiers and SHA-256 digests. Raw reports are not embedded in this Git commit; the companion handoff archive retains the originals.

## Isolation

This commit adds documentation and source metadata only. It changes no existing campaigns, mission builders, unit definitions, load-order files, generated packs, installers or Workshop metadata.

Keep Southern Watch, Southern Reach / Tasman Shield, Red Line and Sulu Line intact. Use an isolated opt-in prototype output and inspect all builder side effects before sharing helpers. Do not register the sandbox in the normal consolidated build or publish it without approval.

Working identifiers, to be checked for collisions: `SEST World Sandbox` for the player-facing name, `world_sandbox` for a future source module and `WSB_` for mission-local event/state identifiers. The branch name stays as requested; it does not require the runtime to use native Task Force Mode.

A 2028-era setting is a provisional collection-alignment choice, not a historical claim or a required storyline.
