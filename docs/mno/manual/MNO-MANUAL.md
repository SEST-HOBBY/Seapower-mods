# Modern Naval Operations: player manual

**For release R16, 25 November 2026. Sea Power 0.9.3 Build 261123 public beta.**

Modern Naval Operations (MNO) is SEST's free, non-commercial integration mod pack for *Sea Power: Naval Combat in the Missile Age*. This manual tells you what MNO adds and how to use each part of it.

> **Read this first: what has been tested.** R16 is the first build for Sea Power 0.9.3 Build 261123 public beta. It has been built and tested in automated checks. It has **not yet been played on the owner's PC.** In this manual, "built and tested in automated checks, awaiting PC confirmation" means exactly that. Where an earlier build was seen working on the owner's PC, the manual says so and names the build.

---

## Contents

1. What MNO is, and what it is not
2. Installing and updating
3. Which game builds are supported
4. Campaigns
5. Features
   - 5.1 Battle preparation and the end of a battle
   - 5.2 F11 World Operations and combat costs
   - 5.3 Weather, storms and local battle weather
   - 5.4 Sea ice
   - 5.5 Ice shelves and icebergs (off by default)
   - 5.6 Replenishment at sea and supply
   - 5.7 Cross-deck operations
   - 5.8 Coordinated Strike Tool refinements
   - 5.9 Ribbons and service awards
   - 5.10 Encyclopedia photos and the offline gallery
   - 5.11 Keys and UI changes
   - 5.12 Working with other code mods
   - 5.13 Smaller fixes that run in the background
6. Troubleshooting and reporting a problem
7. Credits and licence

---

## 1. What MNO is, and what it is not

### What MNO is

- **One Workshop item**, called *Modern Naval Operations*. It used to be called the *SEST Integration Pack - Modernised Campaigns*. If you subscribed to that, your subscription now points to MNO. The Workshop item ID is [new MNO item ID, added when the listing is posted]. The old item 3812461539 will be retired later.
- **A world campaign.** *Global Command Operations (GCO)* is a persistent world campaign. It runs on Bungalow's Dynamic Campaign Mod.
- **Five authored Task Force campaigns:** Southern Watch, Southern Reach / Tasman Shield, Red Line, Sulu Line and Makran Line.
- **Fixes that make about 200 Workshop mods work together.** MNO sits at the top of the Mod Manager. Its files replace the parts of other mods that clash.
- **SEST's own code features.** These include F11 World Operations, sea ice, local battle weather and debrief ribbons. SEST develops its weather and integration systems under the name *Global Strategic Command Operations (GSCO)*.
- **A SETUP script** that checks your mods and writes the load order for you.

### What MNO is not

- **MNO does not contain other authors' mods.** The ships, aircraft, models, weapons and supporting tools come from their original Workshop authors. They are *Required Items*. You get them all from one Steam collection: *Modern Naval Operations | Required Mods* (collection 3812390790).
- **MNO does not ship Dynamic Campaign Mod.** Dynamic Campaign Mod is Bungalow's work and is a Required Item. On Build 261123, SEST adapts it in memory when the game loads it, because that build changed the map. Nothing of Dynamic Campaign Mod is copied into MNO.
- **MNO is not affiliated with Triassic Games or MicroProse.** It contains no game files.
- **The campaigns are fiction.** The story, each nation's conduct in it, the companies, officers, incidents and dates are made up. Real warships appear under their real names.

---

## 2. Installing and updating

MNO is for **Windows only** for now.

### 2.1 First installation

1. **Subscribe.** Open the *Modern Naval Operations | Required Mods* collection on Steam and press **Subscribe to all**. This subscribes you to MNO and its Required Items. (The collection text says 216 Required Items.)
2. **Wait.** Let Steam finish every download. SETUP will stop if a mod is still missing.
3. **Open the MNO folder.** Start Sea Power. In the Mod Manager, select *Modern Naval Operations* and press **Open Folder**.
4. **Quit Sea Power.** SETUP will not run while the game is open.
5. **Run SETUP.** In that folder, double-click **`SETUP - double-click me.cmd`**.
6. **If Windows asks for permission, click Yes.** SETUP needs administrator rights once to install the Anchor Chain preloader in the game folder.
7. **On the supported beta, do the menu check.** On a first installation, SETUP asks for a "menu probe". Start Sea Power, wait about ten seconds at the main menu, quit, and run SETUP again.
8. **Look for "All done".** If SETUP says *"Done, but read the [!!] warning(s) above first"*, read each `[!!]` line. Save its wording if you need to report it.
9. **Start the game.** In the Mod Manager, *Modern Naval Operations* should be at the top and ticked. **If the Mod Manager offers to move or fix dependencies, say no.**

### 2.2 What SETUP does

SETUP checks everything before it changes anything. It backs up the game's settings and every mod file it changes first. It is safe to run again. In order, it:

- reports which Sea Power build you have (see section 3) and warns if code mods did not load at your last launch;
- checks that every mod in the load order is downloaded, and lists any that are not, with links;
- installs the Anchor Chain preloader if it is missing;
- turns off one mod's debug logging (PLA & PLAN & PLAAF AEP) that can freeze a mission;
- marks mods made for an older game version as compatible, so the Mod Manager stops warning about them at start-up (they load either way);
- if you have Contact Log and it has written its settings file, frees its default F6 and F8 keys (see 5.11);
- writes the Mod Manager order: MNO first, then the tested order, then your other mods at the bottom as you had them;
- last, on Build 261123 only, installs or updates SEST's bundled beta features.

SETUP saves a copy of your game settings before it writes the order. The copy sits beside the game's `usersettings.ini` with `.bak_sest_` and a date in its name.

SETUP stops with a clear message if:

- a Required Item is not downloaded yet;
- you are subscribed to more than one copy of the SEST pack (unsubscribe from all but one);
- there is also a copy of the pack in the game folder (two copies fight over the same files).

### 2.3 Updating

- After Steam updates MNO, **close the game and run SETUP again** from the subscribed item.
- Also run SETUP again after Steam updates your other mods, if a mission freezes, or if the "not compatible" warning comes back.

### 2.4 The SEST beta features: on, off and remove

On Build 261123, SETUP installs SEST's code features (called the *beta features*). Three launchers in the MNO folder let you control them. **Quit Sea Power before running any of them.**

| Launcher | What it does | What SETUP does afterwards |
|---|---|---|
| `SEST beta features - turn off.cmd` | Turns SEST's beta loader off. The files stay installed but inactive. Nothing else is changed. | Leaves the features off, also after Steam updates. |
| `SEST beta features - remove.cmd` | Puts the normal SEST plugins back from the backups made at install time, and removes SEST's beta files. Saves and data are kept. | Leaves the features off, also after Steam updates. |
| `SEST beta features - turn on.cmd` | Clears your "off" or "remove" choice, then runs the normal SETUP, which installs the features again. | Installs them, on the supported build. |

**Important:** on Build 261123, Workshop code mods load only through SEST's loader. So with the beta features off, *other authors' code mods* stay off too. Data mods and campaigns still work.

These launchers work only from the subscribed Workshop copy of MNO.

### 2.5 What the beta-feature install changes

On Build 261123 only, the feature install:

- adds `SEST.BetaSafeBootstrap.dll` to `BepInEx\plugins`;
- adds SEST's modified Anchor Chain to `BepInEx\config\SEST-BetaAnchorChain`;
- replaces SEST's own plugins in MNO's `plugins` folder;
- rewrites the Mod Manager order without the local IdentifyExpanded row (Identify Expanded and MNO stay on);
- moves a local `StreamingAssets\IdentifyExpanded` folder to `%LOCALAPPDATA%\SEST\IdentifyExpanded`.

Everything is backed up first under `%LOCALAPPDATA%\SEST\BetaCompatibility`. The install does **not** change your Steam branch, the game's own DLLs or your saves. If it finds an unknown game file or an unknown version of another author's DLL, it does not force anything. SETUP gives one `[!!]` warning naming the file and finishes the rest of its work.

### 2.6 Load order

- `LOAD-ORDER.txt` in the MNO folder lists the order MNO was built against: 220 entries, MNO first.
- **The one rule that matters:** MNO, and any folder whose name starts with `SEST_`, sits **above every Workshop mod**. Its files are whole-file replacements. Anything that outranks them wins, and the fix is lost.
- A mod you have that is not on the list is fine. Put it at the bottom.
- You do not need to do this by hand. SETUP writes exactly this order.
- `REQUIRED-MODS.txt` lists each Required Item and why it is needed.

**Keep every Required Item subscribed.** That includes R.A.T.S. Keel (3835527459), both Sensor View items (3822119548 and 3838468198) and Sensor View - ExtendedGuidance support (3838469336). SETUP checks `LOAD-ORDER.txt` and stops if any of them is missing. SEST's loader still starts the game's code mods itself; subscribing to Keel does not change that.

### 2.7 Game builds and "profiles"

`SEST-PROFILES.txt` in the MNO folder says what SETUP does on each game build. SETUP identifies your build from the game file `Sea Power_Data\Managed\Seapower-Scripts.dll`. Section 3 gives the short version.

---

## 3. Which game builds are supported

MNO has two layers:

- **Data:** campaigns, missions, unit fixes, photos. These do not depend on the exact game build. They are built on the game's 0.9.2 files, and the pack declares game version 0.9.3.
- **Code:** SEST's own features. Each is matched to one exact game file. On any other build, SEST's code stays off.

| Game build | What you get | Status |
|---|---|---|
| **0.9.3 Build 261123 public beta** | Everything: data, campaigns, and the R16 code features (SEST Runtime 1.8.0, UI 1.6.0). Dynamic Campaign Mod 1.0.2 runs through SEST's in-memory bridge. | Built and tested in automated checks, awaiting PC confirmation. |
| 0.9.3 Build 261116 **public release** (Steam's default branch) | Campaigns and data, subject to game compatibility. No SEST code features. | **Not yet supported.** It is a different file from the beta. Support needs one reference capture from a PC on that branch first. |
| 0.9.3 Build 261116 public beta (R15's build) | Campaigns and data. No SEST code features. | Not supported by R16. |
| 0.9.2 Build 261113 and older builds | Campaigns and data. If SEST's beta files are installed, SETUP puts the normal plugins back. | No R16 code. |

**How to get Build 261123:** in Steam, open Sea Power > Properties > Betas and choose the public beta. [owner to confirm: the exact name of the beta branch in Steam's Betas list.]

[owner to confirm: on the default release branch, does Dynamic Campaign Mod 1.0.2, and so GCO, start without SEST's bridge? The repo says only that SEST's bridge is for the Build 261123 map change.]

---

## 4. Campaigns

### 4.1 Global Command Operations (GCO): the world campaign

**What it is.** GCO is a persistent world campaign for Bungalow's Dynamic Campaign Mod. It was called *Global Maritime Operations 2028* before. The world begins on 1 October 2028 and covers the map from 79° South (the Antarctic coast) to 81° North. It is a fictional scenario: deployments and alliances are design choices.

**What it contains.**

| Item | Number |
|---|---|
| Bases | 196 |
| Force groups | 293 |
| Patrol routes | 54 |
| Recruitment (shipyard) entries | 1,668 |
| Command stages | 8 |
| Fleets | 18: 10 Blue (US 2nd to 7th Fleets, Royal Navy, Indian Navy, JMSDF, Australian Fleet) and 8 Red (Northern, Baltic, Black Sea and Pacific Fleets, Iranian Navy, three PLA Navy theatre fleets); each side's fleets share out all 40 sea regions |
| Career starts | 15 |
| Theatres | 6: European Waters; Middle East and Indian Ocean; African and Cape Routes; Americas and Southern Ocean; Allied Southern Flank; Pacific and East Asia |

**The two sides.**

- **Blue: "United States and partners"** (31 nations, including Australia, Japan, the UK, France and others).
- **Red: "China, Russia and their partners"** (China, Russia, Iran, North Korea, Vietnam, Indonesia and Pakistan).

**How to start it.**

1. Open **Campaigns**.
2. Choose the entry marked **[Dynamic]**: *Global Command Operations (GCO)*.
3. On the first page, under the flags, pick **COMMAND: BLUE** or **RED**. The page redraws for that coalition (flags, fleets and bases). Dynamic Campaign Mod itself has no side choice; SEST adds this one for GCO only (`WorldSideChoice=0` under `[Runtime]` removes it).
4. Choose **Theatre Commander** to command the whole coalition, or **Career** to start as one officer. A Career offers 15 starts across both sides (for example a US task force in the Luzon Strait, a Russian submarine off North Channel, a Chinese group near Scarborough Shoal); the navy you pick sets your side.
5. Read the opening brief. SEST shows a short brief first, then every Dynamic Campaign Mod section in full.

**Saves.**

- Use a **new game** to get the full revised layout.
- Dynamic Campaign Mod 1.0.2 can reopen a 1.0.x world save.
- Worlds from Dynamic Campaign Mod 0.25 and earlier need a new game.
- Your existing regional-expansion campaign keeps its identity. No conversion is run.
- **Old original World Sandbox saves:** the original world is kept outside the new-game menu. To show it again, close the game, open PowerShell in the MNO Workshop folder and paste:

  ```
  powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\select-legacy-world.ps1 -PackPath .
  ```

  To hide it again (game closed):

  ```
  powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\select-legacy-world.ps1 -PackPath . -Disable
  ```

  This helper only copies or removes that one campaign definition. It never edits your saves. Steam may restore the default layout when MNO updates.

**How you play it.**

- **Command and renown.** Battle results and completed Admiralty assignments earn renown. Eight command stages open more of the shipyard as your renown grows:

  | Stage | Title | Renown needed |
  |---|---|---|
  | 1 | Task Unit Commander | 0 |
  | 2 | Escort Group Commander | 300 |
  | 3 | Task Group Commander | 800 |
  | 4 | Flotilla Commander | 1,600 |
  | 5 | Force Commander | 2,800 |
  | 6 | Joint Force Commander | 4,500 |
  | 7 | Fleet Commander | 7,000 |
  | 8 | Theatre Commander | 10,500 |

- **Admiralty assignments.** Accept assignments in the Admiralty: escort, shadowing, area control and operations. They can reward renown and credits when their stated conditions are met. What is offered depends on the situation. Routine sailing and leaving a battle do not earn task rewards.
- **Shipyard.** Ship cards show each class's service years. Amphibious lift ships appear under both *Ships* and *Amphibious*. You can sort the list by column. Costs, unlocks and limits are Dynamic Campaign Mod's own.
- **Supply.** Fuel and ammunition are physical stocks. Depots produce them. Convoys move them. Airlift carries ammunition. Replenishment ships support forces at sea. Raise an exposed base's supply priority and escort its deliveries. A purchase gives you a hull; keeping it supplied is a separate job.
- **Extra airfields.** 40 additional airfields start at quarter stock. They add no income, production depots or extra aircraft.
- **Battles.** Play engagements in Sea Power and return to the map with the results. See 5.1 for the paused start and the end-of-battle flow.
- **F11 World Operations.** See 5.2.
- **Sea ice and weather** on the campaign map. See 5.3 and 5.4.

**Geography note.** 37 airfield positions or headings were reviewed against public airport data. Geographic checks cannot certify the game's own coastlines. Small reclaimed-island airfields are explicit exceptions.

**Known limits on Build 261123** (from the R16 notes):

- Old or uncertain contacts are no longer drawn faded on the campaign map.
- The scene-editor timer is lost.
- Map drawings use the game's own map frame, so east-west ring and ruler figures shrink with latitude, as on the game's own campaign map.

**Status:** built and tested in automated checks, awaiting PC confirmation on Build 261123. On the earlier R15 build (0.9.3 Build 261116 public beta, 22 November), the owner's PC started the world as Blue, drew the global weather layer with storms and sea ice, opened a polar battle and returned to the campaign with an autosave.

[owner to confirm: on R15 the game warned that 44 named ships used their class's default hull under the campaign name (for example Warramunga and Toowoomba). Is this fixed in R16?]

### 4.2 The five Task Force campaigns

All five use the game's own **Task Force Mode**, like the stock Pacific Strike campaign. You buy your force from a priced roster. The story releases more of it as you go. Losses, damage, ammunition and crew experience carry forward.

**Start one:** open **Campaigns** and choose *Southern Watch*, *Southern Reach - Tasman Shield*, *Red Line - The Other Watch*, *Sulu Line - The Island Road* or *Makran Line - The Fuel Road*. Choose your commander's nation in the Service Record when the campaign starts (see 5.9).

**Difficulty.** Each campaign offers three levels:

| Level | Starting points | Point cap | Repair cost |
|---|---|---|---|
| Supported | 1,250 | 1,500 (Sulu Line 1,600) | 75 % |
| Standard | 1,000 | 1,500 (Sulu Line 1,600) | 100 % |
| Veteran | 850 | 1,250 (Sulu Line 1,350) | 125 % |

[owner to confirm: another worker is editing campaign files at the time of writing; check these numbers and the mission counts below against the final build.]

**Summary.**

| Campaign | Navy (your side) | Theatre | When | Missions |
|---|---|---|---|---|
| Southern Watch | Royal Australian Navy | Arafura, Timor and Banda seas, north of Australia | Oct-Nov 2028 | 24: 12 core, 10 optional operations, 2 contingencies. Plus 11 single missions in *Southern Watch - Dispatches* |
| Southern Reach / Tasman Shield | Royal Australian Navy | Tasmania to the Antarctic ice edge, then the Tasman Sea | Dec 2028-Mar 2029 | 26 in two chapters (12 + 14), 3 optional |
| Red Line | People's Liberation Army Navy | Northern crisis and southern waters | Nov 2028-Feb 2029 | 9: 6 core, 2 optional air operations, 1 pilot-recovery contingency |
| Sulu Line | Philippine Navy | Sulu Sea and West Philippine Sea | Oct-Nov 2028 | 10: 7 core, 3 optional side operations |
| Makran Line | Pakistan Navy | North Arabian Sea | Oct-Nov 2028 | 4 |

**Southern Watch - The Northern Lifeline.** October 2028. A confrontation elsewhere in the Indo-Pacific has drawn most of America's ready combat power north. Forged orders and insurers refusing cover are closing the sea lanes above Australia. The Meridian Maritime Group offers escorts, inspections and access to its terminals, and some of its ships carry armed teams. When one escort fires on an Indonesian patrol in the Arafura Sea, HMAS Warramunga is the nearest warship. Over six weeks, the Australian-led task group protects people, fuel and supplies as the crisis spreads to the Biak enclave and Chinese carrier groups. Optional operations carry results into later missions. From the mission *Weapons Free*, every force allocation offers the whole roster and an allied fleet at its own navies' prices. The 11 *Dispatches* are single missions in the mission list: allied and opposing ships in the same weeks, a weapons range trial, a 2034 bomber escort and a 1988 exercise that went live.

**Southern Reach - Tasman Shield.** December 2028. Nine days after the northern ceasefire, the same network has come south under a new flag. A "fisheries and research protection" group is stopping Antarctic-bound ships off Tasmania, while a Russian submarine works the Macquarie Ridge. The Australian task group escorts the resupply season from Storm Bay to the ice edge at 60° South. In the second chapter, *Tasman Shield*, the escort follows the opposing group through Fiordland, Cook Strait, the Tasman, Bass Strait and the Bight, with New Zealand's Poseidons in support. Operations near Auckland and Adelaide decide which enemy detachments join the final fleet action. From *Tasman Crossing*, every force allocation offers the whole roster and the allied fleet.

**Red Line - The Other Watch.** You command the Chinese carrier group the Australians only hear on the radio. You win by restraint, deception, escort and evasion: classify the submarine trailing your carrier without firing on it, escort the Biak fuel run, fight for your reconnaissance aircraft, and stop a ceasefire spoiler while protecting the withdrawal. A submarine passage and a contested tender rendezvous vary the pace. Two optional air operations and a short pilot-recovery race sit between the six core missions. Coalition non-belligerents and civil traffic stay protected; declared hostile shooters can be engaged. From the first force allocation you can buy the whole roster, including the PLAN's Type 901 and Type 903A supply ships.

**Sulu Line - The Island Road.** October 2028. With most of America's ready combat power drawn north, the Philippine Navy holds the island supply road alone: Puerto Princesa to Balabac, the gun line off Jolo, the boats to Ayungin Shoal. A Philippine-led group, with a Royal Thai Navy detachment and later one Australian frigate, escorts convoys and fires for the Marines ashore. **There is no free rearm.** What a ship fires stays fired until a supply ship you bought comes alongside at sea (BRP Tarlac, the Thai oiler Chula or a chartered barge carrier), or until a convoy you escorted holds its service window. Supply ships are sold at three points only. Lose one and its cargo is gone. The three optional side operations are flown by other units, so your no-rearm magazines are untouched.

**Makran Line - The Fuel Road.** October 2028. Insurers are refusing cover on the tanker road from the Gulf to Karachi. A Pakistan Navy task group, Task Force 88, keeps the road open: the Karachi approaches, the Gwadar anchorage, a submarine trail off the Makran coast and the last convoy into Port Qasim. The opponent is the fictional Meridian network alone, in armed merchants and trawlers. Your force is the Tughril-class frigates, PNS Alamgir, their helicopters, and the Air Force's JF-17s and ZDK-03 from the second week. There is no Pakistani supply ship in the collection, so your ships rearm at Karachi between missions.

**In every campaign:**

- **Deployment zones.** Before each mission you can position your force inside a blue Deployment Zone, in Formation or Dispersed.
- **Fair openings.** No armed enemy ship or submarine starts within 25 NM of you, and nothing on the enemy side can fire in the first 5 minutes.
- **Time limits.** Each mission has a planned time. Reaching it shows *Behind Schedule*. The mission is lost at one and a half times the plan. The briefing states both.
- **Same-nation discount.** Units of your commander's own navy cost 20 % less. Partner units cost their listed price. Each campaign's rules page says which is which.
- **Briefings** have a photo banner, a chart, and photos of your forces and the expected opposition.

**Newer equipment in the campaigns (26 Nov 2026).** Several modern units now appear in authored missions:

| Mission | Unit | Role |
|---|---|---|
| Southern Reach 07, Beneath the South | RAN Ghost Shark XL-AUV with an Echidna SRT-01 | Your autonomous submarine on the Akula's track |
| Southern Reach 07 | Orca (Marine Fauna Expansion) | A second biologic contact for your sonar |
| Red Line 03, The Other Picture | WZ-7 Soaring Dragon (Chinese UAV Collection) | Your unarmed high-altitude reconnaissance drone |
| Southern Watch 06 | Mi-26 Halo | A PLA heavy-lift helicopter at the enclave |
| Southern Watch 07, Long Way Home | B-21 Raider; S-500 battery | A returning US bomber on your tanker; a Russian battery at the enclave field, out of reach of the corridor |
| Sulu Line 07, Balabac Strait | JAS-39 Gripen pair (Philippine Air Force) | Air cover against the JH-7A raid |
| Makran Line 01, The Fuel Road | Indian Navy Visakhapatnam-class destroyer | A neutral observer; not a target |

**Status.** Campaign data does not depend on the exact game build. Makran Line had not yet been run in game when the feature list was written. The rest have earlier PC play-tests on older game builds. On Build 261123, all five are built and tested in automated checks, awaiting PC confirmation.

---

## 5. Features

Unless a section says otherwise, the features in this chapter are SEST code. They run **only on Sea Power 0.9.3 Build 261123 public beta**, after SETUP has installed the beta features. On every other build they are off.

### Changing options

Many features have switches in `plugins\sest_runtime.ini`, in the `[Runtime]` section, inside the MNO folder. `1` means on, `0` means off. Restart the game after a change.
[owner to confirm: should players edit this file? Does a Steam update or SETUP overwrite their edits? The file shipped in the Workshop folder still has a header about Build 261021.]

### Feature status at a glance

| Feature | Default | Status on Build 261123 |
|---|---|---|
| Paused battle preparation | On | Built and tested in automated checks, awaiting PC confirmation |
| F11 World Operations (Overview, Forces, Combat Costs, Service) | On | Built and tested in automated checks, awaiting PC confirmation |
| Placed storms and the battle Weather layer | On | Built and tested in automated checks, awaiting PC confirmation |
| Local battle weather in every Dynamic Campaign Mod battle | On | Built and tested in automated checks, awaiting PC confirmation |
| Sea ice on the campaign map and in battles | On | Built and tested in automated checks, awaiting PC confirmation (R15 drew it on the PC, on another build) |
| Ice shelves | **Off** | Not yet tested on a PC |
| Icebergs | **Off** | Not yet tested on a PC |
| Coordinated Strike colours and cost estimates | On | Built and tested in automated checks, awaiting PC confirmation |
| Coordinated Strike pop-out button | **Off** | Off because it did not draw on the owner's second monitor (15 November) |
| Debrief runtime ribbons (Red Line) | On | Built and tested in automated checks, awaiting PC confirmation |
| Replenishment at sea, cross-deck, photos | Always (data) | Data features; not tied to the code build. Some parts not yet confirmed in game |

### 5.1 Battle preparation and the end of a battle

**What it does.** When a campaign battle opens, the clock does not run while you get ready. SEST rewrites the *Aircraft and Unit Preparation* popup as four numbered steps with a **Start preparation** button. Your own units show on the map from the first paused moment.

**How to use it.**

1. Enter a campaign engagement. The game is paused.
2. Work through the preparation checklist. The clock stays stopped while it is open.
3. Press **Start preparation**. The game stays paused.
4. Review your ships and aircraft, then start the clock yourself.
5. To finish a world battle, use the end-battle option. Go through the debrief and you return to the campaign.

**Options.** `PreparationMap=0` turns off plotting your own units while paused.

### 5.2 F11 World Operations and combat costs

**What it does.** On the GCO campaign map, **F11** opens *World Operations*, a movable, resizable window with four tabs:

| Tab | What it shows |
|---|---|
| Overview | Your command stage, the next renown milestone, and live Admiralty tasks: offered and active tasks, rewards, failure penalties, offer expiry and deadlines |
| Forces | Your forces |
| Combat Costs | Estimated spending (in US dollars) by mission or across the campaign, from the manual engagements recorded in the loaded save |
| Service | Your world service ribbons (see 5.9) |

A **Combat Costs** button also sits directly beneath *Economy* in the left sidebar of the campaign map. It opens the same report.

In a mission, F11 opens the mission's cost windows.

**Two kinds of money.** Campaign credits (what you spend in the shipyard) are separate from the estimated USD combat prices. The USD figures are gameplay replacement-cost estimates, not real contract prices. SEST gives a price to every weapon, ship, aircraft and land unit in the collection: 2,310 weapons, 1,024 vessels, 811 aircraft and 533 land units. See `COST-COMPATIBILITY.txt`.

**Rules.**

- The window only shows information. It does not pay rewards.
- Opening it, or routine travel, cannot earn renown.

**How to use it.** On the campaign map, press **F11**, or click **Combat Costs** under *Economy*. Press F11 again to close.

**Options.** `CampaignCombatCosts`, `CombatCostInventories` and `CumulativeCombatCosts` (all `1` by default) control the cost reports.

### 5.3 Weather, storms and local battle weather

#### Placed storms

**What it does.** A campaign author can place named storms with tracks. They appear inside Dynamic Campaign Mod's own weather: the weather layer, the storm list (past track, forecast points, cone), map hover, battle weather and Dynamic Campaign Mod's route and deck rules all see the same storm. Your saves and Dynamic Campaign Mod's files are not changed. A campaign without placed storms is untouched.

**Where you see it.** GCO itself does not place any storms. It uses Dynamic Campaign Mod's own weather systems. Cyclone DARYA belongs to a separate Hormuz test campaign. [owner to confirm: is the Hormuz test campaign distributed to players? It is not in the MNO folder.]

**Options.** `WorldStorms=0` keeps Dynamic Campaign Mod's weather exactly as it is.

#### The Weather layer on the battle map

**What it does.** In a Dynamic Campaign Mod battle, the tactical map's **Layers** menu gets a **Weather** entry. It draws every storm in the campaign's weather at the battle time: placed storms, and Dynamic Campaign Mod's own tropical cyclones and gales. For each storm you see:

- a centre marker with its name and wind;
- the gale-force ring and the core ring;
- the track ahead to +1, +3, +6 and +12 hours.

Hover inside a storm for a readout. The layer moves with the battle clock.

**How to use it.** In a campaign battle, open the tactical map, open **Layers** and tick **Weather**.

**Options.** `WorldStormsMapLayer=0` removes the menu entry.

#### Local battle weather

**What it does.** In every Dynamic Campaign Mod battle (GCO included), the weather you see follows where you look. It changes as the campaign's weather systems move over the battle's time. It covers sea state, wind direction, rain, thunder, snow and fog. Changes are gradual: sea state changes at most once every 25 seconds, and only after the view has stayed in the new weather for 5 seconds.

- **Aircraft views:** above 1,500 m, the sea state below the aircraft is held, so it does not change as you fly.
- **The mission's own weather is the baseline.** Saves store it, and it comes back when the battle ends.
- **A mission trigger's *Set Weather* becomes the new baseline.**
- It only runs in a battle whose weather Dynamic Campaign Mod wrote. Other battles keep their own weather.

**How to use it.** Nothing to do. Attach the camera to a ship near bad weather and watch the sea state and rain over a few minutes of game time.

**Options.**

| Key | Default | Effect |
|---|---|---|
| `LocalWeatherView` | 1 | 0 turns local battle weather off |
| `LocalWeatherAllBattles` | 1 | 0 limits it to campaigns with placed storms |
| `LocalWeatherAircraft` | 1 | 0 drops the aircraft height rule |
| `LocalWeatherAirSeaMaxM` | 1500 | The height in metres above which an aircraft view holds the sea state |
| `LocalWeatherClouds` | 0 | 1 lets clouds follow too, one step every 120 seconds |
| `LocalWeatherFollow` | view | `centre` samples the battle centre instead of your view |

**In the Task Force campaigns** (data, all builds): ships make less speed in heavy seas, and objectives are placed so they can still be reached in time.

### 5.4 Sea ice

Sea ice comes from a seasonal climatology based on NSIDC monthly ice-extent data (2016-2025). It is a model for game rules, not an ice chart. The Sea of Okhotsk, the Bering Sea and the Chukchi Sea have their own regional seasons. The ice edge follows NSIDC's measured monthly edge for 2016-2025 from the Greenland Sea east to the Beaufort Sea, and all round Antarctica (for example about 55° South south of Africa in September, and open water off Dronning Maud Land in February while the western Weddell Sea keeps its pack).

#### On the campaign map

**What it does.**

- Ice is drawn on the campaign globe, on every weather layer, and alone when the weather layer is off.
- The forecast slider shows the forecast day's ice.
- Hovering shows a reading such as "Ice 72 % (heavy pack)".
- Surface groups are slowed by the ice at their position.
- Dynamic Campaign Mod's own "hide weather" performance setting hides the ice too.

**Options.** `CampaignIce=0` turns it all off. `CampaignIceMap=0` or `CampaignIceMovement=0` leave out one part.

#### In battles

**What it does.**

- **One ice edge, 10 %.** Below 10 % there is no ice for any rule or picture. At or above it, ice is drawn and acts, so whatever slows a ship is on screen.
- **Floes.** In patchy ice (below about 60 %) you see separate floes, not one large sheet.
- **Contact.** Ships slow, and make ice effects, only where the hull meets drawn ice. Sailing between floes is full speed. Sailing into a floe slows the ship and makes a grinding sound.
- **Channels.** A ship pushes small floes aside as it goes.
- **Speed bands** (every ship currently counts as having no ice strengthening):

  | Ice concentration | Effect on a ship in the ice |
  |---|---|
  | Below 10 % | None |
  | 10-30 % | Up to 70 % of top speed |
  | 30-60 % | Up to 40 % of top speed |
  | 60 % and over (heavy pack) | Blocked. The ship can still go astern at 40 %, go ahead at 40 % towards lighter ice, and keeps steerage way (10 %) into heavier ice, so it is never trapped |

- **Submarines.** Under heavy pack (60 % and over), a submarine may not come shallower than 30 m, raise a mast or snorkel, or blow to the surface, unless it is in open water between floes.
- **Sonar.** Ice adds to ocean noise, so sonars and torpedo seekers hear the seasonal ice.
- **Effects.** Broken ice pieces at the bow and a breaking sound for the nearest ships. Sounds are muted above 2× time compression.
- **Polar frame.** Polar battles use a polar frame from 85° latitude.
- **Mission clock.** The ice appears once the mission has loaded and has its date.

**The Sea ice map layer.** On the tactical map, open **Layers** and tick **Sea ice**. It shows a pale fill, the ice edge as a cyan line and the heavy pack (60 %) as a navy line, under your unit symbols. Hover for a reading and what the ice does to ships and submarines. It also shows on Topographic Map's looks.

**How to use it.** Nothing to set. Play a battle in polar water in the right season.

**Options.**

| Key | Default | Effect |
|---|---|---|
| `SeaIce` | 1 | 0 keeps battles as before |
| `SeaIceEdgePercent` | 10 | Moves the ice edge for every ice rule and picture (15 is the NSIDC extent line) |
| `SeaIceShips`, `SeaIceSubmarines`, `SeaIceNoise`, `SeaIceSheet` | 1 | 0 leaves out that part |
| `SeaIceMapLayer` | 1 | 0 removes the *Sea ice* map layer |
| `SeaIceSound` | 1 | 0 turns the breaking sound off |

**Status.** Built and tested in automated checks, awaiting PC confirmation. On the earlier R15 build, the owner's PC drew ice on the campaign map and a tactical ice sheet in a Barents battle (22 November).

### 5.5 Ice shelves and icebergs (off by default)

These two features are **off by default** and **not yet tested on a PC**.

**What they do.**

- **Ice shelves** (`IceShelves=1`): Antarctic ice-shelf fronts are drawn as ice cliffs. Ships and submarines are kept out, with a stand-off. The shelf outlines are a fixed past position (about 2003-2012); later calvings are not shown.
- **Icebergs** (`Icebergs=1`): icebergs from a climatology, drifting, and melting if you set a sea temperature. The same seed gives the same bergs. Giant bergs are never generated. Densities are estimates.

**How to turn them on.** Quit the game. In `plugins\sest_runtime.ini`, under `[Runtime]`, add `IceShelves=1` and/or `Icebergs=1`. Start the game.

**Options** (out-of-range values fall back to the default):

| Key | Default | Effect |
|---|---|---|
| `IceShelfViewKm` | 30 | Draw cliffs within this distance of the camera (5-80) |
| `IceShelfStandoffNm` | 2 | Submarine stand-off from a front (0.5-10) |
| `IceShelfSurfaceLimitNm` | 0.1 | How far off a front surface ships stop (0.05-2) |
| `IcebergRadiusNm` | 25 | Bergs exist within this distance of the camera (5-60) |
| `IcebergViewKm` | 30 | Bergs are drawn within this distance (2-60) |
| `IcebergMaxDrawn` | 400 | Most berg objects at once (20-3000) |
| `IcebergSeed` | 0 | Generator seed |
| `IcebergSstC` | unset | Sea temperature for melt, °C (-2 to 15). Unset: no melt |
| `IceFeaturesDiagnostics` | 0 | 1 writes log lines |

### 5.6 Replenishment at sea and supply

This is a **data feature**. It works on any build.

**What it does.** Before MNO, most modern warships could not reload anti-ship missiles, torpedoes or VLS strike rounds at sea. MNO gives about 2,200 launchers a way to be refilled from a supply ship alongside. It also gives supply systems to upstream auxiliaries, adds eight modern replenishment ships, and makes HMAS Supply and Stalwart work. There are 26 supply-capable hulls from MNO, plus RE-power's own 8.

**How to use it.** Three things must be true at once:

1. **Get close.** Between 0.3 and 1.0 nautical miles, depending on the ship.
2. **Slow down.** Both ships. Most auxiliaries stop supplying above 13 knots, and the receiving ship above 16. The Don tender needs 5 knots.
3. **Wait.** Rounds come across one at a time. Heavy rounds take minutes. A full 8-cell Tomahawk module off a Supply-class takes about four and a half minutes.

Most auxiliaries serve two ships at once. The Akademik Pashin serves one.

**Pick the right supply ship.** Each has a size ceiling: the heaviest single round it can pass.

| Tier | Ships | What they pass |
|---|---|---|
| No ceiling | Supply-class T-AOE, Sacramento AOE, Lewis and Clark T-AKE, Kilauea AE, Algol T-AKR | Anything |
| Middle | Type 901, Boris Chilikin, Mashuu, Tide, Type 903A, Don tender, HMAS Supply | Tomahawk and Mk 48, but not the heaviest rounds |
| Fuel first | Henry J. Kaiser T-AO, Teide, T2, Kazbek, Sealift Pacific, Delvar, Akademik Pashin | Guns, CIWS, ESSM, RAM, SM-2MR, Harpoon, ship torpedoes. No strike rounds |

**Limits.**

- A supply ship's stock runs down and is **not refilled at sea**.
- Submarines can be resupplied too.
- Some rounds still cannot be reloaded: sealed deck tubes on Cold War hulls, some Italian and French hulls, and SS-N-19 Granit by design.
- Aircraft rearm from their deck or airbase as normal. This feature does not touch them.

**In GCO,** supply is also strategic: see 4.1. **In Sulu Line,** there is no free rearm: see 4.2.

**Status.** Transfers from HMAS Supply and Stalwart, and Sulu Line's no-rearm rule, were listed as not yet confirmed in game.

### 5.7 Cross-deck operations

This is a **data feature** (the *SEST Cross-Deck* pack). It works on any build.

**What it does.** A flight deck that already flies one member of an aircraft family now also takes the allied members of that family. For example, a deck that flies one Seahawk takes the other navies' Seahawks too. Families include Seahawk, NH90, Lynx/Wildcat, Merlin, Sea King, AB 212, Panther, Seasprite, Wasp, Alouette, Harrier and AV-8B/F-35B. Each ship's own list is kept. A deck that already accepts every helicopter is left alone. Only aircraft in the collection are added.

Some decks also take the exact aircraft one campaign flies from them, for example the Philippine H-76 on Sulu Line's frigates, and the Pakistani Z-9CE on the Tughril and Alamgir in Makran Line.

**How to use it.** Nothing to set. Land an allied helicopter on an allied deck. `CROSS-DECK.txt` in the MNO folder lists every deck changed (147 entries) and the aircraft it gained.

**Status.** Listed as not yet confirmed in game.

### 5.8 Coordinated Strike Tool refinements

**What it does.** Coordinated Strike Tool's **F8** planner keeps its author's own controls and launch logic. SEST only changes how it looks and adds information:

- shared SEST colours and easier-to-read sections;
- planned and remaining weapon-cost estimates.

Selection, timing, readiness, salvo commands and launch logic stay the author's.

**How to use it.** In a mission, press **F8** to open the planner as usual.

**Options.** `StrikePopOut=1` adds a *Pop out* / *Return* button to the panel's title bar, to move it to a second monitor (needs Pop-Out Windows). It is **off by default**, because on 15 November the owner's PC did not draw the panel on the second monitor. If the pop-out cannot draw or receive clicks there, SEST withdraws the button for that session.

### 5.9 Ribbons and service awards

#### World service awards (GCO, Build 261123 only)

**What it does.** 25 fictional world awards recognise:

- **manual battles:** 3, 10, 20 and 50 battles;
- **watch awards:** battles on 5 and 15 different campaign days;
- **theatre service and veteran:** 2 and 5 positioned battles in each of the six theatres;
- **expeditionary and global command:** service in 3 theatres and in all 6;
- **Admiralty duties:** 5 completed accepted tasks; 3 different task types; and specialist ribbons (Convoy Protection, Maritime Surveillance, Route Security) for 3 of each kind.

**Rules.**

- Auto-resolved battles do not count for battle awards.
- Failed, cancelled, declined, lapsed and unaccepted tasks do not count.
- A completion replayed after reloading a save counts once.
- A multi-phase operation counts once, when its final phase completes.
- Ribbons add no renown, credits or supplies.

**How to use it.** Press **F11** on the campaign map and open the **Service** tab.

Ribbons are kept per playthrough: every save of one campaign start shares the same record, and starting a new campaign begins a new one.

#### Task Force campaign awards (data, all builds)

**Choosing your commander's nation.** Choose it in the Service Record when a campaign starts. A commander already in a save keeps their nation and name.

| Campaign | Default nation | Other choices |
|---|---|---|
| Southern Watch, Southern Reach | Australia | US, UK, Japan, New Zealand, France, Canada, South Korea, Spain, Italy, Germany, the Netherlands, Norway, Denmark |
| Sulu Line | Philippines | Thailand, Australia |
| Red Line | China only | none |
| Makran Line | Pakistan only | none |

Each nation has its navy's name, ranks and an emblem. The same-nation discount follows your commander's nation.

**Ribbons.**

- Five fictional completion ribbons, one per campaign.
- Ten fictional operation ribbons, each for a named mission's required result.
- Representations of real awards for some nations in Southern Watch, Southern Reach and Sulu Line. Each citation ends: "Game award for a fictional operation; not a real honour."
- Red Line and Makran Line have fictional ribbons only.

`RIBBONS.txt` in the MNO folder lists every award and the mission that earns it.

#### Debrief runtime ribbons (Red Line, Build 261123 only)

Two extra fictional Red Line ribbons are granted at the debrief by SEST's code:

- **RL05 Silent Passage:** complete *Under the Convergence*'s Passage objective with **no weapon launched and no gun round fired** by your task force. A failed launch counts as a launch. Noisemakers, chaff, decoys, sonobuoys and CIWS rounds do not.
- **RLC1 Personnel Recovery:** complete *Pilot in the Water*'s Pilot objective and recover at least one survivor.

A ribbon you already hold is not granted again. `MissionAwards=0` turns these off. The game's developer ribbon menu does not offer them; that is expected.

**Status.** Built and tested in automated checks, awaiting PC confirmation. Makran Line's Pakistan Navy rank abbreviations have not been verified against official sources.

### 5.10 Encyclopedia photos and the offline gallery

This is a **data feature**. It works on any build.

**What it does.**

- **Encyclopedia:** MNO ships 872 encyclopedia pictures, all real photographs. Each picture carries its photographer and licence. Where a unit has no exact photo, a photo of the same class is used, and the picture says "Class photo". R16 adds 117 newly reviewed photographs (for example K9 Thunder, 2S43 Malva and NSM).
- **Briefings:** every SEST mission briefing ends with a RECOGNITION section showing photos of your forces and the expected opposition, with credits.
- **Offline gallery:** a browser page of the photos, flags and loading-screen backgrounds, with a unit index.

**How to open the gallery.**

1. In the Mod Manager, select *Modern Naval Operations* and press **Open Folder**.
2. Open the **Gallery** folder.
3. Double-click **gallery.html**. It opens in your web browser and works offline.

`visual_overhaul.html` in the same folder shows the flags and backgrounds. `PHOTO_CREDITS.txt` and `VISUAL_CREDITS.txt` credit every image.

Only real photographs are used. No AI imagery.

[owner to confirm: the Gallery's README.txt still says 517 photographs and 601 encyclopedia units, while CREDITS.txt says 872 encyclopedia pictures. Update the Gallery README for R16.]

### 5.11 Keys and UI changes

| Key | What it does | Comes from |
|---|---|---|
| **F11** | World Operations on the GCO map; cost windows in a mission | SEST (Build 261123) |
| **F8** | Coordinated Strike planner | Coordinated Strike Tool (a Required Item) |
| **F6** | Topographic Map | Sea Power Topographic Map (a Required Item) |
| **Ctrl+F9** | Quick Load, where SEST's UI companion is active and your Quick Load key was plain F9 | SEST moves the game's own key |

**Contact Log keys.** Contact Log ships with F6 (open window) and F8 (run probe). These clash with Topographic Map's F6 and Coordinated Strike Tool's F8, and the probe can stall the game. SETUP sets each to *None*, but only while it still holds that exact default. A key you set yourself is kept. Contact Log's window stays on its bottom-bar button.

- If Contact Log has no settings file yet, start Sea Power once with it, quit, and run SETUP again.
- SETUP keeps the original file beside it as `com.seapower.contactlog.cfg.sest-ui-keys.bak` (in `BepInEx\config`). To undo, copy it back over the `.cfg` with the game closed.

**Other UI changes.**

- **Beta watermark hidden.** The beta's build text over the game view is hidden. `HideVersionWatermark=0` keeps it.
- **Tactical map lines** (data): black by day, white at night, fully opaque and thicker, with the selected route in red.
- **Menu film and backdrops:** SEST's menu plugin plays a film of SEST Gallery photographs behind the main menu, and shows SEST photographs behind loading screens and menu pages. In `plugins\sest_menu.ini`, `Enabled=0` turns it off and `Backdrops=0` puts the game's backdrops back. [owner to confirm: does the menu background plugin run on Build 261123?]

Sensor View switches the 3D view with `]` by default (set it in `BepInEx/config/local.sensorview.cfg`). R.A.T.S. Sensor Views uses `Ctrl+Insert` for the board, `Ctrl+PageUp` for the scope, `Ctrl+PageDown` for sonar, `Ctrl+Shift+PageUp` for sensor lines and `Ctrl+Shift+PageDown` for coverage; you can change them on its options page.

### 5.12 Working with other code mods

On Build 261123, SEST's loader starts other authors' code mods. It checks each one first. A mod that still needs game code 0.9.3 lacks, or whose own build check rejects 0.9.3, is held before it loads. It is named in `BepInEx\LogOutput.log`. Its data is kept.

**Started or adapted by SEST on Build 261123** (built and tested in automated checks, awaiting PC confirmation):

| Mod | What SEST does |
|---|---|
| Dynamic Campaign Mod 1.0.2 (Bungalow) | Bridged in memory for the Build 261123 map change |
| Anchor Chain | SEST's loader waits for the Workshop folders, then starts Anchor Chain itself |
| R.A.T.S. Topographic Map 1.8.1 | Adapted |
| R.A.T.S. Pop-Out Windows 1.4.1 | Pinned; SEST's pop-out bridges use it |
| R.A.T.S. Rigging 1.0.1 | One verified copy loaded |
| Better Tac Map | Started and adapted |
| Enhanced Decoy 0.5.4 | Adapted, so it no longer rolls itself back (see below) |
| Multi-Stage Missiles | Adapted |
| J-36 systems, Osprey, Z-21, Jiutian UAV | Adapted |
| RAN / Echidna SRT-01, RAN Ghost Shark XL-AUV | Started without R.A.T.S. Keel |
| Sensor View | Only one copy loaded (no doubled overlay) |
| Identify Expanded | Its settings and audio are redirected; SETUP moves a local copy out of the game folder |
| Group Manager 0.2.22 | Loads from its own Workshop file |

Enhanced Decoy comes in the Euromod - Anchorchain Expansion Pack (3784474738), with Missile Control, Test Range and Multi-Stage Missiles.

**Enhanced Decoy on Build 261123.** Try it with the game's *Realistic Countermeasures* off and on:

- **Off:** a chaff order fires the mod's chaff salvo, and the order log says chaff is out. Chaff also goes out on its own against an incoming radar missile.
- **On:** a chaff order still follows the mod and fires chaff only, no flares. A flare order fires flares as without the mod. Automatic release is the game's own.
- Two of the mod's features are off on this build: its air-decoy lifetime extension and one per-search radar filter. So an air decoy may end a little earlier or later than the mod intends.

**Echidna and Ghost Shark** can be placed in the mission editor. They are not yet placed in the RAN campaigns.

**Held back** (they wait for their authors' updates, or by the owner's choice):

| Held | Why |
|---|---|
| Alpine-family code (Alpine Sea Power, MV-75 tilt, MV-75 crew escape, EC-2 jamming, exterior cameras, XQ-58 Shadow) | Their own build check rejects 0.9.3 |
| Saronic Corsair strike code, K5 Kraken contact strike | Their own build check rejects 0.9.3 |
| ExtendedGuidance | Kept off by the owner: SEST's missile tuning assumes the game's own hit chances |
| R.A.T.S. Keel | Not used: it is a loader that would replace SEST's loader |

While these are held, the units still load and play from their data. Only the extra code behaviour is missing (for example, the EC-2 still jams radar, but not radio and data links).

### 5.13 Smaller fixes that run in the background

These run without any action from you. Each has a switch in `plugins\sest_runtime.ini`.

| Fix | What it does | Switch |
|---|---|---|
| Terrain clearance | Keeps a 500 ft floor over land ahead for the Tomahawk MST Block Va in cruise | `TerrainClearance` |
| Task Force debrief | Lists again the ships lost in a mission you allocated the force for | `TaskForceDebrief` |
| Towed sensor guard | Guards towed sonars that have an incomplete link | `TowedSensorGuard` |
| Modifier registry repair | Makes sure every mod's `#!extend` files load, including MNO's cost catalogues and Cross-Deck files | `ModifierRegistry` |

MNO's data also carries many fixes where two mods clash: missile and bomb values, carrier and helicopter references, unit names, flags for 11 nations, airbase launch rates and English loading tips. `CREDITS.txt` lists every mod file MNO carries a changed copy of.

---

## 6. Troubleshooting and reporting a problem

### Common problems

| Problem | What to do |
|---|---|
| SETUP says mods are not downloaded | Press **Subscribe to all** on the collection again, or open the links SETUP lists. Wait for Steam to finish. Run SETUP again |
| SETUP says more than one copy of the pack is subscribed | Unsubscribe from all but one, keeping the one in the collection |
| SETUP says a copy is also in the game folder | Delete that folder, or unsubscribe and run SETUP from that folder |
| SETUP asks for a menu probe | Start Sea Power, wait about ten seconds at the main menu, quit, run SETUP again |
| The Mod Manager offers to move dependencies above MNO | Say no. If it happened, run SETUP again |
| Mods show as "not compatible" at start-up | Run SETUP again with the game closed. The warning does not switch them off |
| No F11 window, no sea ice, no local weather | Check your build (section 3). These need Build 261123 and the beta features on. Run SETUP and read its first step |
| Other authors' code mods stopped working on Build 261123 | Check you have not turned the beta features off. On this build, code mods load only through SEST's loader |
| A mission freezes | Run SETUP again. It turns off a known mod's debug logging that can freeze missions |
| The log says "Could not find AnchorChain chainloader" | On 0.9.3 this line alone is not a fault. SEST's loader starts Anchor Chain itself. SETUP's first step reports `[ok]` if the last launch ran to the end |
| Coordinated Strike's F8 planner does not open | SETUP may have warned about a partial BepInEx install. Reinstall the preloader from Anchor Chain's Workshop page |
| A discontinued `SEST.BetaAnchorBootstrap.dll` is in `BepInEx\plugins` | With the game closed, remove it. The supported file is `SEST.BetaSafeBootstrap.dll` |

### Checking that the features loaded

After a first launch to the main menu on Build 261123, `BepInEx\LogOutput.log` (in the game folder) should show:

- `Sea Power 0.9.3-261123 verified (ea653e49)`
- a line starting `ADAPTED DynamicCampaignMod`

### Where the logs are

| File | Where |
|---|---|
| `LogOutput.log` | `BepInEx\LogOutput.log` in the Sea Power game folder |
| `Player.log` | `%USERPROFILE%\AppData\LocalLow\Triassic Games\Sea Power\Player.log` |
| Game settings (the Mod Manager order) | `%USERPROFILE%\AppData\LocalLow\Triassic Games\Sea Power\usersettings.ini` |
| SETUP's backups and the beta-feature backups | `%LOCALAPPDATA%\SEST\` |

### How to report a problem

Report in either place: the MNO Workshop item's pinned discussion, or GitHub issues on the SEST-HOBBY/Seapower-mods repository.

Include:

1. your **game build and Steam branch** (SETUP's first step names it);
2. the **campaign and mission name**;
3. the **last SETUP message**, and the exact wording of any `[!!]` line;
4. **what you saw on screen**;
5. for a map or pop-out fault, **which layer or window was open**;
6. `LogOutput.log` and `Player.log` from the session where it happened.

If the problem is with a particular unit or mod, please credit its original author when you report it.

---

## 7. Credits and licence

### Credits

- **Modern Naval Operations** is by SocRefleX27 / SEST-DEV.
- **Dynamic Campaign Mod** is by **Bungalow** (Workshop 3813157776). GCO runs on it. It is a Required Item, and SEST adapts it in memory on Build 261123. Nothing of it is shipped in MNO.
- **Anchor Chain** and its preloader belong to their authors. SEST's modified Anchor Chain keeps its MIT notice.
- **R.A.T.S.** mods (Topographic Map, Pop-Out Windows, Rigging, Sensor Views), **Sensor View**, **RAN / Echidna SRT-01** and **RAN Ghost Shark XL-AUV** are their authors' work. The Topographic Map adapter keeps the Topography MIT notice.
- **Coordinated Strike Tool**, **Combat Cost Tracker**, **Contact Log**, **Group Manager**, **Better TacMap**, **Identify Expanded**, **RE-power** and every ship, aircraft and weapon mod in the collection belong to their authors.
- The **RAAF F-35A** model and textures are by Greene. The mod was removed from the Workshop, so MNO carries them. [owner to confirm: permission requests for this and other close-adapted material were being drafted; the public post waits for the answers.]
- **Photographs** come from Wikimedia Commons, government archives and other sources. Each keeps its own licence. `Gallery\PHOTO_CREDITS.txt` credits every one.

`CREDITS.txt` in the MNO folder lists every mod file MNO carries a changed copy of and the mod it came from. `REQUIRED-MODS.txt` lists every Required Item.

### Licence summary

| Part | Licence |
|---|---|
| Original code and tooling (scripts, SETUP, C# plugins, runtime bridges, technical docs) | MIT License (see `LICENSE-MIT`) |
| Original missions, campaigns, briefings and original UI artwork | Copyright (c) 2026 SocRefleX27 / SEST-DEV, Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 (CC BY-NC-ND 4.0) |
| Files from other projects (for example the Anchor Chain fork) | Their own notices |
| Modified copies of other authors' Workshop files | Remain their authors' property, under their terms. Neither licence above applies |
| Photographs | Their own licences (public domain, CC0, CC BY, CC BY-SA, OGL). Credits must stay with the photos |

**What CC BY-NC-ND 4.0 means for you:** you may share the original missions and campaigns unchanged, with credit, for non-commercial purposes. You may not publish modified versions. Fixes and suggestions are welcome as issues or pull requests to the repository. For any other use, ask SEST-DEV.

MNO is a free, non-commercial community project. It is not affiliated with, endorsed by or sponsored by Triassic Games or MicroProse. See `LICENSE.md` for the full terms.

[owner to confirm: the owner chose a "personal-play notice" wording for the new MNO item. That wording is not in the repository yet, so this summary follows the current `LICENSE.md`.]
