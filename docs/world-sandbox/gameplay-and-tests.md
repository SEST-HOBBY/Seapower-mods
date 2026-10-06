# Gameplay contract and proof plan

Everything labelled as a requirement below is a proposed behaviour to implement and test, not a claim that the engine already supports it.

## One live mission

Prefer a persistent scenario over a sequence of native Task Force missions. Keep unit identity, location, damage and stores inside the same running simulation. Native mission save/load is the first persistence mechanism to examine. Cross-mission CampaignVariables are not proof of mid-mission persistence for a new event system.

Do not end the scenario automatically when the first engagement is won. Check the engine's victory/defeat behaviour and deliberately prove that the mission continues between phases. Optional objectives can finish without ending the sandbox. Eventual player-selected conclusion or terminal defeat needs a tested mechanism rather than an invented menu button.

No phase may silently replenish magazines, refill support ships, reconstruct damaged systems, recover aircraft, respawn lost hulls or duplicate an existing formation. Allow any genuine native damage-control behaviour; the prohibition is on artificial phase resets, not on the game's own repairs.

## Phases describe activity, not story chapters

Use a small reusable activity model: prepare/patrol, investigate contact, engage, disengage, service, redeploy. These labels are design metadata, not new INI keys.

Different groups should progress independently. One escort may replenish while another covers the rendezvous and aircraft prosecute a contact elsewhere. The world must not wait for every unit to reach an arbitrary global phase number.

Possible pressure sources are a finite patrol, a reserve surface group, a later aircraft sortie or an escorted supply arrival. Choose from attested route, time, area, detection or loss mechanisms after inspecting the game data. A force found early should not become invulnerable or untargetable just because its scheduled phase has not begun.

Begin with deterministic, authored events and finite reserves. Random selection, probabilities and reusable spawning can be added only after a suitable runtime hook is verified. If random choices are introduced, commit them once to saved state so reload cannot reroll an event or generate additional supplies.

Phases must not become an endless wave defence. Let the player change routes, disengage, choose priorities and use a quiet interval. Avoid spawning an enemy on top of the player, granting the enemy unexplained perfect knowledge or replacing every loss automatically.

## Supply is the core loop

### Ammunition

Reuse SEST Replenishment and the winning collection definitions. For each selected supplier/receiver/store combination, establish target-type compatibility, any supply category, launcher reload eligibility, transfer range, speed restrictions, transfer rate and finite resource limits from the actual files.

Observe both ends of a transfer in game. Receiver ammunition rising is not sufficient if supplier stock or the relevant finite budget never falls. Verify shared ammunition-point pools and category counts independently; a single favourable round does not prove every store works.

Deliberately test empty suppliers, incompatible rounds, out-of-range receivers, excessive speed and interruption by movement or supplier loss. Resume only from remaining stores. A replenishment system enabled in configuration is not proof that the selected platform combination replenishes correctly.

The current SEST material describes at-sea reloads for weapons that are often treated differently in real-world service. These are collection/gameplay rules. Do not market them as verified contemporary real-world VLS handling or weapons logistics.

### Supplier sustainability

A loaded auxiliary enables repeated engagements only until its usable supply is exhausted. The first proof may use finite initial stock plus a finite relief supplier; that is honest persistent play, not an endless economy.

The world-scale design should investigate restocking suppliers at support nodes and escorting replacement cargo. It must not pretend either already works. Test whether the engine can replenish the supplier's supply resource rather than merely its own defensive weapons. Supplier-to-supplier transfer and base-to-supplier restocking are separate capabilities.

If genuine restocking is unavailable, document the limit and use explicitly finite, preallocated relief ships with travel time as a temporary implementation. Do not refill the original ship invisibly, spawn unlimited new auxiliaries or silently inherit an unlimited port supply block.

### Fuel, aircraft and repairs

Ship ammunition transfer does not prove ship fuel transfer. Keep fuel sustainment unimplemented until the engine mechanic and observable state are demonstrated.

Aircraft launch, recovery, turnaround and rearming use the appropriate airbase/carrier systems. Prove compatible recovery and repeat sorties separately. Replenishing a carrier's own launchers does not prove its flight-deck ordnance stocks refill. Landing an aircraft does not automatically prove finite base fuel or aviation ammunition is modelled.

Deep repair, replacement aircraft and new hulls are also separate support services. Implement only the services that can be observed and tested. Represent unavailable services clearly; no hidden repair timer that restores a ship at the next phase.

Destroying one support asset should remove its available service, not instantly empty unrelated combatants' magazines or shut down every base in the theatre.

## Bases and world coverage

Treat source-described ports, airfields and distribution centres as candidate service roles. A named location is not automatically an installed game unit, valid position, shared inventory or usable runway.

Ports, carriers and auxiliaries should have distinct supported services. A command headquarters can remain an abstract world reference; it does not need to become an ammunition depot. Keep separate operators and scenario access rules for colocated facilities. Neutral traffic and neutral facilities do not become hostile merely because of national association.

The long-term target is geographic freedom across a world operating environment. First prove a validated region, then two separated operating areas inside the same persistent mission, then wider coverage. Measure long-distance movement, map/geography behaviour, time compression, aircraft reach, saved-state size and performance as scope increases.

Do not preplace the entire researched world just to claim global coverage. Hidden, distant or disabled units may still have a runtime cost; measure it. If native limits require a later theatre-transfer architecture, present the compromise explicitly and prove state transfer before adopting it. Do not silently replace the requested sandbox with a story campaign.

## First proof setup

Choose an existing, verified mission geography from the repository where practical. The previously developed northern Australia/archipelago sandbox is a candidate only after locating and checking its actual current source. Do not modify or install over that mission.

Use a compact blue group, one mapped ammunition supplier, appropriate aviation support, at least two distinct combat opportunities and finite reserves or reinforcements. Add enough neutral activity to test discrimination without making traffic population the performance bottleneck. Assign exact unit counts, fits and positions after the collection and spatial audit, not from an unsourced global order of battle.

Enemy depletion should matter too. Begin with native finite magazines and finite forces. Autonomous AI withdrawal, replenishment and relaunch is a later proof unless existing behaviour can be demonstrated; scripted movement toward a supplier alone does not establish a functioning enemy logistics model.

## Acceptance tests

| ID | Test | Required observation |
|---|---|---|
| P01 | Continuous combat | Two distinct engagements and a servicing interval occur without a new mission load or a fresh player task force. |
| P02 | No early ending | Completing the first combat objective or destroying its opposition does not terminate the sandbox prematurely. |
| P03 | Identity and attrition | Surviving hulls retain state; sunk hulls stay lost; ammunition spent before service stays spent; no phase reset. |
| P04 | Real transfer | A selected compatible round replenishes under actual limits, with the correct finite supplier resource decreasing. |
| P05 | Negative supply cases | Empty, incompatible, too-fast and out-of-range cases do not supply; destroyed or departed suppliers stop serving. |
| P06 | Repeated service | The same supplier services another depleted receiver or a later cycle using only its remaining stores. |
| P07 | Supply exhaustion/relief | Exhaustion constrains play; any relief has a finite allocation, valid arrival and no duplicate rewards or stocks. |
| P08 | Aircraft cycle | Aircraft launch, perform a task, recover and sortie again where supported; failed recovery and exhausted aviation stocks are handled honestly. |
| P09 | Reload during service | Save partway through a transfer and reload: neither ammunition nor supplier stock is duplicated or reset. |
| P10 | Reload at an event boundary | Save before and after an activation: completed events do not repeat and pending events are neither lost nor double-fired. |
| P11 | Reload after attrition | Damage, loss, finite reserve use, positions and relevant objective state are consistent with the saved mission. |
| P12 | Player freedom | Declining a combat opportunity or withdrawing does not create an unexplained soft lock or force a narrative sequence. |
| P13 | Real orders/neutrality | Test Hold/release behaviour and neutral encounters in game; labels are not treated as a hard weapons inhibit. |
| P14 | Extended session | Measure representative low/high activity, time compression, save/reload and entity growth; record actual duration and hardware, not an invented supported ceiling. |
| P15 | Isolation | Existing campaigns, deployable outputs and default installation behaviour remain unchanged. |

Also test distinct service types separately: supplier restocking, aircraft-magazine restocking, ship fuel transfer and repair. A failed optional service must not be reported as a working global logistics economy.

## Reporting

For every test record build commit, game version, dependency/export snapshot, steps, initial and final values, evidence and result. Distinguish source-inspected, references-resolved, generated, statically-tested, game-loaded, played and save/load-verified. No gameplay or save/load tests were run while preparing this documentation seed.
