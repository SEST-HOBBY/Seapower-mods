# 26 October 2026: SW05 P-8 and combat-debrief triage

Owner playtest: Contact Log (3819427362) and Topographic Map (3826122523) work but both bind F6. Combat-cost debrief still crowds native summary. SW05 "Weapons Free": a player-allocated P-8 with AntiShip Harpoons does not reliably fire. New subscription 3826396311 has **not** been placed in the SEST load order; identity and compatibility not verified.

## Debrief layout candidate
CampaignCosts.cs now limits native summary to concise Cost Weapons, Units, Stores, Mission and Campaign pairs, and one conditional "See F11 Combat Costs" gap row. It intentionally does not rewrite saved combat accounting or weapon tracking. Player and Enemy abbreviate to P/E in the narrow UI. Verify formatting in-game before merging.

## SW05 evidence
SW05 places two RAAF F-35A Attack tasking placeholders; the P-8 is **not** placed directly and is allocated via the campaign air-tasking system. Its actual fit/weapon state must be inspected after allocation. The SEST distributed aircraft/usn_p8.ini already replaces the nonexistent AGM-84G with four AGM-84N rounds. AGM-84N has MidCourseCorrection=1, requiring a guidance channel. usn_p8's WeaponSystem2 hardpoint has no AssociatedSensors; the P-8's upstream AN/APY-10 definition in Workshop 3602046770 has WeaponChannels=0. A prior SEST diagnostic identified the same family of no-channel radio-command issues. **This is a strong hypothesis, not a proven cause**; no missile stat edits are committed here, and changing the shared missile globally would impact other platforms.

For focused test, ensure SW05's P-8 is actually allocated, uses AntiShip with four AGM-84N and not ASW, has a valid hostile surface contact, is in range/altitude and appropriate firing arc, and is not awaiting aircraft preparation. Record precise symptom: absent weapon vs greyed launch vs refused order vs spawned missile doing nothing, and any corresponding log error. Compare a working donor (e.g. other aircraft's AGM-84N or vanilla AGM-84D) before selecting a surgical remedy. Do not change store or missile definitions globally without a compatibility matrix.

## New mod and keys
3826396311 is subscribed only; do not add to canonical order until its _info.ini, files and dependency requirements have been captured. Contact Log and Topographic Map both bind F6. Topography uses configurable BepInEx setting `Toggle key` in `BepInEx/config/dev.sewerlabs.seapowertopo.cfg`. Recommended move Topography toggle to F7 *only after checking that F7 is not used elsewhere*; retain Shift+F6 look cycling or remap it too.

## Safety and acceptance
- Preserve previous Stage A/B ZIPs.
- With Sea Power fully exited, run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\SEST-Playtest-Capture-v2.ps1 -Phase After` to preserve the actual played session in a new archive before relaunch.
- Capture screenshots of native debrief and the P-8 weapon menu, with any on-screen launch rejection.
- Rebuild full pack, compile runtime C#, run tests and then playtest before merging or uploading.
- No Steam publication, save changes, installed modification or production/default branch push in this task.
