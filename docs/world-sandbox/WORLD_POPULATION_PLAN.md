# Populated World - build outline from the supplied research

## 1. What to build

Build a geographically coherent, populated Sea Power world based on the supplied installation and logistics research. Populate it with appropriate bases, ships, submarines, aircraft, supporting infrastructure and maritime activity drawn from the installed collection.

The player operates within that environment over sustained engagements: deploy, patrol, fight, withdraw, resupply and return. Combat phases arise from forces and activity already assigned to the world, not from a mandatory story sequence. Minimal operational context is enough.

**The research is the population blueprint; persistence and resupply are behaviours of the populated world.** A compact resupply experiment is a test fixture, not the world-building deliverable.

All population rules below are design proposals. Installation names and source-described roles are taken from R01-R03; they are not independently verified here. No new asset counts, exact coordinates or real-world readiness schedules are asserted.

## 2. Populate six connected layers

| Layer | What the build should contain | Authoring rule |
|---|---|---|
| Installations | Naval bases, airfields, forward support sites, distribution centres and distinct command/training/maintenance nodes | Match the role described by the research. A headquarters is not automatically a tactical ammunition depot. |
| Forces associated with each location | Suitable surface ships, submarines, maritime patrol aircraft, fighters, helicopters, transports and support aircraft | Distinguish source-described association from a verified resident assignment or an authored scenario detachment. |
| Support assets | Auxiliaries, tenders, cargo ships, aviation service facilities and compatible replenishment providers | Map to actual installed support functions; do not assume a tanker supplies every weapon, fuel type or aircraft stock. |
| Deployed forces | Patrols, task groups, escorts, transiting units and a finite reserve | Allocate each physical asset once. A ship underway cannot also be present at its home base. |
| Connections and activity | Supply relationships, safe transit routes, air operating areas, arrivals, departures and replenishment rendezvous | Source an actual relationship or mark it as an authored link. Route geometry and distances require separate validation. |
| Civilian and neutral surroundings | Appropriate shipping and aviation, ports and noncombatant activity where useful and supported | Treat added traffic as scenario population, not a researched current traffic schedule. Nationality alone does not make a unit hostile. |

Local defence elements can be proposed where installed assets and evidence support them. Do not fabricate exact present-day defensive deployments or tactical vulnerabilities from generic base descriptions.

## 3. World coverage suggested by the reports

This table is a population outline, not a list of missions. Listed locations are candidate nodes. Refer to the originals for distinctions, dates and qualifications.

| Region / network | Nodes or areas named in the research | Population focus | Source locator |
|---|---|---|---|
| US Pacific generation | Coronado / North Island, San Diego, Kitsap / Puget Sound | Naval aviation, surface and submarine support, available force generation and maintenance; not every carrier simultaneously ready at its pier | R03 lines 13-32, 46-62; R02 lines 13-17 |
| US Atlantic and specialist support | Norfolk, Jacksonville, Patuxent River, Whiting Field; Susquehanna, Richmond, Anniston, Red River, Tobyhanna | Atlantic fleet and patrol support; distinguish research, training and depot functions from front-line combat forces | R03 lines 13-32; R02 lines 13-17 |
| Pacific supply and forward basing | San Joaquin, Pearl Harbor distribution, Guam, Andersen, Yokosuka | Forward ships and aviation with associated auxiliaries, logistics relationships and transiting forces; separate naval and aviation sites | R02 lines 13-34; R03 lines 34-40 |
| Chinese maritime regions | Yulin, Longpo, Lingshui, Ningbo; South China Sea and East China Sea context | Source-described naval and aviation families, regional patrols and finite deployed groups; verify exact resident assignments before using them | R03 lines 91-107 |
| Chinese national support | Wuhan, Wuxi, Guilin, Shenyang, Xining, Zhengzhou | Headquarters and regional logistics relationships; tactical representation only where useful and supportable | R02 lines 36-59 |
| Russian northern and aviation regions | Kola / Olenya, Engels-2, Ukrainka, Belaya; Barents and Okhotsk context | Source-described aviation/support roles and regional naval context; named fleet bases missing from the reports require further research | R03 lines 64-89 |
| Japanese and Norwegian patrol network | Kanoya, Atsugi, Naha, Evenes | Maritime patrol aircraft, suitable support and proposed patrol activity; verify platform-to-station assignments rather than assigning the same aircraft everywhere | R03 lines 109-134 |
| Australia and Indian Ocean | HMAS Stirling, RAAF Tindal, Diego Garcia | Naval/aviation support, deployed maritime forces, auxiliaries and long-distance connections; role-appropriate population rather than identical fleet clusters | R01 lines 53-55; R02 lines 19-25 |
| Arabian Sea and Horn of Africa | Bahrain, Muharraq, Jebel Ali; separate US, Chinese, French, Japanese and Italian Djibouti facilities | Naval and aviation support, escorts and neutral traffic; colocated facilities retain different operators and access rules | R03 lines 42-44; R01 lines 47-51 |
| Mediterranean and European support | Rota, Naples, Sigonella, Souda Bay, Akrotiri, Germersheim; Deveselu and Redzikowo | Distinct command, patrol, naval, aviation, distribution and fixed-defence roles, mapped only where supported | R03 line 44; R02 line 23; R01 line 59 |
| South Atlantic | Mount Pleasant, Mare Harbour | Small remote aviation and maritime support presence, patrol and resupply activity, not a gratuitous carrier battle | R02 lines 69-71; R03 lines 140-146 |
| French strategic-support context | Ile Longue | Broad naval/strategic context if needed; no nuclear-storage layouts, handling procedures or nuclear-employment implementation required | R03 lines 148-152 |
| Unresolved expansion lead | Ban Keun training-centre claim | Retain as a research lead; do not populate an operational combat base on that claim alone | R01 lines 35-37 |

Generic references to Kuwait, Oman and the UAE do not identify every usable installation. Do not create precise unnamed bases from those references. Likewise, a report mentioning Kola or a sea region does not supply coordinates or a complete fleet order of battle.

These reports are a strong starting scaffold, not exhaustive global coverage. Keep missing regions visible in an expansion backlog rather than filling gaps with invented provenance.

## 4. Define each location as a population package

For every node, prepare one inspectable record with:

- Identity: stable world ID, report name, country/operator as supported, host/location information and source section.
- Role: naval support, aviation, distribution, command, maintenance, training, research or mixed; keep colocated facilities distinct where appropriate.
- Position: public location evidence and a separately validated in-game anchor. Coordinates may remain pending while the population plan is authored.
- Associated forces: source-described platform families, exact collection mappings when resolved, proposed quantities and initial allocation.
- Initial allocation: at base, underway, on patrol, escorting, servicing or reserve. These are scenario choices unless separately sourced.
- Support: selected installed suppliers, usable services and outstanding limitations; different ammunition, aviation, fuel and repair functions remain separate.
- Connections: other world nodes, proposed arrivals/departures and logistics links, with a source-versus-design label.
- Validation: research status, unit mapping, placement, runtime activation, saved-state behaviour and missing assets.

The register is build metadata, not a new Sea Power INI format. Reuse existing project formats where appropriate instead of inventing engine keys.

A report's fleet size is not an instruction to place that entire fleet in one harbour. Distribute authored available forces among bases, patrols, transit and reserve; never claim those allocations reproduce an exact current deployment.

## 5. Map research to the installed collection

For each candidate force, record the actual winning unit, hull variant, squadron, loadout and source-mod owner. Follow aliases and extensions and validate dependent stores/sensors. Names such as P-8, P-1, Typhoon or a carrier class are lookup terms, not invented game IDs.

Use four explicit outcomes: exact usable mapping; representative proxy requiring a visible label; asset exists but the needed fit or function is missing; no available asset. A source gap and a collection gap are different problems.

Reuse existing SEST base definitions and valid mission positions where suitable. Do not silently retask an unrelated airfield as a named researched base, reskin the same fleet everywhere or assume earlier mod-coverage statistics establish geographic suitability.

Unavailable content remains on the population backlog. Do not block the whole world register on one missing unit, and do not quietly invent the unit to make the coverage total look complete.

## 6. Make the populated world function

Give selected forces standing activity: patrol, escort, transit, hold in reserve or support. An activity description is not implemented AI until its route, orders or triggers are wired and tested.

Keep losses, damage, expenditure and supported state persistent across successive engagements. Service ships and airfields give the player a reason to return or reposition. Reserve forces and replenishment arrivals should belong to the authored world allocation rather than appear as an unlimited wave generator.

Use source-derived logistics relationships as context, but test actual ammunition transfer, aircraft turnaround, supplier restocking, fuel and repair independently. A physical populated support location with one working service is better than claiming a complete economy it does not possess.

The intended experience remains a persistent sandbox. A small test scene may validate a function in parallel, without turning the first world-population deliverable into a separate story campaign or postponing the remaining regional plans.

## 7. Build order and acceptance

**Pass A - world register:** consolidate all three reports, deduplicate installations, retain provenance and create regional population packages across their full scope. Leave unresolved fields explicit.

**Pass B - collection mapping:** identify suitable available assets, fits, service providers, representatives and missing content. Establish proposed population scale and ownership without duplicating individual assets.

**Pass C - populated baseline:** place bases and forces in regional build passes under one world specification. Validate water/land positions, deck/runway compatibility, routes and overall density. Separate authored-world coverage from what is actually active in a test run.

**Pass D - routine activity and support:** add patrols, transit, civilian activity and verified services to that populated baseline. Preserve neutral/operator distinctions.

**Pass E - persistent operations:** exercise successive combat and resupply cycles, disruption, finite reserves and save/load. Use `gameplay-and-tests.md` as a supporting test card.

Do not assume all world assets can run concurrently, but do not declare the global plan impossible without measuring the actual constraints. Report authoring coverage and tested active-world scope separately. Streaming, culling, dynamic spawning or theatre transfers are possible engineering choices to investigate, not promised capabilities or permissions to despawn damaged forces.

The first review should show what will be at each researched location, how it maps to the collection, how regions connect and what remains missing. It should not be a set of narrative chapters or only a resupply demonstration.
