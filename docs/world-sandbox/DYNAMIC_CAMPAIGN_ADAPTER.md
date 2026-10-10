# SEST World Sandbox on the Dynamic Campaign engine - draft adapter

Status: DRAFT BUILD. Generated and statically checked. **Not installed, not loaded, not played.**
Date: 10 October 2026. Branch: `sest-dev/inspiring-wozniak-8vuckh`, which carries the
world-population register (from `sest-dev/sweet-lovelace-3kxsve`) with main merged in at `7dbc3b95`.

## What this adds

The register (`WORLD_POPULATION_REGISTER.md`, `register/`) stays the engine-neutral source of
truth. This draft adds one possible runtime for it: a data pack for Bungalow's Dynamic Campaign
Mod (Workshop 3813157776, plugin 0.24.0), the engine the static review in `engine-review/`
examined.

| File | What it is |
|---|---|
| `integration/world-sandbox/build_dynamic_campaign.py` | Adapter: register -> `campaign.json` |
| `integration/world-sandbox/check_dynamic_campaign.py` | Validator: the engine's own rules, the review's audit, SEST collection and water checks |
| `integration/world-sandbox/draft/sest-world-sandbox/` | The candidate data pack: `_info.ini` and `dynamic_campaigns/sest-world-sandbox/campaign.json` |
| `integration/world-sandbox/draft/conversion.json` | Every register row, converted or skipped, and why; every SCENARIO CHOICE the adapter made |
| `docs/world-sandbox/engine-review/` | The review bundle as supplied (hashes match its manifest). Bungalow's `campaign.json` and `_info.ini` are not copied: they are the author's files |

Nothing here is built by `tools/build_all.py`, installed by SETUP or `sync-sest.ps1`, or
published in the SEST Integration Pack. The folder name has no `SEST_` prefix so no pack tool
picks it up.

Run:

```
python3 integration/world-sandbox/build_dynamic_campaign.py
python3 integration/world-sandbox/check_dynamic_campaign.py
```

The water checks need `pip install global-land-mask numpy`, the same optional dependency
`build_indo_pacific_showcase.py` uses. Without it the adapter still writes the file and says the
water checks were skipped.

## Evidence levels

Kept apart throughout, as the register does:

| Level | This draft |
|---|---|
| Source described | Unchanged: the register's SOURCE CLAIMs |
| Independently checked | Unchanged: the register's three fidelity passes |
| Collection mapped | Every unit id resolves to the winning file on main `7dbc3b95` |
| Placed | Bases, groups, patrols and lanes have coordinates; sea positions are checked against a land mask |
| Runtime active | **Pending.** Needs the game, BepInEx, Anchor Chain and the plugin |
| Playtested | **Pending** |

## Engine capability and limitation matrix

From the static review (`engine-review/REVERSE_ENGINEERING_REVIEW.md`). Tokens are for the
uploaded 0.24.0 DLL only.

| Area | What the code shows | What it means for SEST | Evidence |
|---|---|---|---|
| Discovery | Menu postfix scans every `dynamic_campaigns` directory for a `campaign.json` | A separate SEST data pack may load beside Bungalow's campaign with no DLL change. **Untested**: whether the game's file manager sees a second mod's folder | `CampaignMenuPatch.Postfix` 0x06000949, predicate 0x0600165c |
| Schema | `CampaignDefinition.Load` then `Validate`; 106 error messages state the rules | The adapter writes to those rules and `check_dynamic_campaign.py` re-applies them | 0x060010c4, 0x060010c5; `dll-evidence.json` |
| Strategic world | One simulation step runs economy, shipyards, fuel, supply, replenishment, airlifts, air and carrier operations, movement, detection, AI, victory | The persistent world the user asked for exists in code. It is a strategic map that spawns local battles, **not** one continuously active tactical mission | `CampaignSim.StepTo` 0x06000d01 |
| Battle bridge | Writes native missions with `GeoPosition=`, variants, loadouts and campaign tags; reads survivors, losses, ammunition and damage back | Battles happen in the real game with SEST's units. What survives returns to the map | `MissionWriter.WriteUnit` 0x06000a41, `BattleSession.OnDebriefExit` 0x06000a2c |
| Persistence | Saves fleets, squadrons, flights, base ownership, stocks and hull fuel, ammunition and damage; safe write with temp file and replace | Strong base for "persistent" | `CampaignSave` 0x06000a71, `Files.WriteSafely` 0x0600091c |
| Crew experience | The unit writer emits `CrewSkill=Trained` for every unit | No crew experience carries over. Do not advertise it | 0x06000a41 |
| Replenishment | Strategic transfer when a supplier is within 5 NM of a task force at sea | A campaign abstraction, separate from SEST Replenishment's alongside rules in battle. **Stock accounting between the two is untested** (review test: 20 rounds, fire 10, receive 10) | `Logistics.ReplenishAtSea` 0x06000e35, `BattleSession.Fired` 0x06000a23 |
| Detection | Role presets, e.g. ship 70/150/20 NM, carrier 200/200/50, AEW aircraft 200/200/0 (surface/air/sub) | Modern sensors in SEST's unit files do not change strategic detection | `SensorProfile` 0x0600101e |
| Geography | Longitudes mapped to the copy nearest the bounds' midpoint; nav grid with water and depth checks | A theatre may cross the antimeridian. A whole-globe rectangle is **untested** | `GeoBounds.Continuous` 0x060010ce |
| Sides | Validator needs at least two sides; the sample has two and marks red `comingSoon` | No neutral bases, no third alignment. Host nations (Djibouti, Bahrain) cannot be modelled as hosts | Validate messages "needs at least two sides", "every side is comingSoon" |
| Air groups | Carrier `airWings` lines name squadrons; plain air forces name only a unit and a count | Air forces cannot choose a squadron, so the RAN's 816 Squadron Seahawk markings are not expressible outside a carrier wing | Validate message "is no air wing line"; sample forces |
| Ship identity | A unit line may name ships (`x2 named A; B`); only ships can be named | Names carry over. Variants are not expressible in a unit line, so each hull takes the engine's default variant. **Untested** whether a name selects a variant | Validate messages "names more ships than it has", "only ships can be named" |

## Feasibility

**A data-only SEST pack is feasible for most of the register.** The draft below passes every rule
the engine states. What it cannot carry, by the engine's own design:

- **Neutral hosts and access.** Two sides only. Jebel Ali (a neutral commercial port) is left
  out; Djibouti's five national bases each belong to their operator's side.
- **Peacetime.** The engine is a war engine: sides, conquest, victory. The sandbox can start
  quiet (no invasions, no story beyond a two-paragraph opening), but the AI will fight.
  Removing story text does not remove conquest logic.
- **Allocation detail.** The register's resident, maintenance, reserve and support states all
  become "in harbour". Training and deployed groups become forces at sea.
- **Abstract logistics.** The 21 inland depots and agencies stay abstract. Supply originates
  at 11 depot bases chosen as SCENARIO CHOICE (below).
- **Embarked flights.** Ship flights and carrier wings are not separate forces; the engine flies
  each hull's own air group.

A small adapter in the DLL would only be needed for: neutral/host states, variant selection,
squadron choice on air forces, and SEST-aware replenishment accounting. None is proposed for
application here.

## The draft build

| | Count |
|---|---|
| Register force rows | 318 |
| Converted into forces | 185 |
| Listed as civil traffic | 12 |
| Listed as ground air defence | 4 |
| Skipped (abstract, embarked, scenery, missing fit, quantity 0) | 117 |
| Bases | 39 (16 naval, 23 air, of which 3 are a naval base's own airfield); 11 depots |
| Forces | 92 (43 surface, 49 air), 203 units, 85 of them ships |
| Patrol routes | 16 |
| Sea lanes | 11, all on water |
| Catalogue (buy list) entries and unit values | 1,197: blue 778, red 419 (below) |
| Register nodes not converted | 34 (30 abstract or context only by the register's own policy, 1 reserve-only, 1 do-not-populate, Jebel Ali, NAB Coronado with nothing placeable) |

Sides: **blue** US, Australia, Japan, France, Italy, UK, Norway; **red** China and Russia. Both
are playable (decided 10 October; the sample keeps red `comingSoon`, so playing red is untested).

### The buy list: both sides' full arsenals

Asked for on 10 October: the engine's catalogue, what a side can order, holds every
ship, submarine and aircraft the collection gives that side's nations, not only the
78 types in the opening forces.

| Side | Nation | Ships and submarines | Aircraft |
|---|---|---:|---:|
| blue | US | 244 | 173 |
| blue | Australia | 39 | 34 |
| blue | Japan | 23 | 19 |
| blue | France | 38 | 62 |
| blue | Italy | 35 | 19 |
| blue | UK | 44 | 39 |
| blue | Norway | 8 | 1 |
| red | China | 95 | 106 |
| red | Russia | 115 | 103 |

- **Operator** is the `Nation=` of the winning variants or squadrons file (Soviet is
  Russia). A type several nations fly is listed once, under the side's nation with the
  most variants. A type in an opening force stays on that force's side.
- **No era cut.** Most of the collection's units carry no `ServiceDate`, so a 2028
  filter would drop the J-10C and the KJ-500 as readily as the Knox. Cold War types
  stay buyable; the tier (price band from the unit value) separates them.
- **Left out (96):** civil, merchant and fishing hulls (armed militia variants
  included), intelligence ships, target drones, satellites, a balloon, decoys, rafts,
  a sea mine, and two ids with a space in them (`plaf_j16a block3`, the Project 2498
  assault vessel), which a campaign cannot name.
- **Not on either side:** units only other nations operate - Spain 64, Germany 31,
  Brazil 25, Thailand 24, Iran 21, South Korea 17, Philippines 17 and more
  (`conversion.json` "arsenal"). Adding a nation to a side brings its arsenal in.
- **Shipyards: only US, Australia and China have one** (Bremerton, Norfolk, Yokosuka;
  Stirling; Ningbo). Russia, Japan and Norway have no naval base in the register at all,
  and France, Italy and the UK only overseas outposts (Djibouti, Mare Harbour). Where the
  engine builds a ship for a nation without a yard is unknown - it may use a side yard
  (Ningbo for Russia), or the order may never arrive. Open decision: add one home dockyard
  per nation (Severomorsk, Kure, Portsmouth, Toulon, Taranto, Haakonsvern - a scenario
  addition to the register), or keep those nations to aircraft until a test shows how
  the engine behaves. Aircraft are delivered to air bases, which every nation has.
- **Untested:** how the engine's buy screen copes with ~800 entries a side.

### Mapping rules

| Register | Engine |
|---|---|
| Node with `populate` or `populate_small` and a position | Base. Naval if it has ships, air if aircraft only. A naval node with aircraft gets a colocated airfield with `port` set |
| Operator | Base nation and side. Only the text before "host" counts, so Yokosuka is US |
| Ship rows at sea (escort, transit, deployed, training) | Surface force "at" sea. Escorts and supply ships join the carrier they sail with, matched by the register's own hull numbers and asset ids |
| Ship rows in harbour (resident, maintenance, reserve, support) | One harbour force per base |
| Patrol rows | Patrol force with a four-point route on water; submarines patrol separately |
| Aircraft rows (not embarked) | One air force per aircraft type at the node's airfield |
| Hull names | `named`, from the register's hull names, quoted variant names or carrier asset ids |
| Supply ships | `replenishment` with fuel and ammunition tonnes; their forces start with `cargo: full` |
| Unit ids the collection retired | Retargeted through `integration/missions/retarget_units.py`'s table |

### Scenario choices the adapter makes

All are recorded per row in `conversion.json`. None is a research claim.

- **Positions at sea.** Five named deployments are placed in the areas the register's text gives:
  Lincoln and George Washington in the Philippine Sea, Roosevelt west of Hawaii, Truman in the
  western Atlantic, Fujian in the South China Sea. Other groups start 25 to 60 NM off their base.
- **Patrol routes.** 35 NM rings centred up to 60 NM offshore, every leg on water.
- **Depots.** San Diego, Norfolk, Yokosuka, Guam, Bahrain, Sigonella, Stirling, Yulin, Ningbo,
  Mare Harbour and Olenya. Each base draws from its own nation's nearest depot within 4,000 NM,
  else its side's. Rota, Souda Bay, Akrotiri and Evenes draw from Sigonella.
- **Sigonella** (decided 10 October, "yes if realistic"). The research names DLA Distribution
  Sigonella the "Mediterranean/European logistical gateway" (R02:23, R02:34), the same pairing that
  makes Yokosuka, Guam and Bahrain depots. Rota appears only as an operational gateway for
  destroyers (R03:44). NAS Sigonella is an air station, so its depot supplies by airlift; the
  engine's validator allows a depot to carry airlifts. **An air-station depot is untested**; if it
  cannot feed ships, Rota with sea convoys is the fallback.
- **Unit values.** Ships: fitted on the sample's 102 priced hulls against each hull's own
  Displacement (R² 0.72), supply and cargo ships at 0.32 of that. Aircraft: the sample's median
  value for the aircraft's own Role. Carriers come out at about 1,190, a Burke Flight III at 245.
- **Replenishment tonnes.** Approximate public cargo capacities, rounded.
- **Runway headings.** 0 everywhere; the register has none.
- **Bounds.** Latitude 62S to 74N; longitude 100W east-about to 102W (258). The seam sits over
  Mexico, so a Panama to San Diego passage is cut. Everything else connects.

### Revised from the register

- `asset:wpac:gw_csg_cg1` (George Washington's cruiser) named `usn_cg_ticonderoga_vls_2025`, which
  Modern US Navy retired in the 9 Oct export. The register now names `usn_cg_bunker_hill_vls_2024`,
  Variant5 CG-64 Gettysburg, the same retarget main applies to the Sulu Sea Offensive missions.

## Decisions (10 October 2026)

1. **Strategic map with generated battles: yes.** This engine is the runtime candidate.
2. **European depot: yes, if realistic.** Sigonella, supplied by airlift (above).
3. **Red playable: yes.** `comingSoon` removed; red has its own two-paragraph opening.
4. **The Panama seam: accepted.**
5. **Permission: granted.** The user reports Bungalow's permission for a SEST pack built on the
   Dynamic Campaign engine. Publication itself still waits for a load test.

## Testing on the PC (isolated, when ready)

Use a backed-up install, not the published pack.

1. Subscribe to Dynamic Campaign Mod (3813157776). It needs BepInEx and Anchor Chain. SEST's SETUP
   installs the Anchor Chain preloader; check the mod's page for what else it needs.
2. Copy `integration/world-sandbox/draft/sest-world-sandbox` into the game's
   `Sea Power_Data\StreamingAssets` folder, beside the SEST pack, and enable it in the Mod Manager.
3. Campaign menu: look for "SEST World Sandbox 2028 (draft)" beside Bungalow's campaign.

Then, in order: menu discovery; the validator's verdict in the BepInEx log; one battle each side,
playing blue and then red; whether Sigonella's airlifts reach Rota and Souda Bay;
the review's 20/10/10 ammunition test with a SEST supply ship; save, reload, and reload after a
battle; a transit across the antimeridian (Roosevelt's group); performance with all 92 forces;
the buy screen with ~800 entries a side, and one order each by a nation with a shipyard (US)
and one without (Norway).
