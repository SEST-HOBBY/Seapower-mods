SEST WORKSHOP UPDATE CANDIDATE — 8 NOVEMBER 2026, R9 TOOLKIT

R9 replaces R8. The 22:23 Brisbane capture confirms the PC ran R8 against
0.8.7-261107 (game SHA256 499675cd...). That game image is unchanged. The
current-mission cost window shows AGR-30 and lost-store prices correctly.
R9 retains Runtime 1.5.5 and UI 1.4.8, and updates the bounded loader.
Canonical stable upload code remains Runtime 1.5.0 and UI 1.4.6.

EXISTING R8 INSTALLATION — QUICK REPAIR

Close Sea Power. Extract this complete R9 ZIP into a fresh folder. Run:

  R9\Repair-Beta-Startup.cmd

This upgrades the five-file candidate with its original journal/backups
retained. It preserves existing campaign/data files, saves and Identify data.
Keep your Steam branch on beta. Test startup, Test Range and missile control,
then select a player unit and use Identify stop/surrender orders on a contact.
After quitting, run R9\Capture-Repair-Results.cmd and attach its ZIP.

WHAT R9 CHANGES

- Missile Control 0.1.18: its steering validator accepts the new native
  far-field max-G load. The author's actual validator/transpiler is checked.
- Test Range 0.2.4: its sensor result hook binds the new fourth argument.
- Optimal Target Distance 1.2.2: all seven shared-launch accesses are grouped,
  including the fourth timer write after failed launch. Its incompatible
  optional AAW interception subfeature remains uninstalled; native target
  rules stay active and the plugin's other features remain available.
- Identify Expanded: three sender-selection player checks exclude unassigned
  objects before the native taskforce getter. This repairs the captured
  stop/surrender broadcast null-reference path.
- Native Windows helper DLLs are excluded before CLR metadata discovery.

FEATURES HELD, DATA RETAINED

The exact captured Exterior Cameras, K5 Kraken contact strike, XQ-58 shadow,
Alpine scoped runtime fixes, MV-75/Cheyenne II systems, EC-2 comms jamming and
MV-75 crew escape images reject this game's contracts. R9 holds them before
CLR load, including both duplicate camera/runtime copies. These are held
features awaiting verified ports, not repaired feature ports. Their data and
models remain installed.

The prior EnhancedDecoyMod, both Topographic Map DLLs and MultiStageMissiles
holds remain. ExtendedGuidance remains off by the SEST profile. Native
countermeasures and missile staging remain. The experimental CombatWorker
and UiWorkerProbe native fallbacks remain; their optimization paths are not
claimed active. Clipped tabs and Global Hawk comparison remain unverified.

FULL PREPARATION / UPLOAD FOLDER

Prepare-PC.cmd imports the reviewed source bundle into a fresh detached
checkout, checks author configuration changes, repairs code, refreshes
backed-up data and builds a separate canonical stable upload folder. Use it
when you need the full preparation repeated. It stops on an author change;
keep the report for review. It never submits to Steam.

The data refresh is still the reviewed 8 November configuration capture:
94 changed/new files, 14 explicit deletions, all 203 dependencies present.
All seven author updates and the preceding November fixes remain integrated.
This later DLL/log capture does not supply newer author configuration files.

GAMEPLAY BEFORE PUBLICATION

Test F11 current/previous/campaign costs and Redback prices; debrief and a
second mission; preparation; Contacts/formation pop-out and return; compass
on unit video; SAR; Osprey launch/conversion/fuel; Test Range; missile control;
and Identify stop/surrender broadcasts. Managed tests do not launch Unity or
verify Noesis rendering, inputs, second-monitor behavior or flight.

Stable UI 1.4.6 also needs a stable Build 261021 tester for F11/pop-out/compass
rendering. You can keep your PC on beta. This toolkit does not claim that
those stable UI checks or R9 gameplay have passed.

After checks pass, update existing Workshop item 3812461539 using ONLY the
inner SEST_Integration folder printed under UPLOAD FOLDER. Use the prepared
canonical stable folder. STEAM-CHANGE-NOTE.txt retains the data-update note;
private beta-only feature holds and adapters are documented here and in R9.

Keep the printed backup paths. Restore data before restoring earlier code
if reverting both. The existing candidate's original restore journal and
Identify data remain retained.

Required Items and collection 3812390790 must match the 203 dependency IDs
in data/load-order.tokens.txt. Item and collection links:
https://steamcommunity.com/sharedfiles/filedetails/?id=3812461539
https://steamcommunity.com/sharedfiles/filedetails/?id=3812390790
