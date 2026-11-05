# Plan: capture current mod state, then one Workshop update for both builds

SEST Integration Pack, Workshop item 3812461539, collection 3812390790. Drafted 3 Nov 2026, brought up to date on 4 Nov 2026 after the owner's two captures of 3 Nov 2026. Nothing here is uploaded, merged or installed on the owner's PC without the owner.

## 1. Goal, and what "one update for both builds" can mean today

Goal: one Workshop upload that repairs the published pack, carries the current state of every installed Workshop mod, and loads on Sea Power 0.8.7 on both Steam branches: the normal release (Build 261021) and the public beta (Build 261026).

The repair is overdue. The 26 Oct 2026 upload (4,305 files, 203-entry LOAD-ORDER.txt) names Contact Log 3819427362, Topographic Map 3826122523 and Pop-Out Windows 3826396311, which are in neither the collection nor the item's Required Items, so SETUP refuses to finish for every subscriber without them.

What one update can mean:

- Data: yes. Both builds report 0.8.7, so the SETUP version rule is unaffected. The pack's data is built from the stable vanilla export and the beta reads it. Stable ignores unknown keys, so beta-only keys can be added.
- Code mods: yes, with conditions. Runtime 1.5.0 is hash-gated to the stable build and stays inactive on the beta. Anchor Chain's Workshop preloader fails on the beta ("Could not find AnchorChain chainloader") because the Workshop folder is not registered when BepInEx plugins load, so for an ordinary subscriber no Anchor Chain plugin loads on the beta at all. So one upload gives working code mods on stable and inert ones on the beta; more needs files in BepInEx, which a Workshop item cannot place (section 4).
- Modifier files: a limit, not a choice. The built pack has 169 "#!extend" files (162 Cross-Deck stubs, 4 cost catalogs, 3 ammunition files). On the beta, the Workshop Anchor Chain preloader's early read of FileManager.Directories makes the game's one-time modifier scan complete against a stale folder list, so every Workshop mod's #!extend, #!prepend and #!copy file is ignored for the session (section 4). SEST's beta Runtime 1.5.2 repairs it at startup, but only where that runtime runs. The posting must say so.

## 2. Capture now

Steam pages are not reachable from the build environment; the owner's captures are the only way to learn which authors have updated for the beta.

Capture A, Workshop mods: tools/capture-all-mod-updates.ps1 on release/consolidated-20261103. Done on 3 Nov 2026 at 23:22 (branch chore/workshop-refresh-20261104, commit 530129ec): 28 mods updated by their authors since 28 Oct 2026, 806 changed files, the game still on the stable Build 261021 for that run. It is being integrated as integ/capture-20261104 (section 3). The steps stay for the next capture, which the owner should take again just before the upload if authors keep updating.
1. Close the game. Check out release/consolidated-20261103 with a clean tree; the script refuses uncommitted changes and the deploy branch.
2. Run it once. It creates a fresh chore/workshop-refresh-YYYYMMDD branch, exports every installed Workshop mod, writes fingerprints, runs the inventory check and builds a review zip. It never exports the game's own files, so mods-source/_vanilla keeps the stable export even on the beta PC.
3. Yields: each mod's files and fingerprint against the previous capture (which authors have updated); the installed Pop-Out Windows and Anchor Chain versions; the thirteen author plugins' versions (section 4). The 3 Nov 2026 capture's answers: Pop-Out Windows is 1.1.3 and Topographic Map 1.5.0; AutomaticSAR was rebuilt on 31 Oct 2026 (1.0.0+a40ac539), Custom Loadout Editor's LoadoutManager was rebuilt on 2 Nov 2026 beside a new LoadoutManagerForLive.dll, and Saronic Corsair now ships its own bootstrap (a version.dll to copy beside Sea Power.exe by hand, with HarmonyDependencies); the nine self-stopping plugins' DLLs are unchanged.
4. Send: push the branch, open a pull request, attach the review zip and the inventory output.

Capture B, beta references: tools/capture-beta-references.ps1 and tools/capture-r4-results.ps1 on beta/r4-20261103, on the beta PC after a beta session with the pack loaded. Taken on 3 Nov 2026 at 23:09; it shows the R3 plugins still installed (SEST.RuntimeFixes a0fb4279, SEST.ContactsFix d60e662b), so the beta test is still to run: Repair-Beta-Startup.cmd from SEST-Beta-Repair-R5-20261105.zip (R5 includes R4's fixes and accepts an installed R3), a beta session, then Capture-Repair-Results.cmd. They collect the beta managed assemblies, the logs, SEST's cost catalogs, the quantity history and the Triton's sensor files for the beta test. The logs carry the 32 "UI_Parameters: Settings_UI_Tactical.ini has no map setting" warnings and the modifier-scan outcome, the evidence for section 4's reports; the assemblies serve any beta build or parity test. Send: commit on the beta branch, push, pull request.

Capture C, only for the dual-build Runtime: a complete capture of the stable build's managed folder; the 23 Oct 2026 reference capture (scratchpad mapreview-20261023/zip/game-reference) is not complete enough.

## 3. Integrate

One chore branch (from capture A), rebased on release/consolidated-20261103 (PR #56, 204 entries, all 18 gates pass), one pull request, merged only by the owner.

1. Catalog: update catalog notes and fingerprints for each changed mod; record author version changes in the tracked list (section 4).
2. Pricing: price any new units through the existing path.
3. TacMap keys: done on release/consolidated-20261103 on 4 Nov 2026 (9a56b9ee). SEST_TacMap_Colors carries the 32 keys the beta log reported missing (WeaponNoEscapeRangeColor, SeekerHiddenColor, PlayAreaStrokeColor, DrawingPresetDefault and 28 more) at the beta's default values, read from the beta vanilla export on chore/workshop-refresh-20261028 (f590fb8c). Harmless on stable.
4. The Redback carriers' night check: done on the same branch (d19ce922). The AGR-30 counts as an air-to-air round, so the weapon panel warned "No radar or night vision" on the RAN MH-60R; each Redback helicopter's FLIR night vision level is now written into its unit file at the value the top-most defining mod gives, which both builds honour.
5. CIWS: no change. Per the owner's 30 Oct 2026 decision the stable CIWS behaviour ships unchanged, and the beta ladder (Phalanx 40 to 65, 1000 to 375 rounds, 6 to 10 s) enters only once the developers' release expected on 11 Nov 2026 is available and verified. The beta's other reworks stay out too, on the isolated beta branch.
6. The UI Follow-up re-pin (section 4) lands on the same branch.
7. Rebuild: tools/build_all.py --from-scratch, then the 18 gates. LOAD-ORDER.txt stays at 204 entries unless capture A adds mods.

## 4. Code mods on both builds

Option 1: ship Runtime 1.5.0 as is (SEST.RuntimeFixes.dll 7ba6d6d9). Active on stable, inactive on the beta by its hash gate. Known good. Required companion fix: UI Follow-up 1.4.2 (SEST.ContactsFix.dll) pins Runtime 1.5.0's hash and Pop-Out Windows 1.0.1 (d0027215), while the 3 Nov 2026 capture has 1.1.3 installed (5709ed68), so its pop-out bridges are off for every subscriber. Re-pin to 1.1.3, rebuild, verify on stable. The beta UI 1.4.3 pins Pop-Out 1.1.1 (9be4003d) and is behind the same way: the beta session of 3 Nov 2026 logs "Uninspected assembly: SeaPowerPopOut" and keeps its Contacts, formation and compass bridges off, so R5 (5 Nov 2026, `beta/r5-20261105`) re-pins it to 1.1.3 after an IL comparison of the members it binds. It cannot ship beside the stable UI: the loader loads every DLL it finds, so two DLLs with one assembly name cannot share an Anchor Chain mod folder.

Option 2: one dual-build Runtime. Runtime 1.5.0's source was never recovered; the hybrid reconstruction on feature/runtime-150-source is 253 of 317 methods IL-identical; the complete behavioural reconstruction (314 declared type and method contracts, checked against the captured binary by parity tests) is the basis of beta Runtime 1.5.1/1.5.2 on beta/r4-20261103. That source binds every native member reflectively, so a single Runtime would bind by game hash at start. Known differences to carry: Globals.currentMissionFilePath (field on stable, property on the beta), the beta-only watermark hide and modifier-registry repair, and the pop-out pins. Prerequisites: capture C, and the Roslyn build (integration/beta-feature-parity/build-roslyn.ps1, PowerShell 7's compiler, C# 12) against both reference sets. Regression evidence: parity tests against the captured 1.5.0 binary, the API-contract check, IL comparison of shared methods, and the owner's in-game checks on both Steam branches. It replaces a binary subscribers run today, so it is its own feature branch.

Recommendation: Option 1 for this upload; Option 2 after the 11 Nov 2026 release, so the beta hash is bound once.

Anchor Chain on the beta. SEST's answer on the owner's PC is a bounded Anchor Chain fork plus an inert bootstrap, placed into BepInEx by an installer script with hash checks. The Workshop item cannot do that. The owner's SETUP script could offer the installation as an explicit opt-in.

The modifier-scan defect. Report it to Triassic Games (IniHandler.ScanForModifierFiles runs once, and SearchDirectory's constructor opens _info.ini through IniHandler.open before FileManager.OnStart publishes the rebuilt list, so an early read of FileManager.Directories freezes the stale three-folder list) and to the Anchor Chain author (preloader 1.0.0 reads FileManager.Directories before Steam initialises). Attach capture B's logs.

Author plugins, tracked list. Nine stop themselves on the beta because their own validation finds changed native members: MissileControlMod, MultiStageMissiles, OptimalTargetDist (launch sharing), SubModelStabilization, TestRange, UiWorkerProbe, WeaponLauncherEffects, BetterTacMap, and parts of ParallelRangeProbe. Four are held back by SEST's loader policy: ExtendedGuidance 0.9.7, AutomaticSAR, OspreyMechanics, CombatWorker. A separate investigation decides, plugin by plugin, whether SEST can adapt them or only their authors can. Capture A fills the column "author updated": on 3 Nov 2026 none of the nine had a new build, and of the four held back only AutomaticSAR was rebuilt (31 Oct 2026), which the investigation checks against the beta before any policy change. For an ordinary subscriber on the beta none of them loads until Anchor Chain does.

## 5. The Workshop posting

1. Collection and Required Items first. Add Contact Log 3819427362, Topographic Map 3826122523, Pop-Out Windows 3826396311 and B-21 Raider 3821992229 to collection 3812390790 and to the item's Required Items. Do this before the upload; it ends the SETUP refusal once subscribers obtain them.
2. Test the same build on both Steam branches. Stable: SETUP completes, 204 entries load, Runtime 1.5.0 active, pop-out bridges on, one play session. Beta, with the fork and bootstrap removed from BepInEx (an ordinary subscriber's state): SETUP completes, no SEST plugin loads, no TacMap warnings, modifier-file outcome noted. Beta again with the fork, if the opt-in is offered.
3. Upload the merged build.

Description, compatibility paragraph (draft):

"Works with Sea Power 0.8.7 on both the normal release (Build 261021) and the public beta (Build 261026). All pack data loads on both. The SEST code mods (Runtime 1.5.0, UI Follow-up) are active on the normal release and inactive on the public beta by design: the Anchor Chain loader from the Workshop does not start on that build, so no Anchor Chain mod runs there. Also on the beta, the game currently skips files that extend other mods (#!extend) when the Anchor Chain loader is installed; reported to the developers and the loader's author. CIWS values follow the normal release. Subscribe to all Required Items before running SETUP."

Change note (draft; mod list from capture A):

"[upload date]: the collection and Required Items now include Contact Log, Topographic Map, Pop-Out Windows and B-21 Raider, which SETUP needs. Mods refreshed to their Workshop state of 3 Nov 2026. UI Follow-up re-pinned to the current Pop-Out Windows. SEST_TacMap_Colors gains the public beta's 32 tactical-map keys (no effect on the normal release). Tested on both Steam branches. No CIWS change."

If the opt-in is approved, each text gains a sentence saying what it installs, where, and that it is optional.

## 6. Decisions needed from the owner

1. Both captures were taken on 3 Nov 2026; run the R5 test on the beta PC (capture B's steps), and take capture A again just before the upload if authors update in the meantime.
2. Runtime: Option 1 for this upload, or wait for Option 2.
3. Approve the UI Follow-up re-pin to Pop-Out Windows 1.1.3.
4. SETUP opt-in for the Anchor Chain fork on the beta: offer it, or not yet.
5. Send the modifier-scan reports.
6. Make the collection and Required Items changes on Steam.
7. Upload before 11 Nov 2026 (recommended) or hold for the release.
8. Approve the description and change-note wording.

## 7. Risks

- The 11 Nov 2026 release may change hashes again; everything hash-gated (Runtime 1.5.0, the UI pins, a dual Runtime's beta binding) must be re-verified then.
- A rebuilt Runtime is a new binary whose evidence is parity tests, not field use; keep it out of the repair upload.
- On the beta the 169 modifier files stay ignored for ordinary subscribers until Triassic Games or the Anchor Chain author fixes the early scan.
- Pop-Out Windows drift silently disables the bridges; re-check the pin on every capture.
- Authors may update between capture and upload; then re-run capture A on a new chore branch.
- The opt-in installs files into BepInEx on subscribers' PCs; the hash checks bound it, but the wording must be explicit and the default no.
