# SEST SOUTHERN WATCH
## The Northern Lifeline — campaign lore, research and build brief

**Design version:** 1.0 · **Research checked:** 20 September 2026 · **Fictional campaign:** October–November 2028

**Game:** Sea Power: Naval Combat in the Missile Age, using the SEST mod collection.

**Premise:** Australia and its regional partners must keep people, fuel and supplies moving through the northern approaches while a maritime coercion campaign escalates into a limited regional war. Winning means reopening the sea routes with a functioning force and the confidence of the countries it is helping.

This is a campaign design and research package, not an installed mission pack. The events, characters, deployments and future readiness figures below are fiction. Real-world statements are linked to their sources. Equipment statistics in mods are game parameters, not verified estimates of real weapons performance.

## 1. The campaign to build

Build **one Australian-led story with twelve main missions**, supported by the existing Banda sandbox and optional allied, opposing-force and experimental episodes. Keep the complete enabled mod collection available throughout. Select the units needed for each episode; dependencies and improvements to existing units count as use of a mod even when that mod contributes no separate platform.

The defining experience is a small force working across a very large region. A frigate protects a convoy; an aircraft identifies something the frigate cannot see; the tanker keeps that aircraft on station; the replenishment ship makes tomorrow's mission possible. The player often has enough firepower to win an engagement but too little time or information to satisfy every objective.

The core should feel Australian through its responsibilities, geography and force limits: northern bases, long transit distances, regional cooperation, merchant shipping, maritime patrol, a small number of escorts and aircraft, and the political importance of bringing people home. Major allied formations arrive in stages. The Australians continue to own the convoy, rescue and regional coordination problem after a US carrier appears.

**Recommended modes**

| Mode | Scope | Use of the collection |
|---|---|---|
| Northern Lifeline | Twelve connected 2028 missions | Modern Australian core, regional partners, limited US/Japanese/French support, credible conventional opponents |
| Living Seas | Large free-play theatre | Preserve the user's existing sandbox and hand edits; add campaign context through a separate version |
| Allied Dispatches | Optional missions within the same crisis | Japanese, French, British, European and additional US equipment |
| Red Line | Optional opposing-force perspective | Russian/Chinese reconnaissance, escort and withdrawal problems; finite resources on both sides |
| Future Front | Explicit alternate 2032–35 technology branch | YF-23 production fiction, J-36/J-50, Type 004, MALICE, speculative bomber and missile fits |
| Cold Sea | Separate historical/exercise anthology | Cold War and retired equipment, historical nuclear-era assets with conventional mission settings |

An enabled collection is not an order of battle. Do not place every aircraft, ship or SAM in the opening mission. Do not enable an unsubscribed mod to satisfy the word “all”. Appendix A assigns every one of the 139 enabled Workshop entries a role and records the five excluded catalog entries.

## 2. What the repository actually contains

The design is pinned to [`SEST-HOBBY/Seapower-mods`, commit `afed87cef9dfbcf63fa2f16cd620cde3c477a7d0`](https://github.com/SEST-HOBBY/Seapower-mods/tree/afed87cef9dfbcf63fa2f16cd620cde3c477a7d0), on `feature/northern-front-iii-export`. Both the remote default and `data/deploy-branch.txt` identify that branch. Earlier conversation references to a different active branch do not describe this snapshot.

| Item checked | Result and implication |
|---|---|
| Catalog | 144 entries: 132 active, 5 deprecated, 2 WIP and 5 unsubscribed |
| Canonical order | 140 tokens: 139 Workshop entries plus `SEST_Integration`; every Workshop token has a catalog entry |
| SEST source packs | 16 registered packs, consolidated into one deployable |
| Active mission setting | `NORTHERN FRONT III FINAL NEWEST`; always name the new mission explicitly when running tools |
| Banda scenarios | Twelve generated vignettes in `integration/missions/`, produced by `build_banda_vignettes.py` |
| Living Seas and Lean v2 | Current default branch contains exported copies under `mods-source/_vanilla/user/missions/user_missions/`; it does not contain their top-level `integration/missions/` versions from the other branches |
| Living Seas exported content | Declares 51 neutral vessels, 37 neutral aircraft, 9 neutral biologics and 396 total land units. It is a useful world reference, not a suitable mandatory starting size for every chapter |
| New Anzac model | Current builder patches Workshop `3440622312`'s actual Anzac model. The RAN pack README still describes the old Type 23 stand-in; use the builder and winning output as evidence |
| Aegis BMD / intercept fixes | Present on `sest-dev/kind-faraday-ctr5h0` at `b45ad8cb859290f6b44d62374d6eede3153a6448`; absent from the current default branch's registered packs |
| A-10C+ | `usaf_a-10c_plus` does not resolve in this snapshot. `usa_a-10c` does resolve, with SEST modifications |
| RAN replenishment ship | `ran_aor_supply` resolves, but the inspected winning INI has no explicit `SupplySystem_*` block. Its name and ship role do not prove that it can replenish another unit in game |

The dry-run vignette builder, load-order checker and dependency checker passed during this review. Those checks establish limited static properties. They do not establish that the missions load, that every texture appears, that an aircraft can recover aboard its assigned ship, or that a resupply or victory trigger behaves correctly in game.

**Branch integration rule:** carry needed work onto a new `feature/southern-watch-campaign` branch from the agreed current baseline. Review the BMD/intercept changes and older mission builders separately, preserve newer Anzac and aircraft work, rebuild the consolidated pack, and resolve winners again. Do not replace the current deployable wholesale with one from an older branch.

Repository evidence: [catalog](https://github.com/SEST-HOBBY/Seapower-mods/blob/afed87cef9dfbcf63fa2f16cd620cde3c477a7d0/data/mod-catalog.json), [load order](https://github.com/SEST-HOBBY/Seapower-mods/blob/afed87cef9dfbcf63fa2f16cd620cde3c477a7d0/data/load-order.tokens.txt), [vignette builder](https://github.com/SEST-HOBBY/Seapower-mods/blob/afed87cef9dfbcf63fa2f16cd620cde3c477a7d0/integration/missions/build_banda_vignettes.py), [RAN builder](https://github.com/SEST-HOBBY/Seapower-mods/blob/afed87cef9dfbcf63fa2f16cd620cde3c477a7d0/integration/ran-fleet/build_fleet.py), [separate integration branch](https://github.com/SEST-HOBBY/Seapower-mods/tree/b45ad8cb859290f6b44d62374d6eede3153a6448).

## 3. Research translated into design decisions

The right research question is “what gives this mission an Australian reason to exist?” Public capability announcements support the setting; they do not supply classified performance, future availability or game balance.

| Public evidence | What it supports | Campaign use and limit |
|---|---|---|
| [2026 National Defence Strategy factsheet](https://www.defence.gov.au/sites/default/files/2026-04/2026%20NDS%20Overview_factsheet_WEB.pdf), April 2026 | Northern approaches, economic connections, regional partnerships and greater self-reliance are explicit priorities | Make protection of sea access the strategic objective. Allied support can be constrained without inventing abandonment of Australia |
| [Australia–Indonesia defence discussion](https://www.minister.defence.gov.au/transcripts/2026-03-12/doorstop-jakarta-indonesia), 12 March 2026 | Cooperation following the February Jakarta Treaty; Morotai discussed as an Indonesian training facility | Indonesia is an active partner with its own command and consent decisions. Morotai is not an assumed Australian base |
| [Pukpuk Treaty implementation](https://www.minister.defence.gov.au/media-releases/2026-08-16/australia-papua-new-guinea-advance-pukpuk-treaty), 16 August 2026 | Australia–PNG treaty entered into force on 8 July 2026 | Give PNG an important role and a concrete request for assistance. Mission access arrangements remain fictional and specific |
| [Australian shipping statistics](https://www.bitre.gov.au/resource/maritime/australian-infrastructure-and-transport-statistics-yearbook-2025-shipping-chapter) | 32,142 port calls and 5,841 distinct cargo vessels visiting Australian ports in 2024–25 | Civilian shipping is the strategic purpose of the game world, not background decoration. Avoid unsupported claims about exact wartime trade volumes |
| [AMSA navigation guidance](https://www.amsa.gov.au/safety-navigation/navigating-coastal-waters/navigation-through-great-barrier-reef-and-torres-strait) | Torres Strait and reef passages involve defined routes, pilotage and navigational constraints | Build routes around water, passage geometry and plausible ship draught. Do not draw a direct line through reefs or route very large tankers through an arbitrary shallow passage |
| [Final F-35A delivery](https://www.defence.gov.au/news-events/releases/2024-12-19/final-f-35a-aircraft-delivered), 19 December 2024 | Completion of the 72-aircraft Australian acquisition | A small forward detachment is credible. Seventy-two delivered aircraft is not seventy-two deployable aircraft for the player |
| [RAAF long-range strike milestone](https://www.defence.gov.au/news-events/releases/2026-09-11/air-force-modernises-air-launched-strike), 11 September 2026 | LRASM and JASSM-ER IOC announced for Super Hornet employment; P-8 LRASM firing also described | Make Australian Super Hornet maritime strike a core option. The release does not establish universal P-8 LRASM availability, and this repo's P-8 loadout still needs separate checking |
| [P-8A aircraft page](https://www.airforce.gov.au/aircraft/p-8a-poseidon), checked 20 September 2026 | Maritime patrol, ASW, surveillance and rescue roles; 14 aircraft under No. 92 Wing at the time checked | Patrol, classification and rescue belong in the same campaign. Squadron or national fleet counts are not mission readiness figures |
| [Triton facilities at Tindal](https://www.defence.gov.au/news-events/news/2026-02-12/strengthening-northern-air-power), 12 February 2026 | Aircraft launched, recovered and maintained at Tindal, with remote crews at Edinburgh | Give Triton a northern operating role and a reason to survive. Do not inherit exaggerated detection certainty from a mod description |
| [KC-30A aircraft page](https://www.airforce.gov.au/aircraft/kc-30a-mrtt), checked 20 September 2026 | Australia's actual tanker fleet and both boom and hose-and-drogue systems | KC-46/KC-135 units in the collection are allied support or disclosed stand-ins. A civil A330 mesh is not a working KC-30A |
| [Growler upgrade project](https://www.defence.gov.au/defence-activities/projects/advanced-growler-airborne-electronic-attack-capability) | Public NGJ and other upgrade program; page explicitly says its content is current to February 2024 | Electronic warfare is a sound theme. The listed 2026 IOC is a forecast in that source, not proof every upgrade has arrived. MALICE remains custom fiction |
| [Tomahawk certification](https://www.defence.gov.au/news-events/news/2026-04-17/gold-standard-missile-readiness), 17 April 2026 | Two Australian ships described as equipped, with a third expected | Limited naval strike fits are plausible. Verify the selected game hull and magazine instead of equipping every Hobart identically by assumption |
| [Mogami acquisition contract](https://www.defence.gov.au/news-events/news/2026-04-22/navy-locks-future-frigates), 22 April 2026 | First Australian delivery scheduled for December 2029 | Use JMSDF Mogamis in 2028. An Australian Mogami belongs in a later branch, and delivery alone would not establish operational readiness |
| [Submarine Rotational Force–West preparations](https://www.asa.gov.au/news/upgrades-hmas-stirling-pave-way-submarine-rotational-force-west), 2 December 2025 | US/UK rotational presence planned from 2027; Australian nuclear-powered submarines from the early 2030s | Use Australian Collins boats and allied SSNs in the core. Do not relabel a US Virginia as an Australian 2028 boat |
| [HMAS Anzac history](https://seapower.navy.gov.au/history/units/hmas-anzac-iii) | HMAS Anzac decommissioned on 18 May 2024 | The class remains useful; choose a different named hull for the core. A 2028 recommissioning of Anzac must be declared alternate history |
| [BOM northern wet-season review](https://www.bom.gov.au/climate/current/season/tropics/summary.shtml), 2025–26 edition checked | Seasonal context for cloud, rain and weather variability | October–November offers varied conditions. Exact 2028 weather is authored fiction; set Indonesian and PNG conditions separately rather than applying Darwin's climate to the whole map |

**Confidence convention:** “documented” describes a cited public fact; “projected” describes an announced future schedule; “campaign assumption” describes our fiction; “mod approximation” describes an implementation compromise. Use these labels in designer notes, not as intrusive text in every player briefing.

## 4. Lore: the six weeks that close the north

### The world before the first mission

By October 2028, Australia has spent two years preparing for a crisis that might arrive without a clear declaration of war. The northern bases are busier, regional exercises are larger, and foreign submarines are more familiar visitors to Western Australia. Commercial shipping still runs to schedules built on the assumption that tomorrow will resemble yesterday.

A confrontation elsewhere in the Indo-Pacific draws much of the immediately available US combat power north. It does not automatically put Australia or its neighbours at war. Canberra, Jakarta and Port Moresby initially share the same aim: keep their own region open and prevent an external dispute from becoming a local conflict.

The disruption begins with incidents that can each be explained separately. A merchant misses its reporting window. A cable-repair ship receives contradictory movement instructions. Two ports lose cargo records. An offshore work crew cannot raise its shore office. Insurers begin declining voyages that are still legal and physically possible.

The fictional **Meridian Maritime Group**, a network of freight companies and security contractors, offers an answer: travel in escorted groups, accept its inspections and use its preferred terminals. Some operators cooperate to keep their crews paid. Others refuse. A few Meridian vessels are genuinely commercial; a smaller number carry armed teams and military communications equipment. Appearance and ownership no longer tell the player enough.

Indonesia has not invited a foreign occupation. Its government opposes the inspections and requests narrowly defined assistance after local security personnel and port workers are detained at a small number of facilities. Timor-Leste and PNG make separate requests appropriate to their own circumstances. Access agreements differ between missions, and the player sees those boundaries in the briefing.

### The inciting incident: the Arafura convoy

The fictional Australian-chartered freighter **MV Coral Pioneer** and two regional coasters divert toward a rendezvous after an engine casualty. A “safety escort” arrives first. When an Indonesian patrol vessel challenges the escort, shots are exchanged. An Australian maritime patrol aircraft records enough to establish that this is an armed coercion incident, but not enough to identify every participant.

HMAS Warramunga is the nearest coalition escort. Her first task is to separate the merchant crews from the armed group and keep the incident from expanding. A liner, fishing boats and a rescue helicopter continue operating nearby. The campaign opens with the player trying to understand a situation, not with a theatre-wide missile launch.

### The escalation

During the first week, Meridian's hard-line faction refuses national orders to disarm. It holds a fictional service platform and several small logistics sites. Regional security forces recover most of the facilities, but one airfield and port enclave remains contested. Its foreign advisers have brought more capable air defence than initially reported.

In this fictional crisis, Beijing sends a naval force under a protection-and-evacuation pretext and demands suspension of the coalition patrols. Different officials and commanders disagree about acceptable risk. The fleet is not omniscient and cannot sustain itself indefinitely. After a local engagement escalates, it begins attacking military escorts and enforcing its exclusion demand. Its operational aim is to make the corridor unusable long enough to force a political settlement, rather than to invade the Australian continent.

A small Russian expeditionary detachment supports the enclave under a separate fictional arrangement. It is a useful place for the collection's Russian reconnaissance aircraft, submarines, frigates and SAMs, but it does not explain away unlimited forces. Reinforcements, fuel and ammunition have to arrive by routes the campaign can show. A stronger Russian presence is reserved for Red Line and extended-war episodes.

The campaign then becomes a contest over time. Australia can defeat a local raid and still lose if the next merchant convoy is cancelled. The opposing fleet can lose a ship and still achieve its objective if shipping stops. Every civilian casualty makes cooperation harder. Every successful evacuation or safe arrival makes the next operation easier.

### The ending

The decisive mission is the first convoy to cross after a ceasefire proposal, with forces on both sides still capable of fighting. A withdrawal order, an unidentified contact and a possible spoiler attack arrive together. The player must protect the convoy without turning a limited settlement into another fleet battle.

The best ending is a working sea route, rescued civilians, credible regional cooperation and a battered but usable task group. A costly ending reopens the route while leaving Australia with a severe escort shortage. A poor ending saves the fleet but loses access. A campaign with severe civilian losses ends in political failure even if the player's combat exchange ratio is excellent.

### Recurring people and organisations

All named characters and commercial organisations in this section are fictional.

| Character or group | Role in the story | What they want from the player |
|---|---|---|
| Commodore Alex Mercer, Australian maritime task group | Calm operational lead | Enough surviving ships and ammunition to sustain the corridor |
| Captain Ratna Prasetyo, Indonesian liaison | Represents an independent partner's decisions | Assistance that restores national control and respects agreed access |
| Commander Mara Kila, PNG maritime liaison | Coordinates the eastern relief route | Reliable deliveries to communities and ports, not simply combat victories |
| Wing Commander Daniel Ward, air component | Explains the cost of long-range coverage | Priorities that fit the available aircraft and tanker hours |
| Master Leila Santos, MV Coral Pioneer | A civilian perspective that returns throughout the campaign | A route her crew can actually use and instructions they can trust |
| Meridian duty controller | A changing mix of routine commerce, evasion and coercion | Early ambiguity; later evidence should distinguish individual actors |
| Opposing task-group commander | Professional, constrained military opponent | Complete the assigned pressure operation without losing an irreplaceable fleet |

Use short radio traffic, log extracts and debriefs. Avoid large fictional cabinet speeches between every mission. No nationality should make every fishing boat, merchant or airliner hostile.

## 5. Theatre and force rules

| Area | Narrative function | Build treatment |
|---|---|---|
| Darwin and Tindal | Northern support and command | Recurring recovery points; neither should spawn the whole national inventory |
| Timor and Arafura seas | Initial patrol, trade and offshore-service crisis | Merchant lanes, patrol vessels, helicopters, rigs and maritime aircraft |
| Banda and Seram seas | Escalating escort and naval encounters | Local objectives; separate mission maps prevent unnecessary world-scale simulation |
| Halmahera and the approaches toward Morotai | Coalition access and reconnaissance | Specific Indonesian permissions; hostile sites are fictional occupied positions |
| Biak and western New Guinea | Optional contested enclave linked to existing lore | Explicit fictional seizure; preserve the distinction between Indonesian Papua and PNG |
| Torres Strait and Coral Sea | Alternative supply route and Australian–PNG connection | Validate passage geometry; use appropriate hulls, not every merchant type everywhere |
| PNG ports and airfields | Relief, recovery and later resupply | PNG authorities and civilians remain visible participants |
| Western Australian approaches | Allied submarine arrival and logistics | Suitable for a separate episode instead of stretching every tactical map to Perth |

**Opening force allocation, purely a game-design assumption:** one Hobart-class destroyer, two Anzac-class frigates, one Collins-class submarine, one replenishment ship and one amphibious transport assigned across the opening act. A starting air detachment might contain eight F-35As, four Super Hornets, two Growlers, two P-8As, one Wedgetail, one Triton and two allied tankers. These are campaign allocations, not forecasts of actual deployability; only the subset relevant to the current mission spawns.

The remaining Australian fleet has other tasks, maintenance and transit commitments. A destroyed ship stays unavailable in the campaign ledger. An amphibious ship cannot be a disposable decoy. US, Japanese and French contributions arrive as named detachments with a mission, time window and exit condition. UK and European units protect the wider logistics chain in optional episodes.

Use modern opposing aircraft and ships already in the collection: J-10C/J-16/J-20 families, relevant special-mission aircraft, PLAN surface ships and conventional/nuclear attack submarines. Introduce the carrier after the player has encountered its scouts and supporting logistics. A modern escort should be dangerous because of the encounter design, not because every scenario grants it unlimited ammunition.

## 6. Main campaign: twelve missions

Mission durations below are design targets for active play. Long strategic transits occur between missions. Each chapter should have a normal and setback start state, without requiring an automated campaign engine.

| ID | Title and setting | Main task | Existing material to reuse |
|---|---|---|---|
| SW01 | White Water — Arafura approaches | Establish the picture and protect a civilian rendezvous | Living Seas traffic; Sanctioned Cargo encounter geometry |
| SW02 | Steel Highway — Coral Sea | Escort a priority supply convoy | SEST ANL Convoy – Coral Sea |
| SW03 | Rig Seventeen — Timor Sea | Cover an offshore evacuation | Living Seas platform and helicopter assets |
| SW04 | The Quiet Passenger — Banda approaches | Identify and track a suspected covert supply craft | Narco Transit |
| SW05 | Warramunga's Shot — Timor corridor | Defeat an armed interception attempt | Warramunga's Shot |
| SW06 | Blind Horizon — Arafura Sea | Maintain a usable maritime picture under pressure | Triton's Picture |
| SW07 | Long Way Home — northern air corridor | Bring a strike/patrol package home while protecting support aircraft | Foxhound Sweep |
| SW08 | The Open Door — fictional contested enclave | Open an evacuation/relief window | The Biak Regiment; Tigers over Papua |
| SW09 | Southern Lifeline — rear support area | Protect replenishment and a surfaced submarine service period | RE-power assets; RAN Fleet |
| SW10 | Common Sea — eastern Banda corridor | Pass a convoy through a submarine and surface threat | Mogami's Corner; Viper Zero; French support as a branch |
| SW11 | Fujian's Shadow — wider Banda approaches | Keep the corridor and high-value ships viable through a fleet encounter | Fujian's Shadow |
| SW12 | The First Ship Through — restored route | Escort the first post-crisis convoy and contain a spoiler | Living Seas traffic and campaign survivors |

### SW01 — White Water

**Player:** one Anzac, one helicopter and a P-8 or Triton support track; approximately 6–10 neutral vessels and a small opposing patrol group. **Target:** 35–50 minutes.

The player must locate Coral Pioneer, classify the armed escort and keep a relief vessel alive until rendezvous. Include at least one suspicious-looking but innocent contact and one straightforward rescue task. The same merchant hull must not always be the hostile one on replay.

**Win:** the designated relief/merchant group reaches the handover area and survives to the agreed time. **Fail:** the protected ship is lost or the scripted civilian-loss limit is exceeded. **Optional:** retain the patrol aircraft and complete the rescue. **Carry-over:** strong identification evidence gives an earlier warning message in SW05; poor information changes the briefing, not a magical weapon accuracy bonus.

No mission should require Identify Expanded: it is unsubscribed. Use existing identification orders, authored messages and time/area conditions. If a boarding mechanism is unavailable, represent inspection by a protected rendezvous and a timed message, clearly described as an abstraction.

### SW02 — Steel Highway

**Player:** an Australian escort group with four priority merchant ships, one support aircraft and limited reserve fighters. **Target:** 50–75 minutes.

PNG has requested a protected delivery of engineering equipment, medical stores and fuel. A submarine report disrupts the planned passage. Merchant masters want to continue; the escort wants time to classify the contact. Background shipping must not obediently form part of the player's convoy.

**Win:** at least three of four priority vessels reach the exit area, including the named medical/engineering ship. **Fail:** that essential ship is lost or fewer than three arrive before the cutoff. **Optional:** all four arrive and the escort helicopter returns. **Carry-over:** four arrivals give SW08 its better logistics start; three arrivals give the normal start; failure triggers a reduced-supply variant.

Use armed `ran_ms_*` auxiliaries only if the briefing explicitly describes armed support vessels. Prefer verified unarmed merchant types for ordinary civilian cargo.

### SW03 — Rig Seventeen

**Player:** Choules or Canberra, one escort and a small helicopter detachment. **Target:** 40–60 minutes.

A fictional offshore service platform has civilians trapped between armed contractors and an approaching patrol. The intervention is requested by the relevant coastal state. Not every platform in the map is hostile. The platform's military component must be represented separately where possible so destroying a whole civilian installation is not the only available interaction.

**Win:** evacuation transports complete their protected movement and survive. **Fail:** the designated transport is lost or the evacuation window closes. **Optional:** rescue an additional crew group without losing a helicopter. **Carry-over:** successful evacuation preserves partner confidence and adds a debrief from Santos.

Actual embarkation is a feature gate. If the game/mod combination cannot model it, use timed protected helicopter legs and an explicit “evacuation abstracted” designer note. Do not claim passenger tracking exists because the story mentions passengers.

### SW04 — The Quiet Passenger

**Player:** patrol vessel or frigate, maritime aircraft and helicopter. **Target:** 30–45 minutes.

A low-profile craft may be carrying weapons, smugglers or frightened crew. A confirmed hostile submarine is also operating in the wider area. Civilian craft and biologic contacts make classification matter, but they should not all spawn at the same bearing as the threat.

**Win:** track the designated craft into the patrol handover area while protecting the patrol ship. **Fail:** it escapes the monitored region or the patrol is lost. **Optional:** classify a second contact without engaging it. **Carry-over:** evidence identifies the support route used in SW09.

The existing `_narco_narcosub_adv` is a game representation, not evidence that armed narco submarines are a routine feature of the real Banda Sea. The core mission is tracking and interception; an explicitly armed variant can be an optional combat episode.

### SW05 — Warramunga's Shot

**Player:** HMAS Warramunga, its helicopter and a short support-aircraft window. **Target:** 30–45 minutes.

An opposing armed escort is trying to turn back a protected convoy. The player must establish the target, engage the military threat and get Warramunga clear. Merchant hulls should not become valid targets merely because the designer placed “[SANCTIONED]” in their names.

**Win:** the hostile escort is neutralised or withdraws, and the protected convoy passes. **Fail:** the priority merchant or Warramunga is lost. **Optional:** preserve a useful anti-ship magazine for later chapters. **Carry-over:** the surviving frigate returns in SW10; its expended weapons affect the ledger.

Retain the current Anzac model and NSM integration. Avoid briefing claims that the weapon outranges every possible opponent; the actual winning ammunition and opponent combination decide that in this installation.

### SW06 — Blind Horizon

**Player:** a Hobart, Triton, two fighters and limited Wedgetail support. **Target:** 35–55 minutes.

The destroyer can defend the convoy but lacks a consistent picture beyond its local horizon. Triton locates the opposing surface group while hostile fighters attempt to drive it off. The player chooses between more information now and retaining the aircraft for tomorrow.

**Win:** the convoy reaches its passage window while the reconnaissance asset survives. **Fail:** the protected convoy is lost. **Optional:** maintain the surveillance condition for the required period. **Carry-over:** losing Triton reduces warning quality in SW11 through different starting contacts and messages, rather than an unimplemented global intelligence system.

Prove the actual contact-sharing behaviour in game. If there is no trustworthy trigger for sensor-track state, define the objective around an observable patrol area/time condition and label the approximation in designer notes.

### SW07 — Long Way Home

**Player:** a returning Australian flight, support aircraft and a small allied fighter detachment. **Target:** 35–50 minutes.

A weather diversion and a long patrol have consumed the margin in the day's flying program. A hostile interceptor section approaches while the tanker is still needed by aircraft returning from another mission. The mission is won by recovery, not by pursuing every contact.

**Win:** the named tanker and a minimum surviving flight reach recovery/exit conditions. **Fail:** the tanker or mandatory returning aircraft are lost. **Optional:** keep Wedgetail available. **Carry-over:** saved support aircraft make the broader SW11 air allocation available.

Foxhound Sweep provides a compact encounter seed. In the main story the Russian aircraft require an established fictional detachment; a Chinese interception variant offers a simpler alternative. Verify tanker/receiver compatibility and fuel transfer; a “Tanker” label alone is insufficient.

### SW08 — The Open Door

**Player:** Australian Growler/Super Hornet/F-35 elements, with a bounded allied contribution. **Target:** 45–70 minutes.

The contested enclave is preventing relief access. Local authorities request a temporary protected window to move civilians and emergency supplies. Air-defence suppression and a follow-up strike on a confirmed military launcher support that window; neither should require destroying an entire regional industrial complex.

**Win:** the evacuation/relief aircraft or ships complete their passage. **Fail:** the protected movement is destroyed or the window expires. **Optional:** neutralise the specific military battery and recover all support aircraft. **Carry-over:** success grants the improved SW10 staging option; failure produces a longer route.

The Biak Regiment and Tigers over Papua supply units and encounter patterns. Their occupied-territory premise is fictional. Change the primary objective from a generic kill count to the passage outcome. Keep anti-radiation and strike fits within the chosen core-era rules.

### SW09 — Southern Lifeline

**Player:** replenishment group, escort, helicopter and one Collins-class submarine requiring service. **Target:** 45–65 minutes.

The submarine returns to a friendly rear rendezvous after a difficult patrol. Fuel, provisions, minor service and crew transfer are the immediate problem. An enemy scout or limited raid threatens the service window. Other vessels may support the submarine when the intended donor/receiver mechanics have been demonstrated.

**Win:** support ship and submarine survive the required service window and the group can withdraw. **Fail:** either essential unit is lost. **Optional:** retain both escorts' readiness. **Carry-over:** a completed service restores a defined campaign availability token; it does not silently restore every weapon.

**User requirement retained:** submarine transfer requires the boat to surface, approach a designated support ship and remain within the validated transfer limits. If a mod allows submerged transfer, impose a documented house rule unless a tested script enforces the restriction. Treat torpedo/missile reloads as tender/port work or a between-mission abstraction unless the chosen gameplay mode explicitly proves and labels a broader mechanic. Nuclear-reactor refuelling is not an at-sea replenishment objective.

The current Supply stand-in needs verification or a reviewed support patch before it becomes a functional donor. A tested RE-power donor is an interim game option with its identity disclosed.

### SW10 — Common Sea

**Player:** Australian escort plus a Japanese Mogami detachment; choose one allied air-support branch. **Target:** 50–75 minutes.

The convoy crosses a patrol area where submarine and surface threats overlap. Japanese ASW contributes something the depleted Australian force needs. An F-2A detachment or a French maritime-strike sortie supports a separate part of the operation; do not put every allied carrier on the same map.

**Win:** the priority convoy reaches the handover point. **Fail:** the protected cargo threshold is missed. **Optional:** preserve the allied escort and locate the submarine. **Carry-over:** good results make an allied detachment available in SW11; poor results move it to casualty support.

Mogami's Corner and Viper Zero are useful seeds. Rafale, Timor Gap belongs here as an optional mission using a verified conventional fit. Its current SEST F5 LRASM fit belongs in Future Front unless deliberately accepted as campaign fiction.

### SW11 — Fujian's Shadow

**Player:** the surviving Australian force and one bounded US carrier contribution. **Target:** 60–90 minutes, with a smaller variant.

The opposing carrier group attempts to close the corridor for the final negotiating period. The player has to keep the transports and essential support assets viable through the encounter. The enemy may withdraw after a failed strike; the player should not have to chase it across the entire ocean to win.

**Win:** the protected transport group passes and the designated coalition high-value ship survives to the endpoint. **Fail:** either protected condition is broken. **Optional:** force the opposing carrier to withdraw or inflict mission-limiting damage. **Carry-over:** surviving ships, aircraft and civilian losses determine the final convoy variant.

The existing Fujian's Shadow says to protect Ford but its generator currently awards victory on destruction of the enemy carrier. Correct that mismatch in the new campaign version. Keep core ballistic-missile dependence out until the separate BMD/intercept work is integrated and its relevant behaviour tested. A specialist missile-defence version can then be added.

### SW12 — The First Ship Through

**Player:** the actual surviving escorts, a small support-aircraft allocation and a civilian convoy. **Target:** 45–65 minutes.

The ceasefire is imperfect and some traffic has begun moving again. Coral Pioneer returns. One group is complying with withdrawal orders; another may be preparing a spoiler attack. The player must distinguish them while an essential cargo ship develops a machinery problem.

**Win:** the required cargo reaches its destination and civilian-loss conditions remain satisfied. **Fail:** the protected convoy is lost or the ceasefire/civilian fail state is triggered. **Optional:** rescue additional survivors and preserve the withdrawing contact. **Ending:** derive the debrief from delivery, force survival and civilian protection, not total enemy kills.

The final view should resemble a working sea: coasters, tankers, aircraft and patrols moving again. This is the payoff for the user's Living Seas additions.

## 7. Equipment truth and exact implementation choices

The identifiers below were resolved from the pinned snapshot. Re-resolve them after branch integration. A valid identifier does not guarantee a correct model, livery, flight deck or weapon fit.

| Campaign role | Existing identifier / setting | Build note |
|---|---|---|
| Australian air-defence destroyer | `ran_ddg_hobart` | SEST F-100-based representation; select the actual magazine and do not assume every real upgrade is modelled |
| Australian frigate | `ran_ffh_anzac` | Current Anzac model. `Variant3` = Warramunga, `Variant8` = Perth. Avoid `Variant1`/HMAS Anzac in the core unless recommissioning is explicit fiction |
| Australian conventional submarine | `ran_ssg_collins` | Resolves under the collection's vessel files; S-80 model is a stand-in. Do not claim the donor's acoustics are verified Collins performance |
| Amphibious support | `ran_lhd_canberra`, `ran_lsd_choules` | Canberra's allowed-aircraft list inherits Spanish fixed-wing types; use an explicit helicopter-only campaign air group. Choules uses a Galicia stand-in |
| Replenishment | `ran_aor_supply` | Teide stand-in; gameplay supply mechanism unproven in the inspected file |
| Patrol vessel | `ran_opv_arafura` | Meteoro stand-in with donor weapon options including AntiShip/AntiAir. Restrict the core fit; do not present its donor armament as real Arafura equipment |
| F-35A | `raaf_f-35a` | Tindal's 75 Squadron is `Squadron3`; `Squadron4` is 2 OCU, not a generic combat squadron. `AirToAirStealth` exists; verify its actual weapons |
| Super Hornet | `usn_fa-18f_blk3`, Australian `Squadron8` | Australian nation entry exists in SEST output; donor is a US Block III representation, so identify the fit approximation |
| Growler | `usn_ea-18g`, Australian `Squadron6` | Use current ID and checked loadout. `SEST_NGJLongRange` exists; do not silently choose `SEST_MaliceNGJ` in the core |
| Wedgetail | `E7A_Wedgetail` | Deprecated Workshop source is still an enabled dependency; SEST also provides squadron work |
| Poseidon | `usn_p8`, Australian `Squadron3` | `ASW` and `AntiShip` are available. Do not infer an LRASM fit from the real-world firing announcement |
| Triton | `raaf_mq-4c_triton` | SEST unit uses an MQ-9 ER mesh; unarmed in this implementation |
| Tanker support | `usaf_kc-46a_boom` / `usaf_kc-46a_warp`, `Tanker` | Use as US support. No dedicated KC-30A unit was found by the reviewed filename searches; confirm broader inventory before proposing a new asset |
| Helicopters | `usn_mh-60r` and `usn_mh-60r_26` | Different IDs. Australian ship support lists often name the former; do not substitute the latter without a deck check. RAN livery is not verified by the unit name |
| Allied fighter | `usaf_f-15ex_SEII` | USAF detachment, not a real RAAF F-15 fleet. Keep speculative fits in the explicit fiction tier |
| Allied attack aircraft | `usa_a-10c` | Current SEST-modified unit; do not use the absent `usaf_a-10c_plus` ID |
| Japanese escort | `js_ffg_mogami` | JMSDF in the 2028 core; current supported helicopter IDs include `jp_sh-60k` and `jp_sh-60j` |
| US carrier | `usn_cvn_ford` | Winner is Workshop `3461044389`; declared capacity 90 is a game ceiling, not the desired mission allocation |
| Opposing carrier | `plan_cv_type_003` | Actual winner here is Workshop `3663564190`, capacity 85. Do not pick a Fujian owner from old catalog prose; several mods contain carrier alternatives |
| Opposing escorts | `plan_type_055_2026`, `plan_type_052d_p3`, `plan_type_054a_p5` | Resolve each fit and supporting aircraft against the current PLAN pack |
| Opposing AEW | `plaaf_kj-500` | Explicit `LoadoutVariant=AEW` required; the available list has no `Default` |
| RQ-180 | `usaf_rq-180` | The mod exposes combat and nuclear loadouts. Treat those as speculative mod content; do not use them as factual capability evidence |
| Future aircraft | `plaaf_j36`, production YF-23 and J-50 family | Future Front only; performance and operational status are authored assumptions |

**Core armament rule:** choose conventional loadouts with publicly grounded roles, then verify what their definitions actually contain. A reasonable name does not prove a reasonable fit. JATM performance, MALICE/AIM-424, Rafale F5 LRASM and other custom combinations must be disclosed as fiction when used. Nuclear-capable mods can remain enabled without putting nuclear weapons into campaign magazines.

**Capacity rule:** the three inspected SEST Tindal/Darwin/Scherger base files each declare 200 aircraft; `airfield_small_1` declares 48, `wp_airbase_57` 36 and `airfield_a-10` 80. These are game limits. Count all assigned flights, incoming recoveries and reinforcements, and keep the mission allocation well below the ceiling. Airfield capacity is unrelated to how many aircraft the real base can sustain in a crisis.

## 8. Reuse all twelve existing Banda vignettes

| Existing vignette | Campaign placement | Necessary adaptation |
|---|---|---|
| Sanctioned Cargo | SW01 and a later interdiction side mission | Retain classification pressure; replace blanket sanctioned-cargo sink objectives with individually established military threats and protected traffic |
| Warramunga's Shot | SW05 | Protect the convoy, preserve the frigate, and remove universal weapon-superiority claims |
| Fujian's Shadow | SW11 | Align scripted victory with transport/carrier protection; enemy carrier loss becomes optional |
| The Biak Regiment | SW08 | Establish fictional occupation and partner consent; tie the strike to a relief window |
| Narco Transit | SW04 | Tracking/interception primary; combat variant only with an explicitly armed threat |
| Tigers over Papua | SW08 follow-up / Allied Dispatch | Distinguish Indonesian Papua from PNG, verify strike loadout and target identity |
| Viper Zero | SW10 Japanese air-support branch | Plausible forward detachment, bounded sortie allocation and access arrangement |
| Foxhound Sweep | SW07 / Red Line | Establish the Russian detachment in fiction or substitute a Chinese interceptor variant |
| Mogami's Corner | SW10 | Protect passage; retain fishing traffic and use a supported helicopter |
| Triton's Picture | SW06 | Make surveillance/survival the central objective; test contact sharing |
| Black Widow Debut | Future Front | Clearly alternate history; production YF-23 and J-36 capability assumptions are part of the fiction |
| Rafale, Timor Gap | Allied Dispatch / Future Front | Conventional verified Rafale fit for 2028; SEST F5 LRASM version in the future branch |

Additional optional episodes give the wider collection purposeful roles:

- **Western Passage:** a British, Dutch, German, Nordic or Italian escort rotation protects a replenishment group approaching the theatre. Select one national detachment per variant.
- **Flight Deck Day:** a US carrier aviation episode focused on recovery, aircraft handling and support, using the deck-operation and aviation mods.
- **The Relief Ship:** French or Spanish amphibious units assist a regional evacuation, with helicopter activity tested before making it an objective.
- **Red Line: Return Passage:** play a Russian or Chinese escort trying to bring a damaged auxiliary home among neutral shipping. It shows the opponent's logistics burden without changing the main story's objectives.
- **Range Week:** explicitly simulated trials for THAAD, David's Sling, Scud, Sejjil, Iskander, Type 12 and drone systems that would otherwise force improbable regional deployments. Real-world ownership is retained in the scenario notes.
- **Future Front: Long Reach:** advanced missiles, RQ-180 mod fits, J-36/J-50, YF-23 and Type 004 in an openly speculative crisis. This is where the collection's experimental systems can be central rather than hidden exceptions.
- **Cold Sea: Before the Lifeline:** historical or exercise episodes for older carriers, bombers, fighters and helicopters. Their presence in the collection remains useful without asserting that every retired type returned in 2028.

## 9. A campaign that can actually be implemented

### What persists

Start with a manual, readable campaign ledger. The repository inspection did not establish automatic cross-mission state persistence. Prebuilt normal/setback mission variants are enough for the first release.

| Ledger field | What to record | How it changes the next mission |
|---|---|---|
| Escorts | Surviving named hulls; unavailable/damaged status | Remove lost hulls and substitute a smaller force where appropriate |
| Air support | Wedgetail, Triton, tanker and fighter availability | Select a reduced-warning or reduced-air-support variant |
| Cargo | Essential deliveries and optional deliveries | Determines which relief/staging option is available |
| Magazines | Simple remaining-availability bands, not invented exact logistics | Full / limited / exhausted strike or air-defence allocation in the next authored start |
| Civilian protection | Named losses and completed rescues | Debrief consequences and ending gates; never offset civilian failure with an unrelated kill score |
| Regional access | Specific mission permissions unlocked by story outcome | Changes staging location or route, not national ownership of a base |

Example: SW02 with four arrivals selects `SW08_Normal`; three arrivals selects `SW08_LimitedSupply`; failure selects `SW08_DelayedRelief`. Keep these names in a designer manifest. Do not make the player edit INI files to continue.

### Observable objectives

Every objective must name an observable condition, an endpoint and a priority. Arrival areas, survival at a time, loss of a named unit and explicit mission termination are easier to prove than abstract “sea control”, “boarding complete” or “political confidence”. If a desired mechanic is unsupported, use a disclosed abstraction or delay that objective.

Resolve protected-ship and civilian failures before awarding victory in the same update. Add an explicit normal finish path; the current vignette generator's mission-exit trigger is disabled initially and its defeat path enables it, so copying it does not establish a reliable success termination. The existing neutral-loss handler can fail an objective without independently proving that overall victory is prevented. Test both cases.

### World density

For the first build, target roughly 20–45 placed units per small mission and 45–80 for the larger fleet missions, before dynamically launched aircraft. These are starting budgets, not measured engine limits. Profile the user's PC before expanding them.

Background traffic should have origins, destinations and understandable behaviour: merchants continue, some divert, relief ships join a convoy, and fishing boats do not all turn toward the battle. Use several short route templates with offsets. Repeating circuits are acceptable for bounded patrols, but an endlessly circulating airliner should not be presented as an international flight.

Preserve named formations and established safe passages from the user's saves. A route copied from a parent mission is a starting point, not proof that it is safe for a different ship, submarine depth or larger formation. Do not reuse a world-scale parent with hundreds of inactive land units just to keep its background scenery.

### First release scope

1. Freeze the current intended branch/load-order baseline and decide the BMD/intercept integration separately.
2. Build SW01, SW02 and SW06 as a playable vertical slice: identification, escort and surveillance. These establish the campaign's central experience using available units.
3. Add SW03 only after helicopter movement and evacuation abstraction are demonstrated.
4. Add SW09 after donor/receiver transfer, submarine surfacing and resource limits are proved; use a survival-and-service-window objective in the interim.
5. Build the remaining main missions and the ledger variants; then add Allied Dispatches and Future Front.

Suggested repository homes are `docs/campaigns/southern-watch/` for the bible and source notes, `integration/missions/southern_watch/` for the manifest/build inputs, and the installer's supported mission output directory for the emitted INIs. Confirm nested-directory deployment support before choosing nested output. Keep mission names prefixed `SEST Southern Watch` to make ownership clear.

### Build acceptance criteria

- Resolve unit types, aliases, ammunition, `AvailableLoadouts`, squadron references and vessel variants using the intended enabled order. The resolver currently also falls back to exported mods absent from the canonical order, so explicitly check enabled membership when proving a dependency.
- Validate air groups as well as airborne units. Aircraft can have valid files and invalid squadron indices. Preserve aircraft counts when remapping an index.
- Check helicopter support lists, aircraft capacity and recovery behaviour on the exact recipient. Do not infer compatibility from another aircraft in the same family.
- Check that neutral merchant hulls are unarmed where the story requires that, that civilian aircraft are on the neutral side, and that scenario weapon-control settings match the opening situation. The current vignette helper uses `WeaponStatus=Free` broadly; do not inherit it blindly for identification missions.
- Keep the five unsubscribed entries excluded. Keep source-dependent deprecated entries such as Wedgetail and the current Anzac enabled where still required.
- Validate the ordinary victory route, an early defeat, a civilian-loss case, timeout, save/reload, and return to menu. Run the mission long enough to expose recovery and delayed-trigger behaviour.
- For replenishment: prove transfer begins, the donor loses supply, the recipient gains the intended resource, limits are respected, and transfer ends when separation or the prescribed surfaced condition is broken. If surfacing is a house rule, say so.
- For the BMD branch: verify the actual integrated altitude/speed/intercept behaviour before making success depend on it. Preserve the vanilla impact-table correction if included; do not assume earlier branch work survived consolidation.
- Require an in-game visual and behavioural smoke test. Static checks do not validate pylon positions, textures, invisible weapons, helicopter decks or AI route choice.

Use existing tools first, naming the mission explicitly. For example, after SW01 has actually been generated:

```bash
python3 tools/preflight.py "SEST Southern Watch 01 - White Water"
python3 integration/missions/fix_squadron_refs.py --mission "SEST Southern Watch 01 - White Water"
python3 integration/missions/fix_loadout_variants.py --mission "SEST Southern Watch 01 - White Water"
python3 tools/check_load_order.py
python3 tools/check_dependencies.py
```

The two repair tools above are shown in report mode. Review their proposed changes before using `--write`. Check the current CLI for the weapon-employment and station-clash tools when adding the relevant gates. A from-scratch pack rebuild is appropriate after changing the pack inputs; it is not evidence of an in-game mission test.

## 10. Opening briefing draft

**SEST Southern Watch 01 — White Water**

*Arafura Sea, 18 October 2028, 0540 local.*

Coral Pioneer missed her scheduled rendezvous forty minutes ago. Her last report mentioned an engine casualty and an escort claiming authority to inspect the convoy. The Indonesian patrol sent to investigate has reported gunfire. We have no confirmed picture of what happened next.

Warramunga is the nearest coalition ship. Locate the merchants, establish which contacts are armed, and keep the rendezvous open for the relief vessel. Indonesian authorities have requested assistance within the patrol area shown on your chart.

A maritime patrol aircraft is available for the first part of the operation. Civilian shipping is still moving through the area. Expect fishing vessels, merchant traffic and a scheduled passenger flight. None is a target without identification of a threat.

Your immediate task is to bring the convoy together and get its crews out of danger. Report any wider military activity. Further instructions will follow when we have a reliable picture.

**Primary:** protect the rendezvous and escort the designated merchant group to the handover area.

**Secondary:** retain the patrol aircraft and complete the rescue task if conditions permit.

**Mission failure:** loss of the designated relief ship or breach of the scripted civilian-protection condition.

## 11. Decisions fixed for the first build

The first release is set in 2028, uses conventional weapons, keeps Australia central and treats Indonesia, Timor-Leste and PNG as sovereign actors. The full enabled collection remains available. Experimental equipment is used openly in optional fiction. Existing missions and exported user saves are reference material and retain their identities; Southern Watch receives its own mission files.

The three priority engineering questions are **which branch becomes the approved combined baseline**, **which exact donor/receiver pair supports submarine service**, and **which objective conditions the game reliably exposes**. Those questions affect implementation, but none prevents writing or building the first patrol/escort/surveillance slice.

The first scenario to build is **SW01 — White Water**, followed by **SW02 — Steel Highway** and **SW06 — Blind Horizon**. Together they establish the setting and test the core Australian fleet, civilian traffic, aircraft support and mission logic before the campaign grows.


## Appendix A. Complete Workshop coverage

Every enabled Workshop token is listed below in canonical load order. Position includes `SEST_Integration` at position 1, so Workshop positions begin at 2. “Role” is the proposed campaign use, not an assertion that every file in that mod wins or has been tested. Some packs are required donors, overlapping alternatives, UI tools or shared systems. Keep those enabled without forcing them to spawn an extra unit.

| Order | Workshop ID | Catalog title / status | Campaign role |
|---:|---|---|---|
| 2 | `3380210757` | Anchor Chain — active | Support: framework dependency; keep enabled in canonical position. |
| 3 | `3784474738` | Euromod - Anchorchain Expansion Pack — active | Support: framework expansion and well-deck-related content; test actual mechanics before objectives. |
| 4 | `3789188689` | PLA & PLAN & PLAAF AEP — active | Support / Opposition / Range Week: framework ordnance layer; check patch mechanics as well as whole files. |
| 5 | `3606134711` | Custom Loadout Editor — active | Support: authoring aid and companion content; bake reviewed mission fits into the release. |
| 6 | `3768036424` | Better TacMap — active | Support: player interface throughout the campaign. |
| 7 | `3789793270` | Auto Time-on-Target — active | Support: optional player salvo-planning convenience; campaign must remain completable without perfect synchronisation. |
| 8 | `3437105712` | SAM Pack — active | Support / Opposition / Range Week: choose systems by nation and scenario; check radar-launcher pairing. |
| 9 | `3733719765` | PLA Land Unit Pack — active | Opposition: small, explained military sites and air defence; no blanket hostile cities. |
| 10 | `3760871384` | Dingtools Weapon Pack — active | Support: required shared weapon owner; speculative systems in Future Front. |
| 11 | `3606774881` | U.S. Navy 2027 Capabilities mod — active | Support / Allied Dispatch: current capability overrides; the retired SEST fixes pack is separate. |
| 12 | `3629144864` | Euromod - Main Pack — active | Support: shared European/RAN systems and donor dependency. |
| 13 | `3775128499` | Modern PLAN Systems — active | Support / Opposition: principal PLAN systems and several winning units. |
| 14 | `3637954857` | Y-8/Y-9 Special Mission Aircraft Family — active | Support: intentional overlapping special-mission-aircraft source; do not force duplicate spawns. |
| 15 | `3607989779` | F-35C Lightning II Alt. Loadouts — active | Support / Allied Dispatch: carrier loadout source; separate conventional and speculative weapons. |
| 16 | `3430135740` | F/A-18 Murder Hornet with AIM-174B — active | Support: Super Hornet/Growler loadout layer; select fits deliberately. |
| 17 | `3394781441` | B-52G with AGM-86 (realistic nuke) — active | Support / Cold Sea: bomber and weapon source; nuclear and fictional anti-ship fits excluded from core. |
| 18 | `3395022688` | Tu-95 With AS-15 (Kh-55) ALCM (more realistic nuke) — active | Support / Cold Sea / Red Line: conventional bomber options; review global impact changes, no core nuclear fits. |
| 19 | `3373960386` | Flight Deck Ops — active | Support / Allied Dispatch / Cold Sea: carrier variants and deck mechanics; no extra carrier required in core. |
| 20 | `3461091581` | Air Deck Operations Upgrade - Nimitz (2000s) — active | Support / Allied Dispatch / Cold Sea: carrier variants and deck mechanics; no extra carrier required in core. |
| 21 | `3508275114` | Ground Upgrade: SPAA — active | Support: ground-unit and weapon changes affecting existing encounters. |
| 22 | `3438479626` | 1143.5 Kuznetsov — active | Cold Sea / Red Line alternate: separate carrier episode, not a mandatory 2028 deployment. |
| 23 | `3440622312` | [DEPRECATED] Anzac Class Frigate — deprecated | Core: actual Anzac hull donor now patched by SEST; keep despite deprecated catalog label. |
| 24 | `3432668460` | Auxilliary Merchant Pack — active | Core logistics: ANL/RAN auxiliaries; distinguish armed auxiliaries from neutral merchants. |
| 25 | `3567256221` | Charles De Gaulle & Modern French Navy Pack (WIP) — wip | Allied Dispatch: French group or relief episode; WIP content needs smoke testing. |
| 26 | `3695809489` | Euromod - Modern Japanese Maritime Self Defence Force — active | Allied Dispatch: Japanese escort and support variants. |
| 27 | `3575847216` | Euromod - Modern German Navy — active | Allied Dispatch: one national escort/support rotation per scenario variant. |
| 28 | `3444379330` | Euromod - Modern Dutch navy — active | Allied Dispatch: one national escort/support rotation per scenario variant. |
| 29 | `3642656500` | Euromod - Modern Nordic Navy — active | Allied Dispatch: one national escort/support rotation per scenario variant. |
| 30 | `3461044389` | Gerald R. Ford-class CVN Aircraft Carrier (Updated Dependencies) — active | Core late act: limited US carrier support in SW11; exact air group and recovery checks. |
| 31 | `3384079999` | Humpback Whale — active | Civilian world: biologic contacts; place in plausible seasonal sectors, validate geography before release. |
| 32 | `3505420313` | Italian Navy Mod — active | Support / Cold Sea: older Italian fleet and cross-pack shared systems. |
| 33 | `3406985435` | Kirov-class (Pyotr Velikiy Upgrade) — active | Red Line / Cold Sea alternate: rare capital-ship episode; do not add simply for scale. |
| 34 | `3430106996` | Merchants Expanded — active | Core civilian world: merchant variety, route-based traffic and convoy hulls. |
| 35 | `3417446309` | MIG-29 Family — active | Red Line / Cold Sea: fighter family; Orel carrier belongs in an alternate-history episode. |
| 36 | `3599752717` | Euromod - Modern British Navy — active | Allied Dispatch / Support: British escort rotation and shared systems. |
| 37 | `3488139470` | Euromod - Modern Italian Navy — active | Allied Dispatch: Italian escort rotation; retain shared dependencies. |
| 38 | `3390330875` | Modern US Navy — active | Core late act / Allied Dispatch: modern US escorts, aircraft and submarine options. |
| 39 | `3456859157` | Mogami-class Frigate — active | Core allied partner: Japanese ASW escort in SW10; source for SEST patch. |
| 40 | `3432592449` | Nimitz Expanded — active | Support / Allied Dispatch / Cold Sea: carrier variants and deck mechanics; no extra carrier required in core. |
| 41 | `3594891803` | PLAN Submarines — active | Opposition: submarine threat for SW02, SW04 and SW10. |
| 42 | `3774859959` | PLAN Type 001 Aircraft Carrier Liaoning — active | Opposition alternate: swap the carrier group for replay, rather than adding a second major fleet. |
| 43 | `3774572038` | PLAN Type 071 Amphibious Transport Dock — active | Opposition / Red Line: support and amphibious transport objective, including Viper Zero seed. |
| 44 | `3663564190` | Type 003 Aircraft Carrier - PLANS Fujian CV-18 — active | Core opposing carrier: current owner of plan_cv_type_003; SW11. |
| 45 | `3436170138` | Shenyang J-11 — active | Opposition: distinct Flanker variants; avoid flooding the map with every subtype. |
| 46 | `3486502935` | Type 003 Fujian / Type 004 CVN Aircraft Carriers — active | Support / Future Front: alternative carrier content and speculative Type 004; resolve actual winners. |
| 47 | `3417801942` | Chinese Navy (PLAN) — active | Opposition / Support: PLAN and legacy hulls; overlapping carrier files require winner resolution. |
| 48 | `3597650470` | Russian Navy 21 — active | Opposition / Red Line: frigate and corvette detachment; paper designs in Future Front. |
| 49 | `3468260539` | Russian Submarines (Yasen, Akula, Sierra I/II, Oscar II, Belgorod, Typhoon, Delta IV classes) — active | Red Line / optional opposition: limited Russian submarine presence. |
| 50 | `3403661005` | [DEPRECATED] S-70B-2 Seahawk with AGM-114 'Hellfire' Missiles — deprecated | Support / Cold Sea: legacy helicopter and existing pack dependency; modern core prefers MH-60R. |
| 51 | `3630495619` | Euromod - Cold War Spanish Navy — active | Support / Cold Sea: Teide donor for Supply representation and historical fleet. |
| 52 | `3731208477` | Euromod - Modern Spanish Navy — active | Support / Allied Dispatch: RAN design/stand-in donors and optional Spanish deployment. |
| 53 | `3378409795` | Royal Navy Type 23 'Duke Class' Frigate [OLD] — deprecated | Cold Sea / Allied Dispatch alternate: separate hull IDs; use intentionally, not as duplicate escorts. |
| 54 | `3590477166` | MH-60R Seahawk — active | Core / Support: Seahawk source; reconcile unit and squadron ownership. |
| 55 | `3737267013` | United States Naval Aviation — active | Core / Support: source for allied and Australian-representative aviation and weapons. |
| 56 | `3433957933` | Virginia-, Seawolf-, and Ohio-class Submarines — active | Allied Dispatch: US SSN reinforcement, retaining US identity in 2028. |
| 57 | `3602046770` | Boeing P-8 Poseidon — active | Core: maritime patrol, ASW and surveillance using Australian Squadron3. |
| 58 | `3414146266` | A-10A Thunderbolt II — active | Support / Cold Sea: A-10 model dependency and historical aircraft. |
| 59 | `3459682829` | A-10C — active | Allied Dispatch: current usa_a-10c upgrade; forward assignment is a fictional campaign allocation. |
| 60 | `3425450153` | AH-64 Apache — active | Allied Dispatch / relief-perimeter episode: verified operator/livery and bounded allocation. |
| 61 | `3403993583` | Armed Oil Rig with Helo MOD — active | World / SW03: platform objective; armed version needs explicit hostile military role. |
| 62 | `3652097318` | B-1B Lancer — active | Allied Dispatch: finite US maritime/stand-off strike support; custom fits labelled. |
| 63 | `3480965706` | B-2 Spirit — active | Allied Dispatch: rare US strike allocation; conventional fit and limited availability. |
| 64 | `3741944366` | B-52H Stratofortress — active | Allied Dispatch: bounded US bomber contribution; advanced/custom fits in Future Front. |
| 65 | `3524112296` | Soviet AEW&C + Transport Aircraft (A-50 / Il-76) — active | Opposition / Red Line: tanker, transport and AEW support with finite availability. |
| 66 | `3744475027` | KC-46A Pegasus - Strategic Tanker — active | Allied support: tanker availability and recovery problems; verify receiver compatibility. |
| 67 | `3600788156` | Buildings and Targets for Missions — active | World / Support: scenery and defined military objectives with restrained land-unit counts. |
| 68 | `3801363152` | CH-53E Standalone v0.1.0 — active | Allied Dispatch / SW03 option: helicopter lift; verify deck support, livery and early-release reliability. |
| 69 | `3746453639` | Civil Aircraft Mod (Airbus Family) — active | Civilian world: scheduled air traffic, diversions and evacuation context. |
| 70 | `3504168760` | Dassault Rafale — active | Allied Dispatch: conventional French maritime aviation; F5/custom weapons in Future Front. |
| 71 | `3781062859` | <<E-3G>> — active | Allied Dispatch: US command-and-surveillance reinforcement. |
| 72 | `3499239964` | [DEPRECATED] E-7A Wedgetail — deprecated | Core: Wedgetail source for SW06–07; deprecated but required by current SEST work. |
| 73 | `3587877691` | Eurofighter Typhoon — active | Allied Dispatch / exercise: a defined European air detachment. |
| 74 | `3448845252` | F-117 Nighthawk — active | Cold Sea / exercise: specialist legacy stealth strike; no routine 2028 fleet claim. |
| 75 | `3636386513` | F-15 EX Eagle II — active | Allied Dispatch: USAF aircraft and SEST donor; not RAAF-owned. |
| 76 | `3553116604` | F-15E StrikeEagle — active | Allied Dispatch: conventional USAF strike reinforcement and shared donor content. |
| 77 | `3758320372` | F-16C Fighting Falcon (modern) — active | Allied Dispatch: US fighter detachment and separate optional upgraded fit. |
| 78 | `3418252667` | F-22 Raptor — active | Allied Dispatch: limited protective fighter element, especially SW07. |
| 79 | `3755769170` | F-2A 'Viper Zero' — active | Core allied branch / SW10: Japanese maritime-strike detachment, not Australian-owned. |
| 80 | `3736147136` | French Army Vehicles — active | Allied Dispatch: relief perimeter, liaison or limited land-support set dressing. |
| 81 | `3567228449` | French Helicopter Package — active | Allied Dispatch: evacuation and shipborne helicopter activity; prove supported mechanics. |
| 82 | `3503670861` | General Atomics MQ-9 Reaper — active | Support / Allied Dispatch: Triton mesh dependency and US UAV detachment; not an assumed RAAF fleet. |
| 83 | `3717610332` | IL-78 TANKER — active | Opposition / Red Line: tanker, transport and AEW support with finite availability. |
| 84 | `3506979898` | Shenyang J-16A (歼-16A 潜龙) — active | Opposition: one J-16 implementation; avoid accidental duplication with the other pack. |
| 85 | `3769142422` | J-16 Multirole Fighter — active | Opposition: second J-16 implementation with separate IDs; choose deliberately. |
| 86 | `3591563716` | J-20 (歼-20 威龙) — active | Opposition: bounded advanced fighter element in later missions. |
| 87 | `3801549552` | J-36 Tailless Fighter — active | Future Front: speculative tailless aircraft and Black Widow Debut opponent. |
| 88 | `3670643788` | Shenyang J-50 (沈阳航空工业 歼-50) — active | Future Front: speculative advanced-aircraft episode. |
| 89 | `3481228992` | ChengDu J-10C Vigorous Dragon — active | Opposition: modern land-based fighter encounter. |
| 90 | `3526982088` | XIAN JH-7A (歼轰-7A 飞豹) — active | Opposition: limited maritime-strike element. |
| 91 | `3776340577` | Ka-27RLD — active | Red Line: shipborne AEW option; validate the mod identity and deck compatibility. |
| 92 | `3740293822` | McDonnell Douglas KC-10A Extender - Strategic Tanker — active | Support / Cold Sea: existing base references and historical tanker; any 2028 return is explicit fiction. |
| 93 | `3722749887` | KC-135 STRATOTANKER — active | Allied support: tanker availability and recovery problems; verify receiver compatibility. |
| 94 | `3559495372` | Lockheed AC-130 Pack — active | Allied Dispatch / exercise: permissive support episode; not routine entry into intact modern air defence. |
| 95 | `3458148344` | Mi-8EW — active | Red Line / Cold Sea: utility lift and EW support in a defined fictional enclave. |
| 96 | `3465256032` | Mi-8 T/TV — active | Red Line / Cold Sea: utility lift and EW support in a defined fictional enclave. |
| 97 | `3416372890` | Apex Predators MIG-29A & F-16A — active | Cold Sea / exercise: earlier-generation adversary and allied aircraft. |
| 98 | `3799742828` | MiG-31 Foxhound — active | Red Line / SW07 alternate: explained expeditionary interceptors; advanced strike variant separate. |
| 99 | `3659742367` | MiG-35 Fulcrum-F (米格-35 支点-F) — active | Red Line / exercise: Russian or explicitly fictional export detachment; no unexplained mass deployment. |
| 100 | `3513571010` | Mil Mi-24 Hind — active | Red Line / Cold Sea: armed rotary-wing support in a finite local encounter. |
| 101 | `3716049886` | MORE SU-24M VARIANTS — active | Red Line / exercise: Russian or explicitly fictional export detachment; no unexplained mass deployment. |
| 102 | `3587091564` | 3M25 <<МЕТЕОРИТ>> (AS-X-19 Koala) — active | Cold Sea / Future Front: experimental weapon; not a documented modern operational baseline. |
| 103 | `3681873198` | Pickup truck extension — active | World / local crisis: separate civilians, medical vehicles and identified armed technicals. |
| 104 | `3774746803` | AVIC HARBIN Z-21 — active | Future Front / exercise: advanced helicopter representation with declared assumptions. |
| 105 | `3729578404` | PLA Shenyang J-11BS — active | Opposition: distinct Flanker variants; avoid flooding the map with every subtype. |
| 106 | `3433577445` | Shenyang J-8 — active | Cold Sea / exercise: older interceptor; core uses newer threats. |
| 107 | `3729579342` | PLA Sukhoi Su-27UBK — active | Opposition / exercise: second-line aircraft and training detachment. |
| 108 | `3514484654` | RAAF F-35A Lighting II — active | Core: Australian fighter detachment; use checked conventional fits. |
| 109 | `3796113927` | RQ-180 White Bat Airframe — active | Future Front: speculative aircraft and especially speculative armed loadouts. |
| 110 | `3392434750` | SA-21/S-400 SAM — active | Opposition / Range Week: defined fictional enclave battery and SW08 seed. |
| 111 | `3673250557` | SAAB AEW&C PACK — active | Allied Dispatch / exercise: alternative command-aircraft episode, not another national RAAF type. |
| 112 | `3461519690` | SCUD-B — active | Range Week / Red Line alternate: missile-system episode with explicit fictional location and ownership. |
| 113 | `3455931957` | Sea Lynx — active | Allied Dispatch / Cold Sea: helicopter variants with exact deck and livery checks. |
| 114 | `3551676319` | SEJJIL (Iran Ballistic Missiles) — active | Range Week / Red Line alternate: missile-system episode with explicit fictional location and ownership. |
| 115 | `3497601759` | Shahed-136 Kamikaze Drone (Geran-2) — active | Opposition / Range Week: one-way drone threat; any local operator is campaign fiction. |
| 116 | `3451166840` | Su-25 Frogfoot — active | Red Line / exercise: Russian or explicitly fictional export detachment; no unexplained mass deployment. |
| 117 | `3762023575` | Su-30SM2 — active | Red Line: modern Russian detachment; ownership remains explicit. |
| 118 | `3503594612` | SU-57 Felon (重刑犯) — active | Red Line: optional small advanced detachment; not a ubiquitous regional adversary. |
| 119 | `3434072450` | Sukhoi Flanker Family (苏霍伊侧卫家族) — active | Opposition / Red Line / Cold Sea: choose exact generation, operator and weapons. |
| 120 | `3683253079` | Terminal High Altitude Area Defense (T.H.A.A.D) System (AN/TPY-2 Radar System included) — active | Range Week / optional missile-defence variant: explicit allied deployment and tested interception. |
| 121 | `3558173926` | David's Sling — active | Range Week: defence-system trial; no unexplained Australian operational battery. |
| 122 | `3502273861` | ARRW (AGM-183) — active | Support / Future Front: experimental strike missile, distinct from Dingtools ammunition IDs. |
| 123 | `3509329205` | TU-160 Blackjack — active | Red Line: rare conventional bomber episode; no endless strategic-bomber waves. |
| 124 | `3673908868` | <<Tu-16N>> — active | Cold Sea: historical tanker, not a default modern support aircraft. |
| 125 | `3780118683` | Tu-214R Family (图-214R家族) — active | Red Line: bounded reconnaissance/EW support; speculative family variants require disclosure. |
| 126 | `3411341227` | Tu-95K-22 Bear G MOD — active | Cold Sea / Red Line alternate: older maritime bomber threat, with conventional weapons. |
| 127 | `3715323261` | Tu-95MS (X-101) — active | Red Line: limited long-range conventional strike episode. |
| 128 | `3468959181` | U-2 "Dragon Lady" — active | Allied Dispatch: specialist reconnaissance; historical and balloon variants in optional episodes. |
| 129 | `3478767194` | VH-3D Marine One MOD — active | Exercise / Cold Sea: protected transport vignette; no forced presidential visit to the war zone. |
| 130 | `3373356293` | Royal Navy Westland Lynx HAS.3 Kitbash [OLD] — deprecated | Support / Cold Sea: legacy helicopter and unique Wildcat content; deprecated does not mean disabled. |
| 131 | `3782020901` | Y-20 / KJ-3000 — active | Opposition / Future Front: transport support; advanced special-mission variant is a declared assumption. |
| 132 | `3796349767` | YF-23 Black Widow II — active | Future Front: fictional production aircraft and Black Widow Debut. |
| 133 | `3601891050` | Small and Medium-Sized UAV Series [WIP] (中小型无人机系列) — wip | Opposition / Range Week: small-UAV episode; WIP assets must be individually tested. |
| 134 | `3408662804` | Iskander TBM — active | Range Week / Red Line alternate: missile-system episode with explicit fictional location and ownership. |
| 135 | `3470643173` | Type 12 SSM-ER Anti-Ship Missile System — active | Allied Dispatch / Range Week: Japanese coastal-defence episode; forward deployment needs explicit fiction. |
| 136 | `3631042692` | Modern Chinese Airbase (Large) — active | Support / Opposition: airfield source for a finite detachment with an explained location. |
| 137 | `3629269283` | Modern Russian Airbase (Large) — active | Support / Red Line: source for a small fictional detachment; replace default aircraft inventory. |
| 138 | `3592460366` | Modern US Airbase — active | Support: RAAF base donor and allied airfield template; replace oversized default air groups. |
| 139 | `3413868677` | Red Storm Arsenal — active | Support / optional anthology: broad unique content and shared definitions; preserve lower-priority winners. |
| 140 | `3605013271` | RE-power: the resupply mod — active | Core logistics / SW09: validate exact donor, resource, receiver and transfer limits. |

### Excluded catalog entries

| Workshop ID | Catalog title | Treatment |
|---|---|---|
| `3508978375` | [DEPRECATED] Lockheed Martin F-35C Lighting II | Excluded: unsubscribed in this snapshot; do not re-enable for the campaign. |
| `3426791311` | [DEPRECATED] Boeing F/A-18E/F Super Hornet | Excluded: unsubscribed in this snapshot; do not re-enable for the campaign. |
| `3674240446` | Shahed-136 Drone | Excluded: unsubscribed in this snapshot; do not re-enable for the campaign. |
| `3654230227` | AI Doctrine Overhaul | Excluded: unsubscribed in this snapshot; do not re-enable for the campaign. |
| `3790594162` | Identify Expanded | Excluded: unsubscribed in this snapshot; do not re-enable for the campaign. |

## Appendix B. SEST source-pack coverage

All 16 are registered in the pinned snapshot and feed the single consolidated deployable. The extra BMD/intercept work is a separate integration candidate, not silently included in this list.

| Source pack | Campaign role |
|---|---|
| `SEST_ADF_Persistent_ISR` | Triton for SW01/SW06; retain the MQ-9 donor dependency. |
| `SEST_Allied_Fixes` | Shared aircraft/ship corrections used by the selected fleet. |
| `SEST_B52_ARRW` | Bomber weapon integrations; conventional checked fits for allied episodes, experimental fits for Future Front. |
| `SEST_Collection_Fixes` | Collection corrections applied throughout; verify newly combined output after branch work. |
| `SEST_F-15EX_Revamp` | USAF reinforcement options; experimental fits remain labelled. |
| `SEST_F-35C_JATM` | US carrier aircraft fit layer; JATM availability/performance is an explicit scenario assumption when selected. |
| `SEST_F16CM_JATM` | Allied optional upgrade; not a required core combat advantage. |
| `SEST_Growler_NGJ_MALICE` | Australian/US EW aircraft layer; split conventional NGJ-oriented choices from fictional MALICE. |
| `SEST_JMSDF_Mogami` | Japanese escort integration for SW10. |
| `SEST_RAAF_Bases` | Australian base identities and scenery; author bespoke air groups and capacity budgets. |
| `SEST_RAAF_F-35A_JATM` | Australian F-35 source layer; select core or speculative fit explicitly. |
| `SEST_RAAF_Wedgetail` | Australian AEW squadron integration. |
| `SEST_RAN_Fleet` | Core Australian surface fleet and Collins representation; retain all disclosed donor limitations. |
| `SEST_Rafale_F5` | Future Front weapon fits; ordinary Rafale content can support an Allied Dispatch separately. |
| `SEST_Raptor_Squadrons` | Allied fighter identity and squadron support. |
| `SEST_TacMap_Colors` | Player interface throughout. |

## Appendix C. Handoff to the mission builder

Build the Southern Watch vertical slice from the pinned/current agreed repository state. First reconcile the latest branch, catalog and canonical load order; do not treat remembered branches or the README subscription count as authoritative. Keep changes on a feature branch and preserve the existing missions and exported user saves. Use the twelve mission cards as the narrative specification, starting with SW01, SW02 and SW06.

Use the existing Banda vignette builder as reference material. Correct objective/trigger mismatches in the new builder, explicitly include neutral and protected-unit failure gates, and test success termination. Validate exact unit IDs, enabled owners, squadrons, variants, weapon fits, capacity and recovery. Do not change a ship or aircraft merely because a convenient synonym exists.

Keep an Australian 2028 core, allied national identities and a visible civilian world. The optional modules account for the full collection. Put experimental or historical equipment in its declared branch instead of presenting it as confirmed contemporary Australian equipment. Do not re-enable unsubscribed mods.

For SW09, preserve the requirement that submarines surface for service and permit suitable other vessels to support them only through a verified transfer arrangement. Treat current HMAS Supply gameplay replenishment and automated surfacing enforcement as unresolved until tested. For missile-defence chapters, integrate and validate the separate Aegis/intercept work before making it a mission-critical dependency.

Deliver the three playable slice missions, a short dependency/approximation note, a campaign ledger and the actual static/in-game validation results. Report an untested mechanic plainly rather than writing a briefing that assumes it works.
