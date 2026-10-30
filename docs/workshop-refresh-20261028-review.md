# Workshop refresh, 28 October 2026: the public beta

One capture on the PC, `f590fb8c` ("chore: capture workshop refresh
2026-10-28") on `chore/workshop-refresh-20261028`, taken at `3421284b` and
carried here as `16deca0f` on top of `7e86df43`, the deploy head (the same
patch, 1,347 files). That day the PC had switched Sea Power to the public
beta: 0.8.7 Build 261021 became 0.8.7 Build 261026, **the same version
number** (`data/install-snapshot/changelog.live.txt:6`; Steam build 26103404
-> 26223125, `game-build.txt`). The exporter lists 26 mods as updated by
their authors: **17 changed** and **9 are unchanged** since the 25 Oct 2026
export. **Four subscriptions are new** (Contact Log, B-21 Raider, Sea Power
Topographic Map and Sea Power Pop-Out Windows), and **1,032 game files
changed** (1,031 modified, one added).

The facts are in `data/install-snapshot/workshop-refresh-summary.txt`
(regenerated here); this is the judgement. Four readers took the capture
(the PC and its logs, the game's own files, the mods, and the build), and a
second reader re-checked each one in a scratch worktree. What a re-check
refuted is left out; where it corrected a claim, the correction is used.

Three things stand out. On the beta **no code mod loaded**, SEST's three
plugins included: the Anchor Chain preloader found no chainloader (section
1). The **from-scratch build** on this export stops in two builders, SEST
Collection Fixes and SEST Allied Fixes, both on author updates, and four
more fail after them (section 5). And the **inventory gate** fails on the
four new subscriptions. The owner decided on 30 Oct 2026 (section 4): the
pack keeps targeting the stable Build 261021, the next integration restores
the game files to the 261021 export, and the beta work goes to a beta branch
for the 11 Nov 2026 release.

## 1. SEST in the logged sessions

Four Player logs are in hand: two in this capture and two in the owner's
`pc-snapshot-20261028.zip` ("the 26 Oct zip" below), which holds the PC
clone's `data/install-snapshot` as `capture-context.ps1 -Redact` left it at
09:45 on 26 Oct 2026 (its `environment.txt`: `a3c42251f` on
`sest-dev/jolly-ride-rptj4t`). Times are the PC's (Brisbane). Line numbers
are the files' own, header included.

| Session | Log | Build | SEST | What it shows | End |
|---|---|---|---|---|---|
| 28 Oct 2026, from 22:40 | `player.log` (73 lines), `bepinex.log` (18) | 261026, the beta | the Workshop copy; no plugin loaded | "Could not find AnchorChain chainloader" (`bepinex.log:18`); all 204 subscribed items installed (`player.log:48`); the menu only | normal (`player.log:71-76`) |
| 27 or 28 Oct 2026, before the 22:38 downloads on 28 Oct | `player-prev.log` (906 lines) | 261021 | the Workshop copy (44-45): UI Follow-up 1.4.2 (30-42), Runtime 1.5.0 (46-54), bridges to Group Manager 0.2.17, Pop-Out Windows 1.0.1 and Contact Log 1.0.1 (257-259) | a Sulu Line mission (`PN_FFG-150` at 305), loaded twice (318, 780); Contacts moved to the Pop-Out monitor (821) | normal (904-909) |
| 27 Oct 2026, before 12:41 | not in hand | 261021 | the Workshop copy: Runtime 1.5.0, UI Follow-up 1.4.2 | the crash GPT recorded | crash, by GPT's record |
| 26 Oct 2026, before 09:45 | zip `player-prev.log` (4,642 lines) | 261021 | the local `SEST_Integration`, Runtime 1.2.0 (38) | the tracker ready (138); the Southern Watch campaign map (1981); SW05 Weapons Free's briefing map (2349); a Task Force debrief with Runtime's cost line (3032) | normal |
| 26 Oct 2026, the next session | zip `player.log` (757 lines), zip `bepinex.log` | 261021 | the local pack, switched off: "[SEST Runtime] inactive: owning pack is not enabled in usersettings.ini" (33) | Contact Log 1.0.1, Topographic Map 1.2.0 and Pop-Out Windows 1.0.1 load for the first time (`bepinex.log:87-89`) | normal |

**The beta session.** BepInEx 5.4.23.2 started, found one plugin and loaded
`AnchorChain Preloader 1.0.0`. The preloader logged "AnchorChain Preloader
started!" and then "Could not find AnchorChain chainloader"
(`bepinex.log:17-18`), and BepInEx finished (19). No "Loaded assembly" line
follows. So no mod DLL ran: not Anchor Chain, not any mod it loads, and not
SEST's Runtime, UI Follow-up or menu plugin. `player.log` has no plugin line
at all. The game saw all 204 subscribed items installed, Anchor Chain
(3380210757) and the pack (3812461539) among them (line 48). Data mods do
load: the menu read the Anchorchain Expansion Pack's `kinetic_kill_hit_pac3`
effect material (67-68). The session stayed in the menu and shut down
normally.

**Why the preloader found nothing.** Its files did not change. The preloader
(`BepInEx\plugins\AnchorChain.Preloader.dll`, 7,168 bytes, `1ee1570f`,
1.0.0), the chainloader (`3380210757\AnchorChain.dll`, 17,920 bytes,
`e2728110`, 1.1.0), BepInEx and `winhttp.dll` hash the same on 25, 26 and 28
Oct (`plugin-dlls.txt`). The game changed. The preloader's code (the same
file, `1ee1570f`, came in the owner's 23 Oct diagnostics zip,
`data/map-capture-review-20261023.json`) reads the game's
`FileManager.Instance.Directories`, searches each folder for
`AnchorChain.dll`, and logs "Could not find AnchorChain chainloader" only
when that search ends with no match. An error during the search would have
shown as a BepInEx plugin-load error, and one while loading the DLL as
"Failed to initialize AnchorChain with error". In Build 261021's code the
list is filled the first time it is read (`FileManager.get_Directories`),
which logs "FileManager.Directories contains Mods". Every 261021 session
logs that line twice just before the first plugin line (28 Oct
`player-prev.log:28-29`, first plugin line 30): the preloader's read filled
it. On the beta the first such line is `player.log:49`, after the build
banner (45) and the subscribed-items line (48), with none before. So on
Build 261026 the list holds no folder with `AnchorChain.dll` in it when
BepInEx loads plugins. Whether it is empty at that moment or filled
differently, only the beta's `Seapower-Scripts.dll` can tell; the change
log's "file layers allow mods and user files to selectively overwrite game
files" (line 57) is a candidate. SEST cannot fix this in the pack.

**The 261021 session before it** ran SEST as designed. Every SEST module
installed from the Workshop copy (`player-prev.log:30-54`): UI Follow-up
1.4.2's input, pop-out, formation, performance and cost-cache parts,
TileGuard, the backdrops and menu film, and Runtime 1.5.0's towed-sensor,
MST terrain, debrief, preparation-map, combat-cost and F11 parts. It played
a Sulu Line mission (the Philippine Navy's `PN_FFG-150` loads at line 305;
the 27 Oct saves `sulu test` and `sulu test 2` are Sulu Line saves too,
`campaign-saves.txt`), moved Contacts to the Pop-Out monitor and shut down
normally. It is not the crashed session. It ran Pop-Out 1.0.1 (line 258), so
it came before the 28 Oct 22:38 downloads of Pop-Out 1.0.2 and Topographic
Map 1.3.1, and it ran UI Follow-up 1.4.2, written on 27 Oct 2026 at 09:26
(`plugin-dlls.txt:61`). By GPT's record of the crash (below) it came after
13:18 on 27 Oct 2026.

**What the 26 Oct zip adds.** Two 261021 sessions from before 09:45 on 26
Oct 2026, on the local `SEST_Integration` (4,300 files, zip
`streaming-assets.txt:8`) with Runtime 1.2.0 (`41ff20d9`, zip
`plugin-dlls.txt:96`). The first played Southern Watch and reached a Task
Force debrief carrying Runtime's cost line ("combat costs mission 14
(reference-year): Player $22.0M | Enemy $5.27B; campaign 8: Player $37.9M |
Enemy $5.96B + ?", zip `player-prev.log:3032`). The second ran with the pack
switched off in the Mod Manager: Runtime stood down as designed (zip
`player.log:33`) while the menu plugin ran (30-32). It is the first sight of
Contact Log, Topographic Map and Pop-Out Windows loading.

**The crash is in no log.** All four Player logs end with the normal Input
System shutdown, and none has a stack trace, a crash line or an access
violation. The only account is GPT's (`crash-followup-1318.json` in the 27
Oct handoff, not verified here). It says the crash session's `Player.log`
(3,358,551 bytes) is in `SEST-crash-review-20261027-131824-34062f.zip` in
the owner's Downloads, was unchanged between GPT's 12:41 and 13:18 captures,
and ends after Contacts went out to the Pop-Out monitor, back, and out
again, with no fault stack. The only Windows Application Errors it found
were four `0xc0000005` on 26 Oct 2026, 14:39-14:42, before the upload. The
later session above made the same move and ended normally: one data point,
which neither reproduces the crash nor rules it out.

**The pack on the PC.** The PC runs SEST from its Workshop copy: 3812461539
is first in the live order (`load-order.live.txt`, 206 entries) and there is
no local `SEST_Integration` (`streaming-assets.txt:11`). Steam records the
item's upload at 20:11 on 26 Oct 2026, downloaded by 20:42
(`workshop-subscriptions.txt:199`). The copy's `SEST.RuntimeFixes.dll` is
1.5.0 (`7ba6d6d9`, 128,000 bytes) and its `SEST.MenuBackground.dll` is
`9dfd561d`, both written at 20:41 that day, the download.
`SEST.ContactsFix.dll` (UI Follow-up 1.4.2, `51b56f5e`) was written on 27
Oct 2026 at 09:26, after it (`plugin-dlls.txt:61-63`). The repository's
record says the item carries `b1449201`'s build
(`docs/campaigns/southern-watch/publishing.md:13-14`), whose Runtime is
1.2.0 (`41ff20d9`), and at 09:45 that morning the PC's local
`SEST_Integration` still had 1.2.0 (zip `plugin-dlls.txt:96`). So Runtime
1.5.0 went up with the 26 Oct upload, unless a hand copy kept a 20:41 file
time, which is unlikely. Section 4, item 4, asks for the listing that
settles it. No capture before this one saw the item: the PC was not
subscribed to it on 25 or 26 Oct 2026.

The live order's extras beyond the canonical 199 and the pack
(`load-order.live.txt:13-15, 209-211`): Contact Log, Topographic Map and
Pop-Out Windows placed by hand at 8-10, between Group Manager and Combat
Cost Tracker; `ACConfigs` (off) at 204, Anchor Chain's own config folder;
`IdentifyExpanded` (on) at 205, the folder Identify Expanded looks in for
its localisation file (26 Oct zip `player.problems.txt:5`); and at 206 the
B-21. Both folders are empty (`streaming-assets.txt:5, 7`). The shared
entries are in canonical order (`check_load_order`).

The capture's `player.problems.txt` is the 25 Oct file, unchanged, and says
nothing about the beta session: `tools/capture-context.ps1:270-276` writes
it only when the log has a matching line, and the 73-line beta log had none.

## 2. The game update

**What the beta changed.** Build 261026's change log
(`changelog.live.txt:6-73`) lists, among much else: a Lambert Conformal
Conic map with a play area, "existing missions are migrated automatically"
(54); multiple sides with relations (55, 58); "file layers allow mods and
user files to selectively overwrite game files, also per mission" (57);
"Weapons can now fail at launch" (71) and reworked launch, seeker and
warhead reliability, pitch rates, armour and bombing values (41); a CIWS
rebalance (42) and "CIWS used flat hit rolls instead of its ballistics"
(12); NoesisGUI 4.0.1 (51); Task Force Air Ops, campaign airbases and
campaign settings (67-69); "populated Soviet OODA systems" (40); helicopter
code that "ran at twice the intended speed" (14); and aircraft groups that
now default to Follow Leader (21). The 1,032 game files carry the data side
of this. `tools/check_game_version.py` reads "0.8.7 Build #261026" and asks
for nothing: every pack declares 0.8.7, and the version did not change.

**What the decision means.** The owner keeps the pack on Build 261021
(section 4, item 6). The next integration restores the 261021 game files,
and everything below that depends on the beta goes to the beta branch
(section 5 lists it). The beta still matters now for two groups: the owner's
PC, which is on it, and any subscriber who opts in.

**Anchor Chain on the beta.** Without the chainloader no mod code runs
(section 1). On the beta that means: no SEST Runtime (no Tomahawk MST
terrain clearance, no lost hulls added to Task Force debriefs, no campaign
combat costs or F11 windows, no preparation map, no towed-sonar guard, no
pop-out bridges); no UI Follow-up; no menu film or backdrops; no Dynamic
Campaign Mod, which runs both World Sandbox worlds; no Combat Cost Tracker;
and the other mods' code is off, with the effects the 22 Oct review recorded
for the Fury, the K5, the Corsair, the EC-2, the MV-75 and the YF-23 (its
section 1). SETUP does not notice. It checks only that a file named
`*AnchorChain*` exists under `BepInEx`, and prints "[ok] Anchor Chain
preloader already installed"
(`integration/campaign/setup/sest-setup.ps1:528-530`). Whether `#!extend`
files still apply without Anchor Chain is not settled: the Cross-Deck
builder reads Build 261021's own `IniHandler` as applying them
(`integration/cross-deck/build_pack.py:44-48`), while Collection Fixes'
notes say only the preloader reads `ammunition_overwrite/`
(`integration/collection-fixes/build_patch.py:143-146`).

**The plugin pins.** Even once Anchor Chain loads on the beta, SEST's code
stays off. Runtime 1.5.0 runs only on Build 261021's `Seapower-Scripts.dll`
(`eab2297b`); on any other it logs "inactive: uninspected native assembly"
and installs nothing. Its second pin, NoesisGUI `c4e2c37c`, gates only the
native cost windows, and the beta moved NoesisGUI to 4.0.1. UI Follow-up
1.4.2 checks both hashes at its entry point and turns off whole
(`integration/ui-followup/source/ContactsFix.cs:19-24, 52-59`). The runtime
README already says 1.5.0 goes inactive after the next game update and
cannot be re-gated without its source
(`integration/runtime-fixes/README.md`, lines 137-139 and 248-253). The menu
plugin has no hash gate and would run.

Two mod updates of 28 Oct 2026 break pins on Build 261021 too, for every
player who has them. Pop-Out Windows 1.0.2 (`2c6bc876`) is not the 1.0.1
build both plugins pin (`d0027215`, `ContactsSurfaceFix.cs:15`). Runtime
1.5.0 then logs "pop-out bridge inactive for an uninspected Pop-Out DLL" (a
string in the DLL) and keeps its other parts, F11 windows included. UI
Follow-up turns off its Contacts pop-out surface fix, camera compass and
Formation UI mode control (`ContactsSurfaceFix.cs:28`,
`CameraCompass.cs:51`, `FormationUiMode.cs:99`) and keeps the rest.
Topographic Map 1.3.1 (`fd514064`) misses only a diagnostic timing hook
(`DiagnosticModules.cs:15`). Contact Log 1.0.1 (`a1b8b450`) and Group
Manager 0.2.17 (`6230e8e7`) match. No log shows these lines yet: the last
261021 session ran Pop-Out 1.0.1.

**The weapons rework and the CIWS ladder.** The beta's `systems/weapons.ini`
moves the CIWS calibration: Phalanx Block 0 (`[MK15]`) anchor 40 -> 65,
volley 500 -> 250 rounds, cooldown 3 -> 10 s; Block 1 (`[MK15_Blk1]`) 50 ->
70, 1,000 -> 375, 6 -> 10 s; AK-630 20 -> 40, 1,000 -> 400, 5 -> 30 s,
volley range 2,000 -> 1,600; AK-230 10 -> 20. It adds `[Oerlikon_30mm_KCB]`,
`[Roland]` and `[GWS-30_Mod0]`. The change log says "one Phalanx is now
roughly equal to two AK-630" (42). SEST's `CIWS_RETUNE` puts eleven Workshop
mounts on the old ladder ("Phalanx Block 0 anchor 40, Block 1 (APDS) 50,
AK-630 20, AK-230 10",
`integration/collection-fixes/build_patch.py:1562-1564`, table from 1573).
On the beta's ladder SEST's Phalanx 1B (`MK15C`, anchor 55, 26 hull files in
the dist) and 1A (`MK15B`, 50, 15 files) sit below vanilla's Block 0, and
SEST's AK-630M (`rfn_ak630m`, 25, 6 files) below vanilla's AK-630. Seven of
the eleven fire 1,000-round volleys and the Type 730 fires 700, against the
beta's 250 to 400, with 3-6 s pauses against 10-30 s. On the pack as built
today most of that does not show: Collection Fixes restores Build 261021's
`[MK15]`, `[AK630]` and `[AK230]` over four aircraft mods' stale copies of
the file (`SEST_Collection_Fixes/systems/weapons.ini:237, 258, 630`), so a
beta player gets the 261021 figures on every vanilla Block 0, AK-630 and
AK-230 mount (13, 21 and 1 hull files). One inversion is live: `[MK15_Blk1]`
is in none of the stale copies, so on the beta it reads 70 on the 6 SEST
hull files that mount it, above SEST's Block 1B at 55. The restored
sections' headers still say "the game's 0.8.3 definition"
(`build_patch.py:1898`). Elsewhere: 37 rounds change reliability
(`LaunchReliability` added on 29, changed on 7), 17 missiles gain or raise
`Armor`, 13 lose `MissileEvasiveness`, and 41 aircraft change
`MaxPitchRate`. The Southern Reach test card quotes the old Block 1 volley
("1000 rounds, 6 s cooldown",
`docs/campaigns/southern-reach/test-card.md:224`). All of this waits for the
beta branch (section 4, item 6).

**LaunchReliability.** Rounds can now fail at launch, and the weapon report
lists failures (changelog 38, 71). The game writes the key as a fraction:
`LaunchReliability=0.98`, "Chance that engine will start when launching from
aircraft" (`original/ammunition/usn_agm-84d.ini:105`). SEST's AIM-424 writes
99 (`integration/common/aim424.py:189`), and the Workshop Harpoon copies
SEST Replenishment ships write 98 and 97, with their authors' comment
"(0...100)" (`SEST_Replenishment/ammunition/usn_agm-84d.ini:99`,
`usn_rgm-84d.ini:103`). How the beta reads a value above 1 is unknown
without its assembly; so is whether an ejected dud counts as expended in the
saved weapon report the cost debrief reads.

**The tactical-map settings file.** SEST TacMap Colors ships the whole
`ui/Default/Settings_UI_Tactical.ini` (170 lines in the committed pack; the
beta's file has 202). The beta adds 32 keys. 21 of them (`InvisibleColor`,
the two `WeaponNoEscapeRange` colours, the nine `DrawingPreset` colours and
their night forms) Build 261021's own code already reads
(`UI_Parameters.TacticalUI_ReadUIParameters` in its `Seapower-Scripts.dll`),
with defaults equal to the beta file's values, and 261021's file lacked them
too, so their absence changes nothing. The 11 new to the game (the play-area
fill and stroke colours and stroke thickness, the firing-arc and
seeker-hidden colours, the drawing polygon fill and erase highlight, and the
seeker-cone, jam-cone and weapon-wire thicknesses) cannot be checked without
the beta's assembly. 261021's reader falls back to a code default for any
missing tactical colour or thickness, so a default, not a missing drawing,
is the likely outcome. A rebuild on the beta's files carries all 32 (the
from-scratch build below wrote it). Beta branch.

**The campaign and mission file keys.** The stock campaign
(`campaigns/pacific-strike-task-force/campaign.ini`) gains
`CampaignMapUI=Standard`, `EnableMultipleTaskForces=False`, and a
`TaskForceModeAirbaseSection` on all five of its airbase-preparation
missions. The beta's `language_en/ui.ini:3792` has a new error, "The
mission's configured staging airbase is not a player airfield. Check
TaskForceModeAirbaseSection in the campaign settings." SEST's campaigns
offer airbase preparation on 39 windows (Southern Watch 9, Southern Reach
21, Red Line 2, Sulu Line 7) and the builder writes none of the three keys
(`integration/campaign/build_pack.py:7343-7345`). Whether the beta needs the
section key or has a fallback is unknown without its assembly. The builder
already finds the player airfield it would name (7336-7341). Beta branch.

**The LCC and GeoPosition forms.** The beta re-saved one stock mission,
`missions/PLAN/PLAN 01 Clash in the Paracels.ini`: eight `Lambert*` keys in
`[Environment]` (the play area); all 20 `RelativePositionInNM` lines gone
and 21 `GeoPosition=lat,lon,alt` lines in their place, one for a new
airfield at Lingshui; waypoints as `geo,lat,lon,alt`; `[Sides]` and
`[Relations]`; formation strings with a control mode (`FollowLeader`). The
game's own new `missions/Demo/AircraftEditorMission.ini` still writes
`RelativePositionInKm` (line 41). No mission file in the pack writes
`GeoPosition`, and none has been loaded on the beta. Two SEST readers miss
the new form: the campaign builder's proven-position pool reads
`RelativePositionInNM` only (`build_pack.py:1031`), so PLAN 01's positions
drop out of it; and `tools/audit_beta_map_geometry.py` counts `geo,`
waypoints as malformed and does not know the `Lambert*` keys as a play area.
Air groups without an explicit control mode now default to Follow Leader
(changelog 21), so SEST's air formations, written without one, will follow
their leaders on the beta. Beta branch.

**The new Volume and MinTakeoffDistance keys.** The beta adds
`[General] Volume` to every unit type (423 ammunition, 254 vessel, 187
land-unit, 113 aircraft and 3 whale files) and `MinTakeoffDistance` to all
113 aircraft, with no comment saying what either does. Of this export's mod
changes, only Modern US Navy's adds `Volume` (14 hulls and its SSQ-62). What
the game does with a unit that lacks the keys is unknown without its
assembly. A rebuild on the beta's files would copy them into SEST's verbatim
and forked game units (Replenishment's 37 game-file rebases, Collection
Fixes' `usn_gbu-24`, the Redback 19-tube pod's `Volume=0.2027`); with the
261021 files restored (section 4, item 6) none of that ships.

**controls.ini.** One binding changed, `QuickLoad=F9` to `LeftControl+F9`
(`mods-source/_vanilla/user/controls.ini:19`), and it is SEST's own: UI
Follow-up 1.4.2 moves Quick Load, the game's default
(`original/controls.ini:97`) still says F9, and FEATURES and the Workshop
listing say Options > Accept keeps Ctrl+F9 after the plugin is gone
(`docs/FEATURES.md:573-575`,
`docs/campaigns/southern-watch/workshop-listing.md:133`). It stays on the
beta, where no plugin loads.

**The rest.** Reaction times are shorter (`systems/sensors.ini`
`[TargetAquisitionTime]`: VerySlow 80 -> 55 s, Slow 50 -> 35, Medium 30 ->
20, Fast 15 -> 10, VeryFast 7 -> 5), and the Soviet profiles are re-rated
(More_U and Titanit to datalink tier 4). SEST's OODA profiles use the same
labels, so they speed up with the game's, but the "one datalink tier below
NATO" reasoning in `integration/common/combat.py:50-55` no longer holds
against More_U and Titanit; Red Line's pacing needs a look in beta play.
`config.ini` ships developer settings (`Mission=WIP/Martin tests/lcc`,
`Mission=LCC3Test`, `[Scripting] Debugging=true`); nothing in SEST reads it.
Nothing the cost tooling reads changed: no `Type` value changed, and no unit
or round file was added, removed or renamed. The IRIAF AH-1J's new AntiShip
fit hangs `usn_agm-65b`, already priced
(`docs/combat-costs/cost-list.csv:1333, 3280`).

## 3. The mod updates

All 30 items were read file by file, key by key, against the load order
(`data/load-order.tokens.txt`) and every SEST mission, roster, World Sandbox
list and builder that names an id. "Fork" means a SEST pack ships its own
copy of the file. Each rebuild named here ran in a scratch worktree.

| Mod | What changed (7e86df43 -> 16deca0f) | What it does to SEST | Next |
|---|---|---|---|
| Flight Deck Ops (3373960386), 11 files | The nine stock carrier and cruiser decks it overrides are reworked. Each US carrier goes from 155 to 137 launch points and loses 38 to 44 taxi paths. The Tarawa goes from 58 to 47 launch points, 105 to 60 taxi paths and 14 to 12 recovery points; the Kiev's taxi paths go from 35 to 16 and the Orel's recovery points from 6 to 4. The Forrestal's ten `usn_sh-3h` become ten `usaf_hh-3`. | SEST forks none of these hulls. D2 Flight Deck Day (`usn_cvn_nimitz`) and D7 Before the Lifeline (`usn_cv_kitty_hawk`) sail the new decks as the author ships them; not seen in game. | Catalog note; D2 and D7 deck operations on the play-test card. |
| Euromod - Modern US Navy (3390330875), v626, 65 files | 45 hulls gain a combat system. 40 of them restate what Euromod Main's `#!extend` files already set; new are the three Bunker Hill VLS fits and the early Wasp, and the Arleigh concept now says AEGIS_BL5 where Euromod Main's extend says AEGIS_Mk7. The late Wasp's `[CombatSystem1]` has no `[CombatSystems]` count header. Eight late Burkes carry ESSM Block 2 (`usn_rim-162h`). Both Wasps hold 135,000 flight-deck ammunition points (were 85,000 and 45,000). 14 hulls and the SSQ-62 take the beta's `Volume` key. A copy of the late Wasp sits at the mod's root. | SEST Replenishment's 22 forks of these hulls rebase on the rebuild: `check_pack_fidelity` flags them on the committed pack and passes after. The Nimitz 2025 repairs in `integration/common/ras.py` still match. | Rebuild; catalog note. |
| Euromod - Modern Italian Navy (3488139470), 4 files | New material paths on the FREMM, FREMM ASW and PPX; version counter 51 -> 53. No stat changed. | Replenishment's two FREMM forks rebase. | Rebuild; note. |
| French Helicopter Package (3567228449), 1 file | A typo in the VSR 700's wing-fold animation. | None. | One-line note. |
| Charles De Gaulle & Modern French Navy (3567256221), 38 files | New Floréal-class frigate (`fr_ffg_floréal`, 3,800 t, six variants, a deck for the Panther and the Aliaca) and Aliaca mini-UAV (`fr_aliaca`, 13 kg, Role=Recon). The sensor `[EOMS-NG]` is renamed `[EOMS_NG]`; EOMS, EOMS_100, EO/IR, AIS and DRBV_21 are added. | Both Charles de Gaulle hulls still mount `EOMS-NG`, now defined nowhere (below). Cross-Deck gains a Floréal stub, the first non-ASCII file name in the dist. The World Sandbox values the Floréal at 130 and the Aliaca at 28; Combat Costs prices them at $700M (frigate proxy) and $75M (fighter proxy). | `MISSING_SENSORS` entry (tested); price the Aliaca as a small UAV; note. |
| Spanish Navy Mod (Cold War) (3630495619), 23 files | New S-55 helicopter (`spa_s-55`: ASWKiller and ASWHunter fits, an AQS-4 dipping sonar). The Dedalo's variant embarks four (`spa_S-55=Squadron1,4`) and its Sea Kings drop from 8 to 6. The Mirage IIIEE and its squadrons are reworked. | Replenishment's Dedalo and Principe de Asturias forks rebase. Until then the deployed Dedalo fork's Elevator1 does not list the S-55 its variant embarks; only the World Sandbox sails her. World Sandbox value 39; cost $30M (helicopter proxy). | Rebuild; note. |
| Spanish Navy Mod (Modern) (3731208477), 3 files | Spanish-language round names, change log, `_info.ini`. | None. | One-line note. |
| THE REDFOR MOD (3732654992), 14 files | ApproximateVersion 0.7.7 -> 0.8.8. New Su-24M2 and Su-24MP. `MissileDatalinkRelay.ini` deleted, a Kh-59 material file renamed, radar changes. No DLL. | Nothing SEST fields changes (below). | Catalog note with SETUP's reason. |
| US Naval Aviation (3737267013), v111, 19 files | ApproximateVersion 0.8.4 -> 0.8.7. 16 aircraft gain a combat system. `usn_jsm` becomes an IR round with GPS midcourse and land attack (209 -> 416 kg, 150 -> 100 nm). | The JSM is masked: F-35C Lightning II Alt. Loadouts' copy wins (order 21 against 71). SEST Growler's `usn_ea-18g_2020` takes `Digital_Nav_Attack` on the rebuild. | Rebuild; note. |
| Saronic Corsair ASV (3766210676), 2 files | `SaronicCorsairStrikeUSV.dll` rebuilt at 4.12.2; change log; "defense" spelling. | None. | Note. |
| Euromod - Anchorchain Expansion Pack (3784474738), 22 files | The 26 Oct DLLs; `[ExtendedGuidance]` in 15 overwrites; the RIM-7P overwrite adds TimeLimited, TerminalLoft and OptimizeLoftAlt (Euromod Main's round already sets the first two). Below. | Stops Collection Fixes (section 4, item 1). | Decline the SM-3 keys; note. |
| Identify Expanded (3790594162), 3 files | DLL rebuilt (`9f0ec630`, same version string), the build UI Follow-up pins; English and Chinese texts; `language_jp` moved to `language_ja`. | None. | Note. |
| Anduril FQ-44 Fury (3804868806), 8 files | Every Fury type gains a `Squadron1`; XQ58Shadow 1.2.6, the other DLLs rebuilt. | D6 Long Reach's Fury 61 and 62 take `SquadronReference=Squadron1` on the rebuild. | Rebuild; note. |
| Group Manager (3818251045), 2 files | SeaPowerSquadPanel 0.2.16 -> 0.2.17 (`6230e8e7`). | The build both SEST plugins pin, so the pins hold. The catalog still calls it "Formation Manager Replacement". | Note; retitle. |
| Anduril Maritime Drones (3819522350), 9 files | K5KrakenContactStrike rebuilt at 1.0.1; nine language files. | None. | Note. |
| Steelfin (3820576916), 6 files | Wording ("defense") and line endings. | None. | Note. |
| Euromod - Modern Royal Australian Navy (3820759806), 14 files | The RAN S-70B-2 rebuilt on the SH-60 model (below), its old file kept in `aircraft/Testing/`. New KC-30A (`aus_a330_mrtt`, Role=Airliner, boom and probe-and-drogue). The late Canberra LHD-CV takes `ran_f-35b_late`. | Stops Allied Fixes (section 4, item 2). The KC-30A now wins over French Air Force's (order 29 against 184): the World Sandbox values an Airliner at 2, so the KC-30A falls from 242 to 2, and O8 Bomber Stream's tanker is now Euromod's. Cross-Deck's late-Canberra stub follows the F-35B. | Retarget the row; a hand value for the KC-30A; note. |
| The nine unchanged: 3592460366 Modern US Airbase, 3606774881 U.S. Navy 2027 Capabilities, 3607989779 F-35C Lightning II Alt. Loadouts, 3629144864 Euromod - Main Pack, 3642656500 Euromod-Scandinavian Navy, 3695809489 Euromod-(Japan)JMSDF, 3776730617 Euromod - Modern Armada de Chile, 3802216383 JMSDF Hyūga-class, 3813157776 Dynamic Campaign Mod | Nothing since the 25 Oct export: no exported file and no DLL. | None. Both World Sandbox worlds pass on this export. | Regenerate the fingerprints. |
| YF-23 Black Widow II (3796349767), MV-75 Cheyenne II (3810611344), EC-2 Stand Off Jammer (3813033771), not in the exporter's list | DLLs rebuilt at the same versions (28 Oct 2026, 22:38); no text changed. | None. | Optional "code only" notes. |
| Contact Log (3819427362), B-21 Raider (3821992229), Sea Power Topographic Map (3826122523), Sea Power Pop-Out Windows (3826396311), new | Below. | Not catalogued or ordered: the inventory gate fails. | Section 4, item 3. |

**No unit renamed.** Unlike the HH-60H on 25 Oct 2026, no unit id was
renamed or removed, so SEST needs no rename and no alias for old saves. The
five renamed files are three version counters, Identify Expanded's
`language_jp` folder (now `language_ja`) and REDFOR's
`weapons/wp_as-13/wp_as-18_mat.ini` (now `wp_kh59_mat.ini`); the one round
that names the old path, Red Storm Arsenal's `wp_as_18`, ships its own copy.
The one deleted file is REDFOR's `MissileDatalinkRelay.ini`. The one loadout
removed is the RAN S-70B-2's ASWHunterLight, which no SEST mission or roster
names. The one renamed section that units still name is the French
`[EOMS-NG]`.

**The Charles de Gaulle's EOMS-NG.** Charles De Gaulle & Modern French Navy
renamed its sensor `[EOMS-NG]` to `[EOMS_NG]` (`systems/sensors.ini:989`),
but both carriers still mount `SystemName=EOMS-NG`
(`fr_cvn_charles-de-gaulle.ini:1145`,
`fr_cvn_charles-de-gaulle_late.ini:1142`), and no mod or game file defines
it now. Each carrier loses that 40 km electro-optical search sensor and
keeps its other eleven, its PASEO-XLR IRST among them. SEST fields her: D3
The Relief Ship places the base hull (line 75), both RAN campaigns' allied
rosters sell her, and both World Sandbox worlds list both hulls. No gate
catches it, because `check_dependencies` lists dangling names only on hulls
SEST forks. The fix is the one used for `[ZW06]` on 22 Oct 2026: a
`MISSING_SENSORS` entry in Collection Fixes that clones the author's
`[EOMS_NG]` as `[EOMS-NG]`, and stops on its own the day a mod defines
`[EOMS-NG]` again. Tested: the builder prints "+ 7 sensor definitions no mod
supplied: ... EOMS-NG, ZW06". The author's new section drops the old one's
`RPM=60` and its "Bonus IRST" multipliers, so the clone restores today's
definition, not the 25 Oct one.

**The RAN Seahawk.** Euromod RAN rebuilt `ran_S-70B-2_Seahawk` on US Naval
Aviation's SH-60 model (`assets/models/aircraft/sh60/usn_sh_60.obj`,
`animations_usn_sh60`): single main rotor (was tandem), Role ASW,MPA,SAR,
ten stations, empty mass 6,895 -> 6,190 kg, fuel 1,214 -> 1,830 kg, ceiling
14,700 -> 19,000 ft. AntiShip now hangs a tank on Station2 and
`usn_agm-119_air` on Station10; the Penguin and its Station9 hardpoint are
gone, which is what stops Allied Fixes. Its squadron table now points at the
RAN MH-60R's liveries (`aircraft/ran_mh-60r/`, `ran_mh-60r.png` and
`ran_mh-60r_816.png`, `SpecularTexture=sh60_SpecTex.png`). SEST ships the
old airframe, which draws
`aircraft/ran_S-70B-2_Seahawk/S-70B-2_Seahawk.obj`, but not its squadron
table, and Euromod RAN's table outranks RADF's (order 29 against 192). So
for every subscriber whose Euromod RAN has updated, the deployed pack pairs
SEST's old airframe with liveries painted for another model. ANZAC Variants
1, 2, 3, 5, 6 and 8 embark one each
(`ran_ffh_anzac_variants.ini:25, 37, 49, 71, 83, 105`); White Water and
Southern Departure field it, and both RAN campaigns' rosters sell those
ANZACs. A wrong texture is likely; it has not been seen in game, and the
model and texture files are not in the export. The rebuild with the
retargeted row (section 4, item 2) ships the author's own file and ends it.

**The Anchorchain Expansion DLLs** (`plugin-dlls.txt`, dated 26 Oct 2026):
ExtendedGuidance 0.8.7 -> 0.9.7 (230,912 bytes), HullDamage 0.5.9 -> 0.6.10
(2,533,888 bytes), OptimalTargetDist 1.2.0 -> 1.2.1, TestRange 0.1.3 ->
0.2.3; MultiStageMissiles and ACPackSettings rebuilt with unchanged version
strings; the disabled `SeaPowerDLSS.dll_` (59 MB) gone; the other DLLs
unchanged. HullDamage's README says "Native gameplay damage is unchanged"
and "Colliders, buoyancy, flooding and damage remain native"
(`readme/README_HullDamage.md:36, 87`); from 0.6.10 ships of 30,000 t and
above keep local dents only (101). The 15 `[ExtendedGuidance]` sections set
seeker profiles: IIR on the SM-3 IIA and IIB and the NSM 1A, a CW
semi-active profile on five ESSMs, an active pulse-Doppler one on the other
three ESSMs, both SM-6s, the PAC-3 MSE and the MIM-104F. Only the
ExtendedGuidance submod reads them, and it is off unless switched on
(`mods-source/3784474738/ExtendedGuidance_README.txt:88-90`). SEST ships 6
of the 16 changed rounds (`knm_nsm_1a` and `usn_rim-174b` in Replenishment;
`usn_pac3_mse`, `usn_rim-161c`, `usn_rim-161d` and `usn_rim-174a` in
Collection Fixes) and no `ammunition_overwrite/` file for them, so the
overwrites extend SEST's copies. With ExtendedGuidance off, as SEST plays it
(22 Oct review, section 5), the sections do nothing. The SM-6 guard checks
only MaxFlightTime and TimeLimited and still passes.

**REDFOR.** THE REDFOR MOD now declares ApproximateVersion 0.8.8, newer than
the game, so the Mod Manager lists it as not compatible. SETUP marks it
compatible because it is on the reviewed list ("data only; reviewed 27 Oct
2026 on game 0.8.7", `integration/campaign/setup/sest-setup.ps1:219-220`)
and its folder holds no DLL (`plugin-dlls.txt`). Nothing SEST fields
changes. Nine unit ids that REDFOR ships are placed by SEST missions (the
Su-24MP of D1 among them), and other mods' copies win all nine; the new
Su-24M2 and Su-24MP lose to MORE SU24M VARIANTS' (order 124 against 181). Of
its radar changes, those to `96L6` and `30N6E2` sit behind S-300PMU2's
sections (order 137); the ones that apply, `92H6E` (peak power 500 -> 1,000
kW, gain 100 -> 140) and `91H6E` (a clutter-rejection key), are mounted only
by REDFOR's own Big Bird and Gravestone, which no SEST mission places. The
World Sandbox sells 11 of the units REDFOR wins.

**The four new mods.**

- **Contact Log** (3819427362): `ContactLog.dll` 1.0.1 (`a1b8b450`), the
  build both SEST plugins pin. The export holds only `_info.ini` (0.8.5).
- **Sea Power Topographic Map** (3826122523): `SeaPowerTopo.dll` 1.3.1
  (`fd514064`) and a new `SeaPowerTopoFlat.dll` 1.3.0; MIT licence (Lukas
  Struckl). Its description says it "Works on the current flat map (0.8.7)
  and on the new 3D globe map (public beta, the November release). Requires
  Anchor Chain", so by its author's account Anchor Chain can load on the
  beta.
- **Sea Power Pop-Out Windows** (3826396311): `SeaPowerPopOut.dll` 1.0.2
  (`2c6bc876`), not the 1.0.1 build the plugins pin (section 2); MIT licence
  (Lukas Struckl).
- **B-21 Raider** (3821992229), 41 files: `usaf_b-21_raider`
  (Role=HeavyBomber,Bomber, one squadron, "Raider Evaluation Flight"); five
  rounds (`usaf_b21_agm-158b`, `_agm-158c`, `_gbu-31`, `_gbu-38`, `_mk-82`);
  a `usn_steelfin_air.ini` byte-identical to Steelfin's and three other
  mods' copies; B21Ejection, B21Formation and B21Lights 1.0.0; declares
  0.8.5. Its licence (RSG, AlpineStatic) lets a patch "add content alongside
  this mod, provided they do not copy, replace, override, or redistribute
  Original Project Material" (`LICENSE.txt:20-25`), the same clause as
  Steelfin's, so SEST must ship no copy of a B-21 file. The cost model has
  no bomber rule: unmapped, the airframe would be priced as a $75M fighter
  (`integration/common/cost_completion.py:292-307`).

**The nine unchanged mods.** The exporter's list compares the live folders
with `data/mod-fingerprints.json`, last written on 23 Oct 2026 (`15481bca`);
the 24, 25 and 28 Oct captures did not regenerate it. So it lists mods that
changed on 24 or 25 Oct 2026 and have not moved since. For all nine, the
export is identical at both commits and the DLLs are the same. The Dynamic
Campaign Mod is one of them (0.25.0.1, `eacdb9a4`, dated 25 Oct 2026). The
exporter also cannot see a DLL-only update, which is why the YF-23, the
MV-75 and the EC-2 are missing from it (23 Oct review, section 4). Steam's
own update times, which the summary lists, name 21 items since the 25 Oct
capture: the 17 that changed, those three, and 3796706214, whose time alone
moved.

**What the rebuild changes without a decision** (each checked by rebuilding
in a scratch worktree):

- **Replenishment:** the 26 forks from these mods (22 Modern US Navy hulls,
  2 FREMMs, the Dedalo and the Principe de Asturias) rebase.
  `check_pack_fidelity` flags them on the committed pack and passes after.
  On the beta's game files it also rebased 37 game-file forks; with the
  261021 files restored those stay as they are.
- **Cross-Deck:** the late Canberra's stub lists `ran_f-35b_late` for
  `ran_f-35b`, and a new `fr_ffg_floréal` stub
  (`AircraftSupported=fr_as-565_sa,fr_aliaca,phl_h-76`). The Canberra's old
  pairing predates this update: its air group already embarked the late
  F-35B while its deck listed the early one.
- **Growler NGJ:** `usn_ea-18g_2020` gains `Digital_Nav_Attack`, US Naval
  Aviation's.
- **Campaign:** D6 Long Reach's two Furies gain
  `SquadronReference=Squadron1`. Southern Watch's REQUIRED-MODS keeps French
  Air Force (3758943352) HARD REQUIRED, with the reason changed from "a unit
  a mission places" to "a squadron a flight comes from": the KC-30A O8
  Bomber Stream places now resolves to Euromod RAN's file. Coverage: all 224
  accounted for.
- **World Sandbox:** both worlds go from 1,560 to 1,563 catalogue entries
  (the Aliaca, the S-55, the Floréal), and the KC-30A's value from 242 to 2.
- **Combat Costs:** 4,373 rows; the three new units at proxy prices; the
  KC-30A's owner changes to Euromod RAN with its prices kept.

## 4. For the owner

The owner's decisions of 30 Oct 2026 are recorded here as taken (items 1, 2,
3, 5 and 6). Items 4, 7 and 8 are requests that stay open. Item 9 is what
the beta can show without code mods.

1. **The SM-3 `[ExtendedGuidance]` keys: declined.** The Anchorchain
   overwrites of the SM-3 Block IIA and IIB (`usn_rim-161c_OVWR.ini`,
   `usn_rim-161d_OVWR.ini`) gained five seeker keys in a new
   `[ExtendedGuidance]` section (SeekerProfile=IIR_Imaging,
   SeekerTrackRate=50, IRBackgroundRejection=0.8, IRBrightnessRejection=0.6,
   IRShapeRejection=0.25). Only the AC Pack's ExtendedGuidance submod reads
   them: no game file and no other mod's round sets any of them, and "The
   submod defaults to off"
   (`mods-source/3784474738/ExtendedGuidance_README.txt:90`). SEST keeps it
   off (22 Oct review, section 5). The integration records the five keys per
   round in `SM3_OVWR_DECLINED`
   (`integration/collection-fixes/build_patch.py:199`) with that reason.
   Tested: Collection Fixes builds, and the SM-3 Block IB, IIA and IIB, the
   SM-6 Block I and the PAC-3 MSE come out byte-identical to the committed
   files. The same update gives 13 more overwrites the section; with the
   submod off they do nothing.

2. **The RAN Seahawk Redback row: retargeted to the new AntiShip fit.** The
   row at `integration/allied-fixes/build_patch.py:759` becomes
   `[("usn_agm-119_air", "pod", 1)]`, and `tools/tests/test_redback.py:185`
   expects Station10 for `ran_S-70B-2_Seahawk` only (3403661005's
   `S-70B-2_Seahawk` stays on 9). Tested: Allied Fixes builds, and the
   output is the author's new file plus `[WeaponSystem1SEST_REDBACK]`
   (Station2 `usn_sh60_tank`, Station10 `sest_agr-30_pod`, the
   `H60_Pylon114` submodel hidden); 18 of the 19 Redback tests pass, and the
   19th is the line-185 expectation. Still to check: the pod on the AGM-119
   pylon in the loadout preview, as the note at `build_patch.py:747-751`
   asks. The rebuild also ends the livery mismatch the deployed pack has now
   (section 3, *The RAN Seahawk*), so upload soon after it.

3. **The four new mods: in the catalog, the canonical order and the
   collection.** Contact Log, Sea Power Topographic Map, Sea Power Pop-Out
   Windows and B-21 Raider. This replaces the 28 Oct integration review's
   default that the three UI mods stay off the collection
   (`docs/integration-20261028-review.md:84`). What follows:
   - Every subscriber needs all four. The pack's `LOAD-ORDER.txt` lists
     every canonical id, and SETUP stops while one is missing
     (`integration/campaign/setup/sest-setup.ps1:413-433`). The pack item's
     Required Items and the collection (3812390790) must list the four
     before the upload.
   - UI Follow-up 1.4.2 runs only beside Contact Log 1.0.1
     (`integration/ui-followup/source/ContactsFix.cs:56-57`;
     `docs/FEATURES.md:575-576`). With Contact Log in the collection it can
     run for every subscriber on Build 261021, not only on the owner's PC.
   - With Pop-Out Windows 1.0.2, Runtime 1.5.0's pop-out bridges and UI
     Follow-up's Contacts pop-out surface fix, camera compass and Formation
     UI mode turn themselves off; the rest of both plugins stays on.
     Re-pinning needs Runtime's source (item 5) and the off-repo UI
     Follow-up build.
   - The B-21 needs prices for itself and its five rounds, and a mission, a
     roster sale or an excuse, or the campaign build stops on it. SEST must
     ship no copy of its files (its licence).

   Section 5 lists the entries.

4. **The Workshop item's 26 Oct upload: please send a listing.** The copy on
   the PC shows Runtime 1.5.0 arriving with the 26 Oct 2026 20:11 upload,
   while `docs/campaigns/southern-watch/publishing.md:13-14` says the item
   carries `b1449201`'s build, with Runtime 1.2.0 (section 1). GPT's 27 Oct
   capture of the installed pack (52 files) matches PR #50's head
   (`0776fa50`) byte for byte, including a `LOAD-ORDER.txt` with 202 ids,
   the three UI mods among them. If that file went up with the upload, SETUP
   has refused to run since 26 Oct 2026 for every subscriber without those
   three. Please send, with the game closed, a listing of
   `steamapps\workshop\content\1286220\3812461539` with last-write times
   (files written at 20:41-20:42 on 26 Oct 2026 came with the download;
   later ones were put in by hand), or at least `LOAD-ORDER.txt`'s time and
   the file count. `publishing.md` follows once it is known. The next upload
   replaces either.

5. **Runtime 1.5.0: stays the shipped binary; its source is being recovered
   or reconstructed.** Decided. No branch, tag or commit holds its source
   (`integration/runtime-fixes/README.md:8-19`). The 27 Oct handoff zips
   hold a complete decompiled reference (not source), and a hybrid build
   (the 1.2.0 fork's files for six types, the decompile for the rest)
   already compiles to 253 of 1.5.0's 317 methods IL-identical. For the beta
   this matters twice: 1.5.0 is pinned to Build 261021's assemblies and
   turns off on any other, and re-gating it needs a source (README steps 6
   and 7, lines 248-253). The 1.2.0 fork base builds today, but re-gated it
   would ship a downgrade: no native F11 windows, no three-row debrief, no
   pop-out bridges, no preparation map, no towed-sonar guard. **Request:**
   search the PC for GPT's 1.5.0 project, files dated 25 to 27 Oct 2026.
   Look in Downloads for any SEST zip whose name mentions runtime, 1.5.0 or
   150, or that holds a `source/` folder; in `%LOCALAPPDATA%\SEST\` (the
   `playtest-builds` and backup folders GPT's installers made); in
   `%TEMP%\SEST-*`; and in the PC's clone of this repository
   (`git worktree list`, `git stash list`, `git branch -a`,
   `git fsck --lost-found`). The names to look for are `RuntimeFixesMod.cs`,
   `TowedSensorGuard.cs`, `PopOutBridge.cs`, any `*.csproj`, or a
   128,000-byte `SEST.RuntimeFixes.dll` in an `obj\` or `bin\` folder.
   Failing that, ask GPT for the project folder, its compiler and its
   reference DLLs. Mono's compiler gives the same bytes from the same
   inputs, so the original project should rebuild 1.5.0 exactly, and UI
   Follow-up's three Runtime pins would keep holding.

6. **The target build: 261021; the beta on a beta branch.** Decided. The
   pack keeps targeting the stable Build 261021, so the integration restores
   `mods-source/_vanilla` to the 261021 export and builds as before. The
   CIWS retune moves to the beta's ladder only on a beta branch, for the 11
   Nov 2026 release, with the other beta items of section 2. One consequence
   for testing: the PC is on the beta, where no code mod loads, so play
   tests of the next upload need Steam's public branch (Build 261021).

7. **The DLLs to send.** For the beta branch: on the beta, with the game
   closed, run `tools\export-map-diagnostics.ps1 -IncludeGameAssembly`. It
   copies `Seapower-Scripts.dll` and `Assembly-CSharp.dll` (the script's
   lines 124-142) and every DLL under `BepInEx\plugins` and the Workshop
   folder (83-101), so the preloader and Anchor Chain's `AnchorChain.dll`
   come with it. Add `Sea Power_Data\Managed\Noesis.NoesisGUI.dll` by hand:
   the script does not copy it, and both SEST plugins pin it. With them the
   beta's `FileManager` change can be read, the new hashes recorded for
   re-gating, and the beta's `IniHandler` checked for `#!extend` files
   without Anchor Chain. The other useful step is to ask Anchor Chain's
   authors whether a preloader for the beta exists. Topographic Map's author
   says the mod works on the beta and needs Anchor Chain, so that author may
   know how.

8. **GPT's crash zip.** The 27 Oct crash is in no log in hand (section 1).
   Please send `SEST-crash-review-20261027-131824-34062f.zip` from Downloads
   (or its `player/Player.log`), Unity's crash folder for 27 Oct 2026
   (`%LOCALAPPDATA%\Temp\Triassic Games\Sea Power\Crashes`), and any Windows
   Application Error entries of 27 Oct 2026. The reproduction (Contacts out
   to the Pop-Out monitor, back, and out again) can run on Build 261021
   only: on the beta no code loads.

9. **What to try on the beta without code mods.** The pack's data loads on
   the beta (the menu read a Workshop effect file, `player.log:67-68`), so
   its campaigns can be looked at now, as long as nothing depends on code.
   Open each of the four campaigns and look at the campaign map on the new
   projection. Start one mission in each, Southern Reach's southern missions
   first: they reach 50S and beyond, where the projection differs most
   (`docs/beta-globe-readiness-20261027.md`, review priority 1). Continue
   one of the 27 Oct Sulu saves. Finish a mission and return to the campaign
   map. Note any Mod Manager warning. Then quit and run
   `capture-context.ps1 -Redact -IncludeSaves`. Not testable until Anchor
   Chain loads: costs, the debrief rows, the preparation map, the UI fixes,
   the World Sandbox worlds and every other mod's code.

## 5. Validation

**The from-scratch build on this export**
(`tools/build_all.py --from-scratch`; its log has 76 lines and ends
"exit=1") stops in six builders. Two are root causes, both author updates:

- **SEST Allied Fixes:** "ran_S-70B-2_Seahawk.ini/AntiShip: 0 station(s)
  hang knm_penguin_mk2, expected 1 - upstream changed the fit" (log line 24;
  the row at `integration/allied-fixes/build_patch.py:759`).
- **SEST Collection Fixes:** "usn_rim-161c: the Anchorchain overwrite now
  also sets IRBackgroundRejection, IRBrightnessRejection, IRShapeRejection,
  SeekerProfile, SeekerTrackRate" (log line 28; the guard at
  `build_patch.py:254-298` flattens sections, so the new section's keys read
  as overwrite keys). Line 27 ("usn_rgm_184a: upstream removed
  MinAttackAltitude - no override needed") is information only. The builder
  wrote 13 ammunition files before it stopped.

Four are cascades, as on 25 Oct 2026. **RAAF Bases** found US Naval
Aviation's 19 MH-60R squadrons where Collection Fixes' file defines 20
(38-43). **Replenishment** found The Royal Navy's `usn_cal_40mm`, which has
no AmmoPoints, where Collection Fixes' copy has 4.5 (46-50). **Combat
Costs** and the **campaign** lost RAAF Bases' `airbase_raaf_curtin` and
`airbase_raaf_darwin` (54-72). Both of those also need Allied Fixes: two
missions place its `sest_uav_forward`
(`integration/campaign/mission_depth.py:143`,
`additional_dispatches.py:40`), and the cost tooling reads every pack's land
units (`integration/common/costs.py:544-548`). Neither root cause is in the
game files, and with the two root packs held the four others build on this
export: a second build without `--from-scratch`, holding the two root packs
at their committed output, built the other 23, wrote the cost list (4,373
rows) and consolidated 4,306 files, one more than committed: the Floréal
cross-deck stub.

**The gates**, run twice: on the capture as the from-scratch build left it,
and with the two root packs held at their committed output.

| check | as the from-scratch build left it | root packs held |
|---|---|---|
| check_pack_fidelity | pass: 423 files, every byte difference an intended insertion | pass: 419 files |
| check_campaign_coverage | fail: no built campaign (cascade) | pass: all 224 enabled mods and SEST packs accounted for |
| check_dependencies | pass | pass |
| check_load_order | pass; 7 live entries not canonical: the four new mods, the pack's Workshop copy, ACConfigs, IdentifyExpanded | pass |
| preflight --all | pass; 56 dangling references in 13 missions listed, 31 of them RAAF base ids (cascade) | pass; the 25 known seed-only references in 3 missions |
| check_weapon_employment | pass: 10,349 contracts | pass: 10,527 contracts |
| check_alias_bases | fail: 10 STALE OVERWRITE lines, Euromod Main Pack combat-system patches whose retargeted copies Collection Fixes ships (cascade) | pass: the two known soft lines (`aces_aim-9m_stdm` with no base; `ae_ssk_s80_plus` firing the undefined `DateBased_HWT`) |
| check_scenarios | pass: 11 scenarios, 348 sections | pass |
| check_stale_phrases | pass: 20 phrases | pass |
| check_inventory | **fail: catalog and order miss 3819427362, 3821992229, 3826122523, 3826396311** | **fail: the same** |
| check_game_version | fail: five "not built" lines (cascade); reads 0.8.7 Build #261026, and all 26 builder literals match | pass (REDFOR's 0.8.8 is information only) |
| check_vanilla_drift | pass: 1,032 files (`--since 1bda58a6`) | pass: 1,032 files (`--since 7e86df43`): 48 overridden, 6 merged, 211 placed, 273 builder-read, 693 other, nothing needs a human |
| check_combat_costs | fail: `airbase_raaf_curtin` (cascade) | pass: 4,373 references in both modes |
| World Sandbox | pass, on output with cascade artefacts | pass: 141 bases, 267 forces, 1,563 catalogue entries |
| Regional Expansion | pass, likewise | pass: 156 bases, 293 forces, 1,563 entries |
| tools tests | fail: 254 run, 4 failures and 28 errors, each a missing built file (cascade) | pass: 282, 1 skipped |
| campaign tests | fail: stopped at The Open Door, `airbase_raaf_tindal` (cascade) | pass: 331 |

`check_pack_fidelity` proves SEST Replenishment's files only: with Allied
Fixes held at its committed output it passes, although that pack's RAN
Seahawk is built on a file upstream has rewritten. `--from-scratch` with a
clean `git status` stays the gate; it is what caught this.

**What the next integration must change, in priority order:**

1. **The game files.** Restore `mods-source/_vanilla` to the 261021 export
   of `7e86df43` (section 4, item 6). Keep `data/install-snapshot` as
   captured: it records the beta session. `check_game_version` accepts the
   pair, because its snapshot rule fails only when the export is newer than
   the snapshot (`tools/check_game_version.py:453-457`). Do not re-run
   `tools/workshop_refresh_summary.py` after the restore: it takes the
   game's build line from the export, so it would print Build 261021 beside
   the beta's Steam build; the copy committed with this review records the
   capture.
2. **Collection Fixes.** The five SM-3 keys in `SM3_OVWR_DECLINED` (section
   4, item 1) and the `EOMS-NG` entry in `MISSING_SENSORS` (section 3). Both
   tested.
3. **Allied Fixes.** The RAN S-70B-2 row retargeted and
   `tools/tests/test_redback.py:185` updated (section 4, item 2). Tested.
4. **The four new mods** (section 4, item 3):
   - catalog entries in `data/mod-catalog.json`, and Group Manager retitled
     from "Formation Manager Replacement";
   - positions in `data/load-order.tokens.txt`: the three UI mods directly
     below Group Manager (token 7), as the PC already has them; the B-21
     directly below B-2 Spirit (token 80), which also keeps Steelfin (61)
     above the B-21's copy of `usn_steelfin_air.ini`;
   - "library" entries in `EXCUSES`
     (`integration/campaign/campaign_data.py`, as for `better-tacmap` and
     `formation-manager-replacement`) for the three code mods, and for the
     B-21 a mission or roster that reaches it, or an excuse: an ordered mod
     that is neither stops the campaign build
     (`integration/campaign/build_pack.py:8361-8367`);
   - cost mappings for `usaf_b-21_raider` and its five rounds in
     `integration/combat-costs/mappings.json` (the B-2 Spirit is priced at
     $750M/$1.2B, `docs/combat-costs/cost-list.csv:3621`);
   - the pack item's Required Items and the collection, at the upload.
5. **World Sandbox.** A hand value for `aus_a330_mrtt`: the Tanker figure
   (60) in place of the Airliner one (2)
   (`integration/world-sandbox/build_dynamic_campaign.py:234-237`).
6. **Combat Costs.** `fr_aliaca` as a small UAV (the policy has a $2M
   `small_uav` model, `integration/combat-costs/coverage-policy.json:71`),
   by a name rule or a mapping; `spa_s-55` if $30M is too high for a 1950s
   helicopter.
7. **Records.** `python3 tools/fingerprint_mods.py`; dated 28 Oct catalog
   notes on the 17 changed mods, REDFOR's reviewed-list reason, and the
   code-only updates of the YF-23, MV-75 and EC-2; `docs/mod-catalog.md` and
   the load-order docs regenerated; `publishing.md` once item 4 of section 4
   is answered.
8. **Rebuild, check, upload.** `python3 tools/build_all.py --from-scratch`,
   the 17 checks above; commit the output. Add to the play-test card: D2 and
   D7 on the new decks, D6's Fury squadrons, O8's KC-30A, an ANZAC's RAN
   Seahawk (livery and Redback pod), and the Charles de Gaulle's EOMS-NG.
   Before Submit, `Player.log` on a 261021 PC with today's mods should show
   Runtime's "pop-out bridge inactive" line and UI Follow-up's three
   "inactive" lines (Pop-Out 1.0.2). Then upload soon: the deployed pack
   carries the Seahawk mismatch and the undefined EOMS-NG.
9. **Later, tools.** SETUP's Anchor Chain check could read
   `BepInEx\LogOutput.log` when it holds a finished run ("Chainloader
   startup complete") and warn when there is no "Loaded assembly
   AnchorChain" line. `capture-context.ps1` should write
   `player.problems.txt` with "0 hit(s)" rather than leave the old one.
   After the upload, a listing of the installed pack should show the Floréal
   stub under its exact name, the first non-ASCII path SEST ships.

**On the beta branch, not in this integration:** `CIWS_RETUNE` re-anchored
to the beta's ladder and the restored CIWS sections rebased (with their
"0.8.3" headers); the 32 tactical-map keys; `TaskForceModeAirbaseSection`
and the two campaign-level keys; `GeoPosition` and `geo,` waypoints in the
position pool and the audit tool, and the `Lambert*` keys as a play area;
the Southern Reach test card's Phalanx figures; `combat.py`'s datalink
comment; the formation control mode; the percent-form `LaunchReliability`
values; and both plugins re-gated once the beta's DLLs and 1.5.0's source
are in hand.

**Not checked:**

- Nothing ran in game. On the beta no code loaded, and the beta's
  `Seapower-Scripts.dll` and `Noesis.NoesisGUI.dll` are not in hand. The
  discovery failure is explained from the logs and the preloader's code, not
  from the beta's; the beta's handling of the missing tactical-map keys, an
  absent `TaskForceModeAirbaseSection`, the `Volume` and
  `MinTakeoffDistance` keys, percent-form reliability values and the
  migration of SEST's missions is unknown.
- Whether `#!extend` and `ammunition_overwrite/` files apply without Anchor
  Chain (two repository statements disagree, section 2). It also decides
  which value wins for the Arleigh concept's combat system.
- The Workshop item's file set and when its 202-id `LOAD-ORDER.txt` was
  written (section 4, item 4).
- The 27 Oct crash: the crash session's log is not in hand; its description
  and the four `0xc0000005` events come from GPT's JSON only.
- The RAN Seahawk's livery: inferred from the squadron table and material
  files; the models and textures are not in the export. The Redback pod's
  fit on the AGM-119 pylon is not checked.
- Whether the game reads unit files in `aircraft/Testing/` or at a mod's
  root (Euromod RAN's old Seahawk, Modern US Navy's stray Wasp), and whether
  it reads the late Wasp's `[CombatSystem1]` without a count header.
- ExtendedGuidance, HullDamage and TestRange beyond their READMEs and `.ini`
  files.
- The authors' Steam change notes for these updates:
  `data/install-snapshot/workshop-change-notes.txt` is the 13 Oct file.
- No from-scratch build ran with all the fixes together, and none on the
  restored 261021 files. The fixes were tried builder by builder (Collection
  Fixes, Allied Fixes, Replenishment, Cross-Deck, Growler NGJ, World
  Sandbox, Combat Costs, the campaign) with the gates named above;
  consolidation and the full suites did not run with them.
- Whether the Floréal stub's non-ASCII name survives the installer, SETUP,
  the zip and the Steam upload.
- B-21, Aliaca and S-55 prices: not researched.
