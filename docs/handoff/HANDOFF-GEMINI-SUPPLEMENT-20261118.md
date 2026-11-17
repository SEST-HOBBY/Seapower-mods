# Supplement to the Gemini handoff, 18 November 2026

SEST-DEV. Supplements `SEST_Gemini_UI_Gallery_Awards_Handoff_2026-11-18.md`. It does not replace
it. Read that handoff first, then this. The full package list is in
`WORK-PACKAGES-20261118.md`.

You work from the files the owner attaches. You do not have the repository, its build tools, the
game or the owner's PC. You return documents and data files. The repository's build assistant
converts, builds and tests; the owner plays and uploads.

## 1. Where the project stands

- **Live on Steam:** release R14, built for Sea Power 0.9.2. On game 0.9.3 its code switches
  itself off; the data still loads.
- **R15:** a test build for the 0.9.3 **public beta** file. It compiles and passes its automated
  checks. It has not yet run in the game. Its first PC run is the next step.
- **Public-release file:** the normal 0.9.3 is a different game file. No capture of it exists and
  R15 stays off on it. The owner wants the next posting to work on both files; open until a
  capture and a build exist.
- **Dynamic Campaign Mod** (the engine of the world campaign, "Global Maritime Operations 2028")
  has not been seen running on 0.9.3.
- No data for Antarctica, Africa, South America or India has been added to the world campaign.
  That is what packages GM-01 to GM-06 feed.

## 2. What in the existing Gemini handoff stands

- A (Regional Watch layouts), B (F8 aircraft utility wireframes) and D (gallery and encyclopedia
  information design) stand as design work, with the corrections in section 4.
- The rules stand: vector diagrams and text wireframes only, no generated photographs, every
  proposed control lists its source value and fallback, a mock-up is never described as built.
- The deliverable names requested there stand for those parts.

## 3. What the owner's later decisions change

1. **New Workshop item.** Section E of the handoff asks for a decision matrix on keeping item
   3812461539 against optional extra items, and says not to propose a rename. The owner has since
   decided: the mod is reposted as a new, clean, all-in-one item named **Modern Naval
   Operations**; the old item is marked deprecated and later removed; saves and old ids need not
   carry over. Drop the decision matrix. `Gemini-Workshop-Naming-Options.md` is replaced by
   package GM-12 below. The creator name stays **SEST-DEV**.
2. The new item is to support both the 0.9.3 public-release file and the public-beta file.
3. Left out of the new item: the two plugins for game 0.8.7, the chain of twenty repair builds,
   SETUP branches for old game builds, the legacy world-campaign entry.
4. The small weapon packs stay until a loadout-function enhancement replaces them.
5. The required-mods list is being revised: lean, expansive options kept, unused mods listed for
   the owner's review (GM-14 supports this).

## 4. What the repository scoping found that corrects or sharpens the handoff

- **A, Regional Watch.** Nothing is built and the repository has not scoped it. The engine has two
  sides and no neutral base; every base is owned and garrisoned. F11 tab labels are Overview,
  Forces, Combat Costs, Service. Design only.
- **B, F8.** The existing panel is the other author's (Unity IMGUI); it cannot be drawn on the
  owner's second monitor. It already accepts airborne aircraft carrying missiles or torpedoes as
  shooters. Parked aircraft are invisible to it. It offers no bombs or rockets. The repository
  plan is: aircraft rows with kind, altitude, speed, fuel, launch-point distance and time; then a
  native window; later an optional attack-waypoint button and one linked SEAD plan. The roles
  escort, EW, AEW, ASW, tanker and recovery in the handoff are **not** planned; draw them only as
  "not planned" or leave them out.
- **C, ribbons.** The handoff says no ribbon artwork and no name before award. The repository plan
  shows a dimmed strip and the name with progress, and withholds citation and conditions. The
  owner has not chosen. Draw both. Facts to respect: the 25 world awards are colour strips drawn
  in code, not image files; the native campaign Service Record shows awarded ribbons only; the
  campaign rules page has no commander state and cannot show progress; a static gallery page
  cannot see a save and cannot know what is earned.
- **D, gallery.** The numbers in the handoff are README claims. Actual: 555 photo assets, 732
  profile pictures built, 200 mods in the load order; 165 index entries point at files that no
  longer exist; 367 unit files have no entry; 343 current units have no picture; 21 author photos
  have no creator, licence or source. The gallery opens in a browser from the pack folder
  (`file://`, script tags, no network). There is no in-game button.

## 5. Rules for every package

1. Real, approved photographs only, with licence and source recorded. Never generate, render or
   AI-edit an image. No game screenshots from other authors. No image with an unclear licence.
2. Preserve upstream mod authors' credits.
3. No AI attribution text in any file: no "generated by", no assistant name, no disclaimers about
   being a model. Files carry the identity **SEST-DEV** or none.
4. Nothing is uploaded to Steam or anywhere else by an assistant. Send links, not downloads.
5. Every fact has a source: publication, date, URL, date accessed, and a confidence note (high,
   medium, low). Prefer official sources (navy, ministry, port authority, budget document,
   OurAirports for runways).
6. Do not invent unit ids or base ids. Use the ids in the attached files exactly. If no listed id
   fits, write `none` and describe the real class.
7. Say plainly what could not be found. Keep a "not found" row with the searches tried.
8. Keep real-world fact and 2028 scenario fiction apart. Every site has an `assumption` line that
   says what is fiction (access, side, presence).
9. Decimal degrees, south and west negative. British/Australian spelling.

## 6. Work packages

GM-01 to GM-07, GM-10, GM-11 and GM-12 can start now. GM-08 batch 1 can start now; later batches,
GM-09's audit part, GM-13 and GM-14 wait for a list from the build assistant.

### Background for GM-01 to GM-05: how region data enters the campaign

The world campaign is generated. Research is typed into one JSON file per region in the template
`docs/handoff/inputs/region-template.json`; the build assistant converts it. The blocks:

- `nations`: a nation new to the campaign and the side it joins. There are two sides, blue and
  red, and no neutral. A nation's ships and aircraft can be bought only if it has a home base.
- `home_bases`: a nation's main naval base or air base. `yard` true = can build ships; `depot`
  true = a supply source. `units` = [unit id, count, optional label].
- `sites`: a detachment or access point of a nation already in the campaign. `supplyFrom` must
  be the id of an existing depot (column `depot` = True in `gmo-bases-89b9b4649.csv`) within
  about 4,000 nautical miles. `notObjectiveFor` lists sides that should not try to capture it.
- `forces`: groups at a site. `type` Surface or Air. A unit string is
  `unit_id xN named A; B`. Surface forces have `at` [lat, lon] on water; Air forces have no `at`.
  `cargo: "full"` only on a force that contains a ship listed under `replenishment`.
- `patrols`: 3 to 6 points, all at sea, legs clear of land.
- `airfields`: forward airfields with no forces. `field.unit` must be one of the 13 stock
  airbase models: `airfield_small_1`, `nato_small_airbase`, `nato_very_small_airbase`,
  `wp_airbase_1` to `wp_airbase_5`, `wp_large_pvo_airbase`, `is_airbase_akureyri`,
  `is_airbase_isafjordur`, `is_airbase_keflavik`, `is_airbase_reykjavik`. `heading` is the true
  heading of the main runway.
- `lanes`: merchant shipping lanes, weight 1 (light) to 4 (heavy), points at sea.
- `labels`: map text only. Use labels for places that must not be bases.
- `missing_units`: a real class with no exact unit, and the stand-in, if any.
- `activation`: `in_bounds` for anything between 62S and 74N; `needs_latMin` for anything south
  of 62S.

Data rules: ids lower case a-z 0-9 and underscore; new ids must not collide with any id in
`gmo-bases-89b9b4649.csv`; names without `; # [ ] //`; quantities are a plausible 2028 presence,
not a full order of battle; a named hull is a real name of that class.

What already exists (do not repeat): India has Mumbai (depot, yard), Visakhapatnam, Ambala, INS
Rajali, INS Utkrosh. Brazil has Rio (depot, yard), Santa Cruz, Salvador. Chile has Talcahuano
(depot, yard), Punta Arenas (depot), Chabunco, Santiago. The UK has Mare Harbour (depot) and Mount
Pleasant. Africa has the Djibouti cluster, Egypt (Alexandria, Cairo West) and Russian detachments
at Tobruk, Al-Khadim, Al-Jufra, Bamako, Niamey, Bangui. Nothing south of the Sahel, nothing on
either African coast, no Argentine, South African or Antarctic base. No sea lane in the South
Atlantic, round the Cape, in the Mozambique Channel, the Drake Passage or the Bay of Bengal.

Engine limits to write within: airfields can only use the 13 stock models (no ice runway); there
is no sea ice; every owned base gets an automatic garrison including air-defence units, so treaty
stations and neutral ports should be `labels` or patrol points, not `sites`.

**Attach for GM-01 to GM-04:** `inputs/region-template.json`, `inputs/gmo-bases-89b9b4649.csv`,
`inputs/units-by-nation-regions.csv`, `region-expansion-research.pdf` (GPT's 24-page report; use
it as a list of leads and re-verify each from its source; its coordinates are rounded).

**Return for each:** one JSON file in the template, valid JSON, every block present (empty list
if none), and `<ID>-NOTES.md` with the source list (URL, publisher, publication date, date
accessed), what could not be found, and each scenario assumption you made.

**Acceptance for each (run by the build assistant):** the file parses and has only template keys;
every unit id is in the attached unit list for that nation or is reported under `missing_units`;
every `supplyFrom` is an existing depot id; new ids are unique and well formed; every base lies
inside the bounds or is marked `needs_latMin`; every `at`, patrol point and lane point is on water
and legs are clear of land (checked at 4 NM steps north of 60S); every `field.unit` is a stock
model; every site and airfield has a source URL and an `assumption`; a spot check of 10 per cent
of coordinates against the cited source agrees within 0.02 degrees.

### GM-01 India

- **Slots.** Karwar (second fleet base); Kochi; a naval component at Port Blair beside the
  existing INS Utkrosh; INS Baaz (Campbell Bay); Lakshadweep; Agalega or Mauritius access only if
  sourced; air stations Hansa (Goa), Thanjavur, Car Nicobar. Patrols: Arabian Sea, Bay of Bengal,
  Andaman Sea, Ten Degree Channel. Lanes: Bay of Bengal. Opposing slots (fiction, say so): Gwadar
  and Hambantota access for red; Pakistan already has Karachi, Minhas, Masroor.
- **Units.** Indian ids in the unit list (Visakhapatnam, Kolkata, Shivalik, Nilgiri classes, a
  Kilo, Rafale family, Mirage 2000, MiG-29K, a P-8 squadron, AH-64E). Not in the collection, so
  list under `missing_units`: both carriers, Talwar, Delhi and Kamorta classes, a fleet tanker,
  Arihant, Su-30MKI, Tejas, Jaguar, coast guard hulls.
- **Supply.** `home_ind_mumbai`.
- **Return.** `GM-01-india.json`, `GM-01-NOTES.md`.

### GM-02 Africa

- **Slots.** South Africa: Simon's Town (depot, yard), Durban, AFB Overberg or Ysterplaat, AFB
  Makhado. France: Reunion and Mayotte. US or UK access points as forward airfields: Mombasa or
  Manda Bay, Ascension, Dakar. Red access candidates as fiction slots: Walvis Bay, Bata, Port
  Sudan, Bagamoyo. Morocco and Algeria home bases only if units allow. Patrols: Cape, Mozambique
  Channel, Gulf of Guinea. Lanes: Cape route, South Atlantic, Mozambique Channel, Gulf of Guinea.
  Commercial ports with no force (Lagos, Tema, Cape Town, Maputo, Mombasa and similar): `labels`
  and lane points, not sites.
- **Units.** South Africa has no unit of its own in the collection; every South African hull is a
  stand-in. Name the stand-in from the unit list and its quality. Morocco and Algeria have a
  handful of ids. Nothing exists for Nigeria, Kenya, Mozambique, Angola, Namibia, Tanzania.
- **Open owner decision.** Which side South Africa joins, or none. Fill `nations` for both
  options in the notes; put South African bases in the JSON only under the option the owner
  confirms, otherwise leave them in the notes.
- **Return.** `GM-02-africa.json`, `GM-02-NOTES.md`.

### GM-03 South America

- **Slots.** Brazil: Natal, Belem, Rio Grande, Itaguai. Chile: Puerto Williams, Iquique,
  Valparaiso. Argentina: Puerto Belgrano, Mar del Plata, Ushuaia, Rio Gallegos, Comodoro
  Rivadavia. Peru: Callao. UK: South Georgia as a Port with no force. Patrols: Drake Passage
  north of 62S, Strait of Magellan, Falklands, Rio de la Plata, Brazilian coast. Lanes: South
  Atlantic, Drake, Magellan.
- **Units.** Brazil 37 ids and Chile 20 ids, complete for surface and air but no polar or patrol
  ship. Argentina 36 ids, all 1982-era (say so in `assumption`). Peru: Mirage 2000 only.
- **Open owner decision.** Argentina's side, or none; treat as for South Africa in GM-02.
- **Return.** `GM-03-south-america.json`, `GM-03-NOTES.md`.

### GM-04 Sub-Antarctic sites and Antarctic stations

- **Part 1, in bounds (`in_bounds`).** South Georgia, South Orkney (Orcadas, Signy), Marion,
  Crozet, Kerguelen, Heard, Macquarie: as `labels`, patrol points or, where a real port or
  airstrip exists, a Port or forward airfield with `notObjectiveFor` both sides. Gateways: Punta
  Arenas, Mare Harbour, HMAS Stirling exist; Simon's Town, Hobart, Christchurch/Lyttelton,
  Ushuaia are slots.
- **Part 2, below 62S (reference table only, `needs_latMin`).** King George Island (Frei),
  Marambio, Rothera, McMurdo, Mario Zucchelli, Casey, Davis, Mawson, Zhongshan, Bharati, Maitri,
  SANAE IV, Novolazarevskaya, Troll. These are not placed in the campaign until a PC probe shows
  the game works below 62S.
- **Framing.** South of 60S the Antarctic Treaty allows military personnel and equipment for
  peaceful purposes only. Write every assumption as research supply, search and rescue or
  science logistics. No armed station.
- **Stand-ins available:** `rn_opv_river_batch2`, `ran_opv_arafura`, `ae_opv_meteoro`,
  `ch_ffg_karel_doorman`, the Floreal-class frigate and the A400M (copy their exact ids from
  the unit list; the Floreal id contains an accented letter), `usaf_c-130`, `usmc_kc-130j`,
  civilian merchant hulls (`civ_ms_...`). No icebreaker, research ship or ski aircraft exists.
- **Return.** `GM-04-antarctica.json` (Part 1 in the template); `GM-04-stations.csv` (Part 2):
  `station,operator,lat,lon,year_round,usual_gateway_port,resupply_ship_class,runway_or_skiway,runway_heading_true,stand_in_unit_id,treaty_note,source_url,date_accessed,confidence`;
  `GM-04-NOTES.md`.

### GM-05 Real order of battle mapped to unit ids

- **Goal.** For India, Brazil, Chile, Argentina, Peru, South Africa (and Morocco, Algeria,
  Pakistan where useful), map the real 2026 fleet and air arm to the unit ids that exist.
- **Attach.** `inputs/units-by-nation-regions.csv` (columns nation_key, unit_id, type, role,
  display_name, operator_entries, source_mod, displacement).
- **Return.** `GM-05-oob-map.csv`:
  `nation,real_class,real_count_in_service,real_hull_names,unit_id,quality,note,source_url,date_accessed,confidence`.
  `quality` is one of `exact|same class|same family|representative|proxy|none`. `unit_id` is
  from the list or `none`.
- **Acceptance.** Every `unit_id` is in the attached list; every row has a source; classes with
  no unit are present with `none`.

### GM-06 Workshop search for missing units

- **Goal.** Find Steam Workshop mods for Sea Power that add: Indian carriers, Talwar and Delhi
  classes, Su-30MKI, Tejas; South African Navy (Valour, Heroine, Drakensberg) and Gripen;
  Argentine MEKO 360/140 and F-16; icebreakers, ice patrol ships, research ships, ski-equipped
  aircraft.
- **Return.** `GM-06-workshop-candidates.csv`:
  `wanted_unit,mod_title,workshop_id,author,last_updated,game_version_stated,unit_ids_or_names_added,page_url,date_accessed,note`.
  Keep "none found" rows with the searches tried. No downloads.
- **Acceptance.** Each page URL opens to the stated title and id.

### GM-07 Cost research backlog

- **Goal.** Find a citable public unit cost for the items the cost tracker prices by rough model.
- **Background.** The mod shows what a battle cost in US dollars. 381 weapons, vehicles, ships
  and aircraft had no checked price on 24 October; they now carry labelled model estimates. A
  price needs a source to replace an estimate.
- **Attach.** `docs/combat-costs/not-yet-confirmed.md` (the 381 items with id, description and
  any candidate figure); `docs/combat-costs/cost-list.csv` (4,567 rows; rows whose
  `current_method` is `rough model` are the wider backlog).
- **Order.** Missiles, torpedoes, bombs, ships and aircraft first; then land vehicles and
  installations; then pods, tanks, decoys and sonobuoys.
- **Return.** `GM-07-costs.csv`:
  `id,what_it_is,unit_cost_usd,cost_year,cost_basis,source_title,source_publisher,source_date,source_url,source_quote,date_accessed,confidence,note`.
  `id` copied exactly. `cost_basis` is one of
  `flyaway|procurement unit|contract value divided by quantity|export notification divided by quantity|analogue`.
  `source_quote` is the sentence or table line that carries the figure. If nothing is found:
  leave the cost empty and write `not found` with the searches tried in `note`. An `analogue`
  row names the analogue and is confidence low. `GM-07-NOTES.md` lists outliers you noticed
  within a category of `cost-list.csv`.
- **Acceptance.** Every id exists in the inputs; every priced row has a URL and a quote; no
  figure without a year; currency converted rows state the original amount and rate in `note`.

### GM-08 Photo sourcing for units with no picture

- **Goal.** Find one real photograph per unit that the gallery and the in-game encyclopedia can
  use.
- **Attach.** `inputs/gallery-nopic-batch1.csv` (11 unit ids added by the 17 November mod
  updates). Later batches come as `unit_id,label,nation,type,mod_title,note`.
- **Where to look.** Wikimedia Commons, DVIDS, US Navy, defence ministries with a stated free
  licence. Public domain or Creative Commons only.
- **Return.** `GM-08-photos-batchN.csv`, one row per photo:
  `asset_group,unit_ids,label,category,verdict,creator,licence,licence_url,source_page,source_file_title,note`.
  `unit_ids` separated by `;`. `category` is one of: `Aircraft & helicopters`, `Ships`,
  `Submarines`, `Land units`, `Sensors & equipment`, `Bases & installations`,
  `Weapons & ammunition`. `verdict` is `same_type` (the exact type), `same_family` (a sister or
  parent type, will be labelled "Class photo") or `context`. `source_page` is the file's own page
  (for Commons, the `File:` page), never a search or category page. `note` says what the photo
  shows (hull or tail number, operator, date) and why it matches. Keep a "none found" row per
  unit with the searches tried.
- **Acceptance.** The owner's PC kit downloads each `source_page`; the licence on the page
  equals the row; two reviewers pass each unit/photo pair. Rows that fail are returned.

### GM-09 Credit tracing and licence audit

- **Part 1.** 21 author-supplied photos have no creator, licence or source. **Attach:**
  `integration/gallery/added-photo-credits.csv` and the image files if the owner shares them.
  **Return:** `GM-09-credits.csv`:
  `file,asset_id,creator,licence,licence_url,source_page,confidence,how_found`; "not found"
  stated plainly, and for each not found a credited replacement in the GM-08 format.
- **Part 2.** **Attach:** `gallery-assets.csv` from the build assistant (555 rows:
  asset_id, label, creator, license, license_url, source_page). **Return:**
  `GM-09-licence-audit.csv`: `asset_id,issue,evidence_url,suggested_fix`, for: source page gone,
  licence on the page differs from the record, CC BY or BY-SA entry with no author, odd entries
  ("Attribution", CC BY-SA 1.0), subject mislabelled.
- **Acceptance.** Every `asset_id` exists in the input; every issue has an evidence URL.

### GM-10 Air refuelling fits and replenishment ship capacities

- **Background.** The game pairs a tanker and a receiver only if both declare a matching system:
  Boom, ProbeAndDrogue or Wingtip. Several tanker and receiver files in the collection lack the
  declaration. The build assistant needs the real fits to correct them, and real ship capacities
  to check the world campaign's supply figures.
- **Return.**
  - `GM-10-aar.csv`:
    `type,tanker_systems,receiver_system,max_transferable_fuel_kg,transfer_rate_kg_per_s,contact_speed_band_kias,in_service_from,source_url,date_accessed,confidence,note`
    for tankers KC-46A, KC-135R, KC-10A, KC-30A/A330 MRTT, Voyager, KC-130J, Il-78M, YY-20A,
    F/A-18E buddy store; receivers F-35A/B/C, F-22, F-15EX, F-16CM, F/A-18E/F, EA-18G, P-8A,
    E-7A, B-52H, B-1B, B-2, A-10C, Typhoon, Rafale, J-20, J-16, J-15, Tu-95MS, Tu-160, Tu-22M3.
  - `GM-10-ras-ships.csv`:
    `class,cargo_fuel_tonnes,f76_tonnes,jp5_tonnes,ordnance_tonnes,dry_stores_tonnes,ras_stations,max_ras_speed_kn,full_load_displacement_t,source_url,date_accessed,confidence`
    for Henry J. Kaiser, Lewis and Clark, Supply (T-AOE), HMAS Supply (AOR), Type 903A, Type 901,
    Tide, Mashu, Boris Chilikin, Akademik Pashin, Delvar.
  - `GM-10-procedures.md`: 1 to 2 pages with sourced figures: usual underway replenishment speed,
    separation and time to transfer a given tonnage; usual tanker track altitudes, speeds and
    offload per receiver.
- **Acceptance.** `unknown` used instead of guesses; every row sourced; cargo below full-load
  displacement.

### GM-11 Real national awards

- **Goal.** Check the real awards the campaigns already represent and research the ones not yet
  drawn.
- **Attach.** `integration/campaign/setup/RIBBONS.txt`; `integration/campaign/service_awards.py`
  (table REAL at lines 561-905); each campaign's `art/ribbons/SOURCES.txt`.
- **Return.** `GM-11-awards.csv`:
  `ribbon_id_or_new,nation,official_name_native,official_name_english,issuing_authority,awarded_to_and_for,criteria_quote,criteria_source_url,stripe_colours_left_to_right,stripe_widths,stripe_source_url,commons_file_page,image_author,image_licence,matches_sest,what_differs,fits_commander_to_commodore,confidence`.
  Rows: every award in the REAL table (existing id copied exactly), plus candidates for Italy,
  the Netherlands and Norway (Southern Watch, Southern Reach), the PLA Navy (Red Line) and the
  Pakistan Navy (Makran Line, up to 4), each of the kinds commendation, distinguished service,
  campaign service, unit citation where one exists. Also confirm or correct the Pakistan Navy
  rank abbreviations that `RIBBONS.txt` marks as not verified. `GM-11-awards.md` holds the same
  as a readable table with notes.
- **Acceptance.** Existing ids match the input; every row has a criteria source or "could not
  verify"; no image file is sent, only pages and licences.

### GM-12 Steam Workshop mechanics and name check

- **Questions.** What a subscriber of an old item sees when a new item replaces it; whether an
  item can be marked deprecated or superseded and how other large mods word it; limits on
  Required Items and on collection size; whether a deleted item's saves or subscriptions leave
  anything behind; how three comparable large mods (name them, with URLs) handled a repost and
  what subscriber problems were reported. Then: does "Modern Naval Operations" collide with an
  existing Steam Workshop item, Sea Power mod, game or commercial product.
- **Return.** `GM-12-workshop-mechanics.md`: one section per question, each claim followed by its
  source URL and date accessed, and a separate list of community hearsay.
  `GM-12-name-check.csv`: `name_found,where,url,kind,risk,note`.
- **Acceptance.** Every claim has a URL; hearsay is separated.

### GM-13 Air-launched weapon table and strike timing

- **Attach.** `air-weapons.csv` from the build assistant (`ammo_id,display_name,nation`).
- **Return.** `GM-13-weapons.csv`:
  `ammo_id,real_designation,launch_platforms,min_launch_alt_m,max_launch_alt_m,typical_launch_speed_kn,max_range_nm_high,max_range_nm_low,cruise_speed_mach,guidance,in_service_from,in_service_to,source_url,confidence`;
  `UNKNOWN` rather than a guess. `GM-13-doctrine.md`: 2 pages on how coordinated ship and
  aircraft anti-ship and SEAD strikes were timed, 1975 to 2000, US Navy and Soviet Naval
  Aviation (push times, time-on-target windows, SEAD lead before the main wave, usual launch
  ranges and altitudes), numbered findings each with a source, and a 10-row table
  `parameter | typical value | range | source`.
- **Use.** Sanity-checks the planner's advice and its default offsets. It does not change game data.

### GM-14 Required-mods page status

- **Attach.** `required-mods-usage.csv` from the build assistant
  (`workshop_id,title,used_by,in_required_list,in_load_order`).
- **Return.** `GM-14-mod-status.csv`:
  `workshop_id,title_on_page,author,last_updated,game_version_stated,marked_deprecated_or_replaced,replacement_id,required_items_listed,page_url,date_accessed,note`.
- **Acceptance.** One row per input id; ids unchanged; pages that do not open are reported as such.

## 7. What to send back and how

- One folder or ZIP per package, named with the package id, holding exactly the files named in
  "Return" plus `<ID>-NOTES.md`.
- `<ID>-NOTES.md` contains: date of the work; the input files you were given; the source list;
  what could not be found; scenario assumptions; open questions for the owner.
- CSV: UTF-8, comma separated, one header row, fields with commas or line breaks in double
  quotes, no blank spacer rows. JSON: valid, no comments, template keys only.
- Do not include text that says who or what wrote the file. Do not restate this brief.
- Give the files to the owner. The owner places them under `docs/handoff/returns/<ID>/`; the
  build assistant runs the acceptance checks and replies with accepted, or the rows to fix.
- If an input file named under "Attach" was not given to you, stop and ask for it.
