# Combat Cost Tracker 0.7.1: review (24 Oct 2026)

Workshop 3807187341, `CombatCosts.dll` 0.7.1.0 (SHA-256 `74afa902…`, the build recorded in `data/combat-cost-capture.json`), read from the
owner's 23 Oct capture with dnfile/dncil only; it was not run, changed or copied into the repository. Game: Sea Power 0.8.7 (`eab2297b…`).
SEST never patches the tracker; what SEST can do is in data (its `#!extend` catalogs) and in its own plugin.

## Summary

- **It works on 0.8.7.** Every game type, field and method it binds or patches exists in 0.8.7 with the type it expects.
- **Most expendables are silently left out.** The tracker gives a category only to missiles, torpedoes, bombs, rockets, guns, depth charges and
  ASW rounds. Chaff, flares, noisemakers, sonobuoys, fuel tanks, pods and similar stores fall to its default category, `Ignore`: they are not
  counted, not priced and not flagged as missing. (A first reading said this made the tracker crash; the code shows the default is `Ignore`,
  never empty, so it does not crash - it under-counts.) SEST can fix this in data: give those items a category in `SEST_Combat_Costs`, and they
  are counted, shown as `+ ?` until priced.
- **One display error switches it off for the session.** Any exception in its twice-a-second refresh removes its loss hooks too, so later losses
  go unrecorded and later saves lack its loss data. Only a restart restores it.
- **Losses it never prices:** aircraft destroyed off the flight path (on deck, taxiing, landing crashes, parked at a destroyed base) - the panel
  blames an old save for these, which is untrue; land platforms; crew, fuel, repairs and damage; stores pooled as air-group points.
- **Per mission only:** totals are lost at mission end; there is no campaign total. SEST's design for one is in
  `docs/combat-costs/campaign-costs-design.md`.

## Findings

### Stores with no category are silently excluded (not a crash, as first read)

*bug*

- **Effect:** Chaff, flares, noisemakers, sonobuoys, fuel tanks, pods, MOSS and paratrooper loads add nothing to the weapon total or to lost stores, and no "+ ?" says so. On 0.8.7 chaff and noisemaker launches reach the weapons-spent counter, so they are routinely dropped.
- **Evidence:** `Price::.ctor` sets `Category = "Ignore"`; `CostRules.Resolve` overwrites it only with a validated catalog or inline category or one of its fallbacks (ASM, AAM, SAM, ASW, Other, Torpedo, Bomb, Gun, Rocket). Types outside the fallback table keep `Ignore`, which the snapshot skips. Checked in the IL on 24 Oct 2026 (every `stfld Price::Category` stores a literal or a validated string). About 424 ammunition files in the collection have such a type and no category.
- **Fix for the author:** Never return a null category:
- default to 'Other', as VesselRules does, or derive one: Chaff, Noisemaker and Decoy → 'Decoy'; Sonobuoy → 'ASW'; Fueltank → 'Fuel tank' or Ignore; Container → 'Other';
- make FactionTotals.Get null-safe;
- treat an invalid category as 'Other' with the warning, rather than 'excluded';
- catch failures per entry and mark the entry incomplete instead of failing the snapshot.
- **What SEST can do:** Data only, no DLL change:
- Through #!extend, ship a category-only section in SEST_Combat_Costs/systems/sest_weapon_costs.ini for every ammunition reference whose type the tracker cannot classify. Use Category=Decoy, ASW, Fuel tank or Other with blank prices, which stay unknown and show '?'; or Category=Ignore if the owner prefers to leave decoys and tanks out.
- Generate those sections in build_pack.py from the inventory's [General] Type. No author section is replaced, because none exists.
- Port the tracker's fallback table into costs.py and add a gate: every weapon a fielded unit can carry or fire must resolve to a non-null, valid category.
- Tighten costs.estimate_fields to the tracker's real rule ([A-Za-z0-9 _-]{1,20}); today it checks length only.
- Add a PC acceptance step: lose a ship carrying chaff with the panel visible, then grep Player.log for 'Overlay disabled'.
- Report the IL evidence to the author.
This cannot protect against ammunition SEST does not ship or know about.

### Any display error also stops loss capture, and later saves lose the tracker's data

*bug*

- **Effect:** A pricing or display problem silently turns a complete loss record into an incomplete one for the rest of the session, including in saved games. Only a restart restores tracking.
- **Evidence:** Overlay.Update has a single try block (IL_0009–IL_027a). The catch calls Vessels.Stop(), which runs Harmony.UnpatchSelf, then sets missionActive=false and enabled=false. Snapshot itself runs only while the panel is visible. AfterSave exists only while patched, so a save made after the failure lacks WeaponCostsLostStoresV1 and WeaponCostsAirLossesV1. On load, Snapshot then finds registers without ledger entries and reports UnknownInventories or UnknownAirLosses.
- **Fix for the author:** Keep the capture hooks separate from the display. Catch errors per side and per row, show a 'pricing error' note, keep Harmony patched, and retry at the next refresh or mission. UnpatchSelf only for binding failures.
- **What SEST can do:** Remove the known trigger with the category data above. Have SEST's capture tooling flag 'Overlay disabled after a read failure' and 'Disabled: unsupported API' in Player.log. Say in docs/combat-costs/README.md that the panel must be visible for the failure to occur and what the line means.

### Aircraft destroyed while not flying are never priced, and the note blames an old save

*bug*

- **Effect:** Aircraft lost on a deck spot, while taxiing, in a landing or bolter crash, or parked at a destroyed land air base add no cost. The panel says these losses come from an earlier save, which is untrue.
- **Evidence:** BeforeRegister captures a non-vessel only when AircraftApi.InFlight (Aircraft/Helicopter._isInFlight) is true. ObjectBase.setDestroyedFlag registers the aircraft carried by a lost unit through Taskforce.RegisterNotLaunchedVehicle, which is not hooked. Land units are never vessels. VesselApi.Snapshot reports the remainder as UnknownAirLosses = registered − captured − on board, and OverlayContent words it 'prior/unclassified air losses unavailable'.
- **Fix for the author:** Capture airframe losses that happen off the flight path too: price destroyed aircraft registers not covered by a ship ledger, or hook RegisterNotLaunchedVehicle. Give it its own note, e.g. 'aircraft lost on deck or ground'.
- **What SEST can do:** Document the gap. A SEST plugin computing its own totals could price these from the game's UnitStatusRegister: destroyed Aircraft or Helicopter registers minus those the tracker captured.

### The 'not enabled at startup' check runs once, depends on timing, and names the mod wrongly

*risk*

- **Effect:** On the first launch after subscribing, or whenever the mod is ticked after the game has started, the tracker stays off until restart, which the message does say. A future change in when the game fills the IsChecked flags, or an install whose DLL is not in the mod's root folder, would switch it off silently. The message says 'Weapon Costs' while the mod manager lists 'Combat Cost Tracker'.
- **Evidence:** Overlay.Update checks GameApi.Enabled only once: the first time FileManager exists, matching its own DLL folder against FileManager.Directories[*].DirectoryInfo.FullName and reading IsChecked. If false it logs 'Not enabled in the mod manager; enable Weapon Costs and restart the game.' and stays off for the session.

The 20 Oct 03:09 capture logged that line, recorded in data/combat-cost-capture.json. Every later session reached 'Ready':
- committed 40deeb7f player-prev.log (0.8.6, 4 missions, 'Mission service year fixed' ×4);
- 6d67dcfa, e412fe07, 87b43e03;
- 1bda58a6 (0.8.7);
- the 23 Oct data/install-snapshot/player.log, lines 55 and 131.
The DLL loads from Workshop/3807187341/CombatCosts.dll and LoadOrder.ini has Mod8Directory=3807187341,True.
- **Fix for the author:** Re-check at every mission start rather than once. Log the folder compared. Read usersettings.ini [LoadOrder] as a fallback, as SEST's Policy.PackEnabled does. Use the mod's displayed name in the message.
- **What SEST can do:** Keep the existing PC step that confirms the line is absent. In docs/combat-costs/README.md, record that the 20 Oct line was a first-run artefact: every later session reached Ready.

### Sea Power 0.8.7 changed what feeds _weaponsSpent

*risk*

- **Effect:** The totals now include decoy launches (which also triggers the first bug), every gun round and CIWS burst. In SEST's captured config the Gun row is hidden, because Order omits Gun, Decoy and Other, so the weapon total can greatly exceed the visible rows. If a later update drops the legacy dictionary, startup fails closed with 'Disabled: unsupported API'.
- **Evidence:** In 0.8.7, Taskforce._weaponsSpent is written only by TaskforceWeaponReportExtensions.AddLegacy. It is fed from three calls:
- RecordWeaponLaunch (from WeaponBase.CommonLaunchSettings, skipped for submunitions, for _skipWeaponReportLaunch and for subtype Paratrooper);
- RecordProjectileFired (Projectile.fire, one per round);
- RecordCiwsRoundsFired (WeaponSystemCIWS.OnFixedUpdate, one count per burst).
Record and AddLegacy ignore Fueltank (IsIgnoredAmmo). The primary data is now Taskforce._weaponReport (TaskforceWeaponReport, UnitsByReportId → WeaponReportUnitData with an Ammo dictionary of Launched, ProjectileFired and CiwsRoundsFired). It is also saved as 'WeaponReport' JSON by WriteTaskforceAarData. No 0.8.6 or 0.8.2 DLL is available to diff against.
- **Fix for the author:** Read _weaponReport.BuildTaskforceTotals() (or the per-unit data) when present and fall back to _weaponsSpent. Show Gun by default, or note hidden-category totals.
- **What SEST can do:** In docs, say that hidden categories (Gun, Decoy, Other) still count, and offer to add Gun to [WeaponCategories] Order. Add a new step to integration/runtime-fixes' after-update checklist: diff these weapon-report methods when the game updates.

### Legacy keyboard input inside the guarded update loop

*risk*

- **Effect:** If a game update switches Active Input Handling to 'Input System only', the first mission frame throws InvalidOperationException and the tracker disables itself and its loss hooks, as in the second bug.
- **Evidence:** Update calls UnityEngine.Input.GetKeyDown and GetKey (InputLegacyModule) inside the same try block once a mission is active. The game runs the new Input System; the log reads 'Input System module state changed to: Initialized' and 'Using Windows.Gaming.Input'. Today both input systems are active, otherwise the 20 Oct sessions would have logged a failure.
- **Fix for the author:** Wrap the key check separately, or read the key through the Input System.
- **What SEST can do:** Nothing in data. Add 'F11 toggles the panel' to the PC check after each game update.

### Multi-stage and container weapons can be counted twice

*risk*

- **Effect:** One shot may be charged as booster plus kill vehicle, or pod plus rounds, when both references have prices.
- **Evidence:** CommonLaunchSettings records any WeaponBase launched with isSubmunition = false. Mods that release a second stage or the rounds of a carried pod through Container_Launch, rather than as submunitions, create a second expenditure entry. SEST's load order includes MultiStageMissiles (log line '[MultiStageMissiles] bereit.'). Not verified against that plugin's code.
- **Fix for the author:** Count only the parent round, or document the rule.
- **What SEST can do:** Fire one multi-stage weapon in a test mission and compare the panel with the catalog. If stages are double-counted, give the stage references Category=Ignore in SEST_Combat_Costs and say so in COMPATIBILITY.txt.

### Fragile to game changes: private names, no build check

*risk*

- **Effect:** After a game update the tracker either switches off cleanly or keeps running with changed counting, and nothing tells the player which.
- **Evidence:** Every binding is a reflective lookup of a private or public name, with the type checked. _info.ini says ApproximateVersion=0.8.2. The README says 'gameplay in both builds has not yet been tested'. A binding failure fails closed at startup, which is good, but a change in what a member means passes silently, as the 0.8.7 weapon-report change shows.
- **Fix for the author:** Gate on known game hashes or versions. Log the build. Ship a self-test that compares one known mission against expected counts.
- **What SEST can do:** Treat CombatCosts.dll like the game: keep its SHA-256 (already in data/combat-cost-capture.json). Re-run the bindings check (/tmp/claude-0/-home-user-Seapower-mods/cb2a533c-0bb4-50d5-9069-2002ad35f1f1/scratchpad/ccreview/tools/verify087.py) on every game or tracker update. If SEST code ever reads the tracker, hash-gate that code to this DLL.

### Performance: the panel rebuilds every GUI event

*risk*

- **Effect:** Some garbage-collection churn while the panel is shown; no stutter has been reported.
- **Evidence:** OnGUI rebuilds OverlayContent and OverlayComparison for four sides on every IMGUI event: LINQ, string formatting and GUIStyle.CalcHeight. Snapshot runs by reflection at 2 Hz, and only while visible. MissionEra.Latest opens unit INIs every 0.5 s until the year is fixed after loading.
- **Fix for the author:** Build the lines on the 0.5 s refresh and reuse them in OnGUI.
- **What SEST can do:** None needed. Hide the panel (F11) if frame-time spikes are noticed.

### Land platforms are not priced

*limitation*

- **Effect:** A destroyed SAM site, coastal battery or air base adds nothing, while its missiles fired are charged.
- **Evidence:** README: only vessels, submarines and aircraft are priced. VesselApi.IsVessel accepts only Vessel and Submarine. ObjectType has LandUnit. The weapons that land units fire are still counted, because _weaponsSpent is per taskforce. SEST's cost list marks 27 land units 'not priced: the tracker does not price land platforms'.
- **Fix for the author:** Add landcosts.ini and price destroyed LandUnit registers the same way as hulls.
- **What SEST can do:** Keep documenting it. A SEST plugin computing its own totals could price LandUnit registers from a SEST-owned catalog, shown as a separate, clearly SEST-labelled row.

### Crew, fuel, repairs and damage are not priced

*limitation*

- **Effect:** A crippled but surviving ship costs nothing, and crew losses and sortie fuel are not counted. In a campaign, carried-over damage never appears.
- **Evidence:** README: 'Crew, fuel and repair costs are outside this total.' Only destroyed registers are priced; IsDamaged is ignored.
- **Fix for the author:** Optional damage or repair estimate per IsDamaged register, as a fraction of hull value, shown separately.
- **What SEST can do:** Document it. For a campaign, a SEST layer could add a separately labelled repair estimate from the game's damage records if the owner wants one, but no figure should be invented without a stated method.

### Many torpedoes, bombs, decoys, tanks, sonobuoys and pods have no price

*limitation*

- **Effect:** Totals show '+ ?' and 'incomplete: N× … unpriced'. Only known prices are summed.
- **Evidence:** README: 'Torpedoes and unguided bombs remain incomplete.' The cost list's 'next batch' of stores missing a price: missiles 51, bombs/depth charges 48, torpedoes 50, guns 7, rockets 17, fuel tanks 35, containers 67, chaff 18, noisemakers/decoys 15, sonobuoys 29, other 2.
- **Fix for the author:** Extend the catalogs.
- **What SEST can do:** Continue the research pipeline (mappings.json estimates and reviewed mappings, already gated by costs.estimate_fields). Give the category-only sections from the first bug priority, since they also stop the crash.

### Pooled air-group stores make every carrier and helicopter ship 'incomplete'

*limitation*

- **Effect:** The vessel total of any lost ship with an air group shows '+ ?' permanently, even when every round is priced.
- **Evidence:** Before() sets FlightDeck=true when FlightDeck._currentAmmo is not 0 or any _accountableAmmunition value is not 0. Snapshot adds FlightDeckInventories, and VesselTotals.Incomplete then stays true. The note reads 'air-group stores unavailable'. Launcher and magazine stores in AmmunitionAmountDictionary are still counted.
- **Fix for the author:** Price _accountableAmmunition categories through a per-category catalog. Treat pooled points as a separately labelled estimate.
- **What SEST can do:** Document it; nothing data-side can resolve it.

### Per-mission only: no campaign totals

*limitation*

- **Effect:** When a mission ends its cost totals are lost; there is no running total across a campaign.
- **Evidence:** Overlay.Update clears its caches when the TaskforceManager instance changes. The ledgers are ConditionalWeakTables keyed by Taskforce objects, which are new each mission. Tracker data is written only into mission saves ([Taskforce1], [Taskforce2], [Neutral]). LinearCampaign.SavePersistentDataFromMission writes Mission_<i>, Mission_<i>_TaskForce, Mission_<i>_TaskForceDebrief and Mission_<i>_<tag> records to the campaign state INI with nothing from the tracker. The game's own WeaponsSpent and WeaponReport are not kept in the campaign either.
- **Fix for the author:** At mission end, write a versioned per-mission summary into the campaign state INI and show cumulative totals. Or expose an API so others can.
- **What SEST can do:** Build it in SEST's runtime plugin: capture at mission end, store per mission index, and display. See totals_access.

### Totals are computed only while the panel is visible, and only by side and category

*limitation*

- **Effect:** No unit-by-unit cost view. Hidden-panel sessions log no price gaps.
- **Evidence:** Snapshot runs only when missionActive and visible. Prices, and with them the 'Missing …' log lines, resolve only then. FactionTotals is keyed by side and category. LossLedger.Captured is by vessel or aircraft class (IniRef), not instance. Nothing records per-launcher expenditure.
- **Fix for the author:** Run the snapshot at a low rate even while hidden, at least at mission end. Add a per-unit view from the game's WeaponReport (ReportUnitId, DisplayName, MissionObjectId, CampaignTag).
- **What SEST can do:** SEST code can read Taskforce._weaponReport directly for per-unit expenditure, and UnitStatusRegister or Mission_<i>_<tag> records for per-class or tagged-unit losses.

### Naming, versions and shipped documents are inconsistent

*improvement*

- **Effect:** Confusing messages ('enable Weapon Costs') and broken links to price sources.
- **Evidence:** The plugin id is 'local.seapower.weaponcosts'. The plugin is called 'Weapon Costs', the log prefix is [WeaponCosts], the GameObject is 'Weapon Costs Overlay', the panel says 'COMBAT COSTS' and the Workshop name is 'Combat Cost Tracker'. The README is titled 0.6.0 while the DLL is 0.7.1.0. The README links PRICE-SOURCES.md, AAM-PRICE-UPDATE.md, ECONOMY-SOURCES.md, MISC-SOURCES.md, VESSEL-, AIRCRAFT-, WEAPON- and CIVILIAN-PRICE-*.md and PRICE-GAPS-20260924.md, none of which is in the captured Workshop folder (only README.md, _info.ini and systems/). The AlwaysShow key is dead. config.ini's Order line relies on the game stripping inline '//' comments; IniHandler.commentsSeparators is ';', '//', '#', so it works.
- **Fix for the author:** Use one name, keep the README version in step with the DLL, ship or remove the linked files, and drop AlwaysShow.
- **What SEST can do:** In docs/combat-costs/README.md, map the names ('Weapon Costs' in logs and messages = Combat Cost Tracker). Note the README and DLL version mismatch.

### costs.py reads INI files slightly differently from the game

*improvement*

- **Effect:** None today. A future catalog line like 'WeaponCosts=70000 ; note' would be priced in game but listed as unknown by SEST's cost list.
- **Evidence:** IniHandler.ReadFileToIni cuts each line at the first ';', '//' or '#' and keeps the first value of a repeated key in a section. costs.parse_ini cuts inline text only at '//', skips whole-line ';' and '#', and lets the last repeated key win. A scan of the tracker's three catalogs and SEST's three cost INIs finds no inline ';' or '#' and no repeated keys, so no current output differs. costs.price_status also leaves the category blank where the tracker would derive one, or crash on the null.
- **Fix for the author:** n/a
- **What SEST can do:** Make parse_ini match the game: cut at ';', '//' and '#', first key wins. Model the weapon-category fallback and flag null categories in cost-list.md.

### A public, versioned read API would let other mods integrate safely

*improvement*

- **Effect:** No direct effect. It decides whether campaign and other integrations can be robust.
- **Evidence:** Every type is already public, and Overlay.Api, Overlay.Vessels, GameApi.Snapshot, VesselApi.Snapshot, CostRules, VesselRules and AircraftRules.Resolve are public. Only the result caches (Overlay.rows, vesselRows) and the price-cache methods (GetPrice, GetVesselPrice, GetAircraftPrice), the ledgers, and VesselApi.active are private. There is no event or stable API.
- **Fix for the author:** Add a static entry point, e.g. `CombatCosts.Api.CurrentMissionTotals()`, returning a versioned summary object (sides → categories → count, unpriced, USD; ship, aircraft and air-loss sections; incomplete flags; cost basis). Optionally add an OnMissionEnded event.
- **What SEST can do:** Ask the author for it. Until then use the routes in totals_access.

## Compatibility with 0.8.7

Yes. Every game member the tracker binds or patches exists in 0.8.7 (Seapower-Scripts.dll, SHA-256 eab2297b…, build 0.8.7-261021) with the type the tracker requires. Checked statically with dnfile and dncil by /tmp/claude-0/-home-user-Seapower-mods/cb2a533c-0bb4-50d5-9069-2002ad35f1f1/scratchpad/ccreview/tools/verify087.py.

TYPES (29 of 29 present)
SeaPower.Taskforce, TaskforceManager, FileManager, WeaponsSpent, IniHandler, Utils, Ammunition+Type, Ammunition+Target, Taskforce+TfType, DM, Singleton`1, SearchDirectory, UnitRegister, ObjectBase, ObjectBaseParameters, Ammunition, AmmunitionParameters, SaveLoadManager, ObjectBase+ObjectType, FlightDeck, VehicleTypeOnBoard, FlightDeckTask, PendingLaunchTask, CoolDownTask, LaunchTask, RecoveryTask, Aircraft, Helicopter, SceneCreator.

FIELDS (all public, required types)
- TaskforceManager._taskForces: List<Taskforce>.
- Taskforce._weaponsSpent: Dictionary<string,WeaponsSpent>; Taskforce._unitStatusRegister: List<UnitRegister>.
- WeaponsSpent._number int, _ammoType Ammunition.Type, _targetType Ammunition.Target.
- DM._showDM: bool, static.
- ObjectBase._type and _obp.
- ObjectBaseParameters._objectIniName, _objectIniFolder, _objectVariantReference, _flightDeck.
- FlightDeck._currentAmmo: float, accepted because the tracker allows float or double; FlightDeck._accountableAmmunition: Dictionary<string,int>.
- FlightDeck._vehiclesOnBoard (TrulyObservableCollection<VehicleTypeOnBoard>, assignable to IEnumerable), _flightDeckTasksToAdd and _flightDeckTasksToRemove (List<FlightDeckTask>).
- Ammunition._ap; AmmunitionParameters._type and _targetType.
- VehicleTypeOnBoard._fileName and _objectType; CoolDownTask.iniRef; Aircraft._isInFlight and Helicopter._isInFlight (bool).
- _variantsFolder and _variantsFile are now properties (get__variantsFolder, get__variantsFile). MissionEra.StringReader tries a field and then a property of that name, so they resolve.

PROPERTIES AND METHODS
- Taskforce.Side: TfType. UnitRegister.IniRef, IniFolder, IsDestroyed, ObjectType, Count.
- ObjectBase.AmmunitionAmountDictionary: UniRx.ReactiveDictionary<string,int>. ObjectBase.AmmunitionNameToAmmunitionDictionary: ReactiveDictionary<string,Ammunition>, with an Item(string) indexer returning Ammunition.
- FileManager.Directories: TrulyObservableCollection<SearchDirectory>. SearchDirectory.DirectoryInfo and IsChecked.
- FlightDeck.FlightDeckTasks. VehicleTypeOnBoard.Numbers. FlightDeckTask.VehicleType and Vehicle. PendingLaunchTask.LaunchCount.
- ObjectBase.IsDestroyed. Taskforce.TaskforceObjects (ObservableCollection<ObjectBase>). SceneCreator.IsLoadingDone.
- Singleton<T>.InstanceExists(bool) and get_Instance, static.
- Utils.openVirtualIniFile(string basePath, string fileName, string folderName, bool checkCached) → IniHandler.
- Utils.openIniFile(string rootPath, string name, bool logErrors, bool useCaching) → IniHandler. A new (string,bool,bool) overload exists, but the tracker binds by exact parameter types.
- IniHandler.get_Data. IniHandler.readValue(string sectionName, string key, string defaultValue, bool performLogging) → string, the exact match among about 30 overloads. writeValue(string,string,string).

ENUMS
TfType has Player, Ally, Enemy, Neutral. Ammunition.Type has Missile. Target has AAW, ASuW. ObjectType has Vessel, Submarine, Aircraft, Helicopter.

HARMONY TARGETS (unchanged signatures; static-versus-instance layout as the tracker requires)
- Taskforce.RegisterUnitStatus(bool useTmpList, ObjectBase tfObject, bool destroyed, bool damaged), public instance void.
- SaveLoadManager.WriteTaskforceAarData(IniHandler ini, Taskforce taskforce, string sectionName), private static void.
- SaveLoadManager.LoadTaskforceAarData(IniHandler missionIni, Taskforce taskforce, string sectionName), public static void.

BEHAVIOUR ON 0.8.7, READ FROM THE IL
- setDestroyedFlag still calls RegisterUnitStatus(false, this, true, false) before registering carried aircraft through RegisterNotLaunchedVehicle.
- CalculateEndMissionData uses useTmpList=true, which the tracker correctly ignores.
- A new UnitRegister starts at Count=1, so the tracker's '+1' commit test holds.
- RegisterUnitStatus skips units whose roles include Deco or SeaMine; the tracker then does not commit either, which is consistent.
- WriteMissionToFile saves only Taskforce1 (player), Taskforce2 (enemy) and Neutral.
- HandleCoolDownTask.onExit returns an aircraft to _vehiclesOnBoard only when cooldown ends, so counting cooldown tasks separately is not a double count.
- The material change is the weapon report: _weaponsSpent is now a legacy mirror fed by TaskforceWeaponReportExtensions.AddLegacy. It now includes chaff, noisemaker and MOSS launches and CIWS bursts, and excludes Fueltank (see findings).
- No 0.8.6 or 0.8.2 DLL was available, so nothing could be diffed against earlier builds.

LOG EVIDENCE
- 23 Oct data/install-snapshot/player.log (header '0.8.7-261021'): line 55 '[WeaponCosts] v0.7.1: weapon, vessel, onboard aircraft and save/load capabilities validated; awaiting mod selection.', so every reflective binding resolved at runtime. Line 131 '[WeaponCosts] Ready; F11 toggles the overlay. …', so the enabled check passed, the configuration loaded, and the three Harmony patches applied; a failure there would have logged 'Overlay disabled after a read failure'.
- The same two lines appear in the 22 Oct 0.8.7 capture (commit 1bda58a6, and Player.log in the map-review ZIP).
- Neither 0.8.7 session loaded a mission: the 23 Oct log ends at the main menu. So nothing yet shows in-mission counting, loss capture or save and load on 0.8.7.
- The last in-mission evidence is 0.8.6 on 20 Oct (player-prev.log in commit 40deeb7f): four 'Mission service year fixed' lines (2027, 2027, 2017, 2031) across campaign missions 36 and 37, with no warnings and no 'Missing' lines. So even that session does not prove the panel snapshot ran in combat.
- The 20 Oct 03:09 'not enabled' line is in no committed log. Every later session reached Ready.

## How another mod could read its totals

What exists to read:
- per mission and per side, weapon totals by category (FactionTotals.Categories: category → Count, Unpriced, USD Cost);
- VesselTotals: Hulls by vessel category, Cargo (lost stores by weapon category), Aircraft (on board), AirLosses (Planes or Helicopters), AirCargo, and the Unknown*/FlightDeck counters with Cost, Incomplete, AirLossCost and AirLossIncomplete.
All amounts are decimal USD in the selected cost basis. There is no per-unit breakdown; losses are by class in the ledgers. These are the possible routes, from most to least practical.

1. LIVE, THROUGH THE TRACKER'S PUBLIC MEMBERS (moderately fragile; best fidelity)
- How:
  - From SEST's plugin, get Type.GetType("WeaponCostsMod.Overlay, CombatCosts") and find the component with UnityEngine.Object.FindObjectOfType, or GameObject.Find("Weapon Costs Overlay").
  - Read its public fields Api (GameApi) and Vessels (VesselApi).
  - Call the public methods GameApi.Snapshot(mission, Func<string,string,string,Price>) and VesselApi.Snapshot(mission, vesselPrice, weaponPrice, aircraftPrice), with mission = Singleton<TaskforceManager>.Instance.
  - Build the price delegates from public statics alone: GameApi.Config() and Settings(), then SharedSettings.Apply(cfg, settings, false); VesselApi.Config(), AircraftConfig(), Vessel(ref, folder) and GameApi.Ammo(ref); then CostRules.Resolve, VesselRules.Resolve and AircraftRules.Resolve with CostRules.UseCurrentYearCosts(cfg).
  - This yields the same numbers as the panel, even while it is hidden.
- What it needs:
  - Run it at mission end, while the Taskforce objects are alive: a postfix on SeaPower.LinearCampaign.SavePersistentDataFromMission(), called from MissionDebriefViewModel.ButtonExit_Click and SaveTaskForceMissionState.
  - Check that the tracker is still active. Overlay.enabled is a public Unity property. VesselApi.active, a private static, is null once it has unpatched.
  - Catch the null-category ArgumentNullException (finding 1).
- Fragility:
  - The member names are public, but the assembly is unsigned and changes often: WeaponCosts.dll was renamed CombatCosts.dll in 0.5.1 and versions 0.4 to 0.7.1 came within weeks.
  - Hash-gate this code to CombatCosts.dll 74afa902… the same way SestRuntimeFixes.cs gates the game.
  - Add the bindings to a verifier like verify_native_api.py.
  - It must not patch the tracker; calling its public methods is read-only.

2. LIVE, THROUGH PRIVATE STATE (fragile)
Overlay.rows (List<FactionTotals>) and Overlay.vesselRows (Dictionary<string,VesselTotals>) are private and refresh only while the panel is visible, so they are often stale or empty. The ledgers (VesselApi.ledgers and airLedgers, private ConditionalWeakTable<Taskforce,LossLedger>) are reachable through the private static VesselApi.active. Use these only as a cross-check.

3. THE SAVE SECTION (stable format, but limited in where and when it exists)
- Where: in a mission save, sections [Taskforce1] (player), [Taskforce2] (enemy) and [Neutral].
- The tracker's keys:
  - WeaponCostsLostStoresV1 and WeaponCostsAirLossesV1 (Base64 BinaryWriter; version, FlightDecks, Captured, Ammo, UnknownAircraftInventories, Aircraft, as given in architecture);
  - CombatCostsGDPServiceYear, CombatCostsGDPYearFixed, CombatCostsReferenceYear.
- Beside them, the game's own keys:
  - UnitStatusRegister (JSON of UnitRegister: IniRef, Count, IniFolder, ObjectType, Nation, IsDestroyed, …);
  - WeaponsSpent (JSON);
  - in 0.8.7, WeaponReport (JSON with per-unit Ammo and Launched, ProjectileFired, CiwsRoundsFired).
- Reconstructing the totals means pricing all of this with the same catalogs; costs.py already mirrors ResolveField. That suits an offline Python tool in tools/ or a capture report.
- Limits: it exists only in mission saves (manual or auto), not in the campaign state at mission end, so on its own it cannot give live campaign totals.
- Fragility: low for the tracker's keys (versioned key names plus an in-stream version, and a simple format); medium for the game's JSON keys, which game updates can rename.

4. THE LOG (no use for totals)
'[WeaponCosts]' lines carry no totals: startup and Ready, 'Mission service year fixed', 'Missing WeaponCosts|CurrentYearCost: <ref> (<category>)' (only while visible), 'Missing aircraft price', and warnings and failures. Use them only for health and gap checks: 'Overlay disabled after a read failure', 'Not enabled', 'Disabled: unsupported API'.

5. INDEPENDENT OF THE TRACKER'S CODE (most durable; recommended as the base)
- SEST's plugin reads the game's data at mission end: Taskforce._weaponReport (per launching unit, keyed by ReportUnitId with DisplayName, IniName, MissionObjectId and CampaignTag; fall back to _weaponsSpent) and _unitStatusRegister.
- It prices them with the tracker's catalogs, opened the same way the tracker opens them (Utils.openVirtualIniFile("systems","weaponcosts","weaponcosts",false), and likewise vesselcosts, aircraftcosts and systems/combatcosts/config), applying the precedence and category fallback documented above. The catalogs and that precedence are the tracker's documented and stable interface.
- Lost stores and aircraft on board need the moment of loss. SEST can either take them from the tracker's ledger (routes 1 or 3) or add its own prefix on Taskforce.RegisterUnitStatus, which patches the game, not the tracker, and stays inside SEST's rule.
- This also yields what the tracker cannot: cost per launching unit, and losses for land and on-deck aircraft.
- Fragility: tied to game members, which SEST already re-gates per build, rather than to a third-party DLL.

CUMULATIVE CAMPAIGN COSTS: SUGGESTED SHAPE
- Capture: in a postfix on LinearCampaign.SavePersistentDataFromMission. The mission index comes from LinearCampaignMission._index, which TaskForceDebrief.cs already binds.
- Store: write one record per mission index, e.g. a [SEST_CombatCosts_Mission_<i>] section. Content: per side, the weapon, vessel, air and grand totals, unpriced counts and incomplete flags; the cost basis (IOC or current); the tracker hash and game build. Put it in the campaign state INI returned by SeapowerUI.ViewModels.LinearCampaignTaskForceModeRules.OpenCampaignStateIni(), the handler the game itself saves in that method.
- Keying by mission index means a replay overwrites rather than adds.
- This changes SEST's 'nothing is written to the save' policy. Before relying on it, confirm that the game's IniHandler.saveFile keeps unknown sections. The alternative is a sidecar file under LocalLow keyed by the campaign save.
- Display, which is the user's 'expanded Situation tab' idea: the linear campaign's situation window is SeapowerUI.ViewModels.LinearCampaignEnemyTheaterSituationViewModel.
  - Load() clears Nations, reads OpenCampaignIni() and OpenCampaignStateIni(), and builds Nation(title) → Section(title) → Row(name, detail, status, location, isDestroyed, item, command, isHidden, nation).
  - SummaryText has a setter.
  - A SEST postfix on Load could append a 'Combat costs' tab with Player and Enemy sections: one row per mission (name = mission; detail = USD; status = 'incomplete' or ''), plus a campaign-total row. It could also append the campaign total to SummaryText.
  - Caveats: the window is titled 'Enemy Theater Situation' and its rows expect a nation and status, so this repurposes it. The Row constructor must be exact-bound and hash-gated, as the debrief row is.
- The task-force debrief, which already has a SEST postfix, is a second place to show the mission's own total. Its rows are unit rows and suit money figures less well.

