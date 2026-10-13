# Supporting gameplay requirements and tests

This is a supporting test card for `WORLD_POPULATION_PLAN.md`. It no longer defines a small mechanics prototype as the first deliverable. Global population authoring and collection mapping come first; test scenes may run in parallel and must not replace that work.

## Desired behaviour

The player operates in an already populated world through patrol, contact, combat, withdrawal, service and renewed operations. Different formations may be engaged, transiting or servicing at the same time. Keep story minimal and avoid mandatory chapter transitions.

Use surviving units rather than pristine replacement copies. Preserve supported damage, inventory, position, losses and event state across successive engagements and save/load. Completing a local objective should not prematurely end the sandbox. These are requirements to prove, not claims of implemented functionality.

Keep force allocations finite. A ship at sea is not also at its home port; reserves and arriving support vessels consume their authored allocation. Scenario activity need not be an infinite procedural spawn system.

## Distinct support services

- Ship ammunition: validate supplier/receiver compatibility, categories, reloadable launchers, range, speed, rate and depletion of the actual finite supply resource.
- Aviation: separately validate aircraft recovery, turnaround, repeat sorties and relevant flight-deck stocks.
- Supplier restocking: prove replenishment of the supplier's supply resource, not merely its own defensive weapons. Otherwise expose the limit and use explicitly finite relief assets.
- Ship fuel and repair: do not infer these from ammunition transfer. Implement only observed capabilities and disclose abstractions.

SEST gameplay reload rules are not proof of real-world weapons-handling capability. Destroying a supplier removes its service; it must not instantly empty unrelated ships' existing magazines. No free rearm, stock reset, repair reset or duplicate reinforcement at a combat-phase boundary.

## Tests

| Area | Evidence required |
|---|---|
| World population | Each placed node/force has a source or explicit scenario rationale, valid mapping and validated position; unknowns remain visible. |
| Identity | No physical hull is allocated twice; destroyed units do not return through another spawn path. |
| Activity | Assigned routes/orders execute; a documented patrol is not counted as functioning solely because it appears in a plan. |
| Continuous play | Successive engagements and servicing occur with the same forces and without unintended mission termination. |
| Transfer | Receiver stores rise and the correct finite supplier budget/stock falls. |
| Negative supply cases | Empty, incompatible, too-fast, out-of-range, destroyed and departed suppliers cannot supply. |
| Repeated operations | A later engagement uses the actual remaining force state and support resources. |
| Aircraft support | Selected aircraft can recover and sortie again under the actual base/deck rules. |
| Save/load | Transfer progress, stock, damage, losses and pending/completed events do not reset, duplicate or reroll. |
| Neutrality and combat orders | Test actual Hold/release behaviour and neutral interaction, rather than treating a label as a hard weapons inhibit. |
| Scale | Record measured active-unit scope, geography, time compression, hardware, session duration and save behaviour; do not invent a supported global ceiling. |
| Isolation | Existing campaigns, consolidated output and normal installation remain unchanged. |

Record build commit, game version, dependency snapshot, steps and observations. Static checks are not playtests. No gameplay or save/load tests were performed while preparing this outline.
