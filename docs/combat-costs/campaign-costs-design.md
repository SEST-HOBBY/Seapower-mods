# SEST cumulative campaign combat costs: design

Implementation update, 24 October 2026: this is the original proposal, retained as a design record. Current behavior is documented in `README.md` and `integration/runtime-fixes/README.md`. The owner's later request for full integration adds land prices, a live F10 summary, and independent inventory/expenditure capture. The debrief reader still writes nothing, but the capture module writes versioned SEST raw-quantity keys alongside native mission/campaign records. Older uncaptured stores remain unknown. The new code is built and mock-tested; native PC acceptance is pending. Statements below about unimplemented work or never writing saves describe the earlier proposal.

## Summary

- **Approach: price the campaign's own records, store nothing, and never call the tracker's code.** Sea Power 0.8.7 already saves a `[Mission_<i>_TaskForceDebrief]` section for every completed mission. It holds that mission's weapon reports for each side and its kill and loss rows. SEST's runtime plugin reads those sections when the debrief is shown and prices them with the tracker's own price lists, using the tracker's 0.7.1 rules ported into SEST's code. This is a hybrid only in its data: the price lists are the tracker's, and the code is SEST's.
- **It counts:** weapons expended and ships and aircraft lost, for the Player and Enemy sides. Aircraft lost in flight, aboard a lost ship or on deck are all included.
- **It does not count:**
  - stores aboard lost ships and aircraft (only the tracker captures those, and only into mission saves);
  - land units (no price data exists);
  - damage;
  - the Neutral side (its losses are not recorded).
- **Storage and persistence.** Nothing is written. The records are the game's own `Mission_*` sections, so save, load and continue keep them, a new campaign starts empty, and existing 0.8.7 campaigns work retroactively. SEST's "nothing is written to the save" policy stands.
- **Display.** The owner's Situation-window idea works, but there is a better place: the rows of the task-force debrief's Mission Summary.
  - Its rows are label/value pairs by design and have a public constructor.
  - The debrief opens on its own after every completed mission, and the map reopens older ones.
  - It shows this mission and the campaign to date at the natural moment.
  - A "Combat Costs" block in the Situation window is specified as an optional phase 2 behind its own option, default off. Build it only after phase 1 passes on the PC and if the owner still wants a table on the map.
  - The tracker's F11 overlay stays the in-mission display. SEST cannot extend it without patching it.
- **Rules.**
  - Amounts are in USD. Historical (IOC) or current-year pricing follows the tracker's config.
  - An unknown price shows as `+ ?` with counts and is never treated as zero.
  - On any failure the native debrief is left untouched.
- **Size.**
  - one new C# file (about 300 lines) and one option;
  - about 40 mocked assertions plus a precedence table shared with `costs.py`;
  - about 25 entries in `verify_native_api.py`;
  - in-game acceptance checks A1–A13.

---

## 0. A correction to the tracker review

Finding 1 in the review ("a weapon with no category throws ArgumentNullException") is contradicted by the IL. This changes the rule SEST copies.

- `WeaponCostsMod.Price::.ctor` runs `ldstr 'Ignore'; stfld Price::Category`, so every Price starts as `Category = "Ignore"`.
- `CostRules.Resolve` replaces that default only with a valid string:
  - a valid explicit category;
  - one of the fallbacks: ASM, AAM, SAM, ASW, Other, Torpedo, Bomb, Gun or Rocket.
- An invalid category (IL_0038–IL_0073) and a type outside the fallback table (IL_0126 or IL_01b1 `brfalse IL_021b`) both leave `"Ignore"` in place.
- So Chaff, Noisemaker, Sonobuoy, Cluster, MOSS, Paratrooper, Unknown and None rounds with no explicit category are silently excluded. They are not counted, they get no `+ ?`, and nothing throws.
- The real defect is therefore under-counting with no "incomplete" marker, not a crash. Finding 2's mechanism is still real, but its known trigger goes away.
- Separately, the captured `config.ini` has `VisibleOnStart=True`, so the panel is visible by default.

SEST copies this rule (§5) so that its weapons figure equals the panel's. The category-only sections proposed in the review are still worth having: they would move decoys, sonobuoys and pods from silently excluded to counted, shown as `+ ?` until priced, in both the panel and SEST's rows. That trade-off is the owner's call.

## 1. Choosing the approach

| Route | What it gives | What it costs | How it breaks | Verdict |
|---|---|---|---|---|
| **A. Live tracker totals** (call `Overlay.Api` and `.Vessels` Snapshot at mission end) | The panel's exact figures, including stores aboard | A hook at mission end while the mission is still loaded. SEST must then store each mission itself, which means writing to the save. Hash-gate a third-party DLL that was renamed in 0.5.1 and went from 0.4 to 0.7.1 within weeks. It only works if the tracker is enabled, passed its once-only enabled check and has not switched itself off. It cannot cover missions played before installation. | Every tracker update. The tracker's own self-disable. | Rejected |
| **B. Price the game's records independently** | Weapons, ship losses and all aircraft losses for each completed mission, from records the game already saves and reloads | Port about 80 lines of the tracker's price rules (already mirrored in `costs.py`) | Game members, which SEST already re-checks for each build; the catalog format, which is the tracker's documented interface | **Chosen** |
| C. B plus SEST's own capture of stores aboard (a prefix on `Taskforce.RegisterUnitStatus`, written to `[Mission_<i>_Sest…]`) | Adds stores aboard lost units | Repeats the tracker's capture. Changes the save policy. Needs idempotent writes and replay handling. About double the code. | Game members, plus the section naming and persistence rules | Not now. Ask the tracker's author to write per-mission totals into the campaign (a `Mission_<i>_*` section or a `PersistentData` key); reading one versioned key later is small. |

Route B is the smallest correct design.

- It needs no capture and no writes.
- It is retroactive.
- It does not depend on whether the panel was visible.
- It re-prices the whole campaign on one consistent basis whenever prices or the cost mode change.

Its one gap, stores aboard lost units, is stated in the display.

## 2. What is counted

The sources are `[Mission_<i>_TaskForceDebrief]` sections in `LinearCampaignTaskForceModeRules.OpenCampaignStateIni()`.

| Item | Source | Rule |
|---|---|---|
| Weapons expended, Player and Enemy | `PlayerWeaponReport` and `EnemyWeaponReport` through `TryReadWeaponReports`, then `TaskforceWeaponReport.BuildTaskforceTotals()` (keyed by `AmmoRef`, OrdinalIgnoreCase) | Count = `Launched + ProjectileFired`. This equals the tracker's `_number`. CIWS bursts are already inside ProjectileFired, so CiwsRoundsFired is not added. Fuel tanks are already absent (`IsIgnoredAmmo`). Excluded if the weapon category resolves to Ignore (§5). |
| Ships lost | Rows from `KillRows` (Enemy) and `LossRows` (Player), parsed by the game's own `TryParseRegisterRows` | `IsDestroyed` true, `Count > 0`, `ObjectType` Vessel or Submarine. Price × Count. KillRows include damaged rows, so the IsDestroyed filter is required. |
| Aircraft lost (in flight, aboard a lost ship, on deck) | The same rows | `ObjectType` Aircraft or Helicopter, destroyed. Price × Count. Air-group losses come from `UnitRegister(VehicleTypeOnBoard, numbers, …)` with Folder `aircraft` and ObjectType taken from the vehicle type, so they are included. The tracker misses aircraft lost on deck; SEST counts them. |
| Land units and any other type | The same rows | Not priced. No catalog exists. Counted only for the log line. |
| Neutral side | — | Omitted. Its losses are not in the records, so a weapons-only Neutral figure would mislead. |
| Ally and second enemy | — | Not saved by the game. SEST's allied fleet sails in Taskforce1, so it counts as Player. |
| Failed attempts and replays | — | Not counted. The game writes no snapshot for them and keeps the original one for a replay. "Campaign to date" therefore means each completed mission once, exactly as the campaign's own history does. |

## 3. When the data is read

SEST captures nothing. The game writes the records at mission exit: in `SaveDebriefSnapshot`, task-force mode, only for completed missions that are not replays. That happens before the "UnloadMission" step and before `RefreshAfterMissionReturn` opens the debrief.

SEST reads them in a Harmony postfix on `assembly void LinearCampaignTaskForceDebriefViewModel.Load(LinearCampaignMission mission)` (`__instance`, `__0`). It recomputes every time a debrief is opened, whether automatically after a mission or reopened from the map. A campaign of about 20 missions is about 60 JSON parses plus a few hundred catalog lookups, cached within each call.

## 4. Storage and persistence: nothing is stored

- **Save.** `SaveCampaign` keeps every state section accepted by `ShouldPersistCampaignTempSection`. That includes every `Mission_*` section, and sections containing `_TaskForceDebrief` are never treated as projection sections.
- **Load and continue.** `Initialise` copies every `Mission_*` section from the save back into the state ini. Mid-mission saves write the paired campaign save, so they carry the same records.
- **New campaign.** The authored `campaign.ini` has no `[File] Version`, so nothing is copied and the totals start empty.
- **Code rule.** The module never calls `writeValue` or `saveFile` and never changes a dictionary returned by `get_Data`. It reads only.
- **Re-pricing.** Changing `UseCurrentYearCosts` or updating SEST's price lists re-prices past missions too. That is consistent and stated in the docs.

## 5. Pricing rules (a copy of CombatCosts 0.7.1, checked in its IL)

**Catalogs.** Open each catalog the way the tracker does, with `Utils.openVirtualIniFile(basePath, fileName, folderName, checkCached=false)`, which applies every enabled mod's `#!extend`, SEST_Combat_Costs included:

- `("systems","weaponcosts","weaponcosts",false)`
- `("systems","vesselcosts","vesselcosts",false)`
- `("systems","aircraftcosts","aircraftcosts",false)`
- settings: `("systems/combatcosts","config","config",false)`

Read through `get_Data()`, as the tracker does, not through `readValue`, which has a copy fallback the tracker does not use.

**Prices written in the unit's own file.** Read with `Utils.openIniFile(root, "/<ref>.ini", false, true)`, section `[General]`:

| Kind | root | Key in the unit file |
|---|---|---|
| Weapon | `/ammunition` | `WeaponCosts` or `CurrentYearCost`; category `WeaponCostCategory` |
| Ship | `/` + snapshot Folder (`vessels` if blank) | `VesselCosts` |
| Aircraft and helicopter | `/aircraft` (the tracker uses this folder for both) | `AircraftCosts` |

Choose the catalog by ObjectType, not by folder.

**Cost mode.** `UseCurrentYearCosts` and `CurrentYear` come from weaponcosts `[Costs]`, with `config.ini [Costs]` replacing them when that value is present (`SharedSettings.Apply(cfg, settings, false)`; the tracker never passes `true`). Read with `bool.TryParse`; an invalid value means false.

- The field is `WeaponCosts`, `VesselCosts` or `AircraftCosts` when false, and `CurrentYearCost` when true.
- `CurrentYearCost` never falls back to the historical price.
- The basis label is the tracker's own: `IOC`, or the `CurrentYear` value (`current` when blank).

**Which value wins (ResolveField).**

1. `preferList` starts from catalog `[Costs] OverrideInline`.
2. The entry's `OverrideInline` replaces it.
3. The entry's `Override<field>` replaces that.
4. Each step uses `bool.TryParse`; an invalid value keeps the earlier setting.
5. If `preferList` is false the result is the unit's own value, else the list's; if true, the reverse.

Lookup rules:

- Sections and keys match case-insensitively and are trimmed.
- A missing key falls back to the other source.
- A blank key wins and stays unknown.

**ParsePrice.** `decimal.TryParse(v, NumberStyles.AllowDecimalPoint, InvariantCulture)`, accepted only from 0 to 1e15; anything else is unknown. Zero means free and is counted as known.

**Weapon exclusion (the only use of the category).** The category is resolved with field `Category` in the catalog and `WeaponCostCategory` in the unit's file. The weapon is **excluded** when either:

- the category is non-empty and either invalid (whitespace only, more than 20 characters, or a character the tracker's check rejects) or equal to `Ignore` (OrdinalIgnoreCase); or
- the category is empty and `AmmoType.ToString().ToLowerInvariant()` is not `missile` and not one of `asroc, rbu, airdepthcharge, torpedo, bomb, projectile, aerialrocket, mlrs`.

Ships and aircraft are never excluded: the tracker's ship and aircraft rules have no Ignore.

**Totals.**

- Use `decimal` throughout.
- A side's total is the sum of the known prices × counts.
- `unpriced` is the number of counted items whose price is unknown.
- A total is incomplete when `unpriced > 0` or when a record is missing.

## 6. Display

### 6.1 Where: Situation window, debrief or tracker overlay

| Place | For | Against |
|---|---|---|
| **Debrief Mission Summary rows** | Rows are label/value pairs by design. The constructor `LinearCampaignTaskForceDebriefSummaryRow(string label, string value, bool isPositive, bool isNegative)` is public. `Load` calls `Clear()` first, so reopening never duplicates rows. The debrief is shown after every completed mission and reopens per mission from the map, so both "this mission" and "campaign to date" appear at the natural moment. SEST already patches this view model safely. | Not a standing table on the map. |
| Situation window (the owner's idea) | Opened from the map at any time. Good for a campaign-wide table. | It is the enemy order of battle: every block has UNIT/CLASS/STATUS headers, a flag column and destroyed styling. The row constructor is private, with 9 parameters. It needs `NotifyPropertyChanged("HasForces")`. The XAML cannot be checked from the DLL. It is only seen when the player presses Situation. |
| Tracker F11 overlay | Live during a mission | SEST may not patch it. Its own IMGUI overlay would need Unity references, which the plugin deliberately avoids. Its value would exclude the current mission anyway. |

**Recommendation:** build the debrief rows (phase 1). Treat the Situation block (§6.4) as an optional pairing behind `CampaignCombatCostsSituation`, default 0, built only after phase 1 passes A1–A13 and if the owner still wants it.

### 6.2 Debrief rows

The rows are appended after the native ones (Mission Outcome, Completed, Mission Score, Survivors Rescued). They use `isPositive=false, isNegative=false` and the native Title Case. The figures below are examples.

```
Combat Cost: Weapons    Player $412M + ? | Enemy $1.06B
Combat Cost: Losses     Player $1.43B | Enemy $2.04B
Combat Cost: Mission    Player $1.84B + ? | Enemy $3.10B
Combat Cost: Campaign   Player $9.62B + ? | Enemy $14.4B (7 missions)
Combat Cost: Basis      USD, IOC prices; stores aboard and land units excluded
Combat Cost: Unpriced   Mission: 3 rounds | Campaign: 12 rounds, 1 ship
```

- **Weapons and Losses** are this mission's figures; Losses is ships plus aircraft. **Mission** is Weapons + Losses.
- **Campaign** sums every completed mission that has a snapshot, so it shows the same figure whichever debrief is open. `(1 mission)` is singular.
- **Basis** in current mode reads `USD, 2026-08 prices; stores aboard and land units excluded`, using the CurrentYear value.
- **Unpriced** appears only when a `+ ?` is shown. It sums both sides, lists only the non-zero kinds (rounds, ships, aircraft), and adds `weapons not recorded for N missions` when that applies.
- **Weapon report missing for a side:**
  - the key is absent, or it has a value that does not parse: that side's Weapons reads `not recorded`, and Mission and Campaign get `+ ?`;
  - the key is present but blank: this is what the game writes for "fired nothing" (checked in `WriteWeaponReport`), so it reads `$0`.
- **No rows at all** when:
  - `HasDebriefSnapshot` is false;
  - the state ini is null;
  - the tracker's three catalogs lack `[Costs]`, meaning the tracker is not enabled (SEST's extend files have no `[Costs]`).

### 6.3 Number format

- Invariant culture, 3 significant digits, rounded half away from zero.
- Below $1,000: whole dollars (`$950`). Then `K`, `M`, `B`, `T`.
- Rounding that reaches 1000 moves up a unit: 999,999,999 shows as `$1.00B`.
- Examples: `$0`, `$950`, `$4.12M`, `$41.2M`, `$412M`, `$1.84B`, `$2.50T`.

### 6.4 Optional phase 2: the Situation block

- **Hook.** Postfix `public void LinearCampaignEnemyTheaterSituationViewModel.Load()`. It does nothing if no completed mission has a snapshot.
- **Content.** Append `new LinearCampaignEnemyTheaterSituationNation("Combat Costs: Campaign to Date")`. Each row goes in UNIT | CLASS | STATUS order (Name, Detail, Status):
  - **Section "Player"** (and the same for **"Enemy"**):
    - `Weapons expended | 1,284 rounds | $2.31B + ?`
    - `Ships lost | 3 | $4.50B`
    - `Aircraft lost | 11 | $912M`
    - `Total | 7 missions | $7.72B + ?`
  - **Section "Basis"**:
    - `Prices | USD, IOC prices | SEST estimate`
    - `Unpriced | 12 rounds, 1 ship | shown as + ?`
    - `Excluded | stores aboard, land units | `
- **Rows.** Build them with the private constructor `(name, detail, status, location="", isDestroyed=false, item=null, command=null, isHidden=false, nation=null)`. Per the IL review, a null item makes the row's click do nothing and a null nation gets the unknown flag.
- **After adding.** Call the private `NotifyPropertyChanged("HasForces")`.
- **Headers.** Do not relabel them; that would take three more getter postfixes. If UNIT/CLASS/STATUS or the unknown flag read badly on the PC, do not ship phase 2.

## 7. Unknown prices, gaps and failure

- An unknown price is never zero: the item adds to `unpriced` and the total shows `+ ?`.
- A failure for one entry, such as an INI read that throws, is counted as unpriced and logged once.
- **Failure for a whole call.** All rows are built into a local list first and added only when complete. On an exception:
  - nothing is added;
  - the module turns itself off for the session (`active=false`);
  - it logs `campaign combat costs disabled for this session: <type>: <message>`;
  - the native debrief stays as it is.
- **Log lines** (`[SEST Runtime]`):
  - at install: `campaign combat costs installed: debrief rows priced from the Combat Cost Tracker's price lists; nothing written to the save`;
  - at the first Load: `combat costs: tracker price lists found; CombatCosts.dll <sha12> (rules mirrored from 0.7.1 74afa902…)` (a different hash is only noted, not gated), or `combat costs: Combat Cost Tracker price lists not found (is the tracker enabled?); rows not shown`;
  - at each Load: `combat costs mission <i> (<basis>): player weapons <n> +<u>?, losses <n>; enemy …; campaign <m> missions: player <n> +<u>?, enemy …; land units not priced: <k>`, with raw decimals;
  - the first time a reference is unpriced in a session: `combat costs: no <basis> price for weapon <ref>, vessel <ref>, aircraft <ref>`, at most 20 names plus "and N more". This feeds the cost-list research directly.

## 8. Code shape

- **New file `integration/runtime-fixes/CampaignCosts.cs`.**
  - `CampaignCosts`: Bind, Install and Postfix, written like TaskForceDebrief, with Harmony id `io.github.sest-hobby.campaign-combat-costs`.
  - `CostPolicy`: pure static logic over plain dictionaries — `Value`, `Preference`, `ResolveField`, `ParsePrice`, `ValidCategory`, `WeaponExcluded`, `Format`, and the row text.
- **`SestRuntimeFixes.cs`.** Add a third `if (Policy.OptionEnabled(config, "CampaignCombatCosts")) { try { CampaignCosts.Install(game); } catch … "campaign combat costs not installed" }`. The existing game-hash and pack-enabled gates cover it.
- **`sest_runtime.ini`.** Add `CampaignCombatCosts=1`, plus `CampaignCombatCostsSituation=0` only if phase 2 is built. Ship it on, as the existing modules were; changelog claims follow acceptance.
- **Bindings** (exact, all through `Api.Method` and `GetField`/`GetProperty`; a mismatch throws at Install):
  - **Debrief view model:**
    - `Load(LinearCampaignMission)`, the target;
    - property `SummaryRows`;
    - `HasDebriefSnapshot(IniHandler,int)`;
    - private static `GetDebriefSectionName(int)`, used to recognise section names exactly;
    - private static `TryParseRegisterRows(string, ref List<LinearCampaignTaskForceDebriefRegisterSnapshotRow>)`;
    - private static `TryReadWeaponReports(IniHandler,int, ref TWR×3)`;
  - **Snapshot-row fields:** `IniRef`, `Folder`, `ObjectType` (string), `Count` (int), `IsDestroyed` (bool);
  - **Weapon report:** `TaskforceWeaponReport.BuildTaskforceTotals()`, plus `WeaponReportAmmoData.get_AmmoRef`, `get_AmmoType`, `get_Launched` and `get_ProjectileFired`;
  - **Campaign state:** `LinearCampaignTaskForceModeRules.OpenCampaignStateIni()`;
  - **IniHandler:** `get_Data`, `readValue(string,string,string,bool)` and `doesKeyExist(string,string)`;
  - **Utils:** `openVirtualIniFile(string,string,string,bool)` and `openIniFile(string,string,bool,bool)`;
  - **Mission:** `LinearCampaignMission._index`;
  - **Enum checks:** the 9 type names (Missile plus the eight fallback types) exist in `Ammunition+Type`, else throw.
- **Postfix flow.**
  1. Find the state ini and the mission index; return if `HasDebriefSnapshot` is false.
  2. Load the catalogs, or log once and return.
  3. Collect every `get_Data` key equal to `GetDebriefSectionName(i)` for i ≥ 1 that has a snapshot.
  4. Read each one: KillRows/LossRows through the game's parser, and the weapon reports with the raw-value check from §6.2.
  5. Price each mission (§5), building the rows for this mission and for the campaign.
  6. Add the rows in one go and write the log line.
- It must compile under mcs with `-langversion:7` and no Unity, game or Harmony references, as the existing modules do.

## 9. Mocked tests (`tests/RuntimeTests.cs`)

**Additions to the stand-ins.** Keep the existing TaskForceDebrief tests passing.

- **`IniHandler`:**
  - `Data` (get_Data);
  - `readValue(string,string,string,bool)` that reads Data;
  - `doesKeyExist`.
- **`Utils`:**
  - `openVirtualIniFile`, backed by static test catalogs;
  - `openIniFile(string,string,bool,bool)`, plus a decoy `openIniFile(string,bool,bool)` that throws if it is bound.
- **Weapon report:**
  - `Ammunition.Type`, with the real names;
  - `WeaponReportAmmoData`;
  - `TaskforceWeaponReport.BuildTaskforceTotals()`.
- **Campaign state:** `LinearCampaignTaskForceModeRules.OpenCampaignStateIni()`.
- **Snapshot row:** an internal struct `LinearCampaignTaskForceDebriefRegisterSnapshotRow`.
- **Debrief view model:**
  - `SummaryRows`;
  - a `Load` stub that clears the rows and adds the 4 native rows;
  - `HasDebriefSnapshot`;
  - private `GetDebriefSectionName`;
  - private `TryParseRegisterRows`, using the stub's own simple format, since the plugin delegates parsing;
  - private `TryReadWeaponReports`.
- **Summary row:** `LinearCampaignTaskForceDebriefSummaryRow` with a public `(label, value, isPositive, isNegative)` constructor.

**Assertions.**

1. **Which value wins, read from a shared fixture `tests/cost_precedence.tsv`.** The path is passed as argv by `build_plugin.py` and the fixture is added to the manifest inputs. A new `tools/tests/test_cost_parity.py` runs `costs.field_origin` on the same rows. Cases:
   - missing versus blank, at list, entry and field level;
   - `OverrideInline`, both list-wide and per entry;
   - `Override<field>`;
   - an invalid bool keeps the broader setting;
   - `CurrentYearCost` does not fall back.
2. **ParsePrice.**
   - Accepted: `70000`, `70000.5` and `.5`.
   - `0` gives 0, meaning free.
   - Unknown: blank, `7e4`, `-1`, `1,000` and `1000000000000001`.
3. **Exclusion.**
   - Excluded: `Ignore` in any letter case; an invalid category (21 characters, or `SAM!`); no category with type Chaff, Sonobuoy or Cluster.
   - Counted: no category with Missile, Torpedo or Projectile; a blank category with MLRS.
4. **Kill and loss rows.**
   - A damaged kill row is not priced.
   - Destroyed Vessel, Submarine, Aircraft and Helicopter rows are priced × Count.
   - LandUnit is not priced and is counted only for the log.
   - An air-group row with Folder `aircraft` and ObjectType Helicopter is priced from `aircraftcosts`.
5. **Weapons.**
   - Count = Launched + ProjectileFired; CIWS is not added.
   - AmmoRef matches the catalog regardless of letter case.
   - A blank report gives $0.
   - An absent key or unparsable JSON gives `not recorded` plus `+ ?`.
6. **Unknown price.** It gives `+ ?` and an Unpriced row with the right counts; zero is never shown for an unknown price.
7. **Cost mode.**
   - `config.ini` `UseCurrentYearCosts=True` replaces the catalog's value.
   - A missing CurrentYearCost is unknown, never the historical price.
   - The Basis label shows `IOC` or `2026-08`.
8. **Campaign total.**
   - It equals the sum of the mission totals.
   - It is the same from mission 1's and mission 3's debriefs.
   - A section not named by `GetDebriefSectionName`, such as `Mission_3_TaskForceDebrief_Kill_0`, is not read as a mission.
9. **No rows** when there is no snapshot, the state ini is null, or the catalogs lack `[Costs]`; each logs once.
10. **Stability.**
    - Load, then Load again: no duplicates.
    - The native rows keep their order and the 6 rows follow them.
    - The state ini's Data is unchanged after a Load (compared by deep copy).
11. **Failure.**
    - A catalog stub that throws: no rows added, the native rows intact, the module off, and the next Load is a no-op.
    - TaskForceDebrief still works.
12. **Number format.** The cases from §6.3, including the step from 999,999,999 to `$1.00B`.

Update `build_plugin.py` (the fixture argument, the inputs and the validation string with the new assertion count), then run it to update `plugin-build.json`.

## 10. `verify_native_api.py` additions (checked against 0.8.7 with the decoder)

**Constants:**

- `SUMROW = "SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefSummaryRow"`
- `SNAPROW = "SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefRegisterSnapshotRow"`
- `RULES = "SeapowerUI.ViewModels.LinearCampaignTaskForceModeRules"`
- `TWR = "SeaPower.TaskforceWeaponReport"`
- `AMMO = "SeaPower.WeaponReportAmmoData"`

```python
(VM, "Load"): "instance void(class SeaPower.LinearCampaignMission)",
(VM, "get_SummaryRows"): "instance class System.Collections.ObjectModel.ObservableCollection`1<class %s>()" % SUMROW,
(VM, "HasDebriefSnapshot"): "static bool(class SeaPower.IniHandler, int)",
(VM, "GetDebriefSectionName"): "static string(int)",
(VM, "TryParseRegisterRows"): "static bool(string, ref class System.Collections.Generic.List`1<valuetype %s>)" % SNAPROW,
(VM, "TryReadWeaponReports"): "static bool(class SeaPower.IniHandler, int, ref class SeaPower.TaskforceWeaponReport, ref class SeaPower.TaskforceWeaponReport, ref class SeaPower.TaskforceWeaponReport)",
(VM, "ReadRegisterRows"): "instance void(class SeaPower.IniHandler, int, string, class System.Collections.ObjectModel.ObservableCollection`1<class SeapowerUI.ViewModels.LinearCampaignTaskForceDebriefRegisterRow>)",   # literal checks only
(VM, "Clear"): "instance void()",                                                                                        # literal/call checks only
(SUMROW, ".ctor"): "instance void(string, string, bool, bool)",
(RULES, "OpenCampaignStateIni"): "static class SeaPower.IniHandler()",
(TWR, "BuildTaskforceTotals"): "instance class System.Collections.Generic.Dictionary`2<string, class SeaPower.WeaponReportAmmoData>()",
(AMMO, "get_AmmoRef"): "instance string()",
(AMMO, "get_AmmoType"): "instance valuetype SeaPower.Ammunition+Type()",
(AMMO, "get_Launched"): "instance int()",
(AMMO, "get_ProjectileFired"): "instance int()",
(INI, "get_Data"): "instance class System.Collections.Generic.Dictionary`2<string, class System.Collections.Generic.Dictionary`2<string, string>>()",
(INI, "doesKeyExist"): "instance bool(string, string)",
("SeaPower.Utils", "openVirtualIniFile"): "static class SeaPower.IniHandler(string, string, string, bool)",
("SeaPower.Utils", "openIniFile"): "static class SeaPower.IniHandler(string, string, bool, bool)",
```

- **Second `readValue` overload.** `METHODS` is keyed by (type, name), so add an `OVERLOADS` list checked the same way: `(INI, "readValue", "instance string(string, string, string, bool)")`.
- **Parameter names (`PARAMETERS`):**
  - `TryReadWeaponReports`: `campaignStateIni missionIndex playerReport enemyReport neutralReport`
  - `SUMROW .ctor`: `label value isPositive isNegative`
  - `openVirtualIniFile`: `basePath fileName folderName checkCached`
  - `openIniFile`: `rootPath name logErrors useCaching`
- **Fields:** `(SNAPROW,"IniRef"|"Folder"|"ObjectType"): "string"`, `(SNAPROW,"Count"): "int"`, `(SNAPROW,"IsDestroyed"): "bool"`, with exact letter case.
- **Visibility:** `bound[SUMROW,".ctor"].Flags.mdPublic`.
- **Enums:**
  - `Ammunition+Type` contains Missile, ASROC, RBU, AirDepthCharge, Torpedo, Bomb, Projectile, AerialRocket and MLRS;
  - `ObjectBase+ObjectType` contains Vessel, Submarine, Aircraft and Helicopter.
- **New `ldstr` helper `strings(key)`, with these checks:**
  - `GetDebriefSectionName` has `Mission_` and `_TaskForceDebrief`;
  - `ReadRegisterRows` and `WriteRegisterRows` have `Rows`;
  - `Load` and `SaveDebriefSnapshot` have `Kill` and `Loss`;
  - `TryReadWeaponReports` has `PlayerWeaponReport` and `EnemyWeaponReport`.
- **Call order:**
  - `Load` calls `Clear` before its first `get_SummaryRows`;
  - `Clear` calls `Collection.Clear` on SummaryRows;
  - `ReadRegisterRows` calls `TryParseRegisterRows`;
  - `WriteWeaponReport` loads `String::Empty` on the no-rows path, which is what "blank = none fired" depends on;
  - `IsIgnoredAmmo` compares only with 16 (Fueltank).
- **Update** the final message counts.
- **Phase 2 only:** the Situation members listed in the GAME HOOKS input. The private 9-parameter row constructor has the parameter names `name detail status location isDestroyed item openUnitReferenceCommand isHidden nation` and is exempt from the public-constructor assertion. Also `NotifyPropertyChanged "instance void(string)"`.

**After-update checklist, `integration/runtime-fixes/README.md`:**

- Step 5 gains the IL review of `SaveDebriefSnapshot`, `WriteWeaponReport`, `TryReadWeaponReports`, `ReadRegisterRows`, `BuildTaskforceTotals` and `RecordCiwsRoundsFired`.
- A new item for tracker updates: re-read `Price::.ctor`, `CostRules.Resolve`, `ResolveField`, `ParsePrice` and `ValidCategory`, `VesselRules` and `AircraftRules.Resolve`, `SharedSettings.Apply`, and the catalog paths and arguments against 0.7.1. Update `cost_precedence.tsv` and `CostPolicy` together.

## 11. In-game acceptance checks

These go on a new playtest card, `docs/playtests/campaign-combat-costs-<date>.md`.

- **A1. Startup.** `Player.log` has `campaign combat costs installed`, the other two `correction installed` lines and no `inactive` line. At the first debrief it also has the tracker-catalogs-found line with the DLL hash.
- **A2. First mission (new task-force campaign).** Fire missiles and guns, lose one ship that has a helicopter aboard, lose one aircraft in flight, sink one enemy ship, and win. Before exiting, screenshot the F11 panel.
  - The debrief shows the 5 rows, or 6 with Unpriced, without truncation.
  - Weapons for Player and Enemy equals the panel's weapon totals.
  - Losses covers the hull, the helicopter aboard and the aircraft in flight. It is at least the panel's hull figure and lower than the panel's vessel plus air totals by about the stores aboard.
- **A3. Log line.** The log line for that debrief matches the rows.
- **A4. Second mission.** Complete mission 2. The Campaign row equals the sum of the two Mission rows, by the log figures, and shows `(2 missions)`.
- **A5. Older debrief.** Reopen mission 1's debrief from the map: its Mission rows are unchanged and Campaign shows the same total.
- **A6. Save and continue.** Save, quit to the menu, Continue, reopen both debriefs: the figures are identical.
- **A7. Failed attempt.** Lose a mission, then win the retry: it is counted once and the mission count rises by 1.
- **A8. Replay.** Replay a completed mission: the Campaign row is unchanged.
- **A9. New campaign.** The first debrief shows Campaign = Mission and `(1 mission)`.
- **A10. Cost mode (owner-only, local).** Set `UseCurrentYearCosts=True` in the tracker's `config.ini`, restart, and check that Basis reads `2026-08 prices` and every figure changes. Revert afterwards; it is never shipped.
- **A11. Option off.** `CampaignCombatCosts=0` and a restart: no rows, the native debrief intact, and the TaskForceDebrief correction still works.
- **A12. Tracker disabled.** Disable the tracker and restart: the "price lists not found" line, no rows, nothing else broken.
- **A13. Unknown price.** Fire a weapon listed as a gap in `cost-list.md`: `+ ?` and the Unpriced row appear, and the log names the reference. Fire a blank-report case, such as a mission where the enemy fires nothing, then reload: Enemy shows `$0`, not `not recorded`.
- **Phase 2 only.** The Situation window shows the block last, with readable headers and an acceptable flag. It is not duplicated on reopen, and the "no forces" text is gone.

## 12. Docs to update

- **`SEST_RUNTIME_README.txt`:** a new section "CAMPAIGN COMBAT COSTS (CampaignCombatCosts=1)" covering:
  - what is counted and what is excluded;
  - USD and the cost mode;
  - `+ ?`;
  - nothing written;
  - completed missions only.
- **`docs/combat-costs/README.md`:**
  - a cumulative-costs section;
  - the correction to finding 1 (silent exclusion, not a crash);
  - a map of the names ("Weapons Costs" in logs = Combat Cost Tracker).
- **`integration/runtime-fixes/README.md`:** the module, the after-update items (§10) and the open acceptance checks.
- **Change log:** say "seen working" only after A2–A9 pass.

## 13. Still open and not done

- Stores aboard lost ships and aircraft are not counted. Either the tracker's author writes per-mission totals into the campaign, or the larger route C is built.
- Land units, damage and repairs, and the Neutral side are not counted.
- Not checked against the game assets: the debrief and Situation XAML (whether 6 extra rows fit, and the header and flag appearance), and whether a `Key=` blank value survives a save round trip (A13 checks it). A snapshot from before 0.8.7 is not expected to have the weapon keys; if so, that mission shows `not recorded`, which is the intended result, but no such save was available to confirm it.
- Nothing has been compiled or run. This is a design.

**Files read** (repository, read-only):

- `/home/user/Seapower-mods/integration/runtime-fixes/SestRuntimeFixes.cs`
- `/home/user/Seapower-mods/integration/runtime-fixes/Policy.cs`
- `/home/user/Seapower-mods/integration/runtime-fixes/TaskForceDebrief.cs`
- `/home/user/Seapower-mods/integration/runtime-fixes/TerrainClearance.cs`
- `/home/user/Seapower-mods/integration/runtime-fixes/tests/RuntimeTests.cs`
- `/home/user/Seapower-mods/integration/runtime-fixes/build_plugin.py`
- `/home/user/Seapower-mods/integration/runtime-fixes/verify_native_api.py`
- `/home/user/Seapower-mods/integration/runtime-fixes/README.md`
- `/home/user/Seapower-mods/integration/runtime-fixes/SEST_RUNTIME_README.txt`
- `/home/user/Seapower-mods/integration/runtime-fixes/sest_runtime.ini`
- `/home/user/Seapower-mods/integration/common/costs.py`
- `/home/user/Seapower-mods/integration/combat-costs/build_pack.py`
- `/home/user/Seapower-mods/docs/combat-costs/README.md`
- `/home/user/Seapower-mods/tools/tests/test_runtime_plugin.py`

**IL checked** (with the existing dnfile and dncil scripts in `/tmp/claude-0/-home-user-Seapower-mods/cb2a533c-0bb4-50d5-9069-2002ad35f1f1/scratchpad/ccreview/cum/`):

- `/tmp/claude-0/-home-user-Seapower-mods/cb2a533c-0bb4-50d5-9069-2002ad35f1f1/scratchpad/ccreview/out/all.il` (the tracker)
- `/tmp/claude-0/-home-user-Seapower-mods/cb2a533c-0bb4-50d5-9069-2002ad35f1f1/scratchpad/mapreview-20261023/zip/game-reference/Seapower-Scripts.dll` (the game, 0.8.7)
