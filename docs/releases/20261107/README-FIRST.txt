SEST R11 — MODERNISED WORLD AND SERVICE UPDATE CANDIDATE
9 November 2026 | SEST-DEV | beta 0.8.7-261107

CLOSE SEA POWER, EXTRACT THIS COMPLETE ZIP INTO A NEW FOLDER, THEN RUN:

  Prepare-PC.cmd

This imports the reviewed source into a new detached checkout, checks author
configuration updates, upgrades the existing beta installation and installs
backed-up campaign data. Keep the printed checkout, backup and UPLOAD FOLDER
paths. It does not upload to Steam or change the Steam beta branch.

Prepare-PC.cmd is the full R11 preparation. Repair-PC.cmd changes code only;
use the full preparation to receive the combined world and native ribbon data.
If preparation stops, keep the error/report and send it back. The installer
stops at the first error; do not continue with later manual install commands.

WHAT CHANGED
- One SEST Modernised Worldwide Campaign 2028 entry combines the original
  world and complete regional expansion: 156 bases, 293 forces, 54 patrols,
  1,586 buy entries. The regional campaign ID is retained. New content needs
  a new game; existing saves retain their own state. The original definition
  and reversible legacy-save helper remain inside the pack.
- Four authored campaigns gain native completion ribbons, artwork and
  citations. Existing third-party awards are preserved.
- The separate beta payload adds F11 World Operations: Overview, Forces,
  Costs and Service, with an independent profile service ledger.
- Coordinated Strike keeps the author's controls and scheduling; SEST adds
  shared colours and planned/remaining weapon-cost estimates. A full native
  strike-window redesign is follow-on work.
- Current Topography/Pop-Out images and the DCM salvo-hold beta target are
  reviewed. Original author Workshop DLLs are retained.

PC CHECKS BEFORE PUBLICATION
1. Start a new Modernised Worldwide Campaign; check Europe, Indian Ocean,
   Australia, Americas and the date line on the beta map. Continue your
   existing regional save separately to confirm continuity.
2. On the world map, press F11. Check every tab, window size/movement,
   scrolling and pop-out/return. Credits and estimated USD remain separate.
3. Launch and complete a battle. Check its F11 costs, return to the world,
   inspect service progress, save/load and verify no duplicate report awards.
4. Open Coordinated Strike. Check all original planning/launch controls and
   the new summary. Confirm the estimate changes with planned weapon counts.
5. Check native final-mission ribbons/citations, Contacts, Group Manager,
   Topography, Identify broadcasts and campaign continuation.
6. Quit the game and run:

  R11\Capture-Repair-Results.cmd

Send the resulting capture for review. See R11\README-FIRST.txt for the full
acceptance list, ledger scope, legacy saves, restoration and limitations.

STEAM UPDATE
The separately printed upload folder is canonical stable code plus the new
campaign/ribbon data. The new Operations/strike beta code is not included in
that canonical upload. Keep the two payloads distinct. STEAM-CHANGE-NOTE.txt
covers only the canonical data changes. Both gameplay acceptance and Steam
submission remain pending; no publication has occurred.

OPTIONAL POWERSHELL EQUIVALENT
From this extracted toolkit folder:

  powershell -NoProfile -ExecutionPolicy Bypass -File .\Prepare-PC.ps1

For a nonstandard install, add -MainRepository, -GameRoot and
-WorkshopContentRoot using your actual paths. If an author-update report says
something changed upstream, retain it and capture the new configuration before
installation. Do not bypass that check.
