# Research seed and evidence limits

## Supplied reports

All three uploads are titled *Global Force Posture and Strategic Installations: A Comprehensive Assessment for Campaign Simulation*.

- R01: `Pasted markdown(1).md`, 70 lines. Combined power projection/logistics overview, including Djibouti and Australia.
- R02: `Pasted markdown (2).md`, 79 lines. Distribution networks, afloat prepositioning, JLSF centres and remote support.
- R03: `Pasted markdown (3).md`, 172 lines. Expanded installation and platform descriptions, carrier readiness examples, aviation, allied ASW and isolated outposts.

The uploads are research starting points, not independently verified reference works. They overlap substantially and do not provide a bibliography sufficient to validate their detailed claims. Repetition between them is not independent corroboration. Original-upload digests are in `source-manifest.json`; the raw reports are retained in the companion handoff archive, not falsely described as committed here.

## How the research informs gameplay

| Report basis | Sandbox use | Boundary |
|---|---|---|
| Bases as sustainment nodes: R01 lines 5-7; R03 lines 5-7 | Functional support locations that make continued operations possible | Do not substitute a world map and encyclopedia for playable resupply. |
| Distribution and afloat prepositioning: R02 lines 13-34 | Finite support vessels, relief movements and candidate service hubs | A real supply chain is not proof of a game supply system. |
| JLSF structure: R02 lines 36-59 | Distinct candidate Chinese support relationships | Headquarters, distribution centres and tactical depots are different roles. |
| Djibouti cluster: R01 lines 47-51 and 70 | Separate facilities, operator identities and neutral proximity | Co-location does not imply common allegiance, access or inventory. |
| Stirling and Tindal: R01 lines 53-55 | Australian naval and aviation node candidates | Validate installed assets and geography before placing them. |
| Carrier readiness cycles: R03 lines 46-62 | Finite available forces and later arrivals | Relative-time deployments are not a 2028 schedule. |
| Allied maritime patrol: R03 lines 109-134 | Repeat surveillance, ASW and aircraft-support activities | Verify platform assignments; no perfect detection curtain. |
| Mount Pleasant/Mare Harbour: R02 lines 69-71; R03 lines 140-146 | Remote air/sea support operating area | Source roles do not prove aircraft variant, service capacity or stock values. |
| Logistics dependency: R01 lines 65-70; R02 lines 73-79; R03 lines 170-172 | Attrition, ammunition conservation and protecting suppliers | Avoid the reports' instant-disable framing; surviving units retain their own remaining resources. |

## Initial world coverage inventory

Names below are report-derived candidates, not verified 2028 orders of battle, installed unit mappings or new tactical scenarios.

| Area | Candidate nodes / functions from the reports |
|---|---|
| Australia / Indian Ocean | HMAS Stirling; RAAF Tindal; Diego Garcia |
| Western Pacific | Pearl Harbor distribution; Guam naval base and Andersen as separate facilities; Yokosuka; Yulin; Longpo; Lingshui; Ningbo; Kanoya; Atsugi; Naha |
| Arabian Sea / Red Sea | Bahrain; Jebel Ali; distinct US, Chinese, French, Japanese and Italian facilities in Djibouti |
| Mediterranean / Europe | Rota; Naples; Sigonella; Souda Bay; Akrotiri; Germersheim distribution |
| North Atlantic / High North | Norfolk as a force source; Evenes; Olenya; French strategic-support context at Ile Longue |
| South Atlantic | Mount Pleasant; Mare Harbour |
| US support layer | Susquehanna; San Joaquin; San Diego/Coronado; Norfolk; Kitsap; Jacksonville; Patuxent River; Whiting Field, with distribution, maintenance, research and training kept distinct |
| Chinese support layer | Wuhan; Wuxi; Guilin; Shenyang; Xining; Zhengzhou |
| Russian support layer | Engels-2; Ukrainka; Belaya |

The reports are not comprehensive world coverage. Leave unresearched regions and missing facilities visibly unresolved. Do not invent nodes, coordinates, throughput, stockpiles, airbase capacity or repair rates to fill a map. Nuclear storage layouts and material-handling details are unnecessary for this conventional gameplay project and are not implementation targets.

Before any real-world claim affects the scenario, verify its effective date and supporting primary source. Particular review items include named resident aircraft/squadrons, carrier status, DLA counts and scope, JLSF terminology, the Ban Keun claim, French facility naming in Djibouti, sanctuary language and unsupported causal claims about aircraft losses. Distinguish a fictional assignment from a verified deployment.

## Repository evidence inspected

Baseline: `20b3cf89f858df948a6e985f4c76190a708ea17d`. This is a targeted documentation/source inspection, not a full runtime audit.

| File inspected | What it establishes | What it does not establish |
|---|---|---|
| Root `README.md` | Four existing campaign families, canonical catalog/load order, tools and explicit playtest limitations | That a persistent world sandbox already exists |
| `integration/campaign/build_pack.py`, lines 1-160 | Load-order-aware references, placement rationale and campaign-specific output guards | A mission-local event director, global runtime streaming or safe reuse without a side-effect audit |
| `docs/campaigns/southern-watch/build-notes.md`, opening sections | Observed cross-mission variable examples and an explicit static/runtime distinction | That those examples implement this single-mission persistence requirement |
| `integration/replenishment/README.md`, opening through supplier sections | TruckSupplySystem-based integration, supply-category and launcher gates, donor isolation and supplier configuration | Every supplier/store pair working in the installed game; some counts are historical snapshots |
| `docs/replenishment-in-play.md`, lines 1-203 | Documented range/speed/rate restrictions, finite ammunition holds, distinct aircraft ordnance system and known limitations | Infinite supplier restocking, fuel transfer, deep repair or flight-deck-stock replenishment |

The replenishment player guide states that an auxiliary's hold runs out and does not refill at sea. Treat supplier sustainability as a capability to investigate, not a solved loop. It also distinguishes aircraft ordnance from vessel replenishment and describes a submerged-submarine restriction as a house rule rather than engine enforcement. Preserve those distinctions.

External primary reference checked during preparation: the RE-power author's Workshop description, item `3605013271`, describes expansion of the game's resupply mechanism and warns that ammunition compatibility requires testing. Its limitations are not automatically the limits of SEST's patches; nor do SEST source changes automatically prove runtime success.
https://steamcommunity.com/workshop/filedetails/?id=3605013271

Evidence labels for future work: `supplied_unverified`, `repository_static`, `runtime_verified`, `design_proposal`, `unresolved`. No new world-sandbox feature has `runtime_verified` status yet.
